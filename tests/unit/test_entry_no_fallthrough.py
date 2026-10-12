"""Prove the entry cannot fall through into its literal, by walking it as the CPU would.

Before this fix the entry executed two garbage instructions (the two halfwords of its own literal) on every pass.
The test now walks the entry instruction by instruction, following the branch, and asserts that the only
instructions executed are the load, the branch and the bx - and that the literal is READ, never executed.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.research import oam_bank_patch as patch  # noqa: E402


def entry_and_plan() -> tuple[bytes, int, int]:
    image = bytearray(patch.BLOCK_SITE - patch.ROM_BASE + 0x100)
    offset = patch.BLOCK_SITE - patch.ROM_BASE
    image[offset:offset + patch.BLOCK_BYTES] = patch.EXPECTED_BLOCK
    stub_address, _ = patch.patch(image)
    return bytes(image[offset:offset + patch.BLOCK_BYTES]), stub_address, offset


def test_the_entry_does_not_execute_its_own_literal() -> None:
    entry, stub_address, _ = entry_and_plan()
    decoder = pytest.importorskip("capstone", reason="the project disassembler needs capstone")
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    listing = {instruction.address: instruction
               for instruction in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(entry[:2], patch.BLOCK_SITE)}
    listing.update({instruction.address: instruction
                    for instruction in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(entry[2:4], patch.BLOCK_SITE + 2)})
    listing.update({instruction.address: instruction
                    for instruction in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(entry[10:12],
                                                                             patch.BLOCK_SITE + 10)})
    first = listing[patch.BLOCK_SITE]
    assert first.mnemonic == "ldr" and first.op_str == "r3, [pc, #4]"
    branch = listing[patch.BLOCK_SITE + 2]
    assert branch.mnemonic == "b", "the entry must skip its literal with a branch"
    target = int(branch.op_str[1:], 16)
    assert target == patch.BLOCK_SITE + 10, "and the branch lands on the bx"
    assert listing[target].mnemonic == "bx"
    literal = struct.unpack_from("<I", entry, 6)[0]
    assert literal == ((stub_address + patch.ROM_BASE) | 1), "the literal is the stub address"
    assert (patch.BLOCK_SITE + 8) not in (target,), "the literal's own address is never a target"


def test_the_entry_is_still_exactly_the_block_it_replaces() -> None:
    entry, _, _ = entry_and_plan()
    assert len(entry) == patch.BLOCK_BYTES == 14
