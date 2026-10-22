from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mapcontainer import ROM_BASE  # noqa: E402

FAMILY = "ai_behaviour_node"
ROW_TABLE = 0x70F514
ROW_COUNT = 828
ROW_WORDS = 2 * ROW_COUNT
ROW_TARGETS = 1022
ROW_END = ROW_TABLE + 4 * ROW_WORDS
COMPOSITE = {0x08018F91: "seq", 0x080191C7: "and", 0x0801920F: "or"}
LEAF = 0x10
PARAMLESS_LEAF = 0x0C
PREFIX = 0x10
MAX_CHILDREN = 64
ADDRESSES = ("activate", "evaluate", "release")
CONTRACT = {"records": 2505, "bytes": 53168, "runs": 1031, "composite": 1170, "paramless": 50}


class AiNodeError(ValueError):
    pass


def _u32(rom: bytes, offset: int) -> int:
    return struct.unpack_from("<I", rom, offset)[0]


def _is_pointer(rom: bytes, value: int) -> bool:
    return ROM_BASE <= value < ROM_BASE + len(rom)


def _is_address(rom: bytes, value: int) -> bool:
    return value == 0 or (value & 1 and _is_pointer(rom, value))


def row_targets(rom: bytes) -> list[int]:
    words = [_u32(rom, ROW_TABLE + 4 * index) for index in range(ROW_WORDS)]
    for word in words:
        if not _is_pointer(rom, word):
            raise AiNodeError("the row table holds %#010x, not a ROM address" % word)
    targets = sorted({word - ROM_BASE for word in words})
    if len(targets) != ROW_TARGETS:
        raise AiNodeError("the row table names %d distinct targets, the contract says %d"
                          % (len(targets), ROW_TARGETS))
    return targets


def _walk(rom: bytes) -> dict[int, int]:
    seen: dict[int, int] = {}
    stack = list(row_targets(rom))
    while stack:
        offset = stack.pop()
        if offset in seen or not 0 <= offset <= len(rom) - PREFIX:
            continue
        activate = _u32(rom, offset)
        if activate in COMPOSITE:
            count = _u32(rom, offset + 0x0C)
            if count > MAX_CHILDREN:
                raise AiNodeError("%s at %#x carries child count %d" % (FAMILY, offset, count))
            size = PREFIX + 4 * count
            if offset + size > len(rom):
                raise AiNodeError("%s at %#x runs past the image" % (FAMILY, offset))
            stack += [child - ROM_BASE for child
                      in (_u32(rom, offset + PREFIX + 4 * index) for index in range(count))
                      if _is_pointer(rom, child)]
        else:
            size = LEAF
        seen[offset] = size
    return seen


def rows(rom: bytes) -> list[tuple[int, int]]:
    seen = _walk(rom)
    tiled = []
    for offset, size in sorted(seen.items()):
        if size == LEAF and offset + 0x0C in seen:
            size = PARAMLESS_LEAF
        tiled.append((offset, size))
    for (start, size), (next_start, _) in zip(tiled, tiled[1:]):
        if start + size > next_start:
            raise AiNodeError("%s records at %#x and %#x share a byte" % (FAMILY, start, next_start))
    return tiled


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    if family not in (None, FAMILY):
        raise AiNodeError("%s is not this module's family" % family)
    assert_contract(rom)
    return {FAMILY: rows(rom)}


def fields(rom: bytes, offset: int, size: int) -> dict:
    parsed = {}
    for index, name in enumerate(ADDRESSES):
        value = _u32(rom, offset + 4 * index)
        if not _is_address(rom, value):
            raise AiNodeError("%s at %#x holds %#010x at %s, neither zero nor a code address"
                              % (FAMILY, offset, value, name))
        parsed[name] = value
    if parsed["activate"] in COMPOSITE:
        count = _u32(rom, offset + 0x0C)
        if size != PREFIX + 4 * count:
            raise AiNodeError("%s at %#x is %d bytes, its class %#010x with count %d is %d"
                              % (FAMILY, offset, size, parsed["activate"], count,
                                 PREFIX + 4 * count))
        parsed["children"] = tuple(_u32(rom, offset + PREFIX + 4 * index) for index in range(count))
    elif size == LEAF:
        parsed["param"] = _u32(rom, offset + 0x0C)
    elif size != PARAMLESS_LEAF:
        raise AiNodeError("%s at %#x is %d bytes, not %d or %d"
                          % (FAMILY, offset, size, PARAMLESS_LEAF, LEAF))
    return parsed


def serialize(parsed: dict, size: int) -> bytes:
    out = bytearray()
    for name in ADDRESSES:
        out += struct.pack("<I", parsed[name])
    if "children" in parsed:
        out += struct.pack("<I", len(parsed["children"]))
        for child in parsed["children"]:
            out += struct.pack("<I", child)
    elif size == LEAF:
        out += struct.pack("<I", parsed["param"])
    if len(out) != size:
        raise AiNodeError("%s serializes to %d bytes, its extent is %d" % (FAMILY, len(out), size))
    return bytes(out)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    if family != FAMILY:
        raise AiNodeError("%s is not this module's family" % family)
    return serialize(fields(rom, offset, size), size)


def assert_contract(rom: bytes) -> dict:
    tiled = rows(rom)
    for offset, size in tiled:
        fields(rom, offset, size)
        if ROW_TABLE < offset + size and offset < ROW_END:
            raise AiNodeError("%s record %#x claims a byte of the row table" % (FAMILY, offset))
    measured = {"records": len(tiled), "bytes": sum(size for _, size in tiled),
                "runs": 1 + sum(start + size != next_start
                                for (start, size), (next_start, _) in zip(tiled, tiled[1:])),
                "composite": sum(1 for offset, _ in tiled if _u32(rom, offset) in COMPOSITE),
                "paramless": sum(1 for _, size in tiled if size == PARAMLESS_LEAF)}
    if measured != CONTRACT:
        raise AiNodeError("%s measures %s, the contract says %s" % (FAMILY, measured, CONTRACT))
    return measured


def round_trip(rom: bytes) -> dict:
    equal = 0
    tiled = rows(rom)
    for offset, size in tiled:
        equal += serialize_record(rom, FAMILY, offset, size) == rom[offset:offset + size]
    return {"records": len(tiled), "equal": equal, "bytes": sum(size for _, size in tiled)}


if __name__ == "__main__":
    image = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gba", "rb").read()
    print("%s measure %s" % (FAMILY, assert_contract(image)))
    print("%s verify  round trip %s" % (FAMILY, round_trip(image)))
