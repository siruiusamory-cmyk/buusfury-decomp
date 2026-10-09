"""DRAGONBYTE-Z-MAPS-DESTINATION-001: the Maps destination's page.

The windowed lane runs the real shell offscreen and drives the page a user
drives: the view switch, the map switch, the layer switch, the table, the field
editor, Apply, and `Open bytes`. What it asserts is that the page renders the
model's answers and hands its edit to the shell's one journal - that the window
never computes a support state, a range or a byte effect of its own, and that a
row the evidence does not support carries no edit affordance.

The suite skips without the canonical image.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import replace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

pytest.importorskip("PySide6.QtWidgets")

from tools.dragonbyte import mapsurface as ms  # noqa: E402
from tools.dragonbyte.inspector import SUPPORT_STATES  # noqa: E402
from tools.dragonbyte.mapedits import MAPS_TARGET  # noqa: E402
from tools.dragonbyte.mappage import LAYOUT_MODE, MODES, WARPS_MODE  # noqa: E402
from tools.dragonbyte.session import Session  # noqa: E402
from tools.dragonbyte.shell import Shell  # noqa: E402
from tools.webfoot.build import extract_project  # noqa: E402
from tools.webfoot.catalog import load_catalog  # noqa: E402
from tools.webfoot.rom import identify_rom  # noqa: E402

from tests.unit.test_dragonbyte_state import (  # noqa: E402
    CANONICAL_SHA256,
    SIBLING_CHECKOUT,
    _close,
)

#: A map whose dominant grid is a single chunk, so no cell may be repainted.
ONE_CHUNK_MAP = 1

#: A map the image carries a transition out of.
DOORED_MAP = 33


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


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
def source_project(tmp_path_factory, catalog, canonical_rom):
    directory = tmp_path_factory.mktemp("dbz-mappage") / "source"
    extract_project(canonical_rom, directory, catalog, graphics=False)
    return directory


@pytest.fixture(autouse=True)
def no_range_index(monkeypatch):
    """The ROM page's range index is not what this file tests."""
    from tools.dragonbyte import rompage

    monkeypatch.setattr(
        rompage,
        "load_index",
        lambda profile, directory=None: (None, "the range index is not loaded here"),
    )


def _open(tmp_path, catalog, canonical_rom, source_project, *, project: bool = True):
    session = Session()
    session.open_rom(canonical_rom)
    if project:
        target = tmp_path / "project"
        shutil.copytree(source_project, target)
        session.open_project(target)
    return session, Shell(session, tmp_path / "config")


@pytest.fixture
def map_page(qapp, tmp_path, catalog, canonical_rom, source_project):
    session, shell = _open(tmp_path, catalog, canonical_rom, source_project)
    shell.show_destination("maps")
    yield shell._map_page, shell, session
    _close(shell, session)


def _select_map(page, index: int) -> None:
    page._maps.setCurrentIndex(page._maps.findData(index))
    assert page._map_index == index


def _select_layer(page, slot: int) -> None:
    assert page._surface.layer(page._map_index, slot) is not None
    position = next(
        at
        for at, entry in enumerate(page._surface.layers(page._map_index))
        if entry.slot == slot
    )
    page._layers.setCurrentIndex(position)
    assert page._slot == slot


def _first_paintable(page):
    """Point the page at a cell whose layer offers more than one chunk."""
    for index in (0, ONE_CHUNK_MAP + 1):
        for layer in page._surface.layers(index):
            if layer.editable and layer.chunk_count > 1:
                _select_map(page, index)
                _select_layer(page, layer.slot)
                return layer, page._rows[0]
    pytest.skip("no paintable map in this image")


# --- the two views ------------------------------------------------------------


def test_the_view_switch_offers_layout_and_warps(map_page):
    page, _shell, _session_ = map_page

    assert [label for _identifier, label in MODES] == ["Layout", "Warps"]
    assert page._mode == LAYOUT_MODE
    assert page._modes.currentText() == "Layout"


