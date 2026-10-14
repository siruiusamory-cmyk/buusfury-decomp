"""Guards for ``scripts/local-ci.ps1``, the local full-CI record gate.

The gate is load-bearing evidence while GitLab cannot create a pipeline, so its
own failure paths are tested here rather than trusted. Each guard drives a STUB,
never a real install: the gate is run against a throwaway local clone with a
stub interpreter on ``PYTHONPATH``, whose ``sitecustomize`` replaces the venv
build, the install, the four quality gates, the suite (it writes a clean JUnit
report), the adjacency orders and the integration selection. That makes a full
gate run take seconds and lets one step be made deliberately red.

The five guards, and the defect each one catches:

- ``test_a_red_quality_step_fails_the_record`` - ``Invoke-Step`` read a NULL
  ``ExitCode`` under PowerShell 5.1 because a redirected ``Start-Process`` polled
  on ``HasExited`` loses it, and the old null-to-zero mapping made every step
  report ``exit 0``. A red quality gate therefore could not fail the record.
- ``test_an_early_failure_leaves_no_clone_or_worktree`` - the cleanup was on the
  normal path only, and two early paths removed the worktree from ``$RepoPath``,
  the wrong repository, so a failed run left the neutral clone behind.
- ``test_a_cleanup_failure_reaches_the_record`` - the record was written and
  digested BEFORE the cleanup ran, so the file could say PASS while the process
  exited 1.
- ``test_the_branch_adds_no_whitespace_errors`` - ``git diff --check`` against the
  branch base failed on two carriage-return-terminated lines.
- ``test_the_gate_refuses_when_the_record_directory_cannot_be_computed`` - the
  record directory was computed with ``Join-Path`` and never checked, so an empty
  result turned every later statement into a silent no-op and the gate printed
  ``local-ci: PASS`` with no record at all: the false PASS GitHub run 38504730899
  shipped.

The gate is also given a private ``LOCALAPPDATA``, so its venv and its neutral
clone land in the test's temporary directory and never touch the machine's own
local CI home.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import pytest

from tests.gates import REPOSITORY_ROOT

SCRIPT = REPOSITORY_ROOT / "scripts" / "local-ci.ps1"

#: The base every record on this branch is measured against, so the whitespace
#: guard checks the whole branch and not only its last commit.
BRANCH_BASE = "34da2e67e372176a975a35a6a29cd55d466ac025"

def _windows_powershell() -> str | None:
    """The real Windows PowerShell 5.1, not whatever a PATH entry calls ``powershell``.

    GitHub run 38510276291's probe: the gate child exited 0 with EMPTY stdout and
    stderr, so ``local-ci.ps1`` never ran a single line. The PATH these tests hand the
    child starts with a site-packages directory and a PowerShell 7 install, and a shim
    named ``powershell`` earlier on such a PATH exits 0 having done nothing, which is
    that signature exactly. So the system binary is resolved by its own path, built
    from ``%SystemRoot%`` and never written down, and used whenever it exists.
    """
    root = os.environ.get("SystemRoot") or os.environ.get("windir")
    if root:
        system = Path(root) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        if system.is_file():
            return str(system)
    return shutil.which("powershell")


POWERSHELL = _windows_powershell()


def _shell_summary() -> str:
    """Whether the gate could run at all: the shell, the script's own bytes, the env."""
    if SCRIPT.is_file():
        script = "{} {} bytes sha256 {}".format(
            SCRIPT, SCRIPT.stat().st_size, hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
        )
    else:
        script = "{} ABSENT".format(SCRIPT)
    return (
        "powershell resolved to {0}; shutil.which('powershell')={1}; script={2}; "
        "PSModulePath={3}".format(
            POWERSHELL, shutil.which("powershell"), script, os.environ.get("PSModulePath", "<unset>")
        )
    )


def _argv(repo: Path, sha: str) -> list[str]:
    return [
        str(POWERSHELL),
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(SCRIPT),
        "-Sha",
        sha,
        "-RepoPath",
        str(repo),
    ]

