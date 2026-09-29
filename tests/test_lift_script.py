"""DECOMP-LIFT-SCRIPT-001: the ByteCodeInterpreter entry function.

Two groups, following the pilot's pattern:

* PORTABLE tests need no ROM and no toolchain. They cover the derivation
  primitives, the semantic predicate at this target's minimum, and the source's
  own discipline about what is proven and what is not.
* ROM- and toolchain-gated tests skip cleanly when either is absent.

The ROM is opened READ-ONLY and no test writes to it.
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
def test_the_script_target_is_registered_against_its_own_unit():
    target = lift.get_target("bci")
    assert target.probe_translation_unit == "bci_tu"
    assert target.decomp_source == "src/ByteCodeInterpreter.c"
    assert target.selftest_source == "src/probes/bci_selftest.c"
    assert target.ticket == "DECOMP-LIFT-SCRIPT-001"
    assert target.rom_address == 0x08004038


def test_the_script_target_builds_the_host_check_32_bit():
    """A reconstruction that holds pointers in u32 fields models a 32-bit
    machine. Built 64-bit, every stored context address loses its high half and
    the first dereference through one faults. Asserted, not assumed, because
    widening a typedef would hide the machine model instead of honouring it."""
    target = lift.get_target("bci")
    assert target.host_build_bits == 32
    assert target.semantic_minimum_checks == 70


def test_the_script_minimum_is_a_real_floor():
    """70 is the count the self-check actually reaches, not a round number."""
    source = (identity.REPO_ROOT / "src" / "probes" / "bci_selftest.c").read_text("utf-8")
    assert "check(" in source
    target = lift.get_target("bci")
    assert target.semantic_minimum_checks <= source.count("check(")


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


def test_the_boundary_is_derived_from_the_rom_and_agrees(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "bci_tu")
    assert evidence["problems"] == [], evidence["problems"]
    assert evidence["derived_from_rom"] is True
    assert evidence["not_hand_written"] is True
    assert len(evidence["functions"]) == 3


def test_each_function_has_one_terminator_and_no_gaps(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "bci_tu")
    for row in evidence["functions"]:
        assert row["matches_expected"] is True, row
        assert row["gaps"] == [], row
        assert len(row["terminators"]) == 1, row


def test_the_three_functions_tile_the_code_with_only_padding_left_over(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "bci_tu")
    rows = evidence["functions"]
    assert rows[0]["start"] == "0x08004038"
    assert rows[0]["end"] == "0x08004098"
    assert rows[1]["end"] == "0x08004102"
    assert rows[2]["end"] == "0x08004156"
    assert evidence["alignment_padding_bytes"] == 2


def test_the_entry_function_is_the_one_the_ticket_names(rom_bytes):
    """96 bytes, 47 instructions, a single exit at 0x0800408C."""
    evidence = lift.derive_unit_boundaries(rom_bytes, "bci_tu")
    entry = evidence["functions"][0]
    assert entry["size"] == 96
    assert entry["instructions"] == 47
    assert entry["terminators"] == ["0x0800408C"]


def test_the_pool_is_not_adjacent_to_the_code(rom_bytes):
    """The property the probe manifest's schema cannot express, and the reason
    this unit is derived here instead. Two padding bytes separate the last
    function from the pool."""
    evidence = lift.derive_unit_boundaries(rom_bytes, "bci_tu")
    assert evidence["pool_is_adjacent_to_code"] is False
    assert evidence["alignment_padding_bytes"] != 0


def test_a_wrong_expected_extent_is_reported_not_absorbed(rom_bytes, monkeypatch):
    """The derivation must be able to fail. If it could not, 'derived' would be
    a word rather than a check. The registry entry is the injection point,
    because that is what derive_unit_boundaries actually reads."""
    wrong = list(lift.UNITS["bci_tu"]["functions"])
    wrong[0] = (0x08004038, 0x0800409A, wrong[0][2])
    monkeypatch.setitem(lift.UNITS["bci_tu"], "functions", tuple(wrong))
    evidence = lift.derive_unit_boundaries(rom_bytes, "bci_tu")
    assert evidence["problems"], "a wrong expected extent was accepted"


def test_an_unknown_unit_has_no_derivation():
    with pytest.raises(lift.LiftError):
        lift.derive_unit_boundaries(b"\x00" * 64, "gbaram_tu")


# ---------------------------------------------------------------------------
# the dispatch table
# ---------------------------------------------------------------------------
def test_the_table_is_proven_to_have_31_entries(rom_bytes):
    """Established by what follows the table, not by a remembered number: entry
    30 ends where the UTF-16 assertion string begins."""
    table = lift.derive_dispatch_table(rom_bytes)
    assert table["entries"] == 31
    assert table["address"] == "0x080554C0"
    assert table["null_entries"] == [17]
    assert table["bounding_string_address"] == "0x0805553C"


def test_the_bounding_string_is_the_engine_s_own_words(rom_bytes):
    """The ROM stores the message WITH its surrounding quote characters, which
    is why the expected text includes them."""
    table = lift.derive_dispatch_table(rom_bytes)
    assert table["bounding_string_matches"] is True, table["bounding_string_text"]
    assert "dialog" in table["bounding_string_text"]
    assert "code block" in table["bounding_string_text"]


def test_every_non_null_entry_is_a_thumb_pointer(rom_bytes):
    """30 pointers, all with bit 0 set; the 31st is the NULL terminator."""
    table = lift.derive_dispatch_table(rom_bytes)
    assert table["entries_are_thumb_pointers"] == 30


# ---------------------------------------------------------------------------
# the reconstruction's own discipline
# ---------------------------------------------------------------------------
def test_the_source_decodes_no_opcodes_and_imports_no_other_game():
    """The ticket forbids importing unverified opcode meanings. The mechanical
    form of that promise: the reconstruction contains no switch over opcodes and
    names no handler semantics, so it cannot have transcribed a table."""
    text = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    assert "case " not in code, "the reconstruction decodes opcodes, which it must not"
    for other in ("Legacy of Goku", "LOGI", "LOGII", "Buu", "Webfoot"):
        assert other not in code, other


def test_unknown_semantics_are_declared_unknown():
    text = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter.c").read_text("utf-8")
    assert "UNKNOWN" in text
    assert "Assumption (NOT evidence)" in text
    # The untitled helper must keep its address for a name.
    assert "sub_08004102" in text
    assert "name not justified" in text.lower() or "none is justified" in text.lower()


def test_the_context_is_named_by_offset_not_by_guess():
    """Every member of the context struct is named after its offset. A local
    named `opcode` is fine, because the byte read from the cursor DOES index the
    dispatch table; a FIELD called something semantic would be a guess."""
    text = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter.c").read_text("utf-8")
    match = re.search(r"typedef struct BciContext \{(.*?)\} BciContext;", text, re.DOTALL)
    assert match, "the context struct is not declared"
    members = re.findall(r"\b(?:u8|u16|u32)\s+(\w+)\s*(?:\[[^\]]*\])?\s*;", match.group(1))
    assert members, "no members parsed"
    for name in members:
        assert re.fullmatch(r"(?:field|inline|pad)_[0-9A-Fa-f]{2}", name), name
    assert "field_00" in members and "field_44" in members and "field_58" in members


def test_the_source_labels_what_is_proven_and_what_is_not():
    """The ticket requires unknown semantics to be preserved explicitly, so the
    header must carry both a proven section and an assumption section."""
    text = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter.c").read_text("utf-8")
    assert "WHAT IS EVIDENCE AND WHAT IS ASSUMPTION" in text
    assert "UNKNOWN, deliberately left unknown" in text
    assert "extern void *sub_0803D5B8" in text, "declared-not-reconstructed must be marked"


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "ByteCodeInterpreter.c").read_text("utf-8")
    assert "#include" in shim and "../ByteCodeInterpreter.c" in shim
    assert "sub_08004038(" not in shim
    assert len(shim.splitlines()) < 30


# ---------------------------------------------------------------------------
# the semantic predicate at this target's floor
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "checks,expected",
    [(70, "PROVEN"), (71, "PROVEN"), (69, "PARTIAL"), (0, "PARTIAL")],
)
def test_the_script_minimum_is_enforced(checks, expected):
    status, detail = lift.semantic_verdict(0, checks, 0, minimum=70)
    assert status == expected
    assert detail


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted_bci(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("bci", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted_bci):
    _, document = lifted_bci
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] in lift.SEMANTIC_STATES
    assert verdicts["modern_build"]["status"] in lift.MODERN_BUILD_STATES
    assert verdicts["ads_match"]["status"] in lift.ADS_MATCH_STATES


def test_semantic_is_proven_at_seventy_checks(lifted_bci):
    _, document = lifted_bci
    semantic = document["verdicts"]["semantic"]
    assert semantic["status"] == "PROVEN", semantic["detail"]
    assert semantic["checks"] >= 70
    assert semantic["failures"] == 0
    assert document["target"]["host_build_bits"] == 32


def test_the_modern_build_passes(lifted_bci):
    _, document = lifted_bci
    build = document["modern_build"]
    assert build["status"] == "PASS", build["detail"]
    assert build["identity"]["target_triple"] == "arm-none-eabi"
    assert build["target_support"]["supported"] is True
    assert build["build"]["produced_byte_length"] > 0


def test_ads_match_is_blocked_and_not_inferred(lifted_bci):
    _, document = lifted_bci
    ads = document["verdicts"]["ads_match"]
    assert ads["status"] == "BLOCKED"
    assert ads["code"] == "ADS12_LICENSE_UNAVAILABLE"
    assert ads["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted_bci):
    _, document = lifted_bci
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["literal_pools"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False
    assert document["comparison"]["differing_bytes_in_overlap"] > 0


def test_the_structural_shape_agrees_where_the_bytes_do_not(lifted_bci):
    """The signal worth reading: the call counts match exactly, which says the
    reconstruction's shape is right even though no byte does."""
    _, document = lifted_bci
    rows = document["functions"]
    assert [len(r["original"]["calls"]) for r in rows] == [1, 5, 0]
    assert [len(r["modern"]["calls"]) for r in rows] == [1, 5, 0]
    assert [r["original"]["returns"] for r in rows] == [1, 1, 1]
    assert [r["modern"]["returns"] for r in rows] == [1, 1, 1]
    assert all(r["modern_symbol_present"] for r in rows)


