"""Read-only ROM-gated evidence for LOGX-CHAR-001.

Only findings independently established in
``docs/research/LOGX_CHAR_PROVENANCE.md`` are asserted here: the table's start,
stride and count as the canonical image's own instructions state them, each
record field's physical read and downstream pointer array, the full-census
arithmetic, both pointer arrays' shapes, and the table's boundaries.

The suite skips cleanly when the private canonical ROM is not configured and it
never writes to it. No ROM-derived bytes are committed: every expectation is a
count, an address, an index or a short instruction encoding.
"""

from __future__ import annotations

import hashlib
import os
import struct
from pathlib import Path

import pytest

from tools.research import logx_char_probe as probe
from tools.webfoot.formats import stat_tables
from tools.webfoot.formats import text_tables

ROM_BASE = 0x08000000

# --- independently measured constants of the canonical image ----------------

#: Every ``ldr Rt,[pc,#imm]`` whose literal word is 0x0874D380.
EXPECTED_LITERAL_SITES = (
    0x08024FA0,
    0x08025086,
    0x080251B6,
    0x08025380,
    0x08025E94,
    0x080273AC,
    0x08027962,
    0x080279A0,
)

#: The eight ``index << 4`` sites: one per literal load, three of them inside the
#: two table-walking loops and five single-record lookups.
EXPECTED_STRIDE_SITES = {
    "stride_loop_a": 0x080279A2,
    "stride_loop_b": 0x08027964,
    "stride_lookup_a": 0x08025088,
    "stride_lookup_b": 0x080251B8,
    "stride_lookup_c": 0x08025382,
    "stride_lookup_d": 0x08025E92,
    "stride_lookup_e": 0x080273AE,
    "stride_ui": 0x08024FA8,
}

#: The literal pool words immediately before the table.
EXPECTED_PRECEDING_BYTE_TABLE = bytes((0x00, 0x03, 0x01, 0x02))
EXPECTED_PRECEDING_POINTERS = (
    0x0805752C,
    0x0805762C,
    0x0805772C,
    0x0805782C,
    0x0805782C,
    0x0805772C,
    0x0805762C,
    0x0805752C,
)

#: The first candidate record beyond the accepted count, as raw field values.
EXPECTED_RECORD_232 = (7244, 768, 0x030019A4, 0, 0x2A0)

#: The invariant names that record 232 breaks. Three of the four hold on all 232
#: accepted records.
EXPECTED_RECORD_232_FAILURES = (
    "field_04_is_a_table_id",
    "text_index_2_is_text_index_plus_one",
    "text_index_in_range",
)

#: Raw bytes of two representative records, quoted so a reader can re-derive
#: every field from the tuple without trusting the parser.
RECORD_0_RAW = "100511051f0000000000000000000000"
RECORD_231_RAW = "a004a104320100000000000095000000"

#: The one pair of byte-identical records in the table.
EXPECTED_DUPLICATE_RECORDS = {80, 81}

#: Headline census figures.
EXPECTED_RECORDS = 232
EXPECTED_DISTINCT_TEXT_INDEX = 154
EXPECTED_DISTINCT_FIELD_04 = 198
EXPECTED_DISTINCT_FIELD_08 = 111
EXPECTED_DISTINCT_FIELD_0C = 132
EXPECTED_ZERO_FIELD_08 = 98
EXPECTED_ZERO_FIELD_0C = 1
EXPECTED_NEGATIVE_FIELD_0C = 88
EXPECTED_STAT_REFERENCES = 144
EXPECTED_STAT_UNIQUE_INDICES = 123
EXPECTED_FIELD_04_REFERENCES = 232
EXPECTED_FIELD_08_REFERENCES = 134
EXPECTED_FIELD_08_UNIQUE_SLOTS = 110

#: Distinct *strings* are fewer than distinct indices: three slots hold
#: "Super Buu", and the second text field is shared far more widely.
EXPECTED_DISTINCT_TEXT_STRINGS = 152
EXPECTED_DISTINCT_TEXT_2_STRINGS = 104

#: Records whose ``+0x0C`` index is at or beyond the accepted 141-record extent
#: of the 0x08711274 table. Recorded, not promoted into a record claim.
EXPECTED_BEYOND_STAT_EXTENT = (220, 221, 222, 224, 225, 227, 228, 231)
EXPECTED_BEYOND_STAT_VALUES = frozenset({142, 143, 145, 146, 147, 148, 149})

