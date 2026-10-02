# DragonByte Z - complete roadmap to 100% and v1.0

A capability-driven plan for turning the Webfoot SDK into a complete, shippable
Buu's Fury authoring environment.

| | |
| --- | --- |
| **Status** | Canonical product roadmap. Approved by the owner and adopted into the repository by `ROADMAP-TO-1-0-ADOPTION-001`. |
| **Source** | `DragonByte_Z_Complete_Roadmap_to_1_0.docx`, adapted faithfully into repository-native Markdown. The roadmap substance is that document's; capability names, states and the denominator are reconciled against the registry. |
| **Project head at planning baseline** | `a commit since folded into its successor` |
| **Authority for "what is shipped"** | [`src/data/capabilities.json`](../src/data/capabilities.json) - this document never overrides it. |

## Current product status

**20 / 24 capabilities - 83%**

| Family | Progress |
| --- | --- |
| READ | 5 / 5 |
| EDIT | 8 / 8 |
| AUTHOR | 3 / 7 |
| DELIVER | 4 / 4 |

Variable-length dialogue authoring: **merged, deployed, runtime-proven.**

Map editing (Phase 2): **complete.** Tile painting (`MAP-TILE-PAINT-001`,
2026-09-25), chunk creation (`MAP-CHUNK-AUTHORING-001`, 2026-09-25), map resizing
and layer authoring (`MAP-RESIZE-AND-LAYERS-001`, 2026-09-26) and warp and
connection editing (`MAP-WARPS-AND-CONNECTIONS-001`, 2026-09-28) have all shipped,
each with its own runtime proof. Tile painting was delivered at the engine's own
editable unit - one four-byte chunk-cell reference to an existing 256x256 chunk -
not as individual 8x8 tile authoring. Warp and connection editing shipped together
with its map surface: every supported transition is drawn on the map as the region
that triggers it, where a click selects it and a drag moves it as one undoable
gesture.

Next: **Phase 3 - graphics and actor authoring. NEXT, not started.**

> **North star.** An author should be able to create a genuinely new playable
> piece of Buu's Fury content without manually editing a ROM offset.

## Executive summary

DragonByte Z has crossed the boundary from "ROM editor" toward "content
authoring system." The project can already read all major supported domains,
safely edit several existing-content surfaces, author entities/behavior/text in
defined forms, build safe derivatives, expand the ROM to 16 MiB, allocate new data
above the retail image, preserve allocation provenance, and prove the result in
the retail engine. Variable-length compressed dialogue is now merged and live: an
existing 32-byte dialogue record was grown to 72 bytes, its container was re-laid
out, 470 true references were updated, and the complete longer line was observed
in-game.

The roadmap is optimized around **user-visible capabilities, not audit-finding
order**. The 24-item capability registry remains the fixed definition of "100%
feature complete." Audit findings become risk controls attached to the feature
paths that need them. This prevents foundational quality work from silently
becoming an endless roadmap of its own.

The recommended path to 24/24 is: stabilize the Workbench; finish map editing
(tile painting -> chunk creation -> resize/layers -> warps) - **now complete**;
finish graphics authoring (graphics import -> sprites/animations/frames ->
appearances) - **next, not started**; then make new-map creation the final
composition capability. After 24/24, run a creator-UX/release-candidate phase and a
final v1.0 ship phase.

## What this document is, and what it is not

Three artifacts answer three different questions. None of them answers another's,
and none silently takes over the roadmap:

| Artifact | Question it owns |
| --- | --- |
| [`src/data/capabilities.json`](../src/data/capabilities.json) | **What does "feature complete" mean?** It owns the fixed 24-capability denominator. |
| `docs/ROADMAP_TO_1_0.md` (this file) | **What order do we build the remaining product in?** It owns the long-term route to 24/24 and v1.0. |
| [`research/PROJECT_CODE_QUALITY_AUDIT.md`](research/PROJECT_CODE_QUALITY_AUDIT.md) and its remediation records | **What technical risks and debt exist?** It is a risk register - not automatically the product roadmap. |

Two supporting documents are deliberately **not** planning authority:

- [`research/POST_LOGX_IMPLEMENTATION_ROADMAP.md`](research/POST_LOGX_IMPLEMENTATION_ROADMAP.md)
  is the LOGX research line's **implementation queue** (`FIX-*`, `TOOLS-*`,
  `WRITE-*`, `NEW-*`). It is engineering detail beneath this product roadmap, and
  parts of it are already executed. Where the two name the same work, this file
  owns the phase, the capability exit and the progress number.
- [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) and its `PROJECT_STATE_*.md`
  continuations are historical state snapshots and durable links to evidence,
  not a forward plan.

## Contents

1. Current state and what has already been proven
2. Definition of 100%, feature complete, and shippable
3. What mature tools teach us
4. Roadmap design principles
5. The complete roadmap to 24/24
6. Phase 1 - Workbench safety baseline
7. Phase 2 - Complete map editing
8. Phase 3 - Complete graphics authoring
9. Phase 4 - New map authoring and 24/24
10. Phase 5 - Creator UX and release candidate
11. Phase 6 - v1.0 shipping gate
12. Capability completion matrix
13. Domain addressability strategy
14. Quality, testing, and evidence rules
15. Golden end-to-end acceptance project
16. What we deliberately do not put before 1.0
17. Post-1.0 roadmap
18. Roadmap files and governance
19. References and comparative research

---

## 1. Current state and what has already been proven

The current public product is **20/24 capabilities (83%)**. The denominator is
intentionally unchanged. Tile painting, chunk creation, map resizing with layer
authoring, and warp and connection editing each moved the count because each is a
new capability an author can use, delivered at the engine's own unit rather than as
a finer one the format does not have. Variable-length dialogue strengthened an
existing capability rather than inventing one, which is why it did not move the
count. The important point is that the infrastructure under those 20 shipped
capabilities is substantially stronger than the percentage alone suggests.

