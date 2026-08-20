from pathlib import Path

import pytest
import yaml

from tools.webfoot.analysis.map_entry_pointers import census_map_entry_pointers
from tools.webfoot.analysis.variation_arrays import (
    census_variation_array_first_words,
)
from tools.webfoot.cli import main
from tools.webfoot.formats.map_entry import validate_map_entry_round_trips
from tools.webfoot.profile import RomProfileCatalog


LOCAL_ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")


def test_complete_local_buus_fury_map_entry_table_round_trips():
    if not LOCAL_ROM.is_file():
        pytest.skip("user-supplied Buu's Fury ROM is not present")

    result = validate_map_entry_round_trips(
        LOCAL_ROM,
        RomProfileCatalog.load("config/roms.yaml"),
    )

    assert result.table.identification.profile_match.profile is not None
    assert (
        result.table.identification.profile_match.profile.id
        == "buus_fury_usa_rev0_01c1707f"
    )
    assert result.table.table_address.raw == 0x0808E2E0
    assert result.table.table_offset == 0x0008E2E0
    assert len(result.table.records) == 452
    assert result.serialized_count == 452
    assert result.mismatches == ()
    assert result.byte_mismatch_count == 0


def test_cli_validates_complete_local_map_entry_table(capsys):
    if not LOCAL_ROM.is_file():
        pytest.skip("user-supplied Buu's Fury ROM is not present")

    exit_code = main(["validate-map-entries", str(LOCAL_ROM)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Entries parsed: 452" in output
    assert "Entries serialized: 452" in output
    assert "Byte mismatches: 0" in output
    assert "RESULT:\nPASS" in output


def test_cli_rejects_conflicting_target_table_metadata(tmp_path, capsys):
    if not LOCAL_ROM.is_file():
        pytest.skip("user-supplied Buu's Fury ROM is not present")

    catalog_data = yaml.safe_load(Path("config/roms.yaml").read_text(encoding="utf-8"))
    target = next(
        profile
        for profile in catalog_data["profiles"]
        if profile["id"] == "buus_fury_usa_rev0_01c1707f"
    )
    target["tables"]["map_entries"]["address"] += 4
    catalog_path = tmp_path / "conflicting-roms.yaml"
    catalog_path.write_text(yaml.safe_dump(catalog_data), encoding="utf-8")

    exit_code = main(
        [
            "--profiles",
            str(catalog_path),
            "validate-map-entries",
            str(LOCAL_ROM),
        ]
    )
    error = capsys.readouterr().err

    assert exit_code == 2
    assert "metadata conflicts with the ROM-002 contract" in error


def test_complete_local_pointer_census_accounting():
    if not LOCAL_ROM.is_file():
        pytest.skip("user-supplied Buu's Fury ROM is not present")

    census = census_map_entry_pointers(
        LOCAL_ROM,
        RomProfileCatalog.load("config/roms.yaml"),
    )

    assert census.profile_id == "buus_fury_usa_rev0_01c1707f"
    assert census.entry_count == 452
    assert census.pointer_field_count == 9
    assert census.total_observation_count == 452 * 9
    assert (
        census.null_count + census.valid_rom_count + census.out_of_range_count
        == census.total_observation_count
    )
    for stats in census.field_stats:
        assert stats.null_count + stats.valid_rom_count + stats.out_of_range_count == 452
        assert stats.aligned_4_count <= stats.aligned_2_count <= stats.valid_rom_count
        assert (
            stats.unique_valid_target_count + stats.duplicate_reference_count
            == stats.valid_rom_count
        )
    assert all(item.total_count == 452 for item in census.correlations)


def test_cli_runs_complete_local_pointer_census(capsys):
    if not LOCAL_ROM.is_file():
        pytest.skip("user-supplied Buu's Fury ROM is not present")

    exit_code = main(["map-entries", "pointer-census", str(LOCAL_ROM)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "MapEntries analyzed: 452" in output
    assert "Pointer fields analyzed: 9" in output
    assert "Total observations: 4068" in output
    assert "RESULT:\nCOMPLETE" in output


def test_complete_local_variation_array_first_word_census():
    if not LOCAL_ROM.is_file():
        pytest.skip("user-supplied Buu's Fury ROM is not present")

    census = census_variation_array_first_words(
        LOCAL_ROM,
        RomProfileCatalog.load("config/roms.yaml"),
    )

    assert census.profile_id == "buus_fury_usa_rev0_01c1707f"
    assert census.pointer_count == 452
    assert census.source_valid_address_count == 452
    assert census.source_null_count == 0
    assert census.source_out_of_range_count == 0
    assert census.unique_valid_source_address_count == 452
    assert census.successful_read_count == 452
    assert census.bounds_failure_count == 0
    assert census.successful_read_count + census.bounds_failure_count == 452
    assert census.zero_count + census.nonzero_count == 452
    assert (
        census.zero_count
        + census.rom_address_shaped_count
        + census.non_rom_value_count
        == 452
    )
    assert census.ordering.address_count == 452
    assert census.ordering.unique_address_count == 452


def test_cli_runs_complete_local_variation_array_first_word_census(capsys):
    if not LOCAL_ROM.is_file():
        pytest.skip("user-supplied Buu's Fury ROM is not present")

    exit_code = main(
        ["variation-arrays", "first-word-census", str(LOCAL_ROM)]
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "MapEntries: 452" in output
    assert "Pointers validated: 452" in output
    assert "Words read: 452" in output
    assert "Bounds failures: 0" in output
    assert "RESULT:\nCOMPLETE" in output
