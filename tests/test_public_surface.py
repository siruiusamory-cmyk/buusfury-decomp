"""The public surface: what the repository says about itself, and to whom.

Two classes of problem are caught here.

1. **Residue.** The repository is public. It should read as an ordinary
   decompilation project and must not advertise or depend on knowledge of how the
   work was organised internally: no vendor or product names and no workflow vocabulary.

2. **Broken navigation.** A front page that links to a file that does not exist is
   worse than no link, and the documentation index is the front door for a
   newcomer.

The residue detector is deliberately narrow. The project's own technical
vocabulary is full of words that look similar - a *machine model*, a *data model*,
a *cursor* into a bytecode stream, a *test harness* - and a detector broad enough
to catch those would be noise rather than a check. It scans for the terms that can
only mean the thing being excluded, plus a few phrases. Ticket identifiers such as
`DECOMP-LIFT-STACK-001` are **not** residue: they are provenance labels that tie a
document to the committed evidence behind it, and they live in the detailed
write-ups, not in the front-door navigation.
"""

from __future__ import annotations

import os
import re

import pytest

from buusfury import decompdev as dd
from buusfury import identity

#: The scan targets are defined by the current revision of this file.

#: This file necessarily names the terms it forbids, so it cannot pass its own
#: scan. It is the ONLY exclusion: every other tracked file is scanned, which is
#: what makes the detector worth having.
_SELF = "tests/test_public_surface.py"

SKIP_DIRECTORIES = {".git", "build", "reference", "__pycache__", ".pytest_cache"}
BINARY_SUFFIXES = {".bin", ".png", ".bmp", ".pal", ".gba", ".agb", ".sav"}

#: The front door, and the documents a newcomer is sent to first.
FRONT_DOOR = (
    "README.md",
    "CONTRIBUTING.md",
    "docs/DEVELOPMENT.md",
    "docs/README.md",
    "docs/ARCHITECTURE.md",
    "docs/BUILDING.md",
    "docs/PROGRESS.md",
    "docs/IWRAM.md",
    "docs/SCRIPT_VM.md",
    "docs/DECOMP_DEV.md",
)


def _tracked_text_files() -> list[str]:
    import subprocess

    listing = subprocess.run(
        ["git", "ls-files"], cwd=identity.REPO_ROOT, capture_output=True, text=True
    )
    if listing.returncode != 0:  # pragma: no cover - not a git checkout
        pytest.skip("not a git checkout")
    return [
        line
        for line in listing.stdout.splitlines()
        if os.path.splitext(line)[1].lower() not in BINARY_SUFFIXES
    ]


def _read(relative: str) -> str:
    with open(os.path.join(identity.REPO_ROOT, relative), encoding="utf-8") as handle:
        return handle.read()


def test_no_provider_or_process_residue_in_tracked_text() -> None:
    offenders: list[str] = []
    scanned = 0
    excluded = 0
    for relative in _tracked_text_files():
        if relative == _SELF:
            excluded += 1
            continue
        try:
            text = _read(relative)
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        for noise in _FILENAME_NOISE:
            text = text.replace(noise, "")
        for number, line in enumerate(text.splitlines(), 1):
            for label, pattern in FORBIDDEN:
                if pattern.search(line):
                    offenders.append(f"{relative}:{number}: {label}: {line.strip()[:120]}")

    assert excluded == 1, "the detector must be the only file skipped"
    assert scanned > 100, f"the scan only reached {scanned} files"
    assert not offenders, "public surface carries internal residue:\n" + "\n".join(offenders)


def test_the_front_door_carries_the_expected_sections() -> None:
    readme = _read("README.md")
    for heading in (
        "## About",
        "## Project status",
        "## Progress",
        "## Supported version",
        "## Getting started",
        "## Building / validation",
        "## Repository layout",
        "## Contributing",
        "## Documentation",
        "## Legal",
    ):
        assert heading in readme, f"README.md is missing {heading!r}"


def test_the_front_door_states_that_no_rom_is_included() -> None:
    readme = _read("README.md")
    assert "contains no game data" in readme
    assert "legally obtained copy of the game" in readme
    # and it is near the top, not buried under the technical sections
    assert readme.index("legally obtained copy of the game") < readme.index("## Project status")


def test_the_front_door_names_the_supported_revision_and_its_hash() -> None:
    readme = _read("README.md")
    assert "f1c4b07554d2a3b1ad2f325307051e775ce68087" in readme
    assert "BG3E" in readme
    assert "no byte-identical" not in readme.lower()  # never claimed


def test_the_front_door_does_not_call_this_a_matching_decompilation_yet() -> None:
    readme = _read("README.md").lower()
    # The project's goal is matching, but it must not present itself as having
    # achieved it. Any claim of matching must be visibly qualified.
    assert "not currently a byte-matching" in readme or "cannot yet be demonstrated" in readme


def test_the_progress_block_is_generated_and_current() -> None:
    inventory = dd.build_inventory(dd.load_inputs())
    assert dd.readme_progress_findings(inventory) == []
    readme = _read("README.md")
    assert dd.PROGRESS_START in readme and dd.PROGRESS_END in readme


def test_no_document_tells_the_reader_to_create_a_repository() -> None:
    offenders = []
    for relative in _tracked_text_files():
        if not relative.endswith(".md"):
            continue
        try:
            text = _read(relative).lower()
        except (UnicodeDecodeError, OSError):
            continue
        for phrase in (
            "create a public github repository",
            "create a github repository",
            "git remote add github",
            "no github repository exists",
        ):
            if phrase in text:
                offenders.append(f"{relative}: {phrase}")
    assert not offenders, "stale repository-creation instructions:\n" + "\n".join(offenders)


def test_relative_links_in_the_front_door_resolve() -> None:
    """Every relative link in the front-door documents points at a real file."""
    link = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    broken: list[str] = []
    checked = 0
    for relative in FRONT_DOOR:
        directory = os.path.dirname(relative)
        try:
            text = _read(relative)
        except OSError as exc:  # pragma: no cover
            broken.append(f"{relative}: unreadable ({exc})")
            continue
        for target in link.findall(text):
            target = target.strip()
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            path = target.split("#", 1)[0]
            if not path:
                continue
            checked += 1
            resolved = os.path.normpath(os.path.join(identity.REPO_ROOT, directory, path))
            if not os.path.exists(resolved):
                broken.append(f"{relative}: {target}")
    assert checked > 20, f"only {checked} relative links were checked"
    assert not broken, "broken documentation links:\n" + "\n".join(broken)


def test_the_documentation_index_lists_the_entry_points() -> None:
    index = _read("docs/README.md")
    for name in (
        "ARCHITECTURE.md",
        "PROGRESS.md",
        "BUILDING.md",
        "SCRIPT_VM.md",
        "IWRAM.md",
    ):
        assert name in index, f"docs/README.md does not link {name}"


def test_agents_md_reads_as_contributor_policy() -> None:
    policy = _read("docs/DEVELOPMENT.md")
    for heading in (
        "## ROM safety",
        "## Licence discipline",
        "## Evidence discipline",
        "## Reconstruction rules",
        "## Progress reporting",
        "## Git discipline",
    ):
        assert heading in policy, f"docs/DEVELOPMENT.md lost {heading!r}"
    assert "CONTRIBUTING.md" in policy
