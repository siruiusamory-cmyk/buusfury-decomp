from __future__ import annotations

import concurrent.futures
import hashlib
import os
import shutil
import struct
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "webfoot"))

import ainodes
import cellmap
import emitted
import encode_cache
import endrombank
import endromcontainer
import endromfacing
import endromrecords
import enemystats
import eventindex
import eventpool
import pairsprite
import generate_mapcontainer as generator
import globalstate
import glyphtable
import mapcontainer
import pytest
import rowtable
import webfoot_lz
from testkit import perturbed_record, refusal_message, refused, rom_bytes

ROM = os.path.join(generator.ROOT, "baserom.gba")
MANIFEST = os.path.join(generator.ROOT, "tools", "mapcontainer", "endromcontainer_manifest.csv")
SOURCE = os.path.join(generator.ROOT, "asm", "rest_of_the_game.s")
NAME = "test_the_endrom_population_round_trips_byte_for_byte"
BLOCK_BYTES = endromcontainer.BLOCK_END - endromcontainer.BLOCK_START


def endrom_image():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    generator.set_block("endrom")
    return rom


def synthetic():
    return bytearray(endromcontainer.BLOCK_END + 8)


def test_a_chain_continues_onto_a_back_to_back_container_only():
    image = synthetic()
    first = webfoot_lz.pack(b"abcd" * 4, kind=1)
    second = webfoot_lz.pack(b"wxyz" * 4, kind=1)
    image[0x6B0000:0x6B0000 + len(first)] = first
    assert endromcontainer.container_offsets(image) == [0x6B0000]
    image[0x6B0000 + len(first):0x6B0000 + len(first) + len(second)] = second
    assert endromcontainer.container_offsets(image) == [0x6B0000, 0x6B0000 + len(first)]


def test_a_header_over_the_bound_at_a_chain_end_is_refused():
    image = synthetic()
    blob = webfoot_lz.pack(b"abcd" * 4, kind=1)
    image[0x6B0000:0x6B0000 + len(blob)] = blob
    struct.pack_into("<II", image, 0x6B0000 + len(blob), 1, endromcontainer.MAX_PAYLOAD + 1)
    assert refused(lambda: endromcontainer.container_offsets(image))


def test_a_header_over_the_bound_away_from_a_chain_is_filtered_not_refused():
    image = synthetic()
    struct.pack_into("<II", image, endromcontainer.BLOCK_START, 1, 0x2010E800)
    assert endromcontainer.container_offsets(image) == []


def test_the_population_matches_the_measured_contract():
    rom = endrom_image()
    members = generator.read_members(rom)
    assert len(members) == generator.ENDROM.expected_containers == 427
    assert {member.kind for member in members} == {1}
    sizes = [member.stored_size for member in members]
    assert sum(sizes) == generator.ENDROM.expected_marker_union == 440696
    assert (members[0].offset, members[-1].offset + sizes[-1]) == generator.ENDROM.edges
    spans = []
    for member in members:
        if spans and member.offset <= spans[-1][1]:
            spans[-1][1] = max(spans[-1][1], member.offset + member.stored_size)
        else:
            spans.append([member.offset, member.offset + member.stored_size])
    union = sum(end - start for start, end in spans)
    assert len(spans) == 68 and union == sum(sizes) <= BLOCK_BYTES
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        early = list(pool.map(
            lambda m: mapcontainer.early_extent(rom, m.offset, endromcontainer.MAX_PAYLOAD),
            members))
    assert sum(early) == generator.ENDROM.expected_early_union == 440000
    tails = {}
    for member, early_size in zip(members, early):
        tails[member.stored_size - early_size] = tails.get(member.stored_size - early_size, 0) + 1
    assert tails == {0: 253, 4: 174}
    assert max(member.declared_size for member in members) == 65474
    bank = [struct.unpack_from("<I", rom, endromcontainer.BANK_TABLE + 4 * index)[0]
            for index in range(endromcontainer.BANK_COUNT)]
    by_offset = {member.offset: member for member in members}
    assert all(address - endromcontainer.ROM_BASE in by_offset for address in bank)
    assert {by_offset[address - endromcontainer.ROM_BASE].declared_size
            for address in bank} == {4096}


