"""Read-only map view: one map, classified, rendered to indexed pixels.

DRAGONBYTE-Z-MAP-BROWSER-001 introduced this view on the export side, where it
was written as a facade over the export stack's own map readers. CQA-04 moved it
here, onto the SDK's format layer: the readers it composes
(:mod:`tools.webfoot.formats.map_graphics`) and the tile renderer it draws with
(:mod:`tools.webfoot.formats.bg_tilemap`) are now the same ones the resource
exporter and the map-layout writer use, so a widget can compose a map without any
part of the SDK reaching into ``tools.export`` for a binary interpretation.

**What this module is.** A *view*: it classifies each of a map root's four layer
slots by the record's own handler, renders every form whose pixels are
established, and reports the ones it cannot as warnings rather than guessing.
That is presentation policy, and it is deliberately not the only policy in the
project - :mod:`tools.webfoot.map_render` is the same ROM read through a
narrower contract (dominant chunk grids only, with a character-block coverage
refusal), and the two may show different things about the same map. What they
cannot do is *decode* a record differently: both read through
``formats.map_graphics``.

**The two read-only services the layout editor's preview needs** also live here,
and neither writes anything:

* :func:`render_map` accepts ``chunk_overrides`` - a per-cell pointer
  substitution applied to a layer's window *in memory* - so the editor can show
  what a pending layout edit would look like without touching a byte; and
* :func:`render_chunk_images` renders the chunks a layer already contains, which
  is what a chooser displays.

Both take an optional already-assembled character block, because a chooser
refills on every click and re-decoding a map's block per render is the dominant
cost of a repeated preview.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Iterable, Mapping

from .formats import bg_tilemap as _bg
from .formats import map_graphics as mg
from .packaged import packaged_profile
from .profile import RomProfile

#: The map/graphics constants this view composes with, re-exported so a caller
#: (a widget drawing chunk cells, a layout editor sizing a grid) asks this module
#: rather than reaching past it into the format layer for the same numbers.
CHUNK_PIXELS = mg.CHUNK_PIXELS
CHUNK_SIDE_TILES = mg.CHUNK_SIDE_TILES
CHUNK_ENTRY_COUNT = mg.CHUNK_ENTRY_COUNT
SCREENBLOCK_PIXELS = mg.SCREENBLOCK_PIXELS
TERRAIN_FIELD_CELL_TILES = mg.TERRAIN_FIELD_CELL_TILES
DOMINANT_LAYER_HANDLER = mg.DOMINANT_LAYER_HANDLER
ROOT_BG_ADDEND_OFFSET = mg.ROOT_BG_ADDEND_OFFSET
ROOT_EXTENT_X_OFFSET = mg.ROOT_EXTENT_X_OFFSET
ROOT_EXTENT_Y_OFFSET = mg.ROOT_EXTENT_Y_OFFSET
ROOT_BG_CONTROL_OFFSET = mg.ROOT_BG_CONTROL_OFFSET
ROOT_CONNECTION_COUNT_OFFSET = mg.ROOT_CONNECTION_COUNT_OFFSET
BG_PALETTE_ENTRIES = mg.BG_PALETTE_ENTRIES

#: Layer classifications that establish a slot draws pixels.
GRAPHICAL_CLASSES = (
    "dominant",
    "static_graphical_screenblock",
    "static_graphical_terrain_field",
)

#: The shared map/graphics operations a caller of this view already holds the
#: reader for, re-exported so a consumer (the layout editor's preview, an
#: exporter comparing its own composition) does not reach past this module into
#: the format layer for the same call.
stitch_dominant_entries = mg.stitch_dominant_entries
dominant_chunk_words = mg.dominant_chunk_words
read_animated_tiles = mg.read_animated_tiles
assemble_map_char_block = mg.assemble_map_char_block


class MapBrowserError(ValueError):
    """A map cannot be enumerated or rendered for the view."""


@dataclass(frozen=True, slots=True)
class ChunkImage:
    """One chunk of a layer, rendered through its owning map's character block."""

    address: int
    width: int
    height: int
    pixels: bytes


