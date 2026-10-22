from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import pairsprite  # noqa: E402
import recordfamily  # noqa: E402

FAMILY = "endrom_facing_pair"
BASE = 0x7594F0
STRIDE = 8
COUNT = 4
END = BASE + STRIDE * COUNT
ROM_BASE = 0x08000000
BASE_LITERAL = 0x035884
SIBLING = pairsprite.FAMILY
VECTORS = ((0, 1), (0, -1), (-1, 0), (1, 0))
FIELDS = ("dx", "dy")
CONTRACT = {"records": COUNT, "bytes": STRIDE * COUNT, "pairs": COUNT,
            "first": BASE, "last_end": END}
CONSUMER = ((0x08035670, 0x4A86), (0x08035672, 0x0041), (0x0803567C, 0x00C0),
            (0x0803567A, 0x4A82), (0x0803567E, 0x3208), (0x08035680, 0x1880),
            (0x08035684, 0x6802), (0x08035686, 0x6840), (0x0803568C, 0x62E2))


def fields(rom: bytes, offset: int, size: int = STRIDE) -> dict:
    if size != STRIDE:
        raise ValueError("%s at %#x is %d bytes, not %d" % (FAMILY, offset, size, STRIDE))
    dx, dy = struct.unpack_from("<ii", rom, offset)
    if (dx, dy) not in VECTORS:
        raise ValueError("%s at %#x holds (%d, %d), not a facing vector"
                         % (FAMILY, offset, dx, dy))
    return {"dx": dx, "dy": dy}


def serialize(parsed: dict, size: int = STRIDE) -> bytes:
    out = bytearray(struct.pack("<ii", parsed["dx"], parsed["dy"]))
    return recordfamily.packed(out, size, FAMILY)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return recordfamily.serialize_record(rom, family, FAMILY, offset, size, fields, serialize)


def assert_contract(rom: bytes) -> dict:
    word = struct.unpack_from("<I", rom, BASE_LITERAL)[0]
    if word != ROM_BASE + BASE - STRIDE:
        raise ValueError("%s's base literal at file %#x is %#010x, not %#010x"
                         % (FAMILY, BASE_LITERAL, word, ROM_BASE + BASE - STRIDE))
    recordfamily.consumer_pins(rom, FAMILY, [(address - ROM_BASE, halfword)
                                             for address, halfword in CONSUMER])
    sibling = pairsprite.assert_contract(rom)
    if sibling["records"] != COUNT:
        raise ValueError("%s's index bounds %d records, the sibling table holds %d"
                         % (FAMILY, COUNT, sibling["records"]))
    pairs = []
    for index in range(COUNT):
        parsed = fields(rom, BASE + STRIDE * index)
        pairs.append((parsed["dx"], parsed["dy"]))
    if pairs != list(VECTORS):
        raise ValueError("%s holds %s, not the facing vectors %s"
                         % (FAMILY, pairs, list(VECTORS)))
    return recordfamily.held_contract(
        {"records": COUNT, "bytes": STRIDE * COUNT, "pairs": len(pairs),
         "first": BASE, "last_end": END}, CONTRACT, FAMILY)


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    return recordfamily.extents(rom, family, FAMILY, assert_contract,
                                [(BASE + STRIDE * index, STRIDE) for index in range(COUNT)])


def round_trip(rom: bytes, family: str = None) -> dict[str, int]:
    return recordfamily.round_trip(rom, FAMILY, BASE, STRIDE, COUNT, serialize_record)


if __name__ == "__main__":
    recordfamily.main(FAMILY, assert_contract, round_trip, sys.argv)
