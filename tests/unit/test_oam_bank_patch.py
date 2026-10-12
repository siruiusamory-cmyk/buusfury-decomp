"""The palette-bank patch's rules, proven with no ROM and no emulator.

The stub is hand-assembled, so the test does what the build does: disassemble it and require the exact
mnemonic sequence, then check the entry layout, the absolute return, and that the patched image leaves the
resume address untouched. Capstone is required by the project's own disassembler, so the test skips with a
reason rather than failing when it is absent.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.research import oam_bank_patch as patch  # noqa: E402


def test_the_stub_disassembles_to_the_intended_instructions() -> None:
    decoder = pytest.importorskip("capstone", reason="the project disassembler needs capstone")
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    listing = [(instruction.mnemonic, instruction.op_str)
               for instruction in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(patch.STUB, patch.ROM_BASE)]
    assert listing == [
        ("lsrs", "r6, r6, #0xa"),
        ("lsls", "r6, r6, #0xa"),
        ("ldr", "r3, [r1]"),
        ("lsrs", "r7, r3, #0x19"),
        ("movs", "r3, #7"),
        ("ands", "r7, r3"),
        ("lsls", "r7, r7, #0xc"),
        ("movs", "r3, #0xf0"),
        ("lsls", "r3, r3, #8"),
        ("bics", "r6, r3"),
        ("orrs", "r6, r7"),
        ("mov", "r3, lr"),
        ("lsls", "r3, r3, #0x16"),
        ("lsrs", "r3, r3, #0x16"),
        ("orrs", "r6, r3"),
        ("str", "r6, [r1, #4]"),
        ("ldr", "r3, [r1]"),
        ("movs", "r7, #7"),
        ("lsls", "r7, r7, #0x19"),
        ("bics", "r3, r7"),
        ("str", "r3, [r1]"),
    ], "every opcode is asserted, so a typo cannot silently become another instruction"


def test_the_stub_clears_attr2_masks_and_carries_the_bank_bits() -> None:
    text = patch.STUB.hex()
    assert "b60a" in text and "b602" in text, "attr2 bits 0..9 are cleared before the tile is set"
    assert "f023" in text and "1b02" in text and "9e43" in text, (
        "0xF000 is built and bics'd, so the WHOLE attr2 nibble 12..15 is cleared, not just the low bits")
    assert "5f0e" in text, "the bank is read from OAM word 0 bits 25..27, the piece word's attr1 9..11"
    assert "3f03" in text, "and shifted into attr2 bits 12..14"
    assert "0b60" in text, "word 0 is written back"


def aligned(length: int) -> bytearray:
    """A blank image whose length is word aligned, which the patch requires for its own return literal."""
    return bytearray(length + ((-length) % 4))


def test_the_patch_replaces_exactly_the_block_and_points_at_a_stub_before_the_resume() -> None:
    image = aligned(0x1000 + patch.BLOCK_SITE - patch.ROM_BASE)
    offset = patch.BLOCK_SITE - patch.ROM_BASE
    image[offset:offset + patch.BLOCK_BYTES] = b"\xaa" * patch.BLOCK_BYTES
    resume_before = bytes(image[offset + patch.BLOCK_BYTES:offset + patch.BLOCK_BYTES + 4])
    base_length = len(image)

    stub_address, original = patch.patch(image)
    assert original == b"\xaa" * patch.BLOCK_BYTES
    assert len(image) == base_length + 50
    entry = bytes(image[offset:offset + patch.BLOCK_BYTES])
    assert len(entry) == patch.BLOCK_BYTES
    assert entry[0:2] == bytes.fromhex("014b"), "a PC-relative load, so the stub can live above EOF"
    assert entry[10:12] == bytes.fromhex("1847"), "and bx r3, which has full range"
    loaded = struct.unpack_from("<I", image, offset + 6)[0]
    assert loaded == (stub_address | 1), "the entry loads the stub address with the thumb bit set"
    assert bytes(image[offset + patch.BLOCK_BYTES:offset + patch.BLOCK_BYTES + 4]) == resume_before, (
        "the piece advance at the resume address is untouched")


def test_the_stub_returns_to_the_resume_address_absolutely() -> None:
    image = aligned(patch.BLOCK_SITE - patch.ROM_BASE + 0x100)
    stub_address, _ = patch.patch(image)
    # The stub body is the instructions plus the ldr/bx pair, so the literal follows at STUB + 4.
    literal = struct.unpack_from("<I", image, stub_address + len(patch.STUB) + 4)[0]
    assert literal == patch.RESUME + 1, (
        "an absolute return, because a thumb b cannot reach above EOF from the code region")


def test_a_second_patch_is_refused_rather_than_silently_applied_again() -> None:
    """The first patch grows the image by 50 bytes, so the stub can no longer start word aligned.

    That accident is a useful property: a double patch stops at an assertion instead of appending a second stub
    and replacing an entry the first run already wrote.
    """
    image = aligned(patch.BLOCK_SITE - patch.ROM_BASE + 0x100)
    first_stub, _ = patch.patch(image)
    with pytest.raises(AssertionError):
        patch.patch(image)
    assert first_stub % 4 == 0