def test_the_map_switch_lists_every_map_of_the_open_image(map_page):
    page, _shell, _session_ = map_page

    assert page._maps.count() == 452
    assert page._maps.itemData(0) == 0
    assert page._maps.itemText(0).startswith("Map 0000")
    assert page._surface.map_rows()[0].identity == "map:0000"


def test_the_layout_table_renders_the_models_own_cells(map_page):
    page, _shell, _session_ = map_page
    layer, row = _first_paintable(page)

    assert page._model.rowCount() == len(page._rows) == layer.cell_count
    assert page._model.data(page._model.index(0, 0)) == f"{row.cell}"
    assert page._model.data(page._model.index(0, 4)) == f"0x{row.offset:06X}"
    assert "Editable" in page._model.data(page._model.index(0, 5))


def test_an_unsupported_layer_offers_no_edit_affordance_and_states_its_reason(
    map_page,
):
    page, _shell, _session_ = map_page
    _select_map(page, ONE_CHUNK_MAP)

    entry = next(
        layer
        for layer in page._surface.layers(ONE_CHUNK_MAP)
        if not layer.editable and layer.note
    )
    _select_layer(page, entry.slot)

    assert "(read-only)" in page._layers.currentText()
    assert page._model.rowCount() == 0
    assert page._message.text() == entry.note
    assert not page._apply.isEnabled()
    assert not page._open.isEnabled()
    assert page._caret_row() is None


def test_every_support_word_the_page_renders_is_the_inspectors_own(map_page):
    page, _shell, _session_ = map_page
    _layer, _row = _first_paintable(page)

    assert "Editable" in SUPPORT_STATES and "Read-only" in SUPPORT_STATES
    assert "Editable" in page._model.data(page._model.index(0, 5))


# --- one edit through the page ------------------------------------------------


def test_applying_a_cell_edit_commits_one_entry_owned_by_the_row(map_page):
    page, shell, session = map_page
    layer, row = _first_paintable(page)
    target = layer.chunk_count
    assert row.ordinal != target

    page._value.setText(str(target))
    page._apply.click()

    assert session.journal.depth == 1
    entry = session.journal.edits()[0]
    assert entry.target == MAPS_TARGET
    assert entry.claimed == (ms.layout_span(row),)
    assert session.project.layout.cells()[(row.map_index, row.slot, row.cell)] == target
    assert page._caret_row().identity == row.identity
    assert page._caret_row().ordinal == target
    assert page._model.data(page._model.index(0, 3)) == f"{target}"
    assert row.identity in page._message.text() or "chunk" in page._message.text()


def test_the_change_the_page_committed_is_visible_in_the_rom_surface(map_page):
    page, shell, session = map_page
    layer, row = _first_paintable(page)

    page._value.setText(str(layer.chunk_count))
    page._apply.click()
    page._open.click()

    rom = shell._rom_page
    rom._views.setCurrentText("Bytes")

    assert session.navigation.current.destination == "rom"
    assert rom._caret == row.offset
    assert row.offset in rom._surface.overlay
    assert shell._pending_bytes()[row.offset] == (
        page._surface.pending_bytes(session.project)[row.offset]
    )
    assert rom._surface.current_bytes(row.offset, 4) != rom._surface.canonical_bytes(
        row.offset, 4
    )


def test_the_rom_surface_is_asked_for_every_open_destinations_bytes(map_page):
    """One ROM surface, two destinations: neither provider hides the other."""
    page, shell, session = map_page
    layer, row = _first_paintable(page)

    page._value.setText(str(layer.chunk_count))
    page._apply.click()

    shell.show_destination("data")
    data = shell._data_page
    data_row = data._rows[0]
    data._field.setCurrentText("hp")
    data._value.setText(str(data_row.field("hp").value + 1))
    data._apply.click()

    merged = shell._pending_bytes()

    assert row.offset in merged
    assert data_row.file_offset in merged
    assert merged == {
        **page._surface.pending_bytes(session.project),
        **data._surface.pending_bytes(session.project),
    }


