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
START SHA:     c6821d450b475ec5d262f0b239b3f2dce8de6559
REVIEWED REVISION (REJECTED): c01000953e2682918cc1f2d4e8071abbb5a2d1ba
CORRECTED REVISION: 3529b80f6032c5a7bbb702bddc28802a6c04f441
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
* stores the type word `0x08049C84` at `+0x00` and the record at `+0x04`
  (`0x08008106 str r0,[r4,#4]`);
* initialises the nine slots at `0x08008104`..`0x0800811C`. `0x08008104` loads
  `0x08071018` and `0x0800810A` does `adds r3,#8`, giving **`0x08071020`**, a
  stored 0x400-byte all-zero ROM cell - the "no cell" placeholder; the loop body
  writes that constant to `object + 0x08 + 4*i` (`0x0800811A str r3,[r1,#8]`) and
  `0xFF` to `object + 0x2C + 4*i` (`0x08008114 str r2,[r1,#0x2c]`, `r2 = 0xFF`).
  Both fields therefore start as "no cell"; the **real** slot buffers are
  installed by the driver at `0x08008688`..`0x08008698`
  (`str r1,[r2,#0x2c]` residency and `str r1,[r2,#8]` buffer, with
  `r1 = object + 0x3A0 + slot*0x400`);
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
descriptor at `0x040000D4` (`DMA3SAD`; destination `0x040000D8` = `DMA3DAD`, count
`0x040000DC`, control `0x040000DE`). Nine blocks do this - two clip variants
(blocks 1-6 and 7-9) sharing one DMA programming, each covering one of the
constructor's nine resident slots `[object+0x08]`..`[object+0x28]`. The
destination base literal is at pool `0x080084A8` / `0x08008830`, and the DMA
register literal at pool `0x080084AC` / `0x08008834`. One block's listing:

```text
0800823A  ldr  r6, [pc, #0x26c]    ; = 0x0600F000 (the destination base)
08008268  lsls r6, r6, #0xf
0800826A  lsrs r6, r6, #0x10       ; count = ((32 - m) << 15) >> 16 = (32 - m) / 2
0800826E  mov  r6, lr              ; r6 = the source descriptor value
08008270  str  r6, [r7]            ; DMA3SAD = source
08008272  str  r6, [r7, #4]        ; DMA3DAD = destination
08008278  strh r6, [r7, #8]        ; count, in halfwords
0800827A  movs r6, #1
0800827C  lsls r6, r6, #0xf
0800827E  strh r6, [r7, #0xa]      ; control 0x8000: enable, 16-bit units
08008280  mov  r6, lr
08008282  adds r6, #0x20           ; the SOURCE (DMA3SAD) value advances by 0x20
08008286  mov  r6, ip
08008288  adds r6, #0x40           ; the DESTINATION (DMA3DAD) value advances by 0x40
```

**What the code establishes.** One step moves `32 - m` **bytes** (a count of
`(32 - m) / 2` halfwords under 16-bit units), from a source whose descriptor value
advances `0x20` per step to a destination whose descriptor value advances `0x40`.
The source is one byte per map entry - a 32-byte row of the container. The
destination is a map area of wider rows, i.e. tile entries:

* `0x0600F000` is not a character base: character bases are `0x4000`-aligned and
  all four of map 19's slots declare character base 0. It is map 19's **BG2 map
  base 30**: `root + 0x3C` = 1 selects the row at `0x080716E0` =
  `[0x1C80, 0x1D80, 0xBE80, 0x1F80]`, and the root's per-slot addends at
  `+0x04..+0x07` are `3, 3, 3, 3`, so the background programmer writes
  BG2CNT = `0xBE83`;
* the same constructor family installs an IRQ handler at `0x08008098`..`0x080080BE`
  that, for VCOUNT 55..159, loads a 16-byte record from a per-scanline table
  (`[0x08071018]->+4`, `+0x28`, indexed by `(vcount+1)*16`) and stores it to
  `0x04000020`..`0x0400002C`, i.e. `BG2PA`, `BG2PB`, `BG2PC`, `BG2PD`. Those
  registers only affect the display in affine mode, so the layer is `INFERRED` to
  be projected per scanline. The 64-byte destination row does **not** follow from
  that: it follows from the control word's size field (`§8`).

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
  through the same character block as the map's other layers. Its labels classify
  terrain - sea, coast, river, forest, sand, rock and snow - `INFERRED` from the
  character-block tiles the ordinals select and from the field's own shape; the
  ordinal-to-tile mechanism is `CONFIRMED`, the terrain reading is not an engine
  statement. See §9 for the world-map hypothesis this bears on.
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

## 6. What the runtime attempt established, and what it could not

