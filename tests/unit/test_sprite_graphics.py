"""Portable tests for the sprite graphics codec (TOOLKIT-010).

Synthetic fixtures only - no ROM graphics are embedded. The tile fixtures are
built from arithmetic patterns so a swizzle bug shows up as a specific wrong
byte rather than as a vaguely wrong picture.

The frame and piece fixtures pin the **accepted** record layout: an 8-byte frame
header (piece count plus the frame's bounding box) followed by 12-byte pieces at
``frame + 8 + 12 * index``, with the stored pixel extents at piece ``+0x02``/
``+0x03``, the packed OBJ attribute pair at ``+0x04`` and the container word at
``+0x08``. Until EVIDENCE-RISK-DEBT-001 they pinned the refuted 4-byte header and
16-byte stride, which is why they were rewritten rather than deleted: the
correction has to stay pinned, not merely applied.
"""

from __future__ import annotations

import struct

import pytest

from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.formats import webfoot_lz as wl


def _palette(words: dict[int, int] | None = None) -> sg.Palette:
    raw = [0] * sg.PALETTE_ENTRIES
    for index, word in (words or {}).items():
        raw[index] = word
    return sg.Palette(raw=tuple(raw))


# --- palette -----------------------------------------------------------------

def test_palette_round_trips_through_its_exact_source_words() -> None:
    raw = tuple((i * 517) & 0x7FFF for i in range(sg.PALETTE_ENTRIES))
    data = struct.pack(f"<{sg.PALETTE_ENTRIES}H", *raw)
    palette = sg.decode_palette(data, 0)
    assert palette.raw == raw
    assert sg.encode_palette(palette) == data


def test_palette_expansion_maps_full_scale_to_full_white() -> None:
    """31 must become 255, not 248 - a plain shift would grey out white."""
    palette = _palette({1: 0x7FFF, 2: 0x0000})
    assert palette.rgb[1] == (255, 255, 255)
    assert palette.rgb[2] == (0, 0, 0)


def test_palette_channel_order_is_bgr_in_the_word() -> None:
    """Red is the low five bits; getting this backwards swaps every sprite."""
    palette = _palette({1: 0x001F, 2: 0x03E0, 3: 0x7C00})
    assert palette.rgb[1] == (255, 0, 0)
    assert palette.rgb[2] == (0, 255, 0)
    assert palette.rgb[3] == (0, 0, 255)


def test_palette_preserves_duplicate_colours_at_distinct_indices() -> None:
    """Two entries may hold one colour; the index is still the identity."""
    palette = _palette({5: 0x1234, 200: 0x1234})
    assert palette.rgb[5] == palette.rgb[200]
    assert sg.encode_palette(palette)[10:12] == sg.encode_palette(palette)[400:402]


def test_palette_of_the_wrong_length_is_refused() -> None:
    with pytest.raises(sg.SpriteFormatError, match="expected 256"):
        sg.Palette(raw=(0, 1, 2))


def test_palette_outside_the_image_is_refused() -> None:
    with pytest.raises(sg.SpriteFormatError, match="outside the image"):
        sg.decode_palette(b"\x00" * 16, 0)


# --- tiles -------------------------------------------------------------------

@pytest.mark.parametrize(
    "width,height",
    [(8, 8), (16, 16), (32, 32), (64, 64), (16, 8), (8, 16), (32, 64), (64, 32)],
)
def test_tile_swizzle_is_an_exact_inverse_at_8bpp(width: int, height: int) -> None:
    pixels = bytes((i * 7) % 256 for i in range(width * height))
    tiles = sg.swizzle_tiles(pixels, width, height, colour_256=True)
    assert sg.unswizzle_tiles(tiles, width, height, colour_256=True) == pixels


@pytest.mark.parametrize("width,height", [(8, 8), (16, 32), (32, 16)])
def test_tile_swizzle_is_an_exact_inverse_at_4bpp(width: int, height: int) -> None:
    pixels = bytes((i * 5) % 16 for i in range(width * height))
    tiles = sg.swizzle_tiles(pixels, width, height, colour_256=False)
    assert sg.unswizzle_tiles(tiles, width, height, colour_256=False) == pixels


