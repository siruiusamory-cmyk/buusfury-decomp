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
    QBrush,
    QColor,
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
    QFrame,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from tools.webfoot import map_view as mv
from tools.webfoot.map_layout_edit import (
    LayoutGrid,
    LayoutTarget,
    MapLayoutEditError,
    MapLayoutEditor,
)
from tools.webfoot.map_layout_write import MapLayoutWriteError
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
    mv.MapBrowserError,
    WriteError,
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
        self._last_dirty = 0
        #: The palette's full height, measured from its own content in
        #: `_size_chunk_chooser`; the palette collapses to its header without it.
        self._palette_height = 0
        #: True while a parent editor (the Maps editor) owns mode selection, so
        #: this tab does not render its own Edit Layout toggle a second time.
        self._modes_owned_by_host = False

        self._scene = QGraphicsScene(self)
        self._canvas = MapBrowserCanvas(self._scene)
        self._canvas.set_key_handler(self._on_canvas_key)
        self._canvas.set_hover_handler(self._on_canvas_hover)
        self._hover_text = ""
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
        self._reset_button = QPushButton("Reset all")
        self._reset_button.setToolTip("Discard every pending layout change in this session")
        self._reset_button.clicked.connect(self._reset_edits)
        self._save_button = QPushButton("Save As New ROM\u2026")
        self._save_button.setProperty("dbzRole", "primary")
        self._save_button.setToolTip(
            "Write the pending edits to a new ROM file; the source ROM is never "
            "modified. With no pending edits this writes a byte-identical copy."
        )
        self._save_button.clicked.connect(self._on_save_as)

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
        buttons.addWidget(self._apply_button)
        buttons.addWidget(self._revert_button)
        buttons.addWidget(self._reset_button)
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
        editor_layout.addLayout(buttons)
        editor_layout.addWidget(self._detail_row)
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
            "256\u00d7256 chunk cell to another chunk the same layer already uses."
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
        workspace.addWidget(centre_split)
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
        self._reset_editor()
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
            check.toggled.connect(self._show_composite)
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
        self._cell_label.setText("No cell selected")
        self._chunk_label.setText("")
        self._detail.setText("")

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
        self._cell_label.setText("No cell selected")
        self._chunk_label.setText("")
        self._change_label.setText("No layout changes")
        self._detail.setText("")
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
            images = mv.render_chunk_images(
                self._session.map_image,
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

    def _thumbnail(self, image: mv.ChunkImage) -> QPixmap:
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
        backed.fill(theme.color("checker_dark"))
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
            self._set_mode_badge(
                "EDIT LAYOUT \u00b7 click a 256\u00d7256 cell, then choose a chunk", "edit"
            )
        self._sync_chooser_presence()

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
            # No cell picked yet: say what to do, rather than three dash rows.
            self._cell_label.setText("No cell selected")
            self._chunk_label.setText("")
            self._detail.setText("")

        unsaved = self._unsaved_count()
        if not edits:
            self._set_change_label("No layout changes", "neutral")
        elif unsaved:
            self._set_change_label(
                f"{unsaved} unsaved layout change(s) \u00b7 {len(edits)} pending", "pending"
            )
        else:
            self._set_change_label(
                f"{len(edits)} layout change(s) saved to a new ROM", "saved"
            )

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

        Public because the shell shows the same number in the window title and
        the status bar, and two authorities on "is there unsaved work" would drift.
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
        """
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
            if self._draft is not None:
                parts.append("previewing an unapplied choice")
            elif self._slot is None:
                parts.append("no editable layer on this map")
            elif self._editor is not None:
                edits = self._editor.edits_for(result.index)
                unsaved = self._unsaved_count()
                if edits and unsaved:
                    parts.append(f"{unsaved} unsaved change(s)")
                elif edits:
                    parts.append(f"{len(edits)} change(s) saved")
                else:
                    parts.append("no changes yet")
        else:
            parts.append("read-only")
        if self._hover_text:
            parts.append(self._hover_text)
        self._publish_status("  \u00b7  ".join(parts))

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
        # committed rather than silently dropped. The emit builds at a temporary
        # sibling and only then replaces the destination, so an existing file at the
        # chosen path survives a failed save untouched - hence no delete here.
        self._apply_draft()
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
            f"Its provenance manifest was written beside it:\n{saved.manifest_path.name}\n"
            "DragonByte Z can reopen this ROM from that manifest.\n\n"
            "The source ROM was not modified.",
        )
