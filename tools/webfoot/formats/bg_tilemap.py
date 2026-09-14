"""GBA Mode 0 regular tiled background: screen entries, screenblocks, layer render.

MAP-VIS-001 Phase 3. A pure codec over ``bytes``: no filesystem, no addresses
beyond the block indices its caller supplies, no game-name branching - the same
discipline as `webfoot.formats.sprite_graphics`. It reuses that module's tile
unswizzle rather than re-deriving GBA tile layout.

**The chain**, straight from GBATEK (verified against the MAP-VIS-001 map 40 VRAM
dump manifest, which supplies the block numbers as runtime inputs):

    DISPCNT mode 0            up to four REGULAR tiled BG layers
      -> BGxCNT               char base block, screen base block, size, colour mode
        -> screenblock        2 KiB = 32x32 u16 screen entries (one 256x256 map)
          -> screen entry     tile index + H/V flip + palette bank
            -> charblock       16 KiB of tile graphics; tile N is 64 (8bpp) or
                               32 (4bpp) bytes from the charblock base
              -> tile          8x8 palette indices, unswizzled and flipped

**Blocks are addressed by number, never hardcoded.** A charblock is 0x4000 bytes
and a screenblock is 0x800 bytes from the VRAM base; both this module and its
callers work in block indices so the same code renders any layer of any dump.
The manifest block numbers (28/29/30/31 for map 40) are runtime inputs, not
constants here.

**Palette bank is decoded but unused at 8bpp.** The screen entry carries a
4-bit palette bank in bits 12-15; at 8bpp a tile indexes the full 256-colour
table and the bank is ignored (GBATEK). The field is decoded so a 4bpp caller
can use it, and left untouched by the 8bpp render path rather than silently
dropped.

**A tile index is not clamped to one charblock.** The screen entry's tile index
is 10 bits (0..1023) and the hardware fetches ``char_base + index * tile_bytes``
without stopping at the 16 KiB base block - an 8bpp index past 255 simply reads
into the following VRAM. Map 40 relies on this (its indices reach ~890). So the
render bound is VRAM extent, not one charblock.

**Fail closed.** A tile whose bytes run past VRAM, or a block number that runs
past VRAM, is a `BgTilemapError`, not a wrap-around read - a garbled layer must
surface as an error, not as plausible-looking wrong pixels.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct

from . import sprite_graphics


class BgTilemapError(ValueError):
    """Raised when a screen entry, block, or tile reference is out of range."""


#: A charblock of tile graphics is 16 KiB from the VRAM base (GBATEK).
CHAR_BLOCK_BYTES = 0x4000

#: A screenblock is 2 KiB = 32x32 u16 screen entries (GBATEK).
SCREEN_BLOCK_BYTES = 0x800

#: Screen entries per screenblock (a 32x32 tile map).
SCREEN_ENTRIES = SCREEN_BLOCK_BYTES // 2

#: Tiles are 8x8 on this hardware, always.
TILE_SIDE = sprite_graphics.TILE_SIDE

#: A single 8x8 tile: 64 bytes at 8bpp, 32 bytes at 4bpp.
TILE_BYTES_8BPP = TILE_SIDE * TILE_SIDE
TILE_BYTES_4BPP = TILE_BYTES_8BPP // 2


@dataclass(frozen=True)
class ScreenEntry:
    """One 16-bit BG screen (map) entry.

    ``palette_bank`` is decoded for completeness; it is ignored by the 8bpp
    render path (an 8bpp tile uses the full 256-colour palette - GBATEK).
    """

    tile_index: int
    h_flip: bool
    v_flip: bool
    palette_bank: int

    @classmethod
    def decode(cls, word: int) -> "ScreenEntry":
        if not 0 <= word <= 0xFFFF:
            raise BgTilemapError(f"screen entry {word!r} is not a 16-bit word")
        return cls(
            tile_index=word & 0x3FF,
            h_flip=bool(word & 0x400),
            v_flip=bool(word & 0x800),
            palette_bank=(word >> 12) & 0xF,
        )


def decode_screenblock(data: bytes, offset: int) -> tuple[ScreenEntry, ...]:
    """Decode a 2 KiB screenblock at ``offset`` into 1024 screen entries."""
    if offset < 0 or offset + SCREEN_BLOCK_BYTES > len(data):
        raise BgTilemapError(f"screenblock at {offset:#x} is outside VRAM")
    words = struct.unpack_from(f"<{SCREEN_ENTRIES}H", data, offset)
    return tuple(ScreenEntry.decode(word) for word in words)


def _flip_tile(tile: bytes, h_flip: bool, v_flip: bool) -> bytes:
    """Apply H/V flip to a linear 8x8 block of indices.

    H-flip mirrors the 8 columns of each row; V-flip mirrors the 8 rows.
    """
    if not h_flip and not v_flip:
        return tile
    rows = [tile[y * TILE_SIDE : (y + 1) * TILE_SIDE] for y in range(TILE_SIDE)]
    if h_flip:
        rows = [row[::-1] for row in rows]
    if v_flip:
        rows = rows[::-1]
    return b"".join(rows)


def render_layer(
    vram: bytes,
    *,
    char_base_block: int,
    screen_base_block: int,
    map_width_tiles: int,
    map_height_tiles: int,
    color_256: bool,
) -> tuple[bytes, int, int]:
    """Render one regular tiled BG layer to linear 8bpp palette indices.

    Returns ``(pixels, width, height)`` where ``width = map_width_tiles * 8`` and
    likewise for height. Each screen entry's tile is fetched from the charblock,
    unswizzled to 8x8 indices via `sprite_graphics.unswizzle_tiles`, flipped, and
    blitted into the layer buffer.

    Fails closed on any block or tile reference that runs past VRAM or past the
    charblock.
    """
    if map_width_tiles <= 0 or map_height_tiles <= 0:
        raise BgTilemapError(
            f"map dimensions must be positive, got "
            f"{map_width_tiles}x{map_height_tiles} tiles"
        )

    char_base = char_base_block * CHAR_BLOCK_BYTES
    if char_base < 0 or char_base + CHAR_BLOCK_BYTES > len(vram):
        raise BgTilemapError(
            f"char base block {char_base_block} ({char_base:#x}) is outside VRAM"
        )

    tile_bytes = TILE_BYTES_8BPP if color_256 else TILE_BYTES_4BPP

    screen_base = screen_base_block * SCREEN_BLOCK_BYTES
    entries = decode_screenblock(vram, screen_base)
    needed = map_width_tiles * map_height_tiles
    if needed > len(entries):
        raise BgTilemapError(
            f"a {map_width_tiles}x{map_height_tiles} map needs {needed} screen "
            f"entries but one screenblock holds only {len(entries)}"
        )

    width = map_width_tiles * TILE_SIDE
    height = map_height_tiles * TILE_SIDE
    out = bytearray(width * height)

    for tile_y in range(map_height_tiles):
        for tile_x in range(map_width_tiles):
            entry = entries[tile_y * map_width_tiles + tile_x]
            src = char_base + entry.tile_index * tile_bytes
            if src + tile_bytes > len(vram):
                raise BgTilemapError(
                    f"screen entry at tile ({tile_x},{tile_y}) references tile "
                    f"{entry.tile_index} at {src:#x}, whose {tile_bytes} bytes run "
                    f"past VRAM ({len(vram):#x}) from char base block "
                    f"{char_base_block}"
                )
            raw = vram[src : src + tile_bytes]
            tile = sprite_graphics.unswizzle_tiles(
                raw, TILE_SIDE, TILE_SIDE, colour_256=color_256
            )
            tile = _flip_tile(tile, entry.h_flip, entry.v_flip)
            base = tile_y * TILE_SIDE * width + tile_x * TILE_SIDE
            for y in range(TILE_SIDE):
                dst = base + y * width
                out[dst : dst + TILE_SIDE] = tile[y * TILE_SIDE : (y + 1) * TILE_SIDE]

    return bytes(out), width, height
