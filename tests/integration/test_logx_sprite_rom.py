"""Read-only ROM-gated evidence for LOGX-SPRITE-001.

Only findings independently established in
``docs/research/LOGX_SPRITE_PROVENANCE.md`` are asserted here: the pointer run's
identity and extent, the folded accessor base's real meaning, the definition
object's physical layout and inline array, the byte the engine uses as that
array's bound (with the five sites that use it), the animation and frame records
the array reaches, the appearance join, and the full-census arithmetic.

The suite skips cleanly when the private canonical ROM is not configured and it
never writes to it.  No ROM-derived bytes are committed: every expectation is a
count, an address, an index, a short instruction encoding, or a header that the
provenance document already quotes.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.research import logx_char_probe
from tools.research import logx_sprite_probe as probe

# --- independently measured constants of the canonical image ----------------

#: Every ``ldr Rt,[pc,#imm]`` whose literal word is the definition array address.
EXPECTED_LITERAL_SITES = (0x0800015E, 0x0801713E)

#: The ten words the accessor's folded base reaches for ids 0..9.  They are the
#: inline array of the *last* definition object, not a run prefix.
EXPECTED_WORDS_BELOW_RUN = (
    0x086A6424, 0x086A7238, 0, 0, 0x086A7E7C, 0, 0, 0, 0, 0x086A899C,
)

#: The object that ends exactly where the run starts.
EXPECTED_OBJECT_ENDING_AT_RUN = {
    "count": 10,
    "object_address": 0x086B6B60,
    "inline_array": 0x086B6BB4,
    "object_end": 0x086B6BDC,
    "header_hex": "0400000a",
}

#: Headline census figures.  Each states its own population.
EXPECTED_DEFINITIONS = 297
EXPECTED_COUNT_MIN = 1
EXPECTED_COUNT_MAX = 23
EXPECTED_COUNT_DISTRIBUTION = {
    1: 12, 2: 41, 3: 1, 5: 2, 10: 51, 13: 44, 15: 1, 16: 3, 18: 9,
    19: 67, 20: 29, 21: 16, 22: 16, 23: 5,
}
EXPECTED_DISTINCT_FIELD_02 = 8
EXPECTED_FIELD_04_ZERO = 232
EXPECTED_FIELD_04_NONZERO = 65
EXPECTED_FIELD_50_NONZERO = 10
EXPECTED_FIELD_0C_NONZERO = 14

EXPECTED_ARRAY_SLOTS = 4070
EXPECTED_ARRAY_NON_NULL = 1721
EXPECTED_ARRAY_NULL = 2349
EXPECTED_ANIMATION_REFERENCES = 1721
EXPECTED_UNIQUE_ANIMATIONS = 1017
EXPECTED_FRAME_REFERENCES = 13660
EXPECTED_UNIQUE_FRAMES = 10980
EXPECTED_FRAME_MAX_REUSE = 4
EXPECTED_MAX_ANIMATION_REUSE = 16
EXPECTED_FRAME_COUNT_DISTRIBUTION = {
    1: 80, 2: 275, 3: 180, 4: 407, 5: 16, 6: 13, 7: 11, 8: 3, 9: 2,
    10: 2, 11: 24, 12: 2, 16: 2,
}
EXPECTED_PIECE_COUNT_DISTRIBUTION = {1: 10959, 2: 19, 4: 2}

EXPECTED_APPEARANCE_RECORDS = 232
EXPECTED_APPEARANCE_IDS = 198
EXPECTED_APPEARANCE_TARGETS = 198
EXPECTED_UNREFERENCED_RUN_INDICES = 99
EXPECTED_APPEARANCE_ID_MIN = 12
EXPECTED_APPEARANCE_ID_MAX = 306
EXPECTED_RUN_INDEX_MIN = 2
EXPECTED_RUN_INDEX_MAX = 296

#: The 65 structures whose ``+0x04`` holds ``structure - 0x100``.
EXPECTED_REMAP_STRUCTURES = 65
EXPECTED_REMAP_MIN_DEVIATIONS = 4
EXPECTED_REMAP_MAX_DEVIATIONS = 50

#: The two extent models: counted vs the accepted next-structure walk.
EXPECTED_MODEL_AGREEMENT = 232
EXPECTED_WALKED_SLOTS = 8230
EXPECTED_EXTRA_SLOTS = 4160

#: The five sites that read ``definition + 0x00`` and compare it with an index.
EXPECTED_COUNT_GUARDS = (
    (0x08013044, 0x08013046, 0x08013048, 0x0801304C, 7),
    (0x08013086, 0x08013088, 0x0801308A, 0x0801308E, 8),
    (0x080131D8, 0x080131DA, 0x080131DC, 0x080131E0, 7),
    (0x0802736A, 0x0802736C, 0x0802736E, 0x08027372, 1),
    (0x0802A28A, 0x0802A28E, 0x0802A290, 0x0802A294, 6),
)

#: The state -> animation-index table the engine applies before indexing.
EXPECTED_STATE_TABLE = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    17, 18, 19, 20, 21, 22, 23, 10, 11,
)

#: Raw header-and-array bytes of three representative definitions, quoted so a
#: reader can re-derive every field without trusting the parser.
DEFINITION_10_RAW = (
    "020000040000000010080a0400000000"
    "f8fffffff2ffffff1800000007000000"
    "f9fffffff3ffffff1700000007000000"
    "fafffffff1ffffff1600000007000000"
    "fafffffff1ffffff1600000007000000"
    "00000000c43a3c08c43a3c08"
)
DEFINITION_12_RAW = (
    "020000020000000010080a0400000000"
    "02000000e9ffffff0f00000008000000"
    "00000000e9ffffff0e00000007000000"
    "01000000eaffffff0e00000007000000"
    "02000000eaffffff0f00000007000000"
    "00000000404a3c08c4513c08"
)
DEFINITION_306_RAW = (
    "0a0000040000000010080a0400000000"
    "00000000e9ffffff0f00000008000000"
    "01000000e9ffffff1000000008000000"
    "01000000eaffffff1000000007000000"
    "00000000eaffffff0f00000007000000"
    "0000000024646a0838726a0800000000"
    "000000007c7e6a080000000000000000"
    "00000000000000009c896a08"
)

#: A representative animation record and its first frame record.
REPRESENTATIVE_DEFINITION_ID = 115
REPRESENTATIVE_ANIMATION = 0x0850C1DC
REPRESENTATIVE_ANIMATION_FRAMES = 2
REPRESENTATIVE_ANIMATION_TAIL = (0x2, 0x1, 0x400)
REPRESENTATIVE_FRAME = 0x0850C13C
REPRESENTATIVE_FRAME_BYTES = (0xF8, 0xE8, 0x20, 0x20)


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest().upper() == probe.CANONICAL_SHA256
    return data


# --- section A/B: the pointer run and its boundary ---------------------------


def test_pointer_run_identity_and_extent(canonical_bytes: bytes) -> None:
    """297 entries, ids 10..306, all in ROM, strictly ascending, all distinct."""
    report = probe.run_report(canonical_bytes)
    assert report["entry_count"] == probe.DEFINITION_ARRAY_ENTRY_COUNT == 297
    assert report["first_id"] == 10
    assert report["last_id"] == 306
    assert report["all_entries_in_rom"] is True
    assert report["strictly_ascending"] is True
    assert report["unique_targets"] == 297
    assert report["first_entry"] == "0x086a89d0"
    assert report["last_entry"] == "0x086b6b60"
    assert probe.definition_entry_address(0) == probe.DEFINITION_ARRAY_ADDRESS
    assert probe.definition_entry_address(296) == probe.DEFINITION_ARRAY_ADDRESS + 4 * 296


def test_pointer_run_terminator(canonical_bytes: bytes) -> None:
    """The word after the 297th entry is not a ROM pointer."""
    report = probe.run_report(canonical_bytes)
    assert report["word_after_run_hex"] == "03001068"
    assert report["word_after_run_in_rom"] is False
    assert probe.in_rom(canonical_bytes, 0x03001068) is False


def test_every_literal_reference_to_the_run(canonical_bytes: bytes) -> None:
    sites = probe.thumb_ldr_literal_sites(canonical_bytes)
    found = tuple(sorted(site for site, _, _ in sites[probe.DEFINITION_ARRAY_ADDRESS]))
    assert found == EXPECTED_LITERAL_SITES
    assert probe.DEFINITION_ARRAY_LITERAL_SITES == EXPECTED_LITERAL_SITES
    for site, _, pool in sites[probe.DEFINITION_ARRAY_ADDRESS]:
        assert probe._u32(canonical_bytes, pool) == probe.DEFINITION_ARRAY_ADDRESS


def test_folded_base_is_the_last_definition_s_inline_array(canonical_bytes: bytes) -> None:
    """The accessor's ``0x086B6BB4`` is not a run prefix; it is one object's array."""
    explanation = probe.folded_base_explanation(canonical_bytes)
    assert len(explanation["objects_ending_at_run"]) == 1
    found = explanation["objects_ending_at_run"][0]
    assert found["object_address"] == "0x086b6b60"
    assert found["inline_array"] == "0x086b6bb4"
    assert found["object_end"] == "0x086b6bdc"
    assert found["count"] == EXPECTED_OBJECT_ENDING_AT_RUN["count"]
    assert found["header_hex"] == EXPECTED_OBJECT_ENDING_AT_RUN["header_hex"]
    # The same words, read as the folded base's ten entries.
    assert tuple(probe.run_report(canonical_bytes)["words_below_run"]) == tuple(
        f"{value:#010x}" for value in EXPECTED_WORDS_BELOW_RUN
    )
    # Four of the ten are ROM pointers and six are null; the last one is the
    # word immediately below the run, and it is ascending with the run.
    assert probe.run_report(canonical_bytes)["words_below_run_in_rom"] == 4
    assert probe.run_report(canonical_bytes)["words_below_run_null"] == 6
    assert 0x086A899C < 0x086A89D0


def test_accessor_arithmetic(canonical_bytes: bytes) -> None:
    """``folded_base + 4*id`` is what both accessors compute."""
    assert probe.FOLDED_ARITHMETIC_BASE == probe.DEFINITION_ARRAY_ADDRESS - 0x28
    assert probe.definition_pointer(canonical_bytes, 10) == 0x086A89D0
    assert probe.definition_pointer(canonical_bytes, 11) == 0x086A8A2C
    assert probe.definition_pointer(canonical_bytes, 306) == 0x086B6B60
    assert probe.run_index_for_id(10) == 0
    assert probe.run_index_for_id(306) == 296
    # The run and the folded base agree entry for entry above the floor.
    for identifier in (12, 115, 137, 306):
        index = probe.run_index_for_id(identifier)
        assert probe.definition_pointer(canonical_bytes, identifier) == probe.read_run(
            canonical_bytes
        )[index]


# --- section C/E/F: the definition object -----------------------------------


def test_definition_census(canonical_bytes: bytes) -> None:
    census = probe.definition_census(canonical_bytes)
    assert census["counters"]["definitions"] == EXPECTED_DEFINITIONS
    assert census["count_distribution"] == EXPECTED_COUNT_DISTRIBUTION
    assert census["anomalies"] == []
    assert census["counters"]["field_04_zero"] == EXPECTED_FIELD_04_ZERO
    assert census["counters"]["field_50_nonzero"] == EXPECTED_FIELD_50_NONZERO
    assert census["counters"]["field_0c_nonzero"] == EXPECTED_FIELD_0C_NONZERO
    assert census["distinct"]["field_02"] == EXPECTED_DISTINCT_FIELD_02
    assert census["counters"]["size_zero"] == 0
    assert census["counters"]["field_04_not_a_rom_pointer"] == 0
    # The fixed block holds no ROM pointer, so it is not an array of pointers.
    definitions = probe.iter_definitions(canonical_bytes)
    assert all(
        not any(probe.in_rom(canonical_bytes, word) for word in definition.fixed_block)
        for definition in definitions
    )


def test_object_extent_and_inline_array(canonical_bytes: bytes) -> None:
    """Every object's array has exactly ``count`` words and ends at ``+0x54+4c``."""
    definitions = probe.iter_definitions(canonical_bytes)
    for definition in definitions:
        assert len(definition.array) == definition.count
        assert definition.end_address == (
            definition.address + probe.OBJECT_HEADER_SIZE + 4 * definition.count
        )
        assert definition.end_address <= probe.DEFINITION_ARRAY_ADDRESS + 4 * 297
    assert definitions[-1].end_address == probe.DEFINITION_ARRAY_ADDRESS


