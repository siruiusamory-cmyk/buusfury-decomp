"""MAP-RESIZE-AND-LAYERS-001: the Workbench resize and layer-authoring surface.

Focused, offscreen, synthetic. The SDK half of this capability is pinned by its own
tests; what is pinned here is the WIRING the user touches - what the structure
section states, the resize form's preview and its refusals, one resize (and one
layer creation) as exactly one undo command, a project-authored grid being
selectable and paintable in the existing map editor, the staged-state rules CQA-05
closed, the typed error boundary CQA-06 closed, and the read counts CQA-07 closed -
all driven through the real `MapBrowserTab` against the same duck-typed session,
editor and map fixtures `test_workbench_map_browser` uses (imported, not copied, so
the two cannot drift).

Two doubles stand in for the ROM-coupled SDK work, and each mirrors its real
contract rather than a convenient shape:

* `_World` stands in for `tools.webfoot.map_resize` and the structural half of
  `tools.webfoot.map_paint`: `target`/`resize`/`authored_layer` return the
  PRODUCTION `StructureTarget`, `StructuralLayer`, `LayerResize` and
  `AuthoredLayer` values and refuse exactly what the SDK refuses - a shrink, a
  no-op, a grid outside the supported 1..8 per axis, an initialization chunk
  outside the layer's vocabulary, a slot the canonical image uses, a shared root;
* the same object stands in for the project store, recording the order and the
  count of every structural and layout write and serving the read side back, so
  "one gesture, one project write" and "the document is read once per mutation" are
  measured rather than assumed.

`resolve_layer_record` is doubled only because the real one allocates nothing but
does read the canonical record's grid bytes; the double reproduces the one thing
the surface reads from it - the extent change the build would write - from the
format layer's own viewport constants.
"""

from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QtCore = pytest.importorskip("PySide6.QtCore")

from tools.webfoot import map_view as mv  # noqa: E402
from tools.webfoot.formats.map_graphics import (  # noqa: E402
    CHUNK_PIXELS,
    VIEWPORT_PIXELS_X,
    VIEWPORT_PIXELS_Y,
    MapGraphicsError,
)
from tools.webfoot.map_chunk import ChunkAuthoringError  # noqa: E402
from tools.webfoot.map_layout_edit import MapLayoutEditError  # noqa: E402
from tools.webfoot.map_layout_write import MapLayoutWriteError  # noqa: E402
from tools.webfoot.map_paint import (  # noqa: E402
    MapPaintError,
    PaintCell,
    PaintChunk,
    PaintLayer,
)
from tools.webfoot.map_resize import (  # noqa: E402
    ChunkChoice,
    MapStructureError,
    StructuralLayer,
    StructureTarget,
    layer_identity,
)
from tools.webfoot.project import (  # noqa: E402
    AuthoredChunks,
    AuthoredLayer,
    LayerResize,
    LayoutEdits,
    MapStructure,
    ProjectError,
)
from tools.webfoot.write import WriteError  # noqa: E402
from tools.webfoot.workbench import map_browser_tab as mbt  # noqa: E402
from tools.webfoot.workbench.map_browser_tab import (  # noqa: E402
    MapBrowserTab,
    NewLayerCommand,
    ResizeCommand,
    StructuralPaintCommand,
)
from tools.webfoot.workbench.session import Session  # noqa: E402

from tests.unit.test_workbench_map_browser import (  # noqa: E402,F401
    CHUNKS,
    MAP,
    SLOT,
    _FakeEditor,
    _entry,
    _result,
    _target,
    qapp,
)

#: The synthetic map's own shape: BG0 is a 2x2 dominant grid whose four cells each
#: hold a distinct chunk (so every cell has a distinct earlier value to restore),
#: BG1/BG2 are the two special read-only forms, and BG3 is unused.
RETAIL = (2, 2)
EXTENT = (89, 89)
HANDLER = 0x08008087
BLOCK_HANDLER = 0x08007B63
TERRAIN_HANDLER = 0x080088BD
CELL_OFFSET = 0x00292CA0
AUTHORED = "layer:qa-bg3"

_ABSENT = "absent_placeholder"
_SPECIAL = {
    1: (
        "static_graphical_screenblock",
        "this slot is a single screen-entry plane reached by its own handler; it has "
        "no chunk grid to resize",
    ),
    2: (
        "static_graphical_terrain_field",
        "this slot is the terrain-field form Map 19 uses; its grid is a run of 8-bit "
        "ordinal containers, not a chunk window",
    ),
}


def _choices(cells) -> tuple[ChunkChoice, ...]:
    seen: list[int] = []
    for address in cells:
        if address and address not in seen:
            seen.append(address)
    return tuple(
        ChunkChoice(ordinal=index, address=address, cell_count=1)
        for index, address in enumerate(seen, start=1)
    )


def _resolve_fill(fill, vocabulary):
    """One initialization value to ``(address, authored identity)``, as the SDK does."""
    if isinstance(fill, str):
        return 0, fill
    for choice in vocabulary:
        if choice.ordinal == fill:
            return choice.address, None
    raise MapStructureError(
        f"chunk {fill} is not one of the {len(vocabulary)} chunks this layer uses"
    )


