"""Semantic access to a profile's map transitions. MAP-WARP-FORMAT-001.

This is the layer callers use::

    transitions = load_map_transitions(rom_path, catalog)
    identity = TransitionIdentity(MapIdentity(39), 1)
    transitions.destination(identity)            # -> MapIdentity(40)
    transitions.set_destination(identity, MapIdentity(38))
    plan = transitions.plan()

A caller names a transition by its **source map and its index within that map's
own array**, and never computes a file offset, never dereferences a pointer and
never sees a ROM address, matching `webfoot.maps`, `webfoot.stats` and
`webfoot.text`.

**The supported family.** One structure, and only one: the 24-byte record a
map's *selector-1 root* reaches through the root's `+0x40` count / `+0x44` array
pair. Both fields and the record layout are established in
`docs/research/LOGX_CONNECTOR_PROVENANCE.md` from cited engine instructions, not
from this module: the pair is loaded by one `ldm` at `0x08009676`, handed to the
registry walk `0x08012664` that iterates exactly `+0x40` elements of 4 bytes
each, and each record's `+0x00` word is called as a constructor. Every record in
the canonical corpus is a 24-byte block at a 4-byte-aligned in-ROM address, and
none is reached twice.

The *selector-1 root* is the accepted LOGX-MAP-RENDER-001 route -
`MapEntry[+0x2C]` leads to a run of aligned in-ROM words, whose first word is the
root - read here through `formats.map_graphics`, which owns that route, rather
than re-derived.

**What is supported and what is refused.** A record is refused, before any plan
exists, when its class word is outside the two values the canonical corpus
measured, when its region is not two ordered non-degenerate intervals, when its
destination key resolves to no map, when its address is unaligned or outside the
image, when two maps reach one record, or when two records' 24-byte extents
overlap. Each refusal names the form this project has *not* measured. Nothing
here claims universal warp support: a transition form reached by another route,
or tagged by another class word, is not addressable through this authority at
all.

**Editing is fixed-width and semantic.** Two fields are editable, because both
are self-contained fixed-width values whose meaning the engine's own reads
establish: the destination `MapEntry` key, and the record's two ordered interval
pairs. Everything else is preserved byte-for-byte and is deliberately not
editable - `+0x00` and `+0x04` are code-address-shaped words whose class
semantics is UNRESOLVED, and `+0x10`, `+0x13`, `+0x14`, `+0x16` and `+0x17` are
engine-read fields whose semantics are UNRESOLVED. A pointer or count is refused
for the reason `webfoot.maps` refuses them: editing one moves a structure this
toolkit does not own.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import os
from pathlib import Path
from typing import Iterator

from . import capability
from .binary import BinaryAddressError, GBA_ROM_BASE, GbaRomAddress
from .formats import map_graphics as mg
from .formats import map_entry as me
from .formats.map_entry import MAP_ENTRY_SIZE, MapEntry
from .formats.map_transitions import (
    SUPPORTED_CLASS_RAW,
    TRANSITION_LAYOUT,
    TRANSITION_SIZE,
    MapTransitionError,
    MapTransitionFamilyError,
    MapTransitionLengthError,
    MapTransitionRegionError,
    MapTransitionValueError,
    TransitionRecord,
    TransitionRegion,
)
from .hashing import hash_stream
from .profile import RomProfileCatalog
from .rom import RomChangedError, identify_rom
from .write import ByteChange, WritePlan, plan_changes
from .maps import MapIdentity

#: `root + 0x40`, the count the engine reads with `+0x44` in one `ldm`.
ROOT_COUNT_OFFSET = mg.ROOT_CONNECTION_COUNT_OFFSET

#: `root + 0x44`, the pointer to the array of 4-byte record pointers.
ROOT_ARRAY_OFFSET = mg.ROOT_CONNECTION_ARRAY_OFFSET

#: The array element width, taken from the engine's own `lsls r0, r4, #2`.
ARRAY_ELEMENT_WIDTH = 4

#: `MapEntry + 0x2C`, the indexed-word source the selector-1 route starts from.
MAP_ENTRY_SOURCE_OFFSET = mg.MAP_ENTRY_SOURCE_OFFSET

#: The two `MapEntry` bytes the engine's own lookup compares, in order.
#:
#: `0x08008A0E`/`0x08008A14` compare `entry[+0]` and `entry[+1]` separately
#: against the record's `+0x11` and `+0x12`. The names `map_entry` gives those
#: two fields are upstream labels this module does not rely on; the guard below
#: is what keeps this module from silently disagreeing with that layout.
MAP_ENTRY_KEY_OFFSETS = (0x00, 0x01)

_KEY_FIELD_NAMES = tuple(
    field.name for field in me.MAP_ENTRY_LAYOUT if field.offset in MAP_ENTRY_KEY_OFFSETS
)
if _KEY_FIELD_NAMES != ("output_raw", "zone_raw"):
    raise AssertionError(
        "map_entry's layout no longer places the two-byte lookup key at "
        f"+0x00/+0x01: {_KEY_FIELD_NAMES!r}"
    )

#: Every transition record is 4-byte aligned in the canonical corpus.
RECORD_ALIGNMENT = 4


class MapTransitionsError(ValueError):
    """Base error for semantic transition access."""


class UnknownTransitionError(MapTransitionsError):
    """Raised when an identity names no transition in this corpus."""


class TransitionFieldError(MapTransitionsError):
    """Raised when a field is not editable, or its value is out of range."""


class TransitionProfileError(MapTransitionsError, capability.CapabilityError):
    """Raised when a ROM/profile is not authorized for this format."""


@dataclass(frozen=True, slots=True, order=True)
class TransitionIdentity:
    """A transition's durable identity: source map + index in that map's array.

    Deliberately excludes the record's ROM address and every runtime address. An
    address names where a record sits in one image; the source map plus the
    index the engine's own walk assigns names *which transition it is*, and
    survives any rebuild that keeps the array in order. It is the same choice
    `PlacementIdentity` makes, for the same reason.

    The index is the element index in the map's `root + 0x44` array. The engine
    walks that array descending; the index is the array position, and the
    engine's consumption order is an observation about the walk rather than part
    of the identity.
    """

    source: MapIdentity
    index: int

    def __post_init__(self) -> None:
        if not isinstance(self.source, MapIdentity):
            raise MapTransitionsError(
                f"transition source must be a MapIdentity, got {self.source!r}"
            )
        if type(self.index) is not int or self.index < 0:
            raise MapTransitionsError("transition index must be a non-negative integer")

    @property
    def key(self) -> str:
        return f"{self.source.key}/transition:{self.index:04d}"

    def __str__(self) -> str:
        return self.key


@dataclass(frozen=True, slots=True)
class TransitionEntry:
    """One transition record plus the provenance needed to rebuild it."""

    identity: TransitionIdentity
    record: TransitionRecord
    #: GBA address of the record itself. Provenance only; never an identity.
    record_address: int
    #: GBA address of the array element that holds this record's pointer.
    element_address: int
    file_offset: int
    original_bytes: bytes


def _in_rom(value: int, image_size: int) -> bool:
    """Whether ``value`` is a 4-byte-aligned address inside this image."""
    if value < GBA_ROM_BASE or value % RECORD_ALIGNMENT:
        return False
    try:
        GbaRomAddress(value).to_file_offset(image_size)
    except BinaryAddressError:
        return False
    return True


def _u32(image: bytes, address: int) -> int:
    offset = GbaRomAddress(address).to_file_offset(len(image))
    return int.from_bytes(image[offset : offset + 4], "little")


def _map_entry_key(entry: MapEntry) -> bytes:
    """A map's own two-byte lookup key, in the engine's comparison order."""
    return bytes((entry.output_raw, entry.zone_raw))


def _resolve_root(image: bytes, entry: MapEntry, index: int) -> int:
    """The selector-1 root address for one map, or raise.

    The accepted route is `MapEntry[+0x2C]` -> the leading run of aligned in-ROM
    words at that source -> its first word. Both hops are checked: a source that
    is not an aligned in-ROM address, or a first word that is not one, is a route
    this project has not measured and is refused rather than treated as an empty
    transition list.
    """
    source_address = entry.variation_array_pointer_raw
    if source_address == 0:
        raise MapTransitionsError(
            f"map:{index:04d} declares no selector-1 source at MapEntry+0x2C"
        )
    if not _in_rom(source_address, len(image)):
        raise MapTransitionsError(
            f"map:{index:04d} selector-1 source 0x{source_address:08X} is not an "
            "aligned address inside the image"
        )
    root = _u32(image, source_address)
    if root == 0:
        raise MapTransitionsError(
            f"map:{index:04d} has an empty selector-1 word run at "
            f"0x{source_address:08X}, so it names no root"
        )
    if not _in_rom(root, len(image)):
        raise MapTransitionsError(
            f"map:{index:04d} selector-1 root 0x{root:08X} is not an aligned "
            "address inside the image"
        )
    return root


def _resolve_pair(image: bytes, root: int, index: int) -> tuple[int, int]:
    """`(count, array_address)` from a root's `+0x40`/`+0x44`, or raise."""
    count = _u32(image, root + ROOT_COUNT_OFFSET)
    array = _u32(image, root + ROOT_ARRAY_OFFSET)
    if (count == 0) != (array == 0):
        raise MapTransitionsError(
            f"map:{index:04d} root 0x{root:08X} declares count {count} with array "
            f"0x{array:08X}; the two are null together on 452 of 452 canonical roots"
        )
    if count and not _in_rom(array, len(image)):
        raise MapTransitionsError(
            f"map:{index:04d} root 0x{root:08X} array 0x{array:08X} is not an "
            "aligned address inside the image"
        )
    return count, array


