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
from .binary import BinaryAddressError, GbaRomAddress
from .formats import map_placements as mp
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


@dataclass(frozen=True, slots=True, order=True)
class PlacementIdentity:
    """Stable identity for one factory-led placement record.

    TOOLKIT-008. Identity is `(map index, index within that map's array)` and
    nothing else. It deliberately excludes the record's ROM offset and every
    runtime address: `docs/research/AUTO_RE_<local-state-name>` records that this project
    already lost time once by treating reusable EWRAM actor slots as stable
    identity, and a physical offset would break the moment anything moved.
    """

    map_index: int
    placement_index: int

    def __post_init__(self) -> None:
        if type(self.map_index) is not int or self.map_index < 0:
            raise MapFieldError("placement map index must be a non-negative integer")
        if type(self.placement_index) is not int or self.placement_index < 0:
            raise MapFieldError("placement index must be a non-negative integer")

    @property
    def key(self) -> str:
        return f"map:{self.map_index:04d}/placement:{self.placement_index:04d}"

    def __str__(self) -> str:
        return self.key


@dataclass(frozen=True, slots=True)
class PlacementEntry:
    """One placement record plus the provenance needed to rebuild it."""

    identity: PlacementIdentity
    record: mp.PlacementRecord
    file_offset: int
    original_bytes: bytes
    #: Index of this record's pointer within the map's ENGINE-owned object array.
    #: TOOLKIT-025: this is not the same as `identity.placement_index`. The array is
    #: heterogeneous - sibling-family objects interleave with placements - so a map
    #: whose slot 1 holds a sibling has its second placement at slot 2. Writing a
    #: placement reference at `placement_index * 4` corrupted exactly that case
    #: (map 17, slot 0x00072A38). The slot index is canonical layout provenance and
    #: is preserved rather than recomputed.
    #:
    #: Deliberately NOT defaulted. A default of 0 is silently wrong for every record
    #: after the first, and it produced exactly that failure - overlapping reference
    #: sources - when a construction site omitted it. Every caller states the slot.
    slot_index: int


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
    placement_offsets: tuple[tuple[int, int], ...] = (),
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

    TOOLKIT-008 found 40 more extents in exactly that state, by the same test.
    A declared extent that covers any byte of a factory-led placement record is
    refused whole, because the placement family gives an independent reading of
    those bytes and the two cannot both be right:

    * **33 of the 40** have their first record starting at byte 4 mod 8 - *mid
      slot*. A record straddling a slot boundary is not a slot array with a
      record after it; it is a count that was never describing slots.
    * MapEntry 146 declares 12 slots whose extent walks through three complete
      records: `slots[2]` holds the factory word `0x0800FD55`, and `slots[5]`
      and `slots[6]` split one record's constant tail across a slot boundary.
    * Two slots in the corpus were classified TYPED purely because a record's
      tail constants happen to satisfy the `{type, source_ref}` shape test.

    That TOOLKIT-008 decision used the legacy fixed-tail subset (1,295).
    TOOLKIT-017 protects the full variable-length record extents, descriptors
    and owned scripts. Four additional opaque extents are refused; the typed
    subset is unchanged. See PLACEMENT_CODEC.md for corrected accounting.

    The extent is refused rather than truncated. Truncating would keep whatever
    prefix precedes the first record, and 33 of the 40 cannot be cut on a slot
    boundary at all, so a truncated extent would still emit fabricated slots.
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
    for record_offset, record_size in placement_offsets:
        if offset < record_offset + record_size and record_offset < offset + size:
            return None
    return offset, size


def _declared_run(contract, index: int, record: MapEntry) -> tuple[int, int] | None:
    """The contract's declared run for one map, or None when it declares none.

    TOOLKIT-025 removed a silent `(pointer, 0)` fallback here. A map absent from the
    frozen contract used to be modelled as owning zero object slots, which is how
    map 138 - 21 engine-counted slots, 19 of them placements - reached the census as
    an empty map. Absence of provenance is not evidence of emptiness, so a missing
    entry now yields None, which means "no declared run to cross-check" and lets the
    derived MapEntry traversal stand alone. It never means "this map is empty".
    """
    declared = contract['runs'].get(index)
    if declared is None:
        return None
    return declared


