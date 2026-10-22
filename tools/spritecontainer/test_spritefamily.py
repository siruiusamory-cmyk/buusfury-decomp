from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "mapcontainer"))

import spritefamily as sf
import def50


def rom_bytes():
    return open(os.path.join(ROOT, "baserom.gba"), "rb").read()


def test_the_family_is_the_measured_population_and_sum():
    rom = rom_bytes()
    assert sf.assert_contract(rom) == sf.EXPECTED
    totals = {family: sum(size for _, size in sf.extents(rom, family)[family])
              for family in sf.FAMILIES}
    assert totals == sf.EXPECTED_BYTES
    assert sum(totals.values()) == sf.UNION_BYTES == 337664


def test_every_record_reserializes_byte_equal_from_its_own_fields():
    rom = rom_bytes()
    assert sf.round_trip(rom) == {sf.DEFINITION: (297, 297),
                                  sf.ANIMATION: (1017, 1017),
                                  sf.FRAME: (10980, 10980),
                                  sf.INDEX: (1, 1)}


def test_the_distinct_records_are_disjoint_and_the_fifth_family_is_not_reached():
    rom = rom_bytes()
    walked = sf.walk(rom)
    animations = set(walked[sf.ANIMATION])
    frames = set(walked[sf.FRAME])
    assert len(animations) == 1017 and len(frames) == 10980
    assert not animations & frames
    fifth = set()
    grids = set()
    for site in sf.table_offsets(rom):
        if rom[site + 0x50:site + 0x54] != bytes(4):
            fifth.add(struct.unpack_from("<I", rom, site + 0x50)[0] - sf.ROM_BASE)
    grids = {grid for grid, _definition, _slot, _frames in def50.grids(rom)}
    assert len(fifth) == 10 and len(grids) == 126
    assert not fifth & animations and not fifth & frames
    assert not grids & animations and not grids & frames and not grids & fifth


def test_the_index_table_reserializes_from_its_297_words():
    rom = rom_bytes()
    rebuilt = b"".join(struct.pack("<I", word) for word in
                       (sf.ROM_BASE + offset for offset in sf.table_offsets(rom)))
    assert rebuilt == rom[sf.TABLE:sf.TABLE_END]
    assert len(rebuilt) == sf.TABLE_BYTES == 1188


def test_the_spritedefs_block_plan_is_the_four_components_and_tiles_once():
    import generate_mapcontainer as generator
    rom = rom_bytes()
    generator.set_block("spritedefs")
    members, sections, plan = generator.read_plan(
        rom, os.path.join(ROOT, "tools", "spritecontainer", "spritecontainer_manifest.csv"))
    assert members == [] and plan["containers"] == {}
    assert plan["families"] == sf.FAMILIES + (def50.FAMILY, def50.CELL_FAMILY)
    assert [(section.kind, section.start, section.end - section.start) for section in sections] == [
        (sf.FRAME, 0x6A88AC, 240), (sf.ANIMATION, 0x6A899C, 52),
        (sf.DEFINITION, sf.DEFINITION_START, 57868), (sf.INDEX, sf.TABLE, sf.TABLE_BYTES),
        ("retail", sf.TABLE_END, 0x6B7E8C - sf.TABLE_END)]
    assert (sections[0].start, sections[-1].end) == (generator.SPRITEDEFS.start,
                                                     generator.SPRITEDEFS.end)
    assert {run: len(rows) for run, rows in plan["records"].items()} == \
        {0x6A88AC: 12, 0x6A899C: 1, sf.DEFINITION_START: 297, sf.TABLE: 1}
    payloads = generator.record_payloads(rom, plan["all"])
    assert len(payloads) == 12431
    assert all(blob == rom[offset:offset + size]
               for offset, _, size, blob in payloads)
    assert sum(size for _, _, size, _ in payloads) == sf.UNION_BYTES + 696 + 3656 == 342016


def test_the_definitions_tile_up_to_the_table_and_the_index_serializes_from_297_words():
    rom = rom_bytes()
    definitions = sf.extents(rom, sf.DEFINITION)[sf.DEFINITION]
    assert definitions[0][0] == sf.DEFINITION_START and len(definitions) == 297
    assert [offset + size for offset, size in definitions][:-1] == \
        [offset for offset, _ in definitions][1:]
    assert definitions[-1][0] + definitions[-1][1] == sf.TABLE == sf.DEFINITION_END
    words = struct.unpack_from("<%dI" % sf.COUNT, rom, sf.TABLE)
    assert b"".join(struct.pack("<I", word) for word in words) == \
        rom[sf.TABLE:sf.TABLE_END] == sf.serialize_record(rom, sf.INDEX, sf.TABLE, sf.TABLE_BYTES)
    assert [word - sf.ROM_BASE for word in words] == [offset for offset, _ in definitions]


if __name__ == "__main__":
    test_the_family_is_the_measured_population_and_sum()
    test_every_record_reserializes_byte_equal_from_its_own_fields()
    test_the_distinct_records_are_disjoint_and_the_fifth_family_is_not_reached()
    test_the_index_table_reserializes_from_its_297_words()
    test_the_spritedefs_block_plan_is_the_four_components_and_tiles_once()
    test_the_definitions_tile_up_to_the_table_and_the_index_serializes_from_297_words()
    print("PASS test_spritefamily")