@dataclass(frozen=True, slots=True)
class ChunkSubstitution:
    """A pending cell replacement that is a screen-entry plane, not a pointer.

    MAP-CHUNK-AUTHORING-001. A project-authored chunk has no address in the
    canonical image - a build has not run yet, and choosing the address is the
    build's job - so the ordinary ``chunk_overrides`` form, which names an address
    a dominant layer of the map already uses, cannot express it. This carries the authored 32x32
    plane instead, so a preview draws exactly the entries a build would
    materialize, through the same stitch and the same renderer the retail layout
    uses rather than through a second rendering path.
    """

    entries: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.entries) != mg.CHUNK_ENTRY_COUNT:
            raise MapBrowserError(
                f"an authored chunk plane holds {mg.CHUNK_ENTRY_COUNT} entries, "
                f"not {len(self.entries)}"
            )
        for index, value in enumerate(self.entries):
            if type(value) is not int or not 0 <= value <= 0xFFFF:
                raise MapBrowserError(
                    f"authored chunk entry {index} is {value!r}, which is not a "
                    "16-bit screen entry"
                )


@dataclass(frozen=True, slots=True)
class MapIndexEntry:
    """One flat row for a map list."""

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
        return self.classification in GRAPHICAL_CLASSES


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


#: The historical names, kept so a caller that spells the type either way reads
#: the same class. `MapView` is the module's own name for what a browser shows.
MapView = MapBrowserResult
MapLayerView = MapBrowserLayer


def reader_for(
    rom: bytes | bytearray | mg.MapGraphicsReader,
    profile: RomProfile | None = None,
) -> mg.MapGraphicsReader:
    """One bounds-checked reader over these bytes, under this profile.

    The default profile is the packaged canonical one, the same authority the
    profile gate and every other ROM-addressed reader resolve. A caller that
    already holds a reader gets it back unchanged.
    """
    if isinstance(rom, mg.MapGraphicsReader):
        return rom
    if not isinstance(rom, (bytes, bytearray)):
        raise MapBrowserError("rom must be bytes")
    return mg.MapGraphicsReader(
        rom, profile if profile is not None else packaged_profile()
    )


def _check_map_index(reader: mg.MapGraphicsReader, map_index: int) -> None:
    """Bind a map index by the profile's declared MapEntry count.

    Read from the reader's profile rather than a module constant: the count
    decides which maps exist and which map a render targets, so a stale copy
    would refuse a valid map or accept one past the table.
    """
    count = reader.map_entry_count()
    if type(map_index) is not int or not 0 <= map_index < count:
        raise MapBrowserError(
            f"map index {map_index!r} is outside this profile's 0..{count - 1} "
            "declared map-entry range"
        )


def _verify_supported_rom(reader: mg.MapGraphicsReader) -> None:
    """Fail closed on any image the reader's profile does not describe.

    The readers resolve profile-specific addresses; applying them to any other
    image (even another verified 8 MiB profile) would silently enumerate garbage.
    The comparison is the shared profile identity contract - the same rule
    `tools.webfoot.map_render` and the Workbench session use - so there is one
    statement of it rather than one per reader stack.
    """
    actual = hashlib.sha256(reader.data).hexdigest()
    if actual != reader.profile.sha256:
        raise MapBrowserError(
            f"this view supports the image described by profile "
            f"{reader.profile.id!r} only; got SHA-256 {actual}"
        )


def canonical_identity():
    """The base image this view's readers describe, from the packaged catalog."""
    return packaged_profile().identity


def _resolve_name(reader: mg.MapGraphicsReader, text_index: int | None) -> str | None:
    if text_index is None:
        return None
    return reader.text(text_index) or None


_ACCEPTED_ERRORS = (mg.MapGraphicsError, _bg.BgTilemapError)


def read_map_index(
    rom: bytes | bytearray | mg.MapGraphicsReader,
    profile: RomProfile | None = None,
) -> tuple[MapIndexEntry, ...]:
    """Every MapEntry with its ROM-derived label, in table order."""
    reader = reader_for(rom, profile)
    _verify_supported_rom(reader)
    try:
        entries = mg.read_map_entries(reader)
    except _ACCEPTED_ERRORS as exc:
        raise MapBrowserError(f"could not enumerate maps: {exc}") from exc
    return tuple(
        MapIndexEntry(
            index=entry.index,
            name=_resolve_name(reader, entry.text_index),
            text_index=entry.text_index,
        )
        for entry in entries
    )


