from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recordfamily  # noqa: E402

FAMILY = "event_pool_record"
BASE = 0x77C5A4
END = 0x79B704
INDEX_BASE = 0x79B704
INDEX_ENTRY = 4
COUNT = 522
HEADER = 4
MIN_BYTES = 16
MAX_BYTES = 3168
OUTSIDE_TARGETS = 1
ROM_BASE = 0x08000000
ROM_END = 0x08800000
TYPES = (0, 3, 4, 5, 6, 7)
TYPE_WORDS = (236, 2, 141, 139, 2, 2)
CONTRACT = {"records": COUNT, "bytes": END - BASE, "first": BASE, "last_end": END,
            "min_bytes": MIN_BYTES, "max_bytes": MAX_BYTES,
            "outside_targets": OUTSIDE_TARGETS}


def record_rows(rom: bytes) -> list[tuple[int, int]]:
    starts = [struct.unpack_from("<I", rom, INDEX_BASE + INDEX_ENTRY * index)[0] - ROM_BASE
              for index in range(COUNT)]
    if starts[0] != BASE:
        raise ValueError("%s's first record is %#x, not the pool base %#x" % (FAMILY, starts[0], BASE))
    for index, (previous, following) in enumerate(zip(starts, starts[1:])):
        if following <= previous:
            raise ValueError("%s records %d and %d are %#x then %#x, not ascending"
                             % (FAMILY, index, index + 1, previous, following))
    lengths = [following - previous for previous, following in zip(starts, starts[1:])]
    lengths.append(END - starts[-1])
    if lengths[-1] <= 0:
        raise ValueError("%s's last record %#x ends at %#x, past its end %#x"
                         % (FAMILY, starts[-1], starts[-1] + lengths[-1], END))
    return list(zip(starts, lengths))


def fields(rom: bytes, offset: int, size: int) -> dict:
    if not HEADER <= size <= MAX_BYTES:
        raise ValueError("%s at %#x has a %d-byte extent, not the measured %d..%d"
                         % (FAMILY, offset, size, MIN_BYTES, MAX_BYTES))
    dialog = struct.unpack_from("<I", rom, offset)[0]
    if not ROM_BASE <= dialog < ROM_END:
        raise ValueError("%s at %#x dialog is %#010x, not a ROM address" % (FAMILY, offset, dialog))
    if dialog - ROM_BASE + 3 > len(rom):
        raise ValueError("%s at %#x dialog %#010x has no TYPE byte inside the image"
                         % (FAMILY, offset, dialog))
    dialog_type = rom[dialog - ROM_BASE + 2]
    if dialog_type not in TYPES:
        raise ValueError("%s at %#x dialog %#010x has TYPE %d, not one of %s"
                         % (FAMILY, offset, dialog, dialog_type, list(TYPES)))
    return {"dialog": dialog, "dialog_type": dialog_type,
            "body": rom[offset + HEADER:offset + size]}


def serialize(parsed: dict, size: int) -> bytes:
    out = bytearray(struct.pack("<I", parsed["dialog"]))
    out += parsed["body"]
    return recordfamily.packed(out, size, FAMILY)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return recordfamily.serialize_record(rom, family, FAMILY, offset, size, fields, serialize)


def assert_contract(rom: bytes) -> dict:
    rows = record_rows(rom)
    lengths = [size for _, size in rows]
    if sum(lengths) != END - BASE:
        raise ValueError("%s's records sum to %d B, the pool is %d"
                         % (FAMILY, sum(lengths), END - BASE))
    if min(lengths) != MIN_BYTES or max(lengths) != MAX_BYTES:
        raise ValueError("%s's record lengths measure %d..%d, the contract says %d..%d"
                         % (FAMILY, min(lengths), max(lengths), MIN_BYTES, MAX_BYTES))
    histogram = {value: 0 for value in TYPES}
    outside = 0
    for offset, size in rows:
        parsed = fields(rom, offset, size)
        histogram[parsed["dialog_type"]] += 1
        if not BASE <= parsed["dialog"] - ROM_BASE < END:
            outside += 1
    counted = tuple(histogram[value] for value in TYPES)
    if counted != TYPE_WORDS:
        raise ValueError("%s's TYPE histogram measures %s, the contract says %s"
                         % (FAMILY, counted, TYPE_WORDS))
    if outside != OUTSIDE_TARGETS:
        raise ValueError("%s has %d dialog pointers leaving the pool, the contract says %d"
                         % (FAMILY, outside, OUTSIDE_TARGETS))
    measured = {"records": len(rows), "bytes": sum(lengths), "first": rows[0][0],
                "last_end": rows[-1][0] + rows[-1][1], "min_bytes": min(lengths),
                "max_bytes": max(lengths), "outside_targets": outside}
    if measured != CONTRACT:
        raise ValueError("%s measures %s, the contract says %s" % (FAMILY, measured, CONTRACT))
    return measured


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    return recordfamily.extents(rom, family, FAMILY, assert_contract, record_rows(rom))


def round_trip(rom: bytes) -> dict[str, dict[str, int]]:
    rows = extents(rom, FAMILY)[FAMILY]
    equal = sum(1 for offset, size in rows
                if serialize_record(rom, FAMILY, offset, size) == rom[offset:offset + size])
    return {FAMILY: {"records": len(rows), "equal": equal,
                     "bytes": sum(size for _, size in rows)}}


if __name__ == "__main__":
    recordfamily.main(FAMILY, assert_contract, round_trip, sys.argv)
