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
ENTRY = 0x02000200
SLOT = 0x02000400
POINTER = struct.pack("<I", SLOT)
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

    0x08050D30: ({0: OBJECT}, {OBJECT + 4: struct.pack("<I", SLOT), SLOT: struct.pack("<I", 0x02000600)},
         [
             (OBJECT + 0x0, 4, 0x8049ACC),
         ], [0x08046AA4]),

    0x0800A9D0: ({0: OBJECT}, {OBJECT + 0x30: struct.pack("<I", 1), OBJECT + 0x34: struct.pack("<I", ENTRY), ENTRY: POINTER},
         [
             (OBJECT + 0x30, 4, 0x0),
         ], [0x08046AA2]),

    0x0801157E: ({0: OBJECT}, {OBJECT + 0x208: struct.pack("<I", 1), OBJECT + 0x20C: struct.pack("<I", ENTRY), ENTRY: POINTER},
         [
             (OBJECT + 0x208, 4, 0x0),
         ], [0x0803DA62, 0x08046AA2]),

    0x08012628: ({0: OBJECT}, {OBJECT: struct.pack("<I", 1), OBJECT + 4: struct.pack("<I", ENTRY), ENTRY: POINTER},
         [
             (OBJECT + 0x0, 4, 0x0),
             (OBJECT + 0xD0, 4, 0x1),
             (OBJECT + 0xC4, 4, 0x1),
             (OBJECT + 0xCC, 4, 0x0),
             (OBJECT + 0xC8, 4, 0x1),
         ], [0x08046AA4]),

    0x08011E94: ({0: OBJECT}, {OBJECT + 0x40C: struct.pack("<I", 1), OBJECT + 0x410: struct.pack("<I", ENTRY), ENTRY: POINTER},
         [
             (OBJECT + 0x4, 4, 0x1),
             (OBJECT + 0x8, 4, 0x2000200),
             (OBJECT + 0x40C, 4, 0x0),
         ], [0x08046AA2]),

    0x0801268A: ({0: OBJECT, 1: ENTRY}, {OBJECT: struct.pack("<I", 2), OBJECT + 4: struct.pack("<I", ENTRY), OBJECT + 8: struct.pack("<I", SLOT), ENTRY: POINTER},
         [
             (OBJECT + 0x0, 4, 0x1),
         ], [0x08049138, 0x08046AA4]),

    0x08013A90: ({0: OBJECT, 1: 0x5A}, {},
         [
             (OBJECT + 0xD, 1, 0x5A),
             (OBJECT + 0x2E, 1, 0x0),
             (OBJECT + 0x2F, 1, 0x0),
             (OBJECT + 0xC, 1, 0x1),
         ], []),

    0x08011200: ({0: OBJECT, 1: 0}, {},
         [
             (OBJECT + 0x69C, 1, 0x0),
             (OBJECT + 0x69D, 1, 0x0),
         ], []),

    0x0801137C: ({0: OBJECT, 1: 1}, {},
         [
             (OBJECT + 0x69E, 1, 0xFF),
             (OBJECT + 0x6A5, 1, 0xFF),
             (OBJECT + 0x6A4, 1, 0x0),
             (OBJECT + 0x69B, 1, 0x1),
             (OBJECT + 0x1, 1, 0x1),
         ], []),

    0x0804E490: ({0: OBJECT, 1: 0x02000600, 2: 0x20}, {0x02000600: bytes(range(0x20))},
         [
             (OBJECT + 0x0, 1, 0x1),
             (OBJECT + 0x2, 2, 0x1C4C),
         ], [0x0801124C, 0x08049138]),

    0x08011568: ({0: OBJECT}, {OBJECT + 0xC: struct.pack("<H", 3)},
         [
             (OBJECT + 0xC, 2, 0xFFFF),
         ], [0x0801142A]),

    0x08011818: ({0: OBJECT}, {OBJECT + 0xE: struct.pack("<H", 7)},
         [
             (OBJECT + 0xC, 2, 0x1C4C),
         ], [0x0801124C]),

    0x0800432C: ({0: OBJECT}, {},
         [
             (OBJECT + 0x4D0, 4, 0x0),
         ], []),

    0x08006880: ({0: OBJECT}, {},
         [
             (OBJECT + 0x4, 4, 0x0),
             (OBJECT + 0x0, 4, 0x804BF3C),
             (OBJECT + 0x8, 4, 0x0),
             (OBJECT + 0xC, 4, 0x0),
             (OBJECT + 0x10, 4, 0x0),
             (OBJECT + 0x14, 4, 0x0),
             (OBJECT + 0x1C, 4, 0x0),
             (OBJECT + 0x18, 4, 0xFFFFFFFE),
         ], []),

    0x080091B8: ({0: OBJECT}, {},
         [
             (OBJECT + 0x0, 4, 0x0),
             (OBJECT + 0x4, 4, 0x0),
             (OBJECT + 0x8, 4, 0x0),
             (OBJECT + 0xC, 4, 0x0),
             (OBJECT + 0x10, 4, 0x0),
         ], [0x08009A2A, 0x08011E0E, 0x080210F2]),

    0x0803362A: ({0: OBJECT}, {},
         [
             (OBJECT + 0x20, 4, 0x806E050),
             (OBJECT + 0x18, 4, 0x78),
             (OBJECT + 0x1C, 4, 0x10),
             (OBJECT + 0x15, 1, 0x8),
         ], [0x08046E40, 0x08049150]),

    0x08033664: ({0: OBJECT}, {},
         [
             (OBJECT + 0x20, 4, 0x806EE6C),
             (OBJECT + 0x18, 4, 0x78),
             (OBJECT + 0x1C, 4, 0x18),
             (OBJECT + 0x15, 1, 0x10),
         ], [0x08046E40, 0x08049150]),

    0x0803E8BC: ({0: OBJECT}, {},
         [
             (OBJECT + 0x51, 1, 0x0),
             (OBJECT + 0x30, 4, 0x0),
             (OBJECT + 0x10, 1, 0x2),
         ], []),

    0x08010D7C: ({0: OBJECT}, {},
         [
             (OBJECT + 0x1CC, 4, 0x0),
         ], [0x0800ECDA, 0x0800ED18]),

    0x08011874: ({0: OBJECT, 1: 1, 2: 2, 3: 3}, {},
         [
             (OBJECT + 0xC, 4, 0x1),
             (OBJECT + 0x10, 4, 0x2),
             (OBJECT + 0x14, 4, 0x3),
             (OBJECT + 0x0, 4, 0x804ABA0),
         ], [0x0804E490]),
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

