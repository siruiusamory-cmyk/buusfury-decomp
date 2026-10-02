# Map 19 asset export verification

The map-19 terrain and asset-export corrections, the byte-level change audit, the
independent re-measurements and the runtime placement validation.

Canonical image: the verified Buu's Fury profile used by the export reader.

## Scope of the pass

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
  water (background-palette indices 83 and 177), the lowest such share being
  `35/64 = 0.546875`, while all 195 others select a tile at `0.375` or less - a
  clean split whose plane-level water fraction is `0.6188` as read against a median
  of `0.0981` over 200 seeded random ordinal permutations. Ordinal `2`
  alone (40.7 % of the plane) selects a tile that is 100 % water; `43`/`119` green
  land, `137` sand, `76`/`73` rock, `19` snow.

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
                    passes). the second verification pass re-ran a maps-only export and matched all
                    2,470 map-side rows byte-for-byte, and 33 of its focused
                    integration tests passed.
VISUAL VALIDATION:  PASS as a coherence check only - layer_2.png at 3584x2560 is
                    clean game art: blue sea, a coastline, rivers, snow-capped
                    mountains, forest and sand, with no seams and no repeated or
                    garbage blocks. Visual coherence is validation, not evidence;
                    the unit was established by the semantic split recorded above.
                    the second verification pass re-measured the seams independently: boundary deltas
                    fall below interior deltas at both the 32x32-cell and 8x8-tile
                    scales, while column-major and x-descending alternatives are 8x
                    to 10x discontinuous.
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

The layer's artifact budget, measured: `layer_2.png` is 845,573 bytes,
`composite.png` 851,442 bytes, both 3584x2560 and fully opaque; map 19's composite
is the 0.18 % corner overlay described in the provenance, and no other map's
composite changes size.

## Caller-search discipline

`tools/research/thumb_disasm.py::scan_thumb_bl_callers` was not used as evidence
for any claim in this record. Every field offset, instruction sequence and
constant above was read from the canonical ROM with Capstone 5.0.7. The helper's
known defects (54.9 % true call-site recall, 1,552 false-positive pairs, and the
`resolve_thumb_bl` word-alignment gap for unaligned `BLX` sites) are recorded in
`ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md` §7 and are not repaired here; the
generic helper still needs its own follow-up record.

## Independent verification

### Second verification pass at the corrected revision

```text
VERDICT: REJECT
```

Reviewed revision `3529b80f`. The three original blockers were confirmed closed:
A1 (the payload is a 32x32 tile-ordinal plane), A2 (the destination literal is
`0x0600F000`, `0x06008000` has zero hits in the image, the count pair computes
`(32 - m) / 2` halfwords under a `0x8000` control = `32 - m` bytes, `0x040000D4`
is DMA3SAD, and in all nine blocks the `0x20` advance is the source register and
the `0x40` the destination register), A3, A4, A5 and A6. The verification pass reproduced
the record chain, the container run, the plane digest, the ordinal population, the
character block, the semantic split, both artifacts' digests and a `git archive`
test run, and confirmed the correction history is preserved and reachable through
`git show c010009`.

Required findings, all accepted and closed:

* **A7: the falsified one-byte-per-pixel unit survived in three places**
  (`canonical.py` class docstring, `buu_resource_export.py` `render_layer`
  docstring, and the integration-test constant comment). Independent review found
  these by the record's own "no stale unit" criterion. All three are corrected.
* **A8: the constructor description was wrong.** The nine-slot init writes the
  constant `0x08071020` - a stored 0x400-byte all-zero ROM cell, the "no cell"
  placeholder - to `object + 0x08 + 4*i`, and `0xFF` to `object + 0x2C + 4*i`; the
  real slot buffers are installed by the driver at `0x08008688`..`0x08008698`.
  Reproduced from the ROM and corrected in the provenance.
