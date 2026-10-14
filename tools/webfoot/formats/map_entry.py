
from __future__ import annotations

from dataclasses import dataclass, fields
import os
from pathlib import Path
import struct

from .. import capability
from ..binary import BinaryAddressError, GbaRomAddress
from ..hashing import hash_stream
from ..profile import (
    MapEntryTableProfile,
    RomProfile,
    RomProfileCatalog,
)
from ..rom import RomChangedError, RomIdentification, identify_rom


MAP_ENTRY_SIZE = 0x38
_MAP_ENTRY_STRUCT = struct.Struct("<12B11I")


class MapEntryError(ValueError):
    """Base error for MapEntry parsing, configuration, or validation."""


class MapEntryLengthError(MapEntryError):
    """Raised when a record is not exactly 0x38 bytes."""


class MapEntryValueError(MapEntryError):
    """Raised when a field cannot fit its original binary width."""


class MapEntryProfileError(MapEntryError, capability.CapabilityError):
    """Raised when a ROM/profile is not authorized for this format.

    Inherits `CapabilityError` so the shared gate raises this exact type and
    existing callers keep catching what they already caught.
    """


@dataclass(frozen=True, slots=True)
class MapEntryField:
    offset: int
    width: int
    name: str


#: disassembly that `trigger_count_raw` (`+0x04`) is the engine's placement-run
#: count: the map loader at 0x08008C9E runs `ldrb r0,[r0,#4]` as the bound of a
#: counted loop that indexes the pointer array at `scripts_pointer_raw` (`+0x14`).
#: It is NOT the count of the `triggers_pointer_raw` (`+0x10`) slot array; that
MAP_ENTRY_LAYOUT = (
    MapEntryField(0x00, 1, "output_raw"),
    MapEntryField(0x01, 1, "zone_raw"),
    MapEntryField(0x02, 1, "area_raw"),
    MapEntryField(0x03, 1, "variation_raw"),
    MapEntryField(0x04, 1, "trigger_count_raw"),
    MapEntryField(0x05, 1, "script_count_raw"),
    MapEntryField(0x06, 1, "item_count_raw"),
    MapEntryField(0x07, 1, "object_count_raw"),
    MapEntryField(0x08, 1, "npc_count_raw"),
    MapEntryField(0x09, 1, "flags_raw"),
    MapEntryField(0x0A, 1, "unknown_0a"),
    MapEntryField(0x0B, 1, "unknown_0b"),
    MapEntryField(0x0C, 4, "unknown_0c"),
    MapEntryField(0x10, 4, "triggers_pointer_raw"),
    MapEntryField(0x14, 4, "scripts_pointer_raw"),
    MapEntryField(0x18, 4, "items_pointer_raw"),
    MapEntryField(0x1C, 4, "objects_pointer_raw"),
    MapEntryField(0x20, 4, "npcs_pointer_raw"),
    MapEntryField(0x24, 4, "music_id_raw"),
    MapEntryField(0x28, 4, "variation_script_pointer_raw"),
    MapEntryField(0x2C, 4, "variation_array_pointer_raw"),
    MapEntryField(0x30, 4, "entry_script_pointer_raw"),
    MapEntryField(0x34, 4, "exit_script_pointer_raw"),
)


@dataclass(frozen=True, slots=True)
class MapEntry:
    """All physical fields in one 0x38-byte record, without dereferencing."""

    output_raw: int
    zone_raw: int
    area_raw: int
    variation_raw: int
    trigger_count_raw: int
    script_count_raw: int
    item_count_raw: int
    object_count_raw: int
    npc_count_raw: int
    flags_raw: int
    unknown_0a: int
    unknown_0b: int
    unknown_0c: int
    triggers_pointer_raw: int
    scripts_pointer_raw: int
    items_pointer_raw: int
    objects_pointer_raw: int
    npcs_pointer_raw: int
    music_id_raw: int
    variation_script_pointer_raw: int
    variation_array_pointer_raw: int
    entry_script_pointer_raw: int
    exit_script_pointer_raw: int

    @classmethod
    def from_bytes(cls, data: bytes | bytearray | memoryview) -> "MapEntry":
        if len(data) != MAP_ENTRY_SIZE:
            raise MapEntryLengthError(
                f"MapEntry must be exactly 0x{MAP_ENTRY_SIZE:X} bytes; got {len(data)}"
            )
        return cls(*_MAP_ENTRY_STRUCT.unpack(data))

    def to_bytes(self) -> bytes:
        values = tuple(getattr(self, item.name) for item in fields(self))
        for layout, value in zip(MAP_ENTRY_LAYOUT, values, strict=True):
            maximum = (1 << (layout.width * 8)) - 1
            if type(value) is not int or not 0 <= value <= maximum:
                raise MapEntryValueError(
                    f"{layout.name} must be an unsigned {layout.width * 8}-bit integer"
                )
        encoded = _MAP_ENTRY_STRUCT.pack(*values)
        if len(encoded) != MAP_ENTRY_SIZE:
            raise AssertionError("internal MapEntry serializer size mismatch")
        return encoded


@dataclass(frozen=True, slots=True)
class MapEntryRecord:
    index: int
    file_offset: int
    entry: MapEntry
    original_bytes: bytes


