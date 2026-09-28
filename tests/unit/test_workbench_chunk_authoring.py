"""MAP-CHUNK-AUTHORING-001: the Workbench chunk-authoring surface.

Focused, offscreen, synthetic. The SDK half of this capability is pinned by its
own tests; what is pinned here is the WIRING the user touches - creating a chunk
from a template, painting its 32x32 screen-entry plane, undoing and redoing that,
reverting, applying the chunk to a project, and placing it on a map cell - driven
through the real `MapBrowserTab` against the same duck-typed session, editor and
fixtures `test_workbench_map_browser` uses (imported, not copied, so the two
cannot drift).

Three doubles stand in for ROM-coupled SDK work, and each mirrors its real
contract rather than a convenient shape:

* `_FakeAuthor` stands in for :class:`tools.webfoot.map_chunk.ChunkAuthor` and
  composes REAL :class:`tools.webfoot.project.AuthoredChunk` documents, so the
  tab's own document handling is exercised against the production model;
* the project store stands in for `set_authored_chunk` /
  `set_layout_authored_cells` and their read side, recording the order of the
  writes (the chunk body must land before the cell that references it);
* `mv.render_chunk_entries` returns a flat image, exactly as the existing map
  tests stub the chunk renderer, because no synthetic fixture owns a real
  character block.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QtCore = pytest.importorskip("PySide6.QtCore")

from tools.webfoot.map_chunk import (  # noqa: E402
    ChunkAuthoringError,
    ChunkTemplate,
    chunk_identity,
)
from tools.webfoot.project import (  # noqa: E402
    AuthoredChunk,
    AuthoredChunkEntry,
    AuthoredChunks,
    LayoutEdits,
)
from tools.webfoot.workbench import map_browser_tab as mbt  # noqa: E402
from tools.webfoot.workbench.map_browser_tab import (  # noqa: E402
    AuthoredPlaceCommand,
    ChunkCellCommand,
    ChunkPlaneOverlay,
    MapBrowserTab,
)
from tools.webfoot.workbench.session import Session  # noqa: E402

from tests.unit.test_workbench_map_browser import (  # noqa: E402,F401
    CHUNKS,
    MAP,
    SLOT,
    _FakeEditor,
    _choose,
    _entry,
    _paint_cells,
    _result,
    _target,
    qapp,
)

#: The screen entries the fake layer's own chunks display: the whole permitted
#: authoring vocabulary. Four values is enough to express "paint a different one",
#: "paint the one already there" and "the palette offers exactly these".
VOCAB = (0x0001, 0x0002, 0x0003, 0x0004)

#: The template plane every fake chunk starts from, so an authored cell is
#: unambiguously a change when it differs from VOCAB[0].
TEMPLATE_PLANE = tuple(VOCAB[0] for _ in range(1024))

#: Mutable behaviour the fake facade reads at call time, so one test can make a
#: refusal and the next can clear it without rebuilding the tab.
AUTHOR = {"plane_error": None, "create_error": None, "vocabulary_error": None}

CHUNK_NAME = "qa-chunk"
CHUNK_IDENTITY = "chunk:qa-chunk"


class _FakeResolved:
    """The slice of `ResolvedAuthoredChunk` the tab reads."""

    def __init__(self, chunk: AuthoredChunk) -> None:
        self.identity = chunk.identity
        self.template = ChunkTemplate.parse(chunk.template)
        self.map_index = self.template.map_index
        self.template_entries = TEMPLATE_PLANE
        self.entries = _compose(chunk)
        self.edits = tuple(chunk.entries)
        self.body_sha256 = "0" * 64


def _compose(chunk: AuthoredChunk) -> tuple[int, ...]:
    plane = list(TEMPLATE_PLANE)
    for edit in chunk.entries:
        index = edit.row * 32 + edit.column
        if plane[index] != edit.prior:
            raise ChunkAuthoringError(
                f"chunk cell ({edit.row}, {edit.column}) was authored against "
                f"{edit.prior:#06x}, but the template holds {plane[index]:#06x}"
            )
        plane[index] = edit.entry
    return tuple(plane)


class _FakeAuthor:
    """A duck-typed `ChunkAuthor`: the real contract, no ROM."""

    def __init__(self, canonical_bytes, *, profile=None) -> None:
        self.image = canonical_bytes
        self.profile = profile

    def layer_label(self, map_index: int, layer_slot: int) -> str:
        return f"BG{layer_slot} \u00b7 chunk grid 2\u00d72"

    def templates(self, map_index: int, layer_slot: int):
        return tuple(
            type("Choice", (), {"ordinal": i, "address": address, "cell_count": 1})()
            for i, address in enumerate(CHUNKS[:4], start=1)
        )

    def template_text(self, map_index: int, layer_slot: int, ordinal: int) -> str:
        return ChunkTemplate(map_index, layer_slot, ordinal).text

    def vocabulary(self, map_index: int, layer_slot: int) -> tuple[int, ...]:
        if AUTHOR["vocabulary_error"] is not None:
            raise AUTHOR["vocabulary_error"]
        return VOCAB

    def plane(self, template: ChunkTemplate) -> tuple[int, ...]:
        if AUTHOR["plane_error"] is not None:
            raise AUTHOR["plane_error"]
        return TEMPLATE_PLANE

    def create(self, identity, template: ChunkTemplate, entries):
        if AUTHOR["create_error"] is not None:
            raise AUTHOR["create_error"]
        rows = []
        for (row, column), entry in sorted(entries.items()):
            if not 0 <= row < 32 or not 0 <= column < 32:
                raise ChunkAuthoringError(
                    f"chunk cell ({row}, {column}) is outside the 32x32 plane"
                )
            prior = TEMPLATE_PLANE[row * 32 + column]
            if entry == prior:
                continue
            if entry not in VOCAB:
                raise ChunkAuthoringError(
                    f"screen entry {entry:#06x} is not part of this layer's graphics "
                    "vocabulary"
                )
            rows.append(
                AuthoredChunkEntry(row=row, column=column, prior=prior, entry=entry)
            )
        if not rows:
            raise ChunkAuthoringError(
                "a new chunk must differ from its template; every cell given is "
                "already at that value"
            )
        return AuthoredChunk(
            identity=chunk_identity(identity), template=template.text, entries=tuple(rows)
        )

    def resolve(self, chunk: AuthoredChunk) -> _FakeResolved:
        return _FakeResolved(chunk)

    def entry_label(self, entry: int) -> str:
        return f"tile {entry}"


class _FakeProject:
    """The authored half of a project, in memory, with the SDK's write signatures.

    It records the ORDER of the writes as well as their content, because
    `apply_to_project` has to write a chunk body before the layout cell that
    references it: a project whose layout names an undeclared chunk is refused by
    `read_project`.
    """

    def __init__(self) -> None:
        self.chunks: dict[str, AuthoredChunk] = {}
        self.layout: dict[tuple[int, int, int], str] = {}
        self.writes: list[tuple[str, object]] = []

    # -- the writes the tab performs -----------------------------------------
    def set_chunk(self, project_dir, canonical_bytes, chunk, *, profile=None) -> bool:
        self.writes.append(("chunk", chunk.identity))
        if self.chunks.get(chunk.identity) == chunk:
            return False
        self.chunks[chunk.identity] = chunk
        return True

    def set_authored_cells(self, project_dir, canonical_bytes, edits, *, profile=None):
        self.writes.append(("placement", dict(edits)))
        changed = False
        for key, identity in edits.items():
            current = self.layout.get(key)
            if identity is None:
                if current is not None:
                    self.layout.pop(key)
                    changed = True
            elif current != identity:
                self.layout[key] = identity
                changed = True
        return changed

    def set_cells(self, project_dir, profile, canonical_bytes, edits) -> bool:
        self.writes.append(("paint", dict(edits)))
        return True

    # -- the reads ------------------------------------------------------------
    def read_chunks(self, project_dir) -> AuthoredChunks:
        return AuthoredChunks(chunks=dict(self.chunks))

    def read_layout(self, project_dir) -> LayoutEdits:
        maps: dict[str, dict[int, dict[int, int | str]]] = {}
        for (map_index, layer_slot, cell), identity in self.layout.items():
            maps.setdefault(LayoutEdits.key_for(map_index), {}).setdefault(
                layer_slot, {}
            )[cell] = identity
        return LayoutEdits(maps=maps)


@pytest.fixture
def author_state():
    """Clear the fake facade's mutable behaviour around every test."""
    AUTHOR.update({"plane_error": None, "create_error": None, "vocabulary_error": None})
    yield AUTHOR
    AUTHOR.update({"plane_error": None, "create_error": None, "vocabulary_error": None})


