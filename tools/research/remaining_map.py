from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools", "mapcontainer"))
sys.path.insert(0, os.path.join(ROOT, "tools", "tilebank"))

ROM_SIZE = 8388608
TOKEN = re.compile(r"INCBIN\s+(\S+)")
SLICE = re.compile(r"baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted$")
CLUSTER_GAP = 0x2000


def blocks():
    import generate_mapcontainer as generator
    import generate_tilebank as tilebank

    return (("map-container gap", generator.MAP.start, generator.MAP.end),
            ("sprite-container gap", generator.SPRITE.start, generator.SPRITE.end),
            ("tile-bank gap", tilebank.BLOCK_START, tilebank.BLOCK_START + tilebank.BLOCK_LEN))


def slices():
    out = []
    for name in sorted(os.listdir(os.path.join(ROOT, "asm"))):
        if not name.endswith(".s"):
            continue
        text = open(os.path.join(ROOT, "asm", name), errors="replace").read()
        for match in TOKEN.finditer(text):
            hit = SLICE.search(match.group(1).replace("\\", "/"))
            if hit:
                start, end = int(hit.group(1), 16), int(hit.group(2), 16)
                out.append((start, end - start, name))
    return sorted(out)


def kind_of(start, length, spans):
    for name, low, high in spans:
        if low <= start and start + length <= high:
            return name
    return "unattributed region"


def clusters(rows, gap=CLUSTER_GAP):
    out = []
    for start, length in rows:
        if out and start - out[-1][1] <= gap:
            out[-1] = [out[-1][0], max(out[-1][1], start + length), out[-1][2] + [length]]
        else:
            out.append([start, start + length, [length]])
    return out


def main():
    spans = blocks()
    rows = slices()
    total = sum(length for _, length, _ in rows)
    print("LIVE INCBIN: %d retail slices, %d bytes, %.4f %% of %d"
          % (len(rows), total, 100.0 * total / ROM_SIZE, ROM_SIZE))
    groups = {}
    for start, length, source in rows:
        groups.setdefault(kind_of(start, length, spans), []).append((start, length))
    for name, low, high in spans + (("unattributed region", 0, 0),):
        mine = groups.get(name, [])
        if mine:
            print("  %-22s %4d slices %9d B  %6.4f %%"
                  % (name, len(mine), sum(length for _, length in mine),
                     100.0 * sum(length for _, length in mine) / ROM_SIZE))
    print()
    print("UNATTRIBUTED CLUSTERS (gap <= %#x)" % CLUSTER_GAP)
    for start, end, lengths in clusters(groups.get("unattributed region", [])):
        print("  0x%06x..0x%06x  %3d slices  %8d B  %6.4f %%"
              % (start, end, len(lengths), sum(lengths), 100.0 * sum(lengths) / ROM_SIZE))
    assert total == sum(length for _, length in __import__("gate").incbin_ranges())
    print("SLICE TOTAL MATCHES gate.incbin_ranges()")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
