from __future__ import annotations

import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import testkit

import export_inputs

CRT0 = """\tmov         r1, #0x0
\tldr         r1, hardware_conf_2
\tstr         r1, [r0, #0xD4]
\tldr         r1, hardware_conf_3
\tstr         r1, [r0, #0xD8]
\tldr         r1, hardware_conf_4
\tmovs        r1, r1, lsr #2
\torr         r1, r1, #0x84, 8
\tstrne       r1, [r0, #0xDC]

hardware_conf_2\t\tDCD\t\t0x087B79A4
hardware_conf_3\t\tDCD\t\t0x03000000
hardware_conf_4\t\tDCD\t\t0x00001007
"""

IWRAM = """\tAREA data, DATA

IWRAM_1
\tSPACE 0x1004
IWRAM_2_start
\tSPACE 0x2484
FreeListTail
\tSPACE 0x04
IWRAM_2_end
\tSPACE 0x1E70
IWRAM_3
\tSPACE 0x2d04
\tEND
"""

HEADER = """\tAREA Head, CODE, READONLY
\tENTRY
\t\tB         \tInit
"""


def a_root(root, iwram=IWRAM, ledger="", asm="", header=HEADER):
    for name, text in (("asm/crt0.s", CRT0), ("asm/iwram.s", iwram), ("asm/rom_header.s", header),
                       ("work/ledger.csv", ledger), ("asm/buu.s", asm)):
        path = os.path.join(root, *name.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="ascii", newline="\n") as handle:
            handle.write(text)


def a_census(root, text):
    path = os.path.join(root, *export_inputs.CENSUS.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="ascii", newline="\n") as handle:
        handle.write(text)


def test_the_copy_length_is_the_crt0_count_word_and_the_iwram_block(tmp_path):
    a_root(str(tmp_path))
    found, blocks = export_inputs.copies(str(tmp_path))
    assert found == [(0x03000000, 0x087B79A4, 0x1004)]
    assert sum(blocks) == 0x8000
    assert export_inputs.entry_address(str(tmp_path)) == 0x08000000


def test_an_iwram_block_that_disagrees_with_the_count_word_is_refused(tmp_path):
    a_root(str(tmp_path), iwram=IWRAM.replace("SPACE 0x1004", "SPACE 0x1000"))
    with pytest.raises(SystemExit) as refused:
        export_inputs.copies(str(tmp_path))
    assert "reserves 0x1000 B" in str(refused.value)


def test_a_label_at_a_code_row_is_a_function_and_the_others_are_entries(tmp_path):
    ledger = ("0x100,4,thumb,code_a,b,t,p,4\n"
              "0x104,8,thumb,code_b,b,t,p,8\n"
              "0x10c,4,data,dat_a,b,t,p,4\n")
    asm = ("\tCODE16\n"
           "\tEXPORT |sub_08000100|\n"
           "|sub_08000100|\n"
           "\tEXPORT |sub_08000102|\n"
           "\tEXPORT |sub_08000104|\n"
           "\tCODE32\n"
           "\tEXPORT |sub_0800010c|\n")
    census = ("address,kind,limb,parent\n"
              "0x08000100,start,block,\n"
              "0x08000102,block,,0x08000100\n"
              "0x08000104,start,prologue,\n")
    a_root(str(tmp_path), ledger=ledger, asm=asm)
    a_census(str(tmp_path), census)
    rows = export_inputs.code_rows(str(tmp_path))
    names = export_inputs.labels(str(tmp_path))
    assert export_inputs.functions(rows, names) == [
        (0x100, 4, "thumb", "sub_08000100"),
        (0x104, 8, "thumb", "sub_08000104")]
    assert export_inputs.entries(rows, names) == [(0x102, "thumb"), (0x10C, "arm")]


def test_a_crafted_relabel_moves_no_address_out_of_the_export(tmp_path):
    ledger = ("0x100,4,thumb,code_a,b,t,p,4\n"
              "0x104,8,thumb,code_b,b,t,p,8\n")
    census = ("address,kind,limb,parent\n"
              "0x08000100,start,block,\n"
              "0x08000104,start,prologue,\n"
              "0x08000106,block,,0x08000104\n")
    spelled = ("\tCODE16\n"
               "\tEXPORT |sub_08000100|\n"
               "|sub_08000100|\n"
               "\tEXPORT |sub_08000104|\n"
               "\tEXPORT |%s_08000106|\n")
    a_root(str(tmp_path), ledger=ledger, asm=spelled % "sub")
    a_census(str(tmp_path), census)
    before = export_inputs.census_entries(str(tmp_path))
    names = export_inputs.labels(str(tmp_path))
    assert 0x106 in [off for off, _name in names.items()]
    a_root(str(tmp_path), ledger=ledger, asm=spelled % "loc")
    after = export_inputs.census_entries(str(tmp_path))
    assert 0x106 not in export_inputs.labels(str(tmp_path))
    assert before == after
    assert 0x106 in [off for off, _kind in after]


