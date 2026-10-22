from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import thumb_bodies  # noqa: E402
import thumb_body_convert as convert  # noqa: E402

ROW = (0, 0x10)


def image(*halves):
    out = bytearray(b"\x00" * 0x20)
    for index, value in enumerate(halves):
        struct.pack_into("<H", out, index * 2, value)
    return bytes(out)


def walk(halves, entries=((0, "branch", "test", "tier1"),), row=ROW):
    original = thumb_bodies.ROM
    thumb_bodies.ROM = image(*halves)
    try:
        body = thumb_bodies.walk(row, list(entries))
    finally:
        thumb_bodies.ROM = original
    return body


def test_a_conditional_branch_walks_both_arms_and_a_pool_word_is_a_pool():
    body = walk((0x2803, 0xD000, 0x2001, 0x4901, 0xB002, 0xBD00, 0x1234, 0x0800))
    assert sorted(body.code) == [0, 2, 4, 6, 8, 10], body.code
    assert sorted(body.pool) == [0x0C], body.pool
    assert body.stops == []
    assert body.walked == 12
    assert body.pool_bytes == 4
    assert body.left == 16 - 12 - 4


def test_the_walk_stops_at_an_unconditional_exit_and_not_before_it():
    body = walk((0x2001, 0xBD00, 0x2002, 0x2003))
    assert sorted(body.code) == [0, 2], body.code
    assert body.stops == []


def test_a_pop_that_loads_pc_is_an_exit_and_a_bx_is_a_target_not_a_stop():
    body = walk((0x4778, 0x2001))
    assert sorted(body.code) == [0], body.code
    assert body.stops == []


def test_an_undecodable_halfword_stops_the_walk():
    body = walk((0x2001, 0xFFFF, 0x2002))
    assert sorted(body.code) == [0], body.code
    assert body.stops and body.stops[0][0] == 2


def test_an_instruction_crossing_the_row_end_is_not_code_and_its_target_is_recorded():
    body = walk((0xF000, 0xF800, 0x2001), row=(0, 2))
    assert body.code == {}
    assert body.stops and body.stops[0][0] == 0
    assert body.targets == {0x08000004}, body.targets


def test_a_branch_out_of_the_row_is_a_target_and_not_a_walk():
    body = walk((0xE000, 0x2001), row=(0, 2))
    assert body.code == {0: (2, "b", "#0x8000004")}
    assert body.targets == {0x08000004}


def test_a_transitive_entry_walks_from_its_own_offset_inside_the_row():
    body = walk((0x2001, 0x2002), row=(0, 4), entries=((2, "walk", "chain", "chain"),))
    assert sorted(body.code) == [2], body.code
    assert body.kind == "entry"


def test_direct_target_reads_only_a_direct_branch():
    assert thumb_bodies.direct_target("beq", "#0x80004f8") == 0x080004F8
    assert thumb_bodies.direct_target("bl", "#0x80004f8") == 0x080004F8
    assert thumb_bodies.direct_target("bx", "lr") is None
    assert thumb_bodies.direct_target("ldr", "r0, [pc, #4]") is None


def test_loads_pc_covers_the_arms_a_thumb_body_can_leave_by():
    assert thumb_bodies.loads_pc("bx", "lr")
    assert thumb_bodies.loads_pc("pop", "{r3, pc}")
    assert thumb_bodies.loads_pc("ldm", "r0!, {r1, pc}")
    assert thumb_bodies.loads_pc("mov", "pc, lr")
    assert not thumb_bodies.loads_pc("pop", "{r3}")
    assert not thumb_bodies.loads_pc("add", "sp, #8")


def test_a_row_lookup_is_half_open_at_both_ends():
    index = thumb_bodies.Rows([(0x10, 0x20), (0x30, 0x40)])
    assert index.of(0x10) == (0x10, 0x20)
    assert index.of(0x1F) == (0x10, 0x20)
    assert index.of(0x20) is None
    assert index.of(0x30) == (0x30, 0x40)
    assert index.of(0x0F) is None


def test_the_spelling_forms_the_assembler_measured():
    assert convert.plain_candidates("muls", "r1, r3, r1")[0] == "MUL r1, r3"
    assert convert.plain_candidates("rsbs", "r1, r2, #0")[0] == "NEG r1, r2"
    assert convert.plain_candidates("ldm", "r2, {r1}")[0] == "LDMIA r2!, {r1}"
    assert convert.plain_candidates("adds", "r3, sp, r3")[0] == "ADD r3, sp"
    assert convert.plain_candidates("movs", "r0, r0")[0] == "LSL r0, r0, #0"
    assert convert.plain_candidates("svc", "#6")[0] == "SWI 6"
    assert convert.plain_candidates("beq", "#0x8000000") == []
    assert convert.plain_candidates("dcd", "pool word") == []


