# Reverse-Engineering Research Ledger

Durable brain of the Webfoot reverse-engineering programme
(`OX-AUTO-RE`). Read this file first every loop iteration. Keep it compact;
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

P-003/P-004 contact resolution. Human-provided combat state validated
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
| P-004 | damage | One complete damage event: hit detection -> damage calc -> HP mutation -> reaction/knockback/i-frames -> death | Closes the combat loop end-to-end | none yet | Follow melee hitbox accept into enemy entity HP mutation | BLOCKED by P-003 |
| P-005 | enemy-ai | One simple enemy's update loop (idle/detect/approach/attack/receive-damage/death) | Enemy behavioral spec | `candidate_caller_08021CC0` periodic dual-point sensor candidate | From entity spawn table, pick simplest enemy class and trace update | BLOCKED by P-001 |
| P-006 | differential | Compare recovered Buu player/combat functions against LoGII/LoG1 material (manual structural comparison only) | Answers what combat feel is shared vs changed | recomp repos lack generated code; Legacy repo has LoG1 tooling/VM data | After P-002/P-003 produce constants/state machines, compare shapes/constants with Legacy repo data | DEFERRED until P-003 |
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
research-lane findings only.)

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
  - DESPAWN METHODS DECODED (progress 13 addendum): both "deciders"
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
    entry, now armed with confirmed rel-table mechanism.
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
    (node, actor). Decompile `FUN_08029FE6` fully next - it already
    showed dispatcher LR behavior (`0x08029FF1`).
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
  - Full decompile mapped (stack-slot to rect-field assignment):
    - player rect via global-form `cand_body_bounds_0800FE78(&out)`:
      `x0p=iStack_24, y0p=iStack_20, x1p=iStack_1C, y1p=iStack_18`;
    - target rect via `cand_body_bounds_0800FE78(&out, target)`:
      `x0t=iStack_34, y0t=iStack_30, x1t=iStack_2C, y1t=iStack_28`.
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
    - expands target rect by facing-directional margins
      (`x0-4, y0+3, x1, y1-6` shape);
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
