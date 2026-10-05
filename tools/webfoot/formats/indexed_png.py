"""Indexed PNG: the editable representation that preserves palette indices.

TOOLKIT-010. A minimal colour-type-3 PNG reader and writer, pure over ``bytes``.

**Why indexed and not RGBA.** The canonical asset is a grid of *palette indices*,
and the index is the identity: two entries of the ROM palette may hold the same
colour, and a pixel that means "index 7" is not interchangeable with one that
means "index 200" even when both render identically. Exporting RGBA would throw
that away and force a colour-match on import, which is a quantiser - lossy by
construction, and unable to round-trip. So the export carries PLTE, and the
pixel bytes stay exactly the bytes the ROM holds. The PNG 1.2 specification
gives colour type 3 a ``tRNS`` chunk of one alpha byte per palette entry
starting at index 0, which is precisely the shape this family's transparency
needs.

**Why hand-rolled.** Pillow is not a dependency of this project and adding an
imaging library to write one chunk type is not worth the install surface. This
codec is deliberately narrow and must never leave the indexed domain.

**Round-trip contract.** ``decode(encode(pixels, palette)) == (pixels, palette)``
for every image this project exports. Filtering is fixed at type 0 (None) on
every scanline: filters exist to help compressors on photographic data, they
change nothing about the decoded result, and a single filter keeps the writer
deterministic - the same asset always produces the same file bytes, which is
what makes a project directory diffable and a rebuild reproducible.
"""

from __future__ import annotations

import struct
import zlib


class PngError(ValueError):
    """Raised when a PNG is missing, malformed, or not the indexed form."""


_MAGIC = b"\x89PNG\r\n\x1a\n"

#: Colour type 3 is "each pixel is a palette index". The only type written here.
_COLOUR_TYPE_INDEXED = 3

#: Eight bits per pixel, so one index per byte and up to 256 palette entries.
_BIT_DEPTH = 8


def _chunk(kind: bytes, body: bytes) -> bytes:
    return (
        struct.pack(">I", len(body))
        + kind
        + body
        + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    )


def encode(
    pixels: bytes,
    width: int,
    height: int,
    palette_rgb: tuple[tuple[int, int, int], ...],
    *,
    transparent_index: int | None = None,
) -> bytes:
    """Write an 8-bit indexed PNG.

    ``palette_rgb`` is written in full and in order. It is never sorted,
    deduplicated, or trimmed to the colours actually used: entry order is what
    every pixel byte refers to, so reordering it would silently recolour the
    image and trimming it would break the next edit that reaches for an unused
    index.
    """
    if width <= 0 or height <= 0:
        raise PngError(f"dimensions must be positive, got {width}x{height}")
    if len(pixels) != width * height:
        raise PngError(
            f"{width}x{height} needs {width * height} pixels, got {len(pixels)}"
        )
    if not 1 <= len(palette_rgb) <= 256:
        raise PngError(f"palette must hold 1..256 entries, got {len(palette_rgb)}")
    highest = max(pixels) if pixels else 0
    if highest >= len(palette_rgb):
        raise PngError(
            f"pixel index {highest} has no entry in a {len(palette_rgb)}-colour palette"
        )

    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0 (None), always
        raw += pixels[y * width : (y + 1) * width]

    plte = bytearray()
    for red, green, blue in palette_rgb:
        for channel in (red, green, blue):
            if not 0 <= channel <= 255:
                raise PngError(f"palette channel {channel} is outside 0..255")
        plte += bytes((red, green, blue))

    out = bytearray(_MAGIC)
    out += _chunk(
        b"IHDR",
        struct.pack(
            ">IIBBBBB", width, height, _BIT_DEPTH, _COLOUR_TYPE_INDEXED, 0, 0, 0
        ),
    )
    out += _chunk(b"PLTE", bytes(plte))
    if transparent_index is not None:
        if not 0 <= transparent_index < len(palette_rgb):
            raise PngError(f"transparent index {transparent_index} is outside the palette")
        # tRNS is a prefix: entries beyond its length are opaque. Writing just
        # enough bytes to reach the transparent entry keeps the file small
        # without making any claim about the entries after it.
        alpha = bytearray(b"\xff" * (transparent_index + 1))
        alpha[transparent_index] = 0
        out += _chunk(b"tRNS", bytes(alpha))
    out += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += _chunk(b"IEND", b"")
    return bytes(out)


#: The chunk framing and the deflate stream are the same for every PNG, so the
#: two readers in this package share these helpers and differ only in what a
#: pixel is: an index into PLTE here, a colour triple there. They are private
#: because neither is a decoder on its own; ``decode`` and
#: :func:`tools.webfoot.formats.rgb_png.decode_truecolour` are the entry points.
def _read_chunks(data: bytes) -> dict[bytes, bytes]:
    """Every chunk body, concatenated per chunk type, in file order."""
    if not data.startswith(_MAGIC):
        raise PngError("not a PNG")
    chunks: dict[bytes, bytearray] = {}
    position = len(_MAGIC)
    while position + 8 <= len(data):
        length = struct.unpack_from(">I", data, position)[0]
        kind = data[position + 4 : position + 8]
        body = data[position + 8 : position + 8 + length]
        if len(body) != length:
            raise PngError(f"chunk {kind!r} is truncated")
        chunks.setdefault(kind, bytearray()).extend(body)
        if kind == b"IEND":
            break
        position += 12 + length
    return {kind: bytes(body) for kind, body in chunks.items()}


