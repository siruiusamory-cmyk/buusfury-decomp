"""Dialogue render validation: identify the engine's line per capture, then compare pixel-exactly.

Read-only. A capture is a native 240x160 mGBA screenshot; the ROM supplies the font, the box surface and
the dialogue corpus.

WHY THIS IS A REWRITE OF THE SEARCH. The first version compared every dialogue line against every
prefix, which is ~2,000 lines times ~120 prefixes of full-bitmap work per capture: minutes each. The
engine's ink pixel count is known exactly, and a prefix's ink count only ever grows, so a prefix can
only be the one on screen if its cumulative ink count equals the engine's. That filter leaves a
handful of candidates per line and makes a whole directory cheap.

Any capture whose box is not on screen, or whose text is a line outside the dialogue corpus, is reported
as unidentified rather than forced onto the nearest match.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research.dialogue_font import Font, GLYPH_ROWS  # noqa: E402
from tools.research.dialogue_preview import (  # noqa: E402
    BOX_ART_PRIMARY, LINE_HEIGHT, SURFACE_HEIGHT, SURFACE_WIDTH, TEXT_ORIGIN, WRAP_WIDTH,
    load_box_art, load_palette, read_png_pixels)

ROM_BASE = 0x08000000
INK_TOLERANCE = 3           # a prefix's ink count may differ by rounding at the reveal edge


def capture_rgb(path: Path) -> list[list[tuple[int, int, int]]]:
    """A native capture as RGB triples: an mGBA screenshot is full colour, not palette indices."""
    width, height, rows = read_png_pixels(path)
    if (width, height) != (240, 160):
        raise SystemExit(f"REFUSED: {path.name} is {width}x{height}, not a native 240x160 frame")
    stride = len(rows[0])
    if stride == width * 3:
        return [[(row[3 * x], row[3 * x + 1], row[3 * x + 2]) for x in range(width)] for row in rows]
    if stride == width * 4:
        return [[(row[4 * x], row[4 * x + 1], row[4 * x + 2]) for x in range(width)] for row in rows]
    raise SystemExit(f"REFUSED: {path.name} has an unexpected row stride {stride}")


def locate_box(rows, art) -> tuple[int, int, int]:
    """Where the box surface sits on screen: the offset with the most art pixels identical."""
    best = (-1, 0, 0)
    for offset_y in range(0, 160 - SURFACE_HEIGHT + 1):
        for offset_x in range(0, 240 - SURFACE_WIDTH + 1):
            matches = 0
            for row in range(SURFACE_HEIGHT):
                capture_row = rows[offset_y + row]
                base = row * SURFACE_WIDTH
                for column in range(SURFACE_WIDTH):
                    if capture_row[offset_x + column] == art[base + column]:
                        matches += 1
            if matches > best[0]:
                best = (matches, offset_x, offset_y)
    return best[1], best[2], best[0]


def painted(rows, art, offset_x: int, offset_y: int) -> dict:
    """The pixels that differ from the art: {position: colour}."""
    out = {}
    for row in range(SURFACE_HEIGHT):
        capture_row = rows[offset_y + row]
        base = row * SURFACE_WIDTH
        for column in range(SURFACE_WIDTH):
            value = capture_row[offset_x + column]
            if value != art[base + column]:
                out[(column, row)] = value
    return out


def _advance_positions(font: Font, text: str, wrap: int) -> list[list[tuple[int, int]]]:
    """The ink pixels each character contributes, in drawing order, wrapped as the engine wraps."""
    lines: list[str] = []
    current = ""
    current_width = 0
    for word in text.split(" "):
        word_width = sum(font.advance(ord(character)) for character in word)
        space = font.advance(ord(" "))
        if current and current_width + space + word_width > wrap:
            lines.append(current)
            current, current_width = word, word_width
        else:
            current += (" " if current else "") + word
            current_width += (space if len(current) > len(word) else 0) + word_width
    if current:
        lines.append(current)

    per_character: list[list[tuple[int, int]]] = []
    y = TEXT_ORIGIN[1]
    for line in lines:
        x = TEXT_ORIGIN[0]
        for character in line:
            glyph = font.glyph(ord(character))
            pixels = []
            if glyph is not None:
                for column in range(glyph.width):
                    for row in range(GLYPH_ROWS):
                        if (glyph.columns[column] >> row) & 1:
                            pixels.append((x + column, y + row))
            per_character.append(pixels)
            x += font.advance(ord(character))
        y += LINE_HEIGHT
    return per_character


#: Wrap widths by box style: with a portrait the text area is four cells wide, without one it is two.
#: Both fitted from captures: 108 with a portrait, 132 without, everything else identical.
WRAP_WIDTHS = (124, 144)


def identify(font: Font, corpus: list[str], engine: set[tuple[int, int]],
             ink: tuple[int, int, int]) -> dict | None:
    """The dialogue line, prefix and wrap width that best explain the engine's ink pixels."""
    best = None
    for wrap in WRAP_WIDTHS:
        found = identify_at_width(font, corpus, engine, wrap)
        if found is not None and (best is None or found["missed"] + found["extra"]
                                  < best["missed"] + best["extra"]):
            best = {**found, "wrap": wrap}
    return best


