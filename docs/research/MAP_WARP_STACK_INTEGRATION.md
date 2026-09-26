# MAP-WARP-STACK-REVIEW-AND-INTEGRATE-001 - integrate the map-warp sub-stack

STATUS: **CLOSED AND MERGED (2026-09-26).** A scoped integration sub-pass of the
still-active `MAP-WARPS-AND-CONNECTIONS-001`. It added **no capability**, created
**no transition**, added **no Workbench surface**, and changed **no capability
count**.

## What it was asked to do

1. clean the `docs/DEVELOPMENT.md` diff so it carried only the runtime-rule text, with no
   line-ending churn;
2. freeze the cumulative candidate;
3. obtain a fresh-context independent review;
4. push to MR !89;
5. run CI on the final head;
6. merge if green;
7. verify `master` clean and current.

## Baseline, candidate and merge

| Item | SHA |
| --- | --- |
| baseline | `05870f1e9c90fc5ef83ddfd1fa69fdedb06f926a` |
| reviewed candidate | `4cada7b9ea3f3ce585635fc80bd52462e00e2d88` |
| final frozen candidate | `65b4b24a41f2ea70fe0d93fbb2a10e7c28cf5d76` |
| merge on `master` | `d4baa1448ca63fa575141933edc2acb3d27ef541` |

The source branch was removed on merge. MR: !89.

## The CI failure was real, and it was the line bound

The reviewed candidate differed from its baseline by one edit to `docs/DEVELOPMENT.md`
carrying the transition-proof rule. CI pipeline `2885273922` failed on
`test_instruction_continuations_remain_within_established_bounds` and
`test_required_workflow_files_exist_and_are_bounded`, because the edit took that
file from **300 lines to 308** against a 300-line budget.

The bound is not incidental. `docs/README.md` and both rule files state that
a new permanent rule earns its place by being condensed to fit rather than by moving
the bound, and `docs/DEVELOPMENT.md` is bounded at 240 as well, so neither file could absorb
the rule. It now lives in [`../runtime-capture.md`](../runtime-capture.md), the
authoritative runtime procedure both files already point at, and `docs/DEVELOPMENT.md` and
`docs/DEVELOPMENT.md` are restored **byte-for-byte** to their committed state. The
cumulative diff no longer touches either file.

The pointer sweep that followed corrected three places that would have sent a reader
to a rule that is no longer there - the parent ticket's live and parked copies, and
the facing ticket's archived file table - and the parent ticket's context delta,
which stated the leave-and-re-enter requirement unconditionally, is now scoped to
map and background assembly, which is the correction the runtime sub-pass actually
made.

## A committed line-ending normalisation was removed

An earlier commit on the branch had normalised `tests/unit/test_mgba_capture.py` and
`tools/runtime/inject_mgba_lua.ps1` to bare LF "so the added lines carry no CR". Both
files are among the nine that [`../line-endings.md`](../line-endings.md) records as
deliberately mixed on `origin/master`, and the normalisation rewrote **1069** and
**481** lines it had not otherwise changed.

That document is explicit that this is the wrong remedy - added lines are written
with a bare LF and **no existing line's ending is touched** - and that a repo-wide
normalisation "must never be committed inside a feature or ticket branch: it destroys
reviewability and buries the real change."

master's exact bytes were restored and only the genuinely added lines re-applied with
bare LF. Measured against the previous head with line endings ignored, the staged
content is **byte-identical**, so nothing under review moved; measured against
master, the diff for those two files fell from **2253 and 969** changed lines to the
**115 and 7** lines actually added. Across the whole stack the cumulative diff went
from 7758 insertions / 1573 deletions to **6208 insertions / 23 deletions**.

## Review and why the full gate was not re-run

The independent review of `4cada7b` - `the local reviewer`, headless, fresh context -
returned **`APPROVE WITH NON-BLOCKING NOTES`** with zero blocking findings. One
review finding was fixed before that verdict: `arrival` had no class check, so all
169 class-B records passed a bounds check that would have written a relative delta as
an absolute position.

The three commits after `4cada7b` are documentation-only plus the ending restoration,
whose staged content is byte-identical to `4cada7b` with line endings ignored.
`docs/DEVELOPMENT.md` permits a trivial, non-behavioural change to take a proportionate
lighter path provided the closure record says why. That is the basis here: the code
under review did not change, so no second full gate was warranted, and this record
does not claim one was run. A cloud review was not used because this account cannot
attach to an existing cloud session, so a cloud verdict would not have been readable
locally.

## Follow-ups: the five non-blocking notes

Recorded rather than fixed, because the implementation had already frozen. Note 1 is
the one with a real usability consequence.

1. `set_arrival` refuses even `arrival=None` on a 169-class record, which makes the
   `retarget` convenience path unusable for that class.
2. `MapTransitions.arrival` does not document the class refusal in its docstring.
3. The prior check runs before the class refusal, so a 169 edit is reported as a
   prior mismatch rather than as an unsupported form.
4. Destination and region edits remain permitted on a 169-class record.
5. An observer comment contradicts the recorded position that what `0x03001A34`
   selects is `UNRESOLVED`.

Also outstanding and unchanged from the parent ticket's record: the non-zero gate
case is **UNTESTED**, low-nibble semantics are **UNRESOLVED**, a low nibble of 4 or
more in a 169-class record indexes past the four-byte table, and the caller of
`vtbl+0x04`, the meaning of `*(u16*)0x03003302` bits 7..4 and of `0x03001A34` remain
untraced.

## Public progress

`public progress impact: NONE` - nothing a visitor can do changes: `src/` is
untouched, the registry stays at **19 / 24 (79%)**, `EDIT` stays **7 / 8**, `warps`
remains missing, and the parent capability remains ACTIVE and unshipped. No cosmetic
site edit was made.

## Validation

Focused named files only: `tests/unit/test_mgba_capture.py` **77 passed** (it reads
the injector as text and pins its allowlist and read-only guarantees), the two
line-bound tests plus the doc gates **22 passed**, and a clean `git diff --check` on
the staged restoration. CI on the final head, pipeline `2885281081`, **succeeded**;
the two preceding pipelines on earlier heads also succeeded once the line-bound
failure was fixed.

The full suite was run once earlier in the stack in error against the
evidence-proportional policy and is not repeated here; the blast radius of this
pass - documentation, and two files whose staged content is provably unchanged - is
bounded by the focused gates above.

## Safety

No ROM, save, state or proprietary artifact appears anywhere in the cumulative diff.
The canonical ROM was re-hashed after the merge and is unchanged at
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`. The working
tree was clean before the merge, and `master` was untouched at `05870f1` until the
merge landed.

## Stop

Stopped after the merge and after verifying `master`. The parent ticket's Required
Work 3 (the Workbench transition surface) and 4, and the capability advance to
**20 / 24**, remain untouched and to do. No Workbench work and no new transition
creation was begun.
