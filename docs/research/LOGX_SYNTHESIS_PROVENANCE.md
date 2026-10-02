# LOGX-SYNTHESIS-001 provenance: audit method, measurements and limits

Evidence document for **LOGX-SYNTHESIS-001**, the final ticket of the
LOGExtractor-derived research queue. Companion to
[`LOGX_SYNTHESIS.md`](LOGX_SYNTHESIS.md) (the human-readable synthesis) and
[`POST_LOGX_IMPLEMENTATION_ROADMAP.md`](POST_LOGX_IMPLEMENTATION_ROADMAP.md)
(the implementation queue).

This document records **what this ticket itself measured or audited**, so that
the synthesis's claims are separable from the ten tickets it summarizes. The ten
tickets' own provenance is in their own files and is not duplicated here.

```text
START SHA:             0000000000000000000000000000000000000000
BRANCH:                logx-synthesis-001
WORKTREE:              <temporary directory>\log1-remake-logx-synthesis-001
CANONICAL ROM SHA-256: 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
```

## Scope, and what this ticket deliberately did not do

Research and documentation only. **No GUI, no Workbench, no map-renderer, no
production parser, no codec, no authoring surface and no ROM was modified.** The
active WORKBENCH-006 worktree was not touched. Every production defect found is
**inventoried, not fixed**, because fixing it is a post-freeze engineering
ticket with its own review gate.

---

## 0. Audit tooling

### 0.1 `tools/research/logx_synthesis_audit.py`

A deterministic, read-only, ROM-free audit. It has no third-party dependency
(not even `capstone`), opens every file through `Path.read_text`, and writes
nothing. It answers three mechanical questions:

1. **`check_documents()`** - does every one of the ten accepted tickets have a
   non-empty review record, closeout record and provenance document at the path
   the synthesis cites?
2. **`check_synthesis_matrix()`** - does `docs/research/LOGX_SYNTHESIS.md` agree
   with the module's own `CANONICAL_FACTS` table, and do its read-support and
   authoring-readiness tables use only their declared vocabularies?
3. **`superseded_hits()`** - does any refuted LOGExtractor assumption from
   synthesis §10 still appear in the scan scope (live code and current canonical
   documentation)?

Run it with:

```text
python -m tools.research.logx_synthesis_audit
```

It exits `0` when it reports no findings and `1` otherwise, and prints a JSON
report containing every finding with its `file:line`, pattern key, one line of
context and a `production` flag.

**Historical correction context is excluded by construction.** A line that
carries `superseded`, `refuted`, `added later`, `corrected`, `historical`,
`logx-synthesis-001`, `no longer`, `is not a run base` or `must not be` is
**not** a finding: it is the evidence trail quoting a refuted reading in order to
refute it. The historical ticket records are also outside the scan globs
entirely, because editing them would destroy the record of what was believed and
corrected.

**The audit does not manufacture completeness.** A pattern that produces no hit
is reported as no hit; four of the fourteen refuted patterns produce **zero**
hits repository-wide (see §4.3).

### 0.2 `tests/unit/test_logx_synthesis_audit.py`

Portable synthesis tests. They assert the audit's invariants, not prose:

* every `CANONICAL_FACTS` entry is cited to one of the ten tickets;
* the synthesis document's fact table agrees with `CANONICAL_FACTS` exactly, in
  both directions, so a new fact cannot be added to the document without a
  citation and a fact cannot be dropped silently;
* the read-support and authoring-readiness tables use only their vocabularies;
* **no `PRODUCTION BUG`-class superseded hit survives** anywhere in the scan
  scope;
* the ten tickets' canonical documents all exist and are non-empty;
* the audit is deterministic (two runs give byte-identical reports).

These tests follow the project's existing documentation-consistency convention
(`tests/unit/test_code_review_workflow.py` normalizes whitespace and asserts
required substrings). No brittle whole-sentence prose assertions were added.

---

## 1. ROM Bible consistency audit (`docs/reverse-engineering.md`)

**Method.** The 1,150-line Bible was read in full alongside each of the ten
tickets' review records and provenance documents. Every LOGX-section field row
was compared against the ticket that owns it, by address notation, width,
signedness, count, pointer-versus-index semantics, population totals and status
language. Then the legacy ROM-00x sections (lines 1-357), which the ten tickets
did **not** rewrite, were re-read against the accepted conclusions, because a
reader who lands there sees them before the LOGX block.

