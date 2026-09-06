"""Semantic access to a profile's map records, slot extents and connections.

TOOLKIT-007. This is the layer callers use::

    maps = load_maps(rom_path, catalog)
    entry = maps.entry(MapIdentity(39))
    maps.set_field(entry.identity, "music_id", 12)
    plan = maps.plan()

A caller names a map by identity and supplies a value. It never computes a file
offset and never sees a raw pointer, matching `webfoot.stats` and `webfoot.text`.

**Identity is not an address.** `MapIdentity` wraps the MapEntry table index,
which is what the game itself uses: the confirmed lookup `FUN_080089FC` selects
by index, and a transition's destination is recorded as zone/area bytes resolved
through that same table. An address would name where a record sits today; an
index names which map it is. No display name is invented - this project has
verified names for no map, and `webfoot.text` holds map-name strings whose
mapping to entry indices nothing here establishes.

**Two content rungs, from `webfoot.formats.map_slots`.** Every MapEntry with a
readable slot extent contributes its bytes losslessly; only the 35 arrays whose
every slot matches the one confirmed shape are additionally typed. See that
module for the corpus measurement that forced the split.

**Editing is fixed-width and semantic.** The editable fields are ones this
project has confirmed and whose value is self-contained - no pointer, no count,
nothing whose meaning depends on a structure the toolkit cannot rebuild. Editing
a pointer would require the reference machinery in `webfoot.layout` to rewrite
what points at it, and editing a count would change an extent this module reads
by that very count, so both are refused rather than half-supported.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Iterator

from . import capability
from .formats import map_slots as ms
from .formats import map_entry as me
from .formats.map_entry import MAP_ENTRY_SIZE, MapEntry, MapEntryProfileError
from .hashing import hash_stream
from .profile import RomProfile, RomProfileCatalog
from .rom import RomChangedError, RomIdentification, identify_rom
from .write import ByteChange, WritePlan, plan_changes


class MapError(ValueError):
    """Base error for semantic map access."""


class UnknownMapError(MapError):
    """Raised when an identity names no map in this table."""


class MapFieldError(MapError):
    """Raised when a field is not editable, or its value is out of range.

    One class for both because a caller does the same thing either way: fix the
    project and build again. The message carries which of the two it was.
    """


@dataclass(frozen=True, slots=True, order=True)
class MapIdentity:
    """A map's durable identity: its MapEntry table index.

    Ordered so reports and authored files sort numerically, and frozen so it can
    key a dict. `key` is the authored spelling, zero-padded so lexical order in
    a TOML file matches numeric order - `map:0009` before `map:0010`.
    """

    index: int

    def __post_init__(self) -> None:
        if type(self.index) is not int or self.index < 0:
            raise MapError("map identity must be a non-negative table index")

    @property
    def key(self) -> str:
        return f"map:{self.index:04d}"

    def __str__(self) -> str:
        return self.key


#: Editable MapEntry fields, with their inclusive value ranges.
#:
#: Every one is a self-contained value whose width is fixed by the record
#: layout, so an edit is a pure in-place overwrite with no reference to rewrite
#: and no extent to re-resolve. Deliberately excluded, each for a stated reason:
#:
#: * the five `*_pointer_raw` words and `variation_*_pointer_raw` - editing one
#:   moves a target this toolkit does not own; that is relocation, and
#:   `webfoot.relocation` proves it only against declared free space, which no
#:   verified profile has;
#: * the five `*_count_raw` bytes - this module resolves slot extents *by* the
#:   trigger count, so an edit would change what a later read decodes;
#: * `output_raw`, `unknown_0a`, `unknown_0b`, `unknown_0c` - UNKNOWN semantics,
#:   and ticket TOOLKIT-007 forbids mutating an unknown field merely because it
#:   is easy to reach.
#:
#: `music_id_raw` is a 32-bit field; the range below is its physical width, not
#: a claim about which ids the game has. `zone_raw` and `area_raw` are the bytes
#: the confirmed transition path (`candidate_map_loader_08008d44`) reads to
#: select a destination context, so they are the fields a map edit most
#: naturally reaches for.
MAP_FIELDS: dict[str, tuple[int, int]] = {
    "zone": (0, 0xFF),
    "area": (0, 0xFF),
    "variation": (0, 0xFF),
    "flags": (0, 0xFF),
    "music_id": (0, 0xFFFFFFFF),
}

#: Authored field name -> MapEntry attribute. The `_raw` suffix says "exactly
#: the bytes in the record"; an authored file should not carry it, because a
#: project stores semantic values.
_FIELD_ATTRIBUTES = {
    "zone": "zone_raw",
    "area": "area_raw",
    "variation": "variation_raw",
    "flags": "flags_raw",
    "music_id": "music_id_raw",
}


@dataclass(frozen=True, slots=True)
class SlotArrayEntry:
    """One map's slot extent, as loaded."""

    identity: MapIdentity
    array: ms.MapSlotArray

    @property
    def shape(self) -> ms.ArrayShape:
        return self.array.shape

    @property
    def is_typed(self) -> bool:
        return self.array.shape is ms.ArrayShape.TYPED


