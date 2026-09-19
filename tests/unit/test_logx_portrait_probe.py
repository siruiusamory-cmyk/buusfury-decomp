"""Portable synthetic tests for the GRAPHICS-COVERAGE-001 portrait enumerator.

No ROM is required. A tiny synthetic image is assembled with a portrait-array
pool word, a bounded pointer array and stored-form containers, and the probe's
walk, bounding and decode paths are asserted against it. Container decoding is
covered by the project codec's own tests; here we only assert the enumeration.
"""

from __future__ import annotations

import struct

import pytest

from tools.research import logx_portrait_probe as pp

GBA_BASE = pp.GBA_BASE


def _stored_container(payload: bytes) -> bytes:
    """A form-0 (stored) Webfoot container: kind 0, declared size, raw bytes."""
    return struct.pack("<II", 0, len(payload)) + payload


def _build_image(pointer_slots: list[int], *, pool_target: int) -> bytearray:
    """Assemble a synthetic image large enough to hold the array and containers."""
    size = 0x40000
    data = bytearray(b"\x00" * size)

    def put_word(addr: int, value: int) -> None:
        struct.pack_into("<I", data, addr - GBA_BASE, value)

    # The accessor's pool word points at the array base.
    put_word(pp.PORTRAIT_ARRAY_POOL_WORD, pool_target)

    # Lay the array at pool_target: slots 0..7 zero, then the given pointers,
    # then a non-pointer terminator (mirrors the real 0x0011E502 sentinel).
    for slot in range(pp.FIRST_ARRAY_SLOT):
        put_word(pool_target + 4 * slot, 0)
    for i, ptr in enumerate(pointer_slots):
        put_word(pool_target + 4 * (pp.FIRST_ARRAY_SLOT + i), ptr)
    put_word(pool_target + 4 * (pp.FIRST_ARRAY_SLOT + len(pointer_slots)), 0x0011E502)
    return data


def test_array_base_read_from_engine_pool_word() -> None:
    target = GBA_BASE + 0x10000
    data = _build_image([], pool_target=target)
    assert pp.portrait_array_base(bytes(data)) == target


def test_walk_bounds_itself_at_first_non_pointer() -> None:
    # Three real pointers then the sentinel; the walk must stop after three.
    ptrs = [GBA_BASE + 0x20000, GBA_BASE + 0x20100, GBA_BASE + 0x20200]
    data = _build_image(ptrs, pool_target=GBA_BASE + 0x10000)
    assert pp.portrait_pointers(bytes(data)) == ptrs


def test_skips_the_leading_zero_slots() -> None:
    # A pointer placed in slot 0..7 must not be returned: the walk starts at 8.
    target = GBA_BASE + 0x10000
    data = _build_image([GBA_BASE + 0x20000], pool_target=target)
    struct.pack_into("<I", data, target - GBA_BASE, GBA_BASE + 0x21000)  # slot 0
    assert pp.portrait_pointers(bytes(data)) == [GBA_BASE + 0x20000]


def test_enumerate_decodes_stored_containers() -> None:
    target = GBA_BASE + 0x10000
    c0 = GBA_BASE + 0x20000
    c1 = GBA_BASE + 0x20800
    data = _build_image([c0, c1], pool_target=target)
    payload_a = bytes(range(64))
    payload_b = bytes(range(128))
    data[c0 - GBA_BASE : c0 - GBA_BASE + len(_stored_container(payload_a))] = (
        _stored_container(payload_a)
    )
    data[c1 - GBA_BASE : c1 - GBA_BASE + len(_stored_container(payload_b))] = (
        _stored_container(payload_b)
    )
    report = pp.enumerate_portraits(bytes(data))
    assert report["portrait_count"] == 2
    assert report["decode_failures"] == 0
    assert report["container_kinds"] == {0: 2}
    assert set(report["decoded_sizes"]) == {64, 128}
    assert report["packed_extent_overlaps"] == 0


