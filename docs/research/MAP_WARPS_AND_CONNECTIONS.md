# MAP-WARPS-AND-CONNECTIONS-001 - editing map transitions

STATUS: **SHIPPED (2026-09-28).** Phase 2D is complete, and Phase 2 (Map Editing) is
complete with it. The **`warps`** capability is `shipped`: DragonByte Z moves from
**19 / 24 (79%)** to **20 / 24 - 83%**, and **EDIT** from **7 / 8** to **8 / 8**. The
next capability is **graphics import** (Phase 3), **NOT STARTED**.

The ticket below is completed, not rewritten: its Objective, Context delta, Required
Work, Scope Boundaries, Ticket-Specific Validation, Required Review and Completion
Criteria are the ticket as it was set, and the sections added by this closeout state
what actually shipped and map every numbered requirement to its committed evidence.

A closeout was attempted once before and was **STOPPED** rather than closed over a
gap. The Warps list, form and Create surface existed, but the ticket's Required Work
3 also asks for transitions **drawn and edited on the existing map surface**, and
that half did not exist. That missing half is why **`MAP-WARP-CANVAS-001`** was
opened; it merged as `89a37ed6176db77d7d77b2f4dc660800258911f8`, and this closeout
follows it.

**This file is not the roadmap.** The approved route to 24/24 and v1.0 lives in
[`../ROADMAP_TO_1_0.md`](../ROADMAP_TO_1_0.md); read its Phase 2 section and its
section 13 for this work rather than restating them here. The fixed capability
denominator and the open technical risks live in
[`../../src/data/capabilities.json`](../../src/data/capabilities.json) and
[`../research/PROJECT_CODE_QUALITY_AUDIT.md`](../research/PROJECT_CODE_QUALITY_AUDIT.md).

**Phase 2A (tile painting), 2B (chunk creation), 2C (map resizing and layer
authoring) and 2D (map transitions) are COMPLETE and integrated.** Predecessor
closures:
[`archive/MAP-TILE-PAINT-001-COMPLETE.md`](archive/MAP-TILE-PAINT-001-COMPLETE.md),
[`archive/MAP-CHUNK-AUTHORING-001-COMPLETE.md`](archive/MAP-CHUNK-AUTHORING-001-COMPLETE.md)
and
[`archive/MAP-RESIZE-AND-LAYERS-001-COMPLETE.md`](archive/MAP-RESIZE-AND-LAYERS-001-COMPLETE.md),
whose evidence records are [`MAP-TILE-PAINT-001.md`](MAP-TILE-PAINT-001.md),
[`MAP-CHUNK-AUTHORING-001.md`](MAP-CHUNK-AUTHORING-001.md) and
[`MAP-RESIZE-AND-LAYERS-001.md`](MAP-RESIZE-AND-LAYERS-001.md). **CQA-05** through
**CQA-09**, **CQA-12** and **CQA-15** are CLOSED and must not be reopened.
**CQA-10 remains PARTIAL / IMPROVED** and is not part of this ticket.

## Outcome (2026-09-28)

- **Capability:** `warps` is `shipped`; DragonByte Z is **20 / 24 - 83%**; `EDIT` is
  **8 / 8**. Phase 2 (Map Editing) is complete.
- **Shipped:** an author can edit an existing supported map transition - destination,
  arrival and facing - and create one the image does not contain, through the
  Workbench, persist it semantically in the project, rebuild it deterministically,
  and have the retail engine consume it; on the map canvas every supported
  transition is drawn as its trigger region and can be selected and dragged as one
  undoable gesture.
- **Next capability:** graphics import (Phase 3), **NOT STARTED**. No later
  capability was begun in this pass.
- **Scope of the claim:** the shipped capability is the supported, proven authoring
  surface measured by the sub-passes below. It is **not** a claim of universal
  engine-transition support. Forms the corpus does not carry, or whose semantics the
  toolkit has not measured, are refused rather than guessed, and the limitations
  that remain are listed at the end of this record.

## Objective

