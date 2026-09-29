"""DECOMP-LIFT-SCRIPT-EFFECT-001: sub_08004380, the VM value's effect.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.
"""

from __future__ import annotations

import hashlib
import json
import re

import pytest

from buusfury import identity, lift


def test_the_effect_target_is_registered():
    target = lift.get_target("effect")
    assert target.probe_translation_unit == "effect_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter_effect.c"
    assert target.ticket == "DECOMP-LIFT-SCRIPT-EFFECT-001"
    assert target.rom_address == 0x08004380
    assert target.semantic_minimum_checks == 19


def test_every_earlier_target_survives():
    ids = [t.id for t in lift.load_targets()]
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith", "use"):
        assert earlier in ids, earlier


@pytest.fixture(scope="module")
def rom_bytes():
    try:
        rom = identity.resolve_baserom()
        identity.verify(rom)
    except Exception as exc:  # noqa: BLE001 - the fixture's whole job is to skip
        pytest.skip(f"no canonical baserom available: {exc}")
    return rom.read_bytes()


# ---------------------------------------------------------------------------
# the derived boundary and the mechanical bit-set proof
# ---------------------------------------------------------------------------
def test_the_boundary_is_derived_and_agrees(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "effect_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"], row["instructions"]) \
        == ("0x08004380", "0x08004396", 22, 11)
    assert row["terminators"] == ["0x08004394"]
    assert row["gaps"] == []


def test_it_is_a_leaf_with_no_pool(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "effect_tu")
    assert evidence["has_literal_pool"] is False
    assert evidence["pool_extent"] is None


def test_the_bit_set_arithmetic_is_read_from_the_instructions(rom_bytes):
    write = lift.derive_bit_field_write(rom_bytes)
    assert write["byte_index_shift"] == 3
    assert write["byte_index_shift_is_arithmetic"] is True, \
        "asrs replicates the sign bit, which decides where a negative-looking index lands"
    assert write["bit_index_mask_bits"] == 3
    assert write["object_offset"] == 0x50
    assert write["field_offset_from_object_offset"] == 5


def test_it_is_a_read_modify_write_with_no_calls_or_literals(rom_bytes):
    write = lift.derive_bit_field_write(rom_bytes)
    assert write["read_modify_write"] is True
    assert write["read_count"] >= 1
    assert write["or_count"] >= 1
    assert write["write_count"] >= 1
    assert write["calls"] == 0
    assert write["literal_slots"] == 0


def test_there_is_no_bounds_check(rom_bytes):
    write = lift.derive_bit_field_write(rom_bytes)
    assert write["has_bounds_check"] is False
    assert "no compare against a size" in write["has_bounds_check_evidence"]


def test_the_effect_statement_names_the_byte_and_the_bit(rom_bytes):
    write = lift.derive_bit_field_write(rom_bytes)
    assert "(value & 7)" in write["effect"]
    assert "(value >> 3)" in write["effect"]
    assert "0x55" in write["effect"]
    assert "preserving" in write["effect"]


def test_the_negative_index_behaviour_is_recorded(rom_bytes):
    write = lift.derive_bit_field_write(rom_bytes)
    assert "arithmetic" in write["negative_index_behaviour"]
    assert "before the base" in write["negative_index_behaviour"]


# ---------------------------------------------------------------------------
# the argument contract, proven from the caller (previous ticket)
# ---------------------------------------------------------------------------
def test_the_caller_contract_is_carried_into_this_report(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    document = lift.run_lift("effect", rom_bytes, toolchain)
    called_from = document["boundary_evidence"]["called_from"]
    assert called_from["routine"] == "sub_080007E6"
    assert called_from["site"] == "0x080007F8"
    assert "popped from the VM stack" in called_from["arguments"]


def test_the_callers_own_report_still_names_this_routine(rom_bytes):
    """The two tickets agree: entry 29's report must still bind its callee here."""
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    use = lift.run_lift("use", rom_bytes, toolchain)
    bound = use["modern_build"]["external_calls_bound_to_original_addresses"]
    assert bound == {"sub_08004380": "0x08004380"}


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_models_the_arithmetic_shift_explicitly():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_effect.c").read_text("utf-8")
    assert "arithmetic_shift_right_3" in source
    assert "implementation-defined" in source
    assert "0xE0000000u" in source, "the sign bits must be replicated explicitly"


def test_the_source_adds_no_bounds_or_null_check():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_effect.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "case " not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other
    # No guard of any kind.
    for guard in ("if (base ==", "if (value >", "if (byte_index >", "assert"):
        assert guard not in code, guard


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_effect.c").read_text("utf-8")
    assert "#include" in shim and "../ByteCodeInterpreter_effect.c" in shim
    assert "sub_08004380(" not in shim


@pytest.mark.parametrize("checks,expected", [(19, "PROVEN"), (18, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=19)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted_effect(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("effect", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted_effect):
    _, document = lifted_effect
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 19
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted_effect):
    _, document = lifted_effect
    comparison = document["comparison"]
    assert comparison["is_a_match_claim"] is False
    assert comparison["byte_identical"] is False
    assert comparison["differing_bytes_in_overlap"] > 0


def test_it_pairs_by_name_with_no_external_calls(lifted_effect):
    _, document = lifted_effect
    row = document["functions"][0]
    assert row["name"] == "sub_08004380"
    assert len(row["original"]["calls"]) == len(row["modern"]["calls"]) == 0
    assert row["original"]["returns"] == row["modern"]["returns"] == 1
    assert document["modern_build"]["external_calls_bound_to_original_addresses"] == {}


def test_the_committed_report_matches_a_fresh_run(lifted_effect):
    data, _ = lifted_effect
    result = lift.verify_report(data, "effect")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("effect").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