**Result: `UPDATED`.** Nine corrections were applied. Each was re-derived from
the owning ticket's accepted wording before being written; none was applied on a
reviewer's assertion alone.

| # | Location | Was | Now | Owning ticket |
| ---: | --- | --- | --- | --- |
| C1 | LOGX-CODEC-001 section | "`0x0803D966` ... It has no `BL` caller in the image" | a second dispatcher entry whose `r2` is only NULL-tested and is then a **per-byte lookup-table pointer**, not a length; it has **exactly one** `BL` caller, `0x0800F3D2`; the "no caller" and "length-aware" readings are recorded as **withdrawn** | LOGX-CODEC-001 (A6/A7) |
| C2 | LOGX-CODEC-001 section | blob ROM base "**INFERRED** from the library table at `0x087B7970`" | "**CONFIRMED** from the startup DMA3 literals at `0x08000148`/`0x0800014C`/`0x08000150`, which copy 4,100 bytes from `0x087B79A4` to `0x03000000`"; the library-table reading is named as withdrawn | LOGX-CODEC-001 (A5) |
| C3 | LOGX-CODEC-001 section | default container "followed by `0x800` zero bytes" | followed by **2,040 (`0x7F8`)** zero bytes, the first non-zero byte `0xFF` at `+0x800` | LOGX-CODEC-001 (N2) |
| C4 | LOGX-FRAME-001 section | "The engine also mirrors the index arithmetically (`0x0801AF96 ...`), which is consistent with four positions plus a flip" | a **NOT direction evidence** paragraph: the site writes `obj+0x11`, the *frame index*, so the claim is withdrawn; the four-position structure rests on the facing computers' write set and the shared-target measurement | LOGX-FRAME-001 (correction 9) |
| C5 | LOGX-FRAME-001 section | "the object is `0x04 + 16*frame_count + 8` bytes" | the counted extent is that, **but** in 30 of the 1,017 objects a frame record begins exactly there, so the trailer's existence and extent are `UNPROVEN` | LOGX-FRAME-001 (correction 11) |
| C6 | LOGX-FRAME-001 section | 7,355 described as "a different population" from 7,390 | 7,355 is an exact **subset** - the single-piece-frame set - and the extra 35 are exactly what the 21 multi-piece frames reach; **7,390 is the accepted figure and 7,355 is stale as a headline count** | LOGX-FRAME-001 |
| C7 | `## Buu's Fury MapEntry` | nine `*_pointer_raw` rows and no statement of the accepted key | a new paragraph stating that `+0x00`/`+0x01` are **two ordered key bytes** (big-endian is a display), `CONFIRMED` as a key and byte order with the semantic identity `UNRESOLVED`; `+0x0C`'s low `u16` resolves through `0x0806BCE8` (`CONFIRMED` relationship, `UNRESOLVED` purpose); the remaining `_raw` names are upstream labels carried for history | LOGX-MAP-RECORD-001 |
| C8 | `## ROM-003 pointer-field census` and `## ROM-004` | Category B/C ranking and "Category A ... none", with no superseding note | a superseded note: `MapEntry+0x2C` is an engine-confirmed indexed word source (`0x080089CC`, `source + 4*(selector-1)`) whose selector-1 target is the confirmed load-time template; the ranking is historical | LOGX-MAP-RECORD-001, LOGX-MAP-RENDER-001 |
| C9 | `## ROM-007` and `## ROM-008` | "**STRONGLY SUPPORTED: rectangle-aware runtime object**" (twice) | "runtime object whose engine-read bounds are the record's two ordered `u16` intervals", with the two-axis "rectangle" reading named as **demoted to `UNRESOLVED`** | LOGX-CONNECTOR-001 |
| C10 | new section | LOGX-GFXSCAN-001 had **no** section | a new **`## LOGX-GFXSCAN-001 external scanner, measured (no format claim)`** section recording the scanner's rule set, suitabilities, recall, the two self-inflicted blind spots, the non-disjoint class sum, and the discipline. Every other LOGX ticket has a schema section; this one is explicitly a measurement of a tool | LOGX-GFXSCAN-001 |

### 1.1 What the audit verified clean

Recorded so the coverage of the audit is visible rather than implied:

* **Address notation** - every LOGX section keeps GBA address and file offset
  distinct (`:37`/`:42`, `:734-735`, `:788`/`:801`, `:11`/`:619-621`).
  `docs/reverse-engineering.md` is one of the good examples in the project.
* **Widths and signedness** - MapEntry, root, layer, connector, tile, appearance,
  definition, animation, frame and piece field widths all match their tickets,
  including root `+0x08`/`+0x0A` as `extent - 1`, layer `+0x14`/`+0x15` as
  separate unsigned bytes with `+0x16` signed, connector `+0x08`..`+0x0E` as four
  LE `u16` with signedness `UNRESOLVED`, appearance `+0x0C` as a signed `i32`
  sign-tested with `blt`, and the frame header as `u32` + `s8`/`s8`/`u8`/`u8`.
* **Pointer versus index** - `+0x2C` as an indexed word source; appearance
  `+0x04`/`+0x08` as indices into pointer arrays; the layer `+0x18` **4-byte**
  array versus the root `+0x24`/`+0x28` **`0x18`-byte** stride.
* **Destination representation** - documented as two independent key bytes at
  `+0x11`/`+0x12`, with the `REFUTED` big-endian-`u16` reading named as such.
* **Layer `+0x00`** - documented as an odd Thumb handler entry, not a type tag.
* **Tile bits** - bits 12-15 documented as reserved/constant **with the explicit
  instruction not to call them "unused by the format"**.
* **Container model** - dispatcher, forms `{0,1,2}`, `+0x04`, `+0x08`,
  `UnknownHeader` refutation, 64 KiB refutation and the absent destination
  capacity are all present and correct.
* **Populations** - 452/`0x38`, 232/`0x10`, 297 with ids 10..306, 4,070 /
  1,721 / 2,349, 1,017 / 13,660 / 10,980, 11,005 pieces (10,959 + 19 + 2), 7,390,
  3,745, 187 banks, 4,520 / 4,324 / 4,322 / 2, and the connector 735 / 694 / 674 /
  20 / 3 all reproduce their tickets.

### 1.2 Documentation gaps found and how they were resolved

Three gaps were identified and are **recorded rather than silently filled**:

1. **LOGX-GFXSCAN-001 had no section.** Resolved by C10. The ticket's
   `ROM_BIBLE_IMPACT` was `NONE` by its own decision (it promoted no format
   claim), so the section this synthesis adds is a **pointer and a measurement
   summary**, not a schema.
2. **LOGX-MAP-RECORD-001's accepted key/text findings had never landed in the
   Bible.** Its review recorded "ROM Bible impact: none - the physical facts were
   already documented", which was true of the table/stride/count but not of the
   two-byte key reading or the `+0x0C` text resolution. Resolved by C7.
3. **Several accepted secondary facts are still absent** from the Bible and are
   left absent deliberately, because they are not needed by any planned
   capability and adding them would widen a documentation audit into new
   writing: MapEntry `+0x05` as the length of the `+0x18` array; the root
   `+0x50`/`+0x54` handler+size shape; the per-frame BGxCNT offset at
   `0x080093E2`/`0x080093E4`; the layer's 19 dominant-shape records no root
   references; the 2,994 shared graphics targets; the 9,963-of-10,979 frame-pair
   figure; and the CODEC per-class reference counts. Each is cited in
   `LOGX_SYNTHESIS.md` and remains available in its ticket.

### 1.3 Cross-ticket arithmetic discrepancy, recorded not reconciled

LOGX-TILE-001 reports **4,118 non-null array-element references** and
LOGX-CODEC-001 reports **3,912 dominant-chunk container references** for the same
resource class. Neither ticket reconciles the two, and this synthesis does
**not** invent a reconciliation: they are two accepted measurements at different
granularity, and the unit each owns is named in the synthesis. The figure both
tickets agree on is the **3,745 distinct payloads**.

---

## 2. `GRAPHICS_FORMAT.md` consistency audit

**Method.** The document was read in full after LOGX-SPRITE-001 and
LOGX-FRAME-001, and each claim about the definition/animation/frame/piece chain
was compared against those two tickets. Adjacent graphics documents
(`MAP_FORMAT.md`, `MAP_RENDER_FORMAT.md`, `ENTITY_FORMAT.md`,
`COLLISION_FORMAT.md`, `consumer-analysis.md`) and `PROJECT_<local-state-name>` .. `_8`
were swept for the same models.

