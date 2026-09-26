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

**MAP-WARP-PROJECT-AUTHORING-001 stores that edit in a project and builds it.**
A project names a transition by `TransitionIdentity` and stores the fields it
sets, each beside the value the canonical record held - so the authored file
proves what it was authored against. :func:`plan_transition_edits` is the build's
one entry point: it loads the canonical corpus from the image, checks every stored
prior against the record the image actually holds, stages the authored fields
through the same `set_destination`/`set_region` this module always used, and
returns this authority's own byte plan. Nothing outside this module serializes a
transition: the only encoder is `TransitionRecord.to_bytes`, reached through
:meth:`MapTransitions.changes`. The edit is fixed-width, so it allocates nothing,
relocates nothing and rewrites exactly one 24-byte record.

**MAP-WARP-CREATE-PROJECT-001 creates a transition that does not exist.**
:func:`materialize_transition_creations` is the build's one entry point for that,
and it is the first domain in this module that allocates. A created transition has
no canonical bytes to edit, so:

* it is named ``map:NNNN/transition:<name>`` - a durable authored identity with no
  address and no array index in it, because the index it will occupy does not exist
  until a build appends it;
* it is composed over a **template**: an existing 566-class record of the *same*
  source map, whose UNRESOLVED bytes (``+0x00``, ``+0x04``, ``+0x13`` and
  ``+0x10``'s low nibble) the created record carries rather than invents;
* its region, destination key, arrival pair and arrival-facing override are
  authored, and a creation that would come out byte-identical to its template is
  refused - the capability is creation, not aliasing;
* the storage it needs - a 24-byte record and the expanded ``root + 0x44`` array
  that reaches it - is placed by the production allocator above canonical EOF, and
  the root's count and array pointer are rewritten in place.

The two fields it rewrites are exactly the two the edit path is forbidden to
touch, so the two capabilities meet only in this module and only here.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import os
from pathlib import Path
import re
from typing import Iterable, Iterator, Mapping

from . import capability
from .allocation import (
    Addressability,
    Allocation,
    AllocationKind,
    AllocationRequest,
    allocate,
)
from .binary import BinaryAddressError, FileOffset, GBA_ROM_BASE, GbaRomAddress
from .formats import map_graphics as mg
from .formats import map_entry as me
from .formats.map_entry import MAP_ENTRY_SIZE, MapEntry
from .formats.map_transitions import (
    ARRIVAL_UNSET_MINIMUM,
    CREATED_CLASS_RAW,
    CREATED_FIELD_AUTHORED_MASKS,
    FACING_EAST,
    FACING_MASK,
    FACING_NAMES,
    FACING_NORTH,
    FACING_PRESERVED_MASK,
    FACING_SOUTH,
    FACING_WEST,
    SUPPORTED_CLASS_RAW,
    TRANSITION_LAYOUT,
    TRANSITION_SIZE,
    MapTransitionError,
    MapTransitionFamilyError,
    MapTransitionLengthError,
    MapTransitionRegionError,
    MapTransitionValueError,
    TransitionArrival,
    TransitionRecord,
    TransitionRegion,
    compose_created_record,
)
from .hashing import hash_stream
from .layout import AnchorId, OwnedRegion, RomRange
from .packaged import packaged_profile
from .profile import RomProfile, RomProfileCatalog
from .rom import RomChangedError, identify_rom
from .write import (
    ByteChange,
    GeneratedAllocationProvenance,
    GeneratedImage,
    TransitionCreationProvenance,
    TransitionEditProvenance,
    TransitionRecordFieldProvenance,
    WritePlan,
    plan_changes,
)
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

#: The GBA's visible viewport. The engine stores a map's camera clamp as
#: ``world - screen``, so the walkable extent is the clamp word plus these.
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 160

#: How near an arrival may be to the destination's door and still count as "at"
#: it. The measured corpus puts 670 of 735 inside the door rectangle or within a
#: few pixels outside it, with 16 px covering all but a handful of the rest.
ARRIVAL_DOOR_TOLERANCE = 16

#: The domain name a created transition's allocation provenance carries.
CREATION_DOMAIN = "map_transition_creation"

#: Allocation owner/anchor prefixes. One array per source map, one record per
#: created transition, so the two never collide and each generated write has an
#: owner that :meth:`GeneratedAllocationProvenance.owns` can match.
CREATION_ARRAY_PREFIX = "transition-array:"
CREATION_RECORD_PREFIX = "transition-record:"

#: An authored transition name. Mirrors the project document's own rule
#: (`project.model._TRANSITION_NAME`) so the authority refuses a name the file
#: format would refuse, rather than depending on the parser having done it.
_TRANSITION_NAME = re.compile(r"[a-z][a-z0-9_-]{0,63}$")

#: The largest value `root + 0x40` can hold. It is a 4-byte field, so a count that
#: would not fit is refused rather than truncated.
MAX_TRANSITION_COUNT = 0xFFFFFFFF


def _arrival_is_near(
    arrival: "TransitionArrival", region: "TransitionRegion"
) -> bool:
    """Whether an arrival point sits at a door, inside it or just outside it."""
    (low_x, high_x), (low_y, high_y) = region.first, region.second
    gap_x = 0 if low_x <= arrival.x <= high_x else min(
        abs(arrival.x - low_x), abs(arrival.x - high_x)
    )
    gap_y = 0 if low_y <= arrival.y <= high_y else min(
        abs(arrival.y - low_y), abs(arrival.y - high_y)
    )
    return max(gap_x, gap_y) <= ARRIVAL_DOOR_TOLERANCE


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
    profile: "RomProfile | None" = None,
) -> "MapTransitions":
    """Resolve every transition in ``image``, failing closed on an unknown form.

    Private by design: it takes the map table's physical location, which is the
    profile's business and not a caller's. `load_map_transitions` is the public
    way in; this is the seam a synthetic image is tested through.

    ``profile`` is carried on the corpus because two of its own answers - the
    destination's walkable extent and the arrival bounds check - read the *map
    table* again, and they must read the table of the profile this corpus was
    resolved for. Left out (a synthetic image read directly through this seam) the
    packaged profile is used, which is the canonical case.
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
    #: The `+0x40`/`+0x44` pair of every map that declares a selector-1 root, kept
    #: because creation has to name and rewrite those two fields. Taken from the same
    #: resolution the enumeration uses, so a creation can never disagree with the
    #: enumeration about where a map's array is.
    roots: dict[int, "TransitionRoot"] = {}
    for index, entry in enumerate(entries_by_map):
        source = MapIdentity(index)
        root = _resolve_root(image, entry, index)
        count, array = _resolve_pair(image, root, index)
        roots[index] = TransitionRoot(
            source=source, root_address=root, count=count, array_address=array
        )
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
        roots=roots,
        profile=profile,
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
        roots: "Mapping[int, TransitionRoot] | None" = None,
        profile: "RomProfile | None" = None,
    ) -> None:
        self.profile_id = profile_id
        self.base_sha256 = base_sha256
        self._base_bytes = base_bytes
        self._keys = keys
        self._key_owner = dict(key_owner)
        self._entries = {entry.identity: entry for entry in entries}
        self._order = tuple(entry.identity for entry in entries)
        #: map index -> the `+0x40`/`+0x44` pair, resolved once at load. Empty for a
        #: corpus constructed directly by a caller that does not need creation.
        self._roots: dict[int, TransitionRoot] = dict(roots or {})
        #: The profile whose map table this corpus was resolved against, so the
        #: answers that read that table again (`destination_bounds`) cannot fall
        #: back to a different one. None means the packaged canonical profile.
        self._profile = profile
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

    def check_edit(
        self, identity: TransitionIdentity, request: "TransitionEdit"
    ) -> None:
        """Validate one request against this corpus, recording nothing.

        MAP-WARP-WORKBENCH-001. A surface that lets a human stage an edit needs to
        answer "would the authority accept this?" *before* the edit is staged, and
        the answer has to come from the same code that would apply it - otherwise
        the GUI and the build can disagree about what is authorable. This stages the
        request through the ordinary :meth:`set_destination`, :meth:`set_arrival`
        and :meth:`set_facing` path, in the order the build uses (destination first,
        so the arrival's bounds answer for the map the player will actually arrive
        in), and then restores the pending set exactly as it was.

        Nothing is serialized here and no second rule is stated: every refusal is
        the one the corresponding `set_*` raises, with its own message.
        """
        if not isinstance(request, TransitionEdit):
            raise TransitionFieldError(
                f"a checked edit must be a TransitionEdit, got {request!r}"
            )
        self.entry(identity)
        recorded = dict(self._edits)
        try:
            if request.destination is not None:
                self.set_destination(identity, request.destination)
            if request.region is not None:
                self.set_region(identity, request.region)
            if request.arrival is not None:
                self.set_arrival(identity, request.arrival)
            if request.facing is not None:
                self.set_facing(identity, request.facing)
        finally:
            self._edits = recorded

    # --- the arrival point: safe exit, relative to the direction of travel ---
    #
    # MAP-WARP-RUNTIME-EDIT-001. A destination edit alone is not enough to move a
    # door somewhere else safely: the record also carries the point the player is
    # placed at in the destination, and that point belongs to the OLD destination's
    # geometry. Measured on the canonical image, retail already implements "exit
    # onto the map from the direction you left": of 735 records, 670 place the
    # player within 16 px of the destination's reciprocal door - the record in the
    # destination that leads back to the source - and 8 of the 12 that do not are
    # the 0xFFFx "no authored arrival" sentinel.
    #
    # So a retarget derives the arrival from the destination's own door back. Where
    # there is no such door (a one-way link, or an arbitrary destination), nothing
    # can be derived and the author must state a point, which is then checked
    # against the destination's own walkable extent.

    def reciprocal_doors(
        self, source: MapIdentity, destination: MapIdentity
    ) -> tuple[TransitionEntry, ...]:
        """The destination's own records that lead back to ``source``."""
        return tuple(
            entry
            for entry in self.for_map(destination)
            if self.destination(entry.identity) == source
        )

    def destination_bounds(self, destination: MapIdentity) -> tuple[int, int]:
        """The destination's walkable extent, in pixels, from the engine's own word.

        ``root + 0x08``/``+0x0A`` hold the camera's maximum scroll as ``extent - 1``
        (MAP-RESIZE-AND-LAYERS-001), and the GBA screen is 240x160, so the world is
        ``extent + screen``. This is the engine's statement of how big the map is,
        which is what an arrival has to fit inside; it is not a collision test, and
        a point inside this box can still be inside scenery.
        """
        index = self._require_map(destination)
        table = self._map_entries()
        root = table[index].root_address
        offset = GbaRomAddress(root + 0x08).to_file_offset(len(self._base_bytes))
        extent_x = int.from_bytes(self._base_bytes[offset : offset + 2], "little") + 1
        extent_y = int.from_bytes(self._base_bytes[offset + 2 : offset + 4], "little") + 1
        return extent_x + SCREEN_WIDTH, extent_y + SCREEN_HEIGHT

    def arrival(self, identity: TransitionIdentity) -> "TransitionArrival | None":
        """Where this transition places the player, or None when unset."""
        return self.entry(identity).record.arrival

    def set_arrival(
        self, identity: TransitionIdentity, arrival: "TransitionArrival | None"
    ) -> None:
        """Stage the point this transition places the player at.

        The point is checked against the destination's walkable extent before it is
        recorded, so an arrival that would drop the player off the map is refused
        here rather than discovered as a softlock at runtime.
        """
        self.entry(identity)
        if not self.entry(identity).record.has_raw_arrival_pair:
            # Fail closed rather than write a delta into a field the engine reads
            # as a point. The 169 class's pair needs the scene origin, which no
            # project value supplies, so an authored arrival is refused outright.
            raise TransitionFieldError(
                f"{identity} is a 169-class record whose +0x14/+0x16 pair is a "
                "scene-relative delta, not an arrival point; authoring an arrival "
                "on this class is refused rather than written as a position"
            )
        if arrival is not None and not isinstance(arrival, TransitionArrival):
            raise TransitionFieldError(
                f"{identity}.arrival must be a TransitionArrival or None, "
                f"got {arrival!r}"
            )
        record = self.entry(identity).record.with_arrival(arrival)
        record.validate()
        if arrival is not None:
            target = self.destination(identity)
            width, height = self.destination_bounds(target)
            if not (0 <= arrival.x < width and 0 <= arrival.y < height):
                raise TransitionFieldError(
                    f"{identity} would place the player at ({arrival.x}, {arrival.y}) "
                    f"in {target}, whose walkable extent is {width}x{height}; that "
                    "point is off the map"
                )
        self._edits[identity] = record

    def derive_arrival(
        self, identity: TransitionIdentity, destination: MapIdentity
    ) -> "TransitionArrival":
        """The safe arrival for pointing ``identity`` at ``destination``.

        Preference order, and the reason for it:

        1. **A point the game already uses for this exact link.** If another record
           in the same source map already reaches ``destination`` and its stored
           arrival lies at one of the destination's doors back, that value is the
           engine's own answer for this connection and is used verbatim.
        2. **The destination's door back: its centre.** A point inside the door
           rectangle is on the map by construction, and it is the door the player
           would use to return, which is what "the direction you warped out of"
           means.

        With no door back there is nothing to derive from - the relative direction
        does not exist - so this refuses rather than inventing one.
        """
        doors = self.reciprocal_doors(identity.source, destination)
        if not doors:
            raise TransitionFieldError(
                f"{destination} has no record leading back to {identity.source}, so "
                "no arrival can be derived from the direction of travel; state one "
                "explicitly (see set_arrival) instead of inheriting the previous "
                "destination's point"
            )
        if not self.entry(identity).record.has_raw_arrival_pair:
            raise TransitionFieldError(
                f"{identity} is a 169-class record whose stored pair is a "
                "scene-relative delta; no arrival can be derived for it"
            )
        for sibling in self.for_map(identity.source):
            if sibling.identity == identity:
                continue
            if self.destination(sibling.identity) != destination:
                continue
            # Only a sibling whose pair IS a point can answer for this link.
            if not sibling.record.has_raw_arrival_pair:
                continue
            point = sibling.record.arrival
            if point is not None and any(
                _arrival_is_near(point, door.record.region) for door in doors
            ):
                return point
        (low_x, high_x), (low_y, high_y) = doors[0].record.region.first, doors[0].record.region.second
        return TransitionArrival(x=(low_x + high_x) // 2, y=(low_y + high_y) // 2)

    def retarget(
        self,
        identity: TransitionIdentity,
        destination: MapIdentity,
        *,
        arrival: "TransitionArrival | None" = None,
        facing: "int | None" = None,
    ) -> tuple["TransitionArrival", int]:
        """Point one transition at ``destination``, and place and face the player.

        One operation on purpose. Changing the destination without changing the
        arrival leaves the arrival pointing into the previous destination's
        geometry - measured at runtime as a softlock when the new map is smaller -
        and without changing the facing it leaves the player walking the way they
        were before the warp, which a runtime observation caught walking West out
        of a south door.

        ``arrival`` and ``facing`` are explicit overrides. When ``facing`` is not
        given the :meth:`default_facing` heuristic is used, and that heuristic is
        labelled a default rather than engine law. Returns the pair that was
        staged.
        """
        self.set_destination(identity, destination)
        if arrival is None:
            arrival = self.derive_arrival(identity, destination)
        self.set_arrival(identity, arrival)
        if facing is None:
            facing = self.default_facing(destination, arrival)
        self.set_facing(identity, facing)
        return arrival, facing

    def set_facing(self, identity: TransitionIdentity, direction: int) -> None:
        """Stage the direction the player is forced to face on arrival.

        This writes the **high-nibble override** (``((direction + 1) << 4)``), not
        the low bits. That is deliberate and it is the whole point: with no
        override the engine leaves the actor facing whatever it was already
        walking, which is what a runtime observation caught walking West out of a
        south door. The low two bits are the door gate and are preserved here.
        """
        self.entry(identity)
        if type(direction) is not int or not 0 <= direction <= FACING_MASK:
            raise TransitionFieldError(
                f"{identity}.facing must be an integer 0..{FACING_MASK}, "
                f"got {direction!r}"
            )
        record = self.entry(identity).record.with_arrival_facing(direction)
        record.validate()
        self._edits[identity] = record

    def set_gate_direction(self, identity: TransitionIdentity, direction: int) -> None:
        """Stage the low two gate bits, preserving the arrival-facing override."""
        self.entry(identity)
        if type(direction) is not int or not 0 <= direction <= FACING_MASK:
            raise TransitionFieldError(
                f"{identity} gate direction must be 0..{FACING_MASK}, got {direction!r}"
            )
        record = self.entry(identity).record.with_gate_direction(direction)
        record.validate()
        self._edits[identity] = record

    def facing(self, identity: TransitionIdentity) -> "int | None":
        """The staged or canonical arrival facing, or None when the record is silent.

        ``None`` is the engine's "keep the actor's own facing" state and is a real
        answer, not a missing one.
        """
        return self.entry(identity).record.facing.arrival_direction

    def gate_direction(self, identity: TransitionIdentity) -> int:
        """The staged or canonical door gate bits (the low two of ``+0x10``)."""
        return self.entry(identity).record.facing.gate_direction

    def default_facing(
        self, destination: MapIdentity, arrival: "TransitionArrival"
    ) -> int:
        """The DEFAULT direction to face on arrival: away from the nearest edge.

        **This is an authoring default, not engine law.** It reproduces what the
        canonical corpus overwhelmingly does - the player leaves the door walking
        into the map - and it matched 498 of 559 records of the 566-class in a
        corpus check. It is a heuristic over the arrival point and the
        destination's walkable box; no instruction consuming ``+0x10`` had been
        traced when it was written, so it must not be quoted as the engine's rule.
        Callers who know the answer pass ``facing`` explicitly.
        """
        width, height = self.destination_bounds(destination)
        distances = {
            FACING_NORTH: height - arrival.y,   # door on the south edge -> walk north
            FACING_SOUTH: arrival.y,            # door on the north edge -> walk south
            FACING_WEST: width - arrival.x,     # door on the east edge -> walk west
            FACING_EAST: arrival.x,             # door on the west edge -> walk east
        }
        return min(distances, key=lambda direction: distances[direction])

    def _map_entries(self):
        """The profile's MapEntry table, resolved once per corpus.

        The profile this corpus was resolved for, not the packaged one: a corpus
        read for another profile that fell back to the canonical table would
        answer `destination_bounds` from a table describing different maps.
        """
        cached = getattr(self, "_map_entry_table", None)
        if cached is None:
            reader = mg.MapGraphicsReader(
                self._base_bytes, self._profile or packaged_profile()
            )
            cached = mg.read_map_entries(reader)
            self._map_entry_table = cached
        return cached

    def root_for(self, source: MapIdentity) -> "TransitionRoot":
        """One map's ``+0x40``/``+0x44`` count/array pair, with the root it hangs on.

        MAP-WARP-CREATE-PROJECT-001 needs the pair for a reason the read path never
        did: a created transition changes the count and re-points the array, so the
        two fields have to be nameable. Nothing else is exposed - the root address is
        provenance here, exactly as a record address is.
        """
        index = self._require_map(source)
        try:
            return self._roots[index]
        except KeyError:
            raise MapTransitionsError(
                f"{source} has no resolved selector-1 root in this corpus"
            ) from None

    def shared_root_maps(self, source: MapIdentity) -> tuple[MapIdentity, ...]:
        """Every OTHER map whose selector-1 root is the same root as ``source``'s.

        Measured over the canonical image: 421 distinct roots serve 452 maps, and 11
        roots are shared by 2..10 maps each - every one of them with a zero count.

        It matters for creation and not for editing. The count and the array pointer
        live on the ROOT, so appending a transition to a shared root would silently
        give every map sharing it the same new connection, including maps the project
        never named. That is the "unrelated maps unchanged" property, so a shared root
        is refused rather than written.
        """
        index = self._require_map(source)
        mine = self.root_for(source).root_address
        return tuple(
            MapIdentity(other)
            for other, root in sorted(self._roots.items())
            if other != index and root.root_address == mine
        )

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


# --- authoring: the semantic edit a project stores ---------------------------
#
# MAP-WARP-PROJECT-AUTHORING-001. Two shapes meet here and they are deliberately
# not the same one:
#
# * `TransitionEdit` is what an author asks for - "this transition now leads to
#   map 41" - and carries no prior values, because a caller stating a prior is a
#   caller asserting what the base holds rather than measuring it;
# * `AuthoredTransitionEdit` is what a project file stores: that request PLUS the
#   value each edited field started from. The build checks those priors against
#   the record the image actually holds, so a project authored against a different
#   image is refused rather than silently reinterpreted - the same fail-closed
#   shape `ByteChange.old` gives every other in-place edit.
#
# Both are shaped so a field left as `None` is not authored at all. That is what
# makes "the author did not edit this" become "the build cannot have changed
# this": an untouched field's bytes come from the canonical record and are never
# re-serialized from a project value.


@dataclass(frozen=True, slots=True)
class TransitionEdit:
    """The fields an author is setting on one transition.

    Every field is optional and at least one is required. A field left as `None` is
    not authored: the build preserves the canonical record's own bytes for it and
    never derives them from the project.

    ``arrival`` is MAP-WARP-RUNTIME-EDIT-001. It is the point the player is placed
    at in the destination, and a retarget that does not set it will drop the player
    wherever the previous destination's arrival pointed - which is how a retarget
    to a smaller map puts them off the map entirely. Prefer
    :meth:`MapTransitions.retarget`, which derives it.
    """

    destination: "MapIdentity | None" = None
    region: "TransitionRegion | None" = None
    arrival: "TransitionArrival | None" = None
    #: The direction the player walks out of the door, 0..3. ``None`` is "the
    #: author did not say", which is what lets a caller ask for the derived default
    #: instead of silently inheriting the previous destination's facing.
    facing: int | None = None

    def __post_init__(self) -> None:
        if (
            self.destination is None
            and self.region is None
            and self.arrival is None
            and self.facing is None
        ):
            raise TransitionFieldError(
                "a transition edit must author a destination, a region, an "
                "arrival, a facing, or a combination"
            )
        if self.destination is not None and not isinstance(self.destination, MapIdentity):
            raise TransitionFieldError(
                f"a transition destination must be a MapIdentity, got {self.destination!r}"
            )
        if self.region is not None and not isinstance(self.region, TransitionRegion):
            raise TransitionFieldError(
                f"a transition region must be a TransitionRegion, got {self.region!r}"
            )
        if self.arrival is not None and not isinstance(self.arrival, TransitionArrival):
            raise TransitionFieldError(
                f"a transition arrival must be a TransitionArrival, got {self.arrival!r}"
            )
        if self.facing is not None and (
            type(self.facing) is not int or not 0 <= self.facing <= FACING_MASK
        ):
            raise TransitionFieldError(
                f"a transition facing must be an integer 0..{FACING_MASK} "
                f"({', '.join(f'{k}={v}' for k, v in sorted(FACING_NAMES.items()))}), "
                f"got {self.facing!r}"
            )


@dataclass(frozen=True, slots=True)
class AuthoredTransitionEdit:
    """One project's stored edit to one transition, and what it started from.

    Each editable field group is a `(prior, authored)` pair and either group may be
    absent, because an author who retargets a door is not also authoring its region.
    A group that is absent is not authored at all, so the canonical record's bytes
    for it survive the build untouched.

    ``prior_*`` is what the project records the canonical record as holding. It is
    stored rather than merely derivable for the reason
    `AuthoredChunkEntry.prior` is: the document itself then proves the edit was
    authored against the record it names, and an image that holds a different value
    makes the build refuse instead of reinterpreting the edit.

    ``prior_arrival``/``arrival`` are the same shape for the measured arrival point,
    with ``None`` meaning "no authored arrival" on both sides. A destination edit
    and an arrival edit are deliberately separate groups: the destination names
    which map, and the arrival names where in it, and an author may move one without
    the other.
    """

    prior_destination: "MapIdentity | None" = None
    destination: "MapIdentity | None" = None
    prior_region: "TransitionRegion | None" = None
    region: "TransitionRegion | None" = None
    prior_arrival: "TransitionArrival | None" = None
    arrival: "TransitionArrival | None" = None
    #: Whether an arrival group is present at all. ``True`` with both values
    #: ``None`` is how a project states "this record has no authored arrival",
    #: which is a different statement from "the author did not touch the arrival".
    arrival_authored: bool = False
    #: The ``+0x10`` facing, prior and authored, with the same present/absent rule.
    #: The stored value is the WHOLE byte, not just the direction, so a record
    #: carrying unresolved high bits round-trips them verbatim.
    prior_facing_raw: int | None = None
    facing_raw: int | None = None
    facing_authored: bool = False

    def __post_init__(self) -> None:
        for prior, authored, label, expected in (
            (self.prior_destination, self.destination, "destination", MapIdentity),
            (self.prior_region, self.region, "region", TransitionRegion),
        ):
            if (prior is None) != (authored is None):
                raise TransitionFieldError(
                    f"a transition edit must state the {label} it started from and "
                    f"the {label} it authors together; got {prior!r} and {authored!r}"
                )
            for value, name in ((prior, f"prior_{label}"), (authored, label)):
                if value is not None and not isinstance(value, expected):
                    raise TransitionFieldError(
                        f"{name} must be a {expected.__name__}, got {value!r}"
                    )
        if not self.arrival_authored and (
            self.prior_arrival is not None or self.arrival is not None
        ):
            raise TransitionFieldError(
                "a transition edit states an arrival value without marking the "
                "arrival group as authored"
            )
        for value, name in (
            (self.prior_arrival, "prior_arrival"),
            (self.arrival, "arrival"),
        ):
            if value is not None and not isinstance(value, TransitionArrival):
                raise TransitionFieldError(
                    f"{name} must be a TransitionArrival or None, got {value!r}"
                )
        if not self.facing_authored and (
            self.prior_facing_raw is not None or self.facing_raw is not None
        ):
            raise TransitionFieldError(
                "a transition edit states a facing byte without marking the facing "
                "group as authored"
            )
        for value, name in (
            (self.prior_facing_raw, "prior_facing_raw"),
            (self.facing_raw, "facing_raw"),
        ):
            if value is not None and (type(value) is not int or not 0 <= value <= 0xFF):
                raise TransitionFieldError(
                    f"{name} must be a byte or None, got {value!r}"
                )
        if (
            self.destination is None
            and self.region is None
            and not self.arrival_authored
            and not self.facing_authored
        ):
            raise TransitionFieldError(
                "a transition edit must author a destination, a region, an "
                "arrival, a facing, or a combination"
            )


@dataclass(frozen=True, slots=True)
class TransitionApplication:
    """What applying a project's transition edits to one image produced.

    ``changes`` is the authority's own byte plan over *every* transition record, not
    only the edited one: an untouched record must re-encode to exactly its original
    bytes, and emitting all of them is what proves that round trip rather than
    assuming it. `plan_changes` then drops every no-op, so a build whose transition
    edits changed nothing contributes no effective change.

    ``provenance`` names only the edits that actually changed a field, so a stored
    pair whose authored value equals its prior is absent from it.
    """

    changes: tuple[ByteChange, ...] = ()
    provenance: tuple[TransitionEditProvenance, ...] = ()


def _require_prior(identity: TransitionIdentity, label: str, actual: object,
                   stored: object) -> None:
    """Refuse an edit whose stored prior is not what the image holds."""
    if stored is not None and stored != actual:
        raise TransitionFieldError(
            f"{identity} was authored against {label} {stored}, but this image's "
            f"record holds {actual}; refusing an edit computed against a different image"
        )


def plan_transition_edits(
    image: bytes,
    edits: Mapping[TransitionIdentity, AuthoredTransitionEdit],
    *,
    profile: RomProfile | None = None,
) -> TransitionApplication:
    """Apply a project's stored transition edits to a canonical image.

    In order:

    1. load the canonical corpus through :func:`read_map_transitions`, so a record
       is reached by `TransitionIdentity` and by nothing else - no address is
       accepted from the project and none is computed by it;
    2. check each stored prior against the record the image actually holds;
    3. stage the authored fields through :meth:`MapTransitions.set_destination`
       and :meth:`MapTransitions.set_region`, which refuse an unknown transition,
       an unknown destination map, and an unordered or degenerate region before
       anything is recorded;
    4. re-validate the corpus and return its own byte plan.

    Nothing here serializes a record: the one encoder is the codec's
    `TransitionRecord.to_bytes`, reached through :meth:`MapTransitions.changes`.
    The edit is a fixed-width overwrite of one 24-byte record, so it allocates
    nothing, relocates nothing and touches no other record.

    An edit whose authored values all equal what the image already holds is a no-op:
    it contributes no provenance and, when nothing else changed, no changes at all.
    That is deliberate - a project that stores a value equal to the base must not
    make the build claim an edit.
    """
    if not edits:
        return TransitionApplication()
    canonical = packaged_profile() if profile is None else profile
    corpus = read_map_transitions(image, canonical)
    provenance: list[TransitionEditProvenance] = []
    for identity in sorted(edits):
        edit = edits[identity]
        if not isinstance(edit, AuthoredTransitionEdit):
            raise TransitionFieldError(
                f"{identity} must be authored as an AuthoredTransitionEdit, "
                f"got {edit!r}"
            )
        entry = corpus.entry(identity)
        before_destination = corpus.destination(identity)
        before_region = entry.record.region
        before_arrival = (
            entry.record.arrival if entry.record.has_raw_arrival_pair else None
        )
        before_facing_raw = entry.record.byte_0x10_raw
        _require_prior(identity, "destination", before_destination, edit.prior_destination)
        _require_prior(identity, "region", before_region, edit.prior_region)
        _require_prior(identity, "arrival", before_arrival, edit.prior_arrival)
        _require_prior(identity, "facing", before_facing_raw, edit.prior_facing_raw)

        if edit.destination is not None:
            corpus.set_destination(identity, edit.destination)
        if edit.region is not None:
            corpus.set_region(identity, edit.region)
        if edit.arrival_authored:
            # After the destination, so the bounds check answers for the map the
            # player will actually arrive in.
            corpus.set_arrival(identity, edit.arrival)
        if edit.facing_authored:
            # The whole byte is restored, high bits included, so an unresolved
            # flag cannot be lost by an edit that only meant to turn the player.
            # A null authored value means "state no override" - which must KEEP
            # the canonical low nibble rather than zero the whole byte, because
            # the gate is the other half of this field and bits 2-3 are unread
            # (FACING_PRESERVED_MASK).
            corpus._edits[identity] = corpus.entry(identity).record.with_facing_raw(
                edit.facing_raw
                if edit.facing_raw is not None
                else (before_facing_raw & FACING_PRESERVED_MASK)
            )

        after_destination = corpus.destination(identity)
        after_region = corpus.entry(identity).record.region
        after_arrival = (
            corpus.entry(identity).record.arrival
            if corpus.entry(identity).record.has_raw_arrival_pair
            else None
        )
        after_facing_raw = corpus.entry(identity).record.byte_0x10_raw
        destination_changed = after_destination != before_destination
        region_changed = after_region != before_region
        arrival_changed = after_arrival != before_arrival
        facing_changed = after_facing_raw != before_facing_raw
        if not (
            destination_changed or region_changed or arrival_changed or facing_changed
        ):
            continue
        provenance.append(
            TransitionEditProvenance(
                identity=identity.key,
                source_map=identity.source.index,
                index=identity.index,
                file_offset=entry.file_offset,
                prior_destination=str(before_destination) if destination_changed else "",
                destination=str(after_destination) if destination_changed else "",
                prior_region=(
                    (before_region.first, before_region.second)
                    if region_changed
                    else None
                ),
                region=(
                    (after_region.first, after_region.second) if region_changed else None
                ),
                prior_arrival=(
                    (before_arrival.x, before_arrival.y)
                    if arrival_changed and before_arrival is not None
                    else None
                ),
                arrival=(
                    (after_arrival.x, after_arrival.y)
                    if arrival_changed and after_arrival is not None
                    else None
                ),
                arrival_changed=arrival_changed,
                prior_facing_raw=before_facing_raw if facing_changed else None,
                facing_raw=after_facing_raw if facing_changed else None,
                facing_changed=facing_changed,
            )
        )
    if not provenance:
        return TransitionApplication()
    # `validate()` re-reads every record - edited and untouched - and returns them;
    # reading it is the corpus-wide check, and `changes()` is the one serializer.
    corpus.validate()
    return TransitionApplication(
        changes=corpus.changes(),
        provenance=tuple(provenance),
    )


# --- creation: a transition the canonical image does not contain --------------
#
# MAP-WARP-CREATE-PROJECT-001. Everything below is the second half of the
# transition capability, and it is deliberately shaped like `map_chunk`'s
# materializer rather than like the edit path above:
#
# * a created transition is named by its own durable identity, never by an address
#   and never by an array index, because the index does not exist until the build
#   appends it;
# * its bytes are composed over a canonical TEMPLATE of the same map, so the
#   UNRESOLVED fields are carried from a record the engine already consumes rather
#   than invented;
# * it needs storage, so this is the first transition domain that allocates - the
#   24-byte record and the expanded `root + 0x44` array - and the only one that
#   writes the root's count and array pointer.
#
# Validating a creation and materializing one are the same code path, so "what may
# be authored" and "what may be built" cannot drift: `_resolve_creation` refuses
# everything a build would refuse, and the authoring API runs it too.


@dataclass(frozen=True, slots=True)
class TransitionRoot:
    """One map's ``root + 0x40`` count and ``root + 0x44`` array pointer."""

    source: MapIdentity
    #: GBA address of the selector-1 root. Provenance only; never an identity.
    root_address: int
    count: int
    #: GBA address of the 4-byte-per-element record pointer array, or 0 with count 0.
    array_address: int

    @property
    def count_offset(self) -> int:
        return self.root_address + ROOT_COUNT_OFFSET

    @property
    def array_pointer_offset(self) -> int:
        return self.root_address + ROOT_ARRAY_OFFSET


@dataclass(frozen=True, slots=True, order=True)
class CreatedTransitionIdentity:
    """A created transition's durable identity: ``map:NNNN/transition:<name>``.

    It contains **no** ROM address, **no** allocated address and **no** array index.
    The index a created record occupies is a build-time fact produced by appending
    it to that map's array, so a project that outlives the build cannot be keyed by
    it - which is exactly why the authored name exists.
    """

    source: MapIdentity
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.source, MapIdentity):
            raise MapTransitionsError(
                f"a created transition's source must be a MapIdentity, got {self.source!r}"
            )
        if not isinstance(self.name, str) or _TRANSITION_NAME.match(self.name) is None:
            raise MapTransitionsError(
                f"a created transition's name is {self.name!r}; it must be lowercase, "
                "start with a letter, and use only letters, digits, '_' and '-' "
                "(at most 64 characters)"
            )

    @property
    def key(self) -> str:
        return f"{self.source.key}/transition:{self.name}"

    def __str__(self) -> str:
        return self.key


