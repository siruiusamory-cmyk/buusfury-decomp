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


def classify(data, entries, rows, modes=None, calls=(), table=(), vectors=(), spans=()):
    return function_bounds.classify(bytes(data), entries, modes or {},
                                    [(BASE + start, BASE + stop) for start, stop in rows],
                                    set(BASE + value for value in calls),
                                    set(BASE + value for value in table),
                                    set(BASE + value for value in vectors),
                                    spans=set(BASE + value for value in spans))


def kind_of(found, address):
    return found["starts"].get(address)


def test_a_push_that_saves_lr_is_the_prologue_limb():
    data = image()
    put_half(data, BASE + 0x10, 0xB510)
    put_half(data, BASE + 0x12, 0xBD10)
    found = classify(data, [BASE + 0x10], [(0x10, 0x14)], spans=[0x10])
    assert kind_of(found, BASE + 0x10) == ["prologue"]


def test_a_push_that_does_not_save_lr_is_no_prologue_limb():
    data = image()
    put_half(data, BASE + 0x20, 0xB410)
    put_half(data, BASE + 0x22, 0xBD10)
    found = classify(data, [BASE + 0x20], [(0x20, 0x24)], spans=[0x20])
    assert kind_of(found, BASE + 0x20) == []
    assert BASE + 0x20 in found["unreferenced"]


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
    assert kind_of(found, BASE + 0x60) == ["call"]


def test_a_jump_table_word_is_the_table_limb():
    data = image()
    put_half(data, BASE + 0xA0, 0x4770)
    found = classify(data, [BASE + 0xA0], [(0xA0, 0xA4)], table=[0xA0])
    assert kind_of(found, BASE + 0xA0) == ["table"]


def test_the_reset_entry_is_the_vector_limb():
    data = image()
    put_half(data, BASE, 0x2001)
    put_half(data, BASE + 2, 0xBD00)
    found = classify(data, [BASE], [(0, 4)], vectors=[0])
    assert kind_of(found, BASE) == ["vector"]


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
    found = classify(data, [BASE + 0x80, BASE + 0x84], [(0x80, 0x84), (0x84, 0x88)],
                     spans=[0x80, 0x84])
    assert kind_of(found, BASE + 0x84) == []
    assert BASE + 0x84 in found["unreferenced"]


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
    found = classify(data, [BASE + 0xE0, BASE + 0xF0], [(0xE0, 0xE2), (0xF0, 0xF2)],
                     spans=[0xE0, 0xF0])
    assert found["ends"][BASE + 0xE0] == BASE + 0xE0
    assert BASE + 0xF0 in found["starts"]


def test_an_entry_outside_every_code_run_is_classified_by_nothing():
    data = image()
    put_half(data, BASE + 0x100, 0xB510)
    put_half(data, BASE + 0x102, 0xBD10)
    found = classify(data, [BASE + 0x100], [])
    assert BASE + 0x100 not in found["starts"]
    assert BASE + 0x100 not in found["blocks"]


def test_a_transcribed_span_start_that_no_rule_reaches_is_unreferenced():
    data = image()
    put_half(data, BASE + 0x10, 0x2001)
    put_half(data, BASE + 0x12, 0xBD00)
    found = classify(data, [], [(0x10, 0x14)], spans=[0x10])
    assert kind_of(found, BASE + 0x10) == []
    assert found["unreferenced"] == {BASE + 0x10}
    assert function_bounds.rows_text(found).splitlines()[1] == "0x08000010,unreferenced,,"


def test_a_transcribed_span_start_with_a_prologue_carries_no_block_limb():
    data = image()
    put_half(data, BASE + 0x10, 0xB510)
    put_half(data, BASE + 0x12, 0xBD10)
    found = classify(data, [], [(0x10, 0x14)], spans=[0x10])
    assert kind_of(found, BASE + 0x10) == ["prologue"]
    assert BASE + 0x10 not in found["unreferenced"]


def test_a_transcribed_span_start_parents_the_blocks_in_its_row():
    data = image()
    put_half(data, BASE + 0x20, 0x2001)
    put_half(data, BASE + 0x22, 0x2002)
    put_half(data, BASE + 0x24, 0x2003)
    put_half(data, BASE + 0x26, 0xBD00)
    found = classify(data, [BASE + 0x24], [(0x20, 0x28)], spans=[0x20])
    assert found["unreferenced"] == {BASE + 0x20}
    assert found["blocks"][BASE + 0x24] == BASE + 0x20


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


def test_a_start_in_the_gap_before_the_next_prologue_is_flagged_as_data():
    data = image()
    put_half(data, BASE + 0x10, 0xBD10)
    put_half(data, BASE + 0x14, 0x0804)
    put_half(data, BASE + 0x16, 0xB510)
    put_half(data, BASE + 0x18, 0xBD10)
    found = classify(data, [BASE + 0x14], [(0x14, 0x1A)], spans=[0x14])
    rows = function_bounds.flag_rows(bytes(data), found)
    assert rows == [(BASE + 0x14, "unreferenced", "", "data", BASE + 0x16, "prefix")]
    assert function_bounds.flags_text(rows).splitlines()[1] == \
        "0x08000014,unreferenced,,data,0x08000016,prefix"