Deliver Phase 2D: an author can create and edit a map's transitions - where one
area connects to another - and have the retail engine consume the edit. When it
ships, the product moves from **19 / 24** to **20 / 24**, and the `warps`
capability in the registry is the only authority for that count.

**This objective is met.** The product moved to **20 / 24 - 83%** when `warps` was
marked `shipped`, and the registry holds that count.

## Context delta

- *This is the delta as the ticket was opened.* What the sub-passes actually shipped
  is mapped item by item under Required Work below.
- The transition contract is already read, not guessed: all **735** transition
  records behind the 452 map roots parse with no anomalies, the record is a 24-byte
  block reached from a root's `+0x40`/`+0x44` count/array pair, and the destination
  is a two-byte map key at `+0x11`/`+0x12` resolved against the MapEntry key table.
  **At the ticket's opening, reading a transition was not editing one**: no surface
  wrote a transition record, and the fields past the destination key were recorded
  with meanings still `UNRESOLVED`. Both gaps are closed above, and the
  `UNRESOLVED` fields remain unresolved by design.
- Phase 2C established two facts this ticket will need and must reuse: a map root's
  pointer fields are full 32-bit GBA addresses the retail engine follows above the
  canonical EOF, and a map whose root is **shared** with another map cannot be
  edited in place - 11 canonical roots serve more than one map.
- The runtime methodology is human-operated and mandatory - no scripted player
  input, which is a permanent rule after Phase 2C's recorded process violation.
  The savestate leave-and-re-enter requirement is scoped to **map and background
  assembly**, where a savestate restores an already-built area;
  `MAP-WARP-RUNTIME-EDIT-001` corrected the earlier over-general reading, because
  a transition is read when its trigger fires - see
  [`../runtime-capture.md`](../runtime-capture.md).
- Reuse the existing map view and model, the existing undo system, the identity and
  provenance rules, the production allocator and the one write plan. Do not add a
  second rendering, editing or allocation path.

## Required Work

1. Establish by measurement what a transition record actually is: which fields the
   engine reads, which of them are safe to author, and what the engine's own limits
   are - so an unsupported transition form is refused before it is planned.
2. Implement transition authoring through the production write path, persisting
   semantically and allocating only through declared free space plus generated
   expansion.
3. Make the result observable and revisable in the Workbench: transitions drawn and
   edited on the existing map surface, one undoable gesture, reopen reproducing the
   authored transition.
4. Prove it end to end: the project reopens, a built image contains the authored
   transition, the canonical input is still refused as a write target, and the
   retail engine consumes the transition after a genuine rebuild.
5. Add focused regressions with named failing nodes and one mutation that restores
   the old behaviour, keeping the change bounded to this capability.

## Required Work, closed out item by item

Every numbered item is mapped below to its committed evidence, its sub-pass record
and, where useful, its merge SHA. Every sub-pass record is retained: nine full
evidence records under `docs/research/`, and every closure under
`docs/research/archive/` - `MAP-WARP-FACING-TRACE-001` and
`MAP-WARP-STACK-REVIEW-AND-INTEGRATE-001` exist in the archive only, which is where
their closures were written. Nothing was deleted or squashed.

### RW1 - measure the record, refuse unsupported forms before planning

Closed by **`MAP-WARP-FORMAT-001`**
([`MAP-WARP-FORMAT-001.md`](MAP-WARP-FORMAT-001.md); closure
[`archive/MAP-WARP-FORMAT-001.md`](archive/MAP-WARP-FORMAT-001.md); merge
`05870f1`). The family is the 24-byte record a map's selector-1 root reaches through
the root's `+0x40` count and `+0x44` pointer array; the destination is the two
independent bytes at `+0x11` (high) / `+0x12` (low) resolved through the MapEntry
two-byte key scan; the region is four `u16` at `+0x08`/`+0x0A`/`+0x0C`/`+0x0E`
forming two ordered intervals, exposed positionally because the axis and unit were
`UNRESOLVED`; the identity is `(source map, array index)`, with no ROM offset. The
measurement enumerates **735 canonical records over 452 map roots**, round-trips
735/735 byte-exactly, and **refuses unsupported forms before any plan exists** -
an unmeasured class word, an unordered or degenerate region, an unresolvable
destination key, two maps sharing one lookup key, a null/unaligned/out-of-image
selector-1 source, root, array element or record, a count and array pointer not null
together, a record reached by two maps, and two overlapping record extents - through
the codec's own `validate()`. Independent review `APPROVE` with no findings.

