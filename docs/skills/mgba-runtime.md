# Runtime evidence: the mGBA capture skill

This file is the tracked authority for **any** emulator or runtime evidence in
this repository. It was previously only a machine-local file in an untracked
configuration directory,
which meant a fresh ticket worktree did not contain it and no reviewer could
hold anyone to it. That gap is closed here: the rules travel with the
repository, and `tests/unit/test_mgba_runtime_skill.py` fails when a launcher
departs from them.

Read this before touching mGBA. Every failure listed here has actually
happened, most of them more than once.

## 0. Read these first, in this order

1. Adja node `2d48ed8a`: "WORKING mGBA capture method", five numbered failure
   modes measured end to end.
2. `docs/runtime-capture.md`: the canonical, non-negotiable ordering.
3. `tools/runtime/run_mgba_capture.ps1`: the tracked launcher.

Call `adja_recall` with tags `mgba`, `runtime-capture` before starting. If you
find yourself writing UI-automation code to drive the Scripting window, stop:
it already exists and it is allowlisted.

## 1. Which vehicle

| Need | Use |
| --- | --- |
| GDB breakpoints, memory dumps, attributed stops | `tools/runtime/run_mgba_capture.ps1` |
| Lua scripted breakpoints, free-running core, human play | `start_toolkit031_session.ps1` plus `finish_toolkit031_session.ps1` |

**They are not interchangeable.** `run_mgba_capture.ps1` launches GDB-halted
and hands the single continue to the capture client. Under it a Lua `frame`
callback recorded **zero ticks**, measured in
`build/runtime-captures/20260909-113046-0ad4a46e`, whose `frame-tick.txt` was
never created. A Lua observer that bounds itself by frame count therefore
cannot run under the GDB launcher.

## 2. Emulator identity is the first failure mode

Two builds exist and they are **not** interchangeable:

| Build | Path | Has `emu:setBreakpoint`? |
| --- | --- | --- |
| 0.10.5 stable | `build\tools\mgba-0.10.5\extracted\mGBA-0.10.5-win64\mGBA.exe` | no |
| 0.11 dev | `build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe` | yes |

`C:\Program Files\mGBA\mGBA.exe` has been silently overwritten by the dev
build before. Always check `(Get-Item $path).VersionInfo.FileVersion`, never
trust the path. Both launchers fail closed on a `-RequiredMGBVersion` mismatch.

The Python drivers under `tools/runtime` obey the same rule.
`tools/runtime/mgba_identity.py` is the one identity policy for the GDB probe
family: `rom006_gdb_probe.py`, `rom007_factory_probe.py` and
`rom008_query_probe.py` call `require_mgba_build` before their `subprocess`
launch, and `rom009_callback_probe.py` is covered through
`rom008_query_probe.run_probe`, which it calls. That policy pins the packaged
0.10.5 executable SHA-256 which `docs/runtime-capture.md` already records beside
its `FileVersion`, so a Python driver refuses the same mismatching binary the
PowerShell launcher refuses. `rom011_live_watch.py` and
`rom012_live_containment.py` keep the instrumented-build identity instead: a
pinned source commit, the patch digest and the manifest-declared executable
digest, verified by `verify_instrumented_mgba`.

`tools/runtime/mgba_identity.py::LAUNCH_SITES` is the registry of every
repository-controlled place an mGBA process can start, in Python and in
PowerShell. Each entry carries one frozen classification, the `proof` mechanism
that actually gates it - `executable-digest`, `instrumented-manifest`,
`file-version` or `none` - and a written rationale. Read `proof`, not the class
name, to know which gate a site must have: the class name does not distinguish
the two builds that live inside `instrumented-required`. The recorded exceptions
where no emulator identity is checked at all are the Workbench launch, where a
user-selected mGBA is a product decision, and the combined-ROM smoke check,
whose claim is only that the image boots.

Measured API surface on the 0.11 dev build:

```text
emu:setBreakpoint / clearBreakpoint   yes
emu:loadStateFile / loadStateBuffer   yes
emu:saveStateFile                     yes
emu:getGameCode()                     "BG3E"   <- BARE, not "AGB-BG3E"
emu:romSize()                         8388608
```

`getGameCode()` returning the bare code has broken an observer's opening
`assert`. Accept both spellings.

## 3. Never write .lua or .ps1 through a shell heredoc

This has cost two separate sessions.

A shell heredoc eats backslashes, so the Lua pattern `"[^/\\]+$"` reaches disk
as `"[^/\]+$"`, an invalid escape sequence. The script then throws on load, the
ready marker is never written, and the launcher reports the misleading
`Lua script did not report ready`, which looks like an injection failure and is
not.

Use the `Write` tool for `.lua` and `.ps1`. If a patch must be made
programmatically, operate on bytes and build backslashes with `bytes([92])`.
Note also that `Set-Content -Encoding utf8` has written a byte-order mark on
this machine and broken line 1 of a `.ps1` and a `.lua` in the same session;
patch tracked scripts with `edit`, never by rewriting the whole file.

To see the real error rather than guessing, read the Scripting window's log
pane (AutomationId ends `.log`): it prints the Lua error verbatim.

## 4. Nothing may own the emulator's lifetime during human play

Much of this repository's evidence is produced by a human playing. Two separate
bugs killed a live session part-way through:

1. A deadline that counted setup. `-RunSeconds` started before launch,
   injection and state load, then force-killed mGBA mid-play.
2. A `finally` block plus a background job. Wrapping the launcher in
   `Start-Job` ties mGBA's lifetime to that job's session; when the tool call
   returned, the job was torn down, `finally` ran, and mGBA died after about
   twenty seconds. Symptom: `marker.txt` absent, capture ends around frame
   1320.

