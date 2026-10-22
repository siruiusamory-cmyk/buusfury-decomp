from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import audit
import rank
import testkit


def test_a_call_line_names_its_target_and_a_slice_offset_does_not():
    found = rank.CALL.match("    BL       |sub_08000158|")
    assert found.group(2) == "sub_08000158"
    assert audit.ADDRESS_NAME.match(found.group(2))
    assert not audit.ADDRESS_NAME.match("inc_0x0158_0x143f2")
    assert rank.CALL.match("    BL       |inc_0x046118_0x049114| + 0x98e").group(2) == \
        "inc_0x046118_0x049114"
    assert not audit.ADDRESS_NAME.match("inc_0x046118_0x049114")


def test_a_ram_equ_row_separates_a_named_word_from_an_address_name():
    assert rank.EQU.match("|g_FreeListTail|      EQU     0x03003488")
    assert not audit.ADDRESS_NAME.match("g_FreeListTail")
    assert audit.ADDRESS_NAME.match("unk_03004A68")
    assert not audit.band(0x02000800, audit.IWRAM_START, audit.IWRAM_END)
    assert audit.band(0x03003488, audit.IWRAM_START, audit.IWRAM_END)


def main_output():
    collected = []

    class Sink:
        def write(self, text):
            collected.append(text)

        def flush(self):
            pass

    original = sys.stdout
    sys.stdout = Sink()
    try:
        assert rank.main([]) == 0
    finally:
        sys.stdout = original
    return "".join(collected)


def test_main_reports_every_ranking_and_a_named_start_is_not_a_candidate():
    text = main_output()
    for label in ("functions starts=", "ram refs=", "tables distinct="):
        assert label in text
    starts = rank.population()
    named = rank.named(starts)
    assert named <= set(starts)
    assert "address-named=%d" % (len(starts) - len(named)) in text


def test_a_ram_literal_load_is_a_base_whose_field_offsets_are_the_reader_sites():
    image = testkit.rom_bytes(
        os.path.join(os.path.dirname(os.path.dirname(rank.HERE)), "baserom.gba"),
        digest=rank.name_evidence.ROM_SHA256, size=0x800000)
    slots = rank.pointer_sites(image, [0x08000158])
    assert 0x03001C34 in slots
    assert slots[0x03001C34]["fields"][0] >= 1
    assert slots[0x03001C34]["sites"][0][0].startswith("080001")
