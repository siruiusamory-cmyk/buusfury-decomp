"""Guards for ``scripts/local-ci.ps1``, the local full-CI record gate.

The gate is load-bearing evidence while GitLab cannot create a pipeline, so its
own failure paths are tested here rather than trusted. Each guard drives a STUB,
never a real install: the gate is run against a throwaway local clone with a
stub interpreter on ``PYTHONPATH``, whose ``sitecustomize`` replaces the venv
build, the install, the four quality gates, the suite (it writes a clean JUnit
report), the adjacency orders and the integration selection. That makes a full
gate run take seconds and lets one step be made deliberately red.

The four guards, and the defect each one catches:

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

The gate is also given a private ``LOCALAPPDATA``, so its venv and its neutral
clone land in the test's temporary directory and never touch the machine's own
``%LOCALAPPDATA%\\log1-ci``.
"""

from __future__ import annotations

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

POWERSHELL = shutil.which("powershell")

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


def _run_gate(tmp_path: Path, env_extra: dict[str, str] | None = None):
    if os.name != "nt" or not POWERSHELL:
        pytest.skip("the local-CI gate is a Windows PowerShell script and needs powershell")
    repo, stub = _base_dir(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    environment = dict(os.environ)
    environment.update(
        {
            "LOCALAPPDATA": str(home),
            "PYTHONPATH": str(stub),
        }
    )
    if env_extra:
        environment.update(env_extra)
    sha = _head()
    run = subprocess.run(
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
        capture_output=True,
        text=True,
        env=environment,
        cwd=str(tmp_path),
        timeout=600,
    )
    record = repo / "build" / "local-ci" / sha / "record.txt"
    return run, record, home, sha


def _record_text(record: Path) -> str:
    assert record.exists(), "the gate did not write a record"
    return record.read_text(encoding="utf-8", errors="replace")


def test_a_red_quality_step_fails_the_record(tmp_path):
    """A failing step must reach the verdict, not only the step table.

    ``tools.quality.public_surface`` is stubbed to exit 7 while every other step
    succeeds and the JUnit report is clean, so the ONLY failure source is the
    step's exit code. With the null-to-zero defect restored this record reads
    ``verdict : PASS`` and the step table says ``exit 0``.
    """
    run, record, _home, _sha = _run_gate(tmp_path, {"STUB_QUALITY_EXIT": "7"})
    text = _record_text(record)
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
    text = _record_text(record)
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
    text = _record_text(record)
    assert "the throwaway worktree could not be removed" in text, text
    assert "verdict        : FAIL" in text, text
    assert process.returncode == 1, (process.returncode, output[-2000:])


def test_the_branch_adds_no_whitespace_errors():
    """``git diff --check`` over the branch, the check the review ran."""
    check = subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), "diff", "--check", f"{BRANCH_BASE}..HEAD"],
        capture_output=True,
        text=True,
    )
    assert check.returncode == 0, check.stdout + check.stderr