def identify_at_width(font: Font, corpus: list[str], engine: set[tuple[int, int]],
                      wrap: int) -> dict | None:
    """The best line and prefix at one wrap width."""
    wanted = len(engine)
    best = None
    for text in corpus:
        if not text or len(text) > 400:
            continue
        per_character = _advance_positions(font, text, wrap)
        cumulative: set[tuple[int, int]] = set()
        count = 0
        for index, pixels in enumerate(per_character):
            cumulative = cumulative | set(pixels)
            count += len(pixels)
            if abs(count - wanted) > INK_TOLERANCE:
                continue
            missed = len(engine - cumulative)
            extra = len(cumulative - engine)
            if best is None or missed + extra < best["missed"] + best["extra"]:
                best = {"text": text, "prefix": index + 1, "missed": missed, "extra": extra,
                        "ink_pixels": count}
    return best


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", required=True)
    parser.add_argument("--captures", required=True,
                        help="a directory of native captures, or one file")
    parser.add_argument("--json")
    args = parser.parse_args()
    image = Path(args.rom).read_bytes()
    font = Font(image)
    palette = load_palette(image)
    art_flat = load_box_art(image, BOX_ART_PRIMARY)
    art = [palette[index] for index in art_flat]

    from tools.webfoot import compressed_dialogue as cd
    from tools.webfoot.dialogue_repack import container_pointers, text_of
    from tools.webfoot.formats import webfoot_lz

    streams = {}
    for selector, pointer in container_pointers(image).items():
        if pointer >= ROM_BASE and pointer - ROM_BASE + 8 < len(image):
            streams[selector] = bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)
    corpus = []
    for selector, stream in sorted(streams.items()):
        for record in cd.dialogue_record_inventory(image, selector, len(stream)):
            start, length = record.handle.decoded_start, record.handle.decoded_length
            if start + length <= len(stream):
                corpus.append(text_of(stream, start, length).lstrip("#!"))
    print(f"dialogue corpus: {len(corpus)} line(s)")

    source = Path(args.captures)
    captures = sorted(source.glob("*.png")) if source.is_dir() else [source]
    results = []
    for capture in captures:
        rows = capture_rgb(capture)
        offset_x, offset_y, matches = locate_box(rows, art)
        if matches < SURFACE_WIDTH * SURFACE_HEIGHT * 0.8:
            results.append({"capture": capture.name, "identified": False,
                            "reason": f"no box on screen (best art match {matches})"})
            print(f"{capture.name}: no box (art match {matches})")
            continue
        engine_all = painted(rows, art, offset_x, offset_y)
        counts: dict[tuple[int, int, int], int] = {}
        for colour in engine_all.values():
            counts[colour] = counts.get(colour, 0) + 1
        ink = max(counts, key=counts.get)
        engine = {position for position, colour in engine_all.items() if colour == ink}
        found = identify(font, corpus, engine, ink)
        if found is None:
            results.append({"capture": capture.name, "identified": False,
                            "reason": "no line matches the engine ink count"})
            print(f"{capture.name}: no line matches ({len(engine)} ink pixels)")
            continue
        entry = {"capture": capture.name, "identified": True, "box_at": [offset_x, offset_y],
                 "art_match": matches, "ink_colour": list(ink), "engine_ink_pixels": len(engine),
                 **found}
        entry["pixel_exact"] = found["missed"] == 0 and found["extra"] == 0
        results.append(entry)
        print(f"{capture.name}: {'PIXEL-EXACT' if entry['pixel_exact'] else 'differs'}  "
              f"wrap {found['wrap']}  line {found['text'][:40]!r} prefix {found['prefix']}  "
              f"missed {found['missed']}  extra {found['extra']}")

    exact = sum(1 for entry in results if entry.get("pixel_exact"))
    print(f"\nPIXEL-EXACT: {exact} of {len(results)} capture(s)")
    if args.json:
        Path(args.json).write_text(json.dumps({"results": results, "exact": exact,
                                               "total": len(results)}, indent=2) + "\n",
                                   encoding="utf-8")
        print(f"# wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
