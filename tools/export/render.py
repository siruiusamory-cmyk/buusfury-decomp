"""Pixel assembly for the resource exporter.

ASSET-EXPORT-001. Pure functions over ``bytes``: no filesystem, no addresses.
Everything here works in linear 8bpp palette indices and converts to RGBA only
at the last step.

**Transparency is index 0.** The accepted reading is that a zero palette index
is transparent: it is the platform norm for OBJ pixels, and the accepted map
renderer composes layers with exactly that rule. The exporter therefore writes
alpha 0 wherever the index is 0 and alpha 255 everywhere else. No checkerboard,
no background fill and no padding colour is ever written into an artifact.

**GBA tiling.** Graphics payloads are stored one 8x8 tile at a time, left to
right then top to bottom. :func:`unswizzle_tiles` is the only function here that
knows it; everything above it works in linear pixel order.

**Scaling.** There is none. Every function writes one source pixel to one
destination pixel, so output dimensions are the native dimensions of the
accepted structure.
"""

from __future__ import annotations

from . import canonical as canon

#: One RGBA quadruple per palette index, as a flat lookup table.
_RGBA_TABLE_SIZE = 256


class RenderError(ValueError):
    """Raised when an image cannot be assembled from the accepted structure."""


def object_palette_rgb(rom: "canon.Rom") -> tuple[tuple[int, int, int], ...]:
    """The 256-entry object palette at the profile-declared address.

    Entries are little-endian BGR555 words expanded to 8 bits per channel with
    the high bits replicated into the low ones (`v << 3 | v >> 2`), so 31 maps to
    255 rather than 248.
    """
    offset = rom.span(rom.object_palette_address(), canon.OBJECT_PALETTE_BYTES)
    words = rom.data[offset : offset + canon.OBJECT_PALETTE_BYTES]
    out: list[tuple[int, int, int]] = []
    for index in range(canon.OBJECT_PALETTE_ENTRIES):
        word = words[index * 2] | (words[index * 2 + 1] << 8)
        out.append(_expand_bgr555(word))
    return tuple(out)


def _expand_bgr555(word: int) -> tuple[int, int, int]:
    def expand(part: int) -> int:
        return (part << 3) | (part >> 2)

    return (
        expand(word & 31),
        expand((word >> 5) & 31),
        expand((word >> 10) & 31),
    )


def bg_palette_rgb(rom: "canon.Rom") -> tuple[tuple[int, int, int], ...]:
    """The engine-global 256-entry background palette from ROM `0x080701B0`.

    Stored as RGB888 but the hardware keeps 5 bits per channel, so each channel
    is requantised to 5 bits and expanded back. That reproduces the live VRAM
    palette at full brightness rather than the raw ROM bytes.
    """
    offset = rom.span(rom.bg_palette_address(), canon.BG_PALETTE_BYTES)
    raw = rom.data[offset : offset + canon.BG_PALETTE_BYTES]

    def display(byte: int) -> int:
        five = byte >> 3
        return (five << 3) | (five >> 2)

    return tuple(
        (
            display(raw[index * 3]),
            display(raw[index * 3 + 1]),
            display(raw[index * 3 + 2]),
        )
        for index in range(canon.BG_PALETTE_ENTRIES)
    )


