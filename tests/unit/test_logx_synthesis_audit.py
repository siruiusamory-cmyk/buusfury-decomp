"""Portable tests for the LOGX-SYNTHESIS-001 audit instrument.

These assert the *synthesis's* own invariants, not prose:

* the ten accepted tickets each have a review record, a closeout record and a
  provenance document;
* the canonical fact table in ``docs/research/LOGX_SYNTHESIS.md`` agrees with
  the audit's own ``CANONICAL_FACTS`` in both directions, so a figure cannot be
  added to the document without a cited ticket or dropped silently;
* the read-support and authoring-readiness tables use only their declared
  vocabularies;
* every refuted assumption that survives is in a **recorded** location, so a new
  one cannot appear unnoticed - the recorded defects themselves are expected to
  remain until their Phase 1 fixes land, and a *disappearance* is also a finding;
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
    # every proposed item is named and each phase names its gating fact
    for item in ("FIX-1", "FIX-2", "FIX-3", "TOOLS-3", "WRITE-2", "NEW-4"):
        assert item in text, item
    assert "Recommended first implementation item" in text


# --------------------------------------------------------------------------- #
# superseded-assumption audit
# --------------------------------------------------------------------------- #

#: The superseded assumptions recorded as still present in **live** code by
#: LOGX-SYNTHESIS-001 §11. Each maps to the bounded fix that owns it. A new
#: production hit outside this map fails the audit, which is the point: the
#: synthesis is not allowed to discover a defect and leave it unclassified.
#:
#: **FIX-2 and FIX-5 were executed by EVIDENCE-RISK-DEBT-001**, so
#: `sprite_graphics.py` no longer appears here at all: its four recorded
#: production defects (the 4-byte frame header, the 16-byte piece stride, the
#: stale 7,355 headline and the `+0x0C` graphics word) are gone from live code,
#: and a reappearance is now a regression rather than a known state. What remains
#: is `unbounded-animation-walk`, which is a recorded defect owned by roadmap
#: FIX-3 (the count-bounded animation traversal) and is deliberately not part of
#: this ticket's scope.
KNOWN_PRODUCTION_DEFECTS: dict[str, frozenset[str]] = {
    "tools/webfoot/graphics.py": frozenset({"unbounded-animation-walk"}),
}

#: Files the corrected layout and figures must have left clean. A hit here is a
#: regression of FIX-2 or FIX-5 rather than a recorded state.
FIXED_BY_EVIDENCE_RISK_DEBT_001: frozenset[str] = frozenset(
    {
        "tools/webfoot/formats/sprite_graphics.py",
        "tools/webfoot/formats/webfoot_lz.py",
        "tools/webfoot/data/roms.yaml",
        "config/roms.yaml",
        "docs/architecture.md",
        "docs/project-format.md",
        "docs/research/SUBSYSTEM_MAP.md",
        "THIRD-PARTY-NOTICES.md",
    }
)

#: Documents and modules whose surviving hits are stale *wording* rather than a
#: wrong result. This is the audit's complete expected finding set, and
#: :func:`test_the_recorded_stale_text_set_is_exactly_what_remains` holds it to
#: exactly that: after EVIDENCE-RISK-DEBT-001 executed FIX-2 and FIX-5, the only
#: file left is `graphics.py`, whose single hit is the FIX-3-owned
#: `unbounded-animation-walk` wording.
KNOWN_STALE_TEXT: frozenset[str] = frozenset(
    {
        "tools/webfoot/graphics.py",
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


def test_the_recorded_stale_text_set_is_exactly_what_remains():
    """The map must not drift in either direction.

    An unexpected file is a new defect; a recorded file with no hit left is a map
    that has stopped describing the tree, which is how a fixed defect stays
    "known" long after it was repaired.
    """
    assert set(_hits_by_file()) == KNOWN_STALE_TEXT, sorted(
        set(_hits_by_file()) ^ KNOWN_STALE_TEXT
    )


def test_recorded_production_defects_are_exactly_the_ones_the_synthesis_names():
    for relative, allowed in KNOWN_PRODUCTION_DEFECTS.items():
        keys = {
            finding.detail.split(":", 1)[0]
            for finding in _hits_by_file().get(relative, [])
            if finding.production
        }
        assert keys, f"{relative} no longer shows the recorded defect - update the synthesis"
        assert keys <= allowed, (relative, sorted(keys - allowed))


def test_the_corrected_files_no_longer_carry_a_superseded_assumption():
    """FIX-2 and FIX-5 are executed, so these files' hits must be gone.

    This asserts the *negative* proof mechanically: the refuted 4-byte/16-byte
    layout and the stale 7,355 headline must not be readable as current anywhere
    the correction touched. Reintroducing one is a regression, and the audit
    reports it as a new defect rather than as a recorded state.
    """
    regressed = sorted(set(_hits_by_file()) & FIXED_BY_EVIDENCE_RISK_DEBT_001)
    assert regressed == [], regressed


def test_a_population_qualified_7355_line_is_not_reported_as_stale(tmp_path):
    """FIX-5's own prescribed wording must survive the scan.

    The replacement rule is "state the population", so a line that names the
    accepted total, the subset or the population alongside 7,355 is the corrected
    form. Without this the sweep could never reach zero. Both planted files sit at
    paths the scan's own globs reach, so the test exercises the pattern rather
    than the file list.
    """
    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "config").mkdir(parents=True)
    (tmp_path / "docs" / "architecture.md").write_text(
        "7,390 distinct container offsets are reachable by a piece; 7,355 of them\n"
        "by single-piece frames.\n",
        encoding="utf-8",
    )
    (tmp_path / "config" / "roms.yaml").write_text(
        "The corpus holds 7,355 graphics containers in total.\n", encoding="utf-8"
    )
    findings = audit.superseded_hits(tmp_path)
    locations = {finding.location for finding in findings}
    assert "docs/architecture.md:1" not in locations
    assert "config/roms.yaml:1" in locations


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


def test_a_new_stale_hit_inside_a_listed_file_is_reported(tmp_path):
    """The file-set check alone is not the guard; the hit set is."""
    target = tmp_path / "tools/webfoot/formats"
    target.mkdir(parents=True)
    (target / "planted.py").write_text("PIECE_SIZE = 16\n", encoding="utf-8")
    findings = audit.superseded_hits(tmp_path)
    assert any(
        finding.location.startswith("tools/webfoot/formats/planted.py")
        for finding in findings
    ), "a planted PIECE_SIZE = 16 was not detected"


def test_a_lowercase_hex_address_is_detected(tmp_path):
    """The repository writes hex in lowercase, so the scan must be case-aware."""
    target = tmp_path / "tools/webfoot"
    target.mkdir(parents=True)
    (target / "planted.py").write_text("base = 0x086b6bb4\n", encoding="utf-8")
    findings = audit.superseded_hits(tmp_path)
    assert any(
        "sprite-run-base-0x6b6bb4" in finding.detail for finding in findings
    ), "lowercase 0x086b6bb4 was not detected"


def test_a_defect_line_carrying_hedging_prose_is_still_reported(tmp_path):
    """The historical-marker filter must not swallow a real defect."""
    target = tmp_path / "tools/webfoot/formats"
    target.mkdir(parents=True)
    (target / "planted.py").write_text(
        "PIECE_SIZE = 16  # must not be changed without review\n", encoding="utf-8"
    )
    findings = audit.superseded_hits(tmp_path)
    assert any(
        finding.location.startswith("tools/webfoot/formats/planted.py")
        for finding in findings
    ), "a defect line with a hedging comment was filtered out"


def test_a_new_stale_claim_in_a_banner_exempt_document_is_still_reported(tmp_path):
    """The banner covers its own claims, not the whole document."""
    target = tmp_path / "docs/research"
    target.mkdir(parents=True)
    (target / "GRAPHICS_FORMAT.md").write_text(
        "> ## SUPERSEDED STATEMENTS\n> where a figure below disagrees, this\n"
        "> list wins.\n\nUnknownHeader is the canonical wrapper.\n",
        encoding="utf-8",
    )
    findings = audit.superseded_hits(tmp_path)
    assert any(
        "unknown-header-as-container" in finding.detail for finding in findings
    ), "a new stale claim in an exempt document was not reported"


def test_the_patterns_with_no_surviving_occurrence_stay_absent():
    """These six were refuted and have no hit anywhere; a regression is news.

    Four were already absent when the synthesis closed. The two layout keys joined
    them when EVIDENCE-RISK-DEBT-001 executed FIX-2, which is why this test grew:
    the correction is only complete while nothing reads the 4-byte frame header or
    the 16-byte piece stride as current.
    """
    keys = {"sixty-four-kib-engine-limit", "zero-first-word-means-empty",
            "layer-0x00-numeric-type", "connector-destination-be-u16",
            "four-byte-frame-header", "sixteen-byte-piece"}
    present = {finding.detail.split(":", 1)[0] for finding in audit.superseded_hits()}
    assert keys & present == set(), sorted(keys & present)


def test_banner_exemption_is_conditional_and_key_scoped():
    """A banner covers only its own claims, and only while the banner stands."""
    exempted_keys: set[str] = set()
    for relative, keys in audit.BANNER_EXEMPT_KEYS.items():
        text = (audit.project_root() / relative).read_text(encoding="utf-8")
        for marker in audit.BANNER_REQUIRED_MARKERS:
            assert marker in text, (
                f"{relative} lost the required banner marker {marker!r}; the "
                "scan exemption is no longer justified"
            )
        # the exemption must not blanket the document
        assert keys, relative
        assert keys < {pattern.key for pattern in audit.SUPERSEDED_PATTERNS}, (
            f"{relative} exempts every pattern, which defeats the scan"
        )
        exempted_keys |= set(keys)
    # and each exempt key must name a claim the banner actually states, so the
    # exemption and the document cannot drift apart
    banner = "\n".join(
        (audit.project_root() / relative).read_text(encoding="utf-8")
        for relative in audit.BANNER_EXEMPT_KEYS
    )
    for token in ("7,355", "16-byte", "8-byte", "23-slot", "no header field"):
        assert token in banner, token


def test_the_audit_scope_reaches_the_documents_that_carry_the_stale_figure():
    """reviewer-found omissions: the scan must reach these files."""
    for relative in (
        "THIRD-PARTY-NOTICES.md",
        "config/roms.yaml",
        "docs/architecture.md",
        "docs/project-format.md",
        "docs/research/SUBSYSTEM_MAP.md",
    ):
        assert (audit.project_root() / relative).is_file(), relative
        assert any(
            (audit.project_root() / relative).match(glob)
            for glob in audit.SCAN_GLOBS
        ), f"{relative} is outside SCAN_GLOBS"
    assert (audit.project_root() / "THIRD-PARTY-NOTICES.md").is_file()
    stale = next(p for p in audit.SUPERSEDED_PATTERNS if p.key == "stale-7355")
    assert "THIRD-PARTY-NOTICES.md" in stale.globs
    assert "config/roms.yaml" in stale.globs


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