A runtime session was run with the project's pinned emulator and its tracked
harness: mGBA 0.10.5
(`build/tools/mgba-0.10.5/.../mGBA.exe`, `FileVersion 0.10.5.0`, SHA-256
`5A3C98C2984DD04BD0D7C9378CDFAE937AE0D73A196C880BB2EECF3B254AF247`), launched in
an isolated portable profile (`savegamePath`/`savestatePath`/`screenshotPath` all
outside the repository) on the canonical ROM
(`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`) with the
local save (`7CF0A516EBEBBC74A959D6FC1EBC7AAC808FC99683CCBB9E4B82A0D58BA02A86`).
The read-only observer `tools/runtime/map19_bg_placement.lua` was injected through
the tracked `tools/runtime/inject_mgba_lua.ps1` path - the observer is registered
in that script's allowlist, which is the repository's documented way to add one -
and ran for 900 emulated frames, recording DISPCNT, `BG0CNT..BG3CNT`, the
background scroll and affine registers, the active-map pointer, and the raw bytes
of `0x0600F000` and `0x0600E000`, plus mGBA's own screenshots. The observer writes
no emulated memory and injects no input.

**Observed.** The session sat on the title screen. `active_map_ptr` = `0`, so no
`MapEntry` was loaded; `DISPCNT` = `0x0200` (forced blank, mode 0); the
background-control and scroll registers read `0x78A3`, which is register noise
outside any active display mode, not engine state. `0x0600F000` held an ascending
`0x0001, 0x0002, ...` halfword ramp, the boot-time VRAM contents, and `0x0600E000`
held its own distinct contents. Nothing about map 19 is therefore observable from
this capture, and no display-orientation inference is drawn from it.

**Why map 19 was not reached.** The local `roms/*.sav` is a save image, not a
savestate: reaching map 19 from it needs the title/load menus driven with
deterministic input, and no savestate already inside map 19 exists in this
environment (the tracked states are P-002/placement-pos/ROM-006 captures on other
maps). The documented input path is `emu:setKeys`/`emu:addKey` in a Lua observer,
and reaching an unknown menu path reliably is not something this ticket can
guarantee inside its scope. The tracked launcher's GDB client is read-only by
design, so the active-map pointer cannot be forced either.

**What this leaves open, precisely.** The runtime observation that is missing is a
map-19 session reading: DISPCNT's mode and enabled backgrounds; `BG2CNT` as
written by the background programmer; `BG2HOFS`/`BG2VOFS`; `BG2PA..BG2PD` sampled
inside the vertical window where the IRQ handler writes them (VCOUNT 55..159); and
`0x0600F000` compared byte-for-byte against the ROM-derived ordinal plane. Those
five readings settle which background displays the field, whether the whole
448x320 ordinal plane is ever resident, and whether the placement is a whole-layer
blit or a windowed view.

## 7. Placement: what the static evidence does and does not settle

The accepted rule - every layer drawn at the composite canvas origin in the
documented `(bg_control_addend, bg)` order - is **pre-existing and `INFERRED`**,
and this ticket does not promote it. Applied to map 19 it yields a 3584x2560
composite, which is that rule's arithmetic consequence, not a validated engine
fact.

Two static facts bound what the composite can mean:

* `0x0600F000` is map 19's BG2 **map base 30** (`root + 0x3C` = 1 selects
  `0x080716E0`, and the root addends `3, 3, 3, 3` give `BG2CNT` = `0xBE83`), and
  its affine map block is 1024 bytes = one container. The field is 140 containers,
  so the whole field is never resident in that one block at once. The destination
  is the live background map the engine streams into - a windowed representation -
  and the driver's nine-resident-cell 3x3 window over a 14 x 10 grid is the same
  statement from the other side.
* The driver's cell index is `wrapped_y * grid_x + wrapped_x`, so the field's own
  raster order is `CONFIRMED`, and a whole-field render is a faithful
  reconstruction of the resource.

**Consequence for the export.** `maps/map_019/layer_2.png` (3584x2560) is the
accepted whole-field extraction. `maps/map_019/composite.png` is the current
placement rule applied to it and is **provisional** until the five runtime
readings above exist. The pipeline cannot yet claim 452/452 composites
runtime-validated.

## 8. Row-stride question, resolved

An earlier revision of this ticket recorded the `0x40` destination step as not
reconciling with the background configuration. That record was wrong in its
premise and is corrected here.

**BG2CNT = `0xBE83` decoded field by field** (`0xBE83` = `1011 1110 1000 0011`):
priority `3`, character base `0`, mosaic `0`, 256-colour `1`, map base `30`,
wrap `1`, size field `2`. Bit 6 is **0**, so BG2 is in **text** mode, not affine.
The size field (`2`) gives a map `512` pixels wide in either mode:

* text, `512x256` pixels = `64 x 32` entries at 2 bytes = **64-byte rows** for the
  first 32 entries;
* affine `512x512` pixels = `64 x 64` entries at 1 byte = **64-byte rows**.

