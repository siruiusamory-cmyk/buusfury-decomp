from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "structured"))

import opcode_stream
import pytest

ROM = opcode_stream.read_rom(os.path.join(opcode_stream.ROOT, "baserom.gba"))
CARRIER = os.path.join(opcode_stream.ROOT, "asm", "rawlabeled_71c90.s")


def test_the_interpreter_and_every_handler_are_the_retail_halfwords():
    opcode_stream.pinned(ROM)


def test_the_rows_are_the_map_entry_script_field():
    table = opcode_stream.census(ROM)
    fields = [entry.fields[21] for _offset, entry in opcode_stream.families.map_entries(ROM)
              if opcode_stream.ROM_BASE <= entry.fields[21] < opcode_stream.ROM_BASE + len(ROM)]
    assert (len(fields), len(set(fields))) == (167, 132)
    assert {value - opcode_stream.ROM_BASE for value in fields} == \
        {row["start"] for row in table}
    assert (len(table), sum(row["bytes"] for row in table)) == (132, 14857)


def test_the_counts_are_the_measured_split():
    counts = opcode_stream.totals(opcode_stream.census(ROM))
    assert (counts["moved_rows"], counts["moved_bytes"]) == (34, 1004)
    assert (counts["stayed_rows"], counts["stayed_bytes"]) == (98, 13853)
    assert counts["moved_bytes"] + counts["stayed_bytes"] == counts["bytes"] == 14857


def test_every_moved_row_re_emits_its_bytes():
    for row in opcode_stream.census(ROM):
        if not row["moved"]:
            assert row["stream"] < row["bytes"]
            continue
        assert row["stream"] == row["bytes"]
        assert opcode_stream.encode(row["decoded"]) == ROM[row["start"]:row["end"]]


def test_the_carrier_names_each_row_the_census_says():
    text = open(CARRIER, errors="replace").read()
    for row in opcode_stream.census(ROM):
        if row["moved"]:
            token = "build\\opcode\\gen_%06x_%06x.bin" % (row["start"], row["end"])
            assert token in text
        else:
            token = "baserom.gba_0x%x_0x%x.extracted" % (row["start"], row["end"])
            assert token in text


def test_a_changed_opcode_byte_is_refused():
    body = bytearray(ROM)
    row = next(row for row in opcode_stream.census(ROM) if row["moved"])
    body[row["start"]] = 0x1F
    decoded = opcode_stream.decode(bytes(body), row["start"], row["end"])
    assert decoded["bad"] or decoded["missing"]
    with pytest.raises(SystemExit):
        opcode_stream.encode(decoded)


def test_a_stream_that_ends_early_states_its_stop():
    table = {row["start"]: row for row in opcode_stream.census(ROM)}
    row = table[0x072974]
    assert (row["bytes"], row["stream"], row["moved"]) == (60, 9, False)
    assert ROM[row["start"] + 8] == opcode_stream.END


def test_the_page_is_the_census_this_tool_derives():
    assert opcode_stream.check(ROM) == 0
