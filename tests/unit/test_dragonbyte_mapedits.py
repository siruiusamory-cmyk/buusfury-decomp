"""DRAGONBYTE-Z-MAPS-DESTINATION-001: the map documents in the one journal.

Three things are proved here, and they are the whole contract between the Maps
destination and the journal:

* the adapter is lossless, so a Save writes what the project already held plus
  the edit, and every document this destination does not own is left alone;
* one map edit is one journal entry, and one undo restores both documents
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

from tools.dragonbyte import mapedits
from tools.dragonbyte import mapsurface as ms
from tools.dragonbyte.journal import DOCUMENT_ADAPTERS, EditKind
from tools.dragonbyte.session import Session
from tools.webfoot.build import extract_project
from tools.webfoot.catalog import load_catalog
from tools.webfoot.project import read_project
from tools.webfoot.rom import identify_rom

from tests.unit.test_dragonbyte_state import CANONICAL_SHA256, SIBLING_CHECKOUT

#: The documents this destination owns. Every other document under `maps/` is
#: another writer's, and a save must leave it byte-identical.
OWNED = ("layout.toml", "transitions.toml")


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
def extracted_project(tmp_path_factory, catalog, canonical_rom):
    directory = tmp_path_factory.mktemp("dbz-mapedits") / "source"
    extract_project(canonical_rom, directory, catalog, graphics=False)
    return directory


@pytest.fixture
def project_dir(tmp_path, extracted_project):
    target = tmp_path / "project"
    shutil.copytree(extracted_project, target)
    return target


@pytest.fixture(scope="module")
def surface(catalog, canonical_rom):
    identification = identify_rom(canonical_rom, catalog)
    return ms.load_map_surface(
        canonical_rom,
        catalog,
        identification,
        identification.profile_match.profile,
        canonical_rom.read_bytes(),
    )


def _edit_cell(session, surface) -> object:
    """One layout cell, changed to another chunk of its own layer."""
    for index in (0, 1):
        for layer in surface.layers(index):
            if not layer.editable or layer.chunk_count < 2:
                continue
            row = surface.cells(index, layer.slot, session.project)[0]
            after = ms.with_layout_cell(
                mapedits.read(session.project), row, layer.chunk_count
            )
            session.apply_edit(
                kind=EditKind.SEMANTIC,
                target=mapedits.MAPS_TARGET,
                after=after,
                claimed=(ms.layout_span(row),),
                reason=f"{row.identity} edit: chunk",
            )
            return row
    pytest.skip("no paintable cell in this image")


def _edit_warp(session, surface) -> object:
    """One warp, sent to a neighbouring map."""
    row = surface.warps()[0]
    after = ms.with_warp_destination(
        mapedits.read(session.project), surface.transitions, row, row.destination + 1
    )
    session.apply_edit(
        kind=EditKind.SEMANTIC,
        target=mapedits.MAPS_TARGET,
        after=after,
        reason=f"{row.identity} edit: destination",
    )
    return row


def _other_map_documents(directory: Path) -> dict[str, bytes]:
    maps = directory / "maps"
    return {
        path.name: path.read_bytes()
        for path in sorted(maps.glob("*.toml"))
        if path.name not in OWNED
    }


def test_the_journal_registers_the_maps_target_as_a_reversible_document():
    assert mapedits.MAPS_TARGET in DOCUMENT_ADAPTERS


def _authored(project, surface):
    """The project's map documents with one cell and one warp authored."""
    for index in (0, 1):
        for layer in surface.layers(index):
            if not layer.editable or layer.chunk_count < 2:
                continue
            row = surface.cells(index, layer.slot, project)[0]
            payload = ms.with_layout_cell(
                mapedits.read(project), row, layer.chunk_count
            )
            warp = surface.warps()[0]
            return ms.with_warp_destination(
                payload, surface.transitions, warp, warp.destination + 1
            ), row, warp
    pytest.skip("no paintable cell in this image")


