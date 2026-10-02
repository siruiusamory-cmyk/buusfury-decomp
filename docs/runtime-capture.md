# Canonical mGBA Runtime Capture Pipeline

## Purpose and status

Use this pipeline for bounded runtime event capture instead of writing another
one-off GDB client under `build/research/`.

- **Historical pipeline:** `CONFIRMED` working. The P-004 session launched a
  fresh mGBA process with `--gdb` and `single-wolf.ss1`, connected one capture
  client, installed the HURT breakpoint, and collected seven attributed stops
  plus 132 memory records.
- **Tracked replacement:** mechanically preserves that ordering and the proven
  RSP parser. Its protocol and generated-file logic have portable synthetic
  tests.
- **Live validation 2026-08-26:** `CONFIRMED` working. The tracked launcher
  (`run_mgba_capture.ps1`) with the non-connecting port check launched a fresh
  mGBA PID, armed the HURT breakpoint at `0x0801920E`, and captured 10 clean
  stops attributed to `r1 = 0x0203D504` (wolf combat object) in run
  `build/runtime-captures/20260826-172018-fac53b96`. ROM identity verified
  before and after. Post-launch readiness polling uses the same non-connecting
  query. Regression test added and passing.

The tracked components are:

- `tools/runtime/run_mgba_capture.ps1`: identity checks, isolated launch, Lua
  injection/arming when requested, capture invocation, cleanup, and post-run
  ROM verification.
- `tools/runtime/capture_mgba_event.py`: bounded event loop and evidence files.
- `tools/runtime/mgba_capture.py`: read-only RSP allowlist, robust framing,
  chunked reads, pointer-shape scan, and versioned dump records.
- `tools/runtime/inject_mgba_lua.ps1`: PID-scoped Lua injection with a bounded
  helper process so an mGBA Run-button deadlock cannot strand the caller.

## Tooling rules

These are the hard rules for anyone touching the runtime toolbox. Each one was
learned from a measurement that went wrong.

- **Reuse the tracked launcher and client.** Do not reconstruct the GDB/Lua
  launch-arm-continue sequence in an ignored script under `build/research/`, and
  do not hand-drive the mGBA Scripting window. That automation already exists in
  `tools/runtime/inject_mgba_lua.ps1` and is allowlisted per script.
- **Never author a `.lua` or `.ps1` file through a shell heredoc.** It mangles
  backslashes, so a Lua pattern such as `"[^/\\]+$"` reaches disk as an invalid
  escape, the script throws on load, and the launcher reports the misleading
  "Lua script did not report ready". Write the file with a real file write.
- **A launcher for a human play session must start the emulator and exit**,
  owning no wait loop and no cleanup. Two separate defects have killed live
  sessions mid-play: a deadline that counted setup time, and a `finally` block
  firing when the job hosting the script was torn down. Never wrap an
  interactive session in a background job. The operator ends the session; a
  second script collects the evidence afterwards.
- **Verify the emulator from the binary's `VersionInfo.FileVersion`**, never
  from its path. Two builds are present and only the newer one has the scripted
  breakpoint API; the stable install has been silently overwritten before.
- **The emulator has one GDB slot.** Merely completing a TCP handshake to port
  2345 steals it, so a readiness check must not connect. There is a regression
  test for this: `tools/runtime/test_launcher_no_tcpclient.ps1`.
- **A silent instrument is not negative evidence.** Every observer carries a
  liveness channel watching something known to fire, and the closure report
  states which case the run is in: target silent plus liveness silent proves
  nothing, target silent plus liveness firing is a real negative.

## Provenance of this pipeline

The durable source is the tracked pipeline above. It mechanically preserves the
ordering and the protocol parser that were proven in the original capture
sessions; the ignored local research artifacts that were present at the time
(one-off capture clients, a CSV and a memory dump) remain private research
material and are not part of the repository. Do not move that CSV, those memory
dumps, savestates, saves or any ROM into tracked paths.

## Non-negotiable ordering