* **A9: the row-stride item was bounded wrongly.** Its premise was false: the
  control word's size field (`2`) gives a 64-byte row, so the `0x40` destination
  step *does* reconcile with it. The earlier "does not reconcile" record is
  withdrawn. **This finding's reasoning was itself wrong and is superseded by
  provenance §8:** `BGxCNT` bit 6 is the **mosaic** bit, not an affine selector, so
  the control word does not say "text" at all - affine-ness comes from the DISPCNT
  video mode. The text size this entry quoted, `512x256` = 32 entries x 2 bytes,
  was size-field-1 geometry; size field 2 is `256x512` = `32 x 64` entries in text
  mode and `512x512` = `64 x 64` entries in affine mode. What remains open is
  DISPCNT's video mode for map 19 (from the per-map context field at `ctx + 0xA2`),
  with the affine reading `INFERRED`, and how a byte-granular copy lands in a
  16-bit-entry map if the mode is text.
* **A10: the affine attribution over-claimed.** The 64-byte row follows from the
  size field, not from affine projection; the causal sentence is removed and the
  affine reading is labelled `INFERRED`.
* **A11: the corrected freeze SHA was recorded nowhere.** The identity block now
  names the start SHA, the rejected revision and the corrected revision.

Nits accepted: the quoted listing's addresses were one instruction early (the
`mov r6,lr` / `mov r6,ip` moves were dropped) and are corrected to
`0x08008270`/`0x08008274`/`0x08008282`/`0x08008288`; the count comment now reads
`((32 - m) << 15) >> 16`; "nine structurally identical blocks" now states the two
clip variants; and the terrain-classification sentence is labelled `INFERRED`.

### First verification pass: engine and assembly

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

### Rendering and completeness verification

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

the second verification pass's reconstruction was of the **wrong unit**, which is exactly what
the first verification pass's semantic measurement caught: two implementations agreeing on a
model does not establish the model. Both verification passes' artifact-level and
census-level results are unaffected by the correction and were carried forward.

### Correction table

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
* A new ROM-gated test pins the semantic split (33 water ordinals at more than half
  water against 195 at `<= 0.375`, with a permuted assignment as the control) so the
  unit itself is regression-guarded rather than only its consequence.
* The synthetic unit fixtures cannot catch the unit error - they are built from
  the same model - which is recorded as the reason the ROM-gated semantic test
  exists.

### Verification of the changed surface

```text
VERDICT: APPROVE WITH NON-BLOCKING NOTES
```

the second verification pass re-derived the changed surface with its own packed decoder, its own
raster plane, its own tile lookup and its own PNG decoder: the ordinal plane and
its digest, the 539-tile character block, the 3584x2560 index image, and
**0 mismatching pixels of 9,175,040** against both `layer_2.png` and
`composite.png`. It proved the placement rule is load-bearing (ascending order
would equal the terrain field exactly; all 16,320 pixels the composite differs by
lie inside the top-left 256x256), reproduced the hash-table diff (2 added, 0
removed, 453 changed, 0 changed PNGs anywhere) and verified the 452 changers are
exactly the two new fields, exercised the CLI flag both ways (all 452 flip, no
image byte changes), and re-measured the seams, the water/land split and the
no-prose/no-tracked-asset checks.

Its required item was the same bookkeeping item - freeze a clean tree - which this
revision satisfies. Its nits are applied: the §6 register values now quote the
retained capture, the listing names `mov r6, ip` and stores `DMA3DAD` at
`0x08008274`, the water-share threshold is `35/64 = 0.546875`, the permutation
control is stated as typical rather than universal, the origin overlay is described
as the 0.18 % corner it is, and the root extents are marked unreconciled. Its third
nit identified a **pre-existing** mislabel (`0x04000200` is `REG_IE` bit 1, the
HBlank interrupt, not `DISPSTAT` bit 1) present in the accepted text from
`9154fed`; it is corrected in the three files this record owns. The same mislabel
also survives in the earlier record's records
(`docs/research/ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md` and
the earlier map-handler verification record), which are outside this
record's scope and are recorded here as a finding for a documentation sweep rather
than edited.

### Re-verification after correction

the first verification pass's third pass returned `REJECT` on five documentation items (R1-R5) plus
seven nits, explicitly stating that no artifact, field, mechanism or code change
was implied. All of them are corrected in `db52eac`: the `BGxCNT` bit-6 error is
replaced by the correct mosaic/mode account, the text-mode size is stated as
`256x512` = `32 x 64` entries, the open item is reframed as DISPCNT's video mode
from the per-map context field, the map area is `4 KiB`, the §6 register values
quote the retained capture, the listing and count comments are exact, and the
correction history names each revision.

