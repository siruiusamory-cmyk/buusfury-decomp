"""Is the NAME the only thing that changed, for every record in the image?

THE QUESTION. A rename pass must change the names and nothing else. Two ways this
method could fail that:

1. A token substitution outside a renamed name. The encoder spends expansions
   wherever the dictionary matches, not only inside the new name - "Yamcha" holds
   "Ya" AND "ha", and "in" matches inside "knowing". Every one of those must compose
   back as exactly the glyphs it replaced.

2. A record whose retail span OVERLAPS a renamed one. Retail records share bytes
   (measured: about 40 percent of decoded units are read by more than one record), so
   a rewrite is visible to its neighbours too. If the rewrite moves a character, a
   neighbour displays shifted text - words nobody asked to change.

THE ORACLE, and why it is positional. Two text-matching oracles were tried first and
both produced false failures: a table of old and new strings matches ambiguously
("Tien" and "Tien!" are both in it), so masking the names on each side and comparing
the rest is not a well-defined test. Instead the expected text is built from the
substitution POSITIONS - each substitution is (start, length, replacement) inside the
decoded container - and every record must equal its retail text with those regions
applied, character for character outside them.

HOW INDEPENDENT THIS IS, stated plainly. The regions come from the splicer's own
`substitution_regions` and `local_replacement`, so the oracle re-derives part of the
builder's answer, and that is a real limit: it checks the WRITE, not the INTENT. Six
checks do not depend on the builder at all, and they are the ones that would catch a
build that wrote the wrong thing, or a report that described a different build:

  * the images are read through their own relocated tables, unpacking and record
    inventory, not through anything the builder reported;
  * every record's STORED text must be the same length as retail, which is what stops
    any record from moving any other;
  * the set of records the image actually CHANGED is derived from the two images and
    cross-checked against the report: every record the report claims applied must
    really differ, and every record that differs without being applied must overlap a
    record that was, since a refused record's bytes are still rewritten by applied
    neighbours whose spans cross it;
  * the spliced image's digest must be the one the splice report names, and a report
    without one is refused rather than skipped;
  * each record the map names must display the map's own `new_text`, spaces aside
    (this one uses the report only to know which records were claimed applied);
  * every record the report REFUSED is read out of the image and reported as displaying
    the renamed text, still at retail, or neither. That is the check that answers
    coverage, and it has to exist because the refused record's own regions are out of
    the oracle: without it, a refused record left holding retail text would pass.

Nothing here writes an image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from tools.webfoot import compressed_dialogue as cd
from tools.webfoot.formats import webfoot_lz
from tools.webfoot.token_dictionary import TokenDictionary, decode_text
from tools.research.splice_dialogue_tokens import (substitution_regions,
                                                   substitution_table)

ROM_BASE = 0x08000000
#: The one word that names the container-pointer table. Read from the image rather
#: than assumed, because the spliced image relocates the table and repoints this
#: literal: reading the retail offset would compare the wrong two streams.
TABLE_LITERAL = 0x123CC
TABLE_SLOTS = 7


def table_of(image: bytes) -> int:
    address = struct.unpack_from("<I", image, TABLE_LITERAL)[0]
    if address < ROM_BASE or address - ROM_BASE + TABLE_SLOTS * 4 > len(image):
        raise SystemExit(f"the table literal names {address:#010x}, outside the image")
    return address - ROM_BASE


def stream_of(image: bytes, selector: int) -> bytes:
    pointer = struct.unpack_from("<I", image, table_of(image) + selector * 4)[0]
    if pointer < ROM_BASE or pointer - ROM_BASE >= len(image):
        raise SystemExit(f"selector {selector} is not a container in this image")
    return bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)


def visible(text: str, dictionary: TokenDictionary) -> str:
    """The text the engine composes, with every token expanded to its glyphs."""
    return decode_text(text, dictionary)


def expected_text(retail: str, span_start: int,
                  regions: list[tuple[int, int, str]]) -> str:
    """What a record must hold, built from the regions that were written.

    A region whose substituted name runs past this record's end is CLIPPED, not
    skipped, and the clip is exact because a stored replacement occupies the same
    number of units as the text it replaces - which is the property the whole method
    rests on. Skipping instead reported three correct records as changed. Two regions
    covering the same bytes are applied once, which is what the caller's dedup by
    (start, length) is for.
    """
    out: list[str] = []
    position = 0
    for start, length, replacement in regions:
        local = start - span_start
        first = max(local, 0)
        last = min(local + length, len(retail))
        if first >= last or first < position:
            continue
        out.append(retail[position:first])
        out.append(replacement[first - local:last - local])
        position = last
    out.append(retail[position:])
    return "".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--base-sha256", required=True,
                        help="the exact digest the base must have, so the check cannot "
                             "silently describe a different image")
    parser.add_argument("--spliced", required=True)
    parser.add_argument("--map", required=True)
    parser.add_argument("--tokens", nargs="*", required=True)
    parser.add_argument("--splice-report", required=True,
                        help="the splicer's report. Required: its refused records must "
                             "be excluded from the oracle, and its dictionary must be "
                             "the one this check decodes with")
    parser.add_argument("--report")
    parser.add_argument("--show", type=int, default=10)
    args = parser.parse_args()

    dictionary = TokenDictionary(tuple(args.tokens))
    rows = json.loads(Path(args.map).read_text(encoding="utf-8"))
    table = substitution_table(rows)
    base = Path(args.base).read_bytes()
    spliced = Path(args.spliced).read_bytes()
    if hashlib.sha256(base).hexdigest() != args.base_sha256.lower():
        raise SystemExit("the base is not the declared image")
    map_digest = hashlib.sha256(Path(args.map).read_bytes()).hexdigest()
    splice_report = json.loads(Path(args.splice_report).read_text(encoding="utf-8"))
    declared = splice_report.get("sha256")
    if not declared:
        # Fail closed rather than skip: a report without its digest cannot be tied to
        # the image being checked, and skipping the check silently is how a verifier
        # ends up describing something it never looked at.
        raise SystemExit("the splice report names no sha256, so it cannot be tied to "
                         "the image under test")
    if hashlib.sha256(spliced).hexdigest() != declared:
        raise SystemExit(
            f"the spliced image is not the one the report describes: "
            f"{hashlib.sha256(spliced).hexdigest()} != {declared}"
        )

    if splice_report.get("tokens") != list(args.tokens):
        # The splice wrote one dictionary and this check decodes with another. The
        # verifier would still pass, because it decodes with whatever it is handed,
        # so the tie has to be asserted here.
        raise SystemExit(
            f"the splice used {splice_report.get('tokens')} and this check was given "
            f"{list(args.tokens)}; they must be the same dictionary in id order"
        )
    if "map_sha256" not in splice_report:
        # A report made before the map digest was recorded. Saying so beats reporting a
        # mismatch against a digest that was never written.
        raise SystemExit(
            "the splice report carries no map_sha256: it predates the map digest. "
            "Re-run the splicer to produce a report this check can tie to a map"
        )
    if splice_report.get("map_sha256") != map_digest:
        # The map is private and lives outside the repository, so its digest is the
        # only thing that ties these numbers to the map that produced them.
        raise SystemExit(
            f"the splice used a map with digest {splice_report.get('map_sha256')} and "
            f"this one is {map_digest}: these figures describe a different rename"
        )

    # The regions that were actually written. A record the splicer refused kept its
    # own bytes, so its substitutions are not in the oracle either - the oracle's job
    # is to describe what the image DID, and then the checks below hold every record to
    # it. Its DISPLAYED text is still checked, further down: applied neighbours whose
    # spans cross it rewrite its bytes, and that outcome is reported rather than
    # assumed, because nothing else looks at it.
    refused = set(splice_report.get("refused", {}))
    applied_rows = {key: row for key, row in rows.items() if key not in refused}
    streams: dict[int, bytes] = {}
    # A record whose OWN write was refused can still display its new name, because
    # applied neighbours whose spans cross it rewrite its bytes. The intent check below
    # only covers records the report claims applied, and the refused record's own
    # regions are deliberately out of the oracle, so this is the only check that looks.
    refused_outcomes: dict[str, list[str]] = {"shows_the_new_name": [],
                                              "still_at_retail": [], "neither": []}

    # WHICH RECORDS THE IMAGE ACTUALLY CHANGED, derived from the image rather than
    # taken from the report. This is what stops a report that declares every record
    # refused from passing, and it is precise about the one case that looks like a
    # disagreement: a record the splice REFUSED can still have changed bytes, because
    # its span overlaps a neighbour that was applied. So two things must hold - every
    # record the report claims applied really differs, and every record that differs
    # without being applied overlaps a record that was.
    changed: set[str] = set()
    for selector in range(TABLE_SLOTS):
        base_stream = stream_of(base, selector)
        spliced_stream = stream_of(spliced, selector)
        streams[selector] = spliced_stream
        for key, row in rows.items():
            if row["old_selector"] != selector:
                continue
            start, length = row["old_start"], row["old_length"]
            if spliced_stream[start:start + length] != base_stream[start:start + length]:
                changed.add(key)
    declared_applied = set(rows) - refused
    applied_spans = [(row["old_selector"], row["old_start"], row["old_length"])
                     for key, row in applied_rows.items()]

    def overlaps_an_applied_record(row: dict) -> bool:
        selector, start, length = row["old_selector"], row["old_start"], row["old_length"]
        return any(other_selector == selector
                   and not (start + length <= other_start
                            or start >= other_start + other_length)
                   for other_selector, other_start, other_length in applied_spans)

    not_written = sorted(key for key in declared_applied if key not in changed)
    unexplained = sorted(key for key in changed if key not in declared_applied
                         and not overlaps_an_applied_record(rows[key]))
    if not_written or unexplained:
        raise SystemExit(
            f"the report and the image disagree: {len(not_written)} record(s) claimed "
            f"applied did not change {not_written[:3]}, and {len(unexplained)} changed "
            f"record(s) are neither applied nor inside an applied span "
            f"{unexplained[:3]}"
        )

    # What each refused record displays, read out of the image.
    for key in sorted(refused):
        row = rows[key]
        start, length = row["old_start"], row["old_length"]
        stored = streams[row["old_selector"]][start:start + length]
        now = visible(stored.decode("utf-16le", "replace"), dictionary)
        retail = visible(row["old_text"], dictionary)
        if now.replace(" ", "") == row["new_text"].replace(" ", ""):
            refused_outcomes["shows_the_new_name"].append(key)
        elif now == retail:
            refused_outcomes["still_at_retail"].append(key)
        else:
            refused_outcomes["neither"].append(key)

    # Every substitution the map performs, as an absolute region of its container,
    # in UNITS. `old_start` is a byte offset into the decoded container
    # (tools/webfoot/handles.py) while `substitution_regions` counts characters, so
    # the two are brought into the same unit here - an earlier version mixed them and
    # reported 66 records as changed when their text was correct.
    regions: dict[int, list[tuple[int, int, str]]] = {index: []
                                                      for index in range(TABLE_SLOTS)}
    for row in applied_rows.values():
        for start, length, replacement in substitution_regions(
                row["old_text"], row["new_text"], dictionary, table):
            regions[row["old_selector"]].append(
                (row["old_start"] // 2 + start, length, replacement))
    # Overlapping retail records describe the SAME bytes, so one substitution can
    # arrive from two records. Two records agreeing is one region; two disagreeing is
    # a build that could not satisfy both, which the splicer refuses and this reports.
    for selector, spans in regions.items():
        merged: dict[tuple[int, int], str] = {}
        for start, length, replacement in spans:
            key = (start, length)
            if key in merged and merged[key] != replacement:
                raise SystemExit(
                    f"selector {selector}: two records want different text at "
                    f"{start}+{length}; no build can satisfy both"
                )
            merged[key] = replacement
        regions[selector] = sorted((start, length, replacement)
                                   for (start, length), replacement in merged.items())
        for (a_start, a_len, _), (b_start, _b_len, _) in zip(regions[selector],
                                                             regions[selector][1:]):
            if b_start < a_start + a_len:
                raise SystemExit(
                    f"selector {selector}: substitution regions overlap at "
                    f"{a_start} and {b_start} with different extents"
                )

    def expected(retail: str, span_start: int, selector: int) -> str:
        return expected_text(retail, span_start, regions[selector])

    findings: dict[str, list] = {"record_unchanged": [], "record_name_only": [],
                                 "record_WRONG": [], "unknown_token": []}
    seen = 0
    sharing = 0
    for selector in range(TABLE_SLOTS):
        base_stream = stream_of(base, selector)
        spliced_stream = stream_of(spliced, selector)
        if len(base_stream) != len(spliced_stream):
            raise SystemExit(
                f"selector {selector}: the spliced stream is a different length "
                f"({len(spliced_stream)} vs {len(base_stream)}), so an offset moved "
                f"and every handle in it would have to be re-checked"
            )
        spans = [(record.handle.decoded_start, record.handle.decoded_length)
                 for record in cd.dialogue_record_inventory(base, selector,
                                                            len(base_stream))]
        # How much of this container is read by more than one record. This is why a
        # rewrite is visible to its neighbours at all, and it is reported here rather
        # than in a scratch script so the figure can be reproduced from this tool.
        for index, (start, length) in enumerate(spans):
            if any(not (other + other_len <= start or other >= start + length)
                   for other_index, (other, other_len) in enumerate(spans)
                   if other_index != index):
                sharing += 1

        for record in cd.dialogue_record_inventory(base, selector, len(base_stream)):
            start, length = record.handle.decoded_start, record.handle.decoded_length
            retail = base_stream[start:start + length].decode("utf-16le", "replace")
            stored = spliced_stream[start:start + length].decode("utf-16le", "replace")
            try:
                now = visible(stored, dictionary)
            except Exception as exc:                                  # noqa: BLE001
                findings["unknown_token"].append((selector, start, str(exc)))
                continue
            seen += 1
            want = visible(expected(retail, start // 2, selector), dictionary)
            # The stored text must be the same length: that is what keeps every
            # offset in the container where retail put it, and therefore what stops
            # this record's rewrite from moving any other record's text.
            same_stored_length = len(stored) == len(retail)
            intent_ok = True
            row = next((candidate for candidate in applied_rows.values()
                        if candidate["old_selector"] == selector
                        and candidate["old_start"] == start
                        and candidate["old_length"] == length), None)
            if row is not None:
                # A record the map explicitly renames must display that text, spaces
                # aside: the payment for a shrinking name is spaces, and they are the
                # only permitted difference.
                intent_ok = (now.replace(" ", "") == row["new_text"].replace(" ", ""))
            if same_stored_length and now == want and intent_ok:
                if now == retail:
                    findings["record_unchanged"].append((selector, start))
                else:
                    findings["record_name_only"].append((selector, start))
            else:
                first = next((index for index in range(min(len(now), len(want)))
                              if now[index] != want[index]), min(len(now), len(want)))
                findings["record_WRONG"].append(
                    (selector, start, length, same_stored_length, retail, want, now, first))

    print(f"records whose text is untouched                : "
          f"{len(findings['record_unchanged'])}")
    print(f"records where only the substituted names differ : "
          f"{len(findings['record_name_only'])}")
    print(f"records where anything else differs             : "
          f"{len(findings['record_WRONG'])}")
    print(f"streams holding an unresolvable token           : "
          f"{len(findings['unknown_token'])}")
    print(f"records the splice report refused                : {len(refused)}")
    print(f"  of those, displaying the renamed text         : "
          f"{len(refused_outcomes['shows_the_new_name'])}")
    print(f"  of those, still at retail text                : "
          f"{len(refused_outcomes['still_at_retail'])}")
    print(f"  of those, neither                             : "
          f"{len(refused_outcomes['neither'])} "
          f"{refused_outcomes['neither'][:3]}")
    print(f"records whose bytes the image changed            : {len(changed)} "
          f"(applied {len(declared_applied)}; the rest overlap an applied span)")
    print(f"records examined                                : {seen}")
    print(f"records sharing at least one byte with another  : {sharing}")
    print("scope: the seven decoded containers, over every record their own inventory "
          "names.\n       Bytes outside those records, in container gaps, and outside "
          "the containers are not covered.")

    if findings["record_WRONG"]:
        print("\nrecords where something other than a substituted name changed:")
        for selector, start, length, same_length, retail, want, now, first in \
                findings["record_WRONG"][:args.show]:
            print(f"  selector {selector}, span {start}+{length}, "
                  f"stored length preserved: {same_length}, "
                  f"first divergence at visible offset {first}")
            print(f"    retail : {retail[max(0, first - 25):first + 35]!r}")
            print(f"    want   : {want[max(0, first - 25):first + 35]!r}")
            print(f"    now    : {now[max(0, first - 25):first + 35]!r}")

    # The refused-record failures are recorded BEFORE the report is written, or a
    # failing run would publish a report saying nothing was wrong while its exit code
    # said otherwise, and a consumer reading the report would see success.
    refused_failures: list[dict] = []
    for failure_kind in ("neither", "still_at_retail"):
        if refused_outcomes[failure_kind]:
            # A refused record left at retail text is a rename that did not land, and
            # "neither" is an outcome nothing explains. Both are failures: this tool's
            # job is to answer coverage, not to print it and exit zero.
            print(f"FAILED: {len(refused_outcomes[failure_kind])} refused record(s) "
                  f"{'showing neither the new name nor retail text' if failure_kind == 'neither' else 'still at retail text'}: "
                  f"{refused_outcomes[failure_kind][:3]}")
            refused_failures.append({"kind": failure_kind,
                                     "records": refused_outcomes[failure_kind]})

    if args.report:
        Path(args.report).write_text(json.dumps({
            "counts": {name: len(value) for name, value in findings.items()},
            "records_examined": seen,
            "substitution_regions": sum(len(spans) for spans in regions.values()),
            "refused_record_failures": refused_failures,
            "records_wrong": [
                {"selector": selector, "start": start, "length": length,
                 "stored_length_preserved": same_length, "retail": retail,
                 "want": want, "now": now, "first_divergence": first}
                for selector, start, length, same_length, retail, want, now, first
                in findings["record_WRONG"]],
        }, indent=2), encoding="utf-8")

    # Fail closed: one record whose characters changed outside a substituted name, or
    # one refused rename that did not land, is what this tool exists to refuse.
    return 1 if (findings["record_WRONG"] or findings["unknown_token"]
                 or refused_failures) else 0


if __name__ == "__main__":
    sys.exit(main())
