"""Attach one new actor to a map's engine-owned object array.

SPRITE-NEW-ATTACHMENT-CORE-001.

**What this module owns.** One authoring act: a map that already owns an
engine-counted object array gains ONE more object, appended. Every existing slot
pointer is carried verbatim into a re-emitted array above canonical EOF, the
MapEntry byte the engine reads as that array's bound is incremented, the one
field that named the old array is repointed, and the new object record is
created with the sprite id, position, retained data pointer and behaviour entry
the caller supplies.

**What it deliberately does not own.** It authors no sprite identity (that is
:mod:`webfoot.sprite_identity`, which this planner composes with rather than
duplicates), no graphics, no palette, no dialogue and no script. It offers no
command-line or user-interface surface, it does not choose a wander box, and it
does not model the per-actor frame-composition budget - an actor that draws
larger frames than the engine's buffer for it is the case this planner does not
see. It only appends: it never removes, reorders or rewrites an existing object.

**The one supported record family.** The map-102 sibling family the runtime work
proved: a ``0x1C``-byte object header led by factory ``0x08017DA3``, with a
``0x10``-byte behaviour entry at ``+0x1C``. A retail record does not dispatch the
entry stored at its own ``+0x1C``: of the image's 191 sibling slots, none names
its own entry, 81 name the entry 1C into the record the previous array slot
points at, and 67 name one shared address. What the runtime proved instead is the
self-named shape this planner authors - the record's ``+0x18`` names the entry
written at its own ``+0x1C``, which is the wiring
``docs/research/SPRITE_NEW_BEHAVIOR_REGISTRATION.md`` measured when a clone that
inherited a donor's word dispatched the donor's behaviour and the same clone
pointed at its own entry moved. The entry's body is carried from the caller; its
wander box - four map-pixel halfwords at entry ``+0x08``, the bounds the class-A
walk method tests - is authored explicitly. Anything else is refused rather than
approximated: the other sibling factory ``0x080111A9`` (whose dispatcher reads
its entry at a different offset, ``SPRITE_NEW_BEHAVIOR_REGISTRATION.md`` section
on per-family offsets), the ``0x0800FD55`` placement family, and any array that
mixes families.

**Addressability.** Both spans are ``EXPANDED_ONLY`` by policy. The array is new
content with nowhere canonical to grow - the bytes that follow it are live - and
the shared canonical free window is one 256-byte region other domains draw on.
Placing both above canonical EOF is also the addressability the runtime evidence
covers: the composed image the retail engine followed had its relocated array and
its new object record there.

**What is reused.** :func:`allocation.allocate` places both spans under the
addressability policy, :class:`formats.map_entry.MapEntry` supplies every
MapEntry field offset, :func:`formats.map_placements.iter_object_slots` performs
the engine's own counted walk and family classification, and the write layer
authorizes the appended bytes through
:meth:`allocation.Allocation.generated_allocation_provenance`. No second
allocator, no second writer, no second map-array walker.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

from . import capability
from .allocation import (Addressability, Allocation, AllocationKind,
                         AllocationRequest, allocate)
from .binary import (GBA_ROM_BASE, BinaryAddressError, FileOffset,
                     GbaRomAddress)
from .formats import map_entry as me
from .formats import map_placements as mp
from .layout import (AnchorId, OwnedRegion, Provenance, Reference,
                     ReferenceClass, ReferenceEncoding, RomRange)
from .write import (ByteChange, GeneratedAllocationProvenance, ReferenceRewrite,
                    RelocationProvenance)


class SpriteAttachmentError(ValueError):
    """An attachment this write path will not author without guessing."""


class SpriteAttachmentProfileError(SpriteAttachmentError, capability.CapabilityError):
    """The ROM/profile is not authorized for the map-entry access this needs."""


#: The write-owner prefix of the re-emitted object array and the new record. A
#: resolved owner appends the map index, so a build that attaches several actors
#: carries one distinguishable owner per edit rather than one shared string.
ARRAY_OWNER = "sprite_attachment:object-array"
RECORD_OWNER = "sprite_attachment:object-record"

#: The one domain string this module's allocation provenance is recorded under.
DOMAIN = "sprite_attachment"

#: Both spans are read as little-endian words by the engine.
ALIGNMENT = 4

#: The engine reads the object-array bound from ``MapEntry+0x04`` with ``ldrb``,
#: so the largest array it can count is 255 slots.
MAX_OBJECT_COUNT = 0xFF

#: The dispatcher reads the object's own state block as
#: ``{[+0x00] count, [+0x04..] entry pointer}``, and this planner writes exactly
#: one entry, so the count word is one.
SINGLE_ENTRY_TABLE_COUNT = 1

#: The logical anchor this planner repoints: the object array, named by the
#: MapEntry field the engine's object loop reads.
ARRAY_ANCHOR = "map:{index:04d}/placement_references"

#: The name of the one record family this planner writes, which is what a caller
#: passes as :attr:`NewMapActor.family`.
FAMILY_MAP_SIBLING = "map-sibling-08017da3"

#: The sibling corpus uses sprite ids from 1 through 305, so an id is only
#: refused when it could not be one at all.
MIN_SPRITE_ID = 1
MAX_SPRITE_ID = 0xFFFFFFFF

#: How a family's wander-box value is written, keyed by its measured width.
_BOX_FORMATS = {1: "<B", 2: "<H", 4: "<I"}


@dataclass(frozen=True, slots=True)
class WanderBox:
    """The four map-pixel bounds the class-A walk method accepts a step inside.

    The box is ``(x1, y1, x2, y2)``. The engine accepts a step only while the
    actor's own rectangle, translated by that step, stays inside it: ``x1`` and
    ``y1`` are lower bounds and ``x2`` and ``y2`` upper bounds. A box that does
    not contain the actor's authored position therefore declines every step,
    which is measured behaviour rather than an error - which is why this planner
    neither chooses a box nor checks one against the position.
    """

    x1: int
    y1: int
    x2: int
    y2: int

    def __post_init__(self) -> None:
        for name in ("x1", "y1", "x2", "y2"):
            value = getattr(self, name)
            if type(value) is not int or not 0 <= value <= 0xFFFF:
                raise SpriteAttachmentError(
                    f"wander-box {name} must be an unsigned 16-bit map pixel")
        if self.x1 > self.x2 or self.y1 > self.y2:
            raise SpriteAttachmentError(
                f"wander box ({self.x1}, {self.y1})-({self.x2}, {self.y2}) is "
                "inverted; every step would be declined")

    def as_halfwords(self) -> tuple[int, int, int, int]:
        return (self.x1, self.y1, self.x2, self.y2)

    def to_json(self) -> dict:
        return {"x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2}


@dataclass(frozen=True, slots=True)
class SupportedActorFamily:
    """One object-record family whose layout has been measured end to end.

    Every offset here is a measured byte displacement, and the entry offsets are
    relative to the behaviour entry the record's ``+0x18`` names. A family states
    only what this planner writes or a caller must be able to read back; a field
    whose meaning is unresolved is carried as a verbatim word by the caller.
    """

    name: str
    factory_offset: int
    factory_raw: int
    retained_04_offset: int
    position_offset: int
    data_pointer_offset: int
    sprite_id_offset: int
    table_count_offset: int
    table_entry_offset: int
    header_size: int
    entry_inline_offset: int
    entry_size: int
    entry_class_raw: int
    entry_class_offset: int
    box_offset: int
    box_value_width: int
    evidence: str

    def __post_init__(self) -> None:
        for name in ("factory_offset", "retained_04_offset", "position_offset",
                     "data_pointer_offset", "sprite_id_offset",
                     "table_count_offset", "table_entry_offset"):
            offset = getattr(self, name)
            if type(offset) is not int or not 0 <= offset <= self.header_size - 4:
                raise SpriteAttachmentError(
                    f"{self.name}: {name} is not a word inside the "
                    f"{self.header_size:#x}-byte object header")
        if self.entry_inline_offset != self.header_size:
            raise SpriteAttachmentError(
                f"{self.name}: the behaviour entry follows the header, so its "
                f"offset must be {self.header_size:#x}")
        if self.entry_class_offset != 0:
            raise SpriteAttachmentError(
                f"{self.name}: the entry's first word selects its handler")
        if self.box_value_width not in (1, 2, 4):
            raise SpriteAttachmentError(
                f"{self.name}: a wander-box value is one, two or four bytes")
        if not 0 <= self.box_offset <= self.entry_size - 4 * self.box_value_width:
            raise SpriteAttachmentError(
                f"{self.name}: the wander box does not fit the behaviour entry")

    @property
    def record_size(self) -> int:
        """The object record as this planner writes it: header plus entry."""
        return self.header_size + self.entry_size


#: Every object family this planner will write. One member is deliberate: a
#: second family may only be added with its own measured entry offset and its own
#: evidence, which is exactly the check that keeps an unmodelled family out.
SUPPORTED_FAMILIES: dict[str, SupportedActorFamily] = {
    FAMILY_MAP_SIBLING: SupportedActorFamily(
        name=FAMILY_MAP_SIBLING,
        factory_offset=0x00,
        factory_raw=0x08017DA3,
        retained_04_offset=0x04,
        position_offset=0x08,
        data_pointer_offset=0x0C,
        sprite_id_offset=0x10,
        table_count_offset=0x14,
        table_entry_offset=0x18,
        header_size=0x1C,
        entry_inline_offset=0x1C,
        entry_size=0x10,
        entry_class_raw=0x0800A7A1,
        entry_class_offset=0x00,
        box_offset=0x08,
        box_value_width=2,
        evidence=(
            "the map-102 sibling run: ten 0x08017DA3 records from 0x0807831C, "
            "factory and +0x14 = 1 on all ten, and the bytes at +0x1C a 0x10-byte "
            "0x0800A7A1 behaviour entry whose +0x08 halfwords are the bounds the "
            "class-A walk method compares against. Retail dispatch differs: across "
            "the image's 191 sibling slots none names its own +0x1C, and the "
            "self-named record is the shape the controlled-actor runtime runs"),
    ),
}


def supported_family(name: str) -> SupportedActorFamily:
    """The measured layout for *name*, or a refusal naming what is supported."""
    try:
        return SUPPORTED_FAMILIES[name]
    except (KeyError, TypeError):
        raise SpriteAttachmentError(
            f"{name!r} is not a supported object-record family; this planner "
            f"writes only {', '.join(sorted(SUPPORTED_FAMILIES))}") from None


@dataclass(frozen=True, slots=True)
class NewMapActor:
    """One actor to append, with every unproven field supplied explicitly.

    The fields fall into two groups. Authored: the sprite id the actor resolves,
    its map position, and the wander box its behaviour entry carries. Retained:
    the object header's ``+0x04`` word and its ``+0x0C`` data pointer, both of
    which are measured and neither of which this SDK interprets - ``+0x04`` holds
    0 on 82 of the 191 canonical sibling slots and a pointer or a small value on
    the rest, and ``+0x0C`` is not movement data (the walk method never reads it).
    They are required rather than defaulted so a caller states what it is
    carrying instead of this planner inventing a value.
    """

    map_index: int
    family: str
    sprite_id: int
    position: tuple[int, int]
    retained_04_raw: int
    data_pointer_raw: int
    behaviour_entry: bytes
    wander_box: WanderBox


@dataclass(frozen=True, slots=True)
class AuthoredMapActor:
    """What the planner laid out: the addresses every part of it now has."""

    map_index: int
    family: str
    sprite_id: int
    position: tuple[int, int]
    retained_04_raw: int
    data_pointer_raw: int
    wander_box: WanderBox
    entry_class_raw: int
    entry_size: int
    array_old_range: RomRange
    array_old_rom_address: int
    array_range: RomRange
    array_rom_address: int
    array_slots: int
    record_range: RomRange
    record_rom_address: int
    behaviour_entry_address: int

    def to_json(self) -> dict:
        return {
            "map_index": self.map_index,
            "family": self.family,
            "sprite_id": self.sprite_id,
            "position": list(self.position),
            "retained_04_raw": self.retained_04_raw,
            "retained_04_hex": f"0x{self.retained_04_raw:08X}",
            "data_pointer_raw": self.data_pointer_raw,
            "data_pointer_hex": f"0x{self.data_pointer_raw:08X}",
            "wander_box": self.wander_box.to_json(),
            "behaviour_entry_class": f"0x{self.entry_class_raw:08X}",
            "behaviour_entry_size": self.entry_size,
            "behaviour_entry_address": self.behaviour_entry_address,
            "behaviour_entry_address_hex": f"0x{self.behaviour_entry_address:08X}",
            "array_old_range": self.array_old_range.to_json(),
            "array_old_rom_address": f"0x{self.array_old_rom_address:08X}",
            "array_range": self.array_range.to_json(),
            "array_rom_address": f"0x{self.array_rom_address:08X}",
            "array_slots": self.array_slots,
            "record_range": self.record_range.to_json(),
            "record_rom_address": f"0x{self.record_rom_address:08X}",
        }


@dataclass(frozen=True, slots=True)
class ActorAttachment:
    """Everything this domain contributes to the one merged build plan.

    The four plan fields are the shape every authoring domain returns, so a
    caller threads them into :func:`write.plan_changes` unchanged. ``actor`` is
    this domain's own description of what it laid out.
    """

    actor: AuthoredMapActor
    changes: tuple[ByteChange, ...] = ()
    reserved: tuple[OwnedRegion, ...] = ()
    generated_allocations: tuple[GeneratedAllocationProvenance, ...] = ()
    relocations: tuple[RelocationProvenance, ...] = ()


def plan_new_map_actor(
    image: bytes,
    identification,
    request: NewMapActor,
    *,
    profile=None,
    reserved: tuple[OwnedRegion, ...] = (),
) -> ActorAttachment:
    """Compile one appended map actor into attributed changes. Pure.

    The map's existing object records are never written: the array is re-emitted
    elsewhere with every existing slot carried byte for byte, and the only
    canonical bytes this plan changes are the array's bound byte and the field
    that named the array. Nothing is retired - the old array's bytes stay where
    they were - and the new object record lives entirely above canonical EOF.

    ``profile`` is the collaborator a caller holding a decoded corpus already
    has; when it is omitted, the profile is established from ``identification``
    through the map-entry capability gate, so a ROM this SDK has not verified
    cannot be written through this path.

    ``reserved`` is the build-scoped reservation set every allocating domain
    shares; the two spans this domain places are returned for the domains after
    it.
    """
    if not isinstance(request, NewMapActor):
        raise SpriteAttachmentError(
            f"planning needs a NewMapActor, not {type(request).__name__}")
    family = supported_family(request.family)
    profile = _resolve_profile(image, profile, identification)
    _require_request(image, profile, family, request)
    entry_offset = _map_entry_offset(image, profile, request.map_index)
    entry = me.MapEntry.from_bytes(
        image[entry_offset:entry_offset + me.MAP_ENTRY_SIZE])
    count, array_offset = _object_array(image, entry, request.map_index, family)
    _require_no_other_name(image, entry, entry_offset, count, request.map_index)
    placed = _allocate(profile, request, family, count, reserved)
    return _materialize(image, profile, family, request, entry, entry_offset,
                        count, array_offset, placed)


# --- request validation ------------------------------------------------------


def _resolve_profile(image: bytes, profile, identification):
    """Resolve the profile, and refuse an image its own profile does not describe."""
    if profile is None:
        if identification is None:
            raise SpriteAttachmentError(
                "planning needs either a resolved profile or a verified ROM "
                "identification to resolve one from")
        profile = capability.require(
            identification, capability.Capability.MAP_ENTRIES,
            subsystem="map actor attachment",
            error_type=SpriteAttachmentProfileError, check_header=True)
    if profile.map_entries is None:
        raise SpriteAttachmentError(
            f"profile {profile.id!r} declares no map-entry table, so no map object "
            "array can be named")
    if profile.map_entries.record_size != me.MAP_ENTRY_SIZE:
        raise SpriteAttachmentError(
            f"profile {profile.id!r} declares {profile.map_entries.record_size:#x}"
            f"-byte map records; this planner reads {me.MAP_ENTRY_SIZE:#x}-byte ones")
    if len(image) != profile.size:
        raise SpriteAttachmentError(
            f"the image is {len(image)} bytes but profile {profile.id!r} describes "
            f"{profile.size}; refusing to plan against a different base")
    return profile


def _require_request(image: bytes, profile, family: SupportedActorFamily,
                     request: NewMapActor) -> None:
    if profile.generated_expansion is None:
        raise SpriteAttachmentError(
            "an appended actor lives above canonical EOF, so the profile must "
            "declare a generated expansion")
    if type(request.map_index) is not int or request.map_index < 0:
        raise SpriteAttachmentError("a map index is a non-negative table index")
    if request.map_index >= profile.map_entries.count:
        raise SpriteAttachmentError(
            f"map {request.map_index} is outside the {profile.map_entries.count}-entry "
            "map table this profile declares")
    if (type(request.sprite_id) is not int
            or not MIN_SPRITE_ID <= request.sprite_id <= MAX_SPRITE_ID):
        raise SpriteAttachmentError(
            f"an authored sprite id must be an unsigned 32-bit integer of at least "
            f"{MIN_SPRITE_ID}; got {request.sprite_id!r}")
    if not isinstance(request.position, tuple) or len(request.position) != 2:
        raise SpriteAttachmentError(
            "a position is a (map x, map y) pair of signed 16-bit pixels")
    try:
        mp.encode_position(*request.position)
    except mp.MapPlacementError as exc:
        raise SpriteAttachmentError(f"the position is not authorable: {exc}") from exc
    for name in ("retained_04_raw", "data_pointer_raw"):
        value = getattr(request, name)
        if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
            raise SpriteAttachmentError(
                f"{name} is a retained 32-bit word and must be an unsigned 32-bit "
                f"integer; got {value!r}")
    limit = _window_size(profile)
    if not GBA_ROM_BASE <= request.data_pointer_raw < GBA_ROM_BASE + limit:
        raise SpriteAttachmentError(
            f"the retained data pointer 0x{request.data_pointer_raw:08X} is outside "
            f"the 0x{GBA_ROM_BASE:08X}..0x{GBA_ROM_BASE + limit:08X} window this "
            "build's image occupies")
    if not isinstance(request.behaviour_entry, bytes):
        raise SpriteAttachmentError("a behaviour entry must be immutable bytes")
    if len(request.behaviour_entry) != family.entry_size:
        raise SpriteAttachmentError(
            f"family {family.name} writes a {family.entry_size:#x}-byte behaviour "
            f"entry; got {len(request.behaviour_entry)} bytes")
    class_word = int.from_bytes(
        request.behaviour_entry[family.entry_class_offset:
                                family.entry_class_offset + 4], "little")
    if class_word != family.entry_class_raw:
        raise SpriteAttachmentError(
            f"the behaviour entry's class word is 0x{class_word:08X}; family "
            f"{family.name} dispatches 0x{family.entry_class_raw:08X}")
    if not isinstance(request.wander_box, WanderBox):
        raise SpriteAttachmentError("a wander box must be a WanderBox")
    box_maximum = (1 << (8 * family.box_value_width)) - 1
    if any(value > box_maximum for value in request.wander_box.as_halfwords()):
        raise SpriteAttachmentError(
            f"family {family.name} writes each wander-box value in "
            f"{family.box_value_width} byte(s), so a bound may not exceed "
            f"{box_maximum}")


def _window_size(profile) -> int:
    """The addressable output size, established by ``_require_request``."""
    return profile.generated_expansion.output_size


# --- reading the target map --------------------------------------------------


def _map_field_offset(name: str) -> int:
    """One MapEntry field's byte offset, from the codec that owns the layout."""
    return next(field.offset for field in me.MAP_ENTRY_LAYOUT if field.name == name)


