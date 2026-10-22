from __future__ import annotations

import builtins
import importlib
import io
import json
import os
import struct
import sys

import capstone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

ROM_BASE = 0x08000000
VENEER = b"\x78\x47\x00\x00"
STOCK = {name: None for name in ("arm_bodies", "arm_evidence", "arm_body_convert", "arm_ledger",
                                "arm_csv_class")}


def tool(name):
    if STOCK[name] is None:
        path = os.path.join(ROOT, "baserom.gba")
        original = builtins.open
        if not os.path.exists(path):
            def only_rom(file, *args, **kwargs):
                if os.fspath(file) == path:
                    return io.BytesIO(b"")
                return original(file, *args, **kwargs)
            builtins.open = only_rom
        try:
            STOCK[name] = importlib.import_module(name)
        finally:
            builtins.open = original
    return STOCK[name]


def image(*words, size=None):
    out = bytearray(b"\x00" * (size if size is not None else 4 * len(words)))
    for index, value in enumerate(words):
        struct.pack_into("<I", out, index * 4, value)
    return bytes(out)


def arms(words, offset):
    decoder = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
    return [(instruction.address - ROM_BASE, instruction.size, instruction.mnemonic,
             instruction.op_str, instruction.bytes)
            for instruction in decoder.disasm(image(*words), ROM_BASE + offset)]


def encoded(word):
    return struct.pack("<I", word)


def test_ledger_parses_pads_and_skips_the_four_rows_it_documents(tmp_path):
    path = tmp_path / "ledger.csv"
    path.write_text("# offset,length,isa,...\n"
                    "0x100,8,thumb,region,source,kind,evidence,6\n"
                    "\n"
                    "0x200,16,arm\n", encoding="ascii")
    rows = tool("arm_bodies").ledger(str(path))
    assert rows == [(0x100, 8, "thumb", 6), (0x200, 16, "arm", 0)]


def test_instruction_bytes_cover_an_instruction_count_never_a_row_length():
    rows = [(0x100, 8, "thumb", 6), (0x200, 16, "arm", 0)]
    assert sorted(tool("arm_bodies").instruction_bytes(rows)) == list(range(0x100, 0x106))


def test_the_veneer_before_a_row_is_criterion_b_and_the_overlap_is_criterion_a(monkeypatch):
    bodies = tool("arm_bodies")
    monkeypatch.setattr(bodies, "ROM", image(0x1234) + VENEER + image(0xE1A00000) + image(0xE1A00000))
    assert bodies.criteria_of(8, 12, set()) == "b"
    assert bodies.criteria_of(8, 12, {9}) == "ab"
    assert bodies.criteria_of(4, 8, set()) == ""
    assert bodies.criteria_of(0, 4, set()) == ""
    assert bodies.criteria_of(0, 4, {1}) == "a"


def test_a_word_run_that_spells_an_instruction_is_still_data(monkeypatch):
    convert = tool("arm_body_convert")
    word = {0x08000010: 0x0801455E, 0x08000014: 0x0801466C, 0x08000018: 0x03001000}
    raw = convert.unreachable(16, 28, arms([0xE1A00000] + list(word.values()), 16), set())
    assert sorted(raw) == [20, 24, 28], raw
    assert all(reason for reason in raw.values())
    assert convert.address_word(0x0801455E) and convert.address_word(0x0801456C)
    assert convert.address_word(0x03001000) and convert.address_word(0x07000000)
    assert not convert.address_word(0xE1A00000) and not convert.address_word(0x00000001)


def test_an_isolated_address_like_word_is_left_to_the_assembler(monkeypatch):
    convert = tool("arm_body_convert")
    raw = convert.unreachable(8, 16, arms([0xE1A00000, 0x0801455E], 8), set())
    assert raw == {}, raw
    assert convert.address_word(0x0801455E)


def test_a_pool_word_the_body_carries_is_emitted_as_its_exact_word(monkeypatch):
    bodies = tool("arm_bodies")
    convert = tool("arm_body_convert")
    words = [0xE59F000C, 0, 0, 0, 0, 0x0801455E]
    monkeypatch.setattr(bodies, "ROM", image(*words))
    instructions = arms(words, 16)
    assert [instruction[0] for instruction in instructions] == [16, 20, 24, 28, 32, 36]
    assert instructions[0][3] == "r0, [pc, #0xc]", instructions
    assert convert.pc_loaded(16, 40, instructions) == {36}
    raw = convert.unreachable(16, 40, instructions, set())
    assert sorted(raw) == [36], raw
    lines, where = convert.body_lines(16, 40, instructions, {36: 0x0801455E}, set(), raw=raw)
    assert lines == ["\tLDR      r0, [pc, #0xc]",
                     "\tANDEQ    r0, r0, r0",
                     "\tANDEQ    r0, r0, r0",
                     "\tANDEQ    r0, r0, r0",
                     "\tANDEQ    r0, r0, r0",
                     "|arm_08000024|",
                     "\tDCD     0x0801455E\t; stmdaeq r1, {r1, r2, r3, r4, r6, r8, sl, lr} | %s"
                     % raw[36]]
    assert where == [16, 20, 24, 28, 32, None, 36]


