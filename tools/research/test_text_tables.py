import csv
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import text_tables as T  # noqa: E402

ROWS, BYTES = T.recorded()
BASE = 0x08000000


def blob(size, fill=0):
    return bytearray([fill]) * size


def methods(buffer, base, targets):
    for index, target in enumerate(targets):
        struct.pack_into("<i", buffer, base + 4 * index, target - base)
    return buffer


def test_a_base_relative_table_is_a_record_table():
    buffer = blob(0x100)
    methods(buffer, 0x40, [0x80 | 1, 0x90 | 1, 0xA0 | 1, 0xB0 | 1])
    subclass, explained, evidence = T.classify(bytes(buffer), (0x40, 0x50, "slice_x.s", 1))
    assert subclass == "record table"
    assert explained == 0
    assert "self-relative=4/4" in evidence


def test_one_perturbed_word_drops_the_row_out_of_the_record_table_class():
    buffer = blob(0x100)
    methods(buffer, 0x40, [0x80 | 1, 0x90 | 1, 0xA0 | 1, 0xB0 | 1])
    struct.pack_into("<i", buffer, 0x44, 0x7FFF0000)
    subclass, _, evidence = T.classify(bytes(buffer), (0x40, 0x50, "slice_x.s", 1))
    assert subclass == "unknown"
    assert "self-relative=3/4" in evidence


def test_the_class_slot_convention_is_the_base_and_not_the_slot_address():
    blob_ = blob(0x100)
    struct.pack_into("<i", blob_, 0x50, 0x1234 | 1)
    assert T.method(0x40, 0x10, bytes(blob_)) == 0x40 + 0x1235
    assert T.method(0x40, 0x10, bytes(blob_)) != 0x50 + 0x1235


def test_the_three_recorded_anchors_resolve_base_relative():
    rom = T.read_rom(os.path.join(ROOT, "baserom.gba"))
    assert T.anchor_failures(rom) == []
    assert T.method(0x4AAF4, 0x00, rom) == 0x018EF7
    assert T.method(0x4AAF4, 0x08, rom) == 0x018F75
    assert T.method(0x4C484, 0x68, rom) == 0x04ECB1


def test_a_header_field_is_the_header_class_and_is_explained():
    buffer = blob(0x100)
    subclass, explained, evidence = T.classify(bytes(buffer), (0x40, 0x50, "rom_header.s", 9))
    assert (subclass, explained) == ("cartridge header", 0x10)
    assert "0x04..0xC0" in evidence


def test_a_header_row_outside_the_header_span_is_not_the_header_class():
    buffer = blob(0x100)
    subclass, explained, _ = T.classify(bytes(buffer), (0xC0, 0xD0, "rom_header.s", 60))
    assert (subclass, explained) == ("unknown", 0)


def test_a_text_shaped_row_with_no_reader_stays_unknown():
    buffer = bytearray(0x100)
    buffer[0x10:0x20] = b"A\x00B\x00C\x00D\x00E\x00F\x00G\x00H\x00"
    assert T.utf16(bytes(buffer[0x10:0x20]))
    subclass, explained, evidence = T.classify(bytes(buffer), (0x10, 0x20, "slice_x.s", 1))
    assert (subclass, explained) == ("unknown", 0)
    assert "utf16-shaped" in evidence


def test_the_printable_rule_is_not_the_text_class_either():
    buffer = blob(0x100)
    buffer[0x10:0x18] = b"ABCDEFGH"
    assert T.printable(bytes(buffer[0x10:0x18]))
    assert T.classify(bytes(buffer), (0x10, 0x18, "slice_x.s", 1))[0] == "unknown"


def test_the_class_table_sums_to_the_census_and_two_runs_agree():
    rom = T.read_rom(os.path.join(ROOT, "baserom.gba"))
    built, totals = T.measure(rom)
    assert (len(built), sum(row[1] - row[0] for row, _, _, _ in built)) == (ROWS, BYTES)
    assert sum(count for count, _, _ in totals.values()) == ROWS
    assert sum(size for _, size, _ in totals.values()) == BYTES
    assert T.check(rom) == 0
    assert totals["cartridge header"] == (10, 181, 181)
    assert totals["record table"][0] == 5
    assert totals["text"] == (0, 0, 0) and totals["numeric constant table"] == (0, 0, 0)


