"""Portable tests for the map-layer handler registry.

Synthetic fixtures only: no ROM, no extracted assets. These pin the two facts the
exporter's map classification depends on after ASSET-EXPORT-MAP-HANDLERS-001:

* which record field each screen-entry handler names its container from, and that
  the reader takes that field from the record's own handler word rather than from a
  fixed offset; and
* the class, graphical and composite-blocking predicates for every handler, so a
  handler cannot silently fall back into a class it does not belong to.
"""

from __future__ import annotations

import struct

import pytest

from tools.export import canonical as canon

GBA = 0x08000000
RECORD_ADDRESS = GBA + 0x100
CONTAINER_ADDRESS = GBA + 0x400
OTHER_CONTAINER_ADDRESS = GBA + 0x1000
IMAGE_SIZE = 0x2000
ENTRY_COUNT = canon.SCREENBLOCK_ENTRY_COUNT
PLANE_BYTES = canon.SCREENBLOCK_DECODED_BYTES


def _entries(first: int) -> bytes:
    return b"".join(struct.pack("<H", (first + index) & 0x3FF) for index in range(ENTRY_COUNT))


def _image(*, handler: int, field: int, declared: int = PLANE_BYTES) -> canon.Rom:
    """A minimal image holding one record and two candidate containers."""
    data = bytearray(IMAGE_SIZE)
    struct.pack_into("<I", data, RECORD_ADDRESS - GBA, handler)
    struct.pack_into("<I", data, RECORD_ADDRESS - GBA + field, CONTAINER_ADDRESS)
    # Every other candidate field names a container of a different plane, so a
    # reader that used the wrong field would return recognisably wrong entries.
    for offset in (0x04, 0x08, 0x1C):
        if offset != field:
            struct.pack_into(
                "<I", data, RECORD_ADDRESS - GBA + offset, OTHER_CONTAINER_ADDRESS
            )
    struct.pack_into("<II", data, CONTAINER_ADDRESS - GBA, 0, declared)
    payload = _entries(0)
    data[CONTAINER_ADDRESS - GBA + 8 : CONTAINER_ADDRESS - GBA + 8 + len(payload)] = (
        payload
    )
    struct.pack_into("<II", data, OTHER_CONTAINER_ADDRESS - GBA, 0, PLANE_BYTES)
    other = _entries(1000)
    data[
        OTHER_CONTAINER_ADDRESS - GBA + 8 : OTHER_CONTAINER_ADDRESS - GBA + 8 + len(other)
    ] = other
    return canon.Rom(bytes(data))


def _record(handler: int, chunk_x: int = 2, chunk_y: int = 2) -> canon.LayerRecord:
    address = (
        canon.ABSENT_LAYER_RECORD
        if handler == canon.ABSENT_LAYER_HANDLER
        else RECORD_ADDRESS
    )
    return canon.LayerRecord(
        slot=0,
        address=address,
        handler=handler,
        chunk_x=chunk_x,
        chunk_y=chunk_y,
        chunk_addresses=(),
        null_chunk_count=0,
    )


# --- the handler registry ----------------------------------------------------

def test_the_registry_names_the_two_screen_entry_handlers_and_their_fields():
    assert canon.SCREENBLOCK_HANDLERS == {0x08007B63: 0x04, 0x0800897B: 0x1C}
    assert canon.screenblock_container_offset(0x08007B63) == 0x04
    assert canon.screenblock_container_offset(0x0800897B) == 0x1C


def test_a_handler_that_is_not_a_screen_entry_layer_is_refused():
    for handler in (0x08008087, 0x08007A41, 0x080088BD, 0):
        with pytest.raises(canon.CanonicalError):
            canon.screenblock_container_offset(handler)


def test_the_constructor_buffered_handler_reads_record_plus_0x04():
    rom = _image(handler=0x08007B63, field=0x04)
    assert canon.read_screenblock_entries(rom, RECORD_ADDRESS) == struct.unpack(
        "<1024H", _entries(0)
    )


def test_the_uploaded_handler_reads_record_plus_0x1c():
    """`0x0800897B`'s method 1 loads `record + 0x1C`, not `record + 0x04`."""
    rom = _image(handler=0x0800897B, field=0x1C)
    assert canon.read_screenblock_entries(rom, RECORD_ADDRESS) == struct.unpack(
        "<1024H", _entries(0)
    )


def test_the_container_field_follows_the_records_own_handler_word():
    """Moving the plane to the other handler's field must change what is read.

    This is the regression that matters: the reader takes the field from the
    record's `+0x00` word, so a record cannot be read at the other handler's
    offset.
    """
    uploaded = _image(handler=0x0800897B, field=0x1C)
    assert canon.read_screenblock_entries(uploaded, RECORD_ADDRESS)[0] == 0
    mismatched = _image(handler=0x0800897B, field=0x04)
    assert canon.read_screenblock_entries(mismatched, RECORD_ADDRESS)[0] == 1000


