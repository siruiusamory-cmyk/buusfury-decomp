import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import thumb_annotate  # noqa: E402

BASE = 0x08000000


def image() -> bytes:
    rom = bytearray(0x204)
    struct.pack_into("<H", rom, 0x100, 0x4800 | 0x3F)
    struct.pack_into("<H", rom, 0x102, 0x2000)
    struct.pack_into("<I", rom, 0x200, 0x08001000)
    return bytes(rom)


def test_a_pc_relative_load_is_resolved_to_its_literal_and_value():
    rows = thumb_annotate.annotate(image(), 0x100, 4)
    assert rows[0][0] == BASE + 0x100
    assert rows[0][3] == 0x200
    assert rows[0][4] == 0x08001000


def test_an_instruction_without_a_pc_relative_operand_carries_no_literal():
    rows = thumb_annotate.annotate(image(), 0x102, 2)
    assert rows[0][3] is None and rows[0][4] is None


def test_a_literal_offset_names_the_pc_relative_operand_arithmetic():
    assert thumb_annotate.literal_of(BASE + 0x100, "r0, [pc, #0xfc]") == BASE + 0x200
    assert thumb_annotate.literal_of(BASE + 0x100, "r0, [r1, #4]") is None
