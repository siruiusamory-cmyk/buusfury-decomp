import yaml

from tests.helpers import make_synthetic_rom, profile_for
from tools.webfoot.cli import main


def write_catalog(path, profiles):
    mappings = []
    for profile in profiles:
        mappings.append(
            {
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
        )
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
