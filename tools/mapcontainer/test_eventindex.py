from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import eventindex  # noqa: E402
import generate_mapcontainer as generator  # noqa: E402
from testkit import refused, rom_bytes  # noqa: E402

ROM = os.path.join(generator.ROOT, "baserom.gba")
HOLDERS = (0x31C0, 0x3444)
LOAD_SITES = ((0x30E8, 0x4935), (0x3118, 0x4929), (0x3156, 0x491A), (0x31A4, 0x4906),
              (0x3218, 0x498A), (0x3236, 0x4983), (0x326C, 0x4975), (0x32B0, 0x4964))
ARITHMETIC = ((0x3232, 0x1808), (0x3234, 0x6840), (0x3236, 0x4983), (0x3238, 0x0080),
              (0x323A, 0x5809))
NAME = "test_the_event_resource_index_table_tiles_and_round_trips"


def synthetic():
    image = bytearray(eventindex.END + 4)
    for index in range(eventindex.COUNT):
        struct.pack_into("<I", image, eventindex.BASE + 4 * index,
                         generator.ROM_BASE | (eventindex.POOL + 4 * index))
    return image


def test_the_table_tiles_slice_as_tail_and_round_trips():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    assert eventindex.assert_contract(rom) == {"records": 1, "bytes": 2088, "entries": 522,
                                               "first": 0x79B704, "last_end": 0x79BF2C}
    assert eventindex.extents(rom)[eventindex.FAMILY] == [(0x79B704, 2088)]
    entries = eventindex.fields(rom, eventindex.BASE)["index"]
    assert len(entries) == 522 and len(set(entries)) == 522
    assert entries[0] == generator.ROM_BASE | eventindex.POOL
    assert entries[-1] == 0x0879B6C4
    assert eventindex.round_trip(rom) == {"records": 1, "equal": 1, "bytes": 2088}


def test_the_consumer_chain_is_read_at_the_bytes():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    holders = [offset for offset in range(0, len(rom) - 4, 4)
               if struct.unpack_from("<I", rom, offset)[0] == generator.ROM_BASE | eventindex.BASE]
    assert holders == list(HOLDERS)
    for site, halfword in LOAD_SITES:
        assert struct.unpack_from("<H", rom, site)[0] == halfword, hex(site)
        literal = ((site + 4) & ~2) + 4 * (halfword & 0xFF)
        assert literal in HOLDERS, (hex(site), hex(literal))
        assert struct.unpack_from("<I", rom, literal)[0] == generator.ROM_BASE | eventindex.BASE
    for site, halfword in ARITHMETIC:
        assert struct.unpack_from("<H", rom, site)[0] == halfword, hex(site)


def test_a_non_pointer_entry_is_refused():
    image = synthetic()
    assert eventindex.assert_contract(image)["entries"] == 522
    struct.pack_into("<I", image, eventindex.BASE, 0x1000)
    assert refused(lambda: eventindex.fields(image, eventindex.BASE))


def test_a_non_ascending_pair_is_refused():
    image = synthetic()
    assert eventindex.assert_contract(image)["records"] == 1
    struct.pack_into("<I", image, eventindex.BASE + 4 * 5,
                     generator.ROM_BASE | (eventindex.POOL + 4))
    assert refused(lambda: eventindex.fields(image, eventindex.BASE))


def test_the_serializer_is_field_driven_not_a_copy():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    parsed = eventindex.fields(rom, eventindex.BASE)
    assert eventindex.serialize(parsed) == rom[eventindex.BASE:eventindex.END]
    parsed["index"] = parsed["index"][:7] + (parsed["index"][7] ^ 0x1F,) + parsed["index"][8:]
    changed = eventindex.serialize(parsed)
    assert changed != rom[eventindex.BASE:eventindex.END]
    assert [index for index in range(eventindex.EXTENT)
            if changed[index] != rom[eventindex.BASE + index]] == [28]


if __name__ == "__main__":
    test_the_table_tiles_slice_as_tail_and_round_trips()
    test_the_consumer_chain_is_read_at_the_bytes()
    test_a_non_pointer_entry_is_refused()
    test_a_non_ascending_pair_is_refused()
    test_the_serializer_is_field_driven_not_a_copy()
    print("PASS %s" % NAME)
