"""Portable tests for the BG tilemap codec (MAP-VIS-001 Phase 3).

Synthetic fixtures only - no ROM/dump graphics are embedded. A tiny charblock
with two known tiles and a hand-built screenblock let a render/flip bug show up
as a specific wrong pixel rather than a vaguely wrong picture.
"""

from __future__ import annotations

import struct

import pytest

from tools.webfoot.formats import bg_tilemap as bt
from tools.webfoot.formats import sprite_graphics as sg


def _screenblock(entries: dict[int, int]) -> bytes:
    """A 2 KiB screenblock: {flat index -> raw u16 word}, rest zero."""
    words = [0] * bt.SCREEN_ENTRIES
    for index, word in entries.items():
        words[index] = word
    return struct.pack(f"<{bt.SCREEN_ENTRIES}H", *words)


def _vram_with_tiles(tiles: dict[int, bytes], screenblock: bytes,
                     screen_base_block: int) -> bytes:
    """Charblock 0 holding the given 8bpp tiles, screenblock at its base block."""
    vram = bytearray(bt.CHAR_BLOCK_BYTES + bt.SCREEN_BLOCK_BYTES * 4)
    for tile_index, raw in tiles.items():
        assert len(raw) == bt.TILE_BYTES_8BPP
        vram[tile_index * bt.TILE_BYTES_8BPP : (tile_index + 1) * bt.TILE_BYTES_8BPP] = raw
    base = screen_base_block * bt.SCREEN_BLOCK_BYTES
    vram[base : base + bt.SCREEN_BLOCK_BYTES] = screenblock
    return bytes(vram)


def _corner_tile() -> tuple[bytes, bytes]:
    """A tile whose top-left is 1 and bottom-right is 2, everything else 0.

    Swizzled (tile-order) form for VRAM, plus the expected linear 8x8 form.
    """
    linear = bytearray(bt.TILE_BYTES_8BPP)
    linear[0] = 1                      # (col 0, row 0)
    linear[bt.TILE_BYTES_8BPP - 1] = 2  # (col 7, row 7)
    swizzled = sg.swizzle_tiles(bytes(linear), 8, 8, colour_256=True)
    return swizzled, bytes(linear)


# --- screen entry ------------------------------------------------------------

def test_screen_entry_decodes_all_fields() -> None:
    # tile 0x123, H-flip, V-flip, palette bank 0xA
    entry = bt.ScreenEntry.decode(0xA000 | 0x800 | 0x400 | 0x123)
    assert entry.tile_index == 0x123
    assert entry.h_flip is True
    assert entry.v_flip is True
    assert entry.palette_bank == 0xA


def test_screen_entry_masks_tile_index_to_ten_bits() -> None:
    # bits above 9 belong to flip/bank, not the tile index.
    entry = bt.ScreenEntry.decode(0xFFFF)
    assert entry.tile_index == 0x3FF


def test_decode_screenblock_yields_1024_entries() -> None:
    block = _screenblock({0: 5, 1023: 7})
    entries = bt.decode_screenblock(block, 0)
    assert len(entries) == bt.SCREEN_ENTRIES
    assert entries[0].tile_index == 5
    assert entries[1023].tile_index == 7


def test_decode_screenblock_past_vram_is_refused() -> None:
    with pytest.raises(bt.BgTilemapError, match="outside VRAM"):
        bt.decode_screenblock(b"\x00" * 16, 0)


# --- render ------------------------------------------------------------------

def test_render_places_tile_at_its_map_position() -> None:
    swizzled, linear = _corner_tile()
    # 2x1 map: entry 0 -> tile 1 (blank), entry 1 -> tile 2 (corner tile).
    block = _screenblock({0: 0, 1: 2})
    vram = _vram_with_tiles({2: swizzled}, block, screen_base_block=1)
    pixels, width, height = bt.render_layer(
        vram, char_base_block=0, screen_base_block=1,
        map_width_tiles=2, map_height_tiles=1, color_256=True,
    )
    assert (width, height) == (16, 8)
    # The corner tile is the RIGHT tile: its (0,0)=1 lands at pixel column 8.
    assert pixels[8] == 1
    # Its (7,7)=2 lands at the bottom-right of the whole 16x8 buffer.
    assert pixels[width * height - (width - 15)] == 2
    # Left tile is blank.
    assert pixels[0] == 0