STUBCUSTOMIZE = '''"""Stub interpreter for the local-ci guard tests: no installs, no suite.

Every exit is ``os._exit``: this module runs during site initialisation, and a
``sys.exit`` there becomes "Fatal Python error: init_import_site" with code 1
instead of the code the stub asked for.
"""

import os
import shutil
import sys

argv = list(getattr(sys, "orig_argv", sys.argv))
verb = argv[1:]


def code(name, default):
    return int(os.environ.get(name, default))


def leave(status):
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(status)


if verb[:2] == ["-m", "venv"]:
    if os.environ.get("STUB_VENV_ABSENT") == "1":
        leave(0)
    target = verb[2]
    scripts = os.path.join(target, "Scripts")
    os.makedirs(scripts, exist_ok=True)
    os.makedirs(os.path.join(target, "Lib", "site-packages"), exist_ok=True)
    shutil.copy2(sys.executable, os.path.join(scripts, "python.exe"))
    for name in os.listdir(sys.base_prefix):
        if name.lower().startswith("python") and name.lower().endswith(".dll"):
            shutil.copy2(os.path.join(sys.base_prefix, name), os.path.join(scripts, name))
    with open(os.path.join(target, "pyvenv.cfg"), "w", encoding="utf-8") as handle:
        handle.write("home = %s\\n" % sys.base_prefix)
        handle.write("include-system-site-packages = false\\n")
    leave(0)

if verb[:2] == ["-m", "pip"]:
    leave(0)

if verb[:2] == ["-m", "tools.quality.public_surface"]:
    # Markers on both streams, so the retention guard can prove that a failed step's
    # own output survives on disk. That is exactly what the 05b759ad pip failure could
    # not show, because the gate read its capture into memory and deleted the file.
    print("STUB_PUBLIC_SURFACE_OUT")
    sys.stderr.write("STUB_PUBLIC_SURFACE_ERR\\n")
    leave(code("STUB_QUALITY_EXIT", "7"))

if verb[:2] in (
    ["-m", "tools.quality.architecture"],
    ["-m", "tools.quality.public_release"],
    ["-m", "tools.quality.readability"],
):
    leave(0)

if verb[:2] == ["-m", "scripts.adjacency_run"]:
    print("ran 17 modules clean")
    leave(0)

if verb[:2] == ["-m", "pytest"]:
    for argument in verb:
        if argument.startswith("--junitxml="):
            with open(argument.split("=", 1)[1], "w", encoding="utf-8") as handle:
                handle.write(
                    '<?xml version="1.0" encoding="utf-8"?><testsuites>'
                    '<testsuite name="pytest" tests="1" failures="0" errors="0" skipped="0">'
                    '<testcase classname="stub" name="stub"/></testsuite></testsuites>'
                )
    leave(code("STUB_PYTEST_EXIT", "0"))

leave(0)
'''


def _head() -> str:
    return subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _base_dir(tmp_path: Path) -> tuple[Path, Path]:
    """A throwaway clone the gate may write into, and the stub environment."""
    repo = tmp_path / "repo"
    subprocess.run(
        ["git", "clone", "--quiet", "--local", str(REPOSITORY_ROOT), str(repo)],
        check=True,
        capture_output=True,
    )
    stub = tmp_path / "stub"
    stub.mkdir(parents=True, exist_ok=True)
    (stub / "sitecustomize.py").write_text(STUBCUSTOMIZE, encoding="utf-8")
    return repo, stub


