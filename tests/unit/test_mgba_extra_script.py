"""Test the extra-script rule the owner set: always load it, always record it, always say so.

Two layers, because they catch different failures.

SOURCE-LEVEL (always runs): the launchers must read `LOG1_MGBA_EXTRA_SCRIPT`, treat an EXPLICITLY EMPTY
value as "load no bridge" (which is what makes the functional half hermetic on a machine whose User value
is set), hash the file, record path and hash in the run, and SKIP with a printed note - never refuse - when
the build has no `--script` flag. The banner must not go into the function's return value, which carries
the process.

FUNCTIONAL (runs where its prerequisites exist, and names the missing one when they do not): the GDB
launcher's `-DryRun` prints the identity it would write, so the recording is exercised for real without
starting an emulator. With the variable set to a known file the identity must carry that absolute path and
its true SHA-256; with the variable explicitly empty it must report nothing loaded; and a variable naming a
missing file must say THAT rather than "not set".
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tests.rom_support import CANONICAL_ROM_SHA256, canonical_rom_path  # noqa: E402

SESSION = ROOT / "tools" / "runtime" / "mgba_session.ps1"
CAPTURE = ROOT / "tools" / "runtime" / "run_mgba_capture.ps1"
SKILL = ROOT / "docs" / "skills" / "mgba-runtime.md"


def test_the_session_helper_records_and_can_skip() -> None:
    text = SESSION.read_text(encoding="utf-8")
    assert "LOG1_MGBA_EXTRA_SCRIPT" in text
    assert "GetEnvironmentVariable('LOG1_MGBA_EXTRA_SCRIPT', 'User')" in text, (
        "a shell that predates the user variable must still find it")
    assert "Get-FileHash -Algorithm SHA256" in text, "the bridge's identity must be recorded"
    assert "extra-script.json" in text, "the run must record what it loaded"
    assert "extra script SKIPPED" in text, "an unsupported build must say so"
    block = text[text.index("LOG1_MGBA_EXTRA_SCRIPT"):]
    block = block[:block.index("$options = @()")] if "$options = @()" in block else block
    assert "throw" not in block, "the helper must skip the bridge, not refuse the launch"


def test_the_session_helper_does_not_pollute_its_return_value() -> None:
    """Its callers do `$process = Start-MgbaSession`; Write-Output would land in that value instead."""
    text = SESSION.read_text(encoding="utf-8")
    assert "Write-Output" not in text, (
        "the banner must use Write-Host: Write-Output inside the function becomes part of the returned "
        "array and the caller's .Refresh() then throws")
    assert "Write-Host" in text


def test_the_bridge_is_switched_off_by_a_sentinel_the_shell_cannot_drop() -> None:
    """A "" value does not survive to the child on Windows PowerShell 5.1, so the switch is a sentinel."""
    for path in (SESSION, CAPTURE):
        text = path.read_text(encoding="utf-8")
        assert "LOG1_MGBA_NO_EXTRA_SCRIPT -eq '1'" in text, (
            f"{path.name} must honour LOG1_MGBA_NO_EXTRA_SCRIPT=1")
        assert "$extraScript -ieq 'none'" in text, (
            f"{path.name} must treat the literal value none as 'load no bridge'")


def test_the_gdb_launcher_records_it_before_using_it() -> None:
    text = CAPTURE.read_text(encoding="utf-8")
    assert "extra_script_path = $extraScriptPath" in text
    assert "extra_script_sha256 = $extraScriptSha" in text
    assert "extra_script_loaded = $extraScriptLoaded" in text
    resolution = text.index("$extraScript = $env:LOG1_MGBA_EXTRA_SCRIPT")
    identity = text.index("extra_script_path = $extraScriptPath")
    assert resolution < identity, "the bridge must be resolved before the identity that records it"
    assert "extra script SKIPPED" in text
    assert "throw" not in text[resolution:identity], (
        "an unsupported build must skip, not refuse to launch")


def test_the_skill_document_carries_the_owner_exception() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert "dashboard input bridge" in text
    assert "2026-10-11" in text, "the exception is dated and authorised"
    assert "extra-script.json" in text, "the exception is reviewable because every run records it"
    assert "printed note" in text, "a build without --script must still launch"
    assert "127.0.0.1" in text, "the bridge's loopback listener is part of what it is"
    assert "test_mgba_extra_script.py" in text, "the exception must name the test that holds it"


@pytest.fixture(scope="module")
def prerequisites() -> dict:
    """Everything the dry run needs, or a skip that names the missing prerequisite."""
    rom = canonical_rom_path()
    if rom is None:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    if hashlib.sha256(rom.read_bytes()).hexdigest() != CANONICAL_ROM_SHA256:
        pytest.skip("local ROM is not the canonical profile")
    named = os.environ.get("WEBFOOT_MGBA_DEV")
    builds = [Path(named)] if named and Path(named).is_file() else []
    builds += sorted(ROOT.glob("build/tools/mgba-dev/extracted/*/mGBA.exe"))
    builds = [build for build in builds if build.is_file()]
    if not builds:
        pytest.skip("no 0.11 dev mGBA build present to version-check; name one with WEBFOOT_MGBA_DEV")
    if not (ROOT / ".venv" / "Scripts" / "python.exe").is_file():
        pytest.skip("the launcher requires .venv/Scripts/python.exe and this checkout has none")
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        pytest.skip("no PowerShell host on PATH")
    directory = ROOT / "build" / "fv4" / "dryrun-test"
    directory.mkdir(parents=True, exist_ok=True)
    state = directory / "state.ss1"
    if not state.exists():
        state.write_bytes(b"\x00" * 32)
    return {"rom": rom, "mgb": builds[0], "shell": shell, "state": state}


def dry_run(prerequisites: dict, extra: str) -> dict:
    environment = dict(os.environ)
    environment["LOG1_MGBA_EXTRA_SCRIPT"] = extra
    mgb = prerequisites["mgb"]
    result = subprocess.run(
        [prerequisites["shell"], "-NoProfile", "-File", str(CAPTURE),
         "-RomPath", str(prerequisites["rom"]), "-StatePath", str(prerequisites["state"]),
         "-MGBPath", str(mgb), "-RequiredMGBVersion", "0.11",
         "-MGBSha256", hashlib.sha256(mgb.read_bytes()).hexdigest().upper(),
         "-DryRun"],
        cwd=ROOT, capture_output=True, text=True, env=environment)
    if "{" not in result.stdout:
        pytest.fail(f"the dry run printed no identity:\n{result.stdout}\n{result.stderr}")
    return json.loads(result.stdout[result.stdout.index("{"):])


def test_a_dry_run_with_the_variable_records_the_path_and_hash(prerequisites) -> None:
    bridge = Path(tempfile.gettempdir()) / "dsh-extra-script-test.lua"
    bridge.write_text("-- a stand-in for the dashboard bridge\n", encoding="utf-8")
    identity = dry_run(prerequisites, str(bridge))
    assert identity.get("extra_script_loaded") is True
    assert identity.get("extra_script_path") == str(bridge)
    assert identity.get("extra_script_sha256") == hashlib.sha256(bridge.read_bytes()).hexdigest().upper()
    assert "dashboard" in identity.get("extra_script_note", "")


def test_a_dry_run_with_the_sentinel_records_none(prerequisites) -> None:
    identity = dry_run(prerequisites, "none")
    assert identity.get("extra_script_loaded") is False
    assert identity.get("extra_script_path") is None
    assert identity.get("extra_script_sha256") is None
    assert "disabled by request" in identity.get("extra_script_note", "")


def test_a_dry_run_with_the_switch_variable_records_none(prerequisites) -> None:
    environment = dict(os.environ)
    environment["LOG1_MGBA_NO_EXTRA_SCRIPT"] = "1"
    environment["LOG1_MGBA_EXTRA_SCRIPT"] = str(
        Path(tempfile.gettempdir()) / "dsh-extra-script-test.lua")
    mgb = prerequisites["mgb"]
    result = subprocess.run(
        [prerequisites["shell"], "-NoProfile", "-File", str(CAPTURE),
         "-RomPath", str(prerequisites["rom"]), "-StatePath", str(prerequisites["state"]),
         "-MGBPath", str(mgb), "-RequiredMGBVersion", "0.11",
         "-MGBSha256", hashlib.sha256(mgb.read_bytes()).hexdigest().upper(),
         "-DryRun"],
        cwd=ROOT, capture_output=True, text=True, env=environment)
    assert "{" in result.stdout, result.stdout + result.stderr
    identity = json.loads(result.stdout[result.stdout.index("{"):])
    assert identity.get("extra_script_loaded") is False, (
        "the switch must win even when the bridge variable names a real file")


def test_a_dry_run_naming_a_missing_file_says_so(prerequisites) -> None:
    identity = dry_run(prerequisites, str(Path(tempfile.gettempdir()) / "no-such-bridge.lua"))
    assert identity.get("extra_script_loaded") is False
    assert "does not exist" in identity.get("extra_script_note", ""), (
        "a set-but-missing path is not the same state as 'not set'")


def _dry_run_args(prerequisites: dict, state: bool) -> list[str]:
    # The fixture already skipped without a host; this names it here too, so the
    # skip cannot be lost by a future fixture change.
    _require_host()
    mgb = prerequisites["mgb"]
    args = [
        prerequisites["shell"], "-NoProfile", "-File", str(CAPTURE),
        "-RomPath", str(prerequisites["rom"]),
        "-MGBPath", str(mgb), "-RequiredMGBVersion", "0.11",
        "-MGBSha256", hashlib.sha256(mgb.read_bytes()).hexdigest().upper(),
        "-DryRun",
    ]
    if state:
        args += ["-StatePath", str(prerequisites["state"])]
    return args


def test_a_dry_run_without_a_state_path_reports_none_and_still_runs(prerequisites) -> None:
    """RE Lab N1: a boot-time scene has no savestate, and the launcher refused to
    run at all without one. The state is optional now; when it is absent the
    identity says so rather than carrying a faked path."""
    environment = dict(os.environ)
    environment["LOG1_MGBA_NO_EXTRA_SCRIPT"] = "1"
    result = subprocess.run(
        _dry_run_args(prerequisites, state=False),
        cwd=ROOT, capture_output=True, text=True, env=environment)
    assert "{" in result.stdout, result.stdout + result.stderr
    identity = json.loads(result.stdout[result.stdout.index("{"):])
    assert identity.get("state_path") is None
    assert identity.get("state_sha256") is None
    assert identity.get("working_state_path") is None
    assert "(none: launching without a state load)" in result.stdout


def test_a_dry_run_with_a_state_path_still_carries_its_identity(prerequisites) -> None:
    """Optional must not mean unverified: the identity work stays when a state is given."""
    identity = dry_run(prerequisites, "none")
    assert identity.get("state_path") is not None
    assert identity.get("state_sha256")
    assert identity.get("state_size")


def _require_host() -> str:
    """The PowerShell host this file's -DryRun checks need, or a named skip.

    CI is Linux: the launcher is a `.ps1`, so those checks cannot run there and say
    so. The text checks in this file run everywhere.
    """
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        pytest.skip(
            "the launcher is a PowerShell script and this platform has no PowerShell "
            "host; the text checks in this file hold its invariants in CI"
        )
    return shell


def test_omitting_the_state_is_accepted_by_parameter_binding() -> None:
    """The optional state, proved WITHOUT the canonical image.

    `-StatePath` used to be Mandatory, so a caller that omitted it was refused by
    PowerShell's own binder before any of the launcher's checks ran. PowerShell still
    parses the full parameter block for -DryRun, so this asserts the binder accepts
    the omission; where a host exists it also asserts the launcher got as far as its
    own ROM check, which is the proof that the state is optional.
    """
    if shutil.which("pwsh") is None and shutil.which("powershell") is None:
        return
    shell = _require_host()
    result = subprocess.run(
        [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(CAPTURE),
         "-RomPath", str(ROOT / "no-such-image.gba"),
         "-MGBPath", str(ROOT / "no-such-mgba.exe"),
         "-DryRun"],
        cwd=ROOT, capture_output=True, text=True)
    output = result.stdout + result.stderr
    assert "Missing mandatory" not in output, output
    assert "-StatePath" not in output, (
        "the binder must not be asking for a state that is optional now:\n" + output)
    assert "ROM is missing" in output, output


def test_the_launcher_refuses_to_race_a_running_mgba() -> None:
    """RE Lab M4, lifted from start_toolkit031_session.ps1: a leftover mGBA gave no
    error at all, the run simply produced nothing."""
    text = CAPTURE.read_text(encoding="utf-8")
    assert "Get-Process -Name 'mGBA'" in text
    assert "already running" in text
    process_check = text.index("Get-Process -Name 'mGBA'")
    launch = text.index("$process = Start-Process")
    assert process_check < launch, "the refusal must come before any launch"


def test_a_relative_lua_path_resolves_against_the_invoking_worktree() -> None:
    """RE Lab N1: the launcher read the allowlist and the probe from a DIFFERENT
    worktree than the caller's, and the log stayed empty with nothing saying why."""
    text = CAPTURE.read_text(encoding="utf-8")
    assert "$invokingRoot = (Get-Location).Path" in text
    assert "Resolve-RequiredFile $LuaPath 'Lua script' @($invokingRoot)" in text
    assert "resolved inputs:" in text
    assert "  invoking worktree  : $invokingRoot" in text


def test_the_missing_file_note_cannot_be_overwritten() -> None:
    """The session helper set the missing-file note and then overwrote it, which is the review's finding.

    The fix is the ORDER: the default assignment must be guarded by the missing-file flag. A test that only
    checks both strings exist would pass on the broken version, so this checks the order too.
    """
    text = SESSION.read_text(encoding="utf-8")
    assert "elseif (-not $extraScriptMissing)" in text, (
        "the default 'not set' note must be suppressed when the variable named a missing file")
    missing_note = text.index("does not exist: $extraScript")
    default_note = text.index("'LOG1_MGBA_EXTRA_SCRIPT is not set for this run'")
    assert missing_note < default_note, (
        "the missing-file note must be set before the default assignment, not after it")