**Result: `UPDATED` with a superseded-statements banner.**

The document already carried dated in-place correction notes
(`> **(LOGX-*-001, added later ...)**`) for several superseded readings, but a
reader landing in the middle of the file - or quoting a section - still met the
stale figure first, and three passages had no note at all. A **banner** was added
at the top listing every refuted or offset-corrected claim with the canonical
position and the superseding ticket, and stating explicitly that **where a figure
below disagrees with the banner, the banner wins**.

| Superseded claim | Disposition |
| --- | --- |
| frame record is `u32 piece_count` then **16-byte** pieces | `REFUTED` - 8-byte header then 12-byte pieces |
| piece attribute word at `+0x08`, graphics pointer at `+0x0C` | offset-corrected - attributes `+0x04`, graphics `+0x08`; bit layout confirmed |
| "all 10,959 frames declare exactly one piece" | `REFUTED` - 19 two-piece and 2 four-piece frames |
| "Unique graphics containers: 7,355" | **exact subset**, not the total; the corpus reaches 7,390 |
| "13,596 direction slots / 0 NULL" | confirmed for that reader's population, extended to 13,660 / 0 |
| the animation array is bounded by walking to the next structure | `REFUTED` - `structure + 0x00` bounds it; correcting the walk is a numerical no-op |
| LOGExtractor's fixed **23-slot** table | `REFUTED` as a physical model |

**Also corrected by this ticket, outside the banner:**

* the two production defects the banner names are scheduled in the roadmap
  (`sprite_graphics.py`'s 4+16 layout and `graphics.py::_animations_in`'s
  unbounded walk);
* the document's `0x179764` passage, which still framed it as a standalone
  `level_tileset_table` "with a per-level pointer at `+0x4C`", now states the
  accepted ownership: GBA `0x08179764` is the **value stored at `root+0x4C`** on
  all 452 selector-1 roots and points at the **187-entry selector-bank container
  table**.

**Historical text is preserved, not deleted.** The dated notes remain as the
record of what was corrected and when. The banner exists so the *current* reading
is unambiguous, which is what the ticket requires.

**Verified consistent, no change needed:** `MAP_RENDER_FORMAT.md` (its
"animation record / frame_count" is the *map animated-tile* family - a distinct
structure from the sprite animation object); `MAP_FORMAT.md`;
`COLLISION_FORMAT.md` (refuses collision/hitbox semantics explicitly);
`consumer-analysis.md` (refuses graphics naming explicitly); `PROJECT_<local-state-name>`
through `_7.md`. `PROJECT_<local-state-name>` was `CONSISTENT WITH MARKED HISTORICAL
TEXT` **except** its `## Next` block, corrected in §5 below.

**One address-notation debt is recorded, not fixed here.**
`GRAPHICS_FORMAT.md` never declares its GBA-versus-file-offset convention, and
several values appear in bare file-offset form (`0x006B6BDC`, `0x00711274`). The
banner states the convention for the chain it corrects; a systematic notation
pass over that document belongs to whatever ticket next edits it, not to a
synthesis audit.

---

## 3. Bounded investigation of the 387 referenced residuals

**Authorization and budget.** The ticket permits a **bounded** investigation of
the lead GFXSCAN handed synthesis: the pointer/reference structure around
`0x087B5B64`. It explicitly forbids an open-ended campaign, absorbing a new
subsystem, and claiming graphics without proof. This investigation used the
existing accepted tooling as libraries (`tools/research/logx_gfxscan_probe.py`,
`tools/research/thumb_disasm.py`) and one purpose-built read-only scratch probe
under the ignored `build/` tree; **no new disassembler and no production code
were written.**

**ROM safety.** Verified before and after:

```text
BEFORE 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
AFTER  940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
size   8,388,608 bytes; opened read-only through Path.read_bytes; no write path exists
```

### 3.1 `0x087B5B64` - the structure, measured