def map_label(
    rom: bytes | bytearray | mg.MapGraphicsReader,
    map_index: int,
    profile: RomProfile | None = None,
) -> str | None:
    """The ROM-derived label of one map, or None when it publishes no text.

    The same value :func:`read_map_index` puts in :attr:`MapIndexEntry.name`, for
    a caller that needs one map's label without enumerating the whole table.
    """
    reader = reader_for(rom, profile)
    _check_map_index(reader, map_index)
    _verify_supported_rom(reader)
    try:
        entry = mg.read_map_entries(reader)[map_index]
    except _ACCEPTED_ERRORS as exc:
        raise MapBrowserError(f"map:{map_index:04d} could not be read: {exc}") from exc
    return _resolve_name(reader, entry.text_index)


def _resolve_chunk_overrides(
    records: tuple[mg.LayerRecord, ...],
    overrides: Mapping[tuple[int, int], int | "ChunkSubstitution"] | None,
) -> tuple[dict[int, tuple[int, ...]], dict[int, dict[int, tuple[int, ...]]]]:
    """Apply requested cell replacements to copies of layer pointer windows.

    Keys are ``(layer slot, row-major cell)``. A value is either a replacement
    chunk pointer - re-validated here against the shared replacement policy, so a
    preview can never be driven with a reference the proven writer would refuse -
    or a :class:`ChunkSubstitution` carrying a project-authored plane, which has
    no address to validate because a build has not chosen one yet.

    Returns the substituted address windows, plus the authored planes keyed by
    layer slot and then by cell, which the stitch substitutes for a pointer
    lookup. Nothing is written and no ROM byte is touched.
    """
    from .map_layout_write import (
        MapLayoutWriteError,
        legal_chunk_pointers,
        validate_chunk_replacement,
    )

    if not overrides:
        return {}, {}
    by_slot = {record.slot: record for record in records}
    legal = legal_chunk_pointers(*(record.chunk_addresses for record in records))
    addresses: dict[int, dict[int, int]] = {}
    planes: dict[int, dict[int, tuple[int, ...]]] = {}
    for key, replacement in overrides.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise MapBrowserError("a chunk override key is a (layer slot, cell) pair")
        slot, cell = key
        record = by_slot.get(slot)
        if type(slot) is not int or record is None:
            raise MapBrowserError(f"there is no layer slot {slot!r} on this map")
        if record.handler != mg.DOMINANT_LAYER_HANDLER:
            raise MapBrowserError(
                f"layer slot {slot} is {record.classification}, which has no chunk grid"
            )
        if type(cell) is not int or not 0 <= cell < len(record.chunk_addresses):
            raise MapBrowserError(f"chunk cell {cell!r} is outside layer slot {slot}")
        if isinstance(replacement, ChunkSubstitution):
            planes.setdefault(slot, {})[cell] = replacement.entries
            addresses.setdefault(slot, {})[cell] = 0
            continue
        try:
            validate_chunk_replacement(legal, replacement)
        except MapLayoutWriteError as exc:
            raise MapBrowserError(str(exc)) from exc
        addresses.setdefault(slot, {})[cell] = replacement
    return (
        {
            slot: tuple(
                cells.get(index, address)
                for index, address in enumerate(by_slot[slot].chunk_addresses)
            )
            for slot, cells in addresses.items()
        },
        {slot: dict(cells) for slot, cells in planes.items()},
    )


