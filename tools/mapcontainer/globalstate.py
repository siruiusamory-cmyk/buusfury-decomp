from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recordfamily  # noqa: E402

FAMILY = "global_state_pointer_table"
BASE = 0x6FC238
IWRAM_COUNT = 6
ROM_COUNT = 4
COUNT = IWRAM_COUNT + ROM_COUNT
EXTENT = 4 * COUNT
END = BASE + EXTENT
IWRAM_BASE = 0x03000000
IWRAM_END = 0x03008000
ROM_BASE = 0x08000000
ROM_END = 0x08800000


def fields(rom: bytes, offset: int, size: int = EXTENT) -> dict:
    if size != EXTENT:
        raise ValueError("%s at %#x has a %d-byte extent, not the measured %d"
                         % (FAMILY, offset, size, EXTENT))
    iwram = []
    for index in range(IWRAM_COUNT):
        word = struct.unpack_from("<I", rom, BASE + 4 * index)[0]
        if not IWRAM_BASE <= word < IWRAM_END:
            raise ValueError("%s word %d is %#010x, not an IWRAM address" % (FAMILY, index, word))
        iwram.append(word)
    table = []
    for index in range(IWRAM_COUNT, COUNT):
        word = struct.unpack_from("<I", rom, BASE + 4 * index)[0]
        if not ROM_BASE <= word < ROM_END:
            raise ValueError("%s word %d is %#010x, not a ROM address" % (FAMILY, index, word))
        table.append(word)
    for index, (previous, following) in enumerate(zip(table, table[1:])):
        if following <= previous:
            raise ValueError("%s's ROM words %d and %d are %#010x then %#010x, not ascending"
                             % (FAMILY, index, index + 1, previous, following))
    after = struct.unpack_from("<I", rom, END)[0]
    if IWRAM_BASE <= after < IWRAM_END or ROM_BASE <= after < ROM_END:
        raise ValueError("%s ends at %#x, whose word is %#010x, still a pointer"
                         % (FAMILY, END, after))
    return {"iwram": tuple(iwram), "rom": tuple(table)}


def serialize(parsed: dict, size: int = EXTENT) -> bytes:
    out = bytearray()
    for word in parsed["iwram"]:
        out += struct.pack("<I", word)
    for word in parsed["rom"]:
        out += struct.pack("<I", word)
    return recordfamily.packed(out, size, FAMILY)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return recordfamily.serialize_record(rom, family, FAMILY, offset, size, fields, serialize)


def assert_contract(rom: bytes) -> dict:
    parsed = fields(rom, BASE)
    return {"records": 1, "bytes": EXTENT, "iwram": len(parsed["iwram"]),
            "rom": len(parsed["rom"]), "first": BASE, "last_end": END}


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    return recordfamily.extents(rom, family, FAMILY, assert_contract, [(BASE, EXTENT)])


def round_trip(rom: bytes) -> dict[str, int]:
    return recordfamily.round_trip_one(rom, FAMILY, BASE, EXTENT, serialize_record)


if __name__ == "__main__":
    recordfamily.main(FAMILY, assert_contract, round_trip, sys.argv)
