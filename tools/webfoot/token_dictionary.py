"""Expansion tokens: the dictionary, its blob, and the encoder that uses it.

The engine contract this module is written against is measured and recorded in
``docs/research/DIALOGUE_EXPANSION_TOKEN_DESIGN.md``:

* one stored UTF-16 unit currently composes exactly one glyph and advances
  ``width(glyph) + 1`` pixels;
* the unit window ``0xE000..0xE0FF`` is unused by both text stores (measured
  highest unit is ``0x00EF``), and a unit in it that the engine does *not* know
  is composed as nothing at all while the layout stays stable, because the
  rasteriser refuses every code at or above ``DAT_0803F704 = 0x1D9D``;
* with the hooks installed, a unit ``0xE000 + i`` composes the ``i``-th entry's
  glyphs and advances by the sum of their advances.

So a token buys exactly what the feature exists for: **the same encoded length
with more visible characters.** A two-glyph entry replaces two units with one and
therefore saves one unit, which is what lets authored text longer than the record
it replaces still land on that record's own byte length.

Three rules are deliberate, and each is a refusal rather than a fallback:

* **Ids are generated, never authored.** The document lists expansions in its own
  key order and the build assigns ``0xE000 + index``. No surface accepts a code
  unit from a user, so a token cannot be typed by hand or arrive from a paste.
* **The window is refused in authored text.** ``assert_authored_text`` is what
  keeps that true, and it is the prerequisite of the first build that emits a
  token rather than a later nicety.
* **Everything malformed is refused by name.** A bad entry, an unknown token in a
  stream, an expansion that cannot land on its length: each reports itself, and a
  unit in the window with no entry is never given a fallback rendering.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

MAGIC = b"DTKN"
VERSION = 1
FLAGS = 0
HEADER_BYTES = 12

#: The token window: one page of the Unicode private use area.
TOKEN_BASE = 0xE000
MAX_TOKENS = 0x100

#: Entries are 2..3 glyph units long: up to three glyph codes plus a terminator,
#: a fixed four-halfword stride so the engine's lookup is one shift and one add.
MIN_GLYPHS = 2
MAX_GLYPHS = 3
ENTRY_STRIDE_HALFWORDS = MAX_GLYPHS + 1
TERMINATOR = 0xFFFF

#: The value at which the engine switches to its declared-but-empty wide-glyph
#: class. A glyph code at or above it is never a glyph the rasteriser will draw.
WIDE_CLASS_THRESHOLD = 0xFF

#: Source units the dialogue path reads as an instruction rather than as text:
#: the terminator, the two-unit ink escape, the line break, the soft end, the
#: space that records a wrap checkpoint, and the hyphen join. A token is one unit
#: to the fitter, so it can never honour one of these inside itself, and a space
#: inside a value would silently destroy a wrap opportunity.
STREAM_CONTROLS = frozenset({0x0000, 0x0008, 0x000A, 0x000B, 0x0020, 0x002D})

#: The narrowest line width the fitter is handed on the canonical image: the
#: style record's max width (144 or 128) less the 20 px the pre-reveal branch
#: subtracts. An expansion wider than this could not fit on any line.
LINE_WIDTH_FLOOR = 108


class TokenDictionaryError(ValueError):
    """A dictionary document, blob or token stream this design refuses."""


def glyph_admissible(glyph: int) -> bool:
    """Whether a unit may appear inside an expansion."""
    if not 0 <= glyph <= 0xFFFF:
        return False
    return glyph < WIDE_CLASS_THRESHOLD and glyph not in STREAM_CONTROLS


def is_token_unit(unit: int) -> bool:
    return TOKEN_BASE <= unit < TOKEN_BASE + MAX_TOKENS


def token_unit(index: int) -> str:
    if not 0 <= index < MAX_TOKENS:
        raise TokenDictionaryError(f"token index {index} is outside the window")
    return chr(TOKEN_BASE + index)


def _units(text: str) -> tuple[int, ...]:
    """The stored units of a text, refusing anything the dialogue path cannot hold.

    The dialogue path stores one UTF-16 unit per code point, so a character
    outside the basic multilingual plane is two units and cannot be a glyph.
    """
    if len(text.encode("utf-16le")) // 2 != len(text):
        raise TokenDictionaryError(
            f"{text!r} contains a character outside the basic multilingual plane, "
            f"which the dialogue path cannot store as one unit"
        )
    return tuple(ord(character) for character in text)


def _require_admissible(expansion: str, has_glyph: Callable[[int], bool] | None) -> None:
    units = _units(expansion)
    if not MIN_GLYPHS <= len(units) <= MAX_GLYPHS:
        raise TokenDictionaryError(
            f"expansion {expansion!r} holds {len(units)} glyphs; an entry holds "
            f"{MIN_GLYPHS}..{MAX_GLYPHS}"
        )
    for glyph in units:
        if glyph >= WIDE_CLASS_THRESHOLD:
            raise TokenDictionaryError(
                f"expansion {expansion!r} names {glyph:#06x}, at or above the "
                f"{WIDE_CLASS_THRESHOLD:#04x} wide-class threshold"
            )
        if not glyph_admissible(glyph):
            raise TokenDictionaryError(
                f"expansion {expansion!r} names {glyph:#06x}, which the dialogue path "
                f"reads as an instruction rather than as text"
            )
        if has_glyph is not None and not has_glyph(glyph):
            raise TokenDictionaryError(
                f"expansion {expansion!r} names {glyph:#06x}, which has no glyph record"
            )


@dataclass(frozen=True, slots=True)
class TokenEntry:
    """One generated id and the ordinary glyph units it composes."""

    index: int
    glyphs: tuple[int, ...]

    @property
    def unit(self) -> int:
        return TOKEN_BASE + self.index


@dataclass(frozen=True, slots=True)
class TokenDictionary:
    """A document's expansions, in the key order that fixes their ids."""

    expansions: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.expansions) > MAX_TOKENS:
            raise TokenDictionaryError(
                f"{len(self.expansions)} expansions exceed the {MAX_TOKENS}-token window"
            )
        if len(set(self.expansions)) != len(self.expansions):
            raise TokenDictionaryError("two expansions share the same text")
        for expansion in self.expansions:
            if not expansion:
                raise TokenDictionaryError("an expansion is empty")
            _require_admissible(expansion, None)

    @property
    def count(self) -> int:
        return len(self.expansions)

    def entries(self) -> tuple[TokenEntry, ...]:
        return tuple(TokenEntry(index, _units(text))
                     for index, text in enumerate(self.expansions))

    def unit_for(self, expansion: str) -> str | None:
        for index, text in enumerate(self.expansions):
            if text == expansion:
                return token_unit(index)
        return None

    def keys(self) -> tuple[str, ...]:
        """Expansions longest first, ties by text: the deterministic match order."""
        return tuple(sorted(self.expansions, key=lambda text: (-len(_units(text)), text)))