@pytest.fixture
def chunk_tab(qapp, monkeypatch, tmp_path):
    """The real tab with an identified session, a fake facade and a fake project."""
    entries = (_entry(MAP, "Synthetic Map"),)
    base = _result(MAP)
    fake_editor = _FakeEditor(_target(), base)
    rom_path = tmp_path / "rom.gba"
    rom_path.write_bytes(b"synthetic")
    project = _FakeProject()
    session = Session(
        rom_image=b"synthetic",
        rom_path=rom_path,
        project_dir=tmp_path / "project",
        # The chunk facade resolves profile addresses, so it is only offered for
        # an image `open_rom` identified - which this marker stands in for.
        identification=object(),
    )
    session.profile = type("P", (), {"id": "synthetic_profile"})()

    monkeypatch.setattr(mbt.mv, "read_map_index", lambda rom: entries)
    monkeypatch.setattr(mbt.mv, "render_map", lambda rom, index, **kwargs: base)
    monkeypatch.setattr(
        mbt.mv,
        "render_chunk_images",
        lambda rom, index, addresses, **kwargs: tuple(
            mbt.mv.ChunkImage(
                address=a, width=256, height=256, pixels=bytes([7]) * (256 * 256)
            )
            for a in addresses
        ),
    )
    monkeypatch.setattr(
        mbt.mv,
        "render_chunk_entries",
        lambda char_data, plane, **kwargs: mbt.mv.ChunkImage(
            address=0,
            width=kwargs.get("width", 256),
            height=kwargs.get("height", 256),
            pixels=bytes([7]) * (kwargs.get("width", 256) * kwargs.get("height", 256)),
        ),
    )
    monkeypatch.setattr(mbt, "MapLayoutEditor", lambda rom_image: fake_editor)
    monkeypatch.setattr(mbt, "ChunkAuthor", _FakeAuthor)
    monkeypatch.setattr(mbt, "read_authored_chunks", project.read_chunks)
    monkeypatch.setattr(mbt, "read_layout_edits", project.read_layout)
    monkeypatch.setattr(mbt, "set_authored_chunk", project.set_chunk)
    monkeypatch.setattr(mbt, "set_layout_authored_cells", project.set_authored_cells)
    monkeypatch.setattr(mbt, "set_layout_cells", project.set_cells)
    monkeypatch.setattr(
        mbt.QInputDialog, "getText", staticmethod(lambda *a, **k: (CHUNK_NAME, True))
    )

    tab = MapBrowserTab(session)
    tab.on_session_changed()
    tab._list.setCurrentRow(0)
    tab._edit_toggle.setChecked(True)
    tab.editor = fake_editor
    tab.project = project
    return tab


def _open_new_chunk(tab) -> None:
    """The whole user path: pick a template in the palette, then Create Chunk."""
    _choose(tab, 1)  # Chunk 2 is the template (the default brush is 2 already)
    tab.create_chunk()


def _entry_row(tab, entry: int) -> int:
    for row in range(tab._chunk_palette.count()):
        if tab._chunk_palette.item(row).data(mbt._ENTRY_ROLE) == entry:
            return row
    raise AssertionError(f"entry {entry:#06x} is not in the palette")


def _select_entry(tab, entry: int) -> None:
    """Pick a swatch the way the palette's own signal delivers it."""
    row = _entry_row(tab, entry)
    tab._chunk_palette.blockSignals(True)
    tab._chunk_palette.setCurrentRow(row)
    tab._chunk_palette.blockSignals(False)
    tab._on_entry_selected(tab._chunk_palette.item(row))


