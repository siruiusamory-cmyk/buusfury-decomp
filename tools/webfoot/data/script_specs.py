"""The VM variants are data whose evidence is docs/research/SCRIPT_VM.md."""
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

# Buu's Fury runs the same VM *architecture* as LOGII but a different
# implementation: branch displacements are two-byte big-endian measured from the
# cursor BEFORE the operand, and slot 0x1E is a real handler. Every entry below
# was re-derived from Buu handler code (docs/research/BUU_SCRIPT_VM.md); no LOGII
# opcode number, width or termination rule was transferred.
_BP = 'docs/research/BUU_SCRIPT_VM.md'
_BUU_NAMES = ('push_byte','push_signed_magnitude','native_stack','native_pop',
              'logical_and','logical_or','negate','add','subtract','multiply',
              'divide_raw','equal','not_equal','greater','greater_equal','less',
              'less_equal','terminate','branch_forward','branch_if_zero','pop',
              'native_post_15_raw','native_post_16_raw','native_post_17_raw',
              'native_post_18_raw','native_post_19_raw','native_post_1a_raw',
              'transfer_to_alternate','alternate_count_back','push_many',
              'native_pop_1e_raw')
_BUU_HANDLERS = (0x08003C75,0x08003C8B,0x08003CBF,0x08003CD5,0x08003CF7,
                 0x08003D17,0x08003D31,0x08003D3F,0x08003D53,0x08003D67,
                 0x08003D7B,0x08003DAB,0x08003DC5,0x08003DDF,0x08003DF9,
                 0x08003E13,0x08003E2D,0,0x08003E47,0x08003E57,0x08003E7D,
                 0x08003E85,0x08003EB5,0x08003EE5,0x08003F11,0x08003F49,
                 0x08003F79,0x08003FA5,0x08003FC1,0x08003FEF,0x08003D93)
_BUU_BYTE = {0,2,3,21,22,23,24,25,26}
_BUU_BE16 = {18,19,28}
_BUU_FLOW = {17:'stop',18:'forward',19:'if_zero',28:'count_back'}
_BUU_STACK = {0:(0,1),1:(0,1),3:(1,0),6:(1,1),17:(0,0),18:(0,0),19:(1,0),
              20:(1,0),27:(1,0),30:(1,0)}
_BUU_STACK.update({i:(2,1) for i in (4,5,7,8,9,10,11,12,13,14,15,16)})
# Native dispatch and the operations whose callees are runtime-selected keep UNKNOWN semantics, because structural decoding does not require knowing what they do.
_BUU_UNKNOWN_SEMANTICS = {2,3,10,21,22,23,24,25,26,30}


def _buu_encoding(i):
    if i in _BUU_BE16:
        return 'be16'
    if i in _BUU_BYTE:
        return 'u8'
    if i == 1:
        return 'sm7'
    if i == 29:
        return 'count_sm7'
    return 'none'


STACK_BE16_BUU_V1 = OpcodeSet('stack_be16_buu_v1', tuple(
    Opcode(i, name, _buu_encoding(i), _BUU_FLOW.get(i, 'next'),
           _BUU_STACK.get(i), _E,
           f'{_BP}; handler 0x{_BUU_HANDLERS[i]:08X}' if _BUU_HANDLERS[i]
           else f'{_BP}; null dispatch slot terminates',
           Evidence.UNKNOWN if i in _BUU_UNKNOWN_SEMANTICS else _E,
           'before_operand' if i in _BUU_BE16 else 'after_operand')
    for i, name in enumerate(_BUU_NAMES)), ('buus_fury_usa_rev0_01c1707f',))

OPCODE_SETS = {STACK_BE7_V1.name: STACK_BE7_V1,
               STACK_BE16_BUU_V1.name: STACK_BE16_BUU_V1}

REFERENCE_RULES = {'stack_be7_v1': {
    (2,12): ('text','runtime_byte + 48','docs/research/SCRIPT_VM.md; fetch 0x080094B0'),
    (2,75): ('text','runtime_byte + 54','docs/research/SCRIPT_VM.md; fetch 0x080094CC'),
}}
