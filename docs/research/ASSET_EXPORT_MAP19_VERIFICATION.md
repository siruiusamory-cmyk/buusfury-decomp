# ASSET-EXPORT-MAP19-001 - review

```
START SHA:    c6821d450b475ec5d262f0b239b3f2dce8de6559
              (the current accepted tip of asset-export-map-handlers-001,
              verified as: 9154fed and 5ab0f5c are ancestors, the worktree is
              clean, and both reviewer approvals are recorded in
              docs/research/ASSET-EXPORT-MAP-HANDLERS-001-review.md)
BRANCH:       asset-export-map19-001
COMMITS:      this ticket's own commits on top of the start SHA
CANONICAL ROM SHA BEFORE: 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
CANONICAL ROM SHA AFTER:  940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
```

## What the ticket set out to do

Resolve the one `static_graphical_assembly_unresolved` reference left by
ASSET-EXPORT-MAP-HANDLERS-001: map 19, root `0x082AD8BC`, slot `+0x1C`, record
`0x082ABF00`, handler `0x080088BD`.

## What was found

The container geometry, not a new graphics format. Each of the record's 140
containers decodes to exactly `0x400` bytes, and the engine's own blitter fixes
its shape:

* the driver indexes cells as `wrapped_y * grid_x + wrapped_x`;
* the blitter's DMA source span is one 32-byte raster row, and its source advance
  per iteration is `0x20`;
* its destination row is 64 bytes wide at one byte per pixel, in the background
  character area at `0x06008000`;
* the payload carries contiguous palette indices `1..228` with index `0` absent,
  which a packed 4-bpp arrangement cannot produce.

So a container is a 32x32 one-byte-per-pixel cell and the 140 cells lay out in
raster order to a 448x320 field. The full evidence is in
[`../research/ASSET_EXPORT_MAP19_PROVENANCE.md`](../research/ASSET_EXPORT_MAP19_PROVENANCE.md).

## Result

```text
PREVIOUS CLASS:  static_graphical_assembly_unresolved
FINAL CLASS:     static_graphical_terrain_field

MAP:             19
LAYER SLOT:      2  (root +0x1C)
LAYER RECORD:    0x082ABF00
HANDLER:         0x080088BD
ASSEMBLY MODEL:  140 containers of 0x400 one-byte-per-pixel bytes = 32x32 cells,
                 container y*grid_x + x at (x*32, y*32), 448x320 total
SOURCE RESOURCES: 0x0829F814 .. 0x082ABDF4, every one kind 1 declaring 0x400
BG / VRAM:       destination base 0x06008000 (background character area, one byte
                 per pixel); the record's own grid at +0x04/+0x05

LAYER IMAGE:     EXPORTED  maps/map_019/layer_2.png  448x320
                 image_sha256 3e57e01d60200cde0f74e42be2f68cbb73114f10f0a36e1345f9140a13104b7b
                 index digest 883f6db20c3b908eb61e7d7bcd0c16fade994e184e95c8d3118d85cbbc4976ec
COMPOSITE:       EXPORTED  maps/map_019/composite.png  448x320
                 image_sha256 37c1452e0a67ab70a590573e50531e700ecade22144f55ac68ff75d3a9dce7df
                 index digest deb8fec4fe627b78f8feaeed8a9d69759eaf967b2195bf240d5c288a73a2d170

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

The isolated full export (`<resource-library>_Map19_Test2`, 86,444
artifacts, 0 failures) was diffed against the accepted library
(`<resource-library>_MapHandlers_Test5_Audit`, 86,442 artifacts) by the
audit hash table:

```text
ADDED:    2   maps/map_019/layer_2.png
              maps/map_019/composite.png
REMOVED:  0
CHANGED:  2   maps/map_019/map.json
              metadata/maps.json
UNRELATED PNG CHANGES: 0
```

Every sprite, tile, chunk, palette and dominant-layer artifact is byte-identical
to the accepted library. The unchanged-population counts were re-measured in the
full export and hold at their accepted values: sprite definitions 297, animation
slots 4070, non-null animations 1721, frames 10980, pieces 11005, structured
sprite graphics 7390, tile banks 187, dominant chunks 3745.

## Validation

```text
DETERMINISM:        PASS (the export is a pure function of the ROM: the layer and
                    composite digests are reproduced by the pinned tests from the
                    ROM alone, and the exporter's own repeat-render test passes)
VISUAL VALIDATION:  PASS as a coherence check only - layer_2.png at 448x320 is
                    coherent art (an island landmass: a red mountain crest along
                    the top, green interior, yellow shoreline, a dithered water
                    surround), with no seams at the 32-pixel cell boundaries and
                    no repeated garbage. Visual coherence is validation, not
                    evidence; the assembly model comes from the engine's code.
PORTABLE TESTS:     1787 passed, 8 skipped (`pytest tests/unit`)
ROM-GATED TESTS:    79 passed (`pytest tests/integration/test_asset_export_rom.py`,
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

Two fresh-context reviewers are run against a frozen commit:

* REVIEWER A - engine/assembly: the handler path, the field accesses, the source
  resources, the BG/VRAM relationship and the negative claims.
* REVIEWER B - rendering/completeness: an independent reconstruction of the
  layer and the composite, the byte-level diff, determinism, the no-prose policy
  and the no-generated-assets-tracked check.

Verdicts and the corrections applied are recorded below once the reviewers have
reported.
