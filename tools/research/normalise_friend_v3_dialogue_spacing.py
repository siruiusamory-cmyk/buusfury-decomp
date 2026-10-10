"""Collapse rename-leftover multi-space runs in a friend image's dialogue records.

WHY. A rename pass that swapped a longer word for a shorter one left the difference behind as extra
spaces: measured on this image, 212 records carry an interior run of two or more spaces against 26
in the canonical ROM. Those extras are the artifact the owner sees as "weird spaces after a
rename".

THE HARD PART, MEASURED. These containers are chain-shared: selector 4 holds 486 live handles over
65,322 bytes of payload and selector 5 holds 460 over 65,394, so records cover each other. A record
can only be rebuilt in place if its unit count is unchanged - otherwise every later record in the
container shifts - so a collapsed run has to be paid back as spaces at the END of that record's own
span. If another record also covers the run, the payback lands inside that record's text, and the
outcome depends on which record is written last. Measured: of 424 interior run instances, 135 are
covered by exactly one live record and 289 by two or more. This pass writes ONLY the single-coverage
runs. The rest need a stream rebuild plus handle rewriting, which is a different and larger change.

WHAT IS NEVER TOUCHED. A run whose context also appears in the canonical ROM stays as it is: some of
those sit in the system template pools (`%s learned ...`, `@^You have died!`) where a run of spaces
may be a separator the engine's parser depends on.

STALE HANDLES. The inventory reports every word-aligned handle the engine could read, and a rebuilt
container leaves stale ones: 255 of selector 4's 486 and 233 of selector 5's 460 name a span past
the payload's end. Writing one grows the payload instead of editing it, which corrupted two
containers in an earlier version of this pass. Only in-payload spans are written or compared.

THE CHECKS, all three of which must hold. Every record's sequence of non-space characters is
unchanged: not one visible character added, dropped or reordered. The image's total interior-run
count strictly falls. And no record gains a word-double-space context it did not already have,
because a payback space can lengthen an existing pad but must never create a new one.

MEASURED OUTCOME, AND WHY THIS TOOL IS NOT THE FIX. Run against release 3 it collapsed 118 runs and
moved the image's interior-run count from 424 to 419. The reason is in the coverage numbers above:
a payback inside one record lands inside another record's text and re-creates the run there. This
tool is kept because its guards are the ones the eventual rebuild needs (P-021, P-022, P-023), not
because it solves the problem. The interior spacing is release 4's work, and it needs a container
rebuild with every handle word rewritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot import compressed_dialogue as cd  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

ROM_BASE = 0x08000000
TABLE_LITERAL = 0x123CC
CONTAINERS = 8
UNIT = 2
CONTEXT = 10


class SpacingError(ValueError):
    """The pass refused rather than writing bytes it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def table_offset(image: bytes) -> int:
    return int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE


def read_container(image: bytes, selector: int) -> tuple[bytes, int, int]:
    at = table_offset(image) + 4 * selector
    pointer = int.from_bytes(image[at:at + 4], "little")
    if pointer < ROM_BASE:
        raise SpacingError(f"selector {selector} has no container")
    container = webfoot_lz.unpack(image, pointer - ROM_BASE)
    return bytes(container.data), container.offset, container.kind


def live_records(image: bytes, selector: int, stream: bytes) -> list[tuple[int, int]]:
    out = []
    for record in cd.dialogue_record_inventory(image, selector, len(stream)):
        start = record.handle.decoded_start
        length = record.handle.decoded_length
        if (start + length) * UNIT <= len(stream):
            out.append((start, length))
    return out


def text_of(stream: bytes, start: int, length: int) -> str:
    return stream[start * UNIT:(start + length) * UNIT].decode("utf-16le", "replace")


def interior_runs(text: str) -> list[tuple[int, int]]:
    """Runs of two or more spaces that are not the record's own trailing pad."""
    body = text.rstrip(" ")
    runs = []
    index = 0
    while index < len(body):
        if body[index] == " ":
            begin = index
            while index < len(body) and body[index] == " ":
                index += 1
            if index - begin >= 2:
                runs.append((begin, index - begin))
        else:
            index += 1
    return runs


