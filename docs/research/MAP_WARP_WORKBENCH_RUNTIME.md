# End-to-end proof of a Workbench-authored transition

Authoring a transition in the Workbench, building it through the normal path and
observing the retail engine consume it, with the passive instrument evidence and the
human observation kept distinct.

## Goal

Prove the **existing-transition authoring path end to end**: a transition authored
through the real Workbench surface, saved, reopened, built by the production path,
and consumed by the retail engine - with the destination, arrival and facing the
author set.

Target, as given: `map:0040/transition:0000`, retail destination `map 39`,
authored destination `map 435` (Buu's Stomach), arrival `(16, 360)`, facing
**East**.

## 1. Workbench authoring

Driven through the shipped `Maps -> Warps` surface on the real `MainWindow`
(`tools/webfoot/workbench/warp_tab.py`), one gesture at a time through the
widgets' own signals - not by writing TOML:

| step | gesture | surface's own answer |
| --- | --- | --- |
| open Map 40 | source selector | `map:0040 - Grand Kai's Planet, 2 connections` |
| select the connection | row selection | identity `map:0040/transition:0000`, retail: leads to `map:0039`, arrival `599, 196`, facing Unchanged |
| destination -> 435 | destination selector | refused: `map:0435 has no connection back to map:0040, so no safe arrival can be derived... state the arrival explicitly, then choose the destination.` |
| arrival -> (16, 360) | arrival spin boxes | staged `destination=map:0435, arrival=(16,360)` |
| facing -> East | facing selector | staged `destination=map:0435, arrival=(16,360), facing=3` |
| Apply | Apply button | `Applied the connection edit to maps/transitions.toml. Validate and build to consume it.` |
| row after Apply | - | `map:0435 - Stomach`, arrival `16, 360`, facing `East`, state `Saved` |

**The destination-only step was refused, and that is the designed behaviour**: map
435 has no connection back to map 40, so no arrival can be derived from the
direction of travel, and the surface will not leave the arrival belonging to the
old destination. Stating the arrival authored both together, and the resulting
draft was the retarget the authority accepted. An author reaching a one-way
destination must therefore state the arrival first - a real authoring constraint,
recorded here for the parent rather than worked around.

What the Workbench wrote (`maps/transitions.toml`, read back, not hand-edited):

```toml
[transition."map:0040"]

[transition."map:0040".0000]
prior_destination = "map:0039"
destination = "map:0435"
arrival_authored = true
prior_arrival = [599, 196]
arrival = [16, 360]
facing_authored = true
prior_facing_raw = 2
facing_raw = 66
```

`prior_*` is the retail record's own state (destination map 39, arrival (599,196),
`+0x10 = 2`), and the authored `facing_raw = 66` is `0x42`: the East override
`((3 + 1) << 4)` over the preserved low nibble `0x2`.

**SAVE/REOPEN: PASS.** A fresh `Session` and a fresh `MainWindow` over the same
project directory shows identity `map:0040/transition:0000`, leads to
`map:0435 - Stomach`, arrival `16, 360`, facing `East`, state `Saved` - the same
authored values, from disk.

## 2. Build

Normal production path only: `validate_project` (passed, zero problems) then
`build_project` into a new file. No alternate serializer, no manual byte patch.

| | |
| --- | --- |
| Derivative | `build/warpworkbench001/warpworkbench001-stomach.gba` (ignored) |
| Size | 8,388,608 bytes |
| **SHA-256** | **`3CB291AAE6699D140EBDA1453D9BB49C2D6EE00926822EF2383DDD9D008C7BCA`** |

Read back through the authority, the derivative's record carries exactly the
authored state:

| field | value |
| --- | --- |
| identity | `map:0040/transition:0000` |
| destination | `map:0435` |
| arrival | `(16, 360)` |
| `+0x10` | `0x42` (66) |
| arrival facing | `3` = East |
| gate bits | `2` (low nibble preserved) |
| bytes differing from the canonical image | 6, all inside the 24-byte record |

**Corroboration worth recording:** this derivative is **byte-identical** to the
one `MAP-WARP-FACING-TRACE-001` measured at runtime
(`3CB291AA...C7BCA`). The earlier image was produced by that sub-pass from a
project built outside the Workbench; this one was produced by the Workbench
authoring chain. The chain therefore reproduces the already-proven artifact
exactly - and the run below re-measured it independently.

## 3. Runtime, human-operated

One session, label `WB-stomach`:

```text
launcher : tools/runtime/start_warpedit001_live.ps1 (dry run first)
observer : tools/runtime/warpedit001_transition_watch.lua  (read-only; no input,
           no memory write)
ROM      : the derivative above, digest verified before launch and UNCHANGED after
state    : roms/Dragon Ball Z - Buu's Fury (U).ss1  sha256 2D5740A8...7D9A1AAB
mGBA     : 0.11.0.0, the pinned development build the observer was validated with
run dir  : build/warpedit001/WB-stomach  (ignored; run dir refused if it exists)
```

**No automated gameplay input was used and none is possible through this
pipeline**: the observer sends no keys and writes no memory. The operator walked
into the Map 40 doorway by hand; no leave-and-re-enter cycle was required, because
a transition is consumed when its trigger fires
([`../runtime-capture.md`](../runtime-capture.md)).

### Passive evidence (`session.csv`)

