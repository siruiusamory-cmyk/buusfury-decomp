"""TOOLKIT-033 portable proof for one evidence-backed native effect."""

import pytest

from tools.webfoot.authored_placements import (
    AuthoredBehaviorError,
    _expand_semantic_source,
)
from tools.webfoot.data.script_effects import SCRIPT_EFFECTS
from tools.webfoot.data.script_specs import OPCODE_SETS
from tools.webfoot.formats.script_vm import Entry, assemble, assemble_source, disassemble


PROFILE = 'buus_fury_usa_rev0_01c1707f'
BUU = OPCODE_SETS['stack_be16_buu_v1']
SEMANTIC_SOURCE = ('show_centered_sprite_text text:1525 120 105', 'terminate')
VM_SOURCE = ('push_many 3 1525 120 105', 'native_stack 178', 'terminate')
BODY = bytes.fromhex('1d03976a8170815202b211')


def test_selected_native_semantic_mapping_is_exact_and_narrow():
    assert SCRIPT_EFFECTS == {
        PROFILE: {
            'show_centered_sprite_text': {
                'native_opcode': 'native_stack',
                'native_slot': 178,
                'native_handler_raw': 0x08003031,
                'arguments': ('text', 'x', 'y'),
                'text_count': 1534,
                'evidence': SCRIPT_EFFECTS[PROFILE]['show_centered_sprite_text']['evidence'],
            },
        },
    }
    assert 'BUU_DIALOG_RUNTIME.md:115-230' in (
        SCRIPT_EFFECTS[PROFILE]['show_centered_sprite_text']['evidence'])


def test_semantic_operation_expands_to_the_canonical_native_call_shape():
    assert _expand_semantic_source(SEMANTIC_SOURCE, PROFILE, 'owner') == VM_SOURCE


def test_production_codec_encodes_the_exact_native_invocation():
    assert assemble_source(VM_SOURCE, BUU) == BODY
    ir = disassemble(BODY, (Entry('authored', 0),), BUU)
    assert ir.opaque == ()
    assert assemble(ir) == BODY
    instructions = [i for block in ir.blocks for i in block.instructions]
    assert [i.opcode for i in instructions] == [0x1D, 0x02, 0x11]
    assert [operand.value for operand in instructions[0].operands] == [3, 1525, 120, 105]
    assert instructions[1].operands[0].value == 178


def test_signed_magnitude_source_encoding_matches_canonical_contract():
    assert assemble_source(('push_signed_magnitude 1525', 'terminate'), BUU) == bytes.fromhex(
        '01976a11')
    assert assemble_source(('push_many 3 1525 120 65', 'native_stack 178', 'terminate'),
                           BUU) == bytes.fromhex('1d03976a8170810202b211')


@pytest.mark.parametrize('line, reason', [
    ('show_centered_sprite_text 1525 120 105', 'text:NNNN'),
    ('show_centered_sprite_text text:1534 120 105', 'outside the verified table'),
    ('show_centered_sprite_text text:1525 240 105', 'on screen'),
    ('show_centered_sprite_text text:1525 120 160', 'on screen'),
    ('show_centered_sprite_text text:1525 x 105', 'coordinates must be integers'),
])
def test_semantic_operation_fails_closed(line, reason):
    with pytest.raises(AuthoredBehaviorError, match=reason):
        _expand_semantic_source((line,), PROFILE, 'owner')


def test_unverified_profile_gets_no_semantic_native_mapping():
    assert _expand_semantic_source(SEMANTIC_SOURCE, 'other', 'owner') == SEMANTIC_SOURCE
