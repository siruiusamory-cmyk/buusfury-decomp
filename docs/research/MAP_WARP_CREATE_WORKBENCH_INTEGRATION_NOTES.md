# The Warps surface Create Transition action: integration notes

The condensed record of the Create Transition pass: what shipped, the ownership
family it converged on, and the limits kept.

## Scope

Advance the GUI half of the parent's Required Work 1 and 3 for creation: let the
shipped `Maps -> Warps` surface author a transition the image does not contain -
durable name, same-map 566-class base, positional trigger region, semantic
destination, required (never derived) arrival and facing - stage it, and write it
through the existing creation authority. No second serializer, no format research,
no pointer or count arithmetic in Qt.

## What shipped

Baseline `87a47ff721896a1d99632e78ff7cf6032cf9f8ae`, implemented and isolated in
`<records>\map-warp-create-workbench-001` on
`record/map-warp-create-workbench-001` (origin/master, the primary checkout HEAD and
the record baseline were the same commit, no drift).

* A **Create Transition** action opens a form that authors the durable name, the
  same-map 566-class template, the positional trigger region, the destination, the
  never-derived arrival and the facing; the row appears immediately as
  `New (staged)`, and Apply writes one `set_transition_creations` call into
  `maps/transition_creations.toml`.
* A 169-class base, a map with no 566-class record, a shared connection root and a
  duplicate identity are all refused with the authority's own words; Apply and
  Revert write nothing for a no-op form.
* The two SDK additions are facades over existing authority -
  `check_transition_creation` and `creation_templates`, with
  `set_transition_creations` now sharing one priors measurement.
* **A real defect this pass found and fixed in its own first cut:** a Python
  exception escaping `QUndoCommand::redo` corrupted the heap on this machine
  (`Windows fatal exception: code c0000374`). Every creation gesture now resolves
  both of its states before the command is pushed, and
  `test_cqa06_a_programmer_error_in_a_slot_is_loud` pins that.

Merged into `master` as `5224c7376660c5e35f2063e9e59699911a1a4750`.

## The ownership family the verification converged on

The independent verification was performed by a independent verification pass with no
part in the implementation, which is what the repository's review gate requires.

The review history is preserved because it is the sub-pass's real record:

| round | frozen candidate | verdict | resolution |
| --- | --- | --- | --- |
| 1 | `7d5e4a9` | APPROVE WITH NON-BLOCKING NOTES, 0 blocking, six notes | five corrected (guarded `_retail`, undo across a source-map change, row highlight on close, this record's stale totals, restored the repository rules triggers); one wording note accepted |
| 2 | `9b90659` | BLOCK, one finding | correcting round 1 had introduced a silent discard of a staged creation; fixed at both root causes in `8cad1e4` |
| 3 | `150970d` | BLOCK, one finding | a refused form became the owner of the identity it was refused for; fixed in `eb81fc2` |
| 4 | `eb81fc2` | BLOCK, one finding | the authority-refusal branch also recorded a binding; fixed in `ed8b1d4` |
| 5 | `630c716` | BLOCK, one finding | a binding learned by staging counted as ownership; fixed in `4ab17f7` |
| 6 | `2657120` | BLOCK, two findings | a staged row click claimed the project's entry, and the gate was not at the write; fixed in `4d6fcee` |
| 7 | `21f8473` | BLOCK, one finding | a row both staged and committed showed the staged values and claimed the project's entry; fixed in `1420754` |

Every blocking finding was one family - who owns a durable identity, and when a form
learns that it does - and each was fixed and pinned where the state is created rather
than where the symptom appeared. An adversarial state-machine sweep by the
author between rounds 4 and 5 found one further defect (a closed form reporting
`New (staged)` with an empty staged set), corrected in `dae9b0f`.

**Rounds stopped at five, then resumed, and the loop was closed.** After round
five the record states that a sixth round was not proportionate at that point and
that the frozen tip carried one not-yet-reviewed commit; rounds six and seven
followed, and after the round-seven correction the review loop closed with
`INDEPENDENT REVIEW: NOT REPEATED`, recorded verbatim: the record already underwent
repeated independent review rounds; later findings converged on permutations of the
same ownership-state family rather than new architectural areas; and the final known
failure is addressed by an explicit ownership invariant, an exact order-sensitive
regression, a write-time gate and a state-space sweep.

## Final ownership correction

One correction commit, `1420754`, on top of the reviewed candidate; final candidate
`88a83f1ec253a113e5306b881f626c09f652cfc8`, which carries the correction and this
record.

* **Ownership follows the displayed value source.** A row whose identity is also in
  the staged set claims no ownership, keeps its staged entry staged and binds the
  form to nothing; a row whose source is the project's own entry still owns it.
* **The write-time gate stays authoritative.** `apply_creations` re-reads the
  project's own document at the boundary and refuses the whole batch atomically on
  any conflict - nothing written, nothing partially written, nothing silently
  adopted.
* **An unreadable project document fails closed**, with the normal user-visible
  refusal, rather than falling back to a cached copy.
* **All eight binding-clearing sites** were audited to clear ownership with the
  binding, including a refused Create action.
* The invariant was redefined off the flag: every check now measures displayed-source
  truth and none reads `_open_creation_owned`. The matrix (source x form x row x
  mutation x history x action) covers 486 cases plus ten 40-step random sequences:
  **2,528 checked states, 0 findings.**
* Mutations **M9-M11** were each caught and `warp_tab.py` restored byte-for-byte
  (SHA-256 `504435d3...a6e8`). One negative result is recorded rather than hidden:
  reverting only the `owned` half of the fix is not observable, because
  `_install_creation_state` overwrites the flag from the resolved state; the defect
  needs both halves.

## Limitations preserved

* **A shadowed stale staged creation has no per-row discard action.** A form that did
  not stage it may not discard it, so Revert restores the form to the project's
  values without removing the entry. This is safe - it writes nothing, loses nothing
  and always refuses Apply with the reason stated - and its exit is the **session
  boundary**: a project or image reload clears staged work. A per-row discard action
  would be new surface area, and adding surface area at closeout without review was
  out of scope.
* **No emulator/runtime proof at this pass.** The human-operated run of a created
  transition was supplied later by `MAP-WARP-CREATE-RUNTIME-001`.
* **No transition deletion**, canonical or created.
* **The shell's unsaved-work guard is unchanged**, for the same reason
  `MAP-WARP-WORKBENCH-001` recorded.

## Validation

* Focused named files: `tests/unit/test_workbench_warp_creation.py` **78 passed**,
  `test_workbench_warp_transitions.py` **32 passed**, `test_workbench_smoke.py` +
  `test_workbench_state_and_errors.py` + `test_workbench_map_tab.py` **55 passed**,
  both workflow-budget nodes **2 passed**; **focused total 167 passed**. The creation
  file was run three further times with **no heap corruption** in any run.
* `git diff --check` clean; `git diff --numstat` equals
  `git diff --ignore-cr-at-eol --numstat` for both changed files, and every added
  line is bare LF.
* **Test-policy record, stated rather than implied:** no broad suite, no ROM
  integration rerun (the correction changes only `tools/webfoot/workbench/warp_tab.py`),
  no visual re-capture and no emulator run in the final correction pass.

## Stop

Stopped after the ownership correction and the closure of the review loop.
The runtime proof of a created transition and the capability advance to **20 / 24**
remained; `MAP-WARP-CREATE-RUNTIME-001` followed, and the parent's own closeout
states the final result.
