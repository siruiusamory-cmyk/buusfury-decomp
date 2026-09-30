"""DECOMP-RUNTIME-IWRAM-001: the runtime-installed IWRAM block and its veneers.

The ticket's target was IWRAM slot ``0x030007A8``, reached through the Thumb
trampoline at ``0x0804912C``. Two findings drive every test here:

* the trampoline does NOT dereference the slot - ``ldr pc,[pc,#-4]`` puts the
  stub's own literal into PC, so ``0x030007A8`` IS the destination; and
* that destination is filled at boot by the reset code's DMA3, so the code that
  runs there is statically known.

Both are re-derived from the cartridge on every run rather than remembered.

PORTABLE tests need no ROM and no toolchain. ROM-gated tests skip cleanly. The
ROM is opened READ-ONLY and nothing here writes to it.
"""

from __future__ import annotations

import json
import re

import pytest

from buusfury import gba, identity, lift

IWRAM_BASE = 0x03000000
IWRAM_END = 0x03001004
BLOB_ROM = 0x087B79A4
VENEER_FAMILY_FIRST = 0x08049120
VENEER_FAMILY_END = 0x080491CC


# ---------------------------------------------------------------------------
# the registry
# ---------------------------------------------------------------------------
def test_the_target_is_registered():
    target = lift.get_target("iwramblock")
    assert target.ticket == "DECOMP-RUNTIME-IWRAM-001"
    assert target.probe_translation_unit == "iwram_block_tu"
    assert target.rom_address == 0x087B810C
    assert target.isa == "arm"
    assert target.cpu == "arm7tdmi"
    assert target.semantic_minimum_checks == 160
    assert target.host_build_bits == 32


def test_it_is_the_first_arm_target_and_the_only_one():
    """Every earlier target is Thumb. If a second ARM target appears, this test
    should be widened deliberately rather than silently accept it.

    Widened deliberately by DECOMP-IWRAM-DISPATCH-001, which adds the second ARM
    target: the same copied block's interrupt dispatcher, entered from the BIOS
    IRQ vector rather than from a veneer. The list is still exact, so a third ARM
    target cannot appear without this test being widened again on purpose.
    """
    assert [t.id for t in lift.load_targets() if t.isa == "arm"] == [
        "iwramblock",
        "iwramdispatch",
    ]


def test_every_earlier_target_survives():
    """A FLOOR plus the named survivors, never an exact global count."""
    ids = [t.id for t in lift.load_targets()]
    assert len(ids) >= 20, ids
    for earlier in ("gbaram", "bci", "handler2", "operand", "stack", "arith", "use",
                    "effect", "flagread", "booluse", "clear", "gather", "flagmask",
                    "native178", "append", "collectionread", "collectionwrite2",
                    "collectioninsert2", "collectionflush3"):
        assert earlier in ids, earlier


def test_the_arm_immediate_rotation_is_applied():
    """The bug this pins: ARM reports a rotated immediate as TWO operands, so
    `mov r0, #64, #12` must be rotated into 0x04000000 rather than read as 0x40."""
    assert lift._arm_immediate(0xE3A00640) == 0x04000000   # mov r0, #64, #12
    assert lift._arm_immediate(0xE3811484) == 0x84000000   # orr r1, r1, #132, #8
    assert lift._arm_immediate(0xE3811485) == 0x85000000   # orr r1, r1, #0x85000000
    assert lift._arm_immediate(0xE3A00092) == 0x92


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def rom_bytes():
    try:
        rom = identity.resolve_baserom()
        identity.verify(rom)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"no canonical baserom available: {exc}")
    return rom.read_bytes()


_RUNTIME_CACHE: dict[int, dict] = {}


def runtime_of(rom_bytes: bytes) -> dict:
    """The derivation is re-run once per module rather than once per test.

    It walks the whole image for the veneer pattern and for BL candidates, which
    is a few seconds, and the answer cannot change while the fixture's bytes
    object is alive.
    """
    key = id(rom_bytes)
    if key not in _RUNTIME_CACHE:
        _RUNTIME_CACHE[key] = lift.derive_iwram_runtime(rom_bytes)
    return _RUNTIME_CACHE[key]


