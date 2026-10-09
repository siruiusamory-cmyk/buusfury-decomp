# DragonByte Z implementation roadmap

The ordered path from the current master to a ship-able V1.0, derived from
[`DRAGONBYTE_Z_PRODUCT_SPEC.md`](DRAGONBYTE_Z_PRODUCT_SPEC.md).

**Status: design only.** No step below is implemented. Each step is one ticket.
The order is a dependency order, not a priority order.

## The V1.0 essential set, evaluated

The coverage census recommends seven essentials
(`../research/ROM_EDITOR_COVERAGE_LEDGER.md`, the V1.0 triage table) on top of
the owner's standing requirement. Each is evaluated here rather than adopted.

| Census recommendation | Decision | Reason |
| --- | --- | --- |
| Integrated hex editor | **Required.** Owner decision already records it as a 1.0 requirement. | It is the only surface that can show bytes the SDK has no name for, and the range index has no client without it. |
| Arbitrary byte authority | **Required, and narrower than the census wording.** | Measured: the write stack refuses only an empty owner (`tools/webfoot/write.py:324-325`), while the in-image, old-matches-base and no-overlap guards live in the plan (`:1203-1235`) and a second write to one field is a contradiction (`tools/webfoot/authored_image.py:195-200`). So a raw edit is already a legal change. What is missing is an entry point, a typed raw owner, a claimed-bytes check and undo, not a class. |
| Range-to-owner index | **Required.** | Without it the hex editor is an anonymous viewer and the fail-closed rule has nothing to say. It is derived, small and headless. |
| Raw byte search | **Required.** | It is the only way to reach the bytes the product has no map for; semantic search cannot. |
| Growth-capable container encoder | **Required, scoped to the two container paths it gates,** and scheduled late because it is the riskiest step. | Without it a container edit is shrink-only. The mechanism already exists for one domain (compressed dialogue relayout plus allocation plus relocation) and the step generalises it. A size-changing import is refused with this reason until it ships. |
| Stat-table surfaces | **Required.** | `stats.py` is a complete semantic layer that already produces owner-bearing changes; it is the cheapest real editing surface in the product. |
| Map-header surfaces | **Required.** | The map-entry codec is profile-declared and verified (`config/roms.yaml:45-48`); it is the second cheapest. |
| The three unmodelled per-area object arrays, the save serializer, audio, the 266 handler meanings | **Not V1.0. Research first.** | Each is a modelling question with no verified codec. A surface over an unmodelled structure would be the same class of error as the five excluded relations in the product specification. |

## Steps

### S1 - DRAGONBYTE-Z-FOUNDATION-001: the application exists

- **Goal.** A new package `tools/dragonbyte/` with a session, a destination
  registry, a thin window and one destination rendering.
- **User can now.** Open a project and a verified ROM and see one destination.
- **SDK work.** None.
- **Acceptance proof.** `tools/quality/architecture.py` gains the new root in
  `ALLOWED_ROOTS`, with a test that the new package imports no Qt at module
  level and that nothing under `tools/webfoot/` imports the new package. A
  headless test drives the session with no `QApplication`; the window opens with
  exactly one destination and the strip shows six entries.
- **Depends on.** Nothing.

### S2 - DRAGONBYTE-Z-STATE-001: one journal, one stack, one history

- **Goal.** The edit journal, the single application undo stack, the navigation
  history and the derived dirty state.
- **User can now.** Navigate between resources, come back, and undo across
  destination boundaries.
- **SDK work.** None. `write.ByteChange` is the change type and the journal
  projects into it.
- **Acceptance proof.** With no window: a mixed semantic and raw sequence asserts
  stack count and index through undo and redo, `id()` and `mergeWith()` collapse
  a continuous interaction into one entry, undoing back to the saved point
  restores `saved`, and the history restores destination, mode, identity and
  sub-selection. A grep-level test asserts no per-surface undo stack exists.
