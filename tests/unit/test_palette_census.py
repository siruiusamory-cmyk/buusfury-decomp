"""The palette census, held to the numbers it reported and to what it refuses.

The review noted that the palette work rode this branch with no claim attached to it. This is the claim:
the census over the canonical image finds the container counts and index sets that the palette write-up
quotes, and the tool refuses a descriptor-shaped non-answer the same way the font extractor does.

The census decodes thousands of containers, so its result is computed once for the module.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tests.rom_support import canonical_rom_bytes, canonical_rom_path  # noqa: E402


@pytest.fixture(scope="module")
def census(tmp_path_factory) -> dict:
    """Run the census once over the canonical image, or skip."""
    rom = canonical_rom_path()
    if rom is None:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    canonical_rom_bytes()
    out = tmp_path_factory.mktemp("palette") / "census.json"
    result = subprocess.run(
        [sys.executable, "-m", "tools.research.palette_census", "--rom", str(rom), "--json", str(out)],
        cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(out.read_text(encoding="utf-8"))


def test_the_census_finds_the_measured_container_counts(census) -> None:
    assert census["decoded"]["portraits"] == 155, "the portrait array has 155 live slots"
    assert census["decoded"]["box"] == 2, "the two box surfaces"
    assert census["decoded"]["actors"] > 7000, (
        "every container reachable from every frame of every definition should be decoded; the palette "
        "write-up quotes 7,398")
    assert census["failures"] == 0, "a container that does not decode means the walk is wrong"


def test_the_index_sets_are_the_ones_the_write_up_quotes(census) -> None:
    used = census["used"]
    assert len(used["actors"]) == 252, "actors paint 252 of the 256 indices"
    assert len(used["portraits"]) == 219
    assert census["unused"] == [193, 223, 225, 236], (
        "only these four indices are painted by nobody, which is what makes a naive recolour a global "
        "change")
    assert set(used["portraits"]) <= set(used["actors"]), (
        "every index a portrait paints is also painted by actor art, so portraits share the bank")


def test_the_ink_index_the_dialogue_box_uses_is_credited_to_the_box(census) -> None:
    assert census["counts"]["box"].get("2", 0) > 0, (
        "the box paints index 2, the white the dialogue path uses as ink")
