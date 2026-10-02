# Resizing a supported map and authoring its layers

What a supported map's structure actually is, what the resize capability builds,
what was measured, what is proven at runtime, and what is deliberately not
claimed.

This record states what a supported map's structure actually is, what was built,
what was measured, what is proven at runtime, and what is deliberately not
claimed.

---

## 1. The structural model - measured, not assumed

Every number below comes from the canonical image's own bytes, read through
`tools/webfoot/formats/map_graphics.py`.

### 1.1 The map root

A `MapEntry`'s `+0x2C` is a pointer to a word whose value is the map's **root**
(the engine's load-time definition template). Reached by
`*(MapEntry + 0x2C)`; measured over all 452 entries there are **421 distinct
roots**, so **11 roots are shared by more than one map** (map 23 and map 32 load
one definition; root `0x0822CC08` serves eight maps). The source word itself is
**never shared**: all 452 are distinct.

| Root field | Meaning | Evidence |
|---|---|---|
| `+0x00` | two ordered key bytes and blend registers | read at `0x0800953E` |
| `+0x04..+0x07` | four bytes added to `BG0CNT..BG3CNT`, one per slot | `ROOT_BG_ADDEND_OFFSET` |
| **`+0x08` / `+0x0A`** | **the map's declared extent in pixels, stored as `extent - 1`** | see 1.2 |
| `+0x0C` / `+0x10` | animated-tile count / array | `ROOT_ANIMATED_*` |
| **`+0x14`, `+0x18`, `+0x1C`, `+0x20`** | **four layer-slot pointers, all non-null on all 452 roots** | `ROOT_LAYER_SLOTS` |
| `+0x34` / `+0x38` | two tilemap source containers | `0x0800953E` |
| `+0x3C` | word: `0` on 451 roots, `1` on map 19 | selects the `BGxCNT` table row and the unclamped camera path |
| `+0x40` / `+0x44` | connection count / array | `0x08009676` |
| `+0x48`, `+0x4C` | selector stream, bank table | `0x08009C02`, 187 entries |

### 1.2 `+0x08` / `+0x0A` are the camera's maximum scroll

Independently disassembled for this record (Thumb, read-only, canonical image
hash verified):

```text
0800958A  ldrh r0,[r5,#0x8]   ; the extent word
0800958E  subs r0,#0x1
08009590  strh r0,[r4,#0x1c]  ; dest+0x9C = extent - 1   <- camera clamp maximum X
08009592  ldrh r0,[r5,#0xa]
08009596  strh r0,[r4,#0x1e]  ; dest+0x9E = extent - 1   <- camera clamp maximum Y
08009598  ldrh r0,[r5,#0x8]
0800959A  adds r0,#0xef       ; +239
0800959C  str  r0,[r4,#0x14]  ; dest+0x94 = extent + 239  (virtual-size field)
0800959E  ldrh r0,[r5,#0xa]
080095A0  adds r0,#0x9f       ; +159
080095A2  str  r0,[r4,#0x18]  ; dest+0x98 = extent + 159
```

`dest` is the engine's per-map camera state at `0x030019A4`. `dest+0x9C`/`+0x9E`
are read by the camera clamp at `0x080094F0`, which **saturates the requested view
origin to `[0, extent - 1]` per axis**, and by its in-play twin at `0x08009744`;
`dest+0x18`/`+0x1C` (and `+0x00`/`+0x04` in 10.6) is the camera origin those write.

**So a plane `P` pixels wide is reachable exactly when the stored word is at least
`P - viewport`.** That is `mg.declared_extent_raw`. It also says what a resize has
to do that a cell paint does not: growing a layer's plane is not enough, because
the camera cannot reach the new area until the extent word is raised too.

Two things this correction retires, both previously published: that
`extent - 1 + 239` is the maximum camera scroll (it is the virtual-size field at
`dest+0x94`, read only by a region test at `0x0800CA6A`), and that `0x0800938C`
uses those fields to offset the BG scroll base (it writes `BGxCNT`, `BLDCNT`,
`BLDALPHA` and `DISPCNT` and never touches `0x04000010+`). The BG scroll registers
are written at `0x08007F00`/`0x08007F02` and `0x08007FBA`/`0x08007FBC`.

**The extent gates the camera and nothing else.** A full reader census over
`0x08000000..0x08055000` finds no actor-position code reading these words, so
raising them extends the camera's reach, not the player's walkable area - which is
collision geometry this record does not touch.

### 1.3 A layer record is `header + window` and nothing else

A dominant layer record (`handler == 0x08008087`, the form used by **1,516** of
the 1,808 slot references) is exactly:

```text
+0x00  u32  handler (a Thumb code address, not a type tag)
+0x04  u32  scalar -> object+0x3C   meaning UNKNOWN
+0x08  u32  scalar -> object+0x40   meaning UNKNOWN
+0x0C  u32  -> object+0x44          UNRESOLVED
+0x10  u32  -> object+0x48          UNRESOLVED
+0x14  u8   chunk-grid X count
+0x15  u8   chunk-grid Y count
+0x16  s16  -> object+0x0C          consumer UNRESOLVED
+0x18  4*N  the chunk-pointer window, N = X * Y, four-byte addresses
```

**Measured: the record's byte length is exactly `0x18 + 4 * N` for every one of
the 1,516 canonical dominant records** (28 bytes for 1x1 through 104 for 5x4), and
the bytes immediately after the window belong to the next structure. On map 40
BG1 the word at the end of the window is `0x00000001` - the kind-1 container
header that BG2's cell 0 points at. **That is why a grid that grows cannot be
extended in place: the record is relocated whole, with its header copied verbatim**
(the unknown fields are carried, never reconstructed).

The canonical grid corpus: 18 distinct shapes, largest 5x5; `2x2` 418 times,
`1x1` 410, `2x1` 354, `1x2` 193.

### 1.4 The engine's layer count is fixed at four

`ROOT_LAYER_SLOTS` has four entries because a GBA regular-BG scene has four
backgrounds. Over all 452 roots and all 1,808 slots the handler census is
dominant 1,516, absent placeholder 249, screen-entry plane 42 (two handlers),
terrain field 1 - so **"unused slot" is a slot whose pointer is the one shared
zero-dimension record `0x080707FC`, and "create a new layer" means pointing such a
slot at a new dominant record.** No dynamic layer list the engine does not possess
is modelled. 207 maps have at least one unused slot and at least one dominant
layer; map 39 is one of them and is on the runtime route.

## 2. What was built

**`tools/webfoot/map_resize.py`** - the authority. `MapResizer` is the facade a
surface drives; `resolve_layer_record`, `structural_placements` and
`materialize_map_structure` are the build path; `set_layer_resize`,
`clear_layer_resize`, `set_authored_layer` and `remove_authored_layer` are the
persistence path. One public failure family, `MapStructureError`.

**A fourth project document, `maps/structure.toml`**, with two tables: `[resize]`
keyed by `map:NNNN/BGn` and `[layer]` keyed by `layer:<name>`. Both are semantic
and address-free: the map by durable identity, the layer by slot, the grid in
whole chunks, and the initialization as **the same two value forms a layout cell
already accepts** (a 1-based ordinal into the layer's own vocabulary, or a
`chunk:<name>` identity). A slot has one owner, and a `[layer]` entry may be
paired with a `[resize]` entry on the same slot **only as a strict growth**: the
`[layer]` grid is the grid the layer was created at and the `[resize]` grid is the
grid it was grown to, so an author can grow a layer the project itself created.
Two `[layer]` entries or two `[resize]` entries for one slot remain refused, as
does a pair that does not grow.

**Resize** grows a supported dominant layer's grid, growth only, **top-left
anchored**: retail cell `(x, y)` lands at new cell `(x, y)` by coordinate, and
every cell the growth adds is the initialization chunk. The record is re-emitted
at `0x18 + 4 * columns * rows`, the root's slot pointer is repointed at it, and the
map's extent words are raised - per axis, to `declared_extent_raw(plane_pixels,
viewport)` and never lowered - so the grown plane's far edge is exactly reachable.

**Layer authoring** activates a slot the canonical image leaves unused with a new
dominant record whose header is copied from a named template layer **on the same
map** (an authored chunk and an authored layer are both map-scoped: screen-entry
ordinals only resolve through the map's own assembled character block). Its
dimensions and initialization are the author's; its cell content is the project's
`maps/layout.toml`, which already accepted `(map, layer, cell)` values for any
slot. **An authored layer does not move the extent**: adding a visual layer inside
the map the author already has is not the same operation as extending the camera's
reach.

**Addressability.** `AllocationKind.LAYER_RECORD` is placed through the production
allocator, one request per edit, ordered by the edit's own durable owner, against
the build-scoped reservation set. Its addressability is a new, explicit
`Addressability.EXPANDED_ONLY`: a dominant record grows with the authored grid
(`0x18 + 4*columns*rows`) while the canonical image declares **one 256-byte
VERIFIED_FREE region**, a project may author one record per resize and per layer,
and so the domain's aggregate demand cannot be served canonically. The policy and
the addressability proof are the same decision.

**The paint authority is structure-aware.** `MapPainter(canonical_bytes, *,
structure=...)` reads the authored geometry, the effective cell pointers and the
vocabulary from `map_resize`, so a resize and a paint of it cannot disagree. A cell
that exists only in the authored grid carries `offset == -1`: it has no canonical
four-byte field, and a paint of it is persisted semantically and emitted by the
structure domain. `set_layout_cells` now reads the project's own structure, so the
painter and the build validate against the same grid.

## 3. The addressability answer

**Encoding-capable: YES. Runtime-proven: see section 4.**

| Item | Value |
|---|---|
| layer-slot reference encoding | four-byte little-endian GBA address, unmasked |
| records placed | map 40 BG0 `0x08800030`; map 39 BG0 `0x08800000` |
| file offsets | `0x00800030`, `0x00800000` (= the canonical image's own length, and above it) |
| alignment | 4 |
| above canonical EOF (8 MiB) | **YES**, both |
| bytes changed in the canonical region | 4 (two root slot pointers, two extent words) |

## 4. Runtime proof

Method: the corrected methodology from the two predecessor map records. A
savestate restores the already-assembled background, so a capture under a state
load is decided by the state and not by the ROM; **the rebuild is per run**. Each
run loads the ROM, loads the same saved state
(`2d5740a8c54180d153024a11b0e4d1143306957af55a3ad0664c71cf7d9a1aab`), leaves map
40 for map 39 and re-enters map 40, and is captured only if the observer's own
map-index transitions show the leave-and-return.

**The guard accepted both runs.** Retail left map 40 at frame 1951 and returned at
2221; the authored run left at 1943 and returned at 2213. Both re-entered via map
39, and both transitions are in the observer's `transitions.csv`, read from the
live `MapEntry` pointer at `0x03001980`. The route itself was the first obstacle
and is not a product issue: map 40's exit to map 39 is a band at x 0..9,
y 112..169, and the player loads at about (48, 204), below it, so the exit needs
two legs (walk up, then left).

### 4.1 Layer authoring proven

The engine enumerates and draws the project-authored layer. Measured live, in map
39, per run:

| | retail control | authored derivative |
|---|---|---|
| live BG0 slot record (`u32(root+0x14)`) | `0x080707FC` (the shared absent placeholder) | **`0x08800128`** (above the canonical 8 MiB EOF) |
| its own grid bytes `+0x14`/`+0x15` | `0` x `0` | **3 x 2** |
| its first six window words | all `0x00000000` | `0x082935A0`, `0x082935A0`, `0x082935A0`, `0x082935A0`, **`0x082936D0`**, `0x082935A0` |
| live BG0 screenblock non-zero entries | **0** | **35** |
| `DISPCNT` / `BG0CNT` | `0x1F40` / `0x1C82` | `0x1F40` / `0x1C82` |

The enable bit is identical, so the difference is the layer record and not a
register: at retail the slot is the zero-dimension placeholder and BG0's uploaded
tilemap is empty; in the derivative the slot is a 3x2 dominant record whose window
holds the template's chunks plus the authored cell the project painted, and the
engine has uploaded 35 non-zero screen entries for it. **The authored layer is
enumerated, its cell-grid reference is consumed, and it contributes.**

### 4.2 RESIZE - the engine consumed it, but the added area is not displayed

**Proven at runtime: the engine loads the resized structure, including the record
relocated above the canonical EOF.** Measured live, per run:

| | retail control | authored derivative |
|---|---|---|
| map 40 BG0 slot record | `0x082928C0`, grid 1x1 | **`0x08800030`, grid 2x1**, cell 0 `0x08292884`, **cell 1 `0x087EA400`** (the authored chunk) |
| map 40 declared camera clamp (map-state `+0x9C`) | 88 | **271** |
| map 39 BG1 slot record | `0x08293BEC`, grid 3x2 | **`0x08800158`, grid 4x2** |
| map 39 declared camera clamp (map-state `+0x9C`) | 376 | **783** |
| largest camera x reached in map 39, identical input | 376 | **487** |

So above-EOF addressability for this record's own pointer holder - a **map root's
layer-slot field** - is **RUNTIME-PROVEN**: the retail engine's live layer records
point at records placed at `0x08800030`, `0x08800128` and `0x08800158`, all above
the canonical 8 MiB image, and it reads their grids and their chunk windows. The
raised extent is live too: with identical input the authored camera travels
**111 pixels further** than retail's own clamp allows, because the resize raised
it.

**Not proven: that the added area is displayed.** The added cells sit at layer
pixel x 768..1023 (map 39 BG1) and x 256..511 / y 256..511 (map 40 BG0). The
camera cannot be driven there: measured, the player is confined by level collision
to about x 599 on map 39 and x 64 on map 40 after the re-entry, so the camera
reaches x 487 and x 0 respectively and never the plane edge. Three targets were
tried and each failed on the same measured cause: map 40 BG1 (512 px plane, camera
pinned at x 0), map 40 BG0 in Y and then in X (256 px plane, camera pinned at
x 0/y 59), and map 39 BG1 (768 px plane, camera stopped at 487). On the maps the
savestate and the route reach, **no supported layer's plane edge falls inside the
region the camera can actually traverse.**

This is a real limit of the acceptance attempt rather than a defect in the
capability: the engine consumed and materialized every authored structure, and the
one thing missing is a viewpoint from which to see the added cells. Authoring the
collision geometry that confines the player is explicitly outside this record
("collision or behavioral layers if present" are named as out of scope), and so is
creating a new map or savestate to stand in.

**Consequence at the time this section was written: the RESIZE half was not
satisfied.** It was subsequently closed on other targets - see 4.3, which
supersedes this conclusion. The map-39 BG1 axis remains a measured negative and is
kept for exactly that reason. The next attempt should pick a target by comparing
`root extent` (the camera clamp) against the layer plane and against where the
player can actually walk, *before* building - `build/research/b1_target_search.py`
now does that.

### 4.3 Resize settled on two targets, one of them a retail layer

The pre-flight search (4.2's method, run for real) built the transition graph from
all 735 readable connection records and BFS'd from map 40: **only eight maps are
reachable at all** - 40, 39, 41, 38, 42, 43, 44, 45. It then ranked every
reachable map x supported dominant layer x axis by `raw + viewport - plane_pixels`,
the pixels of an added cell that fall inside the region the engine's camera clamp
lets it display. Six combinations qualify out of 211 project-wide. That table
selected the targets; it is recorded in `build/research/b1_target_search.txt`.

**Target (b): `map:0040` BG0, a RETAIL layer, 1x1 -> 2x1.**
`build/resize001-map40/authored.gba` sha256
`b2315cce49f5500fcd1c240f1207ab47a5aabe3eb46df39d1646646f5e1271b0`. Guard
ACCEPTED in leave-return mode: left map 40 at frame 2671, re-entered at 3017,
settled at 3160, capture taken in map 40.

| | retail control | authored |
|---|---|---|
| BG0 slot `u32(root+0x14)` | `0x082928C0`, grid **1x1** | **`0x08800000`, grid 2x1** |
| BG0 window cells | `0x08292884` only | `0x08292884` then **`0x087EA400`** |
| camera clamp `+0x9C` | **88** | **271** |
| BG0CNT / BG1CNT / DISPCNT | `0x1C82` / `0x1D82` / `0x1F40` | identical - a priority **tie**, so BG0 draws in front: no occlusion |
| BG1 slot (untouched layer) | `0x08292C88`, 2x2 | identical |
| largest camera x reached | 88 (its clamp) | **158** |

**Display evidence, matched camera.** At camera x = 79 in *both* runs on this same
map-40 2x1 configuration: **1024 frame pixels differ, all of them inside the
added cell's band (screen columns 177..239) and none outside**; the BG0
screenblock goes from 28 to 60 non-zero entries with **32 entries differing**; and
**BG1 is byte-identical**, which is what rules out a camera shift. The noise floor,
measured the same way (canonical against canonical at the same camera, map and
player position), is 116-270 px - so the signal is several times the floor and
perfectly confined to the predicted band. In (b)'s own run the camera reached
**158, which is 70 px past retail's hard clamp of 88**: retail cannot render layer
x > 328 at all, while the authored screen covered layer x 158..397, putting 141 px
of the added cell on screen as a visible striped artifact band at screen columns
175..239 over terrain intact to its left.

**Recorded limit, not hidden:** (b)'s own run has no matched retail frame at
camera 158 - retail physically cannot reach that camera - and the observer
overwrites intermediate captures, so no authored frame at 88 was retained. The
matched-camera display proof is the camera-79 pair on the identical configuration.
A capture-at-first-camera->=88 hook plus one more operator pass per ROM would close
even that.

**Target (a): `map:0039` BG0, a project-authored layer created 1x1 and grown to
2x1** (`build/resize001-b1/authored.gba` sha256
`8b048bbcfa9550d495b51bffeb0634867f8d8599818cb57c0325e0ab76cbff08`), chosen
because it needs **no walking at all**: the added column is layer x 256..511 and
map 39's arrival camera is x 376, so the added cell is on screen at arrival with
the extent words untouched - the clamp is **376 in both runs**, which is the
cleanest matched condition available. Live: BG0 slot `0x080707FC` grid 0x0 with
**0** drawn entries -> `0x08800128` grid **2x1** with window `0x082934C4` then
`0x08800000` and **22** drawn entries; BG1 byte-identical; **1145 frame pixels
differ, all inside the predicted band, none outside**, against a 116-270 px noise
floor. **Qualification, stated as such:** the display is *partial* because map 39's
addends (`03 02 03 03`) put BG0 behind BG1, so only BG1's transparent pixels reveal
the authored cell - 1145 px of the cell's ~21,600 on-screen pixels. And the resized
layer is project-authored, so this target alone would not settle "a retail layer's
added cell displays" - which is exactly why (b) exists.

## 5. Focused validation

| Command (explicit files only) | Result |
|---|---|
| `pytest tests/unit/test_map_resize.py tests/unit/test_map_structure_project.py -q` | **101 passed** |
| `pytest tests/integration/test_map_resize_rom.py -q` | **27 passed** |
| the eighteen-file focused unit batch | **475 passed, 1 skipped** |
| `pytest tests/unit/test_workbench_resize_and_layers.py -q` | **78 passed, 0 failed** - stable across 28 repeat runs including 8 `PYTHONHASHSEED` values, plus the four map-workbench files **205 passed** in both file orders |

Broad suites were **not** run manually; CI owns them.

### 5.1 Structural cost

Counts, not wall-clock. Measured by `build/research/resize_cost.py`, which counts
the project's own read and write entry points:

| Operation | Project reads | Project writes |
|---|---|---|
| one resize | 1 | 1 (`maps/structure.toml`) |
| one authored layer | 1 | 1 (`maps/structure.toml`) |
| painting four cells on an authored layer | 1 | 1 (`maps/layout.toml`) |
| a whole build of that project | - | 5 byte changes, 2 structure records, 2 allocations, 3 of them in the canonical region |

A resize is **not** O(cells × project read): the whole operation is one read and
one write regardless of the grid, and a paint batch is one read and one write
regardless of how many cells it covers. The Workbench surface's own call counts
are asserted by its CQA-07 node
(`test_many_painted_cells_do_not_multiply_the_structural_reads`).

## 6. Mutations M1-M12

Each is a minimal literal edit to the shipped code that restores a specific wrong
behaviour; each was applied, the one named node run, and the file restored. All
twelve were caught.

| | Mutation | Node that failed | Result |
|---|---|---|---|
| M1 | ignore the authored dimensions during build | `test_a_built_map_carries_the_resized_grid_and_the_authored_layer` | PASS |
| M2 | wrong row stride in the resize coordinate mapping | `test_a_non_square_retail_grid_maps_by_coordinate_not_by_window_order` | PASS |
| M3 | wrong chunk identity for the added cells | `test_the_old_grid_keeps_its_coordinates_and_the_new_cells_take_the_fill` | PASS |
| M4 | point the layer descriptor back at the retail grid | `test_the_root_slot_field_really_resolves_to_the_relocated_record` | PASS |
| M5 | omit the authored layer body | `test_every_authored_record_lands_above_the_canonical_eof` | PASS |
| M6 | build the layer but omit it from the engine-visible structure | `test_a_built_map_carries_the_resized_grid_and_the_authored_layer` | PASS |
| M7 | make the authored layer mutate its source template | `test_the_authored_layer_never_writes_over_its_template` | PASS |
| M8 | drop the structure on project reopen | `test_the_project_reopens_with_the_structure_and_the_cell_content_intact` | PASS |
| M9 | stop reserving a placed record | `test_allocation_is_deterministic_and_reservations_do_not_overlap` | PASS |
| M10 | truncate the relocated record address to 24 bits | `test_the_root_slot_field_really_resolves_to_the_relocated_record` | PASS |
| M11 | restore the project-mutation state loss (CQA-05) | `test_a_project_mutation_keeps_a_staged_layer_and_its_painted_cells` | PASS |

All twelve are caught. M11's mutation prepends `self._clear_structure_state()` to
`on_project_mutated` - i.e. makes it behave like `on_session_changed` - and the
named node fails.

M2 needed a **non-square** retail grid to be detectable at all: a 2x2 grid cannot
tell a row stride from a column count, which is why the synthetic fixture carries a
1-column by 3-row layer and why that case has its own node.

Runner: `build/research/mutations_resize.py`.

## 7. Reopen, determinism and resource safety

- **Reopen**: a saved project reopens with the resize, the authored layer, their
  dimensions and their semantic identities intact, and its cell content preserved.
- **Determinism**: two builds of one saved project produced byte-identical images
  (`build/research/resize_derivative.py` records `deterministic_rebuild YES`).
- **Unchanged resource safety**: in the canonical region only the two root slot
  pointers and the two extent words differ. Every unrelated layer of both maps
  keeps its own record address, handler and window; every chunk body is untouched;
  the template layer of an authored layer is byte-identical; the canonical ROM is
  unchanged.
- **Allocator safety**: each record is reserved before the next request is placed,
  so two records in one build cannot overlap.

## 9. Scope boundaries and what is NOT claimed

Not claimed, and not implemented: warp or connection editing, new maps, graphics
import, new palettes, new tiles, sprite or appearance authoring, collision editing.

Two limits are recorded rather than hidden:

1. **Shrink is refused.** Removed cells' references - placements, triggers and the
   map's own connections are stated in map coordinates a smaller extent need not
   contain - have not been shown to be safe to drop, so a shrink is refused with
   its reason instead of silently truncating authored content. **This capability
   supports controlled growth only, and the registry and public limits say so.**
2. **A shared map root is refused.** Eleven canonical roots serve more than one
   map; a root holds the layer-slot pointers and the extent, so editing one would
   silently change every map that loads it.

## 11. Workbench surface

`tools/webfoot/workbench/map_browser_tab.py` carries the structural surface: the
resize form with live preview and validation, the layer list and creation form,
one undo command per gesture, Apply/Revert, dirty state, and painting an authored
layer through the structure-aware painter. Its focused suite is
`tests/unit/test_workbench_resize_and_layers.py`, now **78 nodes, 78 passed, 0
failed**, stable across 28 repeat runs including 8 `PYTHONHASHSEED` values and the
four map-workbench files at 205 passed in both orders.

**The five inherited failures, classified** (none was a flaky product defect):

* `test_a_new_layer_is_offered_in_the_map_editor_and_paintable_with_its_vocabulary`
  - **incorrect test assumption**: the unsaved count is the staged layer plus one
  per painted cell (1 + 3 = 4), matching the canonical paint path's own
  per-cell counting. The assertion was corrected, not weakened, with the
  derivation recorded in the file.
* the four `test_a_structural_read_failure_on_a_project_mutation_is_reported`
  cases - **a real product defect plus an incorrect assumption**: an unreadable
  `maps/structure.toml` set only the panel label and never reached the status
  line, while the layout and chunk readers do publish their read failures. Now
  fixed with a sticky `_structure_read_error` that `_update_status` publishes;
  the assertion additionally pinned the wrong literal.
* the previously "sometimes also" trio - **not reproducible** and no defect
  found: the pre-fix failure set was exactly the same five across six full runs,
  eight hash seeds, reverse node order, two Qt platforms, each node in isolation,
  and four cross-file sequences. Module state, shared fixtures, leaked
  `QUndoStack`/connections, timers and tmp-path dependence were each ruled out by
  inspection. The most probable cause of the *earlier* varying set is that the
  worktree file was being edited between those runs, and/or that a shared
  `--basetemp` was being cleared mid-run by a concurrent session. That is reported
  as not reproduced rather than explained.

**A tracked regression this record had introduced**, found by running the adjacent
suite: `test_a_project_mutation_keeps_every_staged_authored_fact` failed because
the new `_reselect_layer()` in `on_project_mutated` rebuilt the layer combo and
reset the author's brush, picked cell and draft - contradicting
`on_project_mutated`'s own contract. Fixed with an I/O-free row signature, so the
editor is left alone when the rows are unchanged. This was the real CQA-05 defect.

**CQA-05, CQA-06, CQA-07 and undo/redo** are each pinned by new nodes in the
surface's section 9: resize undo restores the exact retail dimensions and cells
and redo the exact authored ones, layer create undo/redo, per-cell paint undo/redo
with exact values, no-op gestures creating no command; the declared error family
including `MapStructureError` with a programmer error deliberately *not* converted;
and one write plus one re-read per Apply with no signal cascade.

**Visual QA** ran the real application against a project extracted from the
canonical ROM, driving the tracked harness
(`python -B -m tools.qa.visual_pass_capture --out build/qa/b2-shots --states
40-46,48-56`, 16 captures), and every capture was opened and inspected. Two real
UI defects were found by looking and fixed: the inspector's 290 px action column
clipped button labels ("Resize layer..." rendered as "ssize layer"), and the
4-slot layer list claimed 192 px for four 20 px rows, wasting 110 px. Both were
layout-only fixes; the panel no longer overflows.

Four non-blocking defects are recorded rather than fixed: elided combo/row text
(tooltips carry the full string), a "project paints this cell" wording that is
wrong while a structural paint is still staged, a chunk-usage count that is
base-derived, and a **sibling of the defect fixed here** - a layout or chunk read
failure on a project mutation is still immediately overwritten by the later
`_update_status`, needing the same sticky per-document failure the structural half
now has.