def _chunk_stroke(tab, *cells: int) -> None:
    """One press-drag-release over the plane, exactly as the overlay delivers it."""
    tab.begin_chunk_stroke()
    for cell in cells:
        tab.paint_chunk_cell(cell)
    tab.end_chunk_stroke()


# --- 1. creating a chunk opens a real editor on a real plane ------------------


def test_create_chunk_opens_the_editor_with_the_right_plane(chunk_tab):
    assert not chunk_tab.chunk_is_open()
    _open_new_chunk(chunk_tab)

    assert chunk_tab.chunk_is_open()
    assert chunk_tab._chunk_identity == CHUNK_IDENTITY
    # The plane is the format's own: 32x32 = 1,024 screen entries.
    assert len(chunk_tab.chunk_plane_entries()) == 1024
    assert chunk_tab.chunk_plane_entries() == TEMPLATE_PLANE
    assert chunk_tab._chunk_template.text == f"map:{MAP:04d}/layer:{SLOT}/chunk:2"
    # The editor is the centre surface, and it says what it is showing. The title
    # speaks the author's name for the chunk; the durable identity
    # (`chunk:qa-chunk`, what the project stores) is on the palette row's tooltip.
    assert chunk_tab._centre_stack.currentWidget() is chunk_tab._chunk_page
    assert "Authored: qa-chunk" in chunk_tab._chunk_title.text()
    assert f"map:{MAP:04d}/layer:{SLOT}/chunk:2" in chunk_tab._chunk_title.text()
    # A brand-new chunk is not dirty and not yet a project document.
    assert not chunk_tab.chunk_is_dirty()
    assert chunk_tab.unsaved_edit_count() == 0
    assert chunk_tab._staged_chunks == {}
    # ...and the plane grid is installed over the artwork.
    assert isinstance(chunk_tab._chunk_overlay, ChunkPlaneOverlay)
    assert chunk_tab._chunk_overlay.cell_count == 1024
    assert chunk_tab._chunk_canvas.scene() is chunk_tab._chunk_scene


def test_the_create_chunk_action_is_offered_for_a_paintable_layer(chunk_tab):
    """Both spellings of the action are live, and Edit chunk waits for a chunk."""
    assert chunk_tab._create_chunk_button.isEnabled()
    assert chunk_tab._create_chunk_action.isEnabled()
    assert not chunk_tab._edit_chunk_button.isEnabled()
    assert "Create a new 256" in chunk_tab._create_chunk_button.toolTip()

    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    assert chunk_tab.use_chunk_as_brush() is True

    assert chunk_tab._edit_chunk_button.isEnabled()
    assert chunk_tab.edit_selected_authored_chunk() is True
    assert chunk_tab._chunk_identity == CHUNK_IDENTITY


def test_use_as_brush_refuses_a_chunk_identical_to_its_template(chunk_tab):
    """A chunk with no authored cell is not yet a placeable value."""
    _open_new_chunk(chunk_tab)
    assert chunk_tab.use_chunk_as_brush() is False
    assert chunk_tab._brush_authored is None
    assert chunk_tab._chunk_identity == CHUNK_IDENTITY
    assert chunk_tab.chunk_is_open(), "the editor stays open on the refusal"


def test_create_chunk_is_refused_before_edit_layout_is_on(chunk_tab):
    chunk_tab._edit_toggle.setChecked(False)
    chunk_tab._refresh_editor_state()
    assert not chunk_tab._create_chunk_button.isEnabled()
    assert not chunk_tab._create_chunk_action.isEnabled()


def test_create_chunk_refuses_a_name_that_already_exists(chunk_tab, monkeypatch):
    warnings: list[str] = []
    monkeypatch.setattr(
        mbt.QMessageBox, "warning", lambda *args: warnings.append(args[-1])
    )
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.apply_chunk()
    chunk_tab.create_chunk()
    assert warnings and "already exists" in warnings[-1]
    # The open chunk was left alone.
    assert chunk_tab._chunk_identity == CHUNK_IDENTITY


# --- 2. the cell gesture ------------------------------------------------------


def test_a_cell_click_stages_an_edit(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])

    chunk_tab.paint_chunk_cell(0)

    plane = chunk_tab.chunk_plane_entries()
    assert plane[0] == VOCAB[1]
    assert plane[1] == VOCAB[0], "only the painted cell changed"
    assert chunk_tab.chunk_is_dirty()
    assert chunk_tab._chunk_brush == VOCAB[1]
    # The grid marks the changed cell, and the inspector says how many differ.
    assert chunk_tab._chunk_overlay._edited == frozenset({0})
    assert "1 cell(s) differ" in chunk_tab._chunk_state_label.text()


def test_a_drag_stages_every_changed_cell_as_one_command(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[2])
    _chunk_stroke(chunk_tab, 0, 1, 33, 1)

    assert [chunk_tab.chunk_plane_entries()[c] for c in (0, 1, 33)] == [VOCAB[2]] * 3
    assert chunk_tab._undo_stack.count() == 1, "a drag is ONE history entry"
    command = chunk_tab._undo_stack.command(0)
    assert isinstance(command, ChunkCellCommand)
    assert command.cells == (0, 1, 33), "a re-entered cell is not listed twice"
    assert command.previous == {0: VOCAB[0], 1: VOCAB[0], 33: VOCAB[0]}
    assert chunk_tab._undo_stack.undoText().startswith("Edit 3 chunk cells")


def test_undo_and_redo_reverse_and_reapply(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[3])
    _chunk_stroke(chunk_tab, 5, 6)

    assert chunk_tab.chunk_plane_entries()[5] == VOCAB[3]
    chunk_tab._undo_stack.undo()
    assert chunk_tab.chunk_plane_entries()[5] == VOCAB[0]
    assert chunk_tab.chunk_plane_entries()[6] == VOCAB[0]
    assert not chunk_tab.chunk_is_dirty()
    assert chunk_tab._chunk_overlay._edited == frozenset()

    chunk_tab._undo_stack.redo()
    assert chunk_tab.chunk_plane_entries()[5] == VOCAB[3]
    assert chunk_tab.chunk_plane_entries()[6] == VOCAB[3]
    assert chunk_tab.chunk_is_dirty()
    assert chunk_tab._chunk_overlay._edited == frozenset({5, 6})