def test_every_function_is_paired_by_name(lifted_bci):
    _, document = lifted_bci
    rows = document["functions"]
    assert [r["name"] for r in rows] == ["sub_08004038", "sub_08004098", "sub_08004102"]
    for row in rows:
        assert row["original"]["size"] > 0


def test_external_calls_are_bound_to_the_original_addresses(lifted_bci):
    """The unit calls code it does not contain. Binding those to the ORIGINAL
    addresses keeps every call displacement right and adds no stub bytes."""
    _, document = lifted_bci
    bound = document["modern_build"]["external_calls_bound_to_original_addresses"]
    assert set(bound) == {
        "sub_0803D5B8", "sub_0803D63C", "sub_0803DF14", "sub_08046AA4", "sub_08049120",
    }
    # Each is a real ROM address and each name agrees with it.
    for name, value in bound.items():
        assert name == f"sub_{int(value, 16):08X}"
    # And they come from the ROM, not from a table in this repository.
    derived = lift.derive_external_calls(lifted_bci[0], "bci_tu")
    assert {n: f"0x{v & ~1:08X}" for n, v in derived.items()} == bound


def test_the_literals_are_fully_accounted_for(lifted_bci):
    """The unit's literals live in two places rather than one shared run, so the
    meaningful property is accounting, not contiguity."""
    _, document = lifted_bci
    pools = document["literal_pools"]
    assert pools["original"]["run_count"] == 2
    assert pools["original"]["shared_pool"] is False
    assert pools["original"]["all_referenced_slots_are_declared"] is True
    assert pools["original"]["all_declared_slots_are_referenced"] is True
    assert pools["original"]["undeclared_slots"] == []
    assert pools["original"]["distinct_slots"] == 3


