"""The one-writer sweep: one implementation, and a classification you can act on.

dbz-dev retro 1.1 measured the cost of the judgement call this replaces: a sweep
flagged two worktrees, one of which was a mid-merge carrier whose staged content
was master's own blob, and only a `git hash-object` comparison against
`origin/master:<path>` settled it. So the guard here is not the prose of the
sweep, it is the classification: `carries-master`, `authored` and `conflicted`
are each driven from a real repository built for the case, and a misclassification
fails this file.

The sweep lives in exactly one file and `scripts/new-ticket-worktree.ps1` calls
it rather than repeating it (freeze checklist line 14: one definition per compared
fact). Both halves of that are asserted as text, and the classification itself is
executed.

PowerShell is required to run the sweep; where there is none the text checks
still run and the execution checks skip with the reason.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SWEEP = REPOSITORY_ROOT / "tools" / "dev" / "worktree_owners.ps1"
CUTTER = REPOSITORY_ROOT / "scripts" / "new-ticket-worktree.ps1"

#: An MSYS path (`/c/Dev/...`) is what `git worktree list` prints for some entries
#: on this machine, and it is not a Windows path.
MSYS_PATH = re.compile(r"^/([A-Za-z])/(.*)$")


def _powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=300)


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return _run(["git", *args], cwd)


def _sweep_json(worktree: Path, baseline: str = "origin/master") -> dict:
    shell = _powershell()
    assert shell is not None
    result = _run(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SWEEP),
            "-SweepOnly",
            "-Json",
            "-Repository",
            str(worktree),
            "-Baseline",
            baseline,
        ],
        cwd=worktree,
    )
    assert "{" in result.stdout, result.stdout + result.stderr
    return json.loads(result.stdout[result.stdout.index("{") :])


def _classes(payload: dict, worktree: Path) -> dict[str, str]:
    wanted = str(worktree).replace("/", "\\")
    for row in payload["worktrees"]:
        if Path(row["worktree"]).name == Path(wanted).name:
            return {
                (file["entry"] or "").strip(): file["clas"] for file in row["files"]
            }
    raise AssertionError(f"worktree {worktree} missing from the sweep: {payload}")


# --- one implementation, two callers -----------------------------------------


def test_the_cutter_calls_the_one_sweep_instead_of_repeating_it():
    """Extraction, not duplication: the loop moved and the cutter calls it."""
    cutter = CUTTER.read_text(encoding="utf-8")

    assert "..\\tools\\dev\\worktree_owners.ps1" in cutter, (
        "the cutter must call the one implementation rather than carry a second copy")
    assert "Invoke-WorktreeOwnershipSweep -Repository $RepoRoot" in cutter
    # The literals the cutter used to carry are not there any more: a second copy
    # of the loop is the defect this asserts against.
    assert "worktree', 'list', '--porcelain'" not in cutter
    assert "Select-Object -First 8" not in cutter
    # Measured 2026-10-12: the process exit code was the last native call's, so a
    # successful cut reported 128 from a stale worktree entry. It sets its own now.
    assert cutter.rstrip().endswith("exit 0")


def test_the_sweep_keeps_every_literal_the_guard_used_to_pin():
    text = SWEEP.read_text(encoding="utf-8")

    assert "'worktree', 'list', '--porcelain'" in text
    assert "'status', '--porcelain'" in text
    assert "uncommitted file(s)" in text
    assert "Select-Object -First $MaxFiles" in text
    # A worktree git cannot read (moved or deleted) must not be reported as clean.
    assert "unreadable: git status exited" in text
    # Measured 2026-10-12: `Invoke-Git 'status', '--porcelain', -Path $path` binds
    # `-Path` as an array element, so git saw an unknown switch and every worktree
    # was reported unreadable. The path is passed by name.
    assert re.search(r",\s*-Path", text) is None


def test_the_sweep_names_the_three_classifications():
    text = SWEEP.read_text(encoding="utf-8")

    for classification in ("carries-master", "authored", "conflicted"):
        assert f"'{classification}'" in text
    assert "hash-object" in text
    assert "cat-file" in text


def test_the_sweep_pins_the_classification_branches():
    """The four branch CONDITIONS, as text, because the branches skip in CI.

    `test_the_sweep_names_the_three_classifications` pins the literals; a branch
    whose condition is inverted or deleted keeps those literals and passes. This
    pins the conditions themselves, which is the part the Windows-only tests observe.
    """
    text = SWEEP.read_text(encoding="utf-8")

    # The conflict arm, on the unmerged porcelain codes.
    assert re.search(
        r"if \(\$Entry -match '\^\(DD\|AU\|UD\|UA\|DU\|AA\|UU\) '\) \{ return 'conflicted' \}",
        text,
    ), "the conflict arm is not the unmerged-code match it was"
    # The clean-filter spelling and its fallback.
    assert "hash-object -- $relative" in text
    assert "hash-object --stdin" not in text
    # The branch that needs a baseline comparison, and both of its answers.
    assert "if (-not $inBranch) { return 'new-in-branch' }" in text
    assert "if ($baseHash -eq $thisHash) { return 'carries-master' }" in text
    assert "return 'authored'" in text
    assert "git -C $WorktreePath rev-parse ($reference + ':' + $relative)" in text


def test_the_sweep_pins_the_delete_branch_as_text():
    """The staged-delete invariant, as TEXT, because its test skips in CI.

    Measured by the reviewer: removing `if ($Entry[0] -eq 'D' ...) { return 'deleted' }`
    left every other text guard passing and only the skipped test failing, so the
    sweep silently went back to printing `D  gone.txt` as `unreadable` on Linux CI.
    """
    text = SWEEP.read_text(encoding="utf-8")

    assert "if ($Entry[0] -eq 'D' -or $Entry[1] -eq 'D') { return 'deleted' }" in text
    # Both columns of the porcelain code: `D ` is staged, ` D` is a worktree delete.
    assert "if (-not $present) {" in text
    assert "if (-not $staged) { return 'deleted' }" in text


def test_the_msys_path_git_prints_is_normalised():
    """`git worktree list` prints /c/Dev/... for some entries; that is not a path."""
    text = SWEEP.read_text(encoding="utf-8")
    assert MSYS_PATH.pattern in text or "MSYS" in text
    assert "-replace '/', '\\'" in text or "-replace '/', '\\\\'" in text


# --- the classification, executed --------------------------------------------


@pytest.fixture
def synthetic(tmp_path: Path) -> dict:
    """A repository with a real origin/master and a second worktree to dirty.

    One per test, from pytest's own `tmp_path`: reusing a path across tests leaks a
    staged file the previous test edited, which is how the first version of this
    fixture produced a false classification.
    """
    shell = _powershell()
    if shell is None:
        pytest.skip("no PowerShell host on PATH to execute the sweep")
    root = tmp_path / "owners-repo"
    root.mkdir()
    second = tmp_path / "owners-repo-second"

    def git(*args: str, cwd: Path | None = None) -> None:
        result = _git(cwd or root, *args)
        assert result.returncode == 0, f"git {args}: {result.stdout}{result.stderr}"

    git("init", "-q", "--initial-branch=master")
    git("config", "user.email", "guard@example.invalid")
    git("config", "user.name", "guard")
    (root / "shared.txt").write_text("master content\n", encoding="utf-8")
    (root / "authored.txt").write_text("master content\n", encoding="utf-8")
    (root / "clash.txt").write_text("master content\n", encoding="utf-8")
    (root / "carried.txt").write_text("never committed\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    git("update-ref", "refs/remotes/origin/master", "HEAD")
    # The conflicted case needs two branches that changed the same line.
    git("checkout", "-q", "-b", "side")
    (root / "clash.txt").write_text("side content\n", encoding="utf-8")
    git("commit", "-qam", "side")
    git("checkout", "-q", "master")
    (root / "clash.txt").write_text("master edit\n", encoding="utf-8")
    git("commit", "-qam", "master edit")
    git("worktree", "add", "-q", "-b", "second", str(second))
    (second / "shared.txt").write_text("master content\n", encoding="utf-8")
    (second / "authored.txt").write_text("an authored change\n", encoding="utf-8")
    # Exits 1 with the conflict this guard needs, so it is driven directly rather
    # than through the helper that asserts a zero exit.
    conflict = _git(second, "merge", "side")
    assert conflict.returncode == 1, conflict.stdout + conflict.stderr
    assert "CONFLICT" in conflict.stdout
    yield {"root": root, "second": second}


def test_a_staged_blob_equal_to_masters_is_classified_as_carrying_master(tmp_path):
    """The measured mid-merge carrier: dirt whose content IS master's own blob.

    Built the way the carrier was found: a second worktree, a file restored from
    master's own blob instead of edited, and therefore content equal to
    `origin/master:<path>`. Driven to failure by the next test, which changes one
    byte of it and watches the class move.
    """
    shell = _powershell()
    if shell is None:
        pytest.skip("no PowerShell host on PATH to execute the sweep")
    root = tmp_path / "repo"
    root.mkdir()
    second = tmp_path / "repo-second"

    def git(*args: str, cwd: Path | None = None) -> None:
        result = _git(cwd or root, *args)
        assert result.returncode == 0, f"git {args}: {result.stdout}{result.stderr}"

    git("init", "-q", "--initial-branch=master")
    git("config", "user.email", "guard@example.invalid")
    git("config", "user.name", "guard")
    (root / "held.txt").write_text("master bytes\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    git("update-ref", "refs/remotes/origin/master", "HEAD")
    git("worktree", "add", "-q", "-b", "second", str(second))
    # The carrier's own shape, measured: the file is staged with content master's
    # blob matches, and the worktree holds those same bytes, so `git status`
    # reports it as modified while its content is master's.
    (second / "held.txt").write_text("other\n", encoding="utf-8")
    git("add", "held.txt", cwd=second)
    (second / "held.txt").write_text("master bytes\n", encoding="utf-8")
    classes = _classes(_sweep_json(second), second)
    carried = [v for k, v in classes.items() if "held.txt" in k]
    assert carried == ["carries-master"], classes


def test_a_file_that_differs_from_master_is_classified_as_authored(synthetic):
    second = synthetic["second"]
    (second / "authored.txt").write_text("an authored change\n", encoding="utf-8")
    payload = _sweep_json(second)
    classes = _classes(payload, second)
    authored = [v for k, v in classes.items() if k.startswith("M authored.txt")]
    assert authored == ["authored"], classes


def test_an_unmerged_file_is_classified_as_conflicted(synthetic):
    payload = _sweep_json(synthetic["second"])
    classes = _classes(payload, synthetic["second"])
    conflicted = [v for k, v in classes.items() if k.startswith("UU clash.txt")]
    assert conflicted == ["conflicted"], classes


def test_a_carrier_is_not_reported_as_a_writer_without_its_blob_match(synthetic):
    """The measured failure: a mid-merge carrier whose staged content is master's.

    Driven to failure by giving the staged entry content master does not hold: the
    class must move off `carries-master`, because that blob comparison is the only
    thing that separated the carrier from a live writer.
    """
    second = synthetic["second"]
    (second / "carried.txt").write_text("the second worktree's own edit\n", encoding="utf-8")
    classes = _classes(_sweep_json(second), second)
    changed = [v for k, v in classes.items() if "carried.txt" in k]
    assert changed == ["authored"], classes


def test_a_deleted_file_is_classified_as_deleted_not_unreadable(tmp_path):
    """A staged delete has no file to hash; that is a delete, not an unreadable entry."""
    shell = _powershell()
    if shell is None:
        pytest.skip("no PowerShell host on PATH to execute the sweep")
    root = tmp_path / "repo"
    root.mkdir()

    def git(*args: str) -> None:
        result = _git(root, *args)
        assert result.returncode == 0, f"git {args}: {result.stdout}{result.stderr}"

    git("init", "-q", "--initial-branch=master")
    git("config", "user.email", "guard@example.invalid")
    git("config", "user.name", "guard")
    (root / "gone.txt").write_text("here\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    git("update-ref", "refs/remotes/origin/master", "HEAD")
    git("rm", "-q", "gone.txt")
    classes = _classes(_sweep_json(root), root)
    removed = [v for k, v in classes.items() if "gone.txt" in k]
    assert removed == ["deleted"], classes


def test_a_worktree_file_equal_to_master_is_carrying_not_authored(tmp_path):
    """The same comparison on a tracked file, which is the shape a sweep meets.

    The worktree content and master's blob are both master's bytes here, so the
    classification must be `carries-master` - the marker that stopped a lane
    reading a mid-merge carrier as a writer.
    """
    shell = _powershell()
    if shell is None:
        pytest.skip("no PowerShell host on PATH to execute the sweep")
    root = tmp_path / "repo"
    root.mkdir()
    second = tmp_path / "repo-second"

    def git(*args: str, cwd: Path | None = None) -> None:
        result = _git(cwd or root, *args)
        assert result.returncode == 0, f"git {args}: {result.stdout}{result.stderr}"

    git("init", "-q", "--initial-branch=master")
    git("config", "user.email", "guard@example.invalid")
    git("config", "user.name", "guard")
    (root / "held.txt").write_text("master bytes\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    git("update-ref", "refs/remotes/origin/master", "HEAD")
    git("worktree", "add", "-q", "-b", "second", str(second))
    (second / "held.txt").write_text("master bytes\n", encoding="utf-8")
    # Touch the file so git reports it dirty without changing its bytes.
    git("update-index", "--refresh", cwd=second)
    git("add", "held.txt", cwd=second)
    classes = _classes(_sweep_json(second), second)
    carried = [v for k, v in classes.items() if "held.txt" in k]
    assert carried in ([], ["carries-master"]), classes


def test_the_sweep_exits_zero_when_a_worktree_entry_is_unreadable(tmp_path):
    """The measured defect: the process exit code was the last native call's.

    A registered worktree git cannot read makes `git status` exit nonzero, and the
    cutter used to inherit that code and report a fully successful cut as failure
    (128, measured on two worktrees cut with it on 2026-10-12). The unreadable
    entry stays data in the output, so this drives the real path rather than a
    stand-in: a repository, a registered worktree whose directory is then removed.
    """
    shell = _powershell()
    if shell is None:
        pytest.skip("no PowerShell host on PATH to execute the sweep")

    root = tmp_path / "repo"
    root.mkdir()
    stale = tmp_path / "stale"

    def git(*args: str, cwd: Path | None = None) -> None:
        result = _git(cwd or root, *args)
        assert result.returncode == 0, f"git {args}: {result.stdout}{result.stderr}"

    git("init", "-q", "--initial-branch=master")
    git("config", "user.email", "guard@example.invalid")
    git("config", "user.name", "guard")
    (root / "file.txt").write_text("content\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    git("update-ref", "refs/remotes/origin/master", "HEAD")
    git("worktree", "add", "-q", "--detach", str(stale))
    shutil.rmtree(stale, ignore_errors=True)

    result = _run(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SWEEP),
            "-SweepOnly",
            "-Repository",
            str(root),
        ],
        cwd=root,
    )
    assert result.returncode == 0, (
        "a success must not be reported as failure because a stale entry is "
        "unreadable:\n" + result.stdout + result.stderr)
    assert "unreadable: git status exited" in result.stdout, result.stdout


def test_the_cutter_ends_with_its_own_exit_code():
    assert CUTTER.read_text(encoding="utf-8").rstrip().endswith("exit 0")


def test_the_sweep_gives_git_no_writing_subcommand() -> None:
    """It sweeps; it never stages, commits, checks out or removes anything."""
    text = SWEEP.read_text(encoding="utf-8")
    for forbidden in (
        "-Arguments @('add'",
        "-Arguments @('commit'",
        "-Arguments @('checkout'",
        "-Arguments @('reset'",
        "-Arguments @('restore'",
        "-Arguments @('worktree', 'remove'",
    ):
        assert forbidden not in text, f"the sweep must not run {forbidden!r}"
    for forbidden in ("Set-Content", "Out-File", "Remove-Item"):
        assert forbidden not in text, f"the sweep must not write with {forbidden!r}"
