# MAP-WARP-CREATE-WORKBENCH-001 - the Warps surface's Create Transition action

STATUS: **CLOSED (2026-09-27).** Class:
GUI and project-surface pass. This is a **sub-pass of the parent capability
`MAP-WARPS-AND-CONNECTIONS-001`**, which ships as of the parent's closeout
(2026-09-28); archived at closure in
[`archive/MAP-WARP-CREATE-WORKBENCH-001.md`](archive/MAP-WARP-CREATE-WORKBENCH-001.md),
which carries the multi-round review history and the final ownership closeout.
Nothing here shipped the parent: the capability count was unchanged and the registry
was untouched.

Baseline: `87a47ff721896a1d99632e78ff7cf6032cf9f8ae` (the commit that recorded
`MAP-WARP-CREATE-PROJECT-001` as merged; verified with `git fetch origin --prune`
and `git rev-parse origin/master` at isolation time). **No drift:** origin/master,
the primary checkout's HEAD and the ticket baseline were all that one commit.

Worktree: `<ticket-worktrees>\map-warp-create-workbench-001` on
`ticket/map-warp-create-workbench-001`, created from the clean baseline. The work
was first implemented in the primary checkout, which was **dirty with an unrelated
uncommitted `docs/DEVELOPMENT.md` change** (an 8-line permanent-rule paragraph belonging to
other work). That paragraph was **not** carried into this ticket: the primary
checkout was left untouched as source material, and only this ticket's own hunks
were transplanted. The primary checkout is still dirty with it, by design.

Implementation: **committed** on the ticket branch. This document is committed at
the frozen candidate below; the earlier status of this record, which described an
uncommitted implementation and the primary checkout's pre-isolation test totals, is
superseded.

**public progress impact: NONE.** No capability ships: the `warps` capability is
still `missing`, `src/data/capabilities.json` and the public site are untouched,
`EDIT` stays **7 / 8**, DragonByte Z stays **19 / 24 - 79%**, and
`docs/PROJECT_<local-state-name>` is deliberately not touched because the parent has not
shipped.

Scope boundaries honoured: **no emulator run**, **no capability-count change**,
**no registry or site change**, **no GUI ROM write**, **no new serializer**, **no
new transition-format research**, **no direct pointer/count manipulation in Qt
code**, and **no transition deletion**. Every write goes through
`map_transitions.set_transition_creations` and the production build.

---

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

That run was taken in the **primary checkout**, whose `docs/DEVELOPMENT.md` carries the
unrelated **+8 uncommitted lines** described above. Both failures were the
`docs/DEVELOPMENT.md <= 300` budget, caused by those 8 lines and not by this pass: this pass's
own docs/DEVELOPMENT.md change is a **21-for-21 line replacement** inside the Full-Suite
Policy section. `git diff --check` there reported only the eight lines of that
paragraph.

**On the isolated candidate all of this is resolved.** The unrelated paragraph is
absent, so `docs/DEVELOPMENT.md` is **300 lines** and both budget nodes **pass**
(`test_required_workflow_files_exist_and_are_bounded`,
`test_instruction_continuations_remain_within_established_bounds`), and
`git diff --check` is **clean, with no findings at all**. No file shows ending
churn: `git diff --numstat` and `git diff --ignore-cr-at-eol --numstat` agree
exactly for every changed file, and every line this pass added is bare LF per
[`../line-endings.md`](../line-endings.md).

### Isolated candidate validation

In the clean ticket worktree, over the corrected tip:

- `tests/unit/test_workbench_warp_creation.py` (76) and
  `tests/unit/test_workbench_warp_transitions.py` (32) - **108 passed**.
- Both workflow-budget nodes - **2 passed**.
- `tests/unit/test_workbench_smoke.py`, `test_workbench_state_and_errors.py`,
  `test_workbench_map_tab.py` - **55 passed** (57 with the two budget nodes).
- The full focused total at the frozen tip: **165 passed**.
- `git diff --check` - **clean**; `docs/DEVELOPMENT.md` **300** lines; `git diff --numstat`
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

## Independent review

