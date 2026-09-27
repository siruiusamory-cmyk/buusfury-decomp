# MAP-WARP-CREATE-RUNTIME-001 - a created transition at runtime

STATUS: **AUTHORING, PERSISTENCE AND BUILD COMPLETE; THE HUMAN-OPERATED RUNTIME RUNS
ARE PENDING.** Scoped sub-pass of `MAP-WARPS-AND-CONNECTIONS-001`, which stays
**NOT SHIPPED** in [`PROJECT_<local-state-name>`](PROJECT_<local-state-name>).

Baseline: `5224c7376660c5e35f2063e9e59699911a1a4750` on branch
`ticket/map-warp-create-runtime-001`, worktree
`<ticket-worktrees>\map-warp-create-runtime-001` (clean at creation).
`public progress impact: NONE` - the registry stays at **19 / 24 (79%)**, `EDIT`
stays **7 / 8**, and no site source changed.

## Goal

Prove that a transition which does **not** exist in the canonical image, created
through the real DragonByte Z Workbench, is found and consumed by the retail
engine - including the pointer array and the record the build places **above the
original 8 MiB EOF**. Retargeting an existing transition does not satisfy this
ticket; only creation does.

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

## 6. Retail control and human runtime runs

**PENDING - these are human-operated and no automated input is used or possible.**
Run sheet, with the exact commands, the region to walk into and the annotated map:
`build/runtime-rt001/RUN-SHEET.txt` (ignored working artifact), summarised in the
handoff report. Both runs load the same savestate
(`roms/Dragon Ball Z - Buu's Fury (U).ss1`, sha256
`2D5740A8C54180D153024A11B0E4D1143306957AF55A3AD0664C71CF7D9A1AAB`, the map-40 state
the earlier warp runtime passes used):

* **retail control** on the canonical image: walk into the authored region and
  expect nothing; the observer must show map 40's root count as **2** with element 2
  `absent`;
* **the proof** on the derivative: walk into the same region and expect the engine
  to send the player to **map 435**.

## Safety

* Canonical ROM `940ad5f0...f059e` - verified before every launch and re-verified
  afterwards; **UNCHANGED**.
* No ROM, savestate, save, capture or generated project output is tracked; the
  derivative, the project and the run directories are all under ignored `build/`.
* The private save beside the canonical image is never written: the launcher points
  the emulator at an isolated save directory inside the run directory.
* No product code changed. No test suite was run for this ticket: the acceptance
  evidence is the runtime run.