def test_unswizzle_places_the_second_tile_beside_the_first() -> None:
    """The concrete layout claim: tiles run left to right, then top to bottom."""
    first = bytes([1] * 64)
    second = bytes([2] * 64)
    pixels = sg.unswizzle_tiles(first + second, 16, 8, colour_256=True)
    assert pixels[0:8] == bytes([1] * 8)
    assert pixels[8:16] == bytes([2] * 8)


def test_4bpp_packs_the_low_nibble_first() -> None:
    tiles = bytes([0x21] + [0] * 31)
    pixels = sg.unswizzle_tiles(tiles, 8, 8, colour_256=False)
    assert pixels[0] == 1
    assert pixels[1] == 2


def test_tile_byte_count_halves_at_4bpp() -> None:
    assert sg.tile_byte_count(32, 32, colour_256=True) == 1024
    assert sg.tile_byte_count(32, 32, colour_256=False) == 512


def test_wrong_length_tile_data_is_refused() -> None:
    with pytest.raises(sg.SpriteFormatError, match="bytes of tile data"):
        sg.unswizzle_tiles(b"\x00" * 10, 8, 8, colour_256=True)


def test_dimensions_must_be_whole_tiles() -> None:
    with pytest.raises(sg.SpriteFormatError, match="whole tiles"):
        sg.unswizzle_tiles(b"\x00" * 64, 7, 8, colour_256=True)


def test_index_above_the_4bpp_range_is_refused_on_swizzle() -> None:
    pixels = bytes([16] + [0] * 63)
    with pytest.raises(sg.SpriteFormatError, match="exceeds 15"):
        sg.swizzle_tiles(pixels, 8, 8, colour_256=False)


# --- pieces ------------------------------------------------------------------

def _piece_bytes(x: int, y: int, attributes: int, pointer: int,
                 dims: tuple[int, int] = (32, 32)) -> bytes:
    """One 12-byte piece record: x, y, two extents, attributes, container word."""
    return (
        struct.pack("<bbBB", x, y, dims[0], dims[1])
        + struct.pack("<II", attributes, pointer)
    )


def test_piece_decodes_its_attribute_fields() -> None:
    # attribute0 low half: shape 0, 8bpp set. attribute1 high half: size 2.
    attributes = (0x2000) | (0x8000 << 16)
    piece = sg.decode_piece(_piece_bytes(-8, -24, attributes, 0x08123456), 0)
    assert piece.x == -8 and piece.y == -24
    assert piece.shape == 0 and piece.size == 2
    assert piece.dimensions == (32, 32)
    assert piece.colour_256 is True
    assert piece.graphics_pointer == 0x08123456


def test_piece_stored_extents_are_the_bytes_the_engine_reads() -> None:
    """``+0x02``/``+0x03`` are the piece's own pixel extents, not an unknown span.

    The old reader carried them inside a six-byte ``unknown_raw`` field. They are
    stored fields the engine uses - ``+0x02`` is halved to centre the OBJ and the
    pair is multiplied to size the composite buffer - and the attribute decode
    must agree with them, which is what makes the attribute reading evidence.
    """
    attributes = (0x2000) | (0x8000 << 16)          # shape 0, size 2 -> 32x32
    piece = sg.decode_piece(_piece_bytes(1, 2, attributes, 0, dims=(32, 32)), 0)
    assert piece.stored_dimensions == (32, 32)
    assert piece.dimensions == piece.stored_dimensions
    # A record whose stored extents disagree with its attribute word still reads;
    # the disagreement is visible rather than hidden.
    disagreeing = sg.decode_piece(_piece_bytes(1, 2, attributes, 0, dims=(8, 8)), 0)
    assert disagreeing.stored_dimensions == (8, 8)
    assert disagreeing.dimensions == (32, 32)


def test_piece_flip_bits_are_read_from_attribute_one() -> None:
    horizontal = sg.decode_piece(_piece_bytes(0, 0, 0x1000 << 16, 0), 0)
    vertical = sg.decode_piece(_piece_bytes(0, 0, 0x2000 << 16, 0), 0)
    assert horizontal.horizontal_flip and not horizontal.vertical_flip
    assert vertical.vertical_flip and not vertical.horizontal_flip


