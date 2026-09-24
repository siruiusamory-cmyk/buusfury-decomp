"""Focused interaction tests for the Map Browser tab.

Synthetic only: the ROM-touching facade functions and the layout-edit session are
monkeypatched so the tab's list, search, selection, layer-toggle, info-panel,
edit-mode, cell-selection, chooser, apply/revert/reset, Save As and error paths are
exercised headlessly without a ROM. The real edit session's own ROM-coupled
behaviour is pinned in ``tests/integration/test_map_layout_editor_rom.py``.
"""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QtCore = pytest.importorskip("PySide6.QtCore")
QtGui = pytest.importorskip("PySide6.QtGui")

from tools.export import map_browser as mb  # noqa: E402
from tools.webfoot import map_layout_edit as mle  # noqa: E402
from tools.webfoot import map_layout_provenance as prov  # noqa: E402
from tools.webfoot.map_layout_edit import (  # noqa: E402
    LayoutCell,
    LayoutGrid,
    LayoutSlot,
    LayoutSave,
    LayoutTarget,
    MapLayoutEditError,
)
from tools.webfoot.map_layout_write import MapLayoutWriteError  # noqa: E402
from tools.webfoot.workbench import map_browser_tab as mbt  # noqa: E402
from tools.webfoot.workbench.map_browser_tab import MapBrowserTab  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _entry(index: int, name: str | None) -> mb.MapIndexEntry:
    return mb.MapIndexEntry(index=index, name=name, text_index=0 if name else None)


def _result(index: int, *, width: int = 512, height: int = 512) -> mb.MapBrowserResult:
    layer = mb.MapBrowserLayer(
        slot=0,
        classification="dominant",
        handler=0x08008087,
        addend=2,
        width=width,
        height=height,
        pixels=bytes([5]) * (width * height),
    )
    return mb.MapBrowserResult(
        index=index,
        name=None,
        width=width,
        height=height,
        layers=(layer,),
        composite=layer.pixels,
        palette=tuple((i, i, i) for i in range(256)),
        warnings=("composite placement is derived",),
    )


@pytest.fixture
def tab(qapp, monkeypatch):
    entries = (_entry(0, "West City"), _entry(1, None), _entry(2, "Buu's House"))
    calls: list[int] = []
    monkeypatch.setattr(mbt.mb, "read_map_index", lambda rom: entries)

    def render(rom, index, **kwargs):
        calls.append(index)
        return _result(index)

    monkeypatch.setattr(mbt.mb, "render_map", render)
    value = MapBrowserTab(Session(rom_image=b"synthetic"))
    value.on_session_changed()
    value._render_calls = calls
    return value


def test_list_uses_names_and_neutral_fallbacks(tab):
    texts = [tab._list.item(i).text() for i in range(tab._list.count())]
    assert texts == ["West City  ·  map:0000", "map:0001", "Buu's House  ·  map:0002"]


def test_search_filters_by_name_and_identity(tab):
    tab._search.setText("west")
    assert not tab._list.item(0).isHidden()
    assert tab._list.item(1).isHidden()
    assert tab._list.item(2).isHidden()

    tab._search.setText("map:0001")
    assert tab._list.item(0).isHidden()
    assert not tab._list.item(1).isHidden()
    assert tab._list.item(2).isHidden()

    tab._search.setText("")
    assert all(not tab._list.item(i).isHidden() for i in range(tab._list.count()))


def test_selection_renders_on_demand_and_fills_info_panel(tab):
    tab._list.setCurrentRow(0)
    assert tab._render_calls == [0]
    assert tab._identity.text() == "map:0000"
    assert tab._dimensions.text() == "512 × 512 px"
    assert tab._layer_count.text() == "1 graphical · 1 slot(s)"
    assert tab._layer_types.text() == "BG0 · dominant (512×512)"
    assert tab._notes.text() == "composite placement is derived"


def test_render_cache_skips_redundant_work(tab):
    tab._list.setCurrentRow(0)
    tab._list.setCurrentRow(0)
    assert tab._render_calls == [0]


