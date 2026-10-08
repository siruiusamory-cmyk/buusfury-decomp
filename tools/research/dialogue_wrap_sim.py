"""Offline model of the dialogue line fitter and the one-unit reveal step.

Ticket DIALOGUE-EXPANSION-TOKEN-DESIGN-001, section 11. Read-only, no emulator.

Every rule below is a transcription of an instruction, and the assertions in
`--self-check` fail when the transcription drifts from the measurements the
earlier tickets recorded.

THE ENGINE, AS MEASURED

FUN_0803DE6A (0x0803DE6A) fits one line. param_1 = strip (obj+0x80), param_2 =
the unit pointer, param_3 = max width in pixels, param_4 = a four-word output
{start, cursor, width, end}. Its rules, each with the site:

* leading 0x20 / 0x0A / 0x0B are skipped: 0x0803DE78, 0x0803DE7C, 0x0803DE80
* 0x0000 sets end and returns: 0x0803DE9A
* 0x0020 records the break point (cursor and width so far): 0x0803DEA6
* 0x000A returns, ending the line: 0x0803DEB0
* 0x000B sets end and returns: 0x0803DEB4
* 0x0008 skips TWO units and contributes nothing: 0x0803DEBE / 0x0803DEC2
* width = map[map[c]] below 0xFF, font[1] at or above 0xFF: 0x0803DECA..0x0803DEDE
* overflow (accumulated + width + 1 > max) rewinds to the break point, or stops
  where it is when no break point was seen: 0x0803DEE4..0x0803DEE0
* a fitting unit moves the cursor one unit and adds width + 1: 0x0803DEF2..0x0803DEF6

FUN_0800AE74 (0x0800AE74) reveals. Reached once per reveal step from the
controller 0x0800B0A8, which calls it `font[2]`-derived times per frame (the
typewriter speed). The tail at 0x0800B022..0x0800B094, which is what a token has
to change:

* if the cursor equals the line end, the next line is fitted first: 0x0800AFD0
  (obj+0x14 := out[start]) and 0x0800AFD4 (obj+0x18 := out[cursor])
* 0x0008 consumes its payload unit and writes the ink byte: 0x0800B04C, +4 bytes
* otherwise ONE unit is composed at 0x0800B06A, the advance is recomputed inline
  at 0x0800B07E..0x0800B088, the persistent x is stored at 0x0800B08E and the
  source cursor advances by exactly 2 at 0x0800B092

The advance is `width + 1` in both places, and DIALOGUE_RENDER_PATH.md section 10
recorded twenty consecutive runtime x values; `--self-check` replays them.

WHAT A TOKEN ADDS, AND ONLY THIS

* fitter: a unit in the token range contributes `sum(width(g) + 1)` over its
  expansion and still moves the cursor by ONE unit
* reveal: a unit in the token range composes each glyph of its expansion at
  successive x positions and advances the persistent x by the same total

Nothing else changes, which is what `--corpus` checks: over every record span of
the seven containers the token branch is unreachable, because the highest stored
unit is 0x00EF.

Usage
-----

    python -m tools.research.dialogue_wrap_sim --self-check
    python -m tools.research.dialogue_wrap_sim --rom <canonical.gba> --corpus
    python -m tools.research.dialogue_wrap_sim --self-check --cases
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.research.dialogue_control_codes import (CONTROL_CODES,
                                                   glyph_admissible,
                                                   reserved_ranges)  # noqa: E402

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: The dialogue font struct, read as the reveal step reads it: strip+0x0C holds
#: this address, and the fields are [0] = code -> record-index map, [1] = the fixed
#: advance for codes >= 0xFF, [2] = the wide-code bitmap base. Measured values on
#: the canonical image: 0x0806E05C, 11, 0 (the wide table is declared but empty).
FONT_STRUCT_ROM_ADDRESS = 0x0806EE6C

#: The proposed v1 token window. 0x1D9D is the rasteriser's own upper bound for
#: the wide-code class (DAT_0803F704, read at 0x0803F452): a value at or above it
#: is composed as nothing at all, which is the fail-closed outcome a missing hook
#: should produce. 0xE000..0xF8FF is the Unicode private use area, so no ordinary
#: authoring path can produce one by accident.
EXTENDED_GLYPH_BOUND = 0x1D9D
TOKEN_BASE = 0xE000
MAX_TOKENS = 0x100
#: Fixed entry stride, in halfwords: up to MAX_GLYPHS glyph codes plus a 0xFFFF
#: terminator. Three glyphs cover the useful cases and keep the stride at 8 bytes.
MAX_GLYPHS = 3
ENTRY_STRIDE_HALFWORDS = MAX_GLYPHS + 1
TERMINATOR_GLYPH = 0xFFFF


class TokenError(ValueError):
    """A dictionary or a token stream that the design refuses to accept."""


# --- the font, read from the image the same way the rasteriser reads it --------


@dataclass(frozen=True, slots=True)
class Font:
    """The two-level code -> glyph index -> width table, then the wide class."""

    code_map: dict[int, int]
    map_base: int
    wide_width: int

    def glyph_advance(self, code: int) -> int:
        if code >= 0xFF:
            return self.wide_width + 1
        index = self.code_map.get(code, 0)
        if index == 0:
            return 1
        return self.code_map.get(index, 0) + 1

    def has_glyph(self, code: int) -> bool:
        if code >= 0xFF:
            return code < EXTENDED_GLYPH_BOUND
        return self.code_map.get(code, 0) != 0


def load_font(rom: Path) -> Font:
    image = rom.read_bytes()
    if hashlib.sha256(image).hexdigest() != CANONICAL_SHA256:
        raise SystemExit("not the canonical image")
    fields = [int.from_bytes(
        image[FONT_STRUCT_ROM_ADDRESS - 0x08000000 + index * 4:
              FONT_STRUCT_ROM_ADDRESS - 0x08000000 + index * 4 + 4], "little")
        for index in range(3)]
    map_base, wide, wide_bitmap_base = fields
    if wide_bitmap_base != 0:
        raise SystemExit("this image has a populated wide-code table; the design's "
                         "assumption that codes above 0x1D9D render nothing is void")
    base = map_base - 0x08000000
    # The code map is 256 entries; 0x0100 is already unrelated data (measured).
    code_map = {code: int.from_bytes(image[base + code * 2:base + code * 2 + 2],
                                     "little")
                for code in range(0x100)}
    # The width of a glyph record is reachable through the same map, which is why
    # the map is stored as code -> index AND index -> width in one dict.
    for code in range(0x100):
        index = code_map[code]
        if index:
            offset = base + index * 2
            code_map.setdefault(index, int.from_bytes(image[offset:offset + 2],
                                                      "little"))
    return Font(code_map=code_map, map_base=map_base, wide_width=wide)


# --- the expansion dictionary -------------------------------------------------


@dataclass(frozen=True, slots=True)
class Dictionary:
    """A fixed-stride, 0xFFFF-terminated table of ordinary glyph sequences."""

    entries: tuple[tuple[int, ...], ...]

    def expansion(self, unit: int) -> tuple[int, ...] | None:
        index = unit - TOKEN_BASE
        if 0 <= index < len(self.entries):
            return self.entries[index]
        return None


def decode_dictionary(blob: bytes, font: Font | None = None) -> Dictionary:
    """Decode the proposed production blob; fail closed on anything malformed.

    Header: magic "DTKN" (4 bytes), version (u8), flags (u8), token count (u16),
    max glyphs (u8), stride in halfwords (u8), reserved (u16). Then `count` entries
    of `stride` halfwords each, each entry a run of glyph codes ended by 0xFFFF and
    padded with 0xFFFF. The engine reads no header: it is here so a build can prove
    the blob it wrote is the blob it meant.

    A glyph code must stay below the 0xFF class threshold, must not be a stream
    control (see `glyph_admissible`), and, when a font is supplied, must resolve to
    a real glyph record. Each of those three rules reports itself, so a caller can
    tell a nested token from a formatting operand from a line break.
    """
    if len(blob) < 12 or blob[:4] != b"DTKN":
        raise TokenError("dictionary header missing or wrong magic")
    version, flags, count, max_glyphs, stride = (blob[4], blob[5],
                                                 int.from_bytes(blob[6:8], "little"),
                                                 blob[8], blob[9])
    if version != 1 or flags != 0:
        raise TokenError(f"unsupported dictionary version/flags {version}/{flags}")
    if stride != ENTRY_STRIDE_HALFWORDS or max_glyphs != MAX_GLYPHS:
        raise TokenError("dictionary stride or max glyphs is not this design's")
    if count > MAX_TOKENS:
        raise TokenError(f"token count {count} above the {MAX_TOKENS} window")
    if len(blob) != 12 + count * stride * 2:
        raise TokenError("dictionary length does not match its header")
    entries = []
    for index in range(count):
        offset = 12 + index * stride * 2
        raw = [int.from_bytes(blob[offset + i * 2:offset + i * 2 + 2], "little")
               for i in range(stride)]
        if TERMINATOR_GLYPH not in raw:
            raise TokenError(f"entry {index} has no 0xFFFF terminator")
        glyphs = tuple(raw[:raw.index(TERMINATOR_GLYPH)])
        if not 2 <= len(glyphs) <= MAX_GLYPHS:
            raise TokenError(f"entry {index} holds {len(glyphs)} glyphs")
        for glyph in glyphs:
            if glyph >= 0xFF:
                raise TokenError(f"entry {index} names {glyph:#06x}, at or above "
                                 f"the 0xFF wide-class threshold")
            if not glyph_admissible(glyph):
                raise TokenError(f"entry {index} names {glyph:#06x}, a stream control")
            if font is not None and not font.has_glyph(glyph):
                raise TokenError(f"entry {index} names {glyph:#06x}, which has no "
                                 f"glyph record")
        entries.append(glyphs)
    return Dictionary(tuple(entries))


def encode_dictionary(entries: list[list[int]]) -> bytes:
    count = len(entries)
    if count > MAX_TOKENS:
        raise TokenError("too many tokens")
    blob = bytearray(b"DTKN" + bytes([1, 0]) + count.to_bytes(2, "little")
                     + bytes([MAX_GLYPHS, ENTRY_STRIDE_HALFWORDS]) + bytes([0, 0]))
    for entry in entries:
        raw = list(entry) + [TERMINATOR_GLYPH] * (ENTRY_STRIDE_HALFWORDS - len(entry))
        blob += b"".join(value.to_bytes(2, "little") for value in raw)
    return bytes(blob)


# --- the two engine rules a token changes -------------------------------------


def unit_advance(unit: int, font: Font, dictionary: Dictionary | None) -> int:
    """The fitter's per-unit contribution, with the token branch."""
    if dictionary is not None:
        expansion = dictionary.expansion(unit)
        if expansion is not None:
            return sum(font.glyph_advance(glyph) for glyph in expansion)
    return font.glyph_advance(unit)


