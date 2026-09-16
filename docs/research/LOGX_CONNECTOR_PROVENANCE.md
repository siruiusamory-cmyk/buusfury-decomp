# LOGX-CONNECTOR-001: Buu's Fury root `+0x40`/`+0x44` transition records

Evidence document for the canonical Buu's Fury USA Rev. 0 image, SHA-256
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

Every claim is labelled with one status from
[`../research-conventions.md`](../research-conventions.md):

- **CONFIRMED** - directly supported by cited engine instructions, cited ROM
  bytes, or a reproducible observation scoped to this profile;
- **INFERRED** - best explanation supported by evidence, not directly proven;
- **UNKNOWN** - evidence absent, contradictory or insufficient.

**EXTERNAL CLAIM** marks a statement taken from `mainant/LOGExtractor`.
**PROJECT OBSERVATION** marks a reproducible measurement on the canonical image.
**PROJECT CONCLUSION** marks this ticket's reasoned verdict on an observation.

Terminology. The word *connector* is used in this document **only** where the
engine evidence supports a map-transition identity, and the physical field is
always named by its offset first. A *reference* is one 4-byte element of the
array `root +0x44` points at; a *record* is the address that element holds.
Those two counts are never merged.

---

## 1. Scope and input

Research only. No GUI, renderer, Workbench or authoring change is made. No
derived ROM was produced, no emulator was launched, and the canonical image was
opened read-only. Addresses are GBA addresses; file offset is address minus
`0x08000000`.

External lead: `mainant/LOGExtractor`, `MapViewer/MainForm.cs`. Its claims are
treated as claims only; nothing in this document is inherited from it.

**Correction carried into this ticket.** Two instruction quotations in the
accepted `LOGX_TILE_PROVENANCE.md` section 9.3 (the per-map presentation routine
around `0x080093B2`) do not match the canonical image's bytes. The real
instructions there are:

```text
080093B2  ldr  r4, [r6, #0xc]    ; r6 = arg0 + 0x80, so r4 = arg0 + 0x8C
080093D6  ldr  r0, [r4, #0x3c]   ; r4 = the scene descriptor
080093D8  ldr  r1, [pc, #0x270]  ; pool word 0x0800964C = 0x080716C4
0800964C  .word 0x080716C4
```

so the BG-index read really is `scene[+0x3C]` and the BG table really is
`0x080716D8 = 0x080716C4 + 0x14`, which is what that document concluded; only
its quoted byte strings were off. This ticket re-measured the region and does not
rely on the old quotations. The correction is recorded here rather than edited
into the accepted document.

---

## 2. Accepted dependencies from prior LOGX tickets

Used as given, not re-derived:

| Fact | Source |
| --- | --- |
| `MapEntry` table at `0x0808E2E0`, stride `0x38`, 452 records, `+0x00` a two-byte big-endian lookup key | LOGX-MAP-RECORD-001 |
| Selector-1 root route: `MapEntry[+0x2C]` -> leading run of aligned in-ROM words -> `word[0]` | LOGX-MAP-RENDER-001 |
| Root layer slots `+0x14`, `+0x18`, `+0x1C`, `+0x20` | LOGX-LAYER-001 |
| `root +0x48` selector stream; `root +0x4C` container bank table; Webfoot container header `kind`, `declared_size` | LOGX-TILE-001 |
| Project Webfoot container decoder `tools/webfoot/formats/webfoot_lz.py` | TOOLKIT-010 |

This ticket reuses those routes through `tools/research/logx_layer_probe.py`
and does not restate them as its own. The traversal helper
`resolve_selector_1_roots` is imported, not reimplemented.

---

## 3. `root +0x40` and `root +0x44` physical fields

### 3.1 Measurement

`python -m tools.research.logx_connector_probe <rom>` reports, over all 452
selector-1 roots. The pair was already recorded in `docs/reverse-engineering.md`
from LOGX-MAP-RENDER-001 as "count in `1..14`" / "aligned in-ROM pointer, null
exactly when `+0x40` is null"; this ticket reproduces that census independently
and extends it to the record layout:

| Quantity | Value |
| --- | ---: |
| Roots examined | **452** |
| `+0x40` == 0 | **104** |
| `+0x40` != 0 | **348** |
| Sum of `+0x40` | **735** |
| Maximum `+0x40` | **14** |
| `+0x40` distribution | `{0:104, 1:86, 2:188, 3:40, 4:27, 5:5, 6:1, 14:1}` |
| `+0x44` == 0 | **104** |
| `+0x44` != 0 | **348** |
| Distinct `+0x44` values | **348** |
| `+0x44` values shared by two roots | **0** |
| Every non-null `+0x44` aligned in ROM | **yes** |

### 3.2 The coupling

**PROJECT CONCLUSION.** Over the whole canonical corpus, `root +0x40 == 0` holds
if and only if `root +0x44 == 0`: 104 roots are zero/null and 348 are
nonzero/non-null, with no exception in 452. **CONFIRMED** (full census).

**PROJECT OBSERVATION.** The list pointer satisfies
`root + 0x44 == root - 4 * (root + 0x40)` on **all 348** non-null roots, with the
`root - pointer` distribution `{4:86, 8:188, 12:40, 16:27, 20:5, 24:1, 56:1}`.
This is a property of how the data was laid out, not an arithmetic the engine
performs, and it is recorded as a corpus invariant only. **CONFIRMED**
(full census).

**PROJECT OBSERVATION.** No `+0x44` value is shared between two roots, so the
348 arrays are disjoint in this image. That is a corpus fact, not a format rule.

### 3.3 Independence of the two fields

The ticket asks that PHYSICAL FIELD, COUNT SEMANTIC and CONNECTOR COUNT
SEMANTIC be classified separately. They are:

