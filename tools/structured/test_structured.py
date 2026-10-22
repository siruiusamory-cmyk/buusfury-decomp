from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE)))

import families
import generate_structured as generator
import payload_store
from testkit import require, rom_bytes

ROM = os.path.join(generator.ROOT, "baserom.gba")
STORE = os.path.join(generator.ROOT, "assets", "structured")
NAME = "test_the_structured_families_round_trip_and_tile"


def test_a_map_entry_round_trips_and_a_short_record_is_refused():
    raw = struct.pack("<12B11I", *range(23))
    assert families.MapEntry.from_bytes(raw).to_bytes() == raw
    assert families.MapEntry.from_bytes(raw).trigger_count == 4
    try:
        families.MapEntry.from_bytes(raw[:-1])
    except families.StructuredError:
        pass
    else:
        raise AssertionError("a short map entry was accepted")


def test_a_placement_record_round_trips_and_a_bad_child_count_is_refused():
    body = struct.pack("<8I", families.PLACEMENT_FACTORY, 1, 5, 0x700098, 0x1F, 0x080555A0, 1,
                       0x080716EC)
    record = families.PlacementRecord.from_bytes(body)
    assert record.to_bytes() == body
    assert record.child_count == 1 and record.descriptor_pointer == 0x080555A0
    bad = struct.pack("<8I", families.PLACEMENT_FACTORY, 1, 5, 0, 0, 0x080555A0, 9, 0)
    try:
        families.PlacementRecord.from_bytes(bad)
    except families.StructuredError:
        pass
    else:
        raise AssertionError("a child count of 9 was accepted")


def test_a_sibling_record_keeps_its_factory_and_refuses_a_foreign_one():
    body = struct.pack("<7I", families.SIBLING_FACTORIES[0], 0, 0x00700030, 0xB4, 1, 0, 0)
    assert families.SiblingObjectRecord.from_bytes(body).to_bytes() == body
    try:
        families.SiblingObjectRecord.from_bytes(struct.pack("<7I", 0x0800FD55, *([0] * 6)))
    except families.StructuredError:
        pass
    else:
        raise AssertionError("a placement factory was accepted as a sibling record")


def test_a_method_record_round_trips_and_refuses_a_foreign_method_and_flag():
    body = struct.pack("<2I4H", families.METHOD_RECORD_METHOD, 0x40, 0x58, 0x168, 0xAF, 0x1C7)
    assert families.MethodRecord.from_bytes(body).to_bytes() == body
    for word in (0x0800A7A0, 0x0800A7A2, 0x08039F09):
        try:
            families.MethodRecord.from_bytes(struct.pack("<2I4H", word, 0x40, 0, 0, 0, 0))
        except families.StructuredError:
            pass
        else:
            raise AssertionError("%#010x was accepted as a method record's method word" % word)
    try:
        families.MethodRecord.from_bytes(
            struct.pack("<2I4H", families.METHOD_RECORD_METHOD, 0x20, 0, 0, 0, 0))
    except families.StructuredError:
        pass
    else:
        raise AssertionError("a flag outside the measured pair was accepted")


def test_a_placement_child_round_trips_and_refuses_a_word_that_is_not_code():
    body = struct.pack("<I4H", 0x08039F09, 0x4B0, 0x3F8, 0, 25)
    assert families.PlacementChild.from_bytes(body).to_bytes() == body
    for word in (0x08039F08, 0x7A87021D, 0x09039F09):
        try:
            families.PlacementChild.from_bytes(struct.pack("<I4H", word, 0, 0, 0, 0))
        except families.StructuredError:
            pass
        else:
            raise AssertionError("%#010x was accepted as a placement child's method word" % word)


def test_a_word_and_a_descriptor_round_trip():
    assert families.Word.from_bytes(b"\x01\x02\x03\x04").to_bytes() == b"\x01\x02\x03\x04"
    assert families.DescriptorRecord.from_bytes(bytes(8)).to_bytes() == bytes(8)
    assert families.EightByteRecord.from_bytes(bytes(8)).to_bytes() == bytes(8)
    assert families.EightByteRecord.from_bytes(bytes(range(8))).words == (0x03020100, 0x07060504)
    try:
        families.EightByteRecord.from_bytes(bytes(7))
    except families.StructuredError:
        pass


