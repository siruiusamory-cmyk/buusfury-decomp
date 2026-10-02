# Inferring a human-readable tileset from proven map usage

Evidence document for `TILESET-COMPOSITOR-001`. Canonical image: Buu's Fury USA
rev 0, SHA-256 `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

Claims use this repository's labels: **CONFIRMED**, **INFERRED**, **UNKNOWN**.

**No production behaviour changed. No ROM was written.** This ticket generates a
derived *view* of the tile banks under the ignored `build/` tree and adds an
inference module plus a CLI entry point. It changes no decoder, no renderer, no
project format and no capability count.

## 1. Result

A bank container is 16,384 decoded bytes: 256 tiles of 8x8 pixels in **storage
order**. Storage order carries no meaning, which is why a raw bank sheet reads as
a jigsaw - `docs/research/BUU_MAP_GRAPHICS_DIAG.md` section 6 establishes that
the jigsaw appearance is the storage order of the art and not a format layer.

The missing structure is already in the ROM. Every decoded map layer is a
regular-BG screen-entry plane, so the engine has already recorded which tiles
appear next to which, millions of times over. This ticket censuses that usage and
lays each bank's tiles out so that strongly related tiles sit together.

Over the whole canonical corpus, measured as the fraction of a sheet's
4-neighbour cell pairs whose two tiles were ever observed adjacent in a decoded
map:

| Sheet | Mean | Median | Banks at or above 0.60 |
| --- | --- | --- | --- |
| Raw (storage order) | **0.378** | 0.383 | **0 / 187** |
| Inferred | **0.731** | 0.747 | **156 / 187** |

**All 187 banks improve**, by a mean of **+0.352**; the smallest gain is
**+0.069**, so no bank is made worse. The corpus is **452 maps, 1,808 layers and
4,562,944 censused cells**, with **0 map failures**.

Three banks are carried as before/after evidence, chosen by a stated rule (most
occurrences among the least coherent raw sheets):

| Bank | Tileset | Occurrences | Raw | Inferred | Gain | Canvas |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | Tileset 1 (the supplied "jigsaw" example) | 3,420,904 | 0.327 | **0.814** | **+0.487** | 32x36 tiles |
| 11 | Tileset 12 | 185,161 | 0.425 | **0.703** | +0.278 | 48x40 tiles |
| 79 | Tileset 80 | 70,810 | 0.323 | **0.705** | +0.382 | 32x45 tiles |

Artifacts (ignored): `build/tileset-compositor/evidence/bank-{000,011,079}/`
and the metric table `evidence/evidence.json`.

## 2. What the atlas is

Three views per bank, all deterministic and all traceable to ROM identities.

**Raw** - the bank exactly as its container stores it, 16 tiles per row. This is
the before picture and the control. It is byte-for-byte the payload the
`bg_tilemap` renderer fetches tiles from at runtime.

**Observed** - the distinct 32x32 screen-entry chunks that reference the bank,
rendered through the owning map's own assembled character block. This is a
reference view and a regression oracle, so it is rendered by **calling** the
production renderer (`formats/bg_tilemap.render_entry_words`, the same entry
point `map_view.render_chunk_entries` uses) rather than by reimplementing it.
`tests/integration/test_tileset_compositor_rom.py` requires the two to be
byte-identical on real chunks.

**Inferred** - motif components of strongly related tiles, deterministically
packed onto a tile-cell canvas with at least one blank tile between components.

The atlas is a **view**, not a new ROM layout. A ROM tile may be presented more
than once when it takes part in more than one strong arrangement; that is a
legitimate duplicate presentation instance, it is bounded by policy, and every
instance states its own reason.

## 3. The algorithm

Module: `tools/webfoot/tileset_compositor.py`. The census is a pure function over
already-decoded planes (`census_planes`) and the ROM walk (`census_image`) only
decodes records into it, so a synthetic corpus exercises the same aggregate rules
with no image.

### 3.1 Census - `census_image`

For every one of the 452 maps, for every layer slot, the layer is reduced to its
screen-entry plane: a dominant chunk grid stitched by
`map_graphics.stitch_dominant_entries`, a screen-entry plane read by
`map_graphics.read_screenblock_entries`, or a terrain field stitched by
`map_graphics.stitch_terrain_field_plane`.

The key step is the **ordinal -> source** resolution. A screen entry names a
char-block ordinal, and the map's own selector stream resolves that ordinal to a
`bank:tile` source. So the census census keys on the source tile, which is the
ROM identity the atlas displays, and it never assumes an ordinal means the same
thing in two maps.

Cells that cannot be attributed are counted under their own name, never dropped:
`ordinal_past_selector_stream` (**24,331** cells in the canonical corpus) and
`ordinal_overlaid_by_animation` (0 in the canonical corpus, non-zero under test).
A null chunk pointer is a real state - the engine's occupancy test reads it as
unoccupied - so it names no container rather than a chunk at address zero.

### 3.2 Identity - `TileIdentity` and `DisplayIdentity`

Two identities are kept, deliberately.

* `DisplayIdentity(bank, tile, palette_bank, hflip, vflip)` is the exact
  presentation one occurrence asked for. `palette_bank` is decoded even though
  the canonical corpus is 8bpp and leaves bits 12..15 zero everywhere: the field
  is real, a 4bpp caller would use it, and dropping it would make the record a
  claim about the corpus rather than a statement about the entry.
* `TileIdentity(bank, tile)` is the canonical unflipped identity. Grouping,
  adjacency and motifs are computed on it, because a flip is a property of a
  *use* and folding it in would split one tile's evidence four ways.

### 3.3 Adjacency - directional, confidence-scored

Census counts `(source, direction) -> target` over the four cardinal offsets in
both axes, so `A -> right -> B` and `B -> right -> A` are different facts.
`out_degree` is every neighbour observation in that direction **including the
cells the census could not attribute**, so confidence is never inflated by
discarding negative evidence. Confidence is exact integer parts per million, never
a float.

### 3.4 Motifs - repeated 2x2 and 3x3 arrangements

Every fully-attributable 2x2 and 3x3 window is counted, keyed by its top-left
cell's bank. In the canonical corpus that is **151,261 distinct 2x2** and
**287,264 distinct 3x3** motifs. A motif whose cells are *all the same tile* is
counted but excluded from layout: it says the tile tiles, which is true of nearly
every ground tile and is no evidence for where anything belongs.

The motif index is anchor-scoped - a motif is stored under the bank of its
top-left cell - so motif pair support measures the windows a bank anchors. That
rule is recorded verbatim in every manifest as `motif_anchor_rule`. The adjacency
table, the primary signal, is exact for every source tile; only this booster is
anchor-scoped.

### 3.5 Constraints - one successor per direction, ties refused

For each `(tile, direction)` the best intra-bank successor is chosen by rank
`(-motif_support, -support, tile)`. Two rules then apply:

1. **A tie is refused.** Two tiles that follow equally often, with equal motif
   support, produce no constraint and a recorded `ambiguous_successor` conflict.
   This single rule is what makes it structurally impossible to force a
   conflicting constraint: the accepted set is per-direction unique by
   construction.
2. **The confidence floor is a floor for every accepted relationship.** Motif
   support raises a pair's rank - a repeated arrangement beats a merely frequent
   one - but it cannot admit a relationship the confidence floor refused.
   Otherwise a filler tile that borders eight tiles equally would still earn a
   successor from whichever arrangement happened to repeat, which is precisely
   the dominance the ticket asks the confidence term to prevent. That was a real
   defect found by a unit test and fixed
   (`test_a_common_filler_tile_does_not_dominate_the_layout`).

### 3.6 Components - merged from repeated motifs

Components are grown from the repeated motifs, strongest and largest first. A
motif that fits an existing component in exactly one place is merged, one that
fits nowhere starts a component, and one that fits in several - all of which are
*compatible* with the layout already inferred, which is what the fit test proves -
takes the first by component then offset, with the ambiguity recorded as
`ambiguous_motif_anchor`.

The repeated motif is the strongest structure the corpus offers: an exact
arrangement observed at least N times, with no ranking or threshold judgement
inside it. Merging them is what produces real 2D blocks rather than chains. An
earlier version of this module built components from per-direction best-successor
edges instead, and it fragmented badly - 847 components for bank 0 with 31x tile
duplication - which is why the motif merge is the primary structure and adjacency
only attaches what no motif reached.

Tiles no motif reaches are attached through their strongest accepted adjacency
constraint wherever a matching free cell exists. Whatever is still unplaced is
reported with role `unconstrained` or `unused`, never dropped.

### 3.7 Packing - a roughly square canvas with gutters

Components are ordered by descending area, then tile count, then support, then
root tile, and shelf-packed. The canvas starts at `pack_start_width` tiles (16)
and widens to the smallest multiple of that width whose square holds everything
placed, then further only if one component does not fit. Empty cells are **kept**
- the canvas is a full rectangle, the count is reported, and a digest over the
exact empty coordinates makes the padding verifiable rather than merely claimed.

The user's stated reading of the specification is honoured exactly: "8x8" means
the native 8x8-pixel hardware-tile alignment, not an 8x8-tile atlas block, so the
packing unit is one tile cell with at least a one-tile gutter.

### 3.8 Why duplicates are permitted but bounded

`max_instances_per_tile` (3) bounds how many times one ROM tile may be presented.
The atlas is a view, so a tile in several strong arrangements earns several
instances - but a highly repetitive texture earns hundreds of equally valid ones,
and a sheet of those is noise. Instances past the budget are counted in an
`instance_budget_reached` conflict, never silently created.

## 4. Provenance

Every displayed cell resolves to a real source tile. The manifest maps it
through the census' own usage record for that tile, which carries:

- the **original tile id** (`bank`, `tile`) and the **source bank**;
- every **palette bank** and every **flip state** the tile was ever presented
  with, with counts (`display_identities`);
- the complete set of **maps** that use it, the **layer forms** they use it in,
  and the **chunk containers** it appears in;
- the complete set of distinct **raw 16-bit screen-entry words** it was reached
  by;
- the occurrence count, a **SHA-256 over the complete occurrence stream** in a
  fixed-width encoding, and exact occurrence **samples** (each with map, layer
  slot, chunk address, plane coordinates, raw word and ordinal).

Because the digest covers the whole stream, a sample is provably drawn from a
complete list rather than replacing it. `webfoot tileset census ROM --bank N
--occurrences FILE` writes that complete list as JSONL when a caller needs
every occurrence rather than the digest.

Every placement carries exactly one `Evidence` record: `motif` (with size and
support), `adjacency` (with the full constraint: support, out-degree, exact
confidence in ppm, motif support), or `no_constraint` - which states plainly that
the census offered nothing and the tile was kept rather than placed on a guess.

Conflicts are recorded, not discarded: `ambiguous_successor`,
`ambiguous_motif_anchor`, `instance_budget_reached`. The manifest enumerates the
first `max_recorded_conflicts` (64) and reports `conflict_count` plus a
`conflicts_sha256` over **all** of them, so the cap bounds the document without
weakening the claim that nothing was dropped.

## 5. Determinism

Same inputs, byte-identical manifest content and pixel-identical images.
`tests/unit/test_tileset_compositor.py` asserts both directly, and
`tests/integration/test_tileset_compositor_rom.py` asserts it over the real
corpus and across two independent bundle writes.

Nothing reads a clock, a filesystem, a random source or a set's iteration order.
Every aggregate that reaches output is sorted by an explicit key, every ratio is
an exact integer in parts per million, and every digest is taken over a
fixed-width encoding. An intermediate refactor of the census module was verified
to reproduce **every artifact hash unchanged** before and after.

**One scope qualifier, found by the independent review and now pinned by test.**
The claim holds for the ROM entry point, which supplies a fixed plane order
(maps by index, then layer slots, then cells in raster order). It does *not* hold
for the public `census_planes` API in the absolute: every derived structure -
components, cells, the canvas, the conflict digest - is order-invariant, but a
tile's `occurrences_sha256` and its quoted samples follow the order occurrences
were walked in, so reordering the supplied `planes` reorders them. That is now
stated in the module and `census_planes` docstrings and asserted from both sides
by `test_determinism_is_pinned_to_the_supplied_plane_order`.

## 6. Cross-check against the supplied resource library

The supplied resource library's `Tilesets` directory holds 187 tilesets, each a
16x16 raw
`Sheet.png` and a `Tileset.json`. Two things were confirmed against it:

- **Tileset N is bank N-1, CONFIRMED.** `Tileset 1`'s declared
  `containerAddress` is `0x080945c0`, which is exactly bank 0's container in the
  ROM's own bank table at `0x08179764`; `Tileset 142` is `0x0813cb6c` = bank 141,
  and `Tileset 187` is `0x08177ab8` = bank 186, the one short bank
  (`0x3C40` bytes, 241 tiles).
- **That library is the PRE-correction compile.** Decoding each bank with the
  shipped decoder, unswizzling every 64-byte tile and comparing RGB against each
  `Sheet.png`: **110 banks match and 77 differ**. `BUU_MAP_GRAPHICS_DIAG.md`
  section 1 records the LZ literal-base correction's blast radius as exactly
  **77 / 187** banks. The sets agree, so the supplied sheets show the old decode
  for those 77 banks - including bank 141 (Tileset 142), the bank that section
  3.7 names explicitly.

This is a corroboration of the shipped correction obtained independently of the
runtime capture, and it is a caution for anyone reading the supplied sheets: the
Raw view this tool writes is the corrected decode, so it is expected to differ
from `Sheet.png` for those 77 banks. It is **INFERRED**, not CONFIRMED, that the
library was generated before the correction; what is measured is that the two
decodes differ on exactly the banks the correction is documented to change.

## 7. Boundaries

- **No ROM writes.** The module reads bytes and writes images/JSON under
  `build/`. `prepare_output_root` refuses any path inside the repository that is
  not under `build/`, refuses the repository root, and refuses a non-empty
  directory, so a run cannot scatter generated proprietary artwork through the
  tree.
- **No semantic labels.** Nothing here says "house", "tree" or "cliff". Tiles are
  identified by bank and id; relationships are counts.
- **No machine learning and no image similarity.** Frequency, adjacency and motif
  layout are the whole algorithm; every placement names the evidence that
  produced it.
- **No map editing UI, no warp/connection work, no map-102 investigation, no
  capability-count change.**

## 8. Confidence and limitations

- The **algorithm** is deterministic and mechanically tested; that is
  `CONFIRMED` by the portable and ROM-gated tests.
- The **readability improvement** is measured by the coherence metric above on
  all 187 banks, and is `CONFIRMED` as a measurement. That the result *looks*
  better to a human is a separate claim, and per the ticket it is for human
  acceptance, not for a test.
- The **mean inferred coherence is 0.731, not 1.0.** The remainder is honest: a
  bank's tiles sometimes appear only in arrangements that are themselves
  ambiguous, and a tile with no repeated arrangement cannot be grouped. Bank 178
  is the clearest example - 256 tiles used, no repeated 2x2 or 3x3 arrangement at
  all, so its inferred sheet is storage order and says so. The tool reports that
  rather than inventing a layout for it.
- **Duplicate instances mean the sheet is not a bijection onto the bank.** A
  reader counting cells will count more cells than the bank has tiles. The
  per-tile `occurrence_count` and the canvas' `placed_cells` are different
  quantities and both are reported.
- Motif pair support is anchor-scoped, as stated in section 3.4. A motif whose
  top-left cell is in another bank does not boost this bank's ranking. The
  adjacency term, which decides the confidence floor, is not affected.
- The **observed** view shows first-64 chunks per bank by default
  (`--observed-limit`), while the manifest reports the full
  `observed_chunk_count`. The reference view is a sample of the usage, not all of
  it; the census counts all of it.

## 9. Reproducing this document

```text
python -m tools.webfoot tileset census "roms/Dragon Ball Z - Buu's Fury (U).gba"
python -m tools.webfoot tileset atlas  "roms/Dragon Ball Z - Buu's Fury (U).gba" \
    --bank 0 --bank 11 --bank 79 --out build/tileset-compositor/evidence