# ---------------------------------------------------------------------------
# the boundaries, re-derived by aligned chain-walk
# ---------------------------------------------------------------------------
def test_the_boundaries_are_derived_and_agree(rom_bytes):
    evidence = lift.derive_unit_boundaries(rom_bytes, "iwram_block_tu")
    assert evidence["problems"] == [], evidence["problems"]
    rows = evidence["functions"]
    assert [
        (r["start"], r["end"], r["size"], r["instructions"]) for r in rows
    ] == [
        ("0x087B810C", "0x087B814C", 64, 16),
        ("0x087B814C", "0x087B81A0", 84, 21),
        ("0x087B81A0", "0x087B81FC", 92, 23),
        ("0x087B81FC", "0x087B820C", 16, 4),
    ]
    for row in rows:
        assert row["gaps"] == [], row
        assert row["matches_expected"] is True, row


def test_the_unit_is_register_only_so_the_pool_test_is_not_applicable(rom_bytes):
    """Reported as not-applicable rather than failed: there is no pool at all."""
    evidence = lift.derive_unit_boundaries(rom_bytes, "iwram_block_tu")
    assert evidence["has_literal_pool"] is False
    assert evidence["pool_extent"] is None
    assert evidence["alignment_padding_bytes"] is None


# ---------------------------------------------------------------------------
# the install path
# ---------------------------------------------------------------------------
def test_the_install_path_is_read_from_the_reset_routine(rom_bytes):
    runtime = runtime_of(rom_bytes)
    setups = runtime["dma3_setups_in_the_reset_routine"]
    assert len(setups) == 2

    zero_fill, install = setups
    # First DMA3 setup: a source-fixed 32-bit fill of zeros from the stack.
    assert zero_fill["source_register_write"] == "0x00000000"
    assert zero_fill["destination_register_write"] == "0x03001004"
    assert zero_fill["control_register_write"] == "0x850010BE"
    assert zero_fill["source_address_fixed"] is True
    assert zero_fill["bytes_at_32_bits"] == 17144

    # Second DMA3 setup: the block copy that installs the code under test.
    assert install["source_register_write"] == "0x087B79A4"
    assert install["destination_register_write"] == "0x03000000"
    assert install["control_register_write"] == "0x84000401"
    assert install["count_low_half"] == "0x0401"
    assert install["source_address_fixed"] is False


def test_the_block_ends_where_the_first_dma_begins(rom_bytes):
    """The two DMA setups tile IWRAM with no gap between them."""
    runtime = runtime_of(rom_bytes)
    block = runtime["installed_block"]
    zero_fill = runtime["dma3_setups_in_the_reset_routine"][0]
    assert block["iwram_end"] == zero_fill["destination_register_write"]
    assert block["rom_end"] == "0x087B89A8"
    assert block["bytes"] == 4100
    assert block["verbatim"] is True


def test_the_transfer_width_is_decided_by_tiling_and_not_assumed(rom_bytes):
    """Both readings are reported; exactly one closes the block at both ends.

    DECOMP-IWRAM-DISPATCH-001 corrected the count of veneer destinations the
    16-bit reading would leave outside the copied block: it was prose saying
    "eight" in the docstring and in the report, and the measured value is three
    (0x03000858, 0x03000A4C, 0x03000CA0). The count is now DERIVED from the
    destination list, and this test pins the derivation rather than the prose, so
    it cannot drift back.
    """
    block = runtime_of(rom_bytes)["installed_block"]
    counts = block["transfer_width_byte_counts"]
    assert counts["32-bit"]["bytes"] == 4100
    assert counts["16-bit"]["bytes"] == 2050
    assert counts["32-bit"]["rom_ends_at_the_fill"] is True
    assert counts["32-bit"]["iwram_ends_at_the_second_region"] is True
    assert counts["16-bit"]["rom_ends_at_the_fill"] is False
    assert counts["16-bit"]["iwram_ends_at_the_second_region"] is False

    outside = block["veneer_destinations_outside_the_16_bit_reading"]
    assert [row["iwram"] for row in outside] == [
        "0x03000858",
        "0x03000A4C",
        "0x03000CA0",
    ]
    assert [row["rom"] for row in outside] == [
        "0x087B81FC",
        "0x087B83F0",
        "0x087B8644",
    ]
    # The 16-bit reading ends at 0x087B81A6, so every reported destination is at
    # or above it and every unreported one is below it.
    end_16 = 0x087B79A4 + 2050
    for row in outside:
        assert int(row["rom"], 16) >= end_16
    installed = [
        entry for entry in runtime_of(rom_bytes)["veneers"]["entries"]
        if entry["destination_state"] == "arm" and entry["target_is_installed_code"]
    ]
    assert len(installed) == 13
    assert len(outside) == 3
    assert "leaves 3 of the thirteen" in block["transfer_width_decided_by"]


