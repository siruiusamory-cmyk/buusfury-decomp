"""Read-only ROM-gated evidence for LOGX-SPRITE-001.

Only findings independently established in
``docs/research/LOGX_SPRITE_PROVENANCE.md`` are asserted here: the pointer run's
identity and extent, the folded accessor base's real meaning, the definition
object's physical layout and inline array, the byte the engine uses as that
array's bound (with the five sites that use it), the animation and frame records
the array reaches, the appearance join, and the full-census arithmetic.

The suite skips cleanly when the private canonical ROM is not configured and it
never writes to it.  **No ROM-derived fixtures are committed**: every expectation
here is a count, an address, an index, a field value, a short instruction
encoding, or a permutation of the file's own decoded output.  The one byte-level
check compares the probe's packed dump against the fields the probe decoded from
it, which is a round-trip invariant rather than a stored payload.
"""

from __future__ import annotations

import hashlib
import os
import struct
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
    "object_address": "0x086b6b60",
    "inline_array": "0x086b6bb4",
    "object_end": "0x086b6bdc",
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
#: ``DEFINITIONS`` counts structure boundaries (296 consecutive pairs plus the
#: run terminus); ``PAIRS`` counts only the 296 definitions that have a next
#: definition.  Both populations are asserted so neither can be read as the
#: other.
EXPECTED_EXTENT_MODEL_DEFINITIONS_AGREEING = 232
EXPECTED_EXTENT_MODEL_PAIRS = 296
EXPECTED_EXTENT_MODEL_PAIRS_AGREEING = 231
EXPECTED_WALKED_SLOTS = 8230
EXPECTED_EXTRA_SLOTS = 4160

#: The five sites that read ``definition + 0x00`` and compare it with an index,
#: each followed by the null test on the element it loaded.
EXPECTED_COUNT_GUARDS = (
    (0x08013044, 0x08013046, 0x08013048, 0x0801304C, 0x0801304E, 7),
    (0x08013086, 0x08013088, 0x0801308A, 0x0801308E, 0x08013090, 8),
    (0x080131D8, 0x080131DA, 0x080131DC, 0x080131E0, 0x080131E2, 7),
    (0x0802736A, 0x0802736C, 0x0802736E, 0x08027372, 0x08027374, 1),
    (0x0802A28A, 0x0802A28E, 0x0802A290, 0x0802A294, 0x0802A296, 6),
)

#: The array offset each guard's load instruction uses, written out literally so
#: the expectation cannot be re-derived from the probe's own expression.
EXPECTED_GUARD_ARRAY_OFFSETS = {1: "0x58", 6: "0x6c", 7: "0x70", 8: "0x74"}

#: The state -> animation-index table the engine applies before indexing, and
#: the byte string immediately after it (not part of the table).
EXPECTED_STATE_TABLE = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    17, 18, 19, 20, 21, 22, 23, 10, 11,
)
EXPECTED_STATE_TABLE_BYTES_AFTER = "000000000000000100000000000000ffffffffffffffff00"
EXPECTED_STATE_TABLE_LOOKUP_SITES = (
    "0x0800ecf6", "0x0800ed48", "0x0802cb96", "0x0800eeb6",
)

#: The animation selector's argument census.
EXPECTED_SELECTOR_SITES = 162
EXPECTED_SELECTOR_CONSTANT_HISTOGRAM = {
    0: 9, 1: 8, 3: 10, 4: 5, 7: 2, 9: 4, 10: 2, 11: 1, 12: 4,
    14: 4, 15: 3, 16: 3, 17: 3, 18: 54, 19: 28, 20: 14, 21: 7,
}