def _read_corpus(
    image: bytes,
    *,
    table_offset: int,
    table_count: int,
    profile_id: str,
    base_sha256: str,
) -> "MapTransitions":
    """Resolve every transition in ``image``, failing closed on an unknown form.

    Private by design: it takes the map table's physical location, which is the
    profile's business and not a caller's. `load_map_transitions` is the public
    way in; this is the seam a synthetic image is tested through.
    """
    entries_by_map: list[MapEntry] = []
    keys: list[bytes] = []
    key_owner: dict[bytes, int] = {}
    for index in range(table_count):
        offset = table_offset + index * MAP_ENTRY_SIZE
        entry = MapEntry.from_bytes(image[offset : offset + MAP_ENTRY_SIZE])
        key = _map_entry_key(entry)
        if key in key_owner:
            raise MapTransitionsError(
                f"map:{index:04d} and map:{key_owner[key]:04d} share the two-byte "
                f"lookup key {key.hex()}; the engine's lookup returns the first "
                "match, so a destination written as that key is ambiguous"
            )
        key_owner[key] = index
        keys.append(key)
        entries_by_map.append(entry)

    # Pass 1 - the pointer structure. Every address the format defines is
    # resolved and checked *before* any record is decoded, so a shared or
    # overlapping record is reported as that, rather than as a class-word error
    # raised from an address that was never a record boundary.
    located: list[tuple[TransitionIdentity, int, int]] = []
    claimed: dict[int, TransitionIdentity] = {}
    for index, entry in enumerate(entries_by_map):
        source = MapIdentity(index)
        root = _resolve_root(image, entry, index)
        count, array = _resolve_pair(image, root, index)
        for element in range(count):
            element_address = array + element * ARRAY_ELEMENT_WIDTH
            if not _in_rom(element_address, len(image)):
                raise MapTransitionsError(
                    f"map:{index:04d} array element {element} at "
                    f"0x{element_address:08X} is not inside the image"
                )
            record_address = _u32(image, element_address)
            if not _in_rom(record_address, len(image)):
                raise MapTransitionsError(
                    f"map:{index:04d} element {element} points at "
                    f"0x{record_address:08X}, which is not an aligned transition "
                    "record address inside the image"
                )
            if GbaRomAddress(record_address).to_file_offset(len(image)) + TRANSITION_SIZE > len(image):
                raise MapTransitionsError(
                    f"map:{index:04d} element {element} record at "
                    f"0x{record_address:08X} extends past the image"
                )
            identity = TransitionIdentity(source, element)
            owner = claimed.get(record_address)
            if owner is not None:
                raise MapTransitionsError(
                    f"the record at 0x{record_address:08X} is reached by both "
                    f"{owner} and {identity}; exclusive ownership is a measured "
                    "property of the canonical image and this one breaks it"
                )
            claimed[record_address] = identity
            located.append((identity, record_address, element_address))

    ordered = sorted(located, key=lambda item: item[1])
    for previous, current in zip(ordered, ordered[1:]):
        if current[1] < previous[1] + TRANSITION_SIZE:
            raise MapTransitionsError(
                f"{previous[0]} at 0x{previous[1]:08X} and {current[0]} at "
                f"0x{current[1]:08X} overlap; a record's engine-accessed extent "
                f"is {TRANSITION_SIZE} bytes and two records cannot share a byte"
            )

    # Pass 2 - the records themselves, in (source map, array index) order.
    entries: list[TransitionEntry] = []
    for identity, record_address, element_address in located:
        record_offset = GbaRomAddress(record_address).to_file_offset(len(image))
        original = image[record_offset : record_offset + TRANSITION_SIZE]
        try:
            record = TransitionRecord.from_bytes(original).validate()
        except (MapTransitionLengthError, MapTransitionFamilyError,
                MapTransitionRegionError, MapTransitionValueError) as exc:
            raise type(exc)(f"{identity}: {exc}") from exc
        entries.append(
            TransitionEntry(
                identity=identity,
                record=record,
                record_address=record_address,
                element_address=element_address,
                file_offset=record_offset,
                original_bytes=original,
            )
        )

    return MapTransitions(
        profile_id=profile_id,
        base_sha256=base_sha256,
        base_bytes=image,
        keys=tuple(keys),
        key_owner=key_owner,
        entries=tuple(entries),
    )


