"""RUNTIME-LOAD-STATE-ROUTING-001.

`tools/runtime/toolkit031_load_state.ps1` drove the mGBA Scripting window with
its own UI Automation: it selected the prompt by `AutomationId` and pushed one
`emu:loadStateFile` call through `SetValue`. The tracked runtime authority
(`docs/skills/mgba-runtime.md`, sections 6 and 7) makes
`tools/runtime/inject_mgba_lua.ps1` the one injection authority and puts a state
load in the launcher's post-injection command, never in an observer.

Scope of the first check, stated exactly: every TRACKED PowerShell file in the
tree, classified as a Scripting-window driver only when it carries BOTH the UI
Automation namespaces and the prompt-selection tokens a driver needs. A file
that merely names one of them, a scratch script left untracked in the working
tree, and a driver written in another language are outside that scope, so the
check cannot fail on a file that is not a driver.

The remaining checks pin what replaced the driver: the retired filename stays
tracked as an inert tombstone filed in the README table, and the TOOLKIT-031
session still asks the shared launcher for observer-then-load, in that order.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "tools/runtime"
INJECTOR = "tools/runtime/inject_mgba_lua.ps1"
#: Prompt selection needs both halves. Qt reports an empty IsReadOnly for all
#: three Scripting Edits, so a driver picks the prompt by AutomationId and
#: writes through ValuePattern; a comment naming one token is not a driver.
AUTOMATION = (
    "System.Windows.Automation",
    "UIAutomationClient",
    "UIAutomationTypes",
    "AutomationElement",
)
PROMPT = ("AutomationId", "ValuePattern", "QGBA::HistoryLineEdit")
TOMBSTONE = RUNTIME / "toolkit031_load_state.ps1"


def _tracked_powershell() -> list[str]:
    """Every tracked PowerShell file, so untracked scratch cannot fail this."""
    listing = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.ps1"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [line for line in listing.splitlines() if line.strip()]


def _is_scripting_window_driver(text: str) -> bool:
    return any(token in text for token in AUTOMATION) and any(
        token in text for token in PROMPT
    )


def test_the_driver_predicate_separates_a_driver_from_a_mention():
    """Positive and negative control for the classifier the guard rests on."""
    assert _is_scripting_window_driver(
        'Add-Type -AssemblyName UIAutomationClient\n'
        'if ($edit.Current.AutomationId.EndsWith(".prompt")) { }\n'
        '$edit.GetCurrentPattern([ValuePattern]::Pattern).SetValue($command)\n'
    )
    assert not _is_scripting_window_driver(
        "# The Scripting window automation lives in inject_mgba_lua.ps1,\n"
        "# which is the only file allowed to use UIAutomationClient.\n"
    )


def test_no_second_scripting_window_driver_remains():
    """One implementation drives the Scripting window, and only one."""
    offenders = [
        relative
        for relative in _tracked_powershell()
        if relative != INJECTOR
        and _is_scripting_window_driver(
            (ROOT / relative).read_text(encoding="utf-8", errors="replace")
        )
    ]
    assert not offenders, (
        "a second Scripting-window driver survives; route the command through "
        f"tools/runtime/inject_mgba_lua.ps1 instead: {offenders}")


def test_the_withdrawn_driver_is_an_inert_tombstone():
    """Retired, not runnable, and still resolvable for a citing document."""
    text = TOMBSTONE.read_text(encoding="utf-8")
    assert text.startswith("throw 'RETIRED:")
    assert text.count("\n") == 1, "a tombstone is one failing statement"
    assert "start_toolkit031_session.ps1" in text
    readme = (RUNTIME / "README.md").read_text(encoding="utf-8")
    assert "| `toolkit031_load_state.ps1` |" in readme, (
        "the retired helper must be filed in the README's retired table")


def test_the_toolkit031_session_still_injects_before_it_loads():
    """The tombstone's capability is preserved, in the proven order."""
    session = (RUNTIME / "start_toolkit031_session.ps1").read_text(encoding="utf-8")
    assert "-StatePath $workingState" in session, (
        "the TOOLKIT-031 session must still ask the shared helper for a state")
    helper = (RUNTIME / "mgba_session.ps1").read_text(encoding="utf-8")
    # The observer is armed, then the state loads, then the ready marker is
    # written. A load before the dofile would miss construction-time triggers.
    load = helper.index("emu.loadStateFile")
    assert helper.index("dofile([[{0}]])") < load < helper.index("f:write([[ready]])")
