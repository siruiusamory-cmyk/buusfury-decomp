from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import recomp_leads  # noqa: E402

TOML = """
[program]
entry_pc = 0x08000000

[[code_copy]]
addr = 0x087B79A4
name = "iwram_support_code"

[[extra_func]]
addr = 0x08001234
note = "observed at runtime"

[[extra_func]]
addr = 0x03000B6C
note = "a RAM address, not a ROM offset"

[[extra_func]]
addr = 0x08800000
note = "one past the image"

[[jump_table]]
addr = 0x0800abcd
"""


def a_row(start, end, status="unmapped", region="R32"):
    return {"start": "0x%06x" % start, "end": "0x%06x" % end, "bytes": str(end - start),
            "region": region, "status": status, "attempts": ""}


def test_only_rom_addresses_of_the_two_entry_kinds_are_leads(tmp_path):
    path = tmp_path / "game.toml"
    path.write_text(TOML, encoding="ascii")
    found = recomp_leads.entries(str(path))
    assert found == [(0x1234, "extra_func"), (0xABCD, "jump_table")]


def test_a_row_holds_an_entry_half_open():
    found = [(0x1234, "extra_func")]
    rows = recomp_leads.leads(found, [a_row(0x1200, 0x1234), a_row(0x1234, 0x1240),
                                      a_row(0x1230, 0x1240)])
    assert [row["start"] for row in rows] == [0x1234, 0x1230]


def test_every_entry_is_reported_and_no_other_row_is():
    found = [(0x1010, "extra_func"), (0x1020, "jump_table")]
    rows = recomp_leads.leads(found, [a_row(0x1000, 0x1100), a_row(0x1100, 0x1200)])
    assert len(rows) == 1
    assert rows[0]["entries"] == [0x1010, 0x1020]
    assert rows[0]["bytes"] == 0x100


def test_a_row_carries_the_columns_it_was_read_from():
    found = [(0x2000, "extra_func")]
    row = recomp_leads.leads(found, [a_row(0x2000, 0x2010, status="runtime-pending")])[0]
    assert (row["region"], row["status"]) == ("R32", "runtime-pending")
