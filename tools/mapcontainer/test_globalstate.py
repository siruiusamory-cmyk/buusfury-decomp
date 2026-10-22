from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import generate_mapcontainer as generator  # noqa: E402
import globalstate  # noqa: E402
from testkit import refused, rom_bytes  # noqa: E402

ROM = os.path.join(generator.ROOT, "baserom.gba")
HOLDERS = ((0x17E54, 0), (0x18268, 4), (0x1838C, 4))
LOADS = ((0x17C6A, 0x487A), (0x17EC4, 0x4DE8), (0x182BC, 0x4833))
NAME = "test_the_global_state_pointer_table_is_read_and_tiles"


def synthetic(fill=None):
    image = bytearray(globalstate.END + 4)
    for index in range(globalstate.IWRAM_COUNT):
        struct.pack_into("<I", image, globalstate.BASE + 4 * index, 0x03001000 + 4 * index)
    for index in range(globalstate.ROM_COUNT):
        struct.pack_into("<I", image, globalstate.BASE + 4 * (globalstate.IWRAM_COUNT + index),
                         generator.ROM_BASE + 0x1000 + 4 * index)
    struct.pack_into("<I", image, globalstate.END, 0x02040808)
    if fill is not None:
        struct.pack_into("<I", image, fill[0], fill[1])
    return image


def test_the_table_is_two_runs_and_round_trips():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    assert globalstate.assert_contract(rom) == {"records": 1, "bytes": 40, "iwram": 6, "rom": 4,
                                                "first": 0x6FC238, "last_end": 0x6FC260}
    assert globalstate.extents(rom)[globalstate.FAMILY] == [(0x6FC238, 40)]
    parsed = globalstate.fields(rom, globalstate.BASE)
    assert parsed["iwram"] == (0x030019A4, 0x03003898, 0x03001C4C, 0x03001068, 0x030019A4,
                               0x03002A64)
    assert parsed["rom"] == (0x086FC260, 0x086FC378, 0x086FC790, 0x086FC8A8)
    assert globalstate.round_trip(rom) == {"records": 1, "equal": 1, "bytes": 40}


def test_the_consumer_chain_is_read_at_the_bytes():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    for holder, word_index in HOLDERS:
        value = struct.unpack_from("<I", rom, holder)[0]
        assert value == generator.ROM_BASE | (globalstate.BASE + word_index), hex(holder)
    for site, halfword in LOADS:
        assert struct.unpack_from("<H", rom, site)[0] == halfword, hex(site)
        literal = ((site + 4) & ~2) + 4 * (halfword & 0xFF)
        assert literal in [holder for holder, _ in HOLDERS], hex(site)
    named = []
    for offset in range(0, len(rom) - 4, 4):
        word = struct.unpack_from("<I", rom, offset)[0]
        if generator.ROM_BASE | globalstate.BASE <= word <= generator.ROM_BASE | (
                globalstate.BASE + 4 * (globalstate.COUNT - 1)):
            named.append((offset, word - generator.ROM_BASE - globalstate.BASE))
    assert sorted(named) == sorted(HOLDERS), named


def test_a_word_class_break_is_refused():
    image = synthetic()
    assert globalstate.assert_contract(image)["records"] == 1
    assert refused(lambda: globalstate.fields(synthetic((globalstate.BASE, 0x08001000)),
                                              globalstate.BASE))
    assert refused(lambda: globalstate.fields(
        synthetic((globalstate.BASE + 4 * globalstate.IWRAM_COUNT, 0x03001000)), globalstate.BASE))


def test_a_run_that_does_not_end_on_a_non_pointer_is_refused():
    image = synthetic()
    assert globalstate.fields(image, globalstate.BASE)["rom"][0] == 0x08001000
    assert refused(lambda: globalstate.fields(synthetic((globalstate.END, 0x03001000)),
                                              globalstate.BASE))


def test_the_serializer_is_field_driven_not_a_copy():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    parsed = globalstate.fields(rom, globalstate.BASE)
    assert globalstate.serialize(parsed) == rom[globalstate.BASE:globalstate.END]
    parsed["rom"] = parsed["rom"][:2] + (parsed["rom"][2] ^ 0x1F,) + parsed["rom"][3:]
    changed = globalstate.serialize(parsed)
    assert changed != rom[globalstate.BASE:globalstate.END]
    assert [index for index in range(globalstate.EXTENT)
            if changed[index] != rom[globalstate.BASE + index]] == [4 * 8]


if __name__ == "__main__":
    test_the_table_is_two_runs_and_round_trips()
    test_the_consumer_chain_is_read_at_the_bytes()
    test_a_word_class_break_is_refused()
    test_a_run_that_does_not_end_on_a_non_pointer_is_refused()
    test_the_serializer_is_field_driven_not_a_copy()
    print("PASS %s" % NAME)
