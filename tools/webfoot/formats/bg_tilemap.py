"""GBA Mode 0 regular tiled background: screen entries, screenblocks, layer render.
**Blocks are addressed by number, never hardcoded.** A charblock is 0x4000 bytes
and a screenblock is 0x800 bytes from the VRAM base; both this module and its
callers work in block indices so the same code renders any layer of any dump.
The manifest block numbers (28/29/30/31 for map 40) are runtime inputs, not
constants here.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct

from . import sprite_graphics


class BgTilemapError(ValueError):
    """Raised when a screen entry, block, or tile reference is out of range."""


CHAR_BLOCK_BYTES = 0x4000

SCREEN_BLOCK_BYTES = 0x800

SCREEN_ENTRIES = SCREEN_BLOCK_BYTES // 2

SCREEN_CHUNK_SIDE = 32

TILE_SIDE = sprite_graphics.TILE_SIDE

TILE_BYTES_8BPP = TILE_SIDE * TILE_SIDE
TILE_BYTES_4BPP = TILE_BYTES_8BPP // 2

TILE_ENTRY_ORDINAL_MASK = 0x03FF
TILE_ENTRY_HORIZONTAL_FLIP = 0x0400
TILE_ENTRY_VERTICAL_FLIP = 0x0800
TILE_ENTRY_PALETTE_BANK_SHIFT = 12
TILE_ENTRY_PALETTE_BANK_MASK = 0xF
TILE_ENTRY_HIGH_NIBBLE = 0xF000
TILE_ENTRY_BIT_10 = TILE_ENTRY_HORIZONTAL_FLIP
TILE_ENTRY_BIT_11 = TILE_ENTRY_VERTICAL_FLIP


@dataclass(frozen=True)
class ScreenEntry:

    tile_index: int
    h_flip: bool
    v_flip: bool
    palette_bank: int

    @classmethod
    def decode(cls, word: int) -> "ScreenEntry":
        if not 0 <= word <= 0xFFFF:
            raise BgTilemapError(f"screen entry {word!r} is not a 16-bit word")
        return cls(
            tile_index=word & TILE_ENTRY_ORDINAL_MASK,
            h_flip=bool(word & TILE_ENTRY_HORIZONTAL_FLIP),
            v_flip=bool(word & TILE_ENTRY_VERTICAL_FLIP),
            palette_bank=(word >> TILE_ENTRY_PALETTE_BANK_SHIFT)
            & TILE_ENTRY_PALETTE_BANK_MASK,
        )


def encode_screen_entry(entry: ScreenEntry) -> int:
    return (
        entry.tile_index
        | (int(entry.h_flip) << 10)
        | (int(entry.v_flip) << 11)
        | (entry.palette_bank << TILE_ENTRY_PALETTE_BANK_SHIFT)
    )


def decode_screenblock(data: bytes, offset: int) -> tuple[ScreenEntry, ...]:
    """Decode a 2 KiB screenblock at ``offset`` into 1024 screen entries."""
    if offset < 0 or offset + SCREEN_BLOCK_BYTES > len(data):
        raise BgTilemapError(f"screenblock at {offset:#x} is outside VRAM")
    words = struct.unpack_from(f"<{SCREEN_ENTRIES}H", data, offset)
    return tuple(ScreenEntry.decode(word) for word in words)


def _flip_tile(tile: bytes, h_flip: bool, v_flip: bool) -> bytes:
    return sprite_graphics.flip_tile(tile, h_flip, v_flip)


def render_layer(
    vram: bytes,
    *,
    char_base_block: int,
    screen_base_block: int,
    map_width_tiles: int,
    map_height_tiles: int,
    color_256: bool,
) -> tuple[bytes, int, int]:
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

    try:
        return render_entries(
            vram,
            entries[:needed],
            map_width_tiles=map_width_tiles,
            map_height_tiles=map_height_tiles,
            color_256=color_256,
            char_offset=char_base,
        )
    except BgTilemapError as exc:
        # Preserve this hardware-facing API's established diagnostic wording.
        raise BgTilemapError(str(exc).replace("character data", "VRAM")) from exc


def entry_tile(
    char_data: bytes,
    word: int,
    *,
    colour_256: bool = True,
) -> bytes:
    entry = ScreenEntry.decode(word)
    tile_bytes = TILE_BYTES_8BPP if colour_256 else TILE_BYTES_4BPP
    src = entry.tile_index * tile_bytes
    if src + tile_bytes > len(char_data):
        raise BgTilemapError(
            f"screen entry references tile {entry.tile_index} at {src:#x}, whose "
            f"{tile_bytes} bytes run past character data ({len(char_data):#x})"
        )
    raw = char_data[src : src + tile_bytes]
    unswizzled = sprite_graphics.unswizzle_tiles(
        raw, TILE_SIDE, TILE_SIDE, colour_256=colour_256
    )
    return _flip_tile(unswizzled, entry.h_flip, entry.v_flip)


def render_entries(
    char_data: bytes,
    entries: tuple[ScreenEntry, ...],
    *,
    map_width_tiles: int,
    map_height_tiles: int,
    color_256: bool,
    char_offset: int = 0,
) -> tuple[bytes, int, int]:
    def entry_at(index: int) -> ScreenEntry:
        try:
            return entries[index]
        except IndexError:
            raise BgTilemapError(
                f"logical layout has {len(entries)} entries, expected "
                f"{map_width_tiles * map_height_tiles}"
            ) from None

    return _render_tiles(
        char_data,
        entry_at,
        count=map_width_tiles * map_height_tiles,
        map_width_tiles=map_width_tiles,
        map_height_tiles=map_height_tiles,
        color_256=color_256,
        char_offset=char_offset,
    )


def render_entry_words(
    char_data: bytes,
    words: tuple[int, ...] | list[int],
    *,
    map_width_tiles: int,
    map_height_tiles: int,
    color_256: bool,
    char_offset: int = 0,
) -> tuple[bytes, int, int]:
    if len(words) != map_width_tiles * map_height_tiles:
        raise BgTilemapError(
            f"logical layout has {len(words)} entries, expected "
            f"{map_width_tiles * map_height_tiles}"
        )

    def entry_at(index: int) -> ScreenEntry:
        return ScreenEntry.decode(words[index])

    return _render_tiles(
        char_data,
        entry_at,
        count=len(words),
        map_width_tiles=map_width_tiles,
        map_height_tiles=map_height_tiles,
        color_256=color_256,
        char_offset=char_offset,
    )


def _render_tiles(
    char_data: bytes,
    entry_at,
    *,
    count: int,
    map_width_tiles: int,
    map_height_tiles: int,
    color_256: bool,
    char_offset: int = 0,
) -> tuple[bytes, int, int]:
    if map_width_tiles <= 0 or map_height_tiles <= 0:
        raise BgTilemapError(
            f"map dimensions must be positive, got "
            f"{map_width_tiles}x{map_height_tiles} tiles"
        )
    if count != map_width_tiles * map_height_tiles:
        raise BgTilemapError(
            f"logical layout has {count} entries, expected "
            f"{map_width_tiles * map_height_tiles}"
        )
    if char_offset < 0 or char_offset > len(char_data):
        raise BgTilemapError(f"character offset {char_offset:#x} is outside data")

    tile_bytes = TILE_BYTES_8BPP if color_256 else TILE_BYTES_4BPP
    width = map_width_tiles * TILE_SIDE
    height = map_height_tiles * TILE_SIDE
    out = bytearray(width * height)

    cache: dict[ScreenEntry, bytes] = {}
    for index in range(count):
        entry = entry_at(index)
        tile = cache.get(entry)
        if tile is None:
            src = char_offset + entry.tile_index * tile_bytes
            if src + tile_bytes > len(char_data):
                tile_x, tile_y = index % map_width_tiles, index // map_width_tiles
                raise BgTilemapError(
                    f"screen entry at tile ({tile_x},{tile_y}) references tile "
                    f"{entry.tile_index} at {src:#x}, whose {tile_bytes} bytes run "
                    f"past character data ({len(char_data):#x})"
                )
            raw = char_data[src : src + tile_bytes]
            unswizzled = sprite_graphics.unswizzle_tiles(
                raw, TILE_SIDE, TILE_SIDE, colour_256=color_256
            )
            tile = _flip_tile(unswizzled, entry.h_flip, entry.v_flip)
            cache[entry] = tile
        base = (index // map_width_tiles) * TILE_SIDE * width + (
            index % map_width_tiles
        ) * TILE_SIDE
        for y in range(TILE_SIDE):
            dst = base + y * width
            out[dst : dst + TILE_SIDE] = tile[y * TILE_SIDE : (y + 1) * TILE_SIDE]

    return bytes(out), width, height
