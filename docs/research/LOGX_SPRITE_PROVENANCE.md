# LOGX-SPRITE-001 provenance: Buu's Fury sprite-definition and animation-table structure

Research record for LOGX-SPRITE-001. Status labels are those of
[`../research-conventions.md`](../research-conventions.md): `CONFIRMED`,
`INFERRED`, `UNKNOWN`. The document keeps three voices apart on purpose:

* **EXTERNAL CLAIM** - what `mainant/LOGExtractor` states, quoted as a claim
  under test. Nothing here inherits an upstream field name.
* **PROJECT OBSERVATION** - a number or byte string this ticket read out of the
  canonical image, reproducible with
  `python -m tools.research.logx_sprite_probe <rom>`.
* **PROJECT CONCLUSION** - what the observations and the engine's own
  instructions jointly establish, with the strength stated.

**Canonical profile.** SHA-256
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`,
8,388,608 bytes, read-only throughout. Addresses are GBA addresses; a file
offset is an address minus `0x08000000`. Every headline number below states its
population.

**Accepted dependencies, reused and not re-opened.**

| Source | What is reused |
| --- | --- |
| LOGX-CHAR-001 | the 232-record appearance table at `0x0874D380`, its `+0x04` id field, the accessor `0x08000158` and the folded `-0x28`, and the accepted 297-entry run at `0x086B6BDC` |
| TOOLKIT-010 / [`GRAPHICS_FORMAT.md`](GRAPHICS_FORMAT.md) | the chain *character structure -> animation record -> frame record -> piece record* and its corpus figures, which this ticket tests for consistency |
| TOOLKIT-004 | the text pointer table, used only through LOGX-CHAR-001 |

---

## 1. EXTERNAL CLAIMS AND THEIR VERDICTS

`mainant/LOGExtractor`, `src/sprite_analysis.cpp` (per
[`GRAPHICS_FORMAT.md`](GRAPHICS_FORMAT.md) §1), is recorded as assuming:

1. each resolved sprite-definition object has a **byte animation count at
   `+0x00`**;
2. its **animation-pointer array begins at `+0x54`**;
3. animation positions carry **fixed semantic meanings** for 23 named slots
   (`1 stand`, `2 walk`, `3 run`, `4..7 attack1..4`, `8 block`, `9 idle`,
   `10 hurt`, `11 transform`, `12 unknown1`, `13 arms_up`, `14 pickup`,
   `15 takeoff`, `16 flying`, `17 mode7_fly`, `18 dead`, `19 special`,
   `20 teleport`, `21 unknown4`, `22 fusion`, `23 unknown5`);
4. the pointer table's base is file offset `0x6B6BB4`;
5. an animation record leads with a `u32` frame count, transformed by a
   `value << 2` relationship.

| External claim | Verdict |
| --- | --- |
| 1. byte animation count at `+0x00` | **CONFIRMED** as a count, with the width and the consumers measured (§4) |
| 2. array begins at `+0x54` | **CONFIRMED** (§5) |
| 3. fixed positional semantic slots | **PARTIALLY CONFIRMED**: fixed positional slots exist (§8); the *names* are **mostly UNRESOLVED** (§9) |
| 4. base is `0x6B6BB4` | **REFUTED as a run base, EXPLAINED as the accessor's fold**: `0x086B6BB4` is the last definition object's own inline array, and the accepted 297-entry run begins 40 bytes higher (§2) |
| 5. animation-leading `u32` and `value << 2` | **PARTIALLY CONFIRMED**: the leading word is the animation's frame count and the engine indexes it with `<< 4` and `<< 2`; the `<< 2` reading (`count * 4` = the number of frame pointers) is consistent with the flat layout, but the interpretation of the *frames* is handed to LOGX-FRAME-001 (§10) |

---

## 2. PROJECT CONCLUSION: THE POINTER RUN AND THE FOLDED BASE

**SPRITE POINTER RUN START: CONFIRMED**, GBA `0x086B6BDC` / file `0x6B6BDC`.
**SPRITE POINTER RUN COUNT: CONFIRMED**, 297 entries.
**SPRITE POINTER RUN SEMANTIC IDENTITY: CONFIRMED** as *the definition-pointer
array the `+0x04` accessor indexes*; described by structure below.

PROJECT OBSERVATION (`--run`):

* 297 entries at `0x086B6BDC .. 0x086B707C`; **297 unique targets**, no exact
  duplicates, no sharing at the pointer level; all in ROM; strictly ascending.
* first entry `0x086A89D0`, last entry `0x086B6B60`.
* the word after the last entry is `0x03001068` at `0x086B7080`, an IWRAM
  address, so it is not part of the run.
* the run's literal `0x086B6BDC` occurs as a pool word at exactly two sites,
  `0x080003C0` (loaded at `0x0800015E`) and `0x0801715C` (loaded at
  `0x0801713E`). No other `ldr Rt,[pc,#imm]` in the whole image can reach it.

### 2.1 The id space, and what the folded base really is

The accessor `0x08000158` computes, for `id >= 10`,
`address = 0x086B6BDC + 4*id - 0x28 = 0x086B6BB4 + 4*id`. So id 10 is run index
0 and id 306 is run index 296.

PROJECT OBSERVATION: the ten words the folded base reaches for ids `0..9`,
`0x086B6BB4 .. 0x086B6BD8`, are

```text
0x086A6424, 0x086A7238, 0, 0, 0x086A7E7C, 0, 0, 0, 0, 0x086A899C
```

four ascending ROM pointers and six nulls. LOGX-CHAR-001 left the semantic
identity of the run's first entry UNRESOLVED and recorded a disagreement with
LOGExtractor about whether `0x086B6BB4` or `0x086B6BDC` is the array's first
byte.

**PROJECT CONCLUSION: the folded base is not an array prefix at all. It is the
inline animation array of the definition object at `0x086B6B60`, which is the
run's *last* entry (id 306).** The evidence is arithmetic and needs no
interpretation:

* the object at `0x086B6B60` declares count `10` (`0x08027390`-style header
  `0a000004`, low byte `0x0A`);
* its inline array occupies `0x086B6B60 + 0x54 .. + 0x54 + 4*10`, i.e.
  `0x086B6BB4 .. 0x086B6BDC`;
* `0x086B6BDC` is exactly where the 297-entry run begins.

So the ten words are that object's own ten animation pointers, ids `0..9` are
never array indices (the accessor branches at `cmp r0,#0xa`), and the run's
index 0 has no special meaning beyond being id 10. `probe.folded_base_explanation`
re-derives this by scanning the words below the run for a definition header whose
count lands the object exactly on the run; exactly one candidate is found.

**FIRST POINTER-RUN ENTRY: RESOLVED.** Ids `0..9` are party-slot selectors, not
array indices (§3), so the run's first entry is simply id 10 and the id-to-index
mapping is `index = id - 10` over `10..306`. Nothing in the canonical image makes
run index 0 semantically distinct.

### 2.2 Pointer-run boundary

The engine exposes **no count and no range check** for the run: the accessor is
`push {r4,lr} / cmp r0,#0xa / blt / ldr / lsls / adds / subs / ldr / pop`, with
no comparison against 297 or 307 anywhere. The boundary is therefore
data-and-consumer bounded, not engine bounded:

* the run is the largest contiguous strictly ascending ROM-pointer run
  beginning at `0x086B6BDC`; the next word is not a ROM address;
* every id the canonical image derives (§3, §11) falls in `12..306`, i.e. run
  indices `2..296`, and every one resolves to a valid ROM pointer.

A count/range claim for the run is **UNRESOLVED as an engine fact** and is made
here only as a measured extent. `probe.DEFINITION_ARRAY_ENTRY_COUNT` is labelled
as such.

---

## 3. ENGINE CONSUMERS

### 3.1 The two accessors

PROJECT OBSERVATION, instructions re-read by the ROM-gated suite:

```text
0x08000158  push {r4, lr}
0x0800015A  cmp  r0, #0xa
0x0800015C  blt  #0x800016a
0x0800015E  ldr  r1, [pc, #0x260]   ; pool 0x080003C0 = 0x086B6BDC
0x08000160  lsls r0, r0, #2
0x08000162  adds r0, r0, r1
0x08000164  subs r0, #0x40
0x08000166  ldr  r0, [r0, #0x18]    ; = u32 at 0x086B6BB4 + 4*id
0x08000168  pop  {r4, pc}
```

`0x0800016A .. 0x080001C4` is the party branch. It resolves a party slot
(`0`, `1..8`, or `9`) to a live object, takes a pointer from `0x08054FBC + 0x14`,
indexes a 24-byte-record table at `0x086B82EC` by a byte of that record
(`0x08000182`..`0x08000196`: `0x68 * byte`, `+0x4F8`, `+0x14`, `*24`) and calls
`0x0801713C` with the result. Spot-check of that table: records 0..11 at
`0x086B82EC` carry `u16 +0x0E` = `115, 116, 117, 118, 119, 120, 121, 121, 120,
106, 107, 108`, all at or above the floor.

```text
0x0801713C  ldrh r0, [r0, #0xe]     ; id from the record
0x0801713E  ldr  r1, [pc, #0x1c]    ; pool 0x0801715C = 0x086B6BDC
0x08017140  lsls r0, r0, #2
0x08017142  adds r0, r0, r1
0x08017144  subs r0, #0x40
0x08017146  ldr  r0, [r0, #0x18]
```

**PROJECT CONCLUSION.** `0x0801713C` is a second entry to the same array with
the identical arithmetic and **no party branch**. It is the path by which ids
below the floor could reach the folded base; in the canonical image it is fed
only ids at or above the floor, so the ten words §2.1 identifies are never read
as definition pointers.

### 3.2 What consumes a definition

`0x08027390` is the constructor path that turns an appearance record into a live
object, and it is a `BL` caller of both the accessor (`0x080273B4`) and the
character constructor:

```text
0x080273AA  ldr  r0, [r5]           ; appearance id
0x080273AC  ldr  r1, [pc, #0xc4]    ; = 0x0874D380
0x080273AE  lsls r0, r0, #4
0x080273B0  adds r0, r0, r1
0x080273B2  ldr  r0, [r0, #4]       ; the appearance's +0x04 id
0x080273B4  bl   #0x8000158         ; -> definition pointer
0x080273BE  bl   #0x800eb60         ; ctor(obj, definition, 0x03001b0c)
```

`0x0800EB60(obj, definition, class)` is the consumer this ticket read in full.
It stores the definition at `obj + 0x58`, and it reads definition fields
`+0x00`, `+0x02`, `+0x04`, `+0x08`, `+0x0A`, `+0x0B`, `+0x50` and `+0x54`. The
only reader of `definition + 0x54` in the image is the `ldr r0,[r6,#0x54]` at
`0x0800EBD0`; no other accessor caller and no base-class or
`0x0804CEB8`-class method reads it.

Fields the constructor installs on the object (all `CONFIRMED` as reads):

| Definition field | Instruction | Object field | Role observed |
| --- | --- | --- | --- |
| `+0x02` (`u16`) | `0x0800EB7C ldrh r5,[r6,#2]` | `+0x0E` | copied, then passed to `0x0801124C` |
| `+0x02` (`u16`) | `0x0800EC00 ldrh r0,[r0,#2]` | `+0x40` | handed to the byte allocator `0x0803D5B8` |
| `+0x04` (`u32`) | `0x0800EBF6 ldr r1,[r0,#4]` | `+0x34`, `+0x3C` | a pointer |
| `+0x08` byte `+0x0A`, `+0x0B` | `0x0800EC0A`, `0x0800EC0C` | `+0x5C` | a pair handed to `0x08013E38` |
| `+0x50` (`u32`) | `0x0800EBB6` | `+0x4C` (via `*def[0x50]`) | gates a fixed `0x80`-byte ROM block copy |
| `+0x54` (`u32`) | `0x0800EBD0` | `+0x50` | the animation base (§7) |

`0x0800EDF8(obj, new_definition)` is the re-skin/transform entry: it frees the
old `+0x40` buffer when `+0x02` changes, re-allocates, and re-copies `+0x04`.
It is called directly from 41 sites, all inside the "is this character sprite X?
then become sprite Y" chains (§8.4).

### 3.3 Dispatch shape

`obj + 0x00` holds a class pointer (`0x0804AC20` from the constructor,
`0x0804CEB8` from `0x08027390`) and methods are stored as offsets from it,
dispatched through `0x08046AA4`:

```text
ldr r1, [obj]        ; class
ldr r2, [r1, #0x28]  ; method offset
adds r2, r2, r1
bl  0x08046AA4
```

`0x0804AC20 + 0x28` is `0x0800ECF0`; `+0x0C` is `0x0800EF38`; `+0x30` is
`0x0800ED3E`; `+0x38` is `0x0800EF66`. `0x0804CEB8` overrides `+0x28` with
`0x08027468`, which only swaps the object's `+0x14` state object.

---

## 4. PROJECT CONCLUSION: `+0x00`

Three separate claims, kept apart as the ticket requires.

**`+0x00` PHYSICAL FIELD: CONFIRMED.** One little-endian `u16`; the field's high
byte is `0` on all 297 canonical objects, and the engine reads it with
`ldrb rX,[def]` at `0x08013046`, `0x08013088`, `0x080131DA`, `0x0802736C` and
`0x0802A28E`. No `ldrh` or `ldr` of the whole word was found in any consumer.
The measured low-byte range over the 297 objects is `1..23` over 14 distinct
values.

**`+0x00` COUNT SEMANTIC: CONFIRMED.** The byte is the **number of elements in
the inline array at `+0x54`**. Two independent lines of evidence:

1. *Object extent.* The definition's extent is `0x54 + 4 * count`: of the 296
   consecutive run pairs, **232** have the next definition starting exactly at
   `definition + 0x54 + 4*count`; the last object's computed end is exactly
   `0x086B6BDC`, where the run begins; and the 65 exceptions differ by exactly
   `+0x100`, which is the 256-byte remap block of §6, so the formula holds for every
   object.
2. *Five engine sites use it as an array bound.* Each reads the byte and then
   compares it with the index of the element it loads, skipping the load when
   the count is not greater than that index:

| Site | Count read | Compare | Element loaded | Index |
| --- | --- | --- | --- | --- |
| `0x08013044` | `0x08013046 ldrb r1,[r0]` | `0x08013048 cmp r1,#7` then `0x0801304A bls` | `0x0801304C ldr r0,[r0,#0x70]` | 7 |
| `0x08013086` | `0x08013088 ldrb r1,[r0]` | `0x0801308A cmp r1,#8` then `0x0801308C bls` | `0x0801308E ldr r0,[r0,#0x74]` | 8 |
| `0x080131D8` | `0x080131DA ldrb r1,[r0]` | `0x080131DC cmp r1,#7` then `0x080131DE bls` | `0x080131E0 ldr r0,[r0,#0x70]` | 7 |
| `0x0802736A` | `0x0802736C ldrb r2,[r1]` | `0x0802736E cmp r2,#1` then `0x08027370 bls` | `0x08027372 ldr r1,[r1,#0x58]` | 1 |
| `0x0802A28A` | `0x0802A28E ldrb r1,[r0]` | `0x0802A290 cmp r1,#6` then `0x0802A292 bls` | `0x0802A294 ldr r2,[r0,#0x6c]` | 6 |

`+0x54 + 4*index` is `+0x58`, `+0x6C`, `+0x70` and `+0x74` for indices 1, 6, 7
and 8, exactly the offsets those five sites load. A scan for the whole pattern
(definition pointer load, `ldrb` of the count, `cmp` against a small immediate,
then a load at `+0x54 + 4*index`) finds **exactly these five sites over
`0x08000000..0x08060000`**, and no others.

**`+0x00` ANIMATION-COUNT SEMANTIC: CONFIRMED.** The elements the count bounds
are animation pointers (§5, §7, §8), and the accessor that selects one is called
with indices in `0..21` (§10.1). So the byte is the number of animation entries
the definition carries. It is **not** an engine loop bound at the selection site
(§10.1 has no range check); the five guarded reads above are where the engine
consults it.

---

## 5. PROJECT CONCLUSION: `+0x54`

**`+0x54` PHYSICAL FIELD: CONFIRMED.** One `u32` little-endian word.
**`+0x54` ANIMATION-ARRAY SEMANTIC: CONFIRMED.** It is the **first element of an
inline array of `count` 32-bit ROM pointers**, not a pointer to an external
array and not a single pointer.

* `0x0800EBD0 ldr r0,[r6,#0x54]` is the only read of the field in the image, and
  the value it produces is used as an array base by `0x0800ECDA`
  (`ldr r3,[r3,#0x54]` after `def + 4*index`) and by `0x0800ED3E`,
  `0x0800ED50`.
* `0x0800EF38` reaches element `index` of the *selected animation* at byte
  offset `4 + 16*frame + 4*direction`, which presupposes `+0x54` to be an array
  of animation pointers with the layout of §7.
* 297 of 297 canonical `+0x54` values are word-aligned ROM pointers, so the
  field cannot be anything else on this image.

Array occupancy over the 4,070 slots the 297 counts describe. The model is
**count-bounded and sparse**:

* **1,721 slots are non-null** and **2,349 are null**;
* index 0 is non-null in **297 of 297** definitions; index 1 in 262 of the 285
  that have it; index 22 in 5 of 5;
* null counts by index, over the definitions that have the index: index 2 has
  190 nulls of 244, index 8 has 231 of 241, index 18 has 12 of 133.

**PROJECT CONCLUSION: the model is a count-bounded inline array with optional
(sparse) null elements.** It is not a fixed 23-slot array: the array's extent
tracks the count, and no definition carries an index at or above its count.

---

## 6. PROJECT CONCLUSION: THE PREFIX `+0x04 .. +0x53`

The prefix's fields, physically; consumers named where found.

| Offset | Physical field | Read by | PROJECT OBSERVATION | Status |
| --- | --- | --- | --- | --- |
| `+0x02` | `u16` LE | `ldrh` `0x0800EB7C`, `0x0800EC00` | 8 distinct values, all block sizes: `0x0040, 0x0100, 0x0200, 0x0400, 0x0800, 0x1000, 0x1800, 0x2400`; never zero | **CONFIRMED** as a byte size handed to `0x0803D5B8`; the `0x0801124C` call divides it by 64 (`asrs r0,r1,#6` at `0x08011252`), so a block-pool reading is **INFERRED** |
| `+0x04` | `u32` LE | `ldr` `0x0800EBF6` (twice) | `0` in **232**; in **65** it equals `definition - 0x100` | **CONFIRMED** as a pointer to the 256 bytes immediately before the object. Those bytes are a near-identity byte permutation with 4..50 substituted positions, which is the shape of a palette-index remap. The pointer relationship is CONFIRMED; "palette remap" is **INFERRED** |
| `+0x08` | 4 bytes, read individually | byte 0 `ldrb` `0x0800EF74`; bytes `+0x0A`,`+0x0B` `ldrb` `0x0800EC0A`/`0x0800EC0C` | byte 0 in `{0,8,16,32,64}` (`16` in 239); byte 1 in `{0,8,16,64}`; bytes 2/3 the pair `(0x0A,0x04)` in 222 objects | byte 0 is added to a screen x coordinate in `0x0800EF66`; bytes 2/3 select a resource through `0x08013E38`. Semantics **UNRESOLVED**; recorded as four separate bytes |
| `+0x0C` | `u32` LE | none found | `0` in 283, 6 distinct values | **UNRESOLVED** |
| `+0x10 .. +0x4F` | four 16-byte records of four `s32` LE | none found | value ranges per column are rect-like (`-18..8`, `-64..10`, `2..96`, `-7..56`), which is consistent with per-column bounding boxes | **UNRESOLVED**; accepted `GRAPHICS_FORMAT.md` calls these "per-direction bounding boxes, INFERRED" |
| `+0x50` | `u32` LE | `ldr` `0x0800EBB6`; indexed by animation index at `0x0800ECE4`, `0x0800ED08` | `0` in 287; in **10** a ROM pointer to a parallel, sparse, mostly 16-byte-spaced array with one entry per animation index | **PARTIALLY CONFIRMED**: a parallel per-animation pointer array used for the 10 objects that have one; the entries' meaning is **UNRESOLVED** |

**PROJECT CONCLUSION: none of `+0x04 .. +0x53` is padding.** `+0x02`, `+0x04`,
`+0x08` and `+0x50` each have at least one engine consumer; `+0x0C` and
`+0x10..+0x4F` have none found, and the negative claim for them is scoped in
§12.3.

---

## 7. PROJECT CONCLUSION: ANIMATION RECORDS

An element of the definition's inline array points at an **animation record**,
which is the structure the accepted ROM bible already names:

```text
+0x00            u32 frame_count        (1..16 over the canonical targets)
+0x04            u32 pointer[4 * frame_count]
+0x04 + 16*fc    u32 trailer_0
+0x08 + 16*fc    u32 trailer_1
```

Element byte offset is `4 + 16*frame + 4*direction`, so flat index
`4*frame + direction`. The engine's own arithmetic is that expression:
`0x0800EF38` does `ldrb r2,[obj,#0x11] / ldr r1,[obj,#0x50] /
lsls r2,r2,#4 / adds r1,r1,r2 / ldrb r2,[obj,#0x10] / lsls r2,r2,#2 /
adds r1,r1,r2 / ldr r1,[r1,#4]`.

PROJECT OBSERVATION:

* **1,017 unique animation records** are the distinct non-null targets of the
  1,721 non-null array slots; **410** of them are referenced from more than one
  (definition, index) site, and the maximum reuse is **16**.
* frame counts: `1:80, 2:275, 3:180, 4:407, 5:16, 6:13, 7:11, 8:3, 9:2, 10:2,
  11:24, 12:2, 16:2` over the 1,017 unique records.
* **13,660 frame-pointer slots**, all ROM pointers, **0 malformed**.
* **10,980 unique frame pointers**; maximum reuse 4.
* the trailer word at `+0x04 + 16*fc` is `1` for 1,006 of the 1,017 records;
  the word after it takes 5 distinct values (`256, 512, 1024, 2048, 4096` with
  11 outliers). Both are recorded raw; **UNRESOLVED**.

**Sharing does not imply semantic identity** and is not treated as if it did:
1,017 animation records are reached by 1,721 slots, and 10,980 frame records are
reached by 13,660 slots.

**Handoff boundary.** This ticket stops here. Everything below
`frame + 0x00` (the piece count, the 16-byte piece records, their OAM
attributes, their graphics containers) belongs to LOGX-FRAME-001. The only
frame-level facts recorded here are the ones the *character constructor* reads,
because they are what proves the animation-to-frame boundary:

```text
0x080273E4  str  r1, [r4, #0x54]    ; obj+0x54 = the selected frame record
0x080273F0  ldrsb r7, [r1, #4]      ; s8 at frame+0x04
0x080273F4  ldrsb r1, [r1, #5]      ; s8 at frame+0x05
0x0802740C  ldrb r2, [r3, #6]       ; u8 at frame+0x06
0x08027410  ldrb r3, [r3, #7]       ; u8 at frame+0x07
```

Under the accepted piece layout those four bytes are a piece's `x`, `y` and two
"purpose unexplained" bytes; the constructor uses the first two as signed
offsets and the last two as additive extents. That is recorded as a
corroboration of the accepted layout, not as a new piece claim.

---

## 8. PROJECT CONCLUSION: THE SELECTION MECHANISM AND THE SLOT MODEL

### 8.1 Three selector entry points

| Entry | Signature | What it does |
| --- | --- | --- |
| `0x0800ECDA` | `(obj, index)` | `obj+0x50 = *(u32*)(def + 0x54 + 4*index)`; if `def+0x50` is non-null also `obj+0x4C = def[0x50][index]`; returns |
| `0x0800ECF0` | `(obj, state)` | `index = u8[0x08072670 + state]`, then the same assignment and a class method call |
| `0x0800ED3E` | `(obj, state, row)` | `index = u8[0x08072670 + state]`, the same assignment, and `obj+0x11 = row` |

```text
0x0800ECDA  ldr  r2, [r0, #0x58]    ; definition
0x0800ECDC  lsls r1, r1, #2
0x0800ECDE  adds r3, r2, r1
0x0800ECE0  ldr  r3, [r3, #0x54]    ; def[0x54 + 4*index]
0x0800ECE2  str  r3, [r0, #0x50]    ; obj+0x50 = animation base
```

**`0x0800ECDA` has no range check against `def+0x00`.** It is called directly
from **162 sites**, and 159 of those pass a constant in `0..21`
(`0:9, 1:6, 3:10, 4:5, 7:2, 9:4, 10:2, 11:1, 12:4, 14:4, 15:3, 16:3, 17:3,
18:54, 19:28, 20:14, 21:7`), so selection is **caller-side** and the count's five
guarded reads (§4) are the engine's only bound consult.

**`obj+0x11` is a second index.** `0x0800ED3E` writes it (`strb r5,[r4,#0x11]`)
from its third argument, `0x0800EF38` reads it, and `0x0800F53C`/`0x0800F558`
save and restore it together with `obj+0x12`, `obj+0x14`, `obj+0x50` and
`obj+0x4C` as one animation-state tuple. `obj+0x10` is the other index: the
constructor sets it from the spawn record's `+0x08` low byte
(`0x080273CE..0x080273D4`).

**`0x0800EF38` recomputes the current frame** from those two indices:
`obj+0x54 = *(u32*)(obj+0x50 + 16*obj[0x11] + 4*obj[0x10] + 4)`, then sets
`obj+0x60 = obj+0x64 = 1` and returns 1.

### 8.2 The state-to-index translation table

```text
0x0800ECF0  ldr  r2, [pc, #0xec]    ; = 0x080725E8
0x0800ECF4  adds r2, #0x88          ; -> 0x08072670
0x0800ECF6  ldrb r3, [r2, r1]       ; index = table[state]
```

PROJECT OBSERVATION: the 25 bytes at `0x08072670` are

```text
 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
17 18 19 20 21 22 23 10 11
```

so states `0..15` map to the same animation index, states `16..22` map to
`17..23`, and states `23`/`24` alias indices `10`/`11`. Entries above 24 are
zero. **The mapping is a translation table, not an identity**: two states alias
the same index, and it is not the case that one fixed slot corresponds to one
game state by construction.

### 8.3 FIXED POSITIONAL SLOTS

* **FIXED POSITIONAL SLOTS, structurally: CONFIRMED.** "Animation index `k`"
  means the same *position* of the inline array for every definition: the
  selectors index `def + 0x54 + 4*index` with no per-definition translation, and
  the five guarded reads treat `+0x58`, `+0x6C`, `+0x70` and `+0x74` as
  "index 1", "index 6", "index 7" and "index 8" of the same array. So position
  is comparable across definitions.
* **FIXED POSITIONAL SLOTS, as 23 mandatory slots: REFUTED.** The array is
  count-bounded (extent `0x54 + 4*count`), counts are `1..23` over 14 distinct
  values, **2,349 of 4,070 slots are null**, and no object carries an index at
  or above its own count. Index 0 is the only universally non-null position.
* **VARIABLE-LENGTH MODEL: CONFIRMED.** The count bounds the array's extent.
* **SPARSE-SLOT MODEL: CONFIRMED.** Nulls are real: the selectors copy the
  loaded word into `obj+0x50` with no null test, so a selected null is a null
  animation base, which is a data property of the definition and not an engine
  guarantee.
* **FIXED POSITIONAL SLOTS as *semantic* slots: see §9.**

### 8.4 What gameplay code chooses

`0x08027390(obj, spawn_record)` is the constructor path:

```text
0x080273CE  ldr  r1, [r5, #8]       ; spawn record +0x08, a word
0x080273D0  lsls r1, r1, #0x18
0x080273D2  lsrs r1, r1, #0x18      ; low byte = column index
0x080273D4  strb r1, [r4, #0x10]    ; obj+0x10
0x080273D6  ldrb r3, [r4, #0x11]    ; obj+0x11 (frame index)
0x080273D8  ldr  r2, [r4, #0x50]    ; animation base, animation index 0
0x080273DC  lsls r3, r3, #4
0x080273DE  adds r2, r2, r3
0x080273E0  adds r1, r2, r1
0x080273E2  ldr  r1, [r1, #4]
```

So the constructor's default is animation index 0 and the two in-animation
indices are a frame index and a 0..3 column. An animation change happens through
one of the three selectors.

There is also a "morph" family: 41 direct `BL` call sites of `0x0800EDF8`, and
12-site / 9-site / 6-site functions (`0x080314DC`, `0x0802D3BC`, `0x0802A0C4`,
`0x0802CD20`, `0x0802CD84`, `0x0802DFD8`, `0x0802E040`, `0x08033908`,
`0x08033B4C`, `0x0803BB48`) that compare a live object's `+0x58` against
`0x08000158(id)` for a list of constants and call `0x0800EDF8` with another
constant id. Those are **identity/transform chains**, not animation selection:
they never touch `+0x54`.

---

## 9. PROJECT CONCLUSION: INDIVIDUAL SLOT MEANINGS

**INDIVIDUAL SEMANTIC SLOT NAMES: mostly UNRESOLVED.**

What is established:

* Positions are comparable across definitions (§8.3).
* The five count-guarded reads give four positions an *engine-visible role*
  rather than a name: index 1 is tested before a state-object swap
  (`0x0802736A`), index 6 before a two-versus-three selection (`0x0802A28A`),
  index 7 before allocating a 12-byte object and before an unrelated check
  (`0x08013044`, `0x080131D8`), and index 8 before dispatching method `+0x28`
  with the argument `8` (`0x08013086`), i.e. "if this sprite has animation 8,
  enter state 8", which is a *state/animation correlation*, not a name.
* The nonzero frequencies by position (§5) are consistent with optional
  abilities, but frequency is not meaning.

What is **not** established, and is therefore not written into the ROM bible:

* that index 0 is "stand", index 1 "walk", index 2 "run", 3..6 "attacks",
  7 "block", 8 "idle", or any other label;
* LOGExtractor's 23-slot numbering. The engine's own index space runs `0..23`
  (the state table's maximum output is `23`) while counts run `1..23`, so a
  naive `slot = index + 1` shift is *arithmetically possible* but has no engine
  witness; no code adds one to an animation index.

The labels in §1 claim 3 are recorded as **EXTERNAL CLAIM, not promoted**.

---

## 10. PROJECT CONCLUSION: RECONCILIATION WITH THE ACCEPTED ROM BIBLE

`GRAPHICS_FORMAT.md` publishes corpus figures for the same structures. This
ticket reproduced them independently and found exact agreement at the animation
level and a residual at the frame level.

| Measure | `GRAPHICS_FORMAT.md` | this ticket, raw | reconciled |
| --- | ---: | ---: | --- |
| pointer-run entries | 297 | 297 | agree |
| unique animation records | 1,013 | 1,017 | 4 of the 1,017 fail the accepted art filter; `1017 - 4 = 1013` |
| animation references | 1,562 | 1,721 slots | the accepted walk **deduplicates** per structure; slot counts and distinct-reference counts are different populations |
| direction slots populated | 13,596 | 13,660 | the 4 rejected animations hold **64** slots; `13660 - 64 = 13596` |
| unique frame records | 10,959 | 10,980 | the 4 rejected animations carry 16 frames no accepted animation reaches; `10980 - 16 = 10964`, which is **5 more** than the accepted total; the residual is **UNRESOLVED** and recorded, not explained away |
| structures with decodable art | 295 | 295 | 2 of 297 structures have no decodable animation |
| animation NULL slots | 0 | 0 | agree over the accepted population |

### 10.1 A genuine contradiction with an accepted conclusion

`tools/webfoot/graphics.py::_animations_in` resolves a structure's animation
pointers by walking from `+0x54` to the **next structure**, and its docstring
states the justification:

> "The extent is resolved by walking to the next structure rather than by
> trusting a count, for the same reason `webfoot.formats.map_slots` walks: **no
> field in this header has been shown to bound the list.**"

PROJECT OBSERVATION: that justification is now **refuted**. The `+0x00` byte
bounds the list, and five engine sites use it as an index bound (§4). Measured
consequences of the wrong model on the canonical image:

* the counted model covers **4,070** slots; the walk covers **8,230**;
* the walk's **4,160** extra slots are all **nonzero** and **none** is a ROM
  pointer: they are the 256-byte remap blocks of §6 read as if they were
  pointers;
* the accepted model nonetheless reaches the correct corpus, because
  `_offset_of` rejects every extra word. Its numbers are right for the wrong
  reason, and its per-structure deduplication (which the count model does not
  need) is what makes its "animation references" figure a distinct-reference
  count rather than a slot count.

**Action taken: none.** This ticket does not modify `tools/webfoot/graphics.py`
or `GRAPHICS_FORMAT.md`; per the ticket's rule for a genuine contradiction it
documents the finding and flags it for synthesis or a targeted correction rather
than silently altering an accepted conclusion. The recommended correction is to
replace the walk with `[+0x54, +0x54 + 4*count)` and to re-state the two
reference figures as slot counts.

---

## 11. PROJECT CONCLUSION: THE APPEARANCE JOIN

LOGX-CHAR-001's `+0x04` relationship is reused, not re-derived: `probe` imports
`tools.research.logx_char_probe` and calls its `iter_records`.

| Population | Value |
| --- | ---: |
| appearance records (LOGX-CHAR-001) | 232 |
| distinct `+0x04` ids used | 198 |
| distinct definition targets they resolve to | 198 (no aliasing) |
| run indices reached | 198, spanning index 2 (id 12) .. index 296 (id 306) |
| run indices never reached by any appearance | **99** |
| ids below the accessor's floor | 0 |
| ids at or above `10 + 297` | 0 |
| ids shared by more than one appearance | 25 |

**PROJECT CONCLUSION: the relationship is confirmed and complete for the
canonical table**: every appearance's `+0x04` lands inside the accepted run.
**Appearance-referenced definitions: 198. Unreferenced definitions: 99.** The 99
include the run entry id 10 and id 11 (indices 0 and 1) and 97 others.

---

## 12. NEGATIVE-COVERAGE STATEMENTS

Absence claims in this document are scoped, per `docs/research-conventions.md`.

**12.1 `definition + 0x54`'s reader set.** A raw halfword scan of the whole
8 MiB image for `ldr Rt,[pc,#imm]` sites whose literal word is `0x086B6BDC`
finds exactly two sites (`0x0800015E`, `0x0801713E`), so no folded base other
than `0x086B6BB4` reaches the array through a literal, and that folded base is
explained arithmetically. The `ldr r0,[r6,#0x54]` at `0x0800EBD0` is the only
read of a definition's `+0x54` among the 121 direct accessor call sites and the
object's whole method set as read in `0x0800EC34..0x0800F600`.

**12.2 The five count-guarded reads are exhaustive over the code region.** The
scan pattern (`ldr rX,[obj,#0x58]`, then `ldrb rY,[rX]`, then `cmp rY,#k`, then
within the next 18 instructions `ldr rZ,[rX,#0x54+4k]`) was run over every
decodable instruction boundary in `0x08000000..0x08060000` (183,296
instructions, resynchronising wide-window sweep) and returned exactly the five
sites of §4. It is **not** evidence about code that keeps a definition pointer
in a register across a call, and it does not cover ARM state.

**12.3 `+0x0C` and `+0x10..+0x4F` have no consumer.** The whole method set of
the two classes the constructor installs (`0x0804AC20`, `0x0804CEB8`) was read,
as was `0x0800EB60`, `0x0800EDF8`, `0x08027390` and the 51 functions that call
the accessor at all. None reads a definition at `+0x0C` or in
`+0x10..+0x4F`. This does **not** cover a definition pointer stored in one
function and read in another through an unfollowed offset, and it does not cover
code outside `0x08000000..0x08060000`.

**12.4 The accessor's caller census.** `scan_thumb_bl_callers` over a raw
halfword pass of the whole image finds **121** `BL` sites resolving to
`0x08000158` and **19** to `0x0801713C`. Method dispatch through
`0x08046AA4` is not a `BL` to either accessor, so a caller reached only through
a class method is not counted; §12.3's method reading covers that gap for the
two classes.

---

## 13. ANOMALIES

1. **Two objects end where the run begins.** The last definition (id 306,
   `0x086B6B60`) occupies the bytes immediately before the run, so the folded
   base points into a *different* structure than the one the run holds. This is
   the single fact that made LOGX-CHAR-001's first-entry question look
   undecidable.
2. **65 objects carry a `0x100`-byte remap block before them**, always
   referenced by their `+0x04`, and always at `definition - 0x100`. The
   correlation between "has `+0x04`" and "is preceded by a block" is exact over
   the canonical image (65 and 65).
3. **`+0x02` takes eight block sizes and never zero**, yet the value is also used
   as a resource selector through `0x0801124C` after a `>> 6`. Whether the two
   uses are one field with two views or two coincident fields is **UNRESOLVED**.
4. **A selected animation can be null.** The selectors do not test for null, and
   12 of the 133 definitions that have index 18 carry a null there. No engine
   code was found that guards the selection.
5. **`+0x50` is populated for only 10 of 297 objects**, and the constructor
   branches on it (`0x0800EBB6`). Those 10 are the only objects whose
   `obj+0x4C` is initialised from the definition; the other 287 leave it zero.
6. **The state table aliases two states onto indices 10 and 11** (states 23 and
   24), so state and animation index are not in bijection.
7. **The frame-level corpus figures do not fully reconcile** with
   `GRAPHICS_FORMAT.md`: this ticket reaches 10,964 frames under a reproduction
   of the accepted filter where the accepted document reports 10,959.

---

## 14. UNRESOLVED QUESTIONS

1. What the 256-byte block at `definition - 0x100` is used for. Its shape is a
   palette-index remap and `obj+0x34`/`obj+0x3C` receive it, but no instruction
   was read that indexes it.
2. What `definition + 0x0C` and `definition + 0x10..+0x4F` hold.
3. What the animation record's two trailer words mean; the first is `1` for
   1,006 of 1,017 records and the second takes five small values.
4. What `obj+0x12` is: it is saved and restored with the animation state but
   not read in any function this ticket read.
5. Which game states correspond to the state table's `0..24`, and therefore
   which animation indices they select.
6. Whether any producer of the state numbers passes a value above 24 (the table
   has zeroes there) or an animation index at or above a definition's count.
7. Why the 4 art-filter-rejected animations exist and which definitions reach
   only them.
8. The 5-frame residual in §10.

---

## 15. HANDOFF TO LOGX-FRAME-001

* **Animation record**: `u32 frame_count` at `+0x00`, then `4 * frame_count`
  32-bit ROM pointers; frame `f`, direction slot `d` at byte offset
  `+0x04 + 16*f + 4*d`.
* **How selected**: `0x0800ECDA(obj, index)` assigns
  `*(u32*)(definition + 0x54 + 4*index)` to `obj+0x50`; the state entry points
  `0x0800ECF0`/`0x0800ED3E` translate a state through the 25-byte table at
  `0x08072670` first. `0x0800EF38` then reads
  `*(u32*)(obj+0x50 + 16*obj[0x11] + 4*obj[0x10] + 4)` into `obj+0x54`.
* **How many**: 1,017 unique animation records over 1,721 non-null slots;
  13,660 frame-pointer slots over 10,980 unique frame records.
* **Representative raw prefix**: definition id 115 at `0x086AD1CC` (count 22);
  its animation index 0 is `0x0850C1DC` with `frame_count = 2`, first four
  pointers `0x0850C13C, 0x0850C164, 0x0850C18C, 0x0850C1B4`, trailer
  `(1, 0x400)`; frame `0x0850C13C` has `piece_count = 1` and bytes
  `F8 E8 20 20` at `+0x04`.
* **Entry points**: `0x0800EB60` (constructor), `0x0800EDF8` (re-skin),
  `0x08027390` (spawn path), `0x0800ECDA` / `0x0800ECF0` / `0x0800ED3E`
  (selection), `0x0800EF38` (recompute), `0x0800EF66` (screen position),
  `0x0800F53C` / `0x0800F558` (animation-state save/restore).
* **Count/metadata needed to locate frames**: the frame count at `+0x00`, the
  four-direction stride, and the definition's `+0x00` byte that bounds the
  animation array.
* **Not done here**: frame count interpretation, frame-record internals, piece
  counts, per-piece graphics pointers, OAM attributes and flip flags, frame
  origins. `probe.read_frame_record` exposes only `piece_count` and the four
  bytes the character constructor reads.

## 16. OTHER DOWNSTREAM HANDOFFS

* **TOOLKIT-010 / `GRAPHICS_FORMAT.md`**: §10.1: the extent justification is
  refuted and two corpus figures are slot counts rather than distinct-reference
  counts. A targeted correction is recommended; this ticket does not make it.
* **Toolkit sprite reader (`tools/webfoot/formats/sprite_graphics.py`)**:
  `decode_animation` already models the animation record the way the engine
  does; it needs no change. `webfoot/graphics.py::_animations_in` should read
  `count` from `definition + 0x00`.
* **LOGX-CHAR-001**: its two UNRESOLVED items about the run, namely which byte is the
  first entry and how the id space is anchored, are resolved by §2.1. Its
  accepted conclusions are unchanged.
* **APPROACH for any future authoring work**: an animation slot is optional, so
  an editor must be able to write a null element and must not assume 23
  positions exist.