def test_undo_restores_each_cells_own_earlier_entry(chunk_tab):
    """A previous-value capture that recorded the painted entry could not do this."""
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 3)
    _select_entry(chunk_tab, VOCAB[2])
    _chunk_stroke(chunk_tab, 3)
    assert chunk_tab._undo_stack.count() == 2

    chunk_tab._undo_stack.undo()
    assert chunk_tab.chunk_plane_entries()[3] == VOCAB[1]
    chunk_tab._undo_stack.undo()
    assert chunk_tab.chunk_plane_entries()[3] == VOCAB[0]
    assert not chunk_tab.chunk_is_dirty()


def test_a_no_op_paint_creates_no_edit_and_no_history(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[0])  # the entry cell 0 already holds
    _chunk_stroke(chunk_tab, 0)

    assert chunk_tab.chunk_plane_entries() == TEMPLATE_PLANE
    assert chunk_tab._undo_stack.count() == 0
    assert not chunk_tab.chunk_is_dirty()
    assert chunk_tab.unsaved_edit_count() == 0
    assert not chunk_tab._chunk_apply_button.isEnabled()
    assert not chunk_tab._chunk_revert_button.isEnabled()


def test_two_continuous_strokes_of_one_entry_merge(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0, 1)
    _chunk_stroke(chunk_tab, 1, 2)
    assert chunk_tab._undo_stack.count() == 1
    assert chunk_tab._undo_stack.command(0).cells == (0, 1, 2)
    chunk_tab._undo_stack.undo()
    assert chunk_tab.chunk_plane_entries() == TEMPLATE_PLANE


def test_a_chunk_stroke_never_merges_into_a_map_paint(chunk_tab):
    """One stack, two merge classes: the ids must differ."""
    assert ChunkCellCommand(chunk_tab, "chunk:x", (), {}, {}).id() != 0x4D50
    assert AuthoredPlaceCommand(chunk_tab, 0, 0, (), {}, {}).id() != 0x4D50
    assert (
        ChunkCellCommand(chunk_tab, "chunk:x", (), {}, {}).id()
        != AuthoredPlaceCommand(chunk_tab, 0, 0, (), {}, {}).id()
    )


# --- 3. the vocabulary palette and the eyedropper ----------------------------


def test_the_vocabulary_palette_offers_every_permitted_entry(chunk_tab):
    _open_new_chunk(chunk_tab)
    assert chunk_tab._chunk_palette.count() == len(VOCAB)
    offered = [
        chunk_tab._chunk_palette.item(row).data(mbt._ENTRY_ROLE)
        for row in range(chunk_tab._chunk_palette.count())
    ]
    assert offered == list(VOCAB)
    # A row names the entry in the SDK's own words and carries its swatch.
    item = chunk_tab._chunk_palette.item(0)
    assert item.data(mbt._ENTRY_ROLE) == VOCAB[0]
    assert "tile" in item.toolTip()
    assert not item.icon().isNull()


def test_selecting_a_swatch_sets_the_brush_and_paints_nothing(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[2])
    assert chunk_tab._chunk_brush == VOCAB[2]
    assert chunk_tab.chunk_plane_entries() == TEMPLATE_PLANE
    assert chunk_tab._undo_stack.count() == 0


def test_the_eyedropper_takes_a_plane_cells_entry_as_the_brush(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[2])
    chunk_tab.paint_chunk_cell(7)
    _select_entry(chunk_tab, VOCAB[1])

    chunk_tab.set_chunk_tool(mbt._TOOL_PICK)
    chunk_tab.pick_entry_from_chunk_cell(7)

    assert chunk_tab._chunk_brush == VOCAB[2]
    assert chunk_tab.chunk_plane_entries()[7] == VOCAB[2], "picking edits nothing"
    # ...and Alt-click takes the same path through the overlay's callback.
    chunk_tab.set_chunk_tool(mbt._TOOL_PAINT)
    chunk_tab._on_chunk_cell_clicked(8, True)
    assert chunk_tab._chunk_brush == VOCAB[0]
    assert chunk_tab._chunk_pick_tool.isChecked() is False


# --- 4. apply, revert and the hand-off to the map ----------------------------


def test_apply_chunk_writes_the_chunk_to_the_project(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0, 1)
    assert chunk_tab.unsaved_edit_count() == 1

    assert chunk_tab.apply_chunk() is True

    assert chunk_tab.project.writes == [("chunk", CHUNK_IDENTITY)]
    document = chunk_tab.project.chunks[CHUNK_IDENTITY]
    assert document.template == f"map:{MAP:04d}/layer:{SLOT}/chunk:2"
    assert [(e.row, e.column, e.prior, e.entry) for e in document.entries] == [
        (0, 0, VOCAB[0], VOCAB[1]),
        (0, 1, VOCAB[0], VOCAB[1]),
    ]
    # Applied: the staged document is gone, the plane is the new floor, and the
    # chunk is still reversible through the history.
    assert chunk_tab._staged_chunks == {}
    assert not chunk_tab.chunk_is_dirty()
    assert chunk_tab.unsaved_edit_count() == 0
    assert chunk_tab._undo_stack.count() == 1
    assert "Wrote Authored: qa-chunk" in chunk_tab.status_text()


def test_apply_chunk_refuses_a_plane_identical_to_the_template(chunk_tab, monkeypatch):
    warnings: list[str] = []
    monkeypatch.setattr(
        mbt.QMessageBox, "warning", lambda *args: warnings.append(args[-1])
    )
    _open_new_chunk(chunk_tab)
    assert chunk_tab.apply_chunk() is False
    assert warnings and "does not differ from its template" in warnings[-1]
    assert chunk_tab.project.writes == []


