"""Structural metadata serialization and the no-prose guard.

ASSET-EXPORT-001. The resource library contains no generated prose. Metadata
exists to preserve structure, not to explain it, so this module writes
deterministic JSON and refuses a document that carries a prose field.

**Determinism.** ``json.dumps`` with ``sort_keys=True``, ``indent=2``,
``ensure_ascii=True`` and a trailing newline, encoded UTF-8 with ``\\n`` line
endings. Two runs over the same ROM therefore produce byte-identical metadata.

**The prose guard is enforced, not documented.** :data:`PROSE_KEYS` is the
forbidden key set and :func:`check_structural` walks a document and raises on
any occurrence, at any depth, in any case. It is wired into the writer, so a
prose field cannot reach an artifact even by accident - and the portable test
suite calls the same function over the produced tree.

**Its limit, stated rather than implied.** :data:`PROSE_KEYS` is an explicit
blacklist of *field names*, not a general property of a document. A field that
carries ROM text - a map name, an appearance description - is data with
provenance and passes on purpose, and a newly invented prose field name that
nobody added to the list would pass too. The rule the exporter actually holds to
is that every string it writes either comes from the ROM at a recorded address
or is a numeric, enum or address value the accepted schema defines; the blacklist
is the mechanical backstop for the obvious spellings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

#: Field names that carry generated explanation rather than structure. The list
#: is the ticket's own vocabulary plus the obvious spelling variants.
PROSE_KEYS = frozenset(
    {
        "description",
        "descriptions",
        "notes",
        "note",
        "meaning",
        "interpretation",
        "caption",
        "captions",
        "summary",
        "comment",
        "comments",
        "commentary",
        "explanation",
        "explain",
        "narrative",
        "prose",
        "about",
        "purpose",
        "rationale",
        "title",
        "label",
        "semantic",
        "semantics",
    }
)

#: File extensions that would carry generated prose into the resource library.
FORBIDDEN_DOCUMENT_SUFFIXES = (".md", ".markdown", ".rst", ".txt", ".adoc")


class MetadataError(ValueError):
    """Raised when a metadata document is not structural."""


def check_structural(value: Any, path: str = "$") -> None:
    """Raise :class:`MetadataError` if ``value`` carries a prose field.

    Walks mappings and sequences; a key is matched case-insensitively against
    :data:`PROSE_KEYS`. The path of the offending key is reported so a failure
    names the exact document location.
    """
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise MetadataError(f"{path}: metadata keys must be strings")
            if key.lower() in PROSE_KEYS:
                raise MetadataError(
                    f"{path}.{key}: field name is a prose field; metadata carries "
                    "structural data only"
                )
            check_structural(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            check_structural(item, f"{path}[{index}]")


def dumps(document: Any) -> str:
    """Serialise a structural document to its canonical JSON text."""
    check_structural(document)
    return json.dumps(
        document,
        sort_keys=True,
        indent=2,
        ensure_ascii=True,
        separators=(",", ": "),
    ) + "\n"


def write(path: Path, document: Any) -> int:
    """Write a structural document, returning the bytes written."""
    text = dumps(document)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return len(text.encode("utf-8"))


def csv_rows(header: Iterable[str], rows: Iterable[Iterable[Any]]) -> str:
    """A deterministic CSV document: LF endings, no quoting surprises.

    Values are rendered with ``str``; a comma, quote or newline is quoted and
    doubled, which is the standard rule and keeps a path or hash intact.
    """
    def cell(value: Any) -> str:
        text = "" if value is None else str(value)
        if any(character in text for character in ',\"\n\r'):
            return '"' + text.replace('"', '""') + '"'
        return text

    lines = [",".join(cell(value) for value in header)]
    for row in rows:
        lines.append(",".join(cell(value) for value in row))
    return "\n".join(lines) + "\n"


def write_text(path: Path, text: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return len(text.encode("utf-8"))


def scan_for_prose_files(root: Path) -> tuple[Path, ...]:
    """Every file beneath ``root`` whose suffix suggests generated prose."""
    found: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in FORBIDDEN_DOCUMENT_SUFFIXES:
            found.append(path)
    return tuple(found)


def scan_for_prose_keys(root: Path) -> tuple[tuple[Path, str], ...]:
    """Every JSON document beneath ``root`` that carries a prose field."""
    found: list[tuple[Path, str]] = []
    for path in sorted(root.rglob("*.json")):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            found.append((path, f"unreadable: {exc}"))
            continue
        try:
            check_structural(document)
        except MetadataError as exc:
            found.append((path, str(exc)))
    return tuple(found)
