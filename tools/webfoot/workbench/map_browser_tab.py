"""DRAGONBYTE-Z-MAP-BROWSER-001 / DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001.

The DragonByte Z Map Browser tab: a thin presentation client over
:mod:`tools.export.map_browser` and :mod:`tools.webfoot.map_layout_edit`. It
enumerates all 452 maps with their ROM-derived labels, renders one map on demand,
and lets the user search, zoom, pan and toggle individual graphical layers.

Normal browsing is READ-ONLY. An explicit *Edit Layout* mode adds the first real
map-editing surface: pick a dominant layer's 256x256 chunk cell, choose another
chunk that layer already uses, see the result in the map preview immediately (in
memory - never by writing the source ROM), and save the pending edits to a NEW ROM
copy. Everything the mode can do is decided by the SDK session it drives; this
widget owns no ROM format, no pointer arithmetic and no write of its own.

Layers whose form is not the proven dominant chunk grid - a screen-entry plane, a
terrain-field layer such as Map 19's, an absent slot, or a dominant grid that uses
a single chunk and so has nothing to substitute - are shown READ ONLY with the
reason stated. That is a state, not an error.
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QIcon,
    QImage,
    QPainter,
    QPen,
    QPixmap,
    QUndoCommand,
    QUndoStack,
)
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from tools.webfoot import map_view as mv
from tools.webfoot.formats.map_graphics import MAX_LAYER_GRID_SIDE, MapGraphicsError
from tools.webfoot.map_chunk import (
    ChunkAuthor,
    ChunkAuthoringError,
    ChunkTemplate,
    chunk_identity,
    read_authored_chunks,
    set_authored_chunk,
    set_layout_authored_cells,
)
from tools.webfoot.map_layout_edit import (
    LayoutCell,
    LayoutEdit,
    LayoutGrid,
    LayoutSlot,
    LayoutTarget,
    MapLayoutEditError,
    MapLayoutEditor,
)
from tools.webfoot.map_layout_session import LayoutSession, PendingWork, staged_changes
from tools.webfoot.map_layout_write import MapLayoutWriteError
from tools.webfoot.map_paint import (
    MapPaintError,
    MapPainter,
    read_layout_edits,
    set_layout_cells,
)
from tools.webfoot.map_resize import (
    ChunkChoice,
    MapResizer,
    MapStructureError,
    StructuralLayer,
    StructureTarget,
    clear_layer_resize,
    layer_identity,
    read_map_structure,
    remove_authored_layer,
    resolve_layer_record,
    set_authored_layer,
    set_layer_resize,
)
from tools.webfoot.project import (
    AuthoredChunk,
    AuthoredLayer,
    AuthoredMap,
    AuthoredMaps,
    LayerResize,
    MapStructure,
    ProjectError,
)
from tools.webfoot import map_authoring as map_new
from tools.webfoot.write import WriteError

from . import theme
from .build_panel import is_safe_output_path
from .session import Session
from .widgets import PanelHeader, TechnicalLabel, ToolStrip

#: Cosmetic, honest labels for the accepted structural classifications. The
#: verbatim classification stays in the info panel; these shorten the checkbox.
_LAYER_LABELS = {
    "dominant": "Tilemap",
    "static_graphical_screenblock": "Screen entry",
    "static_graphical_terrain_field": "Terrain field",
    "absent_placeholder": "Absent",
}

#: Bound on retained per-map render results, so browsing never pre-renders the
#: corpus and a session of clicking through maps stays within a modest footprint.
_MAX_RENDER_CACHE = 32

#: The zoom cluster's step buttons. One common width for the two glyph buttons, so
#: the +/- pair reads as one control and the readout between them sits centred.
_ZOOM_BUTTON_W = 34

#: The editable chunk-cell grid is drawn in the accent hue at a cosmetic width, so
#: it reads as a rule over the artwork rather than as a highlight competing with it.
_IDENTITY_ROLE = Qt.ItemDataRole.UserRole
_CHUNK_ROLE = Qt.ItemDataRole.UserRole + 1
#: The row's label without its pending-edit glyph, so the glyph can be added and
#: removed without accumulating dots.
_BASE_TEXT_ROLE = Qt.ItemDataRole.UserRole + 2
#: MAP-CHUNK-AUTHORING-001. The authored chunk identity a palette row names, for
#: the rows that are not canonical chunks. A canonical row leaves it None, so one
#: role carries "which authored chunk" without a second item class.
_AUTHORED_ROLE = Qt.ItemDataRole.UserRole + 3
#: The 16-bit screen entry a chunk editor palette row carries.
_ENTRY_ROLE = Qt.ItemDataRole.UserRole + 4

#: The two editing tools the map surface offers. A tool is a state, not a mode:
#: switching tools never changes what is staged, and the tool strip always shows
#: which one is selected. The chunk editor offers the same two tools over its
#: screen-entry plane.
_TOOL_PAINT = "paint"
_TOOL_PICK = "pick"

#: MAP-CHUNK-AUTHORING-001. The chunk editor's own geometry. A chunk is a 32x32
#: plane of 16-bit screen entries, so one editor cell is one screen entry and the
#: plane is drawn at the format's own 8x8 pixels per tile.
_CHUNK_SIDE = mv.CHUNK_SIDE_TILES
_CHUNK_CELL_PIXELS = mv.CHUNK_PIXELS // _CHUNK_SIDE
#: One screen-entry swatch in the vocabulary palette. 20x20 is small enough that
#: a layer's whole permitted vocabulary is browsable and large enough that a tile
#: is recognisable.
_SWATCH_PIXELS = 20

#: One-line states for a map with nothing editable, keyed by
#: :attr:`LayoutTarget.read_only_kind`. Read-only is a state, not an error.
_READ_ONLY_BADGES = {
    "unsupported": "unsupported layout type",
    "no_alternative": "no alternative chunk in this grid",
    "mixed": "unsupported layout type or no alternative chunk",
}

#: Every failure family a layout-edit slot can see, so no leaf catch can let a
#: sibling escape to a console the user does not have:
#: ``MapLayoutEditError`` (the edit session's own failures),
#: ``MapLayoutWriteError`` (the writer, an unrelated ``ValueError`` subclass the
#: session translates in most paths but which a defensive catch must still cover),
#: ``MapBrowserError`` (the render facade the chooser and preview call),
#: ``ChunkAuthoringError`` (MAP-CHUNK-AUTHORING-001's one public authoring
#: failure: the chunk template, vocabulary, composition and persistence paths all
#: refuse through it, and it is a sibling of every other family here) and
#: ``WriteError`` (the ROM emit path, also unrelated to the other four).
#: The mode-badge role colours. The identity magenta is spent on the editing state
#: only, so the badge cannot compete with the map; a read-only state is a bare glyph
#: plus text, which is why it stays legible without hue.
_MODE_COLORS = {
    "edit": "accent",
    "readonly": "text_muted",
    "neutral": "text_muted",
}
_CHANGE_COLORS = {
    "pending": "pending",
    "saved": "success",
    "neutral": "text_muted",
}
#: Spoken role, so the badge's state survives without any colour at all.
_MODE_ROLE_WORDS = {
    "edit": "Editing state:",
    "readonly": "Read-only state:",
    "neutral": "Browsing state:",
}

_EDIT_ERRORS = (
    MapLayoutEditError,
    MapLayoutWriteError,
    MapPaintError,
    ChunkAuthoringError,
    mv.MapBrowserError,
    WriteError,
)

#: CQA-26. A cell whose pointer could NOT be read. `0` is a real pointer - it is
#: the engine's own null chunk, the value a genuinely empty cell holds - so a
#: failed or not-yet-loaded read must not be spelled with it, or the author is
#: shown a confident "empty cell" for a cell nothing managed to read. The GBA
#: address space starts at 0x08000000, so -1 can never be a real pointer.
_UNREAD_POINTER = -1

#: What every surface says for `_UNREAD_POINTER`, so the unread state reads the
#: same wherever the author meets it and is never mistaken for data.
_UNREAD_CELL = "cell could not be read"

#: The remembered read failure a cell action publishes, in the same shape as
#: `_structure_read_error`: `_update_status` republishes it, so the refresh at the
#: end of a gesture cannot bury the fact that nothing was staged.
_UNREAD_CELL_ACTION = "A cell could not be read, so nothing was staged."

#: The families a *project* read can fail with. `ProjectError` is the project
#: package's own parent (`ProjectLoadError` / `ProjectValidationError`) and
#: `OSError` covers the file read behind it; neither is under `_EDIT_ERRORS`, so a
#: slot that re-reads the project has to name them - the documented "a sibling
#: family needs its own except" rule.
_PROJECT_READ_ERRORS = (ProjectError, ChunkAuthoringError, OSError)

#: The families a project *write* can fail with: the edit families the SDK
#: authoring calls raise, plus the project and filesystem families underneath them.
_EDIT_AND_PROJECT_ERRORS = _EDIT_ERRORS + (ProjectError, OSError)

#: The families the canonical-image chunk facade can fail with. `ChunkAuthor`
#: reads the map table and the layer records underneath it, so the format layer's
#: own error is part of the boundary even though every *authoring* refusal is
#: re-framed as `ChunkAuthoringError`.
_CHUNK_READ_ERRORS = (
    ChunkAuthoringError,
    MapGraphicsError,
    mv.MapBrowserError,
    ProjectError,
    OSError,
)

#: MAP-RESIZE-AND-LAYERS-001. Every family a *structural* slot can meet:
#: ``MapStructureError`` (this capability's one public authoring failure, a
#: ``ValueError`` sibling of every other family here) and ``MapGraphicsError`` (the
#: format layer underneath the structural readers, also a ``ValueError`` sibling),
#: plus the edit, project and filesystem families the surface already declares - the
#: structural readers sit on the same project document, the same write layer and the
#: same format layer the rest of this tab reaches. Naming only ``MapStructureError``
#: would let ``ProjectError`` or ``WriteError`` escape a click to a console the user
#: does not have, which is the documented dead-click failure mode.
_STRUCTURE_ERRORS = (MapStructureError, MapGraphicsError) + _EDIT_AND_PROJECT_ERRORS

#: What building the structural *view* can add on top of that. The reader resolves
#: the profile's own tables by attribute, so a profile object that is not a
#: `RomProfile` surfaces as `AttributeError`/`TypeError` rather than as a refusal. At
#: a session boundary that is a refusal like any other and is reported on screen;
#: a command slot keeps the narrower tuple above, so a programming error in a slot is
#: still loud rather than being dressed up as an SDK refusal.
_STRUCTURE_VIEW_ERRORS = _STRUCTURE_ERRORS + (AttributeError, TypeError)


class PaintCellsCommand(QUndoCommand):
    """One undoable paint gesture: a whole click or drag, not one cell.

    MAP-TILE-PAINT-001. The stroke is staged in the layout session before the
    command is pushed - the same "the edit already happened, the push only
    records it" shape the palette command uses - so a failure inside the SDK
    surfaces in the tab's own guard and NOTHING is pushed.

    `previous` is the value each cell held *before* the stroke, captured from the
    session at stage time. That is what makes undo exact: it restores the
    distinct value each cell had, rather than a single assumed original, and it
    is what the M3 mutation (break previous-value capture) is designed to break.

    Two strokes merge into one command when they are the same layer, the same
    brush, and the second starts on the cell the first ended on - i.e. they are
    one continuous gesture. Then the merged command keeps the FIRST stroke's
    values and the LAST stroke's end cell, so one undo reverses the whole drag.
    """

    def __init__(self, tab, map_index: int, layer_slot: int, cells, previous, applied):
        super().__init__()
        self._tab = tab
        self._map_index = map_index
        self._layer_slot = layer_slot
        #: Row-major cells in stroke order, first-appearance only.
        self._cells = tuple(cells)
        #: cell -> the pointer it held before the stroke.
        self._previous = dict(previous)
        #: cell -> the pointer the stroke staged.
        self._applied = dict(applied)
        #: The gesture identity: the value it painted, the cell it started on and
        #: the cell it ended on. Two gestures merge only when all three agree, so
        #: a continuation of one drag merges while a separate stroke does not.
        self._brush_key = None
        self._start_key = None
        self._end_key = None
        self._first_run = True
        self.setText(self._describe())

    # -- merging -------------------------------------------------------------

    def keys(self):
        return (self._brush_key, self._start_key, self._end_key)

    def set_keys(self, brush_key, start_key, end_key) -> None:
        self._brush_key = brush_key
        self._start_key = start_key
        self._end_key = end_key

    def id(self) -> int:  # noqa: A003 - QUndoCommand's own name
        """Merge class id. Two commands merge only when both return the same id."""
        return 0x4D50  # "MP"

    def mergeWith(self, other: QUndoCommand) -> bool:
        if not isinstance(other, PaintCellsCommand):
            return False
        if self._brush_key is None or other._brush_key != self._brush_key:
            return False
        if other._layer_slot != self._layer_slot or other._map_index != self._map_index:
            return False
        if not self._cells or not other._cells:
            return False
        # Continuity: the second stroke must start where the first ended.
        if other._start_key != self._end_key:
            return False
        # A cell the merged command would visit twice cannot be merged, because
        # undoing it would have to restore two different earlier values.
        if set(other._cells) & set(self._cells):
            return False
        self._cells = self._cells + other._cells
        self._previous.update(other._previous)
        self._applied.update(other._applied)
        self._end_key = other._end_key
        self.setText(self._describe())
        return True

    # -- QUndoCommand --------------------------------------------------------

    def redo(self) -> None:
        if self._first_run:
            # Pushed AFTER the tab staged the stroke; re-applying it here would
            # make this command's first activation a duplicate write.
            self._first_run = False
            return
        self._tab._reapply_paint(self)

    def undo(self) -> None:
        self._tab._reverse_paint(self)

    # -- reporting -----------------------------------------------------------

    @property
    def map_index(self) -> int:
        return self._map_index

    @property
    def layer_slot(self) -> int:
        return self._layer_slot

    @property
    def cells(self) -> tuple[int, ...]:
        return self._cells

    @property
    def previous(self) -> dict[int, int]:
        return dict(self._previous)

    @property
    def applied(self) -> dict[int, int]:
        return dict(self._applied)

    def _describe(self) -> str:
        count = len(self._cells)
        where = f"map:{self._map_index:04d} BG{self._layer_slot}"
        verb = "Revert" if self._tab._naming_revert else "Paint"
        return f"{verb} {count} cell{'s' if count != 1 else ''} on {where}"


class ChunkCellCommand(QUndoCommand):
    """One undoable edit gesture inside the chunk editor's screen-entry plane.

    MAP-CHUNK-AUTHORING-001. The same shape `PaintCellsCommand` uses, for the
    same reasons and on the SAME history: the plane is staged in the tab before
    the command is pushed, so a refusal inside the SDK surfaces in the tab's own
    guard and nothing is pushed; ``previous`` is each cell's entry from before
    the stroke, captured at stage time, so one undo restores the distinct entry
    every cell held rather than one assumed original.

    Its ``id()`` is deliberately NOT the paint command's: two commands merge only
    when both return the same id, so a chunk-plane stroke can never merge into a
    map-cell stroke even though both live on one stack.
    """

    def __init__(self, tab, identity: str, cells, previous, applied):
        super().__init__()
        self._tab = tab
        self._identity = identity
        #: Row-major plane cells in stroke order, first-appearance only.
        self._cells = tuple(cells)
        #: cell -> the screen entry it held before the stroke.
        self._previous = dict(previous)
        #: cell -> the screen entry the stroke staged.
        self._applied = dict(applied)
        self._brush_key = None
        self._start_key = None
        self._end_key = None
        self._first_run = True
        self.setText(self._describe())

    # -- merging -------------------------------------------------------------

    def keys(self):
        return (self._brush_key, self._start_key, self._end_key)

    def set_keys(self, brush_key, start_key, end_key) -> None:
        self._brush_key = brush_key
        self._start_key = start_key
        self._end_key = end_key

    def id(self) -> int:  # noqa: A003 - QUndoCommand's own name
        """Merge class id, distinct from the map paint command's ``0x4D50``."""
        return 0x4348  # "CH"

    def mergeWith(self, other: QUndoCommand) -> bool:
        if not isinstance(other, ChunkCellCommand):
            return False
        if self._brush_key is None or other._brush_key != self._brush_key:
            return False
        if other._identity != self._identity:
            return False
        if not self._cells or not other._cells:
            return False
        # Continuity: the second stroke must start where the first ended.
        if other._start_key != self._end_key:
            return False
        # A cell the merged command would visit twice cannot be merged, because
        # undoing it would have to restore two different earlier entries.
        if set(other._cells) & set(self._cells):
            return False
        self._cells = self._cells + other._cells
        self._previous.update(other._previous)
        self._applied.update(other._applied)
        self._end_key = other._end_key
        self.setText(self._describe())
        return True

    # -- QUndoCommand --------------------------------------------------------

    def redo(self) -> None:
        if self._first_run:
            # Pushed AFTER the tab staged the stroke; re-applying it here would
            # make this command's first activation a duplicate edit.
            self._first_run = False
            return
        self._tab._reapply_chunk_cells(self)

    def undo(self) -> None:
        self._tab._reverse_chunk_cells(self)

    # -- reporting -----------------------------------------------------------

    @property
    def identity(self) -> str:
        return self._identity

    @property
    def cells(self) -> tuple[int, ...]:
        return self._cells

    @property
    def previous(self) -> dict[int, int]:
        return dict(self._previous)

    @property
    def applied(self) -> dict[int, int]:
        return dict(self._applied)

    def _describe(self) -> str:
        count = len(self._cells)
        verb = "Revert" if self._tab._naming_chunk_revert else "Edit"
        return (
            f"{verb} {count} chunk cell{'s' if count != 1 else ''} of "
            f"{self._identity}"
        )


class AuthoredPlaceCommand(QUndoCommand):
    """One undoable gesture that paints an authored chunk into map cells.

    MAP-CHUNK-AUTHORING-001. The map layout editor's own path is pointer-based
    and cannot express a chunk that has no address yet, so an authored placement
    is staged in the tab's own map (``(map, layer, cell) -> chunk identity``) and
    this command records the gesture over it. ``previous`` is the identity each
    cell carried before the stroke - the staged value, else the project's
    committed placement, else ``None`` for "no authored placement here" - so an
    undo restores the exact earlier state of each cell rather than clearing it.

    It shares the tab's ONE history with the paint and chunk commands, and merges
    only with a continuation of the same authored brush, on the same continuity +
    no-repeat-cell rule.
    """

    def __init__(self, tab, map_index: int, layer_slot: int, cells, previous, applied):
        super().__init__()
        self._tab = tab
        self._map_index = map_index
        self._layer_slot = layer_slot
        self._cells = tuple(cells)
        #: cell -> the authored identity the cell carried before, or None.
        self._previous = dict(previous)
        #: cell -> the authored identity the stroke staged.
        self._applied = dict(applied)
        self._brush_key = None
        self._start_key = None
        self._end_key = None
        self._first_run = True
        self.setText(self._describe())

    def keys(self):
        return (self._brush_key, self._start_key, self._end_key)

    def set_keys(self, brush_key, start_key, end_key) -> None:
        self._brush_key = brush_key
        self._start_key = start_key
        self._end_key = end_key

    def id(self) -> int:  # noqa: A003 - QUndoCommand's own name
        """Merge class id, distinct from both the paint and chunk commands."""
        return 0x4150  # "AP"

    def mergeWith(self, other: QUndoCommand) -> bool:
        if not isinstance(other, AuthoredPlaceCommand):
            return False
        if self._brush_key is None or other._brush_key != self._brush_key:
            return False
        if other._layer_slot != self._layer_slot or other._map_index != self._map_index:
            return False
        if not self._cells or not other._cells:
            return False
        if other._start_key != self._end_key:
            return False
        if set(other._cells) & set(self._cells):
            return False
        self._cells = self._cells + other._cells
        self._previous.update(other._previous)
        self._applied.update(other._applied)
        self._end_key = other._end_key
        self.setText(self._describe())
        return True

    def redo(self) -> None:
        if self._first_run:
            self._first_run = False
            return
        self._tab._reapply_authored_place(self)

    def undo(self) -> None:
        self._tab._reverse_authored_place(self)

    @property
    def map_index(self) -> int:
        return self._map_index

    @property
    def layer_slot(self) -> int:
        return self._layer_slot

    @property
    def cells(self) -> tuple[int, ...]:
        return self._cells

    @property
    def previous(self) -> dict[int, str | None]:
        return dict(self._previous)

    @property
    def applied(self) -> dict[int, str]:
        return dict(self._applied)

    def _describe(self) -> str:
        count = len(self._cells)
        where = f"map:{self._map_index:04d} BG{self._layer_slot}"
        verb = "Revert" if self._tab._naming_revert else "Place"
        return f"{verb} {count} cell{'s' if count != 1 else ''} on {where}"


class StructuralPaintCommand(QUndoCommand):
    """One undoable paint gesture inside a project-authored layer grid.

    MAP-RESIZE-AND-LAYERS-001. A resized layer's grown cells - and every cell of a
    project-authored layer - have no four-byte field in the canonical image for the
    layout session to rewrite, so their paints are staged in the tab's own
    ``(map, layer, cell) -> ordinal`` table and written by the SDK's structural-aware
    ``set_layout_cells``. Everything else is the shape `PaintCellsCommand` uses and
    for the same reasons: ``previous`` is each cell's *staged* ordinal from before
    the stroke (``None`` for "no authored paint"), which is what makes one undo
    restore the distinct earlier state of every cell, and its ``id()`` is its own so
    a structural stroke can never merge into a pointer stroke.
    """

    def __init__(self, tab, map_index: int, layer_slot: int, cells, previous, applied):
        super().__init__()
        self._tab = tab
        self._map_index = map_index
        self._layer_slot = layer_slot
        self._cells = tuple(cells)
        #: cell -> the staged ordinal it carried before, or None.
        self._previous = dict(previous)
        #: cell -> the staged ordinal the stroke wrote.
        self._applied = dict(applied)
        self._brush_key = None
        self._start_key = None
        self._end_key = None
        self._first_run = True
        self.setText(self._describe())

    def keys(self):
        return (self._brush_key, self._start_key, self._end_key)

    def set_keys(self, brush_key, start_key, end_key) -> None:
        self._brush_key = brush_key
        self._start_key = start_key
        self._end_key = end_key

    def id(self) -> int:  # noqa: A003 - QUndoCommand's own name
        """Merge class id, distinct from the paint, chunk and placement commands."""
        return 0x5350  # "SP"

    def mergeWith(self, other: QUndoCommand) -> bool:
        if not isinstance(other, StructuralPaintCommand):
            return False
        if self._brush_key is None or other._brush_key != self._brush_key:
            return False
        if other._layer_slot != self._layer_slot or other._map_index != self._map_index:
            return False
        if not self._cells or not other._cells:
            return False
        if other._start_key != self._end_key:
            return False
        if set(other._cells) & set(self._cells):
            return False
        self._cells = self._cells + other._cells
        self._previous.update(other._previous)
        self._applied.update(other._applied)
        self._end_key = other._end_key
        self.setText(self._describe())
        return True

    def redo(self) -> None:
        if self._first_run:
            self._first_run = False
            return
        self._tab._reapply_structural_paint(self)

    def undo(self) -> None:
        self._tab._reverse_structural_paint(self)

    @property
    def map_index(self) -> int:
        return self._map_index

    @property
    def layer_slot(self) -> int:
        return self._layer_slot

    @property
    def cells(self) -> tuple[int, ...]:
        return self._cells

    @property
    def previous(self) -> dict[int, int | None]:
        return dict(self._previous)

    @property
    def applied(self) -> dict[int, int]:
        return dict(self._applied)

    def _describe(self) -> str:
        count = len(self._cells)
        where = f"map:{self._map_index:04d} BG{self._layer_slot}"
        verb = "Revert" if self._tab._naming_revert else "Paint"
        return f"{verb} {count} cell{'s' if count != 1 else ''} on {where}"


# --- MAP-RESIZE-AND-LAYERS-001: the structural surface ------------------------
#
# Everything below is the structural half of this tab. The authority is
# `tools.webfoot.map_resize`: this surface asks `MapResizer` what a map's slots are
# and what a requested resize or authored layer would mean, and persists through
# `set_layer_resize` / `set_authored_layer` / `clear_layer_resize` /
# `remove_authored_layer`. No widget here knows the record layout, the grid bytes,
# the extent arithmetic or the allocator: the labels, the preview line and every
# refusal are the SDK's own.


def _grid_text(columns: int, rows: int) -> str:
    """A chunk grid as the rest of this surface spells one."""
    return f"{columns}\u00d7{rows}"


def _template_text(map_index: int, layer_slot: int) -> str:
    """The project's own spelling of a layer that a new layer copies: ``map:NNNN/BGn``.

    This is the identity `AuthoredLayer.template` stores and
    `MapResizer.template_layer` parses. Spelling it is a *document* matter - no
    offset, address or byte is involved, which is why it belongs to the surface
    that renders the project's own vocabulary rather than to the SDK.
    """
    return f"map:{map_index:04d}/BG{layer_slot}"


def resize_summary(
    label: str,
    previous: tuple[int, int],
    columns: int,
    rows: int,
    fill_label: str,
    extent: tuple[int, int],
    new_extent: tuple[int, int],
) -> str:
    """One readable line for a requested resize: what changes, and to what.

    The shape the ticket names: ``BG0 2x2 -> 3x2; cells 5-6 initialize to Chunk 2;
    map extent x 89 -> 528``. The cell span is stated in the **1-based** numbering
    the grid overlay and the inspector already use ("cell 5 of 6"), so a preview
    and the grid beside it cannot disagree about which cell is which; the extent is
    stated in pixels because that is what the engine's own camera clamp reads, and
    only the axes that actually change are stated.
    """
    parts = [f"{label} {_grid_text(*previous)} \u2192 {_grid_text(columns, rows)}"]
    added = columns * rows - previous[0] * previous[1]
    if added > 0:
        # The SDK refuses a shrink and a no-op, so a validated resize always adds
        # cells; the span is stated in the 1-based numbering the grid overlay uses.
        first = previous[0] * previous[1] + 1
        last = columns * rows
        span = f"cell {first}" if first == last else f"cells {first}-{last}"
        parts.append(f"{span} initialize to {fill_label}")
    for axis, position in (("x", 0), ("y", 1)):
        if new_extent[position] != extent[position]:
            parts.append(
                f"map extent {axis} {extent[position]} \u2192 {new_extent[position]} px"
            )
    return " \u00b7 ".join(parts)


class ResizePreview:
    """What a requested resize would do, stated before anything is written.

    ``edit`` is the value the project would persist; ``summary`` is the one-line
    change statement; ``extent`` is the map's declared pixel extent after the
    resize, per axis, as the build's own resolution computes it.
    """

    __slots__ = ("edit", "summary", "extent")

    def __init__(self, edit: "LayerResize", summary: str, extent: tuple[int, int]) -> None:
        self.edit = edit
        self.summary = summary
        self.extent = extent


class ResizeCommand(QUndoCommand):
    """One undoable resize gesture: the whole grid change, never a cell of it.

    MAP-RESIZE-AND-LAYERS-001. The same shape the paint commands use, and for the
    same reason: the edit is *staged in the tab* before the command is pushed, so a
    refusal inside the SDK surfaces in the tab's own guard and nothing is pushed at
    all. ``previous`` and ``applied`` are the resize the layer carried before and
    after the gesture, ``None`` meaning "no project-authored resize" - which is how
    un-staging a resize, and reverting one, both reverse.

    It deliberately never merges: two resizes are two gestures even when they are
    typed one after the other, because collapsing them would hide an intermediate
    grid the author asked for and one undo would then skip a shape.
    """

    def __init__(self, tab, map_index: int, layer_slot: int, previous, applied) -> None:
        super().__init__()
        self._tab = tab
        self._map_index = map_index
        self._layer_slot = layer_slot
        self._previous = previous
        self._applied = applied
        self._first_run = True
        self.setText(self._describe())

    def id(self) -> int:  # noqa: A003 - QUndoCommand's own name
        """Merge class id, distinct from every cell gesture's."""
        return 0x5253  # "RS"

    def mergeWith(self, other: QUndoCommand) -> bool:
        return False

    def redo(self) -> None:
        if self._first_run:
            # Pushed AFTER the tab staged the resize; re-applying it here would
            # make this command's first activation a duplicate edit.
            self._first_run = False
            return
        self._tab._reapply_resize(self)

    def undo(self) -> None:
        self._tab._reverse_resize(self)

    @property
    def map_index(self) -> int:
        return self._map_index

    @property
    def layer_slot(self) -> int:
        return self._layer_slot

    @property
    def previous(self):
        return self._previous

    @property
    def applied(self):
        return self._applied

    def _describe(self) -> str:
        where = f"map:{self._map_index:04d} BG{self._layer_slot}"
        verb = "Revert" if self._tab._naming_structure_revert else "Resize"
        if self._applied is None:
            return f"{verb} {where} to the retail grid"
        return f"{verb} {where} to {_grid_text(self._applied.columns, self._applied.rows)}"


class NewLayerCommand(QUndoCommand):
    """One undoable layer-authoring gesture: create, or un-create, one layer.

    MAP-RESIZE-AND-LAYERS-001. ``previous`` and ``applied`` are the authored layer
    identity carried before and after the gesture, ``None`` meaning "this project
    declares no such layer" - so undoing a creation un-stages it and redo stages it
    again, on the same one history the paint and chunk gestures use.
    """

    def __init__(self, tab, identity: str, previous, applied) -> None:
        super().__init__()
        self._tab = tab
        self._identity = identity
        self._previous = previous
        self._applied = applied
        self._first_run = True
        self.setText(self._describe())

    def id(self) -> int:  # noqa: A003 - QUndoCommand's own name
        """Merge class id, distinct from every other gesture family's."""
        return 0x4C41  # "LA"

    def mergeWith(self, other: QUndoCommand) -> bool:
        return False

    def redo(self) -> None:
        if self._first_run:
            self._first_run = False
            return
        self._tab._reapply_layer(self)

    def undo(self) -> None:
        self._tab._reverse_layer(self)

    @property
    def identity(self) -> str:
        return self._identity

    @property
    def previous(self):
        return self._previous

    @property
    def applied(self):
        return self._applied

    def _describe(self) -> str:
        verb = "Revert" if self._tab._naming_structure_revert else "Create"
        layer = self._applied if self._applied is not None else self._previous
        where = f"map:{layer.map_index:04d} BG{layer.layer_slot}"
        return f"{verb} {self._identity} on {where} \u00b7 {_grid_text(layer.columns, layer.rows)}"


class _StructureDialog(QDialog):
    """Shared scaffolding for the two structural forms.

    Both forms are the same shape: a few SDK-named fields, one live line that
    states EXACTLY what the change would do (or the SDK's reason it cannot), and
    OK/Cancel. Validation is not duplicated here - the tab hands in a ``preview``
    callable that runs the SDK and raises ``MapStructureError``, so the refusal a
    person reads is the one the SDK would raise, word for word.
    """

    def __init__(self, parent, title: str, preview, apply_command) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self._preview = preview
        self._apply = apply_command
        self._edit = None
        self._ok = None

    # -- the live line -------------------------------------------------------

    def _set_summary(self, text: str, role: str) -> None:
        colour = {
            "ok": "accent",
            "refused": "danger",
            "neutral": "text_secondary",
        }.get(role, "text_secondary")
        self._summary.setText(text)
        self._summary.setStyleSheet(
            f"color: {theme.color(colour).name()}; background: transparent;"
        )
        self._summary.setAccessibleName(text)

    def _run_preview(self, produce) -> None:
        """Run the SDK's own validation and state its verdict, or its refusal.

        A refusal is a *state of the form*, not an error dialog: the line says what
        the SDK said and OK is left to raise it as a `QMessageBox` when pressed, so
        the refusal can never be inferred from a disabled button alone and never
        reaches a console the user does not have.
        """
        try:
            preview = produce()
        except MapStructureError as exc:
            self._edit = None
            self._set_summary(f"Not supported \u00b7 {exc}", "refused")
            return
        self._edit = preview.edit
        self._set_summary(preview.summary, "ok")

    # -- the command ---------------------------------------------------------

    def request(self):
        """The form's current request, in the order the tab's guard takes it."""
        raise NotImplementedError

    def _accept(self) -> None:
        """Run the tab's own SDK guard; stay open when it refuses."""
        if self._apply(*self.request()):
            self.accept()

    def edit(self):
        """The validated value the last preview produced, or None."""
        return self._edit

    def summary_text(self) -> str:
        """The live line's current text, for tests and for the QA harness."""
        return self._summary.text()


class ResizeLayerDialog(_StructureDialog):
    """The resize command: new grid size in chunks, initialization chunk, preview.

    The dialog *shows* the layer's current dimensions and the map's declared pixel
    extent beside the controls, because a grow is only meaningful against what the
    map is now. Shrinking is offered as a value a person can type and is refused
    with the SDK's own reason - never implied to be supported.
    """

    def __init__(self, parent, *, layer, extent, preview, apply_command, current) -> None:
        super().__init__(parent, "Resize layer", preview, apply_command)
        self._layer = layer
        self._extent = extent
        self._current = current

        self._columns = QSpinBox()
        self._columns.setRange(1, MAX_LAYER_GRID_SIDE)
        self._columns.setValue(current[0])
        self._columns.setSuffix(" chunks")
        self._columns.setAccessibleName("New width in chunks")
        self._rows = QSpinBox()
        self._rows.setRange(1, MAX_LAYER_GRID_SIDE)
        self._rows.setValue(current[1])
        self._rows.setSuffix(" chunks")
        self._rows.setAccessibleName("New height in chunks")
        self._fill = QComboBox()
        self._fill.setAccessibleName("Initialization chunk for the new cells")
        for choice in layer.vocabulary:
            self._fill.addItem(choice.label, choice.ordinal)
        self._fill.setToolTip(
            "The chunk every cell the growth adds starts as. Only chunks this "
            "layer already draws are offered."
        )
        self._now = QLabel(
            f"{layer.label} now \u00b7 map extent {extent[0]} \u00d7 {extent[1]} px"
        )
        self._now.setProperty("dbzRole", "hint")
        self._now.setWordWrap(True)
        self._now.setMinimumWidth(0)
        self._summary = QLabel("")
        self._summary.setWordWrap(True)
        self._summary.setMinimumWidth(0)

        form = QFormLayout()
        form.setHorizontalSpacing(theme.SPACE_MD)
        form.setVerticalSpacing(theme.SPACE_XS)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.addRow("Width", self._columns)
        form.addRow("Height", self._rows)
        form.addRow("Initialize new cells", self._fill)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok.setText("Resize")
        self._ok.setProperty("dbzRole", "primary")
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD
        )
        layout.setSpacing(theme.SPACE_SM)
        layout.addWidget(self._now)
        layout.addLayout(form)
        layout.addWidget(self._summary)
        layout.addWidget(buttons)
        self.setMinimumWidth(380)

        self._columns.valueChanged.connect(self._refresh)
        self._rows.valueChanged.connect(self._refresh)
        self._fill.currentIndexChanged.connect(self._refresh)
        self._refresh()

    def request(self) -> tuple[int, int, int]:
        """The requested grid and initialization, as the SDK takes them."""
        return self._columns.value(), self._rows.value(), self._fill.currentData()

    def _refresh(self, *_args) -> None:
        columns, rows = self._columns.value(), self._rows.value()
        if (columns, rows) == self._current:
            # A no-op is a *checkable* condition, not a message the tab has to
            # match: saying so here keeps the first thing a person sees from being
            # a refusal about the shape the layer already has.
            self._edit = None
            self._set_summary(
                f"{self._layer.label} is already {_grid_text(columns, rows)}; a "
                "resize must change the grid.",
                "neutral",
            )
            return
        self._run_preview(
            lambda: self._preview(columns, rows, self._fill.currentData())
        )

    def _accept(self) -> None:
        columns, rows = self._columns.value(), self._rows.value()
        if (columns, rows) == self._current:
            self._set_summary(
                f"{self._layer.label} is already {_grid_text(columns, rows)}; a "
                "resize must change the grid.",
                "neutral",
            )
            return
        super()._accept()


