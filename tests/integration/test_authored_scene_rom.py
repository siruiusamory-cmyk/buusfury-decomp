"""TOOLKIT-035 ROM-gated proof that one authored scene composes through the
ordinary SDK lifecycle.

This test exists because the individual primitives were each proven alone. What
it adds is *composition*: one extract, one authored placement carrying its own
behavior, script and trigger, one authored scene message, one validate, one
build. No production code is patched, no bytes are hand-placed and no test-only
authoring path is used - every call below is a public SDK entry point a mod
author would call.

The scene message is the only new dimension relative to TOOLKIT-034, and it is
deliberately a MODIFIED EXISTING string rather than a newly allocated one. Text
1525's allocation is 30 bytes; the authored message is written inside it. The
over-long case is tested too, because a scene that silently truncated its own
message would be worse than one that refused to build.
"""
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
from tools.webfoot.formats.map_placements import DescriptorRecord, PlacementRecord
from tools.webfoot.formats.text_tables import TextIdentity
from tools.webfoot.project import read_project
from tools.webfoot.text import load_text_strings
from tools.webfoot.project.format import dump_toml, load_toml
from tools.webfoot.project.model import _TEXT_FILE
from tools.webfoot.project.placements import BehaviorTrigger, clone_placement
from tools.webfoot.profile import RomProfileCatalog