| Property | Measurement |
| --- | --- |
| extent | exactly **7 words**, `0x087B5B64..0x087B5B7C` (28 bytes) |
| alignment | word-aligned (address mod 4 = 0, mod 8 = 4) |
| word validity | **7 of 7** are valid in-ROM GBA addresses (`0x08xxxxxx`) |
| indirection | **none** - all 7 point directly at container headers |
| target form word | `1` (packed) on all 7 |
| boundary | of the 18 words after the table, only one is an in-ROM pointer (`0x087B5BA4` -> `0x087B5BB0`); `0x087B5B80..0x087B5B94` are `0x03xxxxxx` EWRAM addresses, so the 7-word boundary is real |
| targets and declared sizes (`+0x04`) | `0x0879BF2C` 65,348; `0x087A04F0` 65,474; `0x087A46C8` 65,464; `0x087A8AD8` 65,334; `0x087AD118` 65,322; `0x087B1558` 65,394; `0x087B5AA0` 436 |

**It is already a documented subsystem.** The table is
`compressed_text.pointer_table` in the shipped atlas evidence
(`tools/webfoot/atlas_producers/seed.py:686-704`, whose own gate reads
"STRUCTURAL GATE: exactly 7 containers"), and it is recorded in
`docs/research/BUU_MAP_EVENT_REFERENCES.md`, TEXT-HANDLE-001/-002,
ROM-EXPAND-001 ("authoritative seven-container table") and TEXT-INDEX-001 (688
runs / 195,328 already indexed). It is the **compressed-text (dialogue text
store) selector table**.

**Its consumer is reachable and known.** A whole-image word sweep for
`0x087B5B64` returns **exactly one** citing word, `0x080123CC`, a literal in
code. That single literal is shared by both documented consumers:

```text
0x08012242  halfword 0x4962  ldr r1,[pc,#0x188]  -> 0x08012244 + 0x188 = 0x080123CC
0x080122C8  halfword 0x4940  ldr r1,[pc,#0x100]  -> 0x080122CC + 0x100 = 0x080123CC
0x08012248  halfword 0x5808  ldr r0,[r1,r0]      ; selects table[handle & 0x3F]
```

`compressed_text.consumer_08012230` is `RUNTIME_CONFIRMED` (65 live hits via
TOOLKIT-031); `compressed_text.consumer_080122B4` is `CONFIRMED` statically. The
sweep hit and the offset arithmetic are this investigation's measurement; the
instruction decoding is taken from the documented halfword bytes in `seed.py`.

**Consequence for the synthesis:** `LOGX_SYNTHESIS.md`'s open question about the
meaning of the `0x087B5B64` structure is **answered by pre-existing records**,
and **6 of the 387 residual containers are a family this project already reads**.
They must not be presented as an unknown.

### 3.2 How the 387 are reached, and the decomposition

| Mechanism | Measurement |
| --- | --- |
| reachability model | the probe's reference index is a **whole-image word-aligned sweep** for a stored word equal to the container address (`logx_gfxscan_probe.py:1327-1406`) |
| code-flow involvement | **none** - no container is reached by a `bl` target or by any decoded instruction |
| word positions swept | **2,097,152** |
| coverage statement | 1,508 targets with a full-GBA-address hit and 38 with only a bare file-offset hit; **computed arithmetic, folded bases and `LDM`/`STM` aggregates are not covered** |
| citing sites | 480 total: 260 inside runs of >= 2 consecutive in-ROM pointers and 220 isolated |
| 251 / 387 | have at least one citation inside a pointer run |
| 136 / 387 | have only isolated-word citations |

**The 387 decompose into three pointer tables plus a remainder:**

| Family | Table | Words | Members in the 387 | Established |
| --- | --- | ---: | ---: | --- |
| `compressed_text` | `0x087B5B64` | 7 | **6** | `ALREADY-KNOWN FAMILY`: consumer `0x080123CC`, table role and the exactly-7 gate are documented |
| size-locked 4,096 family | `0x086F395C..0x086F3BC4` | 155 | **95** | structure `CONFIRMED`; **semantic family UNKNOWN** |
| size-locked 1,024 family | `0x082ABF08..0x082AC134` | 140 | **82** | structure `CONFIRMED`; **semantic family UNKNOWN** |
| remainder | - | - | **204** | cited only by short runs or isolated words |

`6 + 95 + 82 = 183` of the 387 lie in exactly three pointer tables. Each of the
seven `0x087B5B64` targets is cited by exactly its own table slot. The seventh
target `0x087AD118` is a valid form-1 candidate declaring 65,322 but the probe
classifies it as a scanner false positive, which is why only six of the seven
enter the 387.

