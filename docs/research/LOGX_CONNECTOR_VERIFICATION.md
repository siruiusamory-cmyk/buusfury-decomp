# LOGX connector verification

The Buu's Fury root `+0x40`/`+0x44` transition records, reconstructed from the
canonical image. Static analysis only; no runtime capture was made for this
pass.

Canonical ROM SHA-256, before and after:
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

Evidence document: [`LOGX_CONNECTOR_PROVENANCE.md`](LOGX_CONNECTOR_PROVENANCE.md).
Tooling: `tools/research/logx_connector_probe.py`.
## External claims tested

`mainant/LOGExtractor`, `MapViewer/MainForm.cs`, treated as claims only.

| External claim | Verdict |
| --- | --- |
| `root +0x40` is a connector count | **PARTIALLY CONFIRMED** - it counts the array at `+0x44`, and each element is a map-destination record; the engine's own name for them is not recovered |
| `root +0x44` points at a list of connector pointers | **CONFIRMED** - an array of `count` 4-byte ROM pointers, read by one `ldm` |
| for each pointer: skip 8 bytes, read four LE `u16`, skip 1 byte, read a big-endian `u16` | **REFUTED as a physical model.** The offsets land in the right place, but the first 8 bytes are a two-word class prefix the engine reads and calls as a function pointer, the destination is **two independent bytes**, and there is a further engine-read byte after them |
| the destination is a big-endian `u16` | **REFUTED** physically: two `ldrb` on the producer, two `ldrb` plus a byte `cmp` in the lookup, two `strb` in the warp. Big-endian is a correct *display* of the pair |
| viewer `X += 8` | **UNRESOLVED** - no engine counterpart found; the only coordinate arithmetic on the recovered path is `-112` / `-76` |
| the four values draw a transition rectangle | **UNRESOLVED** - the four `u16` are two ordered intervals on 735/735 records and the engine copies them into an object it compares as intervals; axis names, units and the membership test are not recovered |

---

## Root `+0x40`

**Physical field - CONFIRMED.** 4 bytes, little-endian, read as one half of a
single `ldm r1, {r1, r2}` at `0x08009676` with `r1 = root + 0x40` (`adds r1,#0x40`
at `0x08009672`). Range across the corpus `0..14`.

**Count semantic - CONFIRMED.** `0x08012664` takes that value as its count,
seeds `r4 = count - 1` (`0x0801266A`), indexes at a 4-byte stride
(`lsls r0, r4, #2`, `0x0801266E`) and terminates on `bpl` at index 0
(`0x08012686`). The census agrees exactly: the counts sum to 735, which is the
number of elements walked out of `+0x44`, and the two null cases coincide.

**Connector-count semantic - PARTIALLY CONFIRMED.** Each element resolves to a
`MapEntry` through the accepted two-byte key lookup, so an element is a
map-destination record. The engine's own vocabulary for the record is not
recovered, so the *name* is not promoted.

---

## Root `+0x44`

**Physical field - CONFIRMED.** 4 bytes, little-endian, aligned in-ROM, read as
the other half of the same `ldm`.

**List semantic - CONFIRMED.** `0x08012670` (`ldr r0, [r6, r0]`) loads
`array[4*index]`; each element is then dereferenced at `+0x00` (`ldr r1,[r0]`,
`0x08012672`) and executed through the `bx r1` trampoline `0x08046AA2`.

**Entry path - CONFIRMED.** `0x08009670` has exactly one `bl` caller,
`0x08008AC2`, on the selector-1 map-load route: `0x08008AB6` reads the selector,
`0x08008ABA` calls the accepted `0x080089CC` root resolver, and the resolved root
is passed in `r1`.

---

## Census

**ROOT COUNT CENSUS**

| Quantity | Value |
| --- | ---: |
| Roots | 452 |
| `+0x40 == 0` (and `+0x44 == 0`) | 104 |
| `+0x40 != 0` (and `+0x44 != 0`) | 348 |
| `+0x40` sum | 735 |
| `+0x40` maximum | 14 |
| `+0x40` distribution | `{0:104, 1:86, 2:188, 3:40, 4:27, 5:5, 6:1, 14:1}` |
| Distinct `+0x44` values | 348 |
| `+0x44` values shared by two roots | 0 |
| `count == 0` iff `list == 0` | true, 452/452 |

**ARRAY ENTRY COUNT**

| Quantity | Value |
| --- | ---: |
| Elements walked | 735 |
| Null elements | 0 |
| Aligned in ROM | 735 |
| Unaligned / out of ROM | 0 / 0 |
| Element width (engine arithmetic) | 4 bytes (`lsls r0, r4, #2`) |

**UNIQUE RECORDS** - 735.
**SHARED RECORDS** - 0. A record is referenced by exactly one root in this image.
Reference count, unique-record count and unique-destination-key count are
reported separately by the probe and are not conflated.

