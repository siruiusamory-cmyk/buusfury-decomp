from __future__ import annotations

import os
import struct
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import intervals  # noqa: E402

ROM_SIZE = 0x800000
ROM_BASE = 0x08000000

REGION_A = (0x071C90, 0x0945C0)
REGION_B = (0x179764, 0x179A50)

FIRST_MIB_TABLE = 0x071C90
FIRST_MIB_HEADER = 32
FIRST_MIB_ROW = 8
FIRST_MIB_ROWS = 393

ME_TABLE = 0x08E2E0
ME_COUNT = 452
ME_SIZE = 0x38

PLACEMENT_FACTORY = 0x0800FD55
PLACEMENT_PREFIX = 0x1C
PLACEMENT_MAX_CHILDREN = 4

SIBLING_FACTORIES = (0x08017DA3, 0x080111A9)
SIBLING_EXTENT = 0x1C

CHILD_EXTENT = 0x0C

METHOD_RECORD_EXTENT = 0x10
METHOD_RECORD_METHOD = 0x0800A7A1
METHOD_RECORD_FLAGS = (0x40, 0x80)

BANK_TABLE = 0x179764
BANK_COUNT = 187

FAMILY_ORDER = ("map_entry_table", "placement_record", "placement_child",
                "sibling_object_record",
                "placement_descriptor", "object_slot_pointer_array", "entry_pointer_array_18",
                "entry_pointer_array_1c", "entry_record_array_20", "variation_source_words",
                "tile_bank_pointer_table", "firstmib_consumer_table", "method_record")
FAMILY_INDEX = {name: index for index, name in enumerate(FAMILY_ORDER)}
REGION = {"map_entry_table": REGION_A, "placement_record": REGION_A,
          "placement_child": REGION_A,
          "sibling_object_record": REGION_A, "placement_descriptor": REGION_A,
          "object_slot_pointer_array": REGION_A, "entry_pointer_array_18": REGION_A,
          "entry_pointer_array_1c": REGION_A, "entry_record_array_20": REGION_A,
          "variation_source_words": REGION_A, "tile_bank_pointer_table": REGION_B,
          "firstmib_consumer_table": REGION_A, "method_record": REGION_A}

ENTRY_ARRAYS = (("entry_pointer_array_18", 15, 5, 4),
                ("entry_pointer_array_1c", 16, 6, 4),
                ("entry_record_array_20", 17, 7, 8))

MEASURED = {
    "map_entry_table": (1, 452, 25312),
    "object_slot_pointer_array": (316, 1898, 7592),
    "entry_pointer_array_18": (53, 125, 500),
    "entry_pointer_array_1c": (12, 13, 52),
    "entry_record_array_20": (15, 28, 224),
    "variation_source_words": (316, 1898, 7592),
    "placement_record": (404, 1559, 49988),
    "placement_child": (55, 80, 960),
    "placement_descriptor": (130, 130, 1040),
    "sibling_object_record": (229, 339, 9196),
    "tile_bank_pointer_table": (1, 187, 748),
    "firstmib_consumer_table": (1, 394, 3176),
    "method_record": (68, 68, 1088),
}
PLAN = {
    "region_a_extent_bytes": 106720,
    "region_a_union_bytes": 100572,
    "region_a_runs": 400,
    "region_a_gaps": 399,
    "union_components": 401,
    "clipped": {
        "map_entry_table": 0,
        "placement_record": 152,
        "placement_child": 188,
        "sibling_object_record": 476,
        "placement_descriptor": 144,
        "object_slot_pointer_array": 60,
        "entry_pointer_array_18": 0,
        "entry_pointer_array_1c": 0,
        "entry_record_array_20": 0,
        "variation_source_words": 5020,
        "tile_bank_pointer_table": 0,
        "firstmib_consumer_table": 0,
        "method_record": 108,
    },
    "non_whole_fragments": 88,
}


def _u32(rom: bytes, offset: int) -> int:
    if not 0 <= offset <= len(rom) - 4:
        raise StructuredError("word read at %#x is outside the image" % offset)
    return struct.unpack_from("<I", rom, offset)[0]


def _address(rom: bytes, value: int, who: str) -> int:
    if not ROM_BASE <= value < ROM_BASE + len(rom):
        raise StructuredError("%s: %#010x is not a ROM address" % (who, value))
    return value - ROM_BASE


