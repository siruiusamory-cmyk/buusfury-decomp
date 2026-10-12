"""Intent versus screen, on one command: the diff count, its bounding box, and both crops.

WHY. Three hand-written reassembly loops did this job on one ticket, each with its own bug surface, and one of
them shared the converter's wrong layout assumption and therefore agreed with it: the sprite was reported as
rendering correctly from a full-screen capture while a 4x crop showed blank rows in BOTH the patched and the
unpatched run. Both halves of that defect - no crop, and a comparison built on the wrong layout - are
addressed here by making the intent come from the engine's own records and by reporting counts a review can
check rather than an adjective.

WHAT IT COMPOSES, and from where. The intent is the frame the ROM says the sprite should draw: the
sprite-definition pointer table at ``0x6B6BB4 + 4*id``, the definition's inline animation array at
``def + 0x54``, the animation record, the frame record, and each piece's graphics container decoded through
`webfoot.formats.sprite_graphics`. Every step here is that module's own walk; nothing about the layout is
re-derived.

WHAT IT COMPARES. The composed frame stays an INDEX canvas, so it renders through any 256-entry object
palette without re-quantising. The screen side comes from a PNG written by an emulator capture or by
`tools.research.oam_sprites`, and both the indexed and the truecolour forms are read. Three counts are
reported instead of one, because a single "differs" number cannot tell a shape defect from a palette defect:

* ``differing`` - pixels the intent paints where the screen shows a different colour;
* ``missing``   - pixels the intent paints that the screen does not draw at all;
* ``extra``     - pixels the screen draws where the intent paints nothing.

The bounding box is over the union of the three, which is the box a crop should be taken from.

WHAT IT WRITES, and where. Crops under the caller's output prefix, by convention under the ignored
``build/`` tree: the intent through this image's palette, optionally the same intent through the source
title's palette, the screen crop, and a diff marking. Nothing decoded is written into the repository and no
palette is modified.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.export import png  # noqa: E402
from tools.webfoot.formats import indexed_png, rgb_png, sprite_graphics, webfoot_lz  # noqa: E402

ROM_BASE = 0x08000000
#: The sprite-definition pointer table, from the accepted sprite run.
DEFINITION_TABLE = 0x6B6BB4
#: The inline animation pointer array inside a definition.
DEFINITION_SLOTS = 0x54
TRANSPARENT = sprite_graphics.TRANSPARENT_INDEX
#: Diff marking colours: unchanged (transparent), differing, missing, extra.
MARKING_PALETTE = ((0, 0, 0), (255, 0, 0), (0, 128, 255), (255, 255, 0))


class IntentError(ValueError):
    """Raised when the image does not hold the records the walk needs, or a crop does not fit."""


@dataclass(frozen=True)
class Raster:
    """An image in some channel layout: ``channels`` bytes per pixel, row major."""

    pixels: bytes
    width: int
    height: int
    channels: int

    def crop(self, x: int, y: int, width: int, height: int) -> "Raster":
        if x < 0 or y < 0 or x + width > self.width or y + height > self.height:
            raise IntentError(f"crop {width}x{height} at ({x},{y}) leaves a "
                              f"{self.width}x{self.height} raster")
        out = bytearray(width * height * self.channels)
        for row in range(height):
            source = ((y + row) * self.width + x) * self.channels
            out[row * width * self.channels:(row + 1) * width * self.channels] = \
                self.pixels[source:source + width * self.channels]
        return Raster(pixels=bytes(out), width=width, height=height, channels=self.channels)


@dataclass(frozen=True)
class Diff:
    """The three counts and the bounding box over their union, in crop coordinates."""

    width: int
    height: int
    differing: int
    missing: int
    extra: int
    bounding_box: tuple[int, int, int, int] | None

    def report(self) -> str:
        box = "none" if self.bounding_box is None else \
            (f"({self.bounding_box[0]},{self.bounding_box[1]}) "
             f"{self.bounding_box[2]}x{self.bounding_box[3]}")
        return (f"{self.width}x{self.height}: {self.differing} differing, {self.missing} missing, "
                f"{self.extra} extra; bounding box {box}")


# --- the intent, from the image's own records --------------------------------

def definition_offset(image: bytes, sprite_id: int) -> int:
    at = DEFINITION_TABLE + 4 * sprite_id
    if at + 4 > len(image):
        raise IntentError(f"sprite id {sprite_id} has no table entry inside the image")
    pointer = struct.unpack_from("<I", image, at)[0]
    if not ROM_BASE <= pointer < ROM_BASE + len(image):
        raise IntentError(f"sprite id {sprite_id} resolves to {pointer:#010x}, outside the image")
    return pointer - ROM_BASE


def frame_offset(image: bytes, sprite_id: int, slot: int, frame_index: int, direction: int) -> int:
    """The frame record the engine would draw for this (sprite, animation slot, frame, direction)."""
    at = definition_offset(image, sprite_id)
    count = image[at]
    if not 1 <= slot <= count:
        raise IntentError(f"sprite {sprite_id} announces {count} animation slot(s); slot {slot} is outside "
                          "the inline array the engine indexes with no bound check")
    pointer = struct.unpack_from("<I", image, at + DEFINITION_SLOTS + 4 * (slot - 1))[0]
    if not ROM_BASE <= pointer < ROM_BASE + len(image):
        raise IntentError(f"sprite {sprite_id} slot {slot} is a null or out-of-image animation pointer")
    try:
        animation = sprite_graphics.decode_animation(image, pointer - ROM_BASE)
        target = animation.pointer_for(frame_index, direction)
    except sprite_graphics.SpriteFormatError as error:
        raise IntentError(f"sprite {sprite_id} slot {slot}: {error}") from error
    if not ROM_BASE <= target < ROM_BASE + len(image):
        raise IntentError(f"sprite {sprite_id} slot {slot} frame {frame_index} direction {direction} "
                          "points outside the image")
    return target - ROM_BASE


def compose_frame(image: bytes, frame: sprite_graphics.Frame) -> tuple[bytes, int, int]:
    """The frame's pieces as one palette-index canvas, in the frame's own bounding box.

    A 4bpp piece addresses ONE sixteen-entry bank, so its drawn index is ``bank * 16 + nibble`` and a zero
    nibble is transparent; an 8bpp piece's byte IS the index. Keeping indices rather than colours is what
    lets the same canvas render through this image's palette and the source title's.
    """
    min_x, min_y, width, height = frame.piece_bounds
    if width <= 0 or height <= 0:
        raise IntentError(f"frame at {frame.offset:#x} has an empty bounding box")
    canvas = bytearray(width * height)
    for piece in frame.pieces:
        piece_width, piece_height = piece.dimensions
        container = piece.graphics_pointer
        if not ROM_BASE <= container < ROM_BASE + len(image):
            raise IntentError(f"piece at {piece.offset:#x} points at {container:#010x}, outside the image")
        try:
            graphic = sprite_graphics.decode_graphic(image, container - ROM_BASE, piece_width,
                                                     piece_height, colour_256=piece.colour_256)
        except (sprite_graphics.SpriteFormatError, webfoot_lz.ContainerError) as error:
            raise IntentError(f"piece at {piece.offset:#x}: {error}") from error
        bank = (piece.attributes >> 28) & 0xF
        for y in range(piece_height):
            canvas_y = piece.y - min_y + y
            if not 0 <= canvas_y < height:
                continue
            for x in range(piece_width):
                canvas_x = piece.x - min_x + x
                if not 0 <= canvas_x < width:
                    continue
                value = graphic.pixels[y * piece_width + x]
                index = value if piece.colour_256 else (bank * 16 + value if value else 0)
                if index:
                    canvas[canvas_y * width + canvas_x] = index
    return bytes(canvas), width, height


def palette_rgb(image: bytes, offset: int) -> tuple[tuple[int, int, int], ...]:
    return sprite_graphics.decode_palette(image, offset - ROM_BASE).rgb


def render_rgb(canvas: bytes, width: int, height: int,
               colours: tuple[tuple[int, int, int], ...]) -> Raster:
    out = bytearray(width * height * 3)
    for position, index in enumerate(canvas):
        red, green, blue = colours[index]
        out[3 * position:3 * position + 3] = bytes((red, green, blue))
    return Raster(pixels=bytes(out), width=width, height=height, channels=3)


def read_screen(path: Path) -> Raster:
    """A capture as RGB, from either PNG form. A truecolour capture keeps its alpha as a fourth channel."""
    data = path.read_bytes()
    try:
        pixels, width, height, colours, _transparent = indexed_png.decode(data)
        return render_rgb(pixels, width, height, colours)
    except indexed_png.PngError:
        rgb, width, height, alpha = rgb_png.decode_truecolour(data)
        if alpha is None:
            return Raster(pixels=rgb, width=width, height=height, channels=3)
        interleaved = bytearray(width * height * 4)
        for position in range(width * height):
            interleaved[4 * position:4 * position + 3] = rgb[3 * position:3 * position + 3]
            interleaved[4 * position + 3] = alpha[position]
        return Raster(pixels=bytes(interleaved), width=width, height=height, channels=4)


# --- the comparison ----------------------------------------------------------

def compare(canvas: bytes, intent: Raster, screen: Raster) -> tuple[Diff, bytes]:
    """The three counts, the union's bounding box, and a marking image.

    ``canvas`` is the intent in the index domain, which is where transparency lives: index 0 is transparent,
    so a rendered intent pixel carries no way to say "nothing is drawn here". The screen states its own
    transparency with an alpha channel when the capture has one, and a capture without alpha is taken to be
    fully opaque, which is what a screenshot of a screen-wide frame is.
    """
    if (intent.width, intent.height) != (screen.width, screen.height):
        raise IntentError(f"the intent is {intent.width}x{intent.height} and the crop is "
                          f"{screen.width}x{screen.height}")
    if len(canvas) != intent.width * intent.height:
        raise IntentError("the intent canvas does not match the intent raster")
    marks = bytearray(intent.width * intent.height)
    differing = missing = extra = 0
    left = top = None
    right = bottom = -1
    for position in range(intent.width * intent.height):
        intent_index = canvas[position]
        intended = intent.pixels[3 * position:3 * position + 3]
        drawn = screen.pixels[screen.channels * position:screen.channels * position + 3]
        opaque = screen.channels == 3 or screen.pixels[screen.channels * position + 3] != 0
        if intent_index == TRANSPARENT:
            mark = 3 if opaque else 0
            extra += 1 if mark else 0
        elif not opaque:
            mark = 2
            missing += 1
        elif drawn != intended:
            mark = 1
            differing += 1
        else:
            mark = 0
        if mark:
            marks[position] = mark
            x, y = position % intent.width, position // intent.width
            left = x if left is None else min(left, x)
            top = y if top is None else min(top, y)
            right, bottom = max(right, x), max(bottom, y)
    box = None if left is None else (left, top, right - left + 1, bottom - top + 1)
    return Diff(width=intent.width, height=intent.height, differing=differing, missing=missing,
                extra=extra, bounding_box=box), bytes(marks)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", type=Path, required=True, help="the image whose records are the intent")
    parser.add_argument("--sprite", type=int, required=True)
    parser.add_argument("--slot", type=int, default=1, help="animation slot, 1-based as the array is")
    parser.add_argument("--frame", type=int, default=0)
    parser.add_argument("--direction", type=int, default=0)
    parser.add_argument("--palette", type=lambda text: int(text, 0), required=True,
                        help="this image's object palette offset")
    parser.add_argument("--source-palette", type=lambda text: int(text, 0), default=None)
    parser.add_argument("--screen", type=Path, default=None, help="a capture PNG to compare against")
    parser.add_argument("--box", default=None, help="x,y,w,h of the sprite inside the capture")
    parser.add_argument("--out", type=Path, required=True, help="output prefix for the crops")
    args = parser.parse_args()

    image = args.image.read_bytes()
    offset = frame_offset(image, args.sprite, args.slot, args.frame, args.direction)
    frame = sprite_graphics.decode_frame(image, offset)
    canvas, width, height = compose_frame(image, frame)
    painted = sum(1 for index in canvas if index)
    print(f"sprite {args.sprite} slot {args.slot} frame {args.frame} direction {args.direction}: "
          f"frame at 0x{offset + ROM_BASE:08X}, {frame.piece_count} piece(s), {painted} painted pixel(s), "
          f"box {frame.piece_bounds}")

    colours = palette_rgb(image, args.palette)
    intent = render_rgb(canvas, width, height, colours)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    written = [args.out.with_name(args.out.name + "-intent.png")]
    written[0].write_bytes(indexed_png.encode(canvas, width, height, colours,
                                              transparent_index=TRANSPARENT))
    if args.source_palette:
        source = args.out.with_name(args.out.name + "-intent-source-palette.png")
        source.write_bytes(indexed_png.encode(canvas, width, height,
                                              palette_rgb(image, args.source_palette),
                                              transparent_index=TRANSPARENT))
        written.append(source)

    summary = {"sprite": args.sprite, "slot": args.slot, "frame": args.frame,
               "direction": args.direction, "painted": painted, "piece_count": frame.piece_count,
               "frame_bounds": list(frame.piece_bounds)}
    if args.screen and args.box:
        screen = read_screen(args.screen)
        x, y, box_width, box_height = (int(part) for part in args.box.split(","))
        crop = screen.crop(x, y, box_width, box_height)
        diff, marks = compare(canvas, intent, crop)
        print(diff.report())
        marking = args.out.with_name(args.out.name + "-diff.png")
        marking.write_bytes(indexed_png.encode(marks, diff.width, diff.height, MARKING_PALETTE,
                                               transparent_index=0))
        crop_path = args.out.with_name(args.out.name + "-screen-crop.png")
        crop_path.write_bytes(png.encode_rgba(crop.width, crop.height,
                                              rgba_of(crop)))
        written += [marking, crop_path]
        summary["diff"] = {"differing": diff.differing, "missing": diff.missing, "extra": diff.extra,
                           "bounding_box": diff.bounding_box}
    for path in written:
        print(f"wrote {path}")
    print(json.dumps(summary, sort_keys=True))
    return 0


def rgba_of(raster: Raster) -> bytes:
    """An RGBA buffer for the PNG writer, from a 3- or 4-channel raster."""
    if raster.channels == 4:
        return raster.pixels
    out = bytearray(raster.width * raster.height * 4)
    for position in range(raster.width * raster.height):
        out[4 * position:4 * position + 3] = raster.pixels[3 * position:3 * position + 3]
        out[4 * position + 3] = 0xFF
    return bytes(out)


if __name__ == "__main__":
    raise SystemExit(main())
