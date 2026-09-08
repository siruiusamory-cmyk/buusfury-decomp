"""Pure physical bindings for verified placement descriptors and VM dispatch.

No filesystem or project identities. Offsets remain explicit file offsets; raw
Thumb pointers remain separate from code fetch locations.
"""
from dataclasses import dataclass
import struct
from ..binary import GbaRomAddress
from .map_placements import DescriptorRecord, MapPlacementLengthError


def descriptor_at(image, pointer):
    offset = GbaRomAddress(pointer).to_file_offset(len(image))
    return offset, DescriptorRecord.from_bytes(image[offset:offset + 8])


def root_at(image, pointer, size):
    offset = GbaRomAddress(pointer).to_file_offset(len(image))
    if type(size) is not int or size <= 0 or offset + size > len(image):
        raise MapPlacementLengthError('script extent outside image')
    return offset, image[offset:offset + size]


def descriptor_source(placement_offset):
    return placement_offset + 0x14


def payload_source(descriptor_offset):
    return descriptor_offset + 4


def thumb_fetch(image, raw):
    if not raw & 1:
        raise ValueError('verified code pointer must preserve Thumb state')
    return GbaRomAddress(raw - 1).to_file_offset(len(image))


@dataclass(frozen=True)
class NativeBinding:
    source: int
    index: int
    table: int
    slot: int
    handler_raw: int
    handler_fetch: int


def native_bindings(image, ir, segments, table_pointer, opcodes):
    """Bind virtual IR operand bytes to their actual source fields and table slots."""
    table = GbaRomAddress(table_pointer).to_file_offset(len(image))
    result = []
    for block in ir.blocks:
        for ins in block.instructions:
            if ins.opcode not in opcodes:
                continue
            segment = next(s for s in segments
                           if s.ir_offset <= ins.source_offset < s.ir_offset + s.size)
            index = ins.operands[0].value
            slot = table + 4 * index
            raw = struct.unpack_from('<I', image, slot)[0]
            source = segment.file_offset + ins.source_offset - segment.ir_offset + 1
            result.append(NativeBinding(source, index, table, slot, raw, thumb_fetch(image, raw)))
    return tuple(result)