@dataclass(frozen=True, slots=True)
class MapEntryEntry:
    """One map record plus the provenance needed to rebuild it."""

    identity: MapIdentity
    record: MapEntry
    file_offset: int
    original_bytes: bytes


@dataclass(frozen=True, slots=True)
class SourceReference:
    """A typed slot's reference to a secondary structure.

    READ/DECODE only. `AUTO_RE_<local-state-name>:314` verifies the layout behind exactly
    one of these - MapEntry 39 slot[1] -> `0x080755C0`, whose halfwords at
    `+0x08` are the bounds `(481, 121, 615, 271)`. The other targets are
    distinct addresses whose layout no evidence establishes, so this dataclass
    records where the reference points and stops there.
    """

    entry_index: int
    slot_index: int
    type_raw: int
    target_address: int
    target_file_offset: int


@dataclass(frozen=True, slots=True)
class MapConnection:
    """One verified edge in the map graph.

    An edge exists only where a typed slot's reference is resolvable. The
    destination is deliberately absent: resolving a slot's source structure to a
    destination map index would require reading the zone/area bytes the loader
    uses out of a struct whose layout is verified for one instance. So an edge
    records that map X reaches a specific structure, not that X reaches map Y.
    Ticket TOOLKIT-007 sec 15 requires unknown destinations stay explicit.
    """

    source: MapIdentity
    reference: SourceReference

    @property
    def destination(self) -> MapIdentity | None:
        """Always None. The destination is not derivable from verified data."""
        return None


@dataclass(frozen=True, slots=True)
class MapGraph:
    """Every verified connection, in deterministic order."""

    connections: tuple[MapConnection, ...]

    def from_map(self, identity: MapIdentity) -> tuple[MapConnection, ...]:
        return tuple(c for c in self.connections if c.source == identity)

    @property
    def resolved_destination_count(self) -> int:
        return sum(1 for c in self.connections if c.destination is not None)


def _resolve_slot_extent(
    entry: MapEntry,
    image_size: int,
    table_range: tuple[int, int],
) -> tuple[int, int] | None:
    """This entry's readable slot extent as `(file_offset, size)`, or None.

    Returns None for every state with nothing safely readable: no count, no
    pointer, a pointer outside the cartridge window, an extent running past the
    end of the image, or an extent that collides with the MapEntry table. A
    count with a NULL pointer is *not* an error - 163 entries are in that state,
    and treating it as one would refuse the ROM this toolkit verifies.

    The table collision is not hypothetical. MapEntry 451 declares 4 slots at
    `0x0008E2D0`, whose extent covers the first 16 bytes of the map table at
    `0x0008E2E0` - the very table that indexes it. Its declared count therefore
    cannot be describing slots, which is a structural witness for the same
    conclusion the corpus measurement in `webfoot.formats.map_slots` reaches:
    `+0x04` is not a general slot count. Excluding it is not a workaround for a
    plan-overlap error; reading it would emit an extent that provably is not
    one, and the overlap `plan_changes` raises is that error surfacing.
    """
    count = entry.trigger_count_raw
    pointer = entry.triggers_pointer_raw
    if count == 0 or pointer == 0:
        return None
    if not ms.ROM_BASE <= pointer < ms.ROM_BASE + image_size:
        return None
    offset = pointer - ms.ROM_BASE
    size = count * ms.SLOT_SIZE
    if offset + size > image_size:
        return None
    table_start, table_end = table_range
    if offset < table_end and table_start < offset + size:
        return None
    return offset, size


