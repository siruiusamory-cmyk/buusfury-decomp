from __future__ import annotations

import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import pairsprite
import pytest
from testkit import refused, rom_bytes

ROM = os.path.join(os.path.dirname(os.path.dirname(HERE)), "baserom.gba")
DIGEST = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"


def synthetic():
    body = bytearray()
    for index in range(pairsprite.COUNT):
        for entry in (0, 1):
            body += struct.pack("<IHHI", pairsprite.WORD, pairsprite.SIZE_WORD,
                                0x1000 * entry,
                                pairsprite.ROM_BASE + pairsprite.BLOCK_START
                                + pairsprite.BLOCK_SIZE * ((index + entry) % 4))
    return bytes(body)


def test_a_synthetic_table_round_trips_record_by_record():
    body = synthetic()
    for index in range(pairsprite.COUNT):
        offset = pairsprite.STRIDE * index
        parsed = pairsprite.fields(body, offset)
        assert pairsprite.serialize(parsed) == body[offset:offset + pairsprite.STRIDE]


def test_rejects_a_record_without_the_handle_word():
    body = bytearray(synthetic())
    struct.pack_into("<I", body, 0, 0)
    assert refused(lambda: pairsprite.fields(bytes(body), 0))


def test_rejects_a_tile_pointer_outside_the_block_region():
    body = bytearray(synthetic())
    struct.pack_into("<I", body, 8, pairsprite.ROM_BASE + pairsprite.BLOCK_END)
    assert refused(lambda: pairsprite.fields(bytes(body), 0))


def test_rejects_a_record_that_is_not_the_family_stride():
    body = synthetic()
    assert refused(lambda: pairsprite.fields(body, 0, pairsprite.STRIDE - 4))


def test_the_retail_table_round_trips_and_meets_its_contract():
    rom = rom_bytes(ROM, DIGEST)
    assert pairsprite.assert_contract(rom) == pairsprite.CONTRACT
    assert pairsprite.round_trip(rom) == {"records": pairsprite.COUNT, "equal": pairsprite.COUNT,
                                          "bytes": pairsprite.EXTENT}
    assert pairsprite.extents(rom, pairsprite.FAMILY) == {
        pairsprite.FAMILY: [(pairsprite.BASE + pairsprite.STRIDE * index, pairsprite.STRIDE)
                            for index in range(pairsprite.COUNT)]}


@pytest.mark.parametrize("family", sorted(pairsprite.TABLES))
def test_every_table_round_trips_and_meets_its_contract(family):
    rom = rom_bytes(ROM, DIGEST)
    spec = pairsprite.TABLES[family]
    assert pairsprite.assert_contract(rom, family) == spec["contract"]
    assert pairsprite.round_trip(rom, family) == {
        "records": spec["count"], "equal": spec["count"],
        "bytes": spec["stride"] * spec["count"]}
    assert pairsprite.extents(rom, family) == {
        family: [(spec["base"] + spec["stride"] * index, spec["stride"])
                 for index in range(spec["count"])]}


def test_the_extent_walk_names_every_table_once():
    rom = rom_bytes(ROM, DIGEST)
    walked = pairsprite.extents(rom)
    assert sorted(walked) == sorted(pairsprite.TABLES)
    assert sum(len(rows) for rows in walked.values()) == 12
    assert sum(size for rows in walked.values() for _, size in rows) == 384


@pytest.mark.parametrize("family", sorted(pairsprite.TABLES))
def test_a_byte_permuted_table_of_every_family_no_longer_holds_a_record(family):
    rom = rom_bytes(ROM, DIGEST)
    spec = pairsprite.TABLES[family]
    start, end = spec["base"], spec["base"] + spec["stride"] * spec["count"]
    body = bytearray(rom[start:end])
    random.Random(20261021).shuffle(body)
    passing = 0
    for index in range(spec["count"]):
        try:
            pairsprite.fields(bytes(body), spec["stride"] * index, spec["stride"], family)
        except ValueError:
            continue
        passing += 1
    assert passing == 0
