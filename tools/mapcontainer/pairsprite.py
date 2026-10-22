from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recordfamily  # noqa: E402

ROM_BASE = 0x08000000
WORD_HIGH = 0x08080000
SIZE_WORD = 0x2000
MAX_MODE = 0x3000
BLOCK_SIZE = 0x40

FAMILY = "endrom_pair_sprite_record"
TABLES = {
    FAMILY: {"base": 0x759620, "stride": 24, "count": 4, "entries": 2,
             "block_start": 0x759520, "block_end": 0x759620,
             "base_literal": 0x03588C, "end_literal": 0x051CCC, "end_word": 0x03001C4C,
             "vram_literal": (0x035890, 0x06010000),
             "consumer": ((0x08035670, 0x4A86), (0x08035672, 0x0041), (0x08035674, 0x1809),
                          (0x08035676, 0x00C9), (0x08035678, 0x1889), (0x08035688, 0x4D81),
                          (0x08035690, 0x6889), (0x08035696, 0x2240), (0x080356A8, 0x6949))},
    "endrom_sprite_record_r20": {
        "base": 0x76E264, "stride": 36, "count": 4, "entries": 3,
        "block_start": 0x76E0E4, "block_end": 0x76E264,
        "base_literal": 0x0386E8, "end_literal": None, "end_word": 0x00000000,
        "vram_literal": None,
        "consumer": ((0x08038458, 0x4BA3), (0x0803845A, 0x00C1), (0x0803845C, 0x1809),
                     (0x0803845E, 0x0089))},
    "endrom_sprite_record_r25": {
        "base": 0x75043C, "stride": 36, "count": 4, "entries": 3,
        "block_start": 0x7502BC, "block_end": 0x75043C,
        "base_literal": 0x02A58C, "end_literal": 0x02A9FC, "end_word": 0x03001C4C,
        "vram_literal": None,
        "consumer": ((0x0802A37A, 0x4B84), (0x0802A37C, 0x00C1), (0x0802A37E, 0x1809),
                     (0x0802A380, 0x0089))},
}

BASE = TABLES[FAMILY]["base"]
STRIDE = TABLES[FAMILY]["stride"]
COUNT = TABLES[FAMILY]["count"]
ENTRIES = TABLES[FAMILY]["entries"]
EXTENT = STRIDE * COUNT
END = BASE + EXTENT
BLOCK_START = TABLES[FAMILY]["block_start"]
BLOCK_END = TABLES[FAMILY]["block_end"]
WORD = WORD_HIGH
BASE_LITERAL = TABLES[FAMILY]["base_literal"]
END_LITERAL = TABLES[FAMILY]["end_literal"]
VRAM_LITERAL = TABLES[FAMILY]["vram_literal"][0]
VRAM_BASE = TABLES[FAMILY]["vram_literal"][1]
END_WORD = TABLES[FAMILY]["end_word"]
CONSUMER = TABLES[FAMILY]["consumer"]
FIELDS = tuple("entry_%d_%s" % (entry, field) for entry in range(ENTRIES)
               for field in ("word", "size", "mode", "tile"))
for _spec in TABLES.values():
    _spec["contract"] = {"records": _spec["count"], "bytes": _spec["stride"] * _spec["count"],
                         "entries": _spec["entries"] * _spec["count"],
                         "tiles": (_spec["block_end"] - _spec["block_start"]) // BLOCK_SIZE,
                         "first": _spec["base"],
                         "last_end": _spec["base"] + _spec["stride"] * _spec["count"]}
CONTRACT = TABLES[FAMILY]["contract"]


def table(family: str) -> dict:
    if family not in TABLES:
        raise ValueError("%s is not this module's family" % family)
    return TABLES[family]


