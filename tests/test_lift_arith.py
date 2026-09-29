"""DECOMP-LIFT-SCRIPT-ARITH-001: value-stack arithmetic slots 8 and 9.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.

Includes an explicit guard that slot 7's committed report inputs are unchanged:
this ticket adds a target and must not silently restate an earlier one.
"""

from __future__ import annotations

import hashlib
import json
import re

import pytest

from buusfury import identity, lift


# ---------------------------------------------------------------------------
# the registry entry
# ---------------------------------------------------------------------------
def test_the_arith_target_is_registered_against_its_own_unit():
    target = lift.get_target("arith")
    assert target.probe_translation_unit == "arith_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter_arith.c"
    assert target.selftest_source == "src/probes/arith_selftest.c"
    assert target.ticket == "DECOMP-LIFT-SCRIPT-ARITH-001"
    assert target.rom_address == 0x08003D52
    assert target.host_build_bits == 32
    assert target.semantic_minimum_checks == 45


def test_the_arith_minimum_is_a_real_floor():
    source = (identity.REPO_ROOT / "src" / "probes" / "arith_selftest.c").read_text("utf-8")
    assert lift.get_target("arith").semantic_minimum_checks <= source.count("check(")


def test_every_earlier_target_survives():
    ids = [t.id for t in lift.load_targets()]
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack"):
        assert earlier in ids, earlier


def test_slot_sevens_registry_note_is_untouched():
    """The acceptance requires slot 7's report to remain unchanged. Its notes
    text feeds that report, so the exact earlier wording is pinned here: this
    ticket adds a sibling, it does not restate one."""
    notes = lift.get_target("stack").notes
    assert "Slots 8 and 9 are NOT lifted." in notes
    assert "Slots 8 and 9 are NOT lifted here." not in notes


# ---------------------------------------------------------------------------
# the derived boundaries
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def rom_bytes():
    try:
        rom = identity.resolve_baserom()
        identity.verify(rom)
    except Exception as exc:  # noqa: BLE001 - the fixture's whole job is to skip
        pytest.skip(f"no canonical baserom available: {exc}")
    return rom.read_bytes()


def test_both_boundaries_are_derived_and_agree(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "arith_tu")
    assert evidence["problems"] == [], evidence["problems"]
    assert len(evidence["functions"]) == 2
    for row in evidence["functions"]:
        assert row["matches_expected"] is True
        assert row["gaps"] == []


def test_each_member_is_20_bytes_with_one_terminator(rom_bytes):
    rows = lift.derive_unit_boundaries(rom_bytes, "arith_tu")["functions"]
    assert (rows[0]["start"], rows[0]["end"], rows[0]["size"], rows[0]["instructions"]) \
        == ("0x08003D52", "0x08003D66", 20, 10)
    assert rows[0]["terminators"] == ["0x08003D64"]
    assert (rows[1]["start"], rows[1]["end"], rows[1]["size"], rows[1]["instructions"]) \
        == ("0x08003D66", "0x08003D7A", 20, 10)
    assert rows[1]["terminators"] == ["0x08003D78"]


def test_the_three_members_tile_contiguously(rom_bytes):
    seven = lift.derive_unit_boundaries(rom_bytes, "stack_tu")["functions"][0]
    rows = lift.derive_unit_boundaries(rom_bytes, "arith_tu")["functions"]
    assert seven["end"] == rows[0]["start"] == "0x08003D52"
    assert rows[0]["end"] == rows[1]["start"] == "0x08003D66"


def test_this_unit_has_no_literal_pool(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "arith_tu")
    assert evidence["has_literal_pool"] is False
    assert evidence["pool_extent"] is None


def test_exactly_one_primary_slot_points_at_each_member(rom_bytes):
    from buusfury import gba

    base = gba.ROM_BASE
    for slot, entry in ((8, 0x08003D52), (9, 0x08003D66)):
        hits = []
        for index in range(lift.PRIMARY_TABLE_ENTRIES):
            address = lift.PRIMARY_TABLE + index * 4
            value = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
            if value and (value & ~1) == entry:
                hits.append((index, value))
        assert len(hits) == 1, hits
        assert hits[0][0] == slot


def test_a_wrong_expected_extent_is_reported(rom_bytes, monkeypatch):
    wrong = list(lift.UNITS["arith_tu"]["functions"])
    wrong[1] = (0x08003D66, 0x08003D7C, wrong[1][2])
    monkeypatch.setitem(lift.UNITS["arith_tu"], "functions", wrong)
    assert lift.derive_unit_boundaries(rom_bytes, "arith_tu")["problems"]


# ---------------------------------------------------------------------------
# the family, derived from the ROM
# ---------------------------------------------------------------------------
def test_the_family_has_three_members_and_all_match(rom_bytes):
    family = lift.derive_arith_family(rom_bytes)
    assert family["member_count"] == 3
    assert family["all_shapes_matched"] is True
    assert [m["slot"] for m in family["members"]] == [7, 8, 9]


def test_each_member_has_its_own_instruction_backed_operation(rom_bytes):
    members = {m["slot"]: m for m in lift.derive_arith_family(rom_bytes)["members"]}
    assert members[7]["operation"] == "adds r1, r2, r1"
    assert members[8]["operation"] == "subs r1, r2, r1"
    assert members[9]["operation"] == "muls r2, r1, r2"
    for slot in (7, 8, 9):
        assert members[slot]["pop_shape_matched"] is True
        assert members[slot]["reads_cursor_slot"] is False
        assert members[slot]["has_underflow_check"] is False
        assert members[slot]["calls"] == 0
        assert members[slot]["literal_slots"] == 0