Rule: the script that launches mGBA for a human session must **start it and
exit**, holding no wait loop and no cleanup. The operator ends the session by
closing the window, and a separate script collects the evidence afterwards.
Never wrap an interactive session in `Start-Job`.

## 5. The proven sequence

```text
verify emulator version from the binary
  -> verify ROM identity against an EXACT caller-supplied digest
  -> refuse to race an existing mGBA process
  -> create a unique run directory under build/ (ignored)
  -> hash the savestate, copy it in, verify the copy
  -> launch mGBA on the ROM, wait ~8s for the UI
  -> inject the observer via tools/runtime/inject_mgba_lua.ps1
  -> load the savestate AFTER injection
  -> print the PID and EXIT
  -> [human plays, closes the window]
  -> re-verify the ROM hash, summarise the capture
```

**Load the state after injecting**, or construction-time triggers are missed:
entities are built during the load, so a breakpoint armed afterwards never sees
it. `emu:loadStateFile` is available on the 0.11 build and is the mechanism.

## 6. How the observer is delivered

The working path has been `tools/runtime/inject_mgba_lua.ps1`, which drives the
Scripting window by UI Automation and requires the observer to be an exact
allowlisted path. `mGBA.exe --script foo.lua` on its own bypasses the observer
allowlist and the launcher's ROM gate, and that is still forbidden. Node
`88c0c745` measured that it *can* work on the 0.11 dev build and recorded the two
governance caveats.

`tools/runtime/mgba_session.ps1` is the current mechanism, and it uses `--script`
while keeping both gates that a bare flag would drop:

- every Lua file it hands mGBA, the observer and the input driver alike, is put
  through `inject_mgba_lua.ps1 -CheckOnly` first, so the allowlist, the ready and
  marker roots, the long-string terminator and the pre-existence rules all still
  apply;
- the mechanism itself fails closed on the emulator version and on an exact ROM
  digest, so a launcher cannot reach the emulator without naming both. That is
  what section 6's rule always meant: not "never use the flag" but "never use it
  to leave the gates behind".

What it replaced, measured on the same build: a fixed eight-to-twelve second
sleep, a Scripting window opened by UI Automation, and a savestate loaded through
the File dialog. That was 17.2 seconds and three windows taking the operator's
foreground; it is now 7.6 seconds and none.

The savestate is loaded by the bootstrap after the observer's `dofile`, not by
mGBA's `-t`. Measured: with `-t` the state is already in memory when `--script`
runs, so an observer armed afterwards would miss anything the load constructs.

Two details in the injector are load-bearing, and `-CheckOnly` stops before both:

- Prompt selection is by `AutomationId` ending `.prompt`. Qt reports an empty
  `IsReadOnly` for all three Edits, so "first non-read-only" selects the log
  pane and `SetValue` throws `Value is read-only.`
- The Run-button `Invoke` runs in a bounded helper process, because mGBA wires
  it to a synchronous handler that can fail to return.

Every observer must be added to the `$allowedLua` allowlist in that script,
registered with real backslashes.

**Input in an observer is existing practice, not an exception.** Twenty-six of
the allow-listed observers call `emu:setKeys`, so an observer that drives a
controller is not by itself a rule break. What the rule asks is that the input is
deliberate and bounded: `tools/runtime/appearance001_table_watch.lua` sends keys
only when `APPEARANCE001_KEYS=1` is set by the launcher, which is off by default,
and its schedule is bounded so the run ends by itself. A future observer that
sends input should state that the same way rather than silently.

Quote characters do **not** survive PowerShell to UI Automation `SetValue`.
Write Lua sent that way with long-bracket strings: `print([[text]])`.

## 7. Observers stay read-only

`tests/unit/test_mgba_capture.py` greps observer sources and fails on input- or
memory-writing API names. Keep driving code in a separate file. A state load is
driving code: it belongs in the launcher's post-injection command, not in an
observer. Breakpoints are fine: they stop and resume the core, they do not
modify it.

## 8. Prove the instrument before believing a negative

A silent channel is not evidence of absence. TOOLKIT-029's EWRAM scan and
TOOLKIT-030's collision sampler were both invalidated for exactly this.

Give every observer a **liveness channel**: a second breakpoint on something
known to fire in the same run. Then:

| Target | Liveness | Conclusion |
| --- | --- | --- |
| silent | silent | **nothing**: the instrument is unproven |
| silent | fires | real negative: that path was not taken |
| fires | (any) | execution observed |

Say which case you are in, explicitly, in the closure report.

A liveness channel must be chosen for the run that is actually being made. A
construction-time breakpoint is a liveness channel for a cold boot and is
**silent by construction** in a run that loads a savestate, because the
entities were built before the state was written. Using one there produces the
"silent, silent" row and proves nothing.

## 9. Housekeeping

- A failed run can leave an mGBA holding TCP 2345, after which the launcher
  fails closed forever. Check `GetActiveTcpListeners` and stop the orphan.
- The canonical ROM and the savestate are **immutable**. Verify the hash before
  and after every run. Generated images live under `build/` and stay
  uncommitted.
- `run_mgba_capture.ps1` accepts `-GeneratedRomSha256 <exact digest>` to launch
  a generated image. It is still an equality test: there is no accept-anything
  switch, and omitting it keeps the strict canonical guard.
- Observers that write a `marker.txt` need `-SkipLuaArmedMarker` under the GDB
  launcher, which otherwise waits for an `armed-marker.txt` they never write.
