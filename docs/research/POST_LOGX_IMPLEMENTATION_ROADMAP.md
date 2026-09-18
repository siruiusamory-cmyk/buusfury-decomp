# Post-LOGX implementation roadmap

**Owner of this document:** the LOGX research freeze closeout
(LOGX-SYNTHESIS-001). **This is an implementation queue, not a research
provenance record.** The evidence behind every statement here is in
[`LOGX_SYNTHESIS.md`](LOGX_SYNTHESIS.md) (canonical synthesis) and the ten
tickets' own provenance documents; this file does not repeat it.

**Read first:** [`LOGX_SYNTHESIS.md`](LOGX_SYNTHESIS.md) §11 (production
defects), §14 (read support), §15 (authoring readiness), §16 (portrait decision),
§17 (recommended follow-up research) and §18 (`AUTHOR_NEW` gap analysis).

> **This roadmap creates no work by itself.** Every ticket below is a proposal
> for a human to authorize. Tickets are sized to be independent; the dependency
> column, not the ordering, is what must be honoured.

---

## How to read a ticket

| Field | Meaning |
| --- | --- |
| **Goal** | the single thing that is true when the ticket is done |
| **Dependencies** | tickets or facts that must exist first |
| **Subsystem** | the code or document that changes |
| **Kind** | `engineering`, `research`, or `engineering + research` |
| **Acceptance** | the observable condition that proves the goal |
| **Risk** | what can go wrong, and what the blast radius is |
| **`AUTHOR_NEW`** | whether this materially advances the acceptance frontier |
| **Public** | whether it changes a user-visible product capability |