**The two size-locked tables have no nameable consumer.** Neither `0x086F395C`
nor `0x082ABF08` is named by **any** word in the image (whole-image sweep count
**0** for both), so each base is **computed or folded** and no consumer is
reachable through the pointer/literal model. The only code-region citation sites
for any of the 387 are `0x08004EFC`, `0x08028118` and `0x0802837C`.

### 3.3 Size distribution, re-measured

Method: for each of the 387 `kind == 1` engine-referenced novel residuals, read
the declared decoded byte count `u32` at container `+0x04`. All 387 decode to
exactly that declared size.

| Quantity | Value |
| --- | ---: |
| minimum | 128 |
| maximum | 65,474 |
| median | 1,024 |
| mean | 3,017.66 |
| `256` | 129 |
| `4,096` | 97 |
| `1,024` | 88 |
| `2,048` | 24 |
| `8,192` | 16 |
| other | 33 |
| **>= 8 KiB** | **26** |

Buckets: `0..255: 2`, `256: 129`, `257..511: 1`, `512..1023: 3`, `1024: 88`,
`1025..2047: 7`, `2048: 24`, `2049..4095: 7`, `4096: 97`, `4097..8191: 3`,
`8192: 16`, `>8192: 10`.

**This corroborates LOGX-GFXSCAN-001 exactly** - 129 at 256 bytes, 26 at or above
8 KiB, 88 at 1,024, 97 at 4,096, 24 at 2,048, 16 at 8,192 and 33 other - so the
ticket's `387` profile needed **no correction**.

**One new discriminator, measured:**

```text
381 of 387 decoded lengths are divisible by 32.
The 6 exceptions are EXACTLY the 6 compressed_text members:
  65,348 / 65,474 / 65,464 / 65,334 / 65,394 / 436
```

So "not a whole number of 32-byte tiles" and "the already-known text store" are
the same set. **32-byte divisibility is a necessary condition and nowhere near a
sufficient one** - it must not be used as a graphics or tile-bank test.

### 3.4 Verdict, and what was not determined

```text
CLASSIFICATION VERDICT: UNCLASSIFIED - needs a targeted ticket
SUB-VERDICTS:
  (a)  6 / 387  ALREADY-KNOWN FAMILY `compressed_text`
  (b) 177 / 387  two size-locked data-region pointer tables, STRUCTURE known,
                 SEMANTIC family UNKNOWN, no nameable consumer
  (c) 204 / 387  cited only by short runs or isolated words
```

**Not determined, and stated rather than papered over:**

1. why **60** of table A's 155 members and **58** of table B's 140 members fall
   *outside* the 387 (their probe categories were not measured). This decides
   whether those members are a different container form;
2. the semantic identity - graphics, audio, script or something else - of the
   155 x 4,096 and 140 x 1,024 families;
3. any consumer for the **381** non-text members, because the coverage model
   explicitly excludes computed, folded and aggregate accesses;
4. whether a structural header precedes either size-locked table (the runs are
   maximal pointer runs; no surrounding structure was read);
5. whether the 387 overlap LOGX-CODEC-001's non-root dominant-chunk reach.

**No graphics semantic and no new canonical resource class is claimed for the
387.** They are not one family. The follow-up recommendation is
`LOGX-RESTABLE-001` in `LOGX_SYNTHESIS.md` §17 and the roadmap, and it is
explicitly **conditional and low priority** now that a sixth of the population is
known and the remainder is two structurally homogeneous tables with no consumer.

---

## 4. Repository-wide stale-assumption audit

### 4.1 Method

Fourteen refuted LOGExtractor assumptions (synthesis §10) were searched across
the tracked tree with case-insensitive `git grep` over source, docs, config,
tooling, tests and profile data. Ignored scratch trees (`build/`, `.git/`,
`.pytest_cache/`, `node_modules/`, `.venv/`, `extern/`) were excluded. Every
surviving hit was classified with the vocabulary in synthesis §11.5.

The mechanical subset of that audit is now encoded in
`tools/research/logx_synthesis_audit.py`, whose scan scope is **live code and
current canonical documentation**. Historical ticket, provenance and archive
records are out of scope by design: they preserve the superseded wording as the
evidence trail, and editing them would destroy the record of what was believed
and corrected.

### 4.2 Result