@dataclass(frozen=True, slots=True)
class Fit:
    start: int
    cursor: int
    width: int
    end: bool


def fit_line(units: list[int], cursor: int, max_width: int, font: Font,
             dictionary: Dictionary | None = None) -> Fit:
    """FUN_0803DE6A, transcribed. `units` are stored UTF-16 units."""
    limit = len(units)
    while cursor < limit and units[cursor] in (0x20, 0x0A, 0x0B):
        cursor += 1
    start = cursor
    if cursor >= limit or units[cursor] == 0x0000:
        return Fit(start, cursor, 0, True)
    width = 0
    break_cursor = None
    break_width = 0
    position = cursor
    while True:
        if position >= limit:
            return Fit(start, position, width, True)
        unit = units[position]
        if unit == 0x0000:
            return Fit(start, position, width, True)
        if unit == 0x20:
            break_cursor, break_width = position, width
        elif unit == 0x0A:
            return Fit(start, position, width, False)
        elif unit == 0x0B:
            return Fit(start, position, width, True)
        elif unit == 0x08:
            position += 2
            continue
        candidate = width + unit_advance(unit, font, dictionary)
        if max_width < candidate:
            if break_cursor is None:
                return Fit(start, position, width, False)
            return Fit(start, break_cursor, break_width, False)
        position += 1
        width = candidate