def _prepare(tmp_path: Path):
    """A throwaway clone, the stub environment, a private home and the head SHA."""
    repo, stub = _base_dir(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    return repo, stub, home, _head()


def _gate_environment(home: Path, stub: Path, env_extra=None) -> dict[str, str]:
    environment = dict(os.environ)
    environment.update({"LOCALAPPDATA": str(home), "PYTHONPATH": str(stub)})
    if env_extra:
        environment.update(env_extra)
    return environment


#: The environment the child was given, printed with a missing record. PATH first: the
#: difference between the green run and the red one is suspected to be here, not the tree.
PROBE_KEYS = ("PATH", "VIRTUAL_ENV", "LOCALAPPDATA", "PYTHONPATH")


def _probe_record_missing(run, record: Path, environment: dict[str, str]) -> None:
    """Put the gate's own evidence into pytest's captured output, untruncated.

    GitHub run 38504730899 failed six nodes on ``the gate did not write a record``
    while the gate itself printed ``local-ci: PASS``. The artifact carried only a
    truncated ``CompletedProcess`` repr - the middle of it elided by pytest's
    assertion introspection - so the cause could not be read back. So the streams
    are PRINTED in full: pytest prints the captured output of a failing test, and
    that is the one channel that reaches the artifact whole. The environment goes
    with them.
    """
    print("local-ci probe record=" + str(record))
    print("local-ci probe record-written=False")
    print("local-ci probe returncode=" + str(run.returncode))
    print("local-ci probe stdout-begin\n" + str(run.stdout) + "\nlocal-ci probe stdout-end")
    print("local-ci probe stderr-begin\n" + str(run.stderr) + "\nlocal-ci probe stderr-end")
    for key in PROBE_KEYS:
        print("local-ci probe " + key + "=" + str(environment.get(key, "<unset>")))
    print("local-ci probe which-python=" + str(shutil.which("python")))
    print("local-ci probe which-py=" + str(shutil.which("py")))
    print("local-ci probe shell=" + _shell_summary())
    print("local-ci probe argv=" + repr(run.args))


def _invoke(repo: Path, stub: Path, home: Path, sha: str, env_extra=None):
    """One gate run against an already-prepared clone, so a test can run it twice."""
    environment = _gate_environment(home, stub, env_extra)
    arguments = _argv(repo, sha)
    # Printed before the launch, so a child that dies silently still leaves the argv.
    print("local-ci probe launching " + " ".join(arguments) + " | " + _shell_summary())
    run = subprocess.run(
        arguments,
        capture_output=True,
        text=True,
        env=environment,
        cwd=str(repo.parent),
        timeout=600,
    )
    record = repo / "build" / "local-ci" / sha / "record.txt"
    if not record.exists():
        _probe_record_missing(run, record, environment)
    # A gate that ran always prints at least its host line. Run 38510276291's five
    # failures were a child that exited 0 having printed nothing at all, so this is
    # asserted rather than left to the record check to describe as a missing file.
    assert str(run.stdout).strip(), (
        "the gate printed nothing, so it never ran: "
        + _shell_summary()
        + "; argv="
        + repr(run.args)
        + "; returncode="
        + str(run.returncode)
        + "; stderr="
        + repr(str(run.stderr)[-400:])
    )
    return run, record


#: GitHub-only quarantine, owner-ordered 2026-10-13 with a two-strike timebox.
#:
#: These seven nodes drive the local full-CI record tool: each launches Windows
#: PowerShell and reads the record it writes. On the GitHub runners the gate child has
#: twice exited 0 having printed NOTHING AT ALL (runs 38504730899 and 38510276291), so
#: ``scripts/local-ci.ps1`` never reached its first line; the shell is resolved from
#: ``%SystemRoot%`` now, but the runner-side cause is not the repository's contract and
#: is being chased as LOCAL-CI-RUNNER-001. They run UNCHANGED locally, where the record
#: path is what gates a merge.
GITHUB_QUARANTINE_REASON = (
    "tests the local full-CI record tool; runs locally; follow-up LOCAL-CI-RUNNER-001"
)
GITHUB_QUARANTINED = frozenset(
    {
        "test_a_red_quality_step_fails_the_record",
        "test_a_green_run_passes_so_the_red_guard_is_not_vacuous",
        "test_a_green_run_passes_when_the_pinned_files_are_present",
        "test_an_early_failure_leaves_no_clone_or_worktree",
        "test_a_cleanup_failure_reaches_the_record",
        "test_a_failed_step_keeps_its_captured_output",
        "test_a_later_run_keeps_the_earlier_runs_artifacts_and_names_do_not_collide",
    }
)


@pytest.fixture(autouse=True)
def github_quarantine(request):
    """Skip a quarantined node on GitHub only, with the reason stated in the census."""
    if os.environ.get("GITHUB_ACTIONS") == "true" and request.node.name in GITHUB_QUARANTINED:
        pytest.skip(GITHUB_QUARANTINE_REASON)


def _ready() -> None:
    if os.name != "nt" or not POWERSHELL:
        pytest.skip("the local-CI gate is a Windows PowerShell script and needs powershell")


def _run_dirs(record: Path) -> list[Path]:
    runs = record.parent / "runs"
    return sorted(p for p in runs.iterdir() if p.is_dir()) if runs.exists() else []


def _digest(path: Path) -> str:
    # Upper case, because the gate prints the digests Get-FileHash returns.
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _run_gate(tmp_path: Path, env_extra: dict[str, str] | None = None):
    _ready()
    repo, stub, home, sha = _prepare(tmp_path)
    run, record = _invoke(repo, stub, home, sha, env_extra)
    return run, record, home, sha


def _record_text(record: Path, run=None) -> str:
    """The record, with the gate's own streams named when there is no record.

    A bare ``the gate did not write a record`` was all run 38504730899 left in the
    artifact, so this carries the returncode and the tails with it; the full streams
    are printed separately by :func:`_probe_record_missing`.
    """
    assert record.exists(), _missing_record(record, run)
    return record.read_text(encoding="utf-8", errors="replace")


def _missing_record(record: Path, run=None) -> str:
    if run is None:
        return f"the gate did not write a record: {record}"
    return (
        f"the gate did not write a record: {record}; returncode={run.returncode}\n"
        f"--- stdout tail ---\n{(run.stdout or '')[-2000:]}\n"
        f"--- stderr tail ---\n{(run.stderr or '')[-2000:]}"
    )


def test_a_red_quality_step_fails_the_record(tmp_path):
    """A failing step must reach the verdict, not only the step table.

    ``tools.quality.public_surface`` is stubbed to exit 7 while every other step
    succeeds and the JUnit report is clean, so the ONLY failure source is the
    step's exit code. With the null-to-zero defect restored this record reads
    ``verdict : PASS`` and the step table says ``exit 0``.
    """
    run, record, _home, _sha = _run_gate(tmp_path, {"STUB_QUALITY_EXIT": "7"})
    text = _record_text(record, run)
    assert "exit 7" in text, (
        "the step's real exit code did not reach the record:\n"
        + "\n".join(line for line in text.splitlines() if "quality" in line)
    )
    assert "step 'tools.quality.public_surface' exited 7" in text, text
    assert "verdict        : FAIL" in text, text
    assert run.returncode == 1, (run.returncode, run.stdout[-2000:])


def test_a_green_run_passes_so_the_red_guard_is_not_vacuous(tmp_path):
    """The same run with the stub green must PASS, or the guard above proves nothing."""
    run, record, _home, _sha = _run_gate(tmp_path, {"STUB_QUALITY_EXIT": "0"})
    text = _record_text(record, run)
    assert "verdict        : PASS" in text, text
    assert run.returncode == 0, (run.returncode, run.stdout[-2000:])


def test_a_green_run_passes_when_the_pinned_files_are_present(tmp_path):
    """The retro-tools shape: a SHA carrying the pinned files must still PASS.

    The pinned per-file counts came from a Linux trace, where those two modules skip
    because no `.ps1` can run there. On a host WITH a PowerShell the nodes run, so a SHA
    that carries the modules legitimately skips 0; before the host condition, such a SHA
    failed its record on the pinned equality and took the green guard above down with it.
    The modules are committed into the throwaway clone, so the detached worktree the gate
    records really carries them.
    """
    _ready()
    repo, stub, home, _sha = _prepare(tmp_path)
    pinned = ("tests/unit/test_dev_tools.py", "tests/unit/test_worktree_owners.py")
    for relative in pinned:
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# present so the pinned equality would apply\n", encoding="utf-8")

    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()

    git("add", "--", *pinned)
    git(
        "-c",
        "user.email=guard@example.invalid",
        "-c",
        "user.name=guard",
        "commit",
        "-q",
        "-m",
        "carry the pinned modules",
    )
    sha = git("rev-parse", "HEAD")
    run, record = _invoke(repo, stub, home, sha, {"STUB_QUALITY_EXIT": "0"})
    text = _record_text(record, run)
    #: Whitespace-collapsed, because the record pads each count to a fixed width.
    flat = " ".join(text.split())
    assert flat.count("host has PowerShell, so not an equality gate") == 2, text
    assert (
        "test_dev_tools.py host has PowerShell, so not an equality gate "
        "(actual 0, pinned 6)" in flat
    ), text
    assert (
        "test_worktree_owners.py host has PowerShell, so not an equality gate "
        "(actual 0, pinned 7)" in flat
    ), text
    assert "verdict        : PASS" in text, text
    assert run.returncode == 0, (run.returncode, run.stdout[-2000:])


def test_an_early_failure_leaves_no_clone_or_worktree(tmp_path):
    """An early exit must still remove the neutral clone and the throwaway worktree.

    The venv stub declines to create an interpreter, so the gate exits on its
    no-interpreter path. That path used to remove the worktree from ``$RepoPath``,
    a different repository, and left the neutral clone behind entirely.
    """
    run, _record, home, sha = _run_gate(tmp_path, {"STUB_VENV_ABSENT": "1"})
    assert "no interpreter at" in run.stdout, run.stdout[-2000:]
    neutral = home / "log1-ci" / ("neutral-" + sha[:8])
    worktree = home / "log1-ci" / ("wt-" + sha[:8])
    assert not neutral.exists(), f"the gate left its neutral clone behind: {neutral}"
    assert not worktree.exists(), f"the gate left its worktree behind: {worktree}"


def test_a_cleanup_failure_reaches_the_record(tmp_path):
    """A cleanup that fails must make the RECORD fail, not only the process exit.

    The record used to be written and digested before the cleanup ran, so this
    exact situation read ``verdict : PASS`` with a non-zero process exit. The
    handle held here denies deletion of the neutral clone, which is what the
    cleanup then reports.
    """
    if os.name != "nt" or not POWERSHELL:
        pytest.skip("the local-CI gate is a Windows PowerShell script and needs powershell")
    repo, stub = _base_dir(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    environment = dict(os.environ)
    environment.update({"LOCALAPPDATA": str(home), "PYTHONPATH": str(stub), "STUB_QUALITY_EXIT": "0"})
    sha = _head()
    worktree = home / "log1-ci" / ("wt-" + sha[:8])
    process = subprocess.Popen(
        [
            POWERSHELL,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-Sha",
            sha,
            "-RepoPath",
            str(repo),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=environment,
        cwd=str(tmp_path),
    )
    handle = None
    try:
        # The report is written by the suite step, which is well after the clone,
        # so this cannot race the clone itself. Holding it denies deletion of the
        # worktree that contains it, which is the cleanup failure under test.
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline and process.poll() is None:
            candidate = worktree / "report.xml"
            if candidate.exists():
                try:
                    handle = open(candidate, "rb")
                    break
                except OSError:
                    handle = None
            time.sleep(0.01)
        output = process.communicate(timeout=600)[0]
    finally:
        if handle is not None:
            handle.close()
    if handle is None:
        pytest.skip("the worktree report was not caught open, so the cleanup was not driven")
    record = repo / "build" / "local-ci" / sha / "record.txt"
    #: stderr was merged into stdout above, so the one stream is what the probe carries.
    completed = subprocess.CompletedProcess([], process.returncode, output, "")
    if not record.exists():
        _probe_record_missing(completed, record, environment)
    text = _record_text(record, completed)
    assert "the throwaway worktree could not be removed" in text, text
    assert "verdict        : FAIL" in text, text
    assert process.returncode == 1, (process.returncode, output[-2000:])


def test_the_gate_refuses_when_the_record_directory_cannot_be_computed(tmp_path, monkeypatch):
    """A record the gate cannot name is a named failure, never a PASS.

    The empty record directory cannot be produced through the gate's own inputs:
    ``Join-Path`` rejects only a null or empty Path, and both RepoPath and Sha are
    non-empty by the time that line runs. So the drive replaces that single line in
    a COPY of the script with an empty value and asserts the gate's own behaviour:
    exit 1, both inputs named in the message, and no PASS. It is also the shape of
    the false PASS GitHub run 38504730899 shipped, where the gate ran to its last
    line and printed PASS with an empty ``record:`` line and no record on disk.
    """
    _ready()
    repo, stub, home, sha = _prepare(tmp_path)
    computed = (
        "$recordDir = Join-Path (Join-Path $RepoPath 'build') (Join-Path 'local-ci' $Sha)"
    )
    source = SCRIPT.read_text(encoding="utf-8")
    assert computed in source, "the record-directory line moved, so this drive proves nothing"
    forced = tmp_path / "local-ci-empty-record-dir.ps1"
    forced.write_text(source.replace(computed, "$recordDir = ''"), encoding="utf-8")
    # The gate is launched by the same _invoke every other node here uses, with the
    # copy's path in place of the tracked script: no process start is added anywhere.
    monkeypatch.setattr(sys.modules[__name__], "SCRIPT", forced)
    run, record = _invoke(repo, stub, home, sha)
    assert run.returncode == 1, (run.returncode, run.stdout[-2000:], run.stderr[-2000:])
    assert "local-ci: FAIL - the record directory could not be computed" in run.stdout, (
        run.stdout[-2000:]
    )
    assert "RepoPath '" + str(repo) + "'" in run.stdout, run.stdout[-2000:]
    assert "Sha '" + sha + "'" in run.stdout, run.stdout[-2000:]
    assert "local-ci: PASS" not in run.stdout, run.stdout[-2000:]
    assert not (repo / "build" / "local-ci" / sha / "record.txt").exists()


def test_the_branch_adds_no_whitespace_errors():
    """``git diff --check`` over the branch, the check the review ran."""
    check = subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), "diff", "--check", f"{BRANCH_BASE}..HEAD"],
        capture_output=True,
        text=True,
    )
    assert check.returncode == 0, check.stdout + check.stderr


