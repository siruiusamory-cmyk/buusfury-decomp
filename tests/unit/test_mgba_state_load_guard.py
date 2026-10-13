"""STATE-LOAD-GUARD-001: a savestate load that fails must stop the run.

`tools/runtime/mgba_session.ps1` composed a bootstrap that loaded the state with
`assert(pcall(emu.loadStateFile, emu, [[<path>]]), [[savestate load failed]])`. `pcall`
reports only whether the call THREW, and `emu:loadStateFile` signals an ordinary failure by
RETURNING false. A failed load therefore passed silently and the run continued with no state
at all, the only symptom being the launcher's misleading "Lua script did not report ready".

These are source-level checks, which is how this repository holds launcher text that only a
real launch could otherwise execute (see `tests/unit/test_mgba_extra_script.py`). Order alone
cannot carry a claim about containment: where a statement must live inside a block, the block is
extracted by brace matching and searched, because a statement moved past the closing brace
satisfies a position comparison. `helper_text` honours the test-only `STATE_LOAD_GUARD_TEST_LAUNCHER`
override so a mutation check can drive these tests against a broken COPY of the launcher; it is
unset in every real run.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "tools" / "runtime" / "mgba_session.ps1"
#: TEST-ONLY, and unset everywhere else. It exists so the mutation checks can drive these tests
#: against a deliberately broken COPY of the launcher without touching the tracked file.
LAUNCHER_OVERRIDE = "STATE_LOAD_GUARD_TEST_LAUNCHER"


def helper_text() -> str:
    """The launcher text, or the copy named by the test-only override above."""
    override = os.environ.get(LAUNCHER_OVERRIDE)
    if override:
        return Path(override).read_text(encoding="utf-8")
    return HELPER.read_text(encoding="utf-8")


def at(text: str, needle: str) -> int:
    """Where a pinned literal sits. An assertion, so a removed guard fails with its own message."""
    position = text.find(needle)
    assert position != -1, f"not present in the shared launcher: {needle!r}"
    return position


def braced_block(text: str, header: str) -> str:
    """The body of the brace-delimited block that `header` opens, by counting braces.

    Indentation and blank lines are not evidence of containment. A position comparison proves a
    statement comes after the keyword, which a statement moved past the closing brace also
    satisfies, so the blocks that have to hold something are extracted and searched instead.
    """
    start = at(text, header) + len(header)
    assert text[start - 1] == "{", f"{header!r} must end at the brace it opens"
    depth = 1
    for position in range(start, len(text)):
        if text[position] == "{":
            depth += 1
        elif text[position] == "}":
            depth -= 1
            if depth == 0:
                return text[start:position]
    raise AssertionError(f"unbalanced braces after {header!r}")


def test_the_bootstrap_captures_both_results_and_records_them() -> None:
    text = helper_text()
    assert "assert(pcall(emu.loadStateFile" not in text, (
        "the silent form is back: pcall cannot see a load that returned false")
    assert "local state_ok, state_err = emu.loadStateFile(emu, [[" in text, (
        "the load must capture the returned value and the error text, not just a throw")
    assert "state-load.txt" in text, "the result must be recorded in the run directory"
    assert "state_log:write([[ok ]]" in text
    assert "state_ok and [[true]] or [[false]]" in text, (
        "the record must say whether ok was true")
    assert "tostring(state_err)" in text, "the record must carry the error text"
    assert "[[path ]]" in text, "the record must name the state path"


def test_the_bootstrap_refuses_to_continue_when_the_load_is_not_true() -> None:
    text = helper_text()
    capture = at(text, "local state_ok, state_err")
    record = at(text, "state_log:write([[ok ]]")
    refuse = at(text, "if not state_ok then error(")
    ready = at(text, "f:write([[ready]])")
    assert capture < record < refuse < ready, (
        "the load is captured, the record written, then the bootstrap raises - all before the "
        "ready marker, or the launcher waits on a marker that a failed run must never write")


def test_the_state_load_never_writes_state_bytes() -> None:
    """The record carries ok, the error string and the state path. Nothing else travels."""
    text = helper_text()
    write = at(text, "state_log:write([[ok ]]")
    statement = text[write:text.index("\n", write)]
    for field in ("[[ok ]]", "[[err ]]", "[[path ]]", "tostring(state_err)"):
        assert field in statement, f"the record statement must carry {field}"
    for forbidden in ("saveStateFile", "loadStateBuffer", "saveStateBuffer"):
        assert forbidden not in text, (
            f"{forbidden} names state bytes; the launcher loads a state and records only its result")
        assert forbidden not in statement


def test_the_launcher_reports_the_load_failure_instead_of_the_timeout() -> None:
    text = helper_text()
    assert "if ($StatePath -and (Test-Path -LiteralPath $stateLoadRecord))" in text, (
        "the recorded reason is read only when a state was requested and the record exists")
    assert "Get-Content -LiteralPath $stateLoadRecord -Raw" in text
    assert "state-load-failure.txt" in text, "the reason must reach the run directory"
    assert 'throw "savestate load failed: $reason"' in text, "the operator must get the load's reason"
    reason = at(text, 'throw "savestate load failed: $reason"')
    generic = at(text, "throw 'Lua script did not report ready'")
    assert reason < generic, (
        "the load's own reason must be thrown before the generic ready-timeout message")
    guarded = braced_block(text, "if ($StatePath -and (Test-Path -LiteralPath $stateLoadRecord)) {")
    assert 'throw "savestate load failed: $reason"' in guarded, (
        "the reason must be thrown INSIDE that guard, or a run whose record is absent loses the "
        "generic message too")
    assert "throw 'Lua script did not report ready'" not in guarded


def test_the_no_state_path_keeps_its_existing_behaviour() -> None:
    """A launcher with no state to load must be unchanged: no record, the same message."""
    text = helper_text()
    assert "throw 'Lua script did not report ready'" in text, (
        "the generic message is still the fallback for a run that loads no state")
    record = at(text, "state-load.txt")
    guard = at(text, "if ($StatePath -and (Test-Path -LiteralPath $stateLoadRecord))")
    assert record < guard, (
        "the state-load record belongs to the state path, which is composed above it")
    assert "if ($StatePath) {" in text, "the state branch must stay conditional on a requested state"


def test_a_state_requested_through_the_postcommand_shape_takes_the_same_guard() -> None:
    """The second admitted PostCommand shape is a state request, so it must not compose raw.

    `start_spritenew001_session.ps1` asks for its state that way, and a raw composition there kept
    exactly the defect this ticket closes: no record and no abort, and the launcher printed
    SESSION LIVE with no state loaded.
    """
    text = helper_text()
    assert "elseif ($PostCommand -match '^emu:loadStateFile" in text, (
        "the shape must be matched positively, or it falls through to the raw composition")
    assert "$PostCommand -notmatch '^emu:loadStateFile" not in text
    refuse = at(text, "a savestate was requested twice")
    promote = at(text, "$StatePath = [System.IO.Path]::GetFullPath($Matches['state'])")
    clear = at(text, "$PostCommand = $null")
    composed = at(text, "local state_ok, state_err")
    assert refuse < promote < clear < composed, (
        "a second state request is refused, then the path becomes $StatePath and the raw command "
        "is cleared, so the guarded composer below is the one that loads it")
    # And the dofile shape keeps its own branch, untouched.
    dofile = at(text, "if ($PostCommand -match '^dofile")
    assert dofile < at(text, "elseif ($PostCommand -match '^emu:loadStateFile")
    assert "PostCommand dofile target is not allowlisted" in text


def test_the_stale_load_records_are_deleted_before_launch() -> None:
    """A reused run directory must not report the previous run's load result as this run's.

    The ready and marker files were already cleared before launch; the two load records were not,
    so an unrelated timeout in a reused directory could be explained by a record from an earlier
    run.
    """
    text = helper_text()
    ready = at(text, "Remove-Item -LiteralPath $ReadyPath -Force")
    header = "foreach ($staleRecord in 'state-load.txt', 'state-load-failure.txt') {"
    loop = at(text, header)
    composed = at(text, "local state_ok, state_err")
    assert ready < loop < composed, (
        "both records are deleted beside the ready and marker files, which is before the bootstrap "
        "that would write them again and before anything is launched")
    body = braced_block(text, header)
    assert "$stalePath = Join-Path $RunDir $staleRecord" in body
    assert "Remove-Item -LiteralPath $stalePath -Force" in body, (
        "the deletion must be INSIDE the loop over both records, or a statement moved past the "
        "closing brace clears only the last one")


def test_the_rom_digest_is_cleared_inside_the_finally_that_owns_the_launch() -> None:
    """The export is process-wide, so a later mGBA start in the same shell would read it.

    Containment, not order: a clear moved to just after the finally's closing brace still sits
    after the keyword and still runs on the normal path, so an order test stays green while a
    launch that throws leaks the digest. The block is extracted by counting braces.
    """
    text = helper_text()
    clearing = "Remove-Item -LiteralPath Env:\\LOG1_MGBA_ROM_SHA256"
    gate = at(text, "ROM identity mismatch; run refused")
    export = at(text, "$env:LOG1_MGBA_ROM_SHA256 = $expectedHash")
    launch = at(text, "$process = Start-Process")
    opened = text.rindex("try {", 0, launch)
    closed = at(text, "} finally {")
    assert gate < export < opened < launch < closed, (
        "the export must stay after the equality gate, and the finally must be the one that owns "
        "the launch")
    assert text.count(clearing) == 1
    body = braced_block(text, "} finally {")
    assert clearing in body, (
        "the clear must be INSIDE that finally, or a launch that throws leaves the digest set")