- **Depends on.** S1.

### S3 - DRAGONBYTE-Z-RAW-BYTE-AUTHORITY-001: the honest free write

- **Goal.** The raw owner namespace, the claimed-bytes refusal, the write
  confirmation and the journal entry.
- **User can now.** Change a byte the SDK cannot name, undo it, and save a new
  image.
- **SDK work.** None required for admission (see the evaluation above). The claim
  query it depends on arrives in S4; until then claimed bytes are refused
  conservatively from the atlas objects, the declared table extents and the
  journal's own pending entries, and the plan-level overlap guard remains the last
  gate rather than the first.
- **Acceptance proof.** A raw write into bytes a declared structure owns is
  refused, names the owner once, and creates no change. A raw write into a byte a
  pending semantic edit has changed is also refused at commit, naming that
  semantic owner. A write into an unowned range creates exactly one entry owned by
  `raw:<image address>`, the plan accepts it, and `verify_emitted_image` returns
  exactly that offset. Saving over the canonical digest is refused. The canonical
  digest is unchanged before and after.
- **Depends on.** S1, S2.

### S4 - DRAGONBYTE-Z-OWNER-RANGE-INDEX-001: what owns these bytes

- **Goal.** The range index: range to owners, owner to ranges, declared table
  extents, references, and `UNKNOWN` as a first-class answer with a count.
- **User can now.** Tell a coded region from an unowned one before typing.
- **SDK work.** A byte-scanning twin of `atlas.search_text`
  (`tools/webfoot/atlas.py:626`) that returns, per hit, the offset, the coverage
  classification and the owners and references intersecting it.
- **Acceptance proof.** For sampled offsets the index equals direct `atlas.*`
  answers for classification, confidence, owners and references; the unknown
  total equals the atlas's own unknown byte sum; there is no second
  classification vocabulary and no second coverage partition.
- **Depends on.** S3.

### S5 - DRAGONBYTE-Z-ROM-SURFACE-001: the ROM destination

- **Goal.** The Ranges and Bytes views, `Go to address`, the ownership strip,
  the changed-bytes overlay, canonical-versus-current columns, raw search, and
  `Open bytes` from any selection with a proven extent.
- **User can now.** Explore and edit the whole image from anywhere.
- **SDK work.** None beyond S4.
- **Acceptance proof.** `Go to address` accepts an image address and a file
  offset and converts between them; a byte edit is one undo entry; the overlay
  shows exactly the manifest's change set after a build; `Open bytes` is
  disabled with a stated reason when no extent is proven.
- **Depends on.** S3, S4.

### S6 - DRAGONBYTE-Z-DATA-SURFACES-001: the tables that already work

- **Goal.** Data surfaces over the verified tables: enemy stat records
  (`0x08711274`, 141 records of 28 bytes), character base stats
  (`0x086FDA4C`, 9 records of 18 bytes), map-entry header records
  (`0x0808E2E0`, 452 records of 56 bytes), plus the `Coverage` view that reports
  what is modelled, unsupported and unmapped.
- **User can now.** Edit a statistic and a map header through names and see the
  same bytes move under the ROM surface.
- **SDK work.** Map-entry field authoring if any field is read-only today; enemy
  and character stats already have owner-bearing changes.
- **Acceptance proof.** One stat edit produces one change owned by the record
  identity; the same offset is visible in the ROM surface; one `Ctrl+Z` reverts
  both views; the coverage view's counts equal the census totals recomputed from
  the census data file.
- **Depends on.** S5.

### S7 - DRAGONBYTE-Z-SEMANTIC-DESTINATIONS-001: the four editing worlds

- **Goal.** Maps (layout, chunks, warps), Entities (placements and their proven
  relationships), Scripts & Text (text and dialogue replacement), and Graphics
  (sprite, appearance, palette) as editing surfaces over the approved relation
  chains.
- **User can now.** Edit a placement, a string, a map layout and a sprite
  through the destination that owns them.
