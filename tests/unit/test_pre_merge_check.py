"""``scripts/pre-merge-check.ps1``: the gate's rule and its fail-closed path.

The script is PowerShell and the CI image has no PowerShell, so this file is
gated on the host having one: the rule itself is proven by *running the script*
against throwaway repositories built in ``tmp_path``, both outcomes, rather than
by re-implementing it here and hoping the two agree.

The sample, measured 2026-10-12 against this session's own three merges (read-only
``glab api`` on MRs 230, 234 and 235 plus git ancestry in this worktree): master
had moved under exactly one of the three, MR 230, by ten commits. On that one the
two sides DID change the same path - from fork ``1016ab49``, both master
(``c3fc145c``) and the candidate (``50629782``) changed
``docs/research/PROJECT_STATE_AUDIT_RECONCILIATION.md`` - so the gate exits 1
there, while that merge composed cleanly (merge-tree reproduces the recorded tree
``e3466f9a``) and its post-merge master pipeline (``2938640540``) was green. The
gate therefore stops 1 of 1 drifted merges on the sample, and the trade it makes
is a rebase plus a focused re-run, minutes, against a silent interaction no
pipeline tests before the merge. The trade is kept on the review of
RETRO-CI-002-20261012-112919.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.gates import REPOSITORY_ROOT

SCRIPT = REPOSITORY_ROOT / "scripts" / "pre-merge-check.ps1"


def _powershell() -> str | None:
    for name in ("pwsh", "powershell"):
        found = shutil.which(name)
        if found:
            return found
    return None


POWERSHELL = _powershell()
needs_powershell = pytest.mark.skipif(
    POWERSHELL is None, reason="no PowerShell on this host; the script needs one"
)


def _environment() -> dict[str, str]:
    """The host's git identity and signing configuration must not decide a test."""
    environment = dict(os.environ)
    environment["GIT_CONFIG_GLOBAL"] = "NUL" if os.name == "nt" else "/dev/null"
    environment["GIT_CONFIG_SYSTEM"] = "NUL" if os.name == "nt" else "/dev/null"
    environment["GIT_AUTHOR_NAME"] = environment["GIT_COMMITTER_NAME"] = "test"
    environment["GIT_AUTHOR_EMAIL"] = environment["GIT_COMMITTER_EMAIL"] = (
        "test@example.invalid"
    )
    return environment