@dataclass(frozen=True, slots=True)
class TransitionCreation:
    """The fields an author is setting on a transition that does not yet exist.

    Unlike :class:`TransitionEdit` every one of these is required except
    ``facing``, and that is the point: an edit preserves whatever it does not name,
    while a creation has nothing to preserve. A field a project does not state here
    would have to be invented, so there is no optional field to leave out.

    ``template`` names an existing canonical record of the same source map. It is
    not a default and not a copy of the record: it is the source of the bytes this
    creation does not author, and the build refuses a template whose unresolved
    bytes are not the ones the project recorded.
    """

    identity: CreatedTransitionIdentity
    template: TransitionIdentity
    destination: MapIdentity
    region: TransitionRegion
    arrival: TransitionArrival
    #: The direction the player is forced to face on arrival, 0..3, or ``None`` for
    #: "this record states no override" - the engine's own "keep the actor's facing"
    #: state. Deliberately not inherited from the template: the template's override
    #: was a decision about a different door.
    facing: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.identity, CreatedTransitionIdentity):
            raise TransitionFieldError(
                f"a created transition needs a CreatedTransitionIdentity, got "
                f"{self.identity!r}"
            )
        if not isinstance(self.template, TransitionIdentity):
            raise TransitionFieldError(
                f"{self.identity}.template must be a TransitionIdentity, got "
                f"{self.template!r}"
            )
        if not isinstance(self.destination, MapIdentity):
            raise TransitionFieldError(
                f"{self.identity}.destination must be a MapIdentity, got "
                f"{self.destination!r}"
            )
        if not isinstance(self.region, TransitionRegion):
            raise TransitionFieldError(
                f"{self.identity}.region must be a TransitionRegion, got {self.region!r}"
            )
        if not isinstance(self.arrival, TransitionArrival):
            raise TransitionFieldError(
                f"{self.identity}.arrival must be a TransitionArrival, got "
                f"{self.arrival!r}"
            )
        if self.facing is not None and (
            type(self.facing) is not int or not 0 <= self.facing <= FACING_MASK
        ):
            raise TransitionFieldError(
                f"{self.identity}.facing must be an integer 0..{FACING_MASK} or None, "
                f"got {self.facing!r}"
            )


