"""DECOMP-LIFT-SCRIPT-FLAGREAD-001: the bit-array reader.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.
"""

from __future__ import annotations

import hashlib
import json
import re

import pytest

from buusfury import identity, lift


def test_the_flagread_target_is_registered():
    target = lift.get_target("flagread")
    assert target.probe_translation_unit == "flagread_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter_flagread.c"
    assert target.ticket == "DECOMP-LIFT-SCRIPT-FLAGREAD-001"
    assert target.rom_address == 0x08004364
    assert target.semantic_minimum_checks == 17


def test_every_earlier_target_survives():
    ids = [t.id for t in lift.load_targets()]
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith", "use", "effect"):
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
# the derived boundary
# ---------------------------------------------------------------------------
def test_the_boundary_is_derived_and_agrees(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "flagread_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"], row["instructions"]) \
        == ("0x08004364", "0x08004380", 28, 14)
    assert row["terminators"] == ["0x0800437A", "0x0800437E"]
    assert row["gaps"] == []


def test_it_is_a_leaf_with_no_pool(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "flagread_tu")
    assert evidence["has_literal_pool"] is False


def test_the_trio_tiles_contiguously(rom_bytes):
    """reader, setter, clearer are adjacent, so the three boundaries confirm one
    another."""
    reader = lift.derive_unit_boundaries(rom_bytes, "flagread_tu")["functions"][0]
    setter = lift.derive_unit_boundaries(rom_bytes, "effect_tu")["functions"][0]
    assert reader["end"] == setter["start"] == "0x08004380"


# ---------------------------------------------------------------------------
# the bit-test proof
# ---------------------------------------------------------------------------
def test_the_index_split_matches_the_setters(rom_bytes):
    read = lift.derive_bit_field_read(rom_bytes)
    assert read["byte_index_shift"] == 3
    assert read["byte_index_shift_is_arithmetic"] is True
    assert read["bit_index_mask_bits"] == 3
    assert read["object_offset"] == 0x50
    assert read["field_offset"] == 5


def test_it_tests_the_bit_for_set(rom_bytes):
    read = lift.derive_bit_field_read(rom_bytes)
    assert read["tests_for_set"] is True
    assert read["test_mnemonic"] == "ands"


def test_it_writes_nothing(rom_bytes):
    """This is what makes it a reader, not the setter or the clearer."""
    read = lift.derive_bit_field_read(rom_bytes)
    assert read["writes_nothing"] is True
    assert read["store_count"] == 0


def test_it_returns_a_normalised_boolean(rom_bytes):
    read = lift.derive_bit_field_read(rom_bytes)
    assert read["returns_normalised_boolean"] is True
    assert 0 in read["return_values"] and 1 in read["return_values"]
    assert "returns 1 when bit" in read["read_semantics"]


def test_there_is_no_bounds_check(rom_bytes):
    read = lift.derive_bit_field_read(rom_bytes)
    assert read["has_bounds_check"] is False


def test_it_makes_no_calls_and_loads_no_literals(rom_bytes):
    read = lift.derive_bit_field_read(rom_bytes)
    assert read["calls"] == 0
    assert read["literal_slots"] == 0


# ---------------------------------------------------------------------------
# the consequence
# ---------------------------------------------------------------------------
def test_the_call_sites_are_re_derived_from_the_rom(rom_bytes):
    """The consequence must be measured, not remembered: the report re-derives
    its call sites by scanning for BL instructions targeting the entry."""
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    document = lift.run_lift("flagread", rom_bytes, toolchain)
    read = document["boundary_evidence"]["bit_field_read"]
    assert set(read["consumed_by"]) == {"0x080007C4", "0x080007DA", "0x080032EE"}, read["consumed_by"]
    assert "materialised into an engine slot" in read["consequence"]


def test_the_consequence_is_stated_without_naming_the_flag():
    read_source = (identity.REPO_ROOT / "docs" / "LIFT_FLAGREAD.md")
    if not read_source.is_file():
        pytest.skip("doc not written yet")
    text = read_source.read_text("utf-8")
    for other in ("Legacy of Goku", "LOGI", "LOGII"):
        assert other not in text, other


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_models_the_arithmetic_shift_and_writes_nothing():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_flagread.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "flagread_arithmetic_shift_right_3" in source
    assert "0xE0000000u" in source
    assert "const u8 *field" in source, "the byte must be read through a const pointer"
    assert "strb" not in code and "= (u8)" not in code
    assert "case " not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_flagread.c").read_text("utf-8")
    assert "#include" in shim and "../ByteCodeInterpreter_flagread.c" in shim
    assert "sub_08004364(" not in shim


@pytest.mark.parametrize("checks,expected", [(17, "PROVEN"), (16, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=17)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted_flagread(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("flagread", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted_flagread):
    _, document = lifted_flagread
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 17
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted_flagread):
    _, document = lifted_flagread
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False


def test_it_pairs_by_name_with_no_external_calls(lifted_flagread):
    _, document = lifted_flagread
    row = document["functions"][0]
    assert row["name"] == "sub_08004364"
    assert len(row["original"]["calls"]) == len(row["modern"]["calls"]) == 0
    # The ORIGINAL has two exits, one per branch target. The modern count is the
    # compiler's own control flow and is not pinned: only the original's shape is
    # a fact of the ROM.
    assert row["original"]["returns"] == 2
    assert row["modern"]["returns"] >= 1
    assert document["modern_build"]["external_calls_bound_to_original_addresses"] == {}


def test_the_committed_report_matches_a_fresh_run(lifted_flagread):
    data, _ = lifted_flagread
    result = lift.verify_report(data, "flagread")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("flagread").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
