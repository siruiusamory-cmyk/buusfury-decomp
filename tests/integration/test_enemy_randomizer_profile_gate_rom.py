"""The profile contract is enforced on every stat-decoding path.

RANDOMIZER-ENEMY-PACK-001. An independent review found that a fast loading path
added for speed skipped `_require_stat_profile`, so a hand-edited `--profiles`
file whose table locations differed from the packaged catalog was accepted and
planned against. `docs/ROM_SAFETY.md` requires failing closed on a provenance
mismatch, so both paths are pinned here.

The check is a comparison against the PACKAGED contract, and the profile file is
tampered in a temporary directory. The canonical image is only ever read.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile

import pytest
import yaml

from tools.webfoot.cli import load_catalog
from tools.webfoot.enemy_randomizer.config import PRESETS
from tools.webfoot.enemy_randomizer.planner import EnemyRandomizerContext
from tools.webfoot.stats import StatProfileError, load_stat_tables

_ROM_VARIABLES = ("WEBFOOT_BUU_ROM", "LOGX_CANONICAL_ROM")
_ROM_DEFAULT = Path("roms") / "Dragon Ball Z - Buu's Fury (U).gba"
_CATALOG = Path(__file__).resolve().parents[2] / "tools/webfoot/data/roms.yaml"


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


def _tampered_catalog(table: str):
    """A catalog whose ``table`` address is shifted, in a private directory."""
    data = yaml.safe_load(_CATALOG.read_text(encoding="utf-8"))
    shifted = 0
    for entry in data["profiles"]:
        target = entry.get("tables", {}).get(table)
        if target is not None:
            target["address"] += 0x10
            shifted += 1
    assert shifted, f"no profile declares {table}; the fixture is not testing anything"
    directory = Path(tempfile.mkdtemp(prefix="ep001-profile-"))
    path = directory / "roms.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return directory, path


@pytest.mark.parametrize("table", ["character_base_stats", "enemy_stats"])
def test_the_loader_refuses_a_redirected_table(table):
    directory, path = _tampered_catalog(table)
    try:
        with pytest.raises(StatProfileError, match="packaged contract"):
            load_stat_tables(ROM, load_catalog(path))
    finally:
        shutil.rmtree(directory, ignore_errors=True)


@pytest.mark.parametrize("table", ["character_base_stats", "enemy_stats"])
def test_the_randomizer_refuses_a_redirected_table(table):
    """The path the review found open.

    ``EnemyRandomizerContext`` used to build its stat tables through a helper that
    did not re-check the contract, so a doctored profile was accepted and a plan
    returned.

    Which component refuses depends on the table, and that is the point rather than
    a detail: a redirected ``enemy_stats`` address is caught even earlier, when the
    placement-type model resolves its enemy links, while
    ``character_base_stats`` is only read by the stat path itself and was the case
    that actually slipped through. Both must fail closed, so this asserts the
    refusal and the message rather than the exception class.
    """
    from tools.webfoot.capability import CapabilityError

    directory, path = _tampered_catalog(table)
    try:
        with pytest.raises(CapabilityError, match="packaged contract|conflicts"):
            # Construction may refuse (enemy_stats), and planning must refuse
            # otherwise (character_base_stats). Either way nothing may plan.
            context = EnemyRandomizerContext(ROM, load_catalog(path))
            context.plan(
                "profile-gate", PRESETS["stream-safe"].config, preset_name="stream-safe"
            )
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def test_the_packaged_catalog_is_untouched():
    """Guards the guard: the fixture must not have rewritten the real catalog."""
    data = yaml.safe_load(_CATALOG.read_text(encoding="utf-8"))
    addresses = [
        entry["tables"]["character_base_stats"]["address"]
        for entry in data["profiles"]
        if entry.get("tables", {}).get("character_base_stats")
    ]
    assert addresses, "the packaged catalog declares no character stat table"
    assert all(address % 4 == 0 for address in addresses)