@dataclass(frozen=True, slots=True)
class AuthoredTransitionCreation:
    """One project's stored creation, plus the template bytes it was authored against.

    The same split :class:`AuthoredTransitionEdit` makes, for the same reason: a
    caller states what it wants created, and the values that merely *pin the base*
    are measured from the canonical image here rather than asserted by the caller.

    ``prior_facing_raw`` and ``prior_unresolved_raw`` are those pins. They are the
    template record's own ``+0x10`` and ``+0x13`` bytes as the canonical image held
    them when the creation was authored, and the build refuses an image whose
    template no longer matches - otherwise the created record's UNRESOLVED bytes
    would silently change under a project nobody re-authored.
    """

    creation: TransitionCreation
    prior_facing_raw: int
    prior_unresolved_raw: int

    def __post_init__(self) -> None:
        if not isinstance(self.creation, TransitionCreation):
            raise TransitionFieldError(
                f"an authored creation must carry a TransitionCreation, got "
                f"{self.creation!r}"
            )
        for value, label in (
            (self.prior_facing_raw, "prior_facing_raw"),
            (self.prior_unresolved_raw, "prior_unresolved_raw"),
        ):
            if type(value) is not int or not 0 <= value <= 0xFF:
                raise TransitionFieldError(
                    f"{self.creation.identity}.{label} must be a byte, got {value!r}"
                )


