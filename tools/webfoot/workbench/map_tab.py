"""WORKBENCH-006 visual map-authoring workspace.

The Map tab is a thin presentation client over ``map_render`` and ``scene``.
It renders the SDK's ROM-only indexed map output once, adapts that result to a
Qt pixmap, and overlays semantic placement markers at the coordinate API's
confirmed logical map pixels.  It contains no decompression, screen-entry,
palette, pointer, address, or position-bit arithmetic.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QKeySequence, QPainter, QPen, QUndoCommand, QUndoStack
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .. import map_render, scene as scene_sdk
from ..project import ProjectError
from .graphics_tab import indexed_pixmap
from .session import Session


class PlacementMarker(QGraphicsItem):
    """Neutral, semantic placement marker anchored exactly at a map pixel."""

    def __init__(
        self,
        placement: dict,
        *,
        movable: bool,
        drag_completed: Callable[[str, tuple[int, int], tuple[int, int]], bool],
    ) -> None:
        super().__init__()
        self.placement = placement
        self._drag_completed = drag_completed
        self._drag_origin: QPointF | None = None
        self.setPos(placement["position_x"], placement["position_y"])
        self.setZValue(20)
        self.setToolTip(placement["identity"])
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, movable)

        # The full semantic label appears for the selected object only.  This
        # keeps a dense retail map readable while never substituting a guessed
        # sprite/name for the placement identity.
        self._label = QGraphicsSimpleTextItem(placement["identity"].split("/")[-1], self)
        self._label.setBrush(QColor("#F5F7FA"))
        self._label.setPos(10, -18)
        self._label.setVisible(False)

    def boundingRect(self) -> QRectF:
        return QRectF(-10, -10, 20, 20)

    def paint(self, painter: QPainter, _option, _widget=None) -> None:
        painter.save()
        selected = self.isSelected()
        project_authored = self.placement.get("provenance") == "Project"
        # A light halo plus a dark edge remains visible over any palette and
        # distinguishes selection by shape/ring as well as colour.
        painter.setPen(QPen(QColor("#F5F7FA"), 4 if selected else 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(-7, -7, 14, 14))
        painter.setPen(QPen(QColor("#101722"), 2))
        painter.setBrush(QColor("#47C9FF") if project_authored else QColor("#F3C94B"))
        if project_authored:
            painter.drawPolygon((QPointF(0, -6), QPointF(6, 0), QPointF(0, 6), QPointF(-6, 0)))
        else:
            painter.drawEllipse(QRectF(-5, -5, 10, 10))
        if selected:
            painter.setPen(QPen(QColor("#FFFFFF"), 2))
            painter.drawLine(-11, 0, -8, 0)
            painter.drawLine(8, 0, 11, 0)
            painter.drawLine(0, -11, 0, -8)
            painter.drawLine(0, 8, 0, 11)
        painter.restore()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self._label.setVisible(bool(value))
            self.update()
        return super().itemChange(change, value)

    def mousePressEvent(self, event) -> None:
        self._drag_origin = self.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        origin = self._drag_origin
        super().mouseReleaseEvent(event)
        self._drag_origin = None
        if origin is None:
            return
        before = (round(origin.x()), round(origin.y()))
        after = (round(self.pos().x()), round(self.pos().y()))
        if before == after:
            return
        if not self._drag_completed(self.placement["identity"], before, after):
            self.setPos(origin)


class MapCanvasView(QGraphicsView):
    """Crisp map viewport with editor-standard middle pan and wheel zoom."""

    cursorMoved = Signal(int, int)
    nudgeRequested = Signal(int, int)
    zoomChanged = Signal(float)

    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__(scene)
        self._panning = False
        self._pan_position: QPointF | None = None
        self._fit_rect = QRectF()
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setBackgroundBrush(QColor("#18202B"))

    def zoom_in(self) -> None:
        self._change_zoom(1.25)

    def zoom_out(self) -> None:
        self._change_zoom(0.8)

    def fit_map(self) -> None:
        # The scrollable scene can extend beyond the background to make every
        # valid signed placement reachable.  Fitting remains intentionally
        # anchored to the retail map image, not distant overlay outliers.
        rect = self._fit_rect if not self._fit_rect.isEmpty() else self.sceneRect()
        if rect.isEmpty():
            return
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        self.zoomChanged.emit(self.transform().m11())

    def set_fit_rect(self, rect: QRectF) -> None:
        """Set the retail-background rectangle used by the Fit control."""
        self._fit_rect = QRectF(rect)

    def _change_zoom(self, factor: float) -> None:
        current = self.transform().m11()
        target = current * factor
        if not 0.125 <= target <= 16:
            return
        self.scale(factor, factor)
        self.zoomChanged.emit(self.transform().m11())

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
        scene_point = self.mapToScene(event.position().toPoint())
        self.cursorMoved.emit(round(scene_point.x()), round(scene_point.y()))
        if self._panning and self._pan_position is not None:
            delta = event.position() - self._pan_position
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - round(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - round(delta.y()))
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

    def keyPressEvent(self, event) -> None:
        nudges = {
            Qt.Key.Key_Left: (-1, 0),
            Qt.Key.Key_Right: (1, 0),
            Qt.Key.Key_Up: (0, -1),
            Qt.Key.Key_Down: (0, 1),
        }
        direction = nudges.get(event.key())
        if direction is not None:
            self.nudgeRequested.emit(*direction)
            event.accept()
            return
        super().keyPressEvent(event)


class PlacementMoveCommand(QUndoCommand):
    """One committed map drag, stored as a semantic project operation."""

    def __init__(
        self,
        tab: "MapWorkspaceTab",
        identity: str,
        before: tuple[int, int],
        after: tuple[int, int],
    ) -> None:
        map_id = identity.split("/", 1)[0]
        super().__init__(
            f"Moved placement on {map_id}: X {before[0]} → {after[0]}, "
            f"Y {before[1]} → {after[1]}"
        )
        self._tab = tab
        self._identity = identity
        self._before = before
        self._after = after
        # The UI validates and persists before it pushes this command.  Qt calls
        # redo() during push(), so that first redo must not write a second time.
        self._first_redo = True

    def redo(self) -> None:
        if self._first_redo:
            self._first_redo = False
            return
        if not self._tab._apply_command_position(self._identity, self._after):
            self._tab._discard_failed_history()

    def undo(self) -> None:
        if not self._tab._apply_command_position(self._identity, self._before):
            self._tab._discard_failed_history()


class MapWorkspaceTab(QWidget):
    """Visual map workspace, thin over the SDK's renderer and scene facade."""

    projectChanged = Signal()
    openSceneRequested = Signal(str, str)
    buildRunRequested = Signal()

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session
        self._render_cache: dict[str, map_render.MapRenderResult] = {}
        self._pixmap_cache = {}
        self._current_render: map_render.MapRenderResult | None = None
        self._current_map: str | None = None
        self._markers: dict[str, PlacementMarker] = {}
        self._selected_identity: str | None = None
        self._background_rect = QRectF()
        self._history_failed = False

        self._scene = QGraphicsScene(self)
        self._canvas = MapCanvasView(self._scene)
        self._canvas.cursorMoved.connect(self._on_cursor_moved)
        self._canvas.nudgeRequested.connect(self._nudge_selected)
        self._canvas.zoomChanged.connect(self._on_zoom_changed)
        self._scene.selectionChanged.connect(self._on_scene_selection_changed)

        self._maps = QListWidget()
        self._maps.currentItemChanged.connect(self._on_map_changed)
        self._map_support = QLabel("Open a supported ROM to view maps.")
        self._map_support.setWordWrap(True)
        maps_box = QGroupBox("Maps")
        maps_layout = QVBoxLayout(maps_box)
        maps_layout.addWidget(self._maps, 1)
        maps_layout.addWidget(self._map_support)

        self._layers = QComboBox()
        self._layers.currentIndexChanged.connect(self._on_layer_changed)
        self._zoom_out = QPushButton("−")
        self._zoom_out.setToolTip("Zoom out")
        self._zoom_out.clicked.connect(self._canvas.zoom_out)
        self._zoom_in = QPushButton("+")
        self._zoom_in.setToolTip("Zoom in")
        self._zoom_in.clicked.connect(self._canvas.zoom_in)
        self._fit = QPushButton("Fit")
        self._fit.clicked.connect(self._canvas.fit_map)
        self._add = QPushButton("Add Object")
        self._add.setToolTip("Clone the selected placement into the project")
        self._add.clicked.connect(self._on_add_object)
        self._build_run = QPushButton("Build & Run")
        self._build_run.clicked.connect(self.buildRunRequested)
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("View"))
        toolbar.addWidget(self._layers)
        toolbar.addStretch(1)
        toolbar.addWidget(self._zoom_out)
        toolbar.addWidget(self._zoom_in)
        toolbar.addWidget(self._fit)
        toolbar.addWidget(self._add)
        toolbar.addWidget(self._build_run)
        canvas_box = QGroupBox("Retail Map")
        canvas_layout = QVBoxLayout(canvas_box)
        canvas_layout.addLayout(toolbar)
        canvas_layout.addWidget(self._canvas, 1)

        self._identity = QLabel("No placement selected")
        self._identity.setWordWrap(True)
        self._position = QLabel("—")
        self._entity = QLabel("Unknown")
        self._behavior = QLabel("Unknown")
        self._script = QLabel("Unknown")
        self._dialogue = QLabel("No proven dialogue relationship")
        self._references = QLabel("—")
        for label in (
            self._entity,
            self._behavior,
            self._script,
            self._dialogue,
            self._references,
        ):
            label.setWordWrap(True)
        self._open_scene = QPushButton("Open detailed editor")
        self._open_scene.clicked.connect(self._open_detailed_editor)
        self._open_scene.setEnabled(False)
        inspector_form = QFormLayout()
        inspector_form.addRow("Identity", self._identity)
        inspector_form.addRow("Position", self._position)
        inspector_form.addRow("Entity", self._entity)
        inspector_form.addRow("Behavior", self._behavior)
        inspector_form.addRow("Script", self._script)
        inspector_form.addRow("Text / dialogue", self._dialogue)
        inspector_form.addRow("References", self._references)
        inspector_form.addRow(self._open_scene)
        inspector_box = QGroupBox("Selected Object")
        inspector_box.setLayout(inspector_form)

        center_splitter = QSplitter(Qt.Orientation.Horizontal)
        center_splitter.addWidget(canvas_box)
        center_splitter.addWidget(inspector_box)
        center_splitter.setStretchFactor(0, 1)
        center_splitter.setSizes([900, 310])
        workspace = QSplitter(Qt.Orientation.Horizontal)
        workspace.addWidget(maps_box)
        workspace.addWidget(center_splitter)
        workspace.setStretchFactor(1, 1)
        workspace.setSizes([240, 1120])

        self._status = QLabel()
        layout = QVBoxLayout(self)
        layout.addWidget(workspace, 1)
        layout.addWidget(self._status)

        self._undo_stack = QUndoStack(self)
        self._undo_action = self._undo_stack.createUndoAction(self, "Undo")
        self._undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self._redo_action = self._undo_stack.createRedoAction(self, "Redo")
        self._redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self._undo_button = QPushButton("Undo")
        self._redo_button = QPushButton("Redo")
        self._undo_button.clicked.connect(self._undo_action.trigger)
        self._redo_button.clicked.connect(self._redo_action.trigger)
        self._undo_stack.canUndoChanged.connect(lambda _available: self._sync_undo_controls())
        self._undo_stack.canRedoChanged.connect(lambda _available: self._sync_undo_controls())
        toolbar.insertWidget(7, self._undo_button)
        toolbar.insertWidget(8, self._redo_button)
        self.addAction(self._undo_action)
        self.addAction(self._redo_action)
        self._sync_undo_controls()

        self._populate_maps()

    # -- session and render state -------------------------------------------

    def on_session_changed(self) -> None:
        """Reload semantic map choices after a ROM/project session transition."""
        self._render_cache.clear()
        self._pixmap_cache.clear()
        self._history_failed = False
        self._undo_stack.clear()
        self._populate_maps()

    def _populate_maps(self) -> None:
        self._maps.blockSignals(True)
        previous = self._current_map or self._session.selected_map
        self._maps.clear()
        if self._session.maps is None or self._session.rom_image is None:
            self._maps.blockSignals(False)
            self._show_placeholder("Open a supported ROM to view the map workspace.")
            return
        entries = scene_sdk.list_maps(self._session.maps)
        # Present the richest semantic authoring contexts first without embedding
        # map IDs or renderer knowledge in the widget.
        entries.sort(key=lambda item: (item["support"] != scene_sdk.MapSupport.EDITABLE.value, item["identity"]))
        selected_row = 0
        for row, entry in enumerate(entries):
            item = QListWidgetItem(
                f"{entry['identity']}  ·  {entry['support']}\n{entry['placement_count']} placements"
            )
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self._maps.addItem(item)
            if entry["identity"] == previous and (
                self._current_map is not None
                or entry["support"] == scene_sdk.MapSupport.EDITABLE.value
            ):
                selected_row = row
        self._maps.blockSignals(False)
        if not entries:
            self._show_placeholder("The open ROM has no readable map entries.")
            return
        self._maps.setCurrentRow(selected_row)

    def _on_map_changed(self, item: QListWidgetItem | None, _previous=None) -> None:
        entry = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if entry is None:
            self._show_placeholder("Select a map to view it.")
            return
        map_id = entry["identity"]
        self._session.selected_map = map_id
        self._map_support.setText(f"{entry['support']}: {entry['support_reason']}")
        self._load_map(map_id)

    def _load_map(self, map_id: str) -> None:
        if self._session.rom_image is None or self._session.maps is None:
            self._show_placeholder("Open a supported ROM to view the map workspace.")
            return
        try:
            result = self._render_cache.get(map_id)
            if result is None:
                self._status.setText(f"Rendering {map_id} from the verified base ROM…")
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                QApplication.processEvents()
                try:
                    result = map_render.render_map(self._session.rom_image, map_id)
                finally:
                    QApplication.restoreOverrideCursor()
                self._render_cache[map_id] = result
        except map_render.MapRenderError as exc:
            self._show_placeholder(str(exc))
            QMessageBox.warning(self, "Map unavailable", str(exc))
            return
        self._current_map = map_id
        self._current_render = result
        self._layers.blockSignals(True)
        self._layers.clear()
        self._layers.addItem("Retail composite", None)
        for layer in sorted(result.layers, key=lambda item: item.bg):
            self._layers.addItem(f"BG{layer.bg}", layer.bg)
        self._layers.blockSignals(False)
        self._show_layer(None)
        # A ROM commonly opens while this tab is still hidden.  At that moment
        # QGraphicsView has not received its final splitter geometry, so fitting
        # immediately computes against a tiny provisional viewport and leaves
        # the map visually stranded in a large canvas.  Queue the fit after the
        # current layout pass; pan/zoom still only change the view transform.
        QTimer.singleShot(0, self._canvas.fit_map)
        self._update_controls()
        self._status.setText(f"{map_id} rendered from the verified base ROM")

    def _on_layer_changed(self, _index: int) -> None:
        self._show_layer(self._layers.currentData())

    def _show_layer(self, layer_bg: int | None) -> None:
        result = self._current_render
        if result is None:
            return
        if layer_bg is None:
            pixels, width, height, key = result.composite, result.width, result.height, "composite"
        else:
            layer = next((item for item in result.layers if item.bg == layer_bg), None)
            if layer is None:
                return
            pixels, width, height, key = layer.pixels, layer.width, layer.height, f"bg{layer.bg}"
        cache_key = (result.semantic_map_id, key)
        pixmap = self._pixmap_cache.get(cache_key)
        if pixmap is None:
            pixmap = indexed_pixmap(pixels, width, height, result.palette)
            self._pixmap_cache[cache_key] = pixmap
        selected = self._selected_identity
        self._rebuild_scene(pixmap, width, height)
        self._selected_identity = selected
        self._populate_markers()

    def _rebuild_scene(self, pixmap, width: int, height: int) -> None:
        self._scene.clear()
        background = QGraphicsPixmapItem(pixmap)
        background.setTransformationMode(Qt.TransformationMode.FastTransformation)
        background.setZValue(0)
        self._scene.addItem(background)
        self._background_rect = QRectF(0, 0, width, height)
        self._canvas.set_fit_rect(self._background_rect)
        self._scene.setSceneRect(self._background_rect)
        self._markers.clear()

    def _clear_markers(self) -> None:
        """Remove overlays only, retaining the cached retail pixmap item."""
        previous_block = self._scene.blockSignals(True)
        try:
            for marker in self._markers.values():
                if marker.scene() is self._scene:
                    self._scene.removeItem(marker)
            self._markers.clear()
        finally:
            self._scene.blockSignals(previous_block)

    def _update_scene_bounds(self) -> None:
        """Make all exact placement anchors scrollable without changing Fit."""
        rect = QRectF(self._background_rect)
        for marker in self._markers.values():
            rect = rect.united(marker.sceneBoundingRect())
        # Keep a small pan margin around a marker located outside retail art.
        self._scene.setSceneRect(rect.adjusted(-16, -16, 16, 16))

    def _populate_markers(self) -> None:
        if self._current_map is None or self._session.maps is None:
            return
        selected = self._selected_identity
        try:
            placements = scene_sdk.scene_placements(
                self._session.maps, self._current_map, self._session.project_dir
            )
        except (ProjectError, OSError) as exc:
            self._show_placeholder(f"Cannot load this project's placement overlays: {exc}")
            QMessageBox.critical(self, "Placement overlays", str(exc))
            return
        self._clear_markers()
        for placement in placements:
            marker = PlacementMarker(
                placement,
                movable=self._session.project_dir is not None,
                drag_completed=self._on_marker_drag,
            )
            self._markers[placement["identity"]] = marker
            self._scene.addItem(marker)
        self._update_scene_bounds()
        self._selected_identity = None
        if selected in self._markers:
            self._select_marker(selected)
        else:
            self._clear_inspector()

    def _show_placeholder(self, message: str) -> None:
        self._current_render = None
        self._current_map = None
        self._markers.clear()
        self._scene.clear()
        text = QGraphicsSimpleTextItem(message)
        text.setBrush(QColor("#F5F7FA"))
        self._scene.addItem(text)
        self._scene.setSceneRect(0, 0, 640, 360)
        self._map_support.setText(message)
        self._status.setText(message)
        self._clear_inspector()
        self._update_controls()

    # -- selection and inspector -------------------------------------------

    def _on_scene_selection_changed(self) -> None:
        selected = [item for item in self._scene.selectedItems() if isinstance(item, PlacementMarker)]
        if not selected:
            self._clear_inspector()
            return
        self._show_selected(selected[-1])

    def _select_marker(self, identity: str) -> None:
        marker = self._markers.get(identity)
        if marker is None:
            return
        self._scene.clearSelection()
        marker.setSelected(True)
        self._canvas.centerOn(marker)

    def _show_selected(self, marker: PlacementMarker) -> None:
        self._selected_identity = marker.placement["identity"]
        placement = marker.placement
        self._identity.setText(placement["identity"])
        self._position.setText(f"X {placement['position_x']}   Y {placement['position_y']}")
        try:
            relationships = scene_sdk.placement_relationships(
                self._session.maps, placement["identity"], self._session.project_dir
            )
        except (ProjectError, OSError) as exc:
            self._status.setText(str(exc))
            self._clear_inspector()
            return
        self._entity.setText(relationships["entity"] or relationships["entity_type"] or "Unknown")
        self._behavior.setText(relationships["behavior"] or "No proven behavior")
        self._script.setText(relationships["script"] or "No proven script")
        self._dialogue.setText(relationships["dialogue"] or "No proven dialogue relationship")
        references = relationships["used_by"]
        # One descriptor can serve hundreds of placements.  Rendering every
        # semantic ID here buries the selected object's primary fields and the
        # contextual action; the specialized editor remains the drill-down for
        # the actual relationship list.
        self._references.setText(
            f"{len(references)} known placement reference(s)"
            if references else "No known placement references"
        )
        self._open_scene.setEnabled(True)
        self._update_controls()

    def _clear_inspector(self) -> None:
        self._selected_identity = None
        self._identity.setText("No placement selected")
        self._position.setText("—")
        self._entity.setText("Unknown")
        self._behavior.setText("Unknown")
        self._script.setText("Unknown")
        self._dialogue.setText("No proven dialogue relationship")
        self._references.setText("—")
        self._open_scene.setEnabled(False)
        self._update_controls()

    def _open_detailed_editor(self) -> None:
        if self._current_map is not None and self._selected_identity is not None:
            self.openSceneRequested.emit(self._current_map, self._selected_identity)

    # -- direct project mutation / Undo -------------------------------------

    def _on_marker_drag(
        self, identity: str, before: tuple[int, int], after: tuple[int, int]
    ) -> bool:
        if before == after:
            return True
        if not self._persist_position(identity, after):
            return False
        self._undo_stack.push(PlacementMoveCommand(self, identity, before, after))
        return True

    def _nudge_selected(self, dx: int, dy: int) -> None:
        marker = self._markers.get(self._selected_identity or "")
        if marker is None:
            return
        before = (marker.placement["position_x"], marker.placement["position_y"])
        self._on_marker_drag(marker.placement["identity"], before, (before[0] + dx, before[1] + dy))

    def _apply_command_position(self, identity: str, position: tuple[int, int]) -> bool:
        # First application was validated before stack.push().  Undo/redo takes
        # the same facade path and catches the complete project-error family.
        return self._persist_position(identity, position)

    def _discard_failed_history(self) -> None:
        """Fail closed if an Undo/Redo write cannot be persisted.

        Qt advances its command index after an ``undo``/``redo`` callback even
        when an external write fails.  Disable history immediately and clear it
        on the next event turn, once Qt has returned from that callback, so no
        stale command can claim a project state that was never saved.
        """
        if self._history_failed:
            return
        self._history_failed = True
        self._sync_undo_controls()
        self._status.setText("Undo/redo history cleared because the project position could not be saved.")
        QTimer.singleShot(0, self._clear_failed_history)

    def _clear_failed_history(self) -> None:
        self._undo_stack.clear()
        self._history_failed = False
        self._sync_undo_controls()

    def _persist_position(self, identity: str, position: tuple[int, int]) -> bool:
        if self._session.project_dir is None or self._session.maps is None:
            QMessageBox.information(self, "Move placement", "Open a project before editing placements.")
            return False
        try:
            changed = scene_sdk.set_placement_map_position(
                self._session.project_dir, self._session.maps, identity, position
            )
        except (ProjectError, OSError) as exc:
            QMessageBox.critical(self, "Move placement", str(exc))
            return False
        if not changed:
            return True
        self._session.scene_mutated()
        self.projectChanged.emit()
        self._populate_markers()
        self._select_marker(identity)
        self._status.setText(f"Moved {identity} to X {position[0]}, Y {position[1]}")
        return True

    def _on_add_object(self) -> None:
        marker = self._markers.get(self._selected_identity or "")
        if marker is None:
            QMessageBox.information(self, "Add Object", "Select a placement to use as the object source.")
            return
        if self._session.project_dir is None or self._current_map is None:
            QMessageBox.information(self, "Add Object", "Open a project before authoring an object.")
            return
        try:
            relationships = scene_sdk.placement_relationships(
                self._session.maps, marker.placement["identity"], self._session.project_dir
            )
        except (ProjectError, OSError) as exc:
            QMessageBox.critical(self, "Add Object", str(exc))
            return
        source = relationships["clone_from"] or marker.placement["identity"]
        name, accepted = QInputDialog.getText(
            self, "Add Object", "Object name (letters, numbers, _ and -):"
        )
        if not accepted:
            return
        position = (marker.placement["position_x"], marker.placement["position_y"])
        try:
            identity = scene_sdk.add_authored_npc_at(
                self._session.project_dir,
                self._current_map,
                source,
                name,
                position,
                maps=self._session.maps,
            )
        except (ProjectError, OSError) as exc:
            QMessageBox.critical(self, "Add Object", str(exc))
            return
        self._session.scene_mutated()
        self.projectChanged.emit()
        self._populate_markers()
        self._select_marker(identity)
        self._status.setText(f"Added {identity} at X {position[0]}, Y {position[1]}")

    # -- visual status / controls -------------------------------------------

    def _on_cursor_moved(self, x: int, y: int) -> None:
        if self._current_map is not None:
            self._status.setText(
                f"{self._current_map}  ·  X {x}  Y {y}  ·  zoom {self._canvas.transform().m11() * 100:.0f}%"
            )

    def _on_zoom_changed(self, scale: float) -> None:
        if self._current_map is not None:
            self._status.setText(f"{self._current_map}  ·  zoom {scale * 100:.0f}%")

    def _update_controls(self) -> None:
        renderable = self._current_render is not None
        editable = renderable and self._session.project_dir is not None
        self._layers.setEnabled(renderable)
        self._zoom_in.setEnabled(renderable)
        self._zoom_out.setEnabled(renderable)
        self._fit.setEnabled(renderable)
        self._add.setEnabled(editable and self._selected_identity is not None)
        self._build_run.setEnabled(self._session.project_dir is not None)
        self._sync_undo_controls()

    def _sync_undo_controls(self) -> None:
        """Keep both visual controls and shortcuts honest about history state."""
        # QUndoStack emits its final availability signals while QObject teardown
        # is deleting children.  At that point there is no live control state to
        # update; returning avoids calling a deleted wrapped C++ object.
        try:
            can_undo = self._undo_stack.canUndo()
            can_redo = self._undo_stack.canRedo()
        except RuntimeError:
            return
        ready = not self._history_failed
        self._undo_button.setEnabled(ready and can_undo)
        self._redo_button.setEnabled(ready and can_redo)
        self._undo_action.setEnabled(ready and can_undo)
        self._redo_action.setEnabled(ready and can_redo)
