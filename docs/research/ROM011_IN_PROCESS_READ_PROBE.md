# ROM-011 in-process mGBA read-range probe

Replacing the slow GDB watchpoint approach with an in-process mGBA read-range probe,
to capture the first runtime read of the dynamic object's fields.

## Question

Finish the existing ROM-011 human-assisted experiment by replacing the unusably slow GDB watchpoint approach with a lightweight IN-PROCESS mGBA read-range probe.

Do not change the reverse-engineering question.

We still need:

first runtime READ of dynamic object X within:

X + 0x04 through X + 0x0F

or:

X + 0x14 through X + 0x17

The capture must include:

- exact accessed address
- object-relative offset
- access width
- PC
- LR
- CPU registers needed for attribution
- current X identity/load epoch
- user gameplay annotation where applicable

The game must remain normally playable.

---

## Context

ROM-011 attempted GDB-based dynamic object observation.

The target requirement is:

capture the first runtime read of exact live object X at:

+0x04..+0x0F
+0x14..+0x17

while the user controls the game normally.

Stock mGBA 0.10.5 GDB watchpoints are not suitable.

Observed behavior:

- mGBA ignores the requested GDB watchpoint length for this use
- coverage becomes approximately sixteen individual watched addresses
- the debugger memory path scans watchpoints for every emulated memory access
- performance falls below 1 FPS
- even a reduced breakpoint/watchpoint set failed the ROM-011 speed gate

Existing evidence/tooling records this around:

tools/runtime/rom011_live_watch.py

approximately line 1248; inspect the actual current file rather than relying on the line number.

Therefore:

GDB watchpoints are rejected for the final ROM-011 human-play experiment.

The required replacement is:

a lightweight in-process read-range callback/probe

that:

- dynamically arms only after X is established
- watches only the required X-relative ranges
- records the FIRST valid read
- immediately disables itself
- has negligible gameplay overhead
- keeps gameplay near normal speed
- does not depend on Windows UI automation to load instrumentation

---

## Important Architecture Decision

Do NOT patch the game ROM.

Instead build a separate instrumented mGBA 0.10.5 executable.

Pin emulator source to the exact version already used by this project:

mGBA 0.10.5

known build/source commit:

26b7884bc25a5933960f3cdcd98bac1ae14d42e2

Do not switch to mGBA master or another emulator version merely because newer debugger APIs may exist.

Runtime evidence should remain comparable with ROM-006 through ROM-011.

The instrumented emulator is a research tool, not part of the final game.

---

## Baseline

ROM-011 is still the current research pass.

Do NOT commit ROM-011 merely because instrumentation strategy changed.

Inspect:

- git status
- git diff
- git diff --check
- current portable tests

Preserve all existing ROM-011 work.

The stock mGBA/GDB investigation remains useful negative evidence and should remain documented.

Do not discard it.

---

## Phase 1 - Audit Local mGBA Source/Build Availability

Determine whether the exact pinned mGBA source is already available locally.

Search existing project/upstream/tool directories before downloading anything.

If absent:

obtain a clean checkout of upstream mGBA pinned exactly to:

26b7884bc25a5933960f3cdcd98bac1ae14d42e2

Keep the upstream checkout outside tracked project source or beneath the repository's ignored external/build convention.

Do not vendor the full mGBA source into log1-remake.

Do not modify the user's installed stock mGBA executable.

The stock mGBA 0.10.5 must remain available as the control/reference emulator.

---

## Phase 2 - Create a Minimal Instrumentation Patch

Implement the smallest possible native probe in the pinned mGBA source.

Do NOT modify the generic GDB watchpoint implementation to add more watchpoints.

Do NOT route the read probe through the existing generic memory-debugger watchpoint list.

That is the performance problem we are avoiding.

Instead implement a dedicated fast path conceptually equivalent to:

if probe is armed:
    if read address overlaps target range:
        capture first event
        disarm probe

When probe is NOT armed, overhead must be effectively negligible.

When armed, the hot path should require only a very small number of comparisons.

No allocation.
No logging.
No debugger-list scan.
No formatting.
No socket activity.

on every ordinary memory read.

Actual event serialization should occur only after a valid first hit.

---

## Required Watched Ranges

After X is dynamically established:

Range A:

X + 0x04
through
X + 0x0F

inclusive

Range B:

X + 0x14
through
X + 0x17

inclusive

Handle multi-byte reads correctly.

For example:

a 32-bit read beginning at X + 0x02 that overlaps X + 0x04

is relevant only if executable/memory-access semantics make that overlapping read meaningful.

Define and test overlap semantics explicitly.

Do not silently reduce everything to byte reads.

Record the original access:

- start address
- width
- overlap
- object-relative offset