@dataclass(frozen=True, slots=True)
class TransitionCreationPlan:
    """One creation resolved against an image, before anything is allocated.

    Private in spirit: it is what :func:`_resolve_creation` proves and what
    :func:`materialize_transition_creations` then spends storage on.
    """

    identity: CreatedTransitionIdentity
    request: TransitionCreation
    template_entry: TransitionEntry
    #: The canonical array position the created record is appended at.
    index: int
    record: TransitionRecord


@dataclass(frozen=True, slots=True)
class TransitionCreationMaterialization:
    """What materializing a project's creations produced for one build.

    The same shape every allocating domain returns: the attributed byte changes, the
    allocator-issued authorization for the spans above canonical EOF, the spans the
    next domain must avoid, the provenance the manifest publishes, and (when this
    domain allocates) the generated-image policy derived from its own allocations.
    """

    changes: tuple[ByteChange, ...] = ()
    generated_allocations: tuple[GeneratedAllocationProvenance, ...] = ()
    reserved: tuple[RomRange, ...] = ()
    provenance: tuple[TransitionCreationProvenance, ...] = ()
    generated_image: GeneratedImage | None = None


def created_record_fields() -> tuple[TransitionRecordFieldProvenance, ...]:
    """The 24-byte record's field list with each field's authored-bit mask.

    One entry per physical field, in byte order, covering ``+0x00..+0x17`` exactly
    once. ``source`` is derived from the mask the codec states, so the provenance a
    manifest carries and the composition the build performs cannot disagree about
    which bytes were authored.
    """
    fields: list[TransitionRecordFieldProvenance] = []
    for item in TRANSITION_LAYOUT:
        mask = CREATED_FIELD_AUTHORED_MASKS[item.name]
        whole = (1 << (item.width * 8)) - 1
        if mask == 0:
            source = "template"
        elif mask == whole:
            source = "authored"
        else:
            source = "authored+template"
        fields.append(
            TransitionRecordFieldProvenance(
                offset=item.offset,
                width=item.width,
                field=item.name,
                source=source,
                authored_mask=mask,
            )
        )
    return tuple(fields)