def test_a_thumb_xref_is_not_arm_state_evidence_and_an_arm_xref_is(monkeypatch):
    evidence = tool("arm_evidence")
    bodies = tool("arm_bodies")
    row = ("buu.s", 7, "baserom.gba_0x8000_0x8010.extracted", 0x8000, 0x8010)
    thumb = {ROM_BASE + 0x8000: [("thumb", 0x08003C68, "bpl", "#0x8003c70")]}
    arm = {ROM_BASE + 0x8000: [("arm", 0x08004000, "b", "#0x8008000")]}
    both = {ROM_BASE + 0x8000: thumb[ROM_BASE + 0x8000] + arm[ROM_BASE + 0x8000]}
    assert evidence.evidence_for(row, thumb)[0] == "thumb-xref"
    assert evidence.evidence_for(row, thumb)[1].startswith("Thumb 0x08003c68")
    assert evidence.evidence_for(row, arm)[0] == "arm-xref"
    assert evidence.evidence_for(row, both)[0] == "arm-xref"
    assert evidence.evidence_for(row, None) == ("none", "")
    assert evidence.evidence_for(row, {}) == ("none", "")
    assert evidence.evidence_for(row, {ROM_BASE + 0x8004: thumb[ROM_BASE + 0x8000]})[0] == "none"
    monkeypatch.setattr(bodies, "ROM", image(0xE1A00000) + VENEER + image(0xE1A00000, 0xE1A00000))
    assert evidence.evidence_for(("buu.s", 7, "t", 8, 12), thumb)[0] == "veneer"


def test_references_report_the_state_of_the_span_that_holds_the_branch(monkeypatch):
    bodies = tool("arm_bodies")
    evidence = tool("arm_evidence")
    image_bytes = struct.pack("<H", 0xE004) + b"\x00" * 6 + encoded(0xEA000002) + b"\x00" * 4
    monkeypatch.setattr(bodies, "ROM", image_bytes)
    found = evidence.references([(0, 8, "thumb"), (8, 16, "arm")],
                               {ROM_BASE + 0xC, ROM_BASE + 0x18})
    assert found[ROM_BASE + 0xC] == [("thumb", ROM_BASE, "b", "#0x800000c")]
    assert found[ROM_BASE + 0x18] == [("arm", ROM_BASE + 8, "b", "#0x8000018")]
    assert evidence.references([(0, 8, "thumb")], {ROM_BASE + 0x18}) == {}


def test_a_branch_outside_the_body_and_every_arm_span_stays_a_word():
    convert = tool("arm_body_convert")
    inside = convert.branch_text("b", "#0x8000014", ROM_BASE + 16, 16, 28, set(), {})
    assert inside == "\tB        |arm_08000014|"
    spanned = convert.branch_text("b", "#0x8000040", ROM_BASE + 16, 16, 28, set(), {},
                                 [(ROM_BASE + 0x40, ROM_BASE + 0x60)])
    assert spanned == "\tB        |arm_08000040|"
    assert convert.branch_text("b", "#0x08040000", ROM_BASE + 16, 16, 28, set(), {}) is None
    assert convert.branch_text("b", "#0x08040000", ROM_BASE + 16, 16, 28, set(), {},
                               [(ROM_BASE + 0x40, ROM_BASE + 0x60)]) is None
    assert convert.branch_text("bx", "lr", ROM_BASE + 16, 16, 28, set(), {}) is None


def test_a_branch_no_arm_span_owns_keeps_its_word_with_armlinks_reason(monkeypatch):
    bodies = tool("arm_bodies")
    convert = tool("arm_body_convert")
    branch = 0xEA00FFFC
    monkeypatch.setattr(bodies, "ROM", image(0xE1A00000, 0xE1A00000, branch))
    built = []
    monkeypatch.setattr(convert, "assemble",
                        lambda text, base, dev=None: (built.append(text), (encoded(branch), []))[1])
    monkeypatch.setattr(convert, "label_table", lambda: {})
    lines, raw, _reason = convert.build_body(("buu.s", 7, "t", 8, 12))
    assert raw == 1
    assert lines == ["|arm_08000008|",
                     "\tDCD     0xEA00FFFC\t; b #0x8040000 | armlink L6239E: target 0x08040000 "
                     "is Thumb and these areas do not interwork"]
    assert "\tDCD     0xEA00FFFC" in built[0] and "\tB " not in built[0]


def results(*outputs):
    class Done:
        def __init__(self, returncode, text):
            self.returncode = returncode
            self.stdout = text
            self.stderr = ""
    queue = iter(Done(*pair) for pair in outputs)

    def run(*_args, **_kwargs):
        return next(queue)
    return run


