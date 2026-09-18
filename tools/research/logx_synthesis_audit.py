"""Deterministic, read-only audit for LOGX-SYNTHESIS-001.

The LOGExtractor-derived research queue produced ten accepted tickets. This
module is the synthesis ticket's *audit* instrument: it does not decode anything
and it does not require the ROM. It answers three questions a reviewer can check
mechanically:

1. **Does every accepted ticket's canonical record exist** at the path the
   synthesis cites, and is it non-empty?
2. **Do the synthesis deliverables agree with a single machine-readable
   resource matrix**, so prose cannot drift from the table it summarises?
3. **Do superseded LOGExtractor assumptions still appear in live project
   code**, in the places this ticket classified as producible defects rather
   than preserved history?

Consumers
---------
``tests/unit/test_logx_synthesis_audit.py`` imports this module and asserts its
findings. ``python -m tools.research.logx_synthesis_audit`` prints a JSON report.

Rules this module obeys
-----------------------
* read-only; it opens files through :meth:`pathlib.Path.read_text`
* no ROM, no network, no optional dependency (not even ``capstone``)
* deterministic: same tree in, same bytes out
* it never rewrites a document, and it never *fixes* a finding - it reports
* a "superseded" pattern is only reported where the scan scope says the string
  is a defect; historical review/correction records are deliberately out of
  scope because they preserve the superseded wording as evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Iterable, Iterator, Sequence

__all__ = [
    "CANONICAL_FACTS",
    "DOCUMENT_EDITS",
    "READ_SUPPORT_VOCABULARY",
    "AUTHORING_VOCABULARY",
    "EVIDENCE_VOCABULARY",
    "SYNTHESIS_TICKETS",
    "Finding",
    "SupersededPattern",
    "audit_repository",
    "check_documents",
    "check_synthesis_matrix",
    "project_root",
    "superseded_hits",
]


# --------------------------------------------------------------------------- #
# vocabulary and canonical facts
# --------------------------------------------------------------------------- #

#: Evidence labels the whole queue uses. Confidence and readiness are separate
#: vocabularies and must never be substituted for one another (LOGX-SYNTHESIS-001
#: section AE).
EVIDENCE_VOCABULARY = (
    "CONFIRMED",
    "PARTIALLY CONFIRMED",
    "REFUTED",
    "UNRESOLVED",
)

#: Read-support classes from the synthesis read-support matrix (section N).
READ_SUPPORT_VOCABULARY = (
    "TRUSTED",
    "TRUSTED WITH KNOWN FIX",
    "PARTIAL",
    "RESEARCH ONLY",
)

#: Authoring-readiness classes from section O. Deliberately a different
#: vocabulary from evidence: a CONFIRMED structure can still be BLOCKED for
#: authoring because no encoder or allocator exists.
AUTHORING_VOCABULARY = (
    "SAFE NOW",
    "SAFE AFTER BOUNDED FIX",
    "PARTIAL RESEARCH REQUIRED",
    "BLOCKED BY UNKNOWN SEMANTICS",
    "NOT APPLICABLE",
)

#: The ten accepted tickets this synthesis is accountable to, in queue order.
SYNTHESIS_TICKETS: tuple[str, ...] = (
    "LOGX-MAP-RECORD-001",
    "LOGX-MAP-RENDER-001",
    "LOGX-LAYER-001",
    "LOGX-TILE-001",
    "LOGX-CONNECTOR-001",
    "LOGX-CODEC-001",
    "LOGX-CHAR-001",
    "LOGX-SPRITE-001",
    "LOGX-FRAME-001",
    "LOGX-GFXSCAN-001",
)

#: The per-ticket canonical documents the synthesis is required to have read.
#: ``{ticket}`` is substituted in each template. Review records live under
#: ``docs/research/``; archive closeout records under ``docs/research/archive/``;
#: provenance documents under ``docs/research/`` using underscores.
DOCUMENT_EDITS: tuple[str, ...] = (
    "docs/research/{ticket}-review.md",
    "docs/research/archive/{ticket}-COMPLETE.md",
    "docs/research/{provenance}_PROVENANCE.md",
)

#: Populations the ten tickets accepted. Every entry carries the ticket that
#: established it, so the matrix in ``docs/research/LOGX_SYNTHESIS.md`` can be
#: checked against the same source rather than against prose. Values that a
#: later ticket superseded are represented by the surviving figure only; the
#: superseded figure appears in :data:`SUPERSEDED_PATTERNS`.
CANONICAL_FACTS: dict[str, tuple[int, str]] = {
    # value -> (number, owning ticket)
    "mapentry_records": (452, "LOGX-MAP-RECORD-001"),
    "mapentry_stride": (0x38, "LOGX-MAP-RECORD-001"),
    "selector_1_roots": (452, "LOGX-MAP-RENDER-001"),
    "distinct_selector_1_roots": (421, "LOGX-MAP-RENDER-001"),
    "layer_references": (1808, "LOGX-LAYER-001"),
    "unique_layer_records": (1464, "LOGX-LAYER-001"),
    "dominant_layer_references": (1516, "LOGX-LAYER-001"),
    "dominant_layer_records": (1420, "LOGX-LAYER-001"),
    "chunk_grid_cells": (4274, "LOGX-TILE-001"),
    "unique_chunk_targets": (3745, "LOGX-TILE-001"),
    "chunk_decoded_entries": (3834880, "LOGX-TILE-001"),
    "selector_bank_containers": (187, "LOGX-TILE-001"),
    "connector_records": (735, "LOGX-CONNECTOR-001"),
    "connector_directed_links": (694, "LOGX-CONNECTOR-001"),
    "connector_reciprocal_links": (674, "LOGX-CONNECTOR-001"),
    "connector_one_way_links": (20, "LOGX-CONNECTOR-001"),
    "connector_self_links": (3, "LOGX-CONNECTOR-001"),
    "codec_unique_containers": (4324, "LOGX-CODEC-001"),
    "codec_packed_containers": (4322, "LOGX-CODEC-001"),
    "codec_stored_containers": (2, "LOGX-CODEC-001"),
    "appearance_definitions": (232, "LOGX-CHAR-001"),
    "appearance_stride": (0x10, "LOGX-CHAR-001"),
    "sprite_definition_run": (297, "LOGX-SPRITE-001"),
    "sprite_definition_array_slots": (4070, "LOGX-SPRITE-001"),
    "sprite_definition_non_null_slots": (1721, "LOGX-SPRITE-001"),
    "unique_animation_objects": (1017, "LOGX-SPRITE-001"),
    "animation_direction_cells": (13660, "LOGX-FRAME-001"),
    "unique_frame_records": (10980, "LOGX-FRAME-001"),
    "piece_records": (11005, "LOGX-FRAME-001"),
    "multipart_frames": (21, "LOGX-FRAME-001"),
    "unique_sprite_graphics": (7390, "LOGX-FRAME-001"),
    "known_container_corpus": (11715, "LOGX-GFXSCAN-001"),
    "external_scanner_recall": (11513, "LOGX-GFXSCAN-001"),
    "referenced_packed_residuals": (387, "LOGX-GFXSCAN-001"),
    "engine_informed_residuals": (5479, "LOGX-GFXSCAN-001"),
}


def project_root() -> Path:
    """The repository root, derived from this file's own location."""
    return Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------- #
