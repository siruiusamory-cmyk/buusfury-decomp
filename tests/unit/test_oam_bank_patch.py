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
        ("adds", "r0, #2"),
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
    image[offset:offset + patch.BLOCK_BYTES] = patch.EXPECTED_BLOCK
    resume_before = bytes(image[offset + patch.BLOCK_BYTES:offset + patch.BLOCK_BYTES + 4])
    base_length = len(image)

    stub_address, original = patch.patch(image)
    assert original == patch.EXPECTED_BLOCK
    assert len(image) == base_length + 52
    entry = bytes(image[offset:offset + patch.BLOCK_BYTES])
    assert len(entry) == patch.BLOCK_BYTES
    assert entry[0:2] == bytes.fromhex("014b"), "a PC-relative load, so the stub can live above EOF"
    assert entry[10:12] == bytes.fromhex("1847"), "and bx r3, which has full range"
    loaded = struct.unpack_from("<I", image, offset + 6)[0]
    assert loaded == ((stub_address + patch.ROM_BASE) | 1), (
        "the entry loads the stub as a GBA ADDRESS with the thumb bit set: a file offset here jumps into "
        "unmapped memory and hangs the game, which is how this was caught")
    assert bytes(image[offset + patch.BLOCK_BYTES:offset + patch.BLOCK_BYTES + 4]) == resume_before, (
        "the piece advance at the resume address is untouched")


def test_the_stub_returns_to_the_resume_address_absolutely() -> None:
    image = aligned(patch.BLOCK_SITE - patch.ROM_BASE + 0x100)
    offset = patch.BLOCK_SITE - patch.ROM_BASE
    image[offset:offset + patch.BLOCK_BYTES] = patch.EXPECTED_BLOCK
    stub_address, _ = patch.patch(image)
    # The body is padded to a multiple of four so the return load's PC-relative base IS the literal.
    layout = patch.stub_layout(stub_address)
    literal = struct.unpack_from("<I", image, layout["literal_at"])[0]
    assert literal == patch.RESUME + 1, (
        "an absolute return, because a thumb b cannot reach above EOF from the code region")


def test_a_second_patch_is_refused_rather_than_silently_applied_again() -> None:
    """The guard is the block's own content: a second run finds the entry, not the retail sequence."""
    image = aligned(patch.BLOCK_SITE - patch.ROM_BASE + 0x100)
    offset = patch.BLOCK_SITE - patch.ROM_BASE
    image[offset:offset + patch.BLOCK_BYTES] = patch.EXPECTED_BLOCK
    first_stub, _ = patch.patch(image)
    assert first_stub % 4 == 0
    with pytest.raises(AssertionError, match="not the retail sequence"):
        patch.patch(image)


def test_an_image_whose_block_is_unexpected_is_refused() -> None:
    image = aligned(patch.BLOCK_SITE - patch.ROM_BASE + 0x100)
    with pytest.raises(AssertionError, match="not the retail sequence"):
        patch.patch(image)
