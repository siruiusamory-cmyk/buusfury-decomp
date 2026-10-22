from __future__ import annotations

import bisect
import concurrent.futures
import contextlib
import io
import os
import shutil
import struct
import sys
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "webfoot"))

import emitted
import generate_mapcontainer as generator
import mapcontainer
from testkit import refused

ROM = os.path.join(generator.ROOT, "baserom.gba")
MANIFEST = os.path.join(HERE, "mapcontainer_manifest.csv")
SOURCE = os.path.join(generator.ROOT, "asm", "rest_of_the_game.s")
PAYLOADS = os.path.join(generator.ROOT, "assets", "mapcontainer")
RECORDS = os.path.join(generator.ROOT, "assets", "maprecords")
ORACLE_WORKERS = 16


def rom_or_skip():
    if not os.path.exists(ROM):
        pytest.skip("%s is absent, so the ROM-gated acceptance test cannot run" % ROM)
    return open(ROM, "rb").read()


@pytest.fixture(scope="module")
def rom():
    return rom_or_skip()


@pytest.fixture(scope="module")
def extents(rom):
    generator.set_block("map")
    return mapcontainer.record_extents(rom)


@pytest.fixture(scope="module")
def plan(rom):
    generator.set_block("map")
    return generator.read_plan(rom, MANIFEST)


def oracle_streams(members):
    import encode_cache
    _, store = generator.load_store(PAYLOADS, members)
    payloads = sorted({store[member.offset] for member in members})
    scratch = tempfile.mkdtemp(prefix="maprecords-test-")
    try:
        cached, stats, close = encode_cache.cached_compress(
            generator.compressor(generator.COMPRESS, scratch), generator.COMPRESS,
            encode_cache.default_cache_dir())
        with concurrent.futures.ThreadPoolExecutor(max_workers=ORACLE_WORKERS) as pool:
            blobs = list(pool.map(cached, payloads))
        close()
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("oracle streams %d unique of %d, cache hits=%d misses=%d"
          % (len(payloads), len(members), stats["hits"], stats["misses"]))
    return dict(zip(payloads, blobs))


@pytest.fixture(scope="module")
def verify_run(rom, plan):
    members, _, _ = plan
    served = oracle_streams(members)
    guard = io.StringIO()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generator, "compressor",
                      lambda exe, scratch: lambda payload: served[payload])
        with contextlib.redirect_stdout(guard):
            code = generator.cmd_verify(type("Args", (), {
                "rom": ROM, "manifest": MANIFEST, "source": SOURCE,
                "payloads": PAYLOADS, "records": RECORDS})())
    return code, guard.getvalue(), len(served)


def test_every_section_kind_a_plan_can_produce_is_one_the_emitter_knows():
    known = mapcontainer.section_kinds()
    container_only = mapcontainer.plan_sections(0, 20, [0, 8], [8, 12], frozenset([8]))
    mixed = mapcontainer.plan_sections(
        0, 20, [0, 12, 16], [8, 4, 4], frozenset(),
        [mapcontainer.CONTAINER, mapcontainer.ROOT, mapcontainer.DOMINANT_FAMILY])
    for plan in (container_only, mixed):
        unknown = {section.kind for section in plan} - known
        assert not unknown, \
            "the tiling produced kind(s) the emitter would raw-copy: %s" % sorted(unknown)
    assert {"carve-out", "retail", mapcontainer.CONTAINER} <= known
    assert container_only[0].kind == mapcontainer.CONTAINER


def test_a_foreign_generated_run_may_carry_bytes_inside_a_planned_section():
    sections = [mapcontainer.Section(mapcontainer.CONTAINER, 0x00, 0x10),
                mapcontainer.Section("retail", 0x10, 0x40)]
    names = {0x00: "build\\mapcontainer\\map_00000000_00000010.bin",
             0x10: "baserom.gba_0x10_0x40.extracted"}
    name_of = lambda section: names[section.start]
    rows = [(0x00, 0x10, names[0x00], b""),
            (0x10, 0x20, "build\\jcalg1\\gen_10.bin", b""),
            (0x20, 0x40, None, b"")]
    assert emitted.tiling_problems(sections, rows, name_of) == []
    problems = emitted.tiling_problems(
        sections, rows[:2] + [(0x20, 0x40, "build\\jcalg1\\gen_20", b"")], name_of)
    assert problems and "names neither it nor its own bytes" in problems[0], problems


