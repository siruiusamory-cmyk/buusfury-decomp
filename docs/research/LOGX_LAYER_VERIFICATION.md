# LOGX-LAYER-001 review

Reconstruct Buu's Fury layer record structure. Research only.

## Repository and safety

- **START SHA:** `67fe01bdd8457954382190400870c3291449938a`
- **END SHA:** the branch head of `logx-layer-001` after this commit
  (`git rev-parse logx-layer-001`); it is one commit past the two SHAs below
  because this document records them in the commit that follows them
- **BRANCH:** `logx-layer-001`
- **COMMIT SHA(S):** `095cf48` `research(map): reconstruct Buu layer records`
  (the research result), plus `8abd70a` `docs(tickets): record LOGX layer review
  verdict` (the independent review verdict and correction gate)
- **CANONICAL ROM SHA BEFORE:**
  `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`
- **CANONICAL ROM SHA AFTER:**
  `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`

The isolated worktree was created from the START SHA as a fresh branch. The
retained `logx-map-render-001` branch, the active WORKBENCH-006 worktree, and
stale local state were not used. The ROM was opened read-only; no save, state,
derived ROM, dump, or extracted asset was created, and none is staged.

## External claims tested

The external hypothesis source is `mainant/LOGExtractor` as summarised in the
ticket: two layer forms discriminated by the first word (`0x08008087` as a
chunk-grid layer using `+0x0D`/`+0x11` as X/Y and `+0x14`/`+0x15` as chunk
column/row counts, `0x0800897B` as a single-image layer using `+0x1C` as a
content pointer), plus its admitted coordinate uncertainty. Every one of those
claims was treated as a claim only. No LOGExtractor coordinate conversion was
imported.

## Total layer references, unique records, distinct handlers

| Quantity | Value |
| --- | ---: |
| MapEntries examined | 452 |
| Valid selector-1 roots | 452 |
| **Total layer references** | **1808** |
| Null layer slots | **0** |
| **Unique layer records** | **1464** |
| Shared records | 35 |
| **Distinct `+0x00` words** | **5** |
| Layer pointer range | `0x080707FC`..`0x082B8BC8` |

## Handler census

Unique records (references in brackets):

| `+0x00` | Unique records | References |
| --- | ---: | ---: |
| `0x08008087` | 1420 | 1516 |
| `0x0800897B` | 41 | 41 |
| `0x08007A41` | 1 | 249 |
| `0x08007B63` | 1 | 1 |
| `0x080088BD` | 1 | 1 |

Slot distribution: `+0x14` 349/5/98; `+0x18` 326/1/124 plus `0x08007B63`;
`+0x1C` 415/11/25 plus `0x080088BD`; `+0x20` 426/24/2 (dominant / `0x0800897B` /
`0x08007A41`).

## Layer `+0x00`

**CONFIRMED (physical).** A 4-byte word, odd (Thumb-bit set) and not 4-byte
aligned on all 1464 records, holding a valid Thumb code entry for five distinct
addresses. Three of the five were independently disassembled:

- `0x08008086` = `adds r2,r1,#0` / `adds r1,r0,#0` / `push {r3,lr}` /
  `movs r0,#0` / `bl 0x08007B78` / `pop {r3,pc}`;
- `0x08007A40` = 8-byte allocator through `0x0803D5B8`;
- `0x0800897A` = 12-byte allocator through `0x0803D5B8`.

**PARTIALLY CONFIRMED (semantic).** Calling it a handler. No `bl` caller of
`0x08008086` exists anywhere in the image, so it is reached indirectly at most.
The object built by `0x08007B78` carries an **even data pointer**
(`0x08049410`, from pool `0x08007E68` loaded at `0x08007B92`) at *its* `+0x00`,
one per constructor family (`0x08049548`, `0x080498B0`, `0x08049604`). The
record's odd word and the object's even word are different fields; whether
either encodes a class is **UNRESOLVED**.

**REFUTED.** `+0x00` as a discriminator between layer classes with different
field layouts: the only recovered record reader (`0x08007B78`) is shared by 1516
of 1808 references, and it reads the same record offsets regardless of which
`+0x00` word the record carries.

## Handler `0x08008087`

