"""Headless Workbench Scene-tab controller/state tests (WORKBENCH-003).

Reuses the synthetic map/type graph (`types` fixture from test_placement_types)
so no canonical ROM bytes are needed: it carries a type-0001 source classified
CONFIRMED_ENEMY_STAT_LINK and a type-0003 source classified UNKNOWN_CATEGORY,
which is exactly the distinction the on_defeat trigger gate turns on.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from tests.unit.test_placement_types import types  # noqa: E402,F401  shared fixture
from tools.webfoot import build, scene  # noqa: E402
from tools.webfoot.project import ProjectMeta, read_project, write_project  # noqa: E402
from tools.webfoot.project.placements import BehaviorTrigger  # noqa: E402
from tools.webfoot.workbench.scene_tab import SceneTab  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def project(tmp_path, types):
    maps = types.maps
    meta = ProjectMeta(1, maps.profile.id, maps.profile.game, maps.profile.sha256,
                       len(maps.base_bytes), "scene-tab-test")
    write_project(tmp_path, meta, enemies=[], characters=[],
                  maps=build._map_documents(maps))
    return tmp_path


@pytest.fixture
def with_on_defeat(monkeypatch, types):
    """Register the synthetic type-0001 as the on_defeat-qualifying type.

    Mirrors test_scene_authoring: the real contract keys the Buu profile/type:0086;
    this maps the same contract shape onto the synthetic profile so the trigger
    gate is provable against synthetic data.
    """
    profile_id = types.maps.profile.id
    contract = {profile_id: {
        "sha256": types.maps.profile.sha256,
        "on_defeat": {
            "placement_type": f"{profile_id}/placement_type:0001",
            "required_classification": "CONFIRMED_ENEMY_STAT_LINK",
            "binding": "placement_record_descriptor_pointer",
            "evidence": "synthetic",
        },
    }}
    monkeypatch.setattr(scene, "BEHAVIOR_TRIGGER_CONTRACTS", contract)
    return types


@pytest.fixture
def session(types, project):
    value = Session(maps=types.maps)
    value.set_project(project)
    return value


@pytest.fixture
def tab(qapp, session):
    return SceneTab(session)


def _select_source(tab, identity):
    index = tab._source_select.findData(identity)
    assert index >= 0, f"source {identity} not offered"
    tab._source_select.setCurrentIndex(index)


# --- population --------------------------------------------------------------


def test_map_selector_lists_authorable_maps(tab):
    data = [tab._map_select.itemData(i) for i in range(tab._map_select.count())]
    assert data == ["map:0000", "map:0001"]


def test_selecting_map_populates_placements_and_sources(tab):
    # Default selection is map:0000, which has two placements.
    assert tab._placements.rowCount() == 2
    assert tab._placements.item(0, 0).text() == "map:0000/placement:0000"
    sources = [tab._source_select.itemData(i) for i in range(tab._source_select.count())]
    assert sources == ["map:0000/placement:0000", "map:0000/placement:0001"]


def test_trigger_options_reflect_source_type(qapp, project, with_on_defeat):
    session = Session(maps=with_on_defeat.maps)
    session.set_project(project)
    tab = SceneTab(session)
    # Qualifying source (type:0001, CONFIRMED_ENEMY_STAT_LINK) offers on_defeat.
    _select_source(tab, "map:0000/placement:0000")
    triggers = [tab._trigger_select.itemData(i) for i in range(tab._trigger_select.count())]
    assert BehaviorTrigger.ON_DEFEAT.value in triggers
    # Non-qualifying source (type:0003, UNKNOWN_CATEGORY) offers none.
    _select_source(tab, "map:0000/placement:0001")
    triggers = [tab._trigger_select.itemData(i) for i in range(tab._trigger_select.count())]
    assert triggers == [None]


def test_authored_script_input_is_available(tab):
    data = [tab._behavior_select.itemData(i) for i in range(tab._behavior_select.count())]
    assert "__authored_script__" in data


# --- Apply success -----------------------------------------------------------


def test_apply_writes_emits_and_invalidates_state(tab, session, project):
    session.record_validation(True)
    session.last_build = object()
    session.build_revision = session.project_revision
    assert session.validation_current and session.build_current
    before = session.project_revision

    emitted = []
    tab.projectChanged.connect(lambda: emitted.append(True))

    _select_source(tab, "map:0000/placement:0000")
    tab._name.setText("wolf")
    tab._pos_low.setValue(123)
    tab._pos_high.setValue(456)
    tab._on_apply()

    assert emitted == [True]
    assert session.project_revision == before + 1
    assert not session.validation_current
    assert not session.build_current
    reloaded, = read_project(project).maps[0]["authored_placements"]
    assert reloaded.identity == "map:0000/authored:wolf"
    assert (reloaded.position_low, reloaded.position_high) == (123, 456)


def test_apply_authored_script_sets_behavior_and_terminates(tab, session, project, monkeypatch):
    """The authored-script Apply path must set a non-None authored behavior AND a
    script ending in `terminate`. Pre-fix, behavior stayed None and clone_placement
    raised (placements.py:90), so this drove the QMessageBox instead of a write.
    """
    calls = {}
    real = scene.add_authored_npc

    def spy(project_dir, map_id, source, name, position, **kwargs):
        calls["map_id"] = map_id
        calls["behavior"] = kwargs.get("behavior")
        calls["script"] = kwargs.get("script")
        return real(project_dir, map_id, source, name, position, **kwargs)

    monkeypatch.setattr("tools.webfoot.workbench.scene_tab.scene_sdk.add_authored_npc", spy)

    emitted = []
    tab.projectChanged.connect(lambda: emitted.append(True))
    before = session.project_revision

    _select_source(tab, "map:0000/placement:0000")
    tab._name.setText("wolf")
    idx = tab._behavior_select.findData("__authored_script__")
    tab._behavior_select.setCurrentIndex(idx)
    tab._script_text.setValue(1525)
    tab._script_x.setValue(120)
    tab._script_y.setValue(105)
    tab._on_apply()

    assert calls["behavior"] == "map:0000/authored:wolf/behavior"
    assert calls["script"][-1] == "terminate"
    assert calls["script"][0].startswith("show_centered_sprite_text text:1525 120 105")
    assert emitted == [True]
    assert session.project_revision == before + 1


# --- Apply error discipline (WORKBENCH-001 lesson) ---------------------------


def test_apply_rejected_input_surfaces_error_without_escaping(tab, session, project, monkeypatch):
    warnings = []
    monkeypatch.setattr(
        "tools.webfoot.workbench.scene_tab.QMessageBox.critical",
        lambda *a, **k: warnings.append(a[-1]),
    )
    emitted = []
    tab.projectChanged.connect(lambda: emitted.append(True))
    before = session.project_revision

    _select_source(tab, "map:0000/placement:0000")
    tab._name.setText("wolf")
    # Empty name would be one rejection; use a duplicate to force a facade reject:
    tab._on_apply()  # first add succeeds
    tab._on_apply()  # second add of the same name -> ProjectError, must be caught

    # The second Apply must not raise, must show a QMessageBox, must not emit.
    assert warnings, "rejected input did not surface a QMessageBox"
    assert len(emitted) == 1  # only the first (successful) add emitted
    assert session.project_revision == before + 1  # only the first add advanced state
