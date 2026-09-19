# ASSET-EXPORT-MAP19-001 - provenance for map 19's terrain-field layer

Narrow record for one layer: map 19, root `0x082AD8BC`, slot `+0x1C`, record
`0x082ABF00`, handler `0x080088BD`. It was the last
`static_graphical_assembly_unresolved` reference in the export. This document
records the engine observation, the project interpretation and the export
consequence for recovering its assembly. The full handler census is in
[`ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md`](ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md);
it is not repeated here.

## 1. Identity

```text
MAP:           19
ROOT:          0x082AD8BC
SLOT:          +0x1C  (layer slot 2)
RECORD:        0x082ABF00
HANDLER:       0x080088BD
GRID:          +0x04 = 0x0E (14), +0x05 = 0x0A (10)
CONTAINERS:    140 consecutive u32 at +0x08, 0x0829F814 .. 0x082ABDF4
CELL:          0x400 declared decoded bytes each, all 140 decoding to 1024
```

The record's own cell grid is **14 x 10 = 140**, and 140 is exactly the length of
the container pointer run: the word after the last pointer (`+0x238`) is
`0x00000001`, not a pointer. The root's slots are `+0x14 -> 0x0829F6E4` (slot 0),
`+0x18 -> 0x0829F808` (slot 1), `+0x1C -> 0x082ABF00` (slot 2) and
`+0x20 -> 0x080707FC` (slot 3, the shared absent placeholder).

On this record `+0x14` is **not** a grid: the u32 at `+0x14` is `0x0829FB30`, the
fourth container pointer of the same run, so `+0x14`/`+0x15` = `0x30`/`0xFB` read
as `48`/`251`. That is why the exporter publishes `cell_grid_*` for this form and
no `chunk_*` key at all.

## 2. ENGINE OBSERVATION

Entry `0x080088BC`:

```text
080088BC  push {r3, lr}
080088BE  movs r0, #0
080088C0  bl   0x080080C0        ; r1 = the record
080088C4  pop  {r3, pc}
```

Constructor `0x080080C0` (Capstone 5.0.7, Thumb):

* allocates `0x27A0` bytes = `0x3A0 + 9 * 0x400`: a header plus a nine-slot
  resident cache of `0x400`-byte cells;
* stores the type word `0x08049C84` at `+0x00` and the record at `+0x04`;
* fills `object + 0x08 + 4*i` (the nine slot buffer pointers) and
  `object + 0x2C + 4*i` with `0xFF` (slot residency, "no cell") for `i = 0..8`;
* reads the record's grid product and eagerly loads while it is at most 9:
  `0x08008122 ldrb r6,[r0]`, `0x08008124 ldrb r0,[r0,#1]`,
  `0x08008126 muls r6,r0,r6`, `0x08008128 cmp r6,#9`, then per cell
  `0x08008148 bl 0x0803D940` with the destination
  `object + 0x3A0 + i*0x400` (`movs r7,#0x1d / lsls r7,r7,#5` gives `0x3A0`);
* sets `DISPSTAT` bit 1 (`0x04000200`) and clears `0x04000022`/`0x04000026`
  (`BG2PB`/`BG2PD`).

Driver `0x08008598` (through `0x080086D6`):

* `0x080085B4 ldrb r0,[r0,#5]` (grid_y) and `0x080085E4 ldrb r3,[r3,#4]` (grid_x)
  wrap the viewport's chunk coordinates into the record's grid, then
  `0x080085E8 muls r5,r3,r5` / `0x080085EA adds r0,r5,r0` give the cell index
  `wrapped_y * grid_x + wrapped_x` - the raster order of a `grid_x`-wide grid;
* it walks a 3x3 window of nine cells (`0x080085F8`..`0x080086C2`), decompressing
  a required cell through `0x0803D940` into the stack buffer at `sp+4`
  (`0x080086A4`) and copying it into the resident slot with `0x08049138` at a size
  of `1 << 10` = `0x400` (`0x080086AE`/`0x080086B2`);
* it stores the resolved window origin at `object + 0x50`/`+0x54`.