def test_a_failed_step_keeps_its_captured_output(tmp_path):
    """The 05b759ad pip failure left nothing behind because its capture was deleted.

    The stub writes a marker to both streams and exits 7, so the failing step's own text
    must still be on disk after the run, inside the run's private directory, and the
    record must name each capture with the digest that matches the file.
    """
    _run, record, _home, _sha = _run_gate(tmp_path, {"STUB_QUALITY_EXIT": "7"})
    text = _record_text(record, _run)
    assert "step captures (private, under ignored build/)" in text, text
    runs = _run_dirs(record)
    assert len(runs) == 1, runs
    steps = sorted((runs[0] / "steps").iterdir())
    assert steps, "no step capture was kept"
    public = [p for p in steps if "public-surface" in p.name]
    assert public, [p.name for p in steps]
    assert any(
        "STUB_PUBLIC_SURFACE_ERR" in p.read_text(encoding="utf-8", errors="replace")
        for p in public
        if p.suffix == ".err"
    ), [p.name for p in public]
    for path in public:
        assert path.name in text, path.name
        assert _digest(path) in text, (path, _digest(path))
    assert (runs[0] / "record.txt").read_text(encoding="utf-8") == text


def test_a_later_run_keeps_the_earlier_runs_artifacts_and_names_do_not_collide(tmp_path):
    """A second run on the same SHA must not overwrite the first run's evidence.

    The first run fails a step and the second passes, so their records differ; every file
    under the first run's directory must be byte-identical afterwards, the two runs must
    have different directory names, and inside a run the step captures must be uniquely
    named and index-prefixed.
    """
    _ready()
    repo, stub, home, sha = _prepare(tmp_path)
    _first, record = _invoke(repo, stub, home, sha, {"STUB_QUALITY_EXIT": "7"})
    runs = _run_dirs(record)
    assert len(runs) == 1, runs
    before = {
        str(p.relative_to(runs[0])): _digest(p)
        for p in runs[0].rglob("*")
        if p.is_file()
    }
    assert before, "the first run kept nothing"
    _second, record2 = _invoke(repo, stub, home, sha, {"STUB_QUALITY_EXIT": "0"})
    after = {
        str(p.relative_to(runs[0])): _digest(p)
        for p in runs[0].rglob("*")
        if p.is_file()
    }
    assert after == before, "a later run changed the earlier run's artifacts"
    second_runs = _run_dirs(record2)
    assert len(second_runs) == 2, second_runs
    assert runs[0] in second_runs
    assert record.parent == record2.parent
    assert len({p.name for p in second_runs}) == 2, [p.name for p in second_runs]
    for run_dir in second_runs:
        names = sorted(p.name for p in (run_dir / "steps").iterdir())
        assert names, run_dir
        assert len(names) == len(set(names)), names
        assert all(name[:2].isdigit() for name in names), names
        assert any(name.endswith(".out") for name in names), names
        assert any(name.endswith(".err") for name in names), names