def reveal_step(units: list[int], cursor: int, line_end: int, font: Font,
                dictionary: Dictionary | None = None):
    """The tail at 0x0800B022: consume exactly one unit, compose its glyphs.

    Returns (glyph codes composed, new cursor, total advance). The ink changes of
    a 0x0008 escape carry no glyphs and are counted as a zero-glyph step.
    """
    while cursor != line_end:
        unit = units[cursor] if cursor < len(units) else 0x0000
        if unit != 0x08:
            if dictionary is not None:
                expansion = dictionary.expansion(unit)
                if expansion is not None:
                    return (expansion, cursor + 1,
                            sum(font.glyph_advance(g) for g in expansion))
            return ((unit,), cursor + 1, font.glyph_advance(unit))
        cursor += 2
    return ((), cursor, 0)


# --- checks -------------------------------------------------------------------


#: DIALOGUE_RENDER_PATH.md section 10 transcribes the x values of the first twenty
#: compositions of one measured runtime run, and the primary log agrees with every
#: one of them. The document's CODE list is what is wrong: it reads
#: `... 33, 39, 73, 32 ...` where the log reads `... 33, 32, 73, 39 ...`, a
#: transposition of three units. This table is the log's own order, and it is the
#: ORDER that the erratum in the design record corrects; the x values were never in
#: doubt. `--runtime-log` re-reads the log and reports whether its first twenty
#: pairs are these, so the claim is checkable and not merely stated.
TRANSCRIBED_ADVANCES = (
    (0x41, 8), (0x77, 18), (0x77, 28), (0x77, 38), (0x77, 48), (0x2C, 58),
    (0x20, 60), (0x79, 64), (0x65, 70), (0x61, 76), (0x68, 82), (0x21, 88),
    (0x20, 91), (0x49, 95), (0x27, 97), (0x6D, 100), (0x20, 110), (0x74, 114),
    (0x68, 118), (0x65, 124),
)


