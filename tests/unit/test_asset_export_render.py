"""Portable tests for ASSET-EXPORT-001 rendering primitives.

Synthetic fixtures only: no ROM, no extracted assets. These pin transparent
composition, multipart sprite assembly, tile-sheet layout, palette expansion and
the agreement between the exporter's primitives and the production codec's
layout-independent helpers.
"""

from __future__ import annotations

import pytest

from tools.export import canonical as canon
from tools.export import render
from tools.webfoot.formats import sprite_graphics as sg

PALETTE = tuple((index, (index * 3) % 256, (index * 5) % 256) for index in range(256))


def _table() -> bytes:
    return render.rgba_table(PALETTE)


# --- palette and transparency ------------------------------------------------

def test_index_zero_is_transparent_and_the_rest_opaque():
    table = _table()
    rgba = render.to_rgba(bytes([0, 1, 2]), table)
    assert rgba[3] == 0
    assert rgba[7] == 255
    assert rgba[11] == 255
    assert rgba[4:7] == bytes((1, 3, 5))


def test_rgba_expansion_matches_the_channel_order():
    rgba = render.to_rgba(bytes([7]), _table())
    assert tuple(rgba) == (7, 21, 35, 255)


def test_to_rgba_rejects_a_short_colour_table():
    with pytest.raises(render.RenderError):
        render.to_rgba(b"\x01", b"\x00" * 8)


def test_palette_strip_is_opaque_and_ordered():
    width, height, rgba = render.palette_strip(PALETTE)
    assert (width, height) == (256, 1)
    assert rgba[3] == 255
    assert rgba[0:3] == bytes((0, 0, 0))


def test_backdrop_flattens_index_zero_to_the_backdrop_colour():
    """A composite against a backdrop is the screen view, not a hole."""
    table = _table()
    flat = render.to_rgba(bytes([0, 1, 0, 2]), table, backdrop=(9, 8, 7))
    assert flat[0:4] == bytes((9, 8, 7, 255))
    assert flat[4:8] == bytes((1, 3, 5, 255))
    assert flat[8:12] == bytes((9, 8, 7, 255))
    assert flat[12:16] == bytes((2, 6, 10, 255))


def test_backdrop_leaves_no_transparent_pixel():
    table = _table()
    flat = render.to_rgba(bytes([0, 0, 5, 0, 0, 0]), table, backdrop=(0, 0, 0))
    assert set(flat[3::4]) == {255}


def test_without_a_backdrop_index_zero_stays_transparent():
    table = _table()
    plain = render.to_rgba(bytes([0, 1]), table)
    assert plain[3] == 0
    assert plain[7] == 255


def test_backdrop_rejects_a_bad_channel():
    with pytest.raises(render.RenderError):
        render.to_rgba(b"\x00", _table(), backdrop=(0, 0, 999))


# --- tiling -----------------------------------------------------------------

def test_unswizzle_is_tile_major():
    """Two 8x8 tiles laid out left to right, then the next row."""
    tiles = bytes(range(64)) + bytes(range(64, 128)) + bytes(range(128, 192)) + bytes(range(192, 256))
    linear = render.unswizzle_tiles(tiles, 16, 16, colour_256=True)
    assert linear[0:8] == bytes(range(8))
    assert linear[8:16] == bytes(range(64, 72))
    assert linear[16 * 8 : 16 * 8 + 8] == bytes(range(128, 136))


def test_unswizzle_matches_the_production_codec():
    tiles = bytes((index * 13) % 256 for index in range(64 * 4))
    for width, height in ((8, 8), (16, 16), (32, 32), (16, 8), (64, 32)):
        count = width * height
        payload = bytes((index * 7) % 256 for index in range(count))
        assert render.unswizzle_tiles(payload, width, height, colour_256=True) == (
            sg.unswizzle_tiles(payload, width, height, colour_256=True)
        )
    del tiles


def test_unswizzle_refuses_a_partial_tile():
    with pytest.raises(render.RenderError):
        render.unswizzle_tiles(b"\x00" * 64, 12, 8, colour_256=True)


def test_horizontal_flip_mirrors_rows_only():
    pixels = bytes([1, 2, 3, 4, 5, 6, 7, 8])
    assert render.flip_horizontal(pixels, 4, 2) == bytes([4, 3, 2, 1, 8, 7, 6, 5])


def test_vertical_flip_reverses_row_order():
    pixels = bytes([1, 2, 3, 4, 5, 6, 7, 8])
    assert render.flip_vertical(pixels, 4, 2) == bytes([5, 6, 7, 8, 1, 2, 3, 4])


# --- chunk rendering --------------------------------------------------------

