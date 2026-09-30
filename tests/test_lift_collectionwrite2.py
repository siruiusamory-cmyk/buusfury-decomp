"""DECOMP-LIFT-COLLECTION-WRITE2-001: sub_080119BC, the keyed move.

An earlier revision of this file was withdrawn rather than committed: four of its
assertions did not match the derivation's wording, and the honest fix was to read
the real strings and assert those, not to weaken the checks.
"""

from __future__ import annotations

import json
import re

import pytest

from buusfury import analysis as A, gba, identity, lift


def test_the_target_is_registered():
    target = lift.get_target("collectionwrite2")
    assert target.ticket == "DECOMP-LIFT-COLLECTION-WRITE2-001"
    assert target.rom_address == 0x080119BC
    assert target.semantic_minimum_checks == 21
    assert target.host_build_bits == 32


def test_every_earlier_target_survives():
    """A FLOOR plus the named survivors, never an exact global count."""
    ids = [t.id for t in lift.load_targets()]
    assert len(ids) >= 16, ids
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith", "use",
                    "effect", "flagread", "booluse", "clear", "gather", "flagmask",
                    "native178", "append", "collectionread"):
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
    evidence = lift.derive_unit_boundaries(rom_bytes, "collectionwrite2_tu")
    assert evidence["problems"] == [], evidence["problems"]
    row = evidence["functions"][0]
    assert (row["start"], row["end"], row["size"]) == ("0x080119BC", "0x08011A1E", 98)
    assert row["terminators"] == ["0x080119E8"]
    assert row["gaps"] == []


# ---------------------------------------------------------------------------
# the write contract
# ---------------------------------------------------------------------------
def test_the_second_collection_is_reached_by_a_computed_base(rom_bytes):
    """Which is exactly why a displacement search finds nothing."""
    write = lift.derive_collection_write2(rom_bytes)
    assert write["second_collection_count_offset"] == "object + 0x40C"
    assert write["second_collection_values_offset"] == "object + 0x410"
    assert write["second_collection_offset_folded_into_the_base"] is True
    assert "adds r0, r0, r2" in write["second_collection_reached_by"]
    assert "rather than through a displacement" in write["second_collection_reached_by"]


def test_the_fold_is_a_register_add_not_an_immediate(rom_bytes):
    """An immediate-only detector reported this False; the ROM adds a register
    loaded with the 0x40C literal."""
    write = lift.derive_collection_write2(rom_bytes)
    assert write["second_collection_offset_folded_into_the_base"] is True
    from buusfury import analysis as A, gba
    base = gba.ROM_BASE
    insns = list(A.MD_THUMB.disasm(
        rom_bytes[0x080119BC - base:0x08011A1E - base], 0x080119BC))
    adds = [x for x in insns if x.mnemonic == "adds" and "r0, r0" in x.op_str]
    assert any("r0, r0, r" in x.op_str for x in adds), [x.op_str for x in adds]


def test_a_first_collection_hit_is_replaced_in_place(rom_bytes):
    write = lift.derive_collection_write2(rom_bytes)
    assert write["replace_in_place_on_a_first_collection_hit"] is True
    assert write["count_changed_by_a_replace"] is False


def test_a_miss_removes_from_the_second_and_appends_to_the_first(rom_bytes):
    write = lift.derive_collection_write2(rom_bytes)
    assert write["removes_from_the_second_collection_on_a_miss"] is True
    assert write["removal_call"] == {"site": "0x08011A0C", "target": "0x0804FE54"}
    assert write["appends_to_the_first_collection_on_a_miss"] is True


def test_this_routine_never_appends_to_the_second_collection(rom_bytes):
    """So the second collection's INSERTION path is still unfound."""
    write = lift.derive_collection_write2(rom_bytes)
    assert write["appends_to_the_second_collection"] is False
    assert write["increments_the_second_collection_count"] is False


def test_the_replace_path_touches_no_count_at_all(rom_bytes):
    write = lift.derive_collection_write2(rom_bytes)
    assert write["count_changed_by_a_replace"] is False
    assert write["increments_the_second_collection_count"] is False


def test_both_scans_run_forward(rom_bytes):
    read = lift.derive_collection_read(rom_bytes)
    write = lift.derive_collection_write2(rom_bytes)
    assert write["scan_direction"].startswith("FORWARD")
    assert "FIRST element equal to the key wins" in write["scan_direction"]
    assert "the opposite direction from the reader's backward search" in \
        write["scan_direction_evidence"]
    assert read["traversal"].startswith("BACKWARD")


def test_the_value_is_stored_verbatim(rom_bytes):
    assert lift.derive_collection_write2(rom_bytes)["value_stored_verbatim"] is True


def test_there_is_no_capacity_check(rom_bytes):
    write = lift.derive_collection_write2(rom_bytes)
    assert write["has_capacity_check"] is False
    assert "compares either count against a limit" in write["has_capacity_check_evidence"]


def test_plus_0x00_is_not_touched(rom_bytes):
    assert lift.derive_collection_write2(rom_bytes)["accesses_object_plus_0x00"] is False


# ---------------------------------------------------------------------------
# comparison with the first append routine, measured rather than assumed
# ---------------------------------------------------------------------------
def test_the_two_are_in_one_family_with_different_roles(rom_bytes):
    write = lift.derive_collection_write2(rom_bytes)
    text = write["comparison_with_the_first_append"]
    assert "NOT structurally equivalent" in text
    assert "GENERIC append" in text
    assert "DIFFERENT roles" in text


def test_the_first_append_really_is_generic(rom_bytes):
    """MEASURED: scan for BL sites targeting the append and collect the r0 sources.

    If every caller passed the 0x03001C4C object, the routine would not be generic;
    the claim is only sound if callers pass OTHER bases too.
    """
    base = gba.ROM_BASE

    def chain(entry, limit=0x800):
        seen, out, bl, pending = {}, [], [], [entry]
        while pending:
            a = pending.pop()
            if a in seen or not gba.in_cartridge(a):
                continue
            for ins in A.MD_THUMB.disasm(rom_bytes[a - base:a - base + limit], a):
                if ins.address in seen:
                    break
                seen[ins.address] = ins.size
                out.append(ins)
                mn, ops = ins.mnemonic, ins.op_str
                imm = ins.operands[0].imm & 0xFFFFFFFF if (
                    ins.operands and ins.operands[0].type
                    == A.capstone.arm.ARM_OP_IMM) else None
                if mn in ("bl", "blx") and imm is not None:
                    bl.append((ins.address, imm & ~1)); continue
                if mn == "b" and imm is not None:
                    pending.append(imm); break
                if mn.startswith(("bne", "beq", "bcc", "bcs", "bmi", "bpl", "bvs",
                                  "bvc", "bhi", "bls", "bge", "blt", "bgt", "ble")) \
                        and imm is not None:
                    pending.append(imm); continue
                if mn == "bx" or (mn.startswith("pop") and "pc" in ops):
                    break
        out.sort(key=lambda i: i.address)
        return out, bl

    seeds = {a & ~1 for a, _i, _w in A.EXTERNAL_CODE_SEEDS}
    for tbl, n in ((0x080554C0, 31), (0x08055098, 266), (0x08055508, 13)):
        for i in range(n):
            v = int.from_bytes(
                rom_bytes[tbl + i * 4 - base:tbl + i * 4 - base + 4], "little")
            if gba.in_cartridge(v) and v > 0x08000100:
                seeds.add(v & ~1)
    funcs, done = {}, set()
    for _ in range(3):
        new = 0
        for s in sorted(seeds):
            if s in done:
                continue
            done.add(s)
            out, bl = chain(s)
            if out:
                funcs[s] = out
            for _site, tgt in bl:
                if tgt not in seeds and gba.in_cartridge(tgt):
                    seeds.add(tgt); new += 1
        if not new:
            break

    bases = set()
    for entry, insns in funcs.items():
        for i, x in enumerate(insns):
            if x.mnemonic not in ("bl", "blx") or not x.operands:
                continue
            op = x.operands[0]
            if op.type != A.capstone.arm.ARM_OP_IMM or (op.imm & ~1) != 0x0801191A:
                continue
            for y in reversed(insns[max(0, i - 6):i]):
                if (y.operands and y.operands[0].type == A.capstone.arm.ARM_OP_REG
                        and y.reg_name(y.operands[0].reg) == "r0"):
                    bases.add(y.op_str)
                    break

    displacements = {b.split("#")[-1].strip() for b in bases if "#" in b}
    assert len(bases) >= 2, bases
    assert len(displacements) >= 2, (
        f"the append must be called with more than one base; saw {bases}"
    )


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_declares_the_removal_helper_and_shares_the_scan():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectionwrite2.c").read_text("utf-8")
    assert "extern void sub_0804FE54(" in source
    assert "find_by_value" in source
    # It must be DECLARED, never DEFINED: a definition would have a body. The extern
    # declaration legitimately spells the signature, so the check is for a body.
    assert "sub_0804FE54(void *collection, u32 index)\n{" not in source


def test_the_source_adds_no_guard_and_no_name():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectionwrite2.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "case " not in code
    assert "assert" not in code
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_source_states_the_comparison_is_measured():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectionwrite2.c").read_text("utf-8")
    assert "NOT structurally equivalent" in source
    assert "rather than assumed from their adjacency" in source


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_collectionwrite2.c").read_text("utf-8")
    assert "../ByteCodeInterpreter_collectionwrite2.c" in shim


@pytest.mark.parametrize("checks,expected", [(21, "PROVEN"), (20, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=21)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("collectionwrite2", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted):
    _, document = lifted
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 21
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted):
    _, document = lifted
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False


def test_the_removal_helper_is_bound_to_its_original_address(lifted):
    _, document = lifted
    bound = document["modern_build"]["external_calls_bound_to_original_addresses"]
    assert bound == {"sub_0804FE54": "0x0804FE54"}


def test_the_committed_report_matches_a_fresh_run(lifted):
    data, _ = lifted
    result = lift.verify_report(data, "collectionwrite2")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("collectionwrite2").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
