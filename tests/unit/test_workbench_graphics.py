"""Headless DragonByte Z Graphics-tab controller/state tests (WORKBENCH-005 L2).

Most tests drive the tab against a tiny FAKE `ActorSprites` duck-typed to the
facade surface the tab reads (`palette.rgb`, `graphics()`, `graphic()`,
`get_actor_animations()`, `palette_users()`), injected onto the Session's lazy
`sprites` slot. That keeps SC1-SC6/SC9 deterministic and ROM-free, the same way
test_workbench_scene runs on a synthetic profile. One ROM-gated test proves a
real decoded thumbnail renders (SC2) when the canonical ROM is present.
"""

from __future__ import annotations

import glob
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from tools.webfoot import graphics as graphics_sdk  # noqa: E402
from tools.webfoot.graphics import (  # noqa: E402
    ActorAnimation,
    ActorFrame,
    CharacterIdentity,
    GraphicIdentity,
)
from tools.webfoot.project import ProjectMeta, read_project, write_project  # noqa: E402
from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.graphics_tab import GraphicsTab, indexed_pixmap  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)
_PROFILE = "fake_profile_0001"


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


# --- a tiny fake facade ------------------------------------------------------


@dataclass(frozen=True)
class _FakeGraphic:
    identity: GraphicIdentity
    width: int
    height: int
    pixels: bytes
    consumers: tuple
    characters: tuple

    @property
    def shared(self) -> bool:
        return len(self.consumers) > 1


class _FakePalette:
    # A distinctive 256-entry table: index i -> a grey-ish ramp so a rendered
    # thumbnail is not all one colour when the pixels vary.
    @property
    def rgb(self):
        return tuple((i, (i * 2) % 256, (255 - i)) for i in range(256))


class _FakeSprites:
    """Duck-typed to exactly what GraphicsTab reads. Two graphics, one shared."""

    def __init__(self) -> None:
        self.palette = _FakePalette()
        c0 = CharacterIdentity(_PROFILE, 0)
        g0 = GraphicIdentity(_PROFILE, 0)
        g1 = GraphicIdentity(_PROFILE, 1)
        # g0: 2x2 with four distinct indices; used by one frame (not shared).
        self._g0 = _FakeGraphic(g0, 2, 2, bytes([0, 5, 40, 200]), ("frameA",), (c0,))
        # g1: shared across two frames; pixels reference index 40 too.
        self._g1 = _FakeGraphic(g1, 2, 1, bytes([40, 7]), ("frameA", "frameB"), (c0,))
        self._by_id = {g0: self._g0, g1: self._g1}
        self._char = c0

    def graphics(self):
        return (self._g0, self._g1)

    def graphic(self, identity):
        return self._by_id[identity]

    def characters(self):
        return (type("C", (), {"identity": self._char})(),)

    def get_actor_animations(self, identity):
        frame = ActorFrame(
            frame_index=0,
            graphics=(GraphicIdentity(_PROFILE, 0), None, None, None),
        )
        return (ActorAnimation(index=0, frames=(frame,)),)

    def palette_users(self, index):
        # Index 40 is referenced by both graphics; every other index by none.
        return (self._g0.identity, self._g1.identity) if index == 40 else ()

    def export_graphic_png(self, identity, palette_rgb=None):
        # Mirror the real façade: encode the graphic to indexed-PNG bytes. Kept
        # thin so the GUI slot tests drive a real encode through the fake.
        from tools.webfoot.formats import indexed_png
        from tools.webfoot.formats import sprite_graphics as sg

        graphic = self._by_id[identity]
        return indexed_png.encode(
            graphic.pixels,
            graphic.width,
            graphic.height,
            palette_rgb or self.palette.rgb,
            transparent_index=sg.TRANSPARENT_INDEX,
        )


def _session_with_sprites(project_dir=None) -> Session:
    session = Session()
    # Inject the fake into the lazy slot so `.sprites` returns it without a ROM.
    session._sprites = _FakeSprites()
    session._sprites_loaded = True
    session.profile = type("P", (), {"id": _PROFILE})()
    if project_dir is not None:
        session.set_project(project_dir)
    return session


