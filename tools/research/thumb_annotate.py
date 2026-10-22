"""Annotated Thumb decode: every pc-relative literal load resolved to the value it reads.

Deciding what a cited loader does needs the literal's VALUE next to the instruction, and the
project's Ghidra database is a hypothesis (P-011). This decodes the raw bytes with capstone and
prints the halfword, the instruction and, for `ldr/ldrh/ldrb rX,[pc,#imm]`, the literal's file
offset and value.

    python tools/research/thumb_annotate.py --rom baserom.gba --start 0x36A86 --length 0x30
"""

from __future__ import annotations

import argparse
import re
import struct
import sys

import capstone

ROM_BASE = 0x08000000
PC_RELATIVE = re.compile(r"\[pc, #(0x[0-9a-f]+)\]")


def literal_of(address: int, operand: str):
    match = PC_RELATIVE.search(operand)
    if not match:
        return None
    return ((address + 4) & ~3) + int(match.group(1), 16)


def annotate(rom: bytes, start: int, length: int, base: int = ROM_BASE) -> list[tuple]:
    engine = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    rows = []
    for ins in engine.disasm(rom[start:start + length], base + start):
        literal = value = None
        if ins.mnemonic in ("ldr", "ldrh", "ldrb"):
            target = literal_of(ins.address, ins.op_str)
            if target is not None and base <= target + 4 <= base + len(rom):
                literal = target - base
                value = struct.unpack_from("<I", rom, literal)[0]
        rows.append((ins.address, ins.bytes.hex(), ins.mnemonic + " " + ins.op_str, literal, value))
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", default="baserom.gba")
    parser.add_argument("--start", required=True, type=lambda text: int(text, 16))
    parser.add_argument("--length", required=True, type=lambda text: int(text, 16))
    parser.add_argument("--base", default="0x08000000", type=lambda text: int(text, 16))
    args = parser.parse_args(argv)
    rom = open(args.rom, "rb").read()
    for address, halfwords, text, literal, value in annotate(rom, args.start, args.length,
                                                             args.base):
        note = "" if literal is None else "   ; lit 0x%06X = 0x%08X" % (literal, value)
        print("%08X  %-10s %-22s%s" % (address, halfwords, text, note))
    return 0


if __name__ == "__main__":
    sys.exit(main())
