from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import recomp_cited  # noqa: E402

TARGETS = """group,start,end,bytes,region,static_negative,question
set_a,0x1000,0x1010,16,map,K-217,a question
runtime_pending,0x275c60,0x275ca8,72,R32,T-197,another
"""

LEDGER = """0x2000,16,t,r,b,t,p,16
0x3000,8,d,r,b,t,p,8
0x1000,16,t,r,b,t,p,16
"""


def write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="ascii")
    return str(path)


def hits(tmp_path, rows):
    text = "pc,lr,addr,width,frame,value\n" + "".join(
        "%s,%s,%s,%s,%s,0\n" % row for row in rows)
    return recomp_cited.read_hits(write(tmp_path, "hits.csv", text))


def test_a_read_through_a_transcribed_reader_is_one_citation(tmp_path):
    found = recomp_cited.citations(
        list(hits(tmp_path, [("0x08002002", "0x08002010", "0x08001004", 2, 7)])),
        recomp_cited.read_targets(write(tmp_path, "t.csv", TARGETS)),
        recomp_cited.read_ledger(write(tmp_path, "l.csv", LEDGER)))
    assert found == [{"group": "set_a", "start": 0x1000, "end": 0x1010, "address": 0x08001004,
                      "pc": 0x08002002, "reader_start": 0x2000, "reader_end": 0x2010,
                      "width": 2, "frame": 7}]


def test_a_reader_inside_the_cited_row_itself_cites_nothing(tmp_path):
    found = recomp_cited.citations(
        list(hits(tmp_path, [("0x08001002", "0x08001010", "0x08001004", 2, 7)])),
        recomp_cited.read_targets(write(tmp_path, "t.csv", TARGETS)),
        recomp_cited.read_ledger(write(tmp_path, "l.csv", LEDGER)))
    assert found == []


def test_a_reader_in_a_data_row_cites_nothing(tmp_path):
    found = recomp_cited.citations(
        list(hits(tmp_path, [("0x08003000", "0x08003008", "0x08001004", 4, 7)])),
        recomp_cited.read_targets(write(tmp_path, "t.csv", TARGETS)),
        recomp_cited.read_ledger(write(tmp_path, "l.csv", LEDGER)))
    assert found == []


def test_a_read_outside_every_target_row_is_ignored(tmp_path):
    found = recomp_cited.citations(
        list(hits(tmp_path, [("0x08002002", "0x08002010", "0x08001010", 2, 7),
                             ("0x08002002", "0x08002010", "0x03000004", 2, 7)])),
        recomp_cited.read_targets(write(tmp_path, "t.csv", TARGETS)),
        recomp_cited.read_ledger(write(tmp_path, "l.csv", LEDGER)))
    assert found == []


def test_two_pcs_cite_twice_and_a_repeat_keeps_the_earliest_frame(tmp_path):
    found = recomp_cited.citations(
        list(hits(tmp_path, [("0x08002002", "0", "0x08001004", 2, 9),
                             ("0x08002002", "0", "0x08001004", 2, 4),
                             ("0x0800200a", "0", "0x0800100c", 4, 5)])),
        recomp_cited.read_targets(write(tmp_path, "t.csv", TARGETS)),
        recomp_cited.read_ledger(write(tmp_path, "l.csv", LEDGER)))
    assert [(row["pc"], row["frame"], row["width"]) for row in found] == [
        (0x08002002, 4, 2), (0x0800200A, 5, 4)]


def test_a_row_is_found_from_its_guest_address(tmp_path):
    found = recomp_cited.citations(
        list(hits(tmp_path, [("0x08002002", "0", "0x08275C64", 4, 1)])),
        recomp_cited.read_targets(write(tmp_path, "t.csv", TARGETS)),
        recomp_cited.read_ledger(write(tmp_path, "l.csv", LEDGER)))
    assert [(row["start"], row["group"], row["width"]) for row in found] == [
        (0x275C60, "runtime_pending", 4)]


def test_the_range_file_carries_every_target_and_each_lead(tmp_path):
    leads = write(tmp_path, "leads.txt", "0x4000 0x4004\n")
    out = str(tmp_path / "ranges.txt")
    recomp_cited.main(["--targets", write(tmp_path, "t.csv", TARGETS), "--leads", leads,
                       "--ranges-out", out])
    assert open(out, encoding="ascii").read().splitlines() == [
        "1000 1010", "4000 4004", "275c60 275ca8"]


CITED = """group,start,end,address,pc,reader_start,reader_end,width,frame
set_a,0x1000,0x1010,0x08001004,0x08002002,0x002000,0x002010,2,7
"""


def test_excluding_a_cited_row_leaves_the_uncited_row_and_its_bytes(tmp_path):
    out = str(tmp_path / "ranges.txt")
    recomp_cited.main(["--targets", write(tmp_path, "t.csv", TARGETS),
                       "--exclude-cited", write(tmp_path, "c.csv", CITED),
                       "--ranges-out", out])
    assert open(out, encoding="ascii").read().splitlines() == ["275c60 275ca8"]