def test_a_four_byte_word_at_a_halfword_address_becomes_two_halfwords():
    assert convert.word_lines(0, 2, 0xD006) == ["\tDCW     0xD006"]
    assert convert.word_lines(4, 4, 0xFA7AF03B) == ["\tDCD     0xFA7AF03B"]
    assert convert.word_lines(2, 4, 0xFA7AF03B) == ["\tDCW     0xF03B", "\tDCW     0xFA7A"]
    assert convert.word_lines(2, 2, 0xE7F1, "reason") == ["\tDCW     0xE7F1\t; reason"]


def test_a_spelling_class_keeps_the_registers_and_drops_the_immediates():
    assert convert.shape_of("adds", "r1, r2, #0x10") == convert.shape_of("adds", "r1, r2, #4")
    assert convert.shape_of("adds", "r1, r2, #4") != convert.shape_of("adds", "r3, r2, #4")


def test_a_rows_csv_names_the_universe_a_conversion_may_touch(tmp_path):
    path = tmp_path / "class.csv"
    path.write_text("file,start,end,class\na.s,0x10,0x20,code-without-entry\n"
                    "b.s,0x4,0x8,code-without-entry\n", encoding="ascii")
    assert convert.read_rows(str(path)) == [(0x4, 0x8), (0x10, 0x20)]


def test_a_converted_rows_own_incbin_call_is_dropped_and_a_new_gap_one_added(
        tmp_path, monkeypatch):
    path = tmp_path / "rebuild.cmd"
    path.write_text("@echo off\ncall tools\\incbin.bat baserom.gba 0x10 0x20\n"
                    "call tools\\incbin.bat baserom.gba 0x40 0x50\necho done\n", encoding="ascii",
                    newline="\n")
    monkeypatch.setattr(convert, "ROOT", str(tmp_path))
    monkeypatch.setattr(convert, "sources_of", lambda: ({"a.s": [(0x10, 0x20)]}, {}))
    added, dropped = convert.sync_rebuild([(0x20, 0x30)], write=True)
    assert added == ["call tools\\incbin.bat baserom.gba 0x20 0x30"]
    assert dropped == ["call tools\\incbin.bat baserom.gba 0x40 0x50"]
    assert path.read_text(encoding="ascii").splitlines() == [
        "@echo off", "call tools\\incbin.bat baserom.gba 0x10 0x20",
        "call tools\\incbin.bat baserom.gba 0x20 0x30", "echo done"]


def test_full_items_tile_the_whole_row_and_mark_the_gaps():
    original = thumb_bodies.ROM
    thumb_bodies.ROM = image(0x2001, 0xBD00, 0x2002, 0x2003, 0x2004, 0xBD00, 0x1234, 0x0800)
    try:
        body = thumb_bodies.walk(ROW, [(0, "branch", "test", "tier1"),
                                       (8, "walk", "second", "tier1")])
        items = convert.full_items(body)
    finally:
        thumb_bodies.ROM = original
    cursor = ROW[0]
    for offset, size, _m, _o, _v, _gap in items:
        assert offset == cursor, (hex(offset), hex(cursor))
        cursor = offset + size
    assert cursor == ROW[1]
    assert sorted(body.code) == [0, 2, 8, 10]
    assert [offset for offset, _s, _m, _o, _v, gap in items if gap] == [4, 6, 12, 14]


def test_method_sites_reads_the_engines_base_relative_convention():
    blob = bytearray(0x20)
    struct.pack_into("<i", blob, 0x04, 7)
    struct.pack_into("<i", blob, 0x08, 4)
    struct.pack_into("<i", blob, 0x14, -9)
    struct.pack_into("<i", blob, 0x18, 0x7FFFFF00)
    assert thumb_bodies.method_sites(blob, [(0, 0x10), (0x10, 0x1C)]) == [(0, 0x04, 0x06),
                                                                          (0x10, 0x14, 0x06)]


def test_a_method_target_enters_a_row_and_merges_with_the_source_entries(monkeypatch):
    original = thumb_bodies.ROM
    thumb_bodies.ROM = image(0x4770, 0x4770)
    monkeypatch.setattr(thumb_bodies, "source_rows", lambda: [])
    monkeypatch.setattr(thumb_bodies, "method_entries",
                        lambda spans: {ROW: [(2, "method", "method table", "method")]})
    try:
        assert thumb_bodies.entries([ROW]) == {}
        found = thumb_bodies.entries([ROW], method=True)
    finally:
        thumb_bodies.ROM = original
    assert found == {ROW: [(2, "method", "method table", "method")]}