def test_a_plane_of_the_wrong_declared_size_is_refused():
    rom = _image(handler=0x0800897B, field=0x1C, declared=0x400)
    with pytest.raises(canon.CanonicalError) as excinfo:
        canon.read_screenblock_entries(rom, RECORD_ADDRESS)
    assert "expected 2048" in str(excinfo.value)


# --- the class predicates ----------------------------------------------------

@pytest.mark.parametrize(
    "handler,expected",
    [
        (canon.DOMINANT_LAYER_HANDLER, "dominant"),
        (0x08007B63, "static_graphical_screenblock"),
        (0x0800897B, "static_graphical_screenblock"),
        (0x080088BD, "static_graphical_assembly_unresolved"),
    ],
)
def test_each_handler_gets_its_own_final_class(handler: int, expected: str):
    assert _record(handler).classification == expected


def test_no_known_handler_is_left_unclassified():
    for handler in (0x08008087, 0x08007A41, 0x08007B63, 0x0800897B, 0x080088BD):
        assert _record(handler).classification != "unclassified_handler"


def test_the_absent_placeholder_is_the_only_class_that_draws_nothing():
    assert _record(0x08008087).graphical is True
    assert _record(0x08007B63).graphical is True
    assert _record(0x0800897B).graphical is True
    assert _record(0x080088BD).graphical is True
    assert canon.LayerRecord(
        slot=0,
        address=canon.ABSENT_LAYER_RECORD,
        handler=canon.ABSENT_LAYER_HANDLER,
        chunk_x=0,
        chunk_y=0,
        chunk_addresses=(),
        null_chunk_count=0,
    ).graphical is False
    assert _record(0x08007A41).graphical is False


def test_the_absent_handler_is_only_the_absent_placeholder_on_its_own_record():
    """The shared absent handler at any other record fails closed.

    No such record exists in the canonical image, but the class must not spread
    by handler value alone.
    """
    assert canon.LayerRecord(
        slot=0,
        address=RECORD_ADDRESS,
        handler=canon.ABSENT_LAYER_HANDLER,
        chunk_x=0,
        chunk_y=0,
        chunk_addresses=(),
        null_chunk_count=0,
    ).classification == "unclassified_handler"


def test_a_zero_grid_dominant_record_is_not_a_rendered_layer():
    """The accepted dominant handler with an empty grid is its own class."""
    assert _record(canon.DOMINANT_LAYER_HANDLER, 0, 0).classification == (
        "dominant_zero_grid"
    )
    assert _record(canon.DOMINANT_LAYER_HANDLER, 0, 2).classification == (
        "dominant_partial_zero_grid"
    )
    assert _record(canon.DOMINANT_LAYER_HANDLER, 2, 2).classification == "dominant"


def test_only_the_unassembled_graphical_class_blocks_a_composite():
    assert _record(0x08007B63).blocks_composite is False
    assert _record(0x0800897B).blocks_composite is False
    assert _record(0x080088BD).blocks_composite is True
    assert _record(0x08008087).blocks_composite is False


def test_both_screen_entry_handlers_are_renderable():
    assert _record(0x08007B63).renderable is True
    assert _record(0x0800897B).renderable is True
    assert _record(0x080088BD).renderable is False


# --- fail-closed behaviour for an unaccounted record form --------------------

def test_every_handler_the_engine_accounts_for_is_resolved():
    for handler in (0x08008087, 0x08007B63, 0x0800897B, 0x080088BD):
        assert _record(handler).resolved is True


def test_an_unknown_handler_is_not_called_non_graphical():
    """Unknown means unknown: it must withhold, not be treated as drawing nothing.

    Before this, an unaccounted handler reported `graphical=False` and
    `blocks_composite=False`, so a possibly graphical layer neither rendered nor
    blocked - the fail-open the project's semantics rules forbid.
    """
    unknown = _record(0x0800FFFF)
    assert unknown.classification == "unclassified_handler"
    assert unknown.resolved is False
    assert unknown.renderable is False
    assert unknown.blocks_composite is True


def test_a_dominant_record_with_a_zero_grid_is_unresolved_and_withholds():
    for chunk_x, chunk_y in ((0, 0), (0, 2), (2, 0)):
        record = _record(canon.DOMINANT_LAYER_HANDLER, chunk_x, chunk_y)
        assert record.resolved is False
        assert record.blocks_composite is True


def test_the_absent_placeholder_is_resolved_and_does_not_block():
    absent = _record(canon.ABSENT_LAYER_HANDLER, 0, 0)
    assert absent.classification == "absent_placeholder"
    assert absent.resolved is True
    assert absent.blocks_composite is False
