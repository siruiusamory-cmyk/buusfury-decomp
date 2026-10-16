"""What the emulator actually drew: OAM plus OBJ VRAM to an indexed PNG of the visible sprites.

WHY. Comparison screens are full-screen 240x160 captures, and a claim about one actor made from one of those
was blocked twice: the sprite's shape was broken in BOTH the patched and the unpatched run, which a 4x crop
showed and a full-screen view did not. A picture of exactly the sprites the OAM says are on screen is what
makes "no other actor changed" and "the ported actor is present" checkable as pixels rather than as bank
histograms.

WHERE THE BYTES COME FROM, and why nothing new captures them. `tools/runtime/mapvis001_vram_dump.lua` is
already allowlisted and already writes `vram.bin` (0x06000000, 98304 bytes), `palette.bin` (0x05000000, 1024
bytes = BG then OBJ) and `oam.bin` (0x07000000, 1024 bytes) into the run directory, read-only. The OBJ
window is the second half of VRAM, so this reader takes `vram.bin` from 0x10000 and needs no new observer,
no new allowlist entry and no new runtime surface.

WHAT THIS WRITES, and where. An 8-bit indexed PNG under a path the caller names, by convention under the
ignored `build/` tree. It carries the object palette and index 0 as transparent, so the pixels stay palette
INDICES rather than re-quantised colours; nothing here decodes retail art into a tracked file.

HARDWARE RULES THIS ENCODES (GBATEK), each with the reason it is not a guess:

* a sprite's tile data is 8x8 tiles, left to right then top to bottom - the same order
  `webfoot.formats.sprite_graphics.unswizzle_tiles` already implements, so the unswizzle is reused;
* 8bpp tiles are 64 bytes and the OAM tile number's bit 0 is IGNORED, so the address is `(tile & ~1) * 32`;
* 4bpp tiles are 32 bytes, two pixels per byte, low nibble first, and the pixel's colour is
  `palette_bank * 16 + nibble`, where nibble 0 is transparent;
* OAM attr1 x is a signed 9-bit value, so 256..511 means -256..-1; attr0 y is 8-bit;
* mode 2 means the entry is DISABLED and is never drawn.

The composition is deliberately index-domain only: transparency is "leave the canvas at 0", because the
transparent index for this family is 0 and writing a colour there would show up as a solid block.
"""

from __future__ import annotations

import argparse
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.research import exact_search  # noqa: E402
from tools.webfoot.formats import indexed_png, sprite_graphics  # noqa: E402

SCREEN_WIDTH = 240
SCREEN_HEIGHT = 160
OAM_ENTRY_BYTES = 8
OAM_ENTRIES = 128
OBJ_VRAM_BYTES = 0x8000
#: `vram.bin` is dumped from 0x06000000, and the OBJ window starts at 0x06010000.
VRAM_BIN_OBJ_OFFSET = 0x10000
#: `palette.bin` is dumped from 0x05000000: 512 bytes of BG palette, then the OBJ palette.
PALETTE_BIN_OBJ_OFFSET = 0x200
PALETTE_BYTES = sprite_graphics.PALETTE_BYTES
BANK_ENTRIES = 16
#: A tile number indexes 32-byte slots; an 8bpp tile occupies two of them.
TILE_SLOT_BYTES = 32

ATTR0_Y = 0xFF
ATTR0_MODE_SHIFT = 8
ATTR0_MODE_MASK = 3
ATTR0_MODE_DISABLED = 2
ATTR0_COLOUR_256 = sprite_graphics.ATTR0_COLOUR_256


class OamError(ValueError):
    """Raised when a dump is the wrong size or the palette cannot be read from it."""


