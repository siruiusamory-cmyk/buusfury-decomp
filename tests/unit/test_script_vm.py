from dataclasses import replace
from pathlib import Path
import pytest
from tools.webfoot.formats.script_vm import (
    ScriptError, Evidence, Opcode, OpcodeSet, Operand, Entry, disassemble,
    assemble, decode_instruction, encode_instruction)
from tools.webfoot.data.script_specs import STACK_BE7_V1 as S
from tools.webfoot.scripts import Reference, script_references, reverse_text_consumers


def ir(raw, entries=(Entry('script:a',0),)):
    return disassemble(bytes(raw),entries,S)


@pytest.mark.parametrize('opcode',range(30))
def test_verified_opcode_width(opcode):
    op=S.lookup(opcode)
    args={'none':b'', 'u8':b'\x01', 'sm7':b'\x82\x00', 'count_sm7':b'\x02\x00\x01'}[op.encoding]
    raw=bytes([opcode])+args
    ins=decode_instruction(raw,0,S)
    assert ins.encoded_length==len(raw)
    assert encode_instruction(ins,S)==raw
    assert ins.evidence==Evidence.CONFIRMED_ROM
    assert ins.provenance


@pytest.mark.parametrize('raw',[b'\x00',b'\x01',b'\x01\x80',b'\x02',b'\x03',b'\x12',b'\x13',b'\x15',b'\x1c',b'\x1d',b'\x1d\x02\x00',b'\x1d\x00',b'\x1e',b'\xff',b'\x01\xff\xff\xff\xff\xff'])
def test_malformed_closed(raw):
    with pytest.raises(ScriptError): decode_instruction(raw,0,S)


@pytest.mark.parametrize('encoding,value',[(b'\x00',0),(b'\x01',0),(b'\x03',-1),(b'\x02',1),(b'\x80\x02',1),(b'\x82\x00',128)])
def test_varint_representation(encoding,value):
    ins=decode_instruction(b'\x01'+encoding,0,S)
    assert ins.operands[0].value==value
    assert encode_instruction(ins,S)==b'\x01'+encoding


def test_forward_branch_skips_opaque_unknown_bytes():
    graph=ir([18,2,255,255,17])
    assert graph.opaque==((2,b'\xff\xff'),)
    assert len(graph.blocks)==2
    assert graph.blocks[0].instructions[0].target==4
    assert assemble(graph)==bytes([18,2,255,255,17])


def test_conditional_shared_tail():
    graph=ir([0,1,19,2,0,2,17])
    assert len(graph.blocks)==3
    assert tuple(e.kind for e in graph.blocks[0].edges)==('taken','fallthrough')
    assert graph.blocks[0].edges[0].target==graph.blocks[1].edges[0].target
    assert assemble(graph)==bytes([0,1,19,2,0,2,17])


def test_loop_alternate_counter():
    raw=bytes([0,3,27,0,9,20,28,5,17])
    graph=ir(raw)
    ins=next(i for b in graph.blocks for i in b.instructions if i.opcode==28)
    assert ins.target==3
    assert len(graph.blocks)==3
    assert assemble(graph)==raw


def test_shared_entry_block():
    graph=ir([0,1,17],(Entry('a',0),Entry('b',2),Entry('alias',0)))
    assert len(graph.blocks)==2
    assert len(graph.entries)==3
    assert assemble(graph)==bytes([0,1,17])


@pytest.mark.parametrize('raw,entries',[(bytes([18,255]),(Entry('a',0),)),(bytes([19,1,0,3,17]),(Entry('a',0),)),(bytes([0,1,17]),(Entry('a',0),Entry('b',1))), (bytes([0,1]),(Entry('a',0),))])
def test_bad_control_flow(raw,entries):
    with pytest.raises(ScriptError): disassemble(raw,entries,S)


def test_deterministic_and_termination():
    raw=bytes([0,1,17,255])
    assert ir(raw)==ir(raw)
    assert assemble(ir(raw))==raw
    assert S.lookup(17).flow=='stop'
    assert S.lookup(5).stack==(2,1)
    assert S.lookup(2).stack is None


def test_unknown_semantics_known_width_survives():
    graph=ir([2,144,17])
    assert S.lookup(2).semantics==Evidence.UNKNOWN
    assert assemble(graph)==bytes([2,144,17])


def test_budget():
    with pytest.raises(ScriptError,match='budget'):
        disassemble(bytes([0,1,17]),(Entry('a',0),),S,max_instructions=1)


def test_profile_selected_alternative_set():
    other=OpcodeSet('synthetic',(Opcode(255,'halt',flow='stop'),))
    graph=disassemble(b'\xff',(Entry('a',0),),other)
    assert assemble(graph)==b'\xff'
    with pytest.raises(ScriptError): ir([255])


@pytest.mark.parametrize('field,value',[('encoded_length',9),('target',0),('operands',(Operand(99,b'\x01'),)),('provenance','wrong')])
def test_inconsistent_instruction_rejected(field,value):
    ins=decode_instruction(b'\x00\x01',0,S)
    with pytest.raises(ScriptError): encode_instruction(replace(ins,**{field:value}),S)


def test_ir_graph_tampering_rejected():
    graph=ir([18,0,17])
    first=replace(graph.blocks[0],edges=())
    with pytest.raises(ScriptError): assemble(replace(graph,blocks=(first,)+graph.blocks[1:]))


def test_opaque_tampering_rejected():
    graph=ir([17,255])
    with pytest.raises(ScriptError): assemble(replace(graph,opaque=()))


