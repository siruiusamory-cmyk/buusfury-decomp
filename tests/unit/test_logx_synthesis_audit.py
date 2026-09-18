"""Portable tests for the LOGX-SYNTHESIS-001 audit instrument.

These assert the *synthesis's* own invariants, not prose:

* the ten accepted tickets each have a review record, a closeout record and a
  provenance document;
* the canonical fact table in ``docs/research/LOGX_SYNTHESIS.md`` agrees with
  the audit's own ``CANONICAL_FACTS`` in both directions, so a figure cannot be
  added to the document without a cited ticket or dropped silently;
* the read-support and authoring-readiness tables use only their declared
  vocabularies;
* every refuted assumption that survives in live code is one of the **recorded**
  deferred production defects, so a new one cannot appear unnoticed;
* the instrument is deterministic and needs no ROM and no optional dependency.

No ROM, no private input, no proprietary fixture. Everything here reads tracked
documentation, source and config files.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.research import logx_synthesis_audit as audit  # noqa: E402


# --------------------------------------------------------------------------- #
# canonical records
# --------------------------------------------------------------------------- #

def test_all_ten_tickets_have_review_closeout_and_provenance_records():
    findings = audit.check_documents()
    assert findings == [], [finding.as_dict() for finding in findings]


def test_the_queue_is_exactly_the_ten_accepted_tickets():
    assert len(audit.SYNTHESIS_TICKETS) == 10
    assert len(set(audit.SYNTHESIS_TICKETS)) == 10
    for ticket in audit.SYNTHESIS_TICKETS:
        assert ticket.startswith("LOGX-")
        assert audit._ticket_documents(ticket), ticket


def test_every_canonical_fact_is_owned_by_one_of_the_ten_tickets():
    for key, (value, ticket) in audit.CANONICAL_FACTS.items():
        assert isinstance(value, int) and value >= 0, key
        assert ticket in audit.SYNTHESIS_TICKETS, (key, ticket)


# --------------------------------------------------------------------------- #
# the synthesis document
# --------------------------------------------------------------------------- #

def test_synthesis_document_exists_and_states_the_evidence_policy():
    path = audit.project_root() / "docs/research/LOGX_SYNTHESIS.md"
    text = path.read_text(encoding="utf-8")
    assert "UNRESOLVED" in text
    assert "NOT YET SAFE TO AUTHOR" in text
    # confidence and readiness are separate vocabularies
    for label in audit.EVIDENCE_VOCABULARY:
        assert label in text, label
    for label in audit.AUTHORING_VOCABULARY:
        assert label in text, label


def test_synthesis_fact_table_matches_the_audit():
    findings = audit.check_synthesis_matrix()
    assert findings == [], [finding.as_dict() for finding in findings]


def test_synthesis_fact_table_covers_every_canonical_fact():
    """A second, independent reading of the table, not a restatement."""
    path = audit.project_root() / "docs/research/LOGX_SYNTHESIS.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    seen = set()
    for line in lines:
        match = audit.FACT_ROW.match(line)
        if match is not None:
            seen.add(match.group("key"))
            assert match.group("ticket") in audit.SYNTHESIS_TICKETS, line
    assert seen == set(audit.CANONICAL_FACTS)
    assert len(seen) == len(audit.CANONICAL_FACTS)


def test_matrix_sentinels_are_present_so_the_audit_is_not_prose_dependent():
    text = (audit.project_root() / "docs/research/LOGX_SYNTHESIS.md").read_text(
        encoding="utf-8"
    )
    assert audit.READ_MATRIX_SENTINEL in text
    assert audit.AUTHORING_MATRIX_SENTINEL in text


def test_read_and_authoring_vocabularies_do_not_collide_ambiguously():
    """``PARTIAL`` must not be accepted where ``PARTIAL RESEARCH REQUIRED`` fits."""
    assert "PARTIAL" in audit.READ_SUPPORT_VOCABULARY
    assert "PARTIAL" not in audit.AUTHORING_VOCABULARY
    assert (
        audit._leading_cell_token("`PARTIAL RESEARCH REQUIRED`", audit.AUTHORING_VOCABULARY)
        == "PARTIAL RESEARCH REQUIRED"
    )
    assert (
        audit._leading_cell_token("`PARTIAL` - the consumer is unknown", audit.READ_SUPPORT_VOCABULARY)
        == "PARTIAL"
    )
    # a cell must begin with a vocabulary value; prose must not be classified
    assert (
        audit._leading_cell_token("some prose", audit.READ_SUPPORT_VOCABULARY)
        == "some prose"
    )


# --------------------------------------------------------------------------- #
# roadmap
# --------------------------------------------------------------------------- #

def test_roadmap_exists_and_is_grouped_into_phases():
    text = (
        audit.project_root() / "docs/research/POST_LOGX_IMPLEMENTATION_ROADMAP.md"
    ).read_text(encoding="utf-8")
    for phase in (
        "Phase 1 - Correctness and parser repair",
        "Phase 2 - Verified existing-content tools",
        "Phase 3 - Resource writing, allocation and encoding",
        "Phase 4 - `AUTHOR_NEW`",
        "Phase 5 - Advanced / forensic",
    ):
        assert phase in text, phase
    # every proposed ticket is named and each phase names its gating fact
    for ticket in ("FIX-1", "FIX-2", "FIX-3", "TOOLS-3", "WRITE-2", "NEW-4"):
        assert ticket in text, ticket
    assert "Recommended first implementation ticket" in text


# --------------------------------------------------------------------------- #
# superseded-assumption audit
# --------------------------------------------------------------------------- #

#: The superseded assumptions recorded as still present in **live** code by
#: LOGX-SYNTHESIS-001 §11. Each maps to the bounded fix that owns it. A new
#: production hit outside this map fails the audit, which is the point: the
#: synthesis is not allowed to discover a defect and leave it unclassified.
KNOWN_PRODUCTION_DEFECTS: dict[str, frozenset[str]] = {
    "tools/webfoot/formats/sprite_graphics.py": frozenset(
        {"four-byte-frame-header", "sixteen-byte-piece", "stale-7355"}
    ),
    "tools/webfoot/graphics.py": frozenset(
        {"stale-7355", "unbounded-animation-walk"}
    ),
}

#: Documents and modules whose surviving hits are stale *wording* rather than a
#: wrong result, all scheduled under FIX-5 or FIX-3.
KNOWN_STALE_TEXT: frozenset[str] = frozenset(
    {
        "tools/webfoot/formats/sprite_graphics.py",
        "tools/webfoot/formats/webfoot_lz.py",
        "tools/webfoot/build.py",
        "tools/webfoot/cli.py",
        "tools/webfoot/graphics.py",
        "tools/webfoot/atlas_producers/seed.py",
        "tools/webfoot/data/roms.yaml",
    }
)


def _hits_by_file():
    grouped: dict[str, list[audit.Finding]] = {}
    for finding in audit.superseded_hits():
        relative = finding.location.rsplit(":", 1)[0]
        grouped.setdefault(relative, []).append(finding)
    return grouped


def test_no_superseded_assumption_survives_outside_the_recorded_defects():
    unexpected = sorted(set(_hits_by_file()) - KNOWN_STALE_TEXT)
    assert unexpected == [], unexpected


def test_recorded_production_defects_are_exactly_the_ones_the_synthesis_names():
    for relative, allowed in KNOWN_PRODUCTION_DEFECTS.items():
        keys = {
            finding.detail.split(":", 1)[0]
            for finding in _hits_by_file().get(relative, [])
            if finding.production
        }
        assert keys, f"{relative} no longer shows the recorded defect - update the synthesis"
        assert keys <= allowed, (relative, sorted(keys - allowed))


def test_live_code_carries_no_superseded_assumption_of_an_unrecorded_kind():
    """Anything in live code must use a pattern the synthesis already classifies."""
    recorded = {"four-byte-frame-header", "sixteen-byte-piece", "stale-7355",
                "unbounded-animation-walk"}
    for finding in audit.superseded_hits():
        relative = finding.location.rsplit(":", 1)[0]
        if not relative.startswith("tools/webfoot/"):
            continue
        key = finding.detail.split(":", 1)[0]
        assert key in recorded, (relative, key)


def test_the_four_patterns_with_no_surviving_occurrence_stay_absent():
    """These four were refuted and have no hit anywhere; a regression is news."""
    keys = {"sixty-four-kib-engine-limit", "zero-first-word-means-empty",
            "layer-0x00-numeric-type", "connector-destination-be-u16"}
    present = {finding.detail.split(":", 1)[0] for finding in audit.superseded_hits()}
    assert keys & present == set(), sorted(keys & present)


def test_banner_exemption_is_conditional_on_the_banner_being_present():
    path = audit.project_root() / "docs/research/GRAPHICS_FORMAT.md"
    text = path.read_text(encoding="utf-8")
    if "docs/research/GRAPHICS_FORMAT.md" in audit.BANNER_DOCUMENTS:
        for marker in audit.BANNER_REQUIRED_MARKERS:
            assert marker in text, (
                "the supersession banner lost a required marker; the scan "
                "exemption is no longer justified"
            )


# --------------------------------------------------------------------------- #
# determinism and dependency boundary
# --------------------------------------------------------------------------- #

def test_the_audit_is_deterministic():
    import json

    first = json.dumps(audit.audit_repository(), sort_keys=True)
    second = json.dumps(audit.audit_repository(), sort_keys=True)
    assert first == second


def test_the_audit_imports_without_optional_dependencies():
    """The instrument must not require capstone (the CI dependency set)."""
    import importlib

    module = importlib.import_module("tools.research.logx_synthesis_audit")
    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "import capstone" not in source
    assert "from capstone" not in source


def test_superseded_patterns_all_declare_a_scope_and_a_summary():
    for pattern in audit.SUPERSEDED_PATTERNS:
        assert pattern.globs, pattern.key
        assert pattern.summary, pattern.key
        # a regex that cannot compile would silently disable the check
        import re

        re.compile(pattern.regex, re.IGNORECASE if pattern.ignore_case else 0)


def test_unknown_root_is_not_silently_accepted():
    """Pointing the audit at an empty tree must report the missing documents."""
    import tempfile

    with tempfile.TemporaryDirectory() as temporary:
        findings = audit.check_documents(Path(temporary))
        assert findings
        assert all(finding.kind == "missing-document" for finding in findings)
        assert len(findings) == len(audit.SYNTHESIS_TICKETS) * len(audit.DOCUMENT_EDITS)
