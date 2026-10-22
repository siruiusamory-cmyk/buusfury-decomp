"""Who names a byte range, and whether the name can come from code.

A range is only "unconsumed" relative to the search that was actually run, so this tool reports each
axis with its own denominator:

- ``sites``     every word-aligned site in the image holding ``0x08000000 + offset`` for an offset in
                a range, with each site classified as a ledger code row, an INCBIN slice or data.
                A site inside a data table is a NAME, not a consumer.
- ``literals``  every decoded Thumb ``ldr rX,[pc,#imm8*4]`` and ARM ``ldr rX,[pc,#imm12]`` inside the
                ledger's code rows whose LITERAL VALUE is such an address. Two disjoint sets are
                tested here - the literal's own address against the code rows, the value it holds
                against the ranges - and a census that swaps them returns a clean-looking zero.

The code map is the ledger's ``thumb``/``arm`` rows, so a reader outside them is invisible: every
count this tool prints is scoped to that denominator, and the report says so.

    python -m tools.research.consumer_search --image baserom.gba --range 0x71C90-0x945C0
    python -m tools.research.consumer_search --image baserom.gba --range 0x6B7080-0x6B7E8C --json OUT
"""
from __future__ import annotations

import argparse
import bisect
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import gate  # noqa: E402

ROM_BASE = 0x08000000


def parse_range(text):
    start, _, end = text.partition("-")
    return int(start, 16), int(end, 16)


def _index(spans):
    ordered = sorted(spans)
    return [start for start, _ in ordered], ordered


def _holds(index, offset):
    starts, spans = index
    position = bisect.bisect_right(starts, offset) - 1
    return position >= 0 and spans[position][0] <= offset < spans[position][1]


def ledger_rows(path):
    rows = [(row[0], row[1], row[2], row[3]) for row in gate.ledger_rows(path)]
    return rows, [row for row in rows if row[2] in ("thumb", "arm")]


def sites(image, ranges):
    index = _index(ranges)
    out = []
    for offset in range(0, len(image) - 3, 4):
        value = struct.unpack_from("<I", image, offset)[0]
        if ROM_BASE <= value < ROM_BASE + len(image) and _holds(index, value - ROM_BASE):
            out.append((offset, value - ROM_BASE))
    return out


def literal_loads(image, code_rows, ranges):
    index = _index(ranges)
    out = []
    for start, length, mode, _ in code_rows:
        body = image[start:start + length]
        stride = 2 if mode == "thumb" else 4
        for step in range(0, len(body) - 3, stride):
            site = start + step
            if mode == "thumb":
                halfword = struct.unpack_from("<H", body, step)[0]
                if (halfword & 0xF800) != 0x4800:
                    continue
                literal = ((site + 4) & ~3) + 4 * (halfword & 0xFF)
            else:
                word = struct.unpack_from("<I", body, step)[0]
                if (word & 0x0F7F0000) != 0x051F0000:
                    continue
                literal = site + 8 + (word & 0xFFF)
            if literal + 4 > len(image):
                continue
            value = struct.unpack_from("<I", image, literal)[0]
            if ROM_BASE <= value < ROM_BASE + len(image) and _holds(index, value - ROM_BASE):
                out.append((site, literal, value - ROM_BASE))
    return out


def classify(site, code_index, incbin_index):
    if _holds(code_index, site):
        return "code"
    if _holds(incbin_index, site):
        return "incbin"
    return "data"


def report(image, ranges, rows, code_rows, incbin=()):
    code_index = _index((start, start + length) for start, length, _, _ in code_rows)
    incbin_index = _index(incbin)
    found = sites(image, ranges)
    buckets = {}
    for site, _ in found:
        buckets[classify(site, code_index, incbin_index)] = \
            buckets.get(classify(site, code_index, incbin_index), 0) + 1
    loads = literal_loads(image, code_rows, ranges)
    return {"ranges": ["0x%X-0x%X" % pair for pair in ranges],
            "sites": len(found),
            "site_kinds": buckets,
            "literal_loads": len(loads),
            "literal_sites": [{"site": "0x%X" % site, "literal": "0x%X" % literal,
                               "target": "0x%X" % target} for site, literal, target in loads],
            "denominator": {"code_rows": len(code_rows),
                            "code_bytes": sum(length for _, length, _, _ in code_rows),
                            "ledger_rows": len(rows)}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--range", action="append", required=True, dest="ranges",
                        help="START-END in hex, repeatable")
    parser.add_argument("--ledger", default="work/ledger.csv")
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    image = open(args.image, "rb").read()
    rows, code_rows = ledger_rows(args.ledger)
    result = report(image, [parse_range(text) for text in args.ranges], rows, code_rows)
    print("ranges %s: %d word-aligned site(s) name a byte (%s); %d decoded pc-literal load(s) do"
          % (", ".join(result["ranges"]), result["sites"],
             ", ".join("%s=%d" % item for item in sorted(result["site_kinds"].items())),
             result["literal_loads"]))
    print("denominator: %d ledger rows, %d code rows / %d B"
          % (result["denominator"]["ledger_rows"], result["denominator"]["code_rows"],
             result["denominator"]["code_bytes"]))
    for load in result["literal_sites"]:
        print("  site %(site)s loads literal %(literal)s = %(target)s" % load)
    if args.json:
        with open(args.json, "w", newline="\n", encoding="utf-8") as handle:
            json.dump(result, handle, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
