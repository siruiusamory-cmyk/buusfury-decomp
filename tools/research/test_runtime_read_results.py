from __future__ import annotations

import csv
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "runtime"))

import runtime_read_results as results  # noqa: E402
import recomp_read_sweep  # noqa: E402
import warp_patch  # noqa: E402


TARGET = {"group": "set_b", "start": 0x1000, "end": 0x1100}
OWNERS = {0x1000: [40]}
RUNS = [{"run": 40, "status": "ok", "arrival": 40, "witness": 3, "witness_pc": "0x08008a0e",
         "log_sha256": "A" * 64, "log_lines": 9, "patched_sha256": "B" * 64, "seconds": 1}]
CITATION = {"run": 40, "group": "set_b", "start": 0x1000, "end": 0x1100, "address": 0x08001004,
            "pc": 0x08002002, "reader_start": 0x2000, "reader_end": 0x2010, "width": 2,
            "frame": 7}
HIT = {"run": 40, "start": 0x1000, "hits": 3, "pcs": ["0x030002bc"]}


def status(owners=OWNERS, runs=RUNS, citations=(), row_hits=()):
    return results.status_of(TARGET, owners, runs, list(citations), list(row_hits))[0]


def test_a_read_through_a_transcribed_reader_is_cited():
    assert status(citations=[CITATION]) == "cited"


def test_hits_from_outside_the_ledger_are_read_uncited():
    assert status(row_hits=[HIT]) == "read-uncited"


def test_no_hit_while_the_run_is_live_is_silent_live():
    assert status() == "silent-live"


def test_no_hit_and_a_dead_liveness_channel_is_not_a_negative():
    dead = [{**RUNS[0], "witness": 0}]
    assert status(runs=dead) == "silent-dead-log"


def test_no_run_visited_an_owner_map_is_reported_separately():
    assert status(owners={0x1000: [7]}) == "owner-map-not-reached"


def test_a_run_that_did_not_arrive_does_not_count_as_a_visit():
    wrong = [{**RUNS[0], "status": "wrong-arrival-374", "arrival": 374}]
    assert status(runs=wrong) == "owner-map-not-reached"
    timed_out = [{**RUNS[0], "status": "timeout", "arrival": None}]
    assert status(runs=timed_out) == "owner-map-not-reached"


def test_the_boundary_claim_counts_two_pcs_at_one_offset():
    same_offset = {**CITATION, "pc": 0x0800200A}
    second_offset = {**CITATION, "address": 0x0800100C, "pc": 0x08002020}
    cited = {"group": "set_b", "start": 0x1000, "end": 0x1100, "bytes": 0x100,
             "status": "cited", "readers": "0x08002002", "offsets": "4", "widths": "2",
             "frames": "7", "owners": "map:0040", "liveness": "1 run(s) live, 1 visitor(s)"}
    text = results.doc_text([cited], RUNS, [CITATION, same_offset, second_offset])
    claim = [line for line in text.splitlines()
             if "distinct reader pcs" in line or "field boundary" in line]
    assert claim == ["1 read offset(s) in 1 cited row(s) carry two or more distinct reader pcs",
                     "(`0x001000`+4); each such offset is a field boundary in the plan's predicate."]


def test_the_run_table_names_each_scene_and_defaults_a_row_without_one():
    rows = [{"group": "set_b", "start": 0x1000, "end": 0x1100, "bytes": 0x100,
             "status": "cited", "readers": "0x08002002", "offsets": "4", "widths": "2",
             "frames": "7", "owners": "map:0040", "liveness": "1 run(s) live, 1 visitor(s)"}]
    old = dict(RUNS[0])
    new = {**old, "run": 41, "arrival": 41, "scene": "opening"}
    table = [line for line in results.doc_text(rows, [old, new], []).splitlines()
             if line.startswith("| `map:")]
    assert table == ["| `map:0040` | saved-game-warp | ok | 40 | 3 | 9 | `%s` | 1 |" % ("A" * 16),
                     "| `map:0041` | opening | ok | 41 | 3 | 9 | `%s` | 1 |" % ("A" * 16)]


CURRENT_RUN_HEADER = ["run", "scene", "status", "arrival", "witness", "witness_pc",
                      "log_sha256", "log_lines", "patched_sha256", "patched_sha1",
                      "changed_offsets", "seconds", "note"]


