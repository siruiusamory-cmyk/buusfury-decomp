from __future__ import annotations

import csv
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import name_evidence

ROM = os.path.join(ROOT, "baserom.gba")
LEDGER = os.path.join(ROOT, "docs", "NAMING_LEDGER.csv")
RETIRED = os.path.join(ROOT, "docs", "NAMING_RETIRED.csv")


def image():
    if not os.path.exists(ROM):
        pytest.skip("baserom.gba is absent, so the audit cannot run")
    return name_evidence.read_rom(ROM)


def crafted(tmp_path, row):
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    (docs / "NAMING_LEDGER.csv").write_text(
        "address,old,new,evidence_class,evidence\n" + row + "\n", encoding="utf-8")
    return str(tmp_path)


def test_a_row_whose_effect_lies_past_its_return_fails(tmp_path):
    root = crafted(tmp_path, '0x08004DEE,sub_08004DEE,Blend_WriteAlpha1,hardware-register,'
                             '"writes 0x08004EAC then 0x08004EB2"')
    result = name_evidence.audit(image(), root)
    assert result[0]["verdict"] == "FAIL"
    assert result[0]["outside"] == [0x08004EAC, 0x08004EB2]


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


def test_every_ledger_row_passes_the_audit():
    for row in name_evidence.audit(image()):
        assert row["verdict"] == "PASS", row


def test_the_moved_name_is_recorded_by_the_ledger_not_by_a_retirement():
    if not os.path.exists(RETIRED):
        pytest.skip("docs/NAMING_RETIRED.csv is absent, so no name has been retired yet")
    retired = {row["address"] for row in csv.DictReader(open(RETIRED, encoding="utf-8"))}
    assert "0x0803FAF6" not in retired
    ledger = {row["address"]: row for row in csv.DictReader(open(LEDGER, encoding="utf-8"))}
    assert ledger["0x0803FB7C"]["old"] == "sub_0803FB7C"
    assert ledger["0x0803FB7C"]["new"] == "Irq_WriteMaster2"