def test_layer_toggle_recomposes_visible_layers(tab, monkeypatch):
    composed: list[list] = []
    monkeypatch.setattr(mbt.mb, "compose", lambda visible, w, h: composed.append(list(visible)) or b"")
    monkeypatch.setattr(mbt.mb, "rgba", lambda indices, palette: b"\x00" * (512 * 512 * 4))
    tab._list.setCurrentRow(0)
    composed.clear()

    check = tab._layer_checks[0]
    check.setChecked(False)  # no visible layers: short-circuits, no compose
    assert composed == []

    check.setChecked(True)  # one visible layer: compose runs once
    assert len(composed) == 1 and len(composed[-1]) == 1


def test_render_error_is_a_message_not_a_crash(tab, monkeypatch):
    def boom(rom, index, **kwargs):
        raise mb.MapBrowserError("boom")

    monkeypatch.setattr(mbt.mb, "render_map", boom)
    errors: list[str] = []
    monkeypatch.setattr(mbt.QMessageBox, "warning", lambda *args: errors.append(args[-1]))

    tab._list.setCurrentRow(0)
    assert errors == ["boom"]
    assert tab._current is None


def test_index_error_is_a_message_not_a_crash(tab, monkeypatch):
    def boom(rom):
        raise mb.MapBrowserError("cannot enumerate maps")

    monkeypatch.setattr(mbt.mb, "read_map_index", boom)
    errors: list[str] = []
    monkeypatch.setattr(mbt.QMessageBox, "critical", lambda *args: errors.append(args[-1]))

    tab.on_session_changed()
    assert errors == ["cannot enumerate maps"]
    assert tab._list.count() == 0


# --- EDIT LAYOUT mode --------------------------------------------------------
#
# DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001. These tests drive the real tab against a
# duck-typed edit session, so every wiring the user touches - mode toggle, grid
# overlay, cell selection, chooser, apply/revert/reset, Save As, read-only state
# and error handling - is exercised without a ROM. The session's own ROM-coupled
# behaviour is pinned by the ROM-gated integration suite.

MAP = 0
SLOT = 0
CHUNKS = (0x082928DC, 0x08292A54, 0x08292AFC, 0x08292BD8)


def _edit_slot(
    slot: int = SLOT,
    *,
    columns: int = 2,
    rows: int = 2,
    pointers: tuple[int, ...] = CHUNKS,
    classification: str = "dominant",
    reason: str = "",
) -> LayoutSlot:
    grid = LayoutGrid(columns, rows)
    cells = tuple(
        LayoutCell(
            cell=index,
            column=grid.column_of(index) if grid.cell_count else 0,
            row=grid.row_of(index) if grid.cell_count else 0,
            pointer=pointer,
            offset=0x00292CA0 + 4 * index,
        )
        for index, pointer in enumerate(pointers)
    )
    choices = tuple(dict.fromkeys(pointer for pointer in pointers if pointer))
    return LayoutSlot(
        slot=slot,
        classification=classification,
        handler=0x08008087,
        grid=grid,
        cells=cells,
        choices=choices,
        read_only_reason=reason,
    )


def _read_only_slot(slot: int, reason: str, classification: str = "static_graphical_terrain_field") -> LayoutSlot:
    return LayoutSlot(
        slot=slot,
        classification=classification,
        handler=0x080088BD,
        grid=LayoutGrid(0, 0),
        cells=(),
        choices=(),
        read_only_reason=reason,
    )


def _read_only_map_slots() -> tuple[LayoutSlot, ...]:
    """Map 19's shape: a single-chunk dominant grid plus uneditable forms."""
    return (
        _read_only_slot(0, "a grid of 1 cell(s) using a single chunk", "dominant"),
        _read_only_slot(1, "a screen-entry layer, not the dominant chunk grid"),
        _read_only_slot(2, "a terrain-field layer, the special graphical form Map 19 uses"),
        _read_only_slot(3, mle._READ_ONLY_FORMS["absent_placeholder"]),
    )


def _target(
    map_index: int = MAP, slots: tuple[LayoutSlot, ...] | None = None
) -> LayoutTarget:
    if slots is None:
        editable = _edit_slot(SLOT)
        slots = (
            editable,
            _read_only_slot(1, "a screen-entry layer, not the dominant chunk grid"),
            _read_only_slot(2, "a terrain-field layer, the special graphical form Map 19 uses"),
            _read_only_slot(3, "the slot holds no layer"),
        )
    return LayoutTarget(map_index=map_index, name="Synthetic Map", slots=slots)