def _resolve_creation(
    corpus: MapTransitions,
    identity: CreatedTransitionIdentity,
    authored: AuthoredTransitionCreation,
    *,
    offset: int = 0,
) -> TransitionCreationPlan:
    """Validate one creation against a corpus, or refuse it by name.

    Everything a created transition must satisfy, in one place, so the authoring API
    and the build refuse the same forms with the same words:

    1. the source map exists in this profile's table;
    2. the source map's selector-1 root is **not shared** with another map, because
       the count and the array pointer live on the root and a shared root would give
       every map sharing it the same new connection;
    3. the template identity exists, belongs to the **same** source map, and is a
       supported **566-class** record - the only class whose ``+0x14``/``+0x16`` pair
       is an absolute arrival, which is what makes an authored arrival a statement
       about the record alone;
    4. the template's ``+0x10`` and ``+0x13`` are the bytes the project recorded;
    5. the destination resolves to a map, and the arrival lies inside that map's own
       walkable extent;
    6. the composed record is a valid record of the supported family, and is **not**
       byte-identical to its template - a creation, not an alias;
    7. the map's count can hold one more element.

    ``offset`` is the position of this creation within its map's own batch of
    creations, so the plan's ``index`` is the array position the record will occupy
    once the whole batch is appended. A caller validating a single creation in
    isolation (the authoring API) leaves it at 0: it checks the same forms, and the
    index it reports is the one the creation would take if it were the only one.
    """
    creation = authored.creation
    if creation.identity != identity:
        raise TransitionFieldError(
            f"the request for {identity} carries the identity "
            f"{creation.identity}; the two must agree"
        )
    corpus._require_map(identity.source)
    # Sharing is checked before the template, and the order is deliberate: every one
    # of the canonical image's 11 shared roots carries a count of 0, and a corpus in
    # which two maps reached one non-empty array would already be refused as a
    # shared record - so a map on a shared root has no 566-class record of its own to
    # use as a template anyway. Reporting the sharing first names the real reason the
    # map cannot gain a connection, instead of reporting the symptom.
    sharers = corpus.shared_root_maps(identity.source)
    if sharers:
        raise TransitionFieldError(
            f"{identity} cannot be created: {identity.source}'s selector-1 root is "
            f"shared with "
            + ", ".join(str(other) for other in sharers)
            + "; the count at root+0x40 and the array pointer at root+0x44 belong to "
            "the root, so appending here would change those maps' connections too"
        )
    if creation.template.source != identity.source:
        raise TransitionFieldError(
            f"{identity} names template {creation.template}, which belongs to "
            f"{creation.template.source}; a template must be a record of the same "
            "source map, because the bytes the creation does not author are copied "
            "from it"
        )
    try:
        template_entry = corpus.entry(creation.template)
    except UnknownTransitionError:
        raise TransitionFieldError(
            f"{identity} names template {creation.template}, which this image does "
            "not contain"
        ) from None
    template_record = template_entry.record
    if template_record.class_raw != CREATED_CLASS_RAW:
        raise TransitionFieldError(
            f"{identity} names template {creation.template}, whose class word is "
            f"{template_record.class_raw:#010x}; a created transition is supported "
            f"only over the measured {CREATED_CLASS_RAW:#010x} class, because the "
            "other class's arrival pair is a scene-relative delta rather than a point"
        )
    if template_record.byte_0x10_raw != authored.prior_facing_raw:
        raise TransitionFieldError(
            f"{identity} was authored against template {creation.template} with "
            f"+0x10 = {authored.prior_facing_raw:#04x}, but this image's record holds "
            f"{template_record.byte_0x10_raw:#04x}; refusing a creation computed "
            "against a different image"
        )
    if template_record.byte_0x13_raw != authored.prior_unresolved_raw:
        raise TransitionFieldError(
            f"{identity} was authored against template {creation.template} with "
            f"+0x13 = {authored.prior_unresolved_raw:#04x}, but this image's record "
            f"holds {template_record.byte_0x13_raw:#04x}; refusing a creation "
            "computed against a different image"
        )
    root = corpus.root_for(identity.source)
    if root.count + offset >= MAX_TRANSITION_COUNT:
        raise TransitionFieldError(
            f"{identity} cannot be created: {identity.source}'s transition count is "
            f"{root.count} and this is creation {offset + 1} of the batch, so the "
            "count would overflow the 4-byte field at root+0x40"
        )
    destination_key = corpus.key_for(creation.destination)
    width, height = corpus.destination_bounds(creation.destination)
    if not (0 <= creation.arrival.x < width and 0 <= creation.arrival.y < height):
        raise TransitionFieldError(
            f"{identity} would place the player at "
            f"({creation.arrival.x}, {creation.arrival.y}) in {creation.destination}, "
            f"whose walkable extent is {width}x{height}; that point is off the map"
        )
    record = compose_created_record(
        template_record,
        destination_key=destination_key,
        region=creation.region,
        arrival=creation.arrival,
        facing=creation.facing,
    )
    record.validate()
    if record.class_raw != CREATED_CLASS_RAW:  # pragma: no cover - composition copies it
        raise TransitionFieldError(
            f"{identity} composed to class {record.class_raw:#010x}, which is not the "
            f"supported created class {CREATED_CLASS_RAW:#010x}"
        )
    if record == template_record:
        raise TransitionFieldError(
            f"{identity} is byte-identical to its template {creation.template}; every "
            "field a created transition authors is the template's own value, which is "
            "a copy rather than a creation"
        )
    return TransitionCreationPlan(
        identity=identity,
        request=creation,
        template_entry=template_entry,
        index=root.count + offset,
        record=record,
    )


def _creation_requests(
    creations: Mapping[CreatedTransitionIdentity, AuthoredTransitionCreation],
) -> dict[int, list[tuple[CreatedTransitionIdentity, AuthoredTransitionCreation]]]:
    """Group authored creations by source map, each list sorted by authored name."""
    by_map: dict[
        int, list[tuple[CreatedTransitionIdentity, AuthoredTransitionCreation]]
    ] = {}
    for identity, authored in sorted(creations.items()):
        by_map.setdefault(identity.source.index, []).append((identity, authored))
    for entries in by_map.values():
        entries.sort(key=lambda item: item[0].name)
    return by_map