class MapTransitions:
    """Loaded transition records, plus any pending semantic edits.

    Edits accumulate in memory and become a `WritePlan` only when `plan()` is
    called, matching `Maps` and `StatTables`. Nothing here writes or knows a
    destination file.
    """

    def __init__(
        self,
        *,
        profile_id: str,
        base_sha256: str,
        base_bytes: bytes,
        keys: tuple[bytes, ...],
        key_owner: dict[bytes, int],
        entries: tuple[TransitionEntry, ...],
    ) -> None:
        self.profile_id = profile_id
        self.base_sha256 = base_sha256
        self._base_bytes = base_bytes
        self._keys = keys
        self._key_owner = dict(key_owner)
        self._entries = {entry.identity: entry for entry in entries}
        self._order = tuple(entry.identity for entry in entries)
        self._edits: dict[TransitionIdentity, TransitionRecord] = {}

    # --- reading -------------------------------------------------------

    @property
    def base_bytes(self) -> bytes:
        """The exact image these records were decoded from."""
        return self._base_bytes

    @property
    def map_count(self) -> int:
        """How many map identities this profile's table declares."""
        return len(self._keys)

    @property
    def record_count(self) -> int:
        return len(self._order)

    def entries(self) -> Iterator[TransitionEntry]:
        """Every transition, in (source map, array index) order.

        Order is presentation, not identity: `TransitionIdentity` alone names a
        transition, and this iteration is deterministic for a given image.
        """
        for identity in self._order:
            yield self._entry(identity)

    def entry(self, identity: TransitionIdentity) -> TransitionEntry:
        """One transition, reflecting pending edits."""
        if identity not in self._entries:
            raise UnknownTransitionError(
                f"no transition with identity {identity}"
            )
        return self._entry(identity)

    def _entry(self, identity: TransitionIdentity) -> TransitionEntry:
        loaded = self._entries[identity]
        pending = self._edits.get(identity)
        if pending is None:
            return loaded
        return replace(loaded, record=pending)

    def for_map(self, source: MapIdentity) -> tuple[TransitionEntry, ...]:
        """This map's transitions, in array index order. Possibly empty."""
        return tuple(
            self._entry(identity)
            for identity in self._order
            if identity.source == source
        )

    def key_for(self, identity: MapIdentity) -> bytes:
        """The two-byte `MapEntry` lookup key that names ``identity``."""
        index = self._require_map(identity)
        return self._keys[index]

    def map_for_key(self, key: bytes) -> MapIdentity:
        """The map a two-byte lookup key names, or raise."""
        raw = bytes(key)
        try:
            index = self._key_owner[raw]
        except KeyError:
            raise MapTransitionsError(
                f"no map in this profile's table carries the lookup key {raw.hex()}"
            ) from None
        return MapIdentity(index)

    def destination(self, identity: TransitionIdentity) -> MapIdentity:
        """The map this transition leads to.

        The destination is the record's two bytes at `+0x11`/`+0x12`, resolved
        through the same two-byte key scan the engine uses at `0x080089FC`.
        """
        record = self.entry(identity).record
        try:
            index = self._key_owner[record.destination_key]
        except KeyError:
            raise MapTransitionsError(
                f"{identity} declares destination key {record.destination_key.hex()}, "
                "which resolves to no map in this profile's table"
            ) from None
        return MapIdentity(index)

    def validate(self) -> tuple[TransitionEntry, ...]:
        """Re-validate every record, pending edits included. Returns them.

        Raises the same refusals the load path raises, so a caller can check a
        corpus after staging edits without building an image.
        """
        checked = tuple(self.entries())
        for entry in checked:
            entry.record.validate()
        return checked

    # --- editing -------------------------------------------------------

    def set_destination(
        self, identity: TransitionIdentity, destination: MapIdentity
    ) -> None:
        """Stage a retarget of one transition. Validates before recording it."""
        self.entry(identity)
        key = self.key_for(destination)
        record = self.entry(identity).record.with_destination_key(key)
        record.validate()
        self._edits[identity] = record

    def set_region(
        self, identity: TransitionIdentity, region: TransitionRegion
    ) -> None:
        """Stage an edit to one transition's two ordered interval pairs.

        The intervals are positional; see `formats.map_transitions`. Which one is
        horizontal, and what the endpoints' unit is, are UNRESOLVED, so this
        authority edits the confirmed physical shape without naming an axis.
        """
        self.entry(identity)
        if not isinstance(region, TransitionRegion):
            raise TransitionFieldError(
                f"{identity}.region must be a TransitionRegion, got {region!r}"
            )
        record = self.entry(identity).record.with_region(region)
        record.validate()
        self._edits[identity] = record

    def _require_map(self, identity: MapIdentity) -> int:
        if not isinstance(identity, MapIdentity):
            raise TransitionFieldError(
                f"a map identity must be a MapIdentity, got {identity!r}"
            )
        if not 0 <= identity.index < len(self._keys):
            raise TransitionFieldError(
                f"{identity} is outside this profile's 0..{len(self._keys) - 1} "
                "declared map-entry range"
            )
        return identity.index

    # --- planning ------------------------------------------------------

    def changes(self) -> tuple[ByteChange, ...]:
        """Encode every record into attributed, non-overlapping changes.

        Everything is encoded, not just what was edited, because that is what
        proves the round trip: an untouched record must re-encode to exactly its
        original bytes, and `plan_changes` then drops it as a no-op.

        Only the records are yielded. The root's count, the pointer array and its
        elements are not this module's to write - a count or pointer edit is
        relocation, which no verified profile authorizes - so they are preserved
        by never being touched, and a caller that needs them in a manifest takes
        them from a subsystem that owns them.
        """
        changes: list[ByteChange] = []
        for identity in self._order:
            loaded = self._entries[identity]
            entry = self._entry(identity)
            changes.append(
                ByteChange(
                    offset=entry.file_offset,
                    old=entry.original_bytes,
                    new=entry.record.to_bytes(),
                    owner=str(identity),
                    reason=_reason(loaded.record, entry.record),
                )
            )
        return tuple(changes)

    def plan(self) -> WritePlan:
        """Validate this subsystem's changes alone and return an applicable plan."""
        return plan_changes(
            self._base_bytes,
            self.changes(),
            profile_id=self.profile_id,
            base_sha256=self.base_sha256,
        )


