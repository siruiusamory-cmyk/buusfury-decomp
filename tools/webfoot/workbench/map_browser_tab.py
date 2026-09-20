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

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFontDatabase,
    QIcon,
    QImage,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from tools.export import map_browser as mb
from tools.webfoot.map_layout_edit import (
    LayoutGrid,
    LayoutTarget,
    MapLayoutEditError,
    MapLayoutEditor,
)
from tools.webfoot.map_layout_write import MapLayoutWriteError
from tools.webfoot.write import WriteError

from .build_panel import is_safe_output_path
from .session import Session

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

#: The shell's gold accent, reused for the layout states so the editing surface
#: belongs to the tab's existing visual language.
_ACCENT = QColor("#F3C94B")
_WARNING = QColor("#F0A93B")
_SUCCESS = QColor("#7FC98B")
_MUTED = QColor("#8A97A6")

_IDENTITY_ROLE = Qt.ItemDataRole.UserRole
_CHUNK_ROLE = Qt.ItemDataRole.UserRole + 1

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
#: ``MapBrowserError`` (the render facade the chooser and preview call) and
#: ``WriteError`` (the ROM emit path, also unrelated to the other three).
_EDIT_ERRORS = (
    MapLayoutEditError,
    MapLayoutWriteError,
    mb.MapBrowserError,
    WriteError,
)


def _checkerboard() -> QBrush:
    """A navy checkerboard for the canvas: unpainted (index 0) pixels show it."""
    cell = 12
    pixmap = QPixmap(cell * 2, cell * 2)
    pixmap.fill(QColor("#1B2129"))
    painter = QPainter(pixmap)
    painter.fillRect(0, 0, cell, cell, QColor("#232B36"))
    painter.fillRect(cell, cell, cell, cell, QColor("#232B36"))
    painter.end()
    return QBrush(pixmap)