class _World:
    """A duck-typed structural SDK plus the project store behind it."""

    def __init__(self, **overrides) -> None:
        self.structure = MapStructure()
        self.layout: dict[tuple[int, int, int], int | str] = {}
        self.reads = 0
        self.resizer_builds = 0
        self.painter_builds = 0
        self.writes: list[tuple] = []
        self.fail_read: Exception | None = None
        self.fail_write: Exception | None = None
        self.fail_preview: Exception | None = None
        self.fail_target: Exception | None = None
        self.shared: tuple[int, ...] = ()
        self.retail = RETAIL
        self.extent = EXTENT
        for name, value in overrides.items():
            setattr(self, name, value)

    # -- the project's own document ------------------------------------------

    def read_structure(self, project_dir) -> MapStructure:
        self.reads += 1
        if self.fail_read is not None:
            raise self.fail_read
        return self.structure

    def read_chunks(self, project_dir) -> AuthoredChunks:
        # The chunk document's own reader sees only the project text, so it is never
        # what a structural read failure comes from; the structural document is.
        return AuthoredChunks()

    def read_layout(self, project_dir) -> LayoutEdits:
        # The layout document's own reader; a *structural* read failure is not this.
        maps: dict[str, dict[int, dict[int, int | str]]] = {}
        for (map_index, layer_slot, cell), value in self.layout.items():
            maps.setdefault(LayoutEdits.key_for(map_index), {}).setdefault(
                layer_slot, {}
            )[cell] = value
        return LayoutEdits(maps=maps)

    # -- the structural view --------------------------------------------------

    def canonical_layer(self, map_index: int, slot: int) -> StructuralLayer:
        if slot not in (0, 1, 2) and slot not in _SPECIAL:
            return StructuralLayer(
                slot=slot,
                address=0,
                handler=0,
                classification=_ABSENT,
                retail_columns=0,
                retail_rows=0,
                columns=0,
                rows=0,
                cells=(),
                vocabulary=(),
                read_only_reason=(
                    "the canonical image leaves this slot unused; author a layer to "
                    "activate it"
                ),
            )
        if slot in _SPECIAL:
            classification, reason = _SPECIAL[slot]
            return StructuralLayer(
                slot=slot,
                address=0x08292F00 + slot,
                handler=BLOCK_HANDLER if slot == 1 else TERRAIN_HANDLER,
                classification=classification,
                retail_columns=0,
                retail_rows=0,
                columns=0,
                rows=0,
                cells=(),
                vocabulary=(),
                read_only_reason=reason,
            )
        return StructuralLayer(
            slot=slot,
            address=0x08292B00,
            handler=HANDLER,
            classification="dominant",
            retail_columns=self.retail[0],
            retail_rows=self.retail[1],
            columns=self.retail[0],
            rows=self.retail[1],
            cells=CHUNKS[: self.retail[0] * self.retail[1]],
            vocabulary=_choices(CHUNKS[: self.retail[0] * self.retail[1]]),
        )

    def structural_layer(
        self, structure: MapStructure | None, map_index: int, slot: int
    ) -> StructuralLayer:
        structure = structure if structure is not None else MapStructure()
        authored = structure.layer_at(map_index, slot)
        if authored is not None:
            template_slot = int(authored.template.rsplit("BG", 1)[1])
            template = self.canonical_layer(map_index, template_slot)
            address, identity = _resolve_fill(authored.fill, template.vocabulary)
            count = authored.columns * authored.rows
            return StructuralLayer(
                slot=slot,
                address=0,
                handler=template.handler,
                classification="dominant",
                retail_columns=0,
                retail_rows=0,
                columns=authored.columns,
                rows=authored.rows,
                cells=tuple(address for _ in range(count)),
                vocabulary=template.vocabulary,
                identity=authored.identity,
                fill=authored.fill,
                authored_fill=identity,
                authored_cells=tuple(identity for _ in range(count)),
            )
        resize = structure.resize_for(map_index, slot)
        if resize is None:
            return self.canonical_layer(map_index, slot)
        base = self.canonical_layer(map_index, slot)
        if base.read_only_reason:
            raise MapStructureError(
                f"map:{map_index:04d} BG{slot}: {base.read_only_reason}"
            )
        cells: list[int] = []
        authored_cells: list[str | None] = []
        for index in range(resize.columns * resize.rows):
            if index < len(base.cells) and base.cells[index]:
                cells.append(base.cells[index])
                authored_cells.append(None)
                continue
            address, identity = _resolve_fill(resize.fill, base.vocabulary)
            cells.append(address)
            authored_cells.append(identity)
        return StructuralLayer(
            slot=slot,
            address=base.address,
            handler=base.handler,
            classification=base.classification,
            retail_columns=base.retail_columns,
            retail_rows=base.retail_rows,
            columns=resize.columns,
            rows=resize.rows,
            cells=tuple(cells),
            vocabulary=base.vocabulary,
            resized=True,
            fill=resize.fill,
            authored_fill=authored_cells[-1] if authored_cells else None,
            authored_cells=tuple(authored_cells),
        )

    def target(self, structure: MapStructure | None, map_index: int) -> StructureTarget:
        return StructureTarget(
            map_index=map_index,
            name="Synthetic Map",
            root_address=0x08292A00,
            extent_x=self.extent[0],
            extent_y=self.extent[1],
            slots=tuple(
                self.structural_layer(structure, map_index, slot) for slot in range(4)
            ),
            shared_with=self.shared,
        )

    # -- the structural authoring authority -----------------------------------

    def _grid_side(self, value, axis: str) -> int:
        if type(value) is not int:
            raise MapStructureError(f"a grid {axis} count must be a whole number")
        if not 1 <= value <= 8:
            raise MapStructureError(
                f"{axis} = {value} chunks is outside the supported 1..8"
            )
        return value

    def _check_fill(self, fill, vocabulary, label: str) -> None:
        if isinstance(fill, str):
            if not fill.startswith("chunk:"):
                raise MapStructureError(
                    f"{label}: initialization {fill!r} is neither a chunk ordinal nor "
                    "a 'chunk:<name>' authored chunk"
                )
            return
        if type(fill) is not int or fill < 1:
            raise MapStructureError(
                f"{label}: initialization must be a 1-based chunk ordinal or an "
                f"authored chunk identity, got {fill!r}"
            )
        if all(choice.ordinal != fill for choice in vocabulary):
            raise MapStructureError(
                f"{label}: chunk {fill} is not one of the {len(vocabulary)} chunks "
                "this layer uses"
            )

    def resize(self, map_index: int, layer_slot: int, columns, rows, fill) -> LayerResize:
        if self.fail_preview is not None:
            raise self.fail_preview
        if self.shared:
            raise MapStructureError(
                f"map:{map_index:04d}: this map's definition is shared with "
                f"map:{self.shared[0]:04d}; its layer slots and its extent are shared "
                "state"
            )
        layer = self.structural_layer(self.structure, map_index, layer_slot)
        if layer.read_only_reason:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot}: {layer.read_only_reason}"
            )
        columns = self._grid_side(columns, "columns")
        rows = self._grid_side(rows, "rows")
        current = (layer.columns, layer.rows)
        if columns < current[0] or rows < current[1]:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot} is {current[0]}x{current[1]}; "
                f"shrinking to {columns}x{rows} is not supported because the cells it "
                "would remove have not been shown to be unreferenced"
            )
        if (columns, rows) == current:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot} is already {columns}x{rows}; a "
                "resize must change the grid"
            )
        self._check_fill(fill, layer.vocabulary, f"map:{map_index:04d} BG{layer_slot}")
        return LayerResize(
            map_index=map_index,
            layer_slot=layer_slot,
            columns=columns,
            rows=rows,
            fill=fill,
        )

    def authored_layer(
        self, identity, map_index: int, layer_slot: int, template, columns, rows, fill
    ) -> AuthoredLayer:
        if self.fail_preview is not None:
            raise self.fail_preview
        identity = layer_identity(identity)
        layer = self.structural_layer(self.structure, map_index, layer_slot)
        if not layer.absent:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot} is {layer.classification}; an "
                "authored layer can only activate a slot the canonical image leaves "
                "unused, because the engine's layer count is fixed at 4"
            )
        if self.structure.layer_at(map_index, layer_slot) is not None:
            raise MapStructureError(
                f"map:{map_index:04d} BG{layer_slot} is already a project-authored layer"
            )
        if not isinstance(template, str) or not template.startswith(
            f"map:{map_index:04d}/BG"
        ):
            raise MapStructureError(
                f"template {template!r} names another map; an authored layer's "
                "screen-entry ordinals resolve through its own map's assembled "
                "character block"
            )
        template_slot = int(template.rsplit("BG", 1)[1])
        vocabulary = self.canonical_layer(map_index, template_slot).vocabulary
        if not vocabulary:
            raise MapStructureError(
                f"template {template!r} is not a supported dominant chunk grid"
            )
        columns = self._grid_side(columns, "columns")
        rows = self._grid_side(rows, "rows")
        self._check_fill(fill, vocabulary, f"map:{map_index:04d} BG{layer_slot}")
        return AuthoredLayer(
            identity=identity,
            map_index=map_index,
            layer_slot=layer_slot,
            template=template,
            columns=columns,
            rows=rows,
            fill=fill,
        )

    def vocabulary(self, map_index: int, layer_slot: int) -> tuple[ChunkChoice, ...]:
        return self.canonical_layer(map_index, layer_slot).vocabulary

    # -- the build's own resolution, as far as the surface reads it -----------

    def resolve_layer_record(self, image, edit, *, profile=None, **_kwargs):
        """The build's own extent resolution, as `resolve_layer_record` reports it.

        The stored word is the map's maximum camera scroll - `max(1, plane -
        viewport)`, exactly `map_graphics.declared_extent_raw` - and the surface
        states the declared extent the root publishes, which is that word plus one.
        """
        changes = []
        for axis, position, viewport in (
            ("x", 0, VIEWPORT_PIXELS_X),
            ("y", 1, VIEWPORT_PIXELS_Y),
        ):
            plane = (edit.columns if position == 0 else edit.rows) * CHUNK_PIXELS
            required = max(1, plane - viewport)
            if required > self.extent[position] - 1:
                changes.append((axis, 0, required))
        return SimpleNamespace(extent_changes=tuple(changes))

    # -- the paint authority --------------------------------------------------

    def paint_layer(
        self, structure: MapStructure | None, map_index: int, layer_slot: int
    ) -> PaintLayer:
        layer = self.structural_layer(structure, map_index, layer_slot)
        if not layer.columns or not layer.rows:
            raise MapPaintError(
                f"BG{layer_slot} of map:{map_index:04d} is not editable: "
                f"{layer.read_only_reason}"
            )
        # Only the canonical dominant slot has retail cells, and an authored layer
        # has none at all: every other cell exists solely in the record a build
        # materializes, so it carries no four-byte field (`offset == -1`).
        retail_cells = (
            self.retail[0] * self.retail[1]
            if layer_slot == SLOT and layer.identity is None
            else 0
        )
        cells = tuple(
            PaintCell(
                cell=index,
                column=index % layer.columns,
                row=index // layer.columns,
                pointer=layer.cells[index],
                offset=(
                    CELL_OFFSET + 4 * index if index < retail_cells else -1
                ),
            )
            for index in range(layer.cell_count)
        )
        vocabulary = tuple(
            PaintChunk(ordinal=choice.ordinal, pointer=choice.address, cell_count=1)
            for choice in layer.vocabulary
        )
        reason = (
            ""
            if len(vocabulary) >= 2
            else f"a grid of {layer.cell_count} cell(s) using a single chunk, so it "
            "has no other chunk to paint with"
        )
        return PaintLayer(
            slot=layer.slot,
            classification=layer.classification,
            handler=layer.handler,
            columns=layer.columns,
            rows=layer.rows,
            cells=cells,
            vocabulary=vocabulary,
            read_only_reason=reason,
            structural=layer.structural,
        )

    def pointer_edits(self, edits, structure=None) -> dict[tuple[int, int, int], int]:
        resolved = {}
        for (map_index, layer_slot, cell), ordinal in sorted(edits.items()):
            layer = self.paint_layer(structure, map_index, layer_slot)
            resolved[(map_index, layer_slot, cell)] = layer.vocabulary[
                ordinal - 1
            ].pointer
        return resolved

    def pointer_edits_with(self, structure, edits):
        return self.pointer_edits(edits, structure)

    # -- the project store ----------------------------------------------------

    def set_layer_resize(self, project_dir, image, resize, *, profile=None) -> bool:
        if self.fail_write is not None:
            raise self.fail_write
        if self.structure.resize_for(resize.map_index, resize.layer_slot) == resize:
            return False
        self.writes.append(("resize", resize.key, resize.fill))
        resizes = dict(self.structure.resizes)
        resizes[resize.key] = resize
        self.structure = MapStructure(
            resizes=resizes, layers=dict(self.structure.layers)
        )
        return True

    def clear_layer_resize(
        self, project_dir, image, map_index, layer_slot, *, profile=None
    ) -> bool:
        if self.fail_write is not None:
            raise self.fail_write
        key = LayerResize.key_for(map_index, layer_slot)
        if key not in self.structure.resizes:
            return False
        self.writes.append(("clear-resize", key))
        resizes = dict(self.structure.resizes)
        del resizes[key]
        self.structure = MapStructure(
            resizes=resizes, layers=dict(self.structure.layers)
        )
        return True

    def set_authored_layer(self, project_dir, image, layer, *, profile=None) -> bool:
        if self.fail_write is not None:
            raise self.fail_write
        if self.structure.layers.get(layer.identity) == layer:
            return False
        self.writes.append(("layer", layer.identity, layer.fill))
        layers = dict(self.structure.layers)
        layers[layer.identity] = layer
        self.structure = MapStructure(
            resizes=dict(self.structure.resizes), layers=layers
        )
        return True

    def remove_authored_layer(self, project_dir, identity) -> bool:
        if self.fail_write is not None:
            raise self.fail_write
        if identity not in self.structure.layers:
            return False
        self.writes.append(("remove-layer", identity))
        layers = dict(self.structure.layers)
        del layers[identity]
        self.structure = MapStructure(
            resizes=dict(self.structure.resizes), layers=layers
        )
        return True

    def set_layout_cells(self, project_dir, profile, image, edits) -> bool:
        if self.fail_write is not None:
            raise self.fail_write
        changed = False
        for key, value in sorted(edits.items()):
            if value is None:
                if self.layout.pop(key, None) is not None:
                    changed = True
                continue
            if self.layout.get(key) != value:
                self.layout[key] = value
                changed = True
        if changed:
            self.writes.append(("layout", len(edits)))
        return changed

    # -- the surface's own constructors ---------------------------------------

    def resizer(self, image, *, structure=None, profile=None):
        self.resizer_builds += 1
        return _View(self, structure)

    def painter(self, image, *, structure=None, profile=None):
        self.painter_builds += 1
        return _View(self, structure)


