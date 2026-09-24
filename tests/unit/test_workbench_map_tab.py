"""Focused interaction tests for WORKBENCH-006's visual Map workspace."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
from PySide6.QtCore import QPoint, Qt  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402

from tests.unit.test_placement_types import types  # noqa: E402,F401
from tools.webfoot import build, map_render, scene  # noqa: E402
from tools.webfoot.project import ProjectError, ProjectMeta, read_project, write_project  # noqa: E402
from tools.webfoot.workbench import map_tab as mt  # noqa: E402
from tools.webfoot.workbench.map_tab import MapWorkspaceTab  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def project(tmp_path, types):
    maps = types.maps
    meta = ProjectMeta(1, maps.profile.id, maps.profile.game, maps.profile.sha256,
                       len(maps.base_bytes), "map-tab-test")
    write_project(tmp_path, meta, enemies=[], characters=[], maps=build._map_documents(maps))
    return tmp_path


@pytest.fixture
def render_result():
    palette = tuple((index, index, index) for index in range(256))
    pixels = bytes([17]) * (512 * 512)
    layer = map_render.RenderedLayer(
        bg=0, priority=0, char_base_block=0, screen_base_block=0,
        width=512, height=512, pixels=pixels,
    )
    return map_render.MapRenderResult(
        semantic_map_id="map:0000", width=512, height=512,
        layers=(layer,), composite=pixels, palette=palette, provenance={"source": "synthetic"},
    )


@pytest.fixture
def tab(qapp, project, types, render_result, monkeypatch):
    calls = []

    def render(_rom, map_id, **_kwargs):
        """Stub matching the real signature, which now takes `profile=`."""
        calls.append(map_id)
        return render_result

    monkeypatch.setattr(mt.map_render, "render_map", render)
    scene.set_placement_map_position(
        project, types.maps, "map:0000/placement:0000", (100, 100)
    )
    value = MapWorkspaceTab(Session(maps=types.maps, rom_image=b"synthetic"))
    value._session.set_project(project)
    value.on_session_changed()
    value._render_calls = calls
    return value


def test_overlay_selection_and_layer_controls_use_sdk_rows(tab):
    identity = "map:0000/placement:0000"
    marker = tab._markers[identity]
    assert (marker.pos().x(), marker.pos().y()) == (100, 100)
    assert tab._layers.itemText(0) == "Retail composite"
    assert tab._layers.itemText(1) == "BG0"

    tab._select_marker(identity)

    assert tab._identity.text() == identity
    assert tab._position.text() == "X 100   Y 100"
    assert tab._open_scene.isEnabled()
    tab._scene.clearSelection()
    # With nothing selected the detail grid is gone entirely and one sentence
    # stands in for it: no dash rows, no "Unknown" scaffolding. `_identity` is
    # therefore cleared rather than set to a placeholder string. `isHidden` rather
    # than `isVisible`, because an unmapped parent reports every child invisible.
    assert tab._identity.text() == ""
    assert tab._placement_body.isHidden()
    assert not tab._placement_empty.isHidden()


def test_direct_drag_is_semantic_and_undoable(tab, project):
    identity = "map:0000/placement:0000"
    emitted = []
    tab.projectChanged.connect(lambda: emitted.append(True))

    assert tab._on_marker_drag(identity, (100, 100), (112, 80))
    row = next(row for row in read_project(project).maps[0]["placements"] if row["index"] == 0)
    assert (row["position_low"], row["position_high"]) == (112, 80)
    assert tab._undo_stack.count() == 1
    assert tab._position.text() == "X 112   Y 80"
    assert emitted == [True]
    assert len([item for item in tab._scene.items() if isinstance(item, mt.PlacementMarker)]) == len(tab._markers)

    tab._undo_stack.undo()
    row = next(row for row in read_project(project).maps[0]["placements"] if row["index"] == 0)
    assert (row["position_low"], row["position_high"]) == (100, 100)
    tab._undo_stack.redo()
    row = next(row for row in read_project(project).maps[0]["placements"] if row["index"] == 0)
    assert (row["position_low"], row["position_high"]) == (112, 80)
    assert len(emitted) == 3
    assert len([item for item in tab._scene.items() if isinstance(item, mt.PlacementMarker)]) == len(tab._markers)


def test_add_object_clones_at_selected_proven_map_position(tab, project, monkeypatch):
    identity = "map:0000/placement:0000"
    tab._select_marker(identity)
    monkeypatch.setattr(mt.QInputDialog, "getText", lambda *args: ("canvas-wolf", True))

    tab._on_add_object()

    clone, = read_project(project).maps[0]["authored_placements"]
    assert clone.identity == "map:0000/authored:canvas-wolf"
    assert (clone.position_low, clone.position_high) == (100, 100)
    assert clone.identity in tab._markers
    assert len([item for item in tab._scene.items() if isinstance(item, mt.PlacementMarker)]) == len(tab._markers)


def test_map_switch_zoom_and_layer_toggle_use_cached_render(tab):
    initial_calls = list(tab._render_calls)
    tab._canvas.zoom_in()
    tab._canvas.zoom_out()
    tab._layers.setCurrentIndex(1)
    assert tab._render_calls == initial_calls

    tab._maps.setCurrentRow(1)
    assert len(tab._render_calls) == len(initial_calls) + 1
    tab._maps.setCurrentRow(0)
    assert len(tab._render_calls) == len(initial_calls) + 1


def test_read_only_project_state_refuses_direct_mutation(qapp, types, render_result, monkeypatch):
    monkeypatch.setattr(mt.map_render, "render_map", lambda *_, **__: render_result)
    tab = MapWorkspaceTab(Session(maps=types.maps, rom_image=b"synthetic"))
    marker = tab._markers["map:0000/placement:0000"]

    assert not marker.flags() & marker.GraphicsItemFlag.ItemIsMovable
    assert not tab._add.isEnabled()


def test_out_of_range_drag_surfaces_error_without_recording_command(tab, monkeypatch):
    errors = []
    monkeypatch.setattr(mt.QMessageBox, "critical", lambda *args: errors.append(args[-1]))

    assert not tab._on_marker_drag("map:0000/placement:0000", (100, 100), (32768, 80))
    assert errors and "signed 16-bit" in errors[-1]
    assert tab._undo_stack.count() == 0


def test_off_map_marker_extends_scroll_bounds_but_fit_stays_on_retail_map(tab, project, qapp):
    identity = "map:0000/placement:0000"
    scene.set_placement_map_position(project, tab._session.maps, identity, (-48, 640))
    tab._populate_markers()
    marker = tab._markers[identity]

    assert tab._scene.sceneRect().contains(marker.sceneBoundingRect())
    tab.resize(900, 650)
    tab.show()
    qapp.processEvents()
    tab._canvas.fit_map()
    assert tab._canvas._fit_rect == mt.QRectF(0, 0, 512, 512)
    tab._select_marker(identity)
    qapp.processEvents()
    assert marker.isSelected()


def test_failed_undo_clears_history_without_lying_about_saved_position(tab, project, monkeypatch, qapp):
    identity = "map:0000/placement:0000"
    assert tab._on_marker_drag(identity, (100, 100), (112, 80))
    original = mt.scene_sdk.set_placement_map_position

    def refusing_undo(*args, **kwargs):
        position = kwargs.get("map_position", args[-1])
        if position == (100, 100):
            raise ProjectError("simulated project write failure")
        return original(*args, **kwargs)

    errors = []
    monkeypatch.setattr(mt.scene_sdk, "set_placement_map_position", refusing_undo)
    monkeypatch.setattr(mt.QMessageBox, "critical", lambda *args: errors.append(args[-1]))

    tab._undo_stack.undo()
    qapp.processEvents()

    row = next(row for row in read_project(project).maps[0]["placements"] if row["index"] == 0)
    assert (row["position_low"], row["position_high"]) == (112, 80)
    assert (tab._markers[identity].pos().x(), tab._markers[identity].pos().y()) == (112, 80)
    assert errors == ["simulated project write failure"]
    assert tab._undo_stack.count() == 0
    assert not tab._undo_button.isEnabled()
    assert not tab._redo_button.isEnabled()


def test_open_detailed_editor_preserves_semantic_selection(tab):
    opened = []
    tab.openSceneRequested.connect(lambda map_id, identity: opened.append((map_id, identity)))
    tab._select_marker("map:0000/placement:0000")

    tab._open_detailed_editor()

    assert opened == [("map:0000", "map:0000/placement:0000")]


def test_canvas_mouse_click_and_drag_commit_one_undo_step(tab, project, qapp):
    tab.resize(900, 650)
    tab.show()
    qapp.processEvents()
    marker = tab._markers["map:0000/placement:0000"]
    tab._canvas.centerOn(marker)
    point = tab._canvas.mapFromScene(marker.scenePos())

    QTest.mouseClick(tab._canvas.viewport(), Qt.MouseButton.LeftButton, pos=point)
    assert tab._identity.text() == marker.placement["identity"]

    destination = point + QPoint(30, 20)
    QTest.mousePress(tab._canvas.viewport(), Qt.MouseButton.LeftButton, pos=point)
    QTest.mouseMove(tab._canvas.viewport(), destination, 20)
    QTest.mouseRelease(tab._canvas.viewport(), Qt.MouseButton.LeftButton, pos=destination)

    row = next(row for row in read_project(project).maps[0]["placements"] if row["index"] == 0)
    assert (row["position_low"], row["position_high"]) != (100, 100)
    moved = tab._markers["map:0000/placement:0000"]
    assert (moved.pos().x(), moved.pos().y()) == (
        row["position_low"], row["position_high"]
    )
    assert tab._undo_stack.count() == 1