@pytest.mark.parametrize(
    "piece_bytes",
    [
        _piece_bytes(3, -4, 0x2000, 0x08000100, dims=(16, 16)),
        _piece_bytes(-128, 127, 0x80002000, 0x086A87A8, dims=(64, 64)),
    ],
)
def test_piece_round_trips_all_twelve_bytes(piece_bytes: bytes) -> None:
    """``encode_piece`` is the exact inverse of ``decode_piece``."""
    assert len(piece_bytes) == sg.PIECE_SIZE == 12
    piece = sg.decode_piece(piece_bytes, 0)
    assert sg.encode_piece(piece) == piece_bytes


def test_reserved_oam_shape_is_refused_rather_than_guessed() -> None:
    piece = sg.decode_piece(_piece_bytes(0, 0, 0xC000, 0), 0)
    assert piece.shape == 3
    with pytest.raises(sg.SpriteFormatError, match="reserved OAM shape"):
        _ = piece.dimensions


def test_every_shape_and_size_maps_to_the_gbatek_table() -> None:
    assert sg.OBJECT_DIMENSIONS[0] == ((8, 8), (16, 16), (32, 32), (64, 64))
    assert sg.OBJECT_DIMENSIONS[1] == ((16, 8), (32, 8), (32, 16), (64, 32))
    assert sg.OBJECT_DIMENSIONS[2] == ((8, 16), (8, 32), (16, 32), (32, 64))


# --- frames and animations ---------------------------------------------------

def _frame_bytes(count: int, pieces: list[bytes], bounds=(0, 0, 32, 32)) -> bytes:
    """An 8-byte frame header - count plus the frame's own bounding box - then pieces."""
    return struct.pack("<IbbBB", count, *bounds) + b"".join(pieces)


def test_frame_header_is_eight_bytes_then_pieces_at_a_twelve_byte_stride() -> None:
    body = _frame_bytes(
        2,
        [
            _piece_bytes(0, 0, 0x2000 | (0x8000 << 16), 0x08000100, dims=(32, 32)),
            _piece_bytes(8, 0, 0x2000 | (0x8000 << 16), 0x08000200, dims=(16, 32)),
        ],
        bounds=(0, 0, 32, 32),
    )
    frame = sg.decode_frame(body, 0)
    assert sg.FRAME_HEADER_SIZE == 8 and sg.PIECE_SIZE == 12
    assert frame.piece_count == 2
    assert len(frame.pieces) == 2
    assert frame.pieces[1].x == 8
    assert frame.pieces[1].offset - frame.pieces[0].offset == sg.PIECE_SIZE
    assert frame.header_bounds == (0, 0, 32, 32)
    # The header's box is the union over the pieces: the second piece reaches
    # x = 8 + 16 = 24, so the union stays 32 wide because the first one is 32.
    assert frame.piece_bounds == (0, 0, 32, 32)


def test_the_frame_header_records_the_pieces_bounding_box() -> None:
    """Recorded, not enforced: the corpus agrees, and the four bytes are still fields."""
    body = _frame_bytes(
        1,
        [_piece_bytes(-8, -4, 0x2000 | (0x8000 << 16), 0x08000100, dims=(32, 32))],
        bounds=(-8, -4, 32, 32),
    )
    frame = sg.decode_frame(body, 0)
    assert frame.header_bounds == frame.piece_bounds == (-8, -4, 32, 32)


def test_frame_with_an_absurd_piece_count_is_refused() -> None:
    with pytest.raises(sg.SpriteFormatError, match="declares 999 pieces"):
        sg.decode_frame(struct.pack("<I", 999) + b"\x00" * 64, 0)


def test_frame_running_past_the_image_is_refused() -> None:
    with pytest.raises(sg.SpriteFormatError, match="runs past the image"):
        sg.decode_frame(struct.pack("<I", 4) + b"\x00" * 8, 0)


