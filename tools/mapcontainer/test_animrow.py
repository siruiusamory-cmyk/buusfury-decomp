from __future__ import annotations

import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import animrow
import pytest
from testkit import refused, rom_bytes

ROM = os.path.join(os.path.dirname(os.path.dirname(HERE)), "baserom.gba")
DIGEST = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"


def synthetic(count=3):
    body = bytearray(struct.pack("<BBH", count, 0x19, 0x0367))
    body += b"".join(struct.pack("<I", 0x0817BCCC + 4 * index) for index in range(count))
    return bytes(body)


def test_a_synthetic_row_round_trips():
    body = synthetic()
    parsed = animrow.fields(body, 0)
    assert parsed == {"frame_count": 3, "vram_units": 0x19, "vram_slot": 0x0367,
                      "frame": (0x0817BCCC, 0x0817BCD0, 0x0817BCD4)}
    assert animrow.serialize(parsed) == body


def test_a_count_outside_the_population_is_refused():
    assert refused(lambda: animrow.fields(synthetic(0), 0))
    assert refused(lambda: animrow.fields(synthetic(animrow.MAX_FRAMES + 1), 0))


def test_a_frame_pointer_outside_the_image_is_refused():
    body = bytearray(synthetic())
    struct.pack_into("<I", body, 4, 0x1000)
    assert refused(lambda: animrow.fields(bytes(body), 0))


def test_a_size_that_is_not_the_row_extent_is_refused():
    assert refused(lambda: animrow.fields(synthetic(), 12))


def test_the_retail_population_and_the_emitted_rows_meet_their_contract():
    rom = rom_bytes(ROM, DIGEST)
    assert animrow.assert_contract(rom)["problems"] == []
    assert (len(animrow.sites(rom)), sum(animrow.sites(rom).values())) == (431, 12824)
    assert (len(animrow.free(rom)), sum(animrow.free(rom).values())) == (122, 3500)


def test_a_permuted_row_no_longer_parses_to_the_same_record():
    rom = rom_bytes(ROM, DIGEST)
    offsets = sorted(animrow.free(rom))
    random.Random(20261020).shuffle(offsets)
    same = 0
    for offset in offsets[:40]:
        body = bytearray(rom[offset:offset + animrow.free(rom)[offset]])
        random.Random(20261020 + offset).shuffle(body)
        try:
            parsed = animrow.fields(bytes(body), 0)
            animrow.serialize(parsed)
        except ValueError:
            continue
        if bytes(body) == animrow.serialize(parsed) and bytes(body) == rom[offset:offset + len(body)]:
            same += 1
    assert same == 0
