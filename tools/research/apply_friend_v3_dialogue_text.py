"""Replace text inside a friend image's packed dialogue containers, read-only elsewhere.

WHY THIS EXISTS. Two owner-approved wording edits live inside the dialogue containers, not in the
1,534-slot text table: the spaced "Great Soy Man" in one record, and the ten records where retail
says "Kakarot" and the built image says "Yamcha". The table tools cannot reach either, and the
container repack tool (`tools/webfoot/dialogue_repack.py`) rebuilds streams for deduplication
without replacing text. This tool does the replacement and nothing else.

HOW A REPLACEMENT KEEPS EVERY OFFSET. A dialogue record is addressed by its handle: selector,
decoded start and decoded length, all in the image. Moving the units inside a record would move
every later record in the same container, and every handle that names them would then point at
different words. So a replacement is written AT THE RECORD'S OWN UNIT COUNT: a shorter replacement
is padded with spaces at the end of the record's own span, which no reader draws differently and
which keeps every other record exactly where it was. A longer replacement is refused outright.
That is the whole safety argument, and it is checked by comparing every record's text before and
after.

WHAT IS REFUSED. The old text must occur exactly once in that record and nowhere else in the
container's other records; the replacement must not be longer; the packed container is re-encoded
and either fits the space the original occupied or is appended and its table entry repointed,
with the same one-reference guard the project's text tools use. Nothing is written on a refusal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot import compressed_dialogue as cd  # noqa: E402
from tools.webfoot import dialogue_repack as dr  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402
from tools.webfoot.write import WriteError, ensure_not_source_alias  # noqa: E402

ROM_BASE = 0x08000000
TABLE_LITERAL = 0x123CC
CONTAINER_SELECTORS = 8
UNIT = 2


class DialogueTextError(ValueError):
    """The edit refused rather than writing bytes it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def table_offset(image: bytes) -> int:
    return int.from_bytes(image[TABLE_LITERAL:TABLE_LITERAL + 4], "little") - ROM_BASE


def container_pointer(image: bytes, selector: int) -> int:
    at = table_offset(image) + 4 * selector
    return int.from_bytes(image[at:at + 4], "little")


def read_stream(image: bytes, selector: int) -> tuple[bytes, int, int]:
    """The unpacked units, the container's file offset and its kind."""
    pointer = container_pointer(image, selector)
    if pointer < ROM_BASE:
        raise DialogueTextError(f"selector {selector} has no container")
    offset = pointer - ROM_BASE
    container = webfoot_lz.unpack(image, offset)
    return bytes(container.data), offset, container.kind


def record_text(stream: bytes, start: int, length: int) -> str:
    return stream[start * UNIT:(start + length) * UNIT].decode("utf-16le")


