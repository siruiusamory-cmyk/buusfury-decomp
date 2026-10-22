from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "mapcontainer"))

import spritefamily as sf

SPRITE_BLOCK = (0x3C34D0, 0x6A88AC)
ENDROM_BLOCK = (0x6A88AC, 0x7B79A4)


def main(argv):
    rom = open(argv[1] if len(argv) > 1 else os.path.join(ROOT, "baserom.gba"), "rb").read()
    populations = sf.assert_contract(rom)
    print("populations %s" % populations)
    rows = sf.extents(rom)
    for family in sf.FAMILIES:
        sites = [offset for offset, _ in rows[family]]
        total = sum(size for _, size in rows[family])
        print("%-18s %6d records %7d B  %#x..%#x"
              % (family, len(sites), total, sites[0], sites[-1] + rows[family][-1][1]))
    print("components sum %d B (contract 337,664)"
          % sum(sum(size for _, size in rows[family]) for family in sf.FAMILIES))
    definitions_end = max(offset + size for offset, size in rows[sf.DEFINITION])
    if definitions_end != sf.DEFINITION_END:
        raise SystemExit("the definitions end at %#x, not the table" % definitions_end)
    inside = [(offset, size) for offset, size in rows[sf.ANIMATION] + rows[sf.FRAME]]
    outside = [site for site, size in inside if not (SPRITE_BLOCK[0] <= site
                                                     and site + size <= SPRITE_BLOCK[1])]
    boundary = [site for site in outside if site + 4 <= sf.DEFINITION_START]
    print("animations/frames in the sprite block %d, in the endrom boundary (0x6A88AC..0x6A89D0)"
          " %d, elsewhere %d" % (len(inside) - len(outside), len(boundary),
                                 len(outside) - len(boundary)))
    if len(boundary) != len(outside):
        raise SystemExit("%d animation/frame records are neither" % (len(outside) - len(boundary)))
    fifth = set()
    for site in sf.table_offsets(rom):
        if rom[site + 0x50:site + 0x54] != bytes(4):
            fifth.add(struct.unpack_from("<I", rom, site + 0x50)[0] - sf.ROM_BASE)
    print("fifth family (def+0x50) targets %d, caught by animations/frames: %d"
          % (len(fifth), len(fifth & (set(dict(rows[sf.ANIMATION]))
                                      | set(dict(rows[sf.FRAME]))))))
    round_trip = sf.round_trip(rom)
    identical = sum(pair[0] for pair in round_trip.values())
    total = sum(pair[1] for pair in round_trip.values())
    print("round trip %d/%d byte-identical from parsed fields" % (identical, total))
    print("SPRITE-FULL-001 PROBE OK" if identical == total else "SPRITE-FULL-001 PROBE FAIL")
    return 0 if identical == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
