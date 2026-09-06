"""Portable tests for the map semantic layer's pure parts. No ROM bytes."""

from __future__ import annotations

from dataclasses import replace

import pytest

from tools.webfoot.binary import GBA_ROM_BASE
from tools.webfoot.formats.map_entry import MAP_ENTRY_LAYOUT, MapEntry
from tools.webfoot.formats.map_slots import SLOT_SIZE
from tools.webfoot.maps import (
    MAP_FIELDS,
    MapError,
    MapIdentity,
    _resolve_slot_extent,
    _with_fields,
)
from tools.webfoot.project.model import _MAP_FIELD_ORDER


ZERO_ENTRY = MapEntry(*([0] * len(MAP_ENTRY_LAYOUT)))
IMAGE_SIZE = 0x10000
#: A table far from the arrays under test, so only the collision case collides.
TABLE = (0xF000, 0xF800)


def test_identity_key_sorts_numerically():
    assert MapIdentity(39).key == "map:0039"
    keys = sorted(MapIdentity(i).key for i in (9, 10, 100))
    assert keys == ["map:0009", "map:0010", "map:0100"]


def test_identity_rejects_a_negative_index():
    with pytest.raises(MapError):
        MapIdentity(-1)


def test_identity_orders_by_index():
    assert MapIdentity(9) < MapIdentity(10)


def test_project_field_order_matches_the_codec():
    """The authored order duplicates `MAP_FIELDS`; this is what stops it drifting."""
    assert set(_MAP_FIELD_ORDER) == set(MAP_FIELDS)


def test_editable_fields_exclude_pointers_and_counts():
    """Ticket TOOLKIT-007 forbids editing an extent's own count or a pointer."""
    for name in MAP_FIELDS:
        assert not name.endswith("_pointer")
        assert not name.endswith("_count")
    assert "unknown_0a" not in MAP_FIELDS
    assert "unknown_0c" not in MAP_FIELDS


def test_with_fields_changes_only_the_named_field():
    edited = _with_fields(ZERO_ENTRY, {"music_id": 7})
    assert edited.music_id_raw == 7
    assert edited.zone_raw == 0
    assert edited.to_bytes() != ZERO_ENTRY.to_bytes()
    # Frozen source is untouched.
    assert ZERO_ENTRY.music_id_raw == 0


# --- extent resolution ---------------------------------------------------


def entry_with(count: int, pointer: int) -> MapEntry:
    return replace(
        ZERO_ENTRY, trigger_count_raw=count, triggers_pointer_raw=pointer
    )


def test_extent_resolves_a_well_formed_array():
    entry = entry_with(3, GBA_ROM_BASE + 0x100)
    assert _resolve_slot_extent(entry, IMAGE_SIZE, TABLE) == (0x100, 3 * SLOT_SIZE)


@pytest.mark.parametrize(
    "count, pointer, reason",
    [
        (0, 0, "no count and no pointer"),
        (0, GBA_ROM_BASE + 0x100, "a pointer with no declared extent"),
        (4, 0, "a count with no array - 163 real entries are in this state"),
        (4, 0x02000000, "EWRAM is outside the cartridge window"),
        (4, GBA_ROM_BASE + IMAGE_SIZE - 8, "an extent running past the image"),
    ],
)
def test_unreadable_states_resolve_to_nothing(count, pointer, reason):
    assert _resolve_slot_extent(entry_with(count, pointer), IMAGE_SIZE, TABLE) is None, reason


def test_an_extent_colliding_with_the_map_table_is_refused():
    """MapEntry 451's real defect, reproduced synthetically.

    Its declared extent covers the start of the very table that indexes it, so
    the count cannot be describing slots. Reading it would emit an extent that
    provably is not one.
    """
    table_start, table_end = TABLE
    entry = entry_with(4, GBA_ROM_BASE + table_start - SLOT_SIZE * 2)
    assert _resolve_slot_extent(entry, IMAGE_SIZE, TABLE) is None


def test_an_extent_ending_exactly_at_the_table_is_allowed():
    """The collision check is half-open, so an abutting array still reads."""
    table_start, _ = TABLE
    entry = entry_with(2, GBA_ROM_BASE + table_start - SLOT_SIZE * 2)
    resolved = _resolve_slot_extent(entry, IMAGE_SIZE, TABLE)
    assert resolved == (table_start - SLOT_SIZE * 2, SLOT_SIZE * 2)
