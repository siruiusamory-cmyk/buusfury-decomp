"""SPRITE-NEW-RECORD-RUN-001: read-only probe of a map's engine-owned object run.

This writes nothing and changes nothing. It answers one structural question for
one map: are the records an uncounted map object array points at a contiguous
run with a fixed stride, or an arbitrary set of individually placed records?

The engine's own traversal contract is already proven (BUU_MAP_OBJECT_ARRAYS.md):
MapEntry+0x04 is a byte count read with ``ldrb``, MapEntry+0x14 is the pointer
array base, and slot ``i`` is the word at ``base + 4 * i`` with no sentinel and
no terminator. This probe reads those bytes and reports what they point at, so a
claim about run shape is a measurement rather than an assumption.

    python -m tools.research.record_run_probe <rom> --map 102
"""

from __future__ import annotations

import argparse
import struct
import sys

MAP_ENTRY_TABLE_ROM = 0x0808E2E0
MAP_ENTRY_STRIDE = 0x38
MAP_OBJECT_COUNT_FIELD = 0x04
MAP_OBJECT_ARRAY_FIELD = 0x14
ROM_BASE = 0x08000000

#: The largest record the sibling families are known to use. Records are dumped
#: at this width so a neighbouring record is visible inside the dump.
DUMP_WIDTH = 0x2C


def u32(image: bytes, address: int) -> int:
    return struct.unpack_from("<I", image, address - ROM_BASE)[0]


def u16(image: bytes, address: int) -> int:
    return struct.unpack_from("<H", image, address - ROM_BASE)[0]


def dump(image: bytes, address: int, width: int = DUMP_WIDTH) -> list[str]:
    lines: list[str] = []
    for row in range(0, width, 16):
        chunk = image[address - ROM_BASE + row: address - ROM_BASE + row + 16]
        hexed = " ".join(f"{b:02X}" for b in chunk)
        words = " ".join(
            f"{struct.unpack_from('<I', chunk, o)[0]:08X}"
            for o in range(0, len(chunk) - 3, 4))
        lines.append(f"    +0x{row:02X}  {hexed:<47}  {words}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom")
    parser.add_argument("--map", dest="map_index", type=int, default=102)
    args = parser.parse_args(argv)

    image = open(args.rom, "rb").read()
    print(f"image={args.rom} bytes={len(image)}")

    entry = MAP_ENTRY_TABLE_ROM + MAP_ENTRY_STRIDE * args.map_index
    print(f"\n=== map {args.map_index} MapEntry @ rom 0x{entry:08X} "
          f"(file 0x{entry - ROM_BASE:06X}) ===")
    print("\n".join(dump(image, entry, MAP_ENTRY_STRIDE)))

    count = image[entry - ROM_BASE + MAP_OBJECT_COUNT_FIELD]
    array = u32(image, entry + MAP_OBJECT_ARRAY_FIELD)
    print(f"\ncount (MapEntry+0x04, ldrb) = {count}")
    print(f"array (MapEntry+0x14)       = 0x{array:08X} "
          f"(file 0x{array - ROM_BASE:06X})")

    pointers = [u32(image, array + 4 * i) for i in range(count)]
    print(f"\n=== object array, {count} slots @ 0x{array:08X} ===")
    print("  slot  pointer     file      lead word   family")
    for i, pointer in enumerate(pointers):
        lead = u32(image, pointer)
        print(f"  {i:>4}  0x{pointer:08X}  0x{pointer - ROM_BASE:06X}  "
              f"0x{lead:08X}  {'SIBLING' if lead == 0x08017DA3 else ('PLACEMENT' if lead == 0x0800FD55 else 'OTHER')}")

    if count >= 2:
        print("\n=== slot-to-slot deltas (records are what the slots point at) ===")
        for i in range(count - 1):
            delta = pointers[i + 1] - pointers[i]
            print(f"  slot {i} -> {i + 1}: 0x{delta:X} ({delta})")
        ordered = sorted(pointers)
        print("\n=== address order (records sorted by address) ===")
        deltas = [ordered[i + 1] - ordered[i] for i in range(len(ordered) - 1)]
        print("  sorted pointers: " + " ".join(f"0x{p:08X}" for p in ordered))
        print("  sorted deltas  : " + " ".join(f"0x{d:X}" for d in deltas))

    print("\n=== records ===")
    for i, pointer in enumerate(pointers):
        lead = u32(image, pointer)
        print(f"\n--- slot {i}: 0x{pointer:08X} (file 0x{pointer - ROM_BASE:06X}) "
              f"lead=0x{lead:08X} ---")
        print("\n".join(dump(image, pointer)))
        print(f"    +0x08 u32=0x{u32(image, pointer + 0x08):08X} "
              f"u16x=0x{u16(image, pointer + 0x08):04X} u16y=0x{u16(image, pointer + 0x0A):04X}")
        print(f"    +0x0C u32=0x{u32(image, pointer + 0x0C):08X}")
        print(f"    +0x10 u32=0x{u32(image, pointer + 0x10):08X} (sprite id)")
        print(f"    +0x14 u32=0x{u32(image, pointer + 0x14):08X}")
        print(f"    +0x18 u32=0x{u32(image, pointer + 0x18):08X}")
        print(f"    +0x1C u32=0x{u32(image, pointer + 0x1C):08X}")

    print("\n=== the +0x1C view ===")
    print("  a record pointer P is at 0xP; the byte range one stride on is 0x(P+0x2C).")
    for i, pointer in enumerate(pointers):
        through = pointer + 0x1C
        print(f"  slot {i}: P=0x{pointer:08X}  P+0x1C=0x{through:08X}  "
              f"word there=0x{u32(image, through):08X}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
