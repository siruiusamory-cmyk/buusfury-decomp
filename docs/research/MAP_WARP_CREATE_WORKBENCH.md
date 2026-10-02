# The Warps surface Create Transition action

The Create Transition action on the Warps surface: the SDK additions it needed, the
defect it found, the focus validation, the ownership correction and the invariant it
converged on.

## What it adds

`Maps -> Warps` gains a **Create Transition** action beside the map selector. It
opens a compact form on the right-hand pane that authors a transition the image
does not contain, and stages it as one semantic project creation.

| field | what it is |
| --- | --- |
| Connection | `map:NNNN/transition:<name>` - the durable identity, previewed live. Only the name is typed; the map half comes from the map bar |
| Name | the authored name, validated by `CreatedTransitionIdentity` - the production model's own rule and wording |
| Based on | the existing same-map connection the new one starts from, listed from the authority's own `creation_templates` |
| Trigger region | `first` / `second`, the codec's positional intervals, authored as four bounded integers |
| Leads to | the existing semantic destination selector - no key byte, no address |
| Arrival | the authored X/Y pair. **Required and never derived**: a new transition has no existing link to derive one from |
| Facing | Unchanged / South / North / West / East. Unchanged authors no override |

* **The base list is the measured 566 class only** - `creation_templates` filters on
  `CREATED_CLASS_RAW`, so a 169-class record cannot appear, and the authority refuses
  one anyway ("scene-relative delta"). A map with no 566-class base **fails closed**
  with the reason on screen, and so does a map whose selector-1 root is shared with
  another map (its count and array pointer are not this map's to grow).
* **Every gesture is validated by the authority before it is staged**
  (`check_transition_creation`, the creation-side mirror of `check_edit`), so the
  class rule, the same-map rule, the template priors, the destination's walkable
  extent and the "not an alias of its base" rule are the build's rules, stated in the
  build's words.
* **Staging is derived from the form** and rendered in the list immediately: the new
  row carries the authored name in the identity column and a **New (staged)** state,
  becoming **New (saved)** once Apply writes it. Selecting it reopens the form.
* **Apply / Revert.** Apply is one `set_transition_creations` write into
  `maps/transition_creations.toml` - never `transitions.toml` - that validates the
  whole batch first and writes nothing when the project already holds it. Revert
  returns the form to the last saved state and writes nothing: a staged creation is
  discarded with no project residue, and the gesture is itself undoable.
* **Undo / Redo** are real: one history entry per gesture (name, base, region,
  destination, arrival, facing), each entry carrying the whole resolved creation
  state, so undo returns the exact authored values. A no-op gesture enters no history.

## SDK additions (facades over existing authority, no new logic)

1. **`check_transition_creation(corpus, creation)`** - validates one creation
   through the same `_resolve_creation` a build uses, recording nothing and reading
   nothing: the corpus is already loaded, and the template's `+0x10`/`+0x13` priors
   are measured from it. The form's second gate, so a widget never restates a class,
   root-sharing or bounds rule.
2. **`creation_templates(corpus, source)`** - the one statement of which records may
   be a creation's base (`CREATED_CLASS_RAW`), used by the surface and by nothing
   else.
3. **`authored_transition_creation(corpus, creation)`** - measures the template
   priors once, for both the check and `set_transition_creations`, which now share it
   instead of each measuring them.

No serializer was added: `TransitionRecord.to_bytes` remains the only encoder, and
`materialize_transition_creations` remains the only creator.

## A real defect this pass found and fixed

The creation form's first implementation let a Python exception escape
`QUndoCommand::redo()` when the authority raised inside a gesture. Under the new
focused test file that corrupted the heap (`Windows fatal exception: code 0xc0000374`
during garbage collection, ~40% of runs, localised by collecting before each test to
the test that threw through Qt). The fix is structural and stays:

* **every gesture resolves BOTH of its states - the draft and the staged entry, with
  the authority's answer - before the command is pushed**, and `undo()`/`redo()` only
  install an already-resolved :class:`CreationState`;
* a programmer error from the authority therefore surfaces at the call site, loudly,
  with no history entry, instead of unwinding through Qt's C++ undo stack.

The heap corruption disappeared with that change (3 consecutive clean runs of the
full file, and 3 more after the visual fixes), and the property is pinned by
`test_cqa06_a_programmer_error_in_a_slot_is_loud`.

---

## Focused validation, in detail

### Named test file

`tests/unit/test_workbench_warp_creation.py` - **58 passed as first written, 67 at
the frozen tip** (the review corrections added nine pins). The synthetic image is
the one `test_map_transitions` assembles from the measured format, extended with the
two root words the destination's walkable extent comes from; the project is a real
on-disk project written by the real `write_project`; every creation goes through the
real authority and the real build.

Covered by name: the Create action's availability and its fail-closed refusals
(no project, no image, no 566-class base, shared root); the valid-template filter and
the 169-class exclusion at the surface *and* at the authority; the durable authored
name validated by the production model, with its wording; duplicate identity refused
both against the project document and against another staged draft, while a row
opened from the saved creation stays re-authorable; the trigger region's positional
authoring and the codec's degenerate/unordered refusals; the semantic destination
selector and an out-of-range map; the required, never-derived arrival and an off-map
point; the five facing choices, an invalid direction, and Unchanged; low-nibble
preservation end to end; the staged row appearing immediately and its
New (staged) â†’ New (saved) states; Apply writing only the creation document, Apply
with nothing staged, Apply of an already-held creation; the refused-Apply dialog;
Revert without residue and Revert of a saved creation; Close and map-change behaviour;
undo/redo of every gesture and of a rename; the no-op rule; CQA-05 (mutation keeps the
staged creation, including with the form closed, and a session replacement resets it);
CQA-06 (every expected failure, plus the loud programmer error); CQA-07 (exact read
counts); save/reopen; the materialized record against the composed values; and the
four state defects the visual pass found.

`tests/unit/test_workbench_warp_transitions.py` - **32 passed**, unchanged except for
the CQA-07 counters, which now measure ONE project parse supplying both transition
documents (the previous run measured one parse of the edits document).

### Focused run, by named file

| file | result |
| --- | --- |
| `tests/unit/test_workbench_warp_creation.py` | 58 passed (76 at the frozen tip) |
| `tests/unit/test_workbench_warp_transitions.py` | 32 passed |
| `tests/unit/test_map_transition_create.py` | passed |
| `tests/unit/test_map_transition_project.py` | passed |
| `tests/unit/test_map_transitions.py` | passed |
| `tests/unit/test_workflow_migration.py` | 13 passed, 1 failed |
| `tests/unit/test_code_review_workflow.py` | passed except the same budget bound |
| `tests/unit/test_workbench_smoke.py` | passed |
| `tests/unit/test_workbench_state_and_errors.py` | passed |
| `tests/unit/test_workbench_map_tab.py` | passed |
| **total** | **345 passed, 2 failed** |

**On the isolated candidate all of this is resolved.** The unrelated paragraph is
absent, so both workflow-budget nodes **pass**
(`test_required_workflow_files_exist_and_are_bounded`,
`test_instruction_continuations_remain_within_established_bounds`), and
`git diff --check` is **clean, with no findings at all**. No file shows ending
churn: `git diff --numstat` and `git diff --ignore-cr-at-eol --numstat` agree
exactly for every changed file, and every line this pass added is bare LF.

### Isolated candidate validation

Over the corrected tip:

- `tests/unit/test_workbench_warp_creation.py` (76) and
  `tests/unit/test_workbench_warp_transitions.py` (32) - **108 passed**.
- Both workflow-budget nodes - **2 passed**.
- `tests/unit/test_workbench_smoke.py`, `test_workbench_state_and_errors.py`,
  `test_workbench_map_tab.py` - **55 passed** (57 with the two budget nodes).
- The full focused total at the frozen tip: **165 passed**.
- `git diff --check` - **clean**; `git diff --numstat`
  equals `git diff --ignore-cr-at-eol --numstat` for every file (no ending churn).
- The adversarial invariant sweep above - **0 findings**.

### ROM integration, one named file

`tests/integration/test_map_transition_create_rom.py` - **30 passed** (95 s), against
the real 8 MiB canonical image. It is the strongest bound on the SDK refactor: the
refactored template lookup, priors measurement and `set_transition_creations` are
exercised over the real corpus and the real build.

The candidate's production files are **byte-identical** to the versions that run
tested (`tools/webfoot/map_transitions.py` and, at that time,
`tools/webfoot/workbench/warp_tab.py`, verified by SHA-256), so the result
transfers. The worktree's later `warp_tab.py` corrections are GUI-only and are
covered by the focused files above; the ROM file was **not** re-run, and that is
recorded here rather than implied.

### Mutations, each observed and restored

| id | mutation | regression that failed |
| --- | --- | --- |
| M1 | a 169-class transition appears as a valid creation base | `test_only_566_class_transitions_are_offered_as_a_base` |
| M2 | duplicate authored identity is accepted | `test_a_duplicate_authored_identity_is_refused` |
| M3 | Apply writes to `transitions.toml` instead of `transition_creations.toml` | `test_apply_writes_only_the_creation_document` |
| M4 | a project mutation discards the staged creation | `test_a_project_mutation_keeps_a_staged_creation_whose_form_is_closed` |
| M4b | a project mutation rebuilds the creation surface from the project | `test_a_project_mutation_keeps_the_staged_creation` |
| M5 | the low nibble is replaced instead of preserved | `test_the_created_record_preserves_the_bases_low_nibble` |
| M6 | save/reopen loses the authored identity | `test_save_and_reopen_reproduces_the_created_transition` |

Each mutation was a local edit, observed failing, then restored **byte-for-byte**
(the harness asserts the restored hash before re-running the regression, which then
passed). No mutation framework was added.

### Visual QA

States **70-81** of `tools/qa/visual_pass_capture.py` (`warp_create_qa`), captured
from the real `MainWindow` against the canonical image and a real extracted project,
then **opened and inspected** over three rounds:

| state | subject |
| --- | --- |
| 70 | the Create form opened on a map with a usable base |
| 71 | the authored name and its identity preview |
| 72 | the `Based on` selection with the base's own description |
| 73 | region, destination, arrival and facing authored; the staged row appears |
| 74 | the created row selected, its form re-derived |
| 75 | after Apply: the row and the form both say New (saved) |
| 76 | after Revert: the staged row is gone with no project write |
| 77 | undo/redo of the revert |
| 78 | a duplicate name refused, with the name field still editable |
| 79 | a map with no 566-class base: the fail-closed explanation |
| 80 | a map on a shared connection root: the refusal, naming the other map |
| 81 | the narrow window (1100x720) with the form open and staged |

The capture found and fixed six defects:

1. after Apply the chip read **"Not staged"** while the row beside it read
   **"New (saved)"** - the staged/bound distinction is now read from the staged set;
2. a form whose name **collided** with a saved creation **locked the name field**,
   while its refusal told the author to author a different name;
3. a refused Create action stated its reason only in the one-line status bar, which
   elides it - the map bar beside the button, and the pane, now carry it;
4. **Revert was offered with nothing to revert** - it is now disabled unless a draft
   is staged or the form departs from what the project holds;
5. a fresh form kept the **stale created-row selection** highlighted, so the list
   named a row the form was not editing;
6. Revert's status line reported "back at the values the project holds" when a staged
   creation had in fact been discarded - it now says so, including that Undo restores it.

Post-fix captures were re-opened and inspected (`build/qa/warp-create-1` for the
first round, `-2` for the fixes, `-3` for the last two). The shell's 813x450 minimum
holds at 1100x720 with the form open; nothing clips. Captures are local, ignored QA
artifacts; nothing ROM-derived is committed.

## Final engineering corrections

**Seventh review, frozen candidate
`21f8473ff3e97fe3c5c1887bbdf3c0fcdf2f8259`: BLOCK, one blocking finding.** The
verification pass's probe reproduced the last member of the ownership family. A row whose
identity was BOTH staged and committed showed the author's STAGED values, and
`_open_creation_row` then set `owned` from the identity's presence in the committed
map. The form claimed the project's entry while editing something else, the
write-time exemption read that claim, and one Apply replaced the project's authored
creation with the stale staged values with no conflict shown. Both halves are one
rule: ownership must follow the SOURCE of the values on screen.

The review loop for this record then closed. `INDEPENDENT REVIEW: NOT
REPEATED`, for the reason recorded verbatim: *the record already underwent repeated
independent review rounds; later findings converged on permutations of the same
ownership-state family rather than new architectural areas; the final known failure
is now addressed by an explicit ownership invariant, exact order-sensitive
regression, write-time gate, and state-space sweep.*

### The final ownership correction

One correction commit, `1420754`, on top of the reviewed candidate:

* **Ownership follows the displayed value source.** `_open_creation_row` computes
  `shadowed = identity in self._staged_creations`; a shadowed row claims no ownership
  and passes `previous=None`, so the staged entry stays staged, the conflict is
  represented on the form, and the form is bound to nothing. A row whose source IS
  the project's own entry is unchanged, and still owns it.
* **The write-time gate stays authoritative.** `apply_creations` still re-reads the
  project's own document at the boundary and still refuses the whole batch on any
  conflict; the exemption it applies is now the corrected claim.
* **The sixth reset site.** A refused Create action clears `_open_creation_owned`
  with the binding it drops. All eight binding-clearing sites were audited and each
  pairs the two, as do the two derived writers (`apply_creations`,
  `_install_creation_state`).
* **An unreadable project document fails closed.** The boundary no longer falls back
  to the cached copy: it reports the normal user-visible refusal and writes nothing,
  because "this surface cannot read the project" must not mean "the project holds
  nothing".
* **The gate's comment is scoped to what it guarantees.** The overwrite protection
  covers creations the form does NOT legitimately own; an entry the form was given is
  re-authored by its author (last writer wins), which is the behaviour the fifth and
  sixth rounds fixed and this pass keeps.

### The invariant, redefined off the flag

The earlier sweep trusted `_open_creation_owned`, so a form that set the flag wrongly
passed it. Every invariant now measures **displayed-source truth** and none of them
reads the flag:

* **W1** a successful Apply writes exactly what the form DISPLAYED, and may replace an
  identity the document already held only when the form had been GIVEN that entry (a
  row opened whose source was the project's own entry, or this form's own earlier
  Apply), or the identity was not in the document at all;
* **W2** a refused Apply is a total no-op: document bytes, staged set, undo count,
  binding and ownership are exactly what they were, and the user was told;
* **W3** opening a row whose source is the staged set never claims ownership, and
  opening one whose source is the project's entry does;
* **W4** a created row shows the staged entry when one exists, else the project's;
* **W5** a closed form holds no binding and no ownership;
* **W6** no action other than a successful Apply changes the creation document bytes.

Matrix: source (staged-only / committed-only / staged and committed collision) x form
(open / closed) x row (clicked before the mutation / clicked after it / never) x
mutation (none / unrelated connection edit / the same identity introduced) x history
(none / undo / redo) x action (Apply / Revert / Cancel) = **486 cases**, plus ten
40-step random sequences, checked after every step. **Result: 2,528 checked states, 0
findings.**

### Pins and mutations at the final candidate

* `test_cqa06_a_shadowed_row_cannot_write_over_the_project_creation` is the exact
  order-sensitive regression: author, stage, CLOSE, the project gains the same
  identity with different values, broadcast, then click that row. It asserts the row
  still shows the staged values, `owned` is False, there is no binding, the conflict
  is stated on the form, Apply refuses and the document is byte-for-byte unchanged,
  the project's own arrival, destination and region survive, the staged creation is
  still present, and the session boundary is its exit.
* `test_an_unreadable_project_document_fails_closed_and_writes_nothing` pins the
  fail-closed read.
* `test_ownership_clears_when_the_binding_goes` gains the reset-site pin: with the
  form owning a saved creation, a refused Create action leaves neither binding nor
  ownership behind.

| id | mutation | regression that failed |
| --- | --- | --- |
| M9 | the pre-fix ownership rule restored (identity test plus `previous=identity`) | `test_cqa06_a_shadowed_row_cannot_write_over_the_project_creation` |
| M10 | an unreadable document falls back to the cached copy | `test_an_unreadable_project_document_fails_closed_and_writes_nothing` |
| M11 | the refused Create action leaves a stale owned flag | `test_ownership_clears_when_the_binding_goes` |

All three were **CAUGHT**, and `warp_tab.py` was restored **byte-for-byte**:
SHA-256 `504435d3986ff919a13c3ae2d863a9e05c3564a229380cf0ef5bf63b1ae3a6e8` before and
after, with no change left behind. One negative result is recorded rather than
hidden: reverting ONLY the `owned` half of the fix is not observable, because
`_install_creation_state` overwrites the flag from the resolved state. The defect
needs both halves, and the combined reversion above is caught.

### Focused validation at the final candidate

* `tests/unit/test_workbench_warp_creation.py` - **78 passed** (76 at the reviewed
  candidate, plus the two new pins; the reset-site pin extends an existing test).
* `tests/unit/test_workbench_warp_transitions.py` - **32 passed**.
* `tests/unit/test_workbench_smoke.py`, `test_workbench_state_and_errors.py` and
  `test_workbench_map_tab.py` - **55 passed**.
* Both workflow-budget nodes - **2 passed**.
* **Focused total: 167 passed**, superseding the 165 recorded above.
* The creation file was run **three further times** for the QUndo safety claim:
  **78 passed each time, with no heap corruption** (`0xc0000374`) in any run.
* `git diff --check` - **clean**; `git diff --numstat` equals
  `git diff --ignore-cr-at-eol --numstat` for both changed files, and every added
  line is bare LF.
* **Not run in this pass, stated rather than implied:** no broad suite, no ROM
  integration rerun (the correction changes `tools/webfoot/workbench/warp_tab.py`
  only, and this record touched `tools/webfoot/map_transitions.py`, the file that
  integration file exercises, in **one** commit - the implementation `5bae7e6`), no
  visual re-capture and no emulator run.

### Known limitation, recorded

A staged creation that the project has come to hold has **no in-surface removal
path**: a form that did not stage it may not discard it, so Revert restores the form
to the project's values without removing the entry. This is safe - it writes nothing,
loses nothing, and always refuses Apply with the reason stated - and its exit is the
**session boundary**: a project or image reload clears staged work, which the
regression above exercises directly. A per-row "discard this stale staged creation"
action would be new surface area, and adding surface area at closeout without review
is what this pass was told not to do.

### Closeout labels

* **FINAL OWNERSHIP FIX:** `1420754` - the single correction commit, production and
  tests, no amend.
* **FINAL CANDIDATE:** `88a83f1ec253a113e5306b881f626c09f652cfc8` - the branch tip
  that carries that correction and this record, and the tree every number above was
  measured on. The commit that adds these two labels is documentation only, on top
  of it.

## Not in this sub-pass

* **No emulator/runtime proof.** The parent still owes the human-operated run of a
  Workbench-authored transition; this sub-pass produced project, GUI and build
  evidence only. `RUNTIME NEW-TRANSITION PROOF: NOT YET DONE`.
* **No transition deletion**, canonical or created: Revert discards a staged creation
  or restores a saved one's values, and never removes a project entry.
* **No capability advance.** 20 / 24 happens only when the parent ships.
* **No registry or public-site change**, and no `docs/PROJECT_<local-state-name>` update.
* **The shell's unsaved-work guard is unchanged**, for the same reason
  `MAP-WARP-WORKBENCH-001` recorded: a staged transition is project-bound like an
  unapplied palette value, and the surface states its own staged count.
