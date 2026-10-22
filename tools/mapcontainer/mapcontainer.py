from __future__ import annotations

import bisect
import os
import struct
import sys
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Sequence

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "webfoot"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import intervals
import webfoot_lz

HEADER_SIZE = 8
MAX_PAYLOAD = 0x800
ROM_BASE = 0x08000000
ME_TABLE = 0x08E2E0
ME_COUNT = 452
ME_SIZE = 0x38
DOMINANT = 0x08008087
TERRAIN = 0x080088BD
SCREENBLOCK = {0x08007B63: 0x04, 0x0800897B: 0x1C}
KIND_HEADER = 1
LAYER_SLOTS = 4
CONTAINER = "generated"
RETAIL_KINDS = ("retail", "carve-out")
ROOT_EXTENT = 0x50
DOMINANT_PREFIX = 0x18
TILE_BANK_TABLE = 0x08179764


def root_arrays(rom: bytes) -> list[tuple[int, int]]:
    u32 = lambda offset: struct.unpack_from("<I", rom, offset)[0]
    bases = [u32(ME_TABLE + index * ME_SIZE + 0x2C) for index in range(ME_COUNT)]
    for index, pointer in enumerate(bases):
        if not ROM_BASE <= pointer < ROM_BASE + len(rom):
            raise MapContainerError("map entry %d holds %#010x at +0x2C" % (index, pointer))
    out = []
    for pointer in bases:
        base = pointer - ROM_BASE
        later = [other - ROM_BASE for other in bases if other > pointer]
        out.append((base, min(later) if later else base + ROOT_EXTENT))
    return out


def root_slot(rom: bytes, value: int) -> bool:
    site = value - ROM_BASE
    return (ROM_BASE <= value < ROM_BASE + len(rom)
            and site + ROOT_EXTENT <= len(rom)
            and struct.unpack_from("<I", rom, site + 0x4C)[0] == TILE_BANK_TABLE)


def root_slots(rom: bytes) -> list[list[int]]:
    u32 = lambda offset: struct.unpack_from("<I", rom, offset)[0]
    arrays = []
    for base, limit in root_arrays(rom):
        slots = []
        while base + 4 <= limit and root_slot(rom, u32(base)):
            slots.append(u32(base) - ROM_BASE)
            base += 4
        arrays.append(slots)
    return arrays


def map_roots(rom: bytes) -> list[int]:
    arrays = root_slots(rom)
    for index, slots in enumerate(arrays):
        if not slots:
            raise MapContainerError("map entry %d's +0x2C array holds no root" % index)
    return sorted({root for slots in arrays for root in slots})


def dominant_records(rom: bytes) -> list[int]:
    u32 = lambda offset: struct.unpack_from("<I", rom, offset)[0]
    found = set()
    for root in map_roots(rom):
        for slot in range(LAYER_SLOTS):
            record = u32(root + 0x14 + 4 * slot)
            if not ROM_BASE <= record < ROM_BASE + len(rom):
                continue
            site = record - ROM_BASE
            if u32(site) == DOMINANT:
                found.add(site)
    return sorted(found)


def container_offsets(rom: bytes) -> list[int]:
    u32 = lambda offset: struct.unpack_from("<I", rom, offset)[0]
    inrom = lambda address: ROM_BASE <= address < ROM_BASE + len(rom)
    pointers = set()
    handlers = {}
    for root in map_roots(rom):
        for slot in range(LAYER_SLOTS):
            rec = u32(root + 0x14 + 4 * slot)
            if not inrom(rec):
                continue
            site = rec - ROM_BASE
            handler = u32(site)
            handlers[handler] = handlers.get(handler, 0) + 1
            if handler == DOMINANT:
                for j in range(rom[site + 0x14] * rom[site + 0x15]):
                    pointers.add(u32(site + 0x18 + 4 * j))
            elif handler in SCREENBLOCK:
                pointers.add(u32(site + SCREENBLOCK[handler]))
            elif handler == TERRAIN:
                for j in range(rom[site + 4] * rom[site + 5]):
                    pointers.add(u32(site + 8 + 4 * j))
    print("layer handlers=%s" % {("%#010x" % key): value for key, value in sorted(handlers.items())})
    return sorted(pointer - ROM_BASE for pointer in pointers
                  if inrom(pointer) and pointer != 0)