# --- the document and the blob -------------------------------------------------


def dictionary_from_document(document: object,
                            *, source: str = "document") -> TokenDictionary:
    """Read the project document's ``[[token]]`` tables in file order::

        [[token]]
        text = "Ya"
    """
    if not isinstance(document, Mapping):
        raise TokenDictionaryError(f"{source} is not a TOML table")
    tokens = document.get("token", [])
    if not isinstance(tokens, list):
        raise TokenDictionaryError(f"{source}: 'token' is not a list of tables")
    expansions: list[str] = []
    for position, entry in enumerate(tokens):
        if not isinstance(entry, Mapping) or not isinstance(entry.get("text"), str):
            raise TokenDictionaryError(f"{source}: token {position} needs a string 'text'")
        expansions.append(entry["text"])
    return TokenDictionary(tuple(expansions))


def dictionary_to_document(dictionary: TokenDictionary) -> dict[str, object]:
    return {"token": [{"text": text} for text in dictionary.expansions]}


def build_blob(dictionary: TokenDictionary, *,
               has_glyph: Callable[[int], bool] | None = None) -> bytes:
    """Validate every entry against the image and emit the blob the engine reads."""
    for expansion in dictionary.expansions:
        _require_admissible(expansion, has_glyph)
    blob = bytearray(MAGIC + bytes([VERSION, FLAGS])
                     + dictionary.count.to_bytes(2, "little")
                     + bytes([MAX_GLYPHS, ENTRY_STRIDE_HALFWORDS]) + bytes([0, 0]))
    stride = ENTRY_STRIDE_HALFWORDS
    for entry in dictionary.entries():
        raw = list(entry.glyphs) + [TERMINATOR] * (stride - len(entry.glyphs))
        blob += b"".join(value.to_bytes(2, "little") for value in raw)
    return bytes(blob)


