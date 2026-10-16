# tools/runtime

Runtime evidence tooling for the Webfoot SDK: everything that drives mGBA,
observes the running Buu's Fury engine, or turns a capture into a report.

Authoritative documents, not duplicated here:

- `docs/runtime-capture.md`: the canonical capture pipeline, its ordering, and
  the hard tooling rules (reuse the tracked launcher, never write `.lua`/`.ps1`
  through a bash heredoc, a human play session launcher must start mGBA and
  exit, verify the emulator by `VersionInfo.FileVersion`, a silent instrument is
  not negative evidence).

## Do not rename anything in this directory

The historical research prefixes (`p003_`, `p006c_`, `rom009_`, `toolkit031_`,
...) are provenance links. Research documents under `docs/` cite these filenames
as the evidence that backs a measured claim, and `inject_mgba_lua.ps1`
allowlists many of them by exact path. Renaming a file breaks the citation and
the allowlist at once. Add new files; never tidy old names.

## How to read the tables

Every entry is marked with one of two classes:

- **Reusable**: infrastructure you can run today against the current tree.
- **Historical**: an evidence probe written for one ticket, one savestate, and
  one measurement. It documents what a past session measured. Treat it as a
  record and as a worked example, not as a tool with a current contract; most
  need a specific savestate and specific memory conditions to say anything.

### Capture and launcher infrastructure (Reusable)

| File | Purpose |
| --- | --- |
| `run_mgba_capture.ps1` | Tracked launcher: identity checks, isolated GDB-halted launch, optional Lua injection, capture invocation, cleanup, post-run ROM verification. |
| `capture_mgba_event.py` | Bounded, object-attributed breakpoint event loop; owns the GDB connection and writes the evidence files. |
| `mgba_capture.py` | Read-only GDB/RSP primitives: response framing, chunked reads, write-packet allowlist, versioned dump records. |
| `mgba_identity.py` | Fail-closed emulator identity for the Python GDB probes: one pinned build label and executable SHA-256, checked before any process is launched. Also carries `LAUNCH_SITES`: the registry of every repository-controlled place an mGBA process can start, each with one frozen classification, the `proof` mechanism that gates it, and a written rationale. |
| `inject_mgba_lua.ps1` | PID-scoped Lua injection through the mGBA Scripting window, allowlisted per script, via a bounded helper so a Run-button deadlock cannot strand the caller. |
| `invoke_mgba_run.ps1` | The bounded helper process that clicks Run; separated because mGBA's synchronous handler can block Invoke from returning. |
| `load_mgba_lua.ps1` | Verify the ROM and the mGBA build identity, launch mGBA, delegate Lua injection to `inject_mgba_lua.ps1`, and confirm the named ROM-006 state appeared with the ROM unchanged. |
| `start_toolkit031_session.ps1` | Start an instrumented play session and return, leaving mGBA running for the human operator. |
| `finish_toolkit031_session.ps1` | Companion close-out: verify the ROM was not modified and summarise the session's evidence. |
| `run_toolkit031_watch.ps1` | Single-process free-running observation run, for the Lua scripted-breakpoint path that a GDB-halted core cannot serve. |
| `stage_toolkit034_trial.ps1` | Stage one TOOLKIT-034 trial and return, leaving mGBA running for play. |
| `test_launcher_no_tcpclient.ps1` | Regression test: `run_mgba_capture.ps1` must never use TcpClient/BeginConnect/EndConnect, which steal mGBA's single GDB slot. |
| `__init__.py` | Package marker so the Python probes import as `tools.runtime.*`. |

### Deterministic bootstrap scripts (Reusable)

| File | Purpose |
| --- | --- |
| `rom006_bootstrap.lua` | Deterministic reset-to-savestate bootstrap: timed A pulses, then saves `build/rom006/bootstrap.mss`. |
| `rom006_bootstrap_map4.lua` | Same bootstrap extended with two more pulse windows for the second selector-1 sample (`bootstrap-map4.mss`). |

### Map and object research (Historical)

