# CQA-04-DECODE-STACK-AUTHORITY-001

**STATUS: implementation frozen for independent review.** One reader of record per
shared map/graphics binary concept; the production map-layout writer no longer
reads through `tools.export`; equivalence over the common corpus is proved by a
ROM-gated test; the intentional capability differences are classified rather than
left as parser drift.

- **START SHA:** `66a75651a9b30659ce2cdb9d84b42cc24b333796` (`origin/master`)
- **WORKTREE:** `<temp>\log1-remake-cqa-04` (detached at START SHA, clean)
- **REFERENCE CHECKOUT:** `<checkout>` on `workbench-006`
  (`b4b13c9c418910d77c7916644aa881d25dd52f3b`) - untouched, not used as baseline
- **CANONICAL ROM:** `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`,
  8,388,608 bytes; hash verified before and after every ROM-gated run

Audit finding:
[`../research/PROJECT_CODE_QUALITY_AUDIT.md`](../research/PROJECT_CODE_QUALITY_AUDIT.md)
section C.2 (CQA-04), section F group D.

---

## 1. The duplication, inventoried

Measured before the change, not taken from the audit's list. For each pair the
question asked was: which module owns the byte/semantic interpretation, who
consumes it, and does the write path depend on either copy?

| Concept | Export-side owner (before) | SDK-side owner (before) | Agreed? | Write path? |
|---|---|---|---|---|
| MapEntry table address/count/stride | `canonical.Rom.map_entry_*` | `map_render.resolve_descriptor` + `formats/map_entry` layout | same values, two code paths | **yes** (`canonical`) |
| MapEntry record fields | `canonical.read_map_entries` | `map_render.resolve_descriptor` (`+0x2C` by arithmetic) | same, independently derived | **yes** |
| Layer record + handler classification | `canonical.read_layer`/`LayerRecord` | `map_render._decode_layers` | 5 handlers vs 1; **divergent** | **yes** |
| Dominant chunk entry words | `canonical.read_chunk_entries` | `map_render._decode_layers` | equivalent | **yes** |
| Dominant grid stitching order | `map_browser._stitch_dominant` | `map_render._decode_layers` | equivalent, two loops | indirect |
| Selector delta stream | `canonical.read_selector_stream` | `map_render.decode_tile_selectors` | equivalent | **yes** |
| Character-block assembly | `canonical.assemble_char_block` | `map_render.reconstruct_map_assembly` | equivalent, different coverage checks | **yes** |
| Animated-tile records + first frame | `canonical.read_animated_tiles` | inline in `map_render.reconstruct_map_assembly` | equivalent | **yes** |
| Tile unswizzle | `render.unswizzle_tiles` | `sprite_graphics.unswizzle_tiles` | byte-identical copies | indirect |
| Tile flip | `render.flip_tile` | `bg_tilemap._flip_tile` | byte-identical copies | no |
| Tile-entry bit fields | `canonical.TILE_ENTRY_*` | `bg_tilemap.ScreenEntry.decode` literals | same bits, three spellings | indirect |
| Entry-to-pixels tile render | `render.entry_tile`/`render_entries` | `bg_tilemap.render_entries` | equivalent, two implementations | no |
| OAM dimension table | `canonical.OBJECT_DIMENSIONS` | `sprite_graphics.OBJECT_DIMENSIONS` | identical tuples | no |
| BG palette requantisation | `render.bg_palette_rgb` | `map_render.decode_bg_palette` | equivalent | no |
| Screen-entry plane (2 handlers) | `canonical.read_screenblock_entries` | **absent** | export only | no |
| Terrain field (Map 19) | `canonical.read_terrain_field_*` | **absent** | export only | no |
| Bank table | `canonical.read_banks` (address literal) | **absent** (renderer asserts `0x4000`) | **divergent extent** | indirect |
| Container decode strictness | `webfoot_strict.unpack` (end marker) | `webfoot_lz.unpack` (exact size) | deliberately different postcondition | **yes** |

Two real divergences, not three: the layer-handler coverage and the bank-container
extent assumption. Both are recorded below.

## 2. The reader of record, per concept

Low-level binary concepts moved to the SDK's format layer; export tooling consumes
them. The dependency direction is now SDK authority -> export consumer.

