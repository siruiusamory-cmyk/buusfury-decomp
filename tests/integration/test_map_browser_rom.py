"""ROM-gated integration evidence for the Map Browser facade.

Read-only against the canonical image. The suite skips cleanly when the private
ROM is not configured, and it never writes to it. It pins enumeration, the
ROM-derived labels, representative rendered dimensions, and the accepted Map 19
terrain-field composite digest.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.export import map_browser as mb

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

EXPECTED_ENTRIES = 452
EXPECTED_NAMED = 429
EXPECTED_DISTINCT_NAMES = 69

#: Accepted Map 19 composite index-image digest (ASSET-EXPORT-MAP19-001).
MAP19_COMPOSITE_SHA256 = (
    "2ece490ffb793be9a15e4a176ab70fad1a45526793a9a39a85827429af4cfeec"
)


def _rom_path() -> Path:
    return Path(
        os.environ.get(
            "LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"
        )
    )


@pytest.fixture(scope="module")
def rom_bytes() -> bytes:
    path = _rom_path()
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256
    return data


def test_all_452_maps_enumerate_with_rom_derived_labels(rom_bytes: bytes) -> None:
    index = mb.read_map_index(rom_bytes)
    assert len(index) == EXPECTED_ENTRIES
    named = [entry for entry in index if entry.name]
    assert len(named) == EXPECTED_NAMED
    assert len({entry.name for entry in named}) == EXPECTED_DISTINCT_NAMES

    by_index = {entry.index: entry for entry in index}
    assert by_index[14].name == "Buu's House"
    assert by_index[17].name == "West City"
    assert by_index[39].name == "Grand Kai's Planet"
    assert by_index[451].name == "Heaven"
    assert by_index[8].name is None  # neutral fallback for an unnamed map
    assert by_index[19].name is None  # map 19 publishes no name


def test_representative_maps_render_with_expected_dimensions(rom_bytes: bytes) -> None:
    expectations = {
        14: (256, 256, "Buu's House"),
        17: (512, 512, "West City"),
        39: (1024, 512, "Grand Kai's Planet"),
    }
    for index, (width, height, name) in expectations.items():
        result = mb.render_map(rom_bytes, index)
        assert result.name == name
        assert (result.width, result.height) == (width, height)
        assert result.graphical_layer_count >= 1
        assert len(result.composite) == width * height


def test_map_19_renders_the_accepted_terrain_field(rom_bytes: bytes) -> None:
    result = mb.render_map(rom_bytes, 19)
    classifications = [layer.classification for layer in result.layers]
    assert classifications == [
        "dominant",
        "static_graphical_screenblock",
        "static_graphical_terrain_field",
        "absent_placeholder",
    ]
    assert (result.width, result.height) == (3584, 2560)
    terrain = next(
        layer
        for layer in result.layers
        if layer.classification == "static_graphical_terrain_field"
    )
    assert (terrain.width, terrain.height) == (3584, 2560)
    assert hashlib.sha256(result.composite).hexdigest() == MAP19_COMPOSITE_SHA256
    # The static composite is a derived placement, not a runtime claim.
    assert any("not a claim" in warning for warning in result.warnings)


def test_browsing_is_read_only_and_leaves_the_file_untouched(rom_bytes: bytes) -> None:
    path = _rom_path()
    before_mtime = path.stat().st_mtime_ns
    before_size = path.stat().st_size
    for index in (14, 17, 19, 39):
        mb.render_map(rom_bytes, index)
    assert path.stat().st_mtime_ns == before_mtime
    assert path.stat().st_size == before_size
    assert hashlib.sha256(path.read_bytes()).hexdigest() == CANONICAL_SHA256
