
from __future__ import annotations

import concurrent.futures
import hashlib
import os
import pytest
import shutil
import struct
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "webfoot"))

import encode_cache
import generate_mapcontainer as generator
import mapcontainer
import webfoot_lz
from testkit import rom_bytes

ROM = os.path.join(generator.ROOT, "baserom.gba")
NAME = "test_the_map_container_population_round_trips_byte_for_byte"


def refused(call):
    try:
        call()
    except (mapcontainer.MapContainerError, webfoot_lz.ContainerError):
        return True
    return False


def member(payload=b"abcd", declared=4, stored=16):
    header = struct.pack("<II", 1, declared)
    return header, mapcontainer.Member(1, declared, payload, stored, 0)


def test_a_re_encode_shorter_or_longer_than_the_stored_extent_is_refused():
    header, one = member()
    assert mapcontainer.encode(one, lambda payload: header + bytes(8)) == header + bytes(8)
    assert refused(lambda: mapcontainer.encode(one, lambda payload: header + bytes(6)))
    assert refused(lambda: mapcontainer.encode(one, lambda payload: header + bytes(9)))
    assert refused(lambda: mapcontainer.encode(one, lambda payload: struct.pack("<II", 1, 5) + bytes(8)))


def test_a_run_whose_members_do_not_sum_to_the_run_length_is_refused():
    header, one = member()
    compress = lambda payload: header + bytes(8)  # noqa: E731
    assert mapcontainer.encode_run([one, one], compress) == (header + bytes(8)) * 2
    assert refused(lambda: mapcontainer.encode_run([one], lambda payload: header + bytes(3)))


def test_a_stray_value_error_does_not_pass_the_narrow_refusal():
    def stray():
        raise ValueError("a stray ValueError is not a container refusal")
    with pytest.raises(ValueError):
        refused(stray)


def test_a_root_candidate_in_the_last_record_extent_is_not_a_root():
    rom = bytearray(0x100)
    struct.pack_into("<I", rom, 0xF8, mapcontainer.TILE_BANK_TABLE)
    assert mapcontainer.root_slot(bytes(rom), mapcontainer.ROM_BASE + 0xAC) is True
    assert mapcontainer.root_slot(bytes(rom), mapcontainer.ROM_BASE + 0xB0) is False
    assert mapcontainer.root_slot(bytes(rom), mapcontainer.ROM_BASE + 0xB1) is False
    assert mapcontainer.root_slot(bytes(rom), mapcontainer.ROM_BASE + 0xFF) is False


def test_every_gap_stays_retail_and_the_sections_tile_the_span():
    offsets = [0, 4, 12, 20]
    sizes = [4, 4, 8, 8]
    sections = mapcontainer.plan_sections(0, 28, offsets, sizes, frozenset([12]))
    assert sections == [mapcontainer.Section("generated", 0, 8),
                        mapcontainer.Section("retail", 8, 12),
                        mapcontainer.Section("carve-out", 12, 20),
                        mapcontainer.Section("generated", 20, 28)]
    assert [s.start for s in sections[1:]] == [s.end for s in sections[:-1]]
    assert sections[0].start == 0 and sections[-1].end == 28
    gapped = mapcontainer.plan_sections(0, 28, offsets, sizes, frozenset())
    assert mapcontainer.Section("retail", 8, 12) in gapped
    assert refused(lambda: mapcontainer.plan_sections(0, 28, offsets, [4, 4, 8, 8, 4],
                                                      frozenset()))
    assert refused(lambda: mapcontainer.plan_sections(0, 24, offsets, sizes, frozenset()))
    assert refused(lambda: mapcontainer.plan_sections(0, 28, [], [], frozenset()))


def test_the_map_container_population_round_trips_byte_for_byte():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    generator.set_block("map")
    members = generator.read_members(rom)
    assert len(members) == generator.MAP.expected_containers
    assert sum(m.stored_size for m in members) == generator.MAP.expected_marker_union
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        early = list(pool.map(
            lambda m: mapcontainer.early_extent(rom, m.offset, generator.MAP.scan_max_payload),
            members))
    sample = members[::61]
    sample += [m for m, e in zip(members, early) if m.stored_size - e == 4][:1]
    sample += [m for m, e in zip(members, early) if m.stored_size == e][:1]
    sample += [m for m in members if m.offset in generator.MAP.carve_outs]
    scratch = tempfile.mkdtemp(prefix="mapcontainer-test-")
    compress, cache, close = encode_cache.cached_compress(
        generator.compressor(generator.COMPRESS, scratch), generator.COMPRESS,
        encode_cache.default_cache_dir())
    equal = 0
    try:
        for one in sample:
            blob = compress(one.payload)
            if one.offset in generator.MAP.carve_outs:
                assert blob != rom[one.offset:one.offset + one.stored_size]
                continue
            equal += blob == rom[one.offset:one.offset + one.stored_size]
        close()
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    checked = len(sample) - len(generator.MAP.carve_outs)
    print("%d/%d byte-equal over the %d-container sample (misses=%d)"
          % (equal, checked, len(sample), cache["misses"]))
    assert equal == checked


def test_the_packed_population_is_the_lane_contract_and_disjoint_from_everything():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    generator.set_block("map")
    assert len(generator.read_members(rom)) == generator.MAP.expected_containers == 5069
    pointers = mapcontainer.container_offsets(rom)
    pointer_spans = sorted((member.offset, member.offset + member.stored_size)
                           for member in mapcontainer.decode_many(rom, pointers))
    records = mapcontainer.record_extents(rom)
    excluded = pointer_spans + [(start, start + size) for rows in records.values()
                                for start, size in rows]
    excluded += generator.foreign_runs((generator.MAP.start, generator.MAP.end))
    scanned = generator.MAP.scan_walk(rom, (generator.MAP.start, generator.MAP.end), excluded)
    assert len(scanned) == 1116, len(scanned)
    decoded = [mapcontainer.decode(rom, offset, generator.MAP.scan_max_payload)
               for offset in scanned]
    assert sum(member.stored_size for member in decoded) == 168604
    assert {member.kind for member in decoded} == {1}
    spans = sorted((member.offset, member.offset + member.stored_size) for member in decoded)
    assert not any(b > c for (a, b), (c, d) in zip(spans, spans[1:])), "the packed set overlaps"
    assert not set(scanned) & set(pointers), "the scan re-found a pointer-named container"
    for start, end in spans:
        for other_start, other_end in pointer_spans:
            assert not (start < other_end and other_start < end), \
                "a packed member overlaps a pointer-walked container at %#x" % start
    assert 0x29B308 not in scanned


if __name__ == "__main__":
    test_a_re_encode_shorter_or_longer_than_the_stored_extent_is_refused()
    test_a_run_whose_members_do_not_sum_to_the_run_length_is_refused()
    test_every_gap_stays_retail_and_the_sections_tile_the_span()
    test_the_map_container_population_round_trips_byte_for_byte()
    test_the_packed_population_is_the_lane_contract_and_disjoint_from_everything()
    print("PASS %s" % NAME)