| Area | Current | Status | Shipped today |
| --- | --- | --- | --- |
| READ | 5 / 5 | Complete | Shell; atlas/search; record inspection; sprite/animation/palette browsing; Map Browser |
| EDIT | 8 / 8 | Complete | Dialogue; palette recolor; object placement; map layout chunk-cell replacement; tile painting (chunk-cell, 2026-09-25); chunk creation (2026-09-25); map resizing and layer authoring (2026-09-26); warp and connection editing (2026-09-28) |
| AUTHOR | 3 / 7 | 4 missing | Authored entities; behavior/scripts; text beyond retail slot |
| DELIVER | 4 / 4 | Complete | Validate/build; safe Save As; derivative provenance/reopen; launch |

### Major foundations already complete

- **Safe output and immutable-source behavior.** Source-alias protection,
  destination safety, staged publication, rollback, manifest association and
  generated-allocation authorization are centralized in the production write
  path.
- **Compression correctness.** Retail packed-stream termination was
  reverse-engineered, and production packing now emits and validates the explicit
  end marker.
- **ROM/profile/atlas identity.** The Workbench refuses mismatched atlas/profile/
  base identity before incompatible session state becomes active; trusted
  derivatives resolve against their canonical base.
- **Single binary-format authority.** The duplicated map/graphics decode stacks
  were consolidated, so production write paths no longer depend on an independent
  export-side interpretation.
- **Capacity and allocation.** The 8 MiB retail image has only **256 bytes**
  currently `VERIFIED_FREE` under the production proof standard; 16 MiB
  derivatives are engine-proven, giving **8 MiB of raw expansion**. A
  deterministic production allocator can reserve authorized expanded spans,
  record provenance, reopen them and prevent reuse.
- **Runtime expansion proof.** A real packed dialogue resource was allocated at
  file offset `0x00800000` / GBA `0x08800000` and consumed successfully by the
  retail engine.
- **Variable-length compressed dialogue.** An existing line grew from 32 decoded
  bytes to 72; the tool re-authored the durable handle, shifted 443 following
  records, updated 470 true references, left 15 unrelated equal-valued words
  untouched, repacked and relocated the container, reopened the derivative, and
  displayed the full longer line in-game.
- **Independent review gate.** Every nontrivial code-bearing change is reviewed
  by someone who did not implement it, against the frozen diff, its tests, the
  architecture and the underlying evidence. See [`REVIEW.md`](REVIEW.md).

### The most important capacity conclusion

> The future strategy is **ROM expansion + controlled allocation + per-domain
> addressability proof**, not scavenging "empty-looking" retail bytes.

Checkpoint A measured only **256 bytes** as production-safe canonical free space.
Thirteen of sixteen inventoried domains can encode above-EOF addresses, but only
packed dialogue is runtime-proven there today. The allocator therefore has a
global storage model plus a domain-specific addressability policy; it does not
pretend the full 8 MiB expansion is universally usable.