#: ``+0x04`` range over the canonical table, and the pointer-array slots it
#: therefore reaches under the accessor's own arithmetic.
EXPECTED_FIELD_04_MIN = 12
EXPECTED_FIELD_04_MAX = 306

#: ``+0x08``: 0 (no slot) plus a 110-element subset of the array's valid slots.
EXPECTED_FIELD_08_SLOTS = frozenset(
    {0, 8, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 29, 32,
     33, 35, 39, 43, 45, 46, 47, 49, 51, 54, 57, 60, 61, 62, 63, 65, 66, 68, 69,
     72, 73, 74, 76, 77, 78, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 93,
     94, 95, 96, 97, 98, 99, 100, 102, 103, 104, 105, 106, 107, 108, 109, 110,
     112, 113, 114, 115, 117, 118, 119, 120, 121, 124, 126, 127, 129, 131, 133,
     134, 135, 136, 137, 140, 144, 146, 147, 149, 150, 151, 152, 153, 154, 155,
     156, 157, 158, 159, 160, 161, 162}
)

#: Distinct (text, text2) pairs across the table: the repeating records.
EXPECTED_DISTINCT_TEXT_PAIRS = 154

#: The accessor's literal and its folded displacement.
FIELD_04_ACCESSOR_LITERAL_POOL = 0x080003C0


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


# --- section A: table start, stride and count --------------------------------


def test_every_literal_reference_to_the_table_address(canonical_bytes: bytes) -> None:
    """The table address is reached by exactly these eight literal loads."""
    sites = probe.thumb_ldr_literal_sites(canonical_bytes)
    found = tuple(sorted(site for site, _, _ in sites[probe.CHAR_TABLE_ADDRESS]))
    assert found == EXPECTED_LITERAL_SITES
    assert probe.CHAR_TABLE_LITERAL_SITES == EXPECTED_LITERAL_SITES
    # Every site loads through a pool word, and every pool word is the address.
    for site, _, pool in sites[probe.CHAR_TABLE_ADDRESS]:
        assert probe._u32(canonical_bytes, pool) == probe.CHAR_TABLE_ADDRESS
        assert site % 2 == 0


def test_no_folded_base_reaches_the_table_in_the_neighbourhood(
    canonical_bytes: bytes,
) -> None:
    """A base-adjusted accessor would show up as a nearby literal value."""
    values = probe.literal_values_in_range(canonical_bytes, *probe.NEIGHBOURHOOD)
    assert set(values) == {
        probe.PRECEDING_BYTE_TABLE_ADDRESS,
        probe.PRECEDING_POINTER_TABLE_ADDRESS,
        probe.CHAR_TABLE_ADDRESS,
    }


def test_engine_instructions_are_what_the_record_says(canonical_bytes: bytes) -> None:
    """Each quoted site decodes to the recorded instruction, whitespace-normalised."""
    for name, (address, expected) in probe.EVIDENCE_INSTRUCTIONS.items():
        actual = " ".join(probe.format_instruction(canonical_bytes, address).split())
        assert actual == f"{address:08x} {expected}", name


def test_stride_is_sixteen_at_eight_sites(canonical_bytes: bytes) -> None:
    """Every literal load is followed by its own ``index << 4``."""
    for name, address in EXPECTED_STRIDE_SITES.items():
        assert probe.EVIDENCE_INSTRUCTIONS[name][0] == address
        text = " ".join(probe.format_instruction(canonical_bytes, address).split())
        assert text == f"{address:08x} {probe.EVIDENCE_INSTRUCTIONS[name][1]}"
        assert text.endswith("#4")
    assert len(EXPECTED_STRIDE_SITES) == 8
    assert probe.CHAR_RECORD_SIZE == 0x10


def test_count_is_two_hundred_and_thirty_two(canonical_bytes: bytes) -> None:
    """The engine's own loop bound, an exclusive ``0xE8`` in two functions."""
    assert probe.format_instruction(canonical_bytes, 0x080279CC) == (
        "080279cc  cmp      r4, #0xe8"
    )
    assert probe.format_instruction(canonical_bytes, 0x08024F92) == (
        "08024f92  cmp      r0, #0xe8"
    )
    assert probe.CHAR_RECORD_COUNT == 0xE8