def _read_header(chunks: dict[bytes, bytes]) -> tuple[int, ...]:
    """The IHDR fields, or a refusal naming what is missing."""
    header = chunks.get(b"IHDR")
    if header is None:
        raise PngError("PNG has no IHDR")
    try:
        return struct.unpack(">IIBBBBB", header[:13])
    except struct.error as exc:
        raise PngError(f"PNG header is malformed: {exc}") from exc


def _inflate(chunks: dict[bytes, bytes]) -> bytes:
    """The image data, refusing a deflate stream that cannot be read."""
    try:
        return zlib.decompress(chunks.get(b"IDAT", b""))
    except zlib.error as exc:
        raise PngError(
            f"PNG image data is not a readable deflate stream: {exc}"
        ) from exc


def _unfilter(raw: bytes, width: int, height: int, channels: int) -> bytes:
    """Reverse every scanline filter, for pixels ``channels`` bytes wide.

    All five filter types are supported, because an image editor that round-trips
    one of these files will very likely re-filter it.
    """
    stride = width * channels
    expected = (stride + 1) * height
    if len(raw) != expected:
        raise PngError(f"PNG image data is {len(raw)} bytes, expected {expected}")

    pixels = bytearray(width * channels * height)
    previous = bytearray(stride)
    source = 0
    for y in range(height):
        filter_type = raw[source]
        source += 1
        line = bytearray(raw[source : source + stride])
        source += stride
        if filter_type == 1:  # Sub
            for x in range(channels, stride):
                line[x] = (line[x] + line[x - channels]) & 0xFF
        elif filter_type == 2:  # Up
            for x in range(stride):
                line[x] = (line[x] + previous[x]) & 0xFF
        elif filter_type == 3:  # Average
            for x in range(stride):
                left = line[x - channels] if x >= channels else 0
                line[x] = (line[x] + ((left + previous[x]) >> 1)) & 0xFF
        elif filter_type == 4:  # Paeth
            for x in range(stride):
                left = line[x - channels] if x >= channels else 0
                up = previous[x]
                upper_left = previous[x - channels] if x >= channels else 0
                estimate = left + up - upper_left
                da, db, dc = (
                    abs(estimate - left),
                    abs(estimate - up),
                    abs(estimate - upper_left),
                )
                if da <= db and da <= dc:
                    predictor = left
                elif db <= dc:
                    predictor = up
                else:
                    predictor = upper_left
                line[x] = (line[x] + predictor) & 0xFF
        elif filter_type != 0:
            raise PngError(f"unknown PNG filter type {filter_type}")
        pixels[y * stride : (y + 1) * stride] = line
        previous = line
    return bytes(pixels)


def decode(data: bytes) -> tuple[bytes, int, int, tuple[tuple[int, int, int], ...], int | None]:
    """Read an 8-bit indexed PNG.

    Returns ``(pixels, width, height, palette_rgb, transparent_index)``. Anything
    that is not 8-bit, non-interlaced, colour type 3 is refused by name rather
    than converted: a caller who hands this an RGBA file has lost the index
    identity somewhere upstream, and quietly re-quantising would hide that.
    """
    chunks = _read_chunks(data)
    width, height, depth, colour_type, compression, filter_method, interlace = (
        _read_header(chunks)
    )
    palette = chunks.get(b"PLTE", b"")
    transparency = chunks.get(b"tRNS", b"")
    if depth != _BIT_DEPTH or colour_type != _COLOUR_TYPE_INDEXED:
        raise PngError(
            f"expected an 8-bit indexed PNG, got depth {depth} colour type {colour_type}"
        )
    if compression != 0 or filter_method != 0:
        raise PngError("PNG uses a non-standard compression or filter method")
    if interlace:
        raise PngError("interlaced PNG is not supported")
    if not palette or len(palette) % 3:
        raise PngError("indexed PNG needs a PLTE chunk of whole RGB triples")
    if width == 0 or height == 0:
        raise PngError("PNG dimensions must be positive")

    raw = _inflate(chunks)
    pixels = _unfilter(raw, width, height, 1)

    colours = tuple(
        (palette[i * 3], palette[i * 3 + 1], palette[i * 3 + 2])
        for i in range(len(palette) // 3)
    )
    transparent_index = None
    for index, alpha in enumerate(transparency):
        if alpha == 0:
            transparent_index = index
            break
    return bytes(pixels), width, height, colours, transparent_index
