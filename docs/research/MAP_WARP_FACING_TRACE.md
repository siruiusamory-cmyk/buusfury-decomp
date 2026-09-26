# MAP-WARP-FACING-TRACE-001 - instrumented arrival-facing proof

STATUS: **CLOSED (2026-09-26).** Scoped **sub-ticket of
`MAP-WARPS-AND-CONNECTIONS-001`**, which remains **ACTIVE / NOT SHIPPED** in
[`../PROJECT_<local-state-name>`](../PROJECT_<local-state-name>). Independent code review of this sub-ticket's
code has **not** been run; it is a read-only observer, a collector and a
documentation correction, and the parent capability still owns the review gate at
its own closure.

`public progress impact: NONE` - no capability ships, the registry stays at
**19 / 24 (79%)**, `EDIT` stays **7 / 8**, and no site source changed.

## Goal

Turn a human-reported facing result into instrumented evidence, and settle whether
the traced `0x03001A34` selector suppressed the engine's arrival-facing write.

## What was added

| File | Change |
| --- | --- |
| `tools/runtime/warpedit001_transition_watch.lua` | a passive facing channel in its own `facing.csv`, so the `session.csv` contract the finisher parses is untouched |
| `tools/runtime/finish_warpedit001_session.ps1` | reports the facing correlation; a first revision selected the pre-warp player-object swap and was corrected to select the first swap outside the source map |
| `tests/unit/test_mgba_capture.py` | pins the new channel's addresses, its separate output file, and that its player slot is never dereferenced blind |
| `docs/research/LOGX_CONNECTOR_PROVENANCE.md` | correction 6: `+0x10 = 0x02` does **not** mean "face West"; plus the runtime confirmation and the transition-proof rule |
| `docs/DEVELOPMENT.md` | the transition-proof rule, in the runtime-evidence section - **later relocated**: see the note below |

The `docs/DEVELOPMENT.md` edit above did not survive `MAP-WARP-STACK-REVIEW-AND-INTEGRATE-001`.
It took that file to 308 lines against the 300-line budget that
`test_workflow_migration.py` and `test_code_review_workflow.py` both enforce, so CI
failed on the candidate. `docs/DEVELOPMENT.md` and `docs/DEVELOPMENT.md` are bounded context budgets
and each says a new rule earns its place by being condensed to fit rather than by
moving the bound, so `docs/DEVELOPMENT.md` is restored byte-for-byte to its committed state
and the rule now lives in [`../../runtime-capture.md`](../../runtime-capture.md),
the authoritative runtime procedure those files point at. No code changed.

The channel latches three things on one frame clock, because the claim is a
**correlation** and no single value settles it: the record's `+0x10` read through
the engine's own route, the selector at `0x03001A34`, and the live player object at
`0x03001C34` with its own `+0x10`. It writes a row on every change, so the file is
a timeline rather than a sample, and an implausible player slot is reported rather
than dereferenced. **No input or memory-modifying call was added**, and the
read-only guard test pins that.

## Measured result

Run `E-stomach-facing`, derivative `warpedit001-stomach.gba`, `map:0040/transition:0000`
retargeted to `map:0435`, record `+0x10 = 0x42`.

| frame | map | player object | player `+0x10` |
| --- | --- | --- | --- |
| 430 | 40 | `0x0203CEB4` | `00` South |
| 1606 | 40 | `0x0203CEB4` | `01` North |
| 1698 | 40 | `0x0203CEB4` | `02` West - the approach |
| 2154 | **435** | slot `0x00000000` | (empty during the load) |
| 2172 | **435** | `0x0202CCDC` | **`03` East** - written by the warp |
| 2658 | 435 | `0x0202CCDC` | `02` West - the operator walked on |

* **Record `+0x10`**: `0x42` throughout, read live through the engine's own route.
* **Selector `0x03001A34`**: `0x00000000` on **every** sample, including across the
  map load. The traced skip never applied.
* **Player facing byte**: `00` -> `01` -> `02` before the warp, and `03` on the
  player object the warp created. `(0x42 >> 4) - 1 = 3 = East`.
* **Human observation**: East-facing arrival, reversing the westward approach.

All four agree, so the authoring rule is **runtime-proven for this
configuration**.

## What is NOT proven

* **What `0x03001A34` selects is unresolved.** Only that it was `0` here.
* **The non-zero gate case is UNTESTED.** No run has presented a non-zero
  selector, so the rule is proven for this configuration and is not to be called
  universally reliable.
* **The low nibble's semantics remain UNRESOLVED.** It gates the door; `0x02` is
  not "face West".
* The caller of the transition objects' `vtbl+0x04` is still untraced.

## Incidental corroboration of the static trace

The warp **replaced the player object** - `0x0203CEB4` in map 40, the slot reading
`0x00000000` during the load, then `0x0202CCDC` in map 435. That is what the trace
claimed independently: the warp constructs a new player and `0x080109AA` stores it
at `0x03001C34`. Two channels agreeing on more than the facing byte is worth
recording as such.

## Lifecycle

* Implementation commit **`062bea5`** on `ticket/map-warp-facing-trace-001`, from
  `2c2c580`.
* Focused tests only: `tests/unit/test_mgba_capture.py` (77 passed). Broad suite
  not run.
* Canonical ROM `940ad5f0…f059e` unchanged; private save `7cf0a516…` isolated and
  unchanged; no runtime artefact of this run is tracked.
* **Nothing was merged.** MR `!89` remains open.
* The runtime run directories live under the ignored `build/warpedit001/`
  (`D-stomach`, `E-stomach-facing`).

## Stop

Stop when the facing result is instrumented, the selector question is answered for
the run that exists, and the corrected rule is recorded. No third-map run, no
Workbench surface, no capability count change, no merge.