def test_only_the_search_function_returns_minus_one(canonical_bytes: bytes) -> None:
    """``0x08027948`` builds ``-1``; ``0x08024F3C`` returns its object instead."""
    assert probe.format_instruction(canonical_bytes, 0x080279D0) == (
        "080279d0  movs     r0, #0"
    )
    assert probe.format_instruction(canonical_bytes, 0x080279D2) == (
        "080279d2  mvns     r0, r0"
    )
    # 0x08024F3C's own ``mvns`` is a stored sentinel, not a return.
    assert probe.format_instruction(canonical_bytes, 0x08024FFC) == (
        "08024ffc  mvns     r1, r1"
    )
    assert probe.format_instruction(canonical_bytes, 0x08025000) == (
        "08025000  adds     r0, r4, #0"
    )


def test_field_04_accessor_arithmetic_is_the_folded_literal(
    canonical_bytes: bytes,
) -> None:
    """``ldr r1,=0x086B6BDC`` then ``subs #0x40`` then ``ldr [r0,#0x18]``."""
    assert probe._u32(canonical_bytes, FIELD_04_ACCESSOR_LITERAL_POOL) == (
        probe.FIELD_04_TABLE_LITERAL
    )
    assert probe.format_instruction(canonical_bytes, 0x08000164) == (
        "08000164  subs     r0, #0x40"
    )
    assert probe.format_instruction(canonical_bytes, 0x08000166) == (
        "08000166  ldr      r0, [r0, #0x18]"
    )
    assert probe.FIELD_04_TABLE_ARITHMETIC_BASE == 0x086B6BB4
    assert probe.FIELD_04_TABLE_ARITHMETIC_BASE == probe.FIELD_04_TABLE_LITERAL - 0x28
    # The party-path entry uses the identical literal and displacement.
    assert probe.format_instruction(canonical_bytes, 0x08017144) == (
        "08017144  subs     r0, #0x40"
    )


# --- section B: representative records ---------------------------------------


def test_representative_records_are_byte_exact(canonical_bytes: bytes) -> None:
    first = probe.read_record(canonical_bytes, 0)
    assert first.raw.hex() == RECORD_0_RAW
    assert (first.text_index, first.text_index_2, first.field_04, first.field_08) == (
        0x0510, 0x0511, 0x1F, 0)
    assert first.field_0c == 0

    last = probe.read_record(canonical_bytes, 231)
    assert last.raw.hex() == RECORD_231_RAW
    assert (last.text_index, last.text_index_2, last.field_04, last.field_08) == (
        0x04A0, 0x04A1, 0x132, 0)
    assert last.field_0c_signed == 0x95


def test_the_record_beyond_the_count_fails_three_invariants(
    canonical_bytes: bytes,
) -> None:
    boundary = probe.boundary_report(canonical_bytes)
    candidate = boundary["first_candidate_beyond_count"]
    assert candidate["index"] == probe.CHAR_RECORD_COUNT
    record = probe.read_record(canonical_bytes, probe.CHAR_RECORD_COUNT)
    assert (record.text_index, record.text_index_2, record.field_04,
            record.field_08, record.field_0c) == EXPECTED_RECORD_232
    assert tuple(candidate["invariants_failed"]) == EXPECTED_RECORD_232_FAILURES
    assert candidate["field_04"] == 0x030019A4


# --- section C: census arithmetic --------------------------------------------


