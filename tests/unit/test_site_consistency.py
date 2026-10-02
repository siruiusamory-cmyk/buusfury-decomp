"""The public progress site: its data model, and its consistency with the page.

The site is a public product surface, so it is held to the same standard as the
repository. The checks themselves live in :mod:`tools.quality.site_check`, which
CI runs against the freshly built artifact, and this module runs the same checks
locally and proves that each of them can fail.

Two classes of problem are caught:

1. **Structure.** The status data is a small schema, and a schema can be checked:
   unique identifiers, a known status vocabulary, exactly one current step, one
   authoritative progress figure, and a blocker and acceptance target that exist.
   These are facts about the data, not about the English in it.

2. **Drift.** A status page goes stale quietly. A milestone can be marked complete
   while its own text still says the work is unfinished, and a rendered figure can
   disagree with the data behind it. The regression test for the first of those is
   ``test_a_completed_milestone_cannot_read_as_unfinished`` below.

Without a build the artifact checks skip, like the other built-page checks in
this suite. The data checks read ``src/data/project.ts`` and never need one.
"""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import re

import pytest

from tools.quality import site_check

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BUILT_DIRECTORY = REPOSITORY_ROOT / "dist"
PROJECT_SOURCE = REPOSITORY_ROOT / "src" / "data" / "project.ts"


def _status() -> dict:
    try:
        return site_check.load_status(BUILT_DIRECTORY)
    except FileNotFoundError:
        pytest.skip("site not built; run `npm run build`")


def _clean_status() -> dict:
    """A minimal status document that passes every structural rule."""
    return {
        "acceptanceTarget": "Author playable content in the real engine.",
        "blocker": {"title": "Bring graphics in", "short": "Blocked on allocation.", "paragraphs": ["Because."]},
        "breakthroughs": [{"id": "b1", "summary": "Done.", "title": "A win"}],
        "buildout": {"done": 3, "percent": 75, "total": 4},
        "frontier": [],
        "milestones": [
            {"id": "m1", "plainEnglish": "It works.", "status": "complete", "title": "One"},
            {"id": "m2", "plainEnglish": "It will work.", "status": "target", "title": "Two"},
        ],
        "nextPhase": {"id": "p2", "title": "Next"},
        "programme": {"done": 1, "percent": 100, "total": 1},
        "roadmapPhases": [
            {"id": "p1", "state": "complete", "title": "Done"},
            {"id": "p2", "state": "next", "title": "Next"},
        ],
    }


# --- the site passes its own checks ------------------------------------------


def test_the_built_site_passes_every_check():
    if not (BUILT_DIRECTORY / site_check.PAGE).is_file():
        pytest.skip("site not built; run `npm run build`")
    findings = site_check.check(BUILT_DIRECTORY)

    assert findings == [], "the built site has problems:\n" + "\n".join(findings)


def test_the_control_document_passes_every_structural_rule():
    """The control proves the rules are satisfiable, not merely strict."""
    assert site_check.structure_findings(_clean_status()) == []


# --- every structural rule can fail ------------------------------------------


def test_a_missing_section_is_reported():
    status = _clean_status()
    status.pop("blocker")

    assert any("blocker" in finding for finding in site_check.structure_findings(status))


def test_a_duplicate_identifier_is_reported():
    status = _clean_status()
    status["milestones"].append(copy.deepcopy(status["milestones"][0]))

    assert any("duplicate id" in finding for finding in site_check.structure_findings(status))


def test_an_unknown_status_is_reported():
    status = _clean_status()
    status["milestones"][0]["status"] = "nearly"

    assert any("unknown status" in f for f in site_check.structure_findings(status))


def test_a_second_current_phase_is_reported():
    status = _clean_status()
    status["roadmapPhases"].append({"id": "p3", "state": "next", "title": "Also next"})

    assert any(
        "more than one" in finding for finding in site_check.structure_findings(status)
    )


def test_a_current_milestone_in_the_programme_is_reported():
    status = _clean_status()
    status["milestones"][0]["status"] = "current"

    assert any(
        "marked current" in finding for finding in site_check.structure_findings(status)
    )


def test_a_percentage_that_does_not_follow_is_reported():
    status = _clean_status()
    status["buildout"]["percent"] = 99

    assert any(
        "does not follow" in finding for finding in site_check.structure_findings(status)
    )


def test_an_empty_public_field_is_reported():
    status = _clean_status()
    status["acceptanceTarget"] = "   "

    assert any(
        "acceptance target" in finding for finding in site_check.structure_findings(status)
    )


# --- the drift regression ----------------------------------------------------


def test_a_completed_milestone_cannot_read_as_unfinished():
    """The defect this ticket exists to prevent, as an invariant.

    A completed milestone may contrast with the state it replaced, but its own
    description may not assert that the work is unfinished now. Where a milestone
    genuinely must name something it leaves open, it declares that item in
    ``openItems``; the declaration is the explicit decision, so the rule checks
    the shape of the data rather than the wording someone happened to use.
    """
    status = _clean_status()
    status["milestones"][0]["plainEnglish"] = "The limit is not yet measured."

    findings = site_check.structure_findings(status)
    assert any("reads as unfinished" in finding for finding in findings)

    # The same sentence is accepted once the milestone declares the open item.
    declared = copy.deepcopy(status)
    declared["milestones"][0]["openItems"] = ["The exact limit."]
    assert site_check.structure_findings(declared) == []


def test_open_items_are_rejected_outside_a_completed_milestone():
    status = _clean_status()
    status["milestones"][1]["openItems"] = ["Something"]

    assert any("open items while" in finding for finding in site_check.structure_findings(status))


def test_open_items_must_not_be_empty():
    status = _clean_status()
    status["milestones"][0]["openItems"] = []

    assert any("empty open item" in finding for finding in site_check.structure_findings(status))


# --- the source, not the artifact --------------------------------------------


def test_no_hand_written_overall_percentage_survives_in_the_source():
    """A second progress number is a second authority, and they will disagree."""
    source = PROJECT_SOURCE.read_text(encoding="utf-8")

    assert "overallProgress" not in source
    for match in re.finditer(r"\b(\d{1,3})\s*%", source):
        assert match.group(1) in {"100", "0", "24"}, (
            f"a hand-written percentage appears in the site source: {match.group(0)}"
        )


def test_the_progress_figure_is_the_one_the_registry_reports():
    status = _status()
    registry = json.loads(
        (REPOSITORY_ROOT / "src" / "data" / "capabilities.json").read_text(encoding="utf-8")
    )
    shipped = [c for c in registry["capabilities"] if c["state"] == "shipped"]

    assert status["buildout"]["done"] == len(shipped)
    assert status["buildout"]["total"] == len(registry["capabilities"])
    assert status["buildout"]["percent"] == math.floor(
        len(shipped) / len(registry["capabilities"]) * 100 + 0.5
    )
