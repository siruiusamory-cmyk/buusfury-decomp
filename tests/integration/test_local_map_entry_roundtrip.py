from pathlib import Path

import pytest
import yaml

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