def test_full_census_arithmetic(canonical_bytes: bytes) -> None:
    summary = probe.census(canonical_bytes)
    counters = summary["counters"]
    assert counters["records"] == EXPECTED_RECORDS
    assert counters["text_index_out_of_range"] == 0
    assert counters["text_index_2_not_text_index_plus_one"] == 0
    assert counters["field_04_id_below_accessor_floor"] == 0
    assert counters["field_04_id_out_of_table"] == 0
    assert counters["field_08_slot_reserved"] == 0
    assert counters["field_08_slot_out_of_table"] == 0
    assert counters["zero_field_04"] == 0
    assert counters["zero_field_08"] == EXPECTED_ZERO_FIELD_08
    assert counters["field_0c_zero"] == EXPECTED_ZERO_FIELD_0C
    assert counters["field_0c_negative"] == EXPECTED_NEGATIVE_FIELD_0C
    assert counters["field_0c_beyond_accepted_stat_extent"] == len(
        EXPECTED_BEYOND_STAT_EXTENT
    )
    assert tuple(a["index"] for a in summary["anomalies"]) == EXPECTED_BEYOND_STAT_EXTENT
    assert {record.field_0c_signed for record in probe.iter_records(canonical_bytes)
            if record.field_0c_signed >= stat_tables.ENEMY_RECORD_COUNT} == (
        EXPECTED_BEYOND_STAT_VALUES
    )
    assert summary["distinct"] == {
        "text_index": EXPECTED_DISTINCT_TEXT_INDEX,
        "text_index_2": EXPECTED_DISTINCT_TEXT_INDEX,
        "field_04": EXPECTED_DISTINCT_FIELD_04,
        "field_08": EXPECTED_DISTINCT_FIELD_08,
        "field_0c": EXPECTED_DISTINCT_FIELD_0C,
    }
    assert summary["distinct_text_strings"] == {
        "text_index": EXPECTED_DISTINCT_TEXT_STRINGS,
        "text_index_2": EXPECTED_DISTINCT_TEXT_2_STRINGS,
    }
    assert summary["zero_counts"]["field_04"] == 0
    assert summary["zero_counts"]["field_08"] == EXPECTED_ZERO_FIELD_08


def test_duplicate_complete_records(canonical_bytes: bytes) -> None:
    summary = probe.census(canonical_bytes)
    duplicates = summary["duplicate_complete_records"]
    assert len(duplicates) == 1
    assert duplicates[0]["indices"] == [80, 81]
    assert duplicates[0]["row"] == [996, 997, 137, 0, 44]
    assert probe.read_record(canonical_bytes, 80).raw == probe.read_record(
        canonical_bytes, 81
    ).raw


def test_field_04_reaches_the_pointer_array_at_its_arithmetic_base(
    canonical_bytes: bytes,
) -> None:
    records = probe.iter_records(canonical_bytes)
    ids = [record.field_04 for record in records]
    assert min(ids) == EXPECTED_FIELD_04_MIN
    assert max(ids) == EXPECTED_FIELD_04_MAX
    targets = set()
    for record in records:
        target = probe.field_04_target(canonical_bytes, record.field_04)
        assert probe.in_rom(canonical_bytes, target), hex(record.index)
        targets.add(target)
    assert len(targets) == EXPECTED_DISTINCT_FIELD_04
    # The accessor's arithmetic base is exactly 0x28 below its literal.
    for identifier in (EXPECTED_FIELD_04_MIN, EXPECTED_FIELD_04_MAX):
        assert probe.field_04_target(canonical_bytes, identifier) == probe._u32(
            canonical_bytes, 0x086B6BB4 + identifier * 4
        )


def test_field_08_reaches_the_pointer_array_at_its_literal(
    canonical_bytes: bytes,
) -> None:
    records = probe.iter_records(canonical_bytes)
    slots = {record.field_08 for record in records}
    assert slots == EXPECTED_FIELD_08_SLOTS
    for record in records:
        target = probe.field_08_target(canonical_bytes, record.field_08)
        if record.field_08 == 0:
            assert target == 0
        else:
            assert probe.in_rom(canonical_bytes, target), hex(record.index)


def test_field_0c_indexes_the_stat_table_at_the_engine_stride(
    canonical_bytes: bytes,
) -> None:
    records = probe.iter_records(canonical_bytes)
    positive = [record for record in records if record.field_0c_signed >= 0]
    assert len(positive) == EXPECTED_STAT_REFERENCES
    assert len({record.field_0c_signed for record in positive}) == (
        EXPECTED_STAT_UNIQUE_INDICES
    )
    assert max(record.field_0c_signed for record in positive) == 149
    assert min(record.field_0c_signed for record in positive) == 0
    for record in positive:
        address = probe.stat_record_address(canonical_bytes, record.field_0c_signed)
        assert address == 0x08711274 + 0x1C * record.field_0c_signed
        assert probe.in_rom(canonical_bytes, address)
    # The engine scales by 7 then by 4, i.e. 28, and adds the table literal.
    assert stat_tables.ENEMY_TABLE_START + ROM_BASE == probe.STAT_TABLE_ADDRESS
    assert stat_tables.ENEMY_RECORD_SIZE == probe.STAT_TABLE_RECORD_SIZE == 0x1C