def test_definition_array_slots_are_sparse(canonical_bytes: bytes) -> None:
    summary = probe.definition_census(canonical_bytes)["array_slots"]
    assert summary["total_slots"] == EXPECTED_ARRAY_SLOTS
    assert summary["non_null_slots"] == EXPECTED_ARRAY_NON_NULL
    assert summary["null_slots"] == EXPECTED_ARRAY_NULL
    assert summary["index_zero_always_non_null"] is True
    assert summary["by_index"][0] == {"present": 297, "non_null": 297}
    assert summary["by_index"][22] == {"present": 5, "non_null": 5}


def test_animation_reference_arithmetic(canonical_bytes: bytes) -> None:
    references = probe.definition_census(canonical_bytes)["animation_references"]
    assert references["references"] == EXPECTED_ARRAY_SLOTS
    assert references["non_null_references"] == EXPECTED_ANIMATION_REFERENCES
    assert references["null_references"] == EXPECTED_ARRAY_NULL
    assert references["unique_targets"] == EXPECTED_UNIQUE_ANIMATIONS
    assert references["malformed_references"] == 0
    assert references["max_reuse"] == EXPECTED_MAX_ANIMATION_REUSE


def test_remap_pointer_invariant(canonical_bytes: bytes) -> None:
    """All 65 structures with ``+0x04`` point at the 256 bytes before them."""
    invariant = probe.definition_census(canonical_bytes)["remap_pointer_invariant"]
    assert invariant["structures_with_nonzero_field_04"] == EXPECTED_REMAP_STRUCTURES
    assert (
        invariant["structures_where_field_04_is_structure_minus_0x100"]
        == EXPECTED_REMAP_STRUCTURES
    )
    assert invariant["all_nonzero_field_04_hold_the_invariant"] is True
    assert invariant["minimum_block_deviations"] == EXPECTED_REMAP_MIN_DEVIATIONS
    assert invariant["maximum_block_deviations"] == EXPECTED_REMAP_MAX_DEVIATIONS


