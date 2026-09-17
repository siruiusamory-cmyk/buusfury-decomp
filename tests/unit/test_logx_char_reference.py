"""Portable, ROM-free tests for the LOGX-CHAR-001 census reference.

These cover the synthetic-input behaviour of the census reference and the
internal consistency of the probe's constants. No canonical ROM bytes, hashes
or decoded strings are embedded here, and none of these tests touches a file.
"""

from __future__ import annotations

import pytest

from tools.research import logx_char_probe as probe

ROM_BASE = 0x08000000


def _row(
    text: int = 1000,
    text2: int = 1001,
    field_04: int = 12,
    field_08: int = 8,
    field_0c: int = 0,
) -> tuple[int, int, int, int, int]:
    return (text, text2, field_04, field_08, field_0c)


# --- the census reference on synthetic rows ----------------------------------


def test_well_formed_rows_produce_no_anomalies() -> None:
    summary = probe.census_rows([_row(), _row(text=1002, text2=1003, field_08=0)])
    assert summary["counters"]["records"] == 2
    assert summary["anomalies"] == []
    assert summary["duplicate_complete_records"] == []
    assert summary["zero_counts"]["field_08"] == 1


def test_text_index_out_of_range_is_flagged() -> None:
    limits = probe.CensusLimits(text_entries=10)
    summary = probe.census_rows([_row(text=10, text2=11)], limits)
    assert summary["anomalies"] == [
        {"index": 0, "flags": ["text_index_out_of_range"]}
    ]
    assert summary["counters"]["text_index_out_of_range"] == 1


def test_second_text_index_is_flagged_when_not_adjacent() -> None:
    summary = probe.census_rows([_row(text=1000, text2=1005)])
    assert summary["anomalies"][0]["flags"] == [
        "text_index_2_not_text_index_plus_one"
    ]


def test_field_04_id_below_the_accessor_floor_is_flagged() -> None:
    summary = probe.census_rows([_row(field_04=9)])
    assert summary["anomalies"][0]["flags"] == ["field_04_id_below_accessor_floor"]
    # Zero is counted as an absent value rather than an out-of-range id.
    zero = probe.census_rows([_row(field_04=0)])
    assert zero["anomalies"] == []
    assert zero["counters"]["zero_field_04"] == 1


def test_field_04_id_past_the_array_is_flagged() -> None:
    limits = probe.CensusLimits(field_04_entry_count=4)
    assert probe.census_rows([_row(field_04=13)], limits)["anomalies"] == []
    summary = probe.census_rows([_row(field_04=14)], limits)
    assert summary["anomalies"][0]["flags"] == ["field_04_id_out_of_table"]


def test_field_08_slots_are_bounded() -> None:
    assert probe.census_rows([_row(field_08=0)])["anomalies"] == []
    assert probe.census_rows([_row(field_08=8)])["anomalies"] == []
    reserved = probe.census_rows([_row(field_08=3)])
    assert reserved["anomalies"][0]["flags"] == ["field_08_slot_reserved"]
    past = probe.census_rows([_row(field_08=999)])
    assert past["anomalies"][0]["flags"] == ["field_08_slot_out_of_table"]


def test_stat_index_sign_and_extent() -> None:
    limits = probe.CensusLimits(stat_accepted_records=3)
    negative = probe.census_rows([_row(field_0c=-1)], limits)
    assert negative["anomalies"] == []
    assert negative["counters"]["field_0c_negative"] == 1
    inside = probe.census_rows([_row(field_0c=2)], limits)
    assert inside["anomalies"] == []
    outside = probe.census_rows([_row(field_0c=3)], limits)
    assert outside["anomalies"][0]["flags"] == [
        "field_0c_beyond_accepted_stat_extent"
    ]


def test_duplicate_rows_are_grouped_by_index() -> None:
    summary = probe.census_rows([_row(), _row(), _row(text=7, text2=8)])
    assert summary["duplicate_complete_records"] == [
        {"row": list(_row()), "indices": [0, 1]}
    ]


def test_distinct_and_zero_counts_are_population_scoped() -> None:
    rows = [_row(field_08=0), _row(field_08=0), _row(text=5, text2=6, field_08=9)]
    summary = probe.census_rows(rows)
    assert summary["counters"]["records"] == 3
    assert summary["distinct"]["field_08"] == 2
    assert summary["zero_counts"]["field_08"] == 2
    assert summary["distinct"]["text_index"] == 2


# --- constants and pure helpers ---------------------------------------------


def test_table_geometry_is_internally_consistent() -> None:
    assert probe.CHAR_TABLE_ADDRESS == probe.CHAR_TABLE_FILE_OFFSET + ROM_BASE
    assert probe.CHAR_TABLE_FILE_OFFSET == 0x74D380
    assert probe.CHAR_RECORD_SIZE == 0x10
    assert probe.CHAR_RECORD_COUNT == 232
    # The structure before the table ends exactly where the table starts.
    assert (
        probe.PRECEDING_BYTE_TABLE_ADDRESS + probe.PRECEDING_BYTE_TABLE_SIZE
        == probe.PRECEDING_POINTER_TABLE_ADDRESS
    )
    assert (
        probe.PRECEDING_POINTER_TABLE_ADDRESS
        + probe.PRECEDING_POINTER_TABLE_ENTRIES * 4
        == probe.CHAR_TABLE_ADDRESS
    )
    assert probe.PRECEDING_BYTE_TABLE_SIZE == 4


