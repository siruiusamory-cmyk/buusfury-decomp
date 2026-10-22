from __future__ import annotations

import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import cellmap
import pytest
from testkit import refused, rom_bytes

ROM = os.path.join(os.path.dirname(os.path.dirname(HERE)), "baserom.gba")
DIGEST = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"


def synthetic():
    body = bytearray()
    for index in range(cellmap.COUNT):
        for field in range(len(cellmap.FIELDS)):
            body += struct.pack("<I", 0x17 + (index * len(cellmap.FIELDS) + field) % 0x1C0)
    return bytes(body)


def test_a_synthetic_table_round_trips_record_by_record():
    body = synthetic()
    for index in range(cellmap.COUNT):
        offset = cellmap.STRIDE * index
        parsed = cellmap.fields(body, offset)
        assert cellmap.serialize(parsed) == body[offset:offset + cellmap.STRIDE]


def test_a_cell_offsets_field_outside_the_block_is_refused():
    body = bytearray(synthetic())
    struct.pack_into("<I", body, 8, cellmap.BLOCK)
    assert refused(lambda: cellmap.fields(bytes(body), 0))


def test_a_record_that_is_not_the_family_stride_is_refused():
    body = synthetic()
    assert refused(lambda: cellmap.fields(body, 0, cellmap.STRIDE - 4))


def test_the_retail_table_round_trips_and_meets_its_contract():
    rom = rom_bytes(ROM, DIGEST)
    assert cellmap.assert_contract(rom) == cellmap.CONTRACT
    assert cellmap.round_trip(rom) == {"records": cellmap.COUNT, "equal": cellmap.COUNT,
                                       "bytes": cellmap.EXTENT}
    assert cellmap.extents(rom) == {cellmap.FAMILY:
                                    [(cellmap.BASE + cellmap.STRIDE * index, cellmap.STRIDE)
                                     for index in range(cellmap.COUNT)]}


def test_a_byte_permuted_row_no_longer_fits_the_block():
    rom = rom_bytes(ROM, DIGEST)
    body = bytearray(rom[cellmap.BASE:cellmap.END])
    random.Random(20261019).shuffle(body)
    passing = 0
    for index in range(cellmap.COUNT):
        try:
            cellmap.fields(bytes(body), cellmap.STRIDE * index)
        except ValueError:
            continue
        passing += 1
    assert passing == 0