def test_extent_models_compared(canonical_bytes: bytes) -> None:
    """The counted extent agrees with the accepted walk only where data is packed."""
    models = probe.definition_census(canonical_bytes)["extent_models"]
    assert models["structures"] == EXPECTED_DEFINITIONS
    assert (
        models["structures_where_next_structure_follows_the_array"]
        == EXPECTED_MODEL_AGREEMENT
    )
    assert models["counted_slots"] == EXPECTED_ARRAY_SLOTS
    assert models["walked_slots"] == EXPECTED_WALKED_SLOTS
    assert models["extra_slots_the_walk_scans"] == EXPECTED_EXTRA_SLOTS
    # Every extra slot is a nonzero non-ROM word: the walk reads the 256-byte
    # blocks as if they were pointers, and the pointer filter discards them.
    assert models["extra_slots_nonzero"] == EXPECTED_EXTRA_SLOTS
    assert models["extra_slots_that_are_rom_pointers"] == 0


def test_representative_definitions_are_byte_exact(canonical_bytes: bytes) -> None:
    ten = probe.read_definition(canonical_bytes, 10)
    assert ten.address == 0x086A89D0
    assert ten.count == 2
    assert ten.size == 0x400
    assert ten.raw.hex() == DEFINITION_10_RAW
    twelve = probe.read_definition(canonical_bytes, 12)
    assert twelve.address == 0x086A8A88
    assert twelve.raw.hex() == DEFINITION_12_RAW
    last = probe.read_definition(canonical_bytes, 306)
    assert last.address == 0x086B6B60
    assert last.count == 10
    assert last.raw.hex() == DEFINITION_306_RAW
    assert last.array == EXPECTED_WORDS_BELOW_RUN


