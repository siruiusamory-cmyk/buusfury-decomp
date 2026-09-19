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