the second verification pass's re-review of the same material returned `APPROVE WITH NON-BLOCKING
NOTES`, with its required bookkeeping item satisfied and its nits applied.

**State of the gate: OPEN.** the first verification pass's fourth pass reviewed `07a85b3` and
returned `REJECT` on the record's own review record: the corrected provenance and
`asset-export.md` text was verified right, but three of the falsified statements
survived verbatim in this sheet (the A9 entry's bit-6/mode reasoning and its
`512x256` size, and Gate 2's `0x78A3` register block), plus seven nits and one
adjacent finding. All of them are corrected in `0bc8958`:

* the A9 entry is annotated as superseded by provenance §8 (bit 6 is mosaic;
  affine-ness is the DISPCNT mode) and its `512x256` text is corrected in place;
* Gate 2's observed block now quotes the retained capture's actual values;
* the test docstring's `0.547` is replaced by `35 of the tile's 64 pixels`;
* the permutation control is restated with its seed, its median, and the honest
  note that the `+1` and `*7+11` displacements do **not** collapse - my earlier
  `0.052`/`0.051`/`0.086` figures were wrong and are withdrawn;
* §10's open item names DISPCNT and the `ctx + 0xA2` source;
* the identity blocks name every revision and no longer mislabel `3529b80f`;
* the `REG_IE` correction is scoped to the three files this record owns, with the
  surviving instances in the earlier record's records recorded as a finding for a
  documentation sweep;
* provenance §8 records that the accepted `LOGX-TILE-001` text reads size field 2
  as `512x256`, states why the `256x512` reading is the correct one, and declines to
  silently reconcile the two.

No artifact or code behaviour changed in any of these passes: an AST comparison of
every `tools/export/*.py` across `c8cf6c6`..`07a85b3` shows the only differing file
is `canonical.py`, whose AST is identical (comment-only), and the export is
byte-identical. A further confirming verification pass over `0bc8958` is the
outstanding formal step; this record does not claim that pass happened, and the
gate stays `OPEN` until it does.

## World-map hypothesis

The human observation that map 19 is the flying world map was tested against the
ROM and classified **`PARTIALLY CONFIRMED`** - never on visual resemblance, which
is recorded as a lead only. Established: the `0x080088BD` handler occurs exactly
once in the image so the terrain field is one-off; the field is 448x320 tile
ordinals = 3584x2560 pixels, far beyond one screen; its ordinals resolve to
terrain types (`INFERRED`); it is drawn through BG2 (`0xBE83`: priority 3, map
base 30, 256-colour) with `BG2PA`..`BG2PD` written per scanline for VCOUNT
55..159; map 19's declared root extents (3345x2401) are the largest of the 55
distinct extent pairs across all 452 maps; and the driver streams a nine-cell 3x3
window over a 14x10 grid, so the engine copies a **window** of the field rather
than holding it whole. Not established, and therefore not claimed: that the
overworld scene displays this map, and that player flight drives the viewport -
both need the runtime observation this record could not obtain.

The consequence is recorded plainly: **resource completeness** and **runtime
screen composition** are different claims. `maps/map_019/layer_2.png` is complete
and accepted as a resource; a 3584x2560 `composite.png` is a derived utility
artifact, not a plane the hardware displays whole, and its placement is
provisional.

## Gate 2 - runtime placement validation

**Classification: COMPOSITE_PROVISIONAL_RUNTIME_CAPTURE_UNAVAILABLE.**

**Method.** The project's pinned emulator was used, not another static parser:
mGBA 0.10.5 at `build/tools/mgba-0.10.5/extracted/mGBA-0.10.5-win64/mGBA.exe`,
`FileVersion 0.10.5.0`, SHA-256
`5A3C98C2984DD04BD0D7C9378CDFAE937AE0D73A196C880BB2EECF3B254AF247`, against the
canonical ROM with its local save, in an isolated portable profile
(`savegamePath`/`savestatePath`/`screenshotPath` all outside the repository).
A read-only observer, `tools/runtime/map19_bg_placement.lua`, was injected
through the tracked `tools/runtime/inject_mgba_lua.ps1` path and ran 900 emulated
frames, recording `DISPCNT`, `BG0CNT..BG3CNT`, the background scroll and affine
registers, the active-map pointer, the raw bytes of `0x0600F000` and
`0x0600E000`, and mGBA's own screenshots. The observer performs no emulated-memory
write and no input injection.