def test_the_alternation_tiles_the_block_and_matches_the_source():
    rom = endrom_image()
    members, sections, runs = generator.read_plan(rom, MANIFEST)
    runs = runs["containers"]
    assert sections[0].start == generator.ENDROM.start
    assert sections[-1].end == generator.ENDROM.end
    cursor = generator.ENDROM.start
    totals = {}
    for section in sections:
        assert section.start == cursor, "a hole or an overlap at %#x" % section.start
        cursor = section.end
        totals[section.kind] = totals.get(section.kind, 0) + section.end - section.start
    assert cursor == generator.ENDROM.end
    assert totals == {"generated": 440696,
                      endromrecords.FAMILY: 7128,
                      endrombank.FAMILY: 652,
                      ainodes.FAMILY: 53152,
                      rowtable.FAMILY: 6624,
                      enemystats.FAMILY: 4200,
                      eventindex.FAMILY: 2088,
                      eventpool.FAMILY: 127328,
                      globalstate.FAMILY: 40,
                      glyphtable.FAMILY: 680,
                      cellmap.FAMILY: 848,
                      pairsprite.FAMILY: 96,
                      endromfacing.FAMILY: 32,
                      "endrom_sprite_record_r20": 144,
                      "endrom_sprite_record_r25": 144,
                      "retail": (generator.ENDROM.end - generator.ENDROM.start
                                 - 440696 - 7128 - 652 - 53152 - 6624 - 4200 - 2088 - 127328 - 40
                                 - 680 - 848 - 96 - 288 - 32)}
    assert (len(sections), len(runs)) == (2216, 68)
    row_runs = [section for section in sections if section.kind == rowtable.FAMILY]
    assert [(section.start, section.end) for section in row_runs] == [(0x70F514, 0x710EF4)]
    record_runs = [section for section in sections
                   if section.kind == endromrecords.FAMILY]
    assert [(section.start, section.end) for section in record_runs] == [(0x6F82EC, 0x6F9EC4)]
    bank_runs = [section for section in sections if section.kind == endrombank.FAMILY]
    assert [(section.start, section.end) for section in bank_runs] == [(0x6F393C, 0x6F3BC8)]
    enemy_runs = [section for section in sections if section.kind == enemystats.FAMILY]
    assert [(section.start, section.end) for section in enemy_runs] == [(0x711274, 0x7122DC)]
    index_runs = [section for section in sections if section.kind == eventindex.FAMILY]
    assert [(section.start, section.end) for section in index_runs] == [(0x79B704, 0x79BF2C)]
    pool_runs = [section for section in sections if section.kind == eventpool.FAMILY]
    assert [(section.start, section.end) for section in pool_runs] == [(0x77C5A4, 0x79B704)]
    state_runs = [section for section in sections if section.kind == globalstate.FAMILY]
    assert [(section.start, section.end) for section in state_runs] == [(0x6FC238, 0x6FC260)]
    glyph_runs = [section for section in sections if section.kind == glyphtable.FAMILY]
    assert [(section.start, section.end) for section in glyph_runs] == [(0x757EE8, 0x758190)]
    mask_runs = [section for section in sections if section.kind == cellmap.FAMILY]
    assert [(section.start, section.end) for section in mask_runs] == [(0x7198E4, 0x719C34)]
    node_runs = [section for section in sections if section.kind == ainodes.FAMILY]
    assert len(node_runs) == 1030
    assert sum(section.end - section.start for section in node_runs) == 53152
    assert all(generator.ENDROM.start <= section.start < section.end <= generator.ENDROM.end
               for section in node_runs)
    for start, end in ((0x74F080, 0x79BF2C), (0x6FC238, 0x7315E8)):
        inside = [section for section in node_runs if start <= section.start < end]
        assert inside, "no node run inside slice %#x..%#x" % (start, end)
        assert all(section.end <= end for section in inside)
    rows, problems = emitted.source_rows(generator.ROOT, rom,
                                         emitted.source_text(generator.ROOT, SOURCE),
                                         (generator.ENDROM.start, generator.ENDROM.end))
    assert problems == [], problems
    inside = [row for row in rows if generator.ENDROM.start <= row[0] < generator.ENDROM.end]
    tiling = emitted.tiling_problems(sections, inside,
                                     lambda section: generator.section_output(section)
                                     .replace(os.sep, "\\"))
    assert tiling == [], tiling
    missing = [section for section in sections
               if not os.path.exists(os.path.join(generator.ROOT, generator.section_output(section)))]
    if missing:
        pytest.skip("%d section files are absent, so no emitted run can be compared" % len(missing))
    for section in sections:
        path = os.path.join(generator.ROOT, generator.section_output(section))
        assert open(path, "rb").read() == rom[section.start:section.end], path


def test_the_whole_endrom_population_round_trips_byte_for_byte():
    rom = endrom_image()
    members = generator.read_members(rom)
    scratch = tempfile.mkdtemp(prefix="endrom-test-")
    compress, cache, close = encode_cache.cached_compress(
        generator.compressor(generator.COMPRESS, scratch), generator.COMPRESS,
        encode_cache.default_cache_dir())
    equal = 0
    try:
        for member in members:
            blob = compress(member.payload)
            equal += blob == rom[member.offset:member.offset + member.stored_size]
        close()
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("%d/%d byte-equal over the whole population (misses=%d)"
          % (equal, len(members), cache["misses"]))
    assert equal == len(members)


def test_the_44_record_family_tiles_its_region_and_round_trips():
    rom = endrom_image()
    rows = endromrecords.extents(rom)[endromrecords.FAMILY]
    assert len(rows) == 162
    assert sum(size for _, size in rows) == 7128
    assert (rows[0][0], rows[-1][0] + rows[-1][1]) == (0x6F82EC, 0x6F9EC4)
    assert endromrecords.round_trip(rom) == {"records": 162, "equal": 162, "bytes": 7128}
    members = {member.offset for member in generator.read_members(rom)}
    assert all(struct.unpack_from("<I", rom, offset + 0x10)[0] - 0x08000000 in members
               for offset, _ in rows)