The dominant entry. `0x08008086` forwards `(r0=NULL, r1=destination,
r2=record)` to the constructor `0x08007B78`, which reads `record+0x14` and
`record+0x15` with two `ldrb`s (`0x08007BDC`/`0x08007BDE`), multiplies them
(`0x08007BE0`), **skips the chunk-install loop entirely** when the product
exceeds four (`cmp r6,#4` / `bgt` at `0x08007BE2`/`0x08007BE4`), indexes the
chunk-pointer window at `record+0x18+4*i` (`lsls r1,r5,#2` at `0x08007BEE`,
load at `0x08007BF2`), and decompresses each non-null pointer through
`0x0803D940` to `object+0x4C+0x800*i`. It also reads `record+0x04`
(`0x08007BBE`, to `object+0x3C`), `record+0x08` (`0x08007BC4`, to
`object+0x40`), the two words at `record+0x0C` and `record+0x10`
(`0x08007BD0`/`0x08007BD4`, to `object+0x44`/`object+0x48`) and
`record+0x16` with `ldrsh` (`0x08007BB6`). The allocation size `0x204C` loaded
at `0x08007B84` equals `4*0x800 + 0x4C`. Semantic classification: **chunk-grid
is CONFIRMED** for the record shape (`y * x_count + x` index at `0x08007C86`),
not inherited from LOGExtractor.

## Handler `0x0800897B`

41 records, each referenced exactly once. Its entry is a 12-byte allocator
wrapper through `0x0803D5B8`, **not** a rendering routine. The class's
`+0x14`/`+0x15` pair is not a usable grid product (29 of 41 have a zero product;
the non-zero ones are 85, 21930, 41382, 43434, 43605) and no record's first
`x*y` window words are all aligned in-ROM pointers. Its `+0x16` is `-1` on 34 of
41. **PARTIALLY CONFIRMED** as a materially different record representation;
**REFUTED** as "`+0x1C` is its content pointer".

## Other handlers

`0x08007A41` is one shared record, `0x080707FC`, referenced 249 times: the
zero-dimension absent-layer placeholder (`+0x14` = `+0x15` = 0, `+0x18` window
entirely null). `0x08007B63` and `0x080088BD` occur once each with the same
four-step verification applied; both are recorded in the provenance and neither
is assigned to a LOGExtractor form.

## Common layer prefix

```text
+0x00  4  odd word, valid Thumb code entry
+0x04  4  scalar word, read at 0x08007BBE, copied to object+0x3C
+0x08  4  scalar word, read at 0x08007BC4, copied to object+0x40
+0x0C  4  word, read whole by `ldm r0!,{r2}` at 0x08007BD0, copied to object+0x44
+          (its low halfword is at +0x0C, its high halfword at +0x0E)
+0x10  4  word, read whole by `ldr r0,[r0]` at 0x08007BD4, copied to object+0x48
+          (its low halfword is at +0x10, its high halfword at +0x12)
+0x14  1  unsigned x grid count (ldrb 0x08007BDC)
+0x15  1  unsigned y grid count (ldrb 0x08007BDE)
+0x16  2  signed halfword (ldrsh 0x08007BB6), 0 on all 1420 dominant records
+0x18  4*N chunk-pointer window, N = +0x14 * +0x15 for the dominant class
```

## `+0x0D`

**REFUTED at the value level** as an X offset. It is 0 on 1458 of 1464 records,
has five distinct values in the whole corpus (0, 4, 32, 40, 249), and is not
among the offsets the one recovered record consumer reads. The instruction-level
absence claim is **withdrawn**: the resynchronising sweep of
`0x08007000..0x08010000` leaves 2,035 undecodable halfwords, contains 13 `ldrsb`
and 58 `ldrsh` sites, and includes 4 load/store sites with immediate offset
`0x0D`, so it cannot support an absence conclusion.

## `+0x11`

**REFUTED at the value level** as a Y offset. It is 0 on 1453 of 1464 records,
has seven distinct values (0, 4, 40, 128, 156, 240, 250), and is not among the
offsets the one recovered record consumer reads. The same sweep reports 30
load/store sites with immediate offset `0x11`, so the instruction-level absence
claim is withdrawn there too. A stronger "no consumer exists" conclusion is
**UNRESOLVED** and would need xref-driven decoding rather than a linear sweep.

