import pytest
import yaml

from tests.helpers import make_synthetic_rom, profile_for
from tools.webfoot.cli import main
from tools.webfoot.formats.map_entry import MAP_ENTRY_SIZE, SUPPORTED_PROFILE_ID


def write_catalog(path, profiles):
    mappings = []
    for profile in profiles:
        mapping = {
            "id": profile.id,
            "game": profile.game,
            "region": profile.region,
            "revision": profile.revision,
            "game_code": profile.game_code,
            "size": profile.size,
            "crc32": profile.crc32,
            "md5": profile.md5,
            "sha1": profile.sha1,
            "sha256": profile.sha256,
            "sources": list(profile.sources),
            "notes": profile.notes,
        }
        if profile.map_entries is not None:
            mapping["tables"] = {
                "map_entries": {
                    "address": profile.map_entries.address.raw,
                    "count": profile.map_entries.count,
                    "record_size": profile.map_entries.record_size,
                }
            }
        mappings.append(mapping)
    path.write_text(
        yaml.safe_dump({"schema_version": 1, "profiles": mappings}), encoding="utf-8"
    )


def test_cli_reports_verified_profile(tmp_path, capsys):
    data = make_synthetic_rom(game_code="BG3E")
    rom = tmp_path / "synthetic.gba"
    config = tmp_path / "roms.yaml"
    rom.write_bytes(data)
    write_catalog(config, [profile_for(data)])

    exit_code = main(["--profiles", str(config), "identify", str(rom)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Status:\nVERIFIED" in output
    assert "Game Code: BG3E" in output
    assert "CRC32:" in output


def test_cli_unknown_returns_one(tmp_path, capsys):
    rom = tmp_path / "synthetic.gba"
    config = tmp_path / "roms.yaml"
    rom.write_bytes(make_synthetic_rom())
    write_catalog(config, [])

    exit_code = main(["--profiles", str(config), "identify", str(rom)])
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "Status:\nUNKNOWN" in output


def test_cli_path_error_returns_two(tmp_path, capsys):
    config = tmp_path / "roms.yaml"
    write_catalog(config, [])

    exit_code = main(["--profiles", str(config), "identify", str(tmp_path / "no.gba")])
    error = capsys.readouterr().err

    assert exit_code == 2
    assert "does not exist" in error


@pytest.mark.parametrize(
    "command",
    [
        ["validate-map-entries"],
        ["variation-arrays", "first-word-census"],
    ],
)
def test_cli_rejects_spoofed_target_profile(tmp_path, capsys, command):
    table_offset = 0xC0
    data = bytearray(make_synthetic_rom(game_code="BG3E", size=0x100))
    data[table_offset : table_offset + MAP_ENTRY_SIZE] = bytes(range(MAP_ENTRY_SIZE))
    frozen = bytes(data)
    rom = tmp_path / "synthetic.gba"
    config = tmp_path / "roms.yaml"
    rom.write_bytes(frozen)
    profile = profile_for(
        frozen,
        id=SUPPORTED_PROFILE_ID,
        tables={
            "map_entries": {
                "address": 0x08000000 + table_offset,
                "count": 1,
                "record_size": MAP_ENTRY_SIZE,
            }
        },
    )
    write_catalog(config, [profile])

    exit_code = main(["--profiles", str(config), *command, str(rom)])
    error = capsys.readouterr().err

    assert exit_code == 2
    assert "fixed ROM-002 target identity" in error
