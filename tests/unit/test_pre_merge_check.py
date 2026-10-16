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

This file also holds the two halves of the owner's record requirement (ruled
2026-10-13): the gate's own classification of a candidate that changes a file in
``config/rom-dependent-tests.txt`` (a green GitHub run cannot cover it, because
those nodes SKIP on a runner), and the guard nodes for
``scripts/rom-focused-check.ps1``, the focused run that does cover it. One module
for one rule: the classification and the run it points at are the same decision.
The inventory is derived from source here rather than trusted, so a test file that
starts needing the image cannot drift out of it silently.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests import rom_support
from tests.gates import REPOSITORY_ROOT

SCRIPT = REPOSITORY_ROOT / "scripts" / "pre-merge-check.ps1"
FOCUSED_SCRIPT = REPOSITORY_ROOT / "scripts" / "rom-focused-check.ps1"
INVENTORY = REPOSITORY_ROOT / "config" / "rom-dependent-tests.txt"

#: The inventory member every throwaway repository in this file declares, and the
#: file a ROM-touching candidate changes. Its content in the gate's nodes is not
#: ROM-related at all, deliberately: the rule is the path.
ROM_TEST = "tests/unit/test_rom_reader_example.py"
NOT_ROM_TEST = "tests/unit/test_unrelated_example.py"
#: The canonical image's own file name, which is the name every copy keeps.
IMAGE_NAME = "Dragon Ball Z - Buu's Fury (U).gba"


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
    # ``scripts/rom-focused-check.ps1`` resolves its interpreter from PATH, and a
    # throwaway repository carries no environment of its own. The interpreter
    # running this file is the one that has the test runner, so it goes first.
    environment["PATH"] = os.pathsep.join(
        [str(Path(sys.executable).parent), environment.get("PATH", "")]
    )
    return environment


