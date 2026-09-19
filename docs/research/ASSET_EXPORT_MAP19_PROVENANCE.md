# ASSET-EXPORT-MAP19-001 - provenance for map 19's terrain-field layer

Narrow record for one layer: map 19, root `0x082AD8BC`, slot `+0x1C`, record
`0x082ABF00`, handler `0x080088BD`. It was the last
`static_graphical_assembly_unresolved` reference in the export. This document
records the engine observation, the project interpretation and the export
consequence for recovering its assembly. The full handler census is in
[`ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md`](ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md);
it is not repeated here.

## 1. Identity and baseline

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

`+0x04` is `0x0E` and `+0x05` is `0x0A`: the record's own cell grid is
**14 x 10 = 140**, and 140 is exactly the length of the container pointer run -
the word after the last pointer is not a pointer. The root's other slots are
`+0x14 -> 0x0829F6E4` (slot 0), `+0x18 -> 0x0829F808` (slot 1),
`+0x1C -> 0x082ABF00` (slot 2) and `+0x20 -> 0x080707FC` (slot 3), which is the
layout published in `maps/map_019/map.json`.

## 2. ENGINE OBSERVATION - the handler path

Entry `0x080088BC`:

```text
080088BC  push {r3, lr}
080088BE  movs r0, #0
080088C0  bl   0x080080C0        ; r1 = the record
080088C4  pop  {r3, pc}
```

Constructor `0x080080C0`:

* allocates `0x27A0` bytes, which is `0x3A0 + 9 * 0x400`: a header plus a
  nine-slot resident cache of `0x400`-byte cells;
* stores the type word `0x08049C84` at `+0x00` and the record at `+0x04`;
* fills `object + 0x08 + 4*i` for `i = 0..8` (the nine slot buffer pointers) and
  `object + 0x2C + 4*i` with `0xFF` (slot residency, "no cell");
* reads the record's grid product - `movs r7,#0x1d / lsls r7,r7,#5` gives
  `0x3A0`, then `ldrb r6,[r0]` / `ldrb r0,[r0,#1]` / `muls r6,r0,r6` on
  `record + 4` and `record + 5` - and, while the product is at most 9, eagerly
  decompresses container `i` through `0x0803D940` to `object + 0x3A0 + i*0x400`;
* sets `DISPSTAT` bit 1 at `0x04000200` and clears `0x04000022`/`0x04000026`
  (`BG2PB`/`BG2PD`).

Driver `0x08008598` (Capstone listing; the routine runs to `0x080086D6`):

```text
08008598  push {r0, r1, r4, r5, r6, r7, lr}
0800859a  sub  sp, #0x1fc
0800859c  sub  sp, #0x1fc
0800859e  sub  sp, #0x34
080085a0  add  r7, sp, #0x3fc
080085a2  adds r4, r0, #0          ; r4 = object
080085a4  adds r7, #8
080085aa  add  r3, sp, #0x3fc
080085ac  ldr  r0, [r3, #0x34]     ; the caller's argument block
080085ae  ldr  r0, [r0, #4]        ; -> the record
080085b0  adds r2, r0, r6          ; r6 = -1, so r2 = record - 1
080085b2  ldr  r0, [r4, #4]        ; the record again
080085b4  ldrb r0, [r0, #5]        ; grid_y
080085b6  bpl  ...                 ; wrap the chunk Y into [0, grid_y)
080085c2  movs r1, #0
080085c4  mvns r1, r1
080085c6  add  r3, sp, #0x3fc
080085c8  ldr  r0, [r3, #0x34]
080085ca  ldr  r0, [r0]            ; -> the state block
080085cc  ldr  r3, [r4, #4]
080085ce  adds r0, r0, r1          ; x - 1
080085d2  ldrb r3, [r3, #4]        ; grid_x
080085d8  ldrb r5, [r3, #4]
080085da  cmp  r0, r5              ; wrap the chunk X into [0, grid_x)
080085e0  ldr  r3, [r4, #4]
080085e2  adds r5, r2, #0
080085e4  ldrb r3, [r3, #4]        ; grid_x
080085e8  muls r5, r3, r5          ; wrapped_y * grid_x
080085ea  adds r0, r5, r0          ; + wrapped_x = the cell index
080085ec  stm  r7!, {r0}           ; the 3x3 window start indices
```

so the record's chunk index is `wrapped_y * grid_x + wrapped_x`, the raster
order of a `grid_x`-wide grid, and the routine walks a 3x3 window of nine cells
around it (`0x080085f8` .. `0x080086c2`), decompressing a required cell through
`0x0803D940` into the stack buffer at `sp+4` and copying it into the resident
slot with `0x08049138` at a size of `0x400`. It finishes by storing the resolved
window origin at `object + 0x50`/`+0x54`.

Renderer `0x08008192` (the blitter; runs to `0x08008596`): reads the viewport
from the state object, splits it into a clipped span, and per iteration programs
DMA channel 0 at `0x040000D4`:

```text
0800823A  ldr  r6, [pc, #0x26c]    ; = 0x06008000, the destination base
0800824A  lsls r2, r2, #0x1b
0800824C  lsrs r2, r2, #0x1b       ; the source column within a 32-byte row
0800824E  lsls r6, r2, #6
08008250  add  r6, ip
08008252  mov  ip, r6              ; destination column advance = col * 64
0800825A  lsls r7, r2, #5
0800825C  adds r6, r6, r7          ; source column advance = col * 32
08008268  lsls r6, r6, #0xf
0800826A  lsrs r6, r6, #0x10       ; DMA word count = (32 - m) & 0xFFFF
08008280  mov  r6, lr
08008282  adds r6, #0x20           ; source advance per iteration = 0x20
08008286  mov  r6, ip
08008288  adds r6, #0x40           ; destination advance per iteration = 0x40
```

