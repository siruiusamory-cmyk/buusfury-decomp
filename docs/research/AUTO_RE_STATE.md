# Reverse-Engineering Research Ledger

Durable record of the Webfoot reverse-engineering research program. Read this
file first when picking up static or runtime research. Keep it compact;
detailed evidence lives in `docs/reverse-engineering.md`,
`docs/consumer-analysis.md`, and `docs/research/SUBSYSTEM_MAP.md`.

Rules of the lane: static-first, bounded units, evidence labels
`CONFIRMED` / `INFERRED` / `UNKNOWN`, runtime levels 0-4, never modify the
canonical ROM or user saves/states, narrow commits only, never commit
proprietary artifacts.

## Priority Steering (2026-08-23, user)

1. Finish the transition thread cleanly (AUTO-012 first). The causal target:
   WHY did VERTICAL-001 still transition after MapEntry 39's only
   descriptor-owned doorway rectangle was emptied? Strongest remaining
   candidate chain: non-descriptor registry population -> append site
   `candidate_registry_writer_08009172` -> caller path `0x080026FC`. Answer:
   what object is appended, where its bounds originate, whether it exists on
   MapEntry 39, whether it accepts the doorway query, what action it
   dispatches, and whether it reaches `downstream_080075AC`. If explained,
   mark VERTICAL-001 C RESOLVED with the full chain; do NOT enumerate every
   remaining transition subtype. If not explained after bounded work,
   document why and move on.
2. One concise transition-pipeline synthesis in SUBSYSTEM_MAP.md
   (CONFIRMED / STRONGLY SUPPORTED / INFERRED / UNKNOWN separated). Close the
   frontier; do not keep polishing it.
3. Then PIVOT HARD to player/combat as top priority: player entity ->
   update root -> minimum runtime structure (position/velocity/facing/
   animation/HP/ki/attack state/i-frames) -> input->movement rules with
   numbers -> melee initiation/state progression (startup/active/recovery)
   -> one complete damage event (hit detection -> damage calc -> HP mutation
   -> reaction/knockback/i-frames -> death) -> one simple enemy's update loop.
4. Produce BEHAVIORAL SPECIFICATIONS, not field lists (with evidence labels;
   no invented semantics).
5. Use LoG1/LoGII material as differential evidence (manual structural
   comparison; RELATED_IMPLEMENTATION_CANDIDATE until validated).
6. Recover usable gameplay constants: value / unit-representation / where
   used / evidence / game-version.
7. At synthesis passes: audit older claims against new evidence; record
   OLD CLAIM / NEW EVIDENCE / RESOLUTION; archive stays historical.
8. Stay discovery-dominated; synthesis must be cheaper than the units it
   summarizes. Prefer subsystem roots, closed causal chains, state machines,
   formulas/timings, eliminated hypotheses; ignore anonymous leaves.
9. Next-major-checkpoint report must attempt: player update location,
   movement computation, melee initiation, hit->HP-loss chain, knockback,
   enemy update location, recovered constants, LoGII-vs-Buu deltas.

## Current Objective

P-004 RETRY READY (2026-08-25, evening). Run-1 postmortem and fixes, all
validated automatically end-to-end through real mGBA:
- RSP reader rewritten ($-anchored, checksum-verified, acks sent,
  192-byte chunked reads with truncate-tolerant oversize handling).
  mGBA's stub intermittently pads/repeats frames around breakpoint
  stops (e.g. 100-byte replies to 64-byte requests); run-1 lost all
  object dumps to this. Wire-log evidence captured.
- Lua horizon 14400 -> 108000 (run-1 probe expired during pre-play
  idle; zero PUNCH/TRACK/OBJ rows).
- Pointer publish narrowed to r1 only (the confirmed actor argument);
  run-1 published 34 junk candidates that filled the 4-track cap
  before the wolf object appeared.
- Stale STOP-NOW.txt from a prior session silently finished probes;
  driver already clears it - manual launches now verified clean too.
- Autonomous validation: ki-blast aggro via `p004_aggro.lua` (B-taps;
  player already faces wolves) produced 8 live player-side HURT stops;
  27 exact-size dump records; ptr publish -> TRACK -> SEED -> 1108 OBJ
  diff lines + 19 FULL snapshots on the Lua side. Canonical ROM hash
  re-verified after all experiments.

Run-1 salvage (60 HURT entries, valid registers/stacks even though
dumps were empty): r1 cleanly splits actors (wolf 0x203d504 x27,
player 0x203dbb0 x33); chains re-confirm the canonical P-003 path
(m1 continuation 0x80342eb -> 0x8018907 -> flinch wrapper) and the
indexed-dispatcher path (0x800aa5f family). Wolf combat object first
0x180 bytes showed NO word changes at any HURT instant - HP is NOT in
that window; per-tick dumps from the retry are required.

Next human run protocol unchanged: punch #1 deliberately (identity
capture), then ~3 landed punches spaced 2-3 s, no transitions, then
ordinal HIT/MISS labels. After data lands: automated candidate
grading -> writer provenance -> P-004 closure.

P-003/P-004 contact resolution background. Human-provided combat state validated
(sha256 `d8d8578d081e6bc4e535160b52fa0182cf2619ae70c93f63f5401b1d1624dcf1`,
79,767 bytes, mtime 2026-08-23 16:10:07; working copies only under ignored
build/research/p003-exp/). Damage-candidate fields identified but hit
connection is intermittent (enemy AI wanders). Next:
1. Pure-control trace leg (no punches, ~300 ticks): do `0x0203DBB4/
   0x0203DC20` drift without punches? Distinguishes enemy-HP-pair vs
   player-side pair.
2. Locate the enemy entity struct/position (enemy wanders; per-tick diff
   of candidate regions during a no-input leg should expose moving position
   words).
3. Punch leg timed when enemy is within range (read enemy pos per tick,
   punch when close) for a RELIABLE hit with per-tick HP/knockback capture.
1. RESOLVED by runtime: A/0x0001 is the contextual action (dialogue near
   NPC, punch in open field); resolver function still UNKNOWN (deprioritized).
2. RESOLVED: human-provided combat state received and validated (see above).
3. Punch tile-staging timeline established; see P-003 progress 3.

## Research Queue

| ID | Subsystem | Question | Why useful | Known evidence | Suggested next method | Status |
|---|---|---|---|---|---|---|
| AUTO-001 | spatial-descriptors | What descriptors exist in the count-2 array at `0x08294960`, and does a sibling cover the ROM-012 doorway? | Directly targets the recorded smallest blocker of VERTICAL-001 C; extends descriptor format knowledge | Array base/count from ROM-007 runtime (`field_40_raw=2`, `field_44_raw=0x08294960`); descriptor `0x08294948` fully characterized | Read-only byte reads at file offsets `0x00294960..68` + both descriptors; decode factory/bounds fields; cross-check with `webfoot variation-arrays find-first-word` | RESOLVED |
| AUTO-002 | spatial-registry-callers | Which containing functions call point-query entries (`0x08006E4E -> 0x080126D4`, `0x08021DFE/08021E06 -> 0x080126D4`, `0x08012AEC -> 0x080127AE`, `0x08022142 -> 0x08012846`)? | Names the scheduler layer that decides when spatial queries run; open PROJECT_STATE unresolved question | Callsite instructions CONFIRMED by independent BL decode (ROM-008); Ghidra did not recover containing functions | Seed callsite instructions in calibrated Ghidra project; recover boundaries; decompile callers; conservative names | RESOLVED |
| AUTO-003 | transition-action | What does action `0x080125E8 -> downstream 0x080075AC` actually do (map reload? dialogue start?)? | Would explain transition mechanism and likely close VERTICAL-001 C mechanism question | Runtime: action executed and reached `0x080075AC`; trace hit `0x080077EC`, `0x08009744`, `0x080094B8`; no return within 512 steps | Ghidra: seed `0x080125E8`, `0x080075AC`, `0x080077EC`, `0x08009744`, `0x080094B8`; decompile; enumerate callees; look for MapEntry-load flow entry (`0x08008B30`) and registry reset (`0x08048488`) | RESOLVED |
| AUTO-004 | doorway-descriptor-census | Which candidate descriptors ROM-wide overlap the ROM-012 doorway, and which map owns them? | Identifies or eliminates descriptor-driven explanations for VERTICAL-001 C; builds global descriptor corpus | Factory raw words `0x08007675`/`0x080072CD`; half-open AABB semantics; per-map coordinate caveat | 4-aligned scan for factory words, decode bounds, reverse-reference ownership chain (descriptor <- pointer array <- selected value <- variation source <- MapEntry) | RESOLVED |
| AUTO-005 | object-vtables | What methods live in dispatch tables `0x0804A09C`, `0x0804A0AC`, `0x0804E444`? | Defines the rectangle-object class hierarchy; every spatial object routes through these | Cleanup slot raw/fetch `0x080510A1/080510A0`; filter vtable[2] `0x08007769`; receiver base `0x0804A0AC` vtable[1]/[2] used; AUTO-003 added vtable+0x34/+0x84/+0x28 uses | Ghidra data-word dump of each table; follow each raw target; classify per-slot semantics conservatively | READY |
| AUTO-005 | registry-manager | Complete function graph of registry manager around `0x03002A64` (`0x08012628`, `0x08012664`, `0x0801268A`, `0x080126D4`, `0x080127AE`, `0x08012846`, `0x08012900`, neighbors to `0x080128F2+`) | One coherent subsystem map for the best-understood engine area | Individual behaviors established in ROM-006/008/011/012 | Ghidra seeding + decompilation sweep over `0x08012600..0x08012A00` | READY |
| AUTO-006 | descriptor-format | What is the minimal extent/field map of a source descriptor such that parsing is lossless? | Recorded parser-readiness blocker across ROM-008..ROM-012 | Consumers read `+0x00` (factory), `+0x04` (callback producer), `+0x08/+0x0C` (bounds) | Static census of all descriptor accesses from all factories reached via variation arrays; adjacency analysis in ROM | READY |
| AUTO-010 | map-loader | Does `FUN_08008d44` resolve a MapEntry via `0x080089FC` from zone/area/variation bytes, and what are its argument/return contracts? | Completes the transition mechanism chain end-to-end; needed for any future map-warp tooling | AUTO-003: called by `downstream_080075AC` with `(ctx, byte, byte, ptr, byte, 1)`, returns new context | Ghidra: seed + decompile `0x08008d44`; check for `0x080089FC` call and literal use | RESOLVED |
| AUTO-011 | registry-population | Do MapEntry objects/npcs pointer-driven spawns add spatial registry members beyond the variation-array path? | Tests the remaining descriptor-free explanation for VERTICAL-001 C | ROM-007: registry construction is heterogeneous; objects/npcs pointers exist in MapEntry (+0x1C/+0x20) | Enumerate callers of `registry_populate_08012664`; census manager-global xrefs; classify write sites | RESOLVED (refined) |
| AUTO-012 | registry-population | Which load path drives second append site `candidate_registry_writer_08009172` via callsite `0x080026FC`, and what do the `FUN_0800d30e`/`FUN_08017f5a` manager writes do? | Completes the registry-mutation map; candidate VERTICAL-001 C mechanism | AUTO-011: append site appends vtable[0]-dispatch results from an 8-byte-stride record table; caller `0x080026FC` unrecovered | Ghidra: recover containing function of `0x080026FC` (backward seeding), decompile writers | RESOLVED (VERTICAL-001 C explained; FUN_0800d30e/FUN_08017f5a write classification deferred as low-value) |
| P-001 | player-entity | Which runtime entity is the player and where is its update root/dispatcher? | Root anchor for all player/combat research | ROM-012: query entity `0x0202E4D0` tracked human movement; `candidate_caller_08006E3C` frame handler queries at a tracked entity; map loader spawns via 0x18-stride table + `FUN_080109aa/080104f2` | Static: decompile loader spawn path (`FUN_0801713c`, `FUN_080109aa`) to find the player-class factory + its update dispatch entry; then find per-frame update root | RESOLVED |
| P-002 | player-movement | How does directional input become movement (speed, normalization, facing, inhibition)? | Core behavioral spec for remake | Runtime displacement experiment (see Recent Discoveries) completed the spec | RESOLVED via experiment; static input-consumer function remains a future structural question | RESOLVED |
| P-003 | melee | Where does basic melee begin and what is its state progression (startup/active/recovery/hitbox query)? | Core combat spec | none yet | From player update root, follow attack-button branch to melee state machine | BLOCKED by P-001 |
| P-004 | damage | One complete damage event: hit detection -> damage calc -> HP mutation -> reaction/knockback/i-frames -> death | Closes the combat loop end-to-end | P-006A confirmed HP `+0x28C`, damage record `+0x18`, and writer `0x0800FA50`; full event chain remains incomplete | Resume only from the corrected anchor | PARTIAL / BLOCKED |
| P-005 | damage | Physical Damage Semantics and Wolf Hit Reaction | One normal player melee hit through damage and reaction timing | Former timing evidence used a positional field; P-006A corrected the damage anchor | Repeat semantics from writer `0x0800FA50` | PARTIAL / READY |
| P-006 | melee-reaction | Measure hit reaction, knockback, recovery, and re-hit eligibility from a confirmed damage event | Core combat reaction spec | P-006B confirmed HURT-to-damage, HURT exit timing, and authoritative writer intervals | Resolve accepted attack start/gating and exact state/AI-resume boundaries; do not begin P-007 | PARTIAL / TIMING BLOCKERS |
| P-006A | damage-anchor | Correct the invalidated wolf HP and writer attribution | Unblocks P-006 reaction timing | HP `+0x28C`, damage record `+0x18`, writer `0x0800FA50`, death threshold confirmed | Complete | COMPLETE |
| P-007 | differential | Compare recovered Buu player/combat functions against LoGII/LoG1 material (manual structural comparison only) | Answers what combat feel is shared vs changed | P-006 reaction timing remains incomplete | Defer until P-006 reaction work completes | DEFERRED until P-006 |
| AUTO-007 | script-vm | How does the Buu bytecode VM relate to Legacy repo's 145-opcode LoG1 VM inventory? | Dialogue/quest scripting is a whole engine subsystem | `extern/Legacy/OpCodes.csv`, `DBZKit/Legacy/Games/BYTECODE_VM.cs` (LoG1 lineage, INFERRED transferability) | Locate Buu bytecode consumers from MapEntry script pointers; compare opcode dispatch shape | DEFERRED |
| AUTO-008 | bsim | Calibrate BSim against an independent related binary | TOOL-002 closed BLOCKED: no independent related binary locally | TOOL-002 archive | Needs a new local binary (e.g., another-region dump) before any work | BLOCKED |
| AUTO-009 | external-knowledge | Data Crystal / community addresses for Buu's Fury or LoG1/LoGII worth validating? | Cheap candidate anchors if any exist | None imported so far (deliberate) | Web search; record EXTERNAL CLAIM then validate against canonical profile before use | DEFERRED |

## Recent Discoveries

Synthesis pass after units 1-5 (2026-08-23):
- No contradictory field interpretations found; `+0x8C` variation-word
  retention (ROM-005) is now linked to `downstream_080075AC` carrying it
  across transitions (AUTO-003).
- Ghidra markup updated: `FUN_080089fc -> map_entry_lookup_080089FC`,
  `FUN_08009670 -> population_adapter_08009670`.
- Queue reconciled: AUTO-001/002/003/004/010 RESOLVED; BSim stays BLOCKED;
  script VM and external-knowledge stay DEFERRED; next research objective is
  AUTO-011.
- Naming consistency rule going forward: new DB names use
  `<role>_0XXXXXXXXX` lowercase-hex suffix form.

(Inherited anchors are summarized in SUBSYSTEM_MAP.md; this section records new
findings from this research lane only.)

