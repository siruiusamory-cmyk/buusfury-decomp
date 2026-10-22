from __future__ import annotations

import contextlib
import io
import os
import shutil
import sys
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gate


def in_scratch(call):
    root = tempfile.mkdtemp(prefix="gate-test-")
    previous_root = gate.ROOT
    previous_cache = os.environ.get("BUUSFURY_ENCODE_CACHE")
    os.environ["BUUSFURY_ENCODE_CACHE"] = os.path.join(root, "encode-cache")
    gate.ROOT = root
    try:
        return call(root)
    finally:
        gate.ROOT = previous_root
        if previous_cache is None:
            os.environ.pop("BUUSFURY_ENCODE_CACHE", None)
        else:
            os.environ["BUUSFURY_ENCODE_CACHE"] = previous_cache
        shutil.rmtree(root, ignore_errors=True)


def made(root, name, content=b"x"):
    path = os.path.join(root, *name.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(content)
    return path


def log_of(rows, rewritten=0):
    path = os.path.join(tempfile.mkdtemp(prefix="gate-log-"), "rebuild.log")
    with open(path, "w", encoding="utf-8") as handle:
        for spawns, hits, misses, trusted, total in rows:
            if spawns is not None:
                handle.write("oracle spawns=%d cache hits=%d misses=%d\n" % (spawns, hits, misses))
            handle.write("encode_cache_misses=%d trusted=%d total=%d\n" % (misses, trusted, total))
        if rewritten:
            handle.write("files rewritten=%d skipped=0\n" % rewritten)
    return path


COLD = ((None, None, 187, 0, 187), (3918, 0, 3918, 1, 3918), (7390, 0, 7390, 1, 7390),
        (None, None, 925, 1, 925), (355, 72, 355, 1, 427))
WARM_STORE = ((None, None, 0, 1, 187), (0, 3918, 0, 1, 3918), (0, 7390, 0, 1, 7390),
              (None, None, 0, 1, 925), (0, 427, 0, 1, 427))
MANIFEST_PATH = ((None, None, 187, 0, 187), (None, None, 0, 1, 3918), (None, None, 0, 1, 7390),
                 (None, None, 0, 1, 925), (None, None, 0, 1, 427))
ONE_BLOCK = ((None, None, 0, 1, 187), (0, 3918, 0, 1, 3918), (7390, 0, 7390, 1, 7390),
             (None, None, 0, 1, 925), (0, 427, 0, 1, 427))


def test_a_cold_run_accounts_for_every_member_and_the_duplicate_block_is_not_a_shortfall():
    assert sum(row[2] for row in COLD) == 12775
    assert sum(row[4] for row in COLD) == 12847
    assert gate.cold_shortfall(COLD) is None
    assert gate.stage_of(log_of(COLD))[0] == "cold"


def test_an_oracle_emitter_is_full_by_spawns_plus_hits_not_by_misses_over_total():
    endrom = COLD[-1]
    assert endrom == (355, 72, 355, 1, 427)
    assert endrom[0] + endrom[1] == endrom[4] != endrom[2]
    assert gate.cold_shortfall(COLD) is None


def test_cold_promotion_copies_an_absent_entry_and_never_overwrites_one():
    def check(root):
        shared = os.path.join(root, "shared")
        os.makedirs(shared)
        made(root, "build/cold-cache/%s.bin" % ("a" * 64), b"isolated")
        made(root, "build/cold-cache/%s.bin" % ("c" * 64), b"fresh")
        made(root, "build/cold-cache/encoder.sha256", b"stamp")
        made(root, "shared/%s.bin" % ("a" * 64), b"existing")
        made(root, "shared/encoder.sha256", b"stale")
        copied, skipped = gate.cold_promote(shared)
        read = lambda name: open(os.path.join(shared, name), "rb").read()  # noqa: E731
        return (copied, skipped, read("a" * 64 + ".bin"), read("c" * 64 + ".bin"),
                read("encoder.sha256"), [n for n in os.listdir(shared) if ".promote-" in n],
                gate.cold_promote(gate.cold_cache_dir()))
    copied, skipped, kept, promoted, stamp, leftovers, self_target = in_scratch(check)
    assert (copied, skipped) == (2, 1)
    assert kept == b"existing" and promoted == b"fresh" and stamp == b"stamp"
    assert leftovers == [] and self_target == (0, 0)


def test_a_purged_cache_that_served_or_skipped_is_never_cold():
    assert gate.cold_shortfall(MANIFEST_PATH) is not None
    assert gate.stage_of(log_of(MANIFEST_PATH))[0] == "partial"


DEFECT = """manifest path: payload sizes and mtimes unchanged, encoder trusted, every section file present
sections=1973 generated=987 carve-out=0 retail=986 incbin_lines=1973
oracle spawns=0 cache hits=0 misses=0 files rewritten=1973 skipped=0
encode_cache_misses=0 trusted=1 total=0
spritecontainer_gen_exit=0
"""
ENCODED = """sections=1973 generated=987 carve-out=0 retail=986 incbin_lines=1973
oracle spawns=7390 cache hits=0 misses=7390 files rewritten=1973 skipped=0
encode_cache_misses=7390 trusted=1 total=7390
spritecontainer_gen_exit=0
"""
MANIFEST = """manifest path: payload sizes and mtimes unchanged, encoder trusted, every section file present
sections=1973 generated=987 carve-out=0 retail=986 incbin_lines=1973
oracle spawns=0 cache hits=0 misses=0 files rewritten=0 skipped=1973
encode_cache_misses=0 trusted=1 total=7390
spritecontainer_gen_exit=0
"""


def written_log(text):
    path = os.path.join(tempfile.mkdtemp(prefix="gate-log-"), "rebuild.log")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


RECORD_ONLY = """sections=5 generated=4 carve-out=0 retail=1 incbin_lines=5 containers=0 records=4
oracle spawns=0 cache hits=0 misses=0 files rewritten=5 skipped=0
encode_cache_misses=0 trusted=1 total=0
spritedefs_gen_exit=0
"""


def test_a_record_only_emitter_is_not_a_shortfall_and_its_row_is_the_cold_reports_shape():
    rows = gate.emitter_rows(written_log(RECORD_ONLY))
    assert rows == [(0, 0, 0, 1, 0, 0)]
    assert gate.cold_shortfall(rows) is None
    assert gate.generated_shortfall(gate.emitter_report(written_log(RECORD_ONLY))) is None
    for spawns, hits, misses, trusted, total, *_ in rows:
        assert (spawns, hits, misses, trusted, total) == (0, 0, 0, 1, 0)


def test_an_emitter_that_wrote_generated_runs_must_report_an_encode_population():
    blocks = gate.emitter_report(written_log(DEFECT))
    assert blocks == [{"generated": 987, "manifest": True, "spawns": 0, "hits": 0, "misses": 0,
                       "trusted": 1, "total": 0, "name": "spritecontainer_gen"}]
    assert gate.generated_shortfall(blocks) == \
        "spritecontainer_gen wrote generated=987 yet reports an encode population of 0"


def test_an_emitter_with_a_population_of_generated_runs_passes():
    assert gate.generated_shortfall(gate.emitter_report(written_log(ENCODED))) is None
    assert gate.generated_shortfall(gate.emitter_report(written_log(MANIFEST))) is None
    assert gate.generated_shortfall([{"generated": 0, "total": 0, "name": "x"}]) is None


def test_a_warm_store_is_not_cold():
    assert gate.cold_shortfall(WARM_STORE) is not None
    assert gate.stage_of(log_of(WARM_STORE))[0] == "warm"
    assert gate.stage_of(log_of(WARM_STORE, rewritten=4730))[0] == "materialise"


def test_the_stage_rule_cases():
    assert gate.classify(COLD, 5000) == "cold"
    edit = ((1, 186, 1, 1, 187),) + WARM_STORE[1:]
    assert gate.classify(edit, 2) == "edit"
    assert gate.classify(ONE_BLOCK, 1973) == "partial"
    assert gate.classify((), 0) == "partial"


def test_cold_start_isolates_the_cache_purges_and_runs_the_extract_step():
    def check(root):
        made(root, "baserom.gba_0x158_0x143f2.extracted")
        made(root, "build/endrom/emitted.json")
        made(root, "assets/endrom/payloads.store")
        step = made(root, "cold-step.cmd", b"@echo off\r\nexit /b 0\r\n")
        previous = gate.EXTRACT
        gate.EXTRACT = step
        try:
            rc = gate.cold_start()
        finally:
            gate.EXTRACT = previous
        return rc, gate.cold_cache_dir(), {
            "cache_env": os.environ.get("BUUSFURY_ENCODE_CACHE"),
            "slice": os.path.exists(os.path.join(root, "baserom.gba_0x158_0x143f2.extracted")),
            "section": os.path.exists(os.path.join(root, "build", "endrom")),
            "store": os.path.exists(os.path.join(root, "assets", "endrom", "payloads.store")),
        }
    rc, cache, state = in_scratch(check)
    assert rc == 0
    assert cache.endswith(os.path.join("build", "cold-cache"))
    assert state["cache_env"] == cache
    assert state["slice"] is False and state["section"] is False
    assert state["store"] is True


def test_the_purge_leaves_the_emission_input_and_the_extract_inputs():
    kept = ("build/output/ROM_START", "build/bg.pal", "build/asset_intro.compressed",
            "assets/mapcontainer/payloads.store", "assets/tilebank/payloads.store")

    def check(root):
        for name in kept:
            made(root, name)
        removed = gate.cold_purge()
        return removed, [name for name in kept
                         if os.path.exists(os.path.join(root, *name.split("/")))]
    removed, survivors = in_scratch(check)
    assert removed == 0
    assert survivors == list(kept)


def test_the_purge_names_every_block_the_build_writes():
    import emit_all
    out_dirs, out_files = set(), set()
    for _name, argv in emit_all.STEPS:
        for flag, value in zip(argv, argv[1:]):
            if flag == "--out-dir":
                out_dirs.add(os.path.basename(value.replace("\\", "/")))
            elif flag == "--out":
                out_files.add(os.path.basename(value.replace("\\", "/")))
    assert out_dirs == set(gate.COLD_DERIVATIONS)
    assert out_files == {gate.COLD_OUTPUT, gate.COLD_STRINGS, *gate.COLD_RECORDS}


def test_the_cold_procedure_runs_the_extract_script():
    assert gate.EXTRACT == os.path.join(gate.ROOT, "extract.cmd")


def test_an_anti_flake_retry_keeps_the_first_runs_stage():
    calls = []

    def fake_rebuild(quiet=False):
        calls.append(1)
        fake_rebuild.seconds = 999.0
        return 0

    def fake_stage(path, label=None):
        return label or ("cold" if len(calls) == 1 else "warm"), len(calls)

    previous = gate.rebuild, gate.stage_of
    gate.rebuild, gate.stage_of = fake_rebuild, fake_stage
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            rc, timing_ok = gate.rebuild_and_time()
    finally:
        gate.rebuild, gate.stage_of = previous
    printed = out.getvalue()
    assert rc == 0 and timing_ok is False
    assert printed.count("TIMING cold") == 2 and "warm" not in printed


def test_a_cold_run_is_measured_once_and_not_retried():
    calls = []

    def fake_rebuild(quiet=False):
        calls.append(1)
        fake_rebuild.seconds = 999.0
        return 0

    def fake_stage(path, label=None):
        return "cold", 12775

    previous = gate.rebuild, gate.stage_of
    gate.rebuild, gate.stage_of = fake_rebuild, fake_stage
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            rc, timing_ok = gate.rebuild_and_time(retry=False)
    finally:
        gate.rebuild, gate.stage_of = previous
    printed = out.getvalue()
    assert rc == 0 and timing_ok is False and len(calls) == 1
    assert printed.count("TIMING cold") == 1 and "anti-flake" not in printed


def test_a_failed_tools_lowercase_error_line_reaches_the_gate_summary():
    text = "@echo off\r\necho Fatal error: L6031U: Could not open scatter description file\r\n" \
           "exit /b 1\r\n"

    def check(root):
        step = made(root, "failing-build.cmd", text.encode())
        previous = gate.BUILD, gate.LOG, gate.IMAGE
        gate.BUILD, gate.LOG = step, os.path.join(root, "rebuild.log")
        gate.IMAGE = os.path.join(root, "no-such-image")
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                rc = gate.rebuild()
        finally:
            gate.BUILD, gate.LOG, gate.IMAGE = previous
        return rc, out.getvalue()
    rc, printed = in_scratch(check)
    assert rc == 1
    assert "Fatal error: L6031U" in printed


def walk(image, retail, rows, slices):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        ok, total, insn, data = gate.ledger_walk(image, retail, rows, slices)
    return ok, total, insn, data, out.getvalue().splitlines()


def ledger_row(off, length, insn=0):
    return (off, length, "thumb", "region", "asm/x.s", "generated", "byte-proven", insn)


def test_a_byte_equal_ledger_is_green_and_the_walk_ignores_a_slice_that_ends_before_it():
    retail = bytes(range(64))
    ok, total, insn, data, lines = walk(retail, retail, [ledger_row(0, 8), ledger_row(16, 8)], [(12, 4)])
    assert (ok, total, insn, data) == (True, 16, 0, 16)
    assert all(line.endswith("BYTE-EQUAL byte-proven") for line in lines)


def test_a_changed_image_byte_fails_the_walk_and_names_the_row():
    retail = bytes(range(64))
    image = bytearray(retail)
    image[9] ^= 0xFF
    ok, total, _, _, lines = walk(bytes(image), retail, [ledger_row(0, 8), ledger_row(8, 8)], [])
    assert ok is False and total == 16
    assert lines[0].endswith("BYTE-EQUAL byte-proven") and lines[1].endswith("MISMATCH")


def test_a_row_still_inside_an_incbin_slice_fails_the_walk_and_names_the_slice():
    retail = bytes(range(64))
    ok, _, _, _, lines = walk(retail, retail, [ledger_row(0, 8), ledger_row(16, 8)], [(12, 8)])
    assert ok is False
    assert lines[0].endswith("BYTE-EQUAL byte-proven") and lines[1].endswith("STILL INCBIN at 0xc")


def test_the_running_max_end_names_the_same_first_covering_slice_as_the_exhaustive_scan():
    cases = ([(0, 4), (4, 4), (8, 4)], [(0, 20), (4, 4), (24, 4)], [(0, 4), (0, 8), (10, 2)],
             [(2, 100), (3, 1), (200, 5)], [(0, 8388608)], [])
    for slices in cases:
        for off in range(0, 30):
            for length in (1, 4, 8, 16):
                exhaustive = [s for s, l in slices if s < off + length and off < s + l]
                _, _, _, _, lines = walk(bytes(off + length), bytes(off + length),
                                         [ledger_row(off, length)], slices)
                assert ("STILL INCBIN" not in lines[0]) == (not exhaustive), (slices, off, length)
                if exhaustive:
                    assert lines[0].endswith("STILL INCBIN at 0x%x" % exhaustive[0])


LEDGER_ROWS = [(0x158, 120, "thumb", "code_158_143F2", "asm/buu.s", "transcription",
                "byte-proven", 120),
               (0x1C62C, 8, "arm", "sub_0801C62C", "src/sub_0801C62C.c", "c", "c-matched", 8),
               (0x400, 16, "data", "an_unledgered_name", "asm/x.s", "extracted", "byte-proven", 0)]


def ledger_round_trip(rows):
    root = tempfile.mkdtemp(prefix="ledger-test-")
    path = os.path.join(root, "ledger.csv")
    try:
        gate.write_ledger(rows, path)
        return gate.ledger_rows(path)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_the_ledger_format_round_trips_old_rows_to_the_same_rows():
    assert gate.ledger_line(LEDGER_ROWS[0]) == "0x158,120,t,code_158_143F2,b,t,p,120\n"
    assert ledger_round_trip(LEDGER_ROWS) == LEDGER_ROWS


def test_the_round_trip_is_red_on_a_lossy_table():
    words = gate.LEDGER_CODES[5]
    gate.LEDGER_CODES[5] = dict(words, c="t")
    try:
        lossy = ledger_round_trip([LEDGER_ROWS[1]])
    finally:
        gate.LEDGER_CODES[5] = words
    assert lossy != [LEDGER_ROWS[1]] and lossy[0][5] == "transcription"


def test_a_literal_equal_to_a_reserved_code_round_trips_unchanged():
    codes = sorted({code for table in gate.LEDGER_CODES.values() for code in table.values()})
    rows = [(0x100, 2, "thumb", "region", code, "transcription", "byte-proven", 0)
            for code in codes]
    assert ledger_round_trip(rows) == rows
    for row in rows:
        assert gate.LEDGER_ESCAPE + row[4] in gate.ledger_line(row)


def test_a_literal_that_starts_with_the_escape_round_trips_unchanged():
    rows = [(0x100, 2, "thumb", "region", gate.LEDGER_ESCAPE + "b", "transcription",
             "byte-proven", 0)]
    assert ledger_round_trip(rows) == rows


def test_the_tracked_ledger_re_encodes_to_itself():
    path = os.path.join(gate.ROOT, "work", "ledger.csv")
    with open(path, encoding="ascii", newline="") as handle:
        before = handle.read()
    assert "".join(gate.ledger_line(row) for row in gate.ledger_rows(path)) == before


def test_the_source_count_is_positive_attribution():
    raw = sum(length for _start, length in gate.incbin_ranges())
    copies = sum(length for _start, length in gate.identity_ranges())
    covered = sum(length for _start, length in
                  gate.union_ranges(gate.incbin_ranges() + gate.identity_ranges()))
    assert gate.source_bytes() == gate.ROM_SIZE - covered
    assert raw + copies + gate.source_bytes() == gate.ROM_SIZE
    assert gate.source_bytes() == 7893334


def test_a_double_counted_interval_is_refused_instead_of_passing_as_arithmetic(monkeypatch):
    monkeypatch.setattr(gate, "incbin_ranges", lambda: [(0x1000, 0x20)])
    monkeypatch.setattr(gate, "identity_ranges", lambda: [(0x1010, 0x10)])
    with pytest.raises(SystemExit) as error:
        gate.source_bytes()
    message = str(error.value)
    assert "INCBIN" in message and "identity" in message and "overlaps" in message, message


def test_an_interval_outside_the_image_is_refused(monkeypatch):
    monkeypatch.setattr(gate, "incbin_ranges", lambda: [(gate.ROM_SIZE - 8, 0x10)])
    monkeypatch.setattr(gate, "identity_ranges", lambda: [])
    with pytest.raises(SystemExit) as error:
        gate.source_bytes()
    assert "outside" in str(error.value), str(error.value)


def test_the_accounted_class_totals_are_the_image_and_a_perturbed_one_fails():
    raw = sum(length for _start, length in gate.incbin_ranges())
    copies = sum(length for _start, length in gate.identity_ranges())
    source = gate.source_bytes()
    assert gate.accounted(raw, copies, source) == (gate.ROM_SIZE, None)
    total, problem = gate.accounted(raw + 2, copies, source)
    assert total == gate.ROM_SIZE + 2 and problem is not None, problem


def test_the_transcribed_line_carries_the_ledger_walks_total(monkeypatch, tmp_path):
    image = tmp_path / "image.gba"
    image.write_bytes(bytes(gate.ROM_SIZE))
    monkeypatch.setattr(gate, "IMAGE", str(image))
    monkeypatch.setattr(gate, "RETAIL", str(image))
    monkeypatch.setattr(gate.lints, "run", lambda: [])
    monkeypatch.setattr(gate, "rebuild_and_time", lambda **keywords: (0, True))
    monkeypatch.setattr(gate, "emitter_report", lambda path: [])
    monkeypatch.setattr(gate, "ledger_rows", lambda path=None: [])
    monkeypatch.setattr(gate, "ledger_walk", lambda *arguments: (True, 1234567, 11, 22))
    monkeypatch.setattr(gate, "incbin_ranges", lambda: [(0x10, 0x20)])
    monkeypatch.setattr(gate, "identity_ranges", lambda: [])
    monkeypatch.setattr(gate, "extract_sites", lambda root=None: [])
    monkeypatch.setattr(gate, "missing_slices", lambda: [])
    monkeypatch.setattr(gate, "tracked_rom_slices", lambda retail: [])
    monkeypatch.setattr(gate, "raw_classes", lambda: (0x20, 0, 0, 0))
    monkeypatch.setattr(gate, "fill_run", lambda image: (0, 0))
    monkeypatch.setattr(gate, "strings_class", lambda: ("codec", 0))
    monkeypatch.setattr(gate, "accounted", lambda raw, copies, source: (424242, None))
    monkeypatch.setattr(gate.sys, "argv", ["gate.py"])
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        gate.main()
    lines = [line for line in out.getvalue().splitlines()
             if line.startswith("transcribed by ledger=")]
    assert lines == ["transcribed by ledger=1234567 of which instruction bytes=11 data bytes=22"]


def test_no_tracked_file_carries_game_text():
    sys.path.insert(0, os.path.join(gate.ROOT, "tools", "text"))
    import strings_table
    assert strings_table.tracked_text_hits(gate.ROOT) == []


def test_identity_copies_are_measured_ranges_not_a_constant():
    sys.path.insert(0, os.path.join(gate.ROOT, "tools", "mapcontainer"))
    import assetdir
    import assetdir2
    measured = sum(end - start for _name, start, end in gate.extract_sites())
    assert sum(length for _start, length in gate.union_ranges(gate.identity_ranges())) == measured
    assert (assetdir2.BLOCK_START, assetdir2.BLOCK_BYTES) not in gate.identity_ranges()
    assert [r for r in gate.identity_ranges()
            if r[0] < assetdir.BLOCK_END and assetdir.BLOCK_START < r[0] + r[1]] == []


if __name__ == "__main__":
    test_a_cold_run_accounts_for_every_member_and_the_duplicate_block_is_not_a_shortfall()
    test_an_oracle_emitter_is_full_by_spawns_plus_hits_not_by_misses_over_total()
    test_cold_promotion_copies_an_absent_entry_and_never_overwrites_one()
    test_a_purged_cache_that_served_or_skipped_is_never_cold()
    test_a_warm_store_is_not_cold()
    test_the_stage_rule_cases()
    test_cold_start_isolates_the_cache_purges_and_runs_the_extract_step()
    test_the_purge_leaves_the_emission_input_and_the_extract_inputs()
    test_the_purge_names_every_block_the_build_writes()
    test_the_cold_procedure_runs_the_extract_script()
    test_an_anti_flake_retry_keeps_the_first_runs_stage()
    test_a_cold_run_is_measured_once_and_not_retried()
    test_a_failed_tools_lowercase_error_line_reaches_the_gate_summary()
    test_a_byte_equal_ledger_is_green_and_the_walk_ignores_a_slice_that_ends_before_it()
    test_a_changed_image_byte_fails_the_walk_and_names_the_row()
    test_a_row_still_inside_an_incbin_slice_fails_the_walk_and_names_the_slice()
    test_the_running_max_end_names_the_same_first_covering_slice_as_the_exhaustive_scan()
    test_the_ledger_format_round_trips_old_rows_to_the_same_rows()
    test_the_round_trip_is_red_on_a_lossy_table()
    test_a_literal_equal_to_a_reserved_code_round_trips_unchanged()
    test_a_literal_that_starts_with_the_escape_round_trips_unchanged()
    test_the_tracked_ledger_re_encodes_to_itself()
    test_the_source_count_is_positive_attribution()
    test_no_tracked_file_carries_game_text()
    test_identity_copies_are_measured_ranges_not_a_constant()
    print("PASS test_gate")