class _FakeEditor:
    """A duck-typed stand-in for ``MapLayoutEditor``: no ROM, real tab wiring."""

    def __init__(self, target: LayoutTarget, preview: mb.MapBrowserResult) -> None:
        self._target = target
        self._preview = preview
        self._edits: dict[tuple[int, int, int], object] = {}
        self.preview_calls: list[tuple[int, tuple | None]] = []
        self.save_calls: list[tuple[str, str, str]] = []
        self.character_block_calls: list[int] = []
        self.reset_calls = 0
        #: When set, set_cell raises it: the tab must show, not crash. It is set to
        #: whichever SDK failure family the test wants the slot to survive.
        self.reject: Exception | None = None
        #: Same, for the revert paths.
        self.reject_revert: Exception | None = None

    # -- reads the tab performs ------------------------------------------
    def target(self, map_index: int) -> LayoutTarget:
        return self._target

    def edit(self, map_index: int, layer_slot: int, cell: int):
        return self._edits.get((map_index, layer_slot, cell))

    def edits(self) -> tuple:
        return tuple(self._edits[key] for key in sorted(self._edits))

    def edits_for(self, map_index: int) -> tuple:
        return tuple(edit for edit in self.edits() if edit.map_index == map_index)

    def working_pointer(self, map_index: int, layer_slot: int, cell: int) -> int:
        edit = self.edit(map_index, layer_slot, cell)
        if edit is not None:
            return edit.replacement
        return self._target.slots[layer_slot].cells[cell].pointer

    def overrides(self, map_index: int, draft=None) -> dict:
        overrides = {
            (edit.layer_slot, edit.cell): edit.replacement
            for edit in self.edits_for(map_index)
        }
        if draft is not None:
            overrides[(draft[0], draft[1])] = draft[2]
        return overrides

    def preview(self, map_index: int, draft=None) -> mb.MapBrowserResult:
        self.preview_calls.append((map_index, draft))
        return self._preview

    # -- edits the tab requests ------------------------------------------
    def character_block(self, map_index: int) -> bytes:
        """The session's cached character block; the chooser renders through it."""
        self.character_block_calls.append(map_index)
        return b"synthetic-block"

    def set_cell(self, map_index: int, layer_slot: int, cell: int, replacement: int):
        if self.reject:
            raise self.reject
        slot = self._target.slots[layer_slot]
        original = slot.cells[cell].pointer
        key = (map_index, layer_slot, cell)
        if replacement == original:
            self._edits.pop(key, None)
            return None
        edit = mle_edit(map_index, layer_slot, cell, original, replacement, slot.cells[cell].offset)
        self._edits[key] = edit
        return edit

    def revert_cell(self, map_index: int, layer_slot: int, cell: int) -> bool:
        if self.reject_revert:
            raise self.reject_revert
        return self._edits.pop((map_index, layer_slot, cell), None) is not None

    def reset(self) -> int:
        self.reset_calls += 1
        dropped = len(self._edits)
        self._edits.clear()
        return dropped

    def save(self, output_path, *, source_path, profile_id) -> LayoutSave:
        self.save_calls.append((str(output_path), str(source_path), profile_id))
        changes = self.edits()
        return LayoutSave(
            output_path=Path(output_path),
            manifest_path=Path(str(output_path) + ".dragonbyte.json"),
            output_sha256="ab" * 32,
            output_size=8,
            no_op=not changes,
            changes=changes,
            changed_offsets=tuple(
                offset for edit in changes for offset in range(edit.offset, edit.offset + 4)
            ),
            verified=changes,
        )


def mle_edit(map_index, layer_slot, cell, original, replacement, offset):
    from tools.webfoot.map_layout_edit import LayoutEdit

    return LayoutEdit(
        map_index=map_index,
        layer_slot=layer_slot,
        cell=cell,
        original=original,
        replacement=replacement,
        offset=offset,
    )


class _FakeMouseEvent:
    """The tiny slice of a QGraphicsSceneMouseEvent the grid overlay touches."""

    def __init__(self, x: int, y: int) -> None:
        self._pos = QtCore.QPointF(x, y)
        self.accepted = False

    def button(self):
        return QtCore.Qt.MouseButton.LeftButton

    def pos(self):
        return self._pos

    def accept(self) -> None:
        self.accepted = True


