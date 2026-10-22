from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import endrom_index_census as census  # noqa: E402

HEADER = "run,scene,status,arrival,witness,witness_pc,log_sha256,log_lines\n"


def tables(tmp_path, rows, hits):
    runs = tmp_path / "runs.csv"
    runs.write_text(HEADER + "".join(rows), encoding="ascii")
    row_hits = tmp_path / "row_hits.csv"
    row_hits.write_text("run,start,hits,pcs,max_address\n" + "".join(hits), encoding="ascii")
    return str(runs), str(row_hits)


def test_a_watched_read_states_the_record_it_reached(tmp_path):
    runs, hits = tables(
        tmp_path,
        ["40,endrom-warp,ok,40,3,0x08008a0e,%s,7\n" % ("A" * 64)],
        ["40,0x72d6b8,9,0x08019b58,0x72d6f0\n"])
    row, = census.census(census.read_runs(runs), census.read_row_hits(hits))[1:2]
    assert (row["start"], row["whole"], row["tail"]) == (0x72D6B8, 268, 32)
    assert (row["highest"], row["index_reached"], row["hits"]) == (0x38, 0, 9)


def test_a_row_no_run_reads_states_no_index(tmp_path):
    runs, hits = tables(
        tmp_path,
        ["40,endrom-warp,ok,40,3,0x08008a0e,%s,7\n" % ("A" * 64)],
        [])
    for row in census.census(census.read_runs(runs), census.read_row_hits(hits)):
        assert row["index_reached"] is None
        assert census.verdict(row) == "raw, not reached"


def test_a_run_outside_the_census_scene_is_not_counted(tmp_path):
    runs, hits = tables(
        tmp_path,
        ["40,opening,ok,40,3,0x08008a0e,%s,7\n" % ("A" * 64)],
        ["40,0x77b2a8,2,0x0803c31e,0x77b2b0\n"])
    assert census.read_runs(runs) == []
    assert census.census([], census.read_row_hits(hits))[2]["index_reached"] is None


def test_the_page_is_checkable_and_a_moved_index_breaks_it(tmp_path, monkeypatch):
    runs, hits = tables(
        tmp_path,
        ["40,endrom-warp,ok,40,3,0x08008a0e,%s,7\n" % ("A" * 64)],
        ["40,0x762270,4,0x0801b2f4,0x762298\n"])
    page = tmp_path / "page.md"
    monkeypatch.setattr(census, "RUNS", runs)
    monkeypatch.setattr(census, "ROW_HITS", hits)
    monkeypatch.setattr(census, "DOC_OUT", str(page))
    assert census.main([]) == 0
    text = page.read_text(encoding="utf-8")
    assert "the watch reached index 1 of the 983 whole" in text
    assert "no automated run read a byte of the row" in text
    assert census.main(["--check"]) == 0
    page.write_text(text.replace("index 1 of the 983", "index 2 of the 983"), encoding="utf-8")
    try:
        census.main(["--check"])
    except SystemExit as refusal:
        assert "not the census" in str(refusal)
    else:
        raise AssertionError("a page with a moved index passed its check")