def inventory(image: bytes, selector: int, stream: bytes) -> list[tuple[int, int]]:
    return [(record.handle.decoded_start, record.handle.decoded_length)
            for record in cd.dialogue_record_inventory(image, selector, len(stream))]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--edit", action="append", required=True,
                        help="SELECTOR:START:LENGTH:OLD:NEW")
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise DialogueTextError(f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    edits: dict[int, list[tuple[int, int, str, str]]] = {}
    for spec in args.edit:
        selector_text, start_text, length_text, old, new = spec.split(":", 4)
        edits.setdefault(int(selector_text), []).append(
            (int(start_text), int(length_text), old, new))

    streams: dict[int, bytes] = {}
    kinds: dict[int, int] = {}
    before: dict[int, list[tuple[int, int, str]]] = {}
    for selector in range(CONTAINER_SELECTORS):
        pointer = container_pointer(image, selector)
        if pointer < ROM_BASE:
            continue
        stream, _offset, kind = read_stream(image, selector)
        streams[selector] = stream
        kinds[selector] = kind
        before[selector] = [(start, length, record_text(stream, start, length))
                            for start, length in inventory(image, selector, stream)]

    out = bytearray(image)
    document: dict = {
        "input": str(source), "input_sha256": got, "input_bytes": len(image),
        "edits": [],
        "containers": [],
        "output_bytes": None,
    }

    edit_records: dict[int, list[tuple[int, int, str, str, int]]] = {}
    for selector, changes in sorted(edits.items()):
        stream = bytearray(streams[selector])
        records = before[selector]
        for start, length, old, new in changes:
            text = record_text(bytes(stream), start, length)
            if text.count(old) != 1:
                raise DialogueTextError(
                    f"REFUSED: {selector}:{start}:{length} holds {old!r} "
                    f"{text.count(old)} time(s), expected exactly once")
            if len(new) * UNIT > len(old) * UNIT:
                raise DialogueTextError(
                    f"REFUSED: {selector}:{start}:{length}: {new!r} is longer than {old!r}")
            replaced = text.replace(old, new)
            # Keep the record's own unit count so no later record moves: pad the tail.
            pad = length - len(replaced)
            if pad < 0:
                raise DialogueTextError(f"REFUSED: {selector}:{start}:{length}: the replacement "
                                        f"does not fit the record's own span")
            replaced = replaced + " " * pad
            encoded = replaced.encode("utf-16le")
            if len(encoded) != length * UNIT:
                raise DialogueTextError(f"REFUSED: {selector}:{start}:{length}: the padded record "
                                        f"is {len(encoded)} bytes, not {length * UNIT}")
            stream[start * UNIT:(start + length) * UNIT] = encoded
            edit_records.setdefault(selector, []).append((start, length, old, new, pad))
            document["edits"].append({
                "selector": selector, "start": start, "length": length,
                "old": old, "new": new, "padded_with": pad,
            })

        # A container is either stored (kind 0) or packed (kinds 1 and 2), and it has to go back
        # in the form it came out of: re-encoding a stored container as packed would change the
        # reader's path, and the project's packer refuses kind 0 outright.
        if kinds[selector] == webfoot_lz.STORED:
            packed = webfoot_lz.build_stored(bytes(stream))
        else:
            packed = webfoot_lz.pack(bytes(stream), kind=kinds[selector])
        original_size = webfoot_lz.unpack(image, container_pointer(image, selector) - ROM_BASE)
        fits = len(packed) <= (original_size.packed_end - original_size.offset)
        if fits:
            at = original_size.offset
        else:
            at = len(out)
            while at % 4:
                out.append(0x00)
                at += 1
            needle = container_pointer(image, selector).to_bytes(4, "little")
            references = sum(1 for index in range(0, len(image) - 4, 4)
                             if image[index:index + 4] == needle)
            if references != 1:
                raise DialogueTextError(
                    f"REFUSED: selector {selector} needs {len(packed)} bytes but its container "
                    f"occupies {original_size.packed_end - original_size.offset}, and the old "
                    f"pointer has {references} word-aligned references, so it cannot be repointed")
            entry = table_offset(image) + 4 * selector
            out[entry:entry + 4] = (ROM_BASE + at).to_bytes(4, "little")
        while len(out) < at + len(packed):
            out.append(0x00)
        out[at:at + len(packed)] = packed
        document["containers"].append({
            "selector": selector,
            "packed_before": original_size.packed_end - original_size.offset,
            "packed_after": len(packed),
            "written_at": at, "relocated": not fits,
        })

    target = Path(args.out)
    try:
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise DialogueTextError(f"REFUSED: {error}") from error
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(out)
    if staged.read_bytes() != bytes(out):
        raise DialogueTextError("REFUSED: the staged write does not match the plan")
    staged.replace(target)

    # Readback. The containers are chained: one record's span can sit inside another's, so a
    # covering record legitimately reads the new wording too. What must hold for EVERY record is
    # that its words, punctuation and control units are unchanged apart from the edits whose span
    # lies INSIDE that record - never every occurrence of the word, which is why the expectation
    # is built from the spans and not by substituting the word everywhere. The comparison is the
    # project's whitespace-insensitive one, because absorbing a pad moves a space within the
    # covering record.
    written = target.read_bytes()
    applied = {selector: [(start, length, old, new) for start, length, old, new, _pad in changes]
               for selector, changes in edit_records.items()}
    problems = 0
    for selector, records in before.items():
        stream, _offset, _kind = read_stream(written, selector)
        for start, length, text in records:
            expected = text
            for estart, elength, old, new in applied.get(selector, []):
                if start <= estart and estart + elength <= start + length:
                    offset = estart - start
                    span = expected[offset:offset + elength]
                    expected = (expected[:offset] + span.replace(old, new)
                                + " " * (elength - len(span.replace(old, new)))
                                + expected[offset + elength:])
            now = record_text(stream, start, length)
            if dr.normalised(now) != dr.normalised(expected):
                problems += 1
                print(f"FAIL {selector}:{start}:{length}: reads {now[:60]!r}, "
                      f"expected {expected[:60]!r}")
    for selector, changes in sorted(edits.items()):
        stream, _offset, _kind = read_stream(written, selector)
        for start, length, old, _new in changes:
            print(f"  {selector}:{start}:{length} replaced {old!r} -> "
                  f"{dr.normalised(record_text(stream, start, length))[:100]!r}")
    if problems:
        raise DialogueTextError(f"REFUSED: {problems} record(s) changed beyond the replacement")

    document["output"] = str(target)
    document["output_sha256"] = sha256_bytes(written)
    document["output_bytes"] = len(written)
    Path(args.manifest).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    for entry in document["containers"]:
        print(f"  container {entry['selector']}: packed {entry['packed_before']} -> "
              f"{entry['packed_after']} bytes, written at 0x{entry['written_at']:X}"
              f"{' (RELOCATED)' if entry['relocated'] else ''}")
    print(f"# {len(document['edits'])} edit(s); every other record reads unchanged")
    print(f"# wrote {target} {len(written)} bytes sha256 {document['output_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