---

## Dynamic Arming Requirement

Do NOT hard-code an old EWRAM X address.

X must still be discovered dynamically for the current run.

Reuse the strongest existing ROM-010/011 identity chain.

At minimum validate:

- trusted ROM profile
- target factory raw 0x08007675
- target factory Thumb fetch 0x08007674
- descriptor/factory relationship
- factory return object
- registry insertion
- current load epoch

Only after exact X is established may the native range probe arm.

If the current architecture makes it cleaner to arm from Python/GDB AFTER X discovery, that is acceptable provided the expensive GDB watchpoints are not used for memory-read monitoring.

Alternative:

implement minimal native recognition of the established factory/insertion PCs and arm internally.

Choose whichever produces the smallest trustworthy system.

Do not broaden this into a generic dynamic instrumentation framework.

---

## Preferred Control Architecture

Prefer a small native probe API controlled externally.

A good architecture may look like:

existing runtime probe
    ->
discover X
    ->
send ARM command to instrumented mGBA
    ->
native mGBA stores X/ranges
    ->
human gameplay resumes
    ->
CPU performs first matching READ
    ->
native probe captures event
    ->
probe immediately disables
    ->
event becomes available to Python/the operator

The control mechanism may be:

- debugger command
- lightweight localhost socket
- named pipe
- tiny control file polled outside the hot memory path
- another minimal mechanism

Choose based on the existing mGBA architecture and least complexity.

The control channel must NOT be consulted on every memory access.

---

## Preferred Even Simpler Architecture

If the pinned mGBA source makes this cleaner, the instrumented executable may itself recognize the already-established target lifecycle.

For example:

known factory/insertion execution point
    ->
validate target
    ->
capture X
    ->
arm native range probe

This avoids needing GDB for arming.

However:

do not duplicate large amounts of Webfoot/runtime validation logic inside mGBA.

Keep the mGBA patch narrowly observational.

---

## First-Hit Event

The native probe must record the FIRST qualifying CPU READ only.

Required event fields:

- target X
- load epoch or externally supplied identity token
- read address
- X-relative offset
- access width
- PC
- LR
- CPSR / execution state
- r0-r15 if inexpensive at hit time, otherwise the subset needed for exact attribution
- descriptor if already supplied
- factory identity if already supplied
- monotonically unique hit/event ID

Immediately after capture:

DISARM.

No second read may overwrite the first event.

The emulator should continue safely or pause in a controlled way.

Prefer preserving enough state that the operator can inspect the exact hit before gameplay continues.

---

## Human Feedback

When a hit occurs:

the operator should clearly tell the user:

PROBE HIT - STOP INPUT

Then collect the user's short description of what they were doing.

Keep this separate:

HUMAN OBSERVATION

versus

EXECUTABLE EVIDENCE

The user's description is context, not binary proof.

---

## Performance Gate

This is a HARD requirement.

Before doing the human gameplay experiment, measure the instrumented emulator.

Compare:

1. stock mGBA 0.10.5
2. instrumented mGBA with probe DISARMED
3. instrumented mGBA with probe ARMED

Use the same reproducible game state.

Do not require fake precision.

Acceptance target:

normal playable speed approximately 60 FPS

and no obvious severe input latency.

At minimum reject anything remotely comparable to the prior sub-1-FPS GDB watchpoint behavior.

Preferred quantitative requirement:

instrumented ARMED performance remains at least 90% of normal real-time throughput where measurement is stable.

If a normal 59-60 FPS display is maintained during ordinary gameplay, record that.

Do not optimize beyond what is required.

---

## Eliminate Windows UI Automation

The final probe workflow must NOT rely on the unreliable Windows scripting-menu/UI injector.

Do not require:

Tools
-> Scripting
-> Load Script

through automated mouse/keyboard interaction.

Preferred launch should be command-driven.

Possible final form:

PowerShell launcher
    ->
instrumented mGBA executable
    ->
ROM
    ->
working savestate
    ->
native probe/control path ready

Use existing mGBA command-line savestate loading where supported by the pinned build.

If script support is still useful for non-hot-path launch sequencing, load it without Windows UI automation.

Inspect the pinned source/build capabilities rather than assuming a --script option exists.

Do not switch emulator versions solely to obtain --script.

---

## Track the Instrumentation as a Patch

Do not commit a full modified mGBA source tree.

Prefer tracked project artifacts such as:

tools/mgba_probe/
or another appropriate location containing:

- source patch/diff against exact pinned mGBA commit
- build helper
- launcher/helper
- documentation
- probe protocol/schema if needed

Example conceptual artifacts:

tools/mgba_probe/mgba-0.10.5-log1-read-probe.patch
tools/mgba_probe/build.ps1
tools/mgba_probe/README.md