def test_a_start_whose_leading_halfword_the_cpu_cannot_execute_is_flagged():
    data = image()
    put_half(data, BASE + 0x20, 0xBE00)
    put_half(data, BASE + 0x22, 0xBD10)
    found = classify(data, [BASE + 0x20], [(0x20, 0x24)], spans=[0x20])
    rows = function_bounds.flag_rows(bytes(data), found)
    assert rows[0][3] == "undecodable"
    assert rows[0][4] is None


def test_a_prologue_at_the_start_is_not_a_flag():
    data = image()
    put_half(data, BASE + 0x10, 0xBD10)
    put_half(data, BASE + 0x14, 0xB510)
    put_half(data, BASE + 0x16, 0xBD10)
    found = classify(data, [BASE + 0x14], [(0x14, 0x18)], spans=[0x14])
    assert function_bounds.flag_rows(bytes(data), found) == []


def test_a_start_the_runtime_proves_is_not_flagged():
    data = image()
    put_half(data, BASE + 0x10, 0xBD10)
    put_half(data, BASE + 0x14, 0x0804)
    put_half(data, BASE + 0x16, 0xB510)
    found = classify(data, [BASE + 0x14], [(0x14, 0x1A)], spans=[0x14])
    assert function_bounds.flag_rows(bytes(data), found) == [
        (BASE + 0x14, "unreferenced", "", "data", BASE + 0x16, "prefix")]
    assert function_bounds.flag_rows(bytes(data), found, {BASE + 0x14}) == []


def test_a_flagged_start_the_allow_list_does_not_carry_is_named():
    carried = "address,kind,limb,flags,entry,reason\n0x08000010,unreferenced,,data,0x08000012,prefix\n"
    derived = carried + "0x08000020,unreferenced,,data,0x08000022,prefix\n"
    assert function_bounds.uncarried(carried, derived) == "0x08000020"
    assert function_bounds.uncarried(derived, derived) is None


def test_a_stub_record_starting_a_row_is_its_entry_and_is_not_flagged():
    data = image()
    for at, value in enumerate((0x4A03, 0xB508, 0x6002, 0x2900,
                                0xD001, 0xF000, 0xF800, 0xBD08)):
        put_half(data, BASE + 0x40 + 2 * at, value)
    put_word(data, BASE + 0x50, BASE + 0x60)
    put_half(data, BASE + 0x3E, 0xE000)
    assert function_bounds.stub_entry(bytes(data), BASE + 0x40, "thumb") is True
    assert function_bounds.stub_entry(bytes(data), BASE + 0x42, "thumb") is False
    found = classify(data, [BASE + 0x40], [(0x3E, 0x54)], spans=[0x40])
    assert function_bounds.flag_rows(bytes(data), found, set()) == []


def test_a_start_in_an_arm_row_is_tested_by_the_arm_bytes():
    data = image()
    put_word(data, BASE + 0x60, 0xE92D4010)
    found = function_bounds.classify(bytes(data), [BASE + 0x60], {},
                                     [(BASE + 0x60, BASE + 0x64, "arm")],
                                     set(), set(), set(), spans={BASE + 0x60})
    assert found["row_modes"][BASE + 0x60] == "arm"
    assert function_bounds.flag_rows(bytes(data), found, set()) == []


def test_a_row_start_is_classed_by_the_bytes_that_open_and_precede_it():
    data = image()
    put_half(data, BASE + 0x10, 0x4A00)
    put_half(data, BASE + 0x12, 0xB510)
    put_half(data, BASE + 0x14, 0xBD10)
    assert function_bounds.reason_of(bytes(data), BASE + 0x10, "thumb",
                                     (BASE + 0x10, BASE + 0x18)) == "entry"
    put_word(data, BASE + 0x20, 0x03001234)
    assert function_bounds.reason_of(bytes(data), BASE + 0x20, "thumb",
                                     (BASE + 0x20, BASE + 0x22)) == "data"
    put_half(data, BASE + 0x2E, 0x1C08)
    put_half(data, BASE + 0x30, 0x0804)
    put_half(data, BASE + 0x32, 0xDE00)
    assert function_bounds.reason_of(bytes(data), BASE + 0x30, "thumb",
                                     (BASE + 0x30, BASE + 0x34)) == "split"
    put_half(data, BASE + 0x2E, 0xBD10)
    assert function_bounds.reason_of(bytes(data), BASE + 0x30, "thumb",
                                     (BASE + 0x30, BASE + 0x34)) == "data"


def test_the_tracked_entry_allow_list_is_what_the_image_gives():
    root = os.path.dirname(os.path.dirname(HERE))
    rom = os.path.join(root, "baserom.gba")
    if not os.path.exists(rom):
        pytest.skip("the retail image is absent, so the flagged starts cannot be re-derived")
    found = function_bounds.census(open(rom, "rb").read())
    derived = function_bounds.flags_text(function_bounds.flag_rows(open(rom, "rb").read(), found))
    with open(function_bounds.ALLOW, encoding="utf-8") as handle:
        assert handle.read() == derived
    carried = {line.split(",")[0]: line.split(",") for line in derived.splitlines()[1:]}
    starts = set(found["starts"])
    for address, entry in ((0x080335B6, 0x080335BC), (0x0801906E, 0x08019074),
                           (0x08050566, 0x08050568)):
        assert "0x%08x" % address not in carried
        assert entry in starts
        assert address not in starts


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
    test_a_stub_record_starting_a_row_is_its_entry_and_is_not_flagged()
    print("PASS test_function_bounds")