# findings
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Finding:
    """One audit observation.

    ``kind`` is one of ``missing-document``, ``empty-document``,
    ``superseded-string``, ``matrix-mismatch`` or ``matrix-vocabulary``.
    ``production`` is True only when the finding is in live project code that a
    user runs, as opposed to research tooling or documentation.
    """

    kind: str
    location: str
    detail: str
    production: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "location": self.location,
            "detail": self.detail,
            "production": self.production,
        }


@dataclass(frozen=True)
class SupersededPattern:
    """A refuted or superseded LOGExtractor assumption, and where to look.

    ``globs`` are repository-relative globs that are *in scope* for the defect
    check. Historical records that intentionally preserve the superseded text
    are simply not listed. ``regex`` is matched case-sensitively against file
    text unless ``ignore_case`` is set.

    ``severity_production`` distinguishes a hit in live code (a defect the
    roadmap must fix) from a hit that is merely stale wording in a document or
    in research tooling.
    """

    key: str
    regex: str
    summary: str
    globs: tuple[str, ...]
    ignore_case: bool = False
    severity_production: bool = False
    #: Optional guard: a hit is dropped when the matched line also matches this.
    allow_if_line_matches: str | None = None


# --------------------------------------------------------------------------- #
# scan scope
# --------------------------------------------------------------------------- #

#: Live project code. A hit here is a defect the roadmap must fix.
LIVE_CODE_GLOBS: tuple[str, ...] = ("tools/webfoot/**/*.py",)

