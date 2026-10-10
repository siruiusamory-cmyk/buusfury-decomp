"""The read-only spatial preview of one map, painted from the SDK's own render.

The SDK already decodes and composes a map: `tools/webfoot/map_render.py`'s
`render_map` renders every ROM-resident background layer to 8bpp indices,
composes them by the accepted order, and returns the palette, a provenance record
and the list of runtime effects it deliberately does not emulate. This widget
paints that result. It decodes nothing, invents no graphic for a layer the SDK did
not render, and on a refusal it states the SDK's own reason and draws nothing.

Three facts are shown beside the image rather than hidden in a log, because the
owner asked for an honest preview: what was not emulated (the render's own
`warnings`, verbatim), that the composition is the SDK's ROM-derived render and
not an emulator capture, and how long the render took. Measured on the canonical
image, one map costs 0.09 s to 1.33 s, so the render runs on a worker with a
request token: the event loop is never held, and an answer for a map that is no
longer selected is dropped rather than painted.
"""

from __future__ import annotations

import time

from PySide6.QtCore import QObject, QRect, QRunnable, QSize, Qt, QThreadPool, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from tools.webfoot import map_render, map_view
from tools.webfoot.map_render import MapRenderError

from . import theme

#: The one sentence a reader needs before believing the image: where it came from,
#: and which tests pin that provenance.
PREVIEW_CLAIM = (
    "The Webfoot SDK's own ROM renderer drew this (tools/webfoot/map_render.py, "
    "render_map), so it is a ROM-derived composition and NOT an emulator capture. "
    "Pinned by tests/integration/test_map_render_rom.py and "
    "tests/integration/test_map_decode_equivalence_rom.py."
)

#: The SDK's pixel size for one layout cell, taken from the SDK rather than
#: restated here: a click on the image is turned into a cell with this.
CELL_PIXELS = map_view.CHUNK_PIXELS

#: The colours the selection overlays are drawn in. Decoration only: the selected
#: layer and cell are also stated in words beside the image.
_LAYER_PEN = QColor(theme.COLORS.text_muted)
_CELL_PEN = QColor(theme.COLORS.focus)

#: How many rendered maps are kept. One costs about a second of SDK work and its
#: composite is a few megabytes, so four is bounded in memory and enough that
#: stepping back to the map just left does not repay the render. The cache holds
#: its image, so an entry can never be attributed to a later image that reuses the
#: same object id, and it is dropped when the selection moves to a new image.
_CACHE_LIMIT = 4


class _RenderSignals(QObject):
    """The worker's one answer, delivered on the thread that owns the widget."""

    finished = Signal(int, object, float)


class _RenderTask(QRunnable):
    """Render one map off the UI thread.

    `docs/desktop-ui.md` sets a 400 ms feedback budget and forbids blocking the UI
    thread for a decode; a map measured between 0.09 s and 1.33 s, so it belongs
    here. Both refusal families the SDK raises on this path are caught and their
    message kept verbatim: `MapRenderError` (and its
    `UnsupportedMapAssemblyVariant` subclass) from the renderer, and
    `MapBrowserError` from the pixel conversion.
    """

    def __init__(self, renderer, image: bytes, map_id: str, key, token: int, signals) -> None:
        super().__init__()
        self.signals = signals
        self._renderer = renderer
        self._image = image
        self._map_id = map_id
        self._key = key
        self._token = token

    def run(self) -> None:
        started = time.monotonic()
        try:
            result = self._renderer(self._image, self._map_id)
            pixels = map_view.to_rgba(
                result.composite,
                map_view.rgba_table(result.palette),
                backdrop=result.palette[0] if result.palette else None,
            )
            answer = (self._key, self._image, result, pixels, "")
        except (MapRenderError, map_view.MapBrowserError) as exc:
            answer = (self._key, self._image, None, b"", str(exc))
        except Exception as exc:  # noqa: BLE001 - a worker boundary states it
            answer = (self._key, self._image, None, b"", str(exc))
        try:
            self.signals.finished.emit(
                self._token, answer, time.monotonic() - started
            )
        except RuntimeError:
            # The widget was destroyed while this render ran, so the signal source
            # and the labels that would render the answer are gone.
            pass