def test_either_directory_order_migrates_one_canonical_header_and_every_row(
        tmp_path, monkeypatch):
    old, new = tmp_path / "old", tmp_path / "new"
    old.mkdir()
    new.mkdir()
    (old / "runs.csv").write_text(
        "run,status,arrival,witness,witness_pc,log_sha256,log_lines,patched_sha256,patched_sha1,"
        "changed_offsets,seconds,note\n"
        "76,ok,76,3,0x08008a0e,%s,9688,%s,abc,0x295c4d;0x295c4e,12.0,none\n"
        % ("A" * 64, "B" * 64), encoding="ascii")
    (new / "runs.csv").write_text(
        "run,scene,status,arrival,witness,witness_pc,log_sha256,log_lines,patched_sha256,"
        "patched_sha1,changed_offsets,seconds,note\n"
        "77,opening,ok,77,3,0x08008a0e,%s,1200,%s,def,0x295c4d,61.5,second scene\n"
        % ("C" * 64, "D" * 64), encoding="ascii")
    for directory, run in ((old, 76), (new, 77)):
        (directory / "citations.csv").write_text(
            "run,group,start,end,address,pc,reader_start,reader_end,width,frame\n"
            "%d,set_b,0x17a9ac,0x17aaac,0x0817a9ac,0x08009d04,0x009b80,0x009d6c,4,1525\n" % run,
            encoding="ascii")
        (directory / "row-hits.csv").write_text(
            "run,start,hits,pcs\n%d,0x17a9ac,447,0x08009d04\n" % run, encoding="ascii")
    seen = []
    for order in ((old, new), (new, old)):
        for name, filename in (("RUNS", "runs.csv"), ("CITATIONS", "citations.csv"),
                               ("ROW_HITS", "row-hits.csv")):
            monkeypatch.setattr(results, name, str(tmp_path / filename))
        results.migrate([str(directory) for directory in order])
        with open(results.RUNS, newline="") as handle:
            assert handle.readline().strip().split(",") == CURRENT_RUN_HEADER
        seen.append(sorted((row["run"], row["scene"], row["arrival"], row["witness"],
                            row["log_lines"]) for row in results.read_csv(results.RUNS)))
        assert len(results.read_csv(results.CITATIONS)) == 2
        assert len(results.read_csv(results.ROW_HITS)) == 2
    assert seen == [[(76, results.DEFAULT_SCENE, 76, 3, 9688),
                     (77, "opening", 77, 3, 1200)]] * 2


def test_a_scene_with_a_comma_and_a_quote_round_trips_through_the_sweep(tmp_path, monkeypatch):
    scene = 'opening,no-save "quoted"'
    note = 'label, with "quotes"'
    result = {"run": 40, "scene": scene, "status": "ok", "arrival": 40, "witness": 3,
              "witness_pc": 0x08008A0E, "log_sha256": "A" * 64, "log_lines": 9,
              "patched_sha256": "B" * 64, "patched_sha1": "c" * 40,
              "changed_offsets": ["0x295c4d"], "seconds": 12.0, "note": note,
              "citations": [{**CITATION, "run": 40}],
              "row_hits": {0x1000: {"hits": 3, "pcs": {0x030002BC}, "max": 0x1004}}}
    monkeypatch.setattr(recomp_read_sweep, "run_one", lambda args, index, directory: result)
    for name, text in (("targets.csv", "group,start,end\nset_b,0x1000,0x1100\n"),
                       ("ledger.csv", "1000,16,t\n"),
                       ("ranges.txt", "1000 1100\n")):
        (tmp_path / name).write_text(text, encoding="ascii")
    for name in ("rom.gba", "save.sav", "trace.txt"):
        (tmp_path / name).write_bytes(b"")
    out = tmp_path / "out"
    assert recomp_read_sweep.main([
        "--rom", str(tmp_path / "rom.gba"), "--save", str(tmp_path / "save.sav"),
        "--trace", str(tmp_path / "trace.txt"), "--ranges", str(tmp_path / "ranges.txt"),
        "--out", str(out), "--maps", "40", "--scene", scene,
        "--targets", str(tmp_path / "targets.csv"), "--ledger", str(tmp_path / "ledger.csv"),
    ]) == 0
    text = (out / "runs.csv").read_text(encoding="ascii")
    assert "\r" not in text
    run, = list(csv.DictReader(io.StringIO(text)))
    assert None not in run
    assert (run["run"], run["scene"], run["status"], run["arrival"], run["witness"],
            run["log_lines"], run["note"]) == ("40", scene, "ok", "40", "3", "9", note)
    for name, filename in (("RUNS", "runs.csv"), ("CITATIONS", "citations.csv"),
                           ("ROW_HITS", "row-hits.csv")):
        monkeypatch.setattr(results, name, str(tmp_path / filename))
    results.migrate([str(out)])
    imported = results.read_csv(results.RUNS)[0]
    assert (imported["scene"], imported["run"], imported["arrival"], imported["witness"],
            imported["log_lines"], imported["note"]) == (scene, 40, 40, 3, 9, note)
    cited, = results.read_csv(results.CITATIONS)
    assert (cited["start"], cited["address"], cited["pc"], cited["width"],
            cited["frame"]) == (0x1000, 0x08001004, 0x08002002, 2, 7)
    hit, = results.read_csv(results.ROW_HITS)
    assert (hit["run"], hit["start"], hit["hits"], hit["pcs"]) == (40, 0x1000, 3,
                                                                   "0x030002bc")
    assert (out / "row-hits.csv").read_text(encoding="ascii").splitlines()[1].endswith(
        ",0x030002bc,0x001004")


