from __future__ import annotations

import os
import struct
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recomp"))
sys.path.insert(0, os.path.join(ROOT, "tools", "readability"))

import move_entry

BASE = 0x08000000


def image(halfwords):
    return b"".join(struct.pack("<H", word) for word in halfwords)


def tree(tmp_path, files, index_rows, ledger_rows):
    (tmp_path / "asm").mkdir()
    for name, text in files.items():
        (tmp_path / "asm" / name).write_text(text)
    (tmp_path / "asm" / "buu.s").write_text(
        "\tAREA Other, CODE, READONLY\n"
        + "".join("\tINCLUDE %s\n" % name for name in files))
    (tmp_path / "asm" / "rest_of_the_game.s").write_text("\tAREA Rest, CODE, READONLY\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "research").mkdir()
    (tmp_path / "docs" / "research" / "RUNTIME_LABELS.csv").write_text("address,mode\n")
    (tmp_path / "docs" / "ASM_INDEX.csv").write_text(
        "address,kind,symbol,file\n" + "".join(index_rows))
    (tmp_path / "work").mkdir()
    (tmp_path / "work" / "ledger.csv").write_text("".join(ledger_rows))


def test_a_one_function_file_moves_its_start_to_the_entry(tmp_path):
    tree(tmp_path,
         {"sub_08000000.s": "\tCODE16\n|sub_08000000|\n\tPUSH     {r4, lr}\n\tPOP      {r4, pc}\n",
          "sub_08000004.s": "\tCODE16\n|sub_08000004|\n\tLSL      r0, r0, #0\n"
                            "\tPUSH     {r4, lr}\n\tPOP      {r4, pc}\n"},
         ["0x08000000,start,sub_08000000,asm/sub_08000000.s\n",
          "0x08000004,start,sub_08000004,asm/sub_08000004.s\n"],
         ["0x0,4,t,code_a,b,t,p,4\n", "0x4,4,t,code_b,b,t,p,4\n"])
    moves = move_entry.move(str(tmp_path), image([0xB510, 0xBD10, 0x0000, 0xB510, 0xBD10]),
                            [(BASE + 4, BASE + 6)])
    assert [(stop, path) for _address, stop, _new, path, _symbol in moves[0]] == \
        [(BASE + 6, "asm/sub_08000006.s")]
    assert moves[1] == []
    assert tail(tmp_path, "sub_08000000.s") == ["|sub_08000004|", "\tDCW      0x0000"]
    assert head(tmp_path, "sub_08000006.s", 2) == ["\tCODE16", "|sub_08000006|"]
    assert "INCLUDE sub_08000006.s" in (tmp_path / "asm" / "buu.s").read_text()
    assert not (tmp_path / "asm" / "sub_08000004.s").exists()
    assert "0x08000006,start,sub_08000006,asm/sub_08000006.s" in (
        tmp_path / "docs" / "ASM_INDEX.csv").read_text().split("\n")
    assert (tmp_path / "work" / "ledger.csv").read_text().split("\n")[1] == "0x6,2,t,code_b,b,t,p,2"


def test_a_carrier_splits_where_the_entry_starts(tmp_path):
    tree(tmp_path,
         {"sub_08000000.s": "\tCODE16\n|sub_08000000|\n\tPUSH     {r4, lr}\n\tPOP      {r4, pc}\n",
          "sub_08000004.s": "\tCODE16\n|sub_08000004|\n\tPUSH     {r4, lr}\n\tPOP      {r4, pc}\n"
                            "\tLSL      r0, r0, #0\n\tPUSH     {r4, lr}\n\tPOP      {r4, pc}\n"},
         ["0x08000000,start,sub_08000000,asm/sub_08000000.s\n",
          "0x08000004,start,sub_08000004,asm/sub_08000004.s\n",
          "0x08000008,unreferenced,,asm/sub_08000004.s\n"],
         ["0x0,4,t,code_a,b,t,p,4\n", "0x4,4,t,code_b,b,t,p,4\n", "0x8,4,t,code_c,b,t,p,4\n"])
    moves = move_entry.move(str(tmp_path),
                            image([0xB510, 0xBD10, 0xB510, 0xBD10, 0x0000, 0xB510, 0xBD10]),
                            [(BASE + 8, BASE + 10)])
    assert [(stop, path) for _address, stop, _new, path, _symbol in moves[0]] == \
        [(BASE + 10, "asm/sub_0800000A.s")]
    assert moves[1] == []
    assert tail(tmp_path, "sub_08000004.s") == ["|dat_08000008|", "\tDCW      0x0000"]
    assert head(tmp_path, "sub_0800000A.s", 2) == ["|sub_0800000A|", "\tPUSH     {r4, lr}"]
    assert ("\tINCLUDE sub_08000004.s\n\tINCLUDE sub_0800000A.s\n"
            in (tmp_path / "asm" / "buu.s").read_text())
    assert "0xa,2,t,code_c,b,t,p,2" in (tmp_path / "work" / "ledger.csv").read_text().split("\n")


def head(tmp_path, name, count):
    return (tmp_path / "asm" / name).read_text().split("\n")[:count]


def tail(tmp_path, name):
    return [line for line in (tmp_path / "asm" / name).read_text().split("\n") if line][-2:]


def test_a_pair_the_runtime_already_proves_a_start_is_kept(tmp_path):
    tree(tmp_path,
         {"sub_08000000.s": "\tCODE16\n|sub_08000000|\n\tPUSH     {r4, lr}\n\tPOP      {r4, pc}\n",
          "sub_08000004.s": "\tCODE16\n|sub_08000004|\n\tLSL      r0, r0, #0\n"
                            "\tPUSH     {r4, lr}\n\tPOP      {r4, pc}\n"},
         ["0x08000000,start,sub_08000000,asm/sub_08000000.s\n",
          "0x08000004,start,sub_08000004,asm/sub_08000004.s\n"],
         ["0x0,4,t,code_a,b,t,p,4\n", "0x4,6,t,code_b,b,t,p,6\n"])
    (tmp_path / "docs" / "research" / "RUNTIME_LABELS.csv").write_text(
        "address,mode\n0x08000004,thumb\n")
    moves = move_entry.move(str(tmp_path), image([0xB510, 0xBD10, 0x0000, 0xB510, 0xBD10]),
                            [(BASE + 4, BASE + 6)])
    assert moves[0] == []
    assert moves[1] == [(BASE + 4, BASE + 6)]
    assert (tmp_path / "asm" / "sub_08000004.s").exists()
    assert tail(tmp_path, "sub_08000000.s") == ["\tPUSH     {r4, lr}", "\tPOP      {r4, pc}"]


def test_a_prefix_that_would_swallow_a_runtime_entry_stops_at_that_entry():
    assert move_entry.claimed(BASE + 4, BASE + 8, {BASE + 6}) == BASE + 6
    assert move_entry.claimed(BASE + 4, BASE + 8, {BASE + 2}) == BASE + 8
    assert move_entry.claimed(BASE + 4, BASE + 8, set()) == BASE + 8


def test_a_reclaim_takes_the_halfword_back_out_of_the_data_run(tmp_path):
    tree(tmp_path,
         {"sub_08000000.s": "\tCODE16\n|sub_08000000|\n\tPUSH     {r4, lr}\n"
                            "|sub_08000002|\n\tDCW      0x4a00\n",
          "sub_08000004.s": "\tCODE16\n|sub_08000004|\n\tPUSH     {r4, lr}\n\tPOP      {r4, pc}\n"},
         ["0x08000000,start,sub_08000000,asm/sub_08000000.s\n",
          "0x08000004,start,sub_08000004,asm/sub_08000004.s\n"],
         ["0x0,2,t,code_a,b,t,p,2\n", "0x4,4,t,code_b,b,t,p,4\n"])
    target, proof = move_entry.reclaim_one(str(tmp_path),
                                           image([0xB510, 0x4A00, 0xB510, 0xBD10]),
                                           BASE + 4, BASE + 2, {BASE + 2})
    assert proof == "runtime"
    assert target == "asm/sub_08000002.s"
    assert head(tmp_path, "sub_08000002.s", 3)[:2] == ["\tCODE16", "|sub_08000002|"]
    assert head(tmp_path, "sub_08000002.s", 3)[2].startswith("\tLDR")
    assert "pc" in head(tmp_path, "sub_08000002.s", 3)[2]
    assert not (tmp_path / "asm" / "sub_08000004.s").exists()
    assert tail(tmp_path, "sub_08000000.s") == ["\tPUSH     {r4, lr}", "|sub_08000002|"]
    assert "INCLUDE sub_08000002.s" in (tmp_path / "asm" / "buu.s").read_text()
    assert "0x08000002,start,sub_08000002,asm/sub_08000002.s" in (
        tmp_path / "docs" / "ASM_INDEX.csv").read_text().split("\n")
    assert (tmp_path / "work" / "ledger.csv").read_text().split("\n")[1] == "0x2,6,t,code_b,b,t,p,6"


STUB = [0xB510, 0x4A03, 0xB508, 0x6002, 0x2900, 0xD001, 0xF000, 0xF800, 0xBD08, 0x0000, 0x0800]


def stub_tree(tmp_path):
    tree(tmp_path,
         {"sub_08000000.s": "\tCODE16\n|sub_08000000|\n\tPUSH     {r4, lr}\n"
                            "|sub_08000002|\n\tDCW      0x4a03\n",
          "sub_08000004.s": "\tCODE16\n|sub_08000004|\n\tPUSH     {r3, lr}\n"
                            "\tSTR      r2, [r0]\n\tCMP      r1, #0\n"
                            "\tBEQ      |loc_08000010|\n\tBL       |loc_08000000|\n"
                            "|loc_08000010|\n\tPOP      {r3, pc}\n"},
         ["0x08000000,start,sub_08000000,asm/sub_08000000.s\n",
          "0x08000004,start,sub_08000004,asm/sub_08000004.s\n"],
         ["0x0,2,t,code_a,b,t,p,2\n", "0x4,14,t,code_b,b,t,p,14\n"])


def test_a_reclaim_accepts_a_stub_record_the_bytes_prove(tmp_path):
    stub_tree(tmp_path)
    target, proof = move_entry.reclaim_one(str(tmp_path), image(STUB),
                                           BASE + 4, BASE + 2, set())
    assert proof == "shape"
    assert target == "asm/sub_08000002.s"
    assert head(tmp_path, "sub_08000002.s", 3)[:2] == ["\tCODE16", "|sub_08000002|"]
    assert head(tmp_path, "sub_08000002.s", 3)[2].startswith("\tLDR")
    assert not (tmp_path / "asm" / "sub_08000004.s").exists()
    assert "0x2,16,t,code_b,b,t,p,16" in (tmp_path / "work" / "ledger.csv").read_text().split("\n")


def test_a_reclaim_refuses_an_entry_neither_the_runtime_nor_a_stub_proves(tmp_path):
    stub_tree(tmp_path)
    with pytest.raises(SystemExit):
        move_entry.reclaim_one(str(tmp_path), image(STUB), BASE + 4, BASE, set())


def retire_tree(tmp_path, files, index_rows, ledger_rows):
    tree(tmp_path, files, index_rows, ledger_rows)
    (tmp_path / "docs" / "research" / "BF_LABELS.toml").write_text("format = \"gba-labels\"\n")


def test_a_retired_data_start_becomes_a_data_label_in_the_file_before_it(tmp_path):
    retire_tree(tmp_path,
                {"sub_08000000.s": "\tCODE16\n|sub_08000000|\n\tPUSH     {r4, lr}\n"
                                   "\tPOP      {r4, pc}\n",
                 "sub_08000004.s": "\tCODE16\n|sub_08000004|\n\tDCW      0x1234\n"},
                ["0x08000000,start,sub_08000000,asm/sub_08000000.s\n",
                 "0x08000004,start,sub_08000004,asm/sub_08000004.s\n"],
                ["0x0,4,t,code_a,b,t,p,4\n", "0x4,2,t,code_b,b,t,p,2\n"])
    action = move_entry.retire_one(str(tmp_path), image([0xB514, 0xBD14, 0x1234]),
                                   BASE + 4, "data", {BASE: ["prologue"], BASE + 4: []})
    assert action.startswith("data:")
    assert not (tmp_path / "asm" / "sub_08000004.s").exists()
    assert tail(tmp_path, "sub_08000000.s") == ["|dat_08000004|", "\tDCW      0x1234"]
    assert "INCLUDE sub_08000004.s" not in (tmp_path / "asm" / "buu.s").read_text()
    assert "0x08000004" not in (tmp_path / "docs" / "ASM_INDEX.csv").read_text()
    assert (tmp_path / "work" / "ledger.csv").read_text().split("\n")[0] == \
        "0x0,6,t,code_a,b,t,p,4"


def test_a_retired_row_keeps_the_start_after_it_a_code_row(tmp_path):
    retire_tree(tmp_path,
                {"sub_08000000.s": "\tCODE16\n|sub_08000000|\n\tPUSH     {r4, lr}\n"
                                   "\tPOP      {r4, pc}\n\tDCW      0x1111\n"
                                   "\tDCW      0x2222\n\tPUSH     {r4, lr}\n"
                                   "\tPOP      {r4, pc}\n",
                 "sub_08000008.s": ""},
                ["0x08000000,start,sub_08000000,asm/sub_08000000.s\n",
                 "0x08000004,start,,asm/sub_08000000.s\n",
                 "0x08000008,start,sub_08000008,asm/sub_08000008.s\n"],
                ["0x0,4,t,code_a,b,t,p,4\n", "0x4,8,t,code_b,b,t,p,8\n"])
    move_entry.retire_one(str(tmp_path), image([0xB514, 0xBD14, 0x1111, 0x2222, 0xB514, 0xBD14]),
                          BASE + 4, "split", {BASE: ["prologue"], BASE + 8: ["prologue"]})
    body = (tmp_path / "asm" / "sub_08000000.s").read_text().split("\n")
    assert "|dat_08000004|" in body
    assert body[body.index("|dat_08000004|") + 1:][:2] == ["\tDCW      0x1111",
                                                          "\tDCW      0x2222"]
    assert "\tPUSH     {r4, lr}" in body[body.index("|dat_08000004|"):]
    rows = (tmp_path / "work" / "ledger.csv").read_text().split("\n")
    assert rows[0] == "0x0,8,t,code_a,b,t,p,4"
    assert rows[1] == "0x8,4,t,code_b,b,t,p,4"