def fields(rom: bytes, offset: int, size: int = STRIDE, family: str = FAMILY) -> dict:
    spec = table(family)
    if size != spec["stride"]:
        raise ValueError("%s at %#x is %d bytes, not %d" % (family, offset, size, spec["stride"]))
    parsed = {}
    for entry in range(spec["entries"]):
        start = offset + 12 * entry
        word, size_word, mode, tile = struct.unpack_from("<IHHI", rom, start)
        if word & 0xFFFF0000 != WORD_HIGH:
            raise ValueError("%s at %#x entry %d holds %#010x, not %#010x above its low half"
                             % (family, offset, entry, word, WORD_HIGH))
        if size_word != SIZE_WORD:
            raise ValueError("%s at %#x entry %d holds size %#06x, not %#06x"
                             % (family, offset, entry, size_word, SIZE_WORD))
        if mode > MAX_MODE:
            raise ValueError("%s at %#x entry %d holds mode %#06x, above %#06x"
                             % (family, offset, entry, mode, MAX_MODE))
        if not spec["block_start"] <= tile - ROM_BASE < spec["block_end"] or (
                tile - ROM_BASE - spec["block_start"]) % BLOCK_SIZE:
            raise ValueError("%s at %#x entry %d names tile %#010x, not a %#x-byte block in "
                             "%#x..%#x" % (family, offset, entry, tile, BLOCK_SIZE,
                                           spec["block_start"], spec["block_end"]))
        parsed["entry_%d_word" % entry] = word
        parsed["entry_%d_size" % entry] = size_word
        parsed["entry_%d_mode" % entry] = mode
        parsed["entry_%d_tile" % entry] = tile
    return parsed


def serialize(parsed: dict, size: int = STRIDE, family: str = FAMILY) -> bytes:
    spec = table(family)
    out = bytearray()
    for entry in range(spec["entries"]):
        out += struct.pack("<IHHI", parsed["entry_%d_word" % entry],
                           parsed["entry_%d_size" % entry], parsed["entry_%d_mode" % entry],
                           parsed["entry_%d_tile" % entry])
    return recordfamily.packed(out, size, family)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return recordfamily.serialize_record(
        rom, family, family, offset, size, lambda image, at, extent: fields(image, at, extent, family),
        lambda parsed, extent: serialize(parsed, extent, family))


def assert_contract(rom: bytes, family: str = FAMILY) -> dict:
    spec = table(family)
    base, stride, count = spec["base"], spec["stride"], spec["count"]
    end = base + stride * count
    recordfamily.base_word(rom, family, spec["base_literal"], ROM_BASE + base)
    if spec["end_literal"] is not None:
        if struct.unpack_from("<I", rom, spec["end_literal"])[0] != ROM_BASE + end:
            raise ValueError("%s's end literal at file %#x does not hold %#010x"
                             % (family, spec["end_literal"], ROM_BASE + end))
    if struct.unpack_from("<I", rom, end)[0] != spec["end_word"]:
        raise ValueError("%s's extent ends on %#010x, not %#010x"
                         % (family, struct.unpack_from("<I", rom, end)[0], spec["end_word"]))
    if spec["vram_literal"] is not None:
        literal, value = spec["vram_literal"]
        if struct.unpack_from("<I", rom, literal)[0] != value:
            raise ValueError("%s's VRAM literal at file %#x is not %#010x"
                             % (family, literal, value))
    recordfamily.consumer_pins(rom, family, [(address - ROM_BASE, halfword)
                                             for address, halfword in spec["consumer"]])
    tiles = []
    for index in range(count):
        parsed = fields(rom, base + stride * index, stride, family)
        tiles += [parsed["entry_%d_tile" % entry] for entry in range(spec["entries"])]
    measured = sorted({tile - ROM_BASE for tile in tiles})
    expected = [spec["block_start"] + BLOCK_SIZE * index
                for index in range((spec["block_end"] - spec["block_start"]) // BLOCK_SIZE)]
    if measured != expected:
        raise ValueError("%s's tile pointers name %s, not one %#x-byte block each in %s"
                         % (family, ["%#x" % tile for tile in measured], BLOCK_SIZE,
                            ["%#x" % block for block in expected]))
    return recordfamily.held_contract(
        {"records": count, "bytes": stride * count, "entries": spec["entries"] * count,
         "tiles": len(measured), "first": base, "last_end": end}, spec["contract"], family)


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    names = tuple(TABLES) if family is None else (family,)
    out = {}
    for name in names:
        spec = table(name)
        out.update(recordfamily.extents(
            rom, name, name, assert_contract,
            [(spec["base"] + spec["stride"] * index, spec["stride"])
             for index in range(spec["count"])]))
    return out


def round_trip(rom: bytes, family: str = FAMILY) -> dict[str, int]:
    spec = table(family)
    return recordfamily.round_trip(rom, family, spec["base"], spec["stride"], spec["count"],
                                   serialize_record)


if __name__ == "__main__":
    recordfamily.main(FAMILY, assert_contract, round_trip, sys.argv)
