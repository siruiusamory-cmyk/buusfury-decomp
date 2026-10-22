from __future__ import annotations

import struct

from mapcontainer import PairRule, PointerRule, WordRule

ROM_BASE = 0x08000000
ROM_END = 0x08800000
STRIDE = 12
FIELDS = (PointerRule("data_ptr"), WordRule("flags"), PairRule("byte_length"), PairRule("unit"))


class Spec:

    def __init__(self, directory, block, base, count, block_start, block_end, low_words, units,
                 unit_count=None, length_range=None, tied=False):
        self.directory = directory
        self.block = block
        self.families = (directory, block)
        self.base = base
        self.count = count
        self.array_end = base + STRIDE * count
        self.block_start = block_start
        self.block_end = block_end
        self.block_bytes = block_end - block_start
        self.gap = base - block_end
        self.low_words = low_words
        self.units = units
        self.unit_count = unit_count
        self.length_range = length_range
        self.tied = tied
        self.contract = {"records": count, "bytes": STRIDE * count, "blocks": count,
                         "block_bytes": self.block_bytes, "first": block_start, "last_end": block_end}


def decode_stream(blob: bytes) -> list[int]:
    return [value - 256 if value > 127 else value for value in blob]


def encode_stream(samples) -> bytes:
    out = bytearray()
    for sample in samples:
        if sample < -128 or sample > 127:
            raise ValueError("sample %d is outside the signed byte range" % sample)
        out.append(sample + 256 if sample < 0 else sample)
    return bytes(out)


