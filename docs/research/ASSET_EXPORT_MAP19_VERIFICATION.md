# ASSET-EXPORT-MAP19-001 - review

```
START SHA:    c6821d450b475ec5d262f0b239b3f2dce8de6559
              (the current accepted tip of asset-export-map-handlers-001,
              verified as: 9154fed and 5ab0f5c are ancestors, the worktree is
              clean, and both reviewer approvals are recorded in
              docs/research/ASSET-EXPORT-MAP-HANDLERS-001-review.md)
FROZEN CONTENT REVISION: c01000953e2682918cc1f2d4e8071abbb5a2d1ba
              ("export: resolve final special map layer" - the revision both
              reviewers were given)
BRANCH:       asset-export-map19-001
COMMITS:      this ticket's own commits on top of the start SHA
CANONICAL ROM SHA BEFORE: 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
CANONICAL ROM SHA AFTER:  940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
```

Two commits follow the frozen content revision: `3bebe02` ("drop an unused
class-name constant", inert) and the correction commit that closes Reviewer A's
blocking findings (see **Correction record** below). Everything the reviewers
reproduced about the record, the grid, the container run and the census is
unchanged by the correction; what changed is the unit of the payload and the
rendered size.

## What the ticket set out to do

Resolve the one `static_graphical_assembly_unresolved` reference left by
ASSET-EXPORT-MAP-HANDLERS-001: map 19, root `0x082AD8BC`, slot `+0x1C`, record
`0x082ABF00`, handler `0x080088BD`.

## What was found

The containers are not pixels - they are a **tile-ordinal plane**.

Each of the record's 140 containers decodes to exactly `0x400` bytes, and the
engine's own code fixes their shape and layout:

* the driver indexes cells as `wrapped_y * grid_x + wrapped_x`
  (`0x080085E4`/`0x080085E8`/`0x080085EA`);
* the blitter moves `32 - m` **bytes** per step - a count of `(32 - m) / 2`
  halfwords under 16-bit units (`0x08008268`/`0x0800826A`/`0x0800827A`) - from a
  source that advances `0x20` into a destination that advances `0x40`;
* the destination base literal is `0x0600F000` (pool `0x080084A8`/`0x08008830`),
  which is map 19's BG2 **map base 30**, not a character area: `root + 0x3C` = 1
  selects `0x080716E0` = `[0x1C80, 0x1D80, 0xBE80, 0x1F80]` and the root addends
  `3, 3, 3, 3` give BG2CNT = `0xBE83`. A map area holds tile entries;
* the decisive measurement is semantic, not structural: exactly 33 of the 228
  ordinals the plane uses select a character-block tile that is more than half
  water (background-palette indices 83 and 177), all at a share of `0.547` or
  more, while all 195 others select a tile at `0.375` or less - a clean split that
  collapses to fewer than half as many water ordinals under a permuted ordinal
  assignment. Ordinal `2` alone (40.7 % of the plane) selects a tile that is
  100 % water; `43`/`119` green land, `137` sand, `76`/`73` rock, `19` snow.

So a container is a 32x32 plane of 8-bit tile ordinals, the 140 cells lay out in
raster order to 448x320 ordinals, and the layer renders at **3584x2560 pixels**
through map 19's own assembled 539-tile character block. The full evidence is in
[`../research/ASSET_EXPORT_MAP19_PROVENANCE.md`](../research/ASSET_EXPORT_MAP19_PROVENANCE.md).

## Result

```text
PREVIOUS CLASS:  static_graphical_assembly_unresolved
FINAL CLASS:     static_graphical_terrain_field

MAP:             19
LAYER SLOT:      2  (root +0x1C)
LAYER RECORD:    0x082ABF00
HANDLER:         0x080088BD
ASSEMBLY MODEL:  140 containers of 0x400 bytes = 32x32 planes of 8-bit tile
                 ordinals, container y*grid_x + x at (x*32, y*32) ordinals;
                 448x320 ordinals = 3584x2560 pixels at 8x8 per tile
SOURCE RESOURCES: 0x0829F814 .. 0x082ABDF4, every one kind 1 declaring 0x400
TILE SOURCE:     map 19's own assembled character block, 539 tiles; the plane
                 uses ordinals 1..228 and never 0
BG / VRAM:       destination map base 0x0600F000 (map 19's BG2 map base 30,
                 BG2CNT 0xBE83), a tile-entry area, not a character area

LAYER IMAGE:     EXPORTED  maps/map_019/layer_2.png  3584x2560
                 image_sha256 900d7e0c4a4cc7dd3f2719c5ba600cff750fa4fc6b5a35de81bad9e88b2adaee
                 index digest fc7eca6dc1fdefe8518cc49f46f51281d87529215d15032d4fdf6dbdcf252935
                 ordinal-plane digest 883f6db20c3b908eb61e7d7bcd0c16fade994e184e95c8d3118d85cbbc4976ec
COMPOSITE:       EXPORTED  maps/map_019/composite.png  3584x2560
                 image_sha256 827fd0688ff90da36471aa302aa7b6de9c6017bf12368c8c7dc4c668b42c5c66
                 index digest 2ece490ffb793be9a15e4a176ab70fad1a45526793a9a39a85827429af4cfeec

TOTAL MAP ENTRIES:      452
TOTAL LAYER REFERENCES: 1808
LAYER CLASSIFICATION:   1808 / 1808 (dominant 1516, absent_placeholder 249,
                        static_graphical_screenblock 42,
                        static_graphical_terrain_field 1)
GRAPHICAL LAYERS RENDERED: 1559
COMPOSITES:             452   EXPECTED 452
COMPOSITES WITHHELD:      0   EXPECTED 0
UNRESOLVED GRAPHICAL LAYERS: 0
SILENTLY OMITTED LAYERS:  0
```

## Byte-level change audit

The isolated full export (86,444 artifacts, 0 failures) is diffed against the
accepted library (86,442 artifacts) by the audit hash table:

```text
ADDED:    2   maps/map_019/layer_2.png
              maps/map_019/composite.png
REMOVED:  0
CHANGED:  2   maps/map_019/map.json
              metadata/maps.json
UNRELATED PNG CHANGES: 0
```

Every sprite, tile, chunk, palette and dominant-layer artifact is byte-identical
to the accepted library. The unchanged populations were re-measured and every one
of them holds at its accepted value - the exporter's own gates report
measured == expected and accounted for: sprite definitions 297, sprite pieces
11005, animation slots 4070, non-null animations 1721, unique animations 1017,
unique frames 10980, multipart frames 21, structured sprite graphics 7390, tile
banks 187, chunks 3745, map entries 452, maps exported 452, map directories
written 452, layers classified 1808.

## Validation

```text
DETERMINISM:        PASS (the export is a pure function of the ROM: the layer,
                    composite and plane digests are reproduced by the pinned tests
                    from the ROM alone, and the exporter's repeat-render test
                    passes)
VISUAL VALIDATION:  PASS as a coherence check only - layer_2.png at 3584x2560 is
                    clean game art: blue sea, a coastline, rivers, snow-capped
                    mountains, forest and sand, with no seams and no repeated or
                    garbage blocks. Visual coherence is validation, not evidence;
                    the unit was established by the semantic split recorded above.
PORTABLE TESTS:     1789 passed, 8 skipped (`pytest tests/unit`)
ROM-GATED TESTS:    81 passed (`pytest tests/integration/test_asset_export_rom.py`,
                    `LOGX_CANONICAL_ROM` set; not collected by CI)
SAFETY TESTS:       included in both sets
DIFF CHECK:         `git diff --check` clean
GENERATED PROSE FILES:    0   EXPECTED 0
HEURISTIC GFXSCAN ASSETS: 0   EXPECTED 0
GENERATED ASSETS TRACKED BY GIT: 0   EXPECTED 0
CANONICAL ROM:      unchanged before and after
WORKBENCH-006:      UNTOUCHED
```

## Caller-search discipline

`tools/research/thumb_disasm.py::scan_thumb_bl_callers` was not used as evidence
for any claim in this ticket. Every field offset, instruction sequence and
constant above was read from the canonical ROM with Capstone 5.0.7. The helper's
known defects (54.9 % true call-site recall, 1,552 false-positive pairs, and the
`resolve_thumb_bl` word-alignment gap for unaligned `BLX` sites) are recorded in
`ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md` §7 and are not repaired here; the
generic helper still needs its own follow-up ticket.

## Independent review

### Reviewer A - engine/assembly

```text
VERDICT: REJECT
```

Reproduced independently, and confirmed: the identity (`0x082AD8BC`,
slot `+0x1C`, record `0x082ABF00`, handler `0x080088BD`), the grid at
`+0x04`/`+0x05` from the constructor's own `muls` and the driver's wrap, the 140
container pointers with `0x00000001` after the run, all 140 containers decoding at
their declared `0x400`, the byte census (index 0 absent, `1..228` used, and the
five dominant values), the constructor/driver field claims, the `1808/1808`
classification, the `1559` rendered count and the `452 / 0` composite census. It
also confirmed the negative claims: the handler word `0x080088BD` occurs exactly
once in the image and `0x082ABF00` exactly once.

Required findings, all accepted:

* **A1 (blocking): the payload is a 32x32 tile-index plane, not one byte per
  pixel.** Accepted in full. The correction is the whole of this revision.
* **A2 (blocking): the engine evidence quoted for the model was wrong.** Accepted:
  `0x06008000` does not occur anywhere in the image (0 pool words, 0 references);
  the real literal is `0x0600F000`; the count pair computes `(32 - m) / 2`
  halfwords × 16-bit control, i.e. `32 - m` bytes; `0x040000D4` is DMA3, not
  channel 0; and the `0x20`/`0x40` advances belong to the source and destination
  descriptors respectively.
* **A3 (blocking, consequential): the wrong unit was frozen into
  `canonical.py`, `render.py`, `map.json` and both PNGs.** Accepted; all corrected.
* **Nits A4-A6** (the 4-bpp argument does not discriminate pixels from ordinals;
  the visual-coherence validation was unsafe here; the register comments
  mislabeled the row and column roles). Accepted: the provenance and the
  validation wording are corrected, and the discriminating measurement is now a
  pinned ROM-gated test rather than a coherence claim.

### Reviewer B - rendering/completeness

```text
VERDICT: APPROVE (one required bookkeeping item, two non-blocking notes)
```

Reproduced independently: an own-renderer reconstruction of layer 2 and the
composite byte-identical to the frozen revision's artifacts; the hash-table diff
(2 added, 0 removed, 2 changed, nothing outside map 19); a full `--all` rerun whose
`hashes.csv` was byte-identical to the reviewed one; the no-prose and
no-generated-assets-tracked checks; and adversarial seam, tiling-control, palette,
alpha and cell-uniqueness checks. Its required item was the post-freeze commit,
which is resolved by freezing the corrected revision and recording it here; both
nits (the addend half of the ordering key doing no work on this map, and the one
duplicated palette colour at indices 0/1) are recorded.

Reviewer B's reconstruction was of the **wrong unit**, which is exactly what
Reviewer A's semantic measurement caught: two implementations agreeing on a
model does not establish the model. Both reviewers' artifact-level and
census-level results are unaffected by the correction and were carried forward.

### Correction record

Both required findings were closed by re-deriving the unit from the ROM:

* `TERRAIN_FIELD_CELL_TILES` replaces the pixel-size constant; the plane is
  8-bit tile ordinals.
* `read_terrain_field_plane` is new and `render_terrain_field` now resolves the
  plane through the owning map's assembled character block.
* The layer renders 3584x2560 and the composite is the same size; `map.json`
  publishes `cell_tiles`, `cell_grid_*`, `tile_grid_*` and the ordinal census, and
  no `cell_pixels`.
* The provenance's engine section was rewritten from a Capstone listing of the
  constructor, driver and blitter, with the non-existent literal and the swapped
  advance labels removed, and a §5 correction record added.
* A new ROM-gated test pins the semantic split (33 water ordinals at >= 0.547
  against 195 at <= 0.375, collapsing under permutation) so the unit itself is
  regression-guarded rather than only its consequence.
* The synthetic unit fixtures cannot catch the unit error - they are built from
  the same model - which is recorded as the reason the ROM-gated semantic test
  exists.

### Correction gate

Both reviewers' required findings are closed. Reviewer B's required item was
bookkeeping (freeze the reviewed revision), which is satisfied. Reviewer A's
three required findings are closed by the correction above and re-verified by the
full ROM-gated suite (81 passed) and the portable suite (1789 passed). Nothing in
this revision relies on `scan_thumb_bl_callers`.

Reviewer B's verdict was returned against the frozen revision's pixel-unit
artifacts. Its artifact-level, census-level, determinism, no-prose and
no-generated-assets results are unit-independent and were carried forward; its
own-renderer reconstruction was of the same wrong unit, which is why Reviewer A's
semantic measurement, not agreement between two renderers, decided the model. The
corrected revision re-validates the same properties: the byte-level diff against
the accepted library is unchanged (2 added, 0 removed, 2 changed, nothing outside
map 19), the map-side export is byte-identical across two independent runs, the
two artifacts are fully opaque and pinned by file and index-image digest, and the
corrected layer and composite were inspected as images.

## stopping point

`PROJECT_<local-state-name>` was not modified and no integration was performed. The result is
returned isolated on `asset-export-map19-001` for human review.
