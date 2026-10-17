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
#
# One case per rule: a clean document is mutated, and the rule's own sentence must
# appear in the findings. Written as a table because the cases differ only in the
# mutation and the sentence each rule reports.


def _a_missing_section(status):
    status.pop("blocker")


def _a_duplicate_identifier(status):
    status["milestones"].append(copy.deepcopy(status["milestones"][0]))


def _an_unknown_status(status):
    status["milestones"][0]["status"] = "nearly"


def _a_second_current_phase(status):
    status["roadmapPhases"].append({"id": "p3", "state": "next", "title": "Also next"})


def _a_current_milestone_in_the_programme(status):
    status["milestones"][0]["status"] = "current"


def _a_percentage_that_does_not_follow(status):
    status["buildout"]["percent"] = 99


def _an_empty_public_field(status):
    status["acceptanceTarget"] = "   "


def _open_items_outside_a_completed_milestone(status):
    status["milestones"][1]["openItems"] = ["Something"]


def _empty_open_items(status):
    status["milestones"][0]["openItems"] = []


@pytest.mark.parametrize(
    "mutate,expected",
    [
        (_a_missing_section, "blocker"),
        (_a_duplicate_identifier, "duplicate id"),
        (_an_unknown_status, "unknown status"),
        (_a_second_current_phase, "more than one"),
        (_a_current_milestone_in_the_programme, "marked current"),
        (_a_percentage_that_does_not_follow, "does not follow"),
        (_an_empty_public_field, "acceptance target"),
        (_open_items_outside_a_completed_milestone, "open items while"),
        (_empty_open_items, "empty open item"),
    ],
    ids=[
        "a missing section",
        "a duplicate identifier",
        "an unknown status",
        "a second current phase",
        "a current milestone in the programme",
        "a percentage that does not follow",
        "an empty public field",
        "open items outside a completed milestone",
        "empty open items",
    ],
)
def test_every_structural_rule_can_fail(mutate, expected):
    status = _clean_status()
    mutate(status)

    assert any(expected in finding for finding in site_check.structure_findings(status))


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


# --- the artifact rules can fail too -----------------------------------------


def _built(tmp_path, *, page: str, status: dict | None = None) -> Path:
    directory = tmp_path / "dist"
    directory.mkdir()
    (directory / site_check.PAGE).write_text(page, encoding="utf-8")
    (directory / site_check.STATUS_DOCUMENT).write_text(
        json.dumps(status if status is not None else _clean_status()), encoding="utf-8"
    )
    return directory


def _passing_page(status: dict | None = None) -> str:
    """A page that satisfies every artifact rule, quoting its own data."""
    status = status if status is not None else _clean_status()
    section = status["buildout"]
    return (
        "<html><body><h1>Webfoot SDK</h1><h2>Status</h2><h3>Milestones</h3>"
        f'<a href="{site_check.REPOSITORY_URL}">repository</a>'
        '<a href="#status">status</a><div id="status"></div>'
        f"<p>{section['done']} / {section['total']} capabilities, {section['percent']}%</p>"
        '<img src="/shot.png" alt="">'
        "</body></html>"
    )


def test_a_clean_artifact_is_accepted(tmp_path):
    directory = _built(tmp_path, page=_passing_page())
    (directory / "shot.png").write_bytes(b"\x89PNG")

    assert site_check.artifact_findings(directory) == []


def test_a_heading_level_skip_is_reported():
    findings = site_check._heading_findings("<h1>a</h1><h2>b</h2><h4>c</h4>")

    assert any("skips from h2 to h4" in finding for finding in findings)


def test_a_heading_sequence_without_a_skip_is_accepted():
    assert site_check._heading_findings("<h1>a</h1><h2>b</h2><h3>c</h3>") == []


def test_two_h1_headings_are_reported():
    findings = site_check._heading_findings("<h1>a</h1><h1>b</h1>")

    assert any("exactly one h1" in finding for finding in findings)


def test_an_anchor_with_no_target_is_reported(tmp_path):
    page = _passing_page().replace('<div id="status"></div>', "")
    directory = _built(tmp_path, page=page)
    (directory / "shot.png").write_bytes(b"\x89PNG")

    findings = site_check.artifact_findings(directory)

    assert any("#status has no target" in finding for finding in findings)


def test_a_figure_the_data_does_not_report_is_reported(tmp_path):
    page = _passing_page().replace("75%", "91%")
    directory = _built(tmp_path, page=page)
    (directory / "shot.png").write_bytes(b"\x89PNG")

    findings = site_check.artifact_findings(directory)

    assert any("computed 75%" in finding for finding in findings)


def test_a_forbidden_marker_in_the_artifact_is_reported(tmp_path):
    directory = _built(tmp_path, page=_passing_page() + "<p>C:\\Dev\\somewhere</p>")

    findings = site_check.artifact_findings(directory)

    assert any("C:\\" in finding for finding in findings)


def test_a_missing_asset_is_reported(tmp_path):
    directory = _built(tmp_path, page=_passing_page())

    findings = site_check.artifact_findings(directory)

    assert any("missing asset /shot.png" in finding for finding in findings)


# --- unreadable content is not clean content ---------------------------------


def test_an_undecodable_file_is_reported_rather_than_counted(monkeypatch, tmp_path):
    """A file the screen cannot read must not look like a file it cleared."""
    from tools.quality import public_surface

    (tmp_path / "binary-ish.py").write_bytes(b"\xff\xfe\x00\x01")
    monkeypatch.setattr(public_surface, "tracked_text_files", lambda root=None: ["binary-ish.py"])

    report = public_surface.scan_tree(tmp_path)

    assert report["unreadable"] == ["binary-ish.py"]
    assert report["files_scanned"] == 0
    assert report["files_selected"] == 1


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