**Expanded storage is not globally proven for every resource family.** See
[§13](#13-domain-addressability-strategy).

## 2. Definition of 100%, feature complete, and shippable

### 2.1 100% feature complete = 24 / 24

The existing 24-capability registry remains the **fixed denominator**. Changing
it now would make progress percentages historically meaningless. "100%" means
all 24 currently-defined product capabilities are shipped and independently
validated.

The four missing capabilities are the only items that move the score from 83% to
100%. Graphics import is the next one, and it has not started:

| Family | Missing capability |
| --- | --- |
| AUTHOR | graphics import (NEXT - not started) |
| AUTHOR | new sprite / animation / frame authoring |
| AUTHOR | new appearance definitions |
| AUTHOR | new maps |

### 2.2 24/24 is not automatically v1.0

Feature completeness and release readiness are **different milestones**. Once the
registry reaches 24/24, DragonByte Z enters a dedicated release-candidate phase
focused on workflow quality, recovery, diagnostics, packaging, documentation,
distribution and end-to-end dogfooding. A product can have every checkbox and
still be frustrating or unsafe to use.

**24/24 means `FEATURE COMPLETE`. It does not mean `v1.0 SHIPPED`.** Keep those
milestones separate.

### 2.3 Product definition for v1.0

> **v1.0 north-star acceptance statement.** Starting from a clean supported ROM,
> an author can create a genuinely new playable scene with original map edits,
> actors, scripts/dialogue, graphics, transitions, safe allocation and a
> distributable patch - without manually editing a ROM offset.

## 3. What mature tools teach us

The roadmap is intentionally informed by mature editors rather than by
reverse-engineering milestones alone. The useful comparison is not "do they
understand the same binary format?" but "what makes them feel like finished
authoring environments?"

| Reference tool | What a mature product teaches us | Refs |
| --- | --- | --- |
| GB Studio | Scenes, actors, triggers, scripting events, Play / Run From Here, ROM export, and a debugger exposing runtime state and VRAM constraints. Creation, iteration, debugging and engine-limit visibility belong in one workflow. | [1-3] |
| Porymap | Map tiles, collision, events, connections, properties, tileset editing, region-map editing, and undo/redo for painting. A complete map tool must edit both geometry and gameplay topology, not merely render maps. | [4-5] |
| Tiled | Tile layers, object layers, brushes/selections, terrains and automapping, projects/worlds, plugins/scripting, templates/custom properties, and multiple export paths. Mature editors reduce repetitive work and make authored content composable and interoperable. | [6-8] |
| CoilSnake | Deconstructs a ROM into ordinary editable assets and rebuilds a modified ROM; its scope is broad enough to make entirely new games in the EarthBound engine. The end state is content authoring, not byte editing. | [9] |
| Floating IPS / BPS | Patch creation and application are normal distribution primitives for ROM-hacking releases, with both GUI and CLI workflows. A shipped authoring tool needs a clean legal distribution path, not merely a generated ROM. | [10] |

### The common pattern

Mature tools converge on five product qualities:

- Authors manipulate **semantic objects** (maps, actors, scripts, tiles, sprites),
  not raw offsets.
- **Iteration is fast**: edit -> run/preview -> diagnose -> adjust.
- **Engine limits are visible** before they become mysterious corruption.
- **Undo/recovery/project persistence** are first-class, not afterthoughts.
- **Output is reproducible and distributable**, with documentation sufficient for
  a new user to succeed.

These references explain the roadmap's shape. They are not architectural
templates: DragonByte Z remains constrained by Buu's Fury's retail binary engine
and this repository's evidence discipline.

## 4. Roadmap design principles

1. **Capabilities drive the roadmap.** The audit is a risk register, not the
   feature plan. A finding blocks a feature only when its failure path intersects
   that feature.
2. **Finish coherent author workflows.** Prefer tickets that move an author from
   "can inspect" to "can create and play" over isolated decoding milestones.
3. **Prove addressability just-in-time.** Do not launch another giant campaign to
   runtime-prove all pointer domains. Prove a domain when the capability that
   needs it is built.
4. **One production authority per concept.** Research oracles may remain
   independent, but shipping decode, allocation, write, identity and provenance
   behavior each have one production owner.
5. **Fail closed, then widen deliberately.** Unsupported lengths, ranges,
   handlers, pointers and output paths must refuse cleanly rather than guess.
6. **Runtime proof for engine-facing claims.** Static encodability is not engine
   proof. Major new authoring surfaces close only when the retail engine consumes
   the result.
7. **No broad manual test suites.** Implementation feedback stays focused;
   configured CI owns broad validation after the merge request exists.
8. **Keep the denominator stable.** The 24 capabilities define public progress.
   Infrastructure improvements strengthen capabilities but do not inflate the
   score.
9. **New maps are the final composition capability.** By the time map creation is
   implemented, tiles/chunks/layers/warps/graphics/actors/scripts/allocation
   should already be independently proven.
10. **1.0 has a dogfood gate.** 24/24 is necessary but not sufficient; a complete
    authoring journey must work end-to-end from a clean ROM.

## 5. The complete roadmap to 24/24

The roadmap is optimized around dependency order and author value. Exact ticket
boundaries may change, but phase order and capability exits should remain stable
unless new evidence proves a dependency wrong.

| Phase | Focus | Exit condition | Progress |
| --- | --- | --- | --- |
| 0 - Land current work | Completed | Variable-length dialogue merged, CI green, deployed, live wording verified. | 16/24 |
| 1 - Authoring-safety baseline | Completed | CQA-05/06 together (**CLOSED** 2026-09-24); CQA-07/08 together (**CLOSED** 2026-09-25); Phase 1 complete. Preserve staged edits/undo, totalize GUI errors, remove pathological palette work, ensure CI actually executes GUI dependencies. | 16/24 |
| 2A - Tile painting | Map editing | Brush/pick/erase/fill/selection + undo/redo using existing tile vocabulary. **COMPLETE** 2026-09-25: delivered at the engine's own unit, one four-byte chunk-cell reference to an existing chunk; retail-engine display runtime-proven after a genuine map rebuild. | 17/24 |
| 2B - Chunk creation | Map editing | Create/materialize new chunk data; allocate/relocate safely; prove the map/chunk pointer domain the feature needs. **COMPLETE** 2026-09-25: a project-authored chunk body is allocated above the original ROM's end, and the retail engine's own loaded layer record was observed referencing it. | 18/24 |
| 2C - Resize + layers | Map editing | Resize grids, create/relocate layer resources, preserve handler semantics, validate boundaries and reopen. **COMPLETE** 2026-09-26: the grown grid is re-emitted above the original ROM's end, the map root is repointed, and the added ground is displayed at runtime. | 19/24 |
| 2D - Warps / connections | Map editing | Visual destination editing, connection/warp consistency, runtime transition proof. **COMPLETE** 2026-09-28: a transition is retargeted through the project and one the image does not contain is authored above the original ROM's end; every supported transition is drawn and dragged on the map as its trigger region; and a human-operated run confirmed the retail engine consumes an authored transition. | 20/24 |
| 3A - Graphics import | Graphics authoring | Image import -> quantization -> tiles/container encoding -> allocation -> runtime proof; prove graphics-domain expanded addressing as needed. **NEXT** (not started). | 21/24 |
| 3B - Sprite / animation / frame authoring | Graphics authoring | Create new sprite definitions, frames/pieces/OAM and animation records; table expansion where necessary. | 22/24 |
| 3C - Appearance authoring | Graphics authoring | Create new appearance definitions that bind authored graphics into game-visible actors. | 23/24 |
| 4 - New maps | Final capability | Create MapEntry + layers/chunks + objects + warps + scripts/dialogue; expand/relocate tables; prove runtime scene. | 24/24 |
| 5 - Creator UX / RC | Release candidate | Resource budget panel, warnings, Run From Here, recovery/migration, navigation, consistent undo, docs, patch export, end-to-end dogfood. | 24/24 |
| 6 - v1.0 ship | Release | Packaging, hardware smoke, final high-risk debt disposition, release notes, tutorials, signed/reproducible artifacts where practical. | v1.0 |

### Phase 0 - current state / landing (complete)

The variable-length dialogue work is **already merged**. Phase 0 required no
implementation and is recorded here only so that the roadmap's starting point is
explicit: `DIALOGUE-VARIABLE-LENGTH-001` completed, merged and was verified live
at the planning baseline `a commit since folded into its successor`. There is no Phase 0 work outstanding, and
starting it again would be a no-op.

### Recommended tentative ticket packages

Ticket boundaries are proposals for a human to authorize, not commitments. The
dependency order, not the naming, is what must be honoured.

- `CQA-05-06-WORKBENCH-STATE-AND-ERRORS-001` - staged-state preservation + total
  GUI error boundary. **COMPLETE** 2026-09-24.
- `CQA-07-08-WORKBENCH-PERF-AND-CI-001` - eliminate pathological palette
  recomputation + make CI execute the shipping GUI dependencies. **COMPLETE**
  2026-09-25.
- `MAP-TILE-PAINT-001` - complete tile painting UX on existing map resources.
  **COMPLETE** 2026-09-25.
- `MAP-CHUNK-AUTHORING-001` - create, allocate, reference, reopen and
  runtime-prove new chunks. **COMPLETE** 2026-09-25.
- `MAP-RESIZE-AND-LAYERS-001` - structural grid/layer editing. **COMPLETE**
  2026-09-26.
- `MAP-WARPS-AND-CONNECTIONS-001` - author and validate transitions/connections,
  and draw and edit their trigger regions on the map. **COMPLETE** 2026-09-28:
  [`research/MAP_WARPS_AND_CONNECTIONS.md`](research/MAP_WARPS_AND_CONNECTIONS.md).
- `GRAPHICS-IMPORT-001` - import original artwork into the retail graphics
  formats. **NEXT** (not started).
- `SPRITE-ANIMATION-AUTHORING-001` - new sprite/frame/animation resources.
- `APPEARANCE-AUTHORING-001` - new appearance definitions and bindings.
- `MAP-AUTHOR-NEW-001` - new map/scene creation, the 24/24 capability.
- `GOLDEN-AUTHORING-SLICE-001` - end-to-end dogfood project.
- `PRODUCT-HARDENING-RC1-001` - recovery, packaging, patch export, docs,
  shipping-path audit closure.
- `RELEASE-1.0` - final distribution and verification.

## 6. Phase 1 - Workbench safety baseline

This phase should be short and bounded. It exists because the next several
capabilities are GUI-heavy and would be frustrating to build on top of known
state-loss, error-boundary, performance and CI blind spots. **These are
product-risk gates, not the roadmap itself.**

### 6.1 CQA-05 + CQA-06: state and errors

**COMPLETE (2026-09-24).**
The four requirements below were the exit condition and are now met; they are kept
here as the record of what that exit required.

- Project mutation must not silently destroy staged map/layout state or undo
  history.
- Open-ROM/session failures must cross one total error boundary, so the GUI never
  degrades into a dead click.
- ROM/session changes and project-content changes must be separate events with
  explicit ownership.
- Acceptance must include dirty-state prompts or preservation semantics
  appropriate to the operation, plus focused regression tests.

### 6.2 CQA-07 + CQA-08: responsiveness and honest CI

**COMPLETE (2026-09-25).**
The four requirements below were the exit condition and are now met; they are kept
here as the record of what that exit required.

- Palette/editor repaint must not reread or reparse an entire project, nor rescan
  the whole graphics corpus, per UI element.
- Cache/index only what is needed; keep behavior deterministic and invalidate on
  actual relevant changes.
- CI must install the GUI/research dependencies required by shipping tests, and
  should fail when entire shipping files are skipped unexpectedly.
- This is the point to prevent another situation where PySide6 absence makes
  green CI hide real Workbench regressions. At baseline `CI` installed only
  `.[dev]`, so whole portable test families were skipped at import, including
  the entire Workbench suite.

**Not part of the Phase 1 exit:** general CQA-10 cleanup, atlas-seed overlay
cleanup, or unrelated low/medium audit debt. Those remain attached to the paths
that actually need them, or to release hardening.

**PHASE 1 - AUTHORING-SAFETY BASELINE: COMPLETE.** All four findings are
**CLOSED**: CQA-05 and CQA-06 by `CQA-05-06-WORKBENCH-STATE-AND-ERRORS-001`
(2026-09-24), and CQA-07 and CQA-08 by
`CQA-07-08-WORKBENCH-PERF-AND-CI-001` (2026-09-25). The product capability count
did not move for this phase (it stood at **16 / 24 (67%)** when the phase
closed), because this phase is safety infrastructure
and ships no capability. Audit finding CQA-10 remains **PARTIAL / IMPROVED** and
is not closed by this work.

## 7. Phase 2 - Complete map editing (4 capabilities)

Map editing should become a coherent progression rather than four disconnected
features. Each step builds on the previous one and should reuse the same map
view/model, undo system, allocator, identity/provenance rules and runtime proof
workflow.

**PHASE 2 - COMPLETE MAP EDITING: COMPLETE (2026-09-28).** All four capabilities
have shipped and each carries its own runtime proof. EDIT now reads 8 / 8 and the
product stands at **20 / 24 (83%)**.

### 7.1 Tile painting -> 17/24

**COMPLETE (2026-09-25).**
The requirements below were the exit condition and are now met; they are kept here
as the record of what that exit required.

Deliver brush, picker, eraser, fill, rectangular selection/copy/paste,
palette/tile-bank awareness and undo/redo. The first version may be constrained to
the currently addressable tile/chunk vocabulary; it does not need imported
artwork yet. The UX target is that editing a map feels like a map editor, not a
cell-replacement dialog.

Delivered: painting, drag painting, eyedropper/pick, undo, redo and Apply/Revert on
one history, scoped to the currently addressable vocabulary exactly as allowed. The
constraint resolved to the engine's own unit, so the shipped brush selects an
existing chunk and paints a 256x256 chunk cell; an eraser, fill and rectangular
selection/copy/paste were **not** delivered, and the capability ships without them
because the format's editable unit is the cell reference, not an individual 8x8
tile.

### 7.2 Chunk creation -> 18/24

Create and materialize new chunk resources rather than merely mutating an
existing chunk. Use the production allocator when growth cannot fit in place.
This ticket owns the just-in-time addressability proof for the map/chunk pointer
domain it needs. Reopen must preserve authored chunk identity and allocation
reservations.

**COMPLETE (2026-09-25).**
Delivered: a project-authored chunk is a new 32x32 screen-entry body with its own
durable identity, composed only from the screen entries its template layer already
draws, allocated above the original ROM's end and resolved from identity to address
at build time. The retail engine's own loaded layer record was observed referencing
the authored body, with the other three layers byte-identical.

### 7.3 Map resizing and layers -> 19/24

Allow an author to change grid dimensions and supported layer structure.
Relocate affected pointer arrays/resources safely, preserve the special-handler
distinctions discovered by CQA-04, and fail closed for layer types that remain
read-only. Add visible budget/limit information where fixed dimensions or handler
constraints apply.

**COMPLETE (2026-09-26).**
Delivered: a supported dominant layer's chunk grid can be grown, top-left anchored,
so every existing cell keeps its coordinate; the layer record is re-emitted whole
above the original ROM's end and the map root's own layer-slot field is repointed at
it; and one of the map's four fixed layer slots can be activated as a new supported
visual layer. Growth only - shrinking is refused - and read-only layer forms fail
closed with their own reason.

### 7.4 Warp/connection editing -> 20/24

Turn the currently-read connection graph into an authoring surface. Show
source/destination clearly, validate destination identity, keep paired and
bidirectional relationships consistent where the engine contract requires it, and
prove the transition in-game. This should feel closer to Porymap's
event/connection workflow than to editing pointer words.

**COMPLETE (2026-09-28).**
[`research/MAP_WARPS_AND_CONNECTIONS.md`](research/MAP_WARPS_AND_CONNECTIONS.md).
Delivered: the Maps editor's Warps mode lists a map's connections and retargets a
selected transition's destination, arrival and facing through the project, with
Apply and Revert on the editor's own undo history; the Create transition form
authors a transition the image does not contain, under a durable identity of the
form `map:NNNN/transition:<name>`, composed over a same-map template and emitted
with an expanded record-pointer array above the original ROM's end; and the map
canvas draws every supported transition as its trigger region, selects that
connection on a click and moves the region as one undoable gesture. A human-operated
run confirmed the retail engine consumes an authored transition. The 169-class
family, shared connection roots, unresolved record bytes and every unsupported form
fail closed with their reason stated rather than being forced.

## 8. Phase 3 - Complete graphics authoring (3 capabilities)

**PHASE 3 - GRAPHICS AND ACTOR AUTHORING: NEXT, NOT STARTED.** This is the next
phase in the order, and no work on it has begun: the first capability below,
graphics import, is chosen but not started.

Graphics authoring should follow the same pattern as variable-length dialogue:
the user performs a semantic edit, while the tool absorbs quantization, container
layout, relocation, reference updates, allocation, provenance and engine
constraints.

### 8.1 Graphics import -> 21/24

Import original user-provided artwork, quantize/validate it against Buu's Fury
palette and tile constraints, encode the correct graphics container,
allocate/relocate as needed, update references, reopen, and render in the retail
engine. This ticket owns the runtime proof for the graphics-container
addressability domain it actually uses. **NEXT - not started.** It is blocked on
allocation for payloads that change size and on a write path that can put a changed
graphic back.

### 8.2 New sprite / animation / frame authoring -> 22/24

Create new frame pieces/OAM definitions, frame resources, animation sequences and
sprite-definition entries. Expand/relocate tables only when evidence requires it.
Expose useful engine limits - piece counts, tile usage, palette constraints -
before build failure.

### 8.3 New appearance definitions -> 23/24

Create the appearance records that connect authored graphics to actors/entities.
Preserve semantic IDs and reopen behavior, prove a newly-authored appearance on a
real actor, and keep table/count constraints visible in the editor.

## 9. Phase 4 - New map authoring and 24/24

New-map creation is deliberately the **final** capability, because it composes
almost every other authoring system. Implementing it earlier would force the map
ticket to rediscover graphics, layers, objects, transitions, scripts and
allocation at the same time. **It should be treated as composition of
already-proven systems, not as the place where every subsystem is invented
simultaneously.**

### `MAP-AUTHOR-NEW-001` -> 24/24

- Create a new `MapEntry` with a stable project identity and profile-backed table
  ownership.
- Create the required layers/chunks and allocate their data through the
  production allocator.
- Populate placements/entities using the existing authored-entity machinery.
- Attach behavior/scripts and dialogue using already-shipped authoring paths.
- Create at least one connection/warp from an existing map into the new map and
  back out.
- Use imported/new graphics or existing assets as appropriate; **no manual offset
  entry by the author.**
- Expand/relocate the map table if the fixed retail count must change, with
  explicit runtime proof.
- Close only when the retail engine loads, renders, runs scripts in, and
  transitions through the newly-created map.

> **24/24 milestone.** At this point every capability in the fixed registry is
> shipped. Public feature progress may legitimately read 100%. The project is
> **feature complete** - but not yet automatically **release complete**.

## 10. Phase 5 - Creator UX and release candidate

This phase turns engineering completeness into a product a mod author can trust.
It should **not** add new denominator capabilities; it should make the 24
capabilities coherent, discoverable, recoverable and pleasant. **24/24 remains
unchanged throughout this phase.**

### 10.1 Resource Budget / Limits panel

A strong lesson from GB Studio is that old-console limits should be surfaced in
the editor rather than discovered through corruption or opaque build errors.
DragonByte Z should expose per-resource budgets using the evidence already
collected during capacity work.

| Resource | What the editor should surface |
| --- | --- |
| ROM allocation | canonical vs expanded; bytes used; allocation span; remaining proven capacity for the domain; addressability proof status |
| Maps | objects n/255; dimensions/chunks/layers; connection count; handler support; structural limits |
| Dialogue | decoded length; handle capacity; container/table constraints; current packed allocation |
| Sprites | definitions; frames; pieces/OAM; tiles/palettes; relevant table limits |
| Scripts | encoded size; references; opcode/variable constraints; branch/target validity |
| Addressability | canonical-only / expanded encoding-capable / expanded runtime-proven / unknown |

**This UI is not implemented by the roadmap-adoption ticket.** It is a Phase 5
product requirement, documented here so it is not rediscovered late.

### 10.2 Iteration and navigation

- `Run From Here` or an equivalent fast-launch workflow for the currently selected
  map/scene, where technically feasible.
- Cross-resource navigation: from a placement to its behavior, appearance, sprite,
  palette and dialogue; from a reference back to all owners.
- Consistent undo/redo across all interactive editors, with meaningful command
  labels and coalescing for brush strokes.
- Clear "why this cannot be authored yet" messages when a resource remains outside
  the proven format/addressability envelope.
- Build diagnostics that link errors back to the actual resource, instead of only
  showing offsets or stack traces.
- Author-friendly validation messages.

### 10.3 Project durability

- Versioned project/schema migration, so older extracted projects can be upgraded
  deliberately instead of failing mysteriously.
- Atomic project writes, and recovery from interrupted saves/builds.
- Clear dirty-state handling before ROM/session changes and project mutations.
- Deterministic build and provenance retention across reopen/rebuild.
- Documentation and tutorial workflow sufficient for a new user to succeed.

## 11. Phase 6 - v1.0 shipping gate

The final release gate is explicit. It prevents "24/24" from becoming a premature
release merely because every feature exists somewhere in the codebase.

Release requirements include at minimum:

- **Shipping-path correctness.** Zero unresolved critical/high defects on shipping
  paths. Remaining medium/low audit items are explicitly triaged rather than
  silently ignored.
- **CI honesty.** CI installs all dependencies required by shipping tests, does
  not silently skip whole shipping surfaces, and is the only place broad
  validation is routinely run.
- **Packaging.** A normal Windows user can install and run DragonByte Z without
  reproducing the development environment. Version and build identity are
  visible, and build/provenance safety holds.
- **Distribution.** Create a BPS patch from a verified base and generated
  derivative; **never distribute the commercial ROM.** Floating IPS/BPS is
  suitable prior art for this workflow [10].
- **Supported-ROM identity validation.** The release validates supported-ROM
  identity and fails closed on mismatch.
- **Clean install / first-run flow.**
- **Hardware smoke.** At least one derivative produced by the release build is
  tested on real hardware or a flashcart, in addition to emulator coverage.
- **Emulator smoke test.**
- **Documentation.** Install guide, first-project walkthrough, map editing,
  dialogue, graphics, scripts, build/export, troubleshooting, engine limits, and
  an evidence/provenance explanation.
- **Example project.** Ship or document a legal example/tutorial project that
  exercises the creator workflow without redistributing proprietary assets - one
  complete tutorial/example mod.
- **Recovery.** Interruptions, bad paths, insufficient capacity, invalid imports
  and unsupported resource forms fail safely with actionable messages.
- **Release versioning and changelog.**
- **Golden dogfood.** The end-to-end acceptance project in [§15](#15-golden-end-to-end-acceptance-project)
  passes from a clean supported ROM with no manual offset editing.

## 12. Capability completion matrix

This matrix is the stable public-progress ladder. Capability titles and states are
reconciled with [`src/data/capabilities.json`](../src/data/capabilities.json),
which is authoritative; the roadmap note column is this document's.

| Area | Capability | Status | Roadmap / note |
| --- | --- | --- | --- |
| READ | Desktop application shell | Shipped | 5/5 already complete |
| READ | Full-ROM atlas search | Shipped | |
| READ | Recovered-record inspector | Shipped | |
| READ | Sprite, animation and palette browsing | Shipped | |
| READ | Map Browser: every map and layer | Shipped | |
| EDIT | Dialogue line editing | Shipped + strengthened | Variable-length existing compressed dialogue runtime-proven |
| EDIT | Shared palette recolour | Shipped | |
| EDIT | Object placement on the rendered map | Shipped | |
| EDIT | Map layout editing: chunk-cell replacement | Shipped | |
| EDIT | Tile painting | Shipped | Phase 2A, delivered 2026-09-25 at the engine's own unit: one four-byte chunk-cell reference to an existing chunk, not an individual 8x8 tile |
| EDIT | Chunk creation and editing | Shipped | Phase 2B, complete 2026-09-25: the authored body is allocated above the original ROM's end and the retail engine loads it |
| EDIT | Map resizing and layer changes | Shipped | Phase 2C, complete 2026-09-26: the grown layer record is relocated above the original ROM's end and the added ground is displayed at runtime |
| EDIT | Warp and connection editing | Shipped | Phase 2D, complete 2026-09-28: retarget and create transitions, and draw, select and drag their trigger regions on the map; runtime-proven |
| AUTHOR | Authored entities and placements | Shipped | |
| AUTHOR | Authored behavior and scripts | Shipped | |
| AUTHOR | Authored text beyond the retail slot | Shipped | Distinct from the compressed-dialogue capability |
| AUTHOR | Graphics replacement and import | Missing | Phase 3A (NEXT, not started) -> 21/24 |
| AUTHOR | New sprite, animation and frame authoring | Missing | Phase 3B -> 22/24 |
| AUTHOR | New appearance definitions | Missing | Phase 3C -> 23/24 |
| AUTHOR | New map and scene materialisation | Missing | Phase 4 -> 24/24 |
| DELIVER | Deterministic validate and build | Shipped | |
| DELIVER | Safe Save As to a new file | Shipped | |
| DELIVER | Derivative provenance and reopen | Shipped | |
| DELIVER | Launch the build in an emulator | Shipped | |

## 13. Domain addressability strategy

Checkpoint A mapped sixteen addressability domains. Thirteen can encode addresses
above the original 8 MiB boundary. Three of those families now have runtime proof
there, not one: packed dialogue first, and then map chunks/layers (Phase 2B/2C)
and connections/warps (Phase 2D), each proven by the feature that needed it. **The
optimized roadmap does not attempt to prove all thirteen in advance.** Instead,
each feature ticket owns the proof for the domain it needs. This keeps reverse
engineering attached to visible product progress.

| Domain family | When to prove | Policy |
| --- | --- | --- |
| Packed dialogue | Already runtime-proven | Keep as the established reference proof |
| Map chunks/layers | Phase 2B/2C - proven | Chunk creation and resizing both place their records above the original ROM's end, and both are runtime-proven |
| Map connections/warps | Phase 2D - proven | An authored transition record and its expanded pointer array were placed above the original ROM's end and consumed by the retail engine |
| Graphics containers | Phase 3A | Graphics import owns its real engine proof |
| Sprite/frame/animation structures | Phase 3B | The authoring ticket owns pointer/table range proof |
| Appearance table/resources | Phase 3C | Appearance creation owns table expansion/addressability proof |
| MapEntry/table | Phase 4 | New-map creation owns map-table expansion and runtime load proof |
| Other fixed/indexed domains | As encountered | Keep canonical-only or fixed until an authoring feature actually needs widening |

> **Rule.** *Encoding-capable* is not the same as *engine-proven*, and
> *engine-proven* is not the same as *runtime-proven*. The resource budget panel
> should make that distinction visible to users.

**Explicitly not a Phase 1 exit requirement:** opening one giant campaign to prove
every resource domain can use expanded ROM space. Prove each resource family when
the feature that needs it is implemented:

| Feature | Proof it owns |
| --- | --- |
| chunk creation | map/chunk resource relocation and addressability |
| graphics import | graphics/container expanded addressability |
| sprite authoring | sprite/animation/frame table and payload addressability |
| new appearances | appearance table expansion/relocation |
| new maps | `MapEntry`/table expansion and related references |

## 14. Quality, testing, and evidence rules

### 14.1 Definition of done for every capability

1. A semantic user workflow exists; no manual ROM offset is required for the
   supported case.
2. The production authority is single-sourced; research/oracle copies do not
   become competing shipping implementations.
3. Unsupported cases fail closed with a typed, actionable error.
4. If data grows or moves, the production allocator and write transaction own
   placement and publication.
5. Canonical-base identity and provenance survive reopen.
6. Interactive editors preserve undo/dirty state and expose the same safety
   contract as the SDK.
7. Focused tests pin the behavior, and mutations prove critical guards are
   load-bearing.
8. A real ROM-backed/runtime proof exists when the claim depends on engine
   behavior.
9. Independent review has no unresolved `BLOCKING` finding.
10. Broad validation runs in CI; the full or broad suite is not run by hand.
11. The public capability registry changes only when its actual acceptance target
    is met.

### 14.2 Audit-debt policy

**An audit finding blocks a roadmap feature only when repository evidence shows
that the feature exercises the unsafe path.** Do not automatically schedule every
open finding before product work. Remaining audit debt stays real and tracked -
but **audit backlog is not the roadmap.**

Each finding receives one of three dispositions:

- **Feature-blocking.** Must close before the feature, because its failure path is
  directly exercised.
- **Release-blocking.** May wait during feature development, but must close before
  RC/v1.0.
- **Deferred debt.** Documented, bounded, and safe to carry beyond 1.0 if it does
  not compromise shipping paths.

Current examples:

- CQA-05, CQA-06, CQA-07 and CQA-08 were **feature-blocking** for continued
  heavy Workbench expansion, and are now **CLOSED** (2026-09-24 and 2026-09-25).
- CQA-10 remains **PARTIAL / IMPROVED**, but its allocation-relevant portion is
  already closed.
- `ROM-CAPACITY-ATLAS-SEED-OVERLAY-001` remains open, because the allocator does
  not use the structural atlas seed as free-space authority.
- CQA-09 and CQA-12 are **CLOSED** by `ROM-CAPACITY-AND-ALLOCATION-001`.

Remaining high/medium findings should be re-evaluated against the path that
touches them, not blindly sequenced. This rule exists to prevent a recurrence of
the previous "seven findings, therefore seven roadmap tickets" confusion.

## 15. Golden end-to-end acceptance project

Before v1.0, build one deliberately small but complete mod using only DragonByte
Z. This is the final proof that the product is coherent, not merely a collection
of individually-passing features.

Starting from a clean supported Buu's Fury ROM, an author using DragonByte Z
should be able to:

1. Open a clean supported ROM and create a project.
2. Create a new map/area rather than repurposing an existing `MapEntry`.
3. Paint the map, and resize or change its layout.
4. Create the needed chunks and layers.
5. Connect it to another map - a warp/connection from an existing retail map into
   the new area, and a valid exit back out.
6. Import at least one original user-created graphics asset.
7. Create a new sprite/animation/frame resource, and a new appearance that uses
   it.
8. Create and place an NPC or enemy using the existing authored-entity path.
9. Author or attach behavior/script logic.
10. Author variable-length dialogue.
11. Use allocator-backed expanded storage where needed.
12. Build the derivative using only production allocation/write/provenance
    machinery.
13. Launch it from the tool, enter the new area, see the new graphics, interact
    with the authored content, run the script/dialogue, and transition back.
14. Close the application, reopen the project, make another change, and rebuild
    deterministically.
15. Produce a distributable BPS patch from the verified base and the rebuilt
    derivative.
16. Flash/test one release-candidate derivative on real hardware or a
    representative flashcart.

> **Golden rule.** **No hex editor. No manually entered ROM offsets. No one-off
> research script standing in for a shipping feature.**

The acceptance criterion explicitly requires that no manual ROM offsets are used,
no hex editor is used, and no one-off research script substitutes for a product
feature.

## 16. What we deliberately do not put before 1.0

A complete roadmap needs explicit non-goals, so the finish line cannot move
indefinitely. These are valuable ideas, but they should not become hidden
prerequisites for 24/24 or v1.0 unless new evidence changes the decision.

- Runtime-proving all sixteen addressability domains before any feature needs
  them.
- Proving the full nominal 32 MiB GBA ROM window for the engine.
- A general plugin ecosystem comparable to Tiled before core authoring is
  complete.
- Tiled TMX/TSX interchange before DragonByte Z's own map model is fully
  authorable.
- Automapping/terrain rules, prefab/template systems, or large-scale procedural
  content generation.
- Full audio editing, when the community already has a complementary Webfoot
  Audio Engine; integration/interoperability can come later.
- Decompilation-based editing mode, unless a sufficiently complete LoG II/Buu
  decomp becomes a materially better source of truth.
- Closing every LOW/INFO audit finding regardless of shipping relevance.
- Full cross-game support for LoG I / LoG II before Buu's Fury v1.0 is coherent.

**These do not move the finish line**, and they are not requirements for 24/24.

## 17. Post-1.0 roadmap

After 1.0, the roadmap can expand without threatening the definition of "done."
Recommended directions, in **no way required for 24/24 or v1.0**:

- **1.1 Productivity.** Prefabs/templates, batch operations, smarter search,
  map/object copy/paste across projects, resource reuse tools.
- **1.2 Map intelligence.** Terrain/automapping rules inspired by Tiled,
  world/region visualization, connection overview, reusable map templates.
- **1.3 Interchange.** Tiled import/export, or an intermediate open map format,
  once DragonByte Z's own authoring semantics are stable.
- **1.4 Extensibility.** Plugin/scripting API for custom validators, exporters and
  project automation.
- **1.5 More runtime-proven domains.** Targeted expanded-addressability proofs for
  resource families when users need larger projects.
- **1.6 Broader game support.** Extend profile/catalog support toward LoG II and
  possibly LoG I, while preserving per-game evidence boundaries.
- **1.7 Ecosystem integration.** Interoperate with the Webfoot Audio Engine,
  community disassemblers, asset pipelines, and patch/release tooling.
- **1.8 Advanced bulk authoring and optional advanced patch/distribution
  tooling.**
- **1.9 Deeper Ghidra/BSim-assisted reverse engineering.**
- **2.0 / decomp mode.** If a sufficiently complete decompilation/recompilation
  becomes authoritative, consider a Porymap-style source-project backend, while
  retaining the binary-ROM backend for existing users.

## 18. Roadmap files and governance

The project has accumulated several kinds of "what next?" documents. They are
assigned non-overlapping responsibilities, so no single file silently takes over
the roadmap.

| Artifact | Single responsibility | Question it owns |
| --- | --- | --- |
| [`src/data/capabilities.json`](../src/data/capabilities.json) | Stable definition of product completeness and the public progress denominator. Changes only when the product definition itself intentionally changes. | **What does feature-complete mean?** |
| `docs/ROADMAP_TO_1_0.md` | Canonical long-range ordering, phase dependencies, the 24/24 plan, the RC/v1.0 gate, non-goals and the post-1.0 parking lot. | **What order do we build the remaining product in?** |
| [`research/PROJECT_CODE_QUALITY_AUDIT.md`](research/PROJECT_CODE_QUALITY_AUDIT.md) and its remediation records | Risk register. Findings are attached to affected capability/release paths rather than automatically sequenced. | **What technical risks and debt exist?** |
| [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>) and `PROJECT_STATE_*.md` | Historical milestone/state snapshots and durable links to research and closure records. Not planning authority. | **What has been verified?** |

### 18.1 Roadmap change policy

The roadmap is complete enough that there is always a known next phase. It is
**not immutable**:

- Discoveries may change dependencies. New evidence may split or merge
  implementation tickets.
- Any change must say which capability or milestone is affected, and why.
- **An audit finding does not become a roadmap phase merely because it is open.**
  Audit discoveries do not silently reorder the roadmap.
- Infrastructure tickets should state which future capability they unblock.
- Capability percentages change only at merged, independently-validated product
  acceptance points.
- **The capability denominator remains fixed at 24** unless the human explicitly
  changes the product definition.
- **Roadmap changes require an explicit human decision.** This document records
  the approved route; it does not authorize work by itself.
- Large tickets should use checkpoints when the factual research result needs
  human review before policy or implementation is frozen.
- When a ticket closes out of sequence - as variable-length dialogue did -
  `ROADMAP_TO_1_0.md` should be updated so the recorded route matches.

## 19. References and comparative research

The roadmap uses the following mature tools as product-shape references. They are
not treated as direct architectural templates; DragonByte Z remains constrained by
Buu's Fury's retail binary engine and this repository's evidence discipline.

| Ref | Source | URL | Roadmap relevance |
| --- | --- | --- | --- |
| [1] | GB Studio Documentation | https://develop.gbstudio.dev/docs/ | Project editor, scenes, actors, triggers, scripting, assets, build/export |
| [2] | GB Studio Debugger | https://www.gbstudio.dev/docs/debugger/ | Runtime state, breakpoints, VRAM and palette visibility |
| [3] | GB Studio - Building Your Game | https://www.gbstudio.dev/docs/build/ | Play, Run From Here, ROM/web build workflows |
| [4] | Porymap Introduction | https://huderlem.github.io/porymap/manual/introduction.html | Tiles, collision, events, connections, properties, tileset and region-map editing; painting undo/redo |
| [5] | Porymap - Editing Map Events | https://huderlem.github.io/porymap/manual/editing-map-events.html | NPCs, signposts, warps, scripts, adding/deleting events |
| [6] | Tiled Introduction | https://doc.mapeditor.org/en/stable/manual/introduction/ | Tile/object layers, brushes, terrains, projects, plugins, scripting |
| [7] | Tiled Automapping | https://doc.mapeditor.org/en/latest/manual/automapping/ | Rule-driven repetitive tile/object placement and correction |
| [8] | Tiled Export Formats | https://doc.mapeditor.org/en/latest/manual/export/ | Generic/custom export workflows and CLI automation |
| [9] | CoilSnake | https://github.com/pk-hack/CoilSnake | Deconstructs EarthBound assets and rebuilds modified ROMs; broad content-authoring model |
| [10] | Floating IPS (Flips) | https://github.com/bates64/flips | IPS/BPS patch creation/application, GUI/CLI distribution workflow |

### Project-specific evidence used in this roadmap

- `DIALOGUE-VARIABLE-LENGTH-001` final closeout at project head
  `a commit since folded into its successor`.
- `ROM-CAPACITY-AND-ALLOCATION-001` Checkpoints A-D and closeout records
  ([evidence](research/ROM_CAPACITY_AND_ALLOCATION.md)).
- `PROJECT-CODE-QUALITY-AUDIT-001` and the closed remediation records CQA-01,
  CQA-02, CQA-03/CQA-15 and CQA-04
  ([audit](research/PROJECT_CODE_QUALITY_AUDIT.md)).
- Current capability registry: 24 total, 20 shipped (READ 5/5, EDIT 8/8,
  AUTHOR 3/7, DELIVER 4/4); Phase 2 map editing is complete and the next
  capability is graphics import (Phase 3A, not started).
- Known open/deferred items: CQA-10 (partial) and
  `ROM-CAPACITY-ATLAS-SEED-OVERLAY-001`. CQA-05, CQA-06, CQA-07 and CQA-08 are
  **CLOSED** (2026-09-24 and 2026-09-25).

## Final planning snapshot

| | |
| --- | --- |
| **Now** | 20/24 (83%); Phase 2 map editing is complete, all four map capabilities runtime-proven |
| **Next** | Phase 3A graphics import (`GRAPHICS-IMPORT-001`; NEXT, not started) |
| **Then** | Graphics import, then new sprites/animations, then appearances -> 23/24 |
| **Feature-complete finish** | New-map authoring -> 24/24 (100%) |
| **Ship finish** | Creator UX/RC -> golden dogfood -> BPS distribution -> hardware smoke -> v1.0 |

> The roadmap is complete when there is always a known next move, but the
> definition of done never moves.
