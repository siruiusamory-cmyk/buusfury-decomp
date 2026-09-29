"""DECOMP-LIFT-SCRIPT-HANDLER-001: ByteCodeInterpreter primary slot 2.

PORTABLE tests need no ROM and no toolchain. ROM- and toolchain-gated tests skip
cleanly when either is absent. The ROM is opened READ-ONLY.

Includes a regression test for a linker defect this ticket found and fixed: an
absolute symbol made with `--defsym` carries no Thumb marking, so the linker
emits a Thumb-to-ARM interworking veneer around every external call. The veneer
does `bx pc` then an ARM branch, which enters a Thumb target in ARM state, and it
adds eight bytes per call to the compared image.
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
def test_the_handler_target_is_registered_against_its_own_unit():
    target = lift.get_target("handler2")
    assert target.probe_translation_unit == "handler2_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter_handlers.c"
    assert target.selftest_source == "src/probes/handler2_selftest.c"
    assert target.ticket == "DECOMP-LIFT-SCRIPT-HANDLER-001"
    assert target.rom_address == 0x08003CBE
    assert target.host_build_bits == 32
    assert target.semantic_minimum_checks == 23


def test_the_handler_minimum_is_a_real_floor():
    source = (identity.REPO_ROOT / "src" / "probes" / "handler2_selftest.c").read_text("utf-8")
    assert lift.get_target("handler2").semantic_minimum_checks <= source.count("check(")


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


def test_the_handler_boundary_is_derived_and_agrees(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "handler2_tu")
    assert evidence["problems"] == [], evidence["problems"]
    assert evidence["derived_from_rom"] is True
    assert len(evidence["functions"]) == 1


def test_the_handler_is_22_bytes_with_one_terminator(rom_bytes):
    row = lift.derive_unit_boundaries(rom_bytes, "handler2_tu")["functions"][0]
    assert row["start"] == "0x08003CBE"
    assert row["end"] == "0x08003CD4"
    assert row["size"] == 22
    assert row["instructions"] == 10
    assert row["terminators"] == ["0x08003CD2"]
    assert row["gaps"] == []
    assert row["matches_expected"] is True


def test_the_pool_is_not_adjacent_to_the_handler(rom_bytes):
    """The pool is at 0x08003F40, 620 bytes past the end of the code, and four
    other primary handlers load from the same word."""
    evidence = lift.derive_unit_boundaries(rom_bytes, "handler2_tu")
    assert evidence["pool_is_adjacent_to_code"] is False
    assert evidence["pool_gap_bytes"] == 620
    assert evidence["pool_extent"] == "0x08003F40..0x08003F44"
    assert evidence["alignment_padding_bytes"] is None


def test_a_wrong_expected_extent_is_reported_not_absorbed(rom_bytes, monkeypatch):
    wrong = list(lift.UNITS["handler2_tu"]["functions"])
    wrong[0] = (0x08003CBE, 0x08003CD6, wrong[0][2])
    monkeypatch.setitem(lift.UNITS["handler2_tu"], "functions", tuple(wrong))
    evidence = lift.derive_unit_boundaries(rom_bytes, "handler2_tu")
    assert evidence["problems"], "a wrong expected extent was accepted"


# ---------------------------------------------------------------------------
# the native table: width and count re-proved, and 283 refuted
# ---------------------------------------------------------------------------
def test_the_native_entry_width_comes_from_the_handler_s_own_scale(rom_bytes):
    table = lift.derive_native_table(rom_bytes)
    assert table["entry_width_bytes"] == 4
    assert "lsls" in table["entry_width_evidence"]


def test_the_native_index_is_one_byte(rom_bytes):
    table = lift.derive_native_table(rom_bytes)
    assert table["index_width_bytes"] == 1
    assert table["index_range"] == [0, 255]
    assert "ldrb" in table["index_encoding"]


def test_the_native_count_is_bounded_on_both_sides(rom_bytes):
    """The count is proved, not scanned: the index has 256 possible values so
    there must be at least 256 entries, and the primary table's base bounds it
    from above."""
    table = lift.derive_native_table(rom_bytes)
    assert table["lower_bound"] == 256
    assert table["upper_bound"] == table["entries"]
    assert table["address"] == "0x08055098"


def test_the_native_table_has_266_valid_entries(rom_bytes):
    table = lift.derive_native_table(rom_bytes)
    assert table["entries"] == 266
    assert table["invalid_entries"] == []
    assert table["distinct_targets"] == 265
    assert table["target_range"][0].startswith("0x08000")


def test_every_byte_index_is_in_range_so_no_bound_test_is_needed(rom_bytes):
    table = lift.derive_native_table(rom_bytes)
    assert table["index_is_always_in_range"] is True
    assert table["entries"] >= 256


def test_the_primary_table_still_witnesses_the_bound(rom_bytes):
    """The upper bound is re-read from the ROM rather than remembered."""
    table = lift.derive_native_table(rom_bytes)
    assert table["bounded_above_by"] == "0x080554C0"
    assert table["primary_table_base_recheck"] == "0x08003C75"
    assert table["primary_table_bounding_string_matches"] is True


def test_the_283_claim_is_refuted_mechanically(rom_bytes):
    """283 entries at four bytes each reach 0x08055504, which is inside the
    primary dispatch table. The refutation is measured on every run."""
    refuted = lift.derive_native_table(rom_bytes)["refuted_claim"]
    assert refuted["entries"] == 283
    assert refuted["would_end_at"] == "0x08055504"
    assert "INSIDE the primary dispatch table" in refuted["why_impossible"]
    assert refuted["measured_entries"] == 266
    # And the arithmetic itself, checked rather than trusted.
    assert 0x08055098 + 283 * 4 == 0x08055504
    assert 0x080554C0 < 0x08055504 < 0x0805553C


# ---------------------------------------------------------------------------
# the dispatch entry and the source's discipline
# ---------------------------------------------------------------------------
def test_exactly_one_primary_slot_points_at_this_handler(rom_bytes):
    """Read from the ROM here, not taken from the report: the handler is reached
    ONLY through the dispatch table, so the table is the whole of its calling
    surface and 'exactly one slot' is the claim that matters."""
    from buusfury import gba

    base = gba.ROM_BASE
    hits = []
    for index in range(lift.PRIMARY_TABLE_ENTRIES):
        address = lift.PRIMARY_TABLE + index * 4
        value = int.from_bytes(rom_bytes[address - base : address - base + 4], "little")
        if value and (value & ~1) == lift.H2_ENTRY:
            hits.append((index, value))
    assert len(hits) == 1, hits
    assert hits[0][0] == 2
    assert hits[0][1] == 0x08003CBF


def test_the_source_decodes_no_native_routines_and_names_none():
    text = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_handlers.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    assert "case " not in code, "the handler decodes native indices, which it must not"
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_the_source_states_the_contract_and_the_unknowns():
    text = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_handlers.c").read_text("utf-8")
    assert "r0 = context" in text
    assert "ADDRESS OF THE CURSOR SLOT" in text
    assert "WHAT IS UNKNOWN" in text
    assert "266" in text, "the corrected count must be stated in the source"


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter_handlers.c").read_text("utf-8")
    assert "#include" in shim and "../ByteCodeInterpreter_handlers.c" in shim
    assert "sub_08003CBE(" not in shim
    assert len(shim.splitlines()) < 30


@pytest.mark.parametrize("checks,expected", [(23, "PROVEN"), (22, "PARTIAL")])
def test_the_handler_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=23)
    assert status == expected


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted_handler2(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("handler2", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted_handler2):
    _, document = lifted_handler2
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 23
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["code"] == "ADS12_LICENSE_UNAVAILABLE"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted_handler2):
    _, document = lifted_handler2
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False
    assert document["comparison"]["differing_bytes_in_overlap"] > 0


def test_the_single_call_and_literal_agree_where_the_bytes_do_not(lifted_handler2):
    _, document = lifted_handler2
    row = document["functions"][0]
    assert row["name"] == "sub_08003CBE"
    assert len(row["original"]["calls"]) == len(row["modern"]["calls"]) == 1
    assert len(row["original"]["literal_slots"]) == len(row["modern"]["literal_slots"]) == 1
    assert row["original"]["returns"] == row["modern"]["returns"] == 1


def test_the_external_call_is_bound_to_the_original_address(lifted_handler2):
    data, document = lifted_handler2
    bound = document["modern_build"]["external_calls_bound_to_original_addresses"]
    assert bound == {"sub_08046AA2": "0x08046AA2"}
    derived = lift.derive_external_calls(data, "handler2_tu")
    assert {n: f"0x{v:08X}" for n, v in derived.items()} == bound


def test_the_native_table_proof_is_recorded(lifted_handler2):
    _, document = lifted_handler2
    table = document["boundary_evidence"]["native_table"]
    assert table["entries"] == 266
    assert table["index_is_always_in_range"] is True
    assert table["refuted_claim"]["measured_entries"] == 266
    assert document["boundary_evidence"]["primary_slot"]["index"] == 2


def test_the_literals_are_fully_accounted_for(lifted_handler2):
    _, document = lifted_handler2
    pools = document["literal_pools"]
    assert pools["original"]["distinct_slots"] == 1
    assert pools["original"]["all_referenced_slots_are_declared"] is True
    assert pools["original"]["all_declared_slots_are_referenced"] is True
    assert pools["original"]["undeclared_slots"] == []
    # A single-function unit with no adjacent pool: the shared-run test does not
    # apply, and says so rather than reporting a failure.
    assert pools["original"]["shared_pool_applicable"] is False


def test_the_report_names_the_canonical_rom(lifted_handler2):
    data, document = lifted_handler2
    assert document["source_sha1"] == hashlib.sha1(data).hexdigest()
    assert document["target"]["rom_address"] == "0x08003CBE"
    assert document["target"]["byte_length"] == 22


def test_the_committed_report_matches_a_fresh_run(lifted_handler2):
    data, _ = lifted_handler2
    result = lift.verify_report(data, "handler2")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("handler2").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert "Program Files" not in text
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"


# ---------------------------------------------------------------------------
# the linker regression: no interworking veneers
# ---------------------------------------------------------------------------
def test_no_absolute_symbol_veneer_is_emitted_for_any_target():
    """`--defsym` produces an absolute symbol with no Thumb marking, so the
    linker wraps every external call in a Thumb-to-ARM veneer: `bx pc` then an
    ARM branch, which enters Thumb code in ARM state, plus eight bytes per call
    in the compared image. The generated assembly uses `.thumb_func` before
    `.set` instead.

    Three checks, weakest to strongest: the generated source says the right
    thing, no committed report records a --defsym command, and where the linked
    ELFs are still on disk, no veneer symbol exists in any of them.
    """
    source = lift.render_external_symbols({"sub_08046AA2": 0x08046AA2})
    assert "\t.thumb_func" in source
    assert "\t.set sub_08046AA2, 0x08046AA2" in source
    assert ".globl sub_08046AA2" in source

    # The committed reports carry the commands that produced them.
    for target_id in ("gbaram", "bci", "handler2"):
        path = lift.report_path_for(target_id)
        if not path.is_file():
            continue
        document = json.loads(path.read_text("utf-8"))
        commands = document["modern_build"]["build"]["commands"]
        for command in commands:
            assert "--defsym" not in command, f"{target_id}: {command}"

    # And, where the builds are present, no veneer was linked in.
    toolchain = lift.discover_modern_toolchain()
    for target_id in ("gbaram", "bci", "handler2"):
        elf = lift.LIFT_WORKSPACE / target_id / f"{target_id}.elf"
        if not elf.is_file():
            continue
        if toolchain is None:
            pytest.skip("no modern ARM toolchain available")
        symbols = lift._run([toolchain.nm, "--defined-only", elf]).stdout or ""
        veneers = [l.strip() for l in symbols.splitlines() if "from_thumb" in l or "from_arm" in l]
        assert veneers == [], f"{target_id} still emits veneers: " + "; ".join(veneers)
