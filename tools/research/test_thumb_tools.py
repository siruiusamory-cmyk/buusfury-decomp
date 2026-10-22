from __future__ import annotations

import builtins
import csv
import io
import json
import os
import struct
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))

if os.path.exists(os.path.join(ROOT, "baserom.gba")):
    import thumb_bodies  # noqa: E402
else:
    _open = builtins.open

    def _empty(path, *args, **kwargs):
        if os.path.abspath(str(path)) == os.path.join(ROOT, "baserom.gba"):
            return io.BytesIO(b"")
        return _open(path, *args, **kwargs)

    builtins.open = _empty
    try:
        import thumb_bodies  # noqa: E402
    finally:
        builtins.open = _open
    thumb_bodies.ROM = b""

import arm_bodies  # noqa: E402
import thumb_annotate  # noqa: E402
import thumb_body_convert as convert  # noqa: E402


def image(*halves, size=0x100):
    out = bytearray(size)
    for index, value in enumerate(halves):
        struct.pack_into("<H", out, index * 2, value)
    return bytes(out)


def image_at(pairs, size=0x100):
    out = bytearray(size)
    for offset, value in pairs.items():
        struct.pack_into("<H", out, offset, value)
    return bytes(out)


def patched(monkeypatch, data):
    monkeypatch.setattr(thumb_bodies, "ROM", data)
    monkeypatch.setattr(arm_bodies, "ROM", data)


SOURCE = (0x00, 0x20, "thumb", 0x20)
CODE_ROW = (0x20, 0x30)
TARGET_ROW = (0x30, 0x34)


def decoded(HALFWORDS, offset):
    original = thumb_bodies.ROM
    thumb_bodies.ROM = HALFWORDS
    try:
        return thumb_bodies.decode(offset)
    finally:
        thumb_bodies.ROM = original


def planted_branch(image, offset, operand):
    got = decoded(image, offset)
    assert got is not None and got[1] == "b" and got[2] == operand, (got, operand)
    return got[2]


def entry_scan(monkeypatch, data, rows, source):
    monkeypatch.setattr(thumb_bodies, "rows", lambda: list(rows))
    monkeypatch.setattr(thumb_bodies, "source_rows", lambda: list(source))
    patched(monkeypatch, data)
    return thumb_bodies.entries()


def test_a_thumb_branch_in_source_makes_its_target_row_an_entry(monkeypatch):
    data = image(0xE00E)
    operands = planted_branch(data, 0, "#0x8000020")
    found = entry_scan(monkeypatch, data, [CODE_ROW], [SOURCE])
    assert found == {CODE_ROW: [(0x20, "branch", "Thumb 0x08000000 b %s" % operands, "tier1")]}, found


def test_an_arm_mode_source_span_makes_no_entry(monkeypatch):
    data = image(0xE00E)
    planted_branch(data, 0, "#0x8000020")
    assert entry_scan(monkeypatch, data, [CODE_ROW], [(0x00, 0x20, "arm", 0x20)]) == {}


def test_a_branch_target_outside_every_row_makes_no_entry(monkeypatch):
    data = image(0xE01F)
    planted_branch(data, 0, "#0x8000042")
    assert entry_scan(monkeypatch, data, [CODE_ROW], [SOURCE]) == {}


def test_a_defined_16_bit_instruction_and_a_pop_pc_are_decoded(monkeypatch):
    patched(monkeypatch, image(0x2001, 0xBD00))
    assert thumb_bodies.decode(0) == (2, "movs", "r0, #1")
    assert thumb_bodies.decode(2) == (2, "pop", "{pc}")


def test_a_16_bit_pattern_armv4t_does_not_define_is_not_decoded(monkeypatch):
    patched(monkeypatch, image(0xBF00, 0xBE00, 0x2001))
    assert thumb_bodies.decode(0) is None
    assert thumb_bodies.decode(2) is None
    assert thumb_bodies.decode(4) == (2, "movs", "r0, #1")