```text
verify exact ROM identity and hash the private state
  -> copy the state into the unique ignored run directory
  -> refuse if TCP 2345 already has an owner
  -> create a unique ignored run directory
  -> launch one fresh mGBA PID with --gdb and isolated savegamePath
  -> while emulation is halted, optionally inject Lua into that exact PID
  -> wait for injection readiness and, when supported, armed-marker.txt
  -> start one capture client
  -> that client installs all break/watchpoints
  -> that same client sends the first continue packet
  -> human produces the requested gameplay event
  -> capture stops at the bound or STOP-NOW.txt
  -> clear traps, close the client, stop only the owned mGBA PID
  -> verify the original ROM hash again
```

There must be one GDB owner. Do not use a second script to pre-continue the
emulator, and do not attach a new controller while another client owns port
2345. The launcher fails closed when it detects an existing listener.

For full-speed Lua-only behavioral traces, omit `-Breakpoint`. The same single
capture client still owns GDB and sends the first continue; Lua writes only to
the unique ignored run directory. This mode records zero executable stops and
must not be presented as breakpoint evidence.

Optional executable-stop filters include `-LrFilter`, `-DumpWord0Filter`, and
the generic `-DecreaseRegister` plus `-CompareDumpOffset/-CompareLength`.
Filters reduce recorded evidence only; mGBA still halts at the underlying
breakpoint, so use Lua-only mode when stop frequency distorts gameplay speed.

## A transition needs no leave-and-re-enter

**A transition edit is consumed when its trigger fires**, so the first trigger
after a load is valid evidence. A leave-and-re-enter cycle is **not** a generic
prerequisite for warp proof.

The re-entry rule that `MAP-TILE-PAINT-001` established is scoped to **map and
background assembly**: a savestate restores the already-built background, so a
ROM-side *map* edit cannot appear until the engine rebuilds the area. A
*transition* is not assembled that way - its destination and facing are read when
the door fires - and asking an operator for a rebuild loop on a transition run is
wasted effort and, when the savestate loads them on the doorway, impossible.

Confirmed 2026-09-26 by `MAP-WARP-RUNTIME-EDIT-001` and
`MAP-WARP-FACING-TRACE-001`: on the first trigger from a savestate-restored map
the engine entered the authored destination and wrote the authored facing, which
a cached retail destination could not explain.

This file is the authoritative runtime capture procedure for this repository.

## Standard command

From the repository root, a HURT-entry capture matching the old P-004 shape is:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File tools/runtime/run_mgba_capture.ps1 `
  -StatePath build/research/p003-exp/single-wolf.ss1 `
  -Breakpoint 0x0801920E `
  -DumpRegister 1 `
  -DumpLength 0x240 `
  -MaxStops 20 `
  -WindowSeconds 600 `
  -ScanEwramPointers
```

Add `-LuaPath tools/runtime/p004_actor_focus.lua` only when that Lua observer
is actually needed. The launcher waits for the script's `armed-marker.txt` by
default. A script that has no armed-marker contract requires the explicit
`-SkipLuaArmedMarker` switch.

Use `-StackLength` only when the default 64-byte return-candidate window is
demonstrably too short. It accepts 4-byte multiples from 64 through 1024 and
is recorded in `capture.json`; keep the smallest resolving bound. P-006A used
`0xC0` after the 64-byte death stack ended inside generic dispatch wrappers.

The launcher runs the pinned stable emulator at
`build/tools/mgba-0.10.5/extracted/mGBA-0.10.5-win64/mGBA.exe` and refuses any
binary whose `FileVersion` does not begin with `0.10.5`. Do not point
`-MGBPath` at a shared system install; that install was silently replaced by a
development build once already.

Use `-DryRun` first to validate the ROM, state, mGBA executable, and requested
inputs without launching mGBA or creating outputs. The explicit execution
policy flag is required on this workstation, where direct `.ps1` invocation is
disabled by the user-level PowerShell policy.

To end a long capture early, create the exact `STOP-NOW.txt` path printed by
the launcher. Each run uses a unique directory under
`build/runtime-captures/`, preventing stale ready/stop markers from affecting
the next load epoch.

## Evidence products

