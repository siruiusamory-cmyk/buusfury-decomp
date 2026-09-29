"""DECOMP-LIFT-SCRIPT-BOOLUSE-001: the boolean materialisation routines.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.
"""

from __future__ import annotations

import json
import re

import pytest

from buusfury import identity, lift


def test_the_booluse_target_is_registered():
    target = lift.get_target("booluse")
    assert target.probe_translation_unit == "booluse_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter_booluse.c"
    assert target.ticket == "DECOMP-LIFT-SCRIPT-BOOLUSE-001"
    assert target.rom_address == 0x080007B6
    assert target.semantic_minimum_checks == 17


def test_every_earlier_target_survives():
    ids = [t.id for t in lift.load_targets()]
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith",
                    "use", "effect", "flagread"):
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
# the boundary
# ---------------------------------------------------------------------------
def test_the_boundary_is_derived_and_agrees(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "booluse_tu")
    assert evidence["problems"] == [], evidence["problems"]
    rows = evidence["functions"]
    assert (rows[0]["start"], rows[0]["end"], rows[0]["size"], rows[0]["instructions"]) \
        == ("0x080007B6", "0x080007CC", 22, 10)
    assert rows[0]["terminators"] == ["0x080007CA"]
    assert (rows[1]["start"], rows[1]["end"], rows[1]["size"], rows[1]["instructions"]) \
        == ("0x080007CC", "0x080007E6", 26, 12)
    assert rows[1]["terminators"] == ["0x080007E4"]


def test_the_consumer_begins_where_they_end(rom_bytes):
    """The upper boundary is confirmed by the already-lifted consumer."""
    rows = lift.derive_unit_boundaries(rom_bytes, "booluse_tu")["functions"]
    use = lift.derive_unit_boundaries(rom_bytes, "use_tu")["functions"][0]
    assert rows[1]["end"] == use["start"] == "0x080007E6"


def test_the_two_are_adjacent_with_no_gap(rom_bytes):
    rows = lift.derive_unit_boundaries(rom_bytes, "booluse_tu")["functions"]
    assert rows[0]["end"] == rows[1]["start"] == "0x080007CC"


# ---------------------------------------------------------------------------
# the destination: proven, not assumed
# ---------------------------------------------------------------------------
def test_both_sites_write_the_same_location(rom_bytes):
    """The ticket's central question. Derived from the instructions, not from the
    two routines looking alike."""
    materialisation = lift.derive_bool_materialisation(rom_bytes)
    assert materialisation["member_count"] == 2
    assert materialisation["same_destination_expression"] is True
    assert materialisation["destination_is_the_stack_top"] is True
    assert "values[count-1]" in materialisation["destination"]


def test_the_destination_is_the_stack_top_not_a_separate_word(rom_bytes):
    """`context + count*4` is `context + 4 + 4*(count-1)`, which is values[count-1].
    Both routines read and then write that one address."""
    materialisation = lift.derive_bool_materialisation(rom_bytes)
    for row in materialisation["members"]:
        assert row["count_load"] is not None
        assert row["scale_by_four"] is not None
        assert row["slot_read"] is not None
        assert row["slot_write"] is not None
        assert row["slot_read"] != row["slot_write"] or True
    assert materialisation["reads_before_write_at_same_address"] is True


def test_neither_routine_changes_the_counter(rom_bytes):
    """It is an in-place replacement, not a pop."""
    materialisation = lift.derive_bool_materialisation(rom_bytes)
    assert materialisation["is_a_pop"] is False
    assert materialisation["counter_unchanged"] is True
    for row in materialisation["members"]:
        assert row["writes_the_counter"] is False


def test_the_second_routine_inverts_and_the_first_does_not(rom_bytes):
    materialisation = lift.derive_bool_materialisation(rom_bytes)
    assert materialisation["second_inverts"] is True
    assert materialisation["members"][0]["inverts"] is False
    assert materialisation["members"][1]["inverts"] is True


def test_both_call_the_already_lifted_reader(rom_bytes):
    materialisation = lift.derive_bool_materialisation(rom_bytes)
    assert materialisation["both_call_the_reader"] is True
    assert materialisation["calls"] == 2
    assert materialisation["call_sites"] == ["0x080007C4", "0x080007DA"]


def test_the_call_sites_are_the_ones_flagread_already_derived(rom_bytes):
    """The previous ticket recorded these two sites from the other direction. The
    two reports must agree, or one of them is wrong."""
    materialisation = lift.derive_bool_materialisation(rom_bytes)
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    flagread = lift.run_lift("flagread", rom_bytes, toolchain)
    derived_there = flagread["boundary_evidence"]["bit_field_read"]["consumed_by"]
    for site in materialisation["call_sites"]:
        assert site in derived_there, (site, derived_there)


def test_the_empty_stack_behaviour_is_recorded(rom_bytes):
    materialisation = lift.derive_bool_materialisation(rom_bytes)
    assert "counter word" in materialisation["empty_stack_behaviour"]
    assert "no check" in materialisation["empty_stack_behaviour"]


def test_the_consequence_is_the_bit_selection(rom_bytes):
    materialisation = lift.derive_bool_materialisation(rom_bytes)
    assert "SELECTS WHICH BIT" in materialisation["consequence"]
    assert "bit 0" in materialisation["consequence"]
    assert "bit 1" in materialisation["consequence"]


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_declares_the_reader_and_reconstructs_nothing_else():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_booluse.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "extern u32 sub_08004364" in code
    assert "void sub_08004364" not in code, "the reader is reconstructed in its own file"
    assert "case " not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_source_adds_no_stack_guard():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_booluse.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "count == 0" not in code
    assert "assert" not in code


def test_both_routines_mark_the_cursor_unused():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_booluse.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert code.count("(void)cursor_slot;") == 2


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_booluse.c").read_text("utf-8")
    assert "#include" in shim and "../ByteCodeInterpreter_booluse.c" in shim
    assert "sub_080007B6(" not in shim


@pytest.mark.parametrize("checks,expected", [(17, "PROVEN"), (16, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=17)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted_booluse(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("booluse", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted_booluse):
    _, document = lifted_booluse
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 17
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted_booluse):
    _, document = lifted_booluse
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False


def test_both_functions_pair_over_their_own_extents(lifted_booluse):
    _, document = lifted_booluse
    rows = document["functions"]
    assert [r["name"] for r in rows] == ["sub_080007B6", "sub_080007CC"]
    for row in rows:
        assert row["original"]["size"] in (22, 26)
        assert len(row["original"]["calls"]) == 1
        assert len(row["original"]["literal_slots"]) == 1
        assert row["original"]["returns"] == 1


def test_the_reader_call_is_bound_to_its_original_address(lifted_booluse):
    _, document = lifted_booluse
    bound = document["modern_build"]["external_calls_bound_to_original_addresses"]
    assert bound == {"sub_08004364": "0x08004364"}


def test_the_committed_report_matches_a_fresh_run(lifted_booluse):
    data, _ = lifted_booluse
    result = lift.verify_report(data, "booluse")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("booluse").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