def runtime_log_check(path: Path, font: Font) -> list[str]:
    """Validate the advance formula against the primary runtime log.

    The log is the observer's own CSV: `frame,COMPOSE,<desc>,<unit>,<x>,<y>,...`.
    Inside one line (a run of equal y) consecutive x values must differ by exactly
    `width(unit) + 1`. Pairs whose next x does not advance start a new run.
    """
    composes = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(",")
        if len(parts) < 6 or parts[1] != "COMPOSE":
            continue
        composes.append((int(parts[3], 0), int(parts[4]), int(parts[5])))
    checks = 0
    mismatches = []
    for (unit, x, y), (next_unit, next_x, next_y) in zip(composes, composes[1:]):
        if next_y != y or next_x <= x:
            continue
        checks += 1
        expected = font.glyph_advance(unit)
        if next_x - x != expected:
            mismatches.append((unit, x, next_x, expected))
    lines = [f"runtime log {path.name}: {len(composes)} compositions, "
             f"{checks} consecutive-advance checks, {len(mismatches)} mismatches"]
    if [(unit, x) for unit, x, _y in composes[:len(TRANSCRIBED_ADVANCES)]] == \
            list(TRANSCRIBED_ADVANCES):
        lines.append(f"the log's first {len(TRANSCRIBED_ADVANCES)} compositions are "
                     f"the transcribed pairs of section 1c, in the log's own order")
    else:
        lines.append("the log's first compositions are NOT the transcribed pairs "
                     "(a different run, or the erratum has drifted)")
    for unit, x, next_x, expected in mismatches[:8]:
        lines.append(f"  unit {unit:#04x} at x {x}: measured advance "
                     f"{next_x - x}, font table says {expected}")
    return lines