| Class | Count | Where |
| --- | ---: | --- |
| `PRODUCTION BUG` | in `tools/webfoot/formats/sprite_graphics.py` and `tools/webfoot/graphics.py` | the two deferred defects in synthesis §11.2 and §11.3 |
| `STALE DOCUMENTATION` | `GRAPHICS_FORMAT.md` (un-noted totals), `docs/architecture.md`, `docs/project-format.md`, `docs/research/SUBSYSTEM_MAP.md`, `THIRD-PARTY-NOTICES.md`, `config/roms.yaml` and its packaged copy `tools/webfoot/data/roms.yaml`, and docstrings in `build.py`, `cli.py` (user-visible help), `atlas_producers/seed.py`, `webfoot_lz.py` | the `7,355` subset presented as the corpus total, the structure-to-structure animation walk presented as the method, and the single-piece-only frame model |
| `PRODUCTION BUG` (output quality, outside the canonical path) | `tools/webfoot/atlas_producers/scan.py::_compression_rows` | a stride-4 heuristic sweep whose own docstring calls its output noise (24,285 hits / 68.7 MiB); recorded by LOGX-GFXSCAN-001 and inventoried in `LOGX_SYNTHESIS.md` §11.6 |
| `TEST EXPECTATION` | `tests/integration/test_graphics_rom.py` (`UNIQUE_GRAPHICS = 7355` and four dependants), `tests/unit/test_sprite_graphics.py` (16-byte piece and 4-byte-header fixtures), `tests/unit/test_logx_sprite_reference.py` (pins `FRAME_FIRST_PIECE == 0x04`, `PIECE_RECORD_SIZE == 0x10`) | these tests encode the refuted layout and **must move with the parser correction**, not before it |
| `RESEARCH-ONLY LEGACY` | the ten tickets' review, provenance and archive records; `tools/research/logx_sprite_probe.py` (which still models the 4-byte header while the newer `logx_frame_probe.py` uses `0x08`); `docs/research/AUTO_RE_<local-state-name>`; earlier `PROJECT_STATE` parts | preserved deliberately |
| `HARMLESS COMMENT` / `NO LONGER USED` | none material | - |

**No `PRODUCTION BUG`-class hit survives in the audit's scan scope once the
historical markers are honoured**, and the audit test asserts that. The
remaining production hits are exactly the two defects synthesis §11.2 and §11.3
name, both of which are scheduled in Phase 1 of the roadmap.

### 4.3 Patterns with zero surviving occurrences

Four of the fourteen refuted assumptions produce **zero** hits repository-wide,
in any class:

* a ~64 KiB engine or format limit;
* "a zero first wrapper word means empty";
* layer `+0x00` as a numeric type tag;
* the connector destination stored as a big-endian `u16`.

Five more (the `0x6B6BB4` run base, the fixed 23-slot model, `UnknownHeader` as a
canonical wrapper, LOGExtractor's connector `+8`, and `0x179764` as a standalone
atlas table) survive only as **quoted external claims or explicit refutations**,
plus one stale `GRAPHICS_FORMAT.md` passage for `0x179764` which this ticket
corrected.

Two near-misses are **not** hits and are recorded so they are not "fixed" by
mistake: `webfoot_lz.DEFAULT_MAX_OUTPUT = 64 * 1024` is a documented **host
safety limit** whose own docstring says it is not a format fact, and
`graphics.py`'s `maximum_size=64 * 1024` is a decode-plausibility filter. The
largest **reachable** declared size in the accepted corpus is `0x4000` (16 KiB)
and the largest declared size anywhere in the image is `65,474` bytes - below
65,536, so neither filter can change behaviour and the `LOGX_SYNTHESIS.md` §10
#20 refutation still holds.

### 4.4 One production defect the ten tickets recorded and had to be added