def test_a_32_bit_decode_that_is_not_bl_is_not_decoded(monkeypatch):
    patched(monkeypatch, image(0xF000, 0xB800, 0xF000, 0xF800))
    assert thumb_bodies.decode(0) is None
    assert thumb_bodies.decode(4) == (4, "bl", "#0x8000008")


def test_a_partially_converted_tree_is_refused_before_anything_is_walked():
    with pytest.raises(SystemExit) as raised:
        thumb_bodies.refuse_overlap([(0x00, 0x10), (0x08, 0x20)])
    assert "overlap" in str(raised.value)
    assert thumb_bodies.refuse_overlap([(0x00, 0x10), (0x20, 0x30)]) is None


def test_the_scan_resumes_after_a_halfword_the_cpu_cannot_decode(monkeypatch):
    patched(monkeypatch, image(0x2001, 0xFFFF, 0x2002))
    assert list(thumb_bodies.thumb_instructions(0, 6)) == [(0, (2, "movs", "r0, #1")),
                                                            (4, (2, "movs", "r0, #2"))]


def test_a_synthetic_body_counts_its_walked_bytes_its_pool_and_what_is_left():
    body = thumb_bodies.Body((0, 0x20), "entry")
    body.code = {0: (2, "movs", "r0, #1"), 8: (2, "add", "r0, #1")}
    body.pool = {0x10}
    assert body.walked == 4
    assert body.pool_bytes == 4
    assert body.left == 0x20 - 4 - 4
    assert min(body.code_bytes()) == 0
    assert max(body.code_bytes()) == 0x13


def test_a_literal_the_walk_also_executed_is_not_a_pool_word(monkeypatch):
    patched(monkeypatch, image_at({0x00: 0x4903, 0x0C: 0x2003}))
    body = thumb_bodies.walk((0, 0x10), [(0, "branch", "test", "tier1")])
    assert body.code[0] == (2, "ldr", "r1, [pc, #0xc]")
    assert body.code[0x0C] == (2, "movs", "r0, #3")
    assert body.pool == set()


def test_a_row_the_manifest_carries_reports_the_manifest_state(monkeypatch, tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"rows": [{"start": 0x20, "end": 0x30,
                                          "entry_site": "Thumb 0x08000000 b",
                                          "walked_bytes": 12, "pool_bytes": 4,
                                          "verdict": "thumb-converted"}]}))
    monkeypatch.setattr(thumb_bodies, "MANIFEST", str(path))
    assert thumb_bodies.row_state((0x20, 0x30)) == ("Thumb 0x08000000 b", 12, 4, 0,
                                                    "thumb-converted")
    assert thumb_bodies.row_state((0x30, 0x34)) == ("", 0, 0, 4, "")


def test_a_row_absent_from_every_manifest_reports_nothing_walked(monkeypatch, tmp_path):
    monkeypatch.setattr(thumb_bodies, "MANIFEST", str(tmp_path / "absent.json"))
    assert thumb_bodies.row_state((0x20, 0x30)) == ("", 0, 0, 0x10, "")


def test_the_census_writes_one_row_per_frozen_row_through_csv(monkeypatch, tmp_path):
    site = "Thumb 0x08000000 ldr r0, [pc, #0x1f0]"
    monkeypatch.setattr(thumb_bodies, "frozen_rows",
                        lambda: {(0x20, 0x30): {"file": "asm/buu.s", "verdict": "arm-code"}})
    monkeypatch.setattr(thumb_bodies, "tracked", lambda: {})
    monkeypatch.setattr(thumb_bodies, "cached",
                        lambda: {(0x20, 0x30): {"verdict": "thumb-converted", "detail": "",
                                                "walked_bytes": 8, "pool_bytes": 4,
                                                "entry_site": site, "kind": "entry"}})
    monkeypatch.setattr(thumb_bodies, "closure", lambda: {})
    monkeypatch.setattr(thumb_bodies, "site_tiers", lambda: {})
    out = tmp_path / "docs" / "research" / "THUMB_BODIES.csv"
    thumb_bodies.census(str(out), out=io.StringIO())
    with open(out, newline="") as handle:
        rows = list(csv.reader(handle))
    header = ("start", "end", "bytes", "file", "arm_verdict", "walk_kind", "entry_site",
              "entry_kind", "entry_tier", "walked_bytes", "pool_bytes", "left_incbin_bytes",
              "verdict", "detail")
    assert rows[0] == list(header)
    assert len(rows) == 2
    assert all(len(row) == len(header) for row in rows)
    assert rows[1][6] == site
    assert rows[1][11] == "4"
    assert rows[1][12] == "thumb-converted"