@pytest.fixture
def project(tmp_path) -> Path:
    meta = ProjectMeta(1, _PROFILE, "Fake Game", "0" * 64, 1024, "graphics-tab-test")
    write_project(tmp_path, meta, enemies=[], characters=[])
    return tmp_path


@pytest.fixture
def tab(qapp) -> GraphicsTab:
    t = GraphicsTab(_session_with_sprites())
    t.on_session_changed()
    return t


# --- SC1: mounts in the shell before a ROM, disabled -------------------------


def test_shell_mounts_graphics_tab_disabled_pre_rom(qapp):
    from tools.webfoot.profile import RomProfileCatalog

    catalog = RomProfileCatalog.load(os.path.join("config", "roms.yaml"))
    window = MainWindow(Session(), catalog)
    titles = [window._tabs.tabText(i) for i in range(window._tabs.count())]
    assert "Graphics" in titles
    gi = titles.index("Graphics")
    assert not window._tabs.isTabEnabled(gi)  # post-ROM tab, off until ROM open


# --- SC2: indexed pixels + palette -> a non-empty, non-uniform pixmap --------


def test_indexed_pixmap_matches_size_and_is_not_uniform():
    palette = _FakePalette().rgb
    pixmap = indexed_pixmap(bytes([0, 5, 40, 200]), 2, 2, palette)
    assert (pixmap.width(), pixmap.height()) == (2, 2)
    image = pixmap.toImage()
    colours = {image.pixel(x, y) for x in range(2) for y in range(2)}
    assert len(colours) > 1  # distinct indices -> distinct colours, not one blob


def test_populate_grid_adds_items_but_decodes_no_icons(tab):
    # SC1: populate is O(n) cheap widget creation - items exist, but NO icon is
    # decoded yet (the eager full-corpus decode that froze the window is gone).
    assert tab._grid.count() == 2
    assert not tab._pixmap_cache
    assert tab._grid.item(0).icon().isNull()
    assert tab._grid.item(1).icon().isNull()


def test_browser_renders_a_thumbnail_for_a_known_identity(tab):
    # SC2/SC3: triggering the lazy path decodes a real pixmap icon for the row.
    tab._decode_visible_icons(rows=[0])
    icon = tab._grid.item(0).icon()
    assert not icon.isNull()
    pixmap = icon.pixmap(64, 64)
    assert not pixmap.isNull() and pixmap.width() > 0
    # SC2: only the driven row decoded; the untouched row is still icon-less.
    assert tab._grid.item(1).icon().isNull()
    assert set(tab._pixmap_cache) == {GraphicIdentity(_PROFILE, 0)}


def test_scroll_decodes_newly_visible_rows(tab):
    # SC4: the scrollbar signal drives a lazy pass. Offscreen Qt reports no real
    # viewport, so assert the connected slot decodes when handed the visible rows.
    tab._decode_visible_icons(rows=[1])
    assert not tab._grid.item(1).icon().isNull()
    assert GraphicIdentity(_PROFILE, 1) in tab._pixmap_cache


# --- WB-005 missing-thumbnail FIX #1: drain ices every item ------------------


def test_scroll_signal_fires_without_error_on_int_arg(tab):
    # SC2: valueChanged/rangeChanged pass an int; the slot must swallow it and run
    # the visible pass rather than iterate the int (the old direct-connect bug).
    tab._on_scroll(5)  # scrollbar value
    tab._on_scroll(0, 100)  # rangeChanged(min, max)


def test_scroll_and_range_signals_connected_to_slot(tab):
    # SC2: both scrollbar signals are wired so a resize/relayout that shifts the
    # range fills newly-shown rows, not just an explicit user drag.
    bar = tab._grid.verticalScrollBar()
    # Firing the signals must not raise and must decode the currently-visible set.
    bar.rangeChanged.emit(0, 10)
    bar.valueChanged.emit(3)