def _file_offset(address: int, image_size: int, what: str) -> int:
    try:
        return GbaRomAddress(address).to_file_offset(image_size)
    except BinaryAddressError as exc:
        raise SpriteAttachmentError(f"{what} 0x{address:08X}: {exc}") from exc


def _map_entry_offset(image: bytes, profile, map_index: int) -> int:
    table = profile.map_entries
    start = _file_offset(table.address.raw, len(image), "the map-entry table")
    at = start + map_index * table.record_size
    if at + me.MAP_ENTRY_SIZE > len(image):
        raise SpriteAttachmentError(
            f"map {map_index}'s record at 0x{at:06X} runs past the image")
    return at


def _object_array(image: bytes, entry: me.MapEntry, map_index: int,
                  family: SupportedActorFamily) -> tuple[int, int]:
    """The bound and file offset of this map's engine-counted object array.

    The bound is ``MapEntry+0x04``, which TOOLKIT-024 proved is the ``ldrb`` of
    the engine's object loop, and the base is ``+0x14``. The walk classifies every
    slot, and one slot of another family refuses the whole plan: the array is
    heterogeneous in principle, and a planner that appended to one holding
    records it does not model would be guessing about the engine's traversal.
    """
    count = entry.trigger_count_raw
    array_word = entry.scripts_pointer_raw
    if count == 0 or array_word == 0:
        raise SpriteAttachmentError(
            f"map {map_index} declares no object array (count {count}, base "
            f"0x{array_word:08X}); growing an array that does not exist is not an "
            "append")
    array_offset = _file_offset(array_word, len(image), "the object array")
    try:
        slots = mp.iter_object_slots(image, array_offset, count)
    except mp.MapPlacementError as exc:
        raise SpriteAttachmentError(
            f"map {map_index}'s object array at 0x{array_word:08X}: {exc}") from exc
    for slot in slots:
        if slot.family_raw != family.factory_raw:
            raise SpriteAttachmentError(
                f"map {map_index} slot {slot.index} holds "
                f"{_family_name(slot.family_raw)}, not the supported family "
                f"0x{family.factory_raw:08X}; this planner writes only "
                f"{family.name}")
    return count, array_offset


