"""Which residual-ledger rows a static recompilation's named function entries fall inside.

A static recompilation names the addresses it treats as function entries: `<recomp>/game.toml` carries
one `[[extra_func]]` per address (plus `[[jump_table]]`). That list is an EXTERNAL claim - a lead, not
evidence - so this tool only answers the two questions a lead can answer before any conversion:

  * which `docs/research/RESIDUAL_LEDGER.csv` row holds the address (half-open `[start,end)`, P-457);
  * with `--walk`, what this repository's own prover makes of a walk from that address inside that row
    (`thumb_bodies.walk` + `thumb_bodies.returns`): a return, a walk that leaves the row, or bytes that
    are not ARMv4T Thumb.

Nothing here promotes anything. A lead becomes source only through `thumb_body_convert` and the gate.

    python tools/research/recomp_leads.py --game-toml PATH          # the row table
    python tools/research/recomp_leads.py --game-toml PATH --walk   # + the prover's verdict per entry
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LEDGER = os.path.join(ROOT, "docs", "research", "RESIDUAL_LEDGER.csv")
ROM_BASE = 0x08000000
ROM_END = ROM_BASE + 0x00800000
SECTION = re.compile(r"^\[\[(\w+)\]\]$")
FIELD = re.compile(r"^(\w+)\s*=\s*(.+)$")
ENTRY_KINDS = ("extra_func", "jump_table")


def entries(path):
    out = []
    kind = None
    low = None
    for line in open(path, encoding="utf-8", errors="replace"):
        text = line.strip()
        found = SECTION.match(text)
        if found:
            kind = found.group(1) if found.group(1) in ENTRY_KINDS else None
            field = None
            continue
        found = FIELD.match(text)
        if not found or kind is None:
            continue
        if found.group(1) == "addr":
            value = int(found.group(2).strip().strip('"'), 16)
            if ROM_BASE <= value < ROM_END:
                out.append((value - ROM_BASE, kind))
    return sorted(out)


def leads(found, ledger):
    out = []
    for row in ledger:
        start, end = int(row["start"], 16), int(row["end"], 16)
        mine = [offset for offset, _kind in found if start <= offset < end]
        if mine:
            out.append({"start": start, "end": end, "bytes": end - start,
                        "region": row.get("region", ""), "status": row.get("status", ""),
                        "attempts": row.get("attempts", ""), "entries": mine})
    return out


def read_ledger(path=LEDGER):
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle))


def verdict(row, offset):
    import thumb_bodies

    span = (row["start"], row["end"])
    body = thumb_bodies.walk(span, [(offset, "recomp", "recomp entry", "lead")])
    walked = "%d B walked" % body.walked
    if not body.code:
        why = body.stops[0][1] if body.stops else "the walk reached no instruction"
        return "no-code", why
    if thumb_bodies.returns(body):
        return "returns", walked
    if body.stops:
        return "stops", "stops at 0x%06x: %s (%s)" % (body.stops[0][0], body.stops[0][1], walked)
    if body.targets:
        return "leaves", "the walk leaves the row (%s, %d exit(s))" % (walked, len(body.targets))
    return "no-exit", "the walk ends inside the row without a return (%s)" % walked


def summary(rows):
    lines = ["| row | bytes | region | status | recomp entry | verdict |",
             "|---|---|---|---|---|---|"]
    for row in rows:
        for offset in row["entries"]:
            label, detail = verdict(row, offset)
            lines.append("| `0x%06x..0x%06x` | %d | %s | %s | `0x%08x` | %s - %s |"
                         % (row["start"], row["end"], row["bytes"], row["region"], row["status"],
                            ROM_BASE + offset, label, detail))
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game-toml", required=True,
                        help="the recompilation's game.toml (read only; never copied into this tree)")
    parser.add_argument("--walk", action="store_true",
                        help="also run the prover's walk from each entry, inside its own ledger row")
    args = parser.parse_args(argv)
    found = entries(args.game_toml)
    rows = leads(found, read_ledger())
    print("entries at a ROM address: %d, ledger rows they fall inside: %d (of %d rows), "
          "%d B" % (len(found), len(rows), len(read_ledger()),
                    sum(row["bytes"] for row in rows)))
    if args.walk:
        for line in summary(rows):
            print(line)
    else:
        for row in rows:
            print("0x%06x..0x%06x %5d B %-18s %s" % (
                row["start"], row["end"], row["bytes"], row["status"],
                ",".join("0x%08x" % (ROM_BASE + offset) for offset in row["entries"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
