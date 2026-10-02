"""The public surface, and the boundaries of every screen that guards it.

Two classes of problem are caught here.

1. **What the repository says about itself.** The repository is public, so it
   must not carry hosted-service names, workflow vocabulary, private artifact
   names, machine-specific paths or credentials. The screen for that is
   :mod:`tools.quality.public_surface`.

2. **Whether a newcomer can navigate it.** A front page that links to a file
   that does not exist is worse than no link, and the policy documents a
   contributor is sent to must still state the rules they exist for.

The screen is deliberately narrow, and every screen carries a probe pair in the
encoded table: a string it must accept and a near-miss it must reject. A pattern
that quietly stops matching fails its own test here rather than passing the tree
by matching nothing.
"""

from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from tools.quality import public_surface as surface

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: The documents a newcomer is sent to first. Every relative link in one of
#: these must resolve, because a broken link here wastes a reader's time at the
#: exact moment they are deciding whether the project is worth their attention.
FRONT_DOOR = (
    "README.md",
    "CONTRIBUTING.md",
    "docs/README.md",
    "docs/DEVELOPMENT.md",
    "docs/REVIEW.md",
    "docs/ROM_SAFETY.md",
    "docs/architecture.md",
    "docs/project-format.md",
    "docs/reverse-engineering.md",
    "docs/testing.md",
    "docs/runtime-capture.md",
    "docs/PROJECT_<local-state-name>",
    "docs/ROADMAP_TO_1_0.md",
)


def _read(relative: str) -> str:
    return (REPOSITORY_ROOT / relative).read_text(encoding="utf-8")


# --- the screens still have teeth --------------------------------------------


def test_every_screen_carries_a_control_pair_and_the_tables_agree():
    labels = [label for label, _ in surface.FORBIDDEN]

    assert len(labels) >= 8, "the screen set shrank unexpectedly"
    assert labels == [label for label, _, _ in surface.PROBES]
    assert len(set(labels)) == len(labels), "two screens share a label"


@pytest.mark.parametrize("index", range(len(surface.PROBES)))
def test_a_screen_accepts_its_positive_control_and_rejects_its_negative(index):
    label, positive, negative = surface.PROBES[index]
    pattern = surface.FORBIDDEN[index][1]

    assert surface.FORBIDDEN[index][0] == label
    assert pattern.search(positive), f"{label}: missed its own positive control"
    assert not pattern.search(negative), f"{label}: fired on its negative control"


def test_the_controls_are_not_written_down_in_this_repository():
    """The controls travel encoded, so the tree carries nothing it forbids."""
    source = _read("tests/unit/test_public_surface.py")

    for _label, positive, negative in surface.PROBES:
        for probe in (positive, negative):
            assert probe not in source, "a control was written into the test"


# --- findings and exceptions -------------------------------------------------


def test_the_public_surface_is_clean():
    report = surface.scan_tree()

    assert report["files_scanned"] > 500, "the screen did not reach the whole tree"
    assert report["findings"] == [], json.dumps(report["findings"], indent=2)


def test_every_recorded_exception_is_justified_present_and_load_bearing():
    table = surface.ExceptionTable.load()

    assert table.entries, "the exception file is empty or missing"
    for entry in table.entries:
        assert entry.get("reason", "").strip(), f"no reason: {entry}"
        relative = entry["path"]
        assert "*" not in relative, "exceptions name one file, not a directory"
        assert (REPOSITORY_ROOT / relative).is_file(), f"stale exception: {relative}"
        index = entry["signal_index"]
        assert 0 <= index < len(surface.FORBIDDEN), f"bad signal index: {entry}"

        text = (REPOSITORY_ROOT / relative).read_text(encoding="utf-8")
        bare, _ = surface.scan(
            relative=relative, text=text, exceptions=surface.ExceptionTable([])
        )
        assert any(item["signal_index"] == index for item in bare), (
            f"{relative} no longer needs its exception for "
            f"{surface.FORBIDDEN[index][0]!r}"
        )


def test_an_exception_suppresses_only_its_own_screen():
    text = surface.PROBES[0][1]
    entry = {
        "path": "example.py",
        "signal_index": 0,
        "reason": "proves the mechanism",
    }
    table = surface.ExceptionTable([entry])

    found, suppressed = surface.scan(relative="example.py", exceptions=table, text=text)

    assert suppressed == 1
    assert all(item["signal_index"] != 0 for item in found)


