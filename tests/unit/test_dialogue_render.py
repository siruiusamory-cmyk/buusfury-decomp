"""The renderer against the validator's own ink model, at test time from the image.

Three kinds of case, and the difference between them matters:

* a SYNTHETIC image, built here at test time, drives the renderer's own rules - the
  column order, the fitter, the ink escape, the surface size, the refusal to guess a
  scroll window - with no ROM and with no game data committed;
* the CANONICAL corpus is rendered and compared PIXEL FOR PIXEL against the RE Lab
  validator's ink model, which is vendored below rather than imported, so the
  comparison is one measured layout rule written twice by two sessions;
* the native 240x160 captures found under a sibling tree's build directory are located,
  their ink read off the frame, and compared with the render for the same record.

The last two need the canonical image and skip loudly without it. Nothing ROM-derived
is written here: the font, the box art, the palette and the corpus are all decoded from
the image the gate reads.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path

import pytest

from tests.gates import REPOSITORY_ROOT
from tests.rom_support import canonical_rom_bytes, canonical_rom_path
from tools.buufury_text import preview
from tools.webfoot import compressed_dialogue
from tools.webfoot.dialogue_repack import container_pointers, text_of
from tools.webfoot.formats import rgb_png, webfoot_lz

#: The frame a native capture has, and the two box fills the synthetic image uses.
CAPTURE_WIDTH = 240
CAPTURE_HEIGHT = 160
BOX_FILLS = {144: 0x11, 128: 0x22}
#: A portrait operand either exists or it does not, and that is what picks the box.
PORTRAIT_FOR = {144: 1, 128: None}
#: The reference's own tolerance on an ink count, from `dialogue_validate.py`.
INK_TOLERANCE = 3
#: Every advance in the synthetic font, so 16 pixels hold four glyphs.
GLYPH_ADVANCE = 4
FONT_TABLE = 0x100


# --- the reference: the validator's ink model, vendored -----------------------
#
# Copied from `tools/research/dialogue_validate.py` (`_advance_positions` and the word
# wrap it performs) on `origin/ticket/dialogue-preview-validation-2`, commit
# 44a2093037a81deb4340bae3395d390586c28223, read 2026-10-11. That tool reproduced 12 of
# the 13 native captures pixel-exactly. Nothing below is adapted except the three
# placement constants, which are read from `preview` so that both implementations are
# held to the same measurement, and the `font` annotation, which is this tool's own
# reader. Copying rather than importing is the point: the layout rule is then written
# twice, once per session, against the same engine.


def _advance_positions(font, text: str, wrap: int) -> list[list[tuple[int, int]]]:
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
    y = preview.TEXT_ORIGIN[1]
    for line in lines:
        x = preview.TEXT_ORIGIN[0]
        for character in line:
            glyph = font.glyph(ord(character))
            pixels = []
            if glyph is not None:
                for column in range(glyph.width):
                    for row in range(preview.GLYPH_ROWS):
                        if (glyph.columns[column] >> row) & 1:
                            pixels.append((x + column, y + row))
            per_character.append(pixels)
            x += font.advance(ord(character))
        y += preview.LINE_HEIGHT
    return per_character


def _a_word_wider_than_the_limit(font, text: str, limit: int) -> bool:
    """Whether one run of non-space characters is wider than the engine's own limit.

    The copied reference guards its break with `if current and ...`, so a run wider than
    the limit goes on a line by itself and overruns. The engine does not do that: its
    fitter returns WITHOUT advancing when it overflows and has seen no space, read from
    the image's own code at `0x0803DE6A`:

        if (param_3 < iVar4) {          // the width so far exceeds the limit
            if (puVar5 == 0) return;    // no space was seen: stop where it is
            param_4[1] = puVar5;        // otherwise rewind to the last space
            param_4[2] = uVar6;
            return;
        }

    So a run wider than the limit is broken INSIDE the run, and the reference is not a
    model of that branch. The two are not compared there, and the records are counted.
    """
    return any(sum(font.advance(ord(character)) for character in word) > limit
               for word in text.split(" "))


def reference_surface(art: bytes, per_character: list[list[tuple[int, int]]]) -> bytes | None:
    """The box art with the reference's ink pixels painted, as a whole surface.

    None when the reference puts a pixel outside the box. The two models wrap text
    differently above the box's own page: the reference keeps going and the engine's
    fitter stops at four lines, so a record the renderer refuses to draw is a case the
    reference cannot be compared against rather than a disagreement about pixels.
    """
    surface = bytearray(art)
    for pixels in per_character:
        for x, y in pixels:
            if not (0 <= x < preview.SURFACE_WIDTH and 0 <= y < preview.SURFACE_HEIGHT):
                return None
            surface[y * preview.SURFACE_WIDTH + x] = preview.DEFAULT_INK
    return bytes(surface)


# --- a synthetic image, built here --------------------------------------------


@lru_cache(maxsize=None)
def _packed(fill: int) -> bytes:
    """One uniform box surface, packed by the image's own codec."""
    return webfoot_lz.pack(bytes([fill]) * preview.SURFACE_BYTES)


