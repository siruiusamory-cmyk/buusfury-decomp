"""The Maps destination's page: a map's chunk cells and its warps.

Two modes over one map selection. `Layout` renders the chunk-window cells of one
layer of the selected map, and the one editable field of a cell is its chunk,
chosen from that layer's own vocabulary. `Warps` renders the transitions the
image carries out of the selected map, and the one editable field of a warp is
the map it leads to.

The page decides nothing: a layer's paintable state and its own read-only reason,
a cell's pointer and its offset, and a warp's destination all arrive from
`mapsurface`, which asks the SDK's own authorities.

The one edit path is the shell's own `apply_edit`, so a map edit is one entry in
the session's one journal, one `Ctrl+Z` returns the project to what it held, and
the ROM surface - which reads the same journal - moves with it. `Open bytes`
hands the cell's or the record's proven extent to the ROM destination's one
selection instead of opening a second one here.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from . import mapsurface as ms, theme
from .inspector import SUPPORT_ROLES, InspectorContext
from .journal import EditKind
from .mapedits import MAPS_TARGET, read as read_maps
from .session import Session
from .tablemodel import RowsModel
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import RomRange

LAYOUT_MODE = "layout"
WARPS_MODE = "warps"

#: Mode id -> the label the switch shows, in the order the switch offers them.
MODES: tuple[tuple[str, str], ...] = (
    (LAYOUT_MODE, "Layout"),
    (WARPS_MODE, "Warps"),
)

_LAYOUT_HEADERS = ("Cell", "Column", "Row", "Chunk", "File offset", "Support")
_WARP_HEADERS = (
    "Transition",
    "Index",
    "Destination",
    "Region",
    "File offset",
    "Support",
)


def _support_cell(editable: bool) -> str:
    """A support state as glyph plus word, the form every surface renders."""
    word = "Editable" if editable else "Read-only"
    return f"{theme.status_glyph(SUPPORT_ROLES[word])} {word}"


class MapPage(QWidget):
    """The Maps destination's centre page."""

    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("mapPage")
        self._session = session
        #: The shell's one edit path, its one ROM-selection route and the one
        #: inspector. None until the shell wires them.
        self._edit_handler = None
        self._open_handler = None
        self._selection_handler = None
        #: The model for the open image, kept for as long as that image is open.
        self._surface: ms.MapSurface | None = None
        self._surface_for = None
        self._maps_for = None
        self._problem = ""
        self._rows: tuple = ()
        self._caret = ""
        self._mode = LAYOUT_MODE
        self._map_index = 0
        self._slot = 0
        self._applying = False

        self._modes = QComboBox()
        self._modes.setObjectName("mapModeSwitch")
        self._modes.addItems([label for _identifier, label in MODES])
        self._modes.setAccessibleName("Maps view")

        self._maps = QComboBox()
        self._maps.setObjectName("mapSwitch")
        self._maps.setAccessibleName("Map")
        self._maps.setMinimumWidth(theme.INSPECTOR_WIDTH)

        self._layers = QComboBox()
        self._layers.setObjectName("mapLayerSwitch")
        self._layers.setAccessibleName("Layer")

        self._model = RowsModel(self)
        self._table = QTableView()
        self._table.setObjectName("mapTable")
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.setWordWrap(False)

        self._summary = QLabel()
        self._summary.setProperty("dbzRole", "hint")
        self._summary.setWordWrap(True)

        self._field = QComboBox()
        self._field.setObjectName("mapFieldSwitch")
        self._field.setAccessibleName("Field")
        self._value = QLineEdit()
        self._value.setObjectName("mapFieldValue")
        self._value.setAccessibleName("Field value")
        self._apply = QPushButton("Apply")
        self._open = QPushButton("Open bytes")
        self._message = QLabel()
        self._message.setProperty("dbzRole", "hint")
        self._message.setWordWrap(True)
        self._editor = QWidget()
        self._editor.setObjectName("mapFieldEditor")

        editor_row = QHBoxLayout(self._editor)
        editor_row.setContentsMargins(0, 0, 0, 0)
        editor_row.setSpacing(theme.SPACE_SM)
        editor_row.addWidget(QLabel("Field:"))
        editor_row.addWidget(self._field)
        editor_row.addWidget(QLabel("Value:"))
        editor_row.addWidget(self._value, 1)
        editor_row.addWidget(self._apply)
        editor_row.addSpacing(theme.SPACE_LG)
        editor_row.addWidget(self._open)

        self._detail = QLabel()
        self._detail.setProperty("dbzRole", "technical")
        self._detail.setWordWrap(True)
        self._detail.setTextInteractionFlags(
            self._detail.textInteractionFlags()
            | Qt.TextInteractionFlag.TextSelectableByMouse
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD
        )
        layout.setSpacing(theme.SPACE_SM)
        top = QHBoxLayout()
        top.setSpacing(theme.SPACE_SM)
        top.addWidget(QLabel("View:"))
        top.addWidget(self._modes)
        top.addWidget(QLabel("Map:"))
        top.addWidget(self._maps, 1)
        top.addWidget(QLabel("Layer:"))
        top.addWidget(self._layers)
        layout.addLayout(top)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._summary)
        layout.addWidget(self._editor)
        layout.addWidget(self._detail)
        layout.addWidget(self._message)

        self._modes.currentTextChanged.connect(self._on_mode_changed)
        self._maps.currentIndexChanged.connect(self._on_map_changed)
        self._layers.currentIndexChanged.connect(self._on_layer_changed)
        self._field.currentTextChanged.connect(self._on_field_changed)
        self._apply.clicked.connect(self._on_apply)
        self._value.returnPressed.connect(self._on_apply)
        self._open.clicked.connect(self._on_open)
        self._table.selectionModel().currentRowChanged.connect(self._on_row_changed)

        self.refresh()

    # -- wiring ---------------------------------------------------------------

    def set_edit_handler(self, handler) -> None:
        """The shell's one edit path: this page never commits an edit itself."""
        self._edit_handler = handler

    def set_open_bytes_handler(self, handler) -> None:
        """The shell's one route into the ROM surface's selection."""
        self._open_handler = handler

    def set_selection_handler(self, handler) -> None:
        """The shell's one inspector, told what this page has selected."""
        self._selection_handler = handler

    # -- the ROM surface's question -------------------------------------------

    def pending_bytes(self) -> dict[int, bytes]:
        """The byte effect of this destination's pending edits, for the ROM page.

        Asked on every ROM render, so it is a read of the journal-backed project
        rather than a cached value that could lag one undo behind.
        """
        surface = self._surface
        if surface is None or self._session.project is None:
            return {}
        try:
            return surface.pending_bytes(self._session.project)
        except Exception:  # a provider boundary: the ROM page still renders
            return {}

    # -- rendering ------------------------------------------------------------

    def refresh(self) -> None:
        """Re-render from the session. The shell calls this after every change."""
        if self._applying:
            # An edit in flight: the shell's re-render would rebuild the field
            # editor from under the handler that is using it. The handler
            # re-renders once it is done instead.
            return
        self._ensure_surface()
        if self._surface is None:
            self._render_unavailable()
            return
        self._render_maps()
        if self._mode == LAYOUT_MODE:
            self._render_layout()
        else:
            self._render_warps()

    def _render_maps(self) -> None:
        """Fill the map switch once per image, keeping the reader's own choice."""
        rows = self._surface.map_rows()
        if self._maps_for == self._session.rom_path and self._maps.count() == len(rows):
            self._select_combo(self._maps, self._map_index)
            return
        self._maps_for = self._session.rom_path
        self._maps.blockSignals(True)
        self._maps.clear()
        for row in rows:
            self._maps.addItem(f"{row.label} ({row.warps} warp(s))", row.index)
        self._maps.blockSignals(False)
        self._select_combo(self._maps, self._map_index)

    def _render_layout(self) -> None:
        self._layers.setVisible(True)
        layers = self._surface.layers(self._map_index)
        self._fill_layers(layers)
        layer = self._current_layer()
        if layer is None or not layer.editable:
            self._rows = ()
            self._model.set_rows(_LAYOUT_HEADERS, ())
            self._summary.setText(self._layer_summary(layers))
            self._message.setText(
                layer.note
                if layer is not None
                else "this map declares no layer this build can show"
            )
            self._detail.clear()
            self._render_editor()
            self._publish_selection(None)
            return
        rows = self._surface.cells(
            self._map_index, layer.slot, self._session.project
        )
        self._rows = rows
        self._model.set_rows(
            _LAYOUT_HEADERS, tuple(self._cell_cells(row) for row in rows)
        )
        self._summary.setText(self._layer_summary(layers))
        self._message.setText(self._records_message(rows))
        self._select_caret()
        self._render_editor()

    def _render_warps(self) -> None:
        self._layers.setVisible(False)
        rows = self._surface.warps(self._session.project, self._map_index)
        self._rows = rows
        self._model.set_rows(
            _WARP_HEADERS, tuple(self._warp_cells(row) for row in rows)
        )
        self._summary.setText(self._warp_summary(rows))
        self._message.setText(self._records_message(rows))
        self._select_caret()
        self._render_editor()

    def _render_unavailable(self) -> None:
        self._layers.setVisible(False)
        self._rows = ()
        self._model.set_rows(_LAYOUT_HEADERS, ())
        self._summary.setText("")
        self._detail.clear()
        self._message.setText(
            self._problem or "Open a ROM image to see its maps."
        )
        self._apply.setEnabled(False)
        self._open.setEnabled(False)
        self._publish_selection(None)

    def _fill_layers(self, layers) -> None:
        wanted = next((layer for layer in layers if layer.slot == self._slot), None)
        if wanted is None and layers:
            self._slot = layers[0].slot
        labels = [self._layer_label(layer) for layer in layers]
        current = [self._layer_label(layer) for layer in layers if layer.slot == self._slot]
        self._layers.blockSignals(True)
        self._layers.clear()
        self._layers.addItems(labels)
        if current:
            self._layers.setCurrentText(current[0])
        self._layers.blockSignals(False)

    @staticmethod
    def _layer_label(layer: ms.LayerRow) -> str:
        if layer.slot < 0:
            return layer.label
        state = "" if layer.editable else " (read-only)"
        return f"BG{layer.slot} - {layer.classification}{state}"

    def _layer_summary(self, layers) -> str:
        paintable = sum(1 for layer in layers if layer.editable)
        note = f"{len(layers)} layer slot(s), {paintable} paintable in this build"
        if self._session.project is None:
            return f"{note}. Open a project to paint a cell."
        return note

    def _warp_summary(self, rows) -> str:
        if self._surface.transitions is None:
            return self._surface.transitions_problem or "no transition corpus here"
        note = f"{len(rows)} transition(s) out of this map"
        if not rows:
            return f"{note}; this map declares none in this image"
        if self._session.project is None:
            return f"{note}. Open a project to retarget one."
        return note

    def _records_message(self, rows) -> str:
        if self._session.project is None:
            return "No project is open, so there is nothing to edit."
        editable = sum(1 for row in rows if row.editable)
        return f"{editable} of {len(rows)} row(s) editable through the open project."

    def _cell_cells(self, row: ms.CellRow) -> tuple[str, ...]:
        return (
            f"{row.cell}",
            f"{row.column}",
            f"{row.row}",
            "-" if row.ordinal is None else f"{row.ordinal}",
            f"0x{row.offset:06X}",
            _support_cell(row.editable),
        )

    def _warp_cells(self, row: ms.WarpRow) -> tuple[str, ...]:
        return (
            row.label,
            f"{row.index}",
            row.destination_text,
            row.region_text,
            f"0x{row.file_offset:06X}",
            _support_cell(row.editable),
        )

    # -- the field editor -----------------------------------------------------

    def _caret_row(self):
        return next((row for row in self._rows if row.identity == self._caret), None)

    def _render_editor(self) -> None:
        row = self._caret_row()
        if row is None:
            self._field.blockSignals(True)
            self._field.clear()
            self._field.blockSignals(False)
            self._value.clear()
            self._apply.setEnabled(False)
            self._open.setEnabled(False)
            self._detail.clear()
            return
        field = row.field
        self._field.blockSignals(True)
        self._field.clear()
        self._field.addItem(field.name)
        self._field.setCurrentText(field.name)
        self._field.blockSignals(False)
        self._apply.setEnabled(row.editable)
        self._apply.setToolTip(
            row.note or f"Set {field.name} on {row.identity}"
        )
        self._open.setEnabled(True)
        self._open.setToolTip(
            f"Show the bytes this row owns in the ROM destination"
        )
        self._detail.setText(self._detail_text(row, field))
        self._publish_selection(
            InspectorContext(
                friendly=row.label if hasattr(row, "label") else row.identity,
                stable=row.identity,
                support="Editable" if row.editable else "Read-only",
                detail=row.note or f"{field.name} = {field.value}",
            )
        )
        self._on_field_changed()

    def _detail_text(self, row, field) -> str:
        offset = getattr(row, "offset", None)
        if offset is None:
            offset = row.file_offset
        return (
            f"{row.identity} | file offset 0x{offset:06X} | "
            f"{'Editable' if row.editable else 'Read-only'}"
            + (f" | {row.note}" if row.note else "")
        )

    def _on_field_changed(self, _text: str = "") -> None:
        row = self._caret_row()
        if row is None:
            return
        field = row.field
        self._value.setText(str(field.value))
        self._value.setToolTip(f"{field.name}: {field.range_text}")

    def _on_mode_changed(self, label: str) -> None:
        self._mode = next(
            (identifier for identifier, text in MODES if text == label), LAYOUT_MODE
        )
        self._caret = ""
        self.refresh()

    def _on_map_changed(self, _position: int) -> None:
        data = self._maps.currentData()
        if data is None:
            return
        self._map_index = int(data)
        self._caret = ""
        self._slot = 0
        self._layers.clear()
        self.refresh()

    def _on_layer_changed(self, _position: int) -> None:
        layer = self._current_layer()
        if layer is None:
            return
        self._slot = layer.slot
        self._caret = ""
        self.refresh()

    def _current_layer(self) -> ms.LayerRow | None:
        if self._surface is None:
            return None
        return self._surface.layer(self._map_index, self._slot)

    def _select_combo(self, combo: QComboBox, value: int) -> None:
        position = combo.findData(value)
        if position < 0 or position == combo.currentIndex():
            return
        combo.blockSignals(True)
        combo.setCurrentIndex(position)
        combo.blockSignals(False)

    def _select_caret(self) -> None:
        if not self._rows:
            return
        position = next(
            (at for at, row in enumerate(self._rows) if row.identity == self._caret), 0
        )
        self._caret = self._rows[position].identity
        self._select_row(position)

    def _select_row(self, position: int) -> None:
        """Point the table at a row without re-entering the selection handler."""
        selection = self._table.selectionModel()
        selection.blockSignals(True)
        self._table.selectRow(position)
        selection.blockSignals(False)

    def _on_row_changed(self, current, previous) -> None:
        if not current.isValid() or current.row() >= len(self._rows):
            return
        self._caret = self._rows[current.row()].identity
        self._render_editor()

    # -- actions --------------------------------------------------------------

    def _on_apply(self) -> None:
        """Commit one map edit to the session's journal, or state why not."""
        row = self._caret_row()
        if row is None or self._surface is None:
            return
        if self._session.project is None:
            self._report("No project is open, so there is nothing to edit.")
            return
        if not row.editable:
            self._report(row.note or f"{row.identity} cannot be edited.")
            return
        field = row.field
        try:
            value = int(self._value.text().strip(), 0)
        except ValueError:
            self._report(f"{field.name} must be a whole number.")
            return
        if value < field.minimum or value > field.maximum:
            self._report(
                f"{field.name}={value} is outside the supported range "
                f"{field.range_text}."
            )
            return
        if value == field.value:
            self._report(f"{field.name} is already {value}.")
            return
        if isinstance(row, ms.CellRow):
            self._apply_cell(row, value)
        else:
            self._apply_warp(row, value)

    def _apply_cell(self, row: ms.CellRow, ordinal: int) -> None:
        after = ms.with_layout_cell(read_maps(self._session.project), row, ordinal)
        try:
            # The SDK's own painter judges the batch before anything is written
            # down, so a value it would refuse never becomes a journal entry.
            self._surface.changes(after)
        except Exception as exc:  # noqa: BLE001 - the refusal text is the report
            self._report(str(exc))
            return
        self._commit(row, after, (ms.layout_span(row),), ordinal)

    def _apply_warp(self, row: ms.WarpRow, destination: int) -> None:
        try:
            ms.check_transition(self._surface.transitions, row, destination)
            after = ms.with_warp_destination(
                read_maps(self._session.project),
                self._surface.transitions,
                row,
                destination,
            )
            self._surface.changes(after)
        except Exception as exc:  # noqa: BLE001 - the refusal text is the report
            self._report(str(exc))
            return
        self._commit(
            row, after, (RomRange(FileOffset(row.file_offset), row.size),), destination
        )

    def _commit(self, row, after, claimed, value) -> None:
        revision = self._session.journal.current_revision
        self._applying = True
        try:
            self._edit_handler(
                kind=EditKind.SEMANTIC,
                target=MAPS_TARGET,
                after=after,
                claimed=claimed,
                reason=f"{row.identity} edit: {row.field.name}",
            )
        finally:
            self._applying = False
        self.refresh()
        if self._session.journal.current_revision != revision:
            self._caret = row.identity
            self._select_caret()
            self._render_editor()
            self._report(f"{row.identity} {row.field.name} = {value}")

    def _on_open(self) -> None:
        row = self._caret_row()
        if row is None or self._open_handler is None:
            return
        offset = getattr(row, "offset", None)
        if offset is None:
            offset = row.file_offset
        self._open_handler(offset)

    def _report(self, text: str) -> None:
        self._message.setText(text)

    def _publish_selection(self, context: InspectorContext | None) -> None:
        if self._selection_handler is not None:
            self._selection_handler(context)

    # -- the open image -------------------------------------------------------

    def _ensure_surface(self) -> None:
        session = self._session
        if (
            session.base_image is None
            or session.profile is None
            or session.identification is None
            or session.rom_path is None
            or session.catalog is None
        ):
            self._surface = None
            self._surface_for = None
            self._problem = ""
            return
        if self._surface_for == session.rom_path and self._surface is not None:
            return
        self._surface_for = session.rom_path
        try:
            self._surface = ms.load_map_surface(
                session.rom_path,
                session.catalog,
                session.identification,
                session.profile,
                session.base_image,
            )
        except ms.MapSurfaceError as exc:
            self._surface = None
            self._problem = str(exc)
