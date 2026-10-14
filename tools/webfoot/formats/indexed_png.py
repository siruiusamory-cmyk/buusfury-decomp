
from __future__ import annotations

import struct
import zlib


class PngError(ValueError):
    """Raised when a PNG is missing, malformed, or not the indexed form."""


_MAGIC = b"\x89PNG\r\n\x1a\n"

_COLOUR_TYPE_INDEXED = 3

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
        raw.append(0)
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
        alpha = bytearray(b"\xff" * (transparent_index + 1))
        alpha[transparent_index] = 0
        out += _chunk(b"tRNS", bytes(alpha))
    out += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += _chunk(b"IEND", b"")
    return bytes(out)


def _read_chunks(data: bytes) -> dict[bytes, bytes]:
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
    header = chunks.get(b"IHDR")
    if header is None:
        raise PngError("PNG has no IHDR")
    try:
        return struct.unpack(">IIBBBBB", header[:13])
    except struct.error as exc:
        raise PngError(f"PNG header is malformed: {exc}") from exc


def _inflate(chunks: dict[bytes, bytes]) -> bytes:
    try:
        return zlib.decompress(chunks.get(b"IDAT", b""))
    except zlib.error as exc:
        raise PngError(
            f"PNG image data is not a readable deflate stream: {exc}"
        ) from exc


def _unfilter(raw: bytes, width: int, height: int, channels: int) -> bytes:
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
        if filter_type == 1:
            for x in range(channels, stride):
                line[x] = (line[x] + line[x - channels]) & 0xFF
        elif filter_type == 2:
            for x in range(stride):
                line[x] = (line[x] + previous[x]) & 0xFF
        elif filter_type == 3:
            for x in range(stride):
                left = line[x - channels] if x >= channels else 0
                line[x] = (line[x] + ((left + previous[x]) >> 1)) & 0xFF
        elif filter_type == 4:
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