`the local reviewer`, the instrument the previous sub-passes used, **could not run in this
environment**: the harness's local launch planned a `the reviewer --cloud` invocation and
its job (`cl-20260927-054453-0068e4`) failed with no session, cloud-session attach
is not enabled for this account, and a direct local headless run of the installed
CLI (2.1.280) returned `Failed to authenticate: OAuth session expired and could not
be refreshed`. The review was therefore performed by the harness's **fresh-context
reviewer** (a separate agent with no implementer context), which is what the gate in
[`../../docs/DEVELOPMENT.md`](../../docs/DEVELOPMENT.md) requires of any instrument. A the reviewer verdict
remains available to the owner by re-authenticating the CLI.

**First review, frozen candidate `7d5e4a950ba19f4c3a4c723c3d65e79a56d2cec4`:
APPROVE WITH NON-BLOCKING NOTES, zero blocking findings.** It confirmed all 22
required judgements by reading the whole of `warp_tab.py` and the authority, and
reproduced the focused counts (90 passed), both budget nodes and the clean
`--diff --check` itself. It also confirmed `test_cqa06_a_programmer_error_in_a_slot_is_loud`
does pin the undo correction, having verified by experiment that a raising
`redo()` leaves the command on the stack (count 1) - which is what the regression's
`undo_stack().count() == 0` assertion discriminates.

Six non-blocking notes were raised. Three were corrected in the candidate the
reviewer reviewed plus one correction commit, and three are recorded as accepted:

| # | note | disposition |
| --- | --- | --- |
| 1 | `_retail` called the corpus unguarded, a latent raise on the path `undo()`/`redo()` reach through `_install_creation_state` | **CORRECTED** - the call is guarded, so nothing on that path can raise; pinned by `test_a_retail_read_of_an_identity_the_corpus_lacks_is_state_not_an_exception` |
| 2 | undo after a source-map change reinstated a creation form for a different map | **CORRECTED** - an install that belongs to another source map no longer reinstates the draft; pinned by `test_undo_after_a_source_map_change_does_not_reopen_the_form` |
| 3 | with a saved creation open and its draft refused, the chip reads "Not staged" while the row reads "New (saved)" | accepted: wording, not correctness - the row describes the project and the reason line states the refusal |
| 4 | `close_creation` left the created row highlighted while the pane said nothing was selected | **CORRECTED** - the current item and the selection are both cleared, so the highlight does not outlive the pane; pinned by `test_closing_the_form_leaves_no_row_highlighted` |
| 5 | this record described the primary checkout's uncommitted state and its pre-isolation totals | **CORRECTED** - this document |
| 6 | the docs/DEVELOPMENT.md hunk narrowed the full-suite trigger list and dropped two triggers | **CORRECTED** - the enumerated triggers ("VM assembler/decoder", "build/extract", "transaction logic", "dependencies", a fix affecting unrelated systems, a prior failure signalling broader risk) are restored, with the speed rule condensed so the file stays at 300 lines |

The correction is a **production change**, so per the ticket's own rule the corrected
tip is a **new frozen candidate** and takes a **fresh review**; that verdict is
recorded below with its commit. No reviewed commit was amended.

**Second review, frozen candidate `9b90659489b2339f4cb09fdd1db7717c5e1060a0`:
BLOCK, one blocking finding - and it was right.** Correcting note 2 introduced a
worse defect than the one it fixed: `_install_creation_state` dropped a draft that
belonged to another source map but kept its binding, so the next project mutation
ran `_reapply_creation` with `bound` set and `draft` None, popped that binding's
staged entry, and **silently discarded the author's staged creation** - no message,
no undo entry, reachable by Ctrl+Z after a map-bar change followed by any Apply or
Save As elsewhere. The existing pin covered the form-closed path (`close_creation`
clears the binding) and therefore missed it.

Corrected at both root causes, in `8cad1e4a2ab705b6cf462cdfe5bd59fe40333505`:

* `_resolve_creation_state` no longer drops the binding's entry when it is handed no
  draft: a None draft states nothing about the staged set, so it changes nothing, and
  the drop happens only for a draft that is actually being replaced;
* `_install_creation_state` drops the binding together with a draft it refuses to
  reinstate, so "no form, but bound to an identity" is no longer a state the surface
  can hold.