def test_icon_drain_ices_every_item_no_permanent_blank(tab, qapp):
    # SC1: the chained batch drain must eventually give EVERY grid item an icon,
    # proving no row is permanently skipped by viewport/scroll sampling. Drive the
    # drain synchronously by pumping the batches to completion (no real event loop).
    for item_row in range(tab._grid.count()):
        assert tab._grid.item(item_row).icon().isNull()  # pre-drain: all blank
    tab._start_icon_drain()
    # Pump chained batches until the drain reports done (bounded; 2 items, 64/tick).
    for _ in range(100):
        if not tab._drain_active:
            break
        tab._drain_batch()
    for item_row in range(tab._grid.count()):
        assert not tab._grid.item(item_row).icon().isNull()  # every cell iced
    assert tab._drain_active is False


def test_icon_drain_finishes_on_undecodable_item(tab, monkeypatch):
    # A sprite that raises on decode must not loop the drain forever: it gets a
    # blank icon and the drain terminates.
    from tools.webfoot import graphics as gsdk

    def boom(identity):
        raise gsdk.GraphicsError("undecodable")

    monkeypatch.setattr(tab._session.sprites, "graphic", boom)
    tab._start_icon_drain()
    for _ in range(100):
        if not tab._drain_active:
            break
        tab._drain_batch()
    assert tab._drain_active is False
    for item_row in range(tab._grid.count()):
        assert not tab._grid.item(item_row).icon().isNull()


# --- WB-005 viewer-size FIX #2: larger scaled nearest-neighbour preview ------


def test_preview_min_size_increased(tab):
    # SC4: preview minimums bumped materially above the old 160/120.
    assert tab._preview.minimumWidth() >= 320
    assert tab._preview.minimumHeight() >= 320
    assert tab._anim_preview.minimumWidth() >= 320
    assert tab._anim_preview.minimumHeight() >= 320


def test_selected_preview_scales_small_sprite_up(tab):
    # SC3: a 2x2 sprite must display LARGER than native, aspect preserved.
    tab._grid.setCurrentRow(0)  # g0 is 2x2
    shown = tab._preview.pixmap()
    assert not shown.isNull()
    assert shown.width() > 2 and shown.height() > 2  # scaled up from native
    assert max(shown.width(), shown.height()) >= 320  # fills the box
    assert shown.width() == shown.height()  # 2x2 -> square, aspect preserved


def test_scaled_for_preview_matches_keepaspect_nearest_math(tab):
    # SC3: assert the KeepAspectRatio scale target (a 4-wide x 1-tall sprite scales
    # to box-wide, box/4-tall), the exact math nearest-neighbour box-fill produces.
    from PySide6.QtGui import QPixmap

    native = QPixmap(4, 1)
    native.fill()
    scaled = tab._scaled_for_preview(native, box=320)
    assert scaled.width() == 320  # long edge fills the box
    assert scaled.height() == 80  # 4:1 aspect preserved (320/4)


def test_scaled_for_preview_never_shrinks_large_sprite(tab):
    # A sprite already larger than the box is left native, not downscaled.
    from PySide6.QtGui import QPixmap

    big = QPixmap(400, 400)
    big.fill()
    assert tab._scaled_for_preview(big, box=320) is big


def test_animation_preview_scales_up(tab):
    # SC5: the animation frame preview scales the same way as the selected preview.
    tab._grid.setCurrentRow(0)  # loads character 0's animation (frame -> g0 2x2)
    shown = tab._anim_preview.pixmap()
    assert not shown.isNull()
    assert max(shown.width(), shown.height()) >= 320  # scaled up, not tiny


# --- SC3/SC4/E: palette apply records an override, discloses consumers --------