| frame | observation |
| --- | --- |
| 1 | TARGET: `MapEntry+0x2C -> root+0x44 -> record 0x0829343C`; destination key bytes `15 0b`; **key resolves to map 435** |
| 175 | first observed map: **40** |
| 896 | map **435**, `from=40` |

The record the engine reached carries the **authored** destination key, live, and
the source map's first departure is into map 435.

### Passive evidence (`facing.csv`)

| frame | map | record `+0x10` | selector `0x03001A34` | player object | player `+0x10` |
| --- | --- | --- | --- | --- | --- |
| 175-852 | 40 | `42` | `0x00000000` | `0x0203CEB4` | `00` -> `01` -> `02` (the approach) |
| 896 | 435 | `42` | `0x00000000` | slot `0x00000000` | (empty during the load) |
| 914 | 435 | `42` | `0x00000000` | `0x0202CCDC` | `00` |
| 915 | 435 | `42` | `0x00000000` | `0x0202CCDC` | **`03` = East** - written by the warp |
| 1059/1102 | 435 | `42` | `0x00000000` | `0x0202CCDC` | `01` / `03` - the operator walked on |

* The live record `+0x10` is `0x42` throughout, read through the engine's own
  route: `(0x42 >> 4) - 1 = 3` = East, with the low nibble `0x2` preserved.
* **Selector `0x03001A34` was `0x00000000` on every sample**, including across the
  load, so the traced skip never applied and the 566-class arrival-facing write was
  eligible. What the selector selects remains UNRESOLVED and its non-zero case
  remains UNTESTED.
* The warp **replaced the player object** (`0x0203CEB4` -> slot 0 during the load
  -> `0x0202CCDC`), and the new object first carried `00`, then `03` one frame
  later - the writing frame.

### Human observation (labelled as such, distinct from the instrument)

The operator reports: the destination was **Buu's Stomach** (not the retail map
39), the entry happened correctly, and the character was **movable immediately
afterwards**.

## What this proves, and what it does not

**Proven for this configuration:** the chain Workbench UI -> saved project ->
reopened project -> normal build -> derivative -> retail engine -> authored
destination, arrival and facing. The engine consumed the **authored** destination
(map 435) and wrote the **authored** facing (East, `0x42` -> `03`), on an image
whose destination and facing differ from retail, and the player remained usable.

**Not proven / limitations, stated rather than implied:**

* The **arrival pixel** was not machine-measured in this run: the passive observer
  channels are the transition record, the map, the selector and the facing, and it
  has no player-coordinate channel. The authored `(16, 360)` is verified present in
  the built record, and the human observation confirms a correct, movable entry;
  the exact on-screen coordinate is `UNVERIFIED-BY-INSTRUMENT` for this run.
* **What `0x03001A34` selects** is still `UNRESOLVED`; only that it read `0` here.
* **The low nibble's semantics remain `UNRESOLVED`**; it gates the door. `0x02` is
  not "face West", and the authored byte shows the low nibble preserved.
* **A one-way destination requires the arrival to be stated explicitly**, as the
  surface refused the destination-only step and accepted the two together.
* This proves **existing-transition editing** only. The parent capability still
  needs its own decision and proof for transition **creation** before 20 / 24.

## Measured status summary

```text
MAP-WARP-WORKBENCH-RUNTIME-001 - STATUS REPORT

BASELINE:
5294934d25022f1da684775895ef76d451cad4b0

TRANSITION:
map:0040/transition:0000

AUTHORED THROUGH WORKBENCH:
YES - Maps -> Warps, one gesture per field, Apply through the surface

DESTINATION:
map 435

ARRIVAL:
(16, 360)

FACING:
East

SAVE/REOPEN:
PASS

BUILD:
PASS - validate_project clean, build_project, no alternate serializer

DERIVATIVE SHA-256:
3CB291AAE6699D140EBDA1453D9BB49C2D6EE00926822EF2383DDD9D008C7BCA

RETAIL RESULT:
map 40 -> map 39

WORKBENCH-AUTHORED RESULT:
map 40 -> map 435

ARRIVAL POSITION:
PASS (human-observed correct entry and usability; authored (16,360) verified in
the built record; the exact pixel is UNVERIFIED-BY-INSTRUMENT this run)

ARRIVAL FACING:
PASS - the warp's new player object first carries 03 = East from the live
record +0x10 = 0x42

PLAYER USABLE AFTER ARRIVAL:
PASS - operator-reported, and the facing channel shows him walking on

PASSIVE OBSERVER:
record route MapEntry+0x2C -> root+0x44 -> 0x0829343C; key 15 0b -> map 435;
map 40 (frame 175) -> map 435 (frame 896, from=40); record +0x10 = 0x42 live;
selector 0x03001A34 = 0 on every sample; player object replaced
0x0203CEB4 -> 0x0202CCDC with facing 03 written one frame after it appeared

AUTOMATED GAMEPLAY INPUT:
NO

CANONICAL ROM:
UNCHANGED

RUNTIME END-TO-END PROOF:
PASS

PRODUCT CAPABILITY IMPACT:
NONE

DRAGONBYTE Z:
19 / 24 - 79%

PARENT:
MAP-WARPS-AND-CONNECTIONS-001 - NOT SHIPPED

NEXT:
RETURN FOR PARENT GAP DECISION
```