def test_the_entry_arrays_are_the_code_consumed_gap_bytes():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    built = families.plan(rom)
    names = [name for name, _, _, _ in families.ENTRY_ARRAYS]
    assert names == ["entry_pointer_array_18", "entry_pointer_array_1c", "entry_record_array_20"]
    sites = families.overlap_sites(rom)
    assert not [site for site in sites if site[2] in names or site[3] in names]
    total = sum(end - start for name in names for start, end in built.extents[name])
    assert total == sum(families.MEASURED[name][2] for name in names) == 776
    for name in names:
        records_ok, records, bytes_ok, bytes_total = families.round_trip(rom)[name]
        assert records_ok == records and bytes_ok == bytes_total
        assert bytes_total == families.MEASURED[name][2]


def test_a_perturbed_count_byte_moves_the_entry_array_walk():
    rom = bytearray(rom_bytes(ROM, generator.ROM_SHA256))
    before = families.measured_extents(bytes(rom))["entry_pointer_array_18"]
    index = next(i for i in range(families.ME_COUNT)
                 if rom[families.ME_TABLE + i * families.ME_SIZE + 5])
    offset = families.ME_TABLE + index * families.ME_SIZE
    count = rom[offset + 5]
    rom[offset + 5] = 0
    after = families.measured_extents(bytes(rom))["entry_pointer_array_18"]
    assert after[1] == before[1] - count and after[2] < before[2], (before, after)


def test_the_consumer_table_is_a_32_byte_header_and_393_rows_of_8_bytes():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    rows = families.record_extents(rom)["firstmib_consumer_table"]
    assert rows[0] == (0x71C90, 32)
    assert len(rows) == 1 + families.FIRST_MIB_ROWS == 394
    assert families.FIRST_MIB_HEADER + families.FIRST_MIB_ROWS * families.FIRST_MIB_ROW == 3176
    assert sum(length for _, length in rows) == 3176
    assert families.extents(rom)["firstmib_consumer_table"] == [(0x71C90, 0x728F8)]
    header = families.FirstMibHeader.from_bytes(rom[0x71C90:0x71CB0])
    assert header.iwram == (0x03003300, 0x03003898, 0x03001C4C, 0x03001068)
    assert header.rom == (0x0806EE6C, 0x0807012C)
    assert header.indices == (0, 7, 13, 18, 22, 25, 28, 0)
    assert families.FirstMibRow.from_bytes(rom[0x71CB0:0x71CB8]).values == (553, 0, 546, 0)
    assert families.FirstMibRow.from_bytes(rom[0x728F0:0x728F8]).values == (19000, 2091, 17348, 2091)
    assert families.serialize(rom, "firstmib_consumer_table", 0x71C90, 32) == rom[0x71C90:0x71CB0]
    try:
        families.FirstMibRecord.from_bytes(bytes(16))
        raise AssertionError("a 16-byte consumer-table record was accepted")
    except families.StructuredError:
        pass


def test_every_family_round_trips_over_the_retail_corpus():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    result = families.round_trip(rom)
    for family in families.FAMILY_ORDER:
        records_ok, records, bytes_ok, total = result[family]
        print("%-28s %4d/%4d records %6d/%6d bytes"
              % (family, records_ok, records, bytes_ok, total))
        assert records_ok == records and records > 0
        assert bytes_ok == total


def test_the_measured_extents_are_the_recorded_ones():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    measured = families.measured_extents(rom)
    assert measured == families.MEASURED
    built = families.plan(rom)
    extent_bytes = sum(end - start for rows in built.extents.values() for start, end in rows)
    assert extent_bytes == families.PLAN["region_a_extent_bytes"] \
        + families.MEASURED["tile_bank_pointer_table"][2]
    region_a = [run for run in built.runs if run[0] < families.REGION_A[1]]
    assert len(region_a) == families.PLAN["region_a_runs"]
    assert len(built.gaps) == families.PLAN["region_a_gaps"]
    assert sum(end - start for start, end in region_a) == families.PLAN["region_a_union_bytes"]


def test_region_a_runs_and_gaps_tile_the_span():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    built = families.plan(rom)
    region_a = [run for run in built.runs if run[0] < families.REGION_A[1]]
    pieces = sorted([(start, end) for start, end in region_a] + list(built.gaps))
    assert pieces[0][0] == families.REGION_A[0]
    assert pieces[-1][1] == families.REGION_A[1]
    for previous, following in zip(pieces, pieces[1:]):
        assert previous[1] == following[0], "hole or overlap at %#x" % previous[1]
    assert sum(end - start for start, end in pieces) == \
        families.REGION_A[1] - families.REGION_A[0]