class _View:
    """One `MapResizer`/`MapPainter` over the document the tab handed it."""

    def __init__(self, world: _World, structure) -> None:
        self._world = world
        self._structure = structure

    # MapResizer
    def target(self, map_index: int) -> StructureTarget:
        if self._world.fail_target is not None:
            raise self._world.fail_target
        return self._world.target(self._structure, map_index)

    def resize(self, map_index, layer_slot, columns, rows, fill):
        return self._world.resize(map_index, layer_slot, columns, rows, fill)

    def authored_layer(
        self, identity, map_index, layer_slot, template, columns, rows, fill
    ):
        return self._world.authored_layer(
            identity, map_index, layer_slot, template, columns, rows, fill
        )

    def vocabulary(self, map_index: int, layer_slot: int) -> tuple[ChunkChoice, ...]:
        return self._world.vocabulary(map_index, layer_slot)

    # MapPainter
    def layer(self, map_index: int, layer_slot: int) -> PaintLayer:
        return self._world.paint_layer(self._structure, map_index, layer_slot)

    def pointer_edits(self, edits):
        return self._world.pointer_edits_with(self._structure, edits)


def _bind(tab, world: _World, fake_editor) -> None:
    tab.world = world
    tab.editor = fake_editor


def _unreadable_chunk_author(image, **kwargs):
    """A `ChunkAuthor` for an image whose chunks cannot be read: it refuses."""
    raise ChunkAuthoringError("this synthetic image's chunks cannot be read")


@pytest.fixture
def tab(qapp, monkeypatch, tmp_path):
    """The real tab over an identified session, a fake SDK and a fake project."""
    world = _World()
    # `_View.pointer_edits` restores the committed document after resolving, so the
    # structural view the tab asked about is not mistaken for the project's own.
    world._committed_document = MapStructure()

    entries = (_entry(MAP, "Synthetic Map"),)
    base = _result(MAP)
    fake_editor = _FakeEditor(_target(), base)
    rom_path = tmp_path / "rom.gba"
    rom_path.write_bytes(b"synthetic")
    session = Session(
        rom_image=b"synthetic",
        rom_path=rom_path,
        project_dir=tmp_path / "project",
        identification=object(),
    )
    session.profile = SimpleNamespace(id="synthetic_profile")

    monkeypatch.setattr(mbt.mv, "read_map_index", lambda rom: entries)
    monkeypatch.setattr(mbt.mv, "render_map", lambda rom, index, **kwargs: _result(index))
    monkeypatch.setattr(
        mbt.mv,
        "render_chunk_images",
        lambda rom, index, addresses, **kwargs: tuple(
            mv.ChunkImage(
                address=address,
                width=CHUNK_PIXELS,
                height=CHUNK_PIXELS,
                pixels=bytes([7]) * (CHUNK_PIXELS * CHUNK_PIXELS),
            )
            for address in addresses
        ),
    )
    monkeypatch.setattr(
        mbt.mv,
        "render_chunk_entries",
        lambda char_data, plane, **kwargs: mv.ChunkImage(
            address=0,
            width=CHUNK_PIXELS,
            height=CHUNK_PIXELS,
            pixels=bytes([7]) * (CHUNK_PIXELS * CHUNK_PIXELS),
        ),
    )
    monkeypatch.setattr(mbt, "MapLayoutEditor", lambda rom_image: fake_editor)
    # The chunk author reads the same canonical image through the real profile; this
    # synthetic session has no real one, so it is doubled with the contract of an
    # image whose chunks cannot be read - the state a surface has to survive.
    monkeypatch.setattr(mbt, "ChunkAuthor", _unreadable_chunk_author)
    monkeypatch.setattr(mbt, "MapResizer", world.resizer)
    monkeypatch.setattr(mbt, "MapPainter", world.painter)
    monkeypatch.setattr(mbt, "read_map_structure", world.read_structure)
    monkeypatch.setattr(mbt, "read_authored_chunks", world.read_chunks)
    monkeypatch.setattr(mbt, "read_layout_edits", world.read_layout)
    monkeypatch.setattr(mbt, "set_layer_resize", world.set_layer_resize)
    monkeypatch.setattr(mbt, "clear_layer_resize", world.clear_layer_resize)
    monkeypatch.setattr(mbt, "set_authored_layer", world.set_authored_layer)
    monkeypatch.setattr(mbt, "remove_authored_layer", world.remove_authored_layer)
    monkeypatch.setattr(mbt, "set_layout_cells", world.set_layout_cells)
    monkeypatch.setattr(mbt, "resolve_layer_record", world.resolve_layer_record)

    value = MapBrowserTab(session)
    value.on_session_changed()
    value._list.setCurrentRow(0)
    value._edit_toggle.setChecked(True)
    _bind(value, world, fake_editor)
    return value


def _warnings(monkeypatch) -> list[str]:
    """Capture `QMessageBox.warning` the way a user would see it."""
    seen: list[str] = []
    monkeypatch.setattr(
        mbt.QMessageBox, "warning", lambda *args: seen.append(str(args[-1]))
    )
    return seen


def _stroke(tab, *cells: int) -> None:
    """One press-drag-release over the map grid, as the overlay delivers it."""
    tab.begin_paint_stroke()
    for cell in cells:
        tab.paint_cell(cell)
    tab.end_paint_stroke()


# --- 1. what the surface states ----------------------------------------------


def test_the_structure_section_states_the_layer_the_extent_and_the_support(tab):
    assert tab._structure_state.text().startswith("BG0 \u00b7 chunk grid 2\u00d72")
    assert "source image grid" in tab._structure_state.text()
    assert tab._structure_extent.text() == "map extent 89 \u00d7 89 px \u00b7 1 unused slot(s)"
    assert tab._structure_support.text().startswith("Supported \u00b7")
    assert tab._structure_staged.text() == "no staged structural change on this map"
    assert tab._resize_button.isEnabled()
    assert tab._new_layer_button.isEnabled()
    assert not tab._revert_structure_button.isEnabled()


def test_the_layer_list_names_canonical_and_project_layers_with_their_reason(tab):
    rows = [
        tab._structure_list.item(row).text()
        for row in range(tab._structure_list.count())
    ]
    assert rows[0] == "BG0 \u00b7 2\u00d72 \u00b7 dominant \u00b7 source image"
    assert rows[1].endswith("static_graphical_screenblock \u00b7 source image")
    assert rows[2].endswith("static_graphical_terrain_field \u00b7 source image")
    assert rows[3] == f"BG3 \u00b7 no grid \u00b7 {_ABSENT} \u00b7 source image"
    # The read-only rows carry the SDK's own refusal, not a blank.
    assert "screen-entry plane" in tab._structure_list.item(1).toolTip()
    assert "terrain-field form" in tab._structure_list.item(2).toolTip()
    # Selectable rows are the paintable ones, and the list shows the current one.
    assert tab._structure_list.item(1).foreground().color().name() != "#000000"
    assert tab._structure_list.currentRow() == 0


