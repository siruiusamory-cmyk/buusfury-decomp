"""Truecolour PNG: the authoring form of a sprite source sheet.

SPRITE-NEW-PROJECT-SURFACE-001. A source sheet is art an author drew, not an
extracted payload: the identity planner assigns object-palette indices from the
colours it finds, so unlike every asset ``indexed_png`` carries there is no index
identity to preserve and no ROM palette the pixels refer to. The two truecolour
forms an image editor writes - colour type 2 (RGB) and colour type 6 (RGBA) - are
therefore the forms this reader accepts, at the same 8-bit, non-interlaced shape
the indexed reader accepts. Everything else is refused by name rather than
converted, so a caller that hands this a 16-bit or interlaced file is told which
fact it lost rather than being handed silently resampled art.

The alpha plane is returned rather than dropped: an author's sheet may encode its
holes in the alpha channel instead of in a chroma key, and only the caller knows
which convention the project declared.
"""

from __future__ import annotations

from .indexed_png import (PngError, _inflate, _read_chunks, _read_header,
                          _unfilter)

#: Colour type 2 is three channels per pixel, colour type 6 is four.
_COLOUR_TYPE_RGB = 2
_COLOUR_TYPE_RGBA = 6

#: Eight bits per channel, the depth the indexed reader also accepts.
_BIT_DEPTH = 8

_CHANNELS = {_COLOUR_TYPE_RGB: 3, _COLOUR_TYPE_RGBA: 4}


def decode_truecolour(data: bytes) -> tuple[bytes, int, int, bytes | None]:
    """Read an 8-bit truecolour PNG.

    Returns ``(rgb, width, height, alpha)``, where ``rgb`` is three bytes per
    pixel in row-major order and ``alpha`` is one byte per pixel for a colour
    type 6 image, or ``None`` for a colour type 2 one. Raises
    :class:`~tools.webfoot.formats.indexed_png.PngError` for anything that is not
    the 8-bit non-interlaced RGB/RGBA form: a truncated chunk, a short header, a
    corrupt or missing deflate stream and a bad scanline length are all refused by
    name, because the alternative is a library error escaping a build boundary
    that promises to report a problem with the file.
    """
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