def rgba_table(palette: tuple[tuple[int, int, int], ...]) -> bytes:
    """A 256-entry index -> RGBA lookup table with index 0 transparent."""
    if len(palette) != _RGBA_TABLE_SIZE:
        raise RenderError(f"palette must hold 256 entries, got {len(palette)}")
    table = bytearray(_RGBA_TABLE_SIZE * 4)
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
    index-0 pixel becomes the backdrop colour at full alpha instead of a hole.
    On this hardware the backdrop is palette entry 0 of the background palette,
    and it is what the display shows wherever no layer painted - so a flattened
    composite is the faithful view of the screen, while the per-layer images stay
    transparent so a consumer can still composite them itself.

    Slice assignment on an ``array`` performs the interleave at C speed, which is
    what keeps a quarter of a million pixels per chunk affordable.
    """
    import array

    if len(table) != _RGBA_TABLE_SIZE * 4:
        raise RenderError("colour table must be 256 RGBA entries")
    for value in set(indices):
        if value >= _RGBA_TABLE_SIZE:
            raise RenderError(f"pixel index {value} is outside the 256-entry palette")
    count = len(indices)
    red = table[0::4]
    green = table[1::4]
    blue = table[2::4]
    alpha = table[3::4]
    if backdrop is not None:
        for channel in backdrop:
            if type(channel) is not int or not 0 <= channel <= 255:
                raise RenderError(f"backdrop channel {channel!r} is not 8-bit")
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


def unswizzle_tiles(tiles: bytes, width: int, height: int, *, colour_256: bool) -> bytes:
    """Tiled 8x8 blocks -> a linear ``width * height`` block of palette indices."""
    if width <= 0 or height <= 0:
        raise RenderError(f"dimensions must be positive, got {width}x{height}")
    if width % canon.TILE_PIXELS or height % canon.TILE_PIXELS:
        raise RenderError(f"dimensions must be whole tiles, got {width}x{height}")
    expected = width * height if colour_256 else (width * height) // 2
    if len(tiles) != expected:
        raise RenderError(
            f"{width}x{height} at {8 if colour_256 else 4}bpp needs {expected} "
            f"bytes of tile data, got {len(tiles)}"
        )
    out = bytearray(width * height)
    source = 0
    for tile_y in range(0, height, canon.TILE_PIXELS):
        for tile_x in range(0, width, canon.TILE_PIXELS):
            for row in range(canon.TILE_PIXELS):
                start = (tile_y + row) * width + tile_x
                if colour_256:
                    out[start : start + canon.TILE_PIXELS] = tiles[
                        source : source + canon.TILE_PIXELS
                    ]
                    source += canon.TILE_PIXELS
                else:
                    for column in range(0, canon.TILE_PIXELS, 2):
                        packed = tiles[source]
                        source += 1
                        out[start + column] = packed & 0x0F
                        out[start + column + 1] = packed >> 4
    return bytes(out)


def flip_horizontal(indices: bytes, width: int, height: int) -> bytes:
    """Mirror a linear index image left to right."""
    if len(indices) != width * height:
        raise RenderError(
            f"{width}x{height} needs {width * height} pixels, got {len(indices)}"
        )
    out = bytearray(len(indices))
    for row in range(height):
        start = row * width
        out[start : start + width] = indices[start : start + width][::-1]
    return bytes(out)


def flip_vertical(indices: bytes, width: int, height: int) -> bytes:
    """Mirror a linear index image top to bottom."""
    if len(indices) != width * height:
        raise RenderError(
            f"{width}x{height} needs {width * height} pixels, got {len(indices)}"
        )
    out = bytearray(len(indices))
    for row in range(height):
        start = row * width
        source = (height - 1 - row) * width
        out[start : start + width] = indices[source : source + width]
    return bytes(out)


def blank(width: int, height: int) -> bytes:
    """A fully transparent index image."""
    if width <= 0 or height <= 0:
        raise RenderError(f"dimensions must be positive, got {width}x{height}")
    return bytes(width * height)


def blit_masked(
    canvas: bytearray,
    canvas_width: int,
    canvas_height: int,
    source: bytes,
    source_width: int,
    source_height: int,
    at_x: int,
    at_y: int,
) -> None:
    """Copy only the non-zero (opaque) pixels of a source onto a canvas.

    A source that does not fit the canvas is refused rather than clipped, because
    a piece that does not fit its frame's own bounding box means the assembly
    model is wrong and should be seen rather than silently cropped.
    """
    if (
        at_x < 0
        or at_y < 0
        or at_x + source_width > canvas_width
        or at_y + source_height > canvas_height
    ):
        raise RenderError(
            f"a {source_width}x{source_height} image at ({at_x}, {at_y}) does not "
            f"fit the {canvas_width}x{canvas_height} canvas"
        )
    for row in range(source_height):
        target = (at_y + row) * canvas_width + at_x
        start = row * source_width
        for column in range(source_width):
            value = source[start + column]
            if value:
                canvas[target + column] = value


def flip_tile(tile: bytes, horizontal: bool, vertical: bool) -> bytes:
    """Apply the horizontal and vertical flip to a linear square tile."""
    if len(tile) != canon.TILE_PIXELS * canon.TILE_PIXELS:
        raise RenderError(
            f"a tile is {canon.TILE_PIXELS * canon.TILE_PIXELS} pixels, "
            f"got {len(tile)}"
        )
    if not horizontal and not vertical:
        return tile
    side = canon.TILE_PIXELS
    rows = [tile[row * side : (row + 1) * side] for row in range(side)]
    if horizontal:
        rows = [row[::-1] for row in rows]
    if vertical:
        rows = rows[::-1]
    return b"".join(rows)


def entry_tile(char_data: bytes, word: int) -> bytes:
    """The 8x8 tile an entry names, with the entry's stored flips applied.

    Only bits 0..9 are read as the ordinal. Bits 10 and 11 are the platform's
    horizontal and vertical flip selectors for a regular tiled background; the
    accepted work marks the *direction* assignment `PARTIALLY CONFIRMED` and
    records that no payload consumer reads them, but the hardware flips the tile
    and the project's own BG renderer does the same, so the exporter applies them
    rather than dropping them. Bits 12..15 are never interpreted.
    """
    ordinal = word & canon.TILE_ENTRY_ORDINAL_MASK
    start = ordinal * canon.BANK_TILE_BYTES
    if start + canon.BANK_TILE_BYTES > len(char_data):
        raise RenderError(
            f"tile ordinal {ordinal} is not present in the assembled "
            f"character block ({len(char_data)} bytes)"
        )
    return flip_tile(
        char_data[start : start + canon.BANK_TILE_BYTES],
        bool(word & canon.TILE_ENTRY_BIT_10),
        bool(word & canon.TILE_ENTRY_BIT_11),
    )


def render_entries(
    entries: tuple[int, ...],
    char_data: bytes,
    width_tiles: int,
    height_tiles: int,
) -> bytes:
    """Render stitched logical screen entries into a linear index image.

    Entries are row-major, ``width_tiles`` columns by ``height_tiles`` rows, which
    is exactly the order a dominant chunk stores its 32x32 grid in - so a chunk is
    this function at 32x32.
    """
    if width_tiles <= 0 or height_tiles <= 0:
        raise RenderError(
            f"dimensions must be positive, got {width_tiles}x{height_tiles}"
        )
    if len(entries) != width_tiles * height_tiles:
        raise RenderError(
            f"expected {width_tiles * height_tiles} screen entries, got {len(entries)}"
        )
    width = width_tiles * canon.TILE_PIXELS
    height = height_tiles * canon.TILE_PIXELS
    out = bytearray(width * height)
    cache: dict[int, bytes] = {}
    for index, word in enumerate(entries):
        tile = cache.get(word)
        if tile is None:
            tile = entry_tile(char_data, word)
            cache[word] = tile
        tile_x = (index % width_tiles) * canon.TILE_PIXELS
        tile_y = (index // width_tiles) * canon.TILE_PIXELS
        for row in range(canon.TILE_PIXELS):
            target = (tile_y + row) * width + tile_x
            out[target : target + canon.TILE_PIXELS] = tile[
                row * canon.TILE_PIXELS : row * canon.TILE_PIXELS + canon.TILE_PIXELS
            ]
    return bytes(out)


def render_chunk(
    entries: tuple[int, ...],
    char_data: bytes,
    canvas_width: int = canon.CHUNK_PIXELS,
    canvas_height: int = canon.CHUNK_PIXELS,
) -> bytes:
    """Render a dominant chunk's 32x32 tile entries into a 256x256 index image."""
    if len(entries) != canon.CHUNK_ENTRY_COUNT:
        raise RenderError(
            f"a chunk holds {canon.CHUNK_ENTRY_COUNT} entries, got {len(entries)}"
        )
    if canvas_width != canon.CHUNK_PIXELS or canvas_height != canon.CHUNK_PIXELS:
        raise RenderError(
            f"a chunk renders at {canon.CHUNK_PIXELS}x{canon.CHUNK_PIXELS}, not "
            f"{canvas_width}x{canvas_height}"
        )
    return render_entries(
        entries, char_data, canon.CHUNK_SIDE_TILES, canon.CHUNK_SIDE_TILES
    )


