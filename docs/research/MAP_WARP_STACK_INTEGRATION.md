# Integrating the map-warp sub-stack

The integration pass over the map-warp sub-stack: the candidate and merge, the real
integration failure and its cause, the line-ending normalisation and the follow-up
items.

## Scope

1. clean the the repository rules diff so it carried only the runtime-rule text, with no
   line-ending churn;
2. freeze the cumulative candidate;
3. obtain a independent independent review;
4. push to MR !89;
5. run CI on the final head;
6. merge if green;
7. verify `master` clean and current.

## Baseline and candidate

| Item | SHA |
| --- | --- |
| baseline | `7800412dd9dfa8798d32fb1d9d23531f3e86d8c0` |
| reviewed candidate | `5867a96580f598ab7184774120fc7e714e97b77b` |
| final frozen candidate | `e1b5367024e99ca88bd96a46372d41cb84a1ff24` |
| merge on `master` | `197c6671ea121af2849d9de5f751b2ef61641ddd` |

The source branch was removed on merge. MR: !89.

## The integration failure and its cause

The reviewed candidate differed from its baseline by one edit to the repository rules
carrying the transition-proof rule. CI pipeline `2885273922` failed on
`test_instruction_continuations_remain_within_established_bounds` and
`test_required_workflow_files_exist_and_are_bounded`, because the edit took that
file from **300 lines to 308** beyond the documented bound.

The bound is not incidental. The repository rule files state that
a new permanent rule earns its place by being condensed to fit rather than by moving
the bound, and the repository rules is bounded at 240 as well, so neither file could absorb
the rule. It now lives in [`../runtime-capture.md`](../runtime-capture.md), the
authoritative runtime procedure both files already point at, and the repository rules and
the repository rules are restored **byte-for-byte** to their committed state. The
cumulative diff no longer touches either file.

The pointer sweep that followed corrected three places that would have sent a reader
to a rule that is no longer there - the parent record's live and parked copies, and
the facing record's archived file table - and the parent record's context delta,
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
normalisation "must never be committed inside a feature or record branch: it destroys
reviewability and buries the real change."

master's exact bytes were restored and only the genuinely added lines re-applied with
bare LF. Measured against the previous head with line endings ignored, the staged
content is **byte-identical**, so nothing under review moved; measured against
master, the diff for those two files fell from **2253 and 969** changed lines to the
**115 and 7** lines actually added. Across the whole stack the cumulative diff went
from 7758 insertions / 1573 deletions to **6208 insertions / 23 deletions**.

## Verification and gate scope

The independent review of `5867a96580f598ab7184774120fc7e714e97b77b` - an independent local review, headless, independent context -
returned **`APPROVE WITH NON-BLOCKING NOTES`** with zero blocking findings. One
review finding was fixed before that verdict: `arrival` had no class check, so all
169 class-B records passed a bounds check that would have written a relative delta as
an absolute position.

The three commits after `5867a96580f598ab7184774120fc7e714e97b77b` are documentation-only plus the ending restoration,
whose staged content is byte-identical to `5867a96580f598ab7184774120fc7e714e97b77b` with line endings ignored.
the repository rules permits a trivial, non-behavioural change to take a proportionate
lighter path provided the closure record says why. That is the basis here: the code
under review did not change, so no second full gate was warranted, and this record
does not claim one was run. A cloud review was not used because this account cannot
attach to an existing cloud session, so a cloud verdict would not have been readable
locally.

## Follow-up items

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

Also outstanding and unchanged from the parent record's record: the non-zero gate
case is **UNTESTED**, low-nibble semantics are **UNRESOLVED**, a low nibble of 4 or
more in a 169-class record indexes past the four-byte table, and the caller of
`vtbl+0x04`, the meaning of `*(u16*)0x03003302` bits 7..4 and of `0x03001A34` remain
untraced.

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
