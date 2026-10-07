# Chunk creation and materialization

What one chunk object is, what the chunk-authoring capability builds, what was
measured, what is proven at runtime, and what is deliberately not claimed.

This record states what a chunk is, what was built, what was measured, what was
proven at runtime, and what is deliberately not claimed.

---

## 1. What one chunk object is - measured, not assumed

Every number below was measured over the canonical image's own chunk corpus: every
chunk reference reachable from all 452 MapEntry records.

| Property | Measured value |
|---|---|
| dominant layers | 1,516 |
| chunk cells | 4,274 (156 null pointers) |
| distinct chunk bodies | 3,745 |
| container kind | **kind 1 in 3,745 of 3,745** |
| declared size | **2,048 (0x800) in 3,745 of 3,745** |
| body | 1,024 little-endian 16-bit screen entries = one 32×32 plane |
| visible size | 256×256 pixels |
| tile ordinal | bits 0–9; max observed 895 (mask 0x3FF) |
| H-flip | bit 10; 46,034 entries set it |
| V-flip | bit 11; 15,668 entries set it |
| palette bank | bits 12–15; **zero in all 3,834,880 entries** (unused at 8bpp) |
| metadata outside the plane | none |
| chunk catalog / table | **none** - a chunk is discovered only from a layer window |
| cell reference | four-byte little-endian GBA address at `record + 0x18 + 4*cell` |
| observed address range | `0x08179A50` … `0x082B8BAC`, all top byte `0x08` |
| alignment | addresses are multiples of 4; residues mod 16 spread evenly, so 4 is the requirement and 16 is not |
| sharing | 165 bodies are used by more than one cell; **160 of those across different maps** |

**Screen-entry ordinals are map-scoped.** Assembled character blocks are per map:
a 42-map sample produced 42 distinct blocks. A chunk plane holds ordinals, and an
ordinal only means anything through the assembling map's character block, so an
authored chunk is composed against one map and placed only in that map's layers.

Measured by `build/research/chunk_model_measure.py`.

## 2. What was built

**`tools/webfoot/map_chunk.py`** - the authority for the capability. `ChunkAuthor`
is the public facade a surface drives; `resolve_authored_chunk`,
`compose_body` and `materialize_authored_chunks` are the build path;
`set_authored_chunk`, `remove_authored_chunk` and `set_layout_authored_cells` are
the persistence path. One public failure family, `ChunkAuthoringError`.

**Container encoding.** `webfoot_lz.pack` gained an explicit `kind`; the two packed
kinds share one decoder and differ only in initial literal width, and the opener
sets that width to 8 explicitly, so the token stream is identical for either. A
canonical kind-1 chunk was measured to begin with that same escape sequence, so an
authored body is emitted as **kind 1** - the kind the engine demonstrably renders
3,745 times - rather than in the encoder's own kind 2. `map_graphics` gained
`CHUNK_CONTAINER_KIND`, `CHUNK_POINTER_BYTES`, `chunk_body_bytes` and
`pack_dominant_chunk`.

**Project state is semantic and address-free.** `maps/chunks.toml` holds each
authored chunk as an identity (`chunk:name`) plus a sparse delta over the canonical
chunk it was cloned from - `[prior, entry]` per changed cell, so the document
proves its own body was authored against the template it names. A
`maps/layout.toml` cell may now hold either the layer's 1-based chunk ordinal (the
shipped form) or a `chunk:name` identity; `read_project` refuses a cell naming a
chunk the project does not declare. The template is named by the layer's own
1-based vocabulary ordinal and resolved against the **canonical** image only, so
painting a cell can never re-point a template.

**Build.** A fourth allocating domain. `AllocationKind.CHUNK_BODY` is the first
whose pointer is a full 32-bit address rather than a selector or an array index.
Only chunks a cell references are materialized. The generated-image policy is now
derived from the union of every allocating domain's spans, because `plan_changes`
requires the image's allocated spans to equal the allocation provenance exactly
and two expanding domains could not otherwise both be described.

**Workbench.** A chunk editor inside the existing map surface - template chooser,
Create Chunk, the 32×32 plane with the layer's own screen-entry palette, single
cell and drag paint, eyedropper, undo/redo on that surface's one `QUndoStack`,
Apply/Revert, dirty state, and the authored chunk as a map paint brush. The
surface's `_EDIT_ERRORS` family gained `ChunkAuthoringError`; `on_session_changed`
clears the new state and `on_project_mutated` preserves it (CQA-05).

