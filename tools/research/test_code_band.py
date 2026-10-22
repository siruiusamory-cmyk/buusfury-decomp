from __future__ import annotations

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import code_band  # noqa: E402


def test_one_class_per_row_and_the_classes_sum_to_the_population():
    population = [(0x00, 0x10), (0x10, 0x20), (0x20, 0x30), (0x30, 0x40), (0x40, 0x50)]
    table = code_band.assign(population, {(0x00, 0x10): "a"},
                             {(0x10, 0x20): "b"}, {(0x20, 0x30): "c"},
                             {(0x30, 0x40)})
    assert [entry["class"] for entry in table] == ["method-target", "source-entry", "transitive",
                                                   "pool-data", "unreached"]
    assert sum(entry["end"] - entry["start"] for entry in table) == 0x50
    assert len(table) == len(population)


def test_the_first_class_that_fires_owns_a_row_that_several_predicates_match():
    row = (0x10, 0x20)
    table = code_band.assign([row], {row: "method"}, {row: "branch"}, {row: "walk"}, {row})
    assert table[0]["class"] == "method-target"
    assert table[0]["proof"] == "method"


def test_every_class_carries_its_own_entry_proof():
    assert set(code_band.CLASSES) == set(code_band.PROOF)
    assert "class-table slot" in code_band.PROOF["method-target"]


def test_outside_rows_keeps_the_targets_a_region_does_not_own():
    import thumb_bodies
    spans = [(0x10, 0x20), (0x30, 0x40)]
    index = thumb_bodies.Rows(spans)
    region_of = {(0x10, 0x20): "R19", (0x30, 0x40): "R00"}
    sites = [(0x04AAF4, 0x04AAFC, 0x12), (0x04AAF4, 0x04AB00, 0x34), (0x04AAF4, 0x04AB04, 0x99)]
    found = code_band.outside_rows(sites, index, region_of, "R19")
    assert list(found) == [(0x30, 0x40)]
    assert found[(0x30, 0x40)] == ["method table 0x%08x slot 0x%08x -> 0x%08x"
                                   % (thumb_bodies.ROM_BASE + 0x04AAF4,
                                      thumb_bodies.ROM_BASE + 0x04AB00,
                                      thumb_bodies.ROM_BASE + 0x34)]


def test_the_prologue_control_runs_only_when_it_is_asked(monkeypatch):
    table = [{"start": 0, "end": 0x10, "class": "unreached", "proof": "", "region": "R32"}]
    monkeypatch.setattr(code_band, "measure",
                        lambda *a, **k: (table, {"unreached": 1}, {"unreached": 0x10},
                                         ({}, {}, [(0, 0x10)])))
    calls = []
    monkeypatch.setattr(code_band, "prologue_control",
                        lambda population, shape: calls.append(shape) or (0, 0, 0, 0, 0))
    monkeypatch.setattr(code_band.thumb_bodies, "prologue_entries", lambda population: {})
    assert code_band.main(["--region", "R32"]) == 0
    assert calls == []
    assert code_band.main(["--region", "R32", "--prologue"]) == 0
    assert calls == [{}]


def test_check_accepts_a_disjoint_file_and_refuses_an_overlap(tmp_path):
    good = tmp_path / "good.csv"
    good.write_text("start,end,class,proof\n0x0,0x10,unreached,\n0x10,0x20,unreached,\n",
                    newline="\n")
    assert code_band.check(str(good)) == 0
    bad = tmp_path / "bad.csv"
    bad.write_text("start,end,class,proof\n0x0,0x18,unreached,\n0x10,0x20,unreached,\n",
                   newline="\n")
    try:
        code_band.check(str(bad))
    except SystemExit as error:
        assert "overlap" in str(error)
    else:
        raise AssertionError("an overlapping pair was accepted")