class Maps:
    """Loaded map records and slot extents, plus any pending semantic edits.

    Edits accumulate in memory and become a `WritePlan` only when `plan()` is
    called, matching `StatTables`. Nothing here writes or knows a destination.
    """

    def __init__(
        self,
        *,
        identification: RomIdentification,
        profile: RomProfile,
        entries: tuple[MapEntryEntry, ...],
        arrays: tuple[SlotArrayEntry, ...],
        base_bytes: bytes,
    ) -> None:
        self.identification = identification
        self.profile = profile
        self._entries = {entry.identity: entry for entry in entries}
        self._order = tuple(entry.identity for entry in entries)
        self._arrays = {item.identity: item for item in arrays}
        self._array_order = tuple(item.identity for item in arrays)
        self._edits: dict[MapIdentity, dict[str, int]] = {}
        self._base_bytes = base_bytes

    # --- reading -------------------------------------------------------

    @property
    def base_bytes(self) -> bytes:
        """The exact image these records were decoded from."""
        return self._base_bytes

    def entries(self) -> Iterator[MapEntryEntry]:
        """Every map, in table order. Order is presentation, not identity."""
        for identity in self._order:
            yield self._entries[identity]

    def entry(self, identity: MapIdentity) -> MapEntryEntry:
        try:
            return self._entries[identity]
        except KeyError:
            raise UnknownMapError(f"no map record with identity {identity}") from None

    def slot_arrays(self) -> Iterator[SlotArrayEntry]:
        """Every readable slot extent, in map order."""
        for identity in self._array_order:
            yield self._arrays[identity]

    def slot_array(self, identity: MapIdentity) -> SlotArrayEntry | None:
        """This map's slot extent, or None when it has no readable one."""
        return self._arrays.get(identity)

    def field(self, identity: MapIdentity, name: str) -> int:
        """The current value of one editable field, including pending edits."""
        attribute = _require_field(name)
        pending = self._edits.get(identity, {})
        if name in pending:
            return pending[name]
        return getattr(self.entry(identity).record, attribute)

    # --- typed content -------------------------------------------------

    def source_references(self) -> tuple[SourceReference, ...]:
        """Every typed slot's reference, in deterministic order.

        Typed arrays only. An opaque array's second word is not established to
        be a pointer, so emitting one from it would manufacture a reference.
        """
        references: list[SourceReference] = []
        for item in self.slot_arrays():
            if not item.is_typed:
                continue
            for slot_index, slot in enumerate(item.array.slots):
                references.append(
                    SourceReference(
                        entry_index=item.identity.index,
                        slot_index=slot_index,
                        type_raw=slot.word0,
                        target_address=slot.word1,
                        target_file_offset=slot.source_file_offset,
                    )
                )
        # Sorted explicitly rather than relying on iteration order, so the graph
        # is deterministic by construction and not by accident of dict ordering.
        references.sort(key=lambda r: (r.entry_index, r.slot_index))
        return tuple(references)

    def graph(self) -> MapGraph:
        """The verified connection graph. Deterministic for a given ROM."""
        return MapGraph(
            connections=tuple(
                MapConnection(source=MapIdentity(ref.entry_index), reference=ref)
                for ref in self.source_references()
            )
        )

    # --- editing -------------------------------------------------------

    def set_field(self, identity: MapIdentity, name: str, value: int) -> None:
        """Stage one semantic field edit. Validates before recording it."""
        minimum, maximum = MAP_FIELDS[_require_field_name(name)]
        # Confirm the map exists before checking the value, so a typo in the
        # identity is reported as a missing map rather than as a bad value.
        self.entry(identity)
        if type(value) is not int:
            raise MapFieldError(f"{identity}.{name} must be an integer, got {value!r}")
        if not minimum <= value <= maximum:
            raise MapFieldError(
                f"{identity}.{name}={value} is outside the supported range "
                f"{minimum}..{maximum}"
            )
        self._edits.setdefault(identity, {})[name] = value

    # --- planning ------------------------------------------------------

    def changes(self) -> tuple[ByteChange, ...]:
        """Encode every record and every slot extent into attributed changes.

        Everything is encoded, not just what was edited, because that is what
        proves the round trip: an untouched record must re-encode to exactly its
        original bytes and `plan_changes` then drops it as a no-op. Returned as
        changes rather than a plan so a caller can merge subsystems into one
        plan, which is what makes cross-subsystem overlap a hard error.
        """
        changes: list[ByteChange] = []

        for item in self.entries():
            record = item.record
            edits = self._edits.get(item.identity, {})
            if edits:
                record = _with_fields(record, edits)
            changes.append(
                ByteChange(
                    offset=item.file_offset,
                    old=item.original_bytes,
                    new=record.to_bytes(),
                    owner=str(item.identity),
                    reason=_reason(item.identity, edits),
                )
            )

        for array_entry in self.slot_arrays():
            array = array_entry.array
            changes.append(
                ByteChange(
                    offset=array.file_offset,
                    old=array.original_bytes,
                    new=array.to_bytes(),
                    owner=f"{array_entry.identity}:slots",
                    reason=(
                        f"{array.slot_count} {array.shape.value.lower()} slot(s) "
                        "unchanged"
                    ),
                )
            )

        return tuple(changes)

    def plan(self) -> WritePlan:
        """Validate this subsystem's changes alone and return an applicable plan."""
        return plan_changes(
            self._base_bytes,
            self.changes(),
            profile_id=self.profile.id,
            base_sha256=self.identification.hashes.sha256,
        )


