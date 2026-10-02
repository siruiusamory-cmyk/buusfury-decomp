# A created transition at runtime

Runtime proof that the retail engine consumes a transition created through the
Workbench and built by the normal production path, from a record placed above the
original image end.

## Goal

Prove that a transition which does **not** exist in the canonical image, created
through the real DragonByte Z Workbench, is found and consumed by the retail
engine - including the pointer array and the record the build places **above the
original 8 MiB EOF**. Retargeting an existing transition does not satisfy this
record; only creation does.

## 1. The proof transition

| | |
| --- | --- |
| source map | `map:0040` (Grand Kai's Planet) |
| authored identity | `map:0040/transition:proof-door-rt001` |
| template / base | `map:0040/transition:0000` (566-class, same map) |
| region | first interval `10..60`, second interval `112..169` (pixels) |
| destination | `map:0435` (Buu's Stomach) |
| arrival | `(16, 360)` |
| facing | East (`facing_raw = 0x42`, low nibble `0x2` preserved from the base) |

**The region was chosen against retail geometry, not by eye.** Map 40's canonical
transitions are `map:0040/transition:0000` at first interval `0..9` with second
`112..169` (the door retail sends to map 39) and `map:0040/transition:0001` at
`232..273` with second `0..17` (the door to map 41). The authored region shares the
door's second interval and starts one pixel east of it, so it sits in the corridor
the operator already walks to reach the door, and it overlaps **neither** canonical
box (first intervals `10..60` vs `0..9` and `232..273`; the second interval is shared
with the first box only, and an overlap needs both).

**Which interval is horizontal was measured, not assumed.** The record stores two
halfword pairs; the codec names them positionally because the axis was `UNRESOLVED`.
Reading the first pair as horizontal and the second as vertical, all five canonical
boxes on maps 39, 40 and 435 fit inside their own map's walkable extent. Reading
them the other way round, `map:0039/transition:0001` would need `y 592..601` on a map
whose extent is `618x426` - impossible. The first interval is therefore the
horizontal one, and the unit is pixels (the extents the authority derives are
pixels, and every arrival in the same records is a pixel pair). Evidence:
`build/runtime-rt001/axis-proof.txt` (ignored working artifact).

## 2. Authored through the real Workbench

Driven through the shipped `Maps -> Warps` surface of the real `MainWindow`
(`tools/webfoot/workbench/warp_tab.py`) over a project extracted from the canonical
ROM: the Create action, then one gesture per field through the surface's own slots,
then **Apply through the surface's own button**. No TOML was hand-edited and no
research serializer was invoked.

| step | surface's own answer |
| --- | --- |
| select map 40 | two retail rows, `map:0039` (`first 0-9 - second 112-169`) and `map:0041` (`first 232-273 - second 0-17`) |
| Create transition | the form opens; `Not staged`, reason `Author a name for the new transition.` |
| name `proof-door-rt001` | identity `map:0040/transition:proof-door-rt001` |
| template `map:0040/transition:0000` | the 566-class same-map base, offered by the authority |
| region `((10, 60), (112, 169))` | `New (staged)` |
| arrival `(16, 360)` | staged |
| destination `map:0435` | staged |
| facing `3` (East) | staged |
| Apply (button `Apply to project`) | `Applied the new transition to maps/transition_creations.toml. Validate and build to materialize it.` |
| row afterwards | `proof-door-rt001`, `map:0435 - Stomach`, `first 10-60 - second 112-169`, `16, 360`, `East`, `New (saved)` |

What the Workbench wrote (read back):

```toml
[creation."map:0040".proof-door-rt001]
template = "map:0040/transition:0000"
destination = "map:0435"
region = [[10, 60], [112, 169]]
arrival = [16, 360]
prior_facing_raw = 2
prior_unresolved_raw = 0
facing = 3
```

**SAVE / CLOSE / REOPEN: PASS.** The project was closed (`session.project_dir =
None`, the shell recomputed its state) and reopened over the same directory: the row
returns with the same identity, base, region, destination, arrival, facing and
`New (saved)` state, and nothing staged.

## 3. Build through the normal path

`validate_project` over the extracted project - `problems=()`, 141 enemies, 9
characters, 1534 strings, 452 maps - then `build_project` into a new file. No
alternate serializer, no manual allocation, no byte patch.

| | |
| --- | --- |
| derivative | `build/runtime-rt001/create-rt001-stomach.gba` (ignored) |
| size | 16,777,216 bytes (the canonical image is 8,388,608) |
| **SHA-256** | **`03A30D4BACF05939FAE44161334344CF3809B5884BE7E749C857337A3E6DE78A`** |
| reproducibility | a second, independent authoring-and-build run produced the **same** SHA-256 |

## 4. Static build evidence

| | |
| --- | --- |
| root count | canonical **2** -> derivative **3** |
| root | `0x08293474` (unchanged address) |
| root `+0x44` array | canonical `0x0829346C` -> derivative **`0x08800000`**, file `0x800000` |
| array element 0 | file `0x800000` -> `0x0829343C` (the canonical record, unchanged) |
| array element 1 | file `0x800004` -> `0x08293454` (the canonical record, unchanged) |
| **array element 2** | file `0x800008` -> **`0x0880000C`** |
| **new record** | file `0x80000C`, GBA **`0x0880000C`** |
| above the original EOF | **yes**, both the array and the record |

The two canonical elements are byte-identical to the canonical image, in the same
order, still pointing at the same records. The new record differs from its template
exactly as authored, and preserves what a creation does not author:

| field | template | new |
| --- | --- | --- |
| destination key | `0x01, 0x0b` (map 39) | **`0x15, 0x0b` (map 435)** |
| region | `0..9`, `112..169` | **`10..60`, `112..169`** |
| arrival | `(599, 196)` | **`(16, 360)`** |
| `+0x10` | `0x02` | **`0x42`** (high nibble `4` -> direction `3` = East; low nibble `0x2` preserved) |
| class word | `0x08007675` | `0x08007675` (566 family, unchanged) |
| invariant word | `134248301` | `134248301` (unchanged) |
| `+0x13` | `0` | `0` (unchanged) |

**Only four bytes below the canonical EOF changed**: the root's count byte and
three of the four bytes of the root's `+0x44` pointer. Everything else the build
adds lives above the original EOF.

## 5. Runtime observation (read-only)

`tools/runtime/warpcreate001_transition_watch.lua` (new, tracked) follows the
engine's own route - `MapEntry + 0x2C -> root`, then the root's `+0x40` count and
`+0x44` array - for elements **0, 1 and 2** of map 40, resolves each element's
record fields through the address the route returned, resolves the destination key
with the engine's own two-byte `MapEntry` scan, and latches the live map identity on
every change. An element the root's count does not admit is reported `absent` rather
than read past the array (the canonical control), and a count-admitted word that is
not a ROM address is `unreadable`, never conflated with `absent`. It accepts both
the 8 MiB canonical image and the 16 MiB derivative, names no build address, and is
read-only with respect to emulated state and input. The allowlist in
`tools/runtime/inject_mgba_lua.ps1` now names it; every other step reuses the
tracked launcher, injector and state loader.

`tools/runtime/finish_warpcreate001_session.ps1` (new, tracked) summarises a
finished session from `create-watch.csv` and re-verifies the ROM, savestate and
private save against the digests the launcher recorded.

One measured property of the savestate is worth recording before the run: its RAM
holds live pointers to the two **canonical** transition records (`0x0829343C`,
`0x08293454`) and not to the pointer array, so the state carries an area that was
built from the old image. A new array element can therefore only be consumed once
map 40's area is built from the derivative - which is what re-entering the map does.
The run sheet keeps the direct attempt first and records the re-entry attempt
second, so which of the two the engine needs is itself evidence.

### What the observer must report, derived before the run

The observer's derivation was repeated independently over both images (same offsets,
same route) so the expected rows are known in advance. The observer samples the live
emulated memory, so these are the values it must print; anything else is a finding,
not a detail:

| | canonical | derivative |
| --- | --- | --- |
| `MapEntry + 0x2C` -> source | `0x0807561C` | `0x0807561C` |
| root | `0x08293474` | `0x08293474` |
| root `+0x40` count | **2** | **3** |
| root `+0x44` array | `0x0829346C` | **`0x08800000`** |
| element 0 | file `0x29346C` -> record `0x0829343C`, key `0x01,0x0b` -> map 39 | file `0x800000` -> same record, same key -> map 39 |
| element 1 | file `0x293470` -> record `0x08293454`, key `0x01,0x0d` -> map 41 | file `0x800004` -> same record, same key -> map 41 |
| element 2 | **`absent`** (the count does not admit it) | file `0x800008` -> record **`0x0880000C`**, key `0x15,0x0b` -> **map 435**, region bytes `0a0070003c00a900`, `+0x10 = 0x42`, arrival `(16, 360)` |

The region bytes decode positionally as `a,b,c,d` little-endian halfwords:
`a=10, b=112, c=60, d=169`, i.e. first interval `10..60` and second `112..169`, which
is exactly what the Workbench authored. The same decode on the canonical element 0
gives `0,112,9,169` - the row the Warps mode displays as `first 0-9 - second
112-169` - which is a second, independent confirmation of the field order.

The cartridge header is byte-identical in both images (`0x80 = 0xBB`, header checksum
`0xBD = 0x84`): the build changed only the root's count and `+0x44` pointer below the
original EOF and appended the new array and record above it.

## 6. Retail control: PASS

One human-operated session on the canonical image (label `rt001-control`, launcher
`tools/runtime/start_warpedit001_live.ps1`, observer
`tools/runtime/warpcreate001_transition_watch.lua`, the `.ss1` savestate above,
mGBA 0.11.0.0), 39 observer rows. The operator walked the authored region and then
the retail door; no input of any kind came from the instrument.

| observation | value |
| --- | --- |
| map 40 root `+0x40` count, every sample | **2** |
| map 40 root `+0x44` array, every sample | `0x0829346C` |
| element 2 | **`absent`** - `root_count 2 does not admit the index` |
| live map | 40 from frame 158 |
| map changes | frame 3669 -> **39** (`from=40`, the retail door), frame 3767 -> 40 (`from=39`) |
| rows naming map 435 | **none** |
| ROM / savestate / private save | **UNCHANGED** (`940AD5F0...`, `2D5740A8...`, `7CF0A516...`) |

**The authored transition does not exist in retail, and entering the region did not
produce it.** The only transition the walk produced was the retail door's own, and
it still works.

## 7. The proof: the created transition fired

One human-operated session on the derivative (label `rt001-derivative`, same
launcher, observer and savestate), 22 observer rows.

Read live from the running emulator before any walking, through the engine's own
route:

| element | live route |
| --- | --- |
| 0 | root `0x08293474`, count **3**, array **`0x08800000`**, element -> record `0x0829343C`, key `0x01,0x0b` -> map 39 |
| 1 | same root and array, element -> record `0x08293454`, key `0x01,0x0d` -> map 41 |
| **2** | same root and array, element -> **`0x0880000C`**, key **`0x15,0x0b` -> map 435**, region `0a0070003c00a900` = `10..60`/`112..169`, `+0x10 = 0x42`, arrival `(16, 360)` |

Every live map change the engine reported:

| frame | map | note |
| --- | --- | --- |
| 145 | 40 | first observed map |
| 434 | 39 | `from=40` - the operator walked through the retail door, the authored transition did **not** fire on this pass |
| 543 | 40 | `from=39` - re-entered map 40, so its area was rebuilt from the derivative |
| **1191** | **435** | **`from=40` - the created transition fired** |
| 1340 | 434 | `from=435` - the operator walked on inside Buu's Stomach |
| 1450 | 435 | `from=434` - and back |

**Why this is creation and not something else.** On map 40 the only record whose
region contains the authored box is the new element 2: element 0's box is
`0..9`/`112..169` and element 1's is `232..273`/`0..17`, both disjoint from
`10..60`/`112..169` (section 1). Element 2's live key is `0x15,0x0b`, which resolves
to map 435; neither canonical record's key names 435. The map change to 435 is
therefore the created record being consumed, and the live route rows show the engine
reaching it through an array word at `0x08800000` and a record at `0x0880000C`,
both above the original 8 MiB EOF.

**The first pass reaching the retail door is a measured property, not a defect.**
The savestate was made on map 40, and its RAM holds live pointers to the two
canonical records, so the area it carries was built from the old image and knew only
two elements (section 5). Once map 40 was re-entered, its area was built from the
derivative and the third element was consumed. This is recorded because it is the
one procedure the run needs: a savestate taken on the map under test carries that
map's already-built area.

**Player usability after arrival.** The operator's own completion signal ended the
session; the observer shows the player then moved on to map 434 and back to 435
(frames 1340, 1450), which is only possible with a controllable player. Recorded as
the instrument's evidence rather than as a paraphrase of the operator.

## 8. What was and was not measured

| claim | status |
| --- | --- |
| the engine traverses the NEW array element to the NEW record | **measured**: live route rows to `0x08800000` -> `0x0880000C` |
| the engine follows the created record to its destination | **measured**: map 40 -> 435 at frame 1191 |
| above-EOF addressability for creation | **RUNTIME-PROVEN**: both structures live at file `0x800000`/`0x80000C` |
| the authored arrival value at runtime | **in the live record**: `arrival_14 = 0010`, `arrival_16/17 = 68,01` = `(16, 360)` |
| the authored facing at runtime | **in the live record**: `+0x10 = 0x42` (East, low nibble `0x2` preserved) |
| the exact arrival pixel on screen | **NOT INSTRUMENTED**: this observer has no player-coordinate channel, and the record does not require one |
| the warp's write of the arrival facing onto the player object | **not re-measured here**; proved by `MAP-WARP-WORKBENCH-RUNTIME-001` with the facing tracer, which this record did not rerun |
| `0x03001A34` | **not measured in this record** (the facing tracer's channel) |

**One instrument artifact, recorded rather than hidden.** The control session was
run with observer revision `de5c09aa4058c2b6808e09cfa0c209c0971c8121`, whose unresolved-route warning also fired on
frames that merely skipped sampling; its CSV therefore carries one spurious
`ROUTE_UNRESOLVED` row at frame 601 while the route rows beside it resolve count 2
and element 2 `absent` correctly. Commit `17f0c1af307ae8b9c80d1dbbb4fb67e0b424f521` narrowed the condition to frames
that actually sampled and never resolved, and the derivative session was run with
that revision: its CSV has **zero** `ROUTE_UNRESOLVED` rows.

## Measured status summary

```text
MAP-WARP-CREATE-RUNTIME-001 - STATUS REPORT

BASELINE:                    e77e9eede0ac3b8368e2151db95c92475a1b506d
WORKTREE:                    <record worktree>
SOURCE MAP:                  map:0040 (Grand Kai's Planet)
AUTHORED IDENTITY:           map:0040/transition:proof-door-rt001
CANONICAL TRANSITION COUNT:  2
DERIVATIVE TRANSITION COUNT: 3
NEW TRANSITION INDEX:        2
TRIGGER REGION:              first 10..60, second 112..169
DESTINATION:                 map:0435 (Buu's Stomach)
ARRIVAL:                     (16, 360)
FACING:                      East (facing_raw 0x42)

RETAIL CONTROL:              PASS
RETAIL RESULT IN NEW TRIGGER REGION:
                             nothing; element 2 absent, root count 2; the only
                             transition fired was the retail door 40 -> 39
AUTHORED THROUGH WORKBENCH:  YES
SAVE/REOPEN:                 PASS
BUILD:                       PASS
DERIVATIVE SHA-256:          03A30D4BACF05939FAE44161334344CF3809B5884BE7E749C857337A3E6DE78A
NEW POINTER ARRAY:           file 0x800000 / GBA 0x08800000
NEW ARRAY ELEMENT:           index 2, live pointer 0x0880000C (file 0x800008)
NEW TRANSITION RECORD:       file 0x80000C / GBA 0x0880000C
ABOVE ORIGINAL EOF:          YES
LIVE ENGINE ARRAY POINTER:   0x08800000
LIVE ENGINE NEW RECORD:      0x0880000C (key 0x15,0x0b -> map 435)
WORKBENCH-CREATED TRIGGER FIRED: YES - frame 1191, map 40 -> 435
RUNTIME DESTINATION:         map 435
ARRIVAL VALUE:               PASS (live record (16, 360))
EXACT ARRIVAL PIXEL:         NOT INSTRUMENTED (no player-coordinate channel)
ARRIVAL FACING:              PASS in the live record (+0x10 = 0x42 = East, low nibble preserved)
PLAYER USABLE:               PASS (the player moved on to map 434 and back)
AUTOMATED GAMEPLAY INPUT:    NO
PASSIVE OBSERVER:            read-only; engine-route rows for elements 0/1/2, live map
                             channel, heartbeats; zero ROUTE_UNRESOLVED rows on the
                             corrected revision used for the derivative session
ABOVE-EOF TRANSITION ADDRESSABILITY: RUNTIME-PROVEN
RUNTIME NEW-TRANSITION PROOF: PASS
CANONICAL ROM:               UNCHANGED (940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E)
PRIVATE SAVE / SAVESTATE:    UNCHANGED (7CF0A516..., 2D5740A8...)
PRODUCT CODE CHANGED:        NO
MANUAL BROAD SUITE:          NOT RUN
PRODUCT CAPABILITY IMPACT:   NONE
DRAGONBYTE Z:                19 / 24 - 79%
PARENT:                      MAP-WARPS-AND-CONNECTIONS-001 - READY FOR CLOSEOUT
NEXT:                        MAP-WARPS-AND-CONNECTIONS-001 PARENT CLOSEOUT
```
