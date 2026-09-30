"""DECOMP-LIFT-NATIVE178-001: native dispatch slot 178 at 0x08003030.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.
"""

from __future__ import annotations

import json
import re

import pytest

from buusfury import identity, lift


def test_the_target_is_registered():
    target = lift.get_target("native178")
    assert target.ticket == "DECOMP-LIFT-NATIVE178-001"
    assert target.rom_address == 0x08003030
    assert target.probe_translation_unit == "native178_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter_native178.c"
    assert target.semantic_minimum_checks == 22
    assert target.host_build_bits == 32


def test_every_earlier_target_survives():
    """A FLOOR, not an exact count.

    The ticket that added this file pinned `== 14`, and the very next ticket's
    fifteenth target broke it - the same trap this file's own ticket fixed four
    times elsewhere. A ticket that does not own the registry must never pin its size.
    """
    ids = [t.id for t in lift.load_targets()]
    assert len(ids) >= 14, ids
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith",
                    "use", "effect", "flagread", "booluse", "clear", "gather",
                    "flagmask", "native178"):
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
# 1. identity, static and runtime
# ---------------------------------------------------------------------------
def test_the_static_table_word_masks_to_the_runtime_anchor(rom_bytes):
    """The ticket's reason for existing: static and runtime must agree."""
    identity_row = lift.derive_native_slot(rom_bytes, 178)
    assert identity_row["table_address"] == "0x08055360"
    assert identity_row["raw_word"] == "0x08003031"
    assert identity_row["thumb_bit_set"] is True
    assert identity_row["normalized_address"] == "0x08003030"
    assert identity_row["runtime_capture_address"] == "0x08003030"
    assert identity_row["agrees_with_the_runtime_capture"] is True


def test_exactly_one_table_entry_points_here(rom_bytes):
    identity_row = lift.derive_native_slot(rom_bytes, 178)
    assert identity_row["entries_pointing_here"] == [178]
    assert identity_row["identity_is_unique"] is True


def test_the_runtime_capture_is_scoped_to_identity_only(rom_bytes):
    """It must not be presented as semantic evidence."""
    scope = lift.derive_native_slot(rom_bytes, 178)["runtime_evidence_scope"]
    assert "IDENTITY" in scope
    assert "nothing about the" in scope
    assert "no semantic claim" in scope


# ---------------------------------------------------------------------------
# 2. the boundary
# ---------------------------------------------------------------------------
def test_the_boundary_is_derived_and_agrees(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "native178_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"], row["instructions"])         == ("0x08003030", "0x08003070", 64, 30)
    assert row["terminators"] == ["0x0800306E"]
    assert row["gaps"] == []


def test_it_has_a_literal_pool_with_one_word(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "native178_tu")
    assert evidence["has_literal_pool"] is True
    assert evidence["pool_extent"].startswith("0x080031B4"), evidence["pool_extent"]


# ---------------------------------------------------------------------------
# 3. the entry contract
# ---------------------------------------------------------------------------
def test_r0_is_the_context_and_r1_is_never_read(rom_bytes):
    contract = lift.derive_native178_stack(rom_bytes)
    assert contract["reads_incoming_r1"] is False
    assert "overwritten before it can be read" in contract["r1_evidence"]
    assert contract["context_fields_used"] == ["+0x00 the counter", "+0x04+4*i the values"]


# ---------------------------------------------------------------------------
# 4. stack behaviour
# ---------------------------------------------------------------------------
def test_three_pops_and_no_push(rom_bytes):
    contract = lift.derive_native178_stack(rom_bytes)
    assert contract["pops"] == 3
    assert contract["pushes_to_the_vm_stack"] == 0
    assert contract["consumes"] == 3
    assert contract["produces"] == 0
    assert contract["net_counter_delta"] == -3


def test_the_pops_are_read_top_first(rom_bytes):
    contract = lift.derive_native178_stack(rom_bytes)
    assert contract["pops_top_first"] == [
        "values[count-1]", "values[count-2]", "values[count-3]"
    ]


def test_the_local_array_is_built_on_the_frame_in_reverse_stack_order(rom_bytes):
    contract = lift.derive_native178_stack(rom_bytes)
    assert "local[1] gets values[count-1]" in contract["local_array_order"]
    assert "DEEPEST-OF-THE-TWO FIRST" in contract["local_array_order"]
    assert len(contract["local_array_stores"]) == 2