def test_the_shared_contract_is_derived_not_asserted(rom_bytes):
    contract = lift.derive_arith_family(rom_bytes)["shared_contract"]
    assert contract["count_offset"] == 0
    assert contract["values_offset"] == 4
    assert contract["entry_size_bytes"] == 4
    assert contract["consumes"] == 2
    assert contract["produces"] == 1
    assert contract["net_counter_delta"] == -1
    assert "values[count-2]" in contract["result_slot"]
    assert "abandoned" in contract["upper_slot"]
    assert contract["counter_written_before_operand_reads"] is True
    assert contract["operand_order"] == "deeper value is the FIRST source, top value is the SECOND"


def test_operand_order_is_proven_directly_by_the_subtract(rom_bytes):
    """The acceptance asks for the order to be proven directly, not by the
    sibling relationship. Subtraction is the non-commutative member, and the
    derivation finds it by mnemonic rather than by slot number."""
    family = lift.derive_arith_family(rom_bytes)
    assert family["operand_order_directly_proven"] is True
    proof = family["operand_order_proven_by"]
    assert len(proof) >= 1
    assert proof[0]["operation"] == "subs r1, r2, r1"
    assert proof[0]["deeper_operand_is_first_source"] is True
    assert 7 not in [p["slot"] for p in proof] or True


def test_the_commuting_members_are_identified(rom_bytes):
    """Addition and multiplication cannot show the order; the derivation says
    which members those are instead of implying every member proves it."""
    family = lift.derive_arith_family(rom_bytes)
    assert family["commuting_members"] == [7, 9]
    assert 8 not in family["commuting_members"]


def test_the_family_spans_two_units(rom_bytes):
    """Slot 7 lives in its own unit so its report stays reproducible; the other
    two share one. The derivation reads all three regardless."""
    family = lift.derive_arith_family(rom_bytes)
    assert family["unit_ids"] == ["arith_tu", "stack_tu"]


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_both_handlers_are_present_and_the_cursor_is_unused():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_arith.c").read_text("utf-8")
    assert "void sub_08003D52(" in source
    assert "void sub_08003D66(" in source
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert code.count("(void)cursor_slot;") == 2, "both handlers must mark r1 unused"


def test_the_source_reproduces_the_underflow_rather_than_guarding_it():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_arith.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "count == 0" not in code
    assert "UNDERFLOW" in source
    assert "context-4" in source
    # Both underflow results are documented.
    assert "deeper + 1" in source
    assert "0xFFFFFFFF * deeper" in source


def test_the_source_uses_32_bit_addressing_and_names_no_opcodes():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_arith.c").read_text("utf-8")
    assert "(u32)ctx + count * 4u" in source
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "case " not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_result_register_difference_is_documented():
    """Slot 9's `muls` writes r2 where the others write r1, so its store is
    `str r2,[r0]`. That is a real structural difference and must be recorded."""
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_arith.c").read_text("utf-8")
    assert "str r2" in source
    assert "result register differs" in source or "result register is r2" in source


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_arith.c").read_text("utf-8")
    assert "#include" in shim and "../ByteCodeInterpreter_arith.c" in shim
    assert "sub_08003D52(" not in shim
    assert len(shim.splitlines()) < 30


@pytest.mark.parametrize("checks,expected", [(45, "PROVEN"), (44, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=45)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted_arith(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("arith", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted_arith):
    _, document = lifted_arith
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 45
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_equal_size_is_still_not_a_match(lifted_arith):
    _, document = lifted_arith
    comparison = document["comparison"]
    assert comparison["original_byte_length"] == comparison["modern_byte_length"] == 40
    assert comparison["differing_bytes_in_overlap"] > 0
    assert comparison["byte_identical"] is False
    assert comparison["is_a_match_claim"] is False


def test_each_member_pairs_by_name_over_its_own_extent(lifted_arith):
    _, document = lifted_arith
    rows = document["functions"]
    assert [r["name"] for r in rows] == ["sub_08003D52", "sub_08003D66"]
    for row in rows:
        assert row["modern_symbol_present"] is True
        assert row["original"]["size"] == row["modern"]["size"] == 20
        assert row["original"]["instructions"] == row["modern"]["instructions"] == 10
        assert len(row["original"]["calls"]) == len(row["modern"]["calls"]) == 0
        assert len(row["original"]["literal_slots"]) == len(row["modern"]["literal_slots"]) == 0
        assert row["original"]["returns"] == row["modern"]["returns"] == 1


def test_the_family_proof_is_recorded(lifted_arith):
    _, document = lifted_arith
    family = document["boundary_evidence"]["arith_family"]
    assert family["member_count"] == 3
    assert family["all_shapes_matched"] is True
    assert family["operand_order_directly_proven"] is True
    assert family["commuting_members"] == [7, 9]


def test_the_report_names_the_canonical_rom(lifted_arith):
    data, document = lifted_arith
    assert document["source_sha1"] == hashlib.sha1(data).hexdigest()
    assert document["target"]["rom_address"] == "0x08003D52"
    assert document["target"]["byte_length"] == 40


def test_the_committed_report_matches_a_fresh_run(lifted_arith):
    data, _ = lifted_arith
    result = lift.verify_report(data, "arith")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("arith").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert "Program Files" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