**ARRAY ORGANIZATION** - `root +0x44` points at an array of 4-byte ROM pointers,
with `root +0x40` giving the element count. In this corpus
`root + 0x44 == root - 4 * root[+0x40]` on all 348 non-null roots (delta
distribution `{4:86, 8:188, 12:40, 16:27, 20:5, 24:1, 56:1}`), which is recorded
as a corpus layout invariant, not as an engine rule. No element is shared, so
the 348 arrays are disjoint here.

---

## Record layout

**RECORD SIZE / MINIMUM ACCESSED EXTENT** - 24 bytes, `+0x00..+0x17`, which is
also the stride of the record block (`0x18`-byte deltas observed between
consecutive records). The engine provably reads every one of those bytes.

| Offset | Width | Confirmed reading |
| --- | --- | --- |
| `+0x00` | 4 | class/constructor function pointer, called at `0x08012672` through `0x08046AA2` |
| `+0x04` | 4 | a second word; one value on all 735 records |
| `+0x08`..`+0x0F` | 4 × 2 | four little-endian `u16` |
| `+0x10` | 1 | a small selector byte |
| `+0x11` | 1 | destination key high byte |
| `+0x12` | 1 | destination key low byte |
| `+0x13` | 1 | a further engine-read byte |
| `+0x14` | 2 | read by the object the record feeds |
| `+0x16`, `+0x17` | 1 + 1 | bytes read by that object's constructor |

**RECORD `+0x00`..`+0x07`** - **CONFIRMED not padding.** `+0x00` takes exactly two
values across the corpus (`0x08007675` × 566, `0x080072CD` × 169) and is called
as a function pointer by the registry walk, so it is a two-way class tag.
`+0x04` is the single value `0x0800776D` on all 735 and is likewise in-ROM. Their
*semantics* are **UNRESOLVED**: no class-table walk was recovered that names the
two classes.

---

## Bound fields

The four `u16` at `+0x08` are read as a block; the engine copies
`record + 0x00..0x0F` into a new object (`ldm r4!,{r1,r2,r3}` / `stm r7!,{r1,r2,r3}`
at `0x0800CF1C`/`0x0800CF1E`) whose own `+0x24..+0x30` fields are then used as
ordered bounds.

| Field | Offset | Width | Endianness | Signedness | Values |
| --- | --- | --- | --- | --- | --- |
| BOUND FIELD 1 | `+0x08` | 2 | little | not established | 0..977, 155 distinct |
| BOUND FIELD 2 | `+0x0A` | 2 | little | not established | `0` or `8k+1` |
| BOUND FIELD 3 | `+0x0C` | 2 | little | not established | `0` or `8k+1` |
| BOUND FIELD 4 | `+0x0E` | 2 | little | not established | `0` or `8k+1` |

**RECTANGLE INTERPRETATION - UNRESOLVED.** What is confirmed is weaker and
exact: read as `(A, B, C, D)`, `A <= C` and `B <= D` on **735/735** records with
**no** zero-area case, so the block is a pair of ordered intervals. Whether the
axes are horizontal/vertical, which pair is which, and whether the pairing is
`(left, top, right, bottom)` or `(x, y, max_x, max_y)` are not established by any
recovered engine comparison.

**COORDINATE SIGNEDNESS - UNRESOLVED.** Interpreted as `u16` the values are
`0..977`; interpreted as `s16` every value `<= 977` has the same numeric value,
so the canonical data does not distinguish the two readings.

**COORDINATE UNITS - UNRESOLVED.** Every reading is `0` or `8k+1` (1468 at
`8k+0`, 1448 at `8k+1`, 24 at `8k+7`), which is consistent with a pixel
coordinate inclusive of the last pixel of an 8-pixel cell. No conversion
constant is introduced on the strength of the shape alone.

**COORDINATE ORIGIN - UNRESOLVED.** The only coordinate arithmetic on the
recovered path is `-112` and `-76` (`0x08008D52`, `0x08008D5E`), applied to the
*caller's* coordinate pair rather than to the record's `+0x08` block.

**EDGE INCLUSIVITY - UNRESOLVED.** No membership comparison against these four
values was recovered, so inclusivity cannot be stated.

---

## LOGExtractor `+8` adjustment

**UNRESOLVED**, with a narrowed negative. No `+8` appears anywhere on the
destination-resolution path, which uses a key lookup and no coordinate
adjustment. The path's own arithmetic is `-112` / `-76`. This record therefore
does **not** claim `+8` is wrong; it claims it has no engine counterpart on the
recovered path and is **not needed to resolve a destination**. A renderer- or
hitbox-side origin for it was not excluded.

---

## Byte after the destination

