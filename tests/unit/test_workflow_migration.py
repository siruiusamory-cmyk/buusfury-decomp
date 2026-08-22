from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNNER = PROJECT_ROOT / "scripts" / "run-current.ps1"


def _powershell() -> str:
    executable = shutil.which("powershell.exe") or shutil.which("powershell")
    assert executable is not None, "Windows PowerShell is required by this project"
    return executable


def _run_runner(*arguments: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            _powershell(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(RUNNER),
            *arguments,
        ],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_required_workflow_files_exist_and_are_bounded():
    expected_limits = {
        "<local-state-name>": (150, 300),
        "docs/PROJECT_<local-state-name>": (100, 200),
        "docs/PROJECT_<local-state-name>": (10, 800),
        "docs/REVIEW.md": (20, 100),
        "scripts/run-current.ps1": (40, 140),
    }

    for relative_path, (minimum, maximum) in expected_limits.items():
        text = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        line_count = len(text.splitlines())
        assert minimum <= line_count <= maximum, (relative_path, line_count)


def test_context_split_keeps_permanent_state_and_ticket_content_separate():
    agents = (PROJECT_ROOT / "<local-state-name>").read_text(encoding="utf-8")
    state = (PROJECT_ROOT / "docs/PROJECT_<local-state-name>").read_text(encoding="utf-8")
    current = (PROJECT_ROOT / "docs/PROJECT_<local-state-name>").read_text(encoding="utf-8")

    assert "192 passed" not in agents
    assert "buus_fury_usa_rev0_01c1707f" not in agents
    assert "ROM-008 portable baseline: **192 passed" in state
    assert "Current portable suite after workflow migration: **199 passed" in state
    assert "# TOOL-001 - Complete; No Active Ticket" in current
    assert "Original ROM Safety - Mandatory" not in current
    assert "TOOL-002" in current
    assert "ROM-013" in current


def test_current_placeholder_blocks_unapproved_work():
    current = (PROJECT_ROOT / "docs/PROJECT_<local-state-name>").read_text(encoding="utf-8")

    assert "TOOL-001 is complete and archived" in current
    assert "No next research or tooling ticket has been authored or authorized" in current
    assert "Do not execute TOOL-001 again" in current
    assert "Do not begin TOOL-002" in current
    assert "Do not begin ROM-013" in current
    assert "Do not run BSim matching" in current
    assert "Do not import Data Crystal labels" in current
    assert "Do not perform project MCP work" in current
    assert "Do not perform new ROM reverse engineering" in current
    assert "Stop immediately" in current


def test_runner_dry_run_works_from_an_unrelated_directory(tmp_path):
    result = _run_runner(
        "-DryRun",
        "-CodexPath",
        sys.executable,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"repo: {PROJECT_ROOT}" in result.stdout
    assert f"agents: {PROJECT_ROOT / 'docs/DEVELOPMENT.md'}" in result.stdout
    assert f"state: {PROJECT_ROOT / 'docs' / 'PROJECT_<local-state-name>'}" in result.stdout
    assert f"ticket: {PROJECT_ROOT / 'docs' / 'tickets' / 'PROJECT_<local-state-name>'}" in result.stdout
    assert "current: TOOL-001" in result.stdout
    assert "mode: interactive the tool session" in result.stdout
    assert "dry-run: no the tool session launched" in result.stdout


def test_runner_uses_small_bootstrap_without_concatenating_context():
    runner = RUNNER.read_text(encoding="utf-8")

    assert "Get-Content" not in runner
    assert "Read and obey <local-state-name>" in runner
    assert "docs/PROJECT_<local-state-name>" in runner
    assert "docs/PROJECT_<local-state-name>" in runner
    assert "--cd" in runner
    assert "Select-Object -First 1" in runner
    assert len(runner) < 6_000


def test_runner_fails_before_launch_when_current_is_missing(tmp_path):
    fake_root = tmp_path / "incomplete"
    fake_scripts = fake_root / "scripts"
    fake_docs = fake_root / "docs"
    fake_scripts.mkdir(parents=True)
    fake_docs.mkdir()
    shutil.copy2(RUNNER, fake_scripts / RUNNER.name)
    (fake_root / "<local-state-name>").write_text("# Rules\n", encoding="utf-8")
    (fake_docs / "PROJECT_<local-state-name>").write_text("# State\n", encoding="utf-8")

    result = subprocess.run(
        [
            _powershell(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(fake_scripts / RUNNER.name),
            "-DryRun",
            "-CodexPath",
            sys.executable,
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode != 0
    assert "Required workflow file missing" in result.stdout + result.stderr
    assert "PROJECT_<local-state-name>" in result.stdout + result.stderr


def test_workflow_files_do_not_embed_proprietary_artifacts():
    workflow_paths = [
        PROJECT_ROOT / "<local-state-name>",
        PROJECT_ROOT / "docs/PROJECT_<local-state-name>",
        PROJECT_ROOT / "docs/PROJECT_<local-state-name>",
        PROJECT_ROOT / "docs/REVIEW.md",
        RUNNER,
    ]

    for path in workflow_paths:
        text = path.read_text(encoding="utf-8")
        assert "higher-plane-original.ss1" not in text
        assert "higher-plane-original.sav" not in text
        assert "BEGIN ROM" not in text
