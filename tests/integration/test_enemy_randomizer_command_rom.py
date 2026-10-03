"""Write-safety and caching regression tests. RANDOMIZER-ENEMY-PACK-001.

An independent review of this ticket found the guards below were correct but
untested, and that nothing would have caught them breaking. They are the guards
that stop a write from reaching the verified ROM, so they are pinned here.

Every test works on a COPY of the canonical image inside ``tmp_path``. The real
canonical image is never written by this file, and a test that expected it to be
refused would be meaningless if it ran against the original.

The file skips cleanly when no canonical image is configured, matching the rest
of the ROM-gated suite; the "copy of the canonical ROM" guard genuinely needs the
canonical bytes to mean anything.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

import pytest

from tools.webfoot.cli import load_catalog
from tools.webfoot.commands import randomize as randomize_command
from tools.webfoot.enemy_randomizer.config import PRESETS
from tools.webfoot.enemy_randomizer.planner import (
    EnemyRandomizerContext,
    EnemyRandomizerError,
    plan_enemy_randomization,
)
from tools.webfoot.write import apply_plan

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
_ROM_VARIABLES = ("WEBFOOT_BUU_ROM", "LOGX_CANONICAL_ROM")
_ROM_DEFAULT = Path("roms") / "Dragon Ball Z - Buu's Fury (U).gba"


def _canonical_rom() -> Path | None:
    for name in _ROM_VARIABLES:
        configured = os.environ.get(name)
        if configured and Path(configured).is_file():
            return Path(configured)
    if _ROM_DEFAULT.is_file():
        return _ROM_DEFAULT
    return None


ROM = _canonical_rom()
pytestmark = pytest.mark.skipif(
    ROM is None,
    reason="no canonical Buu's Fury image; set " + " or ".join(_ROM_VARIABLES),
)


@pytest.fixture(scope="module")
def catalog():
    return load_catalog(None)


@pytest.fixture()
def rom_copy(tmp_path) -> Path:
    """A private copy of the verified image. Its hash must never move."""
    target = tmp_path / "input.gba"
    shutil.copyfile(ROM, target)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == CANONICAL_SHA256
    return target


def _args(**overrides):
    """A parsed-argument object with the defaults the CLI would supply."""
    import argparse

    base = dict(
        command="randomize", rom=None, seed="guard-test", preset="stream-safe",
        output=None, spoiler=None, manifest=None, overwrite=False, dry_run=False,
        list_presets=False, stat_range=None, stat_fields=None,
        only=None, without=None, profiles=None,
    )
    base.update(overrides)
    return argparse.Namespace(**base)


def _run(args, capsys):
    code = randomize_command.dispatch(args)
    return code, capsys.readouterr().err


# --- write safety: no destination may be the verified input ------------------


class TestWriteSafety:
    def test_the_output_may_not_be_the_input(self, rom_copy, capsys):
        before = hashlib.sha256(rom_copy.read_bytes()).hexdigest()
        code, err = _run(_args(rom=rom_copy, output=rom_copy), capsys)
        assert code == 2
        assert "the output is the input ROM" in err
        assert hashlib.sha256(rom_copy.read_bytes()).hexdigest() == before

    def test_the_manifest_may_not_be_the_input(self, rom_copy, tmp_path, capsys):
        before = hashlib.sha256(rom_copy.read_bytes()).hexdigest()
        code, err = _run(
            _args(rom=rom_copy, output=tmp_path / "out.gba", manifest=rom_copy), capsys
        )
        assert code == 2
        assert "manifest path is the input ROM" in err
        assert hashlib.sha256(rom_copy.read_bytes()).hexdigest() == before

    def test_the_spoiler_may_not_be_the_input(self, rom_copy, tmp_path, capsys):
        """The defect an earlier revision shipped.

        Only the manifest path was checked, so ``--spoiler <the input ROM>``
        overwrote the verified image with JSON, and because the spoiler is written
        after the post-write source hash check, nothing would have noticed.
        """
        before = hashlib.sha256(rom_copy.read_bytes()).hexdigest()
        code, err = _run(
            _args(rom=rom_copy, output=tmp_path / "out.gba", spoiler=rom_copy), capsys
        )
        assert code == 2
        assert "spoiler log path is the input ROM" in err
        assert hashlib.sha256(rom_copy.read_bytes()).hexdigest() == before

    def test_the_spoiler_may_not_be_the_output(self, rom_copy, tmp_path, capsys):
        out = tmp_path / "out.gba"
        code, err = _run(_args(rom=rom_copy, output=out, spoiler=out), capsys)
        assert code == 2
        assert "same file" in err
        assert not out.exists(), "a refused run must not have created the output"

    def test_an_existing_output_needs_overwrite(self, rom_copy, tmp_path, capsys):
        out = tmp_path / "out.gba"
        out.write_bytes(b"previous")
        code, err = _run(_args(rom=rom_copy, output=out), capsys)
        assert code == 2
        assert "already exists" in err
        assert out.read_bytes() == b"previous", "the refused run replaced it anyway"

    def test_an_existing_manifest_needs_overwrite(self, rom_copy, tmp_path, capsys):
        out = tmp_path / "out.gba"
        manifest = tmp_path / "out.manifest.json"
        manifest.write_text("previous", encoding="utf-8")
        code, err = _run(_args(rom=rom_copy, output=out, manifest=manifest), capsys)
        assert code == 2
        assert "already exists" in err
        assert manifest.read_text(encoding="utf-8") == "previous"
        assert not out.exists()

    def test_an_existing_spoiler_needs_overwrite(self, rom_copy, tmp_path, capsys):
        out = tmp_path / "out.gba"
        spoiler = tmp_path / "spoil.json"
        spoiler.write_text("previous", encoding="utf-8")
        code, err = _run(_args(rom=rom_copy, output=out, spoiler=spoiler), capsys)
        assert code == 2
        assert "already exists" in err
        assert spoiler.read_text(encoding="utf-8") == "previous"

    def test_replacing_a_copy_of_the_canonical_rom_is_refused(
        self, rom_copy, tmp_path, capsys
    ):
        """Refused even WITH --overwrite: this is the one file worth protecting."""
        out = tmp_path / "looks-random.gba"
        shutil.copyfile(rom_copy, out)
        code, err = _run(
            _args(rom=rom_copy, output=out, overwrite=True), capsys
        )
        assert code == 2
        assert "copy of the canonical ROM" in err
        assert hashlib.sha256(out.read_bytes()).hexdigest() == CANONICAL_SHA256

    def test_a_dry_run_writes_nothing(self, rom_copy, tmp_path, capsys):
        out = tmp_path / "out.gba"
        code, _ = _run(
            _args(rom=rom_copy, output=out, dry_run=True), capsys
        )
        assert code == 0
        assert not out.exists()
        assert not (tmp_path / "out.manifest.json").exists()

    def test_the_source_is_untouched_by_a_successful_run(
        self, rom_copy, tmp_path, capsys
    ):
        out = tmp_path / "out.gba"
        code, err = _run(_args(rom=rom_copy, output=out), capsys)
        assert code == 0, err
        assert out.is_file()
        assert hashlib.sha256(rom_copy.read_bytes()).hexdigest() == CANONICAL_SHA256


# --- the loader cache --------------------------------------------------------


class TestContextCaching:
    def test_the_context_matches_the_one_shot_path(self, rom_copy, catalog):
        """Caching must not change a single output byte."""
        preset = PRESETS["stream-safe"]
        base = rom_copy.read_bytes()
        one = plan_enemy_randomization(
            rom_copy, catalog, "cache-equiv", preset.config, preset_name=preset.name
        )
        many = EnemyRandomizerContext(rom_copy, catalog).plan(
            "cache-equiv", preset.config, preset_name=preset.name
        )
        assert [(c.offset, c.new, c.owner) for c in one.plan.changes] == \
            [(c.offset, c.new, c.owner) for c in many.plan.changes]
        assert one.manifest.to_json() == many.manifest.to_json()
        assert hashlib.sha256(apply_plan(base, one.plan)).hexdigest() == \
            hashlib.sha256(apply_plan(base, many.plan)).hexdigest()

    def test_seeds_stay_independent_across_reuse(self, rom_copy, catalog):
        """A shared context must not let one seed's edits leak into the next.

        The stat table and the slot model are per-run state precisely so this
        cannot happen; this is the test that says so.
        """
        preset = PRESETS["stream-safe"]
        context = EnemyRandomizerContext(rom_copy, catalog)
        first = context.plan("independent-a", preset.config, preset_name=preset.name)
        second = context.plan("independent-b", preset.config, preset_name=preset.name)
        # Re-planning the first seed after the second must reproduce it exactly.
        again = context.plan("independent-a", preset.config, preset_name=preset.name)
        assert [(c.offset, c.new) for c in again.plan.changes] == \
            [(c.offset, c.new) for c in first.plan.changes]
        assert again.manifest.to_json() == first.manifest.to_json()
        assert [(c.offset, c.new) for c in second.plan.changes] != \
            [(c.offset, c.new) for c in first.plan.changes]
        assert context.plans == 3

    def test_the_context_plans_many_seeds(self, rom_copy, catalog):
        preset = PRESETS["stream-safe"]
        context = EnemyRandomizerContext(rom_copy, catalog)
        digests = set()
        for index in range(3):
            result = context.plan(f"many-{index}", preset.config, preset_name=preset.name)
            digests.add(hashlib.sha256(
                apply_plan(rom_copy.read_bytes(), result.plan)
            ).hexdigest())
        assert len(digests) == 3, "reusing a context must still give distinct seeds"

    def test_a_changed_source_is_refused(self, rom_copy, catalog, tmp_path):
        """The cheap identity guard that replaces a per-seed re-hash.

        The context deliberately does not re-digest 8 MiB per plan, so it compares
        the file's identity instead. A rewrite underneath it must be caught rather
        than planned against.
        """
        preset = PRESETS["stream-safe"]
        context = EnemyRandomizerContext(rom_copy, catalog)
        context.plan("before-change", preset.config, preset_name=preset.name)

        # Rewrite the file to a different length, which the identity tuple sees.
        rom_copy.write_bytes(rom_copy.read_bytes()[: 1 << 20])
        with pytest.raises(EnemyRandomizerError, match="changed after it was loaded"):
            context.plan("after-change", preset.config, preset_name=preset.name)

    def test_a_stable_source_is_accepted_repeatedly(self, rom_copy, catalog):
        preset = PRESETS["stream-safe"]
        context = EnemyRandomizerContext(rom_copy, catalog)
        for index in range(4):
            context.plan(f"stable-{index}", preset.config, preset_name=preset.name)
        assert context.plans == 4
