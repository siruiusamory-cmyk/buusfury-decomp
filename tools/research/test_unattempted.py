from __future__ import annotations

import os
import struct
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _path in (HERE, ROOT, os.path.join(ROOT, "tools")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import unattempted  # noqa: E402

BASE = 0x08000000


def ledger_row(start, end, status="in progress", attempts="GRAPHICS-RESIDUAL-002:null"):
    return {"start": start, "end": end, "bytes": end - start, "region": "R00",
            "status": status, "attempts": attempts}


POPULATION_CASES = (
    ("exact", [{"start": 0x10, "end": 0x18, "bytes": 8, "region": "R00"}], (1, 8),
     {"R00": (1, 8)}, None),
    ("one row short", [], (1, 8), {"R00": (1, 8)}, "not 1 / 8"),
    ("one byte short", [{"start": 0x10, "end": 0x17, "bytes": 7, "region": "R00"}], (1, 8),
     {"R00": (1, 8)}, "not 1 / 8"),
    ("region split moved", [{"start": 0x10, "end": 0x18, "bytes": 8, "region": "R01"}], (1, 8),
     {"R00": (1, 8)}, "region split"),
    ("same span twice", [{"start": 0x10, "end": 0x18, "bytes": 8, "region": "R00"},
                         {"start": 0x10, "end": 0x18, "bytes": 8, "region": "R00"}], (2, 16),
     {"R00": (2, 16)}, "twice"),
)


@pytest.mark.parametrize("name,rows,expected,regions,error", POPULATION_CASES)
def test_assert_population(name, rows, expected, regions, error):
    if error is None:
        assert unattempted.assert_population(rows, expected, regions) is None
    else:
        with pytest.raises(SystemExit, match=error):
            unattempted.assert_population(rows, expected, regions)


LEDGER = [ledger_row(0x00, 0x10, "identified binary", "END-ROM-RECON-001:no-format-beats-null"),
          ledger_row(0x10, 0x20, "unmapped", "none"),
          ledger_row(0x20, 0x28, "unmapped", "none"),
          ledger_row(0x28, 0x40),
          ledger_row(0x50, 0x60, "runtime-pending", "citations_in_source:no-code-site")]


def test_neighbours_skips_the_population_and_flags_adjacency():
    rows = [{"start": 0x10, "end": 0x20, "bytes": 0x10, "region": "R00"},
            {"start": 0x20, "end": 0x28, "bytes": 8, "region": "R00"}]
    sides = unattempted.neighbours(LEDGER, rows)
    previous, following = sides[(0x10, 0x20)]
    assert (previous["start"], previous["status"], previous["adjacent"]) == (
        0x00, "identified binary", True)
    assert (following["start"], following["status"], following["adjacent"]) == (
        0x28, "in progress", False)
    previous, following = sides[(0x20, 0x28)]
    assert (previous["start"], previous["adjacent"]) == (0x00, False)
    assert (following["start"], following["status"], following["adjacent"]) == (
        0x28, "in progress", True)
    assert (following["attempts"], following["bytes"]) == ("GRAPHICS-RESIDUAL-002:null", 0x18)


NEIGHBOUR_CASES = (
    ("adjacent on the side below", 0x10, 0x00, True, 0x20, False),
    ("adjacent on the side above", 0x18, 0x00, False, 0x20, True),
    ("nothing above", 0x70, 0x60, True, None, False),
)


@pytest.mark.parametrize("name,start,previous,previous_adjacent,following,following_adjacent",
                         NEIGHBOUR_CASES)
def test_neighbours_edges(name, start, previous, previous_adjacent, following,
                          following_adjacent):
    ledger = [ledger_row(0x00, 0x10, "identified binary"),
              ledger_row(0x20, 0x28, "unmapped", "none"),
              ledger_row(0x60, 0x70, "runtime-pending")]
    rows = [{"start": start, "end": start + 8, "bytes": 8, "region": "R00"}]
    got_previous, got_following = unattempted.neighbours(ledger, rows)[(start, start + 8)]
    assert (got_previous["start"] if got_previous else None) == previous
    assert bool(got_previous and got_previous["adjacent"]) is previous_adjacent
    assert (got_following["start"] if got_following else None) == following
    assert bool(got_following and got_following["adjacent"]) is following_adjacent


def synthetic_rom():
    rom = bytearray(0x40)
    struct.pack_into("<I", rom, 0x04, BASE + 0x20)
    struct.pack_into("<I", rom, 0x08, BASE + 0x21)
    struct.pack_into("<I", rom, 0x0C, 0x12345678)
    struct.pack_into("<I", rom, 0x24, BASE + 0x24)
    return bytes(rom)


WORD_CASES = (
    ("both sites name the row", [(0x20, 0x30)], 16, 3, [(0x04, BASE + 0x20),
                                                       (0x08, BASE + 0x21)]),
    ("a span the words do not name", [(0x30, 0x38)], 16, 3, []),
)


@pytest.mark.parametrize("name,spans,words,addresses,expected", WORD_CASES)
def test_word_index(name, spans, words, addresses, expected):
    hits, got_words, got_addresses = unattempted.word_index(synthetic_rom(), spans)
    assert got_words == words
    assert got_addresses == addresses
    assert hits.get(spans[0], []) == sorted(expected)


POINTER_CASES = (
    ("two addresses", [(0x00, BASE), (0x04, BASE + 0x8)], True),
    ("one address", [(0x00, BASE), (0x04, 0x12345678)], False),
    ("one word", [(0x00, BASE)], False),
)


@pytest.mark.parametrize("name,words,expected", POINTER_CASES)
def test_pointer_table(name, words, expected):
    rom = bytearray(0x10)
    for offset, value in words:
        struct.pack_into("<I", rom, offset, value)
    span = (0x00, 4 * len(words))
    assert unattempted.pointer_table(bytes(rom), span) is expected


STRIDE_CASES = (
    ("two 8-byte records", 0x10, 8, 8, 2),
    ("four 4-byte records", 0x10, 4, 4, 4),
    ("one record is not a table", 0x04, 0, 4, 0),
    ("a leader that is not an address", 0x08, 0, 4, 0),
)


@pytest.mark.parametrize("name,length,stride,written,records", STRIDE_CASES)
def test_stride_of(name, length, stride, written, records):
    rom = bytearray(0x20)
    for at in range(0, length, written):
        struct.pack_into("<I", rom, at, 0 if name.startswith("a leader") else BASE + at)
    assert unattempted.stride_of(bytes(rom), (0x00, length)) == (stride, records)


TOKEN_CASES = (
    ("nothing fires", {}, "no-entry"),
    ("a converted branch", {"entry": "converted"}, "converted"),
    ("shape only", {"walk_returns": True}, "no-entry;walk-returns"),
    ("named and shaped", {"walk_returns": True, "words": True}, "no-entry;walk-returns;word-named"),
    ("a container", {"container": True, "jcalg1": True}, "no-entry;container;jcalg1"),
    ("a record table", {"text_class": "record table"}, "no-entry;text-record-table"),
)


def entry_of(**flags):
    entry = {field: False for field in unattempted.FLAGS}
    entry.update({"entry": "none", "words": 0, "text_class": "unknown"})
    for name, value in flags.items():
        if name == "words":
            entry["words"] = 1 if value else 0
        elif name == "text_class":
            entry["text_class"] = value
        else:
            entry[name] = value
    return entry


@pytest.mark.parametrize("name,flags,expected", TOKEN_CASES)
def test_result_token(name, flags, expected):
    assert unattempted.result_token(entry_of(**flags)) == expected


def test_csv_text_pins_the_header_and_the_cells():
    entry = {field: "" for field in unattempted.FIELDS}
    entry.update({"start": 0x00FC38, "end": 0x00FC88, "bytes": 80, "region": "R32",
                  "region_name": "first-MiB code band", "prev_start": 0x00FC16,
                  "prev_bytes": 32, "prev_status": "unmapped", "prev_attempts": "none",
                  "prev_adjacent": True, "next_start": None, "next_bytes": 0,
                  "next_status": "", "next_attempts": "", "next_adjacent": False,
                  "code_site": "code:0x0800F938", "words": 3, "word_site": "0x004B04=0x0874CA24",
                  "converted": True, "walk_returns": False, "stride": "20/53",
                  "text_class": "unknown", "block": "", "result": "converted"})
    text = unattempted.csv_text([entry])
    lines = text.splitlines()
    assert lines[0].split(",") == list(unattempted.FIELDS)
    cells = lines[1].split(",")
    assert cells[unattempted.FIELDS.index("start")] == "0x00fc38"
    assert cells[unattempted.FIELDS.index("prev_start")] == "0x00fc16"
    assert cells[unattempted.FIELDS.index("next_start")] == ""
    assert cells[unattempted.FIELDS.index("prev_adjacent")] == "yes"
    assert cells[unattempted.FIELDS.index("converted")] == "yes"
    assert cells[unattempted.FIELDS.index("walk_returns")] == "no"


def test_permuted_is_deterministic_and_changes_only_the_row():
    rom = bytes(range(0x40))
    once = unattempted.permuted(rom, (0x10, 0x18))
    twice = unattempted.permuted(rom, (0x10, 0x18))
    assert once == twice
    assert once[:0x10] == rom[:0x10] and once[0x18:] == rom[0x18:]
    assert once[0x10:0x18] != rom[0x10:0x18]


CHECK_ROWS = ("start,end,bytes,region,code_site\n0x10,0x18,8,R00,\n0x18,0x20,8,R00,\n")
CHECK_LEDGER = ("start,end,bytes,region,route,references,consumer,attempts,status\n"
                "0x10,0x18,8,R00,NONE,none,none,UNATTEMPTED-001:no-entry,unmapped\n"
                "{tail}")


@pytest.mark.parametrize("name,second,ok", (
    ("both rows carry the token", "0x18,0x20,8,R00,NONE,none,none,UNATTEMPTED-001:no-entry,"
     "unmapped\n", True),
    ("a row left at none", "0x18,0x20,8,R00,NONE,none,none,none,unmapped\n", False),
    ("a converted row is gone", "", True),
))
def test_check_reads_the_tracked_table(tmp_path, name, second, ok):
    table = tmp_path / "rows.csv"
    table.write_text(CHECK_ROWS, encoding="ascii")
    ledger = tmp_path / "ledger.csv"
    ledger.write_text(CHECK_LEDGER.format(tail=second), encoding="ascii")
    assert unattempted.check(str(table), str(ledger), (2, 16)) is ok