def _reason(loaded: TransitionRecord, current: TransitionRecord) -> str:
    """What a manifest should say about one record's edit."""
    if current == loaded:
        return "transition unchanged"
    changed = [
        item.name
        for item in TRANSITION_LAYOUT
        if getattr(current, item.name) != getattr(loaded, item.name)
    ]
    return f"transition edit: {', '.join(changed)}"


def load_map_transitions(
    path: str | Path, catalog: RomProfileCatalog
) -> MapTransitions:
    """Identify ``path``, then resolve its complete transition corpus.

    The ROM's identity is re-checked after the read, mirroring `load_maps`, so an
    image that changes underneath is an error rather than a silent mis-decode.
    """
    source = Path(path)
    identification = identify_rom(source, catalog)
    profile = capability.require(
        identification,
        capability.Capability.MAP_ENTRIES,
        subsystem="map transition access",
        error_type=TransitionProfileError,
        check_header=True,
    )
    table_profile = profile.map_entries
    assert table_profile is not None

    with source.open("rb") as stream:
        before = os.fstat(stream.fileno())
        hashes, _ = hash_stream(stream)
        if hashes != identification.hashes:
            raise RomChangedError(f"ROM identity changed before transition read: {source}")
        stream.seek(0)
        image = stream.read()
        after = os.fstat(stream.fileno())

    def identity_of(stat: os.stat_result) -> tuple[int, int, int, int]:
        return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)

    if identity_of(before) != identity_of(after) or identity_of(before) != identity_of(
        source.stat()
    ):
        raise RomChangedError(f"ROM changed while transitions were read: {source}")

    table_offset, _ = me.resolve_map_entry_table_range(table_profile, len(image))
    return _read_corpus(
        image,
        table_offset=table_offset,
        table_count=table_profile.count,
        profile_id=profile.id,
        base_sha256=identification.hashes.sha256,
    )


__all__ = [
    "ARRAY_ELEMENT_WIDTH",
    "MAP_ENTRY_SOURCE_OFFSET",
    "ROOT_ARRAY_OFFSET",
    "ROOT_COUNT_OFFSET",
    "SUPPORTED_CLASS_RAW",
    "TRANSITION_SIZE",
    "MapTransitionError",
    "MapTransitions",
    "MapTransitionsError",
    "TransitionEntry",
    "TransitionFieldError",
    "TransitionIdentity",
    "TransitionProfileError",
    "TransitionRegion",
    "UnknownTransitionError",
    "load_map_transitions",
]
