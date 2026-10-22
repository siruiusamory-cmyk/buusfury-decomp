from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import runtime_targets  # noqa: E402


def a_map_row(start, end, reader):
    return {"start": "0x%06x" % start, "end": "0x%06x" % end, "bytes": str(end - start),
            "reader": reader}


def a_ledger_row(start, end, status, region="R32"):
    return {"start": "0x%06x" % start, "end": "0x%06x" % end, "bytes": str(end - start),
            "region": region, "status": status}


def an_entry_row(start, end, entry="pointer"):
    return {"start": "0x%06x" % start, "end": "0x%06x" % end, "bytes": str(end - start),
            "region": "R32", "entry": entry}


def test_the_map_block_splits_on_the_reader_column():
    rows = runtime_targets.table(
        [], [a_map_row(0x100, 0x110, "unproven"), a_map_row(0x110, 0x120,
                                                           "root_plus_0x10_data_only")], [])
    assert [row["group"] for row in rows] == ["set_b", "set_a"]
    assert [row["static_negative"] for row in rows] == ["K-218", "K-217"]


def test_only_a_runtime_pending_ledger_row_is_a_target():
    rows = runtime_targets.table([a_ledger_row(0x200, 0x210, "runtime-pending"),
                                  a_ledger_row(0x210, 0x220, "unmapped")], [], [])
    assert [(row["group"], row["start"], row["bytes"]) for row in rows] == \
        [("runtime_pending", 0x200, 16)]


def test_the_record_row_is_its_own_pointer_group():
    rows = runtime_targets.table([], [], [an_entry_row(0x0701FA, 0x071758),
                                          an_entry_row(0x04A24A, 0x04A59C),
                                          an_entry_row(0x036E76, 0x036E7A, "none")])
    assert [row["group"] for row in rows] == ["pointer_0x68", "pointer_other"]
    assert rows[0]["bytes"] == 0x071758 - 0x0701FA


def test_every_group_carries_a_question_and_a_negative():
    rows = runtime_targets.table([], [a_map_row(0x100, 0x110, "unproven")], [])
    assert rows[0]["question"] == runtime_targets.QUESTION["set_b"]
    assert set(runtime_targets.NEGATIVE) == set(runtime_targets.GROUPS)
    assert set(runtime_targets.QUESTION) == set(runtime_targets.GROUPS)


def test_the_reconciliation_refuses_a_moved_census(monkeypatch):
    rows = runtime_targets.table([a_ledger_row(0x200, 0x210, "runtime-pending")],
                                [a_map_row(0x100, 0x110, "unproven"),
                                 a_map_row(0x110, 0x120, "root_plus_0x10_data_only")],
                                [an_entry_row(0x0701FA, 0x07020A), an_entry_row(0x300, 0x310)])
    monkeypatch.setattr(runtime_targets, "EXPECT",
                        {"set_a": (1, 16), "set_b": (1, 16), "runtime_pending": (1, 16),
                         "pointer_0x68": (1, 16), "pointer_other": (1, 16)})
    monkeypatch.setattr(runtime_targets, "MAP_TOTAL", (2, 32))
    assert runtime_targets.check(rows)["set_b"] == (1, 16)
    monkeypatch.setattr(runtime_targets, "MAP_TOTAL", (3, 48))
    try:
        runtime_targets.check(rows)
    except SystemExit as refused:
        assert "the map block measures" in str(refused)
    else:
        raise AssertionError("a block total that does not add up must be refused")


def test_the_csv_carries_the_header_and_one_line_per_row():
    rows = runtime_targets.table([], [a_map_row(0x100, 0x110, "unproven")], [])
    lines = runtime_targets.csv_text(rows).splitlines()
    assert lines[0] == "group,start,end,bytes,region,static_negative,question"
    assert lines[1] == ("set_b,0x000100,0x000110,16,map,K-218,"
                        "does any instruction read this child-list payload, and at what offset "
                        "from its start?")
    assert len(lines) == len(rows) + 1
