"""Pure physical bindings for verified placement descriptors and VM dispatch.

No filesystem or project identities. Offsets remain explicit file offsets; raw
Thumb pointers remain separate from code fetch locations.
"""
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


@dataclass(frozen=True)
class EventResourceRecord:
    """One physical entry of the event-resource pointer table.

    `start`/`end` are the record's own tiled extent. `dialog_pointer_raw` is the
    record's first word, which the consumer dereferences before doing anything
    else; `dialog_type` is the byte the consumer then reads from that target and
    branches on. Naming follows the engine's own assertion text, not a guess.
    """
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
        """Only a type-0 dialog exposes its code block directly in ROM.

        Type 4 is real and handled by the engine, but its block is expanded at
        runtime by a routine relocated into IWRAM, so ROM bytes alone cannot
        reproduce it. Everything else hits the engine's own assertion.
        """
        return self.dialog_type == DIALOG_TYPE_CODE_BLOCK


#: The consumer reads this byte and branches on it (0x080040BA..0x080040C2).
DIALOG_TYPE_CODE_BLOCK = 0
DIALOG_TYPE_PACKED = 4
#: Type 0 runs the block starting three bytes into the dialog (0x080040EA).
DIALOG_CODE_OFFSET = 3


def event_resource_records(image, resource):
    """Tile the whole pointer table into exact, non-overlapping records.

    The table is the authority for both bounds: record i runs to the start of
    record i+1, and the last record runs to the table itself. That the result
    tiles the pool exhaustively is asserted, never assumed.
    """
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
        # Every record in the canonical image resolves here, record 0 included:
        # its dialog sits just below the pool rather than inside it, which the
        # dialog_offset makes visible instead of hiding behind a sentinel.
        dialog = GbaRomAddress(dialog_raw).to_file_offset(len(image))
        dialog_type = image[dialog + 2]
        records.append(EventResourceRecord(i, table + 4 * i, raw[i], start, end,
                                           dialog_raw, dialog, dialog_type))
    if sum(r.size for r in records) != table - pool:
        raise ValueError('event resource records do not tile the pool exhaustively')
    return tuple(records)


@dataclass(frozen=True)
class DialogTextReference:
    """One dialog operand proven to index the verified UTF-16 text table.

    TOOLKIT-020. This is a *new* relation reached through a new consumer chain,
    not a reversal of TOOLKIT-018: that ticket refuted three map-scene *event*
    consumer families as text sources, and none of them is this one.

    ``index`` is the text-table entry; ``x``/``y`` are the screen coordinates
    the same call supplies. ``source`` is the physical file offset of the index
    operand's own bytes, so provenance survives IR virtualisation.
    """
    dialog: int
    block: str
    ir_offset: int
    source: int
    encoded_length: int
    index: int
    x: int
    y: int


def dialog_text_references(image, record, spec, dialog_text):
    """Text-table indices a type-0 dialog proves it renders, or ().

    The consumer slot is named by the contract, never inferred. Native handler
    0x08003030 pops three values and routes the deepest into 0x0802BFBC, which
    indexes the verified text pointer table and measures the result as a
    UTF-16LE NUL-terminated string before drawing it. So the index is the value
    pushed *first*, which is exactly what `_producer` resolves at that depth.

    A call whose index is left by an earlier instruction rather than a literal
    push is computed at runtime and yields nothing. Refusing it is the point:
    an unresolvable operand stays UNKNOWN instead of being guessed.
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
            # The handler pops three: index deepest, then x, then y. A producer
            # that supplies fewer than all three leaves the index off-stack, so
            # only a full-width push proves the whole call.
            if where != 1 or len(producer.operands) != depth + 1:
                continue
            operand = producer.operands[where]
            if not 0 <= operand.value < dialog_text['count']:
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
    """Exact ROM extent of a type-0 dialog's code block, or None.

    The extent is not searched for. Every reachable path is walked from the
    entry the consumer uses, one instruction at a time. A terminate ends a path
    but not necessarily the block: a forward branch may legitimately jump over
    a terminate, so the extent is the furthest byte any path reaches. The walk
    is then required to round-trip, which is what actually pins it.
    """
    if not record.supported:
        return None
    start = record.dialog_offset + DIALOG_CODE_OFFSET
    limit = min(len(image), record.start)
    # decode_instruction owns operand widths, both branch bases and the sign of
    # a count_back displacement. Re-deriving any of that here would be a second
    # implementation of the VM that could drift from the real one.
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