def test_selecting_a_read_only_slot_row_says_why_it_cannot_be_edited(tab):
    tab._on_structure_row_selected(2)
    assert "terrain-field" in tab.status_text()
    # The layer combo did not move: slot 2 is not an editable layer.
    assert tab._slot.slot == SLOT


# --- 2. the resize preview and its refusals ----------------------------------


def test_the_resize_preview_states_the_grid_the_new_cells_and_the_extent(tab):
    preview = tab.preview_resize(3, 2, 2)
    assert preview.edit.columns == 3 and preview.edit.rows == 2
    assert preview.edit.fill == 2
    assert "BG0 2\u00d72 \u2192 3\u00d72" in preview.summary
    assert "cells 5-6 initialize to Chunk 2" in preview.summary
    # 3 * 256 = 768 px of plane, less the engine's own viewport, and never lowered.
    # The surface states the DECLARED extent (`extent - 1` stored, + 1 read back),
    # which is the value `StructureTarget.extent_x` publishes and the section shows.
    assert (
        f"map extent x 89 \u2192 {3 * CHUNK_PIXELS - VIEWPORT_PIXELS_X + 1} px"
        in preview.summary
    )
    assert preview.extent[0] == 3 * CHUNK_PIXELS - VIEWPORT_PIXELS_X + 1
    # The rows did not grow, but 2 rows of 256 px is already wider than this
    # synthetic map's declared y reach, so both axes are raised - and only the axes
    # that actually change are stated.
    assert preview.extent[1] == 2 * CHUNK_PIXELS - VIEWPORT_PIXELS_Y + 1
    assert (
        f"map extent y 89 \u2192 {preview.extent[1]} px" in preview.summary
    )


@pytest.mark.parametrize(
    "columns, rows, fill, expected",
    (
        (1, 2, 1, "shrinking to 1x2 is not supported"),
        (3, 1, 1, "shrinking to 3x1 is not supported"),
        (1, 1, 1, "shrinking to 1x1 is not supported"),
        (2, 2, 1, "already 2x2; a resize must change the grid"),
        (9, 2, 1, "columns = 9 chunks is outside the supported 1..8"),
        (3, 9, 1, "rows = 9 chunks is outside the supported 1..8"),
        (3, 2, 99, "chunk 99 is not one of the 4 chunks this layer uses"),
        (3, 2, 0, "initialization must be a 1-based chunk ordinal"),
    ),
)
def test_a_refused_resize_is_the_sdks_own_reason_before_anything_is_staged(
    tab, monkeypatch, columns, rows, fill, expected
):
    seen = _warnings(monkeypatch)
    assert tab.apply_resize(columns, rows, fill) is False
    assert len(seen) == 1 and expected in seen[0]
    assert tab._staged_resizes == {}
    assert tab._undo_stack.count() == 0
    assert tab.unsaved_edit_count() == 0
    assert tab.world.writes == []


def test_an_unsupported_slot_is_refused_with_its_reason(tab, monkeypatch):
    seen = _warnings(monkeypatch)
    # Point the editor at the terrain-field slot the way the surface never does.
    tab._slot = tab._target.slots[2]
    assert tab.apply_resize(3, 2, 1) is False
    assert len(seen) == 1 and "terrain-field" in seen[0]
    assert tab._staged_resizes == {}


def test_a_shared_root_is_refused_with_its_reason(tab, monkeypatch):
    seen = _warnings(monkeypatch)
    tab.world.shared = (7,)
    tab._structure_targets = {}
    assert tab.apply_resize(3, 2, 1) is False
    assert len(seen) == 1 and "shared" in seen[0]
    assert tab._staged_resizes == {}


def test_the_resize_dialog_previews_live_and_refuses_a_shrink_visibly(tab):
    dialog = mbt.ResizeLayerDialog(
        tab,
        layer=tab.structure_target().layer(SLOT),
        extent=EXTENT,
        preview=tab.preview_resize,
        apply_command=tab.apply_resize,
        current=(2, 2),
    )
    # Opening on the current grid states the no-op rather than a refusal.
    assert "already 2\u00d72" in dialog.summary_text()
    assert dialog.edit() is None

    dialog._columns.setValue(3)
    dialog._rows.setValue(2)
    assert "2\u00d72 \u2192 3\u00d72" in dialog.summary_text()
    assert dialog.edit() is not None

    # A shrink is offered as a value a person can type and is refused with the
    # SDK's own reason, in the form, before anything is applied.
    dialog._columns.setValue(1)
    assert "Not supported" in dialog.summary_text()
    assert "shrinking to 1x2 is not supported" in dialog.summary_text()
    assert dialog.edit() is None

    dialog._columns.setValue(3)
    assert dialog.edit() is not None


def test_the_resize_form_offers_the_layers_own_chunks_as_initialization(tab):
    dialog = mbt.ResizeLayerDialog(
        tab,
        layer=tab.structure_target().layer(SLOT),
        extent=EXTENT,
        preview=tab.preview_resize,
        apply_command=tab.apply_resize,
        current=(2, 2),
    )
    labels = [dialog._fill.itemText(row) for row in range(dialog._fill.count())]
    assert labels == ["Chunk 1", "Chunk 2", "Chunk 3", "Chunk 4"]
    assert [dialog._fill.itemData(row) for row in range(dialog._fill.count())] == [
        1,
        2,
        3,
        4,
    ]


# --- 3. one resize is one undo command ---------------------------------------


def test_one_resize_is_one_undo_command_and_undo_and_redo_move_the_staged_grid(tab):
    assert tab.apply_resize(3, 2, 2) is True
    assert tab._undo_stack.count() == 1
    command = tab._undo_stack.command(0)
    assert isinstance(command, ResizeCommand)
    assert command.previous is None
    assert command.applied.columns == 3
    assert "Resize map:0000 BG0 to 3\u00d72" == command.text()
    assert tab.unsaved_edit_count() == 1
    assert set(tab._staged_resizes) == {(MAP, SLOT)}

    # The staged edit is what the surface now shows and what the preview draws.
    assert tab.structure_target().layer(SLOT).columns == 3
    assert tab._structure_state.text().startswith("BG0 \u00b7 chunk grid 3\u00d72")
    assert "BG0 \u2192 3\u00d72 (resize staged)" in tab._structure_staged.text()
    assert tab.world.writes == [], "staging writes nothing"

    tab._undo_stack.undo()
    assert tab._staged_resizes == {}
    assert tab.structure_target().layer(SLOT).columns == 2
    assert tab.unsaved_edit_count() == 0

    tab._undo_stack.redo()
    assert set(tab._staged_resizes) == {(MAP, SLOT)}
    assert tab.structure_target().layer(SLOT).columns == 3
    assert tab.unsaved_edit_count() == 1


def test_applying_a_staged_resize_writes_the_project_once_and_clears_the_stage(tab):
    assert tab.apply_resize(3, 2, 2) is True
    assert tab.apply_to_project() is True

    assert [entry[0] for entry in tab.world.writes] == ["resize"]
    key, fill = tab.world.writes[0][1], tab.world.writes[0][2]
    assert key == LayerResize.key_for(MAP, SLOT)
    assert fill == 2
    assert tab._staged_resizes == {}
    assert tab._undo_stack.count() == 0
    assert tab.unsaved_edit_count() == 0
    assert tab.world.structure.resize_for(MAP, SLOT).columns == 3
    # The surface now reads the project's own grid, not a staged one.
    assert tab.structure_target().layer(SLOT).resized is True
    assert "project resized grid" in tab._structure_state.text()
    assert tab._render_cache is not None


def test_revert_structure_unstages_a_resize_and_is_itself_undoable(tab):
    tab.apply_resize(3, 2, 2)
    assert tab.revert_selected_structure() is True
    # Un-staging returns the slot to what the project holds - nothing - so the staged
    # table is empty again rather than holding a "staged removal" of a resize the
    # project never had.
    assert tab._staged_resizes == {}
    assert tab.structure_target().layer(SLOT).columns == 2
    assert tab._undo_stack.count() == 2
    assert tab._undo_stack.command(1).text() == (
        "Revert map:0000 BG0 to the retail grid"
    )

    tab._undo_stack.undo()
    assert tab._staged_resizes[(MAP, SLOT)].columns == 3
    assert tab.structure_target().layer(SLOT).columns == 3


def test_reverting_a_projects_own_resize_is_staged_and_written_last(tab):
    tab.world.set_layer_resize(None, None, LayerResize(MAP, SLOT, 3, 2, 1))
    tab.world.writes.clear()
    tab.on_project_mutated()
    assert tab.structure_target().layer(SLOT).resized is True
    assert tab._revert_structure_button.isEnabled()

    assert tab.revert_selected_structure() is True
    assert tab._staged_resizes == {(MAP, SLOT): None}
    assert tab.structure_target().layer(SLOT).resized is False

    assert tab.apply_to_project() is True
    assert [entry[0] for entry in tab.world.writes] == ["clear-resize"]
    assert tab.world.structure.resize_for(MAP, SLOT) is None