Creation extends RW1's half: **`MAP-WARP-CREATE-PROJECT-001`** composes a created
record only over a same-map 566-class template and runs the shared-root guard first,
so a transition the engine could not address is refused with the real reason rather
than planned.

### RW2 - author through the production write path, persist semantically, allocate only through declared free space plus generated expansion

Closed by two sub-passes, one for each editable shape:

- **`MAP-WARP-PROJECT-AUTHORING-001`** ([record](MAP-WARP-PROJECT-AUTHORING-001.md);
  closure
  [`archive/MAP-WARP-PROJECT-AUTHORING-001.md`](archive/MAP-WARP-PROJECT-AUTHORING-001.md);
  merge `d4baa14`) - a supported transition is editable **by semantic identity**
  through a project. `maps/transitions.toml` stores `TransitionIdentity(source map,
  array index)` with each editable field as a prior/authored pair; the build loads
  the canonical record by that identity, verifies the stored prior, applies the edit
  through the existing authority, serializes only that 24-byte record in place, and
  records provenance. The edit is fixed-width: **no allocation, no relocation, no
  second serializer**. Independent review `PASS`, zero blocking.
- **`MAP-WARP-CREATE-PROJECT-001`** ([record](MAP-WARP-CREATE-PROJECT-001.md);
  closure
  [`archive/MAP-WARP-CREATE-PROJECT-001.md`](archive/MAP-WARP-CREATE-PROJECT-001.md);
  merge `b39e5fe`) - **creation**. The durable identity is
  `map:NNNN/transition:<name>` - a source map key plus an authored name, with no
  address and no array index, because the index a created record will occupy does
  not exist until a build appends it. The record is composed over a named canonical
  566-class template of the same source map (authored: region, destination key,
  arrival pair and `+0x10`'s high nibble; carried from the template: the class word,
  the invariant word, `+0x13` and `+0x10`'s low nibble, published field by field in
  the manifest), stored in a sixth document `maps/transition_creations.toml`, and
  built by the first transition domain that **allocates**: the new 24-byte record and
  the expanded `root + 0x44` array are both `EXPANDED_ONLY` above canonical EOF, with
  map 40's `root + 0x40` rewritten from 2 to 3. Deterministic allocation, existing
  transitions preserved with their records, addresses and order, and the canonical
  array left untouched at its own address. Independent review `APPROVE` with one
  trivial non-blocking finding, resolved and re-confirmed.

Allocation authorization is the existing one: the two new spans are allocator-issued
against the build-scoped reservation set threaded from every earlier domain, and
`plan_changes` refuses any overlap. It is `BUILD-PROVEN / ENCODING-PROVEN` at this
point - every canonical `+0x44` and array element is a full 32-bit GBA address
(452/452 roots, 735/735 elements, full census) - and explicitly not runtime-proven
until RW4.

### RW3 - observable and revisable in the Workbench, transitions drawn and edited on the existing map surface, one undoable gesture, reopen reproducing the authored transition

This requirement is satisfied in full by **two** records of evidence, and both halves
are needed to close it:

- **The Warps list, form and Create surface** - `MAP-WARP-WORKBENCH-001`
  ([record](MAP-WARP-WORKBENCH-001.md); closure
  [`archive/MAP-WARP-WORKBENCH-001.md`](archive/MAP-WARP-WORKBENCH-001.md); merge
  `7efbb9c`; independent review `APPROVE`, zero blocking) and
  `MAP-WARP-CREATE-WORKBENCH-001`
  ([record](MAP-WARP-CREATE-WORKBENCH-001.md); closure
  [`archive/MAP-WARP-CREATE-WORKBENCH-001.md`](archive/MAP-WARP-CREATE-WORKBENCH-001.md);
  merge `5224c73`). `Maps -> Warps` lists a map's existing connections and
  retargets destination, arrival and facing as one semantic project edit through the
  authority, with Apply/Revert, real Undo/Redo, the 169-class family refused outright
  and the raw `+0x10` never exposed; its **Create Transition** action authors a
  transition the image does not contain and stages it as `New (staged)`. Save and
  reopen reproduce the authored state from disk.