def test_object_install_handler_table1_stores_the_handler_table_word_at_0_and_reaches_the_handler_the_object_at_4_names():
    assert result(0x08050D30) == ROWS[0x08050D30][2:]

def test_list_release_all1_walks_the_count_at_0x30_and_clears_it():
    assert result(0x0800A9D0) == ROWS[0x0800A9D0][2:]

def test_list_release_all2_walks_the_count_at_0x208_and_clears_it():
    assert result(0x0801157E) == ROWS[0x0801157E][2:]

def test_list_release_all3_clears_the_count_and_arms_the_block_at_0xc0():
    assert result(0x08012628) == ROWS[0x08012628][2:]

def test_list_pop_all1_moves_the_entries_into_the_array_at_4_and_clears_the_count():
    assert result(0x08011E94) == ROWS[0x08011E94][2:]

def test_list_remove1_removes_the_entry_the_argument_names_and_shifts_the_rest():
    assert result(0x0801268A) == ROWS[0x0801268A][2:]

def test_list_append_byte1_writes_the_byte_after_the_count_and_clears_the_tail_slots():
    assert result(0x08013A90) == ROWS[0x08013A90][2:]

def test_table_unlink1_unlinks_the_record_from_its_two_neighbours():
    assert result(0x08011200) == ROWS[0x08011200][2:]

def test_table_init_link1_writes_the_two_link_bytes_and_advances_the_owner():
    assert result(0x0801137C) == ROWS[0x0801137C][2:]

def test_gfx_begin_tile_load1_increments_the_byte_and_stores_the_tile_index():
    assert result(0x0804E490) == ROWS[0x0804E490][2:]

def test_handle_release1_unregisters_the_handle_and_stores_0xffff():
    assert result(0x08011568) == ROWS[0x08011568][2:]

def test_handle_acquire1_looks_the_id_up_and_stores_the_handle():
    assert result(0x08011818) == ROWS[0x08011818][2:]

def test_object_subtract_delta1_subtracts_the_global_word_from_the_counter():
    assert result(0x0800432C) == ROWS[0x0800432C][2:]

def test_object_construct2_stores_the_table_word_and_the_stack_arguments():
    assert result(0x08006880) == ROWS[0x08006880][2:]

def test_state_copy_block1_copies_the_five_default_words_and_calls_three_resetters():
    assert result(0x080091B8) == ROWS[0x080091B8][2:]

def test_gfx_init_block1_stores_the_budget_the_count_and_the_copied_block():
    assert result(0x0803362A) == ROWS[0x0803362A][2:]

def test_gfx_init_block2_stores_the_second_budget_the_count_and_the_copied_block():
    assert result(0x08033664) == ROWS[0x08033664][2:]

def test_math_scale_by_table1_scales_the_field_by_the_two_tables_and_sets_the_bit():
    assert result(0x0803E8BC) == ROWS[0x0803E8BC][2:]

def test_table_clear_slot1_clears_the_slot_word_and_calls_the_two_record_helpers():
    assert result(0x08010D7C) == ROWS[0x08010D7C][2:]

def test_object_construct3_stores_the_table_word_and_the_three_arguments():
    assert result(0x08011874) == ROWS[0x08011874][2:]
