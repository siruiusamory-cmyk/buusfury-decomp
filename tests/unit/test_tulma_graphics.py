"""FRIEND-V3-TULMA-GRAPHICS-001: the pure logic of the Tulma graphics writer.

These are the decisions a reviewer must be able to check without a ROM: how a supplied
colour becomes a palette index, how a 32x32 sheet cell becomes a 16x32 donor frame, that
one container named by two cells must receive one art, and that the apply/verify pair
refuses a stale base, an overlap and any byte outside a declared span.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from tools.export.png import encode_rgba
from tools.research import apply_tulma_graphics as tg
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.formats import webfoot_lz as wl

PALETTE_OFFSET = 0x40


def _palette_bytes(entries: dict[int, int]) -> bytes:
    """A 256-entry palette buffer with ``entries`` {index: BGR555 word} placed in it.

    Unstated entries get a distinct non-black colour, so a test meaning "only these
    indices carry black" is not quietly satisfied by the whole buffer being zero.
    """
    out = bytearray(2 * 256)
    for index in range(256):
        word = entries.get(index, (index & 31) | (((index >> 5) & 7) << 5))
        out[2 * index] = word & 0xFF
        out[2 * index + 1] = word >> 8
    return bytes(out)


def _table(entries: dict[int, int]) -> dict[tuple[int, int, int], tuple[int, ...]]:
    data = bytes(PALETTE_OFFSET) + _palette_bytes(entries)
    return tg.palette_indices(data, PALETTE_OFFSET)


def _rgb(width: int, height: int, pixels: list[tuple[int, int, int]]) -> bytes:
    flat = bytes(channel for pixel in pixels for channel in (*pixel, 255))
    assert len(flat) == width * height * 4
    return encode_rgba(width, height, flat)


# --- the palette ----------------------------------------------------------------------


def test_a_colour_resolves_to_the_index_that_carries_it():
    table = _table({5: sg.pack_gba_colour(0, 255, 0), 9: sg.pack_gba_colour(0, 0, 255)})
    assert tg.index_for_colour((0, 255, 0), table) == 5
    assert tg.index_for_colour((0, 0, 255), table) == 9


def test_a_colour_matches_at_the_hardware_five_bit_resolution():
    """Both spellings of one BGR555 colour must reach the same entry.

    The sprite sheets state a colour as ``v << 3`` and the portrait carries
    ``(v << 3) | (v >> 2)``; the reader drops the low three bits of each channel, so both
    resolve to the palette entry that holds ``v``.
    """
    word = 30 | (24 << 5) | (14 << 10)
    table = _table({200: word})
    assert tg.index_for_colour((240, 192, 112), table) == 200
    assert tg.index_for_colour((247, 198, 115), table) == 200
    assert sg.expand_bgr555(word) == (247, 198, 115)


def test_the_chroma_key_is_the_transparent_index():
    table = _table({3: sg.pack_gba_colour(0, 0, 0)})
    assert tg.index_for_colour(tg.CHROMA_KEY, table) == sg.TRANSPARENT_INDEX


def test_black_skips_the_transparent_index_when_both_carry_it():
    table = _table({0: 0, 1: 0})
    assert tg.index_for_colour((0, 0, 0), table) == 1


def test_a_colour_the_palette_does_not_carry_is_refused():
    table = _table({1: sg.pack_gba_colour(0, 0, 0)})
    with pytest.raises(tg.TulmaGraphicsError, match="not in the object palette"):
        tg.index_for_colour((0, 255, 0), table)


def test_an_ambiguous_visible_colour_is_refused_rather_than_guessed():
    table = _table({2: 0, 7: 0})
    with pytest.raises(tg.TulmaGraphicsError, match="no single visible index"):
        tg.index_for_colour((0, 0, 0), table)


def test_a_palette_address_outside_the_image_is_a_refusal_not_an_address():
    with pytest.raises(tg.TulmaGraphicsError, match="outside"):
        tg.file_offset(0x08000020, 16)


# --- the sheet cell -------------------------------------------------------------------


def test_the_cell_crop_reads_the_sixteen_wide_window_at_x_eight():
    """A cell whose columns are their own colour proves which window the crop reads."""
    table = _table({index: index for index in range(1, 32)})
    pixels = [((x << 3), 0, 0) for _ in range(32) for x in range(32)]
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "stand.png"
        target.write_bytes(_rgb(32, 32, pixels))
        raster = tg.raster_from_png(target, table, 16, 32, cell=0)
    assert len(raster) == 16 * 32
    # Column x of the crop is source column 8 + x, whose colour is the index 8 + x.
    assert raster[0] == 8
    assert raster[15] == 23
    assert raster[16] == 8


def test_a_sheet_that_encodes_its_hole_in_alpha_is_refused():
    table = _table({1: sg.pack_gba_colour(0, 0, 0)})
    flat = bytearray()
    for _ in range(32 * 32):
        flat += bytes((0, 0, 0, 0))
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "stand.png"
        target.write_bytes(encode_rgba(32, 32, bytes(flat)))
        with pytest.raises(tg.TulmaGraphicsError, match="partly transparent"):
            tg.raster_from_png(target, table, 16, 32, cell=0)


def test_mirror_reverses_each_row_and_nothing_else():
    raster = bytes(range(4)) * 2
    assert tg.mirror(raster, 4, 2) == bytes([3, 2, 1, 0, 3, 2, 1, 0])


# --- one container, every cell that names it ------------------------------------------


def _cell(offset: int, raster: bytes, *, slot=0, frame=0, direction=0, piece=0x100):
    return tg.Cell(slot=slot, frame=frame, direction=direction, graphic_offset=offset,
                   piece_offset=piece, raster=raster)


def test_a_container_named_twice_keeps_every_reference_word():
    """The defect this guard exists for: repointing one facing leaves the other retail."""
    target, = tg.containers([
        _cell(0x2000, b"a" * 4, direction=2, piece=0x100),
        _cell(0x2000, b"a" * 4, direction=3, piece=0x200),
    ]).values()
    assert target.references == (0x100, 0x200)


def test_a_container_two_cells_disagree_about_is_refused():
    with pytest.raises(tg.TulmaGraphicsError, match="disagrees"):
        tg.containers([
            _cell(0x2000, b"a" * 4, direction=2),
            _cell(0x2000, b"b" * 4, direction=3),
        ])


def test_a_container_named_once_carries_one_reference():
    target, = tg.containers([_cell(0x2000, b"a" * 4, piece=0x188)]).values()
    assert target.references == (0x188,)


def test_the_portrait_payload_is_written_linear_and_not_as_tiles():
    """The defect a runtime session found: the portrait raster is not swizzled tiles.

    Rendering the retail portrait container's own payload as a linear 64x64 raster reproduces
    the retail portrait, so the payload is linear. A writer that swizzles it passes its own
    decode-then-compare round trip, because that round trip is the identity inside the wrong
    model, and puts noise on the screen. This asserts the bytes actually written.
    """
    raster = bytes((i * 7) % 251 for i in range(tg.PORTRAIT_SIDE ** 2))
    container = wl.pack(raster, kind=1)
    data = b"\x00" * 0x40 + container
    plan = tg.Plan()
    tg.plan_portrait(data, plan, 0x40, raster, owner="portrait", reference_words=())
    written = plan.writes[0].new
    assert written == container
    swizzled = wl.pack(sg.swizzle_tiles(raster, tg.PORTRAIT_SIDE, tg.PORTRAIT_SIDE,
                                        colour_256=True), kind=1)
    assert written != swizzled
    assert wl.unpack(bytes(0x40) + written, 0x40).data == raster


def test_a_portrait_whose_extent_disagrees_with_the_raster_is_refused():
    container = wl.pack(bytes(64), kind=1)
    with pytest.raises(tg.TulmaGraphicsError, match="declares"):
        tg.plan_portrait(bytes(0x40) + container, tg.Plan(), 0x40, bytes(80),
                         owner="portrait", reference_words=())


# --- apply and verify -----------------------------------------------------------------


def _write(offset: int, old: bytes, new: bytes, spans: list[list[int]]) -> tuple[tg.Write, dict]:
    return (tg.Write(offset, old, new, "owner", "reason"),
            {"spans": spans, "placement": "x"})


def test_apply_refuses_a_base_that_does_not_hold_what_the_plan_expects():
    plan = tg.Plan()
    plan.writes.append(tg.Write(4, b"zzzz", b"abcd", "o", "r"))
    with pytest.raises(tg.TulmaGraphicsError, match="does not hold"):
        tg.apply(b"0123456789", plan)


def test_apply_refuses_overlapping_writes_even_when_both_match_the_base():
    plan = tg.Plan()
    plan.writes.append(tg.Write(0, b"aaaa", b"bbbb", "o", "r"))
    plan.writes.append(tg.Write(2, b"aa", b"cc", "o", "r"))
    with pytest.raises(tg.TulmaGraphicsError, match="overlapping"):
        tg.apply(b"aaaa" + b"\xff" * 8, plan)


def test_an_append_at_the_old_end_of_image_needs_no_padding():
    plan = tg.Plan()
    plan.writes.append(tg.Write(8, b"", b"XY", "o", "r"))
    assert tg.apply(b"01234567", plan) == b"01234567XY"


def test_an_append_past_the_old_end_is_padded_with_the_open_bus_byte():
    """A payload must land 4-byte aligned, so the alignment run is written as 0xFF."""
    plan = tg.Plan()
    plan.writes.append(tg.Write(10, b"", b"XY", "o", "r"))
    assert tg.apply(b"01234567", plan) == b"01234567\xff\xffXY"


def test_verify_refuses_a_changed_byte_outside_every_declared_span():
    plan = tg.Plan()
    write, record = _write(0, b"ab", b"AB", [[0, 2]])
    plan.writes.append(write)
    plan.records.append(record)
    assert tg.verify(b"abcd", b"ABcd", plan)["changed_bytes_inside_declared_spans"] == 2
    with pytest.raises(tg.TulmaGraphicsError, match="outside every declared span"):
        tg.verify(b"abcd", b"ABcD", plan)


def test_a_declared_span_beyond_the_base_is_still_attributed():
    """An appended payload and its alignment run are one owner's span, not a stray byte."""
    plan = tg.Plan()
    write, record = _write(4, b"", b"\xff\xffXY", [[4, 4]])
    plan.writes.append(write)
    plan.records.append(record)
    report = tg.verify(b"abcd", b"abcd\xff\xffXY", plan)
    assert report["changed_bytes_outside"] == 0
    assert report["appended_bytes"] == 4