Three facts follow from the routine's own constants:

1. **One iteration consumes one 32-byte raster row.** The source pointer used as
   the DMA source is `[object + 8 + 4*slot] + row*0x40 + col*0x20`, and the
   per-iteration source advance is `0x20`; the destination advance is `0x20` for
   a 32-byte span. A row is therefore 32 bytes.
2. **One byte per pixel.** The destination's column advance for the next row slot
   is `0x40` bytes while the source's is `0x20`, so a source row of 32 bytes maps
   onto a destination row of 64 bytes; the destination is the background
   character area at `0x06008000`, whose owning `BGxCNT` is an 8-bpp row, i.e. one
   byte per pixel. A 32-byte row is 32 pixels.
3. **A cell is 32x32 pixels.** `0x400 / 32 = 32` rows, and the grid product equals
   the container count, so the containers tile the field in raster order.

`resolve_thumb_bl` and `scan_thumb_bl_callers` are not used for any claim here;
every caller and field statement above was read from Capstone 5.0.7 disassembly
of the canonical ROM.

## 3. PROJECT INTERPRETATION

* **Graphics format**: `CONFIRMED` for the shape - each `0x400`-byte container is
  a 32-row raster of 32 one-byte pixels, so a container is a 32x32 cell and the
  140 cells lay out in raster order to a 448x320 field.
* **Pixel format is one byte per pixel**: `CONFIRMED` from the blitter's two row
  strides (32-byte source span, 64-byte destination row) and from the payload
  itself. The histogram over all 143,360 decoded bytes carries palette indices
  `1..228` with index `0` absent, which a packed 4-bpp nibble arrangement cannot
  produce; the dominant values are `2` (40.7 %), `43` (9.1 %), `8` (6.2 %),
  `3` (6.1 %) and `137` (5.7 %) of the 143,360 bytes, a contiguous low-index
  palette of a limited-colour field.
* **The record states its grid at `+0x04`/`+0x05`**: `CONFIRMED`. The product
  `14 * 10 = 140` is exactly the container run length, while the dominant form's
  `+0x14`/`+0x15` hold `48`/`251` on this record - unrelated bytes, which is why
  the exporter no longer reads them as a grid for this form.
* **Placement within the field**: `INFERRED`. The cell order is `y * grid_x + x`
  (`CONFIRMED`, from the driver's index arithmetic), and the field is the whole
  layer rather than an overlay (`INFERRED`, from the `0x080088BD` constructor
  allocating a nine-cell cache and driving a viewport-based blitter for it). The
  composite places every layer at the canvas origin because no layer X/Y offset is
  established for any form.
* **Palette**: the global background palette at `0x080701B0`, the same 256-entry
  table the dominant and screen-entry layers render through. No per-layer palette
  is named on this path.
* **Not claimed**: that the 140 containers are second-order data - a height field
  or elevation map - rather than the drawn image. What the blitter copies is
  8-bpp pixels into the background character area; whether the palette indices
  happen to encode a terrain *kind* as well is not established and is not needed
  to render the layer.

## 4. EXPORT CONSEQUENCE

* `tools/export/canonical.py` - `TERRAIN_FIELD_LAYER_HANDLER` and its record
  offsets, `read_terrain_field_containers`, `read_terrain_field_probe`, and the
  `LayerRecord.terrain_x`/`terrain_y` fields with `terrain_grid_x`,
  `terrain_grid_y`, `terrain_cells`.
* `tools/export/render.py` - `render_terrain_field`, which assembles the cells
  into one image with no scaling, no padding and no interleaving.
* `tools/export/buu_resource_export.py` - collection of the record's containers in
  `collect_map_graph`, rendering in the export path and in `render_layer`, the
  byte census published for this form (`cell_pixels`, `cell_bytes`,
  `container_count`, `index_min`, `index_max`, `distinct_indices`) and the grid
  published as `cell_grid_x`/`cell_grid_y`/`cell_grid_cells`. No chunk-grid key is
  published for this form.
* `docs/asset-export.md` - the class description.

Measured result for the layer: `maps/map_019/layer_2.png`, 448x320,
`image_sha256 3e57e01d60200cde0f74e42be2f68cbb73114f10f0a36e1345f9140a13104b7b`,
index-image digest `883f6db20c3b908eb61e7d7bcd0c16fade994e184e95c8d3118d85cbbc4976ec`.
Map 19's composite is produced at 448x320 with index-image digest
`deb8fec4fe627b78f8feaeed8a9d69759eaf967b2195bf240d5c288a73a2d170`.

## 5. Unresolved, stated rather than implied

* The blitter's per-column VRAM placement is not published as a model. The
  engine's column stride and the recovered raster agree on the row length
  (32 bytes) and on the cell size (32x32), and the assembled field is coherent,
  but the destination is the character area of a background the layer shares with
  the map's other layers, and this ticket did not establish how the engine's
  per-column destination arithmetic and the field's raster order reconcile beyond
  those two measurements.
* The frame budget, and whether anything else writes the same background area
  during a frame, were not measured. Both were already open in
  `ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md` §7.
* No runtime capture was taken. Nothing here is `LEVEL 3`; the placement model is
  `INFERRED` and the pixel format is `CONFIRMED` from static code and data.