def render_map(
    rom: bytes | bytearray | mg.MapGraphicsReader,
    map_index: int,
    *,
    profile: RomProfile | None = None,
    chunk_overrides: Mapping[tuple[int, int], int | ChunkSubstitution] | None = None,
    char_data: bytes | None = None,
) -> MapBrowserResult:
    """Render one map to per-layer indexed pixels, on demand.

    Reads only that map's root, layers, character block and containers. Every
    renderable layer is produced by the reader for its own record form (dominant
    chunk grid, screen-entry plane, or terrain field). A layer whose form is not
    established is surfaced as a warning, never silently guessed.

    ``chunk_overrides`` renders a *pending* dominant-layer layout edit without
    modifying anything: the named cells draw the substituted chunk instead. It is
    the preview path for the layout editor and is refused for any layer, cell or
    pointer the layout writer would not accept.

    ``char_data`` is the map's already-assembled character block, for a caller
    that renders the same map repeatedly (a layout preview answers every chooser
    click). It must be the block for *this* map; the default assembles it.
    """
    reader = reader_for(rom, profile)
    _check_map_index(reader, map_index)
    _verify_supported_rom(reader)
    try:
        entry = mg.read_map_entries(reader)[map_index]
        root = entry.root_address
        records = mg.read_layers(reader, root)
        if char_data is None:
            block, _stream, _animated = mg.assemble_map_char_block(reader, root)
            char_data = block.data
        elif not isinstance(char_data, bytes) or not char_data:
            raise MapBrowserError("char_data must be this map's assembled character block")
    except _ACCEPTED_ERRORS as exc:
        raise MapBrowserError(f"map:{map_index:04d} could not be read: {exc}") from exc

    overridden, authored_planes = _resolve_chunk_overrides(records, chunk_overrides)
    chunk_cache: dict[int, tuple[int, ...]] = {}
    rendered: list[MapBrowserLayer] = []
    warnings: list[str] = []
    for record in records:
        try:
            addend = reader.u8(root + mg.ROOT_BG_ADDEND_OFFSET + record.slot)
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
                grid = mg.read_screenblock_entries(reader, record.address)
                width = height = mg.SCREENBLOCK_PIXELS
                pixels, _w, _h = _bg.render_entry_words(
                    char_data,
                    grid,
                    map_width_tiles=mg.CHUNK_SIDE_TILES,
                    map_height_tiles=mg.CHUNK_SIDE_TILES,
                    color_256=True,
                )
            elif record.classification == "static_graphical_terrain_field":
                containers = mg.read_terrain_field_cells(reader, record.address)
                width, height, pixels = render_terrain_field(
                    containers, record.terrain_grid_x, record.terrain_grid_y, char_data
                )
            else:  # dominant
                width, height = record.chunk_pixels_x, record.chunk_pixels_y
                grid = mg.stitch_dominant_entries(
                    reader,
                    record,
                    overridden.get(record.slot),
                    cache=chunk_cache,
                    entries_by_cell=authored_planes.get(record.slot),
                )
                pixels, _w, _h = _bg.render_entry_words(
                    char_data,
                    grid,
                    map_width_tiles=record.chunk_tiles_x,
                    map_height_tiles=record.chunk_tiles_y,
                    color_256=True,
                )
            rendered.append(
                MapBrowserLayer(record.slot, record.classification, record.handler, addend, width, height, pixels)
            )
        except _ACCEPTED_ERRORS as exc:
            raise MapBrowserError(
                f"map:{map_index:04d} layer slot {record.slot} did not render: {exc}"
            ) from exc

    graphical = tuple(layer for layer in rendered if layer.graphical)
    palette = mg.decode_bg_palette(reader)
    if not graphical:
        return MapBrowserResult(
            index=map_index,
            name=_resolve_name(reader, entry.text_index),
            width=0,
            height=0,
            layers=tuple(rendered),
            composite=b"",
            palette=palette,
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
        name=_resolve_name(reader, entry.text_index),
        width=width,
        height=height,
        layers=tuple(rendered),
        composite=composite,
        palette=palette,
        warnings=tuple(warnings),
    )


def render_chunk_images(
    rom: bytes | bytearray | mg.MapGraphicsReader,
    map_index: int,
    addresses: Iterable[int],
    *,
    profile: RomProfile | None = None,
    char_data: bytes | None = None,
) -> tuple[ChunkImage, ...]:
    """Render chunks of one map's character block as 256x256 index images.

    A chunk stores 32x32 tile *ordinals*, which only mean anything resolved
    through the assembled character block of the map that uses them, so the map
    identity is part of the call. This is what a chunk chooser displays; the
    pointers come from the layer the caller is editing.

    ``char_data`` is this map's already-assembled character block, exactly as
    :func:`render_map` takes it, so a chooser refill does not re-decode a block the
    caller already holds.
    """
    reader = reader_for(rom, profile)
    _check_map_index(reader, map_index)
    _verify_supported_rom(reader)
    try:
        entry = mg.read_map_entries(reader)[map_index]
        if char_data is None:
            block, _stream, _animated = mg.assemble_map_char_block(
                reader, entry.root_address
            )
            char_data = block.data
        elif not isinstance(char_data, bytes) or not char_data:
            raise MapBrowserError("char_data must be this map's assembled character block")
        images: list[ChunkImage] = []
        for address in addresses:
            if type(address) is not int or address == 0:
                raise MapBrowserError("a chunk image requires a non-null chunk pointer")
            entries = mg.dominant_chunk_words(reader, address)
            pixels, _w, _h = _bg.render_entry_words(
                char_data,
                entries,
                map_width_tiles=mg.CHUNK_SIDE_TILES,
                map_height_tiles=mg.CHUNK_SIDE_TILES,
                color_256=True,
            )
            images.append(
                ChunkImage(
                    address=address,
                    width=mg.CHUNK_PIXELS,
                    height=mg.CHUNK_PIXELS,
                    pixels=pixels,
                )
            )
    except _ACCEPTED_ERRORS as exc:
        raise MapBrowserError(
            f"map:{map_index:04d} chunks could not be rendered: {exc}"
        ) from exc
    return tuple(images)