def run_process(argv: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """One subprocess entry point, so the launch inventory has one site here.

    Everything this file starts - git, and the script under test - goes through
    this helper, which is why ``tests/unit/test_mgba_launch_coverage.py`` needs
    exactly one exemption for this module. None of it starts an emulator.
    """
    return subprocess.run(
        argv,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=_environment(),
    )


class Fixture:
    """A primary repository plus the linked worktree the gate is allowed in.

    The gate refuses the main worktree structurally, and that refusal is not an
    artifact of the test: a primary has no `origin/master` to check against
    anyway, and the primary on this machine is read-only. So every scenario is
    built the shape a real ticket uses - a primary that owns the remote-tracking
    ref, and a linked worktree that holds the candidate - and the gate is always
    run in the linked worktree.
    """

    def __init__(self, root: Path, *, overlapping: bool) -> None:
        self.primary = root / ("overlap" if overlapping else "disjoint")
        self.worktree = self.primary / "worktree"
        self.primary.mkdir(parents=True)
        self.overlapping = overlapping
        self.primary_git(
            "init", "-q", "-b", "master", str(self.primary)
        )
        write = self.write
        write("shared.txt", "base\n")
        base = self.commit("base")
        write("candidate.txt", "candidate\n")
        self.candidate = self.commit("candidate change")
        # `-B master base` and not `checkout master`: the branch is created at
        # the base, and a plain `checkout master` detaches at the candidate
        # commit instead, making the two "sides" one commit and hiding overlap.
        self.primary_git("checkout", "-q", "-B", "master", base)
        marker = "candidate" if overlapping else "master"
        write(f"{marker}.txt", f"{marker}\n")
        self.target = self.commit("master change")
        self.primary_git("update-ref", "refs/remotes/origin/master", self.target)
        self.primary_git(
            "worktree", "add", "-q", "--detach", str(self.worktree), self.candidate
        )

    def primary_git(self, *arguments: str) -> str:
        completed = run_process(["git", *arguments], cwd=self.primary)
        assert completed.returncode == 0, completed.stderr
        return completed.stdout

    def git(self, *arguments: str) -> str:
        completed = run_process(["git", *arguments], cwd=self.worktree)
        assert completed.returncode == 0, completed.stderr
        return completed.stdout

    def write(self, path: str, text: str) -> None:
        (self.primary / path).write_text(text, encoding="utf-8")

    def commit(self, message: str) -> str:
        self.primary_git("add", "-A")
        self.primary_git("commit", "-q", "-m", message)
        return self.primary_git("rev-parse", "HEAD").strip()


def build_repository(root: Path, *, overlapping: bool) -> Fixture:
    """The scenario described in :class:`Fixture`."""
    return Fixture(root, overlapping=overlapping)


def run_script(
    repository: Path, candidate: str, *extra: str
) -> subprocess.CompletedProcess:
    """Run the real script against ``repository`` with ``candidate``."""
    assert POWERSHELL is not None
    return run_process(
        [
            POWERSHELL,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-Ref",
            candidate,
            "-RepoPath",
            str(repository),
            "-NoFetch",
            *extra,
        ]
    )


def test_the_script_refuses_the_primary_checkout_without_naming_a_path():
    """Prevents: a rehearsal running against the read-only primary checkout.

    Asserted from the source, so it holds on a host with no PowerShell: no
    machine-specific path is written down, which is what lets
    ``config/public_surface_exceptions.json`` carry no exception for this file.
    The refusal itself is proven by running the script, in
    ``test_the_primary_a_subdirectory_of_it_and_a_linked_worktree`` below; a
    source grep for a phrase the code must contain cannot fail on the behaviour
    the phrase describes.
    """
    source = SCRIPT.read_text(encoding="utf-8")
    assert "git-dir" in source or "--git-dir" in source
    assert "refusing to run in the primary checkout" in source
    assert "# Pre-merge check" in source
    assert not re.search(r"[A-Za-z]:\\\\|[A-Za-z]:[\\\\/](?:Users|Dev|tmp|Temp)", source), (
        "a machine-specific absolute path is back in the script"
    )
    assert "ProtectedCheckout" not in source, "the name compare is back"


def test_the_failure_text_is_an_instruction_not_a_block():
    """Prevents: an exit 1 that reads as a stop instead of a next step.

    The trade is kept on the review of RETRO-CI-002-20261012-112919, so the text
    must carry the instruction: rebase onto live master, re-run the focused tests,
    re-request. The review id is recorded in the script's own header.
    """
    source = SCRIPT.read_text(encoding="utf-8")
    for phrase in (
        "REBASE REQUIRED",
        "rebase onto live",
        "re-run the focused tests",
        "re-request the review",
        "MEASURED SAMPLE",
        "docs/research/PROJECT_STATE_AUDIT_RECONCILIATION.md",
    ):
        assert phrase in source, phrase


def test_the_script_has_no_byte_order_mark():
    """Prevents: a BOM, which has broken a tracked script on this machine.

    ``Set-Content -Encoding utf8`` has written a BOM that broke line 1 of a
    PowerShell file in this repository before.
    """
    raw = SCRIPT.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), "the script carries a UTF-8 BOM"
    assert raw.startswith(b"#"), raw[:20]


@needs_powershell
def test_the_script_parses():
    """Prevents: a syntax error reaching a lane that only finds it at run time."""
    parsed = run_process(
        [
            POWERSHELL,  # type: ignore[list-item]
            "-NoProfile",
            "-Command",
            "$e = $null; [void][System.Management.Automation.Language.Parser]::ParseFile("
            f"'{SCRIPT}', [ref]$null, [ref]$e); "
            "if ($e.Count) { $e | ForEach-Object { $_.ToString() }; exit 1 }",
        ]
    )
    assert parsed.returncode == 0, parsed.stdout + parsed.stderr


