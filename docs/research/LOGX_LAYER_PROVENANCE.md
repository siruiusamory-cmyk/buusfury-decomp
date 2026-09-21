# Buu's Fury layer records (LOGX-LAYER-001)

Read-only static evidence for the canonical Buu's Fury USA image,
SHA-256 `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
(8 MiB, GBA address = file offset + `0x08000000`).

This document separates three evidence classes throughout:

* **EXTERNAL CLAIM** - what an outside project (LOGExtractor) asserts;
* **PROJECT OBSERVATION** - what this ticket read or decoded from the image;
* **PROJECT CONCLUSION** - what this ticket concludes, with its status.

Statuses are `CONFIRMED` / `PARTIALLY CONFIRMED` / `REFUTED` / `UNRESOLVED`.
Physical structure (width, alignment, pointerhood) and semantic identity are
classified **separately**; a physical claim is never promoted by a semantic
argument.

Tooling added by this ticket: `tools/research/logx_layer_probe.py` (census) and
`tools/research/thumb_disasm.py` (resynchronising disassembly helpers). Tests:
`tests/integration/test_logx_layer_rom.py`.

---

## 1. Accepted dependencies

Taken as given from `LOGX-MAP-RECORD-001` and `LOGX-MAP-RENDER-001`; nothing in
this ticket re-derives or weakens them.

| Fact | Source |
| --- | --- |
| MapEntry table `0x0808E2E0`, stride `0x38`, 452 records | MAP-RECORD / TOOLKIT-007 |
| `MapEntry+0x2C` is an indexed-word source; selector `1` is `word[0]` of the leading aligned in-ROM run | MAP-RECORD, MAP-RENDER |
| The selector-1 object is a per-map **load-time definition template** | MAP-RENDER |
| `root+0x14`, `+0x18`, `+0x1C`, `+0x20` are 4 aligned in-ROM pointers to layer records | MAP-RENDER |
| `root+0x04..+0x07` are added to `BG0CNT..BG3CNT` in slot order at `0x080093E0..0x08009406` | MAP-RENDER |
| `root+0x08`/`+0x0A` are halfword pixel extents stored as `extent - 1` | MAP-RENDER |
| `root+0x48` is a delta-coded u16 selector stream; `+0x4C` is the shared atlas `u32[]` at `0x08179764` | MAP-RENDER |
| Chunk containers decode to `0x800` bytes = 1024 regular-BG screen entries | MAP-VIS-002 |

The prior ticket's layer claims are re-tested in section 9.

---

## 2. Census methodology

`tools/research/logx_layer_probe.py`:

* opens the ROM read-only. It is SHA-256 gated: any image other than the
  canonical one is refused before a byte is interpreted;
* resolves each of the 452 selector-1 roots with the **accepted** route
  (`MapEntry[+0x2C]` -> leading aligned in-ROM run -> `word[0]`), reusing the
  same rule as `logx_map_render_probe.py` rather than re-implementing it
  differently;
* reads the four layer slots `+0x14`, `+0x18`, `+0x1C`, `+0x20` at 32-bit
  width and classifies each resolved target as null / not-4-aligned-in-ROM /
  outside-ROM / non-null;
* reports each unique target's first 0x60 bytes, its 4-aligned word census, its
  `+0x18` window, and an anomaly list;
* separately scans `0x08100000..0x08400000` for every 4-aligned occurrence of
  each distinct `+0x00` word, so records reachable from a root and records
  merely present in the image are reported apart.

Pointer classification means only "4-byte aligned and inside the 8 MiB image".
It is not evidence of a target structure type.

### 2.1 Aggregate result

| Quantity | Value |
| --- | --- |
| MapEntries examined | 452 |
| Valid selector-1 roots | 452 |
| Layer references (4 slots x 452) | 1808 |
| Null layer slots | **0** |
| Non-null layer references | 1808 |
| Unique layer records | **1464** |
| Shared layer records (referenced more than once) | 35 |
| Distinct `+0x00` words | **5** |
| Layer pointer range | `0x080707FC`..`0x082B8BC8` |
| Unreadable unique records | 0 |
| Unique records with a non-null `+0x18` window | 1463 |

### 2.2 `+0x00` word census

| `+0x00` word | Unique records | References |
| --- | ---: | ---: |
| `0x08008087` | 1420 | 1516 |
| `0x0800897B` | 41 | 41 |
| `0x08007A41` | 1 | **249** |
| `0x08007B63` | 1 | 1 |
| `0x080088BD` | 1 | 1 |

All five values are **odd** (Thumb-bit-set) and **not** 4-byte aligned; that is
the expected shape of a Thumb code pointer, but section 4 shows it is not a
sufficient reading.

### 2.3 Per-slot usage

| Root slot | References | Null | Distinct targets | `0x08008087` | `0x0800897B` | `0x08007A41` | others |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `+0x14` | 452 | 0 | 330 | 349 | 5 | 98 | - |
| `+0x18` | 452 | 0 | 319 | 326 | 1 | 124 | `0x08007B63` x1 |
| `+0x1C` | 452 | 0 | 398 | 415 | 11 | 25 | `0x080088BD` x1 |
| `+0x20` | 452 | 0 | 420 | 426 | 24 | 2 | - |

**PROJECT CONCLUSION.** The four slots are **not** four different schemas:
all four draw on the same five-word vocabulary and the same record shape. The
slot distribution differs (a higher-BG slot is more likely to be the
zero-dimension absent record), but the *structure* is shared. Four root slots
therefore mean four layer instances, not four record types.
**CONFIRMED** (physical).

### 2.4 Shared records

35 records are referenced by more than one root. The dominant one is
`0x080707FC`, referenced **249** times as the zero-dimension placeholder. The
next-largest groups are three records referenced 10, 10 and 10 times by maps
163/172/175/182/184/189/194/197..., i.e. neighbouring maps sharing a layer
definition, and a run of 5- and 4- and 3-way groups in
`0x0822C000`..`0x0822F000` and `0x0829C000`..`0x0829F000`.

**PROJECT OBSERVATION.** Sharing is real and cross-map: at least one group of
ten maps points the **same** `+0x14` record and the same `+0x1C`/`+0x20`
records, i.e. an identical three-layer stack. **CONFIRMED** (physical).

---

## 3. Where the engine consumes a layer record

Every claim in this section is a static instruction reading, from a
resynchronising sweep over `0x08007000..0x08010000` plus raw halfword dumps.

### 3.1 The constructor chain

```text
08008086  1c0a  adds  r2, r1, #0        ; r2 = record
08008088  1c01  adds  r1, r0, #0        ; r1 = destination object
0800808a  b508  push  {r3, lr}
0800808c  2000  movs  r0, #0            ; r0 = NULL
0800808e  f7ff fd73  bl 0x08007B78      ; real constructor
08008092  bd08  pop   {r3, pc}
```

`0x08007B78` is therefore reached with `(r0 = NULL, r1 = destination,
r2 = layer record)`, and returns "the object" in `r0`.

Caller census (`scan_thumb_bl_callers` over the whole image, raw halfword
decoding): `0x08007B78` has exactly **one** `bl` caller, `0x0800808E`.
`0x08008086` has **no** `bl` caller: it is reached only through the `+0x00`
word of a record, i.e. it is invoked indirectly.

**CORRECTED LATER (EVIDENCE-RISK-DEBT-001, 2026-09-20).** The helper this census
was taken with was defective and has since been replaced. The paragraph above is
kept as the record of what was believed at this revision; it is no longer a
citation of live code. Re-derived with the corrected enumeration - every
halfword-aligned site decoded, `BL` and `BLX` both counted -
`0x08007B78` still has exactly one caller, `0x0800808E`, and `0x08008086` still
has none, so the claim itself is unchanged and now rests on a method that can
find both encodings and resolves `BLX` targets correctly.

### 3.2 `0x08007B78` reads

| Instruction | Read or write | Width |
| --- | --- | --- |
| `08007B92  ldr r0,[pc,#0x2d4]` -> pool `0x08007E68` = `0x08049410` | load the object type word | 4 |
| `08007B94  strb r6,[r4,#4]` | write `object+0x04` | 1 |
| `08007B96  str  r0,[r4]` | **write `object+0x00` = `0x08049410`** (even, ROM data, near the `0x080498B0`/`0x08049548`/`0x08049604` family) | 4 |
| `08007B9C  str  r5,[r4,#8]` | write `object+0x08` = the **record** pointer | 4 |
| `08007BA0..08007BA6 strb r7,[r3..r3+3]`, `r7=0xFF`, `r3=r4+0x20` | write `object+0x20..+0x23` = `0xFF` | 1 x4 |
| `08007BA8  ldr r3,[pc,#0x2c0]` -> pool `0x08007E6C` = `0x08070808` | load the default chunk pointer | 4 |
| `08007BAC..08007BB2 str r3,[r4,#0x10..#0x1C]` | write `object+0x10`,`+0x14`,`+0x18`,`+0x1C` = `0x08070808` | 4 x4 |
| **`08007BB6  ldrsh r7,[r5,r3]`, `r3=0x16`** | **read `record+0x16`** | **2, signed** |
| `08007BBC  str r7,[r4,#0xC]` | write `object+0x0C` = that value | 4 |
| `08007BBE  ldr r5,[r5,#4]` | read `record+0x04` | 4 |
| `08007BC2  str r5,[r0]`, `r0 = object+0x3C` | write `object+0x3C` = `record+0x04` | 4 |
| `08007BC4  ldr r0,[r3,#4]`, `r3 = record+4` | read `record+0x08` | 4 |
| `08007BC8  str r0,[r2]`, `r2 = object+0x40` | write `object+0x40` = `record+0x08` | 4 |
| `08007BCA  ldr r0,[r4,#8]` / `08007BCE adds r0,#0xc` | load the record pointer, offset to `record+0x0C` | - |
| **`08007BD0  ldm r0!,{r2}`** | **read `record+0x0C`..`record+0x0F`** | 4 |
| `08007BD2  str r2,[r1]`, `r1 = object+0x44` | write `object+0x44` | 4 |
| **`08007BD4  ldr r0,[r0]`** | **read `record+0x10`..`record+0x13`** | 4 |
| `08007BD6  str r0,[r6]`, `r6 = object+0x48` | write `object+0x48` | 4 |
| **`08007BDC  ldrb r6,[r0]`, `r0 = record+0x14`** | **read `record+0x14`** | **1, unsigned** |
| **`08007BDE  ldrb r0,[r0,#1]`** | **read `record+0x15`** | **1, unsigned** |
| `08007BE0  muls r6,r0,r6` | product of the two bytes | - |
| `08007BE2  cmp r6,#4` / `08007BE4 bgt` | **skip the chunk loop entirely** when the product exceeds 4 | - |
| `08007BF2  ldr r0,[r0,#0x18]`, `r0 = record + 4*i` | read `record+0x18+4*i` | 4 |
| `08007BFE/08007C04` | `bl 0x0803D940` (the accepted decompressor), destination `object+0x4C+0x800*i` | - |
| `08007CBE  ldr r1,[pc,#0x1ac]` -> pool `0x08007E6C` = `0x08070808`; `str r1,[r2,#0x10]` | write the default chunk pointer when a chunk pointer is null | 4 |

Literal pool values used by the constructor, resolved from each instruction's
own encoding rather than by assumption:

```text
0x08007E68 = 0x08049410   the object+0x00 type word (loaded at 0x08007B92)
0x08007E6C = 0x08070808   default chunk pointer (loaded at 0x08007BA8, 0x08007CBE, 0x08007CF8)
0x08007E70 = 0xFFFFF7E4   loaded at 0x08007C14 (inside the streaming consumer)
0x08007E74 = 0x08071008   second default container pointer
0x08007B6C = 0x00001008   the allocation null test in the 0x08007A60 family
0x08007B70 = 0x08049604   the 0x08007A60 family's own object+0x00 type word
0x08007A5C = 0x08049548   the 0x08007A40 family's object+0x00 type word
0x08008994 = 0x080498B0   the 0x0800897A family's object+0x00 type word
0x08007E64 = 0x0000204C   the allocation size argument (0x08007B84), equal to 4*0x800 + 0x4C
```

**PROJECT OBSERVATION.** Each constructor family writes a *different even
(non-Thumb) ROM data pointer* into the object it builds: `0x08049410`
(`0x08007B78`), `0x08049548` (`0x08007A40`), `0x080498B0` (`0x0800897A`) and
`0x08049604` (`0x08007A60`). **The record's `+0x00` word and the object's `+0x00`
word are different fields holding different kinds of value**: the record's is
odd and Thumb-shaped; the object's is even and data-shaped.

**PROJECT OBSERVATION.** The allocation size `0x204C` loaded at `0x08007B84`
equals `4 * 0x800 + 0x4C`, which independently corroborates the four
`0x800`-byte chunk buffers at `object+0x4C`, `+0x44C`, `+0x84C` and `+0xC4C`.

Two facts follow directly and are the backbone of this ticket:

1. the record's dimension bytes are at **`+0x14` and `+0x15`**, loaded as two
   separate unsigned bytes and multiplied (`0x08007BDC`/`0x08007BDE`/`0x08007BE0`);
2. the chunk-pointer array is read at **`record + 0x18 + 4*i`**
   (`0x08007BF2`), with `i` bounded by that product.

**PROJECT CONCLUSION.** `+0x14` and `+0x15` are **separate 1-byte fields**
read by two distinct `ldrb` instructions and never loaded as a halfword by any
recovered consumer. **CONFIRMED** (instruction access width).

### 3.3 The streaming consumer `0x08007C12`

Called from `0x08007EE4` and `0x08007F9E`. It takes a destination buffer and a
coordinate pair, and:

```text
08007C3A  ldr  r2,[r4,#8]      ; object+0x08 = the record pointer
08007C3C  ldrb r2,[r2,#0x15]   ; record+0x15
08007C3E  cmp  ip,r2 / blt     ; vertical bound
08007C64  ldr  r3,[r4,#8]
08007C66  ldrb r7,[r3,#0x14]   ; record+0x14
08007C6E  str  r7,[r3,#0x18]   ; scratch
08007C70  cmp  r2,r7 / blt     ; horizontal bound
08007C7C..08007C82           ; load the scratch x-count back
08007C82  ldr  r3,[r3,#0x18]   ; chunk pointer array
08007C84  mov  r7,ip
08007C86  muls r7,r3,r7
08007C88  adds r2,r7,r2        ; index = y * X + x
08007C8C  ldr  r6,[pc,#0x1e8]
08007C8E  add  r6,sp,r6
08007C90  str  r2,[r6,r3]      ; install selected chunk id
```

and later, for each of four hardware slots (`0x08007CE0`..`0x08007CF4`), reads
`object+0x20+i` (the per-slot chunk id written at `0x08007BFC`) and
`object+0x4C+0x800*i` (the resident decompressed buffer).

**PROJECT CONCLUSION.** The index formula is `y * (record+0x14) + x`, and the
two bounds are `record+0x15` (vertical, checked first) and `record+0x14`
(horizontal). **`+0x14` is the x-count and `+0x15` is the y-count.**
**CONFIRMED** for the dominant class, from the streaming consumer's own
arithmetic rather than from the renderer's resemblance.

This also independently re-derives the `MAP_RENDER_FORMAT.md` statement that
"a resident logical cell `(x, y)` is stored at `(y & 31) * 32 + (x & 31)`",
which the production renderer `tools/webfoot/map_render.py:322` already
implements as `chunk[block_y * width_blocks + block_x]`.

### 3.4 `+0x0D` / `+0x11`: what the sweep does and does not show

A resynchronising Thumb sweep of `0x08007000..0x08010000` decodes 16,397
instructions and records **2,035** undecodable halfwords. In that region there
are **13 `ldrsb`** sites (`0x0800A99A`, `0x0800BC98`, `0x0800E0DE`, `0x0800EF86`,
`0x0800F0CC`, `0x0800F0EE`, `0x0800F13A`, `0x0800F204`, `0x0800F260`,
`0x0800F2F0`, `0x0800FE3C`, `0x0800FE50`, `0x0800FFFA`), **58 `ldrsh`** sites,
**4** load/store instructions with immediate offset `0x0D`
(`0x0800E7A0`, `0x0800F2FE`, `0x0800FDEC`, `0x0800FE1A`) and **30** with
immediate offset `0x11`.

**This does not establish the absence of a `+0x0D`/`+0x11` consumer.** The
region is a code *and data* span; a linear sweep decodes data as code, so the
47 offset hits are not evidence that any of them reads a layer record, and the
sign of a 2,035-halfword gap cannot be recovered from a sweep of this shape. An
earlier draft of this document claimed "no `ldrsb` at all" and "no offset
`0x0D`/`0x11` load" for this region; **that claim is withdrawn as REFUTED**,
it was based on a sweep whose reported undecodable count (18) corresponds to
roughly the first 0x100 bytes of the documented range, not to the range.

What *is* established about `+0x0D`/`+0x11` is value-level and consumer-level:

* `+0x0D` is 0 on 1458 of 1464 unique records and has five distinct values in
  the whole corpus (0, 4, 32, 40, 249);
* `+0x11` is 0 on 1453 of 1464 and has seven distinct values (0, 4, 40, 128,
  156, 240, 250);
* the whole-image `bl`-caller census of the constructor `0x08007B78`
  (`0x08007BF2` indexes `record+0x18+4*i`) shows the constructor reads only
  `+0x04`, `+0x08`, `+0x0C..+0x13`, `+0x14`, `+0x15`, `+0x16` and
  `+0x18..` of a record - not `+0x0D` or `+0x11`.

**PROJECT CONCLUSION.** LOGExtractor's `+0x0D`/`+0x11` X/Y reading is
**REFUTED at the value level** (both bytes are near-universally zero and neither
is among the fields the one recovered record consumer reads) and
**UNRESOLVED at the instruction level**: this ticket did not re-establish the
absence of a consumer with xref-driven decoding, and it does not claim it. The
`ldrsh`/`ldrsb` picture in this region is likewise **not** claimed as complete.

---

## 4. What `+0x00` actually is

### 4.1 The five values are callable entries

| Value | Entry | Body |
| --- | --- | --- |
| `0x08008087` | `0x08008086` | `adds r2,r1,#0` / `adds r1,r0,#0` / `push {r3,lr}` / `movs r0,#0` / `bl 0x08007B78` / `pop {r3,pc}` |
| `0x0800897B` | `0x0800897A` | `push {r3,r4,r5,lr}` / `adds r4,r0,#0` / `adds r5,r1,#0` / `movs r0,#0xc` / `bl 0x0803D5B8` / if non-null: `strb r4,[r0,#4]`, `str r1,[r0]`, `str r5,[r0,#8]` / return |
| `0x08007A41` | `0x08007A40` | `push {r4,lr}` / `adds r4,r0,#0` / `movs r0,#8` / `bl 0x0803D5B8` / `strb r4,[r0,#4]`, `str r1,[r0]` / return |
| `0x08007B63` | `0x08007B62` | `adds r2,r1,#0` / `adds r1,r0,#0` / `movs r0,#0` / `b 0x08007A60` |
| `0x080088BD` | `0x080088BC` | `push {r3,lr}` / `movs r0,#0` / `bl 0x080080C0` / `pop {r3,pc}` |

`0x0803D5B8` is the same allocator family already recorded by MAP-RENDER as
being called by the `0x08007A40` path. `0x080080C0` has exactly one `bl` caller,
`0x080088C0`.

Three observations matter:

1. **`0x08008086` is a real Thumb function**, and its `bl` target is
   `0x08007B78` (`f7ff fd73` resolves to `0x08007B78` from `0x0800808E`). The
   accepted MAP-RENDER statement "`0x08008086` ... is a five-instruction
   constructor that calls `0x08007B78`" is **reproduced exactly**.
2. **The object built by `0x08007B78` holds `0x08049410` at `object+0x00`**, an
   even ROM data pointer (`0x08007B92` -> pool `0x08007E68`). Each constructor
   family writes a different even pointer there (`0x08049548`, `0x080498B0`,
   `0x08049604`). **This is not the same field or value as the record's
   `+0x00`.** An earlier draft of this document claimed the constructor writes
   `0x08008087` into the object; that claim is **REFUTED**.
3. **`0x08007B62` is a one-instruction tail-branch stub into the
   `0x08007A60` family**, not an independent constructor.

### 4.2 Do records store the entry point, or a type word?

`0x08008087` is `(0x08008086 | 1)`. For the 1420 dominant records the stored
value is exactly the Thumb entry of the constructor that consumes them. For
`0x0800897B` and `0x08007A41` the stored value is the Thumb entry of an
allocator wrapper. The object built by those constructors carries a **different**
word at its own `+0x00`: an even data pointer (`0x08049410`, `0x08049548`,
`0x080498B0`, `0x08049604`), one per constructor family.

**PROJECT CONCLUSION.** `layer+0x00` is **CONFIRMED** as a 4-byte, odd (Thumb-
bit-set), non-4-byte-aligned word that is a valid Thumb code entry for at least
five distinct addresses, three of which are independently disassembled
constructors/allocators. Whether the engine ever *branches* through a record's
`+0x00` is **UNRESOLVED**: no `bl` caller of `0x08008086` exists anywhere in the
image, so the encoding is that of a code pointer but the consumption route was
not recovered. Calling it a "handler" is therefore **PARTIALLY CONFIRMED**; the
previous ticket's claim that it is a Thumb handler pointer is reproduced, and
its status is unchanged, not promoted.

**PROJECT CONCLUSION.** The record's `+0x00` is **not** the object's `+0x00`:
the object field is an even pointer drawn from a small family of nearby data
addresses, one per constructor, while the record field is always odd and always
names a constructor entry. Whether either is a *class identity* is
**UNRESOLVED**. What **is** refuted is the reading "`+0x00` discriminates
between layer classes with different field layouts": the *only* routine
recovered reading the record fields (`0x08007B78`) is shared by 1516 of the
1808 references, and it reads the same offsets regardless of which `+0x00`
word its record carries.

---

## 5. Record layout

### 5.1 Common prefix

Every one of the 1464 unique records read at `+0x00` and `+0x01` shares a
4-byte-aligned base with an odd `+0x00` word. The prefix below is the window
the constructor reads.

```text
+0x00  4  odd word, a valid Thumb code entry (section 4)
+0x04  4  scalar word        (read at 0x08007BBE, copied to object+0x3C)
+0x08  4  scalar word        (read at 0x08007BC4, copied to object+0x40)
+0x0C  4  word, read whole by `ldm r0!,{r2}` at 0x08007BD0; low halfword
          lives at +0x0C, high halfword at +0x0E. Copied to object+0x44
+0x10  4  word, read whole by `ldr r0,[r0]` at 0x08007BD4; low halfword
          lives at +0x10, high halfword at +0x12. Copied to object+0x48
+0x14  1  unsigned byte: x-count of the chunk grid
+0x15  1  unsigned byte: y-count of the chunk grid
+0x16  2  signed halfword, read by `ldrsh` at 0x08007BB6; 0 on 1420/1420
          dominant records, non-zero on 36 records of other +0x00 words
+0x18  4*N pointer window (section 6)
```

Note on `+0x0C` and `+0x10`: the constructor reads **four bytes at `+0x0C`**
(`ldm r0!,{r2}` at `0x08007BD0`, so `+0x0C` and `+0x0E`) and **four bytes at
`+0x10`** (`ldr r0,[r0]` at `0x08007BD4`, so `+0x10` and `+0x12`), copying each
whole word into the object at `+0x44` and `+0x48`. The record's `+0x0C`, `+0x0E`,
`+0x10` and `+0x12` are therefore **consumed**, as two 4-byte words, but by a
path whose own destination (`object+0x44`/`object+0x48`) no further consumer was
recovered for. The separate `ldrsh` read of `+0x16` at `0x08007BB6` is a
different field, copied to `object+0x0C`.

An earlier draft of this document stated that `+0x0C`..`+0x12` had no consumer;
that statement is **REFUTED** by `0x08007BCA`..`0x08007BD6`. Their signedness,
units, origin and any X/Y pairing remain **UNRESOLVED**. The table below is a
*byte-level* census only; it does not imply four independent byte fields.

### 5.2 Byte-field census over the 1464 unique records

| Offset | Distinct values | Min | Max | Most common |
| --- | ---: | ---: | ---: | --- |
| `+0x0C` | 4 | 0 | 204 | 0 x1461 |
| `+0x0D` | 5 | 0 | 249 | 0 x1458 |
| `+0x0E` | 5 | 0 | 41 | 0 x1357, 2 x36, 1 x35, 3 x35 |
| `+0x0F` | 2 | 0 | 8 | 0 x1463 |
| `+0x10` | 2 | 0 | 12 | 0 x1463 |
| `+0x11` | 7 | 0 | 250 | 0 x1453 |
| `+0x12` | 7 | 0 | 255 | 0 x1401, 1 x22, 2 x19, 3 x18 |
| `+0x13` | 3 | 0 | 255 | 0 x1460 |
| `+0x14` | 12 | 0 | 171 | 2 x748, 1 x552, 3 x81, 4 x35, 0 x29 |
| `+0x15` | 15 | 0 | 255 | 1 x735, 2 x624, 3 x43, 4 x21, 254 x13 |

### 5.3 The dominant class (`+0x00` = `0x08008087`, 1420 records)

| Offset | Observed |
| --- | --- |
| `+0x00` | `0x08008087` on all 1420 |
| `+0x04` | 13 distinct values; `0x400` x1368, `0` x16, `0x133` x12, `0x200` x9, `0x66` x3, `0x500` x2, `0x100` x2, `0x651` x2 |
| `+0x08` | 10 distinct values; the same shape as `+0x04` but with 16 nulls and 15 non-`0x400` values |
| `+0x0C`..`+0x13` | **0 on 1419 of 1420** |
| `+0x14` | 1 x552, 2 x748, 3 x81, 4 x35, 5 x4, range 1..5, never 0 |
| `+0x15` | 1 x731, 2 x623, 3 x43, 4 x20, 5 x3, range 1..5, never 0 |
| `+0x16`, `+0x17` | 0 on all 1420 |
| `+0x18` window | first `x_count * y_count` words |

Grid-product histogram (all 1464 records, dominant class inset):

| x*y | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 9 | 10 | 12 | 16 | 20 | larger |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| dominant class | 0 | 380 | 499 | 20 | 402 | 2 | 54 | 14 | 20 | 4 | 10 | 14 | 1 | 0 |

All `x_count * y_count` window words are aligned in-ROM pointers on
**1303 / 1420** dominant-class records. On the remaining 117 the window contains
an internal null before the last expected pointer (section 12).

**PROJECT CONCLUSION.** For the dominant class, `+0x14 * +0x15` is a grid
product and `+0x18` is a pointer array of that many entries.
**CONFIRMED** for the physical array (`0x08007BF2` indexes it by `i < product`)
and **PARTIALLY CONFIRMED** for "no gaps" (117 records have at least one null
before the end).

### 5.4 `MAP_RENDER_FORMAT` cross-check

The accepted production renderer `tools/webfoot/map_render.py:292-293` reads
`rom[record_offset + 0x14]` and `rom[record_offset + 0x15]`, requires both
non-zero or both zero, and treats `(0,0)` as an absent layer. The engine
constructor reads the same two bytes at `0x08007BDC`/`0x08007BDE`.

**29 records** in the census have exactly one dimension byte zero: 29 with
`+0x14` == 0 and 2 with `+0x15` == 0 (the sets overlap in none of the measured
pairs, so 29 is the count of records with exactly one zero byte). The measured
pairs are `(0,2)`, `(0,4)`, `(0,240)`, `(0,246)`, `(0,248)`, `(0,252)`,
`(0,254)` and `(170,0)`. **All 29 are in the `0x0800897B` class**, and the
dominant class has **no** partial-zero record at all.
**CONFIRMED**: the renderer's "partial zero dimensions" refusal cannot fire on
any dominant-class record in the canonical image. An earlier draft said "five
records"; that count was wrong and is corrected here.

---

## 6. The `+0x18` window

### 6.1 Shape

* direct pointer array, not pointer-to-pointer: `0x08007BF2` loads the word and
  passes it straight to the decompressor at `0x08007BFE`/`0x08007C04`;
* element width 4, no element stride beyond 4;
* the array is indexed `record + 0x18 + 4*i` with `i` bounded by the `+0x14 *
  +0x15` product (`0x08007BEC`..`0x08007C0C`);
* the constructor **skips the chunk loop entirely** when the `+0x14 * +0x15`
  product exceeds four (`cmp r6,#4` / `bgt 0x08007C0E` at
  `0x08007BE2`/`0x08007BE4`); it never installs "the first four of a larger
  grid". Any null pointer among the installed entries is replaced by the default
  chunk pointer `0x08070808`, loaded at `0x08007CBE` and `0x08007CF8` from pool
  `0x08007E6C`.

### 6.2 Target type

For the dominant class, when the first product word of the window is non-null
its header word at `+0x04` is `0x800`, the accepted decoded size of one 32x32
regular-BG screenblock, on all but **one** record (`0x082ABF00`, a
`0x080088BD` record whose window is a 136-entry pointer run).

### 6.3 The 0x18-byte element claim

The ticket brief carries a prior correction: "the accepted value where relevant
is `0x18`-byte elements; do not regress to 12-byte wording" and "independently
establish exactly WHICH structure has 0x18-byte elements".

**PROJECT OBSERVATION.** The `0x18`-byte stride in this project's records comes
from the **root** `+0x24`/`+0x28` pair, `LSLS r1,r5,#1` / `ADDS r1,r1,r5` /
`LSLS r1,r1,#3` at `0x08009452..0x08009458` gives `24*i`, and from MapEntry
`+0x28`. Neither is the layer record's `+0x18`. **The layer record's `+0x18`
window is a 4-byte-element pointer array** (`lsls r1,r5,#2` at `0x08007BEE`),
and has nothing to do with a 0x18-byte stride.

**PROJECT OBSERVATION.** The MapEntry `+0x18` pointer array is *not* an
`0x18`-byte-element walk: the site recorded by MAP-RENDER at
`0x08008C0A..0x08008C0E` is `lsls r1,r5,#2` / `ldr r0,[r0,#0x18]` /
`ldr r6,[r0,r1]`, a **4-byte** element stride bounded by the count byte at
MapEntry `+0x05`. An earlier draft of this document cited that site as
supporting a MapEntry `0x18`-byte stride; that citation is **REFUTED**.

**PROJECT CONCLUSION.** Applying an `0x18`-byte element stride to a layer
record's `+0x18` window is **REFUTED**. The `0x18`-byte stride in this project
is **CONFIRMED** for root `+0x28` and **not** established for MapEntry `+0x18`
from the site examined here.

---

## 7. What the LOGExtractor hypotheses map onto

**EXTERNAL CLAIM (LOGExtractor).** Two layer forms, discriminated by the first
word:
* `0x0800897B` = single-image/chunk-like layer using `+0x1C` as a content
  pointer;
* `0x08008087` = chunk-grid layer using `+0x0D` and `+0x11` as X/Y offsets,
  `+0x14`/`+0x15` as chunk column/row counts and `+0x18` as container data.

**PROJECT OBSERVATION.**

| LOGExtractor reading | Independent result |
| --- | --- |
| `+0x00` discriminates two layer forms | five distinct constructor/allocator entries; the field is a code pointer, and the only recovered record reader is shared by 1516/1808 references |
| `+0x0D` is an X offset | `+0x0D` is 0 on 1458/1464 records, is not among the fields the one recovered record consumer reads, and no consumer was positively identified (section 3.4) |
| `+0x11` is a Y offset | `+0x11` is 0 on 1453/1464 records, is not among the fields the one recovered record consumer reads, and no consumer was positively identified (section 3.4) |
| `+0x14` chunk-column count | **confirmed**, independently (section 3.3) |
| `+0x15` chunk-row count | **confirmed**, independently (section 3.3) |
| `+0x18` container data | confirmed as a 4-byte-element pointer array of screenblock containers |
| `+0x1C` content pointer for the other form | **refuted as a general field**: `+0x1C` is an ordinary word inside the `+0x18` pointer window (word index 1) for the dominant class. For `0x0800897B` records the layout is different and no content pointer at `+0x1C` was recovered |

**PROJECT CONCLUSION.** LOGExtractor's `+0x14`/`+0x15` and `+0x18` readings are
**CONFIRMED**. Its `+0x0D`/`+0x11` readings are **REFUTED at the value level**
for the canonical image: those bytes are almost universally zero and neither is
among the seven fields the one recovered record consumer reads. The stronger
"no consumer exists" form is **UNRESOLVED** (section 3.4). If LOGExtractor reads
the bytes as signed offsets at all, it is either reading a different object, a
different revision, or an object-addressing variant not present in this image.
**No signed coordinate transform was found in the engine**, so this ticket
imports none (see section 8).

---

## 8. Position semantics: what is established and what is not

The brief's high-priority correction area.

| Question | Result |
| --- | --- |
| Exact physical offsets of position-like fields | `+0x0C` and `+0x0E` form one 4-byte word read at `0x08007BD0`; `+0x10` and `+0x12` form a second 4-byte word read at `0x08007BD4`; `+0x16` is a signed halfword (0 on 1420 records) |
| Field widths | `ldrsh` for `+0x16` at `0x08007BB6` (2 bytes, signed). `+0x0C..+0x13` are consumed as two 4-byte words, so reading them as four halfwords is an interpretation this ticket does not promote. Signedness is **UNRESOLVED** for all of them |
| Are X/Y actually paired? | **UNRESOLVED.** Two 4-byte words at `+0x0C` and `+0x10` admit an (x0,y0,x1,y1) reading, but nothing recovered consumes `object+0x44`/`object+0x48`, so the pairing is **not** promoted |
| Pixels, tiles, chunks, scroll, parallax, clip, origin? | **UNRESOLVED.** The only signed record field with a consumer (`+0x16`) is 0 in all 1420 dominant records, so even its arithmetic could not be exercised |
| Negated or transformed? | **UNRESOLVED** |
| Do classes differ? | Yes for `+0x16`: 0 on all dominant records, non-zero on 36 records of other `+0x00` words, including `-1` on 34 `0x0800897B` records |
| `ldrsb` vs `ldrb` | The record-level picture is that `+0x14`/`+0x15` are `ldrb` and `+0x16` is `ldrsh` (`0x08007BB6`). The region-wide `ldrsb`/`ldrsh` census is **not** claimed: 2,035 of the region's halfwords do not decode, so no absence claim is made (section 3.4) |
| LOGExtractor's negative-coordinate hack | **Not reproduced.** Nothing in this ticket supports a sign correction, and no unexplained constant is introduced to match a screenshot |

**PROJECT CONCLUSION.** Layer positioning is **UNRESOLVED**. The ticket does
*not* hand LOGX-TILE-001 or any other ticket a position transform, because none
was established. Any downstream consumer that needs a layer origin must derive
it from its own evidence.

---

## 9. Re-test of the accepted MAP-RENDER layer claims

| Accepted claim | Re-test result |
| --- | --- |
| "A non-empty proven record has handler `0x08008087`, width and height in 32x32 chunks at bytes `+0x14`/`+0x15`" | **CONFIRMED** (sections 3.2, 3.3, 5.3) |
| "a row-major u32 container array at `+0x18`" | array at `+0x18` **CONFIRMED**; "row-major" **PARTIALLY CONFIRMED** - the index is `y * x_count + x` at `0x08007C86`, which is row-major, but 117 dominant-class records have an internal null inside the first `x*y` words |
| "Every container decodes to `0x800` bytes" | **CONFIRMED** for every dominant-class record whose first window word is non-null, except `0x082ABF00` |
| "A zero-by-zero record is an absent layer" | **CONFIRMED** - `0x080707FC` is the only record with a fully null `+0x18` window and 249 references |
| "constructor `0x08007BDE..0x08007C08` multiplies the record's `+0x14/+0x15`" | **CONFIRMED**; the two loads are at `0x08007BDC`/`0x08007BDE` and the multiply at `0x08007BE0` |
| "reads container pointers at `+0x18 + 4*i`" | **CONFIRMED** at `0x08007BF2` |
| "decompresses up to four resident chunks to 0x800-spaced EWRAM buffers" | **PARTIALLY CONFIRMED**: the source pointer is ROM-resident (`0x08007BF2` loads `record+0x18+4*i` and passes it to `0x0803D940`); the destination is `object + 0x4C + 0x800*i` (`0x08007BFE..0x08007C02`), and the four-slot cap is `cmp r6,#4` at `0x08007BE2` |
| "`0x08007C82..0x08007C90` computes chunk index `y * width + x`" | **CONFIRMED** |
| "98 roots point the `+0x14` slot at the shared `0x080707FC` record" | **CONFIRMED** exactly (98 references of `0x08007A41` at slot `+0x14`; 249 total across all slots) |

---

## 10. Root slot to hardware BG identity

**PROJECT OBSERVATION.** `root+0x04..+0x07` are four bytes added to
`BG0CNT..BG3CNT` in slot order at `0x080093E0..0x08009406` (accepted). The census
shows all four slots are always populated (0 nulls), so there is no
data-driven "this slot is disabled" encoding at the root level: an unused layer
is a zero-dimension record, not a null slot.

No instruction was recovered in this ticket that assigns a root slot index to a
hardware BG number other than that byte-order correspondence.

**PROJECT CONCLUSION.** "Four root slots hold four non-null layer pointers" is
**CONFIRMED**. "Root slot *n* is BG *n*" remains **PARTIALLY CONFIRMED**,
unchanged from MAP-RENDER: the slot-order correspondence to the four
`BGxCNT` registers is strong but the per-slot assignment is still inferred from
byte order rather than shown by a direct per-slot register write. This ticket
adds one more observation in favour of it: the dominant class's grid product
never exceeds 20 and the four installed slots are indexed `object+0x20+i` for
`i < 4` (`0x08007CF0`/`0x08007CF4`), i.e. the engine itself carries exactly four
per-layer slots.

---

## 11. Other `+0x00` values

Beyond `0x08008087` and `0x0800897B`, three further values occur in the census.
None is a silently-classified variant; each is reported with its proven
provenance.

| Value | Records | References | Provenance |
| --- | ---: | ---: | --- |
| `0x08007A41` | 1 | 249 | The zero-dimension placeholder `0x080707FC`. Its entry `0x08007A40` is an 8-byte allocator (`movs r0,#8`, `bl 0x0803D5B8`, `strb r4,[r0,#4]`, `str r1,[r0]`). MAP-RENDER already records it as reached with `(0,0)` from `0x0800923E`. All 249 references resolve to the same single record, so this is one shared object, not a class |
| `0x08007B63` | 1 | 1 | Entry `0x08007B62` is `adds r2,r1,#0` / `adds r1,r0,#0` / `movs r0,#0` / `b 0x08007A60`: a **tail-branch stub into the `0x08007A60` allocator family**. The single record is `0x0829F808` on map 19 slot `+0x18`, with `+0x14`/`+0x15` = 64/192 and `+0x04` = `+0x08` = `0x0829F700`. **PARTIALLY CONFIRMED** as a layer record: it shares the prefix shape but its grid product is 12288, far beyond the four-slot cap, so it is not a dominant-class chunk-grid layer and no consumer was recovered |
| `0x080088BD` | 1 | 1 | Entry `0x080088BC` is `push {r3,lr}` / `movs r0,#0` / `bl 0x080080C0` / `pop {r3,pc}`. The single record is `0x082ABF00` on map 19 slot `+0x1C`, whose `+0x18` window is a 136-entry run of aligned in-ROM pointers whose first entries decode to `0x400`-byte containers. **UNRESOLVED** as a layer record; recorded in the provenance but not classified into either external form |

**PROJECT CONCLUSION.** The layer-record family that the four root slots point
at is **not** uniform. `0x08008087` (1420 records / 1516 references) and
`0x0800897B` (41/41) dominate; the three remaining values account for 251
references but only 3 distinct records, and one of those (`0x08007A41`) is a
single shared placeholder. Full semantic reconstruction of `0x08007B63` and
`0x080088BD` is deferred; they are **not** assigned to either LOGExtractor form.

### 11.1 The `0x0800897B` class

**PROJECT OBSERVATION.** 41 records, all referenced exactly once, in slots
`+0x14` (5), `+0x18` (1), `+0x1C` (11) and `+0x20` (24). Common shape:

```text
+0x00  0x0800897B
+0x04  equals +0x08 on 40/41 records (0x400, 0x266, 0x199, 0x533, 0x2CC, 0x200)
+0x08  see above
+0x0C  0
+0x0E  0
+0x10  0
+0x12  0
+0x14  0 on 29/41; otherwise 85, 86, 170, 171
+0x15  240..255 on most; 0, 1, 2, 4 on the rest
+0x16  -1 on 34/41, 0 on the rest (a signed halfword read by some consumer as yet unrecovered)
+0x18  window: 38 of the 41 records have a null first window word
```

The `+0x14`/`+0x15` pair is **not** usable as an x/y grid count for this class:
29 of the 41 have a zero product, the non-zero products are 85, 21930, 41382,
43434 and 43605, and **no** record's first `x*y` window words are all aligned
in-ROM pointers.

**PROJECT CONCLUSION.** `0x0800897B` is a **materially different** record
representation from `0x08008087`, not a variant with different dimensions.
The external "single image / single-chunk layer" reading is **PARTIALLY
CONFIRMED** only in the weak sense that this class does not have the dominant
class's chunk-pointer array; its `+0x1C` was **not** shown to be a content
pointer. Its entry `0x0800897A` allocates via `0x0803D5B8` and stores two
arguments, which is an allocator-wrapper shape, not a rendering routine.

---

## 12. Anomalies

| Anomaly | Count | Examples |
| --- | ---: | --- |
| `+0x18` window has an internal null within the first `x*y` words (dominant class) | 117 | `0x082B8BC8` (x=1,y=5, word 0 null, words 1..4 non-null) |
| the same anomaly over all 1464 records | 127 | - |
| window word 0 null (all records) | 52 | - |
| window word non-null but not 4-aligned in-ROM | 13 | `0x0824DB1C`, `0x082505D8` |
| `+0x18` window is entirely null | 1 | `0x080707FC` (the absent-layer placeholder) |
| First window word's header `+0x04` is not `0x800` | 1 | `0x082ABF00` |
| Grid product is 0 (one dimension byte zero) | 30 | 29 of them in the `0x0800897B` class, 1 is `0x080707FC` |
| `+0x0E` non-zero | 107 | `0x08187ED4` |
| `+0x12` non-zero | 63 | `0x0818E718` |
| `+0x16` non-zero | 36 | `0x081B2C9C`, `0x081F6F7C` (`-1`) |
| `+0x16`/`+0x17` non-zero | 35 / 36 | same set |
| Dominant-class record with `+0x04` != `0x400` | 52 of 1420 | `0x082B84D0` (`0x651`), `0x082B891C` (`0x2CC`) |
| Record with exactly one dimension byte zero | 29 | all in the `0x0800897B` class |
| Dominant-class record with `+0x04` == 0 | 16 | - |

**Window-analysis bound.** The `+0x18` window is inspected for its first
`POINTER_WINDOW_WORDS = 16` words (`tools/research/logx_layer_probe.py`). A
record whose `x*y` product exceeds 16 is therefore judged on a truncated window.
The only such records are the single product-20 dominant record and the two
large singletons.

The `+0x04`/`+0x08` words are **not** constant across the dominant class, and
the constructor copies them into the object at `object+0x3C` and `object+0x40`
(`0x08007BBE`..`0x08007BC8`). Their meaning is **UNRESOLVED**; the only
structural statement this ticket makes is that they are 4-byte scalar words.

### 12.1 The `0x08007A60` allocator family

Reached from `0x08007B63` (tail branch at `0x08007B68`). Recovered head:

```text
08007A60  push {r3,r4,r5,r6,r7,lr}
08007A62  adds r6,r2,#0        ; r6 = third argument
08007A64  adds r5,r0,#0        ; r5 = object
08007A66  adds r4,r1,#0        ; r4 = second argument
08007A68  cmp  r0,#0
08007A6A  bne  0x08007A7A
08007A6C  ldr  r0,[pc,#0xfc]   ; pool 0x08007B6C = 0x00001008
08007A72  adds r5,r0,#0        ; substitute a fixed default base
08007A7A  strb r4,[r5,#4]
08007A7C  ldr  r0,[pc,#0xf0]   ; pool 0x08007B70 = 0x08049604
08007A84  str  r0,[r5]         ; object+0x00 = 0x08049604
08007A86..08007AAE            ; two-iteration loop (cmp r4,#2 at 0x08007AAC)
08007AB0  adds r0,r5,#0
```

The two iterations index a base taken from the record and decompress through
`0x0803D5B8` (the same allocator entry the `0x08007A40` and `0x0800897B`
wrappers use). This ticket did **not** fully reconstruct this family; it is
recorded because `0x08007B63` reaches it, because its `+0x00` type word is
`0x08049604`, a **different** code site from any of the five census values,
and because its loop bound of two is hard-coded, which is direct evidence that
this family's object carries **two** chunk buffers while the `0x08007B78`
family's carries **four** (`object+0x4C + 0x800*i`, `i < 4`).

**Consequence for the census.** The five `+0x00` values are drawn from at least
two distinct constructor vocabularies. `0x08049604` never appears as a layer
record's `+0x00` word in the canonical census, so the `0x08007A60` family is
not simply "another layer class"; the only record that reaches it
(`0x0829F808`, via the `0x08007B63` tail branch) is already flagged
**PARTIALLY CONFIRMED** in section 11.

---

## 13. The standalone scan

Scanning `0x08100000..0x08400000` for each `+0x00` word as a 4-aligned
little-endian word:

| Word | Aligned hits | Used as a record address | Not used as a record |
| --- | ---: | ---: | ---: |
| `0x08008087` | 1439 | 1420 | 19 |
| `0x0800897B` | 41 | 41 | 0 |
| `0x08007B63` | 1 | 1 | 0 |
| `0x080088BD` | 1 | 1 | 0 |
| `0x08007A41` | 0 | 0 | 0 (the one record `0x080707FC` lies below `0x08100000`) |

**PROJECT OBSERVATION.** 19 additional records carrying `0x08008087` exist in
the image but are not reachable from any selector-1 root slot. Their measured
addresses are `0x08220804`, `0x08220EEC`, `0x08221418`, `0x08221884`,
`0x0822F674`, `0x0822F748`, `0x0822FB10`, `0x0823048C`, `0x0823275C`,
`0x08232C30`, `0x0824A1CC`, `0x0824A2A8`, `0x0824A8C8`, `0x0824AC58`,
`0x0826512C`, `0x0826561C`, `0x082659D4`, `0x08265F74` and `0x082B608C`. They
sit **inside** the referenced set's address range, interleaved with referenced
records, and have the same dominant-class shape (for example `0x08220804` has
`+0x14`/`+0x15` = 2/2 and four aligned in-ROM pointers at `+0x18`).

**PROJECT CONCLUSION.** The layer-record family is larger than what the
selector-1 roots reference, and the unreferenced members are not a distinct
region, they are interleaved with referenced records. They are therefore most
likely reachable through other selector variants of `MapEntry+0x2C`
(`LOGX-MAP-RENDER-001` left "does any executable path pass a selector other
than 1" unresolved), which is **UNRESOLVED** here and is recorded as a handoff.

---

## 14. Disagreements with the prior ticket

| Prior statement | This ticket |
| --- | --- |
| "`0x08008086` is a five-instruction constructor that calls `0x08007B78`" | reproduced exactly (`bl f7ff fd73` -> `0x08007B78`) |
| "`0x08007A40` is the 8-byte absent-layer allocator; called with `(0,0)` at `0x0800923E` it returns `0x080707FC`" | reproduced (`movs r0,#8`; the call site is a `bl` from `0x0800923E`) |
| "`0x08007B78` ... stores the passed chunk pointer at `object+0x08`" | the constructor stores `r5`, the **record** pointer, at `object+0x08` (`0x08007B9C`), and reads chunks through it later. The phrase "passed chunk pointer" reads as the record pointer in the calling convention this ticket reproduced |
| "`0x080088BD` is a layer handler" | its entry calls `0x080080C0` with `r0 = 0`; the record is recorded but not classified |
| "`+0x18` is a container-pointer array" | **CONFIRMED**, and now shown to be read at `record+0x18+4*i` with `i` bounded by `+0x14 * +0x15` |

---

## 15. Unresolved questions

1. **Position fields.** `+0x0C`..`+0x13` are consumed as two 4-byte words and
   copied to `object+0x44`/`object+0x48`, but nothing recovered consumes those
   object fields. Their signedness, units, origin and pairing are unresolved.
2. **`+0x16`.** One record field is read with `ldrsh` and stored at
   `object+0x0C`. It is 0 in every dominant record, so its arithmetic could not
   be exercised. What consumes `object+0x0C`?
3. **The four-slot cap versus products above four.** `cmp r6,#4` / `bgt` at
   `0x08007BE2`/`0x08007BE4` makes the constructor **skip** the chunk loop when
   the product exceeds four, yet 133 of the 1464 records have a grid product
   above four (up to 20 in the dominant class). Either a second installer path
   exists for larger grids, or the product is not the installer's bound.
   **UNRESOLVED.**
4. **`+0x1C` per class.** For the dominant class `+0x1C` is word index 1 of the
   `+0x18` window. LOGExtractor's "content pointer" reading was not reproduced
   for any class.
5. **Class multiplicity.** `0x08007B63` and `0x080088BD` occur once each. Their
   semantic reconstruction is deferred.
6. **The 19 unreferenced dominant-shape records** (section 13): which selector
   reaches them?
7. **Shared records.** Why do ten maps share one three-layer stack? Is that a
   ROM-builder deduplication or intentional reuse?
8. **`+0x04` / `+0x08` semantics.** They vary (13 and 10 distinct values in the
   dominant class) and are copied wholesale into the object.
9. **Interior nulls in the `+0x18` window** (117 dominant / 127 corpus). Whether
   the engine treats a null chunk pointer as "skip" or "default" was only partly
   recovered: the constructor substitutes a default pointer when it *installs*
   (`0x08007CBE`), but the streaming consumer at `0x08007CE0` tests the object
   slot byte, not the record word. Note also that the constructor skips the loop
   for products above four, so for those records neither behaviour was observed.

---

## 16. Handoffs

| Ticket | Handoff |
| --- | --- |
| **LOGX-TILE-001** | A dominant-class layer record's chunk container is addressed `record + 0x18 + 4*i` for `i < record[+0x14] * record[+0x15]`; the container decodes to `0x800` bytes = 1024 little-endian u16 screen entries; the container is decompressed by `0x0803D940` (`0x08007BFE`, `0x08007C04`). The record's `+0x14` is the x-count and `+0x15` the y-count (`0x08007C86`). **Do not** look for a position, flip or palette meaning in the record itself; the tile-level bitfields live in the 0x800-byte payload, which is yours. |
| **LOGX-CONNECTOR-001** | Nothing in this ticket changes the root `+0x40`/`+0x44` handoff. The `0x18`-byte element stride is **CONFIRMED for root `+0x24`/`+0x28` only**; the MapEntry `+0x18` pointer array examined here uses a 4-byte stride, so do not cite it as the `0x18`-byte site. It is **not** a layer-record stride (section 6.3). |
| **LOGX-CODEC-001** | The constructor calls the same decompressor `0x0803D940` for every non-null chunk pointer at `0x08007BFE`/`0x08007C04`, with destination `object + 0x4C + 0x800*i`. The allocator wrapper family is `0x0803D5B8` (called from `0x08007A6E`, `0x08008982`). |
| **LOGX-CHAR-001 / LOGX-SPRITE-001** | Not addressed by this ticket. |
| **Any consumer needing layer position** | Layer positioning is **UNRESOLVED** (section 8). Do not import a coordinate transform from LOGExtractor; none is supported by engine evidence here. |

---

## 17. Reproduction

```powershell
# full census (JSON)
python -m tools.research.logx_layer_probe "<canonical rom>" --references --layers > build\layer_census.json

# per-reference CSV
python -m tools.research.logx_layer_probe "<canonical rom>" --csv build\layer_census.csv

# focused ROM-gated tests (skip cleanly when the private ROM is absent)
python -m pytest tests/integration/test_logx_layer_rom.py
```

Critical instruction sites, for re-derivation:

```text
0800808A..08008092  the 0x08008087 wrapper: bl 0x08007B78
08007B78..08007C10  the layer-object constructor
08007B92            ldr r0,[pc,#0x2d4]  (pool 0x08007E68 = 0x08049410 -> object+0x00)
08007BA8            ldr r3,[pc,#0x2c0]  (pool 0x08007E6C = 0x08070808, default chunk pointer)
08007BB6            ldrsh r7,[r5,#0x16]  (record+0x16, signed)
08007BBE/08007BC4   ldr                 (record+0x04 / record+0x08)
08007BD0/08007BD4   ldm / ldr           (record+0x0C..+0x0F / record+0x10..+0x13)
08007BDC/08007BDE   ldrb                (record+0x14 / record+0x15)
08007BE0            muls r6,r0,r6       (record+0x14 * record+0x15)
08007BE2            cmp  r6,#4          (skip the chunk loop above four)
08007BEE            lsls r1,r5,#2       (4-byte element stride)
08007BF2            ldr  r0,[r0,#0x18]  (chunk pointer array)
08007C12..08007E62  the streaming consumer; index = y * x_count + x at 08007C86
0800897A..08008992  the 0x0800897B allocator wrapper
08007A60..08007AB2  the 0x08007A60 allocator/constructor family
08007A40..08007A54  the 8-byte placeholder allocator
080088BC..080088C4  the 0x080088BD entry (bl 0x080080C0)
```
