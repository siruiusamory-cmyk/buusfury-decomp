from __future__ import annotations

import struct

from mapcontainer import PointerRule, WordRule

ROM_BASE = 0x08000000
TABLE = 0x6B6BDC
COUNT = 297
DEFINITION_START = 0x6A89D0
DEFINITION_END = 0x6B6BDC
TABLE_END = 0x6B7080
SLOTS_AT = 0x54
ANIMATION_PREFIX = 4
FRAME_PREFIX = 8
PIECE_SIZE = 12
GRAPHICS_AT = 8
DIRECTIONS = 4

DEFINITION = "sprite_definition"
ANIMATION = "sprite_animation"
FRAME = "sprite_frame"
INDEX = "sprite_index"
FAMILIES = (DEFINITION, ANIMATION, FRAME, INDEX)
EXPECTED = {DEFINITION: 297, ANIMATION: 1017, FRAME: 10980, INDEX: 1}
EXPECTED_BYTES = {DEFINITION: 57868, ANIMATION: 58708, FRAME: 219900, INDEX: TABLE_END - TABLE}
TABLE_BYTES = TABLE_END - TABLE
UNION_BYTES = 337664

DEFINITION_HEAD_FIELDS = (WordRule("slot_word"), WordRule("word_04"), WordRule("word_08"),
                          WordRule("word_0c"), WordRule("word_10"), WordRule("word_14"),
                          WordRule("word_18"), WordRule("word_1c"), WordRule("word_20"))
ANIMATION_FIELDS = (WordRule("frame_count"),)
FRAME_FIELDS = (WordRule("piece_count"), WordRule("word_04"))
PIECE_FIELDS = (WordRule("attr"), WordRule("flags"), PointerRule("container"))


def slot_span(rom: bytes, offset: int, fields: tuple = None) -> int:
    return SLOTS_AT + 4 * rom[offset]


def animation_span(rom: bytes, offset: int, fields: tuple = None) -> int:
    return ANIMATION_PREFIX + DIRECTIONS * 4 * struct.unpack_from("<I", rom, offset)[0]


def frame_span(rom: bytes, offset: int, fields: tuple = None) -> int:
    return FRAME_PREFIX + PIECE_SIZE * struct.unpack_from("<I", rom, offset)[0]


def definition_end(rom: bytes, offset: int) -> int:
    for index in range(COUNT):
        site = struct.unpack_from("<I", rom, TABLE + 4 * index)[0] - ROM_BASE
        if site > offset:
            return site
    return DEFINITION_END


def table_offsets(rom: bytes) -> list[int]:
    sites = []
    for index in range(COUNT):
        address = struct.unpack_from("<I", rom, TABLE + 4 * index)[0]
        if not ROM_BASE <= address < ROM_BASE + len(rom):
            raise ValueError("definition %d holds %#010x" % (index, address))
        sites.append(address - ROM_BASE)
    if sites != sorted(sites):
        raise ValueError("the definition table is not in file order")
    if sites[0] != DEFINITION_START or sites[-1] >= DEFINITION_END:
        raise ValueError("the definitions span %#x..%#x" % (sites[0], sites[-1]))
    for site in sites:
        if site % 4:
            raise ValueError("definition %#x is not word aligned" % site)
    return sites


def walk(rom: bytes) -> dict[str, dict[int, int]]:
    animation_span_of: dict[int, int] = {}
    frame_span_of: dict[int, int] = {}
    for site in table_offsets(rom):
        end = definition_end(rom, site)
        for slot in range(rom[site]):
            address = struct.unpack_from("<I", rom, site + SLOTS_AT + 4 * slot)[0]
            if address == 0:
                continue
            if not ROM_BASE <= address < ROM_BASE + len(rom):
                raise ValueError("definition %#x slot %d holds %#010x" % (site, slot, address))
            animation = address - ROM_BASE
            animation_span_of[animation] = animation_span(rom, animation)
    for animation, length in animation_span_of.items():
        for index in range(struct.unpack_from("<I", rom, animation)[0]):
            for direction in range(DIRECTIONS):
                at = animation + ANIMATION_PREFIX + 4 * (index * DIRECTIONS + direction)
                address = struct.unpack_from("<I", rom, at)[0]
                if address == 0:
                    continue
                if not ROM_BASE <= address < ROM_BASE + len(rom):
                    raise ValueError("animation %#x frame %d holds %#010x"
                                     % (animation, index, address))
                frame = address - ROM_BASE
                frame_span_of[frame] = frame_span(rom, frame)
    return {DEFINITION: {site: definition_end(rom, site) - site for site in table_offsets(rom)},
            ANIMATION: animation_span_of, FRAME: frame_span_of,
            INDEX: {TABLE: TABLE_BYTES}}


def extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    walked = walk(rom)
    if family and family not in FAMILIES:
        raise ValueError("%r is not a sprite family" % family)
    names = (family,) if family else FAMILIES
    return {name: sorted(walked[name].items()) for name in names}


def assert_contract(rom: bytes) -> dict[str, int]:
    walked = walk(rom)
    populations = {name: len(walked[name]) for name in FAMILIES}
    if populations != EXPECTED:
        raise SystemExit("populations %s, not the measured %s" % (populations, EXPECTED))
    totals = {name: sum(walked[name].values()) for name in FAMILIES}
    if totals != EXPECTED_BYTES:
        raise SystemExit("family totals %s, not the measured %s" % (totals, EXPECTED_BYTES))
    for name in FAMILIES:
        rows = sorted(walked[name])
        for first, second in zip(rows, rows[1:]):
            if first + walked[name][first] > second:
                raise SystemExit("%s %#x overlaps %#x" % (name, first, second))
    if totals[DEFINITION] + TABLE_BYTES + totals[ANIMATION] + totals[FRAME] != UNION_BYTES:
        raise SystemExit("the components do not sum to the union")
    return populations