Choose names consistent with the repository.

The generated mGBA binary belongs under ignored build output.

Do not commit the executable unless repository policy explicitly allows it.

---

## Build Reproducibility

Record:

- upstream mGBA commit
- compiler
- CMake version
- frontend selected
- relevant build options
- output executable hash

Prefer a playable frontend requiring the least new dependency complexity.

If the normal Qt frontend can be built from the available environment without significant dependency work, it is acceptable.

If not, a playable SDL frontend is acceptable if it supports:

- normal keyboard/controller gameplay
- loading the ROM
- loading the working state
- the native probe

Do not spend the record installing a huge unrelated GUI toolchain merely to preserve Qt.

---

## Emulator Semantics Safety

The instrumentation must be observational.

Do not change:

- emulated CPU results
- memory values
- timing-sensitive game state intentionally
- ROM contents
- save contents
- game logic

The hot-path probe may observe:

- access address
- width
- CPU registers
- current PC
- target range

It must not alter the value returned by the memory read.

Add tests or assertions where practical that demonstrate the wrapped/instrumented read returns the exact underlying value unchanged.

---

## Tests

Expected current portable suite:

219 passed before new changes, unless repository state shows a later legitimate count.

Keep existing tests green.

Add project-side synthetic tests for:

- range overlap calculations
- dynamic X ranges
- one-shot capture
- immediate disarm
- wrong X ignored
- stale epoch ignored
- read width preserved
- first hit cannot be overwritten
- protocol/event parsing
- launcher command construction
- failure if wrong instrumented mGBA version/build is used

For the mGBA patch itself, add the smallest feasible upstream/local test for:

- disarmed probe does nothing
- armed nonmatching read does nothing
- matching read records once
- matching read returns original memory value
- second match after disarm is ignored

Do not use commercial ROM data as test fixtures.

---

## Phase 3 - Resume the Human-Assisted ROM-011 Experiment

Once the native probe passes the speed gate:

STOP emulator infrastructure work.

Resume the original experiment.

Sequence:

1. Launch instrumented pinned mGBA without UI automation.
2. Load an ignored working copy of the clean state.
3. Establish exact dynamic target X.
4. Validate registry insertion/load epoch.
5. Arm native ranges:
   X+04..X+0F
   X+14..X+17
6. Confirm normal playable speed.
7. Tell the user:
   instrumentation is armed; take control.
8. User performs bounded natural gameplay.
9. On FIRST read hit:
   capture event
   disarm
   tell user to stop input
10. Record user's action.
11. Attempt one deterministic reproduction if practical.
12. Identify the actual consumer PC/function.
13. Trace only immediate behavior.
14. STOP.

One south map transition maximum remains the gameplay scope.

---

## If X Is Destroyed Before Hit

Retire the old X.

If a new target-family object X2 is created:

- establish new load epoch
- arm X2 ranges
- continue the bounded human session

Do not watch freed/stale addresses.

---

## If No Read Occurs

Only RESULT E is valid if:

- native instrumentation passed the performance gate
- target X was valid
- ranges were armed correctly
- human gameplay remained bounded
- one south transition maximum completed
- no matching reads occurred

That would be substantially stronger than the prior GDB no-hit result because observation would no longer suppress gameplay.

Do not call the object unused/passive without further evidence.

---

## Valid Final Runtime Results

A - HUMAN-TRIGGERED READ CAPTURED

B - HUMAN-TRIGGERED CALLBACK/CONSUMER CAPTURED

C - IDLE/NORMAL PROCESSING READ CAPTURED

D - X TRANSFORMED/REPLACED BEFORE DIRECT READ

E - PLAYABLE NATIVE PROBE OBSERVED NO X READ

F - NATIVE PROBE COULD NOT MEET PERFORMANCE/CORRECTNESS REQUIREMENTS

F is acceptable only with a precise implementation blocker.

"Environment blocked" is no longer sufficient.

---

## Dialogue Hypothesis

Remain:

UNRESOLVED

unless the actual captured consumer provides direct evidence involving dialogue/game-mode gating.

---

## Parser Readiness

Do not implement a parser.

Re-evaluate YES/NO only after the runtime result.

Structural evidence and gameplay semantics remain separate questions.

---

## Documentation

Update existing ROM-011 documentation with:

### GDB Instrumentation Failure

Record why stock mGBA 0.10.5 GDB watchpoints failed the playability requirement.

### Native Probe Architecture

Record:

- pinned emulator version
- patched source locations
- probe range semantics
- arming
- first-hit behavior
- event transport
- performance measurements

### Runtime Result

Record first exact X read if captured.

Do not conflate emulator-tool evidence with ROM semantics.

---
