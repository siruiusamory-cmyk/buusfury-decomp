"""TOOLKIT-030 ROM-gated proof that a behavior attachment is AUTHORED, not inherited.

Every address here was measured from the canonical Buu's Fury image, never
assumed. The canonical ROM is opened read-only on every path; builds emit into
pytest's temporary directory.

The proof this file pins is the ticket's "acceptable alternative" independence
form, and it is the stronger one for this target: the clone template carries the
NULL behavior descriptor `0x080555A0` (handler `0x0800421D`, a bare `bx lr`), so
the authored record cannot acquire a behavior by inheritance at all. Anything it
executes must have been put there by project state.
"""

from __future__ import annotations

import hashlib
import struct
from pathlib import Path

import pytest

from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.formats.map_placements import PlacementRecord
from tools.webfoot.maps import MapIdentity, PlacementIdentity, load_maps
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import ProjectError
from tools.webfoot.project.placements import clone_placement


LOCAL_ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
CATALOG = "config/roms.yaml"
CANONICAL_SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: TOOLKIT-029's runtime-proven target. Reused deliberately: the ticket asks for
#: the same case wherever practical, so the only new variable is the attachment.
TARGET_MAP = 40
TEMPLATE = "map:0040/placement:0001"
POSITION = (176, 176)

#: Measured, not assumed - see `test_template_carries_the_null_behavior`.
NULL_DESCRIPTOR = 0x080555A0
NULL_HANDLER = 0x0800421D

#: The behavior selected by TOOLKIT-030. `0x0808D788` is the descriptor published
#: for `map:0428/placement:0000`; it dispatches script `0x0808D77C`, which is
#: `push_many(4, 52,192,84,200); native_stack(43); terminate`.
BEHAVIOR = "map:0428/placement:0000/descriptor"
BEHAVIOR_DESCRIPTOR = 0x0808D788
BEHAVIOR_SCRIPT = 0x0808D77C
SCRIPT_DISPATCH_HANDLER = 0x0800421F

#: TOOLKIT-028's confirmed free region.
CAPACITY = (0x007EA400, 0x007EA500)

#: TOOLKIT-029's authored body address inside that region.
BODY_OFFSET = 0x7EA400

#: TOOLKIT-029's published output, reproduced here as the inheritance control.
TOOLKIT029_SHA = "a425ae73af5c5b4029882e8fb62ca398ee0e3b8a9a4fbb63dee8dc9834d7bed4"
ATTACHED_SHA = "f6595c4e89189f6420130f2bb5f09e447621ee095f16bff4074f12678ea0a9fb"

pytestmark = pytest.mark.skipif(not LOCAL_ROM.exists(),
                                reason="canonical Buu's Fury image not present")


@pytest.fixture(scope="module")
def canonical():
    data = LOCAL_ROM.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA
    return data


@pytest.fixture(scope="module")
def maps():
    return load_maps(LOCAL_ROM, RomProfileCatalog.load(CATALOG))


def _descriptor(image, pointer):
    return struct.unpack_from("<2I", image, pointer - 0x08000000)


def _build(tmp_path, name, behavior):
    """The production path only: extract -> clone -> validate -> build."""
    catalog = RomProfileCatalog.load(CATALOG)
    root = tmp_path / f"project-{name}"
    extract_project(LOCAL_ROM, root, catalog, graphics=False)
    clone_placement(root, map_index=TARGET_MAP, source=TEMPLATE, name=name,
                    position_low=POSITION[0], position_high=POSITION[1],
                    behavior=behavior)
    assert validate_project(root, LOCAL_ROM, catalog).passed
    out = tmp_path / f"{name}.gba"
    build_project(root, LOCAL_ROM, out, catalog)
    return out.read_bytes()


def test_template_carries_the_null_behavior(canonical, maps):
    """Step 1: what makes the TOOLKIT-029 clone behave like its source?

    The answer is that it inherits `+0x14` verbatim, and on this map that word
    is the shared NULL descriptor. The clone inherits no behavior whatsoever,
    which is why an attachment here cannot be an accident of cloning.
    """
    template = PlacementRecord.from_bytes(
        maps.placement(PlacementIdentity(TARGET_MAP, 1)).original_bytes)
    assert template.descriptor_pointer_raw == NULL_DESCRIPTOR
    handler, _ = _descriptor(canonical, NULL_DESCRIPTOR)
    assert handler == NULL_HANDLER
    # Both of map 40's canonical placements share it, so neither sibling could
    # have supplied a behavior either.
    for placement in maps.map_placements(MapIdentity(TARGET_MAP)):
        record = PlacementRecord.from_bytes(placement.original_bytes)
        assert record.descriptor_pointer_raw == NULL_DESCRIPTOR