def packed_container_offsets(rom: bytes, span: tuple[int, int], excluded: Sequence[tuple[int, int]],
                             maximum_output: int = webfoot_lz.DEFAULT_MAX_OUTPUT) -> list[int]:
    mask = bytearray(span[1] - span[0])
    for start, end in excluded:
        low, high = max(start, span[0]) - span[0], min(end, span[1]) - span[0]
        mask[low:high] = b"\x01" * (high - low)
    runs = []
    start = None
    for index, byte in enumerate(mask):
        if byte:
            if start is not None:
                runs.append((span[0] + start, span[0] + index))
                start = None
        elif start is None:
            start = index
    if start is not None:
        runs.append((span[0] + start, span[1]))
    found = set()
    for run_start, run_end in runs:
        offset = run_start
        while offset + 8 <= run_end:
            kind, declared = struct.unpack_from("<II", rom, offset)
            if kind > 2 or declared < 1 or declared > maximum_output \
                    or not webfoot_lz.looks_like_container(rom, offset):
                offset += 2
                continue
            try:
                container = webfoot_lz.validate_retail_termination(
                    rom, offset, maximum_output=maximum_output)
            except webfoot_lz.ContainerError:
                offset += 2
                continue
            if container.packed_end > run_end or container.packed_end <= offset:
                offset += 2
                continue
            if container.kind in (1, 2):
                found.add(offset)
            offset = container.packed_end
    return sorted(found)


class MapContainerError(ValueError):
    pass


@dataclass(frozen=True)
class Member:
    kind: int
    declared_size: int
    payload: bytes
    stored_size: int
    offset: int


@dataclass(frozen=True)
class Section:
    kind: str
    start: int
    end: int


ROOT = "root_record"
DOMINANT_FAMILY = "dominant_layer_record"
SCREENBLOCK_A = "layer_record_screenblock_a"
SCREENBLOCK_B = "layer_record_screenblock_b"
TERRAIN_FAMILY = "layer_record_terrain"
ROOT_TABLE = "root_table_record"
ROOT_POINTER = "root_pointer_record"
RECORD_FAMILIES = (ROOT, DOMINANT_FAMILY, SCREENBLOCK_A, SCREENBLOCK_B, TERRAIN_FAMILY,
                   ROOT_TABLE, ROOT_POINTER)
LAYER_FACTORIES = {0x08007B63: SCREENBLOCK_A, 0x0800897B: SCREENBLOCK_B, 0x080088BD: TERRAIN_FAMILY}


class PointerRule:

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return "PointerRule(%r)" % self.name


class WordRule:

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return "WordRule(%r)" % self.name


class ByteRule:

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return "ByteRule(%r)" % self.name


class PairRule:

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return "PairRule(%r)" % self.name


class CountRule:

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return "CountRule(%r)" % self.name


class ChunksRule:

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return "ChunksRule(%r)" % self.name


ROOT_FIELDS = (WordRule("scene_word"), WordRule("grid"), WordRule("word_08"), WordRule("word_0c"),
               WordRule("word_10"), PointerRule("layer_0"), PointerRule("layer_1"),
               PointerRule("layer_2"), PointerRule("layer_3"), WordRule("word_24"),
               WordRule("word_28"), WordRule("word_2c"), WordRule("rect"), PointerRule("word_34"),
               PointerRule("word_38"), WordRule("word_3c"), WordRule("word_40"),
               WordRule("word_44"), PointerRule("word_48"), PointerRule("tile_bank_table"))