## `+0x14`

**CONFIRMED.** One unsigned byte, loaded by `ldrb` at `0x08007BDC` (base
`record+0x14`), used as the horizontal grid bound (`0x08007C66`/`0x08007C70`)
and as the row multiplier in the index `y * x + x` at `0x08007C86`. Range 1..5
on all 1420 dominant-class records; 0 on 29 `0x0800897B` records.

## `+0x15`

**CONFIRMED.** One unsigned byte, loaded by `ldrb` at `0x08007BDE` (`[r0,#1]`,
base `record+0x14`), used as the vertical grid bound (`0x08007C3C`/`0x08007C3E`).
Range 1..5 on all 1420 dominant-class records. Never merged with `+0x14` into a
halfword by any recovered instruction by any recovered consumer.

## `+0x18`

**CONFIRMED (physical).** A direct 4-byte-element pointer array, indexed
`record + 0x18 + 4*i` for `i < +0x14 * +0x15` (`0x08007BEC`..`0x08007C0C`,
load at `0x08007BF2`). Element targets decode to `0x800`-byte screenblock
containers on 1303/1420 dominant records. **PARTIALLY CONFIRMED (semantic):**
117 dominant records carry an internal null before the last expected pointer.
**REFUTED:** any `0x18`-byte element stride for this array. The `0x18`-byte
stride in this project is **CONFIRMED for root `+0x24`/`+0x28`** only; the
MapEntry `+0x18` array uses a 4-byte stride at the site examined, and no layer
record uses one.

## `+0x1C`

**REFUTED** as a general content pointer. For the dominant class `+0x1C` is
word index 1 of the `+0x18` chunk-pointer window, not a separate field. For the
`0x0800897B` class no content pointer at `+0x1C` was recovered. LOGExtractor's
reading is not reproduced for any class.

## Position signedness

| Item | Result |
| --- | --- |
| `+0x16` | **CONFIRMED signed**: `ldrsh r7,[r5,r3]`, `r3=0x16`, at `0x08007BB6` (bytes `1623ef5e`) |
| `+0x0C`..`+0x13` | **UNRESOLVED**: consumed as two 4-byte words (`ldm` at `0x08007BD0`, `ldr` at `0x08007BD4`) and copied to `object+0x44`/`object+0x48`, but nothing recovers a consumer of those object fields, so signedness is not established and a four-halfword reading is not promoted |
| region-wide `ldrsb` census | **not claimed**: 2,035 undecodable halfwords in the swept region make an absence claim unsupportable |
| LOGExtractor negative-coordinate hack | **not reproduced**; no sign correction is asserted |

## Position units

**UNRESOLVED.** No consumer of a layer position was recovered. The only signed
record field with a consumer (`+0x16`) is 0 in all 1420 dominant records, so
even its arithmetic could not be exercised. No unit (pixel, tile, chunk, scroll,
parallax, clip, origin) is claimed.

## Position transform

**UNRESOLVED.** No transform is asserted and none is handed downstream.

## Container organization

Row-major grid of 32x32 screenblock containers: the streaming consumer computes
`chunk_index = y * (record+0x14) + x` at `0x08007C86`, which is the same
`(y & 31) * 32 + (x & 31)` projection the accepted production renderer
implements at `tools/webfoot/map_render.py:322`. **CONFIRMED** for the dominant
class.

## Root slot to BG mapping

"Four root slots hold four non-null layer pointers" is **CONFIRMED** (0 null
slots across 452 roots). "Root slot *n* is BG *n*" remains **PARTIALLY
CONFIRMED**, unchanged from MAP-RENDER: the slot-order correspondence to
`BG0CNT..BG3CNT` byte order at `0x080093E0..0x08009406` is strong but no direct
per-slot register write was recovered. This ticket adds that the engine itself
carries exactly four per-layer slots (`object+0x20+i`, `i < 4`, at
`0x08007CF0`/`0x08007CF4`).

## LOGExtractor chunk-grid interpretation

**CONFIRMED** for `+0x14` (x count), `+0x15` (y count) and `+0x18` (container
pointer array). Independently re-derived from `0x08007BE0`, `0x08007BF2` and
`0x08007C86`, not inherited.

## LOGExtractor single-image interpretation

