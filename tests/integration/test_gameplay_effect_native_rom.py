"""TOOLKIT-033 ROM-gated proof for one authored gameplay-effect native call."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import pytest

from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.data.script_specs import OPCODE_SETS
from tools.webfoot.formats.map_placements import DescriptorRecord, PlacementRecord
from tools.webfoot.formats.script_vm import Entry, assemble, disassemble
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project.placements import clone_placement


ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
CATALOG = "config/roms.yaml"
CANONICAL_SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
PROFILE = "buus_fury_usa_rev0_01c1707f"

TARGET_MAP = 40
TEMPLATE = "map:0040/placement:0001"
POSITION = (176, 176)
NAME = "tk033"
IDENTITY = f"map:{TARGET_MAP:04d}/authored:{NAME}"

AUTHORED_SOURCE = ["show_centered_sprite_text text:1525 120 105", "terminate"]
AUTHORED_BODY = bytes.fromhex("1d03976a8170815202b211")
# Same literal setup and termination, but no opcode can dispatch native slot 178.
NEGATIVE_SOURCE = ["push_many 3 1525 120 105", "pop", "pop", "pop", "terminate"]
NEGATIVE_BODY = bytes.fromhex("1d03976a8170815214141411")
# Canonical dialog 290 uses this exact invocation subsequence at file 0x78B5A7.
CANONICAL_INVOCATION = bytes.fromhex("1d03976a8170810202b2")
POSITIVE_SOURCE = ["show_centered_sprite_text text:1525 120 65", "terminate"]
POSITIVE_BODY = CANONICAL_INVOCATION + bytes((0x11,))

SCRIPT_DISPATCH_HANDLER = 0x0800421F
NATIVE_SLOT = 178
NATIVE_HANDLER_RAW = 0x08003031
CANONICAL_INVOCATION_AT = 0x0078B5A7

REGION_START, REGION_END = 0x007EA400, 0x007EA500
RECORD_AT, DESCRIPTOR_AT, SCRIPT_AT, ARRAY_AT = (
    0x007EA400, 0x007EA420, 0x007EA428, 0x007EA434)

pytestmark = pytest.mark.skipif(not ROM.exists(), reason="canonical Buu ROM not present")


@pytest.fixture(scope="module")
def canonical():
    data = ROM.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA
    return data


def build_variant(root: Path, output: Path, source: list[str]):
    """Use only the production extract/project/validate/build path."""
    catalog = RomProfileCatalog.load(CATALOG)
    extract_project(ROM, root, catalog, graphics=False)
    clone_placement(
        root,
        map_index=TARGET_MAP,
        source=TEMPLATE,
        name=NAME,
        position_low=POSITION[0],
        position_high=POSITION[1],
        behavior=f"{IDENTITY}/behavior",
        script=source,
    )
    assert validate_project(root, ROM, catalog).passed
    manifest = output.with_suffix(".json")
    build_project(root, ROM, output, catalog, manifest_path=manifest)
    return output.read_bytes(), json.loads(manifest.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def variants(tmp_path_factory):
    root = tmp_path_factory.mktemp("tk033")
    return {
        name: build_variant(root / name, root / f"{name}.gba", source)
        for name, source in (
            ("authored", AUTHORED_SOURCE),
            ("negative", NEGATIVE_SOURCE),
            ("positive", POSITIVE_SOURCE),
        )
    }


def test_canonical_positive_control_source_is_exact(canonical):
    assert canonical[CANONICAL_INVOCATION_AT:
                     CANONICAL_INVOCATION_AT + len(CANONICAL_INVOCATION)] == CANONICAL_INVOCATION
    assert canonical.count(CANONICAL_INVOCATION) == 1
    assert int.from_bytes(canonical[0x055360:0x055364], "little") == NATIVE_HANDLER_RAW


def test_selected_handler_stack_layout_is_read_not_guessed(canonical):
    # ldr r1,[r0]; subs r1,#1; str r1,[r0]; lsls r1,#2;
    # adds r1,r1,r0; ldr r1,[r1,#4]. Therefore [r0] is a depth/index and
    # values live inline at r0+4, exactly as the runtime observer records them.
    assert canonical[0x003032:0x003040] == bytes.fromhex(
        "016883b001390160890009184968")

    # The primary native_stack handler reads the live cursor through [r1],
    # consumes one slot byte, writes the advanced cursor back, then dispatches.
    assert canonical[0x003CC0:0x003CD0] == bytes.fromhex(
        "0b681a7801330b6091009d4a515842f0")


def test_authored_body_is_novel_and_native_encoding_is_exact(canonical, variants):
    authored, _ = variants["authored"]
    assert canonical.count(AUTHORED_BODY) == 0
    assert authored.count(AUTHORED_BODY) == 1
    assert authored[SCRIPT_AT:SCRIPT_AT + len(AUTHORED_BODY)] == AUTHORED_BODY
    ir = disassemble(AUTHORED_BODY, (Entry("authored", 0),),
                     OPCODE_SETS["stack_be16_buu_v1"])
    assert ir.opaque == () and assemble(ir) == AUTHORED_BODY
    instructions = [i for block in ir.blocks for i in block.instructions]
    assert [i.opcode for i in instructions] == [0x1D, 0x02, 0x11]
    assert [o.value for o in instructions[0].operands] == [3, 1525, 120, 105]
    assert instructions[1].operands[0].value == NATIVE_SLOT


def test_production_reference_chain_is_exact(variants):
    authored, _ = variants["authored"]
    placement = PlacementRecord.from_bytes(authored[RECORD_AT:RECORD_AT + 32])
    assert placement.descriptor_pointer_raw == 0x08000000 + DESCRIPTOR_AT
    descriptor = DescriptorRecord.from_bytes(authored[DESCRIPTOR_AT:DESCRIPTOR_AT + 8])
    assert descriptor.handler_pointer_raw == SCRIPT_DISPATCH_HANDLER
    assert descriptor.payload_raw == 0x08000000 + SCRIPT_AT
    assert authored[descriptor.payload_raw - 0x08000000:
                    descriptor.payload_raw - 0x08000000 + len(AUTHORED_BODY)] == AUTHORED_BODY
    count = authored[0x8EBA4]
    array_at = struct.unpack_from("<I", authored, 0x8EBB4)[0] - 0x08000000
    assert count == 5 and array_at == ARRAY_AT
    assert struct.unpack_from(f"<{count}I", authored, array_at)[-1] == 0x08000000 + RECORD_AT


def test_allocation_demand_is_measured_and_fits(variants):
    authored, manifest = variants["authored"]
    placement = PlacementRecord.from_bytes(authored[RECORD_AT:RECORD_AT + 32])
    descriptor_at = placement.descriptor_pointer_raw - 0x08000000
    descriptor = DescriptorRecord.from_bytes(authored[descriptor_at:descriptor_at + 8])
    script_at = descriptor.payload_raw - 0x08000000
    array_at = struct.unpack_from("<I", authored, 0x8EBB4)[0] - 0x08000000
    count = authored[0x8EBA4]
    spans = sorted((
        ("record", RECORD_AT, 32),
        ("descriptor", descriptor_at, 8),
        ("script", script_at, len(AUTHORED_BODY)),
        ("array", array_at, count * 4),
    ), key=lambda item: item[1])
    assert spans == [
        ("record", RECORD_AT, 32),
        ("descriptor", DESCRIPTOR_AT, 8),
        ("script", SCRIPT_AT, 11),
        ("array", ARRAY_AT, 20),
    ]
    assert sum(size for _, _, size in spans) == 71
    assert REGION_END - max(start + size for _, start, size in spans) == 184
    assert all(REGION_START <= start < start + size <= REGION_END
               for _, start, size in spans)
    assert all(a_start + a_size <= b_start
               for (_, a_start, a_size), (_, b_start, _) in zip(spans, spans[1:]))
    assert manifest["base"]["profile_id"] == PROFILE


def test_three_variants_are_discriminating(variants):
    authored, _ = variants["authored"]
    negative, _ = variants["negative"]
    positive, _ = variants["positive"]
    assert authored[SCRIPT_AT:SCRIPT_AT + len(AUTHORED_BODY)] == AUTHORED_BODY
    assert negative[SCRIPT_AT:SCRIPT_AT + len(NEGATIVE_BODY)] == NEGATIVE_BODY
    assert positive[SCRIPT_AT:SCRIPT_AT + len(POSITIVE_BODY)] == POSITIVE_BODY
    assert bytes((0x02, 0xB2)) not in NEGATIVE_BODY
    assert len({hashlib.sha256(image).hexdigest()
                for image in (authored, negative, positive)}) == 3


def test_build_is_deterministic_and_canonical_noop_is_exact(tmp_path, variants, canonical):
    rebuilt, rebuilt_manifest = build_variant(
        tmp_path / "rebuilt", tmp_path / "rebuilt.gba", AUTHORED_SOURCE)
    authored, manifest = variants["authored"]
    assert rebuilt == authored
    assert rebuilt_manifest == manifest

    catalog = RomProfileCatalog.load(CATALOG)
    root = tmp_path / "noop"
    extract_project(ROM, root, catalog, graphics=False)
    output = tmp_path / "noop.gba"
    build_project(root, ROM, output, catalog)
    assert output.read_bytes() == canonical


def test_changed_bytes_are_bounded_and_canonical_is_immutable(canonical, variants):
    authored, _ = variants["authored"]
    changed = [i for i, (before, after) in enumerate(zip(canonical, authored))
               if before != after]
    assert len(changed) == 75
    assert set(i for i in changed if not REGION_START <= i < REGION_END) <= {
        0x8EBA4, *range(0x8EBB4, 0x8EBB8),
    }
    assert hashlib.sha256(ROM.read_bytes()).hexdigest() == CANONICAL_SHA