def word_context(text: str, begin: int, count: int) -> str:
    """The words either side of a run, so a new run anywhere can be spotted by its neighbours."""
    window = text[max(0, begin - CONTEXT):begin + count + CONTEXT]
    return " ".join(window.split())


def contexts_of(image: bytes) -> set[str]:
    """Every interior run's word context in an image, for the retail comparison."""
    found: set[str] = set()
    for selector in range(CONTAINERS):
        try:
            stream, _offset, _kind = read_container(image, selector)
        except SpacingError:
            continue
        for start, length in live_records(image, selector, stream):
            text = text_of(stream, start, length)
            for begin, count in interior_runs(text):
                found.add(word_context(text, begin, count))
    return found


def single_coverage_runs(image: bytes, selector: int, stream: bytes,
                         live: list[tuple[int, int]]) -> list[tuple[int, int, int]]:
    """Runs covered by exactly one live record: (record start, run start, run length)."""
    selected = []
    for start, length in live:
        text = text_of(stream, start, length)
        for begin, count in interior_runs(text):
            absolute = start + begin
            covering = sum(1 for rstart, rlength in live
                           if rstart <= absolute and absolute + count <= rstart + rlength)
            if covering == 1:
                selected.append((start, absolute, count))
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--retail", required=True,
                        help="the canonical image, whose own spacing is left alone")
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise SpacingError(f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")
    keep = contexts_of(Path(args.retail).read_bytes())

    out = bytearray(image)
    document: dict = {
        "input": str(source), "input_sha256": got, "input_bytes": len(image),
        "retail_contexts": len(keep), "containers": [], "records_changed": 0,
        "runs_collapsed": 0, "runs_kept_as_retail": 0, "runs_left_chained": 0,
        "runs_unpaid_for": 0, "stale_handles": 0, "output_bytes": None,
    }

    for selector in range(CONTAINERS):
        at = table_offset(image) + 4 * selector
        pointer = int.from_bytes(image[at:at + 4], "little")
        if pointer < ROM_BASE or pointer - ROM_BASE >= len(image):
            continue
        stream, offset, kind = read_container(image, selector)
        document["stale_handles"] += sum(
            1 for record in cd.dialogue_record_inventory(image, selector, len(stream))
            if (record.handle.decoded_start + record.handle.decoded_length) * UNIT > len(stream))
        live = live_records(image, selector, stream)

        by_record: dict[int, list[tuple[int, int]]] = {}
        for record_start, run_start, run_length in single_coverage_runs(image, selector, stream,
                                                                       live):
            text = text_of(stream, *next((s, l) for s, l in live if s == record_start))
            if word_context(text, run_start - record_start, run_length) in keep:
                document["runs_kept_as_retail"] += 1
                continue
            by_record.setdefault(record_start, []).append((run_start, run_length))
        document["runs_left_chained"] += sum(
            1 for start, length in live
            for begin, count in interior_runs(text_of(stream, start, length))
            if sum(1 for rstart, rlength in live
                   if rstart <= start + begin and start + begin + count <= rstart + rlength) > 1)

        if not by_record:
            continue
        edited = bytearray(stream)
        for record_start, runs in by_record.items():
            length = next(l for s, l in live if s == record_start)
            text = text_of(stream, record_start, length)
            # The payback has to come out of the record's OWN trailing padding. A record whose text
            # ends on a visible character has nothing to give up, and padding its tail would
            # overwrite its last characters with spaces - the check below caught exactly that on ten
            # records. Such a record is left alone and counted.
            spare = length - len(text.rstrip(" "))
            removed = sum(run_length - 1 for _start, run_length in runs)
            if removed > spare:
                document["runs_unpaid_for"] += len(runs)
                continue
            rebuilt = text
            for run_start, run_length in sorted(runs, reverse=True):
                begin = run_start - record_start
                rebuilt = rebuilt[:begin] + " " + rebuilt[begin + run_length:]
            pad = length - len(rebuilt)
            if pad < 0 or pad > spare:
                raise SpacingError(f"REFUSED: {selector}:{record_start}:{length} needs {pad} "
                                   f"payback units but holds {spare}")
            rebuilt = rebuilt + " " * pad
            if len(rebuilt) != length:
                raise SpacingError(f"REFUSED: {selector}:{record_start}:{length} rebuilt to "
                                   f"{len(rebuilt)} units")
            if text.replace(" ", "") != rebuilt.replace(" ", ""):
                raise SpacingError(f"REFUSED: {selector}:{record_start}:{length} would lose a "
                                   "visible character")
            encoded = rebuilt.encode("utf-16le")
            edited[record_start * UNIT:(record_start + length) * UNIT] = encoded
            document["records_changed"] += 1
            document["runs_collapsed"] += len(runs)

        if kind != webfoot_lz.STORED:
            raise SpacingError(f"REFUSED: container {selector} is packed, and this pass only writes "
                               "stored containers in place")
        if len(edited) != len(stream):
            raise SpacingError(f"REFUSED: container {selector} changed length")
        payload = offset + webfoot_lz.HEADER_SIZE
        out[payload:payload + len(edited)] = edited
        document["containers"].append({"selector": selector, "records": len(by_record),
                                       "runs_collapsed": sum(len(r) for r in by_record.values()),
                                       "written_at": payload})

    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise SpacingError(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(out)
    if staged.read_bytes() != bytes(out):
        raise SpacingError("REFUSED: the staged write does not match the plan")
    staged.replace(target)

    # The three checks. They run on the written image, not on the plan.
    written = target.read_bytes()
    problems = 0
    before_runs = after_runs = 0
    gained = []
    for selector in range(CONTAINERS):
        try:
            old_stream, _offset, _kind = read_container(image, selector)
            new_stream, _offset, _kind = read_container(written, selector)
        except SpacingError:
            continue
        old_contexts = set()
        new_contexts = set()
        for start, length in live_records(image, selector, old_stream):
            old_text = text_of(old_stream, start, length)
            new_text = text_of(new_stream, start, length)
            if old_text.replace(" ", "") != new_text.replace(" ", ""):
                problems += 1
                print(f"FAIL {selector}:{start}:{length} lost or gained a visible character")
            for begin, count in interior_runs(old_text):
                old_contexts.add(word_context(old_text, begin, count))
                before_runs += 1
            for begin, count in interior_runs(new_text):
                new_contexts.add(word_context(new_text, begin, count))
                after_runs += 1
        introduced = new_contexts - old_contexts - keep
        if introduced:
            gained.extend(sorted(introduced)[:3])
    if problems:
        raise SpacingError(f"REFUSED: {problems} record(s) lost or gained a visible character")
    if after_runs >= before_runs:
        raise SpacingError(f"REFUSED: interior runs did not fall ({before_runs} -> {after_runs})")
    if gained:
        raise SpacingError(f"REFUSED: a new interior run appeared: {gained[:3]}")

    document["interior_runs_before"] = before_runs
    document["interior_runs_after"] = after_runs
    document["output"] = str(target)
    document["output_sha256"] = sha256_bytes(written)
    document["output_bytes"] = len(written)
    Path(args.manifest).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    for entry in document["containers"]:
        print(f"  container {entry['selector']}: {entry['records']} record(s) rebuilt, "
              f"{entry['runs_collapsed']} run(s) collapsed, payload at 0x{entry['written_at']:X}")
    print(f"# interior runs: {before_runs} -> {after_runs}")
    print(f"# rebuilt {document['records_changed']} record(s); "
          f"{document['runs_left_chained']} run instance(s) left because two or more records cover "
          f"them; {document['runs_kept_as_retail']} left because retail has the same run; "
          f"{document['stale_handles']} stale handle(s) skipped")
    print(f"# wrote {target} {len(written)} bytes sha256 {document['output_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