#: Definition fields of four representatives, quoted as values rather than as
#: raw bytes.  ``raw`` is still checked, but only against the fields the parser
#: decoded from it (a round-trip), never against a stored dump.
EXPECTED_REPRESENTATIVE_DEFINITIONS = {
    10: {
        "address": 0x086A89D0, "count": 2, "size": 0x400, "field_04": 0,
        "field_08": 0x040A0810, "field_0c": 0, "field_50": 0,
        "array": (0x083C3AC4, 0x083C3AC4),
    },
    12: {
        "address": 0x086A8A88, "count": 2, "size": 0x200, "field_04": 0,
        "field_08": 0x040A0810, "field_0c": 0, "field_50": 0,
        "array": (0x083C4A40, 0x083C51C4),
    },
    115: {
        "address": 0x086AD1CC, "count": 22, "size": 0x400, "field_04": 0,
        "field_08": 0x040A0810, "field_0c": 0, "field_50": 0,
        "array": (
            0x0850C1DC, 0x0850CF74, 0x0850DD14, 0x0850E7DC, 0x0850F68C,
            0x085104E8, 0x0851131C, 0x085116A0, 0x08511A98, 0x08512564,
            0x08512CD8, 0, 0x085133B4, 0x08513668, 0x085140A4, 0x085149C8,
            0x0851506C, 0x08515534, 0x08515F5C, 0x085166AC, 0, 0x0851754C,
        ),
    },
    306: {
        "address": 0x086B6B60, "count": 10, "size": 0x400, "field_04": 0,
        "field_08": 0x040A0810, "field_0c": 0, "field_50": 0,
        "array": (0x086A6424, 0x086A7238, 0, 0, 0x086A7E7C, 0, 0, 0, 0, 0x086A899C),
    },
}

#: A representative animation record and its first frame record.
REPRESENTATIVE_DEFINITION_ID = 115
REPRESENTATIVE_ANIMATION = 0x0850C1DC
REPRESENTATIVE_ANIMATION_FRAMES = 2
REPRESENTATIVE_ANIMATION_POINTERS = (
    0x0850C13C, 0x0850C164, 0x0850C18C, 0x0850C1B4,
    0x0850C150, 0x0850C178, 0x0850C1A0, 0x0850C1C8,
)
REPRESENTATIVE_ANIMATION_TAIL = (0x2, 0x1, 0x400)
REPRESENTATIVE_FRAME = 0x0850C13C
REPRESENTATIVE_FRAME_BYTES = (0xF8, 0xE8, 0x20, 0x20)

#: Trailer histograms over the 1,017 unique animation records.  The first word
#: is 1 in 1,006 of them and takes six other raw values; the second word takes
#: 21 distinct values, five of which cover 974 records.
EXPECTED_TRAILER_0 = {
    1: 1006,
    3825263616: 6,
    3423128584: 1,
    3825787912: 1,
    3808486144: 1,
    3475558184: 1,
    67108866: 1,
}
EXPECTED_TRAILER_1_DISTINCT = 21
EXPECTED_TRAILER_1_TOP = {512: 430, 1024: 379, 4096: 116, 2048: 38, 256: 11}


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
    assert found["object_address"] == EXPECTED_OBJECT_ENDING_AT_RUN["object_address"]
    assert found["inline_array"] == EXPECTED_OBJECT_ENDING_AT_RUN["inline_array"]
    assert found["object_end"] == EXPECTED_OBJECT_ENDING_AT_RUN["object_end"]
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
    slots = probe.definition_census(canonical_bytes)["animation_references"]
    assert slots["slots"] == EXPECTED_ARRAY_SLOTS
    assert slots["non_null_slots"] == EXPECTED_ANIMATION_REFERENCES
    assert slots["null_slots"] == EXPECTED_ARRAY_NULL
    assert slots["unique_targets"] == EXPECTED_UNIQUE_ANIMATIONS
    assert slots["malformed_slots"] == 0
    assert slots["max_reuse"] == EXPECTED_MAX_ANIMATION_REUSE
    # Reference counts and unique-target counts are different populations and
    # the key names say which is which.
    assert slots["slots"] > slots["unique_targets"]


def test_remap_pointer_invariant(canonical_bytes: bytes) -> None:
    """All 65 structures with ``+0x04`` point at the 256 bytes before them, and
    they are exactly the 65 preceded by such a block."""
    invariant = probe.definition_census(canonical_bytes)["remap_pointer_invariant"]
    assert invariant["structures_with_nonzero_field_04"] == EXPECTED_REMAP_STRUCTURES
    assert (
        invariant["structures_where_field_04_is_structure_minus_0x100"]
        == EXPECTED_REMAP_STRUCTURES
    )
    assert invariant["all_nonzero_field_04_hold_the_invariant"] is True
    assert invariant["minimum_block_deviations"] == EXPECTED_REMAP_MIN_DEVIATIONS
    assert invariant["maximum_block_deviations"] == EXPECTED_REMAP_MAX_DEVIATIONS
    # The two 65-element sets are the same set: every structure with the field
    # is preceded by the block, and every structure preceded by a block has it.
    definitions = probe.iter_definitions(canonical_bytes)
    addresses = [d.address for d in definitions]
    preceded = {
        index
        for index in range(1, len(definitions))
        if addresses[index] - definitions[index - 1].end_address
        == probe.REMAP_BLOCK_SIZE
    }
    pointed = {
        index
        for index, definition in enumerate(definitions)
        if definition.field_04 == definition.address - probe.REMAP_BLOCK_SIZE
    }
    assert preceded == pointed
    assert len(preceded) == EXPECTED_REMAP_STRUCTURES


