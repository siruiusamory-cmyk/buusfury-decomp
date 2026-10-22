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
OUTPUT = 0x02000300
TABLE = 0x02000200
CACHE = {}

ROWS = {
    0x0803E5AC: ({"0": OBJECT},
                 {OBJECT + 0x48: bytes([5, 0, 0, 2]), OBJECT + 0x10: b"\xf0"},
                 [(OBJECT + 0x48, 1, 3), (OBJECT + 0x12, 1, 3), (OBJECT + 0x10, 1, 0xF0)],
                 []),
    0x0803E5DA: ({"0": OBJECT},
                 {OBJECT + 0x48: bytes([0x3F, 0, 0, 2])},
                 [(OBJECT + 0x48, 1, 0x41), (OBJECT + 0x48, 1, 0x40),
                  (OBJECT + 0x4A, 1, 0), (OBJECT + 0x12, 1, 0x40),
                  (OBJECT + 0x10, 1, 0x10)], []),
    0x08004448: ({"0": OBJECT, "1": 0x12345678},
                 {OBJECT + 0xE4: struct.pack("<I", 2)},
                 [(OBJECT + 0xE4, 4, 3), (OBJECT + 0xF0, 4, 0x02345678)], []),
    0x08014124: ({"0": OBJECT}, {},
                 [(OBJECT + 0x04, 4, 0), (OBJECT + 0x00, 4, 0x0804A254),
                  (OBJECT + 0x08, 4, 0), (OBJECT + 0x0C, 4, 0),
                  (OBJECT + 0x14, 4, 0), (OBJECT + 0x18, 1, 0),
                  (OBJECT + 0x10, 4, 0), (OBJECT + 0x1C, 4, 0)], []),
    0x08015FFC: ({"0": OBJECT, "1": 0x11, "2": 0x22},
                 {OBJECT + 0x4C: struct.pack("<I", 1)},
                 [(OBJECT + 0x4C, 4, 2), (OBJECT + 0x5C, 4, 0x11),
                  (OBJECT + 0x60, 4, 0x22), (OBJECT + 0x64, 4, 0x0806E050),
                  (OBJECT + 0x110, 4, 0)], [0x0803FFE8]),
    0x0804F944: ({"0": OUTPUT, "1": OBJECT},
                 {OBJECT + 0x1A0: struct.pack("<II", 0x00012300, 0x000456FF)},
                 [(OUTPUT, 4, 0x123), (OUTPUT + 4, 4, 0x456)], []),
    0x08009220: ({"0": OBJECT}, {},
                 [(OBJECT, 4, 0), (OBJECT + 4, 4, 1), (OBJECT + 8, 4, 2),
                  (OBJECT + 0xC, 4, 3)], [0x08007A40] * 4),
    0x0800FA16: ({"0": OBJECT, "1": 2}, {},
                 [(OBJECT + 0x224, 4, 0x087112AC)], []),
}


def image():
    if "rom" not in CACHE:
        CACHE["rom"] = testkit.rom_bytes(os.path.join(harness.ROOT, "baserom.gba"),
                                         digest=harness.ROM_SHA256, size=0x800000)
    return CACHE["rom"]


def result(address):
    registers, memory, _writes, _calls = ROWS[address]
    retail = image()
    if ("body", address) not in CACHE:
        CACHE[("body", address)] = harness.body(retail, address)
    found = harness.run(retail, address, CACHE[("body", address)],
                        {int(key): value for key, value in registers.items()}, memory)
    writes = [item for item in found.writes if 0x02000000 <= item[0] <= 0x0203FFFF]
    return writes, [target for _site, target in found.calls]


def test_object_advance_timer1_subtracts_the_delta_and_sets_the_timer_flag():
    assert result(0x0803E5AC) == ROWS[0x0803E5AC][2:]


def test_object_advance_timer2_adds_the_delta_and_clamps_it_at_0x40():
    assert result(0x0803E5DA) == ROWS[0x0803E5DA][2:]


def test_object_append_entry1_counts_the_entries_and_masks_the_value_to_28_bits():
    assert result(0x08004448) == ROWS[0x08004448][2:]


def test_object_construct1_stores_the_table_word_and_the_arguments_at_fixed_offsets():
    assert result(0x08014124) == ROWS[0x08014124][2:]


def test_object_append_record1_appends_a_12_byte_record_and_clears_the_flag():
    assert result(0x08015FFC) == ROWS[0x08015FFC][2:]


def test_object_read_position1_shifts_the_two_fixed_point_words_right_by_eight():
    assert result(0x0804F944) == ROWS[0x0804F944][2:]


def test_object_rebuild_slots1_replaces_each_of_the_four_slots_with_a_new_handle():
    assert result(0x08009220) == ROWS[0x08009220][2:]


def test_object_write_table_pointer1_stores_the_table_entry_the_index_names():
    assert result(0x0800FA16) == ROWS[0x0800FA16][2:]