def test_dynamic_references_never_fabricate_fixed_id():
    refs=script_references(ir([2,12,2,75,17]))
    assert len(refs)==2
    assert [r.dynamic_expression for r in refs]==['runtime_byte + 48','runtime_byte + 54']
    assert all(r.target_id is None for r in refs)
    assert all(not v for v in reverse_text_consumers(refs,260).values())


def test_reverse_reference_index_synthetic_verified_contract():
    ref=Reference('s','b',0,'text',3,'synthetic contract')
    assert reverse_text_consumers((ref,ref),5)[3]==(ref,)
    with pytest.raises(ScriptError): reverse_text_consumers((replace(ref,target_id=5),),5)


def test_parser_never_writes_partial_output(tmp_path,monkeypatch):
    def forbidden(*args,**kwargs): raise AssertionError('filesystem write from parser')
    monkeypatch.setattr(Path,'write_bytes',forbidden)
    monkeypatch.setattr(Path,'write_text',forbidden)
    with pytest.raises(ScriptError): ir([0,1,255])
    assert list(tmp_path.iterdir())==[]

@pytest.mark.parametrize('field,value',[('count',0),('stride',2),('slots',[4,4]),('slots',[-1]),('slots',[1]),('table_address',0x086d66c0),('pool_size',9000000),('family','')])
def test_invalid_profile_contract(field,value):
    import yaml
    from tools.webfoot.profile import RomProfileCatalog,ProfileConfigError
    data=yaml.safe_load(Path('config/roms.yaml').read_text())
    # Pinned to LOGII: more than one profile declares scripts since TOOLKIT-013,
    # and the table_address case is an overlap against LOGII's pool specifically.
    profile=next(p for p in data['profiles']
                 if p['id']=='legacy_of_goku_ii_usa_rev0_204142e1')
    profile['tables']['scripts'][field]=value
    with pytest.raises(ProfileConfigError): RomProfileCatalog.loads(yaml.safe_dump(data))


# --- TOOLKIT-013: the Buu grammar, exercised on synthetic streams -----------
# The real Buu corpus contains no branch opcode, so the branch contract is only
# reachable here. These fixtures are synthetic by design: no ROM payload is
# embedded, and they test the mechanics the handler disassembly established.

from tools.webfoot.data.script_specs import STACK_BE16_BUU_V1 as B


def buu_ir(raw, entries=(Entry('script:a', 0),)):
    return disassemble(bytes(raw), entries, B)


def test_buu_forward_branch_is_be16_from_the_pre_operand_cursor():
    # 0x12 at 0 with displacement 4: base is the cursor *before* the halfword
    # (offset 1), so the target is 5 - not 7, which a post-operand base gives.
    raw = bytes([0x12, 0x00, 0x04, 0xFF, 0xFF, 0x11])
    graph = buu_ir(raw)
    assert graph.blocks[0].instructions[0].target == 5
    assert graph.opaque == ((3, b'\xff\xff'),)
    assert assemble(graph) == raw


def test_buu_backward_branch_subtracts():
    raw = bytes([0x00, 0x05, 0x1C, 0x00, 0x03, 0x11])
    graph = buu_ir(raw)
    branch = next(i for b in graph.blocks for i in b.instructions if i.opcode == 0x1C)
    assert branch.target == 0
    assert len(graph.blocks) == 2
    assert assemble(graph) == raw


def test_buu_conditional_branch_has_both_edges():
    # 0x13 at offset 2, base 3, displacement 4 -> taken target 7; the
    # fallthrough at 5 terminates, so both successors are real instructions.
    raw = bytes([0x00, 0x01, 0x13, 0x00, 0x04, 0x11, 0x14, 0x11])
    graph = buu_ir(raw)
    branch = next(i for b in graph.blocks for i in b.instructions if i.opcode == 0x13)
    assert branch.target == 7
    block = next(b for b in graph.blocks if branch in b.instructions)
    assert tuple(e.kind for e in block.edges) == ('taken', 'fallthrough')
    assert assemble(graph) == raw


@pytest.mark.parametrize('raw', [
    b'\x12\x00',      # truncated be16 displacement
    b'\x13\x00',
    b'\x1c\x00',
    b'\x1f',          # past the measured 31-slot table
    b'\xff',
])
def test_buu_malformed_fails_closed(raw):
    """Never guess a width, skip bytes, or treat an unknown opcode as a no-op."""
    with pytest.raises(ScriptError):
        decode_instruction(raw, 0, B)


def test_buu_opcode_table_stops_at_the_measured_bound():
    assert len(B.instructions) == 31
    assert B.lookup(0x1E).name
    with pytest.raises(ScriptError):
        B.lookup(0x1F)


@pytest.mark.parametrize('raw', [
    # Backward branch landing inside push_byte's operand at offset 1.
    [0x00, 0x05, 0x1C, 0x00, 0x02, 0x11],
    # Backward branch past the start of the stream.
    [0x00, 0x05, 0x1C, 0x00, 0x40, 0x11],
    # Forward branch past the end of the stream.
    [0x12, 0x00, 0x40, 0x11],
])
def test_buu_branch_outside_an_instruction_boundary_is_refused(raw):
    """A target must land on a real instruction; it is never nudged to fit."""
    with pytest.raises(ScriptError):
        buu_ir(raw)


def test_unverified_rom_rejected_before_scripts(tmp_path):
    from tools.webfoot.scripts import load_scripts
    from tools.webfoot.profile import RomProfileCatalog
    from tools.webfoot.capability import CapabilityError
    from tests.helpers import make_synthetic_rom
    path=tmp_path/'unknown.gba'
    path.write_bytes(make_synthetic_rom())
    with pytest.raises(CapabilityError): load_scripts(path,RomProfileCatalog.load('config/roms.yaml'))
