# Editing map transitions

The shipped map-transition editing capability: the transition record, the project
representation, the Workbench surface, the end-to-end proof and the focused
regressions behind it.

## Outcome

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

## Context

- *This is the delta as the record was opened.* What the sub-passes actually shipped
  is mapped item by item under Required Work below.
- The transition contract is already read, not guessed: all **735** transition
  records behind the 452 map roots parse with no anomalies, the record is a 24-byte
  block reached from a root's `+0x40`/`+0x44` count/array pair, and the destination
  is a two-byte map key at `+0x11`/`+0x12` resolved against the MapEntry key table.
  **At the record's opening, reading a transition was not editing one**: no surface
  wrote a transition record, and the fields past the destination key were recorded
  with meanings still `UNRESOLVED`. Both gaps are closed above, and the
  `UNRESOLVED` fields remain unresolved by design.
- Phase 2C established two facts this record will need and must reuse: a map root's
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

## Required work, closed out item by item

Every numbered item is mapped below to its committed evidence, its sub-pass record
and, where useful, its merge SHA. Every sub-pass record is retained: nine full
evidence records and every closure; `MAP-WARP-FACING-TRACE-001` and
`MAP-WARP-STACK-REVIEW-AND-INTEGRATE-001` exist only as condensed integration notes.
Nothing was deleted or squashed.

### RW1 - measure the record, refuse unsupported forms before planning

Closed by **`MAP-WARP-FORMAT-001`**
([`MAP-WARP-FORMAT-001.md`](MAP-WARP-FORMAT-001.md); closure
[`archive/MAP-WARP-FORMAT-001.md`](archive/MAP-WARP-FORMAT-001.md); merge
`933e0fc39e79a99c0aeb849fa02b63e4d6a906b4`). The family is the 24-byte record a map's selector-1 root reaches through
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
  merge `e21bf5e0d581ca89a28767310cbbca0872b8ee4f`) - a supported transition is editable **by semantic identity**
  through a project. `maps/transitions.toml` stores `TransitionIdentity(source map,
  array index)` with each editable field as a prior/authored pair; the build loads
  the canonical record by that identity, verifies the stored prior, applies the edit
  through the existing authority, serializes only that 24-byte record in place, and
  records provenance. The edit is fixed-width: **no allocation, no relocation, no
  second serializer**. Independent review `PASS`, zero blocking.
- **`MAP-WARP-CREATE-PROJECT-001`** ([record](MAP-WARP-CREATE-PROJECT-001.md);
  closure
  [`archive/MAP-WARP-CREATE-PROJECT-001.md`](archive/MAP-WARP-CREATE-PROJECT-001.md);
  merge `ac1be70250ba2a7c544918a8b9231551f59fe6a4`) - **creation**. The durable identity is
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
  `e9b5da362fa6566b266f7b14316b6cf6076d18c6`; independent review `APPROVE`, zero blocking) and
  `MAP-WARP-CREATE-WORKBENCH-001`
  ([record](MAP-WARP-CREATE-WORKBENCH-001.md); closure
  [`archive/MAP-WARP-CREATE-WORKBENCH-001.md`](archive/MAP-WARP-CREATE-WORKBENCH-001.md);
  merge `e77e9eede0ac3b8368e2151db95c92475a1b506d`). `Maps -> Warps` lists a map's existing connections and
  retargets destination, arrival and facing as one semantic project edit through the
  authority, with Apply/Revert, real Undo/Redo, the 169-class family refused outright
  and the raw `+0x10` never exposed; its **Create Transition** action authors a
  transition the image does not contain and stages it as `New (staged)`. Save and
  reopen reproduce the authored state from disk.
- **The map surface itself** - `MAP-WARP-CANVAS-001`
  ([record](MAP-WARP-CANVAS-001.md); closure
  [`archive/MAP-WARP-CANVAS-001.md`](archive/MAP-WARP-CANVAS-001.md); merged as
  `f4368d99d9ff8fe5fdc4deca128575d10544214f`). Every supported transition of the
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
  merge `6b805bd679b12a1a9ccf9264ac96cd5b55036230`) - the **existing-edit** proof. `map:0040/transition:0000` was
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
  merge `3431fba0039da6bd30fdc01a3f9acb08093b553d`) - the **creation** proof. The retail control on the canonical
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
  Undo deleted a pre-existing authored region. The correction is merged in `f4368d99d9ff8fe5fdc4deca128575d10544214f`.

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