def test_a_sweep_style_table_survives_the_radix_round_trip(tmp_path, monkeypatch):
    private = tmp_path / "private"
    private.mkdir()
    (private / "runs.csv").write_text(
        "run,status,arrival,witness,witness_pc,log_sha256,log_lines,patched_sha256,patched_sha1,"
        "changed_offsets,seconds,note\n"
        "76,ok,76,3,0x08008a0e,%s,9688,%s,abc,0x295c4d;0x295c4e,12.0,none\n"
        % ("A" * 64, "B" * 64), encoding="ascii")
    (private / "citations.csv").write_text(
        "run,group,start,end,address,pc,reader_start,reader_end,width,frame\n"
        "76,set_b,0x17a9ac,0x17aaac,0x0817a9ac,0x08009d04,0x009b80,0x009d6c,4,1525\n",
        encoding="ascii")
    (private / "row-hits.csv").write_text(
        "run,start,hits,pcs\n76,0x17a9ac,447,0x08009d04\n", encoding="ascii")
    for name, filename in (("RUNS", "runs.csv"), ("CITATIONS", "citations.csv"),
                           ("ROW_HITS", "row-hits.csv")):
        monkeypatch.setattr(results, name, str(tmp_path / filename))
    results.migrate([str(private)])
    run, = results.read_csv(results.RUNS)
    assert (run["run"], run["arrival"], run["witness"], run["log_lines"]) == (76, 76, 3, 9688)
    citation, = results.read_csv(results.CITATIONS)
    assert (citation["start"], citation["address"], citation["pc"], citation["width"],
            citation["frame"]) == (0x17A9AC, 0x0817A9AC, 0x08009D04, 4, 1525)
    hit, = results.read_csv(results.ROW_HITS)
    assert (hit["run"], hit["start"], hit["hits"]) == (76, 0x17A9AC, 447)


def test_the_warp_patch_guard_refuses_a_byte_inside_a_watched_row():
    assert "outside every watched row" in warp_patch.guard([0x295C4D, 0x295C4E])
    try:
        warp_patch.guard([0x17A9AC])
    except SystemExit as refusal:
        assert "watched span" in str(refusal)
    else:
        raise AssertionError("a patch inside set_b's first row was not refused")


def test_an_arrival_pointer_off_the_entry_stride_is_not_an_arrival(tmp_path):
    iwram = tmp_path / "iwram.bin"
    image = bytearray(0x2000)
    image[0x1980:0x1984] = (0x08000000 + warp_patch.ME_TABLE
                            + 40 * warp_patch.ME_SIZE).to_bytes(4, "little")
    iwram.write_bytes(image)
    assert recomp_read_sweep.arrival(str(iwram)) == 40
    image[0x1980:0x1984] = (0x08000000 + warp_patch.ME_TABLE
                            + 40 * warp_patch.ME_SIZE + 4).to_bytes(4, "little")
    iwram.write_bytes(image)
    assert recomp_read_sweep.arrival(str(iwram)) is None


def test_a_map_index_outside_the_table_is_refused():
    rom = bytearray(warp_patch.ME_TABLE + 452 * warp_patch.ME_SIZE)
    last = warp_patch.ME_TABLE + 451 * warp_patch.ME_SIZE
    rom[last:last + 2] = b"\x01\xc3"
    assert warp_patch.map_key(bytes(rom), 451) == b"\x01\xc3"
    for index in (452, -1):
        try:
            warp_patch.map_key(bytes(rom), index)
        except SystemExit as refused:
            assert "MapEntry" in str(refused)
        else:
            raise AssertionError("map index %d was accepted" % index)


def test_a_retarget_that_moves_one_key_byte_is_accepted(tmp_path, capsys):
    rom = bytearray(warp_patch.ME_TABLE + 452 * warp_patch.ME_SIZE)
    key = warp_patch.ME_TABLE + 40 * warp_patch.ME_SIZE
    rom[key:key + 2] = b"\x01\x0a"
    record = 0x200
    rom[record + warp_patch.KEY_OFFSET:record + warp_patch.KEY_OFFSET + 2] = b"\x01\x0b"
    path = tmp_path / "copy.gba"
    path.write_bytes(bytes(rom))
    assert warp_patch.main(["--rom", str(path), "--record", hex(record), "--map", "40",
                            "--out", str(tmp_path / "out.gba"), "--check"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["changed_offsets"] == ["0x%06x" % (record + warp_patch.KEY_OFFSET + 1)]
