# End-to-end proof of a Workbench-authored transition: integration notes

The condensed record of the end-to-end runtime proof, with its limits preserved.

## Scope

Prove the **existing-transition authoring path end to end**: a transition authored
through the real Workbench surface, saved, reopened, built by the production path,
and consumed by the retail engine, with the destination, arrival and facing the
author set. Target: `map:0040/transition:0000`, retail destination map 39, authored
destination map 435 (Buu's Stomach), arrival `(16, 360)`, facing East.

## What was proved

Baseline `5294934d25022f1da684775895ef76d451cad4b0` (the merge that integrated
`MAP-WARP-WORKBENCH-001`). Authoring was driven one gesture at a time through the
shipped `Maps -> Warps` widgets, never by writing TOML: open map 40, select the
connection, state the arrival `(16, 360)` after the destination-only step was
correctly refused for a one-way destination, set facing East, then Apply through the
surface's own button. Save/close/reopen reproduced the same identity, destination,
arrival, facing and `Saved` state from disk.

The normal production path then built a derivative
(`3CB291AAE6699D140EBDA1453D9BB49C2D6EE00926822EF2383DDD9D008C7BCA`), and a
human-operated mGBA session on it sent map 40 to **map 435**, not the retail map 39.
The passive observer read the live record `+0x10 = 0x42` through the engine's own
route and the warp's new player object first carrying facing **`03` = East**, with
selector `0x03001A34` reading `0` on every sample. No automated gameplay input was
used and none is possible through the pipeline.

**Corroboration recorded rather than glossed:** this derivative is byte-identical to
the image `MAP-WARP-FACING-TRACE-001` had already measured at runtime from a project
built outside the Workbench, so the Workbench authoring chain reproduces the
already-proven artifact exactly and the run re-measured it independently.

## Limitations preserved

* **The arrival pixel was not machine-measured in this run.** The passive observer
  has no player-coordinate channel; the authored `(16, 360)` is verified present in
  the built record and the human observation confirms a correct, movable entry, but
  the exact on-screen coordinate is `UNVERIFIED-BY-INSTRUMENT` for this run.
* **What `0x03001A34` selects is still `UNRESOLVED`**; only that it read `0` here.
* **The non-zero gate case is `UNTESTED`**, so the facing rule is proven for this
  configuration and is not to be called universally reliable.
* **The low nibble of `+0x10` remains `UNRESOLVED`**; it is preserved, and `0x02` is
  not "face West".
* **A one-way destination requires the arrival to be stated explicitly.**
* **This proves existing-transition editing only.** At this pass the parent still
  needed its own decision and proof for transition creation before 20 / 24.

## Validation

* The evidence is the human-operated runtime run; authoring, save/reopen and build
  were exercised through the production surfaces only.
* **Test-policy record:** no focused or broad suite was re-run for confidence,
  because no product code changed in this pass.
* The operator's own completion signal ended the session, and the observer shows the
  player later moving on to map 434 and back to 435, which is only possible with a
  controllable player.

## Stop

Stopped after the runtime proof. The parent's transition-creation half and the
capability advance to **20 / 24** remained; `MAP-WARP-CREATE-RUNTIME-001` later
proved creation, and the parent's own closeout states the final result.