LOCAL_ROM = Path(os.environ.get(
    "WEBFOOT_BUU_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))
CATALOG_PATH = "config/roms.yaml"
CANONICAL_SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
SCENE_SHA = "ffde3e85aac247c1d549c23a9a07049f9741c98d0c5599ed9e9c4539631a2793"

TARGET_MAP = 40
TEMPLATE = "map:0040/placement:0001"
NAME = "scene"
IDENTITY = f"map:{TARGET_MAP:04d}/authored:{NAME}"
BEHAVIOR = f"{IDENTITY}/behavior"

#: The scene's visible line. Reuses text 1525 - the string the proven native
#: already renders - with author-chosen content. Retail reads "Match 2 Fight!".
SCENE_TEXT_INDEX = 1525
SCENE_TEXT_KEY = f"text:{SCENE_TEXT_INDEX}"
SCENE_TEXT = "SCENE CLEAR!"
RETAIL_TEXT = "Match 2 Fight!"

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


def _author_scene_text(root: Path, text: str) -> None:
    """Set the scene's message through the ordinary authored text file."""
    path = root / _TEXT_FILE
    document = load_toml(path.read_text(encoding="utf-8"))
    document["text"][SCENE_TEXT_KEY]["text"] = text
    path.write_text(dump_toml(document), encoding="utf-8", newline="\n")


def _author_scene(tmp_path: Path, catalog, *, text: str = SCENE_TEXT) -> Path:
    """The whole authoring lifecycle, in the order an author performs it."""
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
        trigger="on_defeat",
    )
    _author_scene_text(root, text)
    return root


def _build_scene(tmp_path: Path, catalog):
    root = _author_scene(tmp_path, catalog)
    report = validate_project(root, LOCAL_ROM, catalog)
    assert report.passed, report.problems
    plan, = authored_capacity_plan(root, LOCAL_ROM, catalog)
    output = tmp_path / "scene.gba"
    build_project(root, LOCAL_ROM, output, catalog)
    return root, plan, output.read_bytes()


@pytest.fixture(scope="module")
def scene(tmp_path_factory, catalog):
    return _build_scene(tmp_path_factory.mktemp("scene"), catalog)


def _scene_spans(image: bytes):
    """Locate every authored structure by following the same chain the engine
    does, rather than by trusting a remembered address."""
    record = PlacementRecord.from_bytes(image[REGION_START:REGION_START + 32])
    descriptor_at = record.descriptor_pointer_raw - 0x08000000
    descriptor = DescriptorRecord.from_bytes(image[descriptor_at:descriptor_at + 8])
    script_at = descriptor.payload_raw - 0x08000000
    array_at = struct.unpack_from("<I", image, 0x8EBB4)[0] - 0x08000000
    count = image[0x8EBA4]
    return (
        (REGION_START, 32),
        (descriptor_at, 8),
        (script_at, len(BODY)),
        (array_at, count * 4),
    )


def test_scene_is_one_authored_declaration_carrying_every_dimension(scene):
    """The composition claim: one project record names entity, behavior, script
    and trigger together, rather than four unrelated proofs."""
    root, _plan, _image = scene
    project = read_project(root)
    clone, = project.maps[TARGET_MAP]["authored_placements"]
    assert clone.identity == IDENTITY
    assert clone.clone_from == TEMPLATE
    assert (clone.position_low, clone.position_high) == (176, 176)
    assert clone.behavior == BEHAVIOR
    assert clone.authored_behavior
    assert clone.script == tuple(SOURCE)
    assert clone.trigger is BehaviorTrigger.ON_DEFEAT
    assert project.strings[TextIdentity(SCENE_TEXT_INDEX)] == SCENE_TEXT


def test_scene_entity_behavior_and_script_are_reachable_by_the_engine_chain(scene):
    """placement -> descriptor -> script body, followed as the engine follows it."""
    _root, _plan, image = scene
    record = PlacementRecord.from_bytes(image[REGION_START:REGION_START + 32])
    descriptor_at = record.descriptor_pointer_raw - 0x08000000
    descriptor = DescriptorRecord.from_bytes(image[descriptor_at:descriptor_at + 8])
    script_at = descriptor.payload_raw - 0x08000000
    assert image[script_at:script_at + len(BODY)] == BODY


def test_scene_message_is_authored_inside_the_existing_text_allocation(
        scene, canonical, catalog):
    """The scene's visible line is author-controlled, and is a MODIFIED EXISTING
    string: it occupies exactly the bytes retail text 1525 already owned.

    The span comes from the profile's own text table rather than a hand-computed
    address, so this cannot drift from where the SDK believes the string lives.
    """
    _root, _plan, image = scene
    location = load_text_strings(LOCAL_ROM, catalog).entry(
        TextIdentity(SCENE_TEXT_INDEX)).location
    span = slice(location.file_offset, location.file_offset + location.allocation)

    assert canonical[span].decode("utf-16le").rstrip("\x00") == RETAIL_TEXT
    assert image[span].decode("utf-16le").rstrip("\x00") == SCENE_TEXT
    # Nothing moved: the pointer entry is byte-identical, so this is an in-place
    # edit of existing storage, not a relocation or a new allocation.
    assert (canonical[location.pointer_offset:location.pointer_offset + 4]
            == image[location.pointer_offset:location.pointer_offset + 4])


def test_over_long_scene_message_is_refused_before_any_output(tmp_path, catalog):
    """A scene message that does not fit fails closed rather than truncating."""
    root = _author_scene(tmp_path, catalog, text="SCENE 035 COMPLETE!")
    report = validate_project(root, LOCAL_ROM, catalog)
    assert not report.passed
    assert any("too long" in problem for problem in report.problems)


def test_scene_fits_the_verified_region_with_measured_remaining_capacity(scene):
    """Composition did not grow the ROM demand: the scene's text dimension costs
    zero region bytes, because it modifies storage that already exists."""
    _root, plan, image = scene
    spans = _scene_spans(image)
    highest = max(start + size for start, size in spans)
    assert sum(size for _, size in spans) == 71
    assert highest == 0x007EA448
    assert REGION_END - highest == 184
    # The author-facing capacity plan must describe the same scene the image
    # ended up containing, or the plan is decoration rather than a check.
    assert plan.record(IDENTITY).trigger is BehaviorTrigger.ON_DEFEAT
    assert plan.allocation_request.size >= sum(size for _, size in spans)


def test_scene_build_is_deterministic_and_leaves_the_source_rom_untouched(
        tmp_path, catalog, canonical, scene):
    _root, _plan, first = scene
    stamp = LOCAL_ROM.stat().st_mtime_ns
    _repeat_root, _repeat_plan, second = _build_scene(tmp_path / "repeat", catalog)
    assert first == second
    assert hashlib.sha256(first).hexdigest() == SCENE_SHA
    assert sum(a != b for a, b in zip(canonical, first)) == 88
    assert LOCAL_ROM.read_bytes() == canonical
    assert LOCAL_ROM.stat().st_mtime_ns == stamp