def materialize_transition_creations(
    image: bytes,
    creations: Mapping[CreatedTransitionIdentity, AuthoredTransitionCreation],
    *,
    profile: RomProfile | None = None,
    reserved: Iterable[RomRange] = (),
) -> TransitionCreationMaterialization:
    """Allocate, emit and reference every transition a project creates.

    **One array request per source map and one record request per creation**, each
    against the caller's reservation set, ordered by the requests' own anchor
    identities - so the same project produces the same addresses on every machine.
    Both kinds are ``EXPANDED_ONLY``: the canonical image declares one 256-byte
    VERIFIED_FREE region that other domains already draw on, this domain's demand
    grows with the project, and above-EOF placement is the addressability this
    capability exists to prove.

    Per map, in the order the ticket's build sequence states it:

    1. resolve and refuse the whole map's creations (see :func:`_resolve_creation`);
    2. allocate the new record and the expanded array;
    3. materialize the record above EOF;
    4. materialize the array: the canonical element pointers, byte for byte, followed
       by one pointer per created record - which is why the canonical array's
       neighbourhood is never touched;
    5. update ``root + 0x40`` from ``N`` to ``N + k``;
    6. update ``root + 0x44`` to the expanded array's address;
    7. record provenance, one entry per created transition, including the field-level
       accounting of the 24 bytes.

    The canonical array is **not** rewritten and the canonical records are not moved:
    the expanded array is a new span that carries the same elements plus the created
    ones, so every existing transition keeps its record, its address and its order,
    and the created record is appended at ``index = N`` - the position the engine's
    own descending walk consumes first.
    """
    if not creations:
        return TransitionCreationMaterialization()
    resolved_profile = profile if profile is not None else packaged_profile()
    corpus = read_map_transitions(image, resolved_profile)
    expansion = resolved_profile.generated_expansion
    prior_reservations = tuple(reserved)
    taken: list[OwnedRegion] = [
        OwnedRegion(span, "build reservation") for span in prior_reservations
    ]

    changes: list[ByteChange] = []
    generated: list[GeneratedAllocationProvenance] = []
    provenance: list[TransitionCreationProvenance] = []
    by_map = _creation_requests(creations)

    for map_index in sorted(by_map):
        entries = by_map[map_index]
        plans = [
            _resolve_creation(corpus, identity, authored, offset=offset)
            for offset, (identity, authored) in enumerate(entries)
        ]
        root = corpus.root_for(MapIdentity(map_index))
        count = root.count
        new_count = count + len(plans)
        if new_count > MAX_TRANSITION_COUNT:
            raise TransitionFieldError(
                f"map:{map_index:04d} would hold {new_count} transitions, which does "
                "not fit the 4-byte count at root+0x40"
            )
        array_owner = f"{CREATION_ARRAY_PREFIX}{MapIdentity(map_index).key}"
        record_owners = [
            f"{CREATION_RECORD_PREFIX}{plan.identity.key}" for plan in plans
        ]
        # One batch per map, so the array and its records are placed clear of each
        # other and of every earlier domain's spans, in one deterministic order.
        # The array request sorts before the record requests, so the array takes the
        # lower address of the two; nothing depends on that beyond determinism.
        requests = [
            AllocationRequest(
                AnchorId(array_owner),
                array_owner,
                ARRAY_ELEMENT_WIDTH * new_count,
                RECORD_ALIGNMENT,
                kind=AllocationKind.TRANSITION_POINTER_ARRAY,
                addressability=Addressability.EXPANDED_ONLY,
                evidence=(
                    "root+0x44 is a full 32-bit little-endian GBA address on 452 of "
                    "452 canonical roots and every array element is one on 735 of "
                    "735; the canonical array is packed against its own root and "
                    "against neighbouring records, so a count that grows needs a new "
                    "span, and the canonical image declares one 256-byte "
                    "VERIFIED_FREE region this domain must not exhaust"
                ),
            )
        ] + [
            AllocationRequest(
                AnchorId(owner),
                owner,
                TRANSITION_SIZE,
                RECORD_ALIGNMENT,
                kind=AllocationKind.TRANSITION_RECORD,
                addressability=Addressability.EXPANDED_ONLY,
                evidence=(
                    "an array element is a full 32-bit little-endian GBA pointer, and "
                    "a created record cannot overwrite the bytes that follow the "
                    "canonical array - for map 40 those bytes are its own root"
                ),
            )
            for owner in record_owners
        ]
        allocations = allocate(resolved_profile, requests, occupied=taken)
        by_owner = {item.request.owner: item for item in allocations}
        array_allocation = by_owner[array_owner]
        for owner in record_owners:
            taken.append(OwnedRegion(by_owner[owner].range, owner))
        taken.append(OwnedRegion(array_allocation.range, array_owner))

        if expansion is None:  # pragma: no cover - EXPANDED_ONLY cannot place otherwise
            raise TransitionFieldError(
                f"map:{map_index:04d}: the allocator placed a created transition "
                "above canonical EOF, but this ROM's profile declares no generated "
                "expansion to authorize that"
            )
        padding = bytes([expansion.padding_byte])

        # 3. the records.
        for plan, owner in zip(plans, record_owners):
            allocation = by_owner[owner]
            offset = allocation.range.start.value
            body = plan.record.to_bytes()
            changes.append(
                ByteChange(
                    offset=offset,
                    old=padding * len(body),
                    new=body,
                    owner=owner,
                    reason=(
                        f"created transition record {plan.identity} over template "
                        f"{plan.request.template}"
                    ),
                )
            )
            generated.append(
                allocation.generated_allocation_provenance(
                    domain=CREATION_DOMAIN,
                    resource=plan.identity.key,
                    # The field that names this record: the expanded array's own
                    # element, which this same batch places, so its offset is known
                    # here. It is a generated span's address rather than a canonical
                    # one, which is exactly the case the write layer's `pointer_offset`
                    # documents as "no canonical field to name".
                    pointer_offset=(
                        array_allocation.range.start.value
                        + ARRAY_ELEMENT_WIDTH * plan.index
                    ),
                    source_range=RomRange(
                        FileOffset(
                            GbaRomAddress(
                                plan.template_entry.record_address
                            ).to_file_offset(len(image))
                        ),
                        TRANSITION_SIZE,
                    ),
                )
            )

        # 4. the expanded array: the canonical pointers verbatim, then the new ones.
        prior_bytes = (
            bytes(image[
                GbaRomAddress(root.array_address).to_file_offset(len(image)):
                GbaRomAddress(root.array_address).to_file_offset(len(image))
                + ARRAY_ELEMENT_WIDTH * count
            ])
            if count
            else b""
        )
        if len(prior_bytes) != ARRAY_ELEMENT_WIDTH * count:  # pragma: no cover
            raise TransitionFieldError(
                f"map:{map_index:04d}: the canonical pointer array at "
                f"0x{root.array_address:08X} does not fit inside the image"
            )
        appended = b"".join(
            by_owner[owner].rom_address.to_bytes(ARRAY_ELEMENT_WIDTH, "little")
            for owner in record_owners
        )
        array_body = prior_bytes + appended
        array_offset = array_allocation.range.start.value
        changes.append(
            ByteChange(
                offset=array_offset,
                old=padding * len(array_body),
                new=array_body,
                owner=array_owner,
                reason=(
                    f"expanded transition pointer array: {count} canonical element(s) "
                    f"plus {len(plans)} created"
                ),
            )
        )
        generated.append(
            array_allocation.generated_allocation_provenance(
                domain=CREATION_DOMAIN,
                resource=MapIdentity(map_index).key,
                pointer_offset=GbaRomAddress(root.array_pointer_offset).to_file_offset(
                    len(image)
                ),
                source_range=(
                    RomRange(
                        FileOffset(
                            GbaRomAddress(root.array_address).to_file_offset(len(image))
                        ),
                        ARRAY_ELEMENT_WIDTH * count,
                    )
                    if count
                    else RomRange(
                        FileOffset(
                            GbaRomAddress(root.array_pointer_offset).to_file_offset(
                                len(image)
                            )
                        ),
                        ARRAY_ELEMENT_WIDTH,
                    )
                ),
            )
        )

        # 5 and 6. the root's count and array pointer.
        count_offset = GbaRomAddress(root.count_offset).to_file_offset(len(image))
        array_pointer_offset = GbaRomAddress(root.array_pointer_offset).to_file_offset(
            len(image)
        )
        prior_count_bytes = image[count_offset:count_offset + 4]
        prior_pointer_bytes = image[array_pointer_offset:array_pointer_offset + 4]
        if len(prior_count_bytes) != 4 or len(prior_pointer_bytes) != 4:
            # The corpus resolved both fields from this image, so a short read means
            # the root sits too close to EOF for the write this creation needs.
            raise TransitionFieldError(
                f"map:{map_index:04d}: root+0x40/+0x44 are not fully inside the image, "
                "so the count and array pointer cannot be rewritten"
            )
        if int.from_bytes(prior_count_bytes, "little") != count:  # pragma: no cover
            raise TransitionFieldError(
                f"map:{map_index:04d}: root+0x40 read as {count} through the corpus "
                "but holds different bytes; refusing to overwrite an unexplained field"
            )
        if int.from_bytes(prior_pointer_bytes, "little") != root.array_address:
            # pragma: no cover - the corpus read both from this image
            raise TransitionFieldError(
                f"map:{map_index:04d}: root+0x44 read as 0x{root.array_address:08X} "
                "through the corpus but holds different bytes; refusing to overwrite "
                "an unexplained field"
            )
        changes.append(
            ByteChange(
                offset=count_offset,
                old=prior_count_bytes,
                new=new_count.to_bytes(4, "little"),
                owner=array_owner,
                reason=(
                    f"map:{map_index:04d} root+0x40 transition count {count} -> "
                    f"{new_count}"
                ),
            )
        )
        changes.append(
            ByteChange(
                offset=array_pointer_offset,
                old=prior_pointer_bytes,
                new=array_allocation.rom_address.to_bytes(4, "little"),
                owner=array_owner,
                reason=(
                    f"map:{map_index:04d} root+0x44 references the expanded transition "
                    f"pointer array 0x{array_allocation.rom_address:08X}"
                ),
            )
        )

        # 7. provenance, one entry per created transition.
        fields = created_record_fields()
        for plan, owner in zip(plans, record_owners):
            record_allocation = by_owner[owner]
            creation = plan.request
            provenance.append(
                TransitionCreationProvenance(
                    identity=plan.identity.key,
                    source_map=map_index,
                    index=plan.index,
                    template=str(creation.template),
                    template_address=plan.template_entry.record_address,
                    destination=str(creation.destination),
                    region=(creation.region.first, creation.region.second),
                    arrival=(creation.arrival.x, creation.arrival.y),
                    facing_raw=plan.record.byte_0x10_raw,
                    facing=creation.facing,
                    record_address=record_allocation.rom_address,
                    record_file_offset=record_allocation.range.start.value,
                    record_size=TRANSITION_SIZE,
                    array_address=array_allocation.rom_address,
                    array_file_offset=array_offset,
                    array_size=len(array_body),
                    count_offset=count_offset,
                    prior_count=count,
                    count=new_count,
                    array_pointer_offset=array_pointer_offset,
                    prior_array_address=root.array_address,
                    count_bytes=new_count.to_bytes(4, "little").hex(),
                    array_pointer_bytes=array_allocation.rom_address.to_bytes(
                        4, "little"
                    ).hex(),
                    record_pointer_bytes=record_allocation.rom_address.to_bytes(
                        ARRAY_ELEMENT_WIDTH, "little"
                    ).hex(),
                    expanded=record_allocation.is_expanded,
                    expansion_evidence=record_allocation.free_region_evidence,
                    prior_facing_raw=plan.template_entry.record.byte_0x10_raw,
                    prior_unresolved_raw=plan.template_entry.record.byte_0x13_raw,
                    fields=fields,
                )
            )

    spans = tuple(region.range for region in taken[len(prior_reservations):])
    generated_image: GeneratedImage | None = None
    if generated and expansion is not None:
        generated_image = expansion.generated_image(
            resolved_profile.size,
            tuple(item.allocated_range for item in generated),
        )
    return TransitionCreationMaterialization(
        changes=tuple(changes),
        generated_allocations=tuple(generated),
        reserved=spans,
        provenance=tuple(provenance),
        generated_image=generated_image,
    )


