from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recordfamily  # noqa: E402
from mapcontainer import PointerRule, WordRule  # noqa: E402

FAMILY = "enemy_stat_record"
BASE = 0x711274
STRIDE = 0x1C
COUNT = 150
END = BASE + STRIDE * COUNT
ROM_BASE = 0x08000000
ROM_END = 0x08800000

FIELDS = (WordRule("word_00"), WordRule("hp"), WordRule("word_08"), WordRule("word_0c"),
          WordRule("word_10"), PointerRule("ai_node"), WordRule("word_18"))


def fields(rom: bytes, offset: int, size: int = STRIDE) -> dict:
    if size != STRIDE:
        raise ValueError("%s at %#x is %d bytes, its stride is %d"
                         % (FAMILY, offset, size, STRIDE))
    parsed = {}
    cursor = 0
    for rule in FIELDS:
        value = struct.unpack_from("<I", rom, offset + cursor)[0]
        if isinstance(rule, PointerRule) and not ROM_BASE <= value < ROM_END:
            raise ValueError("%s at %#x %s is %#010x, not a ROM address"
                             % (FAMILY, offset, rule.name, value))
        parsed[rule.name] = value
        cursor += 4
    return parsed


def serialize(parsed: dict, size: int = STRIDE) -> bytes:
    out = bytearray()
    for rule in FIELDS:
        out += struct.pack("<I", parsed[rule.name])
    return recordfamily.packed(out, size, FAMILY)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return recordfamily.serialize_record(rom, family, FAMILY, offset, size, fields, serialize)


def assert_contract(rom: bytes) -> dict:
    for index in range(COUNT):
        fields(rom, BASE + STRIDE * index)
    if rom[END:END + STRIDE] != bytes(STRIDE):
        raise ValueError("%s ends at %#x, whose %d bytes are not the empty padding"
                         % (FAMILY, END, STRIDE))
    return {"records": COUNT, "bytes": COUNT * STRIDE, "first": BASE, "last_end": END}


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    return recordfamily.extents(rom, family, FAMILY, assert_contract,
                                [(BASE + STRIDE * index, STRIDE) for index in range(COUNT)])


def round_trip(rom: bytes) -> dict[str, int]:
    return recordfamily.round_trip(rom, FAMILY, BASE, STRIDE, COUNT, serialize_record)


if __name__ == "__main__":
    image = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gba", "rb").read()
    print("%s measure %s" % (FAMILY, assert_contract(image)))
    print("%s verify  round trip %s" % (FAMILY, round_trip(image)))