**PARTIALLY CONFIRMED**, weakly. The `0x0800897B` class is materially different
from `0x08008087` and does not carry the dominant class's chunk-pointer grid,
but nothing recovered shows a single-image representation or a `+0x1C` content
pointer.

## LOGExtractor coordinate logic

**REFUTED** for this image: `+0x0D`/`+0x11` are not X/Y, are almost universally
zero, and have no consumer. No engine-side signed coordinate transform was
found, so none was imported and no constant was introduced to match a
screenshot.

## Full-census results

`python -m tools.research.logx_layer_probe <rom> --references --layers` produced
the tables above. All 1808 references were classified; no reference and no
unique record was skipped. 1463 of 1464 unique records have a non-null `+0x18`
window; the exception is the `0x080707FC` placeholder. A standalone scan of
`0x08100000..0x08400000` found 1439 aligned occurrences of `0x08008087`, of
which 1420 are referenced as a record, leaving **19 dominant-shape records that
no selector-1 root references** (recorded as a handoff).

## Representative layers

| Map | Slot | Record | `+0x00` | `+0x14` | `+0x15` |
| ---: | --- | --- | --- | ---: | ---: |
| 0 | `+0x14` | `0x082B84D0` | `0x08008087` | 3 | 1 |
| 0 | `+0x18` | `0x082B87C4` | `0x08008087` | 2 | 1 |
| 0 | `+0x1C` | `0x082B891C` | `0x08008087` | 3 | 1 |
| 0 | `+0x20` | `0x082B8BC8` | `0x08008087` | 1 | 5 |
| 19 | `+0x14` | `0x0829F6E4` | `0x08008087` | 1 | 1 |
| 19 | `+0x18` | `0x0829F808` | `0x08007B63` | 64 | 192 |
| 19 | `+0x1C` | `0x082ABF00` | `0x080088BD` | 48 | 251 |
| 19 | `+0x20` | `0x080707FC` | `0x08007A41` | 0 | 0 |
| 39 | `+0x14` | `0x080707FC` | `0x08007A41` | 0 | 0 |
| 39 | `+0x18` | `0x08293BEC` | `0x08008087` | 3 | 2 |
| 39 | `+0x1C` | `0x082941CC` | `0x08008087` | 3 | 2 |
| 39 | `+0x20` | `0x08294628` | `0x08008087` | 4 | 2 |
| 40 | `+0x14` | `0x082928C0` | `0x08008087` | 1 | 1 |
| 40 | `+0x18` | `0x08292C88` | `0x08008087` | 2 | 2 |
| 40 | `+0x1C` | `0x08293000` | `0x08008087` | 2 | 2 |
| 40 | `+0x20` | `0x082932D0` | `0x08008087` | 2 | 2 |
| 295 | `+0x14` | `0x081FBD50` | `0x08008087` | 2 | 1 |
| 295 | `+0x20` | `0x081FC540` | `0x08008087` | 1 | 1 |

The 39/40 rows are a direct cross-check against the accepted production
renderer, which measures the same bytes: map 39 logical grids 3x2, 3x2, 4x2 and
map 40 1x1, 2x2, 2x2, 2x2.

Also inspected: the shared groups (`0x0822C870`/`0x0822CA1C`/`0x0822CB48`
referenced by ten maps each; `0x0829C0A8`/`0x0829C204`/`0x0829C258` by five),
one-slot-only layers, `0x080707FC` null-container cases, the maximum observed
grid product (20 on `0x0826A1CC`) and the minimum non-zero dimensions (1x1).

## Anomalies

| Anomaly | Count |
| --- | ---: |
| `+0x18` window has an internal null within the first `x*y` words | 117 dominant (127 corpus-wide) |
| `+0x18` window word 0 is null (all records) | 52 |
| `+0x18` window word non-null but not aligned in-ROM | 13 |
| `+0x18` window entirely null | 1 (`0x080707FC`) |
| First window word's header `+0x04` != `0x800` | 1 (`0x082ABF00`) |
| Grid product zero (one dimension byte zero) | 30 (29 in `0x0800897B`, 1 placeholder) |
| `+0x0E` non-zero | 107 |
| `+0x12` non-zero | 63 |
| `+0x16` non-zero | 36 (34 of them `-1`, all `0x0800897B`) |
| Dominant record with `+0x04` != `0x400` | 52 of 1420 |
| Dominant record with `+0x04` == 0 | 16 of 1420 |
| Record with exactly one dimension byte zero | 29 (all `0x0800897B`) |
| Dominant-shape records no root references | 19 |
| Grid product above the constructor's four-slot cap | 133 (dominant class up to 20) |

