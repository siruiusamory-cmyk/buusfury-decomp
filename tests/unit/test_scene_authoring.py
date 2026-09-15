"""WORKBENCH semantic scene-authoring façade tests; no committed ROM bytes.

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
from tools.webfoot.project import (
    ProjectMeta,
    read_project,
    write_dialogue_replacements,
    write_project,
)
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
    monkeypatch.setattr(scene, "SCRIPT_EFFECTS", {profile_id: {
        "show_centered_sprite_text": {
            "text_count": 1534,
            "coordinate_ranges": {"x": (0, 239), "y": (0, 159)},
        },
    }})
    return types


# --- reads -------------------------------------------------------------------


def test_list_authorable_maps_reports_placement_counts(types):
    maps_list = scene.list_authorable_maps(types.maps)
    assert [m["identity"] for m in maps_list] == ["map:0000", "map:0001"]
    assert maps_list[0]["placement_count"] == 2
    assert maps_list[1]["placement_count"] == 1


def test_map_browser_reports_semantic_support_states(with_on_defeat):
    maps_list = scene.list_maps(with_on_defeat.maps)
    by_id = {item["identity"]: item for item in maps_list}
    assert by_id["map:0000"]["support"] == "Editable"
    assert by_id["map:0000"]["label"] == "map:0000"
    assert "address" not in by_id["map:0000"]


def test_map_browser_keeps_unsupported_map_visible_and_read_only(monkeypatch, types):
    class EmptyMaps:
        profile = types.maps.profile

        @staticmethod
        def entries():
            return types.maps.entries()

        @staticmethod
        def map_placements(_identity):
            return ()

        @staticmethod
        def placements():
            return ()

    monkeypatch.setattr(scene, "_placement_types", lambda _maps: None)
    result = scene.list_maps(EmptyMaps())
    assert result
    assert all(item["support"] == "Read-only" for item in result)
    assert all(item["placement_count"] == 0 for item in result)


def test_map_placements_annotate_type_and_classification(types):
    placements = scene.map_placements(types.maps, "map:0000")
    assert [p["identity"] for p in placements] == [
        "map:0000/placement:0000", "map:0000/placement:0001"]
    assert placements[0]["placement_type"].endswith("placement_type:0001")
    assert placements[0]["classification"] == "CONFIRMED_ENEMY_STAT_LINK"
    assert placements[1]["placement_type"].endswith("placement_type:0003")
    assert placements[1]["classification"] == "UNKNOWN_CATEGORY"
    assert all(p["is_clone_source"] for p in placements)
    assert (placements[0]["position_x"], placements[0]["position_y"]) == (86, 4660)


def test_map_placements_bad_map_fails_closed(types):
    with pytest.raises(SceneAuthoringError):
        scene.map_placements(types.maps, "map:9999")
    with pytest.raises(SceneAuthoringError):
        scene.map_placements(types.maps, "not-a-map")


def test_placement_relationships_use_semantic_identities(types):
    relationships = scene.placement_relationships(
        types.maps, "map:0000/placement:0000"
    )
    assert relationships["placement"] == "map:0000/placement:0000"
    assert relationships["entity_type"].endswith("placement_type:0001")
    assert relationships["classification"] == "CONFIRMED_ENEMY_STAT_LINK"
    assert relationships["dialogue"] is None
    assert "file_offset" not in relationships


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


def test_add_authored_npc_at_encodes_signed_map_coordinates(project, types):
    identity = scene.add_authored_npc_at(
        project, "map:0000", "map:0000/placement:0000", "edge", (-1, -32768)
    )
    reloaded, = read_project(project).maps[0]["authored_placements"]
    assert reloaded.identity == identity
    assert (reloaded.position_low, reloaded.position_high) == (0xFFFF, 0x8000)
    row = next(item for item in scene.scene_placements(types.maps, "map:0000", project)
               if item["identity"] == identity)
    assert (row["position_x"], row["position_y"]) == (-1, -32768)


def test_set_placement_map_position_uses_confirmed_inverse_transform(project, types):
    identity = "map:0000/placement:0000"

    assert scene.set_placement_map_position(
        project, types.maps, identity, (-16, 80)
    ) is True
    assert scene.set_placement_map_position(
        project, types.maps, identity, (-16, 80)
    ) is False

    row = next(
        row for row in read_project(project).maps[0]["placements"]
        if row["index"] == 0
    )
    assert (row["position_low"], row["position_high"]) == (0xFFF0, 80)
    rendered = next(
        row for row in scene.scene_placements(types.maps, "map:0000", project)
        if row["identity"] == identity
    )
    assert (rendered["position_x"], rendered["position_y"]) == (-16, 80)
    change = next(
        value for value in scene.pending_changes(project, types.maps)
        if value.object_identity == identity
    )
    assert change.summary == "Moved placement on map:0000"
    assert change.details == ("X 86 → -16", "Y 4660 → 80")


@pytest.mark.parametrize("position", [(32768, 0), (0, -32769), (1.5, 0)])
def test_set_placement_map_position_rejects_out_of_range_without_write(project, types, position):
    before = (project / "maps" / "maps.toml").read_bytes()

    with pytest.raises(SceneAuthoringError, match="signed 16-bit"):
        scene.set_placement_map_position(
            project, types.maps, "map:0000/placement:0000", position
        )

    assert (project / "maps" / "maps.toml").read_bytes() == before


def test_pending_change_is_semantic_and_revert_removes_authored_placement(
    project, types
):
    identity = scene.add_authored_npc(
        project, "map:0000", "map:0000/placement:0000", "wolf", (123, 456)
    )
    changes = scene.pending_changes(project, types.maps)
    change = next(item for item in changes if item.object_identity == identity)
    assert change.revertible
    assert change.summary == "Added placement map:0000/authored:wolf to map:0000"
    assert "offset" not in " ".join((change.summary, *change.details)).lower()

    assert scene.revert_pending_change(project, types.maps, change.identity)
    assert read_project(project).maps[0].get("authored_placements", ()) == ()


def test_scene_placements_and_relationships_include_authored_project_content(
    project, types
):
    identity = scene.add_authored_npc(
        project, "map:0000", "map:0000/placement:0000", "wolf", (123, 456),
        behavior="map:0000/authored:wolf/behavior",
        script=("show_centered_sprite_text text:0001 10 20", "terminate"),
    )

    placements = scene.scene_placements(types.maps, "map:0000", project)
    authored = next(item for item in placements if item["identity"] == identity)
    assert authored["provenance"] == "Project"
    assert authored["position_low"] == 123
    relationships = scene.placement_relationships(types.maps, identity, project)
    assert relationships["clone_from"] == "map:0000/placement:0000"
    assert relationships["entity"]
    assert relationships["behavior"] == "map:0000/authored:wolf/behavior"
    assert relationships["script"] == "map:0000/authored:wolf/behavior/script"
    assert "offset" not in repr(relationships).lower()


def test_pending_change_revert_invalid_identity_fails_closed(project, types):
    with pytest.raises(SceneAuthoringError, match="cannot be reverted"):
        scene.revert_pending_change(project, types.maps, "placement-edit:map:0000")


def test_unknown_dialogue_change_is_not_advertised_as_revertible(project, types):
    write_dialogue_replacements(project, {"not-a-registered-target": "Hello"})

    change = next(
        item for item in scene.pending_changes(project, types.maps)
        if item.identity == "dialogue:not-a-registered-target"
    )

    assert not change.revertible


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
