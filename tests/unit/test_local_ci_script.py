"""The local full-CI gate is checked for what it claims, not only for running.

`scripts/local-ci.ps1` is the temporary CI gate while GitLab cannot create a
pipeline. It is checked here because a wrong value in it is a false record: the
pin table it compares against, the timeout it enforces and the linked-worktree
shape it needs are all stated in the script, and none is exercised by importing
it.

The counts and the path can be read without a PowerShell host. Only the parse
step needs one, so it skips where no host exists.
"""

from __future__ import annotations

import re
import shutil
import tempfile
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "local-ci.ps1"
SOURCE = SCRIPT.read_text(encoding="utf-8")

#: The 13 PowerShell nodes the CI trace pins, by file, read from the trace of
#: job 17121704860 at 9c34f1ae. The count is the guard: a build script that
#: silently drops a node stops the reconciliation from being checkable.
POWERSHELL_PIN = {
    "tests/unit/test_dev_tools.py": 6,
    "tests/unit/test_worktree_owners.py": 7,
}

#: The trace's own summary line, which the whole table has to reconcile with.
PINNED_JOB = "17121704860"
PINNED_SHA = "9c34f1ae"
PINNED_SKIPPED = 320


def pin_table() -> dict[str, tuple[int, str]]:
    """The script's `$PinnedTable` entries as `{file: (count, cause)}`.

    Read from the source text, so the table the script compares against is the
    table checked here. A file listed twice is not a table.
    """
    block = re.search(r"\$PinnedTable = @\((.*?)\n\)", SOURCE, re.DOTALL)
    assert block is not None, "the script has no $PinnedTable block"
    rows = re.findall(r"'([^']+)=(\d+)=([^']+)'", block.group(1))
    table: dict[str, tuple[int, str]] = {}
    for path, count, cause in rows:
        assert path not in table, f"{path} is in the pin table twice"
        table[path] = (int(count), cause)
    return table


def test_the_pin_table_sums_to_the_traced_skip_total() -> None:
    table = pin_table()
    assert sum(count for count, _ in table.values()) == PINNED_SKIPPED


def test_every_powershell_node_the_trace_pins_still_carries_its_count() -> None:
    table = pin_table()
    for path, count in POWERSHELL_PIN.items():
        assert path in table, f"{path} left the pin table"
        assert table[path][0] == count
        assert table[path][1] == "powershell"
    assert sum(POWERSHELL_PIN.values()) == 13


def test_the_pin_provenance_names_the_job_and_the_sha() -> None:
    assert f"'{PINNED_JOB}'" in SOURCE
    assert f"'{PINNED_SHA}'" in SOURCE
    assert "local-ci: ' + $verdict" in SOURCE


def test_the_geometry_is_the_one_the_brief_requires() -> None:
    assert "worktree', 'add', '--detach'" in SOURCE
    assert "taskkill.exe /PID $process.Id /T /F" in SOURCE
    assert "$BudgetSeconds = 45 * 60" in SOURCE
    assert "[math]::Floor($hostCores / 2)" in SOURCE
    assert "'.[dev,workbench,research]'" in SOURCE
    assert "--junitxml=report.xml" in SOURCE
    assert "test_container_decode_synthetic.py" in SOURCE
    assert "CLOUDFLARE_API_TOKEN = ''" in SOURCE
    assert "QT_QPA_PLATFORM = 'offscreen'" in SOURCE
    # $ErrorActionPreference = 'Stop' turns git's stderr into a terminating error
    assert "Invoke-GitLines" in SOURCE
    assert "^{" not in SOURCE
    assert "--format=%T" in SOURCE
    assert "-Recurse" not in SOURCE


def test_the_sha_is_mandatory_and_fails_closed() -> None:
    assert "[Parameter(Mandatory = $true)]" in SOURCE
    assert "if ($resolved.ToLower() -ne $Sha.ToLower())" in SOURCE
    assert "if ($Sha -notmatch '^[0-9a-fA-F]{40}$')" in SOURCE


def test_the_script_parses_under_a_real_powershell_host() -> None:
    host = shutil.which("powershell") or shutil.which("pwsh")
    if host is None or not SCRIPT.exists():
        pytest.skip("no PowerShell host on PATH to parse with")
    result = subprocess.run(
        [
            host,
            "-NoProfile",
            "-Command",
            "$e=$null;$t=$null;"
            "[void][System.Management.Automation.Language.Parser]::ParseFile("
            f"'{SCRIPT}',[ref]$t,[ref]$e);"
            "if ($e.Count) { $e | ForEach-Object { $_.Message }; exit 1 }",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_the_git_helper_resolves_a_sha_in_this_repository() -> None:
    """The two PowerShell traps this script hit, exercised against the real git.

    `$ErrorActionPreference = 'Stop'` makes git's stderr on a resolve failure a
    terminating error, and PowerShell 5.1 does not splat an array argument into a
    native command without a param block, so git received `-C` as the commit to
    resolve and printed its usage text. Both arms are checked here as a fragment,
    without building a venv or running a gate.
    """
    host = shutil.which("powershell") or shutil.which("pwsh")
    if host is None:
        pytest.skip("no PowerShell host on PATH to run the fragment with")
    head = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    fragment = """
function Invoke-GitLines {
    param([string[]] $Arguments)
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $output = @(& git -C 'REPO' @Arguments 2>&1 | ForEach-Object { $_.ToString() })
    $ErrorActionPreference = $previous
    return $output
}
$ErrorActionPreference = 'Stop'
$resolved = (Invoke-GitLines @('rev-parse', '--verify', 'SHA') -join [Environment]::NewLine).Trim()
$tree = (Invoke-GitLines @('show', '-s', '--format=%T', $resolved) -join [Environment]::NewLine).Trim()
$bad = (Invoke-GitLines @('rev-parse', '--verify', 'not-a-real-sha') -join [Environment]::NewLine).Trim()
Write-Output ("resolved=" + $resolved)
Write-Output ("tree=" + $tree)
Write-Output ("bad=" + $bad)
""".replace("REPO", str(REPO_ROOT)).replace("SHA", head)
    # A temp file, not -Command: PowerShell joins -Command lines with spaces, so
    # the fragment's line breaks disappear and statements run together.
    with tempfile.TemporaryDirectory(prefix="local-ci-helper-") as directory:
        script = Path(directory) / "fragment.ps1"
        script.write_text(fragment, encoding="utf-8")
        result = subprocess.run(
            [host, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            capture_output=True,
            text=True,
        )
    assert result.returncode == 0, result.stdout + result.stderr
    lines = dict(
        line.split("=", 1) for line in result.stdout.strip().splitlines() if "=" in line
    )
    assert lines["resolved"] == head
    assert re.fullmatch(r"[0-9a-f]{40}", lines["tree"])
    assert "usage:" not in result.stdout
    assert not re.fullmatch(r"[0-9a-f]{40}", lines["bad"])