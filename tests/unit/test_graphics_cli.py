"""Portable CLI tests for the graphics subsystem (TOOLKIT-010).

These use a synthetic ROM, so they run without the canonical image. What they
assert is refusal behaviour: that the CLI parses identities strictly and that an
undeclared or spoofed profile is turned away before any offset is trusted. The
happy paths need real graphics and live in
`tests/integration/test_graphics_rom.py`.
"""

from __future__ import annotations

import pytest

from tests.helpers import make_synthetic_rom, profile_for
from tests.unit.test_cli import PACKAGED_PROFILE_ID, write_catalog
from tools.webfoot.cli import main


def _synthetic(tmp_path, **overrides):
    data = make_synthetic_rom(game_code="BG3E", size=0x100)
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(data)
    config = tmp_path / "roms.yaml"
    write_catalog(config, [profile_for(data, **overrides)])
    return rom, config


def test_graphics_refuses_a_profile_that_declares_no_sprites(tmp_path, capsys):
    """Declaration authorises the subsystem; bytes alone never do."""
    rom, config = _synthetic(tmp_path, id="declares_nothing")
    exit_code = main(["--profiles", str(config), "graphics", "summary", str(rom)])
    error = capsys.readouterr().err
    assert exit_code == 2
    assert "actor_sprites" in error or "packaged catalog has no" in error


def test_graphics_refuses_a_spoofed_target_profile(tmp_path, capsys):
    """Borrowing a real profile id does not authorise unrelated bytes."""
    rom, config = _synthetic(tmp_path, id=PACKAGED_PROFILE_ID)
    exit_code = main(["--profiles", str(config), "graphics", "summary", str(rom)])
    error = capsys.readouterr().err
    assert exit_code == 2
    assert error.strip()


def test_graphics_reports_a_missing_rom_without_a_traceback(tmp_path, capsys):
    _, config = _synthetic(tmp_path, id="declares_nothing")
    exit_code = main(
        ["--profiles", str(config), "graphics", "summary", str(tmp_path / "absent.gba")]
    )
    error = capsys.readouterr().err
    assert exit_code == 2
    assert "does not exist" in error


@pytest.mark.parametrize(
    "identity",
    ["bogus", "graphic:0001", "profile/graphic:", "profile/graphic:abc", "profile/other:1"],
)
def test_graphics_rejects_a_malformed_identity(tmp_path, capsys, identity):
    """A profile-qualified identity is required; nothing is guessed from a bare number."""
    rom, config = _synthetic(tmp_path, id="declares_nothing")
    exit_code = main(
        ["--profiles", str(config), "graphics", "show", str(rom), identity]
    )
    assert exit_code == 2
    assert capsys.readouterr().err.strip()


def test_graphics_subcommand_is_required(tmp_path):
    with pytest.raises(SystemExit):
        main(["graphics"])


def test_export_requires_an_output_path(tmp_path):
    rom, config = _synthetic(tmp_path, id="declares_nothing")
    with pytest.raises(SystemExit):
        main(
            [
                "--profiles",
                str(config),
                "graphics",
                "export",
                str(rom),
                "profile/graphic:0000",
            ]
        )