@pytest.fixture
def edit_tab(qapp, monkeypatch, tmp_path):
    """The tab with an editable map and a fake edit session wired in."""
    entries = (_entry(MAP, "Synthetic Map"),)
    base = _result(MAP)
    preview_result = _result(MAP)
    preview_result = mb.MapBrowserResult(
        index=base.index,
        name=base.name,
        width=base.width,
        height=base.height,
        layers=base.layers,
        composite=bytes([9]) * (base.width * base.height),
        palette=base.palette,
        warnings=base.warnings,
    )
    fake = _FakeEditor(_target(), preview_result)
    rom_path = tmp_path / "Dragon Ball Z - Buu's Fury (U).gba"
    rom_path.write_bytes(b"synthetic")
    session = Session(rom_image=b"synthetic", rom_path=rom_path)
    session.profile = SimpleNamespace(id="buus_fury_usa_rev0_01c1707f")

    monkeypatch.setattr(mbt.mb, "read_map_index", lambda rom: entries)
    monkeypatch.setattr(mbt.mb, "render_map", lambda rom, index, **kwargs: base)
    def _chunk_images(rom, index, addresses, *, char_data=None):
        return tuple(
            mb.ChunkImage(
                address=address, width=256, height=256, pixels=bytes([7]) * (256 * 256)
            )
            for address in addresses
        )

    monkeypatch.setattr(mbt.mb, "render_chunk_images", _chunk_images)
    monkeypatch.setattr(mbt, "MapLayoutEditor", lambda rom_image: fake)

    value = MapBrowserTab(session)
    value.on_session_changed()
    value._list.setCurrentRow(0)
    value.editor = fake
    value.preview_result = preview_result
    return value


def _choose(tab, row: int) -> None:
    tab._chooser.setCurrentRow(row)


def test_edit_mode_is_off_by_default(edit_tab):
    assert not edit_tab._edit_mode
    assert edit_tab._editor_box.isHidden()
    assert edit_tab._chooser_box.isHidden()
    assert edit_tab._grid_item is None
    assert "read-only" in edit_tab._status.text()
    assert edit_tab._edit_toggle.isEnabled()


def test_entering_edit_mode_installs_the_chunk_grid_and_chooser(edit_tab):
    edit_tab._edit_toggle.setChecked(True)
    assert edit_tab._edit_mode
    assert not edit_tab._editor_box.isHidden() and not edit_tab._chooser_box.isHidden()
    assert edit_tab._grid_item is not None
    assert edit_tab._grid_item._grid.cell_count == 4
    # Only the editable slot is offered.
    assert edit_tab._layer_combo.count() == 1
    assert edit_tab._layer_combo.currentData() == SLOT
    # The chooser offers the layer's own chunks, and marks the cell's current one.
    assert edit_tab._chooser.count() == len(CHUNKS)
    current = [edit_tab._chooser.item(i).text() for i in range(edit_tab._chooser.count())]
    assert "current" in current[0]
    assert "current" not in current[1]
    assert edit_tab._selected_cell == 0
    assert "EDIT LAYOUT" in edit_tab._mode_badge.text()
    assert "EDIT LAYOUT" in edit_tab._status.text()


def test_clicking_a_cell_selects_it_and_shows_its_chunk(edit_tab):
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(3)
    assert edit_tab._selected_cell == 3
    assert edit_tab._grid_item._selected == 3
    assert "column 1, row 1" in edit_tab._cell_label.text()
    assert "cell 4 of 4" in edit_tab._cell_label.text()
    assert "Chunk 4" in edit_tab._chunk_label.text()
    assert f"{CHUNKS[3]:#010x}" in edit_tab._detail.text()


def test_grid_click_selects_the_cell(edit_tab):
    edit_tab._edit_toggle.setChecked(True)
    overlay = edit_tab._grid_item
    event = _FakeMouseEvent(300, 20)  # second column, first row
    overlay.mousePressEvent(event)
    assert event.accepted
    assert edit_tab._selected_cell == 1


