# ROM-CAPACITY-AND-ALLOCATION-001 - Phase A: measured capacity of canonical Buu

**Checkpoint A of ROM-CAPACITY-AND-ALLOCATION-001.** This document establishes the
factual capacity picture before any allocator policy is frozen. Phases B, C and D
(the Gate-B safety slices, the production allocator and the real above-8-MiB
allocation proof) are **not** part of this checkpoint and are not claimed here.

## 0. Baseline, identity, and what this does not establish

| Item | Value |
|---|---|
| Repository authority | `origin/master` |
| Baseline SHA | `a commit since folded into its successor` |
| Canonical ROM | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| Canonical size | 8,388,608 bytes = 0x00800000 = 8 MiB |

`docs/PROJECT_STATE.md` and earlier records show that TOOLKIT-011 refused the whole
upstream tail and TOOLKIT-028 verified one 256-byte carve of it. This checkpoint
does **not** revisit, weaken or widen those decisions. It measures the image, and
it reports candidate capacity separately from declared capacity at every point.

Nothing here promotes a byte, writes a ROM, or changes a profile. The production
free-space declaration is still exactly one region, `[0x007EA400, 0x007EA500)`,
declared `CONFIRMED` by TOOLKIT-028.

---

## 1. Occupancy model

### 1.1 Method

`tools/research/capacity_model.py` (new, research-only, unreachable from the
production allocation path) builds one exhaustive, disjoint partition of the
canonical image:

| Class | Meaning |
|---|---|
| `OWNED` | inside a measured structure/resource extent |
| `REFERENCED` | a known reference target with no covering structure |
| `VERIFIED_FREE` | declared free in the profile (reviewed evidence only) |
| `UNKNOWN` | neither proven occupied nor proven free |

The annotation and reference base is `tools/research/free_space_audit.build_model`
verbatim - the model that produced TOOLKIT-011's positives - so this model's
negatives are directly comparable with them. Three domains that audit did not
carry are appended from their own production readers, because leaving them out
would advertise bytes a production loader already reads as `UNKNOWN`:

1. **script corpora** - each declared family's record table and pool
   (`profile.tables.scripts`);
2. **compressed dialogue** - the seven-word selector table at `0x7B5B64`
   (`docs/research/LOGX_SYNTHESIS_PROVENANCE.md:263`) and each container's
   measured packed extent (`formats.webfoot_lz.Container.packed_size`);
3. **placement-type dispatch table** - `table + 28 * selector` over the
   TOOLKIT-009 measured selector bound.

A generated expanded image is **not** part of this partition. Expansion is a
write-time policy (`profile.generated_expansion`), not canonical occupancy, and
conflating the two is exactly the error this census names.

### 1.2 Measured accounting

| Classification | Bytes | Percent |
|---|---:|---:|
| `OWNED` | 3,037,940 | 36.2151% |
| `REFERENCED` | 87 | 0.0010% |
| `VERIFIED_FREE` | 256 | 0.0031% |
| `UNKNOWN` | 5,350,325 | 63.7808% |
| **total** | **8,388,608** | **100%** |

The partition is **27,323** machine-readable spans
(`build/capacity-a/region_map.jsonl`), attributed by 10,251 measurement
annotations, each carrying `start`, `end`, `length`, `classification`,
`confidence`, `evidence`, `owner` and `kind`, so the allocator can query it
instead of scraping prose. Spans are split at every evidence boundary - an
annotation's start or end, a free declaration's boundary, a reference target -
not merely where the classification changes, so the map carries **all 10,177
distinct owners** the model knows rather than coalescing them by class. Identical
inputs produce identical bytes.

For orientation on the fill/absence distinction the whole census turns on: the
canonical image holds **340,319** `0xFF` bytes and **812,561** zero bytes - and
only **256** of those are proven free.

`REFERENCED` is tiny (87 bytes) for a reason worth stating: almost every known
reference target already lies inside a modelled structure, so it is `OWNED`. The
more informative figure is its complement - see below.

### 1.3 Reconciliation with TOOLKIT-011's number

TOOLKIT-011 measured **5,199,061** bytes with no known annotation, on 16,977
references and 9,598 annotations (`FREE_SPACE_RELOCATION.md:113-117`). This model
measures **5,350,325** `UNKNOWN` on 19,727 references and 10,251 annotations.

The +151,264-byte delta has **three** components, and only the first two are
measured directly here:

| Component | Basis |
|---|---|
| The 292,440-byte candidate tail | TOOLKIT-011 counted it as an *annotation* (`candidate_tail`, status `CANDIDATE`) and therefore outside its `UNKNOWN`. This model refuses to count a candidate as ownership, so the tail is `UNKNOWN` here - which is what "candidate" means. |
| Three domains this model adds | script tables/pools, the compressed-dialogue selector table and containers, the placement-type dispatch table: **13 annotations and 7 references**, all counted. |
| Growth of the **shared base model** itself | `free_space_audit.build_model` is not the same model TOOLKIT-011 ran against: it now yields ~19,720 references and ~10,238 annotations, against TOOLKIT-011's 16,977 and 9,598. This component is **`INFERRED`**: the current counts are measured, the historical counts are read from the earlier record, and the subtraction is arithmetic, not a re-run of the old code. |

The labelled split of the delta is therefore `INFERRED`; the two endpoint figures
are `CONFIRMED`. The direction is the honest one: this model **owns less than
TOOLKIT-011's** on the same bytes, and it says so.

### 1.4 The ownership gap the model exposes

| Measure | Value |
|---|---:|
| Known references in the production graph | 19,727 |
| Distinct reference targets | 11,483 |
| Reference **sources not inside any owned extent** | **11,005** |

Over half of the production reference graph's *source fields* - animation
pointers, frame pointers, piece container pointers, script slots and similar -
sit in bytes no annotation covers. Those bytes are therefore `UNKNOWN` in the
partition even though the project knows the engine reads them.

This is a **measured limitation, not a defect to fix here**: it is why `UNKNOWN`
must never be allocatable, and why a raw "60% of the ROM is unclassified"
reading would be dangerously wrong.

---

## 2. Free regions, geometry and fragmentation

### 2.1 Declared free space (the only genuinely allocatable canonical bytes)

| Measure | Value |
|---|---:|
| Regions | 1 |
| Total | 256 bytes |
| Largest | 256 bytes |
| Median | 256 bytes |
| Usable at alignment 4 | 256 |
| Usable as >= 32-byte blocks | 256 |
| Usable as >= 256-byte blocks | 256 |
| Usable as >= 1024-byte blocks | 0 |

