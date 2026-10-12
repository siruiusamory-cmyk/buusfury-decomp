"""Focused tests for the three-bank joint palette assembly (the C-c emitter's pure half).

ROM-free: a synthetic 16x16 frame and a synthetic source palette drive the same functions the emitter
calls, in the same order. The load-bearing case is
`test_a_merged_rectangle_outside_the_obj_shape_table_is_never_produced`: an earlier merge produced a
64x16 piece, which no OBJ shape encodes, and the emitter crashed with a KeyError only after writing the
image.
"""

from __future__ import annotations

import struct

from tools.research.cell_split import (
    VALID_RECT,
    attribute_cells,
    build_frame,
    cells_of,
    merge_rects,
    palette_for_bank,
    round_trip_check,
)

BANKS = [frozenset({0x11, 0x22, 0x44, 0x55}), frozenset({0x33}), frozenset({0x66})]


def source_palette() -> bytes:
    """A 256-entry RGB555 palette whose entry N is 0x0100 + N, so a swapped entry is detectable."""
    return b"".join(struct.pack("<H", 0x0100 + index) for index in range(256))


def frame_payload() -> bytes:
    """Three occupied cells, each fitting exactly one bank.

    (0,0) holds 0x11, 0x22 and 0x44, all in bank 0; (8,0) holds 0x33 alone (bank 1); (8,8) holds 0x66
    alone (bank 2). A colour shared by cells of different banks is allowed, but every colour of one cell
    must live in one bank, and that is what this layout exercises.
    """
    payload = bytearray(16 * 16)
    payload[0 * 16 + 0] = 0x11
    payload[0 * 16 + 1] = 0x22
    payload[1 * 16 + 0] = 0x44
    payload[0 * 16 + 8] = 0x33
    payload[15 * 16 + 15] = 0x66
    return bytes(payload)


def test_palette_for_bank_puts_each_colour_in_its_own_slot_from_one():
    palette = palette_for_bank({0x11, 0x22, 0x33}, source_palette())
    assert palette["slots"] == {0x11: 1, 0x22: 2, 0x33: 3}
    assert len(palette["colours"]) == 16
    assert palette["colours"][0] == 0                                  # slot 0 stays transparent
    assert palette["colours"][1] == 0x0100 + 0x11
    assert palette["colours"][3] == 0x0100 + 0x33
    assert palette["colours"][4:] == [0] * 12


def test_every_colour_in_a_bank_reaches_a_non_transparent_slot():
    for bank in BANKS:
        palette = palette_for_bank(bank, source_palette())
        for colour in bank:
            slot = palette["slots"][colour]
            assert slot != 0
            assert palette["colours"][slot] == 0x0100 + colour


def test_attribute_cells_gives_each_occupied_cell_exactly_one_bank():
    cells = cells_of(frame_payload(), size=16)
    attributed = attribute_cells(cells, BANKS)
    assert attributed is not None
    occupied = [cell for cell in cells if cell.colours]
    assert len(attributed) == len(occupied)     # transparent cells need no bank
    assert {bank for _, _, bank in attributed} <= {0, 1, 2}
    top_left = next(entry for entry in attributed if entry[:2] == (0, 0))
    assert top_left[2] == 0                    # 0x11, 0x22 and 0x44 all live in bank 0
    bottom_right = next(entry for entry in attributed if entry[:2] == (8, 8))
    assert bottom_right[2] == 2                # 0x66 only lives in bank 2


def test_attribute_cells_refuses_a_cell_no_bank_holds():
    cells = cells_of(frame_payload(), size=16)
    banks = [frozenset({0x11}), frozenset({0x22}), frozenset({0x33})]
    assert attribute_cells(cells, banks) is None


def test_build_frame_round_trips_every_opaque_pixel_through_the_three_banks():
    payload = frame_payload()
    cells = cells_of(payload, size=16)
    attributed = attribute_cells(cells, BANKS)
    cell_banks = {(x, y): bank for x, y, bank in attributed}
    palettes = [palette_for_bank(bank, source_palette()) for bank in BANKS]
    pieces = build_frame(payload, 16, cell_banks, palettes)
    assert pieces
    assert {bank for *_, bank, _ in pieces} == {0, 1, 2}
    for x, y, width, height, _bank, packed in pieces:
        assert (width, height) in VALID_RECT
        assert len(packed) == width * height // 2
    report = round_trip_check({"payload": payload, "size": 16},
                              [(x, y, w, h, bank) for x, y, w, h, bank, _ in pieces], BANKS)
    assert report["mismatch"] == 0
    assert report["missed"] == 0
    assert report["overlap"] == 0
    assert report["opaque"] == 5

def test_a_merged_rectangle_outside_the_obj_shape_table_is_never_produced():
    """(8,8)+(8,8) stacked four times is 8x32 (valid); the invalid 64x16 style merge must be refused."""
    stacked = [(0, index * 8, 8, 8, 0) for index in range(4)]
    merged = merge_rects(stacked, 64)
    assert merged == [(0, 0, 8, 32, 0)]
    assert (8, 32) in VALID_RECT
    assert (64, 16) not in VALID_RECT
    # A width-only run of eight 8x8 cells would need 64x8, which no shape encodes, so it must stay split.
    run = [(index * 8, 0, 8, 8, 0) for index in range(8)]
    merged_run = merge_rects(run, 64)
    for _, _, width, height, _ in merged_run:
        assert (width, height) in VALID_RECT
    assert len(merged_run) >= 1


def test_merge_rects_never_exceeds_sixteen_tiles():
    wide = [(0, 0, 32, 8, 0), (0, 8, 32, 8, 0)]
    merged = merge_rects(wide, 64)
    for _, _, width, height, _ in merged:
        assert width * height // 64 <= 16