class Directory:

    def __init__(self, spec):
        self.spec = spec

    def fields(self, rom: bytes, offset: int, size: int = STRIDE) -> dict:
        parsed = {}
        cursor = 0
        for rule in FIELDS:
            width = 2 if isinstance(rule, PairRule) else 4
            if cursor + width > size:
                raise ValueError("%s at %#x: the field map overruns its %d-byte extent"
                                 % (self.spec.directory, offset, size))
            if width == 2:
                parsed[rule.name] = struct.unpack_from("<H", rom, offset + cursor)[0]
            else:
                value = struct.unpack_from("<I", rom, offset + cursor)[0]
                if isinstance(rule, PointerRule) and not ROM_BASE <= value < ROM_END:
                    raise ValueError("%s at %#x %s is %#010x, not a ROM address"
                                     % (self.spec.directory, offset, rule.name, value))
                parsed[rule.name] = value
            cursor += width
        if cursor != size:
            raise ValueError("%s at %#x parses to %d bytes, its extent is %d"
                             % (self.spec.directory, offset, cursor, size))
        return parsed

    def serialize(self, parsed: dict, size: int = STRIDE) -> bytes:
        out = bytearray()
        for rule in FIELDS:
            out += struct.pack("<H" if isinstance(rule, PairRule) else "<I", parsed[rule.name])
        if len(out) != size:
            raise ValueError("%s serializes to %d bytes, its extent is %d"
                             % (self.spec.directory, len(out), size))
        return bytes(out)

    def block_blob(self, rom: bytes, offset: int, size: int) -> bytes:
        for index in range(self.spec.count):
            record = self.fields(rom, self.spec.base + STRIDE * index, STRIDE)
            if record["data_ptr"] - ROM_BASE != offset:
                continue
            if record["byte_length"] != size:
                raise ValueError("%s record %d names %d B at %#x, the block holds %d"
                                 % (self.spec.directory, index, record["byte_length"], offset,
                                    size))
            return encode_stream(decode_stream(rom[offset:offset + size]))
        raise ValueError("%s holds no record naming %#x" % (self.spec.directory, offset))

    def serialize_record(self, rom: bytes, family: str, offset: int, size: int) -> bytes:
        if family == self.spec.block:
            if self.spec.tied:
                return self.block_blob(rom, offset, size)
            return rom[offset:offset + size]
        if family != self.spec.directory:
            raise ValueError("%s is not this module's family" % family)
        return self.serialize(self.fields(rom, offset, size), size)

    def directory_rows(self, rom: bytes) -> list[tuple[int, int]]:
        return [(self.spec.base + STRIDE * index, STRIDE) for index in range(self.spec.count)]

    def block_rows(self, rom: bytes) -> list[tuple[int, int]]:
        return [(record["data_ptr"] - ROM_BASE, record["byte_length"])
                for record in (self.fields(rom, offset, size)
                               for offset, size in self.directory_rows(rom))]

    def assert_contract(self, rom: bytes) -> dict:
        spec = self.spec
        records = [self.fields(rom, offset, size) for offset, size in self.directory_rows(rom)]
        for index, (record, following) in enumerate(zip(records, records[1:])):
            if record["data_ptr"] + record["byte_length"] != following["data_ptr"]:
                raise ValueError("%s record %d ends at %#010x, the next starts at %#010x"
                                 % (spec.directory, index, record["data_ptr"] + record["byte_length"],
                                    following["data_ptr"]))
        last = records[-1]
        if last["data_ptr"] + last["byte_length"] != ROM_BASE + spec.block_end:
            raise ValueError("%s record %d ends at %#010x, not %#010x"
                             % (spec.directory, spec.count - 1,
                                last["data_ptr"] + last["byte_length"], ROM_BASE + spec.block_end))
        low = {}
        units = {}
        for record in records:
            low[record["flags"] & 0xFFFF] = low.get(record["flags"] & 0xFFFF, 0) + 1
            units[record["unit"]] = units.get(record["unit"], 0) + 1
        if low != spec.low_words:
            raise ValueError("%s flags' low 16 bits measure %s, the contract says %s"
                             % (spec.directory, low, spec.low_words))
        if spec.unit_count is not None and len(units) != spec.unit_count:
            raise ValueError("%s units hold %d distinct values, the contract says %d"
                             % (spec.directory, len(units), spec.unit_count))
        for unit, count in spec.units.items():
            if units.get(unit, 0) != count:
                raise ValueError("%s unit %d appears %d times, the contract says %d"
                                 % (spec.directory, unit, units.get(unit, 0), count))
        blocks = self.block_rows(rom)
        if blocks[0][0] != spec.block_start:
            raise ValueError("%s's first block starts at %#x, not %#x"
                             % (spec.directory, blocks[0][0], spec.block_start))
        for (start, length), (next_start, _) in zip(blocks, blocks[1:]):
            if start + length != next_start:
                raise ValueError("%s's blocks do not tile: %#x ends at %#x, %#x starts"
                                 % (spec.directory, start, start + length, next_start))
        if sum(length for _, length in blocks) != spec.block_bytes:
            raise ValueError("%s's blocks sum to %d B, the contract says %d"
                             % (spec.directory, sum(length for _, length in blocks), spec.block_bytes))
        if spec.length_range is not None:
            lengths = [length for _, length in blocks]
            if (min(lengths), max(lengths)) != spec.length_range:
                raise ValueError("%s's block lengths measure %d..%d, the contract says %d..%d"
                                 % (spec.directory, min(lengths), max(lengths),
                                    spec.length_range[0], spec.length_range[1]))
        if spec.base - spec.block_end != spec.gap:
            raise ValueError("%s's blocks end at %#x and its table starts at %#x, not %d B apart"
                             % (spec.directory, spec.block_end, spec.base, spec.gap))
        measured = {"records": len(records), "bytes": len(records) * STRIDE, "blocks": len(blocks),
                    "block_bytes": sum(length for _, length in blocks), "first": blocks[0][0],
                    "last_end": blocks[-1][0] + blocks[-1][1]}
        if measured != spec.contract:
            raise ValueError("%s measures %s, the contract says %s"
                             % (spec.directory, measured, spec.contract))
        return measured

    def extents(self, rom: bytes, family: str = None) -> dict[str, list[tuple[int, int]]]:
        if family not in (None,) + self.spec.families:
            raise ValueError("%s is not this module's family" % family)
        self.assert_contract(rom)
        rows = {self.spec.directory: self.directory_rows(rom), self.spec.block: self.block_rows(rom)}
        return rows if family is None else {family: rows[family]}

    def round_trip(self, rom: bytes) -> dict[str, dict[str, int]]:
        out = {}
        for family in self.spec.families:
            equal = bytes_ = 0
            for offset, size in self.extents(rom, family)[family]:
                equal += self.serialize_record(rom, family, offset, size) == rom[offset:offset + size]
                bytes_ += size
            out[family] = {"records": self.spec.count, "equal": equal, "bytes": bytes_}
        return out


def install(namespace: dict, spec: Spec) -> Directory:
    directory = Directory(spec)
    namespace.update(
        DIRECTORY=spec.directory, BLOCK=spec.block, FAMILY=spec.directory, FAMILIES=spec.families,
        SPEC=spec, BASE=spec.base, STRIDE=STRIDE, COUNT=spec.count, ARRAY_END=spec.array_end,
        BLOCK_START=spec.block_start, BLOCK_END=spec.block_end, BLOCK_BYTES=spec.block_bytes,
        GAP=spec.gap, ROM_BASE=ROM_BASE, ROM_END=ROM_END, CONTRACT=spec.contract,
        LOW_WORDS=spec.low_words, UNITS=spec.units, TIED=spec.tied,
        fields=directory.fields, serialize=directory.serialize,
        serialize_record=directory.serialize_record, block_blob=directory.block_blob,
        directory_rows=directory.directory_rows, block_rows=directory.block_rows,
        assert_contract=directory.assert_contract,
        extents=directory.extents, round_trip=directory.round_trip)
    return directory