Fragmentation is not a factor at this size: the single declared region is
contiguous and already aligned. `0x7EA400` is 1,024-aligned (it is not 2,048-aligned, a figure inherited from the TOOLKIT-028 record).

The model also asserts the **absence of a conflict**: no declared free byte is
covered by any annotation. A free declaration landing on content would be
reported in `free_region_conflicts` rather than silently outranking it, and
`require_consistent` - which the `audit` entry point applies - **fails closed** on
such a model, because every capacity figure derived from it would be wrong in the
unsafe direction. That list is empty for the canonical image.

### 2.2 Candidate windows: a census, not a declaration

Phase A must distinguish "free" from "looks like fill". The census
therefore runs the **same checks TOOLKIT-028's verifier runs** over the *whole
image* rather than one 292 KB tail:

* every byte of a window must be the `FF` fill;
* no `OWNED` byte, no known inbound reference;
* no candidate target at **any byte alignment**, interior bytes included;
* no candidate source starting inside it;
* a stated clearance margin from the nearest candidate target on each side.

The whole-image pointer sweep finds **140,259** pointer-shaped words (94,648 with
word-aligned sources) addressing **89,516** distinct target bytes and starting at
140,259 distinct source positions. TOOLKIT-011 found 516 of them inside the tail,
and the same procedure restricted to the tail reproduces 516 observations / 475
distinct targets exactly - which is what makes the wider scan a superset rather
than a new method.

**Result at the reviewed 1,024-byte margin: 115 runs, 23,595 bytes.**

| Minimum block size (alignment 4) | Bytes |
|---|---:|
| raw | 23,595 |
| squared to alignment 4 | 23,456 |
| >= 32-byte blocks | 23,136 |
| >= 256-byte blocks | 19,712 |
| >= 1,024-byte blocks | 8,192 |

89 of the 115 runs are under 32 bytes, so the practical figure is the
block-quantised one, not the raw total.

Every one of the 115 runs was re-verified against
`capacity_proof.verify_window` with this model's real annotations and references:
**115 verified, 0 rejected**. That check is run over *every* run rather than the
largest, because the largest is not representative - an earlier draft of this
model checked only the largest and silently omitted the candidate-source term,
which the largest run happened not to exercise.

### 2.3 The margin, not the candidates, is what most of the tail fails

| Margin | Promotable bytes | Runs |
|---:|---:|---:|
| 0 | 336,135 | 35,729 |
| 256 | 143,346 | 4,750 |
| 512 | 72,223 | 1,185 |
| **1,024 (reviewed policy)** | **23,595** | **115** |
| 2,048 | 781 | 2 |
| 4,096 | 0 | 0 |

With 475 candidate targets spread through 292,440 bytes of tail, the average gap
is ~614 bytes - under twice the margin - so most intervals contribute nothing.
The margin is a **policy** number: it exists because a candidate that *is* real
means a structure begins there with unknown length. The curve is reported so this
number is not mistaken for a property of the ROM.

### 2.4 Independent agreement with the reviewed verifier

The largest census run, `[0x7FB408, 0x7FBC60)` (2,136 bytes), was handed to
`tools/research/capacity_proof.verify_window` with this model's real annotations
and references. Verdict: **`VERIFIED`**, no failed checks. The declared
TOOLKIT-028 window `[0x7EA400, 0x7EA500)` re-verifies unchanged, and its four
positive controls - the declared header, the largest declared table, the
most-referenced target in the graph, and a candidate observation inside the same
`FF` tail - are all rejected, each on the check it exists to exercise. That is not
inherited on trust: `tests/integration/test_capacity_proof_rom.py` is the standing
regression that re-runs exactly that measurement against the canonical image, and
it passes on this candidate.

The census also reproduces TOOLKIT-028's geometry. TOOLKIT-028 records the
largest candidate-free interval as `[0x7E9D4C, 0x7EB000)`, 4,788 bytes
(`BUU_VERIFIED_CAPACITY.md:73`), and records the nearest candidate **target**
below its window at `0x7E9D4B`, a clearance of 1,717 bytes (`:92`). The census
measures clearance from that target *byte*, so its margin-adjusted interval is
`[0x7E9D4B + 1024, 0x7EB000 - 1024)` = `[0x7EA14B, 0x7EAC00)`, 2,741 bytes:

```text
[0x7EA14B, 0x7EA400)   693 bytes   (promotable)
[0x7EA400, 0x7EA500)   256 bytes   (already declared free)
[0x7EA500, 0x7EAC00)  1792 bytes   (promotable)
                                    693 + 256 + 1792 = 2741
```

The one-byte difference from `4,788 - 2 x 1,024 = 2,740` is the boundary
convention, not a disagreement: TOOLKIT-028 names the interval by its first *free*
byte `0x7E9D4C`, while the census clips from the target byte `0x7E9D4B` one below
it. Stated on the same boundary the two agree: the census finds precisely the two
promotable runs either side of the already-declared window, and nothing else in
that interval. Two independent procedures, written for different purposes, agree
on the same bytes.

**Every census run was re-verified, not just the largest.** That distinction is
load-bearing: an earlier draft of this model verified only the largest run and
silently omitted the candidate-source check, and the largest run happened to be
clean while a one-byte run elsewhere was not. See §2.2, which states the corrected
figures.

---

## 3. ROM expansion: reconfirming the existing proof

### 3.1 What was actually proven (not restated, read)

`docs/research/ROM_EXPANSION.md` records the experiment and its outcome.

| What the proof establishes | Value |
|---|---|
| Generated image size | 16 MiB (`0x01000000`) |
| Placement address | file `0x00800000` = ROM address `0x08800000` |
| Pointer encoding | absolute GBA u32 LE in selector 1's word at file `0x007B5B68` |
| Engine path | retail consumer at `0x08012240` read packed handle `0x02002641`, selector 1, and `0x08800000` |
| Runtime observation | deterministic-fixture snapshot shows `Nice work, Goku!` in the normal retail dialogue box |
| Output hash | `3ccbef45940e8f5c27d3f88839639eb04d9cc50f8d942f18bc850872628724cb` |
| Rebuild | production build path regenerated a byte-identical image |
| Evidence level | **CONFIRMED / LEVEL 4** |
| Base image | exactly the canonical SHA above |

`ROM_EXPAND-001-COMPLETE.md:177-179` states the runtime proof rests on the
committed capture rather than a fresh run. That limitation is inherited here
unchanged and is not upgraded.

### 3.2 Classification of the existing proof

**Sufficient, for exactly one domain.** It proves that a *compressed-dialogue
selector-table entry* can address a container above canonical EOF and that the
retail engine dereferences it. It does **not** prove that any other pointer
family can, and it does not prove a 16 MiB image is safe in general - only that a
16 MiB generated image with this one relocated container was consumed correctly.

