"""Portable tests for the indexed PNG codec (TOOLKIT-010).

The property under test throughout is index preservation. An RGBA codec would
pass a "looks the same" check while destroying exactly what makes these files a
canonical authoring representation, so several tests assert on palette *indices*
where an image-diff would be the obvious but wrong thing to check.
"""

from __future__ import annotations

import struct
import zlib

import pytest

from tools.webfoot.formats import indexed_png as ip


def _ramp_palette(count: int = 256) -> tuple[tuple[int, int, int], ...]:
    return tuple((i, (i * 3) % 256, (i * 7) % 256) for i in range(count))


def test_round_trip_preserves_pixels_palette_and_dimensions() -> None:
    palette = _ramp_palette()
    pixels = bytes((i * 13) % 256 for i in range(32 * 16))
    blob = ip.encode(pixels, 32, 16, palette, transparent_index=0)
    got, width, height, colours, transparent = ip.decode(blob)
    assert got == pixels
    assert (width, height) == (32, 16)
    assert colours == palette
    assert transparent == 0


def test_distinct_indices_sharing_one_colour_stay_distinct() -> None:
    """The reason RGBA export is unacceptable, stated as a test."""
    palette = tuple([(9, 9, 9)] * 2 + [(1, 2, 3)] * 254)
    pixels = bytes([0, 1, 0, 1])
    blob = ip.encode(pixels, 2, 2, palette)
    got, _, _, colours, _ = ip.decode(blob)
    assert got == pixels               # indices survive
    assert colours[0] == colours[1]    # even though the colours are identical


def test_palette_order_is_preserved_exactly() -> None:
    """Never sorted, never deduplicated: index order is the identity."""
    palette = tuple([(255, 0, 0), (0, 0, 0), (128, 128, 128)] + [(1, 1, 1)] * 253)
    blob = ip.encode(bytes([2, 1, 0, 2]), 2, 2, palette)
    _, _, _, colours, _ = ip.decode(blob)
    assert colours[:3] == palette[:3]


def test_encoding_is_deterministic() -> None:
    palette = _ramp_palette()
    pixels = bytes((i * 5) % 256 for i in range(64))
    assert ip.encode(pixels, 8, 8, palette) == ip.encode(pixels, 8, 8, palette)


def test_transparency_is_optional_and_absent_by_default() -> None:
    palette = _ramp_palette()
    blob = ip.encode(bytes(4), 2, 2, palette)
    _, _, _, _, transparent = ip.decode(blob)
    assert transparent is None


def test_transparent_index_other_than_zero_survives() -> None:
    palette = _ramp_palette()
    blob = ip.encode(bytes([5]) * 4, 2, 2, palette, transparent_index=5)
    _, _, _, _, transparent = ip.decode(blob)
    assert transparent == 5


def test_declared_colour_type_is_indexed() -> None:
    blob = ip.encode(bytes(4), 2, 2, _ramp_palette())
    # IHDR body begins 8 (magic) + 8 (length+type) in; colour type is its 10th byte.
    ihdr = blob[16:29]
    _, _, depth, colour_type, _, _, _ = struct.unpack(">IIBBBBB", ihdr)
    assert depth == 8
    assert colour_type == 3


def test_pixel_index_with_no_palette_entry_is_refused() -> None:
    with pytest.raises(ip.PngError, match="no entry in a 4-colour palette"):
        ip.encode(bytes([7]), 1, 1, _ramp_palette(4))


def test_pixel_count_must_match_the_dimensions() -> None:
    with pytest.raises(ip.PngError, match="needs 64 pixels"):
        ip.encode(bytes(10), 8, 8, _ramp_palette())


def test_transparent_index_outside_the_palette_is_refused() -> None:
    with pytest.raises(ip.PngError, match="outside the palette"):
        ip.encode(bytes(4), 2, 2, _ramp_palette(4), transparent_index=9)


def test_non_png_input_is_refused() -> None:
    with pytest.raises(ip.PngError, match="not a PNG"):
        ip.decode(b"GIF89a and the rest")


def test_non_indexed_png_is_refused_rather_than_converted() -> None:
    """An RGBA file has already lost the indices; converting would hide that."""
    body = struct.pack(">IIBBBBB", 2, 2, 8, 6, 0, 0, 0)
    blob = (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", len(body))
        + b"IHDR"
        + body
        + struct.pack(">I", zlib.crc32(b"IHDR" + body) & 0xFFFFFFFF)
    )
    with pytest.raises(ip.PngError, match="expected an 8-bit indexed PNG"):
        ip.decode(blob)


def test_indexed_png_without_a_palette_is_refused() -> None:
    body = struct.pack(">IIBBBBB", 1, 1, 8, 3, 0, 0, 0)
    blob = (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", len(body))
        + b"IHDR"
        + body
        + struct.pack(">I", zlib.crc32(b"IHDR" + body) & 0xFFFFFFFF)
    )
    with pytest.raises(ip.PngError, match="needs a PLTE chunk"):
        ip.decode(blob)


@pytest.mark.parametrize("filter_type", [0, 1, 2, 3, 4])
def test_every_png_filter_type_is_read_correctly(filter_type: int) -> None:
    """An editor round-tripping one of our files will re-filter it."""
    palette = _ramp_palette()
    width, height = 8, 4
    pixels = bytes((i * 29) % 256 for i in range(width * height))

    raw = bytearray()
    previous = bytearray(width)
    for y in range(height):
        line = bytearray(pixels[y * width : (y + 1) * width])
        encoded = bytearray(width)
        for x in range(width):
            left = line[x - 1] if x else 0
            up = previous[x]
            upper_left = previous[x - 1] if x else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) >> 1
            else:
                estimate = left + up - upper_left
                da, db, dc = (
                    abs(estimate - left),
                    abs(estimate - up),
                    abs(estimate - upper_left),
                )
                predictor = left if (da <= db and da <= dc) else (up if db <= dc else upper_left)
            encoded[x] = (line[x] - predictor) & 0xFF
        raw.append(filter_type)
        raw += encoded
        previous = line

    def chunk(kind: bytes, body: bytes) -> bytes:
        return (
            struct.pack(">I", len(body))
            + kind
            + body
            + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
        )

    plte = b"".join(bytes(c) for c in palette)
    blob = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0))
        + chunk(b"PLTE", plte)
        + chunk(b"IDAT", zlib.compress(bytes(raw)))
        + chunk(b"IEND", b"")
    )
    got, _, _, _, _ = ip.decode(blob)
    assert got == pixels