def test_chunk_render_reads_only_the_ten_bit_ordinal():
    char_data = bytearray(2 * canon.BANK_TILE_BYTES)
    char_data[canon.BANK_TILE_BYTES :] = b"\x09" * canon.BANK_TILE_BYTES
    entries = [0] * canon.CHUNK_ENTRY_COUNT
    # Ordinal 1 with a non-zero high nibble still reads ordinal 1: bits 12..15
    # are reserved in canonical data and are never interpreted.
    entries[0] = 1 | 0xF000
    pixels = render.render_chunk(tuple(entries), bytes(char_data))
    assert len(pixels) == canon.CHUNK_PIXELS * canon.CHUNK_PIXELS
    assert set(pixels[: canon.TILE_PIXELS]) == {9}
    assert set(pixels[canon.TILE_PIXELS : 2 * canon.TILE_PIXELS]) == {0}


def test_chunk_render_applies_the_stored_flip_bits():
    """Bits 10 and 11 are the platform's flip selectors and are applied."""
    tile = bytes(range(64))
    char_data = tile
    entries = [0] * canon.CHUNK_ENTRY_COUNT
    plain = render.render_chunk(tuple(entries), char_data)
    entries[0] = canon.TILE_ENTRY_BIT_10
    horizontal = render.render_chunk(tuple(entries), char_data)
    entries[0] = canon.TILE_ENTRY_BIT_11
    vertical = render.render_chunk(tuple(entries), char_data)
    entries[0] = canon.TILE_ENTRY_BIT_10 | canon.TILE_ENTRY_BIT_11
    both = render.render_chunk(tuple(entries), char_data)

    assert plain[0:8] == tile[0:8]
    assert horizontal[0:8] == tile[0:8][::-1]
    assert vertical[0:8] == tile[56:64]
    assert both[0:8] == tile[56:64][::-1]
    assert plain != horizontal != vertical


def test_flip_tile_is_its_own_operation_pair():
    tile = bytes(range(64))
    assert render.flip_tile(tile, False, False) == tile
    assert render.flip_tile(render.flip_tile(tile, True, False), True, False) == tile
    assert render.flip_tile(render.flip_tile(tile, False, True), False, True) == tile


def test_flip_tile_refuses_a_wrong_size():
    with pytest.raises(render.RenderError):
        render.flip_tile(b"\x00" * 10, True, False)


def test_entry_tile_refuses_a_missing_ordinal():
    with pytest.raises(render.RenderError):
        render.entry_tile(bytes(canon.BANK_TILE_BYTES), 5)


def test_chunk_render_refuses_a_missing_tile():
    entries = [5] * canon.CHUNK_ENTRY_COUNT
    with pytest.raises(render.RenderError):
        render.render_chunk(tuple(entries), bytes(canon.BANK_TILE_BYTES))


def test_chunk_render_refuses_a_short_entry_array():
    with pytest.raises(render.RenderError):
        render.render_chunk((0,) * 10, bytes(64))


# --- entry statistics --------------------------------------------------------

def test_entry_stats_separate_the_ordinal_from_the_high_bits():
    from tools.export.buu_resource_export import entry_stats

    entries = (0,) * (canon.CHUNK_ENTRY_COUNT - 3) + (
        5,
        5 | canon.TILE_ENTRY_BIT_10,
        9 | canon.TILE_ENTRY_BIT_11 | 0xF000,
    )
    stats = entry_stats(entries)
    assert stats["tile_ordinal_min"] == 0
    assert stats["tile_ordinal_max"] == 9
    assert stats["distinct_tile_ordinals"] == 3
    assert stats["entry_bit_10_count"] == 1
    assert stats["entry_bit_11_count"] == 1
    assert stats["entry_high_nibble_nonzero_count"] == 1

def test_composition_is_transparent_where_every_layer_is_zero():
    bottom = (2, 0, 2, 0)
    top = (0, 3, 0, 0)
    composed = render.compose_layers(
        ((1, 0, 2, 2, bytes(bottom)), (0, 1, 2, 2, bytes(top))), 2, 2
    )
    assert composed == bytes((2, 3, 2, 0))


def test_lower_addend_draws_on_top_and_lower_bg_wins_a_tie():
    lower = (7, 0, 1, 1, bytes([7]))
    higher = (3, 1, 1, 1, bytes([3]))
    assert render.compose_layers((lower, higher), 1, 1) == bytes([3])
    tie_a = (5, 0, 1, 1, bytes([4]))
    tie_b = (5, 1, 1, 1, bytes([6]))
    assert render.compose_layers((tie_b, tie_a), 1, 1) == bytes([4])


def test_composition_pads_a_smaller_layer_at_the_origin():
    small = (0, 0, 1, 1, bytes([5]))
    big = (1, 1, 2, 2, bytes([1, 1, 1, 1]))
    composed = render.compose_layers((small, big), 2, 2)
    assert composed == bytes([5, 1, 1, 1])


def test_composition_refuses_an_oversized_layer():
    with pytest.raises(render.RenderError):
        render.compose_layers(((0, 0, 3, 1, bytes([1, 2, 3])),), 2, 1)


# --- sheets -----------------------------------------------------------------

def test_tile_sheet_layout_pads_the_last_row_transparently():
    tiles = tuple(bytes([index + 1] * 64) for index in range(3))
    width, height, sheet = render.tile_sheet(tiles, 2)
    assert (width, height) == (16, 16)
    assert sheet[0] == 1
    assert sheet[8] == 2
    assert sheet[16 * 8] == 3
    assert sheet[16 * 8 + 8] == 0
    assert set(sheet[16 * 8 + 8 : 16 * 9]) == {0}