So the `0x40` destination step agrees with the control word under either reading,
and the source's `0x20` step is the 32-byte half-row the copy covers. There is no
stride obstruction left to record, and one earlier "does not reconcile" statement
is withdrawn.

What remains genuinely open is narrower and is recorded as `UNRESOLVED`:

* **text versus affine.** The control word says text (bit 6 = 0), yet the
  constructor's IRQ handler writes `BG2PA`..`BG2PD` for VCOUNT 55..159, and those
  registers have no display effect in text mode. One of the two is not yet
  accounted for.
* **how a byte-granular copy lands in a 16-bit-entry map.** The copy moves
  `32 - m` bytes from a one-byte-per-entry source into a map whose entries are 2
  bytes wide in text mode. Whether the destination is staged and converted later,
  or the map is affine after all, is not established.

Neither affects the layer's content, extent or ordinals, and neither changes the
placement status in §7.

## 9. The world-map hypothesis

A human observation proposed that map 19 is the flying world map. It is a
hypothesis, not evidence; visual resemblance is deliberately not one of the
findings below. Candidate corroboration was then tested against the ROM, and none
of it is a runtime observation.

| Check | Result |
| --- | --- |
| Map name / text | map 19's `text_index` is null: the map publishes no name. Neutral. |
| Declared root extents | `root + 0x08`/`+0x0A` = **3345 x 2401**. Ranked against all 452 maps these are the **largest of 55 distinct extent pairs**, and no other map comes close. Weak corroboration. |
| Maps large enough for the field | 10 maps declare extents reaching 448x320 tiles or more (`19, 46, 102, 107, 113, 138, 139, 359, 410, 425`), so size alone does not single map 19 out. |
| Layer form | map 19 is the **only** map carrying the `0x080088BD` handler, and the handler word occurs exactly once in the image, so its terrain field is one-off. Corroborating. |
| Field extent | 448x320 tile ordinals = 3584x2560 pixels, far beyond one screen. A field of that size exists to be traversed. Corroborating. |
| Field content | the ordinals' tiles resolve to terrain types (sea, coast, river, forest, sand, rock, snow), `INFERRED` from the character block. Corroborating. |
| Background configuration | BG2 (`BG2CNT` = `0xBE83`: priority 3, map base 30, 256-colour, text mode) with the constructor writing `BG2PA`..`BG2PD` per scanline. Consistent with a dedicated full-screen background. Corroborating. |
| Camera traversal / streaming | the driver keeps a nine-cell 3x3 window over the 14x10 grid and the blitter is viewport-driven, so the engine streams the field as the view moves. **Confirmed structurally**, but the traversal itself (who moves the viewport, and whether player flight drives it) was **not** observed. |
| World-flight state / map entry and exit | not investigated - out of this ticket's scope. **Missing.** |
| Runtime capture of the overworld using this data | not obtained (`S6`). **Missing.** |

**Classification: `PARTIALLY CONFIRMED`.** What is established is that map 19 is
the only map with this one-off handler, that its terrain field is an enormous
traversable-scale semantic terrain raster, that it is drawn through a dedicated
background, and that the engine streams a window of it. What is not established is
the decisive runtime fact - that the flying-overworld scene displays this map, and
that player flight drives the viewport over it. `PARTIALLY CONFIRMED` is the
strongest label the evidence supports; `CONFIRMED` would require the runtime
observation in §6 and is not claimed.

**Consequence if the hypothesis holds.** A 3584x2560 whole-field composite is then
a derived resource-pack artifact, not a screen the hardware ever displays as one
plane: the engine presents a window of the field, streamed through BG2's map area,
with the affine registers carried per scanline. Resource completeness and runtime
screen composition are different claims, and this document keeps them apart.


## 10. Unresolved, stated rather than implied

* **The composite placement.** No map-19 runtime session was obtained (§6), so the
  origin-based placement and the resulting 3584x2560 composite are `PROVISIONAL`.
  The five readings §6 names are the missing evidence.
* **Text versus affine, and how a byte-granular copy lands in a 16-bit-entry
  map.** `G8` records both halves of what remains open on the destination. Neither
  affects the layer's content, extent or ordinals.
* **Whether map 19 is the flying world map**, and therefore whether the whole-field
  composite corresponds to any single displayed screen: `PARTIALLY CONFIRMED`
  (§9). The decisive runtime observation is missing.
* The per-scanline affine projection, and therefore the layer's on-screen scale
  and orientation, is `INFERRED` from the IRQ handler; no runtime capture of it was
  taken.
* The frame budget, and whether anything else writes the same background area
  during a frame, were not measured. Both were already open in
  `ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md` §7.
* `tools/research/thumb_disasm.py::scan_thumb_bl_callers` was not used for any
  claim here. Its defects are recorded in
  `ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md` §7 and still need their own ticket.
