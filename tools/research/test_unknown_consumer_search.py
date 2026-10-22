import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import unknown_consumer_search as search  # noqa: E402

RANGE = (0x1000, 0x1100)


def image() -> bytes:
    rom = bytearray(0x1400)
    struct.pack_into("<H", rom, 0x100, 0x4800 | 0x3F)
    struct.pack_into("<I", rom, 0x200, 0x08001000)
    struct.pack_into("<I", rom, 0x300, 0x08001040)
    struct.pack_into("<I", rom, 0x1000, 0x08001080)
    return bytes(rom)


def test_a_pc_relative_loader_is_found_with_its_literal():
    targets = search.loader_targets(image())
    assert targets[0x200] == (0x100,)


def test_a_literal_loaded_once_is_a_singleton_and_twice_is_a_cluster():
    one = search.loaders(image(), *RANGE)
    assert (one["loaders"], one["literals"], one["multi"]) == (1, 1, 0)
    rom = bytearray(image())
    struct.pack_into("<H", rom, 0x110, 0x4800 | 0x3B)
    twice = search.loaders(bytes(rom), *RANGE)
    assert (twice["loaders"], twice["literals"], twice["multi"], twice["largest"]) == (2, 1, 1, 2)


def test_direct_splits_the_word_inside_the_range_from_the_words_outside_it():
    hit = search.direct(image(), *RANGE)
    assert (hit["inside"], hit["outside"]) == (1, 2)
    assert sorted(site for site, _ in hit["sites"]) == [0x200, 0x300]


def test_shape_classifies_a_zero_an_iwram_pointer_and_a_rom_pointer():
    rom = bytearray(image())
    struct.pack_into("<I", rom, 0x1004, 0x03000100)
    struct.pack_into("<I", rom, 0x1008, 0x08001000)
    counts = search.shape(bytes(rom), 0x1000, 0x100C)
    assert (counts["words"], counts["rom"], counts["iwram"]) == (3, 2, 1)


def test_controls_are_measured_somewhere_other_than_the_range():
    rows = search.control_loaders(image(), 0x100, count=3, stride=0x40)
    assert len(rows) == 3
    assert all(0 <= row["start"] < 0x1400 for row in rows)