def test_selected_behavior_is_a_verified_script_descriptor(canonical):
    """The attachment names real, already-verified engine behavior."""
    handler, payload = _descriptor(canonical, BEHAVIOR_DESCRIPTOR)
    assert handler == SCRIPT_DISPATCH_HANDLER
    assert payload == BEHAVIOR_SCRIPT
    # push_many(4, 52,192,84,200); native_stack(43); terminate
    assert canonical[BEHAVIOR_SCRIPT - 0x08000000:][:9].hex() == "1d0468830081288310"


def test_attachment_is_authored_rather_than_inherited(tmp_path, canonical, maps):
    """The independence proof, on production build machinery only."""
    attached = _build(tmp_path, "tk030", BEHAVIOR)
    inherited = _build(tmp_path, "tk030ctrl", None)

    authored = PlacementRecord.from_bytes(attached[BODY_OFFSET:BODY_OFFSET + 32])
    control = PlacementRecord.from_bytes(inherited[BODY_OFFSET:BODY_OFFSET + 32])

    assert control.descriptor_pointer_raw == NULL_DESCRIPTOR
    assert authored.descriptor_pointer_raw == BEHAVIOR_DESCRIPTOR
    assert authored.descriptor_pointer_raw != control.descriptor_pointer_raw

    # Ancestry is untouched: the body is still structurally a clone of TEMPLATE.
    template = PlacementRecord.from_bytes(
        maps.placement(PlacementIdentity(TARGET_MAP, 1)).original_bytes)
    for field in ("factory_raw", "flags_raw", "type_raw", "id_raw", "child_pointers_raw"):
        assert getattr(authored, field) == getattr(template, field)

    # Exactly the descriptor word separates the two builds.
    differing = [i for i in range(len(attached)) if attached[i] != inherited[i]]
    assert differing == list(range(BODY_OFFSET + 0x14, BODY_OFFSET + 0x17))


def test_removing_the_declaration_reproduces_the_toolkit029_rom(tmp_path):
    """The control is not merely similar - it is byte-identical to the prior proof."""
    inherited = _build(tmp_path, "tk029repro", None)
    assert hashlib.sha256(inherited).hexdigest() == TOOLKIT029_SHA


def test_attached_build_is_deterministic(tmp_path):
    first = _build(tmp_path, "det-a", BEHAVIOR)
    second = _build(tmp_path, "det-b", BEHAVIOR)
    assert first == second
    assert hashlib.sha256(first).hexdigest() == ATTACHED_SHA


def test_allocation_demand_fits_confirmed_capacity(tmp_path, canonical):
    """TOOLKIT-028's 256 confirmed bytes still suffice; no new hunt is needed."""
    attached = _build(tmp_path, "capacity", BEHAVIOR)
    start, end = CAPACITY
    changed = [i for i in range(start, end) if attached[i] != canonical[i]]
    assert changed, "the authored content must land inside the confirmed region"
    demand = max(changed) + 1 - start
    assert demand == 52                       # 32-byte body + 20-byte 5-slot array
    assert demand <= end - start              # 52 of 256; 204 bytes headroom
    # Untouched capacity is still erased flash, so nothing silently spilled.
    assert set(attached[start + demand:end]) == {0xFF}


def test_unknown_behavior_fails_the_build_and_publishes_nothing(tmp_path):
    """A behavior this profile cannot verify must never reach a ROM."""
    catalog = RomProfileCatalog.load(CATALOG)
    root = tmp_path / "project-unknown"
    extract_project(LOCAL_ROM, root, catalog, graphics=False)
    clone_placement(root, map_index=TARGET_MAP, source=TEMPLATE, name="bad",
                    position_low=POSITION[0], position_high=POSITION[1],
                    behavior="map:9999/placement:9999/descriptor")
    out = tmp_path / "unpublished.gba"
    with pytest.raises(ProjectError, match="no verified placement descriptor"):
        validate_project(root, LOCAL_ROM, catalog)
        build_project(root, LOCAL_ROM, out, catalog)
    assert not out.exists()


def test_canonical_rom_is_never_modified(tmp_path, canonical):
    stamp = LOCAL_ROM.stat().st_mtime_ns
    _build(tmp_path, "immutability", BEHAVIOR)
    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == CANONICAL_SHA
    assert LOCAL_ROM.read_bytes() == canonical
    assert LOCAL_ROM.stat().st_mtime_ns == stamp