class StructuredError(ValueError):
    pass


@dataclass(frozen=True)
class MapEntry:

    fields: tuple[int, ...]

    @classmethod
    def from_bytes(cls, data: bytes) -> "MapEntry":
        if len(data) != ME_SIZE:
            raise StructuredError("map entry must be %d bytes, got %d" % (ME_SIZE, len(data)))
        return cls(struct.unpack("<12B11I", data))

    def to_bytes(self) -> bytes:
        return struct.pack("<12B11I", *self.fields)

    @property
    def trigger_count(self) -> int:
        return self.fields[4]

    @property
    def scripts_pointer(self) -> int:
        return self.fields[14]

    @property
    def variation_array_pointer(self) -> int:
        return self.fields[20]


@dataclass(frozen=True)
class PlacementRecord:

    words: tuple[int, ...]

    @classmethod
    def from_bytes(cls, data: bytes) -> "PlacementRecord":
        if len(data) < PLACEMENT_PREFIX:
            raise StructuredError("truncated placement prefix")
        header = struct.unpack_from("<7I", data)
        count = header[6]
        if not 1 <= count <= PLACEMENT_MAX_CHILDREN:
            raise StructuredError("placement child count %d is outside 1..%d"
                                  % (count, PLACEMENT_MAX_CHILDREN))
        size = PLACEMENT_PREFIX + 4 * count
        if len(data) != size:
            raise StructuredError("placement extent must be %d bytes, got %d" % (size, len(data)))
        if header[0] != PLACEMENT_FACTORY:
            raise StructuredError("placement factory %#010x is not %#010x"
                                  % (header[0], PLACEMENT_FACTORY))
        return cls(struct.unpack("<%dI" % (7 + count), data))

    def to_bytes(self) -> bytes:
        return struct.pack("<%dI" % len(self.words), *self.words)

    @property
    def child_count(self) -> int:
        return self.words[6]

    @property
    def descriptor_pointer(self) -> int:
        return self.words[5]


@dataclass(frozen=True)
class PlacementChild:

    word_00: int
    half_04: int
    half_06: int
    half_08: int
    half_0A: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "PlacementChild":
        if len(data) != CHILD_EXTENT:
            raise StructuredError("placement child must be %d bytes, got %d"
                                  % (CHILD_EXTENT, len(data)))
        word = struct.unpack_from("<I", data)[0]
        if not word & 1 or not ROM_BASE <= word < ROM_BASE + ROM_SIZE:
            raise StructuredError("placement child's first word %#010x is not a Thumb pointer"
                                  % word)
        return cls(word, *struct.unpack_from("<4H", data, 4))

    def to_bytes(self) -> bytes:
        return struct.pack("<I4H", self.word_00, self.half_04, self.half_06, self.half_08,
                           self.half_0A)


@dataclass(frozen=True)
class MethodRecord:

    method: int
    flags: int
    halves: tuple[int, int, int, int]

    @classmethod
    def from_bytes(cls, data: bytes) -> "MethodRecord":
        if len(data) != METHOD_RECORD_EXTENT:
            raise StructuredError("method record must be %d bytes, got %d"
                                  % (METHOD_RECORD_EXTENT, len(data)))
        method, flags = struct.unpack_from("<2I", data)
        if method != METHOD_RECORD_METHOD:
            raise StructuredError("method record's word %#010x is not %#010x"
                                  % (method, METHOD_RECORD_METHOD))
        if flags not in METHOD_RECORD_FLAGS:
            raise StructuredError("method record's flags %#x are not one of %s"
                                  % (flags, ["%#x" % flag for flag in METHOD_RECORD_FLAGS]))
        return cls(method, flags, struct.unpack_from("<4H", data, 8))

    def to_bytes(self) -> bytes:
        return struct.pack("<2I4H", self.method, self.flags, *self.halves)


@dataclass(frozen=True)
class DescriptorRecord:

    words: tuple[int, ...]

    @classmethod
    def from_bytes(cls, data: bytes) -> "DescriptorRecord":
        if len(data) != 8:
            raise StructuredError("descriptor must be 8 bytes, got %d" % len(data))
        return cls(struct.unpack("<2I", data))

    def to_bytes(self) -> bytes:
        return struct.pack("<2I", *self.words)