@needs_powershell
def test_a_master_commit_on_a_disjoint_path_passes(tmp_path):
    """The measured case: master moved under the candidate, touching nothing.

    MR 234 and MR 235 merged against exactly the master they were cut from; MR
    230's ten commits are the disjoint case if the two sides had not shared a
    path. Drift alone must stay a PASS, which is what keeps the gate usable.
    """
    fixture = build_repository(tmp_path, overlapping=False)
    completed = run_script(fixture.worktree, fixture.candidate)
    output = completed.stdout + completed.stderr
    assert completed.returncode == 0, output
    assert "PASS" in output, output
    assert "without an interaction" in output, output


@needs_powershell
def test_a_master_commit_on_a_path_the_candidate_changed_fails(tmp_path):
    """The case the gate exists for: both sides changed the same path.

    The MR 230 shape. It exits 1 and the text is an instruction, not a block.
    """
    fixture = build_repository(tmp_path, overlapping=True)
    completed = run_script(fixture.worktree, fixture.candidate)
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert "REBASE REQUIRED" in output, output
    assert "changed on both sides" in output, output
    assert "candidate.txt" in output, output
    # The trade is kept on the review of RETRO-CI-002-20261012-112919; the text
    # must carry the next step.
    assert "rebase onto live" in output, output
    assert "re-run the focused tests" in output, output
    assert "re-request the review" in output, output


@needs_powershell
def test_an_unchanged_master_is_a_pass(tmp_path):
    """The common case: the candidate was cut from the live master.

    MR 234 and MR 235 were exactly that. The gate must be silent on it, or it
    becomes noise that gets skipped.
    """
    fixture = build_repository(tmp_path, overlapping=False)
    # A branch on the live target, inside the linked worktree: master has
    # nothing this candidate does not already contain.
    fixture.git("checkout", "-q", "-B", "live", fixture.target)
    (fixture.worktree / "candidate.txt").write_text("candidate\n", encoding="utf-8")
    fixture.git("add", "-A")
    fixture.git("commit", "-q", "-m", "candidate on the live target")
    tip = fixture.git("rev-parse", "HEAD").strip()
    completed = run_script(fixture.worktree, tip)
    output = completed.stdout + completed.stderr
    assert completed.returncode == 0, output
    assert "PASS" in output, output
    assert "0 in both" in output, output


@needs_powershell
def test_a_conflicting_merge_is_a_failure(tmp_path):
    """The other fail-closed branch: the merge itself does not compose.

    Both sides change one file to different content, so ``git merge-tree`` cannot
    produce a tree. The gate must fail on that, not only on the both-sides path
    check, and the failure must say the tree could not be produced.
    """
    fixture = build_repository(tmp_path, overlapping=True)
    (fixture.primary / "candidate.txt").write_text("the other side\n", encoding="utf-8")
    fixture.primary_git(
        "commit", "-q", "-m", "master writes different content", "--", "candidate.txt"
    )
    target = fixture.primary_git("rev-parse", "HEAD").strip()
    fixture.primary_git("update-ref", "refs/remotes/origin/master", target)
    completed = run_script(fixture.worktree, fixture.candidate)
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert "could not produce a tree" in output, output


@needs_powershell
def test_a_supplied_merged_tree_digest_that_does_not_match_fails(tmp_path):
    """The only check on the predicted tree: a caller-supplied digest.

    No such digest is recorded anywhere today, so with no digest supplied the
    printed tree is never checked. This is the path that turns it into a failure,
    and it is the behaviour ``-ExpectMergedTree``'s own comment claims.

    Run on the overlapping fixture so two failures are listed, which is what
    makes the next-step list number each item: one instruction cannot show it.
    """
    fixture = build_repository(tmp_path, overlapping=True)
    completed = run_script(
        fixture.worktree, fixture.candidate, "-ExpectMergedTree", "0" * 40
    )
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert "is not the reviewed" in output, output
    assert "  1. " in output, output
    assert "  2. " in output, output