def test_a_partial_manifest_cannot_erase_the_verdict_the_census_already_carries(monkeypatch,
                                                                                tmp_path):
    header = ("start,end,bytes,file,arm_verdict,walk_kind,entry_site,entry_kind,entry_tier,"
              "walked_bytes,pool_bytes,left_incbin_bytes,verdict,detail\n")
    carried = tmp_path / "tracked.csv"
    carried.write_text(header + "0x20,0x30,16,asm/buu.s,arm-code,entry,Thumb 0x08000020 b,"
                       "branch,tier1,8,4,4,thumb-converted,\n", encoding="ascii")
    monkeypatch.setattr(thumb_bodies, "CENSUS_THUMB", str(carried))
    monkeypatch.setattr(thumb_bodies, "MANIFEST", str(tmp_path / "absent.json"))
    assert thumb_bodies.record()[(0x20, 0x30)]["verdict"] == "thumb-converted"
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"rows": [{"start": 0x40, "end": 0x48,
                                              "verdict": "thumb-not-code", "detail": "",
                                              "walked_bytes": 0, "pool_bytes": 0,
                                              "entry_site": "", "kind": "entry",
                                              "file": "asm/buu.s"}]}), encoding="ascii")
    monkeypatch.setattr(thumb_bodies, "MANIFEST", str(manifest))
    assert sorted(thumb_bodies.record()) == [(0x20, 0x30), (0x40, 0x48)]


