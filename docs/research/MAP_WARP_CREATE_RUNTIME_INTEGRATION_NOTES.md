# MAP-WARP-CREATE-RUNTIME-001 - a created transition at runtime

STATUS: **CLOSED.** Scoped **sub-pass of `MAP-WARPS-AND-CONNECTIONS-001`**,
completed 2026-09-27 and archived at the parent's closeout (2026-09-28). The full
evidence record, the run sheets and the observer derivations stay at
[`../MAP-WARP-CREATE-RUNTIME-001.md`](../MAP-WARP-CREATE-RUNTIME-001.md).

`public progress impact: NONE` - no capability shipped here: no product code
changed, the registry stayed at **19 / 24 (79%)**, `EDIT` stayed **7 / 8**, and no
site source changed. The capability advance to **20 / 24** belongs to the parent's
own closeout.

## What it was asked to do

Prove that a transition the canonical image does **not** contain, created through the
real DragonByte Z Workbench and built by the normal production path, is found and
consumed by the retail engine - including the pointer array and the record the build
places **above the original 8 MiB EOF**. Retargeting an existing transition would not
have satisfied this; only creation does.

## What was proved

Baseline `5224c7376660c5e35f2063e9e59699911a1a4750`. The proof transition was
`map:0040/transition:proof-door-rt001`, a 566-class same-map template of
`map:0040/transition:0000`, region first `10..60` / second `112..169` (chosen against
retail geometry so it overlaps neither canonical box), destination `map:0435`,
arrival `(16, 360)`, facing East (`facing_raw = 0x42`, low nibble preserved).

* **Authored through the real Workbench**: the Create action and one gesture per
  field through the surface's own slots, then Apply through the surface's own button.
  No TOML was hand-edited. Save/close/reopen returned the same identity, base,
  region, destination, arrival, facing and `New (saved)` state.
* **Built through the normal path**: `validate_project` clean, then `build_project`;
  derivative SHA-256 `03A30D4BACF05939FAE44161334344CF3809B5884BE7E749C857337A3E6DE78A`,
  16,777,216 bytes, and a second independent authoring-and-build run produced the
  same SHA-256.
* **Above the original EOF**: root count 2 -> 3; root `+0x44` array
  `0x0829346C` -> `0x08800000` (file `0x800000`); element 2 -> `0x0880000C`; new
  record at file `0x80000C` / GBA `0x0880000C`. The two canonical elements are
  byte-identical to the canonical image, in the same order, pointing at the same
  records. Only four bytes below the canonical EOF changed: the root's count byte and
  three of the four bytes of its `+0x44` pointer.
* **Retail control PASS** on the canonical image: root count 2 and element 2 `absent`
  on every sample, the only transition fired was the retail door 40 -> 39, and no
  row named map 435.
* **The created transition fired on the derivative**: map 40 -> **435** at frame
  1191, after the operator re-entered map 40 so its area was rebuilt from the
  derivative. The live route rows show the engine reaching an array word at
  `0x08800000` and a record at `0x0880000C`, both above the original EOF, and the
  player then moved on to map 434 and back to 435, which is only possible with a
  controllable player. **No automated gameplay input** was used or possible.

The record states why this is creation and not something else: on map 40 only the new
element 2's region contains the authored box, both canonical boxes are disjoint from
it, and neither canonical record's key names map 435.

## Review status

No product code changed, so no independent code-review gate applied to a diff. The
tracked additions are a read-only observer, a session summariser and an
additions-only allowlist entry naming the observer; the parent capability owns the
review gate at its own closure.

## Limitations preserved

* **The exact arrival pixel on screen was NOT INSTRUMENTED.** The observer has no
  player-coordinate channel and the ticket did not require one. The authored value
  is verified present in the live record (`arrival_14 = 0010`,
  `arrival_16/17 = 68,01` = `(16, 360)`).
* **The warp's write of the arrival facing onto the player object was not re-measured
  here.** It is proved by `MAP-WARP-WORKBENCH-RUNTIME-001` with the facing tracer,
  which this ticket did not rerun.
* **`0x03001A34` was not measured in this ticket** (it is the facing tracer's
  channel), and what it selects remains `UNRESOLVED`; its non-zero case remains
  `UNTESTED`.
* **The savestate carries the map's already-built area.** A savestate taken on the
  map under test holds live pointers to the canonical records, so the created element
  can only be consumed once that map is re-entered - which is a measured property of
  the procedure, recorded rather than presented as a defect.
* **One instrument artifact, recorded rather than hidden.** The control session ran
  with observer revision `fb66c3f`, whose unresolved-route warning also fired on
  frames that merely skipped sampling, so its CSV carries one spurious
  `ROUTE_UNRESOLVED` row at frame 601 while the route rows beside it resolve
  correctly. The condition was narrowed so it fires only on frames that actually
  sampled and never resolved; the derivative session ran with that revision and has
  **zero** `ROUTE_UNRESOLVED` rows.

## Validation and policy

* The evidence is the human-operated runtime run plus the static build evidence; the
  observer's expected rows were derived independently over both images before the
  run.
* **Test-policy record:** no manual broad suite was run for this ticket; the
  acceptance evidence is the runtime run.
* Authoring was driven through the shipped surface and the build through the shipped
  path, so the proof is of the shipped chain, not of a research harness.

## Safety

Canonical ROM `940ad5f0...f059e` verified before every launch and re-verified
afterwards and **UNCHANGED**; private save and savestate unchanged
(`7CF0A516...`, `2D5740A8...`); no ROM, savestate, save, capture or generated project
output tracked - the derivative, the project and the run directories all live under
ignored `build/`; the private save beside the canonical image was never written.

## Stop and next

Stopped after the runtime proof. The sub-pass reported the parent as ready for
closeout. The parent's own closeout states the final result: `warps` ships, `EDIT`
becomes **8 / 8** and DragonByte Z becomes **20 / 24 - 83%**.