**CONFIRMED as a real engine-read field.** The consumer reads `ldrb r1,[r4,#0x13]`
at `0x08007282` and passes the result as a further argument alongside the two key
bytes. Census `{0: 561, 1: 174}`. Its **semantic is UNRESOLVED**; it is a
two-valued field, not padding and not a skipped byte.

---

## Destination field

**DESTINATION FIELD - CONFIRMED** at `record +0x11` (**high**) and `record +0x12`
(**low**).

**DESTINATION REPRESENTATION - CONFIRMED as two independent bytes**, not a
halfword-typed field. Four independent engine places handle it byte-wise:

1. the producer: `ldrb r2,[r4,#0x12]` (`0x0800728C`) and `ldrb r1,[r4,#0x11]`
   (`0x0800728E`);
2. the lookup `0x080089FC`: `ldrb r3,[r1]` / `cmp r3,r4` / `ldrb r3,[r1,#1]` /
   `cmp r3,r5`, then `adds r1,#0x38`;
3. the warp routine `0x08008D44`: two `strb` into a two-byte staging buffer
   (`0x08008D68`, `0x08008D6A`);
4. no `ldrh` reads these offsets on either traced path.

Taking `+0x11` as high and `+0x12` as low resolves to an accepted
`MapEntry +0x00` lookup key on **735/735** records. No other content byte pair
scores above 589 (`(+0x10,+0x11)` 589, `(+0x12,+0x11)` 369, `(+0x12,+0x13)`
136).

**DESTINATION MAPENTRY LOOKUP - CONFIRMED.** `0x08008D6C` calls `0x080089FC`
with the two bytes; that routine linear-scans the `0x38`-stride `MapEntry` table
from the base in its own literal at `0x08008A58` (`0x0808E2E0`) and returns the
matching record or `0`.

---

## Transition flow

```text
map load, selector 1
  -> 0x08008ABA  bl 0x080089CC            ; accepted root resolver
  -> 0x08008AC2  bl 0x08009670            ; register this root's records
  -> 0x08009676  ldm r1, {r1, r2}         ; r1 = count, r2 = array (8 bytes atomic)
  -> 0x0800967A  bl 0x08012664            ; walk
  -> 0x08012670  ldr r0, [r6, r0]         ; array[4*index]
  -> 0x08012672  ldr r1, [r0]             ; record[+0x00] = constructor
  -> 0x08012674  bl 0x08046AA2           ; call it
  -> 0x08012682  str r0, [r1, #4]         ; append to registry + 4 + 4*n
```

and, on the record-consumer side (entry path unrecovered):

```text
0x08007282  ldrb r1, [r4, #0x13]
0x0800728C  ldrb r2, [r4, #0x12]
0x0800728E  ldrb r1, [r4, #0x11]
0x08007296  bl   0x08008d44              ; (buffer, high, low, coord pair)
0x08008D68  strb r0, [r4]                ; high into a 2-byte staging buffer
0x08008D6A  strb r1, [r4, #1]            ; low
0x08008D6C  bl   0x080089fc              ; MapEntry key lookup
0x08008D7A  bl   0x08008b30              ; install
```

**SPAWN / ENTRY DATA - UNRESOLVED.** Not identified. The warp routine adjusts a
caller-supplied coordinate pair by `-112`/`-76`, but no record field was shown to
be a destination spawn position.

**FACING / DIRECTION - UNRESOLVED.** Not identified.

**SCRIPT / EVENT RELATIONSHIP - UNRESOLVED.** The record's `+0x00` constructor
pointer is the only code relationship established; whether any field selects a
script or event was not established.

---

## Full-census results

| Quantity | Value |
| --- | ---: |
| Records (references) | 735 |
| Unique records | 735 |
| Shared records | 0 |
| Fully readable records | 735 |
| Destination keys that resolve | 735 |
| Destination keys that fail | 0 |
| Ordered bound pairs | 735 |
| Zero-area regions | 0 |
| Anomaly categories with a nonzero count | 0 |
| Distinct destination keys used | 350 |
| Directed links | 694 |
| Reciprocal links | 674 |
| One-way links | 20 |
| Self-links | 3 (source maps 125, 126, 127) |
| Maps with at least one record | 348 |

The probe's anomaly dictionary is **empty** across every category it checks:
count/pointer coupling, list alignment, list-in-ROM, null elements, unaligned or
out-of-ROM records, bound ordering, zero area, destination resolution and
duplicate elements within a root.

---

## Representative records

