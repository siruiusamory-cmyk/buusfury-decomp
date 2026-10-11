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


def test_an_explicitly_empty_variable_is_hermetic() -> None:
    """The functional half cannot rely on this machine's registry being unset; empty must mean empty."""
    for path in (SESSION, CAPTURE):
        text = path.read_text(encoding="utf-8")
        assert "elseif ($extraScript -eq '')" in text, (
            f"{path.name} must treat an explicitly empty variable as 'load no bridge'")


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


def test_a_dry_run_with_an_explicitly_empty_variable_records_none(prerequisites) -> None:
    identity = dry_run(prerequisites, "")
    assert identity.get("extra_script_loaded") is False
    assert identity.get("extra_script_path") is None
    assert identity.get("extra_script_sha256") is None
    assert "not set" in identity.get("extra_script_note", "")


def test_a_dry_run_naming_a_missing_file_says_so(prerequisites) -> None:
    identity = dry_run(prerequisites, str(Path(tempfile.gettempdir()) / "no-such-bridge.lua"))
    assert identity.get("extra_script_loaded") is False
    assert "does not exist" in identity.get("extra_script_note", ""), (
        "a set-but-missing path is not the same state as 'not set'")