Every tracked capture writes:

- `inputs.json`: ROM/source-state identities, working-state path, and requested
  breakpoint. mGBA loads the ignored working copy, never the source state.
- `capture/capture.json`: capture parameters, final status, stop count, and
  elapsed time.
- `capture/capture-ready.txt`: proof that the client received a halt reply and
  mGBA accepted the breakpoint before gameplay began.
- `capture/events.csv`: registers, PC/LR/SP, stack-shaped ROM return addresses,
  and the dynamic dump address for each stop.
- `capture/dumps.wfcap`: `WFCAP001` header followed by little-endian
  `(stop, address, length)` records and raw payloads.
- `capture/ewram-pointers.csv`: optional numeric pointer-shape observations.
  These are candidates only; they do not establish object type or semantics.

All generated products are ignored because they may contain proprietary or
private runtime data. Record only the minimum evidence-derived facts in the
tracked research documentation.

## Failure modes that must stay learned

### The emulator binary must be version-verified, not path-trusted (2026-08-27)

`C:\Program Files\mGBA\mGBA.exe` was overwritten in place by the 0.11
development build. Its SHA-256 was byte-identical to the ignored dev build under
`build/tools/mgba-dev/`, and its window title read `0.11-9128-c65e8a3d4`. Every
capture launched through the old default silently ran an emulator the research
tickets do not accept, and the earlier "state is not loading or advancing"
observation was that build rather than a Lua defect.

Stable mGBA 0.10.5 is now kept separately at
`build/tools/mgba-0.10.5/extracted/mGBA-0.10.5-win64/mGBA.exe`:

| Property | Value |
|---|---|
| `FileVersion` | `0.10.5.0` |
| Executable SHA-256 | `5A3C98C2984DD04BD0D7C9378CDFAE937AE0D73A196C880BB2EECF3B254AF247` |
| Source archive | `mGBA-0.10.5-win64.7z` |
| Archive SHA-256 | `B497A57C7D9093834DADC64F33A90F7C411439C21FDB8A0143255A45EA37563A` |

`run_mgba_capture.ps1` defaults `-MGBPath` to that copy and verifies
`-RequiredMGBVersion` (default `0.10.5`) against the binary's `FileVersion`,
failing closed on mismatch. Overriding the version is a deliberate act.

### Select the Lua prompt by control identity, not `IsReadOnly`

The Scripting window exposes three `Edit` elements: the log pane
(`QGBA::LogWidget`), the script buffer (`QPlainTextEdit`), and the prompt
(`QGBA::HistoryLineEdit`). Qt reports an **empty** `IsReadOnly` for all three,
so the old `if (-not $edit.Current.IsReadOnly)` test matched the first
descendant, the read-only log pane, and `SetValue` failed with
`Value is read-only.` `inject_mgba_lua.ps1` now matches the `AutomationId`
ending in `.prompt`, falls back to the `QGBA::HistoryLineEdit` class, and only
then to an explicit `-eq $false` comparison.

### Never author a Lua or PowerShell file through a shell heredoc

Writing `p006c_ctrl_stack.lua` through a heredoc mangled the Lua pattern
`"[^/\\]+$"` into `"[^/\]+$"`. Init then threw before the injected command
finished, the ready file was never created, and the launcher reported
`Lua script did not report ready`, a message that points at the emulator
rather than at the real cause. Author these files with an editor tool and
verify the escapes on disk.

### Clear the orphaned emulator before relaunching

A launcher run that fails after `Start-Process` leaves an mGBA process holding
TCP 2345. Because the launcher fails closed when a listener exists, every later
launch aborts until that process is stopped. Confirm with
`GetActiveTcpListeners()` and stop only the orphaned PID.

### Full-EWRAM discovery is cheap and is not a readiness risk

Measured in run `20260827-230550-7a8e5aaf`: scanning
`0x02000000..0x02040000` on a 4-byte stride for dispatch word `0x0804C484`
takes **0.102 seconds** from the Scripting prompt and returns **exactly one**
match. Init-time discovery is therefore safe; a `Lua script did not report
ready` failure is not explained by scan cost, since that wait allows ten
seconds.

