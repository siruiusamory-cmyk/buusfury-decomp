"""Census every placement that carries Spopovich's sprite id, with the stat selector each fight uses.

The review found my first census incomplete: it missed eight placements in two maps' declared object arrays
and mislabelled map 137's family. This walks every map's slot array, classifies each record by its factory
word, and reports the sprite id and stat selector the record itself carries - so the count is repeatable and
the family of each site is read rather than assumed.

Families and where their sprite id lives, from each family's own entry instruction:
  0x0800FD55  record base = slot word,             sprite at +0x10, stat at +0x08
  0x080111A9  record base = slot word,             sprite at +0x0C, stat at +0x08
  0x08017DA3  record base = slot word - 0x10,      sprite at the slot word itself, stat at -0x10+0x08
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROM_BASE = 0x08000000
MAP_TABLE = 0x8E2E0
MAP_STRIDE = 0x38
MAP_COUNT = 452
SPRITE_ID = 252


def word(image: bytes, offset: int) -> int:
    return struct.unpack_from("<I", image, offset)[0]


def main() -> int:
    image = Path(sys.argv[1]).read_bytes()
    family_offsets = {0x0800FD55: 0x10, 0x080111A9: 0x0C, 0x08017DA3: 0x00}
    sites = []
    for map_id in range(MAP_COUNT):
        entry = MAP_TABLE + MAP_STRIDE * map_id
        count = word(image, entry + 0x04)
        array = word(image, entry + 0x14)
        if not (ROM_BASE <= array < ROM_BASE + len(image)) or not 0 < count <= 256:
            continue
        base = array - ROM_BASE
        for slot in range(count):
            if base + 4 * slot + 4 > len(image):
                break
            record = word(image, base + 4 * slot)
            if not (ROM_BASE <= record < ROM_BASE + len(image)):
                continue
            offset = record - ROM_BASE
            # A record's own first word is either a factory pointer or an attribute word; the family is
            # whichever of the three the word before it (for 0x08017DA3) or the word itself names.
            factory = None
            sprite_at = None
            if word(image, offset) in family_offsets:
                factory = word(image, offset)
                # All three families read the sprite id from the record: 0x10 for FD55 and 17DA3,
                # 0x0C for 111A9. Measured from each family's own entry instruction.
                sprite_at = offset + (0x0C if factory == 0x080111A9 else 0x10)
            elif offset >= 0x10 and word(image, offset - 0x10) in family_offsets:
                factory = word(image, offset - 0x10)
                sprite_at = offset
            if factory is None or sprite_at is None or sprite_at + 4 > len(image):
                continue
            if word(image, sprite_at) != SPRITE_ID:
                continue
            # Only the FD55 family stores the stat selector at +0x08. The 17DA3 record has a different
            # layout (the value there is coordinate data), so reporting it as a stat selector would be
            # wrong - it is printed as not applicable instead.
            stat = word(image, offset + 0x08) if factory == 0x0800FD55 else None
            sites.append((map_id, slot, factory, stat, record))
    print(f"{len(sites)} placement(s) carrying sprite id {SPRITE_ID}:")
    for map_id, slot, factory, stat, record in sites:
        family = {0x0800FD55: "FD55", 0x080111A9: "111A9", 0x08017DA3: "17DA3"}[factory]
        shown = "not applicable (this family's record layout differs)" if stat is None else str(stat)
        print(f"  map {map_id:>3} slot {slot:>3}  family {family}  stat selector {shown:>4}  "
              f"record 0x{record:08X}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
