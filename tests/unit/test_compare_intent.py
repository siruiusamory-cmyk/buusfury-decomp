"""Intent versus screen: the walk, the index canvas, and the three counts.

The comparison is checked in the index domain because that is where transparency lives, and the counts are
checked separately - a shape defect shows up as `missing`/`extra`, a palette defect as `differing`, and a
report that only counted "differs" could not tell a reviewer which of the two it was looking at.
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.research import compare_intent as intent  # noqa: E402
from tools.webfoot.formats import indexed_png, sprite_graphics, webfoot_lz  # noqa: E402

SPRITE = 7
PALETTE_AT = 0x1000
#: The command takes GBA addresses, the fixture is built at file offsets.
PALETTE_ADDRESS = intent.ROM_BASE + PALETTE_AT
CONTAINER_AT = 0x2000
FRAME_AT = 0x3000
ANIMATION_AT = 0x4000
DEFINITION_AT = 0x5000
TABLE_AT = 0x100
COLOURS = ((0, 0, 0), (248, 0, 0), (0, 248, 0), (0, 0, 248))


def build_image(*, pixels: bytes | None = None) -> bytes:
    """A small image holding one 8x8 8bpp sprite: palette, container, frame, animation, definition, table."""
    payload = pixels if pixels is not None else bytes([1] * 64)
    image = bytearray(DEFINITION_AT + 0x60)
    words = [0] * 256
    words[1], words[2], words[3] = 0x001F, 0x03E0, 0x7C00
    struct.pack_into("<256H", image, PALETTE_AT, *words)
    packed = webfoot_lz.pack(payload, kind=1)
    image[CONTAINER_AT:CONTAINER_AT + len(packed)] = packed
    struct.pack_into("<I", image, FRAME_AT, 1)                     # one piece
    struct.pack_into("<bbBB", image, FRAME_AT + 4, 0, 0, 8, 8)     # bounding box
    struct.pack_into("<bbBB", image, FRAME_AT + 8, 0, 0, 8, 8)     # piece x, y, w, h
    struct.pack_into("<I", image, FRAME_AT + 12, 0x2000)           # 8bpp, square 8x8
    struct.pack_into("<I", image, FRAME_AT + 16, intent.ROM_BASE + CONTAINER_AT)
    struct.pack_into("<I", image, ANIMATION_AT, 1)
    for direction in range(4):
        struct.pack_into("<I", image, ANIMATION_AT + 4 + 4 * direction,
                         intent.ROM_BASE + FRAME_AT)
    image[DEFINITION_AT] = 1                                        # one animation slot
    struct.pack_into("<I", image, DEFINITION_AT + intent.DEFINITION_SLOTS,
                     intent.ROM_BASE + ANIMATION_AT)
    struct.pack_into("<I", image, TABLE_AT + 4 * SPRITE, intent.ROM_BASE + DEFINITION_AT)
    return bytes(image)


@pytest.fixture(autouse=True)
def small_table(monkeypatch) -> None:
    monkeypatch.setattr(intent, "DEFINITION_TABLE", TABLE_AT)


def intent_canvas(image: bytes) -> tuple[bytes, int, int]:
    offset = intent.frame_offset(image, SPRITE, 1, 0, 0)
    frame = sprite_graphics.decode_frame(image, offset)
    return intent.compose_frame(image, frame)


def test_the_walk_finds_the_frame_the_definition_names() -> None:
    image = build_image()
    assert intent.frame_offset(image, SPRITE, 1, 0, 0) == FRAME_AT
    with pytest.raises(intent.IntentError, match="announces 1 animation slot"):
        intent.frame_offset(image, SPRITE, 2, 0, 0)
    with pytest.raises(intent.IntentError, match="slot 1: frame 5 out of range"):
        intent.frame_offset(image, SPRITE, 1, 5, 0)


def test_the_canvas_holds_indices_in_the_frames_own_box() -> None:
    canvas, width, height = intent_canvas(build_image())
    assert (width, height) == (8, 8)
    assert set(canvas) == {1}
    written = intent_canvas(build_image(pixels=bytes([2] * 64)))[0]
    assert set(written) == {2}
    with pytest.raises(intent.IntentError, match="no table entry"):
        intent.definition_offset(build_image(), 0xFFFF)


def test_a_matching_crop_reports_nothing_and_a_changed_pixel_reports_one() -> None:
    image = build_image()
    canvas, width, height = intent_canvas(image)
    colours = intent.palette_rgb(image, PALETTE_ADDRESS)
    assert colours[:4] == ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255))
    rendered = intent.render_rgb(canvas, width, height, colours)

    same, marks = intent.compare(canvas, rendered, rendered)
    assert (same.differing, same.missing, same.extra) == (0, 0, 0)
    assert same.bounding_box is None and set(marks) == {0}

    other = bytearray(rendered.pixels)
    other[3 * (2 * 8 + 3):3 * (2 * 8 + 3) + 3] = bytes((0, 0, 255))
    changed = intent.Raster(pixels=bytes(other), width=width, height=height, channels=3)
    diff, marks = intent.compare(canvas, rendered, changed)
    assert diff.differing == 1 and diff.bounding_box == (3, 2, 1, 1)
    assert marks[2 * 8 + 3] == 1
    assert "1 differing, 0 missing, 0 extra; bounding box (3,2) 1x1" in diff.report()


def test_a_screen_that_draws_nothing_is_missing_and_one_that_draws_elsewhere_is_extra() -> None:
    image = build_image(pixels=bytes([1] * 8 + [0] * 56))
    canvas, width, height = intent_canvas(image)
    colours = intent.palette_rgb(image, PALETTE_ADDRESS)
    rendered = intent.render_rgb(canvas, width, height, colours)

    blank = intent.Raster(pixels=bytes(width * height * 4), width=width, height=height, channels=4)
    diff, marks = intent.compare(canvas, rendered, blank)
    assert diff.missing == 8 and diff.differing == 0 and diff.extra == 0
    assert diff.bounding_box == (0, 0, 8, 1)
    assert marks[0] == 2

    full = bytearray(width * height * 4)
    for position in range(width * height):
        full[4 * position:4 * position + 4] = bytes((9, 9, 9, 255))
    diff, marks = intent.compare(canvas, rendered, intent.Raster(pixels=bytes(full), width=width,
                                                                 height=height, channels=4))
    assert diff.extra == 56, "everything the intent leaves transparent"
    assert diff.differing == 8 and diff.bounding_box == (0, 0, 8, 8)


def test_the_command_writes_both_crops_and_prints_its_counts(tmp_path: Path, monkeypatch, capsys) -> None:
    image = build_image()
    image_path = tmp_path / "intent.gba"
    image_path.write_bytes(image)
    canvas, width, height = intent_canvas(image)
    screen = tmp_path / "screen.png"
    screen.write_bytes(indexed_png.encode(canvas, width, height,
                                          intent.palette_rgb(image, PALETTE_ADDRESS),
                                          transparent_index=0))
    out = tmp_path / "compare" / "crop"
    monkeypatch.setattr(sys, "argv", [
        "compare_intent", "--image", str(image_path), "--sprite", str(SPRITE),
        "--palette", hex(PALETTE_ADDRESS), "--screen", str(screen), "--box", "0,0,8,8",
        "--source-palette", hex(PALETTE_ADDRESS), "--out", str(out)])
    assert intent.main() == 0
    printed = capsys.readouterr().out
    assert "0 differing, 0 missing, 0 extra" in printed
    summary = json.loads(printed.strip().splitlines()[-1])
    assert summary["diff"]["differing"] == 0 and summary["piece_count"] == 1
    for suffix in ("-intent.png", "-intent-source-palette.png", "-diff.png", "-screen-crop.png"):
        assert out.with_name(out.name + suffix).is_file(), suffix
    pixels, png_width, png_height, _colours, transparent = indexed_png.decode(
        out.with_name(out.name + "-intent.png").read_bytes())
    assert (png_width, png_height, transparent) == (width, height, 0)
    assert pixels == canvas