Blitter `0x08008192` (through `0x08008596`): reads the viewport from the state
object, splits it into a clipped span, and per iteration programs a DMA
descriptor at `0x040000D4` (`DMA3SAD`; count `0x040000DC`, control `0x040000DE`).
Nine structurally identical blocks do this; the destination base literal is at
pool `0x080084A8` / `0x08008830`:

```text
0800823A  ldr  r6, [pc, #0x26c]    ; = 0x0600F000
08008268  lsls r6, r6, #0xf
0800826A  lsrs r6, r6, #0x10       ; count = ((32 - m) * 2) >> 16 = (32 - m) / 2
0800826E  str  r6, [r7]            ; DMA source
08008272  str  r6, [r7, #4]        ; DMA destination
08008278  strh r6, [r7, #8]        ; count, in halfwords
0800827A  movs r6, #1
0800827C  lsls r6, r6, #0xf
0800827E  strh r6, [r7, #0xa]      ; control 0x8000: enable, 16-bit units
08008280  adds r6, #0x20           ; the SOURCE descriptor advances by 0x20
08008286  adds r6, #0x40           ; the DESTINATION descriptor advances by 0x40
```

**What the code establishes.** One step moves `32 - m` **bytes** (a count of
`(32 - m) / 2` halfwords under 16-bit units), from a source that advances `0x20`
per step into a destination that advances `0x40`. The source is one byte per map
entry - a 32-byte row of the container - and the destination is a map area of
wider rows, i.e. tile entries, not a character area:

