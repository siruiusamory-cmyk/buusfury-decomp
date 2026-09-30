"""DECOMP-LIFT-NATIVE178-EFFECT-001: sub_0801191A, the object append.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.
"""

from __future__ import annotations

import json
import re

import pytest

from buusfury import identity, lift


def test_the_target_is_registered():
    target = lift.get_target("append")
    assert target.ticket == "DECOMP-LIFT-NATIVE178-EFFECT-001"
    assert target.rom_address == 0x0801191A
    assert target.probe_translation_unit == "append_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter_append.c"
    assert target.semantic_minimum_checks == 15
    assert target.host_build_bits == 32


def test_every_earlier_target_survives():
    """A FLOOR plus the named survivors, never an exact global count."""
    ids = [t.id for t in lift.load_targets()]
    assert len(ids) >= 14, ids
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith", "use",
                    "effect", "flagread", "booluse", "clear", "gather", "flagmask",
                    "native178"):
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
    evidence = lift.derive_unit_boundaries(rom_bytes, "append_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"], row["instructions"]) \
        == ("0x0801191A", "0x0801192C", 18, 9)
    assert row["terminators"] == ["0x0801192A"]
    assert row["gaps"] == []


def test_it_is_a_leaf_with_no_pool(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "append_tu")
    assert evidence["has_literal_pool"] is False
    assert evidence["pool_extent"] is None


def test_the_caller_is_native_slot_178(rom_bytes):
    """The incoming contract is re-proven from the caller's own call site."""
    caller = lift.derive_native178_stack(rom_bytes)
    assert caller["call_count"] == 2
    assert [c["target"] for c in caller["calls"]] == ["0x0802BFBC", "0x0801191A"]
    assert caller["calls"][1]["site"] == "0x08003068"


# ---------------------------------------------------------------------------
# the append contract
# ---------------------------------------------------------------------------
def test_it_is_an_append_with_the_count_at_0x04(rom_bytes):
    append = lift.derive_object_append(rom_bytes)
    assert append["count_offset"] == "object + 0x04"
    assert append["values_base"] == "object + 0x08"
    assert append["element_offset"] == "object + 0x08 + 4*count"
    assert "APPENDS the incoming value" in append["effect"]


def test_the_count_is_read_before_it_is_written(rom_bytes):
    append = lift.derive_object_append(rom_bytes)
    assert append["count_read_before_it_is_written"] is True
    assert append["element_store_follows_the_count_store"] is True


def test_the_object_relative_accesses_are_all_mapped(rom_bytes):
    append = lift.derive_object_append(rom_bytes)
    accesses = " | ".join(append["accesses"])
    assert "+0x04 read" in accesses
    assert "+0x04 written" in accesses
    assert "+0x08 + 4*count written" in accesses
    assert append["writes_object_plus_0x00"] is False


def test_plus_0x00_is_never_touched(rom_bytes):
    """The routine reads and writes only +0x04 and the element.

    The raw displacement is NOT the object offset: r0 is advanced by 4 first, so the
    displacement-0 store targets object+4 and the derivation must account for the
    advance rather than reading the displacement alone.
    """
    append = lift.derive_object_append(rom_bytes)
    assert append["object_offset_advanced_first"] == 4
    assert append["writes_object_plus_0x00"] is False
    assert "displacement-0 store targets object+4" in append["writes_object_plus_0x00_evidence"]


def test_there_is_no_capacity_check(rom_bytes):
    append = lift.derive_object_append(rom_bytes)
    assert append["compares_the_count_against_anything"] is False
    assert append["has_capacity_check"] is False
    assert append["branches"] == 0
    assert "no capacity is enforced" in append["has_capacity_check_evidence"]


def test_the_return_value_is_not_defined(rom_bytes):
    append = lift.derive_object_append(rom_bytes)
    assert append["return_value_defined"] is False
    assert "not a status" in append["return_value_evidence"]


def test_it_makes_no_calls_and_loads_no_literals(rom_bytes):
    append = lift.derive_object_append(rom_bytes)
    assert append["calls"] == 0
    assert append["literal_slots"] == 0


def test_the_object_layout_is_preserved_for_reuse(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    document = lift.run_lift("append", rom_bytes, toolchain)
    note = document["boundary_evidence"]["object_layout_note"]
    assert note["object"] == "0x03001C4C"
    assert note["count_offset"] == "object + 0x04"
    assert note["values_base"] == "object + 0x08"
    assert note["caller"] == "native slot 178 at 0x08003030"


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_adds_no_guard_and_no_name():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_append.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "case " not in code
    assert "assert" not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_source_returns_void():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_append.c").read_text("utf-8")
    assert "void sub_0801191A(void *object, u32 value)" in source


def test_the_source_has_no_nested_comment_delimiters():
    """A `/* ... */` inside a block comment closes it early and breaks the build."""
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_append.c").read_text("utf-8")
    body = source[:source.index("*/")]
    assert body.count("/*") == 1, "a nested comment delimiter would close the block early"


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_append.c").read_text("utf-8")
    assert "../ByteCodeInterpreter_append.c" in shim
    assert "sub_0801191A(" not in shim


@pytest.mark.parametrize("checks,expected", [(15, "PROVEN"), (14, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=15)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("append", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted):
    _, document = lifted
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 15
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted):
    _, document = lifted
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False
    assert document["comparison"]["differing_bytes_in_overlap"] > 0


def test_it_pairs_by_name_with_no_external_calls(lifted):
    _, document = lifted
    row = document["functions"][0]
    assert row["name"] == "sub_0801191A"
    assert len(row["original"]["calls"]) == len(row["modern"]["calls"]) == 0
    assert document["modern_build"]["external_calls_bound_to_original_addresses"] == {}


def test_the_committed_report_matches_a_fresh_run(lifted):
    data, _ = lifted
    result = lift.verify_report(data, "append")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("append").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
