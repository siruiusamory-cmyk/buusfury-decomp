from __future__ import annotations

import os
import struct
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import function_bounds

BASE = 0x08000000


def image(size=0x200):
    return bytearray(size)


def put_half(data, address, value):
    struct.pack_into("<H", data, address - BASE, value & 0xFFFF)


def put_word(data, address, value):
    struct.pack_into("<I", data, address - BASE, value & 0xFFFFFFFF)


def classify(data, entries, rows, modes=None, calls=(), table=(), vectors=()):
    return function_bounds.classify(bytes(data), entries, modes or {},
                                    [(BASE + start, BASE + stop) for start, stop in rows],
                                    set(BASE + value for value in calls),
                                    set(BASE + value for value in table),
                                    set(BASE + value for value in vectors))


def kind_of(found, address):
    return found["starts"].get(address)


def test_a_push_that_saves_lr_is_the_prologue_limb():
    data = image()
    put_half(data, BASE + 0x10, 0xB510)
    put_half(data, BASE + 0x12, 0xBD10)
    found = classify(data, [BASE + 0x10], [(0x10, 0x14)])
    assert kind_of(found, BASE + 0x10) == ["prologue", "block"]


def test_a_push_that_does_not_save_lr_is_no_prologue_limb():
    data = image()
    put_half(data, BASE + 0x20, 0xB410)
    put_half(data, BASE + 0x22, 0xBD10)
    found = classify(data, [BASE + 0x20], [(0x20, 0x24)])
    assert kind_of(found, BASE + 0x20) == ["block"]


def test_an_arm_stmfd_that_saves_lr_is_the_prologue_limb():
    data = image()
    put_word(data, BASE + 0x40, 0xE92D4030)
    put_word(data, BASE + 0x44, 0xE12FFF1E)
    found = classify(data, [BASE + 0x40], [(0x40, 0x48)], {BASE + 0x40: "arm"})
    assert "prologue" in kind_of(found, BASE + 0x40)


def test_a_bl_target_is_the_call_limb():
    data = image()
    put_half(data, BASE + 0x56, 0xF000)
    put_half(data, BASE + 0x58, 0xF806)
    put_half(data, BASE + 0x60, 0x2001)
    put_half(data, BASE + 0x62, 0xBD00)
    found = classify(data, [BASE + 0x60], [(0x60, 0x64)], calls=[0x60])
    assert kind_of(found, BASE + 0x60) == ["call", "block"]


def test_a_jump_table_word_is_the_table_limb():
    data = image()
    put_half(data, BASE + 0xA0, 0x4770)
    found = classify(data, [BASE + 0xA0], [(0xA0, 0xA4)], table=[0xA0])
    assert kind_of(found, BASE + 0xA0) == ["table", "block"]


def test_the_reset_entry_is_the_vector_limb():
    data = image()
    put_half(data, BASE, 0x2001)
    put_half(data, BASE + 2, 0xBD00)
    found = classify(data, [BASE], [(0, 4)], vectors=[0])
    assert kind_of(found, BASE) == ["vector", "block"]


def test_an_entry_with_no_limb_inside_a_proved_body_is_a_block_with_its_parent():
    data = image()
    put_half(data, BASE + 0x60, 0x2001)
    put_half(data, BASE + 0x62, 0xBD00)
    put_half(data, BASE + 0x64, 0x2003)
    put_half(data, BASE + 0x66, 0xBD00)
    found = classify(data, [BASE + 0x60, BASE + 0x64], [(0x60, 0x68)], calls=[0x60])
    assert found["blocks"][BASE + 0x64] == BASE + 0x60
    assert BASE + 0x64 not in found["starts"]


def test_an_entry_that_opens_a_proved_code_run_is_a_start():
    data = image()
    put_half(data, BASE + 0x80, 0x2001)
    put_half(data, BASE + 0x82, 0xBD00)
    put_half(data, BASE + 0x84, 0x2002)
    put_half(data, BASE + 0x86, 0xBD00)
    found = classify(data, [BASE + 0x80, BASE + 0x84], [(0x80, 0x84), (0x84, 0x88)])
    assert kind_of(found, BASE + 0x84) == ["block"]


