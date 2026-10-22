from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mapcontainer import PointerRule  # noqa: E402

FAMILY = "ai_row_table"
BASE = 0x70F514
STRIDE = 8
COUNT = 828
ARRAY_END = BASE + STRIDE * COUNT
DISTINCT_TARGETS = 1022
ROM_BASE = 0x08000000
ROM_END = 0x08800000
CONTRACT = {"records": COUNT, "bytes": STRIDE * COUNT, "distinct": DISTINCT_TARGETS}

FIELDS = (PointerRule("node_a"), PointerRule("node_b"))


def fields(rom: bytes, offset: int, size: int = STRIDE) -> dict:
    if size != STRIDE:
        raise ValueError("%s at %#x is %d bytes, not %d" % (FAMILY, offset, size, STRIDE))
    parsed = {}
    for index, rule in enumerate(FIELDS):
        value = struct.unpack_from("<I", rom, offset + 4 * index)[0]
        if not ROM_BASE <= value < ROM_END:
            raise ValueError("%s at %#x %s is %#010x, not a ROM address"
                             % (FAMILY, offset, rule.name, value))
        parsed[rule.name] = value
    return parsed


def serialize(parsed: dict, size: int = STRIDE) -> bytes:
    return b"".join(struct.pack("<I", parsed[rule.name]) for rule in FIELDS)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    if family != FAMILY:
        raise ValueError("%s is not this module's family" % family)
    return serialize(fields(rom, offset, size), size)


def assert_contract(rom: bytes) -> dict:
    targets = set()
    for index in range(COUNT):
        offset = BASE + STRIDE * index
        for cursor, rule in enumerate(FIELDS):
            value = struct.unpack_from("<I", rom, offset + 4 * cursor)[0]
            if not ROM_BASE <= value < ROM_END:
                raise ValueError("%s at %#x %s is %#010x, not a ROM address"
                                 % (FAMILY, offset, rule.name, value))
            targets.add(value)
    measured = {"records": COUNT, "bytes": STRIDE * COUNT, "distinct": len(targets)}
    if measured != CONTRACT:
        raise ValueError("%s measures %s, the contract says %s" % (FAMILY, measured, CONTRACT))
    return measured


def rows(rom: bytes) -> list[tuple[int, int]]:
    assert_contract(rom)
    return [(BASE + STRIDE * index, STRIDE) for index in range(COUNT)]


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    if family not in (None, FAMILY):
        raise ValueError("%s is not this module's family" % family)
    return {FAMILY: rows(rom)}


def round_trip(rom: bytes) -> dict[str, int]:
    equal = 0
    for offset, size in rows(rom):
        equal += serialize_record(rom, FAMILY, offset, size) == rom[offset:offset + size]
    return {"records": COUNT, "equal": equal, "bytes": STRIDE * COUNT}


if __name__ == "__main__":
    image = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gba", "rb").read()
    print("%s measure %s" % (FAMILY, assert_contract(image)))
    print("%s verify  round trip %s" % (FAMILY, round_trip(image)))