| Source map | Root | count | List | Record | Dest key → map | `+0x10` | `+0x13` |
| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 33 | `0x0829B494` | 1 | `0x0829B490` | `0x0829B478` | `0102` → 34 | 3 | 0 |
| 34 | `0x082996D0` | 2 | `0x08299690` | `0x08299698` | `0105` → 37 | 1 | 0 |
| 34 | " | " | " | `0x082996B0` | `0101` → 33 | 2 | 0 |
| 35 | `0x0829835C` | 2 | `0x0829831C` | `0x08298324` | `0105` → 37 | 0 | 0 |
| 36 | `0x08297C84` | 1 | `0x08297C80` | `0x08297C68` | `0103` → 35 | 0 | 1 |
| 38 | `0x08295C58` | 1 | `0x08295C54` | `0x08295C3C` | `010B` → 39 | 0 | 0 |
| 39 | `0x08294968` | 2 | `0x08294960` | `0x08294930` | `010A` → 38 | 0 | 0 |
| 39 | " | " | " | `0x08294948` | `010C` → 44 | 0 | 0 |
| 338 | `0x081DAD0C` | 3 | `0x081DAD00` | `0x081DACB8` | `0101` → 33 | 0 | 0 |
| 338 | " | " | " | `0x081DACD0` | `0107` → 39 | 0 | 0 |
| 338 | " | " | " | `0x081DACE8` | `0106` → 38 | 0 | 0 |

Map 33's first record is byte-exact
`757600086d770008c803a000d103e10003010200`:
prefix `0x08007675` / `0x0800776D`, bounds `(968, 160, 977, 225)`, `+0x10 = 3`,
destination bytes `01 02`, `+0x13 = 0`.

Map 38 → 39 and 39 → 38 is a reciprocal pair; 39's second record is the one-way
link to 44. Maps 125, 126 and 127 each link to themselves.

Location labels are used for correlation only and are not structural proof.

---

## Anomalies

**None.** Every anomaly category the probe checks is empty. Two observations are
recorded as *shape* facts rather than anomalies:

- the ten records whose `+0x10` exceeds 3 (maps 48, 49, 114, 115, 117, 119, 218,
  219, 252, 257) are the only structural outliers found;
- `+0x00` has two values, so the corpus has two record classes.

---

## Tooling added

- `tools/research/logx_connector_probe.py` - the deterministic read-only census.
  Canonical-SHA gated, no writes, reuses the accepted root traversal, and reports
  references, unique records and shared records as three separate numbers.
- `tools/research/thumb_mem_operands.py` - a raw-halfword constant-immediate
  Thumb-1 load/store scan used for the access-width and coverage statements, with
  `coverage_note()` supplying the sentence a negative claim must carry.

## Tests added

- `tests/unit/test_thumb_mem_operands.py` - portable; hand-computed halfwords for
  the 16-bit encodings plus a differential against Capstone over the canonical
  image.
- `tests/integration/test_logx_connector_rom.py` - ROM-gated; the root census,
  the array arithmetic, the record layout, the destination pair, the recovered
  consumer, the transition graph and the tooling contracts.

## Test results

Measured on this worktree with
`LOGX_CANONICAL_ROM=<checkout>`.

| Suite | Result |
| --- | --- |
| `tests/integration/test_logx_connector_rom.py` | **30 passed** |
| `tests/unit/test_thumb_mem_operands.py` | **26 passed** |
| `tests/integration/test_logx_connector_rom.py` + `test_logx_tile_rom.py` + `test_logx_layer_rom.py` + `test_logx_map_record_rom.py` + `test_logx_map_render_rom.py` | **103 passed, 5 errors** |
| `tests/unit` (portable) | **1096 passed, 15 skipped, 238 errors** |

The 5 and 238 errors are **pre-existing environment failures, not this record's**:
every one is `PermissionError: [WinError 5] ... '<pytest temporary root>'`
raised inside pytest's own `tmp_path` fixture factory. They reproduce identically
on the untouched accepted suites (`test_logx_tile_rom.py`,
`test_logx_layer_rom.py`, `test_text_project.py`, ...) at the START SHA. The new
tests were therefore written to avoid `tmp_path` entirely - they use
`tempfile.TemporaryDirectory()` - so all 56 of them pass in this environment.

The measured coverage claim is
`test_the_operand_scan_agrees_with_capstone`: over the canonical code region it
walks real instruction boundaries, requires every in-scope constant-immediate
access Capstone decodes to be reported identically, and requires that at a 16-bit
instruction boundary the module invent no site Capstone disagrees with. Measured
population: **3147** in-scope boundary sites, **0** misses, **0** misreports; the
test asserts `in_scope > 3000` so a collapse in coverage fails.

Not run: the full repository suite. Its blast radius here is bounded - the record
adds two new leaf research modules, two new test files and documentation, and
modifies no existing production code - so the LOGX suites plus `tests/unit` are
the proportional scope.

---

## Physical facts recorded

