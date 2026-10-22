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


OBJECT_BOUNDS = 0x0800FDFA
LIST_CALL_METHOD = 0x08011C70
OUTPUT = 0x02000300
VTABLE = 0x02000400


def test_object_write_bounds1_stores_the_position_and_the_sum_of_position_and_size():
    fields = bytearray(0x1B0)
    struct.pack_into("<II", fields, 0x1A0, 0x00012300, 0x000456FF)
    struct.pack_into("<BB", fields, 0x19C, 2, 3)
    result = run(OBJECT_BOUNDS, {0: OUTPUT, 1: OBJECT},
                 {OBJECT: bytes(fields), OUTPUT: bytes(0x20)})
    assert [entry for entry in result.writes if 0x02000000 <= entry[0] <= 0x0203FFFF] == [
        (OUTPUT, 4, 0x123), (OUTPUT + 4, 4, 0x456),
        (OUTPUT + 8, 4, 0x125), (OUTPUT + 12, 4, 0x459)]
    assert result.calls == []


def test_list_call_method1_calls_through_the_table_word_the_single_record_names():
    table = bytearray(0x40)
    struct.pack_into("<I", table, 0x24, 0x1000)
    memory = {OBJECT: struct.pack("<III", 0, 1, TABLE), TABLE: struct.pack("<I", VTABLE),
              VTABLE: bytes(table)}
    result = run(LIST_CALL_METHOD, {0: OBJECT, 1: 0x11, 2: 0x22}, memory)
    assert result.calls == [(0x08011C94, 0x08046AA6)]