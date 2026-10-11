"""Test the extra-script rule the owner set: always load it, always record it.

Two layers, because they catch different failures.

SOURCE-LEVEL (always runs): the tracked launchers must read `LOG1_MGBA_EXTRA_SCRIPT` from the process
environment AND fall back to the User registry, hash the file, write the path and hash into the run's
records, and SKIP with a printed note - never refuse - when the build has no `--script` flag.

FUNCTIONAL (runs where the canonical ROM is present): the GDB launcher's own `-DryRun` prints the identity
it would write, so the recording can be exercised for real without starting an emulator. With the variable
set to a known file the printed identity must carry that absolute path and its true SHA-256; without it the
identity must say the script was not set and not loaded.
"""

from __future__ import annotations

import hashlib
import json
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


def test_the_gdb_launcher_records_it_before_using_it() -> None:
    text = CAPTURE.read_text(encoding="utf-8")
    assert "extra_script_path = $extraScriptPath" in text
    assert "extra_script_sha256 = $extraScriptSha" in text
    assert "extra_script_loaded = $extraScriptLoaded" in text
    resolution = text.index("$extraScript = $env:LOG1_MGBA_EXTRA_SCRIPT")
    identity = text.index("extra_script_path = $extraScriptPath")
    assert resolution < identity, "the bridge must be resolved before the identity that records it"
    assert "extra script SKIPPED" in text
    block = text[resolution:identity]
    assert "throw" not in block, "an unsupported build must skip, not refuse to launch"


def test_the_skill_document_carries_the_owner_exception() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert "dashboard input bridge" in text
    assert "2026-10-11" in text, "the exception is dated and authorised"
    assert "extra-script.json" in text, "the exception is reviewable because every run records it"
    assert "printed note" in text, "a build without --script must still launch"


@pytest.fixture(scope="module")
def canonical(tmp_path_factory) -> tuple[Path, Path]:
    """The canonical ROM and a state file, or a skip."""
    rom = canonical_rom_path()
    if rom is None:
        pytest.skip("canonical ROM not present locally")
    if hashlib.sha256(rom.read_bytes()).hexdigest() != CANONICAL_ROM_SHA256:
        pytest.skip("local ROM is not the canonical profile")
    # The launcher's default emulator is the digest-pinned 0.10.5 build, which a research worktree may not
    # carry. The dry run only needs an executable it can version-check, so the dev build is used when it is
    # present, and the test skips rather than pretending.
    global MGB_PATH
    candidates = sorted(ROOT.glob("build/tools/mgba-dev/extracted/*/mGBA.exe"))
    if not candidates:
        pytest.skip("no mGBA build present to version-check")
    MGB_PATH = candidates[0]
    directory = tmp_path_factory.mktemp("dryrun")
    state = directory / "state.ss1"
    state.write_bytes(b"\x00" * 32)
    return rom, state


MGB_PATH: Path | None = None


def dry_run(rom: Path, state: Path, extra: Path | None) -> dict:
    import os
    environment = dict(os.environ)
    environment.pop("LOG1_MGBA_EXTRA_SCRIPT", None)
    if extra is not None:
        environment["LOG1_MGBA_EXTRA_SCRIPT"] = str(extra)
    # The launcher is a PowerShell script; which host is on PATH differs between the operator's shell and a
    # test runner, so both spellings are tried before giving up.
    import shutil
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        pytest.skip("no PowerShell host on PATH")
    result = subprocess.run(
        [shell, "-NoProfile", "-File", str(CAPTURE),
         "-RomPath", str(rom), "-StatePath", str(state), "-DryRun",
         "-MGBPath", str(MGB_PATH), "-RequiredMGBVersion", "0.11"],
        cwd=ROOT, capture_output=True, text=True, env=environment)
    payload = result.stdout[result.stdout.index("{"):] if "{" in result.stdout else "{}"
    return json.loads(payload)


def test_a_dry_run_with_the_variable_records_the_path_and_hash(canonical) -> None:
    rom, state = canonical
    bridge = Path(tempfile.gettempdir()) / "dsh-extra-script-test.lua"
    bridge.write_text("-- a stand-in for the dashboard bridge\n", encoding="utf-8")
    identity = dry_run(rom, state, bridge)
    assert identity.get("extra_script_loaded") is True
    assert identity.get("extra_script_path") == str(bridge)
    assert identity.get("extra_script_sha256") == hashlib.sha256(bridge.read_bytes()).hexdigest().upper()
    assert "dashboard" in identity.get("extra_script_note", "")


def test_a_dry_run_without_the_variable_records_none(canonical) -> None:
    rom, state = canonical
    identity = dry_run(rom, state, None)
    assert identity.get("extra_script_loaded") is False
    assert identity.get("extra_script_path") is None
    assert identity.get("extra_script_sha256") is None
    assert "not set" in identity.get("extra_script_note", "")