def test_a_source_carried_generated_run_is_not_scanned_as_a_packed_container(rom):
    source = ("        INCBIN  build\\jcalg1\\gen_40.bin\n"
              "        INCBIN  build\\mapcontainer\\map_00000060_00000080.bin\n"
              "        INCBIN  baserom.gba_0x80_0xa0.extracted\n")
    assert generator.foreign_runs((0x00, 0x100), source) == [(0x40, 0x60)]
    image = b"\xff" * 0x40 + bytes(rom[0x179A50:0x179A50 + 488])
    assert 0x40 in mapcontainer.packed_container_offsets(image, (0x00, len(image)), [])
    assert mapcontainer.packed_container_offsets(
        image, (0x00, len(image)), [(0x40, 0x40 + 488)]) == []


def test_the_two_root_named_families_are_planned_and_their_runs_are_sections(rom, plan):
    members, sections, plan = plan
    for family, rows, expected in (
            (mapcontainer.ROOT_TABLE, mapcontainer.root_table_sites(rom), (949, 22776)),
            (mapcontainer.ROOT_POINTER, mapcontainer.root_pointer_sites(rom), (740, 2960))):
        assert (len(rows), sum(length for _, length in rows)) == expected, family
        runs = [section for section in sections if section.kind == family]
        starts = [section.start for section in runs]
        for offset, length in rows:
            index = bisect.bisect_right(starts, offset) - 1
            assert index >= 0 and runs[index].start <= offset \
                and offset + length <= runs[index].end, \
                "%s at %#x is not inside one %s section" % (family, offset, family)
    assert sum(section.end - section.start for section in sections
               if section.kind in (mapcontainer.ROOT_TABLE, mapcontainer.ROOT_POINTER)) == 25736


def test_the_two_root_named_families_parse_and_repack_synthetic_records():
    image = bytearray(0x40)
    table = bytes((index * 11) & 0xFF for index in range(24))
    image[0x20:0x38] = table
    image[0x38:0x3C] = (0x08000010).to_bytes(4, "little")
    image = bytes(image)
    parsed = mapcontainer.record_fields(image, mapcontainer.ROOT_TABLE, 0x20, 24)
    assert mapcontainer.serialize_fields(mapcontainer.ROOT_TABLE, parsed) == table
    pointer = mapcontainer.record_fields(image, mapcontainer.ROOT_POINTER, 0x38, 4)
    assert mapcontainer.serialize_fields(mapcontainer.ROOT_POINTER, pointer) == image[0x38:0x3C]
    broken = image[:0x38] + (0x1234).to_bytes(4, "little")
    assert refused(lambda: mapcontainer.record_fields(broken, mapcontainer.ROOT_POINTER, 0x38, 4))