def test_a_value_outside_the_layers_vocabulary_is_refused_and_stores_nothing(
    map_page,
):
    page, _shell, session = map_page
    layer, row = _first_paintable(page)

    page._value.setText(str(layer.chunk_count + 50))
    page._apply.click()

    assert session.journal.depth == 0
    assert session.project.layout.cells() == {}
    assert "outside the supported range" in page._message.text()


def test_a_value_that_is_already_the_cells_chunk_reports_and_commits_nothing(
    map_page,
):
    page, _shell, session = map_page
    _layer, row = _first_paintable(page)

    page._value.setText(str(row.field.value))
    page._apply.click()

    assert session.journal.depth == 0
    assert "already" in page._message.text()


def test_the_page_publishes_the_rows_identity_to_the_one_inspector(map_page):
    page, _shell, _session_ = map_page
    _layer, row = _first_paintable(page)

    page._on_row_changed(page._model.index(0, 0), None)

    assert page._caret == row.identity
    assert row.identity in page._detail.text()
    assert "file offset" in page._detail.text()


def test_an_edit_without_an_open_project_is_refused_with_the_reason(
    qapp, tmp_path, catalog, canonical_rom
):
    session, shell = _open(
        tmp_path, catalog, canonical_rom, None, project=False
    )
    try:
        shell.show_destination("maps")
        page = shell._map_page
        _layer, row = _first_paintable(page)

        page._apply.click()

        assert session.journal.depth == 0
        assert "No project is open" in page._message.text()
    finally:
        _close(shell, session)


# --- the warps ----------------------------------------------------------------


def test_the_warps_view_renders_the_transitions_of_the_selected_map(map_page):
    page, _shell, _session_ = map_page
    _select_map(page, DOORED_MAP)
    page._modes.setCurrentText("Warps")

    assert page._mode == WARPS_MODE
    assert not page._layers.isVisible()
    assert len(page._rows) == 1
    row = page._rows[0]
    assert row.identity.startswith(f"map:{DOORED_MAP:04d}/transition:")
    assert page._model.data(page._model.index(0, 2)) == row.destination_text
    assert "Editable" in page._model.data(page._model.index(0, 5))


def test_applying_a_warp_edit_commits_one_entry_owned_by_the_transition(map_page):
    page, shell, session = map_page
    _select_map(page, DOORED_MAP)
    page._modes.setCurrentText("Warps")
    row = page._rows[0]
    target = row.destination + 1

    page._value.setText(str(target))
    page._apply.click()

    assert session.journal.depth == 1
    entry = session.journal.edits()[0]
    assert entry.target == MAPS_TARGET
    assert entry.claimed[0].start.value == row.file_offset
    assert entry.claimed[0].size == row.size
    authored = session.project.transitions.edits()[(row.source, row.index)]
    assert authored.destination == f"map:{target:04d}"
    assert page._caret_row().identity == row.identity


def test_a_warp_whose_destination_does_not_resolve_is_read_only_and_says_why(
    map_page, monkeypatch
):
    page, _shell, _session_ = map_page
    _select_map(page, DOORED_MAP)
    page._modes.setCurrentText("Warps")
    assert page._rows

    unresolvable = replace(
        page._rows[0],
        destination=None,
        destination_text="unresolved",
        editable=False,
        note="its destination key resolves to no map in this profile's table",
    )
    monkeypatch.setattr(
        page._surface, "warps", lambda project, map_index: (unresolvable,)
    )
    page.refresh()

    assert page._rows == (unresolvable,)
    assert not page._apply.isEnabled()
    assert page._caret_row().identity == unresolvable.identity
    assert unresolvable.note in page._detail.text()
    assert "Read-only" in page._model.data(page._model.index(0, 5))