def object_array_slots(image: bytes, profile, map_index: int,
                       family: SupportedActorFamily):
    """Every slot of one map's engine-counted object array, or a refusal.

    The reader half of what :func:`plan_new_map_actor` writes: the same map entry,
    the same bound and the same base, refusing an array that holds a family this
    writer does not model. A surface listing the slots an authored actor can start
    from calls this rather than re-deriving those three steps.
    """
    entry_offset = _map_entry_offset(image, profile, map_index)
    entry = me.MapEntry.from_bytes(
        image[entry_offset:entry_offset + me.MAP_ENTRY_SIZE])
    count, array_offset = _object_array(image, entry, map_index, family)
    return mp.iter_object_slots(image, array_offset, count)


def _family_name(family_raw: int | None) -> str:
    if family_raw is None:
        return "a pointer outside the image"
    return f"family 0x{family_raw:08X}"


def _require_no_other_name(image: bytes, entry: me.MapEntry, entry_offset: int,
                           count: int, map_index: int) -> None:
    """The array must be named by this map's own field, and by nothing else.

    A relocation must move every reference to a structure or prove that none
    other exists, and this is the census that decides which. Every address the
    move retires is searched, not only the array's base: a word naming slot *i*
    would be stranded by a re-emitted array just as surely as one naming the base.
    The census is deliberately word-aligned, because the engine's pointers are and
    a byte-aligned coincidence is noise rather than a reference. Anything beyond
    the one MapEntry field is a reference this planner does not model, so it
    refuses instead of guessing which map or structure the engine reads it
    through.
    """
    array_word = entry.scripts_pointer_raw
    base_field = entry_offset + _map_field_offset("scripts_pointer_raw")
    for slot in range(count):
        address = array_word + 4 * slot
        needle = address.to_bytes(4, "little")
        holders = []
        at = image.find(needle)
        while at != -1:
            if at % ALIGNMENT == 0:
                holders.append(at)
            at = image.find(needle, at + 1)
        if slot == 0:
            if tuple(holders) != (base_field,):
                raise SpriteAttachmentError(
                    f"map {map_index}: the object array at 0x{array_word:08X} is "
                    f"named at {_name_offsets(holders)}, not only by the MapEntry "
                    f"field at 0x{base_field:06X}; this planner rewrites that field "
                    "alone and will not leave a reference to the old array behind")
        elif holders:
            raise SpriteAttachmentError(
                f"map {map_index}: slot {slot}'s address 0x{address:08X} is named at "
                f"{_name_offsets(holders)}; a re-emitted array moves that address "
                "too, and this planner does not model a reference into the middle "
                "of the array")


