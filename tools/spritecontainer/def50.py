from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "mapcontainer"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recordfamily  # noqa: E402

import spritefamily  # noqa: E402

FAMILY = "sprite_def_array_50"
CELL_FAMILY = "sprite_cell_grid"
FAMILIES = (FAMILY, CELL_FAMILY)
ARRAY_AT = 0x50
SLOTS_AT = 0x54
SLOT_SIZE = 4
CELL_SIZE = 2
DIRECTIONS = 4
FRAME_CELLS = DIRECTIONS * CELL_SIZE
ROM_BASE = 0x08000000
BLOCK = (0x3C34D0, 0x6A88AC)


def arrays(rom: bytes) -> list[tuple[int, int]]:
    found = []
    for definition in spritefamily.table_offsets(rom):
        pointer = struct.unpack_from("<I", rom, definition + ARRAY_AT)[0]
        if pointer == 0:
            continue
        if not ROM_BASE <= pointer < ROM_BASE + len(rom):
            raise ValueError("%s definition %#x names %#010x at +0x50"
                             % (FAMILY, definition, pointer))
        found.append((definition, pointer - ROM_BASE))
    return found


def grids(rom: bytes) -> list[tuple[int, int, int, int]]:
    found = []
    for definition, array in arrays(rom):
        for slot in range(rom[definition]):
            pointer = struct.unpack_from("<I", rom, array + SLOT_SIZE * slot)[0]
            if pointer == 0:
                continue
            if not ROM_BASE <= pointer < ROM_BASE + len(rom):
                raise ValueError("%s definition %#x slot %d names %#010x"
                                 % (CELL_FAMILY, definition, slot, pointer))
            animation = struct.unpack_from("<I", rom, definition + SLOTS_AT + SLOT_SIZE * slot)[0]
            if not ROM_BASE <= animation < ROM_BASE + len(rom):
                raise ValueError("%s grid %#010x has no animation (%#010x)"
                                 % (CELL_FAMILY, pointer, animation))
            found.append((pointer - ROM_BASE, definition, slot,
                          struct.unpack_from("<I", rom, animation - ROM_BASE)[0]))
    return found


def array_rows(rom: bytes) -> list[tuple[int, int]]:
    rows = sorted((array, SLOT_SIZE * rom[definition]) for definition, array in arrays(rom))
    for start, size in rows:
        if not (BLOCK[0] <= start and start + size <= BLOCK[1]):
            raise ValueError("%s array %#x..%#x is outside the sprite block"
                             % (FAMILY, start, start + size))
        for other, other_size in rows:
            if other != start and start < other + other_size and other < start + size:
                raise ValueError("%s arrays %#x and %#x share a byte" % (FAMILY, start, other))
    return rows


def cell_rows(rom: bytes) -> list[tuple[int, int]]:
    rows = sorted((grid, FRAME_CELLS * frames) for grid, _definition, _slot, frames in grids(rom))
    for start, size in rows:
        if not size:
            raise ValueError("%s grid %#x has no frame" % (CELL_FAMILY, start))
        if not (BLOCK[0] <= start and start + size <= BLOCK[1]):
            raise ValueError("%s grid %#x..%#x is outside the sprite block"
                             % (CELL_FAMILY, start, start + size))
        for other, other_size in rows:
            if other != start and start < other + other_size and other < start + size:
                raise ValueError("%s grids %#x and %#x share a byte" % (CELL_FAMILY, start, other))
        for other, other_size in array_rows(rom):
            if start < other + other_size and other < start + size:
                raise ValueError("%s grid %#x shares a byte with the array %#x"
                                 % (CELL_FAMILY, start, other))
    return rows


