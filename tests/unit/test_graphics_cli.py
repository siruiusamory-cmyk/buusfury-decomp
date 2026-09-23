"""Portable CLI tests for the graphics subsystem (TOOLKIT-010).

These use a synthetic ROM, so they run without the canonical image. What they
assert is refusal behaviour: that the CLI parses identities strictly and that an
undeclared or spoofed profile is turned away before any offset is trusted. The
happy paths need real graphics and live in
`tests/integration/test_graphics_rom.py`.

The last block is CQA-01-OUTPUT-SAFETY-001: `graphics export` is the only
ROM-loading command whose destination is a caller-chosen artefact path, and it
must refuse a destination that is the input ROM. These drive the real `main`
argument vector, not the guard in isolation, because a correct helper that no
command calls is exactly the defect being closed.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tests.helpers import (
    SPRITE_PROFILE_ID,
    actor_sprite_tables,
    make_synthetic_rom,
    make_synthetic_sprite_rom,
    profile_for,
    write_catalog,
)
from tests.unit.test_cli import PACKAGED_PROFILE_ID
from tools.webfoot.cli import main
from tools.webfoot.formats import indexed_png
from tools.webfoot.graphics import ActorSprites, GraphicIdentity

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _synthetic(tmp_path, **overrides):
    data = make_synthetic_rom(game_code="BG3E", size=0x100)
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(data)
    config = tmp_path / "roms.yaml"
    write_catalog(config, [profile_for(data, **overrides)])
    return rom, config


def _synthetic_sprite_rom(tmp_path):
    """A catalogued ROM whose profile declares the actor-sprite capability."""
    data = make_synthetic_sprite_rom()
    rom = tmp_path / "synthetic_sprites.gba"
    rom.write_bytes(data)
    config = tmp_path / "roms.yaml"
    write_catalog(
        config, [profile_for(data, id=SPRITE_PROFILE_ID)], tables=actor_sprite_tables()
    )
    return rom, config


def _stub_corpus(profile_id: str):
    """A read-only sprite corpus that encodes a real 2x2 PNG through the real codec.

    `capability.require` re-checks every declared extent against the packaged
    catalogue, so synthetic bytes can never authorise the real corpus walk. Only
    that read-only load is stubbed; the export command, the identity parse, the
    source-alias policy and `indexed_png.encode` are all the production ones.
    """
    identity = GraphicIdentity(profile_id, 0)

    class _Graphic:
        pass

    graphic = _Graphic()
    graphic.identity = identity
    graphic.width = 2
    graphic.height = 2
    graphic.pixels = bytes([0, 1, 2, 3])

    palette = type("Pal", (), {"rgb": tuple((i, i, i) for i in range(256))})()

    sprites = ActorSprites.__new__(ActorSprites)
    sprites.palette = palette
    sprites.graphic = lambda requested: graphic
    return sprites, identity


def _patch_corpus(monkeypatch, sprites):
    """Point the CLI's own corpus load at `sprites`.

    `_run_graphics` imports `load_actor_sprites` from `tools.webfoot.graphics`
    at call time, so patching the module attribute is what the real command path
    sees.
    """
    from tools.webfoot import graphics as graphics_sdk

    monkeypatch.setattr(
        graphics_sdk, "load_actor_sprites", lambda image, identification: sprites
    )



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


# --- CQA-01: the export destination may never be the input ROM ----------------
#
# The defect: `graphics export <rom> <identity> --out <the same rom>` replaced the
# 2,077-byte source with a 15-byte PNG and exited 0 (audit CQA-01, reproduced
# twice). These tests drive the real command and assert the refusal AND that the
# source is byte-identical - an assertion on the exit code alone would pass even
# if the guard ran after a truncating open.


def _export_argv(config: Path, rom: Path, identity: str, out: Path) -> list[str]:
    return [
        "--profiles",
        str(config),
        "graphics",
        "export",
        str(rom),
        identity,
        "--out",
        str(out),
    ]


def test_export_refuses_to_write_over_its_own_input_rom(
    tmp_path, capsys, monkeypatch
):
    rom, config = _synthetic_sprite_rom(tmp_path)
    sprites, identity = _stub_corpus(SPRITE_PROFILE_ID)
    _patch_corpus(monkeypatch, sprites)

    before = rom.read_bytes()
    before_sha256 = hashlib.sha256(before).hexdigest()

    exit_code = main(_export_argv(config, rom, str(identity), rom))

    captured = capsys.readouterr()
    assert exit_code != 0, captured.out
    assert "source" in captured.err and "never" in captured.err
    # No success document was printed, and the ROM is not a PNG.
    assert str(rom) not in captured.out
    after = rom.read_bytes()
    assert hashlib.sha256(after).hexdigest() == before_sha256
    assert not after.startswith(_PNG_MAGIC)


def test_export_refuses_a_relative_spelling_of_the_input_rom(
    tmp_path, capsys, monkeypatch
):
    """A different spelling of the input path is the same destination."""
    rom, config = _synthetic_sprite_rom(tmp_path)
    sprites, identity = _stub_corpus(SPRITE_PROFILE_ID)
    _patch_corpus(monkeypatch, sprites)

    before = rom.read_bytes()
    spelling = tmp_path / "unused" / ".." / rom.name
    exit_code = main(_export_argv(config, rom, str(identity), spelling))

    captured = capsys.readouterr()
    assert exit_code != 0, captured.out
    assert "source" in captured.err
    assert rom.read_bytes() == before


def test_export_still_writes_a_safe_distinct_destination(
    tmp_path, capsys, monkeypatch
):
    """The positive control: the guard must not refuse an ordinary export."""
    rom, config = _synthetic_sprite_rom(tmp_path)
    sprites, identity = _stub_corpus(SPRITE_PROFILE_ID)
    _patch_corpus(monkeypatch, sprites)

    before = rom.read_bytes()
    out = tmp_path / "export" / "sprite_0000.png"
    exit_code = main(_export_argv(config, rom, str(identity), out))

    captured = capsys.readouterr()
    assert exit_code == 0, captured.err
    blob = out.read_bytes()
    assert blob.startswith(_PNG_MAGIC)
    decoded = indexed_png.decode(blob)
    assert decoded[1:3] == (2, 2)
    # The out directory did not exist: the command creates it, as before.
    assert rom.read_bytes() == before
