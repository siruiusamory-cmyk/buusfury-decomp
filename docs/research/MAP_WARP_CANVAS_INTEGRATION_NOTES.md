# Connections on the Maps canvas: integration notes

The condensed record of the map-connection canvas pass: what shipped, the
coordinate mapping, the correction it produced and the limits kept.

## Why this work exists

The parent's map-surface half of Required Work 3 did not exist when the closeout was
first attempted, and that attempt was **STOPPED** rather than closed over the gap: the
Warps list, form and Create surface shipped in
`MAP-WARP-WORKBENCH-001` / `MAP-WARP-CREATE-WORKBENCH-001`, but Required Work 3 also
asks for transitions **drawn and edited on the existing map surface**. That missing
half is the reason this sub-pass was opened, and the parent's own record states the
stop plainly.

## What shipped

The Maps editor's **Objects** canvas already drew the rendered map and its placement
markers. It now also draws every connection of the displayed map as its **trigger
region**, and that overlay is directly editable.

* **The overlay.** One item per connection, drawn as the record's own two ordered
  intervals at the region's own coordinates, so the view's single zoom/scroll
  transform carries it exactly as it carries the artwork. The **authored** value wins
  where the project has one; created transitions are drawn at the region the project
  authors for them.
* **Click to select.** A press that ends where it started marks that connection and
  switches the Maps editor to **Warps** with that row selected, found by the SDK's own
  identity and never by matching display text. The Warps editor owns the selection;
  returning to Objects re-reads it.
* **One direct canvas edit.** A drag translates the whole rectangle (both endpoints
  of each interval by one delta), so a region cannot become unordered or degenerate,
  and writes through `map_transitions.set_transition_edits` - the same entry point the
  Warps editor's Apply uses - as **one undoable entry** resolved before it is pushed.
  A drag that ends where it started writes nothing and enters no history, and
  save/reopen reproduces the authored region.
* **Fail closed.** The canvas states no rule of its own: the Maps editor installs the
  Warps surface's `region_edit_refusal` as the drag guard, and a canvas with no guard
  installed edits nothing. The 169-class record, an unresolved destination, a shared
  selector-1 root, an unreadable or missing project document and a project-created
  transition are all refused, in the surface's own words, with the refusals still
  drawn (dashed) and still draggable so the refusal can be read. An out-of-`u16`
  endpoint is refused by `TransitionRegion` itself.
* **One gap closed elsewhere:** the Warps list's `Trigger region` column now prefers
  the project's authored region over the record's, so the list and the canvas cannot
  state two different regions for one connection.

## The coordinate mapping

Measured, and stated once in `tools/webfoot/workbench/map_tab.py`:
`region.first` is the horizontal interval in engine map pixels, `region.second` the
vertical one, and the canvas rectangle is a single scene item at those coordinates.
The Qt side adds no offset, no scale and no origin of its own. Independent
confirmation, not a fixture: on the canonical image
`map:0039/transition:0001`'s region (`first 592-601`, `second 136-241`) lands exactly
on map 39's east doorway band, which `MAP-RESIZE-AND-LAYERS-001` had measured at
runtime as that map's only eastward passage. A transposed or offset mapping could not
put that rectangle on that door.

## Independent verification and the correction it produced

Frozen candidate `0ac734cb5be2bb424f00f35c2f0b933ef3eda0cd`, reviewed against all
twelve claims by a separate verification pass with no author context: **zero blocking
findings, eight non-blocking**. The correction applies the four it named and nothing
else, in the commit merged as part of `10178f557659e2d4fe26fadff321a43a32e5bb0b`:

* **NB1, the one behaviour change.** The region write reported success when the
  authority wrote nothing, so a drag over a canvas stale by exactly the drag delta
  pushed an undo entry over an edit that was never written - and that entry's Undo
  wrote the stale region back and **deleted a pre-existing authored region**. The
  write now propagates whether the project actually changed, history is pushed only
  for a real write, and the canvas is repopulated after every attempted edit. Pinned
  by `test_a_drag_that_writes_nothing_adds_no_history_and_keeps_the_authored_region`.
* **NB2** the record's test count was corrected from 19 to 20; **NB3** a trailing
  space was removed and the `git diff --check` claim corrected; **NB4** the byte test
  added `test_a_drag_above_0xFF_changes_only_the_four_region_halfwords`, because the
  existing assertion covered only the set of differing offsets with every endpoint
  under `0x100`, so a write that kept only the low byte of each region halfword would
  have passed.

The frozen candidate was not amended. The sub-pass merged into `master` as
`10178f557659e2d4fe26fadff321a43a32e5bb0b`.

## Validation

* Focused named files at the reviewed freeze: the new
  `tests/unit/test_workbench_map_warp_canvas.py` **20 passed**,
  `test_workbench_map_tab.py` **10**, `test_workbench_warp_transitions.py` **32**,
  `test_workbench_warp_creation.py` **78**; the four together **140 passed**.
  Neighbour runs added 133 passed and 195 passed / 5 skipped (the skips are the
  absent local canonical ROM). After the correction the new file defines **22**
  tests and the four together run **142 passed**. The new file was run three further
  times clean, with no Qt heap corruption.
* Visual QA states **90-97** of `tools/qa/visual_pass_capture.py`, captured from the
  real `MainWindow` and **opened and inspected** in two rounds: the overlay lands on
  the right map parts, stays legible over canopy and sand, a drag visibly moves the
  region, the list and canvas agree (authored, then retail after Undo), and the
  169-class refusal carries the shipped wording. One visual fix (a light chip behind
  the selected region's identity label) and one harness fix (state 96 no longer
  renders a second, minutes-long map) came out of looking at the captures.
* `git diff --check` clean over the corrected range; `git diff --numstat` equals
  `git diff --ignore-cr-at-eol --numstat` for every modified file; the new test file
  is LF-only like every modified file.
* **Test-policy record:** focused named files only; no broad suite, no `-m fast`, no
  `scripts/test.ps1`.

## Limitations preserved

* **A transition the project creates is drawn read-only and its region drag refuses.**
  Editing it would mean a second write path (`set_transition_creations`) in the
  canvas; that is scope this pass did not take, and it is stated rather than silent.
* **No runtime or emulator proof from this pass.** Whether the engine reads a dragged
  region as the door the author sees is a question for the parent's human-operated
  run; this pass produced project, GUI and build-level evidence only.
* **The status line after an Undo states "Moved the trigger region of ... to <the
  restored region>"** - the shipped placement-drag behaviour reused rather than a new
  message. It is accurate about the resulting region and slightly odd about the verb.
* **The shared-root refusal is asserted through a corpus built by the authority's own
  constructor**, because the real loader refuses a shared root that reaches records
  and an empty shared root has no transition to draw, so the state cannot be produced
  by loading an image. The refusal itself still comes from the shipped surface.
* **A staged creation the project has come to hold still has no per-row discard
  action**, unchanged from `MAP-WARP-CREATE-WORKBENCH-001`.

## Stop

Stopped after the correction, with the parent's map-surface half of Required Work 3
satisfied in full. The parent's own closeout states the final result: `warps` ships,
`EDIT` becomes **8 / 8**, DragonByte Z becomes **20 / 24 - 83%** and Phase 2 (Map
Editing) is complete.