The `+0x18` window is inspected for its first 16 words; a record whose `x*y`
product exceeds 16 is judged on a truncated window (one product-20 dominant
record and the two large singletons).

The four-slot skip versus products above four is the ticket's sharpest open
question and is stated as **UNRESOLVED** in the provenance.

## Tooling added

- `tools/research/logx_layer_probe.py` - SHA-256-gated, read-only, deterministic
  census. Reuses the accepted selector-1 root rule; enumerates all 1808
  references and all 1464 unique records; classifies each `+0x00` word;
  reports raw fields at engine access widths; supports `--references`,
  `--layers` and `--csv`.
- `tools/research/thumb_disasm.py` - resynchronising disassembly helpers that
  never treat an empty linear sweep as absence: single-pass sweep with an
  undecodable-halfword census, exact Thumb BL target decoding, whole-image
  `bl`-caller scan, exact word-reference scan, Thumb prologue discovery.

## Tests added

`tests/integration/test_logx_layer_rom.py`, 32 ROM-gated tests. They skip
cleanly when `LOGX_CANONICAL_ROM` / the default ROM path is unavailable, never
write to the ROM, and assert only independently established facts:

- 452 roots, 1808 references, zero null slots, 1464 unique, 35 shared;
- layer pointer min/max and every slot target aligned in-ROM;
- handler census (5 values, both unique-record and reference counts);
- every `+0x00` word odd and not 4-byte aligned;
- representative records and representative root slot targets;
- the raw instruction bytes for the two `ldrb`s, the `muls`, the `+0x18`
  indexing sequence, and the `ldrsh` at `0x08007BB6`;
- dominant-class grid bytes never zero and products <= 20;
- 1303 clean vs 117 internal-null `+0x18` windows, and no all-null dominant
  window;
- the absent-layer placeholder is the only entirely null window and is shared
  249 times;
- the standalone scan finds 19 unreferenced dominant-shape records;
- the `0x0800897B` class does not use the dominant grid reading;
- the probe refuses a non-canonical image and its documented invocation leaves
  the input byte-identical.

## Test results

Measured in this worktree with `LOGX_CANONICAL_ROM` and `WEBFOOT_BUU_ROM` set to
the canonical ROM:

- `tests/integration/test_logx_layer_rom.py`: **32 passed** (3.4 s).
- `test_logx_map_render_rom.py`: **12 passed**; `test_logx_map_record_rom.py`:
  **4 passed**; the three LOGX files together: **48 passed, 0 skipped**.
- `tests/integration/test_map_render_rom.py` (the accepted production renderer):
  **3 passed, 2 skipped** (the file collects 5 tests; the skips are the VRAM
  oracle inputs). All four files together: **51 passed, 2 skipped**.
- With the ROM unavailable (env pointed at a nonexistent path) the suite skips
  cleanly with no failures: the layer file alone gives **2 passed, 30 skipped,
  0 failed**, and across all four files the independent reviewer measured
  **4 passed, 49 skipped, 0 failed**. The two tests that still pass are the ones
  that need no ROM (the non-canonical-image refusal and the rejection of a
  short image).

The record-shape findings this ticket documents therefore do not disturb the
accepted production renderer.

Private-runtime validation: none performed; this ticket is static-only and made
no mGBA capture.

## ROM_BIBLE_IMPACT

`docs/reverse-engineering.md` gains a "LOGX-LAYER-001 layer records" section
stating physical facts only: reference and unique-record counts, the
`+0x14`/`+0x15` separate-byte reading, the `+0x18` window and its index formula,
the `ldrsh` at `+0x16`, the five-value `+0x00` vocabulary, and the explicit
statement that layer positioning is UNRESOLVED. Speculative semantic names are
not promoted.

## public progress impact

**NONE.** The ticket is research-only and produces no new shipping capability:
no parser, editor, or rendering behavior changes, and no public capability or
frontier moves.

