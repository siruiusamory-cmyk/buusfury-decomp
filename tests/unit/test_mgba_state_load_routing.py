"""RUNTIME-LOAD-STATE-ROUTING-001.

`tools/runtime/toolkit031_load_state.ps1` drove the mGBA Scripting window with
its own UI Automation: it selected the prompt by `AutomationId` and pushed one
`emu:loadStateFile` call through `SetValue`. The tracked runtime authority
(`docs/skills/mgba-runtime.md`, sections 6 and 7) makes
`tools/runtime/inject_mgba_lua.ps1` the one injection authority and puts a state
load in the launcher's post-injection command, never in an observer.

These are properties, not a restatement of one deletion: the second driver is
gone, nothing rebuilds it, and the inject-then-load capability it carried still
reaches the emulator through the single launch helper, in the order the
authority's proven sequence requires.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "tools/runtime"
INJECTOR = "tools/runtime/inject_mgba_lua.ps1"
#: The injector's bounded helper clicks Run inside the window the injector
#: already owns; it selects no prompt of its own.
HELPER = "tools/runtime/invoke_mgba_run.ps1"
#: Generated and repository-internal trees; they hold no tracked driver and a
#: stale copy under one must not be able to fail this check.
SKIP = {".git", "build"}
#: The machinery a Scripting-window driver cannot avoid. Qt reports an empty
#: IsReadOnly for all three Edits, so a driver that picks the prompt at all
#: picks it by AutomationId and writes through ValuePattern.
SCRIPTING_WINDOW = (
    "System.Windows.Automation",
    "UIAutomationClient",
    "UIAutomationTypes",
    "AutomationElement",
    "AutomationId",
    "ValuePattern",
    "QGBA::HistoryLineEdit",
)


def _powershell_files() -> list[str]:
    """Every PowerShell file in the tree, so a reintroduced driver cannot hide."""
    return sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*.ps1")
        if not SKIP & set(path.relative_to(ROOT).parts)
    )


def test_no_second_scripting_window_driver_remains():
    """One implementation drives the Scripting window, and only one."""
    offenders: dict[str, list[str]] = {}
    for relative in _powershell_files():
        if relative in (INJECTOR, HELPER):
            continue
        text = (ROOT / relative).read_text(encoding="utf-8", errors="replace")
        found = [token for token in SCRIPTING_WINDOW if token in text]
        if found:
            offenders[relative] = found
    assert not offenders, (
        "a second Scripting-window driver survives; route the command through "
        f"tools/runtime/inject_mgba_lua.ps1 instead: {offenders}")


def test_the_toolkit031_session_still_injects_before_it_loads():
    """The deleted driver's capability is preserved, in the proven order."""
    assert not (RUNTIME / "toolkit031_load_state.ps1").exists()
    session = (RUNTIME / "start_toolkit031_session.ps1").read_text(encoding="utf-8")
    assert "-StatePath $workingState" in session, (
        "the TOOLKIT-031 session must still ask the shared helper for a state")
    helper = (RUNTIME / "mgba_session.ps1").read_text(encoding="utf-8")
    # The observer is armed, then the state loads, then the ready marker is
    # written. A load before the dofile would miss construction-time triggers.
    load = helper.index("emu.loadStateFile")
    assert helper.index("dofile([[{0}]])") < load < helper.index("f:write([[ready]])")
