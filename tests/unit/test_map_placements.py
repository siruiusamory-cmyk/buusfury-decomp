"""Portable tests for the placement codec. Synthetic bytes only.

No ROM bytes appear here: every fixture is built from the family's documented
constants, so these run without the canonical image. The ROM-gated corpus proofs
live in `tests/integration/test_local_maps_rom.py`.
"""

from __future__ import annotations

import struct

import pytest

from tools.webfoot.formats.map_placements import (
    FACTORY_RAW,
    PLACEMENT_SIZE,
    RECORD_TAIL,
    ROM_BASE,
    MapPlacementLengthError,
    MapPlacementShapeError,
    MapPlacementValueError,
    PlacementRecord,
    is_placement_record,
    iter_placement_offsets,
    read_placement_record,
)


IMAGE_SIZE = 0x2000


def record_bytes(
    *,
    flags: int = 0x00000000,
    type_raw: int = 0x0000001C,
    position: int = 0x0041003C,
    id_raw: int = 0x0000002B,
    tail: tuple[int, int, int] = RECORD_TAIL,
) -> bytes:
    """One well-formed record, matching the shape measured from the ROM."""
    return struct.pack(
        "<8I", FACTORY_RAW, flags, type_raw, position, id_raw, *tail
    )


def image_with(records: dict[int, bytes], pointers: dict[int, int]) -> bytearray:
    """A synthetic image holding `records` at offsets and `pointers` as words."""
    data = bytearray(IMAGE_SIZE)
    for offset, blob in records.items():
        data[offset : offset + len(blob)] = blob
    for offset, value in pointers.items():
        struct.pack_into("<I", data, offset, value)
    return data


def test_a_record_round_trips_to_exactly_its_original_bytes() -> None:
    original = record_bytes()
    assert PlacementRecord.from_bytes(original).to_bytes() == original


def test_every_word_survives_decode_unchanged() -> None:
    original = record_bytes(flags=0x000200A3, type_raw=0x44, position=0x01B101A9)
    record = PlacementRecord.from_bytes(original)
    assert record.factory_raw == FACTORY_RAW
    assert record.flags_raw == 0x000200A3
    assert record.type_raw == 0x44
    assert record.position_raw == 0x01B101A9
    assert (record.tail0_raw, record.tail1_raw, record.tail2_raw) == RECORD_TAIL


def test_unknown_words_are_preserved_rather_than_normalised() -> None:
    """`flags_raw`, `type_raw` and `id_raw` have UNKNOWN semantics.

    A value this toolkit cannot interpret must still survive a round trip
    byte-for-byte, including values that look like padding or like a pointer.
    """
    original = record_bytes(flags=0xFFFFFFFF, type_raw=0x00000000, id_raw=0x08001234)
    assert PlacementRecord.from_bytes(original).to_bytes() == original


def test_a_short_record_is_refused() -> None:
    with pytest.raises(MapPlacementLengthError):
        PlacementRecord.from_bytes(record_bytes()[:-1])


def test_a_word_wider_than_32_bits_is_refused_at_encode() -> None:
    record = PlacementRecord(
        factory_raw=FACTORY_RAW,
        flags_raw=0x1_0000_0000,
        type_raw=0,
        position_raw=0,
        id_raw=0,
        descriptor_pointer_raw=RECORD_TAIL[0],
        child_pointers_raw=(RECORD_TAIL[2],),
    )
    with pytest.raises(MapPlacementValueError):
        record.to_bytes()


def test_the_position_halfwords_split_the_word_low_first() -> None:
    record = PlacementRecord.from_bytes(record_bytes(position=0x0041003C))
    assert record.position_low == 0x003C
    assert record.position_high == 0x0041


def test_editing_the_position_changes_only_that_word() -> None:
    original = record_bytes(position=0x0041003C)
    record = PlacementRecord.from_bytes(original)
    edited = record.with_position(low=0x004C, high=0x0041).to_bytes()
    differing = [i for i in range(PLACEMENT_SIZE) if edited[i] != original[i]]
    assert differing == [12]


def test_a_position_halfword_out_of_range_is_refused_before_it_wraps() -> None:
    """An overflowing halfword must not silently corrupt its neighbour."""
    record = PlacementRecord.from_bytes(record_bytes())
    with pytest.raises(MapPlacementValueError):
        record.with_position(low=0x10000, high=0)
    with pytest.raises(MapPlacementValueError):
        record.with_position(low=0, high=-1)


def test_shape_detection_requires_both_the_factory_word_and_the_tail() -> None:
    data = image_with({0x100: record_bytes()}, {})
    assert is_placement_record(data, 0x100)

    wrong_head = image_with({0x100: record_bytes()}, {0x100: FACTORY_RAW + 2})
    assert not is_placement_record(wrong_head, 0x100)

    wrong_tail = image_with({0x100: record_bytes()}, {0x114: 0xDEADBEEF})
    assert not is_placement_record(wrong_tail, 0x100)


def test_a_record_running_past_the_end_of_the_image_is_not_a_record() -> None:
    data = bytearray(record_bytes())
    assert not is_placement_record(data, 1)
    assert not is_placement_record(data, -1)


def test_reading_bytes_that_are_not_this_family_is_refused() -> None:
    data = image_with({}, {})
    with pytest.raises(MapPlacementShapeError):
        read_placement_record(data, 0x100)


def test_the_walk_returns_every_record_an_array_points_at() -> None:
    records = {0x400: record_bytes(), 0x420: record_bytes(), 0x440: record_bytes()}
    pointers = {
        0x100: ROM_BASE + 0x400,
        0x104: ROM_BASE + 0x420,
        0x108: ROM_BASE + 0x440,
    }
    data = image_with(records, pointers)
    assert iter_placement_offsets(data, 0x100) == (0x400, 0x420, 0x440)


def test_the_walk_stops_at_the_first_word_that_is_not_a_record_pointer() -> None:
    """The declared count does not bound the array; the shape test does."""
    records = {0x400: record_bytes(), 0x420: record_bytes()}
    pointers = {
        0x100: ROM_BASE + 0x400,
        0x104: ROM_BASE + 0x420,
        0x108: 0x00000001,
        0x10C: ROM_BASE + 0x400,
    }
    data = image_with(records, pointers)
    assert iter_placement_offsets(data, 0x100) == (0x400, 0x420)


def test_the_walk_stops_at_a_pointer_leaving_the_cartridge_window() -> None:
    data = image_with({0x400: record_bytes()}, {0x100: ROM_BASE + 0x400, 0x104: 0x02000000})
    assert iter_placement_offsets(data, 0x100) == (0x400,)


def test_an_array_pointing_at_nothing_yields_no_records() -> None:
    data = image_with({}, {0x100: ROM_BASE + 0x400})
    assert iter_placement_offsets(data, 0x100) == ()


def test_the_walk_is_deterministic_for_the_same_bytes() -> None:
    records = {0x400: record_bytes(), 0x420: record_bytes()}
    pointers = {0x100: ROM_BASE + 0x400, 0x104: ROM_BASE + 0x420, 0x108: 0}
    data = image_with(records, pointers)
    assert iter_placement_offsets(data, 0x100) == iter_placement_offsets(data, 0x100)
