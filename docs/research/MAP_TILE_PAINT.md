# MAP-TILE-PAINT-001 evidence record

Ticket: tile painting on existing map resources. Baseline
`fb20e06e070ae72fadf91af6bf07be6b7467906c`. Worktree
`<ticket-worktrees>\map-tile-paint-001`, branch
`ticket/map-tile-paint-001`.

This file records what was measured, what was not, and why. It is deliberately
specific about the runtime result, because that is the one acceptance criterion
this ticket does **not** satisfy.

## The editable unit, established from the production format

A supported (dominant) layer record is a `chunk_x` by `chunk_y` grid of
four-byte chunk pointers at `record + 0x18`
(`formats/map_graphics.py`, `LAYER_CHUNK_X_OFFSET` / `LAYER_CHUNK_WINDOW_OFFSET`).
Each pointer names a 32x32 plane of 16-bit screen entries - a 256x256-pixel
chunk (`CHUNK_SIDE_TILES`, `CHUNK_ENTRY_COUNT`, `CHUNK_PIXELS`). The innermost
unit the format lets an author choose between is therefore the chunk, and the
layer's own chunk grid is squared by `CHUNK_SIDE_TILES` for the logical map size.

The replacement rule is the one MAP-LAYOUT-WRITE-001 proved and this ticket
reuses unchanged: a cell may only be given a non-null chunk pointer **the same
layer already uses at another of its cells**. That is why the legal brush
vocabulary is the layer's own existing chunks, and why this ticket cannot
allocate, relocate, create a chunk, resize a layer, or create a map.

Painting in this ticket is therefore **chunk-cell painting on an existing
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

## The runtime result, stated exactly

**RUNTIME ENGINE DISPLAY: NOT PROVEN.**

Attempt 1 loaded the canonical ROM and the authored derivative with the same
savestate and confirmed both live in map 40 with BG1's screenblock at
`0x0600E800`. Every dumped region - VRAM, palette, all four screenblocks, IO
registers - was **byte-identical** between the two runs. Explanation, and it is
a property of the input rather than of the ticket: a savestate restores emulated
RAM and VRAM, including the map background the engine had already assembled, so
the engine never re-reads the map from ROM. **A ROM-side map edit cannot appear
under a state taken after the map was loaded.**

Attempt 2 addressed that by making the engine build the map: a human walked out
of Grand Kai and back in. The crossing is real and is in the capture index -
`snapshots.csv` shows map 40 -> map 39 (frame 1650) -> map 40 (frame 1800) - and
the engine rebuilt BG1's screenblock, changing 509 of its 1024 entries.

The authored cell's own region could **not** be confirmed from that dump. Two
checks were run and neither settled it:

- The live screenblock is not a verbatim chunk plane under either plausible
  layout: reading it at a 32-entry stride or at the layer's 64-tile stride, its
  region matches neither the retail nor the authored chunk entry-for-entry. The
  engine clearly applies a further transformation when it uploads the map, and
  that transformation is not established by this ticket.
- The captured frames differ across 76% of the viewport, because the camera
  moved between the two captures; the difference is dominated by scrolling and
  cannot isolate a 256x256 chunk region.

So: the engine **did** rebuild the background from the authored ROM, and the ROM
change is byte-exactly the intended one, but **this ticket does not demonstrate
that the authored cell is what the engine displayed**. Reporting otherwise would
be claiming a runtime proof from an instrument that did not resolve it.

Attempt 3 controlled the camera, which attempts 1 and 2 did not. A savestate
taken by the operator AFTER walking out and back in (so its assembled map came
from the authored ROM) was loaded with the retail image and again with the
derivative. Both runs landed in map 40 with BG1's screenblock at `0x0600E800`,
and VRAM, palette, all four screenblocks and the IO registers were again
**byte-identical**. That is the cleanest form of the negative: the state supplies
the assembled background regardless of which ROM is running, so this instrument
cannot distinguish the two ROMs at all.

The remaining honest statement is narrow and it is the one the evidence record
stands on: **the authored layout is proven at the ROM, project and build level,
and is NOT proven to reach the engine display.**

The operator reports the area looked different after re-entering, and the naive
screenshot pair (retail before, derivative after) differs in 18,179 of 38,400
normalised pixels across all 240 columns. That observation is recorded as
firsthand-report evidence and is **not** promoted to a runtime proof, because the
camera moved between those two captures, so the difference is not attributable to
the authored cell.

## What would settle it

One of:

1. A save file that boots into Grand Kai (so the engine builds the map from ROM
   on its own), plus a paired retail capture from the same player position; or
2. A savestate taken *before* the map is assembled, so the load itself is the
   build; or
3. The engine's map-upload transformation, so a live screenblock dump can be
   decoded back to the chunk that produced it.

The first is the cheapest and is a human input, not an engineering task.

## Mutation campaign (the ticket's M1-M6)

| Mutation | Result |
|---|---|
| M1 remove cell serialization | integration red (2 named nodes) |
| M2 swap row/column indexing | **survived**, exposing a coverage gap; closed by `test_the_tab_geometry_matches_the_production_paint_authority`, which compares `LayoutGrid` and `map_paint.PaintLayer` on a non-square grid |
| M3 break previous-value capture | **survived** at first (a single stroke's undo is also undone by un-staging); closed by `test_undo_restores_the_retail_value_after_the_cell_was_repainted` and `test_a_command_records_each_cells_own_previous_value` |
| M4 drop persisted edits on load | integration and project-format red |
| M5 restore project-mutation reset | CQA-05 red (3 nodes) |
| M6 omit the layout from the build | integration red |

## Runtime input identity

| Input | SHA-256 |
|---|---|
| `roms/Dragon Ball Z - Buu's Fury (U).gba` | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| `roms/Dragon Ball Z - Buu's Fury (U).ss1` | `2d5740a8c54180d153024a11b0e4d1143306957af55a3ad0664c71cf7d9a1aab` |

Both were re-hashed after every run and are unchanged. The derivative and every
snapshot live under ignored `build/`; nothing proprietary is committed.

## Capability

**CAPABILITY: NOT SHIPPED.** The registry stays at **16 / 24**. EDIT / TILE
PAINTING cannot advance while the engine-display criterion is unproven, however
complete the authoring, persistence, build and reopen evidence is.
