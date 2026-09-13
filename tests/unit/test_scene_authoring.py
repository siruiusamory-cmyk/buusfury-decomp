"""WORKBENCH-003 public scene-authoring façade tests; no committed ROM bytes.

The synthetic map/type graph is the shared `types` fixture from
`test_placement_types.py`: two maps, a type-0001 source classified
CONFIRMED_ENEMY_STAT_LINK and a type-0003 source classified UNKNOWN_CATEGORY.
That is exactly the distinction the on_defeat trigger gate turns on, so the
qualifying/non-qualifying proof needs no canonical ROM.
"""

from __future__ import annotations

import pytest

from tests.unit.test_placement_types import types  # shared synthetic graph fixture
from tools.webfoot import build
from tools.webfoot import scene
from tools.webfoot.project import ProjectMeta, read_project, write_project
from tools.webfoot.project.placements import BehaviorTrigger
from tools.webfoot.scene import SceneAuthoringError
from tools.webfoot.workbench.session import Session


@pytest.fixture
def project(tmp_path, types):
    maps = types.maps
    meta = ProjectMeta(1, maps.profile.id, maps.profile.game, maps.profile.sha256,
                       len(maps.base_bytes), "scene-test")
    write_project(tmp_path, meta, enemies=[], characters=[],
                  maps=build._map_documents(maps))
    return tmp_path


@pytest.fixture
def with_on_defeat(monkeypatch, types):
    """Declare the synthetic type-0001 as the on_defeat-qualifying type.

    The real contract keys on the Buu profile and type:0086; the synthetic graph
    uses type:0001. Registering the same contract shape against the synthetic
    profile lets the trigger gate be proven against synthetic data.
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


# --- reads -------------------------------------------------------------------


def test_list_authorable_maps_reports_placement_counts(types):
    maps_list = scene.list_authorable_maps(types.maps)
    assert [m["identity"] for m in maps_list] == ["map:0000", "map:0001"]
    assert maps_list[0]["placement_count"] == 2
    assert maps_list[1]["placement_count"] == 1


def test_map_placements_annotate_type_and_classification(types):
    placements = scene.map_placements(types.maps, "map:0000")
    assert [p["identity"] for p in placements] == [
        "map:0000/placement:0000", "map:0000/placement:0001"]
    assert placements[0]["placement_type"].endswith("placement_type:0001")
    assert placements[0]["classification"] == "CONFIRMED_ENEMY_STAT_LINK"
    assert placements[1]["placement_type"].endswith("placement_type:0003")
    assert placements[1]["classification"] == "UNKNOWN_CATEGORY"
    assert all(p["is_clone_source"] for p in placements)


def test_map_placements_bad_map_fails_closed(types):
    with pytest.raises(SceneAuthoringError):
        scene.map_placements(types.maps, "map:9999")
    with pytest.raises(SceneAuthoringError):
        scene.map_placements(types.maps, "not-a-map")


def test_clone_source_candidates_filter_by_type(types):
    profile_id = types.maps.profile.id
    everything = scene.clone_source_candidates(types.maps, "map:0000")
    assert len(everything) == 2
    only_enemy = scene.clone_source_candidates(
        types.maps, "map:0000", require_type=f"{profile_id}/placement_type:0001")
    assert [c["identity"] for c in only_enemy] == ["map:0000/placement:0000"]
    # A type that no placement on this map resolves to yields nothing (closed).
    assert scene.clone_source_candidates(
        types.maps, "map:0000", require_type=f"{profile_id}/placement_type:0003"
    ) == [{"identity": "map:0000/placement:0001",
           "placement_type": f"{profile_id}/placement_type:0003",
           "classification": "UNKNOWN_CATEGORY"}]


# --- trigger gate (SC4) ------------------------------------------------------


def test_on_defeat_only_offered_for_qualifying_source(with_on_defeat):
    types = with_on_defeat
    qualifying = "map:0000/placement:0000"   # type:0001, CONFIRMED_ENEMY_STAT_LINK
    non_qualifying = "map:0000/placement:0001"  # type:0003, UNKNOWN_CATEGORY
    assert scene.trigger_options(types.maps, qualifying) == [BehaviorTrigger.ON_DEFEAT.value]
    assert scene.trigger_options(types.maps, non_qualifying) == []


def test_no_contract_offers_no_triggers(types):
    # Without the monkeypatched contract, the synthetic profile has none.
    assert scene.trigger_options(types.maps, "map:0000/placement:0000") == []


# --- write (SC3) -------------------------------------------------------------


def test_add_authored_npc_writes_and_returns_identity(project, types):
    identity = scene.add_authored_npc(
        project, "map:0000", "map:0000/placement:0000", "wolf", (123, 456))
    assert identity == "map:0000/authored:wolf"
    reloaded, = read_project(project).maps[0]["authored_placements"]
    assert reloaded.identity == identity
    assert (reloaded.position_low, reloaded.position_high) == (123, 456)


@pytest.mark.parametrize("kwargs", [
    {"map_id": "map:9999"},                              # unknown map
    {"source_identity": "map:0000/placement:9999"},      # non-existent source
    {"position": (-1, 0)},                               # out-of-range low
    {"position": (0, 65536)},                            # out-of-range high
    {"source_identity": "garbage"},                      # unparseable source
    {"map_id": "garbage"},                               # unparseable map
])
def test_invalid_add_fails_closed_and_writes_nothing(project, kwargs):
    before = (project / "maps/maps.toml").read_bytes()
    args = dict(map_id="map:0000", source_identity="map:0000/placement:0000",
                name="wolf", position=(1, 2))
    args.update(kwargs)
    with pytest.raises(SceneAuthoringError):
        scene.add_authored_npc(project, **args)
    assert (project / "maps/maps.toml").read_bytes() == before


def test_unsupported_trigger_for_source_fails_closed(project, with_on_defeat):
    types = with_on_defeat
    before = (project / "maps/maps.toml").read_bytes()
    # placement:0001 is type-0003 (UNKNOWN) so on_defeat is not valid for it.
    with pytest.raises(SceneAuthoringError, match="not valid for source"):
        scene.add_authored_npc(
            project, "map:0000", "map:0000/placement:0001", "wolf", (1, 2),
            trigger="on_defeat", maps=types.maps)
    assert (project / "maps/maps.toml").read_bytes() == before


# --- Session wiring (SC2) ----------------------------------------------------


def test_session_scene_mutation_advances_revision_and_clears_state():
    session = Session()
    session.record_validation(True)
    session.last_build = object()
    session.build_revision = session.project_revision
    assert session.validation_current
    assert session.build_current

    before = session.project_revision
    session.scene_mutated()

    assert session.project_revision == before + 1
    assert not session.validation_current
    assert not session.build_current
    assert session.last_build is None


def test_session_has_scene_fields():
    session = Session()
    assert session.maps is None
    assert session.selected_map is None
