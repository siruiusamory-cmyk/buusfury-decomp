"""DECOMP-LIFT-SCRIPT-FLAGSTATE-001: the clearer and the gather loop.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.
"""

from __future__ import annotations

import json
import re

import pytest

from buusfury import identity, lift


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------
def test_both_targets_are_registered():
    clear = lift.get_target("clear")
    gather = lift.get_target("gather")
    assert clear.ticket == gather.ticket == "DECOMP-LIFT-FLAGSTATE-001"
    assert clear.rom_address == 0x08004396
    assert gather.rom_address == 0x080032C2
    assert clear.semantic_minimum_checks == 18
    # Raised from 20 by DECOMP-FLAGSTATE-SHIFT-FIX-001, which added the explicit
    # ARM7TDMI register-LSL cases.
    assert gather.semantic_minimum_checks == 31
    for target in (clear, gather):
        assert target.host_build_bits == 32


def test_every_earlier_target_survives():
    ids = [t.id for t in lift.load_targets()]
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith",
                    "use", "effect", "flagread", "booluse"):
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
# the clearer
# ---------------------------------------------------------------------------
def test_the_clears_boundary_is_derived_and_agrees(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "clear_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"], row["instructions"]) \
        == ("0x08004396", "0x080043AC", 22, 11)
    assert row["terminators"] == ["0x080043AA"]
    assert evidence["has_literal_pool"] is False


def test_the_trio_tiles_contiguously(rom_bytes):
    reader = lift.derive_unit_boundaries(rom_bytes, "flagread_tu")["functions"][0]
    setter = lift.derive_unit_boundaries(rom_bytes, "effect_tu")["functions"][0]
    clearer = lift.derive_unit_boundaries(rom_bytes, "clear_tu")["functions"][0]
    assert reader["end"] == setter["start"] == "0x08004380"
    assert setter["end"] == clearer["start"] == "0x08004396"


def test_the_clearer_clears_because_of_bics(rom_bytes):
    """Derived on its own evidence: the differing instruction is what decides."""
    trio = {row["entry"]: row for row in lift.derive_flag_state(rom_bytes)["trio"]}
    assert trio["0x08004364"]["combining_instruction"] == "ands"
    assert trio["0x08004380"]["combining_instruction"] == "orrs"
    assert trio["0x08004396"]["combining_instruction"] == "bics"


def test_the_clearer_is_a_read_modify_write(rom_bytes):
    trio = {row["entry"]: row for row in lift.derive_flag_state(rom_bytes)["trio"]}
    clearer = trio["0x08004396"]
    assert clearer["reads_byte"] is True
    assert clearer["writes_byte"] is True
    assert clearer["read_modify_write"] is True
    assert clearer["calls"] == 0


def test_the_trio_shares_one_contract(rom_bytes):
    state = lift.derive_flag_state(rom_bytes)
    assert state["trio_contract_is_shared"] is True
    assert state["trio_has_no_bounds_check"] is True
    for row in state["trio"]:
        assert row["byte_index_shift"] == 3
        assert row["byte_index_shift_is_arithmetic"] is True
        assert row["object_offset"] == 0x50
        assert row["field_offset"] == 5
        assert row["has_bounds_check"] is False


def test_the_shared_contract_says_base_plus_0x55(rom_bytes):
    contract = lift.derive_flag_state(rom_bytes)["trio_shared_contract"]
    assert contract["storage_base"] == "base + 0x55"
    assert contract["entry_size_bytes"] == 1


# ---------------------------------------------------------------------------
# the gather loop
# ---------------------------------------------------------------------------
def test_the_gather_boundary_is_derived_and_agrees(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "gather_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"], row["instructions"]) \
        == ("0x080032C2", "0x08003310", 78, 38)
    assert row["terminators"] == ["0x0800330E"]


def test_the_gather_consumes_two_and_produces_one(rom_bytes):
    gather = lift.derive_flag_state(rom_bytes)["gather"]
    assert gather["consumes"] == 2
    assert gather["produces"] == 1
    assert gather["net_counter_delta"] == -1
    assert gather["pops"] == 2
    assert gather["pushes"] == 1


def test_the_offset_is_added_to_the_index(rom_bytes):
    """The detail that fixes the second operand's meaning: the reader is called
    with `offset + n`, so the offset is a BIT NUMBER, not a byte index."""
    gather = lift.derive_flag_state(rom_bytes)["gather"]
    assert gather["offset_is_added_to_the_index"] is True
    assert lift.derive_flag_state(rom_bytes)["gather_note"].count("offset + n") == 1


def test_the_bound_is_compared_as_signed(rom_bytes):
    """A bound of zero or less must skip the loop entirely."""
    gather = lift.derive_flag_state(rom_bytes)["gather"]
    assert gather["bound_compared_signed"] is True


def test_the_mask_arithmetic_is_recorded(rom_bytes):
    gather = lift.derive_flag_state(rom_bytes)["gather"]
    assert gather["mask_accumulator_cleared_at_entry"] is True
    assert gather["mask_built_with"] == "orrs"
    assert "shift_amount_is_modulo_32" not in gather, "that claim was wrong and is removed"
    assert gather["shift_is_register_controlled"] is True
    assert gather["shift_amount_at_or_above_32_yields_zero"] is True
    assert gather["shift_bits_above_31_can_never_be_set"] is True
    assert "ZERO" in gather["shift_amount_rule"]
    assert gather["loop_calls_the_reader"] is True