DOMINANT_FIELDS = (WordRule("factory"),
                   WordRule("declared_size"),
                   WordRule("word_08"),
                   WordRule("word_0c"),
                   WordRule("word_10"),
                   CountRule("chunk_rows"),
                   CountRule("chunk_columns"),
                   PairRule("word_16"),
                   ChunksRule("chunk_pointers"))
DOMINANT_FACTORY = DOMINANT
SCREENBLOCK_A_FIELDS = (WordRule("factory"), PointerRule("container"), WordRule("mirror"))
SCREENBLOCK_B_FIELDS = (WordRule("factory"), WordRule("word_04"), WordRule("word_08"),
                        WordRule("word_0c"), WordRule("word_10"), WordRule("word_14"),
                        WordRule("word_18"), PointerRule("container"))
TERRAIN_FIELDS = (WordRule("factory"), CountRule("cols"), CountRule("rows"), PairRule("zero"),
                  ChunksRule("chunk_pointers"))
SCREENBLOCK_A_EXTENT = 0x0C
SCREENBLOCK_B_EXTENT = 0x20
TERRAIN_PREFIX = 8
ROOT_TABLE_EXTENT = 24
ROOT_POINTER_EXTENT = 4
ROOT_TABLE_FIELDS = (WordRule("word_00"), WordRule("word_04"), WordRule("word_08"),
                     WordRule("word_0c"), WordRule("word_10"), WordRule("word_14"))
ROOT_POINTER_FIELDS = (PointerRule("pointer"),)


def screenblock_a_extent(rom: bytes, offset: int, fields: tuple) -> int:
    return SCREENBLOCK_A_EXTENT


def screenblock_b_extent(rom: bytes, offset: int, fields: tuple) -> int:
    return SCREENBLOCK_B_EXTENT


def terrain_extent(rom: bytes, offset: int, fields: tuple) -> int:
    return TERRAIN_PREFIX + 4 * (rom[offset + 4] * rom[offset + 5])


def layer_record_sites(rom: bytes) -> dict[str, list[int]]:
    out: dict[str, set[int]] = {name: set() for name in LAYER_FACTORIES.values()}
    for root in map_roots(rom):
        for slot in range(LAYER_SLOTS):
            record = struct.unpack_from("<I", rom, root + 0x14 + 4 * slot)[0]
            if not ROM_BASE <= record < ROM_BASE + len(rom):
                continue
            site = record - ROM_BASE
            family = LAYER_FACTORIES.get(struct.unpack_from("<I", rom, site)[0])
            if family is not None:
                out[family].add(site)
    return {name: sorted(sites) for name, sites in out.items()}


def record_specs() -> dict[str, tuple]:
    return {ROOT: (ROOT_FIELDS, root_extent),
            DOMINANT_FAMILY: (DOMINANT_FIELDS, dominant_extent),
            SCREENBLOCK_A: (SCREENBLOCK_A_FIELDS, screenblock_a_extent),
            SCREENBLOCK_B: (SCREENBLOCK_B_FIELDS, screenblock_b_extent),
            TERRAIN_FAMILY: (TERRAIN_FIELDS, terrain_extent),
            ROOT_TABLE: (ROOT_TABLE_FIELDS, root_table_extent),
            ROOT_POINTER: (ROOT_POINTER_FIELDS, root_pointer_extent)}


def root_table_extent(rom: bytes, offset: int, fields: tuple) -> int:
    return ROOT_TABLE_EXTENT


def root_pointer_extent(rom: bytes, offset: int, fields: tuple) -> int:
    return ROOT_POINTER_EXTENT


def root_extent(rom: bytes, offset: int, fields: tuple) -> int:
    return ROOT_EXTENT


def dominant_extent(rom: bytes, offset: int, fields: tuple) -> int:
    return DOMINANT_PREFIX + 4 * (rom[offset + 0x14] * rom[offset + 0x15])