def test_arrow_keys_move_the_cell_selection(edit_tab):
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(0)
    right = QtGui.QKeyEvent(
        QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_Right, QtCore.Qt.KeyboardModifier.NoModifier
    )
    assert edit_tab._on_canvas_key(right)
    assert edit_tab._selected_cell == 1
    down = QtGui.QKeyEvent(
        QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_Down, QtCore.Qt.KeyboardModifier.NoModifier
    )
    assert edit_tab._on_canvas_key(down)
    assert edit_tab._selected_cell == 3
    # At the edge the selection stays put rather than wrapping.
    assert edit_tab._on_canvas_key(down)
    assert edit_tab._selected_cell == 3


def test_choosing_a_chunk_previews_in_memory_only(edit_tab):
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(0)
    before = edit_tab._session.rom_image
    _choose(edit_tab, 1)
    assert edit_tab.editor.preview_calls == [(MAP, (SLOT, 0, CHUNKS[1]))]
    assert edit_tab._current is edit_tab.preview_result
    # The source bytes are the same object: previewing never touches the ROM.
    assert edit_tab._session.rom_image is before
    assert "preview" in edit_tab._detail.text()
    assert "unapplied choice" in edit_tab._status.text()
    assert edit_tab._apply_button.isEnabled()


def test_apply_commits_the_change_and_reports_it_as_unsaved(edit_tab):
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(0)
    _choose(edit_tab, 1)
    edit_tab._apply_draft()
    assert edit_tab.editor.edits_for(MAP)[0].replacement == CHUNKS[1]
    assert "unsaved" in edit_tab._change_label.text()
    assert edit_tab._grid_item._edited == frozenset({0})
    assert edit_tab._reset_button.isEnabled()
    assert edit_tab._save_button.isEnabled()
    assert not edit_tab._apply_button.isEnabled()


def test_revert_returns_the_cell_to_the_source_rom_chunk(edit_tab):
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(0)
    _choose(edit_tab, 1)
    edit_tab._apply_draft()
    edit_tab._revert_cell()
    assert edit_tab.editor.edits_for(MAP) == ()
    assert "No layout changes" in edit_tab._change_label.text()
    assert edit_tab._grid_item._edited == frozenset()
    assert not edit_tab._reset_button.isEnabled()


def test_escape_drops_an_unapplied_choice(edit_tab):
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(0)
    _choose(edit_tab, 1)
    assert edit_tab._draft == (SLOT, 0, CHUNKS[1])
    escape = QtGui.QKeyEvent(
        QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_Escape, QtCore.Qt.KeyboardModifier.NoModifier
    )
    assert edit_tab._on_canvas_key(escape)
    assert edit_tab._draft is None
    assert edit_tab.editor.edits_for(MAP) == ()
    assert edit_tab._chooser.currentItem().data(mbt._CHUNK_ROLE) == CHUNKS[0]


def test_reset_drops_every_pending_edit(edit_tab, monkeypatch):
    monkeypatch.setattr(
        mbt.QMessageBox, "information", lambda *args, **kwargs: None
    )
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(0)
    _choose(edit_tab, 1)
    edit_tab._apply_draft()
    edit_tab._on_cell_clicked(3)
    _choose(edit_tab, 0)
    edit_tab._apply_draft()
    assert len(edit_tab.editor.edits_for(MAP)) == 2
    edit_tab._reset_edits()
    assert edit_tab.editor.reset_calls == 1
    assert edit_tab.editor.edits_for(MAP) == ()
    assert "Discarded 2 pending layout change(s)" in edit_tab._status.text()


def test_a_map_without_an_editable_layer_stays_read_only(edit_tab, monkeypatch):
    target = _target(slots=_read_only_map_slots())
    monkeypatch.setattr(edit_tab.editor, "_target", target)
    edit_tab._sync_editor_for_map(MAP)
    edit_tab._edit_toggle.setChecked(True)
    assert edit_tab._target is not None and not edit_tab._target.editable
    assert edit_tab._layer_combo.count() == 0
    assert edit_tab._chooser.count() == 0
    assert not edit_tab._chooser.isEnabled()
    assert not edit_tab._save_button.isEnabled()
    assert edit_tab._grid_item is None
    badge = edit_tab._mode_badge.text()
    assert badge.startswith("READ ONLY")
    # The badge is a short state; the per-layer explanation sits under it, in full.
    assert badge == "READ ONLY · unsupported layout type or no alternative chunk"
    assert edit_tab._layer_combo.isHidden()
    detail = edit_tab._read_only_detail.text()
    assert "terrain-field" in detail and "Map 19" in detail
    assert "single chunk" in detail and "screen-entry" in detail
    # Each reason completes the sentence the target composes.
    assert "BG3 is an empty slot holding no layer" in detail
    # The status line must not claim an editing state the badge calls read-only.
    assert "no editable layer on this map" in edit_tab._status.text()
    assert "no changes yet" not in edit_tab._status.text()
    # Read-only is a state, not an error: the toggle stays usable and no dialog
    # is raised.
    assert edit_tab._edit_toggle.isEnabled()