def test_the_mask_and_its_destination_are_stated(rom_bytes):
    state = lift.derive_flag_state(rom_bytes)
    assert "offset + n" in state["gather_mask"]
    assert "bound-1" in state["gather_mask"]
    assert "PUSHED" in state["gather_mask_destination"]
    assert "VM value stack" in state["gather_mask_destination"]


def test_the_gather_has_no_bounds_check(rom_bytes):
    gather = lift.derive_flag_state(rom_bytes)["gather"]
    assert gather["has_bounds_check"] is False
    assert "no size is reachable" in gather["has_bounds_check_evidence"]


def test_the_call_site_is_the_one_flagread_recorded(rom_bytes):
    gather = lift.derive_flag_state(rom_bytes)["gather"]
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    flagread = lift.run_lift("flagread", rom_bytes, toolchain)
    assert gather["call_site"] in flagread["boundary_evidence"]["bit_field_read"]["consumed_by"]


# ---------------------------------------------------------------------------
# array extent: bounded honestly, not guessed
# ---------------------------------------------------------------------------
def test_the_array_extent_is_a_lower_bound_only(rom_bytes):
    extent = lift.derive_flag_state(rom_bytes)["array_extent"]
    assert extent["proven_lower_bound_bytes"] == 1
    assert extent["proven_lower_bound_bits"] == 8
    assert extent["upper_bound"] is None, "no static upper bound is derivable"
    assert extent["kind"] == "bounded_only_below"
    assert extent["no_bounds_check_anywhere"] is True
    assert "runtime values" in extent["upper_bound_reason"]


# ---------------------------------------------------------------------------
# source discipline
# ---------------------------------------------------------------------------
def test_the_clearer_source_adds_no_guard_and_returns_nothing():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_clear.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "void sub_08004396(void *base, u32 value)" in code
    assert "bics" in source.replace("`bics`", "bics")
    assert "return" not in code.split("sub_08004396")[1], "no result is invented"
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_gather_source_uses_the_same_shifts_as_the_reader():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_gather.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "offset + n" in code
    # DECOMP-FLAGSTATE-SHIFT-FIX-001: the amount is a runtime value, so the
    # architectural rule is modelled rather than left to C's shift.
    assert "gather_thumb_lsl_1(n)" in code
    assert "amount >= 32u" in code
    assert "1u << n" not in code, "the raw C shift must not be used for a runtime amount"
    assert "sub_08004364" in code
    assert "void sub_08004364" not in code, "the reader is reconstructed elsewhere"


def test_both_probe_paths_are_shims():
    for name, entry in (("clear", "sub_08004396"), ("gather", "sub_080032C2")):
        shim = (identity.REPO_ROOT / "src" / "probes" / f"ByteCodeInterpreter_{name}.c").read_text("utf-8")
        assert f"../ByteCodeInterpreter_{name}.c" in shim
        assert f"{entry}(" not in shim


@pytest.mark.parametrize("checks,minimum,expected", [
    (18, 18, "PROVEN"), (17, 18, "PARTIAL"), (31, 31, "PROVEN"), (30, 31, "PARTIAL"),
])
def test_the_minimums_are_enforced(checks, minimum, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=minimum)
    assert status == expected


# ---------------------------------------------------------------------------
# the full reports
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def toolchain():
    found = lift.discover_modern_toolchain()
    if found is None:
        pytest.skip("no modern ARM toolchain available")
    return found


def test_all_three_verdicts_are_separate_for_both(rom_bytes, toolchain):
    for target_id in ("clear", "gather"):
        document = lift.run_lift(target_id, rom_bytes, toolchain)
        verdicts = document["verdicts"]
        assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
        assert verdicts["semantic"]["status"] == "PROVEN", (target_id, verdicts["semantic"])
        assert verdicts["semantic"]["failures"] == 0
        assert verdicts["modern_build"]["status"] == "PASS", (target_id, verdicts["modern_build"])
        assert verdicts["ads_match"]["status"] == "BLOCKED"
        assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True
        assert verdicts["semantic"]["checks"] >= lift.get_target(target_id).semantic_minimum_checks


def test_no_match_is_claimed(rom_bytes, toolchain):
    for target_id in ("clear", "gather"):
        document = lift.run_lift(target_id, rom_bytes, toolchain)
        assert document["comparison"]["is_a_match_claim"] is False
        assert document["comparison"]["byte_identical"] is False


def test_the_gathers_reader_call_is_bound(rom_bytes, toolchain):
    document = lift.run_lift("gather", rom_bytes, toolchain)
    bound = document["modern_build"]["external_calls_bound_to_original_addresses"]
    assert bound == {"sub_08004364": "0x08004364"}


def test_the_clearer_has_no_external_calls(rom_bytes, toolchain):
    document = lift.run_lift("clear", rom_bytes, toolchain)
    assert document["modern_build"]["external_calls_bound_to_original_addresses"] == {}


def test_both_committed_reports_match_a_fresh_run(rom_bytes, toolchain):
    for target_id in ("clear", "gather"):
        result = lift.verify_report(rom_bytes, target_id)
        if result["exempted"]:
            assert "no host C compiler" in result["exempted"][0]
        assert result["ok"], (target_id, result["problems"][:8])


def test_both_committed_reports_are_environment_independent():
    for target_id in ("clear", "gather"):
        raw = lift.report_path_for(target_id).read_bytes()
        assert b"\r\n" not in raw
        text = raw.decode("utf-8")
        assert "devkitPro" not in text
        assert "buusfury-decomp" not in text
        assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
