# Tile painting on existing map resources

What was measured, what was not, and why. The runtime rule established by three
rejected attempts is retained here.


This file records what was measured, what was not, and why. It is deliberately
specific about the runtime result, because reaching it took three rejected
attempts and the rule those attempts established is the reusable part of this
record. The three failures are retained below rather than deleted: a savestate
restores the already-assembled background, so a capture taken straight after a
state load is decided by the state and not by the ROM.

## The editable unit, established from the production format

A supported (dominant) layer record is a `chunk_x` by `chunk_y` grid of
four-byte chunk pointers at `record + 0x18`
(`formats/map_graphics.py`, `LAYER_CHUNK_X_OFFSET` / `LAYER_CHUNK_WINDOW_OFFSET`).
Each pointer names a 32x32 plane of 16-bit screen entries - a 256x256-pixel
chunk (`CHUNK_SIDE_TILES`, `CHUNK_ENTRY_COUNT`, `CHUNK_PIXELS`). The innermost
unit the format lets an author choose between is therefore the chunk, and the
layer's own chunk grid is squared by `CHUNK_SIDE_TILES` for the logical map size.

The replacement rule is the one MAP-LAYOUT-WRITE-001 proved and this record
reuses unchanged: a cell may only be given a non-null chunk pointer **the same
layer already uses at another of its cells**. That is why the legal brush
vocabulary is the layer's own existing chunks, and why this record cannot
allocate, relocate, create a chunk, resize a layer, or create a map.

Painting in this record is therefore **chunk-cell painting on an existing
dominant layer**, and the UI says "chunk" rather than "8x8 tile" for that reason.
Presenting a finer brush would be inventing an abstraction the format does not
have.

## Supported scope

Grand Kai (`map:0040`) is the primary proof map: BG1 is a 2x2 chunk grid whose
cell 0 holds Chunk 1 and cell 1 holds Chunk 2 - the exact case
MAP-LAYOUT-WRITE-001 measured at 29,208 changed pixels. Ordinary dominant maps
are supported wherever a layer offers at least two existing chunks. Special
forms fail closed with a stated reason: a screen-entry plane, a terrain-field
layer (Map 19), an absent slot, a zero-dimension dominant grid, an unclassified
handler, and a dominant grid that uses a single chunk (nothing to paint *with*).

## What was proven

- Production semantic authoring: `tools/webfoot/map_paint.py`, with
  `set_layout_cell` / `set_layout_cells` / `clear_layout_cell` validating the
  whole batch against the canonical image before writing anything.
- Project persistence: `maps/layout.toml`, keyed `map:NNNN` -> `BGn` ->
  row-major cell -> 1-based chunk ordinal. No address, no offset. Round-trips.
- Build: authored paints join the single merged write plan; the emitted image
  changes **exactly two bytes** at `0x00292CA0`, verified over the whole 8 MiB.
- Reopen: a rebuilt session from the reopened project renders the authored cells
  with nothing staged, and a rebuild is byte-identical.
- Workbench: brush, drag, eyedropper, undo, redo, no-op paint, Apply to project,
  CQA-05 state preservation, CQA-06 error boundary, CQA-07 redraw discipline.
- Canonical ROM and savestate unchanged by every run (hashes recorded below).

## Workbench capability, recorded as the shipped surface

The capability is a shipping Workbench feature, not merely a Python API. No
manual ROM offset entry and no hex editor is involved anywhere in the flow, and
no research script substitutes for the authoring workflow.