## Disagreements with LOGExtractor

- `+0x0D` and `+0x11` are **not** X/Y offsets in this image (REFUTED).
- `+0x1C` is **not** a content pointer for any recovered class (REFUTED).
- The "two layer forms discriminated by the first word" model is **replaced** by
  "five constructor/allocator entries over one shared record shape, with two
  dominant representations".
- LOGExtractor's admitted negative-coordinate handling is **not** reproduced;
  no sign correction is imported.

## Unresolved questions

1. What consumes `+0x0C`, `+0x0E`, `+0x10`, `+0x12`? Signedness, units, origin
   and any X/Y pairing are all open.
2. What consumes `object+0x0C` (the copied `record+0x16`)?
3. The four-slot install cap (`cmp r6,#4`) versus 133 records with products
   above four.
4. Whether the engine ever branches through a record's `+0x00`.
5. Full semantics of the `0x08007B63` and `0x080088BD` singletons.
6. Whether the `0x0800897B` class is a layer at all.
7. Which selector reaches the 19 unreferenced dominant-shape records.
8. Why ten maps share one three-layer stack.
9. Meaning of `+0x04`/`+0x08`.
10. Whether an internal null chunk pointer means "skip" or "default".

## Handoff to LOGX-TILE-001

Layer record -> container: `record + 0x18 + 4*i` for `i < record[+0x14] *
record[+0x15]`; `record[+0x14]` is the x count and `record[+0x15]` the y count;
each container decodes to `0x800` bytes = 1024 little-endian u16 screen entries
through `0x0803D940` (`0x08007BFE`, `0x08007C04`). The tile-level bitfields live
in that payload and are LOGX-TILE-001's scope; this ticket does not decode them.

## Handoff to other LOGX tickets

- **LOGX-CODEC-001:** the chunk decompressor call sites and destination layout
  (`object+0x4C+0x800*i`), plus the allocator entry `0x0803D5B8`.
- **LOGX-CONNECTOR-001:** the 0x18-byte element stride belongs to root
  `+0x24`/`+0x28` and MapEntry `+0x18`, **not** to layer records.
- **LOGX-MAP-RENDER successor / any position consumer:** layer positioning is
  UNRESOLVED; do not import LOGExtractor's transform.

## Independent review

**Verdict: APPROVE WITH REQUIRED CORRECTIONS.** A fresh-context reviewer with no
knowledge of this ticket independently re-derived the MapEntry table, the
selector-1 route, the entire census, the instruction bytes, the string
dissassembly of the constructor and consumer, the literal pools, the whole-image
`bl`-caller scan, the resynchronising sweep, the byte-field census, the window
classification, the standalone scan, the representative records and the test
results. It reproduced every headline census number exactly (452 / 452 / 1808 /
0 / 1464 / 35, all five `+0x00` counts, the slot distributions, the pointer
range, the byte-field table, the anomaly counts, 1303 + 117 = 1420, and the 19
unreferenced records) and confirmed the canonical ROM SHA-256 was unchanged.

It then found **13 required corrections**, all of which this ticket verified
independently and applied. The four material ones were:

1. the claim that the constructor writes `0x08008087` into its object was false
   - the pool at `0x08007E68` holds `0x08049410`, an even data pointer, and the
   claim was the sole support for the "entry-word, not a type tag" argument;
2. the `+0x0D`/`+0x11`/`ldrsb` absence claims rested on a sweep whose real
   undecodable count is 2,035, not 18 - i.e. the sweep covered about 1% of the
   documented range - and the region does contain `ldrsb`, `ldrsh` and
   offset-`0x0D`/`0x11` sites;
3. `+0x0C`..`+0x13` **are** consumed, as two 4-byte words copied to
   `object+0x44`/`object+0x48`, so the "no recovered consumer" premise was wrong
   even though the positioning conclusion survives;
4. several descriptive statistics were mis-measured (`+0x04` histogram,
   `+0x04 != 0x400` count, partial-zero record count, the "78" internal-null
   figure, the `-1` count, the unreferenced-record examples, one literal pool
   address, the instruction range for the `+0x04`/`+0x08` copies, and the test
   totals).