def test_reference_and_target_arithmetic(canonical_bytes: bytes) -> None:
    references = probe.census(canonical_bytes)["references"]
    assert references["text_index"] == {
        "references": EXPECTED_RECORDS,
        "unique_values": EXPECTED_DISTINCT_TEXT_INDEX,
        "unique_targets": EXPECTED_DISTINCT_TEXT_INDEX,
    }
    assert references["text_index_2"] == {
        "references": EXPECTED_RECORDS,
        "unique_values": EXPECTED_DISTINCT_TEXT_INDEX,
        "unique_targets": EXPECTED_DISTINCT_TEXT_INDEX,
    }
    assert references["field_04"] == {
        "references": EXPECTED_FIELD_04_REFERENCES,
        "unique_values": EXPECTED_DISTINCT_FIELD_04,
        "unique_targets": EXPECTED_DISTINCT_FIELD_04,
    }
    assert references["field_08"] == {
        "references": EXPECTED_FIELD_08_REFERENCES,
        "unique_values": EXPECTED_FIELD_08_UNIQUE_SLOTS,
        "unique_targets": EXPECTED_FIELD_08_UNIQUE_SLOTS,
    }
    assert references["field_0c"] == {
        "references": EXPECTED_STAT_REFERENCES,
        "unique_values": EXPECTED_STAT_UNIQUE_INDICES,
        "unique_targets": EXPECTED_STAT_UNIQUE_INDICES,
    }


# --- section D: text ----------------------------------------------------------


def test_every_text_index_resolves_and_the_two_fields_are_adjacent(
    canonical_bytes: bytes,
) -> None:
    for record in probe.iter_records(canonical_bytes):
        assert record.text_index < probe.TEXT_TABLE_ENTRIES
        assert record.text_index_2 == record.text_index + 1
        assert probe.resolve_text(canonical_bytes, record.text_index)


def test_text_indices_are_scaled_by_four_before_the_indexed_load(
    canonical_bytes: bytes,
) -> None:
    """The doubling reading is wrong: the engine shifts left by two."""
    for address in (0x080251C0, 0x080252EA, 0x080253A2, 0x08025EC6):
        assert probe.format_instruction(canonical_bytes, address).endswith("#2")
    assert probe.format_instruction(canonical_bytes, 0x080251C2) == (
        "080251c2  ldr      r1, [r1, r0]"
    )
    assert probe.format_instruction(canonical_bytes, 0x080253A4) == (
        "080253a4  ldr      r0, [r1, r0]"
    )
    assert probe.format_instruction(canonical_bytes, 0x08025EC8) == (
        "08025ec8  ldr      r0, [r1, r0]"
    )


def test_representative_text_resolution(canonical_bytes: bytes) -> None:
    records = probe.iter_records(canonical_bytes)
    by_index = {record.index: record for record in records}
    assert probe.resolve_text(canonical_bytes, by_index[58].text_index) == "Goku"
    assert probe.resolve_text(canonical_bytes, by_index[231].text_index) == "Zombie"
    assert probe.resolve_text(canonical_bytes, by_index[0].text_index) == (
        "Airship Warlord"
    )
    assert probe.resolve_text(canonical_bytes, by_index[58].text_index_2).startswith(
        "Goku is a Saiyan"
    )
    # Two records can share the appearance id while carrying different text: the
    # text field is not derived from the appearance field.
    assert by_index[0].field_04 == by_index[11].field_04
    assert by_index[0].text_index != by_index[11].text_index
    assert probe.resolve_text(canonical_bytes, by_index[11].text_index) == "Bio Mech"
    # 232 records carry 154 distinct text-index pairs: the rest repeat an
    # existing pair with different resource fields.
    pairs = {(record.text_index, record.text_index_2) for record in records}
    assert len(pairs) == EXPECTED_DISTINCT_TEXT_PAIRS
    # Three distinct +0x00 slots hold the identical string, which is why the
    # distinct-string count is smaller than the distinct-index count.
    super_buu = {by_index[index].text_index for index in (184, 188, 189)}
    assert len(super_buu) == 3
    assert {probe.resolve_text(canonical_bytes, value) for value in super_buu} == {
        "Super Buu"
    }


