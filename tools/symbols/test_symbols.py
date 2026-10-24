from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import gate
import pytest

import generate_symbols

pytestmark = pytest.mark.skipif(
    not os.path.exists(os.path.join(ROOT, "baserom.gba")),
    reason="baserom.gba is absent, so the symbol proofs cannot run")

TOOLCHAIN = "ARM Linker, ADS1.2 [Build 805]"
COMMIT = "2026-10-15T00:00:00-07:00"
SLICE = (0x1000, 0x2000)
IMAGE_SIZE = 8388608


def in_scratch(call):
    root = tempfile.mkdtemp(prefix="symbols-test-")
    previous_root = gate.ROOT
    gate.ROOT = root
    try:
        return call(root)
    finally:
        gate.ROOT = previous_root
        shutil.rmtree(root, ignore_errors=True)


def write(root, name, text):
    path = os.path.join(root, *name.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n", encoding="utf-8") as handle:
        handle.write(text)
    return path


def slashed(root, name, text):
    return write(root, name, "\n".join(line + "\n" for line in text.splitlines()))


def map_file(root, symbols=(), states=("$d", 0x08000000), name="build/buu.map"):
    lines = ["=" * 80, "Image Symbol Table", "    Mapping Symbols",
             "    Sym    Value        Execution Region"]
    if states and isinstance(states[0], str):
        states = (states,)
    for state, address in states:
        lines.append("    %s     0x%08x   ROM_START" % (state, address))
    lines += ["    Global Symbols",
              "    Symbol Name                              Value     Ov Type        Size"
              "  Object(Section)"]
    for entry in symbols:
        symbol, address, type_, size, obj = entry
        lines.append("    %-40s 0x%08x   %-12s %d  %s" % (symbol, address, type_, size, obj))
    lines += ["=" * 80, "Memory Map of the image", "  Image entry point : 0x08000000",
              "  Load Region LOAD_ROM (Base: 0x08000000, Size: 0x00800000, Max: 0xffffffff,"
              " ABSOLUTE)",
              "    Execution Region ROM_START (Base: 0x08000000, Size: 0x00800000,"
              " Max: 0xffffffff, ABSOLUTE)",
              "    Base Addr    Size         Type   Attr  Idx  E Section Name        Object",
              "    0x08000000   0x00800000   Data   RO     1    .text               probe.o"]
    return slashed(root, name, "\n".join(lines))


def ledger_file(root, rows, name="work/ledger.csv"):
    text = "".join("0x%x,%d,%s,%s,%s,%s,%s,%d\n" % row for row in rows)
    return write(root, name, text)


def asm_file(root, name="asm/probe.s"):
    return write(root, name, "\tINCBIN  baserom.gba_0x%x_0x%x.extracted\n" % SLICE)


def image_file(root, name="build/output/ROM_START", size=IMAGE_SIZE):
    path = os.path.join(root, *name.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.truncate(size)
    return path


def emit(root, symbols=(), rows=(), states=("$d", 0x08000000), out="build/output/symbols.json"):
    asm_file(root)
    return generate_symbols.emit(map_file(root, symbols, states), ledger_file(root, rows),
                                 os.path.join(root, *out.split("/")),
                                 image_file(root), COMMIT, TOOLCHAIN)


def load(path):
    with open(path, "rb") as handle:
        return handle.read()


def scratch_case():
    rows = [(0x2800, 0x40, "thumb", "proven_region", "asm/probe.s", "transcription",
             "byte-proven", 20),
            (0x1200, 0x40, "data", "slice_region", "asm/probe.s", "generated",
             "byte-proven", 0)]
    symbols = [("proven_label", 0x08002810, "Thumb Code", 0x20, "probe.o(Probe)"),
               ("slice_label", 0x08001210, "Data", 0x10, "probe.o(Probe)")]
    states = (("$d", 0x08000000), ("$t", 0x08002800))
    return symbols, rows, states


def test_two_emits_of_one_tree_are_byte_equal_and_the_second_pays_no_parse():
    def check(root):
        symbols, rows, states = scratch_case()
        first = emit(root, symbols, rows, states, out="build/output/one.json")
        second = emit(root, symbols, rows, states, out="build/output/two.json")
        calls = []
        original = generate_symbols.read_map

        def counted(path):
            calls.append(path)
            return original(path)

        generate_symbols.read_map = counted
        try:
            skipped = emit(root, symbols, rows, states, out="build/output/one.json")
        finally:
            generate_symbols.read_map = original
        return (first, second, skipped, calls, load(os.path.join(root, "build", "output",
                                                                "one.json")),
                load(os.path.join(root, "build", "output", "two.json")))

    first, second, skipped, calls, one, two = in_scratch(check)
    assert first == second == 4
    assert skipped == -1
    assert calls == []
    assert one == two
    assert one.endswith(b"\n") and b"\r" not in one


def test_the_key_holds_the_map_the_ledger_the_image_and_the_commit_date():
    def check(root):
        symbols, rows, states = scratch_case()
        path = os.path.join(root, "build", "output", "symbols.json")
        emit(root, symbols, rows, states)
        key = open(path + ".key").read()
        emit(root, symbols, rows, states)
        newer = generate_symbols.emit(map_file(root, symbols, states),
                                      ledger_file(root, rows), path, image_file(root),
                                      "2026-10-16T00:00:00-07:00", TOOLCHAIN)
        grown = generate_symbols.emit(map_file(root, symbols, states),
                                      ledger_file(root, rows + [(0x2840, 0x10, "thumb",
                                                                 "appended_region",
                                                                 "asm/probe.s", "transcription",
                                                                 "byte-proven", 2)]),
                                      path, image_file(root), COMMIT, TOOLCHAIN)
        return key, newer, grown, open(path + ".key").read()

    key, newer, grown, final = in_scratch(check)
    assert len(re.findall(r"[0-9a-f]{64}", key)) == 3 and COMMIT in key
    assert newer == 4 and grown == 5 and final != key


def test_an_entry_inside_an_incbin_slice_is_never_byte_proven():
    def check(root):
        symbols, rows, states = scratch_case()
        emit(root, symbols, rows, states)
        return json.loads(load(os.path.join(root, "build", "output", "symbols.json")))

    built = in_scratch(check)
    by_name = {entry["name"]: entry for entry in built["symbols"]}
    slice_extent = "slice_0x%08x_0x%08x" % (0x08000000 + SLICE[0], 0x08000000 + SLICE[1])
    assert by_name["slice_region"]["evidence"] == "inferred"
    assert by_name["slice_region"]["region"] == slice_extent
    assert by_name["slice_label"]["evidence"] == "inferred"
    assert by_name["slice_label"]["region"] == slice_extent
    assert by_name["proven_region"]["evidence"] == "byte-proven"
    assert by_name["proven_region"]["region"] == "proven_region"
    assert by_name["proven_label"]["evidence"] == "byte-proven"
    assert by_name["proven_label"]["region"] == "proven_region"


def test_a_touched_slice_that_does_not_contain_the_whole_range_is_still_not_proven():
    def check(root):
        symbols = [("spanning_label", 0x08000f00, "Data", 0x2000, "probe.o(Probe)")]
        emit(root, symbols, [(0x2800, 0x40, "thumb", "proven_region", "asm/probe.s",
                              "transcription", "byte-proven", 20)],
             (("$d", 0x08000000), ("$t", 0x08002800)))
        return json.loads(load(os.path.join(root, "build", "output", "symbols.json")))

    built = in_scratch(check)
    entry = [item for item in built["symbols"] if item["name"] == "spanning_label"][0]
    assert entry["evidence"] == "inferred" and "region" not in entry


def test_an_ambiguous_symbol_name_is_dropped_and_a_ledger_collision_is_resolved():
    def check(root):
        symbols = [(".data", 0x08003000, "Data", 0, "probe.o(Probe)"),
                   (".data", 0x08003004, "Data", 0, "probe.o(Probe)"),
                   ("proven_region", 0x08002800, "Thumb Code", 0x40, "probe.o(Probe)")]
        emit(root, symbols, [(0x2800, 0x40, "thumb", "proven_region", "asm/probe.s",
                              "transcription", "byte-proven", 20)],
             (("$t", 0x08000000),))
        return json.loads(load(os.path.join(root, "build", "output", "symbols.json")))

    built = in_scratch(check)
    names = [entry["name"] for entry in built["symbols"]]
    assert names.count("proven_region") == 1
    assert ".data" not in names
    assert built["symbols"] == sorted(built["symbols"],
                                      key=lambda entry: (int(entry["address"], 16),
                                                         entry["size"], entry["name"]))
    assert len(names) == len(set(names))


def test_a_symbol_that_collides_with_a_ledger_name_at_another_address_is_refused():
    def check(root):
        symbols = [("proven_region", 0x08002900, "Thumb Code", 0x10, "probe.o(Probe)")]
        return emit(root, symbols, [(0x2800, 0x40, "thumb", "proven_region", "asm/probe.s",
                                     "transcription", "byte-proven", 20)],
                    (("$t", 0x08000000),))

    try:
        in_scratch(check)
    except SystemExit as exc:
        assert "collides with the ledger" in str(exc)
    else:
        raise AssertionError("a colliding symbol name was accepted")


def test_a_mapping_symbol_contradicting_the_ledgers_isa_is_refused():
    def check(root):
        return emit(root, [("filler", 0x08000000, "Data", 0, "probe.o(Probe)")],
                    [(0x2800, 0x40, "data", "proven_region", "asm/probe.s", "generated",
                      "byte-proven", 0)], (("$t", 0x08000000),))

    try:
        in_scratch(check)
    except SystemExit as exc:
        assert "the mapping symbol says" in str(exc)
    else:
        raise AssertionError("a contradicting mapping symbol was accepted")


def test_the_document_names_its_sources_and_the_schema_is_the_pinned_one():
    def check(root):
        symbols, rows, states = scratch_case()
        emit(root, symbols, rows, states)
        return json.loads(load(os.path.join(root, "build", "output", "symbols.json")))

    built = in_scratch(check)
    assert set(built) == {"schema", "game", "rom_sha256", "build", "symbols"}
    assert built["schema"] == 1 and built["game"] == "buus_fury"
    assert built["rom_sha256"] == gate.CANONICAL_SHA256
    assert set(built["build"]) == {"toolchain", "image_sha256", "image_size", "map_source",
                                   "generated"}
    assert built["build"]["toolchain"] == TOOLCHAIN
    assert built["build"]["map_source"] == "armlink -map -symbols"
    assert built["build"]["generated"] == COMMIT
    assert built["build"]["image_size"] == IMAGE_SIZE
    assert built["build"]["image_sha256"] == hashlib.sha256(b"\0" * IMAGE_SIZE).hexdigest()


ALLOWED = {"name", "address", "size", "kind", "evidence", "format", "region", "source",
           "instructions"}
KINDS = {"arm", "thumb", "data", "asset"}
EVIDENCES = {"byte-proven", "ghidra", "runtime-proven", "declared", "inferred"}
ADDRESS = re.compile(r"^0x[0-9a-f]{8}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
PRINTABLE = re.compile(r"^[\x20-\x7e]+$")
HEX_RUN = re.compile(r"[0-9a-fA-F]{24,}")
HEX_DUMP = re.compile(r"\b(?:[0-9a-fA-F]{2} ){8,}")


def test_no_value_in_the_artefact_can_carry_an_image_byte_span():
    def check(root):
        symbols, rows, states = scratch_case()
        emit(root, symbols, rows, states)
        return load(os.path.join(root, "build", "output", "symbols.json"))

    blob = in_scratch(check)
    built = json.loads(blob)
    values = []
    for entry in built["symbols"]:
        assert set(entry) <= ALLOWED
        assert entry["kind"] in KINDS and entry["evidence"] in EVIDENCES
        assert ADDRESS.match(entry["address"])
        assert isinstance(entry["size"], int) and entry["size"] >= 0
        values += [value for value in entry.values() if isinstance(value, str)]
    values += [built["build"]["toolchain"], built["build"]["map_source"],
               built["build"]["generated"], built["game"]]
    for value in values:
        assert PRINTABLE.match(value), value
        assert not HEX_RUN.search(value), value
        assert not HEX_DUMP.search(value), value
        assert len(value) <= 160, value
    for digest in (built["rom_sha256"], built["build"]["image_sha256"]):
        assert DIGEST.match(digest), digest
    assert len(blob) < IMAGE_SIZE


def test_a_hexdump_shaped_symbol_name_is_refused_before_it_reaches_the_file():
    def check(root):
        return emit(root, [("08040a1cff00aabbccddeeff00112233", 0x08000000, "Data", 4,
                            "probe.o(Probe)")], [])

    try:
        in_scratch(check)
    except SystemExit as exc:
        assert "carries name=" in str(exc)
    else:
        raise AssertionError("a hexdump-shaped name reached the artefact")


def test_a_c_matched_row_is_accepted_and_names_the_compiled_source():
    def check(root):
        emit(root, [("filler", 0x08000000, "Data", 0, "probe.o(Probe)")],
             [(0x1C62C, 8, "thumb", "sub_0801C62C", "src/sub_0801C62C.c", "c",
               "c-matched", 8)], (("$t", 0x08000000),))
        return json.loads(load(os.path.join(root, "build", "output", "symbols.json")))

    built = in_scratch(check)
    entry = [item for item in built["symbols"] if item["name"] == "sub_0801C62C"][0]
    assert entry["source"] == "src/sub_0801C62C.c"
    assert entry["size"] == 8 and entry["evidence"] == "byte-proven"


def test_rebuild_cmd_carries_the_map_flags_and_names_the_step():
    text = open(os.path.join(ROOT, "rebuild.cmd"), errors="replace").read()
    assert "scatter.ld -map -symbols -o build/buu.axf 2> build\\buu.map" in text
    assert 'tools\\symbols\\generate_symbols.py' in text
    assert "echo symbols_exit=%ERRORLEVEL%" in text


if __name__ == "__main__":
    test_two_emits_of_one_tree_are_byte_equal_and_the_second_pays_no_parse()
    test_the_key_holds_the_map_the_ledger_the_image_and_the_commit_date()
    test_an_entry_inside_an_incbin_slice_is_never_byte_proven()
    test_a_touched_slice_that_does_not_contain_the_whole_range_is_still_not_proven()
    test_an_ambiguous_symbol_name_is_dropped_and_a_ledger_collision_is_resolved()
    test_a_symbol_that_collides_with_a_ledger_name_at_another_address_is_refused()
    test_a_mapping_symbol_contradicting_the_ledgers_isa_is_refused()
    test_the_document_names_its_sources_and_the_schema_is_the_pinned_one()
    test_no_value_in_the_artefact_can_carry_an_image_byte_span()
    test_a_hexdump_shaped_symbol_name_is_refused_before_it_reaches_the_file()
    test_a_c_matched_row_is_accepted_and_names_the_compiled_source()
    test_rebuild_cmd_carries_the_map_flags_and_names_the_step()
    print("PASS test_symbols")