@dataclass(frozen=True, slots=True)
class MapEntryTable:
    identification: RomIdentification
    table_address: GbaRomAddress
    table_offset: int
    records: tuple[MapEntryRecord, ...]


@dataclass(frozen=True, slots=True)
class RoundTripMismatch:
    index: int
    file_offset: int
    record_byte_offset: int


@dataclass(frozen=True, slots=True)
class MapEntryValidationResult:
    table: MapEntryTable
    serialized_count: int
    mismatches: tuple[RoundTripMismatch, ...]
    byte_mismatch_count: int

    @property
    def passed(self) -> bool:
        return not self.mismatches


def _file_identity(stat_result: os.stat_result) -> tuple[int, int, int, int]:
    return (
        stat_result.st_dev,
        stat_result.st_ino,
        stat_result.st_size,
        stat_result.st_mtime_ns,
    )


def _require_target_profile(identification: RomIdentification) -> RomProfile:
    """Fail closed unless this exact ROM is verified and declares the table.
    TOOLKIT-005 removed the fourth check requiring the profile id to equal one
    constant naming Buu's Fury. Structure still gates the codec:
    `resolve_map_entry_table_range` refuses any record size other than
    `MAP_ENTRY_SIZE`, so a profile whose map records are not this shape is
    rejected on its layout rather than on the game's name. That is the check
    which should have been carrying the weight all along - Legacy of Goku II
    also has a 0x38-stride map table, but its fields are laid out differently,
    so it must not declare `map_entries` against this codec.
    """
    return capability.require(
        identification,
        capability.Capability.MAP_ENTRIES,
        subsystem="MapEntry access",
        error_type=MapEntryProfileError,
        check_header=True,
    )


def resolve_map_entry_table_range(
    table: MapEntryTableProfile,
    rom_size: int,
) -> tuple[int, int]:
    if table.record_size != MAP_ENTRY_SIZE:
        raise MapEntryProfileError(
            f"configured map-entry size must be 0x{MAP_ENTRY_SIZE:X}; "
            f"got 0x{table.record_size:X}"
        )
    try:
        table_offset = table.address.to_file_offset(rom_size)
    except BinaryAddressError as exc:
        raise MapEntryProfileError(str(exc)) from exc
    total_size = table.count * table.record_size
    if total_size > rom_size - table_offset:
        raise MapEntryProfileError("configured map-entry table extends beyond the ROM")
    return table_offset, total_size


def read_map_entry_table(
    path: str | Path,
    catalog: RomProfileCatalog,
) -> MapEntryTable:
    """Identify *path*, then read the complete target table without writing."""
    source = Path(path)
    identification = identify_rom(source, catalog)
    profile = _require_target_profile(identification)
    table_profile = profile.map_entries
    assert table_profile is not None

    with source.open("rb") as stream:
        before = os.fstat(stream.fileno())
        hashes, _ = hash_stream(stream)
        after_hash = os.fstat(stream.fileno())
        if hashes != identification.hashes:
            raise RomChangedError(f"ROM identity changed before table read: {source}")

        table_offset, total_size = resolve_map_entry_table_range(
            table_profile, before.st_size
        )
        stream.seek(table_offset)
        table_bytes = stream.read(total_size)
        after_read = os.fstat(stream.fileno())

    path_after = source.stat()
    before_identity = _file_identity(before)
    if (
        before_identity != _file_identity(after_hash)
        or before_identity != _file_identity(after_read)
        or before_identity != _file_identity(path_after)
    ):
        raise RomChangedError(f"ROM changed while map entries were read: {source}")
    if len(table_bytes) != total_size:
        raise MapEntryError(
            f"short map-entry table read: expected {total_size}, got {len(table_bytes)}"
        )

    records = []
    for index in range(table_profile.count):
        relative = index * MAP_ENTRY_SIZE
        original = table_bytes[relative : relative + MAP_ENTRY_SIZE]
        records.append(
            MapEntryRecord(
                index=index,
                file_offset=table_offset + relative,
                entry=MapEntry.from_bytes(original),
                original_bytes=original,
            )
        )
    return MapEntryTable(
        identification=identification,
        table_address=table_profile.address,
        table_offset=table_offset,
        records=tuple(records),
    )


def validate_map_entry_round_trips(
    path: str | Path,
    catalog: RomProfileCatalog,
) -> MapEntryValidationResult:
    table = read_map_entry_table(path, catalog)
    mismatches = []
    byte_mismatch_count = 0
    for record in table.records:
        encoded = record.entry.to_bytes()
        if encoded != record.original_bytes:
            differing_offsets = tuple(
                index
                for index, (actual, expected) in enumerate(
                    zip(encoded, record.original_bytes, strict=True)
                )
                if actual != expected
            )
            byte_mismatch_count += len(differing_offsets)
            first_difference = differing_offsets[0]
            mismatches.append(
                RoundTripMismatch(
                    index=record.index,
                    file_offset=record.file_offset,
                    record_byte_offset=first_difference,
                )
            )
    return MapEntryValidationResult(
        table=table,
        serialized_count=len(table.records),
        mismatches=tuple(mismatches),
        byte_mismatch_count=byte_mismatch_count,
    )
