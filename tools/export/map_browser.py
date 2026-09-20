"""Read-only map-browser facade over the accepted ASSET-EXPORT schemas.

DRAGONBYTE-Z-MAP-BROWSER-001. The Map Browser tab renders one map at a time as
per-layer 8bpp palette-index pixels. This module composes the accepted readers in
:mod:`tools.export.canonical` (MapEntry enumeration, layer classification, chunk
and tile-bank decoding, the Map 19 terrain-field handler) with the pure pixel
functions in :mod:`tools.export.render`. A widget that calls this module computes
no ROM-format value of its own and never reimplements an accepted binary format.

It is read-only and deterministic: nothing here writes, and every value comes
from the same readers the resource exporter already uses.

DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001 adds two read-only services the layout
editor's preview and chunk chooser need, and neither one writes anything:

* :func:`render_map` accepts ``chunk_overrides`` - a per-cell pointer
  substitution applied to a layer's window *in memory* - so the editor can show
  what a pending layout edit would look like without touching a byte of the
  image; and
* :func:`render_chunk_images` renders the chunks a layer already contains, which
  is what the chooser displays.

:func:`validate_cell_replacement` is the single statement of the policy every
such substitution must satisfy, and :mod:`tools.webfoot.map_layout_write` - the
only writer - re-uses it rather than restating it. It lives here because it is a
read-side fact about the accepted dominant form: which references a chunk-pointer
window may hold.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Iterable, Mapping

from . import canonical as canon
from . import render as render_sdk
from . import webfoot_strict as ws

#: Layer classifications that establish a slot draws pixels.
_GRAPHICAL_CLASSES = (
    "dominant",
    "static_graphical_screenblock",
    "static_graphical_terrain_field",
)

#: Only the canonical Buu's Fury USA image is supported. Every address the
#: accepted readers use (the MapEntry table, the text pointer table, the bank
#: table, the BG palette) is specific to that image; a different image - even one
#: of the same 8 MiB size - would resolve different bytes and must be refused
#: rather than enumerated as garbage. This is the same image
#: `tools.webfoot.map_render` gates on.
SUPPORTED_ROM_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)


class MapBrowserError(ValueError):
    """A map cannot be enumerated or rendered for the browser."""


def validate_cell_replacement(
    layer_addresses: tuple[int, ...], replacement: object
) -> int:
    """Whether a value may occupy a dominant-layer chunk-pointer cell.

    The whole policy, in one place: a cell of the accepted dominant form may only
    reference an existing, non-null chunk pointer **the same layer already uses**.
    Nothing else is established - not the null pointer (which the engine's own
    occupancy test reads as unoccupied), not a chunk from another layer, not a
    fresh address the layer does not contain (which would be allocation, not a
    fixed-size replacement), and not a boolean that merely equals an integer.

    :mod:`tools.webfoot.map_layout_write` is the only module that writes such a
    cell, and it calls this function rather than restating the rule, so the
    preview path and the write path can never disagree about what is legal.

    Returns the accepted pointer so a caller can use the result directly.
    """
    if type(replacement) is not int:
        raise MapBrowserError("a chunk pointer must be an integer address")
    if replacement == 0:
        raise MapBrowserError("the null chunk pointer is not a replacement")
    if replacement not in layer_addresses:
        raise MapBrowserError(
            "a replacement chunk must already be used by the same dominant layer"
        )
    return replacement


@dataclass(frozen=True, slots=True)
class ChunkImage:
    """One chunk of a layer, rendered through its owning map's character block."""

    address: int
    width: int
    height: int
    pixels: bytes


@dataclass(frozen=True, slots=True)
class MapIndexEntry:
    """One flat row for the browser's map list."""

    index: int
    #: The ROM text resolved through MapEntry ``+0x0C``, or None when the map
    #: publishes no text. The relationship is CONFIRMED; calling the string a
    #: *name* is not promoted, so callers present it as a ROM-derived label and
    #: fall back to the neutral ``map:NNNN`` identity when it is absent.
    name: str | None
    text_index: int | None