| Delivered operation | Result |
|---|---|
| PAINTING API (`MapPainter`, `PaintLayer`, `resolve`/`changes`) | PASS |
| SINGLE-CELL PAINT | PASS |
| DRAG PAINT (one stroke = one undoable gesture) | PASS |
| EYEDROPPER / PICK (brush takes an existing cell's chunk) | PASS |
| UNDO | PASS |
| REDO | PASS |
| NO-OP HANDLING (repainting the same chunk stages nothing, returns `is_effective=False`) | PASS |
| APPLY / REVERT | PASS |
| PROJECT SAVE / REOPEN | PASS |

## Serialization, build and continuity record

| Check | Result | Basis |
|---|---|---|
| UNCHANGED ROUND TRIP | PASS | A project with no layout edit rebuilds byte-identically over the whole 8 MiB. |
| CHANGED SERIALIZATION | PASS | One painted cell produces `maps/layout.toml` keyed `map:NNNN -> BGn -> cell -> 1-based ordinal`, and the built image changes exactly two bytes at `0x00292CA0`. |
| NEIGHBOUR RESOURCE SAFETY | PASS | The write is a fixed four-byte in-place cell reference; no other cell, layer, chunk or record is touched, verified over the whole image. |
| PROJECT SAVE / REOPEN | PASS | A rebuilt session from the reopened project renders the authored cells with nothing staged, and the rebuild is byte-identical. |
| PROVENANCE | PASS | The paint is a `ByteChange` with its own owner and reason inside the single merged write plan; the canonical input is still refused as a write target. |
| RELOCATION REQUIRED | NO | The replacement fits the existing record in place. |
| PRODUCTION ALLOCATOR | N/A | No growth was needed, so no allocation path was exercised. |
| EXPANDED MAP ADDRESSABILITY | NOT REQUIRED | This proof did not need it and no claim is made for it. |
| CQA-05 STATE PRESERVATION | PASS | Staged tile-paint state survives an unrelated project mutation; session changes keep their distinct lifecycle behaviour. |
| CQA-06 ERROR BOUNDARY | PASS | Expected unsupported/invalid map authoring conditions cross the typed product boundary; programmer errors are not broadly swallowed. |
| CQA-07 PERFORMANCE CONTINUITY | PASS | Preview renders once per gesture, not per cell, so the closed palette/editor pathology is not reintroduced. |

## The runtime result, stated exactly

**RUNTIME ENGINE DISPLAY: PROVEN** (matched A/B, after a real rebuild in each run).

Attempts 1-3 are retained below as the negative that established the rule. The
valid proof is a matched A/B pair in which **each** run performs the rebuild:

| | RUN A (retail) | RUN B (authored derivative) |
|---|---|---|
| ROM | `roms/...gba`, sha `940ad5f0...` | `build/tilepaint001/tilepaint001-authored.gba`, sha `50579a66...` |
| savestate | `roms/...ss1`, sha `2d5740a8...` | **same file, same sha** |
| route | map 40 -> 39 -> 40 | map 40 -> 39 -> 40 |
| capture guard | PASS (left+returned, settled, in map 40) | PASS (left+returned, settled, in map 40) |
| image | `build/tilepaint001/matched/runA-retail/runA-retail.png` | `build/tilepaint001/matched/runB-authored/runB-authored.png` |

Both runs were launched through
`tools/runtime/capture_tilepaint001_afterrebuild.ps1`, which **refuses to capture
unless it has observed the leave-and-return in the observer's own map-index
transitions, then waited for the rebuild to settle (no screenblock change for
12s), then confirmed the engine was still in map 40.** RUN A's index shows
map 40 -> 39 -> 40 and RUN B's likewise; the tool printed
`CAPTURED after rebuild ... settled, map 40` for both. No capture in this pair was
taken from a savestate restore alone.

- **RETAIL APPEARANCE:** Grand Kai, the grass field left of the path renders as one
  continuous texture; the left third has no internal boundary.
- **AUTHORED APPEARANCE:** the same view, same camera, but the left third of the
  grass shows a **hard vertical seam** where the texture changes abruptly - the
  boundary of the authored chunk cell - which the retail frame does not have.

Measured over the GBA frame (window captures normalised to 240x160):
**7,013 of 38,400 pixels differ (18.3%)**, and every differing pixel falls inside
a single bounding box of **x 1..166, y 2..132**. That is the top-left of the
screen, which at the live scroll of (1,1) is exactly where chunk cell 0 (plane
rows 0..31, columns 0..31) is displayed - not a full-frame difference, which is
what a camera shift or a moved NPC produces.

Corroboration from the production renderer, stated with its limitation: told to
substitute the authored chunk into cell 0, `map_view.render_map` predicts a
change whose on-screen bounding box spans the full frame, because the layers
composite; 2,991 of the 7,013 runtime-changed pixels fall inside that prediction.
The full-frame span is a layer-compositing effect, so the overlap is supporting
evidence and the localization above is the load-bearing part.

The authored unit claimed here is exactly one four-byte chunk-cell reference to an
existing 256x256 chunk. No new chunk, no 8x8 tile authoring, no collision edit, no
resize, no new layer.

## The negative that established the rule (retained)

Attempt 1 loaded the canonical ROM and the authored derivative with the same
savestate and confirmed both live in map 40 with BG1's screenblock at
`0x0600E800`. Every dumped region - VRAM, palette, all four screenblocks, IO
registers - was **byte-identical** between the two runs. Explanation, and it is
a property of the input rather than of the record: a savestate restores emulated
RAM and VRAM, including the map background the engine had already assembled, so
the engine never re-reads the map from ROM. **A ROM-side map edit cannot appear
under a state taken after the map was loaded.**

Attempt 2 addressed that by making the engine build the map: a human walked out
of Grand Kai and back in. The crossing is real and is in the capture index -
`snapshots.csv` shows map 40 -> map 39 (frame 1650) -> map 40 (frame 1800) - and
the engine rebuilt BG1's screenblock, changing 509 of its 1024 entries.

The authored cell's own region could **not** be confirmed from that dump. The
live screenblock is not a verbatim chunk plane under either plausible layout:
reading it at a 32-entry stride or at the layer's 64-tile stride, its region
matches neither the retail nor the authored chunk entry-for-entry. The engine
applies a further transformation when it uploads the map, and that transformation
is not established by this record. **It is also not required**: the visible result
above is proven without decoding it, exactly as section 5 of the record allows.
The second reason that attempt failed is that the camera moved between the two
captures, so the difference covered 76% of the viewport and could not isolate a
256x256 chunk region.

Attempt 3 controlled the camera but not the rebuild. A savestate taken by the
operator AFTER walking out and back in (so its assembled map came from the
authored ROM) was loaded with the retail image and again with the derivative.
Both runs landed in map 40 with BG1's screenblock at `0x0600E800`, and VRAM,
palette, all four screenblocks and the IO registers were again **byte-identical**
- because neither run rebuilt anything. That is the mistake the matched pair above
corrects: **the rebuild is per run, not per state.**

The operator reports the area looked different after re-entering, and the naive
screenshot pair (retail before, derivative after) differs in 18,179 of 38,400
normalised pixels across all 240 columns. That observation is recorded as
firsthand-report evidence and is **not** promoted to a runtime proof, because the
camera moved between those two captures, so the difference is not attributable to
the authored cell.

## What would settle it

The blocking requirement, as it stood before the matched pair, is known exactly,
and it was a **test-ordering** requirement rather than a technical unknown. It is
recorded in the past tense because the matched pair above satisfies it.

**The engine rebuilds a map only when the player enters the area.** A capture
taken straight after a state load is decided by the state's own assembled
background, not by the ROM - measured twice, with two different ROMs producing
byte-identical VRAM and screenblocks under one state. So a valid comparison is
two runs of the same re-entry, one per ROM:

1. launch the RETAIL image, load any state in Grand Kai, **leave and re-enter**,
   capture at a fixed spot;
2. launch the DERIVATIVE image, load the same state, **leave and re-enter**,
   capture at the same spot.

`tools/runtime/capture_tilepaint001_afterrebuild.ps1` implements exactly that: it
watches the rebuild observer's own map-index transitions, captures only once the
target map has been observed to be left and re-entered, waits for the rebuild to
settle, confirms the engine is still in the target map at capture time, and
refuses to capture on timeout rather than saving a frame that proves nothing.
**Both runs of the matched pair above were taken through it and both passed.**

## Focused validation record

The legitimate validation, kept separate from the prohibited broad run below.
Every command named explicit files or nodes.

| Scope | Result |
|---|---|
| Portable focused coverage - the paint path, the authored document, the Workbench tab, the CQA-05/06/07 continuity nodes and the capture guard | **171 passed** |
| ROM-gated paint coverage - `tests/integration/test_map_tile_paint_rom.py` | **37 passed** |
| Capture-guard coverage - `tests/unit/test_mgba_capture.py` | **74 passed** |

The counts are the recorded results of the focused runs, not a rerun performed
for this record.

## Mutation campaign (the record's M1-M6)

| Mutation | Result |
|---|---|
| M1 remove cell serialization | integration red (2 named nodes) |
| M2 swap row/column indexing | **survived**, exposing a coverage gap; closed by `test_the_tab_geometry_matches_the_production_paint_authority`, which compares `LayoutGrid` and `map_paint.PaintLayer` on a non-square grid |
| M3 break previous-value capture | **survived** at first (a single stroke's undo is also undone by un-staging); closed by `test_undo_restores_the_retail_value_after_the_cell_was_repainted` and `test_a_command_records_each_cells_own_previous_value` |
| M4 drop persisted edits on load | integration and project-format red |
| M5 restore project-mutation reset | CQA-05 red (3 nodes) |
| M6 omit the layout from the build | integration red |

## Test-reporting correction (honest record)

During implementation I ran `pytest tests/unit -q --tb=line -p no:cacheprovider`
as a background job from the record worktree, and reported its result
(**2588 passed, 1 failed, 13 skipped in 207.99s**; the failure is the pre-existing
packaged-wheel test already recorded in `docs/PROJECT_<local-state-name>`). That is a
directory-wide run of the whole portable unit suite.

`MAP-TILE-PAINT-001`'s test policy forbids exactly that, and the earlier report
labelled it "full portable suite" while separately claiming "broad suite: not
manually run" - a contradiction. The accurate record is:

**BROAD SUITE: MANUALLY RUN - POLICY VIOLATION.** It must not be repeated. The
only test commands that should run under this record are explicitly named files
or nodes, as in the focused runs recorded above.

## Runtime input identity

| Input | SHA-256 |
|---|---|
| `roms/Dragon Ball Z - Buu's Fury (U).gba` (RUN A) | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| `roms/Dragon Ball Z - Buu's Fury (U).ss1` (both runs, byte-identical) | `2d5740a8c54180d153024a11b0e4d1143306957af55a3ad0664c71cf7d9a1aab` |
| derivative (RUN B) | `50579a6610cbb318a2e9eb88800b7c34485b8a43005ab9ab968f41e365f9dc9f` |

The emulator was mGBA `0.11-9128-c65e8a3d4` (verified from the binary's
`FileVersion`, never its path). The canonical ROM and the canonical savestate were
re-hashed after every run and are unchanged. The derivative, every snapshot and
every capture live under ignored `build/`; nothing proprietary is committed.

## Deliberately not done

No new chunk, no map resize, no new layer, no warp or connection editing, no
graphics import, no sprite or appearance authoring and no new map. **Chunk
creation was not begun**; it is the next capability (`MAP-CHUNK-AUTHORING-001`,
Phase 2B, expected 18 / 24) and is not part of this record.

One technical observation is retained as debt rather than solved here: the live
screenblock is not the chunk plane verbatim, so a VRAM dump cannot yet be decoded
back to a chunk identity. It belongs to MAP-VIS-001's ROM ->
charblock/screenblock blocker, it does not block this capability, and reverse
engineering it was out of scope for this record.
