from __future__ import annotations

import os
import struct
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import testkit

import harness

BASE = harness.ROM_BASE
LR = 14


def program(*halfwords):
    return struct.pack("<%dH" % len(halfwords), *halfwords)


def movs(rd, imm):
    return 0x2000 | (rd << 8) | (imm & 0xFF)


def adds(rd, imm):
    return 0x3000 | (rd << 8) | (imm & 0xFF)


def subs(rd, imm):
    return 0x3800 | (rd << 8) | (imm & 0xFF)


def cmp(rd, imm):
    return 0x2800 | (rd << 8) | (imm & 0xFF)


def lsls(rd, rs, imm):
    return ((imm & 0x1F) << 6) | ((rs & 7) << 3) | (rd & 7)


def asrs(rd, rs, imm):
    return 0x1000 | ((imm & 0x1F) << 6) | ((rs & 7) << 3) | (rd & 7)


def alu(operation, rd, rs):
    return 0x4000 | ((operation & 0xF) << 6) | ((rs & 7) << 3) | (rd & 7)


def muls(rd, rs):
    return 0x4340 | ((rs & 7) << 3) | (rd & 7)


def bx(rm):
    return 0x4700 | ((rm & 0xF) << 3)


def ldr(rd, rb, imm5=0):
    return 0x6800 | ((imm5 & 0x1F) << 6) | ((rb & 7) << 3) | (rd & 7)


def strh(rd, rb, imm5=0):
    return 0x8000 | ((imm5 & 0x1F) << 6) | ((rb & 7) << 3) | (rd & 7)


def ldrh(rd, rb, imm5=0):
    return 0x8800 | ((imm5 & 0x1F) << 6) | ((rb & 7) << 3) | (rd & 7)


def strb(rd, rb, imm5=0):
    return 0x7000 | ((imm5 & 0x1F) << 6) | ((rb & 7) << 3) | (rd & 7)


def stmia(rb, registers):
    return 0xC000 | ((rb & 7) << 8) | (registers & 0xFF)


def ldmia(rb, registers):
    return 0xC800 | ((rb & 7) << 8) | (registers & 0xFF)


def push(registers):
    return 0xB400 | (registers & 0xFF)


def pop(registers):
    return 0xBC00 | (registers & 0xFF)


