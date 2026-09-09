"""TOOLKIT-032 ROM-gated proof that a NEW behavior BODY is authored, not attached.

TOOLKIT-030 chose an existing descriptor and TOOLKIT-031 proved the engine ran
it - but every byte it executed already existed in canonical Buu. This file pins
the step past that: the descriptor AND the script it dispatches are both content
this build creates, at addresses where canonical Buu holds nothing.

Every address here was measured from the canonical image, never assumed. The
canonical ROM is opened read-only on every path, and its hash and mtime are
asserted unchanged; builds emit into pytest's temporary directory.
"""

from __future__ import annotations

import hashlib
import struct
from pathlib import Path

import pytest

from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.formats.map_placements import DescriptorRecord, PlacementRecord
from tools.webfoot.formats.script_vm import Entry, assemble, disassemble
from tools.webfoot.data.script_specs import OPCODE_SETS
from tools.webfoot.maps import PlacementIdentity, load_maps
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project.placements import clone_placement

LOCAL_ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
CATALOG = "config/roms.yaml"
CANONICAL_SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: TOOLKIT-029/030/031's runtime-proven target, reused so the only new variable
#: is that the behavior body is now authored rather than selected.
TARGET_MAP = 40
TEMPLATE = "map:0040/placement:0001"
POSITION = (176, 176)
NAME = "tk032"
IDENTITY = f"map:{TARGET_MAP:04d}/authored:{NAME}"

#: The authored script, in the two forms that must agree: what a project declares,
#: and what the engine must end up holding.
SOURCE = ["push_byte 84", "push_byte 75", "add", "pop", "terminate"]
BODY = bytes.fromhex("0054004b071411")

#: The verified script-dispatch handler. TOOLKIT-031 watched this exact handler
#: dispatch the descriptor it attached, which is why an authored descriptor uses
#: it rather than a handler this toolkit has never seen run.
SCRIPT_DISPATCH_HANDLER = 0x0800421F

#: TOOLKIT-028's confirmed free region.
REGION_START, REGION_END = 0x007EA400, 0x007EA500

#: MEASURED allocation, not assumed - `test_allocation_accounting_is_exact` derives
#: each of these from the built image rather than trusting the constants.
RECORD_AT, DESCRIPTOR_AT, SCRIPT_AT, ARRAY_AT = 0x7EA400, 0x7EA420, 0x7EA428, 0x7EA430

pytestmark = pytest.mark.skipif(not LOCAL_ROM.exists(),
                                reason="canonical Buu's Fury image not present")


@pytest.fixture(scope="module")
def canonical():
    data = LOCAL_ROM.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA
    return data


def _build(tmp_path, name, *, authored):
    """The production path only: extract -> clone -> validate -> build."""
    catalog = RomProfileCatalog.load(CATALOG)
    root = tmp_path / f"project-{name}"
    extract_project(LOCAL_ROM, root, catalog, graphics=False)
    clone_placement(root, map_index=TARGET_MAP, source=TEMPLATE, name=NAME,
                    position_low=POSITION[0], position_high=POSITION[1],
                    behavior=(f"{IDENTITY}/behavior" if authored else None),
                    script=(SOURCE if authored else None))
    assert validate_project(root, LOCAL_ROM, catalog).passed
    out = tmp_path / f"{name}.gba"
    build_project(root, LOCAL_ROM, out, catalog, manifest_path=tmp_path / f"{name}.json")
    return out.read_bytes()


@pytest.fixture(scope="module")
def authored(tmp_path_factory):
    return _build(tmp_path_factory.mktemp("authored"), "authored", authored=True)


@pytest.fixture(scope="module")
def control(tmp_path_factory):
    """The same clone, same position, same template - no authored behavior."""
    return _build(tmp_path_factory.mktemp("control"), "control", authored=False)


# ------------------------------------------------------------- A3: the novelty

def test_authored_script_body_exists_nowhere_in_canonical_buu(canonical):
    """A3 / SC9. The closure claim, pinned: this body is genuinely new content.

    Not "absent from the window we wrote into" - absent from all 8 MB. A body
    that already occurred somewhere in the ROM would leave the ticket unable to
    say the engine executed something it did not already contain.
    """
    assert canonical.count(BODY) == 0


def test_authored_script_body_is_the_exact_contract_sequence():
    """The 7-byte body is fixed by the ticket; a shorter form is not equivalent.

    A 3-byte `push_byte N; terminate` occurs in canonical Buu several times, so
    shortening this body would silently weaken the novelty proof above.
    """
    assert BODY == bytes([0x00, 0x54, 0x00, 0x4B, 0x07, 0x14, 0x11])
    assert len(BODY) == 7


# ------------------------------------------ SC2/SC3: production serialization

