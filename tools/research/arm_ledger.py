from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools", "symbols"))

import gate  # noqa: E402
import generate_symbols  # noqa: E402
import arm_bodies  # noqa: E402

LEDGER = os.path.join(ROOT, "work", "ledger.csv")
MANIFEST = os.path.join(ROOT, "build", "arm_bodies", "manifest.json")
ROM_BASE = 0x08000000


def arm_ranges(manifest=None, key="converted"):
    manifest = manifest or MANIFEST
    if not os.path.exists(manifest):
        raise SystemExit("%s is missing: run the converter with --write first" % manifest)
    data = json.load(open(manifest))
    if key == "converted":
        return sorted((entry["start"], entry["end"]) for entry in data["converted"])
    out = []
    for entry in data["rows"]:
        if entry.get("verdict") != "thumb-converted":
            continue
        for start, end in entry.get("runs", []):
            out.append((start, end))
    merged = []
    for start, end in sorted(out):
        if merged and merged[-1][1] == start:
            merged[-1][1] = end
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def covered(rows):
    out = set()
    for offset, length, _isa, _region, _source, _kind, _evidence, _insn in rows:
        out |= set(range(offset, offset + length))
    return out


def relabel(ranges, states):
    out = []
    for start, end in ranges:
        state = generate_symbols.state_at(states, start + ROM_BASE)
        isa = generate_symbols.STATE_KIND[state]
        out.append((start, end, isa, 0 if isa == "data" else end - start))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--manifest", default=MANIFEST)
    parser.add_argument("--key", default="converted", choices=("converted", "runs"))
    parser.add_argument("--region", default="arm_body")
    parser.add_argument("--source", default="asm/*.s")
    args = parser.parse_args(argv)
    if not os.path.exists(os.path.join(ROOT, "build", "buu.map")):
        print("build/buu.map is missing: rebuild before recording ledger rows")
        return 1
    states = generate_symbols.read_map(os.path.join(ROOT, "build", "buu.map"))[1]
    rows = [row for row in gate.ledger_rows() if not row[3].startswith(args.region)]
    dropped = len(gate.ledger_rows()) - len(rows)
    have = covered(rows)
    wanted = relabel(arm_ranges(args.manifest, args.key), states)
    stale = [span for span in wanted if set(range(span[0], span[1])) & have]
    for span in stale:
        raise SystemExit("a converted range 0x%06x..0x%06x is already covered by a ledger row"
                         % (span[0], span[1]))
    added = [(start, end - start, isa, "%s_%06X" % (args.region, start), args.source,
              "transcription", "byte-proven", insn) for start, end, isa, insn in wanted]
    print("converted bodies: %d; replaced ledger rows: %d; bytes: %d; instruction bytes: %d"
          % (len(added), dropped, sum(row[1] for row in added), sum(row[7] for row in added)))
    kinds = {}
    for row in added:
        kinds[row[2]] = kinds.get(row[2], 0) + 1
    print("  isa: %s" % kinds)
    if args.apply and added:
        out = list(rows) + added
        out.sort(key=lambda row: row[0])
        gate.write_ledger(out)
        print("wrote %s: %d rows" % (LEDGER, len(out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