def test_reverting_a_layer_that_still_holds_cells_is_refused_with_the_count(
    tab, monkeypatch
):
    seen = _warnings(monkeypatch)
    tab.world.set_layer_resize(None, None, LayerResize(MAP, SLOT, 3, 2, 1))
    tab.world.layout[(MAP, SLOT, 4)] = 2
    tab.world.writes.clear()
    tab.on_project_mutated()

    assert tab.revert_selected_structure() is False
    assert len(seen) == 1 and "still holds 1 authored cell(s)" in seen[0]
    assert tab.world.writes == []
    assert tab.world.structure.resize_for(MAP, SLOT) is not None


# --- 4. authoring a layer ----------------------------------------------------


def test_only_an_unused_slot_is_offered_for_a_new_layer(tab):
    assert tab.free_slots(MAP) == (3,)
    dialog = tab.build_new_layer_dialog()
    assert dialog is not None
    assert dialog._slot.count() == 1
    assert dialog._slot.itemData(0) == 3
    # The template is one of this map's own supported dominant layers.
    assert [dialog._template.itemData(row) for row in range(dialog._template.count())] == [
        SLOT
    ]
    dialog.reject()


def test_a_new_layer_is_one_undo_command_and_undo_and_redo_move_it(tab):
    assert tab.apply_new_layer("qa-bg3", 3, SLOT, 2, 2, 1) is True
    assert tab._undo_stack.count() == 1
    command = tab._undo_stack.command(0)
    assert isinstance(command, NewLayerCommand)
    assert command.identity == AUTHORED
    assert command.previous is None
    assert command.applied.columns == 2
    assert tab.world.writes == []

    layer = tab.structural_layer(MAP, 3)
    assert layer is not None and layer.identity == AUTHORED
    assert (layer.columns, layer.rows) == (2, 2)
    assert tab.unsaved_edit_count() == 1
    assert "BG3 \u2192 layer:qa-bg3 2\u00d72 (new layer staged)" in tab._structure_staged.text()

    tab._undo_stack.undo()
    assert tab.structural_layer(MAP, 3) is None
    assert tab.unsaved_edit_count() == 0

    tab._undo_stack.redo()
    assert tab.structural_layer(MAP, 3).identity == AUTHORED


def test_applying_a_new_layer_writes_the_project_once(tab):
    tab.apply_new_layer("qa-bg3", 3, SLOT, 3, 1, 2)
    assert tab.apply_to_project() is True
    assert [entry[0] for entry in tab.world.writes] == ["layer"]
    identity, fill = tab.world.writes[0][1], tab.world.writes[0][2]
    assert identity == AUTHORED and fill == 2
    assert tab.world.structure.layers[AUTHORED].columns == 3
    assert tab._staged_layers == {}
    assert tab.unsaved_edit_count() == 0


def test_a_new_layer_on_a_used_slot_is_refused_with_its_reason(tab, monkeypatch):
    seen = _warnings(monkeypatch)
    assert tab.apply_new_layer("qa-bg1", 1, SLOT, 2, 2, 1) is False
    assert len(seen) == 1 and "can only activate a slot the canonical image leaves unused" in seen[0]
    assert tab._staged_layers == {}


def test_a_new_layer_is_refused_when_its_name_is_not_a_usable_identity(tab, monkeypatch):
    seen = _warnings(monkeypatch)
    assert tab.apply_new_layer("QA BG3", 3, SLOT, 2, 2, 1) is False
    assert len(seen) == 1 and "not a usable layer name" in seen[0]
    assert tab._staged_layers == {}


def test_a_new_layer_refuses_an_initialization_chunk_the_template_does_not_draw(
    tab, monkeypatch
):
    seen = _warnings(monkeypatch)
    assert tab.apply_new_layer("qa-bg3", 3, SLOT, 2, 2, 9) is False
    assert len(seen) == 1 and "not one of the 4 chunks" in seen[0]
    assert tab._staged_layers == {}


def test_a_new_layers_chunks_are_offered_by_the_form_from_its_template(tab):
    dialog = tab.build_new_layer_dialog()
    labels = [dialog._fill.itemText(row) for row in range(dialog._fill.count())]
    assert labels == ["Chunk 1", "Chunk 2", "Chunk 3", "Chunk 4"]
    dialog._name.setText("qa-layer-two")
    dialog._columns.setValue(3)
    dialog._rows.setValue(2)
    assert "layer:qa-layer-two" in dialog.summary_text()
    assert "3\u00d72" in dialog.summary_text()
    dialog.reject()


# --- 5. the new layer in the existing map editor -----------------------------


def test_a_new_layer_is_offered_in_the_map_editor_and_paintable_with_its_vocabulary(
    tab,
):
    tab.apply_new_layer("qa-bg3", 3, SLOT, 2, 2, 1)

    # Selectable: the map editor's own Layer row offers the slot, marked as authored.
    rows = [
        (tab._layer_combo.itemData(row), tab._layer_combo.itemText(row))
        for row in range(tab._layer_combo.count())
    ]
    assert (3, "BG3 \u00b7 chunk grid 2\u00d72 \u00b7 authored Authored: qa-bg3") in rows

    combo_row = tab._layer_combo.findData(3)
    tab._layer_combo.setCurrentIndex(combo_row)
    assert tab._slot is not None and tab._slot.slot == 3
    assert tab._structure_slot is not None and tab._structure_slot.identity == AUTHORED
    # The SAME chunk vocabulary the painter offers, from the template layer.
    assert tab._slot.choices == tuple(choice.address for choice in tab.structure_target().layer(3).vocabulary)
    assert len(tab._slot.choices) == 4
    # Every cell of an authored layer has no canonical field, and the surface says so.
    assert all(cell.offset == -1 for cell in tab._slot.cells)
    assert tab._chunk_label.text() == "Chunk 1 \u00b7 used by 4 cell(s) of BG3"
    assert "no canonical field" in tab._detail.text()

    # Paintable: one stroke over the authored grid stages ordinals, not pointers.
    tab.set_brush_ordinal(3)
    _stroke(tab, 0, 1, 2)
    assert tab._structural_cells == {
        (MAP, 3, 0): 3,
        (MAP, 3, 1): 3,
        (MAP, 3, 2): 3,
    }
    assert tab._chunks.cells == {}
    assert tab._undo_stack.count() == 2  # the creation, then the one stroke
    command = tab._undo_stack.command(1)
    assert isinstance(command, StructuralPaintCommand)
    assert command.cells == (0, 1, 2)
    assert command.previous == {0: None, 1: None, 2: None}
    assert command.applied == {0: 3, 1: 3, 2: 3}
    # Four, not two: the tab's pending count is per CHANGED CELL, exactly as it is
    # for a canonical paint (`_unsaved_count` sums the layout session's edits), and
    # the staged layer is one more change on top of the three painted cells.
    assert tab.unsaved_edit_count() == 1 + 3


def test_a_structural_paint_gesture_undoes_to_each_cells_own_earlier_value(tab):
    tab.world.set_authored_layer(None, None, AuthoredLayer(AUTHORED, MAP, 3, f"map:{MAP:04d}/BG0", 2, 2, 1))
    tab.world.layout[(MAP, 3, 0)] = 2
    tab.on_project_mutated()
    tab._layer_combo.setCurrentIndex(tab._layer_combo.findData(3))

    tab.set_brush_ordinal(4)
    _stroke(tab, 0, 1)
    assert tab._structural_cells == {(MAP, 3, 0): 4, (MAP, 3, 1): 4}

    tab._undo_stack.undo()
    # Cell 0 had a committed ordinal of its own and gets it back; cell 1 had none.
    assert tab._structural_cells == {}
    assert tab._structural_pointer(tab._structure_slot, 0) == tab._slot.choices[1]
    tab._undo_stack.redo()
    assert tab._structural_cells == {(MAP, 3, 0): 4, (MAP, 3, 1): 4}


def test_a_structural_paint_is_written_through_the_one_layout_authority(tab):
    tab.apply_resize(3, 2, 2)
    tab.set_brush_ordinal(3)
    _stroke(tab, 4, 5)
    assert tab._structural_cells == {(MAP, SLOT, 4): 3, (MAP, SLOT, 5): 3}

    assert tab.apply_to_project() is True
    kinds = [entry[0] for entry in tab.world.writes]
    # The grid first, then the cells that only exist because of it.
    assert kinds == ["resize", "layout"]
    assert tab.world.layout == {(MAP, SLOT, 4): 3, (MAP, SLOT, 5): 3}
    assert tab._structural_cells == {}
    assert tab.unsaved_edit_count() == 0