- **The map surface itself** - `MAP-WARP-CANVAS-001`
  ([record](MAP-WARP-CANVAS-001.md); closure
  [`archive/MAP-WARP-CANVAS-001.md`](archive/MAP-WARP-CANVAS-001.md); merged as
  `89a37ed6176db77d7d77b2f4dc660800258911f8`). Every supported transition of the
  displayed map is drawn as its trigger region on the rendered Objects canvas, a
  click selects that connection in the Warps editor, and a drag translates the region
  as **one undoable gesture** through `map_transitions.set_transition_edits` - the
  same entry point the Warps Apply uses. The canvas states no rule of its own: it
  installs the Warps surface's `region_edit_refusal` as the guard, so a 169-class
  record, an unresolved destination, a shared selector-1 root, an unreadable project
  and a project-created transition are all refused in the surface's own words, with
  the refused regions still drawn dashed and still draggable so the refusal is
  readable. The coordinate mapping was measured, not assumed: `first` is the
  horizontal interval in engine map pixels, confirmed independently because
  `map:0039/transition:0001`'s region lands exactly on map 39's east doorway band
  that `MAP-RESIZE-AND-LAYERS-001` had measured at runtime.

**Why the canvas record exists, stated plainly.** The earlier closeout attempt was
**STOPPED** because this second half did not exist. That history is the reason
`MAP-WARP-CANVAS-001` was opened, and it is recorded here rather than smoothed over:
without it, Required Work 3 would have been marked closed on the Warps surface alone.

### RW4 - prove it end to end: reopen, a built image contains the authored transition, the canonical input is still refused as a write target, and the retail engine consumes it after a genuine rebuild

Closed by two human-operated runtime proofs, both driven through the shipped
surfaces and the normal build path:

- **`MAP-WARP-WORKBENCH-RUNTIME-001`** ([record](MAP-WARP-WORKBENCH-RUNTIME-001.md);
  closure
  [`archive/MAP-WARP-WORKBENCH-RUNTIME-001.md`](archive/MAP-WARP-WORKBENCH-RUNTIME-001.md);
  merge `df81e7a`) - the **existing-edit** proof. `map:0040/transition:0000` was
  retargeted from map 39 to **map 435** with arrival `(16, 360)` and facing **East**,
  authored one gesture at a time through the shipped `Maps -> Warps` surface, saved,
  reopened, and built by the normal production path into a derivative that is
  byte-identical to the image `MAP-WARP-FACING-TRACE-001` had already measured. A
  human-operated mGBA run on that derivative sent map 40 to **map 435**, and the
  passive observer read the live record `+0x10 = 0x42` and the warp's new player
  object first facing **`03` = East**, with selector `0x03001A34` reading `0`
  throughout (and therefore not suppressing the write). The player was usable
  immediately.
- **`MAP-WARP-CREATE-RUNTIME-001`** ([record](MAP-WARP-CREATE-RUNTIME-001.md);
  closure
  [`archive/MAP-WARP-CREATE-RUNTIME-001.md`](archive/MAP-WARP-CREATE-RUNTIME-001.md);
  merge `fc5d1b8`) - the **creation** proof. The retail control on the canonical
  image showed root count **2**, the created element **absent**, and the authored
  destination never reached. On the derivative, the created transition **fired**:
  the live array was `0x08800000` and the live new record `0x0880000C`, both above
  the original 8 MiB EOF, and map 40 went to **map 435 at frame 1191**, with the
  player usable afterwards and **no automated input**.

Across both: the project reopened reproducing the authored transition, the built
image contained it, the canonical input was still refused as a write target, the
retail engine consumed it after a genuine rebuild, and the canonical ROM was
UNCHANGED (`940ad5f0...f059e`) before and after every run.

### RW5 - focused regressions with named failing nodes and a mutation restoring the old behaviour

