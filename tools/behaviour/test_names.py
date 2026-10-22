from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import testkit

import harness

OBJECT = 0x02000000
TABLE = 0x02000100
SECOND = 0x02000200
LIST_APPEND = 0x0801191A
RECORD_SELECT = 0x0800ECDA
RECORD_INIT = 0x0800DE60
STRUCT_ZERO = 0x080402D6


def image():
    return testkit.rom_bytes(os.path.join(harness.ROOT, "baserom.gba"),
                             digest=harness.ROM_SHA256, size=0x800000)


def run(start, registers, memory):
    retail = image()
    return harness.run(retail, start, harness.body(retail, start), registers, memory)


def test_list_append_stores_the_value_after_the_last_one_and_increments_the_count():
    memory = {OBJECT: struct.pack("<III", 0, 1, 0xAAAAAAAA)}
    result = run(LIST_APPEND, {0: OBJECT, 1: 0x12345678}, memory)
    assert result.writes == [(OBJECT + 4, 4, 2), (OBJECT + 12, 4, 0x12345678)]
    assert result.calls == []


def test_list_append_leaves_the_list_length_untouched():
    memory = {OBJECT: struct.pack("<II", 0x00000010, 0)}
    result = run(LIST_APPEND, {0: OBJECT, 1: 0xDEADBEEF}, memory)
    assert result.writes == [(OBJECT + 4, 4, 1), (OBJECT + 8, 4, 0xDEADBEEF)]


def test_record_select_indexed_copies_the_indexed_dword_into_offset_50():
    memory = {OBJECT: bytes(0x58) + struct.pack("<I", TABLE) + bytes(4),
              TABLE: bytes(0x54) + struct.pack("<II", 0x11111111, 0x22222222)}
    result = run(RECORD_SELECT, {0: OBJECT, 1: 1}, memory)
    assert result.writes == [(OBJECT + 0x50, 4, 0x22222222)]


def test_record_select_indexed_also_copies_the_second_table_when_that_pointer_is_set():
    table = bytearray(0x5C)
    struct.pack_into("<I", table, 0x50, SECOND)
    struct.pack_into("<II", table, 0x54, 0x11111111, 0x22222222)
    memory = {OBJECT: bytes(0x58) + struct.pack("<I", TABLE) + bytes(4),
              TABLE: bytes(table),
              SECOND: struct.pack("<II", 0xAAAAAAAA, 0xBBBBBBBB)}
    result = run(RECORD_SELECT, {0: OBJECT, 1: 1}, memory)
    assert result.writes == [(OBJECT + 0x50, 4, 0x22222222),
                             (OBJECT + 0x4C, 4, 0xBBBBBBBB)]


def test_record_init_fields_writes_a_zero_halfword_a_0x38_byte_and_a_zero_byte():
    memory = {OBJECT: bytes(0x20)}
    result = run(RECORD_INIT, {0: 0, 1: OBJECT}, memory)
    assert result.writes == [(OBJECT + 0x12, 2, 0), (OBJECT + 8, 1, 0x38),
                             (OBJECT + 0x11, 1, 0)]
    assert result.registers[0] == 0x38


def test_struct_zero_fields_writes_four_zero_stores_over_the_first_eight_bytes():
    memory = {OBJECT: bytes(0x20)}
    result = run(STRUCT_ZERO, {0: OBJECT}, memory)
    assert result.writes == [(OBJECT, 1, 0), (OBJECT + 2, 2, 0),
                             (OBJECT + 4, 2, 0), (OBJECT + 6, 2, 0)]
    assert result.registers[0] == OBJECT