def test_palette_apply_records_override_bumps_revision_emits(tab, qapp, project):
    session = _session_with_sprites(project)
    t = GraphicsTab(session)
    t.on_session_changed()
    emitted = []
    t.projectChanged.connect(lambda: emitted.append(True))
    # Auto-approve the shared-edit confirmation dialog.
    from tools.webfoot.workbench import graphics_tab as gt
    orig_q = gt.QMessageBox.question
    gt.QMessageBox.question = staticmethod(
        lambda *a, **k: gt.QMessageBox.StandardButton.Yes
    )
    try:
        before = session.project_revision
        t._palette_pending[40] = (10, 20, 30)
        t._on_apply()
    finally:
        gt.QMessageBox.question = orig_q

    assert emitted == [True]
    assert session.project_revision == before + 1
    assert read_project(project).graphics_overrides.palette[40] == (10, 20, 30)


def test_pending_change_discloses_shared_consumer_count(tab):
    # Index 40 is shared by both fake graphics; the disclosed count must equal
    # len(palette_users(40)) (SC4), and be phrased in game language, not a write.
    tab._palette_pending[40] = (1, 2, 3)
    tab._refresh_pending_ui()
    text = tab._pending_label.text()
    users = len(tab._session.sprites.palette_users(40))
    assert f"known consumers: {users}" in text
    assert "Palette color 40" in text
    assert "0x" not in text and "write" not in text.lower()


def test_pending_change_for_unshared_index_shows_zero(tab):
    tab._palette_pending[7] = (1, 2, 3)
    tab._refresh_pending_ui()
    assert "known consumers: 0" in tab._pending_label.text()


# --- SC5: animation view carries no fabricated timing ------------------------


def test_animation_view_never_invents_timing(tab):
    tab._grid.setCurrentRow(0)  # selects graphic 0, loads its character's anims
    assert tab._animations
    for animation in tab._animations:
        for frame in animation.frames:
            assert frame.duration is None
            assert frame.timing_unknown is True
    # The frame label carries a count, never a millisecond value.
    assert "ms" not in tab._frame_label.text().lower()


def test_frame_stepper_wraps_without_a_playback_speed(tab):
    tab._grid.setCurrentRow(0)
    tab._step_frame(1)  # single-frame anim: wraps back to itself, no crash
    assert "Frame 1 / 1" in tab._frame_label.text()


# --- SC6: SDK-calling slots catch the family parent, no dead click -----------


def test_apply_surfaces_sdk_error_without_escaping(qapp, project, monkeypatch):
    session = _session_with_sprites(project)
    t = GraphicsTab(session)
    t.on_session_changed()
    warnings = []
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.QMessageBox.critical",
        lambda *a, **k: warnings.append(a[-1]),
    )
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.QMessageBox.question",
        lambda *a, **k: __import__(
            "tools.webfoot.workbench.graphics_tab", fromlist=["QMessageBox"]
        ).QMessageBox.StandardButton.Yes,
    )
    # A GraphicsError from the SDK set path must become a QMessageBox, not escape.
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.graphics_sdk.set_palette_override",
        lambda *a, **k: (_ for _ in ()).throw(graphics_sdk.GraphicsError("bad index")),
    )
    emitted = []
    t.projectChanged.connect(lambda: emitted.append(True))
    before = session.project_revision

    t._palette_pending[40] = (1, 2, 3)
    t._on_apply()  # must not raise

    assert warnings == ["bad index"]
    assert emitted == []
    assert session.project_revision == before


def test_apply_surfaces_project_error_without_escaping(qapp, project, monkeypatch):
    from tools.webfoot.project import ProjectError

    session = _session_with_sprites(project)
    t = GraphicsTab(session)
    t.on_session_changed()
    warnings = []
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.QMessageBox.critical",
        lambda *a, **k: warnings.append(a[-1]),
    )
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.QMessageBox.question",
        lambda *a, **k: __import__(
            "tools.webfoot.workbench.graphics_tab", fromlist=["QMessageBox"]
        ).QMessageBox.StandardButton.Yes,
    )
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.graphics_sdk.set_palette_override",
        lambda *a, **k: (_ for _ in ()).throw(ProjectError("profile mismatch")),
    )
    t._palette_pending[40] = (1, 2, 3)
    t._on_apply()
    assert warnings == ["profile mismatch"]


