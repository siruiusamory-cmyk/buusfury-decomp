"""DECOMP-LIFT-COLLECTION-INSERT2-001: sub_08011732, the insertion path."""

from __future__ import annotations

import json
import re

import pytest

from buusfury import identity, lift


def test_the_target_is_registered():
    target = lift.get_target("collectioninsert2")
    assert target.ticket == "DECOMP-LIFT-COLLECTION-INSERT2-001"
    assert target.rom_address == 0x08011732
    assert target.semantic_minimum_checks == 27
    assert target.host_build_bits == 32


def test_every_earlier_target_survives():
    """A FLOOR plus the named survivors, never an exact global count."""
    ids = [t.id for t in lift.load_targets()]
    assert len(ids) >= 17, ids
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith", "use",
                    "effect", "flagread", "booluse", "clear", "gather", "flagmask",
                    "native178", "append", "collectionread", "collectionwrite2"):
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
    evidence = lift.derive_unit_boundaries(rom_bytes, "collectioninsert2_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"], row["instructions"]) \
        == ("0x08011732", "0x0801180A", 216, 97)
    assert row["terminators"] == ["0x08011808"]


# ---------------------------------------------------------------------------
# the insertion contract
# ---------------------------------------------------------------------------
def test_the_insertion_increments_the_second_count(rom_bytes):
    ins = lift.derive_collection_insert2(rom_bytes)
    assert ins["increments_the_second_collection_count"] is True
    assert ins["second_collection_count_offset"] == "object + 0x40C"
    assert ins["second_collection_values_offset"] == "object + 0x410"


def test_the_index_is_the_count_before_the_increment(rom_bytes):
    """`count2` is read, then incremented, and the OLD value is the index."""
    ins = lift.derive_collection_insert2(rom_bytes)
    assert ins["appends_at_the_old_count"] is True
    assert ins["index_is_the_count_before_the_increment"] is True
    assert ins["insertion_site"] == "0x0801177E..0x0801178A"


def test_the_second_collection_is_reached_by_a_computed_base(rom_bytes):
    ins = lift.derive_collection_insert2(rom_bytes)
    assert ins["second_collection_offset_folded_into_the_base"] is True


def test_the_element_is_moved_out_of_the_first_collection(rom_bytes):
    ins = lift.derive_collection_insert2(rom_bytes)
    assert ins["also_removes_from_the_first_collection"] is True
    assert ins["first_collection_count_offset"] == "object + 0x04"
    assert ins["first_collection_values_offset"] == "object + 0x08"
    assert "0x0804FE54" in ins["distinct_callees"]


def test_it_is_the_inverse_of_the_keyed_move(rom_bytes):
    read = lift.derive_collection_read(rom_bytes)
    ins = lift.derive_collection_insert2(rom_bytes)
    assert "sub_080119BC" in ins["inverse_of"]
    assert read["traversal"].startswith("BACKWARD")
    assert ins["scan_direction"].startswith("BACKWARD")


def test_the_verdict_drives_the_branches(rom_bytes):
    ins = lift.derive_collection_insert2(rom_bytes)
    assert ins["verdict_method_offset"] == 0x18
    assert ins["verdict_one_calls_04_and_removes"] is True
    assert ins["verdict_two_calls_1C_appends_and_removes"] is True


def test_there_is_no_duplicate_check_and_no_capacity_check(rom_bytes):
    ins = lift.derive_collection_insert2(rom_bytes)
    assert ins["has_duplicate_check"] is False
    assert ins["has_capacity_check"] is False


def test_there_is_a_third_collection_at_plus_0x208(rom_bytes):
    ins = lift.derive_collection_insert2(rom_bytes)
    assert ins["third_collection_count_offset"] == "object + 0x208"
    assert ins["third_collection_is_flushed_not_migrated"] is True


def test_plus_0x00_is_not_touched(rom_bytes):
    assert lift.derive_collection_insert2(rom_bytes)["accesses_object_plus_0x00"] is False


# ---------------------------------------------------------------------------
# the removal helper's argument convention, and the earlier note's correction
# ---------------------------------------------------------------------------
def test_the_removal_helper_takes_the_count_slot(rom_bytes):
    """Proven by this routine passing object + 4 for the first collection."""
    ins = lift.derive_collection_insert2(rom_bytes)
    assert ins["removal_helper_argument_is_the_count_slot"] is True
    assert ins["first_collection_count_offset"] == "object + 0x04"


def test_the_earlier_note_no_longer_claims_the_wrong_offset():
    notes = lift.get_target("collectionwrite2").notes
    assert "sub_0804FE54(object + 0x408, index)" not in notes, (
        "the count-slot convention means the call is at object + 0x40C"
    )
    assert "sub_0804FE54(object + 0x40C, index)" in notes
    assert "CORRECTION" in notes


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_redirects_absolute_machine_state_for_the_host():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectioninsert2.c").read_text("utf-8")
    assert "COLLECTIONINSERT2_HOST_TEST" in source
    assert "INSERT2_GLOBAL_WORD" in source
    assert "*(u32 *)0x08072824u" in source


def test_the_host_macro_is_actually_defined_by_the_self_check():
    """Forgetting it dereferenced an unmapped address and crashed the run."""
    test = (identity.REPO_ROOT / "src" / "probes" / "collectioninsert2_selftest.c").read_text("utf-8")
    assert "#define COLLECTIONINSERT2_HOST_TEST 1" in test
    assert "collectioninsert2_host_global_word" in test


def test_the_virtual_calls_use_32_bit_arithmetic():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectioninsert2.c").read_text("utf-8")
    assert "u32 method = table + offset;" in source
    assert "(u8 *)table + offset" not in source


def test_the_source_adds_no_guard_and_no_name():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectioninsert2.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "assert" not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_collectioninsert2.c").read_text("utf-8")
    assert "../ByteCodeInterpreter_collectioninsert2.c" in shim


@pytest.mark.parametrize("checks,expected", [(27, "PROVEN"), (26, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=27)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("collectioninsert2", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted):
    _, document = lifted
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 27
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted):
    _, document = lifted
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False


def test_the_externals_are_bound_to_their_original_addresses(lifted):
    _, document = lifted
    bound = document["modern_build"]["external_calls_bound_to_original_addresses"]
    for name in ("sub_080116FC", "sub_080115B0", "sub_0803DA62", "sub_0804FE54"):
        assert name in bound, bound
    assert not any(k.startswith("__defsym") for k in bound)


def test_the_committed_report_matches_a_fresh_run(lifted):
    data, _ = lifted
    result = lift.verify_report(data, "collectioninsert2")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("collectioninsert2").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