python -m tools.webfoot tileset atlas  "roms/Dragon Ball Z - Buu's Fury (U).gba" \
    --all --no-observed --out build/tileset-compositor/all
```

The coherence table and the selection rule live in the evidence generator that
produced `evidence.json`; it is a read-only probe and is not part of the shipped
module.

Portable tests: `pytest tests/unit/test_tileset_compositor.py` (39 tests, no ROM).
ROM-gated tests: `pytest tests/integration/test_tileset_compositor_rom.py`
(9 tests, ~3 minutes, needs the canonical image).

## 10. Independent review

A fresh-context reviewer, given the frozen candidate, the diff and this brief,
returned **APPROVE WITH NON-BLOCKING NOTES** after running its own synthetic
probes against the real code rather than arguing from the diff. It confirmed, by
probe: the conflict policy does not force a constraint (motif merges only land on
an empty cell or the same tile); `out_degree` including unattributed neighbours
makes confidence conservative, not inflated; the observed-view equivalence is not
circular because both sides delegate the tile path to one function.

It raised three notes, all of which are resolved rather than banked:

| Note | Disposition |
| --- | --- |
| **NOTE-1 (MEDIUM)** the module's determinism claim was absolute but the occurrence digest follows the supplied plane order | Docstrings in the module and `census_planes` now state the scope exactly; `test_determinism_is_pinned_to_the_supplied_plane_order` asserts both the order-invariant half and the order-dependent half |
| **NOTE-2 (LOW)** the four "mutation" tests were positive controls; their `pytest.fail` guards could not fire | rewritten as genuine mutations: each defines the check, shows it accepts the correct artefact, **injects the break** (a direction-blind adjacency table, an ordinal-only identity key, six forged provenance records, a merged bank partition) and requires rejection |
| **NOTE-3 (LOW)** the observed sheet's chunk placement was verified only by dimensions | `test_observed_sheet_places_each_chunk_at_its_own_offset` now asserts each of two different chunks lands at its own offset with its own pixels and that the gutter between them stays transparent |

The resolutions were re-frozen (`1f33e63412ff5fb086dbbf749f7b147cbb81520b`) and re-reviewed on `a commit since folded into its successor`, which
returned **APPROVE** - *"All three prior notes are fully resolved; nothing new
blocks."* The reviewer confirmed each resolution individually, verified by diff
that the resolution commit changed no production logic (two docstring insertions,
zero code lines), re-ran the portable suite (39 passed), and independently
re-checked the six probe areas with no findings:
