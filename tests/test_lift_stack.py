"""DECOMP-LIFT-SCRIPT-STACK-001: the first value-stack consumer.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.

The idiom scan here is the same mechanical search used to select the target, run
again independently so the "it is the smallest" claim is re-derived rather than
remembered.
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
def test_the_stack_target_is_registered_against_its_own_unit():
    target = lift.get_target("stack")
    assert target.probe_translation_unit == "stack_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter_stack.c"
    assert target.selftest_source == "src/probes/stack_selftest.c"
    assert target.ticket == "DECOMP-LIFT-SCRIPT-STACK-001"
    assert target.rom_address == 0x08003D3E
    assert target.host_build_bits == 32
    assert target.semantic_minimum_checks == 34


def test_the_stack_minimum_is_a_real_floor():
    source = (identity.REPO_ROOT / "src" / "probes" / "stack_selftest.c").read_text("utf-8")
    assert lift.get_target("stack").semantic_minimum_checks <= source.count("check(")


def test_all_five_targets_remain_registered():
    assert [t.id for t in lift.load_targets()] == ["gbaram", "bci", "handler2", "operand", "stack"]


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
    evidence = lift.derive_unit_boundaries(rom_bytes, "stack_tu")
    assert evidence["problems"] == [], evidence["problems"]
    assert evidence["derived_from_rom"] is True


def test_the_consumer_is_20_bytes_with_one_terminator(rom_bytes):
    row = lift.derive_unit_boundaries(rom_bytes, "stack_tu")["functions"][0]
    assert row["start"] == "0x08003D3E"
    assert row["end"] == "0x08003D52"
    assert row["size"] == 20
    assert row["instructions"] == 10
    assert row["terminators"] == ["0x08003D50"]
    assert row["gaps"] == []
    assert row["matches_expected"] is True


def test_this_unit_has_no_literal_pool(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "stack_tu")
    assert evidence["has_literal_pool"] is False
    assert evidence["pool_extent"] is None


def test_exactly_one_primary_slot_points_at_this_consumer(rom_bytes):
    from buusfury import gba

    base = gba.ROM_BASE
    hits = []
    for index in range(lift.PRIMARY_TABLE_ENTRIES):
        address = lift.PRIMARY_TABLE + index * 4
        value = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
        if value and (value & ~1) == lift.STACK_ENTRY:
            hits.append((index, value))
    assert len(hits) == 1, hits
    assert hits[0] == (7, 0x08003D3F)


def test_a_wrong_expected_extent_is_reported(rom_bytes, monkeypatch):
    wrong = list(lift.UNITS["stack_tu"]["functions"])
    wrong[0] = (0x08003D3E, 0x08003D54, wrong[0][2])
    monkeypatch.setitem(lift.UNITS["stack_tu"], "functions", wrong)
    assert lift.derive_unit_boundaries(rom_bytes, "stack_tu")["problems"]


# ---------------------------------------------------------------------------
# the pop, step by step
# ---------------------------------------------------------------------------
def test_every_step_of_the_pop_shape_matches(rom_bytes):
    access = lift.derive_stack_consumer(rom_bytes)
    assert access["pop_shape_matched"] is True
    assert access["instructions"] == 10
    for step in access["steps"]:
        assert step["matched"], step


def test_the_stack_layout_offsets_are_proven(rom_bytes):
    access = lift.derive_stack_consumer(rom_bytes)
    assert access["count_offset"] == 0
    assert access["values_offset"] == 4
    assert access["entry_size_bytes"] == 4


def test_it_is_a_pop_consuming_two_and_producing_one(rom_bytes):
    access = lift.derive_stack_consumer(rom_bytes)
    assert access["consumes"] == 2
    assert access["produces"] == 1
    assert access["net_counter_delta"] == -1


def test_the_operation_is_a_32_bit_add(rom_bytes):
    access = lift.derive_stack_consumer(rom_bytes)
    assert access["operation"] == "adds r1, r2, r1"
    assert access["operation_is_32_bit"] is True


def test_the_result_lands_in_the_lower_operand_slot(rom_bytes):
    access = lift.derive_stack_consumer(rom_bytes)
    assert "values[count-2]" in access["result_slot"]
    assert "LOWER" in access["result_slot"]
    assert "abandoned" in access["upper_slot"]


def test_the_counter_is_written_before_the_operands_are_read(rom_bytes):
    access = lift.derive_stack_consumer(rom_bytes)
    assert access["counter_written_before_operand_reads"] is True
    assert "BEFORE" in access["steps"][2]["step"]


def test_it_makes_no_calls_and_loads_no_literals(rom_bytes):
    access = lift.derive_stack_consumer(rom_bytes)
    assert access["calls"] == 0
    assert access["literal_slots"] == 0


def test_it_never_reads_the_cursor_slot(rom_bytes):
    access = lift.derive_stack_consumer(rom_bytes)
    assert access["reads_cursor_slot"] is False
    assert "overwrites r1" in access["reads_cursor_slot_evidence"]


def test_there_is_no_underflow_check(rom_bytes):
    access = lift.derive_stack_consumer(rom_bytes)
    assert access["has_underflow_check"] is False
    assert "no test and no branch" in access["underflow_evidence"]


# ---------------------------------------------------------------------------
# operand order, from the siblings
# ---------------------------------------------------------------------------
def test_the_siblings_establish_the_operand_order(rom_bytes):
    """This handler cannot show the order because addition is commutative. The
    siblings share the shape and differ in one instruction, and the subtract
    makes the order visible."""
    access = lift.derive_stack_consumer(rom_bytes)
    assert access["operand_order_from_this_handler"].startswith("not observable")
    siblings = {row["slot"]: row for row in access["siblings"]}
    assert siblings[8]["entry"] == "0x08003D52"
    assert siblings[8]["combining_instruction"] == "subs r1, r2, r1"
    assert siblings[9]["combining_instruction"] == "muls r2, r1, r2"
    assert all(row["shares_the_shape"] for row in access["siblings"])


def test_the_order_convention_is_deeper_operand_first(rom_bytes):
    """Thumb renders a two-source ALU op as `op Rd, Rn, Rm`, and Rn is the left
    operand. The deeper value is loaded into r2 and the top into r1, and slot 8's
    `subs r1, r2, r1` therefore computes values[count-2] - values[count-1]."""
    access = lift.derive_stack_consumer(rom_bytes)
    assert access["operand_order"] == "values[count-2] <op> values[count-1] on the sibling evidence"
    assert access["deeper_operand_is_first_source"] is True
    assert "left operand" in access["deeper_operand_is_first_source_evidence"]


# ---------------------------------------------------------------------------
# the family, re-derived
# ---------------------------------------------------------------------------
def _contains_pop_idiom(rom_bytes, entry):
    """The six-instruction pop, matched mechanically. Returns the pop count."""
    from buusfury import gba

    base = gba.ROM_BASE
    md = lift.cp.MD["thumb"]
    seen, out, pending = {}, [], [entry]
    while pending:
        address = pending.pop()
        if address in seen or not gba.in_cartridge(address):
            continue
        for ins in md.disasm(rom_bytes[address - base : address - base + 0x400], address):
            if ins.address in seen:
                break
            seen[ins.address] = ins.size
            out.append(ins)
            if ins.mnemonic == "b" and ins.operands and ins.operands[0].type == lift.cp.capstone.arm.ARM_OP_IMM:
                pending.append(ins.operands[0].imm)
                break
            if ins.mnemonic.startswith(("bne", "beq", "bcc", "bcs", "bmi", "bpl", "bvs", "bvc",
                                        "bhi", "bls", "bge", "blt", "bgt", "ble")) \
                    and ins.operands and ins.operands[0].type == lift.cp.capstone.arm.ARM_OP_IMM:
                pending.append(ins.operands[0].imm)
                continue
            if ins.mnemonic == "bx" or (ins.mnemonic.startswith("pop") and "pc" in ins.op_str) \
                    or (ins.mnemonic.startswith("ldr") and ins.op_str.startswith("pc")):
                break
    out.sort(key=lambda i: i.address)
    count = 0
    for i in range(len(out) - 5):
        a, b, c, d, e, f = out[i:i + 6]
        ma, mc, mf = lift._thumb_mem(a), lift._thumb_mem(c), lift._thumb_mem(f)
        if not (a.mnemonic == "ldr" and ma and ma[1] == 0 and ma[2] is None):
            continue
        reg = lift._thumb_dst(a)
        if not (b.mnemonic == "subs" and reg in b.op_str and "#1" in b.op_str):
            continue
        reg2 = lift._thumb_dst(b)
        if not (c.mnemonic == "str" and mc and mc[1] == 0 and mc[2] is None and reg2 in c.op_str):
            continue
        if not (d.mnemonic == "lsls" and "#2" in d.op_str and reg2 in d.op_str):
            continue
        reg3 = lift._thumb_dst(d)
        if not (e.mnemonic == "adds" and reg3 in e.op_str and "r0" in e.op_str):
            continue
        reg4 = lift._thumb_dst(e)
        if not (f.mnemonic == "ldr" and mf and mf[0] == reg4 and mf[1] == 4 and mf[2] is None):
            continue
        count += 1
    return len(out), count


def test_the_value_stack_family_is_larger_than_this_one_function(rom_bytes):
    """This consumer is not unique: the idiom recurs across the VM surface, which
    is why the ticket lifts exactly one and says so."""
    base = identity.__dict__.get("ROM_BASE", 0x08000000)
    from buusfury import gba

    base = gba.ROM_BASE
    found = []
    for table, count in ((lift.PRIMARY_TABLE, lift.PRIMARY_TABLE_ENTRIES),
                         (lift.NATIVE_TABLE, lift.derive_native_table(rom_bytes)["entries"])):
        for index in range(count):
            address = table + index * 4
            value = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
            if not value:
                continue
            entry = value & ~1
            instructions, pops = _contains_pop_idiom(rom_bytes, entry)
            if pops:
                found.append((entry, instructions * 2, pops))
    assert len(found) > 20, f"the idiom should recur; found {len(found)}"
    smallest = min(found, key=lambda row: row[1])
    assert smallest[0] == lift.STACK_ENTRY, smallest
    assert smallest[1] == 20, smallest


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_reproduces_the_underflow_rather_than_guarding_it():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_stack.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "count == 0" not in code
    assert "underflow" not in code.lower(), "no guard may appear in the code itself"
    # But the behaviour must be documented.
    assert "UNDERFLOW" in source
    assert "context - 4" in source


def test_the_source_uses_32_bit_addressing_on_purpose():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_stack.c").read_text("utf-8")
    assert "(u32)ctx + count * 4u" in source
    assert "wrap" in source


def test_the_source_imports_no_other_game_and_has_no_opcode_table():
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_stack.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other
    assert "case " not in code


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_stack.c").read_text("utf-8")
    assert "#include" in shim and "../ByteCodeInterpreter_stack.c" in shim
    assert "sub_08003D3E(" not in shim
    assert len(shim.splitlines()) < 30


@pytest.mark.parametrize("checks,expected", [(34, "PROVEN"), (33, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=34)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted_stack(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("stack", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted_stack):
    _, document = lifted_stack
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 34
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_equal_size_is_still_not_a_match(lifted_stack):
    """This is the first target whose modern build is the same SIZE as the
    original. Size equality is not identity, and the report must still say so."""
    _, document = lifted_stack
    comparison = document["comparison"]
    assert comparison["original_byte_length"] == comparison["modern_byte_length"] == 20
    assert comparison["differing_bytes_in_overlap"] > 0
    assert comparison["byte_identical"] is False
    assert comparison["is_a_match_claim"] is False
    assert comparison["matching_instruction_spans"] >= 1


def test_the_shape_agrees_where_the_bytes_do_not(lifted_stack):
    _, document = lifted_stack
    row = document["functions"][0]
    assert row["name"] == "sub_08003D3E"
    assert len(row["original"]["calls"]) == len(row["modern"]["calls"]) == 0
    assert len(row["original"]["literal_slots"]) == len(row["modern"]["literal_slots"]) == 0
    assert row["original"]["returns"] == row["modern"]["returns"] == 1
    assert row["original"]["instructions"] == row["modern"]["instructions"] == 10
    assert document["modern_build"]["external_calls_bound_to_original_addresses"] == {}


def test_the_stack_proof_is_recorded(lifted_stack):
    _, document = lifted_stack
    access = document["boundary_evidence"]["value_stack_access"]
    assert access["pop_shape_matched"] is True
    assert access["net_counter_delta"] == -1
    assert access["has_underflow_check"] is False
    assert document["boundary_evidence"]["primary_slot"]["index"] == 7


def test_the_report_names_the_canonical_rom(lifted_stack):
    data, document = lifted_stack
    assert document["source_sha1"] == hashlib.sha1(data).hexdigest()
    assert document["target"]["rom_address"] == "0x08003D3E"
    assert document["target"]["byte_length"] == 20


def test_the_committed_report_matches_a_fresh_run(lifted_stack):
    data, _ = lifted_stack
    result = lift.verify_report(data, "stack")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("stack").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert "Program Files" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
