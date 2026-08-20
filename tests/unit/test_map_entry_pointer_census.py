from dataclasses import replace

import pytest

from tools.webfoot.analysis.map_entry_pointers import (
    POINTER_CANDIDATE_FIELDS,
    PointerCandidateField,
    PointerCensusError,
    PointerClassification,
    analyze_map_entry_pointers,
)
from tools.webfoot.binary import GBA_ROM_BASE
from tools.webfoot.formats.map_entry import MAP_ENTRY_LAYOUT, MapEntry


ZERO_ENTRY = MapEntry(*([0] * len(MAP_ENTRY_LAYOUT)))


def observations_by_field(census):
    return {item.field_name: item for item in census.observations}


def stats_for(census, field_name):
    return next(item for item in census.field_stats if item.field_name == field_name)


def correlation_for(census, field_name):
    return next(
        item for item in census.correlations if item.pointer_field_name == field_name
    )


def test_classification_covers_null_bounds_and_alignment():
    rom_size = 0x100
    entry = replace(
        ZERO_ENTRY,
        triggers_pointer_raw=0,
        scripts_pointer_raw=GBA_ROM_BASE,
        items_pointer_raw=GBA_ROM_BASE + rom_size - 1,
        objects_pointer_raw=GBA_ROM_BASE + rom_size,
        npcs_pointer_raw=GBA_ROM_BASE - 1,
        variation_script_pointer_raw=GBA_ROM_BASE + 2,
        variation_array_pointer_raw=GBA_ROM_BASE + 4,
        entry_script_pointer_raw=GBA_ROM_BASE + 1,
        exit_script_pointer_raw=GBA_ROM_BASE + 8,
    )

    observed = observations_by_field(
        analyze_map_entry_pointers([entry], rom_size=rom_size)
    )

    assert observed["triggers_pointer_raw"].classification is PointerClassification.NULL
    assert observed["scripts_pointer_raw"].file_offset == 0
    assert observed["scripts_pointer_raw"].aligned_4
    assert observed["items_pointer_raw"].file_offset == rom_size - 1
    assert not observed["items_pointer_raw"].aligned_2
    assert (
        observed["objects_pointer_raw"].classification
        is PointerClassification.OUT_OF_RANGE
    )
    assert (
        observed["npcs_pointer_raw"].classification
        is PointerClassification.OUT_OF_RANGE
    )
    assert observed["variation_script_pointer_raw"].aligned_2
    assert not observed["variation_script_pointer_raw"].aligned_4
    assert not observed["entry_script_pointer_raw"].aligned_2


def test_duplicate_and_frequency_statistics_are_consistent():
    entries = [
        replace(ZERO_ENTRY, triggers_pointer_raw=GBA_ROM_BASE + 4),
        replace(ZERO_ENTRY, triggers_pointer_raw=GBA_ROM_BASE + 4),
        replace(ZERO_ENTRY, triggers_pointer_raw=GBA_ROM_BASE + 8),
    ]

    stats = stats_for(
        analyze_map_entry_pointers(entries, rom_size=0x100),
        "triggers_pointer_raw",
    )

    assert stats.valid_rom_count == 3
    assert stats.unique_valid_target_count == 2
    assert stats.duplicate_reference_count == 1
    assert stats.repeated_target_count == 1
    assert stats.most_frequent_targets[0].raw_value == GBA_ROM_BASE + 4
    assert stats.most_frequent_targets[0].reference_count == 2


def test_count_pointer_correlation_accounts_for_all_cases():
    entries = [
        replace(ZERO_ENTRY, trigger_count_raw=0, triggers_pointer_raw=0),
        replace(
            ZERO_ENTRY,
            trigger_count_raw=0,
            triggers_pointer_raw=GBA_ROM_BASE,
        ),
        replace(ZERO_ENTRY, trigger_count_raw=1, triggers_pointer_raw=0),
        replace(
            ZERO_ENTRY,
            trigger_count_raw=1,
            triggers_pointer_raw=GBA_ROM_BASE + 4,
        ),
        replace(
            ZERO_ENTRY,
            trigger_count_raw=1,
            triggers_pointer_raw=GBA_ROM_BASE + 0x100,
        ),
    ]

    correlation = correlation_for(
        analyze_map_entry_pointers(entries, rom_size=0x100),
        "triggers_pointer_raw",
    )

    assert correlation.count_zero_pointer_null == 1
    assert correlation.count_zero_pointer_non_null == 1
    assert correlation.count_positive_pointer_null == 1
    assert correlation.count_positive_pointer_valid == 1
    assert correlation.count_positive_pointer_out_of_range == 1
    assert correlation.total_count == len(entries)