@dataclass(frozen=True)
class SiblingObjectRecord:

    factory: int
    tail: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> "SiblingObjectRecord":
        if len(data) != SIBLING_EXTENT:
            raise StructuredError("sibling record must be %d bytes, got %d"
                                  % (SIBLING_EXTENT, len(data)))
        factory = struct.unpack_from("<I", data)[0]
        if factory not in SIBLING_FACTORIES:
            raise StructuredError("sibling factory %#010x is not one of %s"
                                  % (factory, ["%#010x" % f for f in SIBLING_FACTORIES]))
        return cls(factory, data[4:])

    def to_bytes(self) -> bytes:
        return struct.pack("<I", self.factory) + self.tail


@dataclass(frozen=True)
class Word:

    value: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "Word":
        if len(data) != 4:
            raise StructuredError("word must be 4 bytes, got %d" % len(data))
        return cls(struct.unpack("<I", data)[0])

    def to_bytes(self) -> bytes:
        return struct.pack("<I", self.value)


@dataclass(frozen=True)
class EightByteRecord:

    words: tuple[int, ...]

    @classmethod
    def from_bytes(cls, data: bytes) -> "EightByteRecord":
        if len(data) != 8:
            raise StructuredError("8 B record must be 8 bytes, got %d" % len(data))
        return cls(struct.unpack("<2I", data))

    def to_bytes(self) -> bytes:
        return struct.pack("<2I", *self.words)


@dataclass(frozen=True)
class FirstMibHeader:

    iwram: tuple[int, ...]
    rom: tuple[int, ...]
    indices: tuple[int, ...]

    @classmethod
    def from_bytes(cls, data: bytes) -> "FirstMibHeader":
        if len(data) != FIRST_MIB_HEADER:
            raise StructuredError("consumer-table header must be %d bytes, got %d"
                                  % (FIRST_MIB_HEADER, len(data)))
        return cls(struct.unpack_from("<4I", data), struct.unpack_from("<2I", data, 0x10),
                   tuple(data[0x18:0x20]))

    def to_bytes(self) -> bytes:
        return (struct.pack("<4I", *self.iwram) + struct.pack("<2I", *self.rom)
                + bytes(self.indices))


@dataclass(frozen=True)
class FirstMibRow:

    values: tuple[int, ...]

    @classmethod
    def from_bytes(cls, data: bytes) -> "FirstMibRow":
        if len(data) != FIRST_MIB_ROW:
            raise StructuredError("consumer-table row must be %d bytes, got %d"
                                  % (FIRST_MIB_ROW, len(data)))
        return cls(struct.unpack("<4H", data))

    def to_bytes(self) -> bytes:
        return struct.pack("<4H", *self.values)


class FirstMibRecord:

    @staticmethod
    def from_bytes(data: bytes):
        if len(data) == FIRST_MIB_HEADER:
            return FirstMibHeader.from_bytes(data)
        return FirstMibRow.from_bytes(data)


CODEC = {
    "map_entry_table": (MapEntry, ME_SIZE),
    "object_slot_pointer_array": (Word, 4),
    "entry_pointer_array_18": (Word, 4),
    "entry_pointer_array_1c": (Word, 4),
    "entry_record_array_20": (EightByteRecord, 8),
    "variation_source_words": (Word, 4),
    "placement_record": (PlacementRecord, None),
    "placement_child": (PlacementChild, CHILD_EXTENT),
    "placement_descriptor": (DescriptorRecord, 8),
    "sibling_object_record": (SiblingObjectRecord, SIBLING_EXTENT),
    "tile_bank_pointer_table": (Word, 4),
    "firstmib_consumer_table": (FirstMibRecord, FIRST_MIB_ROW),
    "method_record": (MethodRecord, METHOD_RECORD_EXTENT),
}


