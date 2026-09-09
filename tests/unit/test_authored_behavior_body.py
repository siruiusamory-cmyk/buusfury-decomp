"""TOOLKIT-032: authoring a NEW behavior body - descriptor AND script.

Every earlier ticket attached a descriptor the canonical ROM already contained.
These tests cover the parts that need no ROM: the author-facing declaration and
the production script encoder.

The descriptor/script WIRING is deliberately not tested here. Encoding an
authored body requires the profile's verified script contract, and the synthetic
fixture profile has none - it refuses, correctly and by design. So allocation,
descriptor serialization and the pointer edges are proven against canonical Buu
in tests/integration/test_authored_behavior_body_rom.py, where a real contract
exists rather than a stand-in.
"""
from dataclasses import replace

import pytest

from tests.unit.test_authored_placements import project, add, rewrite
from tests.unit.test_placement_types import types  # noqa: F401 - fixture for `project`
from tools.webfoot.data.script_specs import OPCODE_SETS
from tools.webfoot.formats.script_vm import (Entry, ScriptError, assemble, assemble_source,
                                             disassemble)
from tools.webfoot.project import ProjectValidationError, read_project
from tools.webfoot.project.format import load_toml
from tools.webfoot.project.placements import AuthoredPlacement

BUU = OPCODE_SETS["stack_be16_buu_v1"]

#: The authored body this ticket declares, in both of its forms. The mnemonics are
#: what a project writes; the bytes are what the engine must end up holding. They
#: are pinned together here so a change to either without the other fails.
SOURCE = ("push_byte 84", "push_byte 75", "add", "pop", "terminate")
BODY = bytes.fromhex("0054004b071411")


# ---------------------------------------------------------------- SC2: encoding

def test_authored_script_encodes_to_the_exact_contract_bytes():
    """SC2. The production codec, not a literal, produces the authored body."""
    assert assemble_source(SOURCE, BUU) == BODY


def test_authored_script_round_trips_through_the_production_codec():
    """SC2. Fully covered - no opaque bytes - and re-assembles identically."""
    ir = disassemble(BODY, (Entry("authored", 0),), BUU)
    assert ir.opaque == ()
    assert assemble(ir) == BODY
    assert [i.opcode for b in ir.blocks for i in b.instructions] == [0x00, 0x00, 0x07, 0x14, 0x11]


def test_authored_script_uses_only_confirmed_rom_opcodes():
    """Nothing authored here rests on an opcode the toolkit merely guessed."""
    ir = disassemble(BODY, (Entry("authored", 0),), BUU)
    for block in ir.blocks:
        for instruction in block.instructions:
            assert BUU.lookup(instruction.opcode).evidence.value == "CONFIRMED_ROM"


@pytest.mark.parametrize("source, reason", [
    ((), "at least one instruction"),
    (("nonsense",), "unknown instruction"),
    (("add 1",), "takes no operand"),
    (("push_byte",), "exactly one operand"),
    (("push_byte 256",), "unsigned byte"),
    (("push_byte x",), "must be an integer"),
    (("branch_forward 4",), "does not support"),
    (("push_signed_magnitude",), "exactly one operand"),
    (("push_many 2 1",), "disagrees"),
])
def test_authored_script_refuses_what_it_cannot_encode_exactly(source, reason):
    """A body the codec cannot express is refused by name, never mis-encoded."""
    with pytest.raises(ScriptError, match=reason):
        assemble_source(source, BUU)


# ------------------------------------------------- SC1: author-facing declaration

def test_authored_behavior_declares_a_stable_semantic_identity(project):
    """SC1. The behavior is named by project identity, never by a ROM address."""
    clone = add(project, name="beh", behavior="map:0000/authored:beh/behavior", script=list(SOURCE))
    assert clone.behavior == "map:0000/authored:beh/behavior"
    assert clone.authored_behavior
    assert clone.script == SOURCE
    # Nothing in the declaration is physical.
    assert not any(part.startswith("0x") for part in clone.behavior.split("/"))


def test_authored_behavior_survives_the_project_round_trip(project):
    """SC1. It is written to TOML and read back as the same declaration."""
    add(project, name="beh", behavior="map:0000/authored:beh/behavior", script=list(SOURCE))
    document = load_toml((project / "maps/maps.toml").read_text())
    row = document["map"]["map:0000"]["authored_placements"]["map:0000/authored:beh"]
    assert row["behavior"] == "map:0000/authored:beh/behavior"
    assert row["script"] == list(SOURCE)
    reloaded, = read_project(project).maps[0]["authored_placements"]
    assert reloaded.script == SOURCE and reloaded.authored_behavior


def test_authored_identity_is_stable_across_positions_and_templates(project):
    """SC1. Identity is the project's name, so moving the entity does not move it."""
    a = AuthoredPlacement("map:0000/authored:beh", 0, "map:0000/placement:0000", 1, 2,
                          behavior="map:0000/authored:beh/behavior", script=SOURCE)
    b = replace(a, position_low=999, position_high=7,
                clone_from="map:0000/placement:0001")
    assert a.behavior == b.behavior == "map:0000/authored:beh/behavior"


def test_a_script_without_an_authored_behavior_is_refused():
    """The two halves are one declaration; a stray script cannot be ignored."""
    with pytest.raises(ProjectValidationError, match="requires behavior"):
        AuthoredPlacement("map:0000/authored:beh", 0, "map:0000/placement:0000", 1, 2,
                          behavior="map:0428/placement:0000/descriptor", script=SOURCE)


def test_an_authored_behavior_without_a_script_is_refused():
    with pytest.raises(ProjectValidationError, match="requires a script body"):
        AuthoredPlacement("map:0000/authored:beh", 0, "map:0000/placement:0000", 1, 2,
                          behavior="map:0000/authored:beh/behavior")


def test_a_behavior_naming_another_records_authored_body_is_refused():
    """An authored behavior belongs to the record that declares it, and no other."""
    with pytest.raises(ProjectValidationError, match="behavior must name"):
        AuthoredPlacement("map:0000/authored:beh", 0, "map:0000/placement:0000", 1, 2,
                          behavior="map:0000/authored:other/behavior", script=SOURCE)


@pytest.mark.parametrize("script", [[], "push_byte 1", [""], [5], ["  "]])
def test_a_malformed_script_declaration_is_refused(script):
    with pytest.raises(ProjectValidationError, match="non-empty list of instruction strings"):
        AuthoredPlacement("map:0000/authored:beh", 0, "map:0000/placement:0000", 1, 2,
                          behavior="map:0000/authored:beh/behavior", script=script)


def test_a_raw_rom_address_is_still_not_an_authoring_api():
    """TOOLKIT-030's refusal is not weakened by the new identity form."""
    for behavior in ("0x0808D788", "map:0000/authored:beh", "134600000"):
        with pytest.raises(ProjectValidationError, match="behavior must name"):
            AuthoredPlacement("map:0000/authored:beh", 0, "map:0000/placement:0000", 1, 2,
                              behavior=behavior, script=SOURCE)


def test_an_unknown_field_is_still_refused(project):
    """`script` joins the closed field set; it does not open it."""
    from tools.webfoot.project import ProjectLoadError
    add(project, name="beh", behavior="map:0000/authored:beh/behavior", script=list(SOURCE))
    rewrite(project, lambda m: m["authored_placements"]["map:0000/authored:beh"]
            .update(descriptor_address="0x0808D788"))
    with pytest.raises(ProjectLoadError, match="structural fabrication unsupported"):
        read_project(project)
