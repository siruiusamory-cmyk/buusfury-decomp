"""The injector's two arm steps that survive an operator, driven with fakes.

tools/runtime/inject_mgba_lua.ps1 must keep arming while the owner clicks or
types anywhere (P-370: a click closes the Tools popup, so the first attempt died
with "Scripting menu item not found"). Two steps carry that:

  * the Tools-menu step re-expands Tools and retries, bounded at 10 attempts and
    never fewer than 5, instead of throwing on the first miss;
  * the Scripting prompt is read back through ValuePattern and re-set before the
    Run is invoked, at most 5 times, because the operator can type into it.

Both are pure functions of the caller's own UI Automation access
(tools/runtime/mgba_arm.ps1, which the injector dot-sources), so this test drives
the shipped decisions with scriptblocks instead of a copy of them.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INJECTOR = PROJECT_ROOT / "tools/runtime/inject_mgba_lua.ps1"
ARM_HELPERS = PROJECT_ROOT / "tools/runtime/mgba_arm.ps1"


def _run_ps(body):
    """Run one snippet with the injector's arm helpers dot-sourced."""
    powershell = shutil.which("powershell.exe")
    if powershell is None:
        pytest.skip("the injector is driven by Windows PowerShell; this host has none")
    assert ARM_HELPERS.is_file(), "the injector's arm helpers are missing"
    result = subprocess.run(
        [
            powershell, "-NoProfile", "-NonInteractive",
            "-ExecutionPolicy", "Bypass", "-Command",
            ". '" + str(ARM_HELPERS) + "'; " + body,
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    return result


def test_menu_retry_re_expands_and_finds_on_a_later_attempt():
    """A click closes the popup, so the item can be found on a later attempt."""
    result = _run_ps(
        "\n".join(
            [
                "$state = @{ expands = 0; finds = 0 }",
                "$item = Invoke-MgbaMenuWithRetry -ReExpand { $state.expands++ }"
                " -FindItem { $state.finds++; if ($state.finds -ge 3) { 'ITEM' }"
                " else { $null } } -Pause { }",
                "\"RESULT=$item EXPANDS=$($state.expands) FINDS=$($state.finds)\"",
            ]
        )
    )
    assert result.returncode == 0, result.stderr
    assert "RESULT=ITEM" in result.stdout, result.stdout
    # Every attempt re-expands, and the attempt that found it is the third.
    assert "EXPANDS=3 FINDS=3" in result.stdout, result.stdout
    assert "attempt 3 of 10" in result.stdout, result.stdout


def test_menu_retry_is_bounded_and_throws_only_after_the_last_attempt():
    result = _run_ps(
        "\n".join(
            [
                "$state = @{ expands = 0 }",
                "try { Invoke-MgbaMenuWithRetry -ReExpand { $state.expands++ }"
                " -FindItem { $null } -Pause { }; 'NO_THROW' }",
                "catch { \"THREW: $($_.Exception.Message)\" }",
                "\"EXPANDS=$($state.expands)\"",
            ]
        )
    )
    assert result.returncode == 0, result.stderr
    assert "NO_THROW" not in result.stdout, result.stdout
    assert "after 10 attempts" in result.stdout, result.stdout
    assert "EXPANDS=10" in result.stdout, result.stdout


def test_menu_retry_bounds_refuse_fewer_than_five_and_more_than_ten():
    result = _run_ps(
        "try { Invoke-MgbaMenuWithRetry -ReExpand { } -FindItem { 'X' } "
        "-MinAttempts 4 -Pause { }; 'NO_THROW_MIN' } "
        "catch { \"THREW_MIN: $($_.Exception.Message)\" } "
        "try { Invoke-MgbaMenuWithRetry -ReExpand { } -FindItem { 'X' } "
        "-MaxAttempts 11 -Pause { }; 'NO_THROW_MAX' } "
        "catch { \"THREW_MAX: $($_.Exception.Message)\" }"
    )
    assert result.returncode == 0, result.stderr
    assert "NO_THROW_MIN" not in result.stdout, result.stdout
    assert "NO_THROW_MAX" not in result.stdout, result.stdout
    assert "at least 5" in result.stdout, result.stdout
    assert "at most 10" in result.stdout, result.stdout


def test_prompt_is_read_back_and_re_set_when_the_operator_typed_into_it():
    result = _run_ps(
        "\n".join(
            [
                "$state = @{ reads = 0; sets = 0 }",
                "$ok = Set-MgbaPromptCommand"
                " -ReadValue { $state.reads++; if ($state.reads -ge 2) { 'CMD' }"
                " else { 'operator typed this' } }"
                " -SetValue { param($value) $state.sets++ }"
                " -Command 'CMD' -Pause { }",
                "\"OK=$ok READS=$($state.reads) SETS=$($state.sets)\"",
            ]
        )
    )
    assert result.returncode == 0, result.stderr
    assert "OK=True" in result.stdout, result.stdout
    # One read that saw the operator's text, one re-set, one confirming read.
    assert "READS=2 SETS=1" in result.stdout, result.stdout


def test_prompt_read_back_refuses_to_run_after_five_re_sets():
    result = _run_ps(
        "\n".join(
            [
                "$state = @{ reads = 0; sets = 0 }",
                "try { Set-MgbaPromptCommand"
                " -ReadValue { $state.reads++; 'operator typed this' }"
                " -SetValue { param($value) $state.sets++ }"
                " -Command 'CMD' -Pause { }; 'NO_THROW' }",
                "catch { \"THREW: $($_.Exception.Message)\" }",
                "\"READS=$($state.reads) SETS=$($state.sets)\"",
            ]
        )
    )
    assert result.returncode == 0, result.stderr
    assert "NO_THROW" not in result.stdout, result.stdout
    assert "after 5 attempt" in result.stdout, result.stdout
    # Five re-sets, each followed by a read that still did not hold the command.
    assert "READS=6 SETS=5" in result.stdout, result.stdout


def test_injector_arms_through_the_helpers_and_never_needs_focus():
    injector = INJECTOR.read_text(encoding="utf-8")
    helpers = ARM_HELPERS.read_text(encoding="utf-8")

    assert "mgba_arm.ps1" in injector
    assert "Invoke-MgbaMenuWithRetry" in injector
    assert "Set-MgbaPromptCommand" in injector
    # The single-shot throw is what a click defeated; it must be gone from the
    # injector, and the read-back must land before the Run helper is started.
    assert "Scripting menu item not found" not in injector
    assert injector.index("Set-MgbaPromptCommand") < injector.index("Start-Process")
    # A3: an open Scripting window is reused, and the injector closes no window.
    assert "Find-MgbaWindow -NamePattern '^Scripting$'" in injector
    assert "CloseMainWindow" not in injector
    assert ".Close(" not in injector

    # A4: UI Automation patterns only, in the injector and in its helpers.
    for forbidden in ("SendKeys", "SetForegroundWindow", "SendInput", "BlockInput"):
        assert forbidden not in helpers, forbidden
        assert forbidden not in injector, forbidden
