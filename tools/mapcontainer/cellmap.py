from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recordfamily  # noqa: E402

FAMILY = "endrom_cell_map_table"
BASE = 0x7198E4
STRIDE = 16
COUNT = 0x35
EXTENT = STRIDE * COUNT
END = BASE + EXTENT
BLOCK = 0x200
ROM_BASE = 0x08000000
BASE_LITERAL = 0x0197AC
CONSUMER = ((0x080196D6, 0xAD01), (0x080196E8, 0x4F30), (0x080196EA, 0x2101),
            (0x080196EC, 0x0102), (0x080196EE, 0x58BB), (0x080196F0, 0x19D2),
            (0x080196F2, 0x54E9), (0x080196F4, 0x6853), (0x080196F6, 0x3001),
            (0x080196F8, 0x54E9), (0x080196FA, 0x6893), (0x080196FC, 0x2835),
            (0x080196FE, 0x54E9), (0x08019700, 0x68D2), (0x08019702, 0x54A9),
            (0x08019704, 0xDBF2), (0x08019716, 0xB07F), (0x08019718, 0xB002))

FIELDS = ("cell_00", "cell_04", "cell_08", "cell_0c")
CONTRACT = {"records": COUNT, "bytes": EXTENT, "values": COUNT * len(FIELDS), "min": 0x17,
            "max": 0x1E8, "distinct": COUNT * len(FIELDS), "first": BASE, "last_end": END}


def fields(rom: bytes, offset: int, size: int = STRIDE) -> dict:
    if size != STRIDE:
        raise ValueError("%s at %#x is %d bytes, not %d" % (FAMILY, offset, size, STRIDE))
    parsed = {}
    for index, name in enumerate(FIELDS):
        value = struct.unpack_from("<I", rom, offset + 4 * index)[0]
        if value >= BLOCK:
            raise ValueError("%s at %#x %s is %#x, outside the consumer's %#x-byte block"
                             % (FAMILY, offset, name, value, BLOCK))
        parsed[name] = value
    return parsed


def serialize(parsed: dict, size: int = STRIDE) -> bytes:
    return recordfamily.packed(bytearray(b"".join(struct.pack("<I", parsed[name])
                                                  for name in FIELDS)), size, FAMILY)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return recordfamily.serialize_record(rom, family, FAMILY, offset, size, fields, serialize)


def assert_contract(rom: bytes) -> dict:
    recordfamily.base_word(rom, FAMILY, BASE_LITERAL, ROM_BASE + BASE)
    recordfamily.consumer_pins(rom, FAMILY, [(address - ROM_BASE, halfword)
                                             for address, halfword in CONSUMER])
    values = [value for index in range(COUNT)
              for value in fields(rom, BASE + STRIDE * index).values()]
    return recordfamily.held_contract(
        {"records": COUNT, "bytes": EXTENT, "values": len(values), "min": min(values),
         "max": max(values), "distinct": len(set(values)), "first": BASE, "last_end": END},
        CONTRACT, FAMILY)


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    return recordfamily.extents(rom, family, FAMILY, assert_contract,
                                [(BASE + STRIDE * index, STRIDE) for index in range(COUNT)])


def round_trip(rom: bytes) -> dict[str, int]:
    return recordfamily.round_trip(rom, FAMILY, BASE, STRIDE, COUNT, serialize_record)


if __name__ == "__main__":
    recordfamily.main(FAMILY, assert_contract, round_trip, sys.argv)