MODE_ROW = "child_list_row"
MODE_CHILD = 0x08007675
MODE_CONSTRUCTOR = 0x080072CD
MODE_HANDLERS = (MODE_CHILD, MODE_CONSTRUCTOR)
MODE_SECOND = 0x0800776D
MODE_OBJECT = 0x18
MODE_MAX_CHILDREN = 32
MODE_TAGS = frozenset(range(0x0351, 0x0380))


def mode_row_fields(rom: bytes, offset: int, end: int):
    u32 = lambda at: struct.unpack_from("<I", rom, at)[0]
    cursor = offset
    lists = []
    while cursor + 4 <= end:
        count, tag = rom[cursor], struct.unpack_from("<H", rom, cursor + 2)[0]
        if not 1 <= count <= MODE_MAX_CHILDREN or tag not in MODE_TAGS:
            break
        size = 4 + 4 * count
        if cursor + size > end:
            return None
        pointers = tuple(u32(cursor + 4 + 4 * index) for index in range(count))
        for pointer in pointers:
            if not ROM_BASE <= pointer < ROM_BASE + len(rom):
                return None
        lists.append((cursor, count, rom[cursor + 1], tag, pointers))
        cursor += size
    index = ()
    if lists:
        if cursor + 4 * len(lists) > end:
            return None
        index = tuple(u32(cursor + 4 * entry) for entry in range(len(lists)))
        if index != tuple(ROM_BASE + start for start, _, _, _, _ in lists):
            return None
        cursor += 4 * len(lists)
    objects = []
    while (cursor + MODE_OBJECT <= end and u32(cursor) in MODE_HANDLERS
           and u32(cursor + 4) == MODE_SECOND):
        objects.append(tuple(u32(cursor + 4 * word) for word in range(MODE_OBJECT // 4)))
        cursor += MODE_OBJECT
    if cursor == offset:
        return None
    return {"lists": lists, "index": index, "objects": objects}, cursor - offset


def serialize_mode_row(rom: bytes, family: str, offset: int, size: int) -> bytes:
    parsed = mode_row_fields(rom, offset, offset + size)
    if parsed is None or parsed[1] != size:
        raise MapContainerError("%s at %#x does not parse to its %d bytes"
                                % (family, offset, size))
    parts = parsed[0]
    out = bytearray()
    for _, count, word_01, tag, pointers in parts["lists"]:
        out += struct.pack("<BBH", count, word_01, tag)
        out += b"".join(struct.pack("<I", pointer) for pointer in pointers)
    out += b"".join(struct.pack("<I", pointer) for pointer in parts["index"])
    for words in parts["objects"]:
        out += b"".join(struct.pack("<I", word) for word in words)
    if len(out) != size:
        raise MapContainerError("%s at %#x packs to %d bytes, not its %d"
                                % (family, offset, len(out), size))
    return bytes(out)


def mode_row_chain(rom: bytes, at: int, high: int) -> list[tuple[int, int]]:
    out, cursor = [], at
    while cursor < high:
        parsed = mode_row_fields(rom, cursor, high)
        if parsed is None:
            break
        out.append((cursor, parsed[1]))
        cursor += parsed[1]
    return out


def mode_row_tail(rom: bytes, low: int, high: int) -> list[tuple[int, int]]:
    at = low
    while at + 4 <= high:
        got = mode_row_chain(rom, at, high)
        if got and got[-1][0] + got[-1][1] == high:
            return got
        at += 2
    return []


def mode_row_sites(rom: bytes, span: tuple, claimed: Sequence[tuple]) -> list[tuple[int, int]]:
    gaps, cursor = [], span[0]
    for low, high in sorted((max(span[0], low), min(span[1], high)) for low, high in claimed):
        if low > cursor:
            gaps.append((cursor, low))
        cursor = max(cursor, high)
    if cursor < span[1]:
        gaps.append((cursor, span[1]))
    rows = []
    for low, high in gaps:
        got = mode_row_chain(rom, low, high)
        end = got[-1][0] + got[-1][1] if got else low
        if end < high:
            got += mode_row_tail(rom, end, high)
        rows.extend(got)
    return rows


def record_extents(rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
    specs = record_specs()
    out = {name: [] for name in RECORD_FAMILIES}
    for root in map_roots(rom):
        out[ROOT].append((root, root_extent(rom, root, specs[ROOT][0])))
    for site in dominant_records(rom):
        out[DOMINANT_FAMILY].append((site, dominant_extent(rom, site, specs[DOMINANT_FAMILY][0])))
    for name, sites in layer_record_sites(rom).items():
        out[name] = [(site, specs[name][1](rom, site, specs[name][0])) for site in sites]
    out[ROOT_TABLE] = root_table_sites(rom)
    out[ROOT_POINTER] = root_pointer_sites(rom)
    return {name: rows for name, rows in out.items()} if family is None else {family: out[family]}


def root_table_sites(rom: bytes) -> list[tuple[int, int]]:
    u32 = lambda offset: struct.unpack_from("<I", rom, offset)[0]
    out = []
    for root in map_roots(rom):
        count, base = u32(root + 0x24), u32(root + 0x28)
        if not count or not ROM_BASE <= base < ROM_BASE + len(rom):
            continue
        out.extend((base - ROM_BASE + ROOT_TABLE_EXTENT * index, ROOT_TABLE_EXTENT)
                   for index in range(count))
    return out


def root_pointer_sites(rom: bytes) -> list[tuple[int, int]]:
    u32 = lambda offset: struct.unpack_from("<I", rom, offset)[0]
    out = []
    for root in map_roots(rom):
        count, base = u32(root + 0x40), u32(root + 0x44)
        if not count or not ROM_BASE <= base < ROM_BASE + len(rom):
            continue
        out.extend((base - ROM_BASE + ROOT_POINTER_EXTENT * index, ROOT_POINTER_EXTENT)
                   for index in range(count))
    return out


def record_fields(rom: bytes, family: str, offset: int, size: int | None = None) -> dict:
    fields = record_specs()[family][0]
    cursor = 0
    parsed = {}
    for rule in fields:
        if isinstance(rule, ChunksRule):
            count = 1
            for other in fields:
                if isinstance(other, CountRule):
                    count *= parsed[other.name]
            words = []
            for index in range(count):
                chunk = struct.unpack_from("<I", rom, offset + cursor + 4 * index)[0]
                if chunk and not (ROM_BASE <= chunk < ROM_BASE + len(rom)):
                    raise MapContainerError("%s at %#x chunk %d is %#010x, not a ROM address"
                                            % (family, offset, index, chunk))
                if chunk and struct.unpack_from("<I", rom, chunk - ROM_BASE)[0] != KIND_HEADER:
                    raise MapContainerError("%s at %#x chunk %d names %#010x, not a kind-%d header"
                                            % (family, offset, index, chunk, KIND_HEADER))
                words.append(chunk)
            parsed[rule.name] = tuple(words)
            cursor += 4 * count
            continue
        if isinstance(rule, (ByteRule, CountRule)):
            parsed[rule.name] = rom[offset + cursor]
            cursor += 1
            continue
        if isinstance(rule, PairRule):
            parsed[rule.name] = struct.unpack_from("<H", rom, offset + cursor)[0]
            cursor += 2
            continue
        value = struct.unpack_from("<I", rom, offset + cursor)[0]
        if isinstance(rule, PointerRule) and not (ROM_BASE <= value < ROM_BASE + len(rom)):
            raise MapContainerError("%s at %#x %s is %#010x, not a ROM address"
                                    % (family, offset, rule.name, value))
        parsed[rule.name] = value
        cursor += 4
    if size is not None and cursor != size:
        raise MapContainerError("%s at %#x parses to %d bytes, its extent is %d"
                                % (family, offset, cursor, size))
    return parsed


def serialize_fields(family: str, parsed: dict) -> bytes:
    out = bytearray()
    for rule in record_specs()[family][0]:
        if isinstance(rule, ChunksRule):
            for chunk in parsed[rule.name]:
                out += struct.pack("<I", chunk)
        elif isinstance(rule, (ByteRule, CountRule)):
            out.append(parsed[rule.name])
        elif isinstance(rule, PairRule):
            out += struct.pack("<H", parsed[rule.name])
        else:
            out += struct.pack("<I", parsed[rule.name])
    return bytes(out)


def serialize_record(rom: bytes, family: str, offset: int, size: int) -> bytes:
    return serialize_fields(family, record_fields(rom, family, offset, size))


def decode(blob: bytes, offset: int, maximum_output: int = MAX_PAYLOAD) -> Member:
    container = webfoot_lz.validate_retail_termination(
        blob, offset, maximum_output=maximum_output)
    if container.packed_end > len(blob):
        raise MapContainerError("container at %#x runs past the %d-byte blob"
                                % (offset, len(blob)))
    return Member(container.kind, container.declared_size, container.data,
                  container.packed_size, offset)


def early_extent(blob: bytes, offset: int, maximum_output: int = MAX_PAYLOAD) -> int:
    return webfoot_lz.unpack(blob, offset, maximum_output=maximum_output).packed_size


def decode_many(blob: bytes, offsets: Sequence[int]) -> list[Member]:
    if list(offsets) != sorted(set(offsets)):
        raise MapContainerError("offsets must be a strictly increasing list")
    return [decode(blob, offset) for offset in offsets]


def encode(member: Member, compress: Callable[[bytes], bytes]) -> bytes:
    if member.declared_size != len(member.payload):
        raise MapContainerError("declared %d against a %d-byte payload"
                                % (member.declared_size, len(member.payload)))
    blob = compress(member.payload)
    header = struct.pack("<II", member.kind, member.declared_size)
    if blob[:HEADER_SIZE] != header:
        raise MapContainerError("compressor header %s is not %s"
                                % (blob[:HEADER_SIZE].hex(), header.hex()))
    if len(blob) != member.stored_size:
        raise MapContainerError("re-encoded %d bytes against a stored %d"
                                % (len(blob), member.stored_size))
    return blob


def encode_run(members: Sequence[Member], compress: Callable[[bytes], bytes],
               pool: ThreadPoolExecutor | None = None) -> bytes:
    if pool is None:
        blobs = [encode(member, compress) for member in members]
    else:
        blobs = list(pool.map(lambda member: encode(member, compress), members))
    blob = b"".join(blobs)
    length = sum(member.stored_size for member in members)
    if len(blob) != length:
        raise MapContainerError("run is %d bytes against its members' %d" % (len(blob), length))
    return blob


def clip(rows: Sequence[tuple[int, int]], span: tuple[int, int]) -> list[tuple[int, int]]:
    return [(offset, offset + length) for offset, length in rows
            if span[0] <= offset and offset + length <= span[1]]


def plan_sections(span_start: int, span_end: int, offsets: Sequence[int],
                  sizes: Sequence[int], carve_outs: frozenset[int],
                  records: Sequence[str] = ()) -> list[Section]:
    if len(offsets) != len(sizes) or list(offsets) != sorted(set(offsets)):
        raise MapContainerError("offsets and sizes must agree and increase")
    if records and len(records) != len(offsets):
        raise MapContainerError("%d record kinds against %d extents" % (len(records), len(offsets)))
    if not offsets:
        raise MapContainerError("the span holds no tokens")
    claimed = []
    for index, offset in enumerate(offsets):
        if not span_start <= offset or offset + sizes[index] > span_end:
            raise MapContainerError("token %#x is outside the span" % offset)
        if offset in carve_outs:
            kind = "carve-out"
        elif records:
            kind = records[index]
        else:
            kind = CONTAINER
        claimed.append((offset, offset + sizes[index], kind))
    for previous, following in zip(claimed, claimed[1:]):
        if previous[1] > following[0]:
            raise MapContainerError("tokens %#x and %#x overlap" % (previous[0], following[0]))
    sections: list[Section] = []
    if span_start < claimed[0][0]:
        sections.append(Section("retail", span_start, claimed[0][0]))
    for start, end, kind in claimed:
        if sections and sections[-1].end > start:
            raise MapContainerError("token %#x claims a byte twice" % start)
        if sections and sections[-1].end < start:
            sections.append(Section("retail", sections[-1].end, start))
        if sections and sections[-1].kind == kind and sections[-1].end == start:
            sections[-1] = Section(kind, sections[-1].start, end)
        else:
            sections.append(Section(kind, start, end))
    if sections[-1].end < span_end:
        sections.append(Section("retail", sections[-1].end, span_end))
    for previous, following in zip(sections, sections[1:]):
        if previous.end != following.start:
            raise MapContainerError("sections do not tile: %#x then %#x"
                                    % (previous.end, following.start))
    if sections[0].start != span_start or sections[-1].end != span_end:
        raise MapContainerError("the sections span %#x..%#x" % (sections[0].start,
                                                               sections[-1].end))
    return sections


def record_sections(span_start: int, span_end: int,
                    extents: dict[str, Sequence[tuple[int, int]]],
                    families: Sequence[str] = RECORD_FAMILIES) -> tuple[list[int], list[int],
                                                                         list[str]]:
    tokens: list[tuple[int, int, str]] = []
    for family in families:
        for start, end in intervals.union(extents[family]):
            if not (span_start <= start and end <= span_end):
                raise MapContainerError("%s record run %#x..%#x is outside the block"
                                        % (family, start, end))
            tokens.append((start, end, family))
    tokens.sort()
    for previous, following in zip(tokens, tokens[1:]):
        if previous[1] > following[0]:
            raise MapContainerError("record runs %#x and %#x overlap" % (previous[0],
                                                                         following[0]))
    return ([start for start, _, _ in tokens], [end - start for start, end, _ in tokens],
            [family for _, _, family in tokens])


def record_members(sections: Sequence[Section], extents: dict[str, Sequence[tuple[int, int]]],
                   families: Sequence[str] = RECORD_FAMILIES
                   ) -> dict[int, list[tuple[int, int, str]]]:
    runs = sorted((section.start, section.end, section.kind) for section in sections
                  if section.kind in families)
    starts = [start for start, _, _ in runs]
    buckets: dict[int, list[tuple[int, int, str]]] = {start: [] for start in starts}
    for family in families:
        for start, end in extents[family]:
            index = bisect.bisect_right(starts, start) - 1
            if index < 0:
                continue
            run_start, run_end, kind = runs[index]
            if not (run_start <= start < run_end):
                continue
            if kind != family:
                raise MapContainerError("the %s record at %#x sits in a %s run"
                                        % (family, start, kind))
            buckets[run_start].append((start, end - start, family))
    for start, end, kind in runs:
        if sum(size for _, size, _ in buckets[start]) != end - start:
            raise MapContainerError("record run %#x does not hold exactly its records" % start)
    return buckets


def section_kinds(families: Sequence[str] = RECORD_FAMILIES) -> frozenset:
    return frozenset((CONTAINER,) + tuple(families) + RETAIL_KINDS)


def members_of(sections: Sequence[Section], members: Sequence[Member],
               container_provenance: str = CONTAINER) -> dict[int, list[Member]]:
    by_offset = {member.offset: member for member in members}
    runs = {}
    for section in sections:
        if section.kind != container_provenance:
            continue
        run = [by_offset[offset] for offset in sorted(by_offset)
               if section.start <= offset < section.end]
        if sum(member.stored_size for member in run) != section.end - section.start:
            raise MapContainerError("run %#x does not hold exactly its members" % section.start)
        runs[section.start] = run
    return runs
