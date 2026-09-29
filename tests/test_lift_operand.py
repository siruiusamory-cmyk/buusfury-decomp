"""DECOMP-LIFT-SCRIPT-SM7-001: ByteCodeInterpreter primary slot 1.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.

The name "sm7" is NOT a ROM string. It is asserted to be recorded as a candidate
alias only, never as an established name.
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
def test_the_operand_target_is_registered_against_its_own_unit():
    target = lift.get_target("operand")
    assert target.probe_translation_unit == "operand_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter_operand.c"
    assert target.selftest_source == "src/probes/operand_selftest.c"
    assert target.ticket == "DECOMP-LIFT-SCRIPT-SM7-001"
    assert target.rom_address == 0x08003C8A
    assert target.host_build_bits == 32
    assert target.semantic_minimum_checks == 42


def test_the_operand_minimum_is_a_real_floor():
    source = (identity.REPO_ROOT / "src" / "probes" / "operand_selftest.c").read_text("utf-8")
    assert lift.get_target("operand").semantic_minimum_checks <= source.count("check(")


def test_the_target_count_is_now_four():
    """The three earlier targets must remain registered: this ticket adds one."""
    ids = [t.id for t in lift.load_targets()]
    assert ids == ["gbaram", "bci", "handler2", "operand"]


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
    evidence = lift.derive_unit_boundaries(rom_bytes, "operand_tu")
    assert evidence["problems"] == [], evidence["problems"]
    assert evidence["derived_from_rom"] is True


def test_the_handler_is_52_bytes_with_one_terminator(rom_bytes):
    row = lift.derive_unit_boundaries(rom_bytes, "operand_tu")["functions"][0]
    assert row["start"] == "0x08003C8A"
    assert row["end"] == "0x08003CBE"
    assert row["size"] == 52
    assert row["instructions"] == 26
    assert row["terminators"] == ["0x08003CBC"]
    assert row["gaps"] == []
    assert row["matches_expected"] is True


def test_the_handler_ends_where_the_slot_2_handler_begins(rom_bytes):
    """Two independently derived boundaries confirming each other."""
    operand = lift.derive_unit_boundaries(rom_bytes, "operand_tu")["functions"][0]
    handler2 = lift.derive_unit_boundaries(rom_bytes, "handler2_tu")["functions"][0]
    assert operand["end"] == handler2["start"] == "0x08003CBE"


def test_this_unit_has_no_literal_pool(rom_bytes):
    """A register-only leaf: no `ldr rX,[pc,#N]` anywhere, so there is no pool
    word to declare. Reported as 'none', not as a measurement that failed."""
    evidence = lift.derive_unit_boundaries(rom_bytes, "operand_tu")
    assert evidence["has_literal_pool"] is False
    assert evidence["pool_extent"] is None
    assert evidence["pool_gap_bytes"] is None
    assert evidence["alignment_padding_bytes"] is None


def test_exactly_one_primary_slot_points_at_this_handler(rom_bytes):
    from buusfury import gba

    base = gba.ROM_BASE
    hits = []
    for index in range(lift.PRIMARY_TABLE_ENTRIES):
        address = lift.PRIMARY_TABLE + index * 4
        value = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
        if value and (value & ~1) == lift.OP_TU.rom_address:
            hits.append((index, value))
    assert len(hits) == 1, hits
    assert hits[0][0] == 1
    assert hits[0][1] == 0x08003C8B


def test_a_wrong_expected_extent_is_reported_not_absorbed(rom_bytes, monkeypatch):
    wrong = list(lift.UNITS["operand_tu"]["functions"])
    wrong[0] = (0x08003C8A, 0x08003CC0, wrong[0][2])
    monkeypatch.setitem(lift.UNITS["operand_tu"], "functions", tuple(wrong))
    assert lift.derive_unit_boundaries(rom_bytes, "operand_tu")["problems"]


# ---------------------------------------------------------------------------
# the encoding, derived from the instructions
# ---------------------------------------------------------------------------
def test_the_group_width_is_read_from_the_masking_shift_pair(rom_bytes):
    encoding = lift.derive_operand_encoding(rom_bytes)
    assert encoding["group_bits"] == 7
    assert "0x08003C98" in encoding["group_bits_evidence"]
    assert encoding["bytes_read_per_iteration"] == 1


def test_the_continuation_and_sign_bits_are_read_from_their_branches(rom_bytes):
    encoding = lift.derive_operand_encoding(rom_bytes)
    assert encoding["continuation_bit"] == 7
    assert encoding["sign_bit"] == 0
    assert "bmi" in encoding["continuation_bit_evidence"]
    assert "bpl" in encoding["sign_bit_evidence"]


def test_the_groups_arrive_most_significant_first(rom_bytes):
    encoding = lift.derive_operand_encoding(rom_bytes)
    assert encoding["group_order"] == "most significant first"
    assert "shifted left" in encoding["group_order_evidence"]


def test_the_magnitude_shift_is_arithmetic(rom_bytes):
    encoding = lift.derive_operand_encoding(rom_bytes)
    assert encoding["magnitude_shift_is_arithmetic"] is True
    assert "asrs" in encoding["magnitude_shift_evidence"]


def test_it_makes_no_calls_and_loads_no_literals(rom_bytes):
    encoding = lift.derive_operand_encoding(rom_bytes)
    assert encoding["calls"] == 0
    assert encoding["literal_slots"] == 0
    assert encoding["has_literal_pool"] is False


def test_there_is_no_length_limit_and_no_validation(rom_bytes):
    encoding = lift.derive_operand_encoding(rom_bytes)
    assert encoding["has_length_limit"] is False
    assert "only exit is the bit-7 test" in encoding["has_length_limit_evidence"]


def test_the_encoding_is_not_canonical(rom_bytes):
    encoding = lift.derive_operand_encoding(rom_bytes)
    assert encoding["is_canonical"] is False
    assert "0x80 0x02" in encoding["is_canonical_evidence"]


def test_the_extremes_are_simulated_from_the_derived_width(rom_bytes):
    """Computed here from the derived group width, so the report and this test
    would disagree if either changed. This cross-check caught a one-bit error in
    an earlier revision of the derivation."""
    encoding = lift.derive_operand_encoding(rom_bytes)
    bits = encoding["group_bits"]
    expected = []
    for groups in (1, 2, 3, 4):
        accumulator = (1 << (bits * groups)) - 1
        expected.append(-(accumulator >> 1))
    actual = [row["value"] for row in encoding["extreme_per_byte_count"][:4]]
    assert actual == expected == [-63, -8191, -1048575, -134217727]


def test_the_five_group_extreme_is_the_artifact(rom_bytes):
    encoding = lift.derive_operand_encoding(rom_bytes)
    row = encoding["extreme_per_byte_count"][4]
    assert row["accumulator"] == "0xFFFFFFFF"
    assert row["accumulator_bit_31_set"] is True
    assert row["value"] == 1, "the maximal five-group encoding decodes to +1"
    assert row["sign_magnitude_holds"] is False
    assert "0xFFFFFFFF" in encoding["high_accumulator_artifact"]


def test_the_semantic_test_asserts_the_same_extremes():
    """Ties the derived report to the executable check: the four extremes and
    the artifact value must appear in the C self-check as asserted constants."""
    source = (identity.REPO_ROOT / "src" / "probes" / "operand_selftest.c").read_text("utf-8")
    for literal in ("63", "8191", "1048575", "134217727", "1073741824"):
        assert literal in source, literal


# ---------------------------------------------------------------------------
# the name, and the source's discipline
# ---------------------------------------------------------------------------
def test_sm7_is_not_a_rom_string(rom_bytes):
    for needle in (b"sm7", b"SM7", b"Sm7"):
        assert rom_bytes.find(needle) < 0, needle


def test_sm7_is_recorded_as_a_candidate_alias_not_a_fact():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_operand.c").read_text("utf-8")
    assert "CANDIDATE ALIAS" in source
    assert "NOT a string in the ROM" in source


def test_the_source_reproduces_the_artifact_rather_than_correcting_it():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_operand.c").read_text("utf-8")
    assert "artifact" in source.lower()
    assert "+1" in source
    # The arithmetic shift is modelled explicitly rather than left to the
    # compiler, because C's >> on a negative value is implementation-defined.
    assert "arithmetic_shift_right_1" in source
    assert "implementation-defined" in source


def test_the_source_adds_no_validation_the_original_lacks():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_operand.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    # No length cap, no counter, no bounds comparison in the loop.
    assert "max_bytes" not in code
    assert "byte_count" not in code
    assert "remain" not in code
    # And no opcode table.
    assert "case " not in code


def test_the_source_imports_no_other_game():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_operand.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_operand.c").read_text("utf-8")
    assert "#include" in shim and "../ByteCodeInterpreter_operand.c" in shim
    assert "sub_08003C8A(" not in shim
    assert len(shim.splitlines()) < 30


@pytest.mark.parametrize("checks,expected", [(42, "PROVEN"), (41, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=42)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted_operand(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("operand", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted_operand):
    _, document = lifted_operand
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 42
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted_operand):
    _, document = lifted_operand
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False
    assert document["comparison"]["differing_bytes_in_overlap"] > 0


def test_the_shape_agrees_where_the_bytes_do_not(lifted_operand):
    _, document = lifted_operand
    row = document["functions"][0]
    assert row["name"] == "sub_08003C8A"
    assert len(row["original"]["calls"]) == len(row["modern"]["calls"]) == 0
    assert len(row["original"]["literal_slots"]) == len(row["modern"]["literal_slots"]) == 0
    assert row["original"]["returns"] == row["modern"]["returns"] == 1
    assert document["modern_build"]["external_calls_bound_to_original_addresses"] == {}


def test_the_encoding_proof_is_recorded(lifted_operand):
    _, document = lifted_operand
    encoding = document["boundary_evidence"]["operand_encoding"]
    assert encoding["group_bits"] == 7
    assert encoding["has_length_limit"] is False
    assert encoding["calls"] == 0
    assert document["boundary_evidence"]["primary_slot"]["index"] == 1


def test_the_report_names_the_canonical_rom(lifted_operand):
    data, document = lifted_operand
    assert document["source_sha1"] == hashlib.sha1(data).hexdigest()
    assert document["target"]["rom_address"] == "0x08003C8A"
    assert document["target"]["byte_length"] == 52


def test_the_committed_report_matches_a_fresh_run(lifted_operand):
    data, _ = lifted_operand
    result = lift.verify_report(data, "operand")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("operand").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert "Program Files" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