# --- section C/E: the count-guarded array reads ------------------------------


def test_the_engine_bounds_the_inline_array_with_the_count(
    canonical_bytes: bytes,
) -> None:
    """Five sites read ``definition + 0x00`` and compare it with a live index."""
    report = probe.count_guard_report(canonical_bytes)
    assert tuple(
        (int(entry["pointer_site"], 16), int(entry["count_site"], 16),
         int(entry["compare_site"], 16), int(entry["array_site"], 16), entry["index"])
        for entry in report
    ) == EXPECTED_COUNT_GUARDS
    for entry in report:
        index = entry["index"]
        assert entry["array_offset"] == f"{probe.FIELD_ARRAY + 4 * index:#04x}"
        pointer, count, compare, array = (
            probe.instruction_at(canonical_bytes, int(entry["pointer_site"], 16)),
            probe.instruction_at(canonical_bytes, int(entry["count_site"], 16)),
            probe.instruction_at(canonical_bytes, int(entry["compare_site"], 16)),
            probe.instruction_at(canonical_bytes, int(entry["array_site"], 16)),
        )
        assert pointer[0] == "ldr"
        assert count[0] == "ldrb"
        assert compare[0] == "cmp"
        assert f"#{index}" in f"{compare[0]} {compare[1]}"
        assert array[0] == "ldr"
        assert f"#{probe.FIELD_ARRAY + 4 * index:#x}" in f"{array[0]} {array[1]}"