def test_tile_sheet_needs_whole_tiles():
    with pytest.raises(render.RenderError):
        render.tile_sheet((b"\x00" * 10,), 1)


def test_frame_sheet_uses_the_largest_cell_and_does_not_rescale():
    cells = ((2, 2, bytes([1, 1, 1, 1])), (4, 1, bytes([2, 2, 2, 2])))
    width, height, sheet = render.frame_sheet(cells, 2)
    assert (width, height) == (8, 2)
    assert sheet[0:2] == bytes([1, 1])
    assert sheet[2:4] == bytes([0, 0])
    assert sheet[4:8] == bytes([2, 2, 2, 2])


def test_frame_sheet_refuses_an_inconsistent_cell():
    with pytest.raises(render.RenderError):
        render.frame_sheet(((2, 2, bytes([1, 2, 3])),), 1)


# --- multipart frame assembly ------------------------------------------------

def _frame(pieces, width, height, min_x, min_y) -> canon.FrameRecord:
    records = []
    for index, (x, y, dim_0, dim_1, attributes, graphics) in enumerate(pieces):
        records.append(
            canon.PieceRecord(
                index=index,
                address=0x08000000 + index * canon.PIECE_RECORD_SIZE,
                x=x,
                y=y,
                dim_0=dim_0,
                dim_1=dim_1,
                attributes=attributes,
                graphics_address=graphics,
            )
        )
    return canon.FrameRecord(
        address=0x08000000,
        piece_count=len(records),
        min_x=min_x,
        min_y=min_y,
        width=width,
        height=height,
        pieces=tuple(records),
    )


def test_multipart_frame_places_pieces_at_their_offsets():
    """Two 8x8 pieces side by side in a 16x8 canvas."""
    attribute = canon.ATTR0_COLOUR_256  # shape 0, size 0 -> 8x8
    frame = _frame(
        [
            (0, 0, 8, 8, attribute, 0x08100000),
            (8, 0, 8, 8, attribute, 0x08100040),
        ],
        16,
        8,
        0,
        0,
    )
    graphics = {0x08100000: bytes([1] * 64), 0x08100040: bytes([2] * 64)}
    extents = {0x08100000: (8, 8), 0x08100040: (8, 8)}
    pixels = render.assemble_frame(frame, graphics, extents)
    assert len(pixels) == 128
    assert set(pixels[0:8]) == {1}
    assert set(pixels[8:16]) == {2}
    assert set(pixels[128 - 8 :]) == {2}


def test_multipart_frame_honours_the_stored_horizontal_flip():
    attribute = canon.ATTR0_COLOUR_256
    flipped = attribute | (canon.ATTR1_HORIZONTAL_FLIP << 16)
    frame = _frame([(0, 0, 8, 8, flipped, 0x08100000)], 8, 8, 0, 0)
    row = bytes([1, 2, 3, 4, 5, 6, 7, 8])
    graphics = {0x08100000: row * 8}
    extents = {0x08100000: (8, 8)}
    pixels = render.assemble_frame(frame, graphics, extents)
    assert pixels[0:8] == row[::-1]


def test_frame_assembly_uses_the_stored_bounding_box_origin():
    attribute = canon.ATTR0_COLOUR_256
    frame = _frame([(3, 4, 8, 8, attribute, 0x08100000)], 8, 8, 3, 4)
    graphics = {0x08100000: bytes([9] * 64)}
    extents = {0x08100000: (8, 8)}
    assert render.assemble_frame(frame, graphics, extents) == bytes([9] * 64)


def test_frame_assembly_refuses_a_piece_outside_the_box():
    attribute = canon.ATTR0_COLOUR_256
    frame = _frame([(0, 0, 8, 8, attribute, 0x08100000)], 7, 8, 0, 0)
    graphics = {0x08100000: bytes([9] * 64)}
    extents = {0x08100000: (8, 8)}
    with pytest.raises(render.RenderError):
        render.assemble_frame(frame, graphics, extents)


def test_frame_assembly_refuses_an_undecoded_container():
    attribute = canon.ATTR0_COLOUR_256
    frame = _frame([(0, 0, 8, 8, attribute, 0x08100000)], 8, 8, 0, 0)
    with pytest.raises(render.RenderError):
        render.assemble_frame(frame, {}, {})


def test_frame_assembly_leaves_index_zero_pixels_transparent_in_the_canvas():
    attribute = canon.ATTR0_COLOUR_256
    frame = _frame([(0, 0, 8, 8, attribute, 0x08100000)], 8, 8, 0, 0)
    source = bytearray(64)
    source[0] = 5
    graphics = {0x08100000: bytes(source)}
    extents = {0x08100000: (8, 8)}
    pixels = render.assemble_frame(frame, graphics, extents)
    assert pixels[0] == 5
    assert set(pixels[1:]) == {0}