def _name_offsets(offsets: list[int], limit: int = 4) -> str:
    """A bounded list of naming offsets, so a refusal stays readable."""
    shown = ", ".join(f"0x{offset:06X}" for offset in offsets[:limit])
    if len(offsets) > limit:
        return f"{shown} and {len(offsets) - limit} more"
    return shown or "nothing"


# --- allocation and emission -------------------------------------------------


def _owner(prefix: str, map_index: int) -> str:
    """One write owner, resolved for the map it edits."""
    return f"{prefix}:map-{map_index:04d}"


@dataclass(frozen=True, slots=True)
class _Placed:
    """The two allocations and the owners the writes against them carry."""

    array_owner: str
    record_owner: str
    array: Allocation
    record: Allocation


def _allocate(profile, request: NewMapActor, family: SupportedActorFamily,
              count: int, reserved: tuple[OwnedRegion, ...]) -> _Placed:
    """Place the new record and the re-emitted array, both above canonical EOF.

    The array's payload needs the record's address, which is why nothing is
    encoded here. The allocator sorts by anchor identity and takes the lowest
    aligned first fit, so the two addresses are a function of the request pair
    alone and the plan is deterministic.
    """
    if count >= MAX_OBJECT_COUNT:
        raise SpriteAttachmentError(
            f"map {request.map_index} already declares {count} object slots; "
            f"MapEntry+0x04 is one byte and the engine cannot count {count + 1}")
    array_owner = _owner(ARRAY_OWNER, request.map_index)
    record_owner = _owner(RECORD_OWNER, request.map_index)
    requests = (
        AllocationRequest(
            AnchorId(array_owner), array_owner, 4 * (count + 1), ALIGNMENT,
            kind=AllocationKind.PLACEMENT_REFERENCE_ARRAY,
            addressability=Addressability.EXPANDED_ONLY,
            evidence=(
                f"map {request.map_index}'s object array re-emitted one slot "
                "longer so a new actor can be appended; every existing slot pointer "
                "is carried verbatim and the array cannot grow in place because the "
                "bytes that follow it are live")),
        AllocationRequest(
            AnchorId(record_owner), record_owner, family.record_size, ALIGNMENT,
            kind=AllocationKind.MAP_OBJECT_RECORD,
            addressability=Addressability.EXPANDED_ONLY,
            evidence=(
                f"one new {family.name} object record: the actor entity that "
                f"carries sprite id {request.sprite_id}, its inline behaviour entry "
                "and its authored wander box")),
    )
    allocations = allocate(
        profile, requests,
        # The build-scoped set is stated in plain `RomRange` spans, the way
        # `compressed_dialogue` consumes it, so each span is wrapped here rather
        # than assumed to already arrive owned.
        occupied=tuple(span if isinstance(span, OwnedRegion)
                       else OwnedRegion(span, "build reservation")
                       for span in reserved))
    by_owner = {allocation.request.owner: allocation for allocation in allocations}
    for allocation in allocations:
        if not allocation.is_expanded:
            raise SpriteAttachmentError(
                f"{allocation.request.owner} landed inside the canonical image; "
                "both spans of an appended actor are expansion-only")
    if by_owner[array_owner].range.overlaps(by_owner[record_owner].range):
        raise SpriteAttachmentError("the new array and its record overlap")
    return _Placed(array_owner=array_owner, record_owner=record_owner,
                   array=by_owner[array_owner], record=by_owner[record_owner])