| Concept | Reader of record |
|---|---|
| MapEntry table, record fields, root resolution | `formats/map_graphics.read_map_entries` (over `formats/map_entry.MapEntry`, the byte-exact record the writer serializes) |
| Layer record, handler, chunk window, terrain grid | `formats/map_graphics.read_layer` / `read_layers` |
| Layer classification and renderability | `formats/map_graphics.LayerRecord.classification` and its predicates |
| Dominant chunk words, grid stitching | `formats/map_graphics.dominant_chunk_words`, `stitch_dominant_entries` |
| Selector delta decode | `formats/map_graphics.decode_selector_stream` / `selectors_from_payload` |
| Character-block assembly, banks, animations | `formats/map_graphics.assemble_char_block`, `assemble_map_char_block`, `read_animated_tiles`, `read_banks` |
| Screen-entry plane, terrain field | `formats/map_graphics.read_screenblock_entries`, `read_terrain_field_*`, `stitch_terrain_field_plane` |
| Tile-entry bits, flip, unswizzle, entry-to-pixels | `formats/bg_tilemap` (bits, entries, render core) and `formats/sprite_graphics` (unswizzle, flip, GBA colour expansion) |
| OAM dimensions | `formats/sprite_graphics.OBJECT_DIMENSIONS`, re-exported by `map_graphics` |
| BG palette requantisation | `formats/map_graphics.decode_bg_palette` |
| Container decode | one format (`formats/webfoot_lz`), two policies injected through `map_graphics.ContainerDecoder` |
| Classified map view (layer render, composition, chunk chooser) | `tools/webfoot/map_view.py` |
| Chunk-replacement policy | `tools/webfoot/map_layout_write.validate_chunk_replacement` |
| Packaged profile resolution | `tools/webfoot/packaged.py` |

Six production consumers were re-pointed:

- `tools/webfoot/map_render.py` - the narrow SDK renderer, now a *presentation
  policy* over shared reads (dominant-layer-only, character-block coverage
  refusal). Its public API, error family and messages are unchanged.
- `tools/webfoot/map_layout_write.py` - the writer. Now imports
  `formats.map_graphics`, `formats.map_entry` and `packaged`; **zero** `tools.export`
  imports.
- `tools/webfoot/map_layout_edit.py` - the edit session and preview. Same.
- `tools/webfoot/map_layout_provenance.py` - derivative verification. Same.
- `tools/webfoot/workbench/map_browser_tab.py` - the shipped Maps editor, now on
  `tools.webfoot.map_view`.
- `tools/export/{canonical,render,map_browser,profile_authority}.py` - now thin
  export-facing spellings over the SDK, keeping their public names and error
  families so no exporter call site or evidence label moved.

`canonical.MapEntry`, `LayerRecord`, `CharBlock`, `AnimatedTileSource` and `Bank`
are **aliases** of the format layer's dataclasses, not second definitions, so a
field cannot exist in one copy only.

## 3. Production import inversion removed

Before: `map_layout_write.py:18-20`, `map_layout_edit.py:32-36` and
`map_layout_provenance.py:41-43` each imported `tools.export.canonical`,
`tools.export.map_browser` and/or `tools.export.profile_authority`; the Workbench
map tab imported `tools.export.map_browser`.

After: **no module under `tools/webfoot` imports `tools.export` at all** (AST
check over every file, including lazy imports). Asserted by
`tests/unit/test_map_decode_authority.py::test_the_sdk_never_imports_the_export_stack`,
with a companion test that the allowed direction actually occurs so the guard is
not vacuous.

## 4. Equivalence evidence

`tests/integration/test_map_decode_equivalence_rom.py` (8 tests, ROM-gated,
run by name only):

1. `test_map_entry_interpretation_matches_a_raw_bytes_oracle` - all 452 rows, the
   shared reader against an **independent raw-bytes oracle** that reads the record
   at the offsets `formats.map_entry` declares. This is what keeps the parity
   assertions from being tautological.
2. `test_layer_interpretation_matches_a_raw_bytes_oracle` - 452 x 4 = 1,808 layer
   records against the same style of oracle.
3. `test_every_commonly_renderable_map_is_byte_identical_across_the_stacks` - every
   map the SDK renderer accepts, rendered by both surfaces; per-layer index bytes,
   composite, palette, width and height must be identical. >300 maps compared.
4. `test_the_two_surfaces_disagree_only_about_deliberately_unrendered_forms` - the
   refused maps: both surfaces name the same handler **from the same reader**.
5. `test_map_19s_terrain_field_is_understood_and_deliberately_not_authored` - below.
6. `test_writer_plans_are_re_derived_from_the_shared_reader` - >100 cells: the
   writer's pointer, field offset and old bytes all equal the shared reader's own
   answer.
7. `test_a_supported_writer_edit_is_byte_for_byte_what_it_planned` - a planned edit
   changes only bytes inside the planned span, holds the planned value, and reverts
   to the canonical image exactly.
8. `test_the_canonical_rom_is_not_modified_by_this_module`.

Result: **8 passed**, 447 s. Canonical ROM hash unchanged.

`tests/unit/test_map_decode_authority.py` (10 tests, portable):