def decode_blob(blob: bytes, *,
                has_glyph: Callable[[int], bool] | None = None) -> TokenDictionary:
    """Decode the blob, refusing anything the builder would not have written."""
    if len(blob) < HEADER_BYTES or blob[:4] != MAGIC:
        raise TokenDictionaryError("dictionary header missing or wrong magic")
    version, flags = blob[4], blob[5]
    count = int.from_bytes(blob[6:8], "little")
    max_glyphs, stride = blob[8], blob[9]
    if version != VERSION or flags != FLAGS:
        raise TokenDictionaryError(f"unsupported dictionary version/flags {version}/{flags}")
    if max_glyphs != MAX_GLYPHS or stride != ENTRY_STRIDE_HALFWORDS:
        raise TokenDictionaryError("dictionary stride or max glyphs is not this design's")
    if count > MAX_TOKENS:
        raise TokenDictionaryError(f"token count {count} is above the {MAX_TOKENS} window")
    if len(blob) != HEADER_BYTES + count * stride * 2:
        raise TokenDictionaryError("dictionary length does not match its header")
    expansions: list[str] = []
    for index in range(count):
        offset = HEADER_BYTES + index * stride * 2
        raw = [int.from_bytes(blob[offset + i * 2:offset + i * 2 + 2], "little")
               for i in range(stride)]
        if TERMINATOR not in raw:
            raise TokenDictionaryError(f"entry {index} has no {TERMINATOR:#06x} terminator")
        glyphs = raw[:raw.index(TERMINATOR)]
        text = "".join(chr(glyph) for glyph in glyphs)
        if not MIN_GLYPHS <= len(glyphs) <= MAX_GLYPHS:
            raise TokenDictionaryError(
                f"entry {index} holds {len(glyphs)} glyphs; an entry holds "
                f"{MIN_GLYPHS}..{MAX_GLYPHS}"
            )
        _require_admissible(text, has_glyph)
        expansions.append(text)
    return TokenDictionary(tuple(expansions))


# --- the encoder and the decoder ----------------------------------------------


def authored_window_problem(text: object, *, what: str = "text") -> str | None:
    """The reason this text may not be authored, or None when it may.

    The predicate form is what the dialogue authoring path needs: it must report
    the refusal through its own error type, per keystroke in the editor and at
    build validation, without this module owning that type.
    """
    if not isinstance(text, str):
        return f"{what} is not a string"
    for character in text:
        if is_token_unit(ord(character)):
            return (
                f"{what} contains the reserved code point U+{ord(character):04X}; the "
                f"window {TOKEN_BASE:#06x}..{TOKEN_BASE + MAX_TOKENS - 1:#06x} is "
                f"generated by the build and cannot be authored"
            )
    return None


def assert_authored_text(text: object, *, what: str = "text") -> None:
    """Refuse the token window in text a person could have typed.

    Without this rule a paste could produce a unit the decoder would silently
    expand, so it is what makes the window safe for authored text at all.
    """
    problem = authored_window_problem(text, what=what)
    if problem is not None:
        raise TokenDictionaryError(problem)


