# ROM-010 runtime probe reliability

Removing the runtime-launch blocker that stopped the clean-state callback trace,
then re-running the exact-object experiment against a reliably usable probe.

## Objective

Remove the environment/runtime-launch blocker that prevented ROM-009 from executing its clean-gameplay experiment.

Once the runtime harness is reliably usable, immediately re-run the existing ROM-009 exact-object experiment.

This is NOT a new reverse-engineering direction.

The research question remains:

Does a dialogue-free gameplay state allow a factory `0x08007675` object to reach its exact AABB/callback path?

---

## Context

ROM-009 completed with:

- Result: D - ENVIRONMENT BLOCKED
- Dialogue hypothesis: UNRESOLVED
- Parser readiness: NO
- Evidence level: Level 3
- Portable tests: 208 passed
- `git diff --check`: clean
- ROM/save/state hashes unchanged
- no proprietary artifacts tracked or staged
- independent review completed

ROM-009 did NOT obtain new behavioral evidence because the required runtime experiment could not execute.

Do not reinterpret environment failure as negative ROM evidence.

---

## Baseline

ROM-009 changes are currently uncommitted.

At the start of ROM-010:

1. inspect the actual ROM-009 diff
2. run the 208-test portable suite
3. verify ROM/save/state hashes
4. commit legitimate ROM-009 work as the new baseline
5. update `docs/PROJECT_<local-state-name>` accordingly
6. begin ROM-010 from a clean tree

Use an appropriate commit message such as:

`feat: prepare clean-state spatial callback tracing`

Do not blindly stage files by expected name.

No proprietary/runtime artifacts may enter the commit.

---

## Primary Problem

The current mGBA/GDB/Lua launch sequencing depends on an execution path that the environment could not complete reliably.

Determine the exact failure boundary.

Classify it as one of:

- emulator launch blocked
- GUI approval blocked
- debugger attachment blocked
- Lua injection/loading blocked
- process discovery blocked
- save-state loading blocked
- launch-condition timing or race
- another precisely demonstrated cause

Do not merely report "environment blocked" again.

Identify the narrowest concrete boundary.

---

## Phase 1: audit the existing runtime harness

Inspect existing runtime tooling from ROM-006 through ROM-009.

Map the actual pipeline:

working save/state
→ mGBA launch/reuse
→ Lua initialization if applicable
→ GDB server availability
→ probe attachment
→ breakpoint installation
→ deterministic input
→ event capture

For every stage record:

- command/process involved
- whether GUI interaction is required
- whether an existing process can be reused
- whether success can be machine-detected
- current failure mode

Prefer adapting existing infrastructure over adding a second competing harness.

---

## Phase 2: minimize GUI dependency

Make the smallest robust change that lets the operator perform the experiment without repeated GUI approval attempts.

Preferred approaches, in order:

1. reuse an already-running compatible mGBA instance when safe
2. launch mGBA once and perform multiple debugger operations against that process
3. use supported CLI/debugger/startup facilities that avoid manual GUI interaction
4. create a deterministic user-assisted launch boundary only if unavoidable

Do NOT:

- patch the ROM
- inject ROM hooks
- modify commercial ROM data
- build a custom emulator
- replace mGBA
- create a giant generic automation framework

If a manual launch is impossible in the current environment, make the manual boundary extremely small and explicit.

Example acceptable outcome:

> User launches one prepared command/state once; the probe then attaches and completes unattended.

But prefer zero manual interaction if supported.

---

## Phase 3: harden the probe state machine

The runtime launcher/probe must fail closed.

It should detect and clearly distinguish:

- mGBA absent
- wrong mGBA process
- debugger unavailable
- wrong ROM
- wrong runtime state
- connection timeout
- breakpoint installation failure
- state load failure
- probe success
- probe research failure

Do not collapse all failures into "environment blocked."

Use bounded timeouts.

Do not repeatedly relaunch GUI processes in an uncontrolled loop.

---

## Phase 4: re-run the exact-object experiment

As soon as the runtime path is working, STOP infrastructure expansion.