Reviewer B found that LOGX-GFXSCAN-001's production-follow-up list names
`tools/webfoot/atlas_producers/scan.py::_compression_rows` as a stride-4
heuristic sweep whose own docstring calls its output noise, and that neither the
synthesis nor the roadmap mentioned it. The finding was reproduced
(`scan.py:331`, `:380-382`: **24,285 hits / 68.7 MiB**, "overwhelmingly probe
noise"), accepted, and is now inventoried as `LOGX_SYNTHESIS.md` §11.6 with an
explicit disposition. The same review also flagged
`sprite_graphics.decode_animation`'s `maximum_frames = 64`, which this synthesis
records §11.3 as a **recorded disagreement rather than a defect**: `64` is a
bound, the canonical `frame_count` range is `1..16`, and removing it would delete
a sanity check with no demonstrated benefit.

---

## 5. Other corrections made by this ticket

| File | Correction |
| --- | --- |
| `docs/PROJECT_<local-state-name>` | its `## Next` block still named `LOGX-GFXSCAN-001` as NEXT with baseline `b5d87aed022cb09083f51c34fe50c81c4f944c5b`, contradicting the same file's own header (GFXSCAN COMPLETE / ACCEPTED) and its "Current Baseline" entry (LOGX-SYNTHESIS-001 next). Corrected to name `LOGX-SYNTHESIS-001` with the authorized baseline `0000000000000000000000000000000000000000`, and the original paragraph retained beneath as marked history |
| `docs/research/GRAPHICS_FORMAT.md` | superseded-statements banner; the `0x179764` ownership correction; the two named production defects cross-referenced to the roadmap |
| `docs/reverse-engineering.md` | the ten corrections in §1 |

No historical review, provenance or archive record was edited.

---

## 6. Test and validation results

Reported as measured. Environment note: this worktree has no local `roms/`
directory and no junction was created for it (`LOGX-CHAR-001` recorded that a
`roms/` junction inside a worktree breaks
`tests/unit/test_project_safety.py::test_proprietary_and_generated_paths_are_git_ignored`).
The canonical image is supplied only through `LOGX_CANONICAL_ROM`.

| Suite | Command | Result |
| --- | --- | --- |
| synthesis audit (portable) | `pytest tests/unit/test_logx_synthesis_audit.py -q` | see the ticket review record |
| synthesis audit instrument | `python -m tools.research.logx_synthesis_audit` | exits **1** with **28 findings** (5 in live code), every one already inventoried in `LOGX_SYNTHESIS.md` §11.1-§11.6; the instrument reports, it does not fix |
| LOGX portable unit suites | `pytest tests/unit/test_logx_*_reference.py tests/unit/test_logx_*_probe.py tests/unit/test_logx_frame_probe.py -q` | see the ticket review record |
| LOGX ROM-gated integration suites | `pytest tests/integration/test_logx_*_rom.py -q` with `LOGX_CANONICAL_ROM` set | see the ticket review record |
| projector/safety/workflow | `pytest tests/unit/test_project_safety.py tests/unit/test_rom_safety.py tests/unit/test_code_review_workflow.py tests/unit/test_workflow_migration.py -q` | see the ticket review record |
| ROM-absent behaviour | the same LOGX integration suites with `LOGX_CANONICAL_ROM` pointed at a non-existent path | must skip cleanly, 0 failures |
| whitespace | `git diff --check` | must be clean |
| ROM identity | SHA-256 before and after | `940AD5F0...F059E`, unchanged |

The full repository suite is **not** run by this ticket by default: this ticket
changes documentation, one new research module and one new portable test file,
and modifies **no production code**, so its blast radius is bounded by the LOGX
suites plus the safety/workflow files. If the review round changes that scope,
the suite gate applies.

---

## 7. Limits of this synthesis

* **No ROM decoding was re-derived.** Every population in
  `LOGX_SYNTHESIS.md` is quoted from the ticket that owns it, except the residual
  measurements in §3 above, which were measured here and state their method.
* **Only one bounded new investigation was performed** (§3). It is deliberately
  narrow, used the accepted tooling as libraries, and stopped at the budget
  rather than widening.
* **Consistency was checked against accepted documents, not by re-measuring the
  ROM.** A stale figure shared by a ticket, its provenance and the Bible would
  survive this audit. That is why the synthesis cites the owning ticket for every
  number and why the follow-up research list is separate from the read-support
  claims.
* **Historical records were not edited.** Superseded wording in the ten tickets'
  own review, provenance and archive files is preserved as evidence.
* **No decode was taken on trust, and no limit is an engine limit.** The packed
  decoder's own `DEFAULT_MAX_OUTPUT = 64 * 1024` is a **host safety bound**, not a
  format maximum; the largest **reachable** declared size in the accepted corpus
  is `0x4000` (16 KiB), and the largest declared size anywhere in the image is
  `65,474` bytes - still below 65,536, which is why the refutation in
  `LOGX_SYNTHESIS.md` §10 #20 holds.
* **Production defects were inventoried, not fixed.** No production parser,
  codec, renderer or authoring path was modified.
