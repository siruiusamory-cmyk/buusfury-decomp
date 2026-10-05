"""SPRITE-NEW-PROJECT-SURFACE-001: a project sheet PNG as the planner reads it.

The one thing that has to be exactly right here is cell order. A sheet is a
single row of square cells in four facing groups, and the planner reads cell
``c`` from pixel ``c * cell_width * cell_height`` - so the bytes it receives are
NOT the file's own row-major order once a sheet holds more than one cell. A
reader that handed over the file order would still produce a build: it would
simply draw a rearrangement of the author's art, which is why the discriminating
test below gives every cell its own colour.
"""

from __future__ import annotations

import pytest

from tests.helpers import write_truecolour_png
from tools.webfoot.project.model import AuthoredSpriteAnimation
from tools.webfoot.sprite_authoring import SpriteAuthoringError, read_source_sheet

SIDE = 4

#: Four facing colours and, for a two-frame sheet, the second frame's four.
FACING_COLOURS = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0))
SECOND_FRAME = ((0, 255, 255), (255, 0, 255), (128, 128, 128), (16, 32, 48))


def _sheet_png(path, frame_colours, *, alpha=None, side=SIDE):
    """One authored sheet in the layout the cell index describes.

    ``frame_colours[frame][cell]`` fills each cell, and the cells are laid out
    direction-major - every cell of facing ``d`` before the next facing - because
    that is the order the planner's own cell index names.
    """
    frames = len(frame_colours)
    width = frames * 4 * side
    rgb = bytearray()
    for _y in range(side):
        for cell in range(frames * 4):
            direction, frame = divmod(cell, frames)
            colour = frame_colours[frame][direction]
            for _ in range(side):
                rgb += bytes(colour)
    alpha_plane = None
    if alpha is not None:
        alpha_plane = bytes(alpha)
    return write_truecolour_png(path, bytes(rgb), width, side,
                                alpha=alpha_plane)


def _solid(sheet, cell: int, side: int = SIDE) -> bytes:
    pixels = sheet.cell(cell)
    assert len(pixels) == side * side * 3
    colours = {pixels[3 * index : 3 * index + 3] for index in range(side * side)}
    assert len(colours) == 1, "a cell should hold exactly one colour"
    return next(iter(colours))


def _animation(path, frames):
    return AuthoredSpriteAnimation(name="stand", sheet=str(path.name), frames=frames)


def test_each_cell_is_delivered_at_its_own_cell_index(tmp_path):
    """Four facings, one frame: cell ``d`` is facing ``d``, not a slice of the row."""
    path = _sheet_png(tmp_path / "stand.png", (FACING_COLOURS,))
    sheet = read_source_sheet(tmp_path, _animation(path, 1), where="test")
    assert (sheet.cell_width, sheet.cell_height) == (SIDE, SIDE)
    assert (sheet.frames_per_direction, sheet.frame_cells) == (1, 4)
    for direction in range(4):
        cell = sheet.slot_cell_index(0, direction)
        assert _solid(sheet, cell) == bytes(FACING_COLOURS[direction])


def test_a_second_frame_is_a_second_group_of_cells(tmp_path):
    path = _sheet_png(tmp_path / "walk.png", (FACING_COLOURS, SECOND_FRAME))
    sheet = read_source_sheet(tmp_path, _animation(path, 2), where="test")
    assert (sheet.frames_per_direction, sheet.frame_cells) == (2, 8)
    for frame in range(2):
        expected = (FACING_COLOURS, SECOND_FRAME)[frame]
        for direction in range(4):
            cell = sheet.slot_cell_index(frame, direction)
            assert _solid(sheet, cell) == bytes(expected[direction])


def test_the_sheet_must_be_one_row_of_square_cells(tmp_path):
    rgb = bytes(FACING_COLOURS[0] * (SIDE * SIDE * 4))
    path = write_truecolour_png(tmp_path / "stand.png", rgb, SIDE * 4, SIDE)
    with pytest.raises(SpriteAuthoringError, match="square cells"):
        read_source_sheet(tmp_path, _animation(path, 2), where="test")


def test_pixels_inside_a_cell_are_neither_transposed_nor_flipped(tmp_path):
    """A solid cell cannot tell a transpose from a correct read, so draw a shape.

    The pattern is asymmetric in both axes and every pixel differs from its
    neighbours, so a reader that flipped or transposed within the cell fails here
    rather than only in the one test that needs the private art.
    """
    side = SIDE
    key = (255, 0, 255)
    pixels = bytearray()
    for y in range(side):
        for x in range(side):
            pixels += bytes((10 + x, 20 + y, 30 + 2 * (x * side + y)))
    width = 4 * side
    rows = [pixels[3 * y * side : 3 * (y + 1) * side] for y in range(side)]
    rgb = bytearray()
    for row in rows:
        for _cell in range(4):
            rgb += row
    path = write_truecolour_png(tmp_path / "stand.png", bytes(rgb), width, side)
    sheet = read_source_sheet(tmp_path, _animation(path, 1), where="test")
    assert sheet.cell(2) == bytes(pixels)
    assert sheet.cell(2) != bytes(pixels[3:] + pixels[:3])


def test_a_missing_sheet_is_refused(tmp_path):
    animation = AuthoredSpriteAnimation(name="stand", sheet="missing.png", frames=1)
    with pytest.raises(SpriteAuthoringError, match="not a file in this project"):
        read_source_sheet(tmp_path, animation, where="test")


def test_a_partly_transparent_pixel_is_refused(tmp_path):
    """A palette index cannot carry a fraction of a colour, so refuse one."""
    side = SIDE
    alpha = bytearray([255]) * (4 * side * side)
    alpha[3] = 128
    path = _sheet_png(tmp_path / "stand.png", (FACING_COLOURS,), alpha=alpha)
    with pytest.raises(SpriteAuthoringError, match="partly transparent"):
        read_source_sheet(tmp_path, _animation(path, 1), where="test")


def test_a_fully_transparent_pixel_becomes_the_sheets_transparent_colour(tmp_path):
    """Alpha states the hole; the planner's chroma key is what reaches it."""
    alpha = bytearray([255]) * (4 * SIDE * SIDE)
    alpha[SIDE * 0 + 1] = 0
    path = _sheet_png(tmp_path / "stand.png", (FACING_COLOURS,), alpha=alpha)
    sheet = read_source_sheet(tmp_path, _animation(path, 1), where="test",
                              transparent_colour=(9, 8, 7))
    pixels = sheet.cell(sheet.slot_cell_index(0, 0))
    assert pixels[3 * 1 : 3 * 1 + 3] == bytes((9, 8, 7))
    assert sheet.transparent_colour == (9, 8, 7)


def test_an_rgb_sheet_needs_no_alpha_plane(tmp_path):
    path = _sheet_png(tmp_path / "stand.png", (FACING_COLOURS,))
    sheet = read_source_sheet(tmp_path, _animation(path, 1), where="test")
    assert _solid(sheet, sheet.slot_cell_index(0, 2)) == bytes(FACING_COLOURS[2])