def test_definition_count_is_read_as_a_byte(canonical_bytes: bytes) -> None:
    """``+0x00``'s high byte is zero everywhere, so the count is one byte wide."""
    definitions = probe.iter_definitions(canonical_bytes)
    assert all(definition.field_00 >> 8 == 0 for definition in definitions)
    assert all(
        probe.COUNT_MIN <= definition.count <= probe.COUNT_MAX
        for definition in definitions
    )
    # The load registers at the five guard sites differ, so the byte is read
    # into a general register rather than consumed as part of a word.
    for name in ("guard_1_count", "guard_6_count", "guard_7_count", "guard_8_count"):
        mnemonic, operands, raw = probe.instruction_at(
            canonical_bytes, probe.EVIDENCE_INSTRUCTIONS[name][0]
        )
        assert mnemonic == "ldrb"
        assert "]" in operands
        assert len(raw) == 2


def test_definition_size_is_a_u16_passed_to_the_allocator(
    canonical_bytes: bytes,
) -> None:
    """``+0x02`` is read with ``ldrh`` and handed to the byte allocator."""
    sites = (0x0800EB7C, 0x0800EC00)
    for site in sites:
        mnemonic, operands, _ = probe.instruction_at(canonical_bytes, site)
        assert mnemonic == "ldrh"
        assert "#2" in operands
    sizes = {definition.size for definition in probe.iter_definitions(canonical_bytes)}
    assert sizes == {0x0040, 0x0100, 0x0200, 0x0400, 0x0800, 0x1000, 0x1800, 0x2400}


# --- section F/H/I: selection -------------------------------------------------


