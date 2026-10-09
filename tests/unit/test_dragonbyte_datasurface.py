"""DRAGONBYTE-Z-DATA-SURFACES-001: the Data destination's model.

The three verified tables are read from the canonical image and the edits are
staged through the SDK's own setters, so what this file proves is that the model
passes the SDK's answers through rather than inventing any of its own: the
declared extents, the stable identities, the supported ranges, and the
owner-bearing change one edit produces.

The project fixture is a real extraction, not a hand-written one, because the
whole point of the model is that it agrees with records the SDK itself produced.
The suite skips without the canonical image.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tools.dragonbyte import datasurface as ds
from tools.webfoot import maps as maps_mod
from tools.webfoot import stats as stats_mod
from tools.webfoot.build import extract_project
from tools.webfoot.catalog import load_catalog
from tools.webfoot.formats import stat_tables as st
from tools.webfoot.formats.map_entry import MAP_ENTRY_SIZE
from tools.webfoot.project import read_project
from tools.webfoot.rom import identify_rom

from tests.unit.test_dragonbyte_state import CANONICAL_SHA256, SIBLING_CHECKOUT

ENEMY_HP_OFFSET = 0x04
ENEMY_HP_WIDTH = 3


@pytest.fixture(scope="module")
def catalog():
    return load_catalog(None)


@pytest.fixture(scope="module")
def canonical_rom(catalog):
    roms = SIBLING_CHECKOUT / "roms"
    for candidate in sorted(roms.glob("*.gba")) if roms.is_dir() else []:
        try:
            identification = identify_rom(candidate, catalog)
        except Exception:  # noqa: BLE001 - any unreadable file is simply not it
            continue
        if identification.hashes.sha256 == CANONICAL_SHA256:
            return candidate
    pytest.skip(f"no canonical image in {roms}")


@pytest.fixture(scope="module")
def identification(catalog, canonical_rom):
    return identify_rom(canonical_rom, catalog)


@pytest.fixture(scope="module")
def profile(identification):
    return identification.profile_match.profile


@pytest.fixture(scope="module")
def surface(catalog, canonical_rom, identification, profile):
    return ds.load_data_surface(
        canonical_rom, catalog, identification, profile, canonical_rom.read_bytes()
    )


@pytest.fixture(scope="module")
def project(tmp_path_factory, catalog, canonical_rom):
    directory = tmp_path_factory.mktemp("dbz-data-project") / "project"
    extract_project(canonical_rom, directory, catalog, graphics=False)
    return read_project(directory)


def _first_enemy(project, surface):
    row = surface.rows(ds.ENEMY, project)[0]
    return row, project.enemies[row.key]


def _with_field(project, kind, key, name, value):
    """The project with one authored field changed, and nothing else touched."""
    if kind == ds.ENEMY:
        authored = {**project.enemies, key: {**project.enemies[key], name: value}}
        return replace(project, enemies=authored)
    if kind == ds.CHARACTER:
        authored = {**project.characters, key: {**project.characters[key], name: value}}
        return replace(project, characters=authored)
    authored = {**project.maps, key.index: {**project.maps[key.index], name: value}}
    return replace(project, maps=authored)


# --- 1. the declared extents --------------------------------------------------


def test_the_three_tables_enumerate_at_their_declared_extents(surface, profile):
    enemy = profile.enemy_stats
    character = profile.character_base_stats
    table = profile.map_entries
    image_size = profile.size

    enemies = surface.rows(ds.ENEMY, None)
    characters = surface.rows(ds.CHARACTER, None)
    maps = surface.rows(ds.MAP_HEADER, None)

    assert len(enemies) == enemy.count == 141
    assert len(characters) == character.count == 9
    assert len(maps) == table.count == 452

    assert {row.size for row in enemies} == {enemy.record_size} == {0x1C}
    assert {row.size for row in characters} == {character.record_size} == {0x12}
    assert {row.size for row in maps} == {table.record_size} == {MAP_ENTRY_SIZE} == {0x38}

    assert enemies[0].file_offset == enemy.address.to_file_offset(image_size)
    assert characters[0].file_offset == character.address.to_file_offset(image_size)
    assert maps[0].file_offset == table.address.to_file_offset(image_size)
    assert maps[-1].file_offset == (
        table.address.to_file_offset(image_size) + (table.count - 1) * table.record_size
    )


def test_every_row_carries_its_stable_identity_and_its_supported_fields(surface):
    enemies = surface.rows(ds.ENEMY, None)
    characters = surface.rows(ds.CHARACTER, None)
    maps = surface.rows(ds.MAP_HEADER, None)

    assert all(row.identity.startswith("enemy:") for row in enemies)
    assert all(row.identity.startswith("character:") for row in characters)
    assert all(row.identity.startswith("map:") for row in maps)
    assert len({row.identity for row in enemies}) == len(enemies)
    assert len({row.identity for row in characters}) == len(characters)
    assert len({row.identity for row in maps}) == len(maps)

    assert tuple(field.name for field in enemies[0].fields) == tuple(
        stats_mod.ENEMY_FIELDS
    )
    assert tuple(field.name for field in characters[0].fields) == tuple(
        stats_mod.CHARACTER_FIELDS
    )
    assert tuple(field.name for field in maps[0].fields) == tuple(maps_mod.MAP_FIELDS)
    assert all(field.maximum is None or field.maximum >= field.minimum for row in enemies for field in row.fields)

    character = characters[0]
    entry = surface.tables.character(character.key)
    assert entry.alias in character.label


# --- 2. the view is the project's, not the image's ----------------------------


def test_the_untouched_extraction_edits_nothing(surface, project):
    assert surface.changes(project) == ()
    assert surface.pending_bytes(project) == {}


def test_a_record_the_project_authors_shows_the_authored_value_and_is_editable(
    surface, project
):
    row = surface.rows(ds.ENEMY, project)[0]
    authored = project.enemies[row.key]

    assert row.editable
    assert row.note == ""
    assert row.field("hp").value == authored["hp"]


def test_a_record_the_project_does_not_author_is_read_only_with_its_reason(surface):
    row = surface.rows(ds.MAP_HEADER, None)[0]

    assert not row.editable
    assert "authors no map record" in row.note


def test_a_missing_map_table_is_a_stated_absence_rather_than_an_error(surface, project):
    without = replace(surface, maps=None, maps_problem="no map-entry table here")

    assert without.rows(ds.MAP_HEADER, project) == ()
    assert without.changes(project) == ()


# --- 3. one edit, one change, owned by the record identity --------------------


def test_one_enemy_edit_produces_one_change_owned_by_the_record_identity(
    surface, project
):
    row, authored = _first_enemy(project, surface)
    edited = _with_field(project, ds.ENEMY, row.key, "hp", authored["hp"] + 1)

    changes = surface.changes(edited)

    assert len(changes) == 1
    change = changes[0]
    assert change.owner == row.identity
    assert change.offset == row.file_offset
    assert change.old == surface.tables.enemy(row.key).original_bytes
    assert change.new != change.old
    differ = {at for at, (old, new) in enumerate(zip(change.old, change.new)) if old != new}
    assert differ
    assert differ <= set(range(ENEMY_HP_OFFSET, ENEMY_HP_OFFSET + ENEMY_HP_WIDTH))


def test_one_character_edit_produces_one_change_owned_by_the_record_identity(
    surface, project
):
    row = surface.rows(ds.CHARACTER, project)[0]
    authored = project.characters[row.key]
    edited = _with_field(project, ds.CHARACTER, row.key, "speed", authored["speed"] + 1)

    changes = surface.changes(edited)

    assert [change.owner for change in changes] == [row.identity]
    assert changes[0].offset == row.file_offset
    assert changes[0].old != changes[0].new
    assert len(changes[0].old) == st.BASE_STAT_RECORD_SIZE


def test_one_map_header_edit_produces_one_change_owned_by_the_record_identity(
    surface, project
):
    row = surface.rows(ds.MAP_HEADER, project)[0]
    authored = project.maps[row.key.index]
    value = (authored["zone"] + 1) % 0x100
    edited = _with_field(project, ds.MAP_HEADER, row.key, "zone", value)

    changes = surface.changes(edited)

    assert len(changes) == 1
    assert changes[0].owner == row.identity == f"map:{row.key.index:04d}"
    assert changes[0].offset == row.file_offset
    assert changes[0].old != changes[0].new
    assert len(changes[0].old) == MAP_ENTRY_SIZE


def test_the_change_is_visible_as_bytes_for_the_rom_surface(surface, project):
    row, authored = _first_enemy(project, surface)
    edited = _with_field(project, ds.ENEMY, row.key, "hp", authored["hp"] + 7)

    pending = surface.pending_bytes(edited)

    assert list(pending) == [row.file_offset]
    assert pending[row.file_offset] == surface.changes(edited)[0].new
    assert surface.tables.enemy(row.key).original_bytes != pending[row.file_offset]


def test_two_edited_records_are_two_changes_in_table_order(surface, project):
    rows = surface.rows(ds.ENEMY, project)[:2]
    edited = _with_field(project, ds.ENEMY, rows[0].key, "hp", project.enemies[rows[0].key]["hp"] + 1)
    edited = _with_field(edited, ds.ENEMY, rows[1].key, "exp", project.enemies[rows[1].key]["exp"] + 1)

    changes = surface.changes(edited)

    assert {change.owner for change in changes} == {rows[0].identity, rows[1].identity}
    assert len(changes) == 2


# --- 4. a value the SDK would refuse is skipped and stated --------------------


def test_an_authored_value_outside_the_supported_range_is_skipped_and_stated(
    surface, project
):
    row = surface.rows(ds.ENEMY, project)[0]
    edited = _with_field(project, ds.ENEMY, row.key, "level", 255)

    assert surface.changes(edited) == ()
    stated = surface.rows(ds.ENEMY, edited)[0]
    assert not stated.editable
    assert "level" in stated.note
    assert stated.field("level").value == 255


def test_a_change_the_sdk_refuses_never_reaches_the_change_list(surface, project):
    """A record the image does not contain is skipped, not crashed on."""
    row = surface.rows(ds.ENEMY, project)[0]
    stranger = st.StatIdentity(kind="enemy", key=999_999)
    edited = replace(
        project,
        enemies={**project.enemies, stranger: {**project.enemies[row.key], "hp": 1_000}},
    )

    assert surface.changes(edited) == ()


def test_every_kind_is_named_and_unknown_kinds_are_refused(surface):
    assert set(ds.KINDS) == {ds.ENEMY, ds.CHARACTER, ds.MAP_HEADER}
    assert set(ds.KIND_LABELS) == set(ds.KINDS)
    with pytest.raises(ds.DataSurfaceError):
        surface.rows("no_such_kind", None)