| File | Purpose |
| --- | --- |
| `rom006_gdb_probe.py` | Read-only ROM-006 GDB probe comparing observed `r0` against the profile-scoped first-word census. |
| `rom007_factory_probe.py` | Bounded read-only probe of one map-object factory, accepting private save artifacts without copying them into tracked paths. |
| `rom007_move_south.lua` | Scripted route leg: verifies the core identity, then drives movement south. |
| `rom008_object_trace.py` | Fail-closed identity helpers: an EWRAM address is never treated as a stable identity across registry, reset, or removal events. |
| `rom008_query_probe.py` | Bounded read-only probe of one exact object, discovered per run from its descriptor and factory return. |
| `rom009_callback_probe.py` | Bounded probe for dynamic exact-object callback attribution. |
| `rom009_object_trace.py` | Dynamic exact-object identity layer for the ROM-009 trace. |
| `rom009_clean_route.lua` | Scripted clean route used to reach the ROM-009 observation point. |
| `rom009_post_transition_route.lua` | Route continuation after the map transition. |
| `rom010_probe_status.py` | Stable fail-closed outcome taxonomy for runtime orchestration. |
| `rom011_live_watch.py` | Human-assisted exact-object read-watch support. |
| `rom011_dev_range.lua` | Configurable dev-range watch driven by a `rom011_dev` config table. |
| `rom011_human_ready.lua` | Three-line identity assert used to confirm a human session is on the right core and ROM. |
| `rom011_idle_benchmark.lua` | Idle frame benchmark: counts to frame 180 and reports through the marker file. |
| `rom011_stop_setup.lua` | Cancels the active clean-route driver so the human can take over input. |
| `rom012_live_containment.py` | Human-assisted exact-family containment and callback capture. |

### Combat research (Historical)

| File | Purpose |
| --- | --- |
| `p002_walk_probe.lua` | Walking displacement: samples player position and the buffered input halfword every gameplay frame. |
| `p003_attack_scout.lua` | Attack scout: buffered input, player position, spatial-registry counts, one condition per launch. |
| `p003_move_attack.lua` | Walks away from the NPC, then presses the candidate attack button, with a screenshot at attack+12. |
| `p003_punch_timing.lua` | Tap versus held A, with an OAM differential. |
| `p003_mash.lua` | Mash-A contact discovery: isolates the first accepted press. |
| `p003_hit_dump.lua` | Before/after EWRAM dumps plus a per-tick trace around a hit. |
| `p003_armed_punch.lua` | Armed single punch: primes while GDB-halted, presses A on the first frames after continue. |
| `p003_armed_mash.lua` | Armed mash variant with per-tick entity-zone diff and combat fields. |
| `p003_armed_one.lua` | Armed one-press or control run, selected by the marker filename. |
| `p003_human_play.lua` | Arms while GDB-halted then never touches input; logs player and field state per tick. |
| `p003_zdump.lua` | Single armed punch with a full per-tick dump of the entity zone. |
| `p004_hit_trace.lua` | Double punch with a per-tick enemy-struct window diff. |
| `p004_wander.lua` | No input; three EWRAM snapshots to locate the enemy's moving position words. |
| `p004_kihit.lua` | Ki-blast hit catch: full-EWRAM snapshots around the hit plus an HP-candidate trace. |
| `p004_watcher.lua` | Armed watcher for a state that loads with a ki blast already in flight. |
| `p004_aggro.lua` | Aggro driver: B-taps fire ki blasts, no directional input needed from this state. |
| `p004_fine.lua` | Per-tick fine capture of the wolf controller neighborhood. |
| `p004_full_label.lua` | Labeled punches with an EWRAM plus IWRAM diff around each one. |
| `p004_punch_label.lua` | Numbers the A rising edges of a human session and logs the zone diff. |
| `p004_human_watch.lua` | Human session: per-tick diff outside the sprite zone, plus HP and position. |
| `p004_actor_focus.lua` | Full-object temporal dumps of dynamically captured HURT-path actor pointers with punch edge labels. |
| `p004_actor_enum.lua` | Walks the engine's global actor list and identifies wolves by combat-object presence. |
| `p006_ewram_hp_scan.lua` | Snapshots full EWRAM before and after a ki-blast hit and reports every value that fell by the observed damage. |
| `p006_hit_bracket_scan.lua` | Rolling full-EWRAM snapshot preserving the frames before, at, and after the target event marker. |
| `p006_reaction_trace.lua` | Per-frame reaction trace; rediscovers the moving HURT-path target every load epoch instead of reusing an address. |
| `p006c_anchor_trace.lua` | Shared-tick observer for accepted-attack and post-HURT anchors. |
| `p006c_ctrl_probe.lua` | Locates the behavior-controller structures on player and wolf separately rather than assuming a shared offset. |
| `p006c_ctrl_stack.lua` | Controller-stack observer for the same two anchors. |
| `p006c_pool_probe.lua` | Attack-object pool probe. |
| `p006c_punch_field_probe.lua` | Punch-field probe. |
| `p006c_scan_timing_probe.lua` | Capability probe: how long a full EWRAM dispatch scan takes from the Scripting prompt, and how many matches it finds. |
| `p006c_dev_breakpoint_probe.lua` | mGBA 0.11 capability probe: confirms a scripted breakpoint callback resumes emulation and exposes live registers. |
| `p007_wolf_ai_trace.lua` | Wolf AI state observer. |
| `p008_clip_sequence.lua` | Normal-melee clip-sequence observer. |
| `p008_contact_trace.lua` | Melee contact observer for per-variant damage equivalence; the human drives. |
| `p008_mash_driver.lua` | Scripted melee driver for the same equivalence question. This one WRITES INPUT, which is why it is a separate file from the observer. |
| `p009_crit_report.py` | Decodes a P-009 damage-apply capture into per-hit critical evidence (caller LR, the special-damage-number boolean). |
| `p010_death_timeline.lua` | Enemy death and reward timeline observer. |
| `p011_wolf_speed_probe.lua` | Wolf pursuit probe: movement rate and pathing, per selector. |
| `p012_rng_probe.lua` | RNG source verification for the wolf pursuit pause. |
| `p013_knockback_probe.lua` | Knockback measurement: how far a landed hit displaces the victim. |
| `p015_bodyrect_probe.lua` | Body-rect recovery: the actual collision rectangles, per direction. |
| `p016_anchor_probe.lua` | Anchor recovery: what the actor world position at +0x1A0/+0x1A4 physically points at on the character. |

