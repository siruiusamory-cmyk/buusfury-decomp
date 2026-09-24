"""TOOLKIT-034 semantic trigger representation and evidence gates."""
from types import SimpleNamespace

import pytest

from tests.unit.test_authored_placements import add, project  # shared project fixture
from tests.unit.test_placement_types import types
from tools.webfoot.authored_placements import (
    AuthoredTriggerError,
    PlannedPlacement,
    _require_trigger_contract,
)
from tools.webfoot.cli import main
from tools.webfoot.data.behavior_triggers import BEHAVIOR_TRIGGER_CONTRACTS
from tools.webfoot.entities import PlacementTypeIdentity
from tools.webfoot.project import ProjectError, read_project
from tools.webfoot.project.format import load_toml
from tools.webfoot.project.placements import AuthoredPlacement, BehaviorTrigger


PROFILE = "buus_fury_usa_rev0_01c1707f"
SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
TYPE = f"{PROFILE}/placement_type:0086"
IDENTITY = "map:0000/authored:enemy"
BEHAVIOR = f"{IDENTITY}/behavior"
SCRIPT = ("terminate",)


def placement(*, trigger="on_defeat", behavior=BEHAVIOR):
    return AuthoredPlacement(
        IDENTITY,
        0,
        "map:0000/placement:0000",
        10,
        20,
        behavior=behavior,
        script=SCRIPT if behavior == BEHAVIOR else None,
        trigger=trigger,
    )


def maps(profile=PROFILE, sha256=SHA256):
    """A stand-in `Maps` carrying the two facts the trigger gate reads.

    `profile.sha256` is the profile's declared identity, which is what the gate
    compares a contract against; `identification.hashes.sha256` is the loaded
    image's hash, which is what the stand-in previously carried. Both are set to
    the same value here so the fixture models a matched profile, and a case that
    wants to model a mismatched one overrides `sha256`.
    """
    return SimpleNamespace(
        profile=SimpleNamespace(id=profile, sha256=sha256),
        identification=SimpleNamespace(hashes=SimpleNamespace(sha256=sha256)),
    )


def trigger_types(*, selector=86, enemy=True):
    item = SimpleNamespace(
        identity=PlacementTypeIdentity(PROFILE, selector),
        enemy_identity=(SimpleNamespace(key=434) if enemy else None),
        original_bytes=(bytes(28) if enemy else None),
        classification=("CONFIRMED_ENEMY_STAT_LINK" if enemy else "UNKNOWN_CATEGORY"),
    )
    return SimpleNamespace(type_of=lambda source_id: item)


def test_trigger_is_one_stable_semantic_enum_value():
    assert tuple(BehaviorTrigger) == (BehaviorTrigger.ON_DEFEAT,)
    assert BehaviorTrigger.ON_DEFEAT.value == "on_defeat"
    assert set(BEHAVIOR_TRIGGER_CONTRACTS) == {PROFILE}
    assert set(BEHAVIOR_TRIGGER_CONTRACTS[PROFILE]) == {"sha256", "on_defeat"}
    assert BEHAVIOR_TRIGGER_CONTRACTS[PROFILE]["on_defeat"]["placement_type"] == TYPE


@pytest.mark.parametrize("value", ["defeat", "on_kill", "0x08011A5A", 86, True])
def test_raw_unknown_and_unsupported_trigger_values_are_rejected(value):
    with pytest.raises(ProjectError, match="trigger must be exactly 'on_defeat'"):
        placement(trigger=value)


def test_trigger_requires_a_declared_behavior():
    with pytest.raises(ProjectError, match="requires a behavior"):
        placement(behavior=None)


def test_trigger_round_trips_through_normal_project_source(project):
    clone = add(project, name="enemy", behavior=BEHAVIOR, script=list(SCRIPT),
                trigger="on_defeat")
    row = load_toml((project / "maps/maps.toml").read_text())["map"]["map:0000"][
        "authored_placements"][IDENTITY]
    assert row["trigger"] == "on_defeat"
    reloaded, = read_project(project).maps[0]["authored_placements"]
    assert reloaded == clone
    assert reloaded.trigger is BehaviorTrigger.ON_DEFEAT


def test_cli_clone_accepts_the_exact_trigger(project, capsys):
    assert main([
        "placement", "clone", str(project), "--map", "map:0000", "--source",
        "map:0000/placement:0000", "--name", "enemy", "--position-low", "10",
        "--position-high", "20", "--behavior", "map:0428/placement:0000/descriptor",
        "--trigger", "on_defeat",
    ]) == 0
    assert capsys.readouterr().out.strip() == IDENTITY
    reloaded, = read_project(project).maps[0]["authored_placements"]
    assert reloaded.trigger is BehaviorTrigger.ON_DEFEAT


def test_supported_type_and_confirmed_enemy_link_satisfy_contract():
    clone = placement()
    catalog = trigger_types()
    assert _require_trigger_contract(clone, maps(), object(), catalog) is catalog


def test_non_whitelisted_enemy_linked_type_is_rejected():
    with pytest.raises(AuthoredTriggerError, match="requires canonical template type"):
        _require_trigger_contract(placement(), maps(), object(), trigger_types(selector=85))


def test_whitelisted_type_without_confirmed_enemy_link_is_rejected():
    with pytest.raises(AuthoredTriggerError, match="CONFIRMED enemy-stat link"):
        _require_trigger_contract(placement(), maps(), object(), trigger_types(enemy=False))


@pytest.mark.parametrize("profile,sha256", [
    ("synthetic_exact", SHA256),
    (PROFILE, "0" * 64),
])
def test_unverified_profile_or_revision_has_no_trigger_contract(profile, sha256):
    with pytest.raises(AuthoredTriggerError, match="has no evidence contract"):
        _require_trigger_contract(placement(), maps(profile, sha256), object(), trigger_types())


def test_trigger_is_planning_attribution_not_a_second_binary_field():
    row = PlannedPlacement(
        IDENTITY,
        "AUTHORED_CLONE",
        "map:0000/placement:0000",
        bytes(32),
        behavior=BEHAVIOR,
        inherited_descriptor_raw=0x080555A0,
        descriptor_pointer_raw=0x087EA420,
        script_body=b"\x11",
        trigger=BehaviorTrigger.ON_DEFEAT,
    )
    assert row.to_json()["trigger"] == "on_defeat"
    legacy = PlannedPlacement("map:0000/authored:legacy", "AUTHORED_CLONE",
                              "map:0000/placement:0000", bytes(32))
    assert "trigger" not in legacy.to_json()