def test_the_adapter_round_trips_the_projects_own_documents(
    project_dir, tmp_path, surface
):
    project = read_project(project_dir)
    payload, row, warp = _authored(project, surface)

    written = tmp_path / "written"
    shutil.copytree(project_dir, written)
    mapedits.write(written, payload)
    again = read_project(written)

    assert again.meta == project.meta
    assert again.layout.cells() == payload.layout.cells()
    assert again.transitions.edits() == payload.transitions.edits()
    assert again.chunks == project.chunks
    assert (written / "maps" / "layout.toml").is_file()
    assert (written / "maps" / "transitions.toml").is_file()


def test_an_emptied_document_is_removed_rather_than_written_empty(
    project_dir, surface
):
    """The SDK's own writer removes the optional document, so a reader accepts it."""
    project = read_project(project_dir)
    authored, _row, _warp = _authored(project, surface)
    mapedits.write(project_dir, authored)

    assert (project_dir / "maps" / "layout.toml").is_file()
    before = _other_map_documents(project_dir)

    mapedits.write(project_dir, mapedits.read(project))

    assert not (project_dir / "maps" / "layout.toml").exists()
    assert not (project_dir / "maps" / "transitions.toml").exists()
    assert _other_map_documents(project_dir) == before
    assert read_project(project_dir).meta == project.meta


def test_one_cell_edit_is_one_journal_entry_and_one_undo_restores_it(
    project_dir, surface
):
    session = Session()
    session.open_project(project_dir)
    before = dict(session.project.layout.cells())

    row = _edit_cell(session, surface)

    assert session.project.layout.cells()
    assert session.journal.depth == 1
    assert session.journal.is_dirty
    entry = session.journal.edits()[0]
    assert entry.target == mapedits.MAPS_TARGET
    assert entry.kind is EditKind.SEMANTIC
    assert entry.claimed == (ms.layout_span(row),)

    session.undo_edit()

    assert dict(session.project.layout.cells()) == before
    assert session.journal.depth == 0

    session.redo_edit()

    assert session.project.layout.cells()


def test_a_saved_cell_edit_lands_in_the_projects_own_document(project_dir, surface):
    session = Session()
    session.open_project(project_dir)
    row = _edit_cell(session, surface)

    session.save_project()

    assert session.journal.is_dirty is False
    reloaded = read_project(project_dir)
    assert reloaded.layout.cells()[(row.map_index, row.slot, row.cell)] == row.maximum
    assert (project_dir / "maps" / "layout.toml").is_file()


def test_a_saved_warp_edit_lands_in_the_projects_own_document(project_dir, surface):
    session = Session()
    session.open_project(project_dir)
    row = _edit_warp(session, surface)

    session.save_project()

    reloaded = read_project(project_dir)
    authored = reloaded.transitions.edits()[(row.source, row.index)]
    assert authored.destination == f"map:{row.destination + 1:04d}"
    assert (project_dir / "maps" / "transitions.toml").is_file()


def test_a_save_leaves_every_document_this_destination_does_not_own_alone(
    project_dir, surface
):
    session = Session()
    session.open_project(project_dir)
    before = _other_map_documents(project_dir)

    _edit_cell(session, surface)
    _edit_warp(session, surface)
    session.save_project()

    assert _other_map_documents(project_dir) == before


def test_a_payload_carrying_another_projects_identity_is_refused(project_dir):
    project = read_project(project_dir)
    payload = mapedits.read(project)
    stranger = replace(payload, meta=replace(project.meta, name="another-project"))

    with pytest.raises(mapedits.MapsEditError):
        mapedits.validate(project, stranger)


def test_a_payload_that_is_not_authored_map_documents_is_refused(project_dir):
    project = read_project(project_dir)

    with pytest.raises(mapedits.MapsEditError):
        mapedits.validate(project, {"layout": {}})
    with pytest.raises(mapedits.MapsEditError):
        mapedits.install(project, None)
    with pytest.raises(mapedits.MapsEditError):
        mapedits.write(Path("."), None)