The regression that should have caught it - undo after a source-map change - now
continues through the transitions that follow it: the staged creation must survive
an unrelated project mutation, a redo, and a change back to its own map, and must
still be applicable there. Three further notes from that review were also acted on:
the `close_creation` suppression is confirmed non-stranding, the docs/DEVELOPMENT.md wording
drifts were restored (the measured/derived restriction "allowed only where trivial
arithmetic permits", the "iterative debugging loop" and the trigger phrases), and
`docs/PROJECT_<local-state-name>` was corrected from "uncommitted" to the branch commits.

The reviewer also stated plainly what its retail pin does and does not prove: it
drives `_retail`/`_base`/`_effective` directly, so it pins the guard rather than a
UI path to it, and a `CreatedTransitionIdentity` never reaches `_retail` through the
widgets. That is recorded as the pin's actual scope.

**Third review, frozen candidate `150970d9d569c04d829a59fca3a3ef32d376790c`:
BLOCK, one blocking finding - also right.** `_reapply_creation` inferred the form's
binding from the draft's own identity when none was recorded. That made a form the
surface had just REFUSED into the owner of the identity it was refused for, so a
project mutation would either stage the refused duplicate (enabling Apply to
overwrite the project's saved creation) or pop another draft's staged entry for the
same name and replace it with the refused form's values. Corrected in
`eb81fc2eda8bbe06b4a6e42c1599634535e543af`: the binding is only ever the recorded
one, recorded where the form learns it - a staging gesture, a saved row opened into
it, its own Apply - and `_staged_creation_key()` is the single answer to "is this
form's creation staged", read from the staged set.

**Fourth review, frozen candidate `eb81fc2eda8bbe06b4a6e42c1599634535e543af`:
BLOCK, one blocking finding - right again, and the same family one step earlier.**
The authority-REFUSAL branch also recorded a binding, which is not a place a form
learns one. A refused form therefore owned an identity it did not stage, so once the
project came to create that name (a peer Apply, a Save As, a project opened over the
session) the next ordinary gesture skipped the saved-identity conflict gate and
staged an overwrite that Apply then wrote - with no conflict shown. Corrected in
`ed8b1d412dde152fa69c947b7a7341a77e8400d4` by stating the rule at its root: a
binding is recorded only when the form stages its own creation, and a refusal can
only KEEP a binding the form already had. The form now reports its binding through
`creation_form_state()` so provenance is checkable, not just its effects.

That review also found two docs/DEVELOPMENT.md lines whose text this pass never changed but
whose line ending it had rewritten; they are back to the baseline ending, checked by
requiring `git diff --numstat` and `git diff --ignore-cr-at-eol --numstat` to agree
for every file, and it found `selected_editable()` claiming the connections pane
could edit a created row that only the creation form edits.

**The state machine was then swept adversarially by the implementer**, before
spending a fifth review: 12 seeds x 60 random operations plus four targeted
scenarios, checking after every step that (I2) every staged creation is one the
authority accepts, (I3) the binding names only something the form owns, (I4) the
chip, the staged flag, Apply and the list row agree, and (I5) a mutation never
replaces another draft's entry. It found one real defect the reviews had not: a
CLOSED form kept its last chip text, so it reported `New (staged)` with an empty
staged set. Corrected in `dae9b0feea32f4d125df69008f50303b423b9fbc` - the chip is
written whether or not a form is open - with the sweep then clean at 0 findings over
the same run. Two mutations pin the rule that produced the third and fourth
findings: reintroducing the inference, and reintroducing the refusal-recorded
binding, each make the named regressions fail.

Four review rounds produced four blocking findings, all in one family - who owns a
durable identity, and when a form learns that it does - and each is now both fixed
and pinned at the place the state is created rather than where the symptom appeared.

**Fifth review, frozen candidate `630c716d4bb694dfcfe2dc8de0e1921aa4453ca2`:
BLOCK, one blocking finding - the same family once more, and the first half of the
gate rather than the second.** The saved-identity gate asked only whether the form
was bound to the identity, so a binding learned by merely STAGING a new creation
counted as ownership: once the project came to create that name (a peer Apply, a
Save As, a project opened over the session), one ordinary gesture staged the form's
values as an update and Apply wrote them over the project's authored creation with
no conflict shown. Corrected in `4ab17f73ff391ecbcc3b947582a174affc895bc9` by
requiring both halves of the claim: the binding must be this identity AND it must
have come from the project's own entry. `CreationState` carries that provenance as
`owned`, set only where the form is GIVEN the project's entry - a saved creation
opened into the form from its row, and this form's own Apply - and carried through
undo/redo with the rest of the state; a staging gesture binds the form to its own
creation without claiming the project's entry.

**Review rounds stopped at five, deliberately.** Five rounds found five defects and
each round cost more than the last while the findings shrank to one narrow gate
condition; the fifth correction is pinned in both directions and the invariant sweep
is clean, so a sixth round was not proportionate. The frozen tip therefore carries
one **not yet independently reviewed** commit (`4ab17f7`); its the reviewer-channel review
is available to the owner by re-authenticating the CLI.

**Sixth review, frozen candidate `2657120fc77fea3771485158e6c6249928e86f03`:
BLOCK, two blocking findings - and both were real authored-data loss.** The
ownership rule was stated in one place (`_resolve_creation_state`, i.e. only for an
OPEN form) and the round before had left two holes in it:

1. **A staged row click claimed the project's entry.** `_open_creation_row` set
   `owned` unconditionally, so clicking the row of the author's own STAGED creation
   made the form the owner of an identity it did not own - one Apply later the
   project's authored creation was overwritten with no conflict shown.
2. **The gate was not at the write.** Three routes reached `apply_creations` with
   stale staged state: the form was closed, the form had never been given the entry,
   or undo reinstated a captured staged state. Each ended in the same silent
   overwrite.

Both are corrected in `4d6fceefe0636db29b8e71ec7907d7e2ffb80070`:

* ownership follows the **SOURCE** of the values, not the click - a row owns its
  entry only when `identity in self._committed_creations`;
* the rule is enforced **at the write boundary** in `apply_creations`, which every
  write crosses, reading the project's own document rather than trusting the last
  broadcast (so a second instance, a hand edit or a CLI write cannot be overwritten
  either);
* a conflicting batch is refused **atomically**: nothing written, nothing partially
  written, nothing silently adopted, and the conflict is stated through the normal
  refused-Apply surface;
* a legitimate owned edit - a committed creation opened from its own row, or one this
  form applied - still writes, which is pinned;
* `_open_creation_owned` is cleared wherever its binding is dropped, and the form
  reports it through `creation_form_state()`.

**The ownership matrix was then swept deliberately, not one case at a time:** 1,372
checked states over source state (none / staged / committed) x form (open / closed) x
row (clicked / never) x project mutation (none / unrelated / same identity introduced)
x history (none / undo / redo) x action (Apply / Revert / Cancel), plus ten random
40-step sequences, checking after every step that (I1) no staged creation overwrites
a project creation that appeared after staging unless the editor has an explicit
legitimate owned binding, and (I2) no refusal or conflict path writes project data.
I1 and I2 hold in every state. The nine states where Apply does change a held value
are the intended owned re-authoring - verified directly: the editor owns the entry,
`_creation_conflicts()` is empty, and its own value is written.

## Final engineering closeout

**Seventh review, frozen candidate
`21f8473ff3e97fe3c5c1887bbdf3c0fcdf2f8259`: BLOCK, one blocking finding.** The
reviewer's probe reproduced the last member of the ownership family. A row whose
identity was BOTH staged and committed showed the author's STAGED values, and
`_open_creation_row` then set `owned` from the identity's presence in the committed
map. The form claimed the project's entry while editing something else, the
write-time exemption read that claim, and one Apply replaced the project's authored
creation with the stale staged values with no conflict shown. Both halves are one
rule: ownership must follow the SOURCE of the values on screen.

The owner then closed the review loop for this ticket. `INDEPENDENT REVIEW: NOT
REPEATED`, for the reason recorded verbatim: *the ticket already underwent repeated
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
  only, and this ticket touched `tools/webfoot/map_transitions.py`, the file that
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