No further experiment was required for this checkpoint, so none was run. The
proof is reused, and its scope is narrowed in the addressability matrix below
rather than widened.

### 3.3 Raw storage ceiling: four separate numbers

These must not be conflated. They are not.

| | Quantity | Value | Basis |
|---|---|---|---|
| **A** | Canonical retail image size | 8,388,608 bytes (8 MiB) | measured identity |
| **B** | Platform-visible nominal ROM window | 32 MiB (`0x08000000..0x09FFFFFF`) | **PLATFORM / external** (GBATEK, cited in `ROM_EXPANSION.md:12-19`); not a project measurement |
| **C** | Maximum size the engine actually handles | **16 MiB, proven for one domain**; above that `UNKNOWN` | LEVEL 4 runtime, `ROM_EXPANSION.md:24-46` |
| **D** | Maximum size our writer/build pipeline safely emits | profile `generated_expansion.output_size`, capped at 32 MiB and required to be a power of two (`profile.py:782-788`) | validated contract; byte-identical rebuild proven at 16 MiB |

**B is not evidence for C.** The 32 MiB figure is a documented platform window.
Nothing in this repository shows this engine using a byte above `0x08FFFFFF`, and
real cartridge/flash hardware remains untested (`ROM_EXPANSION.md:21-22`).

**RAW EXTRA ADDRESSABLE BYTES:** 8,388,608 (the 16 MiB proven image minus the
8 MiB canonical image), of which only allocator-authorized spans are writable
(`write.py:551-558`). The remaining nominal 16 MiB up to B is **unproven**.

---

## 4. Addressability matrix

Two ranges must be kept apart throughout: what the *toolkit* accepts, and what
the *engine* is proven to accept.

* **ENGINE-PROVEN above canonical EOF: exactly one domain.** Compressed-dialogue
  selector-table entries, `0x08800000`, CONFIRMED / LEVEL 4.
* **TOOLKIT-SIDE nominal 32 MiB window (`base + 0x02000000`): exactly one
  production occurrence**, `tools/webfoot/formats/map_placements.py:166`, bounding
  one field (`descriptor_pointer_raw`). Every other production read path bounds
  against the **actual image length**, so they would admit an expanded image
  unchanged: `binary.py:46-57`, `graphics.py:755-759`,
  `formats/map_graphics.py:403-422`, `map_render.py:245-252`,
  `formats/map_slots.py:160-164`, `maps.py:312`, `formats/text_tables.py:273`,
  `formats/ascii_text_tables.py:178`, `scripts.py:156`, `stats.py:163-165`.

The 32-bit-looking fields therefore do **not** behave identically. Five distinct
encodings are in play.

| # | Domain | Pointer format | W | Align | Engine limit | Level | Above 8 MiB? | Evidence |
|---|---|---|---:|---:|---|---|---|---|
| 1 | Generic ROM pointers | absolute GBA u32 LE | 4 | none in helper | `UNKNOWN` | CONFIRMED (representation only) | **NO** | `binary.py:8,22-25,46-57` |
| 2 | **Compressed-dialogue selector table** | absolute GBA u32 LE, `0x7B5B64 + selector*4` | 4 | 4 | **`0x08800000` PROVEN** | **CONFIRMED / LEVEL 4** | **YES** | `compressed_dialogue.py:68-77,142-156`; `ROM_EXPANSION.md:24-46` |
| 3 | MapEntry `+0x14` scripts pointer | absolute GBA u32 LE | 4 | 4 | `UNKNOWN` | CONFIRMED (encoding) | NO | `BUU_PLACEMENT_RUN_RELOCATION.md:70-71`; `entities.py:184,213` |
| 4 | MapEntry `+0x2C` scene selector array | **base of a u32 selector array**; descriptor = `base + 4*(selector-1)` | 4 | 4 | `UNKNOWN`; resolution CONFIRMED L3 | CONFIRMED (L3) | NO | `atlas_producers/seed.py:201-202`; `map_render.py:327-332` |
| 5 | MapEntry `+0x10/+0x18/+0x1C/+0x20/+0x28/+0x30/+0x34` | absolute GBA u32 LE (shape only) | 4 | 4 | `UNKNOWN` | DISCOVERED, not decoded | NO | `formats/map_entry.py:74-83`; `MAP_FORMAT.md:184-187` |
| 6 | Placement run (object array) | array of absolute u32 LE; exactly `count*4`, no sentinel | 4/slot | 4 | count bound proven; range `UNKNOWN` | CONFIRMED (traversal) | NO | `BUU_PLACEMENT_RUN_RELOCATION.md:96-142`; `entities.py:211-212` |
| 7 | 8-byte slot arrays (`+0x10`) | slot = two u32 LE | 4 | 4 | `UNKNOWN` | round-trip only; typed rung is a heuristic | NO | `formats/map_slots.py:69-71,153-164` |
| 8 | Placement / descriptor records | u32 LE words; `child_count` 1..4 (corpus bound) | 4 | 4 | `UNKNOWN` | CONFIRMED (shape) | NO | `formats/map_placements.py:1-8,83-131,166` |
| 9 | Text pointer table + pool | absolute LE GBA addresses, table of 1,534 | 4 | pool 2 | `UNKNOWN` | CONFIRMED (round-trip) | NO | `formats/text_tables.py:66,260-278`; `TEXT_FORMAT.md:79-101` |
| 10 | Script record slots + bodies | absolute u32 LE in the record slot; body offset is pool-relative | 4 | 4 | `UNKNOWN` | CONFIRMED (round-trip) | NO | `scripts.py:144-175`; `BUU_SCRIPT_VM.md:97-103` |
| 11 | Actor sprite chain | character table -> structure -> animation -> frame -> piece -> container, all absolute u32 LE | 4 | 4 on the table | `UNKNOWN` | CONFIRMED (round-trip) | NO | `formats/sprite_graphics.py:460-465,550-591`; `graphics.py:755-759` |
| 12 | Map scene descriptor + graphics | absolute u32 LE at fixed descriptor offsets; banks `. +0x4C` | 4 | 4 | `UNKNOWN` | CONFIRMED (static; render proven on maps 39/40) | NO | `formats/map_graphics.py:182-211,403-422` |
| 13 | Palettes | **no indirection**: fixed absolute address, entry is the literal colour | 2 | 2 | `UNKNOWN` | CONFIRMED | NO | `graphics.py:487-506`; `config/roms.yaml:19-20` |
| 14 | Stat tables + placement-type selector | fixed table + stride; selector is an **index**, not a pointer | 4 idx | - | `UNKNOWN` above canonical; profile gate at canonical size | CONFIRMED static / L2 | NO | `formats/stat_tables.py:53-78`; `profile.py:622-623` |
| 15 | Relocation / indirect families | `ABSOLUTE_ROM_U32_LE` (only real user), `RELATIVE_I32_LE` (**no ROM domain uses it**), `INDEX_U32_LE`, `INDEX_U8` | 4/1 | - | - | CONFIRMED | n/a | `layout.py:120-158,188-196` |
| 16 | Packed text handle | 32-bit: selector 0-5, decoded start 6-20, length 21-31 | 4 | - | **encodes no ROM address** by design | CONFIRMED | address-independent (proven); not itself a >8 MiB address carrier | `handles.py:17-31`; `ROM_EXPANSION.md:36-39` |

