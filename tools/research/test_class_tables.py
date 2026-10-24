from __future__ import annotations

import csv
import os
import struct
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import class_tables

ROM = os.path.join(ROOT, "baserom.gba")


def image():
    if not os.path.exists(ROM):
        pytest.skip("baserom.gba is absent, so the class tables cannot be measured")
    return class_tables.romfile.read_rom(ROM, class_tables.name_evidence.ROM_SHA256)


def table():
    with open(class_tables.OUTPUT, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    slots = {(row["table"], row["slot"]): row["target"] for row in rows if row["slot"]}
    installers = {row["table"]: [part for part in row["installed_by"].split(";") if part]
                  for row in rows if not row["slot"]}
    return slots, installers


def test_the_three_class_table_facts_hold_at_the_retail_bytes():
    rom = image()
    slots, installers = table()
    assert slots[("0x0804C484", "22")] == "0x0800FA2A"
    assert slots[("0x0804DE7C", "2")] == "0x0801A6CC"
    assert len(installers["0x08049680"]) == 111
    assert (struct.unpack_from("<I", rom, 0x4C4DC)[0] + 0x0804C484) & 0xFFFFFFFF == 0x0800FA2B
    assert (struct.unpack_from("<I", rom, 0x4DE84)[0] + 0x0804DE7C) & 0xFFFFFFFF == 0x0801A6CD