@dataclass(frozen=True, slots=True)
class MapBrowserLayer:
    """One layer slot of a rendered map, as linear 8bpp palette indices."""

    slot: int
    classification: str
    handler: int
    #: The byte the engine adds to ``BGxCNT``; the accepted renderer uses it as a
    #: draw-order key (lower draws on top). Not promoted to a semantic priority.
    addend: int
    width: int
    height: int
    pixels: bytes

    @property
    def graphical(self) -> bool:
        return self.classification in _GRAPHICAL_CLASSES


@dataclass(frozen=True, slots=True)
class MapBrowserResult:
    """A rendered map: per-layer indices, palette, canvas size and composite."""

    index: int
    name: str | None
    width: int
    height: int
    layers: tuple[MapBrowserLayer, ...]
    #: All graphical layers composed origin-aligned in descending
    #: ``(addend, slot)`` order. Index 0 stays transparent (it is the unpainted
    #: hole), so a consumer can flatten it against a backdrop or a checkerboard.
    composite: bytes
    palette: tuple[tuple[int, int, int], ...]
    warnings: tuple[str, ...]

    @property
    def graphical_layer_count(self) -> int:
        return sum(1 for layer in self.layers if layer.graphical)


def _coerce(rom: "canon.Rom | bytes | bytearray") -> canon.Rom:
    if isinstance(rom, canon.Rom):
        return rom
    if not isinstance(rom, (bytes, bytearray)):
        raise MapBrowserError("rom must be bytes")
    return canon.Rom(rom)


def _verify_supported_rom(rom: canon.Rom) -> None:
    """Fail closed on any image that is not the canonical Buu's Fury ROM.

    The accepted readers resolve profile-specific addresses; applying them to any
    other image (even another verified 8 MiB profile) would silently enumerate
    garbage. This mirrors `tools.webfoot.map_render._verify_supported_rom`.
    """
    actual = hashlib.sha256(rom.data).hexdigest()
    if actual != SUPPORTED_ROM_SHA256:
        raise MapBrowserError(
            "the Map Browser supports the canonical Buu's Fury USA rev0 ROM only; "
            f"got SHA-256 {actual}"
        )


def _resolve_name(rom: canon.Rom, text_index: int | None) -> str | None:
    if text_index is None:
        return None
    text = rom.text(text_index)
    return text or None


_ACCEPTED_ERRORS = (canon.CanonicalError, ws.ContainerError, render_sdk.RenderError)


def read_map_index(rom: "canon.Rom | bytes | bytearray") -> tuple[MapIndexEntry, ...]:
    """Every MapEntry with its ROM-derived label, in table order."""
    rom = _coerce(rom)
    _verify_supported_rom(rom)
    try:
        entries = canon.read_map_entries(rom)
    except _ACCEPTED_ERRORS as exc:
        raise MapBrowserError(f"could not enumerate maps: {exc}") from exc
    return tuple(
        MapIndexEntry(
            index=entry.index,
            name=_resolve_name(rom, entry.text_index),
            text_index=entry.text_index,
        )
        for entry in entries
    )


def map_label(rom: "canon.Rom | bytes | bytearray", map_index: int) -> str | None:
    """The ROM-derived label of one map, or None when it publishes no text.

    The same value :func:`read_map_index` puts in :attr:`MapIndexEntry.name`, for a
    caller that needs one map's label without enumerating all 452.
    """
    if type(map_index) is not int or not 0 <= map_index < canon.MAP_ENTRY_COUNT:
        raise MapBrowserError(
            f"map index {map_index!r} is outside 0..{canon.MAP_ENTRY_COUNT - 1}"
        )
    rom = _coerce(rom)
    _verify_supported_rom(rom)
    try:
        entry = canon.read_map_entries(rom)[map_index]
    except _ACCEPTED_ERRORS as exc:
        raise MapBrowserError(f"map:{map_index:04d} could not be read: {exc}") from exc
    return _resolve_name(rom, entry.text_index)