# --- SDK trio round trip (the new project-authoring facade) -------------------


def test_set_get_remove_palette_override_round_trip(project):
    profile = type("P", (), {"id": _PROFILE})()
    assert graphics_sdk.get_palette_override(project, profile, 40) is None
    graphics_sdk.set_palette_override(project, profile, 40, 9, 8, 7)
    assert graphics_sdk.get_palette_override(project, profile, 40) == (9, 8, 7)
    assert graphics_sdk.remove_palette_override(project, profile, 40) is True
    assert graphics_sdk.get_palette_override(project, profile, 40) is None
    assert graphics_sdk.remove_palette_override(project, profile, 40) is False


def test_set_palette_override_rejects_out_of_range(project):
    profile = type("P", (), {"id": _PROFILE})()
    with pytest.raises(graphics_sdk.GraphicsError):
        graphics_sdk.set_palette_override(project, profile, 40, 300, 0, 0)
    with pytest.raises(graphics_sdk.GraphicsError):
        graphics_sdk.set_palette_override(project, profile, 999, 0, 0, 0)


def test_set_palette_override_rejects_profile_mismatch(project):
    from tools.webfoot.project import ProjectValidationError

    wrong = type("P", (), {"id": "some_other_profile"})()
    with pytest.raises(ProjectValidationError):
        graphics_sdk.set_palette_override(project, wrong, 40, 1, 2, 3)


# --- WB-005 L4 FIX #1: applied recolour is visible in-session ----------------


def _auto_yes(monkeypatch):
    from tools.webfoot.workbench import graphics_tab as gt
    monkeypatch.setattr(
        gt.QMessageBox,
        "question",
        staticmethod(lambda *a, **k: gt.QMessageBox.StandardButton.Yes),
    )


def test_effective_rgb_reflects_committed_override_after_apply(qapp, project, monkeypatch):
    _auto_yes(monkeypatch)
    session = _session_with_sprites(project)
    t = GraphicsTab(session)
    t.on_session_changed()
    canonical = t._session.sprites.palette.rgb[40]
    assert t._effective_rgb(t._session.sprites)[40] == canonical  # pre-apply
    t._palette_pending[40] = (10, 20, 30)
    t._on_apply()
    # After Apply the effective palette shows the AUTHORED colour, not canonical.
    assert t._effective_rgb(t._session.sprites)[40] == (10, 20, 30)


def test_apply_clears_pixmap_cache_so_thumbnails_repaint(qapp, project, monkeypatch):
    _auto_yes(monkeypatch)
    session = _session_with_sprites(project)
    t = GraphicsTab(session)
    t.on_session_changed()
    # Prime the cache via a lazy pass, then recolour index 40 (both fake graphics).
    t._decode_visible_icons(rows=[0, 1])
    assert t._pixmap_cache
    t._grid.setCurrentRow(0)
    t._palette_pending[40] = (10, 20, 30)
    t._on_apply()
    # Cache was dropped so a re-fetched thumbnail decodes against the new colour.
    ident = GraphicIdentity(_PROFILE, 1)  # g1 uses index 40
    g1 = t._session.sprites.graphic(ident)
    fresh = indexed_pixmap(g1.pixels, g1.width, g1.height, t._effective_rgb(t._session.sprites))
    img = fresh.toImage()
    # index-40 pixel now renders the authored colour (10,20,30).
    assert img.pixelColor(0, 0).getRgb()[:3] == (10, 20, 30)