def test_a_session_change_leaves_edit_mode(qapp, monkeypatch, tmp_path):
    entries = (_entry(MAP, "Synthetic Map"),)
    monkeypatch.setattr(mbt.mb, "read_map_index", lambda rom: entries)
    monkeypatch.setattr(mbt.mb, "render_map", lambda rom, index, **kwargs: _result(index))
    monkeypatch.setattr(mbt, "MapLayoutEditor", lambda rom_image: None)
    tab = MapBrowserTab(Session(rom_image=b"synthetic", rom_path=tmp_path / "s.gba"))
    tab.on_session_changed()
    tab._list.setCurrentRow(0)
    tab._edit_toggle.setChecked(True)
    assert tab._edit_mode
    tab.on_session_changed()
    assert not tab._edit_mode
    assert not tab._edit_toggle.isChecked()
    assert tab._editor_box.isHidden() and tab._chooser_box.isHidden()


def test_an_editable_map_shows_the_layer_row(edit_tab):
    edit_tab._edit_toggle.setChecked(True)
    assert not edit_tab._layer_combo.isHidden()
    assert edit_tab._read_only_detail.text() == ""
    assert edit_tab._mode_badge.text().startswith("EDIT LAYOUT")


def test_map_19_style_layer_is_described_not_called_an_error(edit_tab, monkeypatch):
    warnings: list[str] = []
    monkeypatch.setattr(
        mbt.QMessageBox, "warning", lambda *args: warnings.append(args[-1])
    )
    target = _target(map_index=19, slots=_read_only_map_slots())
    monkeypatch.setattr(edit_tab.editor, "_target", target)
    edit_tab._sync_editor_for_map(19)
    edit_tab._edit_toggle.setChecked(True)
    assert warnings == []
    assert "READ ONLY" in edit_tab._mode_badge.text()


def test_an_unsupported_rom_keeps_browsing_read_only(qapp, monkeypatch, tmp_path):
    entries = (_entry(MAP, "Synthetic Map"),)
    monkeypatch.setattr(mbt.mb, "read_map_index", lambda rom: entries)
    monkeypatch.setattr(mbt.mb, "render_map", lambda rom, index, **kwargs: _result(index))
    tab = MapBrowserTab(Session(rom_image=b"synthetic", rom_path=tmp_path / "s.gba"))
    tab.on_session_changed()
    tab._list.setCurrentRow(0)
    tab._edit_toggle.setChecked(True)
    assert tab._editor is None
    assert tab._mode_badge.text() == "READ ONLY · layout editing is unavailable"
    # The refusal names the profile whose extents the writer would resolve
    # against, which is the profile authority rather than a bare hash literal.
    assert "profile 'buus_fury_usa_rev0_01c1707f'" in tab._read_only_detail.text()
    assert not tab._save_button.isEnabled()


def test_a_rejected_replacement_is_a_message_not_a_crash(edit_tab, monkeypatch):
    errors: list[str] = []
    monkeypatch.setattr(mbt.QMessageBox, "warning", lambda *args: errors.append(args[-1]))
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(0)
    _choose(edit_tab, 1)
    edit_tab.editor.reject = MapLayoutEditError(
        "a replacement chunk must already be used by the same dominant layer"
    )
    edit_tab._apply_draft()
    assert errors == [
        "a replacement chunk must already be used by the same dominant layer"
    ]
    assert edit_tab.editor.edits_for(MAP) == ()
    assert edit_tab._draft is not None  # the pick is kept so the user can retry