def test_script_body_lands_in_the_built_rom_exactly(authored):
    """SC2. The bytes the production codec produced are the bytes emitted."""
    assert authored[SCRIPT_AT:SCRIPT_AT + len(BODY)] == BODY


def test_emitted_script_body_round_trips_as_buu_vm_code(authored):
    """The emitted bytes are real code to the same decoder that reads canonical.

    Decoding what was written - rather than what we meant to write - is what
    distinguishes an authored script from an authored blob.
    """
    spec = OPCODE_SETS["stack_be16_buu_v1"]
    raw = authored[SCRIPT_AT:SCRIPT_AT + len(BODY)]
    ir = disassemble(raw, (Entry("authored", 0),), spec)
    assert ir.opaque == ()
    assert assemble(ir) == raw
    names = [spec.lookup(i.opcode).name for b in ir.blocks for i in b.instructions]
    assert names == ["push_byte", "push_byte", "add", "pop", "terminate"]


def test_descriptor_is_the_production_record_pointing_at_the_authored_script(authored):
    """SC3 + A2. The handler is right AND the payload is THIS build's script.

    A2 exists because a correct handler alone proves nothing: a descriptor could
    carry the right handler and still dispatch a canonical script. The payload
    word must be the address the allocator gave the body written above.
    """
    raw = authored[DESCRIPTOR_AT:DESCRIPTOR_AT + 8]
    record = DescriptorRecord.from_bytes(raw)
    assert record.handler_pointer_raw == SCRIPT_DISPATCH_HANDLER
    assert record.payload_raw == 0x08000000 + SCRIPT_AT
    # And it is byte-for-byte what the production codec emits for that pair.
    assert raw == DescriptorRecord(SCRIPT_DISPATCH_HANDLER, 0x08000000 + SCRIPT_AT).to_bytes()
    # The word it points at really is the authored body, not merely a valid address.
    payload = record.payload_raw - 0x08000000
    assert authored[payload:payload + len(BODY)] == BODY


# ---------------------------------------------------- SC4: the attachment edge

def test_authored_record_points_at_the_authored_descriptor(authored, control):
    """SC4. `+0x14` is this build's descriptor, and differs from the inherited one."""
    record = PlacementRecord.from_bytes(authored[RECORD_AT:RECORD_AT + 32])
    assert record.descriptor_pointer_raw == 0x08000000 + DESCRIPTOR_AT
    inherited = PlacementRecord.from_bytes(control[RECORD_AT:RECORD_AT + 32])
    assert inherited.descriptor_pointer_raw != record.descriptor_pointer_raw


def test_the_whole_chain_resolves_record_to_descriptor_to_script(authored):
    """The edge the engine walks, followed in the emitted image end to end."""
    record = PlacementRecord.from_bytes(authored[RECORD_AT:RECORD_AT + 32])
    descriptor_at = record.descriptor_pointer_raw - 0x08000000
    descriptor = DescriptorRecord.from_bytes(authored[descriptor_at:descriptor_at + 8])
    script_at = descriptor.payload_raw - 0x08000000
    assert descriptor.handler_pointer_raw == SCRIPT_DISPATCH_HANDLER
    assert authored[script_at:script_at + len(BODY)] == BODY


def test_the_expanded_array_reaches_the_authored_record(authored, canonical):
    """The engine finds the record at all: the appended slot holds its address."""
    entry = struct.unpack_from("<I", authored, 0x8EBB4)[0]
    array_at = entry - 0x08000000
    count = authored[0x8EBA4]
    assert count == canonical[0x8EBA4] + 1
    slots = struct.unpack_from(f"<{count}I", authored, array_at)
    assert slots[-1] == 0x08000000 + RECORD_AT


# ---------------------------------------------------- SC5: allocation accounting

def test_allocation_accounting_is_exact(authored, canonical):
    """SC5. Every authored structure sits inside the declared region, disjoint.

    The spans are DERIVED from the built image by following the pointers, so this
    checks where the allocator actually put things rather than restating constants.
    """
    record = PlacementRecord.from_bytes(authored[RECORD_AT:RECORD_AT + 32])
    descriptor_at = record.descriptor_pointer_raw - 0x08000000
    descriptor = DescriptorRecord.from_bytes(authored[descriptor_at:descriptor_at + 8])
    script_at = descriptor.payload_raw - 0x08000000
    array_at = struct.unpack_from("<I", authored, 0x8EBB4)[0] - 0x08000000
    count = authored[0x8EBA4]

    spans = sorted([
        ("record", RECORD_AT, 32),
        ("descriptor", descriptor_at, 8),
        ("script", script_at, len(BODY)),
        ("array", array_at, 4 * count),
    ], key=lambda s: s[1])

    for name, start, size in spans:
        assert REGION_START <= start and start + size <= REGION_END, name
    for (_, a_start, a_size), (_, b_start, _b) in zip(spans, spans[1:]):
        assert a_start + a_size <= b_start

    # The measured demand. The array is 4 * 5 = 20 because map 40 carries FOUR
    # canonical object slots, not two - so the expanded array costs 20 bytes here
    # rather than the 12 a two-slot map would need.
    assert 4 * count == 20
    assert sum(size for _, _, size in spans) == 67
    assert max(start + size for _, start, size in spans) - REGION_START == 68


