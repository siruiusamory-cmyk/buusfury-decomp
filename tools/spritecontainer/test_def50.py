from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "mapcontainer"))

import def50  # noqa: E402
import generate_mapcontainer as generator  # noqa: E402
import spritefamily  # noqa: E402
from testkit import refused, rom_bytes  # noqa: E402

ROM = os.path.join(generator.ROOT, "baserom.gba")
TABLE_LITERAL = 0x3C0
TABLE_LDR = (0x15E, 0x4998)
READERS = ((0xECE4, 0x6D12), (0xEBB6, 0x6D30))
SCALE_AT = (0xECDC, 0x0089)
ARRAYS = ((0x46D354, 40), (0x4ADD90, 72), (0x4BA3B4, 80), (0x51C898, 88), (0x527A7C, 88),
          (0x532DCC, 80), (0x597DF0, 52), (0x5BFC84, 20), (0x6681EC, 88), (0x674384, 88))
GRIDS = ((0x46D2EC, 104), (0x4ADD30, 96), (0x4BA1FC, 440), (0x51C618, 640), (0x52781C, 608),
         (0x532C1C, 432), (0x597DB0, 64), (0x5BFC44, 64), (0x667F64, 648), (0x674154, 560))
NAME = "test_the_def50_arrays_tile_and_round_trip"


def synthetic(pointer):
    image = bytearray(spritefamily.TABLE_END + 4)
    for index in range(spritefamily.COUNT):
        struct.pack_into("<I", image, spritefamily.TABLE + 4 * index,
                         generator.ROM_BASE | spritefamily.DEFINITION_START)
    image[spritefamily.DEFINITION_START] = 2
    struct.pack_into("<I", image, spritefamily.DEFINITION_START + def50.ARRAY_AT, pointer)
    return image


def test_the_arrays_tile_and_round_trip():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    assert def50.assert_contract(rom) == {"arrays": 10, "slots": 174, "bytes": 696, "grids": 126,
                                          "frames": 457, "grid_bytes": 3656}
    rows = def50.extents(rom)[def50.FAMILY]
    assert rows == list(ARRAYS)
    assert def50.round_trip(rom) == {"records": 10, "equal": 10, "bytes": 696}
    for definition, array in def50.arrays(rom):
        assert (array, 4 * rom[definition]) in rows


def test_the_cell_grids_are_eight_bytes_per_animation_frame():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    rows = def50.extents(rom)[def50.CELL_FAMILY]
    assert len(rows) == 126 and sum(size for _, size in rows) == 3656
    assert def50.round_trip_cells(rom) == {"records": 126, "equal": 126, "bytes": 3656}
    for definition, array in def50.arrays(rom):
        body = sorted((grid, 8 * frames) for grid, site, _slot, frames in def50.grids(rom)
                      if site == definition)
        assert body[0][0] == next(start for start, size in GRIDS if start + size == array)
    for grid, _definition, _slot, frames in def50.grids(rom):
        assert (grid, 8 * frames) in rows
        assert def50.cell_fields(rom, grid, 8 * frames)["frame_count"] == frames
    grid, _definition, _slot, frames = def50.grids(rom)[0]
    assert (grid, 8 * frames) == (0x46D2EC, 16)
    assert refused(lambda: def50.cell_fields(rom, grid, 8 * frames + 8))
    assert refused(lambda: def50.cell_fields(rom, ARRAYS[0][0], ARRAYS[0][1]))


def test_the_cell_serializer_is_field_driven_not_a_copy():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    offset, size = 0x46D2EC, 16
    parsed = def50.cell_fields(rom, offset, size)
    assert def50.serialize_cells(parsed, size) == rom[offset:offset + size]
    cells = list(parsed["cells"])
    cells[3] = (cells[3][0] ^ 0x7F, cells[3][1])
    parsed["cells"] = tuple(cells)
    changed = def50.serialize_cells(parsed, size)
    assert changed != rom[offset:offset + size]
    assert [index for index in range(size) if changed[index] != rom[offset + index]] == [6]


def test_the_consumer_chain_is_read_at_the_bytes():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    site, halfword = TABLE_LDR
    assert struct.unpack_from("<H", rom, site)[0] == halfword
    literal = ((site + 4) & ~2) + 4 * (halfword & 0xFF)
    assert literal == TABLE_LITERAL
    assert struct.unpack_from("<I", rom, literal)[0] == generator.ROM_BASE | spritefamily.TABLE
    for reader, halfword in READERS:
        assert struct.unpack_from("<H", rom, reader)[0] == halfword, hex(reader)
    assert struct.unpack_from("<H", rom, SCALE_AT[0])[0] == SCALE_AT[1]


def test_a_function_pointer_that_is_not_a_rom_address_is_refused():
    assert len(def50.arrays(synthetic(generator.ROM_BASE | 0x6A8000))) == spritefamily.COUNT
    assert refused(lambda: def50.arrays(synthetic(0x1234)))


def test_the_serializer_is_field_driven_not_a_copy():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    offset, size = ARRAYS[0]
    parsed = def50.fields(rom, offset, size)
    assert def50.serialize(parsed, size) == rom[offset:offset + size]
    parsed["slots"] = parsed["slots"][:2] + (parsed["slots"][2] ^ 0x1F,) + parsed["slots"][3:]
    changed = def50.serialize(parsed, size)
    assert changed != rom[offset:offset + size]
    assert [index for index in range(size) if changed[index] != rom[offset + index]] == [8]


if __name__ == "__main__":
    test_the_arrays_tile_and_round_trip()
    test_the_cell_grids_are_eight_bytes_per_animation_frame()
    test_the_cell_serializer_is_field_driven_not_a_copy()
    test_the_consumer_chain_is_read_at_the_bytes()
    test_a_function_pointer_that_is_not_a_rom_address_is_refused()
    test_the_serializer_is_field_driven_not_a_copy()
    print("PASS %s" % NAME)
