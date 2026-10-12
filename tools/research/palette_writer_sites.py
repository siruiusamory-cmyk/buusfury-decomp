"""Census the OBJ palette write sites, and decode any ROM range as Thumb plus a word dump.

Why it exists: a runtime palette transplant needs a site whose replaced instructions it can afford. K-042
says every OBJ palette write goes through the IWRAM veneers and that the once-per-scene write is a 512-byte
copy of the ROM palette table, but it does not say which sites those are or how much room each has. This
prints all of it: every word-aligned literal holding 0x05000200, every Thumb `ldr` that reaches one, the
instruction window around each site, and the words each site's literals hold.

Invoke:
  python -m tools.research.palette_writer_sites --image RETAIL.gba
  python -m tools.research.palette_writer_sites --image RETAIL.gba --decode 0x08006570 --length 0x20

Read-only: prints; writes nothing.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.research import thumb_disasm as t  # noqa: E402

ROM_BASE = 0x08000000
OBJ_PAL = 0x05000200
ROM_TABLE = 0x0805652C
IWRAM_COPY = 0x08049144
IWRAM_FILL = 0x0804912C


def literals_holding(image: bytes, value: int) -> list[int]:
    """Every word-aligned address whose word equals `value` (stride 4, so no invented sites: P-090)."""
    out = []
    for offset in range(0, len(image) - 4, 4):
        if struct.unpack_from("<I", image, offset)[0] == value:
            out.append(ROM_BASE + offset)
    return out


def thumb_loads_of(image: bytes, literals: set[int]) -> list[tuple[int, int]]:
    """(site, literal) for every Thumb `ldr rX,[pc,#imm]` that reads one of `literals`."""
    found = []
    for start in range(ROM_BASE, ROM_BASE + len(image) - 4, 2):
        halfword = struct.unpack_from("<H", image, start - ROM_BASE)[0]
        if halfword & 0xF800 != 0x4800:
            continue
        literal = ((start + 4) & ~3) + (halfword & 0xFF) * 4
        if literal in literals:
            found.append((start, literal))
    return found


def hexdump(image: bytes, start: int, length: int) -> None:
    offset = start - ROM_BASE
    for row in range(0, length, 16):
        chunk = image[offset + row:offset + row + 16]
        pairs = " ".join(f"{byte:02X}" for byte in chunk)
        print(f"  0x{start + row:08X}  {pairs}")
    first = (start + 3) & ~3
    for address in range(first, start + length - 3, 4):
        word = struct.unpack_from("<I", image, address - ROM_BASE)[0]
        print(f"    word 0x{address:08X} = 0x{word:08X}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", type=Path,
                        default=Path(r"C:\Dev\log1-remake\roms\Dragon Ball Z - Buu's Fury (U).gba"))
    parser.add_argument("--decode", type=lambda text: int(text, 16), default=None)
    parser.add_argument("--length", type=lambda text: int(text, 16), default=0x20)
    args = parser.parse_args()

    image = args.image.read_bytes()
    if args.decode is not None:
        print(f"Thumb decode 0x{args.decode:08X}..0x{args.decode + args.length:08X}")
        sweep = t.linear_thumb(image, args.decode, args.decode + args.length)
        for ins in sweep.instructions:
            print(f"  {ins.address:08X}  {ins.mnemonic:<8} {ins.operands}")
        if sweep.undecodable_halfwords:
            print(f"  undecodable halfwords: {sweep.undecodable_halfwords}")
        hexdump(image, args.decode, args.length)
        return 0

    words = literals_holding(image, OBJ_PAL)
    print(f"{len(words)} word-aligned literal(s) hold 0x{OBJ_PAL:08X}:")
    print("  " + ", ".join(f"0x{address - ROM_BASE:06X}" for address in words))
    sites = thumb_loads_of(image, set(words))
    print(f"\n{len(sites)} Thumb load site(s) reach them:")
    for site, literal in sites:
        sweep = t.linear_thumb(image, site - 8, site + 12)
        listing = " | ".join(f"{ins.address:08X} {ins.mnemonic} {ins.operands}"
                            for ins in sweep.instructions)
        print(f"  site 0x{site:08X} -> literal 0x{literal:08X} (file 0x{literal - ROM_BASE:06X})")
        print(f"      {listing}")
    for target, label in ((IWRAM_COPY, "copy"), (IWRAM_FILL, "fill")):
        sites = t.scan_thumb_bl_callers(image, {target}).get(target, [])
        print(f"\n{label} veneer 0x{target:08X}: {len(sites)} call site(s): "
              + ", ".join(f"0x{site:08X}" for site in sites[:24]))
    print(f"\nthe ROM palette table literal 0x{ROM_TABLE:08X} appears at: "
          + ", ".join(f"file 0x{address - ROM_BASE:06X}" for address in literals_holding(image, ROM_TABLE)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