def test_h_flip_mirrors_columns() -> None:
    swizzled, _ = _corner_tile()
    block = _screenblock({0: 0x400 | 1})  # H-flip, tile 1
    vram = _vram_with_tiles({1: swizzled}, block, screen_base_block=1)
    pixels, width, _ = bt.render_layer(
        vram, char_base_block=0, screen_base_block=1,
        map_width_tiles=1, map_height_tiles=1, color_256=True,
    )
    # (col 0,row 0)=1 mirrors to col 7 of row 0.
    assert pixels[7] == 1
    assert pixels[0] == 0
    # (col 7,row 7)=2 mirrors to col 0 of row 7.
    assert pixels[7 * width + 0] == 2


def test_v_flip_mirrors_rows() -> None:
    swizzled, _ = _corner_tile()
    block = _screenblock({0: 0x800 | 1})  # V-flip, tile 1
    vram = _vram_with_tiles({1: swizzled}, block, screen_base_block=1)
    pixels, width, _ = bt.render_layer(
        vram, char_base_block=0, screen_base_block=1,
        map_width_tiles=1, map_height_tiles=1, color_256=True,
    )
    # (col 0,row 0)=1 mirrors to row 7, col 0.
    assert pixels[7 * width + 0] == 1
    # (col 7,row 7)=2 mirrors to row 0, col 7.
    assert pixels[7] == 2


def test_hv_flip_together_is_a_180_rotation() -> None:
    swizzled, _ = _corner_tile()
    block = _screenblock({0: 0x400 | 0x800 | 1})
    vram = _vram_with_tiles({1: swizzled}, block, screen_base_block=1)
    pixels, width, _ = bt.render_layer(
        vram, char_base_block=0, screen_base_block=1,
        map_width_tiles=1, map_height_tiles=1, color_256=True,
    )
    # (0,0)=1 -> bottom-right; (7,7)=2 -> top-left.
    assert pixels[7 * width + 7] == 1
    assert pixels[0] == 2


def test_tile_index_beyond_base_charblock_is_allowed_when_in_vram() -> None:
    # An 8bpp tile index past 255 is NOT clamped to the base charblock: the
    # fetch reads into following VRAM. Map 40 relies on this. Tile 300 lands at
    # 0x4B00, in-bounds of the helper's 0x6000-byte VRAM.
    swizzled, _ = _corner_tile()
    vram = bytearray(bt.CHAR_BLOCK_BYTES + bt.SCREEN_BLOCK_BYTES * 4)
    vram[300 * bt.TILE_BYTES_8BPP : 301 * bt.TILE_BYTES_8BPP] = swizzled
    base = 1 * bt.SCREEN_BLOCK_BYTES
    vram[base : base + bt.SCREEN_BLOCK_BYTES] = _screenblock({0: 300})
    pixels, _, _ = bt.render_layer(
        bytes(vram), char_base_block=0, screen_base_block=1,
        map_width_tiles=1, map_height_tiles=1, color_256=True,
    )
    assert pixels[0] == 1  # the tile actually decoded from index 300


def test_tile_bytes_past_vram_are_refused() -> None:
    # A high index whose bytes run past the end of VRAM fails closed. Tile 1023
    # sits at 0xFFC0, past the helper's 0x6000-byte VRAM.
    block = _screenblock({0: 1023})
    vram = _vram_with_tiles({}, block, screen_base_block=1)
    with pytest.raises(bt.BgTilemapError, match="past VRAM"):
        bt.render_layer(
            vram, char_base_block=0, screen_base_block=1,
            map_width_tiles=1, map_height_tiles=1, color_256=True,
        )


def test_char_base_block_past_vram_is_refused() -> None:
    vram = b"\x00" * (bt.CHAR_BLOCK_BYTES + bt.SCREEN_BLOCK_BYTES)
    with pytest.raises(bt.BgTilemapError, match="outside VRAM"):
        bt.render_layer(
            vram, char_base_block=99, screen_base_block=0,
            map_width_tiles=1, map_height_tiles=1, color_256=True,
        )