def test_reverting_a_structural_cell_goes_back_to_the_grids_own_default(tab):
    tab.world.set_layer_resize(None, None, LayerResize(MAP, SLOT, 3, 2, 2))
    tab.on_project_mutated()
    tab.set_brush_ordinal(3)
    _stroke(tab, 4)
    assert tab._structural_cells == {(MAP, SLOT, 4): 3}

    tab._selected_cell = 4
    tab._revert_cell()
    assert tab._structural_cells == {}
    # Revert is a gesture like any other: one more command, and undo brings it back.
    assert tab._undo_stack.command(tab._undo_stack.count() - 1).text().startswith(
        "Revert 1 cell"
    )
    tab._undo_stack.undo()
    assert tab._structural_cells == {(MAP, SLOT, 4): 3}


def test_a_structural_paint_of_the_value_a_cell_already_shows_is_not_a_change(tab):
    tab.world.set_layer_resize(None, None, LayerResize(MAP, SLOT, 3, 2, 2))
    tab.on_project_mutated()
    tab.set_brush_ordinal(2)
    _stroke(tab, 4)
    assert tab._structural_cells == {}
    assert tab._undo_stack.count() == 0
    assert tab.unsaved_edit_count() == 0


def test_the_grown_grid_is_what_the_editor_draws_and_what_the_canvas_shows(tab):
    tab.apply_resize(3, 2, 2)
    slot = tab._slot
    assert slot.grid.columns == 3 and slot.grid.rows == 2
    assert slot.grid.cell_count == 6
    assert tab._grid_item is not None and tab._grid_item._grid.cell_count == 6
    # The canvas shows the grown plane: 3 * 256 px wide, from the accepted stitcher.
    assert tab._scene.sceneRect().width() == 3 * CHUNK_PIXELS
    assert tab._scene.sceneRect().height() == 2 * CHUNK_PIXELS


def test_an_authored_layer_gets_its_own_visibility_control(tab):
    tab.apply_new_layer("qa-bg3", 3, SLOT, 2, 2, 1)
    assert 3 in tab._layer_checks
    assert "authored" in tab._layer_checks[3].text()
    tab._layer_checks[3].setChecked(False)
    # Nothing of the authored layer is drawn, but the retail layer still is.
    assert tab._scene.sceneRect().width() == _result(MAP).width


# --- 6. CQA-05: staged structural state survives a project mutation ----------


def test_a_session_change_clears_every_staged_structural_fact(tab):
    tab.apply_resize(3, 2, 2)
    tab.apply_new_layer("qa-bg3", 3, SLOT, 1, 1, 1)
    tab.set_brush_ordinal(3)
    assert tab._staged_resizes and tab._staged_layers

    tab.on_session_changed()

    assert tab._staged_resizes == {}
    assert tab._staged_layers == {}
    assert tab._structural_cells == {}
    assert tab._structure_slot is None
    assert tab._resizer is not None  # re-read for the session that just arrived
    assert tab._undo_stack.count() == 0


def test_a_project_mutation_keeps_a_staged_resize_and_re_reads_the_project(tab):
    tab.apply_resize(3, 2, 2)
    reads_before = tab.world.reads
    builds_before = tab.world.resizer_builds

    # An unrelated project write: the chunk table, the layout document - anything
    # another tab might have authored.
    tab.world.layout[(MAP, SLOT, 0)] = 3
    tab.on_project_mutated()

    assert tab._staged_resizes[(MAP, SLOT)].columns == 3
    assert tab.structure_target().layer(SLOT).columns == 3
    assert tab._undo_stack.count() == 1
    assert tab.world.reads == reads_before + 1
    assert tab.world.resizer_builds == builds_before + 1
    # The ordinal cell of the staged grid is a paint of that grid, not of the
    # canonical record, so it is classified as a structural cell.
    assert tab._structural_committed == {(MAP, SLOT, 0): 3}
    assert tab._chunks.committed == {}


def test_a_project_mutation_re_reads_the_committed_structural_cells(tab):
    tab.world.set_layer_resize(None, None, LayerResize(MAP, SLOT, 3, 2, 1))
    tab.world.layout[(MAP, SLOT, 4)] = 2
    tab.on_project_mutated()
    assert tab._structural_committed == {(MAP, SLOT, 4): 2}

    tab.world.layout.pop((MAP, SLOT, 4))
    tab.on_project_mutated()
    assert tab._structural_committed == {}


# --- 7. CQA-06: the typed boundary ------------------------------------------


#: Every family a structural slot can meet, as an instance and the message it
#: carries. The claim is that none of them escapes a Qt slot: each is exercised on
#: the write path, the preview path and the read path.
STRUCTURAL_FAMILIES = (
    ("MapStructureError (control)", MapStructureError("the grid is refused")),
    ("MapLayoutEditError", MapLayoutEditError("the layer is not editable")),
    ("MapLayoutWriteError", MapLayoutWriteError("the record does not fit")),
    ("MapPaintError", MapPaintError("cell 9 is outside BG0")),
    ("ChunkAuthoringError", ChunkAuthoringError("the chunk template is unknown")),
    ("MapBrowserError", mv.MapBrowserError("the map did not render")),
    ("ProjectError", ProjectError("maps/structure.toml is malformed")),
    ("WriteError", WriteError("the output is not writable")),
    ("MapGraphicsError", MapGraphicsError("the layer record is truncated")),
    ("OSError", OSError("the project file is locked")),
)


@pytest.mark.parametrize("name, error", STRUCTURAL_FAMILIES)
def test_a_structural_write_failure_is_a_warning_not_a_crash(tab, monkeypatch, name, error):
    seen = _warnings(monkeypatch)
    tab.apply_resize(3, 2, 2)
    tab.world.fail_write = error
    assert tab.apply_to_project() is False
    assert seen == [str(error)]


@pytest.mark.parametrize("name, error", STRUCTURAL_FAMILIES)
def test_a_structural_preview_failure_is_a_warning_not_a_crash(tab, monkeypatch, name, error):
    seen = _warnings(monkeypatch)
    tab.world.fail_preview = error
    assert tab.apply_resize(3, 2, 2) is False
    assert seen == [str(error)]
    assert tab._staged_resizes == {}


#: The families reading a project's *structural* document can raise. Narrower than
#: `STRUCTURAL_FAMILIES` on purpose: `read_map_structure` reads the project text and
#: resolves the map table, so it cannot raise a write or an edit failure.
STRUCTURE_READ_FAMILIES = (
    ("MapStructureError (control)", MapStructureError("the grid is refused")),
    ("ProjectError", ProjectError("maps/structure.toml is malformed")),
    ("MapGraphicsError", MapGraphicsError("the layer record is truncated")),
    ("OSError", OSError("the project file is locked")),
)


@pytest.mark.parametrize("name, error", STRUCTURE_READ_FAMILIES)
def test_a_structural_read_failure_on_a_project_mutation_is_reported(
    tab, monkeypatch, name, error
):
    _warnings(monkeypatch)
    status: list[str] = []
    tab.statusChanged.connect(status.append)
    tab.world.fail_read = error
    tab.on_project_mutated()
    assert status and str(error) in status[0]
    assert tab._resizer is None
    # The panel states the same failure sentence the project's layout and chunk
    # readers use - "<subject> could not be read: <reason>" - and names the SDK's
    # own message. (This node used to look for "cannot be read", a wording no
    # surface has ever used; the shipped wording is the one its sibling readers
    # already state, and the test now pins that instead of a guess.)
    panel = tab._structure_support.text()
    assert "could not be read" in panel and str(error) in panel


def test_a_structural_form_that_cannot_validate_reports_and_opens_nothing(tab, monkeypatch):
    seen = _warnings(monkeypatch)
    tab.world.fail_target = MapStructureError("the slot is not a supported grid")
    tab._structure_targets = {}
    assert tab.build_resize_dialog() is None
    assert seen == ["the slot is not a supported grid"]


# --- 8. CQA-07: read counts --------------------------------------------------


def test_a_frame_of_structural_painting_reads_no_project_and_rebuilds_no_view(tab):
    tab.apply_resize(3, 2, 2)
    reads = tab.world.reads
    builds = (tab.world.resizer_builds, tab.world.painter_builds)

    tab.set_brush_ordinal(3)
    for cell in (4, 5):
        _stroke(tab, cell)
    for _ in range(5):
        tab._refresh_preview()
        tab._refresh_editor_state()
        tab._mark_pending_rows()

    assert tab.world.reads == reads
    assert (tab.world.resizer_builds, tab.world.painter_builds) == builds


def test_the_structural_document_is_read_once_per_mutation_and_never_per_gesture(tab):
    # Two reads to start with: the session change, and the map selection, which
    # re-reads the project because the shell may have changed since the last look.
    baseline = tab.world.reads
    assert baseline == 2

    tab.apply_resize(3, 2, 2)
    assert tab.world.reads == baseline, "staging a resize reads nothing"

    tab._undo_stack.undo()
    tab._undo_stack.redo()
    assert tab.world.reads == baseline, "history reads nothing"

    tab.on_project_mutated()
    assert tab.world.reads == baseline + 1, "one mutation, one read"

    # A repaint and a form refresh read nothing at all.
    for _ in range(3):
        tab._refresh_preview()
        tab._refresh_editor_state()
        tab._mark_pending_rows()
    assert tab.world.reads == baseline + 1