def test_extent_models_compared(canonical_bytes: bytes) -> None:
    """The counted extent agrees with the accepted walk only where data is packed."""
    models = probe.definition_census(canonical_bytes)["extent_models"]
    assert models["structures"] == EXPECTED_DEFINITIONS
    # Both populations are checked, so neither can be read as the other:
    # 231 of the 296 consecutive pairs, and 232 of the 297 structure
    # boundaries once the last structure is measured against the run itself.
    assert models["consecutive_pairs"] == EXPECTED_EXTENT_MODEL_PAIRS
    assert (
        models["consecutive_pairs_where_the_next_definition_starts_at_the_counted_end"]
        == EXPECTED_EXTENT_MODEL_PAIRS_AGREEING
    )
    assert (
        models["structures_where_the_counted_end_is_the_next_boundary"]
        == EXPECTED_EXTENT_MODEL_DEFINITIONS_AGREEING
    )
    assert (
        EXPECTED_EXTENT_MODEL_PAIRS_AGREEING + EXPECTED_FIELD_04_NONZERO
        == EXPECTED_EXTENT_MODEL_PAIRS
    )
    assert (
        EXPECTED_EXTENT_MODEL_DEFINITIONS_AGREEING + EXPECTED_FIELD_04_NONZERO
        == EXPECTED_DEFINITIONS
    )
    assert models["counted_slots"] == EXPECTED_ARRAY_SLOTS
    assert models["walked_slots"] == EXPECTED_WALKED_SLOTS
    assert models["extra_slots_the_walk_scans"] == EXPECTED_EXTRA_SLOTS
    # Every extra slot is a nonzero non-ROM word: the walk reads the 256-byte
    # blocks as if they were pointers, and the pointer filter discards them.
    assert models["extra_slots_nonzero"] == EXPECTED_EXTRA_SLOTS
    assert models["extra_slots_that_are_rom_pointers"] == 0


def test_counted_end_is_the_next_boundary_for_the_packed_run(
    canonical_bytes: bytes,
) -> None:
    """Every one of the 65 disagreements is exactly the 256-byte remap block;
    the block belongs to the object that *follows* it."""
    definitions = probe.iter_definitions(canonical_bytes)
    addresses = [d.address for d in definitions]
    gaps = 0
    for index, definition in enumerate(definitions):
        next_start = (
            addresses[index + 1]
            if index + 1 < len(addresses)
            else probe.DEFINITION_ARRAY_ADDRESS
        )
        delta = next_start - definition.end_address
        assert delta >= 0
        if delta:
            gaps += 1
            assert delta == probe.REMAP_BLOCK_SIZE
            # The gap, not this object, carries the block pointer: the
            # successor's +0x04 is the gap's own address.
            assert definitions[index + 1].field_04 == definition.end_address
        preceded = (
            index > 0
            and definition.address - definitions[index - 1].end_address
            == probe.REMAP_BLOCK_SIZE
        )
        if preceded:
            assert definition.field_04 == definition.address - probe.REMAP_BLOCK_SIZE
        else:
            assert definition.field_04 == 0
    assert gaps == EXPECTED_FIELD_04_NONZERO