class NewLayerDialog(_StructureDialog):
    """The layer-authoring command: which unused slot, copied from what, how big.

    Only slots the canonical image leaves unused are offered - the engine's layer
    count is fixed at four, so "a new layer" means activating one - and the
    template is a layer of the same map, which is what makes the new record's screen
    entries resolve. The permitted initialization chunks are the template's own, as
    the SDK resolves them, so the form cannot offer a value the build would refuse.
    """

    def __init__(
        self,
        parent,
        *,
        map_index: int,
        free_slots,
        templates,
        vocabulary_for,
        preview,
        apply_command,
        default_name: str,
    ) -> None:
        super().__init__(parent, "New layer", preview, apply_command)
        self._map_index = map_index
        self._vocabulary_for = vocabulary_for

        self._slot = QComboBox()
        self._slot.setAccessibleName("Layer slot to activate")
        for slot in free_slots:
            self._slot.addItem(f"BG{slot} \u00b7 unused by the source image", slot)
        self._template = QComboBox()
        self._template.setAccessibleName("Template layer to copy")
        for layer in templates:
            self._template.addItem(layer.label, layer.slot)
        self._template.setToolTip(
            "The new layer's record header and permitted chunk vocabulary come from "
            "this layer of the same map."
        )
        self._name = QLineEdit(default_name)
        self._name.setAccessibleName("New layer name")
        self._name.setToolTip(
            "A stable project identity: a lowercase letter followed by a-z, 0-9, "
            "'_' or '-'."
        )
        self._columns = QSpinBox()
        self._columns.setRange(1, MAX_LAYER_GRID_SIDE)
        self._columns.setValue(1)
        self._columns.setSuffix(" chunks")
        self._columns.setAccessibleName("New width in chunks")
        self._rows = QSpinBox()
        self._rows.setRange(1, MAX_LAYER_GRID_SIDE)
        self._rows.setValue(1)
        self._rows.setSuffix(" chunks")
        self._rows.setAccessibleName("New height in chunks")
        self._fill = QComboBox()
        self._fill.setAccessibleName("Initialization chunk for the new layer")
        self._note = QLabel(
            "The source image leaves this slot unused, so the new layer is a whole "
            "grid of one chunk until its cells are painted. It does not change the "
            "map's own pixel extent."
        )
        self._note.setProperty("dbzRole", "hint")
        self._note.setWordWrap(True)
        self._note.setMinimumWidth(0)
        self._summary = QLabel("")
        self._summary.setWordWrap(True)
        self._summary.setMinimumWidth(0)

        form = QFormLayout()
        form.setHorizontalSpacing(theme.SPACE_MD)
        form.setVerticalSpacing(theme.SPACE_XS)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.addRow("Slot", self._slot)
        form.addRow("Template", self._template)
        form.addRow("Name", self._name)
        form.addRow("Width", self._columns)
        form.addRow("Height", self._rows)
        form.addRow("Initialize cells", self._fill)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok.setText("Create layer")
        self._ok.setProperty("dbzRole", "primary")
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD
        )
        layout.setSpacing(theme.SPACE_SM)
        layout.addWidget(self._note)
        layout.addLayout(form)
        layout.addWidget(self._summary)
        layout.addWidget(buttons)
        self.setMinimumWidth(400)

        self._template.currentIndexChanged.connect(self._reload_vocabulary)
        self._slot.currentIndexChanged.connect(self._refresh)
        self._columns.valueChanged.connect(self._refresh)
        self._rows.valueChanged.connect(self._refresh)
        self._fill.currentIndexChanged.connect(self._refresh)
        self._name.textChanged.connect(self._refresh)
        self._reload_vocabulary()

    # -- the form's own state ------------------------------------------------

    def template_slot(self) -> int | None:
        return self._template.currentData()

    def slot(self) -> int | None:
        return self._slot.currentData()

    def name(self) -> str:
        return self._name.text().strip()

    def request(self) -> tuple:
        return (
            self.name(),
            self.slot(),
            self.template_slot(),
            self._columns.value(),
            self._rows.value(),
            self._fill.currentData(),
        )

    def _reload_vocabulary(self, *_args) -> None:
        """Re-offer the initialization chunks of the TEMPLATE the form now names."""
        template = self.template_slot()
        self._fill.blockSignals(True)
        self._fill.clear()
        if template is not None:
            for choice in self._vocabulary_for(template):
                self._fill.addItem(choice.label, choice.ordinal)
        self._fill.blockSignals(False)
        self._refresh()

    def _refresh(self, *_args) -> None:
        identity, slot, template, columns, rows, fill = self.request()
        if slot is None or template is None or not identity:
            self._edit = None
            self._set_summary(
                "Name the layer, choose the slot to activate and the template to "
                "copy.",
                "neutral",
            )
            return
        self._run_preview(
            lambda: self._preview(identity, slot, template, columns, rows, fill)
        )


def _checkerboard() -> QBrush:
    """A navy checkerboard for the canvas: unpainted (index 0) pixels show it.

    Two close values of the same navy as every panel, so it marks transparency
    without becoming a black field that makes the map look like it is floating in
    a terminal window.
    """
    cell = 12
    pixmap = QPixmap(cell * 2, cell * 2)
    pixmap.fill(theme.color("checker_dark"))
    painter = QPainter(pixmap)
    painter.fillRect(0, 0, cell, cell, theme.color("checker_light"))
    painter.fillRect(cell, cell, cell, cell, theme.color("checker_light"))
    painter.end()
    return QBrush(pixmap)


class NewMapCommand(QUndoCommand):
    """One undoable new-map gesture: author a map identity, or un-author it.

    MAP-NEW-AUTHORING-001. The document is project-wide rather than per-map -
    `maps/authored.toml` holds every authored identity in one file - so the
    command carries the whole document before and after the gesture and rewrites
    it through the SDK's one writer. ``previous`` and ``applied`` are those two
    documents, which is what makes undo remove exactly the definition this
    gesture added and leave every other one alone.
    """

    def __init__(self, tab, previous: "AuthoredMaps", applied: "AuthoredMaps",
                 text: str) -> None:
        super().__init__()
        self._tab = tab
        self._previous = previous
        self._applied = applied
        self._first_run = True
        self.setText(text)

    def id(self) -> int:  # noqa: A003 - QUndoCommand's own name
        return 0x4D41  # "MA", distinct from every other gesture family

    def mergeWith(self, other: QUndoCommand) -> bool:
        return False

    def redo(self) -> None:
        if self._first_run:
            self._first_run = False
            return
        self._tab.write_authored_maps_document(self._applied)

    def undo(self) -> None:
        self._tab.write_authored_maps_document(self._previous)

    @property
    def previous(self) -> "AuthoredMaps":
        return self._previous

    @property
    def applied(self) -> "AuthoredMaps":
        return self._applied


class NewMapDialog(QDialog):
    """The new-map form: a durable name, a donor, and the engine's two key bytes.

    Only what the author decides is a field. Everything else about the new map is
    inherited from the donor, which is why the form offers a donor rather than a
    root, a layer list or a table index: those are the donor's own values, and a
    form that asked for them would be asking the author to invent engine
    semantics nothing has resolved.

    Validation is not duplicated here. The tab hands in ``preview``, which runs
    the SDK's own plan against the open image and raises its own error type, so
    the refusal a person reads is the one the build would raise.
    """

    def __init__(self, parent, *, donors, default_name: str, default_donor: int,
                 default_key, preview, apply_command) -> None:
        super().__init__(parent)
        self.setWindowTitle("New map")
        self.setModal(True)
        self._preview = preview
        self._apply = apply_command

        self._name = QLineEdit(default_name)
        self._name.setAccessibleName("New map name")
        self._name.setToolTip(
            "A stable project identity: a lowercase letter followed by a-z, 0-9, "
            "'_' or '-'."
        )
        self._donor = QComboBox()
        self._donor.setAccessibleName("Donor map")
        for index, label in donors:
            self._donor.addItem(f"map:{index:04d} \u00b7 {label}", index)
        position = self._donor.findData(default_donor)
        if position >= 0:
            self._donor.setCurrentIndex(position)
        self._donor.setToolTip(
            "The map whose record fields, graphics, layers and chunks the new map "
            "inherits. The engine's unresolved root fields are copied from it "
            "rather than invented."
        )
        self._key_high = QSpinBox()
        self._key_high.setRange(0, 0xFF)
        self._key_high.setValue(default_key[0])
        self._key_high.setPrefix("0x")
        self._key_high.setDisplayIntegerBase(16)
        self._key_high.setAccessibleName("New map key high byte")
        self._key_low = QSpinBox()
        self._key_low.setRange(0, 0xFF)
        self._key_low.setValue(default_key[1])
        self._key_low.setPrefix("0x")
        self._key_low.setDisplayIntegerBase(16)
        self._key_low.setAccessibleName("New map key low byte")
        self._key_low.setToolTip(
            "The engine's own map identity: the two bytes the lookup at 0x080089FC "
            "compares and a transition record carries. They must be a pair no map "
            "in this image uses."
        )
        self._summary = QLabel("")
        self._summary.setWordWrap(True)
        self._summary.setProperty("dbzRole", "hint")

        form = QFormLayout(self)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.addRow("Name", self._name)
        form.addRow("Donor", self._donor)
        form.addRow("Key high byte", self._key_high)
        form.addRow("Key low byte", self._key_low)
        form.addRow("Result", self._summary)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self._name.textChanged.connect(lambda *_: self._refresh())
        self._donor.currentIndexChanged.connect(lambda *_: self._refresh())
        self._key_high.valueChanged.connect(lambda *_: self._refresh())
        self._key_low.valueChanged.connect(lambda *_: self._refresh())
        self._refresh()

    def request(self):
        """The form's current request, in the order the tab's guard takes it."""
        return (self._name.text().strip(), int(self._donor.currentData()),
                self._key_high.value(), self._key_low.value())

    def _refresh(self) -> None:
        try:
            summary = self._preview(*self.request())
        except map_new.MapAuthoringError as exc:
            self._summary.setText(f"Not supported \u00b7 {exc}")
            self._summary.setStyleSheet(
                f"color: {theme.color('danger').name()}; background: transparent;"
            )
            return
        self._summary.setText(summary)
        self._summary.setStyleSheet(
            f"color: {theme.color('accent').name()}; background: transparent;"
        )

    def _accept(self) -> None:
        """Run the tab's own SDK guard; stay open when it refuses."""
        if self._apply(*self.request()):
            self.accept()