def _require_field_name(name: str) -> str:
    if name not in MAP_FIELDS:
        supported = ", ".join(sorted(MAP_FIELDS))
        raise MapFieldError(
            f"{name!r} is not an editable map field; this toolkit edits: {supported}"
        )
    return name


def _require_field(name: str) -> str:
    return _FIELD_ATTRIBUTES[_require_field_name(name)]


def _with_fields(record: MapEntry, edits: dict[str, int]) -> MapEntry:
    """A copy of `record` with `edits` applied. `MapEntry` is frozen."""
    values = {field.name: getattr(record, field.name) for field in me.MAP_ENTRY_LAYOUT}
    for name, value in edits.items():
        values[_FIELD_ATTRIBUTES[name]] = value
    return MapEntry(**values)


def _reason(identity: MapIdentity, edits: dict[str, int]) -> str:
    if not edits:
        return "map unchanged"
    return f"map edit: {', '.join(sorted(edits))}"


def load_maps(path: str | Path, catalog: RomProfileCatalog) -> Maps:
    """Identify `path`, then load its complete map table and slot extents.

    The ROM's identity is re-checked after the read, mirroring `identify_rom`,
    so an image that changes underneath is an error rather than a silent
    mis-decode.
    """
    source = Path(path)
    identification = identify_rom(source, catalog)
    profile = capability.require(
        identification,
        capability.Capability.MAP_ENTRIES,
        subsystem="map access",
        error_type=MapEntryProfileError,
        check_header=True,
    )
    table_profile = profile.map_entries
    assert table_profile is not None

    with source.open("rb") as stream:
        before = os.fstat(stream.fileno())
        hashes, _ = hash_stream(stream)
        if hashes != identification.hashes:
            raise RomChangedError(f"ROM identity changed before map read: {source}")
        stream.seek(0)
        image = stream.read()
        after = os.fstat(stream.fileno())

    def identity_of(stat: os.stat_result) -> tuple[int, int, int, int]:
        return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)

    if identity_of(before) != identity_of(after) or identity_of(before) != identity_of(
        source.stat()
    ):
        raise RomChangedError(f"ROM changed while maps were read: {source}")

    table_offset, table_size = me.resolve_map_entry_table_range(
        table_profile, len(image)
    )
    table_range = (table_offset, table_offset + table_size)

    entries: list[MapEntryEntry] = []
    arrays: list[SlotArrayEntry] = []
    for index in range(table_profile.count):
        offset = table_offset + index * MAP_ENTRY_SIZE
        original = image[offset : offset + MAP_ENTRY_SIZE]
        record = MapEntry.from_bytes(original)
        identity = MapIdentity(index)
        entries.append(
            MapEntryEntry(
                identity=identity,
                record=record,
                file_offset=offset,
                original_bytes=original,
            )
        )

        extent = _resolve_slot_extent(record, len(image), table_range)
        if extent is None:
            continue
        array_offset, size = extent
        arrays.append(
            SlotArrayEntry(
                identity=identity,
                array=ms.decode_slot_array(
                    image[array_offset : array_offset + size],
                    entry_index=index,
                    file_offset=array_offset,
                    image_size=len(image),
                ),
            )
        )

    return Maps(
        identification=identification,
        profile=profile,
        entries=tuple(entries),
        arrays=tuple(arrays),
        base_bytes=image,
    )