def test_the_installed_image_is_a_verbatim_copy(rom_bytes):
    """IWRAM 0x03000000 + k == ROM 0x087B79A4 + k, checked at three addresses."""
    runtime = runtime_of(rom_bytes)
    for entry in runtime["veneers"]["entries"]:
        if not entry["target_is_installed_code"]:
            continue
        offset = int(entry["iwram_offset"], 16)
        rom_word = int.from_bytes(
            rom_bytes[BLOB_ROM - gba.ROM_BASE + offset:][:4], "little"
        )
        assert entry["rom_source"] == f"0x{BLOB_ROM + offset:08X}"
        assert int(entry["first_word"], 16) == rom_word


# ---------------------------------------------------------------------------
# the veneer family
# ---------------------------------------------------------------------------
def test_the_veneer_family_is_walked_not_declared(rom_bytes):
    family = runtime_of(rom_bytes)["veneers"]
    assert family["family_first"] == f"0x{VENEER_FAMILY_FIRST:08X}"
    assert family["family_end"] == f"0x{VENEER_FAMILY_END:08X}"
    assert family["family_bytes"] == 172
    assert family["entry_count"] == 15
    assert family["installed_code_destinations"] == 13
    assert family["rom_destinations"] == 2
    assert family["destinations_unique"] is True
    assert family["all_installed_destinations_are_arm"] is True
    assert sorted(family["forms"]) == ["thumb-to-arm-absolute", "thumb-to-arm-branch"]
    assert sorted({e["size"] for e in family["entries"]}) == [8, 12]


def test_the_slot_the_previous_ticket_could_not_resolve_is_resolved(rom_bytes):
    """The exact claim the ticket exists to settle."""
    family = runtime_of(rom_bytes)["veneers"]
    entry = next(e for e in family["entries"] if e["entry"] == "0x0804912C")
    assert entry["literal"] == "0xE51FF004", "ldr pc,[pc,#-4] and not a pointer load"
    assert entry["form"] == "thumb-to-arm-absolute"
    assert entry["size"] == 12
    assert entry["destination"] == "0x030007A8"
    assert entry["destination_state"] == "arm"
    assert entry["target_is_installed_code"] is True
    assert entry["rom_source"] == "0x087B814C"
    # `cmp r2, #0x20` is the first instruction that runs at the destination.
    assert entry["first_word"] == "0xE3520020"


def test_the_two_branch_form_veneer_targets_are_arm_code(rom_bytes):
    family = runtime_of(rom_bytes)["veneers"]
    branches = [e for e in family["entries"] if e["form"] == "thumb-to-arm-branch"]
    assert [e["entry"] for e in branches] == ["0x08049198", "0x080491A0"]
    assert [e["destination"] for e in branches] == ["0x08047040", "0x08047450"]
    for entry in branches:
        assert entry["destination_state"] == "arm"
        assert entry["decodes_as_arm"] is True


def test_every_installed_destination_lies_inside_the_copied_block(rom_bytes):
    family = runtime_of(rom_bytes)["veneers"]
    for entry in family["entries"]:
        if not entry["target_is_installed_code"]:
            continue
        destination = int(entry["destination"], 16)
        assert IWRAM_BASE <= destination < IWRAM_END, entry
        assert 0 <= int(entry["iwram_offset"], 16) < 4100, entry


# ---------------------------------------------------------------------------
# the four block-memory slots
# ---------------------------------------------------------------------------
def test_the_four_block_memory_slots_are_mapped(rom_bytes):
    slots = runtime_of(rom_bytes)["block_memory_slots"]
    assert slots["0x03000768"] == {
        "function": "sub_087B810C",
        "rom_source": "0x087B810C",
        "first_word": "0xE3520020",
        "reached_through": "0x08049138",
    }
    assert slots["0x030007A8"]["function"] == "sub_087B814C"
    assert slots["0x030007A8"]["rom_source"] == "0x087B814C"
    assert slots["0x030007A8"]["reached_through"] == "0x0804912C"
    assert slots["0x030007FC"]["function"] == "sub_087B81A0"
    assert slots["0x030007FC"]["reached_through"] == "0x08049144"
    assert slots["0x03000858"]["function"] == "sub_087B81FC"
    assert slots["0x03000858"]["reached_through"] == "0x08049168"


def test_the_block_memory_slots_are_named_only_by_their_own_veneers(rom_bytes):
    """The negative that explains why the earlier writer search failed.

    Each of these three slot addresses occurs in the image EXACTLY ONCE, and
    that occurrence is the veneer's own literal. Nothing stores them by absolute
    address, which is why no writer could be found by searching for one.
    """
    census = runtime_of(rom_bytes)["slot_addresses_in_the_image"]
    for slot, veneer, literal in (
        ("0x030007A8", "0x0804912C", "0x08049134"),
        ("0x03000768", "0x08049138", "0x08049140"),
        ("0x03000858", "0x08049168", "0x08049170"),
    ):
        row = census[slot]
        assert row["veneer"] == veneer
        assert row["veneer_literal_slot"] == literal
        assert row["occurrences_at_any_offset"] == [literal]
        assert row["occurs_only_as_the_veneer_literal"] is True