def test_an_armasm_failure_that_names_no_line_is_raised_and_never_read_as_a_byte_diff(
        monkeypatch, tmp_path):
    convert = tool("arm_body_convert")
    monkeypatch.setattr(convert, "workspace", lambda dev=None: str(tmp_path))
    monkeypatch.setattr(convert.subprocess, "run",
                        results((1, '"<command line>": Error: A1439E: Cannot obtain license\n'
                                    "License path: C:\\missing\\license.dat\n")))
    try:
        convert.assemble("\tAREA |x|, CODE16\n\tEND\n", 0x08000000)
    except SystemExit as error:
        assert "A1439E" in str(error), str(error)
    else:
        raise AssertionError("an assembler that names no line must stop the caller")


def test_an_armlink_failure_keeps_its_own_words_in_the_refusal(monkeypatch, tmp_path):
    convert = tool("arm_body_convert")
    monkeypatch.setattr(convert, "workspace", lambda dev=None: str(tmp_path))
    monkeypatch.setattr(convert.subprocess, "run",
                        results((0, ""), (1, "L6239E: Cannot call ARM symbol in Thumb code\n")))
    got, refusals = convert.assemble("\tAREA |x|, CODE16\n\tEND\n", 0x08000000)
    assert got is None
    assert refusals == [(0, "armlink: L6239E: Cannot call ARM symbol in Thumb code")]


def test_arm_ranges_needs_the_manifest_and_reads_both_manifest_shapes(tmp_path):
    ledger = tool("arm_ledger")
    missing = str(tmp_path / "none.json")
    try:
        ledger.arm_ranges(missing)
    except SystemExit:
        pass
    else:
        raise AssertionError("a missing manifest must be refused")
    converted = tmp_path / "converted.json"
    converted.write_text(json.dumps({"converted": [{"start": 0x40, "end": 0x60},
                                                   {"start": 0x10, "end": 0x20}]}),
                         encoding="ascii")
    assert ledger.arm_ranges(str(converted)) == [(0x10, 0x20), (0x40, 0x60)]
    runs = tmp_path / "runs.json"
    runs.write_text(json.dumps({"rows": [
        {"verdict": "thumb-converted", "runs": [[0x20, 0x30], [0x10, 0x20], [0x40, 0x50]]},
        {"verdict": "thumb", "runs": [[0x80, 0x90]]}]}), encoding="ascii")
    assert ledger.arm_ranges(str(runs), key="runs") == [(0x10, 0x30), (0x40, 0x50)]
    assert ledger.covered([(0x10, 4, "$a", "r", "s", "k", "e", 4)]) == set(range(0x10, 0x14))


def test_relabel_takes_the_isa_from_the_mapping_symbol_and_counts_code_bytes():
    ledger = tool("arm_ledger")
    states = [(ROM_BASE + 0x10, "$a"), (ROM_BASE + 0x20, "$t"), (ROM_BASE + 0x30, "$d")]
    assert ledger.relabel([(0x10, 0x20), (0x20, 0x30), (0x30, 0x40)], states) == [
        (0x10, 0x20, "arm", 16), (0x20, 0x30, "thumb", 16), (0x30, 0x40, "data", 0)]


def test_the_frozen_census_carries_the_sixtynine_converted_runs(tmp_path):
    csv_class = tool("arm_csv_class")
    spans = csv_class.spans(str(tmp_path / "no-manifest.json"))
    assert len(spans) == 69, len(spans)
    assert all(start < end for start, end in spans)


def test_the_committed_run_measurement_is_the_two_thousand_four_hundred_ninety_six():
    rows = tool("arm_csv_class").base_rows()
    assert len(rows) == 2496
    assert len({(row["file"], row["line_first"]) for row in rows}) == 2496


def test_a_run_only_partly_inside_a_converted_span_is_not_marked(tmp_path):
    csv_class = tool("arm_csv_class")
    spans = {(0x10, 0x20)}
    assert csv_class.covered({"rom_start": "0x10", "rom_end": "0x18"}, spans)
    assert not csv_class.covered({"rom_start": "0x14", "rom_end": "0x24"}, spans)
    assert not csv_class.covered({"rom_start": "0x08", "rom_end": "0x18"}, spans)


def test_the_pre_assembler_gate_calls_a_byte_exact_reassembly_arm_and_a_decode_alone_ambiguous(
        monkeypatch):
    bodies = tool("arm_bodies")
    monkeypatch.setattr(bodies, "ROM", image(0xE1A00000, 0xE1A01001, 0, 0))
    row = ("buu.s", 7, "t", 4, 12)
    assert bodies.classify("a", row, reassembles=True) == (
        "arm", "2 ARM instruction(s), 0 pool word(s)")
    assert bodies.classify("a", row, reassembles=False)[0] == "ambiguous"
    assert bodies.classify("a", row) == ("arm-decode", "2 whole ARM instruction(s), 0 pool word(s)")
    assert bodies.classify("b", ("buu.s", 7, "t", 4, 11))[0] == "stays-incbin"
    assert bodies.classify("b", tuple(row))[0] == "arm-decode"