def serialize(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return CODEC[family][0].from_bytes(rom[offset:offset + size]).to_bytes()


def map_entries(rom: bytes) -> list[tuple[int, MapEntry]]:
    out = []
    for index in range(ME_COUNT):
        offset = ME_TABLE + index * ME_SIZE
        out.append((offset, MapEntry.from_bytes(rom[offset:offset + ME_SIZE])))
    return out


def record_extents(rom: bytes) -> dict[str, list[tuple[int, int]]]:
    out = {name: [] for name in FAMILY_ORDER}
    for index in range(ME_COUNT):
        offset = ME_TABLE + index * ME_SIZE
        out["map_entry_table"].append((offset, ME_SIZE))
    for index in range(BANK_COUNT):
        offset = BANK_TABLE + 4 * index
        out["tile_bank_pointer_table"].append((offset, 4))
    out["firstmib_consumer_table"].append((FIRST_MIB_TABLE, FIRST_MIB_HEADER))
    for index in range(FIRST_MIB_ROWS):
        offset = FIRST_MIB_TABLE + FIRST_MIB_HEADER + FIRST_MIB_ROW * index
        out["firstmib_consumer_table"].append((offset, FIRST_MIB_ROW))
    for _, entry in map_entries(rom):
        count = entry.trigger_count
        if count and entry.scripts_pointer:
            base = _address(rom, entry.scripts_pointer, "MapEntry+0x14")
            for index in range(count):
                offset = base + 4 * index
                out["object_slot_pointer_array"].append((offset, 4))
                target = _u32(rom, offset)
                if not ROM_BASE <= target < ROM_BASE + len(rom):
                    continue
                site = target - ROM_BASE
                lead = _u32(rom, site)
                if lead == PLACEMENT_FACTORY:
                    size = PLACEMENT_PREFIX + 4 * _u32(rom, site + 0x18)
                    if not 1 <= _u32(rom, site + 0x18) <= PLACEMENT_MAX_CHILDREN:
                        raise StructuredError("placement child count %d at %#x"
                                              % (_u32(rom, site + 0x18), site))
                    PlacementRecord.from_bytes(rom[site:site + size])
                    out["placement_record"].append((site, size))
                    descriptor = _address(rom, _u32(rom, site + 0x14), "placement+0x14")
                    out["placement_descriptor"].append((descriptor, 8))
                    for child_index in range(_u32(rom, site + 0x18)):
                        target = _u32(rom, site + PLACEMENT_PREFIX + 4 * child_index)
                        if not ROM_BASE <= target < ROM_BASE + len(rom):
                            continue
                        child = target - ROM_BASE
                        child_lead = _u32(rom, child)
                        if child_lead == PLACEMENT_FACTORY or child_lead in SIBLING_FACTORIES:
                            continue
                        if child_lead & 1 and ROM_BASE <= child_lead < ROM_BASE + len(rom):
                            PlacementChild.from_bytes(rom[child:child + CHILD_EXTENT])
                            out["placement_child"].append((child, CHILD_EXTENT))
                elif lead in SIBLING_FACTORIES:
                    out["sibling_object_record"].append((site, SIBLING_EXTENT))
        if count:
            variation = _address(rom, entry.variation_array_pointer, "MapEntry+0x2C")
            for index in range(count):
                out["variation_source_words"].append((variation + 4 * index, 4))
        for family, word, count_byte, size in ENTRY_ARRAYS:
            length = entry.fields[count_byte]
            if not length:
                continue
            base = _address(rom, entry.fields[word], "MapEntry+0x%02X" % (4 * (word - 12) + 0x0C))
            for index in range(length):
                out[family].append((base + size * index, size))
    for offset in range(REGION_A[0], REGION_A[1] - METHOD_RECORD_EXTENT + 1, 4):
        if _u32(rom, offset) != METHOD_RECORD_METHOD:
            continue
        MethodRecord.from_bytes(rom[offset:offset + METHOD_RECORD_EXTENT])
        out["method_record"].append((offset, METHOD_RECORD_EXTENT))
    return {name: sorted(set(rows)) for name, rows in out.items()}


def extents(rom: bytes) -> dict[str, list[tuple[int, int]]]:
    out = {}
    for family, rows in record_extents(rom).items():
        low, high = REGION[family]
        kept = []
        for start, end in intervals.union((offset, offset + length) for offset, length in rows):
            start, end = max(start, low), min(end, high)
            if start < end:
                kept.append((start, end))
        out[family] = kept
    return out


def payload(rom: bytes, family: str, start: int, end: int, rows=None) -> bytes:
    size = end - start
    if size <= 0:
        raise StructuredError("%s extent %#x..%#x is empty" % (family, start, end))
    if rows is None:
        rows = record_extents(rom)[family]
    buffer = bytearray(size)
    filled = bytearray(size)
    for offset, length in rows:
        if offset + length <= start or offset >= end:
            continue
        blob = serialize(rom, family, offset, length)
        low, high = max(offset, start), min(offset + length, end)
        for position in range(low, high):
            value = blob[position - offset]
            if filled[position - start] and buffer[position - start] != value:
                raise StructuredError("%s records disagree at %#x" % (family, position))
            buffer[position - start] = value
            filled[position - start] = 1
    if not all(filled):
        missing = filled.index(0)
        raise StructuredError("%s extent %#x..%#x has no record for %#x"
                              % (family, start, end, start + missing))
    return bytes(buffer)


@dataclass(frozen=True)
class Member:

    key: int
    family: str
    start: int
    end: int
    extent_start: int
    extent_end: int
    whole: bool


@dataclass(frozen=True)
class Plan:
    extents: dict[str, tuple[tuple[int, int], ...]]
    members: tuple[Member, ...]
    kept: dict[str, tuple[tuple[int, int], ...]]
    clipped: dict[str, int]
    runs: tuple[tuple[int, int], ...]
    gaps: tuple[tuple[int, int], ...]
    whole_fragments: dict[str, int]
    non_whole_fragments: dict[str, int]
    union_components: int


def plan(rom: bytes) -> Plan:
    rom = bytes(rom)
    if len(rom) != ROM_SIZE:
        raise StructuredError("image is %d bytes, not %d" % (len(rom), ROM_SIZE))
    built_extents = extents(rom)
    items = [(end - start, FAMILY_INDEX[family], family, start, end)
             for family in FAMILY_ORDER for start, end in built_extents[family]]
    items.sort(key=lambda item: (-item[0], item[1]))
    low = min(REGION_A[0], REGION_B[0])
    high = max(REGION_A[1], REGION_B[1])
    owner = bytearray(high - low)
    for _, index, _, start, end in items:
        for position in range(start - low, end - low):
            if owner[position] == 0:
                owner[position] = index + 1

    members: list[Member] = []
    kept: dict[str, list[tuple[int, int]]] = {family: [] for family in FAMILY_ORDER}
    clipped: dict[str, int] = {family: 0 for family in FAMILY_ORDER}
    whole: dict[str, int] = {family: 0 for family in FAMILY_ORDER}
    broken: dict[str, int] = {family: 0 for family in FAMILY_ORDER}
    for _, index, family, start, end in items:
        mark = index + 1
        fragments = []
        run_start = None
        for position in range(start - low, end - low):
            if owner[position] == mark and run_start is None:
                run_start = position + low
            elif owner[position] != mark and run_start is not None:
                fragments.append((run_start, position + low))
                run_start = None
        if run_start is not None:
            fragments.append((run_start, end))
        kept[family].extend(fragments)
        clipped[family] += (end - start) - sum(b - a for a, b in fragments)
        for fragment_start, fragment_end in fragments:
            stride = CODEC[family][1]
            is_whole = ((fragment_end - fragment_start) % stride == 0) \
                if stride is not None else _placement_whole(rom, fragment_start, fragment_end)
            members.append(Member(start, family, fragment_start, fragment_end,
                                  start, end, is_whole))
            whole[family] += is_whole
            broken[family] += not is_whole

    members.sort(key=lambda member: member.key)
    tiled = intervals.union((member.start, member.end) for member in members)
    if sum(end - start for start, end in tiled) != sum(m.end - m.start for m in members):
        raise StructuredError("a byte is owned twice")

    in_region_a = [(start, end) for start, end in tiled
                   if start < REGION_A[1] and end > REGION_A[0]]
    gaps: list[tuple[int, int]] = []
    cursor = REGION_A[0]
    for start, end in in_region_a:
        if start > cursor:
            gaps.append((cursor, start))
        cursor = max(cursor, min(end, REGION_A[1]))
    if cursor < REGION_A[1]:
        gaps.append((cursor, REGION_A[1]))

    return Plan(extents={family: tuple(rows) for family, rows in built_extents.items()},
                members=tuple(members), kept={family: tuple(sorted(rows))
                                              for family, rows in kept.items()},
                clipped=clipped, runs=tuple(tiled), gaps=tuple(gaps),
                whole_fragments=whole, non_whole_fragments=broken,
                union_components=len(tiled))


def _placement_whole(rom: bytes, start: int, end: int) -> bool:
    offset = start
    while offset < end:
        count = _u32(rom, offset + 0x18)
        if not 1 <= count <= PLACEMENT_MAX_CHILDREN:
            return False
        size = PLACEMENT_PREFIX + 4 * count
        if offset + size > end:
            return False
        offset += size
    return offset == end


def round_trip(rom_bytes: bytes) -> dict[str, tuple[int, int, int, int]]:
    rom = bytes(rom_bytes)
    result = {}
    for family, rows in record_extents(rom).items():
        records_ok = bytes_ok = 0
        for offset, size in rows:
            blob = serialize(rom, family, offset, size)
            records_ok += 1
            bytes_ok += size if blob == rom[offset:offset + size] else 0
        result[family] = (records_ok, len(rows), bytes_ok, sum(size for _, size in rows))
    return result


def measured_extents(rom_bytes: bytes) -> dict[str, tuple[int, int, int]]:
    rom = bytes(rom_bytes)
    out = {}
    for family, rows in record_extents(rom).items():
        low, high = REGION[family]
        inside = [row for row in rows if low <= row[0] and row[0] + row[1] <= high]
        extents_rows = extents(rom)[family]
        out[family] = (len(extents_rows), len(inside),
                       sum(end - start for start, end in extents_rows))
    return out


def overlap_sites(rom_bytes: bytes) -> list[tuple[int, int, str, str, int, int]]:
    built = plan(bytes(rom_bytes))
    items = [(end - start, FAMILY_INDEX[family], family, start, end)
             for family in FAMILY_ORDER for start, end in built.extents[family]]
    sites = []
    for index, first in enumerate(items):
        for second in items[index + 1:]:
            low = max(first[3], second[3])
            high = min(first[4], second[4])
            if low >= high:
                continue
            if (first[0], -first[1]) > (second[0], -second[1]):
                owner, loser = first, second
            else:
                owner, loser = second, first
            sites.append((low, high, loser[2], owner[2], loser[0], owner[0]))
    return sorted(sites)


def assert_contract(rom_bytes: bytes) -> Plan:
    rom = bytes(rom_bytes)
    measured = measured_extents(rom)
    if measured != MEASURED:
        raise StructuredError("measured extents %s are not the recorded %s"
                              % (measured, MEASURED))
    built = plan(rom)
    extent_bytes = sum(end - start for rows in built.extents.values() for start, end in rows)
    for family in FAMILY_ORDER:
        if built.clipped[family] != PLAN["clipped"][family]:
            raise StructuredError("%s clipped %d bytes, recorded %d"
                                  % (family, built.clipped[family], PLAN["clipped"][family]))
    if extent_bytes != PLAN["region_a_extent_bytes"] + MEASURED["tile_bank_pointer_table"][2]:
        raise StructuredError("extent bytes %d" % extent_bytes)
    if sum(built.clipped.values()) != extent_bytes - PLAN["region_a_union_bytes"] \
            - MEASURED["tile_bank_pointer_table"][2]:
        raise StructuredError("clipped %d bytes do not account for extent_sum - union"
                              % sum(built.clipped.values()))
    region_a_runs = [run for run in built.runs if run[0] < REGION_A[1]]
    if sum(end - start for start, end in region_a_runs) != PLAN["region_a_union_bytes"]:
        raise StructuredError("region A union %d bytes"
                              % sum(end - start for start, end in region_a_runs))
    if len(region_a_runs) != PLAN["region_a_runs"] or len(built.gaps) != PLAN["region_a_gaps"]:
        raise StructuredError("region A runs=%d gaps=%d" % (len(region_a_runs), len(built.gaps)))
    if built.union_components != PLAN["union_components"]:
        raise StructuredError("union components %d" % built.union_components)
    if sum(end - start for start, end in region_a_runs) \
            + sum(end - start for start, end in built.gaps) != REGION_A[1] - REGION_A[0]:
        raise StructuredError("region A does not tile")
    if sum(built.non_whole_fragments.values()) != PLAN["non_whole_fragments"]:
        raise StructuredError("%d non-whole fragments, recorded %d"
                              % (sum(built.non_whole_fragments.values()),
                                 PLAN["non_whole_fragments"]))
    for family, (records_ok, records, bytes_ok, total) in round_trip(rom).items():
        if records_ok != records or bytes_ok != total:
            raise StructuredError("%s round trip %d/%d records, %d/%d bytes"
                                  % (family, records_ok, records, bytes_ok, total))
    return built
