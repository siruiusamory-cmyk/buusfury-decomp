from dataclasses import dataclass
import struct
from ..binary import GbaRomAddress
from .map_placements import DescriptorRecord, MapPlacementLengthError
from .script_vm import Entry, assemble, decode_instruction, disassemble


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


PUSH_MANY = 0x1D
NATIVE_STACK = 0x02


@dataclass(frozen=True)
class OperandReference:
    kind: str
    event: str
    block: str
    ir_offset: int
    source: int
    encoded_length: int
    index: int
    access: str = ''


def _producer(block, position, depth):
    if position == 0:
        return None, None
    previous = block.instructions[position - 1]
    if previous.opcode != PUSH_MANY:
        return None, None
    count = len(previous.operands) - 1
    if count < depth:
        return None, None
    return previous, 1 + count - depth


def operand_references(ir, segments, resource, save_flag):
    found = []

    def physical(segment, ins, operand_position):
        offset = segment.file_offset + ins.source_offset - segment.ir_offset
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


@dataclass(frozen=True)
class EventResourceRecord:
    index: int
    slot_offset: int
    pointer_raw: int
    start: int
    end: int
    dialog_pointer_raw: int
    dialog_offset: int
    dialog_type: int

    @property
    def size(self):
        return self.end - self.start

    @property
    def supported(self):
        """Only a type-0 dialog exposes its code block directly in ROM."""
        return self.dialog_type == DIALOG_TYPE_CODE_BLOCK


#: The consumer reads this byte and branches on it (0x080040BA..0x080040C2).
DIALOG_TYPE_CODE_BLOCK = 0
DIALOG_TYPE_PACKED = 4
#: Type 0 runs the block starting three bytes into the dialog (0x080040EA).
DIALOG_CODE_OFFSET = 3


def event_resource_records(image, resource):
    table = GbaRomAddress(resource['table']).to_file_offset(len(image))
    count = resource['count']
    pool = GbaRomAddress(resource['pool_start']).to_file_offset(len(image))
    if table + 4 * count > len(image):
        raise ValueError('event resource table outside image')
    raw = [struct.unpack_from('<I', image, table + 4 * i)[0] for i in range(count)]
    starts = []
    for pointer in raw:
        offset = GbaRomAddress(pointer).to_file_offset(len(image))
        if not pool <= offset < table:
            raise ValueError('event resource record outside declared pool')
        starts.append(offset)
    if any(starts[i] >= starts[i + 1] for i in range(count - 1)):
        raise ValueError('event resource table is not strictly ascending')
    if starts[0] != pool:
        raise ValueError('event resource pool does not start at the first record')
    records = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < count else table
        dialog_raw = struct.unpack_from('<I', image, start)[0]
        dialog = GbaRomAddress(dialog_raw).to_file_offset(len(image))
        dialog_type = image[dialog + 2]
        records.append(EventResourceRecord(i, table + 4 * i, raw[i], start, end,
                                           dialog_raw, dialog, dialog_type))
    if sum(r.size for r in records) != table - pool:
        raise ValueError('event resource records do not tile the pool exhaustively')
    return tuple(records)


@dataclass(frozen=True)
class DialogTextReference:
    dialog: int
    block: str
    ir_offset: int
    source: int
    encoded_length: int
    index: int
    x: int
    y: int


def dialog_text_references(image, record, spec, dialog_text, text_count):
    """Text-table indices a type-0 dialog proves it renders, or ().
    The consumer slot is named by the contract, never inferred. Native handler
    0x08003030 pops three values and routes the deepest into 0x0802BFBC, which
    indexes the verified text pointer table and measures the result as a
    UTF-16LE NUL-terminated string before drawing it. So the index is the value
    pushed *first*, which is exactly what `_producer` resolves at that depth.
    """
    block = dialog_code_block(image, record, spec)
    if block is None:
        return ()
    start, _, ir = block
    slot = dialog_text['consumer_slot']
    depth = dialog_text['pops']
    found = []
    for code in ir.blocks:
        for position, ins in enumerate(code.instructions):
            if ins.opcode != NATIVE_STACK or not ins.operands:
                continue
            if ins.operands[0].value != slot:
                continue
            producer, where = _producer(code, position, depth)
            if producer is None:
                continue
            if where != 1 or len(producer.operands) != depth + 1:
                continue
            operand = producer.operands[where]
            if not 0 <= operand.value < text_count:
                raise ValueError('dialog text index outside declared table')
            offset = start + producer.source_offset + 1
            for earlier in producer.operands[:where]:
                offset += len(earlier.encoding)
            found.append(DialogTextReference(
                record.index, code.identity, producer.source_offset, offset,
                len(operand.encoding), operand.value,
                producer.operands[where + 1].value,
                producer.operands[where + 2].value))
    return tuple(sorted(found, key=lambda r: r.ir_offset))


def dialog_code_block(image, record, spec):
    if not record.supported:
        return None
    start = record.dialog_offset + DIALOG_CODE_OFFSET
    limit = min(len(image), record.start)
    window = image[start:limit]
    end, seen, pending = 0, set(), [0]
    while pending:
        pos = pending.pop()
        while 0 <= pos < len(window) and pos not in seen:
            seen.add(pos)
            ins = decode_instruction(window, pos, spec)
            after = pos + ins.encoded_length
            if ins.target is not None:
                if not 0 <= ins.target <= len(window):
                    raise ValueError('dialog branch leaves the record')
                pending.append(ins.target)
                end = max(end, ins.target)
            end = max(end, after)
            if spec.lookup(ins.opcode).flow == 'stop':
                break
            pos = after
    if end <= 0:
        raise ValueError('dialog code block is empty')
    raw = image[start:start + end]
    ir = disassemble(raw, (Entry('dialog', 0),), spec)
    # Opaque bytes are tolerated here, unlike in the map-scene corpus, because
    # a block may branch over a terminate that no path falls through to. Such a
    # byte is real code the walk already bounded, so exact re-encoding is the
    # guarantee that matters; a byte that did not re-encode would still fail.
    if assemble(ir) != raw:
        raise ValueError('dialog code block does not round-trip')
    return start, raw, ir
