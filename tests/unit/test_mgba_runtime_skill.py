"""Enforcement gate for the mGBA runtime skill.

`docs/skills/mgba-runtime.md` is the tracked authority for emulator evidence.
Before this test, those rules lived only in an untracked machine-local file, so
a ticket worktree did not contain them and no review could cite them. The test
below is the part of the policy that can be checked mechanically; loosening it
is loosening the policy, not tidying a test.

What is checked, and why each one is checkable:

1. the tracked authority exists, says something, and is named from the tracked
   policy document, so it travels with the repository;
2. every observer the injector will accept exists on disk and writes no
   emulated memory, because the allowlist is only a guard if its entries are
   real and read-only;
3. the injector can run a command AFTER the observer's `dofile`, which is the
   only ordering under which a savestate load can be observed at all;
4. a runtime script that hands mGBA `--script` also fails closed on emulator
   version and on an exact ROM digest, because `--script` leaves the allowlist
   path and must not also leave the two identity gates.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "docs/skills/mgba-runtime.md"
DEVELOPMENT = ROOT / "docs/DEVELOPMENT.md"
INJECTOR = ROOT / "tools/runtime/inject_mgba_lua.ps1"
RUNTIME = ROOT / "tools/runtime"

MEMORY_WRITE_NAMES = ("emu:write8", "emu:write16", "emu:write32",
                      "emu:writeRange", "emu:writes")


def _injector_text() -> str:
    return INJECTOR.read_text(encoding="utf-8")


def _allowlisted_observers() -> list[str]:
    """Every observer path the injector will accept, as repository-relative paths."""
    text = _injector_text()
    block = text.split("$allowedLua", 1)[1].split("\n)", 1)[0]
    return re.findall(r"Join-Path \$workspaceRoot '([^']+)'", block)


def test_the_tracked_authority_exists_and_is_not_a_stub():
    assert SKILL.is_file(), (
        "docs/skills/mgba-runtime.md is the tracked mGBA runtime authority; "
        "without it the rules do not travel to a ticket worktree")
    body = SKILL.read_text(encoding="utf-8")
    assert len(body) > 4000, "the authority has been reduced to a stub"
    for required in ("Allowlist", "Liveness", "read-only"):
        assert required.lower() in body.lower(), required


def test_the_tracked_policy_names_the_authority():
    policy = DEVELOPMENT.read_text(encoding="utf-8")
    assert "skills/mgba-runtime.md" in policy, (
        "docs/DEVELOPMENT.md must name the tracked authority, so the policy "
        "and the skill cannot drift apart")
    assert "Runtime evidence" in policy


def test_every_allowlisted_observer_exists():
    names = _allowlisted_observers()
    assert len(names) > 50, f"allowlist parse produced only {len(names)} entries"
    missing = [name for name in names if not (ROOT / name).is_file()]
    assert not missing, f"allowlisted observers that do not exist: {missing}"


def test_every_allowlisted_observer_is_read_only():
    offenders = {}
    for name in _allowlisted_observers():
        path = ROOT / name
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        found = [token for token in MEMORY_WRITE_NAMES if token in source]
        if found:
            offenders[name] = found
    assert not offenders, f"observers that write emulated memory: {offenders}"


def test_the_injector_can_act_after_the_observer_loads():
    """The savestate must load AFTER injection, so the injector needs a suffix."""
    text = _injector_text()
    assert "$PostCommand" in text, (
        "the injector must accept a post-injection command; that is where a "
        "savestate load belongs")
    dofile_at = text.index("dofile([[")
    post_at = text.index("$command += '; ' + $PostCommand")
    ready_at = text.index("if ($resolvedReady) {", dofile_at)
    assert dofile_at < post_at < ready_at, (
        "the post-injection command must run after the observer's dofile and "
        "before the ready marker is written")


def test_the_injector_still_confines_its_host_paths_to_build():
    """Guards that a regex prune of the allowlist has already destroyed once.

    `$allowedReadyRoot` and `$allowedMarkerRoot` are built with the same
    `Join-Path $workspaceRoot 'build'` shape as an allowlist entry, so a prune
    that matches that shape removes them and leaves
    `$allowedReadyRoot =.TrimEnd('\\') + '\\'`. The file still parses, and the
    confinement check silently compares against an empty root. Pin both.
    """
    text = _injector_text()
    assert text.count("Join-Path $workspaceRoot 'build'") == 2
    assert "$allowedReadyRoot = [System.IO.Path]::GetFullPath(" in text
    assert "$allowedMarkerRoot = [System.IO.Path]::GetFullPath(" in text
    for name in _allowlisted_observers():
        assert name != "build", "the build root is not an observer entry"


@pytest.mark.parametrize("script", sorted(p.name for p in RUNTIME.glob("*.ps1")))
def test_a_script_that_uses_script_flag_keeps_the_identity_gates(script):
    """`--script` leaves the allowlist path, so it must not leave the gates too."""
    text = (RUNTIME / script).read_text(encoding="utf-8", errors="replace")
    if not re.search(r"['\"]--script['\"]", text):
        pytest.skip("does not pass --script to the emulator")
    assert "VersionInfo.FileVersion" in text or "RequiredMGBVersion" in text, (
        f"{script} passes --script without verifying the emulator build")
    assert re.search(r"Sha256", text), (
        f"{script} passes --script without an exact ROM digest gate")
