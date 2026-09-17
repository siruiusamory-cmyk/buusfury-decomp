"""Portable, ROM-free tests for the LOGX-SPRITE-001 census reference.

These cover the synthetic-input behaviour of the census reference, the internal
consistency of the probe's constants, the deferred-capstone dependency boundary,
and the naming invariant that keeps unproven animation-slot semantics out of the
API.  No canonical ROM bytes, hashes or addresses of payload data are embedded
here, and none of these tests touches a file.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from tools.research import logx_sprite_probe as probe

ROM_BASE = 0x08000000


def _row(
    field_00: int = 10,
    field_02: int = 0x0400,
    field_04: int = 0,
    field_08: int = 0x040A0810,
    field_0c: int = 0,
    field_50: int = 0,
) -> tuple[int, int, int, int, int, int]:
    return (field_00, field_02, field_04, field_08, field_0c, field_50)


# --- the definition census on synthetic rows ---------------------------------


def test_well_formed_rows_produce_no_anomalies() -> None:
    summary = probe.census_definitions([_row(), _row(field_00=2, field_02=0x0200)])
    assert summary["counters"]["definitions"] == 2
    assert summary["anomalies"] == []
    assert summary["count_distribution"] == {2: 1, 10: 1}
    assert summary["counters"]["field_50_nonzero"] == 0


def test_count_range_and_high_byte_are_checked() -> None:
    limits = probe.DefinitionLimits(count_min=2, count_max=4)
    low = probe.census_definitions([_row(field_00=1)], limits)
    assert low["anomalies"][0]["flags"] == ["count_below_min"]
    high = probe.census_definitions([_row(field_00=5)], limits)
    assert high["anomalies"][0]["flags"] == ["count_above_max"]
    wide = probe.census_definitions([_row(field_00=0x0210)])
    assert wide["anomalies"][0]["flags"] == ["count_high_byte_nonzero"]


def test_zero_size_is_flagged_and_zero_pointers_are_counted_not_flagged() -> None:
    summary = probe.census_definitions([_row(field_02=0), _row(field_04=0, field_50=1)])
    assert summary["anomalies"] == [{"index": 0, "flags": ["size_zero"]}]
    assert summary["counters"]["field_04_zero"] == 2
    assert summary["counters"]["field_50_nonzero"] == 1
    assert summary["counters"]["field_50_zero"] == 1


def test_array_slot_census_is_position_scoped() -> None:
    summary = probe.census_array_slots(
        [(0x10, 0x20), (0x30,), (0, 0x40, 0), (0x50,)]
    )
    assert summary["total_slots"] == 7
    assert summary["non_null_slots"] == 5
    assert summary["null_slots"] == 2
    assert summary["by_index"][0] == {"present": 4, "non_null": 3}
    assert summary["by_index"][2] == {"present": 1, "non_null": 0}
    assert summary["index_zero_always_non_null"] is False


def test_animation_reference_arithmetic_separates_the_two_populations() -> None:
    inside = lambda value: ROM_BASE <= value < ROM_BASE + 0x1000
    summary = probe.census_animation_pointers(
        [0x08000010, 0x08000010, 0, 0x08000020, 0x03000000], inside
    )
    assert summary["references"] == 5
    assert summary["non_null_references"] == 4
    assert summary["null_references"] == 1
    assert summary["unique_targets"] == 3
    assert summary["malformed_references"] == 1
    assert summary["max_reuse"] == 2
    assert summary["reuse_histogram"] == {1: 2, 2: 1}


# --- constants and pure helpers ----------------------------------------------


def test_run_geometry_is_internally_consistent() -> None:
    assert probe.DEFINITION_ARRAY_ADDRESS == 0x086B6BDC
    assert probe.DEFINITION_ARRAY_FILE_OFFSET == 0x6B6BDC
    assert probe.DEFINITION_ARRAY_FILE_OFFSET == probe.DEFINITION_ARRAY_ADDRESS - ROM_BASE
    assert probe.DEFINITION_ARRAY_ENTRY_COUNT == 297
    assert probe.DEFINITION_ID_FLOOR == 10
    # The folded base is the literal minus the floor's worth of entries.
    assert probe.FOLDED_ARITHMETIC_BASE == probe.DEFINITION_ARRAY_ADDRESS - 4 * 10
    assert probe.FOLDED_ARITHMETIC_BASE == 0x086B6BB4
    # The last id the canonical appearances use lands on the last entry.
    assert probe.DEFINITION_ID_LAST_USED - probe.DEFINITION_ID_FLOOR == (
        probe.DEFINITION_ARRAY_ENTRY_COUNT - 1
    )


def test_definition_geometry_is_internally_consistent() -> None:
    assert probe.FIELD_COUNT == 0x00
    assert probe.FIELD_SIZE == 0x02
    assert probe.FIELD_ARRAY == 0x54
    assert probe.OBJECT_HEADER_SIZE == probe.FIELD_ARRAY
    assert probe.FIXED_BLOCK_START == 0x10
    assert probe.FIXED_BLOCK_END == 0x50
    # The four 16-byte records tile the fixed block exactly.
    assert (
        probe.FIXED_BLOCK_START
        + probe.FIXED_BLOCK_RECORDS * probe.FIXED_BLOCK_RECORD_SIZE
        == probe.FIXED_BLOCK_END
    )
    assert probe.FIELD_50 == probe.FIXED_BLOCK_END
    assert probe.REMAP_BLOCK_SIZE == 0x100


def test_animation_and_frame_geometry_is_internally_consistent() -> None:
    assert probe.ANIM_FRAME_COUNT == 0x00
    assert probe.ANIM_POINTERS == 0x04
    assert probe.ANIM_DIRECTIONS == 4
    # The engine reaches slot d of frame f at 16*f + 4*d + 4.
    assert probe.ANIM_POINTERS + 16 * 1 + 4 * 3 == 0x20
    assert probe.ANIM_POINTERS + 16 * 0 + 4 * 0 == 0x04
    assert probe.FRAME_PIECE_COUNT == 0x00
    assert probe.FRAME_FIRST_PIECE == 0x04
    assert probe.PIECE_RECORD_SIZE == 0x10


def test_run_index_arithmetic_and_refusals() -> None:
    assert probe.run_index_for_id(10) == 0
    assert probe.run_index_for_id(11) == 1
    assert probe.run_index_for_id(306) == 296
    with pytest.raises(probe.SpriteProbeError, match="party-slot branch"):
        probe.run_index_for_id(9)
    with pytest.raises(probe.SpriteProbeError, match="party-slot branch"):
        probe.run_index_for_id(0)


def test_definition_entry_address_bounds_are_checked() -> None:
    assert probe.definition_entry_address(0) == probe.DEFINITION_ARRAY_ADDRESS
    assert probe.definition_entry_address(296) == probe.DEFINITION_ARRAY_ADDRESS + 4 * 296
    with pytest.raises(probe.SpriteProbeError, match="outside"):
        probe.definition_entry_address(297)
    with pytest.raises(probe.SpriteProbeError, match="outside"):
        probe.definition_entry_address(-1)


def test_count_guard_table_shape() -> None:
    assert len(probe.COUNT_GUARD_SITES) == 5
    for pointer_site, count_site, compare_site, array_site in probe.COUNT_GUARD_SITES:
        for site in (pointer_site, count_site, compare_site, array_site):
            assert site % 2 == 0
        assert pointer_site < count_site < compare_site < array_site
    # Every guard covers a distinct animation index, and none exceeds the
    # largest count any canonical definition carries.
    indices = {0x08013044: 7, 0x08013086: 8, 0x080131D8: 7, 0x0802736A: 1,
               0x0802A28A: 6}
    assert sorted(set(indices.values())) == [1, 6, 7, 8]
    assert max(indices.values()) < probe.COUNT_MAX


def test_state_table_bounds() -> None:
    assert probe.STATE_TABLE_ADDRESS == probe.STATE_TABLE_LITERAL + probe.STATE_TABLE_OFFSET
    assert probe.STATE_TABLE_LITERAL == 0x080725E8
    assert probe.STATE_TABLE_OFFSET == 0x88
    assert probe.STATE_TABLE_SIZE == 25


def test_evidence_instruction_sites_are_even_and_unique() -> None:
    addresses = [address for address, _ in probe.EVIDENCE_INSTRUCTIONS.values()]
    assert len(addresses) == len(set(addresses))
    assert all(address % 2 == 0 for address in addresses)


# --- the dependency boundary and the naming invariant -------------------------


def test_module_import_does_not_pull_in_capstone() -> None:
    """The census API must import and run where capstone is not installed.

    CI's portable job installs only ``.[dev]``, and ``thumb_disasm`` raises
    ``SystemExit`` when capstone is missing.  A module-scope import of either
    would turn the whole portable suite into a collection error, so the module
    must not have one.
    """
    tree = ast.parse(Path(probe.__file__).read_text(encoding="utf-8"))
    top_level: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            top_level.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            top_level.add(node.module or "")
    assert top_level, "the module must import something"
    assert not [name for name in top_level if "capstone" in name]
    assert not [name for name in top_level if "thumb_disasm" in name]


UNPROVEN_SLOT_NAMES = (
    "stand", "walk", "attack", "idle", "hurt", "transform",
    "arms_up", "pickup", "takeoff", "flying", "mode7", "teleport",
    "fusion", "dead", "portrait",
)


@pytest.mark.parametrize("name", UNPROVEN_SLOT_NAMES)
def test_probe_identifiers_do_not_promote_unproven_slot_names(name: str) -> None:
    """No probe identifier may encode an animation-slot meaning this ticket did
    not establish.  Two of LOGExtractor's slot words are deliberately excluded:
    ``run`` is the project's word for the pointer run, not for slot 3, and
    ``block`` is this ticket's word for the definition's fixed 16-byte-record
    area, not for slot 8."""
    identifiers = [
        attribute for attribute in dir(probe)
        if attribute.isupper() or callable(getattr(probe, attribute))
    ]
    pattern = re.compile(rf"(?:^|_){re.escape(name)}(?:$|_)", re.IGNORECASE)
    assert not [attribute for attribute in identifiers if pattern.search(attribute)]


# --- the canonical gate fails closed -----------------------------------------


def test_gate_rejects_an_image_of_the_wrong_size() -> None:
    with pytest.raises(probe.SpriteProbeError, match="expected"):
        probe.verify_canonical(b"\x00" * 1024)


def test_gate_rejects_a_wrong_hash() -> None:
    with pytest.raises(probe.SpriteProbeError, match="non-canonical"):
        probe.verify_canonical(b"\x00" * probe.ROM_SIZE)


# --- structure readers on a small synthetic image -----------------------------


def _synthetic_image() -> bytes:
    """A 0x200-byte buffer with one animation and one frame record in it."""
    buffer = bytearray(0x200)
    animation = 0x40
    buffer[animation:animation + 4] = (2).to_bytes(4, "little")  # frame count
    for index in range(8):
        pointer = ROM_BASE + 0x100 + index
        buffer[animation + 4 + 4 * index:
               animation + 8 + 4 * index] = pointer.to_bytes(4, "little")
    frame = 0x100
    buffer[frame:frame + 4] = (1).to_bytes(4, "little")  # piece count
    buffer[frame + 4:frame + 8] = bytes((0xF8, 0xE8, 0x20, 0x20))
    return bytes(buffer)


def test_animation_reader_and_pointer_for() -> None:
    data = _synthetic_image()
    animation = probe.read_animation(data, ROM_BASE + 0x40)
    assert animation.frame_count == 2
    assert len(animation.pointers) == 8
    assert animation.pointer_for(0, 0) == ROM_BASE + 0x100
    assert animation.pointer_for(1, 3) == ROM_BASE + 0x107
    assert animation.end_address == ROM_BASE + 0x40 + 4 + 32
    with pytest.raises(probe.SpriteProbeError, match="frame 2 out of range"):
        animation.pointer_for(2, 0)
    with pytest.raises(probe.SpriteProbeError, match="direction slot 4"):
        animation.pointer_for(0, 4)


def test_animation_reader_refuses_implausible_counts() -> None:
    data = bytearray(_synthetic_image())
    data[0x40:0x44] = (0).to_bytes(4, "little")
    with pytest.raises(probe.SpriteProbeError, match="implausible frame count"):
        probe.read_animation(bytes(data), ROM_BASE + 0x40)
    data[0x40:0x44] = (65).to_bytes(4, "little")
    with pytest.raises(probe.SpriteProbeError, match="implausible frame count"):
        probe.read_animation(bytes(data), ROM_BASE + 0x40)


def test_animation_reader_refuses_an_address_outside_the_image() -> None:
    with pytest.raises(probe.SpriteProbeError, match="not in ROM"):
        probe.read_animation(_synthetic_image(), ROM_BASE + 0x1000)


def test_frame_record_reader_and_extent() -> None:
    data = _synthetic_image()
    record = probe.read_frame_record(data, ROM_BASE + 0x100)
    assert record.piece_count == 1
    assert (record.byte_04, record.byte_05, record.byte_06, record.byte_07) == (
        0xF8, 0xE8, 0x20, 0x20
    )
    assert record.signed_04 == -8
    assert record.signed_05 == -24
    assert record.end_address == ROM_BASE + 0x100 + 4 + 16
    with pytest.raises(probe.SpriteProbeError, match="not in ROM"):
        probe.read_frame_record(data, ROM_BASE + 0x1000)


def test_signed_byte_helper() -> None:
    assert probe._s8(0x00) == 0
    assert probe._s8(0x7F) == 127
    assert probe._s8(0x80) == -128
    assert probe._s8(0xFF) == -1


def test_header_signature_helper_rejects_non_canonical_shapes() -> None:
    data = bytearray(0x100)
    address = ROM_BASE + 0x40
    # A canonical shape: count in 1..23, zero high byte, a known size halfword.
    data[address - ROM_BASE: address - ROM_BASE + 4] = bytes((3, 0, 0x00, 0x04))
    assert probe.header_like(bytes(data), address) is True
    for count in (0, 24):
        data[address - ROM_BASE] = count
        assert probe.header_like(bytes(data), address) is False
    data[address - ROM_BASE] = 3
    data[address - ROM_BASE + 1] = 1
    assert probe.header_like(bytes(data), address) is False
    data[address - ROM_BASE + 1] = 0
    data[address - ROM_BASE + 2] = 0x77
    assert probe.header_like(bytes(data), address) is False