**Standing prerequisites that apply to every writing ticket** (not repeated per
ticket, because they come from the project's own rules rather than from LOGX):

* the original ROM is read-only; every write goes
  `verified base -> working copy -> generated output`;
* any ROM access re-verifies the exact configured profile and fails closed;
* round-trip formats losslessly **before** editing them;
* no proprietary artifact is committed, and no ROM-derived fixture enters a
  portable test;
* every write path needs bounds, and every count/pointer it changes needs the
  invariant that couples them re-checked.

---

## Phase 1 - Correctness and parser repair

**Theme:** stop relying on tooling that is known wrong. Nothing downstream should
be built on a parser whose offsets are refuted, or on a decoder that can report a
truncated payload as success. Every ticket here is `engineering`; none needs
research.

---

### FIX-1 - Strict decoded-size enforcement in `webfoot_lz`

| | |
| --- | --- |
| **Goal** | the packed decoder refuses a stream that does not produce **exactly** its declared decoded size, instead of silently clipping an over-long final match and reporting success |
| **Dependencies** | none. `LOGX-CODEC-001` established the required behaviour and pinned the failing case |
| **Subsystem** | `tools/webfoot/formats/webfoot_lz.py` (`_unpack_stream`, `unpack`), its unit tests, and every caller that relies on the current "always succeeds" behaviour |
| **Kind** | `engineering` |
| **Acceptance** | `01000000040000000558d020000000c0` (form 1, declared 4) is **rejected**, not accepted with a 4-byte result; all **4,322** reachable canonical packed containers still decode to exactly their declared sizes; declared-size mismatch and missing-end-marker truncation both surface as errors; the existing clipping regression test is replaced by a refusal test rather than deleted |
| **Risk** | **medium.** The decoder is shared by map chunks, selector streams, banks, sprite graphics and the atlas path. A stricter failure policy can turn previously "successful" decodes into errors. Blast radius is the whole graphics/tile pipeline, which is why this is first: everything later trusts it |
| **`AUTHOR_NEW`** | no - but it is a hard prerequisite for every insertion capability |
| **Public** | no direct capability change; it can only make an existing path fail loudly instead of silently |

---

### FIX-2 - `sprite_graphics` 8+12 frame and piece layout

| | |
| --- | --- |
| **Goal** | the sprite codec models the accepted frame record: an **8-byte header**, `piece_count` **12-byte** pieces at `+0x08 + 12*i`, the packed OBJ attribute pair at piece **`+0x04`** and the graphics-container word at piece **`+0x08`** |
| **Dependencies** | none for the codec itself. FIX-3 (the walker) should land in the same window so the reader and the codec agree |
| **Subsystem** | `tools/webfoot/formats/sprite_graphics.py` (`PIECE_SIZE`, `decode_piece`, `encode_piece`, `decode_frame`, `Piece`'s fields and docstrings), `tools/webfoot/graphics.py` (the `+0x0C` reference it composes), `tests/unit/test_sprite_graphics.py`, `tests/integration/test_graphics_rom.py`, `tests/unit/test_logx_sprite_reference.py` |
| **Kind** | `engineering` |
| **Acceptance** | `decode_frame` decodes the 2- and 4-piece canonical frames; all **11,005** pieces across **10,980** frames resolve to a container whose declared decoded length equals `dim_0 * dim_1`; `Piece.shape` / `size` / `colour_256` / `horizontal_flip` / `vertical_flip` / `dimensions` are **kept** and derived from `+0x04`; the piece's `+0x02`/`+0x03` extents are stored fields rather than part of an "unknown" span; `encode_piece` round-trips a 12-byte piece exactly; the **7,390** distinct container offsets are reachable rather than 7,355; the module's stale text goes with the code (its chain diagram, its "One piece per frame, measured - not assumed" claim, its `+0x50` header offset, its `4,014 of 7,354` pair figure and its "13,588 reachable pieces" stride comment all describe the refuted layout); the unit tests' 4-byte-header and 16-byte-piece fixtures are replaced, not deleted, so the correction is pinned |
| **Risk** | **high, but well-bounded.** This is the single most load-bearing parser defect in the queue. The blast radius is the sprite-graphics reader, the atlas producer, the build's PNG extraction and the Workbench graphics surface - all of which currently depend on `decode_frame` rejecting multipart frames. The mitigation is that the corrected layout is already proved by an independent test (declared size equals `dim_0 * dim_1` on 11,005 of 11,005) |
| **`AUTHOR_NEW`** | partial - it is the prerequisite for multipart sprite rendering, replacement and authoring |
| **Public** | yes, eventually: it makes 21 multipart frames and 35 graphics containers visible, so a user-visible asset inventory grows |

---

### FIX-3 - Count-bounded animation-array traversal

| | |
| --- | --- |
| **Goal** | `graphics.py::_animations_in` honours `definition + 0x00`: it reads the element count and walks `[+0x54, +0x54 + 4*count)` instead of walking to the next structure |
| **Dependencies** | FIX-2 in the same window (the reader and the codec must agree on the piece layout) |
| **Subsystem** | `tools/webfoot/graphics.py` (`_animations_in`, its docstring, the caller at `ActorSprites.__init__`), the profile contract if the count offset must be declared (`tools/webfoot/profile.py`), `config/roms.yaml` + `tools/webfoot/data/roms.yaml` evidence text |
| **Kind** | `engineering` |
| **Acceptance** | the walk reads the count and never scans past it; **4,070** slots are considered over the 297 definitions rather than **8,230**; the accepted graphics totals are **unchanged** (`1017 - 4 = 1013` admitted animations, `13660 - 64 = 13596` direction slots, `10964 - 5 = 10959` frames), proving the recorded no-op; a profile can declare the count offset, or the code documents why it cannot |
| **Risk** | **low.** `LOGX-SPRITE-001` measured the correction to be a numerical no-op for the accepted corpus: the 4,160 extra slots are all nonzero non-ROM-pointer words discarded by the existing filter. The risk is a profile-contract change, whose blast radius is the profile loader and its tests |
| **`AUTHOR_NEW`** | no |
| **Public** | no |

---

### FIX-4 - Multipart-aware OAM asset path in `graphics.py`

| | |
| --- | --- |
| **Goal** | the graphics reader's document/reference graph addresses the graphics word by field, not by a hard-coded `frame + 4 + 0x0C`, so it stays correct once FIX-2 lands |
| **Dependencies** | FIX-2 (its offset becomes wrong the moment the codec is corrected) |
| **Subsystem** | `tools/webfoot/graphics.py` (`ActorSprites.plan`/`_piece_for` reference construction) |
| **Kind** | `engineering` |
| **Acceptance** | the reference offset is derived from the piece record the reader actually decoded; no reader site composes a piece field by literal arithmetic; the ROM-gated graphics suite passes with the corrected codec |
| **Risk** | **low** today and **high** if skipped: `4 + 0x0C` happens to equal `8 + 0x08`, so it emits the right address only for piece 0 of single-piece frames. After FIX-2 the reader can return a non-first piece, and a stale literal would then emit a wrong ROM reference into a relocation/edit graph |
| **`AUTHOR_NEW`** | no |
| **Public** | no |

---

### FIX-5 - Stale-figure sweep: `7,355` and single-piece framing

| | |
| --- | --- |
| **Goal** | no shipped text, profile evidence string or docstring presents the single-piece subset as the corpus total |
| **Dependencies** | FIX-2 (the figure only becomes "reachable" once the codec can see the 21 multipart frames) |
| **Subsystem** | `tools/webfoot/graphics.py`, `build.py`, `cli.py` (user-visible help text), `atlas_producers/seed.py` (including its refuted "structures tile one contiguous region" claim), `formats/sprite_graphics.py`, `formats/webfoot_lz.py`, `data/roms.yaml` + `config/roms.yaml` (profile evidence strings), `docs/architecture.md`, `docs/project-format.md`, `docs/research/SUBSYSTEM_MAP.md`, `docs/research/GRAPHICS_FORMAT.md` |
| **Kind** | `engineering` (documentation and strings) |
| **Acceptance** | every figure states its population: "7,390 distinct container offsets reachable by a piece; 7,355 of them by single-piece frames". **A blanket replacement of 7,355 with 7,390 is not acceptable** while any reader still cannot see the multipart frames. `docs/research/GRAPHICS_FORMAT.md` is **exempt** from this sweep while its `SUPERSEDED STATEMENTS` banner stands, because that banner is what makes its figures unambiguous; the audit enforces the banner's presence. The ROM-gated tests that pin the stale constants (`UNIQUE_GRAPHICS = 7355` in `tests/integration/test_graphics_rom.py`, and the 16-byte/4-byte-header fixtures named under FIX-2) belong to FIX-2, which must move them so they pin the **corrected** layout rather than delete them |
| **Risk** | **low.** Text and profile evidence only; `tools/research/logx_synthesis_audit.py` now detects a regression of the headline form |
| **`AUTHOR_NEW`** | no |
| **Public** | marginal - corrected CLI help and documentation |

---

### FIX-6 - MapEntry metadata round-trip writer

| | |
| --- | --- |
| **Goal** | an in-place, byte-preserving writer for the confirmed MapEntry fields (`+0x00`/`+0x01` key bytes, `+0x0C` text index, `+0x2C` source word) that changes nothing else in the 56-byte record |
| **Dependencies** | none |
| **Subsystem** | the map-entry reader/writer under `tools/webfoot/formats/` (`map_entry.py`) |
| **Kind** | `engineering` |
| **Acceptance** | read-modify-write of a single field leaves the other 55 bytes byte-identical; a round-trip of all 452 records reproduces the source region exactly; a write that would produce an out-of-range text index, a duplicate key or a non-in-ROM source word is refused |
| **Risk** | **low.** Fixed-size record, no allocation, no relocation, no count update |
| **`AUTHOR_NEW`** | no |
| **Public** | enables "edit existing map metadata", the first user-visible editing capability |

---

## Phase 2 - Verified existing-content tools

**Theme:** capabilities that need **no new bytes** - inspection and safe in-place
editing of content the engine already has. All are `engineering`.

---

### TOOLS-1 - Canonical character/appearance inspector

| | |
| --- | --- |
| **Goal** | the SDK exposes the accepted appearance-definition table: 232 records, the five physical fields, resolved text for `+0x00`/`+0x02`, resolved sprite-definition target for `+0x04`, resolved portrait pointer for `+0x08`, and the signed `+0x0C` stat index |
| **Dependencies** | FIX-6 (the shared metadata writer, if the ticket is extended to edit); otherwise independent |
| **Subsystem** | a new reader over `0x0874D380` in `tools/webfoot/formats/`, plus the atlas/project path and CLI surface |
| **Kind** | `engineering` |
| **Acceptance** | all 232 records read with the accepted population figures (154 distinct `+0x00` indices -> 152 strings, 154 `+0x02` -> 104 strings, 198 distinct `+0x04` ids -> 198 targets, 110 distinct non-zero `+0x08` slots, 144 non-negative `+0x0C`); the three anomaly sets are surfaced rather than hidden; the neutral vocabulary ("named appearance definitions with optional slot and stat indices") is used, **not** "character table" |
| **Risk** | **low.** Read-only over a fixed table whose layout is `CONFIRMED`. The naming risk is the real one: a UI that says "character name" would promote a `PARTIALLY CONFIRMED` semantic |
| **`AUTHOR_NEW`** | no |
| **Public** | yes - the first canonical character/appearance view |

---

### TOOLS-2 - Correct multipart sprite and animation preview

| | |
| --- | --- |
| **Goal** | a preview that renders a sprite definition's animation correctly, including the **21 multipart frames**, and can step frames and direction cells |
| **Dependencies** | FIX-2, FIX-3, FIX-4 |
| **Subsystem** | the Workbench graphics surface and the graphics reader |
| **Kind** | `engineering` |
| **Acceptance** | frames `0x08423128` (2 pieces) and `0x08579890` (4 pieces) composite correctly and their bounds match the frame header's bounding box; all 13,660 direction cells resolve; the UI presents direction slots as **numbered**, never named |
| **Risk** | **medium.** The composite path is engine-derived (the bounding box, the extents and the OAM attribute merge are all `CONFIRMED`), but piece **origin** is `UNRESOLVED`. The preview must state that offsets are relative to the entity's own coordinates and must not imply a hitbox or anchor |
| **`AUTHOR_NEW`** | no |
| **Public** | yes - correct multipart rendering is a visible correctness fix |

---

### TOOLS-3 - Warp destination inspector and editor

| | |
| --- | --- |
| **Goal** | read every transition record, resolve its destination, show the link graph, and rewrite a single destination pair in place |
| **Dependencies** | none (the whole record layout is `CONFIRMED`) |
| **Subsystem** | a new `tools/webfoot/formats/` connection reader/writer over `root +0x40`/`+0x44` |
| **Kind** | `engineering` |
| **Acceptance** | all 735 records read with 0 anomalies; 694 directed / 674 reciprocal / 20 one-way / 3 self links reproduce; a destination rewrite changes exactly `+0x11`/`+0x12` and leaves the other 22 bytes byte-identical; **a proposed destination that does not resolve through `0x080089FC` is refused** |
| **Risk** | **low.** Fixed-size record, in-place, no count or pointer changes. The one real risk is a UI that names `+0x10`/`+0x13`/`+0x14`/`+0x16`/`+0x17` or draws the interval as a rectangle - all `UNRESOLVED`, all must stay labelled unknown |
| **`AUTHOR_NEW`** | no |
| **Public** | yes - the first warp editing capability |

---

### TOOLS-4 - Warp randomizer

| | |
| --- | --- |
| **Goal** | shuffle existing **destination keys** with a deterministic, reproducible seed, per a stated policy |
| **Dependencies** | TOOLS-3 |
| **Subsystem** | the connection writer plus a randomization policy module |
| **Kind** | `engineering` |
| **Acceptance** | every reshuffled destination resolves; the record set's other bytes are untouched; the permutation is reproducible from its seed; the policy is explicit about **self-links** (3 exist in the corpus), **one-way links** (20 exist) and whether reciprocity is preserved; a no-op seed reproduces the original image byte-for-byte |
| **Risk** | **low structurally, high in consequence if the policy is silent.** Rewriting two bytes can make the game unwinnable. The mitigation is that the tool must state its policy, refuse unresolvable keys, and never claim progression safety |
| **`AUTHOR_NEW`** | no |
| **Public** | yes - a headline modding feature |

---

### TOOLS-5 - Animation and frame in-place replacement

| | |
| --- | --- |
| **Goal** | replace an animation's cell pointers and a frame's piece records **in place at the same counts**, and replace a graphics container with one of the same decoded size |
| **Dependencies** | FIX-1, FIX-2 |
| **Subsystem** | the sprite codec's encode paths and a container same-size writer |
| **Kind** | `engineering` |
| **Acceptance** | a replaced animation object re-reads identically; a replaced frame's declared extents still equal its containers' declared decoded sizes; a same-size container replacement round-trips byte-for-byte; a replacement that changes a count, a size or a pointer target is refused rather than silently written |
| **Risk** | **medium.** "Same size, same shape" in-place editing is the only class where allocation, relocation and count updates all vanish. The risk is a caller that assumes a replaced payload may change size |
| **`AUTHOR_NEW`** | partial - it is the last step before creating new bodies |
| **Public** | yes - replace sprite graphics without changing the ROM layout |

---

## Phase 3 - Resource writing, allocation and encoding

**Theme:** produce **new** bytes. This is the phase where `NEEDS ENGINEERING` and
`NEEDS RESEARCH` separate cleanly: allocation and serialization are engineering,
packed-stream emission has open research items.

---

### WRITE-1 - Raw (form 0) container writer

| | |
| --- | --- |
| **Goal** | emit a stored-form Webfoot container: `u32` form `0`, `u32` declared decoded size, payload at `+0x08` |
| **Dependencies** | FIX-1 |
| **Subsystem** | `tools/webfoot/formats/webfoot_lz.py` (`build_stored` already exists; this ticket hardens and integrates it) |
| **Kind** | `engineering` |
| **Acceptance** | a generated stored container is read back by the project decoder and by an independent reader with identical bytes; the engine's own form-0 path (`memcpy` of exactly `container[+0x04]` bytes) is honoured; a zero-length stored container is legal and round-trips |
| **Risk** | **low.** The stored form is the simpler branch and is already implemented; the risk is integration, not correctness |
| **`AUTHOR_NEW`** | partial - it makes new resources representable but not yet sized |
| **Public** | no direct capability |

---

### WRITE-2 - Packed encoder

| | |
| --- | --- |
| **Goal** | emit a packed Webfoot container the engine decodes correctly, with the stream's control escape placed so decoding stops exactly at the declared size |
| **Dependencies** | FIX-1; the recommended research ticket `LOGX-CODEC-WRITE-001` (see §Follow-up research) |
| **Subsystem** | `tools/webfoot/formats/webfoot_lz.py` (`pack`), or a new encoder module |
| **Kind** | `engineering + research` - the wrapper and grammar are `CONFIRMED`; the **initial literal width** is `UNRESOLVED` and the marker-versus-declared-size disagreement rule has no canonical instance |
| **Acceptance** | decode(encode(x)) == x byte-for-byte; the emitted declared size equals the decoded length; the emitted end marker falls at that same length; the emitted stream length is measured and reported against `packed_end - offset`; the encoder **does not** rely on the unresolved dispatcher literal state, or the ticket resolves it first |
| **Risk** | **medium-high.** The engine performs **no** validation: a bad stream is not caught at runtime. `webfoot_lz.pack` already produces valid streams with a **measured size penalty**, so the open question is whether its output fits where it must go |
| **`AUTHOR_NEW`** | yes - it is the gate for every insertion capability |
| **Public** | no direct capability change until allocation exists |

---

### WRITE-3 - Allocator integration for the SDK's writing paths

| | |
| --- | --- |
| **Goal** | a writing path that places a newly authored resource in verified free space and returns the ROM address to point at it |
| **Dependencies** | WRITE-1, WRITE-2 |
| **Subsystem** | the existing free-space/relocation machinery (`FREE_SPACE_RELOCATION.md`, `ROM_EXPANSION.md`, `BUU_VERIFIED_CAPACITY.md`, `tools/webfoot/relocation.py`) plus the container writers |
| **Kind** | `engineering` |
| **Acceptance** | an authored resource is placed at a verified free address, the profile's capacity proof still holds, the placement is reproducible, and the original ROM is byte-identical afterwards; a placement that cannot fit fails closed |
| **Risk** | **medium.** Relocation logic already exists in this project and has its own regressions; the new risk is that container payloads are smaller and denser than the structures the existing allocator was built for. Blast radius is shared with every existing relocation consumer |
| **`AUTHOR_NEW`** | yes |
| **Public** | no |

---

### WRITE-4 - Graphics replacement and insertion

| | |
| --- | --- |
| **Goal** | replace or insert a sprite graphics container, by size-preserving replacement where possible and by allocation where not |
| **Dependencies** | FIX-2, WRITE-2, WRITE-3 |
| **Subsystem** | the graphics import path (`plan_pixels` / `apply_plan` / `import_graphic_png` currently have **no production caller**) plus the writers |
| **Kind** | `engineering` |
| **Acceptance** | an imported PNG produces a container whose decoded length equals `dim_0 * dim_1`; the piece's stored extents and attribute pair remain consistent with the new payload; the round-trip returns identical pixels; an import whose dimensions would change the declared size either allocates (WRITE-3) or is refused |
| **Risk** | **medium.** The pixel/PNG representation round-trip is already proved for the accepted corpus; the new risk is the write path and the OAM attribute consistency |
| **`AUTHOR_NEW`** | yes |
| **Public** | yes - "replace sprite graphics" and "import graphics" become user capabilities |

---

## Phase 4 - `AUTHOR_NEW`

**Theme:** create content that does not exist. Each ticket here is gated by a
research item or an allocation dependency; none is close to ready today.

---

### NEW-1 - New animation and frame authoring

| | |
| --- | --- |
| **Goal** | create a new animation object and its frame records rather than reusing existing ones |
| **Dependencies** | WRITE-3, TOOLS-5 |
| **Subsystem** | the sprite authoring path |
| **Kind** | `engineering` (the layouts are `STRUCTURALLY SOLVED`) with one caveat |
| **Acceptance** | a new animation's `frame_count` and `4*frame_count` cells are emitted; its two trailing words are **copied from a chosen existing record** rather than invented; a new frame's header bounding box is **computed** from its pieces and matches the engine's own rule; the definition's `+0x00` count is updated consistently and `+0x54 + 4*count` is the new extent |
| **Risk** | **medium.** The animation's two trailing words are `UNRESOLVED`; the ticket must preserve them from an existing record rather than guess. The count update is the coupled invariant |
| **`AUTHOR_NEW`** | yes |
| **Public** | yes |

---

### NEW-2 - New sprite definition

| | |
| --- | --- |
| **Goal** | append a new definition object to the pointer run and make it addressable |
| **Dependencies** | NEW-1, WRITE-3 |
| **Subsystem** | the sprite-definition table and the run at `0x086B6BDC` |
| **Kind** | `engineering` |
| **Acceptance** | a 298th definition body is materialised with the accepted extent formula; the run is extended **and its terminator word moved**; the accessor's literal still resolves; every existing id still resolves to the same target |
| **Risk** | **high.** The run is bounded by a literal plus a non-ROM terminator word, and the definitions do not tile one contiguous region (65 gaps of exactly `0x100`, each pointed at by the successor's `+0x04`). Relocating the run touches a literal in exactly two `ldr` sites and every id the game derives |
| **`AUTHOR_NEW`** | yes |
| **Public** | yes |

---

### NEW-3 - New appearance definition

| | |
| --- | --- |
| **Goal** | append a 233rd appearance definition |
| **Dependencies** | NEW-2, TOOLS-1 |
| **Subsystem** | the appearance table `0x0874D380` |
| **Kind** | `research + engineering` - the **table growth story is genuinely unresolved** |
| **Acceptance** | the 233rd record is reachable by the engine's own search; `+0x02 == +0x00 + 1` is preserved or the divergence is deliberately stated; the `+0x0C` stat index is either valid or negative |
| **Risk** | **high, and currently blocked by an unresolved fact.** The count is baked into **eight** engine sites as `cmp rN,#0xE8` with a pre-increment, there is no terminator, and the runtime roster walk is bounded by a 232-bit bitmap. Growing the table means either relocating it and following eight literal sites, or extending it in place and finding that every bound is a constant. This ticket must start with a bounded research question - *is the count reloadable, or is it a compile-time constant the engine never re-reads?* - and stop if the answer is "constant" |
| **`AUTHOR_NEW`** | yes |
| **Public** | yes |

---

### NEW-4 - Arbitrary new warp authoring

| | |
| --- | --- |
| **Goal** | create a new transition record with a new trigger region and a chosen arrival |
| **Dependencies** | TOOLS-3, TOOLS-4, WRITE-3, and **`LOGX-CONNECTOR-GEOMETRY-001`** |
| **Subsystem** | the connection writer, plus the root's coupled count/pointer pair |
| **Kind** | `research + engineering` |
| **Acceptance** | a new record's interval is a region the engine treats as a trigger, verified by runtime observation; its destination resolves; its arrival position and facing are controlled; the root's `+0x40`/`+0x44` pair stays coupled and the array does not collide with the bytes below the root |
| **Risk** | **very high, and blocked.** Three independent blockers: the `+0x00`/`+0x04` class pointers cannot be invented; the array is non-null-terminated with a null-coupled count; and the `root + 0x44 == root - 4*count` corpus layout means growth may overwrite the bytes immediately below the root. **Do not schedule before `LOGX-CONNECTOR-GEOMETRY-001` closes** |
| **`AUTHOR_NEW`** | yes - this is the flagship authoring capability for maps |
| **Public** | yes |

---

### NEW-5 - New map / scene materialisation

| | |
| --- | --- |
| **Goal** | author an entirely new map that the engine loads |
| **Dependencies** | NEW-4, NEW-3, WRITE-3, plus the unresolved root fields |
| **Subsystem** | the whole map-load template |
| **Kind** | `research + engineering` |
| **Acceptance** | the engine loads the authored map by key, resolves its root, builds four layers, streams chunks, and accepts a connection into and out of it |
| **Risk** | **very high.** Requires layer positioning (unknown), selector semantics above `1` (unresolved), the `+0x0C`/`+0x10` consumer (unrecovered), the `+0x24`/`+0x28` object types (unknown), and a verified allocator for every new structure plus five pointer/count updates per root. This is the last ticket in the roadmap, not the first |
| **`AUTHOR_NEW`** | yes - the terminal acceptance frontier |
| **Public** | yes |

---

## Phase 5 - Advanced / forensic (do not schedule without a product reason)

These are explicitly **not** recommended by the synthesis. They are listed so a
future reader knows they were considered and why they are parked.

| Item | Why parked |
| --- | --- |
| tile bits 12-15 semantics | zero in all 3,834,880 canonical entries. An editor must **preserve** them, which needs no semantics |
| LOGExtractor's connector `+8` | forensic curiosity; not needed to resolve a destination |
| the two connector record classes | does not block an in-place destination rewrite, which preserves `+0x00` byte-exactly |
| animation slot names | naming them would be an invented semantic; a UI may show index, occupancy and a preview |
| MapEntry's upstream-labelled metadata fields | the accepted discovery route uses `+0x00`, `+0x0C` and `+0x2C` only; an editor preserves the rest byte-exactly |
| the animation trailing words | preserving two unknown words needs no semantics; only `NEW-1` touches them, by copying |
| `SUBSYSTEM_MAP.md` / `GRAPHICS_FORMAT.md` address-notation pass | a documentation cleanup with no capability attached. Do it when a ticket next edits those files, not on its own |

---

## Randomized-warp readiness

Because connector research produced the queue's strongest low-risk use case, the
randomizer's assessment is stated separately from the roadmap.

### Structural randomization readiness

**Ready after `TOOLS-3` + `TOOLS-4`.**

| Question | Answer |
| --- | --- |
| **What fields change?** | exactly two bytes per record: `+0x11` (destination key high) and `+0x12` (destination key low). Nothing else |
| **What invariants must remain?** | (1) each new pair must resolve through the `0x080089FC` `MapEntry` lookup - the corpus has **0** unresolvable destinations, so a randomizer that produces one has created a state the canonical data never contains; (2) the record's other 22 bytes must be preserved byte-exactly, including the `+0x00` class pointer, the `+0x04` word and the four interval `u16`; (3) the root's `+0x40`/`+0x44` count/pointer pair must not change; (4) the record count must not change |
| **Can reciprocal links be preserved?** | Yes, and the tool must say **which policy it used**. Reciprocity is a measured property (**674 of 694** links), not an engine invariant: the corpus already contains **20 one-way** links and **3 self-links**. A randomizer may preserve, break or create reciprocity, but silence about the choice is not acceptable |
| **Can one-way / self links be allowed or forbidden?** | Either, by policy. Allowing them is faithful to the corpus; forbidding them is a stronger constraint that the corpus does not support as a rule. Self-links exist on maps 125, 126 and 127, so a policy that forbids them is **not** reproducing canonical structure - it is choosing one |
| **What progression validation would eventually be needed?** | That is the second half, below |

### Gameplay-logic and softlock validation - a separate problem

Structural randomization readiness says nothing about whether the result is
**playable**. Rewriting a destination can make the game unwinnable, and no
amount of LOGX research answers that. It requires world and progression
knowledge that is explicitly **outside** this research queue:

1. reachability of the start state under the shuffled graph (a graph-reachability
   computation over the 452-map link graph, which the connection reader makes
   possible);
2. key-item and flag gating, which lives in the script/event layer and not in the
   connection record;
3. one-way links as potential traps - 20 exist as authored content and a
   randomizer can create many more;
4. self-links as no-ops or as traps, depending on spawn semantics, which are
   `UNRESOLVED`;
5. a "solvable" certificate the tool can print, or an explicit statement that the
   tool does not guarantee solvability.

**Recommendation:** ship the randomizer as a **structural** tool that states its
policy, refuses unresolvable keys and never claims progression safety. Treat
solvability validation as a separate, later ticket owned by whoever owns
progression logic - not by the LOGX research line.

---

## Follow-up research

Only what materially blocks a scheduled capability. Full reasoning in
[`LOGX_SYNTHESIS.md`](LOGX_SYNTHESIS.md) §17.

| Ticket | Blocks | Priority |
| --- | --- | --- |
| **`LOGX-CODEC-WRITE-001`** | `WRITE-2` and therefore every insertion capability (`WRITE-4`, `NEW-1`..`NEW-5`). The encoder format is `PARTIAL`: the initial literal width is `UNRESOLVED`, no production encoder exists, and `pack` has a measured size penalty | **high** - the gate for Phase 3/4 |
| **`LOGX-CONNECTOR-GEOMETRY-001`** | `NEW-4` (arbitrary new warp trigger authoring) and map position authoring generally. Needs a runtime capture placing the player inside and outside a record's interval | **only when trigger authoring is scheduled.** Does **not** block `TOOLS-3`/`TOOLS-4` |
| **`LOGX-PORTRAIT-FORMAT-001`** | portrait import/replacement. The pointer relationship is `CONFIRMED`; the resource's pixel format, dimensions and rendering claim are not, and portrait recall is unmeasured | **only when portrait import is scheduled.** Non-blocking today |
| **`LOGX-RESTABLE-001`** | nothing currently planned. 177 of the 387 packed residuals sit in two size-locked pointer tables (`0x086F395C`, 155 x 4,096; `0x082ABF08`, 140 x 1,024) whose bases are computed and whose consumers are unknown | **conditional / low.** A sixth of the population turned out to be the known `compressed_text` store, so the remaining unknown is two homogeneous tables with no consumer |

---

## Recommended first implementation ticket

**`FIX-1` - strict decoded-size enforcement in `webfoot_lz`.**

It is the only Phase 1 item that every later writing capability depends on, it is
the smallest change in the roadmap, its failure mode is the most damaging one
available (a silently truncated payload reported as success), and it is already
proven reproducible by a pinned test. It needs no research, no allocation and no
new format knowledge.

**`FIX-2` and `FIX-3` should follow immediately as one window**, because the
reader and the codec must agree before any graphics editing is built on them; but
`FIX-1` is first because a wrong decoder can corrupt a payload that a correct
parser then faithfully reports as valid.

---

## Queue summary

| Phase | Tickets | Gating fact |
| --- | --- | --- |
| 1 - Correctness and parser repair | `FIX-1` .. `FIX-6` | none. Every item is engineering with a `CONFIRMED` target structure |
| 2 - Verified existing-content tools | `TOOLS-1` .. `TOOLS-5` | needs Phase 1's parsers for `TOOLS-2`/`TOOLS-5`; `TOOLS-3`/`TOOLS-4` need nothing from Phase 1 |
| 3 - Resource writing and allocation | `WRITE-1` .. `WRITE-4` | `LOGX-CODEC-WRITE-001` for `WRITE-2` |
| 4 - `AUTHOR_NEW` | `NEW-1` .. `NEW-5` | `LOGX-CONNECTOR-GEOMETRY-001` for `NEW-4`; `NEW-3` starts with a bounded research question about the table count |
| 5 - Advanced / forensic | not scheduled | no product reason |