def fields(rom: bytes, offset: int, size: int) -> dict:
    if size % SLOT_SIZE:
        raise ValueError("%s at %#x is %d bytes, not a whole number of slots" % (FAMILY, offset, size))
    definition = next((site for site, array in arrays(rom)
                       if array == offset and size == SLOT_SIZE * rom[site]), None)
    if definition is None:
        raise ValueError("%s at %#x with %d bytes is not a modelled array" % (FAMILY, offset, size))
    return {"definition": definition,
            "slots": tuple(struct.unpack_from("<I", rom, offset + SLOT_SIZE * index)[0]
                           for index in range(size // SLOT_SIZE))}


def cell_fields(rom: bytes, offset: int, size: int) -> dict:
    frames = next((count for grid, _definition, _slot, count in grids(rom) if grid == offset), None)
    if frames is None:
        raise ValueError("%s at %#x is not a modelled grid" % (CELL_FAMILY, offset))
    if size != FRAME_CELLS * frames:
        raise ValueError("%s at %#x is %d bytes, its animation has %d frames"
                         % (CELL_FAMILY, offset, size, frames))
    return {"frame_count": frames,
            "cells": tuple(struct.unpack_from("<bb", rom, offset + CELL_SIZE * index)
                           for index in range(DIRECTIONS * frames))}


def serialize(parsed: dict, size: int) -> bytes:
    out = bytearray()
    for word in parsed["slots"]:
        out += struct.pack("<I", word)
    return recordfamily.packed(out, size, FAMILY)


def serialize_cells(parsed: dict, size: int) -> bytes:
    out = bytearray()
    for x, y in parsed["cells"]:
        out += struct.pack("<bb", x, y)
    return recordfamily.packed(out, size, CELL_FAMILY)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    if family == CELL_FAMILY:
        return serialize_cells(cell_fields(rom, offset, size), size)
    return recordfamily.serialize_record(rom, family, FAMILY, offset, size, fields, serialize)


def assert_contract(rom: bytes) -> dict:
    arrays_ = array_rows(rom)
    cells = cell_rows(rom)
    slots = sum(size // SLOT_SIZE for _, size in arrays_)
    frames = [count for _grid, _definition, _slot, count in grids(rom)]
    measured = (len(arrays_), slots, sum(size for _, size in arrays_), len(cells),
                sum(frames), sum(size for _, size in cells))
    if measured != (10, 174, 696, 126, 457, 3656):
        raise ValueError("%s measures %d arrays / %d slots / %d B, %d grids / %d frames / %d B"
                         % ((FAMILY,) + measured))
    for definition, array in arrays(rom):
        run = sorted((grid, FRAME_CELLS * count) for grid, site, _slot, count in grids(rom)
                     if site == definition)
        run.append((array, SLOT_SIZE * rom[definition]))
        run.sort()
        for (start, size), (later, _length) in zip(run, run[1:]):
            if start + size != later:
                raise ValueError("%s definition %#x does not tile: %#x..%#x then %#x"
                                 % (CELL_FAMILY, definition, start, start + size, later))
    return {"arrays": len(arrays_), "slots": slots, "bytes": sum(size for _, size in arrays_),
            "grids": len(cells), "frames": sum(frames), "grid_bytes": sum(size for _, size in cells)}


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    if family not in (None,) + FAMILIES:
        raise ValueError("%s is not this module's family" % family)
    out = {}
    if family in (None, FAMILY):
        out[FAMILY] = array_rows(rom)
    if family in (None, CELL_FAMILY):
        out[CELL_FAMILY] = cell_rows(rom)
    return out


def round_trip(rom: bytes) -> dict:
    equal = 0
    rows = extents(rom)[FAMILY]
    for offset, size in rows:
        equal += serialize_record(rom, FAMILY, offset, size) == rom[offset:offset + size]
    return {"records": len(rows), "equal": equal, "bytes": sum(size for _, size in rows)}


def round_trip_cells(rom: bytes) -> dict:
    equal = 0
    rows = extents(rom)[CELL_FAMILY]
    for offset, size in rows:
        equal += serialize_record(rom, CELL_FAMILY, offset, size) == rom[offset:offset + size]
    return {"records": len(rows), "equal": equal, "bytes": sum(size for _, size in rows)}


if __name__ == "__main__":
    image = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gba", "rb").read()
    print("%s measure %s" % (FAMILY, assert_contract(image)))
    print("%s verify  round trip %s" % (FAMILY, round_trip(image)))
    print("%s verify  round trip %s" % (CELL_FAMILY, round_trip_cells(image)))
