"""WORKBENCH-004 semantic workspace and second-map build acceptance."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot import scene
from tools.webfoot.binary import GbaRomAddress
from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.formats.map_placements import (
    DescriptorRecord,
    PlacementRecord,
    SCRIPT_DISPATCH_HANDLER,
)
from tools.webfoot.maps import load_maps
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import read_project
from tools.webfoot.project.placements import BehaviorTrigger


LOCAL_ROM = Path(os.environ.get(
    "WEBFOOT_BUU_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))
CANONICAL_SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
TARGET_MAP = "map:0041"
TYPE_SUFFIX = "placement_type:0086"
SCRIPT = ("show_centered_sprite_text text:1525 120 105", "terminate")


_needs_rom = pytest.mark.skipif(
    not LOCAL_ROM.exists(), reason="canonical Buu's Fury image not present")


@pytest.fixture(scope="module")
def catalog():
    return RomProfileCatalog.load("config/roms.yaml")


@_needs_rom
def test_real_map_inventory_classifies_second_acceptance_map(catalog):
    maps = load_maps(LOCAL_ROM, catalog)
    inventory = {item["identity"]: item for item in scene.list_maps(maps)}

    assert len(inventory) == 452
    assert inventory[TARGET_MAP]["support"] == "Editable"
    assert inventory[TARGET_MAP]["placement_count"] == 3
    assert inventory["map:0010"]["support"] == "Partial"
    assert any(item["support"] == "Read-only" for item in inventory.values())
    assert all("address" not in item for item in inventory.values())


@_needs_rom
def test_second_map_scene_uses_normal_deterministic_build_and_preserves_source(
    tmp_path, catalog
):
    canonical = LOCAL_ROM.read_bytes()
    assert hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA
    hashes = []

    for suffix in ("one", "two"):
        project_dir = tmp_path / suffix
        output = tmp_path / f"{suffix}.gba"
        extract_project(LOCAL_ROM, project_dir, catalog, graphics=False)
        maps = load_maps(LOCAL_ROM, catalog)
        required_type = f"{maps.profile.id}/{TYPE_SUFFIX}"
        candidates = scene.clone_source_candidates(
            maps, TARGET_MAP, require_type=required_type
        )
        assert [item["identity"] for item in candidates] == [
            "map:0041/placement:0000",
            "map:0041/placement:0001",
            "map:0041/placement:0002",
        ]
        source = candidates[0]["identity"]
        assert scene.trigger_options(maps, source) == [
            BehaviorTrigger.ON_DEFEAT.value
        ]

        identity = scene.add_authored_npc(
            project_dir, TARGET_MAP, source, "second-scene", (176, 176),
            behavior=f"{TARGET_MAP}/authored:second-scene/behavior",
            script=SCRIPT,
            trigger=BehaviorTrigger.ON_DEFEAT.value,
            maps=maps,
        )
        assert identity == "map:0041/authored:second-scene"
        change = next(
            item for item in scene.pending_changes(project_dir, maps)
            if item.object_identity == identity
        )
        assert change.revertible
        assert any("Visible response assigned" in line for line in change.details)

        report = validate_project(project_dir, LOCAL_ROM, catalog)
        assert report.passed, report.problems
        result = build_project(project_dir, LOCAL_ROM, output, catalog)
        assert result.output_path == output
        image = output.read_bytes()
        assert len(image) == len(canonical)
        hashes.append(hashlib.sha256(image).hexdigest())

        record_change = next(
            change for change in result.manifest.changes
            if change.reason == f"authored placement body: {identity}"
        )
        descriptor_change = next(
            change for change in result.manifest.changes
            if change.reason == f"authored placement body: {identity}/behavior"
        )
        script_change = next(
            change for change in result.manifest.changes
            if change.reason == f"authored placement body: {identity}/behavior/script"
        )
        record = PlacementRecord.from_bytes(record_change.new)
        descriptor_at = GbaRomAddress(record.descriptor_pointer_raw).to_file_offset(
            len(image)
        )
        assert descriptor_at == descriptor_change.offset
        descriptor = DescriptorRecord.from_bytes(descriptor_change.new)
        assert descriptor.handler_pointer_raw == SCRIPT_DISPATCH_HANDLER
        script_at = GbaRomAddress(descriptor.payload_raw).to_file_offset(len(image))
        assert script_at == script_change.offset
        assert image[record_change.offset:record_change.end] == record_change.new
        assert image[descriptor_at:descriptor_change.end] == descriptor_change.new
        assert image[script_at:script_change.end] == script_change.new

        clone, = read_project(project_dir).maps[41]["authored_placements"]
        assert clone.identity == identity
        assert clone.trigger is BehaviorTrigger.ON_DEFEAT
        assert clone.script == SCRIPT
        assert LOCAL_ROM.read_bytes() == canonical

    assert hashes[0] == hashes[1]
    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == CANONICAL_SHA