def test_animation_indexes_direction_slots_major_within_a_frame() -> None:
    pointers = tuple(range(1, 9))
    body = struct.pack("<I", 2) + struct.pack("<8I", *pointers)
    animation = sg.decode_animation(body, 0)
    assert animation.frame_count == 2
    assert animation.pointer_for(0, 0) == 1
    assert animation.pointer_for(0, 3) == 4
    assert animation.pointer_for(1, 0) == 5


def test_animation_rejects_an_out_of_range_slot() -> None:
    body = struct.pack("<I", 1) + struct.pack("<4I", 1, 2, 3, 4)
    animation = sg.decode_animation(body, 0)
    with pytest.raises(sg.SpriteFormatError, match="direction slot"):
        animation.pointer_for(0, 4)
    with pytest.raises(sg.SpriteFormatError, match="frame 5"):
        animation.pointer_for(5, 0)


def test_animation_with_an_absurd_frame_count_is_refused() -> None:
    with pytest.raises(sg.SpriteFormatError, match="declares 500 frames"):
        sg.decode_animation(struct.pack("<I", 500) + b"\x00" * 64, 0)


# --- decoded graphics and the capacity rule ----------------------------------

def _graphic_blob(width: int, height: int, fill: int = 3) -> tuple[bytes, bytes]:
    pixels = bytes([fill]) * (width * height)
    tiles = sg.swizzle_tiles(pixels, width, height, colour_256=True)
    return wl.pack(tiles), pixels


def test_decode_graphic_cross_checks_the_declared_size_against_the_piece() -> None:
    blob, pixels = _graphic_blob(16, 16)
    graphic = sg.decode_graphic(blob, 0, 16, 16, colour_256=True)
    assert graphic.pixels == pixels
    # The same payload claimed as a different shape must be refused, because the
    # container size and the OAM dimensions are independent ROM facts.
    with pytest.raises(sg.SpriteFormatError, match="its piece declares"):
        sg.decode_graphic(blob, 0, 32, 32, colour_256=True)


def test_pixel_index_above_the_depth_is_refused_before_encoding() -> None:
    """A 4bpp graphic cannot address index 16, and the plan refuses by name."""
    pixels = bytes([1]) * 64
    blob = wl.pack(sg.swizzle_tiles(pixels, 8, 8, colour_256=False))
    graphic = sg.decode_graphic(blob, 0, 8, 8, colour_256=False)
    too_high = bytes([16]) + bytes([1]) * 63
    with pytest.raises(sg.SpriteFormatError, match="above the 15"):
        sg.plan_graphic_payload(blob, graphic, too_high)


def test_wrong_pixel_count_is_refused() -> None:
    blob, _ = _graphic_blob(8, 8)
    graphic = sg.decode_graphic(blob, 0, 8, 8, colour_256=True)
    with pytest.raises(sg.SpriteFormatError, match="expected 64 pixels"):
        sg.plan_graphic_payload(blob, graphic, b"\x00" * 10)


def test_payload_that_would_grow_past_its_allocation_is_refused() -> None:
    """The capacity rule: no free space is declared, so growth fails closed."""
    # A flat fill packs tiny; replacing it with incompressible noise cannot fit.
    blob, _ = _graphic_blob(32, 32, fill=0)
    graphic = sg.decode_graphic(blob, 0, 32, 32, colour_256=True)
    noise = bytes((i * 97 + (i * i) % 251) % 256 for i in range(32 * 32))
    with pytest.raises(sg.SpriteFormatError, match="growth is refused"):
        sg.plan_graphic_payload(blob, graphic, noise)


def test_a_payload_that_fits_is_planned_with_its_original_extent() -> None:
    blob, pixels = _graphic_blob(32, 32, fill=7)
    graphic = sg.decode_graphic(blob, 0, 32, 32, colour_256=True)
    plan = sg.plan_graphic_payload(blob, graphic, pixels)
    assert plan.offset == 0
    assert plan.original_size == graphic.packed_size
    assert len(plan.payload) <= plan.original_size
    assert plan.padding >= 0
    # The planned payload must itself decode to the pixels asked for.
    assert sg.unswizzle_tiles(
        wl.unpack(plan.payload, 0).data, 32, 32, colour_256=True
    ) == pixels