def b(offset):
    return 0xE000 | ((offset // 2) & 0x7FF)


def bcond(condition, offset):
    return 0xD000 | ((condition & 0xF) << 8) | ((offset // 2) & 0xFF)


def bl(site, target):
    delta = target - (site + 4)
    return (0xF000 | ((delta >> 12) & 0x7FF), 0xF800 | ((delta >> 1) & 0x7FF))


def whole(code):
    return set(range(BASE, BASE + len(code)))


def run(code, registers=None, memory=None, budget=harness.BUDGET):
    return harness.run(code, BASE, whole(code), registers, memory, budget)


def test_a_crafted_snippet_records_the_stores_the_registers_and_the_flags():
    code = program(movs(0, 5), adds(0, 3), strh(0, 1), ldrh(2, 1), cmp(2, 8),
                   bcond(0, 2), movs(3, 1), movs(3, 9), bx(LR))
    result = run(code, {1: 0x02000100}, {0x02000100: bytes(4)})
    assert result.writes == [(0x02000100, 2, 8)]
    assert result.registers[0] == 8
    assert result.registers[2] == 8
    assert result.registers[3] == 0
    assert result.calls == []


def test_a_conditional_branch_that_is_taken_skips_the_next_instruction():
    code = program(movs(0, 8), cmp(0, 8), bcond(0, 0), movs(3, 1), movs(3, 9), bx(LR))
    assert run(code).registers[3] == 9


def test_a_shift_a_subtraction_a_negation_and_a_product_land_in_the_registers():
    code = program(movs(0, 6), lsls(0, 0, 2), subs(0, 27), asrs(1, 0, 1), alu(9, 2, 0),
                   movs(3, 2), muls(3, 0), bx(LR))
    result = run(code)
    assert result.registers[0] == 0xFFFFFFFD
    assert result.registers[1] == 0xFFFFFFFE
    assert result.registers[2] == 3
    assert result.registers[3] == 0xFFFFFFFA


def test_a_loop_past_the_step_budget_is_refused():
    code = program(movs(0, 0), b(-4))
    with pytest.raises(ValueError, match="step budget"):
        run(code, budget=8)


def test_a_branch_outside_the_body_is_refused():
    code = program(b(0x20), bx(LR))
    with pytest.raises(ValueError, match="left the body"):
        harness.run(code, BASE, set(range(BASE, BASE + 4)))


def test_a_call_is_recorded_and_stubbed_so_the_next_instruction_runs():
    high, low = bl(0, BASE + 0x100)
    code = program(high, low, movs(0, 1), bx(LR))
    result = run(code)
    assert result.calls == [(BASE, BASE + 0x100)]
    assert result.registers[0] == 1
    assert result.steps == 3


def test_a_read_outside_the_mapped_footprints_is_refused():
    code = program(ldr(0, 1), bx(LR))
    with pytest.raises(ValueError, match="outside"):
        run(code, {1: 0x07000000})


def test_push_and_pop_keep_the_stack_and_transfer_a_halfword():
    code = program(push(0x10), strh(0, 1), ldrh(2, 1), pop(0x10), bx(LR))
    result = run(code, {0: 0xBEEF, 1: 0x02000200}, {0x02000200: bytes(4)})
    assert result.registers[2] == 0xBEEF
    assert result.registers[13] == harness.STACK
    assert result.writes == [(harness.STACK - 4, 4, 0), (0x02000200, 2, 0xBEEF)]


def test_a_block_copy_moves_both_words_and_advances_both_base_registers():
    code = program(ldmia(1, 0x0C), stmia(0, 0x0C), bx(LR))
    memory = {0x02000300: bytes(8), 0x02000400: struct.pack("<II", 0x11111111, 0x22222222)}
    result = run(code, {0: 0x02000300, 1: 0x02000400}, memory)
    assert result.writes == [(0x02000300, 4, 0x11111111), (0x02000304, 4, 0x22222222)]
    assert result.registers[0] == 0x02000308
    assert result.registers[1] == 0x02000408


def test_a_byte_store_records_its_width():
    code = program(movs(0, 0x41), strb(0, 1, 2), bx(LR))
    result = run(code, {1: 0x02000500}, {0x02000500: bytes(8)})
    assert result.writes == [(0x02000502, 1, 0x41)]


def test_the_body_of_a_retail_start_is_reachable_code_inside_its_own_row():
    image = testkit.rom_bytes(os.path.join(harness.ROOT, "baserom.gba"),
                              digest=harness.ROM_SHA256, size=0x800000)
    start = 0x0801191A
    allowed = harness.body(image, start)
    assert start in allowed
    assert 0x0801192A in allowed
    row = next(row for row in harness.code_rows()
               if BASE + row[0] <= start < BASE + row[0] + row[1])
    assert all(BASE + row[0] <= address < BASE + row[0] + row[1] for address in allowed)


def test_a_flagged_start_is_refused_and_names_the_flag_it_carries():
    with pytest.raises(ValueError, match="0x080335B6 is a flagged start \\(data\\+clobber\\)"):
        harness.refuse(0x080335B6)


def test_a_start_the_allow_list_does_not_carry_is_not_refused():
    assert harness.refuse(0x0801191A) is None


def test_the_refusal_comes_before_the_body_is_walked():
    image = testkit.rom_bytes(os.path.join(harness.ROOT, "baserom.gba"),
                              digest=harness.ROM_SHA256, size=0x800000)
    with pytest.raises(ValueError, match="entered at data"):
        harness.body(image, 0x0801906E)