- the import-direction guards;
- every shared concept resolving to the format layer's *objects* (identity, not
  equality-by-luck);
- one container format with two injected policies;
- a **synthetic non-Buu map** (relocated table, non-canonical key bytes, relocated
  palette, synthetic handler record) read by both stacks to identical pixels, and
  its entry flip bits proved directional;
- malformed shared input still failing closed on four distinct record defects;
- the replacement policy having one implementation behind two spellings.

## 5. Map 19 / special-handler classification

The audit's named divergence is **intentional and now explicit**, not parser drift:

- The terrain-field handler `0x080088BD` and the two screen-entry handlers are
  decoded by the shared reader for **both** surfaces: handler, cell grid, container
  run, raster order and the ordinal payload's resolution all come from
  `formats.map_graphics`.
- `tools/webfoot/map_view.py` (the shipped Browse/Layout surface) renders all three
  graphical forms.
- `tools/webfoot/map_render.py` (the Objects/layout renderer) accepts **only** the
  dominant chunk grid `0x08008087` and raises `UnsupportedMapAssemblyVariant` for
  anything else - its accepted contract, unchanged by this ticket, pinned by
  `tests/unit/test_map_render.py::test_unsupported_layer_variant_fails_closed`.
- The layout writer's *one* write operation is a four-byte dominant-layer chunk
  pointer; a terrain field has no such window, so it is refused by name
  (`"layer is not the dominant chunk form"`), which the ROM-gated test asserts.

So "one path displays what the other rejects" is: one **renderer** refuses a record
form the other draws, from the same decoded record. No object-authoring capability
was added, and no rendering capability was added or removed.

## 6. Intentional remaining differences

1. **Renderer component/dimension policy.** `map_render` draws dominant grids only;
   `map_view` classifies and draws three forms. Never a difference in *decoding*.
2. **Container decode strictness.** The export path requires the packed stream's own
   end marker at its declared size (a canonical postcondition measured over 11,712
   containers); the SDK renderer accepts the project decoder's exact-declared-size
   contract. Injected through `map_graphics.ContainerDecoder`; one grammar, one
   format, two outer postconditions.
3. **Bank-container extent check.** `map_render` additionally requires a referenced
   tile bank to decode to exactly `0x4000` bytes, which is the extent its maps were
   verified with. `map_graphics.read_banks` and the exporter read the container's
   declared size instead. This is a renderer-specific acceptance test and is
   documented as such in `map_render._decode_layers`; it is *not* a second reading
   of the bank format.
4. **Character-block coverage refusal.** `map_render` refuses a layer that
   references a tile no selector or animation supplies; the exporter does not.
   Expressed as the shared reader's `require_referenced` parameter, so the
   difference is a caller policy rather than two implementations.
5. **Palette presentation and chrome.** Each surface chooses its own overlays and
   warnings; only the decoded pixels are shared.

## 7. Focused validation

Manual policy: explicitly named files/nodes only. No broad suite, no marker gates,
no `scripts/test.ps1`.

| Command (abridged to the file list) | Result |
|---|---|
| `pytest tests/unit -q` (whole portable unit suite, as the blast-radius gate for a shared-code change) | **2335 passed, 10 skipped** |
| `pytest tests/unit/test_capability.py tests/unit/test_extent_profile_authority.py tests/unit/test_profile_authority_contract.py tests/unit/test_map_decode_authority.py tests/unit/test_map_render.py tests/unit/test_map_browser.py tests/unit/test_map_layout_edit.py tests/unit/test_map_layout_provenance.py tests/unit/test_workbench_map_browser.py tests/unit/test_bg_tilemap.py tests/unit/test_sprite_graphics.py tests/unit/test_asset_export_render.py tests/unit/test_asset_export_map_handlers.py` | **272 passed, 1 skipped** |
| `pytest tests/integration/test_map_render_rom.py tests/integration/test_map_browser_rom.py tests/integration/test_map_layout_write_rom.py tests/integration/test_map_layout_editor_rom.py` | **34 passed, 2 skipped** (two VRAM-oracle dumps absent) |
| `pytest tests/integration/test_map_decode_equivalence_rom.py` | **8 passed** (447 s) |
| `pytest tests/integration/test_asset_export_rom.py` | **81 passed** (530 s) - export behavior unchanged |
| `git diff --check` | clean (exit 0) |

The skips are environment, not coverage: 4 site-build skips, 1 capstone-present
skip, 1 optional VRAM-dump skip, 1 assembled-atlas skip, 1 map40-dump skip. They
are unchanged from the START SHA.

**ROM-gated runs, by explicit file:** 6 files above. `tests/integration` as a
directory was **not** run. The canonical ROM was present for all of them.

