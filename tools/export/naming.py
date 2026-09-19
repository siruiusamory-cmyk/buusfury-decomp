"""Deterministic numeric naming and directory layout for the resource library.

ASSET-EXPORT-001. Every path is built from a numeric identity. No direction is
named, no animation slot is named and no bank is named: the accepted work
establishes occupancy and ordering, not semantics, so the canonical identity
stays the number.

**A confirmed ROM name is appended where one exists.** Where the accepted data
carries a genuine text string for an object - a map's text-table relationship, an
appearance definition's name - the sanitized string is appended after the numeric
id, so `map_039` becomes `map_039_grand_kai_s_planet` and `sprite_028` becomes
`sprite_028_babidi`. The numeric id stays first and stays canonical: the name is
a convenience for reference, and a stripped or changed name can never make a path
ambiguous because the id alone is unique. Nothing is invented - a name is used
only when it resolves from an accepted ROM structure, and the full mapping lives
in `metadata/names.json`.

**Padding is fixed, not adaptive.** A width is a constant per artifact family,
so ``chunk_000007.png`` stays ``chunk_000007.png`` whether the corpus holds
eight chunks or four thousand. A layout that padded to the widest current index
would rename every file the moment the corpus grew.

**No prose.** This module writes no README, no manifest description and no human
label of its own; every name it appends is a direct ROM string.
"""

from __future__ import annotations

MAP_DIRECTORY = "map_{index:03d}"
NAMED_MAP_DIRECTORY = "map_{index:03d}_{name}"
TILE_BANK_DIRECTORY = "bank_{index:03d}"
TILE_FILE = "tile_{index:04d}.png"
CHUNK_FILE = "chunk_{index:06d}.png"
LAYER_FILE = "layer_{slot}.png"
COMPOSITE_FILE = "composite.png"
MAP_RECORD_FILE = "map.json"
SHEET_FILE = "sheet.png"

SPRITE_DIRECTORY = "sprite_{sprite_id:03d}"
NAMED_SPRITE_DIRECTORY = "sprite_{sprite_id:03d}_{name}"
ANIMATION_DIRECTORY = "animation_{slot:02d}"
FRAME_DIRECTORY = "frame_{index:03d}"
DIRECTION_FILE = "direction_{index}.png"

GRAPHIC_FILE = "graphic_{index:06d}.png"
PALETTE_FILE = "palette_{index:03d}.png"
PALETTE_METADATA_FILE = "palette_{index:03d}.json"

#: Longest sanitized name fragment appended to a directory. Truncation is on a
#: character boundary and the numeric prefix keeps the path unique regardless, so
#: a truncated name can never collide with another identity.
NAME_LIMIT = 48

#: Characters a sanitized name may contain. Everything else collapses to one
#: underscore, so the mapping from a ROM string to a path is deterministic and
#: reversible by inspection against `metadata/names.json`.
NAME_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"

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
NAMES_JSON = "names.json"

#: Tile-sheet geometry: 16 tiles per row is 128 pixels wide at 8 pixels a tile.
SHEET_TILE_COLUMNS = 16
#: Frame-sheet geometry: the four direction indices of one frame share a row.
SHEET_DIRECTION_COLUMNS = 4


def sanitize_name(text: str) -> str:
    """A ROM string to a deterministic path fragment.

    Lowercased, every character outside :data:`NAME_ALPHABET` collapsed to a
    single underscore, leading and trailing underscores removed, and truncated to
    :data:`NAME_LIMIT` characters. Two different strings may sanitize to the same
    fragment - a variant of the same name, for example - and that is harmless,
    because the fragment is always appended to a numeric identity that is unique
    on its own. An empty result means the string held no usable characters.
    """
    if not isinstance(text, str):
        raise TypeError("a name must be a string")
    out: list[str] = []
    for character in text.lower():
        if character in NAME_ALPHABET:
            out.append(character)
        elif out and out[-1] != "_":
            out.append("_")
    fragment = "".join(out).strip("_")
    return fragment[:NAME_LIMIT].strip("_")


def map_directory(map_index: int, name: str | None = None) -> str:
    """``map_039`` or ``map_039_grand_kais_planet`` when the ROM names it."""
    fragment = sanitize_name(name) if name else ""
    if not fragment:
        return MAP_DIRECTORY.format(index=map_index)
    return NAMED_MAP_DIRECTORY.format(index=map_index, name=fragment)


def layer_file(slot: int) -> str:
    return LAYER_FILE.format(slot=slot)


def tile_bank_directory(bank_id: int) -> str:
    return TILE_BANK_DIRECTORY.format(index=bank_id)


def tile_file(tile_id: int) -> str:
    return TILE_FILE.format(index=tile_id)


def chunk_file(chunk_id: int) -> str:
    return CHUNK_FILE.format(index=chunk_id)


def sprite_directory(sprite_id: int, name: str | None = None) -> str:
    """``sprite_028`` or ``sprite_028_babidi`` when an appearance names it."""
    fragment = sanitize_name(name) if name else ""
    if not fragment:
        return SPRITE_DIRECTORY.format(sprite_id=sprite_id)
    return NAMED_SPRITE_DIRECTORY.format(sprite_id=sprite_id, name=fragment)


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


def map_layer_relative_path(map_index: int, slot: int, name: str | None = None) -> str:
    return f"{MAPS}/{map_directory(map_index, name)}/{layer_file(slot)}"


def map_composite_relative_path(map_index: int, name: str | None = None) -> str:
    return f"{MAPS}/{map_directory(map_index, name)}/{COMPOSITE_FILE}"


def map_record_relative_path(map_index: int, name: str | None = None) -> str:
    return f"{MAPS}/{map_directory(map_index, name)}/{MAP_RECORD_FILE}"


def tile_sheet_relative_path(bank_id: int) -> str:
    return f"{TILES}/{TILE_BANKS}/{tile_bank_directory(bank_id)}/{SHEET_FILE}"


def tile_relative_path(bank_id: int, tile_id: int) -> str:
    return (
        f"{TILES}/{TILE_BANKS}/{tile_bank_directory(bank_id)}/tiles/"
        f"{tile_file(tile_id)}"
    )


def chunk_relative_path(chunk_id: int) -> str:
    return f"{TILES}/{TILE_CHUNKS}/{chunk_file(chunk_id)}"


def animation_relative_directory(
    sprite_id: int, slot: int, name: str | None = None
) -> str:
    return (
        f"{SPRITES}/{sprite_directory(sprite_id, name)}/{ANIMATIONS}/"
        f"{animation_directory(slot)}"
    )


def frame_direction_relative_path(
    sprite_id: int,
    slot: int,
    frame_index: int,
    direction_index: int,
    name: str | None = None,
) -> str:
    return (
        f"{animation_relative_directory(sprite_id, slot, name)}/"
        f"{frame_directory(frame_index)}/{direction_file(direction_index)}"
    )


def animation_sheet_relative_path(
    sprite_id: int, slot: int, name: str | None = None
) -> str:
    return f"{animation_relative_directory(sprite_id, slot, name)}/{SHEET_FILE}"


def graphic_relative_path(graphic_id: int) -> str:
    return f"{SPRITE_GRAPHICS}/{graphic_file(graphic_id)}"


def palette_relative_path(palette_id: int) -> str:
    return f"{PALETTES}/{palette_file(palette_id)}"


def palette_metadata_relative_path(palette_id: int) -> str:
    return f"{PALETTES}/{palette_metadata_file(palette_id)}"


def metadata_relative_path(name: str) -> str:
    return f"{METADATA}/{name}"