def _stitch_dominant(
    rom: canon.Rom,
    layer: canon.LayerRecord,
    cache: dict[int, tuple[int, ...]],
    addresses: tuple[int, ...] | None = None,
) -> tuple[int, ...]:
    """Stitch a dominant layer's chunk grid into one logical entry array.

    Mirrors the accepted loader order (``y * chunk_x + x`` cells, each a 32x32
    plane): for every chunk row, for every local row, for every chunk in that
    row, that local row's 32 entries. A null chunk pointer contributes entry 0,
    the value the engine's own occupancy test treats as unoccupied.

    ``addresses`` optionally substitutes the layer's own window - the preview
    path's in-memory replacement set - and must stay exactly as long as the grid
    the record states.
    """
    side = canon.CHUNK_SIDE_TILES
    if addresses is None:
        addresses = layer.chunk_addresses
    elif len(addresses) != len(layer.chunk_addresses):
        raise MapBrowserError("a layout override set must cover the layer's whole grid")
    blanks = (0,) * (side * side)
    chunks: list[tuple[int, ...]] = []
    for address in addresses:
        if address == 0:
            chunks.append(blanks)
            continue
        if address not in cache:
            cache[address] = canon.read_chunk_entries(rom, address)
        chunks.append(cache[address])
    out: list[int] = []
    for block_y in range(layer.chunk_y):
        for local_y in range(side):
            for block_x in range(layer.chunk_x):
                chunk = chunks[block_y * layer.chunk_x + block_x]
                start = local_y * side
                out.extend(chunk[start : start + side])
    return tuple(out)


def _resolve_chunk_overrides(
    records: tuple[canon.LayerRecord, ...],
    overrides: Mapping[tuple[int, int], int] | None,
) -> dict[int, tuple[int, ...]]:
    """Apply requested cell replacements to copies of layer pointer windows.

    Keys are ``(layer slot, row-major cell)`` and values are replacement chunk
    pointers. Every request is re-validated here - the slot must exist, its record
    must be the accepted dominant form, the cell must be inside that record's own
    grid, and the pointer must satisfy :func:`validate_cell_replacement` - so a
    preview can never be driven with a reference the proven writer would refuse.
    Nothing is written and no ROM byte is touched; the result is a substituted
    address tuple per slot.
    """
    if not overrides:
        return {}
    by_slot = {record.slot: record for record in records}
    resolved: dict[int, dict[int, int]] = {}
    for key, replacement in overrides.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise MapBrowserError("a chunk override key is a (layer slot, cell) pair")
        slot, cell = key
        record = by_slot.get(slot)
        if type(slot) is not int or record is None:
            raise MapBrowserError(f"there is no layer slot {slot!r} on this map")
        if record.handler != canon.DOMINANT_LAYER_HANDLER:
            raise MapBrowserError(
                f"layer slot {slot} is {record.classification}, which has no chunk grid"
            )
        if type(cell) is not int or not 0 <= cell < len(record.chunk_addresses):
            raise MapBrowserError(f"chunk cell {cell!r} is outside layer slot {slot}")
        validate_cell_replacement(record.chunk_addresses, replacement)
        resolved.setdefault(slot, {})[cell] = replacement
    return {
        slot: tuple(
            cells.get(index, address)
            for index, address in enumerate(by_slot[slot].chunk_addresses)
        )
        for slot, cells in resolved.items()
    }