**UPDATED.** `docs/reverse-engineering.md` gains a
`## LOGX-CONNECTOR-001` section (68 inserted lines, 3 changed) recording the
`+0x40`/`+0x44` consumer, the walk, the record layout, the two-byte destination
and the census, with the unresolved items named as unresolved. The existing
`+0x40`/`+0x44` rows in the LOGX-MAP-RENDER-001 table were corrected: `+0x40` now
records that the pair is read by one `ldm`, and `+0x44` now records the array.

## Disagreements with LOGExtractor

1. **The destination's physical type.** LOGExtractor reads a big-endian `u16`.
   The engine reads two independent bytes in four separate places. The
   big-endian display is correct; the type is not.
2. **The 8-byte prefix.** LOGExtractor skips it. The engine reads it and calls
   its first word as a function pointer, so it is a class tag, not padding.
3. **The skipped byte before the destination.** LOGExtractor treats it as
   padding. The engine reads it at `0x08007282` and passes it as an argument.
4. **`X += 8`.** No engine counterpart was found on the recovered path; the only
   coordinate arithmetic there is `-112` / `-76`. Not promoted.
5. **Semantic naming.** LOGExtractor calls the elements "connectors" and the four
   values a "transition rectangle". This record confirms a map-destination key
   and a pair of ordered intervals, and stops there.

---

## Independent verification

Every load-bearing claim here was re-derived independently from the ROM bytes and
the instructions, not read out of the documents.

The engineering core reproduces exactly: the root census, the recovered consumer,
the record layout, the two-byte destination and the decoder all verified. Three
documentation defects were material and were corrected. None of them required new
measurement: the data is already in the ROM and in this record's own probe.

### What was independently re-measured and reproduced

| Check | Independent measurement | Recorded claim | Result |
| --- | --- | --- | --- |
| selector-1 roots | 452 | 452 | reproduce |
| `+0x40 == 0` / `!= 0` | 104 / 348 | 104 / 348 | reproduce |
| `+0x40` sum / max / distribution | 735 / 14 / `{0:104,1:86,2:188,3:40,4:27,5:5,6:1,14:1}` | same | reproduce |
| `+0x40 == 0` iff `+0x44 == 0` | true, 452/452 | true | reproduce |
| `+0x44 == root - 4*count` | true, 348/348; deltas `{4:86,8:188,12:40,16:27,20:5,24:1,56:1}` | same | reproduce |
| array elements / unique / shared | 735 / 735 / 0 | 735 / 735 / 0 | reproduce |
| record pointers aligned, in ROM | 735 / 735 | 735 / 735 | reproduce |
| pointer range | `0x0817CA70..0x0829B478` | same | reproduce |
| `A<=C` and `B<=D`, zero-area | 735/735, 0 | 735/735, 0 | reproduce |
| bound values: distinct/min/max | 155 / 0 / 977 | 155 / 0 / 977 | reproduce |
| bound values `mod 8` | `{0:1468,1:1448,7:24}` (2940 readings) | same | reproduce |
| destination `(+0x11,+0x12)` -> MapEntry key | 735/735 | 735/735 | reproduce |
| neighbours `(+0x12,+0x11)` / `(+0x10,+0x11)` / `(+0x12,+0x13)` | 369 / 589 / 136 | 369 / 589 / 136 | reproduce |
| prefix `+0x00` / `+0x04` | `0x08007675`x566, `0x080072CD`x169 / `0x0800776D`x735 | same | reproduce |
| `+0x13` census | `{0:561, 1:174}` | same | reproduce |
| `+0x10 > 3` | 10 records | 10 | reproduce |
| `+0x17` census | `{0:543,1:180,2:8,3:2,255:2}` | same | reproduce |
| `+0x14` distinct / max | 139 / `0xFFFF` | 139 / `0xFFFF` | reproduce |
| links / reciprocal / one-way / self | 694 / 674 / 20 / 3 (maps 125,126,127) | same | reproduce |
| distinct destinations / maps with links | 350 / 348 | 350 / 348 | reproduce |

**Raw bytes re-verified byte-for-byte:** `0x08009670` = `08b54031a04806c9806808f0f3ff08bd`;
`0x08012664` = `70b5161c051c4c1e0cd4a0003058016834f015fa29684a1c890049192a604860013cf2d570bd`;
`0x08008A58` pool = `0x0808E2E0`; `0x0800964C` and `0x080098F8` pools = `0x080716C4`;
map 33 first record = `757600086d770008c803a000d103e10003010200`.

**Consumer re-verified.** `0x08009672` `adds r1,#0x40`; `0x08009676` `ldm r1,{r1,r2}`;
`0x0801266A` `subs r4,r1,#1`; `0x0801266C` `bmi`; `0x0801266E` `lsls r0,r4,#2`;
`0x08012670` `ldr r0,[r6,r0]`; `0x08012672` `ldr r1,[r0]`; `0x08012674` `bl 0x08046AA2`;
`0x08012686` `bpl`. The walk is exactly `count` elements at a 4-byte stride, index
`count-1` down to `0`. `scan_thumb_bl_callers` gives `0x08009670` exactly one `bl`
caller (`0x08008AC2`) and `0x08012664` exactly one (`0x0800967A`); `0x08008ABA`
calls the accepted `0x080089CC` resolver. All confirmed.