def test_the_halfword_copy_slot_has_one_stray_match_that_is_not_a_stored_word(rom_bytes):
    """Stated rather than rounded off: one extra match exists, at an ODD offset,
    where no 32-bit stored word can live."""
    census = runtime_of(rom_bytes)["slot_addresses_in_the_image"]
    row = census["0x030007FC"]
    assert row["veneer_literal_slot"] == "0x0804914C"
    extras = row["occurrences_other_than_the_veneer_literal"]
    assert len(extras) == 1, extras
    assert int(extras[0], 16) % 2 == 1, "an odd offset cannot hold a stored word"


def test_the_range_census_is_reported_as_a_summary_and_not_as_a_list(rom_bytes):
    """A full listing of the 4100-address range would be mostly compressed-data
    coincidences, so only the per-slot census is treated as evidence."""
    census = runtime_of(rom_bytes)["words_naming_the_block_anywhere_in_it"]
    assert census["distinct_value_count"] == len(census["distinct_values"])
    assert census["total_words"] >= census["distinct_value_count"]
    assert "per-slot census above is the decision-relevant one" in census["method"]
    # The block's own globals really are referenced from ROM code outside it.
    for value in ("0x03000F90", "0x03000FB0", "0x03000868"):
        assert value in census["distinct_values"], value


def test_every_veneer_has_thumb_callers_and_no_arm_caller(rom_bytes):
    """The ARM sweep is arithmetic over aligned words, so it has no alignment
    blind spot; the Thumb counts are a pattern scan and are reported as bounds."""
    callers = runtime_of(rom_bytes)["veneer_callers"]
    assert callers["arm_branch_sites_reaching_a_veneer"] == []
    assert "UPPER BOUND" in callers["method"]
    counts = callers["bound_counts_by_entry"]
    assert len(counts) == 15
    for entry, row in counts.items():
        assert row["pattern_scan_any_even_offset"] >= 1, entry
        assert (
            row["pattern_scan_four_byte_aligned"]
            <= row["pattern_scan_any_even_offset"]
        ), entry
    # The slot this ticket exists for is the second-heaviest caller target.
    assert counts["0x0804912C"]["pattern_scan_any_even_offset"] >= 10


# ---------------------------------------------------------------------------
# the source's discipline
# ---------------------------------------------------------------------------
def test_the_source_declares_the_four_functions_and_the_contract():
    source = (identity.REPO_ROOT / "src" / "IwramBlock.c").read_text("utf-8")
    for name in ("sub_087B810C", "sub_087B814C", "sub_087B81A0", "sub_087B81FC"):
        assert f"void {name}(" in source, name
    # The un-masked fill is the reason `r1` may carry an address, and it must be
    # stated rather than discovered.
    assert "NEVER masked" in source
    assert "0xE51FF004" in source


def test_the_source_adds_no_guard_and_names_nothing_semantically():
    source = (identity.REPO_ROOT / "src" / "IwramBlock.c").read_text("utf-8")
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    assert "assert" not in code
    assert "memcpy" not in code and "memset" not in code, (
        "the reconstruction must not borrow a library name for behaviour it proves"
    )
    for other in ("Legacy of Goku", "LOG1", "LOGII", "Buu", "Webfoot", "ads12", "ADS"):
        assert other not in code, other


def test_the_source_records_the_round_up_rather_than_guarding_it():
    source = (identity.REPO_ROOT / "src" / "IwramBlock.c").read_text("utf-8")
    assert "RUNS AT LEAST ONCE" in source
    assert "NO ZERO CHECK" in source


def test_the_probe_path_is_a_shim():
    shim = (identity.REPO_ROOT / "src" / "probes" / "IwramBlock.c").read_text("utf-8")
    assert '#include "../IwramBlock.c"' in shim
    assert "void sub_087B810C(" not in shim
    assert len(shim.splitlines()) < 30, "the shim has grown into a second copy"