def test_the_record_families_walk_to_the_measured_contract(rom, extents):
    measured = {family: (len(rows), sum(length for _, length in rows))
                for family, rows in extents.items()}
    assert measured == {mapcontainer.ROOT: (427, 34160),
                        mapcontainer.DOMINANT_FAMILY: (1439, 51184),
                        mapcontainer.SCREENBLOCK_A: (1, 12),
                        mapcontainer.SCREENBLOCK_B: (41, 1312),
                        mapcontainer.TERRAIN_FAMILY: (1, 568),
                        mapcontainer.ROOT_TABLE: (949, 22776),
                        mapcontainer.ROOT_POINTER: (740, 2960)}
    kept = {family: mapcontainer.clip(rows, (generator.MAP.start, generator.MAP.end))
            for family, rows in extents.items()}
    assert {family: (len(rows), sum(end - start for start, end in rows))
            for family, rows in kept.items()} == {mapcontainer.ROOT: (426, 34080),
                                                  mapcontainer.DOMINANT_FAMILY: (1438, 51140),
                                                  mapcontainer.SCREENBLOCK_A: (1, 12),
                                                  mapcontainer.SCREENBLOCK_B: (41, 1312),
                                                  mapcontainer.TERRAIN_FAMILY: (1, 568),
                                                  mapcontainer.ROOT_TABLE: (949, 22776),
                                                  mapcontainer.ROOT_POINTER: (740, 2960)}
    from collections import Counter
    factories = Counter(mapcontainer.LAYER_FACTORIES[rom[offset:offset + 4][0]
                                                     | rom[offset + 1] << 8
                                                     | rom[offset + 2] << 16
                                                     | rom[offset + 3] << 24]
                        for offset, _ in extents[mapcontainer.SCREENBLOCK_A]
                        + extents[mapcontainer.SCREENBLOCK_B]
                        + extents[mapcontainer.TERRAIN_FAMILY])
    assert factories == Counter({mapcontainer.SCREENBLOCK_A: 1, mapcontainer.SCREENBLOCK_B: 41,
                                 mapcontainer.TERRAIN_FAMILY: 1})
    terrain = extents[mapcontainer.TERRAIN_FAMILY][0][0]
    assert mapcontainer.terrain_extent(rom, terrain, mapcontainer.TERRAIN_FIELDS) == 568
    assert rom[terrain + 4] * rom[terrain + 5] == 140
    assert all(mapcontainer.screenblock_a_extent(rom, offset, mapcontainer.SCREENBLOCK_A_FIELDS)
               == 0x0C for offset, _ in extents[mapcontainer.SCREENBLOCK_A])
    assert all(mapcontainer.screenblock_b_extent(rom, offset, mapcontainer.SCREENBLOCK_B_FIELDS)
               == 0x20 for offset, _ in extents[mapcontainer.SCREENBLOCK_B])
    for offset, length in extents[mapcontainer.DOMINANT_FAMILY]:
        assert length == 0x18 + 4 * (rom[offset + 0x14] * rom[offset + 0x15])
        assert rom[offset] == 0x87 and rom[offset + 1] == 0x80
    assert all(mapcontainer.root_extent(rom, offset, mapcontainer.ROOT_FIELDS) == 0x50
               for offset, _ in extents[mapcontainer.ROOT])


def test_every_record_re_serializes_from_its_parsed_fields(rom, plan):
    equal = total = 0
    members, sections, plan = plan
    for family, rows in plan["all"].items():
        serializer = generator.MAP_SERIALIZERS[family]
        for offset, size in rows:
            blob = serializer(rom, family, offset, size)
            equal += blob == rom[offset:offset + size]
            total += 1
    print("records %d/%d byte-equal to the image" % (equal, total))
    assert equal == total == 3956


def test_the_record_runs_and_the_container_runs_claim_every_byte_once(rom, plan, extents):
    members, sections, plan = plan
    cursor = generator.MAP.start
    for section in sections:
        assert section.start == cursor, "a hole or an overlap at %#x" % section.start
        cursor = section.end
    assert cursor == generator.MAP.end
    records = [section for section in sections if section.kind in plan["families"]]
    containers = [section for section in sections
                  if section.kind == mapcontainer.CONTAINER]
    carve = [section for section in sections if section.kind == "carve-out"]
    assert len(records) == 2773, len(records)
    assert sum(section.end - section.start for section in records) == 141136
    assert sum(section.end - section.start for section in containers) == 1056452
    assert [(section.start, section.end) for section in carve] == [(0x29B308, 0x29B320)]
    assert len(plan["records"]) == len(records) == 2773
    assert sum(len(run) for run in plan["records"].values()) == 3954
    assert sum(len(rows) for rows in plan["all"].values()) == 3956
    assert not set(plan["records"]) & set(plan["containers"])
    spans = sorted((member.offset, member.offset + member.stored_size) for member in members)
    for family, rows in extents.items():
        for offset, length in rows:
            for span in spans:
                assert not (max(offset, span[0]) < min(offset + length, span[1]))