def test_representative_definitions_decode_exactly(canonical_bytes: bytes) -> None:
    """Field values are asserted directly; the packed dump is a round trip."""
    for identifier, expected in EXPECTED_REPRESENTATIVE_DEFINITIONS.items():
        definition = probe.read_definition(canonical_bytes, identifier)
        assert definition.address == expected["address"], identifier
        assert definition.count == expected["count"], identifier
        assert definition.size == expected["size"], identifier
        assert definition.field_00 == expected["count"], identifier
        assert definition.field_04 == expected["field_04"], identifier
        assert definition.field_08 == expected["field_08"], identifier
        assert definition.field_0C == expected["field_0c"], identifier
        assert definition.field_50 == expected["field_50"], identifier
        assert definition.array == expected["array"], identifier
        # The dump is exactly the engine's extent, and re-reading it returns the
        # same fields: a drift in packing or in a width fails here.
        assert len(definition.raw) == probe.OBJECT_HEADER_SIZE + 4 * definition.count
        assert struct.unpack_from("<HHIII", definition.raw, 0) == (
            definition.field_00, definition.field_02, definition.field_04,
            definition.field_08, definition.field_0C,
        )
        assert (
            struct.unpack_from("<I", definition.raw, probe.FIELD_50)[0]
            == definition.field_50
        )
        assert struct.unpack_from(
            f"<{definition.count}I", definition.raw, probe.FIELD_ARRAY
        ) == definition.array


# --- section C/E: the count-guarded array reads ------------------------------


def test_the_engine_bounds_the_inline_array_with_the_count(
    canonical_bytes: bytes,
) -> None:
    """Five sites read ``definition + 0x00``, compare it with a live index, load
    that element, and then null-test it."""
    report = probe.count_guard_report(canonical_bytes)
    assert tuple(
        (int(entry["pointer_site"], 16), int(entry["count_site"], 16),
         int(entry["compare_site"], 16), int(entry["array_site"], 16),
         int(entry["null_test_site"], 16), entry["index"])
        for entry in report
    ) == EXPECTED_COUNT_GUARDS
    for entry in report:
        index = entry["index"]
        # Written out literally, not re-derived from the probe's expression.
        assert entry["array_offset"] == EXPECTED_GUARD_ARRAY_OFFSETS[index]
        pointer, count, compare, array, null_test = (
            probe.instruction_at(canonical_bytes, int(entry["pointer_site"], 16)),
            probe.instruction_at(canonical_bytes, int(entry["count_site"], 16)),
            probe.instruction_at(canonical_bytes, int(entry["compare_site"], 16)),
            probe.instruction_at(canonical_bytes, int(entry["array_site"], 16)),
            probe.instruction_at(canonical_bytes, int(entry["null_test_site"], 16)),
        )
        assert pointer[0] == "ldr"
        assert count[0] == "ldrb"
        assert compare[0] == "cmp"
        assert compare[1].split(",")[-1].strip() == f"#{index}"
        assert array[0] == "ldr"
        assert array[1].split(",")[-1].strip() == f"#{EXPECTED_GUARD_ARRAY_OFFSETS[index]}]"
        # The load is immediately followed by a null test on the element.
        assert null_test[0] == "cmp"
        assert null_test[1].split(",")[-1].strip() == "#0"
        # And the branch that acts on it is the very next instruction.
        branch = probe.instruction_at(
            canonical_bytes, int(entry["null_test_site"], 16) + 2
        )
        assert branch[0] in ("beq", "bne")


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
    assert report["max_value"] == 23
    assert report["largest_state"] == 24
    # States 23 and 24 alias animation indices 10 and 11, so the mapping is a
    # translation table and not one fixed slot per state.
    assert report["entries"][23] == 10
    assert report["entries"][24] == 11
    # The bytes after the table are not part of it: index 32 holds 1 and
    # indices 40..47 hold 0xFF, so "above 24 is zero" would be false.
    assert report["bytes_after_table_hex"] == EXPECTED_STATE_TABLE_BYTES_AFTER
    assert report["size"] == 25
    # The reader set is asserted as literals so a probe constant cannot make a
    # missing reader invisible.
    assert report["lookup_sites"] == list(EXPECTED_STATE_TABLE_LOOKUP_SITES)
    assert len(report["address_literal_sites"]) == 1
    assert (
        report["address_literal_sites"][0]["site"]
        == f"{probe.STATE_TABLE_ADDRESS_LITERAL_SITE:#010x}"
    )
    for site in probe.STATE_TABLE_LITERAL_SITES:
        assert probe.instruction_at(canonical_bytes, site)[0] == "adds"
        assert "#0x88" in probe.instruction_at(canonical_bytes, site)[1]
    for site in probe.STATE_TABLE_LOOKUP_SITES:
        assert probe.instruction_at(canonical_bytes, site)[0] == "ldrb"
    # The fourth reader reaches the table from the other literal in the same
    # structure, with +0x80 instead of +0x88, and uses it as a predicate.
    assert probe.instruction_at(canonical_bytes, 0x0800EEB0)[0] == "ldr"
    assert "#0x80" in probe.instruction_at(canonical_bytes, 0x0800EEB4)[1]
    assert probe.instruction_at(canonical_bytes, 0x0800EEC0)[0] == "cmp"