def fields(rom: bytes, family: str, offset: int) -> dict:
    if family == DEFINITION:
        parsed = {"slot_word": rom[offset]}
        parsed.update({rule.name: struct.unpack_from("<I", rom, offset + 4 * (index + 1))[0]
                       for index, rule in enumerate(DEFINITION_HEAD_FIELDS[1:])})
        slots = {slot: struct.unpack_from("<I", rom, offset + SLOTS_AT + 4 * slot)[0]
                 for slot in range(rom[offset])}
        end = definition_end(rom, offset)
        tail = rom[offset + slot_span(rom, offset):end]
        return {"fields": parsed, "head": struct.unpack_from("<I", rom, offset)[0],
                "middle": rom[offset + 0x24:offset + SLOTS_AT], "slots": slots, "tail": tail}
    if family == ANIMATION:
        count = struct.unpack_from("<I", rom, offset)[0]
        pointers = [struct.unpack_from("<I", rom, offset + ANIMATION_PREFIX + 4 * index)[0]
                    for index in range(DIRECTIONS * count)]
        return {"fields": {"frame_count": count}, "frame_pointers": pointers}
    if family == FRAME:
        count = struct.unpack_from("<I", rom, offset)[0]
        pieces = [{"attr": struct.unpack_from("<I", rom, offset + FRAME_PREFIX
                                              + PIECE_SIZE * index)[0],
                   "flags": struct.unpack_from("<I", rom, offset + FRAME_PREFIX
                                               + PIECE_SIZE * index + 4)[0],
                   "container": struct.unpack_from("<I", rom, offset + FRAME_PREFIX
                                                   + PIECE_SIZE * index + GRAPHICS_AT)[0]}
                  for index in range(count)]
        return {"fields": {"piece_count": count,
                           "word_04": struct.unpack_from("<I", rom, offset + 4)[0]},
                "pieces": pieces}
    if family == INDEX:
        words = TABLE_BYTES // 4
        return {"fields": {"definition_addresses":
                           [struct.unpack_from("<I", rom, offset + 4 * index)[0]
                            for index in range(words)]},
                "table_base": TABLE}
    raise ValueError("%r is not a sprite family" % family)


def serialize(family: str, parsed: dict, size: int) -> bytes:
    if family == DEFINITION:
        out = bytearray(size)
        out[0] = parsed["fields"]["slot_word"]
        for index, rule in enumerate(DEFINITION_HEAD_FIELDS[1:]):
            struct.pack_into("<I", out, 4 * (index + 1), parsed["fields"][rule.name])
        struct.pack_into("<I", out, 0, parsed["head"])
        out[0x24:SLOTS_AT] = parsed["middle"]
        for slot, value in parsed["slots"].items():
            struct.pack_into("<I", out, SLOTS_AT + 4 * slot, value)
        out[len(out) - len(parsed["tail"]):] = parsed["tail"]
        return bytes(out)
    if family == ANIMATION:
        out = bytearray(size)
        struct.pack_into("<I", out, 0, parsed["fields"]["frame_count"])
        for index, value in enumerate(parsed["frame_pointers"]):
            struct.pack_into("<I", out, ANIMATION_PREFIX + 4 * index, value)
        return bytes(out)
    if family == FRAME:
        out = bytearray(size)
        struct.pack_into("<I", out, 0, parsed["fields"]["piece_count"])
        struct.pack_into("<I", out, 4, parsed["fields"]["word_04"])
        names = [rule.name for rule in PIECE_FIELDS]
        for index, piece in enumerate(parsed["pieces"]):
            for word, name in enumerate(names):
                struct.pack_into("<I", out, FRAME_PREFIX + PIECE_SIZE * index + 4 * word,
                                 piece[name])
        return bytes(out)
    if family == INDEX:
        return b"".join(struct.pack("<I", address)
                        for address in parsed["fields"]["definition_addresses"])
    raise ValueError("%r is not a sprite family" % family)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return serialize(family, fields(rom, family, offset), size)


def round_trip(rom: bytes) -> dict[str, tuple[int, int]]:
    out = {}
    for family, rows in extents(rom).items():
        identical = sum(1 for offset, size in rows
                        if serialize_record(rom, family, offset, size) == rom[offset:offset + size])
        out[family] = (identical, len(rows))
    return out


def tables() -> dict[str, tuple]:
    return {DEFINITION: DEFINITION_HEAD_FIELDS, ANIMATION: ANIMATION_FIELDS, FRAME: FRAME_FIELDS}


def payload_for(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return serialize_record(rom, family, offset, size)


__all__ = ["ROM_BASE", "TABLE", "COUNT", "DEFINITION_START", "DEFINITION_END", "TABLE_END",
           "DEFINITION", "ANIMATION", "FRAME", "FAMILIES", "EXPECTED", "EXPECTED_BYTES",
           "TABLE_BYTES", "UNION_BYTES", "walk", "extents", "assert_contract", "fields",
           "serialize", "serialize_record", "round_trip", "tables", "payload_for",
           "ByteRule", "PairRule", "PointerRule", "WordRule"]