def test_refuses_non_canonical_image(tmp_path) -> None:
    bad = tmp_path / "not-the-rom.gba"
    bad.write_bytes(b"\x00" * 1024)
    with pytest.raises(SystemExit):
        pp.load_rom(bad)


# --- PORTRAIT-COMPLETENESS-001: the field-to-run join -------------------------
#
# The join is pure arithmetic over the appearance table's portrait field, so
# every branch - no portrait, reserved slot, in-run slot, out-of-run slot - is
# exercised here without a ROM.


def test_join_counts_references_inside_and_unused_run_entries() -> None:
    report = pp.join_portrait_references([0, 8, 162, 0, 8])
    assert report["records"] == 5
    assert report["with_reference"] == 3
    assert report["without_reference"] == 2
    assert report["references"] == 3
    assert report["unique_references"] == 2
    assert report["min_in_run_reference"] == 8
    assert report["max_in_run_reference"] == 162
    assert report["min_non_zero_reference"] == 8
    assert report["max_non_zero_reference"] == 162
    assert report["references_inside_run"] == 3
    assert report["references_outside_run"] == 0
    assert report["reserved_references"] == 0
    assert report["run_entries"] == 155
    assert report["run_entries_referenced"] == 2
    assert report["run_entries_unused"] == 153
    assert 8 not in report["unused_slots"]
    assert 162 not in report["unused_slots"]
    assert report["references_outside_run_is_empty"] is True


def test_join_separates_reserved_slots_from_the_run() -> None:
    # 1..7 cannot select a run entry: the accessor returns 0 for 0 and 7 and
    # takes its party path for 1..6, so a reserved value is neither inside nor
    # outside the run and must not be silently counted as either.
    report = pp.join_portrait_references([3, 7, 0])
    assert report["reserved_references"] == 2
    assert report["reserved_values"] == [3, 7]
    assert report["references_inside_run"] == 0
    assert report["references_outside_run"] == 0
    assert report["run_entries_referenced"] == 0
    assert report["run_entries_unused"] == 155
    # with_reference is "non-zero field", so reserved values are included there
    # and excluded from both the inside and the outside buckets.
    assert report["with_reference"] == report["reserved_references"]


def test_join_reports_references_past_the_run() -> None:
    report = pp.join_portrait_references([162, 163, 400])
    assert report["references_outside_run"] == 2
    assert report["outside_values"] == [163, 400]
    assert report["references_outside_run_is_empty"] is False
    assert report["references_inside_run"] == 1
    assert report["run_entries_unused"] == 154
    # The in-run range must not be read as the population range.
    assert report["max_in_run_reference"] == 162
    assert report["max_non_zero_reference"] == 400


def test_join_rejects_negative_values_instead_of_mis_bucketing() -> None:
    # A negative field is impossible through a `ldr` u32 read, so it is caller
    # error; bucketing it would produce with_reference != sum-of-buckets.
    with pytest.raises(ValueError, match="negative"):
        pp.join_portrait_references([-5, 8])


def test_join_handles_an_empty_population() -> None:
    report = pp.join_portrait_references([])
    assert report["records"] == 0
    assert report["with_reference"] == 0
    assert report["unique_references"] == 0
    assert report["min_in_run_reference"] is None
    assert report["max_in_run_reference"] is None
    assert report["min_non_zero_reference"] is None
    assert report["run_entries"] == 155
    assert report["run_entries_unused"] == 155


def test_join_respects_custom_run_bounds() -> None:
    report = pp.join_portrait_references([1, 2, 4, 5], first_run_slot=2, last_run_slot=4)
    assert report["run_entries"] == 3
    assert report["reserved_values"] == [1]
    assert report["outside_values"] == [5]
    assert report["run_entries_referenced"] == 2
    assert report["unused_slots"] == [3]


