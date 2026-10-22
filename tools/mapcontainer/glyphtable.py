from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recordfamily  # noqa: E402

FAMILY = "endrom_glyph_table_85"
BASE = 0x757EE8
STRIDE = 8
COUNT = 85
EXTENT = STRIDE * COUNT
END = BASE + EXTENT
FIELD_COUNT = 4
BUFFER = 0x300
ROM_BASE = 0x08000000
BASE_LITERAL = 0x03037C
VRAM_LITERAL = 0x030378
VRAM_BASE = 0x06010000
CONSUMER = ((0x0803029E, 0x4F37), (0x0803029A, 0x2855), (0x080302AE, 0x2855),
            (0x080302A2, 0x00C2), (0x080302A4, 0x5ABB), (0x080302AC, 0x8853),
            (0x080302B2, 0x8893), (0x080302B6, 0x88D2), (0x08030288, 0x2203),
            (0x0803028A, 0x0212), (0x0803028C, 0xAE01), (0x080302AA, 0x54F1),
            (0x080302C0, 0x0140), (0x080302C4, 0x0C4A))
CONTRACT = {"records": COUNT, "bytes": EXTENT, "values": COUNT * FIELD_COUNT, "max": 0x2E8,
            "first": BASE, "last_end": END}

FIELDS = ("field_00", "field_02", "field_04", "field_06")


def fields(rom: bytes, offset: int, size: int = STRIDE) -> dict:
    if size != STRIDE:
        raise ValueError("%s at %#x is %d bytes, not %d" % (FAMILY, offset, size, STRIDE))
    index = (offset - BASE) // STRIDE
    parsed = {}
    for field, name in enumerate(FIELDS):
        value = struct.unpack_from("<H", rom, offset + 2 * field)[0]
        if not 0 < value < BUFFER:
            raise ValueError("%s record %d field %d is %#x, outside the consumer's %#x-byte buffer"
                             % (FAMILY, index, field, value, BUFFER))
        parsed[name] = value
    return parsed


def serialize(parsed: dict, size: int = STRIDE) -> bytes:
    return recordfamily.packed(bytearray(b"".join(struct.pack("<H", parsed[name])
                                                   for name in FIELDS)), size, FAMILY)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return recordfamily.serialize_record(rom, family, FAMILY, offset, size, fields, serialize)


def assert_contract(rom: bytes) -> dict:
    word = struct.unpack_from("<I", rom, BASE_LITERAL)[0]
    if word != ROM_BASE + BASE:
        raise ValueError("%s's base literal at file %#x is %#010x, not %#010x"
                         % (FAMILY, BASE_LITERAL, word, ROM_BASE + BASE))
    pattern = struct.pack("<I", ROM_BASE + BASE)
    hits, at = [], rom.find(pattern)
    while at != -1:
        hits.append(at)
        at = rom.find(pattern, at + 1)
    if hits != [BASE_LITERAL]:
        raise ValueError("%s's base word occurs at %s, not once at file %#x"
                         % (FAMILY, ["%#x" % hit for hit in hits], BASE_LITERAL))
    vram = struct.unpack_from("<I", rom, VRAM_LITERAL)[0]
    if vram != VRAM_BASE:
        raise ValueError("%s's VRAM literal at file %#x is %#010x, not %#010x"
                         % (FAMILY, VRAM_LITERAL, vram, VRAM_BASE))
    for address, halfword in CONSUMER:
        got = struct.unpack_from("<H", rom, address - ROM_BASE)[0]
        if got != halfword:
            raise ValueError("%s's consumer instruction at %#010x is %#06x, not %#06x"
                             % (FAMILY, address, got, halfword))
    values = [value for index in range(COUNT)
              for value in fields(rom, BASE + STRIDE * index).values()]
    measured = {"records": COUNT, "bytes": EXTENT, "values": len(values), "max": max(values),
                "first": BASE, "last_end": END}
    if measured != CONTRACT:
        raise ValueError("%s measures %s, the contract says %s" % (FAMILY, measured, CONTRACT))
    return measured


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    return recordfamily.extents(rom, family, FAMILY, assert_contract,
                                [(BASE + STRIDE * index, STRIDE) for index in range(COUNT)])


def round_trip(rom: bytes) -> dict[str, int]:
    return recordfamily.round_trip(rom, FAMILY, BASE, STRIDE, COUNT, serialize_record)


if __name__ == "__main__":
    recordfamily.main(FAMILY, assert_contract, round_trip, sys.argv)
