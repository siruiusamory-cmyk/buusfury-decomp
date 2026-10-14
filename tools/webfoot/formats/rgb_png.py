
from __future__ import annotations

from .indexed_png import (PngError, _inflate, _read_chunks, _read_header,
                          _unfilter)

_COLOUR_TYPE_RGB = 2
_COLOUR_TYPE_RGBA = 6

_BIT_DEPTH = 8

_CHANNELS = {_COLOUR_TYPE_RGB: 3, _COLOUR_TYPE_RGBA: 4}


def decode_truecolour(data: bytes) -> tuple[bytes, int, int, bytes | None]:
    chunks = _read_chunks(data)
    width, height, depth, colour_type, compression, filter_method, interlace = (
        _read_header(chunks)
    )
    channels = _CHANNELS.get(colour_type)
    if depth != _BIT_DEPTH or channels is None:
        raise PngError(
            f"expected an 8-bit RGB or RGBA PNG, got depth {depth} colour type "
            f"{colour_type}"
        )
    if compression != 0 or filter_method != 0:
        raise PngError("PNG uses a non-standard compression or filter method")
    if interlace:
        raise PngError("interlaced PNG is not supported")
    if width == 0 or height == 0:
        raise PngError("PNG dimensions must be positive")

    pixels = _unfilter(_inflate(chunks), width, height, channels)
    if channels == 3:
        return pixels, width, height, None

    rgb = bytearray(width * height * 3)
    alpha = bytearray(width * height)
    for position in range(width * height):
        start = channels * position
        rgb[3 * position : 3 * position + 3] = pixels[start : start + 3]
        alpha[position] = pixels[start + 3]
    return bytes(rgb), width, height, bytes(alpha)
