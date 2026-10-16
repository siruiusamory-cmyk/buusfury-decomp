"""The dialogue decoder's special source-unit values, with the site that proves each.

Ticket DIALOGUE-EXPANSION-TOKEN-DESIGN-001, section 1. This module is the
machine-readable half of the source-unit census: `classify(value)` names what the
engine does with a unit, and every entry cites the instruction that does it.

Rules for this table, so it does not decay into folklore:

* One entry per measured site. A value is "special" only if an instruction
  COMPARES against it on the dialogue path; adjacency in the corpus is not
  evidence of a payload.
* `payload_units` is the number of EXTRA stored units the decoder consumes after
  the code. A leading box-width command consumes only itself, so its payload is 0;
  the numeric span a value reserves is always one value, because the following
  stored unit is a unit of its own and not "the next value".
* `leading_only` marks a comparison that only runs on the FIRST unit of a string
  (the box-width commands), so the value is not reserved mid-text by it.
* A value with no entry is reported as UNCLASSIFIED. Absence of a glyph record is
  not a class; it is a font fact and belongs to the census, not here.

Evidence vocabulary follows docs/research-conventions.md: MEASURED (observed at
runtime) and STATIC (read from the image) are kept distinct. Every entry published
here is STATIC, because a reader can re-read the instruction from the canonical
image. Where an earlier session also observed the site at runtime, that log is not
part of this repository, so the label does not claim it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ControlCode:
    value: int
    name: str
    payload_units: int
    evidence: str
    site: str
    leading_only: bool = False


#: Every equality comparison on a source-unit value on the dialogue path.
CONTROL_CODES: tuple[ControlCode, ...] = (
    ControlCode(
        0x0000, "terminator", 0, "STATIC",
        "0x0803DE6E and 0x0803DE9A test a unit for zero and set out[3] = 1; "
        "0x0800AEB2 tests the first unit at obj+0x18. The decoded containers hold "
        "no NUL halfword at all (census, whole-container count 0); the NUL the "
        "fitter can see is written by the record copier at 0x08012272, one unit "
        "past the copied span.",
    ),
    ControlCode(
        0x0002, "formatting-payload", 0, "STATIC+census",
        "No enumerated instruction compares it. In the whole container it occurs "
        "164 times and every 0x0008 escape (328 of them) consumes exactly one of "
        "{0x0002, 0x0007} as its payload, so it is the ink value the 0x0800B04C "
        "store writes to strip+3.",
    ),
    ControlCode(
        0x0007, "formatting-payload", 0, "STATIC+census",
        "The other payload value; same evidence as 0x0002 (164 occurrences).",
    ),
    ControlCode(
        0x0008, "inline-formatting", 1, "STATIC",
        "0x0800AE20, 0x0800B046 and 0x0803DEBE compare a unit against 8. The "
        "reveal loop stores the next halfword into strip+3 at 0x0800B04C and "
        "advances the source cursor by four bytes at 0x0800B052; the fitter skips "
        "two units at 0x0803DEC2; the dispatcher writes obj+0x83 at 0x0800AE30.",
    ),
    ControlCode(
        0x000A, "line-break", 0, "STATIC",
        "0x0800AE06 (dispatcher: advance one unit) and 0x0803DEB0 (fitter: "
        "return, ending the line). Also skipped as a leading unit at 0x0803DE7C.",
    ),
    ControlCode(
        0x000B, "soft-end", 0, "STATIC",
        "0x0803DEB4 sets out[3] = 1 and returns; also skipped as a leading unit "
        "at 0x0803DE80.",
    ),
    ControlCode(
        0x0020, "space-break-point", 0, "STATIC",
        "0x0803DEA6 records the break point; 0x0800AE4C/0x0800AE58 eat spaces "
        "after a hyphen.",
    ),
    ControlCode(
        0x0021, "box-width-40", 0, "STATIC",
        "0x080120E4 compares the first unit against 0x21 and 0x080120EC advances "
        "the text pointer by one unit",
        leading_only=True,
    ),
    ControlCode(
        0x0023, "box-width-120", 0, "STATIC",
        "0x080120FC compares the first unit against 0x23 and 0x08012102 advances "
        "the text pointer by one unit",
        leading_only=True,
    ),
    ControlCode(
        0x002D, "hyphen-join", 0, "STATIC",
        "0x0800AE42: advance one unit, then eat the following 0x20 units and "
        "return 1.",
    ),
    ControlCode(
        0x0040, "box-width-80", 0, "STATIC",
        "0x080120F0 compares the first unit against 0x40 and 0x080120F8 advances "
        "the text pointer by one unit",
        leading_only=True,
    ),
    ControlCode(
        0x005E, "reveal-start", 0, "STATIC",
        "0x0800B16E compares a unit against 0x5E in the builder's default "
        "obj+0xB4 handler: it advances one unit, sets obj+0x28 = 1 and installs "
        "the reveal controller 0x0800B0A9.",
    ),
)


_BY_VALUE = {code.value: code for code in CONTROL_CODES}

#: Values that must never be allocated to an expansion token, whatever the
#: encoding: a decoder site already tests the value. The box-width commands are
#: included even though they only fire on the first unit, because a token that can
#: occur anywhere must not be confused for one by a reader.
RESERVED_VALUES = frozenset(_BY_VALUE)

#: Values a token's own glyph sequence must not contain. Each is re-read as a
#: stream control by some decoder (0x0000 terminator, 0x0008 escape, 0x000A line
#: break, 0x000B soft end) or is the fitter's own break or join point (0x0020,
#: 0x002D), which a token cannot honour internally: the fitter never sees inside an
#: expansion, so a space there destroys a wrap opportunity silently. The positional
#: commands (0x0021, 0x0023, 0x0040) and the pre-reveal command (0x005E) are NOT in
#: this set: they carry no meaning once the unit sits inside an expansion.
STREAM_CONTROLS = frozenset({0x0000, 0x0008, 0x000A, 0x000B, 0x0020, 0x002D})


def glyph_admissible(value: int) -> bool:
    """Whether a value may appear inside an expansion before the font is read.

    The caller must also require that the value has a glyph record; that is a font
    fact and lives in the census and the simulator, not here.
    """
    return value < 0xFF and value not in STREAM_CONTROLS


def code_for(value: int) -> ControlCode | None:
    return _BY_VALUE.get(value)


def classify(value: int) -> str:
    code = _BY_VALUE.get(value)
    if code is not None:
        return code.name
    if value >= 0x100:
        return "extended-or-token-class"
    if 0x20 <= value < 0x7F:
        return "unclassified-printable"
    return "unclassified-nonprintable"


def reserved_ranges() -> tuple[tuple[int, int, str], ...]:
    """The half-open numeric span each code's OWN value occupies.

    Always one value wide. A payload is a separate stored unit whose value the code
    does not constrain, so it is reported by `payload_units` on the entry rather
    than by widening this span.
    """
    return tuple((code.value, code.value + 1, code.name)
                 for code in sorted(CONTROL_CODES, key=lambda item: item.value))


def is_reserved(value: int) -> bool:
    return any(low <= value < high for low, high, _name in reserved_ranges())