**Thirteen of the sixteen domains above have unproven expansion** (rows 1 and 3-14;
row 15 is format-neutral and row 16 is proven address-*independent* rather than
address-capable). The one proven domain is proven because a relocation experiment
dereferenced it at runtime, not because its field is 32 bits wide.

### 4.1 Fail-closed consequence for allocation (Phase B input, not a decision)

For every domain whose expansion is `UNKNOWN`, an allocator or its caller must
**refuse** to place that class above canonical EOF unless a separate bounded
proof exists. Placing globally and hoping each consumer accepts the address is
exactly what the policy forbids. Encoding that per-domain constraint is Phase B
work; this section is its evidence base.

---

## 5. Engine / table / ID ceilings

Byte capacity and **number-of-objects capacity** are different quantities, and
for several subsystems the object ceiling binds first. Retail use is measured;
"engine-verified" means a document or disassembly records the bound.

| Space | Retail use | Encoded max | Engine-verified max | What breaks first | Relocatable? |
|---|---|---|---:|---|---|
| MapEntry table | 452 records (stride 0x38) | none (no count field; length is a code constant) | **452** (`0x080125E0` returns `0x1C4`) | the engine count constant; a 453rd record is never scanned | base literal at one code site; kind not relocation-eligible |
| MapEntry `+0x04` object count | 0..51 measured, 316/452 non-zero, 1,898 slots | **255** (u8, `ldrb`) | counted loop, no upper compare | the count byte at 255 **and** the `+0x14` array | **yes, bounded**: `placement_reference_array` is eligible |
| MapEntry `+0x05` script count | 0..19 measured | 255 (u8) | `ldrb`-guarded loop over `+0x18` | the count byte | no |
| MapEntry `+0x06/+0x07/+0x08` | small | 255 (u8) | **`UNKNOWN`** - no consumer found | nothing known | no statement |
| Map lookup key | 452 unique keys, `0x0001..0x1601` | 2 bytes (two separate `ldrb`+`cmp`) | table bound 452 | key width or the 452-row bound | no |
| Placement-type selectors | 101 distinct; max 149 | u32 field, ROM-bounded | **141** (`enemy_stats` extent); 149 is an observed bound, **not** a table count | the 141-record extent: selectors >=141 have no record codec | read-only; refuses reassignment |
| `character_base_stats` | 9 x 0x12 | none (fixed array) | `UNKNOWN` | toolkit-side count only | no |
| Actor sprite definitions | 297 (ids 10..306) | sprite-id read with `ldr` (u32) | **none** - no compare against 297 or 307 anywhere | the table length; the next word is an IWRAM address | not eligible; no statement |
| Animation slots per definition | 1..23 per definition; 4,070 slots, 1,721 non-null | 255 (u8 count at `+0x00`) | count-guarded at five sites (7/8/7/1/6) | the count byte | no |
| Text pointer table | 1,534 x 4 | index widths vary: **u16** at item records, u16 at MapEntry `+0x0C`/appearance records, varint at slot 178 | **none found** | the table length; the pool has **zero slack** | bodies **per entry**; the table has no growth path (51 code refs) |
| Scripts `static40` | 40 records, 120 roots, 548 B pool | no count field | **40** (`cmp r6,#0x28`) | the walker immediate - retail is exactly at the bound | no |
| Scripts `item_use` | 83 records; 23 own a script; 703 B pool | no count field | `UNKNOWN` (12 sites compute `table + 52*i`, no compare) | in-image: the next container header at `0x3BE3D4` | no |
| Event-resource table | 522 x 4; 127,328 B pool | index is a varint (no fixed width) | **522** (three ways) | the table extent | no |
| Compressed-dialogue selectors | **7** (6 x ~65 KB + 1 x 436 B) | selector field is 6 bits -> 63 | **7** - documented structural gate, "must NOT be widened" | the 7-entry table | payload relocatable; table widening refused |
| Appearances | 232 x 0x10 | u16 text indices | **232** (engine walks 0..231 against a 232-bit bitmap) | the engine's 232-wide index space | no |
| VM opcode slots | 31 | u8 -> 255 | **31** ("never extend past 0x1E") | the dispatch table | code only |
| Native dispatch slots | 283 | u8 operand -> 255 | 283 measured; no bound check documented | **INFERRED**: slots above 255 are unselectable | code only |
| Interpreter variables | 12 | u8 -> 255 | 12 defined; 0 setter uses in the corpus | index byte | RAM, not ROM |

**Two structural facts for Phase B.** First, the object ceilings that bind before
bytes are: 452 maps, 255 objects per map, 7 dialogue containers, 40 static
scripts, 232 appearances, 297 sprite definitions, 1,534 text entries and 522
event resources. Second, most of those tables are addressed by a literal in
executable code, so growing them is an **executable patch**, not an allocation
question.

---

## 6. Runtime working-set ceilings

The repository records **no engine memory ceiling as a number**. That absence is
itself the finding, and what the project has measured points the same way: the
engine has one container dispatcher (`0x0803D940`) and one packed decoder whose
output is **unbounded** - it takes `(source, destination)` and writes until the
stream's own escape (`tools/webfoot/formats/webfoot_lz.py:54-63`). The ceiling is
never the codec; it is whatever destination each call site reserved.

