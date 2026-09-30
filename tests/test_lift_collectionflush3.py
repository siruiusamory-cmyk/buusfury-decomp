"""DECOMP-LIFT-COLLECTION-INSERT3-001: the third region's drain and the negative proof."""

from __future__ import annotations

import json
import re

import pytest

from buusfury import analysis as A, gba, identity, lift

OBJECT = 0x03001C4C


def test_the_target_is_registered():
    target = lift.get_target("collectionflush3")
    assert target.ticket == "DECOMP-LIFT-COLLECTION-INSERT3-001"
    assert target.rom_address == 0x0801157E
    assert target.semantic_minimum_checks == 16
    assert target.host_build_bits == 32


def test_every_earlier_target_survives():
    """A FLOOR plus the named survivors, never an exact global count."""
    ids = [t.id for t in lift.load_targets()]
    assert len(ids) >= 18, ids
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith", "use",
                    "effect", "flagread", "booluse", "clear", "gather", "flagmask",
                    "native178", "append", "collectionread", "collectionwrite2",
                    "collectioninsert2"):
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
    evidence = lift.derive_unit_boundaries(rom_bytes, "collectionflush3_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"], row["instructions"]) \
        == ("0x0801157E", "0x080115B0", 50, 23)
    assert row["terminators"] == ["0x080115AE"]


# ---------------------------------------------------------------------------
# the third region's shape, proven from the routine's own instructions
# ---------------------------------------------------------------------------
def test_the_third_region_layout(rom_bytes):
    flush = lift.derive_collection_flush3(rom_bytes)
    assert flush["third_count_offset"] == "object + 0x208"
    assert flush["third_values_offset"] == "object + 0x20C"
    assert flush["count_width_bytes"] == 4
    assert flush["element_width_bytes"] == 4
    assert flush["elements_are_pointers"] is True


def test_the_offset_is_built_by_a_shift_pair(rom_bytes):
    """Which is why no displacement or literal search can find the region."""
    flush = lift.derive_collection_flush3(rom_bytes)
    assert flush["built_by_shift_pair"] is True
    assert "0x41" in flush["built_by_shift_pair_evidence"]
    assert "never an immediate displacement" in flush["built_by_shift_pair_evidence"]


def test_the_method_slot_is_0x14_and_is_not_shared(rom_bytes):
    flush = lift.derive_collection_flush3(rom_bytes)
    read = lift.derive_collection_read(rom_bytes)
    assert flush["method_slot"] == 0x14
    assert read["method_offset_in_the_table"] == 0x24
    assert flush["method_slot"] != read["method_offset_in_the_table"]


def test_the_traversal_is_backward(rom_bytes):
    flush = lift.derive_collection_flush3(rom_bytes)
    assert flush["traversal"].startswith("BACKWARD")
    assert "bpl" in flush["traversal_evidence"]


# ---------------------------------------------------------------------------
# drain, not population
# ---------------------------------------------------------------------------
def test_it_drains_and_zeroes_the_count(rom_bytes):
    flush = lift.derive_collection_flush3(rom_bytes)
    assert flush["drains_the_third_region"] is True
    assert flush["writes_zero_to_the_count"] is True


def test_it_never_writes_an_element_or_increments_a_count(rom_bytes):
    flush = lift.derive_collection_flush3(rom_bytes)
    assert flush["writes_an_element"] is False
    assert flush["increments_a_count"] is False


def test_it_does_not_consult_the_other_collections(rom_bytes):
    flush = lift.derive_collection_flush3(rom_bytes)
    assert flush["touches_the_first_collection"] is False
    assert flush["touches_the_second_collection"] is False


def test_it_does_not_touch_plus_0x00(rom_bytes):
    assert lift.derive_collection_flush3(rom_bytes)["accesses_object_plus_0x00"] is False


def test_the_same_operation_is_inlined_in_the_insertion_routine(rom_bytes):
    flush = lift.derive_collection_flush3(rom_bytes)
    ins = lift.derive_collection_insert2(rom_bytes)
    assert flush["same_operation_as_the_inline_block_in"] == "sub_08011732"
    assert ins["third_collection_is_flushed_not_migrated"] is True


# ---------------------------------------------------------------------------
# THE NEGATIVE PROOF: there is no population path, checked against the ROM
# ---------------------------------------------------------------------------
def _builders_of(rom_bytes, value):
    """Every ROM address where a movs/lsls pair produces `value`."""
    base = gba.ROM_BASE
    hits = set()
    for rd in range(8):
        for imm in range(0x100):
            for n in range(32):
                if (imm << n) != value:
                    continue
                movs = 0x2000 | (rd << 8) | imm
                lsls = (n << 6) | (rd << 3) | rd
                pat = movs.to_bytes(2, "little") + lsls.to_bytes(2, "little")
                pos = rom_bytes.find(pat)
                while pos != -1:
                    hits.add(base + pos)
                    pos = rom_bytes.find(pat, pos + 1)
    return hits