def _write_font(image: bytearray) -> None:
    """A solid glyph for A to Z and a blank one of the same advance for the space."""
    record = FONT_TABLE + 2 * preview.PALETTE_ENTRIES
    for code in (preview.SPACE, *range(0x41, 0x5B)):
        width = GLYPH_ADVANCE - 1
        image[record:record + 2] = width.to_bytes(2, "little")
        for column in range(width + 1):
            at = record + 2 + 2 * column
            ink = 0xFFFF if column < width and code != preview.SPACE else 0
            image[at:at + 2] = ink.to_bytes(2, "little")
        at = FONT_TABLE + 2 * code
        image[at:at + 2] = ((record - FONT_TABLE) // 2).to_bytes(2, "little")
        record += 2 + 2 * (width + 1)
    image[preview.FONT_DESCRIPTOR:preview.FONT_DESCRIPTOR + 4] = \
        (preview.ROM_BASE + FONT_TABLE).to_bytes(4, "little")
    image[preview.FONT_DESCRIPTOR + 4:preview.FONT_DESCRIPTOR + 6] = (11).to_bytes(2, "little")


def synthetic_image() -> bytearray:
    """An image holding a font, the object palette and both box containers at the real offsets."""
    packed = {limit: _packed(fill) for limit, fill in BOX_FILLS.items()}
    size = max(offset + len(packed[limit]) for limit, offset in preview.BOX_ART.items()) + 0x10
    image = bytearray(max(size, preview.OBJ_PALETTE + 2 * preview.PALETTE_ENTRIES))
    for index, word in ((preview.DEFAULT_INK, 0x7FFF), (BOX_FILLS[144], 0x001F),
                        (BOX_FILLS[128], 0x03E0)):
        at = preview.OBJ_PALETTE + 2 * index
        image[at:at + 2] = word.to_bytes(2, "little")
    _write_font(image)
    for limit, offset in preview.BOX_ART.items():
        image[offset:offset + len(packed[limit])] = packed[limit]
    return image


# --- the renderer's own rules, on the synthetic image -------------------------


def test_the_font_decodes_through_the_descriptor() -> None:
    font = preview.decode_font(bytes(synthetic_image()))
    assert font.advance(ord("A")) == GLYPH_ADVANCE
    assert font.advance(preview.SPACE) == GLYPH_ADVANCE
    assert font.glyph(ord("A")) is not None
    # A code below 0x20 has no record: nothing drawn, advance 1.
    assert font.glyph(0x01) is None
    assert font.advance(0x01) == 1
    # A code at or above 0xFF takes the fixed class: the descriptor's advance plus one.
    assert font.glyph(0xFF) is None
    assert font.advance(0xFF) == 12


def test_a_glyph_is_a_column_per_pixel_and_row_zero_is_at_the_top() -> None:
    image = bytes(synthetic_image())
    font = preview.decode_font(image)
    glyph = font.glyph(ord("A"))
    assert glyph is not None
    # Width 3, so four column words: the last is the record's stride, never ink.
    assert glyph.width == 3
    assert glyph.columns == (0xFFFF, 0xFFFF, 0xFFFF, 0)
    surface = preview.render(font, preview.decode_box(image, 128), "A").surface
    x, y = preview.TEXT_ORIGIN
    for column in range(3):
        for row in range(preview.GLYPH_ROWS):
            assert surface[(y + row) * preview.SURFACE_WIDTH + x + column] == preview.DEFAULT_INK
    assert surface[y * preview.SURFACE_WIDTH + x + 3] == BOX_FILLS[128]


def test_the_box_is_an_engine_surface_at_the_engines_own_size() -> None:
    image = bytes(synthetic_image())
    for limit in preview.LAYOUT_LIMITS:
        art = preview.decode_box(image, limit)
        assert len(art) == preview.SURFACE_BYTES
        assert set(art) == {BOX_FILLS[limit]}


def test_the_box_is_chosen_from_the_record_portrait() -> None:
    assert preview.box_for(None) == 128
    assert preview.box_for(0x3F) == 144


def test_a_line_breaks_at_the_last_space_and_never_draws_the_space() -> None:
    image = bytes(synthetic_image())
    font, art = preview.decode_font(image), preview.decode_box(image, 128)
    units = preview.units_of("AB CD")
    # 16 pixels hold four glyphs, and the space records the break point BEFORE it, so
    # the first line is the two glyphs and the space itself is never drawn.
    assert preview.fit_line(font, units, 0, 16) == (0, 2, False)
    assert preview.wrap(font, units, 16) == ((0, 2), (3, 5))
    surface = preview.paint(font, art, units, preview.wrap(font, units, 16))
    x, y = preview.TEXT_ORIGIN
    first = y * preview.SURFACE_WIDTH
    assert surface[first + x] == preview.DEFAULT_INK
    assert surface[first + x + GLYPH_ADVANCE] == preview.DEFAULT_INK
    assert surface[first + x + 2 * GLYPH_ADVANCE] == BOX_FILLS[128]
    # The next line starts at the origin: the space it broke at moved no cursor.
    second = (y + preview.LINE_HEIGHT) * preview.SURFACE_WIDTH
    assert surface[second + x - 1] == BOX_FILLS[128]
    assert surface[second + x] == preview.DEFAULT_INK


def test_the_fitter_stops_where_it_is_when_no_space_was_seen() -> None:
    image = bytes(synthetic_image())
    font = preview.decode_font(image)
    units = preview.units_of("ABCDEF")
    # 12 pixels hold three glyphs; the fourth overflows with no break point to rewind to.
    assert preview.fit_line(font, units, 0, 12) == (0, 3, False)
    assert preview.wrap(font, units, 12) == ((0, 3), (3, 6))
    # A space before the overflow IS the break point, and lands in the same place.
    assert preview.fit_line(font, preview.units_of("ABC DEF"), 0, 12) == (0, 3, False)


def test_the_newline_ends_the_line_and_the_soft_end_ends_the_record() -> None:
    image = bytes(synthetic_image())
    font, art = preview.decode_font(image), preview.decode_box(image, 128)
    assert preview.wrap(font, preview.units_of("A\x0aB"), 128) == ((0, 1), (2, 3))
    surface = preview.render(font, art, "A\x0aB").surface
    x, y = preview.TEXT_ORIGIN
    assert surface[y * preview.SURFACE_WIDTH + x] == preview.DEFAULT_INK
    assert surface[(y + preview.LINE_HEIGHT) * preview.SURFACE_WIDTH + x] == preview.DEFAULT_INK
    # 0x0B ends the record, so nothing after it is drawn.
    assert preview.wrap(font, preview.units_of("A\x0bB"), 128) == ((0, 1),)


def test_the_ink_escape_sets_the_index_and_consumes_its_operand() -> None:
    image = bytes(synthetic_image())
    font, art = preview.decode_font(image), preview.decode_box(image, 128)
    units = preview.units_of("A\x08\x03B")
    assert preview.wrap(font, units, 128) == ((0, 4),)
    surface = preview.render(font, art, "A\x08\x03B").surface
    x, y = preview.TEXT_ORIGIN
    assert surface[y * preview.SURFACE_WIDTH + x] == preview.DEFAULT_INK
    # The escape advances nothing of its own, so B sits one glyph after A at index 3.
    assert surface[y * preview.SURFACE_WIDTH + x + GLYPH_ADVANCE] == 3


def test_a_code_the_font_does_not_carry_advances_and_draws_nothing() -> None:
    image = bytes(synthetic_image())
    font, art = preview.decode_font(image), preview.decode_box(image, 128)
    assert preview.render(font, art, "\x01").surface == art
    # An ink escape with no operand is the last unit: the line stops at the record's
    # own end rather than reading past it.
    x, y = preview.TEXT_ORIGIN
    assert preview.wrap(font, preview.units_of("A\x08"), 128) == ((0, 2),)
    surface = preview.render(font, art, "A\x08").surface
    assert surface[y * preview.SURFACE_WIDTH + x] == preview.DEFAULT_INK


def test_a_record_wider_than_the_box_is_reported_and_never_windowed() -> None:
    image = bytes(synthetic_image())
    font, art = preview.decode_font(image), preview.decode_box(image, 128)
    # 128 pixels hold 32 glyphs, so 200 glyphs need seven lines and the box holds four.
    result = preview.render(font, art, "A" * 200)
    assert result.problem, "a record the box cannot hold was rendered anyway"
    assert result.surface == b""
    assert result.drawn is False
    assert result.lines == 7
    assert result.limit == 128
    # Four lines exactly is still rendered: the refusal is only about the window.
    fits = preview.render(font, art, "A" * 128)
    assert fits.drawn is True
    assert fits.lines == 4


def test_a_bad_descriptor_or_a_short_container_is_refused_by_name() -> None:
    image = synthetic_image()
    image[preview.FONT_DESCRIPTOR:preview.FONT_DESCRIPTOR + 4] = (0).to_bytes(4, "little")
    with pytest.raises(preview.DecodeError, match="names no table"):
        preview.decode_font(bytes(image))
    # A container that decodes to something other than the surface's own size.
    short = synthetic_image()
    stored = webfoot_lz.build_stored(b"\x00" * 100)
    offset = preview.BOX_ART[128]
    short[offset:offset + len(stored)] = stored
    with pytest.raises(preview.DecodeError, match="decodes to 100 bytes"):
        preview.decode_box(bytes(short), 128)


def test_the_renderer_and_the_reference_agree_on_the_synthetic_image() -> None:
    """The two implementations, on inputs the reference models: no control unit.

    A unit below 0x20 is deliberately absent here. The reference prices `0x0A` as one
    advance and the engine ends the line there, so the two models are not expected to
    agree on such a record; that case is covered by its own test above.
    """
    image = bytes(synthetic_image())
    font = preview.decode_font(image)
    for limit in preview.LAYOUT_LIMITS:
        art = preview.decode_box(image, limit)
        for text in ("A", "AB", "AB CD", "A B C", "ABCDEFGH", "A  B", " AB", "A" * 30):
            expected = reference_surface(art, _advance_positions(font, text, limit))
            mine = preview.render(font, art, text, PORTRAIT_FOR[limit])
            assert mine.surface == expected, (limit, text, mine.problem)


# --- the canonical corpus -----------------------------------------------------


@lru_cache(maxsize=None)
def corpus() -> tuple[str, ...]:
    """Every dialogue record's text, read from the canonical image as the validator read it."""
    image = canonical_rom_bytes()
    streams = {}
    for selector, pointer in container_pointers(image).items():
        if pointer >= preview.ROM_BASE and pointer - preview.ROM_BASE + 8 < len(image):
            streams[selector] = bytes(webfoot_lz.unpack(image, pointer - preview.ROM_BASE).data)
    texts = []
    for selector, stream in sorted(streams.items()):
        for record in compressed_dialogue.dialogue_record_inventory(image, selector,
                                                                   len(stream)):
            start, length = record.handle.decoded_start, record.handle.decoded_length
            if start + length <= len(stream):
                texts.append(text_of(stream, start, length).lstrip("#!"))
    return tuple(texts)


def test_the_renderer_matches_the_validator_over_the_whole_corpus() -> None:
    """Every record the box can hold, at both layout limits, pixel for pixel.

    A record the box cannot hold is the scroll case and is counted, not compared: the
    rule that moves the window is not established, and comparing a guessed window with a
    measurement would prove nothing. A record carrying a unit below 0x20 is counted
    separately: the reference prices that unit as one advance and the engine does
    something else with it, so the two models are not expected to agree there.
    """
    image = canonical_rom_bytes()
    font = preview.decode_font(image)
    arts = {limit: preview.decode_box(image, limit) for limit in preview.LAYOUT_LIMITS}
    texts = corpus()
    assert texts, "the canonical image holds no dialogue records"
    exact = 0
    limited = 0
    controls = 0
    oversized = 0
    unbroken = 0
    failures: list[str] = []
    for text in texts:
        units = preview.units_of(text)
        for limit in preview.LAYOUT_LIMITS:
            lines = preview.wrap(font, units, limit)
            if len(lines) > preview.LINES_PER_PAGE:
                limited += 1
                continue
            mine = preview.paint(font, arts[limit], units, lines)
            if _a_word_wider_than_the_limit(font, text, limit):
                unbroken += 1
                continue
            expected = reference_surface(arts[limit], _advance_positions(font, text, limit))
            if expected is None:
                oversized += 1
                continue
            if mine == expected:
                exact += 1
                continue
            if any(unit < 0x20 for unit in units):
                controls += 1
                continue
            differing = sum(1 for left, right in zip(mine, expected) if left != right)
            failures.append(f"limit {limit}: {differing} pixel(s) differ for {text[:48]!r}")
    summary = (f"{len(texts)} record(s): {exact} compared and exact, {limited} too long for the "
               f"box, {oversized} that the reference runs past the box, {unbroken} carrying a "
               f"run wider than the limit, {controls} carrying a unit the reference prices "
               f"differently")
    assert not failures, (f"{summary}; the renderer and the reference disagree:\n"
                          + "\n".join(failures[:10]))
    assert exact >= 50, f"too little was compared: {summary}"
    print(summary)


# --- the native captures found on this machine --------------------------------


def capture_directories() -> tuple[Path, ...]:
    """Build directories under a sibling image worktree that hold native capture frames.

    Derived from this checkout's own location, never written down as a machine path: a
    capture run writes its frames beside the worktree it ran in.
    """
    root = REPOSITORY_ROOT.parent
    found = set()
    for pattern in ("log1-remake*/build/*/shot-*.png",
                    "log1-remake*/build/*/*/shot-*.png"):
        for path in root.glob(pattern):
            found.add(path.parent)
    return tuple(sorted(found))


#: Probe cells spread across the surface on strides that share no factor with either
#: side, so a periodic art pattern cannot alias every one of them at once. A probe is
#: what makes a full search affordable: 7,857 offsets times 10,240 pixels is minutes of
#: pure Python per capture, and 7,857 times 24 is not.
PROBE = tuple(((index * 37) % preview.SURFACE_HEIGHT, (index * 97) % preview.SURFACE_WIDTH)
              for index in range(24))
#: How many of the best-probing offsets are counted in full before one is chosen.
PROBE_FINALISTS = 64


def _matches(frame: bytes, art: bytes, x: int, y: int, step: int) -> int:
    """How many art pixels the frame reproduces at this offset, sampled every `step`.

    `art` is three bytes per pixel, the frame's own colour space: a capture is RGB, and
    comparing it against palette INDICES would compare nothing at all.
    """
    found = 0
    for row in range(0, preview.SURFACE_HEIGHT, step):
        base = row * preview.SURFACE_WIDTH
        screen = 3 * ((y + row) * CAPTURE_WIDTH + x)
        for column in range(0, preview.SURFACE_WIDTH, step):
            at = 3 * (base + column)
            if frame[screen + 3 * column:screen + 3 * column + 3] == art[at:at + 3]:
                found += 1
    return found


def _probe(frame: bytes, art: bytes, x: int, y: int) -> int:
    """How many of the scattered probe cells this offset reproduces."""
    return sum(1 for row, column in PROBE
               if frame[3 * ((y + row) * CAPTURE_WIDTH + x + column):
                        3 * ((y + row) * CAPTURE_WIDTH + x + column) + 3]
               == art[3 * (row * preview.SURFACE_WIDTH + column):
                      3 * (row * preview.SURFACE_WIDTH + column) + 3])


def art_rgb(palette: tuple[tuple[int, int, int], ...], art: bytes) -> bytes:
    """The box surface in the frame's own colour space, which is what a capture shows."""
    return b"".join(bytes(palette[index]) for index in art)


def locate_box(frame: bytes, art: bytes) -> tuple[int, int, int]:
    """Where the box surface sits on screen: the offset reproducing the most art pixels.

    Every offset is probed on scattered cells, the best-probing finalists are then
    counted in full, and the fullest wins. A subsampled ART would have been cheaper and
    is wrong: the instrument test below caught it settling seven pixels away from a box
    that was there, because sampling both dimensions aliases a repeating pattern.
    """
    scored = []
    for offset_y in range(0, CAPTURE_HEIGHT - preview.SURFACE_HEIGHT + 1):
        for offset_x in range(0, CAPTURE_WIDTH - preview.SURFACE_WIDTH + 1):
            scored.append((_probe(frame, art, offset_x, offset_y), offset_x, offset_y))
    scored.sort(key=lambda entry: -entry[0])
    best = (-1, 0, 0)
    for _probe_score, offset_x, offset_y in scored[:PROBE_FINALISTS]:
        found = _matches(frame, art, offset_x, offset_y, 1)
        if found > best[0]:
            best = (found, offset_x, offset_y)
    return best[1], best[2], best[0]


def engine_ink(frame: bytes, art: bytes, x: int, y: int) -> frozenset[tuple[int, int]]:
    """The engine's ink pixels: what differs from the art, by the commonest colour."""
    painted = {}
    for row in range(preview.SURFACE_HEIGHT):
        screen = 3 * ((y + row) * CAPTURE_WIDTH + x)
        base = row * preview.SURFACE_WIDTH
        for column in range(preview.SURFACE_WIDTH):
            at = 3 * (base + column)
            pixel = frame[screen + 3 * column:screen + 3 * column + 3]
            if pixel != art[at:at + 3]:
                painted[(column, row)] = pixel
    if not painted:
        return frozenset()
    ink = Counter(painted.values()).most_common(1)[0][0]
    return frozenset(position for position, colour in painted.items() if colour == ink)


def cumulative_ink(font, text: str) -> list[int]:
    """Ink pixels after each character, which no line break can change."""
    counts = []
    total = 0
    for character in text:
        glyph = font.glyph(ord(character))
        if glyph is not None:
            total += sum(bin(column).count("1") for column in glyph.columns[:glyph.width])
        counts.append(total)
    return counts


def identify(font, counts: list[tuple[str, list[int]]], engine: frozenset[tuple[int, int]],
             art: bytes, limit: int) -> tuple[str, int, bytes] | None:
    """The record, reveal prefix and expected surface that explain the engine's ink.

    The layout is the whole record's, because that is what the engine fits; the drawing
    stops at the revealed unit. The ink count is a pre-filter and can pick a record whose
    count agrees while the text does not, so the pixels decide.
    """
    wanted = len(engine)
    for text, totals in counts:
        candidates = {index + 1 for index, count in enumerate(totals)
                      if abs(count - wanted) <= INK_TOLERANCE}
        if not candidates:
            continue
        per_character = _advance_positions(font, text, limit)
        cumulative: set[tuple[int, int]] = set()
        for index, pixels in enumerate(per_character):
            cumulative |= set(pixels)
            if index + 1 in candidates and cumulative == engine:
                return text, index + 1, reference_surface(art, per_character[:index + 1])
    return None


def test_the_capture_instrument_finds_a_box_that_is_there() -> None:
    """The locator and the ink reader, proven on a frame built here.

    The capture case below can only report what it finds, so a locator that quietly
    stopped working would report a negative and look the same as a missing box. This
    frame is one the instrument must find, at an offset and with an art pattern that no
    other offset reproduces.
    """
    image = bytes(synthetic_image())
    font = preview.decode_font(image)
    palette = preview.decode_palette(image)
    art = bytes(0x11 if ((row // 4) + (column // 7)) % 2 else 0x22
                for row in range(preview.SURFACE_HEIGHT)
                for column in range(preview.SURFACE_WIDTH))
    surface = preview.render(font, art, "AB CD").surface
    offset_x, offset_y = 41, 79
    frame = bytearray(bytes((9, 9, 9)) * (CAPTURE_WIDTH * CAPTURE_HEIGHT))
    for row in range(preview.SURFACE_HEIGHT):
        for column in range(preview.SURFACE_WIDTH):
            colour = bytes(palette[surface[row * preview.SURFACE_WIDTH + column]])
            at = 3 * ((offset_y + row) * CAPTURE_WIDTH + offset_x + column)
            frame[at:at + 3] = colour
    found = locate_box(bytes(frame), art_rgb(palette, art))
    assert found[:2] == (offset_x, offset_y), found
    engine = engine_ink(bytes(frame), art_rgb(palette, art), offset_x, offset_y)
    assert engine, "the frame's own ink was not read at all"
    counts = [("AB CD", cumulative_ink(font, "AB CD"))]
    hit = identify(font, counts, engine, art, 128)
    assert hit is not None, (len(engine), engine)
    assert hit[0] == "AB CD"
    units = preview.units_of("AB CD")
    assert preview.paint(font, art, units, preview.wrap(font, units, 128)) == hit[2]


@pytest.mark.skipif(not capture_directories(),
                    reason="no sibling image worktree holds a build directory of native "
                           "shot-*.png captures on this machine")
def test_the_native_captures_match_the_render() -> None:
    """Locate the box in every capture, read its ink, and hold the render to it.

    These frames are the RE Lab's, taken from a modified image whose font, box art and
    dialogue text are the canonical ones. Nothing is copied into the repository: a frame
    stays where the capture run wrote it.
    """
    directories = capture_directories()
    if canonical_rom_path() is None:
        frames = sum(1 for directory in directories for _ in directory.glob("shot-*.png"))
        pytest.skip(f"{frames} native capture(s) in {len(directories)} build director(ies) "
                    f"were found, and the canonical Buu's Fury image that holds the font, "
                    f"the box art and the corpus they are compared against is not present")
    image = canonical_rom_bytes()
    font = preview.decode_font(image)
    palette = preview.decode_palette(image)
    arts = {limit: preview.decode_box(image, limit) for limit in preview.LAYOUT_LIMITS}
    rgbs = {limit: art_rgb(palette, art) for limit, art in arts.items()}
    texts = corpus()
    counts = [(text, cumulative_ink(font, text)) for text in texts]
    assert texts, "the canonical image holds no dialogue records"
    reproduced: list[str] = []
    reported: list[str] = []
    for directory in directories:
        for path in sorted(directory.glob("shot-*.png")):
            frame, width, height, _alpha = rgb_png.decode_truecolour(path.read_bytes())
            if (width, height) != (CAPTURE_WIDTH, CAPTURE_HEIGHT):
                reported.append(f"{path.name}: {width}x{height}, not a native frame")
                continue
            hit = None
            for limit in preview.LAYOUT_LIMITS:
                x, y, matches = locate_box(frame, rgbs[limit])
                if matches < preview.SURFACE_BYTES * 0.8:
                    reported.append(f"{path.name}: no box at limit {limit} "
                                    f"(best art match {matches})")
                    continue
                engine = engine_ink(frame, rgbs[limit], x, y)
                found = identify(font, counts, engine, arts[limit], limit)
                if found is None:
                    reported.append(f"{path.name}: box at {x},{y} ({matches} art pixels), "
                                    f"no record explains its {len(engine)} ink pixels at "
                                    f"limit {limit}")
                    continue
                text, prefix, expected = found
                units = preview.units_of(text)
                lines = preview.wrap(font, units, limit)
                if len(lines) > preview.LINES_PER_PAGE:
                    reported.append(f"{path.name}: the record needs {len(lines)} lines at "
                                    f"limit {limit}, and the box holds "
                                    f"{preview.LINES_PER_PAGE}")
                    continue
                shown = tuple((start, min(stop, prefix))
                              for start, stop in lines if start < prefix)
                mine = preview.paint(font, arts[limit], units, shown)
                if mine == expected:
                    hit = (limit, x, y, matches, len(engine), prefix)
                    break
                differing = sum(1 for left, right in zip(mine, expected) if left != right)
                reported.append(f"{path.name}: limit {limit}, {differing} pixel(s) differ "
                                f"between the render and the engine's own ink")
            if hit is None:
                continue
            reproduced.append(f"{path.name}: limit {hit[0]}, box at {hit[1]},{hit[2]} "
                              f"({hit[3]} art pixels), {hit[4]} ink pixels over a "
                              f"{hit[5]}-character prefix, reproduced pixel for pixel")
    print("\n".join(reproduced + reported))
    assert reproduced, ("no capture on this machine was located and held to the render; "
                        "report:\n" + "\n".join(reported[:10]))