@dataclass(frozen=True)
class OamEntry:
    """One 8-byte OAM entry, decoded at the bit positions the hardware reads."""

    index: int
    attr0: int
    attr1: int
    attr2: int

    @property
    def y(self) -> int:
        return self.attr0 & ATTR0_Y

    @property
    def x(self) -> int:
        value = self.attr1 & 0x1FF
        return value - 512 if value >= 256 else value

    @property
    def mode(self) -> int:
        return (self.attr0 >> ATTR0_MODE_SHIFT) & ATTR0_MODE_MASK

    @property
    def enabled(self) -> bool:
        return self.mode != ATTR0_MODE_DISABLED

    @property
    def shape(self) -> int:
        return (self.attr0 >> 14) & 3

    @property
    def size(self) -> int:
        return (self.attr1 >> 14) & 3

    @property
    def colour_256(self) -> bool:
        return bool(self.attr0 & ATTR0_COLOUR_256)

    @property
    def tile(self) -> int:
        return self.attr2 & 0x3FF

    @property
    def palette_bank(self) -> int:
        return (self.attr2 >> 12) & 0xF

    @property
    def priority(self) -> int:
        return (self.attr2 >> 10) & 3

    @property
    def horizontal_flip(self) -> bool:
        return bool(self.attr1 & sprite_graphics.ATTR1_HORIZONTAL_FLIP)

    @property
    def vertical_flip(self) -> bool:
        return bool(self.attr1 & sprite_graphics.ATTR1_VERTICAL_FLIP)

    @property
    def dimensions(self) -> tuple[int, int]:
        if self.shape >= len(sprite_graphics.OBJECT_DIMENSIONS):
            raise OamError(f"OAM entry {self.index} uses reserved shape "
                           f"{self.shape}; the hardware does not draw it")
        return sprite_graphics.OBJECT_DIMENSIONS[self.shape][self.size]

    def describe(self) -> str:
        width, height = self.dimensions
        return (f"entry {self.index:3d} at ({self.x:4d},{self.y:3d}) {width}x{height} "
                f"{'8bpp' if self.colour_256 else '4bpp'} tile {self.tile} bank "
                f"{self.palette_bank} priority {self.priority}"
                f"{' hflip' if self.horizontal_flip else ''}"
                f"{' vflip' if self.vertical_flip else ''}")


