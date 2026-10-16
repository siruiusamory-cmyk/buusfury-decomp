"""DRAGONBYTE-Z-DATA-SURFACES-001: the data documents in the one journal.

Three things are proved here, and they are the whole contract between the Data
destination and the journal:

* the adapter is lossless, so a Save writes what the project already held plus
  the edit and nothing else;
* one data edit is one journal entry, and one undo restores the documents
  exactly;
* the payload may not carry another project's identity, because `install`
  replaces the project's meta.

The project fixture is a real extraction; the suite skips without the canonical
image.
"""

from __future__ import annotations

import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from tools.dragonbyte import dataedits
from tools.dragonbyte.journal import DOCUMENT_ADAPTERS, EditKind
from tools.dragonbyte.session import Session
from tools.webfoot.binary import FileOffset
from tools.webfoot.build import extract_project
from tools.webfoot.catalog import load_catalog
from tools.webfoot.layout import RomRange
from tools.webfoot.project import read_project
from tools.webfoot.rom import identify_rom

from tests.unit.test_dragonbyte_state import CANONICAL_SHA256, SIBLING_CHECKOUT

#: Any span inside the enemy table: this file tests the journal, not the offset.
ENEMY_SPAN = RomRange(FileOffset(0x711274), 28)


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
def extracted(tmp_path_factory, catalog, canonical_rom):
    directory = tmp_path_factory.mktemp("dbz-dataedits") / "source"
    extract_project(canonical_rom, directory, catalog, graphics=False)
    return directory


@pytest.fixture
def project_dir(tmp_path, extracted):
    target = tmp_path / "project"
    shutil.copytree(extracted, target)
    return target


def _edit_hp(session: Session) -> tuple[object, int]:
    """One enemy's hp, changed by one, committed as one journal edit."""
    payload = dataedits.read(session.project)
    identity = sorted(payload.enemies, key=lambda item: item.key)[0]
    value = payload.enemies[identity]["hp"] + 1
    after = replace(
        payload,
        enemies={**payload.enemies, identity: {**payload.enemies[identity], "hp": value}},
    )
    session.apply_edit(
        kind=EditKind.SEMANTIC,
        target=dataedits.DATA_TARGET,
        after=after,
        claimed=(ENEMY_SPAN,),
        reason=f"enemy edit: hp",
    )
    return identity, value


def test_the_journal_registers_the_data_target_as_a_reversible_document():
    assert dataedits.DATA_TARGET in DOCUMENT_ADAPTERS


def test_the_adapter_round_trips_the_projects_own_documents(project_dir, tmp_path):
    project = read_project(project_dir)
    payload = dataedits.read(project)
    assert payload.record_count == len(project.enemies) + len(project.characters) + len(
        project.maps
    )

    written = tmp_path / "written"
    dataedits.write(written, payload)
    again = read_project(written)

    assert again.meta == project.meta
    assert again.enemies == project.enemies
    assert again.characters == project.characters
    assert again.maps == project.maps
    for name in ("enemies/enemies.toml", "characters/characters.toml", "maps/maps.toml"):
        assert (written / name).is_file(), name


def test_an_untouched_project_round_trips_through_the_writer_byte_for_byte(
    project_dir, tmp_path
):
    """The documents are the SDK's own output, so re-emitting them changes nothing."""
    source = project_dir / "maps" / "maps.toml"
    payload = dataedits.read(read_project(project_dir))
    written = tmp_path / "written"
    dataedits.write(written, payload)

    assert source.read_bytes() == (written / "maps" / "maps.toml").read_bytes()
    assert (project_dir / "enemies" / "enemies.toml").read_bytes() == (
        written / "enemies" / "enemies.toml"
    ).read_bytes()


def test_one_data_edit_is_one_journal_entry_and_one_undo_restores_it(project_dir):
    session = Session()
    session.open_project(project_dir)
    before = {key: dict(values) for key, values in session.project.enemies.items()}

    identity, value = _edit_hp(session)

    assert session.project.enemies[identity]["hp"] == value
    assert session.journal.depth == 1
    assert session.journal.is_dirty
    entry = session.journal.edits()[0]
    assert entry.target == dataedits.DATA_TARGET
    assert entry.kind is EditKind.SEMANTIC
    assert entry.claimed == (ENEMY_SPAN,)

    session.undo_edit()

    assert {key: dict(values) for key, values in session.project.enemies.items()} == before
    assert session.journal.depth == 0

    session.redo_edit()

    assert session.project.enemies[identity]["hp"] == value


def test_a_saved_data_edit_lands_in_the_projects_own_documents(project_dir):
    session = Session()
    session.open_project(project_dir)
    identity, value = _edit_hp(session)

    session.save_project()

    assert session.journal.is_dirty is False
    reloaded = read_project(project_dir)
    assert reloaded.enemies[identity]["hp"] == value
    assert reloaded.characters == session.project.characters
    assert reloaded.maps == session.project.maps


def test_a_payload_carrying_another_projects_identity_is_refused(project_dir):
    project = read_project(project_dir)
    payload = dataedits.read(project)
    stranger = replace(payload, meta=replace(project.meta, name="another-project"))

    with pytest.raises(dataedits.DataEditError):
        dataedits.validate(project, stranger)


def test_a_payload_that_is_not_authored_data_is_refused(project_dir):
    project = read_project(project_dir)

    with pytest.raises(dataedits.DataEditError):
        dataedits.validate(project, {"enemies": {}})
    with pytest.raises(dataedits.DataEditError):
        dataedits.install(project, None)
    with pytest.raises(dataedits.DataEditError):
        dataedits.write(Path("."), None)


def test_an_edit_of_an_unregistered_target_still_writes_nothing(project_dir):
    """The data target is additive: every other target's refusal is unchanged."""
    session = Session()
    session.open_project(project_dir)
    before = (project_dir / "enemies" / "enemies.toml").read_bytes()

    with pytest.raises(Exception):
        session.apply_edit(
            kind=EditKind.SEMANTIC,
            target="not-a-registered-target",
            after={},
        )

    assert (project_dir / "enemies" / "enemies.toml").read_bytes() == before
    assert session.journal.depth == 0