def test_revert_returns_the_plane_to_the_applied_state_and_is_undoable(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.apply_chunk()
    _select_entry(chunk_tab, VOCAB[2])
    _chunk_stroke(chunk_tab, 1)
    assert chunk_tab.chunk_is_dirty()

    assert chunk_tab.revert_chunk_edits() is True

    assert chunk_tab.chunk_plane_entries()[1] == VOCAB[0]
    assert chunk_tab.chunk_plane_entries()[0] == VOCAB[1], "the applied cell survives"
    assert not chunk_tab.chunk_is_dirty()
    assert "Revert" in chunk_tab._undo_stack.undoText()
    chunk_tab._undo_stack.undo()
    assert chunk_tab.chunk_plane_entries()[1] == VOCAB[2]


def test_use_as_brush_returns_to_the_map_with_the_authored_chunk(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)

    assert chunk_tab.use_chunk_as_brush() is True

    assert not chunk_tab.chunk_is_open()
    assert chunk_tab._centre_stack.currentWidget() is chunk_tab._centre_split
    assert chunk_tab._brush_authored == CHUNK_IDENTITY
    assert chunk_tab._brush_pointer is None and chunk_tab._brush_ordinal is None
    assert "Authored: qa-chunk" in chunk_tab._brush_label()
    # The chunk is placeable BEFORE it is written, because the apply writes it.
    assert chunk_tab.placeable_authored(MAP) == (CHUNK_IDENTITY,)
    assert chunk_tab.placeable_authored(MAP + 1) == (), "a chunk is map-scoped"


def test_the_palette_offers_an_authored_chunk_beside_the_retail_ones(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.use_chunk_as_brush()

    rows = [
        chunk_tab._chooser.item(row).data(mbt._AUTHORED_ROLE)
        for row in range(chunk_tab._chooser.count())
    ]
    assert rows == [None] * len(CHUNKS) + [CHUNK_IDENTITY]
    authored_row = chunk_tab._chooser.item(len(CHUNKS))
    assert "Authored" in authored_row.text() and "qa-chunk" in authored_row.text()
    assert chunk_tab._chooser.currentRow() == len(CHUNKS), "the selection follows the brush"


# --- 5. painting a map cell with an authored chunk ---------------------------


def test_an_authored_brush_stages_a_placement_instead_of_a_pointer_paint(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.use_chunk_as_brush()

    _paint_cells(chunk_tab, 1)

    assert chunk_tab._authored_cells == {(MAP, SLOT, 1): CHUNK_IDENTITY}
    assert chunk_tab.editor.edits_for(MAP) == (), "set_cell was never called"
    assert chunk_tab.unsaved_edit_count() == 2, "one chunk + one placement"
    assert chunk_tab._grid_item._edited == frozenset({1})
    # The chunk stroke is the first entry; the placement is the second.
    command = chunk_tab._undo_stack.command(chunk_tab._undo_stack.count() - 1)
    assert isinstance(command, AuthoredPlaceCommand)
    assert command.previous == {1: None}
    assert command.applied == {1: CHUNK_IDENTITY}
    assert chunk_tab._undo_stack.undoText().startswith("Place 1 cell")

    chunk_tab._undo_stack.undo()
    assert chunk_tab._authored_cells == {}
    chunk_tab._undo_stack.redo()
    assert chunk_tab._authored_cells == {(MAP, SLOT, 1): CHUNK_IDENTITY}


def test_a_no_op_authored_placement_creates_no_history(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.use_chunk_as_brush()
    _paint_cells(chunk_tab, 2)
    history = chunk_tab._undo_stack.count()

    _paint_cells(chunk_tab, 2)

    assert chunk_tab._undo_stack.count() == history
    assert chunk_tab.unsaved_edit_count() == 2


def test_an_authored_brush_paints_the_preview_through_a_plane_substitution(chunk_tab, monkeypatch):
    """The preview must carry the authored plane, not a pointer the cell cannot hold."""
    seen: list[dict] = []
    monkeypatch.setattr(
        mbt.mv,
        "render_map",
        lambda rom, index, **kwargs: seen.append(kwargs.get("chunk_overrides"))
        or chunk_tab._current,
    )
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.use_chunk_as_brush()

    _paint_cells(chunk_tab, 1)
    chunk_tab._refresh_preview()

    assert seen, "the preview was re-rendered"
    overrides = seen[-1]
    substitution = overrides[(SLOT, 1)]
    assert isinstance(substitution, mbt.mv.ChunkSubstitution)
    assert substitution.entries == chunk_tab._resolved_plane(CHUNK_IDENTITY)
    assert substitution.entries[0] == VOCAB[1], "the authored body reaches the preview"


def test_apply_to_project_writes_the_chunk_before_the_placement(chunk_tab):
    """The order is load-bearing: a cell may not name an undeclared chunk."""
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.use_chunk_as_brush()
    _paint_cells(chunk_tab, 3)

    assert chunk_tab.apply_to_project() is True

    assert chunk_tab.project.writes == [
        ("chunk", CHUNK_IDENTITY),
        ("placement", {(MAP, SLOT, 3): CHUNK_IDENTITY}),
    ]
    # Re-read back: the project now holds the placement, so the staged set is clean.
    assert chunk_tab._authored_committed == {(MAP, SLOT, 3): CHUNK_IDENTITY}
    assert chunk_tab._authored_cells == {}
    assert chunk_tab.unsaved_edit_count() == 0
    assert "authored chunk(s)" in chunk_tab.status_text()
    assert "authored placement(s)" in chunk_tab.status_text()


def test_the_eyedropper_reads_back_an_authored_placement(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.use_chunk_as_brush()
    _paint_cells(chunk_tab, 3)
    _choose(chunk_tab, 0)  # brush back to a retail chunk
    assert chunk_tab._brush_authored is None

    chunk_tab._set_tool(mbt._TOOL_PICK)
    chunk_tab._on_cell_clicked(3)

    assert chunk_tab._brush_authored == CHUNK_IDENTITY
    assert "Authored: qa-chunk" in chunk_tab._chunk_label.text()
    assert chunk_tab.editor.edits_for(MAP) == ()


# --- 6. CQA-05: which event clears what --------------------------------------


def test_a_session_change_clears_every_staged_authored_fact(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.use_chunk_as_brush()
    _paint_cells(chunk_tab, 1)
    assert chunk_tab._authored_cells and chunk_tab._staged_chunks

    chunk_tab.on_session_changed()

    assert chunk_tab._authored_cells == {}
    assert chunk_tab._staged_chunks == {}
    assert chunk_tab._resolved_planes == {}
    assert chunk_tab._project_chunks == {}
    assert chunk_tab._authored_committed == {}
    assert chunk_tab._brush_authored is None
    assert chunk_tab._chunk_identity is None
    assert not chunk_tab.chunk_is_open()
    assert chunk_tab._undo_stack.count() == 0
    assert chunk_tab.unsaved_edit_count() == 0
    assert chunk_tab._centre_stack.currentWidget() is chunk_tab._centre_split


# --- project currency (WORKBENCH-MUTATION-CURRENCY-001) ----------------------
#
# `Session.project_revision` is the one authority for "is validation/build still
# about this project": `validation_current` is `validation_revision ==
# project_revision`, and `app._refresh_action_state` gates the Build action on
# `validation_current`. The Inspector, Graphics and Warps applies all advance it
# through `Session.project_mutated()`; the Map Browser's own writes did not, so a
# layout apply left the status bar reading "validation current" and Build enabled
# over a project that was never validated in that state. These tests pin the
# contract for both of the tab's project writes, and its absence for a no-op.


def _arm_currency(session) -> int:
    """A session that has validated and built, so staleness is observable."""
    session.record_validation(True)
    session.last_build = object()
    session.build_revision = session.project_revision
    assert session.validation_current
    assert session.build_current
    return session.project_revision


def _assert_invalidated(session, before: int) -> None:
    """One real mutation: exactly one revision, validation and build stale."""
    assert session.project_revision == before + 1
    assert not session.validation_current
    assert not session.build_current
    assert session.last_build is None


def test_layout_apply_advances_revision_and_invalidates(chunk_tab):
    """A real `apply_to_project` write invalidates validation and build."""
    session = chunk_tab._session
    emitted: list[int] = []
    chunk_tab.projectChanged.connect(lambda: emitted.append(1))

    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    before = _arm_currency(session)

    assert chunk_tab.apply_to_project() is True

    _assert_invalidated(session, before)
    assert emitted, "a real write still notifies every peer"


def test_chunk_write_advances_revision_and_invalidates(chunk_tab):
    """The chunk editor's own write owes the same contract as a layout apply."""
    session = chunk_tab._session

    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    before = _arm_currency(session)

    assert chunk_tab.apply_chunk() is True

    _assert_invalidated(session, before)


def test_a_no_op_apply_leaves_validation_and_build_current(chunk_tab, monkeypatch):
    """Nothing moved, so no revision: currency survives a no-op.

    Every SDK writer reports whether project source actually changed, and each
    already has its own idempotence test. This pins the currency half: when they
    all report no change, `changed` is False and the revision must not move.
    """
    session = chunk_tab._session

    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    # The SDK's own answers: this project already holds exactly this content.
    monkeypatch.setattr(mbt, "set_authored_chunk", lambda *a, **k: False)
    monkeypatch.setattr(mbt, "set_layout_cells", lambda *a, **k: False)
    monkeypatch.setattr(mbt, "set_layout_authored_cells", lambda *a, **k: False)

    before = _arm_currency(session)
    assert chunk_tab.apply_to_project() is False

    assert session.project_revision == before
    assert session.validation_current
    assert session.build_current
    assert session.last_build is not None


def test_a_no_op_chunk_write_leaves_validation_and_build_current(chunk_tab, monkeypatch):
    """A chunk the project already holds exactly is not a mutation."""
    session = chunk_tab._session

    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    monkeypatch.setattr(mbt, "set_authored_chunk", lambda *a, **k: False)

    before = _arm_currency(session)
    assert chunk_tab.apply_chunk() is False

    assert session.project_revision == before
    assert session.validation_current
    assert session.build_current
    assert session.last_build is not None


def test_a_real_write_preserves_unrelated_staged_work(chunk_tab):
    """Currency advances; the surrounding authoring session is not collateral.

    The write re-reads the project, which is what makes the applied chunk clean.
    Everything the author staged that this write did not land has to survive it:
    advancing the revision must not quietly reset the surface or drop the history
    the author built.
    """
    session = chunk_tab._session

    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    # The chunk's own plane edit is still open and still undoable.
    plane = chunk_tab.chunk_plane_entries()
    history = chunk_tab._undo_stack.count()
    assert history > 0, "the plane edit is on the history"
    assert chunk_tab._staged_chunks.get(CHUNK_IDENTITY) is not None

    before = _arm_currency(session)
    assert chunk_tab.apply_chunk() is True

    _assert_invalidated(session, before)
    # The write committed the chunk and left the author's session coherent: the
    # plane, the open editor and its history are exactly what they were.
    assert chunk_tab.chunk_plane_entries() == plane
    assert chunk_tab.chunk_is_open()
    assert chunk_tab._chunk_identity == CHUNK_IDENTITY
    assert chunk_tab._undo_stack.count() == history, "the history was not discarded"


def test_a_real_write_disables_build_through_the_shells_own_gate(chunk_tab):
    """The consequence the ticket exists for: Build is disabled until Validate.

    The shell's chain is `MapsEditor.projectChanged` -> `MainWindow`
    `_on_project_changed` -> `_refresh_action_state`, which hands each action the
    session's own predicate. This pins the two halves that make the disable
    real - the wiring, and the predicate's value after a write - without
    constructing the window inside a tab's unit test.
    """
    app_source = (
        Path(mbt.__file__).resolve().parent / "app.py"
    ).read_text(encoding="utf-8")
    assert "self._maps.projectChanged.connect(self._on_project_changed)" in app_source
    assert "self._refresh_action_state()" in app_source
    # The gate the shell evaluates, read straight off the source.
    assert "self._action_build.setEnabled(self._session.validation_current)" in app_source

    session = chunk_tab._session
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    before = _arm_currency(session)
    assert session.validation_current, "a validated project can build"

    assert chunk_tab.apply_to_project() is True

    _assert_invalidated(session, before)
    # What `_action_build.setEnabled(...)` now receives.
    assert not session.validation_current


def test_a_project_mutation_keeps_every_staged_authored_fact(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.use_chunk_as_brush()
    _paint_cells(chunk_tab, 1)
    plane = chunk_tab.chunk_plane_entries()
    staged_documents = dict(chunk_tab._staged_chunks)
    placements = dict(chunk_tab._authored_cells)
    history = chunk_tab._undo_stack.count()
    unsaved = chunk_tab.unsaved_edit_count()

    chunk_tab.on_project_mutated()

    assert chunk_tab._authored_cells == placements
    assert chunk_tab._staged_chunks == staged_documents
    assert chunk_tab.chunk_plane_entries() == plane
    assert chunk_tab._chunk_identity == CHUNK_IDENTITY
    assert chunk_tab._brush_authored == CHUNK_IDENTITY
    assert chunk_tab._undo_stack.count() == history
    assert chunk_tab.unsaved_edit_count() == unsaved


def test_a_project_mutation_re_reads_the_committed_placements(chunk_tab):
    """The other half of CQA-05: project-derived facts ARE refreshed."""
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.use_chunk_as_brush()
    _paint_cells(chunk_tab, 2)
    chunk_tab.apply_to_project()
    assert chunk_tab._authored_committed == {(MAP, SLOT, 2): CHUNK_IDENTITY}

    # A placement written elsewhere (another tab, or an undo that rewrote the
    # project) must be picked up by the next mutation - without dropping the
    # session's own view of the chunk.
    chunk_tab.project.layout[(MAP, SLOT, 0)] = CHUNK_IDENTITY

    chunk_tab.on_project_mutated()

    assert set(chunk_tab._authored_committed) == {(MAP, SLOT, 2), (MAP, SLOT, 0)}
    assert CHUNK_IDENTITY in chunk_tab._project_chunks


def test_reset_discards_staged_authored_work(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.use_chunk_as_brush()
    _paint_cells(chunk_tab, 1)

    chunk_tab._reset_edits()

    assert chunk_tab._authored_cells == {}
    assert chunk_tab._staged_chunks == {}
    assert not chunk_tab.chunk_is_open()
    assert chunk_tab._undo_stack.count() == 0
    assert chunk_tab.unsaved_edit_count() == 0


# --- 7. CQA-06: an SDK refusal is a message, never a crash -------------------


def test_a_chunk_authoring_error_on_create_is_a_warning_not_a_crash(
    chunk_tab, author_state, monkeypatch
):
    warnings: list[str] = []
    monkeypatch.setattr(
        mbt.QMessageBox, "warning", lambda *args: warnings.append(args[-1])
    )
    author_state["plane_error"] = ChunkAuthoringError(
        "template map:0000/layer:0/chunk:9 names chunk 9, but this layer uses only 4"
    )
    _choose(chunk_tab, 1)

    chunk_tab.create_chunk()  # must not raise

    assert warnings == [
        "template map:0000/layer:0/chunk:9 names chunk 9, but this layer uses only 4"
    ]
    assert not chunk_tab.chunk_is_open()


def test_a_chunk_authoring_error_on_a_plane_edit_is_a_warning_not_a_crash(
    chunk_tab, author_state, monkeypatch
):
    warnings: list[str] = []
    monkeypatch.setattr(
        mbt.QMessageBox, "warning", lambda *args: warnings.append(args[-1])
    )
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    author_state["create_error"] = ChunkAuthoringError(
        "screen entry 0x0009 is not part of this layer's graphics vocabulary"
    )

    chunk_tab.paint_chunk_cell(0)  # must not raise

    assert warnings == [
        "screen entry 0x0009 is not part of this layer's graphics vocabulary"
    ]
    # The refusal is reported ONCE per identity, not once per repaint, and the
    # stroke the author made is still on screen rather than silently dropped.
    chunk_tab.paint_chunk_cell(1)
    assert len(warnings) == 1
    assert chunk_tab.chunk_plane_entries()[0] == VOCAB[1]
    assert chunk_tab.unsaved_edit_count() == 0, (
        "a chunk that cannot be composed is not a project-pending document"
    )


def test_a_chunk_authoring_error_on_apply_is_a_warning_not_a_crash(
    chunk_tab, monkeypatch
):
    warnings: list[str] = []
    monkeypatch.setattr(
        mbt.QMessageBox, "warning", lambda *args: warnings.append(args[-1])
    )
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    monkeypatch.setattr(
        mbt,
        "set_authored_chunk",
        lambda *a, **k: (_ for _ in ()).throw(
            ChunkAuthoringError("authored chunk chunk:qa-chunk is not a dominant chunk")
        ),
    )

    assert chunk_tab.apply_chunk() is False  # must not raise

    assert warnings == [
        "authored chunk chunk:qa-chunk is not a dominant chunk"
    ]
    assert chunk_tab._staged_chunks, "a refused write leaves the work staged"


def test_a_chunk_authoring_error_on_the_vocabulary_is_a_warning_not_a_crash(
    chunk_tab, author_state, monkeypatch
):
    warnings: list[str] = []
    monkeypatch.setattr(
        mbt.QMessageBox, "warning", lambda *args: warnings.append(args[-1])
    )
    author_state["vocabulary_error"] = ChunkAuthoringError(
        "map:0000 BG0 could not be read: not a dominant chunk grid"
    )

    chunk_tab.create_chunk()  # must not raise

    assert warnings and "not a dominant chunk grid" in warnings[-1]
    # Read before the editor opens, so an unusable layer never opens an editor
    # with an empty palette.
    assert not chunk_tab.chunk_is_open()


def test_a_self_constructed_command_shaped_badly_is_never_reached(chunk_tab):
    """The overlay only ever reports cells inside its own plane."""
    _open_new_chunk(chunk_tab)
    assert chunk_tab._chunk_overlay.contains(1023)
    assert not chunk_tab._chunk_overlay.contains(1024)
    assert not chunk_tab._chunk_overlay.contains(-1)
    assert chunk_tab._chunk_overlay.cell_at(0, 0) == 0
    assert chunk_tab._chunk_overlay.cell_at(255, 255) == 1023
    assert chunk_tab._chunk_overlay.cell_at(256, 0) is None
    assert chunk_tab._chunk_overlay.cell_rect(33) == (8, 8, 8, 8)


# --- 8. CQA-07: no project or template work per cell -------------------------


def test_a_frame_of_painting_does_no_project_or_template_work(chunk_tab, monkeypatch):
    """One drag costs one composed document and one project read of nothing.

    The counts are the point: a per-cell re-read of the project or a per-cell
    re-resolution of the chunk body would show up here as a number that grows with
    the number of cells painted.
    """
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    reads: list[int] = []
    monkeypatch.setattr(
        mbt, "read_layout_edits", lambda d: reads.append(1) or chunk_tab.project.read_layout(d)
    )
    composes: list[int] = []
    original_create = _FakeAuthor.create

    def counting_create(self, identity, template, entries):
        composes.append(1)
        return original_create(self, identity, template, entries)

    monkeypatch.setattr(_FakeAuthor, "create", counting_create)
    resolves: list[int] = []
    original_resolve = _FakeAuthor.resolve

    def counting_resolve(self, chunk):
        resolves.append(1)
        return original_resolve(self, chunk)

    monkeypatch.setattr(_FakeAuthor, "resolve", counting_resolve)

    _chunk_stroke(chunk_tab, 0, 1, 2, 3)

    assert reads == [], "a paint gesture reads no project document"
    assert len(resolves) <= 1, f"resolutions observed: {len(resolves)}"
    assert chunk_tab._undo_stack.count() == 1, "a drag is one history entry"
    assert len(chunk_tab._staged_chunks) == 1, "one composed document, not one per cell"
    assert chunk_tab.unsaved_edit_count() == 1


def test_the_resolved_plane_is_cached_per_identity(chunk_tab, monkeypatch):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    resolves: list[int] = []
    original = _FakeAuthor.resolve

    def counting(self, chunk):
        resolves.append(1)
        return original(self, chunk)

    monkeypatch.setattr(_FakeAuthor, "resolve", counting)

    first = chunk_tab._resolved_plane(CHUNK_IDENTITY)
    second = chunk_tab._resolved_plane(CHUNK_IDENTITY)

    assert first == second and first is not None
    assert len(resolves) == 1, "a cached plane is not re-resolved"


# --- 9. the chunk editor's page and its keys ---------------------------------


def test_the_chunk_editor_page_is_a_second_centre_page_not_a_new_tab(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    assert chunk_tab._chunk_page is not chunk_tab._centre_split
    assert chunk_tab._centre_stack.count() == 2
    assert chunk_tab._centre_stack.currentWidget() is chunk_tab._chunk_page

    chunk_tab.close_chunk_editor()

    assert not chunk_tab.chunk_is_open()
    assert chunk_tab._centre_stack.currentWidget() is chunk_tab._centre_split
    # Closing keeps the staged chunk: it is still unsaved work.
    assert chunk_tab._staged_chunks
    assert chunk_tab.unsaved_edit_count() == 1


def test_an_authored_chunk_can_be_reopened_and_revised(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.apply_chunk()
    chunk_tab.close_chunk_editor()

    assert chunk_tab.open_authored_chunk(CHUNK_IDENTITY) is True

    assert chunk_tab.chunk_plane_entries()[0] == VOCAB[1], "the applied body is shown"
    assert not chunk_tab.chunk_is_dirty()
    _select_entry(chunk_tab, VOCAB[3])
    _chunk_stroke(chunk_tab, 500)
    assert chunk_tab.chunk_is_dirty()
    chunk_tab.apply_chunk()
    document = chunk_tab.project.chunks[CHUNK_IDENTITY]
    assert [(e.row, e.column, e.entry) for e in document.entries] == [
        (0, 0, VOCAB[1]),
        (15, 20, VOCAB[3]),
    ]


def test_undo_after_closing_the_editor_reopens_the_chunk(chunk_tab):
    _open_new_chunk(chunk_tab)
    _select_entry(chunk_tab, VOCAB[1])
    _chunk_stroke(chunk_tab, 0)
    chunk_tab.close_chunk_editor()
    assert not chunk_tab.chunk_is_open()

    chunk_tab._undo_stack.undo()

    assert chunk_tab.chunk_is_open()
    assert chunk_tab._chunk_identity == CHUNK_IDENTITY
    assert chunk_tab.chunk_plane_entries() == TEMPLATE_PLANE


def test_the_chunk_canvas_keys_move_the_selection_and_leave_the_page(chunk_tab):
    _open_new_chunk(chunk_tab)
    right = QtWidgets.QKeyEvent if False else None  # placeholder, replaced below
    from PySide6.QtGui import QKeyEvent

    def key(code):
        return QKeyEvent(
            QtCore.QEvent.Type.KeyPress, code, QtCore.Qt.KeyboardModifier.NoModifier
        )

    assert chunk_tab._chunk_selected == 0
    assert chunk_tab._on_chunk_canvas_key(key(QtCore.Qt.Key.Key_Right))
    assert chunk_tab._chunk_selected == 1
    assert chunk_tab._on_chunk_canvas_key(key(QtCore.Qt.Key.Key_Down))
    assert chunk_tab._chunk_selected == 33
    assert chunk_tab.chunk_plane_entries() == TEMPLATE_PLANE, "keys do not paint"
    assert chunk_tab._on_chunk_canvas_key(key(QtCore.Qt.Key.Key_Escape))
    assert not chunk_tab.chunk_is_open()