@needs_powershell
def test_report_only_reports_the_overlap_without_failing(tmp_path):
    """``-ReportOnly`` reports the overlap and exits 0, asked for by name.

    The flag has no default, and when it is passed the failure text is a report
    rather than a stop: the same both-sides path that exits 1 above exits 0 here.
    """
    fixture = build_repository(tmp_path, overlapping=True)
    completed = run_script(fixture.worktree, fixture.candidate, "-ReportOnly")
    output = completed.stdout + completed.stderr
    assert completed.returncode == 0, output
    assert "changed on both sides" in output, output
    assert "-ReportOnly, so this is a report and not a stop" in output, output


@needs_powershell
def test_the_primary_a_subdirectory_of_it_and_a_linked_worktree(tmp_path):
    """The refusal rule, run against all three paths rather than read as source.

    The rule is: the primary checkout is refused, a subdirectory of it is refused
    and the message names the checkout it sits in, and a linked worktree of the
    primary is allowed - every ticket worktree is one. Asserted by running the
    script, never by grepping its text: a source grep cannot fail on the
    behaviour the phrase describes.
    """
    fixture = build_repository(tmp_path, overlapping=False)
    primary = run_script(fixture.primary, fixture.candidate)
    primary_output = primary.stdout + primary.stderr
    assert primary.returncode == 1, primary_output
    assert "refusing to run in the primary checkout" in primary_output, primary_output
    subdirectory = fixture.primary / "docs"
    subdirectory.mkdir()
    nested = run_script(subdirectory, fixture.candidate)
    nested_output = nested.stdout + nested.stderr
    assert nested.returncode == 1, nested_output
    # The VALUE git reports, not a fragment the caller already supplied:
    # ``$RepoPath`` is the subdirectory, and its own text contains
    # ``fixture.primary.name``, so only the whole ``--show-toplevel`` proves the
    # message came from git rather than from the argument.
    toplevel = fixture.primary_git("rev-parse", "--show-toplevel").strip()
    assert toplevel, "the fixture primary has no --show-toplevel"
    #: The refusal is thrown through PowerShell, which wraps a long message to the
    #: console width and can split the reported path across two lines. Whitespace is
    #: therefore removed from both sides first: the message must still carry the value
    #: git reported, character for character, and nothing else about the check moves.
    assert "".join(toplevel.split()) in "".join(nested_output.split()), nested_output
    assert "not a git worktree" not in nested_output, nested_output
    linked = run_script(fixture.worktree, fixture.candidate)
    linked_output = linked.stdout + linked.stderr
    assert linked.returncode == 0, linked_output
    assert "PASS" in linked_output, linked_output


@needs_powershell
def test_the_primary_checkout_is_refused_and_a_linked_worktree_is_not(tmp_path):
    """The structural refusal, proven both ways on real worktrees.

    A linked worktree is the normal case for every ticket and must run; the main
    worktree is refused. Both are decided by one structural fact - the main
    worktree answers `.git` for `--git-dir`, a linked one answers an absolute
    path under the common directory - which is what makes the refusal
    independent of any machine's path. A subdirectory of the primary is refused
    earlier still, by the `.git` test at its root, so it never reaches that
    compare.

    The refusal is before the fetch, so nothing is written into the refused
    checkout. That order is read from the script rather than proven here: the
    fixture has already set `refs/remotes/origin/master`, and every run from
    this file passes `-NoFetch`, so this test cannot show it by an absent ref.
    """
    fixture = build_repository(tmp_path, overlapping=False)
    primary = run_script(fixture.primary, fixture.candidate)
    primary_output = primary.stdout + primary.stderr
    assert primary.returncode != 0, primary_output
    assert "refusing to run in the primary checkout" in primary_output, primary_output
    accepted = run_script(fixture.worktree, fixture.candidate)
    accepted_output = accepted.stdout + accepted.stderr
    assert accepted.returncode == 0, accepted_output
    assert "PASS" in accepted_output, accepted_output
