# Connections on the Maps canvas

The map-connection overlay on the Maps canvas: selection, the direct canvas edit,
the coordinate mapping, fail-closed behaviour and the visual QA record.

## What it adds

The Maps editor's **Objects** canvas already drew the rendered map and its
placement markers. It now also draws every connection of the displayed map as its
**trigger region**, and that overlay is directly editable.

### 1. The overlay

* One `TransitionOverlay` per connection of the current map, drawn as the
  record's own two ordered intervals. It is a `QGraphicsRectItem` at the region's
  own coordinates, so the view's **one** zoom/scroll transform carries it exactly
  as it carries the rendered artwork and the placement markers - there is no
  second coordinate system and no per-paint arithmetic.
* **Authored values win.** The region drawn is the one a build would apply: the
  project's authored region where it has one, the record's own otherwise. The
  project's two transition documents are read **once per project revision**
  (`read_project`, then `transition_edits_to_requests` /
  `transition_creations_to_requests`), and the connection corpus is resolved
  **once per session** (`read_map_transitions`). A repaint, a layer change, a
  zoom, a pan, a selection or a scroll reads nothing at all.
* **Created transitions are drawn too**, at the region the project authors for
  them, because they are connections the build will materialize. They are not
  draggable, and that is stated rather than silent (see Fail closed).
* Retail and authored regions are distinguishable by hue (`region_retail`,
  `region_authored`), the whole rectangle carries a white halo under a dark edge
  so it reads over any palette, and the wash is light enough that the terrain
  under a door stays legible.

### 2. Click to select

* A press that ends where it started is a **click**: the canvas marks that
  connection and emits `transitionSelected`. The Maps editor answers it with
  `show_transition`, which switches to the **Warps** mode and selects that
  connection's row (`select_source_map` + a new `select_identity`), so the
  shipped form states the connection being edited.
* The identity travels as the SDK's own value (`TransitionIdentity` /
  `CreatedTransitionIdentity`); the row is found by identity, never by matching
  display text.
* **One owner.** The Warps editor owns which connection is selected. Coming back
  to the Objects mode re-reads that selection
  (`MapsEditor.set_mode` -> `show_selected_transition(warps.selected_identity())`),
  so a row picked in the list marks its region and a highlight cannot go stale.
* Clicking **empty canvas** clears the canvas selection (a view-level
  `backgroundPressed`, because the scene emits nothing when there was nothing
  selected to clear), and clicking a **placement marker** clears it too - exactly
  one thing on the canvas is selected at a time.

### 3. One direct canvas edit

* A press that ends elsewhere is a **drag**: the rectangle moves, and on release
  the region is translated as a whole (both endpoints of the horizontal interval
  by `dx`, both of the vertical one by `dy`), so the region's size is preserved
  and a drag cannot make an interval unordered or degenerate.
* The write goes through `map_transitions.set_transition_edits` - the same entry
  point the Warps editor's Apply uses - with a region-only `TransitionEdit`, so
  the authority measures the prior itself, rewrites exactly the one record's
  eight region bytes and leaves every other field of that record, and every other
  record, alone.
* **One undoable entry** (`TransitionRegionCommand`), resolved before it is
  pushed: Qt calls `redo()` inside `push()`, so a refusal must not cross that
  frame. `undo()`/`redo()` re-apply a stored region through the same authority
  path and catch the whole failure family.
* **A drag that ends where it started writes nothing and enters no history.**
* Save/reopen reproduces the authored region, because the project is the only
  carrier of it.

### 4. Fail closed

The canvas states **no** editability rule of its own. The Maps editor installs
the Warps surface's `region_edit_refusal` as the guard, and every drag asks it:

| refused | why (the surface's own words) |
| --- | --- |
| 169-class record | its stored arrival is a scene-relative delta; the row is read-only |
| destination key resolves to no map | the record's destination is unresolved |
| selector-1 root shared with another map | the count and array pointer belong to the root, not the map |
| no project, or an unreadable project document | nothing to author into |
| a transition the project creates | it has no record in the image; its region is authored in the Create form |
| **no guard installed at all** | a canvas with no authoring surface behind it edits nothing |

The refusals are shown through the same surface the Warps editor uses (a
`QMessageBox.warning` plus the status line). Two more paths fail closed without
inventing a rule:

* an endpoint translated outside the `u16` domain is refused by
  `TransitionRegion` itself, in the codec's own wording;
* a project whose transition documents cannot be read draws **no** regions at
  all, rather than drawing retail regions as if the project authored nothing.

Regions a refusal covers are still **drawn** (with a dashed edge, so the state is
visible before the gesture), and they are still draggable precisely so the
refusal can be read - a region that silently refused to move would be the
WORKBENCH-001 dead click.

The Warps list had one gap this pass closed: its `Trigger region` column read the
record's own region even when the project authored a different one. It now reads
the project's value over the record's, exactly as its destination, arrival and
facing columns already did, so the list and the canvas cannot state two different
regions for one connection.

## The coordinate mapping

Measured, and stated once, in `tools/webfoot/workbench/map_tab.py`:

```text
region.first  = (low, high) horizontal, in the engine's map pixels
region.second = (low, high) vertical,   in the engine's map pixels

canvas rectangle = QRectF(first_low, second_low,
                          first_high - first_low, second_high - second_low)
```

The canvas has exactly one coordinate space - the engine's map pixels - so the
rectangle is one scene item at those coordinates and the `QGraphicsView`
transform (zoom and scroll) places it exactly as it places the artwork and the
placement markers. **The Qt side adds no offset, no scale and no origin of its
own.** The first-interval-horizontal / second-interval-vertical reading is the
measured one the record states.

Independent confirmation from the visual pass, not from a fixture: on the
canonical image, `map:0039/transition:0001`'s region is `first 592-601`,
`second 136-241`, and the rendered overlay lands exactly on map 39's east doorway
band - `x 592..601 / y 136..241` - which `MAP-RESIZE-AND-LAYERS-001` had
measured at **runtime** as that map's only eastward passage. A transposed or
offset mapping could not put that rectangle on that door.

## Focused validation

Named files only; no broad suite, no `-m fast`, no `scripts/test.ps1`.

| command | result |
| --- | --- |
| `python -m pytest tests/unit/test_workbench_map_warp_canvas.py -q` | **20 passed** (reviewed freeze; 22 after the correction) |
| `python -m pytest tests/unit/test_workbench_map_tab.py -q` | **10 passed** |
| `python -m pytest tests/unit/test_workbench_warp_transitions.py -q` | **32 passed** |
| `python -m pytest tests/unit/test_workbench_warp_creation.py -q` | **78 passed** |
| all four files in one run | **140 passed** (10.5 s) (reviewed freeze; 142 after the correction) |
| `test_workbench_state_and_errors.py`, `test_workbench_smoke.py`, `test_workbench_map_browser.py`, `test_workbench_chunk_authoring.py` | **133 passed** |
| `test_workbench_graphics.py`, `test_workbench_chunk_authoring.py`, `test_workbench_resize_and_layers.py`, `test_workbench_scene.py`, `test_workbench_session.py`, `test_workbench_build_run_dialogs.py`, `test_workbench_dialogue.py` | **195 passed, 5 skipped** (the skips are "canonical Buu's Fury ROM not present locally", which this worktree does not hold; `test_workbench_chunk_authoring.py` appears in both neighbour runs and is not counted twice anywhere) |
| `git diff --check` | **clean over the corrected range** (the first freeze carried one trailing space at line 204, which the review caught and this correction removed) |
| `git diff --numstat` vs `git diff --ignore-cr-at-eol --numstat` | **identical for every modified file** (no ending churn) |

The new test file is tracked at the frozen candidate; it is LF-only, like
every modified file.

### What the new file covers, by test name

* **Overlay geometry**: `test_the_overlay_is_the_regions_own_rectangle_in_map_pixels`
  (both records of the fixture map, so a transposed interval cannot pass),
  `test_the_view_transform_carries_the_region_exactly_as_it_carries_the_map`
  (a non-unit zoom, the mapping back through the view, and a scrolled viewport).
* **Authored values win**:
  `test_an_authored_region_is_drawn_instead_of_the_retail_one` (and the Warps row
  agrees), `test_a_transition_the_project_creates_is_drawn_at_its_authored_region`.
* **Click-select wiring**:
  `test_clicking_a_region_selects_that_connection_in_the_warps_editor` (a real
  `QTest` click through a real `MapsEditor`: the mode becomes `warps`, the map
  and the row are the connection's, the form agrees, and a second click selects
  the other connection),
  `test_the_canvas_marks_the_connection_the_warps_editor_has_selected` (a row
  picked in the list, then the canvas),
  `test_clicking_empty_canvas_clears_the_canvas_selection`,
  `test_selecting_a_placement_marker_clears_the_region_selection`.
* **The drag**: `test_a_drag_writes_only_the_region_and_is_one_undo_entry` (the
  built record differs from retail at `+0x08`, `+0x0A`, `+0x0C`, `+0x0E` and
  nowhere else; destination, arrival, class, facing and the constant word are
  byte-identical; one history entry),
  `test_undo_and_redo_restore_the_exact_original_bytes` (undo leaves the project
  with no authored region and the built record byte-for-byte retail),
  `test_a_drag_that_ends_where_it_started_adds_no_history`,
  `test_the_region_reproduces_after_save_and_reopen`,
  `test_a_real_mouse_drag_commits_one_undo_step` (press, move, release: one
  entry, both interval widths preserved, one common delta).
* **Fail closed**:
  `test_a_169_class_connection_refuses_the_drag_in_the_surfaces_words`,
  `test_a_shared_connection_root_refuses_the_drag`,
  `test_a_connection_this_image_does_not_hold_refuses_in_the_authoritys_words`
  (an identity the corpus lacks - the unsupported-form answer one step later),
  `test_an_out_of_domain_drag_is_refused_by_the_codec_and_leaves_no_history`,
  `test_a_canvas_with_no_authoring_surface_refuses_every_drag`.
* **Bounded reads (CQA-07)**: `test_painting_selection_and_zoom_read_nothing`
  (selection, re-selection, zoom and a repaint: corpus 0, project 0),
  `test_a_map_switch_resolves_no_corpus_again_and_parses_the_project_once`
  (corpus 0; the one project parse is the placement facade's own, which predates
  this overlay; the overlay's authored-region read is cached against the project
  revision and adds none).

The shared-root test builds the corpus through the authority's own constructor,
and says why in its docstring: the real loader refuses a shared root that reaches
records (two maps would read one array), and an empty shared root has no
transition to draw, so that state cannot be produced by loading an image. The
refusal it asserts still comes from the shipped surface, through the same guard
every other drag goes through.

## Visual QA

States **90-97** of `tools/qa/visual_pass_capture.py` (`warp_canvas_qa`), captured
from the real `MainWindow` against the canonical image and a real extracted
project, then **opened and inspected** (two rounds, `build/qa/warp-canvas-3` and
`build/qa/warp-canvas-4`). Captures are local, ignored artifacts; nothing
ROM-derived is committed.

| state | subject |
| --- | --- |
| 90 | the Objects canvas with both of map 39's trigger regions drawn |
| 91 | a region clicked: the Maps editor is in Warps with that row selected |
| 92 | back on the canvas: the region the Warps editor has selected is marked |
| 93 | after a drag: the region has visibly moved, status names the new region |
| 94 | the Warps list and form after the drag: the authored region, state Saved |
| 95 | after Undo: both surfaces are back on the retail region, Redo is armed |
| 96 | a 169-class region: drawn, dashed, framed |
| 97 | the refusal dialog for that connection |

What was seen, specifically:

* **The overlay lands on the right part of the map.** `map:0039` has two
  connections: `transition:0001` at `first 592-601 / second 136-241` and
  `transition:0000` at `first 96-257 / second 0-17`. On the rendered map the
  first is the vertical band across the fence's gap, exactly the doorway
  `MAP-RESIZE-AND-LAYERS-001` measured at runtime, and the second is the wide
  band along the top-left grass. Both are in the right place and neither is
  offset or transposed.
* **It is legible against the terrain.** The white halo under the edge keeps the
  region readable over both the bright green canopy and the pale desert, at 86%
  and at 135%.
* **A dragged region visibly moves.** After a 24, 18 drag the rectangle sits
  below and right of the fence gap, and the status line reads `Moved the trigger
  region of map:0039/transition:0001 to first 616-625, second 154-259`.
* **The selection is indicated** by a thicker selection-coloured edge and by the
  connection's identity on a chip.
* **The two surfaces agree.** The Warps list and form show `first 616-625,
  second 154-259` with state `Saved` immediately after the drag, and the retail
  region again after Undo.
* **The refusal is the surface's own**: the dialog for the 169-class record reads
  `169-class connection: its stored arrival is a scene-relative delta rather than
  a point, so the toolkit cannot safely retarget it. Read-only in this pass.`

**One defect the pass found and fixed:** the selected connection's identity label
was drawn directly on the artwork and was hard to read over the dark canopy. The
overlay now paints a light chip behind the label, and the re-capture shows it legible
over foliage. Nothing else was wrong in the captures.

**One harness defect the first round found:** state 96 originally opened a second
map chosen only for having 169-class records, and that map's render ran for
minutes (the first capture attempt was killed at 10 minutes with states 90-95
written). The state now uses the map the capture already rendered, chosen to hold
BOTH classes, so the editable and the read-only region appear on one canvas and
one render. It also centres the read-only region before grabbing, so a region on a
map edge is not captured as half a rectangle.

**One wording observation, recorded rather than changed:** the 169-class refusal
sentence names *retargeting*, because it is the Warps surface's own read-only
reason for that record. Reusing it verbatim is what "never invent a rule in Qt"
requires; a region-specific second sentence would be a second statement of the
same rule.

## Not done, or not verified

* **Dragging the region of a transition the project CREATES is not implemented.**
  Such a transition is drawn at its authored region and its drag is refused with
  the Create form named. Editing it would mean a second write path
  (`set_transition_creations`) in the canvas; that is scope this pass did not
  take, and it is stated rather than silent.
* **No runtime/emulator proof.** Whether the engine reads a dragged region as the
  door the author sees is a question for the parent capability's human-operated
  run; this pass produced project, GUI and build-level evidence only.
* **The full suite was not run**, by the record's instruction and the
  evidence-proportional policy: the touch is GUI-only plus two Qt-side
  neighbours, and the focused files above bound it.
* **Independent review: PASS.** The frozen candidate
  `5f588049f0063431cfd8b1739e4c9b53f7cfeaed` was reviewed against all twelve
  claims by a separate verification pass: zero blocking findings, eight non-blocking. NB1
  was a real defect and is fixed in the correction section below; NB2 is the
  endpoint test added there; NB3 and NB4 are the two record corrections made
  there.
* **The status line after an Undo states "Moved the trigger region of ... to
  <the restored region>"**, which is the shipped placement-drag behaviour reused
  rather than a new message. It is accurate about the resulting region and
  slightly odd about the verb.

## Correction after independent verification
Findings are bound to the review's numbers explicitly: NB1 is the phantom-undo
defect fixed here; NB2 is the high-byte coverage added here as
`test_a_drag_above_0xFF_changes_only_the_four_region_halfwords`; NB3 is the
`git diff --check` claim and the trailing space corrected here; NB4 is the test
count corrected here.


This section supersedes the review status recorded above. The independent review
passed the frozen candidate `5f588049f0063431cfd8b1739e4c9b53f7cfeaed` with **zero blocking findings and eight
non-blocking** ones; this pass applies the four it named, and nothing else.

* **NB1 - the one behaviour change.** The region write reported success when the
  authority wrote nothing, so `_on_overlay_drag` pushed a `TransitionRegionCommand`
  over an edit that was never written. Measured consequence: with the canvas's drawn
  region stale by exactly the drag delta, a drag reported success, added one history
  entry, wrote nothing, and that entry's Undo wrote the stale region, deleting a
  pre-existing authored region. `_write_transition_region` now propagates whether the
  project actually changed (`True` changed, `False` nothing written, `None` refused),
  `_on_overlay_drag` pushes history only for a real write, and the canvas is
  repopulated after every attempted edit, so it shows the project's truth either way.
  Pinned by
  `test_a_drag_that_writes_nothing_adds_no_history_and_keeps_the_authored_region`
  (a pre-existing authored region plus an overlay stale by exactly the drag delta: the
  drag reports no write, no history entry is added, and the authored region survives
  the Undo).
* **NB2 and NB3 - the two record corrections.** The file row above said the new
  focused file defines 19 tests; it defines **20** at that freeze. And this record
  claimed `git diff --check` was clean while line 204 carried one trailing space,
  which made the check over the first freeze exit 2; the space is removed, so the
  check is clean over the corrected range - baseline `3431fba0039da6bd30fdc01a3f9acb08093b553d` through this
  correction's commit. The frozen candidate `5f588049f0063431cfd8b1739e4c9b53f7cfeaed` still carries the space, because
  an amended freeze is not permitted.
* **NB4 - the byte test's coverage.** It asserted only the SET of differing offsets,
  and every endpoint in its fixture was under `0x100`, so a write that kept only the
  low byte of each region `u16` would have passed. The new
  `test_a_drag_above_0xFF_changes_only_the_four_region_halfwords` drags to
  `first (400, 440)` / `second (320, 360)` and asserts that exactly the four halfwords
  at `+0x08`, `+0x0A`, `+0x0C` and `+0x0E` change - `0x0190`, `0x0140`, `0x01B8`,
  `0x0168` little-endian - and that `+0x00..+0x07` and `+0x10..+0x17` are
  byte-identical to before.

Re-measured after this correction (the focused table above records the reviewed
freeze): the focused file defines **22** tests - the reviewed 20 plus the two added
here - and the four named files run **142 passed** together
(22 + 10 + 32 + 78).