def render_chunk_entries(
    char_data: bytes,
    entries: object,
    *,
    width: int = mg.CHUNK_PIXELS,
    height: int = mg.CHUNK_PIXELS,
) -> ChunkImage:
    """Render a 32x32 screen-entry plane through a map's character block.

    MAP-CHUNK-AUTHORING-001. :func:`render_chunk_images` renders chunks that
    already exist, by address; this renders a plane the caller holds, which is what
    a chunk *editor* needs: the author's in-progress plane has no container and no
    address until a build writes one.

    ``width``/``height`` exist so the same entry vocabulary can be drawn at one
    tile per pixel as a compact tile picker - the shape a chooser needs when it has
    to show every entry of a layer's vocabulary at once - rather than only at the
    full 256x256 an author edits.
    """
    if not isinstance(char_data, bytes) or not char_data:
        raise MapBrowserError("a chunk render requires the map's character block")
    plane = tuple(entries)
    if len(plane) != mg.CHUNK_ENTRY_COUNT:
        raise MapBrowserError(
            f"a chunk plane holds {mg.CHUNK_ENTRY_COUNT} screen entries, "
            f"not {len(plane)}"
        )
    for index, value in enumerate(plane):
        if type(value) is not int or not 0 <= value <= 0xFFFF:
            raise MapBrowserError(
                f"chunk entry {index} is {value!r}, which is not a 16-bit screen entry"
            )
    if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
        raise MapBrowserError("a chunk render needs positive pixel dimensions")
    pixels, _w, _h = _bg.render_entry_words(
        char_data,
        plane,
        map_width_tiles=mg.CHUNK_SIDE_TILES,
        map_height_tiles=mg.CHUNK_SIDE_TILES,
        color_256=True,
    )
    if width != mg.CHUNK_PIXELS or height != mg.CHUNK_PIXELS:
        pixels = _scale_nearest(pixels, mg.CHUNK_PIXELS, mg.CHUNK_PIXELS, width, height)
    return ChunkImage(
        address=0, width=width, height=height, pixels=pixels
    )


