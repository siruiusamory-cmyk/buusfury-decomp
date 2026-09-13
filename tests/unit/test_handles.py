"""WORKBENCH-001 T0.4: unit proofs for the extracted packed-handle API.

`unpack_handle` is pure bit-slicing and is tested on known and synthetic words.
`recover_handle` reads the real `CONTRACTS` pool/table offsets, so its round
trip is exercised against a SYNTHETIC full-size image with one handle word
planted in the record pool - no commercial ROM bytes, and no fixture file. The
function only ever reads the pool region between two fixed offsets, so a zeroed
image large enough to hold that region is a faithful stand-in.
"""

from __future__ import annotations

import struct

from tools.webfoot.binary import GBA_ROM_BASE
from tools.webfoot.data.placement_contracts import CONTRACTS
from tools.webfoot.handles import (HANDLE_LENGTH_SHIFT, HANDLE_SELECTOR_MASK,
                                    HANDLE_START_MASK, HANDLE_START_SHIFT,
                                    recover_handle, unpack_handle)


def pack(selector: int, start_halfwords: int, length_halfwords: int) -> int:
    """Build a handle word from its three fields (the inverse of unpack)."""
    return (selector & HANDLE_SELECTOR_MASK) \
        | ((start_halfwords & HANDLE_START_MASK) << HANDLE_START_SHIFT) \
        | (length_halfwords << HANDLE_LENGTH_SHIFT)


def test_unpack_handle_critical_path():
    # Critical-path test 1: the canonical word decodes to (selector, start
    # bytes, length bytes) = (1, 0x132, 0x20) = (1, 306, 32).
    assert unpack_handle(0x02002641) == (1, 306, 32)


def test_unpack_handle_zero():
    assert unpack_handle(0x00000000) == (0, 0, 0)


def test_unpack_handle_field_isolation():
    # Selector-only, start-only, length-only words each move exactly one field.
    assert unpack_handle(0x0000003F) == (0x3F, 0, 0)          # all selector bits
    assert unpack_handle(HANDLE_START_MASK << HANDLE_START_SHIFT) == (
        0, HANDLE_START_MASK * 2, 0)
    assert unpack_handle(1 << HANDLE_LENGTH_SHIFT) == (0, 0, 2)


def test_unpack_handle_round_trip_through_pack():
    for selector, start_hw, length_hw in [(1, 0x99, 0x10), (5, 0, 1),
                                          (0x3F, 0x7FFF, 0x7FF)]:
        value = pack(selector, start_hw, length_hw)
        assert unpack_handle(value) == (selector, start_hw * 2, length_hw * 2)


def test_recover_handle_out_of_bounds_image():
    # An image too small to hold the record pool is reported, never guessed.
    result = recover_handle(b"\x00" * 0x100, 1, 306, 32)
    assert result["packed_handle"] is None
    assert "outside this image" in result["unrecovered_because"]


def test_recover_handle_round_trip_synthetic_pool():
    # A synthetic full-size image with ONE handle word planted in the real
    # event-resource pool. recover_handle should name exactly that handle for a
    # phrase span contained in the handle's decoded span.
    resource = CONTRACTS["buus_fury_usa_rev0_01c1707f"]["event_resource"]
    pool = resource["pool_start"] - GBA_ROM_BASE
    table = resource["table"] - GBA_ROM_BASE
    image = bytearray(table + 0x100)

    selector, start_hw, length_hw = 1, 0x99, 0x10   # start 306 bytes, len 32 bytes
    handle = pack(selector, start_hw, length_hw)
    site = pool + 0x40
    struct.pack_into("<I", image, site, handle)

    # A phrase fully inside the handle's decoded span [306, 306+32).
    result = recover_handle(bytes(image), selector, 306, 8)
    assert result["packed_handle"] == f"0x{handle:08X}"
    assert result["handle_selector"] == selector
    assert result["handle_decoded_start"] == "0x132"
    assert result["handle_decoded_length"] == "0x20"
    assert result["reference_sites"] == [f"0x{GBA_ROM_BASE + site:08X}"]
    assert result["reference_site_count"] == 1


def test_recover_handle_span_no_record_covers():
    # A span no planted handle covers reports its absence rather than guessing.
    resource = CONTRACTS["buus_fury_usa_rev0_01c1707f"]["event_resource"]
    pool = resource["pool_start"] - GBA_ROM_BASE
    table = resource["table"] - GBA_ROM_BASE
    image = bytearray(table + 0x100)
    struct.pack_into("<I", image, pool + 0x40, pack(1, 0x99, 0x10))

    result = recover_handle(bytes(image), 1, 0x4000, 8)  # far outside the span
    assert result["packed_handle"] is None
    assert "no event-resource record" in result["unrecovered_because"]