def test_pointer_array_constants_follow_their_accessors() -> None:
    # The +0x04 accessor's arithmetic base is its literal minus ten entries.
    assert probe.FIELD_04_TABLE_LITERAL == 0x086B6BDC
    assert probe.FIELD_04_TABLE_DISPLACEMENT == -4 * probe.FIELD_04_ID_FLOOR
    assert probe.FIELD_04_TABLE_ARITHMETIC_BASE == probe.FIELD_04_TABLE_LITERAL - 0x28
    assert probe.FIELD_04_TABLE_ENTRY_RUN_START == probe.FIELD_04_TABLE_LITERAL
    # The last id the canonical table uses lands on the last valid entry.
    assert 306 - probe.FIELD_04_ID_FLOOR == probe.FIELD_04_TABLE_ENTRY_COUNT - 1
    # The +0x08 array's first and last valid slots bracket its run, and the run
    # is an inclusion in the slot range, not the whole of it.
    assert probe.FIELD_08_FIRST_VALID_SLOT == 8
    assert probe.FIELD_08_FIRST_VALID_SLOT <= probe.FIELD_08_VALID_SLOT_LAST
    assert probe.FIELD_08_VALID_SLOT_LAST - probe.FIELD_08_FIRST_VALID_SLOT + 1 == 155
    assert probe.FIELD_08_TABLE_ADDRESS == 0x086F393C


def test_census_limits_separate_engine_bounds_from_measured_extents() -> None:
    """The two kinds of bound are named separately so neither is over-claimed."""
    limits = probe.CensusLimits()
    assert limits.text_entries == probe.TEXT_TABLE_ENTRIES
    assert limits.stat_accepted_records == probe.STAT_TABLE_ACCEPTED_RECORDS
    # These two are pointer-run extents measured from the image, not engine
    # bounds; the probe names them after their field, not after a semantic.
    assert limits.field_04_entry_count == probe.FIELD_04_TABLE_ENTRY_COUNT == 297
    assert limits.field_08_last_valid_slot == probe.FIELD_08_VALID_SLOT_LAST == 162


def test_neighbourhood_literals_are_the_ones_the_scan_expects() -> None:
    low, high = probe.NEIGHBOURHOOD
    assert low <= probe.PRECEDING_BYTE_TABLE_ADDRESS < high
    assert low <= probe.CHAR_TABLE_ADDRESS < high
    for value in probe.NEIGHBOUR_LITERAL_VALUES:
        assert low <= value < high
    # The range is the 0x100 bytes below the table plus the table's own head, so
    # a folded base would fall inside it.
    assert high - low == 0x180
    assert probe.CHAR_TABLE_ADDRESS - low == 0x100


def test_evidence_instruction_sites_are_even_and_unique() -> None:
    addresses = [address for address, _ in probe.EVIDENCE_INSTRUCTIONS.values()]
    assert len(addresses) == len(set(addresses))
    assert all(address % 2 == 0 for address in addresses)
    assert tuple(sorted(probe.CHAR_TABLE_LITERAL_SITES)) == probe.CHAR_TABLE_LITERAL_SITES
    assert len(set(probe.CHAR_TABLE_LITERAL_SITES)) == len(probe.CHAR_TABLE_LITERAL_SITES)


def test_probe_identifiers_name_fields_not_targets() -> None:
    """No identifier in the API promotes a partially confirmed target semantic."""
    names = [name for name in dir(probe) if name.isupper() or callable(getattr(probe, name))]
    assert not [name for name in names if "SPRITE" in name.upper()]
    assert not [name for name in names if "PORTRAIT" in name.upper()]
    assert not [name for name in names if name.lower().startswith("sprite")]
    assert not [name for name in names if name.lower().startswith("portrait")]


# --- the canonical gate fails closed ----------------------------------------


def test_gate_rejects_an_image_of_the_wrong_size() -> None:
    with pytest.raises(probe.CharProbeError, match="expected"):
        probe.verify_canonical(b"\x00" * 1024)


def test_gate_rejects_a_wrong_hash() -> None:
    with pytest.raises(probe.CharProbeError, match="non-canonical"):
        probe.verify_canonical(b"\x00" * probe.ROM_SIZE)


# --- record-level helpers without a ROM -------------------------------------


def test_signed_field_0c_reading() -> None:
    record = probe.CharacterRecord(
        index=0,
        file_offset=probe.CHAR_TABLE_FILE_OFFSET,
        address=probe.CHAR_TABLE_ADDRESS,
        text_index=1,
        text_index_2=2,
        field_04=12,
        field_08=8,
        field_0c=0xFFFFFFFF,
    )
    assert record.field_0c_signed == -1
    assert record.raw == bytes.fromhex("010002000c00000008000000ffffffff")


def test_field_04_accessor_floor_is_refused_rather_than_guessed() -> None:
    with pytest.raises(probe.CharProbeError, match="party-slot branch"):
        probe.field_04_target(b"\x00" * 16, probe.FIELD_04_ID_FLOOR - 1)


def test_field_08_party_slots_are_refused_rather_than_guessed() -> None:
    with pytest.raises(probe.CharProbeError, match="party path"):
        probe.field_08_target(b"\x00" * 16, 3)


def test_text_index_bounds_are_checked_before_reading() -> None:
    with pytest.raises(probe.CharProbeError, match="outside"):
        probe.resolve_text(b"\x00" * 16, probe.TEXT_TABLE_ENTRIES)
    with pytest.raises(probe.CharProbeError, match="outside"):
        probe.text_target(b"\x00" * 16, probe.TEXT_TABLE_ENTRIES)


def test_negative_stat_index_is_refused() -> None:
    with pytest.raises(probe.CharProbeError, match="negative"):
        probe.stat_record_address(b"\x00" * 16, -1)