| Destination | Size | Kind | Constrains | Evidence |
|---|---:|---|---|---|
| Dominant-layer chunk cell | `0x800` x **4** resident slots | DECOMPRESSED TEMPORARILY into a FIXED-SIZE POOL | map chunk layer | `LOGX_TILE_PROVENANCE.md:193-196,236-237` |
| Terrain-field cell (map 19 form) | `0x400` x **9** resident slots | FIXED-SIZE POOL | terrain field | `ASSET_EXPORT_MAP19_PROVENANCE.md:62-63`; `map_graphics.py:262-265` |
| Tileset bank work buffer | `0x4000` | DECOMPRESSED TEMPORARILY | map tileset bank | `MAP_RENDER_FORMAT.md:88-92,104-108` |
| Record `+0x34`/`+0x38` containers | `0x2000` each | DECOMPRESSED TEMPORARILY | map root | `LOGX_MAP_RENDER_PROVENANCE.md:541` |
| Selector stream (`root+0x48`) | declared 2..892 selectors | RESIDENT for the load | per-map selector stream | `docs/reverse-engineering.md:618-622` |
| Screen-entry plane upload | `0x800` | DECOMPRESSED TEMPORARILY | map plane | `ASSET_EXPORT_MAP_HANDLERS_PROVENANCE.md:126-142` |

Largest declared container size anywhere in the image: **65,474 bytes**; largest
reachable in the accepted corpus: `0x4000` (16 KiB). The **64 KiB figure is
explicitly not an engine limit** - it is a host-side tool constant, refuted three
times (`LOGX_CODEC_PROVENANCE.md:716`, `LOGX_SYNTHESIS.md:351`,
`LOGX_SYNTHESIS_PROVENANCE.md:455-457`), and one such bound was already proven
wrong once (CQA-02).

**INFERRED, arithmetic on cited facts (not directly observed):** canonical
selector streams decode to at most 892 selectors and each writes a 64-byte tile at
`0x06000000 + 64*ordinal`, while the BG screenblock area begins at `0x0600E000`.
`0x0600E000 / 64 = 896` tiles fit; the canonical worst case leaves ~**3 tiles** of
character-memory headroom. A stream with ~4 more selectors than the canonical
worst case would collide.

**Not established anywhere in this repository** (searched, not assumed): any
live-object/actor-instance cap (the registry at `0x03002A64` is append-only with
no capacity check); any OAM/on-screen sprite cap; the engine's destination buffer
for the compressed-text decode; any EWRAM/IWRAM heap ceiling; any per-frame copy
budget. One automated EWRAM instantiation scan is recorded as
**invalid / non-discriminating** (it returns zero for its own positive control),
so its empty result is not negative evidence
(`docs/research/AUTHORED_RUNTIME_PROOF.md:143-163`).

**Consequence:** "the ROM has room" does not imply "the engine can use more".
Every load path has a fixed reservation, and none of those reservations has been
shown to grow.

---

## 7. Capacity scenarios

Scenarios are arithmetic on the measured size distributions below, not on a
bytes-to-objects rule of thumb.

| Measured resource class | Count | Median | p90 | Max |
|---|---:|---:|---:|---:|
| Placement record | 1,559 | 32 B | 32 B | 44 B |
| Map slot array (modelled) | 105 | 32 B | 80 B | 184 B |
| Map objects per map | 452 maps | 2 | 9 | 51 |
| Text string (UTF-16LE body) | 1,534 | 30 B | 130 B | 490 B |
| Sprite container, packed | 7,390 | 280 B | 792 B | 1,708 B |
| Sprite container, decoded | 7,390 | 1,024 B | 4,096 B | 4,096 B |
| Dialogue container, packed | 7 | 17,472 B | 17,980 B | 17,980 B |
| Dialogue container, decoded | 7 | 65,348 B | 65,474 B | 65,474 B |

The text figures are not an estimate: the 1,534 bodies tile the declared
82,874-byte pool with total `82,874`, exactly.

### A. Existing holes only (no expansion)

| Basis | Bytes | What that is, practically |
|---|---:|---|
| **Declared free (allocatable today)** | **256** | 8 placement records, or 64 object slots, or 8 median text strings, or no sprite container at the median packed size (280 B), or no dialogue container (median packed 17,472 B) |
| Promotable-pending-review, margin 1,024 | 23,595 | ~737 placement records, or ~786 median text strings - but text is capped by the table's 1,534 entries, not by bytes |
| Promotable as >= 256-byte blocks | 19,712 | 70 sprite containers at the median packed size |
| Promotable as >= 1,024-byte blocks | 8,192 | 29 sprite containers at the median packed size |

**The 23,595 bytes are not free.** They are `UNKNOWN` fill that the established
verifier *could* clear, one bounded window per review. Promoting them requires
either accepting a smaller margin (which weakens a stated safety policy) or the
per-window proof-review path TOOLKIT-028 used. Nothing here promotes any of them.

### B. Modest expansion (16 MiB generated image)

| Quantity | Value |
|---|---:|
| Raw appended padding | 8,388,608 bytes |
| Engine-proven capacity, by domain | the compressed-dialogue selector path only |
| Dialogue containers | 7 exist; the selector table "must NOT be widened" |
| Sprite containers at the median packed size | ~29,959 fit by bytes |

The dialogue number exposes the distinction: 8 MiB holds roughly 480
copies of a median packed dialogue container, but there are only **seven
selectors**, so byte capacity is not what constrains dialogue. The table is.

### C. Maximum proven expansion

16 MiB. That is the largest engine-proven generated size, for one domain. The
nominal 32 MiB platform window is **unproven** for this engine, and the writer's
own cap is a policy (`<= 32 MiB`, power of two), not evidence.

---

## 8. Known unknowns

1. **No engine-side proof for thirteen of the sixteen listed pointer domains above canonical
   EOF.** Only compressed-dialogue selector entries are proven.
2. **5,350,325 bytes are `UNKNOWN`**, and 11,005 production reference *sources*
   live in bytes no annotation covers. Absence of an annotation is not absence of
   use.
3. **475 distinct unresolved candidate targets** inside the 292,440-byte tail.
   Each still blocks the bytes it addresses; none is resolved, whitelisted or
   downgraded.
4. **No measured live-object cap, OAM cap, engine heap bound, or per-frame copy
   budget.** One instrument that would have measured the first is recorded as
   invalid.
5. **`MapEntry+0x10`'s count field is unidentified.** The toolkit still sizes that
   extent with `+0x04`, a pairing the project has since proven bounds `+0x14`
   instead (`maps.py:308-315` vs `BUU_PLACEMENT_RUN_RELOCATION.md:207-219`). Any
   expansion reasoning about `+0x10` must treat its bound as `UNKNOWN`.
6. **Untested above 16 MiB**, and on real cartridge/flash hardware.
7. **The engine's compressed-text destination buffer is unknown**, so a larger
   dialogue container has no proven runtime budget.
8. **The local atlas is not usable as an allocation occupancy authority** - see
   below.

### 8.1 Finding: the atlas seed records derivative allocations as canonical structures

The tracked seed module `tools/webfoot/atlas_producers/seed.py` declares four
structures inside the 256-byte window this project has declared free:

| Seed claim | Offset | Bytes | Source |
|---|---|---:|---|
| `authored.placement_body` | `0x7EA400` | 32 | `seed.py:530-539` |
| `authored.descriptor` | `0x7EA420` | 8 | `seed.py:541-547` |
| `authored.script_body` | `0x7EA428` | 11 | `seed.py:549-556` |
| `authored.expanded_slot_array` | `0x7EA434` | 20 | `seed.py:558-566` |

**32 + 8 + 11 + 20 = 71 bytes**, and these are reproducible from tracked source
alone. The canonical bytes there are `FF` fill - measured here (histogram
`{0xFF: 256}`) and the basis of TOOLKIT-028's declaration. The seed rows say so
themselves: *"this is SDK-authored content written into that verified free window,
not canonical ROM structure. It does not exist in the canonical image; it is
recorded because the atlas must know the window is now claimed by the SDK"*
(`seed.py:537-539`).

It propagates: a local, identity-verified atlas built from this seed
(`build/atlas/atlas.jsonl`, `base_sha256` = the canonical hash; gitignored, so it
does not exist in a clean checkout) was observed to classify those 71 bytes as
`RUNTIME_CONFIRMED`/`CONFIRMED` coverage, leaving only 185 of the window's 256
bytes as `VERIFIED_FREE`. That observation is local corroboration; the tracked
seed rows above are the reproducible basis for the claim.

So this is a **deliberate, documented design choice**, not an accident - but it
means a canonical atlas answers "what is at this offset in the canonical image"
with derivative content, and it disagrees with the canonical free declaration for
71 of 256 bytes. Its positive half remains useful: an independent entropy pass
classifies the census's largest runs as `PADDING_CANDIDATE`, corroborating the
fill measurement.

**DEBT - `ROM-CAPACITY-ATLAS-SEED-OVERLAY-001` (OPEN, accepted by the owner; NOT
fixed in Checkpoint A or Checkpoint B).** Give the atlas seed rows an explicit
"not canonical" axis, or move SDK-authored rows into a separate layer, so a
canonical atlas and an allocation occupancy authority cannot disagree. Scope:
`tools/webfoot/atlas_producers/seed.py` (the four `authored.*` rows at
`:530-566`) and whatever consumes `free_region` rows in `atlas_build._seed_claims`.
It is outside capacity/allocation scope, it does not block this work - the
capacity model deliberately does not read the atlas - and it must not be folded
into Checkpoint B.

---

## 9. Production allocator policy: capacity-derived constraints (Phase B input)

The allocator itself is Checkpoint C work. What Phase A fixes is the input space
it must be written against:

* **Allocatable canonical bytes today: 256**, plus candidate windows only after a
  per-window review; `UNKNOWN` is never allocatable by default.
* **Allocatable expanded bytes:** only spans the profile's generated-image policy
  authorizes *and* only for domains proven able to address them. Today that is the
  compressed-dialogue selector domain; every other domain must fail closed above
  canonical EOF until separately proven.
* **The binding ceiling is often objects, not bytes:** 452 maps, 255 objects per
  map, 7 dialogue containers, 1,534 text entries, 297 sprite definitions,
  232 appearances, 40 static scripts.
* **Alignment:** 4-byte alignment is required by every pointer domain measured;
  the text pool needs 2; palettes 2. The declared window costs nothing to
  alignment.
* **Determinism and provenance** are Checkpoint C/D requirements, unchanged.

---

## 10. Product-facing summary: how much new stuff can we realistically add?

The answer is multidimensional, so there is no single percentage.

**ROM storage.** The canonical 8 MiB image has **256 bytes** of genuinely
verified-free space - enough for about eight new placement records. Beyond that,
the honest number is **23,595 bytes of *candidate* fill** (115 windows, largest
2,136 bytes) that the existing proof procedure could clear, one reviewed window at
a time; it is not free today. Expanding the image is proven safe at **16 MiB**,
which adds **8 MiB** of raw padding - but only for resources the engine is proven
to reach there.

**Engine addressability.** That qualifier is the real ceiling. Exactly one pointer
family has been shown to work above 8 MiB: the compressed-dialogue selector table.
Maps, scripts, text, sprites, map graphics, stats and palettes are all encoded as
absolute 32-bit ROM addresses and the toolkit will happily write them above 8 MiB,
but **no experiment shows the engine dereferencing any of them there**. For those
domains the practical capacity is still the canonical image.

**Object and table limits.** Several subsystems hit a count ceiling long before
they hit a byte ceiling. Dialogue has **7** containers and the selector gate must
not be widened. Text has 1,534 entries, and growing the table means rewriting 51
code references. Maps are capped at **452** by a constant in executable code. A
map holds at most **255** objects (retail peaks at 51). `static40` scripts are
exactly at their engine bound of 40. Appearances stop at 232, sprite definitions
at 297.

**Runtime limits.** The ROM is not the only budget. The engine's decoder has no
output bound at all - each load path reserved a fixed buffer (`0x400` to `0x4000`,
plus a 4-slot chunk cache and a 9-slot terrain cache), and nothing has been shown
to grow. Canonical character memory is within roughly **three tiles** of the
screenblock area. No live-object cap and no OAM cap has ever been measured.

**In one sentence:** the ROM can grow by 8 MiB and be addressed there by exactly
one subsystem today, canonical free space is 256 bytes, and for most subsystems a
fixed table or index - not ROM size - is what will stop you first.

---

## 11. Census corrections carried by this report

Two real defects were found in the census while it was being checked, and every
figure in this document already reflects the corrections.

The census omitted the `candidate_source` check it claimed to mirror. The
counterexample is real and canonical: `[0x32EC99, 0x32EC9A)`, a one-byte `FF`
pocket whose following bytes read `06 14 08`, holds the word `0x081406FF`, a
valid ROM pointer **sourced inside the pocket**. Writing that byte would corrupt a
word some unknown consumer reads as a pointer, and `verify_window` refuses it.
The reasoning that produced the omission is worth recording because it is
plausible and wrong: *"a census run is all `FF`, and `0xFFFFFFFF` is not a ROM
address, so no pointer can start inside it."* Only the **first** byte of the word
has to lie inside the run. The census now tests `candidate_sources` as well, and
`census_agrees_with_verifier` checks **every** run rather than the largest; the
largest run happened to be clean, which is precisely how the defect survived the
original tests.

Effect on this report: the promotable census **116 runs / 23,596 bytes became 115
runs / 23,595 bytes**, and the no-margin figure 336,393 / 35,968 became 336,135 /
35,729.

