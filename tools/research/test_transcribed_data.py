import csv
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "mapcontainer"))

import animrow  # noqa: E402
import transcribed_data as T  # noqa: E402

BASE = 0x08000000
FILES = 16
RUNS = 2496
BYTES = 165961
CLASSES = {"data": (1682, 125527), "pool": (249, 3882), "ptrtable": (1, 4),
           "arm-body": (69, 11096), "thumb-body": (495, 25452)}
THUMB_CENSUS = os.path.join(ROOT, "docs", "research", "THUMB_BODIES.csv")


def converted_rows():
    if not os.path.exists(THUMB_CENSUS):
        return set()
    with open(THUMB_CENSUS, newline="") as handle:
        return {(int(row["start"], 16), int(row["end"], 16))
                for row in csv.DictReader(handle) if row["verdict"] == "thumb-converted"}


def rom_bytes():
    path = os.path.join(ROOT, "baserom.gba")
    if not os.path.exists(path):
        pytest.skip("baserom.gba is absent; run extract.cmd first")
    return open(path, "rb").read()


def symbolic_tables():
    path = os.path.join(ROOT, "docs", "research", "POINTER_ROWS.csv")
    if not os.path.exists(path):
        return []
    with open(path, newline="") as handle:
        return sorted({(int(row["row_start"], 16), int(row["row_end"], 16))
                       for row in csv.DictReader(handle) if row["row_verdict"] == "yes"})


def symbols():
    path = os.path.join(ROOT, "build", "output", "symbols.json")
    if not os.path.exists(path):
        return {}
    return T.load_symbols(path)


def number_tables():
    path = os.path.join(ROOT, "docs", "research", "NUMBER_TABLES.csv")
    if not os.path.exists(path):
        return []
    with open(path, newline="") as handle:
        return sorted({(int(row["start"], 16), int(row["end"], 16))
                       for row in csv.DictReader(handle)})


def written(tmp_path, text, name="buu.s"):
    path = tmp_path / name
    path.write_text(text, encoding="ascii")
    return str(path)


def test_a_runs_label_is_the_label_before_it_and_never_the_one_after_it(tmp_path):
    path = written(tmp_path, "|before_08000000|\n\tDCD\t0x08000000\n|after_08000004|\n\tDCD\t1\n")
    rows = T.runs_of(path)
    assert [row["label"] for row in rows] == ["before_08000000", "after_08000004"]
    assert [row["first"] for row in rows] == [2, 4]


def test_a_run_inside_a_while_body_is_flagged_as_a_fill_body(tmp_path):
    path = written(tmp_path, "|a|\n\tWHILE\tn > 0\n\tDCB\t0xFF\n\tn\tSETA\tn - 1\n\tWEND\n\tDCB\t1\n")
    rows = T.runs_of(path)
    assert [(row["first"], row["loop"]) for row in rows] == [(3, True), (6, False)]


def test_a_statement_and_an_unreadable_operand_each_end_or_void_a_run(tmp_path):
    path = written(tmp_path, "|a|\n\tDCB\t1\n\tCODE16\n\tDCB\t2\n\tDCD\tSYMBOL\n")
    rows = T.runs_of(path)
    assert [(row["first"], row["last"], row["label"], row["ok"]) for row in rows] == [
        (2, 2, "a", True), (4, 5, None, False)]
    assert T.runs_of(path, lambda name: 0x08000000)[1]["ok"] is True


def test_a_quoted_string_counts_its_characters_and_a_symbolic_operand_its_width():
    assert T.operand_bytes("DCB", '"DBZBUUSFURY",0') == b"DBZBUUSFURY\x00"
    assert T.operand_bytes("DCD", "SYM", lambda name: 0x0805622C) == b"\x2c\x62\x05\x08"
    assert T.operand_bytes("DCD", "SYM") is None


def test_a_word_equal_to_a_symbols_address_becomes_that_reference_and_thumb_keeps_its_bit():
    reverse = {0x0801C634: ("sub_0801C634", "|sub_0801C634|")}
    assert T.substitute("0x0801C634", reverse) == ("|sub_0801C634|", 1)
    assert T.substitute("0x0801C635", reverse) == ("|sub_0801C634|+1", 1)
    assert T.substitute("0x00002000", reverse) == ("0x00002000", 0)
    assert T.substitute("0x0801C634,0x00000001", reverse) == ("|sub_0801C634|, 0x00000001", 1)