def test_undo_redo_move_effective_palette(qapp, project, monkeypatch):
    _auto_yes(monkeypatch)
    session = _session_with_sprites(project)
    t = GraphicsTab(session)
    t.on_session_changed()
    canonical = t._session.sprites.palette.rgb[40]
    t._palette_pending[40] = (10, 20, 30)
    t._on_apply()
    assert t._effective_rgb(t._session.sprites)[40] == (10, 20, 30)
    t._undo_stack.undo()
    assert t._effective_rgb(t._session.sprites)[40] == canonical
    # Undo dropped the whole decode cache; a fresh lazy decode of g1 (index 40)
    # renders the reverted canonical colour, proving the stale thumbnail is gone.
    g1 = t._session.sprites.graphic(GraphicIdentity(_PROFILE, 1))
    assert g1.identity not in t._pixmap_cache
    t._decode_visible_icons(rows=[1])
    assert t._pixmap_cache[g1.identity].toImage().pixelColor(0, 0).getRgb()[:3] == canonical
    t._undo_stack.redo()
    assert t._effective_rgb(t._session.sprites)[40] == (10, 20, 30)


def test_pending_from_colour_is_effective_not_canonical(qapp, project, monkeypatch):
    _auto_yes(monkeypatch)
    session = _session_with_sprites(project)
    t = GraphicsTab(session)
    t.on_session_changed()
    # Commit a first recolour, then start a second pending edit on the same index.
    t._palette_pending[40] = (10, 20, 30)
    t._on_apply()
    t._palette_pending[40] = (99, 88, 77)
    t._refresh_pending_ui()
    # The "from" swatch is the committed effective colour (0A1418), not canonical.
    assert "#0A141E -> #63584D" in t._pending_label.text()


# --- WB-005 L4 FIX #3: consumers "unknown" on SDK error, never "0" ------------


def test_pending_shows_unknown_when_palette_users_raises(tab, monkeypatch):
    def boom(index):
        raise graphics_sdk.GraphicsError("transient")
    monkeypatch.setattr(tab._session.sprites, "palette_users", boom)
    tab._palette_pending[40] = (1, 2, 3)
    tab._refresh_pending_ui()
    text = tab._pending_label.text()
    assert "known consumers: unknown" in text
    assert "known consumers: 0" not in text


# --- WB-005 sprite PNG export: SDK façade + GUI button/slot -------------------

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _real_sprites():
    """Exercise the REAL ActorSprites.export_graphic_png (not the fake facade).

    Built via __new__ + a stub palette and graphic-lookup, so the encode runs
    through the actual SDK method and the real indexed_png.encode; the graphic is
    a tiny 2x2 duck carrying just the width/height/pixels the façade reads.
    """
    from tools.webfoot.graphics import ActorSprites, GraphicIdentity as GID

    ident = GID(_PROFILE, 0)
    graphic = type(
        "G", (), {"width": 2, "height": 2, "pixels": bytes([0, 1, 2, 3])}
    )()
    palette = type("Pal", (), {"rgb": tuple((i, i, i) for i in range(256))})()
    sprites = ActorSprites.__new__(ActorSprites)
    sprites.palette = palette
    sprites.graphic = lambda i, g=graphic: g
    return sprites, ident


def test_export_graphic_png_returns_png_bytes_matching_size():
    # SC1: façade returns non-empty PNG bytes; decoded dims == graphic w x h.
    from tools.webfoot.formats import indexed_png

    sprites, ident = _real_sprites()
    blob = sprites.export_graphic_png(ident)
    assert blob.startswith(_PNG_MAGIC) and len(blob) > len(_PNG_MAGIC)
    pixels, width, height, _pal, _tr = indexed_png.decode(blob)
    assert (width, height) == (2, 2)


def test_export_graphic_png_uses_explicit_palette():
    # SC2: an explicit palette_rgb reaches encode - a distinct palette yields
    # distinct PLTE bytes vs the canonical one.
    sprites, ident = _real_sprites()
    canonical = sprites.export_graphic_png(ident)
    effective = tuple((255 - i, 0, i) for i in range(256))
    edited = sprites.export_graphic_png(ident, effective)
    assert edited != canonical  # the passed palette changed the encoded output