# --- authoring: project persistence ------------------------------------------
#
# The one authority through which a transition edit reaches the project. It is
# shaped like `map_paint.set_layout_cells` on purpose: validate the WHOLE batch
# against the canonical image, load the project ONCE, apply the batch on top of
# what is committed, and write only when the result actually differs. That is what
# makes a batch one write, an undo of a transition that was never authored a
# removal, and a re-issue of the value already committed a no-op.


def read_transition_edits(project_dir) -> "TransitionEdits":
    """The committed authored transition edits for a project, in one load.

    Reads the project's own document only. It consults no image, so a caller that
    only wants to know what is authored can ask without one.
    """
    from .project import read_project

    return read_project(project_dir).transitions


def _map_identity(key: "str | None") -> "MapIdentity | None":
    """A project's durable ``map:NNNN`` key as the SDK's own identity.

    The authored layer already refuses any other shape at load (`_MAP_KEY`), so
    this only has to be the one place the two representations meet - and it says so
    loudly rather than indexing a string that was never checked.
    """
    if key is None:
        return None
    if not isinstance(key, str) or not key.startswith("map:"):
        raise TransitionFieldError(
            f"{key!r} is not a 'map:NNNN' map identity"
        )
    try:
        return MapIdentity(int(key[4:], 10))
    except ValueError:
        raise TransitionFieldError(
            f"{key!r} is not a 'map:NNNN' map identity"
        ) from None


def transition_edits_to_requests(edits) -> dict[TransitionIdentity, AuthoredTransitionEdit]:
    """A project's stored edits as the authority's own request type.

    MAP-WARP-WORKBENCH-001. `AuthoredTransitionEdit` is what
    :func:`plan_transition_edits` applies and what the build passes it, so this is
    the single conversion from the project document's durable keys, point pairs and
    facing bytes into the SDK's identities and values. A surface that shows an
    author what the project currently authors therefore reads the same values the
    build will write, rather than parsing the document a second way.

    It is deliberately mechanical: nothing is inferred, and a value the authored
    layer already refused cannot reach here.
    """
    requests: dict[TransitionIdentity, AuthoredTransitionEdit] = {}
    for (map_index, position), entry in sorted(edits.edits().items()):
        requests[TransitionIdentity(MapIdentity(map_index), position)] = (
            AuthoredTransitionEdit(
                prior_destination=_map_identity(entry.prior_destination),
                destination=_map_identity(entry.destination),
                prior_region=entry.prior_region,
                region=entry.region,
                prior_arrival=(
                    TransitionArrival(*entry.prior_arrival)
                    if entry.prior_arrival is not None
                    else None
                ),
                arrival=(
                    TransitionArrival(*entry.arrival)
                    if entry.arrival is not None
                    else None
                ),
                arrival_authored=entry.arrival_authored,
                prior_facing_raw=entry.prior_facing_raw,
                facing_raw=entry.facing_raw,
                facing_authored=entry.facing_authored,
            )
        )
    return requests


def read_project_transition_requests(
    project_dir,
) -> dict[TransitionIdentity, AuthoredTransitionEdit]:
    """A project's authored transition edits, in one read, as build requests.

    The read a surface that displays the project's current connections uses: one
    project load, no image, no offset and no document parsing of its own.
    """
    return transition_edits_to_requests(read_transition_edits(project_dir))


def transition_creations_to_requests(
    creations,
) -> dict[CreatedTransitionIdentity, AuthoredTransitionCreation]:
    """A project's stored creations as the authority's own request type.

    The single conversion from the created-transition document's durable keys into
    the SDK's identities and values, matching
    :func:`transition_edits_to_requests`. Nothing is inferred: the document already
    refused any other shape, and the template bytes the creation preserves are
    carried through as the priors :func:`_resolve_creation` checks.
    """
    requests: dict[CreatedTransitionIdentity, AuthoredTransitionCreation] = {}
    for (map_index, name), entry in sorted(creations.edits().items()):
        identity = CreatedTransitionIdentity(MapIdentity(map_index), name)
        requests[identity] = AuthoredTransitionCreation(
            creation=TransitionCreation(
                identity=identity,
                template=_transition_identity(entry.template),
                destination=_map_identity(entry.destination),
                region=entry.region,
                arrival=TransitionArrival(*entry.arrival),
                facing=entry.facing,
            ),
            prior_facing_raw=entry.prior_facing_raw,
            prior_unresolved_raw=entry.prior_unresolved_raw,
        )
    return requests


def read_transition_creations(project_dir):
    """The committed created transitions for a project, in one load.

    Reads the project's own document only. It consults no image, so a caller that
    only wants to know what the project creates can ask without one.
    """
    from .project import read_project

    return read_project(project_dir).transition_creations


def read_project_transition_creations(
    project_dir,
) -> dict[CreatedTransitionIdentity, AuthoredTransitionCreation]:
    """A project's created transitions, in one read, as build requests."""
    return transition_creations_to_requests(read_transition_creations(project_dir))


def _transition_identity(key: object) -> TransitionIdentity:
    """A project's durable ``map:NNNN/transition:IIII`` key as an SDK identity.

    The document layer already refused any other shape (`_TRANSITION_TEMPLATE_KEY`),
    so this is the one place the two representations meet - and it raises rather
    than indexing a string that was never checked.
    """
    if not isinstance(key, str):
        raise TransitionFieldError(
            f"a transition template identity must be a string, got {key!r}"
        )
    match = re.match(r"map:(\d{4})/transition:(\d{4})$", key)
    if match is None:
        raise TransitionFieldError(
            f"{key!r} is not a 'map:NNNN/transition:IIII' transition identity"
        )
    return TransitionIdentity(MapIdentity(int(match.group(1), 10)), int(match.group(2), 10))


def set_transition_creations(
    project_dir,
    profile: RomProfile,
    canonical_bytes: bytes,
    creations: Mapping[CreatedTransitionIdentity, "TransitionCreation | None"],
) -> bool:
    """Validate and persist a batch of created transitions in ONE write.

    The creation-side mirror of :func:`set_transition_edits`, with the same three
    properties: the WHOLE batch is validated against the canonical image through the
    same :func:`_resolve_creation` a build uses before any document is touched; the
    project is loaded once and the batch applied on top of what is committed; and
    the document is rewritten only when the result differs.

    ``None`` means "this project does not create this transition", which is how an
    undo reverses. The stored template priors are **measured from the canonical
    image here**, never taken from the caller, so the document's proof-of-base is
    something this SDK read rather than something a caller asserted.
    """
    from .project import (
        AuthoredTransitionCreation as StoredCreation,
        TransitionCreations,
        read_project,
        write_transition_creations,
    )

    corpus = read_map_transitions(canonical_bytes, profile)
    requested: dict[CreatedTransitionIdentity, TransitionCreation] = {}
    for identity, request in sorted(creations.items()):
        if request is None:
            continue
        if not isinstance(request, TransitionCreation):
            raise TransitionFieldError(
                f"{identity} must be authored as a TransitionCreation, got {request!r}"
            )
        if request.identity != identity:
            raise TransitionFieldError(
                f"the request for {identity} carries the identity {request.identity}; "
                "the two must agree"
            )
        requested[identity] = request

    # Pass 1 - resolve and refuse the whole batch before any document is touched.
    # The priors are measured here, so this is the same check the build performs.
    measured: dict[CreatedTransitionIdentity, AuthoredTransitionCreation] = {}
    for identity, request in requested.items():
        template = corpus.entry(request.template)
        authored = AuthoredTransitionCreation(
            creation=request,
            prior_facing_raw=template.record.byte_0x10_raw,
            prior_unresolved_raw=template.record.byte_0x13_raw,
        )
        _resolve_creation(corpus, identity, authored)
        measured[identity] = authored

    committed = read_project(project_dir).transition_creations.edits()
    updated = dict(committed)
    for identity, authored in measured.items():
        key = (identity.source.index, identity.name)
        updated[key] = StoredCreation(
            source=identity.source.key,
            name=identity.name,
            template=str(authored.creation.template),
            destination=str(authored.creation.destination),
            region=authored.creation.region,
            arrival=(authored.creation.arrival.x, authored.creation.arrival.y),
            prior_facing_raw=authored.prior_facing_raw,
            prior_unresolved_raw=authored.prior_unresolved_raw,
            facing=authored.creation.facing,
        )
    for identity, request in sorted(creations.items()):
        if request is None:
            updated.pop((identity.source.index, identity.name), None)

    if updated == committed:
        return False
    write_transition_creations(project_dir, TransitionCreations.from_edits(updated))
    return True