## 8. Mutations

Each applied, run against the exact test expected to detect it, then reverted
before freeze. Verified reverted (`git diff` clean of the mutation marker).

| # | Mutation | Expected detector | Observed |
|---|---|---|---|
| M1 | Production import inversion: `from tools.export import canonical as _inverted` added to `tools/webfoot/map_layout_edit.py` | `test_map_decode_authority.py::test_the_sdk_never_imports_the_export_stack` | **FAILED as expected** (also `test_the_writer_and_edit_session_name_the_sdk_reader`); 2 failed, 8 passed |
| M2 | Shared field decode: `read_map_entries` swapped `key_high`/`key_low` | `test_map_entry_interpretation_matches_a_raw_bytes_oracle` + `test_a_synthetic_map_is_interpreted_by_the_shared_reader` | **FAILED as expected**; 2 failed, 9 passed |
| M3 | Writer bypass: `chunk_pointer` returned `chunk_addresses[0]` (the old wrong-cell question) | `test_map_layout_write_rom.py::test_fixed_width_edit_noop_inverse_and_render` | **FAILED as expected**; 1 failed, 1 passed |

M3 note recorded for honesty: the profile-bound test
(`test_the_map_layout_writer_bound_is_the_profiles`) **passed** under M3, because
that mutation changes which cell is read, not the index bound. The cell-value test
is the one that detects it.

## 9. What this ticket did **not** do

- No rendering rewrite: `map_render` still renders dominant grids only, and
  `map_view` still renders three forms. No capability was added or removed.
- No object-authoring expansion for Map 19 or any other handler.
- No capacity work: `ROM-CAPACITY-AND-ALLOCATION-001` stays **BLOCKED**.
- **CQA-15 was not reopened.** The reviewed `RomProfile`/catalog authority, the
  retained-literal classification and the writer's profile-injection proof all
  stand. `tools/webfoot/profile.py` is byte-identical to the START SHA; the one
  new provenance label lives in its own module (`tools/webfoot/packaged.py`)
  precisely because `profile.py` is one of the core modules
  `tests/unit/test_capability.py` holds to "no game name in executable code".
  Every extent, address and hash still comes from the catalog entry the label
  names. The pre-existing CQA-15 synthetic-profile proofs still pass against the
  writer (with its reader attribute renamed `_rom` -> `_reader`, which the tests
  now name).
- No unrelated product capability; `public progress impact: NONE` - the buildout
  stays at 16/24 (67%).
- **No third shared implementation was created.** The export stack has no decode
  logic left; what remains under `tools/export` is a facade over the SDK.

## 10. Remaining related debt

- CQA-05, CQA-06, CQA-07, CQA-08, CQA-09, CQA-10 (PARTIAL/IMPROVED), CQA-12 remain
  open and were not started.
- `tests/unit/test_asset_export_render.py`'s error-message assertion was updated
  for wording that now comes from the shared tile renderer
  (`"expected 0x800"`/`"decoded 0x400"` rather than `"expected 2048"`); the
  refusal itself is unchanged.
- The export stack still keeps its own *strict container postcondition*
  (`webfoot_strict`). That is deliberate and classified above; collapsing the two
  postconditions into one would either weaken the exporter's completeness claim or
  make the renderer refuse canonical containers it currently reads.

## 11. Files changed

Modified: `tools/export/canonical.py`, `tools/export/map_browser.py`,
`tools/export/profile_authority.py`, `tools/export/render.py`,
`tools/webfoot/formats/bg_tilemap.py`, `tools/webfoot/formats/sprite_graphics.py`,
`tools/webfoot/map_layout_edit.py`, `tools/webfoot/map_layout_provenance.py`,
`tools/webfoot/map_layout_write.py`, `tools/webfoot/map_render.py`,
`tools/webfoot/workbench/map_browser_tab.py`,
`tests/integration/test_map_layout_editor_rom.py`,
`tests/integration/test_map_layout_write_rom.py`,
`tests/unit/test_asset_export_map_handlers.py`,
`tests/unit/test_extent_profile_authority.py`,
`tests/unit/test_workbench_map_browser.py`.

Added: `tools/webfoot/formats/map_graphics.py`, `tools/webfoot/map_view.py`,
`tools/webfoot/packaged.py`, `tests/unit/test_map_decode_authority.py`,
`tests/integration/test_map_decode_equivalence_rom.py`.

`tools/webfoot/profile.py` is untouched (restored byte-exactly after an
intermediate edit that had normalized its mixed line endings - a line-ending
change is not a line change and was reverted rather than kept).

No ROM-derived fixture is committed; the ROM is gitignored and was copied into the
worktree only for the gated runs.