def test_a_promoted_name_is_a_label_at_the_address_the_ledger_gives_it(tmp_path):
    ledger = ("0x100,4,thumb,code_a,b,t,p,4\n"
              "0x104,8,thumb,code_b,b,t,p,8\n")
    asm = ("\tCODE16\n"
           "\tEXPORT |sub_08000100|\n"
           "|sub_08000100|\n"
           "\tEXPORT |KeyInput_Read|\n"
           "\tEXPORT |Unknown_Thing|\n")
    a_root(str(tmp_path), ledger=ledger, asm=asm)
    path = os.path.join(str(tmp_path), "docs", "NAMING_LEDGER.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("address,old,new,evidence_class,evidence\n"
                     "0x08000104,sub_08000104,KeyInput_Read,hardware-register,none\n")
    assert export_inputs.labels(str(tmp_path)) == {0x100: ("sub_08000100", "thumb"),
                                                   0x104: ("KeyInput_Read", "thumb")}


def test_the_tracked_export_is_the_one_the_tree_derives():
    testkit.require(os.path.join(export_inputs.ROOT, "baserom.gba"),
                    "no image, so the identity block cannot be re-derived")
    assert export_inputs.main(["--check"]) == 0


def a_dispatch_pair(image):
    for at, half in ((0x100, 0x4C07), (0x102, 0x447C), (0x104, 0x4D07), (0x106, 0x447D),
                     (0x108, 0x42A5), (0x10A, 0x3C04)):
        image[at:at + 2] = half.to_bytes(2, "little")
    image[0x120:0x124] = (0x200 - 0x106).to_bytes(4, "little")
    image[0x124:0x128] = (0x208 - 0x10A).to_bytes(4, "little")
    image[0x200:0x204] = (0x301 - 0x200).to_bytes(4, "little")
    image[0x204:0x208] = (0x311 - 0x204).to_bytes(4, "little")
    return bytes(image)


def test_the_seeded_pair_gives_the_table_its_count_and_its_stride():
    assert export_inputs.jump_tables(a_dispatch_pair(bytearray(0x400))) == [(0x200, 4, 2)]


def test_a_veneer_word_inside_the_copy_is_an_arm_entry():
    image = bytearray(0x200)
    image[0x40:0x48] = export_inputs.VENEER
    image[0x48:0x4C] = (0x03000040).to_bytes(4, "little")
    found = export_inputs.copy_entries(bytes(image), [], [(0x03000000, 0x08000000, 0x1004)])
    assert found == [(0x03000040, "arm")]


def a_thumb_image(cells, pointers):
    image = bytearray(0x400)
    for at, half in cells:
        image[at:at + 2] = half.to_bytes(2, "little")
    for at, value in pointers:
        image[at:at + 4] = value.to_bytes(4, "little")
    return bytes(image)


def test_a_pointer_into_a_branching_body_is_an_entry():
    image = a_thumb_image(((0x100, 0x2800), (0x102, 0xD102), (0x104, 0x4770),
                           (0x10A, 0x4770)), ((0x300, 0x08000101),))
    bounds = {0x100: "thumb", 0x102: "thumb", 0x104: "thumb", 0x10A: "thumb"}
    _words, raw, accepted = export_inputs.address_taken(image, bounds, [], [], [])
    assert raw == {0x100: "thumb"}
    assert accepted == {0x100: "thumb"}


def test_a_pointer_into_a_leaf_without_a_caller_is_not_an_entry():
    image = a_thumb_image(((0x120, 0x4770),), ((0x300, 0x08000121),))
    _words, raw, accepted = export_inputs.address_taken(
        image, {0x120: "thumb"}, [], [], [])
    assert raw == {0x120: "thumb"}
    assert accepted == {}


def test_a_leaf_that_a_call_names_is_an_entry():
    image = a_thumb_image(((0x100, 0xF000), (0x102, 0xF80E), (0x104, 0x4770),
                           (0x120, 0x4770)), ((0x300, 0x08000121),))
    bounds = {0x100: "thumb", 0x104: "thumb", 0x120: "thumb"}
    _words, raw, accepted = export_inputs.address_taken(
        image, bounds, [(0x100, 4, "thumb")], [], [])
    assert raw == {0x120: "thumb"}
    assert accepted == {0x120: "thumb"}