- **SDK work.** None beyond S6.
- **Acceptance proof.** Per destination: one round-trip build asserting the
  owner identity, the change count and the manifest content; the change is
  visible in the ROM surface; the write goes through the one stack; each
  destination's unsupported rows offer no edit affordance and state their
  reason. No unproven relation appears anywhere.
- **Depends on.** S6.

### S8 - DRAGONBYTE-Z-CONTAINER-GROWTH-001: size-changing payloads

- **Goal.** One reusable growth-capable container operation: allocate,
  re-encode, rewrite references, and emit relocation provenance. Generalised
  from the compressed dialogue relayout path, which already does allocation and
  relocation for one domain.
- **User can now.** Import a payload larger than the one it replaces, instead of
  being limited to same-size replacement.
- **SDK work.** The growth operation itself. The stored-rewrite path is not
  enough: it exceeds the original allocation in every measured sprite container,
  so growth has to move bytes rather than rewrite in place.
- **Acceptance proof.** A grown container decodes to a byte-identical payload;
  every dislodged reference is rewritten and named in the relocation provenance;
  the plan is still one plan for the build; a second build with identical inputs
  is byte-identical; the importer now accepts a size-changing payload, and before
  this step it refused it with this reason.
- **Depends on.** S3, S4, S5.

### S9 - DRAGONBYTE-Z-SHIP-V1-001: the release surface

- **Goal.** Patch export, packaging, visible version identity, and the
  documentation owed by the sequence.
- **User can now.** Hand someone a patch and install the application.
- **SDK work.** None; export and verify already exist and are verified.
- **Acceptance proof.** The exported patch applies to the canonical image and
  reproduces the built image byte for byte; a packaged build opens a project;
  the visible version matches the build identity; the owed documentation changes
  are in.
- **Depends on.** All previous steps.

## What is not on this roadmap

**Research first, and never promoted silently into a step.** The three
unmodelled per-area object families; the save format and whether the expansion
path preserves it; audio; the 266 script handler meanings. Each is a research
ticket. None is a V1.0 dependency and none blocks a step above.

**Deliberately post-1.0.** Map graphics below the chunk level and tileset
authoring; portraits, UI, HUD and fonts; item and shop surfaces; the LOGII and
LOG1 domains as their research lands; save-domain support; side-by-side
comparison of two resources; any docking or layout-profile system.

**Not product-worthy.** A dedicated editor for the compiler-embedded assertion
strings, the colour lookup block or debug debris. The census records the
recommendation; this roadmap agrees.

**Not a ticket queue.** The 40 census systems are not a backlog. The V1.0 surface
set above is seven capabilities over the domains the evidence already supports,
and the rest of the census is evidence for honesty rather than work to schedule.

## Documentation owed by the sequence

1. `../desktop-ui.md` gains the ROM surface's address-first exception, so the
   single deliberate inversion of "addresses are diagnostics" is written where
   the rule lives. S5 owns this.
2. `../workbench-architecture.md:3` currently states that DragonByte Z is the
   desktop editor shipped from `tools/webfoot/workbench/`. That sentence is true
   of the beta and false of this product, so it is amended when the new
   application ships, naming the beta as the engineering surface the release
   review already records it to be. S9 owns this.
3. The existing journeys under `../journeys/` describe the beta's surfaces.
   Each is mapped to its home among the five destinations and the action bar, or
   recorded as having no home yet, in the same change. S7 owns this. Users of the
   beta are not migrated by this sequence: the beta keeps working unchanged.
4. `docs/README.md` indexes this directory (done with this specification).
5. `src/data/capabilities.json` changes only when a capability actually ships.
   It reads 24 of 24 today and this roadmap does not change it. S9 owns any
   entry it needs.

## Next ticket

`DRAGONBYTE-Z-FOUNDATION-001` (S1 above): the new package, the session, the
destination registry, the architecture gate change, and the import-direction
test.
