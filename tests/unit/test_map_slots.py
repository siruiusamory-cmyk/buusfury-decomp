"""Portable tests for the map slot codec. Synthetic bytes only."""

from __future__ import annotations

import struct

import pytest

from tools.webfoot.formats.map_slots import (
    ArrayShape,
    MapSlot,
    MapSlotLengthError,
    MapSlotValueError,
    SLOT_SIZE,
    decode_slot_array,
)


IMAGE_SIZE = 0x1000


def slot_bytes(word0: int, word1: int) -> bytes:
    return struct.pack("<II", word0, word1)


def test_slot_round_trips_exactly():
    data = slot_bytes(0x00020006, 0x08000100)
    assert MapSlot.from_bytes(data).to_bytes() == data


def test_slot_rejects_wrong_length():
    with pytest.raises(MapSlotLengthError):
        MapSlot.from_bytes(b"\x00" * 7)


def test_slot_rejects_out_of_range_word():
    with pytest.raises(MapSlotValueError):
        MapSlot(word0=0x1_0000_0000, word1=0).to_bytes()


def test_slot_rejects_non_integer_word():
    # bool is an int subclass; a True that silently became 1 would encode.
    with pytest.raises(MapSlotValueError):
        MapSlot(word0=True, word1=0).to_bytes()


def test_array_of_confirmed_shape_is_typed():
    data = slot_bytes(0x00020006, 0x08000100) + slot_bytes(0x00020003, 0x08000200)
    array = decode_slot_array(
        data, entry_index=1, file_offset=0x40, image_size=IMAGE_SIZE
    )
    assert array.shape is ArrayShape.TYPED
    assert array.slot_count == 2
    assert array.byte_size == 2 * SLOT_SIZE
    assert array.to_bytes() == data


def test_one_bad_slot_makes_the_whole_array_opaque():
    """Uniformity is per-array, not per-slot: a typed array is wholly typed."""
    data = slot_bytes(0x00020006, 0x08000100) + slot_bytes(0x08293474, 0x080111A9)
    array = decode_slot_array(
        data, entry_index=1, file_offset=0x40, image_size=IMAGE_SIZE
    )
    assert array.shape is ArrayShape.OPAQUE
    assert array.to_bytes() == data


@pytest.mark.parametrize(
    "word0, word1, reason",
    [
        (0x00020006, 0x00000000, "null second word is not a reference"),
        (0x00020006, 0x02000100, "EWRAM is outside the cartridge window"),
        (0x00020006, 0x08000101, "an unaligned pointer is not a struct pointer"),
        (0x08293474, 0x08000100, "a large high halfword is not the confirmed shape"),
        (0x00020006, 0x08000000 + IMAGE_SIZE, "past the end of this image"),
    ],
)
def test_slots_outside_the_confirmed_shape_are_opaque(word0, word1, reason):
    array = decode_slot_array(
        slot_bytes(word0, word1),
        entry_index=0,
        file_offset=0,
        image_size=IMAGE_SIZE,
    )
    assert array.shape is ArrayShape.OPAQUE, reason


def test_opaque_array_round_trips_byte_identically():
    """The whole point of the opaque rung: unknown bytes still rebuild."""
    data = b"".join(
        slot_bytes(value, value ^ 0xA5A5A5A5) for value in range(0x10, 0x20)
    )
    array = decode_slot_array(
        data, entry_index=7, file_offset=0x800, image_size=IMAGE_SIZE
    )
    assert array.shape is ArrayShape.OPAQUE
    assert array.to_bytes() == data


@pytest.mark.parametrize("size", [0, 1, 7, 9, 15])
def test_extent_must_be_whole_slots(size):
    with pytest.raises(MapSlotLengthError):
        decode_slot_array(
            b"\x00" * size, entry_index=0, file_offset=0, image_size=IMAGE_SIZE
        )


def test_decoding_is_deterministic():
    data = slot_bytes(0x00020006, 0x08000100) + slot_bytes(0x11223344, 0x55667788)
    first = decode_slot_array(
        data, entry_index=3, file_offset=0x20, image_size=IMAGE_SIZE
    )
    second = decode_slot_array(
        data, entry_index=3, file_offset=0x20, image_size=IMAGE_SIZE
    )
    assert first == second
