from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import enemystats  # noqa: E402
import generate_mapcontainer as generator  # noqa: E402
from testkit import refused, rom_bytes  # noqa: E402

ROM = os.path.join(generator.ROOT, "baserom.gba")
STRIDE_SITES = ((0xFA16, 0x00CB), (0xFA18, 0x1A59), (0xFA1A, 0x4AB2), (0xFA1C, 0x0089),
                (0xFA1E, 0x1889), (0xFD58, 0x00D3), (0xFD5A, 0x1A9A), (0xFD5C, 0x4B04),
                (0xFD5E, 0x0092), (0xFD60, 0x18D2))
LOAD_SITES = ((0x2F502, 0x4938, enemystats.BASE), (0x3347E, 0x494E, enemystats.BASE),
              (0x304BE, 0x4A08, enemystats.BASE + 14 * enemystats.STRIDE),
              (0x392CE, 0x4A21, enemystats.BASE + 13 * enemystats.STRIDE))
HP_SITE = ((0xF700, 0x6850), (0xF706, 0x0280), (0xF708, 0x6008))
NAME = "test_the_enemy_stat_records_tile_and_round_trip"


def synthetic(fill=None):
    image = bytearray(enemystats.END + enemystats.STRIDE)
    for index in range(enemystats.COUNT):
        struct.pack_into("<I", image, enemystats.BASE + enemystats.STRIDE * index + 0x14,
                         generator.ROM_BASE + 0x10 * index)
    if fill is not None:
        image[fill] = 1
    return image


def test_the_array_tiles_its_region_and_round_trips():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    assert enemystats.assert_contract(rom) == {"records": 150, "bytes": 4200,
                                              "first": 0x711274, "last_end": 0x7122DC}
    rows = enemystats.extents(rom)[enemystats.FAMILY]
    assert len(rows) == 150
    assert (rows[0][0], rows[-1][0] + rows[-1][1]) == (0x711274, 0x7122DC)
    assert enemystats.round_trip(rom) == {"records": 150, "equal": 150, "bytes": 4200}
    assert rom[0x7122DC:0x7122DC + enemystats.STRIDE] == bytes(enemystats.STRIDE)


def test_the_stride_and_the_load_sites_are_read_at_the_bytes():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    for site, halfword in STRIDE_SITES:
        assert struct.unpack_from("<H", rom, site)[0] == halfword, hex(site)
    for site, halfword, value in LOAD_SITES:
        assert struct.unpack_from("<H", rom, site)[0] == halfword, hex(site)
        literal = ((site + 4) & ~2) + 4 * (halfword & 0xFF)
        assert struct.unpack_from("<I", rom, literal)[0] == generator.ROM_BASE | value, hex(site)
    for site, halfword in HP_SITE:
        assert struct.unpack_from("<H", rom, site)[0] == halfword, hex(site)


def test_a_record_whose_ai_pointer_is_not_a_rom_address_is_refused():
    image = synthetic()
    assert enemystats.fields(image, enemystats.BASE)["ai_node"] == generator.ROM_BASE
    struct.pack_into("<I", image, enemystats.BASE + 7 * enemystats.STRIDE + 0x14, 0x1234)
    assert refused(lambda: enemystats.fields(image, enemystats.BASE + 7 * enemystats.STRIDE))


def test_a_filled_151st_slot_is_refused():
    image = synthetic()
    assert enemystats.assert_contract(image)["records"] == 150
    assert refused(lambda: enemystats.assert_contract(synthetic(enemystats.END)))


def test_the_serializer_is_field_driven_not_a_copy():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    parsed = enemystats.fields(rom, enemystats.BASE)
    assert enemystats.serialize(parsed) == rom[enemystats.BASE:enemystats.BASE + enemystats.STRIDE]
    parsed["hp"] ^= 0x1F
    changed = enemystats.serialize(parsed)
    assert changed != rom[enemystats.BASE:enemystats.BASE + enemystats.STRIDE]
    assert [index for index in range(enemystats.STRIDE)
            if changed[index] != rom[enemystats.BASE + index]] == [0x04]


if __name__ == "__main__":
    test_the_array_tiles_its_region_and_round_trips()
    test_the_stride_and_the_load_sites_are_read_at_the_bytes()
    test_a_record_whose_ai_pointer_is_not_a_rom_address_is_refused()
    test_a_filled_151st_slot_is_refused()
    test_the_serializer_is_field_driven_not_a_copy()
    print("PASS %s" % NAME)