**Observed.**

```text
frames run                900
active_map_ptr            0x00000000   (no MapEntry loaded)
DISPCNT                   0x00000200   (forced blank, mode 0)
VCOUNT                    0x000000A0
DISPSTAT                  0x00000019
frame 900:  BG0CNT 0x0000  BG1CNT 0x1E83  BG2CNT 0x1F83  BG3CNT 0x0F83
            BG0HOFS/BG0VOFS .. BG3HOFS/BG3VOFS   0x0001
            BG2PA..BG2PD                          0x0001
frame 300:  all scroll and affine registers         0xFFFB
0x0600F000                ascending 0x0001, 0x0002, ... halfword ramp (boot VRAM)
0x0600E000                the observer's own distinct boot contents
screenshot frame 600      the game's title screen
```

These are the values actually present in the retained capture. They are boot-state
registers on a screen no map owns, so they are recorded raw and nothing is inferred
from them.

The session never left the title screen, so it is not map-19 evidence and no
display-orientation inference is drawn from it.

**Why map 19 was not reached.** The local `roms/*.sav` is a save image, not a
savestate: reaching map 19 from it requires the title/load menus to be driven with
deterministic input, and no savestate already inside map 19 exists in this
environment (the tracked states are P-002 / placement-pos / ROM-006 captures on
other maps). The tracked GDB client is read-only by design, so the active-map
pointer cannot be forced either. The observer's input path works
(`emu:setKeys`), but driving an unknown menu path reliably is outside this
record's scope.

**Missing evidence, stated exactly.** One map-19 session reading: `DISPCNT`'s mode
and enabled backgrounds; `BG2CNT` as the background programmer writes it;
`BG2HOFS`/`BG2VOFS`; `BG2PA..BG2PD` sampled inside the VCOUNT 55..159 window the
IRQ handler writes; and `0x0600F000` compared byte-for-byte with the ROM-derived
ordinal plane. Those five readings settle which background displays the field,
whether the whole 448x320 plane is ever resident, and whether the placement is a
whole-layer blit or a windowed view.

**Consequence.** `maps/map_019/layer_2.png` (3584x2560) is accepted. The
composite rule is a pre-existing `INFERRED` model, and the placement dimension is
not validated, so:

* every composite now carries `composite_placement_model` and
  `composite_runtime_status` in `map.json`; without
  `--runtime-placement-validated` that status is
  `provisional_runtime_capture_unavailable`;
* map 19's composite is **provisional**, and the pipeline does not claim
  452/452 composites runtime-validated. The 452 composites remain structurally
  justified - no layer is withheld and no layer is silently omitted - which is a
  different claim from runtime placement.

## Runtime tooling change

One tracked file changed for the runtime attempt:
`tools/runtime/inject_mgba_lua.ps1` gained one additive allowlist entry for
`tools/runtime/map19_bg_placement.lua`, which is the repository's documented way
to add a runtime observer (`tools/runtime/README.md`: "Add new files; never tidy
old names"). The entry was spliced into the byte stream rather than written
through a text round-trip, because that file mixes CRLF and bare-LF lines and a
normalising write made `git diff --check` flag every touched line; the resulting
diff is six added lines and nothing else. The observer itself is new and
read-only. No launcher, client or GBA-tooling behaviour was altered, and the
generic Thumb helper was not touched.

## Validation after the placement change

```text
PORTABLE TESTS:     1789 passed, 8 skipped (`pytest tests/unit`)
ROM-GATED TESTS:    81 passed (`pytest tests/integration/test_asset_export_rom.py`)
DETERMINISM:        PASS (two independent full exports; the map side is
                    byte-identical and the change is confined to map.json)
UNRELATED PNG CHANGES: 0
DIFF CHECK:         `git diff --check` clean
```