#: Current canonical documentation and shipped profile/notice data. A hit here
#: is stale current wording, not a wrong result.
CANONICAL_DOC_GLOBS: tuple[str, ...] = (
    "docs/research/GRAPHICS_FORMAT.md",
    "docs/architecture.md",
    "docs/project-format.md",
    "docs/research/SUBSYSTEM_MAP.md",
    "THIRD-PARTY-NOTICES.md",
    "config/roms.yaml",
    "tools/webfoot/data/*.yaml",
)

#: Everything a superseded assumption must not appear in as a surviving claim.
SCAN_GLOBS: tuple[str, ...] = LIVE_CODE_GLOBS + CANONICAL_DOC_GLOBS

#: Superseded LOGExtractor assumptions whose surviving occurrences in live
#: project code or in the *current* canonical documentation are defects. The
#: historical ticket review, provenance and archive records are out of scope by
#: design: they preserve the superseded wording as the evidence trail, and
#: editing them would destroy the record of what was believed and corrected.
SUPERSEDED_PATTERNS: tuple[SupersededPattern, ...] = (
    SupersededPattern(
        key="sprite-run-base-0x6b6bb4",
        # Matches the address digits only, so it covers the file-offset form
        # (``0x6B6BB4``), the full GBA form (``0x086B6BB4``) and any number of
        # leading zeros, and ``ignore_case`` makes it match this repository's own
        # lowercase hex convention. Requiring a literal ``0x0?`` prefix missed the
        # GBA form, because the quantifier consumed the leading zero of ``086``.
        regex=r"6[Bb]6[Bb]B4",
        summary=(
            "0x086B6BB4 is not the sprite-definition pointer-run start; it is "
            "definition id 306's inline animation array"
        ),
        globs=SCAN_GLOBS,
        ignore_case=True,
    ),
    SupersededPattern(
        key="fixed-23-animation-slots",
        regex=r"\b23(?:-|\s)(?:animation\s+)?slots?\b|fixed\s+23\b",
        summary=(
            "the fixed 23-slot animation model is refuted; definition +0x54 is "
            "a count-bounded, variable-length, sparse array"
        ),
        globs=SCAN_GLOBS,
        ignore_case=True,
        # A dated correction note that quotes the refuted model in order to
        # refute it is the historical record, not a surviving claim.
        allow_if_line_matches=r"refuted|superseded|added later|CORRECTED",
    ),
    SupersededPattern(
        key="four-byte-frame-header",
        regex=r"4-byte frame header|frame header is (?:four|4) bytes|"
              r"u32 piece_count\b[^\n]*16-byte",
        summary="the frame header is 0x08 bytes, not 4",
        globs=SCAN_GLOBS,
        ignore_case=True,
    ),
    SupersededPattern(
        key="sixteen-byte-piece",
        regex=r"PIECE_SIZE\s*=\s*16|16-byte (?:piece|OBJ)|\+\s*0x0C\b[^\n]*graphics",
        summary=(
            "the piece stride is 0x0C; piece +0x04 is the packed OBJ attribute "
            "pair and piece +0x08 is the graphics-container word"
        ),
        globs=SCAN_GLOBS,
        severity_production=True,
    ),
    SupersededPattern(
        key="stale-7355",
        regex=r"7,?355",
        summary=(
            "the accepted sprite-graphics container count is 7390; 7355 is the "
            "single-piece-frame subset and must not be the headline figure"
        ),
        globs=SCAN_GLOBS,
    ),
    SupersededPattern(
        key="unknown-header-as-container",
        regex=r"UnknownHeader",
        summary=(
            "UnknownHeader is not an engine container form; the dispatcher "
            "knows only {0, 1, 2}"
        ),
        globs=SCAN_GLOBS,
    ),
    SupersededPattern(
        key="sixty-four-kib-engine-limit",
        regex=r"64\s?KiB[^\n]*(?:engine|format) limit|"
              r"(?:engine|format)[^\n]*64\s?KiB limit",
        summary="no 64 KiB engine or format limit exists",
        globs=SCAN_GLOBS,
        ignore_case=True,
    ),
    SupersededPattern(
        key="zero-first-word-means-empty",
        regex=r"first word[^\n]{0,40}(?:is|means)\s+(?:zero|0)[^\n]{0,40}empty|"
              r"zero[- ]word[^\n]{0,30}empty",
        summary=(
            "a zero first wrapper word selects the stored form; it does not "
            "mean empty"
        ),
        globs=LIVE_CODE_GLOBS,
        ignore_case=True,
    ),
    SupersededPattern(
        key="layer-0x00-numeric-type",
        regex=r"layer[^\n]{0,40}(?:numeric|integer)[^\n]{0,20}type|"
              r"layer type tag|layer type id",
        summary=(
            "layer +0x00 is a Thumb handler/function entry, not a numeric type "
            "tag"
        ),
        globs=LIVE_CODE_GLOBS,
        ignore_case=True,
    ),
    SupersededPattern(
        key="connector-plus-8",
        regex=r"X\s*\+=\s*8|connector[^\n]{0,30}\+\s*8\b",
        summary=(
            "LOGExtractor's +8 connector adjustment has no engine counterpart "
            "and is unresolved"
        ),
        globs=LIVE_CODE_GLOBS,
        severity_production=True,
    ),
    SupersededPattern(
        key="connector-destination-be-u16",
        regex=r"[Bb]ig[- ]endian[^\n]{0,40}destination|"
              r"destination[^\n]{0,40}big[- ]endian",
        summary=(
            "the connector destination is two independent bytes at record "
            "+0x11/+0x12, not a big-endian u16"
        ),
        globs=LIVE_CODE_GLOBS,
        ignore_case=True,
    ),
    SupersededPattern(
        key="0x179764-is-the-atlas-table",
        regex=r"179764[^\n]{0,60}(?:is|as)\s+the\s+(?:global\s+)?atlas|"
              r"atlas table (?:itself|at)\s*`?0x0?179764",
        summary=(
            "0x08179764 is the value stored at root +0x4C and points at a "
            "187-entry selector-bank container table"
        ),
        globs=SCAN_GLOBS,
        ignore_case=True,
    ),
    SupersededPattern(
        key="unbounded-animation-walk",
        regex=r"no field in this header has been shown to bound the list",
        summary=(
            "definition +0x00 does bound the inline animation array; the "
            "next-structure walk is unbounded by construction"
        ),
        globs=SCAN_GLOBS,
        severity_production=True,
    ),
)


