"""Verified script corpus loading; parsing never performs project/build writes."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
import struct
from . import capability
from .binary import GbaRomAddress
from .data.script_specs import OPCODE_SETS
from .formats.script_vm import Entry, ScriptError, ScriptIR, disassemble, assemble
from .rom import identify_rom, RomChangedError


@dataclass(frozen=True)
class ScriptCorpus:
    profile_id: str
    source_offset: int
    ir: ScriptIR

    @property
    def instruction_count(self):
        return sum(len(b.instructions) for b in self.ir.blocks)


@dataclass(frozen=True)
class Reference:
    script: str
    block: str
    instruction_offset: int
    kind: str
    target_id: int | None
    provenance: str
    dynamic_expression: str | None = None


def reverse_text_consumers(references, count: int):
    if type(count) is not int or count < 0:
        raise ScriptError('invalid text count')
    result = {i: [] for i in range(count)}
    for ref in references:
        if ref.kind != 'text' or ref.target_id is None:
            continue
        if type(ref.target_id) is not int or ref.target_id not in result:
            raise ScriptError('text reference outside declared table')
        if not ref.provenance:
            raise ScriptError('text reference lacks provenance')
        result[ref.target_id].append(ref)
    return {i: tuple(sorted(set(refs), key=lambda r:(r.script,r.block,r.instruction_offset)))
            for i, refs in result.items()}


def script_references(ir: ScriptIR):
    """Only evidence-declared native references; no numeric stack-value guessing."""
    # Rule data belongs with the selected opcode specification.
    from .data.script_specs import REFERENCE_RULES
    rules = REFERENCE_RULES.get(ir.opcode_set.name, {})
    blocks = {b.identity:b for b in ir.blocks}
    at = {b.instructions[0].source_offset:b.identity for b in ir.blocks}
    found = []
    for entry in ir.entries:
        pending = [at[entry.offset]]
        seen = set()
        while pending:
            label = pending.pop()
            if label in seen:
                continue
            seen.add(label)
            block = blocks[label]
            pending.extend(e.target for e in block.edges)
            for ins in block.instructions:
                key = (ins.opcode, ins.operands[0].value if ins.operands else None)
                if key in rules:
                    kind, expr, provenance = rules[key]
                    found.append(Reference(entry.identity,label,ins.source_offset,
                                           kind,None,provenance,expr))
    return tuple(sorted(found,key=lambda r:(r.script,r.block,r.instruction_offset)))


def load_scripts(path, catalog) -> ScriptCorpus:
    identification = identify_rom(path, catalog)
    profile = capability.require(identification, capability.Capability.SCRIPTS,
                                 subsystem='script access')
    layout = profile.scripts
    spec = OPCODE_SETS.get(layout.encoding)
    if spec is None:
        raise ScriptError(f'unsupported opcode set {layout.encoding}')
    if profile.id not in spec.profiles:
        raise ScriptError('opcode set is not verified for this profile')
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != identification.hashes.sha256:
        raise RomChangedError('ROM changed before script read')
    table = layout.table_address.to_file_offset(len(data))
    pool = layout.pool_address.to_file_offset(len(data))
    entries = []
    for ordinal in range(layout.count):
        for slot in layout.slots:
            ptr = struct.unpack_from('<I',data,table+ordinal*layout.stride+slot)[0]
            offset = GbaRomAddress(ptr).to_file_offset(len(data))-pool
            if not 0 <= offset < layout.pool_size:
                raise ScriptError('entry outside declared script corpus')
            identity = f'{profile.id}:{layout.family}:{ordinal:02d}:slot{slot:02x}'
            entries.append(Entry(identity,offset))
    original = data[pool:pool+layout.pool_size]
    ir = disassemble(original,tuple(entries),spec)
    if ir.opaque:
        raise ScriptError('declared rooted corpus contains uncovered bytes')
    if assemble(ir) != original:
        raise ScriptError('script corpus does not round-trip')
    return ScriptCorpus(profile.id,pool,ir)
