from __future__ import annotations

import csv
import os
import struct
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import name_evidence

ROM = os.path.join(ROOT, "baserom.gba")
LEDGER = os.path.join(ROOT, "tools", "lint", "NAMING_LEDGER.csv")
RETIRED = os.path.join(ROOT, "tools", "lint", "NAMING_RETIRED.csv")


def image():
    if not os.path.exists(ROM):
        pytest.skip("baserom.gba is absent, so the audit cannot run")
    return name_evidence.read_rom(ROM)


def crafted(tmp_path, row):
    store = tmp_path / "tools" / "lint"
    store.mkdir(parents=True)
    (store / "NAMING_LEDGER.csv").write_text(
        "address,old,new,evidence_class,evidence\n" + row + "\n", encoding="utf-8")
    return str(tmp_path)


def test_an_effect_in_a_later_block_counts_for_its_function(tmp_path):
    root = crafted(tmp_path, '0x0803FB7C,sub_0803FB7C,Irq_WriteMaster2,hardware-register,'
                             '"writes IME 0x04000208: 0x0803FC2A strh r0, [r1, #8]"')
    result = name_evidence.audit(image(), root)
    assert result[0]["outside"] == []
    assert result[0]["verdict"] == "PASS"


def test_an_effect_in_another_function_does_not_count(tmp_path):
    root = crafted(tmp_path, '0x0803FB7C,sub_0803FB7C,Irq_WriteMaster2,hardware-register,'
                             '"calls BIOS Div (SWI 0x06) at 0x0800BA7A"')
    result = name_evidence.audit(image(), root)
    assert result[0]["verdict"] == "FAIL"
    assert result[0]["outside"] == [0x0800BA7A]


def test_a_row_whose_effect_lies_inside_its_function_passes(tmp_path):
    root = crafted(tmp_path, '0x080080D8,sub_080080D8,Irq_WriteEnable1,hardware-register,'
                             '"reads 0x0800815C and writes 0x08008166"')
    assert name_evidence.audit(image(), root)[0]["verdict"] == "PASS"


def test_a_caller_role_row_must_quote_a_call_to_it(tmp_path):
    good = crafted(tmp_path / "good", '0x08049144,sub_08049144,Thunk_PaletteCopy,caller-role,'
                                      '"0x0800657A calls it"')
    assert name_evidence.audit(image(), good)[0]["verdict"] == "PASS"
    bad = crafted(tmp_path / "bad", '0x08049144,sub_08049144,Thunk_PaletteCopy,caller-role,'
                                    '"0x080080D8 calls it"')
    assert name_evidence.audit(image(), bad)[0]["verdict"] == "FAIL"


def test_a_row_that_cites_the_call_its_body_makes_passes(tmp_path):
    root = crafted(tmp_path, '0x08009196,sub_08009196,Ram_CopyFiveWords1,behaviour-test,'
                             '"0x080091AC calls 0x080099B6"')
    assert name_evidence.audit(image(), root)[0]["verdict"] == "PASS"


def test_a_row_that_cites_the_word_its_body_loads_passes(tmp_path):
    root = crafted(tmp_path, '0x08006880,sub_08006880,Object_Construct2,behaviour-test,'
                             '"asm/Object_Construct2.s:19 stores 0x0804BF3C at +0"')
    assert name_evidence.audit(image(), root)[0]["verdict"] == "PASS"


def test_a_row_that_names_an_address_its_body_neither_calls_nor_loads_fails(tmp_path):
    root = crafted(tmp_path, '0x08009196,sub_08009196,Ram_CopyFiveWords1,behaviour-test,'
                             '"0x0800BA7A is the BIOS Div call site"')
    result = name_evidence.audit(image(), root)
    assert result[0]["verdict"] == "FAIL"
    assert result[0]["outside"] == [0x0800BA7A]


def thumb_bl(offset, delta):
    high = 0xF000 | (((delta >> 22) & 1) << 10) | ((delta >> 12) & 0x3FF)
    low = 0xF800 | ((delta >> 1) & 0x7FF)
    data = bytearray(offset + 4)
    struct.pack_into("<HH", data, offset, high, low)
    return bytes(data)


def test_a_thumb_bl_pair_decodes_to_its_target_from_pc_plus_four():
    rom = thumb_bl(0x100, 0x2F8)
    site = name_evidence.ROM_BASE + 0x100
    found = name_evidence.instruction(rom, site, "thumb")
    assert found is not None
    assert found.size == 4
    assert found.mnemonic == "bl"
    assert name_evidence.call_target(rom, site) == site + 4 + 0x2F8


def test_a_backward_thumb_bl_offset_is_sign_extended():
    rom = thumb_bl(0x200, -0x102)
    site = name_evidence.ROM_BASE + 0x200
    assert name_evidence.call_target(rom, site) == site + 4 - 0x102


def test_the_walk_reads_a_thumb_bl_as_one_instruction():
    rom = thumb_bl(0x100, 0x2F8)
    walked = [found.address for found in name_evidence.steps(rom, (0x100, 4), "thumb")]
    assert walked == [name_evidence.ROM_BASE + 0x100]


def test_a_caller_role_row_cites_a_thumb_bl_site(tmp_path):
    root = crafted(tmp_path, '0x08049144,sub_08049144,Thunk_PaletteCopy,caller-role,'
                             '"0x0800657A calls it"')
    rom = image()
    assert name_evidence.call_target(rom, 0x0800657A) == 0x08049144
    assert name_evidence.audit(rom, root)[0]["verdict"] == "PASS"


def test_a_pool_word_and_the_next_start_bound_the_body():
    data = bytearray(0x140)
    struct.pack_into("<8H", data, 0x100, 0x4801, 0x4770, 0x46C0, 0x46C0,
                     0x0050, 0x0400, 0x4770, 0x46C0)
    base = name_evidence.ROM_BASE
    starts, parents = {base + 0x100, base + 0x10C}, {base + 0x100: [base + 0x104]}
    body = name_evidence.extent(bytes(data), base + 0x100, (0x100, 0x40, "thumb"),
                                starts, parents)
    assert base + 0x104 in body
    assert base + 0x106 in body
    assert base + 0x108 not in body
    assert base + 0x10C not in body


def test_an_unreferenced_census_row_starts_a_body(tmp_path):
    store = tmp_path / "tools" / "research"
    store.mkdir(parents=True)
    (store / "FUNCTION_BOUNDS.csv").write_text(
        "address,kind,limb,parent\n0x08000100,unreferenced,,\n", encoding="utf-8")
    starts, parents = name_evidence.census(str(tmp_path))
    assert starts == {0x08000100}
    assert parents == {}


def test_every_ledger_row_passes_the_audit():
    for row in name_evidence.audit(image()):
        assert row["verdict"] == "PASS", row


def test_the_moved_name_is_recorded_by_the_ledger_not_by_a_retirement():
    if not os.path.exists(RETIRED):
        pytest.skip("tools/lint/NAMING_RETIRED.csv is absent, so no name has been retired yet")
    retired = {row["address"] for row in csv.DictReader(open(RETIRED, encoding="utf-8"))}
    assert "0x0803FAF6" not in retired
    ledger = {row["address"]: row for row in csv.DictReader(open(LEDGER, encoding="utf-8"))}
    assert ledger["0x0803FB7C"]["old"] == "sub_0803FB7C"
    assert ledger["0x0803FB7C"]["new"] == "Irq_WriteMaster2"