# ---------------------------------------------------------------------------
# the correction this ticket carries
# ---------------------------------------------------------------------------
def test_the_refuted_claim_is_corrected_in_the_sibling_it_was_made_in():
    """DECOMP-LIFT-COLLECTION-INSERT3-001 recorded that the IWRAM call at
    0x0804912C was 'NOT statically resolvable'. It is resolvable, so the earlier
    artifacts must carry the correction rather than the refuted claim."""
    source = (identity.REPO_ROOT / "src" / "ByteCodeInterpreter_collectionflush3.c").read_text("utf-8")
    assert "jumps to whatever is stored at 0x030007A8" not in source
    assert "NOT statically resolvable" not in source
    assert "THAT WAS WRONG" in source

    doc = (identity.REPO_ROOT / "docs" / "LIFT_COLLECTIONFLUSH3.md").read_text("utf-8")
    assert "REFUTED" in doc
    assert "DECOMP-RUNTIME-IWRAM-001" in doc

    notes = lift.get_target("collectionflush3").notes
    assert "CORRECTED by DECOMP-RUNTIME-IWRAM-001" in notes
    assert "IS statically resolvable" in notes


# ---------------------------------------------------------------------------
# the full report
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def lifted(rom_bytes):
    toolchain = lift.discover_modern_toolchain()
    if toolchain is None:
        pytest.skip("no modern ARM toolchain available")
    return rom_bytes, lift.run_lift("iwramblock", rom_bytes, toolchain)


def test_all_three_verdicts_are_present_and_separate(lifted):
    _, document = lifted
    verdicts = document["verdicts"]
    assert set(verdicts) == {"semantic", "modern_build", "ads_match"}
    assert verdicts["semantic"]["status"] == "PROVEN", verdicts["semantic"]["detail"]
    assert verdicts["semantic"]["checks"] >= 160
    assert verdicts["semantic"]["failures"] == 0
    assert verdicts["modern_build"]["status"] == "PASS", verdicts["modern_build"]["detail"]
    assert verdicts["ads_match"]["status"] == "BLOCKED"
    assert verdicts["ads_match"]["not_inferable_from_modern_build"] is True


def test_no_match_is_claimed(lifted):
    """A modern ARM build of these four cannot be a match claim either."""
    _, document = lifted
    assert document["comparison"]["is_a_match_claim"] is False
    assert document["comparison"]["byte_identical"] is False
    assert document["comparison"]["differing_bytes_in_overlap"] > 0


def test_every_function_is_paired_by_name(lifted):
    _, document = lifted
    rows = document["functions"]
    assert [r["name"] for r in rows] == [
        "sub_087B810C", "sub_087B814C", "sub_087B81A0", "sub_087B81FC"
    ]
    for row in rows:
        assert row["modern_symbol_present"] is True, row["name"]
        assert row["modern"]["size"] > 0, row["name"]
        assert row["modern"]["instructions"] > 0, row["name"]
    assert [(r["original"]["size"], r["original"]["instructions"]) for r in rows] == [
        (64, 16), (84, 21), (92, 23), (16, 4)
    ]


def test_the_evidence_travels_with_the_report(lifted):
    _, document = lifted
    runtime = document["boundary_evidence"]["iwram_runtime"]
    assert runtime["derived_from_rom"] is True
    assert runtime["not_hand_written"] is True
    assert runtime["installed_block"]["bytes"] == 4100
    assert runtime["veneers"]["entry_count"] == 15
    assert document["boundary_evidence"]["method"].startswith("aligned chain-walk")


def test_the_committed_report_matches_a_fresh_run(lifted):
    data, _ = lifted
    result = lift.verify_report(data, "iwramblock")
    if result["exempted"]:
        assert "no host C compiler" in result["exempted"][0]
    assert result["ok"], result["problems"][:10]


def test_the_committed_report_is_environment_independent():
    raw = lift.report_path_for("iwramblock").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "devkitPro" not in text
    assert "buusfury-decomp" not in text
    document = json.loads(text)
    assert document["modern_build"]["toolchain"]["root"] == "<DEVKITARM>"
    assert document["target"]["rom_address"] == "0x087B810C"


def test_the_self_check_runs_the_reconstruction_and_reports_its_count():
    """The semantic verdict is a measurement, so the harness's own parser must
    see a real summary line, and the minimum must be enforced."""
    text = (identity.REPO_ROOT / "src" / "probes" / "iwramblock_selftest.c").read_text("utf-8")
    assert "check(s), %d failure(s)" in text
    assert "setvbuf(stdout, NULL, _IONBF, 0)" in text


@pytest.mark.parametrize("checks,expected", [(160, "PROVEN"), (159, "PARTIAL")])
def test_the_minimum_is_enforced(checks, expected):
    status, _detail = lift.semantic_verdict(0, checks, 0, minimum=160)
    assert status == expected
