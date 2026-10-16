"""RUNTIME-LUA-INJECTOR-CONSOLIDATION-001.

`tools/runtime/load_mgba_lua.ps1` carried its own copy of the mGBA Scripting
window UI Automation, its own private observer allowlist, and no emulator
identity gate. The tracked runtime authority (`docs/skills/mgba-runtime.md`,
section 6, and `docs/runtime-capture.md`, "Tooling rules") says that
`tools/runtime/inject_mgba_lua.ps1` already owns that automation and that
"Every observer must be added to the `$allowedLua` allowlist in that script".

These tests pin the consolidation: one injection implementation, one allowlist,
and an explicit build-identity gate. They are properties, not a restatement of
one edit, so each one fails again if the duplication, the second allowlist, or
the missing version gate comes back.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "tools/runtime/load_mgba_lua.ps1"
INJECTOR = ROOT / "tools/runtime/inject_mgba_lua.ps1"
ROM006_BOOTSTRAPS = ("rom006_bootstrap.lua", "rom006_bootstrap_map4.lua")


def _launcher_text() -> str:
    return LAUNCHER.read_text(encoding="utf-8")


def _injector_allowlist_block() -> str:
    text = INJECTOR.read_text(encoding="utf-8")
    return text.split("$allowedLua", 1)[1].split("\n)", 1)[0]


def test_load_mgba_lua_delegates_injection_to_the_tracked_injector():
    """The one injection path in the tree is inject_mgba_lua.ps1."""
    text = _launcher_text()
    call = "& (Join-Path $PSScriptRoot 'inject_mgba_lua.ps1')"
    assert call in text, (
        "load_mgba_lua.ps1 must delegate Lua injection to the tracked injector")
    assert "-TargetProcessId $process.Id" in text, (
        "the delegation must be PID-scoped to the emulator this script launched")
    assert "-LuaPath $LuaPath" in text
    assert text.index("Start-Process") < text.index(call), (
        "the emulator is started, then injected into")


def test_load_mgba_lua_carries_no_scripting_window_automation():
    """The duplicated UI Automation driver is gone, not merely unused.

    `-not $edit.Current.IsReadOnly` is the literal broken prompt selector: Qt
    reports an empty IsReadOnly for all three Scripting Edits, so it matched the
    read-only log pane and SetValue failed with `Value is read-only.` The
    stronger check is that no Scripting-window machinery of any kind remains.
    """
    text = _launcher_text()
    assert "-not $edit.Current.IsReadOnly" not in text
    for machine in (
        "Automation",
        "System.Windows.Automation",
        "AutomationElement",
        "AutomationId",
        "Current.IsReadOnly",
        "ValuePattern",
        "InvokePattern",
        "ExpandCollapsePattern",
        "UIAutomationClient",
        "UIAutomationTypes",
        "QGBA::HistoryLineEdit",
    ):
        assert machine not in text, f"duplicated UI Automation survives: {machine}"
    assert "Scripting..." not in text, "the Tools/Scripting menu walk is duplicated"
    assert "Buu" not in text, "the loaded-ROM window title check is duplicated"


def test_load_mgba_lua_enforces_the_mgba_build_identity_gate():
    """Version is read from the binary and compared; never inferred from a path.

    `C:\\Program Files\\mGBA\\mGBA.exe` was measured holding 0.11.0.0, and both
    ROM-006 bootstraps open with `assert(emu:getGameCode() == "AGB-BG3E")`,
    which the 0.11 build fails because it reports the bare `BG3E`.
    """
    text = _launcher_text()
    assert "$RequiredMGBVersion = '0.10.5'" in text
    assert "VersionInfo.FileVersion" in text
    assert "mGBA version mismatch" in text
    assert "Resolve-Path -LiteralPath $resolvedMgb" in text, "must resolve the binary"
    # Pin the COMPARISON, not a version-looking string. Asserting that a path or a
    # filename contains "0.10.5" would pass for exactly the path-based reason the
    # gate exists to forbid.
    assert "$mgbVersion.StartsWith($RequiredMGBVersion)" in text, (
        "the gate must compare the version read from the binary")
    assert "$MgbaPath = 'C:\\Program Files\\mGBA" not in text, (
        "the default must not point at the shared install")


def test_the_rom006_bootstraps_are_allowlisted_once_by_the_injector():
    """Membership is decided in exactly one place, and it still fails closed."""
    block = _injector_allowlist_block()
    for name in ROM006_BOOTSTRAPS:
        assert block.count(name) == 1, (
            f"{name} must appear exactly once in the injector's $allowedLua")
    injector = INJECTOR.read_text(encoding="utf-8")
    assert "if ($resolvedLua -notin $allowedLua) {" in injector
    assert "LuaPath is not an allowlisted tracked movement script" in injector


def test_load_mgba_lua_keeps_no_second_lua_allowlist():
    """The launcher must not name permitted Lua scripts at all.

    A private path list that gates admission is a second allowlist, and two
    lists drift. It also means the launcher could refuse a path the injector
    accepts, or admit one it does not.
    """
    text = _launcher_text()
    assert "allowedPairs" not in text
    for name in ROM006_BOOTSTRAPS:
        assert name not in text, (
            f"{name} is named by the launcher; the injector's $allowedLua is the "
            "only membership check")


def test_load_mgba_lua_keeps_the_rom006_expected_state_gate():
    """The launcher keeps only its ROM-006-specific behaviour."""
    text = _launcher_text()
    assert "build\\rom006" in text
    for state in ("bootstrap.mss", "bootstrap-map4.mss"):
        assert state in text
    assert "$resolvedExpectedState -notin $allowedStates" in text
    # A stale state is deleted, so confinement to the ignored bootstrap
    # directory is what keeps that deletion from reaching anything else.
    assert text.index("$resolvedExpectedState -notin $allowedStates") < text.index(
        "Remove-Item -LiteralPath $ExpectedState")
    # The state the bootstrap writes is awaited, and its absence fails closed.
    assert text.index("inject_mgba_lua.ps1") < text.rindex(
        "Test-Path -LiteralPath $ExpectedState")
    assert "throw 'Expected state was not created'" in text
    # The ROM is an immutable input here, checked on both sides of the run.
    assert text.count("Get-FileHash -Algorithm SHA256 -LiteralPath $RomPath") == 2
    assert "ROM changed during mGBA bootstrap" in text