# --- section E: the two pointer arrays ---------------------------------------


def test_field_04_pointer_array_shape(canonical_bytes: bytes) -> None:
    report = probe.field_04_table_report(canonical_bytes)
    assert report["entry_count"] == 297
    assert report["all_entries_in_rom"] is True
    assert report["strictly_ascending"] is True
    assert report["word_after_run_in_rom"] is False
    assert report["word_after_run_hex"] == "03001068"
    # The ten slots the accessor's arithmetic base would reach are not a uniform
    # run of pointers: four hold ascending valid pointers and six are null, which
    # is why the entry run is reported from the literal.
    assert report["slots_before_run_valid"] == 4
    assert report["slots_before_run_null"] == 6
    assert report["slots_before_run"] == [
        "0x086a6424", "0x086a7238", "0x00000000", "0x00000000", "0x086a7e7c",
        "0x00000000", "0x00000000", "0x00000000", "0x00000000", "0x086a899c",
    ]
    assert report["word_before_run_hex"] == "086a899c"
    # Entry 0 and the last entry, distinguished from the terminator slot.
    assert report["first_entry"] == "0x086a89d0"
    assert report["last_entry"] == "0x086b6b60"
    assert probe._u32(canonical_bytes, 0x086B707C) == 0x086B6B60


def test_field_08_pointer_array_shape(canonical_bytes: bytes) -> None:
    report = probe.field_08_table_report(canonical_bytes)
    assert report["slot_count"] == 163
    assert report["slots_before_first_valid_are_zero"] is True
    assert report["valid_slots_all_in_rom"] is True
    assert report["valid_slots_strictly_ascending"] is True
    assert report["first_valid_slot"] == "0x086b880c"
    assert report["valid_slot_count"] == 155
    assert report["word_after_last_slot_in_rom"] is False


def test_table_boundaries(canonical_bytes: bytes) -> None:
    boundary = probe.boundary_report(canonical_bytes)
    assert boundary["preceding_byte_table"]["bytes_hex"] == (
        EXPECTED_PRECEDING_BYTE_TABLE.hex()
    )
    assert boundary["preceding_pointer_table"]["all_in_rom"] is True
    for index, expected in enumerate(EXPECTED_PRECEDING_POINTERS):
        address = probe.PRECEDING_POINTER_TABLE_ADDRESS + index * 4
        assert probe._u32(canonical_bytes, address) == expected
    # The eight-entry pointer table ends exactly where the character table starts.
    assert (
        probe.PRECEDING_POINTER_TABLE_ADDRESS + probe.PRECEDING_POINTER_TABLE_ENTRIES * 4
        == probe.CHAR_TABLE_ADDRESS
    )
    assert (
        probe.PRECEDING_BYTE_TABLE_ADDRESS + probe.PRECEDING_BYTE_TABLE_SIZE
        == probe.PRECEDING_POINTER_TABLE_ADDRESS
    )


# --- section F: determinism and the gate -------------------------------------


def test_probe_is_deterministic(canonical_bytes: bytes) -> None:
    assert probe.census(canonical_bytes) == probe.census(canonical_bytes)
    assert probe.engine_report(canonical_bytes) == probe.engine_report(canonical_bytes)
    assert probe.build_report(canonical_bytes) == probe.build_report(canonical_bytes)


def test_canonical_gate_accepts_the_canonical_image(canonical_bytes: bytes) -> None:
    assert hashlib.sha256(canonical_bytes).hexdigest().upper() == probe.CANONICAL_SHA256
    probe.verify_canonical(canonical_bytes)


def test_records_are_read_at_their_stated_offsets(canonical_bytes: bytes) -> None:
    """``+0x00`` as a u16, ``+0x04``/``+0x08``/``+0x0C`` as u32, little-endian."""
    for index in (0, 1, 115, 231):
        address = probe.CHAR_TABLE_ADDRESS + index * probe.CHAR_RECORD_SIZE
        raw = canonical_bytes[address - ROM_BASE : address - ROM_BASE + 16]
        assert probe.read_record(canonical_bytes, index).raw == raw
        assert struct.unpack_from("<H", raw, 0)[0] == probe._u16(
            canonical_bytes, address
        )
