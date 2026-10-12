"""WORKBENCH-006 visual map-authoring workspace.
MAP-WARP-CANVAS-001 - its connection trigger regions.

The Map tab is a thin presentation client over ``map_render``, ``scene`` and
``map_transitions``. It renders the SDK's ROM-only indexed map output once,
adapts that result to a Qt pixmap, and overlays semantic placement markers at the
coordinate API's confirmed logical map pixels. It contains no decompression,
screen-entry, palette, pointer, address, or position-bit arithmetic.

**The connection overlay (MAP-WARP-CANVAS-001).** The same canvas draws every
connection of the displayed map as its **trigger region** - the record's two
ordered intervals, the first horizontal and the second vertical in the engine's
own map pixels, which is the measured reading and the same pixel space the
rendered artwork and the placement markers already use. So the rectangle is one
scene item at those coordinates and the view's single zoom/scroll transform
carries it exactly as it carries everything else; no widget here re-derives a
coordinate. The region shown is the one a build would apply: the project's
authored region where it has one (that is why the canvas reads the project's
transition documents), the record's own otherwise.

Clicking a region drives the **shipped** Warps editor - the Maps editor switches
to that mode and selects the connection's row - and dragging one moves the region
through the same authority that editor's Apply uses
(``map_transitions.set_transition_edits``), in one ``ByteChange``, as one undo
entry. Nothing here composes a record, writes a document, computes an offset or
masks a byte, and nothing here states an editability rule of its own: whether a
region may be moved is answered by the Warps surface (``region_edit_refusal``),
whose refusal is the one shown, and a canvas with no such surface wired refuses
every drag rather than inventing a rule.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QPainter, QPen, QUndoCommand, QUndoStack
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .. import map_render, map_transitions as transition_sdk, scene as scene_sdk
from ..formats.map_entry import MapEntryProfileError
from ..formats.map_graphics import MapGraphicsError
from ..formats.map_transitions import MapTransitionError, TransitionRegion
from ..project import ProjectError
from . import theme
from .graphics_tab import indexed_pixmap
from .session import Session
from .widgets import PanelHeader, ToolStrip

#: Every failure family the transition authority and the project underneath it can
#: raise on a gesture. `MapTransitionsError` is the authority's parent
#: (`TransitionFieldError`, `UnknownTransitionError`, `TransitionProfileError`),
#: `MapTransitionError` is the codec's, `MapEntryProfileError` and
#: `MapGraphicsError` are the map-table and map-graphics families the corpus route
#: goes through, and `ProjectError`/`OSError` are the project read and write. None
#: shares a parent with the others, so each is named - the WORKBENCH-001 rule.
_TRANSITION_ERRORS = (
    transition_sdk.MapTransitionsError,
    MapTransitionError,
    MapEntryProfileError,
    MapGraphicsError,
    ProjectError,
    OSError,
)

#: What reading the *session's* image or project can add on top of that. A profile
#: object that is not a `RomProfile` surfaces as `AttributeError`/`TypeError` rather
#: than as a refusal, and at a session boundary or a repaint that is a read-only
#: state like any other ("this image's connections cannot be read") rather than a
#: traceback inside a widget. The gesture slots keep the narrower tuple above, so a
#: programmer error there is still loud - the split `warp_tab` makes between
#: `_WARP_SESSION_ERRORS` and `_WARP_ERRORS`.
_TRANSITION_SESSION_ERRORS = _TRANSITION_ERRORS + (AttributeError, TypeError)

#: Why a transition's trigger region cannot be moved from this canvas at all: no
#: authoring surface is wired to answer what may be edited. Fail closed rather than
#: invent a rule here - the Maps editor always wires the Warps surface.
_NO_TRANSITION_GUARD = (
    "This canvas is not connected to the Maps editor's Warps surface, so no "
    "connection can be authorised for editing here."
)


def _region_words(region: TransitionRegion) -> str:
    """One region in the codec's own positional words, for a status line."""
    return (
        f"first {region.first[0]}-{region.first[1]}, "
        f"second {region.second[0]}-{region.second[1]}"
    )


def _translated_region(
    region: TransitionRegion, dx: int, dy: int
) -> TransitionRegion:
    """The region one canvas drag produced, in the codec's own domain.

    The gesture is a translation of the region the project currently applies: both
    endpoints of the horizontal interval move by ``dx`` and both of the vertical
    one by ``dy``, so a move preserves both widths and cannot make an interval
    unordered or degenerate. A translated endpoint outside the ``u16`` domain is
    refused by :class:`TransitionRegion` itself, in its own words; the canvas adds
    no bounds rule of its own.
    """
    (first_low, first_high), (second_low, second_high) = region.first, region.second
    return TransitionRegion(
        first=(first_low + dx, first_high + dx),
        second=(second_low + dy, second_high + dy),
    )


