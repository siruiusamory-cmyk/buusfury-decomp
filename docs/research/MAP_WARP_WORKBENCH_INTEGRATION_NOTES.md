# The Maps editor Warps surface: integration notes

The condensed record of the Warps-surface pass: what shipped, the limits kept and
the validation.

## Scope

Advance the GUI half of the parent's Required Work 3: make an existing supported
transition observable and revisable in the Workbench, through the already-merged
authority, without a second serializer, without exposing a ROM offset to an author,
and without creating a transition.

## What shipped

`Maps` gained a fourth mode, **Warps** (`tools/webfoot/workbench/warp_tab.py`,
mounted in `editors.py`), as a thin client of the runtime-proven transition
authority:

| surface | what it is |
| --- | --- |
| Connection list | one row per existing record of the chosen map: index, destination, trigger region (positional), arrival, facing, state |
| Selected connection | semantic identity, Leads-to selector, arrival X/Y, facing selector, trigger region, state chip, Apply / Revert |
| Map bar | a source-map selector labelled with the map's own semantic identity and its connection count |

Behaviour, as measured by the record:

* no address, offset or key byte is ever shown or typed; the identity is
  `map:NNNN/transition:IIII`;
* the trigger region is positional (`first a-b - second c-d`) because the axis was
  `UNRESOLVED` at this pass and no axis name was invented;
* facing offers exactly five choices - Unchanged, South, North, West, East - and a
  record whose byte is `0x02` reads **Unchanged**, not West;
* a 169-class record is read-only with the reason on screen, and destination,
  arrival and facing are all refused on it rather than offering a destination edit
  that would leave the stored delta pointing into the old scene;
* Apply is one `set_transition_edits` write into `maps/transitions.toml`; Revert
  discards the staged change, or removes the project's saved edit; Undo/Redo are one
  history entry per gesture, and a no-op enters no history.

Four SDK defects the surface exposed were corrected in the same branch, and each is
recorded as a real defect rather than a convenience: the low nibble of `+0x10` is
preserved whole (`FACING_PRESERVED_MASK`, byte-identical on all 735 measured
records); `MapTransitions.check_edit` validates one request through the ordinary
path and records nothing; a corpus now carries the profile it was read for, so
`destination_bounds` no longer answers from a table describing different maps; and
`build._transition_requests` moved to
`map_transitions.transition_edits_to_requests`, so the surface that displays what
the project authors and the build that writes it read one implementation.

## Independent verification

One pass, independent context, an independent local review headless. Frozen reviewed candidate
`a0d9cab12379e8692fef5cfe32f0baca4394734b`; job `the review job`.

**Verdict: `APPROVE` - zero blocking findings, two NOTE-level observations, no
production correction.** The candidate was not amended, and the commits after it
are documentation only. Merged into `master` as
`7efbb9c1f83169f42c548557fb3bab1fb73f8804`, after the branch merged
`5e01f5fec177e4d3413a6ff2c19b9b46265739a6` (WARPRAND-APP-001) conflict-free and
additively only.

## Limitations preserved

These were true at this pass and are not erased by the parent shipping:

* **No runtime proof at this pass.** The human-operated end-to-end run of a
  Workbench-authored transition was still owed, and was later supplied by
  `MAP-WARP-WORKBENCH-RUNTIME-001`.
* **No new transition.** The array, its count and its pointer were not touched by
  this surface; creation was later supplied by `MAP-WARP-CREATE-PROJECT-001` and
  `MAP-WARP-CREATE-WORKBENCH-001`.
* **The trigger region was positional**, because which interval is horizontal and
  the endpoints' unit were `UNRESOLVED`. `MAP-WARP-CREATE-RUNTIME-001` later
  measured the first interval as horizontal in map pixels; the surface's positional
  vocabulary is retained as the authority's own.
* **A one-way destination requires the arrival to be stated explicitly**: the
  destination-only step is refused because no arrival can be derived, which is a
  real authoring constraint rather than a defect.
* **The shell's unsaved-work guard is unchanged.** A staged transition edit is
  project-bound like an unapplied palette value; the surface states its own staged
  count in its status line, its map bar and its row states.
* **The map surface was not yet drawn or edited here.** The other half of Required
  Work 3 - transitions drawn and edited on the existing map canvas - was untouched
  and was later supplied by `MAP-WARP-CANVAS-001`.

## Validation

* Focused named file `tests/unit/test_workbench_warp_transitions.py`:
  **32 passed**, over the synthetic image the format sub-pass assembled and a real
  on-disk project written by the real `write_project`; no SDK path is mocked.
* Mutations **M1-M4**, each observed failing a named regression and then reverted:
  wrong row identity (`test_selecting_a_row_loads_its_editable_state`), raw facing
  bits read as a direction (`test_the_facing_control_offers_five_choices_and_no_raw_byte`),
  a 169-class record treated as retargetable
  (`test_a_169_class_connection_is_read_only_with_a_reason`), and a project mutation
  discarding the staged draft
  (`test_a_project_mutation_keeps_the_staged_connection_edit`).
* Visual QA states 60-69 of `tools/qa/visual_pass_capture.py`, captured from the
  real `MainWindow` and opened and inspected. Four defects were found by looking and
  fixed; the captures are ignored local artifacts under `build/qa/`.
* **Test-policy record:** focused named files only, per the record and the
  evidence-proportional policy; no broad suite was run in this pass.

## Stop

Stopped after the review and the merge. At that point the parent's Required Work 4
and the map-surface half of Required Work 3 remained, and the capability advance to
**20 / 24** had not happened. `MAP-WARP-WORKBENCH-RUNTIME-001` and
`MAP-WARP-CANVAS-001` followed; the parent's own closeout states the final result.