def run_process(
    argv: list[str],
    cwd: Path | None = None,
    *,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """One subprocess entry point, so the launch inventory has one site here.

    Everything this file starts - git, and the two scripts under test - goes
    through this helper, which is why ``tests/unit/test_mgba_launch_coverage.py``
    needs exactly one exemption for this module. None of it starts an emulator.
    """
    return subprocess.run(
        argv,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=environment if environment is not None else _environment(),
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

    def __init__(
        self,
        root: Path,
        *,
        overlapping: bool,
        changed: tuple[str, ...] = ("candidate.txt",),
        inventory: tuple[str, ...] | None = (ROM_TEST,),
        content: dict[str, str] | None = None,
    ) -> None:
        self.primary = root / ("overlap" if overlapping else "disjoint")
        self.worktree = self.primary / "worktree"
        self.primary.mkdir(parents=True)
        self.overlapping = overlapping
        self.primary_git(
            "init", "-q", "-b", "master", str(self.primary)
        )
        write = self.write
        write("shared.txt", "base\n")
        # The inventory both the gate and the focused run read. Written into the
        # BASE commit, so every tree in the fixture carries it: a candidate cut
        # from the base, and the master side the gate diffs against. The gate
        # refuses a repository without it, and one node below proves that.
        if inventory is not None:
            write(
                "config/rom-dependent-tests.txt",
                "# provenance\n" + "".join(f"{member}\n" for member in inventory),
            )
        base = self.commit("base")
        # The candidate's own paths.
        texts = content or {}
        for path in changed:
            write(path, texts.get(path, "candidate\n"))
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
        target = self.primary / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def commit(self, message: str) -> str:
        self.primary_git("add", "-A")
        self.primary_git("commit", "-q", "-m", message)
        return self.primary_git("rev-parse", "HEAD").strip()


def build_repository(
    root: Path,
    *,
    overlapping: bool,
    changed: tuple[str, ...] = ("candidate.txt",),
    inventory: tuple[str, ...] | None = (ROM_TEST,),
    content: dict[str, str] | None = None,
) -> Fixture:
    """The scenario described in :class:`Fixture`."""
    return Fixture(
        root,
        overlapping=overlapping,
        changed=changed,
        inventory=inventory,
        content=content,
    )


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


def run_focused(
    repository: Path,
    *extra: str,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run the focused-run script against ``repository``."""
    assert POWERSHELL is not None
    return run_process(
        [
            POWERSHELL,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(FOCUSED_SCRIPT),
            "-RepoPath",
            str(repository),
            *extra,
        ],
        environment=environment,
    )


#: PowerShell 7 renders a thrown message as coloured text and prefixes every
#: wrapped line with a ``Line |`` gutter, so the gutter's pipe lands INSIDE a phrase
#: that spans two lines and survives whitespace flattening: ``names no|test file``
#: against a phrase of ``names no test file``. GitHub run 38504730899 failed four
#: nodes on exactly that, on a message the gate had produced correctly. The colour
#: and the gutter are therefore removed before the whitespace.
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")
RENDERED_GUTTER = re.compile(r"(?m)^[ \t]*\|[ \t]?")


def _rendered(text: str) -> str:
    """The message with PowerShell's colour and its line gutter removed."""
    return RENDERED_GUTTER.sub("", ANSI_ESCAPE.sub("", text))


def _flat(text: str) -> "_Flattened":
    """The output with the rendering and all whitespace removed.

    PowerShell wraps a long line to the width of its console, and a thrown message
    can be split across two lines with padding - a digest included. PowerShell 5.1
    writes that plainly; PowerShell 7 colours it and gutters every line. So a phrase
    is compared with the colour, the gutter and the whitespace gone from BOTH sides,
    which the ``in`` override below does: ``"a long phrase" in _flat(output)``
    compares flat to flat, and every other use of the result still behaves as the
    string it is.
    """
    return _Flattened("".join(_rendered(text).split()))


class _Flattened(str):
    """A flat string whose ``in`` flattens the phrase it is asked about."""

    def __contains__(self, phrase: object) -> bool:
        return "".join(_rendered(str(phrase)).split()) in str(self)


def test_the_flattening_removes_the_power_shell_seven_error_rendering():
    """Run 38504730899: a wrapped, coloured message must still match its phrase.

    The gutter's pipe sat between ``no`` and ``test``, so removing whitespace alone
    left ``namesno|testfile`` against a phrase of ``names no test file``, and the
    four focused-run nodes failed on a refusal the gate had produced correctly.
    """
    rendered = (
        "\x1b[31;1mException: \x1b[0mscripts/rom-focused-check.ps1:71\x1b[0m\n"
        "\x1b[36;1mLine |\x1b[0m\n"
        '\x1b[36;1m  71 | \x1b[0mthrow "rom-focused-check: $Reason"\n'
        "\x1b[36;1m     | \x1b[0mrom-focused-check: worktree names no\n"
        "\x1b[36;1m     | \x1b[0mtest file, so there is nothing to run\n"
    )
    flat = _flat(rendered)
    assert "names no test file" in flat
    assert "there is nothing to run" in flat
    assert "\x1b" not in str(flat)
    # The preamble's own ``71 |`` is not a wrapped phrase and stays legible, so the
    # normalisation removed the gutter without flattening the message away.
    assert "Exception: scripts/rom-focused-check.ps1:71" in flat


def _canonical_image() -> Path | None:
    """A canonical image this host can read, or None.

    The same lookup the inventory's own modules make: the environment variables
    ``tests/rom_support.py`` honours, then that module's repository-relative path,
    then the sibling checkout
    ``tests/unit/dragonbyte_acceptance_support.py`` globs - it resolves
    ``Path(__file__).resolve().parents[2].parent / "log1-remake"``, which from a
    ticket worktree is the primary checkout. A host with no image (the GitHub
    runner) matches nothing here and the nodes that need one skip.
    """
    candidates = [rom_support.canonical_rom_path()]
    sibling = REPOSITORY_ROOT.parent / "log1-remake" / "roms"
    if sibling.is_dir():
        candidates.extend(sorted(sibling.glob("*.gba")))
    for candidate in candidates:
        if candidate is None or not candidate.is_file():
            continue
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest == rom_support.CANONICAL_ROM_SHA256:
            return candidate
    return None


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


# --- the record requirement: is a green GitHub run enough? ---------------------
#
# Owner ruling, 2026-10-13: a green GitHub Actions run on the merge SHA replaces
# the local full-CI record, EXCEPT for a change that touches a ROM-dependent test
# file, because those nodes SKIP on a runner. The gate must therefore say which
# case it is, in both cases, and stop with its own verdict in the second one.

@needs_powershell
def test_a_candidate_that_touches_an_inventory_member_needs_the_focused_run(tmp_path):
    """The drive to failure. The rule is the path, not the content.

    The changed file below holds nothing ROM-related at all: it is the path the
    inventory names that decides. The gate must stop with its own verdict, name
    that path, and never print the rebase text, whose meaning is a different rule.
    """
    fixture = build_repository(
        tmp_path, overlapping=False, changed=("candidate.txt", ROM_TEST)
    )
    completed = run_script(fixture.worktree, fixture.candidate)
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert (
        "pre-merge-check: record requirement: FOCUSED ROM RUN REQUIRED (1 changed "
        f"path(s) need the canonical image and SKIP on GitHub: {ROM_TEST})"
    ) in _flat(output), output
    assert "pre-merge-check: FOCUSED ROM RUN REQUIRED" in _flat(output), output
    assert "REBASE REQUIRED" not in _flat(output), output
    # The next step must name the run that covers it, honestly: a full record is
    # not what is required, and the copy has to be private.
    assert "scripts\\rom-focused-check.ps1" in _flat(output), output
    assert "PRIVATE COPY of the canonical image" in _flat(output), output
    assert "checked before and after" in _flat(output), output
    assert "a full local record is not required" in _flat(output), output


@needs_powershell
def test_a_candidate_that_touches_no_inventory_member_is_covered_by_the_github_run(
    tmp_path,
):
    """The control: a changed test file the inventory does not name.

    It exits 0, prints the classification line for the covered case, and never
    prints the focused-run verdict.
    """
    fixture = build_repository(
        tmp_path, overlapping=False, changed=(NOT_ROM_TEST,)
    )
    completed = run_script(fixture.worktree, fixture.candidate)
    output = completed.stdout + completed.stderr
    assert completed.returncode == 0, output
    assert (
        "pre-merge-check: record requirement: GITHUB RUN SUFFICES (no changed path "
        "is a ROM-dependent test file)"
    ) in _flat(output), output
    assert "pre-merge-check: PASS" in _flat(output), output
    assert "FOCUSED ROM RUN REQUIRED" not in _flat(output), output


@needs_powershell
def test_report_only_reports_the_focused_requirement_without_failing(tmp_path):
    """``-ReportOnly`` downgrades this stop the way it downgrades the overlap."""
    fixture = build_repository(tmp_path, overlapping=False, changed=(ROM_TEST,))
    completed = run_script(fixture.worktree, fixture.candidate, "-ReportOnly")
    output = completed.stdout + completed.stderr
    assert completed.returncode == 0, output
    assert "record requirement: FOCUSED ROM RUN REQUIRED" in _flat(output), output
    assert "pre-merge-check: FOCUSED ROM RUN REQUIRED" in _flat(output), output
    assert "-ReportOnly, so this is a report and not a stop" in _flat(output), output


@needs_powershell
def test_a_repository_without_the_inventory_is_refused_by_name(tmp_path):
    """Fail closed: no inventory, no classification, no PASS.

    An absent inventory would otherwise classify every candidate as covered by a
    GitHub run, which is the one answer the gate must never guess at.
    """
    fixture = build_repository(tmp_path, overlapping=False, inventory=None)
    completed = run_script(fixture.worktree, fixture.candidate)
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert "config/rom-dependent-tests.txt is missing" in _flat(output), output
    assert "GITHUB RUN SUFFICES" not in _flat(output), output
    assert "pre-merge-check: PASS" not in _flat(output), output


#: Source markers that say a test file resolves the canonical image, or an
#: artefact derived from it. Measured on this tree they match 51 files under
#: tests/unit: the record's own 32 census members, the file that is newer than the
#: record and gated (test_dialogue_render.py), the pin test below, and the 18
#: exclusions. The inventory holds exactly those 32 plus test_dialogue_render.py,
#: which is also exactly the 33 files the GitHub run for 7e7f537 records as ROM
#: skips (run 38498291601, 20261014, step 01-test-sdk).
ROM_MARKERS = (
    r"rom_support",
    r"SIBLING_CHECKOUT",
    r"dragonbyte_acceptance_support",
    r"canonical_rom_path",
    r"canonical_rom_bytes",
    r"canonical_rom_sha256",
    r"CANONICAL_ROM_SHA256",
    r"mutable_rom",
    r"canonical_profile",
    r"WEBFOOT_V4A_IMAGE",
    r"build/atlas/atlas\.jsonl",
    r"rom011_",
    r"rom012_",
    r"WEBFOOT_MGBA_DEV",
    r"LOG1_MAIN_CHECKOUT",
    r"DEV_MGBA",
    r"roms/Dragon Ball Z",
    r"roms/DragonBallZ",
    r"\*Buu\*\.gba",
    r"ROM_DEFAULT",
    r"WEBFOOT_BUU_ROM",
    r"LOGX_CANONICAL_ROM",
)

#: Derived by a marker and NOT ROM-dependent, each with the reason a reader can
#: check. An exclusion is a documented judgement, not a silent filter. Every one of
#: these existed at the record's commit, unless its own reason says otherwise, and
#: the record's skip census holds no skip line for it, so its marker is satisfied
#: without the image in a run that has none. A file that is genuinely gated and
#: merely NEWER than the record belongs in the inventory instead, which is where
#: test_dialogue_render.py is.
ROM_MARKER_EXCLUSIONS = {
    "tests/unit/dragonbyte_acceptance_support.py": (
        "matches SIBLING_CHECKOUT; it is not a test module at all but the lookup "
        "the 19 DragonByte modules import"
    ),
    "tests/unit/test_allocation_authority.py": (
        "matches canonical_profile; existed at the record's commit and the census "
        "holds no skip for it, so the profile it uses is synthetic"
    ),
    "tests/unit/test_atlas_identity.py": (
        "matches the atlas index path; the census holds no skip for it"
    ),
    "tests/unit/test_dragonbyte_acceptance_image_guard.py": (
        "matches the guard helper's name; it tests that guard against a temporary "
        "tree and the census holds no skip for it"
    ),
    "tests/unit/test_dragonbyte_coverage.py": (
        "matches CANONICAL_PROFILE; the census holds no skip for it"
    ),
    "tests/unit/test_extent_profile_authority.py": (
        "matches canonical_profile and CANONICAL_ROM_SHA256; the census holds no "
        "skip for it, so the constant is compared, not the image read"
    ),
    "tests/unit/test_gameplay_effect_native.py": (
        "matches canonical_profile; the census holds no skip for it"
    ),
    "tests/unit/test_map_layout_provenance.py": (
        "matches the canonical image path; it requires provenance to be recorded "
        "and the census holds no skip for it"
    ),
    "tests/unit/test_mgba_capture.py": (
        "matches the rom011 token; that names an instrumented build, not the game "
        "image, and the census holds no skip for it"
    ),
    "tests/unit/test_mgba_identity_gate.py": (
        "matches rom011_ and rom012_; those name instrumented builds, and the "
        "census holds no skip for it"
    ),
    "tests/unit/test_profile_authority_contract.py": (
        "matches canonical_profile; the census holds no skip for it"
    ),
    "tests/unit/test_public_release.py": (
        "matches the canonical image path inside the check that bans machine paths "
        "from published files, and the census holds no skip for it"
    ),
    "tests/unit/test_readability.py": (
        "matches the canonical image path as a readability fixture, not as an "
        "input, and the census holds no skip for it"
    ),
    "tests/unit/test_rom011_runtime.py": (
        "matches rom011_; that build is an emulator tree, not the game image, and "
        "the census holds no skip for it"
    ),
    "tests/unit/test_rom012_runtime.py": (
        "matches rom012_; that build is an emulator tree, not the game image, and "
        "the census holds no skip for it"
    ),
    "tests/unit/test_runtime_evidence_bundle.py": (
        "matches rom011_ and rom012_; it bundles evidence from those builds, and "
        "the census holds no skip for it"
    ),
    "tests/unit/test_text_engine_profile_row.py": (
        "matches canonical_profile through the name of the engine constant it reads; "
        "its images come from the synthetic text fixture"
    ),
    "tests/unit/test_ticket_worktree_setup.py": (
        "matches WEBFOOT_BUU_ROM and LOGX_CANONICAL_ROM as names to copy into a "
        "worktree, and the census holds no skip for it"
    ),
    "tests/unit/test_pre_merge_check.py": (
        "the pin test itself, excluded on the owner's ruling of 2026-10-13 and for the "
        "self-reference below. Self-reference: it defines the marker literals and "
        "imports tests.rom_support, so the sweep matches the file that defines the "
        "markers for ever. Measured: the GitHub run 38498291601 for 7e7f537 recorded "
        "0 skips in this file and ran its nodes, so at that commit the exception did "
        "not reach it. Stated plainly because it cuts the other way: the four "
        "focused-run nodes this change adds DO skip on a runner without the image, so "
        "on those terms the exception would reach this file; the ruling, not the "
        "derivation, is what keeps it out"
    ),
}


def test_the_inventory_is_the_marker_derivation():
    """The inventory is derived from source and pinned to the file, both ways.

    A marker sweep alone cannot be exact - several modules name an image path
    without needing the image - so the derivation is a sweep minus an explicit,
    reasoned exclusion list. The point of the pin is drift: a test file that
    starts reading the canonical image is derived here and fails until it is
    either added to ``config/rom-dependent-tests.txt`` or excluded with a reason,
    and a member that stops being derived fails too.
    """
    declared = [
        line.strip()
        for line in INVENTORY.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert declared, "the inventory is empty"
    assert declared == sorted(declared), f"the inventory is not sorted: {declared}"
    assert len(set(declared)) == len(declared), "the inventory repeats a path"
    for relative in declared:
        assert (REPOSITORY_ROOT / relative).is_file(), (
            f"{relative} is in the inventory but is not a file in this tree"
        )

    derived: set[str] = set()
    for path in sorted((REPOSITORY_ROOT / "tests" / "unit").glob("*.py")):
        source = path.read_text(encoding="utf-8")
        if any(re.search(marker, source, re.IGNORECASE) for marker in ROM_MARKERS):
            derived.add(f"tests/unit/{path.name}")

    excluded = set(ROM_MARKER_EXCLUSIONS)
    assert excluded <= derived, (
        "an exclusion is no longer derived, so it documents nothing: "
        f"{sorted(excluded - derived)}"
    )
    for relative, reason in ROM_MARKER_EXCLUSIONS.items():
        assert reason.strip(), f"{relative} is excluded with no reason"

    missing = sorted(set(declared) - (derived - excluded))
    extra = sorted((derived - excluded) - set(declared))
    assert not missing, (
        "in the inventory but not derived from any marker, so a reader cannot "
        f"check why it is there: {missing}"
    )
    assert not extra, (
        "derived from a marker but not in the inventory: add it, or give it a "
        f"reason in ROM_MARKER_EXCLUSIONS: {extra}"
    )


# --- the focused run the verdict points at -------------------------------------
#
# One module for one rule: the gate's classification and the script it tells the
# operator to run are the same decision, so the guard nodes for
# scripts/rom-focused-check.ps1 live here rather than in a file of their own.
# Every refusal below is driven by running the real script against a throwaway
# repository. The nodes that need a readable canonical image skip on a host
# without one, exactly as tests/unit/test_rom_fixture_isolation.py does.

@needs_powershell
def test_the_focused_run_refuses_a_missing_image(tmp_path):
    fixture = build_repository(tmp_path, overlapping=False, changed=(ROM_TEST,))
    completed = run_focused(
        fixture.worktree, "-Image", str(tmp_path / "no-such-image.gba")
    )
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert "rom-focused-check: the image" in _flat(output), output
    assert "does not exist" in _flat(output), output


@needs_powershell
def test_the_focused_run_refuses_an_image_that_is_not_canonical(tmp_path):
    """The digest gate, and it names both digests rather than only refusing."""
    fixture = build_repository(tmp_path, overlapping=False, changed=(ROM_TEST,))
    not_the_image = tmp_path / "not-the-canonical-image.gba"
    not_the_image.write_bytes(b"this is not the canonical image\n")
    completed = run_focused(fixture.worktree, "-Image", str(not_the_image))
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert "is not the canonical image" in _flat(output), output
    # The digest is long enough for PowerShell to wrap it, so it is compared on the
    # flattened view too: the value must survive wherever the line broke.
    assert rom_support.CANONICAL_ROM_SHA256.upper() in _flat(output).upper(), output


@needs_powershell
def test_the_focused_run_refuses_a_missing_or_empty_inventory(tmp_path):
    """Both halves of the same fail-closed rule, named differently."""
    absent = build_repository(
        tmp_path / "absent", overlapping=False, changed=(ROM_TEST,), inventory=None
    )
    absent_run = run_focused(absent.worktree)
    absent_output = absent_run.stdout + absent_run.stderr
    assert absent_run.returncode == 1, absent_output
    assert "config/rom-dependent-tests.txt is missing" in _flat(absent_output), (
        absent_output
    )

    empty = build_repository(
        tmp_path / "empty", overlapping=False, changed=(ROM_TEST,), inventory=()
    )
    empty_run = run_focused(empty.worktree)
    empty_output = empty_run.stdout + empty_run.stderr
    assert empty_run.returncode == 1, empty_output
    assert "config/rom-dependent-tests.txt" in _flat(empty_output), empty_output
    assert "names no test file" in _flat(empty_output), empty_output


@needs_powershell
def test_the_focused_run_refuses_a_pre_existing_destination(tmp_path):
    """Never write through a name that exists.

    ``Copy-Item`` writes through an existing name, so a destination that already
    exists may be a hard link to the canonical image and copying into it would
    edit the image. The refusal comes before the image is even resolved, which is
    what makes it drivable here without one.
    """
    fixture = build_repository(tmp_path, overlapping=False, changed=(ROM_TEST,))
    staging = fixture.worktree / "build" / "pre-existing-destination"
    destination = staging / "log1-remake" / "roms" / IMAGE_NAME
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"a name this run must not write through\n")
    completed = run_focused(
        fixture.worktree,
        "-StagingRoot",
        str(staging),
        "-Image",
        str(tmp_path / "no-such-image.gba"),
    )
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert f"the destination {destination} already exists" in _flat(output), output
    assert "link to the canonical image" in _flat(output), output
    assert destination.read_bytes() == b"a name this run must not write through\n"


@needs_powershell
def test_the_focused_run_refuses_a_staging_sibling_that_is_not_its_own_copy(tmp_path):
    """The sibling the DragonByte modules glob must hold this run's copy only."""
    fixture = build_repository(tmp_path, overlapping=False, changed=(ROM_TEST,))
    staging = fixture.worktree / "build" / "sibling-preoccupied"
    sibling = staging / "log1-remake" / "roms"
    sibling.mkdir(parents=True)
    (sibling / "some-other-image.gba").write_bytes(b"not the canonical image\n")
    completed = run_focused(
        fixture.worktree,
        "-StagingRoot",
        str(staging),
        "-Image",
        str(tmp_path / "no-such-image.gba"),
    )
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert f"the staging sibling {sibling} already holds some-other-image.gba" in (
        _flat(output)
    ), output
    assert "copy of the canonical image" in _flat(output), output


@needs_powershell
def test_the_focused_run_refuses_a_hard_link_to_the_canonical_image(tmp_path):
    """The R3 shape, proved by file identity: the run must not write through it.

    The destination is a genuine hard link to the genuine canonical image, made in
    the staging root this test chose, exactly as
    ``test_rom_fixture_isolation.test_a_hard_link_to_a_protected_input_is_refused``
    makes one. After the refusal the two names must still be one file and the
    image's digest must be unchanged, which is the whole point of the check.
    """
    canonical = _canonical_image()
    if canonical is None:
        pytest.skip("no canonical image reachable on this host")
    fixture = build_repository(tmp_path, overlapping=False, changed=(ROM_TEST,))
    staging = fixture.worktree / "build" / "hard-link-destination"
    destination = staging / "log1-remake" / "roms" / IMAGE_NAME
    destination.parent.mkdir(parents=True)
    try:
        os.link(canonical, destination)
    except OSError as exc:  # pragma: no cover - cross-volume temporary root
        pytest.skip(f"this host cannot hard-link across these directories: {exc}")
    before = hashlib.sha256(canonical.read_bytes()).hexdigest()
    assert os.path.samefile(destination, canonical)

    completed = run_focused(
        fixture.worktree,
        "-StagingRoot",
        str(staging),
        "-Image",
        str(canonical),
    )
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert f"the destination {destination} already exists" in _flat(output), output
    assert os.path.samefile(destination, canonical), "the run wrote through the link"
    assert hashlib.sha256(canonical.read_bytes()).hexdigest() == before


@needs_powershell
def test_the_focused_run_passes_on_a_private_copy(tmp_path):
    """The real run: a private copy, the environment for the child, and cleanup."""
    canonical = _canonical_image()
    if canonical is None:
        pytest.skip("no canonical image reachable on this host")
    content = {
        ROM_TEST: (
            "import os\n"
            "\n"
            "\n"
            "def test_the_child_reads_the_private_copy():\n"
            '    path = os.environ["WEBFOOT_BUU_ROM"]\n'
            "    assert os.path.isfile(path)\n"
            "    assert os.path.getsize(path) == 8388608\n"
        )
    }
    fixture = build_repository(
        tmp_path, overlapping=False, changed=(ROM_TEST,), content=content
    )
    staging = fixture.worktree / "build" / "private-copy"
    completed = run_focused(
        fixture.worktree,
        "-Image",
        str(canonical),
        "-FocusFiles",
        ROM_TEST,
        "-StagingRoot",
        str(staging),
    )
    output = completed.stdout + completed.stderr
    assert completed.returncode == 0, output
    assert f"{ROM_TEST} executed 1, skipped 0" in _flat(output), output
    assert "PASS, 1 node(s) executed against a private copy" in _flat(output), output
    assert not staging.exists(), f"the staging tree was left behind: {staging}"


@needs_powershell
def test_the_focused_run_fails_a_run_that_executed_no_node(tmp_path):
    """Zero executed is a failure, and the skipped node is reported as skipped.

    The owner asked for two drives here - a run where zero nodes executed exits
    non-zero, and the all-skipped case is reported as skipped rather than as a
    pass. They are one run: the node below skips, pytest exits 0, and the script
    must both say what skipped and fail anyway.
    """
    canonical = _canonical_image()
    if canonical is None:
        pytest.skip("no canonical image reachable on this host")
    content = {
        ROM_TEST: (
            "import pytest\n"
            "\n"
            "\n"
            "def test_this_only_skips():\n"
            '    pytest.skip("the zero-executed guard: nothing here runs")\n'
        )
    }
    fixture = build_repository(
        tmp_path, overlapping=False, changed=(ROM_TEST,), content=content
    )
    staging = fixture.worktree / "build" / "all-skipped"
    completed = run_focused(
        fixture.worktree,
        "-Image",
        str(canonical),
        "-FocusFiles",
        ROM_TEST,
        "-StagingRoot",
        str(staging),
    )
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert f"{ROM_TEST} executed 0, skipped 1" in _flat(output), output
    assert "the zero-executed guard: nothing here runs" in _flat(output), output
    assert "no node executed" in _flat(output), output
    assert "PASS" not in _flat(output), output


@needs_powershell
def test_the_focused_run_fails_when_a_private_copy_moved(tmp_path):
    """The detective half: a write through the copy is caught after the run.

    The child test below is the shape the R3 incident had, aimed at the private
    copy rather than at the image. The run's own post-run digests must notice it,
    and the image's digest must still be the canonical one.
    """
    canonical = _canonical_image()
    if canonical is None:
        pytest.skip("no canonical image reachable on this host")
    content = {
        ROM_TEST: (
            "import os\n"
            "\n"
            "\n"
            "def test_it_writes_through_the_private_copy():\n"
            '    with open(os.environ["WEBFOOT_BUU_ROM"], "r+b") as handle:\n'
            '        handle.write(b"\\x00")\n'
        )
    }
    fixture = build_repository(
        tmp_path, overlapping=False, changed=(ROM_TEST,), content=content
    )
    staging = fixture.worktree / "build" / "copy-moved"
    before = hashlib.sha256(canonical.read_bytes()).hexdigest()
    completed = run_focused(
        fixture.worktree,
        "-Image",
        str(canonical),
        "-FocusFiles",
        ROM_TEST,
        "-StagingRoot",
        str(staging),
    )
    output = completed.stdout + completed.stderr
    assert completed.returncode == 1, output
    assert "a private copy moved during this run" in _flat(output), output
    assert "PASS" not in _flat(output), output
    assert hashlib.sha256(canonical.read_bytes()).hexdigest() == before