def render_map(
    rom: "canon.Rom | bytes | bytearray",
    map_index: int,
    *,
    chunk_overrides: Mapping[tuple[int, int], int] | None = None,
    char_data: bytes | None = None,
) -> MapBrowserResult:
    """Render one map to per-layer indexed pixels, on demand.

    Reads only that map's root, layers, character block and containers. Every
    renderable layer is produced by the accepted reader for its own record form
    (dominant chunk grid, screen-entry plane, or terrain field). A layer whose
    form is not established is surfaced as a warning, never silently guessed.

    ``chunk_overrides`` renders a *pending* dominant-layer layout edit without
    modifying anything: the named cells draw the substituted chunk instead. It is
    the preview path for the layout editor and is refused for any layer, cell or
    pointer the layout writer would not accept.

    ``char_data`` is the map's already-assembled character block, for a caller that
    renders the same map repeatedly (a layout preview answers every chooser click).
    It must come from :func:`tools.export.canonical.assemble_map_char_block` for
    *this* map; the default re-decodes it on every call.
    """
    rom = _coerce(rom)
    if type(map_index) is not int or not 0 <= map_index < canon.MAP_ENTRY_COUNT:
        raise MapBrowserError(
            f"map index {map_index!r} is outside 0..{canon.MAP_ENTRY_COUNT - 1}"
        )
    _verify_supported_rom(rom)
    try:
        entry = canon.read_map_entries(rom)[map_index]
        root = entry.root_address
        records = canon.read_layers(rom, root)
        if char_data is None:
            block, _selectors, _animated = canon.assemble_map_char_block(rom, root)
            char_data = block.data
        elif not isinstance(char_data, bytes) or not char_data:
            raise MapBrowserError("char_data must be this map's assembled character block")
    except _ACCEPTED_ERRORS as exc:
        raise MapBrowserError(f"map:{map_index:04d} could not be read: {exc}") from exc

    overridden = _resolve_chunk_overrides(records, chunk_overrides)
    chunk_cache: dict[int, tuple[int, ...]] = {}
    rendered: list[MapBrowserLayer] = []
    warnings: list[str] = []
    for record in records:
        try:
            addend = rom.u8(root + canon.ROOT_BG_ADDEND_OFFSET + record.slot)
            if record.classification == "absent_placeholder":
                rendered.append(
                    MapBrowserLayer(record.slot, record.classification, record.handler, addend, 0, 0, b"")
                )
                continue
            if not record.renderable:
                warnings.append(
                    f"layer slot {record.slot} is {record.classification}; not rendered"
                )
                rendered.append(
                    MapBrowserLayer(record.slot, record.classification, record.handler, addend, 0, 0, b"")
                )
                continue
            if record.classification == "static_graphical_screenblock":
                grid = canon.read_screenblock_entries(rom, record.address)
                width = height = canon.SCREENBLOCK_PIXELS
                pixels = render_sdk.render_chunk(grid, char_data)
            elif record.classification == "static_graphical_terrain_field":
                containers = canon.read_terrain_field_cells(rom, record.address)
                width, height, pixels = render_sdk.render_terrain_field(
                    containers, record.terrain_grid_x, record.terrain_grid_y, char_data
                )
            else:  # dominant
                width = record.chunk_x * canon.CHUNK_PIXELS
                height = record.chunk_y * canon.CHUNK_PIXELS
                grid = _stitch_dominant(
                    rom, record, chunk_cache, overridden.get(record.slot)
                )
                pixels = render_sdk.render_entries(
                    grid,
                    char_data,
                    record.chunk_x * canon.CHUNK_SIDE_TILES,
                    record.chunk_y * canon.CHUNK_SIDE_TILES,
                )
            rendered.append(
                MapBrowserLayer(record.slot, record.classification, record.handler, addend, width, height, pixels)
            )
        except _ACCEPTED_ERRORS as exc:
            raise MapBrowserError(
                f"map:{map_index:04d} layer slot {record.slot} did not render: {exc}"
            ) from exc

    graphical = tuple(layer for layer in rendered if layer.graphical)
    if not graphical:
        return MapBrowserResult(
            index=map_index,
            name=_resolve_name(rom, entry.text_index),
            width=0,
            height=0,
            layers=tuple(rendered),
            composite=b"",
            palette=render_sdk.bg_palette_rgb(rom),
            warnings=tuple(warnings),
        )

    width = max(layer.width for layer in graphical)
    height = max(layer.height for layer in graphical)
    composite = compose(graphical, width, height)
    warnings.append(
        "composite layers are placed origin-aligned in descending "
        "(BG control addend, BG) order; runtime placement not validated"
    )
    if any(layer.classification == "static_graphical_terrain_field" for layer in graphical):
        warnings.append(
            "a terrain-field layer is rendered as the accepted whole-field "
            "extraction; its static composite is a derived placement, not a claim "
            "that the runtime presents the full field as one image"
        )

    return MapBrowserResult(
        index=map_index,
        name=_resolve_name(rom, entry.text_index),
        width=width,
        height=height,
        layers=tuple(rendered),
        composite=composite,
        palette=render_sdk.bg_palette_rgb(rom),
        warnings=tuple(warnings),
    )


