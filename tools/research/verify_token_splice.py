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
builder's answer, and that is a real limit: it checks the WRITE, not the INTENT. Four
checks do not depend on the builder at all, and they are the ones that would catch a
build that wrote the wrong thing anywhere:

  * the images are read through their own relocated tables, unpacking and record
    inventory, not through anything the builder reported;
  * every record's STORED text must be the same length as retail, which is what stops
    any record from moving any other;
  * each record the map names must display the map's own `new_text`, spaces aside;
  * the spliced image's digest must be the one the splice report names.

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
    splice_report = json.loads(Path(args.splice_report).read_text(encoding="utf-8"))
    declared = splice_report.get("sha256")
    if declared and hashlib.sha256(spliced).hexdigest() != declared:
        # Not just "a spliced image": the one the report describes.
        raise SystemExit(
            f"the spliced image is not the one the report describes: "
            f"{hashlib.sha256(spliced).hexdigest()} != {declared}"
        )

    # The regions that were actually written. A record the splicer refused kept its
    # retail bytes, so its substitutions are not in the image and must not be in the
    # oracle either - the oracle's job is to describe what the image DID, and then
    # the two checks below hold every record to it.
    refused = set()
    if splice_report.get("tokens") != list(args.tokens):
        # The splice wrote one dictionary and this check decodes with another. The
        # verifier would still pass, because it decodes with whatever it is handed,
        # so the tie has to be asserted here.
        raise SystemExit(
            f"the splice used {splice_report.get('tokens')} and this check was given "
            f"{list(args.tokens)}; they must be the same dictionary in id order"
        )
    refused = set(splice_report.get("refused", {}))
    applied_rows = {key: row for key, row in rows.items() if key not in refused}

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
        """What this record must hold, built from the regions that were written.

        A region whose substituted name runs past this record's end is CLIPPED, not
        skipped, and the clip is exact because a stored replacement occupies the same
        number of units as the text it replaces - which is the property the whole
        method rests on. Skipping instead reported three correct records as changed.
        """
        out: list[str] = []
        position = 0
        for start, length, replacement in regions[selector]:
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

    if args.report:
        Path(args.report).write_text(json.dumps({
            "counts": {name: len(value) for name, value in findings.items()},
            "records_examined": seen,
            "substitution_regions": sum(len(spans) for spans in regions.values()),
            "records_wrong": [
                {"selector": selector, "start": start, "length": length,
                 "stored_length_preserved": same_length, "retail": retail,
                 "want": want, "now": now, "first_divergence": first}
                for selector, start, length, same_length, retail, want, now, first
                in findings["record_WRONG"]],
        }, indent=2), encoding="utf-8")

    # Fail closed: one record whose characters changed outside a substituted name is
    # the thing this tool exists to refuse.
    return 1 if findings["record_WRONG"] or findings["unknown_token"] else 0


if __name__ == "__main__":
    sys.exit(main())