A second real defect was found while fixing the first: the region map's
attribution used a bounded backward scan for the innermost annotation, which could
miss a long enclosing span when many annotations began in between - reporting
`unattributed` for bytes that were in fact owned. It is now an exact active-set
sweep, and the map carries all 10,177 annotation owners instead of 4,185.


---

## 12. Domain reachable-capacity map (Checkpoint D addendum)

Checkpoint A answered *what each pointer domain can address* qualitatively. This
section answers it **quantitatively**, and it keeps three reachability levels
apart because collapsing them is exactly how a 32-bit field becomes a capacity
claim:

| Level | Meaning | Domains |
|---|---|---|
| **ENCODING** | the field's wire form can represent the address. A property of the format and of nothing else. | 13 of 16 |
| **ENGINE-STATIC** | static analysis of the consuming code found **no** truncation, masking, sign extension, fixed high bits or comparison that would reject the address. | **0 of 16** |
| **RUNTIME** | a real derivative actually caused the engine to dereference bytes in that range. | **1 of 16** |

`ENGINE-STATIC` is empty on purpose. The addendum's rule - *do not promote a
theoretical maximum* - cuts both ways: **not finding a bound is not the same as
proving there is none**, and this project has already lost time to a claim that
rested on absence of evidence. Where no bound was found the cell says UNKNOWN, and
the honest statement is "each untested domain has one byte of proof (none) and a
32-bit field", not "13 domains can use 8 MiB".

The one runtime-proven domain is proven over **the extent the engine actually
read** - the 17,932-byte relocated container at `0x08800000..0x0880460B` - and
deliberately **not** over the whole expansion. This is the distinction the
addendum asks for: *a pointer at `0x08800000` works* is not *every address
through `0x08FFFFFF` is proven*.

The tables below are generated from `tools/research/domain_reachability.py`; a
test compares this document against that module's output, so a figure cannot
drift between the data and the prose.
<!-- BEGIN GENERATED: domain reachable-capacity map -->

#### Reachable bytes by domain

| Domain | Pointer / reference form | Canonical VERIFIED_FREE reachable | Expanded ENCODABLE bytes | Expanded ENGINE-JUSTIFIED bytes | Expanded RUNTIME-PROVEN bytes | Proof level |
|---|---|---:|---:|---:|---:|---|
| Generic ROM pointers | absolute GBA u32 LE; no relative form | 256 | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| Compressed-dialogue selector table | absolute GBA u32 LE at 0x7B5B64 + selector*4 | 256 | 25,165,823 | UNKNOWN | 17,932 | RUNTIME |
| MapEntry +0x14 object array pointer | absolute GBA u32 LE; count is +0x04 (u8) | 256 | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| MapEntry +0x2C scene selector array | base of a u32 selector array; descriptor = base + 4*(selector-1) | 256 | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| MapEntry +0x10/+0x18/+0x1C/+0x20/+0x28/+0x30/+0x34 | absolute GBA u32 LE (shape only; no consumer decoded) | UNKNOWN | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| Placement-run pointer array (engine object array) | array of absolute GBA u32 LE; exactly count*4, no sentinel | 256 | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| Eight-byte slot arrays (MapEntry +0x10) | two u32 LE per slot; second word treated as a reference | 256 | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| Placement and descriptor records | u32 LE words at fixed record offsets; child_count 1..4 | 256 | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| Text pointer table and string pool | absolute LE GBA addresses; access is by index | 256 | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| Script record slots and bodies | absolute u32 LE in the record slot; body offset is pool-relative | 256 | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| Actor sprite chain (character/animation/frame/piece/container) | absolute u32 LE at every hop | 256 | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| Map scene descriptor and map graphics | absolute u32 LE at fixed descriptor offsets | 256 | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| Object and background palettes | NO indirection: a fixed absolute address, entry is the colour | 0 | 0 | 0 | 0 | NONE |
| Stat tables and the placement-type selector | fixed table + stride; the selector is an INDEX, not a pointer | 0 | 0 | 0 | 0 | NONE |
| Relocation and indirect pointer families | ABSOLUTE_ROM_U32_LE, RELATIVE_I32_LE, INDEX_U32_LE, INDEX_U8 | 256 | 25,165,823 | UNKNOWN | UNKNOWN | ENCODING |
| Packed text handle | 32-bit handle: selector 0-5, decoded start 6-20, length 21-31 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NONE |

#### Address ranges, limits and policy by domain