def test_a_call_target_inside_another_body_is_reported_and_not_a_start():
    data = image()
    put_half(data, BASE + 0xC0, 0xB510)
    put_half(data, BASE + 0xC2, 0xE000)
    put_half(data, BASE + 0xC4, 0xBD10)
    put_half(data, BASE + 0xC6, 0x2003)
    put_half(data, BASE + 0xC8, 0xBD00)
    found = classify(data, [BASE + 0xC0, BASE + 0xC6], [(0xC0, 0xCC)], calls=[0xC6])
    assert found["contained"] == 1
    assert BASE + 0xC6 not in found["starts"]
    assert found["blocks"][BASE + 0xC6] == BASE + 0xC0


def test_a_body_stops_at_the_end_of_its_run():
    data = image()
    put_half(data, BASE + 0xE0, 0x2001)
    found = classify(data, [BASE + 0xE0, BASE + 0xF0], [(0xE0, 0xE2), (0xF0, 0xF2)])
    assert found["ends"][BASE + 0xE0] == BASE + 0xE0
    assert BASE + 0xF0 in found["starts"]


def test_an_entry_outside_every_code_run_is_classified_by_nothing():
    data = image()
    put_half(data, BASE + 0x100, 0xB510)
    put_half(data, BASE + 0x102, 0xBD10)
    found = classify(data, [BASE + 0x100], [])
    assert BASE + 0x100 not in found["starts"]
    assert BASE + 0x100 not in found["blocks"]


def test_the_sample_names_ten_blocks_with_their_parent():
    data = image()
    put_half(data, BASE + 0x120, 0x2001)
    put_half(data, BASE + 0x122, 0xBD00)
    for index in range(12):
        put_half(data, BASE + 0x124 + 2 * index, 0x2000 + index)
    found = classify(data, [BASE + 0x120] + [BASE + 0x124 + 2 * i for i in range(12)],
                     [(0x120, 0x13C)], calls=[0x120])
    lines = function_bounds.sample_text(bytes(data), found, 10)
    assert len(lines) == 11
    assert lines[0].startswith("address,parent,limb")
    assert all(line.split(",")[1] == "0x08000120" for line in lines[1:])


def test_a_candidate_outside_the_image_is_refused_as_a_wrong_address_space():
    data = image()
    put_half(data, BASE + 0x10, 0xB510)
    with pytest.raises(SystemExit):
        function_bounds.classify(bytes(data), [BASE + 0x10000058], {}, [(0x10, 0x14)],
                                 set(), set(), set())


def test_the_tracked_census_is_what_the_image_gives():
    root = os.path.dirname(os.path.dirname(HERE))
    rom = os.path.join(root, "baserom.gba")
    if not os.path.exists(rom):
        pytest.skip("the retail image is absent, so the census cannot be re-derived")
    found = function_bounds.census(open(rom, "rb").read())
    with open(function_bounds.BOUNDS, encoding="utf-8") as handle:
        assert handle.read() == function_bounds.rows_text(found)


if __name__ == "__main__":
    test_a_push_that_saves_lr_is_the_prologue_limb()
    test_a_push_that_does_not_save_lr_is_no_prologue_limb()
    test_an_arm_stmfd_that_saves_lr_is_the_prologue_limb()
    test_a_bl_target_is_the_call_limb()
    test_a_jump_table_word_is_the_table_limb()
    test_the_reset_entry_is_the_vector_limb()
    test_an_entry_with_no_limb_inside_a_proved_body_is_a_block_with_its_parent()
    test_an_entry_that_opens_a_proved_code_run_is_a_start()
    test_a_call_target_inside_another_body_is_reported_and_not_a_start()
    test_a_body_stops_at_the_end_of_its_run()
    test_an_entry_outside_every_code_run_is_classified_by_nothing()
    test_the_sample_names_ten_blocks_with_their_parent()
    print("PASS test_function_bounds")
