"""Export-side facade over the SDK map view.

DRAGONBYTE-Z-MAP-BROWSER-001 built this module as a read-only map browser over
the accepted ASSET-EXPORT schemas, composing ``tools.export.canonical`` readers
with ``tools.export.render`` pixel functions. CQA-04 moved the view itself, and
every reader and tile primitive under it, into the SDK:

* the map-entry, layer, chunk, selector, screen-entry and terrain-field reads are
  :mod:`tools.webfoot.formats.map_graphics`;
* the entry-to-pixels render and the GBA tile codec are
  :mod:`tools.webfoot.formats.bg_tilemap` and
  :mod:`tools.webfoot.formats.sprite_graphics`;
* the classified render, the chunk chooser and the pixel composition are
  :mod:`tools.webfoot.map_view`;
* the chunk-replacement policy is
  :func:`tools.webfoot.map_layout_write.validate_chunk_replacement`.

What is left here is a **facade**: the same names, over the SDK implementation,
for the resource exporter's own consumers. Nothing in this file decodes a ROM
byte, and ``tests/unit/test_map_decode_authority.py`` fails if the SDK is made to
depend on it again.
"""

from __future__ import annotations

from typing import Iterable

from tools.webfoot import map_view as _mv
from tools.webfoot.formats import map_graphics as _mg
from tools.webfoot.map_layout_write import validate_chunk_replacement as _validate

#: Re-exported view types and readers. These are the SDK's objects, not copies:
#: `isinstance` and dataclass equality hold across the two spellings, which is
#: what makes this a facade rather than a second implementation.
MapBrowserError = _mv.MapBrowserError
MapIndexEntry = _mv.MapIndexEntry
MapBrowserLayer = _mv.MapBrowserLayer
MapBrowserResult = _mv.MapBrowserResult
ChunkImage = _mv.ChunkImage
read_map_index = _mv.read_map_index
render_map = _mv.render_map
render_chunk_images = _mv.render_chunk_images
compose = _mv.compose
rgba = _mv.rgba

#: Every map/graphics constant a consumer of this facade reached for, taken from
#: the one owner rather than restated.
CHUNK_PIXELS = _mv.CHUNK_PIXELS
CHUNK_SIDE_TILES = _mv.CHUNK_SIDE_TILES
CHUNK_ENTRY_COUNT = _mv.CHUNK_ENTRY_COUNT
CHUNK_DECODED_BYTES = _mg.CHUNK_DECODED_BYTES
SCREENBLOCK_PIXELS = _mv.SCREENBLOCK_PIXELS
DOMINANT_LAYER_HANDLER = _mv.DOMINANT_LAYER_HANDLER
ABSENT_LAYER_HANDLER = _mg.ABSENT_LAYER_HANDLER
ABSENT_LAYER_RECORD = _mg.ABSENT_LAYER_RECORD
SCREENBLOCK_HANDLERS = _mg.SCREENBLOCK_HANDLERS
TERRAIN_FIELD_LAYER_HANDLER = _mg.TERRAIN_FIELD_LAYER_HANDLER
TERRAIN_FIELD_CELL_TILES = _mv.TERRAIN_FIELD_CELL_TILES
BG_PALETTE_ENTRIES = _mv.BG_PALETTE_ENTRIES
GRAPHICAL_CLASSES = _mv.GRAPHICAL_CLASSES


def canonical_identity():
    """The base image the view's readers describe.

    Read from the packaged profile rather than held as a literal here: this
    stack's readers resolve table addresses that are the profile's declarations,
    so the identity that authorises them must be the same declaration.
    """
    return _mv.canonical_identity()


def map_label(rom, map_index: int) -> str | None:
    """The ROM-derived label of one map, or None when it publishes no text."""
    return _mv.map_label(rom, map_index)


def validate_cell_replacement(
    layer_addresses: tuple[int, ...], replacement: object
) -> int:
    """Whether a value may occupy a dominant-layer chunk-pointer cell.

    The whole policy is the SDK's
    (:func:`tools.webfoot.map_layout_write.validate_chunk_replacement`), which the
    write path calls too, so the preview path and the write path can never
    disagree about what is legal. It is translated into this facade's error
    family here so existing exporters keep catching what they already caught.
    """
    try:
        return _validate(layer_addresses, replacement)
    except Exception as exc:  # MapLayoutWriteError, re-homed
        raise MapBrowserError(str(exc)) from exc


def render_chunk_images_for(
    rom,
    map_index: int,
    addresses: Iterable[int],
    *,
    char_data: bytes | None = None,
) -> tuple[ChunkImage, ...]:
    """Historical alias of :func:`tools.webfoot.map_view.render_chunk_images`."""
    return _mv.render_chunk_images(
        rom, map_index, addresses, char_data=char_data
    )


__all__ = [
    "MapBrowserError",
    "MapIndexEntry",
    "MapBrowserLayer",
    "MapBrowserResult",
    "ChunkImage",
    "read_map_index",
    "map_label",
    "render_map",
    "render_chunk_images",
    "validate_cell_replacement",
    "compose",
    "rgba",
    "canonical_identity",
    "CHUNK_PIXELS",
    "CHUNK_SIDE_TILES",
    "DOMINANT_LAYER_HANDLER",
    "TERRAIN_FIELD_CELL_TILES",
    "BG_PALETTE_ENTRIES",
]