def test_the_bank_table_family_round_trips_and_names_endrom_containers():
    rom = endrom_image()
    assert endrombank.extents(rom)[endrombank.FAMILY] == [(0x6F393C, 652)]
    assert endrombank.round_trip(rom) == {"records": 1, "equal": 1, "bytes": 652}
    members = {member.offset: member for member in generator.read_members(rom)}
    words = endrombank.fields(rom, endrombank.BASE)["bank"]
    assert len(words) == 155
    named = [members[word - 0x08000000] for word in words if word - 0x08000000 in members]
    assert len(named) == 155, "only %d of 155 bank words name a container" % len(named)
    assert {member.declared_size for member in named} == {4096}


def test_a_bank_table_with_a_non_pointer_word_is_refused():
    assert refused(lambda: endrombank.extents(synthetic()))


def test_a_44_record_that_breaks_its_own_id_rule_is_refused():
    assert refused(lambda: endromrecords.extents(synthetic()))


def test_the_record_serializer_is_field_driven_not_a_copy():
    rom = endrom_image()
    parsed = endromrecords.fields(rom, 0x6F82EC)
    assert endromrecords.serialize(parsed) == rom[0x6F82EC:0x6F82EC + 44]
    parsed["word_08"] ^= 0x1F
    changed = endromrecords.serialize(parsed)
    assert changed != rom[0x6F82EC:0x6F82EC + 44]
    differs = [index for index in range(44) if changed[index] != rom[0x6F82EC + index]]
    assert differs == [0x08]


def test_the_glyph_table_family_round_trips_its_85_records():
    rom = endrom_image()
    rows = glyphtable.extents(rom)[glyphtable.FAMILY]
    assert len(rows) == 85 and sum(size for _, size in rows) == 680
    assert (rows[0][0], rows[-1][0] + rows[-1][1]) == (0x757EE8, 0x758190)
    assert glyphtable.round_trip(rom) == {"records": 85, "equal": 85, "bytes": 680}
    assert glyphtable.assert_contract(rom) == glyphtable.CONTRACT == {
        "records": 85, "bytes": 680, "values": 340, "max": 0x2E8,
        "first": 0x757EE8, "last_end": 0x758190}


def test_a_glyph_value_outside_the_buffer_bound_is_refused():
    rom = bytearray(glyphtable.END)
    legal = [0x17, 0x1E, 0x25, 0x2C] * glyphtable.COUNT
    struct.pack_into("<%dH" % len(legal), rom, glyphtable.BASE, *legal)
    assert [glyphtable.fields(rom, glyphtable.BASE + 8 * index)["field_02"]
            for index in range(glyphtable.COUNT)] == [0x1E] * glyphtable.COUNT
    record = glyphtable.BASE + 8 * 3
    struct.pack_into("<4H", rom, record, 0x17, 0x1E, glyphtable.BUFFER, 0x2C)
    assert refusal_message(lambda: glyphtable.fields(rom, record)) == (
        "endrom_glyph_table_85 record 3 field 2 is 0x300, outside the consumer's 0x300-byte buffer")


def test_the_glyph_serializer_is_field_driven_not_a_copy():
    rom = endrom_image()
    parsed = glyphtable.fields(rom, glyphtable.BASE)
    assert glyphtable.serialize(parsed) == rom[glyphtable.BASE:glyphtable.BASE + 8]
    parsed["field_04"] += 1
    changed = glyphtable.serialize(parsed)
    differs = [index for index in range(8) if changed[index] != rom[glyphtable.BASE + index]]
    assert differs == [4]


def test_a_moved_glyph_field_moves_exactly_its_own_bytes():
    rom = endrom_image()
    image = perturbed_record(glyphtable, 3, "field_04", 1)
    differs = [offset for offset in range(glyphtable.BASE, glyphtable.END)
               if image[offset] != rom[offset]]
    assert differs == [glyphtable.BASE + 8 * 3 + 4]


if __name__ == "__main__":
    test_a_chain_continues_onto_a_back_to_back_container_only()
    test_a_header_over_the_bound_at_a_chain_end_is_refused()
    test_a_header_over_the_bound_away_from_a_chain_is_filtered_not_refused()
    test_the_population_matches_the_measured_contract()
    test_the_alternation_tiles_the_block_and_matches_the_source()
    test_the_whole_endrom_population_round_trips_byte_for_byte()
    test_the_bank_table_family_round_trips_and_names_endrom_containers()
    test_a_bank_table_with_a_non_pointer_word_is_refused()
    test_the_44_record_family_tiles_its_region_and_round_trips()
    test_a_44_record_that_breaks_its_own_id_rule_is_refused()
    test_the_record_serializer_is_field_driven_not_a_copy()
    test_the_glyph_table_family_round_trips_its_85_records()
    test_a_glyph_value_outside_the_buffer_bound_is_refused()
    test_the_glyph_serializer_is_field_driven_not_a_copy()
    test_a_moved_glyph_field_moves_exactly_its_own_bytes()
    print("PASS %s" % NAME)
