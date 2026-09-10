"""TOOLKIT-034 ROM-gated proof of the narrow `on_defeat` build contract."""
from __future__ import annotations

import hashlib
import os
import struct
from pathlib import Path

import pytest

from tools.webfoot.build import (
    authored_capacity_plan,
    build_project,
    extract_project,
    validate_project,
)
from tools.webfoot.entities import load_placement_types
from tools.webfoot.formats.map_placements import DescriptorRecord, PlacementRecord
from tools.webfoot.maps import PlacementIdentity
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project.placements import BehaviorTrigger, clone_placement
from tools.webfoot.project import ProjectError


LOCAL_ROM = Path(os.environ.get(
    "WEBFOOT_BUU_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))
CATALOG_PATH = "config/roms.yaml"
PROFILE = "buus_fury_usa_rev0_01c1707f"
CANONICAL_SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
OUTPUT_SHA = "bbd0bbbe1f01b4d715b89bb20a22f63276e36ec4fd2dc443e34ae3b99880ff35"
TYPE = f"{PROFILE}/placement_type:0086"
TARGET_MAP = 40
TEMPLATE = "map:0040/placement:0001"
NAME = "tk034"
IDENTITY = f"map:{TARGET_MAP:04d}/authored:{NAME}"
BEHAVIOR = f"{IDENTITY}/behavior"
SOURCE = ["show_centered_sprite_text text:1525 120 105", "terminate"]
BODY = bytes.fromhex("1D03976A8170815202B211")
REGION_START, REGION_END = 0x007EA400, 0x007EA500


pytestmark = pytest.mark.skipif(
    not LOCAL_ROM.exists(), reason="canonical Buu's Fury image not present")


@pytest.fixture(scope="module")
def catalog():
    return RomProfileCatalog.load(CATALOG_PATH)


@pytest.fixture(scope="module")
def canonical():
    data = LOCAL_ROM.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA
    return data


def _build(tmp_path, catalog, *, trigger):
    root = tmp_path / "project"
    extract_project(LOCAL_ROM, root, catalog, graphics=False)
    clone_placement(
        root,
        map_index=TARGET_MAP,
        source=TEMPLATE,
        name=NAME,
        position_low=176,
        position_high=176,
        behavior=BEHAVIOR,
        script=SOURCE,
        trigger=trigger,
    )
    report = validate_project(root, LOCAL_ROM, catalog)
    assert report.passed, report.problems
    plan, = authored_capacity_plan(root, LOCAL_ROM, catalog)
    output = tmp_path / "authored.gba"
    build_project(root, LOCAL_ROM, output, catalog)
    return root, plan, output.read_bytes()


@pytest.fixture(scope="module")
def triggered(tmp_path_factory, catalog):
    return _build(tmp_path_factory.mktemp("triggered"), catalog, trigger="on_defeat")


@pytest.fixture(scope="module")
def legacy(tmp_path_factory, catalog):
    return _build(tmp_path_factory.mktemp("legacy"), catalog, trigger=None)


def test_canonical_template_resolves_to_exact_supported_enemy_type(catalog):
    types = load_placement_types(LOCAL_ROM, catalog)
    item = types.type_of(PlacementIdentity(40, 1))
    assert str(item.identity) == TYPE
    assert item.classification == "CONFIRMED_ENEMY_STAT_LINK"
    assert item.enemy_identity is not None
    assert item.original_bytes is not None


def test_trigger_is_preserved_in_project_and_capacity_attribution(triggered):
    root, plan, _image = triggered
    clone, = read_authored(root)
    assert clone.trigger is BehaviorTrigger.ON_DEFEAT
    planned = plan.record(IDENTITY)
    assert planned.trigger is BehaviorTrigger.ON_DEFEAT
    assert planned.to_json()["trigger"] == "on_defeat"


def read_authored(root):
    from tools.webfoot.project import read_project
    return read_project(root).maps[TARGET_MAP]["authored_placements"]


def test_trigger_uses_existing_record_descriptor_script_chain(triggered):
    _root, _plan, image = triggered
    record = PlacementRecord.from_bytes(image[REGION_START:REGION_START + 32])
    descriptor_at = record.descriptor_pointer_raw - 0x08000000
    descriptor = DescriptorRecord.from_bytes(image[descriptor_at:descriptor_at + 8])
    script_at = descriptor.payload_raw - 0x08000000
    assert image[script_at:script_at + len(BODY)] == BODY


def test_trigger_adds_no_parallel_binary_field_or_allocation(triggered, legacy):
    _trigger_root, trigger_plan, trigger_image = triggered
    _legacy_root, legacy_plan, legacy_image = legacy
    assert trigger_image == legacy_image
    assert trigger_plan.allocation_request == legacy_plan.allocation_request
    assert trigger_plan.record(IDENTITY).payload == legacy_plan.record(IDENTITY).payload
    assert trigger_plan.record(IDENTITY).trigger is BehaviorTrigger.ON_DEFEAT
    assert legacy_plan.record(IDENTITY).trigger is None


def test_exact_allocation_demand_output_attribution_and_remaining_capacity(
        triggered, canonical):
    _root, _plan, image = triggered
    record = PlacementRecord.from_bytes(image[REGION_START:REGION_START + 32])
    descriptor_at = record.descriptor_pointer_raw - 0x08000000
    descriptor = DescriptorRecord.from_bytes(image[descriptor_at:descriptor_at + 8])
    script_at = descriptor.payload_raw - 0x08000000
    array_at = struct.unpack_from("<I", image, 0x8EBB4)[0] - 0x08000000
    count = image[0x8EBA4]
    spans = (
        (REGION_START, 32),
        (descriptor_at, 8),
        (script_at, len(BODY)),
        (array_at, count * 4),
    )
    assert sum(size for _, size in spans) == 71
    assert max(start + size for start, size in spans) == 0x007EA448
    assert REGION_END - max(start + size for start, size in spans) == 184
    assert hashlib.sha256(image).hexdigest() == OUTPUT_SHA
    assert sum(a != b for a, b in zip(canonical, image)) == 75


def test_non_whitelisted_enemy_type_fails_before_output(tmp_path, catalog):
    root = tmp_path / "project"
    extract_project(LOCAL_ROM, root, catalog, graphics=False)
    identity = "map:0309/authored:unsupported"
    clone_placement(
        root,
        map_index=309,
        source="map:0309/placement:0001",
        name="unsupported",
        position_low=1,
        position_high=1,
        behavior=f"{identity}/behavior",
        script=SOURCE,
        trigger="on_defeat",
    )
    output = tmp_path / "must-not-exist.gba"
    with pytest.raises(ProjectError, match="requires canonical template type"):
        build_project(root, LOCAL_ROM, output, catalog)
    assert not output.exists()


def test_triggered_build_is_deterministic_and_source_is_immutable(
        tmp_path, catalog, canonical, triggered):
    stamp = LOCAL_ROM.stat().st_mtime_ns
    _root, _plan, first = triggered
    _other_root, _other_plan, second = _build(
        tmp_path / "repeat", catalog, trigger="on_defeat")
    assert first == second
    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == CANONICAL_SHA
    assert LOCAL_ROM.stat().st_mtime_ns == stamp
    assert canonical == LOCAL_ROM.read_bytes()
