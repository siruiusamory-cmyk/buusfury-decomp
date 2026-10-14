"""Map-linked 8-byte slot arrays: lossless bytes first, typed decode second.

The confirmed example is MapEntry 39 slot[1] `{0x00020006, 0x080755C0}`, whose source `+0x08` halfwords are `(481, 121, 615, 271)`, the bounds AUTO_RE_STATE records.
That example is real; the generalisation is not, because its declared count of 11 runs past its four well-formed slots into data of another shape.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import struct

from ..binary import GBA_ROM_BASE as ROM_BASE


SLOT_SIZE = 8

_SLOT_STRUCT = struct.Struct("<II")


#: example is `0x0002000X`, and this accepts a wider low range so the classifier
_TYPED_HIGH_HALFWORD_LIMIT = 0x0010


class MapSlotError(ValueError):
    """Base error for slot-array decoding."""


class MapSlotLengthError(MapSlotError):
    """Raised when slot bytes are not a whole number of 8-byte slots."""


class MapSlotValueError(MapSlotError):
    """Raised when a slot word cannot fit its 32-bit width."""


class ArrayShape(str, Enum):

    TYPED = "TYPED"
    OPAQUE = "OPAQUE"


@dataclass(frozen=True, slots=True)
class MapSlot:

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
        """Whether this slot matches the one confirmed `{type, source}` shape."""
        return (
            ROM_BASE <= self.word1 < ROM_BASE + image_size
            and self.word1 % 4 == 0
            and (self.word0 >> 16) < _TYPED_HIGH_HALFWORD_LIMIT
        )

    @property
    def source_file_offset(self) -> int:
        """This slot's second word as a file offset. Only meaningful when typed."""
        return self.word1 - ROM_BASE


@dataclass(frozen=True, slots=True)
class MapSlotArray:

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
