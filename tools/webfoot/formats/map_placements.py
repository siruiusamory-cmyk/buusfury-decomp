"""Factory-led 32-byte map placement records: bytes first, coordinates second.

TOOLKIT-008. This module carries the record family reached from a `MapEntry`'s
`+0x14` pointer, and it exists because the corpus measurement contradicted the
ticket's starting assumption.

**OLD CLAIM.** `MapEntry` declares `item_count`/`items_pointer` (`+0x06`/`+0x18`),
`object_count`/`objects_pointer` (`+0x07`/`+0x1C`) and `npc_count`/`npcs_pointer`
(`+0x08`/`+0x20`). Those upstream names suggested the entity-placement corpus
lived behind them.

**NEW EVIDENCE.** Measured across all 452 records of the canonical image, the
declared families are nearly empty:

    items     4 entries with a positive count and a live pointer
    objects   0 entries
    npcs     14 entries, against 406 carrying a count with a NULL pointer

The names originate from `spicybung/DragonByteZ` and carry `INFERRED` semantics
only; `docs/reverse-engineering.md` records that no consumer in the pinned
disassembly loads any of the nine pointer words. A far larger family is reached
through a different field: 1,571 four-aligned words in the image equal the
factory raw `0x0800FD55`, and 1,403 of those begin a 32-byte record whose last
three words are the constants `{0x080555A0, 0x00000001, 0x080716EC}`.

**RESOLUTION.** This module decodes that factory-led family. It does NOT rename
it: nothing here calls a record an NPC, an object or an item, because no
evidence in this project establishes which of those - if any - it is. The
upstream-labelled fields keep their names and their `INFERRED` status elsewhere,
unchanged and undeleted.

**Ownership.** Walking every `MapEntry`'s `+0x14` pointer while each successive
word points at a well-formed record reaches **1,295 records across 215 maps**,
with **no record claimed by two maps** and **no two pointer arrays overlapping
each other**. 108 well-formed records exist in the image that no map reaches;
they are left out rather than forced into a map's extent.

**UNRESOLVED, and it blocks a build.** Those record extents collide with the
slot extents `webfoot.formats.map_slots` resolves: **57 records overlap 40 slot
arrays**, so `plan_changes` refuses the merged plan with `OverlappingChangeError`
rather than letting two owners write the same bytes. That refusal is correct.
Which extent is wrong is NOT yet determined - the slot extent rests on
`trigger_count_raw`, recorded UNKNOWN in `docs/research/MAP_FORMAT.md`, and this
walk rests only on record shape. Until that is measured, this family does not
reach ROUND_TRIP and no placement edit can be built.

**The declared count does not bound the array.** `script_count_raw` (`+0x05`)
matches the reachable array length for only 2 of those 215 maps; 212 declare a
*smaller* count - usually zero - and 1 declares a larger one. So the extent is
resolved by walking, exactly as `webfoot.formats.map_slots` refuses to trust
`+0x04`. What `+0x05` counts is UNKNOWN and was not investigated here.

**Record layout**, measured over the 1,295 reachable records:

    +0x00  factory_raw     always 0x0800FD55 (the family's defining constant)
    +0x04  flags_raw       33 distinct values
    +0x08  type_raw        1..149, 111 distinct, high halfword always 0
    +0x0C  position_raw    low halfword 0..1982, high halfword 0..930
    +0x10  id_raw          5..306, high halfword always 0
    +0x14  0x080555A0      constant across every reachable record
    +0x18  0x00000001      constant
    +0x1C  0x080716EC      constant

**`position_raw` is carried as one opaque word.** Its packing matches the one
CONFIRMED bounds structure in this project - `0x080755C0 +0x08` decodes as
`(481, 121, 615, 271)` with the low halfword holding X - and within a map the
low halfword's spread exceeds the high halfword's in 130 maps against 52. That
is consistent with an `(x, y)` pair and is NOT proof of one: 52 maps run the
other way, and no consumer of this word has been traced. Callers get the raw
word and the two halfwords under neutral names. Nothing here promotes either
halfword to a coordinate.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct


#: One record is eight little-endian 32-bit words. CONFIRMED as a stride: 1,156
#: of the 1,571 factory occurrences sit exactly 32 bytes from the next one.
PLACEMENT_SIZE = 32

_PLACEMENT_STRUCT = struct.Struct("<8I")

#: GBA cartridge window. A pointer is a reference only when it lands inside the
#: image actually being read, which is checked against that image's real size.
ROM_BASE = 0x08000000

#: The raw word every record in this family begins with. CONFIRMED as a factory
#: raw value by `docs/research/AUTO_RE_<local-state-name>`, which records the sibling
#: factories `0x08007675` and `0x080072CD` from runtime evidence. Being odd, it
#: is Thumb-shaped, as a factory pointer must be. What the factory *constructs*
#: is not established here.
FACTORY_RAW = 0x0800FD55

#: The three trailing words, identical in every one of the 1,403 well-formed
#: records. They are what makes the family recognisable without guessing at a
#: length, so they are matched exactly rather than treated as a heuristic.
#:
#: This is a measured invariant of the canonical image, NOT a semantic claim: no
#: evidence in this project establishes what any of the three words mean.
RECORD_TAIL = (0x080555A0, 0x00000001, 0x080716EC)


class MapPlacementError(ValueError):
    """Base error for placement-record decoding."""


class MapPlacementLengthError(MapPlacementError):
    """Raised when a record is not exactly `PLACEMENT_SIZE` bytes."""


class MapPlacementValueError(MapPlacementError):
    """Raised when a field cannot fit its original binary width."""


class MapPlacementShapeError(MapPlacementError):
    """Raised when bytes do not carry this family's factory word or tail."""


