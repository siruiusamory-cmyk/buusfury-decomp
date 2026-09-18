"""Deterministic numeric naming and directory layout for the resource library.

ASSET-EXPORT-001. Every path is a pure function of numeric identity. No
direction is named, no animation slot is named, no bank is named and no map is
named: the accepted work establishes occupancy and ordering, not semantics, so
the canonical identity stays the number.

**Padding is fixed, not adaptive.** A width is a constant per artifact family,
so ``chunk_000007.png`` stays ``chunk_000007.png`` whether the corpus holds
eight chunks or four thousand. A layout that padded to the widest current index
would rename every file the moment the corpus grew.

**No prose and no aliases.** This module writes no README, no manifest
description and no human label. The optional alias material the ticket permits
is ROM-derived text, and it lives in ``metadata/aliases.json`` as data rather
than as a filename.
"""

from __future__ import annotations

MAP_DIRECTORY = "map_{index:03d}"
TILE_BANK_DIRECTORY = "bank_{index:03d}"
TILE_FILE = "tile_{index:04d}.png"
CHUNK_FILE = "chunk_{index:06d}.png"
LAYER_FILE = "layer_{slot}.png"
COMPOSITE_FILE = "composite.png"
SHEET_FILE = "sheet.png"

SPRITE_DIRECTORY = "sprite_{sprite_id:03d}"
ANIMATION_DIRECTORY = "animation_{slot:02d}"
FRAME_DIRECTORY = "frame_{index:03d}"
DIRECTION_FILE = "direction_{index}.png"

GRAPHIC_FILE = "graphic_{index:06d}.png"
PALETTE_FILE = "palette_{index:03d}.png"
PALETTE_METADATA_FILE = "palette_{index:03d}.json"

#: Directory names under the export root.
MAPS = "maps"
TILES = "tiles"
TILE_BANKS = "banks"
TILE_CHUNKS = "chunks"
SPRITES = "sprites"
ANIMATIONS = "animations"
SPRITE_GRAPHICS = "sprite_graphics"
PALETTES = "palettes"
METADATA = "metadata"

#: Metadata document names.
MAPS_JSON = "maps.json"
TILE_BANKS_JSON = "tile_banks.json"
CHUNKS_JSON = "chunks.json"
SPRITES_JSON = "sprites.json"
ANIMATIONS_JSON = "animations.json"
FRAMES_JSON = "frames.json"
SPRITE_GRAPHICS_JSON = "sprite_graphics.json"
ALIASES_JSON = "aliases.json"

#: Tile-sheet geometry: 16 tiles per row is 128 pixels wide at 8 pixels a tile.
SHEET_TILE_COLUMNS = 16
#: Frame-sheet geometry: the four direction indices of one frame share a row.
SHEET_DIRECTION_COLUMNS = 4


def map_directory(map_index: int) -> str:
    return MAP_DIRECTORY.format(index=map_index)


def layer_file(slot: int) -> str:
    return LAYER_FILE.format(slot=slot)


def tile_bank_directory(bank_id: int) -> str:
    return TILE_BANK_DIRECTORY.format(index=bank_id)


def tile_file(tile_id: int) -> str:
    return TILE_FILE.format(index=tile_id)


def chunk_file(chunk_id: int) -> str:
    return CHUNK_FILE.format(index=chunk_id)


def sprite_directory(sprite_id: int) -> str:
    return SPRITE_DIRECTORY.format(sprite_id=sprite_id)


def animation_directory(slot: int) -> str:
    return ANIMATION_DIRECTORY.format(slot=slot)


def frame_directory(frame_index: int) -> str:
    return FRAME_DIRECTORY.format(index=frame_index)


def direction_file(direction_index: int) -> str:
    return DIRECTION_FILE.format(index=direction_index)


def graphic_file(graphic_id: int) -> str:
    return GRAPHIC_FILE.format(index=graphic_id)


def palette_file(palette_id: int) -> str:
    return PALETTE_FILE.format(index=palette_id)


def palette_metadata_file(palette_id: int) -> str:
    return PALETTE_METADATA_FILE.format(index=palette_id)


def map_layer_relative_path(map_index: int, slot: int) -> str:
    return f"{MAPS}/{map_directory(map_index)}/{layer_file(slot)}"


def map_composite_relative_path(map_index: int) -> str:
    return f"{MAPS}/{map_directory(map_index)}/{COMPOSITE_FILE}"


def tile_sheet_relative_path(bank_id: int) -> str:
    return f"{TILES}/{TILE_BANKS}/{tile_bank_directory(bank_id)}/{SHEET_FILE}"


def tile_relative_path(bank_id: int, tile_id: int) -> str:
    return (
        f"{TILES}/{TILE_BANKS}/{tile_bank_directory(bank_id)}/tiles/"
        f"{tile_file(tile_id)}"
    )


def chunk_relative_path(chunk_id: int) -> str:
    return f"{TILES}/{TILE_CHUNKS}/{chunk_file(chunk_id)}"


def animation_relative_directory(sprite_id: int, slot: int) -> str:
    return (
        f"{SPRITES}/{sprite_directory(sprite_id)}/{ANIMATIONS}/"
        f"{animation_directory(slot)}"
    )


def frame_direction_relative_path(
    sprite_id: int, slot: int, frame_index: int, direction_index: int
) -> str:
    return (
        f"{animation_relative_directory(sprite_id, slot)}/"
        f"{frame_directory(frame_index)}/{direction_file(direction_index)}"
    )


def animation_sheet_relative_path(sprite_id: int, slot: int) -> str:
    return f"{animation_relative_directory(sprite_id, slot)}/{SHEET_FILE}"


def graphic_relative_path(graphic_id: int) -> str:
    return f"{SPRITE_GRAPHICS}/{graphic_file(graphic_id)}"


def palette_relative_path(palette_id: int) -> str:
    return f"{PALETTES}/{palette_file(palette_id)}"


def palette_metadata_relative_path(palette_id: int) -> str:
    return f"{PALETTES}/{palette_metadata_file(palette_id)}"


def metadata_relative_path(name: str) -> str:
    return f"{METADATA}/{name}"
