from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recordfamily  # noqa: E402
from mapcontainer import PairRule, PointerRule, WordRule  # noqa: E402

FAMILY = "endrom_44_record"
BASE = 0x6F82EC
STRIDE = 44
COUNT = 162
ARRAY_END = BASE + STRIDE * COUNT
ROM_BASE = 0x08000000
ROM_END = 0x08800000

FIELDS = (PairRule("id"),
          PairRule("id_next"),
          WordRule("word_04"),
          WordRule("word_08"),
          WordRule("word_0c"),
          PointerRule("container"),
          WordRule("word_14"),
          WordRule("word_18"),
          WordRule("word_1c"),
          WordRule("word_20"),
          WordRule("word_24"),
          WordRule("word_28"))


def _width(rule) -> int:
    if isinstance(rule, PairRule):
        return 2
    return 4


def fields(rom: bytes, offset: int, size: int = STRIDE) -> dict:
    parsed = {}
    cursor = 0
    for rule in FIELDS:
        width = _width(rule)
        if cursor + width > size:
            raise ValueError("%s at %#x: the field map overruns its %d-byte extent"
                             % (FAMILY, offset, size))
        if width == 2:
            parsed[rule.name] = struct.unpack_from("<H", rom, offset + cursor)[0]
        else:
            value = struct.unpack_from("<I", rom, offset + cursor)[0]
            if isinstance(rule, PointerRule) and not ROM_BASE <= value < ROM_END:
                raise ValueError("%s at %#x %s is %#010x, not a ROM address"
                                 % (FAMILY, offset, rule.name, value))
            parsed[rule.name] = value
        cursor += width
    if cursor != size:
        raise ValueError("%s at %#x parses to %d bytes, its extent is %d"
                         % (FAMILY, offset, cursor, size))
    return parsed


def serialize(parsed: dict, size: int = STRIDE) -> bytes:
    out = bytearray()
    for rule in FIELDS:
        out += struct.pack("<H" if _width(rule) == 2 else "<I", parsed[rule.name])
    return recordfamily.packed(out, size, FAMILY)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return recordfamily.serialize_record(rom, family, FAMILY, offset, size, fields, serialize)


def assert_contract(rom: bytes) -> dict:
    for index in range(COUNT):
        offset = BASE + STRIDE * index
        first, second = struct.unpack_from("<HH", rom, offset)
        if second != (first + 1) & 0xFFFF:
            raise ValueError("%s at %#x holds %d then %d, not consecutive ids"
                             % (FAMILY, offset, first, second))
        pointer = struct.unpack_from("<I", rom, offset + 0x10)[0]
        if not ROM_BASE <= pointer < ROM_END:
            raise ValueError("%s at %#x names %#010x at +0x10, not a ROM address"
                             % (FAMILY, offset, pointer))
    return {"records": COUNT, "bytes": COUNT * STRIDE,
            "first": BASE, "last_end": ARRAY_END}


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    return recordfamily.extents(rom, family, FAMILY, assert_contract,
                                [(BASE + STRIDE * index, STRIDE) for index in range(COUNT)])


def round_trip(rom: bytes) -> dict[str, int]:
    return recordfamily.round_trip(rom, FAMILY, BASE, STRIDE, COUNT, serialize_record)
