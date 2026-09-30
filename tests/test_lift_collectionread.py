"""DECOMP-LIFT-COLLECTION-READ-001: the collection reader, sub_08011C70."""

from __future__ import annotations

import json
import re

import pytest

from buusfury import identity, lift


def test_the_target_is_registered():
    target = lift.get_target("collectionread")
    assert target.ticket == "DECOMP-LIFT-COLLECTION-READ-001"
    assert target.rom_address == 0x08011C70
    assert target.semantic_minimum_checks == 23
    assert target.host_build_bits == 32


def test_every_earlier_target_survives():
    """A FLOOR plus the named survivors, never an exact global count."""
    ids = [t.id for t in lift.load_targets()]
    assert len(ids) >= 15, ids
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith", "use",
                    "effect", "flagread", "booluse", "clear", "gather", "flagmask",
                    "native178", "append"):
        assert earlier in ids, earlier


@pytest.fixture(scope="module")
def rom_bytes():
    try:
        rom = identity.resolve_baserom()
        identity.verify(rom)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"no canonical baserom available: {exc}")
    return rom.read_bytes()


def test_the_boundary_is_derived_and_agrees(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "collectionread_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"], row["instructions"]) \
        == ("0x08011C70", "0x08011CCA", 90, 43)
    assert row["terminators"] == ["0x08011CC8"]


# ---------------------------------------------------------------------------
# the collection layout, proven a third time
# ---------------------------------------------------------------------------
def test_the_collection_layout(rom_bytes):
    read = lift.derive_collection_read(rom_bytes)
    assert read["count_offset"] == "collection + 0x04"
    assert read["values_offset"] == "collection + 0x08"
    assert read["element_width_bytes"] == 4
    assert read["elements_are_pointers"] is True


def test_the_element_is_dereferenced_to_a_table(rom_bytes):
    read = lift.derive_collection_read(rom_bytes)
    assert "FIRST WORD" in read["element_dereference"]
    assert read["method_offset_in_the_table"] == 0x24


# ---------------------------------------------------------------------------
# traversal semantics
# ---------------------------------------------------------------------------
def test_traversal_is_backward_from_the_top(rom_bytes):
    read = lift.derive_collection_read(rom_bytes)
    assert read["traversal"].startswith("BACKWARD")
    assert "count-1" in read["traversal"]
    assert "most recently appended" in read["traversal_evidence"]
    assert "bpl" in read["signed_loop_tests"]


def test_the_first_non_zero_result_wins(rom_bytes):
    read = lift.derive_collection_read(rom_bytes)
    assert "FIRST non-zero" in read["stop_rule"]


def test_an_empty_collection_calls_nothing(rom_bytes):
    read = lift.derive_collection_read(rom_bytes)
    assert "no method is called" in read["empty_collection_behaviour"]
    assert "bmi" in read["signed_loop_tests"]


def test_the_count_is_read_only(rom_bytes):
    read = lift.derive_collection_read(rom_bytes)
    assert read["count_is_read_only"] is True
    assert "no store" in read["count_is_read_only_evidence"]


# ---------------------------------------------------------------------------
# capacity evidence and the object's other half
# ---------------------------------------------------------------------------
def test_there_is_a_second_collection_at_plus_0x408(rom_bytes):
    """Found here, not inferred from adjacency."""
    read = lift.derive_collection_read(rom_bytes)
    assert read["second_collection_offset"] == "object + 0x408"
    assert read["collections_searched"] == 2
    assert "0x40C" in read["second_collection_evidence"]


def test_plus_0x00_is_not_touched_by_the_reader(rom_bytes):
    read = lift.derive_collection_read(rom_bytes)
    assert read["accesses_object_plus_0x00"] is False


def test_there_is_no_bounds_check(rom_bytes):
    read = lift.derive_collection_read(rom_bytes)
    assert read["has_bounds_check"] is False
    assert "never compared against a capacity" in read["has_bounds_check_evidence"]


def test_the_method_reaches_the_bx_thunk(rom_bytes):
    read = lift.derive_collection_read(rom_bytes)
    assert read["reaches_the_method_through_the_bx_thunk"] is True
    assert "0x08046AA6" in [c["target"] for c in read["calls"]]


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_models_the_indirect_call_rather_than_a_thunk():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectionread.c").read_text("utf-8")
    assert "call_element_method" in source
    assert "the `bx r3` thunk" in source
    assert "no external symbol is introduced" in source


def test_the_source_adds_no_guard_and_no_name():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectionread.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "case " not in code
    assert "assert" not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_collectionread.c").read_text("utf-8")
    assert "../ByteCodeInterpreter_collectionread.c" in shim


@pytest.mark.parametrize("checks,expected", [(23, "PROVEN"), (22, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=23)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("collectionread", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted):
    _, document = lifted
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 23
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted):
    _, document = lifted
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False
    assert document["comparison"]["differing_bytes_in_overlap"] > 0


def test_the_committed_report_matches_a_fresh_run(lifted):
    data, _ = lifted
    result = lift.verify_report(data, "collectionread")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("collectionread").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