def test_a_relative_label_operand_reads_as_its_difference():
    line = "\tDCD\t|sub_080298D8|+1-|unk_0804AA94|"
    assert T.emitted.operand_value("|sub_080298D8|+1-|unk_0804AA94|") == 0x080298D9 - 0x0804AA94
    assert T.operand_bytes("DCD", "|sub_080298D8|+1-|unk_0804AA94|") == b"\x45\xee\xfd\xff"
    text = "|unk_0804AA94|\n%s\n" % line
    assert T.emitted.labeled_bytes(text) == [(0x4AA94, b"\x45\xee\xfd\xff")]
    assert T.emitted.operand_value("|nameless|+1-|unk_0804AA94|") is None
    assert T.operand_bytes("DCD", "SYM") is None


def animation_tables(rom):
    return sorted((start, start + length) for start, length in animrow.free(rom).items())


def test_the_frozen_tree_keeps_only_pools_pointer_tables_and_the_fill_body_as_text():
    if symbols():
        pytest.importorskip("capstone")
    rom = rom_bytes()
    runs, totals = T.measured(rom, ROOT, symbols().get, symbols())
    rows = [run for run, _, _ in runs]
    converted = (sorted(converted_rows()) + symbolic_tables() + number_tables()
                 + animation_tables(rom))
    survivors = [run for run, kind, _ in runs if kind == "data"
                 and not any(start <= run.start and run.end <= end for start, end in converted)]
    assert [len(run.data) for run in survivors] == [1] and survivors[0].loop, \
        "a `data` run outside a converted row survived the conversion: %s" \
        % [(run.file, run.first, len(run.data)) for run in survivors]
    for run in rows:
        assert rom[run.start:run.end] == run.data, "%s:%d" % (run.file, run.first)
    ordered = sorted(rows, key=lambda run: run.start)
    assert not [1 for left, right in zip(ordered, ordered[1:]) if right.start < left.end]
    loops = [run for run in rows if run.loop]
    assert [(run.file, len(run.data), run.data) for run in loops] == [
        ("rest_of_the_game.s", 1, b"\xff")], "the fill body is the loop exception, not a run"


def test_the_frozen_csv_places_the_two_runs_that_share_a_byte_string():
    with open(os.path.join(ROOT, "docs", "research", "TRANSCRIBED_DATA_RUNS.csv"), newline="") as fh:
        rows = {(row["file"], int(row["line_first"])): row for row in csv.DictReader(fh)}
    assert int(rows[("buu.s", 12391)]["rom_start"], 16) == 0x03D77C
    assert int(rows[("GBARam.s", 375)]["rom_start"], 16) == 0x03D730


def test_the_committed_csv_carries_the_measurement_and_the_tree_carries_its_data_rows():
    path = os.path.join(ROOT, "docs", "research", "TRANSCRIBED_DATA_RUNS.csv")
    assert os.path.exists(path), "the classification CSV is not committed"
    with open(path, newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == RUNS
    assert len({(row["file"], row["line_first"]) for row in rows}) == RUNS
    totals = {}
    for row in rows:
        totals[row["class"]] = totals.get(row["class"], 0) + int(row["bytes"])
    assert totals == {kind: count[1] for kind, count in CLASSES.items()}
    assert sum(totals.values()) == BYTES
    loop = [row for row in rows if "loop=fill" in row["evidence"]]
    assert [(row["file"], int(row["line_first"])) for row in loop] == [
        ("rest_of_the_game.s", 14066)]
    wanted = {(int(row["rom_start"], 16), int(row["rom_end"], 16))
              for row in rows if row["class"] == "data" and "loop=fill" not in row["evidence"]}
    named = set()
    for name in sorted(os.listdir(os.path.join(ROOT, "asm"))):
        if not name.endswith(".s"):
            continue
        text = "\n".join(T.lines_of(os.path.join(ROOT, "asm", name)))
        for token in T.emitted.incbin_tokens(text):
            found = T.emitted.SLICE.search(token.replace("\\", "/"))
            if found:
                named.add((int(found.group(1), 16), int(found.group(2), 16)))
    carried = named | converted_rows() | set(symbolic_tables()) | set(number_tables()) | fills()
    uncovered = [row for row in wanted if not covers(carried, row)]
    assert not uncovered, "a data row the conversion did not carry: %s" % sorted(uncovered)


def fills():
    import fill_promote

    out = set()
    directory = os.path.join(ROOT, "asm")
    for name in sorted(os.listdir(directory)):
        found = re.match(r"fill_([0-9a-f]+)\.s$", name)
        if not found:
            continue
        length = len(fill_promote.read_back(open(os.path.join(directory, name)).read()))
        start = int(found.group(1), 16)
        out.add((start, start + length))
    return out


def covers(named, row):
    cursor, end = row
    for start, stop in sorted(named):
        if stop <= cursor:
            continue
        if start > cursor:
            return False
        cursor = max(cursor, stop)
        if cursor >= end:
            return True
    return cursor >= end
