from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "readability"))

import harness
import rank
import romfile

OBJECT = 0x02000000


def probe(image, address, registers=None):
    registers = {0: OBJECT} if registers is None else registers
    try:
        allowed = harness.body(image, address)
        found = harness.run(image, address, allowed, dict(registers), {})
    except Exception as error:
        return {"address": address, "why": "%s: %s" % (type(error).__name__, error)}
    return {"address": address, "steps": found.steps,
            "writes": [list(write) for write in found.writes],
            "calls": [call for _site, call in found.calls]}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run every address-named start through the behaviour harness.")
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    image = romfile.read_rom(args.rom, harness.ROM_SHA256)
    starts = rank.population()
    named = rank.named(starts)
    rows = [probe(image, start) for start in starts if start not in named]
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")
    ran = sum(1 for row in rows if "why" not in row)
    print("starts=%d unnamed=%d ran=%d refused=%d"
          % (len(starts), len(rows), ran, len(rows) - ran))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