#: A line carrying one of these markers is *historical correction context*: it
#: quotes a superseded reading in order to refute it. Such lines are always in
#: scope for reading and never a defect, so every pattern's line filter honours
#: them.
#:
#: **Deliberately narrow.** An earlier revision of this filter also accepted
#: generic hedging phrases such as "must not be" and "no longer", and an
#: independent review demonstrated that a real defect line carrying one of those
#: phrases in a trailing comment went unreported. Only markers that *name the
#: correction act* are accepted now, plus the synthesis documents' own banner
#: identifier.
HISTORICAL_MARKERS = (
    "superseded",
    "refuted",
    "added later",
    "corrected",
    "historical",
    "logx-synthesis-001",
)


def _is_historical(line: str) -> bool:
    """True when a line is correction context rather than a surviving claim."""
    lowered = line.lower()
    return any(marker in lowered for marker in HISTORICAL_MARKERS)


def _iter_files(root: Path, patterns: Sequence[str]) -> Iterator[Path]:
    seen: set[Path] = set()
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            if not path.is_file():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            yield path


def superseded_hits(
    root: Path | None = None,
    patterns: Sequence[SupersededPattern] = SUPERSEDED_PATTERNS,
) -> list[Finding]:
    """Every in-scope surviving occurrence of a superseded assumption."""
    base = root if root is not None else project_root()
    findings: list[Finding] = []
    # A document that carries the synthesis's own supersession banner may quote
    # a superseded figure in its body: the banner is the authoritative statement
    # of the current reading and sits *above* every quotation. That is only
    # acceptable while the banner and its "this list wins" clause are present,
    # and only for the pattern keys the banner actually covers, so the exemption
    # is conditional rather than permanent and does not blanket the document.
    banner_exempt: dict[str, frozenset[str]] = {}
    for relative, keys in BANNER_EXEMPT_KEYS.items():
        path = base / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if all(marker in text for marker in BANNER_REQUIRED_MARKERS):
            banner_exempt[relative] = keys
    for pattern in patterns:
        flags = re.IGNORECASE if pattern.ignore_case else 0
        compiled = re.compile(pattern.regex, flags)
        allow = (
            re.compile(pattern.allow_if_line_matches, flags)
            if pattern.allow_if_line_matches
            else None
        )
        for path in _iter_files(base, pattern.globs):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            relative = path.relative_to(base).as_posix()
            if pattern.key in banner_exempt.get(relative, frozenset()):
                continue
            for number, line in enumerate(text.splitlines(), start=1):
                if not compiled.search(line):
                    continue
                if allow is not None and allow.search(line):
                    continue
                if _is_historical(line):
                    continue
                findings.append(
                    Finding(
                        kind="superseded-string",
                        location=f"{relative}:{number}",
                        detail=f"{pattern.key}: {line.strip()}",
                        production=pattern.severity_production,
                    )
                )
    return findings


# --------------------------------------------------------------------------- #
# canonical record presence
# --------------------------------------------------------------------------- #

def _ticket_documents(ticket: str) -> tuple[str, ...]:
    provenance = re.sub(r"-\d+$", "", ticket).replace("-", "_")
    return tuple(
        template.format(ticket=ticket, provenance=provenance)
        for template in DOCUMENT_EDITS
    )


def check_documents(root: Path | None = None) -> list[Finding]:
    """Every accepted ticket has a non-empty review, closeout and provenance."""
    base = root if root is not None else project_root()
    findings: list[Finding] = []
    for ticket in SYNTHESIS_TICKETS:
        for relative in _ticket_documents(ticket):
            path = base / relative
            if not path.is_file():
                findings.append(
                    Finding(
                        kind="missing-document",
                        location=relative,
                        detail=f"{ticket}: canonical record not found",
                    )
                )
            elif not path.read_text(encoding="utf-8").strip():
                findings.append(
                    Finding(
                        kind="empty-document",
                        location=relative,
                        detail=f"{ticket}: canonical record is empty",
                    )
                )
    return findings


# --------------------------------------------------------------------------- #
# synthesis matrix consistency
# --------------------------------------------------------------------------- #

MATRIX_ROW = re.compile(r"^\|\s*`(?P<resource>[^`]+)`\s*\|(?P<cells>.*)\|\s*$")
MATRIX_SEPARATOR = re.compile(r"^\|[\s:|-]+\|$")
FACT_ROW = re.compile(
    r"^\|\s*`(?P<key>[a-z0-9_]+)`\s*\|\s*(?P<value>\d+)\s*\|\s*`(?P<ticket>[^`]+)`\s*\|"
)


def _cell_values(cells: str) -> list[str]:
    return [cell.strip().strip("`") for cell in cells.split("|")]


def _leading_cell_token(value: str, vocabulary: Sequence[str]) -> str:
    """The vocabulary token at the start of a table cell.

    Cells carry their justification inline (``PARTIAL - the consumer was not
    recovered``), so the audit compares only the leading token. A cell must
    still *begin* with a value of the **given** vocabulary; prose must not be
    classified, and a token from the other vocabulary must not be accepted by
    accident (``PARTIAL`` is a read-support value and the prefix of the
    authoring value ``PARTIAL RESEARCH REQUIRED``, so the vocabulary must be
    supplied by the caller rather than guessed).
    """
    cleaned = value.strip().strip("`").strip()
    for token in sorted(vocabulary, key=len, reverse=True):
        if cleaned.startswith(token):
            return token
    return cleaned


#: Sentinel comments that mark the vocabulary tables in the synthesis document.
#: They exist so the audit does not depend on heading wording, which is prose.
READ_MATRIX_SENTINEL = "<!-- read-support-matrix -->"
AUTHORING_MATRIX_SENTINEL = "<!-- authoring-readiness-matrix -->"

#: Documents that may quote a superseded figure because they carry the
#: synthesis's supersession banner at the top. The exemption is granted only
#: while every one of :data:`BANNER_REQUIRED_MARKERS` is present, so deleting the
#: banner re-arms the scan instead of silently keeping the exemption.
#: Per-document exemptions for a superseded figure that the document itself
#: declares superseded in a banner the audit verifies. Keyed by document, valued
#: by the **only** pattern keys the banner actually covers - so a *new* stale
#: claim in the same document, of any other kind, is still reported. The
#: exemption is granted only while every marker in
#: :data:`BANNER_REQUIRED_MARKERS` is present.
BANNER_EXEMPT_KEYS: dict[str, frozenset[str]] = {
    "docs/research/GRAPHICS_FORMAT.md": frozenset(
        {
            "stale-7355",
            "four-byte-frame-header",
            "sixteen-byte-piece",
            "fixed-23-animation-slots",
            "unbounded-animation-walk",
        }
    ),
}
BANNER_REQUIRED_MARKERS: tuple[str, ...] = (
    "SUPERSEDED STATEMENTS",
    "this\n> list wins",
)