def test_selector_argument_census(canonical_bytes: bytes) -> None:
    """The direct selector takes a compile-time index at almost every call site."""
    census = probe.selector_argument_census(canonical_bytes)
    assert census["call_sites"] == EXPECTED_SELECTOR_SITES
    assert census["constant_index_histogram"] == EXPECTED_SELECTOR_CONSTANT_HISTOGRAM
    assert census["constant_index_count"] == sum(
        EXPECTED_SELECTOR_CONSTANT_HISTOGRAM.values()
    )
    assert census["max_constant_index"] == 21
    assert census["runtime_index_sites"] == 1
    assert census["unresolved_sites"] == 0
    # The one runtime index is the inlined state-table lookup.
    assert probe.instruction_at(canonical_bytes, 0x0802CB9A)[0] == "bl"
    assert probe.instruction_at(canonical_bytes, 0x0802CB96)[0] == "ldrb"


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
    # The pointers are written out literally, so this is not a restatement of
    # how the animation was read.
    assert animation.pointers == REPRESENTATIVE_ANIMATION_POINTERS
    # The engine's two-dimensional arithmetic selects the same element as the
    # record's flat order: slot d of frame f is flat index 4*f + d.
    for frame in range(animation.frame_count):
        for direction in range(probe.ANIM_DIRECTIONS):
            flat = 4 * frame + direction
            assert (
                animation.pointer_for(frame, direction)
                == REPRESENTATIVE_ANIMATION_POINTERS[flat]
            )


# --- section D/L: animations and frames ---------------------------------------


def test_animation_census(canonical_bytes: bytes) -> None:
    census = probe.animation_census(canonical_bytes)
    assert census["unique_animations"] == EXPECTED_UNIQUE_ANIMATIONS
    assert census["frame_count_distribution"] == EXPECTED_FRAME_COUNT_DISTRIBUTION
    assert (
        census["frame_slots_over_unique_animations"] == EXPECTED_FRAME_REFERENCES
    )
    assert census["unique_frames"] == EXPECTED_UNIQUE_FRAMES
    assert census["frame_max_reuse"] == EXPECTED_FRAME_MAX_REUSE
    assert census["max_animation_reuse"] == EXPECTED_MAX_ANIMATION_REUSE
    # Reference and unique counts are different populations.
    assert census["frame_slots_over_unique_animations"] > census["unique_frames"]
    assert EXPECTED_ANIMATION_REFERENCES > census["unique_animations"]
    # The two trailer words are recorded raw, with their measured histograms.
    assert census["trailer_0_histogram"] == EXPECTED_TRAILER_0
    assert len(census["trailer_1_histogram"]) == EXPECTED_TRAILER_1_DISTINCT
    for value, count in EXPECTED_TRAILER_1_TOP.items():
        assert census["trailer_1_histogram"][value] == count
    assert sum(EXPECTED_TRAILER_1_TOP.values()) == 974


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
    """The report is a pure function of the image bytes, and it tracks them."""
    first = probe.definition_census(canonical_bytes)
    second = probe.definition_census(canonical_bytes)
    assert first == second
    assert probe.run_report(canonical_bytes) == probe.run_report(canonical_bytes)
    assert probe.animation_census(canonical_bytes) == probe.animation_census(
        canonical_bytes
    )
    # A one-byte change must move the report, so the equality above is not
    # vacuous.
    mutated = bytearray(canonical_bytes)
    mutated[probe.DEFINITION_ARRAY_ADDRESS - probe.ROM_BASE] ^= 0x01
    assert probe.run_report(bytes(mutated)) != probe.run_report(canonical_bytes)


def test_canonical_gate_rejects_a_non_canonical_image() -> None:
    with pytest.raises(probe.SpriteProbeError, match="expected"):
        probe.verify_canonical(b"\x00" * 16)
    with pytest.raises(probe.SpriteProbeError, match="non-canonical"):
        probe.verify_canonical(b"\x00" * probe.ROM_SIZE)