def test_the_emitter_spells_a_named_slot_as_a_relative_label_and_keeps_residue_numeric():
    buffer = blob(0x100)
    buffer[0x40:0x48] = struct.pack("<ii", 0x80 + 1 - 0x40, 0x90 + 1 - 0x40)
    named = {0x08000040: "unk_08000040", 0x08000080: "sub_08000080", 0x08000090: "sub_08000090"}
    lines, residue = T.dcd(bytes(buffer), (0x40, 0x48), [0x40], named)
    assert residue == 0
    assert lines == ["\tDCD\t|sub_08000080|+1-|unk_08000040|",
                     "\tDCD\t|sub_08000090|+1-|unk_08000040|"]
    assert b"".join(struct.pack("<i", value) for value in (0x80 + 1 - 0x40, 0x90 + 1 - 0x40)) \
        == bytes(buffer[0x40:0x48])
    unnamed, residue = T.dcd(bytes(buffer), (0x40, 0x48), [0x40], {0x08000040: "unk_08000040"})
    assert residue == 2 and unnamed == ["\tDCD\t0x00000041", "\tDCD\t0x00000051"]


def test_the_retail_region_converts_no_row_under_the_five_percent_rule():
    rom = T.read_rom(os.path.join(ROOT, "baserom.gba"))
    named = T.labels()
    table = T.table_report(rom, named)
    bases = sorted(T.class_bases(rom))
    assert table["bases"] == len(bases) == 150
    assert table["words"] == 1027 and len(table["rows"]) == 5
    for entry in table["rows"]:
        start, end = entry["row"][0], entry["row"][1]
        lines, residue = T.dcd(rom, (start, end), bases, named)
        assert len(lines) == len(T.words(rom, start, end))
        assert residue == len(lines) - entry["derivable"]
        assert residue > T.RESIDUE_MAXIMUM * len(lines) or not lines


def test_the_numeric_route_spells_every_byte_and_counts_an_unbased_word_as_residue():
    buffer = bytearray(0x100)
    struct.pack_into("<ii", buffer, 0x44, 0x20, 0x24)
    lines, residue, table, resolved = T.numeric_lines(bytes(buffer), (0x42, 0x4C), [0x40])
    assert lines == ["\tDCW\t0x0000", "\tDCD\t0x00000020", "\tDCD\t0x00000024"]
    assert (table, resolved, residue) == (2, 2, 2)
    body = b"".join(struct.pack("<H", int(line.split()[1], 16)) if line.startswith("\tDCW")
                    else struct.pack("<I", int(line.split()[1], 16)) for line in lines)
    assert body == bytes(buffer[0x42:0x4C])
    unbased = T.numeric_lines(bytes(buffer), (0x42, 0x4C), [])
    assert unbased[1:] == (10, 2, 0)


def test_the_numeric_group_is_the_rows_whose_every_word_is_a_method_offset():
    rom = T.read_rom(os.path.join(ROOT, "baserom.gba"))
    built, out = T.groups(rom)
    assert len(built) == 713
    assert sum(row[1] - row[0] for row, _, _, _ in built) == 13788
    assert sum(count for count, _ in out.values()) == 720
    assert sum(size for _, size in out.values()) == 26438
    with open(os.path.join(ROOT, "docs", "research", "NUMBER_TABLES.csv"), newline="") as handle:
        record = list(csv.DictReader(handle))
    assert len(record) == 7
    assert sum(int(entry["bytes"]) for entry in record) == 12650
    assert sum(int(entry["words"]) for entry in record) == 3158
    assert sum(int(entry["residue"]) for entry in record) == 18
    assert all(entry["resolved"] == entry["words"] for entry in record)
    assert sum(int(entry["residue"]) for entry in record) <= T.RESIDUE_MAXIMUM * 12650


def test_the_numeric_record_reproduces_the_retail_bytes_and_nothing_is_still_incbin():
    rom = T.read_rom(os.path.join(ROOT, "baserom.gba"))
    assert T.check_numeric(rom) == 0


def test_the_record_matches_every_column_the_generator_writes():
    rom = T.read_rom(os.path.join(ROOT, "baserom.gba"))
    built, totals, table, record, doc = T.generated(rom)
    with open(os.path.join(ROOT, "docs", "research", "TEXT_TABLES.csv"), newline="") as handle:
        carried = handle.read()
    with open(os.path.join(ROOT, "docs", "research", "TEXT_TABLES.md"), newline="") as handle:
        page = handle.read()
    assert T.first_difference(carried, record) is None
    assert T.first_difference(page, doc) is None
    lines = record.splitlines()
    cells = lines[1].split(",")
    cells[1] = str(int(cells[1]) + 1)
    shifted = "\n".join([lines[0], ",".join(cells)] + lines[2:]) + "\n"
    assert "line 2:" in T.first_difference(shifted, record)