class ChunkGridOverlay(QGraphicsItem):
    """The editable chunk-cell grid drawn over one dominant layer of the map.

    One cell is one 256x256 chunk region, so the grid is the layer's own chunk
    count in both directions. Cells are click targets; the selected cell, the
    hovered cell and cells that already carry a pending edit are each marked
    distinctly - by fill, border style and corner marker, never by hue alone.
    """

    def __init__(self, grid: LayoutGrid, on_cell_clicked) -> None:
        super().__init__()
        self._grid = grid
        self._on_cell_clicked = on_cell_clicked
        self._selected: int | None = None
        self._hovered: int | None = None
        self._edited: frozenset[int] = frozenset()
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        self.setToolTip(
            "Each cell is one 256×256 chunk region. Click a cell to choose a "
            "different chunk for it."
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        for cell in range(self._grid.cell_count):
            x, y, width, height = self._grid.cell_rect(cell)
            rect = QRectF(x, y, width, height)
            if cell in self._edited:
                painter.fillRect(rect, QColor(243, 201, 75, 40))
                marker = 10
                painter.fillRect(
                    QRectF(x + 3, y + 3, marker, marker), QColor(243, 201, 75, 210)
                )
            if cell == self._hovered and cell != self._selected:
                painter.fillRect(rect, QColor(255, 255, 255, 26))
        # Grid lines: cosmetic, so they stay one device pixel at any zoom.
        grid_pen = QPen(QColor(243, 201, 75, 120))
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
            hover_pen = QPen(QColor(255, 255, 255, 170))
            hover_pen.setCosmetic(True)
            hover_pen.setWidthF(2.0)
            painter.setPen(hover_pen)
            painter.drawRect(QRectF(x, y, width, height).adjusted(1, 1, -1, -1))
        if self._selected is not None:
            x, y, width, height = self._grid.cell_rect(self._selected)
            selected_pen = QPen(_ACCENT)
            selected_pen.setCosmetic(True)
            selected_pen.setWidthF(3.0)
            painter.setPen(selected_pen)
            painter.fillRect(QRectF(x, y, width, height), QColor(243, 201, 75, 64))
            painter.drawRect(QRectF(x, y, width, height).adjusted(1, 1, -2, -2))

    def hoverMoveEvent(self, event) -> None:
        cell = self._grid.cell_at(int(event.pos().x()), int(event.pos().y()))
        if cell != self._hovered:
            self._hovered = cell
            self.update()
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
                self._on_cell_clicked(cell)
                event.accept()
                return
        super().mousePressEvent(event)


class MapBrowserCanvas(QGraphicsView):
    """Crisp map viewport with wheel zoom, middle-drag pan and fit-to-window.

    In layout edit mode the tab installs a key handler: arrow keys move the chunk
    cell selection and Enter applies the pending chunk change.
    """

    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__(scene)
        self._panning = False
        self._pan_position = None
        self._key_handler = None
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setBackgroundBrush(_checkerboard())

    def set_key_handler(self, handler) -> None:
        """Install (or clear) the edit-mode key handler: it returns True if used."""
        self._key_handler = handler

    def zoom_in(self) -> None:
        self._change_zoom(1.25)

    def zoom_out(self) -> None:
        self._change_zoom(0.8)

    def fit_map(self) -> None:
        rect = self.sceneRect()
        if rect.isEmpty():
            return
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def reset_zoom(self) -> None:
        self.resetTransform()

    def _change_zoom(self, factor: float) -> None:
        current = self.transform().m11()
        target = current * factor
        if not 0.0625 <= target <= 32:
            return
        self.scale(factor, factor)

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
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._panning and event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self._pan_position = None
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class MapBrowserTab(QWidget):
    """Map browser: list + search | viewer | inspector, plus an Edit Layout mode."""

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session
        self._entries: dict[int, mb.MapIndexEntry] = {}
        self._render_cache: "OrderedDict[int, mb.MapBrowserResult]" = OrderedDict()
        self._current: mb.MapBrowserResult | None = None
        self._layer_checks: dict[int, QCheckBox] = {}

        # -- layout editing state, all in-memory -----------------------------
        self._edit_mode = False
        self._editor: MapLayoutEditor | None = None
        self._editor_error: str | None = None
        self._target: LayoutTarget | None = None
        self._slot = None
        self._selected_cell: int | None = None
        #: One uncommitted chooser pick: (layer slot, cell, replacement).
        self._draft: tuple[int, int, int] | None = None
        #: The edit set as last written to a ROM, so "saved" and "unsaved" differ.
        self._saved: dict[tuple[int, int, int], int] = {}
        self._thumbnails: dict[int, QPixmap] = {}
        self._suppress_chooser = False

        self._scene = QGraphicsScene(self)
        self._canvas = MapBrowserCanvas(self._scene)
        self._canvas.set_key_handler(self._on_canvas_key)
        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._grid_item: ChunkGridOverlay | None = None

        # -- LEFT: search + map list -----------------------------------------
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search by name or map id (e.g. West City, map:0017)")
        self._search.textChanged.connect(self._apply_filter)
        self._list = QListWidget()
        self._list.currentItemChanged.connect(self._on_selection)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self._search)
        left_layout.addWidget(self._list, 1)

        # -- CENTER: edit mode + layer toggles + zoom + canvas ---------------
        self._edit_toggle = QPushButton("Edit Layout")
        self._edit_toggle.setCheckable(True)
        self._edit_toggle.setEnabled(False)
        self._edit_toggle.setToolTip(
            "Edit a supported map's dominant-layer chunk layout. Browsing stays "
            "read-only until this is on."
        )
        self._edit_toggle.toggled.connect(self._on_edit_mode_toggled)

        self._layers_box = QWidget()
        self._layers_layout = QHBoxLayout(self._layers_box)
        self._layers_layout.setContentsMargins(0, 0, 0, 0)
        self._layers_layout.addWidget(QLabel("Layers:"))
        self._zoom_out = QPushButton("−")
        self._zoom_out.setToolTip("Zoom out")
        self._zoom_out.clicked.connect(self._canvas.zoom_out)
        self._zoom_in = QPushButton("+")
        self._zoom_in.setToolTip("Zoom in")
        self._zoom_in.clicked.connect(self._canvas.zoom_in)
        self._fit = QPushButton("Fit")
        self._fit.setToolTip("Fit the map to the window")
        self._fit.clicked.connect(self._canvas.fit_map)
        self._actual = QPushButton("100%")
        self._actual.setToolTip("Reset to 1:1 pixels")
        self._actual.clicked.connect(self._canvas.reset_zoom)
        toolbar = QHBoxLayout()
        toolbar.addWidget(self._edit_toggle)
        toolbar.addSpacing(12)
        toolbar.addWidget(self._layers_box, 1)
        toolbar.addWidget(self._zoom_out)
        toolbar.addWidget(self._zoom_in)
        toolbar.addWidget(self._actual)
        toolbar.addWidget(self._fit)
        canvas_box = QGroupBox("Map")
        canvas_layout = QVBoxLayout(canvas_box)
        canvas_layout.addLayout(toolbar)
        canvas_layout.addWidget(self._canvas, 1)

        # -- RIGHT: layout editor, chunk chooser, map information -------------
        self._mode_badge = QLabel("VIEW MODE · read-only")
        mode_font = self._mode_badge.font()
        mode_font.setBold(True)
        self._mode_badge.setFont(mode_font)
        self._mode_badge.setWordWrap(True)
        #: The full explanation behind a READ ONLY badge, kept quiet and separate
        #: so the badge itself stays a one-line state a user can read at a glance.
        self._read_only_detail = QLabel("")
        self._read_only_detail.setWordWrap(True)
        self._read_only_detail.setStyleSheet("color: #8A97A6;")

        self._layer_combo = QComboBox()
        self._layer_combo.setToolTip("Which dominant layer of this map to edit")
        self._layer_combo.currentIndexChanged.connect(self._on_layer_changed)

        self._cell_label = QLabel("—")
        self._cell_label.setWordWrap(True)
        self._chunk_label = QLabel("—")
        self._chunk_label.setWordWrap(True)
        self._change_label = QLabel("No layout changes")
        self._change_label.setWordWrap(True)

        self._apply_button = QPushButton("Apply")
        self._apply_button.setToolTip("Commit the chosen chunk to the selected cell (Enter)")
        self._apply_button.clicked.connect(self._apply_draft)
        self._revert_button = QPushButton("Revert cell")
        self._revert_button.setToolTip(
            "Put the selected cell back to the chunk the source ROM holds (Esc)"
        )
        self._revert_button.clicked.connect(self._revert_cell)
        self._reset_button = QPushButton("Reset pending edits")
        self._reset_button.setToolTip("Discard every pending layout change in this session")
        self._reset_button.clicked.connect(self._reset_edits)
        self._save_button = QPushButton("Save As New ROM…")
        self._save_button.setToolTip(
            "Write the pending edits to a new ROM file; the source ROM is never "
            "modified. With no pending edits this writes a byte-identical copy."
        )
        self._save_button.clicked.connect(self._on_save_as)

        editor_form = QFormLayout()
        editor_form.addRow("Layer", self._layer_combo)
        editor_form.addRow("Selected cell", self._cell_label)
        editor_form.addRow("Chunk", self._chunk_label)
        editor_form.addRow("Changes", self._change_label)
        self._editor_form = editor_form
        buttons = QHBoxLayout()
        buttons.addWidget(self._apply_button)
        buttons.addWidget(self._revert_button)
        buttons.addWidget(self._reset_button)
        self._detail = QLabel("—")
        self._detail.setWordWrap(True)
        self._detail.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self._detail.setStyleSheet("color: #8A97A6;")

        editor_layout = QVBoxLayout()
        editor_layout.addWidget(self._mode_badge)
        editor_layout.addWidget(self._read_only_detail)
        editor_layout.addLayout(editor_form)
        editor_layout.addLayout(buttons)
        editor_layout.addWidget(self._save_button)
        editor_layout.addWidget(self._detail)
        self._editor_box = QGroupBox("Layout editor")
        self._editor_box.setLayout(editor_layout)

        self._chooser_hint = QLabel("Select a map to see its chunks.")
        self._chooser_hint.setWordWrap(True)
        self._chooser_hint.setStyleSheet("color: #8A97A6;")
        self._chooser = QListWidget()
        self._chooser.setViewMode(QListWidget.ViewMode.IconMode)
        self._chooser.setIconSize(QSize(64, 64))
        self._chooser.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._chooser.setMovement(QListWidget.Movement.Static)
        self._chooser.setUniformItemSizes(False)
        self._chooser.setWordWrap(True)
        self._chooser.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._chooser.setToolTip(
            "Only chunks this layer already uses can replace a cell's chunk."
        )
        self._chooser.currentItemChanged.connect(self._on_chunk_selected)
        chooser_layout = QVBoxLayout()
        chooser_layout.addWidget(self._chooser_hint)
        chooser_layout.addWidget(self._chooser, 1)
        self._chooser_box = QGroupBox("Replace chunk")
        self._chooser_box.setLayout(chooser_layout)

        self._name = QLabel("—")
        self._name.setWordWrap(True)
        self._identity = QLabel("—")
        self._dimensions = QLabel("—")
        self._layer_count = QLabel("—")
        self._layer_types = QLabel("—")
        self._layer_types.setWordWrap(True)
        self._notes = QLabel("—")
        self._notes.setWordWrap(True)
        info_form = QFormLayout()
        info_form.addRow("Name", self._name)
        info_form.addRow("Map ID", self._identity)
        info_form.addRow("Dimensions", self._dimensions)
        info_form.addRow("Layers", self._layer_count)
        info_form.addRow("Layer types", self._layer_types)
        info_form.addRow("Notes", self._notes)
        info_box = QGroupBox("Map information")
        info_box.setLayout(info_form)

        right_body = QWidget()
        right_layout = QVBoxLayout(right_body)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self._editor_box)
        right_layout.addWidget(self._chooser_box)
        right_layout.addWidget(info_box)
        right_layout.addStretch(1)
        right_scroll = QScrollArea()
        right_scroll.setWidget(right_body)
        right_scroll.setWidgetResizable(True)
        right_scroll.setMinimumWidth(340)

        center_split = QSplitter(Qt.Orientation.Horizontal)
        center_split.addWidget(canvas_box)
        center_split.addWidget(right_scroll)
        center_split.setStretchFactor(0, 1)
        center_split.setSizes([860, 360])

        workspace = QSplitter(Qt.Orientation.Horizontal)
        workspace.addWidget(left)
        workspace.addWidget(center_split)
        workspace.setStretchFactor(1, 1)
        workspace.setSizes([260, 1120])

        self._status = QLabel("Open a supported ROM to browse maps.")
        root = QVBoxLayout(self)
        root.addWidget(workspace, 1)
        root.addWidget(self._status)

        self._apply_style()
        self._size_chunk_chooser()
        self._show_edit_groups(False)

    def _size_chunk_chooser(self) -> None:
        """Size the chooser's cells for a thumbnail *and* two text lines.

        Each item carries an explicit size hint rather than relying on the view's
        grid: with a grid, a two-line item is clipped to the grid cell that the
        *first* item's size hint produced, which silently elides the state tag
        (``current`` / ``original``) that marks the selected cell's chunk. The
        text height comes from the real font, so a scaled desktop or a larger UI
        font grows the cell instead of eating the tag.
        """
        line = self._chooser.fontMetrics().lineSpacing()
        self._chooser_cell = QSize(100, 64 + 2 * line + 16)
        self._chooser.setMinimumHeight(2 * self._chooser_cell.height() + 8)

    def _apply_style(self) -> None:
        """Restrained navy/blue-gray shell with a gold selection accent.

        Scoped to this tab so the existing tabs keep their current look; the hex
        values match the palette the other visual tabs already use.
        """
        self.setStyleSheet(
            """
            QWidget { background-color: #141A22; color: #F5F7FA; }
            QGroupBox { border: 1px solid #2A3340; margin-top: 10px; padding-top: 8px; }
            QGroupBox::title { color: #F3C94B; subcontrol-origin: margin; left: 8px; }
            QLineEdit, QListWidget, QComboBox { background-color: #1B2129;
                                      border: 1px solid #2A3340;
                                      border-radius: 3px; padding: 4px; }
            QComboBox QAbstractItemView { background-color: #1B2129; color: #F5F7FA; }
            QListWidget::item { padding: 4px; }
            QListWidget::item:selected { background-color: #3A3220; color: #F3C94B; }
            QListWidget::item:hover { background-color: #20262F; }
            QCheckBox { background: transparent; }
            QPushButton { background-color: #232B36; border: 1px solid #2A3340;
                          border-radius: 3px; padding: 3px 10px; }
            QPushButton:hover { background-color: #2A3340; }
            QPushButton:checked { background-color: #3A3220; color: #F3C94B;
                                  border: 1px solid #F3C94B; }
            QPushButton:disabled { color: #5A6675; background-color: #1B2129; }
            QLabel { background: transparent; }
            QScrollArea { border: none; }
            """
        )

    # -- session wiring -------------------------------------------------------

    def on_session_changed(self) -> None:
        self._render_cache.clear()
        self._entries = {}
        self._current = None
        self._clear_layer_checks()
        self._reset_editor()
        self._list.blockSignals(True)
        self._list.clear()
        self._list.blockSignals(False)
        if self._session.rom_image is None:
            self._edit_toggle.setEnabled(False)
            self._show_placeholder("Open a supported ROM to browse its maps.")
            return
        try:
            index = mb.read_map_index(self._session.rom_image)
        except mb.MapBrowserError as exc:
            self._edit_toggle.setEnabled(False)
            self._show_placeholder(f"Cannot read the map index: {exc}")
            QMessageBox.critical(self, "Map Browser", str(exc))
            return
        self._entries = {entry.index: entry for entry in index}
        self._populate_list()
        self._edit_toggle.setEnabled(True)

    def _populate_list(self) -> None:
        self._list.blockSignals(True)
        self._list.clear()
        for entry in sorted(self._entries.values(), key=lambda item: item.index):
            name = entry.name or ""
            text = f"{name}  ·  map:{entry.index:04d}" if name else f"map:{entry.index:04d}"
            item = QListWidgetItem(text)
            item.setData(_IDENTITY_ROLE, entry.index)
            if name:
                item.setToolTip(name)
            self._list.addItem(item)
        self._list.blockSignals(False)
        self._apply_filter(self._search.text())

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
                result = mb.render_map(self._session.rom_image, index)
            except mb.MapBrowserError as exc:
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
        for check in self._layer_checks.values():
            self._layers_layout.removeWidget(check)
            # Removing from a layout does not unparent: until the deferred delete
            # runs, an orphan would still paint at its stale geometry and overlap
            # the next map's own checkboxes.
            check.setParent(None)
            check.deleteLater()
        self._layer_checks = {}

    def _populate_layer_checks(self) -> None:
        self._clear_layer_checks()
        result = self._current
        if result is None:
            return
        for layer in result.layers:
            if not layer.graphical:
                continue
            check = QCheckBox(f"BG{layer.slot} · {_LAYER_LABELS.get(layer.classification, layer.classification)}")
            check.setChecked(True)
            check.setToolTip(layer.classification)
            check.toggled.connect(self._show_composite)
            self._layer_checks[layer.slot] = check
            self._layers_layout.addWidget(check)

    def _visible_layers(self) -> tuple[mb.MapBrowserLayer, ...]:
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
            indices = mb.compose(visible, result.width, result.height)
            pixmap = self._pixmap_from_indices(indices, result.width, result.height, result.palette)
        except mb.MapBrowserError as exc:
            QMessageBox.warning(self, "Map Browser", str(exc))
            return
        self._set_map_pixmap(pixmap, result.width, result.height)

    def _pixmap_from_indices(self, indices: bytes, width: int, height: int, palette) -> QPixmap:
        rgba = mb.rgba(indices, palette)
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
        self._layer_types.setText("\n".join(lines))
        self._notes.setText("\n".join(result.warnings) if result.warnings else "—")

    def _show_placeholder(self, message: str) -> None:
        self._current = None
        self._clear_layer_checks()
        self._forget_map_selection()
        self._scene.clear()
        self._pixmap_item = None
        self._grid_item = None
        text = QGraphicsSimpleTextItem(message)
        text.setBrush(QColor("#F5F7FA"))
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
        self._selected_cell = None
        self._draft = None
        self._thumbnails = {}
        self._clear_grid_item()
        self._chooser.blockSignals(True)
        self._chooser.clear()
        self._chooser.blockSignals(False)
        self._chooser_hint.setText("No editable layer is selected on this map.")
        self._layer_combo.blockSignals(True)
        self._layer_combo.clear()
        self._layer_combo.blockSignals(False)
        self._cell_label.setText("—")
        self._chunk_label.setText("—")
        self._detail.setText("—")

    def _reset_editor(self) -> None:
        """Drop all edit-session state; the ROM, and so the base, has changed."""
        self._editor = None
        self._editor_error = None
        self._target = None
        self._slot = None
        self._selected_cell = None
        self._draft = None
        self._saved = {}
        self._thumbnails = {}
        # A new ROM starts in view mode: leaving the toggle checked would claim an
        # editing mode for an image the tab has not judged yet.
        self._edit_mode = False
        self._edit_toggle.blockSignals(True)
        self._edit_toggle.setChecked(False)
        self._edit_toggle.blockSignals(False)
        self._show_edit_groups(False)
        self._clear_grid_item()
        self._chooser.clear()
        self._chooser_hint.setText("Select a map to see its chunks.")
        self._mode_badge.setText("VIEW MODE · read-only")
        self._mode_badge.setStyleSheet("")
        self._cell_label.setText("—")
        self._chunk_label.setText("—")
        self._change_label.setText("No layout changes")
        self._detail.setText("—")
        self._layer_combo.blockSignals(True)
        self._layer_combo.clear()
        self._layer_combo.blockSignals(False)

    def _editor_session(self) -> MapLayoutEditor | None:
        """The edit session for the open ROM, or None with the reason recorded."""
        if self._editor is not None or self._editor_error is not None:
            return self._editor
        if self._session.rom_image is None:
            self._editor_error = "no ROM is open"
            return None
        try:
            self._editor = MapLayoutEditor(self._session.rom_image)
        except MapLayoutEditError as exc:
            # Unsupported image: the browser keeps working, read-only.
            self._editor_error = str(exc)
        return self._editor

    def _sync_editor_for_map(self, index: int) -> None:
        """Re-point the edit surface at the newly selected map."""
        self._forget_map_selection()
        editor = self._editor_session()
        if editor is None:
            self._editor_box.setToolTip(self._editor_error or "")
            self._refresh_editor_state()
            return
        try:
            self._target = editor.target(index)
        except MapLayoutEditError as exc:
            self._editor_box.setToolTip(str(exc))
            self._target = None
            self._refresh_editor_state()
            return
        self._editor_box.setToolTip("")
        self._layer_combo.blockSignals(True)
        self._layer_combo.clear()
        for slot in self._target.editable_slots:
            self._layer_combo.addItem(slot.label, slot.slot)
        self._layer_combo.blockSignals(False)
        if self._layer_combo.count():
            self._layer_combo.setCurrentIndex(0)
            self._select_layer(self._layer_combo.itemData(0))
        else:
            self._slot = None
            self._populate_chooser()
        self._refresh_editor_state()

    def _select_layer(self, layer_slot: int | None) -> None:
        """Point the editor and the grid overlay at one dominant layer slot."""
        self._draft = None
        self._slot = None
        self._selected_cell = None
        self._thumbnails = {}
        if self._target is None or layer_slot is None:
            self._clear_grid_item()
            self._populate_chooser()
            return
        slot = self._target.slots[layer_slot]
        self._slot = slot if slot.editable else None
        if self._slot is not None:
            # An edited layer must stay visible: a hidden layer would silently
            # swallow the preview the user is judging.
            check = self._layer_checks.get(layer_slot)
            if check is not None and not check.isChecked():
                check.setChecked(True)
            self._selected_cell = 0
        self._install_grid_item()
        self._populate_chooser()
        self._sync_chooser_selection()

    def _install_grid_item(self) -> None:
        self._clear_grid_item()
        if not self._edit_mode or self._slot is None:
            return
        self._grid_item = ChunkGridOverlay(self._slot.grid, self._on_cell_clicked)
        self._scene.addItem(self._grid_item)
        self._grid_item.set_selected(self._selected_cell)

    def _clear_grid_item(self) -> None:
        if self._grid_item is not None and self._grid_item.scene() is self._scene:
            self._scene.removeItem(self._grid_item)
        self._grid_item = None

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
        self._editor_box.setVisible(visible)
        self._chooser_box.setVisible(visible)

    def _on_layer_changed(self, _row: int) -> None:
        self._select_layer(self._layer_combo.currentData())
        self._refresh_editor_state()

    def _on_cell_clicked(self, cell: int) -> None:
        """A chunk cell was clicked on the map."""
        if self._slot is None or not self._slot.grid.contains(cell):
            return
        self._selected_cell = cell
        self._draft = None
        if self._grid_item is not None:
            self._grid_item.set_selected(cell)
        self._sync_chooser_selection()
        self._refresh_preview()
        self._refresh_editor_state()
        self._canvas.setFocus()

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
        """Fill the chooser with this layer's own existing chunks, as artwork."""
        self._chooser.blockSignals(True)
        self._chooser.clear()
        slot = self._slot
        if slot is None or self._current is None:
            self._chooser.blockSignals(False)
            self._chooser_hint.setText(
                "No editable layer is selected on this map."
            )
            return
        self._chooser_hint.setText(
            f"Chunks BG{slot.slot} already uses ({len(slot.choices)}). "
            "Only these can replace a cell's chunk."
        )
        try:
            # The session's cached character block, so a refill does not re-decode
            # what the preview already decoded. Thumbnail expansion stays inside
            # this guard: it is the same facade error family.
            images = mb.render_chunk_images(
                self._session.rom_image,
                self._current.index,
                slot.choices,
                char_data=(
                    self._editor.character_block(self._current.index)
                    if self._editor is not None
                    else None
                ),
            )
            for ordinal, image in enumerate(images, start=1):
                item = QListWidgetItem(QIcon(self._thumbnail(image)), f"Chunk {ordinal}")
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
        finally:
            self._chooser.blockSignals(False)

    def _thumbnail(self, image: mb.ChunkImage) -> QPixmap:
        """A small chunk image on the canvas checkerboard, cached per address."""
        cached = self._thumbnails.get(image.address)
        if cached is not None:
            return cached
        pixmap = self._pixmap_from_indices(image.pixels, image.width, image.height, self._current.palette)
        scaled = pixmap.scaled(
            QSize(64, 64),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        backed = QPixmap(scaled.size())
        backed.fill(QColor("#1B2129"))
        painter = QPainter(backed)
        painter.fillRect(backed.rect(), _checkerboard())
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        self._thumbnails[image.address] = backed
        return backed

    def _sync_chooser_selection(self) -> None:
        """Show the selected cell's current chunk, and tag the chooser's items."""
        slot = self._slot
        if slot is None or self._current is None:
            return
        working = None
        original = None
        if self._selected_cell is not None:
            working = self._working_pointer(slot.slot, self._selected_cell)
            original = slot.cells[self._selected_cell].pointer
        self._suppress_chooser = True
        for row in range(self._chooser.count()):
            item = self._chooser.item(row)
            pointer = item.data(_CHUNK_ROLE)
            ordinal = slot.ordinal_of(pointer) or row + 1
            tags = []
            if working is not None and pointer == working:
                tags.append("current")
            elif original is not None and pointer == original:
                tags.append("original")
            item.setText(f"Chunk {ordinal}" + (f"\n{' · '.join(tags)}" if tags else ""))
            font = item.font()
            font.setBold(working is not None and pointer == working)
            item.setFont(font)
        if working is not None:
            row = self._chooser_row_for(working)
            if row is not None:
                self._chooser.setCurrentRow(row)
        else:
            self._chooser.setCurrentRow(-1)
        self._suppress_chooser = False

    def _chooser_row_for(self, pointer: int) -> int | None:
        for row in range(self._chooser.count()):
            if self._chooser.item(row).data(_CHUNK_ROLE) == pointer:
                return row
        return None

    def _on_chunk_selected(self, current: QListWidgetItem | None, _previous=None) -> None:
        """A chooser pick previews immediately; Apply commits it."""
        if self._suppress_chooser or current is None or self._slot is None:
            return
        if self._selected_cell is None:
            self._status.setText("Select a chunk cell on the map first.")
            return
        replacement = current.data(_CHUNK_ROLE)
        self._draft = (self._slot.slot, self._selected_cell, replacement)
        self._refresh_preview()
        self._refresh_editor_state()

    # -- layout editing: apply, revert, reset, preview ------------------------

    def _working_pointer(self, layer_slot: int, cell: int) -> int:
        """The pointer a cell holds once pending edits (not the draft) are applied."""
        if self._editor is None or self._current is None:
            return 0
        try:
            return self._editor.working_pointer(self._current.index, layer_slot, cell)
        except _EDIT_ERRORS:
            return 0

    def _apply_draft(self) -> None:
        """Commit the chooser's pick for the selected cell into the edit set."""
        if self._editor is None or self._current is None or self._draft is None:
            return
        layer_slot, cell, replacement = self._draft
        try:
            self._editor.set_cell(self._current.index, layer_slot, cell, replacement)
        except _EDIT_ERRORS as exc:
            QMessageBox.warning(self, "Layout edit", str(exc))
            return
        self._draft = None
        self._sync_chooser_selection()
        self._refresh_preview()
        self._refresh_editor_state()

    def _revert_cell(self) -> None:
        """Put the selected cell back to the chunk the source ROM holds."""
        if self._editor is None or self._current is None or self._slot is None:
            return
        if self._selected_cell is None:
            return
        self._draft = None
        try:
            self._editor.revert_cell(self._current.index, self._slot.slot, self._selected_cell)
        except _EDIT_ERRORS as exc:
            QMessageBox.warning(self, "Layout edit", str(exc))
            return
        self._sync_chooser_selection()
        self._refresh_preview()
        self._refresh_editor_state()

    def _reset_edits(self) -> None:
        """Discard every pending layout change in this session."""
        if self._editor is None:
            return
        dropped = self._editor.reset()
        self._draft = None
        self._saved = {}
        self._sync_chooser_selection()
        self._refresh_preview()
        self._refresh_editor_state()
        if dropped:
            self._status.setText(
                f"Discarded {dropped} pending layout change(s); the preview is back to "
                "the source ROM's layout."
            )

    def _preview_overrides(self) -> dict[tuple[int, int], int]:
        if self._editor is None or self._current is None:
            return {}
        try:
            return self._editor.overrides(self._current.index, self._draft)
        except _EDIT_ERRORS as exc:
            QMessageBox.warning(self, "Layout edit", str(exc))
            self._draft = None
            return {}

    def _refresh_preview(self) -> None:
        """Re-render the map with the pending edits applied, in memory only."""
        if self._editor is None or self._current is None:
            return
        index = self._current.index
        if not self._preview_overrides():
            cached = self._render_cache.get(index)
            if cached is not None:
                self._current = cached
            self._show_composite()
            return
        self._status.setText(f"Updating the map:{index:04d} preview…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
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
        if editing and slot is not None:
            self._grid_item.set_edited({edit.cell for edit in edits if edit.layer_slot == slot.slot})
        elif self._grid_item is not None:
            self._grid_item.set_edited(())

        # Mode badge: the tab says what state it is in and why, in words. The
        # badge is a one-line state; its explanation sits in the quiet label under
        # it, so a long reason cannot clip the state itself.
        self._read_only_detail.setText("")
        self._set_layer_row_visible(True)
        if not editing:
            self._mode_badge.setText("VIEW MODE · read-only until Edit Layout is on")
            self._mode_badge.setStyleSheet("color: #8A97A6;")
        elif self._editor is None:
            self._mode_badge.setText("READ ONLY · layout editing is unavailable")
            self._mode_badge.setStyleSheet("color: #8A97A6;")
            self._read_only_detail.setText(self._editor_error or "")
            self._set_layer_row_visible(False)
        elif target is None or not target.editable:
            reason = (
                target.read_only_reason if target is not None else "this map could not be read"
            )
            kind = target.read_only_kind if target is not None else ""
            self._mode_badge.setText(
                f"READ ONLY · {_READ_ONLY_BADGES.get(kind, 'unsupported layout type')}"
            )
            self._mode_badge.setStyleSheet("color: #F0A93B;")
            self._read_only_detail.setText(reason)
            self._set_layer_row_visible(False)
        else:
            self._mode_badge.setText(
                "EDIT LAYOUT · click a 256×256 cell, then choose a chunk"
            )
            self._mode_badge.setStyleSheet("color: #F3C94B;")

        # Selected cell and current chunk.
        if slot is not None and self._selected_cell is not None:
            cell = slot.cells[self._selected_cell]
            self._cell_label.setText(
                f"column {cell.column}, row {cell.row} · cell {cell.cell + 1} of "
                f"{slot.grid.cell_count}"
            )
            working = self._working_pointer(slot.slot, cell.cell)
            ordinal = slot.ordinal_of(working)
            used = len(slot.cells_using(working))
            self._chunk_label.setText(
                f"{self._chunk_name(ordinal)} · used by {used} cell(s) of BG{slot.slot}"
            )
            if self._draft is not None:
                self._detail.setText(
                    f"pending preview: {self._chunk_name(slot.ordinal_of(cell.pointer))} → "
                    f"{self._chunk_name(slot.ordinal_of(self._draft[2]))}\n"
                    f"field 0x{cell.offset:08X} (4 bytes, in place)"
                )
            else:
                self._detail.setText(
                    f"pointer {working:#010x}\n"
                    f"field 0x{cell.offset:08X} (4 bytes, in place)"
                )
        else:
            self._cell_label.setText("—")
            self._chunk_label.setText("—")
            self._detail.setText("—")

        unsaved = self._unsaved_count()
        if not edits:
            self._change_label.setText("No layout changes")
            self._change_label.setStyleSheet("color: #8A97A6;")
        elif unsaved:
            self._change_label.setText(
                f"● {unsaved} unsaved layout change(s) · {len(edits)} pending"
            )
            self._change_label.setStyleSheet("color: #F0A93B;")
        else:
            self._change_label.setText(f"✔ {len(edits)} layout change(s) saved to a new ROM")
            self._change_label.setStyleSheet("color: #7FC98B;")

        self._apply_button.setEnabled(editing and self._draft is not None)
        index = result.index if result is not None else None
        self._revert_button.setEnabled(
            editing
            and index is not None
            and slot is not None
            and self._selected_cell is not None
            and (
                self._draft is not None
                or self._editor is not None
                and self._editor.edit(index, slot.slot, self._selected_cell) is not None
            )
        )
        self._reset_button.setEnabled(editing and bool(edits))
        # Save As needs something to save: an editable layer on this map, the
        # no-op copy included, or pending changes made on another map.
        self._save_button.setEnabled(
            editing and self._editor is not None and (slot is not None or bool(edits))
        )
        self._layer_combo.setEnabled(editing and self._layer_combo.count() > 0)
        self._chooser.setEnabled(editing and slot is not None)
        self._update_status()

    def _update_status(self) -> None:
        result = self._current
        if result is None:
            return
        parts = [
            f"map:{result.index:04d}",
            f"{result.width}×{result.height}",
            f"{result.graphical_layer_count} graphical layer(s)",
        ]
        if self._edit_mode and self._slot is None:
            # Edit mode is on but this map has nothing to edit: say that, rather
            # than reporting an editing state the badge already calls read-only.
            parts.append("EDIT LAYOUT · no editable layer on this map")
        elif self._edit_mode:
            parts.append("EDIT LAYOUT")
            if self._draft is not None:
                parts.append("previewing an unapplied choice")
            if self._editor is not None:
                edits = self._editor.edits_for(result.index)
                unsaved = self._unsaved_count()
                if edits and unsaved:
                    parts.append(f"{unsaved} unsaved change(s)")
                elif edits:
                    parts.append(f"{len(edits)} change(s) saved")
                elif self._draft is None:
                    parts.append("no changes yet")
        else:
            parts.append("read-only")
        self._status.setText("  ·  ".join(parts))

    def _unsaved_count(self) -> int:
        """Pending changes that no Save As has written yet."""
        if self._editor is None:
            return 0
        return sum(
            1
            for edit in self._editor.edits()
            if self._saved.get((edit.map_index, edit.layer_slot, edit.cell))
            != edit.replacement
        )

    @staticmethod
    def _chunk_name(ordinal: int | None) -> str:
        return f"Chunk {ordinal}" if ordinal else "an empty cell"

    def _set_layer_row_visible(self, visible: bool) -> None:
        """Show or hide the Layer row's combo and its label together."""
        self._layer_combo.setVisible(visible)
        label = self._editor_form.labelForField(self._layer_combo)
        if label is not None:
            label.setVisible(visible)

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
        # Save As writes what the preview shows, so an unapplied chooser pick is
        # committed rather than silently dropped.
        self._apply_draft()
        if Path(chosen).exists():
            # The file dialog already asked the user whether to replace it. The
            # emit path creates a new file, so remove the old one first - after
            # re-asserting it is not the source ROM.
            try:
                Path(chosen).unlink()
            except OSError as exc:
                QMessageBox.critical(self, "Save As", f"Could not replace {chosen}: {exc}")
                return
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
        self._saved = {
            (edit.map_index, edit.layer_slot, edit.cell): edit.replacement
            for edit in self._editor.edits()
        }
        self._refresh_editor_state()
        detail = (
            "no layout changes were pending, so the copy is byte-identical to the "
            "source ROM"
            if saved.no_op
            else f"{len(saved.changes)} layout change(s), "
            f"{len(saved.changed_offsets)} byte(s) changed"
        )
        self._status.setText(f"Saved {saved.output_path} · {detail}")
        QMessageBox.information(
            self,
            "Save As",
            f"Wrote a new ROM:\n{saved.output_path}\n\n{detail}.\n"
            f"SHA-256 {saved.output_sha256}\n\n"
            "The source ROM was not modified.",
        )
