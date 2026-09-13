"""WORKBENCH-003 Phase-12 integration: the scene-authoring façade composes
through the ordinary SDK build lifecycle end to end.

`test_authored_scene_rom.py` already proves that ONE authored scene composes -
but it authors by calling `clone_placement` (the low-level writer) directly with
a HARD-CODED template placement, plus a hand-set scene text. What it does NOT
prove is the path the Workbench Scene tab actually drives: discover a clone
source through the public `scene` façade (`clone_source_candidates` filtered by
placement type, `trigger_options` gate), then author through `scene.add_authored_npc`.

This module pins THAT composed path as a regression: extract -> discover a
placement_type:0086 source via the façade -> add_authored_npc with an on_defeat
trigger and an authored `show_centered_sprite_text` script -> validate -> build ->
generated ROM, with canonical-ROM protection and determinism asserted. It reuses
the existing test's ROM-gating, build invocation and canonical-safety shape
rather than inventing new ones; it does not re-assert the byte-level engine-chain
reachability that test already covers.

The clone source is DISCOVERED, never hard-coded (SC4): the façade is asked which
placements resolve to the qualifying type, and the first is used. If the ROM ever
stops having a type:0086 placement on map 40, this test fails loudly at discovery
rather than silently authoring against a stale identity.

When the canonical ROM is absent this module SKIPS the build body cleanly (same
guard as test_authored_scene_rom.py) and the synthetic-fixture test below still
exercises the non-build façade composition headless.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tests.unit.test_placement_types import types  # shared synthetic graph fixture
from tools.webfoot import scene
from tools.webfoot.build import (
    build_project,
    extract_project,
    validate_project,
)
from tools.webfoot.maps import load_maps
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import read_project
from tools.webfoot.project.placements import BehaviorTrigger


LOCAL_ROM = Path(os.environ.get(
    "WEBFOOT_BUU_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))
CATALOG_PATH = "config/roms.yaml"
CANONICAL_SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

TARGET_MAP = "map:0040"
NAME = "scene"
POSITION = (176, 176)
#: The settled scene: clone a CONFIRMED_ENEMY_STAT_LINK source (type:0086),
#: attach on_defeat + an authored centred-sprite-text script.
REQUIRE_TYPE_SUFFIX = "placement_type:0086"
SCRIPT = ("show_centered_sprite_text text:1525 120 105", "terminate")
EXPECTED_SIZE = 8_388_608


_needs_rom = pytest.mark.skipif(
    not LOCAL_ROM.exists(), reason="canonical Buu's Fury image not present")


@pytest.fixture(scope="module")
def catalog():
    return RomProfileCatalog.load(CATALOG_PATH)


def _discover_source(maps) -> str:
    """The clone source, DISCOVERED via the façade rather than hard-coded (SC4)."""
    require_type = f"{maps.profile.id}/{REQUIRE_TYPE_SUFFIX}"
    candidates = scene.clone_source_candidates(
        maps, TARGET_MAP, require_type=require_type)
    assert candidates, (
        f"no {require_type} clone source on {TARGET_MAP}; the settled scene "
        "cannot be authored against this ROM")
    return candidates[0]["identity"]


def _author_through_facade(root: Path, catalog) -> str:
    """The whole composed authoring path the Scene tab drives, façade only."""
    extract_project(LOCAL_ROM, root, catalog, graphics=False)
    maps = load_maps(LOCAL_ROM, catalog)
    source = _discover_source(maps)
    # The trigger the GUI would offer must actually be offered for this source.
    assert BehaviorTrigger.ON_DEFEAT.value in scene.trigger_options(maps, source)
    return scene.add_authored_npc(
        root,
        TARGET_MAP,
        source,
        NAME,
        POSITION,
        behavior=f"{TARGET_MAP}/authored:{NAME}/behavior",
        script=SCRIPT,
        trigger=BehaviorTrigger.ON_DEFEAT.value,
        maps=maps,
    )


def _build(root: Path, output: Path, catalog):
    report = validate_project(root, LOCAL_ROM, catalog)
    assert report.passed, report.problems
    result = build_project(root, LOCAL_ROM, output, catalog)
    return result, output.read_bytes()


@_needs_rom
def test_facade_scene_composes_through_the_build_lifecycle(tmp_path, catalog):
    """extract -> façade discover+author -> validate -> build -> generated ROM.

    Asserts the composition claim (SC1/SC3): validate passes, build succeeds,
    the output is the full ROM size, the source ROM is byte-for-byte unchanged
    across the build, and a second identical author+build is deterministic.
    """
    canonical_before = LOCAL_ROM.read_bytes()
    assert hashlib.sha256(canonical_before).hexdigest() == CANONICAL_SHA

    identity = _author_through_facade(tmp_path / "p1", catalog)
    assert identity == f"{TARGET_MAP}/authored:{NAME}"

    # The authored declaration is present in the project the build reads.
    clone, = read_project(tmp_path / "p1").maps[40]["authored_placements"]
    assert clone.identity == identity
    assert clone.trigger is BehaviorTrigger.ON_DEFEAT
    assert clone.script == SCRIPT

    result, image = _build(tmp_path / "p1", tmp_path / "o1.gba", catalog)
    assert result.output_path.exists()
    assert len(image) == EXPECTED_SIZE

    # Canonical ROM protection: the source is untouched by the build.
    assert LOCAL_ROM.read_bytes() == canonical_before
    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == CANONICAL_SHA

    # Determinism: an independent identical author+build yields the same bytes.
    _identity2 = _author_through_facade(tmp_path / "p2", catalog)
    _result2, image2 = _build(tmp_path / "p2", tmp_path / "o2.gba", catalog)
    assert hashlib.sha256(image).hexdigest() == hashlib.sha256(image2).hexdigest()


# --- headless, ROM-free portion (runs even when the ROM is absent) -----------
# The module-level skipif gates the build tests above. This one uses the shared
# synthetic map/type graph so the façade-composition wiring (discover -> gate ->
# author -> reload) is exercised headless with no canonical ROM. It mirrors the
# unit fixtures rather than duplicating them: the point here is the ordered
# discover+gate+author call chain as one path, not each call alone.


def test_facade_composition_headless_on_synthetic_maps(tmp_path, monkeypatch, types):
    from tools.webfoot import build as build_module
    from tools.webfoot.project import ProjectMeta, read_project, write_project

    maps = types.maps
    profile_id = maps.profile.id
    monkeypatch.setattr(scene, "BEHAVIOR_TRIGGER_CONTRACTS", {profile_id: {
        "sha256": maps.profile.sha256,
        "on_defeat": {
            "placement_type": f"{profile_id}/placement_type:0001",
            "required_classification": "CONFIRMED_ENEMY_STAT_LINK",
            "binding": "placement_record_descriptor_pointer",
            "evidence": "synthetic",
        },
    }})

    meta = ProjectMeta(1, profile_id, maps.profile.game, maps.profile.sha256,
                       len(maps.base_bytes), "scene-synth")
    write_project(tmp_path, meta, enemies=[], characters=[],
                  maps=build_module._map_documents(maps))

    require_type = f"{profile_id}/placement_type:0001"
    candidates = scene.clone_source_candidates(maps, "map:0000", require_type=require_type)
    assert candidates, "synthetic type:0001 source must be discoverable"
    source = candidates[0]["identity"]
    assert BehaviorTrigger.ON_DEFEAT.value in scene.trigger_options(maps, source)

    identity = scene.add_authored_npc(
        tmp_path, "map:0000", source, "wolf", (12, 34),
        behavior="map:0000/authored:wolf/behavior", script=SCRIPT,
        trigger=BehaviorTrigger.ON_DEFEAT.value, maps=maps)
    assert identity == "map:0000/authored:wolf"
    reloaded, = read_project(tmp_path).maps[0]["authored_placements"]
    assert reloaded.identity == identity
    assert reloaded.trigger is BehaviorTrigger.ON_DEFEAT