def test_the_report_is_deterministic(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    assert surface.main(["--no-fail", "--json", str(first)]) == 0
    assert surface.main(["--no-fail", "--json", str(second)]) == 0

    assert first.read_bytes() == second.read_bytes()


def test_no_fail_reports_without_failing(monkeypatch, tmp_path):
    """--no-fail is the reading mode: findings are printed, the exit code is 0."""
    (tmp_path / "example.py").write_text("clean\n", encoding="utf-8")
    monkeypatch.setattr(surface, "REPOSITORY_ROOT", tmp_path)
    monkeypatch.setattr(surface, "tracked_text_files", lambda root=None: ["example.py"])
    monkeypatch.setattr(
        surface,
        "scan",
        lambda *a, **k: (
            [
                {
                    "path": "example.py",
                    "line": 1,
                    "signal_index": 0,
                    "signal": "a screen",
                    "text": "matched",
                }
            ],
            0,
        ),
    )

    assert surface.main(["--all", "--no-fail"]) == 0
    assert surface.main(["--all"]) == 1


# --- the front door ----------------------------------------------------------


def test_the_front_door_states_what_the_product_is_and_does():
    readme = _read("README.md")

    for heading in (
        "## What it can do",
        "## Current status",
        "## Getting started",
        "## Legal / ROM policy",
        "## Project status / experimental warning",
        "## License",
    ):
        assert heading in readme, f"README.md is missing {heading!r}"


def test_the_front_door_states_that_no_rom_is_included():
    readme = _read("README.md")

    assert "contains no game data" in readme
    assert "legally obtained" in readme
    assert readme.index("legally obtained") < readme.index("## Current status")


def test_the_front_door_points_at_conventional_documents_only():
    readme = _read("README.md")

    assert "CONTRIBUTING.md" in readme
    assert "docs/DEVELOPMENT.md" in readme
    assert "docs/ROM_SAFETY.md" in readme
    assert "docs/PROJECT_<local-state-name>" in readme


def test_relative_links_in_the_front_door_resolve():
    link = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    broken: list[str] = []
    checked = 0
    for relative in FRONT_DOOR:
        directory = Path(relative).parent
        for target in link.findall(_read(relative)):
            target = target.strip()
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            path = target.split("#", 1)[0]
            if not path:
                continue
            checked += 1
            if not (REPOSITORY_ROOT / directory / path).exists():
                broken.append(f"{relative}: {target}")

    assert checked > 20, f"only {checked} relative links were checked"
    assert broken == [], "broken documentation links:\n" + "\n".join(broken)


def test_the_policy_documents_still_state_their_rules():
    policy = _read("docs/DEVELOPMENT.md")
    for heading in (
        "## The product and its acceptance target",
        "## ROM safety",
        "## Evidence discipline",
        "## Reverse-engineering policy",
        "## Testing and validation",
        "## Git safety",
    ):
        assert heading in policy, f"docs/DEVELOPMENT.md lost {heading!r}"

    review = _read("docs/REVIEW.md")
    for dimension in (
        "Correctness",
        "Architecture and product alignment",
        "ROM and data safety",
        "Determinism",
        "Tests and evidence",
        "Compatibility",
        "Maintainability",
        "Public-release readiness",
    ):
        assert dimension in review, f"docs/REVIEW.md lost {dimension!r}"
    for verdict in ("APPROVE", "APPROVE WITH NON-BLOCKING NOTES", "BLOCK"):
        assert verdict in review

    safety = _read("docs/ROM_SAFETY.md")
    assert "verified base -> working copy/generated output -> patch/output ROM" in safety
    assert "must never be committed" in safety


def test_the_documentation_index_lists_the_entry_points():
    index = _read("docs/README.md")

    for name in (
        "DEVELOPMENT.md",
        "REVIEW.md",
        "ROM_SAFETY.md",
        "architecture.md",
        "project-format.md",
        "reverse-engineering.md",
        "testing.md",
    ):
        assert name in index, f"docs/README.md does not link {name}"