def test_many_painted_cells_do_not_multiply_the_structural_reads(tab):
    tab.world.set_layer_resize(None, None, LayerResize(MAP, SLOT, 4, 4, 1))
    tab.on_project_mutated()
    reads = tab.world.reads
    tab._layer_combo.setCurrentIndex(tab._layer_combo.findData(SLOT))
    tab.apply_new_layer("qa-bg3", 3, SLOT, 4, 4, 1)
    tab._layer_combo.setCurrentIndex(tab._layer_combo.findData(3))
    tab.set_brush_ordinal(4)
    _stroke(tab, *range(16))
    assert len(tab._structural_cells) == 16
    assert tab.world.reads == reads


# --- 9. BLOCKER B2: the functional proof this surface owes -------------------
#
# The nodes below are the ones B2 requires and the file was missing: the exact
# retail/authored values an undo and a redo move, that a no-op is not a command,
# the staged-state rules CQA-05 closes (including the layer edit, not only the
# resize), the typed boundary CQA-06 closes with a programmer error still loud,
# and the measured one-write-one-read cost CQA-07 closes.


def test_resize_undo_and_redo_move_the_exact_retail_and_authored_cells(tab, monkeypatch):
    """Undo restores the exact prior grid and cells; redo the exact authored ones."""
    _warnings(monkeypatch)
    retail = tab.structure_target().layer(SLOT)
    retail_cells = retail.cells
    assert (retail.columns, retail.rows) == RETAIL

    assert tab.apply_resize(3, 2, 2) is True
    grown = tab.structure_target().layer(SLOT)
    assert (grown.columns, grown.rows) == (3, 2)
    # Every retail cell keeps its own coordinate and its own chunk...
    assert grown.cells[:4] == retail_cells
    # ...and every cell the growth adds is the initialization chunk.
    fill = grown.chunk(2)
    assert fill is not None
    assert grown.cells[4:] == (fill.address, fill.address)
    assert tab._undo_stack.count() == 1

    tab._undo_stack.undo()
    restored = tab.structure_target().layer(SLOT)
    assert (restored.columns, restored.rows) == RETAIL
    assert restored.cells == retail_cells
    assert restored.resized is False
    assert tab._staged_resizes == {}

    tab._undo_stack.redo()
    again = tab.structure_target().layer(SLOT)
    assert (again.columns, again.rows) == (3, 2)
    assert again.cells == grown.cells

    # A resize that changes nothing is the SDK's own refusal before anything is
    # staged, and it leaves the history and the staged grid exactly as they were.
    assert tab.apply_resize(2, 2, 1) is False
    assert tab._undo_stack.count() == 1
    assert tab._staged_resizes[(MAP, SLOT)].columns == 3


def test_new_layer_undo_and_redo_restore_it_and_a_repeat_is_not_a_command(
    tab, monkeypatch
):
    """Undo removes the authored layer, redo restores it, a repeat is no command."""
    seen = _warnings(monkeypatch)
    assert tab.apply_new_layer("qa-bg3", 3, SLOT, 3, 2, 2) is True
    created = tab.structural_layer(MAP, 3)
    assert created is not None and created.identity == AUTHORED
    assert (created.columns, created.rows) == (3, 2)
    assert tab._undo_stack.count() == 1
    assert tab._staged_layers[AUTHORED].columns == 3

    # The same request again is the same layer: refused, and no second command.
    assert tab.apply_new_layer("qa-bg3", 3, SLOT, 3, 2, 2) is False
    assert "already exists in this project" in seen[-1]
    assert tab._undo_stack.count() == 1
    assert tab._staged_layers[AUTHORED].columns == 3

    tab._undo_stack.undo()
    assert tab.structural_layer(MAP, 3) is None
    assert AUTHORED not in tab._staged_layers
    assert tab.unsaved_edit_count() == 0

    tab._undo_stack.redo()
    again = tab.structural_layer(MAP, 3)
    assert again is not None and again.identity == AUTHORED
    assert (again.columns, again.rows) == (3, 2)
    assert again.cells == created.cells


def test_a_structural_paint_undo_and_redo_move_the_exact_cell_values(tab):
    """Undo and redo restore each cell's own value, staged or committed."""
    tab.world.set_layer_resize(None, None, LayerResize(MAP, SLOT, 3, 2, 1))
    tab.world.layout[(MAP, SLOT, 4)] = 2
    tab.on_project_mutated()
    layer = tab._structure_slot
    assert layer is not None and (layer.columns, layer.rows) == (3, 2)

    before = [tab._structural_pointer(layer, cell) for cell in range(6)]
    tab.set_brush_ordinal(4)
    _stroke(tab, 4, 5)
    painted = [tab._structural_pointer(layer, cell) for cell in range(6)]
    assert painted[4] == painted[5] == layer.chunk(4).address
    assert painted[:4] == before[:4]
    assert tab._undo_stack.count() == 1

    tab._undo_stack.undo()
    assert [tab._structural_pointer(layer, cell) for cell in range(6)] == before
    tab._undo_stack.redo()
    assert [tab._structural_pointer(layer, cell) for cell in range(6)] == painted


def test_a_structural_paint_of_the_projects_own_value_is_not_a_change(tab):
    """A paint of the value a cell already shows is not a command."""
    tab.world.set_layer_resize(None, None, LayerResize(MAP, SLOT, 3, 2, 1))
    tab.world.layout[(MAP, SLOT, 4)] = 2
    tab.on_project_mutated()
    tab.set_brush_ordinal(2)  # exactly what the project already holds at cell 4
    _stroke(tab, 4)
    assert tab._structural_cells == {}
    assert tab._undo_stack.count() == 0
    assert tab.unsaved_edit_count() == 0


# --- 9.1 CQA-05: staged structural state survives a project mutation ---------


def test_a_project_mutation_keeps_a_staged_layer_and_its_painted_cells(tab):
    """A staged layer AND its painted cells survive an unrelated project write."""
    assert tab.apply_new_layer("qa-bg3", 3, SLOT, 2, 2, 1) is True
    tab._layer_combo.setCurrentIndex(tab._layer_combo.findData(3))
    assert tab._slot is not None and tab._slot.slot == 3
    tab.set_brush_ordinal(4)
    _stroke(tab, 0, 1)
    assert tab._structural_cells == {(MAP, 3, 0): 4, (MAP, 3, 1): 4}
    reads = tab.world.reads
    resizer_builds = tab.world.resizer_builds

    # An unrelated, supported project write by another surface, then the shell's
    # own notification.
    tab.world.layout[(MAP, SLOT, 0)] = 3
    tab.on_project_mutated()

    assert tab._staged_layers[AUTHORED].columns == 2
    layer = tab.structural_layer(MAP, 3)
    assert layer is not None and layer.identity == AUTHORED
    assert tab._structural_cells == {(MAP, 3, 0): 4, (MAP, 3, 1): 4}
    assert tab._slot is not None and tab._slot.slot == 3
    assert tab._structure_slot is not None and tab._structure_slot.slot == 3
    assert tab._undo_stack.count() == 2
    # The editor's own working state is the user's, not the document's: the picked
    # cell and the brush survive the same mutation. Re-pointing the editor on every
    # mutation is what lost a staged authored-chunk brush on the tracked
    # MAP-CHUNK-AUTHORING-001 CQA-05 node, and the same rule covers this half.
    assert tab._selected_cell == 1  # the cell the user's stroke finished on
    assert tab._brush_ordinal == 4
    # One mutation re-reads the document once and rebuilds the one facade once.
    assert tab.world.reads == reads + 1
    assert tab.world.resizer_builds == resizer_builds + 1


def test_a_session_change_drops_the_staged_state_and_re_reads_the_project(tab):
    """A genuine image/project replacement resets every session-bound fact."""
    tab.world.set_layer_resize(None, None, LayerResize(MAP, SLOT, 3, 2, 1))
    tab.on_project_mutated()
    assert tab.structural_layer(MAP, SLOT) is not None
    tab.set_brush_ordinal(4)
    _stroke(tab, 4)
    assert tab._structural_cells == {(MAP, SLOT, 4): 4}
    assert tab._undo_stack.count() == 1

    # The project the session was built from is replaced: it no longer holds the
    # resize, and nothing the session had may be carried across.
    tab.world.structure = MapStructure()
    tab.on_session_changed()

    assert tab._staged_resizes == {} and tab._staged_layers == {}
    assert tab._structural_cells == {}
    assert tab._structural_committed == {}
    assert tab.structure_document().resizes == {}
    assert tab.structural_layer(MAP, SLOT) is None
    assert tab._undo_stack.count() == 0
    assert tab._brush_ordinal is None and tab._selected_cell is None
    assert tab._resizer is not None  # re-read for the session that just arrived