@dataclass(frozen=True, slots=True)
class TransitionOverlayState:
    """One connection drawn on the canvas, and whether its region may be moved.

    ``identity`` is an SDK transition identity - `TransitionIdentity` for a record
    the image holds, `CreatedTransitionIdentity` for one the project creates - and
    ``region`` is the region a build would apply: the project's authored one where
    it has one, the record's own otherwise. ``refusal`` is the authoring surface's
    own answer about editing this connection, or None; it is never a rule stated
    here.
    """

    identity: object
    region: TransitionRegion
    refusal: str | None
    #: Whether the region shown is the project's rather than the base image's.
    authored: bool = False


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
        self._label.setBrush(theme.color("text_primary"))
        self._label.setPos(10, -18)
        self._label.setVisible(False)

    def boundingRect(self) -> QRectF:
        return QRectF(-10, -10, 20, 20)

    def paint(self, painter: QPainter, _option, _widget=None) -> None:
        painter.save()
        selected = self.isSelected()
        project_authored = self.placement.get("provenance") == "Project"
        # A light halo plus a dark edge remains visible over any palette: the map
        # is the most saturated object on screen, so a marker is separated from it
        # by value rather than by adding another bright hue.
        painter.setPen(QPen(theme.color("marker_halo"), 4 if selected else 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(-7, -7, 14, 14))
        painter.setPen(QPen(theme.color("marker_outline"), 2))
        painter.setBrush(
            theme.color("marker_authored" if project_authored else "marker_retail")
        )
        if project_authored:
            painter.drawPolygon((QPointF(0, -6), QPointF(6, 0), QPointF(0, 6), QPointF(-6, 0)))
        else:
            painter.drawEllipse(QRectF(-5, -5, 10, 10))
        if selected:
            # Selection is a *shape* change too - four ticks around the marker - so
            # it survives without hue.
            painter.setPen(QPen(theme.color("marker_halo"), 2))
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


class TransitionOverlay(QGraphicsRectItem):
    """One connection's trigger region, drawn where the engine reads it.

    The item IS the region: its rectangle is the region's own two intervals on the
    item's axes and its position is the region's low corner, both in the map pixels
    the rendered artwork and the placement markers already live in. Nothing is
    recomputed per paint, and the view's one zoom/scroll transform places it exactly
    as it places the map underneath.

    A press that ends where it started is a **selection** and a press that ends
    elsewhere is a **move**, reported once on release so one drag is one gesture -
    the same shape `PlacementMarker` gives a placement. A region the authoring
    surface will refuse is drawn dashed and still draggable: the gesture has to be
    possible for its refusal to be readable, which is what keeps it from looking
    like a dead click.
    """

    def __init__(
        self,
        state: TransitionOverlayState,
        *,
        clicked: Callable[[object], None],
        drag_completed: Callable[[TransitionOverlayState, tuple[int, int], tuple[int, int]], bool],
    ) -> None:
        super().__init__()
        self.state = state
        self._clicked = clicked
        self._drag_completed = drag_completed
        self._drag_origin: QPointF | None = None
        self._selected = False
        first_low, first_high = state.region.first
        second_low, second_high = state.region.second
        self.setRect(QRectF(0, 0, first_high - first_low, second_high - second_low))
        self.setPos(first_low, second_low)
        # Above the artwork (0) and below the placement markers (20): a region is a
        # large wash, and a marker sitting on a door must stay on top of it.
        self.setZValue(10)
        self.setToolTip(
            f"{state.identity}\n"
            f"Trigger region: {_region_words(state.region)}\n"
            + (state.refusal if state.refusal is not None else
               "Drag to move the trigger region on the map")
        )
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        # The region's own identity appears only while it is selected, so a map
        # dense with doors stays readable - the placement marker's rule.
        self._label = QGraphicsSimpleTextItem(str(state.identity), self)
        self._label.setBrush(theme.color("text_primary"))
        self._label.setPos(2, 2)
        self._label.setVisible(False)

    def boundingRect(self) -> QRectF:
        # The painted halo sits outside the region's own rectangle.
        return self.rect().adjusted(-3, -3, 3, 3)

    def set_selected(self, selected: bool) -> None:
        """Show (or stop showing) that this is the connection being edited."""
        if selected == self._selected:
            return
        self._selected = selected
        self._label.setVisible(selected)
        self.update()

    def paint(self, painter: QPainter, _option, _widget=None) -> None:
        painter.save()
        rect = self.rect()
        provenance = theme.color(
            "region_authored" if self.state.authored else "region_retail"
        )
        # A white halo plus a dark edge, so the region reads over any palette: the
        # map is the most saturated object on screen, so the overlay is separated
        # from it by value as well as by hue.
        painter.setPen(QPen(theme.color("marker_halo"), 5 if self._selected else 4))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(rect)
        # A light wash, not a fill: the terrain under a door is what tells the
        # author where that door is.
        wash = QColor(provenance)
        wash.setAlpha(84 if self._selected else 56)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(wash)
        painter.drawRect(rect)
        pen = QPen(theme.color("selection_edge") if self._selected else provenance, 3 if self._selected else 2)
        if self.state.refusal is not None:
            # Dashed: this connection is one the authoring surface will refuse to
            # move, and the shape says so before the gesture is made.
            pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(rect)
        if self._selected:
            # A chip behind the identity label, drawn by the parent so the child
            # text lands on it: the one label on a dense map has to stay readable
            # over foliage and over sand, not only over sky.
            chip = QColor(theme.color("marker_halo"))
            chip.setAlpha(215)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(chip)
            painter.drawRoundedRect(
                self._label.boundingRect().translated(self._label.pos()).adjusted(
                    -2, -1, 2, 1
                ),
                2,
                2,
            )
        painter.restore()

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
            # A click: the connection is selected rather than moved. Nothing is
            # written and no history entry is created.
            self._clicked(self.state.identity)
            return
        if not self._drag_completed(self.state, before, after):
            # The authority refused the move: the region goes back where it was.
            self.setPos(origin)


class MapCanvasView(QGraphicsView):
    """Crisp map viewport with editor-standard middle pan and wheel zoom."""

    cursorMoved = Signal(int, int)
    nudgeRequested = Signal(int, int)
    zoomChanged = Signal(float)
    #: A left press that landed on no overlay at all. The scene clears its own
    #: selection for such a press, but it emits nothing when there was none to
    #: clear - and "click empty canvas to deselect" has to work in that case too.
    backgroundPressed = Signal()

    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__(scene)
        self._panning = False
        self._pan_position: QPointF | None = None
        self._fit_rect = QRectF()
        #: True while the view is in its fitted state; a manual zoom clears it, so
        #: a resize refits a fitted map and never overrides a chosen zoom.
        self._fitted = False
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setBackgroundBrush(theme.color("canvas"))

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
        self._fitted = True
        self.zoomChanged.emit(self.transform().m11())

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """Keep a fitted map fitted while the window or a splitter is resized.

        A fit computed before the viewport reached its final size is stale the
        moment anything resizes, and the map then sits in a corner at a zoom
        nobody asked for. Refitting while the view is in its fitted state - and
        only then, so a manual zoom is never overridden - is what Porymap and
        Tiled both do.
        """
        super().resizeEvent(event)
        if self._fitted:
            self.fit_map()

    def set_fit_rect(self, rect: QRectF) -> None:
        """Set the retail-background rectangle used by the Fit control."""
        self._fit_rect = QRectF(rect)

    def _change_zoom(self, factor: float) -> None:
        current = self.transform().m11()
        target = current * factor
        if not 0.125 <= target <= 16:
            return
        self.scale(factor, factor)
        # A manual zoom ends the fitted state's claim on the view.
        self._fitted = False
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
        if event.button() == Qt.MouseButton.LeftButton and not self._hits_an_overlay(
            event.position().toPoint()
        ):
            self.backgroundPressed.emit()
        super().mousePressEvent(event)

    def _hits_an_overlay(self, point) -> bool:
        """Whether a left press at ``point`` lands on a selectable canvas object."""
        return any(
            isinstance(item, (PlacementMarker, TransitionOverlay))
            for item in self.items(point)
        )

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


class TransitionRegionCommand(QUndoCommand):
    """One committed region drag, stored as a semantic project operation.

    The whole gesture is one entry, and both endpoints are resolved before it is
    pushed: the widget validates and persists first, so `redo()`'s first call -
    which Qt makes during `push()` - must not write a second time, exactly as
    `PlacementMoveCommand` records it.
    """

    def __init__(
        self,
        tab: "MapWorkspaceTab",
        identity,
        before: TransitionRegion,
        after: TransitionRegion,
    ) -> None:
        super().__init__(
            f"Moved the trigger region of {identity}: "
            f"{_region_words(before)} \u2192 {_region_words(after)}"
        )
        self._tab = tab
        self._identity = identity
        self._before = before
        self._after = after
        self._first_redo = True

    def redo(self) -> None:
        if self._first_redo:
            self._first_redo = False
            return
        if not self._tab._apply_command_region(self._identity, self._after):
            self._tab._discard_failed_history()

    def undo(self) -> None:
        if not self._tab._apply_command_region(self._identity, self._before):
            self._tab._discard_failed_history()


class MapWorkspaceTab(QWidget):
    """Visual map workspace, thin over the SDK's renderer and scene facade."""

    projectChanged = Signal()
    openSceneRequested = Signal(str, str)
    buildRunRequested = Signal()
    #: A connection was selected on the canvas, as an SDK transition identity. The
    #: Maps editor answers it by showing the Warps mode on that connection's row.
    transitionSelected = Signal(object)
    #: The compact one-line status this editor maintains, republished for the shell.
    statusChanged = Signal(str)

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
        #: Every connection of the displayed map, drawn as its trigger region, by
        #: identity key.
        self._transition_overlays: dict[str, TransitionOverlay] = {}
        #: The whole-image connection corpus, resolved once per session (CQA-07).
        self._transition_corpus: "transition_sdk.MapTransitions | None" = None
        #: Why it could not be resolved, when it could not.
        self._transition_corpus_error: str | None = None
        #: The authoring surface's own answer to "may this connection be edited?".
        #: Installed by the Maps editor; absent means nothing may be edited here.
        self._transition_guard: Callable[[object], str | None] | None = None
        #: The project's authored regions and creations, re-read ONCE per project
        #: revision - never per repaint, per layer change or per overlay.
        self._transition_project_revision: int | None = None
        self._transition_authored_regions: dict = {}
        self._transition_creations: dict = {}
        self._transition_project_error: str | None = None
        #: The map domain's own identity for each `map:NNNN` key, so the corpus can
        #: be asked about the displayed map without parsing its identity here.
        self._map_identities: dict = {}
        #: The connection the Warps editor has selected, mirrored for the canvas.
        self._selected_transition: str | None = None

        self._scene = QGraphicsScene(self)
        self._canvas = MapCanvasView(self._scene)
        self._canvas.cursorMoved.connect(self._on_cursor_moved)
        self._canvas.nudgeRequested.connect(self._nudge_selected)
        self._canvas.zoomChanged.connect(self._on_zoom_changed)
        self._canvas.backgroundPressed.connect(self._on_canvas_background_pressed)
        self._scene.selectionChanged.connect(self._on_scene_selection_changed)

        self._maps = QListWidget()
        self._maps.setUniformItemSizes(True)
        # A list of long labels must not demand the width its longest row would
        # need: it has its own scrollbar, and a pane that insists on full text
        # makes the splitter wider than the window (and the canvas then scrolls).
        self._maps.setMinimumWidth(0)
        self._maps.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._maps.currentItemChanged.connect(self._on_map_changed)
        self._map_support = QLabel("Open a supported ROM to view maps.")
        self._map_support.setWordWrap(True)
        self._map_support.setProperty("dbzRole", "hint")
        self._maps_count = QLabel("")
        self._maps_count.setProperty("dbzRole", "count")
        maps_header = PanelHeader("Placements by map", trailing=self._maps_count)
        # The map's support state is shown ONCE, under the header, where the map
        # itself is. It used to be repeated at the foot of the list as well, which
        # printed the same sentence twice in one pane and wrapped into the row
        # beneath it.
        self._map_support = QLabel("Open a supported ROM to view maps.")
        self._map_support.setWordWrap(True)
        self._map_support.setProperty("dbzRole", "hint")
        maps_box = QWidget()
        maps_layout = QVBoxLayout(maps_box)
        maps_layout.setContentsMargins(0, 0, 0, 0)
        maps_layout.setSpacing(0)
        maps_layout.addWidget(maps_header)
        maps_layout.addWidget(self._map_support)
        maps_layout.addWidget(self._maps, 1)

        self._layers = QComboBox()
        self._layers.setAccessibleName("View layer")
        self._layers.setMinimumWidth(0)
        self._layers.setToolTip(
            "Which graphical layer of the retail map to draw: the composite the "
            "engine builds, or one layer on its own"
        )
        self._layers.currentIndexChanged.connect(self._on_layer_changed)
        self._zoom_out = QPushButton("\u2212")
        self._zoom_out.setToolTip("Zoom out")
        self._zoom_out.setMinimumWidth(30)
        self._zoom_out.clicked.connect(self._canvas.zoom_out)
        self._zoom_in = QPushButton("+")
        self._zoom_in.setToolTip("Zoom in")
        self._zoom_in.setMinimumWidth(30)
        self._zoom_in.clicked.connect(self._canvas.zoom_in)
        self._fit = QPushButton("Fit")
        self._fit.setToolTip("Fit the map to the window")
        self._fit.clicked.connect(self._canvas.fit_map)
        self._add = QPushButton("Add Object")
        self._add.setToolTip("Clone the selected placement into the project")
        self._add.clicked.connect(self._on_add_object)
        # Build & Run is NOT duplicated here. Validate, Build and Run are project
        # actions and the shell's strip owns them; a second, locally-styled button
        # for the same three operations made it look like this editor had its own
        # build system. The `buildRunRequested` signal is kept because it is the
        # command path the shell's actions drive, and it is what a future
        # selection-scoped build would attach to.
        self._build_run = QPushButton("Build & Run")
        self._build_run.setProperty("dbzRole", "primary")
        self._build_run.setToolTip(
            "Validate, build and launch the project (Validate \u2192 Build \u2192 Run)"
        )
        self._build_run.clicked.connect(self.buildRunRequested)
        self._build_run.setVisible(False)
        # One contextual strip directly above the canvas (Porymap's row 0), so the
        # canvas is the only undecorated region on this tab.
        toolbar_widget = ToolStrip()
        toolbar_widget.add_label("View")
        toolbar_widget.add(self._layers)
        toolbar_widget.add_stretch()
        toolbar_widget.add(self._zoom_out)
        toolbar_widget.add(self._zoom_in)
        toolbar_widget.add(self._fit)
        toolbar_widget.add_separator()
        toolbar_widget.add(self._add)
        toolbar_widget.add(self._build_run)
        self._tool_strip = toolbar_widget
        # The strip's content must not set the canvas width, so it is given the
        # same ignored width policy the Map Browser's strip uses.
        toolbar_widget.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed
        )
        canvas_box = QFrame()
        canvas_box.setObjectName("dbzRetailMapFrame")
        canvas_layout = QVBoxLayout(canvas_box)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)
        canvas_layout.addWidget(toolbar_widget)
        canvas_layout.addWidget(self._canvas, 1)

        # The placement detail lives in ONE two-column grid, and the whole grid is
        # revealed only when a placement is selected: with nothing selected there is
        # nothing to say, so the pane shows one sentence instead of a column of
        # dashes and "Unknown" scaffolding. That is the same defect the Graphics
        # editor had, and it is fixed the same way.
        self._placement_empty = QLabel(
            "Select a placement on the canvas to inspect it. Its position, entity, "
            "behaviour and text relationship appear here."
        )
        self._placement_empty.setProperty("dbzRole", "hint")
        self._placement_empty.setWordWrap(True)
        self._placement_empty.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self._identity = QLabel("")
        self._identity.setWordWrap(True)
        self._position = QLabel("")
        self._entity = QLabel("")
        self._behavior = QLabel("")
        self._script = QLabel("")
        self._dialogue = QLabel("")
        self._references = QLabel("")
        for label in (
            self._entity,
            self._behavior,
            self._script,
            self._dialogue,
            self._references,
        ):
            label.setWordWrap(True)
            label.setProperty("dbzRole", "hint")
        self._open_scene = QPushButton("Open detailed editor")
        self._open_scene.setToolTip(
            "Open this placement in the Scene editor, where its entity, behavior "
            "and script are authored"
        )
        self._open_scene.clicked.connect(self._open_detailed_editor)
        self._open_scene.setEnabled(False)

        # An explicit two-column grid rather than a form layout, for the same
        # reason as the Graphics inspector: a form stacks a caption and its value on
        # consecutive lines here, which reads as unlabelled values.
        self._detail_rows: list[tuple[QLabel, QLabel]] = []
        self._placement_body = QWidget()
        body = QGridLayout(self._placement_body)
        body.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM
        )
        body.setHorizontalSpacing(theme.SPACE_MD)
        body.setVerticalSpacing(theme.SPACE_XS)
        body.setColumnStretch(1, 1)
        for row, (caption, value) in enumerate(
            (
                ("Identity", self._identity),
                ("Position", self._position),
                ("Entity", self._entity),
                ("Behavior", self._behavior),
                ("Script", self._script),
                ("Text / dialogue", self._dialogue),
                ("References", self._references),
            )
        ):
            label = QLabel(caption)
            label.setProperty("dbzRole", "fieldLabel")
            label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
            )
            body.addWidget(label, row, 0)
            body.addWidget(value, row, 1)
            self._detail_rows.append((label, value))
        body.addWidget(self._open_scene, len(self._detail_rows), 1)
        inspector_box = QWidget()
        inspector_layout = QVBoxLayout(inspector_box)
        inspector_layout.setContentsMargins(0, 0, 0, 0)
        inspector_layout.setSpacing(0)
        self._inspector_header = PanelHeader("Placement")
        inspector_layout.addWidget(self._inspector_header)
        inspector_layout.addWidget(self._placement_empty, 1)
        inspector_layout.addWidget(self._placement_body, 1)
        self._inspector_box = inspector_box
        self._show_placement_detail(False)

        center_splitter = QSplitter(Qt.Orientation.Horizontal)
        center_splitter.addWidget(canvas_box)
        center_splitter.addWidget(inspector_box)
        center_splitter.setStretchFactor(0, 1)
        center_splitter.setCollapsible(0, False)
        center_splitter.setSizes([900, 310])
        self._center_splitter = center_splitter
        workspace = QSplitter(Qt.Orientation.Horizontal)
        workspace.addWidget(maps_box)
        workspace.addWidget(center_splitter)
        workspace.setStretchFactor(0, 0)
        workspace.setStretchFactor(1, 1)
        workspace.setCollapsible(0, True)
        workspace.setCollapsible(1, False)
        workspace.setSizes([240, 1180])
        self._workspace_split = workspace

        self._status = QLabel()
        self._status.setProperty("dbzRole", "status")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(theme.SPACE_XS)
        layout.addWidget(workspace, 1)
        # `_status` is NOT added to this layout: the shell owns the one status bar
        # and copies this editor's line into it. Drawing it here as well is what put
        # a second status strip above the real one.
        self._status.setVisible(False)

        self._undo_stack = QUndoStack(self)
        # Undo/Redo join the one canvas strip rather than a second toolbar. The
        # actions carry no key of their own: CQA-23 leaves Ctrl+Z and Ctrl+Y to
        # the shell's Edit -> Undo/Redo, which route to the ACTIVE mode's history
        # (`MapsEditor.undo_stack`). Binding the standard keys here as well made
        # one key answer to two live actions in this window.
        self._undo_action = self._undo_stack.createUndoAction(self, "Undo")
        self._redo_action = self._undo_stack.createRedoAction(self, "Redo")
        self._undo_button = QPushButton("Undo")
        self._redo_button = QPushButton("Redo")
        self._undo_button.clicked.connect(self._undo_action.trigger)
        self._redo_button.clicked.connect(self._redo_action.trigger)
        self._undo_stack.canUndoChanged.connect(lambda _available: self._sync_undo_controls())
        self._undo_stack.canRedoChanged.connect(lambda _available: self._sync_undo_controls())
        row = toolbar_widget.layout_row()
        row.insertWidget(row.count() - 2, self._undo_button)
        row.insertWidget(row.count() - 2, self._redo_button)
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
        # The connection corpus, the project's authored regions and every identity
        # they are keyed by describe the image and project that were open, so a true
        # session replacement drops them; a project mutation does not.
        self._transition_corpus = None
        self._transition_corpus_error = None
        self._transition_project_revision = None
        self._transition_authored_regions = {}
        self._transition_creations = {}
        self._transition_project_error = None
        self._map_identities = {}
        self._selected_transition = None
        self._populate_maps()

    def on_project_mutated(self) -> None:
        """A project mutation elsewhere: re-read placements, keep the history.

        CQA-05. The placement corpus is project state, so a mutation made in
        another editor - a Scene NPC added, a dialogue applied, a palette
        recolour committed - must become visible here. ``_populate_markers``
        re-reads it and re-selects the placement that was selected, so an
        unrelated write refreshes the overlays without moving the user.

        The undo stack is deliberately NOT cleared. Its commands are semantic
        positions on placements the project still holds, so an unrelated write
        cannot make them wrong. ``on_session_changed`` clears them because there
        the *base* image, and with it the whole map corpus those positions were
        read from, has been replaced - a different event with a different
        consequence, which is exactly why the two are no longer one callback.
        """
        self._populate_markers()
        self._update_controls()

    def _populate_maps(self) -> None:
        self._maps.blockSignals(True)
        previous = self._current_map or self._session.selected_map
        self._maps.clear()
        # The map domain's own identities, keyed by the identity spelling the list
        # and the session already use, so the connection overlay can ask the corpus
        # about the displayed map without parsing a `map:NNNN` string itself.
        self._map_identities = {}
        if self._session.maps is None or self._session.rom_image is None:
            self._maps.blockSignals(False)
            self._maps_count.setText("")
            self._show_placeholder("Open a supported ROM to view the map workspace.")
            return
        self._map_identities = {
            str(entry.identity): entry.identity
            for entry in self._session.maps.entries()
        }
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
        self._maps_count.setText(f"{len(entries)}")
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
                self._set_status(f"Rendering {map_id} from the verified base ROM…")
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                QApplication.processEvents()
                try:
                    result = map_render.render_map(
                        self._session.rom_image, map_id, profile=self._session.profile
                    )
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
        self._set_status(f"{map_id} rendered from the verified base ROM")

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
        # `QGraphicsScene.clear()` destroys every item it owns, so the overlay map
        # must be emptied with it. Holding a wrapper for a deleted C++ item is a
        # use-after-free waiting for the next repaint.
        self._transition_overlays.clear()

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

    def _clear_transition_overlays(self) -> None:
        """Remove the connection overlays only, retaining the retail pixmap item."""
        previous_block = self._scene.blockSignals(True)
        try:
            for overlay in self._transition_overlays.values():
                if overlay.scene() is self._scene:
                    self._scene.removeItem(overlay)
            self._transition_overlays.clear()
        finally:
            self._scene.blockSignals(previous_block)

    def _update_scene_bounds(self) -> None:
        """Make all exact placement anchors and regions scrollable without changing Fit."""
        rect = QRectF(self._background_rect)
        for marker in self._markers.values():
            rect = rect.united(marker.sceneBoundingRect())
        # A trigger region is inside its map's walkable extent, which the rendered
        # artwork need not cover; making it reachable is what lets a door be seen and
        # dragged at the edge of a map. Fit stays anchored to the retail artwork.
        for overlay in self._transition_overlays.values():
            rect = rect.united(overlay.sceneBoundingRect())
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
        self._populate_transitions()
        self._update_scene_bounds()
        self._selected_identity = None
        if selected in self._markers:
            self._select_marker(selected)
        else:
            self._clear_inspector()

    def _set_status(self, text: str) -> None:
        """Set this editor's own status line and republish it for the shell.

        One implementation, one place it is drawn: the shell owns the one status
        label and copies this line into it, so the two can never disagree.
        """
        self._status.setText(text)
        self.statusChanged.emit(text)

    def restate_status(self) -> None:
        """Republish the current line without changing it.

        The Maps editor calls this when this mode becomes visible again, so a
        readout that was last set while a different mode was on screen is not the
        one the user is shown.
        """
        self.statusChanged.emit(self._status.text())

    def _show_placeholder(self, message: str) -> None:
        """Nothing to render: state it on the canvas and publish it once.

        The message is drawn on the canvas itself, where the missing map would be,
        and published to the shell's status bar through `_set_status`. It is
        deliberately NOT also written to `_map_support`: that wrote the same
        sentence into a second body label, so one fact rendered twice on one screen.
        See `tools/qa/status_duplication_probe.py`.
        """
        self._current_render = None
        self._current_map = None
        self._markers.clear()
        self._transition_overlays.clear()
        self._selected_transition = None
        self._scene.clear()
        text = QGraphicsSimpleTextItem(message)
        text.setBrush(theme.color("text_primary"))
        self._scene.addItem(text)
        self._scene.setSceneRect(0, 0, 640, 360)
        self._map_support.setText("")
        self._set_status(message)
        self._clear_inspector()
        self._update_controls()

    # -- the connection overlay (MAP-WARP-CANVAS-001) -----------------------

    def set_transition_guard(self, guard: Callable[[object], str | None] | None) -> None:
        """Install the authoring surface's own answer about editing a connection.

        The Maps editor hands over the Warps surface's `region_edit_refusal`, so the
        canvas refuses exactly what that surface refuses, in its words: the measured
        566/169 split, an unresolved destination, a project that cannot be read, a
        missing project, and a connection root shared with another map. Without it
        NOTHING is editable here, which is the fail-closed default for a canvas with
        no authoring surface behind it.
        """
        self._transition_guard = guard
        self._populate_transitions()

    def selected_transition(self) -> str | None:
        """The connection key the canvas is currently showing as selected."""
        return self._selected_transition

    def show_selected_transition(self, key: str | None) -> None:
        """Indicate the connection the Warps editor has selected, when it is here.

        The Warps editor owns the selection; the canvas only shows it. Called when
        this mode becomes visible again, so a row picked in the connection list
        highlights the region it belongs to instead of leaving the last clicked one
        marked.
        """
        self._selected_transition = key if key in self._transition_overlays else None
        self._refresh_transition_selection()

    def transition_overlays(self) -> dict:
        """The drawn regions, keyed by connection identity, for tests and probes."""
        return {
            key: overlay.state.region
            for key, overlay in self._transition_overlays.items()
        }

    def transition_corpus_error(self) -> str | None:
        """Why this image's connections could not be read, or None."""
        self._transition_corpus_for_session()
        return self._transition_corpus_error

    def _transition_corpus_for_session(self) -> "transition_sdk.MapTransitions | None":
        """The whole image's connection corpus, resolved once per session.

        The canonical corpus is 735 records over 452 maps, so it is resolved ONCE
        here and every overlay is derived from it; a layer change, a zoom, a pan, a
        selection or a repaint reads nothing at all (CQA-07).
        """
        if self._transition_corpus is not None or self._transition_corpus_error is not None:
            return self._transition_corpus
        image = self._session.map_image
        profile = self._session.profile
        if image is None or profile is None:
            self._transition_corpus_error = "Open a game image to read its connections."
            return None
        try:
            self._transition_corpus = transition_sdk.read_map_transitions(image, profile)
        except _TRANSITION_SESSION_ERRORS as exc:
            self._transition_corpus = None
            self._transition_corpus_error = str(exc)
        return self._transition_corpus

    def _read_authored_transitions(self) -> None:
        """The project's authored regions and creations, once per revision.

        One `read_project` supplies both of the project's transition documents, the
        same way the Warps surface reads them, and the results are cached against the
        session's project revision so a repaint or a map switch never re-parses the
        project (CQA-07).
        """
        revision = self._session.project_revision
        if self._transition_project_revision == revision:
            return
        self._transition_project_revision = revision
        self._transition_authored_regions = {}
        self._transition_creations = {}
        self._transition_project_error = None
        project = self._session.project_dir
        if project is None:
            return
        try:
            from ..project import read_project

            document = read_project(project)
            self._transition_authored_regions = {
                identity: edit.region
                for identity, edit in transition_sdk.transition_edits_to_requests(
                    document.transitions
                ).items()
                if edit.region is not None
            }
            self._transition_creations = dict(
                transition_sdk.transition_creations_to_requests(
                    document.transition_creations
                )
            )
        except _TRANSITION_ERRORS as exc:
            # A project this surface cannot read is not permission to draw retail
            # regions as if the project authored nothing.
            self._transition_authored_regions = {}
            self._transition_creations = {}
            self._transition_project_error = str(exc)

    def _current_map_identity(self):
        """The displayed map as the SDK's own `MapIdentity`, or None."""
        if self._current_map is None:
            return None
        return self._map_identities.get(self._current_map)

    def _transition_refusal(self, identity) -> str | None:
        """Why one connection may not be edited here, in the surface's own words."""
        if self._transition_guard is None:
            return _NO_TRANSITION_GUARD
        try:
            return self._transition_guard(identity)
        except _TRANSITION_SESSION_ERRORS as exc:
            return str(exc)

    def _transition_states(self) -> tuple[TransitionOverlayState, ...]:
        """Every connection of the displayed map, as the overlay draws it."""
        corpus = self._transition_corpus_for_session()
        identity = self._current_map_identity()
        if corpus is None or identity is None:
            return ()
        self._read_authored_transitions()
        if self._transition_project_error is not None:
            # The project's own regions could not be read, so no region can be shown
            # as the one a build would apply.
            return ()
        states: list[TransitionOverlayState] = []
        try:
            entries = corpus.for_map(identity)
        except _TRANSITION_ERRORS:
            entries = ()
        for entry in entries:
            region = self._transition_authored_regions.get(entry.identity)
            authored = region is not None
            if region is None:
                region = entry.record.region
            states.append(
                TransitionOverlayState(
                    identity=entry.identity,
                    region=region,
                    refusal=self._transition_refusal(entry.identity),
                    authored=authored,
                )
            )
        for created in sorted(self._transition_creations):
            if created.source != identity:
                continue
            states.append(
                TransitionOverlayState(
                    identity=created,
                    region=self._transition_creations[created].creation.region,
                    refusal=self._transition_refusal(created),
                    authored=True,
                )
            )
        return tuple(states)

    def _populate_transitions(self) -> None:
        """Draw every connection of the displayed map as its trigger region."""
        self._clear_transition_overlays()
        for state in self._transition_states():
            overlay = TransitionOverlay(
                state,
                clicked=self._on_overlay_clicked,
                drag_completed=self._on_overlay_drag,
            )
            self._transition_overlays[state.identity.key] = overlay
            self._scene.addItem(overlay)
        self._refresh_transition_selection()

    def _refresh_transition_selection(self) -> None:
        for key, overlay in self._transition_overlays.items():
            overlay.set_selected(key == self._selected_transition)

    def _on_overlay_clicked(self, identity) -> None:
        """A click on a region selects it and drives the Warps editor to its row.

        The canvas keeps no editor state of its own for this: it states which
        connection is selected and tells the Maps editor, which shows the Warps mode
        and selects the connection's row there. A placement that was selected is
        dropped with its inspector, so exactly one thing on this canvas is selected.
        """
        previous_block = self._scene.blockSignals(True)
        try:
            self._scene.clearSelection()
        finally:
            self._scene.blockSignals(previous_block)
        self._selected_identity = None
        self._clear_inspector()
        self._selected_transition = identity.key
        self._refresh_transition_selection()
        self._set_status(f"{identity}: showing this connection in the Warps editor")
        self.transitionSelected.emit(identity)

    def _on_canvas_background_pressed(self) -> None:
        """A press on empty canvas clears what this canvas had selected."""
        self._selected_transition = None
        self._refresh_transition_selection()

    def _on_overlay_drag(
        self,
        state: TransitionOverlayState,
        before: tuple[int, int],
        after: tuple[int, int],
    ) -> bool:
        """One committed region drag: one authority write, one undo entry.

        Ends where it started, or ends on a region the authority reports the project
        already holds: nothing is written by this gesture, no history entry is created
        and the canvas is repopulated from the project either way. Otherwise the whole
        gesture is resolved - the authority's answer about editing this connection,
        the translated region, and the write itself - BEFORE the command is pushed,
        because Qt calls `redo()` inside `push()` and a refusal must not cross that
        frame.
        """
        if before == after:
            return True
        identity = state.identity
        if not isinstance(identity, transition_sdk.TransitionIdentity):
            self._report_transition_refusal(
                state.refusal if state.refusal is not None else _NO_TRANSITION_GUARD
            )
            return False
        refusal = self._transition_refusal(identity)
        if refusal is not None:
            self._report_transition_refusal(refusal)
            return False
        dx = after[0] - before[0]
        dy = after[1] - before[1]
        try:
            region = _translated_region(state.region, dx, dy)
        except MapTransitionError as exc:
            # The codec's own refusal: an endpoint outside the u16 domain.
            self._report_transition_refusal(str(exc))
            return False
        written = self._write_transition_region(identity, region)
        if written is None:
            # The edit could not be attempted or was refused: it is reported, and it
            # is not a write this canvas may record as undoable.
            return False
        if written:
            self._undo_stack.push(
                TransitionRegionCommand(self, identity, state.region, region)
            )
        return written

    def _apply_command_region(self, identity, region: TransitionRegion) -> bool:
        """Undo/redo's own application of a resolved region.

        The first application was validated before `stack.push()`; undo and redo take
        the same authority path and catch the complete failure families, so nothing
        raises across Qt's undo frame. A re-application the authority reports as
        already current wrote nothing and is still a success: this entry's history
        stands rather than being discarded for having had nothing left to do.
        """
        return self._write_transition_region(identity, region) is not None

    def _write_transition_region(
        self, identity, region: TransitionRegion
    ) -> bool | None:
        """Move one trigger region through the authority, in ONE semantic write.

        `set_transition_edits` is the entry point the Warps editor's Apply uses: it
        re-reads the canonical record, checks that only the fields this request names
        change, and returns the authority's own byte plan for the one record. Nothing
        here composes a record, a byte or an offset, and every other field of that
        record is preserved because it was never named.

        Returns `True` when the write changed the project's stored region, `False`
        when the authority wrote nothing because the project already held exactly this
        region, and `None` when the edit could not be attempted or was refused (the
        refusal is reported). The canvas is repopulated after every call that reached
        the authority, so what it draws is the project's own truth whether or not this
        gesture was the one that changed it - and only a real change may become a
        history entry.
        """
        project = self._session.project_dir
        image = self._session.map_image
        profile = self._session.profile
        if project is None or image is None or profile is None:
            self._report_transition_refusal(self._transition_refusal(identity))
            return None
        try:
            changed = transition_sdk.set_transition_edits(
                project,
                profile,
                image,
                {identity: transition_sdk.TransitionEdit(region=region)},
            )
        except _TRANSITION_ERRORS as exc:
            self._report_transition_refusal(str(exc))
            return None
        if not changed:
            # The project already holds exactly this region, so this gesture wrote
            # nothing and there is no write to undo. The canvas is repopulated anyway:
            # an overlay stale by the drag delta must end the gesture showing the
            # project's own region rather than the one it drew.
            self._populate_transitions()
            return False
        # The write is committed, so the session advances and the shell re-arms
        # validation and build, exactly as a placement drag does.
        self._session.project_mutated()
        self.projectChanged.emit()
        self._populate_transitions()
        self._selected_transition = identity.key
        self._refresh_transition_selection()
        self._set_status(
            f"Moved the trigger region of {identity} to {_region_words(region)}"
        )
        return True

    def _report_transition_refusal(self, message: str) -> None:
        """An expected refusal on a gesture the user made: stated, never silent."""
        self._set_status(message)
        QMessageBox.warning(self, "Move trigger region", message)


    # -- selection and inspector -------------------------------------------

    def _on_scene_selection_changed(self) -> None:
        selected = [item for item in self._scene.selectedItems() if isinstance(item, PlacementMarker)]
        # Selecting a placement is the canvas moving on from a connection, so the
        # connection highlight goes with it: one thing on this canvas is selected.
        self._selected_transition = None
        self._refresh_transition_selection()
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

    def _show_placement_detail(self, visible: bool) -> None:
        """Reveal the detail grid only when there is a placement to detail."""
        self._placement_body.setVisible(visible)
        self._placement_empty.setVisible(not visible)

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
            self._set_status(str(exc))
            self._clear_inspector()
            return
        # "Unknown" is only ever shown where UNKNOWN is itself the proven answer:
        # a relationship the project genuinely does not record. Every field here is
        # one the facade answered for THIS placement, so nothing is a placeholder.
        self._entity.setText(
            relationships["entity"]
            or relationships["entity_type"]
            or "Not recorded for this placement"
        )
        self._behavior.setText(relationships["behavior"] or "No proven behavior")
        self._script.setText(relationships["script"] or "No proven script")
        self._dialogue.setText(
            relationships["dialogue"] or "No proven dialogue relationship"
        )
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
        self._show_placement_detail(True)
        self._update_controls()

    def _clear_inspector(self) -> None:
        """No placement selected: one sentence, no dash or Unknown scaffolding."""
        self._selected_identity = None
        for _caption, value in self._detail_rows:
            value.clear()
        self._open_scene.setEnabled(False)
        self._show_placement_detail(False)
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
        self._set_status("Undo/redo history cleared because the project could not be saved.")
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
        self._set_status(f"Moved {identity} to X {position[0]}, Y {position[1]}")
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
        self._set_status(f"Added {identity} at X {position[0]}, Y {position[1]}")

    # -- visual status / controls -------------------------------------------

    def _on_cursor_moved(self, x: int, y: int) -> None:
        if self._current_map is not None:
            self._set_status(
                f"{self._current_map}  ·  X {x}  Y {y}  ·  zoom {self._canvas.transform().m11() * 100:.0f}%"
            )

    def _on_zoom_changed(self, scale: float) -> None:
        if self._current_map is not None:
            self._set_status(f"{self._current_map}  ·  zoom {scale * 100:.0f}%")

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
        """Keep both visual controls honest about history state."""
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