class _Canvas(QLabel):
    """The image area: the scaled render, and the pixel a click landed on.

    The scaled pixmap is centred, so the click is mapped back through the same
    rectangle the label drew it in rather than through the label's own size.
    """

    clicked = Signal(int, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("mapPreviewCanvas")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(180)
        self._pixmap: QPixmap | None = None
        #: The size of the RENDERED image, which is what a click is mapped into.
        #: The pixmap is a scaled copy, so its own size cannot answer that.
        self._source = QSize(0, 0)

    def set_render(self, pixmap: QPixmap | None, source: QSize) -> None:
        self._pixmap = pixmap
        self._source = QSize(source) if source is not None else QSize(0, 0)
        self.setPixmap(pixmap if pixmap is not None else QPixmap())

    def display_rect(self) -> QRect:
        """Where the pixmap actually sits inside this label.

        A `QLabel` draws a pixmap at the pixmap's own size, centred, and never
        scales it to the label. So the rect is the pixmap's size and not the
        label's: a mapping that used the label's size would stretch the
        coordinates whenever the two differ, which is every render that is not
        exactly label-shaped.
        """
        if self._pixmap is None or self._pixmap.isNull():
            return QRect()
        available = self.size()
        size = self._pixmap.size()
        return QRect(
            (available.width() - size.width()) // 2,
            (available.height() - size.height()) // 2,
            size.width(),
            size.height(),
        )

    def mousePressEvent(self, event) -> None:
        if self._pixmap is None or self._pixmap.isNull() or self._source.isEmpty():
            return
        rect = self.display_rect()
        position = event.position().toPoint()
        if not rect.contains(position):
            return
        self.clicked.emit(
            (position.x() - rect.x()) * self._source.width() // max(1, rect.width()),
            (position.y() - rect.y()) * self._source.height() // max(1, rect.height()),
        )


class MapPreview(QWidget):
    """The Maps destination's read-only spatial preview."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("mapPreview")
        #: The SDK renderer, injectable so a test can drive both refusal names.
        self._renderer = map_render.render_map
        self._pool = QThreadPool.globalInstance()
        self._signals = _RenderSignals(self)
        self._tasks: dict[int, _RenderTask] = {}
        self._request = 0
        self._for: tuple[int, int] | None = None
        #: Rendered maps, keyed by (the image object's id, map index). The entry
        #: holds the image itself, so the id cannot be reused behind its back.
        self._cache: dict[tuple[int, int], tuple] = {}
        self._result = None
        self._rgba: bytes | None = None
        self._pixmap: QPixmap | None = None
        self._seconds = 0.0
        self._problem = ""
        self._loading = False
        self._slot = 0
        self._cell: tuple[int, int] | None = None
        self._columns = 0
        self._rows = 0
        self._cell_handler = None

        self._caption = QLabel()
        self._caption.setProperty("dbzRole", "hint")
        self._caption.setWordWrap(True)
        self._canvas = _Canvas()
        self._canvas.setToolTip(
            "Click a cell to select it in the table. The preview is read-only: "
            "no cell here can be painted."
        )
        self._warnings = QLabel()
        self._warnings.setProperty("dbzRole", "hint")
        self._warnings.setWordWrap(True)
        self._message = QLabel()
        self._message.setProperty("dbzRole", "technical")
        self._message.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(theme.SPACE_SM)
        layout.addWidget(self._caption)
        layout.addWidget(self._canvas, 1)
        layout.addWidget(self._warnings)
        layout.addWidget(self._message)

        self._signals.finished.connect(self._rendered)
        self._canvas.clicked.connect(self._on_canvas_clicked)
        self._render_state("Open a map to see its spatial layout.")

    # -- wiring ---------------------------------------------------------------

    def set_renderer(self, renderer) -> None:
        """Use this renderer instead of the SDK's. For a test that needs to refuse."""
        self._renderer = renderer

    def set_cell_handler(self, handler) -> None:
        """Told the (column, row) cell a click on the image landed on."""
        self._cell_handler = handler

    # -- what is shown --------------------------------------------------------

    def show_map(self, image: bytes | None, map_index: int | None, name: str = "") -> None:
        """Render one map, or state that there is nothing to render.

        A map already rendered is installed from the cache instead of rendered
        again, and a render already running for this map is not started twice, so
        moving between maps and layers never pays the same second twice. The
        request token still moves every time the selection does, so an answer for
        a map that is no longer selected is dropped rather than painted.
        """
        if image is None or map_index is None:
            self._for = None
            self._request += 1
            self._loading = False
            self._result = None
            self._rgba = None
            self._pixmap = None
            self._canvas.set_render(None, None)
            self._render_state("No map is selected, so there is nothing to render.")
            return
        key = (id(image), map_index)
        if key in self._cache:
            self._for = key
            self._request += 1
            self._loading = False
            self._install(self._cache[key])
            return
        if self._for == key and self._loading:
            return
        self._for = key
        self._request += 1
        self._loading = True
        self._problem = ""
        self._result = None
        self._rgba = None
        self._pixmap = None
        self._canvas.set_render(None, None)
        self._caption.setText(name or f"Map {map_index:04d}")
        self._warnings.setText("")
        self._message.setText(
            f"Rendering map {map_index:04d} through the SDK, which takes about a "
            "second..."
        )
        task = _RenderTask(
            self._renderer,
            image,
            f"map:{map_index:04d}",
            key,
            self._request,
            self._signals,
        )
        self._tasks[self._request] = task
        self._pool.start(task)

    def select(self, slot: int, columns: int, rows: int, cell=None) -> None:
        """Reflect the selected layer and cell. Draws nothing the SDK did not render."""
        self._slot = slot
        self._cell = cell
        self._columns = columns
        self._rows = rows
        self._paint()

    # -- the worker's answer --------------------------------------------------

    def _rendered(self, token: int, answer, seconds: float) -> None:
        self._tasks.pop(token, None)
        if token != self._request:
            # A render for a map that is no longer selected is dropped rather than
            # painted or kept: its palette and its cells describe something else.
            return
        self._loading = False
        key = answer[0]
        self._cache[key] = (answer[1], answer[2], answer[3], answer[4], seconds)
        while len(self._cache) > _CACHE_LIMIT:
            self._cache.pop(next(iter(self._cache)))
        self._install(self._cache[key])

    def _install(self, entry) -> None:
        """Show one rendered map, or its refusal: one path for fresh and cached.

        A refusal is cached by the same key as a render, because the answer is the
        same every time and re-rendering a map the SDK refuses once per status
        refresh would pay a second of work for an answer already known.
        """
        _image, result, pixels, problem, seconds = entry
        self._seconds = seconds
        self._problem = problem
        self._result = result
        self._rgba = pixels
        if result is None:
            self._pixmap = None
            self._canvas.set_render(None, None)
            self._caption.clear()
            self._warnings.setText("")
            self._message.setText(
                f"{problem} Nothing is drawn: this preview refuses rather than "
                "drawing a map the SDK did not prove."
            )
            return
        self._message.clear()
        self._pixmap = self._build_pixmap()
        self._paint()

    # -- painting -------------------------------------------------------------

    def _build_pixmap(self) -> QPixmap | None:
        """The composite as a pixmap the widget owns.

        `QImage` does not copy the buffer it is handed, so it is copied before the
        bytes can be collected; every later scale and overlay works on the copy.
        Nearest-neighbour scaling keeps a pixel a pixel.
        """
        result = self._result
        if result is None or self._rgba is None:
            return None
        image = QImage(
            self._rgba,
            result.width,
            result.height,
            result.width * 4,
            QImage.Format.Format_RGBA8888,
        ).copy()
        available = self._canvas.size()
        if available.width() < 8 or available.height() < 8:
            # A widget that has not been laid out yet has no size to scale into,
            # and scaling to an empty size would hand back a null pixmap: the
            # resize handler scales it again once there is room.
            available = QSize(result.width, result.height)
        scaled = QPixmap.fromImage(image).scaled(
            available,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        return scaled

    def _paint(self) -> None:
        """Draw the cached render with this selection's overlays, or the state."""
        if self._pixmap is None:
            return
        result = self._result
        factor = self._pixmap.width() / result.width if result.width else 1.0
        drawn = QPixmap(self._pixmap)
        painter = QPainter(drawn)
        try:
            if 0 <= self._slot < 4:
                layer = next(
                    (item for item in result.layers if item.bg == self._slot), None
                )
                if layer is not None and layer.width and layer.height:
                    painter.setPen(QPen(_LAYER_PEN, 1, Qt.PenStyle.DashLine))
                    painter.drawRect(
                        0,
                        0,
                        int(layer.width * factor) - 1,
                        int(layer.height * factor) - 1,
                    )
            if self._cell is not None:
                column, row = self._cell
                painter.setPen(QPen(_CELL_PEN, 2))
                painter.drawRect(
                    int(column * CELL_PIXELS * factor),
                    int(row * CELL_PIXELS * factor),
                    int(CELL_PIXELS * factor) - 1,
                    int(CELL_PIXELS * factor) - 1,
                )
        finally:
            painter.end()
        self._canvas.set_render(drawn, QSize(result.width, result.height))
        self._state_text()

    def _state_text(self) -> None:
        """The caption, the SDK's own warnings and the measured render time.

        The warnings are the renderer's, verbatim and unedited: they are the
        honest statement of what this preview does not emulate.
        """
        result = self._result
        if result is None:
            return
        cell = "" if self._cell is None else f", cell {self._cell[0]},{self._cell[1]}"
        self._caption.setText(
            f"{result.semantic_map_id}, {result.width}x{result.height} pixels, "
            f"layer BG{self._slot} selected{cell}"
        )
        self._warnings.setText(
            f"{PREVIEW_CLAIM} Rendered in {self._seconds:.2f} s. "
            "Not emulated by this render: "
            + " ".join(result.warnings)
        )

    def _render_state(self, text: str) -> None:
        self._caption.clear()
        self._warnings.setText("")
        self._message.setText(text)

    def _on_canvas_clicked(self, x: int, y: int) -> None:
        """Turn a click into a cell, and tell the page which one was picked."""
        if self._result is None or self._cell_handler is None:
            return
        column, row = x // CELL_PIXELS, y // CELL_PIXELS
        if not 0 <= column < self._columns or not 0 <= row < self._rows:
            return
        self._cell = (column, row)
        self._paint()
        self._cell_handler(column, row)

    def resizeEvent(self, event) -> None:
        """Rescale the cached render: the SDK is never asked to render again."""
        super().resizeEvent(event)
        if self._result is not None:
            self._pixmap = self._build_pixmap()
            self._paint()
