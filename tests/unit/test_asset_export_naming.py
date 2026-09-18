"""Portable tests for the ASSET-EXPORT-001 deterministic naming and layout.

Nothing here needs the private ROM.
"""

from __future__ import annotations

import re

import pytest

from tools.export import naming

#: Names the exporter must never invent. The accepted work establishes occupancy
#: and ordering, never semantics, so no direction, animation slot, map, bank or
#: tile may be spelled with a word.
FORBIDDEN_WORDS = (
    "north", "south", "east", "west", "left", "right", "up", "down",
    "walk", "idle", "attack", "hurt", "stand", "run", "block", "dead",
    "special", "teleport", "fusion", "flying", "takeoff", "pickup",
    "overworld", "town", "cave", "forest", "boss", "character", "gohan",
    "goku", "vegeta", "trunks", "piccolo", "buu",
)


def test_map_paths_are_numeric_and_padded():
    assert naming.map_directory(0) == "map_000"
    assert naming.map_directory(451) == "map_451"
    assert naming.map_layer_relative_path(7, 2) == "maps/map_007/layer_2.png"
    assert naming.map_composite_relative_path(39) == "maps/map_039/composite.png"


def test_tile_paths_are_numeric_and_padded():
    assert naming.tile_bank_directory(0) == "bank_000"
    assert naming.tile_file(4) == "tile_0004.png"
    assert naming.tile_sheet_relative_path(17) == "tiles/banks/bank_017/sheet.png"
    assert (
        naming.tile_relative_path(17, 42)
        == "tiles/banks/bank_017/tiles/tile_0042.png"
    )
    assert naming.chunk_relative_path(1827) == "tiles/chunks/chunk_001827.png"


def test_sprite_paths_are_numeric_and_padded():
    assert naming.sprite_directory(10) == "sprite_010"
    assert naming.sprite_directory(306) == "sprite_306"
    assert (
        naming.frame_direction_relative_path(24, 3, 2, 1)
        == "sprites/sprite_024/animations/animation_03/frame_002/direction_1.png"
    )
    assert (
        naming.animation_sheet_relative_path(24, 3)
        == "sprites/sprite_024/animations/animation_03/sheet.png"
    )
    assert naming.graphic_relative_path(0) == "sprite_graphics/graphic_000000.png"
    assert naming.graphic_relative_path(7389) == "sprite_graphics/graphic_007389.png"


@pytest.mark.parametrize(
    "builder",
    [
        lambda: naming.map_directory(0),
        lambda: naming.tile_bank_directory(0),
        lambda: naming.tile_file(0),
        lambda: naming.chunk_file(0),
        lambda: naming.sprite_directory(10),
        lambda: naming.animation_directory(0),
        lambda: naming.frame_directory(0),
        lambda: naming.direction_file(0),
        lambda: naming.graphic_file(0),
        lambda: naming.palette_file(0),
        lambda: naming.palette_metadata_file(0),
    ],
)
def test_names_carry_no_semantic_word(builder):
    name = builder().lower()
    for word in FORBIDDEN_WORDS:
        assert word not in name, f"{name} carries the invented word {word!r}"


def test_padding_is_fixed_not_adaptive():
    """A width is a constant per family, so growth never renames a file."""
    assert naming.chunk_file(7) == "chunk_000007.png"
    assert naming.chunk_file(700000) == "chunk_700000.png"
    assert naming.sprite_directory(10) == "sprite_010"


def test_every_numeric_name_matches_a_strict_pattern():
    patterns = {
        naming.map_directory(3): r"^map_\d{3}$",
        naming.sprite_directory(10): r"^sprite_\d{3}$",
        naming.animation_directory(0): r"^animation_\d{2}$",
        naming.frame_directory(0): r"^frame_\d{3}$",
        naming.direction_file(0): r"^direction_\d\.png$",
        naming.tile_file(0): r"^tile_\d{4}\.png$",
        naming.chunk_file(0): r"^chunk_\d{6}\.png$",
        naming.graphic_file(0): r"^graphic_\d{6}\.png$",
        naming.palette_file(0): r"^palette_\d{3}\.png$",
    }
    for name, pattern in patterns.items():
        assert re.match(pattern, name), f"{name} does not match {pattern}"


def test_metadata_document_names_are_exact():
    assert naming.metadata_relative_path(naming.MAPS_JSON) == "metadata/maps.json"
    for name in (
        naming.MAPS_JSON,
        naming.TILE_BANKS_JSON,
        naming.CHUNKS_JSON,
        naming.SPRITES_JSON,
        naming.ANIMATIONS_JSON,
        naming.FRAMES_JSON,
        naming.SPRITE_GRAPHICS_JSON,
        naming.ALIASES_JSON,
    ):
        assert name.endswith(".json")
        assert name.lower() == name


def test_no_path_builder_emits_a_document_suffix():
    """The resource library holds no README, note or text file."""
    for path in (
        naming.map_composite_relative_path(0),
        naming.tile_sheet_relative_path(0),
        naming.chunk_relative_path(0),
        naming.graphic_relative_path(0),
        naming.animation_sheet_relative_path(10, 0),
        naming.palette_relative_path(0),
        naming.palette_metadata_relative_path(0),
    ):
        assert path.endswith(".png") or path.endswith(".json")