def test_the_census_lists_a_converted_row_the_frozen_census_never_carried(monkeypatch, tmp_path):
    monkeypatch.setattr(thumb_bodies, "frozen_rows", lambda: {})
    monkeypatch.setattr(thumb_bodies, "record",
                        lambda: {(0x40, 0x48): {"verdict": "thumb-converted", "detail": "",
                                                "walked_bytes": 6, "pool_bytes": 0,
                                                "entry_site": "Thumb 0x08000040 b #0x8000040",
                                                "kind": "entry", "file": "asm/slice_000158.s"}})
    monkeypatch.setattr(thumb_bodies, "closure", lambda: {})
    monkeypatch.setattr(thumb_bodies, "site_tiers", lambda: {})
    out = tmp_path / "docs" / "research" / "THUMB_BODIES.csv"
    thumb_bodies.census(str(out), out=io.StringIO())
    with open(out, newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [(row["start"], row["end"], row["file"], row["arm_verdict"], row["verdict"])
            for row in rows] == [("0x40", "0x48", "asm/slice_000158.s", "", "thumb-converted")]
    assert rows[0]["left_incbin_bytes"] == "2"


@pytest.mark.xfail(strict=True, reason="thumb_annotate.PC_RELATIVE at thumb_annotate.py:21 only "
                                       "accepts a '#0x..' operand, and capstone 5.0.7 spells this "
                                       "small immediate in decimal ('#4'), so this literal is not "
                                       "resolved (the same tool resolves '#0xfc': "
                                       "test_thumb_annotate.py:26 passes)")
def test_the_annotator_reads_the_literal_the_load_names():
    rows = thumb_annotate.annotate(image_at({0x00: 0x4901, 0x08: 0x1234, 0x0A: 0x0800}), 0, 2)
    address, halfwords, text, literal, value = rows[0]
    assert address == 0x08000000
    assert halfwords == "0149"
    assert text == "ldr r1, [pc, #4]"
    assert (literal, value) == (8, 0x08001234)


def test_the_annotator_does_not_read_a_literal_past_the_end_of_the_image():
    rom = image(0x483F, size=4)
    assert decoded(rom, 0)[2] == "r0, [pc, #0xfc]", decoded(rom, 0)
    assert thumb_annotate.annotate(rom, 0, 2)[0][3:] == (None, None)


def test_a_non_pc_relative_operand_names_no_literal():
    assert convert.literal_of("movs", "r0, #1", 0) is None


def test_a_pc_relative_operand_resolves_to_the_word_its_pc_names():
    assert convert.literal_of("ldr", "r1, [pc, #4]", 0) == 0x08000008
    assert convert.literal_of("adr", "r0, #4", 0) == 0x08000008


def test_a_body_starting_at_two_mod_four_gets_one_halfword_of_pad():
    assert convert.body_text(["\tMOVS    r0, #1"], 0).count("DCW") == 0
    assert convert.body_text(["\tMOVS    r0, #1"], 2).count("DCW") == 1


def test_an_odd_row_start_takes_a_byte_pad_and_a_one_byte_item(monkeypatch):
    odd = convert.body_text(["\tMOVS    r0, #1"], 1)
    assert odd.count("DCB") == 1 and odd.count("DCW") == 0
    assert convert.word_lines(0x0803018D, 1, 0x04, "retail byte") == ["\tDCB     0x04\t; retail byte"]
    monkeypatch.setattr(convert, "ROM", bytes.fromhex("b5041c00"))
    assert [(item[0], item[1]) for item in convert.gap_items(1, 4)] == [(1, 1), (2, 2)]


def test_a_prologue_shape_is_an_entry_only_when_its_walk_returns(monkeypatch):
    blob = bytearray(8)
    blob[0:2] = (0xB505).to_bytes(2, "little")
    blob[2:4] = (0xBD00).to_bytes(2, "little")
    monkeypatch.setattr(thumb_bodies, "ROM", bytes(blob))
    found = thumb_bodies.prologue_entries([(0, 8)])
    assert list(found) == [(0, 8)] and found[(0, 8)][0][0] == 0
    monkeypatch.setattr(thumb_bodies, "ROM", bytes(8))
    assert thumb_bodies.prologue_entries([(0, 8)]) == {}


def test_a_census_branch_operand_is_seven_digits_not_eight():
    assert thumb_bodies.ENTRY_ADDRESS.findall("Thumb 0x080004e6 beq #0x80004f8") == \
        ["080004e6", "80004f8"]
    assert thumb_bodies.ENTRY_ADDRESS.findall(
        "method table 0x080498c4 slot 0x080498e4 -> 0x08014588")[-1] == "08014588"


def test_a_pointer_word_with_bit_zero_is_an_entry_and_an_even_one_is_not(monkeypatch):
    import pointer_rows

    monkeypatch.setattr(pointer_rows, "rows", lambda: [(8, 12, "carrier", 1)])
    monkeypatch.setattr(pointer_rows, "grid", lambda start, length: [start])
    value = thumb_bodies.ROM_BASE + 0x10 + 1
    monkeypatch.setattr(thumb_bodies, "ROM", bytes(8) + struct.pack("<I", value) + bytes(20))
    found = thumb_bodies.pointer_entries([(0x10, 0x20)])
    assert list(found) == [(0x10, 0x20)]
    assert found[(0x10, 0x20)][0][0] == 0x10
    assert found[(0x10, 0x20)][0][2] == "pointer table word 0x000008 = 0x%08X" % value
    monkeypatch.setattr(thumb_bodies, "ROM", bytes(8) + struct.pack("<I", value - 1) + bytes(20))
    assert thumb_bodies.pointer_entries([(0x10, 0x20)]) == {}
