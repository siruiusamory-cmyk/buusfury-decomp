"""DECOMP-LIFT-FLAGMASK-001: the first consumer of the gathered mask.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.
"""

from __future__ import annotations

import json
import re

import pytest

from buusfury import identity, lift


def test_the_flagmask_target_is_registered():
    target = lift.get_target("flagmask")
    assert target.ticket == "DECOMP-LIFT-FLAGMASK-001"
    assert target.rom_address == 0x08003310
    assert target.probe_translation_unit == "flagmask_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter_flagmask.c"
    assert target.semantic_minimum_checks == 22
    assert target.host_build_bits == 32


def test_every_earlier_target_survives():
    ids = [t.id for t in lift.load_targets()]
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith", "use",
                    "effect", "flagread", "booluse", "clear", "gather"):
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
# the boundary, and its connection to the gather
# ---------------------------------------------------------------------------
def test_the_boundary_is_derived_and_agrees(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "flagmask_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"], row["instructions"]) \
        == ("0x08003310", "0x08003366", 86, 41)
    assert row["terminators"] == ["0x08003364"]
    assert row["gaps"] == []


def test_it_begins_exactly_where_the_gather_ends(rom_bytes):
    """This is what makes it the mask's first consumer rather than a neighbour."""
    gather = lift.derive_unit_boundaries(rom_bytes, "gather_tu")["functions"][0]
    consumer = lift.derive_unit_boundaries(rom_bytes, "flagmask_tu")["functions"][0]
    assert gather["end"] == consumer["start"] == "0x08003310"


def test_it_is_native_dispatch_entry_187(rom_bytes):
    from buusfury import gba

    base = gba.ROM_BASE
    hits = []
    for index in range(lift.derive_native_table(rom_bytes)["entries"]):
        address = lift.NATIVE_TABLE + index * 4
        value = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
        if value and (value & ~1) == lift.FLAGMASK_ENTRY:
            hits.append((index, value))
    assert hits == [(187, 0x08003311)], hits


# ---------------------------------------------------------------------------
# stack behaviour
# ---------------------------------------------------------------------------
def test_it_pops_three_and_pushes_nothing(rom_bytes):
    application = lift.derive_mask_application(rom_bytes)
    assert application["pops"] == 3
    assert application["pushes"] == 0
    assert application["consumes"] == 3
    assert application["produces"] == 0
    assert application["net_counter_delta"] == -3


def test_the_mask_is_the_stack_top_and_is_not_put_back(rom_bytes):
    application = lift.derive_mask_application(rom_bytes)
    assert application["mask_is_the_stack_top"] is True
    assert application["writes_the_mask_back_to_the_stack"] is False
    assert application["popped_in_order"][0] == "mask (the stack top)"
    assert application["popped_in_order"] == ["mask (the stack top)", "width", "bit offset"]


def test_the_three_pop_sites_are_found_in_the_instruction_stream(rom_bytes):
    application = lift.derive_mask_application(rom_bytes)
    assert application["pop_sites"] == ["0x0800331C", "0x08003326", "0x08003330"], \
        application["pop_sites"]


# ---------------------------------------------------------------------------
# mask interpretation
# ---------------------------------------------------------------------------
def test_the_mask_is_applied_per_bit(rom_bytes):
    application = lift.derive_mask_application(rom_bytes)
    assert "bit i of the mask becomes the STATE" in application["mask_interpretation"]
    assert "offset + i" in application["mask_interpretation"]


def test_it_calls_both_the_setter_and_the_clearer(rom_bytes):
    application = lift.derive_mask_application(rom_bytes)
    assert application["calls_the_setter"] is True
    assert application["calls_the_clearer"] is True
    assert application["call_count"] == 2
    assert {c["target"] for c in application["calls"]} == {"0x08004380", "0x08004396"}


def test_the_bit_under_test_is_brought_down_each_iteration(rom_bytes):
    application = lift.derive_mask_application(rom_bytes)
    assert application["tests_mask_bit_0_via_lsls_31"] is True
    assert application["shifts_the_mask_with_asrs"] is True


def test_both_clamps_and_both_signed_branches_are_recorded(rom_bytes):
    application = lift.derive_mask_application(rom_bytes)
    assert application["clamp_1_is_signed"] is True
    assert application["width_compared_signed"] is True
    assert application["shifts_the_mask_with_asrs"] is True
    assert "width_32_edge_case" in application


def test_the_width_32_edge_case_is_stated(rom_bytes):
    application = lift.derive_mask_application(rom_bytes)
    text = application["width_32_edge_case"]
    assert "ZERO for an amount of 32" in text
    assert "0xFFFFFFFF" in text


def test_there_is_no_bounds_check(rom_bytes):
    application = lift.derive_mask_application(rom_bytes)
    assert application["has_bounds_check"] is False
    assert "compared against any size" in application["has_bounds_check_evidence"]


def test_the_consequence_names_it_as_the_gathers_counterpart(rom_bytes):
    application = lift.derive_mask_application(rom_bytes)
    assert "counterpart of the gather" in application["consequence"]


# ---------------------------------------------------------------------------
# source discipline
# ---------------------------------------------------------------------------
def test_the_source_models_the_thumb_shift_instead_of_using_c_shift():
    """The width-32 case turns on ARM LSL giving 0 for amounts >= 32, where C's
    shift is undefined and MSVC yields 1."""
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_flagmask.c").read_text("utf-8")
    assert "flagmask_thumb_lsls_1" in source
    assert "amount >= 32u" in source
    assert "undefined" in source
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "1u << width" not in code, "the raw C shift must not be used"


def test_the_source_adds_no_guard_and_no_name():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_flagmask.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "case " not in code
    assert "assert" not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_source_consumes_the_three_values_in_order():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_flagmask.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert code.index("mask = state[") < code.index("width = state[") < code.index("offset = state[")


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_flagmask.c").read_text("utf-8")
    assert "../ByteCodeInterpreter_flagmask.c" in shim
    assert "sub_08003310(" not in shim


@pytest.mark.parametrize("checks,expected", [(22, "PROVEN"), (21, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=22)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("flagmask", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted):
    _, document = lifted
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 22
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted):
    _, document = lifted
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False


def test_both_callees_are_bound_to_their_original_addresses(lifted):
    _, document = lifted
    bound = document["modern_build"]["external_calls_bound_to_original_addresses"]
    assert bound == {"sub_08004380": "0x08004380", "sub_08004396": "0x08004396"}


def test_the_committed_report_matches_a_fresh_run(lifted):
    data, _ = lifted
    result = lift.verify_report(data, "flagmask")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("flagmask").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