class ChunkGridOverlay(QGraphicsItem):
    """The editable chunk-cell grid drawn over one dominant layer of the map.

    One cell is one 256x256 chunk region, so the grid is the layer's own chunk
    count in both directions. Cells are paint targets: the selected cell, the
    hovered cell and cells that already carry a staged edit are each marked
    distinctly - by fill, border style and corner marker, never by hue alone.

    The overlay owns no editing. It reports which cell the pointer is over, on
    press, on drag and on release, and the tab decides what a gesture means; a
    gesture therefore costs one callback per cell the pointer enters rather than
    one per mouse-move event.
    """

    def __init__(
        self,
        grid: LayoutGrid,
        on_cell_clicked,
        *,
        on_stroke_begin=None,
        on_stroke_end=None,
        on_hover=None,
    ) -> None:
        super().__init__()
        self._grid = grid
        self._on_cell_clicked = on_cell_clicked
        self._on_stroke_begin = on_stroke_begin
        self._on_stroke_end = on_stroke_end
        self._on_hover = on_hover
        self._selected: int | None = None
        self._hovered: int | None = None
        self._edited: frozenset[int] = frozenset()
        self._painting = False
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        self.setToolTip(
            "Each cell is one 256×256 chunk region. Click or drag a cell to paint "
            "it with the selected chunk."
        )

    # -- state ---------------------------------------------------------------

    def set_selected(self, cell: int | None) -> None:
        if cell != self._selected:
            self._selected = cell
            self.update()

    def set_edited(self, cells) -> None:
        edited = frozenset(cells)
        if edited != self._edited:
            self._edited = edited
            self.update()

    def cell_at(self, x: int, y: int) -> int | None:
        return self._grid.cell_at(x, y)

    # -- QGraphicsItem -------------------------------------------------------

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._grid.width, self._grid.height)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        """Draw the cell grid and its three cell states.

        Every colour comes from the theme, and the fills are translucent so the map
        artwork stays readable underneath: the review's rule is that game content is
        the most saturated object on screen, so the overlay may only tint it. The
        edited cells carry a corner marker as well as a tint, so "this cell has a
        pending change" is never carried by hue alone.
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        grid_line = theme.qcolor("grid", 130)
        edited_fill = theme.qcolor("pending", 46)
        edited_mark = theme.qcolor("pending", 220)
        hover_fill = theme.qcolor("text_primary", 26)
        hover_edge = theme.qcolor("text_primary", 180)
        selected_fill = theme.qcolor("accent", 60)
        for cell in range(self._grid.cell_count):
            x, y, width, height = self._grid.cell_rect(cell)
            rect = QRectF(x, y, width, height)
            if cell in self._edited:
                painter.fillRect(rect, edited_fill)
                marker = 10
                painter.fillRect(QRectF(x + 3, y + 3, marker, marker), edited_mark)
            if cell == self._hovered and cell != self._selected:
                painter.fillRect(rect, hover_fill)
        # Grid lines: cosmetic, so they stay one device pixel at any zoom.
        grid_pen = QPen(grid_line)
        grid_pen.setCosmetic(True)
        grid_pen.setWidthF(1.0)
        painter.setPen(grid_pen)
        for column in range(1, self._grid.columns):
            x = column * 256
            painter.drawLine(x, 0, x, self._grid.height)
        for row in range(1, self._grid.rows):
            y = row * 256
            painter.drawLine(0, y, self._grid.width, y)
        if self._hovered is not None and self._hovered != self._selected:
            x, y, width, height = self._grid.cell_rect(self._hovered)
            hover_pen = QPen(hover_edge)
            hover_pen.setCosmetic(True)
            hover_pen.setWidthF(2.0)
            painter.setPen(hover_pen)
            painter.drawRect(QRectF(x, y, width, height).adjusted(1, 1, -1, -1))
        if self._selected is not None:
            x, y, width, height = self._grid.cell_rect(self._selected)
            selected_pen = QPen(theme.color("accent"))
            selected_pen.setCosmetic(True)
            selected_pen.setWidthF(3.0)
            painter.setPen(selected_pen)
            painter.fillRect(QRectF(x, y, width, height), selected_fill)
            painter.drawRect(QRectF(x, y, width, height).adjusted(1, 1, -2, -2))

    def hoverMoveEvent(self, event) -> None:
        cell = self._grid.cell_at(int(event.pos().x()), int(event.pos().y()))
        if cell != self._hovered:
            self._hovered = cell
            self.update()
            if cell is not None and self._on_hover is not None:
                self._on_hover(cell)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        if self._hovered is not None:
            self._hovered = None
            self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            cell = self._grid.cell_at(int(event.pos().x()), int(event.pos().y()))
            if cell is not None:
                self._painting = True
                if self._on_stroke_begin is not None:
                    self._on_stroke_begin()
                self._on_cell_clicked(cell)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """Extend a press-drag over the cells the pointer actually enters.

        Only a *changed* cell is reported, so dragging within one 256x256 cell
        costs nothing after the first event. That is what keeps a drag from
        turning into one edit per mouse-move sample.
        """
        if self._painting:
            cell = self._grid.cell_at(int(event.pos().x()), int(event.pos().y()))
            if cell is not None and cell != self._selected:
                self._on_cell_clicked(cell)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._painting and event.button() == Qt.MouseButton.LeftButton:
            self._painting = False
            if self._on_stroke_end is not None:
                self._on_stroke_end()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class ChunkPlaneOverlay(QGraphicsItem):
    """The chunk editor's 32x32 screen-entry grid, drawn over the chunk's pixels.

    MAP-CHUNK-AUTHORING-001. The same contract `ChunkGridOverlay` gives the map:
    one cell is one screen entry, cells are paint targets, and the overlay owns no
    editing - it reports which cell the pointer is over on press, on drag and on
    release, and only when that cell *changed*, so a drag costs one callback per
    cell the pointer actually enters rather than one per mouse-move event.

    It differs in two ways the plane needs: the cell is one 8x8 tile rather than a
    256x256 chunk, and a press carries whether Alt was held, which is the
    eyedropper's second spelling beside the Pick tool.
    """

    def __init__(
        self,
        side: int,
        on_cell_clicked,
        *,
        cell_pixels: int = _CHUNK_CELL_PIXELS,
        on_stroke_begin=None,
        on_stroke_end=None,
        on_cell_hover=None,
    ) -> None:
        super().__init__()
        self._side = side
        self._cell_pixels = cell_pixels
        self._on_cell_clicked = on_cell_clicked
        self._on_stroke_begin = on_stroke_begin
        self._on_stroke_end = on_stroke_end
        self._on_cell_hover = on_cell_hover
        self._selected: int | None = None
        self._hovered: int | None = None
        self._edited: frozenset[int] = frozenset()
        self._painting = False
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        self.setToolTip(
            "Each cell is one screen entry (one 8\u00d78 tile) of this chunk. Click "
            "or drag to paint the selected entry; Alt-click picks the entry under "
            "the pointer."
        )

    # -- geometry ------------------------------------------------------------

    @property
    def side(self) -> int:
        return self._side

    @property
    def cell_count(self) -> int:
        return self._side * self._side

    def contains(self, cell: int) -> bool:
        return type(cell) is int and 0 <= cell < self.cell_count

    def cell_at(self, x: int, y: int) -> int | None:
        if x < 0 or y < 0:
            return None
        column = x // self._cell_pixels
        row = y // self._cell_pixels
        if column >= self._side or row >= self._side:
            return None
        return row * self._side + column

    def cell_rect(self, cell: int) -> tuple[int, int, int, int]:
        column = cell % self._side
        row = cell // self._side
        return (
            column * self._cell_pixels,
            row * self._cell_pixels,
            self._cell_pixels,
            self._cell_pixels,
        )

    # -- state ---------------------------------------------------------------

    def set_selected(self, cell: int | None) -> None:
        if cell != self._selected:
            self._selected = cell
            self.update()

    def set_edited(self, cells) -> None:
        edited = frozenset(cells)
        if edited != self._edited:
            self._edited = edited
            self.update()

    # -- QGraphicsItem -------------------------------------------------------

    def boundingRect(self) -> QRectF:
        extent = self._side * self._cell_pixels
        return QRectF(0, 0, extent, extent)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        """Draw the entry grid and its three cell states.

        The plane's own pixels are the content, so the overlay may only tint them:
        the fills are translucent, and an edited cell carries a corner marker as
        well as a tint, so "this entry was changed" is never carried by hue alone.
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        grid_line = theme.qcolor("grid", 90)
        edited_fill = theme.qcolor("pending", 70)
        edited_mark = theme.qcolor("pending", 230)
        hover_fill = theme.qcolor("text_primary", 30)
        hover_edge = theme.qcolor("text_primary", 180)
        selected_fill = theme.qcolor("accent", 70)
        for cell in self._edited:
            x, y, width, height = self.cell_rect(cell)
            painter.fillRect(QRectF(x, y, width, height), edited_fill)
            painter.fillRect(QRectF(x + 1, y + 1, 3, 3), edited_mark)
        if self._hovered is not None and self._hovered != self._selected:
            x, y, width, height = self.cell_rect(self._hovered)
            painter.fillRect(QRectF(x, y, width, height), hover_fill)
        grid_pen = QPen(grid_line)
        grid_pen.setCosmetic(True)
        grid_pen.setWidthF(1.0)
        painter.setPen(grid_pen)
        extent = self._side * self._cell_pixels
        for index in range(1, self._side):
            offset = index * self._cell_pixels
            painter.drawLine(offset, 0, offset, extent)
            painter.drawLine(0, offset, extent, offset)
        if self._hovered is not None and self._hovered != self._selected:
            x, y, width, height = self.cell_rect(self._hovered)
            hover_pen = QPen(hover_edge)
            hover_pen.setCosmetic(True)
            hover_pen.setWidthF(2.0)
            painter.setPen(hover_pen)
            painter.drawRect(QRectF(x, y, width, height).adjusted(1, 1, -1, -1))
        if self._selected is not None:
            x, y, width, height = self.cell_rect(self._selected)
            selected_pen = QPen(theme.color("accent"))
            selected_pen.setCosmetic(True)
            selected_pen.setWidthF(3.0)
            painter.setPen(selected_pen)
            painter.fillRect(QRectF(x, y, width, height), selected_fill)
            painter.drawRect(QRectF(x, y, width, height).adjusted(1, 1, -2, -2))

    def hoverMoveEvent(self, event) -> None:
        cell = self.cell_at(int(event.pos().x()), int(event.pos().y()))
        if cell != self._hovered:
            self._hovered = cell
            self.update()
            if self._on_cell_hover is not None:
                self._on_cell_hover(cell)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        if self._hovered is not None:
            self._hovered = None
            self.update()
            if self._on_cell_hover is not None:
                self._on_cell_hover(None)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            cell = self.cell_at(int(event.pos().x()), int(event.pos().y()))
            if cell is not None:
                alt = bool(event.modifiers() & Qt.KeyboardModifier.AltModifier)
                self._painting = True
                if self._on_stroke_begin is not None:
                    self._on_stroke_begin()
                self._on_cell_clicked(cell, alt)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """Extend a press-drag over the cells the pointer actually enters."""
        if self._painting:
            cell = self.cell_at(int(event.pos().x()), int(event.pos().y()))
            if cell is not None and cell != self._selected:
                self._on_cell_clicked(cell, False)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._painting and event.button() == Qt.MouseButton.LeftButton:
            self._painting = False
            if self._on_stroke_end is not None:
                self._on_stroke_end()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class MapBrowserCanvas(QGraphicsView):
    """Crisp map viewport with wheel zoom, middle-drag pan and fit-to-window.

    In layout edit mode the tab installs a key handler: arrow keys move the chunk
    cell selection and Enter applies the pending chunk change.
    """

    #: Current scale, so the status bar and tool strip can show a real zoom
    #: readout instead of the user having to guess (Tiled's zoom combo).
    zoomChanged = Signal(float)

    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__(scene)
        self._panning = False
        self._pan_position = None
        self._key_handler = None
        self._hover_handler = None
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setBackgroundBrush(_checkerboard())

    def set_key_handler(self, handler) -> None:
        """Install (or clear) the edit-mode key handler: it returns True if used."""
        self._key_handler = handler

    def set_hover_handler(self, handler) -> None:
        """Install the hover readout handler: ``handler(x, y)`` in map pixels.

        ``handler(None, None)`` is delivered when the pointer leaves the canvas,
        so the readout can clear instead of freezing on a stale coordinate.
        """
        self._hover_handler = handler

    def scale_factor(self) -> float:
        """The current view scale, 1.0 meaning one map pixel per screen pixel."""
        return float(self.transform().m11())

    def zoom_in(self) -> None:
        self._change_zoom(1.25)

    def zoom_out(self) -> None:
        self._change_zoom(0.8)

    def fit_map(self) -> None:
        rect = self.sceneRect()
        if rect.isEmpty():
            return
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        self.zoomChanged.emit(self.scale_factor())

    def reset_zoom(self) -> None:
        self.resetTransform()
        self.zoomChanged.emit(self.scale_factor())

    def _change_zoom(self, factor: float) -> None:
        current = self.transform().m11()
        target = current * factor
        if not 0.0625 <= target <= 32:
            return
        self.scale(factor, factor)
        self.zoomChanged.emit(self.scale_factor())

    def keyPressEvent(self, event) -> None:
        if self._key_handler is not None and self._key_handler(event):
            event.accept()
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event) -> None:
        if event.angleDelta().y():
            self._change_zoom(1.15 if event.angleDelta().y() > 0 else 1 / 1.15)
            event.accept()
            return
        super().wheelEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_position = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._panning and self._pan_position is not None:
            delta = event.position() - self._pan_position
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - round(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - round(delta.y())
            )
            self._pan_position = event.position()
            event.accept()
            return
        if self._hover_handler is not None:
            # Porymap's status bar is a live hover instrument rather than a fixed
            # ticker; the tab turns this point into map pixels, cell and chunk.
            scene_pos = self.mapToScene(event.position().toPoint())
            self._hover_handler(int(scene_pos.x()), int(scene_pos.y()))
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if self._hover_handler is not None:
            self._hover_handler(None, None)
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._panning and event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self._pan_position = None
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class MapBrowserTab(QWidget):
    """Map browser: list + search | viewer | inspector, plus an Edit Layout mode.

    Geometry, and the reference each pane comes from
    (``docs/research/UI_REFERENCE_MATRIX.md``):

    - **left** - search field over the map collection (Porymap's filter-then-list
      pane; LDtk's fixed-height scroll region).
    - **centre** - one contextual tool strip directly above the canvas, then the
      canvas itself, then the chunk palette below it. Porymap puts its paint
      tools, view toggles and a structural action on one line at grid row 0 with
      the canvas at row 1; Tiled makes the canvas the *only* undecorated region;
      LDtk's palette is regenerated per active layer. DragonByte Z therefore has
      exactly one tool strip, one undecorated canvas, and one palette that is
      present only while editing.
    - **right** - one inspector pane whose contents the mode swaps, the way
      Porymap's ``stackedWidget_MapEvents`` swaps the whole right pane per mode.
    - **bottom** - one compact status line (Porymap's mode-aware instrument
      readout and Tiled's status-bar contract).

    The tab owns no ROM format, no pointer arithmetic and no write of its own.
    """

    #: Pending layout edits appeared or disappeared; the shell shows this too.
    dirtyChanged = Signal()
    #: The compact one-line tab status, forwarded to the shell's status bar.
    statusChanged = Signal(str)
    #: Save As wrote a new ROM, which changes what the Shell's project state means.
    projectChanged = Signal()

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session
        self._entries: dict[int, mv.MapIndexEntry] = {}
        self._render_cache: "OrderedDict[int, mv.MapBrowserResult]" = OrderedDict()
        self._current: mv.MapBrowserResult | None = None
        self._layer_checks: dict[int, QCheckBox] = {}

        # -- layout editing state, all in-memory -----------------------------
        self._edit_mode = False
        self._editor: MapLayoutEditor | None = None
        #: The layout domain's session: what a write has published, and what is
        #: pending on it (CQA-27). The policy is the SDK's; this tab renders it.
        self._layout = LayoutSession()
        self._editor_error: str | None = None
        self._target: LayoutTarget | None = None
        self._slot = None
        self._selected_cell: int | None = None
        #: One uncommitted chooser pick: (layer slot, cell, replacement).
        self._draft: tuple[int, int, int] | None = None
        #: The brush value, held as BOTH the 1-based ordinal a project persists
        #: and the pointer the render and edit paths take. They are one fact in
        #: two forms, resolved through the session's own layer vocabulary, so a
        #: paint can never stage a value the build would refuse.
        self._brush_ordinal: int | None = None
        self._brush_pointer: int | None = None
        #: The cells the current drag gesture has already staged, what each held
        #: before and after - the raw material of its one undo command - and the
        #: first and last cells the pointer VISITED, which is what makes two
        #: consecutive presses recognisably one continuous drag even when the
        #: shared cell needed no change.
        self._stroke: list[int] = []
        self._stroke_previous: dict[int, int] = {}
        self._stroke_applied: dict[int, int] = {}
        self._stroke_first: int | None = None
        self._stroke_last: int | None = None
        self._stroke_active = False
        self._thumbnails: dict[int, QPixmap] = {}
        self._suppress_chooser = False
        self._last_dirty = 0
        #: The session's tool selection and its committed-project layer, both
        #: read by the status line.
        self._tool = _TOOL_PAINT
        self._alt_pick = False
        #: WB-005 Layer 3's rule, applied here: the paint history is ONE stack for
        #: the whole map surface, raised by a stroke at gesture end so a drag is a
        #: single undoable gesture. It survives an unrelated project mutation
        #: (CQA-05) and is cleared only by a session change, when the base image
        #: every command's captured values came from is actually replaced.
        self._undo_stack = QUndoStack(self)
        #: The palette's full height, measured from its own content in
        #: `_size_chunk_chooser`; the palette collapses to its header without it.
        self._palette_height = 0
        #: True while a parent editor (the Maps editor) owns mode selection, so
        #: this tab does not render its own Edit Layout toggle a second time.
        self._modes_owned_by_host = False
        #: Set while the revert button is building its own history entry, so the
        #: command names the operation the user performed:
        #: ``Paint 1 cell on map:0000 BG0`` versus ``Revert 1 cell ...``.
        self._naming_revert = False

        # -- MAP-CHUNK-AUTHORING-001 state, all in-memory ---------------------
        #
        # The map paint path is pointer-based - `MapLayoutEditor.set_cell` takes a
        # 4-byte chunk address and `LayoutSlot.choices` only holds chunks the
        # layer already uses - so an authored chunk, which has no address until a
        # build allocates one, cannot travel through it. It is staged here instead
        # and persisted by its own SDK authority.
        #: Staged authored placements: ``(map, layer, cell) -> chunk identity``.
        self._authored_cells: dict[tuple[int, int, int], str] = {}
        #: The authored chunk the map painter will place, or None for a canonical
        #: brush. Exactly one of `_brush_authored` and `_brush_pointer` is set.
        self._brush_authored: str | None = None
        #: The project's committed authored chunks and placements, re-read from the
        #: project on a mutation or a session change - never per repaint (CQA-07).
        self._project_chunks: dict[str, AuthoredChunk] = {}
        self._authored_committed: dict[tuple[int, int, int], str] = {}
        #: identity -> the resolved 1,024-entry plane, cached per session. Resolving
        #: a chunk re-reads its template and re-validates every edit, so doing it
        #: per repaint would be the CQA-07 regression in a different costume.
        self._resolved_planes: dict[str, tuple[int, ...]] = {}
        #: Chunk documents composed but not yet written to the project, keyed by
        #: identity. A chunk is created in the editor before it is persisted, so
        #: this is what "the chunk counts as unsaved work" means.
        self._staged_chunks: dict[str, AuthoredChunk] = {}
        #: The cached read/compose facade over the open image's canonical bytes.
        self._chunk_author_cache: ChunkAuthor | None = None
        self._chunk_author_error: str | None = None

        # -- the chunk editor's own state -------------------------------------
        #: True while the chunk editor page is the centre surface.
        self._chunk_editor_open = False
        self._chunk_identity: str | None = None
        self._chunk_template: ChunkTemplate | None = None
        #: The template's own plane: what an authored cell is a delta against.
        self._chunk_template_plane: tuple[int, ...] = ()
        #: The plane as the project holds it (the last applied/template state).
        self._chunk_applied_plane: tuple[int, ...] = ()
        #: The staged plane: a mutable list, one 16-bit entry per cell.
        self._chunk_plane: list[int] = []
        self._chunk_brush: int | None = None
        self._chunk_selected: int | None = None
        self._chunk_tool = _TOOL_PAINT
        self._chunk_hover: str = ""
        self._chunk_stroke: list[int] = []
        self._chunk_stroke_previous: dict[int, int] = {}
        self._chunk_stroke_applied: dict[int, int] = {}
        self._chunk_stroke_first: int | None = None
        self._chunk_stroke_last: int | None = None
        self._chunk_stroke_active = False
        self._chunk_thumbnails: dict[tuple[int, int, int], QPixmap] = {}
        #: Set while the chunk editor's revert is building its history entry.
        self._naming_chunk_revert = False
        self._suppress_chunk_palette = False
        #: The template map's assembled character block, taken from the session's
        #: own cached block when the editor opens, so a plane repaint does not
        #: re-decode it.
        self._chunk_char_data: bytes | None = None
        #: Authored chunks whose plane could not be resolved, so the refusal is
        #: reported once rather than on every repaint of the palette.
        self._plane_error_reported: set[str] = set()

        # -- MAP-RESIZE-AND-LAYERS-001 state, all in-memory -------------------
        #
        # The project's own `maps/structure.toml` is read ONCE per session and per
        # project mutation (CQA-07) into `_structure`; everything on screen is
        # derived from that document merged with the two staged tables below, which
        # is what makes an undoable staged resize cost no project read at all.
        #: The project's committed structural document.
        self._structure: MapStructure | None = None
        #: Why structure editing is unavailable, empty when it is.
        self._structure_unavailable: str = ""
        #: The project's structural document could not be read, in the sentence the
        #: status line states; empty while it reads. A project mutation is a
        #: background event, so this is the channel that reports it where a user is
        #: looking - the same rule the layout and chunk readers already follow.
        self._structure_read_error: str = ""
        #: CQA-26: the last cell read that failed, republished by `_update_status`
        #: so a gesture's own refresh cannot bury it. Cleared by the next read that
        #: succeeds, which every refresh performs.
        self._cell_read_error: str = ""
        #: The merged document (committed + staged), rebuilt without any I/O.
        self._staged_document: MapStructure | None = None
        #: Staged resizes and layers: the value, or None meaning "remove the
        #: project's own". Keyed exactly as the project keys them.
        self._staged_resizes: dict[tuple[int, int], "LayerResize | None"] = {}
        self._staged_layers: dict[str, "AuthoredLayer | None"] = {}
        #: The one structural facade over the merged document, and the one paint
        #: authority over the same, both rebuilt only by `_rebuild_structure_view`.
        self._resizer: MapResizer | None = None
        self._painter: MapPainter | None = None
        #: Per-map `StructureTarget`, memoized for the life of one merged document.
        self._structure_targets: dict[int, StructureTarget] = {}
        #: What the Layer row last listed: `(slot, label, project layer or None)`.
        #: `None` means "the combo was cleared by something other than a fill", so
        #: the next fill happens whatever the rows are. A project mutation compares
        #: against this instead of rebuilding the editor selection, which would
        #: discard the user's brush, picked cell and draft (CQA-05).
        self._layer_rows_signature: tuple | None = None
        #: The structural layer the map editor is pointed at, when the selected
        #: slot's grid is the project's rather than the canonical record's.
        self._structure_slot: StructuralLayer | None = None
        #: Staged paints on project-authored grids: `(map, slot, cell) -> ordinal`,
        #: and the same cells as the project holds them, re-read with the project.
        self._structural_cells: dict[tuple[int, int, int], int] = {}
        self._structural_committed: dict[tuple[int, int, int], int] = {}
        #: Chunk images for structural cells, keyed by canonical chunk address, so a
        #: repaint of a grown grid re-renders no chunk body more than once.
        self._structural_images: dict[int, mv.ChunkImage] = {}
        #: Set while the structure section is rebuilding its own list, so selecting
        #: a row programmatically cannot re-enter the selection slot.
        self._suppress_structure_list = False
        #: The structure list's current content, so a repaint that changes nothing
        #: allocates no item and touches no widget.
        self._structure_row_signature: tuple = ()
        #: Set while a structural gesture is building its history entry, so the
        #: command names the operation the user performed.
        self._naming_structure_revert = False

        self._scene = QGraphicsScene(self)
        self._canvas = MapBrowserCanvas(self._scene)
        self._canvas.set_key_handler(self._on_canvas_key)
        self._canvas.set_hover_handler(self._on_canvas_hover)
        self._hover_text = ""
        #: The cell-under-pointer readout, set by the grid overlay's hover and
        #: cleared when the pointer leaves it. Kept apart from `_hover_text`
        #: (map pixels) so the canvas can show both without either erasing the
        #: other.
        self._hover_cell: str | None = None
        self._tool = _TOOL_PAINT
        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._grid_item: ChunkGridOverlay | None = None

        # -- LEFT: search + map collection ------------------------------------
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search by name or map id (e.g. West City, map:0017)")
        self._search.setClearButtonEnabled(True)
        self._search.setAccessibleName("Filter maps")
        self._search.textChanged.connect(self._apply_filter)
        self._list = QListWidget()
        self._list.setUniformItemSizes(True)
        self._list.setAlternatingRowColors(False)
        # Long map labels must not force the collection pane wider than its
        # share: it elides and scrolls instead, which is what keeps the canvas
        # from being pushed into a horizontal scrollbar.
        self._list.setMinimumWidth(0)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self._list.currentItemChanged.connect(self._on_selection)
        self._list_count = QLabel("")
        self._list_count.setProperty("dbzRole", "count")
        left_header = PanelHeader("Maps")
        left_header.add_trailing(self._list_count)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_layout.addWidget(left_header)
        left_layout.addWidget(self._search)
        left_layout.addWidget(self._list, 1)

        # -- CENTRE: one contextual strip over the canvas, then the palette ----
        self._edit_toggle = QPushButton("Edit Layout")
        self._edit_toggle.setCheckable(True)
        self._edit_toggle.setEnabled(False)
        self._edit_toggle.setProperty("dbzRole", "primary")
        self._edit_toggle.setToolTip(
            "Edit a supported map's dominant-layer chunk layout. Browsing stays "
            "read-only until this is on."
        )
        self._edit_toggle.toggled.connect(self._on_edit_mode_toggled)

        self._layers_box = QWidget()
        self._layers_box.setObjectName("dbzLayerToggleHost")
        self._layers_layout = QHBoxLayout(self._layers_box)
        self._layers_layout.setContentsMargins(0, 0, 0, 0)
        self._layers_layout.setSpacing(theme.SPACE_MD)
        # One button per graphical layer, each carrying a menu with the layer's
        # own classification. The wording lives in the menu rather than on the
        # button face, so a narrow window shortens *which* layers are offered
        # without ever making a layer's meaning unreadable - the failure a row of
        # labelled check boxes has, and the reason LDtk keeps its context in a
        # single-line strip and its detail in a pop-out.
        self._layers_menu = QMenu(self)
        self._layers_button = QToolButton()
        self._layers_button.setText("Layers")
        self._layers_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._layers_button.setMenu(self._layers_menu)
        self._layers_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self._layers_button.setToolTip("Which graphical layers of this map to draw")
        self._layers_button.setAccessibleName("Layers")

        # -- the paint tool group ---------------------------------------------
        #
        # Three mutually exclusive tools, the way Porymap's tool strip offers its
        # pencil/picker pair: the paint tool is the default and what a click
        # means depends on it, so the tool strip carries one selected tool rather
        # than a mode the user has to infer from the cursor.
        self._tool_group = QButtonGroup(self)
        self._tool_group.setExclusive(True)
        self._paint_tool = QPushButton("Paint")
        self._paint_tool.setCheckable(True)
        self._paint_tool.setChecked(True)
        self._paint_tool.setToolTip(
            "Paint the selected chunk: click a cell, or drag to paint a run of them"
        )
        self._paint_tool.setAccessibleName("Paint tool")
        self._pick_tool = QPushButton("Pick")
        self._pick_tool.setCheckable(True)
        self._pick_tool.setToolTip(
            "Eyedropper: take the chunk under the pointer as the brush, without "
            "changing the map (P)"
        )
        self._pick_tool.setAccessibleName("Eyedropper tool")
        self._tool_group.addButton(self._paint_tool)
        self._tool_group.addButton(self._pick_tool)
        self._paint_tool.clicked.connect(lambda: self._set_tool(_TOOL_PAINT))
        self._pick_tool.clicked.connect(lambda: self._set_tool(_TOOL_PICK))

        # -- undo/redo ---------------------------------------------------------
        #
        # The stack's own actions, so the buttons stay enabled in step with the
        # history. The keys are NOT set here: CQA-23 leaves Ctrl+Z and Ctrl+Y to
        # the shell's Edit -> Undo/Redo, which route to the ACTIVE mode's history
        # (`MapsEditor.undo_stack`). Binding the standard keys here as well made
        # one key answer to two live actions in this window.
        self._undo_action = self._undo_stack.createUndoAction(self, "Undo paint")
        self._redo_action = self._undo_stack.createRedoAction(self, "Redo paint")
        self._undo_button = QPushButton("Undo")
        self._undo_button.setToolTip(
            "Undo the last paint gesture (also Edit > Undo, Ctrl+Z)"
        )
        self._undo_button.clicked.connect(self._undo_action.trigger)
        self._undo_button.setEnabled(False)
        self._redo_button = QPushButton("Redo")
        self._redo_button.setToolTip(
            "Redo the last undone paint gesture (also Edit > Redo, Ctrl+Y)"
        )
        self._redo_button.clicked.connect(self._redo_action.trigger)
        self._redo_button.setEnabled(False)
        self._undo_stack.canUndoChanged.connect(self._undo_button.setEnabled)
        self._undo_stack.canRedoChanged.connect(self._redo_button.setEnabled)
        self.addAction(self._undo_action)
        self.addAction(self._redo_action)

        # -- MAP-CHUNK-AUTHORING-001: create a chunk ---------------------------
        #
        # ONE action with two spellings, so the button and the menu entry cannot
        # drift: the inspector's button triggers it, and the tool strip's "Chunk"
        # menu holds it as the menu action. The template is whatever chunk the
        # layer's own chooser has selected, which is the surface requirement 2
        # names - there is no second template picker.
        self._create_chunk_action = QAction("Create Chunk\u2026", self)
        self._create_chunk_action.setToolTip(
            "Create a new 256\u00d7256 chunk from the selected chunk of this layer, "
            "then arrange its screen entries"
        )
        self._create_chunk_action.triggered.connect(self.create_chunk)
        self._chunk_menu = QMenu(self)
        self._chunk_menu.addAction(self._create_chunk_action)
        self._chunk_menu_button = QToolButton()
        self._chunk_menu_button.setText("Chunk")
        self._chunk_menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._chunk_menu_button.setMenu(self._chunk_menu)
        self._chunk_menu_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextOnly
        )
        self._chunk_menu_button.setToolTip(
            "Chunk authoring: create a new chunk from this layer's chunks"
        )
        self._chunk_menu_button.setAccessibleName("Chunk")


        # -- the zoom cluster --------------------------------------------------
        #
        # A conventional compact zoom group, in the order every desktop editor
        # uses: decrease, the CURRENT zoom readout, increase, then the two reset
        # commands. The readout used to be right-aligned *before* the buttons and
        # sat beside a "100%" button, so two percentages appeared together with
        # nothing to say which was state and which was a command. Now the state is
        # a readout between the two buttons that change it, the reset reads "1:1"
        # because that is literally what it does (one image pixel per screen pixel,
        # `reset_zoom`), and both reset commands are buttons rather than labels.
        self._zoom_out = QPushButton("\u2212")
        self._zoom_out.setToolTip("Zoom out")
        self._zoom_out.setFixedWidth(_ZOOM_BUTTON_W)
        self._zoom_out.setAccessibleName("Zoom out")
        self._zoom_out.clicked.connect(self._canvas.zoom_out)
        self._zoom_label = QLabel("Fit")
        self._zoom_label.setProperty("dbzRole", "technical")
        self._zoom_label.setToolTip("Current zoom")
        self._zoom_label.setMinimumWidth(56)
        self._zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._zoom_in = QPushButton("+")
        self._zoom_in.setToolTip("Zoom in")
        self._zoom_in.setFixedWidth(_ZOOM_BUTTON_W)
        self._zoom_in.setAccessibleName("Zoom in")
        self._zoom_in.clicked.connect(self._canvas.zoom_in)
        self._actual = QPushButton("1:1")
        self._actual.setToolTip("Reset to 1:1 pixels")
        self._actual.setAccessibleName("Reset zoom to 1:1")
        self._actual.clicked.connect(self._canvas.reset_zoom)
        self._fit = QPushButton("Fit")
        self._fit.setToolTip("Fit the map to the window")
        self._fit.setAccessibleName("Fit map to window")
        self._fit.clicked.connect(self._canvas.fit_map)

        self._strip = ToolStrip()
        self._strip.add(self._edit_toggle)
        self._strip.add_separator()
        self._strip.add(self._paint_tool)
        self._strip.add(self._pick_tool)
        self._strip.add(self._undo_button)
        self._strip.add(self._redo_button)
        self._strip.add_separator()
        self._strip.add(self._chunk_menu_button)
        self._strip.add_separator()
        self._strip.add(self._layers_box)
        self._strip.add_stretch()
        self._strip.add(self._zoom_out)
        self._strip.add(self._zoom_label)
        self._strip.add(self._zoom_in)
        self._strip.add_separator()
        self._strip.add(self._actual)
        self._strip.add(self._fit)
        self._canvas.zoomChanged.connect(self._on_zoom_changed)

        canvas_frame = QFrame()
        canvas_frame.setObjectName("dbzMapCanvasFrame")
        canvas_layout = QVBoxLayout(canvas_frame)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)
        canvas_layout.addWidget(self._strip)
        canvas_layout.addWidget(self._canvas, 1)
        #: Retained for callers and tests that referenced the old titled box.
        self._canvas_box = canvas_frame

        # -- CENTRE-BOTTOM: the chunk palette --------------------------------
        self._chooser_hint = QLabel("Select a map to see its chunks.")
        self._chooser_hint.setProperty("dbzRole", "hint")
        self._chooser_hint.setWordWrap(True)
        self._chooser = QListWidget()
        self._chooser.setViewMode(QListWidget.ViewMode.IconMode)
        self._chooser.setIconSize(QSize(48, 48))
        self._chooser.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._chooser.setMovement(QListWidget.Movement.Static)
        self._chooser.setUniformItemSizes(False)
        self._chooser.setWordWrap(True)
        self._chooser.setFlow(QListWidget.Flow.LeftToRight)
        self._chooser.setWrapping(False)
        self._chooser.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._chooser.setAccessibleName("Chunks this layer already uses")
        self._chooser.setToolTip(
            "Only chunks this layer already uses can replace a cell's chunk."
        )
        self._chooser.currentItemChanged.connect(self._on_chunk_selected)
        self._chooser_header = PanelHeader("Cell chunks", collapsible=True)
        self._chooser_header.toggled.connect(self._on_chooser_toggled)
        chooser_body = QWidget()
        chooser_layout = QVBoxLayout(chooser_body)
        chooser_layout.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_XS, theme.SPACE_SM, theme.SPACE_XS
        )
        chooser_layout.setSpacing(theme.SPACE_XS)
        chooser_layout.addWidget(self._chooser_hint)
        chooser_layout.addWidget(self._chooser, 1)
        self._chooser_box = QWidget()
        self._chooser_box.setObjectName("dbzChunkPalette")
        chooser_box_layout = QVBoxLayout(self._chooser_box)
        chooser_box_layout.setContentsMargins(0, 0, 0, 0)
        chooser_box_layout.setSpacing(0)
        chooser_box_layout.addWidget(self._chooser_header)
        chooser_box_layout.addWidget(chooser_body, 1)

        # -- THE CHUNK EDITOR: a second centre surface, not a second editor tab --
        #
        # MAP-CHUNK-AUTHORING-001. A chunk is a 32x32 screen-entry plane, so it
        # needs its own canvas and its own vocabulary palette; the ticket forbids
        # a new top-level tab and one surface keeps one undo history, so the
        # centre column swaps between the map and this page instead. Nothing about
        # the map editor changes when the page is not current.
        self._chunk_scene = QGraphicsScene(self)
        self._chunk_canvas = MapBrowserCanvas(self._chunk_scene)
        self._chunk_canvas.set_key_handler(self._on_chunk_canvas_key)
        self._chunk_canvas.set_hover_handler(self._on_chunk_canvas_hover)
        self._chunk_pixmap_item: QGraphicsPixmapItem | None = None
        self._chunk_overlay: ChunkPlaneOverlay | None = None

        self._chunk_title = QLabel("\u2014")
        self._chunk_title.setProperty("dbzRole", "fieldLabel")
        self._chunk_title.setWordWrap(True)
        self._chunk_state_label = QLabel("No chunk is open")
        self._chunk_state_label.setWordWrap(True)
        self._chunk_hover_label = QLabel("")
        self._chunk_hover_label.setProperty("dbzRole", "technical")
        self._chunk_hover_label.setWordWrap(True)
        #: The entry the next plane click will paint, stated in words. The map's own
        #: brush readout lives in the inspector, which describes the MAP brush while
        #: this page is on screen, so the chunk editor states its own.
        self._chunk_entry_readout = QLabel("\u2014")
        self._chunk_entry_readout.setProperty("dbzRole", "technical")
        self._chunk_entry_readout.setWordWrap(True)
        self._chunk_entry_readout.setMinimumWidth(0)
        self._chunk_entry_readout.setToolTip("The screen entry the next click will paint")

        # The chunk editor's tool pair is its own selection, so switching to the
        # pick tool here cannot silently change what a map click does.
        self._chunk_tool_group = QButtonGroup(self)
        self._chunk_tool_group.setExclusive(True)
        self._chunk_paint_tool = QPushButton("Paint")
        self._chunk_paint_tool.setCheckable(True)
        self._chunk_paint_tool.setChecked(True)
        self._chunk_paint_tool.setToolTip(
            "Paint the selected screen entry: click a cell, or drag along a run of them"
        )
        self._chunk_paint_tool.setAccessibleName("Paint entry tool")
        self._chunk_pick_tool = QPushButton("Pick")
        self._chunk_pick_tool.setCheckable(True)
        self._chunk_pick_tool.setToolTip(
            "Eyedropper: take the entry under the pointer as the brush "
            "(Alt-click does the same)"
        )
        self._chunk_pick_tool.setAccessibleName("Pick entry tool")
        self._chunk_tool_group.addButton(self._chunk_paint_tool)
        self._chunk_tool_group.addButton(self._chunk_pick_tool)
        self._chunk_paint_tool.clicked.connect(lambda: self.set_chunk_tool(_TOOL_PAINT))
        self._chunk_pick_tool.clicked.connect(lambda: self.set_chunk_tool(_TOOL_PICK))

        # Undo/redo here are the SAME QUndoStack's actions the map strip uses, so
        # the keyboard shortcut, the map buttons and these buttons can never
        # disagree about the history.
        self._chunk_undo_button = QPushButton("Undo")
        self._chunk_undo_button.setToolTip(
            "Undo the last edit gesture (also Edit > Undo, Ctrl+Z)"
        )
        self._chunk_undo_button.clicked.connect(self._undo_action.trigger)
        self._chunk_undo_button.setEnabled(False)
        self._chunk_redo_button = QPushButton("Redo")
        self._chunk_redo_button.setToolTip(
            "Redo the last undone gesture (also Edit > Redo, Ctrl+Y)"
        )
        self._chunk_redo_button.clicked.connect(self._redo_action.trigger)
        self._chunk_redo_button.setEnabled(False)
        self._undo_stack.canUndoChanged.connect(self._chunk_undo_button.setEnabled)
        self._undo_stack.canRedoChanged.connect(self._chunk_redo_button.setEnabled)

        self._chunk_apply_button = QPushButton("Apply chunk")
        self._chunk_apply_button.setProperty("dbzRole", "primary")
        self._chunk_apply_button.setToolTip(
            "Write this chunk into the project's maps/chunks.toml, so a cell can "
            "reference it and a build can materialize it"
        )
        self._chunk_apply_button.clicked.connect(self.apply_chunk)
        self._chunk_revert_button = QPushButton("Revert edits")
        self._chunk_revert_button.setToolTip(
            "Put every edited cell back to the entry the last applied chunk holds "
            "(this is itself undoable)"
        )
        self._chunk_revert_button.clicked.connect(self.revert_chunk_edits)
        self._chunk_brush_button = QPushButton("Use as paint brush")
        self._chunk_brush_button.setProperty("dbzRole", "primary")
        self._chunk_brush_button.setToolTip(
            "Return to the map with this chunk selected, then click map cells to "
            "place it"
        )
        self._chunk_brush_button.clicked.connect(self.use_chunk_as_brush)
        self._chunk_back_button = QPushButton("Back to map")
        self._chunk_back_button.setToolTip(
            "Leave the chunk editor. An unapplied chunk stays staged, so it still "
            "counts as unsaved work and still appears in the map's chunk palette."
        )
        self._chunk_back_button.clicked.connect(self.close_chunk_editor)

        self._chunk_fit = QPushButton("Fit")
        self._chunk_fit.setToolTip("Fit the chunk to the window")
        self._chunk_fit.setAccessibleName("Fit chunk to window")
        self._chunk_fit.clicked.connect(self._chunk_canvas.fit_map)
        self._chunk_actual = QPushButton("1:1")
        self._chunk_actual.setToolTip("Reset to one chunk pixel per screen pixel")
        self._chunk_actual.setAccessibleName("Reset chunk zoom to 1:1")
        self._chunk_actual.clicked.connect(self._chunk_canvas.reset_zoom)

        self._chunk_strip = ToolStrip()
        self._chunk_strip.add(self._chunk_paint_tool)
        self._chunk_strip.add(self._chunk_pick_tool)
        self._chunk_strip.add(self._chunk_undo_button)
        self._chunk_strip.add(self._chunk_redo_button)
        self._chunk_strip.add_separator()
        self._chunk_strip.add(self._chunk_back_button)
        self._chunk_strip.add_stretch()
        self._chunk_strip.add(self._chunk_fit)
        self._chunk_strip.add(self._chunk_actual)

        # The screen-entry vocabulary: one swatch per entry the layer's own chunks
        # already display, which is the whole permitted authoring vocabulary.
        self._chunk_palette = QListWidget()
        self._chunk_palette.setViewMode(QListWidget.ViewMode.IconMode)
        self._chunk_palette.setIconSize(QSize(_SWATCH_PIXELS, _SWATCH_PIXELS))
        self._chunk_palette.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._chunk_palette.setMovement(QListWidget.Movement.Static)
        self._chunk_palette.setFlow(QListWidget.Flow.LeftToRight)
        self._chunk_palette.setWrapping(True)
        self._chunk_palette.setUniformItemSizes(True)
        # The SDK's own entry label ("tile 3 · flip H") is longer than one line, and
        # two entries that share a tile ordinal differ exactly in that suffix: a
        # label clipped to "tile 3" would offer two identical-looking swatches with
        # different artwork, so the text wraps instead.
        self._chunk_palette.setWordWrap(True)
        self._chunk_palette.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._chunk_palette.setAccessibleName("Screen entries this layer already draws")
        self._chunk_palette.setToolTip(
            "Every screen entry this layer's own chunks draw. An authored chunk may "
            "only rearrange graphics the layer already uses, so these are the only "
            "values an entry can hold."
        )
        self._chunk_palette.currentItemChanged.connect(self._on_entry_selected)
        palette_header = PanelHeader("Screen entries", collapsible=True)
        palette_header.set_expanded(True)
        palette_body = QWidget()
        palette_layout = QVBoxLayout(palette_body)
        palette_layout.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_XS, theme.SPACE_SM, theme.SPACE_XS
        )
        palette_layout.setSpacing(theme.SPACE_XS)
        self._chunk_palette_hint = QLabel("No chunk is open.")
        self._chunk_palette_hint.setProperty("dbzRole", "hint")
        self._chunk_palette_hint.setWordWrap(True)
        self._chunk_palette_hint.setMinimumWidth(0)
        palette_layout.addWidget(self._chunk_palette_hint)
        palette_layout.addWidget(self._chunk_palette, 1)
        palette_box = QWidget()
        palette_box.setObjectName("dbzEntryPalette")
        palette_box_layout = QVBoxLayout(palette_box)
        palette_box_layout.setContentsMargins(0, 0, 0, 0)
        palette_box_layout.setSpacing(0)
        palette_box_layout.addWidget(palette_header)
        palette_box_layout.addWidget(palette_body, 1)
        # Two 94px swatch cells plus the list's own border and scrollbar, so a row
        # is never clipped at the pane's edge and no partial column can appear.
        palette_box.setFixedWidth(216)

        chunk_body = QHBoxLayout()
        chunk_body.setContentsMargins(0, 0, 0, 0)
        chunk_body.setSpacing(0)
        chunk_body.addWidget(self._chunk_canvas, 1)
        chunk_body.addWidget(palette_box)

        chunk_header = QWidget()
        chunk_header_layout = QVBoxLayout(chunk_header)
        chunk_header_layout.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_XS
        )
        chunk_header_layout.setSpacing(theme.SPACE_XS)
        chunk_header_layout.addWidget(self._chunk_title)
        chunk_header_layout.addWidget(self._chunk_entry_readout)
        chunk_header_layout.addWidget(self._chunk_state_label)
        chunk_header_layout.addWidget(self._chunk_hover_label)

        chunk_actions = QHBoxLayout()
        chunk_actions.setContentsMargins(
            theme.SPACE_SM, 0, theme.SPACE_SM, theme.SPACE_SM
        )
        chunk_actions.addWidget(self._chunk_apply_button)
        chunk_actions.addWidget(self._chunk_revert_button)
        chunk_actions.addWidget(self._chunk_brush_button)
        chunk_actions.addStretch(1)

        self._chunk_page = QWidget()
        self._chunk_page.setObjectName("dbzChunkEditor")
        chunk_page_layout = QVBoxLayout(self._chunk_page)
        chunk_page_layout.setContentsMargins(0, 0, 0, 0)
        chunk_page_layout.setSpacing(0)
        chunk_page_layout.addWidget(self._chunk_strip)
        chunk_page_layout.addWidget(chunk_header)
        chunk_page_layout.addLayout(chunk_body, 1)
        chunk_page_layout.addLayout(chunk_actions)

        centre_split = QSplitter(Qt.Orientation.Vertical)
        centre_split.addWidget(canvas_frame)
        centre_split.addWidget(self._chooser_box)
        centre_split.setStretchFactor(0, 1)
        centre_split.setStretchFactor(1, 0)
        centre_split.setCollapsible(0, False)
        centre_split.setCollapsible(1, False)
        # The palette is a fixed-height instrument, not a second canvas: giving
        # it a stretch factor is what let the canvas eat it entirely. Its height
        # comes from its own content in `_size_chunk_chooser`, so nothing clips.
        centre_split.setSizes([700, 150])
        self._centre_split = centre_split

        # The centre column is ONE surface with two pages: the map layout, and the
        # chunk editor. Swapping pages keeps the surrounding shell, the inspector
        # pages and the undo history exactly where they were.
        self._centre_stack = QStackedWidget()
        self._centre_stack.addWidget(centre_split)
        self._centre_stack.addWidget(self._chunk_page)
        self._centre_stack.setCurrentWidget(centre_split)
        self._chunk_page.setVisible(False)

        # -- RIGHT: one inspector pane, contents swapped by mode --------------
        self._mode_badge = QLabel("VIEW MODE \u00b7 read-only")
        mode_font = self._mode_badge.font()
        mode_font.setBold(True)
        self._mode_badge.setFont(mode_font)
        self._mode_badge.setWordWrap(True)
        #: The full explanation behind a READ ONLY state, kept quiet and separate
        #: so the state itself stays a one-line thing a user can read at a glance.
        self._read_only_detail = QLabel("")
        self._read_only_detail.setWordWrap(True)
        self._read_only_detail.setProperty("dbzRole", "hint")

        self._layer_combo = QComboBox()
        self._layer_combo.setToolTip("Which dominant layer of this map to edit")
        self._layer_combo.setAccessibleName("Layer")
        self._layer_combo.currentIndexChanged.connect(self._on_layer_changed)

        self._cell_label = QLabel("\u2014")
        self._cell_label.setWordWrap(True)
        self._chunk_label = QLabel("\u2014")
        self._chunk_label.setWordWrap(True)
        self._change_label = QLabel("No layout changes")
        self._change_label.setWordWrap(True)

        self._apply_button = QPushButton("Apply")
        self._apply_button.setProperty("dbzRole", "primary")
        self._apply_button.setToolTip("Commit the chosen chunk to the selected cell (Enter)")
        self._apply_button.clicked.connect(self._apply_draft)
        self._revert_button = QPushButton("Revert cell")
        self._revert_button.setToolTip(
            "Put the selected cell back to the chunk the source ROM holds (Esc)"
        )
        self._revert_button.clicked.connect(self._revert_cell)
        self._reset_button = QPushButton("Discard pending")
        self._reset_button.setToolTip(
            "Discard every staged paint in this session; the project keeps what it "
            "already has"
        )
        self._reset_button.clicked.connect(self._reset_edits)
        self._commit_button = QPushButton("Apply to project")
        self._commit_button.setProperty("dbzRole", "primary")
        self._commit_button.setToolTip(
            "Write every staged paint into the project's layout source. The project "
            "is then validated and built like any other authored content."
        )
        self._commit_button.clicked.connect(self.apply_to_project)
        self._save_button = QPushButton("Save As New ROM\u2026")
        self._save_button.setProperty("dbzRole", "primary")
        self._save_button.setToolTip(
            "Write the pending edits to a new ROM file; the source ROM is never "
            "modified. With no pending edits this writes a byte-identical copy."
        )
        self._save_button.clicked.connect(self._on_save_as)

        # MAP-CHUNK-AUTHORING-001. The chunk inspector's own action: the template
        # is the chunk selected in the palette below the canvas, and this opens the
        # chunk editor page on a new chunk built from it.
        self._create_chunk_button = QPushButton("Create Chunk\u2026")
        self._create_chunk_button.setToolTip(
            "Create a new 256\u00d7256 chunk from the chunk selected in the palette, "
            "then arrange its screen entries"
        )
        self._create_chunk_button.clicked.connect(self._create_chunk_action.trigger)
        self._edit_chunk_button = QPushButton("Edit chunk\u2026")
        self._edit_chunk_button.setToolTip(
            "Reopen the authored chunk currently selected in the palette"
        )
        self._edit_chunk_button.clicked.connect(self.edit_selected_authored_chunk)

        # -- MAP-RESIZE-AND-LAYERS-001: the map's own structure ----------------
        #
        # One inspector section, in the same place the surface already keeps its
        # technical detail: the layer list (canonical and project-authored, which is
        # what makes a new layer identifiable), the selected layer's grid and the
        # map's declared extent, whether that slot is supported or refused with the
        # SDK's reason, and the two commands that change the structure. Both
        # commands open a form; the entry controls live there rather than here, so
        # the inspector stays a readout of state and the writing surface stays one
        # thing at a time.
        self._structure_list = QListWidget()
        self._structure_list.setUniformItemSizes(True)
        self._structure_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._structure_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._structure_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self._structure_list.setAccessibleName("Layer slots of this map")
        self._structure_list.setToolTip(
            "Every layer slot of this map: the canonical record it holds, whether "
            "the project resized it or authored it, and why a slot cannot be edited."
        )
        self._structure_list.currentRowChanged.connect(self._on_structure_row_selected)
        self._structure_state = QLabel("No map is selected.")
        self._structure_state.setWordWrap(True)
        self._structure_state.setMinimumWidth(0)
        self._structure_extent = QLabel("")
        self._structure_extent.setProperty("dbzRole", "hint")
        self._structure_extent.setWordWrap(True)
        self._structure_extent.setMinimumWidth(0)
        self._structure_support = QLabel("")
        self._structure_support.setProperty("dbzRole", "hint")
        self._structure_support.setWordWrap(True)
        self._structure_support.setMinimumWidth(0)
        self._structure_staged = QLabel("")
        self._structure_staged.setProperty("dbzRole", "hint")
        self._structure_staged.setWordWrap(True)
        self._structure_staged.setMinimumWidth(0)

        self._resize_button = QPushButton("Resize layer\u2026")
        self._resize_button.setToolTip(
            "Grow the selected layer's chunk grid. A resize redistributes nothing: "
            "the cells the source image holds stay exactly where they are."
        )
        self._resize_button.clicked.connect(self.open_resize_dialog)
        self._new_layer_button = QPushButton("New layer\u2026")
        self._new_layer_button.setToolTip(
            "Activate a layer slot the source image leaves unused, copied from one of "
            "this map's own layers"
        )
        self._new_layer_button.clicked.connect(self.open_new_layer_dialog)
        self._revert_structure_button = QPushButton("Revert structure")
        self._revert_structure_button.setToolTip(
            "Un-stage the selected layer's structural change; the project keeps what "
            "it already holds (this is itself undoable)"
        )
        self._revert_structure_button.clicked.connect(self.revert_selected_structure)
        # MAP-NEW-AUTHORING-001. A project-level command rather than a per-layer
        # one, so it sits on its own row with the other project-wide action rather
        # than in the row of layer-structure commands, where it read as "a fifth
        # layer gesture".
        self._new_map_button = QPushButton("New map\u2026")
        self._new_map_button.setToolTip(
            "Author a new map identity: a row the image does not contain, built "
            "from a donor map's record, root, layers and chunks"
        )
        self._new_map_button.clicked.connect(self.open_new_map_dialog)

        structure_form = QFormLayout()
        structure_form.setContentsMargins(theme.SPACE_SM, theme.SPACE_XS, theme.SPACE_SM, 0)
        structure_form.setHorizontalSpacing(theme.SPACE_MD)
        structure_form.setVerticalSpacing(theme.SPACE_XS)
        structure_form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        structure_form.addRow("Selected layer", self._structure_state)
        structure_form.addRow("Map extent", self._structure_extent)
        structure_form.addRow("Supported", self._structure_support)
        structure_form.addRow("Staged change", self._structure_staged)
        structure_buttons = QHBoxLayout()
        structure_buttons.setContentsMargins(theme.SPACE_SM, 0, theme.SPACE_SM, 0)
        structure_buttons.addWidget(self._resize_button, 1)
        structure_buttons.addWidget(self._new_layer_button, 1)
        # The third command gets its own row. The inspector's action column is
        # 290 px at the default window size, and "Resize layer…" + "New layer…" +
        # "Revert structure" need 339: Qt clipped two of the three labels down to
        # "ssize layer" and "ert struct" (found by looking at the QA captures).
        # Two rows keep every command's own SDK wording readable, which matters
        # more than one row of height in a panel that scrolls.
        structure_revert = QHBoxLayout()
        structure_revert.setContentsMargins(theme.SPACE_SM, 0, theme.SPACE_SM, 0)
        structure_revert.addWidget(self._revert_structure_button, 1)
        structure_revert.addWidget(self._new_map_button, 1)
        structure_body = QWidget()
        structure_body_layout = QVBoxLayout(structure_body)
        structure_body_layout.setContentsMargins(0, 0, 0, 0)
        structure_body_layout.setSpacing(theme.SPACE_XS)
        structure_body_layout.addWidget(self._structure_list)
        structure_body_layout.addLayout(structure_form)
        structure_body_layout.addLayout(structure_buttons)
        structure_body_layout.addLayout(structure_revert)
        self._structure_box = QWidget()
        self._structure_box.setObjectName("dbzMapStructure")
        structure_box_layout = QVBoxLayout(self._structure_box)
        structure_box_layout.setContentsMargins(0, 0, 0, 0)
        structure_box_layout.setSpacing(0)
        structure_box_layout.addWidget(PanelHeader("Map structure"))
        structure_box_layout.addWidget(structure_body)

        editor_form = QFormLayout()
        editor_form.setContentsMargins(theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, 0)
        editor_form.setHorizontalSpacing(theme.SPACE_MD)
        editor_form.setVerticalSpacing(theme.SPACE_XS)
        editor_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        editor_form.addRow("Layer", self._layer_combo)
        editor_form.addRow("Selected cell", self._cell_label)
        editor_form.addRow("Chunk", self._chunk_label)
        editor_form.addRow("Changes", self._change_label)
        self._editor_form = editor_form
        buttons = QHBoxLayout()
        buttons.setContentsMargins(theme.SPACE_SM, 0, theme.SPACE_SM, 0)
        buttons.addWidget(self._apply_button, 1)
        buttons.addWidget(self._revert_button, 1)
        # "Discard pending" needs 127 px and the row has 274 for three commands:
        # the label was clipped to "iscard pendin" (seen in the QA captures). It
        # gets its own row for the same reason the structural row does.
        reset_row = QHBoxLayout()
        reset_row.setContentsMargins(theme.SPACE_SM, 0, theme.SPACE_SM, 0)
        reset_row.addWidget(self._reset_button, 1)
        # Undo/redo sit next to the gesture buttons as a second, discoverable
        # spelling of the strip's pair; both drive the SAME QUndoStack, so the
        # keyboard shortcut and the button can never disagree about the history.
        history = QHBoxLayout()
        history.setContentsMargins(theme.SPACE_SM, 0, theme.SPACE_SM, 0)
        history.addWidget(self._undo_button)
        history.addWidget(self._redo_button)
        history.addStretch(1)
        # Advanced technical detail sits behind a disclosure (Godot's Advanced
        # Settings idiom), so the default surface speaks cells and chunks.
        self._detail = TechnicalLabel("\u2014")
        self._detail_row = QWidget()
        detail_layout = QVBoxLayout(self._detail_row)
        detail_layout.setContentsMargins(theme.SPACE_SM, 0, theme.SPACE_SM, theme.SPACE_SM)
        detail_layout.setSpacing(0)
        detail_layout.addWidget(QLabel("Selected cell details"))
        detail_layout.addWidget(self._detail)

        editor_layout = QVBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(theme.SPACE_SM)
        editor_layout.addWidget(self._mode_badge)
        editor_layout.addWidget(self._read_only_detail)
        editor_layout.addLayout(editor_form)
        editor_layout.addLayout(history)
        editor_layout.addLayout(buttons)
        editor_layout.addLayout(reset_row)
        editor_layout.addWidget(self._detail_row)
        editor_layout.addWidget(self._structure_box)
        editor_layout.addWidget(self._create_chunk_button)
        editor_layout.addWidget(self._edit_chunk_button)
        editor_layout.addWidget(self._commit_button)
        editor_layout.addWidget(self._save_button)
        editor_layout.addStretch(1)
        self._editor_box = QWidget()
        self._editor_box.setObjectName("dbzLayoutEditor")
        self._editor_box.setLayout(editor_layout)

        self._name = QLabel("\u2014")
        self._name.setWordWrap(True)
        self._identity = QLabel("\u2014")
        self._dimensions = QLabel("\u2014")
        self._layer_count = QLabel("\u2014")
        self._layer_types = TechnicalLabel("\u2014")
        self._notes = QLabel("\u2014")
        self._notes.setWordWrap(True)
        self._notes.setProperty("dbzRole", "hint")
        info_form = QFormLayout()
        info_form.setContentsMargins(theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM)
        info_form.setHorizontalSpacing(theme.SPACE_MD)
        info_form.setVerticalSpacing(theme.SPACE_XS)
        info_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        info_form.addRow("Name", self._name)
        info_form.addRow("Map ID", self._identity)
        info_form.addRow("Dimensions", self._dimensions)
        info_form.addRow("Layers", self._layer_count)
        info_form.addRow("Layer types", self._layer_types)
        info_form.addRow("Notes", self._notes)
        info_box = QWidget()
        info_box.setLayout(info_form)
        self._info_box = info_box

        # Porymap keeps a named empty state (`label_NoEvents`) rather than a
        # blank pane; this is the browse-mode equivalent.
        self._empty_box = QWidget()
        empty_layout = QVBoxLayout(self._empty_box)
        empty_layout.setContentsMargins(
            theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD
        )
        empty_layout.setSpacing(theme.SPACE_SM)
        empty_state = QLabel("Browse mode")
        empty_state.setProperty("dbzRole", "fieldLabel")
        empty_layout.addWidget(empty_state)
        self._empty_explanation = QLabel(
            "This map is read-only. Switch Edit Layout on to reassign one "
            "256\u00d7256 chunk cell to another chunk a dominant layer of the map "
            "already uses."
        )
        self._empty_explanation.setProperty("dbzRole", "hint")
        self._empty_explanation.setWordWrap(True)
        # A wrapped label still reports the width of its longest word as its
        # minimum, and `256x256` is one long word: without releasing the floor the
        # label can be wider than the pane and its last line is clipped rather than
        # wrapped.
        self._empty_explanation.setMinimumWidth(0)
        empty_layout.addWidget(self._empty_explanation)
        empty_layout.addStretch(1)

        # The inspector reacts to the workspace mode; it does NOT offer a second
        # mode selector. It used to be a QTabWidget labelled "Layout | Browse |
        # Map", which repeated the Maps editor's own Browse/Layout/Objects strip and
        # left it genuinely unclear whether clicking a tab changed the editor mode,
        # an inspector section, or both. The workspace strip is authoritative, and
        # `_show_edit_groups` swaps this stack in response to it.
        self._inspector_stack = QStackedWidget()
        self._inspector_stack.addWidget(self._editor_box)
        self._inspector_stack.addWidget(self._empty_box)
        # `info_box` is deliberately NOT a page: it was the old "Map" tab. Its
        # contents are the map-support sentence, which the left pane's header now
        # states once, so adding it here would put the same fact back on screen as a
        # second, differently-labelled section.
        self._inspector_stack.setCurrentWidget(self._empty_box)
        self._inspector_tabs = self._inspector_stack

        right = QWidget()
        # A floor on the pane, so its wrapped explanatory text has room to wrap. A
        # QStackedWidget reports no minimum of its own, so without this the splitter
        # can squeeze the inspector until its prose is clipped.
        right.setMinimumWidth(240)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        self._inspector_header = PanelHeader("Inspector")
        right_layout.addWidget(self._inspector_header)
        right_layout.addWidget(self._inspector_stack, 1)
        self._right_pane = right

        # -- assembly ----------------------------------------------------------
        # Both side panes sit in their own scroll areas, as Porymap's do, so a
        # narrow window shortens what they can show instead of forcing the split
        # wider (which is what would squeeze the canvas beside them).
        left_scroll = QScrollArea()
        left_scroll.setWidget(left)
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(200)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)

        right_scroll = QScrollArea()
        right_scroll.setWidget(right)
        right_scroll.setWidgetResizable(True)
        right_scroll.setMinimumWidth(250)
        right_scroll.setFrameShape(QFrame.Shape.NoFrame)

        workspace = QSplitter(Qt.Orientation.Horizontal)
        workspace.addWidget(left_scroll)
        workspace.addWidget(self._centre_stack)
        workspace.addWidget(right_scroll)
        workspace.setStretchFactor(0, 0)
        workspace.setStretchFactor(1, 1)
        workspace.setStretchFactor(2, 0)
        workspace.setCollapsible(0, True)
        workspace.setCollapsible(1, False)
        workspace.setCollapsible(2, True)
        workspace.setSizes([250, 890, 300])
        self._workspace_split = workspace

        self._status = QLabel("Open a supported ROM to browse maps.")
        self._status.setProperty("dbzRole", "status")
        self._status.setWordWrap(True)
        self._status.setMinimumWidth(0)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(workspace, 1)
        # `_status` holds this editor's one status line and is deliberately NOT in
        # this layout: the shell owns the single physical status bar and mirrors
        # this text into it, so drawing it here too would state the same fact twice.
        self._status.setVisible(False)

        self._size_chunk_chooser()
        self._show_edit_groups(False)

    def _size_chunk_chooser(self) -> None:
        """Size the palette cells for a thumbnail *and* two text lines.

        Each item carries an explicit size hint rather than relying on the view's
        grid: with a grid, a two-line item is clipped to the grid cell that the
        *first* item's size hint produced, which silently elides the state tag
        (``current`` / ``original``) that marks the selected cell's chunk. The
        text height comes from the real font, so a scaled desktop or a larger UI
        font grows the cell instead of eating the tag.
        """
        line = self._chooser.fontMetrics().lineSpacing()
        self._chooser_cell = QSize(84, 48 + 2 * line + 10)
        # The palette's height is derived from one row of cells plus its header and
        # hint rather than guessed: a fixed height a few pixels short clipped the
        # second text line ("current") off the selected chunk, which is exactly the
        # tag the cell exists to show. The view is told to be exactly one cell tall
        # so the panel has no empty band under the row.
        chrome = (
            theme.PANEL_HEADER_HEIGHT
            + self._chooser_hint.sizeHint().height()
            + 3 * theme.SPACE_SM
        )
        self._chooser.setFixedHeight(self._chooser_cell.height())
        self._chooser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._palette_height = chrome + self._chooser_cell.height()
        self._chooser_box.setFixedHeight(self._palette_height)

    def _on_zoom_changed(self, scale: float) -> None:
        self._zoom_label.setText(f"{scale * 100:.0f}%")

    def _on_canvas_hover(self, x: int | None, y: int | None) -> None:
        """Turn a canvas point into the readout Porymap and Tiled both carry.

        Porymap's status bar reports ``X: %1, Y: %2`` plus the named element under
        the cursor and the scale; Tiled's reports ``%1, %2 [%3]`` plus the active
        layer in its permanent zone. This is the same information expressed in
        DragonByte Z's own nouns: map pixels, the chunk cell, and the chunk.
        """
        if x is None or y is None:
            text = ""
        else:
            parts = [f"{x}, {y} px"]
            slot = self._slot
            if self._edit_mode and slot is not None:
                cell = slot.grid.cell_at(x, y)
                if cell is not None:
                    parts.append(
                        f"cell {cell + 1} of {slot.grid.cell_count} "
                        f"(col {slot.grid.column_of(cell)}, row {slot.grid.row_of(cell)})"
                    )
                    pointer = slot.cells[cell].pointer
                    parts.append(self._chunk_name(slot.ordinal_of(pointer)))
            text = "  \u00b7  ".join(parts)
        if text != self._hover_text:
            self._hover_text = text
            self._update_status()

    def _on_chooser_toggled(self, expanded: bool) -> None:
        self._chooser.setVisible(bool(expanded))

    def _sync_chooser_presence(self) -> None:
        """Collapse the palette when there is nothing to choose.

        LDtk's palette only exists for a layer type that can use it. A read-only
        map has no layer to pick from, so leaving a full-height empty palette open
        under the canvas is dead space that also repeats the inspector's own
        explanation. The header stays, so the palette is still discoverable and the
        disclosure control does not move; everything below it is hidden, so the
        collapsed palette is *only* its header rather than a header with squeezed
        emptiness under it.
        """
        usable = self._edit_mode and self._slot is not None
        if usable:
            self._chooser_box.setFixedHeight(self._palette_height)
            self._chooser_hint.setVisible(True)
            self._chooser.setVisible(self._chooser_header.is_expanded())
        else:
            self._chooser_hint.setVisible(False)
            self._chooser.setVisible(False)
            self._chooser_box.setFixedHeight(theme.PANEL_HEADER_HEIGHT)

    # -- session wiring -------------------------------------------------------

    def on_session_changed(self) -> None:
        self._render_cache.clear()
        self._entries = {}
        self._current = None
        self._clear_layer_checks()
        # MAP-CHUNK-AUTHORING-001. Everything authored is derived from the image
        # that is being replaced - the chunk facade reads the canonical bytes, the
        # cached planes and chunk documents were resolved against them, and an
        # authored placement names a chunk this project may not even declare on the
        # other side of the change - so this is the event that clears it (CQA-05).
        self._clear_authored_state()
        # MAP-RESIZE-AND-LAYERS-001. The same rule for the structural half: a layer
        # record, a grid and a staged resize are claims about the image that is being
        # replaced, so a session change is the ONE event that clears them, and the
        # project's structural document is then read once for the new session.
        self._clear_structure_state()
        self._refresh_structure()
        self._reset_editor()
        # A new image is a new base: every history command's captured values came
        # from the image that is being replaced, so the stack cannot survive it.
        # This is the ONE event that clears the paint history (CQA-05).
        self._undo_stack.clear()
        self._list.blockSignals(True)
        self._list.clear()
        self._list.blockSignals(False)
        if self._session.rom_image is None:
            self._edit_toggle.setEnabled(False)
            self._show_placeholder("Open a supported ROM to browse its maps.")
            return
        try:
            index = mv.read_map_index(self._session.map_image)
        except mv.MapBrowserError as exc:
            self._edit_toggle.setEnabled(False)
            self._show_placeholder(f"Cannot read the map index: {exc}")
            QMessageBox.critical(self, "Map Browser", str(exc))
            return
        self._entries = {entry.index: entry for entry in index}
        self._populate_list()
        self._edit_toggle.setEnabled(True)
        # Restate the line for the session that just arrived. The label was created
        # carrying "Open a supported ROM to browse maps." and nothing overwrote it
        # until the user happened to select a map, so a loaded image still read as
        # though no image were open.
        self._update_status()

    def on_project_mutated(self) -> None:
        """A project mutation elsewhere: keep this session's staged layout edits.

        CQA-05. The layout session is built from the open image's own bytes
        (``MapLayoutEditor(self._session.rom_image)``) and the map records it
        edits come from those same bytes, so nothing a *project* write changes
        can invalidate it: ``_editor``, ``_saved``, ``_edit_mode``, ``_target``,
        ``_slot``, the selected cell and the uncommitted draft all survive an
        unrelated dialogue Apply, palette Apply, Scene NPC add or placement drag.

        Resetting the session belongs to ``on_session_changed`` alone, because
        only there is the base image - and with it the map records every pending
        edit points into - actually replaced. What a project write can still
        change on screen is bookkeeping *about* those edits: the per-map pending
        glyphs, the panel's own controls and the mode line. That is what is
        re-read here, from the live state rather than rebuilt.

        MAP-TILE-PAINT-001 adds one thing this must do: the committed project
        layer is re-read from the project, so a paint applied in another tab (or
        by an undo that rewrote the project) is reflected without discarding the
        staged gesture on top of it. The undo history is untouched - a project
        mutation is not a session change.

        MAP-CHUNK-AUTHORING-001 adds the same rule for the authored half: the
        project's chunk table and committed authored placements are re-read *only*
        here and in the reload below, never per repaint or per cell (CQA-07), and
        nothing the user staged - the staged authored placements, the staged chunk
        documents and the open chunk editor with its in-progress plane - is
        touched.

        MAP-RESIZE-AND-LAYERS-001 adds the structural half to that list: the
        project's structural document is re-read here, the staged structural edits
        (a staged resize, a staged new layer, a staged removal) survive untouched on
        top of it, and the one `MapResizer`/`MapPainter` over the merged document is
        rebuilt once - so an unrelated project write never costs a staged resize.
        """
        self.reload_project_layout()
        self._reselect_layer()
        self._mark_pending_rows()
        self._refresh_editor_state()
        self._update_status()

    def _populate_list(self) -> None:
        """Fill the map collection, with a per-map pending-edit glyph.

        Porymap shows unsaved state *per map, in the navigator*, so a user can see
        which of dozens of maps is dirty without opening any of them. The glyph
        trails the label so the leading name/identity text stays exactly as it
        reads today. Which maps are editable is deliberately not enumerated here:
        classifying all 452 maps up front would render the list slowly, and the
        inspector already states the state of the map that is actually open.
        """
        self._list.blockSignals(True)
        self._list.clear()
        for entry in sorted(self._entries.values(), key=lambda item: item.index):
            name = entry.name or ""
            text = f"{name}  \u00b7  map:{entry.index:04d}" if name else f"map:{entry.index:04d}"
            item = QListWidgetItem(text)
            item.setData(_IDENTITY_ROLE, entry.index)
            if name:
                item.setToolTip(name)
            self._list.addItem(item)
        self._list.blockSignals(False)
        self._list_count.setText(f"{len(self._entries)}")
        self._mark_pending_rows()
        self._apply_filter(self._search.text())

    def _mark_pending_rows(self) -> None:
        """Append a pending glyph to the rows whose maps carry unsaved edits."""
        pending: set[int] = set()
        if self._editor is not None:
            pending = {edit.map_index for edit in self._editor.edits()}
        # An authored placement is a staged map edit like any other, so the map it
        # belongs to is marked exactly the way a staged pointer paint marks it; a
        # chunk composed for a map is unsaved work for that map even before it is
        # placed, so its template's map is marked too.
        pending |= {key[0] for key in self._authored_cells}
        staged_chunks = self._pending_chunk_documents()
        for identity in staged_chunks:
            template = self._chunk_template_of(staged_chunks[identity])
            if template is not None:
                pending.add(template.map_index)
        for row in range(self._list.count()):
            item = self._list.item(row)
            base = item.data(_BASE_TEXT_ROLE)
            if base is None:
                base = item.text()
                item.setData(_BASE_TEXT_ROLE, base)
            item.setText(
                f"{base}  {theme.TITLE_DIRTY}"
                if item.data(_IDENTITY_ROLE) in pending
                else base
            )

    def _apply_filter(self, text: str) -> None:
        needle = text.strip().lower()
        for row in range(self._list.count()):
            item = self._list.item(row)
            index = item.data(_IDENTITY_ROLE)
            entry = self._entries.get(index)
            if entry is None:
                item.setHidden(bool(needle))
                continue
            name = (entry.name or "").lower()
            identity = f"map:{index:04d}".lower()
            item.setHidden(bool(needle) and needle not in name and needle not in identity)

    # -- selection and rendering ---------------------------------------------

    def _on_selection(self, current: QListWidgetItem | None, _previous=None) -> None:
        if current is None:
            return
        index = current.data(_IDENTITY_ROLE)
        if not isinstance(index, int) or index not in self._entries:
            return
        self._render_map(index)

    def _render_map(self, index: int) -> None:
        if self._session.rom_image is None:
            self._show_placeholder("Open a supported ROM to browse its maps.")
            return
        result = self._render_cache.get(index)
        if result is None:
            self._status.setText(f"Rendering map:{index:04d} from the verified ROM…")
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            # No processEvents(): yielding to the event loop mid-render lets a
            # selection change or window close re-enter this slot or delete the
            # tab, leaving stale state or a deleted C++ object.
            try:
                result = mv.render_map(
                    self._session.map_image,
                    index,
                    chunk_overrides=self._session.layout_overrides(index) or None,
                )
            except mv.MapBrowserError as exc:
                self._show_placeholder(f"map:{index:04d} could not be rendered: {exc}")
                QMessageBox.warning(self, "Map Browser", str(exc))
                return
            finally:
                QApplication.restoreOverrideCursor()
            self._render_cache[index] = result
            self._render_cache.move_to_end(index)
            while len(self._render_cache) > _MAX_RENDER_CACHE:
                self._render_cache.popitem(last=False)
        else:
            self._render_cache.move_to_end(index)
        self._current = result
        self._populate_layer_checks()
        self._sync_editor_for_map(index)
        # Pending edits made on an earlier visit must reappear with the map, or the
        # canvas would contradict the change list (and the ROM Save As writes).
        self._refresh_preview()
        self._populate_info()
        # The tab is visible by the time a user selects a map, so the viewport
        # already has its final geometry; fitting synchronously avoids a deferred
        # call that could outlive the canvas.
        self._canvas.fit_map()
        self._update_status()

    def _clear_layer_checks(self) -> None:
        # Drop the menu's actions first: a QWidgetAction owns the widget it is
        # given, so clearing the menu would delete a check box that the layout
        # still holds a Python reference to.
        for action in list(self._layers_menu.actions()):
            widget = action.defaultWidget()
            if widget is not None:
                action.setDefaultWidget(None)
                widget.setParent(self._layers_box)
            self._layers_menu.removeAction(action)
        for check in self._layer_checks.values():
            self._layers_layout.removeWidget(check)
            # Removing from a layout does not unparent: until the deferred delete
            # runs, an orphan would still paint at its stale geometry and overlap
            # the next map's own controls.
            check.setParent(None)
            check.deleteLater()
        self._layer_checks = {}
        self._layers_button.setEnabled(False)

    def _populate_layer_checks(self) -> None:
        """One checkable menu entry per graphical layer.

        The check box itself stays the control (so the visibility contract is
        unchanged and testable), but it lives inside a menu: the button face says
        only "Layers", so no amount of narrowing can turn "BG2 - Terrain field"
        into an unreadable stub.
        """
        self._clear_layer_checks()
        result = self._current
        if result is None:
            return
        for layer in result.layers:
            if not layer.graphical:
                continue
            label = _LAYER_LABELS.get(layer.classification, layer.classification)
            check = QCheckBox(f"BG{layer.slot} \u00b7 {label}")
            check.setChecked(True)
            check.setToolTip(layer.classification)
            check.toggled.connect(self._on_layer_toggled)
            self._layer_checks[layer.slot] = check
            self._layers_layout.addWidget(check)
            action = QWidgetAction(self._layers_menu)
            action.setDefaultWidget(check)
            self._layers_menu.addAction(action)
        # MAP-RESIZE-AND-LAYERS-001. A layer the project authored sits on a slot the
        # canonical image leaves unused, so the render reports no graphical layer for
        # it and it would have no way to be hidden or shown - and the structural
        # preview draws it as a normal dominant layer, which means it needs the same
        # control as one. A *resized* layer already has its check box above.
        drawn = set(self._layer_checks)
        for layer in self.structural_layers(result.index):
            if layer.slot in drawn or layer.identity is None:
                continue
            check = QCheckBox(
                f"BG{layer.slot} \u00b7 {self._structural_marker(layer)}"
            )
            check.setChecked(True)
            check.setToolTip(
                f"{layer.label} \u00b7 a layer this project authors; a build "
                "materializes it"
            )
            check.toggled.connect(self._on_layer_toggled)
            self._layer_checks[layer.slot] = check
            self._layers_layout.addWidget(check)
            action = QWidgetAction(self._layers_menu)
            action.setDefaultWidget(check)
            self._layers_menu.addAction(action)
        self._layers_button.setEnabled(bool(self._layer_checks))

    def _visible_layers(self) -> tuple[mv.MapBrowserLayer, ...]:
        result = self._current
        if result is None:
            return ()
        return tuple(
            layer
            for layer in result.layers
            if layer.graphical and self._layer_checks[layer.slot].isChecked()
        )

    def _show_composite(self, _checked: bool = False) -> None:
        result = self._current
        if result is None:
            return
        visible = self._visible_layers()
        if not visible:
            self._set_map_pixmap(QPixmap(), result.width, result.height)
            return
        try:
            indices = mv.compose(visible, result.width, result.height)
            pixmap = self._pixmap_from_indices(indices, result.width, result.height, result.palette)
        except mv.MapBrowserError as exc:
            QMessageBox.warning(self, "Map Browser", str(exc))
            return
        self._set_map_pixmap(pixmap, result.width, result.height)

    def _on_layer_toggled(self, _checked: bool = False) -> None:
        """Re-draw after a layer's visibility changed.

        MAP-RESIZE-AND-LAYERS-001: when the map has a project-authored grid the
        canvas is not the canonical composite, so hiding a layer has to rebuild the
        structural preview rather than the retail one - otherwise the toggled layer
        would keep painting exactly as before.
        """
        if self._current is not None and self.structural_layers(self._current.index):
            self._refresh_preview()
            return
        self._show_composite()

    def _pixmap_from_indices(self, indices: bytes, width: int, height: int, palette) -> QPixmap:
        rgba = mv.rgba(indices, palette)
        image = QImage(rgba, width, height, width * 4, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(image)

    def _set_map_pixmap(self, pixmap: QPixmap, width: int, height: int) -> None:
        if self._pixmap_item is not None and self._pixmap_item.scene() is self._scene:
            self._scene.removeItem(self._pixmap_item)
        self._pixmap_item = self._scene.addPixmap(pixmap)
        self._pixmap_item.setTransformationMode(Qt.TransformationMode.FastTransformation)
        self._pixmap_item.setZValue(0)
        # A null pixmap (every layer hidden) still gets a bounded scene so the
        # checkerboard remains visible and Fit stays a safe no-op.
        if pixmap.isNull():
            self._scene.setSceneRect(QRectF(0, 0, 640, 360))
        else:
            self._scene.setSceneRect(QRectF(0, 0, width, height))

    def _populate_info(self) -> None:
        result = self._current
        if result is None:
            return
        index = result.index
        self._name.setText(result.name or "(unnamed)")
        self._identity.setText(f"map:{index:04d}")
        structural = self.structural_layers(index)
        if structural:
            # MAP-RESIZE-AND-LAYERS-001. A project-authored grid is not the record
            # the canonical image holds, so stating only the rendered retail size
            # would describe a map the project no longer builds. The extent is the
            # camera's reach, which is what a resize actually raises.
            target = self._structure_target_for(index)
            extent = (
                f"{target.extent_x} × {target.extent_y} px map extent"
                if target is not None
                else f"{result.width} × {result.height} px"
            )
            self._dimensions.setText(extent)
        else:
            self._dimensions.setText(f"{result.width} × {result.height} px")
        self._layer_count.setText(
            f"{result.graphical_layer_count} graphical · {len(result.layers)} slot(s)"
        )
        lines = []
        for layer in result.layers:
            if layer.graphical:
                lines.append(f"BG{layer.slot} · {layer.classification} ({layer.width}×{layer.height})")
            else:
                lines.append(f"BG{layer.slot} · {layer.classification}")
        for layer in structural:
            lines.append(
                f"BG{layer.slot} · {self._structural_marker(layer)} "
                f"({layer.columns}×{layer.rows} chunks · {layer.width}×{layer.height} px)"
            )
        self._layer_types.setText("\n".join(lines))
        notes = list(result.warnings)
        if self._session.authored is not None:
            # A derivative says what it is, so a rendered layout is never mistaken
            # for the canonical one.
            notes.insert(0, self._session.authored.summary())
        self._notes.setText("\n".join(notes) if notes else "—")

    def _show_placeholder(self, message: str) -> None:
        self._current = None
        self._clear_layer_checks()
        self._forget_map_selection()
        self._scene.clear()
        self._pixmap_item = None
        self._grid_item = None
        text = QGraphicsSimpleTextItem(message)
        text.setBrush(theme.color("text_primary"))
        self._scene.addItem(text)
        self._scene.setSceneRect(QRectF(0, 0, 640, 360))
        self._status.setText(message)
        self._name.setText("—")
        self._identity.setText("—")
        self._dimensions.setText("—")
        self._layer_count.setText("—")
        self._layer_types.setText("—")
        self._notes.setText("—")
        # Nothing is selected any more, so the editor must say so rather than
        # keep a stale layer/cell that no map backs.
        self._refresh_editor_state()

    # -- layout editing: mode, target and cell selection ----------------------

    def _forget_map_selection(self) -> None:
        """Drop the per-map selection state (the session and images stay)."""
        self._target = None
        self._slot = None
        self._structure_slot = None
        self._selected_cell = None
        self._draft = None
        self._thumbnails = {}
        # The chunk editor belongs to one map's layer: its plane, its vocabulary and
        # its character block are all that map's, so a different map closes it and
        # clears the page. A staged chunk survives in `_staged_chunks` and comes
        # back from the palette of the map it was composed against.
        self._close_chunk_editor_page()
        self._clear_chunk_editor_state()
        self._clear_grid_item()
        self._chooser.blockSignals(True)
        self._chooser.clear()
        self._chooser.blockSignals(False)
        self._chooser_hint.setText("No editable layer is selected on this map.")
        self._layer_combo.blockSignals(True)
        self._layer_combo.clear()
        self._layer_combo.blockSignals(False)
        self._layer_rows_signature = None
        self._cell_label.setText("No cell selected")
        self._chunk_label.setText("")
        self._detail.setText("")

    def _reset_editor(self) -> None:
        """Drop all edit-session state; the ROM, and so the base, has changed."""
        self._editor = None
        self._editor_error = None
        self._target = None
        self._slot = None
        self._structure_slot = None
        self._selected_cell = None
        self._draft = None
        self._layout = LayoutSession()
        self._thumbnails = {}
        self._brush_ordinal = None
        self._brush_pointer = None
        self._stroke = []
        self._stroke_previous = {}
        self._stroke_applied = {}
        self._stroke_first = None
        self._stroke_last = None
        self._stroke_active = False
        self._thumbnails = {}
        self._brush_ordinal = None
        self._brush_pointer = None
        # A new ROM starts in view mode: leaving the toggle checked would claim an
        # editing mode for an image the tab has not judged yet.
        self._edit_mode = False
        self._edit_toggle.blockSignals(True)
        self._edit_toggle.setChecked(False)
        self._edit_toggle.blockSignals(False)
        self._show_edit_groups(False)
        self._close_chunk_editor_page()
        self._clear_grid_item()
        self._chooser.clear()
        self._chooser_hint.setText("Select a map to see its chunks.")
        self._mode_badge.setText("VIEW MODE · read-only")
        self._mode_badge.setStyleSheet("")
        self._cell_label.setText("No cell selected")
        self._chunk_label.setText("")
        self._change_label.setText("No layout changes")
        self._detail.setText("")
        self._layer_combo.blockSignals(True)
        self._layer_combo.clear()
        self._layer_combo.blockSignals(False)
        self._layer_rows_signature = None

    def _editor_session(self) -> MapLayoutEditor | None:
        """The edit session for the open ROM, or None with the reason recorded."""
        if self._editor is not None or self._editor_error is not None:
            return self._editor
        if self._session.rom_image is None:
            self._editor_error = "no ROM is open"
            return None
        if self._session.authored is not None:
            # Its layout is shown by rendering the reconstructed canonical bytes with
            # the derivative's verified edits applied; further editing belongs to the
            # canonical image this was derived from.
            self._editor_error = (
                "this image is a verified DragonByte Z layout derivative of the "
                "canonical ROM; open the canonical ROM to make further layout edits"
            )
            return None
        try:
            # The project's committed layout is read FIRST and handed to the
            # session as its floor, so a project that was closed and reopened
            # shows its painted layout immediately rather than only after the
            # first project mutation. The base image is still the canonical one.
            self._editor = MapLayoutEditor(self._session.rom_image)
            set_floor = getattr(self._editor, "set_floor", None)
            if set_floor is not None:
                set_floor(self._project_floor(self._session.rom_image))
        except MapLayoutEditError as exc:
            # Unsupported image: the browser keeps working, read-only.
            self._editor_error = str(exc)
        return self._editor

    def _project_floor(self, image: bytes) -> dict[tuple[int, int, int], int]:
        """The committed project *pointer* paints for the open project.

        Empty when no project is open or the project paints no layout. A project
        that cannot be read is reported and treated as empty here; the surface
        then says so in its status line rather than presenting an unreadable
        project as an unpainted one.

        MAP-CHUNK-AUTHORING-001: a layout cell may now hold an authored chunk
        *identity* instead of an ordinal. Those cells are deliberately excluded
        here - the layout session's floor is a pointer map, and an identity has no
        pointer - and travel through the render overrides instead
        (:meth:`_committed_authored_overrides`), where a plane can express them.
        """
        if self._session.project_dir is None:
            return {}
        structural = self.structural_pairs()
        try:
            ordered = {
                key: value
                for key, value in read_layout_edits(self._session.project_dir).cells().items()
                if type(value) is int and (key[0], key[1]) not in structural
            }
        except _PROJECT_READ_ERRORS as exc:
            self._publish_status(f"Project layout could not be read: {exc}")
            return {}
        if not ordered:
            return {}
        try:
            # The structural session's own painter when there is one, so resolving
            # the floor costs no second read of the map table; the document it was
            # built over is the one just read (CQA-07).
            painter = self._painter or MapPainter(
                image, structure=self.structure_document()
            )
            return painter.pointer_edits(ordered)
        except MapPaintError as exc:
            # A project that names a cell this image cannot carry is a real
            # problem, and it is named rather than dropped: the build refuses it
            # too, so a silent empty floor here would hide it until build time.
            self._publish_status(f"Project layout does not apply to this ROM: {exc}")
            return {}

    def _sync_editor_for_map(self, index: int) -> None:
        """Re-point the edit surface at the newly selected map."""
        self._forget_map_selection()
        # CQA-26: the read failure belonged to the cell it was measured on, and
        # this is the other half of the layer-switch reset - the two early
        # returns below never reach `_select_layer`, and `_refresh_editor_state`
        # republishes the field ahead of every other fact.
        self._cell_read_error = ""
        editor = self._editor_session()
        if editor is None:
            self._editor_box.setToolTip(self._editor_error or "")
            self._refresh_editor_state()
            return
        # The base image has not changed but the project may have: re-read the
        # committed layout before the layer is resolved, so a project painted
        # since the last look is what the user sees. This does not touch staged
        # work.
        self.reload_project_layout()
        try:
            self._target = editor.target(index)
        except MapLayoutEditError as exc:
            self._editor_box.setToolTip(str(exc))
            self._target = None
            self._refresh_editor_state()
            return
        self._editor_box.setToolTip("")
        self._populate_layer_combo()
        self._refresh_editor_state()

    def _layer_rows(self) -> tuple[tuple[int, str, "StructuralLayer | None"], ...]:
        """The Layer row's own rows - ``(slot, label, project layer)`` - with no I/O.

        One computation behind both the combo and the "has anything actually
        changed?" question a project mutation asks, so the two cannot disagree
        about what this map offers. The project layer is part of the row and not
        only its label: a resize whose dimensions are unchanged but whose
        initialization chunk is not carries the same label and a different grid.
        """
        if self._target is None or self._current is None:
            return ()
        index = self._current.index
        structural = {layer.slot: layer for layer in self.structural_layers(index)}
        rows: list[tuple[int, str, "StructuralLayer | None"]] = []
        for slot in self._target.editable_slots:
            layer = structural.get(slot.slot)
            label = (
                slot.label
                if layer is None
                else f"{layer.label} \u00b7 {self._structural_marker(layer)}"
            )
            rows.append((slot.slot, label, layer))
        listed = [row[0] for row in rows]
        for slot, layer in sorted(structural.items()):
            if not layer.editable or slot in listed:
                continue
            if self._structural_layout_slot(layer) is None:
                continue
            rows.append(
                (slot, f"{layer.label} \u00b7 {self._structural_marker(layer)}", layer)
            )
        return tuple(rows)

    def _populate_layer_combo(
        self, select: int | None = None, *, preserve: bool = False
    ) -> None:
        """Fill the Layer row from the canonical slots AND the project's own grids.

        MAP-RESIZE-AND-LAYERS-001: a slot the project resized, or one whose layer the
        project authored, is a paintable layer of this map like any other - the
        requirement that a new layer be selectable in the existing map editor - so it
        is offered here, marked so a person can tell a project-authored grid from a
        retail one. Nothing here reads a file: the structural rows come from the
        cached merged document.

        ``preserve`` is for `_reselect_layer` alone, which runs on every project
        mutation: if the rows are exactly the ones already listed the editor is left
        untouched, because rebuilding it resets the brush, the picked cell and the
        uncommitted draft - the user's state, not the document's. Rebuilding on a
        mutation is what lost a staged authored-chunk brush (the tracked
        MAP-CHUNK-AUTHORING-001 CQA-05 node) and it is the same rule this ticket's
        own staged structural edits answer to. When a row really has changed the
        combo is refilled and the selection re-pointed exactly as before.
        """
        rows = self._layer_rows()
        if preserve and rows == self._layer_rows_signature:
            return
        self._layer_combo.blockSignals(True)
        self._layer_combo.clear()
        for slot, label, _layer in rows:
            self._layer_combo.addItem(label, slot)
        self._layer_combo.blockSignals(False)
        self._layer_rows_signature = rows
        wanted = select
        if wanted is None and self._layer_combo.count():
            wanted = self._layer_combo.itemData(0)
        if wanted is not None:
            row = self._layer_combo.findData(wanted)
            if row >= 0:
                self._layer_combo.blockSignals(True)
                self._layer_combo.setCurrentIndex(row)
                self._layer_combo.blockSignals(False)
        # The selection is applied explicitly rather than through the combo's own
        # signal: refilling a combo whose index does not change emits nothing, and a
        # structural change must re-point the editor at the new grid even when the
        # slot number is the same.
        if self._layer_combo.count():
            self._select_layer(self._layer_combo.itemData(self._layer_combo.currentIndex()))
        else:
            self._slot = None
            self._structure_slot = None
            self._populate_chooser()

    def _select_layer(self, layer_slot: int | None) -> None:
        """Point the editor and the grid overlay at one dominant layer slot.

        MAP-RESIZE-AND-LAYERS-001: a slot whose grid the project owns - a resized
        layer, or one the project authored - is resolved through the structural
        authority into the same slot type the canonical path uses, so the grid
        overlay, the cell readout and the palette all state the *project's* geometry
        and its own permitted chunks rather than a retail record that is not what a
        build will emit.
        """
        self._draft = None
        self._slot = None
        self._structure_slot = None
        self._selected_cell = None
        self._thumbnails = {}
        self._brush_ordinal = None
        self._brush_pointer = None
        self._brush_authored = None
        # CQA-26: the read failure belongs to the cell it was measured on, so a
        # layer switch drops it rather than republishing it as the new layer's
        # status; the next read sets it again if the new layer also fails.
        self._cell_read_error = ""
        if self._target is None or layer_slot is None:
            self._clear_grid_item()
            self._populate_chooser()
            return
        project_layer = (
            self.structural_layer(self._current.index, layer_slot)
            if self._current is not None
            else None
        )
        if project_layer is not None:
            slot = self._structural_layout_slot(project_layer)
            self._structure_slot = project_layer if slot is not None else None
        else:
            slot = self._target.slots[layer_slot]
        self._slot = slot if slot is not None and slot.editable else None
        if self._slot is not None:
            # An edited layer must stay visible: a hidden layer would silently
            # swallow the preview the user is judging.
            check = self._layer_checks.get(layer_slot)
            if check is not None and not check.isChecked():
                check.setChecked(True)
            self._selected_cell = 0
            # A sensible default brush: the second value this layer uses, because
            # the first is usually the one already filling the cells a user wants
            # to change. The palette shows it as the selected paint value.
            self._brush_ordinal = 2 if len(self._slot.choices) > 1 else None
            self._brush_pointer = self._lookup_pointer(self._brush_ordinal or 0)
        self._install_grid_item()
        self._populate_chooser()
        self._sync_chooser_selection()

    def _install_grid_item(self) -> None:
        self._clear_grid_item()
        if not self._edit_mode or self._slot is None:
            return
        self._grid_item = ChunkGridOverlay(
            self._slot.grid,
            self._on_cell_clicked,
            on_stroke_begin=self._begin_stroke,
            on_stroke_end=self._end_stroke,
        )
        self._scene.addItem(self._grid_item)
        self._grid_item.set_selected(self._selected_cell)

    def _on_grid_hover(self, cell: int | None) -> None:
        """Report the cell under the pointer, for the canvas status readout.

        The canvas already reports map pixels; this is the one thing a painter
        needs and pixels cannot give - which cell, and which chunk is in it.
        Cached and published through the same line the canvas hover uses, so the
        two never fight over it.
        """
        if not self._edit_mode or self._slot is None or cell is None:
            self._hover_cell = None
            return
        authored = self._authored_value_at(self._current.index, self._slot.slot, cell)
        if authored is not None:
            name = self._authored_name(authored)
        else:
            pointer = self._working_pointer(self._slot.slot, cell)
            name = (
                _UNREAD_CELL
                if pointer == _UNREAD_POINTER
                else self._chunk_name(self._slot.ordinal_of(pointer))
            )
        self._hover_cell = (
            f"BG{self._slot.slot} cell {cell + 1}/{self._slot.grid.cell_count} · {name}"
        )

    def _clear_grid_item(self) -> None:
        if self._grid_item is not None and self._grid_item.scene() is self._scene:
            self._scene.removeItem(self._grid_item)
        self._grid_item = None

    def enter_edit_layout(self) -> None:
        """Switch this browser into its Layout mode.

        The Maps editor's mode switch calls this rather than flipping the check box
        directly, so the toggle, the grid overlay and the inspector page all move
        together exactly as they do when a user clicks the toggle.
        """
        self._edit_toggle.setChecked(True)

    def leave_edit_layout(self) -> None:
        """Switch this browser back to read-only browsing."""
        self._edit_toggle.setChecked(False)

    def _on_edit_mode_toggled(self, checked: bool) -> None:
        self._edit_mode = bool(checked)
        self._draft = None
        self._show_edit_groups(self._edit_mode)
        self._install_grid_item()
        if self._edit_mode and self._selected_cell is None and self._slot is not None:
            self._selected_cell = 0
            if self._grid_item is not None:
                self._grid_item.set_selected(0)
        if self._edit_mode:
            self._canvas.setFocus()
        self._refresh_editor_state()

    def _show_edit_groups(self, visible: bool) -> None:
        """Swap the inspector pane's page and show or hide the chunk palette.

        This is the one place the mode changes which surfaces exist, and it is
        deliberately a *swap* rather than a stack of greyed panels: Porymap swaps
        its whole right-hand page per tool context, and LDtk's palette only
        exists for a layer type that can use it. The hidden-by-default empty
        state stands in until something is selected.
        """
        visible = bool(visible)
        self._editor_box.setVisible(visible)
        self._chooser_box.setVisible(visible)
        self._empty_box.setVisible(not visible)
        # While the Maps editor owns mode selection, the browser's own Edit Layout
        # toggle is hidden rather than repeated: the mode strip already says which
        # mode is on, and the same action must not be represented twice on one
        # screen. The toggle stays the single implementation both callers drive.
        self._edit_toggle.setVisible(not self._modes_owned_by_host)
        if visible:
            self._inspector_stack.setCurrentWidget(self._editor_box)
        else:
            self._inspector_stack.setCurrentWidget(self._empty_box)

    def set_modes_owned_by_host(self, owned: bool) -> None:
        """Let the Maps editor own mode selection, so this tab stops showing it."""
        self._modes_owned_by_host = bool(owned)
        self._edit_toggle.setVisible(not self._modes_owned_by_host)

    def _on_layer_changed(self, _row: int) -> None:
        self._select_layer(self._layer_combo.currentData())
        self._refresh_editor_state()

    def _set_tool(self, tool: str) -> None:
        """Select the paint or eyedropper tool."""
        self._tool = tool
        self._paint_tool.setChecked(tool == _TOOL_PAINT)
        self._pick_tool.setChecked(tool == _TOOL_PICK)
        self._update_status()

    def _on_cell_clicked(self, cell: int) -> None:
        """One cell was pressed or entered during a gesture.

        The tool decides what that means: the eyedropper takes the cell's chunk
        as the brush and changes nothing, and the paint tool stages the brush
        into the cell.

        The grid overlay brackets a gesture - it calls :meth:`_begin_stroke` on
        press, this method once per cell the pointer enters, and
        :meth:`_end_stroke` on release - so a drag stages every cell it crosses
        and raises ONE undo command for the gesture. A caller that reaches this
        path without an open gesture (a test driving the cell callback directly,
        or an accessory button) gets a complete single-cell gesture rather than a
        half-open one; that is decided by `_stroke_active`, not by guessing.
        """
        if self._slot is None or not self._slot.grid.contains(cell):
            return
        own_gesture = not self._stroke_active
        if own_gesture:
            self._begin_stroke()
        self._selected_cell = cell
        if self._grid_item is not None:
            self._grid_item.set_selected(cell)
        if self._tool == _TOOL_PICK or self._alt_pick:
            self._pick_cell(cell)
            self._sync_chooser_selection()
            self._refresh_editor_state()
            if own_gesture:
                self._end_stroke()
            return
        self._paint_cell(cell)
        self._draft = None
        if own_gesture:
            self._end_stroke()
        self._sync_chooser_selection()
        self._refresh_preview()
        self._refresh_editor_state()

    def _lookup_pointer(self, ordinal: int) -> int | None:
        """The chunk pointer a 1-based ordinal names, in the current layer.

        The single translation between the ordinal a project persists and the
        pointer the session's render and edit paths take; both come from the
        session's own ``LayoutSlot`` vocabulary, so a painted value resolves
        exactly the way the write path would resolve it.
        """
        slot = self._slot
        if slot is None or type(ordinal) is not int:
            return None
        if not 1 <= ordinal <= len(slot.choices):
            return None
        return slot.choices[ordinal - 1]

    def _ordinal_of_pointer(self, pointer: int) -> int | None:
        slot = self._slot
        return None if slot is None else slot.ordinal_of(pointer)

    def _brush_key(self) -> int | None:
        """The brush as the stored ordinal a project persists, or None."""
        return self._brush_ordinal

    def set_brush_ordinal(self, ordinal: int | None) -> None:
        """Choose the paint value by its stored ordinal (1-based)."""
        if ordinal is None:
            self._brush_ordinal = None
            self._brush_pointer = None
        else:
            self._brush_ordinal = ordinal
            self._brush_pointer = self._lookup_pointer(ordinal)
        self._brush_authored = None
        self._sync_chooser_selection()
        self._refresh_editor_state()

    def set_authored_brush(self, identity: str) -> bool:
        """Choose a project-authored chunk as the paint value.

        The authored counterpart of :meth:`set_brush_ordinal`, and the call the
        chunk editor's "Use as paint brush" makes. False when the identity is not
        a chunk this session can place, in which case nothing changes.
        """
        return self._set_authored_brush(identity)

    def _set_authored_brush(self, identity: str, *, publish: bool = True) -> bool:
        if identity not in self.placeable_authored(None):
            if publish:
                self._publish_status(
                    f"{identity!r} is not an authored chunk this session can place."
                )
            return False
        self._brush_authored = identity
        self._brush_pointer = None
        self._brush_ordinal = None
        # An authored chunk that has never been placed has no palette row yet, so
        # the chooser is refilled to show which value is now the brush rather than
        # leaving the selection on a retail chunk the user is no longer painting.
        if self._chooser_row_for_authored(identity) is None:
            self._populate_chooser()
        self._sync_chooser_selection()
        if publish:
            self._refresh_editor_state()
        return True

    def pick_brush_from_cell(self, cell: int) -> None:
        """Eyedropper, as one call: take a cell's chunk as the brush."""
        if self._slot is None or not self._slot.grid.contains(cell):
            return
        self._selected_cell = cell
        if self._grid_item is not None:
            self._grid_item.set_selected(cell)
        self._pick_cell(cell)
        self._sync_chooser_selection()
        self._refresh_editor_state()

    def _pick_cell(self, cell: int) -> None:
        """Take one cell's current chunk as the brush, without editing it.

        MAP-CHUNK-AUTHORING-001: a cell may hold an authored placement rather than
        a pointer, and picking it must give the authored chunk back - otherwise the
        eyedropper would report "no chunk this layer uses" over a cell the author
        can plainly see holds one.
        """
        if self._slot is None:
            return
        authored = self._authored_value_at(self._current.index, self._slot.slot, cell)
        if authored is not None:
            self._set_authored_brush(authored, publish=False)
            self._publish_status(
                f"Picked {self._authored_name(authored)} as the paint value."
            )
            return
        pointer = self._working_pointer(self._slot.slot, cell)
        if pointer == _UNREAD_POINTER:
            self._publish_status(self._cell_read_error or _UNREAD_CELL_ACTION)
            return
        ordinal = self._slot.ordinal_of(pointer)
        if ordinal is None:
            self._publish_status(
                "That cell holds no chunk this layer uses, so it is not a brush value."
            )
            return
        self._brush_authored = None
        self._brush_pointer = pointer
        self._brush_ordinal = ordinal
        self._publish_status(f"Picked Chunk {ordinal} as the paint value.")

    def _paint_cell(self, cell: int) -> bool:
        """Stage the brush into one cell; True when the cell's value changed.

        A cell already showing the brush value stages nothing and reports False:
        painting a cell the brush already matches is not a change, so it must not
        enter the history or mark the map dirty.

        The cell's PRE-GESTURE value is recorded before anything is staged, and
        only once per gesture. It has to be the value from before the whole
        stroke, not from before this call: a drag that re-crosses a cell it has
        already painted would otherwise record the stroke's own earlier value as
        that cell's original, and one undo would leave the map mid-stroke rather
        than restoring it.

        MAP-CHUNK-AUTHORING-001: when the brush is an authored chunk the cell is
        staged in the tab's own authored placement map instead of the pointer-based
        layout session, because that session cannot express a chunk with no
        address. Nothing else about the gesture changes: the same stroke record,
        the same changed-cell rule, the same one-command-per-drag history.
        """
        slot = self._slot
        if slot is None or self._editor is None or self._current is None:
            return False
        if self._structure_slot is not None and self._brush_authored is None:
            # A project-authored grid travels through the structural staging table:
            # only its retail cells have a four-byte field, and a cell that exists
            # only in the authored grid has none at all - so the whole layer is
            # staged semantically and written by `set_layout_cells`, which reads the
            # project's own structure.
            return self._stage_structural_paint(cell)
        if self._brush_authored is not None:
            return self._stage_authored_placement(cell)
        pointer = self._brush_pointer
        if pointer is None:
            self._publish_status("Choose a chunk in the palette first.")
            return False
        before = self._working_pointer(slot.slot, cell)
        if before == _UNREAD_POINTER:
            # CQA-26: staging a paint whose "previous" value was never read would
            # record a fabricated original and hand it back to the SDK on revert.
            self._publish_status(self._cell_read_error or _UNREAD_CELL_ACTION)
            return False
        if cell not in self._stroke_previous:
            self._stroke_previous[cell] = before
        # The gesture's span is where the pointer WENT, not only where it changed
        # something: a drag that starts on a cell already holding the brush is
        # still the same gesture, and the next press on that cell must merge with
        # it rather than start a second history entry.
        if self._stroke_first is None:
            self._stroke_first = cell
        self._stroke_last = cell
        if pointer == before:
            return False
        try:
            edit = self._editor.set_cell(self._current.index, slot.slot, cell, pointer)
        except _EDIT_ERRORS as exc:
            QMessageBox.warning(self, "Map paint", str(exc))
            return False
        if edit is None:
            # The session already agreed with this cell: nothing staged.
            return False
        if cell not in self._stroke:
            self._stroke.append(cell)
            self._stroke_applied[cell] = pointer
        return True

    def _stage_authored_placement(self, cell: int) -> bool:
        """Stage the authored brush into one cell; True when the cell changed.

        The staged record is the cell's authored value before the gesture - the
        staged identity, else the project's committed one, else None - so an undo
        restores exactly what the author had rather than clearing the cell.
        """
        slot = self._slot
        identity = self._brush_authored
        if slot is None or identity is None:
            return False
        key = (self._current.index, slot.slot, cell)
        before = self._authored_value_at(*key)
        if cell not in self._stroke_previous:
            self._stroke_previous[cell] = before
        if self._stroke_first is None:
            self._stroke_first = cell
        self._stroke_last = cell
        if before == identity:
            return False
        self._authored_cells[key] = identity
        if cell not in self._stroke:
            self._stroke.append(cell)
            self._stroke_applied[cell] = identity
        return True

    def _stage_structural_paint(self, cell: int) -> bool:
        """Stage the brush ordinal into one cell of a project-authored grid.

        The same shape the authored-chunk placement uses, for the same reason: the
        staged value is the cell's *staged* ordinal before the gesture - ``None``
        meaning "this cell carries no authored paint and shows the grid's own
        default" - so one undo restores exactly what the author had rather than
        rewriting a cell that was never painted.
        """
        layer = self._structure_slot
        ordinal = self._brush_ordinal
        if layer is None or ordinal is None:
            self._publish_status("Choose a chunk in the palette first.")
            return False
        key = (self._current.index, layer.slot, cell)
        before = self._structural_staged_value(layer, cell)
        if cell not in self._stroke_previous:
            self._stroke_previous[cell] = before
        if self._stroke_first is None:
            self._stroke_first = cell
        self._stroke_last = cell
        # The cell's effective value is the staged one, else the project's, else the
        # grid's own default - and painting the value a cell already shows is not a
        # change, so it stages nothing and enters no history.
        if self._structural_ordinal(layer, cell) == ordinal:
            return False
        self._structural_cells[key] = ordinal
        if cell not in self._stroke:
            self._stroke.append(cell)
            self._stroke_applied[cell] = ordinal
        return True

    def _begin_stroke(self) -> None:
        """Open a gesture record; called by the grid overlay on press."""
        self._stroke = []
        self._stroke_previous = {}
        self._stroke_applied = {}
        self._stroke_first = None
        self._stroke_last = None
        self._stroke_active = True

    def begin_paint_stroke(self) -> None:
        """Open a gesture explicitly, for a caller driving the surface without a mouse."""
        self._begin_stroke()

    def paint_cell(self, cell: int) -> bool:
        """Paint one cell as part of the current gesture; True when it changed."""
        changed = self._paint_cell(cell)
        if changed:
            self._selected_cell = cell
            if self._grid_item is not None:
                self._grid_item.set_selected(cell)
        return changed

    def end_paint_stroke(self) -> None:
        """Close the current gesture and raise it on the undo stack."""
        self._end_stroke()

    def _end_stroke(self) -> None:
        """Close the current gesture and raise it on the undo stack.

        The command records only the cells whose value actually changed, so a
        drag that re-crosses a cell it already painted, or that sweeps cells it
        leaves at their current value, produces one tightly-scoped history entry.
        An empty gesture - every cell already showing the brush - pushes nothing
        at all, which is the "painting the same effective value creates no
        history" rule.
        """
        self._stroke_active = False
        changed = [
            cell
            for cell in self._stroke
            if self._stroke_previous.get(cell) != self._stroke_applied.get(cell)
        ]
        first, last = self._stroke_first, self._stroke_last
        # Captured before the gesture record is cleared: the command needs the
        # values, and the record is about to be reused by the next gesture.
        previous = {cell: self._stroke_previous[cell] for cell in changed}
        applied = {cell: self._stroke_applied[cell] for cell in changed}
        self._stroke = []
        self._stroke_previous = {}
        self._stroke_applied = {}
        self._stroke_first = None
        self._stroke_last = None
        if not changed or self._slot is None or self._current is None:
            self._refresh_editor_state()
            return
        if self._brush_authored is not None:
            # An authored brush travels through the tab's own placement map, not
            # the pointer-based session, so it raises its own command on the same
            # stack. The merge key is the authored identity, which can never equal
            # a pointer, so a placement stroke cannot merge into a paint stroke.
            command = AuthoredPlaceCommand(
                self,
                map_index=self._current.index,
                layer_slot=self._slot.slot,
                cells=changed,
                previous=previous,
                applied=applied,
            )
            command.set_keys(self._brush_authored, first, last)
        elif self._structure_slot is not None:
            # A project-authored grid raises the structural command: same stack,
            # same one-gesture shape, its own merge class id, and a merge key that
            # names the ordinal it painted.
            command = StructuralPaintCommand(
                self,
                map_index=self._current.index,
                layer_slot=self._slot.slot,
                cells=changed,
                previous=previous,
                applied=applied,
            )
            command.set_keys(self._brush_ordinal, first, last)
        else:
            command = PaintCellsCommand(
                self,
                map_index=self._current.index,
                layer_slot=self._slot.slot,
                cells=changed,
                previous=previous,
                applied=applied,
            )
            # The gesture identity: one brush, and the cells the pointer started
            # and ended on, so only a continuation of THIS drag merges into this
            # command.
            command.set_keys(self._brush_pointer, first, last)
        self._undo_stack.push(command)
        self._refresh_editor_state()

    def _reapply_paint(self, command: "PaintCellsCommand") -> None:
        """Re-apply one already-recorded gesture (redo, or a merged stroke)."""
        if self._editor is None:
            return
        for cell, pointer in command.applied.items():
            try:
                self._editor.set_cell(command.map_index, command.layer_slot, cell, pointer)
            except _EDIT_ERRORS as exc:
                QMessageBox.warning(self, "Map paint", str(exc))
                return
        self._after_paint_change(command.map_index)

    def _reverse_paint(self, command: "PaintCellsCommand") -> None:
        """Undo one gesture: put every cell back to the value it held before.

        A cell whose pre-gesture value IS the value the cell's base holds is
        un-staged - the staged work is removed, which is what an undo of a paint
        means - and a cell whose pre-gesture value was itself a paint is staged
        back to it. Both go through the session; the tab owns no edit state.
        """
        if self._editor is None:
            return
        for cell, pointer in command.previous.items():
            try:
                base = self._editor.committed_pointer(
                    command.map_index, command.layer_slot, cell
                )
                if pointer == base:
                    self._editor.clear_cell(command.map_index, command.layer_slot, cell)
                else:
                    self._editor.set_cell(
                        command.map_index, command.layer_slot, cell, pointer
                    )
            except _EDIT_ERRORS as exc:
                QMessageBox.warning(self, "Map paint", str(exc))
                return
        self._after_paint_change(command.map_index)

    def _reapply_authored_place(self, command: "AuthoredPlaceCommand") -> None:
        """Re-apply one staged authored placement gesture (redo / merged stroke)."""
        for cell, identity in command.applied.items():
            self._authored_cells[(command.map_index, command.layer_slot, cell)] = identity
        self._after_paint_change(command.map_index)

    def _reverse_authored_place(self, command: "AuthoredPlaceCommand") -> None:
        """Undo one authored placement gesture, cell by cell.

        A cell whose previous value was itself a staged placement gets it back; a
        cell that had none has the staged placement removed, so the project's own
        committed value (authored or retail) is what the cell shows again.
        """
        for cell, identity in command.previous.items():
            key = (command.map_index, command.layer_slot, cell)
            if identity is None:
                self._authored_cells.pop(key, None)
            else:
                self._authored_cells[key] = identity
        self._after_paint_change(command.map_index)

    def _after_paint_change(self, map_index: int) -> None:
        """Re-render and re-sync after history moved the staged edit set."""
        if self._current is not None and self._current.index == map_index:
            self._refresh_preview()
        else:
            self._mark_pending_rows()
        self._refresh_editor_state()

    def _reapply_structural_paint(self, command: "StructuralPaintCommand") -> None:
        """Re-apply one staged structural-grid gesture (redo / merged stroke)."""
        for cell, ordinal in command.applied.items():
            self._structural_cells[(command.map_index, command.layer_slot, cell)] = ordinal
        self._after_paint_change(command.map_index)

    def _reverse_structural_paint(self, command: "StructuralPaintCommand") -> None:
        """Undo one structural-grid gesture, cell by cell.

        A cell whose previous value was itself a staged paint gets it back; a cell
        that had none has the staged paint removed, so the grid's own default - the
        retail chunk on a retail cell, the initialization chunk on a grown one - is
        what the cell shows again.
        """
        for cell, ordinal in command.previous.items():
            key = (command.map_index, command.layer_slot, cell)
            if ordinal is None:
                self._structural_cells.pop(key, None)
            else:
                self._structural_cells[key] = ordinal
        self._after_paint_change(command.map_index)

    def _move_cell_selection(self, delta_column: int, delta_row: int) -> None:
        slot = self._slot
        if slot is None:
            return
        grid = slot.grid
        if self._selected_cell is None:
            self._on_cell_clicked(0)
            return
        column = grid.column_of(self._selected_cell) + delta_column
        row = grid.row_of(self._selected_cell) + delta_row
        if not 0 <= column < grid.columns or not 0 <= row < grid.rows:
            return
        self._on_cell_clicked(row * grid.columns + column)

    def _on_canvas_key(self, event) -> bool:
        """Edit-mode keys on the map canvas; returns True when the key was used."""
        if not self._edit_mode or self._slot is None:
            return False
        key = event.key()
        if key == Qt.Key.Key_Left:
            self._move_cell_selection(-1, 0)
            return True
        if key == Qt.Key.Key_Right:
            self._move_cell_selection(1, 0)
            return True
        if key == Qt.Key.Key_Up:
            self._move_cell_selection(0, -1)
            return True
        if key == Qt.Key.Key_Down:
            self._move_cell_selection(0, 1)
            return True
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._apply_draft()
            return True
        if key == Qt.Key.Key_Escape:
            self._draft = None
            self._sync_chooser_selection()
            self._refresh_preview()
            self._refresh_editor_state()
            return True
        return False

    # -- layout editing: chunk chooser ---------------------------------------

    def _populate_chooser(self) -> None:
        """Fill the chooser with the layer's own chunks and this map's authored ones.

        MAP-CHUNK-AUTHORING-001. The canonical rows are unchanged: the chunks the
        layer already uses, in its own 1-based order. The authored rows follow
        them, labelled ``Authored: <name>`` so a person can tell a project-authored
        chunk from a retail one at a glance, and drawn from the *resolved* authored
        plane - the arrangement the build would materialize - through the same
        renderer the retail chunks use. Only chunks composed against this map are
        offered: an authored plane holds tile ordinals, which resolve only through
        the character block of the map it was composed against.
        """
        self._chooser.blockSignals(True)
        self._chooser.clear()
        slot = self._slot
        if slot is None or self._current is None:
            self._chooser.blockSignals(False)
            self._chooser_hint.setText(
                "No editable layer is selected on this map."
            )
            return
        authored = self.placeable_authored(self._current.index)
        self._chooser_hint.setText(
            f"Chunks a dominant layer of this map uses ({len(slot.choices)})"
            + (f", plus {len(authored)} authored here. " if authored else ". ")
            + "Pick the one a click should paint; Create Chunk\u2026 starts from the "
            "selected one."
        )
        char_data = (
            self._editor.character_block(self._current.index)
            if self._editor is not None
            else None
        )
        try:
            # The session's cached character block, so a refill does not re-decode
            # what the preview already decoded. Thumbnail expansion stays inside
            # this guard: it is the same facade error family.
            images = mv.render_chunk_images(
                self._session.map_image,
                self._current.index,
                slot.choices,
                char_data=char_data,
            )
            for ordinal, image in enumerate(images, start=1):
                item = QListWidgetItem(
                    QIcon(self._thumbnail(image)),
                    f"Chunk {ordinal}{slot.borrowed_note(image.address)}",
                )
                item.setData(_CHUNK_ROLE, image.address)
                item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
                item.setSizeHint(self._chooser_cell)
                item.setToolTip(
                    f"Chunk {ordinal} · {len(slot.cells_using(image.address))} cell(s) in "
                    f"BG{slot.slot}\npointer {image.address:#010x}"
                )
                self._chooser.addItem(item)
        except _EDIT_ERRORS as exc:
            QMessageBox.warning(self, "Map Browser", str(exc))
            self._chooser.blockSignals(False)
            return
        self._add_authored_chooser_rows(authored, char_data)
        self._chooser.blockSignals(False)

    def _add_authored_chooser_rows(self, identities, char_data) -> None:
        """Append one palette row per authored chunk placeable in this map."""
        for identity in identities:
            plane = self._resolved_plane(identity)
            if plane is None:
                continue
            try:
                image = mv.render_chunk_entries(char_data, plane)
            except _EDIT_ERRORS as exc:
                QMessageBox.warning(self, "Map Browser", str(exc))
                continue
            name = self._authored_name(identity)
            item = QListWidgetItem(
                QIcon(self._thumbnail(image, key=identity)), f"Authored:\n{name}"
            )
            # A canonical row carries its pointer here and an authored row leaves
            # it None, so "which pointer" and "which authored chunk" never have to
            # be told apart by guessing at the value's type.
            item.setData(_CHUNK_ROLE, None)
            item.setData(_AUTHORED_ROLE, identity)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            item.setSizeHint(self._chooser_cell)
            item.setToolTip(
                f"Authored chunk {name}\n{self._authored_template_text(identity)}"
            )
            self._chooser.addItem(item)

    def _thumbnail(self, image: mv.ChunkImage, *, key=None) -> QPixmap:
        """A small chunk image on the canvas checkerboard, cached per key.

        The key is the chunk's address for a retail chunk and its authored
        identity for an authored one: an authored plane has no address (its
        rendered image is reported at address 0), so keying by address alone would
        make every authored swatch display whichever one was drawn first.
        """
        cache_key = image.address if key is None else key
        cached = self._thumbnails.get(cache_key)
        if cached is not None:
            return cached
        pixmap = self._pixmap_from_indices(image.pixels, image.width, image.height, self._current.palette)
        scaled = pixmap.scaled(
            QSize(64, 64),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        backed = QPixmap(scaled.size())
        backed.fill(theme.color("checker_dark"))
        painter = QPainter(backed)
        painter.fillRect(backed.rect(), _checkerboard())
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        self._thumbnails[cache_key] = backed
        return backed

    def _sync_chooser_selection(self) -> None:
        """Tag the palette with what each chunk means right now.

        Three tags, and they are states rather than decoration: ``brush`` is the
        value a click will paint (bold, and the one the palette's selection
        follows), ``cell`` is what the selected cell currently holds, and
        ``source`` is the chunk the canonical image stores there - so a painted
        cell is visibly different from a retail one in the palette itself. An
        authored row carries the same two states over authored identities instead
        of pointers.
        """
        slot = self._slot
        if slot is None or self._current is None:
            return
        working = None
        original = None
        staged_authored = None
        if self._selected_cell is not None:
            working = self._working_pointer(slot.slot, self._selected_cell)
            original = slot.cells[self._selected_cell].pointer
            staged_authored = self._authored_value_at(
                self._current.index, slot.slot, self._selected_cell
            )
        self._suppress_chooser = True
        for row in range(self._chooser.count()):
            item = self._chooser.item(row)
            # The same tag vocabulary as the retail-canonical chunks, and the same
            # rule as `_chunk_name`: a chunk the project authored is
            # "Authored: <name>" everywhere the surface names it.
            pointer = item.data(_CHUNK_ROLE)
            authored = item.data(_AUTHORED_ROLE)
            if authored is not None:
                tags = []
                if authored == self._brush_authored:
                    tags.append("brush")
                if staged_authored == authored:
                    tags.append("cell")
                item.setText(
                    f"Authored:\n{self._authored_name(authored)}"
                    + (f"\n{' · '.join(tags)}" if tags else "")
                )
                font = item.font()
                font.setBold(authored == self._brush_authored)
                item.setFont(font)
                continue
            ordinal = slot.ordinal_of(pointer) or row + 1
            tags = []
            if self._brush_authored is None and pointer == self._brush_pointer:
                tags.append("brush")
            if working is not None and pointer == working:
                tags.append("cell")
            elif original is not None and pointer == original:
                tags.append("source")
            item.setText(f"Chunk {ordinal}" + (f"\n{' · '.join(tags)}" if tags else ""))
            font = item.font()
            font.setBold(self._brush_authored is None and pointer == self._brush_pointer)
            item.setFont(font)
        # The palette's own selection follows the brush, so the visible selection
        # and the value a click paints are the same fact.
        if self._brush_authored is not None:
            row = self._chooser_row_for_authored(self._brush_authored)
        else:
            row = (
                None
                if self._brush_pointer is None
                else self._chooser_row_for(self._brush_pointer)
            )
        self._chooser.setCurrentRow(-1 if row is None else row)
        self._suppress_chooser = False

    def _chooser_row_for(self, pointer: int) -> int | None:
        for row in range(self._chooser.count()):
            item = self._chooser.item(row)
            if item.data(_AUTHORED_ROLE) is None and item.data(_CHUNK_ROLE) == pointer:
                return row
        return None

    def _chooser_row_for_authored(self, identity: str) -> int | None:
        for row in range(self._chooser.count()):
            if self._chooser.item(row).data(_AUTHORED_ROLE) == identity:
                return row
        return None

    def _on_chunk_selected(self, current: QListWidgetItem | None, _previous=None) -> None:
        """A palette pick becomes the brush. It paints nothing on its own.

        This is the whole difference between choosing a tool and using it: the
        old surface staged the picked chunk into whichever cell happened to be
        selected, so merely browsing the palette edited the map. The brush is now
        a value that a click or a drag applies, and the toolbar's status line says
        which value it is.

        Choosing the value that is ALREADY the brush changes nothing, and does no
        work at all - not a status line, not a render. The tab's own re-sync
        re-selects this row after every refresh, so needless work here would run
        once per painted cell (CQA-07's pathological-redraw rule).

        The map is deliberately NOT re-rendered either: the brush is a value the
        next click will place, not something drawn on the map, so the pixels on
        screen cannot have changed and re-rendering them would be pure cost.
        """
        if self._suppress_chooser or current is None or self._slot is None:
            return
        identity = current.data(_AUTHORED_ROLE)
        if identity is not None:
            if identity == self._brush_authored:
                return
            self._set_authored_brush(identity, publish=False)
            self._publish_status(
                f"{self._brush_label()} is the paint value; click or drag cells to "
                "place it."
            )
            self._refresh_editor_state()
            return
        pointer = current.data(_CHUNK_ROLE)
        ordinal = self._slot.ordinal_of(pointer)
        if ordinal is None:
            return
        if pointer == self._brush_pointer and self._brush_authored is None:
            return
        self._brush_authored = None
        self._brush_pointer = pointer
        self._brush_ordinal = ordinal
        self._publish_status(
            f"Chunk {ordinal} is the paint value; click or drag cells to paint it."
        )
        self._refresh_editor_state()

    # -- layout editing: apply, revert, reset, preview ------------------------

    def _working_pointer(self, layer_slot: int, cell: int) -> int:
        """The pointer a cell holds once pending edits (not the draft) are applied.

        MAP-RESIZE-AND-LAYERS-001: a project-authored grid's cells are resolved
        through the structural staging table first, because the layout session has no
        cell to ask about for a grid the canonical record does not state.

        CQA-26: an unread cell answers `_UNREAD_POINTER`, never the null pointer. A
        failed read is not data, and every caller has to say so rather than render
        it as an empty cell.
        """
        # CQA-26: cleared on EVERY attempt, before either early return, so a failure
        # recorded for one layer or one image cannot outlive the read that replaces
        # it. A read that still fails re-sets it on this same call.
        self._cell_read_error = ""
        if self._structure_slot is not None:
            return self._structural_pointer(self._structure_slot, cell)
        if self._editor is None or self._current is None:
            return _UNREAD_POINTER
        try:
            pointer = self._editor.working_pointer(self._current.index, layer_slot, cell)
        except _EDIT_ERRORS as exc:
            # The reader's own reason is the author's; a bare "could not be read" is
            # not, and every other edit failure in this tab shows `str(exc)`.
            self._cell_read_error = f"{_UNREAD_CELL_ACTION} ({exc})"
            return _UNREAD_POINTER
        return pointer

    def _apply_draft(self) -> None:
        """Apply the brush to the selected cell, as one undoable gesture.

        The keyboard/menu spelling of a single-cell paint (Enter, and the
        inspector's Apply button): it opens a gesture, paints one cell and closes
        it, which is exactly what a click does. It goes through
        :meth:`paint_cell` and therefore through the same history, so the two
        spellings cannot diverge.
        """
        if self._slot is None or self._selected_cell is None:
            return
        self._begin_stroke()
        changed = self.paint_cell(self._selected_cell)
        self._end_stroke()
        self._draft = None
        self._sync_chooser_selection()
        self._refresh_preview()
        self._refresh_editor_state()
        if not changed:
            self._publish_status(
                "That cell already holds the paint value; nothing was staged."
            )

    # -- project commit -------------------------------------------------------

    def _staged_layout_edits(self) -> dict[tuple[int, int, int], int | None]:
        """Every staged cell as the ``(map, layer, cell) -> ordinal | None`` batch.

        A cell whose staged value equals what the project already holds is
        spelled ``None`` (remove the authored paint) rather than re-written,
        because re-writing it would make an undo that returns a cell to its
        committed value rewrite an identical document. A cell whose value
        differs is spelled with its ordinal, resolved through the layer's own
        vocabulary so the persisted form is the one a build resolves.
        """
        if self._editor is None:
            return {}
        batch: dict[tuple[int, int, int], int | None] = {}
        for edit in self._editor.edits():
            slot = self._editor.slot(edit.map_index, edit.layer_slot)
            ordinal = slot.ordinal_of(edit.replacement)
            if ordinal is None:
                raise MapPaintError(
                    f"BG{edit.layer_slot} of map:{edit.map_index:04d} cannot store "
                    f"{edit.replacement:#010x}: it is not a chunk this layer uses"
                )
            committed = self._editor.committed_pointer(
                edit.map_index, edit.layer_slot, edit.cell
            )
            batch[(edit.map_index, edit.layer_slot, edit.cell)] = (
                None if edit.replacement == committed else ordinal
            )
        return batch

    def _staged_authored_placements(self) -> dict[tuple[int, int, int], str]:
        """Every staged authored placement that would actually change the project.

        A cell the project already authors with this same chunk is not a change
        and is left out, exactly as the ordinal batch leaves out a cell whose
        staged value the project already holds: re-writing it would make a no-op
        apply rewrite an identical document.
        """
        return staged_changes(self._authored_cells, self._authored_committed)

    def apply_to_project(self) -> bool:
        """Commit every staged paint into the project, then re-read it back.

        The authoring path, in one call: the staged gesture set becomes the
        project's semantic layout document through the one SDK authority
        (:func:`tools.webfoot.map_paint.set_layout_cells`), which validates the
        WHOLE batch against the canonical image before writing anything. The
        session then re-reads the project so what is on screen is what is on
        disk, and reports whether project source actually changed.

        MAP-CHUNK-AUTHORING-001 adds two more writes to the same gesture, and the
        ORDER is load-bearing:

        1. every staged chunk body is written first, through
           :func:`tools.webfoot.map_chunk.set_authored_chunk`. A layout cell that
           names an authored chunk is only a valid project once the chunk document
           declares it (`read_project` refuses the pair otherwise), so the bodies
           have to land before anything references them;
        2. the staged canonical ordinals, through ``set_layout_cells`` - unchanged
           for that path, and it also clears an ordinal's cell of any committed
           authored identity, because the cell now holds an ordinal;
        3. the staged authored placements last, through
           :func:`tools.webfoot.map_chunk.set_layout_authored_cells`, so the two
           documents cannot fight over a cell.

        It stays ONE project write per document and one `projectChanged`, and the
        history is cleared only after everything succeeded.
        """
        if self._editor is None or self._session.map_image is None:
            return False
        if self._session.project_dir is None:
            self._publish_status(
                "Open or extract a project first; a paint is stored in the project, "
                "not in a ROM."
            )
            return False
        try:
            batch = self._staged_layout_edits()
        except _EDIT_ERRORS as exc:
            QMessageBox.warning(self, "Map paint", str(exc))
            return False
        placements = self._staged_authored_placements()
        chunks = self._pending_chunk_documents()
        resizes = self._staged_resize_edits()
        layers = self._staged_layer_edits()
        structural_cells = self._staged_structural_cells()
        if (
            not batch
            and not placements
            and not chunks
            and not resizes
            and not layers
            and not structural_cells
        ):
            self._publish_status("There is no staged paint to apply.")
            return False
        try:
            changed = False
            # MAP-RESIZE-AND-LAYERS-001: the structural order is load-bearing. A
            # grown grid and a new layer are written FIRST, because a cell the author
            # painted in that grid is only a legal layout cell once the grid exists;
            # the cells follow; and a staged *removal* goes last, when nothing names
            # the slot any more.
            if resizes or layers:
                if self._write_staged_structure(removals=False):
                    changed = True
            for identity in sorted(chunks):
                if set_authored_chunk(
                    self._session.project_dir,
                    self._session.map_image,
                    chunks[identity],
                    profile=self._session.profile,
                ):
                    changed = True
            if batch or structural_cells:
                merged = dict(batch)
                merged.update(structural_cells)
                if set_layout_cells(
                    self._session.project_dir,
                    self._session.profile,
                    self._session.map_image,
                    merged,
                ):
                    changed = True
            if placements:
                if set_layout_authored_cells(
                    self._session.project_dir,
                    self._session.map_image,
                    placements,
                    profile=self._session.profile,
                ):
                    changed = True
            if resizes or layers:
                if self._write_staged_structure(removals=True):
                    changed = True
        except _STRUCTURE_ERRORS as exc:
            QMessageBox.warning(self, "Map paint", str(exc))
            return False
        # Re-read the project so the session's floor, its chunk table, its authored
        # placements and its structural document are what was just written.
        self._staged_chunks.clear()
        self._chunk_applied_plane = tuple(self._chunk_plane)
        self._staged_resizes = {}
        self._staged_layers = {}
        self._structural_cells = {}
        self.reload_project_layout()
        self._reselect_layer()
        # A placement the project now holds unchanged is no longer staged work: the
        # same rule the ordinal batch uses for a cell whose value the project
        # already had, so the pending count and the pending glyphs go clean without
        # touching a placement a write did not land.
        self._authored_cells = self._staged_authored_placements()
        self._undo_stack.clear()
        self._draft = None
        if changed:
            parts = []
            if chunks:
                parts.append(f"{len(chunks)} authored chunk(s)")
            if resizes:
                parts.append(f"{len(resizes)} layer resize(s)")
            if layers:
                parts.append(f"{len(layers)} authored layer(s)")
            if batch:
                parts.append(f"{len(batch)} painted cell(s)")
            if structural_cells:
                parts.append(f"{len(structural_cells)} painted cell(s) of a project grid")
            if placements:
                parts.append(f"{len(placements)} authored placement(s)")
            message = (
                f"Applied {' and '.join(parts)} to the project. "
                "Validate and build to run them."
            )
        else:
            message = "The project already held exactly this layout."
        self._populate_chooser()
        self._sync_chooser_selection()
        self._refresh_preview()
        self._refresh_editor_state()
        # The confirmation is the LAST word on the status line: the refreshes above
        # each restate the working state, and the author's answer to "what did my
        # Apply do" is what the line has to leave behind.
        self._publish_status(message)
        if changed:
            # WORKBENCH-MUTATION-CURRENCY-001. A real project write invalidates
            # validation and any current build, exactly as the Inspector's Apply,
            # the Graphics palette Apply and the Warps Apply already do. This tab
            # used to emit `projectChanged` alone, which re-read every peer but
            # left `Session.project_revision` untouched - so `validation_current`
            # stayed True, the shell kept the status bar reading "validation
            # current", Build stayed enabled, and a build could run against a
            # project that was never validated in its current state.
            #
            # One call, in the one branch that a real write reaches: `changed` is
            # True only when the SDK reports project source actually moved, so a
            # no-op or refused apply never advances the revision.
            self._session.project_mutated()
            self.projectChanged.emit()
        return changed

    def reload_project_layout(self) -> None:
        """Re-read the committed project into the session's floor and this tab.

        The one place a project change reaches the layout session. It does not
        rebuild the session (which would discard staged work, the CQA-05
        regression) and it does not touch the base image; the floor is simply
        replaced and the writer re-derived from it.

        MAP-CHUNK-AUTHORING-001: the authored facts - the project's chunk table
        and its committed authored placements - are re-read here too, once per
        call rather than once per cell or per repaint (CQA-07). The identities the
        session's pointer floor deliberately cannot carry travel into the preview
        as resolved planes instead.

        MAP-RESIZE-AND-LAYERS-001: the project's structural document is read FIRST,
        once, and the merged view rebuilt from it - so the layout read below can tell
        a project-authored grid's cells from a canonical layer's, and the painter
        that resolves the pointer floor is handed the document that makes a grown
        cell resolvable at all. Nothing the user staged structurally is dropped.
        """
        self._refresh_structure()
        self._reload_project_authored()
        if self._editor is None or self._session.map_image is None:
            return
        floor: dict[tuple[int, int, int], int] = {}
        if self._session.project_dir is not None:
            structural = self.structural_pairs()
            try:
                authored = read_layout_edits(self._session.project_dir)
                # Only the ordinal form belongs in a pointer floor; a cell holding
                # an authored identity is rendered through a plane override, and a
                # cell of a project-authored grid is rendered by the structural
                # preview from its own geometry - the canonical session has no cell
                # for it to point at.
                ordered = {
                    key: value
                    for key, value in authored.cells().items()
                    if type(value) is int and (key[0], key[1]) not in structural
                }
                if ordered:
                    floor = MapPainter(
                        self._session.map_image, structure=self.structure_document()
                    ).pointer_edits(ordered)
            except _PROJECT_READ_ERRORS + (MapPaintError,) as exc:
                # An unreadable project is reported where the user can see it and
                # leaves the session's staged work alone; it does not silently
                # present an unpainted layout as if the project were empty.
                self._publish_status(f"Project layout could not be read: {exc}")
                return
        self._editor.set_floor(floor)
        self._refresh_editor_state()

    def _revert_cell(self) -> None:
        """Put the selected cell back to the value the base holds for it.

        "Back" means the canonical image plus the committed project: a cell the
        project paints reverts to that authored value, and a cell it does not
        paint reverts to the source ROM's own chunk. It is the session's
        un-stage operation, so it removes the staged paint rather than recording
        a new one, and it is itself undoable because it is a gesture like any
        other.
        """
        if self._editor is None or self._current is None or self._slot is None:
            return
        if self._selected_cell is None:
            return
        index = self._current.index
        slot = self._slot.slot
        cell = self._selected_cell
        if self._structure_slot is not None:
            self._revert_structural_cell(index, slot, cell)
            return
        if self._editor.edit(index, slot, cell) is None:
            self._publish_status("That cell has no staged paint to revert.")
            return
        before = self._working_pointer(slot, cell)
        if before == _UNREAD_POINTER:
            self._publish_status(self._cell_read_error or _UNREAD_CELL_ACTION)
            return
        base = self._editor.committed_pointer(index, slot, cell)
        self._draft = None
        try:
            self._editor.clear_cell(index, slot, cell)
        except _EDIT_ERRORS as exc:
            QMessageBox.warning(self, "Map paint", str(exc))
            return
        # One history entry, whose "previous" value is the staged one and whose
        # redo re-stages it: reverting is a paint of the base value.
        self._naming_revert = True
        try:
            command = PaintCellsCommand(
                self,
                map_index=index,
                layer_slot=slot,
                cells=(cell,),
                previous={cell: before},
                applied={cell: base},
            )
        finally:
            self._naming_revert = False
        command.set_keys(self._brush_pointer, cell, cell)
        self._undo_stack.push(command)
        self._sync_chooser_selection()
        self._refresh_preview()
        self._refresh_editor_state()

    def _revert_structural_cell(self, index: int, layer_slot: int, cell: int) -> None:
        """Put one cell of a project-authored grid back to the grid's own default.

        "Back" means the value the project's structure puts there - the retail chunk
        on a retail cell, the initialization chunk on a grown one - so this removes
        the staged paint rather than recording a new one, and it is itself undoable
        because it is a gesture like any other.
        """
        layer = self._structure_slot
        key = (index, layer_slot, cell)
        if layer is None or key not in self._structural_cells:
            self._publish_status("That cell has no staged paint to revert.")
            return
        before = self._structural_cells[key]
        after = self._structural_committed.get(key)
        self._draft = None
        self._naming_revert = True
        try:
            command = StructuralPaintCommand(
                self,
                map_index=index,
                layer_slot=layer_slot,
                cells=(cell,),
                previous={cell: before},
                applied={} if after is None else {cell: after},
            )
        finally:
            self._naming_revert = False
        command.set_keys(self._brush_ordinal, cell, cell)
        self._structural_cells.pop(key, None)
        self._undo_stack.push(command)
        self._sync_chooser_selection()
        self._refresh_preview()
        self._refresh_editor_state()

    def _reset_edits(self) -> None:
        """Discard every *staged* paint in this session, and clear the history.

        The project keeps what it already holds: "discard pending" means the work
        that has not been applied, not the authored layout. The history is cleared
        with it, because every command in it describes a staged value that no
        longer exists.

        MAP-CHUNK-AUTHORING-001: staged work now includes the authored placements
        and the chunk documents composed but not yet written, so this discards
        those too - an author who says "discard pending" does not expect a staged
        chunk to survive it.
        """
        if self._editor is None:
            return
        dropped = self._editor.reset()
        dropped_authored = len(self._authored_cells)
        self._authored_cells = {}
        dropped_chunks = len(self._staged_chunks)
        self._staged_chunks = {}
        self._resolved_planes = {}
        # MAP-RESIZE-AND-LAYERS-001: staged structural work is staged work too, so
        # "discard pending" drops a staged resize, a staged new layer and a staged
        # removal exactly as it drops a staged paint - and rebuilds the merged view
        # from the project, which is what the preview then shows.
        dropped_structural = len(self._staged_resize_edits()) + len(
            self._staged_layer_edits()
        )
        dropped_structural_cells = len(self._staged_structural_cells())
        self._staged_resizes = {}
        self._staged_layers = {}
        self._structural_cells = {}
        self._rebuild_structure_view()
        self._populate_layer_combo(
            self._slot.slot if self._slot is not None else None
        )
        self._close_chunk_editor_page()
        self._undo_stack.clear()
        self._draft = None
        self._stroke = []
        self._stroke_previous = {}
        self._stroke_applied = {}
        self._sync_chooser_selection()
        self._refresh_preview()
        self._refresh_editor_state()
        if dropped or dropped_authored or dropped_chunks or dropped_structural:
            extra = ""
            if dropped_authored:
                extra += f" and {dropped_authored} authored placement(s)"
            if dropped_chunks:
                extra += f" and {dropped_chunks} unapplied chunk(s)"
            if dropped_structural:
                extra += f" and {dropped_structural} structural change(s)"
            if dropped_structural_cells:
                extra += f" and {dropped_structural_cells} painted cell(s) of one"
            self._publish_status(
                f"Discarded {dropped} staged paint(s){extra}; the preview shows what "
                "the project holds."
            )

    def _committed_authored_overrides(self, map_index: int) -> dict:
        """The project's committed authored placements for one map, as planes.

        Built from the cached project facts and the cached resolved planes, so a
        repaint costs a dict walk and no project or template read (CQA-07).
        """
        overrides: dict[tuple[int, int], mv.ChunkSubstitution] = {}
        for (cell_map, layer_slot, cell), identity in self._authored_committed.items():
            if cell_map != map_index:
                continue
            plane = self._resolved_plane(identity)
            if plane is None:
                continue
            overrides[(layer_slot, cell)] = mv.ChunkSubstitution(plane)
        return overrides

    def _preview_overrides(self) -> dict[tuple[int, int], int | mv.ChunkSubstitution]:
        """The cell substitutions this preview must apply, in precedence order.

        Three layers, as the layout session's own ``overrides`` documents them,
        plus the authored planes a pointer cannot express:

        1. the project's committed authored placements, as :class:`ChunkSubstitution`
           planes - the reason an authored cell still renders after a project
           reload, when the cell's canonical pointer names the template rather than
           the authored body;
        2. the session's committed project paints and staged edits, as pointers -
           a canonical paint over an authored cell therefore replaces the authored
           plane, which is exactly what the ordinal write does on disk;
        3. the tab's staged authored placements, as planes, which is the value a
           click has already put on screen.

        Nothing here reads the project, and the resolved planes are cached per
        identity, so this is cheap enough to run on every repaint.
        """
        if self._editor is None or self._current is None:
            return {}
        index = self._current.index
        try:
            overrides: dict[tuple[int, int], int | mv.ChunkSubstitution] = dict(
                self._committed_authored_overrides(index)
            )
            overrides.update(self._editor.overrides(index, self._draft))
        except _EDIT_ERRORS as exc:
            QMessageBox.warning(self, "Layout edit", str(exc))
            self._draft = None
            return {}
        for (cell_map, layer_slot, cell), identity in self._authored_cells.items():
            if cell_map != index:
                continue
            plane = self._resolved_plane(identity)
            if plane is None:
                continue
            overrides[(layer_slot, cell)] = mv.ChunkSubstitution(plane)
        return overrides

    def _refresh_preview(self) -> None:
        """Re-render the map with the pending edits applied, in memory only.

        The map is re-rendered through the layout session's own preview while the
        substitutions are all pointers, which is the accepted path and keeps the
        character block decoded once per session. An authored plane is not a
        pointer, so that case goes through :func:`tools.webfoot.map_view.render_map`
        directly - the same facade, the same character block, the same stitch -
        with the merged substitution set.
        """
        if self._editor is None or self._current is None:
            return
        index = self._current.index
        # A project-authored grid is drawn from the project's own geometry: the
        # canonical renderer has no record for it, because the record the build will
        # emit does not exist before the build (MAP-RESIZE-AND-LAYERS-001).
        if self.structural_layers(index) and self._structural_preview():
            return
        overrides = self._preview_overrides()
        if not overrides:
            cached = self._render_cache.get(index)
            if cached is not None:
                self._current = cached
            self._show_composite()
            return
        authored = any(
            isinstance(value, mv.ChunkSubstitution) for value in overrides.values()
        )
        self._status.setText(f"Updating the map:{index:04d} preview…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            if authored:
                self._current = mv.render_map(
                    self._session.map_image,
                    index,
                    chunk_overrides=overrides,
                    char_data=self._editor.character_block(index),
                )
            else:
                self._current = self._editor.preview(index, self._draft)
        except _EDIT_ERRORS as exc:
            QMessageBox.warning(self, "Layout edit", str(exc))
        finally:
            QApplication.restoreOverrideCursor()
        self._show_composite()

    # -- layout editing: panel state and status ------------------------------

    def _refresh_editor_state(self) -> None:
        """Re-sync every editor control with the session's real state."""
        result = self._current
        editing = self._edit_mode
        target = self._target
        slot = self._slot
        edits = self._editor.edits_for(result.index) if (self._editor and result) else ()
        staged_cells = {edit.cell for edit in edits if slot is not None and edit.layer_slot == slot.slot}
        if editing and slot is not None and result is not None:
            # A staged authored placement is a staged map edit, so the cell carries
            # the same "something is pending here" mark a staged paint does - and so
            # does a staged paint of a project-authored grid.
            staged_cells |= {
                cell
                for (cell_map, layer_slot, cell) in self._authored_cells
                if cell_map == result.index and layer_slot == slot.slot
            }
            staged_cells |= {
                cell
                for (cell_map, layer_slot, cell) in self._structural_cells
                if cell_map == result.index and layer_slot == slot.slot
            }
        if editing and slot is not None:
            self._grid_item.set_edited(staged_cells)
        elif self._grid_item is not None:
            self._grid_item.set_edited(())

        # Mode badge: the tab says what state it is in and why, in words, with a
        # glyph so the state never depends on hue. The badge is a one-line state;
        # its explanation sits in the quiet label under it, so a long reason
        # cannot clip the state itself.
        self._read_only_detail.setText("")
        self._set_layer_row_visible(True)
        if not editing:
            self._set_mode_badge("VIEW MODE \u00b7 read-only until Edit Layout is on", "neutral")
        elif self._editor is None:
            self._set_mode_badge("READ ONLY \u00b7 layout editing is unavailable", "readonly")
            self._read_only_detail.setText(self._editor_error or "")
            self._set_layer_row_visible(False)
        elif target is None or not target.editable:
            reason = (
                target.read_only_reason if target is not None else "this map could not be read"
            )
            kind = target.read_only_kind if target is not None else ""
            self._set_mode_badge(
                f"READ ONLY \u00b7 {_READ_ONLY_BADGES.get(kind, 'unsupported layout type')}",
                "readonly",
            )
            self._read_only_detail.setText(reason)
            self._set_layer_row_visible(False)
        else:
            tool = "Paint" if self._tool == _TOOL_PAINT else "Pick"
            brush = self._brush_label()
            self._set_mode_badge(
                f"EDIT LAYOUT \u00b7 {tool} tool \u00b7 {brush} \u00b7 click or drag a "
                "256\u00d7256 cell",
                "edit",
            )
        self._sync_chooser_presence()

        # Selected cell and current chunk.
        if slot is not None and self._selected_cell is not None:
            cell = slot.cells[self._selected_cell]
            self._cell_label.setText(
                f"column {cell.column}, row {cell.row} · cell {cell.cell + 1} of "
                f"{slot.grid.cell_count}"
            )
            staged_authored = (
                self._authored_value_at(result.index, slot.slot, cell.cell)
                if result is not None
                else None
            )
            if staged_authored is not None:
                # The cell holds an authored chunk, so the pointer readout below it
                # would describe the template the cell no longer shows. What the
                # surface states instead is the authored identity and its body,
                # which is what a build will materialize there.
                self._chunk_label.setText(
                    f"{self._authored_name(staged_authored)} · authored chunk, "
                    f"placed in BG{slot.slot}"
                )
                self._detail.setText(
                    f"source ROM holds {self._chunk_name(slot.ordinal_of(cell.pointer))}\n"
                    "project authors this cell\n"
                    f"chunk {staged_authored}\n"
                    + (
                        "no canonical field; the build materializes this cell"
                        if cell.offset < 0
                        else f"field 0x{cell.offset:08X} (4 bytes, in place)"
                    )
                )
            else:
                working = self._working_pointer(slot.slot, cell.cell)
                # CQA-26: a cell nothing could read is not reported as empty, is
                # not counted among a chunk's users, and does not ask the session
                # for a committed pointer it may not be able to answer for.
                unread = working == _UNREAD_POINTER
                ordinal = None if unread else slot.ordinal_of(working)
                used = 0 if unread else len(slot.cells_using(working))
                self._chunk_label.setText(
                    f"{_UNREAD_CELL} · BG{slot.slot}"
                    if unread
                    else f"{self._chunk_name(ordinal)} · used by {used} cell(s) of BG{slot.slot}"
                )
                source = slot.ordinal_of(cell.pointer)
                # The unread guard only has to run first: it is what keeps the
                # committed-pointer call below out of a read that already failed.
                painted = False
                if not unread:
                    painted = (
                        self._structural_staged_value(self._structure_slot, cell.cell)
                        is not None
                        if self._structure_slot is not None
                        else (
                            self._editor.committed_pointer(
                                result.index, slot.slot, cell.cell
                            )
                            != cell.pointer
                            if (self._editor and result)
                            else False
                        )
                    )
                # A cell that exists only in a project-authored grid has no
                # four-byte field in the canonical image to rewrite: saying "field
                # 0x-0000001" would be a lie about how the paint is stored, so the
                # detail states what actually happens instead.
                field = (
                    "no canonical field; the build materializes this cell"
                    if cell.offset < 0
                    else f"field 0x{cell.offset:08X} (4 bytes, in place)"
                )
                self._detail.setText(
                    f"source ROM holds {self._chunk_name(source)}\n"
                    + ("project paints this cell\n" if painted else "")
                    + (f"{self._structural_marker(self._structure_slot)}\n" if self._structure_slot is not None else "")
                    + (f"{_UNREAD_CELL}\n" if unread else f"pointer {working:#010x}\n")
                    + field
                )
        else:
            # No cell picked yet: say what to do, rather than three dash rows.
            self._cell_label.setText("No cell selected")
            self._chunk_label.setText("")
            self._detail.setText("")

        # The change summary counts BOTH kinds of staged map edit and the chunk
        # documents waiting to be written, because the shell's window title reads
        # the same number: one authority on "is there unsaved work".
        unsaved = self._unsaved_count()
        committed = self._editor.floor_cell_count if self._editor is not None else 0
        authored_committed = len(
            [key for key in self._authored_committed if result is not None and key[0] == result.index]
        )
        if not edits and not committed and self.unsaved_edit_count() == 0:
            self._set_change_label("No layout changes", "neutral")
        elif unsaved:
            parts = [f"{unsaved} staged {self._staged_noun()}(s)"]
            if committed or authored_committed:
                parts.append(f"{committed + authored_committed} in the project")
            self._set_change_label(" \u00b7 ".join(parts), "pending")
        else:
            self._set_change_label(
                f"{committed + authored_committed} authored cell(s) in the project",
                "saved",
            )

        self._apply_button.setEnabled(editing and slot is not None)
        self._apply_button.setToolTip(
            "Paint the selected cell with the current value (Enter)"
        )
        index = result.index if result is not None else None
        self._revert_button.setEnabled(
            editing
            and index is not None
            and slot is not None
            and self._selected_cell is not None
            and self._cell_has_staged_paint(index, slot.slot, self._selected_cell)
        )
        # A staged authored placement or an unapplied chunk is staged work, so the
        # reset and commit buttons answer to them exactly as they do to a paint -
        # and so is a staged structural edit (a resize, a new layer, a removal) or a
        # paint of a project-authored grid.
        pending_chunks = bool(self._pending_chunk_documents())
        staged_any = (
            bool(edits)
            or bool(self._authored_cells)
            or pending_chunks
            or bool(self._staged_resize_edits())
            or bool(self._staged_layer_edits())
            or bool(self._staged_structural_cells())
        )
        self._reset_button.setEnabled(editing and staged_any)
        self._commit_button.setEnabled(
            editing and self._editor is not None and staged_any
            and self._session.project_dir is not None
        )
        self._commit_button.setToolTip(
            "Write every staged paint into the project's layout source. The project "
            "is then validated and built like any other authored content."
            if self._session.project_dir is not None
            else "Open or extract a project first: a paint is stored in the project."
        )
        # Save As needs something to save: an editable layer on this map, the
        # no-op copy included, or pending changes made on another map.
        self._save_button.setEnabled(
            editing and self._editor is not None and (slot is not None or bool(edits))
        )
        self._layer_combo.setEnabled(editing and self._layer_combo.count() > 0)
        self._chooser.setEnabled(editing and slot is not None)
        # The chunk-authoring actions need an editable layer AND an image whose
        # chunks the SDK can read; `chunk_author()` answers once per session and
        # records its refusal, so this never becomes a per-refresh read.
        author_ready = bool(editing and slot is not None and self.chunk_author() is not None)
        self._create_chunk_button.setEnabled(author_ready)
        self._create_chunk_button.setToolTip(
            "Create a new 256\u00d7256 chunk from the chunk selected in the palette, "
            "then arrange its screen entries"
            if author_ready
            else self._chunk_author_error
            or "Turn Edit Layout on and pick a paintable layer first."
        )
        self._edit_chunk_button.setEnabled(author_ready and self._brush_authored is not None)
        self._edit_chunk_button.setToolTip(
            "Reopen the authored chunk currently selected in the palette"
            if self._brush_authored is not None
            else "Select an authored chunk in the palette to revise it."
        )
        self._create_chunk_action.setEnabled(author_ready)
        self._paint_tool.setEnabled(editing and slot is not None)
        self._pick_tool.setEnabled(editing and slot is not None)
        self._sync_structure_controls()
        self._mark_pending_rows()
        self._announce_dirty()
        self._update_status()

    # -- state rendering ------------------------------------------------------

    def _set_mode_badge(self, text: str, role: str) -> None:
        """Set the mode badge's wording, colour and accessible name together.

        The badge is a *sentence*, and its wording already names the state
        ("EDIT LAYOUT", "READ ONLY", "VIEW MODE"), so no glyph is added to it -
        a symbol in front of a sentence that already says the same thing is
        decoration, and the ticket's ban on ornament applies to glyphs as much as
        to gradients. The non-colour channels are therefore the wording itself and
        the brightness of the role: the identity magenta for the editing state,
        recessive grey for a read-only one. The role drives the colour, so no caller
        can express a state with colour alone, and the accessible name states the
        role in words.
        """
        self._mode_badge.setText(text)
        self._mode_badge.setStyleSheet(
            f"color: {theme.color(_MODE_COLORS.get(role, 'text_secondary')).name()};"
            " background: transparent;"
        )
        self._mode_badge.setAccessibleName(f"{_MODE_ROLE_WORDS.get(role, '')} {text}".strip())

    def _set_change_label(self, text: str, role: str) -> None:
        """Set the change summary's glyph, wording and colour together.

        The glyph leads here, because the change count is a state the user scans
        for rather than reads.
        """
        glyph = theme.status_glyph(role)
        self._change_label.setText(f"{glyph} {text}")
        self._change_label.setStyleSheet(
            f"color: {theme.color(_CHANGE_COLORS.get(role, 'text_secondary')).name()};"
            " background: transparent;"
        )
        self._change_label.setAccessibleName(text)

    def _announce_dirty(self) -> None:
        """Tell the shell when the pending-edit count changes."""
        count = self.unsaved_edit_count()
        if count != self._last_dirty:
            self._last_dirty = count
            self.dirtyChanged.emit()

    def unsaved_edit_count(self) -> int:
        """Pending layout changes no Save As has written yet.

        This is the BROWSER's count, which is what its change label and its
        Discard-pending button are scoped to. The window title and the status bar
        report `Session.unsaved_edit_count()`, which also counts the Warps surface,
        so the two legitimately differ by the staged connection edits.
        """
        return self._unsaved_count()

    def status_text(self) -> str:
        """The compact one-line status this tab currently reports."""
        return self._status.text()

    def _publish_status(self, text: str) -> None:
        """Set the tab's own status line and tell the shell to show it.

        One implementation, one place it is drawn: the shell re-parents this very
        label into its status bar, so the two can never disagree.
        """
        self._status.setText(text)
        self.statusChanged.emit(text)

    def _update_status(self) -> None:
        """The active tab's own line, with nothing the rest of the screen states.

        Deliberately absent, because another surface already states it:

        - the image and project identity - the window title and the shell's status
          bar carry those;
        - the map's pixel dimensions and its graphical-layer count - the Map
          inspector states both, in more detail;
        - the layer names and their classifications - the tool strip's own
          checkboxes state those.

        What is left is what only this line knows: which map is open, the live
        hover readout, the edit state, and how much work is unsaved.

        One thing outranks all of that: when the project's structural document
        could not be read, this line says so instead. Every structural readout is
        derived from that document, so a working line drawn over the failure would
        be stating facts the surface does not have - and the failure arrives from a
        background project mutation, where the Structure section's own label is
        usually not in view. It is republished from here on every refresh, so the
        refresh at the end of the mutation cannot bury it.
        """
        if self._structure_read_error:
            self._publish_status(self._structure_read_error)
            return
        if self._cell_read_error:
            self._publish_status(self._cell_read_error)
            return
        result = self._current
        if result is None:
            # A loaded image with no map chosen yet. Say so, rather than leaving
            # this label at the text it was created with, which read as though no
            # image were open at all.
            self._publish_status(
                f"{len(self._entries)} maps \u00b7 no map selected"
                if self._entries
                else "Open a supported ROM to browse its maps."
            )
            return
        parts = [f"map:{result.index:04d}"]
        if result.name:
            parts.append(result.name)
        if self._session.authored is not None:
            parts.append(
                f"DragonByte Z derivative \u00b7 {len(self._session.authored.edits)} "
                "verified layout change(s)"
            )
        # The edit *mode* is named once here and once on the tool strip's badge;
        # what this line adds is the working detail no other surface carries -
        # whether a choice is previewed but uncommitted, and how much is unsaved.
        if self._edit_mode:
            parts.append("EDIT LAYOUT")
            if self._slot is None:
                parts.append("no paintable layer on this map")
            elif self._editor is not None:
                committed = self._editor.floor_cell_count
                committed += len(
                    [key for key in self._authored_committed if key[0] == result.index]
                )
                unsaved = self._unsaved_count()
                if unsaved:
                    parts.append(
                        f"{unsaved} staged {self._staged_noun()}(s) to apply"
                    )
                elif committed:
                    parts.append(f"{committed} authored cell(s) in the project")
                else:
                    parts.append("nothing painted yet")
                parts.append(f"brush {self._brush_label()}")
        else:
            parts.append("read-only")
        if self._hover_text:
            parts.append(self._hover_text)
        if self._hover_cell:
            parts.append(self._hover_cell)
        self._publish_status("  \u00b7  ".join(parts))

    def _edits(self) -> tuple[LayoutEdit, ...]:
        """The editor's pending paints, or none while no editor can be built."""
        return self._editor.edits() if self._editor is not None else ()

    def _pending_work(self) -> PendingWork:
        """What this session staged and no write has published yet (CQA-27).

        The policy is the SDK session's: it holds the written baseline and decides
        what counts as a change. This tab contributes only the families it alone
        knows about - a staged chunk document, an authored placement, a staged
        resize or new layer - and each is named here rather than sent as one
        number, so a family that stops being staged cannot be counted by accident.
        """
        return self._layout.pending(
            self._edits(),
            paints=(len(self._staged_structural_cells()),),
            changes=(
                len(self._staged_authored_placements()),
                len(self._pending_chunk_documents()),
                # MAP-RESIZE-AND-LAYERS-001: a staged resize or a staged new layer
                # is work the user has done and would lose, exactly as a staged
                # cell paint is; a paint of a project-authored grid joins the count
                # for the same reason, and stays a paint where the wording is
                # decided.
                len(self._staged_resize_edits()),
                len(self._staged_layer_edits()),
            ),
        )

    def _unsaved_count(self) -> int:
        """Pending changes that no Save As or project apply has written yet.

        MAP-CHUNK-AUTHORING-001 extends the count by exactly the two forms of
        unpublished chunk work: an authored placement the project does not already
        hold, and a chunk document composed but not yet written. Both are work the
        user has done and would lose, so a shell that showed only painted cells in
        its title would understate the unsaved state.
        """
        return self._pending_work().count

    def _staged_noun(self) -> str:
        """What to call the staged work: a paint when that is all there is.

        The authored half is real work but not a *paint* - a chunk body and a
        placement are not cell paints - so the wording only widens when authored
        work is actually staged, and a surface that staged only paints keeps
        saying so. A structural change widens it too, for the same reason: a resize
        is not a paint.
        """
        return self._pending_work().noun

    def _brush_label(self) -> str:
        """The paint value in words: an authored chunk names itself."""
        if self._brush_authored is not None:
            return self._authored_name(self._brush_authored)
        return self._chunk_name(self._brush_ordinal)

    def _authored_name(self, identity: str) -> str:
        """The display name of an authored chunk identity.

        ``chunk:name`` -> ``Authored: name``: the same distinct spelling the
        palette row uses, so a person can tell an authored chunk from a retail one
        wherever either is named.
        """
        name = identity.split(":", 1)[1] if ":" in identity else identity
        return f"Authored: {name}"

    @staticmethod
    def _chunk_name(ordinal: int | None) -> str:
        return f"Chunk {ordinal}" if ordinal else "an empty cell"

    def _set_layer_row_visible(self, visible: bool) -> None:
        """Show or hide the Layer row's combo and its label together."""
        self._layer_combo.setVisible(visible)
        label = self._editor_form.labelForField(self._layer_combo)
        if label is not None:
            label.setVisible(visible)

    # -- MAP-RESIZE-AND-LAYERS-001: reading the project's structure -----------
    #
    # The SDK authority is `tools.webfoot.map_resize`. This surface reads the
    # project's structural document ONCE per session and per project mutation
    # (CQA-07), merges the staged structural edits over it IN MEMORY, and builds one
    # `MapResizer`/`MapPainter` pair over the result. Every readout, every preview
    # and every repaint reads those caches; nothing below this heading opens a file.

    def structure_document(self) -> MapStructure:
        """The committed + staged structural document this session is showing."""
        if self._staged_document is not None:
            return self._staged_document
        return MapStructure()

    def structural_pairs(self) -> frozenset[tuple[int, int]]:
        """Every ``(map, slot)`` the structural document owns."""
        return self.structure_document().structural_slots()

    def structure_target(self) -> StructureTarget | None:
        """The structural view of the map on screen, or None with a recorded reason."""
        if self._current is None:
            return None
        return self._structure_target_for(self._current.index)

    def structural_layers(self, map_index: int) -> tuple[StructuralLayer, ...]:
        """The layers of one map whose grid the project owns, in slot order."""
        target = self._structure_target_for(map_index)
        if target is None:
            return ()
        return tuple(layer for layer in target.slots if layer.structural)

    def structural_layer(self, map_index: int, layer_slot: int) -> StructuralLayer | None:
        """One project-owned layer, or None when the canonical record is the grid."""
        for layer in self.structural_layers(map_index):
            if layer.slot == layer_slot:
                return layer
        return None

    def free_slots(self, map_index: int) -> tuple[int, ...]:
        """Slots the canonical image leaves unused and this project may activate."""
        target = self._structure_target_for(map_index)
        return () if target is None else target.free_slots

    def layer_templates(self, map_index: int) -> tuple[StructuralLayer, ...]:
        """The canonical layers of this map a new layer may be copied from.

        Only the supported dominant form may template a new record: its header and
        its own chunk vocabulary are what the new layer inherits, and the engine has
        no other form this capability has established.
        """
        target = self._structure_target_for(map_index)
        if target is None:
            return ()
        return tuple(
            layer
            for layer in target.slots
            if layer.absent is False
            and layer.classification == "dominant"
            and layer.columns * layer.rows > 0
        )

    def template_vocabulary(
        self, map_index: int, layer_slot: int
    ) -> tuple[ChunkChoice, ...]:
        """The initialization chunks a new layer copied from `layer_slot` may use."""
        if self._resizer is None:
            raise MapStructureError(self._structure_refusal())
        return self._resizer.vocabulary(map_index, layer_slot)

    def _structure_refusal(self) -> str:
        """Why no structural command can run, in words."""
        return self._structure_unavailable or (
            "turn Edit Layout on and select a layer of a map whose structure can be read"
        )

    def _clear_structure_state(self) -> None:
        """Drop every structural fact; the session's base image has changed.

        CQA-05. A layer record, a grid, a resolved rendering and a staged grid change
        are all claims about one image's map table, so a new image invalidates them
        at once - which is why this is called from ``on_session_changed`` alone.
        """
        self._structure = None
        self._structure_unavailable = ""
        self._structure_read_error = ""
        # CQA-26: the cell-read failure names THIS image's map table, so it goes
        # with the image for the same reason the structural one does.
        self._cell_read_error = ""
        self._staged_document = None
        self._staged_resizes = {}
        self._staged_layers = {}
        self._resizer = None
        self._painter = None
        self._structure_targets = {}
        self._structure_slot = None
        self._structural_cells = {}
        self._structural_committed = {}
        self._structural_images = {}
        self._structure_row_signature = ()
        self._structure_list.blockSignals(True)
        self._structure_list.clear()
        self._structure_list.blockSignals(False)

    def _cell_has_staged_paint(self, map_index: int, layer_slot: int, cell: int) -> bool:
        """Whether one cell carries a staged paint, of either kind.

        A project-authored grid is asked through its own staging table: its grown
        cells have no canonical field and no canonical cell index, so asking the
        layout session about them would be a question it cannot answer - and, for a
        slot the canonical image leaves unused, one it answers with an error.
        """
        if self._structure_slot is not None and self._structure_slot.slot == layer_slot:
            return (map_index, layer_slot, cell) in self._structural_cells
        if self._authored_cells.get((map_index, layer_slot, cell)) is not None:
            return True
        if self._editor is None:
            return False
        try:
            working = self._working_pointer(layer_slot, cell)
            committed = self._editor.committed_pointer(map_index, layer_slot, cell)
        except _EDIT_ERRORS:
            return False
        # CQA-26: an unread cell has nothing to revert, and comparing the sentinel
        # against the committed pointer would otherwise report a staged paint.
        return working != _UNREAD_POINTER and working != committed

    def _reselect_layer(self) -> None:
        """Re-point the editor at the selected slot after the structure changed.

        A project mutation can add, resize or remove a layer another tab authored, and
        a slot that was the canonical record a moment ago can be the project's own
        grid now (or the other way round), so the slot adapter is rebuilt from the
        cached merged document. One rebuild, and no extra project read (CQA-07).
        """
        if self._current is None or self._target is None:
            return
        if self._slot is not None:
            selected = self._slot.slot
        elif self._structure_slot is not None:
            selected = self._structure_slot.slot
        else:
            selected = None
        self._populate_layer_combo(selected, preserve=True)

    def _refresh_structure(self) -> None:
        """Read the project's structural document ONCE, then rebuild the view.

        The one read of ``maps/structure.toml``: called from a session change and a
        project mutation, never from a paint, a repaint or a form refresh (CQA-07).
        """
        self._structure = None
        self._structure_unavailable = ""
        self._structure_read_error = ""
        if self._session.project_dir is not None:
            try:
                self._structure = read_map_structure(self._session.project_dir)
            except _STRUCTURE_VIEW_ERRORS as exc:
                # Reported twice on purpose, and neither is a duplicate: the
                # structure section states why *editing* is unavailable, and the
                # status line states that the project could not be read at all.
                # Only the second survives a refresh later in the same slot - the
                # panel is a passive label a mutation may not have in view, and a
                # project mutation is exactly when nobody is looking at the panel.
                # `_update_status` re-publishes this sentence on every refresh, so
                # it is not overwritten by the working readout a moment later.
                self._structure_read_error = (
                    f"Project structure could not be read: {exc}"
                )
                self._structure_unavailable = (
                    f"the project's map structure could not be read: {exc}"
                )
        self._rebuild_structure_view()

    def _rebuild_structure_view(self) -> None:
        """Merge the staged structural edits over the committed document.

        No I/O at all: this is what a staging gesture, an undo and a redo call, so a
        staged grid change never costs a project read (CQA-07). It invalidates the
        per-map targets and the rendered chunk bodies, because both are derived from
        the grid that just changed.
        """
        self._staged_document = None
        self._resizer = None
        self._painter = None
        if not self._structure_unavailable:
            committed = self._structure if self._structure is not None else MapStructure()
            resizes = dict(committed.resizes)
            layers = dict(committed.layers)
            for (map_index, layer_slot), edit in self._staged_resizes.items():
                key = LayerResize.key_for(map_index, layer_slot)
                if edit is None:
                    resizes.pop(key, None)
                else:
                    resizes[edit.key] = edit
            for identity, layer in self._staged_layers.items():
                if layer is None:
                    layers.pop(identity, None)
                else:
                    layers[identity] = layer
            document = MapStructure(
                resizes=dict(sorted(resizes.items())),
                layers=dict(sorted(layers.items())),
            )
            self._staged_document = document
            self._build_structure_facades(document)
        self._structure_targets = {}
        self._structural_images = {}

    def structure_supported(self) -> bool:
        """Whether this session names an image whose map structure may be read.

        The canonical image only. A verified derivative is browseable and read-only -
        its layout is reconstructed from the canonical bytes plus its manifest, and
        further authored structure belongs to the image it derives from - which is the
        same rule `_editor_session` applies to a cell edit. Failing closed here keeps
        one answer to "may this image be authored" instead of two.
        """
        return (
            self._session.identification is not None
            and self._session.authored is None
        )

    def _build_structure_facades(self, document: MapStructure) -> None:
        """The one structural resolver and the one painter over the merged document."""
        image = self._session.map_image
        if image is None or not self.structure_supported():
            self._structure_unavailable = (
                "this image is a verified DragonByte Z derivative of the canonical "
                "ROM; open the canonical ROM to change a map's structure"
                if self._session.authored is not None
                else "this image was not identified against the ROM catalog, so its "
                "map structure cannot be read"
            )
            return
        try:
            self._resizer = MapResizer(
                image, structure=document, profile=self._session.profile
            )
            self._painter = MapPainter(
                image, profile=self._session.profile, structure=document
            )
        except _STRUCTURE_VIEW_ERRORS as exc:
            self._resizer = None
            self._painter = None
            self._structure_unavailable = (
                f"this image's map structure cannot be read: {exc}"
            )

    def _structure_target_for(self, map_index: int) -> StructureTarget | None:
        """One map's structural view, memoized for the life of one merged document."""
        if self._resizer is None:
            return None
        cached = self._structure_targets.get(map_index)
        if cached is None:
            try:
                cached = self._resizer.target(map_index)
            except _STRUCTURE_VIEW_ERRORS as exc:
                self._structure_unavailable = str(exc)
                return None
            self._structure_targets[map_index] = cached
        return cached

    # -- structural layers in the existing editor ----------------------------

    def _structural_layout_slot(self, layer: StructuralLayer) -> LayoutSlot | None:
        """One project-authored grid, as the map editor's own slot type.

        The geometry, the effective cell pointers and the permitted brush values all
        come from `MapPainter`'s structural resolution - the same authority the build
        and the project writer use - so this adapter cannot offer a cell the grid does
        not have or a chunk the layer may not place. Only the *write* path differs
        from a canonical layer's, because a cell that exists only in the authored
        grid has no four-byte field to rewrite.
        """
        index = self._current.index if self._current is not None else None
        if index is None or self._painter is None:
            return None
        try:
            paint = self._painter.layer(index, layer.slot)
        except _STRUCTURE_VIEW_ERRORS:
            return None
        grid = LayoutGrid(paint.columns, paint.rows)
        cells = tuple(
            LayoutCell(
                cell=cell.cell,
                column=cell.column,
                row=cell.row,
                pointer=cell.pointer,
                offset=cell.offset,
            )
            for cell in paint.cells
        )
        return LayoutSlot(
            slot=paint.slot,
            classification=paint.classification,
            handler=paint.handler,
            grid=grid,
            cells=cells,
            choices=tuple(chunk.pointer for chunk in paint.vocabulary),
            read_only_reason=paint.read_only_reason,
        )

    def _structural_layer_selected(self) -> bool:
        return self._structure_slot is not None

    def _structural_ordinal(self, layer: StructuralLayer, cell: int) -> int | None:
        """The ordinal one cell of a project-authored grid currently holds."""
        index = self._current.index if self._current is not None else None
        if index is None:
            return None
        key = (index, layer.slot, cell)
        staged = self._structural_cells.get(key)
        if staged is not None:
            return staged
        committed = self._structural_committed.get(key)
        if committed is not None:
            return committed
        if layer.contains(cell) and layer.cells[cell]:
            return layer.ordinal_of(layer.cells[cell])
        return None

    def _structural_staged_value(self, layer: StructuralLayer, cell: int) -> int | None:
        """The *staged* value one cell carries, or None for "no staged paint"."""
        index = self._current.index if self._current is not None else None
        if index is None:
            return None
        return self._structural_cells.get((index, layer.slot, cell))

    def _structural_pointer(self, layer: StructuralLayer, cell: int) -> int:
        """The chunk pointer one cell of a project-authored grid shows."""
        ordinal = self._structural_ordinal(layer, cell)
        if ordinal is not None:
            choice = layer.chunk(ordinal)
            if choice is not None:
                return choice.address
        if layer.contains(cell):
            return layer.cells[cell]
        return 0

    def _structural_marker(self, layer: StructuralLayer) -> str:
        """How a project-authored grid is named wherever a layer is listed."""
        if layer.identity is not None:
            return f"authored {self._authored_name(layer.identity)}"
        return "resized"

    def _structural_edit_for(
        self, map_index: int, layer_slot: int
    ) -> tuple["LayerResize | None", object]:
        """The staged resize and authored layer one slot carries, either possibly None."""
        resize = self._staged_resizes.get(
            (map_index, layer_slot),
            None
            if self._structure is None
            else self._structure.resize_for(map_index, layer_slot),
        )
        authored = None
        for identity, layer in self._staged_layers.items():
            if layer is not None and (layer.map_index, layer.layer_slot) == (
                map_index,
                layer_slot,
            ):
                authored = layer
                break
        if authored is None and self._structure is not None:
            authored = self._structure.layer_at(map_index, layer_slot)
        return resize, authored

    # -- structural commands: validation, staging and history ----------------

    def preview_resize(self, columns: int, rows: int, fill) -> ResizePreview:
        """Validate a resize through the SDK and state what it would do. No write.

        Every refusal this surface can give is the SDK's own reason, raised as
        ``MapStructureError``: a shrink, a no-op, an unsupported slot, a grid outside
        the supported 1..8 per axis, and an initialization chunk outside the layer's
        vocabulary. The new extent is read from the same resolution the build uses,
        so the preview cannot promise a camera reach the build would not write.
        """
        index = self._current.index if self._current is not None else None
        if self._resizer is None or index is None or self._slot is None:
            raise MapStructureError(self._structure_refusal())
        target = self._structure_target_for(index)
        if target is None:
            raise MapStructureError(self._structure_refusal())
        layer = target.layer(self._slot.slot)
        edit = self._resizer.resize(index, layer.slot, columns, rows, fill)
        extent = (target.extent_x, target.extent_y)
        new_extent = [extent[0], extent[1]]
        resolved = resolve_layer_record(
            self._session.map_image, edit, profile=self._session.profile
        )
        for axis, _field, required in resolved.extent_changes:
            # The stored word is `extent - 1`, which is exactly the arithmetic the
            # engine's own camera clamp performs; the surface states pixels.
            new_extent[0 if axis == "x" else 1] = required + 1
        choice = layer.chunk(fill) if type(fill) is int else None
        fill_label = choice.label if choice is not None else str(fill)
        summary = resize_summary(
            f"BG{layer.slot}",
            (layer.columns, layer.rows),
            edit.columns,
            edit.rows,
            fill_label,
            extent,
            (new_extent[0], new_extent[1]),
        )
        return ResizePreview(edit, summary, (new_extent[0], new_extent[1]))

    def apply_resize(self, columns: int, rows: int, fill) -> bool:
        """Validate and stage ONE resize as ONE undoable command.

        Validation happens BEFORE anything is staged, through the SDK, and every
        refusal is the SDK's own reason in a `QMessageBox` - which is what keeps a
        shrink, a no-op or an unsupported slot from ever reaching the project.
        """
        if self._current is None or self._slot is None or self._resizer is None:
            QMessageBox.warning(self, "Resize layer", self._structure_refusal())
            return False
        try:
            preview = self.preview_resize(columns, rows, fill)
        except _STRUCTURE_ERRORS as exc:
            QMessageBox.warning(self, "Resize layer", str(exc))
            return False
        index, layer_slot = self._current.index, self._slot.slot
        previous, _authored = self._structural_edit_for(index, layer_slot)
        if previous == preview.edit:
            self._publish_status(
                "That resize is already staged for this layer; nothing changed."
            )
            return False
        self._stage_resize_value(index, layer_slot, preview.edit)
        self._rebuild_structure_view()
        command = ResizeCommand(self, index, layer_slot, previous, preview.edit)
        self._undo_stack.push(command)
        self._after_structure_change(index)
        self._publish_status(
            f"Staged {preview.summary}. Apply to project to write it."
        )
        return True

    def _stage_resize_value(
        self, map_index: int, layer_slot: int, edit: "LayerResize | None"
    ) -> None:
        """Record one staged resize, or forget it when it matches the project.

        A staged value that equals the project's own is not staged work: keeping it
        would make an undo of a resize look like a staged *removal*, and the pending
        count and the "staged change" line would both claim work that does not exist.
        """
        committed = (
            None if self._structure is None else self._structure.resize_for(map_index, layer_slot)
        )
        key = (map_index, layer_slot)
        if edit == committed:
            self._staged_resizes.pop(key, None)
        else:
            self._staged_resizes[key] = edit

    def _stage_layer_value(
        self, identity: str, layer: "AuthoredLayer | None"
    ) -> None:
        """Record one staged authored layer, or forget it when it matches the project."""
        committed = (
            None if self._structure is None else self._structure.layers.get(identity)
        )
        if layer == committed:
            self._staged_layers.pop(identity, None)
        else:
            self._staged_layers[identity] = layer

    def _after_structure_change(self, map_index: int) -> None:
        """Re-point the editor at the new grids, without re-reading the project."""
        selected = self._slot.slot if self._slot is not None else None
        self._populate_layer_combo(selected)
        if self._current is not None and self._current.index == map_index:
            self._repopulate_structural_checks()
            self._refresh_preview()
        self._refresh_editor_state()

    def _repopulate_structural_checks(self) -> None:
        """Re-offer the layer-visibility check boxes, keeping the current selection."""
        checked = {slot: box.isChecked() for slot, box in self._layer_checks.items()}
        self._populate_layer_checks()
        for slot, box in self._layer_checks.items():
            if slot in checked:
                box.blockSignals(True)
                box.setChecked(checked[slot])
                box.blockSignals(False)

    def _reapply_resize(self, command: "ResizeCommand") -> None:
        self._stage_resize_value(command.map_index, command.layer_slot, command.applied)
        self._rebuild_structure_view()
        self._after_structure_change(command.map_index)

    def _reverse_resize(self, command: "ResizeCommand") -> None:
        self._stage_resize_value(command.map_index, command.layer_slot, command.previous)
        self._rebuild_structure_view()
        self._after_structure_change(command.map_index)

    # -- structural commands: the two forms ----------------------------------

    def build_resize_dialog(self) -> "ResizeLayerDialog | None":
        """The resize form, built but not shown. None when it cannot be offered.

        A Qt slot, so every SDK family it can meet is caught here: the refusal is
        reported where the user can see it, never left to stderr. Building and
        showing are separate calls because a caller that drives the surface without a
        mouse (a test, the QA harness) needs the form without its modal loop.
        """
        if self._current is None or self._slot is None or self._resizer is None:
            QMessageBox.warning(self, "Resize layer", self._structure_refusal())
            return None
        index = self._current.index
        try:
            target = self._structure_target_for(index)
            if target is None:
                raise MapStructureError(self._structure_refusal())
            layer = target.layer(self._slot.slot)
        except _STRUCTURE_VIEW_ERRORS as exc:
            QMessageBox.warning(self, "Resize layer", str(exc))
            return None
        return ResizeLayerDialog(
            self,
            layer=layer,
            extent=(target.extent_x, target.extent_y),
            preview=self.preview_resize,
            apply_command=self.apply_resize,
            current=(layer.columns, layer.rows),
        )

    def open_resize_dialog(self) -> "ResizeLayerDialog | None":
        """The resize command's form, shown modally."""
        dialog = self.build_resize_dialog()
        if dialog is None:
            return None
        dialog.exec()
        return dialog

    def preview_new_layer(
        self, name: str, layer_slot: int, template_slot: int, columns: int, rows: int, fill
    ) -> ResizePreview:
        """Validate a new layer through the SDK and state what it would do.

        ``ResizePreview`` carries the ``AuthoredLayer`` here rather than a
        ``LayerResize``; the shape is the same because both are "a validated value
        plus the line that says what it means".
        """
        index = self._current.index if self._current is not None else None
        if self._resizer is None or index is None:
            raise MapStructureError(self._structure_refusal())
        edit = self._resizer.authored_layer(
            name,
            index,
            layer_slot,
            _template_text(index, template_slot),
            columns,
            rows,
            fill,
        )
        template = self._structure_target_for(index)
        template_label = (
            template.layer(template_slot).label if template is not None else "the template"
        )
        choice = None
        for candidate in self.template_vocabulary(index, template_slot):
            if candidate.ordinal == fill:
                choice = candidate
        summary = (
            f"{edit.identity} \u00b7 new BG{layer_slot} on map:{index:04d} \u00b7 "
            f"{_grid_text(columns, rows)} from {template_label} \u00b7 initialized to "
            f"{choice.label if choice is not None else fill}"
        )
        return ResizePreview(edit, summary, (0, 0))

    def apply_new_layer(
        self, name: str, layer_slot: int, template_slot: int, columns: int, rows: int, fill
    ) -> bool:
        """Validate and stage ONE new layer as ONE undoable command."""
        if self._current is None or self._resizer is None:
            QMessageBox.warning(self, "New layer", self._structure_refusal())
            return False
        try:
            preview = self.preview_new_layer(
                name, layer_slot, template_slot, columns, rows, fill
            )
        except _STRUCTURE_ERRORS as exc:
            QMessageBox.warning(self, "New layer", str(exc))
            return False
        edit = preview.edit
        committed = None if self._structure is None else self._structure.layers.get(edit.identity)
        if committed is not None or self._staged_layers.get(edit.identity) is not None:
            QMessageBox.warning(
                self,
                "New layer",
                f"{edit.identity} already exists in this project.",
            )
            return False
        index = self._current.index
        self._stage_layer_value(edit.identity, edit)
        self._rebuild_structure_view()
        command = NewLayerCommand(self, edit.identity, None, edit)
        self._undo_stack.push(command)
        self._after_structure_change(index)
        self._publish_status(f"Staged {preview.summary}. Apply to project to write it.")
        return True

    def build_new_layer_dialog(self) -> "NewLayerDialog | None":
        """The layer-authoring form, built but not shown. None when it cannot be offered."""
        index = self._current.index if self._current is not None else None
        if index is None or self._resizer is None:
            QMessageBox.warning(self, "New layer", self._structure_refusal())
            return None
        try:
            target = self._structure_target_for(index)
            if target is None:
                raise MapStructureError(self._structure_refusal())
            free = target.free_slots
            templates = self.layer_templates(index)
        except _STRUCTURE_VIEW_ERRORS as exc:
            QMessageBox.warning(self, "New layer", str(exc))
            return None
        if not free:
            QMessageBox.warning(
                self,
                "New layer",
                f"map:{index:04d} leaves no layer slot unused"
                + (
                    f": {target.read_only_reason}"
                    if target.read_only_reason
                    else ""
                ),
            )
            return None
        if not templates:
            QMessageBox.warning(
                self,
                "New layer",
                f"map:{index:04d} has no supported dominant layer to copy a new "
                "layer from",
            )
            return None
        return NewLayerDialog(
            self,
            map_index=index,
            free_slots=free,
            templates=templates,
            vocabulary_for=lambda slot: self.template_vocabulary(index, slot),
            preview=self.preview_new_layer,
            apply_command=self.apply_new_layer,
            default_name=f"map{index:04d}-bg{free[0]}",
        )

    def open_new_layer_dialog(self) -> "NewLayerDialog | None":
        """The layer-authoring form, shown modally."""
        dialog = self.build_new_layer_dialog()
        if dialog is None:
            return None
        dialog.exec()
        return dialog

    # -- MAP-NEW-AUTHORING-001: a new map identity --------------------------

    def new_map_donors(self):
        """Every canonical map as a donor, with the browser's own labels."""
        return [(entry.index, entry.label)
                for entry in sorted(self._entries.values(),
                                    key=lambda item: item.index)]

    def used_map_keys(self):
        """Every engine key this image already uses, plus the project's own."""
        import struct

        image = self._session.map_image
        profile = self._session.profile
        used = set()
        if image is None or profile is None:
            return used
        layout = profile.map_entries
        if layout is None:
            return used
        offset = layout.address.to_file_offset(len(image))
        for index in range(layout.count):
            at = offset + index * layout.record_size
            used.add(struct.unpack_from("<BB", image, at))
        window = self._session.project_dir
        if window is not None:
            try:
                for item in map_new.authored_maps(window).ordered():
                    used.add(item.key)
            except (ProjectError, OSError):
                pass
        return used

    def next_map_key(self):
        """The first unused engine key above the canonical corpus's own range."""
        used = self.used_map_keys()
        for high in range(0x17, 0x100):
            for low in range(1, 0x100):
                if (high, low) not in used:
                    return (high, low)
        return (0x99, 0x01)

    def _draft_new_map(self, name: str, donor: int, key_high: int,
                       key_low: int) -> "AuthoredMaps":
        """The document this form's fields would write, or the model's refusal."""
        previous = map_new.authored_maps(self._session.project_dir)
        item = AuthoredMap(name=name, donor=donor, key_high=key_high,
                           key_low=key_low)
        return AuthoredMaps(maps={**previous.maps, item.name: item})

    def preview_new_map(self, name: str, donor: int, key_high: int,
                        key_low: int) -> str:
        """Run the SDK's own plan against the open image and state the verdict."""
        document = self._draft_new_map(name, donor, key_high, key_low)
        image = self._session.map_image
        identification = self._session.identification
        profile = self._session.profile
        if image is None or identification is None or profile is None:
            raise map_new.MapAuthoringError(
                "opening a ROM is what makes a map authorable")
        map_new.validate_authored_maps(image, identification, profile, document)
        item = document.maps[name]
        position = sorted(document.maps).index(name)
        index = profile.map_entries.count + position
        return (f"Creates map:{index:04d} key 0x{key_high:02X}{key_low:02X} from "
                f"donor map:{donor:04d}: the map table is re-emitted with this row "
                "appended, and the two engine sites that name the table and its "
                "bound are repointed.")

    def apply_new_map(self, name: str, donor: int, key_high: int,
                      key_low: int) -> bool:
        """Validate, write and stage ONE new map as ONE undoable command."""
        if self._session.project_dir is None:
            QMessageBox.warning(
                self, "New map",
                "Open or extract a project first: a new map identity is stored in "
                "the project's own maps/authored.toml.")
            return False
        try:
            document = self._draft_new_map(name, donor, key_high, key_low)
            previous = map_new.authored_maps(self._session.project_dir)
            self.preview_new_map(name, donor, key_high, key_low)
        except (map_new.MapAuthoringError, ProjectError, OSError) as exc:
            QMessageBox.warning(self, "New map", str(exc))
            return False
        try:
            map_new.apply_authored_maps(self._session.project_dir, document,
                                        canonical_rows=self._map_row_count())
        except (ProjectError, OSError, map_new.MapAuthoringError) as exc:
            QMessageBox.warning(self, "New map", str(exc))
            return False
        self._undo_stack.push(NewMapCommand(
            self, previous, document,
            f"Create map-new:{name} from map:{donor:04d}"))
        self._session.project_mutated()
        self._publish_status(
            f"Staged map-new:{name} \u00b7 Apply to project is already written; "
            "Build compiles it into the image.")
        return True

    def write_authored_maps_document(self, document: "AuthoredMaps") -> None:
        """The one write path the new-map command uses, for redo and undo."""
        if self._session.project_dir is None:
            return
        try:
            map_new.apply_authored_maps(self._session.project_dir, document,
                                        canonical_rows=self._map_row_count())
        except (ProjectError, OSError, map_new.MapAuthoringError) as exc:
            QMessageBox.warning(self, "New map", str(exc))
            return
        self._session.project_mutated()
        self._publish_status("New-map document restored.")

    def _map_row_count(self) -> "int | None":
        """The open image's canonical map row count, or None without an image."""
        profile = self._session.profile
        layout = getattr(profile, "map_entries", None) if profile else None
        return layout.count if layout is not None else None

    def build_new_map_dialog(self) -> "NewMapDialog | None":
        """The new-map form, built but not shown. None when it cannot be offered."""
        image = self._session.map_image
        identification = self._session.identification
        profile = self._session.profile
        if image is None or identification is None or profile is None:
            QMessageBox.warning(
                self, "New map",
                "Open a supported ROM first: a new map identity is planned against "
                "the image it will be built from.")
            return None
        if self._session.project_dir is None:
            QMessageBox.warning(
                self, "New map",
                "Open or extract a project first: a new map identity is stored in "
                "the project's own maps/authored.toml.")
            return None
        donors = self.new_map_donors()
        if not donors:
            QMessageBox.warning(self, "New map", "this image lists no map to copy")
            return None
        default_donor = (self._current.index if self._current is not None
                         else donors[0][0])
        return NewMapDialog(
            self,
            donors=donors,
            default_name=f"map{profile.map_entries.count:04d}",
            default_donor=default_donor,
            default_key=self.next_map_key(),
            preview=self.preview_new_map,
            apply_command=self.apply_new_map,
        )

    def open_new_map_dialog(self) -> "NewMapDialog | None":
        """The new-map form, shown modally."""
        dialog = self.build_new_map_dialog()
        if dialog is None:
            return None
        dialog.exec()
        return dialog

    def _reapply_layer(self, command: "NewLayerCommand") -> None:
        self._stage_layer_value(command.identity, command.applied)
        self._rebuild_structure_view()
        self._after_structure_change(
            command.applied.map_index
            if command.applied is not None
            else command.previous.map_index
        )

    def _reverse_layer(self, command: "NewLayerCommand") -> None:
        self._stage_layer_value(command.identity, command.previous)
        self._rebuild_structure_view()
        self._after_structure_change(
            command.applied.map_index
            if command.applied is not None
            else command.previous.map_index
        )

    # -- structural commands: reverting --------------------------------------

    def _slot_cell_holders(self, map_index: int, layer_slot: int) -> int:
        """How many layout cells name this slot, committed or staged.

        The same rule `remove_authored_layer` enforces on the project side, stated
        against what the surface can see so the user is told before the write rather
        than by it.
        """
        committed = sum(
            1
            for key in list(self._structural_committed) + list(self._authored_committed)
            if (key[0], key[1]) == (map_index, layer_slot)
        )
        staged = sum(
            1
            for key in list(self._structural_cells) + list(self._authored_cells)
            if (key[0], key[1]) == (map_index, layer_slot)
        )
        return committed + staged

    def revert_selected_structure(self) -> bool:
        """Un-stage the selected layer's structural change, or stage its removal.

        Two states, one command. A slot with a *staged* change returns to what the
        project holds - the same "revert means un-stage" rule the cell revert uses -
        and a slot the *project* authored is staged for removal, which the next Apply
        writes through the SDK's own `clear_layer_resize`/`remove_authored_layer`. A
        layer that still holds authored cell content is refused with the reason,
        because removing it would leave those cells naming a slot the project no
        longer declares.
        """
        index = self._current.index if self._current is not None else None
        if index is None or self._slot is None:
            return False
        layer_slot = self._slot.slot
        staged_resize, staged_layer = self._structural_edit_for(index, layer_slot)
        committed_resize = (
            None if self._structure is None else self._structure.resize_for(index, layer_slot)
        )
        committed_layer = (
            None if self._structure is None else self._structure.layer_at(index, layer_slot)
        )
        staged_key = (index, layer_slot)
        if staged_key in self._staged_resizes or (
            staged_layer is not None and staged_layer.identity in self._staged_layers
        ):
            before_resize = self._staged_resizes.get(staged_key)
            before_layer = (
                None
                if staged_layer is None
                else self._staged_layers.get(staged_layer.identity)
            )
            self._naming_structure_revert = True
            try:
                if staged_layer is not None:
                    command = NewLayerCommand(
                        self, staged_layer.identity, before_layer, committed_layer
                    )
                else:
                    command = ResizeCommand(
                        self, index, layer_slot, before_resize, committed_resize
                    )
            finally:
                self._naming_structure_revert = False
            # Un-staging returns the slot to what the PROJECT holds, which is what
            # makes an undo of this gesture restore the staged value again.
            if staged_layer is not None:
                self._stage_layer_value(staged_layer.identity, committed_layer)
            else:
                self._stage_resize_value(index, layer_slot, committed_resize)
            self._rebuild_structure_view()
            self._undo_stack.push(command)
            self._after_structure_change(index)
            self._publish_status(
                "Un-staged the structural change on "
                f"map:{index:04d} BG{layer_slot}; the project keeps what it holds."
            )
            return True
        if committed_resize is None and committed_layer is None:
            self._publish_status(
                "This layer carries no structural change to revert."
            )
            return False
        holders = self._slot_cell_holders(index, layer_slot)
        if holders:
            QMessageBox.warning(
                self,
                "Revert structure",
                f"map:{index:04d} BG{layer_slot} still holds {holders} authored "
                "cell(s); clear those cells before reverting the layer",
            )
            return False
        if committed_layer is not None:
            self._naming_structure_revert = True
            try:
                command = NewLayerCommand(
                    self, committed_layer.identity, committed_layer, None
                )
            finally:
                self._naming_structure_revert = False
            self._stage_layer_value(committed_layer.identity, None)
        else:
            self._naming_structure_revert = True
            try:
                command = ResizeCommand(self, index, layer_slot, committed_resize, None)
            finally:
                self._naming_structure_revert = False
            self._stage_resize_value(index, layer_slot, None)
        self._rebuild_structure_view()
        self._undo_stack.push(command)
        self._after_structure_change(index)
        self._publish_status(
            f"Staged the removal of the project's own structural change on "
            f"map:{index:04d} BG{layer_slot}. Apply to project to write it."
        )
        return True

    # -- structural staging: what Apply writes -------------------------------

    def _staged_resize_edits(self) -> dict[tuple[int, int], "LayerResize | None"]:
        """Staged resizes that would actually change the project."""
        structure = self._structure if self._structure is not None else MapStructure()
        return staged_changes(
            self._staged_resizes,
            {key: structure.resize_for(*key) for key in self._staged_resizes},
        )

    def _staged_layer_edits(self) -> dict[str, "AuthoredLayer | None"]:
        """Staged authored layers that would actually change the project."""
        structure = self._structure if self._structure is not None else MapStructure()
        return staged_changes(self._staged_layers, structure.layers)

    def _staged_structural_cells(self) -> dict[tuple[int, int, int], int | None]:
        """Staged paints on project-authored grids, as the layout batch spells them."""
        return staged_changes(self._structural_cells, self._structural_committed)

    def _write_staged_structure(self, *, removals: bool) -> bool:
        """Write the staged structural edits through the SDK, in the safe order.

        Creations and resizes are written BEFORE the cells they carry (a cell in a
        grown grid is only a legal layout cell once the grid exists) and removals
        AFTER them (a removed layer must not still be named). One SDK call per
        staged edit, and each returns whether project source actually changed.
        """
        if self._session.project_dir is None or self._session.map_image is None:
            return False
        changed = False
        resizes = self._staged_resize_edits()
        layers = self._staged_layer_edits()
        if removals:
            for (map_index, layer_slot), edit in sorted(resizes.items()):
                if edit is not None:
                    continue
                if clear_layer_resize(
                    self._session.project_dir,
                    self._session.map_image,
                    map_index,
                    layer_slot,
                    profile=self._session.profile,
                ):
                    changed = True
            for identity, layer in sorted(layers.items()):
                if layer is not None:
                    continue
                if remove_authored_layer(self._session.project_dir, identity):
                    changed = True
            return changed
        for (map_index, layer_slot), edit in sorted(resizes.items()):
            if edit is None:
                continue
            if set_layer_resize(
                self._session.project_dir,
                self._session.map_image,
                edit,
                profile=self._session.profile,
            ):
                changed = True
        for identity, layer in sorted(layers.items()):
            if layer is None:
                continue
            if set_authored_layer(
                self._session.project_dir,
                self._session.map_image,
                layer,
                profile=self._session.profile,
            ):
                changed = True
        return changed

    # -- the structure section ------------------------------------------------

    def _structure_rows(self) -> tuple[tuple, ...]:
        """One row per layer slot: identity, size, form and whether it is editable."""
        result = self._current
        if result is None:
            return ()
        target = self._structure_target_for(result.index)
        if target is None:
            return ()
        rows = []
        for layer in target.slots:
            where = (
                f"authored {self._authored_name(layer.identity)}"
                if layer.identity is not None
                else ("project resize" if layer.resized else "source image")
            )
            size = (
                _grid_text(layer.columns, layer.rows)
                if layer.columns and layer.rows
                else "no grid"
            )
            handler = f"handler {layer.handler:#010x}"
            detail = layer.read_only_reason or (
                f"{size} chunks \u00b7 {layer.width}\u00d7{layer.height} px \u00b7 "
                f"{layer.classification} \u00b7 {where} \u00b7 {handler}"
            )
            rows.append(
                (
                    layer.slot,
                    f"BG{layer.slot} \u00b7 {size} \u00b7 {layer.classification} \u00b7 {where}",
                    detail,
                    layer.editable,
                )
            )
        return tuple(rows)

    def _sync_structure_controls(self) -> None:
        """Bring the structure section up to date from cached state.

        Called from every editor refresh, so it reads no file and allocates no
        widget unless a row's text actually changed (CQA-07's rule that a repaint
        never rebuilds what it can reuse).
        """
        rows = self._structure_rows()
        signature = tuple((slot, text) for slot, text, _detail, _ok in rows)
        if signature != self._structure_row_signature:
            self._structure_row_signature = signature
            self._suppress_structure_list = True
            self._structure_list.blockSignals(True)
            self._structure_list.clear()
            for slot, text, detail, editable in rows:
                item = QListWidgetItem(text)
                item.setData(_IDENTITY_ROLE, slot)
                item.setToolTip(detail)
                if not editable:
                    item.setForeground(theme.color("text_muted"))
                self._structure_list.addItem(item)
            self._structure_list.blockSignals(False)
            self._suppress_structure_list = False
            self._fit_structure_list()
        selected = self._slot.slot if self._slot is not None else None
        self._suppress_structure_list = True
        if selected is None:
            self._structure_list.setCurrentRow(-1)
        else:
            for row in range(self._structure_list.count()):
                if self._structure_list.item(row).data(_IDENTITY_ROLE) == selected:
                    self._structure_list.setCurrentRow(row)
                    break
        self._suppress_structure_list = False
        self._update_structure_labels()

    def _fit_structure_list(self) -> None:
        """Make the layer list exactly as tall as the slot rows it holds.

        The engine's layer count is fixed at four, so this list never scrolls and
        never needs slack - but a `QListWidget`'s own size hint reserves far more
        than its rows (measured: 192 px for four 20 px rows), and that dead space
        was what the panel spent instead of showing its own Apply and Save As
        buttons at the default window size.
        """
        rows = self._structure_list.count()
        if not rows:
            return
        self._structure_list.setFixedHeight(
            rows * self._structure_list.sizeHintForRow(0)
            + 2 * self._structure_list.frameWidth()
        )

    def _update_structure_labels(self) -> None:
        result = self._current
        if result is None:
            self._structure_state.setText("No map is selected.")
            self._structure_extent.setText("")
            self._structure_support.setText("")
            self._structure_staged.setText("")
            self._set_structure_buttons(False, False, False)
            return
        index = result.index
        target = self._structure_target_for(index)
        if target is None:
            self._structure_state.setText(f"map:{index:04d} \u00b7 no structural view")
            self._structure_extent.setText("")
            self._structure_support.setText(
                self._structure_unavailable or "this map's structure could not be read"
            )
            self._structure_staged.setText("")
            self._set_structure_buttons(False, False, False)
            return
        self._structure_extent.setText(
            f"map extent {target.extent_x} \u00d7 {target.extent_y} px \u00b7 "
            f"{len(target.free_slots)} unused slot(s)"
        )
        slot = self._slot.slot if self._slot is not None else None
        if slot is None or not any(row[0] == slot for row in self._structure_rows()):
            self._structure_state.setText("No layer selected.")
            self._structure_support.setText(
                "Select a layer to see whether it can be resized."
            )
        else:
            layer = target.layer(slot)
            source = (
                f"authored layer {self._authored_name(layer.identity)}"
                if layer.identity is not None
                else ("project resized grid" if layer.resized else "source image grid")
            )
            self._structure_state.setText(
                f"{layer.label} \u00b7 {layer.classification} \u00b7 {source}"
            )
            if target.shared_with:
                self._structure_support.setText(f"Read only \u00b7 {target.read_only_reason}")
            elif layer.editable:
                self._structure_support.setText(
                    "Supported \u00b7 a supported dominant chunk grid; a resize may "
                    "grow it and never shrink it"
                )
            else:
                self._structure_support.setText(f"Read only \u00b7 {layer.read_only_reason}")
        staged = self._staged_structure_lines(index)
        self._structure_staged.setText(
            " \u00b7 ".join(staged) if staged else "no staged structural change on this map"
        )
        resizable = (
            slot is not None
            and self._resizer is not None
            and not target.shared_with
            and target.layer(slot).editable
        )
        creatable = self._resizer is not None and bool(target.free_slots)
        revertible = slot is not None and (
            (index, slot) in self._staged_resizes
            or any(
                layer is not None and (layer.map_index, layer.layer_slot) == (index, slot)
                for layer in self._staged_layers.values()
            )
            or (
                self._structure is not None
                and (
                    self._structure.resize_for(index, slot) is not None
                    or self._structure.layer_at(index, slot) is not None
                )
            )
        )
        self._set_structure_buttons(resizable, creatable, revertible)

    def _set_structure_buttons(
        self, resizable: bool, creatable: bool, revertible: bool
    ) -> None:
        editing = self._edit_mode
        project = self._session.project_dir is not None
        self._resize_button.setEnabled(editing and resizable)
        self._resize_button.setToolTip(
            "Grow the selected layer's chunk grid; the source cells stay where they are"
            if editing and resizable
            else self._structure_refusal()
        )
        self._new_layer_button.setEnabled(editing and creatable and project)
        self._new_layer_button.setToolTip(
            "Activate a layer slot the source image leaves unused"
            if editing and creatable and project
            else (
                "Open or extract a project first: a layer is stored in the project."
                if not project
                else "No slot on this map is unused."
            )
        )
        self._revert_structure_button.setEnabled(editing and revertible)
        self._revert_structure_button.setToolTip(
            "Un-stage this layer's structural change, or stage the removal of the "
            "project's own"
            if editing and revertible
            else "This layer carries no structural change to revert."
        )

    def _staged_structure_lines(self, map_index: int) -> list[str]:
        """One line per staged structural change on one map, in durable order."""
        lines = []
        for (index, slot), edit in sorted(self._staged_resizes.items()):
            if index != map_index:
                continue
            if edit is None:
                lines.append(f"BG{slot} \u2192 source grid (removal staged)")
            else:
                lines.append(
                    f"BG{slot} \u2192 {_grid_text(edit.columns, edit.rows)} (resize staged)"
                )
        for identity, layer in sorted(self._staged_layers.items()):
            if layer is None:
                committed = (
                    None
                    if self._structure is None
                    else self._structure.layers.get(identity)
                )
                if committed is not None and committed.map_index == map_index:
                    lines.append(f"BG{committed.layer_slot} \u2192 removed (staged)")
                continue
            if layer.map_index != map_index:
                continue
            lines.append(
                f"BG{layer.layer_slot} \u2192 {identity} "
                f"{_grid_text(layer.columns, layer.rows)} (new layer staged)"
            )
        return lines

    def _on_structure_row_selected(self, row: int) -> None:
        """Selecting a slot row selects that layer in the editor, when it can be."""
        if self._suppress_structure_list or row < 0:
            return
        item = self._structure_list.item(row)
        if item is None:
            return
        slot = item.data(_IDENTITY_ROLE)
        combo_row = self._layer_combo.findData(slot)
        if combo_row < 0:
            self._publish_status(
                f"BG{slot} cannot be edited here: {item.toolTip()}"
            )
            return
        self._layer_combo.setCurrentIndex(combo_row)

    # -- structural rendering -------------------------------------------------

    def _structural_plane(self, layer: StructuralLayer, map_index: int):
        """One project-authored grid as indexed pixels, or None when nothing draws.

        The canonical renderer draws the record the canonical image holds, and a
        resized or authored grid is by definition not in that record - the record a
        build materializes does not exist before the build. So the accepted
        primitives are fed the project's own geometry: chunk bodies come from
        `mv.render_chunk_images` (retail chunks) and `mv.render_chunk_entries`
        (authored planes) - the same two calls the palette draws its swatches with -
        and the composite still comes from `mv.compose`. Nothing is decoded,
        arranged or stitched a second way.
        """
        width = layer.columns * mv.CHUNK_PIXELS
        height = layer.rows * mv.CHUNK_PIXELS
        if not width or not height:
            return None
        plane = bytearray(width * height)
        drew = False
        for cell in range(layer.cell_count):
            image = self._structural_cell_image(layer, map_index, cell)
            if image is None:
                continue
            column, row = cell % layer.columns, cell // layer.columns
            for y in range(image.height):
                source = y * image.width
                target = (row * mv.CHUNK_PIXELS + y) * width + column * mv.CHUNK_PIXELS
                plane[target : target + image.width] = image.pixels[
                    source : source + image.width
                ]
            drew = True
        return (width, height, bytes(plane)) if drew else None

    def _structural_cell_image(self, layer: StructuralLayer, map_index: int, cell: int):
        """The chunk image one cell of a project-authored grid shows, or None."""
        ordinal = self._structural_ordinal(layer, cell)
        identity = None
        address = 0
        if ordinal is not None:
            choice = layer.chunk(ordinal)
            if choice is None:
                return None
            address = choice.address
        elif layer.contains(cell):
            address = layer.cells[cell]
            if layer.authored_cells:
                identity = layer.authored_cells[cell]
        if identity:
            entries = self._resolved_plane(identity)
            if entries is None:
                return None
            char_data = (
                self._editor.character_block(map_index)
                if self._editor is not None
                else None
            )
            try:
                return mv.render_chunk_entries(char_data, entries)
            except _EDIT_ERRORS as exc:
                self._report_plane_error(identity, str(exc))
                return None
        if not address:
            return None
        return self._structural_chunk_image(map_index, address)

    def _structural_chunk_image(self, map_index: int, address: int):
        """One retail chunk's pixels, rendered once per session and cached."""
        cached = self._structural_images.get(address)
        if cached is not None:
            return cached
        char_data = (
            self._editor.character_block(map_index) if self._editor is not None else None
        )
        try:
            images = mv.render_chunk_images(
                self._session.map_image, map_index, (address,), char_data=char_data
            )
        except _EDIT_ERRORS as exc:
            self._report_plane_error(f"chunk {address:#010x}", str(exc))
            return None
        if not images:
            return None
        self._structural_images[address] = images[0]
        return images[0]

    def _structural_preview(self) -> bool:
        """Draw this map with the project's own layer grids; False when none apply.

        The retail layers are kept exactly as `mv.render_map` produced them and only
        the layers whose grid the project owns are replaced - so a map with one
        resized layer still shows every other layer through the accepted renderer.
        """
        result = self._current
        if result is None:
            return False
        structural = {layer.slot: layer for layer in self.structural_layers(result.index)}
        if not structural:
            return False
        rendered: list[mv.MapBrowserLayer] = []
        for layer in result.layers:
            project_layer = structural.pop(layer.slot, None)
            if project_layer is None:
                rendered.append(layer)
                continue
            plane = self._structural_plane(project_layer, result.index)
            if plane is None:
                continue
            width, height, pixels = plane
            rendered.append(
                mv.MapBrowserLayer(
                    slot=layer.slot,
                    classification="dominant",
                    handler=layer.handler,
                    addend=layer.addend,
                    width=width,
                    height=height,
                    pixels=pixels,
                )
            )
        for slot, project_layer in sorted(structural.items()):
            plane = self._structural_plane(project_layer, result.index)
            if plane is None:
                continue
            width, height, pixels = plane
            rendered.append(
                mv.MapBrowserLayer(
                    slot=slot,
                    classification="dominant",
                    handler=project_layer.handler,
                    addend=0,
                    width=width,
                    height=height,
                    pixels=pixels,
                )
            )
        visible = tuple(
            layer
            for layer in rendered
            if layer.graphical
            and (
                self._layer_checks.get(layer.slot) is None
                or self._layer_checks[layer.slot].isChecked()
            )
        )
        if not visible:
            self._set_map_pixmap(QPixmap(), result.width, result.height)
            return True
        width = max(layer.width for layer in visible)
        height = max(layer.height for layer in visible)
        try:
            indices = mv.compose(visible, width, height)
        except _EDIT_ERRORS as exc:
            QMessageBox.warning(self, "Map structure", str(exc))
            return False
        pixmap = self._pixmap_from_indices(indices, width, height, result.palette)
        self._set_map_pixmap(pixmap, width, height)
        return True

    def _report_plane_error(self, key: str, message: str) -> None:
        """Report one structural render refusal once, not once per repaint."""
        if key in self._plane_error_reported:
            return
        self._plane_error_reported.add(key)
        QMessageBox.warning(self, "Map structure", f"{key}: {message}")


    # -- MAP-CHUNK-AUTHORING-001: the chunk author and the project's chunks ----
    #
    # Everything below is the authored half of this surface. The SDK authority is
    # `tools.webfoot.map_chunk`: this tab composes a chunk through `ChunkAuthor`,
    # persists it through `set_authored_chunk`, and places it through
    # `set_layout_authored_cells`. No widget here knows the entry bitfield, the
    # container layout or the vocabulary rule; the labels and refusals are the
    # SDK's own.

    def chunk_author(self) -> ChunkAuthor | None:
        """The cached read/compose facade for the open image, or None with a reason.

        Built once per session: it memoizes the layer vocabularies and pointer
        windows it reads, and re-building it per chooser refill would re-read the
        map table every time (CQA-07).
        """
        if self._chunk_author_cache is not None or self._chunk_author_error is not None:
            return self._chunk_author_cache
        if not self.chunk_authoring_supported():
            self._chunk_author_error = (
                "this image was not identified against the ROM catalog, so its "
                "chunks cannot be read"
            )
            return None
        if self._session.map_image is None:
            self._chunk_author_error = "no ROM is open"
            return None
        try:
            self._chunk_author_cache = ChunkAuthor(
                self._session.map_image, profile=self._session.profile
            )
        except _CHUNK_READ_ERRORS as exc:
            self._chunk_author_error = (
                f"this image's chunks cannot be read: {exc}"
            )
        return self._chunk_author_cache

    def chunk_authoring_supported(self) -> bool:
        """Whether this session names an image whose chunks may be read at all.

        The chunk facade resolves addresses through the ROM profile, so it is only
        meaningful for an image ``Session.open_rom`` identified against the
        catalog. A session that was never opened carries neither an identification
        nor a verified derivative, and building the facade over it would resolve a
        profile that does not describe the bytes - so the surface refuses on that
        checkable condition rather than on whatever the reader happened to raise.
        """
        return (
            self._session.identification is not None
            or self._session.authored is not None
        )

    def _reload_project_authored(self) -> None:
        """Re-read the project's chunk table and committed authored placements.

        The ONE read of the authored half of a project, called from a project
        mutation, an apply, a map selection and a session change - never from a
        repaint or a paint (CQA-07). Nothing the user staged is touched: the staged
        placements, the staged chunk documents and the open chunk editor all
        survive it, which is the CQA-05 rule for this surface.
        """
        # The documents behind the cached planes may have changed, so the planes
        # are recomputed lazily on the next read rather than stored stale.
        self._resolved_planes = {}
        if self._session.project_dir is None:
            self._project_chunks = {}
            self._authored_committed = {}
            self._structural_committed = {}
            return
        try:
            chunks = read_authored_chunks(self._session.project_dir)
        except _PROJECT_READ_ERRORS as exc:
            self._publish_status(f"Project chunks could not be read: {exc}")
            return
        try:
            cells = read_layout_edits(self._session.project_dir).cells()
        except _PROJECT_READ_ERRORS as exc:
            self._publish_status(f"Project layout could not be read: {exc}")
            return
        self._project_chunks = dict(chunks.chunks)
        self._authored_committed = {
            key: value for key, value in cells.items() if isinstance(value, str)
        }
        # MAP-RESIZE-AND-LAYERS-001. An ordinal cell on a slot whose grid the
        # project owns is a paint of that grid, not of the canonical record, and it
        # is cached here so a repaint resolves it without re-reading the project
        # (CQA-07). The classification uses the structural document just read, not a
        # second lookup.
        structural = self.structural_pairs()
        self._structural_committed = {
            key: value
            for key, value in cells.items()
            if type(value) is int and (key[0], key[1]) in structural
        }

    def _clear_authored_state(self) -> None:
        """Drop every authored fact; the session's base image has changed.

        CQA-05. A chunk body, a resolved plane and a placement identity are all
        claims about one image's map and character data, so a new image invalidates
        all of them at once - which is why this is called from
        ``on_session_changed`` alone.
        """
        self._authored_cells = {}
        self._brush_authored = None
        self._project_chunks = {}
        self._authored_committed = {}
        self._resolved_planes = {}
        self._staged_chunks = {}
        self._chunk_author_cache = None
        self._chunk_author_error = None
        self._chunk_thumbnails = {}
        self._plane_error_reported = set()
        self._close_chunk_editor_page()
        self._clear_chunk_editor_state()

    def _clear_chunk_editor_state(self) -> None:
        self._chunk_identity = None
        self._chunk_template = None
        self._chunk_template_plane = ()
        self._chunk_applied_plane = ()
        self._chunk_plane = []
        self._chunk_brush = None
        self._chunk_selected = None
        self._chunk_char_data = None
        self._chunk_hover = ""
        self._chunk_stroke = []
        self._chunk_stroke_previous = {}
        self._chunk_stroke_applied = {}
        self._chunk_stroke_first = None
        self._chunk_stroke_last = None
        self._chunk_stroke_active = False
        self._suppress_chunk_palette = False

    def _chunk_template_of(self, chunk: AuthoredChunk) -> ChunkTemplate | None:
        try:
            return ChunkTemplate.parse(chunk.template)
        except ChunkAuthoringError:
            # A hand-edited project can hold a template this build would refuse;
            # `resolve` names it, this only keeps the palette from offering it.
            return None

    def placeable_authored(self, map_index: int | None = None) -> tuple[str, ...]:
        """Authored chunk identities this session can place, in identity order.

        The project's declared chunks plus any chunk composed here but not yet
        written, filtered - when a map is named - to the chunks composed against
        that map, because a chunk plane holds tile ordinals that only resolve
        through the character block of the map it was made for.
        """
        documents: dict[str, AuthoredChunk] = dict(self._project_chunks)
        documents.update(self._pending_chunk_documents())
        identities: list[str] = []
        for identity in sorted(documents):
            template = self._chunk_template_of(documents[identity])
            if template is None:
                continue
            if map_index is not None and template.map_index != map_index:
                continue
            identities.append(identity)
        return tuple(identities)

    def _authored_template_text(self, identity: str) -> str:
        chunk = self._project_chunks.get(identity) or self._staged_chunks.get(identity)
        return "template unknown" if chunk is None else f"from {chunk.template}"

    def _resolved_plane(self, identity: str) -> tuple[int, ...] | None:
        """The authored body's 1,024 screen entries, resolved once and cached.

        Resolving re-reads the template and re-validates every authored cell, so
        the result is cached per identity for the session and invalidated when the
        document behind it changes - which is what keeps a repaint from paying a
        resolution per cell (CQA-07).
        """
        cached = self._resolved_planes.get(identity)
        if cached is not None:
            return cached
        chunk = self._project_chunks.get(identity) or self._staged_chunks.get(identity)
        if chunk is None:
            return None
        author = self.chunk_author()
        if author is None:
            return None
        try:
            entries = author.resolve(chunk).entries
        except _CHUNK_READ_ERRORS as exc:
            if identity not in self._plane_error_reported:
                self._plane_error_reported.add(identity)
                QMessageBox.warning(
                    self, "Authored chunk", f"{self._authored_name(identity)}: {exc}"
                )
            return None
        self._resolved_planes[identity] = entries
        return entries

    def _pending_chunk_documents(self) -> dict[str, AuthoredChunk]:
        """Chunk documents composed here and not yet written to the project.

        Maintained by :meth:`_sync_staged_chunk` on every plane change, so this is
        a read of the current state and never a re-composition (the unsaved count
        and the palette ask it on paths that must stay cheap).
        """
        return dict(self._staged_chunks)

    def _compose_staged_chunk(self) -> AuthoredChunk | None:
        """The open editor's plane as the authored chunk a project would store.

        The SDK's own `ChunkAuthor.create` fills in every cell's prior value from
        the template, so there is no way for this surface to state a prior the
        template does not hold. None means "not yet different from the template",
        which is not an error: a chunk with no authored cell would be a
        byte-identical copy, and the SDK refuses to persist one.
        """
        identity = self._chunk_identity
        template = self._chunk_template
        if identity is None or template is None or not self._chunk_plane:
            return None
        changed = {
            divmod(cell, _CHUNK_SIDE): entry
            for cell, entry in enumerate(self._chunk_plane)
            if entry != self._chunk_template_plane[cell]
        }
        if not changed:
            return None
        author = self.chunk_author()
        if author is None:
            return None
        try:
            return author.create(identity, template, changed)
        except _CHUNK_READ_ERRORS as exc:
            if identity not in self._plane_error_reported:
                self._plane_error_reported.add(identity)
                QMessageBox.warning(self, "Chunk editor", str(exc))
            return None

    def _authored_value_at(
        self, map_index: int, layer_slot: int, cell: int
    ) -> str | None:
        """The authored identity a map cell holds right now: staged, else committed."""
        key = (map_index, layer_slot, cell)
        staged = self._authored_cells.get(key)
        if staged is not None:
            return staged
        return self._authored_committed.get(key)

    # -- the chunk editor: opening and closing --------------------------------
    def create_chunk(self, _checked: bool = False) -> None:
        """The Create Chunk action: name a new chunk built from the selected template.

        The template is the chunk the layer's palette has selected - the same
        "Chunk N" the project stores - because there is no chunk catalog to pick
        from: a chunk is named by the layer that uses it.
        """
        if not self._edit_mode or self._slot is None or self._current is None:
            self._publish_status(
                "Turn Edit Layout on and pick a paintable layer before creating a "
                "chunk."
            )
            return
        if self._brush_authored is not None:
            self._publish_status(
                "Pick one of this layer's own chunks in the palette first: a new "
                "chunk is created from an existing one."
            )
            return
        ordinal = self._brush_ordinal
        if ordinal is None and self._selected_cell is not None:
            ordinal = self._slot.ordinal_of(
                self._working_pointer(self._slot.slot, self._selected_cell)
            )
        if not ordinal:
            self._publish_status(
                "Pick one of this layer's own chunks in the palette first: a new "
                "chunk is created from an existing one."
            )
            return
        author = self.chunk_author()
        if author is None:
            QMessageBox.warning(
                self,
                "Create chunk",
                self._chunk_author_error or "chunk authoring is unavailable for this image",
            )
            return
        name, accepted = QInputDialog.getText(
            self,
            "Create chunk",
            "New chunk name (a-z, 0-9, '_' and '-'; a leading 'chunk:' is optional):",
        )
        if not accepted:
            return
        try:
            identity = chunk_identity(name)
        except ChunkAuthoringError as exc:
            QMessageBox.warning(self, "Create chunk", str(exc))
            return
        if identity in self._project_chunks or identity in self._staged_chunks:
            QMessageBox.warning(
                self,
                "Create chunk",
                f"{identity} already exists in this project. Select it in the chunk "
                "palette and use Edit chunk\u2026 to revise it.",
            )
            return
        try:
            template = ChunkTemplate(self._current.index, self._slot.slot, ordinal)
            # The vocabulary is read before the editor opens, so a layer whose
            # permitted entries cannot be read refuses here - with the reason -
            # rather than opening an editor whose palette is empty.
            author.vocabulary(template.map_index, template.layer_slot)
            plane = author.plane(template)
        except _CHUNK_READ_ERRORS as exc:
            QMessageBox.warning(self, "Create chunk", str(exc))
            return
        self.open_chunk_editor(identity, template, plane, plane)
        self._publish_status(
            f"Created {self._authored_name(identity)} from Chunk {ordinal}. Paint its "
            "screen entries, then Apply chunk."
        )

    def open_chunk_editor(
        self,
        identity: str,
        template: ChunkTemplate,
        template_plane,
        applied_plane,
        *,
        staged_plane=None,
    ) -> None:
        """Open the chunk editor on a chunk's plane.

        ``template_plane`` is what an authored cell is a delta against;
        ``applied_plane`` is the state Apply/Revert return to; ``staged_plane``
        (defaulting to ``applied_plane``) is the in-progress state, which is how a
        chunk whose editor was closed comes back with the work it still holds.
        """
        self._chunk_identity = identity
        self._chunk_template = template
        self._chunk_template_plane = tuple(template_plane)
        self._chunk_applied_plane = tuple(applied_plane)
        self._chunk_plane = list(
            self._chunk_applied_plane if staged_plane is None else staged_plane
        )
        self._chunk_brush = self._chunk_plane[0] if self._chunk_plane else None
        self._chunk_selected = 0
        self._chunk_hover = ""
        self._chunk_stroke = []
        self._chunk_stroke_previous = {}
        self._chunk_stroke_applied = {}
        self._chunk_stroke_first = None
        self._chunk_stroke_last = None
        self._chunk_stroke_active = False
        self._chunk_tool = _TOOL_PAINT
        self._chunk_char_data = (
            self._editor.character_block(template.map_index)
            if self._editor is not None
            else None
        )
        self._chunk_editor_open = True
        self._centre_stack.setCurrentWidget(self._chunk_page)
        self._chunk_page.setVisible(True)
        self._populate_chunk_palette()
        self._install_chunk_overlay()
        self._sync_staged_chunk()
        self._refresh_chunk_editor_state()
        self._chunk_canvas.setFocus()

    def open_authored_chunk(self, identity: str) -> bool:
        """Reopen the chunk editor on a chunk this project or session holds.

        The revision path the ticket requires: a chunk already created is
        observable and revisable. The three planes are resolved explicitly:

        * ``template_plane`` - the canonical body the chunk was composed from, so
          every authored cell is a delta against it;
        * ``applied_plane`` - the project's own resolved body when the chunk has
          been written, and the template when it has not, so "dirty" keeps meaning
          "differs from what the project holds";
        * ``staged_plane`` - the staged document's body when there is unpublished
          work, so reopening brings that work back rather than dropping it.
        """
        project_doc = self._project_chunks.get(identity)
        staged_doc = self._staged_chunks.get(identity)
        document = project_doc or staged_doc
        if document is None:
            self._publish_status(f"{identity!r} is not a chunk this project declares.")
            return False
        template = self._chunk_template_of(document)
        if template is None:
            QMessageBox.warning(
                self,
                "Chunk editor",
                f"{identity} names template {document.template!r}, which is not a "
                "valid template.",
            )
            return False
        author = self.chunk_author()
        if author is None:
            QMessageBox.warning(
                self,
                "Chunk editor",
                self._chunk_author_error or "chunk authoring is unavailable for this image",
            )
            return False
        try:
            template_plane = author.plane(template)
            applied_plane = (
                author.resolve(project_doc).entries
                if project_doc is not None
                else template_plane
            )
            staged_plane = (
                author.resolve(staged_doc).entries if staged_doc is not None else None
            )
        except _CHUNK_READ_ERRORS as exc:
            QMessageBox.warning(self, "Chunk editor", str(exc))
            return False
        self.open_chunk_editor(
            identity,
            template,
            template_plane,
            applied_plane,
            staged_plane=applied_plane if staged_plane is None else staged_plane,
        )
        return True

    def edit_selected_authored_chunk(self) -> bool:
        """The inspector's Edit chunk action: reopen the brush when it is authored."""
        identity = self._brush_authored
        if identity is None:
            self._publish_status(
                "Select an authored chunk in the palette first; a retail chunk has no "
                "editable body in this project."
            )
            return False
        return self.open_authored_chunk(identity)

    def close_chunk_editor(self) -> None:
        """Leave the chunk editor page, keeping the staged chunk.

        Staged chunk work is NOT discarded here: it stays in the project-pending
        set, so it still counts as unsaved work, still appears in the map's
        palette and is still written by "Apply to project".
        """
        identity = self._chunk_identity
        staged = identity is not None and identity in self._pending_chunk_documents()
        self._close_chunk_editor_page()
        if identity is not None:
            self._publish_status(
                f"{self._authored_name(identity)} is closed"
                + (
                    f"; its {self._authored_edit_count()} staged cell(s) are still "
                    "unsaved and Apply to project will write them."
                    if staged
                    else "."
                )
            )
        self._refresh_editor_state()

    def _close_chunk_editor_page(self) -> None:
        self._chunk_editor_open = False
        self._clear_chunk_overlay()
        page = getattr(self, "_chunk_page", None)
        stack = getattr(self, "_centre_stack", None)
        if page is not None and stack is not None:
            page.setVisible(False)
            stack.setCurrentWidget(self._centre_split)

    def _authored_edit_count(self) -> int:
        if not self._chunk_plane:
            return 0
        return sum(
            1
            for cell, entry in enumerate(self._chunk_plane)
            if entry != self._chunk_template_plane[cell]
        )

    # -- the chunk editor: the plane, its palette and its gestures ------------

    def chunk_plane_entries(self) -> tuple[int, ...]:
        """The staged 32x32 plane, row-major, for a caller or a test."""
        return tuple(self._chunk_plane)

    def chunk_is_open(self) -> bool:
        return self._chunk_editor_open

    def chunk_is_dirty(self) -> bool:
        """Whether the staged plane differs from the last applied/template state."""
        return bool(self._chunk_plane) and tuple(self._chunk_plane) != self._chunk_applied_plane

    def set_chunk_tool(self, tool: str) -> None:
        """Select the chunk editor's paint or eyedropper tool."""
        self._chunk_tool = tool
        self._chunk_paint_tool.setChecked(tool == _TOOL_PAINT)
        self._chunk_pick_tool.setChecked(tool == _TOOL_PICK)
        self._refresh_chunk_editor_state()

    def set_chunk_brush(self, entry: int | None) -> None:
        """Choose the screen entry the chunk-plane paint gesture will place."""
        self._chunk_brush = entry
        self._refresh_chunk_editor_state()

    def _populate_chunk_palette(self) -> None:
        """One swatch per screen entry this layer's own chunks already display.

        The permitted authoring vocabulary, straight from the SDK: an authored
        chunk may only rearrange graphics the map already uses, so this palette is
        the whole set of values a cell may hold and there is no free-entry field.
        """
        self._suppress_chunk_palette = True
        self._chunk_palette.clear()
        try:
            template = self._chunk_template
            author = self.chunk_author()
            if template is None or author is None:
                self._chunk_palette_hint.setText("No chunk is open.")
                return
            try:
                vocabulary = author.vocabulary(template.map_index, template.layer_slot)
            except _CHUNK_READ_ERRORS as exc:
                self._chunk_palette_hint.setText(f"This layer's entries could not be read: {exc}")
                QMessageBox.warning(self, "Chunk editor", str(exc))
                return
            if self._chunk_char_data is None:
                self._chunk_palette_hint.setText(
                    "This chunk's graphics are unavailable, so its entries cannot be "
                    "shown."
                )
                return
            self._chunk_palette_hint.setText(
                f"{len(vocabulary)} screen entr"
                f"{'y' if len(vocabulary) == 1 else 'ies'} this layer already draws. "
                "An authored chunk may only rearrange these."
            )
            # Rendering every swatch is the one real cost of opening the editor
            # (measured ~13 ms per entry through the SDK's own renderer), so the
            # palette is filled inside a wait cursor and each swatch is cached per
            # (map, layer, entry).
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                for entry in vocabulary:
                    pixmap = self._entry_swatch(template, entry)
                    label = author.entry_label(entry)
                    item = QListWidgetItem(QIcon(pixmap), label)
                    item.setData(_ENTRY_ROLE, entry)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
                    # Two columns, each wide enough for the SDK's whole label
                    # ("tile 30 · flip H") to wrap onto two lines rather than be
                    # elided: a label clipped to "tile 3…" would hide the flip that
                    # distinguishes two entries sharing a tile ordinal.
                    item.setSizeHint(QSize(94, 52))
                    item.setToolTip(f"{label}\nscreen entry {entry:#06x}")
                    self._chunk_palette.addItem(item)
            finally:
                QApplication.restoreOverrideCursor()
            self._select_chunk_palette_row()
        finally:
            self._suppress_chunk_palette = False

    def _entry_swatch(self, template: ChunkTemplate, entry: int) -> QPixmap:
        """A 20x20 swatch of one screen entry, rendered through the SDK.

        The entry is drawn as a plane of itself and downscaled by
        :func:`tools.webfoot.map_view.render_chunk_entries`, so the swatch is the
        graphics the map really shows for that value - including a tile's flip
        bits - rather than a second, invented preview path.
        """
        key = (template.map_index, template.layer_slot, entry)
        cached = self._chunk_thumbnails.get(key)
        if cached is not None:
            return cached
        plane = (entry,) * mv.CHUNK_ENTRY_COUNT
        image = mv.render_chunk_entries(
            self._chunk_char_data, plane, width=_SWATCH_PIXELS, height=_SWATCH_PIXELS
        )
        pixmap = self._pixmap_from_indices(
            image.pixels, image.width, image.height, self._current.palette
        )
        backed = QPixmap(_SWATCH_PIXELS, _SWATCH_PIXELS)
        backed.fill(theme.color("checker_dark"))
        painter = QPainter(backed)
        painter.fillRect(backed.rect(), _checkerboard())
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        self._chunk_thumbnails[key] = backed
        return backed

    def _on_entry_selected(self, current: QListWidgetItem | None, _previous=None) -> None:
        """A swatch pick becomes the entry the next plane click paints."""
        if self._suppress_chunk_palette or current is None:
            return
        entry = current.data(_ENTRY_ROLE)
        if entry is None or entry == self._chunk_brush:
            return
        self.set_chunk_brush(entry)
        self._publish_status(
            f"{self._entry_label(entry)} is the entry to paint; click or drag plane "
            "cells."
        )

    def _entry_label(self, entry: int) -> str:
        author = self.chunk_author()
        if author is None:
            return f"screen entry {entry:#06x}"
        try:
            return author.entry_label(entry)
        except _CHUNK_READ_ERRORS:
            return f"screen entry {entry:#06x}"

    def _select_chunk_palette_row(self) -> None:
        """Point the palette's own selection at the brush entry."""
        was = self._suppress_chunk_palette
        self._suppress_chunk_palette = True
        try:
            row = None
            for index in range(self._chunk_palette.count()):
                if self._chunk_palette.item(index).data(_ENTRY_ROLE) == self._chunk_brush:
                    row = index
                    break
            self._chunk_palette.setCurrentRow(-1 if row is None else row)
        finally:
            self._suppress_chunk_palette = was

    def _install_chunk_overlay(self) -> None:
        """Install the plane grid overlay and draw the chunk's pixels under it.

        The overlay is installed even when the artwork cannot be drawn: the grid,
        the hover readout and the gestures are still the surface's structure, and a
        missing character block is reported by the render path rather than by a
        silently dead page.
        """
        self._clear_chunk_overlay()
        if not self._chunk_editor_open or not self._chunk_plane:
            return
        self._render_chunk_plane()
        self._chunk_scene.setSceneRect(QRectF(0, 0, mv.CHUNK_PIXELS, mv.CHUNK_PIXELS))
        self._chunk_overlay = ChunkPlaneOverlay(
            _CHUNK_SIDE,
            self._on_chunk_cell_clicked,
            on_stroke_begin=self._begin_chunk_stroke,
            on_stroke_end=self._end_chunk_stroke,
            on_cell_hover=self._on_chunk_cell_hover,
        )
        self._chunk_scene.addItem(self._chunk_overlay)
        self._chunk_overlay.set_selected(self._chunk_selected)
        self._chunk_overlay.set_edited(self._edited_chunk_cells())
        self._chunk_canvas.fit_map()

    def _clear_chunk_overlay(self) -> None:
        if self._chunk_overlay is not None and self._chunk_overlay.scene() is self._chunk_scene:
            self._chunk_scene.removeItem(self._chunk_overlay)
        self._chunk_overlay = None
        if (
            self._chunk_pixmap_item is not None
            and self._chunk_pixmap_item.scene() is self._chunk_scene
        ):
            self._chunk_scene.removeItem(self._chunk_pixmap_item)
        self._chunk_pixmap_item = None

    def _edited_chunk_cells(self) -> frozenset[int]:
        """The cells whose entry differs from the last applied state."""
        if not self._chunk_plane or not self._chunk_applied_plane:
            return frozenset()
        return frozenset(
            cell
            for cell, entry in enumerate(self._chunk_plane)
            if entry != self._chunk_applied_plane[cell]
        )

    def _render_chunk_plane(self) -> bool:
        """Draw the staged plane as a 256x256 image through the map's char block."""
        if not self._chunk_plane or self._chunk_char_data is None:
            return False
        if self._current is None:
            return False
        try:
            image = mv.render_chunk_entries(self._chunk_char_data, tuple(self._chunk_plane))
        except _CHUNK_READ_ERRORS as exc:
            QMessageBox.warning(self, "Chunk editor", str(exc))
            return False
        pixmap = self._pixmap_from_indices(
            image.pixels, image.width, image.height, self._current.palette
        )
        if (
            self._chunk_pixmap_item is not None
            and self._chunk_pixmap_item.scene() is self._chunk_scene
        ):
            self._chunk_scene.removeItem(self._chunk_pixmap_item)
        self._chunk_pixmap_item = self._chunk_scene.addPixmap(pixmap)
        self._chunk_pixmap_item.setTransformationMode(
            Qt.TransformationMode.FastTransformation
        )
        self._chunk_pixmap_item.setZValue(0)
        self._chunk_scene.setSceneRect(QRectF(0, 0, mv.CHUNK_PIXELS, mv.CHUNK_PIXELS))
        return True

    def _on_chunk_cell_clicked(self, cell: int, alt: bool = False) -> None:
        """One plane cell was pressed or entered during a gesture.

        The tool decides what that means, exactly as it does on the map: the
        eyedropper takes the cell's entry as the brush and changes nothing, the
        paint tool stages the brush into the cell. Alt is the eyedropper's second
        spelling, and the overlay brackets the gesture so a drag is ONE history
        entry.
        """
        if not self._chunk_editor_open or self._chunk_overlay is None:
            return
        if not self._chunk_overlay.contains(cell):
            return
        own_gesture = not self._chunk_stroke_active
        if own_gesture:
            self._begin_chunk_stroke()
        self._chunk_selected = cell
        self._chunk_overlay.set_selected(cell)
        if self._chunk_tool == _TOOL_PICK or alt:
            self._pick_chunk_entry(cell)
            self._refresh_chunk_editor_state()
            if own_gesture:
                self._end_chunk_stroke()
            return
        self._paint_chunk_cell(cell)
        if own_gesture:
            self._end_chunk_stroke()
        self._refresh_chunk_editor_state()

    def _on_chunk_cell_hover(self, cell: int | None) -> None:
        """Report the cell under the pointer on the chunk editor's own readout."""
        if cell is None or not self._chunk_plane:
            self._chunk_hover = ""
            self._update_chunk_hover_label()
            return
        column = cell % _CHUNK_SIDE
        row = cell // _CHUNK_SIDE
        self._chunk_hover = (
            f"row {row}, column {column} \u00b7 cell {cell + 1} of "
            f"{_CHUNK_SIDE * _CHUNK_SIDE} \u00b7 {self._entry_label(self._chunk_plane[cell])}"
        )
        self._update_chunk_hover_label()

    def _on_chunk_canvas_hover(self, x: int | None, y: int | None) -> None:
        """The plane's pixel readout, derived from the cell the pointer is in."""
        if x is None or y is None or self._chunk_overlay is None:
            if self._chunk_hover:
                self._chunk_hover = ""
                self._update_chunk_hover_label()
            return
        self._on_chunk_cell_hover(self._chunk_overlay.cell_at(x, y))

    def _update_chunk_hover_label(self) -> None:
        self._chunk_hover_label.setText(self._chunk_hover or "")

    def _paint_chunk_cell(self, cell: int) -> bool:
        """Stage the brush entry into one plane cell; True when it changed.

        The same two rules the map painter obeys: a cell already holding the brush
        entry is not a change (no history, no dirty state), and the cell's
        pre-gesture entry is captured once per gesture, so a drag that re-crosses a
        cell still undoes to what it held before the whole stroke.
        """
        if not self._chunk_plane or not self._chunk_editor_open:
            return False
        entry = self._chunk_brush
        if entry is None:
            self._publish_status("Choose a screen entry in the palette first.")
            return False
        before = self._chunk_plane[cell]
        if cell not in self._chunk_stroke_previous:
            self._chunk_stroke_previous[cell] = before
        if self._chunk_stroke_first is None:
            self._chunk_stroke_first = cell
        self._chunk_stroke_last = cell
        if before == entry:
            return False
        self._chunk_plane[cell] = entry
        if cell not in self._chunk_stroke:
            self._chunk_stroke.append(cell)
            self._chunk_stroke_applied[cell] = entry
        self._after_chunk_edit()
        return True

    def _pick_chunk_entry(self, cell: int) -> None:
        """Take one plane cell's entry as the brush, without editing it."""
        if not self._chunk_plane:
            return
        entry = self._chunk_plane[cell]
        self.set_chunk_brush(entry)
        self._publish_status(
            f"Picked {self._entry_label(entry)} as the entry to paint."
        )

    def paint_chunk_cell(self, cell: int) -> bool:
        """Paint one plane cell as part of the current gesture; True when it changed."""
        changed = self._paint_chunk_cell(cell)
        if changed and self._chunk_overlay is not None:
            self._chunk_selected = cell
            self._chunk_overlay.set_selected(cell)
        return changed

    def pick_entry_from_chunk_cell(self, cell: int) -> None:
        """Eyedropper over the plane, as one call: take a cell's entry as the brush."""
        if not self._chunk_plane or not self._chunk_editor_open:
            return
        if not 0 <= cell < len(self._chunk_plane):
            return
        self._chunk_selected = cell
        if self._chunk_overlay is not None:
            self._chunk_overlay.set_selected(cell)
        self._pick_chunk_entry(cell)
        self._refresh_chunk_editor_state()

    def _begin_chunk_stroke(self) -> None:
        """Open a plane gesture record; called by the overlay on press."""
        self._chunk_stroke = []
        self._chunk_stroke_previous = {}
        self._chunk_stroke_applied = {}
        self._chunk_stroke_first = None
        self._chunk_stroke_last = None
        self._chunk_stroke_active = True

    def begin_chunk_stroke(self) -> None:
        """Open a plane gesture explicitly, for a caller driving the surface."""
        self._begin_chunk_stroke()

    def _end_chunk_stroke(self) -> None:
        """Close the plane gesture and raise it on the SAME undo stack.

        The changed-cell rule is the map painter's: only cells whose entry actually
        changed enter the command, and an empty gesture pushes nothing at all.
        """
        self._chunk_stroke_active = False
        changed = [
            cell
            for cell in self._chunk_stroke
            if self._chunk_stroke_previous.get(cell)
            != self._chunk_stroke_applied.get(cell)
        ]
        first, last = self._chunk_stroke_first, self._chunk_stroke_last
        previous = {cell: self._chunk_stroke_previous[cell] for cell in changed}
        applied = {cell: self._chunk_stroke_applied[cell] for cell in changed}
        self._chunk_stroke = []
        self._chunk_stroke_previous = {}
        self._chunk_stroke_applied = {}
        self._chunk_stroke_first = None
        self._chunk_stroke_last = None
        identity = self._chunk_identity
        if not changed or identity is None:
            self._sync_staged_chunk()
            self._refresh_chunk_editor_state()
            self._refresh_editor_state()
            return
        command = ChunkCellCommand(
            self, identity=identity, cells=changed, previous=previous, applied=applied
        )
        command.set_keys(self._chunk_brush, first, last)
        self._undo_stack.push(command)
        self._sync_staged_chunk()
        self._refresh_chunk_editor_state()
        # The map inspector's own "Changes" row and its Apply to project button
        # count the staged chunk too, so they are re-synced at the gesture's end
        # (once per drag, not once per cell).
        self._refresh_editor_state()

    def end_chunk_stroke(self) -> None:
        """Close the current plane gesture and raise it on the history."""
        self._end_chunk_stroke()

    def _reapply_chunk_cells(self, command: "ChunkCellCommand") -> None:
        """Re-apply one already-recorded plane gesture (redo or a merged stroke)."""
        if not self._focus_chunk_for(command):
            return
        for cell, entry in command.applied.items():
            self._chunk_plane[cell] = entry
        self._after_chunk_edit()

    def _reverse_chunk_cells(self, command: "ChunkCellCommand") -> None:
        """Undo one plane gesture: every cell back to the entry it held before."""
        if not self._focus_chunk_for(command):
            return
        for cell, entry in command.previous.items():
            self._chunk_plane[cell] = entry
        self._after_chunk_edit()

    def _focus_chunk_for(self, command: "ChunkCellCommand") -> bool:
        """Make the command's chunk the open one, reopening the page when needed.

        A history entry outlives the editor page, so an undo after "Back to map"
        has to show the chunk it reverses - silently changing a plane nobody can
        see would be a change the author has no way to verify.
        """
        if self._chunk_identity != command.identity:
            if not self.open_authored_chunk(command.identity):
                return False
            return self._chunk_identity == command.identity
        if not self._chunk_plane:
            return False
        if not self._chunk_editor_open:
            self._reopen_chunk_page()
        return True

    def _reopen_chunk_page(self) -> None:
        """Show the chunk editor page again for the chunk that is already loaded."""
        self._chunk_editor_open = True
        self._centre_stack.setCurrentWidget(self._chunk_page)
        self._chunk_page.setVisible(True)
        self._populate_chunk_palette()
        self._install_chunk_overlay()
        self._refresh_chunk_editor_state()
        self._chunk_canvas.setFocus()

    def _after_chunk_edit(self) -> None:
        """Repaint the plane, its markers and the dirty state after a change.

        The project-pending document is recomposed at a GESTURE BOUNDARY, not per
        cell: composing re-reads the template and re-validates every authored cell
        (measured 4.35 ms on the canonical image), which is wasted work for a cell
        in the middle of a drag when the gesture's own end will compose the whole
        set once. A caller that paints outside a gesture (`paint_chunk_cell` on its
        own) is not in a stroke, so it composes immediately and behaves as before.
        """
        self._render_chunk_plane()
        if self._chunk_overlay is not None:
            self._chunk_overlay.set_edited(self._edited_chunk_cells())
        if not self._chunk_stroke_active:
            self._sync_staged_chunk()
        else:
            self._announce_dirty()
        self._refresh_chunk_editor_state()

    def _sync_staged_chunk(self) -> None:
        """Re-derive the open chunk's project-pending document and dirty state.

        One place decides whether the open chunk is "composed but not written", so
        the unsaved count, the map palette and the apply batch cannot disagree. A
        chunk the project already holds exactly is NOT pending, which is what makes
        an applied chunk stop counting as unsaved work. The identity's cached
        resolved plane is dropped because the document behind it just changed.
        """
        identity = self._chunk_identity
        if identity is None:
            return
        self._resolved_planes.pop(identity, None)
        document = self._compose_staged_chunk()
        if document is None or self._project_chunks.get(identity) == document:
            self._staged_chunks.pop(identity, None)
        else:
            self._staged_chunks[identity] = document
        self._announce_dirty()

    def _refresh_chunk_editor_state(self) -> None:
        """Re-sync the chunk editor's page with the chunk it is showing."""
        if self._chunk_identity is None:
            self._chunk_title.setText("\u2014")
            self._chunk_state_label.setText("No chunk is open.")
            self._chunk_entry_readout.setText("\u2014")
            self._chunk_apply_button.setEnabled(False)
            self._chunk_revert_button.setEnabled(False)
            self._chunk_brush_button.setEnabled(False)
            self._chunk_palette.setEnabled(False)
            self._chunk_paint_tool.setEnabled(False)
            self._chunk_pick_tool.setEnabled(False)
            return
        template = self._chunk_template
        self._chunk_title.setText(
            f"{self._authored_name(self._chunk_identity)}"
            + (f" \u00b7 {template.text}" if template is not None else "")
        )
        edited = self._edited_chunk_cells()
        edited_total = self._authored_edit_count()
        applied = self._chunk_identity in self._project_chunks
        if edited:
            self._chunk_state_label.setText(
                f"{theme.status_glyph('pending')} {len(edited)} cell(s) differ from the "
                f"applied chunk \u00b7 {edited_total} authored cell(s) vs the template"
                + ("" if applied else " \u00b7 not written to the project yet")
            )
        elif edited_total:
            self._chunk_state_label.setText(
                f"{theme.status_glyph('saved')} applied \u00b7 {edited_total} authored "
                "cell(s) vs the template"
            )
        else:
            self._chunk_state_label.setText(
                "Unchanged from its template. Paint at least one screen entry, because "
                "a chunk identical to its template is a copy rather than a new chunk."
            )
        can_apply = self._session.project_dir is not None
        self._chunk_apply_button.setEnabled(can_apply and bool(edited))
        self._chunk_apply_button.setToolTip(
            "Write this chunk into the project's maps/chunks.toml"
            if can_apply
            else "Open or extract a project first: an authored chunk is stored in the "
            "project, not in a ROM."
        )
        self._chunk_revert_button.setEnabled(bool(edited))
        self._chunk_brush_button.setEnabled(
            self._chunk_identity in self.placeable_authored(None)
        )
        self._chunk_palette.setEnabled(bool(self._chunk_palette.count()))
        self._chunk_paint_tool.setEnabled(True)
        self._chunk_pick_tool.setEnabled(True)
        self._chunk_paint_tool.setChecked(self._chunk_tool == _TOOL_PAINT)
        self._chunk_pick_tool.setChecked(self._chunk_tool == _TOOL_PICK)
        self._chunk_entry_readout.setText(
            f"Painting {self._entry_label(self._chunk_brush)}"
            if self._chunk_brush is not None
            else "No entry selected"
        )
        self._select_chunk_palette_row()
        self._update_chunk_hover_label()

    def _on_chunk_canvas_key(self, event) -> bool:
        """Chunk-editor keys on the plane canvas; True when the key was used."""
        if not self._chunk_editor_open:
            return False
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.close_chunk_editor()
            return True
        deltas = {
            Qt.Key.Key_Left: (-1, 0),
            Qt.Key.Key_Right: (1, 0),
            Qt.Key.Key_Up: (0, -1),
            Qt.Key.Key_Down: (0, 1),
        }
        if key in deltas:
            self._move_chunk_selection(*deltas[key])
            return True
        return False

    def _move_chunk_selection(self, delta_column: int, delta_row: int) -> None:
        """Move the plane selection without painting, the way the map canvas does."""
        if not self._chunk_plane:
            return
        if self._chunk_selected is None:
            self._chunk_selected = 0
            if self._chunk_overlay is not None:
                self._chunk_overlay.set_selected(0)
            return
        column = self._chunk_selected % _CHUNK_SIDE + delta_column
        row = self._chunk_selected // _CHUNK_SIDE + delta_row
        if not 0 <= column < _CHUNK_SIDE or not 0 <= row < _CHUNK_SIDE:
            return
        self._chunk_selected = row * _CHUNK_SIDE + column
        if self._chunk_overlay is not None:
            self._chunk_overlay.set_selected(self._chunk_selected)
        self._on_chunk_cell_hover(self._chunk_selected)

    # -- the chunk editor: apply, revert, and hand the chunk to the map -------

    def apply_chunk(self) -> bool:
        """Persist the open chunk into the project through the SDK authority.

        ONE write, one project document: `set_authored_chunk` validates the chunk
        against the canonical image - template, priors and every authored entry -
        before anything is written, so a chunk that cannot be built cannot be saved
        either. Applying does not clear the history: the chunk's own edits are still
        reversible through it, and the applied state becomes the new revert floor.
        """
        identity = self._chunk_identity
        if not self._chunk_editor_open or identity is None:
            return False
        if self._session.project_dir is None:
            message = (
                "Open or extract a project first: an authored chunk is stored in the "
                "project, not in a ROM."
            )
            self._publish_status(message)
            QMessageBox.warning(self, "Chunk editor", message)
            return False
        document = self._pending_chunk_documents().get(identity)
        if document is None:
            QMessageBox.warning(
                self,
                "Chunk editor",
                "This chunk does not differ from its template yet. Paint at least one "
                "screen entry first: a chunk identical to its template is a copy "
                "rather than a new chunk.",
            )
            return False
        try:
            changed = set_authored_chunk(
                self._session.project_dir,
                self._session.map_image,
                document,
                profile=self._session.profile,
            )
        except _EDIT_AND_PROJECT_ERRORS as exc:
            QMessageBox.warning(self, "Chunk editor", str(exc))
            return False
        self._staged_chunks.pop(identity, None)
        self._resolved_planes.pop(identity, None)
        self._chunk_applied_plane = tuple(self._chunk_plane)
        self._plane_error_reported.discard(identity)
        self._reload_project_authored()
        self._after_chunk_edit()
        self._refresh_editor_state()
        if changed:
            self._publish_status(
                f"Wrote {self._authored_name(identity)} into the project "
                f"({self._authored_edit_count()} authored cell(s)). Select it in the "
                "palette and place it on map cells."
            )
            # WORKBENCH-MUTATION-CURRENCY-001: the chunk editor is the tab's
            # second project write, so it owes the same currency contract as
            # `apply_to_project` - one revision, validation and build stale.
            # `changed` is False for a chunk the project already holds exactly,
            # and that no-op must leave validation and build alone.
            self._session.project_mutated()
            self.projectChanged.emit()
        else:
            self._publish_status(
                f"The project already held {self._authored_name(identity)} exactly."
            )
        return changed

    def revert_chunk_edits(self) -> bool:
        """Discard the staged plane back to the last applied/template state.

        Reverting is a gesture like any other: it is staged and then recorded as
        ONE history entry whose redo re-applies the edits it removed, so a revert
        is itself undoable rather than a silent loss.
        """
        if not self._chunk_editor_open or not self._chunk_plane:
            return False
        changed = {
            cell: self._chunk_plane[cell]
            for cell in range(len(self._chunk_plane))
            if self._chunk_plane[cell] != self._chunk_applied_plane[cell]
        }
        if not changed:
            self._publish_status("This chunk already matches its applied state.")
            return False
        applied = {
            cell: self._chunk_applied_plane[cell] for cell in changed
        }
        for cell in changed:
            self._chunk_plane[cell] = self._chunk_applied_plane[cell]
        self._naming_chunk_revert = True
        try:
            command = ChunkCellCommand(
                self,
                identity=self._chunk_identity,
                cells=sorted(changed),
                previous=changed,
                applied=applied,
            )
        finally:
            self._naming_chunk_revert = False
        # No brush key: a revert must never merge into a paint gesture.
        command.set_keys(None, min(changed), max(changed))
        self._undo_stack.push(command)
        self._after_chunk_edit()
        self._refresh_editor_state()
        self._publish_status(
            f"Reverted {len(changed)} cell(s) of "
            f"{self._authored_name(self._chunk_identity)} to the applied chunk."
        )
        return True

    def use_chunk_as_brush(self) -> bool:
        """Leave the editor with this chunk selected as the map's paint value."""
        identity = self._chunk_identity
        if identity is None:
            return False
        if identity not in self.placeable_authored(None):
            self._publish_status(
                f"{self._authored_name(identity)} is not placeable yet; paint at "
                "least one screen entry so it differs from its template."
            )
            return False
        self.close_chunk_editor()
        if not self._set_authored_brush(identity, publish=False):
            return False
        self._publish_status(
            f"{self._authored_name(identity)} is the paint value; click or drag map "
            "cells to place it, then Apply to project."
        )
        self._refresh_editor_state()
        return True

    # -- layout editing: save as ---------------------------------------------

    def _default_output_path(self) -> Path | None:
        """``<source name> - Edited.gba`` beside the source ROM."""
        source = self._session.rom_path
        if source is None:
            return None
        return Path(source).with_name(f"{Path(source).stem} - Edited.gba")

    def _on_save_as(self) -> None:
        """Write the pending edits to a NEW ROM, then verify what was written."""
        if self._editor is None or self._session.rom_path is None:
            return
        if self._session.profile is None:
            QMessageBox.warning(
                self, "Save As", "The open ROM has no identified profile; cannot save."
            )
            return
        default = self._default_output_path()
        chosen, _filter = QFileDialog.getSaveFileName(
            self,
            "Save edited ROM as",
            str(default) if default is not None else "",
            "GBA ROM (*.gba)",
        )
        if not chosen:
            return
        # THE SAFETY INVARIANT: the generated ROM may never be the source ROM.
        if not is_safe_output_path(chosen, self._session.rom_path):
            QMessageBox.critical(
                self, "Save As refused",
                f"The new ROM would overwrite the source ROM:\n{chosen}\n"
                "Choose another file name; the source ROM is never modified.",
            )
            return
        # Save As writes exactly what is STAGED. It deliberately does not paint
        # anything on its own: a paint is a user gesture, and a save that
        # silently edited the cell that happened to be selected would write
        # content the user never saw themselves place.
        try:
            saved = self._editor.save(
                chosen,
                source_path=self._session.rom_path,
                profile_id=self._session.profile.id,
            )
        except (_EDIT_ERRORS + (OSError,)) as exc:
            QMessageBox.critical(self, "Save As", str(exc))
            self._status.setText(f"Save As failed: {exc}")
            return
        self._layout = self._layout.note_saved(self._edits())
        self._refresh_editor_state()
        detail = (
            "no layout changes were pending, so the copy is byte-identical to the "
            "source ROM"
            if saved.no_op
            else f"{len(saved.changes)} layout change(s), "
            f"{len(saved.changed_offsets)} byte(s) changed"
        )
        # A ROM copy carries layout edits only. Authored chunks, placements and
        # project structure are materialized by the build, so the confirmation has
        # to name what stayed behind; without it, "no layout changes were pending"
        # reads as "nothing was staged" next to a title that says otherwise.
        staged_in_project = self._unsaved_count()
        if staged_in_project:
            detail += (
                f"; {staged_in_project} staged change(s) stay in the project, because a "
                "ROM copy carries layout edits only - Apply or Build writes them"
            )
        self._status.setText(f"Saved {saved.output_path} · {detail}")
        QMessageBox.information(
            self,
            "Save As",
            f"Wrote a new ROM:\n{saved.output_path}\n\n{detail}.\n"
            f"SHA-256 {saved.output_sha256}\n\n"
            f"Its provenance manifest was written beside it:\n{saved.manifest_path.name}\n"
            "DragonByte Z can reopen this ROM from that manifest.\n\n"
            "The source ROM was not modified.",
        )