Every code-bearing sub-pass carries its own named regressions and mutations, recorded
in full in its evidence record:

- `MAP-WARP-FORMAT-001`: mutations **M1-M4**, each breaking a named regression in
  `tests/unit/test_map_transitions.py` (54 tests) and
  `tests/integration/test_map_transitions_rom.py` (15 ROM-gated tests).
- `MAP-WARP-PROJECT-AUTHORING-001`: mutations **M1-M4**, observed failing 3, 4, 3 and
  4 named tests respectively.
- `MAP-WARP-WORKBENCH-001`: mutations **M1-M4**, each failing a named regression in
  `tests/unit/test_workbench_warp_transitions.py`
  (`test_selecting_a_row_loads_its_editable_state`,
  `test_the_facing_control_offers_five_choices_and_no_raw_byte`,
  `test_a_169_class_connection_is_read_only_with_a_reason`,
  `test_a_project_mutation_keeps_the_staged_connection_edit`).
- `MAP-WARP-CREATE-PROJECT-001`: mutations **M1-M6**, each killed by the focused unit
  file and a named ROM-gated regression, with the source restored byte-identically.
- `MAP-WARP-CREATE-WORKBENCH-001`: mutations **M9-M11** at the final candidate,
  including the pre-fix ownership rule, with `warp_tab.py` restored byte-for-byte.
- `MAP-WARP-CANVAS-001`: the **new focused file**
  `tests/unit/test_workbench_map_warp_canvas.py` (20 tests at the reviewed freeze, 22
  after the correction) and the **phantom-undo regression**
  `test_a_drag_that_writes_nothing_adds_no_history_and_keeps_the_authored_region`.
  The regression pins the review's NB1: the region write had reported success when
  the authority wrote nothing, so a drag over a canvas stale by exactly the drag
  delta pushed an undo entry over an edit that was never written, and that entry's
  Undo deleted a pre-existing authored region. The correction is merged in `89a37ed`.

## Sub-pass chain

| Sub-pass | What it closed | Merge |
| --- | --- | --- |
| `MAP-WARP-FORMAT-001` | the measured format, one SDK authority and the fail-closed refusals (RW1; the format half of RW2 and RW5) | `05870f1` |
| `MAP-WARP-PROJECT-AUTHORING-001` | a semantic prior/authored transition edit persisted in the project and applied by the production build (RW2) | `d4baa14` |
| `MAP-WARP-RUNTIME-EDIT-001`, `MAP-WARP-FACING-TRACE-001` | the earlier runtime work that resolved the arrival pair and the facing rule and corrected two over-general runtime rules (context for RW4) | folded into the stacked candidate merged at `d4baa14` |
| `MAP-WARP-STACK-REVIEW-AND-INTEGRATE-001` | the preceding sub-passes frozen, reviewed, CI-run and merged as one candidate | `d4baa14` |
| `MAP-WARP-WORKBENCH-001` | the Warps list and form (RW3, first half) | `7efbb9c` |
| `MAP-WARP-WORKBENCH-RUNTIME-001` | the human-operated end-to-end proof of an existing-transition edit (RW4) | `df81e7a` |
| `MAP-WARP-CREATE-PROJECT-001` | creation through the project and the build (RW1, RW2) | `b39e5fe` |
| `MAP-WARP-CREATE-WORKBENCH-001` | the Create Transition surface (RW3) | `5224c73` |
| `MAP-WARP-CREATE-RUNTIME-001` | the retail engine consuming a created transition (RW4) | `fc5d1b8` |
| `MAP-WARP-CANVAS-001` | transitions drawn and edited on the map surface (RW3, second half), and the missing half that stopped the earlier closeout | `89a37ed` |

## Scope Boundaries

- Do not change the canonical ROM, and do not commit ROM-derived fixtures or
  runtime captures. Do not lower a real assertion to make a gate green.
- Do not implement new maps, graphics import, collision editing, sprite or
  appearance authoring - those are Phase 3 and later.
- Do not re-open Phase 2A, 2B or 2C's accepted limits, and do not weaken the
  fail-closed refusal list.