### Authored-content runtime proofs (Historical)

These observers answer whether the original engine really executes content the
SDK authored, which is the SDK's central claim.

| File | Purpose |
| --- | --- |
| `toolkit029_placement_watch.lua` | An SDK-authored map 10 placement is loaded and instantiated by the original engine. |
| `toolkit030_behavior_watch.lua` | A behavior the SDK attached to an authored placement is actually executed. |
| `toolkit031_api_probe.lua` | Capability probe for the scripted-breakpoint API and the identity asserts the execution observer depends on. |
| `toolkit031_execution_watch.lua` | Does the attached behavior execute, and what triggers it. |
| `toolkit032_authored_script_watch.lua` | Does the engine execute a script body the SDK authored, bytes that did not exist in canonical Buu's Fury. |
| `toolkit033_gameplay_effect_watch.lua` | Read-only observer proving four independent edges for one authored native effect. |
| `toolkit034_dispatch_caller_watch.lua` | Read-only causal trace for an authored death-trigger candidate: death callback, descriptor trampoline, and caller. |

### Retired tombstones (do not run, do not delete)

Each is a single failing statement naming why the helper was withdrawn:
`error(...)` in a Lua tombstone, `throw` in a PowerShell one. They
stay tracked so a research document citing the filename still resolves, and so
nobody reintroduces the same unsafe helper.

| File | Retired because |
| --- | --- |
| `p006_armed_punch.lua` | Hardcoded EWRAM and false HP semantics. |
| `p006_auto_punch.lua` | Hardcoded load-specific EWRAM addresses. |
| `p006_load_and_scan.lua` | Direct Lua state loading bypasses provenance and identity checks; use `run_mgba_capture.ps1` with `-StatePath`/`-LuaPath`. |
| `p006_load_slot1.lua` | Not part of the tracked capture pipeline. |
| `p006_save_state.lua` | Wrote a state beside the read-only source state. |
| `toolkit031_load_state.ps1` | A second mGBA Scripting-window driver beside `inject_mgba_lua.ps1`. Load a state through `start_toolkit031_session.ps1`, which asks `Start-MgbaSession -StatePath` for the inject-then-load order. |