@pytest.mark.parametrize(
    ("first", "last"),
    [(0, 8), (8, 7), (-1, 4)],
)
def test_join_rejects_impossible_run_bounds(first: int, last: int) -> None:
    with pytest.raises(ValueError):
        pp.join_portrait_references([8], first_run_slot=first, last_run_slot=last)


def test_declared_population_matches_the_accepted_census() -> None:
    from tools.research import logx_char_probe as cp

    assert pp.APPEARANCE_TABLE_ADDRESS == cp.CHAR_TABLE_ADDRESS == 0x0874D380
    assert pp.APPEARANCE_RECORD_COUNT == cp.CHAR_RECORD_COUNT == 232
    assert pp.APPEARANCE_RECORD_SIZE == cp.CHAR_RECORD_SIZE == 0x10
    assert pp.APPEARANCE_PORTRAIT_OFFSET == cp.FIELD_08 == 0x08
    assert pp.DEFINITION_RUN_ADDRESS == 0x086B6BDC
    assert pp.DEFINITION_RUN_COUNT == 297
    assert pp.FIRST_ARRAY_SLOT == 8
    assert pp.PORTRAIT_ARRAY_POOL_WORD == 0x08012194


def _image_with_halfwords(words: dict[int, int], size: int = 0x1000) -> bytes:
    data = bytearray(size)
    for address, halfword in words.items():
        struct.pack_into("<H", data, address - GBA_BASE, halfword)
    return bytes(data)


def test_ldr_literal_pool_computes_the_pc_relative_word() -> None:
    # ``ldr r1, [pc, #0x10]`` at a word-aligned site: pool = site + 4 + 0x10.
    site = GBA_BASE + 0x100
    data = _image_with_halfwords({site: 0x4904})
    pool, register = pp.thumb_ldr_literal_pool(data, site)
    assert pool == site + 4 + 0x10
    assert register == 1
    assert pool % 4 == 0


def test_ldr_literal_pool_refuses_another_encoding() -> None:
    site = GBA_BASE + 0x100
    data = _image_with_halfwords({site: 0x2800})  # cmp r0, #0
    with pytest.raises(ValueError):
        pp.thumb_ldr_literal_pool(data, site)


def test_bl_target_decodes_forward_and_backward() -> None:
    # Forward: 0xF000/0xF810 encodes a +0x20 displacement.
    forward = GBA_BASE + 0x200
    data = _image_with_halfwords({forward: 0xF000, forward + 2: 0xF810})
    assert pp.thumb_bl_target(data, forward) == forward + 4 + 0x20
    # Backward: 0xF7FF/0xFFFE encodes -4, i.e. a bl to its own address.
    backward = GBA_BASE + 0x300
    data = _image_with_halfwords({backward: 0xF7FF, backward + 2: 0xFFFE})
    assert pp.thumb_bl_target(data, backward) == backward


def test_bl_target_refuses_a_non_bl_pair() -> None:
    site = GBA_BASE + 0x400
    data = _image_with_halfwords({site: 0x2800, site + 2: 0x2800})
    with pytest.raises(ValueError):
        pp.thumb_bl_target(data, site)


def test_bl_target_refuses_a_thumb2_second_halfword_shape() -> None:
    # 0xF0xx followed by 0xD0xx is not an ARMv4T bl: bit 13 is J1 in Thumb-2 but
    # a fixed 1 in ARMv4T, so accepting it would decode a bogus target.
    site = GBA_BASE + 0x500
    data = _image_with_halfwords({site: 0xF000, site + 2: 0xD000})
    with pytest.raises(ValueError):
        pp.thumb_bl_target(data, site)


def test_bl_target_accepts_every_armv4t_second_halfword_class() -> None:
    # The ARMv4T shape is 11111 in the top five bits of the second halfword.
    for second in (0xF800, 0xFD47, 0xFF25, 0xFFFE):
        site = GBA_BASE + 0x600
        data = _image_with_halfwords({site: 0xF7EC, site + 2: second})
        assert isinstance(pp.thumb_bl_target(data, site), int)
