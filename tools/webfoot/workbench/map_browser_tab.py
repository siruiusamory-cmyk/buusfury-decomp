"""DRAGONBYTE-Z-MAP-BROWSER-001 - the read-only DragonByte Z Map Browser tab.

A thin presentation client over :mod:`tools.export.map_browser`: enumerate all 452
maps with their ROM-derived labels, render one map on demand, and let the user
search, zoom, pan and toggle individual graphical layers. The widget owns no ROM
format: every pixel, dimension, classification, name and palette comes from the
facade, which composes the accepted ASSET-EXPORT readers.

This tab is deliberately READ-ONLY. It is a browser/viewer, not the WORKBENCH-006
authoring workspace (``map_tab.py``), and it adds no editing, painting, object or
warp surface.
"""

from __future__ import annotations

from collections import OrderedDict

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QImage, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFormLayout,
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
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from tools.export import map_browser as mb

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

_IDENTITY_ROLE = Qt.ItemDataRole.UserRole


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


class MapBrowserCanvas(QGraphicsView):
    """Crisp map viewport with wheel zoom, middle-drag pan and fit-to-window."""

    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__(scene)
        self._panning = False
        self._pan_position = None
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setBackgroundBrush(_checkerboard())

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
    """Read-only map browser: list + search | viewer | info panel."""

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session
        self._entries: dict[int, mb.MapIndexEntry] = {}
        self._render_cache: "OrderedDict[int, mb.MapBrowserResult]" = OrderedDict()
        self._current: mb.MapBrowserResult | None = None
        self._layer_checks: dict[int, QCheckBox] = {}

        self._scene = QGraphicsScene(self)
        self._canvas = MapBrowserCanvas(self._scene)
        self._pixmap_item: QGraphicsPixmapItem | None = None

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

        # -- CENTER: layer toggles + zoom + canvas ---------------------------
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
        toolbar.addWidget(self._layers_box, 1)
        toolbar.addWidget(self._zoom_out)
        toolbar.addWidget(self._zoom_in)
        toolbar.addWidget(self._actual)
        toolbar.addWidget(self._fit)
        canvas_box = QGroupBox("Map")
        canvas_layout = QVBoxLayout(canvas_box)
        canvas_layout.addLayout(toolbar)
        canvas_layout.addWidget(self._canvas, 1)

        # -- RIGHT: info panel -----------------------------------------------
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

        center_split = QSplitter(Qt.Orientation.Horizontal)
        center_split.addWidget(canvas_box)
        center_split.addWidget(info_box)
        center_split.setStretchFactor(0, 1)
        center_split.setSizes([880, 300])

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
            QLineEdit, QListWidget { background-color: #1B2129; border: 1px solid #2A3340;
                                      border-radius: 3px; padding: 4px; }
            QListWidget::item { padding: 4px; }
            QListWidget::item:selected { background-color: #3A3220; color: #F3C94B; }
            QListWidget::item:hover { background-color: #20262F; }
            QCheckBox { background: transparent; }
            QPushButton { background-color: #232B36; border: 1px solid #2A3340;
                          border-radius: 3px; padding: 3px 10px; }
            QPushButton:hover { background-color: #2A3340; }
            QPushButton:disabled { color: #5A6675; background-color: #1B2129; }
            QLabel { background: transparent; }
            """
        )

    # -- session wiring -------------------------------------------------------

    def on_session_changed(self) -> None:
        self._render_cache.clear()
        self._entries = {}
        self._current = None
        self._clear_layer_checks()
        self._list.blockSignals(True)
        self._list.clear()
        self._list.blockSignals(False)
        if self._session.rom_image is None:
            self._show_placeholder("Open a supported ROM to browse its maps.")
            return
        try:
            index = mb.read_map_index(self._session.rom_image)
        except mb.MapBrowserError as exc:
            self._show_placeholder(f"Cannot read the map index: {exc}")
            QMessageBox.critical(self, "Map Browser", str(exc))
            return
        self._entries = {entry.index: entry for entry in index}
        self._populate_list()

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
        self._show_composite()
        self._populate_info()
        # The tab is visible by the time a user selects a map, so the viewport
        # already has its final geometry; fitting synchronously avoids a deferred
        # call that could outlive the canvas.
        self._canvas.fit_map()
        self._status.setText(
            f"map:{index:04d}  ·  {result.width}×{result.height}  ·  "
            f"{result.graphical_layer_count} graphical layer(s)  ·  rendered from the verified ROM"
        )

    def _clear_layer_checks(self) -> None:
        for check in self._layer_checks.values():
            self._layers_layout.removeWidget(check)
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
        self._scene.clear()
        self._pixmap_item = None
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