@dataclass(frozen=True)
class Composite:
    """The composed screen: palette indices, the entries that contributed and what was skipped."""

    canvas: bytes
    width: int
    height: int
    drawn: tuple[OamEntry, ...]
    skipped: tuple[str, ...]

    @property
    def painted(self) -> int:
        return sum(1 for index in self.canvas if index)

    def painted_banks(self) -> list[int]:
        """Which of the sixteen 16-entry banks any painted pixel came from, ascending.

        Index 0 is the only transparent value in this family and is in bank 0's range, so it is cleared
        before the slicing: without that, every canvas would report bank 0 as painted.
        """
        mask = exact_search.byte_values(self.canvas) & ~1
        banks = exact_search.chunks_of(mask, BANK_ENTRIES,
                                       count=sprite_graphics.PALETTE_ENTRIES // BANK_ENTRIES)
        return [bank for bank, bits in enumerate(banks) if bits]


def decode_entry(oam: bytes, index: int) -> OamEntry:
    at = index * OAM_ENTRY_BYTES
    if at + OAM_ENTRY_BYTES > len(oam):
        raise OamError(f"OAM entry {index} is outside a {len(oam)}-byte dump")
    attr0 = oam[at] | oam[at + 1] << 8
    attr1 = oam[at + 2] | oam[at + 3] << 8
    attr2 = oam[at + 4] | oam[at + 5] << 8
    return OamEntry(index=index, attr0=attr0, attr1=attr1, attr2=attr2)


def _tile_offset(entry: OamEntry) -> int:
    # A tile number indexes 32-byte slots, and for 8bpp the low bit is IGNORED: tile 5 and tile 4 name the
    # same 64-byte tile. Masking before the multiply is what the hardware does, not a rounding this tool
    # chose, and getting it wrong reads a neighbouring tile - which is how a bank census can name the wrong
    # bank.
    slot = entry.tile & ~1 if entry.colour_256 else entry.tile
    return slot * TILE_SLOT_BYTES


def _pixels_for(entry: OamEntry, objvram: bytes) -> bytes:
    width, height = entry.dimensions
    count = sprite_graphics.tile_byte_count(width, height, colour_256=entry.colour_256)
    start = _tile_offset(entry)
    # The window is 32 KiB and a tile number is ten bits, so this bound cannot fire on a well-formed dump;
    # it is kept because the tile number is file data and a short window should refuse rather than read past.
    if start + count > len(objvram):
        raise OamError(f"entry {entry.index}: tile {entry.tile} needs bytes "
                       f"{start}..{start + count} of a {len(objvram)}-byte OBJ window")
    pixels = sprite_graphics.unswizzle_tiles(objvram[start:start + count], width, height,
                                             colour_256=entry.colour_256)
    if entry.horizontal_flip or entry.vertical_flip:
        rows = [pixels[y * width:(y + 1) * width] for y in range(height)]
        if entry.horizontal_flip:
            rows = [row[::-1] for row in rows]
        if entry.vertical_flip:
            rows = rows[::-1]
        pixels = b"".join(rows)
    return pixels


def compose(oam: bytes, objvram: bytes, *, width: int = SCREEN_WIDTH,
            height: int = SCREEN_HEIGHT) -> Composite:
    """Every enabled entry drawn into one palette-index canvas, lowest priority entry last on top.

    The draw order is the OAM order, which is what the hardware uses within one priority: a lower entry
    number is drawn first and a later entry overwrites it. Priority is recorded per entry and reported, not
    reordered here, because reordering would be a claim about layering this tool has not measured.
    """
    if len(oam) != OAM_ENTRIES * OAM_ENTRY_BYTES:
        raise OamError(f"OAM dump is {len(oam)} bytes, expected "
                       f"{OAM_ENTRIES * OAM_ENTRY_BYTES}")
    if len(objvram) != OBJ_VRAM_BYTES:
        raise OamError(f"OBJ VRAM window is {len(objvram)} bytes, expected {OBJ_VRAM_BYTES}")
    canvas = bytearray(width * height)
    drawn: list[OamEntry] = []
    skipped: list[str] = []
    for index in range(OAM_ENTRIES):
        entry = decode_entry(oam, index)
        if not entry.enabled:
            continue
        try:
            pixels = _pixels_for(entry, objvram)
        except OamError as error:
            skipped.append(str(error))
            continue
        sprite_width, sprite_height = entry.dimensions
        for y in range(sprite_height):
            screen_y = entry.y + y
            if not 0 <= screen_y < height:
                continue
            for x in range(sprite_width):
                screen_x = entry.x + x
                if not 0 <= screen_x < width:
                    continue
                value = pixels[y * sprite_width + x]
                if entry.colour_256:
                    colour = value if value else None
                else:
                    colour = entry.palette_bank * BANK_ENTRIES + value if value else None
                if colour is not None:
                    canvas[screen_y * width + screen_x] = colour
        drawn.append(entry)
    return Composite(canvas=bytes(canvas), width=width, height=height,
                     drawn=tuple(drawn), skipped=tuple(skipped))


def read_palette(data: bytes, *, offset: int = PALETTE_BIN_OBJ_OFFSET) -> bytes:
    """The 256-entry OBJ palette out of a `palette.bin` (or a bare 512-byte OBJ palette)."""
    if len(data) == PALETTE_BYTES:
        offset = 0
    if offset + PALETTE_BYTES > len(data):
        raise OamError(f"a {len(data)}-byte palette dump has no OBJ palette at {offset:#x}")
    return data[offset:offset + PALETTE_BYTES]


def vram_window(vram: bytes) -> bytes:
    """The OBJ window out of a whole-VRAM dump, or the dump itself when it already is one."""
    if len(vram) == OBJ_VRAM_BYTES:
        return vram
    if len(vram) == VRAM_BIN_OBJ_OFFSET + OBJ_VRAM_BYTES:
        return vram[VRAM_BIN_OBJ_OFFSET:]
    raise OamError(f"a VRAM dump is either {OBJ_VRAM_BYTES} bytes of the OBJ window or "
                   f"{VRAM_BIN_OBJ_OFFSET + OBJ_VRAM_BYTES} bytes of all VRAM, got {len(vram)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_argument_group("capture")
    source.add_argument("--run", type=Path,
                        help="a run directory holding oam.bin, palette.bin and vram.bin")
    source.add_argument("--oam", type=Path, help="an OAM dump (1024 bytes)")
    source.add_argument("--palette", type=Path, help="palette.bin (1024 bytes) or the 512-byte OBJ palette")
    source.add_argument("--vram", type=Path, help="vram.bin (98304 bytes) or a 32768-byte OBJ window")
    parser.add_argument("--out", type=Path, required=True, help="the PNG to write")
    args = parser.parse_args()

    if args.run is not None:
        oam_path, palette_path, vram_path = (args.run / "oam.bin", args.run / "palette.bin",
                                             args.run / "vram.bin")
    else:
        if not (args.oam and args.palette and args.vram):
            parser.error("name --run, or all of --oam, --palette and --vram")
        oam_path, palette_path, vram_path = args.oam, args.palette, args.vram

    held = [path for path in (oam_path, palette_path, vram_path) if not path.is_file()]
    if held:
        raise SystemExit("missing dump file(s): " + ", ".join(str(path) for path in held))

    composite = compose(oam_path.read_bytes(), vram_window(vram_path.read_bytes()))
    palette = sprite_graphics.Palette(
        raw=struct.unpack("<256H", read_palette(palette_path.read_bytes())))

    for entry in composite.drawn:
        print(entry.describe())
    for note in composite.skipped:
        print(f"SKIPPED: {note}")
    banks = composite.painted_banks()
    print(f"{len(composite.drawn)} enabled entr(ies), {composite.painted} painted pixel(s), "
          f"painted palette banks {banks}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(indexed_png.encode(composite.canvas, composite.width, composite.height,
                                            palette.rgb, transparent_index=0))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