# --- 9.2 CQA-06: the typed boundary ------------------------------------------


def test_the_structural_boundary_is_one_declared_family_tuple(tab):
    """Every family a structural slot can meet is declared, and no wider one is."""
    assert MapStructureError in mbt._STRUCTURE_ERRORS
    for family in (
        MapGraphicsError,
        ProjectError,
        WriteError,
        MapLayoutEditError,
        MapLayoutWriteError,
        MapPaintError,
        ChunkAuthoringError,
        mv.MapBrowserError,
        OSError,
    ):
        assert family in mbt._STRUCTURE_ERRORS, family
    # Programmer errors are deliberately NOT converted: a defect in a slot stays
    # loud instead of being reported to the user as an SDK refusal.
    assert Exception not in mbt._STRUCTURE_ERRORS
    assert KeyError not in mbt._STRUCTURE_ERRORS
    assert KeyError not in mbt._STRUCTURE_VIEW_ERRORS


def test_the_four_expected_authoring_failures_land_in_one_typed_boundary(
    tab, monkeypatch
):
    """Unsupported structure, bad dimensions, bad chunk, malformed layer request."""
    seen = _warnings(monkeypatch)

    # 1. Unsupported structure: a slot whose canonical form is not a chunk grid.
    tab._slot = tab._target.slots[2]
    assert tab.apply_resize(3, 2, 1) is False
    assert "terrain-field" in seen[-1]

    # 2. Invalid dimensions, in the SDK's own words.
    tab._slot = tab._target.slots[SLOT]
    assert tab.apply_resize(9, 2, 1) is False
    assert "outside the supported 1..8" in seen[-1]

    # 3. An initialization chunk outside this layer's own vocabulary.
    assert tab.apply_resize(3, 2, 99) is False
    assert "not one of the 4 chunks" in seen[-1]

    # 4. A malformed authored-layer request: an identity the project cannot use,
    #    and a template that is not a supported dominant grid.
    assert tab.apply_new_layer("QA BG3", 3, SLOT, 2, 2, 1) is False
    assert "not a usable layer name" in seen[-1]
    assert tab.apply_new_layer("qa-bg3", 3, 99, 2, 2, 1) is False
    assert "not a supported dominant chunk grid" in seen[-1]

    assert len(seen) == 5
    assert tab._staged_resizes == {} and tab._staged_layers == {}
    assert tab._undo_stack.count() == 0
    assert tab.world.writes == []


def test_a_programmer_error_in_a_structural_slot_is_not_dressed_up_as_a_refusal(
    tab, monkeypatch
):
    """`_STRUCTURE_ERRORS` is a family list, not a blanket: defects stay loud."""
    seen = _warnings(monkeypatch)
    for defect in (KeyError("a defect in the caller"), TypeError("a defect in the caller")):
        tab.world.fail_preview = defect
        with pytest.raises(type(defect)):
            tab.apply_resize(3, 2, 2)
    assert seen == []
    assert tab._staged_resizes == {}
    assert tab._undo_stack.count() == 0


def test_a_view_that_cannot_resolve_the_image_is_a_refusal_not_a_crash(tab, monkeypatch):
    """The declared *view* families are refusals: a bad profile object is reported."""
    seen = _warnings(monkeypatch)
    tab.world.fail_target = TypeError("the profile object is not a RomProfile")
    tab._structure_targets = {}
    assert tab.build_resize_dialog() is None
    assert seen == ["the profile object is not a RomProfile"]


# --- 9.3 CQA-07: the measured cost and the fan-out ---------------------------


def test_one_structural_operation_is_one_project_write_and_one_read(tab):
    """Resize, authored layer and a four-cell paint: each one write, one re-read."""
    reads, writes = tab.world.reads, len(tab.world.writes)

    assert tab.apply_resize(3, 2, 2) is True
    assert tab.world.reads == reads, "staging a resize reads nothing"
    assert len(tab.world.writes) == writes, "staging a resize writes nothing"
    assert tab.apply_to_project() is True
    assert tab.world.reads == reads + 1, "one apply, one re-read"
    assert [entry[0] for entry in tab.world.writes[writes:]] == ["resize"]

    reads, writes = tab.world.reads, len(tab.world.writes)
    assert tab.apply_new_layer("qa-bg3", 3, SLOT, 4, 4, 1) is True
    assert tab.world.reads == reads
    assert tab.apply_to_project() is True
    assert tab.world.reads == reads + 1
    assert [entry[0] for entry in tab.world.writes[writes:]] == ["layer"]

    # Four painted cells on the authored grid are ONE layout write and ONE read.
    tab._layer_combo.setCurrentIndex(tab._layer_combo.findData(3))
    assert tab._slot is not None and tab._slot.slot == 3
    tab.set_brush_ordinal(2)
    reads, writes = tab.world.reads, len(tab.world.writes)
    _stroke(tab, 0, 1, 2, 3)
    assert tab.world.reads == reads
    assert len(tab._structural_cells) == 4
    assert tab.apply_to_project() is True
    assert tab.world.reads == reads + 1
    assert [entry[0] for entry in tab.world.writes[writes:]] == ["layout"]


def test_one_structural_apply_broadcast_back_costs_one_more_read_not_a_cascade(tab):
    """Signal fan-out stays linear: one Apply, one broadcast, one extra read."""
    broadcasts: list[int] = []
    tab.projectChanged.connect(lambda: broadcasts.append(1))
    # The shell wires a surface's own `projectChanged` to every other surface's
    # `on_project_mutated`; connecting this tab to itself is the worst case.
    tab.projectChanged.connect(tab.on_project_mutated)
    reads = tab.world.reads

    assert tab.apply_resize(3, 2, 2) is True
    assert tab.apply_to_project() is True

    assert broadcasts == [1], "one apply, one broadcast"
    assert [entry[0] for entry in tab.world.writes] == ["resize"]
    assert tab.world.reads == reads + 2, "the apply's own re-read plus the broadcast's"


# --- 9.4 project currency (WORKBENCH-MUTATION-CURRENCY-001) ------------------
#
# Resize and layer authoring reach the project through the same
# `apply_to_project`, so they owe the same one-revision contract as a paint. The
# first test below reuses the existing full-write path (resize, then authored
# layer, then a four-cell paint on the authored grid) and records the currency
# after each; the second pins that a re-apply of what the project already holds
# is not a mutation.


def _arm_currency(session) -> int:
    """A session that has validated and built, so staleness is observable."""
    session.record_validation(True)
    session.last_build = object()
    session.build_revision = session.project_revision
    assert session.validation_current
    assert session.build_current
    return session.project_revision


def _assert_currency_spent(session, before: int) -> None:
    """One real mutation: exactly one revision, validation and build stale."""
    assert session.project_revision == before + 1
    assert not session.validation_current
    assert not session.build_current
    assert session.last_build is None


def test_a_structural_apply_then_a_paint_advances_revision_once_each(tab):
    """Each real write invalidates; a no-op structural re-apply does not."""
    session = tab._session
    before = _arm_currency(session)

    assert tab.apply_resize(3, 2, 2) is True
    assert tab.apply_to_project() is True
    _assert_currency_spent(session, before)

    before = _arm_currency(session)
    assert tab.apply_new_layer("qa-bg3", 3, SLOT, 4, 4, 1) is True
    assert tab.apply_to_project() is True
    _assert_currency_spent(session, before)

    before = _arm_currency(session)
    tab._layer_combo.setCurrentIndex(tab._layer_combo.findData(3))
    tab.set_brush_ordinal(2)
    _stroke(tab, 0, 1, 2, 3)
    assert tab.apply_to_project() is True
    _assert_currency_spent(session, before)


def test_a_no_op_structural_apply_leaves_currency_alone(tab):
    """Re-applying a resize the project already holds is not a mutation."""
    session = tab._session
    assert tab.apply_resize(3, 2, 2) is True
    assert tab.apply_to_project() is True

    # The same structural edit again: the project already holds exactly this, so
    # the writer reports no change and nothing is staged.
    before = _arm_currency(session)
    assert tab._staged_resize_edits() == {}, "re-applying stages nothing new"
    assert tab.apply_to_project() is False
    assert session.project_revision == before
    assert session.validation_current
    assert session.build_current
    assert session.last_build is not None


def test_one_apply_is_one_revision_even_when_the_tab_hears_its_own_broadcast(tab):
    """The shell's fan-out must not charge a second revision for one Apply."""
    session = tab._session
    assert tab.apply_resize(3, 2, 2) is True
    before = _arm_currency(session)
    # The shell wires a surface's own `projectChanged` to every other surface's
    # `on_project_mutated`; connecting this tab to itself is the worst case.
    tab.projectChanged.connect(tab.on_project_mutated)

    assert tab.apply_to_project() is True

    assert session.project_revision == before + 1, "one Apply, one revision"
    assert not session.validation_current
    assert not session.build_current