* `0x0600F000` is not character-base aligned for a background (character bases are
  `0x4000`-aligned, and all four of map 19's slots declare character base 0). It is
  map 19's **BG2 map base 30**: `root + 0x3C` = 1 selects the row at
  `0x080716E0` = `[0x1C80, 0x1D80, 0xBE80, 0x1F80]`, and the root's per-slot
  addends at `+0x04..+0x07` are `3, 3, 3, 3`, so the background programmer writes
  BG2CNT = `0xBE83`;
* the same constructor family installs an IRQ handler at `0x08008098`..`0x080080BE`
  that writes `BG2PA`..`BG2Y` per scanline from a per-scanline table, i.e. the
  layer is projected affinely - which is also why the map area is addressed with a
  64-byte row stride rather than the affine map's nominal 32.

The literal the earlier revision of this ticket quoted, `0x06008000`, does **not
occur anywhere in the 8 MiB image**: 0 pool words and 0 references. It was a
misread of the destination arithmetic, and with it fell the claim that the
destination was a character area at one byte per pixel. A corrected revision of
this ticket replaced that reading (see §5).

## 3. PROJECT INTERPRETATION

* **A container is a 32x32 plane of 8-bit tile ordinals.** `CONFIRMED`. 1024
  decoded bytes = 32 rows of 32 ordinals, and the plane's ordinals resolve inside
  map 19's own assembled character block of 539 tiles: the ordinals used are
  `1..228`, none is `0`, and the character block's tile 0 is all-zero - a tilemap
  never needs the blank tile. `CONFIRMED`.
* **The containers lay out in raster order**: container `y * grid_x + x` covers
  the 32x32-ordinal cell at `(x * 32, y * 32)`. `CONFIRMED` from the driver's
  index arithmetic (`wrapped_y * grid_x + wrapped_x`).
* **The ordinals are ordinals, not palette indices.** `CONFIRMED` by a semantic
  measurement, which is the decisive one: exactly 33 of the 228 ordinals the plane
  uses select a tile that is more than half water (character-block tiles whose
  pixels are dominated by background-palette indices 83 and 177, `(24,140,255)`
  and `(33,165,231)`), every one of them at a share of `0.547` or more, while all
  195 remaining ordinals select a tile at `0.375` or less. The two classes do not
  overlap. The same measurement over a permuted ordinal assignment collapses to
  fewer than half as many water ordinals. Ordinal `2` alone - 40.7 % of the plane
  - selects a tile that is 100 % water; `43` and `119` select green land, `137`
  sand, `76`/`73` rock and `19` snow.
* **Rendered result**: `448 x 320` tile ordinals, resolved at 8x8 pixels per tile
  = **3584 x 2560 pixels**, through the map's own character block. `CONFIRMED`
  for the construction; the image is clean game art - blue sea, coastline, rivers,
  snow-capped mountains, forest and sand.
* **What the layer is**: a world-scale terrain/tile field for map 19, driven
  through the same character block as the map's other layers. Its pixels classify
  the terrain (sea, coast, river, forest, sand, rock, snow) rather than being a
  per-map backdrop.
* **Not claimed**: the per-scanline affine projection is `INFERRED` from the IRQ
  handler's register writes; no runtime capture was taken, so nothing here is
  `LEVEL 3`. The composite places every layer at the canvas origin because no
  layer X/Y offset is established for any form; that model is pre-existing and
  `INFERRED`.

## 4. EXPORT CONSEQUENCE

* `tools/export/canonical.py` - `TERRAIN_FIELD_LAYER_HANDLER` and its record
  offsets, `read_terrain_field_cells`, `read_terrain_field_containers`,
  `read_terrain_field_probe`, and `LayerRecord.terrain_x`/`terrain_y` with
  `terrain_grid_x`, `terrain_grid_y`, `terrain_cells`, `terrain_tiles_x`,
  `terrain_tiles_y`, `terrain_pixels_x`, `terrain_pixels_y`.
* `tools/export/render.py` - `read_terrain_field_plane` (the ordinal plane) and
  `render_terrain_field` (the plane resolved through a character block).
* `tools/export/buu_resource_export.py` - collection in `collect_map_graph`,
  rendering in the export path and in `render_layer`, and the published census for
  this form: `cell_tiles`, `cell_bytes`, `container_count`, `cell_grid_x`,
  `cell_grid_y`, `cell_grid_cells`, `tile_grid_x`, `tile_grid_y`,
  `tile_ordinal_min`, `tile_ordinal_max`, `distinct_tile_ordinals`. No chunk-grid
  key is published for this form.
* `docs/asset-export.md` - the class description.

Measured result for the layer: `maps/map_019/layer_2.png`, 3584x2560,
`image_sha256 900d7e0c4a4cc7dd3f2719c5ba600cff750fa4fc6b5a35de81bad9e88b2adaee`,
index-image digest `fc7eca6dc1fdefe8518cc49f46f51281d87529215d15032d4fdf6dbdcf252935`,
ordinal-plane digest `883f6db20c3b908eb61e7d7bcd0c16fade994e184e95c8d3118d85cbbc4976ec`.
Map 19's composite is produced at 3584x2560 with index-image digest
`2ece490ffb793be9a15e4a176ab70fad1a45526793a9a39a85827429af4cfeec`.

## 5. Correction record

The first frozen revision of this ticket read the same record, grid and container
run correctly but drew the wrong unit from the blitter: it claimed each container
was a 32x32 one-byte-per-pixel image and rendered a 448x320 thumbnail, quoting a
destination literal (`0x06008000`) that does not exist in the image and
mislabeling which descriptor the `0x20` and `0x40` advances belong to.

Independent review falsified it with the semantic measurement recorded in §3: a
permuted ordinal assignment destroys the water/land correspondence, which a
palette-index reading cannot explain; and nine 32x32-*pixel* cells cover only
96x96 pixels, less than one screen, so the wrong model could not have drawn the
layer at all. The unit was corrected to tile ordinals, the layer to 3584x2560, and
every claim above re-derived from the ROM. The corrected revision keeps the
identity, grid, container-run and census findings, which the review reproduced
independently.

## 6. Unresolved, stated rather than implied

* The blitter's destination row stride (`0x40` bytes for a `32 - m` byte step)
  does not reconcile with BG2CNT declaring an affine map, whose entries are one
  byte: a `0x40` stride implies a 64-entry row while the affine map is `32` wide.
  The layer's own size, cell layout and ordinals do not depend on which of the two
  is the engine's rule, but the exact per-row placement inside VRAM is not
  established.
* The per-scanline affine projection, and therefore the layer's on-screen scale
  and orientation, is `INFERRED` from the IRQ handler; no runtime capture was
  taken.
* The frame budget, and whether anything else writes the same background area
  during a frame, were not measured. Both were already open in
  `ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md` §7.
* `tools/research/thumb_disasm.py::scan_thumb_bl_callers` was not used for any
  claim here. Its defects are recorded in
  `ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md` §7 and still need their own ticket.
