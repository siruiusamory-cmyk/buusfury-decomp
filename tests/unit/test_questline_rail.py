"""The questline rail must track the milestone data, not hardcoded percentages.

The rail's colour stops were fixed percentages (52% / 62% / 91%) chosen when the
milestone list was shorter. Nothing recomputed them as milestones were checked
off, so the fill silently drifted: with 9 of 12 milestones complete the rail
still showed 52%. These tests pin the derivation so it cannot drift again.

The rail is inset to the first and last node centres, so node k sits at
k / (n - 1). It is a CONNECTOR between nodes, which is why a band ending after
the last complete milestone ends at that milestone's own node.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA = PROJECT_ROOT / "src/data/project.ts"
COMPONENT = PROJECT_ROOT / "src/components/Questline.astro"
STYLES = PROJECT_ROOT / "src/styles/global.css"


def milestone_statuses() -> list[str]:
    source = DATA.read_text(encoding="utf-8")
    start = source.index("  milestones: [")
    end = source.index("  dependencyLadder", start)
    block = source[start:end]
    return [status for _, status in re.findall(
        r'id:\s*"([^"]+)"[\s\S]*?status:\s*"([^"]+)"', block)]


def expected_stops() -> dict[str, str]:
    statuses = milestone_statuses()
    spans = max(len(statuses) - 1, 1)

    def at(index: int) -> str:
        return f"{(min(max(index, 0), spans) / spans) * 100:.2f}%"

    last_complete = max((i for i, s in enumerate(statuses) if s == "complete"),
                        default=-1)
    last_current = max((i for i, s in enumerate(statuses) if s == "current"),
                       default=-1)
    first_target = next((i for i, s in enumerate(statuses) if s == "target"), spans)
    return {
        "--rail-complete": at(last_complete),
        "--rail-current": at(max(last_current, last_complete)),
        "--rail-target": at(first_target),
    }


def test_rail_stops_are_not_hardcoded_in_css():
    """The gradient must read the custom properties, not literal percentages."""
    rule = next(line for line in STYLES.read_text(encoding="utf-8").splitlines()
                if line.startswith(".questline::before"))
    for name in ("--rail-complete", "--rail-current", "--rail-target"):
        assert name in rule, f"{name} missing from the rail gradient"
    gradient = rule[rule.index("linear-gradient"):]
    assert not re.search(r"\d+%", gradient), (
        "the rail gradient still contains a literal percentage; stops must come "
        "from the milestone data")


def test_component_derives_the_stops_from_milestone_data():
    source = COMPONENT.read_text(encoding="utf-8")
    assert "project.milestones" in source
    assert 'style={railStyle}' in source
    # The divisor must be the number of gaps between nodes, not the node count;
    # using length alone leaves the rail short by one whole milestone.
    assert "milestones.length - 1" in source


@pytest.mark.parametrize("name", ["--rail-complete", "--rail-current", "--rail-target"])
def test_built_page_carries_the_derived_stop(name):
    built = PROJECT_ROOT / "dist/index.html"
    if not built.exists():
        pytest.skip("site not built; run `npm run build`")
    style = re.search(r'class="questline"\s+style="([^"]+)"',
                      built.read_text(encoding="utf-8"))
    assert style, "the built questline carries no derived rail style"
    assert f"{name}: {expected_stops()[name]}" in style.group(1)


def test_every_node_falls_in_its_own_colour_band():
    """The real regression: a node whose band disagrees with its status.

    This is what a drifted rail looks like from the reader's side - a milestone
    marked complete sitting on an unfilled stretch of rail.
    """
    statuses = milestone_statuses()
    spans = max(len(statuses) - 1, 1)
    stops = {k: float(v.rstrip("%")) for k, v in expected_stops().items()}
    wanted = {"complete": "complete", "current": "current",
              "next": "pending", "target": "target"}

    for index, status in enumerate(statuses):
        position = (index / spans) * 100
        if position <= stops["--rail-complete"]:
            band = "complete"
        elif position <= stops["--rail-current"]:
            band = "current"
        elif position < stops["--rail-target"]:
            band = "pending"
        else:
            band = "target"
        assert band == wanted[status], (
            f"milestone {index} is {status!r} but sits on the {band!r} band")


def test_unstarted_milestones_keep_a_visible_band():
    """A zero-width pending band swallows the not-yet-started milestones."""
    statuses = milestone_statuses()
    if not any(s == "next" for s in statuses):
        pytest.skip("no not-yet-started milestone to render")
    stops = {k: float(v.rstrip("%")) for k, v in expected_stops().items()}
    assert stops["--rail-target"] > stops["--rail-current"], (
        "the pending band collapsed to zero width")


def test_fill_reflects_actual_completion():
    """Guards the original symptom: the fill lagging what is checked off."""
    statuses = milestone_statuses()
    spans = max(len(statuses) - 1, 1)
    last_complete = max((i for i, s in enumerate(statuses) if s == "complete"),
                        default=-1)
    filled = float(expected_stops()["--rail-complete"].rstrip("%"))
    assert filled == pytest.approx((last_complete / spans) * 100, abs=0.01)
    # The specific drift that prompted this: 9 of 12 complete rendering as 52%.
    if statuses[:9] == ["complete"] * 9 and len(statuses) == 12:
        assert filled > 70