Use the NEW dialogue-free runtime state already documented in `PROJECT_<local-state-name>`.

Re-run the existing clean-state experiment.

Required sequence:

1. verify normal free gameplay
2. derive active MapEntry from runtime
3. validate static/runtime selected-value agreement
4. capture a suitable factory `0x08007675` invocation
5. capture dynamic returned object X
6. verify registry insertion and load epoch
7. observe exact-object AABB processing
8. use only bounded deterministic movement
9. optionally transition SOUTH once
10. if new map creates X2, retire X and track X2 separately
11. stop on exact-object callback

Object identity rules from prior records remain mandatory.

Object Y is never evidence for object X.

Do not hard-code historical EWRAM addresses.

---

## If Exact Callback Is Reached

Capture:

- active MapEntry
- descriptor
- factory
- dynamic object
- registry slot/load epoch
- AABB bounds/query/result
- callback raw target
- normalized Thumb/ARM fetch address
- arguments
- return value
- immediate downstream consequence

Trace only far enough to classify the immediate role.

Possible classifications remain:

- collision region
- transition region
- activation/event region
- interaction region
- generic spatial predicate
- generic rectangle-aware object

Do not force a stronger label.

Promote to Level 4 only if meaningful runtime subsystem behavior is actually established.

---

## If Exact AABB Is Reached but Callback Is Filtered

Record the exact filtering condition and stop.

Do not wander around the game looking for a different trigger.

---

## If Target Still Never Reaches AABB Under Clean Gameplay

Only after the runtime environment is confirmed functional:

perform the bounded guard trace already identified around:

- `0x080126D4`
- `0x080127AE`
- `0x08012846`
- callback region `0x08012784`

Identify the FIRST guard rejecting the exact target object.

Then stop.

---

## Dialogue Hypothesis

ROM-010 must finally classify:

- SUPPORTED
- NOT SUPPORTED
- UNRESOLVED

Compare the earlier dialogue-contaminated/suspected state with the new clean state only using actual runtime evidence.

Do not infer causality from save descriptions alone.

---

## Parser Readiness

Re-evaluate independently of gameplay naming.

Answer YES only if the `0x08007675` source descriptor family is structurally understood well enough for a minimal read-only parser:

- family discrimination
- sufficient descriptor boundary/extent
- field offsets and widths
- rectangle-producing fields
- callback/source field where established
- raw pointer treatment
- lossless preservation strategy

Otherwise NO and identify the single smallest blocker.

Do not implement the parser in ROM-010.

---

## Implementation Constraints

Prefer modifying/extending existing runtime tooling.

Do not build a generic debugger framework.

All local runtime artifacts remain beneath ignored `build/rom010/` or existing ignored runtime locations.

Portable tests must not require private ROM/save/state files.

Add synthetic tests for any new launch-sequencing logic.

At minimum cover:

- process/connection failure classification
- timeout behavior
- successful attach state
- wrong target rejection
- stale object rejection
- exact callback success
- infrastructure success vs research failure distinction

---

## Validation

Before changes:

- expected portable suite: 208 passed

After changes:

- all portable tests pass
- prior ROM-002 through ROM-009 regressions remain valid
- `git diff --check` passes
- ROM hash unchanged
- original save/state hashes unchanged
- no proprietary files staged/tracked

Report private runtime replay separately from portable pytest.

---

## Result classifications

ROM-010 should end in one of:

### A - EXACT CALLBACK CAPTURED

Runtime environment fixed and exact target callback observed.

### B - EXACT AABB REACHED, CALLBACK FILTER IDENTIFIED

Runtime environment fixed; exact target reached spatial processing but was filtered later.

### C - FIRST ENTRY GUARD IDENTIFIED

Runtime environment fixed; clean-state target still skipped and exact rejecting guard identified.

### D - PRECISE EXTERNAL BLOCKER

Only acceptable if execution remains genuinely impossible.

Unlike ROM-009, D must identify the exact external boundary and the smallest user/manual action or environment change required to unblock it.

Do not simply repeat "environment blocked."

---
