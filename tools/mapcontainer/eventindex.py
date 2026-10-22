from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recordfamily  # noqa: E402

FAMILY = "event_resource_index_522"
BASE = 0x79B704
COUNT = 522
EXTENT = 4 * COUNT
END = BASE + EXTENT
POOL = 0x77C5A4
ROM_BASE = 0x08000000
ROM_END = 0x08800000


def fields(rom: bytes, offset: int, size: int = EXTENT) -> dict:
    if size != EXTENT:
        raise ValueError("%s at %#x has a %d-byte extent, not the measured %d"
                         % (FAMILY, offset, size, EXTENT))
    entries = []
    for index in range(COUNT):
        word = struct.unpack_from("<I", rom, BASE + 4 * index)[0]
        if not ROM_BASE <= word < ROM_END:
            raise ValueError("%s entry %d is %#010x, not a ROM address" % (FAMILY, index, word))
        entries.append(word)
    if entries[0] != ROM_BASE | POOL:
        raise ValueError("%s's first entry is %#010x, not the pool base %#010x"
                         % (FAMILY, entries[0], ROM_BASE | POOL))
    for index, (previous, following) in enumerate(zip(entries, entries[1:])):
        if following <= previous:
            raise ValueError("%s entries %d and %d are %#010x then %#010x, not ascending"
                             % (FAMILY, index, index + 1, previous, following))
    if entries[-1] - ROM_BASE >= BASE:
        raise ValueError("%s's last entry %#010x is not before the table" % (FAMILY, entries[-1]))
    return {"index": tuple(entries)}


def serialize(parsed: dict, size: int = EXTENT) -> bytes:
    out = bytearray()
    for word in parsed["index"]:
        out += struct.pack("<I", word)
    return recordfamily.packed(out, size, FAMILY)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return recordfamily.serialize_record(rom, family, FAMILY, offset, size, fields, serialize)


def assert_contract(rom: bytes) -> dict:
    parsed = fields(rom, BASE)
    return {"records": 1, "bytes": EXTENT, "entries": len(parsed["index"]),
            "first": BASE, "last_end": END}


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    return recordfamily.extents(rom, family, FAMILY, assert_contract, [(BASE, EXTENT)])


def round_trip(rom: bytes) -> dict[str, int]:
    return recordfamily.round_trip_one(rom, FAMILY, BASE, EXTENT, serialize_record)


if __name__ == "__main__":
    recordfamily.main(FAMILY, assert_contract, round_trip, sys.argv)