def test_a_pointer_that_is_not_an_instruction_boundary_is_not_a_candidate():
    image = a_thumb_image(((0x100, 0x4770),), ((0x300, 0x08000103),))
    _words, raw, accepted = export_inputs.address_taken(image, {0x100: "thumb"}, [], [], [])
    assert raw == {}
    assert accepted == {}


def test_a_branch_that_leaves_the_walked_boundaries_rejects_the_entry():
    image = a_thumb_image(((0x100, 0x2800), (0x102, 0xD17D)), ((0x300, 0x08000101),))
    _words, raw, accepted = export_inputs.address_taken(
        image, {0x100: "thumb", 0x102: "thumb"}, [], [], [])
    assert raw == {0x100: "thumb"}
    assert accepted == {}


def test_every_entry_has_a_mode_and_a_covering_row():
    text = open(export_inputs.OUT, encoding="ascii", newline="").read()
    code = [(int(addr, 16) - export_inputs.ENTRY_PC, int(size), mode)
            for addr, mode, size in re.findall(
                r'\[\[code\]\]\naddr = 0x([0-9a-fA-F]+)\nmode = "(\w+)"\nsize = (\d+)', text)]
    copies = [(int(addr, 16), 0, int(size, 16)) for addr, size in re.findall(
        r'\[\[code_copy\]\]\nruntime_start = 0x([0-9a-fA-F]+)\nsource_start = 0x[0-9a-fA-F]+'
        r'\nsize = 0x([0-9a-fA-F]+)', text)]
    entries = [(int(addr, 16), mode) for addr, mode in re.findall(
        r'\[\[entry\]\]\naddr = 0x([0-9a-fA-F]+)\nmode = "(\w*)"', text)]
    tagged = {int(addr, 16) for addr in re.findall(
        r'\[\[entry\]\]\naddr = 0x([0-9a-fA-F]+)\nmode = "\w+"\nclass = "runtime"', text)}
    assert entries
    for addr, mode in entries:
        assert mode in export_inputs.CODE
        assert addr in tagged or export_inputs.covered(addr, mode, code, copies)


def test_a_runtime_label_off_a_walked_boundary_is_refused():
    labels = [(0x08000100, "thumb"), (0x08000102, "thumb"), (0x08000105, "thumb")]
    assert export_inputs.runtime_entries({0x100: "thumb"}, {}, labels) == [(0x08000100, "thumb")]


def test_the_copy_source_gives_boundaries_at_its_run_address():
    image = bytearray(0x400)
    image[0x100:0x108] = bytes.fromhex("1eff2fe1") * 2
    bounds = export_inputs.copy_bounds(bytes(image), [(0x03000000, 0x08000100, 8)])
    assert bounds == {0x03000000: "arm", 0x03000004: "arm"}
    labels = [(0x03000000, "arm"), (0x03000002, "arm")]
    assert export_inputs.runtime_entries({}, bounds, labels) == [(0x03000000, "arm")]


def test_a_thunk_walks_into_arm_at_the_next_word():
    image = bytearray(0x200)
    image[0x100:0x108] = export_inputs.VENEER
    image[0x108:0x10C] = bytes.fromhex("1eff2fe1")
    rows = export_inputs.veneer_rows(bytes(image))
    assert rows == [(0x100, 8, "thumb")]
    bounds, _starts = export_inputs.walk(bytes(image), rows)
    assert bounds[0x104] == "arm"
    assert export_inputs.runtime_entries(bounds, {}, [(0x08000104, "arm")]) == [(0x08000104, "arm")]


def test_the_export_carries_every_tracked_runtime_label():
    text = open(export_inputs.OUT, encoding="ascii", newline="").read()
    tagged = {(int(addr, 16), mode) for addr, mode in re.findall(
        r'\[\[entry\]\]\naddr = 0x([0-9a-fA-F]+)\nmode = "(\w+)"\nclass = "runtime"', text)}
    code = {int(addr, 16) for addr in re.findall(r'\[\[code\]\]\naddr = 0x([0-9a-fA-F]+)', text)}
    wanted = export_inputs.runtime_labels()
    assert wanted and tagged
    assert tagged <= set(wanted)
    assert not [(addr, mode) for addr, mode in wanted
                if addr not in code and (addr, mode) not in tagged]