def test_region_clustering_uses_numeric_file_offset_buckets():
    entries = [
        replace(ZERO_ENTRY, scripts_pointer_raw=GBA_ROM_BASE + 0x10),
        replace(ZERO_ENTRY, scripts_pointer_raw=GBA_ROM_BASE + 0x20),
        replace(ZERO_ENTRY, scripts_pointer_raw=GBA_ROM_BASE + 0x10010),
    ]

    stats = stats_for(
        analyze_map_entry_pointers(entries, rom_size=0x20000),
        "scripts_pointer_raw",
    )

    assert [(item.start_file_offset, item.reference_count) for item in stats.regions] == [
        (0, 2),
        (0x10000, 1),
    ]


def test_global_and_per_field_totals_are_consistent():
    census = analyze_map_entry_pointers([ZERO_ENTRY, ZERO_ENTRY], rom_size=0x100)

    assert census.entry_count == 2
    assert census.pointer_field_count == 9
    assert census.total_observation_count == 18
    assert census.null_count == 18
    assert census.valid_rom_count == 0
    assert census.out_of_range_count == 0
    assert all(item.total_count == 2 for item in census.field_stats)
    assert all(item.total_count == 2 for item in census.correlations)


def test_valid_observation_retains_raw_address_and_file_offset():
    census = analyze_map_entry_pointers(
        [replace(ZERO_ENTRY, scripts_pointer_raw=GBA_ROM_BASE + 0x44)],
        rom_size=0x100,
    )
    observation = observations_by_field(census)["scripts_pointer_raw"]

    assert observation.raw_value == GBA_ROM_BASE + 0x44
    assert observation.gba_address is not None
    assert observation.gba_address.raw == GBA_ROM_BASE + 0x44
    assert observation.file_offset == 0x44


@pytest.mark.parametrize(
    "candidates,message",
    [
        ((PointerCandidateField("not_a_field"),), "not a 32-bit"),
        (
            (PointerCandidateField("scripts_pointer_raw", "not_a_count"),),
            "not an 8-bit",
        ),
        (
            (
                PointerCandidateField("scripts_pointer_raw"),
                PointerCandidateField("scripts_pointer_raw"),
            ),
            "duplicate pointer candidate",
        ),
    ],
)
def test_unexpected_candidate_fields_are_rejected(candidates, message):
    with pytest.raises(PointerCensusError, match=message):
        analyze_map_entry_pointers(
            [ZERO_ENTRY],
            rom_size=0x100,
            candidates=candidates,
        )


@pytest.mark.parametrize(
    "kwargs,message",
    [
        ({"rom_size": 0}, "ROM size"),
        ({"rom_size": True}, "ROM size"),
        ({"rom_size": 0x100, "region_size": 0}, "region size"),
        ({"rom_size": 0x100, "profile_id": ""}, "profile id"),
    ],
)
def test_malformed_analysis_configuration_is_rejected(kwargs, message):
    with pytest.raises(PointerCensusError, match=message):
        analyze_map_entry_pointers([ZERO_ENTRY], **kwargs)


def test_declared_candidate_set_contains_exactly_nine_unique_fields():
    names = [item.field_name for item in POINTER_CANDIDATE_FIELDS]

    assert len(names) == 9
    assert len(set(names)) == 9


def test_malformed_count_value_is_rejected():
    entry = replace(ZERO_ENTRY, trigger_count_raw=True)

    with pytest.raises(PointerCensusError, match="raw 8-bit"):
        analyze_map_entry_pointers([entry], rom_size=0x100)


def test_non_map_entry_input_is_rejected():
    with pytest.raises(PointerCensusError, match="only MapEntry"):
        analyze_map_entry_pointers([object()], rom_size=0x100)