Every correction was re-verified against the ROM before it was applied, and the
documents now state the measured values. The review's non-blocking notes (the
unstated 16-word window bound, the "installs at most four" wording, and the
`0x08007E70` pool description) were also applied.

## Required corrections

| # | Correction | Status |
| ---: | --- | --- |
| 1 | Constructor/target pool: object `+0x00` is `0x08049410` (pool `0x08007E68`), not `0x08008087`; restate 4.2 without the inverted argument | APPLIED and re-verified |
| 2 | Withdraw the `+0x0D`/`+0x11`/`ldrsb` absence claims; report the real sweep numbers (16,397 decoded, 2,035 undecodable, 13 `ldrsb`, 58 `ldrsh`, 4 offset-`0x0D`, 30 offset-`0x11`) | APPLIED and re-verified |
| 3 | `+0x0C`..`+0x13` are read as two words at `0x08007BD0`/`0x08007BD4` and copied to `object+0x44`/`+0x48`; remove "no recovered consumer" | APPLIED and re-verified |
| 4 | `+0x04`/`+0x08` copy destination is `object+0x3C`/`+0x40` at `0x08007BBE`..`0x08007BC8` | APPLIED and re-verified |
| 5 | The `+0x18` null-substitution literal is pool `0x08007E6C` = `0x08070808` | APPLIED and re-verified |
| 6 | `+0x04` histogram corrected (`0x400` x1368, `0` x16, `0x133` x12, ...); `+0x04 != 0x400` is 52 dominant / 70 corpus | APPLIED and re-verified |
| 7 | Partial-zero dimension records: 29, not five | APPLIED and re-verified |
| 8 | Section 9's internal-null count: 117 dominant / 127 corpus, not 78 | APPLIED and re-verified |
| 9 | `0x0800897B` `+0x16 == -1` on 34, not 26 | APPLIED and re-verified |
| 10 | Replace the unreferenced-record example list with the 19 measured addresses; drop the false "below the referenced range" claim | APPLIED and re-verified |
| 11 | `0x080088BC` includes `bl 0x080080C0`; drop "constant-return stub" | APPLIED and re-verified |
| 12 | Replace the test totals with the observed ones (32; 48/0; 3 passed + 2 skipped of 5 collected; 51 passed + 2 skipped; skip scenario 2 passed / 30 skipped for the layer file, 4 / 49 across all four) | APPLIED and re-verified |
| 13 | Scope the `0x18`-byte stride claim to root `+0x24`/`+0x28`; the cited MapEntry site is a 4-byte stride | APPLIED and re-verified |

## Correction gate

Closed. All 13 required corrections were verified against the ROM by this
ticket after the review reported, the documents and the ROM bible were updated,
and the focused suites were re-run: `tests/integration/test_logx_layer_rom.py`
**32 passed**; the three LOGX files **48 passed**; all four files plus
`test_map_render_rom.py` **51 passed, 2 skipped**. The canonical ROM SHA-256 was
re-verified as unchanged after the corrections.

## Git status

The isolated worktree's change set is **5 new files plus one edited file**:

```text
 M docs/reverse-engineering.md
?? docs/research/LOGX_LAYER_PROVENANCE.md
?? docs/research/LOGX-LAYER-001-review.md
?? tests/integration/test_logx_layer_rom.py
?? tools/research/logx_layer_probe.py
?? tools/research/thumb_disasm.py
```

The worktree otherwise reports a large number of modified paths that are pure
CRLF/EOL noise from checkout, not content changes: `git diff
--ignore-cr-at-eol --stat` leaves only `docs/reverse-engineering.md`. Because of
that noise a whole-tree `git diff --check` is not a usable gate here; the scoped
check is clean:

```text
git diff --check -- docs/reverse-engineering.md   -> exit 0
```

None of the five new files contains trailing whitespace or tabs, and every new
file is written with LF that Git normalises on commit.

No ROM, save, state, dump, generated commercial asset, or `extern/` checkout is
staged or untracked in the worktree; the canonical ROM lives outside it and
outside the repository tree.

Commit SHA(s): `095cf48` `research(map): reconstruct Buu layer records`, plus
`8abd70a` `docs(tickets): record LOGX layer review verdict` recording the
independent review verdict and the correction gate. The branch head after those
two is one commit further, since this text records their SHAs.
