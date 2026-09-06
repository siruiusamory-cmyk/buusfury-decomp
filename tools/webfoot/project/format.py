"""Deterministic TOML for the values this project actually authors.

TOOLKIT-002. Reading is `tomllib` from the standard library. Writing is the
~50 lines below, and that asymmetry is deliberate rather than lazy:

**Python has no TOML writer in the standard library.** `tomllib` (3.11+) parses
and does not serialize; the documented answer is a third-party package. This
project has exactly one runtime dependency (PyYAML) and the authored schema is
a closed set - integers, short ASCII strings, booleans, and tables of those.
Adding a dependency to emit that would cost more than emitting it.

**Determinism is the actual requirement, and a general writer does not give it
for free.** A build is reproducible only if the same inputs produce the same
bytes, so key order, integer formatting, string quoting and the trailing
newline all have to be decided by us rather than inherited. Writing the emitter
is how those become properties we assert instead of properties we hope for.
`reproducible-builds.org` names exactly this class of variance - "stable order
for outputs" - as a thing a build must control rather than discover.

The restriction is the safety feature: `dump_toml` refuses any value it cannot
emit unambiguously. If a future ticket needs floats, dates or multi-line
strings, it will get a loud `ProjectFormatError` rather than a subtly
non-round-tripping file.
"""

from __future__ import annotations

import tomllib
from typing import Any, Mapping

#: Characters a bare TOML key may use. Anything else gets quoted, and anything
#: unquotable is refused rather than mangled.
_BARE_KEY = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")


class ProjectFormatError(ValueError):
    """Raised when a value cannot be emitted or parsed unambiguously."""


def _format_key(key: str) -> str:
    if not isinstance(key, str) or not key:
        raise ProjectFormatError(f"table keys must be non-empty strings; got {key!r}")
    if all(character in _BARE_KEY for character in key):
        return key
    return _format_string(key)


#: Characters emitted as a TOML escape rather than literally. Backslash and
#: quote have always been here; newline and tab joined them in TOOLKIT-004,
#: because authored dialogue carries real line breaks. Every other control
#: character stays refused.
_ESCAPES = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\t": "\\t"}


def _format_string(value: str) -> str:
    """Emit a basic TOML string, refusing anything needing exotic escaping.

    Newline and tab are escaped rather than refused: authored dialogue contains
    real line breaks - the Buu's Fury pool has 24 of them - and TOML's basic
    string escapes both unambiguously, so the round trip through `tomllib`
    stays exact. Every other control character is still refused, because
    nothing this project authors contains one and accepting them would mean
    owning escape forms that are never otherwise exercised.
    """
    if any(
        (character < " " or character == "\x7f") and character not in _ESCAPES
        for character in value
    ):
        raise ProjectFormatError(
            "authored strings may not contain control characters other than "
            "newline and tab"
        )
    return '"' + "".join(_ESCAPES.get(c, c) for c in value) + '"'


def _format_value(value: Any) -> str:
    # bool before int: bool is a subclass of int and would otherwise emit as 1.
    if isinstance(value, bool):
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    if isinstance(value, str):
        return _format_string(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_format_value(item) for item in value) + "]"
    raise ProjectFormatError(
        f"cannot emit {type(value).__name__} deterministically; authored data "
        "is limited to integers, strings, booleans and lists of those"
    )


def _emit_table(lines: list[str], path: tuple[str, ...], table: Mapping[str, Any]) -> None:
    """Emit one table: scalars first in insertion order, then subtables.

    Insertion order, NOT sorted order. The caller decides the order of fields
    within a record - `hp` before `level` reads better than alphabetical - and
    determinism only requires that the order be *fixed*, which a dict literal
    already guarantees. Sorting is applied by the caller where the ordering is
    over data (records) rather than over a schema it wrote itself.
    """
    scalars = [(k, v) for k, v in table.items() if not isinstance(v, Mapping)]
    subtables = [(k, v) for k, v in table.items() if isinstance(v, Mapping)]

    if path:
        if lines:
            lines.append("")
        lines.append("[" + ".".join(_format_key(part) for part in path) + "]")
    for key, value in scalars:
        lines.append(f"{_format_key(key)} = {_format_value(value)}")
    for key, value in subtables:
        _emit_table(lines, path + (key,), value)


def dump_toml(document: Mapping[str, Any]) -> str:
    """Serialize `document` to TOML text. Same input, same bytes, always.

    Ends with exactly one newline so the file is well-formed for Git and for
    every diff tool, and so appending nothing is a no-op.
    """
    if not isinstance(document, Mapping):
        raise ProjectFormatError("a TOML document must be a mapping")
    lines: list[str] = []
    _emit_table(lines, (), document)
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def load_toml(text: str) -> dict[str, Any]:
    """Parse TOML text with the standard library, reporting failures as ours."""
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ProjectFormatError(f"invalid TOML: {exc}") from exc
