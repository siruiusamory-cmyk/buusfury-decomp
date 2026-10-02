"""Validate and screen the built public site.

The site is a public product surface, so the artifact is checked twice: once by
the tests a developer runs, and once in CI immediately after the build and
before anything is published. This module is the one implementation of those
checks, so the two cannot disagree.

It is standard-library only and imports nothing from the test tree, which is what
lets the deploy job run it with a bare Python install next to Node. It reads
``dist/project.json``, the machine-readable copy of the status data the page
renders, so the page and the data behind it are compared rather than assumed to
agree.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.quality import public_surface  # noqa: E402

STATUS_DOCUMENT = "project.json"
PAGE = "index.html"

MILESTONE_STATUSES = {"complete", "current", "next", "target"}
PHASE_STATES = {"complete", "in-progress", "next", "planned"}

REQUIRED_SECTIONS = (
    "acceptanceTarget",
    "blocker",
    "breakthroughs",
    "buildout",
    "frontier",
    "milestones",
    "nextPhase",
    "programme",
    "roadmapPhases",
)

#: Present-tense claims that a piece of work is unfinished. A completed
#: milestone may contrast with the state it replaced, so each phrase is one that
#: cannot carry a historical reading when it describes the milestone's own work.
UNFINISHED_CLAIMS = (
    "not yet",
    "has yet to",
    "still needs",
    "remains to be",
    "is not implemented",
    "not implemented",
    "is not started",
    "has not started",
    "is blocked",
    "no editor surface offers",
    "has no production caller",
)

#: Paths a visitor's browser must never be asked for.
FORBIDDEN_IN_ARTIFACT = ("C:\\", "C:/", "/Users/", "/home/", "localhost", "127.0.0.1", "file://")

#: The project's own repository link, which the page must offer.
REPOSITORY_URL = "https://gitlab.com/siruiusamory/log1-remake"


def load_status(directory: Path) -> dict:
    path = directory / STATUS_DOCUMENT
    if not path.is_file():
        raise FileNotFoundError(f"no {path}; build the site first")
    return json.loads(path.read_text(encoding="utf-8"))


def structure_findings(status: dict) -> list[str]:
    """Facts about the status data: shape, vocabulary, arithmetic, no drift."""
    findings: list[str] = []

    for key in REQUIRED_SECTIONS:
        if key not in status:
            findings.append(f"{STATUS_DOCUMENT} has no {key!r}")

    for key in ("milestones", "breakthroughs", "roadmapPhases"):
        ids = [entry["id"] for entry in status.get(key, [])]
        if len(set(ids)) != len(ids):
            findings.append(f"{key}: duplicate id")
        if any(not entry_id.strip() for entry_id in ids):
            findings.append(f"{key}: empty id")

    for milestone in status.get("milestones", []):
        if milestone["status"] not in MILESTONE_STATUSES:
            findings.append(f"{milestone['id']}: unknown status {milestone['status']!r}")
        if not milestone["title"].strip() or not milestone["plainEnglish"].strip():
            findings.append(f"{milestone['id']}: missing required public field")
    for breakthrough in status.get("breakthroughs", []):
        if not breakthrough["title"].strip() or not breakthrough["summary"].strip():
            findings.append(f"{breakthrough['id']}: missing required public field")
    for phase in status.get("roadmapPhases", []):
        if phase["state"] not in PHASE_STATES:
            findings.append(f"{phase['id']}: unknown state {phase['state']!r}")

    if not status.get("acceptanceTarget", "").strip():
        findings.append("the acceptance target is empty")
    blocker = status.get("blocker", {})
    if not blocker.get("title", "").strip() or not blocker.get("short", "").strip():
        findings.append("the current blocker is empty")
    if not blocker.get("paragraphs"):
        findings.append("the current blocker has no explanation")

    next_phases = [
        phase for phase in status.get("roadmapPhases", []) if phase["state"] == "next"
    ]
    if len(next_phases) > 1:
        findings.append("more than one roadmap phase is marked current")
    if next_phases:
        if status.get("nextPhase", {}).get("id") != next_phases[0]["id"]:
            findings.append("nextPhase does not name the phase marked current")
    elif status.get("nextPhase") is not None:
        findings.append("nextPhase is set while no phase is marked current")

    if [m for m in status.get("milestones", []) if m["status"] == "current"]:
        findings.append("a milestone in the completed programme is marked current")

    for key in ("buildout", "programme"):
        section = status.get(key, {})
        total = section.get("total", 0)
        done = section.get("done", 0)
        if total <= 0 or not 0 <= done <= total:
            findings.append(f"{key}: {done}/{total} is not a coherent count")
            continue
        expected = math.floor(done / total * 100 + 0.5)
        if section.get("percent") != expected:
            findings.append(
                f"{key}: percent {section.get('percent')} does not follow from "
                f"{done}/{total}"
            )

    for milestone in status.get("milestones", []):
        declared = milestone.get("openItems")
        if declared is not None:
            if milestone["status"] != "complete":
                findings.append(
                    f"{milestone['id']}: declares open items while {milestone['status']}"
                )
            if not declared or any(not item.strip() for item in declared):
                findings.append(f"{milestone['id']}: empty open item")
        if milestone["status"] != "complete":
            continue
        text = " ".join(
            part
            for part in (milestone.get("plainEnglish"), milestone.get("technical"))
            if part
        ).lower()
        reads_as_open = [phrase for phrase in UNFINISHED_CLAIMS if phrase in text]
        if reads_as_open and not declared:
            findings.append(
                f"{milestone['id']}: reads as unfinished ({reads_as_open}) with no "
                "openItems declaration"
            )

    return findings


def artifact_findings(directory: Path) -> list[str]:
    """Facts about what a visitor receives, rather than about the sources."""
    findings: list[str] = []
    page_path = directory / PAGE
    if not page_path.is_file():
        return [f"no {page_path}; build the site first"]
    page = page_path.read_text(encoding="utf-8")

    report = public_surface.scan_built(directory)
    findings.extend(
        f"{item['path']}:{item['line']}: {item['signal']}: {item['text']}"
        for item in report["findings"]
    )

    for marker in FORBIDDEN_IN_ARTIFACT:
        if marker in page:
            findings.append(f"{PAGE}: contains {marker!r}")
    if REPOSITORY_URL not in page:
        findings.append(f"{PAGE}: does not link {REPOSITORY_URL}")

    targets = set(re.findall(r'\sid="([^"]+)"', page))
    anchors = set(re.findall(r'href="#([^"]+)"', page))
    for anchor in sorted(anchors - targets):
        findings.append(f"{PAGE}: anchor #{anchor} has no target")

    status = load_status(directory)
    percent = status["buildout"]["percent"]
    if f"{percent}%" not in page:
        findings.append(f"{PAGE}: does not show the computed {percent}%")
    done, total = status["buildout"]["done"], status["buildout"]["total"]
    if f"{done} / {total}" not in page and f"{done}/{total}" not in page.replace(" ", ""):
        findings.append(f"{PAGE}: does not show the computed {done}/{total}")

    for reference in sorted(set(re.findall(r'(?:src|href)="(/[^"#?]+)"', page))):
        if not (directory / reference.lstrip("/")).exists():
            findings.append(f"{PAGE}: references a missing asset {reference}")

    findings.extend(_heading_findings(page))
    return findings


def _heading_findings(page: str) -> list[str]:
    """The document outline: one h1, and no skipped level.

    A skipped level is the whole defect: a screen reader user navigating by
    heading hears a section jump from the page title to a sub-sub-heading with
    nothing in between, and the outline a search engine reads has a hole in it.
    """
    levels = [int(level) for level in re.findall(r"<h([1-6])\b", page)]
    findings = []
    if levels.count(1) != 1:
        findings.append(f"{PAGE}: expected exactly one h1, found {levels.count(1)}")
    elif levels[0] != 1:
        findings.append(f"{PAGE}: the first heading is h{levels[0]}, not h1")
    for previous, current in zip(levels, levels[1:]):
        if current > previous + 1:
            findings.append(
                f"{PAGE}: heading level skips from h{previous} to h{current}"
            )
    return findings


def check(directory: Path) -> list[str]:
    return structure_findings(load_status(directory)) + artifact_findings(directory)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="site-check",
        description="Validate the built progress site and screen its artifact.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=str(REPOSITORY_ROOT / "dist"),
        help="the built site directory (default: dist)",
    )
    arguments = parser.parse_args(argv)

    try:
        findings = check(Path(arguments.directory))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2

    if findings:
        print("the built site has problems:", file=sys.stderr)
        for finding in findings:
            print(f"  {finding}", file=sys.stderr)
        return 1
    print(f"built site ok: {arguments.directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