def test_the_comparison_counts_add_up(lifted_bci):
    _, document = lifted_bci
    comparison = document["comparison"]
    for key, value in comparison.items():
        if isinstance(value, int):
            assert value >= 0, key
    assert (
        comparison["matching_bytes_in_overlap"] + comparison["differing_bytes_in_overlap"]
        == comparison["overlap_byte_length"]
    )
    assert comparison["original_instruction_spans"] > 0
    # The only bytes outside the original's instruction spans are its pool.
    assert comparison["bytes_not_covered_by_an_original_instruction"] == 8


def test_the_derivation_is_recorded_in_the_report(lifted_bci):
    _, document = lifted_bci
    evidence = document["boundary_evidence"]
    assert evidence["derived_from_rom"] is True
    assert evidence["problems"] == []
    assert evidence["dispatch_table"]["bounding_string_matches"] is True
    assert evidence["dispatch_table"]["entries"] == 31


def test_the_report_names_the_canonical_rom(lifted_bci):
    data, document = lifted_bci
    assert document["source_sha1"] == hashlib.sha1(data).hexdigest()
    assert document["target"]["rom_address"] == "0x08004038"
    assert document["target"]["byte_length"] == 296
    assert document["target"]["code_byte_length"] == 288


def test_the_committed_report_matches_a_fresh_run(lifted_bci):
    data, _ = lifted_bci
    result = lift.verify_report(data, "bci")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    """No path specific to the machine that produced the report.

    The one drive-letter path allowed is the GAME's own build path,
    T:\\Source\\ByteCodeInterpreter\\..., which is a ROM constant and the
    strongest provenance evidence in the document. It is a fact about the
    cartridge, not about this checkout, so it is asserted to be the ONLY one
    rather than banned.
    """
    raw = lift.report_path_for("bci").read_bytes()
    assert b"\r\n" not in raw, "the report must be LF-only"
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    assert "Program Files" not in text

    paths = set(re.findall(r"[A-Za-z]:\\\\[^\s\"']*", text))
    assert paths == {r"T:\\Source\\ByteCodeInterpreter\\ByteCodeInterpreter.cpp"}, paths
    assert json.loads(text)["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