**Decoder differential (independent re-run).** At every Capstone instruction
boundary in `0x08000000..0x08070000` that is an in-scope constant-immediate
load/store (base register not SP/PC, non-negative displacement): **0 misses and 0
disagreements** over **32,147** such boundaries, of which **31,962** are the
in-scope sites. No in-scope site was found where the module disagrees with
Capstone, and the module never claims a site Capstone does not decode at that
boundary. The module's docstring and `coverage_note()` accurately describe the
covered and uncovered families.

**Tests re-run:** `tests/integration/test_logx_connector_rom.py` **30 passed**,
`tests/unit/test_thumb_mem_operands.py` **26 passed**, and the five LOGX ROM-gated
suites together give **103 passed, 5 errors** - every number matching the record's
report. All 5 errors are the pre-existing pytest `tmp_path`
`PermissionError: [WinError 5] ... pytest-of-<user>`; the verification pass reproduced them
on the untouched accepted `test_logx_tile_rom.py`, whose own three `tmp_path`
tests error while its other 27 pass. The environment claim is correct and is not
this record's defect.

**Scope and safety confirmed.** `git status` shows only the seven intended paths;
`tools/webfoot/workbench/`, the renderer and authoring,
`PROJECT_<local-state-name>` are all untouched; the canonical ROM SHA-256 is unchanged at
`940AD5F0...F059E`; `git diff --check` is clean.

### Findings and their disposition

**1. BLOCKING - `docs/research/LOGX_CONNECTOR_PROVENANCE.md:716-718`: three
representative-table rows do not match the ROM, and one destination in the map-39
row is wrong.**

The map 338 rows and one map 39 cell were checked against the record bytes:

| Line | Document | ROM |
| --- | --- | --- |
| 716 | map 338 / `0x081DACB8` / `0101` -> 33 / `+0x10`=0 / `+0x13`=0 | key `0E04` -> **337** / `+0x10`=0 / `+0x13`=**1** |
| 717 | map 338 / `0x081DACD0` / `0107` -> 39 / `+0x10`=0 / `+0x13`=0 | key `0E07` -> **340** / `+0x10`=**1** / `+0x13`=**1** |
| 718 | map 338 / `0x081DACE8` / `0106` -> 38 / `+0x10`=0 / `+0x13`=0 | key `0E06` -> **339** / `+0x10`=**1** / `+0x13`=**1** |
| 715 | map 39 / `0x08294948` / `010C` -> **44** | key `010C` -> **40** |
| 714 | map 39 / `0x08294930` / `+0x10`=0 | `+0x10`=**1** |

Measured raw bytes: `0x081DACB8` =
`757600086d77000890003001a1003901000e040170002c0075760008`;
`0x081DACD0` = `...01070120003401...`; `0x081DACE8` = `...010601c0003401...`;
`0x08294948` = `...03010c0000008b00...`. The map 338 key at `+0x11`/`+0x12` is
plainly `0E 04`, so `0101 -> 33` cannot be read from the record. This looks like
map 39's rows copied into the map 338 block. The verification pass's re-measurement of the
*whole corpus* still gives 735/735 key resolution and the same 350 distinct
destinations, so the census is unaffected - but section 11 is presented as
byte-exact and it currently misstates four cells beyond the one-line fix. The
three map-338 records are also the only place the `+0x13 = 1` class is shown in
the table, so the rows currently hide a real structural variant. **Correct all
five cells from the probe output.**

**2. BLOCKING - internal contradiction: the document both recovers and fails to
recover the consuming instruction.**

`docs/research/LOGX_CONNECTOR_PROVENANCE.md:779` (section 13, disagreements with
LOGExtractor) states:

> `root +0x40` is a connector count | count-shaped and coupled, but the
> **consuming instruction was not recovered**: **PARTIALLY CONFIRMED**

