"""Portable, synthetic regression tests for the LOGX-TILE-001 disassembly helpers.

These encode no ROM bytes and need no private input: they build the exact
halfword sequences the helper claims to recognise, so the mask-idiom scan and
the wide-window Thumb decode are pinned independently of any image.

The mask half of this file exists because the first draft of
``find_field_extractions`` accepted only a strictly larger second shift, which
made ``right_shift == 0`` unreachable: every ROM-gated assertion of the form
"no site masks the low *n* bits" was then vacuously true. These tests fail if
that regression returns.

The ROM-gated half of LOGX-TILE-001 lives in
``tests/integration/test_logx_tile_rom.py``.
"""

from __future__ import annotations

import struct

from tools.research.thumb_disasm import (
    FieldExtraction,
    decode_thumb_at,
    find_field_extractions,
    iter_thumb,
    linear_thumb_wide,
)

ROM_BASE = 0x08000000


def _thumb(*halfwords: int) -> bytes:
    return b"".join(struct.pack("<H", halfword) for halfword in halfwords)


def _scan(image: bytes) -> list[FieldExtraction]:
    return find_field_extractions(image, ROM_BASE, ROM_BASE + len(image))


def test_the_mask_idiom_is_reported_for_the_low_ten_bits() -> None:
    # lsls r0,r0,#0x16 ; lsrs r0,r0,#0x16  ->  value & 0x3FF
    found = _scan(bytes(0x100) + _thumb(0x0580, 0x0D80))
    assert found == [FieldExtraction(address=ROM_BASE + 0x100, right_shift=0, width=10)]
    assert found[0].mask == 0x03FF


def test_the_mask_idiom_is_reported_for_the_low_four_bits() -> None:
    # lsls r2,r2,#0x1C ; lsrs r2,r2,#0x1C  ->  value & 0xF
    found = _scan(bytes(0x20) + _thumb(0x0712, 0x0F12))
    assert [(item.right_shift, item.width) for item in found] == [(0, 4)]
    assert found[0].mask == 0x000F


def test_a_true_field_extraction_is_reported_for_bit_ten() -> None:
    # lsls r1,r1,#0x15 ; lsrs r1,r1,#0x1F  ->  (value >> 10) & 1
    found = _scan(bytes(0x40) + _thumb(0x0549, 0x0FC9))
    assert [(item.right_shift, item.width) for item in found] == [(10, 1)]
    assert found[0].mask == 0x0001


def test_a_true_field_extraction_is_reported_for_the_high_nibble() -> None:
    # lsls r2,r2,#0x10 ; lsrs r2,r2,#0x1C  ->  (value >> 12) & 0xF
    found = _scan(bytes(0x40) + _thumb(0x0412, 0x0F12))
    assert [(item.right_shift, item.width) for item in found] == [(12, 4)]
    assert found[0].mask == 0x000F


def test_pairs_that_do_not_share_a_destination_are_ignored() -> None:
    # lsls r0,r0,#0x16 ; lsrs r1,r0,#0x16  ->  the second shift writes r1, so
    # the pair is not a mask of the value the first shift produced.
    assert _scan(_thumb(0x0580, 0x0D81)) == []


def test_a_pair_reading_an_unrelated_register_is_still_reported() -> None:
    # lsls r0,r1,#0x16 ; lsrs r0,r0,#0x16  ->  the source differs but the
    # destination matches, so this is a mask of r0 either way.
    found = _scan(_thumb(0x0588, 0x0D80))
    assert [(item.right_shift, item.width) for item in found] == [(0, 10)]


def test_a_shift_by_thirty_two_is_not_a_field_extraction() -> None:
    # lsrs r0,r0,#0 encodes "shift by 32", which is not a mask
    assert _scan(_thumb(0x0580, 0x0800)) == []


def test_a_net_left_shift_pair_is_not_reported() -> None:
    # lsls r0,r0,#0x16 ; lsrs r0,r0,#0x10  ->  b < a, so this shifts left
    assert _scan(_thumb(0x0580, 0x0C00)) == []


def test_the_wide_sweep_decodes_a_two_halfword_instruction() -> None:
    # push {lr} ; bl +0 ; pop {pc}
    image = _thumb(0xB500, 0xF000, 0xF800, 0xBD00)
    wide = linear_thumb_wide(image, ROM_BASE, ROM_BASE + len(image))
    assert wide.undecodable_halfwords == []
    assert [item.mnemonic for item in wide.instructions] == ["push", "bl", "pop"]
    assert [item.size for item in wide.instructions] == [2, 4, 2]

    # The legacy two-byte sweep cannot see the two-halfword instruction.
    narrow = list(iter_thumb(image, ROM_BASE, ROM_BASE + len(image)))
    assert any(isinstance(item, int) for item in narrow)


def test_decode_thumb_at_returns_none_outside_the_image() -> None:
    assert decode_thumb_at(_thumb(0x46C0), ROM_BASE + 0x100) is None


def test_the_scan_range_is_respected() -> None:
    image = bytes(0x40) + _thumb(0x0580, 0x0D80) + bytes(0x40)
    assert find_field_extractions(image, ROM_BASE, ROM_BASE + 0x40) == []
    assert len(find_field_extractions(image, ROM_BASE, ROM_BASE + 0x44)) == 1
    assert len(_scan(image)) == 1
