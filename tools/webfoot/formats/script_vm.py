"""Pure bounded instruction codec and control-flow IR. No ROM or filesystem I/O."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class ScriptError(ValueError):
    pass


class Evidence(str, Enum):
    CONFIRMED_ROM = 'CONFIRMED_ROM'
    CONFIRMED_RUNTIME = 'CONFIRMED_RUNTIME'
    VERIFIED_UPSTREAM = 'VERIFIED_UPSTREAM'
    INFERRED = 'INFERRED'
    UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True)
class Opcode:
    value: int
    name: str
    encoding: str = 'none'
    flow: str = 'next'
    stack: tuple[int, int] | None = None
    evidence: Evidence = Evidence.UNKNOWN
    provenance: str = ''
    semantics: Evidence = Evidence.UNKNOWN


@dataclass(frozen=True)
class OpcodeSet:
    name: str
    instructions: tuple[Opcode, ...]
    profiles: tuple[str, ...] = ()

    def lookup(self, value: int) -> Opcode:
        matches = [op for op in self.instructions if op.value == value]
        if len(matches) != 1:
            raise ScriptError(f'unknown or ambiguous opcode 0x{value:02X}; parsing boundary')
        return matches[0]


@dataclass(frozen=True)
class Operand:
    value: int
    encoding: bytes  # preserves non-minimal representation and negative zero


@dataclass(frozen=True)
class Instruction:
    opcode: int
    operands: tuple[Operand, ...]
    source_offset: int
    encoded_length: int
    target: int | None
    evidence: Evidence
    provenance: str


@dataclass(frozen=True)
class Entry:
    identity: str
    offset: int


@dataclass(frozen=True)
class Edge:
    kind: str
    target: str


@dataclass(frozen=True)
class Block:
    identity: str
    instructions: tuple[Instruction, ...]
    edges: tuple[Edge, ...]


@dataclass(frozen=True)
class ScriptIR:
    opcode_set: OpcodeSet
    entries: tuple[Entry, ...]
    blocks: tuple[Block, ...]
    extent: int
    opaque: tuple[tuple[int, bytes], ...]


def _integer(value: int, what: str) -> None:
    if type(value) is not int or value < 0:
        raise ScriptError(f'{what} must be a nonnegative integer')


def _operand(data: bytes, pos: int, encoding: str) -> tuple[Operand, int]:
    start = pos
    if pos >= len(data):
        raise ScriptError(f'truncated operand at {pos}')
    if encoding == 'u8':
        return Operand(data[pos], data[pos:pos+1]), pos+1
    if encoding != 'sm7':
        raise ScriptError(f'unsupported operand encoding {encoding}')
    raw = 0
    for _ in range(5):
        if pos >= len(data):
            raise ScriptError(f'truncated varint at {start}')
        byte = data[pos]
        pos += 1
        raw = (raw << 7) | (byte & 127)
        # Overflow and signed-shift ambiguity are outside the supported contract.
        if raw > 0x7fffffff:
            raise ScriptError('varint overflow outside supported signed range')
        if byte < 128:
            value = -(raw >> 1) if raw & 1 else raw >> 1
            return Operand(value, data[start:pos]), pos
    raise ScriptError('varint exceeds bounded width')


def decode_instruction(data: bytes, offset: int, spec: OpcodeSet) -> Instruction:
    _integer(offset, 'offset')
    if offset >= len(data):
        raise ScriptError(f'instruction outside extent at {offset}')
    op = spec.lookup(data[offset])
    pos = offset + 1
    args = []
    if op.encoding in ('u8', 'sm7'):
        arg, pos = _operand(data, pos, op.encoding)
        args.append(arg)
    elif op.encoding == 'count_sm7':
        count, pos = _operand(data, pos, 'u8')
        if count.value == 0:
            raise ScriptError('zero count is outside supported multi-push contract')
        args.append(count)
        for _ in range(count.value):
            arg, pos = _operand(data, pos, 'sm7')
            args.append(arg)
    elif op.encoding != 'none':
        raise ScriptError(f'unknown width for opcode {op.value}')
    target = None
    if op.flow in ('forward', 'if_zero', 'count_back'):
        if len(args) != 1 or op.encoding != 'u8':
            raise ScriptError('branch specification requires one byte')
        target = pos + (-args[0].value if op.flow == 'count_back' else args[0].value)
    elif op.flow not in ('next', 'stop'):
        raise ScriptError('unknown control-flow contract')
    return Instruction(op.value, tuple(args), offset, pos-offset, target,
                       op.evidence, op.provenance)


def encode_instruction(ins: Instruction, spec: OpcodeSet) -> bytes:
    _integer(ins.opcode, 'opcode')
    if ins.opcode > 255:
        raise ScriptError('opcode outside byte range')
    raw = bytes([ins.opcode]) + b''.join(arg.encoding for arg in ins.operands)
    check = decode_instruction(raw, 0, spec)
    target = None if check.target is None else check.target + ins.source_offset
    if (check.operands != ins.operands or check.encoded_length != len(raw)
            or ins.encoded_length != len(raw) or target != ins.target
            or check.evidence != ins.evidence or check.provenance != ins.provenance):
        raise ScriptError('instruction operands, length, target or provenance disagree with encoding')
    return raw


def _successors(ins: Instruction, spec: OpcodeSet) -> tuple[tuple[str, int], ...]:
    flow = spec.lookup(ins.opcode).flow
    after = ins.source_offset + ins.encoded_length
    if flow == 'stop':
        return ()
    if flow == 'forward':
        return (('branch', ins.target),)
    if flow in ('if_zero', 'count_back'):
        return (('taken', ins.target), ('fallthrough', after))
    return (('fallthrough', after),)


def disassemble(data: bytes, entries: tuple[Entry, ...], spec: OpcodeSet,
                *, max_instructions: int = 100000) -> ScriptIR:
    if not isinstance(data, bytes) or not data:
        raise ScriptError('nonempty immutable bytes required')
    if not entries or len({e.identity for e in entries}) != len(entries):
        raise ScriptError('entry identities must be nonempty and unique')
    if any(not e.identity for e in entries):
        raise ScriptError('empty entry identity')
    _integer(max_instructions, 'instruction budget')
    pending = [e.offset for e in entries]
    decoded = {}
    owners = {}
    while pending:
        pos = pending.pop()
        _integer(pos, 'target')
        if pos in decoded:
            continue
        if pos in owners:
            raise ScriptError(f'target enters an operand at {pos}')
        if len(decoded) >= max_instructions:
            raise ScriptError('instruction budget exceeded')
        ins = decode_instruction(data, pos, spec)
        for byte in range(pos, pos+ins.encoded_length):
            if byte in owners:
                raise ScriptError(f'overlapping instructions at {byte}')
            owners[byte] = pos
        decoded[pos] = ins
        pending.extend(target for _, target in _successors(ins, spec))
    leaders = {e.offset for e in entries}
    for ins in decoded.values():
        if spec.lookup(ins.opcode).flow != 'next':
            leaders.update(target for _, target in _successors(ins, spec))
    labels = {pos: f'block:{i:04d}' for i, pos in enumerate(sorted(leaders))}
    blocks = []
    for pos in sorted(leaders):
        seq = []
        cursor = pos
        while True:
            ins = decoded[cursor]
            seq.append(ins)
            succ = _successors(ins, spec)
            after = cursor + ins.encoded_length
            if spec.lookup(ins.opcode).flow != 'next' or after in leaders:
                edges = tuple(Edge(kind, labels[target]) for kind, target in succ)
                break
            cursor = after
        blocks.append(Block(labels[pos], tuple(seq), edges))
    opaque = []
    pos = 0
    while pos < len(data):
        if pos in owners:
            pos += 1
            continue
        start = pos
        while pos < len(data) and pos not in owners:
            pos += 1
        opaque.append((start, data[start:pos]))
    return ScriptIR(spec, tuple(sorted(entries, key=lambda e:e.identity)),
                    tuple(blocks), len(data), tuple(opaque))


def assemble(ir: ScriptIR) -> bytes:
    _integer(ir.extent, 'extent')
    if ir.extent > 16 * 1024 * 1024:
        raise ScriptError('assembly extent exceeds budget')
    output = bytearray(ir.extent)
    occupied = set()
    fragments = list(ir.opaque)
    for block in ir.blocks:
        fragments.extend((i.source_offset, encode_instruction(i, ir.opcode_set))
                         for i in block.instructions)
    for start, raw in fragments:
        _integer(start, 'fragment offset')
        if not raw or start+len(raw)>ir.extent:
            raise ScriptError('fragment outside extent')
        span = set(range(start,start+len(raw)))
        if span & occupied:
            raise ScriptError('overlapping assembly fragments')
        occupied.update(span)
        output[start:start+len(raw)] = raw
    if len(occupied) != ir.extent:
        raise ScriptError('unrepresented assembly bytes')
    result = bytes(output)
    if disassemble(result, ir.entries, ir.opcode_set) != ir:
        raise ScriptError('IR graph or opaque coverage disagrees with instructions')
    return result