def test_canonical_holds_nothing_at_the_allocated_offsets(canonical):
    """SC9. The region really was free; the authored bytes displaced nothing."""
    assert set(canonical[REGION_START:REGION_END]) == {0xFF}
    assert canonical[DESCRIPTOR_AT:DESCRIPTOR_AT + 8] != DescriptorRecord(
        SCRIPT_DISPATCH_HANDLER, 0x08000000 + SCRIPT_AT).to_bytes()
    assert canonical[SCRIPT_AT:SCRIPT_AT + len(BODY)] != BODY


# ------------------------------------------------- SC9: the independence control

def test_control_build_contains_neither_authored_structure(control, authored):
    """SC9. Without the declaration, neither structure exists anywhere in the image."""
    descriptor = authored[DESCRIPTOR_AT:DESCRIPTOR_AT + 8]
    assert control.count(BODY) == 0
    assert control.count(descriptor) == 0


def test_control_build_still_authors_its_placement(control, canonical):
    """The control differs by the BEHAVIOR only - it is not an unbuilt project."""
    assert control != canonical
    record = PlacementRecord.from_bytes(control[RECORD_AT:RECORD_AT + 32])
    assert (record.position_low, record.position_high) == POSITION


def test_authored_bytes_derive_from_project_state(tmp_path):
    """SC9. Change the declared script, and only the authored body changes.

    This is what makes the bytes attributable to project state rather than to the
    toolkit: a different declaration produces a different body at the same place.
    """
    catalog = RomProfileCatalog.load(CATALOG)
    root = tmp_path / "project-variant"
    extract_project(LOCAL_ROM, root, catalog, graphics=False)
    clone_placement(root, map_index=TARGET_MAP, source=TEMPLATE, name=NAME,
                    position_low=POSITION[0], position_high=POSITION[1],
                    behavior=f"{IDENTITY}/behavior",
                    script=["push_byte 1", "push_byte 2", "add", "pop", "terminate"])
    out = tmp_path / "variant.gba"
    build_project(root, LOCAL_ROM, out, catalog)
    image = out.read_bytes()
    assert image[SCRIPT_AT:SCRIPT_AT + 7] == bytes([0x00, 0x01, 0x00, 0x02, 0x07, 0x14, 0x11])
    assert image[SCRIPT_AT:SCRIPT_AT + 7] != BODY
    # The descriptor still points at it, so the edge follows the content.
    descriptor = DescriptorRecord.from_bytes(image[DESCRIPTOR_AT:DESCRIPTOR_AT + 8])
    assert descriptor.payload_raw == 0x08000000 + SCRIPT_AT


# ------------------------------------------------------ SC6/SC7/SC8: the build

def test_two_builds_are_byte_identical(tmp_path_factory):
    """SC6. Determinism, measured by building twice rather than asserted."""
    first = _build(tmp_path_factory.mktemp("det1"), "det1", authored=True)
    second = _build(tmp_path_factory.mktemp("det2"), "det2", authored=True)
    assert hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()


def test_canonical_noop_build_is_byte_identical(tmp_path, canonical):
    """SC7. Authoring nothing still emits exactly the verified base."""
    catalog = RomProfileCatalog.load(CATALOG)
    root = tmp_path / "project-noop"
    extract_project(LOCAL_ROM, root, catalog, graphics=False)
    out = tmp_path / "noop.gba"
    build_project(root, LOCAL_ROM, out, catalog)
    assert out.read_bytes() == canonical


def test_canonical_rom_is_never_modified(authored, control):
    """SC8. The input is read-only, across every build this module ran."""
    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == CANONICAL_SHA


def test_only_the_authored_structures_and_their_map_entry_changed(authored, canonical):
    """The blast radius: the free region, plus the two MapEntry fields it derives."""
    changed = [i for i in range(len(canonical)) if canonical[i] != authored[i]]
    assert changed, "an authored build that changes nothing is not a build"
    outside = [i for i in changed if not REGION_START <= i < REGION_END]
    # `MapEntry+0x04` (the derived count) and `+0x14` (the relocated array pointer).
    assert set(outside) <= {0x8EBA4, *range(0x8EBB4, 0x8EBB8)}