def _match(text: str, position: int, keys: tuple[str, ...]) -> str | None:
    for expansion in keys:
        if text.startswith(expansion, position):
            return expansion
    return None


def encode_text(text: str, dictionary: TokenDictionary) -> str:
    """Replace every expansion occurrence with its token unit.

    Longest match first, non-overlapping, left to right: one pass, and the choice
    at each position does not depend on what follows.
    """
    assert_authored_text(text, what="the text to encode")
    keys = dictionary.keys()
    if not keys:
        return text
    out: list[str] = []
    position = 0
    while position < len(text):
        expansion = _match(text, position, keys)
        if expansion is None:
            out.append(text[position])
            position += 1
            continue
        out.append(token_unit(dictionary.expansions.index(expansion)))
        position += len(expansion)
    return "".join(out)


def decode_text(text: str, dictionary: TokenDictionary) -> str:
    """Expand every token unit back to its glyphs; refuse an unknown one."""
    out: list[str] = []
    for character in text:
        unit = ord(character)
        if not is_token_unit(unit):
            out.append(character)
            continue
        index = unit - TOKEN_BASE
        if index >= dictionary.count:
            raise TokenDictionaryError(
                f"U+{unit:04X} is in the token window but the dictionary declares "
                f"only {dictionary.count} entries, so the engine would draw nothing"
            )
        out.append(dictionary.expansions[index])
    return "".join(out)


def encoded_units(text: str) -> int:
    """The stored unit count, which is what a record's length is measured in."""
    return len(text)


def encode_to_length(text: str, dictionary: TokenDictionary, target_units: int) -> str:
    """Encode exactly ``target_units`` units, or refuse.

    Every entry replaces at least two units with one, so an occurrence saves at
    least one unit. Landing on a target is therefore a choice of *how many*
    occurrences to spend: a left-to-right pass that tokenises until the saving is
    met and then leaves the rest as ordinary text. Text can only be shortened, so
    a target longer than the text is refused rather than padded with invisible
    units the engine would still count.
    """
    assert_authored_text(text, what="the text to encode")
    available = encoded_units(text)
    if available < target_units:
        raise TokenDictionaryError(
            f"{available} units cannot reach the {target_units}-unit target; the text "
            f"is already shorter than the record it replaces"
        )
    saving = available - target_units
    if saving == 0:
        return text
    keys = dictionary.keys()
    out: list[str] = []
    position = 0
    spent = 0
    while position < len(text):
        expansion = _match(text, position, keys) if spent < saving else None
        # A three-glyph entry saves two units, so a match that would overshoot the
        # target is skipped rather than spent.
        if expansion is not None and spent + len(_units(expansion)) - 1 > saving:
            expansion = None
        if expansion is None:
            out.append(text[position])
            position += 1
            continue
        out.append(token_unit(dictionary.expansions.index(expansion)))
        position += len(expansion)
        spent += len(_units(expansion)) - 1
    if spent != saving:
        raise TokenDictionaryError(
            f"the text offers {spent} units of saving but the target needs {saving}; "
            f"this dictionary cannot close the record"
        )
    return "".join(out)


def expansion_advance(expansion: str, width_of: Callable[[int], int]) -> int:
    """``sum(width(glyph) + 1)``: the design's exact expansion advance."""
    return sum(width_of(glyph) + 1 for glyph in _units(expansion))


def check_widths(dictionary: TokenDictionary, width_of: Callable[[int], int]) -> None:
    """Refuse an expansion that cannot fit the narrowest measured line."""
    for expansion in dictionary.expansions:
        advance = expansion_advance(expansion, width_of)
        if advance > LINE_WIDTH_FLOOR:
            raise TokenDictionaryError(
                f"expansion {expansion!r} advances {advance} px, over the "
                f"{LINE_WIDTH_FLOOR} px narrowest line"
            )
