"""DRAGONBYTE-Z-MAPS-DESTINATION-001: the Maps destination's model.

The layout cells, their chunk vocabulary and the warps are read from the
canonical image and staged through the SDK's own authorities, so what this file
proves is that the model passes those answers through rather than inventing any
of its own: the declared map table, the SDK's own read-only reasons, the
owner-bearing change one edit produces, and the two document rules that make a
project file prove its base.

The project fixture is a real extraction, not a hand-written one, because the
whole point of the model is that it agrees with documents the SDK itself
produced. The suite skips without the canonical image.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tools.dragonbyte import mapsurface as ms
from tools.webfoot.build import extract_project
from tools.webfoot.catalog import load_catalog
from tools.webfoot.map_paint import MapPaintError
from tools.webfoot.map_transitions import TransitionFieldError
from tools.webfoot.maps import MapIdentity
from tools.webfoot.project import read_project
from tools.webfoot.rom import identify_rom

from tests.unit.test_dragonbyte_state import CANONICAL_SHA256, SIBLING_CHECKOUT

#: A map whose dominant grid is a single chunk: a real read-only layer this
#: image holds, used to prove the reason is stated rather than invented.
ONE_CHUNK_MAP = 1

#: A map the image carries a transition out of, measured from the corpus.
DOORED_MAP = 33


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
    return ms.load_map_surface(
        canonical_rom, catalog, identification, profile, canonical_rom.read_bytes()
    )


@pytest.fixture(scope="module")
def project(tmp_path_factory, catalog, canonical_rom):
    directory = tmp_path_factory.mktemp("dbz-maps-project") / "project"
    extract_project(canonical_rom, directory, catalog, graphics=False)
    return read_project(directory)


def _first_paintable(surface, project):
    """A cell of the first map whose dominant layer has more than one chunk."""
    for row in surface.map_rows():
        if row.index not in (0, ONE_CHUNK_MAP):
            continue
        for layer in surface.layers(row.index):
            if layer.editable and layer.chunk_count > 1:
                cells = surface.cells(row.index, layer.slot, project)
                return layer, cells
    pytest.skip("no paintable map in this image")


# --- 1. the declared table ----------------------------------------------------


def test_the_map_table_enumerates_at_its_declared_extent(surface, profile):
    rows = surface.map_rows()
    table = profile.map_entries

    assert len(rows) == table.count == 452
    assert {row.size for row in rows} == {table.record_size} == {0x38}
    assert rows[0].file_offset == table.address.to_file_offset(profile.size)
    assert rows[-1].file_offset == (
        table.address.to_file_offset(profile.size)
        + (table.count - 1) * table.record_size
    )


def test_every_row_carries_its_stable_identity(surface):
    rows = surface.map_rows()

    assert all(row.identity.startswith("map:") for row in rows)
    assert len({row.identity for row in rows}) == len(rows)
    assert rows[0].identity == "map:0000"


def test_a_map_row_counts_the_transitions_the_warps_view_lists(surface):
    row = next(item for item in surface.map_rows() if item.index == DOORED_MAP)

    assert row.warps == len(surface.warps(map_index=DOORED_MAP)) == 1


# --- 2. unsupported rows state the SDK's own reason ---------------------------


def test_a_map_with_no_paintable_layer_says_why_on_every_row(surface):
    layers = surface.layers(ONE_CHUNK_MAP)

    assert layers
    assert not any(layer.editable for layer in layers)
    assert all(layer.note for layer in layers)
    assert any("single chunk" in layer.note for layer in layers)


def test_a_paintable_layer_carries_the_vocabulary_a_cell_may_take(surface):
    layer, cells = _first_paintable(surface, None)

    assert layer.editable and layer.note == ""
    assert layer.chunk_count == len(layer.chunks) > 1
    assert {chunk.ordinal for chunk in layer.chunks} == set(
        range(1, layer.chunk_count + 1)
    )
    assert len(cells) == layer.cell_count


def test_a_map_the_image_cannot_resolve_is_a_stated_reason_not_an_error(
    surface, monkeypatch
):
    monkeypatch.setattr(
        type(surface), "target", lambda self, index: _raise_paint_error(), raising=True
    )

    layers = ms.MapSurface.layers(surface, ONE_CHUNK_MAP + 1)

    assert len(layers) == 1
    assert not layers[0].editable
    assert "could not be read" in layers[0].note


def _raise_paint_error():
    raise MapPaintError("map:0001 could not be read: the layer record is not readable")


def test_layer_and_cell_identities_are_the_sdk_own_spellings(surface):
    layer, cells = _first_paintable(surface, None)

    assert layer.identity == f"map:{layer.map_index:04d} layer {layer.slot}"
    assert all(
        cell.identity == f"{layer.identity} cell {cell.cell}" for cell in cells
    )
    assert all(cell.ordinal == layer.chunks[cell.ordinal - 1].ordinal for cell in cells if cell.ordinal)


def test_a_cell_shows_the_value_the_open_project_would_build(surface, project):
    layer, cells = _first_paintable(surface, project)

    assert surface.changes(project) == ()
    assert surface.pending_bytes(project) == {}

    edited = ms.with_layout_cell(project, cells[0], layer.chunk_count)
    reread = surface.cells(layer.map_index, layer.slot, edited)[0]

    assert reread.ordinal == layer.chunk_count
    assert reread.note
    assert surface.cells(layer.map_index, layer.slot, project)[0].ordinal != (
        layer.chunk_count
    )


# --- 3. one edit, one change, owned by the row identity -----------------------


def test_one_cell_edit_produces_one_change_owned_by_the_row_identity(
    surface, project
):
    layer, cells = _first_paintable(surface, project)
    row = cells[0]
    edited = ms.with_layout_cell(project, row, layer.chunk_count)

    changes = surface.changes(edited)

    assert len(changes) == 1
    assert changes[0].owner == row.identity
    assert changes[0].offset == row.offset
    assert len(changes[0].old) == len(changes[0].new) == 4
    assert changes[0].old != changes[0].new
    assert ms.layout_span(row).start.value == row.offset
    assert ms.layout_span(row).size == 4


def test_the_cell_change_is_visible_as_bytes_for_the_rom_surface(surface, project):
    layer, cells = _first_paintable(surface, project)
    row = cells[0]
    edited = ms.with_layout_cell(project, row, layer.chunk_count)

    pending = surface.pending_bytes(edited)

    assert list(pending) == [row.offset]
    assert pending[row.offset] == surface.changes(edited)[0].new
    assert surface.image[row.offset : row.offset + 4] != pending[row.offset]


def test_the_chunk_zero_is_offered_only_where_it_is_a_real_revert(surface, project):
    """0 removes an authored chunk, so it is no choice on a cell with none."""
    layer, cells = _first_paintable(surface, project)
    row = cells[0]

    assert not row.revertable
    assert row.field.minimum == 1
    assert row.field.maximum == layer.chunk_count
    assert row.field.range_text == f"1..{layer.chunk_count}"

    edited = ms.with_layout_cell(project, row, layer.chunk_count)
    reread = surface.cells(layer.map_index, layer.slot, edited)[0]

    assert reread.revertable
    assert reread.field.minimum == 0
    assert reread.field.range_text == f"0..{layer.chunk_count}"


def test_a_cell_set_back_to_its_chunk_removes_the_authored_edit(surface, project):
    layer, cells = _first_paintable(surface, project)
    row = cells[0]
    edited = ms.with_layout_cell(project, row, layer.chunk_count)
    reverted = ms.with_layout_cell(edited, row, 0)

    assert edited.layout.cells()
    assert reverted.layout.cells() == {}
    assert surface.changes(reverted) == ()


def test_two_edited_cells_are_two_changes_in_table_order(surface, project):
    layer, cells = _first_paintable(surface, project)
    edited = ms.with_layout_cell(project, cells[0], layer.chunk_count)
    other = next(cell for cell in cells if cell.identity != cells[0].identity)
    edited = ms.with_layout_cell(edited, other, layer.chunk_count)

    changes = surface.changes(edited)

    assert [change.owner for change in changes] == [cells[0].identity, other.identity]


# --- 4. the warps -------------------------------------------------------------


def test_every_transition_of_the_image_is_a_warp_row(surface):
    rows = surface.warps()

    assert len(rows) == surface.transitions.record_count
    assert len({row.identity for row in rows}) == len(rows)
    assert all(row.identity.startswith("map:") and "/transition:" in row.identity for row in rows)
    assert all(row.size == 24 for row in rows)


def test_a_warp_states_the_map_it_leads_to_and_that_it_may_be_edited(surface):
    row = surface.warps(map_index=DOORED_MAP)[0]

    assert row.editable
    assert row.destination is not None
    assert row.destination_text == f"Map {row.destination:04d}"
    assert row.field.name == "destination"
    assert row.field.value == row.destination
    assert row.field.maximum == surface.transitions.map_count - 1


def test_one_warp_edit_produces_one_change_owned_by_the_transition_identity(
    surface, project
):
    row = surface.warps(map_index=DOORED_MAP)[0]
    target = row.destination + 1
    ms.check_transition(surface.transitions, row, target)
    edited = ms.with_warp_destination(project, surface.transitions, row, target)

    changes = surface.changes(edited)

    assert len(changes) == 1
    assert changes[0].owner == row.identity
    assert changes[0].offset == row.file_offset
    assert len(changes[0].old) == len(changes[0].new) == 24
    assert changes[0].old != changes[0].new
    assert surface.pending_bytes(edited) == {row.file_offset: changes[0].new}


def test_a_warp_set_back_to_its_canonical_destination_authors_nothing(
    surface, project
):
    row = surface.warps(map_index=DOORED_MAP)[0]
    edited = ms.with_warp_destination(
        project, surface.transitions, row, row.destination + 1
    )
    reverted = ms.with_warp_destination(
        edited, surface.transitions, row, row.destination
    )

    assert edited.transitions.edits()
    assert reverted.transitions.edits() == project.transitions.edits()
    assert surface.changes(reverted) == ()


def test_a_destination_that_resolves_to_no_map_is_the_sdk_own_refusal(surface):
    row = surface.warps(map_index=DOORED_MAP)[0]

    with pytest.raises(TransitionFieldError):
        ms.check_transition(surface.transitions, row, surface.transitions.map_count)


def test_the_warp_view_reads_no_unproven_edge(surface):
    """The map graph's destinations are unproven, so no surface may read them."""
    tree = ast.parse(Path(ms.__file__).read_text(encoding="utf-8"))
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    assert "MapGraph" not in imported
    assert "MapConnection" not in imported
    for row in surface.warps():
        if row.editable:
            assert row.destination is not None
            assert MapIdentity(row.destination).key in {
                item.identity for item in surface.map_rows()
            }


# --- 5. the loader ------------------------------------------------------------


def test_a_profile_that_disagrees_with_the_open_image_is_refused(
    catalog, canonical_rom, identification, profile
):
    """The one check that keeps a table read against another profile out of view."""

    class _OtherProfile:
        id = "not_the_open_images_profile"

    with pytest.raises(ms.MapSurfaceError):
        ms.load_map_surface(
            canonical_rom, catalog, identification, _OtherProfile(), canonical_rom.read_bytes()
        )