| Claim | Status |
| --- | --- |
| `root +0x40` is a 4-byte field | **CONFIRMED** (see 3.4) |
| `root +0x44` is a 4-byte pointer field | **CONFIRMED** (see 3.4) |
| `root +0x40` is the *number of elements* of the array at `+0x44` | **CONFIRMED** (see 3.4) |
| `root +0x40` is specifically a *connector* count | **PARTIALLY CONFIRMED** (the count pairs with an array of transition records; the engine's own name for them is not recovered) |

### 3.4 The consumer, and where the widths and the count semantic come from

**PROJECT OBSERVATION (the consumer, recovered).** The accepted
`docs/reverse-engineering.md` entry for LOGX-MAP-RENDER-001 already recorded that
`0x08009670` loads exactly this pair and forwards it to `0x08012664`; it listed
the record layout of `+0x44` as unresolved. This ticket read that site directly
and confirms the load. `0x08009670` is eight instructions:

```text
08009670  push  {r3, lr}
08009672  adds  r1, #0x40        ; r1 = selector-1 root + 0x40
08009674  ldr   r0, [pc, #0x280] ; pool 0x080098F8 = 0x080716C4 (a static base)
08009676  ldm   r1, {r1, r2}     ; r1 = root[+0x40] (count), r2 = root[+0x44] (array)
08009678  ldr   r0, [r0, #8]     ; r0 = the registry object
0800967a  bl    0x08012664       ; register(count, array, registry)
0800967e  pop   {r3, pc}
```

Raw bytes: `08b54031a04806c9806808f0f3ff08bd`. The single
`ldm r1, {r1, r2}` is the load that no constant-immediate scan can find: it reads
**eight bytes atomically** from `root + 0x40`, so neither half is read by a
`ldr ..., #0x40` / `#0x44` form. That is why the offset scan in this ticket found
nothing relevant.

**PROJECT OBSERVATION (the walk).** `0x08012664` is the consumer. It takes
`(r0 = registry, r1 = count, r2 = array)` and walks the array **backwards**,
calling each element's first word as a function pointer:

```text
08012664  push  {r4, r5, r6, lr}
08012666  adds  r6, r2, #0      ; r6 = the array
08012668  adds  r5, r0, #0      ; r5 = the registry
0801266a  subs  r4, r1, #1      ; r4 = count - 1
0801266c  bmi   0x08012688      ; count == 0 -> register nothing
0801266e  lsls  r0, r4, #2      ; 4 * index
08012670  ldr   r0, [r6, r0]    ; r0 = array[index]     <-- the pointer array
08012672  ldr   r1, [r0]        ; r1 = record + 0x00    <-- the record's first word
08012674  bl    0x08046AA2      ; call it through the bx r1 trampoline
08012678  ldr   r1, [r5]        ; registry count
0801267a  adds  r2, r1, #1
0801267c  lsls  r1, r1, #2
0801267e  adds  r1, r1, r5
08012680  str   r2, [r5]        ; bump the registry count
08012682  str   r0, [r1, #4]    ; append the returned object
08012684  subs  r4, #1
08012686  bpl   0x0801266e      ; index count-1 .. 0
```

Raw bytes: `70b5161c051c4c1e0cd4a0003058016834f015fa29684a1c890049192a604860013cf2d570bd`.

**PROJECT CONCLUSION.** `root +0x40` **is** the count of the pointer array at
`root +0x44`, and the engine iterates exactly that many elements. The element
width is 4 because of the `lsls r0, r4, #2` at `0x0801266E`; the record's first
word is called as a **function pointer** (`ldr r1,[r0]` at `0x08012672` through
the `bx r1` trampoline `0x08046AA2`); and each returned object is appended at
`registry + 4 + 4*n`. **CONFIRMED** (instruction access). This is the strongest
evidence in the ticket: it turns the count semantic from a census inference into
a cited engine loop.

**PROJECT CONCLUSION (entry path).** `0x08009670` has exactly one `bl` caller,
`0x08008AC2`, inside `0x08008AA0`:

```text
08008AB6  ldrb r1, [r7, #2]      ; request[+0x02] = the selector
08008AB8  ldr  r0, [r7, #4]      ; request[+0x04] = the MapEntry source array
08008ABA  bl   0x080089CC        ; the accepted "root + 4*(selector-1)" resolver
08008ABE  adds r1, r0, #0        ; r1 = the selector-1 root
08008AC0  ldr  r0, [r5, #0xc]    ; r0 = the registry object
08008AC2  bl   0x08009670        ; register that root's records
```

`0x080089CC` is the accepted selector resolver, so the count/array pair this
ticket censused is reached on the ordinary map-load selector-1 route.
**CONFIRMED.**

**PROJECT CONCLUSION (the prefix words).** The record's `+0x00` word is the
**class/constructor function pointer** the registry calls, which explains the
corpus shape of that field: two values (`0x08007675` x 566, `0x080072CD` x 169)
and one value at `+0x04` (`0x0800776D` x 735). A record carries a two-way class
tag as its first word plus a shared second word. **CONFIRMED** that the first
word is called as a function pointer; the *meaning of the two classes* is
**UNRESOLVED**.

**PROJECT CONCLUSION.** The physical widths are confirmed by the `ldm` (8 bytes
read into two 4-byte registers) as well as by the raw values. `+0x40` is a
4-byte little-endian count and `+0x44` is a 4-byte little-endian aligned pointer.
**CONFIRMED.**

### 3.5 The offset scan, and what an empty result would have meant

The project's constant-immediate scan
(`tools/research/thumb_mem_operands.py`) over `0x08000000..0x08007000` reports
**three** constant-offset sites at displacement `0x40` or `0x44`:

| Site | Instruction |
| --- | --- |
| `0x08003FC2` | `ldr r0, [r0, #0x44]` |
| `0x08004060` | `str r0, [r4, #0x44]` |
| `0x080040B6` | `str r3, [r4, #0x44]` |

All three are ordinary object-field accesses below the map/layer region and none
is the consumer. The real consumer uses `ldm`, which no constant-immediate scan
covers - a concrete instance of the warning in
`docs/research-conventions.md`: an empty scan result is not evidence of absence.
This ticket records the scan **and** the consumer it missed, so that the next
reader does not repeat the inference.

---

## 4. The array at `root + 0x44`

**PROJECT OBSERVATION.** Reading the elements as consecutive 4-byte
little-endian words from the pointer enumerates 735 references, all of which are
distinct 4-byte-aligned in-ROM addresses in `0x0817CA70..0x0829B478`.

| Quantity | Value |
| --- | ---: |
| References (array elements) | **735** |
| Null elements | **0** |
| Non-null elements | **735** |
| Aligned in ROM | **735** |
| Unaligned in ROM | **0** |
| Outside ROM | **0** |
| Distinct destination keys used | **350** |
| **Unique record addresses** | **735** |
| Records referenced more than once (**shared**) | **0** |
| Maximum references to one record | **1** |
| Record pointer range | `0x0817CA70`..`0x0829B478` |

*References*, *unique record addresses* and *unique destination keys* are three
different numbers and are never mixed. In this corpus references and unique
records happen to be equal (735), which is a *coincidence of this image*, not a
structural identity: nothing in the format prevents two array elements pointing
at one record, and the probe reports `shared_records` separately so that a future
image where it is nonzero is visible.

**PROJECT CONCLUSION.** `root +0x44` points at an **array of 4-byte ROM
pointers**, and `root +0x40` gives the number of elements. The element width is
4 because the engine's own indexing arithmetic multiplies an index by 4 before
adding it to the base (see section 5), not because the targets happen to be
spaced four bytes apart. **CONFIRMED** for the container, the element width and the count
(section 3.4).

---

## 5. The record

### 5.1 Physical layout

Every one of the 735 records was read at the engine's own access widths. The
layout below is stated per byte offset and is deliberately unnamed wherever the
engine does not name it.

| Offset | Width | Engine access | Measurement over 735 records |
| --- | --- | --- | --- |
| `+0x00` | 4 | not recovered | two values: `0x08007675` (566), `0x080072CD` (169) |
| `+0x04` | 4 | not recovered | one value on all 735: `0x0800776D` |
| `+0x08` | 2 | copied and compared by the object at `0x0800CEF4` | four-`u16` block A |
| `+0x0A` | 2 | " | four-`u16` block B |
| `+0x0C` | 2 | " | four-`u16` block C |
| `+0x0E` | 2 | " | four-`u16` block D |
| `+0x10` | 1 | `ldrb r0,[r4,#0x10]` at `0x0800729C` | `0..3` on 725; ten outliers |
| `+0x11` | 1 | `ldrb r1,[r4,#0x11]` at `0x0800728E` | **destination key high byte** |
| `+0x12` | 1 | `ldrb r2,[r4,#0x12]` at `0x0800728C` | **destination key low byte** |
| `+0x13` | 1 | `ldrb r1,[r4,#0x13]` at `0x08007282` | `{0:561, 1:174}` |
| `+0x14` | 2 | `ldrh r1,[r1,#0x14]` at `0x0800CDC6` | 139 distinct, `0..0xFFFF` |
| `+0x16` | 1+1 | `ldrb r2,[r2,#0x16]` at `0x0800CB70` | 142 distinct `u16`, `0..0xFFFC` |

**PROJECT OBSERVATION.** `+0x16` is read as a **byte** by the constructor
(`0x0800CB70`, `0x0800CB7E`) and as the high half of a `u16` elsewhere
(`0x0800CDC4` reads a `ldrh` at `+0x16` from a *different* base object). The
record's own `+0x16`+`+0x17` pair is therefore best described as two bytes whose
joint use is not established; the table records `+0x16` as the byte the engine
provably reads from the record.

**PROJECT OBSERVATION.** The 8-byte prefix is not padding and is not uniform:
`+0x04` is the same word on all 735 records, while `+0x00` takes exactly two
values. A record therefore carries a two-way class tag before its payload.

**PROJECT CONCLUSION (physical).** The record's **engine-accessed extent** is
`+0x00 .. +0x17`: 24 bytes, which is also the stride of the record block in this
image. The minimum extent the engine provably reads is `+0x00..+0x17`.
**CONFIRMED** (access widths above plus the 24-byte observed spacing).

**PROJECT CONCLUSION (prefix status).** `+0x00` and `+0x04` are 4-byte fields
whose *semantics* are **UNRESOLVED**. They are **not** declared padding; they
carry structured, invariant data, and two independent project points argue they
are code-address-shaped (both are 4-byte-aligned addresses in the
`0x08000000`-based code region, and `+0x00`'s two values sit in the same
`0x08007xxx` block as the record consumers recovered in sections 7 and 8). That
reading is **INFERRED**, not proven, and no class-table walk was recovered that
would settle it.

### 5.2 The four `u16` at `+0x08`

**PROJECT OBSERVATION.** Read as four consecutive little-endian `u16` values
`(A, B, C, D)`:

| Property | Result |
| --- | --- |
| `A <= C` and `B <= D` | **735 / 735** |
| Distinct values over all 2940 readings | **155** |
| Minimum | **0** |
| Maximum | **977** |
| `value % 8 == 0` | 1468 |
| `value % 8 == 1` | 1448 |
| `value % 8 == 7` | 24 |
| Zero-area (`A == C` or `B == D`) | **0** |

**PROJECT CONCLUSION.** The block is a pair of ordered intervals
(`A <= C`, `B <= D`) on all 735 records with no degenerate case. Calling them
left/top/right/bottom, or x/y/width/height, or min/max is **UNRESOLVED**: a pair
of ordered intervals is what the data supports, and the engine comparisons that
would name the axes were not recovered (section 9).

**PROJECT OBSERVATION.** Every value is `0` or `8k + 1` (with 24 exceptions at
`8k + 7`). That is a strong and reproducible shape, and it is consistent with a
pixel coordinate whose *last* pixel of an 8-pixel cell is the inclusive maximum.
It is **not** proof of a coordinate unit, and no conversion constant is
introduced on the strength of it.

### 5.3 The two `u16` at `+0x14`

**EXTERNAL CLAIM (LOGExtractor).** Nothing; LOGExtractor stops at the
destination.

**PROJECT OBSERVATION.** The record continues past the destination. The portal
object's update path holds the record at `r5` and reads it twice:

```text
0800CDC4  ldrh r0, [r5, #0x16]   ; the object's own current counter
0800CDC6  ldrh r1, [r1, #0x14]   ; record + 0x14  (r1 = the record pointer)
0800CDC8  adds r0, r0, r1
0800CDCA  strh r0, [r4, #0x16]   ; advance by record + 0x14 per step
```

and the constructor at `0x0800CB70`/`0x0800CB7C` reads the record's `+0x16`
**byte** twice and branches on `0x28` and `0x3C`:

```text
0800CB6E  ldr  r2, [r4, #0x20]   ; r2 = the record
0800CB70  ldrb r2, [r2, #0x16]
0800CB72  cmp  r2, #0x28
0800CB7E  ldrb r2, [r2, #0x16]   ; re-read after the first branch
0800CB80  cmp  r2, #0x3c
```

**PROJECT CONCLUSION.** `+0x14` and `+0x16` are engine-read fields whose
behaviour is time/behaviour-shaped rather than position-shaped: `+0x14` is an
animation advance and `+0x16` selects among at least three constructor
behaviours. Their exact semantics are **UNRESOLVED** and belong to the object
that consumes them, not to this record format. `+0x17` is read by the
constructor too (`0x0800CF30`) and is a small boolean-shaped byte (census
`{0:543, 1:180, 2:8, 3:2, 255:2}`).

---

## 6. The destination key

### 6.1 The measurement

**PROJECT OBSERVATION.** Treating the raw byte at `+0x11` as the **high** byte
and the raw byte at `+0x12` as the **low** byte gives a two-byte value that
equals an accepted `MapEntry +0x00` lookup key on **735 of 735** records.

An exhaustive 24 x 23 scan of every ordered byte pair in the record block finds
that this is **not** the only pair scoring 735: eleven others do, all of them
involving at least one offset inside the **invariant 8-byte prefix** or the
`+0x1B` byte - `(+0x02,+0x03)`, `(+0x02,+0x07)`, `(+0x02,+0x1B)`,
`(+0x03,+0x07)`, `(+0x03,+0x1B)`, `(+0x06,+0x03)`, `(+0x06,+0x07)`,
`(+0x06,+0x1B)`, `(+0x07,+0x03)`, `(+0x07,+0x1B)` and `(+0x1B,+0x03)`. Those
offsets do not vary with the record's destination (the prefix words are
constants and `+0x1B` is the last byte of the block), so they are constants
rather than keys. What distinguishes `(+0x11,+0x12)` is that it is the only
scoring pair whose two offsets are **both** inside the record's variable payload
and that the engine actually reads as a pair. **PROJECT OBSERVATION.**