def _resolve_object_slots(record: MapEntry, image: bytes) -> tuple[mp.ObjectSlot, ...]:
    """Every engine-owned object slot this map declares, in exact array order.

    The count is `trigger_count_raw` (`+0x04`) and the base is `scripts_pointer_raw`
    (`+0x14`); both names are upstream-INFERRED and are read here without being
    believed - TOOLKIT-024 proved what the engine does with these two fields, and
    that proof, not the name, is why they are used. The result is heterogeneous:
    placement-family and sibling-family targets interleave, and the order is
    canonical.

    An array reaching into the MapEntry table is refused whole, on the same
    reasoning `_resolve_slot_extent` refuses MapEntry 451: a structure that
    consumes the table indexing it is not that structure.
    """
    pointer = record.scripts_pointer_raw
    count = record.trigger_count_raw
    if not pointer or not count:
        return ()
    try:
        array_offset = GbaRomAddress(pointer).to_file_offset(len(image))
    except BinaryAddressError:
        return ()
    try:
        return mp.iter_object_slots(image, array_offset, count)
    except mp.MapPlacementLengthError:
        return ()


def _resolve_placements(
    record: MapEntry,
    image: bytes,
    table_range: tuple[int, int],
    claimed: dict[int, int],
    entry_index: int,
    declared_run: tuple[int, int] | None = None,
) -> tuple[int, ...]:
    """File offsets of the placement records this map owns, in array order.

    The array is located by `scripts_pointer_raw` (`+0x14`). TOOLKIT-017 uses
    trusted profile run counts, never `script_count_raw` (`+0x05`). Historical
    TOOLKIT-008 walking covered 215 maps; only two declared counts matched that
    legacy subset. What `+0x05` counts remains UNKNOWN.

    That the placement array hangs off the field upstream named "scripts" is an
    observation about where the pointer lives, not a claim that these records
    are scripts. `docs/reverse-engineering.md` records every one of those names
    as `INFERRED` from `DragonByteZ`, with no consumer identified in the pinned
    disassembly, so this resolver reads the field and names nothing.

    An array that reaches into the MapEntry table is refused whole, on the same
    reasoning `_resolve_slot_extent` refuses MapEntry 451: a structure that
    consumes the table indexing it is not that structure.

    Exclusive ownership is a MEASURED property of the canonical image - walking
    every engine-counted object array reaches 1,559 placement records with none
    claimed twice - so a second claim is raised rather than skipped. Dropping it
    silently would give the caller a shorter array with no indication that the
    walk had left the extent it believed it was reading.

    TOOLKIT-025: the bound is `trigger_count_raw` (`+0x04`), read straight from the
    MapEntry, NOT the historical `contract['runs']` count. TOOLKIT-024 proved that
    byte is the engine's own loop bound (`ldrb` at 0x08008CA2 and 0x08008CD2), and
    the frozen contract was measured to be wrong in two independent ways: five maps
    stored a count disagreeing with it (map 17 stored 1 against an engine count of
    4, losing two placements behind a sibling object), and 76 maps with engine slots
    were absent from it entirely, defaulting to count zero (map 138: 21 engine
    slots, 0 modelled). Deriving the bound recovers 117 genuine placement records
    that the frozen table could not express, so the contract is no longer consulted
    for traversal at all. The declared run is still accepted, and is now checked
    against the derived truth rather than trusted over it.
    """
    pointer = record.scripts_pointer_raw
    if not pointer:
        return ()
    try:
        array_offset = GbaRomAddress(pointer).to_file_offset(len(image))
    except BinaryAddressError:
        return ()

    if declared_run is not None and pointer != declared_run[0]:
        raise MapError('placement run pointer differs from trusted provenance')
    slots = _resolve_object_slots(record, image)
    placement_slots = tuple((slot.index, slot.target_offset)
                            for slot in slots if slot.is_placement)
    offsets = tuple(offset for _, offset in placement_slots)
    if not offsets:
        return ()

    table_start, table_end = table_range
    #: The array spans every ENGINE slot, not only the placement-family ones, so the
    #: table-overlap refusal is measured against the real extent (`count * 4`).
    array_end = array_offset + 4 * len(slots)
    if array_offset < table_end and table_start < array_end:
        return ()

    accepted: list[tuple[int, int]] = []
    for slot_index, offset in placement_slots:
        if offset < table_end and table_start < offset + mp.read_placement_record(image, offset).consumed_length:
            raise MapError("placement overlaps map table")
        owner = claimed.get(offset)
        if owner is not None:
            raise MapError(
                f"placement record at 0x{offset:06X} is reached by both "
                f"map:{owner:04d} and map:{entry_index:04d}; exclusive ownership "
                "is a measured property of the verified image and this one "
                "breaks it"
            )
        claimed[offset] = entry_index
        accepted.append((slot_index, offset))
    return tuple(accepted)


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
        placements: tuple[PlacementEntry, ...],
        base_bytes: bytes,
    ) -> None:
        self.identification = identification
        self.profile = profile
        self._entries = {entry.identity: entry for entry in entries}
        self._order = tuple(entry.identity for entry in entries)
        self._arrays = {item.identity: item for item in arrays}
        self._array_order = tuple(item.identity for item in arrays)
        self._placements = {item.identity: item for item in placements}
        self._placement_order = tuple(item.identity for item in placements)
        self._edits: dict[MapIdentity, dict[str, int]] = {}
        self._placement_edits: dict[PlacementIdentity, mp.PlacementRecord] = {}
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

    def placements(self) -> Iterator[PlacementEntry]:
        """Every reachable placement record, in (map, index) order.

        Reflects pending edits, so a caller reading back after `set_placement_
        position` sees what a build would write rather than the original bytes.
        """
        for identity in self._placement_order:
            yield self._placement_entry(identity)

    def legacy_view(self):
        """Explicit TOOLKIT-008 project compatibility; no new production ceiling."""
        placements = self.legacy_placements()
        extents = tuple((p.file_offset, len(p.original_bytes)) for p in placements)
        start = min(e.file_offset for e in self.entries())
        end = max(e.file_offset + len(e.original_bytes) for e in self.entries())
        arrays = []
        for e in self.entries():
            extent = _resolve_slot_extent(e.record, len(self.base_bytes), (start, end), extents)
            if extent is not None:
                offset, size = extent
                arrays.append(SlotArrayEntry(e.identity, ms.decode_slot_array(
                    self.base_bytes[offset:offset + size], entry_index=e.identity.index,
                    file_offset=offset, image_size=len(self.base_bytes))))
        return Maps(identification=self.identification, profile=self.profile,
                    entries=tuple(self.entries()), arrays=tuple(arrays),
                    placements=placements, base_bytes=self.base_bytes)

    def legacy_placements(self) -> tuple[PlacementEntry, ...]:
        """Exact TOOLKIT-008 prefixes, not every full-census record with old shape."""
        result = []
        for entry in self.entries():
            for p in self.map_placements(entry.identity):
                if not mp.is_legacy_placement_record(p.original_bytes, 0):
                    break
                result.append(p)
        return tuple(result)

    def map_placements(self, identity: MapIdentity) -> tuple[PlacementEntry, ...]:
        """Every placement this map owns, in array order. Possibly empty.

        Ownership is exclusive by measurement: walking all 452 maps reaches
        1,559 records with none claimed twice, so a placement belongs to exactly
        one map and this never needs to report a shared record.
        """
        return tuple(
            self._placement_entry(key)
            for key in self._placement_order
            if key.map_index == identity.index
        )

    def placement(self, identity: PlacementIdentity) -> PlacementEntry:
        if identity not in self._placements:
            raise UnknownMapError(f"no placement record with identity {identity}")
        return self._placement_entry(identity)

    def _placement_entry(self, identity: PlacementIdentity) -> PlacementEntry:
        entry = self._placements[identity]
        pending = self._placement_edits.get(identity)
        if pending is None:
            return entry
        return PlacementEntry(
            identity=entry.identity,
            record=pending,
            file_offset=entry.file_offset,
            original_bytes=entry.original_bytes,
            slot_index=entry.slot_index,
        )

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

    def set_placement_position(
        self,
        identity: PlacementIdentity,
        *,
        low: int,
        high: int,
    ) -> None:
        """Stage an edit to one placement's `position_raw`, by halfword.

        The parameters are named by POSITION IN THE WORD rather than by axis,
        and are keyword-only so a caller cannot pass them in the wrong order by
        accident. This module does not claim which halfword is X: the packing
        matches the single CONFIRMED bounds structure in this project, and that
        correspondence is not established for this record family.

        Only `position_raw` is editable here. Descriptor and child relations are
        read-only; their counts and pointers cannot grow or be reassigned.
        Flags and IDs retain UNKNOWN semantics. Type reassignment is unsupported.
        """
        entry = self.placement(identity)
        self._placement_edits[identity] = entry.record.with_position(low, high)

    # --- planning ------------------------------------------------------

    def changes(self, *, authored_maps: frozenset[MapIdentity] = frozenset()) -> tuple[ByteChange, ...]:
        """Encode every record and every slot extent into attributed changes.

        Everything is encoded, not just what was edited, because that is what
        proves the round trip: an untouched record must re-encode to exactly its
        original bytes and `plan_changes` then drops it as a no-op. Returned as
        changes rather than a plan so a caller can merge subsystems into one
        plan, which is what makes cross-subsystem overlap a hard error.

        TOOLKIT-028: `authored_maps` names the maps an authored expansion has taken
        ownership of, and this yields BOTH their MapEntry record and their object
        array to it. Two structures of such a map are no longer describable here:
        its `MapEntry+0x04` count and `MapEntry+0x14` owner pointer are both derived
        by the expansion, and its object array has MOVED, so re-encoding the record
        at its canonical value or the array at its canonical home would contradict
        the expansion byte-for-byte. Yielding is what keeps that a single-owner
        write; the round-trip property is unaffected because the expansion emits the
        same bytes for everything it did not deliberately change, and any map NOT in
        this set is still encoded in full exactly as before.
        """
        changes: list[ByteChange] = []

        for item in self.entries():
            if item.identity in authored_maps:
                continue
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
            if array_entry.identity in authored_maps:
                continue
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

        for placement in self.placements():
            edited = placement.identity in self._placement_edits
            changes.append(
                ByteChange(
                    offset=placement.file_offset,
                    old=placement.original_bytes,
                    new=placement.record.to_bytes(),
                    owner=str(placement.identity),
                    reason=(
                        "placement edit: position"
                        if edited
                        else "placement unchanged"
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
    placements: list[PlacementEntry] = []
    #: Guards the exclusivity the full corpus measurement showed: 1,559 reachable
    #: records, none claimed by two maps. A second claim raises rather than
    #: being dropped, because giving one record two owners would make
    #: `plan_changes` emit overlapping writes for the same bytes.
    claimed_placements: dict[int, int] = {}
    from .data.placement_contracts import CONTRACTS
    contract = CONTRACTS.get(profile.id)
    if contract is not None and contract['sha256'] != identification.hashes.sha256:
        raise MapError('placement contract provenance mismatch')

    #: Placements are resolved for EVERY map before any slot extent, because a
    #: slot extent is only accepted once it is known to cover no record, and a
    #: record owned by a later map can fall inside an earlier map's declared
    #: extent - MapEntry 58's extent covers a record reached from MapEntry 59.
    #: Resolving in one interleaved pass would accept that extent and only
    #: discover the conflict at plan time, as an overlap error rather than as
    #: the evidence finding it is.
    for index in range(table_profile.count):
        offset = table_offset + index * MAP_ENTRY_SIZE
        record = MapEntry.from_bytes(image[offset : offset + MAP_ENTRY_SIZE])
        for placement_index, (slot_index, record_offset) in enumerate(
            _resolve_placements(record, image, table_range, claimed_placements, index,
                                None if contract is None else
                                _declared_run(contract, index, record))
        ):
            placements.append(
                PlacementEntry(
                    identity=PlacementIdentity(index, placement_index),
                    record=mp.read_placement_record(image, record_offset),
                    file_offset=record_offset,
                    original_bytes=image[
                        record_offset : record_offset + mp.read_placement_record(image, record_offset).consumed_length
                    ],
                    slot_index=slot_index,
                )
            )
    placement_offsets = tuple((item.file_offset, len(item.original_bytes)) for item in placements)
    bodies = sorted((offset, offset + size) for offset, size in placement_offsets)
    if any(a[1] > b[0] for a, b in zip(bodies, bodies[1:])):
        raise MapError('overlapping placement record bodies across maps')
    #: TOOLKIT-025: these extents are the ENGINE-counted arrays, derived per map from
    #: `+0x04` and `+0x14`, not the frozen contract runs. The contract expressed only
    #: 240 of the 316 arrays the engine actually traverses, so checking its runs left
    #: 76 arrays unchecked for overlap and let their records go unmodelled entirely.
    #: Each array owns exactly `count * 4` bytes - TOOLKIT-024 proved the loop reads
    #: no sentinel and no suffix - so the extent is exact, not a bound.
    object_arrays = []
    for index in range(table_profile.count):
        offset = table_offset + index * MAP_ENTRY_SIZE
        record = MapEntry.from_bytes(image[offset : offset + MAP_ENTRY_SIZE])
        if _resolve_object_slots(record, image):
            object_arrays.append(
                (GbaRomAddress(record.scripts_pointer_raw).to_file_offset(len(image)),
                 record.trigger_count_raw * 4))
    object_arrays.sort()
    if any(a + n > b for (a, n), (b, _) in zip(object_arrays, object_arrays[1:])):
        raise MapError('overlapping placement pointer runs')
    if any(a < end and start < a + n for a, n in object_arrays for start, end in bodies):
        raise MapError('placement run overlaps a record body')

    protected_extents = placement_offsets
    if contract is not None:
        protected_extents += tuple((GbaRomAddress(ptr).to_file_offset(len(image)), 8)
                                   for ptr in contract['descriptors'])
        protected_extents += tuple((GbaRomAddress(ptr).to_file_offset(len(image)), size)
                                   for ptr, size in contract['roots'])

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

        extent = _resolve_slot_extent(
            record, len(image), table_range, protected_extents
        )
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

    result = Maps(
        identification=identification,
        profile=profile,
        entries=tuple(entries),
        arrays=tuple(arrays),
        placements=tuple(placements),
        base_bytes=image,
    )

    if contract is not None:
        from .placement_events import PlacementEvents
        PlacementEvents(result)  # Validate descriptor/child provenance on normal map reads.
    return result