def _padding(profile) -> int:
    """The generated image's fill byte, established by ``_require_request``."""
    return profile.generated_expansion.padding_byte


def _encode_record(family: SupportedActorFamily, request: NewMapActor,
                   entry_address: int) -> bytes:
    """The new object record: the family's shape, this actor's own fields."""
    record = bytearray(family.record_size)
    struct.pack_into("<I", record, family.factory_offset, family.factory_raw)
    struct.pack_into("<I", record, family.retained_04_offset, request.retained_04_raw)
    low, high = mp.encode_position(*request.position)
    struct.pack_into("<I", record, family.position_offset, (high << 16) | low)
    struct.pack_into("<I", record, family.data_pointer_offset,
                     request.data_pointer_raw)
    struct.pack_into("<I", record, family.sprite_id_offset, request.sprite_id)
    struct.pack_into("<I", record, family.table_count_offset,
                     SINGLE_ENTRY_TABLE_COUNT)
    struct.pack_into("<I", record, family.table_entry_offset, entry_address)
    entry = bytearray(request.behaviour_entry)
    box_format = _BOX_FORMATS[family.box_value_width]
    for index, value in enumerate(request.wander_box.as_halfwords()):
        struct.pack_into(box_format, entry,
                         family.box_offset + index * family.box_value_width, value)
    record[family.entry_inline_offset:
           family.entry_inline_offset + family.entry_size] = entry
    return bytes(record)