def self_check(font: Font, dictionary: Dictionary | None = None) -> list[str]:
    """The advance formula, the two token rules and the dictionary rules."""
    lines = []
    # The transcribed run is asserted, not reported: it is the log's own unit
    # order, so a drift here means the font table and the runtime disagree.
    x = TRANSCRIBED_ADVANCES[0][1]
    for unit, measured in TRANSCRIBED_ADVANCES:
        assert x == measured, f"transcribed run drifted at {unit:#04x}: {x} != {measured}"
        x += font.glyph_advance(unit)
    lines.append(f"transcribed advance run: {len(TRANSCRIBED_ADVANCES)} runtime pairs "
                 f"reproduced from the font table with the log's own unit order")

    dictionary = dictionary or Dictionary(((0x74, 0x68), (0x69, 0x6E, 0x67)))
    token = TOKEN_BASE + 0
    text = [0x61] + [token] + [0x20, 0x62]
    # one stored unit, one consume, one reveal step, two glyphs
    glyphs, cursor, advance = reveal_step(text, 1, len(text), font, dictionary)
    assert glyphs == (0x74, 0x68), glyphs
    assert cursor == 2, cursor
    assert advance == sum(font.glyph_advance(g) for g in (0x74, 0x68))
    lines.append(f"token reveal: one unit -> {len(glyphs)} glyphs, advance "
                 f"{advance}, cursor 1 -> {cursor}")

    fitted = fit_line(text, 0, 1000, font, dictionary)
    wider = fit_line(text, 0, 1000, font, None)
    assert fitted.cursor == wider.cursor == len(text)
    assert fitted.width == wider.width + advance - font.glyph_advance(token)
    lines.append(f"token width in the fitter: {fitted.width} against the "
                 f"unpatched {wider.width} (the engine's wide class would give "
                 f"this unit {font.glyph_advance(token)} px on its own)")

    # A token is ONE unit, so it is placed whole or not at all: a fit that cannot
    # hold it stops exactly at the token, never past it.
    too_narrow = fit_line(text, 1, font.glyph_advance(0x74) - 1, font, dictionary)
    assert too_narrow.cursor == 1 and too_narrow.width == 0, too_narrow
    lines.append("token indivisibility: a fit too narrow for the token stops at "
                 "the token's own unit and places nothing of it")

    # fail closed: an out-of-window unit is not a token
    assert dictionary.expansion(TOKEN_BASE + MAX_TOKENS) is None
    assert dictionary.expansion(0x0041) is None
    lines.append("out-of-window units decode as no token")

    # The dictionary refuses exactly the things section 4 lists. Each case names
    # the rule that must fire and the message that proves it fired, so a check that
    # silently stops working cannot hide behind another one.
    from tools.research.dialogue_control_codes import is_reserved
    assert not is_reserved(0x22) and not is_reserved(0x24) and not is_reserved(0x41), \
        "a leading box-width code must reserve only itself"
    accepted = decode_dictionary(encode_dictionary([[0x22, 0x24], [0x41, 0x42]]), font)
    assert accepted.entries == ((0x22, 0x24), (0x41, 0x42))

    refusals = (
        ([[0x41, 0x0A]], "a stream control", "a line break inside a value"),
        ([[0x41, 0x20]], "a stream control", "a space inside a value"),
        ([[0x41, 0xFF]], "wide-class threshold", "the 0xFF class threshold"),
        ([[0x41, TOKEN_BASE + 1]], "wide-class threshold", "a nested token"),
        ([[0x41, 0x02]], "no glyph record", "a formatting operand"),
        ([[0x41]], "holds 1 glyphs", "a single-glyph entry"),
        ([[0x41, 0x42, 0x43, 0x44]], "terminator",
         "four glyphs, which cannot carry a terminator in this stride"),
    )
    for bad, expected, label in refusals:
        try:
            decode_dictionary(encode_dictionary(bad), font)
        except TokenError as error:
            assert expected in str(error), (bad, str(error), expected)
            continue
        raise AssertionError(f"dictionary accepted {label}: {bad}")
    no_terminator = bytearray(encode_dictionary([[0x41, 0x42]]))
    for index in range(ENTRY_STRIDE_HALFWORDS):
        no_terminator[12 + index * 2:12 + index * 2 + 2] = (0x41).to_bytes(2, "little")
    try:
        decode_dictionary(bytes(no_terminator), font)
    except TokenError as error:
        assert "terminator" in str(error), str(error)
    else:
        raise AssertionError("dictionary accepted an entry with no terminator")
    lines.append("dictionary validation refuses, each on its own rule: stream "
                 "controls, the 0xFF threshold, glyphless operands, nested tokens, "
                 "single-glyph and over-long entries, a missing terminator")
    lines.append("dictionary validation accepts real glyphs a leading box-width "
                 "command could not reserve: 0x22 '\"' and 0x24 '$'")

    # a token wider than the line cannot stall: it is a word like any other
    huge = decode_dictionary(encode_dictionary([[0x6D, 0x77, 0x57]]), font)
    stalled = fit_line([TOKEN_BASE], 0, 4, font, huge)
    assert stalled.cursor == 0 and stalled.width == 0, stalled
    lines.append("a token wider than the whole line reproduces the engine's "
                 "long-word behaviour: the fit stops before it (which is why the "
                 "build must bound expansion width)")

    # The failure the wrap hook exists to prevent: a WIDE expansion whose stored
    # unit the unpatched engine prices at the fixed 12 px, so the line is filled
    # as if it fitted and the token then overruns the measured line end.
    wide = Dictionary(((0x57, 0x57),))          # 'WW' = 14 + 14 = 28 px
    line = [0x74, 0x68, 0x65, TOKEN_BASE, 0x6D]  # "the" + token + "m"
    unpatched = fit_line(line, 0, 30, font, None)
    patched = fit_line(line, 0, 30, font, wide)
    assert unpatched.cursor == 4 and patched.cursor == 3, (unpatched, patched)
    assert font.glyph_advance(TOKEN_BASE) == font.wide_width + 1
    lines.append(f"wrap integration: the same line at max 30 px ends at unit "
                 f"{unpatched.cursor} unpatched (token priced at "
                 f"{font.glyph_advance(TOKEN_BASE)} px) and at unit "
                 f"{patched.cursor} patched (token priced at 28 px), so without the "
                 f"wrap hook the token overruns the line by 26 px")
    return lines