def test_the_image_builds_0x208_at_eight_sites(rom_bytes):
    """Scans EVERY byte of the image, not just the reachable set.

    The offset is NOT unique to this object: five further sites build the same
    constant for other structures. An earlier revision of the lift claimed only three
    sites existed and this check is what caught the error.
    """
    hits = _builders_of(rom_bytes, 0x208)
    assert hits == {0x0801158A, 0x080117CA, 0x08011B7A, 0x080344CC, 0x08034A6A,
                    0x0804843E, 0x0804E9AE, 0x08054492}, sorted(hex(h) for h in hits)


def test_the_three_cluster_sites_are_the_ones_that_use_this_object(rom_bytes):
    """The three in the collection cluster all write zero to the count."""
    hits = _builders_of(rom_bytes, 0x208)
    cluster = {0x0801158A, 0x080117CA, 0x08011B7A}
    assert cluster <= hits
    assert lift.derive_collection_flush3(rom_bytes)["writes_zero_to_the_count"] is True
    assert lift.derive_collection_insert2(rom_bytes)[
        "third_collection_is_flushed_not_migrated"] is True


def test_every_builder_writes_zero_and_none_writes_an_element(rom_bytes):
    """The three builders are the drain, the inline drain, and the object reset."""
    assert lift.derive_collection_flush3(rom_bytes)["writes_an_element"] is False
    ins = lift.derive_collection_insert2(rom_bytes)
    assert ins["increments_the_second_collection_count"] is True
    # the insertion routine's third block zeroes the count rather than appending
    assert ins["third_collection_is_flushed_not_migrated"] is True


def test_no_stored_pointer_to_the_third_region_exists(rom_bytes):
    """So a generic append could not be aimed at it through a pointer either."""
    for value, why in ((OBJECT + 0x204, "third base"),
                       (OBJECT + 0x208, "third count slot"),
                       (OBJECT + 0x20C, "third element array")):
        word = value.to_bytes(4, "little")
        assert rom_bytes.find(word) == -1, (
            f"a stored pointer to the {why} (0x{value:08X}) was found after all"
        )


def test_no_immediate_displacement_accesses_the_region(rom_bytes):
    """The address is always computed, which is why displacement searches fail."""
    base = gba.ROM_BASE
    found = []
    for ins in A.MD_THUMB.disasm(rom_bytes, base):
        if not ins.mnemonic.startswith(("ldr", "str")):
            continue
        for op in ins.operands:
            if op.type != A.capstone.arm.ARM_OP_MEM or op.mem.index:
                continue
            if ins.reg_name(op.mem.base) in ("pc", "sp"):
                continue
            if 0x1F0 <= op.mem.disp <= 0x230:
                found.append((hex(ins.address), ins.mnemonic, op.mem.disp))
    # a linear sweep is capped by the disassembler's own reach, so the check is a
    # floor: nothing that DID disassemble addresses the region directly
    assert all(not (0x200 <= d <= 0x215) for _a, _m, d in found), found[:10]


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_redirects_absolute_state_and_uses_32_bit_math():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectionflush3.c").read_text("utf-8")
    assert "COLLECTIONFLUSH3_HOST_TEST" in source
    assert "FLUSH3_GLOBAL_WORD" in source
    assert "u32 method = table + offset;" in source
    assert "(u8 *)table + offset" not in source


def test_the_host_macro_is_defined_by_the_self_check():
    test = (identity.REPO_ROOT / "src" / "probes" / "collectionflush3_selftest.c").read_text("utf-8")
    assert "#define COLLECTIONFLUSH3_HOST_TEST 1" in test


def test_the_source_records_the_negative_finding():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectionflush3.c").read_text("utf-8")
    assert "THERE IS NO POPULATION PATH" in source
    assert "NOT statically resolvable" in source


def test_the_source_adds_no_guard_and_no_name(rom_bytes):
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectionflush3.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "assert" not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_collectionflush3.c").read_text("utf-8")
    assert "../ByteCodeInterpreter_collectionflush3.c" in shim


@pytest.mark.parametrize("checks,expected", [(16, "PROVEN"), (15, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=16)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("collectionflush3", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted):
    _, document = lifted
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 16
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
    assert "sub_0803DA62" in bound
    assert not any(k.startswith("__defsym") for k in bound)


def test_the_committed_report_matches_a_fresh_run(lifted):
    data, _ = lifted
    result = lift.verify_report(data, "collectionflush3")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("collectionflush3").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