def remove_transition_creation(
    project_dir, identity: CreatedTransitionIdentity
) -> bool:
    """Drop one created transition. Returns whether anything was removed."""
    from .project import TransitionCreations, read_project, write_transition_creations

    project = read_project(project_dir)
    committed = project.transition_creations.edits()
    key = (identity.source.index, identity.name)
    if key not in committed:
        return False
    updated = dict(committed)
    del updated[key]
    write_transition_creations(project_dir, TransitionCreations.from_edits(updated))
    return True


def set_transition_edits(
    project_dir,
    profile: RomProfile,
    canonical_bytes: bytes,
    edits: Mapping[TransitionIdentity, "TransitionEdit | None"],
) -> bool:
    """Validate and persist a batch of transition edits in ONE write.

    ``edits`` maps a transition identity to the fields the author is setting, or to
    ``None`` meaning "this transition carries no authored edit" - which is how an
    undo of a transition that was never edited reverses.

    The WHOLE batch is validated against the canonical image first, through the same
    authority a build uses, so a batch containing one illegal entry writes nothing
    at all rather than half of itself, and "what may be authored" and "what may be
    built" cannot drift apart. The project is then loaded ONCE, the batch is applied
    on top of what is already committed, and the document is rewritten only when the
    resulting set differs from the one that was loaded.

    The stored prior values are read from the canonical record HERE, not taken from
    the caller: the project file's proof-of-base is then something this SDK measured
    rather than something a caller asserted.

    Setting a field back to the value the canonical record already holds removes
    that field's stored pair rather than recording a pretend edit, so a project
    cannot claim an authority it does not have. Returns whether the project changed.
    """
    from .project import (
        AuthoredTransition,
        TransitionEdits,
        read_project,
        write_transition_edits,
    )

    corpus = read_map_transitions(canonical_bytes, profile)
    # Pass 1 - resolve and refuse the whole batch before any document is touched.
    requests: dict[TransitionIdentity, TransitionEdit] = {}
    for identity, request in sorted(edits.items()):
        if request is None:
            continue
        if not isinstance(request, TransitionEdit):
            raise TransitionFieldError(
                f"{identity} must be authored as a TransitionEdit, got {request!r}"
            )
        corpus.entry(identity)
        if request.destination is not None:
            corpus.key_for(request.destination)
        requests[identity] = request

    committed = read_project(project_dir).transitions.edits()
    updated = dict(committed)
    for identity, request in requests.items():
        key = (identity.source.index, identity.index)
        existing = updated.get(key)
        prior_destination = existing.prior_destination if existing else None
        destination = existing.destination if existing else None
        prior_region = existing.prior_region if existing else None
        region = existing.region if existing else None
        prior_arrival = existing.prior_arrival if existing and existing.arrival_authored else None
        arrival = existing.arrival if existing and existing.arrival_authored else None
        arrival_authored = bool(existing and existing.arrival_authored)
        before_destination = corpus.destination(identity)
        before_region = corpus.entry(identity).record.region
        before_arrival = (
            corpus.entry(identity).record.arrival
            if corpus.entry(identity).record.has_raw_arrival_pair
            else None
        )
        if request.arrival is not None and not corpus.entry(identity).record.has_raw_arrival_pair:
            raise TransitionFieldError(
                f"{identity} is a 169-class record whose +0x14/+0x16 pair is a "
                "scene-relative delta, not an arrival point; authoring an arrival "
                "on this class is refused rather than written as a position"
            )
        before_facing_raw = corpus.entry(identity).record.byte_0x10_raw
        prior_facing_raw = (
            existing.prior_facing_raw if existing and existing.facing_authored else None
        )
        facing_raw = existing.facing_raw if existing and existing.facing_authored else None
        facing_authored = bool(existing and existing.facing_authored)
        if request.destination is not None:
            if request.destination == before_destination:
                # Set back to what the base holds: an authored pair that changes
                # nothing would be a claim this project does not have.
                prior_destination = destination = None
            else:
                prior_destination = before_destination.key
                destination = request.destination.key
        if request.region is not None:
            if request.region == before_region:
                prior_region = region = None
            else:
                prior_region, region = before_region, request.region
        if request.arrival is not None:
            # Validate the point against the map it will be used in, after the
            # destination has been resolved, so an off-map arrival is refused at
            # authoring time rather than discovered as a runtime softlock.
            staged = corpus.entry(identity).record
            if request.destination is not None:
                staged = staged.with_destination_key(corpus.key_for(request.destination))
            target = corpus.map_for_key(staged.destination_key)
            width, height = corpus.destination_bounds(target)
            if not (0 <= request.arrival.x < width and 0 <= request.arrival.y < height):
                raise TransitionFieldError(
                    f"{identity} would place the player at "
                    f"({request.arrival.x}, {request.arrival.y}) in {target}, whose "
                    f"walkable extent is {width}x{height}; that point is off the map"
                )
            point = (request.arrival.x, request.arrival.y)
            prior_point = (
                (before_arrival.x, before_arrival.y) if before_arrival is not None else None
            )
            arrival_authored = True
            if point == prior_point:
                # Stated back to the base value: no authored arrival.
                prior_arrival = arrival = None
                arrival_authored = False
            else:
                prior_arrival, arrival = prior_point, point
        if request.facing is not None:
            # `TransitionEdit.facing` is the ARRIVAL facing - the high-nibble
            # override the 566 update path turns into (v >> 4) - 1 - because that
            # is the half that forces the sprite. The low two bits are the door
            # gate and are carried through untouched.
            authored_raw = ((request.facing + 1) << 4) | (
                before_facing_raw & FACING_PRESERVED_MASK
            )
            if authored_raw == before_facing_raw:
                prior_facing_raw = facing_raw = None
                facing_authored = False
            else:
                prior_facing_raw, facing_raw = before_facing_raw, authored_raw
                facing_authored = True
        if (
            destination is None
            and region is None
            and not arrival_authored
            and not facing_authored
        ):
            updated.pop(key, None)
        else:
            updated[key] = AuthoredTransition(
                prior_destination=prior_destination,
                destination=destination,
                prior_region=prior_region,
                region=region,
                prior_arrival=prior_arrival,
                arrival=arrival,
                arrival_authored=arrival_authored,
                prior_facing_raw=prior_facing_raw,
                facing_raw=facing_raw,
                facing_authored=facing_authored,
            )
    for identity, request in sorted(edits.items()):
        if request is None:
            updated.pop((identity.source.index, identity.index), None)

    if updated == committed:
        return False
    write_transition_edits(project_dir, TransitionEdits.from_edits(updated))
    return True


def remove_transition_edit(project_dir, identity: TransitionIdentity) -> bool:
    """Drop one transition's authored edit. Returns whether anything was removed."""
    from .project import TransitionEdits, read_project, write_transition_edits

    project = read_project(project_dir)
    committed = project.transitions.edits()
    key = (identity.source.index, identity.index)
    if key not in committed:
        return False
    updated = dict(committed)
    del updated[key]
    write_transition_edits(project_dir, TransitionEdits.from_edits(updated))
    return True


def read_map_transitions(image: bytes, profile: RomProfile) -> MapTransitions:
    """Resolve a transition corpus from an in-memory image and its profile.

    The bytes seam `load_map_transitions` uses once identification is done, exposed
    so a caller that already holds the canonical image - the project build and its
    validation step - does not re-open and re-hash an 8 MiB file per domain. The
    profile is the authority for where the map table is, exactly as it is on the
    file path; the image is not checked against it here, because
    `apply_plan`/`identify_rom` already own that, and duplicating it would mean two
    identity rules that could disagree.

    A profile that declares no map-entry table has no transition corpus to read,
    and that is refused by name rather than answered with an empty corpus.
    """
    if not capability.declared(profile, capability.Capability.MAP_ENTRIES):
        raise TransitionProfileError(
            f"profile {profile.id!r} does not declare map_entries; map transition "
            "access is unavailable for this ROM"
        )
    table_profile = profile.map_entries
    assert table_profile is not None
    table_offset, _ = me.resolve_map_entry_table_range(table_profile, len(image))
    return _read_corpus(
        image,
        table_offset=table_offset,
        table_count=table_profile.count,
        profile_id=profile.id,
        base_sha256=profile.identity.sha256,
        profile=profile,
    )


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

    return read_map_transitions(image, profile)


__all__ = [
    "ARRAY_ELEMENT_WIDTH",
    "CREATION_ARRAY_PREFIX",
    "CREATION_DOMAIN",
    "CREATION_RECORD_PREFIX",
    "CREATED_CLASS_RAW",
    "MAP_ENTRY_SOURCE_OFFSET",
    "MAX_TRANSITION_COUNT",
    "ROOT_ARRAY_OFFSET",
    "ROOT_COUNT_OFFSET",
    "SUPPORTED_CLASS_RAW",
    "TRANSITION_SIZE",
    "AuthoredTransitionCreation",
    "AuthoredTransitionEdit",
    "CreatedTransitionIdentity",
    "MapTransitionError",
    "MapTransitions",
    "MapTransitionsError",
    "TransitionApplication",
    "TransitionCreation",
    "TransitionCreationMaterialization",
    "TransitionCreationPlan",
    "TransitionEdit",
    "TransitionEntry",
    "TransitionFieldError",
    "TransitionIdentity",
    "TransitionProfileError",
    "TransitionRegion",
    "TransitionRoot",
    "UnknownTransitionError",
    "created_record_fields",
    "load_map_transitions",
    "materialize_transition_creations",
    "plan_transition_edits",
    "read_map_transitions",
    "read_project_transition_creations",
    "read_project_transition_requests",
    "read_transition_creations",
    "read_transition_edits",
    "remove_transition_creation",
    "remove_transition_edit",
    "set_transition_creations",
    "set_transition_edits",
    "transition_creations_to_requests",
    "transition_edits_to_requests",
]
