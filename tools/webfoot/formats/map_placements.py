"""Pure codec for the TOOLKIT-016 factory-led variable-length placement family.
CONFIRMED: 0x1C + 4*n bytes; +14 descriptor pointer, +18 child count,
+1C ordered child pointers. Evidence: BUU_FD55_SCRIPT_OWNER.md, constructor
0800F6D2 -> 0800A93C. Position halfwords stay lossless raw bits at this layer;
for the supported Buu placement constructor, their signed interpretations are
map/world X (low) and Y (high) pixels; see PLACEMENT_POSITION_PROVENANCE.md.
TOOLKIT-008's 32-byte fixed-tail shape remains a legacy subset predicate only.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import struct

from ..binary import GBA_ROM_BASE as ROM_BASE

FACTORY_RAW = 0x0800FD55
PREFIX_SIZE = 0x1C
PLACEMENT_SIZE = 32
RECORD_TAIL = (0x080555A0, 1, 0x080716EC)
MAX_CHILDREN = 4  # Verified supported corpus bound, not an engine maximum.
HANDLERS = {0x0800421D: 'handler_0800421d',
            0x0800421F: 'handler_0800421f',
            0x0800424F: 'handler_0800424f'}
SCRIPT_DISPATCH_HANDLER = 0x0800421F


class MapPlacementError(ValueError):
    pass


class MapPlacementLengthError(MapPlacementError):
    pass


class MapPlacementValueError(MapPlacementError):
    pass


class MapPlacementShapeError(MapPlacementError):
    pass


def decode_position_halfword(raw: int) -> int:
    """Decode one lossless placement halfword as its signed map-pixel value."""
    if type(raw) is not int or not 0 <= raw <= 0xFFFF:
        raise MapPlacementValueError('position halfword must be an unsigned 16-bit integer')
    return raw if raw < 0x8000 else raw - 0x10000


def encode_position_coordinate(coordinate: int) -> int:
    """Encode one signed map-pixel coordinate without wrapping or clamping."""
    if type(coordinate) is not int or not -0x8000 <= coordinate <= 0x7FFF:
        raise MapPlacementValueError('position coordinate must be a signed 16-bit integer')
    return coordinate & 0xFFFF


def decode_position(low: int, high: int) -> tuple[int, int]:
    """Decode raw low/high halves to the confirmed `(map_x, map_y)` pair."""
    return decode_position_halfword(low), decode_position_halfword(high)


def encode_position(map_x: int, map_y: int) -> tuple[int, int]:
    """Encode map-pixel X/Y to lossless raw low/high halves."""
    return encode_position_coordinate(map_x), encode_position_coordinate(map_y)


@dataclass(frozen=True)
class DescriptorRecord:
    handler_pointer_raw: int
    payload_raw: int

    @classmethod
    def from_bytes(cls, data):
        if len(data) != 8:
            raise MapPlacementLengthError('descriptor must contain exactly two words')
        return cls(*struct.unpack('<2I', data))

    def to_bytes(self):
        return struct.pack('<2I', self.handler_pointer_raw, self.payload_raw)


def record_size(child_count: int) -> int:
    if type(child_count) is not int or not 1 <= child_count <= MAX_CHILDREN:
        raise MapPlacementLengthError('child count outside verified supported range 1..4')
    return PREFIX_SIZE + 4 * child_count


@dataclass(frozen=True, slots=True)
class PlacementRecord:
    factory_raw: int
    flags_raw: int
    type_raw: int
    position_raw: int
    id_raw: int
    descriptor_pointer_raw: int
    child_pointers_raw: tuple[int, ...]

    @property
    def child_count(self) -> int:
        return len(self.child_pointers_raw)

    @property
    def consumed_length(self) -> int:
        return record_size(self.child_count)

    tail0_raw = property(lambda self: self.descriptor_pointer_raw)
    tail1_raw = property(lambda self: self.child_count)
    tail2_raw = property(lambda self: self.child_pointers_raw[0])

    @classmethod
    def from_bytes(cls, data: bytes | bytearray | memoryview) -> PlacementRecord:
        if len(data) < PREFIX_SIZE:
            raise MapPlacementLengthError('truncated placement fixed prefix')
        prefix = struct.unpack_from('<7I', data)
        size = record_size(prefix[6])
        if len(data) != size:
            raise MapPlacementLengthError(f'placement extent must be {size} bytes; got {len(data)}')
        return cls(*prefix[:6], struct.unpack_from(f'<{prefix[6]}I', data, PREFIX_SIZE))

    def to_bytes(self) -> bytes:
        size = self.consumed_length
        values = (self.factory_raw, self.flags_raw, self.type_raw, self.position_raw,
                  self.id_raw, self.descriptor_pointer_raw, self.child_count,
                  *self.child_pointers_raw)
        if any(type(v) is not int or not 0 <= v <= 0xFFFFFFFF for v in values):
            raise MapPlacementValueError('every placement word must be an unsigned 32-bit integer')
        encoded = struct.pack(f'<{len(values)}I', *values)
        assert len(encoded) == size
        return encoded

    position_low = property(lambda self: self.position_raw & 0xFFFF)
    position_high = property(lambda self: (self.position_raw >> 16) & 0xFFFF)
    position_x = property(lambda self: decode_position_halfword(self.position_low))
    position_y = property(lambda self: decode_position_halfword(self.position_high))

    def with_position(self, low: int, high: int) -> PlacementRecord:
        if any(type(v) is not int or not 0 <= v <= 0xFFFF for v in (low, high)):
            raise MapPlacementValueError('position halfwords must be unsigned 16-bit integers')
        return replace(self, position_raw=(high << 16) | low)

    def with_map_position(self, map_x: int, map_y: int) -> PlacementRecord:
        """Return this record at signed map-pixel `(map_x, map_y)`."""
        return self.with_position(*encode_position(map_x, map_y))


def is_legacy_placement_record(data, offset: int) -> bool:
    if offset < 0 or offset + PLACEMENT_SIZE > len(data):
        return False
    words = struct.unpack_from('<8I', data, offset)
    return words[0] == FACTORY_RAW and words[5:] == RECORD_TAIL


def read_placement_record(data, offset: int, *, end: int | None = None) -> PlacementRecord:
    """Read within an explicit exclusive extent; malformed factory records raise."""
    end = len(data) if end is None else end
    if not 0 <= offset < end <= len(data) or offset + PREFIX_SIZE > end:
        raise MapPlacementLengthError('placement prefix outside declared extent')
    if struct.unpack_from('<I', data, offset)[0] != FACTORY_RAW:
        raise MapPlacementShapeError('unsupported placement factory')
    size = record_size(struct.unpack_from('<I', data, offset + 0x18)[0])
    if offset + size > end:
        raise MapPlacementLengthError('truncated child pointer array outside declared extent')
    record = PlacementRecord.from_bytes(data[offset:offset + size])
    if not ROM_BASE <= record.descriptor_pointer_raw < ROM_BASE + 0x02000000:
        raise MapPlacementShapeError('descriptor is outside cartridge provenance')
    return record


def is_placement_record(data, offset: int) -> bool:
    try:
        read_placement_record(data, offset)
        return True
    except MapPlacementError:
        return False


#: placement family. TOOLKIT-025 measured the complete `MapEntry+0x04` traversal over
#: `0x0800FD55` placements, 191 `0x08017DA3` and 148 `0x080111A9` - with zero UNKNOWN
SIBLING_FACTORIES = (0x08017DA3, 0x080111A9)


@dataclass(frozen=True, slots=True)
class ObjectSlot:
    """One physical 4-byte pointer slot of a map's engine-owned object array.
    The engine's outer loop (`0x08008C9E`, proven in TOOLKIT-024) consumes exactly
    `MapEntry+0x04` slots of `MapEntry+0x14`, dereferencing each without inspecting
    the target's family. The array is therefore HETEROGENEOUS: placement-family
    records and sibling-family objects interleave in an order that is canonical and
    must survive round-trip exactly as measured.
    """

    index: int
    source_offset: int
    pointer_raw: int
    target_offset: int | None
    family_raw: int | None

    @property
    def is_placement(self) -> bool:
        return self.family_raw == FACTORY_RAW

    @property
    def is_sibling(self) -> bool:
        return self.family_raw in SIBLING_FACTORIES

    @property
    def family(self) -> str:
        if self.family_raw is None:
            return 'OUT_OF_IMAGE'
        if self.is_placement:
            return 'PLACEMENT'
        if self.is_sibling:
            return f'SIBLING_{self.family_raw:08X}'
        return 'UNKNOWN'


def iter_object_slots(data, array_offset: int, count: int) -> tuple[ObjectSlot, ...]:
    if type(count) is not int or count < 0:
        raise MapPlacementLengthError('object-array count must be a non-negative integer')
    if array_offset < 0 or array_offset + 4 * count > len(data):
        raise MapPlacementLengthError('object pointer array outside image')
    slots = []
    for index in range(count):
        source = array_offset + 4 * index
        pointer = struct.unpack_from('<I', data, source)[0]
        target = pointer - ROM_BASE
        if 0 <= target <= len(data) - 4:
            family = struct.unpack_from('<I', data, target)[0]
        else:
            target, family = None, None
        slots.append(ObjectSlot(index=index, source_offset=source, pointer_raw=pointer,
                                target_offset=target, family_raw=family))
    return tuple(slots)


def iter_placement_offsets(data, array_offset: int, *, count: int | None = None) -> tuple[int, ...]:
    if array_offset < 0 or array_offset + 4 > len(data):
        if count is not None:
            raise MapPlacementLengthError('pointer array outside image')
        return ()
    if count is not None and (type(count) is not int or count < 0 or array_offset + 4 * count > len(data)):
        raise MapPlacementLengthError('truncated placement pointer array')
    offsets = []
    extents = []
    cursor = array_offset
    while cursor + 4 <= len(data) and (count is None or len(offsets) < count):
        word = struct.unpack_from('<I', data, cursor)[0]
        target = word - ROM_BASE
        if not 0 <= target <= len(data) - 4 or struct.unpack_from('<I', data, target)[0] != FACTORY_RAW:
            if count is not None:
                raise MapPlacementShapeError('declared run contains a non-placement pointer')
            break
        record = read_placement_record(data, target)
        offsets.append(target)
        extents.append((target, target + record.consumed_length))
        cursor += 4
    ordered = sorted(extents)
    if any(a[1] > b[0] for a, b in zip(ordered, ordered[1:])):
        raise MapPlacementShapeError('overlapping placement record bodies')
    return tuple(offsets)