def assemble_frame(
    frame: "canon.FrameRecord",
    graphics: dict[int, bytes],
    extents: dict[int, tuple[int, int]],
) -> bytes:
    """Assemble a frame's pieces into its own rendered-frame canvas.

    The canvas is exactly the frame record's stored bounding box, and each piece
    is placed at ``piece offset - frame minimum``. The stored bit is applied
    because the engine merges the piece's packed attribute pair into the outgoing
    OAM word under mask `0xFE00FFFF`, which preserves attribute-1 bits 12 and 13
    (the hardware flip bits) and clears only the X coordinate - so the flip
    reaches hardware rather than being a dead stored bit.

    ``graphics`` maps a container address to its unswizzled, unflipped linear
    indices and ``extents`` maps it to that image's ``(width, height)``.
    """
    if frame.width <= 0 or frame.height <= 0:
        raise RenderError(
            f"frame at {frame.address:#010x} has a zero bounding box "
            f"{frame.width}x{frame.height}"
        )
    canvas = bytearray(frame.width * frame.height)
    for piece in frame.pieces:
        pixels = graphics.get(piece.graphics_address)
        extent = extents.get(piece.graphics_address)
        if pixels is None or extent is None:
            raise RenderError(
                f"piece at {piece.address:#010x} names an undecoded graphics "
                f"container {piece.graphics_address:#010x}"
            )
        width, height = extent
        if piece.horizontal_flip:
            pixels = flip_horizontal(pixels, width, height)
        if piece.vertical_flip:
            pixels = flip_vertical(pixels, width, height)
        blit_masked(
            canvas,
            frame.width,
            frame.height,
            pixels,
            width,
            height,
            piece.x - frame.min_x,
            piece.y - frame.min_y,
        )
    return bytes(canvas)


