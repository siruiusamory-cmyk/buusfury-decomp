"""DECOMP-LIFT-SCRIPT-USE-001: the first surviving-value consumer.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.
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
def test_the_use_target_is_registered_against_its_own_unit():
    target = lift.get_target("use")
    assert target.probe_translation_unit == "use_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter_use.c"
    assert target.ticket == "DECOMP-LIFT-SCRIPT-USE-001"
    assert target.rom_address == 0x080007E6
    assert target.semantic_minimum_checks == 32


def test_every_earlier_target_survives():
    ids = [t.id for t in lift.load_targets()]
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith"):
        assert earlier in ids, earlier


# ---------------------------------------------------------------------------
# the derived boundary
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def rom_bytes():
    try:
        rom = identity.resolve_baserom()
        identity.verify(rom)
    except Exception as exc:  # noqa: BLE001 - the fixture's whole job is to skip
        pytest.skip(f"no canonical baserom available: {exc}")
    return rom.read_bytes()


def test_the_boundary_is_derived_and_agrees(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "use_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"], row["instructions"]) \
        == ("0x080007E6", "0x080007FE", 24, 11)
    assert row["terminators"] == ["0x080007FC"]
    assert row["gaps"] == []


def test_the_literal_pool_is_not_adjacent(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "use_tu")
    assert evidence["has_literal_pool"] is True
    assert evidence["pool_is_adjacent_to_code"] is False
    assert evidence["pool_extent"] == "0x080008D8..0x080008DC"


def test_exactly_one_native_entry_points_here(rom_bytes):
    from buusfury import gba

    base = gba.ROM_BASE
    count = lift.derive_native_table(rom_bytes)["entries"]
    hits = []
    for index in range(count):
        address = lift.NATIVE_TABLE + index * 4
        value = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
        if value and (value & ~1) == lift.USE_ENTRY:
            hits.append((index, value))
    assert hits == [(29, 0x080007E7)], hits


# ---------------------------------------------------------------------------
# the pop, and the absence of a write-back
# ---------------------------------------------------------------------------
def test_the_pop_prefix_matches_step_by_step(rom_bytes):
    use = lift.derive_value_use(rom_bytes)
    assert use["pop_prefix_matched"] is True
    for step in use["pop_steps"]:
        assert step["matched"], step
    # The reported address must name the instruction that matched, not the one
    # before it: this unit opens with a register save.
    assert use["pop_steps"][0]["address"] == "0x080007E8"
    assert "ldr r1, [r0]" in use["pop_steps"][0]["instruction"]
    assert use["pop_steps"][5]["address"] == "0x080007F2"


def test_it_is_a_pop_that_produces_nothing(rom_bytes):
    use = lift.derive_value_use(rom_bytes)
    assert use["is_a_pop"] is True
    assert use["is_a_peek"] is False
    assert use["consumes"] == 1
    assert use["produces"] == 0, "this routine writes no replacement value"
    assert use["counter_delta"] == -1


def test_it_does_not_write_back_to_the_stack(rom_bytes):
    """This is what separates it from the arithmetic family, and it is the whole
    reason the write-back shape matcher could not describe it."""
    use = lift.derive_value_use(rom_bytes)
    assert use["writes_back_to_the_stack"] is False
    assert "never used as the base of a store" in use["no_write_back_evidence"]


def test_the_value_read_is_the_old_top(rom_bytes):
    use = lift.derive_value_use(rom_bytes)
    assert "values[count-1]" in use["value_read"]


def test_it_reads_one_literal_and_makes_one_call(rom_bytes):
    use = lift.derive_value_use(rom_bytes)
    assert use["literal_slots"] == 1
    assert use["call_count"] == 1
    assert use["calls"] == [{"site": "0x080007F8", "target": "0x08004380"}]
    assert use["reads_cursor_slot"] is False


def test_there_is_no_underflow_check_and_the_underflow_is_read_only(rom_bytes):
    use = lift.derive_value_use(rom_bytes)
    assert use["has_underflow_check"] is False
    assert use["underflow_is_read_only"] is True
    assert "nothing below the context is written" in use["underflow_effect"]


def test_the_use_derivation_does_not_claim_a_write_back_shape(rom_bytes):
    """Regression guard: an earlier revision reused the arithmetic shape matcher
    here and the report claimed a result slot, a two-into-one reduction and an
    operation that were all false. A field must be derived or absent."""
    unit = lift.derive_unit_boundaries(rom_bytes, "use_tu")
    # The unit's own derivation must not carry the arithmetic matcher's fields.
    document = lift.run_lift("use", rom_bytes, lift.discover_modern_toolchain()) \
        if lift.discover_modern_toolchain() else None
    if document is None:
        pytest.skip("no modern ARM toolchain available")
    evidence = document["boundary_evidence"]
    assert "value_use" in evidence
    assert "stack_access" not in evidence
    assert evidence["value_use"]["produces"] == 0
    assert evidence["value_use"]["writes_back_to_the_stack"] is False


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_records_the_absence_of_a_write_back_and_no_guard():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_use.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "writes NOTHING back" in source
    assert "UNDERFLOW" in source
    assert "HARMLESS TO MEMORY" in source
    assert "count == 0" not in code
    assert "(u32)ctx + count * 4u" in source
    assert "case " not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_callee_is_declared_not_reconstructed():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_use.c").read_text("utf-8")
    assert "extern void sub_08004380" in source
    assert "sub_08004380(" in source
    # No definition of the callee in this tree.
    assert "void sub_08004380(void *target, u32 value)\n{" not in source


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_use.c").read_text("utf-8")
    assert "#include" in shim and "../ByteCodeInterpreter_use.c" in shim
    assert "sub_080007E6(" not in shim


@pytest.mark.parametrize("checks,expected", [(32, "PROVEN"), (31, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=32)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted_use(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("use", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted_use):
    _, document = lifted_use
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 32
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted_use):
    _, document = lifted_use
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False
    assert document["comparison"]["differing_bytes_in_overlap"] > 0


def test_the_call_is_bound_to_its_original_address(lifted_use):
    data, document = lifted_use
    bound = document["modern_build"]["external_calls_bound_to_original_addresses"]
    assert bound == {"sub_08004380": "0x08004380"}
    derived = lift.derive_external_calls(data, "use_tu")
    assert {n: f"0x{v:08X}" for n, v in derived.items()} == bound


def test_the_single_function_pairs_over_its_own_extent(lifted_use):
    _, document = lifted_use
    row = document["functions"][0]
    assert row["name"] == "sub_080007E6"
    assert len(row["original"]["calls"]) == len(row["modern"]["calls"]) == 1
    assert row["original"]["returns"] == row["modern"]["returns"] == 1
    # The ORIGINAL loads exactly one literal, from its pool. The modern literal
    # count is NOT asserted equal: GCC places its pool inside the function body,
    # and decoding those pool words as Thumb code invents further literal loads.
    # A literal count on the modern side is a codegen artifact, not a contract.
    assert len(row["original"]["literal_slots"]) == 1


def test_the_committed_report_matches_a_fresh_run(lifted_use):
    data, _ = lifted_use
    result = lift.verify_report(data, "use")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("use").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