def _materialize(image: bytes, profile, family: SupportedActorFamily,
                 request: NewMapActor, entry: me.MapEntry, entry_offset: int,
                 count: int, array_offset: int, placed: _Placed):
    """Encode both payloads, attribute every write, and describe the result."""
    padding = _padding(profile)
    array_allocation = placed.array
    record_allocation = placed.record
    array_at = array_allocation.range.start.value
    record_at = record_allocation.range.start.value
    entry_address = record_allocation.rom_address + family.entry_inline_offset
    existing = image[array_offset:array_offset + 4 * count]
    if len(existing) != 4 * count:
        raise SpriteAttachmentError("the object array runs past the image")
    array_payload = existing + struct.pack("<I", record_allocation.rom_address)
    record_payload = _encode_record(family, request, entry_address)

    count_field = entry_offset + _map_field_offset("trigger_count_raw")
    array_field = entry_offset + _map_field_offset("scripts_pointer_raw")
    changes = (
        ByteChange(record_at, bytes([padding]) * len(record_payload), record_payload,
                   placed.record_owner,
                   f"map {request.map_index}: the new {family.name} object record "
                   f"carrying sprite id {request.sprite_id}"),
        ByteChange(array_at, bytes([padding]) * len(array_payload), array_payload,
                   placed.array_owner,
                   f"map {request.map_index}'s object array re-emitted with "
                   f"{count + 1} slots, the first {count} verbatim"),
        ByteChange(count_field, image[count_field:count_field + 1],
                   bytes([count + 1]), placed.array_owner,
                   f"map {request.map_index}'s object bound {count} -> {count + 1}, "
                   "the byte the engine's object loop reads"),
        ByteChange(array_field, image[array_field:array_field + 4],
                   array_allocation.rom_address.to_bytes(4, "little"),
                   placed.array_owner,
                   f"map {request.map_index}: the field that named the object array "
                   f"now names the {count + 1}-slot array"),
    )
    anchor = ARRAY_ANCHOR.format(index=request.map_index)
    reference = Reference(
        source=FileOffset(array_field),
        target=AnchorId(anchor),
        target_delta=0,
        encoding=ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
        classification=ReferenceClass.CONFIRMED_REFERENCE,
        provenance=Provenance(profile.id, profile.sha256,
                              "the MapEntry field the engine's object loop reads"),
    )
    old_range = RomRange(FileOffset(array_offset), 4 * count)
    relocation = RelocationProvenance(
        anchor=anchor, owner=placed.array_owner, old_range=old_range,
        new_range=array_allocation.range, alignment=ALIGNMENT,
        free_region_evidence=array_allocation.free_region_evidence,
        references=(ReferenceRewrite(
            reference=reference, new_source_file_offset=array_field,
            old_target_file_offset=array_offset,
            new_target_file_offset=array_at),),
    )
    generated = (
        array_allocation.generated_allocation_provenance(
            domain=DOMAIN, resource=placed.array_owner, pointer_offset=array_field,
            source_range=old_range),
        record_allocation.generated_allocation_provenance(
            domain=DOMAIN, resource=placed.record_owner,
            pointer_offset=array_at + 4 * count,
            source_range=RomRange(FileOffset(array_at + 4 * count), 4)),
    )
    actor = AuthoredMapActor(
        map_index=request.map_index, family=family.name,
        sprite_id=request.sprite_id, position=request.position,
        retained_04_raw=request.retained_04_raw,
        data_pointer_raw=request.data_pointer_raw,
        wander_box=request.wander_box, entry_class_raw=family.entry_class_raw,
        entry_size=family.entry_size, array_old_range=old_range,
        array_old_rom_address=entry.scripts_pointer_raw,
        array_range=array_allocation.range,
        array_rom_address=array_allocation.rom_address, array_slots=count + 1,
        record_range=record_allocation.range,
        record_rom_address=record_allocation.rom_address,
        behaviour_entry_address=entry_address,
    )
    return ActorAttachment(
        actor=actor, changes=changes,
        reserved=(OwnedRegion(array_allocation.range, placed.array_owner),
                  OwnedRegion(record_allocation.range, placed.record_owner)),
        generated_allocations=generated, relocations=(relocation,))