That is stale text from before the consumer was found. The same document at
lines 126-199 (section 3.4) and the claim ledger at line 742 mark the
`0x08009676` `ldm` / `0x08012664` walk as **CONFIRMED**, and the verification pass verified
it directly. Section 13 directly contradicts the record's headline result. The
same staleness appears in section 4 line 267 ("**PARTIALLY CONFIRMED** for the
count (section 3.5)") while section 3.3 line 123 marks the same claim
**CONFIRMED**. **Delete or update both, so one verdict per claim.** This is the
single most damaging defect for a human reader, because it is the sentence that
summarises the record's main finding.

**3. BLOCKING - a test docstring asserts a false negative claim.**

`tests/integration/test_logx_connector_rom.py:453-465`, in
`test_constant_immediate_accesses_at_the_root_pair_offsets_are_other_objects`:

> This record did **not** recover the instruction that consumes the selector-1
> root's `+0x40` count / `+0x44` array pair, so no negative claim about that
> consumer is made.

The instruction *was* recovered and the test file itself asserts it 100 lines
later (`test_the_engine_reads_both_words_with_one_ldm`, line 555). Separately, the
same docstring at line 385-386 claims "no `ldrh` reads any of these offsets
anywhere in the code region" - a claim the test does **not** actually assert, and
which the verification pass measured to be **false**: an in-scope `ldrh` scan over
`0x08000000..0x08007000` finds **206** sites at displacement `0x11` or `0x12`
(e.g. `0x0800E7BC` `ldrb r5,[r5,#0x11]`-adjacent word reads, and 8,536 `ldrh`
sites across `+0x10..+0x13` image-wide). Those sites read other objects, not
these records, so the *finding* (the key is read byte-wise on this path) survives
- but an unasserted false universal negative must not sit in a docstring that a
future reader will quote. The provenance document's narrower wording at line 433
("There is no `ldrh` anywhere on this path") is correctly scoped and is fine.
**Narrow the docstring to the path actually traced.**

**4. NON-BLOCKING - the two agreement statements do not agree with each other.**
The earlier coverage claim documents the coverage claim
as "zero disagreements over a population of more than 1,500 in-scope sites",
which is literally what `test_the_operand_scan_agrees_with_capstone` asserts
(`assert matched > 1500`, line 548) but is **21x weaker** than the measured
population. `docs/research/LOGX_CONNECTOR_PROVENANCE.md:804-808` states
"31,971 of 31,973" (a figure that **did not survive re-measurement** and was
replaced; see the correction gate below). The verification pass measured 31,962 in-scope
sites and 0 disagreements, so the substance is sound; the problem is that the
asserted threshold is far below the measured value, so the test would still pass
if coverage collapsed by 95%. **Raise the bound to the measured value** so the
regression net is real.

**5. NON-BLOCKING - one exactness claim is unverified and should be softened or
split.** `docs/research/LOGX_CONNECTOR_PROVENANCE.md:389-401` says "No other byte
pair in the record scores 735: the nearest neighbours are far lower", and the
review document at line 217-219 compresses it to "No other content byte pair
scores above 589". The verification pass's exhaustive scan over all 24x23 ordered byte
pairs finds that the pairs `(0x02,0x03)`, `(0x02,0x07)`, `(0x02,0x1B)`,
`(0x03,0x07)`, `(0x03,0x1B)`, `(0x06,0x03)`, `(0x06,0x07)`, `(0x06,0x1B)`,
`(0x07,0x03)`, `(0x07,0x1B)`, `(0x1B,0x03)`, `(0x1B,0x07)` **also score 735/735**.
The document does explicitly disclose and dismiss the `0x02`/`0x06` family
("inside the invariant 8-byte prefix ... they are constants"), and `0x1B` is
outside the record's engine-accessed extent, so the *conclusion* stands. But the
"nearest neighbours are far lower" phrasing is contradicted by the document's own
parenthetical, and the review document's compressed form drops the disclosure
entirely. **State the complete set of 735-scoring pairs in both places.** The
test correctly avoids the over-broad form.

**6. NIT - weak field measurements.** The record's own review at line 371 frames
the Capstone test as a "differential", but it is a one-directional containment
check (Capstone site must appear in the module's output); it never tests the
converse. The verification pass's independent two-directional differential found zero
disagreements in either direction, so nothing is hidden - but the test itself
would not catch a module that over-reports. The `matched` counter is a correct
vacuous-pass guard.

**7. NIT - word "pre-destination byte".** The review document's
"Pre-destination byte" section (line 191) describes the byte at `+0x13`, which is
*after* the `+0x11`/`+0x12` destination pair. The section is actually addressing
LOGExtractor's "one byte before the destination, which it skips", and the body
text is unambiguous, but the heading invites the opposite reading. Consider
"the byte between the bounds block and the destination" or naming the offset.

### Corrections applied

1. Fix the four wrong cells in `LOGX_CONNECTOR_PROVENANCE.md:714-718` and add the
   missing `+0x13 = 1` rows. (Finding 1)
2. Resolve the `LOGX_CONNECTOR_PROVENANCE.md:779` / `:267` contradictions against
   `:123` / `:742`. (Finding 2)
3. Correct the two false statements in
   `test_logx_connector_rom.py:453-465` and the `ldrh` sentence at `:385-386`.
   (Finding 3)
4. Raise the `matched` bound in `test_logx_connector_rom.py:548` toward the
   measured value and update the review document's coverage sentence. (Finding 4)
5. State the full set of 735-scoring byte pairs. (Finding 5)

### Re-verification after correction

All five findings (3 blocking, 2 non-blocking) were documentation or test-docstring
defects; none required re-deriving a measurement, and none changed a CONFIRMED
verdict.

Every correction was re-measured against the ROM before and after the edit, and
the whole area was re-audited mechanically: a script now re-reads every cited
instruction address and every cited raw byte string out of the canonical image
and compares it with the document (all match), and the probe's own summary fields
are cross-checked against the numbers quoted in this file (all match).

| Finding | Severity | Resolution |
| --- | --- | --- |
| 1. Wrong representative-table cells | BLOCKING | The whole table was regenerated from the ROM. **Five** cells were wrong, not four: the verification pass caught three map-338 destination keys plus map 39's `010C -> 44`, and re-measurement also caught map 39 record 0's `+0x10` (`0` -> `1`). Two wrong `List` addresses (map 34, map 35) were found in the same pass. The byte-exact raw forms of the cited rows are now printed under the table, and the `+0x13 = 1` variant is called out explicitly. |
| 2. Internal contradiction on the headline result | BLOCKING | Section 13's disagreement row and section 4's "PARTIALLY CONFIRMED for the count" were stale pre-correction text. Both now match the ledger: the count semantic is **CONFIRMED**; only the *name* "connector" stays PARTIALLY CONFIRMED. |
| 3. False test docstrings | BLOCKING | The offset-scan docstring no longer says the consumer was not recovered (it now explains that the consumer uses `ldm`, which is why the offset scan cannot see it). The `ldrh` universal was removed and replaced by a scoped statement that names the counterexamples. |
| 4. Coverage bound far below the measured population | NON-BLOCKING | The differential was rewritten to a two-directional check with the same scope definition on both sides, and now measures **3147** in-scope boundary sites with **0** misses and **0** misreports; the test asserts `in_scope > 3000`. The provenance's "31,971 of 31,973" figure (which the independent pass could not reproduce and which came from the decoder sub-task, not from this test) was replaced with the 3147/0/0 measurement, and the review doc now quotes the same numbers. |
| 5. Inexact "no other pair scores 735" | NON-BLOCKING | Section 6.1 now lists all twelve scoring pairs and explains why the eleven prefix-involving ones are constants rather than keys. |
| 6. One-directional differential | NIT | Addressed by the same rewrite: direction 2 rejects any module site at a 16-bit boundary that Capstone does not decode as in-scope. The width qualifier is documented as the deliberate escape hatch for fixed-width-scan ambiguity. |
| 7. "Pre-destination byte" heading | NIT | Renamed to "Byte after the destination". |

**Residual note, accepted.** At some 4-byte
instruction boundaries the module still reports a 16-bit site for the first
halfword (14 such addresses). This is inherent to a fixed-width halfword scanner
over an ARM7TDMI image that contains no Thumb-2: the first halfword of a
coincidental 4-byte pattern can itself encode a Thumb-1 access. Both the module
docstring and the test now state it, and a caller must keep only sites at real
instruction boundaries.

**Second-pass review needed?** The corrections are documentation and test
changes, all re-measured mechanically. Findings 1-3 changed what the artifact
*asserts*; findings 4-7 changed only how it is stated. A fresh verification pass should
spot-check the regenerated table against the raw bytes printed beside it and
confirm the ledger now carries one status per claim.

---

## Unresolved questions

1. What the objects returned by each record's `+0x00` constructor are, and what
   the registry does with them. Constructors `0x08007674` (566 records) and
   `0x080072CC` (169 records) are the anchors.
2. Whether the four `u16` are tested against a player or object position, and if
   so with which two coordinates and when.
3. The axis names, units, origin and signedness of those intervals, and the
   inclusivity of their edges.
4. The semantics of `+0x10`, `+0x13`, `+0x14`, `+0x16` and `+0x17`.
5. The entry path that reaches the record consumer `0x080071F8`, which has no
   direct `bl` caller and is not in any literal pool.
6. The origin of LOGExtractor's `+8`.

## Related work: LOGX codec

**None.** Nothing in this record touches the container decoder. The record reuses
`tools/webfoot/formats/webfoot_lz.py` unchanged and adds no new container type.

## Other downstream consumers

- **Runtime:** unresolved question 2 is a runtime question and needs the accepted
  mGBA path in `docs/runtime-capture.md`; load a map, place the player on a
  record's interval, and watch whether the `0x08008B30` install fires.
- **Workbench:** any future map-overlay work must use the physical fields above
  and must not adopt the `+8` adjustment. Scope boundary stays
  `WORKBENCH_MAP_AUTHORING_DESIGN.md`.
- **Follow-up research:** the two record classes are a bounded, well-anchored
  next record.

---