## 3. The addressability answer

**Encoding-capable: YES. Runtime-proven: YES.**

The map cell's reference is a full four-byte GBA address. The canonical image
declares a single 256-byte `VERIFIED_FREE` region and a chunk container is larger
in every case measured, so a canonical placement does not exist and **expansion is
required rather than optional** - this capability could not have been satisfied in
place, which is why it owns the proof.

| Item | Value |
|---|---|
| chunk reference encoding | four-byte little-endian GBA address, unmasked |
| selected allocation file offset | `0x00800000` (= the canonical image's own length) |
| selected GBA runtime address | `0x08800000` |
| alignment | 4 |
| above canonical EOF (8 MiB) | **YES** |
| container size | 408 bytes |
| derivative | 16,777,216 bytes, sha256 `5c51ece754fbe7b3d54b872a94fbe4404dfa4b7e350d3c11f26c5a6c6f0675a0` |
| bytes changed in the canonical region | exactly 3, at `0x00292CA0..0x00292CA2` |

## 4. Runtime proof

Method: MAP-TILE-PAINT-001's corrected methodology. A savestate restores the
already-assembled background, so a capture taken under a state load is decided by
the state and not by the ROM; **the rebuild is per run**. Each run loads the ROM,
loads the same saved state, leaves map 40 and re-enters it, waits for the rebuild
to settle, and is captured only if the observer's own map-index transitions show
the leave-and-return and the engine is still in the target map.

Inputs: canonical ROM `940ad5f0…f059e`; saved state
`2d5740a8c54180d153024a11b0e4d1143306957af55a3ad0664c71cf7d9a1aab`; derivative as
above. Route map 40 → 39 → 40 in both runs.

**Engine-side liveness evidence.** The successor observer records the address the
engine's own live layer record holds for the watched chunk cell, read through the
engine's live MapEntry pointer:

| | retail control | authored derivative |
|---|---|---|
| ROM the engine is running | 8,388,608 bytes | **16,777,216 bytes** |
| address the engine's BG1 cell 0 holds | `0x082928DC` (the canonical chunk) | **`0x08800000` (the new body, above EOF)** |

**The engine's own uploaded tilemap.** Comparing the live VRAM screenblocks
captured after each run's rebuild:

| layer | result |
|---|---|
| BG0 | byte-identical |
| **BG1** | **593 of 1,024 screen entries differ**, rows 1–31, columns 0–30 |
| BG2 | byte-identical |
| BG3 | byte-identical |

The differing BG1 entries carry the authored arrangement: retail
`0x0020, 0x00D8, 0x00DC, 0x0019, 0x001A, 0x001B` against authored
`0x0021, 0x0020, 0x001F, 0x001E, 0x001D, 0x001C` - the mirror ordering the author
imposed. Only the layer the chunk was placed in changed.

**RETAIL APPEARANCE:** Grand Kai's grass field, trees and dirt path render as one
continuous texture; the tree clusters sit left of centre.
**AUTHORED APPEARANCE:** the same view and camera, but vertical mirror seams run
through the grass and the tree clusters have moved to the opposite side.
**MATCHED DIFFERENCE:** 11,429 of 35,264 counted pixels (32.4 %) differ, over the
whole visible area - which is the expected shape here, because the authored
arrangement rewrites the chunk's entire plane and one chunk cell covers more than
the visible screen. BG0/BG2/BG3 being byte-identical is what rules out a camera
shift.

Captures and the run indexes are local runtime artefacts under
`build/chunkauth001/matched/{retail,authored}/` and are not committed.

## 5. Focused validation

| Command (explicit files only) | Result |
|---|---|
| `pytest tests/unit/test_map_chunk_authoring.py tests/unit/test_map_chunk_project.py tests/unit/test_workbench_chunk_authoring.py -q` | **131 passed** |
| `pytest tests/integration/test_map_chunk_authoring_rom.py -q` | **37 passed** |
| `pytest tests/unit/test_map_chunk_authoring.py tests/unit/test_map_chunk_project.py tests/unit/test_workbench_chunk_authoring.py tests/unit/test_workbench_map_browser.py tests/unit/test_workbench_state_and_errors.py tests/unit/test_workbench_palette_cost.py tests/unit/test_map_layout_project.py tests/unit/test_map_layout_edit.py tests/unit/test_map_layout_provenance.py tests/unit/test_mgba_capture.py -q` | **371 passed** |
| `pytest tests/integration/test_map_tile_paint_rom.py tests/integration/test_map_layout_write_rom.py tests/integration/test_rom_expand_001.py -q` | **39 passed, 4 skipped** (the skips need a ROM path this run did not set) |
| `pytest tests/unit/test_mgba_capture.py -q` | **74 passed** - the read-only guard accepts the successor observer |

Broad suites were **not** run manually; CI owns them.

## 6. Mutations M1–M8

Each is a minimal literal edit to the shipped code that restores a specific wrong
behaviour; each was applied, the one named node run, and the file reverted.

| | Mutation | Node that failed | Result |
|---|---|---|---|
| M1 | drop the authored body from the build output | `test_a_built_project_carries_the_authored_body_and_only_it` | PASS |
| M2 | resolve the identity to the wrong address | `test_the_map_cell_resolves_to_the_allocated_address` | PASS |
| M3 | write the body over its own template's container | `test_every_unchanged_canonical_chunk_body_is_still_byte_identical_in_the_build` | PASS |
| M4 | swap the row and column of an authored cell | `test_an_authored_chunk_differs_from_its_template` | PASS |
| M5 | stop reserving a placed body | `test_allocation_is_deterministic_and_reservations_do_not_overlap` | PASS |
| M6 | drop the chunk document on project read | `test_the_project_reopens_with_the_identity_body_and_reference_intact` | PASS |
| M7 | truncate the encoded address to 24 bits | `test_the_encoded_cell_reference_is_the_full_gba_address` | PASS |
| M8 | leave the cell on its canonical chunk | `test_the_built_map_cell_names_the_authored_chunk_not_the_canonical_one` | PASS |

Runner: `build/research/mutations.py`. All eight caught.

## 7. Reopen, determinism and resource safety

- **Reopen**: a saved project reopens with the chunk's identity, its body and its
  map reference intact; the body resolves byte-identically and the reference is
  still semantic. No part of the project depends on a previous process's runtime
  allocation.
- **Determinism**: building the same saved project twice produced byte-identical
  images and byte-identical manifests; allocations and the resolved address are
  identical across runs.
- **Unchanged resource safety**: in the canonical region exactly three bytes differ
  (the cell's pointer field). Every canonical chunk container in the derivative was
  compared against the canonical image and is byte-identical. The canonical ROM is
  unchanged. Sharing is respected: creating a chunk never mutates the template, and
  the corpus's cross-map shared chunks are intact.
- **Allocator safety**: the body is reserved before the next request is placed;
  two chunks in one build cannot overlap; a second chunk in the same build lands
  after the first.

## 9. Scope boundaries and what is NOT claimed

Not claimed, and not implemented: graphics import, new tiles, new palettes, new
sprite graphics, map resizing, layer creation, warp or connection editing, new
maps. An authored chunk is a new **arrangement** of screen entries the layer
already draws; the permitted vocabulary is exactly the entries the template's own
layer displays, and an entry outside it is refused.

Two limits are recorded rather than hidden:

1. **An authored chunk is map-scoped.** Cross-map reuse needs character-block
  equality proved first; the placement is refused today.
2. **A 16 MiB derivative cannot be reopened through `verify_authored_image`.**
  That shared verifier reconstructs the canonical image from the whole input
  buffer and hashes it, so any derivative larger than the canonical image is
  refused. This is **pre-existing**: the compressed-dialogue domain has expanded
  above EOF since ROM-EXPAND-001 and is refused the same way. This record's
  reopen acceptance is the **project** reopen, which passes. Widening the shared
  verifier is a separate change with its own blast radius and is not attempted
  here.

> **SUPERSEDED (2026-10-07) by `DERIVATIVE-16M-REOPEN-001`.** The shared verifier
> no longer reconstructs and hashes the whole file: the caller states the
> canonical span and only that span is verified, so a valid expanded derivative
> now reopens. See the `chunks` record in `src/data/capabilities.json` and
> `docs/research/PROJECT_STATE_AUDIT_RECONCILIATION.md` finding 70. The paragraph
> above is the state when this record was written and is not restated.

Also noted for the record: `tools/runtime/inject_mgba_lua.ps1` keeps its own
CRLF line endings, so `git diff --check` reports the documented CRLF artifact on
added lines. Measured separately: that file is 481 CRLF and 0 LF-only lines, with
**zero** lines carrying actual trailing whitespace. No bytes were rewritten to
make the artifact disappear.
