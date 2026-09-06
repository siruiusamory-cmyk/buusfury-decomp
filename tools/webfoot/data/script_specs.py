"""Verified VM variants as data; evidence: docs/research/SCRIPT_VM.md."""
from ..formats.script_vm import Evidence, Opcode, OpcodeSet

_E = Evidence.CONFIRMED_ROM
_P = 'docs/research/SCRIPT_VM.md:25'
_NAMES = ('push_byte','push_signed_magnitude','native_stack','native_pop',
          'logical_and','logical_or','negate','add','subtract','multiply',
          'divide_raw','equal','not_equal','greater','greater_equal','less',
          'less_equal','terminate','branch_forward','branch_if_zero','pop',
          'native_post_15_raw','native_post_16_raw','native_post_17_raw',
          'native_post_18_raw','native_post_19_raw','native_post_1a_raw',
          'transfer_to_alternate','alternate_count_back','push_many')
_HANDLERS = (0x8f44,0x8f5a,0x8f8e,0x8fa4,0x8fc6,0x8fe6,0x9000,0x900e,
             0x9022,0x9036,0x904a,0x9062,0x907c,0x9096,0x90b0,0x90ca,
             0x90e4,0,0x90fe,0x910a,0x9128,0x9130,0x9160,0x9190,
             0x91bc,0x91ec,0x9224,0x9250,0x926c,0x929a)
_BYTE = {0,2,3,18,19,21,22,23,24,25,26,28}
_FLOW = {17:'stop',18:'forward',19:'if_zero',28:'count_back'}
_STACK = {0:(0,1),1:(0,1),3:(1,0),6:(1,1),17:(0,0),18:(0,0),19:(1,0),20:(1,0),27:(1,0)}
_STACK.update({i:(2,1) for i in (4,5,7,8,9,10,11,12,13,14,15,16)})
STACK_BE7_V1 = OpcodeSet('stack_be7_v1', tuple(
    Opcode(i,name,'u8' if i in _BYTE else 'sm7' if i==1 else
           'count_sm7' if i==29 else 'none', _FLOW.get(i,'next'),
           _STACK.get(i),_E,f'{_P}; handler file 0x{_HANDLERS[i]:08X}',
           Evidence.UNKNOWN if i in (2,3,10,21,22,23,24,25,26) else _E)
    for i,name in enumerate(_NAMES)), ('legacy_of_goku_ii_usa_rev0_204142e1',))
OPCODE_SETS = {STACK_BE7_V1.name: STACK_BE7_V1}

# No fixed text operand proven. These native operations access runtime-selected slots.
REFERENCE_RULES = {'stack_be7_v1': {
    (2,12): ('text','runtime_byte + 48','docs/research/SCRIPT_VM.md; fetch 0x080094B0'),
    (2,75): ('text','runtime_byte + 54','docs/research/SCRIPT_VM.md; fetch 0x080094CC'),
}}