#: Section 11's representative cases. (name, units, max width). The widths are the
#: measured effective line widths: the style record holds 144 px (style 0) and
#: 128 px (style 1) and FUN_0800AE74 subtracts 20 px while obj+0x28 == 0, so 124
#: and 108 are what the fitter is actually handed on the canonical image.
#: The dictionary is 0 = ('t','h') 10 px, 1 = ('i','n','g') 14 px, 2 = ('W','W') 28 px.
def cases() -> list[tuple[str, list[int], int]]:
    A, B, C = TOKEN_BASE, TOKEN_BASE + 1, TOKEN_BASE + 2
    return [
        ("expansion mid-word", [0x74, 0x68, A, 0x65, 0x20, 0x74, 0x68, B], 124),
        ("expansion at a line boundary", [0x74, 0x68, 0x65, 0x20, A, 0x72, 0x65], 40),
        ("expansion before a space", [0x74, A, 0x20, 0x74, 0x68, 0x65], 124),
        ("expansion after a space", [0x74, 0x20, A, 0x74, 0x68, 0x65], 124),
        ("two expansions on one line", [A, 0x20, B, 0x20, C, 0x20, A], 124),
        ("narrow glyphs inside", [0x69, A, 0x6C, 0x6C], 124),
        ("wide glyphs inside", [0x57, A, 0x4D, 0x57], 124),
        ("wide expansion that looked narrow", [0x74, 0x68, 0x65, C, 0x6D, 0x20, 0x61], 40),
        ("expansion before a control code",
         [0x74, A, 0x000A, 0x74, 0x68], 124),
        ("expansion before a formatting escape", [0x74, A, 0x0008, 0x0002, 0x74], 124),
        ("expansion on the narrower style", [0x74, 0x68, 0x65, 0x20, C, 0x20, A, 0x6D], 108),
    ]