def read_terrain_field_plane(
    containers: tuple[bytes, ...],
    grid_x: int,
    grid_y: int,
) -> tuple[int, int, bytes]:
    """Lay a terrain field's containers out as one plane of tile ordinals.

    ASSET-EXPORT-MAP19-001 recovered this record form from the engine's own code
    and its payload's semantics: the `0x080088BD` constructor streams
    `grid_x * grid_y` containers of ``canon.TERRAIN_FIELD_CELL_BYTES`` decoded
    bytes through a nine-slot resident cache, and each container is a 32x32 plane
    of 8-bit tile ordinals. Container ``y * grid_x + x`` covers the cell at
    ``(x * 32, y * 32)``, so the whole field is ``32 * grid_x`` by ``32 * grid_y``
    ordinals.

    The plane is returned as ``(width, height, ordinals)`` in tile units. It is
    not an image: the ordinals resolve through the owning map's assembled
    character block, which the caller already holds.
    """
    if grid_x <= 0 or grid_y <= 0:
        raise RenderError(
            f"a terrain field needs a positive grid, got {grid_x}x{grid_y}"
        )
    expected = grid_x * grid_y
    if len(containers) != expected:
        raise RenderError(
            f"a {grid_x}x{grid_y} terrain field needs {expected} containers, "
            f"got {len(containers)}"
        )
    cell = canon.TERRAIN_FIELD_CELL_TILES
    row_bytes = canon.TERRAIN_FIELD_CELL_BYTES // cell
    width, height = grid_x * cell, grid_y * cell
    plane = bytearray(width * height)
    for index, data in enumerate(containers):
        if len(data) != canon.TERRAIN_FIELD_CELL_BYTES:
            raise RenderError(
                f"terrain-field container {index} holds {len(data)} bytes, "
                f"expected {canon.TERRAIN_FIELD_CELL_BYTES}"
            )
        at_x = (index % grid_x) * cell
        at_y = (index // grid_x) * cell
        for y in range(cell):
            target = (at_y + y) * width + at_x
            source = y * row_bytes
            plane[target : target + cell] = data[source : source + row_bytes]
    return width, height, bytes(plane)


def render_terrain_field(
    containers: tuple[bytes, ...],
    grid_x: int,
    grid_y: int,
    char_data: bytes,
) -> tuple[int, int, bytes]:
    """Render a terrain field's containers to an image, 8x8 pixels per ordinal.

    The plane's ordinals are masked to ``canon.TERRAIN_FIELD_TILE_ORDINAL_MASK``
    and each selects one 8x8 tile from ``char_data`` - the owning map's assembled
    character block, the same block the dominant and screen-entry layers resolve
    against. The image is therefore ``32 * grid_x * 8`` by ``32 * grid_y * 8``
    pixels, and it is written with no scaling, no padding and no interleaving.
    """
    width, height, plane = read_terrain_field_plane(containers, grid_x, grid_y)
    blocks_x = width
    tile = canon.TILE_PIXELS * canon.TILE_PIXELS
    image_width = width * canon.TILE_PIXELS
    image_height = height * canon.TILE_PIXELS
    out = bytearray(image_width * image_height)
    mask = canon.TERRAIN_FIELD_TILE_ORDINAL_MASK
    for row in range(height):
        for column in range(blocks_x):
            ordinal = plane[row * blocks_x + column] & mask
            start = ordinal * tile
            block = char_data[start : start + tile]
            if len(block) != tile:
                raise RenderError(
                    f"terrain-field ordinal {ordinal} at ({column}, {row}) is "
                    f"outside the {len(char_data) // tile}-tile character block"
                )
            for y in range(canon.TILE_PIXELS):
                target = (row * canon.TILE_PIXELS + y) * image_width + (
                    column * canon.TILE_PIXELS
                )
                out[target : target + canon.TILE_PIXELS] = block[
                    y * canon.TILE_PIXELS : (y + 1) * canon.TILE_PIXELS
                ]
    return image_width, image_height, bytes(out)


def compose_layers(
    layers: tuple[tuple[int, int, int, int, bytes], ...],
    width: int,
    height: int,
) -> bytes:
    """Compose rendered layers onto one canvas by the accepted ordering.

    ``layers`` is ``(addend, bg, layer_width, layer_height, pixels)``. The addend
    is the byte the engine adds to `BGxCNT`; the accepted renderer uses it as a
    draw-order key, and the exporter mirrors that without promoting the byte to a
    semantic name. Lower addend draws on top and a lower BG number wins a tie, so
    composition runs in descending ``(addend, bg)`` order and each non-zero pixel
    overwrites. Index 0 is transparent and never overwrites.

    A layer smaller than the canvas is placed at the canvas origin; the accepted
    model has no layer X/Y offset, and the renderer it is derived from copies each
    layer at its own row stride from the top left.
    """
    for _addend, _bg, layer_width, layer_height, pixels in layers:
        if len(pixels) != layer_width * layer_height:
            raise RenderError(
                f"a layer declares {layer_width}x{layer_height} but holds "
                f"{len(pixels)} pixels"
            )
        if layer_width > width or layer_height > height:
            raise RenderError(
                f"a {layer_width}x{layer_height} layer does not fit the "
                f"{width}x{height} canvas"
            )
    composite = bytearray(width * height)
    for _addend, _bg, layer_width, layer_height, pixels in sorted(
        layers, key=lambda item: (item[0], item[1]), reverse=True
    ):
        for row in range(layer_height):
            target = row * width
            start = row * layer_width
            for column in range(layer_width):
                value = pixels[start + column]
                if value:
                    composite[target + column] = value
    return bytes(composite)


def tile_sheet(
    tiles: tuple[bytes, ...],
    columns: int,
    *,
    tile_pixels: int = canon.TILE_PIXELS,
) -> tuple[int, int, bytes]:
    """Lay 8x8 tiles out in a deterministic grid, padding with transparent cells.

    Rows are filled left to right, top to bottom, and any cell past the last tile
    stays transparent. No scaling and no resampling: a tile occupies exactly
    ``tile_pixels`` square pixels.
    """
    if columns <= 0:
        raise RenderError(f"columns must be positive, got {columns}")
    if not tiles:
        raise RenderError("a sheet needs at least one tile")
    rows = (len(tiles) + columns - 1) // columns
    width = columns * tile_pixels
    height = rows * tile_pixels
    out = bytearray(width * height)
    for index, tile in enumerate(tiles):
        if len(tile) != tile_pixels * tile_pixels:
            raise RenderError(
                f"tile {index} is {len(tile)} bytes, not "
                f"{tile_pixels * tile_pixels}"
            )
        column, row = index % columns, index // columns
        for line in range(tile_pixels):
            target = (row * tile_pixels + line) * width + column * tile_pixels
            out[target : target + tile_pixels] = tile[
                line * tile_pixels : line * tile_pixels + tile_pixels
            ]
    return width, height, bytes(out)


def frame_sheet(
    cells: tuple[tuple[int, int, bytes], ...],
    columns: int,
) -> tuple[int, int, bytes]:
    """Lay assembled frames out in a deterministic grid, transparently padded.

    ``cells`` is ``(width, height, pixels)`` per cell. The cell box is the
    maximum width and height over the cells, so a sheet of mixed-size frames is
    laid out on a regular grid with no rescaling - a smaller cell is placed at
    the box origin and the rest of its cell stays transparent.
    """
    if columns <= 0:
        raise RenderError(f"columns must be positive, got {columns}")
    if not cells:
        raise RenderError("a sheet needs at least one cell")
    cell_width = max(cell[0] for cell in cells)
    cell_height = max(cell[1] for cell in cells)
    rows = (len(cells) + columns - 1) // columns
    width = columns * cell_width
    height = rows * cell_height
    out = bytearray(width * height)
    for index, (cell_w, cell_h, pixels) in enumerate(cells):
        if len(pixels) != cell_w * cell_h:
            raise RenderError(f"cell {index} is not {cell_w}x{cell_h} pixels")
        column, row = index % columns, index // columns
        origin_x = column * cell_width
        origin_y = row * cell_height
        for line in range(cell_h):
            target = (origin_y + line) * width + origin_x
            start = line * cell_w
            out[target : target + cell_w] = pixels[start : start + cell_w]
    return width, height, bytes(out)


def palette_strip(
    palette: tuple[tuple[int, int, int], ...],
) -> tuple[int, int, bytes]:
    """A ``len(palette)`` x 1 opaque strip of the palette's colours.

    The strip is opaque on purpose: it is a view of the palette values, so
    suppressing entry 0 would hide an entry rather than show its colour.
    """
    width = len(palette)
    out = bytearray(width * 4)
    for index, (red, green, blue) in enumerate(palette):
        base = index * 4
        out[base] = red
        out[base + 1] = green
        out[base + 2] = blue
        out[base + 3] = 255
    return width, 1, bytes(out)