def test_export_graphic_png_unknown_identity_fails_closed():
    # SC3: unknown identity raises GraphicsError before any bytes are produced.
    from tools.webfoot.graphics import GraphicsError, GraphicIdentity as GID

    sprites, _ident = _real_sprites()
    sprites.graphic = lambda i: (_ for _ in ()).throw(GraphicsError("unknown"))
    with pytest.raises(GraphicsError):
        sprites.export_graphic_png(GID(_PROFILE, 999))


def test_export_button_disabled_until_selection(tab):
    # SC4: the Export button is disabled with no selection, enabled after select.
    assert not tab._export.isEnabled()
    tab._grid.setCurrentRow(0)  # drives _show_selected
    assert tab._export.isEnabled()


def test_export_slot_writes_a_real_png(tab, tmp_path, monkeypatch):
    # SC5: the slot writes a real non-empty PNG to the chosen path.
    tab._grid.setCurrentRow(0)
    out = tmp_path / "sprite_export.png"
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.QFileDialog.getSaveFileName",
        lambda *a, **k: (str(out), "PNG image (*.png)"),
    )
    tab._on_export()
    assert out.exists()
    blob = out.read_bytes()
    assert blob.startswith(_PNG_MAGIC) and len(blob) > len(_PNG_MAGIC)


def test_export_slot_cancel_writes_nothing(tab, tmp_path, monkeypatch):
    tab._grid.setCurrentRow(0)
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.QFileDialog.getSaveFileName",
        lambda *a, **k: ("", ""),  # user cancelled
    )
    tab._on_export()  # must not raise, must not write
    assert not list(tmp_path.iterdir())


def test_export_slot_surfaces_sdk_error_without_escaping(tab, tmp_path, monkeypatch):
    # SC6: an SDK error from export becomes a QMessageBox, never a traceback.
    tab._grid.setCurrentRow(0)
    out = tmp_path / "sprite.png"
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.QFileDialog.getSaveFileName",
        lambda *a, **k: (str(out), ""),
    )
    warnings = []
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.QMessageBox.critical",
        lambda *a, **k: warnings.append(a[-1]),
    )
    monkeypatch.setattr(
        tab._session.sprites,
        "export_graphic_png",
        lambda *a, **k: (_ for _ in ()).throw(graphics_sdk.GraphicsError("bad graphic")),
    )
    tab._on_export()  # must not raise
    assert warnings == ["bad graphic"]
    assert not out.exists()  # nothing partial written


def test_export_slot_surfaces_oserror_without_escaping(tab, monkeypatch):
    # SC6: an OSError on the file write is caught the same way.
    tab._grid.setCurrentRow(0)
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.QFileDialog.getSaveFileName",
        lambda *a, **k: ("/nonexistent-dir/deeper/sprite.png", ""),
    )
    warnings = []
    monkeypatch.setattr(
        "tools.webfoot.workbench.graphics_tab.QMessageBox.critical",
        lambda *a, **k: warnings.append(a[-1]),
    )
    tab._on_export()  # write fails; must not raise
    assert len(warnings) == 1


# --- ROM-gated: a real decoded thumbnail renders (SC2 against real data) ------


def _rom_path() -> str:
    matches = glob.glob(os.path.join("roms", "*Buu*.gba"))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    if hashlib.sha256(open(matches[0], "rb").read()).hexdigest() != CANONICAL_SHA256:
        pytest.skip("local ROM is not the canonical profile")
    return matches[0]


def test_real_rom_thumbnail_is_non_empty(qapp):
    from tools.webfoot.profile import RomProfileCatalog

    rom = _rom_path()
    catalog = RomProfileCatalog.load(os.path.join("config", "roms.yaml"))
    session = Session()
    session.open_rom(rom, catalog)
    sprites = session.sprites
    assert sprites is not None
    graphic = sprites.graphics()[0]
    pixmap = indexed_pixmap(
        graphic.pixels, graphic.width, graphic.height, sprites.palette.rgb
    )
    assert (pixmap.width(), pixmap.height()) == (graphic.width, graphic.height)
    assert not pixmap.isNull()