def test_state_table_is_a_translation_not_an_identity(canonical_bytes: bytes) -> None:
    report = probe.state_table_report(canonical_bytes)
    assert tuple(report["entries"]) == EXPECTED_STATE_TABLE
    assert report["identity_prefix"] is True
    assert report["max_index"] == 23
    # States 23 and 24 alias animation indices 10 and 11, so the mapping is a
    # translation table and not one fixed slot per state.
    assert report["entries"][23] == 10
    assert report["entries"][24] == 11


def test_animation_selection_reads_the_inline_array(
    canonical_bytes: bytes,
) -> None:
    """``0x0800ECDA`` indexes the array by the caller's animation index."""
    for name in (
        "select_direct_pointer", "select_direct_scale", "select_direct_base",
        "select_direct_load", "select_direct_store",
        "select_state_offset", "select_state_lookup", "select_state_array",
        "select_state2_lookup", "select_state2_array",
        "part_base", "part_row_scale", "part_row_add",
        "part_column_scale", "part_column_add", "part_load", "part_store",
    ):
        address, expected = probe.EVIDENCE_INSTRUCTIONS[name]
        mnemonic, operands, _ = probe.instruction_at(canonical_bytes, address)
        assert f"{mnemonic} {operands}".rstrip() == expected
    # The direct selector's arithmetic is exactly `def + 4*index + 0x54`.
    assert probe.instruction_at(canonical_bytes, 0x0800ECDC)[0] == "lsls"
    assert "r1, r1, #2" in probe.instruction_at(canonical_bytes, 0x0800ECDC)[1]
    assert "#0x54" in probe.instruction_at(canonical_bytes, 0x0800ECE0)[1]


def test_frame_selection_indexes_the_animation_two_dimensionally(
    canonical_bytes: bytes,
) -> None:
    """``16*frame + 4*direction + 4`` is the engine's own slot arithmetic."""
    assert "#4" in probe.instruction_at(canonical_bytes, 0x0800EF3C)[1]
    assert "#2" in probe.instruction_at(canonical_bytes, 0x0800EF42)[1]
    assert "#4" in probe.instruction_at(canonical_bytes, 0x0800EF46)[1]
    animation = probe.read_animation(canonical_bytes, REPRESENTATIVE_ANIMATION)
    assert animation.frame_count == REPRESENTATIVE_ANIMATION_FRAMES
    # The engine's arithmetic and the record's flat layout agree.
    for frame in range(animation.frame_count):
        for direction in range(probe.ANIM_DIRECTIONS):
            offset = probe.ANIM_POINTERS + 16 * frame + 4 * direction
            assert animation.pointer_for(frame, direction) == probe._u32(
                canonical_bytes, REPRESENTATIVE_ANIMATION + offset
            )


# --- section D/L: animations and frames ---------------------------------------


def test_animation_census(canonical_bytes: bytes) -> None:
    census = probe.animation_census(canonical_bytes)
    assert census["unique_animations"] == EXPECTED_UNIQUE_ANIMATIONS
    assert census["frame_count_distribution"] == EXPECTED_FRAME_COUNT_DISTRIBUTION
    assert census["frame_references"] == EXPECTED_FRAME_REFERENCES
    assert census["unique_frames"] == EXPECTED_UNIQUE_FRAMES
    assert census["frame_max_reuse"] == EXPECTED_FRAME_MAX_REUSE
    assert census["max_animation_reuse"] == EXPECTED_MAX_ANIMATION_REUSE
    # Reference and unique counts are different populations.
    assert census["frame_references"] > census["unique_frames"]