| Candidate pair (high, low) | Resolves to a `MapEntry` key |
| --- | ---: |
| `(+0x11, +0x12)` | **735 / 735** |
| `(+0x12, +0x11)` | 369 / 735 |
| `(+0x10, +0x11)` | 589 / 735 |
| `(+0x12, +0x13)` | 136 / 735 |

(The pairs `(+0x02, +0x03)`, `(+0x06, +0x07)` and similar also score 735, but
those offsets are inside the **invariant 8-byte prefix**, whose two words do not
vary with the record's destination; they are constants, not keys.)

**PROJECT CONCLUSION.** The destination is the two bytes at `record +0x11` (high)
and `record +0x12` (low). **CONFIRMED** (full census; 735 of 735 with no
ambiguity among content offsets).

### 6.2 The engine reads it as two bytes, not as a halfword

**PROJECT OBSERVATION.** The record consumer at `0x080071F8` reads the
destination with three separate byte loads:

```text
08007282  ldrb r1, [r4, #0x13]   ; tail byte
0800728C  ldrb r2, [r4, #0x12]   ; key low  -> r2
0800728E  ldrb r1, [r4, #0x11]   ; key high -> r1
08007296  bl   0x08008d44        ; r0 = id, r1 = high, r2 = low, r3 = stack rect
```

**PROJECT OBSERVATION.** The accepted `MapEntry` lookup at `0x080089FC` also
compares its key with two separate byte loads rather than one halfword load:

```text
08008A0A  ldr  r1, [pc, #0x4c]   ; pool 0x08008A58 = 0x0808E2E0, the table base
08008A0E  ldrb r3, [r1]          ; entry[+0]
08008A10  cmp  r3, r4
08008A14  ldrb r3, [r1, #1]      ; entry[+1]
08008A16  cmp  r3, r5
08008A1E  adds r1, #0x38         ; next record
08008A20  adds r2, #1
```

The second halfword of the `ldrb r3,[r1]` encoding at `0x08008A0E` is `a342`,
i.e. `cmp r3, r4` - a byte comparison. There is no `ldrh` anywhere on this path.

**PROJECT CONCLUSION.** The destination is **two independent key bytes**, not a
halfword-typed field. The accepted prior-ticket rule that `MapEntry +0x00` is
"physically two bytes used as an ordered lookup key" therefore applies to the
destination *exactly*, and the record does not store a big-endian `u16` object
that happens to be comparable. **CONFIRMED** (instruction access on both the
producer and the consumer side).

**This is a REFUTATION of the external claim's physical model.**
**EXTERNAL CLAIM (LOGExtractor).** The destination is read as a big-endian
`u16`. **PROJECT CONCLUSION.** The engine never performs a halfword load of
these bytes; it compares two bytes separately. The big-endian *interpretation*
agrees with the engine's (high byte first) and is a correct way to display the
pair, but it is not the physical representation. **REFUTED as a physical
claim**; **CONFIRMED as a display convention that happens to match**.

### 6.3 The byte after the destination

**EXTERNAL CLAIM (LOGExtractor).** One byte is skipped before the destination.

**PROJECT OBSERVATION.** The consumer reads `[r4,#0x13]` into `r1` at
`0x08007282` and passes it as a *further argument* to the warp call, alongside
the two key bytes. Its census is `{0: 561, 1: 174}` - a boolean-shaped field.

**PROJECT CONCLUSION.** The byte is neither skipped nor padding; it is a
separate two-valued field the engine reads. Its *semantic* is **UNRESOLVED**
(a one-bit flag of unknown meaning is what the data and the call shape support).
**CONFIRMED** physically; **UNRESOLVED** semantically.

---

## 7. The engine's destination resolution

### 7.1 The lookup

`0x080089FC` is a linear scan over the `0x38`-stride `MapEntry` table:

| Question | Answer |
| --- | --- |
| Signature | `(r0 = table base, r1 = key byte 0, r2 = key byte 1)` |
| Reads per entry | `ldrb` at `+0` and `ldrb` at `+1` |
| Advance | `+0x38` per iteration |
| Bound | the count returned by `0x080125E0` |
| Miss behaviour | logs at `0x08008A26` and returns `0` |

**PROJECT CONCLUSION.** The destination resolves through exactly the accepted
`MapEntry +0x00` two-byte lookup key, by a linear scan. **CONFIRMED**
(instruction access).

### 7.2 The warp routine

`0x08008D44` is called with `r0` = a record-shaped destination buffer, `r1`/`r2`
= the two destination key bytes, and `r3` = a pointer to a coordinate pair:

```text
08008D44  push {r4,r5,r6,r7,lr}
08008D46  adds r5, r3, #0      ; r5 = the caller's coordinate pair
08008D4A  adds r4, r0, #0      ; r4 = the destination record buffer
08008D4C  ldrsh r0, [r5, #0]   ; r0 = coordinate[0]
08008D52  subs r0, #0x70       ; - 112
08008D54  str  r0, [sp, #8]
08008D5A  ldrsh r0, [r5, #2]   ; r0 = coordinate[1]
08008D5C  subs r0, #0x4c       ; - 76
08008D5E  str  r0, [sp, #0xc]
08008D60  lsls r0, r1, #0x18
08008D62  lsrs r0, r0, #0x18   ; r0 = key high byte, masked to 8 bits
08008D64  lsls r1, r2, #0x18
08008D66  lsrs r1, r1, #0x18   ; r1 = key low byte, masked to 8 bits
08008D68  strb r0, [r4]        ; destination[+0] = key high
08008D6A  strb r1, [r4, #1]    ; destination[+1] = key low
08008D6C  bl   0x080089fc      ; resolve the destination MapEntry
08008D70  adds r1, r0, #0
08008D78  add  r2, sp, #8      ; the adjusted coordinate pair
08008D7A  bl   0x08008b30      ; install it
```

**PROJECT OBSERVATION.** The two key bytes are copied into a two-byte buffer
**as two separate bytes** (`strb r0,[r4]` / `strb r1,[r4,#1]`) and then that
buffer is handed to the lookup. This is a third independent place where the
destination is handled byte-wise rather than as a halfword.

**PROJECT OBSERVATION.** The subtractions `-112` (`0x70`) and `-76` (`0x4C`) are
applied to the **caller's** coordinate pair (`r5`, passed in `r3`), not to the
record's `+0x08` block. They are the only coordinate arithmetic recovered on
this path.

**PROJECT CONCLUSION.** The destination resolution path is
`record +0x11/+0x12` -> `MapEntry` linear key scan -> `0x08008B30` install, with
the key bytes copied through a two-byte staging buffer. **CONFIRMED**
(instruction access and caller/callee analysis). What `0x08008B30` does with the
installed entry beyond storing it, and what coordinate space the `-112`/`-76`
adjustment converts between, are not decoded here and are handed off.

### 7.3 What is *not* claimed about the transition

**PROJECT CONCLUSION.** The engine performs a **two-byte-keyed map-entry lookup**
from each record. That is enough to support calling the record a **map-link
record** for the destination *field*: the destination is a `MapEntry` key by
construction, and a `MapEntry` is a map. It is **not** enough to name the
`+0x08` block a transition rectangle, to name the records "connectors" as a
format term, or to claim the engine tests a region membership on them.

| Claim | Status |
| --- | --- |
| the destination field is a `MapEntry` lookup key | **CONFIRMED** |
| the destination identifies a destination *map* | **CONFIRMED** (`MapEntry` is a map record; the lookup is the accepted map lookup) |
| the record is a map-to-map link | **PARTIALLY CONFIRMED** (the destination is a map; the trigger condition is not recovered) |
| the record is specifically a *connector* in the engine's own vocabulary | **UNRESOLVED** |
| the `+0x08` block is the transition region | **UNRESOLVED** (section 9) |

---

## 8. Consumers and data flow

### 8.1 The record consumer

`0x080071F8` is a per-record consumer. It reads, in order:

```text
08007210  ldrb r1, [r6, #0x11]
08007270  ldrh r7, [r0, #0x10]
08007272  ldrb r0, [r6, #0x10]
08007282  ldrb r1, [r4, #0x13]
0800728C  ldrb r2, [r4, #0x12]
0800728E  ldrb r1, [r4, #0x11]
0800729C  ldrb r0, [r4, #0x10]
```

`r4` is the record and `r6`/`r5` are scene objects. It therefore reads the
record's `+0x10`, `+0x11`, `+0x12` and `+0x13` bytes and calls the warp routine
with `+0x11`/`+0x12` as the destination key.

**PROJECT OBSERVATION.** The record consumer has **no direct `bl` caller
anywhere in the image** and is not reached through any literal pool word. It is
reached indirectly, exactly like the layer class methods recovered in
LOGX-TILE-001 (whose class words are tables of self-relative offsets rather than
absolute pointers).

**PROJECT CONCLUSION.** The record consumer's *existence and field reads* are
**CONFIRMED**; its *entry path* is **UNRESOLVED**. This is the same
indirect-dispatch shape the project has recorded before and is not a new
anomaly.

### 8.2 The object the record feeds

`0x0800CEF4` builds an object and **copies the record's 8-byte prefix plus its
`+0x08..+0x0F` block** into the new object:

```text
0800CF1C  ldm  r4!, {r1, r2, r3}   ; 12 bytes from the record
0800CF1E  stm  r7!, {r1, r2, r3}   ; ... to object + 0x24
0800CF20  ldm  r4!, {r3}           ; 4 more bytes
0800CF24  stm  r7!, {r3}           ; -> object + 0x30
0800CF26  ldr  r1, [r0, #0x20]     ; the saved record pointer
0800CF28  ldrb r2, [r1, #0x16]     ; record + 0x16 -> object + 0x08
0800CF30  ldrb r1, [r1, #0x17]     ; record + 0x17
```

**PROJECT CONCLUSION.** The record's first sixteen bytes flow into an engine
object whose own fields are then compared as ordered intervals. This is the
strongest engine-side evidence that the record's leading bytes are **region
data**, and it is why section 5.2 stops at "a pair of ordered intervals".
**CONFIRMED** (instruction access).

### 8.3 The consumer

**PROJECT OBSERVATION.** The selector-1 root's `+0x40`/`+0x44` pair is consumed
on the ordinary map-load route by `0x08009670`, which `ldm`s both words at once
and hands them to `0x08012664`; that routine walks the array backwards and calls
each element's `+0x00` word as a function pointer, appending the returned object
to a registry. The full instruction trace is in section 3.4.

**PROJECT CONCLUSION.** The record array is a **registry of constructor-called
objects**, populated once per map load, not a per-frame structure. What each
constructor returns, and what the registry does with the objects afterwards, are
outside this ticket.

**PROJECT OBSERVATION.** What this ticket still did not recover:
- which two coordinates the object created from a record compares, and when;
- whether a record is tested against the player's position at all;
- the caller chain that reaches the record consumer `0x080071F8` (it has no
  direct `bl` caller and is not in any literal pool, so it is reached indirectly
  like the layer class methods of LOGX-TILE-001).

**PROJECT CONCLUSION.** Those three are recorded as handoffs, not as absences.

## 9. LOGExtractor's `+8` adjustment

**EXTERNAL CLAIM (LOGExtractor).** Its viewer applies `X += 8` to the connector
rectangle, described by its author only as something that "seems right".

**PROJECT OBSERVATION.** No engine arithmetic recovered in this ticket adds or
subtracts `8` on a record coordinate. The two offsets the warp path *does* apply
are `-112` and `-76` at `0x08008D52` and `0x08008D5C`, to a separate coordinate
pair.

**PROJECT OBSERVATION.** A constant-immediate scan of the whole code region for
a load or store at displacement `8` would be meaningless (it is the most common
small displacement in any ARM program), so the ticket does not claim "no
instruction in the image involves `+8`". It claims something narrower and
checkable: **no `+8` was found on the destination-resolution path traced in
section 7**, and the destination path in fact adjusts by `-112` and `-76`.

**PROJECT CONCLUSION.** The `+8` adjustment is **UNRESOLVED**. It is neither
confirmed as part of the record semantics nor refuted as a viewer artefact: this
ticket found no engine counterpart, but it also did not exclude a
renderer- or hitbox-side origin. What can be said is that **it is not needed to
resolve the destination**, because the engine resolves destinations by key
lookup with no `+8` involved. The adjustment must not be promoted into any
project data.

---

## 10. Full record census

### 10.1 The graph

| Quantity | Value |
| --- | ---: |
| Records (references) | **735** |
| Unique records | **735** |
| Shared records | **0** |
| Maps with at least one link | **348** |
| Distinct destination keys used | **350** |
| Directed links | **694** |
| Reciprocal links | **674** |
| One-way links | **20** |
| Self links | **3** (source maps 125, 126, 127) |
| Destination resolutions that fail | **0** |

**PROJECT OBSERVATION.** Every one of the 348 maps with at least one record has
its destination keys covered by the 452-entry `MapEntry` table with no miss.

**PROJECT CONCLUSION.** The link graph is overwhelmingly reciprocal (674 of 694
directed links). That is a topology observation and is **not** used as semantic
proof: a reciprocal destination key is what two maps that lead into each other
look like, and also what two maps that merely reference each other look like.

### 10.2 Anomalies

The probe reports **zero** anomalies across every category it checks: no
zero-count-with-non-null-list, no non-null-count-with-null-list, no list outside
ROM, no null element, no unaligned or out-of-ROM record pointer, no unordered
bound pair, no zero-area region, no unresolved destination key, no duplicate
element within one root.

**PROJECT OBSERVATION.** A corpus with 735 records and *no* malformed entry is
itself informative: the record format has no in-image sentinel, no optional
fields and no partial records in this build.

### 10.3 Structural variants

**PROJECT OBSERVATION.** The only structural variation in the corpus is in the
8-byte prefix and in `+0x10`:

| Field | Census |
| --- | --- |
| `+0x00` | `0x08007675` x 566, `0x080072CD` x 169 |
| `+0x04` | `0x0800776D` x 735 |
| `+0x10` | `0..3` x 725; `0x11` x 6, `0x12`, `0x23`, `0x30`, `0x41` x 1 each |
| `+0x13` | `0` x 561, `1` x 174 |

**PROJECT CONCLUSION.** There are two record classes, tagged by `+0x00`. The
ten records whose `+0x10` exceeds 3 are the same records measured in section
10.4 and are the only shape outliers found. **CONFIRMED** (full census).

---

## 11. Representative records

All values are read from the canonical image.

| Source map | Root | `count` | List | Record | Destination key | `+0x10` | `+0x13` |
| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 33 | `0x0829B494` | 1 | `0x0829B490` | `0x0829B478` | `0102` -> 34 | 3 | 0 |
| 34 | `0x082996D0` | 2 | `0x082996C8` | `0x08299698` | `0105` -> 37 | 1 | 0 |
| 34 | " | " | " | `0x082996B0` | `0101` -> 33 | 2 | 0 |
| 35 | `0x0829835C` | 2 | `0x08298354` | `0x08298324` | `0105` -> 37 | 0 | 0 |
| 35 | " | " | " | `0x0829833C` | `0104` -> 36 | 1 | 0 |
| 36 | `0x08297C84` | 1 | `0x08297C80` | `0x08297C68` | `0103` -> 35 | 0 | 1 |
| 38 | `0x08295C58` | 1 | `0x08295C54` | `0x08295C3C` | `010B` -> 39 | 0 | 0 |
| 39 | `0x08294968` | 2 | `0x08294960` | `0x08294930` | `010A` -> 38 | 1 | 0 |
| 39 | " | " | " | `0x08294948` | `010C` -> 40 | 3 | 0 |
| 338 | `0x081DAD0C` | 3 | `0x081DAD00` | `0x081DACB8` | `0E04` -> 337 | 0 | 1 |
| 338 | " | " | " | `0x081DACD0` | `0E07` -> 340 | 1 | 1 |
| 338 | " | " | " | `0x081DACE8` | `0E06` -> 339 | 1 | 1 |

The byte-exact raw forms of the rows the body cites:

```text
map 33 0x0829B478  757600086d770008c803a000d103e10003010200
map 38 0x08295C3C  cd7200086d770008c00090016101a10100010b00
map 39 0x08294930  cd7200086d770008600000000101110001010a00
map 39 0x08294948  757600086d770008500288005902f10003010c00
map 338 0x081DACB8 757600086d77000890003001a1003901000e0401
map 338 0x081DACD0 757600086d7700080801200019013100010e0701
map 338 0x081DACE8 757600086d770008b8002000c9003100010e0601
```

**PROJECT OBSERVATION.** Maps 36 and 338 are where the `+0x13 = 1` class
appears among these rows: all four of those records carry `+0x13 = 1`, and three
of the three map-338 records do. The `+0x13` flag is therefore not confined to
one destination; it varies within a single map's own array.

Map 38's single record points at map 39, and map 39 has one record pointing back
at map 38 and one pointing at map 44 - a reciprocal pair plus a one-way link,
which is the shape most of the graph takes.

**PROJECT OBSERVATION.** The three self-links are maps 125, 126 and 127, whose
records point at their own `MapEntry` key.

**PROJECT CONCLUSION.** Location labels are used here only for correlation.
They are not structural proof, and no claim in this document depends on them.

---

## 12. Claim ledger

| # | Claim | Status | Support |
| --- | --- | --- | --- |
| 1 | `root +0x40` is a 4-byte integer field | **CONFIRMED** | raw inspection, full census |
| 2 | `root +0x40` is the element count of the `+0x44` array | **CONFIRMED** | `ldm r1,{r1,r2}` at `0x08009676`; the walk at `0x0801266A`..`0x08012686` |
| 3 | `root +0x40` is specifically a *connector* count | **PARTIALLY CONFIRMED** | it counts an array of map-destination records; the engine's own name for them is not recovered |
| 4 | `root +0x44` is a 4-byte aligned pointer field | **CONFIRMED** | raw inspection, full census |
| 5 | `root +0x44` points at an array of 4-byte ROM pointers | **CONFIRMED** | engine `4 * index` arithmetic, full census |
| 6 | `root +0x40 == 0` iff `root +0x44 == 0` | **CONFIRMED** | 452/452 |
| 7 | 735 references, 735 unique records, 0 shared | **CONFIRMED** | full census |
| 8 | Record accessed extent is `+0x00..+0x17` | **CONFIRMED** | instruction access widths, 24-byte spacing |
| 9 | `+0x00` and `+0x04` are not padding | **CONFIRMED** | invariant/two-valued census; engine reads them |
| 9a | `+0x00` is the record's class/constructor function pointer | **CONFIRMED** | `ldr r1,[r0]` at `0x08012672` calls it through `0x08046AA2` |
| 9b | the consumed count is exactly `root +0x40` | **CONFIRMED** | `0x08009676` `ldm`, `0x0801266A` `subs r4,r1,#1`, `0x08012686` `bpl` |
| 9c | the element width is 4 | **CONFIRMED** | `lsls r0,r4,#2` at `0x0801266E` |
| 10 | the meaning of the two `+0x00` classes | **UNRESOLVED** | two constructor addresses identified, class semantics not |
| 11 | `+0x08` is a block of four little-endian `u16` | **CONFIRMED** | access width, full census |
| 12 | the four `u16` form two ordered intervals | **CONFIRMED** | 735/735 `A<=C` and `B<=D`, no zero area |
| 13 | the intervals are left/top/right/bottom or min/max | **UNRESOLVED** | no axis-naming engine comparison recovered |
| 14 | the interval unit is a pixel or a tile | **UNRESOLVED** | values are `0` or `8k+1`; no conversion evidence |
| 15 | the destination is the bytes at `+0x11` (high) and `+0x12` (low) | **CONFIRMED** | 735/735 key resolution, engine reads |
| 16 | the destination is physically **two bytes**, not a `u16` | **CONFIRMED** | two `ldrb` on the producer and two on the consumer |
| 17 | the destination resolves through the `MapEntry +0x00` lookup | **CONFIRMED** | `0x08008D6C` -> `0x080089FC` |
| 18 | `+0x13` is a real engine-read two-valued field, not padding | **CONFIRMED** | `0x08007282`, census `{0:561, 1:174}` |
| 19 | the semantic of `+0x13` | **UNRESOLVED** | passed as an argument; meaning not recovered |
| 20 | `+0x14`/`+0x16` are engine-read fields | **CONFIRMED** | `0x0800CDC4`, `0x0800CF28` |
| 21 | the semantics of `+0x14`/`+0x16` | **UNRESOLVED** | belong to the consuming object |
| 22 | LOGExtractor's big-endian `u16` destination is the physical model | **REFUTED** | two byte loads, not one halfword load |
| 23 | LOGExtractor's `+8` adjustment has engine support | **UNRESOLVED** | no `+8` on the destination path; `-112`/`-76` instead |
| 24 | the record is a map-to-map link | **PARTIALLY CONFIRMED** | destination is a map; trigger condition not recovered |
| 25 | the records are "connectors" in the engine's own terms | **UNRESOLVED** | vocabulary and consumer not recovered |
| 26 | spawn / entry / facing / script fields | **UNRESOLVED** | not identified |
| 27 | the selector-1 root's `+0x40`/`+0x44` consuming instruction | **CONFIRMED** | `0x08009670` -> `0x08012664`, reached from `0x08008AC2` |
| 28 | the registry the returned objects are appended to | **PARTIALLY CONFIRMED** | `registry + 4 + 4*n`; the registry's other registrants were not enumerated |

---

## 13. Disagreements with LOGExtractor

| External claim | Project result |
| --- | --- |
| `root +0x40` is a connector count | the count is read together with the array by one `ldm` and consumed by `0x08012664`, which walks exactly that many elements: **PARTIALLY CONFIRMED** (confirmed as the element count of the `+0x44` array; the engine's own name for the records is not recovered) |
| `root +0x44` is a list of connector pointers | **CONFIRMED** as a 4-byte-pointer array with the count at `+0x40` |
| element = 8 skipped bytes + four `u16` + 1 byte + big-endian `u16` | **the offsets are right; the "skip" and the `u16` type are wrong**: `+0x00..+0x07` is a two-word prefix the engine reads, the four `u16` are at `+0x08`, and the destination is **two separate bytes** at `+0x11`/`+0x12` with a further byte at `+0x13` |
| the destination is a big-endian `u16` | **REFUTED** physically; the big-endian *view* matches the engine's byte order |
| `X += 8` | **UNRESOLVED**; no engine counterpart found, and not needed for resolution |
| the four values draw a map-transition rectangle | the four values are two ordered intervals on 735/735 and the engine copies them into an object it compares as intervals; **rectangle semantics are UNRESOLVED** |

---

## 14. Reproduction

```powershell
python -m tools.research.logx_connector_probe 'C:\path\to\Buu''s Fury (U).gba'
python -m tools.research.logx_connector_probe <rom> --roots --references --records
```

`tools/research/logx_connector_probe.py` opens its argument through
`Path.read_bytes`, performs no write, requires the exact 8 MiB size and the exact
canonical SHA-256, and emits deterministic JSON. It imports the accepted
root/layer traversal rather than re-deriving it. `--roots`, `--references` and
`--records` opt into the three detail blocks.

`tools/research/thumb_mem_operands.py` is the constant-immediate Thumb
load/store scan used for the access-width and coverage statements. It is a raw
halfword pass, so an undecodable neighbour cannot hide a site. Its coverage was
measured, not assumed. Over the canonical code region
``0x08000000..0x08070000``, walking real instruction boundaries
(resynchronising past undecodable halfwords) gives **3147** in-scope
constant-immediate accesses; the module reports every one of them identically
(**0 misses**). At every halfword offset where Capstone decodes a **16-bit**
instruction, the module never reports a site Capstone does not also decode as an
in-scope access (**0 misreports**). The same measurement is the projection
assertion in
``tests/integration/test_logx_connector_rom.py::test_the_operand_scan_agrees_with_capstone``.
It does **not** cover:

* the 32-bit register-offset / `imm8` pre-post-indexed families, `ldrsb`/`ldrsh`
  or the `pld`/`pldw` hints;
* `ldm`/`stm` and other register-list forms. This matters here: the
  `root +0x40`/`+0x44` pair is consumed by an `ldm`, so an empty result from this
  module says nothing about it;
* PC-relative literal loads, SP-relative loads and register-offset forms. The
  32-bit `imm12` encoding is shared with the SP-relative and PC-relative aliases,
  so the scan *does* report those two base registers and a field-access claim
  must filter them out.

`coverage_note()` returns the sentence a negative claim from it must carry.

`tests/integration/test_logx_connector_rom.py` is the ROM-gated regression form;
`LOGX_CANONICAL_ROM` overrides the default `roms/` path.
`tests/unit/test_thumb_mem_operands.py` is the portable synthetic form and needs
no ROM.

---

## 15. Unresolved questions and handoffs

**ANSWERED (was the primary question).** The instruction that reads
`root +0x40`/`+0x44` is `0x08009676` (`ldm r1, {r1, r2}` from `root + 0x40`) and
the walk is `0x08012664`. The earlier constant-immediate scan could not see it
because the pair is read as a single 8-byte `ldm`. See section 3.4.

**UNRESOLVED (now the primary question).** What the objects returned by each
record's `+0x00` constructor are, and what the registry does with them. The next
probe is the constructor at `0x08007674` (the 566-member class) and
`0x080072CC` (the 169-member class), plus the registry's own consumer. This is a
bounded, well-anchored follow-up.

**UNRESOLVED.** Whether the `+0x08` block is tested against a player or object
position at run time. Section 8.2 proves the block reaches an object that
compares ordered intervals; it does not prove which two coordinates the
comparison uses or when it runs.

**UNRESOLVED.** The coordinate unit and axis naming for the `+0x08` block. The
`0`-or-`8k+1` shape is recorded but not converted.

**UNRESOLVED.** The meaning of `+0x10`, `+0x13`, `+0x14` and `+0x16`.

**UNRESOLVED.** The `+8` adjustment's origin.

**HANDOFF to LOGX-CODEC-001.** Nothing in this ticket touches the container
decoder; the ticket reuses `tools/webfoot/formats/webfoot_lz.py` unchanged and
adds no new container type. No handoff.

**HANDOFF (runtime).** The region-membership question in section 8.3 is a
runtime question and needs the accepted mGBA capture path from
`docs/runtime-capture.md`: load a map, place the player on a record's interval,
and watch whether the `0x08008B30` install fires.

**HANDOFF (Workbench).** Any future Workbench map-overlay work that wants to
draw these records must use the physical fields in section 5.1 and must not
adopt the LOGExtractor `+8` adjustment; see `docs/research/WORKBENCH-006-design.md`
for the current scope boundary.