def test_every_generated_run_is_the_retail_bytes():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    built = families.plan(rom)
    rows = families.record_extents(rom)
    members = {}
    for member in built.members:
        members.setdefault(generator.run_of(built, member.key), []).append(member)
    for run in built.runs:
        run_members = sorted(members.get(run, []), key=lambda member: member.start)
        assert run_members and run_members[0].start == run[0]
        assert run_members[-1].end == run[1]
        for previous, following in zip(run_members, run_members[1:]):
            assert previous.end == following.start
        blob = b"".join(families.payload(rom, member.family, member.extent_start,
                                         member.extent_end, rows[member.family])
                        [member.start - member.extent_start:
                         member.end - member.extent_start]
                        for member in run_members)
        assert blob == rom[run[0]:run[1]], "run %#x is not retail" % run[0]
    print("%d of %d generated runs are the retail bytes" % (len(built.runs), built.union_components))


def test_the_overlap_clipping_never_double_counts_a_byte():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    built = families.plan(rom)
    extent_bytes = sum(end - start for rows in built.extents.values() for start, end in rows)
    assert sum(built.clipped.values()) == extent_bytes - families.PLAN["region_a_union_bytes"] \
        - families.MEASURED["tile_bank_pointer_table"][2]
    for family in families.FAMILY_ORDER:
        kept_bytes = sum(end - start for start, end in built.kept[family])
        extent = sum(end - start for start, end in built.extents[family])
        assert kept_bytes + built.clipped[family] == extent
    assert sum(member.end - member.start for member in built.members) == \
        sum(end - start for start, end in built.runs)
    for member in built.members:
        assert member.extent_start <= member.start < member.end <= member.extent_end
    sites = families.overlap_sites(rom)
    assert len(sites) == 371
    assert sum(high - low for low, high, *_ in sites) == 6160


def test_a_section_file_is_what_the_library_re_serializes_from_the_store():
    store_path = payload_store.path(STORE)
    require(store_path, "%s is absent, so run extract.cmd first" % store_path)
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    built = families.plan(rom)
    store = payload_store.read(store_path)
    members = {}
    for member in built.members:
        members.setdefault(generator.run_of(built, member.key), []).append(member)
    checked = 0
    for run in built.runs:
        run_members = sorted(members[run], key=lambda member: member.start)
        blob = b"".join(store[member.key] for member in run_members)
        assert blob == rom[run[0]:run[1]], "the store's run %#x is not retail" % run[0]
        path = os.path.join(generator.ROOT, generator.section_output(("generated",) + run))
        if os.path.exists(path):
            assert open(path, "rb").read() == blob, "%s is not the store's bytes" % path
            checked += 1
    print("%d generated section file(s) equal the library's re-serialization" % checked)


def test_a_settled_overlap_is_decided_by_the_longer_extent():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    built = families.plan(rom)
    placement = [row for row in built.extents["placement_record"]
                 if row[0] <= 0x074590 < row[1]][0]
    variation = [row for row in built.extents["variation_source_words"]
                 if row[0] <= 0x074590 < row[1]][0]
    assert placement[1] - placement[0] == 1632 and variation[1] - variation[0] == 204
    assert (variation[0], variation[1]) == (0x07458C, 0x074658)
    kept_variation = [row for row in built.kept["variation_source_words"]
                      if row[0] >= 0x07458C and row[1] <= 0x074658]
    assert kept_variation == [(0x07458C, 0x074590)], \
        "the shorter extent did not keep exactly its four leading bytes"


if __name__ == "__main__":
    test_a_map_entry_round_trips_and_a_short_record_is_refused()
    test_a_placement_record_round_trips_and_a_bad_child_count_is_refused()
    test_a_sibling_record_keeps_its_factory_and_refuses_a_foreign_one()
    test_a_placement_child_round_trips_and_refuses_a_word_that_is_not_code()
    test_a_word_and_a_descriptor_round_trip()
    test_the_entry_arrays_are_the_code_consumed_gap_bytes()
    test_a_perturbed_count_byte_moves_the_entry_array_walk()
    test_the_consumer_table_is_a_32_byte_header_and_393_rows_of_8_bytes()
    ROM = os.path.join(generator.ROOT, "baserom.gba")
    test_every_family_round_trips_over_the_retail_corpus()
    test_the_measured_extents_are_the_recorded_ones()
    test_region_a_runs_and_gaps_tile_the_span()
    test_every_generated_run_is_the_retail_bytes()
    test_the_overlap_clipping_never_double_counts_a_byte()
    test_a_section_file_is_what_the_library_re_serializes_from_the_store()
    test_a_settled_overlap_is_decided_by_the_longer_extent()
    print("PASS %s" % NAME)