@dataclass(frozen=True, slots=True)
class PlacementRecord:
    """All eight words of one record, without dereferencing any of them.

    Every field keeps a `_raw` suffix for the same reason `MapEntry` does: the
    binary width and position are CONFIRMED, and the meaning is not.
    """

    factory_raw: int
    flags_raw: int
    type_raw: int
    position_raw: int
    id_raw: int
    tail0_raw: int
    tail1_raw: int
    tail2_raw: int

    @classmethod
    def from_bytes(cls, data: bytes | bytearray | memoryview) -> "PlacementRecord":
        if len(data) != PLACEMENT_SIZE:
            raise MapPlacementLengthError(
                f"placement record must be exactly {PLACEMENT_SIZE} bytes; "
                f"got {len(data)}"
            )
        return cls(*_PLACEMENT_STRUCT.unpack(data))

    def to_bytes(self) -> bytes:
        values = (
            self.factory_raw,
            self.flags_raw,
            self.type_raw,
            self.position_raw,
            self.id_raw,
            self.tail0_raw,
            self.tail1_raw,
            self.tail2_raw,
        )
        for value in values:
            if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
                raise MapPlacementValueError(
                    "every placement word must be an unsigned 32-bit integer"
                )
        encoded = _PLACEMENT_STRUCT.pack(*values)
        if len(encoded) != PLACEMENT_SIZE:
            raise AssertionError("internal placement serializer size mismatch")
        return encoded

    @property
    def position_low(self) -> int:
        """Low halfword of `position_raw`.

        Named by POSITION IN THE WORD, not by axis. The packing matches the one
        CONFIRMED bounds structure, where the low halfword holds X, but that
        correspondence is not established for this family and is not asserted
        here.
        """
        return self.position_raw & 0xFFFF

    @property
    def position_high(self) -> int:
        """High halfword of `position_raw`. See `position_low` on naming."""
        return (self.position_raw >> 16) & 0xFFFF

    def with_position(self, low: int, high: int) -> "PlacementRecord":
        """This record with `position_raw` repacked from two halfwords.

        Both halves are range-checked here rather than at encode time, so an
        out-of-range edit is refused before it can silently wrap into the
        neighbouring halfword.
        """
        for name, value in (("low", low), ("high", high)):
            if type(value) is not int or not 0 <= value <= 0xFFFF:
                raise MapPlacementValueError(
                    f"position {name} halfword must be an unsigned 16-bit integer"
                )
        return PlacementRecord(
            factory_raw=self.factory_raw,
            flags_raw=self.flags_raw,
            type_raw=self.type_raw,
            position_raw=(high << 16) | low,
            id_raw=self.id_raw,
            tail0_raw=self.tail0_raw,
            tail1_raw=self.tail1_raw,
            tail2_raw=self.tail2_raw,
        )


def is_placement_record(data: bytes | bytearray | memoryview, offset: int) -> bool:
    """Whether `PLACEMENT_SIZE` bytes at `offset` carry this family's shape.

    Both the leading factory word and all three trailing constants must match.
    Requiring the tail as well as the head is what keeps the walk in
    `iter_placement_offsets` from running off the end of an array into
    unrelated data that merely happens to start with the factory word.
    """
    if offset < 0 or offset + PLACEMENT_SIZE > len(data):
        return False
    words = _PLACEMENT_STRUCT.unpack_from(data, offset)
    return words[0] == FACTORY_RAW and words[5:] == RECORD_TAIL


def read_placement_record(
    data: bytes | bytearray | memoryview,
    offset: int,
) -> PlacementRecord:
    """Decode one record, refusing bytes that are not this family's shape."""
    if not is_placement_record(data, offset):
        raise MapPlacementShapeError(
            f"no factory-led placement record at file offset 0x{offset:06X}"
        )
    return PlacementRecord.from_bytes(data[offset : offset + PLACEMENT_SIZE])


def iter_placement_offsets(
    data: bytes | bytearray | memoryview,
    array_offset: int,
) -> tuple[int, ...]:
    """File offsets of the records an array at `array_offset` points at.

    The array is walked one word at a time and stops at the first word that is
    not a cartridge address reaching a well-formed record. That termination
    rule - rather than the declared `script_count_raw` - is what bounds the
    extent, because the declared count matches the walk for only 2 of the 215
    maps that reach any record at all.

    **This termination rule is NOT established as sufficient.** Walking it over
    the canonical image produces record extents that collide with 40 of the slot
    arrays `webfoot.formats.map_slots` resolves, across 57 records. One of the
    two extents runs long and this project has not determined which: the slot
    extent is bounded by `trigger_count_raw`, whose meaning
    `docs/research/MAP_FORMAT.md` records as UNKNOWN, while this walk is bounded
    only by record shape. Until measurement settles it, the tail of a walked
    array is unverified rather than a proven extent.
    """
    if array_offset < 0 or array_offset + 4 > len(data):
        return ()
    offsets: list[int] = []
    cursor = array_offset
    while cursor + 4 <= len(data):
        (word,) = struct.unpack_from("<I", data, cursor)
        if not ROM_BASE <= word < ROM_BASE + len(data):
            break
        target = word - ROM_BASE
        if not is_placement_record(data, target):
            break
        offsets.append(target)
        cursor += 4
    return tuple(offsets)
