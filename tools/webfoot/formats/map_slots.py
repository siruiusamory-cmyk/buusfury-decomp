"""Map-linked 8-byte slot arrays: lossless bytes first, typed decode second.

TOOLKIT-007. A `MapEntry` at `+0x10` carries a pointer and at `+0x04` a byte.
Prior research (`docs/research/AUTO_RE_<local-state-name>:314`) established, from a static
decode of one entry, that the pointer reaches 8-byte records and that the byte
counts them. Measured across the whole 452-record corpus that reading does not
generalise, and this module is shaped by exactly what the measurement showed:

    136 entries   count 0, pointer NULL          nothing to carry
     69 entries   count 0, pointer non-NULL      pointer with no declared extent
    163 entries   count > 0, pointer NULL        count with no array to count
    153 entries   count > 0, pointer in ROM      a bounded, readable extent

No entry points outside the ROM window, and no two arrays share a start. Of the
153 readable extents, every declared count fits inside the gap to the next array
- 152 of 152 gaps are short, none overruns - so the declared extent is safe to
read even though the arrays do not tile.

One of the 153 is refused a second time, by `webfoot.maps`: MapEntry 451's
declared extent covers the start of the MapEntry table that indexes it, so its
count cannot be describing slots.

**TOOLKIT-008 refused 40 more, by the same test, leaving 112.** Those 40
declared extents cover bytes belonging to factory-led placement records
(`webfoot.formats.map_placements`) - 57 records in total - and the placement
reading is the better-witnessed one: **33 of the 40** have their first record
starting at byte 4 mod 8, *mid slot*, so those bytes cannot be whole 8-byte
slots at all. MapEntry 146 declares 12 slots whose extent walks through three
complete records, with the factory word landing in `slots[2]` and one record's
constant tail split across `slots[5]` and `slots[6]`. The corrected corpus is
**112 arrays**. `docs/research/ENTITY_FORMAT.md` carries the measurement.

**Two rungs, deliberately separate.** The broad corpus is carried as opaque
8-byte slots: all 596 of them, 4,768 bytes, reproduced verbatim. Only 35 of the
112 arrays have every slot shaped like the one confirmed example, and only those
get typed `{type_raw, source_ref}` decoding. Calling all 596 slots "triggers"
would promote a single-entry static finding to a corpus-wide fact the bytes
contradict, so this module does not name them that.

The typed rung is **unchanged** by the TOOLKIT-008 correction at 35 arrays / 89
slots: every refused extent was opaque.

**What the confirmed example proves.** MapEntry 39 slot[1] is
`{0x00020006, 0x080755C0}`, and the halfwords at that source `+0x08` are
`(481, 121, 615, 271)` - the bounds `AUTO_RE_STATE` records. That reproduces
here exactly. It also shows why 39 is *not* in the typed 35: its declared count
of 11 runs past its four well-formed slots into data of another shape, so the
array as declared is not uniform. The example is real; the generalisation was
not.

Source structures behind `source_ref` are READ only. The typed arrays reference
89 distinct targets and no evidence in this project establishes the layout of
any of them - the single verified structure is reached from MapEntry 39, whose
array is opaque, so it is not among the 89. This module therefore exposes the
reference and refuses to interpret what it points at.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import struct

from ..binary import GBA_ROM_BASE as ROM_BASE


#: One slot is two little-endian 32-bit words. CONFIRMED as a stride by the
#: static decode; nothing here depends on what the words mean.
SLOT_SIZE = 8

_SLOT_STRUCT = struct.Struct("<II")

#: GBA cartridge window. A slot's second word is only a reference when it lands
#: inside the image actually being read, which is checked against its real size.
#: `ROM_BASE` is an alias of the sanctioned `binary.GBA_ROM_BASE`, not a second
#: literal, so address-window semantics have one owner.

#: An explicit classifier HEURISTIC, and nothing more. Upper bound on a typed
#: slot's `type_raw` high halfword: every slot in the confirmed MapEntry 39
#: example is `0x0002000X`, and this accepts a wider low range so the classifier
#: describes a shape rather than memorising one entry.
#:
#: The threshold is HAND-PICKED, NOT measured from ROM semantics. Nothing in this
#: project establishes what the high halfword means or where its real boundary
#: lies. It is NOT `CONFIRMED`, carries no semantic status, must not be promoted
#: to either, and no claim about the ROM may rest on it.
#:
#: It is acceptable only because corpus classification is INVARIANT across the
#: tested `0x0003`-`0x0100` range: every limit in that range yields the identical
#: corpus of 35 arrays / 89 slots. Only dropping the constraint entirely moves it
#: (to 40 / 112), so the reported corpus is a property of the ROM's data rather
#: than of this number. `test_the_typed_corpus_is_insensitive_to_the_threshold`
#: guards that invariant.
#:
#: If that invariant ever fails, the classifier requires NEW EVIDENCE rather than
#: threshold tweaking - retuning this number to restore a preferred corpus size
#: would be fitting the constant to a desired answer.
_TYPED_HIGH_HALFWORD_LIMIT = 0x0010


class MapSlotError(ValueError):
    """Base error for slot-array decoding."""


class MapSlotLengthError(MapSlotError):
    """Raised when slot bytes are not a whole number of 8-byte slots."""


class MapSlotValueError(MapSlotError):
    """Raised when a slot word cannot fit its 32-bit width."""


class ArrayShape(str, Enum):
    """How much of a slot array this toolkit can honestly describe.

    `TYPED` means every slot matched the confirmed shape and the array may be
    presented as `{type_raw, source_ref}` pairs. `OPAQUE` means the bytes are
    carried exactly and nothing is claimed about their fields. There is no
    third value: an array is either wholly describable or it is bytes.
    """

    TYPED = "TYPED"
    OPAQUE = "OPAQUE"


@dataclass(frozen=True, slots=True)
class MapSlot:
    """One 8-byte slot, as two raw words.

    Both words are kept raw. `word0`/`word1` are positional names, not semantic
    ones, because for 77 of the 112 supported arrays this project cannot say
    what either word is. `MapSlotArray.shape` is what tells a caller whether the
    typed reading applies.
    """

    word0: int
    word1: int

    @classmethod
    def from_bytes(cls, data: bytes | bytearray | memoryview) -> "MapSlot":
        if len(data) != SLOT_SIZE:
            raise MapSlotLengthError(
                f"a slot is exactly {SLOT_SIZE} bytes; got {len(data)}"
            )
        return cls(*_SLOT_STRUCT.unpack(data))

    def to_bytes(self) -> bytes:
        for name, value in (("word0", self.word0), ("word1", self.word1)):
            if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
                raise MapSlotValueError(f"{name} must be an unsigned 32-bit integer")
        return _SLOT_STRUCT.pack(self.word0, self.word1)

    def is_typed(self, image_size: int) -> bool:
        """Whether this slot matches the one confirmed `{type, source}` shape.

        Three conditions, all from the confirmed example and none inferred:
        the second word lands inside the cartridge window, it is 4-aligned as a
        struct pointer must be, and the first word's high halfword is small.
        """
        return (
            ROM_BASE <= self.word1 < ROM_BASE + image_size
            and self.word1 % 4 == 0
            and (self.word0 >> 16) < _TYPED_HIGH_HALFWORD_LIMIT
        )

    @property
    def source_file_offset(self) -> int:
        """This slot's second word as a file offset. Only meaningful when typed.

        Callers reach this through a `TYPED` array; it does not re-check, so
        that a caller cannot get a plausible offset out of an opaque slot by
        asking a different way.
        """
        return self.word1 - ROM_BASE


@dataclass(frozen=True, slots=True)
class MapSlotArray:
    """One MapEntry's declared slot extent, with its shape classification."""

    entry_index: int
    file_offset: int
    slots: tuple[MapSlot, ...]
    original_bytes: bytes
    shape: ArrayShape

    @property
    def slot_count(self) -> int:
        return len(self.slots)

    @property
    def byte_size(self) -> int:
        return len(self.original_bytes)

    def to_bytes(self) -> bytes:
        """Re-encode every slot. Must reproduce `original_bytes` exactly."""
        return b"".join(slot.to_bytes() for slot in self.slots)


def decode_slot_array(
    data: bytes | bytearray | memoryview,
    *,
    entry_index: int,
    file_offset: int,
    image_size: int,
) -> MapSlotArray:
    """Decode one extent into slots and classify its shape. Pure.

    Takes bytes rather than a path so the codec stays usable against a decomp
    tree, matching every other format module here.
    """
    if len(data) == 0 or len(data) % SLOT_SIZE:
        raise MapSlotLengthError(
            f"entry {entry_index}: slot extent must be a positive multiple of "
            f"{SLOT_SIZE} bytes; got {len(data)}"
        )
    blob = bytes(data)
    slots = tuple(
        MapSlot.from_bytes(blob[index : index + SLOT_SIZE])
        for index in range(0, len(blob), SLOT_SIZE)
    )
    shape = (
        ArrayShape.TYPED
        if all(slot.is_typed(image_size) for slot in slots)
        else ArrayShape.OPAQUE
    )
    return MapSlotArray(
        entry_index=entry_index,
        file_offset=file_offset,
        slots=slots,
        original_bytes=blob,
        shape=shape,
    )