- Do not weaken `tools/webfoot/profile.py`, the identity checks, output and source
  separation, allocation authorization or provenance.
- Do not touch CQA-10, and do not reopen CQA-01 through CQA-09, CQA-12 or CQA-15.

## Ticket-Specific Validation

- The transition operation, demonstrated on a real map with a real rebuild.
- A named regression that fails on the pre-edit shape, with the failing node
  recorded, plus the mutation that restores the old shape.
- The reopen, build and identity-refusal proof named in Required Work.
- Focused named-file tests only, `git diff --check`, and the gates for the changed
  surface. Broad validation belongs to CI.

**Met.** Both the existing-edit and the creation operations were demonstrated on a
real map with a real rebuild; the named regressions and their mutations are listed
under Required Work 5; and the reopen, build and identity-refusal proofs are the RW4
runtime records.

## Required Review

Independent code-review gate per [`../../docs/DEVELOPMENT.md`](../../docs/DEVELOPMENT.md) using
[`REVIEW.md`](REVIEW.md), with a fresh-context reviewer given the
ticket, the START SHA, the frozen SHA and the frozen worktree. A review is launched
only when its verdict can be read.

**The gate was met sub-pass by sub-pass**, because this capability was built as a
chain of scoped passes rather than one code change: `MAP-WARP-FORMAT-001`
`APPROVE` (no findings), `MAP-WARP-PROJECT-AUTHORING-001` `PASS` (zero blocking),
`MAP-WARP-STACK-REVIEW-AND-INTEGRATE-001` `APPROVE WITH NON-BLOCKING NOTES` (its five
notes recorded as follow-ups), `MAP-WARP-WORKBENCH-001` `APPROVE` (zero blocking),
`MAP-WARP-CREATE-PROJECT-001` `APPROVE` (one trivial non-blocking finding resolved
and re-confirmed), `MAP-WARP-CREATE-WORKBENCH-001` seven review rounds (five blocking
findings in the ownership family, all fixed and pinned) and `MAP-WARP-CANVAS-001`
`PASS` (zero blocking, eight non-blocking, four applied in the correction). The two
runtime-proof sub-passes changed no product code, so no diff gate applied and their
own records are the evidence. The reviews record that a cloud verdict was not
available on this account and that the readable local channel was used instead; the
no-amend rule was observed throughout.

## Completion Criteria

- A supported map's transitions can be authored, materialized, reopened and
  consumed by the retail engine, and the addressability the feature needs is proven
  rather than assumed.
- Because every write must use the flow
  `verified base -> working copy/generated output -> patch/output ROM`, the
  canonical input is still refused as a write target and the canonical ROM is
  unchanged.
- Reopen reproduces the authored transition byte-exactly, and the build is
  deterministic.
- Focused tests pass, the independent review returns a verdict with no unresolved
  blocking finding, and the `warps` capability is marked shipped only after the
  work is done and reviewed.

**All four are met.** Addressability is proven by measurement and by the retail
engine following an above-EOF array and record; the canonical input stayed refused
and unchanged; reopen reproduced the authored transition and the build was
deterministic (the derivative's SHA-256 was reproduced by an independent second
run); and the focused tests and the independent reviews completed with no unresolved
blocking finding before `warps` was marked shipped.

## Limitations that do not block the shipped capability

- **Class-169 creation and edit semantics stay intentionally unsupported** where the
  production authority fails closed: a 169-class record's stored arrival is a
  scene-relative delta, so the Warps surface refuses destination, arrival and facing
  on it, and the canvas draws it dashed and refuses its region drag. The refusal is
  the authority's own wording, not a second rule stated in Qt.
- **Non-zero `0x03001A34` arrival-facing behaviour is UNTESTED.** Every proving run
  read the selector as `0`. The facing rule is proven for the measured configuration
  and is not to be called universally reliable.
- **The low nibble of `+0x10` and `+0x13` remain UNRESOLVED** though preserved
  byte-for-byte; nothing is authored there and no meaning is invented.