def test_frame_records_and_the_constructor_boundary(canonical_bytes: bytes) -> None:
    census = probe.frame_record_census(canonical_bytes)
    assert census["unique_frames"] == EXPECTED_UNIQUE_FRAMES
    assert census["piece_count_distribution"] == EXPECTED_PIECE_COUNT_DISTRIBUTION
    assert census["frames_fully_inside_the_image"] == EXPECTED_UNIQUE_FRAMES
    frames, trailer_0, trailer_1 = probe.read_animation_tail(
        canonical_bytes, REPRESENTATIVE_ANIMATION
    )
    assert (frames, trailer_0, trailer_1) == REPRESENTATIVE_ANIMATION_TAIL
    record = probe.read_frame_record(canonical_bytes, REPRESENTATIVE_FRAME)
    assert record.piece_count == 1
    assert (
        record.byte_04, record.byte_05, record.byte_06, record.byte_07
    ) == REPRESENTATIVE_FRAME_BYTES
    assert record.signed_04 == -8
    assert record.signed_05 == -24
    assert record.end_address == REPRESENTATIVE_FRAME + 4 + 16
    assert probe.instruction_at(canonical_bytes, 0x080273F0)[0] == "ldrsb"
    assert probe.instruction_at(canonical_bytes, 0x080273F4)[0] == "ldrsb"
    assert "#6" in probe.instruction_at(canonical_bytes, 0x0802740C)[1]
    assert "#7" in probe.instruction_at(canonical_bytes, 0x08027410)[1]
    assert probe.instruction_at(canonical_bytes, 0x0802740C)[0] == "ldrb"
    assert probe.instruction_at(canonical_bytes, 0x08027410)[0] == "ldrb"


# --- section M: the appearance join -------------------------------------------


def test_appearance_join(canonical_bytes: bytes) -> None:
    join = probe.appearance_join(canonical_bytes)
    assert join["appearance_records"] == EXPECTED_APPEARANCE_RECORDS
    assert join["ids_used"] == EXPECTED_APPEARANCE_IDS
    assert join["unique_targets"] == EXPECTED_APPEARANCE_TARGETS
    assert join["unreferenced_run_indices"] == EXPECTED_UNREFERENCED_RUN_INDICES
    assert join["id_min"] == EXPECTED_APPEARANCE_ID_MIN
    assert join["id_max"] == EXPECTED_APPEARANCE_ID_MAX
    assert join["run_index_min"] == EXPECTED_RUN_INDEX_MIN
    assert join["run_index_max"] == EXPECTED_RUN_INDEX_MAX
    assert join["every_id_in_run"] is True
    assert len(join["shared_by_multiple_appearances"]) == 25
    # LOGX-CHAR-001's relationship is reused, not re-derived.
    assert logx_char_probe.CHAR_RECORD_COUNT == EXPECTED_APPEARANCE_RECORDS
    assert logx_char_probe.FIELD_04_ID_FLOOR == probe.DEFINITION_ID_FLOOR


# --- engine evidence ----------------------------------------------------------


def test_every_quoted_instruction_matches_the_image(canonical_bytes: bytes) -> None:
    for name, (address, expected) in probe.EVIDENCE_INSTRUCTIONS.items():
        mnemonic, operands, _ = probe.instruction_at(canonical_bytes, address)
        assert f"{mnemonic} {operands}".rstrip() == expected, name


def test_evidence_sites_are_even_and_unique() -> None:
    addresses = [address for address, _ in probe.EVIDENCE_INSTRUCTIONS.values()]
    assert len(addresses) == len(set(addresses))
    assert all(address % 2 == 0 for address in addresses)


# --- determinism and the canonical gate ---------------------------------------


def test_reports_are_deterministic(canonical_bytes: bytes) -> None:
    first = probe.definition_census(canonical_bytes)
    second = probe.definition_census(canonical_bytes)
    assert first == second
    assert probe.run_report(canonical_bytes) == probe.run_report(canonical_bytes)
    assert probe.animation_census(canonical_bytes) == probe.animation_census(
        canonical_bytes
    )


def test_canonical_gate_rejects_a_non_canonical_image() -> None:
    with pytest.raises(probe.SpriteProbeError, match="expected"):
        probe.verify_canonical(b"\x00" * 16)
    with pytest.raises(probe.SpriteProbeError, match="non-canonical"):
        probe.verify_canonical(b"\x00" * probe.ROM_SIZE)
