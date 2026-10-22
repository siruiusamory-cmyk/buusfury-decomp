"""Which MapEntry owns each map-block row of RUNTIME_TARGETS.csv.

The plan's set (a) and set (b) are the map block's census rows; the engine reaches those bytes
through a MapEntry's selector-1 root (`MapEntry+0x2C` array), the root's own `+0x0C`/`+0x10`
child-list pair, and the root record itself (K-214, K-217, K-218). So a row's owner is the map
entry whose chain points into it, and this tool measures that chain at the bytes.

  * `root_record` - the 0x50-byte root the entry's `+0x2C` array holds falls inside the row;
  * `map-root-field` - a word of that root names an address inside the row;
  * `child_list_row` - an entry of the root's `+0x10` array names an address inside the row.

    python tools/research/map_row_owners.py --rom <private copy> --csv docs/research/MAP_ROW_OWNERS.csv
    python tools/research/map_row_owners.py --check

A row with no owner is printed as `owner unknown` and is not guessed.
"""
from __future__ import annotations

import argparse
import csv
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "mapcontainer"))

import mapcontainer  # noqa: E402

TARGETS = os.path.join(ROOT, "docs", "research", "RUNTIME_TARGETS.csv")
CSV_OUT = os.path.join(ROOT, "docs", "research", "MAP_ROW_OWNERS.csv")
FIELDS = ("group", "start", "end", "bytes", "owners", "families")
GROUPS = ("set_b", "set_a")


def rows(path=TARGETS):
    with open(path, newline="") as handle:
        return [{"group": row["group"], "start": int(row["start"], 16), "end": int(row["end"], 16)}
                for row in csv.DictReader(handle) if row["group"] in GROUPS]


def owner_chain(rom):
    u32 = lambda at: struct.unpack_from("<I", rom, at)[0]
    limit = mapcontainer.ROM_BASE + len(rom)

    def list_at(offset):
        if offset + 4 > len(rom):
            return None
        count, tag = rom[offset], struct.unpack_from("<H", rom, offset + 2)[0]
        if not 1 <= count <= mapcontainer.MODE_MAX_CHILDREN or tag not in mapcontainer.MODE_TAGS:
            return None
        if offset + 4 + 4 * count > len(rom):
            return None
        pointers = [u32(offset + 4 + 4 * index) for index in range(count)]
        if not all(mapcontainer.ROM_BASE <= value < limit for value in pointers):
            return None
        return pointers

    chains = []
    for index, slots in enumerate(mapcontainer.root_slots(rom)):
        for root in slots:
            named = [("root_record", root)]
            for at in range(root, root + mapcontainer.ROOT_EXTENT - 3, 4):
                value = u32(at)
                if mapcontainer.ROM_BASE <= value < limit:
                    named.append(("map-root-field", value - mapcontainer.ROM_BASE))
            count, array = u32(root + 0x0C), u32(root + 0x10)
            if not (count and mapcontainer.ROM_BASE <= array < limit):
                chains.append((index, root, named))
                continue
            queue, seen = [], set()
            for element in range(count):
                value = u32(array - mapcontainer.ROM_BASE + 4 * element)
                if mapcontainer.ROM_BASE <= value < limit:
                    queue.append(value - mapcontainer.ROM_BASE)
            for _hop in range(4):
                following = []
                for offset in queue:
                    if offset in seen:
                        continue
                    seen.add(offset)
                    named.append(("child_list_row", offset))
                    for value in list_at(offset) or []:
                        following.append(value - mapcontainer.ROM_BASE)
                queue = following
            chains.append((index, root, named))
    return chains


def table(rom, target_rows):
    chains = owner_chain(rom)
    out = []
    for row in target_rows:
        owners, families = set(), set()
        for index, _root, named in chains:
            hit = [(family, offset) for family, offset in named
                   if row["start"] <= offset < row["end"]]
            if hit:
                owners.add(index)
                families.update(family for family, _ in hit)
        out.append({**row, "bytes": row["end"] - row["start"],
                    "owners": sorted(owners), "families": sorted(families)})
    return out


def csv_text(rows_found):
    lines = [",".join(FIELDS)]
    for row in rows_found:
        cells = []
        for field in FIELDS:
            if field in ("start", "end"):
                cells.append("0x%06x" % row[field])
            elif field == "owners":
                cells.append(";".join("map:%04d" % index for index in row["owners"])
                             or "owner unknown")
            elif field == "families":
                cells.append(";".join(row["families"]))
            else:
                cells.append(str(row[field]))
        lines.append(",".join(cells))
    return "\n".join(lines) + "\n"


def summary(rows_found):
    lines = ["| group | rows | bytes | rows with an owner | distinct maps |",
             "|---|---|---|---|---|"]
    for group in GROUPS:
        mine = [row for row in rows_found if row["group"] == group]
        maps = {index for row in mine for index in row["owners"]}
        lines.append("| `%s` | %d | %d | %d | %d |"
                     % (group, len(mine), sum(row["bytes"] for row in mine),
                        sum(1 for row in mine if row["owners"]), len(maps)))
    owners = {index for row in rows_found for index in row["owners"]}
    lines.append("| **total** | **%d** | **%d** | **%d** | **%d** |"
                 % (len(rows_found), sum(row["bytes"] for row in rows_found),
                    sum(1 for row in rows_found if row["owners"]), len(owners)))
    return lines


def check(path=CSV_OUT, target_rows=None, rom_path=None):
    rom = open(rom_path, "rb").read()
    text = csv_text(table(rom, target_rows or rows()))
    with open(path, encoding="ascii") as handle:
        committed = handle.read()
    if committed != text:
        raise SystemExit("%s does not match the bytes: regenerate it" % os.path.relpath(path, ROOT))
    print("CHECK PASS: %s matches the measured ownership" % os.path.relpath(path, ROOT))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rom", required=True, help="a private copy of the canonical image")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    target_rows = rows()
    if args.check:
        check(rom_path=args.rom, target_rows=target_rows)
        return 0
    found = table(open(args.rom, "rb").read(), target_rows)
    for line in summary(found):
        print(line)
    for row in found:
        if not row["owners"]:
            print("owner unknown: %s row 0x%06x..0x%06x" % (row["group"], row["start"], row["end"]))
    if args.write:
        with open(CSV_OUT, "w", encoding="ascii", newline="\n") as handle:
            handle.write(csv_text(found))
        print("wrote %s: %d row(s)" % (os.path.relpath(CSV_OUT, ROOT), len(found)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