- **AUTO-001 (2026-08-23), read-only static, canonical profile:**
  - `CONFIRMED`: MapEntry-39 selected value `0x08294968` is unique among all
    452 variation first-words (webfoot find-first-word).
  - `CONFIRMED`: descriptor array at `0x08294960` = `[0x08294930, 0x08294948]`.
  - `CONFIRMED` bytes of sibling descriptor `0x08294930`: factory raw
    `0x080072CD` (matches ROM-007's second runtime factory), `+0x04` raw code
    pointer `0x0800776D`, bounds `(96,0)-(257,17)`, bytes `+0x10/+0x11`
    `01 01`.
  - Negative result: sibling bounds `(96,0)-(257,17)` do not overlap the
    ROM-012 doorway `(592,136)-(601,241)`. Under the CONFIRMED containment
    semantics, VERTICAL-001 result-C's persisting transition is NOT caused by
    this array's sibling. The remaining source lies elsewhere in the registry
    population or another mechanism.
  - `INFERRED` (strong): descriptor stride/extent `0x18` for this pair -
    adjacent, both array-referenced, both start with plausible raw factory
    words, one value (`0x08007675`) independently runtime-confirmed. Not yet
    proven as a global rule (feeds AUTO-006).
  - Both sibling descriptors share `+0x04 = 0x0800776D` (Thumb fetch
    `0x0800776C`, four bytes after filter `0x08007768`). Function role
    UNKNOWN; Ghidra seeding candidate.
  - Literal `0x08179764` observed at `0x082949B4` inside the variation-record
    neighborhood. Matches DragonByteZ's upstream claim of a global atlas table
    at file offset `0x179764`; independent consumer proof pending.
    Classification: EXTERNAL CLAIM corroborated by byte presence only.

- **AUTO-002 (2026-08-23), Ghidra static, calibrated project:**
  - All five verified query callsites are now attributed to recovered
    containing functions; every containment check CONTAINS:
    - `candidate_caller_08006E3C` (body `0x08006E3C..0x08006FDF`) contains
      point-query callsite `0x08006E4E`.
    - `candidate_caller_08012A24` (body `..0x08012B5D`) contains
      `0x08012AEC -> aabb_query_080127AE`.
    - `candidate_caller_08021CC0` (body `..0x08021EAD`) contains both
      `0x08021DFE/08021E06 -> point_query`.
    - `candidate_caller_080220D8` (body `..0x08022149`) contains
      `0x08022142 -> aabb_query_08012846`.
  - New DB entries: `aabb_query_080127AE`, `aabb_query_08012846`
    (`STRONG_STATIC`; entries from ROM-008 independent BL decode).
  - Cross-validation: post-seed entry references for all three query entries
    list exactly the ROM-008 callsites with resolved source functions.
  - Static shape classifications (CANDIDATE semantics, boundaries candidate):
    - `candidate_caller_08006E3C`: parameterless global-driven frame handler;
      button bits (halfword at `*ctx+4` bit0/bit1), point query at a tracked
      entity, heavy use of message family `FUN_08011xxx`.
    - `candidate_caller_08012A24`: entity method; flag gate on global `+0xC`;
      table-indexed text/message calls (`FUN_08052fd4` +
      `FUN_08011c0c/08011c70`); the known `+0x16` halfword gate; sound-like
      `FUN_0800797c(0xf,0x4b)`. Entity position words at `+0xA0/+0xA4`
      (`>>8` fixed point).
    - `candidate_caller_08021CC0`: periodic dual-point spatial sensor with
      60-frame counters, animation-id getter `FUN_0802bfbc(0x6f..0x73,...)`,
      two dispatched objects' `+0x16` gates.
    - `candidate_caller_080220D8`: factory allocating 0x200 via shared
      allocator `FUN_0803d5b8`, installs table `_DAT_080222d8`, registers a
      child into the message family, then immediately runs
      `aabb_query_08012846` - area-effect/hitbox-spawner shape.
  - New subsystem anchors: allocator `0x0803D5B8`, resource-by-id getter
    `FUN_0802bfbc`, message/dialogue family `FUN_0801191a / 08011944 /
    08011a1e / 08011c0c / 08011c70 / 08011db4 / 08011e0e / 08011e94`
    (CANDIDATE roles).

- **AUTO-003 (2026-08-23), Ghidra static, calibrated project:**
  - `downstream_080075AC` (body `0x080075AC..0x08007673`) is a **map-transition
    executor** (STRONG_STATIC, semantics CANDIDATE):
    - gates on object vtable`+0x84` dispatch result halfword `+2` vs receiver
      byte `+0x11`;
    - invokes the object's vtable`+0x34` method with arg `2`, remembering the
      result;
    - calls `FUN_08008d44(global_ctx, byte[ctx+0x11], byte[ctx+0x12],
      ptr=ctx+0x14, byte[ctx+0x13], 1)` -> returns a NEW map-context pointer.
      `FUN_08008d44` sits inside the established map-load flow between the
      confirmed MapEntry-lookup BL sites `0x08008D2A/0x08008D6C`. Three bytes +
      pointer args match MapEntry's zone/area/variation byte shape.
    - transfers spawn-position byte (`ctx+0x10`, nibble logic) into new
      context `+0x10`;
    - when the vtable method returned nonzero: stores the pre-transition saved
      word at **new context `+0x8C`** - exactly where consumer-analysis placed
      the retained selected variation word - then dispatches the new context's
      table`+0x28` method (population-shaped);
    - else allocates a 0xC-byte pending marker object via `FUN_0803d5b8`.
  - Trace-site functions recovered and named:
    `candidate_trace_site_080077EC` (`..0x08007853`, calls `08009744`),
    `candidate_trace_site_08009744` (`..0x080097A5`, calls `080094B8`,
    callers also `08007916`, `080211fa`),
    `candidate_trace_site_080094B8` (`..0x080094EF`, copy-shaped).
  - Interpretation (INFERRED): accepted spatial actions of this family execute
    area transitions; VERTICAL-001's persisting transition therefore likely
    came from another accepted containment on some other descriptor-driven
    object or another mechanism feeding the same loader.

- **AUTO-004 (2026-08-23), read-only static census, canonical profile:**
  - `CONFIRMED`: 839 four-aligned words match confirmed factory raw values
    (`669 x 0x08007675`, `170 x 0x080072CD`); ALL decode as shape-plausible
    descriptors (odd Thumb-shaped `+0x04`, ordered signed bounds). Nearly all
    share `+0x04 = 0x0800776D`; an earlier data region uses `0x080077DF`.
    Strong global support for the descriptor field map (extent still
    unproven; feeds AUTO-006).
  - `CONFIRMED`: exactly ONE candidate besides `0x08294948` overlaps the
    doorway rectangle: `0x081BE1B8`, bounds `(600,176)..(609,201)`.
  - `CONFIRMED` ownership chain for that candidate:
    descriptor <- array `0x081BE260[7]` of 14 pointers <- selected value
    `S=0x081BE298` (`+0x40`=14, `+0x44`=array; word0 `0x000C1041`) <-
    variation source `0x0808AEBC[0]` <- **MapEntry 377**
    (out=15, zone=19, area=1, variation=5). Different map: its map-local
    bounds cannot fire at MapEntry-39's doorway.
  - `CONFIRMED`: MapEntry 39's variation source `0x080753F0` contains exactly
    one selected-value-shaped structure (`source[0] = S39`); no selector!=1
    alternative population exists statically there.
  - Consequence (INFERRED, strong): after the VERTICAL-001 patch, NO
    descriptor-driven registry member of MapEntry 39 could accept containment
    at the doorway. The persisting transition must come from non-descriptor
    registry members (heterogeneous population, e.g., entity-spawned) or a
    non-registry mechanism. New queue items AUTO-010/AUTO-011 target these.
  - INFERRED leads (unproven): descriptor byte10 clusters by rectangle shape
    (`00` interior/bottom strips, `01` top strips, `02` left strips,
    `03` right strips); byte11 clusters by map group (MapEntry-39 pair has
    `01`, MapEntry-377 set has `0F`). Descriptors also carry unknown halfword
    fields at `+0x12/+0x14`.

- **AUTO-010 (2026-08-23), Ghidra static, calibrated project:**
  - `candidate_map_loader_08008d44` (body `0x08008D44..0x08008E6F`) is the
    map-transition loader (STRONG_STATIC):
    - writes its zone/area byte args into context `+0/+1`;
    - adjusts spawn coordinates by `-0x70, -0x4C`;
    - calls **`FUN_080089fc`** (the CONFIRMED MapEntry lookup) and feeds the
      result plus adjusted spawn into **`FUN_08008b30`** (the established
      map-load flow);
    - spawns entities through an 0x18-stride per-type table
      (`FUN_0801713c`, `FUN_080109aa`/`FUN_080104f2`, allocator wrappers,
      list-add `FUN_08021094`, message attach `FUN_0801191a`);
    - compares `FUN_08008a36(ctx+4)` music id against ctx `+8` and attaches a
      change object on difference (map BGM switch).
  - Additional direct callers of the loader: `FUN_080022e6`, `FUN_08002390`,
    `FUN_08005abe` - candidate non-door warp sources (scripts/NPCs).
  - Transition chain now end-to-end statically: containment -> filter ->
    `spatial_action_080125E8` -> `downstream_080075AC` ->
    `candidate_map_loader_08008d44` -> MapEntry lookup + load flow.

- **AUTO-011 (2026-08-23), Ghidra static + xref census:**
  - `CONFIRMED` (static): `registry_populate_08012664` has exactly ONE
    caller - `population_adapter_08009670`. The descriptor-array path is the
    only feeder of that primitive.
  - `CONFIRMED` (static): a SECOND independent registry-append site exists at
    `candidate_registry_writer_08009172` (body `..0x08009195`): reads an
    object pointer from `*(arg+4)+0x10 + idx*8 + 4` (8-byte-stride record
    table), dispatches vtable[0] via `FUN_08046aa2`, appends result to the
    manager reached through literal `DAT_080091fc+0x10`. Its only recovered
    callsite is `0x080026FC` (containing function unrecovered).
  - Manager-global `0x03002A64` xref census (25 refs): known sites plus
    direct READ/WRITE accessors `FUN_0800d30e` (`0x0800D4C0/C4`),
    `FUN_08017f5a` (`0x0801804A/E`), `FUN_08018078`, `FUN_08018346`,
    `FUN_0803643c`, `FUN_0803656c` (x3), `FUN_08036914`, `FUN_08002862`,
    and DATA references at `0x08070190`, `0x080707B4/E0/E4`. The reset at
    `0x08048488` did not appear in recovered xrefs (likely unrecovered
    literal flow; not evidence of absence).
  - Consequence (INFERRED): the spatial registry has multiple mutation sites;
    non-descriptor members (e.g., entity-spawned) remain a live candidate for
    VERTICAL-001 C. Refined into AUTO-012.

- **AUTO-012 (2026-08-23), Ghidra static + byte decode - VERTICAL-001
  RESOLVED:**
  - `CONFIRMED` (static): containing function of callsite `0x080026FC` is
    `candidate_registry_spawn_080026EA` (`..0x08002701`): pops an index from a
    `{count, elems[]}` stack-array and calls the writer with the map-context
    global **`0x0300197C`** (literal chain `0x08002954 -> 0x08054FBC+0xC`).
    Reached via function-pointer table entry `0x080552C0 -> 0x080026EB`
    (dense engine dispatch table region `~0x08055284..`).
  - `CONFIRMED` (static): `candidate_registry_writer_08009172` iterates
    **`MapEntry[+0x10] triggers_pointer_raw` as 8-byte records** (count =
    MapEntry `+0x04`), reads each record's `+4` pointer, and dispatches its
    vtable[0] to construct the registry member.
  - `CONFIRMED` (static): handler `candidate_trigger_handler_0800742C`
    allocates the SAME 24-byte rectangle object and runs the SAME common
    initializer `FUN_08009AEC`; source field roles identical to spatial
    descriptors (`+04` callback producer, `+08/+0C` bounds); installs family
    vtable base `0x08049BD4`; copies source `+0x10` word to object `+0x14`.
    Trigger objects are first-class rectangle members of the same registry.
  - MapEntry 39 has 11 trigger records; record[1] type `0x00020006` ->
    source `0x080755C0`: producer `0x08007791`, bounds **`(481,121)..(615,271)`
    - CONTAINING the entire doorway rectangle `(592,136)..(601,241)`**
    (`producer candidate_trigger_producer_08007790` builds an 8-byte receiver
    `{table 0x0804ACE0, 0}`).
  - CAUSAL CHAIN for VERTICAL-001 result C (STRONGLY SUPPORTED, Level 2/3
    boundary): after descriptor `0x08294948` was emptied, the player still
    stood inside trigger[1]'s rectangle; the generic point query accepted it;
    ITS action path executed; the transition persisted. The exact concrete
    action target behind receiver table `0x0804ACE0` is UNKNOWN (computed
    dispatch; no static refs beyond producer). Per steering rule this does
    not change the resolution.
  - OLD CLAIM / NEW EVIDENCE / RESOLUTION:
    - OLD: "The remaining transition source is not established" (VERTICAL-001,
      PROJECT_STATE unresolved list).
    - NEW: trigger-array population path + containing rectangle identified.
    - RESOLUTION: descriptor-driven doorway was one of at least two overlapping
      accept regions on MapEntry 39; the trigger-family member persists.

- **TOOLKIT-007 (2026-09-06), corpus-wide byte measurement - AUTO-012 scope
  narrowed:**
  - Measured all 452 MapEntry records against the canonical Buu ROM, rather
    than the single entry AUTO-012 decoded. The `+0x04`/`+0x10` pairing splits
    four ways: 136 entries count 0 + NULL pointer; **163 entries count > 0 with
    a NULL pointer**; **69 entries count 0 with a live ROM pointer**; 153
    entries count > 0 with an in-window pointer. No entry points outside the
    ROM window, and no two arrays share a start.
  - Of the 153 readable extents, only **35 have every slot shaped like the
    confirmed `{type, source_ptr}` example**; the other 118 contain words that
    are neither small type codes nor ROM pointers. MapEntry 39 is itself one of
    the 118: its declared count of 11 runs past its four well-formed records
    into data of another shape.
  - **MapEntry 451 declares 4 records at `0x0008E2D0`, an extent covering the
    first 16 bytes of the MapEntry table at `0x0008E2E0`** - the table that
    indexes it. A count describing an array that consumes its own table is not
    describing an array.
  - Unaffected: the AUTO-012 static findings stand exactly as recorded, and the
    MapEntry 39 example reproduces byte-for-byte - slot[1] is
    `{0x00020006, 0x080755C0}` and that source's halfwords at `+0x08` are
    `(481,121,615,271)`. TOOLKIT-007 keeps it as a regression fixture.
  - OLD CLAIM / NEW EVIDENCE / RESOLUTION:
    - OLD: `MapEntry +0x04` broadly counts 8-byte trigger records reached
      through `+0x10` (read from AUTO-012's single-entry static decode).
    - NEW: corpus-wide measurement contradicts that generalisation - 232 of 452
      entries pair a count with no array or an array with no count, 118 of 153
      readable extents are non-uniform, and one declared extent overruns the
      map table itself.
    - RESOLUTION: `+0x04` is NOT a general trigger count. The stride and the
      one verified example remain CONFIRMED; the corpus-wide reading is
      withdrawn. TOOLKIT-007 therefore carries all readable extents as opaque
      8-byte slots (152 arrays, 873 slots, 6,984 bytes, byte-exact) and applies
      typed `{type, source_ref}` semantics only to the 35 uniform arrays
      (89 slots, 712 bytes). What `+0x04` actually counts is UNKNOWN and was
      not investigated; TOOLKIT-007 scope forbids fresh RE on it.

- **P-001 progress (2026-08-23), Ghidra static - player entity anchors:**
  - `CONFIRMED` (static): `candidate_entity_ctor_a_080109AA` allocates a
    **0x240-byte entity**, base-initializes via `FUN_0800e6b8`, installs table
    base (literal `0x08010b68`), and stores the entity into global
    **`0x03001C34`** (write at `0x080109e6`; literal `0x08010b6c`). It then
    attaches a per-type component chosen through a `0x68`-stride record array
    (`FUN_0801714a`) and dispatches its vtable[0].
  - `STRONG_STATIC`: the stored `0x03001C34` entity is the player-controlled
    entity candidate: ROM-009 identified that slot as the point-query context;
    ROM-012's query entity tracked human movement; frame handler
    `candidate_caller_08006E3C` queries at this slot's value.
  - `CONFIRMED` (static): wrapper ctor `candidate_entity_ctor_b_080104F2`
    (0x240 alloc, calls ctor_a with flag 1, overrides vtable, attaches a
    0x10-byte sub-object via `FUN_0800ed18`, `FUN_0800ecda(ent,0xf)`); called
    by the map loader in its alternate branch.
  - `CONFIRMED` (static): `candidate_entity_dispatch_08013914(entity, arg)` is
    an **entity state-machine tick**:
    - gate: halfword `entity+0x16 != 0` (the ubiquitous +0x16 gate);
    - state-group byte at `+0x14` indexes a 0x18-stride table
      (`DAT_08013b9c`);
    - current/next state halfwords at `+0x16/+0x18` (+ copies to `+0x1A/
      +0x1C`) advance on timer expiry (`FUN_080135d2` reads `+0x24` timer;
      threshold from table; advance via `FUN_08013678`; sound wrappers
      `FUN_0800f53c/f558` around `FUN_0801064c`);
    - nibbles of `entity+0x02` select two 0x68-stride per-character records
      at `DAT_08013ba0+0x4f8` (recursion over both; `FUN_0801375e` on
      transition).
  - Update-root candidate: `FUN_080043d8` (sole non-recursive caller of the
    tick) - NEXT decompile target.
  - `CONFIRMED` (static): `candidate_frame_update_080043D8` is a thin adapter:
    `tick(base + base[0]*0x68 + 0x4f8)` - i.e., it runs the entity state
    machine for the ACTIVE record of the recurring 0x68-stride per-character
    array (leading byte = active index). Its caller is `FUN_080033d2`
    (next link toward the frame scheduler).
  - `CONFIRMED` (static): scheduler chain completed -
    `candidate_game_tick_080033D2(tasklist)` pops a task (`count--`, element
    `[count]`) and ticks it with base = `[0x08054FBC]+0x14` = IWRAM
    **`0x03001068`** (reached via function pointer; no direct BL callers).
  - `CONFIRMED` (byte-level): game-state block at IWRAM `0x03001068`
    (`+0x00` active character byte; character records begin at `+0x4F8`);
    record array base in ROM at **`0x086B7578`** (`DAT_08013ba0=0x086B7080`
    literal pool + 0x4F8). The tick's `DAT_08013ba4` is literally
    **`0x03001C34`** - the state machine directly drives the player-entity
    slot.
  - Observation: character records embed UTF-16 dev labels (record[0]
    begins `'state data "'`) followed by packed parameter groups pairing ROM
    data pointers (`0x086B75DC/61C/65C/69C...`) with consecutive IWRAM words
    (`0x03002B88..0x03002B94`). Layout semantics UNKNOWN; likely per-state
    definitions. P-002 will decode as needed.
  - P-001 answer summary: player entity = object stored at `0x03001C34`;
    update path = task stack -> `candidate_game_tick_080033D2` ->
    `candidate_frame_update_080043D8` -> `candidate_entity_dispatch_08013914`
    (state machine) over active character record.

- **P-002 progress (2026-08-23), static - input/position anchors:**
  - `CONFIRMED` (byte-level): ROM table `0x08070180` is a master global
    directory: `[0]=0x03003300` (system/input ctx), `[1]=0x03003898`,
    `[2]=0x030019A4`, `[3]=0x03001068` (character block),
    `[4]=0x03002A64` (spatial registry manager), `[5]=0x03001C4C`.
    Only two literal-pool references exist to the directory
    (`0x08006FE0` frame-handler pool; `0x0804FDB0`).
  - Behavioral fact (raw): button state is read as
    `*(u16*)(*(0x08070180)+4)` = `*(u16*)(0x03003300+4)`; masks observed:
    `& 0xF3` (text entry gate), `& 0xF0` (interact toggle). Bit meanings and
    the +4 writer are UNKNOWN (no KEYINPUT literal anywhere in ROM -> IRQ or
    computed-address copy).
  - Behavioral fact (raw): positions are 32-bit fixed-point words whose
    map-pixel value is obtained with `>>8` (integer part in upper bits;
    "32-bit fixed-point with 8 fractional bits", not 8.8). Seen as
    `param+0xA0/+0xA4` in `candidate_caller_08012A24`; point query compares
    `>>8` values against descriptor bounds; projectile stepper integrates
    `pos += vel` on the same representation.
  - Behavioral fact (raw): `candidate_input_acc_b_0802C564` writes entity
    `+0x1A0/+0x1A4` from stored coords before dispatching vtable[+0x28] on
    both entities - warp/respawn-position shape (INFERRED purpose).
  - Behavioral fact (raw): linear-animator pattern in
    `candidate_input_acc_c_0802D940`: per-tick `field+0x20 += field+0x40`,
    `+0x24 += +0x44`, frame counter `+0x48` wraps at 24 ticks, row stride
    0xC into `+0x4C` table (sprite/frame stepper candidate; INFERRED).
  - Next P-002 step: identify the `0x03003300+4` writer (IRQ/main-loop key
    copy), then follow direction-bit consumers into entity velocity writes;
    recover cardinal/diagonal speeds.

- **P-002 progress 2 (2026-08-23), static - dev labels + first combat
  quantities:**
  - `CONFIRMED` (byte-level): UTF-16 developer diagnostics embedded before
    the character-record region:
    - `0x086B7400`: "Energy attack level set for attack which doesn't exist
      for player!"
    - `0x086B748C`: "Energy attack level requested for attack which doesn't
      exist for player!"
    - `0x086B7524`: "Unable to find sprite index in character state data"
    Literal-pool refs: `0x08013BC8` and `0x08013E20` - an energy-attack
    accessor cluster immediately after the state-machine tick (P-003 lead).
    INTERNAL DEVELOPER EVIDENCE only; semantics to be validated against
    executable behavior before naming.
  - Record-region layout note: record[0] is a `'state data "'` header;
    subsequent 0x68-stride slots are heterogeneous (pointers like
    `0x086B7CCC`, packed bytes) - the uniform-record model needs revision;
    treat 0x68 indexing as into a mixed state-data blob until decoded.
  - `CONFIRMED` (static): `candidate_player_update_080247BE` (body
    `..0x080248DB`) is a projectile/effect stepper, NOT the walking player.
    Behavioral spec captured anyway (first concrete combat quantities):
    - integration per tick: `pos+0x20 += vel+0x48`; `pos+0x24 += vel+0x4C`
      (32-bit words, 8 fractional bits);
    - animation counter `+0x50++`; anim byte `+0x44 = counter>>2`;
      frames table at `+0x54` stride 0xC; after counter>>2 >= 5 the object
      detaches via message-family remove (`FUN_08011944`);
    - hitbox: rect `(pos>>8 -8) .. (pos>>8 +8)` on both axes = 16x16 pixels,
      tested against target bounds by AABB helper `FUN_0800fe78`
      (`iStack_* < ...` overlap form);
    - on hit: attach to target (`FUN_0800e9d8`), dispatch target vtable
      `+0x5C`, then vtable[+0x34] with id 0x17, and on nonzero vtable[+0x28];
      sets self flag `+0x40=1`;
    - a timer clamp compares two globals' `+4` fields and raises the lower
      to the higher (cooldown-style; roles UNKNOWN).
  - Next P-002 step unchanged (buffered-input consumers -> walk speed);
    P-004 anchors now include projectile integration + hitbox + hit dispatch.

- **P-002 progress 3 (2026-08-23), static - corrections + collision concept A:**
  - CORRECTION (OLD CLAIM / NEW EVIDENCE / RESOLUTION):
    - OLD: `candidate_entity_dispatch_08013914` interpreted as the player
      behavior state-machine tick.
    - NEW: its helpers are `candidate_state_timer_080135D2` (binary search in
      a 150-entry tier table), `candidate_state_advance_08013678` (RNG-scaled
      blends of paired halfwords via `FUN_0803facc(0x100)` randoms),
      `candidate_dual_transition_0801375E` (averages TWO character records'
      paired values with ~0.605 weighting (`*0x9A>>8`), packs both component
      IDs into `entity+2` nibbles, averages timers, adds +10 to three bytes).
    - RESOLUTION: reclassify as CANDIDATE character-blend/progression system
      (not input-driven movement). Movement lives elsewhere.
  - `CONFIRMED` (static): player entity dispatch table at `0x0804C9F0`
    uses **signed 32-bit relative offsets** (target = table + offset); 16
    slots resolved, all valid Thumb entries.
  - `CONFIRMED` (static): slot[9] -> `candidate_player_method9_08010DDE`
    is an entity MESSAGE HANDLER (inter-entity query protocol):
    - msg 0x00: rect-vs-body overlap via bounds helper `FUN_0800fe78`;
      accept -> attach caller obj + dispatch own vtable`+0x58`, return 1
    - msg 0x01: point-in-body via `FUN_0800fdfa`; same accept path
    - msg 0x02: overlap test only (no attach)
    - msg 0x09: return self
    - msg 0x0a/0x0b: singleton acquire/release keyed by active character
      record byte (`[char*0x68+0x50C]` pattern); stores self into a global
    - msg 0x1a: dispatch through retained ref at entity word index 0x8b
    - msg 0x28: **circle-vs-body**: clamp point to body AABB, squared-distance
      vs radius^2; accept -> attach + vtable`+0x58`
    - default: `FUN_080102d8` continuation
  - Collision concepts now separated (steering #4):
    - **A. PLAYER WORLD BODY**: bounds getter `FUN_0800fe78(entity)`, point
      test `FUN_0800fdfa`, message ids 0/1/2/0x28 on entity vtable slot 9;
      accept reaction = attach + vtable`+0x58`. Dimensions UNKNOWN so far.
    - **B. MELEE ATTACK REGION**: not yet located.
    - **C. PROJECTILE/EFFECT REGION** (`candidate_projectile_stepper_080247BE`,
      renamed): per-tick `pos(+0x20/+0x24) += vel(+0x48/+0x4C)`; 16x16
      centered AABB `(pos>>8 -8)..(pos>>8 +8)` vs target body via
      `FUN_0800fe78`; hit dispatch target vtable`+0x5C` ->
      vtable`+0x34`(id 0x17) -> conditional vtable`+0x28`; lifetime counter
      `+0x50`, frame byte `counter>>2`, detach at >=5. Counter cadence NOT
      established (the 4-ticks/frame idea is speculation; do not rely).
  - Next P-002 steps: decompile remaining resolved slots of the player
    vtable (esp. early slots) for the frame update that consumes buffered
    direction bits; then movement quantities.

- **P-002 progress 4 (2026-08-23), static - position fields + body model
  CONFIRMED; slot triage pass 1:**
  - CORRECTION (OLD / NEW / RESOLUTION):
    - OLD: `entity+0xA0/+0xA4` treated as generic entity position words.
    - NEW: for the player/actor class, position lives at **`+0x1A0` (X),
      `+0x1A4` (Y)** - independently confirmed by `cand_body_bounds_0800FE78`,
      `cand_point_in_body_0800FDFA`, and `cand_slot3_0801003A`
      (`param_1[0x68]>>8`, `param_1[0x69]>>8`). The `+0xA0/A4` pattern seen
      earlier belongs to a different entity class.
    - RESOLUTION: movement-spec POSITION rows use `+0x1A0/+0x1A4`.
  - `CONFIRMED` behavioral facts (raw):
    - Body rect A (table-driven): `bounds(entity)` =
      `{px + T[i].x0, py + T[i].y0, px + T[i].x1, py + T[i].y1}` where
      `T = *(entity+0x58) + byte(entity+0x10)*0x10` and each entry is
      `{+0x10 x0, +0x14 y0, +0x18 x1, +0x1C y1}` (signed, pixel units after
      `px=*(+0x1A0)>>8`).
    - Body rect B (simple): `{px, py, px + byte(+0x19C), py + byte(+0x19D)}`
      from `cand_point_in_body_0800FDFA`; slot3 additionally uses signed
      extent bytes `+0x19E/+0x19F` around the position for an in-map test.
    - slot3 also derives camera-relative coords into entity words `[0x1b]/
      [0x1c]` from map-ctx (`DAT_080102d0` -> ctx +0x28/+0x2C origin,
      +0x1C/+0x20/+0x24 map rect) and sets in-bounds flags `[0x18]/[0x19]`,
      plus a secondary hotspot-rect test driven by tables at `[0x14]/
      [0x16]`.
  - Shallow vtable triage (16-slot table `0x0804C9F0`; sizes are function
    body spans):
    - [0] `0x08010B80` (0x38) UNKNOWN (named candidate_player_method0)
    - [1] `0x0804F53C` (0x14) UTILITY tiny
    - [2] `0x08010BD2` (0x20) UNKNOWN small
    - [3] `0x0801003A` (0x293) UTILITY - derived spatial status (above)
    - [4] `0x0800EF94` (~0x463) RENDER-candidate - packs entity data into a
      buffer with `>>2` packing via `FUN_08046ff4/FUN_0803fcf4`
    - [5] `0x0800F3F8` (0x16) UTILITY tiny
    - [6] `0x08011050` (0x8) STUB/tiny
    - [7] `0x0800F516` (0x26) UNKNOWN small
    - [8] `0x0800F4E6` (0x30) UNKNOWN small
    - [9] `0x08010DDE` MESSAGE (message-handler ABI; DB name currently
      `candidate_player_method9_08010DDE` - forced rename to
      `candidate_entity_message_handler_08010DDE` did not apply due to arg
      quoting; same function)
    - [10] `0x0800ECF0` (0x28) UNKNOWN small
    - [11] `0x08010974` (0x36) helper directly preceding ctor_a
    - [12] `0x0800ED3E` (0x42) UNKNOWN small
    - [13] `0x08010D26` (0x56) UNKNOWN
    - [14] `0x0800FFA2` (0x66) UNKNOWN
    - [15] `0x0804E4F8` (0x2) STUB
  - No input-consumer slot identified yet; next pass targets remaining
    UNKNOWN slots ([0][2][13][14] first) and key-mask constant hunting
    around the player method cluster.

- **P-002 progress 5 (2026-08-23), static - bounded pass CLOSED:**
  - Additional frame-handler callees ruled out as walkers:
    `cand_frame_step_0800425C` = timer/flag housekeeping (countdowns at
    ctx+0x4D4/0x4D8/0x4DC, one point-in-body liveness check);
    `cand_frame_helper_0800938C` = BG/DISPCNT video-mode setup from map ctx
    (BGxCNT scroll fields +0xA4..+0xC0).
  - Projectile stepper has NO recovered callers (indirect dispatch).
  - Static per-function triage has diminishing returns -> steering Â§6
    runtime displacement experiment designed (see Current Objective) and
    queued as the P-002 closer.

- **P-002 RESOLVED (2026-08-23), RUNTIME displacement experiment:**
  - Method: stock mGBA `--savestate` launches (one per condition; NO --gdb -
    the gdb flag halts emulation without a client), established Lua injector,
    tracked probe `tools/runtime/p002_walk_probe.lua` (allowlisted in the
    injector), untracked driver `build/research/p002-exp/run_experiment.ps1`.
    Working state = hash-verified copy of ROM-008 Higher Plane state; canonical
    ROM SHA verified before/after every launch. Per-frame trajectory CSV under
    ignored build/research/p002-exp/p002-walk-log.csv.
  - BEHAVIORAL SPECIFICATION (evidence: this experiment unless noted):
    - INPUT: buffered halfword at **`0x03003304`**, ACTIVE-HIGH mirror of GBA
      KEYINPUT bits, empirically: Right=0x0010 (+X motion CONFIRMED),
      Left=0x0020 (-X), Up=0x0040 (-Y), Down=0x0080 (+Y); A=0x0001, B=0x0002,
      Select=0x0004, Start=0x0008 echoed but not motion-relevant (INFERRED
      identity). Game consumes/clears the buffer (value visible only on some
      sampled frames). NOTE: `C.GBA_KEY.*` Lua constants are enum indices,
      NOT bitmasks - do not feed them to setKeys.
    - POSITION: X=`player+0x1A0`, Y=`player+0x1A4`, player ptr from
      `0x03001C34` (dynamically re-read every frame). 32-bit fixed-point with
      8 fractional bits. Start pixel (272,352).
    - CARDINAL MOVEMENT: raw delta **352/tick** (= 352/256 = **1.375
      px/gameplay-tick**) on each axis, sign per direction. Constant while
      held.
    - DIAGONAL MOVEMENT: components remain **352 & 352** - UNNORMALIZED;
      resultant ~498 raw (~1.945 px/tick) = sqrt(2) x cardinal.
    - INPUT->MOTION DELAY: first nonzero delta observed 2-3 ticks after
      buffer assertion.
    - ACCELERATION: IMMEDIATE (constant step magnitude from first moving
      tick; no ramp).
    - UPDATE CADENCE: movement steps appear on consecutive sampled frames
      during hold; display frames vs gameplay ticks behaved 1:1 in this
      experiment (warmup ticks advanced ~60/second wall-clock).
    - FACING: UNKNOWN (not sampled; deferred to animation/melee work).
    - STATE GATES/COLLISION: none encountered on tested open area; where
      desired movement is rejected/clamped remains UNKNOWN.
  - Static input-consumer function (writer/reader of 0x03003304) remains
    UNKNOWN and is deprioritized per steering.

- **P-003 progress (2026-08-23), runtime attack scout:**
  - Method: `tools/runtime/p003_attack_scout.lua` +
    `tools/runtime/p003_move_attack.lua` (both allowlisted), untracked driver
    `build/research/p002-exp/run_scout.ps1` / `run_move_attack.ps1`; per-tick
    differential of player entity words 0x000..0x23C + registry count +
    buffered input; screenshots at fixed offsets. ROM hash verified per
    launch; same clean Higher Plane state throughout.
  - `CONFIRMED` (runtime): **A (buffer 0x0001) is the attack/interact
    button.**
    - Near the fountain NPC: A opens a dialogue/menu overlay (screenshot:
      darkened scene + text bar; entity fields freeze; pointer swap burst
      +0x14/+0x4c/+0x50 at that moment was dialogue entry, NOT attack).
    - After walking ~35 px away: A produces a VISIBLE PUNCH (screenshot
      p003-MoveA.png: extended-arm pose) with **zero** entity-word changes
      in 0x000..0x23C during the punch window and no +0x10/+0x11 anim-word
      change - punch presentation is handled outside the sampled struct.
  - `CONFIRMED` (runtime): B (0x0002) produced no observable entity change
    in open field (role UNKNOWN - candidate: energy/charge/guard).
  - `CONFIRMED` (runtime): walk->idle transition swaps +0x14/+0x4c/+0x50
    (animation-table pointers) and sets +0x11 anim byte to 01; registry
    count stays 3 throughout (melee does not register spatial objects).
  - Entity word +0x10 layout refined: byte +0x11 = animation/segment id,
    byte +0x12 = per-anim frame counter (control idle cycles segments
    03->02; values observed only, semantics INFERRED).
  - OLD CLAIM / NEW EVIDENCE / RESOLUTION: earlier Scout_A pointer-swap
    burst was interpreted as possible attack state; screenshot proved it
    was dialogue entry. Attack identification now rests on the open-field
    punch evidence.

- **P-003/P-004 progress 3 (2026-08-23), combat-state hit experiments:**
  - Probes: `tools/runtime/p003_hit_dump.lua` (before/after EWRAM 256KB
    dumps + per-tick trace) and `tools/runtime/p004_hit_trace.lua` (per-tick
    enemy-window diff); drivers under ignored build/research/p003-exp/.
    BUG FIXED during iteration: per-leg log path referenced LEG_NAME before
    declaration (top-level nil concat killed dofile silently; lupa compiles
    such files fine - runtime-only failure).
  - `CONFIRMED` (runtime): combat state has player at `0x0203D074`,
    px(48,208), registry count 2; enemy present (screenshot t20: creature on
    left path). Player-class vtable scan found ONLY the player - enemy uses
    a different class/table (UNKNOWN).
  - `CONFIRMED` (runtime): punch tile-staging timeline - buffer consumed at
    press+1; punch sprite tiles staged `+1..+4/5`; second punch re-triggers;
    player animation struct at ~`0x0203DBC0` swaps table ptrs (`+0x3DBC4`
    anim descriptor, `+0x3DBE0/+0x3DC00/+0x3DC04` frame-row tables) at punch
    start and returns to idle tables ~34 ticks after the second punch.
    Walk/turn also swaps these tables (facing-dependent).
  - DAMAGE CANDIDATES (identity UNCONFIRMED): `0x0203DBB4` and
    `0x0203DC20` moved TOGETHER in two runs (212->199 = -13; 211->191 &
    80->60 = -20) but did NOT change in a third identical-pattern run
    (Trace2) - consistent with punches connecting only when the wandering
    enemy is in range. Damage varies between hits (13 vs 20) - stat/RNG
    formula implied. The -1 pre-dump drift (212 vs 211) is unexplained.
  - OPEN: whether the pair is enemy HP (two enemies? HP+mirror?) or
    player-side; enemy entity struct/location UNKNOWN; knockback/hitstun
    not yet captured; message-ABI participation untested (needs a reliable
    hit first).
- **P-003 progress 11 (2026-08-23), armed Z0 run - m5 never executes on
  normal punch:**
  - Setup: `--gdb` halt + Lua arm + GDB continue (all worked; game ran
    220 ticks, 18 A presses at 2on/10off, punch signature at every press);
    `Z0,8029ed8,2` installed (stub OK) BEFORE continue; watcher captured
    zero stops.
  - `CONFIRMED` (runtime): **the normal A-punch in this state does NOT
    execute m1/m5 (0x080342AE/0x08029ED8)** - Z0-on-ROM is proven
    functional (ROM-006 hits at 0x080089D4), so absence is real.
  - REINTERPRETATION (OLD / NEW / RESOLUTION):
    - OLD: "punch writes attack-object vtable 0x08049DF0 into the enemy
      struct at 0x3DE6C" (progress 7).
    - NEW: bytes `F0 9D 04 08` are equally plausible as sprite tile pixel
      data; the 0x3DE64..0x3DEB8 punch-time writes match the tile-staging
      pattern class already invalidated twice (18->13; 0->16).
    - RESOLUTION: the attack-object<->A-press linkage is UNPROVEN; m1/m5's
      owner and trigger are UNKNOWN. The m5/m1 FUNCTIONS remain valid
      static decodes (genuine body-bounds hit test + phase machine) but
      belong to an untriggered path in this state.
  - NEW LEAD: punch writes ROM pointer **`0x0804A4B8`** at `0x0203DEA4`
    (0x0804A4B8 also appears in the frame-handler literal-pool region).
    Static identity check queued.
  - P-003 status: PARTIAL - input/presentation/geometry candidates exist;
    the executable contact path is NOT yet runtime-confirmed.
  - Methodology note: armed GDB run is clean and reusable (halt-arm-
    continue; per-frame capture; 220 ticks at full speed with Z0 armed
    and never hit).

- **P-003 progress 12 (2026-08-23), writer-watch taxonomy - the
  0x3DE6C zone is sprite/animation work, not combat state:**
  - Human play session (the maintainer: melee kills, area transition + respawn,
    ki kills, one level-up) with `Z2` write watch on `0x0203DEA4`
    armed before resume: 110 captures, 27 distinct writer PCs; control
    run (no input) diffed against it. Watchpoint cost: gameplay stayed
    fully playable.
  - Watched address classified: `0x0203DEA4` = accumulator field
    (`+0x38`) of a sprite/animation controller block based at
    **`0x0203DE6C`**, inside EWRAM sprite-work zone `0x3DE60..0x3DFA0`.
    Zone layout (INFERRED from FUN_0802A8AA decode + dump): `+0x10/+0x14`
    sprite-space pos, `+0x20..+0x2C` live rect, `+0x34` frame-stream ptr,
    `+0x38` accumulator, `+0x3C` frames left, `+0x40` step rate.
  - `FUN_0802A8AA` (top punch-session writer, 48 hits) decoded: frame
    stepper walking 12-byte records `{dx,dy,w,h}`, advancing `+0x34`,
    writing rect `+0x20..+0x2C`, ending via
    `FUN_08011944(&DAT_03001c4c,...)` when `+0x3C` exhausts.
  - RECLASSIFICATION of the orphaned subsystem (progress 11): code in
    the `0x080342xx` region executes during ORDINARY frames (shared with
    no-input control), installing function pointer `0x080342A9` into
    sprite-block `+0x30`; clip pointers (`0x0804BC98`, `0x080499E4`,
    `0x080497C4/D4`, `0x0804AAF4`) rotate through zone slots on
    animation change. The `cand_49df0_*` family is best explained as
    the SPRITE/ANIMATION subsystem, not melee combat. m5's body-test
    geometry stands as decoded but its subsystem role is presentation-
    adjacent, not proven contact logic.
  - Punch press-tick footprint (single-punch zone dump t12): ONLY
    animation-clip pointer swaps + tile staging changed in the zone -
    NO HP-like decrement anywhere in `0x3DE60..0x3DFA0` at press.
    Damage application must occur at the CONTACT frame, not at press.
  - RUNTIME CONFIRMED player stat pair: max HP `0x0203DBB4` rose
    0x212 -> 0x218 exactly across the maintainer's level-up; current HP
    `0x0203DC20` fell 0x81 -> 0x77 across the fights.
  - `0x0804A4B8` classification (bounded): offset-table data region
    immediately after an ARM interworking veneer block; aligned refs at
    `0x08006FFC` and `0x08050588`; NOT established as punch handler -
    its "punch correlation" was the same volatile-slot artifact class.
  - NEXT (P-003/P-004): find the enemy ACTOR struct outside the sprite
    zone (per-tick diff during wolf-only movement with player still),
    then kill-detection watch for wolf HP; damage write hunt moves to
    the contact frame, not the press frame.

- **P-003/P-004 progress 13 (2026-08-23), human-session watchers -
  current-HP candidate weakened, wolf candidates listed:**
  - METHOD ADOPTED (steering): human plays + OX arms narrow watchers =
    primary runtime method for combat events.
  - Two armed sessions with `Z2` on `0x0203DC20` + per-tick EWRAM diff:
    both hit the 40-stop cap on ONE repetitive per-frame writer
    **PC `0x8010252`** (r2=`0x0203DC24`, watched word rewritten every
    frame). Session 2 values rose steadily (~1/frame) - regen/timer-like
    behavior.
  - DOWNGRADE: `0x0203DC20` = player current-HP is now UNCERTAIN (it
    also climbs steadily between fights); max-HP `0x0203DBB4` stays
    STRONG (level-up +6 delta). Do not treat DC20 as proven HP.
    Static identity of `FUN_08010250..` writer queued.
  - Watcher cap lesson: repetitive writers exhaust MAX_STOPS before
    rare events; next runs need cap >=400 or skip-filtering of known
    PCs.
  - Lua full-zone per-tick diff (27K words) throttles emulation to a
    crawl (40 ticks/session) - zone narrowed to `0x0203C400..0x0203DE50`.
  - Player-still/wolf-moving change candidates (single short window,
    UNVERIFIED): `0x0203C57C/0x0203C590/0x0203C570` trio,
    `0x0203D214`; always-active writers `0x0203C5D0`, `0x0203D084`,
    `0x0203DBC0`. Require multi-second coherent-motion validation
    before any classification.
  - NEXT: static decode of writer `0x08010252`; rerun with big cap +
    narrow zone; validate wolf candidates across long player-still
    spans; then contact-frame hunt.
  - RESOLVED (progress 13 addendum, value-change capture): during real
    human combat, `0x0203DC20` shows ONLY smooth ±1/frame ramps
    (0x51->0x2c decay mid-fight; climb when idle) - writer always PC
    `0x08010252`. RECLASSIFIED: timer-like field, NOT player current
    HP. Player current-HP field is UNKNOWN again; max-HP `0x0203DBB4`
    (+6 level-up) remains the only runtime-supported stat. Damage-hunt
    must target discrete multi-unit drops on other fields.
  - STAGE A asset: clean no-debugger human session captured
    (`p004-actor-diff.csv`, 14400 ticks, u32 diff of
    `0x0203C400..0x0203DE50` + player pos/keys/HP-timer per tick).
    First-pass knockback heuristic (px jump + no-dpad) found zero
    player-hit events - detection needs loosening or explicit hit
    marking; intersection analysis pending. Data remains on disk for
    re-analysis.
  - BANK MINED (progress 13 addendum): 9 A-rising-edge presses; punch
    BASE signature = 157 rare fields in `0x0203C4xx-51x` (presentation);
    a recurring punch EXTRA signature
    `{0x203C400,404,408,40C,410,414,418,41C,420,42C}` appears as an
    identical set after 5 presses (t1074/1126/1311/1324/1341) -
    CANDIDATE contact-punch group. Independent non-punch rare clusters
    recur on `{0x0203D248, 0x0203D24C, 0x0203D29C}` (t346/820/1233/
    1039) - CANDIDATE wolf-event/wolf->player fields. Stage B: watch
    these two field sets' writers during armed human play.
  - STAGE B FIRST ATTEMPT FAILED INSTRUMENTATION-WISE: three
    simultaneous `Z2` watchpoints (203d248/24c/29c) throttled emulation
    to 33 Lua ticks in the whole window; zero writer rows. Watchpoints
    on per-frame-changing player fields are too hot for RSP halt/resume
    capture. NEXT: narrow to ONE field (start `+0x1D8`) or use skip-
    filtering by writer PC once the first capture identifies it;
    alternative - Lua-side polling of the three fields each tick
    (values, not writers) + single-field watchpoint only at confirmed
    event windows.
  - HUMAN-LABELED PUNCH EXPERIMENT (progress 13 addendum): 16 punches
    captured with per-tick zone diff; the maintainer labels post-return set
    (PUNCH 10..16): HIT = 10,11,12,14,15,16; MISS = 13. PERFECT
    discriminator: `0x0203D328` and `0x0203D330` changed after all
    6 landed, never after the miss. Player-relative: base `0x0203D074`
    + **+0x2B4 / +0x2BC** (adjacent combat/stat block; nominal size
    0x240 exceeded - block boundary needs re-check). Supporting hit-
    active neighborhood: `0x0203D2FC..0x0203D334`. NEXT (Stage B):
    single watchpoint on 0x0203D328 during short armed session ->
    writer PC -> contact/damage function; also test the old five-punch
    signature (0x203C400..2C) against these labels (not yet done).
  - STAGE B ON D328 EXECUTED - NEGATIVE WITH INFO: single `Z2` on
    `0x0203D328` armed through a human session where one punch was
    visibly LANDED; zero watchpoint hits while the labeled bank proves
    the value changes post-hit. CONCLUSION: D328/D330 are DMA-written
    (impact-effect tile staging), so CPU watchpoints cannot see their
    writer. Pre-hit values are tile-pattern bytes
    (`0x3032`, `0x312a2b29`), consistent with palette/tile payload.
    NEXT ROUTES: (a) static - identify what requests the impact-effect
    upload (find DMA descriptor/source for that tile block); (b) wolf-
    side - the labeled-bank zone ended at 0x0203DE50; diff a WIDER
    range around landed-vs-missed punches to locate the wolf actor's
    flinch/state mutation (CPU-written), then watch THAT.
  - D328 GENERALIZATION FAILURE (progress 13 addendum): follow-up
    single-watch session (one human-confirmed landed punch) - Z2 on
    `0x0203D328` fired zero times AND the parallel Lua zone diff shows
    `d328` unchanged across all 14400 post-resume ticks. Arming race
    excluded (halt-arm-continue verified). CONCLUSION: the 6-hit/0-miss
    discrimination does NOT generalize across sessions/areas - treat
    D328/D330 as CONTEXT-DEPENDENT EFFECT-TILE candidates only. The
    labeled-bank protocol must be repeated from THIS starting state
    before any field graduates to contact-signature status.
  - REPEAT LABELED RUN (same start state): human threw 5 punches
    (missed 3rd); probe detected 6 rising edges (P1..P6 - one spurious,
    likely double-edge; mapping ambiguity noted). `D328/D330` again
    unchanged in ALL windows - confirmed dead in this context. New
    perfect discriminators (4 HIT / 0 MISS): 12 fields in
    `0x0203CD8C..0x0203CFA8` (+ near-perfect neighbors) - AGAIN inside
    the presentation zone. CROSS-SESSION PATTERN: every hit-correlated
    field so far lives in sprite/effect memory; the wolf's gameplay
    state must lie OUTSIDE the diffed zone (`0x0203C400..0x0203DE50`).
    NEXT: widen zone beyond 0x0203DE50 / below 0x0203C400 around labeled
    punches to find CPU-written wolf flinch state; or static route -
    locate impact-effect request caller from tile-block provenance.
  - FULL-MEMORY LABELED RUN CAPTURED (progress 13 addendum): root cause
    of arming failures found - mGBA had gone FULLSCREEN/borderless, so
    UI Automation saw an empty control tree ("Tools menu not found");
    windowed mode fixed it. New p004_full_label.lua probes raw A edges,
    dumps changed words across FULL EWRAM+IWRAM at T+1/+9/+17 per punch
    vs rolling reference. Session captured 16 edge events x 3 dumps.
    Human labels (post-levelup): miss 1st two, rest hit - but probe/edge
    count mismatch (16) leaves mapping uncertain. Strict all-HIT/0-MISS
    intersection: zero fields. NEXT: confirm true throw count with
    human, coalesce edges by presentation onset, rerun graded
    differential (>=N-1 hits, 0 misses); STOP-NOW.txt kill-switch now
    ends capture instantly when human says done.
  - SLOT-1 FULL-MEMORY LABELED SESSION (progress 13 addendum): fresh
    working copy `slot1-working.ss1` (sha16 D084E8D5ABB91830); human
    labels: 11 throws, MISS=1,2,9, rest HIT. Probe saw 12 edges (one
    spurious - known artifact). GRADED RESULT: 79 fields with >=6/8
    hits and 0/3 misses; 76 are presentation-zone, **3 are IWRAM**:
    `0x03006F48` (6/8), `0x03006F50` (6/8), `0x03007C50` (7/8) - first
    non-presentation hit-correlated mutations ever captured. Likely
    stack-resident locals of a combat routine (stable call depth).
    NEXT: single Z2 watchpoint on 0x03006F48 during armed human punch
    -> writer PC -> containing function = candidate contact/damage
    routine. All EWRAM hit-correlated fields so far remain
    presentation-only.
  - 0x03006F48 WRITER CAPTURED - CLASSIFIED NOISE: single Z2 during a
    human-confirmed landed punch produced 14 stops. ALL writers execute
    from IWRAM-resident code (PC `0x0300026C`/`0x03000280`/
    `0x03000ED4`/`0x03000EE8`; LR `0x030001F4`/`0x03000E5C`; constant
    SP `0x03006B1C`) writing drifting single bytes
    (`0x4e`,`0x4d`,`0x5f`,`0xd0`,`0x40`). Classification: frame-
    counter/bookkeeping maintenance by a RAM-executed handler; its
    bank correlation was a dump-phase alignment artifact. Per decision
    tree -> next target `0x03007C50` with the same single-watchpoint
    method. Note for Stage B design: IWRAM candidates from dump-phase
    sampling need writer capture BEFORE being treated as leads.
  - 0x03007C50 WRITER CAPTURED - REAL ROM CODE, COLLISION RAYCAST:
    single Z2 during landed-punch session (mGBA closed early but 120
    stops captured first). Writers are ROM Thumb code alternating in a
    loop: PC `0x0803B68C`/`0x0803B69A`, plus `0x0803B590`/`0x0803B66E`;
    **LR = `0x020363AC` (EWRAM-resident caller)**; args include two
    adjacent actor pointers `r1=0x0203C7C8`, `r2=0x0203C7C4`; written
    values are signed word pairs (delta-like). STATIC ID: containing
    function **`FUN_0803B4FC`** (body `0x0803B4FC..0x0803B6E9`) is a
    dual ray-march against map collision via `FUN_08046AA4` (point
    query on `*param_2+0x54` room data), up to 255 steps, storing the
    clamped endpoint to `param_1+0xC/+0x10`; picks ray by distance to
    target `(param_7,param_8)`. CLASSIFICATION: wall-collision clamp /
    line-of-sight utility - plausibly invoked for hit knockback
    repositioning or AI approach, called through an EWRAM function
    pointer. Stack slot 0x3007C50 = its local. NEXT: capture r0/param_1
    at these writers (CSV column gap), identify EWRAM caller chain at
    0x020363AC, decide knockback-vs-AI provenance.
  - PROVENANCE PARTIAL (progress 13 addendum): fixed r0 capture + LR-
    region dump. param_1 = STACK-LOCAL output struct (`r0=0x03007C48/`
    `C30`) - FUN_0803B4FC is a pure utility (clamp movement vs walls);
    r1/r2 = per-frame actor-struct pairs from the presentation zone.
    The EWRAM "LR site" `0x020363AC` contains ZEROS flanked by a
    dispatch-record pair (`0x0800EBE0` ROM ptr, `0x3001D4D0` IWRAM
    ptr) - the call is made by TABLE/SCRIPT DISPATCH that loads LR
    manually, not ordinary BL. Cap removed permanently after repeated
    budget-exhaustion auto-closes (hot field = stop cap burned in
    seconds; the maintainer directive: no budgets). NEXT: unlimited run, dump
    WIDER EWRAM code region (0x02036000..0x02037000) BEFORE first
    write, find dispatch interpreter owning record {0x0800EBE0,
    0x3001D4D0}.
  - EWRAM CALLER REGION DUMPED (progress 13 addendum): live 4KB read of
    `0x02036000..0x02037000` via one-shot GDB probe (`dump_ewram.py`,
    chunked `m` reads - stub rejects >=0x400 per packet). Nonzero span
    `0x020363A4..0x02036870` = REAL COPIED CODE/data in EWRAM. Record
    confirmed: `0x020363A4`=word `0x0800E0EB` (ROM Thumb ptr ->
    0x0800E0EA), `0x020363A8`=word `0x03001D4D4`, `0x020363AC`
    halfword `0xE000` (Thumb unconditional branch) = the LR landing
    site. Shape matches a TRAMPOLINE/dispatch record rather than a
    normal call frame. NEXT: disassemble `0x020363AC..0x02036870` as
    Thumb from the saved dump (`ewram-caller.bin`) to find the BL into
    `FUN_0803B4FC`; statically inspect ROM `0x0800E0EA`; identify the
    interpreter that owns/copies this block. Session corpus: 312 writer
    stops across varied play confirm `FUN_0803B4FC` runs CONTINUOUSLY
    (every-frame utility), further weakening any hit-specific reading.
  - DISPATCH STATIC RESOLUTION - FUN_0803B4FC CLOSED AS FALSE LEAD
    (progress 13 addendum): ROM @`0x0800E0EA` is a bare epilogue
    (`str r1,[r0,#0x28]; pop {r4,r5}; bx lr`) - the record word
    `0x0800E0EB` is a CONTINUATION/tail address, not an entry. NO
    aligned ROM literals reference the record, block base, fnptr, or
    IWRAM ptr -> all addresses are computed at runtime => interpreter/
    copy-driven construction CONFIRMED (INFERRED). Dump was taken at
    idle post-load; block contents are likely rebuilt per area/load,
    so byte-level trampoline reconstruction from this snapshot alone
    is unreliable. CLASSIFICATION: FUN_0803B4FC = generic per-frame
    wall-clamp utility dispatched by an interpreter for actor movement;
    NOT hit/knockback-specific. All three non-presentation
    discriminators from the graded bank (6F48/6F50/7C50) are now
    rejected as leads. STRONGEST NEXT TARGETS: (a) locate the WOLF
    gameplay object by widening labeled-bank capture beyond
    `0x0203DE50` (its flinch/AI mutation must be CPU-written
    somewhere); or (b) execution-trajectory diffing (PC samples)
    between human-labeled HIT and MISS frames. Presentation-zone
    discriminators remain valid CLASSIFIERS but carry no provenance.
  - WOLF CONTROLLER LOCATED (progress 13 addendum): regraded full-
    memory corpus with clean labels (miss 1,2 / hit rest) surfaced
    `0x03003488` = engine actor-slot pointer that swaps from player
    block `0x0203DEAC` to wolf-side `0x0203C7A0/C8D4/C934..` on every
    landed punch (10/10 hits, 0/2 misses). Neighborhood mining:
    **wolf sprite/anim controller at `0x0203C8C8..0x0203C94x`** -
    8/10 hits, 0 misses, receiving ROM clip pointers
    (`0x0804BC98`, `0x0804A710`, `0x08049DF0`) = CPU-written flinch
    clip installs. `0x203CAD0` also 10/10 (tile junk). Watchpoint now
    armed on `0x0203C8DC` (clip-slot) - next session: writer PC ->
    routine switching wolf into flinch -> upstream contact decision.
    Also noted: `0x20366EC` packed s16 pairs change 10/10 hits 0/2
    miss = probable screen-shake BG scroll (presentation, unproven).
  - ANIM INSTALLER FAMILY PINNED (progress 13 addendum): ROM literal
    hunt shows flinch clips installed by code at
    **`0x080188xx..0x080192xx`** (literals `0x0804A710`@`0x0801923C`,
    `0x0804BC98`@`0x0801894C`; earlier runtime catches `0x080188C4`,
    `0x0801891C`, `0x080190D0` same family). Prologue scan found
    candidate entries (`0x08019 20F/1E9/1C7`, `0x08018 937/921/90B/
    8CB`); Ghidra seeds created but bodies empty under `-noanalysis`.
    NEXT ITERATION (no human needed): rerun headless WITH analysis
    enabled for these seeds -> callers of the installer family ->
    find the caller passing FLINCH clip id on hit frames -> upstream
    contact decision. This is the current strongest P-003 thread.
  - TOOLING AUDIT REQUIRED BEFORE NEXT STATIC STEP (progress 13
    addendum): two scripting defects found and one fixed. (1) FIXED:
    BL scanner had Python precedence bug (`h1 & 0xF800 == 0xF000`
    parses as `h1 & (0xF800 == 0xF000)` = always False) - all prior
    "no direct BL callers" results were vacuous; corrected scanner
    still shows no direct BL callers for the wrapper entries (now a
    REAL negative), consistent with pointer-based dispatch.
    (2) UNRESOLVED: prologue-scan candidate dumps disagree with direct
    byte reads at the same addresses (e.g. claimed `b570` at
    `0x0801920F`, direct read says `05 b5 1c c0`). Canonical ROM hash
    verified; reader bug suspected in the scan's address arithmetic.
    NEXT: rewrite prologue/decoder scripts with single shared
    addr<->offset helpers + assertions, re-derive installer function
    boundaries, then caller recovery via corrected tools. Do not trust
    any pre-audit disassembly addresses from this iteration.
  - ENEMY AI STATE MACHINE LOCATED (progress 13 addendum, CONFIRMED):
    clean-read static pass found the behavior-table region
    `0x086FC000..0x08702000` (~2K+ code pointers). NODE LAYOUT decoded:
    arrays of 2-3 handler fn-ptrs (the installer wrappers, e.g.
    {0x0801890B, 0x08018921, 0x08018937}), an id/param word
    (0x11/0x12/0x13...), links to other nodes, and cross-links into
    `0x08029D14`-style handlers. Table ROOT literal `0x086FD9D0`
    referenced by ~12 functions across the `0x0802xxxx..0x0804xxxx`
    combat/AI cluster; early-engine readers at entries ~`0x0800CA0A`,
    `0x08004A88`, `0x0800446C`. REINTERPRETATION (INFERRED): the old
    m1/m5/ctor-lit addresses (`0x08029ED8`, `0x08029FE6`,
    `0x080342AE`) sit inside THIS AI machinery - the "attack object"
    was likely an enemy ATTACK state of the table machine, explaining
    why normal punches never executed it. NEXT: decompile ~
    `0x0800CA0A` (state runner), find the HURT/flinch state transition
    for the wolf = the contact decision; then downstream damage write.
  - STATE-RUNNER PARTIAL DECODE (progress 13 addendum): manual Thumb
    decode of `0x0800CA0A..0x0800CB10` - function performs bounds/
    collision checks via point-query `0x08046AA6` and signed range
    compares, consumes table root `0x086FD9D0` from its literal pool,
    calls `0x08009930`/`0x0800C912`; Ghidra createFunction fails here
    (conflicting flow) so manual decoding required. TOOLING NEXT:
    `pip install capstone` into .venv for proper Thumb disassembly
    (hand-decoding too slow/error-prone); then decode state-runner
    fully, find node-dispatch loop, locate HURT-state transition =
    contact decision. Concurrent-session WIP note: untracked failing
    test `tests/integration/test_local_thumb_decoders.py` (private-ROM
    dependent) appeared mid-loop from another session - preserved
    untouched, excluded from my gate runs (tests/unit green 310).
  - NODE LAYOUT FULLY DECODED (progress 13 addendum, CONFIRMED):
    behavior node = fn[3] `{0x08018 90A, 0x08018920, 0x08018936}`
    (GENERIC shared handlers - enter/tick/exit shape), `+0x0C` =
    state-id (chains: 1,2,3,4 / 6 / D,E,F), secondary fn array
    {0x08018F90, 0x0801900A, 0x08019042}, tail links to adjacent
    nodes/state-data. All states SHARE handlers - per-state behavior
    comes via linked DATA blocks. Flinch clip `0x0804BC98` literal sits
    in this handler family's pool (`@0x0801894C`) - clip selection
    flows from STATE DATA. ALSO REJECTED: `0x03003488` = sprite-
    pipeline working slot (writers `0x0803D50A/544/5A4`) - false lead
    #4. NEXT: decode handler family vs state-data clip selection;
    find dispatcher loop;     HURT-state entry = contact decision.
  - WOLF GAMEPLAY OBJECT FOUND (progress 13 addendum, STRONG):
    decrement-mining surfaced `0x03007BBC` rotating pointers across
    three combat-object blocks per punch window. Two identified:
    `0x0203DBB0` = PLAYER combat object (max-HP candidate 0x203DBB4 =
    +4 inside it), and **`0x0203D504` = WOLF combat object**: its +0
    state-vtable word SWAPS `0x0804C484 <-> 0x0804E454` on landed
    punches (h=3 direct, plus +4 byte jitter h=9 m=0), zero on
    misses - first actor-owned non-presentation hit-correlated state
    transition. Layout hypothesis: +0 vtable, +4 state byte/timer.
    ALSO: `0x0203DECC` third combat block (second wolf?). NEXT: Z2 on
    `0x0203D504` vtable word during labeled punches -> transition
    writer PC -> state-switch routine -> damage flow upstream.
    Static follow-up: inspect vtables 0x0804C484 / 0x0804E454.
  - WOLF STATE-TRANSITION WRITERS CAPTURED (progress 13 addendum,
    CONFIRMED runtime): Z2 on `0x0203D504` during two-wolf fight-to-
    death produced 4 stops, all ROM-code state installations writing
    DIFFERENT state-vtable values into the wolf object:
    - `PC 0x0800E868` (LR `0x0800F7FF`) wrote `0x0804C888`
    - `PC 0x0800EC3E` (LR `0x0800E8DB`, i.e. chained from the previous
      function) wrote `0x0804AC20`
    - `PC 0x0800EC90` (LR `0x0803D6C9` - sprite-side caller) wrote
      `0x08049680`
    - `PC 0x0800ECA6` (LR `0x080114F5` - the animation-CALLBACK family
      `FUN_08011944` neighborhood!) wrote `0x0804E454` with r1=3
    INTERPRETATION: wolf combat object runs a VTABLE-SWAPPED state
    machine; installers live in `0x0800E800..0x0800ED00`; one
    transition fires from an animation-completion callback (hit anim
    ends -> next state), another from the sprite/death side. This is
    the executable contact/reaction chain - NO more correlation
    guessing. NEXT (static): decompile functions containing
    `0x0800E868`, `0x0800EC3E/ECA6`, and caller context `0x080114F5`;
    identify which state = HURT vs DEATH vs AGGRO; trace the damage
    operand upstream through the installer arguments.
  - STATE INSTALLERS DECOMPILED (progress 13 addendum, CONFIRMED):
    - `FUN_0800E85E` (`0x0800E85E..E85`) = wolf object TEARDOWN/
      DESTROY: unlinks from a doubly-linked actor list (+0x1F0/+0x1F4/
      +0x1F8/+0x1FC neighbor ptrs!), clears children (+500), releases
      point-query obj, then calls `FUN_0800EC34(obj, flag)`.
      Callers: `FUN_0800F76E` and `FUN_0800E6F8` - THE DECIDERS of
      wolf removal (death/respawn).
    - `FUN_0800EC34` (`0x0800EC34..CAF`) = state REINIT: swaps vtable
      (DAT_0800EDDC then DAT_0800EDF0 - matches observed
      C484<->E454-class vtables), frees old resources
      (`FUN_0804FE20`), rebinds point-query objects (+0x28/+0x30),
      and calls `FUN_0801142A(*DAT_0800EDE0)` when a ushort at
      obj+0xC differs from a table value.
    - `FUN_0801142A` (`0x0801142A..11551`) = CENTRAL SEQUENCER
      (19 callers across engine!): byte-array work area,
      `(param_2>>1)+0xC00` indexing, 10-byte records chained by
      0xFF-terminated next-indices - plays scripted
      animation/effect/event sequences.
    PROVENANCE CHAIN NOW EXECUTABLE: hit -> wolf anim plays ->
    completion callback -> `FUN_0800EC34` re-init (state swap) ->
    on death `FUN_0800E85E` teardown via deciders
    `FUN_0800F76E`/`FUN_0800E6F8`. NEXT: decompile those two deciders
    to find the HP/death condition test; trace their caller passing
    damage;     identify the HURT-state installer vs DEATH installer.
  - DECIDERS DECOMPILED (progress 13 addendum, CONFIRMED):
    - `FUN_0800F76E(obj,flag)` = REMOVE-ACTOR-from-active-list:
      unlinks obj from global array `DAT_0800F914` (count+entries),
      optional body-check via `cand_point_in_body_0800FDFA`, then
      teardown `FUN_0800E85E`. Byte at obj+0x291 gates an extra
      body-register write.
    - `FUN_0800E6F8(obj,flag)` = remove from second global list
      `DAT_0800E750`. CALLERS: `FUN_08039182` and
      **`candidate_player_method0_08010B80`** - THE PLAYER-SIDE METHOD
      removes actors! Strong signal that the player melee/kill flow
      runs through 0x08010B80.
    NEXT (highest priority): decompile
    `candidate_player_method0_08010B80` and `FUN_08039182`; find the
    damage/HP test upstream of the removal call; that branch IS the
    HIT-vs-DEATH-vs-KNOCKBACK decision. Then link back to the labeled
    hit frames for the per-hit non-lethal path (hurt-state installer).
  - DUAL PROBE SESSION RESULTS (progress 13 final addendum): register
    decode fixed (decode_register_payload); session captured exactly
    TWO removal stops - wolf `0x0203D504` and PLAYER `0x0203DBB0`
    (player removal = area transition) - but **ZERO writes to wolf
    +0x74 (D578) despite landed punches**. Combined with slot rebinding
    evidence: the `0x0203D504` object is a REUSED SLOT; its occupant
    changes across spawns, so cross-session "+74: 100 -> 92" compared
    DIFFERENT actors. Wolf HP field remains UNLOCATED via absolute
    addresses. NEXT SESSION PLAN (fresh context, high confidence):
    (1) single-wolf focus - do not transition areas mid-capture;
    (2) per-tick FULL object dump of whichever combat object receives
    flinch-wrapper entries (r1 of Z0-on-0x8018920E-family stops gives
    actor ptr directly); (3) within one continuous same-object span,
    HP = the word decrementing on labeled HIT windows only; (4) Z2 on
    that word -> damage writer PC -> P-004 closure. Alternative
    faster route: at a removal stop, dump BOTH wolves' objects while
    ALIVE by scanning r0-neighbors (actor structs cluster).
    are generic per-object DESPAWN methods called THROUGH VTABLES
    (`candidate_player_method0_08010B80` = player's own despawn used
    on map transition; `FUN_08039182` = generic enemy despawn) - so
    the kill decision lives in whoever CALLS obj->despawn after a
    HP<=0 test. BL scanning cannot find vtable-dispatched callers.
    NEXT ITERATION PLAN (fresh session): (1) locate the state vtables
    (dump words at 0x0804C484/0x0804E454/0x0804C888/0x0804AC20/
    0x08049680 - each should contain the despawn + tick + hurt method
    ptrs for that state); (2) find ROM code holding those vtable
    ADDRESSES as literals = the state-machine core that dispatches
    them; (3) decompile the dispatcher's damage branch (HP test);
    (4) connect to wolf object 0x0203D504 field +0x4 byte jitter as
    the likely HP/state byte. All tooling ready: disasm.py,
    find_callers.py, AutoP3Func.java.
  - REL-DISPATCH TABLES CONFIRMED (progress 13 addendum, CONFIRMED):
    wolf object `+0` points to RELATIVE-OFFSET function tables (entries
    = signed deltas from table base). Decoded targets:
    - table[0] = despawn/destructor slot: `0x804C484[0]->FUN_0800F76E`,
      `0x804C888[0]->FUN_0800E85E`, `0x804AC20[0]->FUN_0800EC34`
    - table[1] shared -> `0x0804F53D`; entries [2..5] state-specific.
    State transition = swapping obj->+0 between tables (observed
    C484<->E454 on hits). DISPATCHER = generic code doing
    `call obj->[0][k]` - still to locate. This mirrors the veneer/
    offset-table convention at `0x0804A4B8` (same engine idiom).
    P-003 CHAIN STATUS: A press -> punch presentation -> HIT/MISS
    (classifier: wolf flinch clips) -> wolf combat obj 0x0203D504
    vtable swap via FUN_0800EC34-family installers -> death ->
    FUN_0800F76E removal. MISSING LINK: damage application + the
    dispatcher loop. Fresh-session resume at step (1) of previous
    dispatcher loop; HURT-state entry = contact decision.
  - WOLF HP CANDIDATE TESTED AND REJECTED (progress 13 addendum):
    fresh-object read showed `0x0203D578 = 0x64`(100) - attractive HP
    value. Corpus check: D578 flips between patterns
    (`3d63e00<->3222100`) on hits, becomes tile-junk near death
    (`2fc0e1cc`) - it is a GRAPHICS/FRAME pointer slot, not HP.
    Wolf current-HP field remains UNLOCATED. CRITICAL NEW OBSERVATION:
    P11 window (t=176) shows the WHOLE 0x203D504 object being RESET
    (+4->1000000, +0x74->0...) = despawn/death signature, and earlier
    sessions showed wolf controller addresses MOVING across punches
    (`C7A0/C8D4/C934`). WORKING EXPLANATION (INFERRED): combat-object
    slots get RE-BOUND to different actors over time, so fixed-address
    grading scatters real signals. FUTURE WORK: track wolf identity via
    the `0x03003488` actor-slot rotation chain instead of absolute
    addresses, or capture with only ONE wolf alive. Damage application
    path remains the open P-004 question.
  - WOLF +4 WRITER CAPTURED - SEQUENCER-DRIVEN (progress 13 addendum,
    CONFIRMED): single writer `PC 0x080101C8` (LR `0x080115DB`) writes
    an oscillating byte (e3<->dd sine-like, r2=4 r3=0xE constant) into
    `0x0203D508`. Classification: animation-driven oscillation (bob/
    hover), NOT HP - another dump-phase artifact explained. BIG
    STRUCTURAL FINDING: LR lands inside the `FUN_0801142A` SEQUENCER
    family - wolf combat objects are driven by the central SEQUENCER
    (19 callers, byte-array work area, 10-byte chained records).
    WORKING MODEL (INFERRED): actor behavior = scripted sequences;
    damage/contact likely applied via SEQUENCE COMMANDS at scripted
    frames (explains why no persistent field diverged at fixed offsets
    on hits vs misses in sampled dumps). NEXT: decode sequencer record
    format + command set (entry `FUN_0801142A`, worker `0x080101C8`,
    `LR 0x080115DB` region), find the DAMAGE/OVERLAP command; then the
    contact decision = a sequencer branch comparing attacker/target
    overlap. Writer containing function entry ~= `0x0801154F`
    (prologue scan; verify).
  - SEQUENCER ENTRY DECODED (progress 13 addendum): `FUN_0801142A` =
    RECORD RELINKER, not a script VM - it moves 10-byte records
    between linked chains in a work array (`[+6]/[+7]` = next/prev
    indices, 0xFF = none; `[+4]` accumulator; calls `FUN_0801137C`
    twice per move). Shape matches a queue manager (effects/sounds/
    scheduled tasks), weakening the "damage via sequence commands"
    model. The wolf+4 oscillation thread may terminate here (bob
    driven by a task queue). NEXT SESSION SHOULD DECIDE: continue
    queue thread vs pivot to (a) full Ghidra analysis run on the
    calibrated project (previous attempt exceeded 1h timeout - run
    headless overnight-style or restrict analysis scope), then use
    real xrefs to find who calls the rel-table wrappers indirectly;
    or (b) runtime: Z2 on `FUN_0801890A` (node ENTER handler!) during
    labeled punches -> catches every state entry including HURT ->
    LR reveals the dispatcher directly. Option (b) is cheap and
    high-signal: enter-handler fires rarely (only on state changes).
  - DISPATCHER FOUND (progress 13 addendum, CONFIRMED): Z0 on
    `FUN_0801890A` (node enter) during wolf fight -> 146 stops.
    Call-site LRs: **`0x080188B5`** (main dispatcher, x83),
    **`0x08029FF1`** (x35 - INSIDE the old `0x08029FE6..A026`
    "ctor_lit" function => that cluster IS part of the state
    dispatch machinery after all!), `0x08018FC9` (x27). Args: r0 =
    ROM node-def pointers `0x08706A28..0x08706B44` (wolf behavior
    definitions!), r1 = actor combat object alternating
    `0x0203D504`(wolf)/`0x0203DBB0`(player). CONFIRMS: player AND
    wolves are nodes of the same table machine; wolf node defs at
    `0x08706A2C-B44`. NEXT: decompile dispatcher fn containing
    `0x080188B5` (~entry 0x08018870-88x) and `0x08029FE6` body ->
    find state-id selection = HIT/MISS decision; then damage write.
    REFINEMENT: `0x080188B5` sits in node-type handler `0x080188A4`
    (point-test enter variant allocating 16-byte instance) - these
    0x080188xx-90xx functions are PER-NODE-TYPE handlers, so the TRUE
    dispatcher (which walks an actor's node list and calls type
    handlers) is still one level up - find code calling
    `0x080188A4`/`0x0801890A` indirectly via their addresses as DATA
    (they appeared as fn-ptrs INSIDE behavior nodes: e.g. secondary
    arrays {0x08018F90, 0x0801900A, 0x08019042} and node words).
    So node defs CONTAIN handler ptrs -> two-level design:
    interpreter walks node def -> calls its type handlers with
    (node, actor).     Decompile `FUN_08029FE6` fully next - it already
    showed dispatcher LR behavior (`0x08029FF1`).
  - NODE-ENTER CALL SITES CHARACTERIZED (progress 13 addendum): 44
    enter-handler stops during wolf fight. Three call sites:
    `LR 0x080188B5` (main), `LR 0x08029FF1`, `LR 0x08018FC9`. Args:
    r0=node def (`0x08706A28-B44`), r1=actor combat object
    (wolf `0x0203D504` / player `0x0203DBB0` alternating). KEY
    OBSERVATION: several LRs are ODD (`0x08029FF1`) => the caller
    sets LR to a THUMB CONTINUATION POINTER rather than a normal BL
    return - i.e., an INTERPRETER loads LR with the next descriptor
    after a landed hit IS the HURT transition.
  - DISPATCHER BODY LOCATED (progress 13 addendum): LR `0x08029FF1`
    resolves to REAL sequential code at `0x08029FF0` directly above
    the enter-handler `FUN_08029FE6` - i.e., one large function spans
    ~`0x08029Exx..0x0802A0xx` containing: an AABB overlap test
    (4 signed compares -> bool, ends `0x8029FE2`), inline calls to
    node-enter handlers (`FUN_08029FE6`, and via LRs to
    `FUN_0801890A` etc.), and 12-byte instance allocation. THIS IS
    THE BEHAVIOR INTERPRETER/OVERLAP-CONTACT EVALUATOR for actor
    states. NEXT SESSION (fresh context): find its entry via wider
    prologue scan (~0x08029B00-9F0), full capstone decode, identify
    (a) which overlap = punch contact vs movement, (b) the branch
    selecting HURT node id on contact, (c) the damage operand source.
    Then P-003 chain closes: A -> punch seq -> interpreter overlap
    check vs wolf combat obj -> HURT node enter -> clip swap ->
    (P-004)     damage write in same path.
  - **P-003 SOLVED (progress 13 addendum, CONFIRMED runtime):** stack-
    walk capture during labeled punches returned nested return chains
    proving the full contact path. Flinch-wrapper stops showed chains
    `0x80342EB -> 0x8018907 -> 0x804ECBD` where **0x080342EB lies
    INSIDE m1 (`0x080342AE..34305`) - the old attack-object phase
    machine directly invokes the flinch/HURT-node enter on landed
    punches**. Other stops chained through the indexed dispatcher
    (`0x0800AA5F`) with wolf node defs + state table (`0x087102C4`).
    RESOLUTION OF THE EARLIER CONTRADICTION: the armed Z0-on-m5 run
    that "never fired" was a context/timing failure, not evidence -
    m1/m5 WERE the melee path all along. FULL CONFIRMED CHAIN:
    A press -> attack object created -> m1 phase machine ->
    m5 AABB reach test (melee-adjusted target rect) -> HIT branch ->
    flinch wrapper `0x0801920E` -> wolf HURT node enter ->
    clip install at controller. REJECTED-LEADS REHABILITATED:
    `candidate_attack_object_dispatch_08049DF0`, m1, m5 all restored
    to the canonical melee path.
  - P-004 handover point: damage operand lives in the m1 -> HURT-enter
    argument flow (m1 dispatches owner vtable methods with target;
    m5 computes direction byte at target+0x10). Next session: decode
    m1's full body for the damage constant/source passed alongside
    the HURT transition; watchpoint on wolf obj fields during ONE
    labeled punch with m1-region breakpoints isolates the exact HP
    write.     Wolf combat obj = `0x0203D504`; player = `0x0203DBB0`.
  - M1 FULLY DECODED (P-004 Track A, CONFIRMED byte-exact):
    ```
    m1(obj, target):                  ; 0x080342AE
      table = [obj+0]                 ; rel-table ptr
      r2 = table + [table+0x14]       ; resolve rel entry [+5]
      res = 0x8046AA4(r?, target, r2) ; overlap/query w/ resolved data
      if res == 0 -> 0x080342EC:
          if [obj+8](phase) != 0: phase=0
            owner=[obj+4]; vt=[owner]
            call [vt+8](owner, target)   ; arm B: owner slot +8
          return 0
      else (res != 0):
          if phase == 0: phase = 1
            owner=[obj+4]; vt=[owner]
            call [vt+0](owner, target)   ; arm A: owner slot +0
          fallthrough pop
    ```
    Attack object layout CONFIRMED: +0 rel-table, +4 owner actor,
    +8 phase flag. Arms call OWNER ABSOLUTE-VTABLE methods with the
    TARGET pointer as argument - damage flows through those methods.
  - CRITICAL REFINEMENT: the stack-chain word `0x80342EB` (odd) is a
    CONTINUATION into the code immediately AFTER m1's pop - i.e.
    function `0x080342EC..0x08034305` (arm-B body, starts right at
    m1's exit) is a SEPARATE handler dispatched back-to-back with m1
    via LR-as-continuation. The attack-object rel-table lists these
    as consecutive entries. Flinch-wrapper invocation observed from
    this continuation context.
  - PLAYER/WOLF SHARED TABLES: player obj 0x203DBB0 and wolf
    0x203D504 both carry +0 = same state-table family
    (`0x0804C484`<->`0x0804E454` swaps observed); rel-table entries
    decoded earlier: C484[0]=despawn(F76F),[1]=0x804F53D,
    [2]=0x0800FAE7,[3]=0x0801003B,[4]=0x0800EF95,[5]=0x0800F3F9;
    E454[0]=0x08052EC9,[2]=0x080501E1,[3]=0x0804FC41,[4]=0x08046CAD,
    [5]=0x0804FE9D. Arm A calls [vt+0], arm B calls [vt+8] (=entry
    index +2 in the rel-table = 0x0800FAE7 / 0x080501E1 pair).
  - NEXT (Track C/D): decompile owner-method targets 0x0800FAE7 and
    0x080501E1 (and slot+0 pair 0x0801003B / 0x08052EC9) with target
    pointer argument - ONE of these four contains the damage/HP write
    on the HIT arm. Then watchpoint the identified HP field during
    one labeled punch for writer PC confirmation.
  - ARM A RESOLVED (P-004 Track C, partial): rel-entry [+5] of C484
    -> Thumb handler `0x0800FAE6` (`push {r4,lr}; bl 0x800EF08;
    r0 += 0x238; bl 0x0800AB0C`) - passes ACTOR+0x238 into
    `FUN_0800AB0C`. Adjacent big switch fn (~0x0800FAF6) branches on
    command values (2/0x16/0x19) calling
    `cand_body_bounds_0800FE78` - the melee/body-rect comparison
    region. NOTE: rel-table targets must be disassembled at EVEN
    addresses (thumb bit stripped) - odd-start reads decode garbage.
    NEXT: decode `FUN_0800AB0C` (actor+0x238 consumer - candidate
    damage/hit application) and map the switch commands.
  - DEEPER LAYER (progress 13 addendum): `FUN_0800AB0C` = another
    dispatch wrapper - indexes an 8-byte-stride table by [r4+4],
    resolves ptr, calls `0x8046AA4` yet again. The engine is a
    MULTI-LEVEL command interpreter: m1 -> rel-entry handler ->
    actor+0x238 -> indexed table -> deeper call. Static layer-peeling
    has diminishing returns. DECISION: next runtime session captures
    the BOTTOM directly - Z2 watchpoints on wolf combat obj
    (`0x0203D504..+0x84` full range, or targeted +4/+74 fields) during
    ONE labeled landed punch, WITH the proven stack-walk logging ->
    writer PC + full dispatcher chain to the top in one capture. That
    closes P-004's writer-provenance requirement in a single run.
  - NEXT-SESSION PROBE SPECIFIED (progress 13 addendum): at each
    `FUN_0801890A` stop, also DUMP THE STACK (`m<sp>,40`) - nested
    return addresses in the stack walk the full dispatcher call chain
    (LR alone only shows the innermost continuation). Add to
    gdb_writer_watch.py: after regs, read 16 words at SP and log them;
    ROM-range words = return sites -> containing functions via
    disasm.py. This resolves the top-level selector without any new
    tooling. Ghidra route permanently abandoned for this task (OSGi
    cache poisons script recompiles even after deletion; capstone +
    manual decode authoritative).
  - WOLF STATE TABLE LOCATED (progress 13 addendum, CONFIRMED):
    indexed `{primary-node, secondary-node}` pairs at
    `0x0871027C..0x087102D4+`, including the entry
    **`{0x08706B7C, 0x08706A64}` @ `0x087102AC` containing the
    flinch-family node** (`0x08706B7C` = runtime-captured r0 on flinch
    wrapper entries). Other entries map ids 762/773 states and shared
    defaults (`0x080716F4`). This is the wolf family's
    state-index->behavior-node table consumed by the indexed
    dispatcher (`FUN_0800AA4A` pattern). REMAINING FOR P-003 CLOSURE:
    (1) scan back from 0x87102AC for the table's true base and entry
    count; (2) identify which actor field holds the current state
    INDEX and who writes it on landed hits (= HIT-vs-MISS decision);
    (3) decompile that writer -> damage operand source = P-004
    handoff. All tooling ready (disasm.py,     find_callers.py,
    corpus analyzers).
  - TABLE STRUCTURE CORRECTION (progress 13 addendum): the
    `0x0871027C+` "entries" are part of one CONTIGUOUS LINKED NODE
    GRAPH spanning `~0x086FD900..0x08710400` - nodes as pairs of
    pointers into `0x08706xxx/0x086FDxxx` def clusters plus shared
    default `0x080716F4`. NOT an indexed array. The behavior system
    is a LINKED STATE GRAPH walked by the (still unlocated)
    interpreter. Remaining closure work unchanged: interpreter entry +
    HURT-transition branch + damage operand. Recommend fresh-session
    full decode starting from `FUN_0801890A` callers' continuation
    glue (`0x08029FF0`, `0x08018FC9` regions) upward.
  - KI-VS-MELEE FLINCH RUN CAPTURED (progress 13 addendum): Z0 on
    flinch wrapper `0x0801920E` during human session (ki blast landed,
    then punch) -> 13 stops. ALL have r1=`0x0203DBB0`; TWO alternating
    call-site/node pairs: (`LR 0x0800AA5F`, node `0x08706B7C`) and
    (`LR 0x08018FC9`, node `0x08706BF8`). OPEN QUESTION: is
    `0x0203DBB0` the PLAYER (max-HP adjacency) or the WOLF (ki+melee
    both landing on it)? The alternating two-node pattern entered via
    two different callers suggests a state PAIR (e.g. hurt<->recover,
    or action<->idle toggle). NEXT: decompile callers `0x0800AA5F`
    (containing fn near engine core 0x0800Axxx!) and `0x08018FC9`;
    dump node defs `0x08706B7C`/`0x08706BF8` ids+links; determine
    actor identity of `0x0203DBB0` decisively (check whether its
    fields track player position 0x03001C34->+0x1A0 during movement).
  - CALLER 0x0800AA5F DECODED (progress 13 addendum): containing fn
    `0x0800AA4A` does `r1*8` indexing into an 8-byte-stride STATE
    TABLE (literal [pc,#0xfc]) -> node-def ptr -> point query ->
    flinch-wrapper enter. CONFIRMED: state-index -> node-def lookup
    dispatch (indexed state machine). NEXT: dump that state table
    (base = word at pool ~0x0800ab50), map indices to node defs,
    find which index = HURT for wolves vs player, and decompile
    second caller `FUN_~08018FC9` context.
  - WOLF STATE GRAPH EXTRACTED (progress 13 addendum, CONFIRMED):
    node defs = `{fn[3] handlers, param=clip/state id, enter-variant
    ptr, links}`. Wolf nodes: ids `428`(enter 0x080188A9 point-test),
    `435` (r0 seen at runtime!), `436`, `437` (enter FUN_08029FE6
    point-query), `438`, `439`, `762`. FLINCH node identified:
    `0x08706A48` family (fns `0x0801920E/0x08018FDA/0x08019042`,
    param 2) - its wrapper's pool literal IS `0x0804A710`, the clip
    observed installed at the wolf controller ONLY on labeled hits.
    No static refs to the flinch node => entered via interpreter
    computation. CLOSING EXPERIMENT READY: Z0 execution breakpoint on
    wrapper `0x0801920E` during one labeled punch session -> the LR
    at the flinch stop = the HURT-transition decider -> decompile it
    -> HIT-vs-MISS branch -> P-003 closed + damage operand upstream
    for P-004 handoff.
  - WOLF NODE DEFS MAPPED (progress 13 addendum, CONFIRMED): wolf
    behavior defs at `0x08706A00..0x08706B6C`. Nodes = `{fn[3],
    param, links}` where param looks like an ANIMATION/CLIP id:
    nodes with generic fns carry params `0x2FA(762)`, `0x305(773)`,
    `0x1B3(435)`, `0x1B5(437)`, `0x1B8(440)`; special nodes:
    `0x08706A38` (handler `FUN_08029D14` + const `0x2710`=10000),
    `0x08706A48` -> fns {0x0801920E,...} param 2 (the FLINCH-clip
    family!), `0x08706A8C` (handler `FUN_08029FE6`, param 0x1B5),
    `0x08706AAC` (thumb ptr `0x080188A9` = point-test enter variant).
    Runtime r0=`0x08706A28` confirms THIS def set drives the fought
    wolves. NEXT SESSION: enumerate all wolf node ids/params in
    `0x087069xx..B6C`, correlate param values with observed flinch
    clip swaps, find which node id = HURT and what enters it.
  - HANDLER LIBRARY SEGMENTED (progress 13 addendum, CONFIRMED):
    `0x08029800..0x0802A100` = ~30 SMALL node-type handler functions
    (push/pop bounded), including **`0x08029ED8` = the old "m5"** -
    REIDENTIFIED: its tail (`0x8029FC0..FE2`) is the 4-signed-compare
    AABB overlap -> bool. So m5 IS an overlap-evaluator node handler
    (not presentation), just not exercised by the normal player punch
    in the tested context. No giant interpreter function exists in
    this range - it lives elsewhere (still unlocated). NEXT: find the
    dispatcher by scanning ROM for aligned DATA references to these
    handler addresses (they must appear in behavior NODE DEFS like
    `0x08706A2C` do); cross-ref which defs contain them; then find
    who walks those defs.
  - EWRAM STUB REGION DECODED (progress 13 addendum): the
    `0x020363A4..0x02036870` copied block = THUNK/VENEER POOL
    (`b target` stubs over nop sleds), NOT the dispatcher. LR landing
    there = caller returned through a veneer. Static idiom scans for
    the rel-table dispatch loop found nothing in early ROM; dispatcher
    remains UNLOCATED - possibly also ROM-indirect or in the
    interpreter-driven layer. RECOMMENDED NEXT EXPERIMENTS (in order):
    (1) runtime: Z2 on wolf obj `+4` byte (`0x0203D508`, hit-jitter
    h=9/m=0 small signed changes) during labeled kill run -> writer PC
    at damage moment; (2) static: capstone-decode
    `FUN_0800F76E`'s callers (who invokes removal = death decision);
    (3) locate rel-table dispatcher by scanning for `adds rX, rY`
    resolve-then-`bx` idiom across FULL ROM incl. high addresses
    (prior scan covered only <0x8030000).
  - CAPSTONE DEPLOYED (progress 13 addendum): `capstone 5.0.7` installed
    into .venv; reusable disassembler at
    `build/research/p003-exp/disasm.py` (`python disasm.py <addr> <len>`).
    First full decode: `0x0800CA0A` = mode-switched AABB TRIGGER CHECK -
    compares actor body rect (+0x14/+0x18/+0x1C/+0x20) against node-data
    rect via `0x8046AA6` point queries and signed range compares;
    consumes table root `0x086FD9D0`. Same check-shape as the
    transition-trigger system from VERTICAL-001 - behavior nodes use
    region tests to gate state transitions. NEXT: decode the node
    DISPATCHER that evaluates these checks and swaps handler arrays
    (find callers of 0x0800CA0A first), then map the wolf HURT node +
    its entry transition = contact decision.

- **P-003 progress 10 (2026-08-23), constructor-hunt false positive:**
  - The aligned word `0x08049DF0` at `0x0802A008` is CODE, not a literal
    (bytes `F0 9D 04 08` = `LDR r5,[sp,#0x3C0]` + next-instruction
    halfwords, inside function `0x08029FE6..0x0802A026` which is a small
    initializer reading `obj->+0xC`/`obj->+0x0` and storing to
    `obj->+0x1C/+0x20` - relationship to the attack object unclear).
  - No aligned ROM reference to `0x08049DF0` (or thumb-form `...DF1`)
    exists anywhere - the attack object's vtable pointer is installed by
    COPY/ADDITION from a template or parent object, not a direct literal.
    Consequence: static constructor hunt via literal scan is a dead end;
    the m1-caller chain must be reached via runtime capture (GDB Z0 at
    m5 fetch `0x08029ED8`, log r0/r1 per call = attack object + target)
    or by finding the attack-object LIST owner another way.
  - m5 geometry terminology per steering: the inequalities define the
    MELEE-ADJUSTED TARGET BODY RECT (x0-4 outward, x1+3 outward, y0
    unchanged, y1-6 reduced) tested against the plain player world body;
    canonical form preserved verbatim in progress 9.

- **P-003/P-004 progress 9 (2026-08-23), m5 exact hit geometry:**
  - Full decompile mapped (stack-slot to rect-field assignment). CORRECTED
    2026-08-31 from the static disassembly: the two rect buffers were
    previously assigned to the wrong actors. The proven assignment is
    - PLAYER rect buffer = `sp+0x2c, 0x30, 0x34, 0x38` via the global form
      `cand_body_bounds_0800FE78(&out)`: buffer built at
      `08029EF6 add r0, sp, #0x2c` then `08029EF8 bl 0x800fe78`, with r1 =
      the GLOBAL actor `[[0x0802A004]] = 0x03001B94` loaded at `08029EDE`;
    - TARGET rect buffer = `sp+0x1c, 0x20, 0x24, 0x28` via
      `cand_body_bounds_0800FE78(&out, target)`: buffer built at
      `08029EFE add r0, sp, #0x1c` then `08029F00 bl 0x800fe78`, with
      r1 = r4 = the `target` argument (`08029EFC adds r1, r4, #0`; r4 saved
      at `08029EDC`). So `x0t=[sp+0x1c], y0t=[sp+0x20], x1t=[sp+0x24],
      y1t=[sp+0x28]`.
    - The reach inequalities below are UNAFFECTED by this correction. They
      were derived from the registers the compare instructions actually
      read, not from these buffer labels; only the player/target naming of
      the two stack groups was wrong.
  - Gate: global `*DAT_0802a004 != 0` AND `*global != 0 -> +0x1CC != 0`.
  - **Initial reach test** (all strict `<`; TARGET rect expanded against
    plain player world body):
    `target.x0 - 4 < player.x1  &&  player.x0 < target.x1 + 3  &&
     target.y0      < player.y1  &&  player.y0 < target.y1 - 6`
  - **Direction resolution** (player center `(x0p+x1p)/2,(y0p+y1p)/2`;
    target center analogous):
    - `dx = playerCx - targetCx`, `dy = playerCy - targetCy`;
    - horizontal dominant (`|dy| < |dx|`): writes `*(u8*)(target+0x10) =
      2` if `dx < 1` else `3`;
    - else vertical dominant: `1` if `dy < 1` else `0`;
    - secondary rect test then confirms (horizontal: uses
      `target.x1+3`; vertical: `target.y1-6`).
  - **`target+0x10` = hit-direction byte**, same byte the body-bounds
    getter multiplies by 0x10 to select the body-table entry - getting
    hit sets the victim's direction byte. Encoding 0/1/2/3 semantics
    INFERRED (likely a down/up/left/right family).
  - Boundary semantics: strict inequality (half-open style, consistent
    with registry AABB). Player rect IS the ordinary world-body; melee
    reach = body-vs-EXPANDED-target-body (no separate hitbox).
  - Caller chain: **m1 (0x080342AE) dispatches obj.vtable[+0x14] = m5**
    with its own target argument; the target list lives in m1's caller
    (attack-object update loop) - next structural target.
  - Facing table (hit-direction written to target+0x10, INFERRED
    semantics): horizontal-dominant dx<1 -> 2, dx>=1 -> 3;
    vertical-dominant dy<1 -> 1, dy>=1 -> 0.
  - `0x08049DF0` is a **relative-offset dispatch table** (same format as the
    player entity vtable) with two identical 5-method groups; referenced by
    a literal at `0x0802A008` (constructor in the `0x08029Exx-0x0802A0xx`
    cluster).
  - Resolved methods (fetch addrs): m0 `0x080342A8` (zeroes obj+8),
    **m1 `0x080342AE` = attack phase state machine** (dispatches owner
    vtable`+0x14`; toggles phase flag obj`+8`; on transitions notifies
    owner via obj[1] vtable`+0x0/+0x8` and dispatches target vtable`+0x4`
    with the caller arg), m4 `0x08050F08`, **m5 `0x08029ED8` = the melee
    reach/target test**, m5b `0x08029ED8` group-2, slot[5] `0x08029ED9`
    region, slot[11] `0x080379B0`.
  - **`cand_49df0_m5_08029ED8(obj, target)` decompiled behavior** (the
    melee hit-region + target acquisition):
    - gates on global `*_DAT_0802a004` and its `+0x1CC` field;
    - `cand_body_bounds_0800FE78(&rA)` - PLAYER body (global form);
      `cand_body_bounds_0800FE78(&rB, target)` - candidate target body;
    - expands the target rect by per-edge margins
      (`x0-4, y0+0, x1+3, y1-6` shape) - CORRECTED 2026-08-31; the earlier
      `x0-4, y0+3, x1, y1-6` wording transposed the `+3` from x1 onto y0.
      Disassembly evidence: `08029F2A adds r1, #3` where r1 = `[sp+0x24]` =
      x1t, consumed at `08029F38 cmp r2, r1`, so x1 IS expanded by +3;
      and y0t is loaded at `08029F32 ldr r6, [sp, #0x20]` and compared at
      `08029F3E cmp r6, r2` with nothing writing r6 in between
      (`08029F34 bge`, `08029F36 ldr r2,[sp,#0x2c]`, `08029F38 cmp`,
      `08029F3A bge`, `08029F3C ldr r2,[sp,#0x38]`), so NO constant is
      applied to y0 anywhere in the reach test. Agrees with the canonical
      form in progress 9 above;
    - overlap test, then center-to-center deltas
      (`(x0+x1)>>1` both rects) for direction.
  - **Attack object layout (from m1/m5 usage):** `+0x00` vtable
    (0x08049DF0), `+0x04` owner pointer (player; its vtable supplies
    `+0x14/+0x8/+0x4/+0x0` methods), `+0x08` phase/active flag.
  - Interpretation (STRONG_STATIC): A press creates an attack object that
    per-frame tests candidates' body rectangles against a facing-extended
    player reach rectangle, and on phase changes notifies owner and
    dispatches the target. This is the P-003 melee structural chain:
    A -> attack object -> reach test vs target body -> owner/target
    dispatch. Remaining: target-list source, enemy object identity,
    enemy HP field, damage application.
  - Steering names adopted: `candidate_attack_object_dispatch_08049DF0`
    semantics; `0x0203DFA4` remains adjacent-runtime-object candidate.

- **P-003/P-004 progress 8 (2026-08-23), attack-object vtable decoded:**

- **P-003/P-004 progress 7 (2026-08-23), armed-punch methodology + punch
  writes into enemy struct:**
  - Human correction adopted: the current state ALREADY has the enemy
    adjacent/facing; previous runs armed too late (6s launch + injection
    latency = ~400 free frames before sampling). Solution implemented:
    launch with `--gdb` (core HALTED until a client continues - proven in
    P-002), inject the Lua via the Scripting window WHILE HALTED (prime the
    diff baseline + register callbacks), then GDB-continue via
    `build/research/p003-exp/gdb_continue.py` (RspClient handshake + 'c').
    Driver: `build/research/p003-exp/run_armed.ps1`; probe
    `tools/runtime/p003_armed_punch.lua`. Per-frame capture now starts at
    the true first frame.
  - `CONFIRMED` (runtime, armed punch, A at t=2):
    - punch writes INTO the enemy-struct region at press+0:
      `0x0203DE6C: f7e7f0ef -> 08049df0` (ROM pointer -
      **punch-effect/hit handler candidate 0x08049DF0**) and
      `0x0203DE70: 03002bd0 -> 0203DFA4` (pointer to the adjacent object
      at 0x0203DFA4).
    - at t=27: large tile-streaming burst into `0x3CA38..0x3CB68`
      (sprite tiles).
    - at t=61: entity-list reorder - the sampled words `0x3DE7C` and
      `0x3DF88` SWAPPED contents (e1: f799 -> 0203DE8C; walk:
      804bc98 -> f799) - confirming these are volatile list/pointer-ish
      slots, NOT stable stats. Reinforces the progress-6 invalidation.
    - player HP pair +1 regen at t=68 (d4->d5 / 54->55).
  - NEXT (static-first, cheap): xref/inspect `0x08049DF0` - the pointer the
    punch writes into the enemy struct; it should lead to the punch effect
    constructor and from there to damage application. Also identify the
    object at `0x0203DFA4`.
  - Enemy HP location: STILL UNKNOWN (volatile fields invalidated; the
    armed-capture machinery is now good enough to catch the real decrement
    once the punch connects - hit confirmation still pending).

- **P-003 progress 6 (2026-08-23), mash-A contact run - NEGATIVE +
  candidate invalidation:**
  - `tools/runtime/p003_mash.lua`: stood still (px=48,py=207 all run),
    17 A presses (2 ticks on / 10 off, t=20..212), per-tick entity-zone
    diff + all four HP-candidate words.
  - NO CONTACT: no enemy-side decrement of any candidate; enemy never
    entered melee range during 220 ticks (it does not approach the idle
    player in this state).
  - **CANDIDATE INVALIDATION** (OLD / NEW / RESOLUTION):
    - OLD: `0x0203DE7C` (18->13 twice) and `0x0203DEE4` (192->187) treated
      as enemy HP candidates; "ki damage = 5".
    - NEW: the SAME savestate re-run reads `0x3DE7C` = 0 -> 16 ->
      33801380 and `0x3DEE4` = 522178 constant with one transient blip.
      Values are not stable across runs of an identical state.
    - RESOLUTION: both addresses are VOLATILE FRAME DATA (sprite/tile
      streaming buffers), NOT persistent HP. The earlier 18->13 pair was
      coincidence. "Ki damage = 5" RETRACTED. Enemy HP remains UNKNOWN.
  - `CONFIRMED` (runtime): player HP pair `0x3DBB4/0x3DC20` + regeneration
    re-confirmed (three separate +1 recoveries: 210->211, 211->212,
    208->209 with both words moving together).
  - Per steering #6: requesting a human savestate with the enemy ALREADY
    directly beside the player and the player FACING it (saved before any
    attack). The mash technique did not work here because the enemy does
    not approach an idle player in this state.

- **P-003/P-004 progress 5 (2026-08-23), armed watcher on ki-blast state:**
  - New human state: sha256 `95de20ae4166995f66c28510aa01c0eeef57d69d490a785f14009694b40b44dc`,
    38,560 bytes, mtime 2026-08-23 17:19:57 (ki blast in flight). Probe
    `tools/runtime/p004_watcher.lua`: per-tick diff of entity zone
    `0x0203C000..0x02040000` from tick 0 + full-EWRAM snapshots
    (t=0,15,30,45,60,90,120). NOTE: an earlier "wrong save state" report
    coincided with a probe bug (primed-tick early return skipped the t0
    snapshot and desynced the chain) - fixed; disk had exactly one .ss1 and
    sha verification confirmed the correct state was loaded.
  - `CONFIRMED` (runtime): impact burst at **t=8** (93 changes: object-list
    pointer swaps at `0x3DDF0/0x3DE1C/0x3DE6C/0x3DE70`, tile waves).
  - **ENEMY HP CANDIDATES (paired-decrement convention):**
    - `0x0203DE7C`: 18 -> 13 (d=-5) - ALSO 18->13 in the previous ki-hit
      state (independent reproduction).
    - `0x0203DEE4`: 192 -> 187 (d=-5).
    - Ki-blast physical-energy damage = 5. Ownership split (HP vs mirror vs
      two actors) still to be resolved by a physical punch test.
  - CORRECTIONS (OLD / NEW / RESOLUTION):
    - `0x0203DF28`: earlier treated as HP candidate - it is a **periodic AI
      timer** (18-tick countdown inside a ~52-tick cycle; bursts at cycle
      boundaries). NOT HP.
    - `0x0203DF88`: steadily walking actor position, constant +110
      raw/tick (= 0.43 px/tick) - movement candidate, not damage.
    - Player-side pair `0x3DBB4/0x3DC20` (-13/-20 in earlier runs): now
      attributed to WOLF COUNTERATTACKS on the player (player HP pair),
      plus observed +1 regen at t~110. Player combat/anim block sits at
      ~`0x0203DBB0..0x0203DC40` (HP words + anim complex `0x3DBC0`).
  - Enemy struct web ~`0x0203DD80..0x0203DF00` includes pointer
    `0x3DDE8 -> 0x0203DBB0` (links enemy block to player block).
  - Next: physical punch at this enemy -> which candidate drops (resolves
    ownership split); then damage formula, knockback, hitstun per steering.

- **P-003/P-004 progress 4 (2026-08-23), control-drift + enemy search:**
  - `CONFIRMED` (runtime, Wander leg: no input, 380 ticks): `0x0203DBB4`
    (0xD4=212) and `0x0203DC20` (0x51=81) are **completely stable** without
    player action. Steering wording adopted: "variable hit-associated deltas
    observed" (-13, -20); damage RNG/stat contribution UNKNOWN; the fields
    are STRONGER hit-associated candidates (stable in control, changed only
    in punch legs). Ownership (enemy HP pair vs player-side vs mirrors)
    still UNPROVEN. The DoubleA pre-dump -1 drift (211/80 vs 212/81) remains
    unexplained.
  - Enemy-position search NEGATIVE in `0x02030000..0x0203FFFF` (4 snapshots
    100 ticks apart): no coordinate-like movers passed filters (values
    0..0x40000, |d|<=0x8000, >=2 moves). Enemy entity likely lives outside
    this window, uses another coordinate representation, or barely moves.
    Next: full-EWRAM snapshots (0x02000000..0x02040000) with looser filters.
  - Probe: `tools/runtime/p004_wander.lua` (allowlisted); snapshots +
    drift log under ignored build/research/p003-exp/.

- **P-003 progress 2 (2026-08-23), punch-timing probe:**
  - `tools/runtime/p003_punch_timing.lua` sampled buffered input,
    `+0x10` word, and OAM entries 0..15 (words `0x07000000..0x0700003F`)
    per tick across TapA (2-tick press), HoldA (14-tick press), and a
    no-press control, all from identical walk-ups.
  - Result: **all three legs byte-identical** in every sampled channel
    (only background-scroll words changed). Combined with the earlier
    entity-word null result, the punch presentation uses channels outside
    {entity words 0x000..0x23C, OAM[0..15], +0x10} - candidates: higher
    OAM entries, a shadow OAM buffer committed at VBlank, or sprite
    tile/VRAM state. Whether the punch fired in THESE runs is unverifiable
    with current sampling (the MoveA screenshot proof of the punch stands).
  - Conservative wording per steering: "no word-level player-entity
    mutation was observed during sampled punches" - NOT "punch state lives
    outside the entity" (byte/halfword or external-controller state not
    excluded).
  - OAM words `0x07000018/0x20/0x28` high bytes decrement continuously
    (background scroll drift) - useful as a liveness signal, not sprite
    state.
  - BLOCKER (clean statement per steering #5/#11): no locally available
    legal save/state contains a hittable enemy (Higher Plane mansion
    exterior + interior dialogue area only). A human-provided state in a
    simple combat encounter would unlock the contact chain (hit region ->
    target dispatch -> damage) and is the single highest-value next input.
    Everything establishable without a target has been established:
    attack input = A/0x0001 (context-sensitive interact-vs-attack),
    edge-consumed buffer, registry-negative, entity-word-negative,
    presentation channel unidentified.

## Function Knowledge

See `SUBSYSTEM_MAP.md` for the consolidated table. Confidence vocabulary:
`CONFIRMED` (runtime or byte-exact), `STRONG_STATIC` (static executable
behavior, multiple corroborations), `CANDIDATE` (single static observation).

## Structures

- `MapEntry` 0x38 bytes, 452 records at `0x0808E2E0` - CONFIRMED layout,
  field semantics mostly INFERRED/UNKNOWN (see reverse-engineering.md).
- Runtime rectangle object 0x18 bytes - bounds `+0x04..+0x0B` signed halfwords
  (CONFIRMED), callback reference `+0x0C`, retained descriptor `+0x14`,
  dispatch-table base `+0x00`.
- Source spatial descriptor - `+0x00` raw factory, `+0x04` unknown
  (callback-producer input), `+0x08/+0x0C` bound pairs; extent UNKNOWN.

## Blockers

- BSim uncalibrated: no genuinely distinct locally ingestible binary.
- Recomp repos ship no generated C++ (`generated/` empty), so no recomp symbol
  transfer surface exists.
- mGBA GUI-launch approval quotas historically flaky; native SDL probe path
  (ROM-011+) avoids Lua injection.

## Next Candidate

P-001 (player entity + update root) - top of the player/combat pivot.
Transition frontier is CLOSED; do not spend further units on transition
taxonomy (AUTO-005 vtable dump remains READY but demoted below P-series).

  - CALLER `LR=0x08018FC9` DECODED (progress 13 addendum): containing`n    fn `0x08018F90` = collision-instance BUILDER - allocates 16-byte`n    instance, binds node+0xC, loops node-data ptrs (+0x10 array)`n    calling point-query `0x8046AA4` per element, storing results into`n    the instance. The flinch wrapper `0x0801920E` is invoked from this`n    loop's vicinity (odd LR = continuation-style call). CONFIRMED: this`n    whole layer is overlap/collision evaluation feeding state instances.`n    Remaining unknown is only the TOP-level selector (which state id gets`n    entered on landed hit) - one level up.

- PROGRESS-13 FINAL (dual-probe session): removal dumps captured
  (player 203DBB0 on area transition + wolf objects); hp_writes.csv
  logged rows but register-parse bug (pc offset wrong in raw g-packet
  slice) misattributed Z0-vs-Z2 stops - raw evidence preserved in
  removal_objs.bin + hp_writes.csv for reparse with
  decode_register_payload. WOLF HP CANDIDATE CONFIRMED DIRECTIONALLY:
  wolf obj +0x74 was 100 (fresh spawn read) and 92 at a removal dump
  (decremented across fights). NEXT SESSION: fix reg decode (use
  decode_register_payload), rerun dual probe, capture HP writer PC +
  damage operand = P-004 closure.

- **CORRECTION (2026-08-26): +0x6c/+0x70 are NOT HP fields.**
  Prior handoff summary identified wolf combat-object `+0x6c` as an HP
  field (192->115 monotonic decrement across 17 HURT stops). This is
  RETRACTED. Static and runtime evidence proves `+0x6c` and `+0x70` are
  screen-space position deltas computed by the periodic writer at
  `0x08010250`:

  Static proof (`0x0801023e..0x08010250`):
  ```
  0801023e: adds     r0, r4, #0x6c       ; r0 = entity + 0x6c
  08010240: subs     r2, r2, r3          ; delta_x = entity_x - camera_x
  08010242: ldr      r3, [sp, #0x20]     ; camera_y
  08010244: ldr      r1, [r1, #4]        ; camera_y_component
  08010248: subs     r1, r3, r1          ; delta_y
  0801024c: adds     r1, r2, #0          ; r1 = delta_x
  0801024e: ldr      r2, [sp, #0x10]     ; r2 = delta_y
  08010250: stm      r0!, {r1, r2}       ; store delta_x to +0x6c, delta_y to +0x70
  ```
  STM writes r1 (delta_x) to `[entity+0x6c]` and r2 (delta_y) to
  `[entity+0x70]`. These are recomputed every frame from entity world
  position minus camera position.

  Runtime confirmation:
  - Z2 watchpoint on `0x0203d570` (+0x6c) fires at PC `0x08010252`
    (instruction after the STM), value = 0xc0, with the same chain
    (`8715ed8`) at every stop, a presentation-periodic writer, not a
    damage writer.
  - Conditional Z2 capture (value-change filter) showed +0x6c decrementing
    by 1/frame continuously, consistent with wolf walking left on screen,
    not HP damage.
  - Field probe (Z0+Z2 combined) showed +0x6c changing by -19, -14, -7
    between HURT entries, consistent with screen-position jumps during
    movement, not discrete damage events.

  Same-object dump audit confirms:
  - 17 wolf records (addr `0x0203d504`) and 17 player records
    (`0x0203dbb0`) at fixed addresses, one per HURT stop.
  - Wolf `+0x6c` values: screen X positions as wolf walks left.
  - Wolf `+0x70` values: screen Y positions.
  - Wolf `+0x0004` values: 228 constant across two-wolf capture (wolf
    wasn't being hit in that session). Single-wolf capture showed 35
    decrementing to 34, THIS IS THE HP FIELD.

  IMPLICATION: HP IS in the 0x180-byte combat object at `+0x0004` (u16).
  The two-wolf capture showed constant 228 because the breakpoint fired
  on wolf-attack events (wolf hitting player), not player-attack events
  (player hitting wolf). Single-wolf capture with write watchpoint
  confirmed HP decrement at this offset.

## P-004 Closure (2026-08-26, corrected)

Wolf HP located in combat object at `wolf_obj + 0x0004` (u16).

**HP field**: `wolf_obj + 0x0004` (u16)
- Value copied from monster stat block (`+0x0036`), which gets it from
  ROM entities (`gWolfAnimSet_base_804c52c + 0x42`)
- HP decrements on each hit (confirmed via write watchpoint)
- Initial HP = 35 (single-wolf capture)
- HP write at `0x0800aba8`: `add r0,r0,#0x1f00; strh r3,[r0,#0x34]`
  where r0 = `wolf_obj - 0x1F0`

**HP initialization chain**:
```
ROM entities → monster stat block (+0x0036) → combat obj (+0x0004)
  str r1,[r6,#0x50] at 0x0800aebc (stat_block → combat_obj+0x50)
  str r1,[r1,#0x42] at 0x080190de (stat_block → combat_obj+0x42)
```

**Secondary HP mirror**: `wolf_obj + 0x3e`, written at
`m4_phase1_enter_s20_or_s30` with same initial value

**Retracted claims**:
- +0x6C/+0x70 = screen-space position deltas (NOT HP)
- `0x0203C934 + 0x0118` = player HP (NOT wolf HP, confirmed by
  call-path analysis: stops 2,4,6,7 are wolf-attack chain)

**Evidence level**: CONFIRMED (write watchpoint on wolf_obj+0x04,
HP decrement observed, writer PC identified)

## P-004/P-005 Correction (2026-08-27, supersedes closure above)

- `CONFIRMED`: `+0x04` is not HP. Across 2,060 per-frame samples from three
  fresh captures, `u32(target+0x04) == floor(u32(target+0x1A4)/256) + 4`
  with zero mismatches, including no-input movement.
- `CONFIRMED` static role: `0x080101C6` is inside spatial-status function
  `cand_slot3_0801003A`, not combat. It converts `+0x1A4` fixed-point world Y
  to integer pixels, adds half of byte `+0x19D`, and stores the body-center/
  anchor at `+0x04`. The same function forms body/map bounds and derives
  camera-relative coordinates. See `build/ghidra/reports/p2-slot-triage.txt`
  lines 890-893, 1080-1106, and 1222-1233.
- `RETRACTED`: `+0x04` as u16/u32 HP; `0x080101C6` as an HP writer; 1 HP
  damage; autonomous healing; and all re-hit intervals based on this field.
  The old value 35 and newer values 228..233 were position-derived.
- `RETRACTED`: `0x0800ABA8` as an STRH writer. Canonical Thumb decode has a
  `bl 0x0803DC96` beginning at `0x0800ABA6`; `0x0800ABA8` is inside that BL
  encoding, and the next instruction at `0x0800ABAA` is `ldrh`, not a store.
- `RETRACTED`: classifying the `0x0804C484` object as the wolf combat/HP
  object. It is retained only as a moving HURT-path target of unresolved type.
- `REJECTED`: `+0x74` as a fallback HP candidate; prior evidence identifies it
  as a graphics/frame pointer slot (`AUTO_RE_<local-state-name>` lines 1081-1095 and
  1128-1142 before this insertion).
- True wolf entity, HP field, and damage mutation are `UNKNOWN`. The strongest
  bounded next locus is hit-phase function `0x080342AE..0x08034305`, which
  passes the target through callbacks at `0x080342D8` and `0x080342E6` after a
  nonzero hit query (`build/ghidra/reports/p3-49df0.txt` lines 44-69). This is
  a candidate capture boundary, not a damage or HP claim.

## P-006 Damage-Anchor Search (2026-08-27)

Human observation establishes that the preloaded ki blast in
`single-wolf.ss1` deals 37 damage and that frames 5 and 60 intentionally
bracket its hit. The Lua-only full-EWRAM scan in run
`20260827-104049-25bad19b` reported `EXACT16_TOTAL,0` and
`EXACT32_TOTAL,0`; therefore no aligned u16/u32 EWRAM value had a net decrease
of exactly 37 across that broad interval. This is a clean negative for those
representations and interval only.

The tighter tracked `p006_hit_bracket_scan.lua` dynamically rediscovers the
single `0x0804C484` target on every load, monitors its `+0x1D4` event marker,
and preserves full EWRAM/IWRAM snapshots for two frames before, the event
frame, and two frames after. Runs `20260827-110937-767e2653`,
`20260827-111207-7f191534`, and `20260827-111608-dd69bad4` all observed the
same marker transition at tick 32. All used ROM SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
and source-state SHA-256
`c7c97aa7eb673f6260f08e9a9b315d8561f3ebab2764266f7aa05b36cb2bd6a2`.

The five-frame run found no aligned or unaligned u16/u32 value in EWRAM or
IWRAM that decreased by exactly 37 on the marker-transition frame. Four EWRAM
bytes did: `0x0200049C` 53->16, `0x02000507` 38->1,
`0x0203C876` 37->0, and `0x0203C91E` 37->0. Every surrounding neighborhood
was simultaneously rewritten across many adjacent bytes, so none is an
isolated stable-field mutation. One IWRAM byte also decreased by 37, but its
containing word changed again on the next frame. These coincidences are not
adequate HP candidates. The negative does not exclude encoding, indirection,
a mutation outside the sampled event boundary, or a non-literal damage update.

Bounded static decoding of the observed m1 path found:

- `0x080342D8` resolves through the observed owner table to slot 0 method
  `0x0804E500`, a `bx lr` no-op;
- `0x080342E6` resolves through owner slot 4 to `0x080188F4`, then target
  vtable `+0x68`, state selector `0x0800AA4A`, and HURT composite
  `0x08706B7C` / constructor `0x0801920E`;
- no damage/stat store occurs in those bounded wrappers;
- `0x08039182` installs table `0x0804D514`, performs cleanup/list removal,
  and optionally frees based on a caller flag. It neither reads nor tests an
  HP candidate and is reached only through runtime-relative slot-0 dispatch.

The authoritative HP mutation therefore remains `UNKNOWN`. The minimum
resolving evidence is an execution breakpoint at `0x08039182` during a
human-confirmed enemy death, recording LR and a bounded stack walk, followed
by static decoding of the concrete continuation. That is a corrective
damage-anchor ticket, not P-007.

## P-006A Corrective Damage Anchor (2026-08-27)

The `0x08039182` candidate produced zero stops during a human-confirmed wolf
death and is rejected for this target family. The observed `0x0804C484`
relative table instead resolves slot 0 to `0x0800F76E`. A death run stopped at
that method with target `0x0203D504`; its LR `0x0804F54E` identifies generic
slot-1 wrapper `0x0804F53C`, which forwards to target slot 0 with free flag 1.

The final complete run `20260827-133446-e142dd9e` captured the concrete
upstream method at `0x08018950`: target `r1=0x0203D504`, LR `0x0800FA78`, and
stack chain beginning `0x0800FA2B`. Static decode of `0x0800FA2A` is the
authoritative correction:

- current HP is signed u32 at target `+0x28C`;
- applied damage is loaded from incoming record `+0x18`;
- `0x0800FA4E` subtracts damage from current HP;
- `0x0800FA50` stores the new HP;
- signed result `> 0` returns the survivor path;
- result `<= 0` is zeroed, broadcasts event `0x11`, invokes the configured
  death callback, and reaches the captured removal path.

The retained 0x2A0-byte death dump independently records target `+0x28C = 0`.
Combined with the maintainer's separate visible-death confirmation, current HP, damage
operand, writer, and death threshold are **CONFIRMED, Level 4** for this
observed target family. Earlier full-memory scans missed a literal `-37` on
their marker-transition frame because that frame was not independently tied
to this mutation; their bounded negative remains valid.

## P-006B Corrected Melee Reaction Timing (2026-08-27)

Run `20260827-154856-842990b7` is the controlled single-punch evidence. The
physical reaction node `0x08706BA8` was selected at gameplay tick 320 and the
authoritative HP writer `0x0800FA50` executed at tick 323. Its load-specific
target was `0x0203D504`; old/new HP were `0x00022A3C`/`0x000161B2`, incoming
record was `0x03007D44`, and record `+0x18` was `0x0000C88A`. This was a
nonlethal survivor result. Therefore physical HURT preceded real damage by
three gameplay ticks (**CONFIRMED, Level 3**).

The controller is rooted at target `+0x238`. Physical reaction node
`0x08706BA8` contains raw entry/update/exit pointers
`0x0801920F`/`0x08018FDB`/`0x08019043` (fetch addresses `0x0801920E`,
`0x08018FDA`, and `0x08019042`). Its controller depth unwound from 2 to 1 at
tick 348, supporting `T_HURT_ENTER=320` and `T_HURT_EXIT=348`. A generic
`0x08706B7C` controller event followed at tick 350, but that node also occurs
outside ordinary attack behavior. The separate human observation that the wolf
recovered quickly and began punching was not tick-synchronized. Exact
`T_AI_RESUME` and HURT-to-AI suppression duration therefore remain **UNKNOWN**.

Writer-only mash run `20260827-211421-4e307ab8` preserved full-speed play and
recorded post-ki authoritative decrements at ticks 673, 976, and 992. The
consecutive observed writer intervals were 303 ticks (673 to 976) and 16 ticks
(976 to 992). The latter hit crossed HP below zero and is retained only as a
timing observation because death behavior is out of scope. Neither interval
establishes an immunity timer or general minimum eligibility window. The user's
visible report that the wolf died is separate corroboration, not a death-path
investigation.

Lua samples at ticks 969 and 984 are raw A-held input among many such samples;
their proximity to damage writes cannot establish attack acceptance or cadence.
Breakpoint `0x080342AE` was rejected for `T_ATTACK` because runtime showed it
serves broad animation/collision objects rather than uniquely accepted player
punches. Historical presentation evidence at 22 ticks was not a minimum test.

Reaction-family entries without a writer in the noisy mash capture could not
be attributed strongly enough to accepted physical punches. They therefore do
not prove contact gating or post-hit damage immunity. Separate invulnerability,
the exact executable `T_ATTACK`, minimum accepted-punch cadence, exact AI resume,
HURT-to-AI suppression duration, HURT exit condition, normal pre/post handler
identity, and accepted-punch gating classifications remain **UNKNOWN**. Explicit
knockback kinematics are deferred under the ticket's bounded rule. P-006B
stops **PARTIAL** at these precise timing blockers and does not begin P-007.

## P-006C Behavior-Controller Decode (2026-08-27)

### Controller primitives and the state table

Capstone decode of the canonical ROM resolved the actor state machine's public
primitives. Each takes `r0` = controller pointer and `r1` = selector index:

| Address | Role |
|---|---|
| `0x0800AA9C` | PUSH a state, guarded by `depth < 5` |
| `0x0800AA4A` | REPLACE the top state |
| `0x0800AAD8` | POP the top state |
| `0x0800AB0C` | update the current state |

The controller structure is:

```text
ctrl+0x00   context/actor pointer
ctrl+0x04   stack depth
ctrl+0x08 + 8*i   entry i = { node_ptr, table_slot }
ctrl+0x30   pending-notify count, ring at ctrl+0x34
```

Both `LDR` sites (`0x0800AA50` and `0x0800AAA8`) resolve through the literal
pool at `0x0800AB50` to **state-table base `0x0870F514`**, stride 8, entry
`{primary_node, secondary_node}`. A selector therefore addresses
`0x0870F514 + selector * 8`.

Six wrappers expose the primitives per controller offset. They have zero `BL`
callers and are dispatched indirectly:

| Wrapper | Controller offset | Operation |
|---|---|---|
| `0x0804EC8C` | `+0x238` | push |
| `0x0804ECA0` | `+0x228` | push |
| `0x0804ECB0` | `+0x238` | replace |
| `0x0804ECC4` | `+0x228` | replace |
| `0x0804ECD4` | `+0x238` | pop |
| `0x0804ECE8` | `+0x228` | pop |

A behavior node is 24 bytes: `{entry_fn, update_fn, exit_fn, param, child,
sibling}`.

### Correction: `0x0801920F` is a generic handler

`0x0801920F` is **not** HURT-specific. It appears as the entry handler of about
170 selectors spanning every actor family in the table. Breakpoint
`0x0801920E` therefore cannot establish HURT identity by itself; identity comes
from the node pointer and table slot.

Wolf selector `0x1B4` (436) has primary node `0x08706BC4`, whose handlers are
`{0x08018F91, 0x0801900B, 0x08019043}`. The previously named reaction node
`0x08706BA8` is that node's **child** at `+0x10`, carrying the clip handlers
`{0x0801920F, 0x08018FDB, 0x08019043}` and param 3.

The wolf's selectors are contiguous:

| Selector | Table slot |
|---:|---|
| 434 | `0x087102A4` |
| 435 | `0x087102AC` |
| 436 | `0x087102B4` |
| 437 | `0x087102BC` |
| 438 | `0x087102C4` |
| 439 | `0x087102CC` |

Selector 2 (`0x0870F524`) is a shared default seen beneath wolf states.

### Runtime confirmation without breakpoints

Runs `20260827-230924-163182ab` and `20260827-231155-d5b7df8d` used the tracked
launcher in Lua-only mode on stable mGBA 0.10.5, with zero executable stops and
no effect on gameplay pacing. Reading `wolf+0x238` per frame produced live depth
and `{node, slot}` entries whose slots decode exactly to the statically resolved
selectors 434-439 and the default 2. The state table at `0x0870F514` is
therefore **CONFIRMED, Level 3**.

### Negative result: the player has no behavior controller

A structural probe scanned every 4-byte offset across the first `0x400` bytes of
each actor on twelve sampled ticks, accepting any offset whose depth was in
`[1,5]` and whose top entry pointed into the state table. Only `wolf+0x238`
matched, on all twelve samples. The player object, taken from the documented
slot `0x03001C34`, matched at **no** offset, and `wolf+0x228` did not match
either despite a wrapper existing for that offset.

The accepted normal-punch anchor consequently cannot come from this controller
system and must be sought on the attack-object path of the P-003 chain.

### Attack-object constructor located (P-006C, 2026-08-27)

The P-003 progress-10 conclusion that the aligned word `0x08049DF0` at
`0x0802A008` is "code, not a literal" and that the static constructor hunt was a
dead end is **corrected**. `0x0802A008` is a literal pool word that a
disassembler renders as an instruction, which is why it was dismissed.

Function `0x08029FE6` is the attack-object constructor:

```text
08029FF2  movs r0, #0xC       ; 12-byte allocation
08029FF4  bl 0x0803D5B8       ; heap allocator
08029FF8  cmp r0, #0
08029FFA  beq 0x0802A002      ; skip on allocation failure
08029FFC  ldr r1, [pc, #8]    ; pool 0x0802A008 = 0x08049DF0
08029FFE  stm r0!, {r1, r4}   ; vtable at +0x00, owner at +0x04
```

This matches the confirmed attack-object layout `{+0x00 vtable, +0x04 owner,
+0x08 phase}` exactly. `r4` is loaded at `0x08029FF0` from the result of the
`0x08046AA4` query at `0x08029FEC`.

The constructor is a **behavior-node handler**, not an ordinary function. It has
zero `BL` callers ROM-wide and 77 aligned data references as the Thumb pointer
`0x08029FE7`, spread across `0x086FE11C..0x0870F444` at roughly one per actor
family. The wolf-cluster node at `0x08706A8C` is
`{0x0801890B, 0x08018921, 0x08018937, param 0x1B5, ctor 0x08029FE7, ...}`, so
the constructor occupies node slot `+0x10`.

These nodes are reached by chaining through `+0x18`, not directly from the state
table's primary and secondary pointers; scanning only the six slots hanging off
`0x0870F514` entries finds no match, which is why the constructor was missed.

The runtime anchor initially selected for `T_ATTACK_ACCEPT` was `0x08029FFE`
rather than `0x08029FF4`, because it executes only after a successful
allocation and carries `r0` = the new attack object.

**That selection was refuted at runtime; see the following subsection.** The
expectation that `r4` would identify the owning actor was also wrong.

#### Runtime refutation of the constructor as the punch anchor

Run `20260827-233643-45f579b4` armed breakpoint `0x08029FFE` alongside the Lua
controller observer, so executable stops and input shared one gameplay tick.

The capture recorded 11 stops, all between tick 31 and tick 204. The human's A
presses ran ticks 278 to 806, with 188 rising edges. **No constructor stop
occurred during the entire mash window.** The recorded stops are startup and
idle activity belonging to other actors.

Two families appeared among those stops, and neither is the player:

| Family | LR | Object | Ticks |
|---|---|---|---|
| A | `0x0803D604` | always `0x0203DEB4` | 31, 74, 117, 144, 170, 198 |
| B | `0x08029FF8` | fresh each time | 63, 118, 157, 178, 204 |

Neither family's `r4` matches the observer's player object `0x0203CEB4` or the
wolf `0x0203D504`, so `r4` at this site is **not** the owning actor. It is the
result of the `0x08046AA4` query at `0x08029FEC`; do not read it as an owner.

The static decode of `0x08029FE6` stands: it allocates 12 bytes and installs
vtable `0x08049DF0`. What is refuted is the inference that a player punch
triggers that construction. Family A reusing the identical address
`0x0203DEB4` six times suggests the melee attack object may be **pooled and
recycled** rather than constructed per punch, which would explain the absence
of construction events during sustained attacking.

`0x08029FFE` is therefore **rejected** as the `T_ATTACK_ACCEPT` anchor, joining
`0x080342A8`, `0x08034298`, and `0x080342AE`.

### `T_ATTACK_ACCEPT` resolved: the animation-clip pointer (P-006C, 2026-08-28)

Two proposed-structure candidates were refuted at runtime. The attack-object
constructor `0x08029FFE` never executed across 188 A presses, and no
attack-object phase field at `+0x08` moved across 290 A presses
(run `20260828-003928-9c690116`, 90.1 seconds, complete, zero transitions in
ticks 571 to 3407).

The method that worked stopped proposing a field. `p006c_punch_field_probe.lua`
snapshots the entire player object from slot `0x03001C34` every frame, records
every changed word offset, and emits a standalone row for each A rising edge.
Taking the differential of offsets changing on press ticks against off-press
ticks lets the data select the anchor.

In run `20260828-004513-27dae1f8` three offsets stood out, changing on 163, 163,
and 162 of the press frames: `+0x04C`, `+0x050`, and `+0x014`. `+0x04C` holds a
ROM pointer in the `0x0851Cxxx` family and is an **animation-clip pointer**:

| Value | Meaning |
|---|---|
| `0x0851C618` | idle / neutral |
| `0x0851C680`, `0x0851C6C0`, `0x0851C6A0` | normal punch clips, entered only while A is held |
| `0x0851C6E0` | a different action, entered on `keys=0x0100`, never on A |

An accepted normal punch is therefore the transition of `+0x04C` from idle into
a punch clip while A is held. Off-press changes are returns to idle or other
actions, so that filter is what makes the anchor exact.

Measured over 154 accepted punches in one 90-second window:

| Metric | Accepted punch | Raw A |
|---|---:|---:|
| Count | 154 | 330 |
| Minimum interval | **20 ticks** | 8 ticks |
| Median interval | 26 ticks | 13 ticks |

The engine accepts roughly every second to third press, confirming the ticket's
requirement that raw A assertion cannot substitute for acceptance. The three
punch clips appeared about 50 times each, which suggests a combo cycle; that is
an observation from clip counts only and was not investigated.

### P-006 closed (2026-08-28)

P-006 is **RESOLVED**. P-006C is archived at `docs/research/archive/P-006C.md`
and `docs/PROJECT_<local-state-name>` is a stop-only placeholder; P-007 is not started.

Two corrections carried into the permanent state file:

- `0x0801920F` is a generic handler shared by roughly 170 selectors, so
  executing `0x0801920E` or `0x0801920F` alone does **not** establish HURT
  semantics. Any earlier claim resting on that program counter alone is
  superseded. The reaction-state push and pop, correlated with authoritative HP
  decreases, is the stronger anchor.
- The player has **no** behavior controller. Any interpretation that assumed one
  is superseded.

The 28-tick reaction duration from the three-breakpoint run is retained as
historical evidence and explained by that instrumentation's pacing
perturbation; the canonical low-perturbation value is 24 ticks.

`docs/PROJECT_<local-state-name>` is bounded at 240 lines by
`tests/unit/test_workflow_migration.py`. Completed-ticket result records now
continue in `docs/PROJECT_<local-state-name>`, linked from the primary file, so closing
a ticket no longer forces older verified records to be compressed away.

## P-007 Wolf Combat AI (2026-08-28)

### Behavior-tree architecture

The actor system is a behavior tree, not a flat state machine. A node is
`{entry, update, exit, count, child[count]}`; the field at `+0x0C` is an array
length, proven by builder `0x08018F90`, which allocates `count * 4 + 0x10` bytes
and iterates `node+0x10[]`. Composite update `0x0801900A` calls every child,
ANDs their results, and short-circuits on status 2.

### One reusable distance primitive

`0x08029C90` and `0x08029BE0` are instruction-for-instruction equivalent. Both
call body-bounds getter `0x0800FDFA` for each actor, reduce each rectangle to a
center via `(lo + hi) >> 1`, then:

```text
dx = centerA.x - centerB.x
dy = centerA.y - centerB.y
r0 = dx*dx + dy*dy          ; muls, muls, adds
r1 = [instance + 0x0C]      ; threshold copied from the node
cmp r0, r1
bgt -> return 0             ; outside
     -> return 1            ; inside, inclusive
```

The comparison is a signed `bgt`, so the test is `dist_sq <= threshold`. This is
one primitive parameterised per node, not a family of separate range checks.
Constructors `0x08029C64` and `0x08029D14` allocate a 16-byte instance and copy
the node's `+0x0C` constant into instance `+0x0C`; they differ only in the
vtable installed, `0x08049C28` versus `0x08049C40`, whose evaluator slot `+0x14`
selects `0x08029BE0` or `0x08029C90` respectively.

Observed thresholds: idle node `0x08706A38` carries 10000; hub node
`0x08706B7C` children carry 440, 524, 2500, 4900, 7864, and 8100.

### Confirmed transition graph

```text
IDLE 434
  - dist_sq <= 10000           -> HUB 435

HUB 435
  - dist_sq <= 524             -> ATTACK 437
  - otherwise                  -> PURSUIT 438 / 439

ATTACK 437
  - after 35 ticks             -> HUB 435

DISENGAGE: NONE
```

Pooled transition counts across four captures: `435->438` 144, `437->435` 108,
`438->435` 73, `438->437` 69, `435->437` 40, `435->436` 32, `436->435` 32,
`435->439` 6, `439->435` 5, `434->435` 2. Selector 438 is near pursuit and 439
far pursuit; both return to the hub. Selector 436 is observed and returns to the
hub, but no condition was established for it.

ATTACK 437 held for exactly 35 ticks in 52 of 52 episodes and returned to 435 in
all 52. The minimum observed attack-start cadence is 36 ticks, consistent with
the 35-tick state plus the earliest following start. No executable timer was
found, and `+0x12` was tested and refuted: all 17 attacks in run
`20260828-012734-586c44d8` entered at counter 0 yet exited at values from 4 to
252, so it is an animation clock rather than an attack timer.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: acquisition radius

**OLD CLAIM.** Hub constant 8100, radius 90, might be the wolf acquisition
radius.

**NEW EVIDENCE.** Idle selector 434 owns its own distance condition. Its primary
node's `child[0]` is node `0x08706A38`, entry `0x08029D15`, threshold 10000.
In run `20260828-101954-32dfd87b` both wolves held idle for over 1000 ticks and
left it independently:

| Wolf | Last idle | First pursuit |
|---|---|---|
| `0x0203D504` | 10709 (r 103.5) | 9602 (r 98.0) |
| `0x0203DBB0` | 9870 (r 99.3) | 9356 (r 96.7) |

No hub constant lies in either bracket; 10000 lies inside the `0x0203D504`
bracket. Rows are change-triggered, so no row was sampled at exactly 10000.

**RESOLUTION.** The acquisition-radius interpretation of 8100 is **SUPERSEDED**.
Acquisition is `dist_sq <= 10000`, radius 100. The static threshold is
CONFIRMED; the runtime transition is consistent and strongly bracketed. The 8100
constant remains a real hub band whose role is unmapped.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: absolute-address identity

**OLD CLAIM.** P-004-era notes associated `0x0203DBB0` with player context.

**NEW EVIDENCE.** In state `wolf-acquire.ss1`, `0x0203DBB0` carries the wolf
dispatch word `0x0804C484`, holds a behavior controller at `+0x238`, idles in
selector 434, and executes the full wolf combat loop.

**RESOLUTION.** Absolute EWRAM addresses are session and state dependent and are
not permanent actor identity. Structural provenance, meaning the dispatch word
and controller, overrides address-based naming. The older observation stands for
its own capture and is marked with this caveat rather than rewritten.

### Disengagement

**NONE.** The wolf does not disengage once acquired. Runtime testing observed
continued engagement out to at least radius 157 in run
`20260828-100719-3a8e0ca3`, where the wolf remained in selectors 435, 438, and
439 throughout the retreat and left only because the player changed area.
Firsthand gameplay experience independently confirms wolves do not drop aggro.
Classification is CONFIRMED BEHAVIOR; a static mechanism for the absence of a
disengagement path was not required for closure.

Implementation rule: once IDLE 434 enters the combat loop, do not add a
distance-based leash. The observed radius 157 is a lower bound on engagement,
not a leash value, and must not be implemented as one.

## P-008 Normal Melee Variant Selection (2026-08-28)

### External research first

This ticket is the first run under the External-Research-First rule, and it is
the rule's own justification. Seven angles were opened before any probe.

The decisive source was `<reference-checkout>\docs\REFERENCE.md:518`,
drawn from the retail instruction booklet read cover to cover, which records
that the real behavior is "a single repeating attack alternating punch/kick
animations, so the plan implements one attack, not a combo string". Line 273
records a critical hit as exactly twice normal melee damage with chance rising
with STR, and line 494 records that public attack, hitstun, and knockback frame
data is confirmed absent rather than merely unfound. The IGN control list
documents `A` as "Melee attack" with no combo notation.

That baseline removed four investigations from the ticket before it opened:
combo-reset timing, miss-dependent combo advancement, movement-reset combo
semantics, and finite or looping chain behavior. External research narrowed the
question; it is not executable proof and is not recorded as such.

### Clip table

The three punch clips are contiguous entries in the character animation table
based at `0x0851C898`:

| Index | Slot | Clip |
|---:|---|---|
| 0 | `0x0851C898` | `0x0851C618` idle |
| 4 | `0x0851C8A8` | `0x0851C680` punch |
| 5 | `0x0851C8AC` | `0x0851C6A0` punch |
| 6 | `0x0851C8B0` | `0x0851C6C0` punch |

The contiguity of indices 4 to 6 is consistent with a base-plus-offset
selection, and it also explains `0x0851C708`, seen once during an idle smoke
test: that is index 9, an unrelated animation.

### Selection: uniform random, mechanism UNKNOWN

Run `20260828-105601-6865162d`, 120.219 seconds, human air-punch with no
contact, read-only observer. 266 accepted punches.

| Hypothesis | Predicts | Observed | Verdict |
|---|---|---|---:|
| Previous-animation avoidance | 0 immediate repeats | 94 of 265 | REFUTED |
| Fixed cycle | 100% self-match at some lag | 26 to 34% at lags 2 to 6 | REFUTED |
| Uniform random | about 88.3 repeats | 94, z = 0.74 | CONSISTENT |

Counts were `0x0851C6C0` 91, `0x0851C6A0` 91, `0x0851C680` 84; chi-square for
uniformity is 0.37 on 2 degrees of freedom against a 5% critical value of 5.99.

**The executable selector was never located, and the mechanism is UNKNOWN.**
The only aligned reference to the clip-table base `0x0851C898` is `0x086AD35C`,
which is a data slot inside a per-character table of clip tables, not an
instruction. Uniform random is therefore a **behavioral** finding from the
observed distribution, not a decoded `rand() % 3`. Do not record it as executable
provenance.

A published lead was refuted. `REFERENCE.md:491` records LoG2 RNG seeds at
`0x03003890` and `0x03003894` from TASVideos. Those words, and the adjacent
`0x03003898`, were sampled on all 532 rows of the run and **never changed**
(`0x00000200`, `0x00000200`, `0x00000000`; zero changes across 265 consecutive
punch pairs) while selection varied 266 times. They are not this game's RNG.
This also retires the P-007 hunch that leaf node `0x0875028C` referencing
`0x03003898` might be reading one.

### Duration: identical, 16 ticks

Run `20260828-110417-0e6ef2a1`, 150.235 seconds, **scripted input**, 50 punches.

| Clip | n | Duration |
|---|---:|---|
| `0x0851C680` | 19 | 16, no variance |
| `0x0851C6A0` | 13 | 16, no variance |
| `0x0851C6C0` | 18 | 16, no variance |

Every observation was exactly 16 ticks; the distinct-value set is `{16}` for all
three. Measured clip-leaves-idle to clip-returns-to-idle at frame granularity,
Lua-only with zero executable breakpoints.

The press interval cycled through 18, 21, 24, 19, 27, 22, 31 and 20 ticks
precisely so a fixed period could not alias against an internal timer; each gap
appeared 6 or 7 times.

**Do not conflate 16 with 20.** The animation completes in 16 ticks, but P-006C
established the minimum accepted-punch cadence as 20, so at maximum mash rate
there are about 4 non-attacking ticks between swings. The gate is not the
animation finishing.

### Damage: indistinguishable

Run `20260828-111132-b8551f49`, human-driven combat, wolves killed and
respawned repeatedly. Authoritative HP is `target+0x28C` signed 32-bit, per
P-006A, with writer `0x0800FA50`.

Of 30 recorded hits, 8 were discarded because two wolves lost HP on the same
tick and could not be attributed to one swing. Excluding two outliers:

| Clip | n | Mean | Range | Spread |
|---|---:|---:|---|---:|
| `0x0851C680` | 7 | 51018 | 49476 to 52440 | 2964 |
| `0x0851C6A0` | 8 | 49884 | 47956 to 51528 | 3572 |
| `0x0851C6C0` | 5 | 50358 | 49096 to 51148 | 2052 |

The between-variant mean difference is about 1100, while each variant's own
internal spread is 2000 to 3600. Variation within a variant exceeds variation
between variants, so the three are indistinguishable at this sample size.

A level-up confound was raised and checked rather than assumed away: damage
holds a stable 48000 to 52000 band from tick 943 to tick 5006 with no upward
drift, so the per-variant means are not comparing different STR values. Keep
this check in future damage comparisons.

The run ended at 175.907 seconds with `ConnectionError`, an emulator exit of the
same class seen in run `20260828-100719-3a8e0ca3`. It is not a Lua fault, and 30
hits were captured before it ended.

### Unexplained outliers

Two events measured 72010 and 75354, which are 1.43 and 1.50 times the pooled
non-outlier mean of 50399.

**OBSERVATION:** two anomalous higher-magnitude events.
**INTERPRETATION:** UNKNOWN.
**POSSIBLE FUTURE LEAD:** the critical-hit system.

`REFERENCE.md:273` documents a critical hit as **exactly twice** normal damage.
1.43 and 1.50 are not 2. These must not be labelled critical hits, combo
finishers, special attacks, or RNG damage bonuses without executable
provenance. External documentation makes critical hits a plausible future
hypothesis, not a P-008 conclusion.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: the combo hypothesis

**OLD CLAIM.** Three punch clips at roughly balanced usage counts, first
observed in P-006C, might represent a deterministic three-step combo cycle.

**NEW EVIDENCE.** Selection is uniform random across 266 accepted punches, with
avoidance and fixed-cycle both refuted; all three variants have an identical
16-tick duration with zero variance; damage is indistinguishable; and no
deterministic progression is needed to explain the observed sequence.

**RESOLUTION.** The deterministic-combo interpretation is **RETRACTED**. The
canonical classification is random normal-melee presentation variants. The
original balanced-count observation stands, and this resolution explains it.

### Tooling correction

`tools/runtime/p008_contact_trace.lua` latched its `active_punch` attribution
only when the immediately preceding clip was idle. Real combat transitions punch
to punch and hurt to punch without passing through idle, so in run
`20260828-111132-b8551f49` the tracker latched once at tick 857 on
`0x0851C628`, a non-punch clip, and never updated; all 30 rows carried that
stale value.

**The defect did not reach the result.** Every damage figure came from the
`clip` column, which is read live at the hit tick and correctly recorded the
three variants at 11, 11 and 8 occurrences. The stale column was redundant.

The fix replaces the idle-predecessor test with an explicit `PUNCH_CLIPS`
membership set, because "not idle" is wrong: the player has non-idle clips that
are not punches, such as being hurt. A regression test covers the membership
logic and asserts the observer still performs no input.

A runtime re-run was **not** required for this correction. The justification is
the combination of impact analysis, regression coverage, and an unchanged
evidence basis, not an assumption that the bug was harmless.

A second defect was found in the new test itself: it asserted the bare word
`setKeys` was absent, but the file's header comment names those APIs while
explaining it does not call them. A grep confirmed line 4 is the only
occurrence and no call exists, so the assertion was tightened to the call form
`emu:setKeys` rather than the probe being changed.

### Scripted input

the maintainer directed that repetitive mashing be scripted rather than performed by hand.
`tools/runtime/p008_mash_driver.lua` is deliberately a **separate** file from
the read-only observers, whose tests assert input APIs are absent; that
assertion encodes the guarantee that a capture was input-free, and merging input
into an observer would void it silently while leaving the test green.

The mGBA scripting documentation records that `setKeys`, `addKeys` and
`clearKeys` take a `u32` bitmask and that `C.GBA_KEY.A` is bit index 0, so the A
mask is 1 rather than the constant itself.

Scripted input is not equivalent evidence to human input. The selection result
rests on a human capture; the scripted run establishes duration only, and each
run's provenance is recorded with it.

## P-009 Critical Hit Mechanics (2026-08-28)

### External research first

The behavioral prior was taken from documentation before any probe: criticals
occur on normal melee, deal double damage, become more likely with STR, display
yellow rather than red, and are reported to knock enemies back. Scope therefore
began at *how exactly*, not *do criticals exist*.

One element of that prior is now contradicted by the binary. Per the
External-Research-First rule the runtime observation wins, and "double damage"
is retained as EXTERNAL_BEHAVIOR that runtime evidence overturned.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: the damage scale

**OLD CLAIM.** Damage of roughly 50,000 per normal punch, recorded across
P-006B and P-008 as though it were an HP quantity.

**NEW EVIDENCE.** Two independent static paths fix a 1024 scale. The
number-refresh path at `0x0800AB9A` loads the accumulator at `obj+0x14`, adds
literal `0x3FF` from pool `0x0800AD84`, executes `asrs r2, r0, #0xA`, and passes
the result to formatter `0x0803DC96` with the format string at `0x0800AD88`,
which is `"%d"` in UTF-16LE. The heal counterpart at `0x0800FA80` computes
`(record[0] + 0x3FF) >> 10 << 10`, adds it to `+0x28C`, and clamps against
`maxHP << 10`; the explicit shift on an unscaled maximum is decisive.

Applied to the P-006B capture, raw HP `141884` displays as **139** and raw
damage `51338` as **51**, which is about 50 damage on a 139 HP wolf and roughly
three hits to kill. That matches firsthand gameplay, which the earlier figures
did not.

**RESOLUTION.** `target+0x28C` and `record+0x18` are **fixed-point with ten
fractional bits**, not raw HP. Displayed value is `(raw + 1023) >> 10`, a
ceiling divide. HP is not a multiple of 1024 (`141884 mod 1024 = 572`), so the
field carries real fractional residue. This is a different scale from the 8.8
world position at `0x0800FE78`; the two must not be conflated. Every previously
recorded damage figure needs division by 1024 to become player-facing.

### The critical discriminator

`0x0800E94E` tests `record+0x10` and branches: zero selects spawner mode 3 with
flag 0, nonzero selects mode 4 with flag 1. The flag reaches number-object
`+0x1C`, and `0x0800AB6A` uses it to choose asset `0x0806F150` or `0x0806E050`
from context table `0x08071700`. The heal path `0x0800E97E` uses mode 6, so mode
is the number *type* selector.

Run `20260828-213108-fab01490` broke at `0x0800FA2A` with `--dump-register r1`
and took 60 stops. Across the 59 usable records `record+0x10` was the **sole**
field separating the 2 special hits from the other 57: every other offset was
either constant across all hits or was the damage magnitude itself.

**CONFIRMED**, static branch plus runtime discrimination.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: the critical multiplier

**OLD CLAIM.** `REFERENCE.md:273`, from the retail instruction booklet, records
a critical hit as exactly twice normal melee damage. P-008 relied on this to
refuse the 1.43x and 1.50x outliers.

**NEW EVIDENCE.** Both flagged hits are exactly three halves of an integer base
that lands on the same 38-raw-unit lattice all damage uses, and both bases fall
inside the observed normal range of 47804 to 52440:

```text
76494 = 1.5 * 50996      (50996 divisible by 38)
75924 = 1.5 * 50616      (50616 divisible by 38)
```

Normal hits were n = 57, mean 50250. All damage values, critical and normal
alike, are multiples of 38 raw units.

**RESOLUTION.** The multiplier is **exactly 1.5**, and the documented 2x is
contradicted for this game. The P-008 outliers are **reclassified as genuine
critical hits**; the P-008 refusal was correct on the evidence then available.

### Producer trace: two routes attempted and failed

Recorded so future work does not repeat them.

Route 1, walking up from the consumer. Run `20260828-213908-6dd2f261` broke at
`0x080187A8` for 60 stops; LR was `0x0801902A` on all 60. That sits inside
`0x0801900A`, a generic behavior-tree child iterator that walks `node+0x10[i]`,
calls each child through vtable `+0x04`, ANDs results and early-exits on 2.
Above it are only `0x08019298`, a thin node-type dispatcher, and composite nodes
`0x08706C94`, `0x086FDBC8` and `0x08706C30` carrying the documented
`{entry, update, exit, count, child[]}` layout. Node `0x08706C30` contains
`0x0801920F`, the P-006B HURT entry, so this chain is the **reaction tree**,
downstream of damage. The arithmetic completes before the tree is entered.
`0x0800FA2A` also has zero direct BL callers, reached only through
relative-vtable dispatch as P-006A found for `0x08039182`.

Route 2, a write watchpoint on the damage field. The record is stack scratch at
`0x03007D3C`, so `+0x18` is `0x03007D54`. Run `20260828-214512-d8e5d344` armed a
4-byte Z2 write watchpoint there for 40 stops and caught only two program
counters in a fixed repeating cycle with no gameplay ticks: `0x08007E4C`
(LR `0x08007E34`) and `0x08029CE2` (LR `0x08029CCC`), both unrelated
stack-local sprite and position writes reusing the slot. The address is
meaningful only during the damage call, so a persistent watchpoint cannot
isolate the producer regardless of tuning.

Both failures are **structural**, not sampling shortfalls.

### Static scans deliberately rejected

Four scans were run and their output discarded rather than reported, because
none discriminated and mining them would manufacture a false lead of exactly the
kind P-008 produced: a relative-table scan yielding 230 arithmetic coincidences,
stores to `[rN,#0x18]` yielding 584 sites, record-builder shape matching
yielding 50+, and `lsls #10` proximity yielding 40+. No candidate from these is
recorded, and none should be revived.

### Corrections made during this ticket

`record+0x00` was briefly read as a class discriminator because the two critical
hits carried EWRAM pointers where normal hits carried a ROM pointer. Checking
the full set refuted it: flag=0 hits show the same EWRAM values. It is
uninitialized stack scratch. `+0x34` and `+0x38` were likewise considered as STR
inputs and refuted; they vary continuously without tracking the flag.

### Limits

Only 2 critical events were observed, so 2-of-59 is a raw count and **not** a
probability estimate. Both observed bases were even multiples of 38, so the
multiply landed exactly and the rounding rule for an odd base is **UNKNOWN**.
Whether criticals select a distinct reaction or knockback path was not reached.
The claim that the critical asset renders yellow is not established, only that
it is the distinct critical-side asset.

### Status

**PARTIAL.** Discriminator, multiplier, fixed-point scale and presentation
branch are confirmed. The RNG source, the STR probability formula, the producer
of `record+0x10`, and the exact site of the 1.5 multiply are **blocked** on a
hit-resolution-side search. Continuation is a new ticket, P-010 - Critical
Producer & Hit-Resolution Path, not an extension of P-009.

## P-010 Enemy Death, EXP & Drop Pipeline (2026-08-29)

### External research first

External sources established **player-visible behavior only**; RE established
the entire precision layer. This ticket is the clearest example so far of the
standing method.

The decisive artifact was the Data Crystal RAM map for this game. It is
fetch-blocked by a human-verification interstitial on both `curl` and WebFetch;
the working route is the Wayback mirror, which is worth recording for reuse:

```text
curl -sL "https://web.archive.org/web/2024/https://datacrystal.tcrf.net/wiki/Dragon_Ball_Z:_Buu%27s_Fury/RAM_map"
```

It supplied current-character index `0x03001068`, Zeni `0x0300155C`, Goku XP
`0x03001584`, item count `0x0300114C`, and a per-character stat block stride of
`0x68`. GameFAQs supplied the character-switch glitch and the detail that the
enemy must be lured onto a **save point**.

Every address was then verified against our own ROM, because P-008 refuted a
published address set. The save-block base was confirmed independently from ROM
pool `0x086B7080`, which holds `0x03001068`, and the `0x68` stride was found in
executable code at `0x0801394A` and `0x080043DC`. External evidence narrowed
the search; it was never accepted as proof.

### Death to EXP timing

Run `20260828-234311-1426d3c4`, breakpoints `0x0800FA50` and `0x080139F8`, with
`p010_death_timeline.lua` supplying the shared tick. Wolf A: T_LETHAL 9630,
T_EXP 9631. Wolf B: T_LETHAL 9744, T_EXP 9745.

**`T_EXP - T_LETHAL` = exactly 1 gameplay tick.** Do not round to "immediate".

HP goes negative at the lethal write (`-22390`, `-24252`) before `0x0800FA56`
zeroes it, so `HP <= 0` is a genuine signed test on a value transiently holding
the overkill amount.

### The amount/recipient asymmetry

The award **amount** is fixed at reward-object creation with the equipment bonus
already applied; the **recipient** is resolved one tick later at payout. This is
the mechanism behind the documented save-point switch glitch, derived from the
binary rather than from the anecdote.

Evidence for amount-at-creation: reward object `+0x08` read 225 unequipped
(`20260829-000534-be15deff`) and 271 equipped (`20260829-000912-69c3fb0e`).
Evidence for recipient-at-payout: `0x080043DA` reads the index with
`ldrb r2,[r0]` and multiplies by `0x68` at `0x080043DC`, inside the payout call.
LR was `0x08011A5E` on every stop, runtime-confirming award-on-destroy from the
refcount destructor loop `0x08011A1E`.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: the 300 award

**OLD CLAIM.** An early capture showed awards of 300 then 225, suggesting the
per-wolf award varied.

**NEW EVIDENCE.** A clean run gave four consecutive awards of exactly 225. The
300 appeared only on the first stop of the earlier run.

**RESOLUTION.** The 300 was the tail of an award already in progress when the
breakpoint armed. Wolf base EXP is a constant **225**.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: the +46 bonus

**OLD CLAIM.** A single unexplained `+46` was measured; `46/225 = 20.44%` is not
a round percentage, so additive was recorded as "more plausible than a
multiplier" and explicitly unproven.

**NEW EVIDENCE.** the maintainer isolated the two items: 1 Ton Armbands alone gave 248,
1 Ton Boots alone gave 248, both gave 271. Run `20260829-000057-5b79657e`.

**RESOLUTION.** Each item contributes exactly **+23**, and composition is
**additive**: `225 + 23 + 23 = 271`. Multiplicative is refuted by an exact
integer, since `225 * (248/225)^2 = 273.35` gives 273, not 271.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: the award queue

**OLD CLAIM.** `0x080033D2` was read as popping a queued EXP award, making it a
candidate site for the bonus arithmetic.

**NEW EVIDENCE.** The push side at `0x080033EA` stores `charblock+0x24`, the
character's *current* XP, on the same `0x68` stride.

**RESOLUTION.** The pair is an XP **save/restore**, not an award queue and not
the bonus arithmetic. The original reading was wrong.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: an apparent contradiction

**OLD CLAIM.** Captured reward objects carried an unmodified 225 while the
awarder received 271, appearing to contradict the static finding that `r1`
passes through the award path untouched.

**NEW EVIDENCE.** The equipped re-run showed reward objects carrying 271.

**RESOLUTION.** The two earlier kills were simply **unequipped**; that capture
had not recorded equipment state. The static reading was correct. This was a gap
in experiment design, not in the analysis.

### Drop structure

Two **independent** four-entry tables; reward value and presentation are
separate concerns.

Denominations: pointer table `0x086FC250`, amounts a plain integer at `+0x0C` -
`0x086FC260` = 5, `0x086FC378` = 25, `0x086FC790` = 50, `0x086FC8A8` = 100. The
live pickup reaches its record through `+0x60`. Runtime: Zeni `165 -> 325`
across 13 pickups, deltas only `{5, 100}`.

Visual tiers: 16-byte records at `0x086B759C`, reached from pickup `+0x10`,
resolved by a two-key lookup fully decoded at `0x08013E38` over exactly 4
entries with keys `(4,2) (10,4) (16,6) (24,10)`. Every +5 pickup used record 0;
the +100 used record 1. Reward-type identity therefore lives at object `+0x10`.

An earlier suspicion that the packed word at descriptor `+0x00` encoded the
amount was **refuted** by the wider dump: the amount is the plain u32 at
`[+0x60]+0x0C`.

### Item add

`0x08004448`: cap at `0xFA` (250, silent no-op), increment count, then store
`item_id & 0x0FFFFFFF` at `inventory + 0xE4 + 4 + old_count*4`. The top 4 bits
of each entry are a flag field, read back at `0x08004406-0x08004410`. Runtime:
item id `0x74`, count `0 -> 1`.

A real asymmetry: the XP writer (`0x080139F4`) and Zeni writer (`0x08017ED6`)
both use a readback-verify retry loop; the item writer at `0x08004464` does not.

### Level thresholds and cap - extra results

Pool literal `0x086B7080` holds the save-block pointer `0x03001068`; the XP
threshold table begins at `0x086B7084` with `0, 10, 40, 100, 200, 350, 560, 840,
1200, 1650, 2200, 2875, 3700, 4700, 5900, ...`, strictly increasing over at
least 150 entries. Lookup at `0x08013A08-0x08013A1A`. Level cap 200 at
`0x08013A00` (`cmp r6,#0xc8`).

Cross-check: captured XP began at exactly **3700**, threshold entry 12, so the
player had just reached level 13. The table lands on the observed value.

An earlier decode of this table read entries as `141249528` and similar; those
are ROM pointers, because the region below `0x086B7084` is a pointer table. The
thresholds start at `0x086B7084`.

### Tooling defect

`tools/runtime/p010_death_timeline.lua`'s `looks_like_actor()` is too loose and
produced **73 bogus LETHAL rows for 2 real kills** across 13,513 rows. The
defect did not reach any result: every value came from the breakpoint capture,
which is independent of the observer's own rows, and the observer's tick counter
was correct. Tighten discovery before trusting its SCAN or LETHAL rows.

### Status

**RESOLVED**, all 11 closure criteria met, with two bounded unknowns recorded as
research debts. The EXP bonus **arithmetic site** is upstream of reward-object
creation and unlocated; next anchor is the constructor, vtable `0x0804A820` at
object `+0x00`. The **drop roll** selecting a table index is unlocated, the same
producer-tracing class as the P-009 blocker; next anchor is the pickup-object
constructor on the death path. Drop probability was **not** estimated
statistically; the observed 25-to-1 split is a raw count, not a rate.

## TOOLKIT-012 correction: `0x08046AA4` is a call veneer, not a point query

**OLD CLAIM.** Entries above at lines 910, 1022, 1291, 1338, 1461, 1741, 2090
and 2129 describe a "point query" or "overlap/query" function at `0x08046AA4`
(and `0x08046AA6`), and read `FUN_0803B4FC` as ray-marching "against map
collision via `FUN_08046AA4` (point query on `*param_2+0x54` room data)".

**NEW EVIDENCE.** Disassembly of the canonical image at that address:

```
08046AA0  bx r0     08046AA8  bx r4
08046AA2  bx r1     08046AAA  bx r5
08046AA4  bx r2     08046AAC  bx r6
08046AA6  bx r3     08046AAE  bx r7
```

This is the gcc `__call_via_rN` indirect-call thunk block. `0x08046AA4` performs
no query; it jumps to whatever address is in `r2`. `docs/consumer-analysis.md:252`
already identified `0x08046AA2` correctly as "the Thumb `BX r1` veneer".

At the `FUN_0803B4FC` call site, `[base+0x54]` is loaded and added to the base to
form `r2` **as the call target**, so `+0x54` is a self-relative *virtual method
slot* taking `(object, point*)` and returning a boolean - not a pointer to room
data.

**RESOLUTION.** The predicate those entries describe is real, and a movement
guard does route through it (57 such call sites exist ROM-wide). What is wrong is
the callee identity: it is a virtual dispatch, and the vtables involved resolve
to IWRAM addresses built at load time, not to static ROM tables. No shipped
capability depended on the old reading. See
[collision evidence](COLLISION_FORMAT.md).
