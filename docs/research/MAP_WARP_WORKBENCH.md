# The Maps editor Warps surface

The Warps surface in the Maps editor: what it adds, the SDK corrections it
required, the mutation record and the visual QA.

## What it adds

**One new Maps mode.** `Maps` has carried Browse / Layout / Objects; it now also
carries **Warps** (`tools/webfoot/workbench/warp_tab.py`, mounted in
`editors.py`). The mode is a thin client of the already-merged, runtime-proven
transition authority:

| surface | what it is |
| --- | --- |
| Connection list | one row per existing record of the chosen map: index, destination, trigger region (positional), arrival, facing, state |
| Selected connection | semantic identity, Leads-to selector, arrival X/Y, facing selector, trigger region, state chip, Apply / Revert |
| Map bar | a source-map selector whose label is the map's own semantic identity plus its connection count |

* **No address, offset or key byte is ever shown or typed.** The identity is
  `map:NNNN/transition:IIII`; the destination selector lists all 452 maps by their
  ROM-derived label with `map:NNNN` as the fallback when a map publishes no text,
  exactly as `map_view` and the Map Browser already do.
* **Trigger region is positional**, `first a–b · second c–d`, because which
  interval is which is `UNRESOLVED`; no axis name is invented.
* **Facing offers exactly five choices** - Unchanged, South, North, West, East.
  Unchanged authors **no** facing (the authority's own no-override state). Raw
  `+0x10` and its gate bits are never shown. A record whose byte is `0x02` reads
  **Unchanged**, not West.
* **169-class records are refused, not partially edited.** The row and the editor
  are read-only, with the reason on screen: the stored pair is a scene-relative
  delta, so the toolkit cannot state where the player lands on another map. The
  surface refuses destination, arrival *and* facing on such a record rather than
  offering a destination edit that would leave the delta pointing into the old
  scene.
* **Apply / Revert** follow the established staged-state model: Apply is one
  `set_transition_edits` write into `maps/transitions.toml` (which validates the
  whole batch against the canonical image before writing anything); Revert
  discards the staged change, or - with nothing staged - removes the project's
  saved edit so the retail connection applies again.
* **Undo / Redo** are real: one history entry per gesture, the whole draft as one
  command, so a combined retarget is one step. A no-op gesture enters no history.
  The shell routes Edit → Undo to the **active** mode's stack.

## SDK corrections the surface required (small, and each is a real defect)

1. **The low nibble of `+0x10` is now preserved whole** (`FACING_PRESERVED_MASK`).
   An arrival-facing write previously kept only the two gate bits, so a record
   carrying bits 2-3 would lose them; the record requires the unresolved low-nibble
   bits to survive. Every canonical low nibble is `0..3`, so this is
   **byte-identical on all 735 measured records** and strictly more conservative
   for any other image.
2. **`MapTransitions.check_edit`** - validate one request through the ordinary
   `set_destination`/`set_arrival`/`set_facing` path and record nothing. The
   surface answers "would the authority accept this?" *before* staging, with the
   authority's own rules and message, instead of restating a bounds or class rule
   in a widget.
3. **A corpus carries the profile it was read for.** `destination_bounds` re-read
   the MapEntry table through `packaged_profile()` regardless of the profile
   `read_map_transitions` was given, so a corpus read for any other profile
   answered the arrival bounds check from a table describing different maps (and
   raised on a synthetic image). `_read_corpus`/`MapTransitions` now carry it.
4. **One project→request conversion.** `build._transition_requests` moved to
   `map_transitions.transition_edits_to_requests`, and the build delegates to it.
   The surface that *displays* what the project authors and the build that
   *writes* it now read one implementation rather than two that could disagree.

No serializer was added: `TransitionRecord.to_bytes` remains the only encoder.

---

## Measured status summary

```text
MAP-WARP-WORKBENCH-001 - STATUS REPORT

BASELINE:
2ca0d833e004c069ed5f743652d1076289e3d608

WORKTREE:
<record worktree> (record/map-warp-workbench-001)

IMPLEMENTATION COMMITS:
c96b5084305470bca11c74afd0619fdfe7fce531 map_transitions: bind the corpus to its profile, preserve the facing
        low nibble, add check_edit
bfae3a52ea726369bfc017f935847994ef7ede74 workbench: add the Maps editor's Warps mode
0c58517516698669cd41aa54244bc1c976286c66 tests: cover the Warps surface, its refusals and the authority corrections
d18e7c4ee8733db461804fc8cfeae3a6afc2762a qa: capture the Warps surface from the real application
767a64619d30ef731fa001188bef7a0a953d0618 docs: record MAP-WARP-WORKBENCH-001 and its progress note
c31a7e56b43f79d861646bcb5d92bc63a09897b6 merge origin/master (8724ebecd08d858a02de5c17c43102aae824ebfb, WARPRAND-APP-001) - conflict-free, additive
a commit since folded into its successor docs: add the independent review brief  <-- FROZEN REVIEWED CANDIDATE

FROZEN REVIEWED CANDIDATE:
a commit since folded into its successor

INDEPENDENT REVIEW:
APPROVE - zero blocking findings, two NOTE-level observations, no production
correction. The review job (an independent local review); record:
MAP-WARP-WORKBENCH-001-review.md

TRANSITION LIST:
PASS - one row per record of the chosen map; index, destination label,
positional trigger region, arrival, facing, state. No address in any cell or
tooltip.

SUPPORTED 566 EDIT:
PASS - destination, arrival and facing all stage and apply through the existing
authority; the retarget derives its arrival and defaults its facing in the same
gesture.

CLASS-169 RETARGET:
REFUSED SAFELY - whole record read-only with the measured reason; every gesture
refuses and stages nothing; the authority refuses an arrival for such a record
independently.

DESTINATION EDIT:
PASS

ARRIVAL EDIT:
PASS - the pair is shown and edited as the production model states it (two
positional coordinates); an off-map point is refused with the authority's own
message.

FACING EDIT:
PASS - Unchanged / South / North / West / East; Unchanged authors no facing.

LOW-NIBBLE PRESERVATION:
PASS - 0x0E + South authors 0x1E end to end.

APPLY/REVERT:
PASS - Apply is one project write and writes nothing when the project already
holds the value; Revert un-stages, or un-authors a saved edit.

UNDO/REDO:
PASS - destination, arrival, facing and the combined retarget each return their
exact authored values; one entry per gesture.

NO-OP:
PASS - an edit that asks for the base value stages nothing, creates no undo entry
and no project change.

CQA-05:
PASS - an unrelated project mutation keeps the staged draft and the history; a
true session replacement clears both.

CQA-06:
PASS - the 169-class refusal, an off-map arrival, a destination with no
connection back and a malformed maps/transitions.toml all reach the status line
and the editor's reason field; a refused Apply raises the SDK message through the
normal warning surface, never a dead click.

CQA-07:
PASS - measured call counts, not wall clock. Loading the surface reads the
corpus once, the project once and the labels once. Selecting a map, selecting a
row, changing destination/arrival/facing and undoing/redoing read NOTHING. One
Apply is exactly one project write, one corpus read, two project parses and one
re-read of the authored document - none of which grows with the number of rows,
controls or staged fields.

SAVE/REOPEN:
PASS - Apply, then a fresh session and a fresh surface over the same project,
shows the same destination, arrival and facing, and the production authority
builds exactly that record.

VISUAL QA:
PASS - 10 states captured from the real application against the canonical image
and opened for inspection (states 60-69). Four defects found and fixed.

M1-M4:
PASS - all four mutations produced the expected named failure and were restored.

MANUAL VALIDATION:
Final focused run, by named file:
tests/unit/test_workbench_warp_transitions.py (32), test_map_transitions.py,
test_map_transition_project.py, test_map_arrival_semantics.py,
test_warp_randomizer.py, test_workbench_smoke.py,
test_workbench_state_and_errors.py, test_test_gates.py,
test_ci_gui_surface.py - 268 passed, 1 skipped (the CI-environment-only
contract check, skipped outside CI by design).
Earlier in the pass, the wider affected set was also re-run by name and passed:
test_workbench_map_browser.py, test_workbench_project_status.py,
test_workbench_scene.py, test_workbench_map_tab.py,
test_workbench_chunk_authoring.py, test_workbench_resize_and_layers.py,
test_workbench_graphics.py, test_workbench_graphics_undo.py,
test_workbench_dialogue.py, test_workbench_palette_cost.py,
test_workbench_launcher_settings.py, test_workbench_build_run_dialogs.py -
308 passed, 1 skipped (the canonical ROM is not present inside the worktree).
git diff --check: clean.

BROAD SUITE:
NOT RUN

CANONICAL ROM:
UNCHANGED - SHA-256 940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e

PRODUCT CAPABILITY IMPACT:
NONE

DRAGONBYTE Z:
19 / 24 - 79%

PARENT:
MAP-WARPS-AND-CONNECTIONS-001 - NOT SHIPPED

NEXT:
RETURN FOR REVIEW
```

---

## Focused validation, in detail

### Named test file

`tests/unit/test_workbench_warp_transitions.py` - **32 passed**. The synthetic
image is the one `test_map_transitions` assembles from the measured format,
extended with the two root words the engine's own walkable extent comes from; the
project is a real on-disk project written by the real `write_project`. No SDK path
is mocked.

Covered by name: list population and address-freedom; the empty map; selection;
the semantic destination selector; the combined retarget (destination + derived
arrival + defaulted facing in one entry); an arrival-only edit; a facing-only edit;
the five-choice facing vocabulary with `0x02` reading Unchanged; low-nibble
preservation (`0x0E` + South → `0x1E`); a destination with no connection back
refused; an off-map arrival refused; the no-op rule; the 169-class read-only state
at the surface *and* the authority; `check_edit` recording nothing; Apply/Revert;
Apply-is-not-a-no-op-write; revert-is-undoable; undo/redo for each field and for
the combination; a no-op gesture entering no history; CQA-05 both halves; CQA-06
(malformed project document, refused Apply, apply without a project); CQA-07 exact
read/write counts; save/reopen; byte locality of the applied retarget.

### Mutations, each observed and restored

| id | mutation | regression that failed |
| --- | --- | --- |
| M1 | the row selection resolved to the wrong transition identity | `test_selecting_a_row_loads_its_editable_state` - `'map:0000/transition:0000' == 'map:0000/transition:0001'` |
| M2 | the facing display read the raw low bits as a direction | `test_the_facing_control_offers_five_choices_and_no_raw_byte` and `test_the_list_shows_the_maps_connections_without_addresses` - the `0x02` record read `West` |
| M3 | the class-169 record treated as retargetable | `test_a_169_class_connection_is_read_only_with_a_reason` - `selected_editable()` returned True |
| M4 | a project mutation discarded the staged draft | `test_a_project_mutation_keeps_the_staged_connection_edit` - the staged draft was None |

No repository-wide mutation framework was added; each mutation was a local edit,
observed, and reverted, and the file passes afterwards.

### Visual QA

States 60-69 of `tools/qa/visual_pass_capture.py` (`warp_qa`), captured from the
real `MainWindow` against the canonical image and a real extracted project, then
**opened and inspected**:

| state | subject |
| --- | --- |
| 60 | the connection list on a map with two connections, nothing staged |
| 61 | one connection selected, its editable state populated |
| 62 | a staged retarget: row and editor agree, Apply enabled |
| 63 | undo back to retail (byte-identical to state 60) |
| 64 | after Apply: state Saved, Revert enabled, status names the write |
| 65 | after Revert: back to the retail connection |
| 66 | a 169-class connection: read-only row and editor with the reason |
| 67 | a destination with no connection back: the refusal, on screen |
| 68 | the narrow window (1100x720) |
| 69 | a map with no connections: the empty state |

Defects found by looking at the captures and fixed:

1. the map bar repeated the connection count the selector already carried;
2. the state chip used the pending/error roles for every state, so "Retail" and
   "Read-only" carried the emphasis of work in progress; each state now has its
   own role (neutral / saved / pending / readonly);
3. a read-only record showed the hint "Type the point the player should arrive
   at." beside controls that are disabled; the hints are now empty for a record
   the authority will not retarget, and the reason line states why;
4. selecting a map with no connections left the previous selection's destination
   and arrival on screen; the editor now clears to a true empty state.

Post-fix captures were re-opened and inspected; the shell's 813x326 minimum at
1100x720 shows no clipped control. The captures are local, ignored QA artifacts
under `build/qa/` (`warp3` for states 60-69 after the first three fixes,
`warp-final/69-warps-map-with-no-connections.png` for the empty state after the
fourth); nothing ROM-derived is committed.

## Not in this sub-pass

* **No runtime/emulator proof.** The parent still owes the human-operated
  end-to-end run of a Workbench-authored transition; this sub-pass produced
  project and build evidence only.
* **No new transition.** The array, its count and its pointer are not touched by
  this surface at all.
* **No capability advance.** 20 / 24 happens only when the parent ships.
* **No registry or public-site change.**
* **The shell's unsaved-work guard is unchanged.** `MapsEditor.unsaved_edit_count`
  and the ROM-open discard dialogue remain scoped to layout edits, because those are
  the Save-As-bound edits that guard exists for; a staged transition edit is
  project-bound like an unapplied palette or dialogue value, which the guard's own
  docstring already describes as cleared by a session change by design. The
  surface states its own staged count in its status line, its map bar and its row
  states.