def test_a_writer_family_rejection_is_also_a_message_not_a_crash(edit_tab, monkeypatch):
    """MapLayoutWriteError is a sibling of MapLayoutEditError, not a child."""
    errors: list[str] = []
    monkeypatch.setattr(mbt.QMessageBox, "warning", lambda *args: errors.append(args[-1]))
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(0)
    _choose(edit_tab, 1)
    edit_tab.editor.reject = MapLayoutWriteError("the null chunk pointer is not a replacement")
    edit_tab._apply_draft()
    assert errors == ["the null chunk pointer is not a replacement"]

    edit_tab.editor.reject = None
    edit_tab._apply_draft()
    edit_tab.editor.reject_revert = MapLayoutWriteError("boom")
    edit_tab._revert_cell()
    assert errors[-1] == "boom"


def test_chooser_renders_through_the_sessions_cached_character_block(edit_tab, monkeypatch):
    calls: list[dict] = []
    monkeypatch.setattr(
        mbt.mb,
        "render_chunk_images",
        lambda rom, index, addresses, **kwargs: calls.append(kwargs)
        or tuple(
            mb.ChunkImage(address=a, width=256, height=256, pixels=bytes([7]) * (256 * 256))
            for a in addresses
        ),
    )
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._populate_chooser()
    assert calls == [{"char_data": b"synthetic-block"}]
    assert MAP in edit_tab.editor.character_block_calls


def test_pending_edits_reappear_when_a_map_is_re_selected(edit_tab):
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(0)
    _choose(edit_tab, 1)
    edit_tab._apply_draft()
    edit_tab.editor.preview_calls.clear()
    # Re-selecting the map must re-render from the session, not the cached base.
    edit_tab._render_map(MAP)
    assert edit_tab.editor.preview_calls == [(MAP, None)]
    assert edit_tab._current is edit_tab.preview_result
    assert "1 unsaved change(s)" in edit_tab._status.text()


def test_a_render_error_forgets_the_map_selection_and_cannot_crash_edit_mode(
    edit_tab, monkeypatch
):
    edit_tab._edit_toggle.setChecked(True)
    assert edit_tab._slot is not None
    monkeypatch.setattr(mbt.QMessageBox, "warning", lambda *args: None)

    def boom(rom, index, **kwargs):
        raise mb.MapBrowserError("boom")

    monkeypatch.setattr(mbt.mb, "render_map", boom)
    # The fixture already rendered this map, so force the render path itself.
    edit_tab._render_cache.clear()
    edit_tab._render_map(MAP)
    assert edit_tab._current is None
    assert edit_tab._slot is None and edit_tab._target is None
    assert edit_tab._grid_item is None
    assert edit_tab._chooser.count() == 0
    # Toggling edit mode on an empty tab must be a no-op, not an AttributeError.
    edit_tab._edit_toggle.setChecked(False)
    edit_tab._edit_toggle.setChecked(True)
    assert edit_tab._grid_item is None
    assert not edit_tab._save_button.isEnabled()


def test_save_as_writes_a_new_rom_and_reports_it(edit_tab, monkeypatch, tmp_path):
    target = tmp_path / "Dragon Ball Z - Buu's Fury (U) - Edited.gba"
    monkeypatch.setattr(
        mbt.QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), ""))
    )
    shown: list[str] = []
    monkeypatch.setattr(mbt.QMessageBox, "information", lambda *args: shown.append(args[-1]))

    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(0)
    _choose(edit_tab, 1)
    edit_tab._on_save_as()

    assert edit_tab.editor.save_calls == [
        (str(target), str(edit_tab._session.rom_path), "buus_fury_usa_rev0_01c1707f")
    ]
    # Save As writes what the preview showed: the unapplied pick was committed.
    assert edit_tab.editor.edits_for(MAP)[0].replacement == CHUNKS[1]
    assert "✔" in edit_tab._change_label.text()
    assert str(target) in edit_tab._status.text()
    assert shown and "SHA-256" in shown[0]
    assert "source ROM was not modified" in shown[0]


def test_save_as_default_name_comes_from_the_source_rom(edit_tab):
    default = edit_tab._default_output_path()
    assert default is not None
    assert default.name == "Dragon Ball Z - Buu's Fury (U) - Edited.gba"
    assert default.parent == edit_tab._session.rom_path.parent