def _scale_nearest(
    pixels: bytes, src_width: int, src_height: int, dst_width: int, dst_height: int
) -> bytes:
    """Nearest-neighbour down/up-scale of one 8bpp index plane.

    Nearest neighbour on purpose: a palette index is not a colour, so blending two
    of them would invent an index that means a third colour. A preview that has to
    shrink must drop samples, never average them.
    """
    out = bytearray(dst_width * dst_height)
    for y in range(dst_height):
        sy = min(src_height - 1, y * src_height // dst_height)
        row = sy * src_width
        base = y * dst_width
        for x in range(dst_width):
            out[base + x] = pixels[row + min(src_width - 1, x * src_width // dst_width)]
    return bytes(out)


def render_terrain_field(
    containers: tuple[bytes, ...],
    grid_x: int,
    grid_y: int,
    char_data: bytes,
) -> tuple[int, int, bytes]:
    """Render a terrain field's containers to an image, 8x8 pixels per ordinal.

    The plane's layout is the map/format reader's; each ordinal is masked to
    :data:`map_graphics.TERRAIN_FIELD_TILE_ORDINAL_MASK` and selects one 8x8 tile
    from ``char_data`` - the owning map's assembled character block, the same
    block the dominant and screen-entry layers resolve against. The image is
    therefore ``32 * grid_x * 8`` by ``32 * grid_y * 8`` pixels, written with no
    scaling, no padding and no interleaving.
    """
    width, height, plane = mg.stitch_terrain_field_plane(containers, grid_x, grid_y)
    tile = mg.TILE_PIXELS * mg.TILE_PIXELS
    image_width = width * mg.TILE_PIXELS
    image_height = height * mg.TILE_PIXELS
    out = bytearray(image_width * image_height)
    mask = mg.TERRAIN_FIELD_TILE_ORDINAL_MASK
    for row in range(height):
        for column in range(width):
            ordinal = plane[row * width + column] & mask
            start = ordinal * tile
            block = char_data[start : start + tile]
            if len(block) != tile:
                raise MapBrowserError(
                    f"terrain-field ordinal {ordinal} at ({column}, {row}) is "
                    f"outside the {len(char_data) // tile}-tile character block"
                )
            for y in range(mg.TILE_PIXELS):
                target = (row * mg.TILE_PIXELS + y) * image_width + (
                    column * mg.TILE_PIXELS
                )
                out[target : target + mg.TILE_PIXELS] = block[
                    y * mg.TILE_PIXELS : (y + 1) * mg.TILE_PIXELS
                ]
    return image_width, image_height, bytes(out)


def compose(
    visible: tuple[MapLayerView, ...], width: int, height: int
) -> bytes:
    """Compose the given layers onto one indexed canvas by the accepted order.

    ``(addend, slot)`` decides the order: lower addend draws on top, and a lower
    BG number wins a tie, so composition runs in descending order and each
    non-zero pixel overwrites. Index 0 is transparent and never overwrites. A
    layer smaller than the canvas is placed at the canvas origin: the accepted
    model has no layer X/Y offset.
    """
    for layer in visible:
        if len(layer.pixels) != layer.width * layer.height:
            raise MapBrowserError(
                f"a layer declares {layer.width}x{layer.height} but holds "
                f"{len(layer.pixels)} pixels"
            )
        if layer.width > width or layer.height > height:
            raise MapBrowserError(
                f"a {layer.width}x{layer.height} layer does not fit the "
                f"{width}x{height} canvas"
            )
    composite = bytearray(width * height)
    for layer in sorted(
        visible, key=lambda item: (item.addend, item.slot), reverse=True
    ):
        for row in range(layer.height):
            target = row * width
            start = row * layer.width
            for column in range(layer.width):
                value = layer.pixels[start + column]
                if value:
                    composite[target + column] = value
    return bytes(composite)


def rgba_table(palette: tuple[tuple[int, int, int], ...]) -> bytes:
    """A 256-entry index -> RGBA lookup table with index 0 transparent."""
    if len(palette) != 256:
        raise MapBrowserError(f"palette must hold 256 entries, got {len(palette)}")
    table = bytearray(256 * 4)
    for index, (red, green, blue) in enumerate(palette):
        base = index * 4
        table[base] = red
        table[base + 1] = green
        table[base + 2] = blue
        table[base + 3] = 0 if index == 0 else 255
    return bytes(table)


def to_rgba(
    indices: bytes, table: bytes, *, backdrop: tuple[int, int, int] | None = None
) -> bytes:
    """Expand 8bpp palette indices to RGBA using a 256-entry lookup table.

    With ``backdrop`` the image is flattened as the display would show it: an
    index-0 pixel becomes the backdrop colour at full alpha instead of a hole. On
    this hardware the backdrop is palette entry 0 of the background palette, and
    it is what the display shows wherever no layer painted - so a flattened
    composite is the faithful view of the screen, while the per-layer images stay
    transparent so a consumer can still composite them itself.
    """
    import array

    if len(table) != 256 * 4:
        raise MapBrowserError("colour table must be 256 RGBA entries")
    for value in set(indices):
        if value >= 256:
            raise MapBrowserError(f"pixel index {value} is outside the 256-entry palette")
    count = len(indices)
    red = table[0::4]
    green = table[1::4]
    blue = table[2::4]
    alpha = table[3::4]
    if backdrop is not None:
        for channel in backdrop:
            if type(channel) is not int or not 0 <= channel <= 255:
                raise MapBrowserError(f"backdrop channel {channel!r} is not 8-bit")
        red = bytes([backdrop[0]]) + red[1:]
        green = bytes([backdrop[1]]) + green[1:]
        blue = bytes([backdrop[2]]) + blue[1:]
        alpha = b"\xff" + alpha[1:]
    buffer = array.array("B", bytes(count * 4))
    buffer[0::4] = array.array("B", indices.translate(red))
    buffer[1::4] = array.array("B", indices.translate(green))
    buffer[2::4] = array.array("B", indices.translate(blue))
    buffer[3::4] = array.array("B", indices.translate(alpha))
    return buffer.tobytes()


def rgba(
    indices: bytes, palette: tuple[tuple[int, int, int], ...]
) -> bytes:
    """Expand 8bpp palette indices to RGBA with index 0 transparent."""
    return to_rgba(indices, rgba_table(palette))
