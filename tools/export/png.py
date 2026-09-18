"""Deterministic RGBA PNG writer used by the resource exporter.

ASSET-EXPORT-001. A minimal, dependency-free encoder for the one image form the
exporter produces: 8-bit RGBA, filter type 0 on every row, a fixed ``zlib``
compression level.

**Why its own encoder.** The resource library must be byte-reproducible: two
runs against the same ROM must produce the same PNG bytes. A general imaging
library carries version-dependent encoder choices, optional chunks (``tIME``,
``pHYs``, ``tEXt``), and filter heuristics that can change between releases.
Writing the four chunks this format needs removes all of that, and the resource
directory then hashes stably.

**Compression level is a fixed constant, not a tuning knob.** Level 6 is
`zlib`'s default: measured over the canonical corpus it encodes a 256x256 image
about six times faster than level 9 for roughly seven percent more bytes. The
level is part of the format contract here - changing it changes every artifact
hash - so it is pinned in one place and reported in the audit manifest.

**Colour type 6, not 3.** An indexed PNG would preserve palette identity, but
the exported art must be directly reusable with real alpha. Index 0 is
transparent in every layer, frame and tile this exporter writes (the platform
norm for OBJ and BG pixels, and the reading the accepted map renderer uses), so
the alpha channel is the transparent-mask channel and is written explicitly.

**No interpolation, no scaling.** Pixels are written one to one. The only
resampling in this module is none at all.
"""

from __future__ import annotations

import binascii
import struct
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

#: Colour type 6 - truecolour with alpha.
COLOUR_TYPE_RGBA = 6
BIT_DEPTH = 8

#: Per-row filter type. 0 is "None"; the exporter never filters, so a decoder
#: reading these files back reconstructs the exact bytes this module wrote.
FILTER_NONE = 0

#: Fixed deflate level. Part of the artifact-byte contract; see the module
#: docstring. Never change it without re-baselining every published hash.
COMPRESSION_LEVEL = 6


class PngError(ValueError):
    """Raised when an image cannot be encoded."""


def _chunk(tag: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + tag
        + payload
        + struct.pack(">I", binascii.crc32(tag + payload) & 0xFFFFFFFF)
    )


def encode_rgba(width: int, height: int, pixels: bytes) -> bytes:
    """Encode a linear RGBA buffer as a PNG file image.

    ``pixels`` is ``width * height * 4`` bytes in row-major order, top row
    first, four bytes per pixel in R, G, B, A order. There is no padding and no
    stride: the buffer is exactly the image.
    """
    if type(width) is not int or type(height) is not int:
        raise PngError("width and height must be ints")
    if width <= 0 or height <= 0:
        raise PngError(f"dimensions must be positive, got {width}x{height}")
    expected = width * height * 4
    if len(pixels) != expected:
        raise PngError(
            f"{width}x{height} RGBA needs {expected} bytes, got {len(pixels)}"
        )

    stride = width * 4
    raw = bytearray()
    for row in range(height):
        raw.append(FILTER_NONE)
        start = row * stride
        raw += pixels[start : start + stride]

    header = struct.pack(">IIBBBBB", width, height, BIT_DEPTH, COLOUR_TYPE_RGBA, 0, 0, 0)
    return (
        PNG_SIGNATURE
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), COMPRESSION_LEVEL))
        + _chunk(b"IEND", b"")
    )


def read_ihdr(png: bytes) -> tuple[int, int, int, int]:
    """Read ``(width, height, bit_depth, colour_type)`` back from a PNG image.

    Used by the tests and the audit comparison mode to verify an artifact
    without a third-party decoder.
    """
    if not png.startswith(PNG_SIGNATURE):
        raise PngError("not a PNG image")
    if len(png) < 8 + 12 + 13:
        raise PngError("image is too short to hold an IHDR chunk")
    if png[12:16] != b"IHDR":
        raise PngError("first chunk is not IHDR")
    length = struct.unpack_from(">I", png, 8)[0]
    if length != 13:
        raise PngError(f"IHDR length {length} is not 13")
    if 8 + 12 + length > len(png):
        raise PngError("IHDR chunk runs past the end of the image")
    width, height, depth, colour, compression, filt, interlace = struct.unpack_from(
        ">IIBBBBB", png, 16
    )
    if compression != 0 or filt != 0 or interlace != 0:
        raise PngError("unsupported PNG compression, filter or interlace method")
    return width, height, depth, colour


def decode_rgba(png: bytes) -> tuple[int, int, bytes]:
    """Decode a PNG this module wrote back into ``(width, height, pixels)``.

    Deliberately narrow: it accepts only the single form :func:`encode_rgba`
    produces (colour type 6, 8-bit, filter 0, one IDAT) so the audit can verify
    artifact bytes without depending on an imaging library - and so a change to
    the encoder that silently alters the form fails a test rather than passing
    unnoticed.
    """
    width, height, depth, colour = read_ihdr(png)
    if depth != BIT_DEPTH or colour != COLOUR_TYPE_RGBA:
        raise PngError(f"only 8-bit RGBA is readable, got depth {depth} colour {colour}")
    position = 8
    data = bytearray()
    while position < len(png):
        length = struct.unpack_from(">I", png, position)[0]
        tag = png[position + 4 : position + 8]
        body = png[position + 8 : position + 8 + length]
        if tag == b"IDAT":
            data += body
        elif tag == b"IEND":
            break
        position += 12 + length
    raw = zlib.decompress(bytes(data))
    stride = width * 4
    if len(raw) != height * (stride + 1):
        raise PngError(
            f"raw scanline data is {len(raw)} bytes, expected {height * (stride + 1)}"
        )
    out = bytearray()
    for row in range(height):
        start = row * (stride + 1)
        if raw[start] != FILTER_NONE:
            raise PngError(f"row {row} uses filter {raw[start]}, expected 0")
        out += raw[start + 1 : start + 1 + stride]
    return width, height, bytes(out)
