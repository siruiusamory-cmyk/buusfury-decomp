"""PINMAP-05: the text-edit row is the profile's, and a profile edit moves it."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from unittest import mock

import pytest

from tests.text_fixture import build, open_image
from tools.webfoot import capability, textedit
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.textedit import engine

#: Scratch offsets this module plants its map row, event table and placement at; the
#: profile's real map row lies past the fixture's end on purpose.
MAPS_AT = 0x3000
EVENT_TABLE_AT = 0x4000
PLACEMENT_AT = 0x4200
RESOURCES = (0x2000, 0x4000, 0x7000)


def _packaged():
    catalog = RomProfileCatalog.load(Path("tools/webfoot/data/roms.yaml"))
    return next(item for item in catalog.profiles
                if item.id == engine._CANONICAL_PROFILE_ID)


def _without(key: str):
    declared = _packaged()
    return replace(declared,
                   text_strings=replace(declared.text_strings, **{key: None}))


def _row():
    row = engine.PROFILES[0]
    return replace(row, event_pool=(0x2000, 0x2100), maps=replace(
        row.maps, table=MAPS_AT, event_table=EVENT_TABLE_AT))


def _image(slots=None) -> bytes:
    return build(records=[(1, 0x00, 2)], slots=slots)


def _opened(directory, row=None, image=None):
    with mock.patch.object(engine, "PROFILES", (row or _row(),)):
        return open_image(_image() if image is None else image, directory)


@pytest.fixture(scope="module")
def row() -> engine.TitleProfile:
    return engine.PROFILES[0]


@pytest.fixture(scope="module")
def declared():
    return _packaged()


def test_the_row_carries_every_value_the_profile_declares(row, declared):
    text, maps = declared.text_strings, declared.map_entries
    base = engine.ROM_BASE
    assert (row.key, row.game_code) == (declared.game, declared.game_code)
    assert row.text_table == text.pointer_table_address.raw - base
    assert row.text_slots == text.count
    assert row.table_literal == text.table_literal - base
    assert row.live_selectors == text.live_selectors
    assert row.grown_selector == text.grown_selector
    assert row.appearance_table == declared.appearances.address.raw - base
    assert row.appearance_count == declared.appearances.count
    assert row.event_pool == tuple(address - base for address in text.event_pool)
    assert row.maps.table == maps.address.raw - base
    assert row.maps.count == maps.count
    assert row.maps.stride == maps.record_size
    assert row.maps.placement_family == declared.placement_types.factory_raw
    assert row.maps.name_slot_at == text.map_name_slot_offset - base
    assert row.maps.array_at == text.map_array_offset - base
    assert row.maps.count_at == text.map_count_offset - base
    assert row.maps.descriptor_at == text.map_descriptor_offset - base
    assert row.maps.resource_handler == text.event_resource_handler
    assert row.maps.event_table == text.event_table - base
    assert row.maps.event_count == text.event_count


def test_the_packaged_contract_is_the_gate_that_authorises_the_row(declared):
    without = replace(declared, text_strings=None)
    with mock.patch.object(capability, "packaged_contract", return_value=without):
        with pytest.raises(textedit.TextEditError, match="declares no text_strings"):
            engine.profiles()


def test_an_omitted_optional_key_refuses_by_name_and_never_defaults(row):
    for key in ("event_pool", "map_descriptor_offset", "event_count"):
        with pytest.raises(textedit.TextEditError, match=f"declares no {key}"):
            engine._title_profile(_without(key))
        with pytest.raises(textedit.TextEditError, match=f"declares no {key}"):
            engine._text_address(None, key, row.key)


def test_a_moved_slot_count_moves_the_slots_the_image_yields(tmp_path):
    """`_read_slots` walks `profile.text_slots` entries, so the model carries that many."""
    model = _opened(tmp_path, replace(_row(), text_slots=64))
    assert model.profile.text_slots == 64
    assert len(model.slots) == 64
    assert len(_opened(tmp_path).slots) == 1534


def test_a_moved_event_count_moves_how_much_of_the_table_is_read(tmp_path):
    """`_event_extents` closes each resource at the next pointer it reads."""
    image = _event_image()
    whole = engine._event_extents(_opened(tmp_path, image=image))
    assert whole == {RESOURCES[0]: (RESOURCES[0], RESOURCES[1]),
                     RESOURCES[1]: (RESOURCES[1], RESOURCES[2]),
                     RESOURCES[2]: (RESOURCES[2], EVENT_TABLE_AT)}
    short = replace(_row(), maps=replace(_row().maps, event_count=1))
    assert engine._event_extents(_opened(tmp_path, short, image)) == {
        RESOURCES[0]: (RESOURCES[0], EVENT_TABLE_AT)}


def test_a_moved_event_table_address_moves_where_the_words_are_read(tmp_path):
    image = _event_image()
    assert engine._event_extents(_opened(tmp_path, image=image)) != {}
    elsewhere = replace(_row(), maps=replace(_row().maps, event_table=EVENT_TABLE_AT + 0x80))
    assert engine._event_extents(_opened(tmp_path, elsewhere, image)) == {}


def test_the_resource_handler_is_the_declared_word_and_not_an_offset(row, declared):
    """`record_maps` compares a descriptor's own word, so the handler keeps ROM space."""
    assert row.maps.resource_handler == declared.text_strings.event_resource_handler
    assert row.maps.resource_handler > engine.ROM_BASE


def test_the_placement_family_is_the_declared_word_and_not_an_offset(row, declared):
    """The placement's first word is compared as the image spells it."""
    assert row.maps.placement_family == declared.placement_types.factory_raw
    assert row.maps.placement_family > engine.ROM_BASE


def test_moving_the_map_name_slot_offset_moves_which_slot_names_a_map(tmp_path):
    """`maps()` reads the row's name slot at `maps.name_slot_at`."""
    assert [item.label for item in _named(tmp_path)] == ["first", "second"]
    shifted = replace(_row(), maps=replace(_row().maps, name_slot_at=0x10))
    assert [item.label for item in _named(tmp_path, shifted)] == ["second", "third"]

def _event_image(slots=None) -> bytes:
    image = bytearray(_image(slots))
    for index, offset in enumerate(RESOURCES):
        start = EVENT_TABLE_AT + index * 4
        image[start:start + 4] = (engine.ROM_BASE + offset).to_bytes(4, "little")
    return bytes(image)


def _put32(image: bytearray, at: int, value: int) -> None:
    for offset, byte in enumerate(value.to_bytes(4, "little")):
        image[at + offset] = byte


def _map_row(image: bytearray, name_slot: int, array: int, count: int,
             at: int = MAPS_AT) -> None:
    _put32(image, at + 0x04, count)
    _put32(image, at + 0x0C, name_slot)
    _put32(image, at + 0x14, engine.ROM_BASE + array)


def _named(directory, row=None):
    """Two map rows, each carrying two name-slot words, so the profile's own
    `name_slot_at` decides which of the pair a row reads."""
    row = row or _row()
    image = bytearray(_event_image(
        slots={0: "first", 2: "second", 4: "second", 6: "third"}))
    _map_row(image, 0, PLACEMENT_AT, 0)
    _map_row(image, 2, PLACEMENT_AT, 0, at=MAPS_AT + 0x38)
    _put32(image, MAPS_AT + 0x10, 4)
    _put32(image, MAPS_AT + 0x38 + 0x10, 6)
    return textedit.maps(_opened(directory, replace(
        row, maps=replace(row.maps, count=2)), bytes(image)))