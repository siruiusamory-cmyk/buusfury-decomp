"""The read-only spatial map preview: what it paints, and what it refuses.

The preview is glue over the SDK: `map_render.render_map` renders the map and
returns the layers, the composite, the palette and the SDK's own unemulated-effect
warnings; `map_view.rgba_table`/`to_rgba` convert the composite. These tests drive
the widget with an injected renderer, so they prove the widget's own contract -
it paints what the SDK produced, it states the warnings, it draws NOTHING on
either refusal family, and it drops an answer for a map that is no longer
selected - without needing the canonical image.

The ROM-gated lane in the capture suite is what proves the render itself; it is
the SDK's own tests (`tests/integration/test_map_render_rom.py`,
`tests/integration/test_map_decode_equivalence_rom.py`) that pin the pixels.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from PySide6.QtCore import QSize, Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from tools.webfoot.map_render import (  # noqa: E402
    MapRenderResult,
    RenderedLayer,
    UnsupportedMapAssemblyVariant,
)
from tools.webfoot.map_view import MapBrowserError  # noqa: E402

from tools.dragonbyte.mappreview import CELL_PIXELS, PREVIEW_CLAIM, MapPreview  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def _palette() -> tuple[tuple[int, int, int], ...]:
    return tuple((index, index, index) for index in range(256))


def _result(map_id: str = "map:0007", warnings: tuple[str, ...] = ("not emulated: x",)):
    size = 4
    return MapRenderResult(
        semantic_map_id=map_id,
        width=size,
        height=size,
        layers=(
            RenderedLayer(
                bg=0,
                priority=0,
                char_base_block=0,
                screen_base_block=0,
                width=size,
                height=size,
                pixels=bytes([1]) * (size * size),
            ),
        ),
        composite=bytes([1]) * (size * size),
        palette=_palette(),
        provenance={"source": "test"},
        warnings=warnings,
    )


def _settle(preview: MapPreview) -> None:
    assert preview._pool.waitForDone(30_000), "the render worker did not finish"
    QApplication.processEvents()
    assert not preview._loading, "the render answer never reached the widget"


def _blank(preview: MapPreview) -> bool:
    """Whether the canvas holds no image at all."""
    pixmap = preview._canvas.pixmap()
    return pixmap is None or pixmap.isNull()


def test_the_preview_paints_the_composite_and_states_the_sdks_warnings(qapp):
    preview = MapPreview()
    preview.set_renderer(lambda image, map_id: _result(warnings=("camera-relative storage",)))
    preview.show_map(b"image", 7, "Map 0007 - Test")

    _settle(preview)

    assert preview._result is not None
    assert not _blank(preview)
    text = preview._warnings.text()
    assert "camera-relative storage" in text, "the SDK's warning is shown verbatim"
    assert PREVIEW_CLAIM in text
    assert "NOT an emulator capture" in text
    assert "Rendered in" in text, "the measured render time is shown beside the image"


def test_the_preview_selects_a_map_once_and_never_renders_it_twice(qapp):
    calls: list[str] = []
    image = b"image"

    def renderer(rom, map_id):
        calls.append(map_id)
        return _result(map_id)

    preview = MapPreview()
    preview.set_renderer(renderer)
    preview.show_map(image, 7, "Map 0007")
    _settle(preview)
    preview.select(0, 2, 2, (1, 1))
    preview.show_map(image, 7, "Map 0007")
    preview.select(0, 2, 2, (0, 0))

    assert calls == ["map:0007"], "a repaint must not cost a second SDK render"
    assert "cell 0,0" in preview._caption.text()


def test_stepping_back_to_a_map_just_rendered_comes_from_the_cache(qapp):
    calls: list[str] = []
    image = b"image"

    def renderer(rom, map_id):
        calls.append(map_id)
        return _result(map_id)

    preview = MapPreview()
    preview.set_renderer(renderer)
    preview.show_map(image, 1, "Map 0001")
    _settle(preview)
    preview.show_map(image, 2, "Map 0002")
    _settle(preview)
    preview.show_map(image, 1, "Map 0001")

    assert calls == ["map:0001", "map:0002"], "the second visit is a cache hit"
    assert not preview._loading
    assert preview._result.semantic_map_id == "map:0001"
    assert "Rendered in" in preview._warnings.text()


def test_the_cache_is_bounded_and_a_new_image_invalidates_it(qapp):
    from tools.dragonbyte.mappreview import _CACHE_LIMIT

    calls: list[str] = []

    def renderer(rom, map_id):
        calls.append((bytes(rom), map_id))
        return _result(map_id)

    preview = MapPreview()
    preview.set_renderer(renderer)
    first = b"image one"
    for map_index in range(_CACHE_LIMIT + 1):
        preview.show_map(first, map_index, f"Map {map_index:04d}")
        _settle(preview)

    assert len(preview._cache) == _CACHE_LIMIT, "the cache is bounded"

    # A different image object is a different key, so nothing cached for the first
    # image can be installed under the second one's name.
    preview.show_map(b"image two", 0, "Map 0000")
    _settle(preview)

    assert calls[-1] == (b"image two", "map:0000")
    assert preview._result.semantic_map_id == "map:0000"


def test_the_preview_draws_nothing_on_an_unsupported_assembly_variant(qapp):
    reason = "the descriptor uses a map assembly variant not yet proven"

    def renderer(image, map_id):
        raise UnsupportedMapAssemblyVariant(reason)

    preview = MapPreview()
    preview.set_renderer(renderer)
    preview.show_map(b"image", 12, "Map 0012")
    _settle(preview)

    assert preview._result is None
    assert _blank(preview)
    assert reason in preview._message.text()
    assert "Nothing is drawn" in preview._message.text()
    assert preview._warnings.text() == ""


def test_the_preview_draws_nothing_on_a_map_browser_refusal(qapp):
    reason = "colour table must hold 256 RGBA entries"

    def renderer(image, map_id):
        raise MapBrowserError(reason)

    preview = MapPreview()
    preview.set_renderer(renderer)
    preview.show_map(b"image", 12, "Map 0012")
    _settle(preview)

    assert preview._result is None
    assert _blank(preview)
    assert reason in preview._message.text()


def test_a_render_for_a_map_no_longer_selected_is_dropped(qapp):
    """The request token, and the map it belongs to, are what stop a stale paint."""
    image = b"image"
    preview = MapPreview()
    preview.set_renderer(lambda rom, map_id: _result(map_id))
    preview.show_map(image, 1, "Map 0001")
    preview.show_map(image, 2, "Map 0002")
    _settle(preview)

    assert preview._result is not None
    assert preview._result.semantic_map_id == "map:0002"
    assert preview._caption.text().startswith("map:0002")


def test_a_click_is_turned_into_the_cell_the_page_can_open(qapp):
    preview = MapPreview()
    preview.set_renderer(lambda rom, map_id: _result())
    picked: list[tuple[int, int]] = []
    preview.set_cell_handler(lambda column, row: picked.append((column, row)))
    preview.show_map(b"image", 7, "Map 0007")
    _settle(preview)
    preview.select(0, 4, 4, None)

    preview._on_canvas_clicked(CELL_PIXELS * 2 + 5, CELL_PIXELS + 5)

    assert picked == [(2, 1)]
    assert "cell 2,1" in preview._caption.text()
    preview._on_canvas_clicked(CELL_PIXELS * 9, 0)
    assert picked == [(2, 1)], "a click outside the layer's own grid selects nothing"


def test_a_real_mouse_click_is_mapped_through_the_DRAWN_rectangle(qapp):
    """The canvas maps a click back to the RENDERED image, not to its scaled copy.

    The scaled pixmap is a different size from the render, so a mapping that used
    the pixmap's own width (or height) would report a cell near the top left for a
    click near the bottom right. This drives a real mouse event.
    """
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QPixmap
    from PySide6.QtTest import QTest

    from tools.dragonbyte.mappreview import _Canvas

    canvas = _Canvas()
    canvas.resize(200, 200)
    canvas.set_render(QPixmap(100, 100), QSize(512, 512))
    picked: list[tuple[int, int]] = []
    canvas.clicked.connect(lambda x, y: picked.append((x, y)))

    rectangle = canvas.display_rect()
    assert (rectangle.width(), rectangle.height()) == (100, 100)
    # Three quarters across and down the drawn rectangle is pixel 384 of 512.
    QTest.mouseClick(
        canvas,
        Qt.MouseButton.LeftButton,
        pos=QPoint(
            rectangle.x() + rectangle.width() * 3 // 4,
            rectangle.y() + rectangle.height() * 3 // 4,
        ),
    )

    assert picked == [(384, 384)]
    canvas.clicked.disconnect()
    QTest.mouseClick(canvas, Qt.MouseButton.LeftButton, pos=QPoint(0, 0))
    assert picked == [(384, 384)], "a click outside the image selects nothing"


def test_no_map_selected_states_that_rather_than_drawing_a_blank(qapp):
    preview = MapPreview()
    preview.show_map(None, None)

    assert "No map is selected" in preview._message.text()
    assert preview._warnings.text() == ""