def test_the_map_prover_re_derives_the_records_and_the_tokens(verify_run):
    code, output, streams = verify_run
    assert streams > 0
    assert code == 0, output
    assert "records 3956/3956 byte-equal and retail" in output
    assert "INCBIN tokens=4970 tile 0x179a50..0x2b8bc8 exactly" in output
    assert "ledger rows to append: 4686" in output


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))


def test_a_map_entrys_variant_slot_names_a_root_the_first_slot_does_not(rom):
    roots = mapcontainer.map_roots(rom)
    variant = {0x22229C, 0x230C64, 0x232F6C, 0x24AE74, 0x2666BC, 0x2B7E78}
    assert len(roots) == 427
    assert variant <= set(roots)
    first = set()
    for index in range(mapcontainer.ME_COUNT):
        base = struct.unpack_from("<I", rom, mapcontainer.ME_TABLE
                                  + index * mapcontainer.ME_SIZE + 0x2C)[0] - mapcontainer.ROM_BASE
        first.add(struct.unpack_from("<I", rom, base)[0] - mapcontainer.ROM_BASE)
    assert len(first) == 421
    assert not variant & first
    assert all(struct.unpack_from("<I", rom, root + 0x4C)[0] == mapcontainer.TILE_BANK_TABLE
               for root in roots)


def test_a_child_list_row_states_its_own_length_and_refuses_a_foreign_part(rom):
    offset, size = 0x1C28D4, 200
    parts, length = mapcontainer.mode_row_fields(rom, offset, offset + size)
    assert length == size
    assert (len(parts["lists"]), len(parts["index"]), len(parts["objects"])) == (5, 5, 2)
    assert mapcontainer.serialize_mode_row(rom, mapcontainer.MODE_ROW, offset, size) \
        == rom[offset:offset + size]
    outside = bytearray(rom)
    outside[offset + 2] = 0x00
    assert mapcontainer.mode_row_fields(bytes(outside), offset, offset + size) is None
    index_at = parts["lists"][-1][0] + 4 + 4 * parts["lists"][-1][1]
    miscounted = bytearray(rom)
    miscounted[index_at] ^= 0x04
    assert mapcontainer.mode_row_fields(bytes(miscounted), offset, offset + size) is None


def test_a_second_constructor_is_an_object_and_a_gaps_tail_is_claimed(rom):
    assert mapcontainer.MODE_HANDLERS == (0x08007675, 0x080072CD)
    parts, length = mapcontainer.mode_row_fields(rom, 0x19D634, 0x19D664)
    assert length == 0x30 and len(parts["objects"]) == 2
    assert [words[0] for words in parts["objects"]] == [0x080072CD, 0x08007675]
    assert mapcontainer.serialize_mode_row(rom, mapcontainer.MODE_ROW, 0x19D634, 0x30) \
        == rom[0x19D634:0x19D664]
    tail, tail_length = mapcontainer.mode_row_fields(rom, 0x17C0DC, 0x17C0F4)
    assert tail_length == 0x18 and len(tail["lists"]) == 1 and len(tail["index"]) == 1
    assert tail["objects"] == []
    sites = mapcontainer.mode_row_sites(
        rom, (generator.MAP.start, generator.MAP.end),
        [(member.offset, member.offset + member.stored_size)
         for member in generator.read_members(rom)]
        + [(offset, offset + size) for rows in mapcontainer.record_extents(rom).values()
           for offset, size in rows]
        + generator.foreign_runs((generator.MAP.start, generator.MAP.end)))
    assert len(sites) == 358, len(sites)
    assert sum(size for _, size in sites) == 28288
    assert (0x1AB430, 72) in sites and (0x17C0DC, 0x18) in sites