### A PNG prefix does not prove a savestate is corrupt

The successfully loaded `single-wolf.ss1` was 65,121 bytes with SHA-256
`58146DFE8B12F4EE99DEB2EDAF3FD251041A0C1EB1BBBF571E51B5D630E1AF1` and
began with the PNG signature. Three other known local mGBA states had the same
container prefix. Validate a state by its recorded hash and an actual bounded
mGBA load; never reject it from PNG magic alone.

### GUI Lua injection can block after Run

The mGBA scripting Run invocation can remain blocked while Lua is already
executing. `inject_mgba_lua.ps1` delegates that click to a bounded helper,
polls the explicit ready file, and terminates only the helper after readiness.
Do not replace it with an unbounded synchronous UI Automation Invoke call.

### Port check must not connect (2026-08-26)

The original `Test-GdbPortInUse` used `TcpClient.BeginConnect/EndConnect` to
probe port 2345. This completes a TCP handshake and consumes mGBA's single GDB
slot. The replacement queries `[System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners()`, no connection, no binding. The launcher fails closed if a listener exists; it waits for the port to appear using the same non-connecting query. A regression test (`tools/runtime/test_launcher_no_tcpclient.ps1`) forbids `TcpClient`, `BeginConnect`, `EndConnect`, `TcpListener`, and `GetStream().Close()` in the launcher.

### P-004/P-005 wolf HP claims retracted (2026-08-27)

The former claims that `wolf_obj+0x04` was HP and that `0x080101C6` was a
damage writer are retracted. Across 2,060 runtime samples from three captures,
the field matched this spatial invariant without exception:

```text
u32(target+0x04) == floor(u32(target+0x1A4) / 256) + 4
```

Static code at `0x080101A6..0x080101C6` independently shows the integer world-Y
calculation and its store to `target+0x04`. The observed `228 -> 227` changes
were therefore position updates, not damage. The still-earlier `0x0800ABA8`
claim is also invalid: that address lies inside the encoding of the Thumb `BL`
starting at `0x0800ABA6`; it is not a standalone `STRH` instruction.

P-006A superseded only the final sentence above: authoritative signed current
HP is target `+0x28C`, incoming damage is record `+0x18`, and the writer is
`0x0800FA50`. The retractions of `+0x04`, `0x080101C6`, and `0x0800ABA8`
remain in force.

### RSP replies are a stream, not one `recv`

Replies may contain leading acknowledgements/noise, multiple frames, partial
frames, oversized memory responses, or short memory responses. The tracked
client anchors on `$`, verifies the checksum, preserves buffered trailing
frames, reads memory in at most 192-byte chunks, truncates oversized replies,
and advances by the actual byte count after a short reply.

### Runtime object addresses expire at reload

The old `r1 = 0x0203D504` value belongs only to its observed load epoch. The
tracked capture dumps the configured register at each event. Do not promote
that historical absolute EWRAM address to a permanent object identity or
hard-code it into a new experiment.

### Too many watchpoints destroy gameplay timing

Past broad GDB watchpoint sets reduced execution below useful gameplay speed.
Begin with one narrow event breakpoint. Add a write watchpoint only after the
object is dynamically rediscovered for the current load and only when the
ticket requires writer provenance.

## Validation before relying on a new run

1. Run the launcher's `-DryRun`; preserve its reported ROM/state hashes.
2. Run `pytest -q tests/unit/test_mgba_capture.py`.
3. Start the bounded capture and wait for `capture-ready.txt` before asking the
   human to act.
4. Confirm the observed PC matches the requested event and the dump pointer is
   valid for that stop. Numeric shape alone is not semantic evidence.
5. Record the run directory, input hashes, exact stop count, and any limitations
   in the active ticket evidence. Do not commit the run directory.
6. Confirm the launcher completed its post-run ROM identity check.

If a capture fails, preserve the exact phase that failed, identity, port,
launch, Lua injection, Lua armed marker, breakpoint acceptance, event wait, or
evidence grading. Do not restart by writing a new controller.
