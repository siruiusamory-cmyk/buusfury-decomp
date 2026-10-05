"""SPRITE-NEW-PROJECT-SURFACE-001: the truecolour PNG a source sheet arrives as.

The reader exists because a source sheet is art an author drew, not an extracted
payload: the identity planner assigns object-palette indices from the colours it
finds, so there is no index identity to preserve. What these tests establish is
that the two truecolour forms an image editor writes decode exactly - including
every scanline filter, whose per-pixel arithmetic differs once a pixel is more
than one byte wide - and that everything else is refused by name rather than
converted.
"""

from __future__ import annotations

import struct
import zlib

import pytest

from tests.helpers import write_truecolour_png
from tools.webfoot.formats import indexed_png as ip
from tools.webfoot.formats import rgb_png as rp


def _pixels(width: int, height: int) -> bytes:
    """A small image whose bytes differ from their filter predictors."""
    out = bytearray()
    for y in range(height):
        for x in range(width):
            out += bytes(((17 * x + 3 * y) & 0xFF, (5 * x + 29 * y) & 0xFF,
                          (x * y + 7) & 0xFF))
    return bytes(out)


def _patch_ihdr(data: bytes, *, depth: int | None = None,
                interlace: int | None = None) -> bytes:
    """Rewrite one IHDR field, so a refusal can be attributed to that field."""
    out = bytearray(data)
    at = out.index(b"IHDR") + 4
    if depth is not None:
        out[at + 8] = depth
    if interlace is not None:
        out[at + 12] = interlace
    return bytes(out)


def test_rgb_pixels_decode_exactly(tmp_path):
    rgb = _pixels(5, 3)
    path = write_truecolour_png(tmp_path / "sheet.png", rgb, 5, 3)
    decoded, width, height, alpha = rp.decode_truecolour(path.read_bytes())
    assert (decoded, width, height, alpha) == (rgb, 5, 3, None)


def test_rgba_pixels_keep_their_alpha_plane(tmp_path):
    rgb = _pixels(4, 2)
    alpha = bytes([0, 255, 255, 0, 255, 0, 255, 255])
    path = write_truecolour_png(tmp_path / "sheet.png", rgb, 4, 2, alpha=alpha)
    decoded, width, height, plane = rp.decode_truecolour(path.read_bytes())
    assert (decoded, width, height, plane) == (rgb, 4, 2, alpha)


@pytest.mark.parametrize("filter_type", [1, 2, 3, 4])
def test_every_scanline_filter_is_reversed(tmp_path, filter_type):
    """Sub, Up, Average and Paeth all read back, at four bytes per pixel."""
    rgb = _pixels(6, 4)
    alpha = bytes(range(24))
    path = write_truecolour_png(tmp_path / "sheet.png", rgb, 6, 4, alpha=alpha,
                                filter_type=filter_type)
    decoded, _, _, plane = rp.decode_truecolour(path.read_bytes())
    assert decoded == rgb
    assert plane == alpha


def test_a_truncated_chunk_is_refused():
    data = (b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 100) + b"IDAT" + b"short")
    with pytest.raises(rp.PngError, match="truncated"):
        rp.decode_truecolour(data)


def test_something_that_is_not_a_png_is_refused():
    with pytest.raises(rp.PngError, match="not a PNG"):
        rp.decode_truecolour(b"not a png at all")


def test_an_indexed_png_is_refused_rather_than_quantised():
    """The exported asset form is a different representation, not a source sheet."""
    data = ip.encode(bytes([0, 1, 2, 3]), 2, 2,
                     ((1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)))
    with pytest.raises(rp.PngError, match="expected an 8-bit RGB or RGBA PNG"):
        rp.decode_truecolour(data)


def test_a_sixteen_bit_image_is_refused(tmp_path):
    path = write_truecolour_png(tmp_path / "sheet.png", _pixels(2, 2), 2, 2)
    with pytest.raises(rp.PngError, match="depth 16 colour type 2"):
        rp.decode_truecolour(_patch_ihdr(path.read_bytes(), depth=16))


def test_an_interlaced_image_is_refused(tmp_path):
    path = write_truecolour_png(tmp_path / "sheet.png", _pixels(2, 2), 2, 2)
    with pytest.raises(rp.PngError, match="interlaced"):
        rp.decode_truecolour(_patch_ihdr(path.read_bytes(), interlace=1))


def test_the_indexed_reader_still_reads_its_own_form():
    """The shared chunk and unfilter helpers changed no published behaviour."""
    pixels = bytes([0, 1, 2, 3])
    palette = ((1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12))
    data = ip.encode(pixels, 2, 2, palette, transparent_index=0)
    assert ip.decode(data) == (pixels, 2, 2, palette, 0)


def test_a_hand_built_indexed_png_still_refuses_non_indexed_chunks():
    body = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    chunk = (struct.pack(">I", len(body)) + b"IHDR" + body
             + struct.pack(">I", zlib.crc32(b"IHDR" + body) & 0xFFFFFFFF))
    with pytest.raises(ip.PngError, match="expected an 8-bit indexed PNG"):
        ip.decode(b"\x89PNG\r\n\x1a\n" + chunk)
