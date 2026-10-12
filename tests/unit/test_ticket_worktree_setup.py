"""The worktree setup path: the interpreter fallback, the cutter, the sweep.

CI runs on Linux, where no `.ps1` can execute, so the two entry-point scripts are
guarded as text. What is asserted is what a lane depends on and cannot see drift
away: the fallback interpreter and the order it is tried in, the line that names
the interpreter it chose, the frozen base SHA the worktree is cut from, the
junction, the ownership sweep, and that neither script can name the primary
checkout as a target. Deleting the fallback fails this file, which is the point
of it. The fallback's behaviour itself is measured by running the script in both
states, which this file cannot do on Linux.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPOSITORY_ROOT / "scripts"

#: The shared test venv is named by this sibling path, relative to whatever
#: directory holds the worktrees. It is not an absolute path: the quality gate
#: forbids a machine-specific absolute path in tracked text, and both scripts
#: search upward for this sibling instead of naming one machine's directory.
SHARED_SIBLING = r"log1-remake-test-speed-003\build\test-speed-003\venv"

#: The primary checkout is the sibling whose name is the shared prefix with no
#: ticket suffix, so `log1-remake` followed by anything but a hyphen is a path
#: into that checkout and never a sibling worktree.
PRIMARY_CHECKOUT = re.compile(r"log1-remake(?![-\w])")


def _script(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def test_the_entry_point_tries_the_worktree_venv_before_the_shared_one():
    text = _script("test.ps1")

    candidates = text[text.index("$candidates = @(") : text.index("$Python = $null")]
    assert candidates.count("Join-Path") == 2
    assert candidates.index("Join-Path $ProjectRoot") < candidates.index(
        "Join-Path $SharedVenv"
    )
    assert "$SharedSibling = '" + SHARED_SIBLING + "'" in text


def test_the_entry_point_prints_the_interpreter_it_chose_and_why():
    text = _script("test.ps1")

    assert "interpreter $Python" in text
    assert "$($candidate.Why)" in text


def test_the_entry_point_stops_after_resolving_on_request():
    """Both measured states are read off `-ResolveOnly`, with no gate run."""
    text = _script("test.ps1")

    assert "[switch]$ResolveOnly" in text
    assert "if ($ResolveOnly) { exit 0 }" in text


def test_the_entry_point_refuses_when_neither_interpreter_exists():
    text = _script("test.ps1")

    assert text.index("if (-not $Python)") < text.index("if ($ResolveOnly)")


@pytest.mark.parametrize("name", ["test.ps1", "new-ticket-worktree.ps1"])
def test_no_script_names_the_primary_checkout_as_a_target(name):
    assert PRIMARY_CHECKOUT.search(_script(name)) is None


def test_the_cutter_cuts_from_the_fetched_origin_master_tip():
    text = _script("new-ticket-worktree.ps1")

    assert "'fetch', 'origin', '--prune'" in text
    assert "'rev-parse', 'origin/master'" in text
    assert "'worktree', 'add', '-b', $Branch, $Worktree, $Base" in text
    assert text.index("'rev-parse', 'origin/master'") < text.index("'worktree', 'add', '-b'")


def test_the_cutter_judges_git_by_exit_code_when_a_caller_redirects_a_stream():
    """PowerShell 5.1 makes redirected native stderr terminating, measured."""
    text = _script("new-ticket-worktree.ps1")

    assert "function Invoke-Git" in text
    assert "$ErrorActionPreference = 'Continue'" in text
    assert "2>&1" in text
    assert "if ($exit -ne 0) {" in text


def test_the_cutter_derives_the_worktree_name_and_junctions_the_shared_venv():
    text = _script("new-ticket-worktree.ps1")

    assert "'log1-remake-' + $Ticket.ToLowerInvariant()" in text
    assert "New-Item -ItemType Junction" in text
    assert "$SharedSibling = '" + SHARED_SIBLING + "'" in text


def test_the_cutter_runs_npm_ci_only_for_the_site_gates():
    text = _script("new-ticket-worktree.ps1")

    assert "if ($SiteGates) {" in text
    assert "[-Parent <dir>] [-SiteGates]" in text
    assert "npm ci" in text
    assert "$npmExit" in text


def test_the_cutter_prints_the_ownership_sweep_bounded():
    text = _script("new-ticket-worktree.ps1")

    assert "'worktree', 'list', '--porcelain'" in text
    assert "'status', '--porcelain'" in text
    assert "uncommitted file(s)" in text
    assert "Select-Object -First 8" in text
    # A worktree git cannot read (moved or deleted) must not be reported as clean.
    assert "unreadable: git status exited" in text
    # Measured 2026-10-12: `Invoke-Git 'status', '--porcelain', -Path $path` binds
    # `-Path` as an array element, so git saw an unknown switch and every worktree
    # was reported unreadable. The path is passed by name.
    assert re.search(r",\s*-Path", text) is None


def test_the_testing_document_states_the_interpreter_fallback_and_both_rom_variables():
    documented = (REPOSITORY_ROOT / "docs" / "testing.md").read_text(encoding="utf-8")

    assert SHARED_SIBLING in documented
    assert "LOGX_CANONICAL_ROM" in documented
    assert "WEBFOOT_BUU_ROM" in documented
    assert "new-ticket-worktree.ps1" in documented
