"""Read the ordinary dialogue font out of the canonical image, and find free space.

Two questions this answers before any patch is written.

FONT. The rasteriser FUN_0803F444 takes the glyph's font record from
``*(u32 *)(strip + 0x0C)``, which the runtime measured as ``0x0806EE6C``. For a
glyph code ``g`` it reads ``index = u16[font_base + g*2]``, then the record at
``font_base + index*2``, whose first u16 is the advance width and whose remaining
``width`` u16s are the glyph bitmap. The bitmap is COLUMN major: bit ``r`` of the
``c``-th u16 is the pixel at column ``c``, row ``r``, sixteen rows tall. The
caller computes the same advance, ``x += width + 1``, from the same two u16s, so
this decode is the same data both paths read.

This is what lets the pair of glyphs in the two-glyph proof be chosen by what
they actually look like rather than by a guess about the code-to-letter mapping,
which the previous run left unproven.

FREE SPACE. The diagnostic needs roughly 150 bytes of executable code. The image
is exactly 8 MiB and the GBA mirrors all of it, so a cave grown past the end
would change ``emu:romSize()``. This reports the longest runs of 0x00 and 0xFF
inside the image instead, so the cave sits in space the image already contains.

Read-only: nothing here writes to the ROM.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
ROM_BASE = 0x08000000
FONT_DESCRIPTOR = 0x0806EE6C
GLYPH_HEIGHT = 16


def read_u16(image: bytes, address: int) -> int:
    offset = address - ROM_BASE
    return image[offset] | (image[offset + 1] << 8)


def read_u32(image: bytes, address: int) -> int:
    offset = address - ROM_BASE
    return int.from_bytes(image[offset : offset + 4], "little")


def glyph(image: bytes, font_base: int, code: int):
    index = read_u16(image, font_base + code * 2)
    if index == 0:
        return None
    record = font_base + index * 2
    width = read_u16(image, record)
    if not 0 < width <= 64:
        return None
    columns = [read_u16(image, record + 2 + column * 2) for column in range(width)]
    return width, columns


def art(width: int, columns: list[int]) -> list[str]:
    rows = []
    for row in range(GLYPH_HEIGHT):
        rows.append("".join("#" if columns[c] >> row & 1 else "." for c in range(width)))
    return rows


def free_runs(image: bytes, minimum: int, start_at: int = 0x400000):
    found = []
    for fill in (0x00, 0xFF):
        start = None
        for offset in range(start_at, len(image)):
            if image[offset] == fill:
                if start is None:
                    start = offset
            else:
                if start is not None and offset - start >= minimum:
                    found.append((offset - start, fill, start))
                start = None
        if start is not None and len(image) - start >= minimum:
            found.append((len(image) - start, fill, start))
    found.sort(reverse=True)
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--codes", type=int, nargs="*", default=[])
    parser.add_argument("--widths", action="store_true", help="list every code with a width")
    parser.add_argument("--free", type=int, default=256, help="minimum free run length")
    parser.add_argument("--free-from", type=lambda text: int(text, 0), default=0x400000,
                        help="first file offset to scan for free runs")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    rom = args.rom or root / "roms" / "Dragon Ball Z - Buu's Fury (U).gba"
    digest = hashlib.sha256(rom.read_bytes()).hexdigest()
    if digest != CANONICAL_SHA256:
        raise SystemExit(f"not the canonical image: {digest}")
    image = rom.read_bytes()

    font_descriptor = FONT_DESCRIPTOR
    font_base = read_u32(image, FONT_DESCRIPTOR)
    print(f"image       : {rom}")
    print(f"sha256      : {digest}")
    print(f"font holder : {font_descriptor:#010x}")
    print(f"font base   : {font_base:#010x} (the u32 stored at the holder)")
    print()

    if args.free:
        print(f"longest free runs >= {args.free} bytes, from {args.free_from:#08X}:")
        for length, fill, start in free_runs(image, args.free, args.free_from)[:12]:
            print(f"  {length:8d} bytes of {fill:#04x} at 0x{start:06X} "
                  f"(ROM 0x{start + ROM_BASE:08X})")
        print()

    if args.widths:
        printable = []
        for code in range(0x100):
            record = glyph(image, font_base, code)
            if record:
                printable.append((code, record[0]))
        print(f"codes with a glyph record: {len(printable)} of 256")
        print("code width:", " ".join(f"{c}:{w}" for c, w in printable))
        print()

    for code in args.codes:
        record = glyph(image, font_base, code)
        if not record:
            print(f"code {code}: no glyph record")
            continue
        width, columns = record
        print(f"code {code} ({code:#04x}): width {width}, packed {width} u16, "
              f"index {read_u16(image, font_base + code * 2)}")
        for line in art(width, columns):
            print("   " + line)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