def check_synthesis_matrix(
    root: Path | None = None,
    document: str = "docs/research/LOGX_SYNTHESIS.md",
) -> list[Finding]:
    """The synthesis document's own tables must be self-consistent.

    Three checks, all mechanical:

    * the **canonical fact table** (``| `key` | value | `ticket` |``) must equal
      :data:`CANONICAL_FACTS` exactly, in both directions;
    * the **read-support matrix** must use only :data:`READ_SUPPORT_VOCABULARY`;
    * the **authoring-readiness matrix** must use only
      :data:`AUTHORING_VOCABULARY`.
    """
    base = root if root is not None else project_root()
    path = base / document
    findings: list[Finding] = []
    if not path.is_file():
        return [
            Finding(
                kind="missing-document",
                location=document,
                detail="the synthesis document does not exist",
            )
        ]

    lines = path.read_text(encoding="utf-8").splitlines()

    # --- canonical fact table ------------------------------------------------
    facts: dict[str, tuple[int, str]] = {}
    for number, line in enumerate(lines, start=1):
        match = FACT_ROW.match(line)
        if match is None:
            continue
        facts[match.group("key")] = (
            int(match.group("value")),
            match.group("ticket"),
        )
    for key, (value, ticket) in CANONICAL_FACTS.items():
        found = facts.get(key)
        if found is None:
            findings.append(
                Finding(
                    kind="matrix-mismatch",
                    location=document,
                    detail=f"canonical fact `{key}` is missing from the fact table",
                )
            )
        elif found != (value, ticket):
            findings.append(
                Finding(
                    kind="matrix-mismatch",
                    location=document,
                    detail=(
                        f"canonical fact `{key}` is {found[0]} ({found[1]}) in the "
                        f"document but {value} ({ticket}) in the audit"
                    ),
                )
            )
    for key in sorted(set(facts) - set(CANONICAL_FACTS)):
        findings.append(
            Finding(
                kind="matrix-mismatch",
                location=document,
                detail=f"canonical fact `{key}` is audited by no ticket record",
            )
        )

    # --- vocabulary tables ---------------------------------------------------
    # Located by sentinel comment rather than by heading wording, so the check
    # does not depend on prose. The sentinel enables the table whose rows start
    # on the following lines; the first non-table line disables it again.
    table: str | None = None
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped == READ_MATRIX_SENTINEL:
            table = "read"
            continue
        if stripped == AUTHORING_MATRIX_SENTINEL:
            table = "authoring"
            continue
        if table is None:
            continue
        if not stripped.startswith("|"):
            table = None
            continue
        if MATRIX_SEPARATOR.match(stripped):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or set(cells[0]) <= set("-: "):
            continue
        if table == "read":
            # Column 0 resource, 1 discovery root, 2 structure confidence,
            # 3 field confidence, 4 READ SUPPORT, 5 implementation, 6 bugs,
            # 7 authoring readiness, 8 follow-up.
            if len(cells) < 5:
                continue
            value = _leading_cell_token(cells[4], READ_SUPPORT_VOCABULARY)
            vocabulary = READ_SUPPORT_VOCABULARY
            label = "read support"
        else:
            # Column 0 capability, 1 CLASSIFICATION, 2 why.
            if len(cells) < 2:
                continue
            value = _leading_cell_token(cells[1], AUTHORING_VOCABULARY)
            vocabulary = AUTHORING_VOCABULARY
            label = "authoring readiness"
        if value not in vocabulary:
            findings.append(
                Finding(
                    kind="matrix-vocabulary",
                    location=f"{document}:{number}",
                    detail=f"{label} {value!r} is outside {vocabulary}",
                )
            )
    return findings


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #

def audit_repository(root: Path | None = None) -> dict[str, object]:
    """Run every check and return a JSON-serialisable report."""
    base = root if root is not None else project_root()
    documents = check_documents(base)
    matrix = check_synthesis_matrix(base)
    superseded = superseded_hits(base)
    findings = [*documents, *matrix, *superseded]
    return {
        "root": str(base),
        "tickets": list(SYNTHESIS_TICKETS),
        "counts": {
            "document_findings": len(documents),
            "matrix_findings": len(matrix),
            "superseded_findings": len(superseded),
            "production_findings": sum(
                1 for finding in findings if finding.production
            ),
        },
        "findings": [finding.as_dict() for finding in findings],
    }


def main(argv: Iterable[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "root",
        nargs="?",
        default=None,
        help="repository root (defaults to this checkout)",
    )
    arguments = parser.parse_args(list(argv) if argv is not None else None)
    report = audit_repository(Path(arguments.root) if arguments.root else None)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not report["findings"] else 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