def run_cases(font: Font, dictionary: Dictionary) -> list[str]:
    lines = []
    for name, units, width in cases():
        plain = fit_line(units, 0, width, font, None)
        patched = fit_line(units, 0, width, font, dictionary)
        verdict = "same line end" if plain.cursor == patched.cursor else "line end moved"
        lines.append(f"{name:38} max {width:3d}  stored-look width "
                     f"{plain.width:3d} ends at {plain.cursor:2d}  |  expanded "
                     f"{patched.width:3d} ends at {patched.cursor:2d}  ({verdict})")
    return lines


def corpus_check(rom: Path, font: Font, dictionary: Dictionary) -> list[str]:
    """No stored unit of the shipped corpus is in the token window."""
    from tools.webfoot.compressed_dialogue import dialogue_record_inventory
    from tools.webfoot.formats.webfoot_lz import unpack

    image = rom.read_bytes()
    if hashlib.sha256(image).hexdigest() != CANONICAL_SHA256:
        raise SystemExit("not the canonical image")
    highest = 0
    units_seen = 0
    spans = 0
    selectors = 0
    for selector in range(8):
        slot = 0x007B5B64 + selector * 4
        word = int.from_bytes(image[slot:slot + 4], "little")
        if not 0x08000000 <= word < 0x08000000 + len(image):
            continue
        container = unpack(image, word - 0x08000000)
        if not container.declared_size:
            continue
        selectors += 1
        data = container.data
        for record in dialogue_record_inventory(image, selector, len(data)):
            handle = record.handle
            start, length = handle.decoded_start, handle.decoded_length
            units = [data[offset] | (data[offset + 1] << 8)
                     for offset in range(start, min(start + length, len(data)) - 1, 2)]
            spans += 1
            units_seen += len(units)
            if units:
                highest = max(highest, max(units))
    lines = [f"corpus: {selectors} containers, {spans} record spans, "
             f"{units_seen} stored units, highest value {highest:#06x}"]
    if highest >= TOKEN_BASE:
        raise AssertionError("the shipped corpus already uses the token window")
    lines.append(f"token window {TOKEN_BASE:#06x}..{TOKEN_BASE + MAX_TOKENS - 1:#06x} "
                 f"is above the highest stored unit, and above the rasteriser's "
                 f"wide-class bound {EXTENDED_GLYPH_BOUND:#06x}")
    lines.append(f"reserved ranges a token must avoid: "
                 + ", ".join(f"{low:#06x}..{high - 1:#06x} {name}"
                             for low, high, name in reserved_ranges()
                             if not (name.startswith("box-width")
                                     or name == "formatting-payload")))
    lines.append(f"control values that carry a payload unit: "
                 + ", ".join(f"{code.value:#06x} ({code.name})"
                             for code in CONTROL_CODES if code.payload_units))
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path,
                        default=ROOT / "roms" / "Dragon Ball Z - Buu's Fury (U).gba")
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--cases", action="store_true")
    parser.add_argument("--corpus", action="store_true")
    parser.add_argument("--runtime-log", type=Path,
                        help="observer CSV whose COMPOSE rows validate the advance")
    args = parser.parse_args()
    if not (args.self_check or args.cases or args.corpus or args.runtime_log):
        args.self_check = args.cases = True

    font = load_font(args.rom)
    dictionary = Dictionary(((0x74, 0x68), (0x69, 0x6E, 0x67), (0x57, 0x57)))
    if args.self_check:
        for line in self_check(font, dictionary):
            print("PASS  " + line)
    if args.cases:
        for line in run_cases(font, dictionary):
            print(line)
    if args.corpus:
        for line in corpus_check(args.rom, font, dictionary):
            print(line)
    if args.runtime_log:
        for line in runtime_log_check(args.runtime_log, font):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