def render_chunk_images(
    rom: "canon.Rom | bytes | bytearray",
    map_index: int,
    addresses: Iterable[int],
    *,
    char_data: bytes | None = None,
) -> tuple[ChunkImage, ...]:
    """Render chunks of one map's character block as 256x256 index images.

    A chunk stores 32x32 tile *ordinals*, which only mean anything resolved
    through the assembled character block of the map that uses them, so the map
    identity is part of the call. This is what a chunk chooser displays; the
    pointers come from the layer the caller is editing.

    ``char_data`` is this map's already-assembled character block, exactly as
    :func:`render_map` takes it, so a chooser refill does not re-decode a block the
    caller already holds. As there, it must be the block for *this* map.
    """
    rom = _coerce(rom)
    if type(map_index) is not int or not 0 <= map_index < canon.MAP_ENTRY_COUNT:
        raise MapBrowserError(
            f"map index {map_index!r} is outside 0..{canon.MAP_ENTRY_COUNT - 1}"
        )
    _verify_supported_rom(rom)
    try:
        entry = canon.read_map_entries(rom)[map_index]
        if char_data is None:
            block, _selectors, _animated = canon.assemble_map_char_block(
                rom, entry.root_address
            )
            char_data = block.data
        elif not isinstance(char_data, bytes) or not char_data:
            raise MapBrowserError("char_data must be this map's assembled character block")
        images: list[ChunkImage] = []
        for address in addresses:
            if type(address) is not int or address == 0:
                raise MapBrowserError("a chunk image requires a non-null chunk pointer")
            entries = canon.read_chunk_entries(rom, address)
            images.append(
                ChunkImage(
                    address=address,
                    width=canon.CHUNK_PIXELS,
                    height=canon.CHUNK_PIXELS,
                    pixels=render_sdk.render_chunk(entries, char_data),
                )
            )
    except _ACCEPTED_ERRORS as exc:
        raise MapBrowserError(
            f"map:{map_index:04d} chunks could not be rendered: {exc}"
        ) from exc
    return tuple(images)


def compose(visible: tuple[MapBrowserLayer, ...], width: int, height: int) -> bytes:
    """Compose the given layers onto one indexed canvas by the accepted order."""
    try:
        return render_sdk.compose_layers(
            tuple((layer.addend, layer.slot, layer.width, layer.height, layer.pixels) for layer in visible),
            width,
            height,
        )
    except _ACCEPTED_ERRORS as exc:
        raise MapBrowserError(f"could not compose layers: {exc}") from exc


def rgba(indices: bytes, palette: tuple[tuple[int, int, int], ...]) -> bytes:
    """Expand 8bpp palette indices to RGBA with index 0 transparent.

    Convenience so a widget builds a ``QImage`` from one facade call instead of
    reaching into the render module directly.
    """
    try:
        return render_sdk.to_rgba(indices, render_sdk.rgba_table(palette))
    except _ACCEPTED_ERRORS as exc:
        raise MapBrowserError(f"could not expand pixels: {exc}") from exc