- **The exact runtime arrival pixel was not instrumented** in the existing-edit
  proof: the observer has no player-coordinate channel, the authored `(16, 360)` is
  verified in the built and live record, and the human observation confirms a
  correct, movable entry; the exact on-screen pixel is not machine-measured.
- **A shadowed stale staged creation has no per-row discard action.** It is safe - it
  writes nothing, loses nothing and always refuses Apply with the reason stated - and
  its exit is the session boundary, where a project or image reload clears staged
  work.
- **A transition the project creates is drawn read-only on the canvas and its region
  drag refuses**, with the reason named. Editing it would mean a second write path in
  the canvas, which this capability did not take.
- **A map with no supported 566-class record of its own cannot gain a created
  transition.** That is creation's deliberate fail-closed narrowing; widening it
  needs evidence for `+0x13` and the door gate bits, not borrowed bytes.
- **The class words, the invariant word at `+0x04`, `+0x14`/`+0x16`/`+0x17` and the
  destination position's source remain `UNRESOLVED`**, as recorded by
  `MAP-WARP-FORMAT-001`.

**The shipped capability is the supported, proven authoring surface, not a claim of
universal engine-transition support.** An unsupported transition form is refused
before it is planned, and every refusal fails closed rather than guessing.

## Stop

Stop when transition authoring is implemented, proved and reviewed. **That condition
was reached on 2026-09-28.**

Do not begin MAP-NEW-MAPS-001 or any later capability in this pass. Do not
implement new maps, graphics import, or sprite or appearance authoring, and do not
reorder the roadmap's phases. **The next capability is graphics import (Phase 3),
NOT STARTED**, and no part of it was begun here.

No capability count may be advanced before the work is done and reviewed: the
capability registry is the authority, and reaching 20 / 24 happens only when the
capability actually ships.

WORKBENCH-006 remains untouched and needs owner direction before it resumes. It is
not part of this ticket.

## Completed

- **MAP-WARPS-AND-CONNECTIONS-001** - **SHIPPED (2026-09-28)**; Phase 2D map
  transitions shipped, Phase 2 (Map Editing) complete, DragonByte Z **20 / 24
  (83%)**, `EDIT` **8 / 8**. The sub-pass records stay under `docs/research/` and
  their closures under `docs/research/archive/`.
- **MAP-RESIZE-AND-LAYERS-001** - CLOSED and reviewed (2026-09-26); Phase 2C map
  growth and supported layer authoring shipped, DragonByte Z **19 / 24 (79%)**;
  closeout
  [`archive/MAP-RESIZE-AND-LAYERS-001-COMPLETE.md`](archive/MAP-RESIZE-AND-LAYERS-001-COMPLETE.md).
- **MAP-CHUNK-AUTHORING-001** - CLOSED and integrated (2026-09-25); Phase 2B chunk
  creation shipped, DragonByte Z **18 / 24 (75%)**; closeout
  [`archive/MAP-CHUNK-AUTHORING-001-COMPLETE.md`](archive/MAP-CHUNK-AUTHORING-001-COMPLETE.md).
- **MAP-TILE-PAINT-001** - CLOSED and integrated (2026-09-25); Phase 2A tile
  painting shipped, DragonByte Z **17 / 24 (71%)**; closeout
  [`archive/MAP-TILE-PAINT-001-COMPLETE.md`](archive/MAP-TILE-PAINT-001-COMPLETE.md).
- **CQA-07-08-WORKBENCH-PERF-AND-CI-001** - CLOSED and integrated (2026-09-25);
  closeout [`archive/CQA-07-08-WORKBENCH-PERF-AND-CI-001-COMPLETE.md`](archive/CQA-07-08-WORKBENCH-PERF-AND-CI-001-COMPLETE.md).
- **CQA-05-06-WORKBENCH-STATE-AND-ERRORS-001** - CLOSED and integrated.
- **CQA-04-DECODE-STACK-AUTHORITY-001** - CLOSED and integrated.
- **CQA-03-15-IDENTITY-AND-EXTENTS-001**,
  **CQA-02-PACKED-STREAM-TERMINATION-001** and
  **CQA-01-OUTPUT-SAFETY-001** - CLOSED and integrated (2026-09-23).
