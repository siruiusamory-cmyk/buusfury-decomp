from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recordfamily  # noqa: E402

FAMILY = "endrom_bank_table_155"
BASE = 0x6F393C
TABLE = 0x6F395C
COUNT = 155
ZERO_WORDS = 8
END = TABLE + 4 * COUNT
EXTENT = END - BASE
ROM_BASE = 0x08000000
ROM_END = 0x08800000


def fields(rom: bytes, offset: int, size: int = EXTENT) -> dict:
    if size != EXTENT:
        raise ValueError("%s at %#x has a %d-byte extent, not the measured %d"
                         % (FAMILY, offset, size, EXTENT))
    zeros = tuple(struct.unpack_from("<I", rom, offset + 4 * index)[0]
                  for index in range(ZERO_WORDS))
    if any(zeros):
        raise ValueError("%s at %#x holds %s in its zero run" % (FAMILY, offset, zeros))
    bank = []
    for index in range(COUNT):
        word = struct.unpack_from("<I", rom, TABLE + 4 * index)[0]
        if not ROM_BASE <= word < ROM_END:
            raise ValueError("%s word %d is %#010x, not a ROM address" % (FAMILY, index, word))
        bank.append(word)
    if len(set(bank)) != COUNT:
        raise ValueError("%s names %d distinct words of %d" % (FAMILY, len(set(bank)), COUNT))
    return {"zeros": zeros, "bank": tuple(bank)}


def serialize(parsed: dict, size: int = EXTENT) -> bytes:
    out = bytearray()
    for zero in parsed["zeros"]:
        out += struct.pack("<I", zero)
    if len(out) != 4 * ZERO_WORDS:
        raise ValueError("%s's zero run is %d bytes" % (FAMILY, len(out)))
    for word in parsed["bank"]:
        out += struct.pack("<I", word)
    return recordfamily.packed(out, size, FAMILY)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return recordfamily.serialize_record(rom, family, FAMILY, offset, size, fields, serialize)


def assert_contract(rom: bytes) -> dict:
    parsed = fields(rom, BASE)
    return {"records": 1, "bytes": EXTENT, "words": len(parsed["bank"]),
            "first": BASE, "last_end": END}


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    return recordfamily.extents(rom, family, FAMILY, assert_contract, [(BASE, EXTENT)])


def round_trip(rom: bytes) -> dict[str, int]:
    return recordfamily.round_trip_one(rom, FAMILY, BASE, EXTENT, serialize_record)