def test_save_as_refuses_the_source_rom_path(edit_tab, monkeypatch, tmp_path):
    monkeypatch.setattr(
        mbt.QFileDialog,
        "getSaveFileName",
        staticmethod(lambda *a, **k: (str(edit_tab._session.rom_path), "")),
    )
    errors: list[str] = []
    monkeypatch.setattr(mbt.QMessageBox, "critical", lambda *args: errors.append(args[-1]))
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_save_as()
    assert edit_tab.editor.save_calls == []
    assert errors and "overwrite the source ROM" in errors[0]


def test_save_as_no_op_is_allowed_and_reported(edit_tab, monkeypatch, tmp_path):
    target = tmp_path / "copy.gba"
    monkeypatch.setattr(
        mbt.QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), ""))
    )
    shown: list[str] = []
    monkeypatch.setattr(mbt.QMessageBox, "information", lambda *args: shown.append(args[-1]))
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_save_as()
    assert edit_tab.editor.save_calls and shown
    assert "byte-identical" in shown[0]
    assert "byte-identical" in edit_tab._status.text()


def test_save_as_leaves_an_existing_destination_to_the_emit(edit_tab, monkeypatch, tmp_path):
    """The tab must not delete the destination: the emit publishes atomically."""
    target = tmp_path / "existing.gba"
    target.write_bytes(b"old")
    monkeypatch.setattr(
        mbt.QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), ""))
    )
    monkeypatch.setattr(mbt.QMessageBox, "information", lambda *args: None)
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_save_as()
    assert edit_tab.editor.save_calls == [
        (str(target), str(edit_tab._session.rom_path), "buus_fury_usa_rev0_01c1707f")
    ]
    # This fake save writes nothing; the destination is untouched because the tab
    # never removes it, and the real emit replaces it only after verification.
    assert target.read_bytes() == b"old"


def test_a_verified_derivative_renders_its_edits_and_stays_read_only(
    qapp, monkeypatch, tmp_path
):
    """Opening a tool-authored ROM shows its layout, from the canonical bytes."""
    entries = (_entry(MAP, "Synthetic Map"),)
    base = _result(MAP)
    seen: dict = {}

    def render(rom, index, **kwargs):
        seen["rom"] = rom
        seen["overrides"] = kwargs.get("chunk_overrides")
        return base

    monkeypatch.setattr(mbt.mb, "read_map_index", lambda rom: entries)
    monkeypatch.setattr(mbt.mb, "render_map", render)

    session = Session(rom_image=b"derivative-bytes", rom_path=tmp_path / "derived.gba")
    session.profile = SimpleNamespace(id="buus_fury_usa_rev0_01c1707f")
    session.authored = prov.AuthoredRom(
        path=tmp_path / "derived.gba",
        manifest_path=tmp_path / "derived.gba.dragonbyte.json",
        profile_id="buus_fury_usa_rev0_01c1707f",
        canonical_sha256="cd" * 32,
        output_sha256="ab" * 32,
        edits=(
            prov.AuthoredEdit(
                map_index=MAP,
                layer_slot=SLOT,
                cell=1,
                offset=0x00292CA4,
                old=CHUNKS[0],
                new=CHUNKS[1],
            ),
        ),
        canonical_image=b"canonical-bytes",
    )
    tab = MapBrowserTab(session)
    tab.on_session_changed()
    tab._list.setCurrentRow(0)

    assert seen["rom"] == b"canonical-bytes"
    assert seen["overrides"] == {(SLOT, 1): CHUNKS[1]}
    assert "DragonByte Z layout derivative" in tab._notes.text()
    assert "DragonByte Z derivative" in tab._status.text()

    # Editing belongs to the canonical image; the derivative says so.
    tab._edit_toggle.setChecked(True)
    assert tab._editor is None
    assert "READ ONLY" in tab._mode_badge.text()
    assert "derivative" in tab._read_only_detail.text()
    assert not tab._save_button.isEnabled()
    assert tab._grid_item is None


def test_switching_maps_drops_the_selection_and_draft(edit_tab):
    edit_tab._edit_toggle.setChecked(True)
    edit_tab._on_cell_clicked(2)
    _choose(edit_tab, 1)
    assert edit_tab._draft is not None
    edit_tab._sync_editor_for_map(MAP)
    assert edit_tab._draft is None
    assert edit_tab._selected_cell == 0
