from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import ainodes  # noqa: E402
import generate_mapcontainer as generator  # noqa: E402
from testkit import refused, rom_bytes  # noqa: E402

ROM = os.path.join(generator.ROOT, "baserom.gba")
LITERAL = 0xAB50
LOADER = 0xAA50
LOADER_HALFWORD = 0x493F
NAME = "test_the_ai_behaviour_node_family_tiles_and_round_trips"


def synthetic():
    image = bytearray(ainodes.ROW_END + 0x1000)
    nodes = [0x1000, 0x100C] + [0x1020 + 0x10 * index
                                for index in range(ainodes.ROW_TARGETS - 2)]
    for index in range(ainodes.ROW_WORDS):
        struct.pack_into("<I", image, ainodes.ROW_TABLE + 4 * index,
                         generator.ROM_BASE + nodes[index % len(nodes)])
    return image, nodes


def test_the_family_tiles_its_extent_and_round_trips():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    assert ainodes.assert_contract(rom) == ainodes.CONTRACT
    rows = ainodes.rows(rom)
    assert len(rows) == 2505
    assert sum(size for _, size in rows) == 53168
    assert rows[0] == (0x716F4, 16), rows[0]
    assert ainodes.round_trip(rom) == {"records": 2505, "equal": 2505, "bytes": 53168}
    assert len({offset for offset, _ in rows}) == len(rows)


def test_the_row_table_is_the_consumer_read_at_the_bytes():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    assert struct.unpack_from("<I", rom, LITERAL)[0] == generator.ROM_BASE | ainodes.ROW_TABLE
    halfword = struct.unpack_from("<H", rom, LOADER)[0]
    assert halfword == LOADER_HALFWORD
    assert ((LOADER + 4) & ~2) + 4 * (halfword & 0xFF) == LITERAL
    rows = dict(ainodes.rows(rom))
    words = [struct.unpack_from("<I", rom, ainodes.ROW_TABLE + 4 * index)[0]
             for index in range(ainodes.ROW_WORDS)]
    assert all(words)
    assert len({word - generator.ROM_BASE for word in words}) == ainodes.ROW_TARGETS
    assert (words[0] - generator.ROM_BASE, 16) in rows.items()
    assert not [offset for offset, _ in rows.items()
                if ainodes.ROW_TABLE < offset + 16 and offset < ainodes.ROW_END]


def test_a_row_table_word_that_is_not_a_pointer_is_refused():
    image, _ = synthetic()
    assert len(ainodes.row_targets(image)) == ainodes.ROW_TARGETS
    struct.pack_into("<I", image, ainodes.ROW_TABLE + 4 * 7, 0)
    assert refused(lambda: ainodes.row_targets(image))


def test_two_records_that_share_a_byte_are_refused():
    image, nodes = synthetic()
    assert len(ainodes.rows(image)) == ainodes.ROW_TARGETS
    assert any(size == ainodes.PARAMLESS_LEAF for _, size in ainodes.rows(image))
    struct.pack_into("<III", image, nodes[0], 0x08018F91, 0x0801900B, 0x08019043)
    struct.pack_into("<I", image, nodes[0] + 0x0C, 4)
    assert refused(lambda: ainodes.rows(image))


def test_the_serializer_is_field_driven_not_a_copy():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    offset, size = next((offset, size) for offset, size in ainodes.rows(rom)
                        if size == ainodes.LEAF)
    parsed = ainodes.fields(rom, offset, size)
    assert ainodes.serialize(parsed, size) == rom[offset:offset + size]
    parsed["param"] ^= 0x1F
    changed = ainodes.serialize(parsed, size)
    assert changed != rom[offset:offset + size]
    assert [index for index in range(size) if changed[index] != rom[offset + index]] == [0x0C]
    composite = next((offset, size) for offset, size in ainodes.rows(rom)
                     if size > ainodes.LEAF)
    parsed = ainodes.fields(rom, composite[0], composite[1])
    assert ainodes.serialize(parsed, composite[1]) == rom[composite[0]:composite[0] + composite[1]]
    assert len(parsed["children"]) == (composite[1] - ainodes.PREFIX) // 4


if __name__ == "__main__":
    test_the_family_tiles_its_extent_and_round_trips()
    test_the_row_table_is_the_consumer_read_at_the_bytes()
    test_a_row_table_word_that_is_not_a_pointer_is_refused()
    test_two_records_that_share_a_byte_are_refused()
    test_the_serializer_is_field_driven_not_a_copy()
    print("PASS %s" % NAME)
