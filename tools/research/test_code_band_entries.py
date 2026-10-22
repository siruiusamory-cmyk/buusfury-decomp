from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import code_band_entries  # noqa: E402
import thumb_bodies  # noqa: E402


def a_row(start=0x160, end=0x170):
    return {"start": start, "end": end, "bytes": end - start, "region": "R32", "text_tables": ""}


def test_a_direct_bl_site_is_the_source_channel_with_that_site():
    row = a_row()
    original = thumb_bodies.ROM
    thumb_bodies.ROM = bytes.fromhex("00f002f8") + bytes(0x100)
    try:
        size, mnemonic, operands = thumb_bodies.decode(0)
    finally:
        thumb_bodies.ROM = original
    assert (size, mnemonic) == (4, "bl")
    assert thumb_bodies.direct_target(mnemonic, operands) == thumb_bodies.ROM_BASE + 8
    site = "Thumb 0x%08x %s %s" % (thumb_bodies.ROM_BASE, mnemonic, operands)
    found = {"source": {(row["start"], row["end"]): site}}
    entry = code_band_entries.census([row], found)[0]
    assert (entry["entry"], entry["site"]) == ("source", site)


def test_a_site_at_the_row_start_is_preferred_to_one_inside_it():
    row = (0x160, 0x170)
    found = {"source": {row: [(0x168, "branch", "inside", "tier1"),
                              (0x160, "branch", "start", "tier2")]}}
    assert code_band_entries.first(found["source"]) == {row: "start"}


def test_the_first_channel_that_fires_owns_the_row_and_both_flags_stay_true():
    row = a_row()
    span = (row["start"], row["end"])
    found = {"method": {span: "method table 0x0804aaf4 slot 0x0804aafc -> 0x08000160"},
             "pool": {span: "code ldr 0x08053b84 pool word"}}
    entry = code_band_entries.census([row], found)[0]
    assert entry["entry"] == "method"
    assert entry["method"] is True and entry["pool"] is True
    assert entry["site"] == found["method"][span]


def test_a_row_no_channel_names_is_none():
    entry = code_band_entries.census([a_row()], {})[0]
    assert (entry["entry"], entry["site"]) == ("none", "")
    assert [entry[name] for name in code_band_entries.CHANNELS] == [False] * 6


def test_the_text_tables_column_marks_only_the_classed_row():
    rows = [a_row(0x160, 0x170), dict(a_row(0x170, 0x180), text_tables="text/tables")]
    table = code_band_entries.census(rows, {})
    assert [entry["text_tables"] for entry in table] == ["", "text/tables"]
    lines = code_band_entries.csv_text(table).splitlines()
    assert lines[1].split(",")[4] == ""
    assert lines[2].split(",")[4] == "text/tables"


def test_the_writer_emits_the_header_and_one_line_per_row():
    table = code_band_entries.census([a_row(0x160, 0x170), a_row(0x170, 0x180)],
                                     {"source": {(0x170, 0x180): "Thumb 0x08000170, b #0x1"}})
    lines = code_band_entries.csv_text(table).splitlines()
    assert lines[0] == ("start,end,bytes,region,text_tables,source,converted,method,pool,pointer,"
                        "prologue,entry,site,shape")
    assert len(lines) == len(table) + 1
    assert lines[1] == "0x000160,0x000170,16,R32,,no,no,no,no,no,no,none,,"
    assert lines[2] == "0x000170,0x000180,16,R32,,yes,no,no,no,no,no,source,Thumb 0x08000170; b #0x1,"


def test_the_summary_reports_every_channel_and_the_none_rows():
    table = code_band_entries.census([a_row(0x160, 0x170), a_row(0x170, 0x180)],
                                     {"prologue": {(0x160, 0x170): "PUSH {..,lr}"}})
    lines = code_band_entries.summary(table, "population")
    assert lines[0] == "population: 2 row(s) 32 B"
    assert "| `source` | 0 | 0 |" in lines and "| `prologue` | 1 | 16 |" in lines
    assert "| **`entry=none`** | **2** | **32** |" in lines
    assert "| `code` | 0 | 0 |" in lines and "| `table` | 0 | 0 |" in lines


def test_a_row_a_channel_names_is_the_entry_shape():
    found = {"pointer": {(0x160, 0x170): "pointer table word 0x1 = 0x08000160"}}
    assert code_band_entries.shapes([a_row()], found)[(0x160, 0x170)][0] == "entry"


def test_code_needs_the_walk_to_return_and_the_permuted_row_not_to(monkeypatch):
    row = a_row()
    span = (row["start"], row["end"])
    calls = []

    def fake_returns_at(one):
        calls.append(one)
        return len(calls) == 1

    monkeypatch.setattr(code_band_entries, "returns_at", fake_returns_at)
    monkeypatch.setattr(code_band_entries, "permuted_row", lambda one: bytes(0x200))
    assert code_band_entries.shapes([row], {})[span][0] == "code"
    calls.clear()

    def always(one):
        calls.append(one)
        return True

    monkeypatch.setattr(code_band_entries, "returns_at", always)
    monkeypatch.setattr(code_band_entries, "first_word_inside", lambda one: False)
    assert code_band_entries.shapes([row], {})[span][0] == "table"
    monkeypatch.setattr(code_band_entries, "first_word_inside", lambda one: True)
    assert code_band_entries.shapes([row], {})[span][0] == "table-pointer"


def test_permuted_row_keeps_the_span_and_the_byte_multiset():
    original = thumb_bodies.ROM
    thumb_bodies.ROM = bytes(16) + bytes(range(16)) + bytes(16)
    try:
        permuted = code_band_entries.permuted_row((16, 32))
    finally:
        thumb_bodies.ROM = original
    assert len(permuted) == 48
    assert sorted(permuted[16:32]) == sorted(range(16))
    assert permuted[:16] == bytes(16) and permuted[32:] == bytes(16)



def test_rows_text_lists_only_the_named_channel():
    table = [dict(a_row(0x160, 0x170), entry="pointer"), dict(a_row(0x170, 0x180), entry="source")]
    assert code_band_entries.rows_text(table, "pointer") == "start,end\n0x000160,0x000170\n"