| Domain | Max ENCODABLE address | Max ENGINE-JUSTIFIED address | RUNTIME-PROVEN address | Structural / table limit | Structural class | Alignment / format | Allocator range policy | Primary bottleneck | Notes / UNKNOWN |
|---|---|---|---|---|---|---|---|---|
| Generic ROM pointers | 0x09FFFFFF | UNKNOWN | UNKNOWN | none (a helper, not a table) | THEORETICALLY_WIDENABLE | none imposed by the helper | per kind: only PACKED_STREAM defaults expanded-permitted | no bound found is not a bound found: the consumer decides | Representation is CONFIRMED; engine acceptance above EOF is UNKNOWN for every consumer that has not been tested. |
| Compressed-dialogue selector table | 0x09FFFFFF | UNKNOWN | 0x08800000..0x0880460B | exactly 7 selectors; the gate must NOT be widened | FIXED | 4 (word-indexed table) | PACKED_STREAM, EXPANDED_PERMITTED | the 7-entry selector table, not bytes: 8 MiB of expansion cannot add an eighth container | The one domain with runtime proof above EOF. Proven over the extent the engine actually read - the relocated container - NOT over the whole expansion. |
| MapEntry +0x14 object array pointer | 0x09FFFFFF | UNKNOWN | UNKNOWN | object count is one byte: 255 per map | RELOCATABLE | 4 | PLACEMENT_REFERENCE_ARRAY, canonical-only | the count byte, then the relocation-eligible array kind | Relocatable as an anchor kind; expansion above EOF is UNKNOWN. |
| MapEntry +0x2C scene selector array | 0x09FFFFFF | UNKNOWN | UNKNOWN | selector width UNKNOWN; longest observed run is 12 words | UNKNOWN | 4 | canonical-only (no kind allocates it) | selector resolution proven only for selector 1 | Resolution mechanism CONFIRMED at LEVEL 3; expansion UNKNOWN. |
| MapEntry +0x10/+0x18/+0x1C/+0x20/+0x28/+0x30/+0x34 | 0x09FFFFFF | UNKNOWN | UNKNOWN | +0x10 count field is UNIDENTIFIED | UNKNOWN | 4 | canonical-only | no consumer decoded, so no bound and no capacity claim | The toolkit still sizes the +0x10 extent with +0x04, a pairing the project has since shown bounds +0x14 instead. |
| Placement-run pointer array (engine object array) | 0x09FFFFFF | UNKNOWN | UNKNOWN | 255 slots per map (MapEntry+0x04, one ldrb) | RELOCATABLE | 4 | PLACEMENT_REFERENCE_ARRAY, canonical-only | the count byte | Traversal contract CONFIRMED; address range above EOF UNKNOWN. |
| Eight-byte slot arrays (MapEntry +0x10) | 0x09FFFFFF | UNKNOWN | UNKNOWN | array shape by measurement; no engine count decoded | UNKNOWN | 4 (required by the classifier) | canonical-only | the typed rung is a heuristic, not a decoded consumer | Round-trip is proven for the bytes; semantics are not. |
| Placement and descriptor records | 0x09FFFFFF | UNKNOWN | UNKNOWN | child_count clamped 1..4 (corpus bound, not an engine max) | UNKNOWN | 4 | canonical-only | the descriptor pointer's own validation window | The only production pointer bound using the nominal 32 MiB window (map_placements.py:166); that is a TOOLKIT bound, not engine evidence. |
| Text pointer table and string pool | 0x09FFFFFF | UNKNOWN | UNKNOWN | 1,534 entries; index widths u16 at consumers (65,535 max) | THEORETICALLY_WIDENABLE | pool alignment 2 | TEXT_STRING, canonical-only | the table has no growth path: a 1,535th string needs the table grown and 51 code references rewritten | Per-ENTRY relocation is proven on synthetic fixtures only. |
| Script record slots and bodies | 0x09FFFFFF | UNKNOWN | UNKNOWN | static40: exactly 40 records (engine bound); item_use: 83 | FIXED | 4 | canonical-only | the walker's immediate: retail is exactly at the 40-record bound | 28 execute from a runtime cursor, so a static pool cannot enumerate every reachable body. |
| Actor sprite chain (character/animation/frame/piece/container) | 0x09FFFFFF | UNKNOWN | UNKNOWN | 297 sprite definitions, terminated by a non-ROM word | FIXED | 4 on the table; no alignment test on a container pointer | canonical-only | the 297-entry run and its literal terminator | Containers are packed with zero slack: pixel edits do not relocate. |
| Map scene descriptor and map graphics | 0x09FFFFFF | UNKNOWN | UNKNOWN | 187 tile banks declared 0x4000 each | UNKNOWN | 4 | canonical-only | VRAM character extent, not ROM bytes (see runtime ceilings) | Rendering is proven only for maps 39/40, within the canonical image. |
| Object and background palettes | UNKNOWN | UNKNOWN | UNKNOWN | 256 object entries; 256 background entries | FIXED | 2 | no kind allocates a palette; edits are in place | the address is a code literal, so a palette cannot be moved without an executable patch | The one authoring class with no capacity question at all. |
| Stat tables and the placement-type selector | UNKNOWN | UNKNOWN | UNKNOWN | enemy_stats 141 x 0x1C; character_base_stats 9 x 0x12 | FIXED | 4 | no kind allocates a stat table | the table address is a code literal; six selectors already point past the verified extent | Index encodings are read-only: reassignment is not verified. |
| Relocation and indirect pointer families | 0x09FFFFFF | UNKNOWN | UNKNOWN | two anchor kinds are relocation-eligible | THEORETICALLY_WIDENABLE | 4 (1 for INDEX_U8) | depends on the anchor kind's semantic class | RELATIVE_I32_LE has no ROM user; index encodings are read-only | There is no relocation table in the ROM; relocation is a codec phase over anchors and typed references. |
| Packed text handle | UNKNOWN | UNKNOWN | UNKNOWN | selector 6 bits (64) but only 7 containers exist; record length 0..4,094 bytes | FIXED | no address; the extent is even by construction | not an address carrier; the selector slot carries the pointer | the handle never moves, which is why relocation works at all | Proven address-INDEPENDENT: the handle was unchanged while its container moved to 0x08800000. It is not itself an above-EOF carrier. |

<!-- END GENERATED: domain reachable-capacity map -->


### 12.3 Plain-English usable-capacity verdict

**Raw physical expansion.** The canonical 8 MiB image has 8,388,608 bytes of
authorized expanded storage behind it, and a 16 MiB generated image is
engine-proven to exist. That number is real and it is not usable by everything.

**Currently runtime-proven usable expansion.** **17,932 bytes, for one domain.**
The compressed-dialogue selector path placed a rebuilt container at file
`0x00800000` / address `0x08800000` through the production allocator, and the
retail engine read it and displayed the authored line. That is the whole of what
is *proven*, and it is small because it is the first thing proven rather than the
last thing possible.

**Statically addressable but not runtime-proven.** Thirteen domains can *encode*
an address above EOF - maps, scripts, text, sprites, map graphics, placements -
and **none** of them has a consumer whose acceptance above EOF has been
established either statically or at runtime. For those domains the practical
expanded capacity today is **zero**, not 8 MiB.

**Table-limited systems.** Several domains have bytes to spare and no way to use
them, and this is where the real ceiling sits for most authoring:

| System | Byte capacity | Structural capacity | Binds first |
|---|---|---|---|
| Dialogue | 8 MiB of expansion | **7 containers**, gate must not widen | the table |
| Text | 8 MiB (if proven) | 1,534 entries; table has no growth path | the table |
| Maps | 8 MiB (if proven) | **452** MapEntry records, a code constant | the constant |
| Objects per map | 8 MiB (if proven) | **255** (one `ldrb` count byte) | the count byte |
| Static scripts | 8 MiB (if proven) | **40** records, exactly at the engine bound | the engine bound |
| Sprites | 8 MiB (if proven) | **297** definitions plus a literal terminator | the run |
| Appearances | 8 MiB (if proven) | **232**, a 232-bit runtime bitmap | the bitmap |
| Palettes | none | 256 + 256 entries, fixed addresses in code | the address |

**Runtime memory.** Unchanged from Checkpoint A: the engine's decoder has no
output bound, every load path reserved a fixed buffer, and no live-object or OAM
cap has ever been measured. Reachable ROM bytes do not imply a usable working
set, and this section makes no claim about one.

**Where the limit actually is.** For dialogue the limit is a **7-entry table**.
For most other authoring it is **pointer reachability** - the bytes exist and
nothing has shown the engine will read them there. For maps, objects, scripts,
sprites and appearances it is a **count or index**, not bytes. Raw ROM size is the
binding constraint for almost nothing.

**In one sentence:** the ROM can grow by 8 MiB, exactly one subsystem is proven
able to use storage there and it is table-limited to seven containers, and for
everything else the limit is not ROM size but whether a domain's pointers reach
above 8 MiB at all.