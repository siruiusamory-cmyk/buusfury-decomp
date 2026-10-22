from __future__ import annotations

import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import endromfacing
import pytest
from testkit import refused, rom_bytes

ROM = os.path.join(os.path.dirname(os.path.dirname(HERE)), "baserom.gba")
DIGEST = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"


def synthetic():
    body = bytearray()
    for dx, dy in endromfacing.VECTORS:
        body += struct.pack("<ii", dx, dy)
    return bytes(body)


def test_a_synthetic_table_round_trips_record_by_record():
    body = synthetic()
    for index in range(endromfacing.COUNT):
        offset = endromfacing.STRIDE * index
        parsed = endromfacing.fields(body, offset)
        assert endromfacing.serialize(parsed) == body[offset:offset + endromfacing.STRIDE]


def test_rejects_a_pair_that_is_not_a_facing_vector():
    body = bytearray(synthetic())
    struct.pack_into("<ii", body, 0, 2, 0)
    assert refused(lambda: endromfacing.fields(bytes(body), 0))


def test_rejects_a_record_that_is_not_the_family_stride():
    body = synthetic()
    assert refused(lambda: endromfacing.fields(body, 0, endromfacing.STRIDE + 4))


def test_the_retail_table_round_trips_and_meets_its_contract():
    rom = rom_bytes(ROM, DIGEST)
    assert endromfacing.assert_contract(rom) == endromfacing.CONTRACT
    assert endromfacing.round_trip(rom) == {"records": endromfacing.COUNT,
                                            "equal": endromfacing.COUNT,
                                            "bytes": endromfacing.STRIDE * endromfacing.COUNT}
    assert endromfacing.extents(rom) == {
        endromfacing.FAMILY: [(endromfacing.BASE + endromfacing.STRIDE * index,
                               endromfacing.STRIDE) for index in range(endromfacing.COUNT)]}


def test_the_index_bound_is_the_sibling_table_and_not_a_guess():
    rom = rom_bytes(ROM, DIGEST)
    import pairsprite
    assert pairsprite.assert_contract(rom)["records"] == endromfacing.COUNT


def test_a_word_permuted_table_no_longer_holds_the_facing_order():
    rom = rom_bytes(ROM, DIGEST)
    body = bytearray(rom[endromfacing.BASE:endromfacing.END])
    words = [body[index:index + 4] for index in range(0, len(body), 4)]
    random.Random(20261021).shuffle(words)
    shuffled = b"".join(words)
    pairs = []
    for index in range(endromfacing.COUNT):
        pairs.append(struct.unpack_from("<ii", shuffled, endromfacing.STRIDE * index))
    assert pairs != list(endromfacing.VECTORS)
