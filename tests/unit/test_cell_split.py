"""Focused tests for the 8x8-cell sub-piece machinery and its pixel round-trip proof.

ROM-free: every case drives the module with a synthetic payload, so CI runs it. The load-bearing case is
`test_a_mapped_slot_compared_with_a_source_index_would_fail`: it pins the distinction that made an
earlier verifier unable to pass (a mapped slot versus a raw source index), so the check this module
exists to make cannot silently regress into one that tests nothing.
"""

from __future__ import annotations

from tools.research.cell_split import (
    Cell,
    cells_of,
    merge_rects,
    pack_rect,
    rects_for_bank,
    round_trip_check,
    slot_maps_for,
    unpack_rect,
)


def build_payload(size=16):
    """A 16x16 payload: index 0 background, a few colours laid out at known positions."""
    payload = bytearray(size * size)
    for y in range(size):
        for x in range(size):
            payload[y * size + x] = 0
    payload[0 * size + 0] = 0x11
    payload[0 * size + 1] = 0x22
    payload[1 * size + 0] = 0x33
    payload[8 * size + 8] = 0x44
    payload[15 * size + 15] = 0x11
    return bytes(payload)


def test_cells_of_splits_into_8x8_cells_and_excludes_transparent():
    cells = cells_of(build_payload(), size=16, step=8)
    assert len(cells) == 4
    assert all(isinstance(cell, Cell) for cell in cells)
    top_left = next(cell for cell in cells if (cell.x, cell.y) == (0, 0))
    assert top_left.colours == frozenset({0x11, 0x22, 0x33})
    bottom_right = next(cell for cell in cells if (cell.x, cell.y) == (8, 8))
    assert bottom_right.colours == frozenset({0x44, 0x11})
    assert next(cell for cell in cells if (cell.x, cell.y) == (8, 0)).colours == frozenset()


def test_pack_and_unpack_round_trip_every_source_index():
    payload = build_payload()
    size = 16
    banks = [frozenset({0x11, 0x22, 0x33, 0x44})]
    rects = [(0, 0, 8, 8, 0), (8, 8, 8, 8, 0)]
    report = round_trip_check({"payload": payload, "size": size}, rects, banks)
    assert report["mismatch"] == 0
    assert report["opaque"] == 5          # (0,0), (1,0), (0,1); (8,8) and (15,15) in the second
    assert report["missed"] == 0
    assert report["overlap"] == 0
    assert report["bytes"] == 8 * 8 // 2 + 8 * 8 // 2


def test_a_mapped_slot_compared_with_a_source_index_would_fail():
    """The original defect, pinned: 0x33 lives at slot 1 of its bank, so slot != source index."""
    payload = build_payload()
    slots = slot_maps_for([frozenset({0x11, 0x22, 0x33})])[0]
    assert slots[0x33] == 3
    packed = pack_rect(payload, 16, 0, 0, 8, 8, slots)
    decoded = unpack_rect(packed, 0, 0, 8, 8, {3: 0x33, 2: 0x22, 1: 0x11, 0: 0})
    assert decoded[(1, 0)] == 0x22          # round trip through the packed byte
    assert slots[0x33] != 0x33              # the mapped value is NOT the source index


def test_a_colour_outside_the_bank_is_refused_not_written_as_zero():
    payload = build_payload()
    banks = [frozenset({0x11, 0x22})]       # 0x33 is outside this bank's palette
    try:
        round_trip_check({"payload": payload, "size": 16}, [(0, 0, 8, 8, 0)], banks)
    except KeyError as error:
        assert "0x33" in str(error)
    else:
        raise AssertionError("a colour outside the bank's palette must be refused")


def test_a_source_pixel_outside_every_rectangle_is_reported_as_missed():
    payload = bytearray(build_payload())
    payload[15 * 16 + 15] = 0             # clear the bottom-right pixel; keep only one there
    payload[15 * 16 + 14] = 0x44          # an opaque pixel the (0,0,8,8) rectangle does not cover
    banks = [frozenset({0x11, 0x22, 0x33, 0x44})]
    report = round_trip_check({"payload": bytes(payload), "size": 16}, [(0, 0, 8, 8, 0)], banks)
    assert report["opaque"] == 3          # the three inside the rectangle
    assert report["mismatch"] == 0
    assert report["missed"] == 2          # (8,8) and (14,15), neither drawn by this rectangle
    assert report["gaps"] == [(8, 8), (14, 15)]


def test_overlapping_rectangles_are_reported():
    payload = build_payload()
    banks = [frozenset({0x11, 0x22, 0x33})]
    rects = [(0, 0, 8, 8, 0), (0, 0, 8, 8, 0)]
    report = round_trip_check({"payload": payload, "size": 16}, rects, banks)
    assert report["overlap"] == 64
    assert report["mismatch"] == 0


def test_rects_for_bank_covers_exactly_the_owned_cells():
    owned = {(0, 0), (8, 0), (0, 8), (8, 8)}
    count, rects = rects_for_bank(owned, 16)
    assert count == 1
    assert rects == [(0, 0, 16, 16)]
    covered = set()
    for x, y, width, height in rects:
        for tile_y in range(y, y + height, 8):
            for tile_x in range(x, x + width, 8):
                covered.add((tile_x, tile_y))
    assert covered == owned


def test_merge_rects_merges_vertically_and_never_exceeds_sixteen_tiles():
    rects = [(0, 0, 8, 8, 0), (0, 8, 8, 8, 0)]
    merged = merge_rects(rects, 64)
    assert merged == [(0, 0, 8, 16, 0)]
    many = [(0, index * 8, 8, 8, 0) for index in range(4)]
    merged = merge_rects(many, 64)
    for x, y, width, height, bank in merged:
        assert width * height // 64 <= 16


def test_merge_rects_leaves_different_banks_apart():
    rects = [(0, 0, 8, 8, 0), (0, 8, 8, 8, 1)]
    assert sorted(merge_rects(rects, 64)) == sorted(rects)
