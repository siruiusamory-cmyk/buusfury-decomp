"""Compare a rendered dialogue line against a native mGBA capture, pixel by pixel.

Read-only: it reads a capture and the ROM and reports a diff; it writes nothing but its own report.

HOW THE COMPARISON AVOIDS GUESSING THE LAYOUT. The box's position on screen is not taken from any
model: the decoder's box art (a 160x64 container) is template-matched against the capture over every
offset, and the offset with the most matching pixels wins. That locates the surface the engine drew.
The pixels that then DIFFER from the art are the text the engine painted, which is exactly the layer a
renderer must reproduce; comparing that mask against rendered candidates both identifies the line and
measures the renderer, without either side being assumed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research.dialogue_font import Font, GLYPH_ROWS  # noqa: E402
from tools.research.dialogue_preview import (  # noqa: F401
    WRAP_WIDTH,  # noqa: E402
    BOX_ART_ALT, BOX_ART_PRIMARY, LINE_HEIGHT, NEWLINE, SURFACE_HEIGHT, SURFACE_WIDTH,
    load_box_art, read_png_pixels)
from tools.webfoot import compressed_dialogue as cd  # noqa: E402
from tools.webfoot.dialogue_repack import container_pointers, text_of  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402

ROM_BASE = 0x08000000


def capture_pixels(path: Path) -> list[list[tuple[int, int, int]]]:
    """The capture as RGB triples per pixel.

    An mGBA screenshot is a full-colour PNG: three bytes per pixel (or four, or an indexed palette).
    Comparing those bytes against palette indices compares nonsense, so everything here is RGB.
    """
    width, height, rows = read_png_pixels(path)
    if (width, height) != (240, 160):
        raise SystemExit(f"REFUSED: the capture is {width}x{height}, not a native 240x160 frame")
    sample = rows[0]
    if len(sample) == width * 3:
        return [[(row[3 * x], row[3 * x + 1], row[3 * x + 2]) for x in range(width)]
                for row in rows]
    if len(sample) == width * 4:
        return [[(row[4 * x], row[4 * x + 1], row[4 * x + 2]) for x in range(width)]
                for row in rows]
    raise SystemExit(f"REFUSED: unexpected capture row stride {len(sample)} for {width} pixels")


def art_rgb(art: bytes, palette: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    return [palette[index] for index in art]


def find_box(rows: list[list[tuple[int, int, int]]],
             art: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    """The offset where the box art best matches, with its match count, in RGB."""
    best = (-1, 0, 0)
    for offset_y in range(0, 160 - SURFACE_HEIGHT + 1):
        for offset_x in range(0, 240 - SURFACE_WIDTH + 1):
            matches = 0
            for row in range(SURFACE_HEIGHT):
                capture_row = rows[offset_y + row]
                for column in range(SURFACE_WIDTH):
                    if capture_row[offset_x + column] == art[row * SURFACE_WIDTH + column]:
                        matches += 1
            if matches > best[0]:
                best = (matches, offset_x, offset_y)
    return best[1], best[2], best[0]


def text_mask(rows: list[list[tuple[int, int, int]]], art: list[tuple[int, int, int]],
              offset_x: int, offset_y: int) -> dict:
    """The pixels the engine painted over the art, with the colours it used."""
    mask = {}
    colour_counts: dict[tuple[int, int, int], int] = {}
    for row in range(SURFACE_HEIGHT):
        capture_row = rows[offset_y + row]
        for column in range(SURFACE_WIDTH):
            value = capture_row[offset_x + column]
            if value != art[row * SURFACE_WIDTH + column]:
                mask[(column, row)] = value
                colour_counts[value] = colour_counts.get(value, 0) + 1
    return {"mask": mask, "colour_counts": colour_counts}


def wrap_lines(font: Font, text: str, width: int) -> list[str]:
    """Greedy word wrap at width pixels, the rule the capture fitted."""
    lines = []
    current = ""
    current_width = 0
    for word in text.split(" "):
        word_width = sum(font.advance(ord(character)) for character in word)
        if current and current_width + font.advance(ord(" ")) + word_width > width:
            lines.append(current)
            current, current_width = word, word_width
        else:
            current += (" " if current else "") + word
            current_width += (font.advance(ord(" ")) if len(current) > len(word) else 0) + word_width
    if current:
        lines.append(current)
    return lines


def render_mask(font: Font, text: str, ink: tuple[int, int, int],
                origin: tuple[int, int] = (8, 3), wrap_width: int = WRAP_WIDTH) -> dict:
    """Where a candidate line would put ink, and in which colour, WRAPPED as the engine wraps.

    Rendering a candidate unwrapped was the reason a correct line could never match: the engine broke
    this very line after "evil", and an unwrapped render put its remaining words on one long row.
    """
    mask = {}
    y = origin[1]
    for line in wrap_lines(font, text, wrap_width):
        x = origin[0]
        for character in line:
            code = ord(character)
            glyph = font.glyph(code)
            if glyph is not None:
                for column in range(glyph.width):
                    for row in range(GLYPH_ROWS):
                        if (glyph.columns[column] >> row) & 1:
                            mask[(x + column, y + row)] = ink
            x += font.advance(code)
        y += LINE_HEIGHT
    return mask


def compare(engine_mask: dict, candidate: dict) -> tuple[int, int, int]:
    """(positions only the engine painted, positions only the candidate painted, both)."""
    engine = engine_mask["mask"]
    both = len(set(engine) & set(candidate))
    return len(set(engine) - set(candidate)), len(set(candidate) - set(engine)), both


def dialogue_texts(image: bytes) -> list[str]:
    streams = {}
    for selector, pointer in container_pointers(image).items():
        if pointer >= ROM_BASE and pointer - ROM_BASE + 8 < len(image):
            streams[selector] = bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)
    texts = []
    for selector, stream in sorted(streams.items()):
        for record in cd.dialogue_record_inventory(image, selector, len(stream)):
            start, length = record.handle.decoded_start, record.handle.decoded_length
            if start + length <= len(stream):
                texts.append(text_of(stream, start, length).lstrip("#!"))
    return texts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--capture", required=True)
    parser.add_argument("--box", default=hex(BOX_ART_PRIMARY))
    args = parser.parse_args()
    image = Path(args.rom).read_bytes()
    font = Font(image)
    art = load_box_art(image, int(args.box, 16))
    rows = capture_pixels(Path(args.capture))
    from tools.research.dialogue_preview import load_palette
    palette = load_palette(image)
    art = art_rgb(art, palette)
    offset_x, offset_y, matches = find_box(rows, art)
    print(f"box art matched at ({offset_x},{offset_y}) with {matches} of "
          f"{SURFACE_WIDTH * SURFACE_HEIGHT} pixels identical "
          f"({100 * matches // (SURFACE_WIDTH * SURFACE_HEIGHT)}%)")
    engine = text_mask(rows, art, offset_x, offset_y)
    print(f"pixels the engine painted over the art: {len(engine['mask'])}, "
          f"colours {sorted(engine['colour_counts'].items(), key=lambda item: -item[1])[:5]}")
    ink = (max(engine["colour_counts"], key=engine["colour_counts"].get)
           if engine["colour_counts"] else palette[1])
    if ink in palette:
        print(f"engine ink colour {ink} is palette index {palette.index(ink)}")
    # The engine reveals a line character by character, so the comparison is against prefixes.
    best = None
    for text in dialogue_texts(image):
        limit = min(len(text), 120)
        for length in range(1, limit + 1):
            candidate = render_mask(font, text[:length], ink)
            if not candidate:
                continue
            only_engine, only_candidate, both = compare(engine, candidate)
            score = only_engine + only_candidate
            if best is None or score < best[0]:
                best = (score, text, length, only_engine, only_candidate, both, (8, 3))
    if best is None:
        print("no candidate line rendered anything")
        return 1
    score, text, length, only_engine, only_candidate, both, origin = best
    # Fit the origin on the winning line: the strip's surface origin is not established statically.
    # The origin is now the measured one; only a small window around it is searched, and a zero-score
    # result is reported as pixel-exact rather than as a better fit.
    for origin_x in range(6, 11):
        for origin_y in range(1, 6):
            candidate = render_mask(font, text[:length], ink, (origin_x, origin_y))
            only_e, only_c, both_c = compare(engine, candidate)
            if only_e + only_c < score:
                score, origin = only_e + only_c, (origin_x, origin_y)
                only_engine, only_candidate, both = only_e, only_c, both_c
    print(f"best candidate: {text[:70]!r}")
    print(f"  revealed prefix length:     {length} of {len(text)} characters")
    print(f"  fitted text origin:         {origin} in surface coordinates")
    print(f"  painted by the engine only: {only_engine}")
    print(f"  painted by the render only: {only_candidate}")
    print(f"  painted by both:            {both}")
    print(f"  total disagreement:         {score} of {len(engine['mask'])} engine pixels")
    if score == 0:
        print("VERDICT: pixel-exact for the revealed prefix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