def test_there_is_no_stack_guard(rom_bytes):
    contract = lift.derive_native178_stack(rom_bytes)
    assert contract["has_stack_guard"] is False
    assert "walk below the context" in contract["has_stack_guard_evidence"]


# ---------------------------------------------------------------------------
# 5. the calls and the concrete effect
# ---------------------------------------------------------------------------
def test_the_two_calls_and_their_arguments(rom_bytes):
    contract = lift.derive_native178_stack(rom_bytes)
    assert contract["call_count"] == 2
    assert [c["target"] for c in contract["calls"]] == ["0x0802BFBC", "0x0801191A"]
    assert contract["first_call_args"] == (
        "r0 = values[count-3], r1 = &local[0] (a two-element array)"
    )
    assert contract["owner_word_offset"] == "0x18"
    assert "*(0x08054FBC + 0x18)" in contract["second_call_args"]


def test_the_concrete_effect_is_the_engine_call(rom_bytes):
    contract = lift.derive_native178_stack(rom_bytes)
    assert "pushes nothing back" in contract["effect"]
    assert "*(0x08054FBC + 0x18)" in contract["effect"]


def test_the_owner_word_is_the_iwram_object(rom_bytes):
    """The table entry at +0x18 is the object the effect targets."""
    layout = identity.REPO_ROOT / "config" / "ewram_layout.json"
    if not layout.is_file():
        pytest.skip("the static layout artifact is not present")
    entries = json.loads(layout.read_text("utf-8"))["entries"]
    row = next(e for e in entries if e["table_offset"] == "0x18")
    assert row["value"] == "0x03001C4C", "the +0x18 object is the IWRAM object"


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_declares_both_callees_and_reconstructs_neither():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_native178.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "extern u32 sub_0802BFBC(" in code
    assert "extern void sub_0801191A(" in code
    assert "u32 sub_0802BFBC(" not in code.replace("extern u32 sub_0802BFBC(", "")
    assert "void sub_0801191A(" not in code.replace("extern void sub_0801191A(", "")


def test_the_source_adds_no_guard_and_no_name():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_native178.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "case " not in code
    assert "assert" not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_source_marks_the_cursor_unused():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_native178.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "(void)cursor_slot;" in code


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_native178.c").read_text("utf-8")
    assert "../ByteCodeInterpreter_native178.c" in shim
    assert "sub_08003030(" not in shim


def test_the_source_records_the_static_and_runtime_agreement():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_native178.c").read_text("utf-8")
    assert "0x08003031" in source
    assert "runtime capture" in source
    assert "IDENTITY" in source


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
    return rom_bytes, lift.run_lift("native178", rom_bytes, toolchain)


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


def test_the_identity_derivation_is_in_the_report(lifted):
    _, document = lifted
    row = document["boundary_evidence"]["slot_identity"]
    assert row["raw_word"] == "0x08003031"
    assert row["agrees_with_the_runtime_capture"] is True
    assert row["identity_is_unique"] is True


def test_the_stack_contract_is_in_the_report(lifted):
    _, document = lifted
    contract = document["boundary_evidence"]["stack_contract"]
    assert contract["pops"] == 3
    assert contract["pushes_to_the_vm_stack"] == 0
    assert contract["call_count"] == 2


def test_no_match_is_claimed(lifted):
    _, document = lifted
    comparison = document["comparison"]
    assert comparison["is_a_match_claim"] is False
    assert comparison["byte_identical"] is False
    assert comparison["differing_bytes_in_overlap"] > 0


def test_the_sizes_happen_to_agree_but_that_is_not_a_match(lifted):
    """Worth recording precisely because equal size is NOT a match."""
    _, document = lifted
    row = document["functions"][0]
    assert row["original"]["size"] == row["modern"]["size"] == 64
    assert row["original"]["instructions"] == row["modern"]["instructions"] == 30
    assert document["comparison"]["is_a_match_claim"] is False


def test_both_callees_are_bound_to_their_original_addresses(lifted):
    _, document = lifted
    bound = document["modern_build"]["external_calls_bound_to_original_addresses"]
    assert bound == {"sub_0802BFBC": "0x0802BFBC", "sub_0801191A": "0x0801191A"}


def test_the_committed_report_matches_a_fresh_run(lifted):
    data, _ = lifted
    result = lift.verify_report(data, "native178")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("native178").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
