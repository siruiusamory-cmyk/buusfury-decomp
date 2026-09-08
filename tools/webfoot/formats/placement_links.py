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


#: `push_many` is the only opcode that supplies several operands to one later
#: native call, so it is the only producer these classifiers accept.
PUSH_MANY = 0x1D
NATIVE_STACK = 0x02


@dataclass(frozen=True)
class OperandReference:
    """One script operand proven to select a stable resource.

    ``kind`` is structural, never a gameplay name. ``source`` is the physical
    file offset of the operand bytes, so provenance survives IR virtualisation.
    """
    kind: str
    event: str
    block: str
    ir_offset: int
    source: int
    encoded_length: int
    index: int
    access: str = ''


def _producer(block, position, depth):
    """The instruction supplying the value popped ``depth``-from-top, if proven.

    Returns the producer and the operand's own position within it, because two
    operands of one ``push_many`` can share a value and only the position
    identifies which encoded field is meant.

    A consumer's arguments must come from one immediately preceding producer.
    Anything else (values left by an earlier block, arithmetic, a second
    producer) is not proven provenance and yields nothing rather than a guess.
    """
    if position == 0:
        return None, None
    previous = block.instructions[position - 1]
    if previous.opcode != PUSH_MANY:
        return None, None
    # push_many(count, v1..vN) pushes in order, so vN is on top. The consumer
    # pops `depth` values; the deepest of those is v(N-depth+1). Operand 0 is
    # the count, so the values start at index 1.
    count = len(previous.operands) - 1
    if count < depth:
        return None, None
    return previous, 1 + count - depth


def operand_references(ir, segments, resource, save_flag):
    """Classify operands that reach a proven table index or save-flag bit.

    Both contracts name their consumer dispatch slots explicitly; an operand is
    only classified when its own producer is proven, so numeric resemblance to
    any resource range can never promote one.
    """
    found = []

    def physical(segment, ins, operand_position):
        offset = segment.file_offset + ins.source_offset - segment.ir_offset
        # Skip the opcode byte, then every operand encoded before this one.
        offset += 1
        for earlier in ins.operands[:operand_position]:
            offset += len(earlier.encoding)
        return offset

    for block in ir.blocks:
        for position, ins in enumerate(block.instructions):
            if ins.opcode != NATIVE_STACK or not ins.operands:
                continue
            slot = ins.operands[0].value
            segment = next(s for s in segments
                           if s.ir_offset <= ins.source_offset < s.ir_offset + s.size)
            if slot in resource['consumers']:
                producer, where = _producer(block, position,
                                            resource['consumers'][slot])
                if producer is None:
                    continue
                operand = producer.operands[where]
                if not 0 <= operand.value < resource['count']:
                    raise ValueError('event resource index outside declared table')
                found.append(OperandReference(
                    'event_resource', segment.event, block.identity,
                    producer.source_offset, physical(segment, producer, where),
                    len(operand.encoding), operand.value))
            elif slot in save_flag['consumers']:
                producer = None
                if position:
                    previous = block.instructions[position - 1]
                    # A save-flag index is pushed alone, by a single push.
                    if previous.opcode in (0x00, 0x01) and previous.operands:
                        producer = previous
                if producer is None:
                    continue
                operand = producer.operands[0]
                found.append(OperandReference(
                    'save_flag', segment.event, block.identity,
                    producer.source_offset, physical(segment, producer, 0),
                    len(operand.encoding), operand.value,
                    save_flag['consumers'][slot]))
    return tuple(sorted(found, key=lambda r: (r.kind, r.event, r.ir_offset)))
