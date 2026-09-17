# LOGX-CHAR-001: Buu's Fury character-definition records

Evidence document for the canonical Buu's Fury USA Rev. 0 image, SHA-256
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

Every claim is labelled with one status from
[`../research-conventions.md`](../research-conventions.md):

- **CONFIRMED** - directly supported by cited engine instructions, cited ROM
  bytes, or a reproducible observation scoped to this profile;
- **PARTIALLY CONFIRMED** - the physical fact is established but the semantic
  reading is not;
- **INFERRED** - best explanation supported by evidence, not directly proven;
- **UNKNOWN** - evidence absent, contradictory or insufficient.

Three provenance labels are used and never mixed:

- **EXTERNAL CLAIM** - a statement taken from `mainant/LOGExtractor`;
- **PROJECT OBSERVATION** - a reproducible measurement on the canonical image or
  a reading of the canonical image's own instructions;
- **PROJECT CONCLUSION** - this ticket's reasoned verdict on an observation.

Terminology is fixed here. A **character record** is one 16-byte entry of the
table below. The **`+0x04` pointer array** is the 4-byte-entry pointer array the
record's `+0x04` selects; it is named after the field because what its entries
are is only partially established. The **`+0x08` pointer array** is the
4-byte-entry pointer array the record's `+0x08` selects, likewise. The **stat
table** is the 28-byte-record table at `0x08711274` the record's `+0x0C` indexes,
already accepted by TOOLKIT-009. LOGExtractor's names for the two arrays
("sprite-definition pointer table", "portrait pointer table") appear only inside
quoted EXTERNAL CLAIMs and in the partial-semantic verdicts, never as the
project's identifiers. Field names in this document are positions (`+0x04`),
never invented semantics.

---

## 1. Scope and input

Research only. No GUI, Workbench, authoring, sprite or frame reconstruction; no
derived ROM; no emulator; no mutation of the canonical image. Addresses are GBA
addresses unless stated; a file offset is an address minus `0x08000000`. The
image was opened read-only and its SHA-256 re-verified before and after every
measurement pass.

Detailed sprite-definition, animation and frame reconstruction is explicitly out
of scope and handed to LOGX-SPRITE-001 and LOGX-FRAME-001; section 16 records
exactly where this ticket stopped.

---

## 2. Accepted dependencies used as given

| Fact | Source |
| --- | --- |
| UTF-16LE text pointer table at file offset `0x0006BCE8`, 1,534 entries, pool `0x0005792C..0x0006BCE6` | TOOLKIT-004 / `docs/research/TEXT_FORMAT.md` |
| Enemy-stat table at file offset `0x00711274`, stride `0x1C`, 141 records | `tools/webfoot/formats/stat_tables.py` (`ENEMY_TABLE_START`, `ENEMY_RECORD_SIZE`, `ENEMY_RECORD_COUNT`) |
| Placement-type view of the same base: stride 28, `max_selector` 149 | `config/roms.yaml` `placement_types` (TOOLKIT-009) |
| Character graphics pointer table at file offset `0x006B6BDC`, 297 entries, all valid and strictly ascending | TOOLKIT-010 / `docs/research/GRAPHICS_FORMAT.md` |
| Webfoot container wrapper `0x0803D940` | LOGX-CODEC-001 |

This ticket re-measures each of those bounds where it depends on them; it does
not re-derive the text codec, the stat record layout or the sprite object layout.

---

## 3. EXTERNAL CLAIMS AND THEIR DISPOSITION

**EXTERNAL CLAIM (LOGExtractor, `CharacterSpriteExtractor`).** A character table
begins at `0x74D380`, with 232 records of 16 bytes, and record fields `+0x00`
name text index, `+0x02` skipped/"description", `+0x04` sprite-definition index,
`+0x08` portrait index, `+0x0C` unresolved.

**EXTERNAL CLAIM (LOGExtractor).** A sprite-definition pointer table at
`0x6B6BB4`, a portrait pointer table at `0x6F393C`, and a text pointer table at
`0x06BCE8`.

**PROJECT OBSERVATION (address space).** LOGExtractor's addresses are **file
offsets**. Its `0x06BCE8` text pointer table is this project's independently
verified `TEXT_TABLE_START = 0x0006BCE8`, and its `0x74D380`, `0x6B6BB4` and
`0x6F393C` are all inside the 8 MiB file with no `0x08000000` base added. The
engine's own literal for the text table is `0x0806BCE8` and for the `0x08`
pointer array `0x086F393C`, i.e. file offset plus the cartridge base.
**CONFIRMED**: the external notation is file-relative, and every address in this
document is given in both forms.

**PROJECT CONCLUSION.** The table start, the 232-record count and the 16-byte
stride are **CONFIRMED** from the engine's own instructions (sections 5-7). The
field readings are **CONFIRMED as physical fields** and separately classified as
semantics (sections 9-12). One external statement is **REFUTED**: the `+0x02`
field is not inert. Two further external statements are given a narrower reading
rather than a flat correction: the `+0x04` pointer array's *arithmetic* base is
indeed `0x086B6BB4`, but which byte is the array's first entry stays
**UNRESOLVED** (section 10.3), and "character table" is replaced by the neutral
name because the table spans more than characters (section 14).

---

## 4. THE CANDIDATE TABLE AND ITS NEIGHBOURS

```text
file 0x74D35C  00 03 01 02                    4-byte table, referenced by 0x0802734C
file 0x74D360  2c750508 2c760508 ...          8-entry u32 pointer table, referenced by 0x08027494
file 0x74D380  record 0 ... record 231        232 x 16 bytes = 0xE80 bytes
file 0x74E200  first word 0x03001C4C          not a record (section 15)
```

GBA addresses: byte table `0x0874D35C`, pointer table `0x0874D360`, the
232-record table `0x0874D380`, first word past it `0x0874E200`.

The eight-entry pointer table immediately before the records holds
`0x0805752C, 0x0805762C, 0x0805772C, 0x0805782C, 0x0805782C, 0x0805772C,
0x0805762C, 0x0805752C` and its consumer masks its index with `& 7`
(`0x08027490 lsls r1,r1,#0x1b` / `0x08027492 lsrs r1,r1,#0x1d`), so it is an
eight-entry table, not a misaligned record table. None of its words is a text
index, and its own boundary is exactly the first record's first byte.

---

## 5. TABLE START

**PROJECT OBSERVATION.** The word `0x0874D380` occurs **5 times** in the image,
all word-aligned, and is loaded by **8** `ldr Rt,[pc,#imm]` instructions:

| Site | Register | Literal pool word |
| --- | --- | --- |
| `0x08024FA0` | `r7` | `0x08025310` |
| `0x08025086` | `r1` | `0x08025310` |
| `0x080251B6` | `r1` | `0x08025310` |
| `0x08025380` | `r1` | `0x080256B8` |
| `0x08025E94` | `r2` | `0x0802618C` |
| `0x080273AC` | `r1` | `0x08027474` |
| `0x08027962` | `r1` | `0x080279D8` |
| `0x080279A0` | `r1` | `0x080279D8` |

Method: a raw halfword scan of **every even offset** over the whole 8 MiB image
for the 16-bit PC-relative load encoding (`01001 Rt imm8`), with the effective
pool address computed as `((site + 4) & ~3) + imm8*4`. No control-flow knowledge
and no disassembly resynchronisation is involved, so an undecodable neighbouring
halfword cannot hide a site.

**PROJECT CONCLUSION - TABLE START: CONFIRMED.** Eight independent engine loads
address this exact byte as a record base, and each is followed by its own
`index << 4` scale (section 6).

### 5.1 Negative coverage for the start

The negative claim is narrower than "nothing else reaches the table": it is that
**no folded base reaches it**. The `+0x04` accessor (section 11.1) reaches its own
array through a literal `0x28` bytes above the base it uses, so a folded base was
a live possibility here.

- **Scope searched:** every even offset of the whole image, for `ldr Rt,[pc,#imm]`.
- **Region reported:** `0x0874D280..0x0874D400`, i.e. the `0x100` bytes below the
  table plus the table's own head. The literal values found in it are exactly
  `0x0874D35C`, `0x0874D360` and `0x0874D380`; the first two are the two
  independently explained neighbouring structures, so neither is a folded
  character-table base.
- **Coverage gap, stated rather than hidden:** a folded base *more than `0x100`
  bytes* below the table is outside the reported range by construction. Literals
  at `0x0874CA24`, `0x0874CA38`, `0x0874D02C`, `0x0874D03C` and `0x0874D248` do
  exist in the image; each was inspected at its load sites and none is used with
  a 16-byte stride plus an index, so none is a character-record base. The claim
  is nonetheless limited to the reported range.
- **Not covered, and therefore not part of the claim:** the 16-bit Thumb
  `add Rd, pc, #imm8*4` form, which can only reach within 1,020 bytes of the
  instruction; every such encoding in the 0x400 bytes below the table was
  inspected and **none** computes the table address. The ARM `add Rd, pc, #imm12`
  and `ldr Rd, [pc, #imm12]` forms reach at most 4,095 bytes; the corresponding
  words in the 0x1000 bytes below the table compute no address in the table.
  A `movw`/`movt` pair does not exist on ARM7TDMI.

---

## 6. TABLE STRIDE

**PROJECT OBSERVATION.** **Eight** engine sites compute a record address as
`index << 4` and add the table base - one per literal load of section 5. Three of
them are inside the two table-walking loops; the other five are single-record
lookups:

| Site | Instruction | Function | Kind |
| --- | --- | --- | --- |
| `0x08027964` | `lsls r0, r4, #4` then `0x08027966 adds r6, r0, r1` | `0x08027948` | walk |
| `0x080279A2` | `lsls r0, r4, #4` then `0x080279A4 adds r0, r0, r1` | `0x08027948` | walk |
| `0x08024FA8` | `lsls r5, r5, #4` then `0x08024FAA adds r5, r5, r7` | `0x08024F3C` | walk |
| `0x08025088` | `lsls r0, r0, #4` | `0x08025056` | lookup |
| `0x080251B8` | `lsls r0, r0, #4` | `0x08025056` | lookup |
| `0x08025382` | `lsls r0, r0, #4` | `0x08025354` | lookup |
| `0x08025E92` | `lsls r1, r5, #4` | `0x08025E50` | lookup |
| `0x080273AE` | `lsls r0, r0, #4` | `0x08027390` | lookup |

`0x10` is the only scale applied to a record index anywhere in these functions.
Other `adds rX, #0x10` instructions do exist in them (`0x08024F64`, `0x0802506C`,
`0x08025378`, `0x0802607A`) and other `lsls #1`/`#2` scales exist throughout, so
the claim is scoped to the **record index**: none of those sites walks a record
base or scales a record index.

**PROJECT CONCLUSION - TABLE STRIDE: CONFIRMED**, 16 bytes, from engine
arithmetic at eight sites and not from record plausibility. The adjacent
eight-entry pointer table uses a 4-byte stride, the `+0x04`/`+0x08` pointer
arrays 4 bytes per entry and the stat table 28 bytes, so the four are not
conflatably "aligned records".

---

## 7. TABLE COUNT

**PROJECT OBSERVATION.** Three engine loop bounds over the table's index are
`0xE8` = **232**:

| Site | Instruction | Loop |
| --- | --- | --- |
| `0x08027998` | `cmp r4, #0xe8` / `0x0802799A blt` | `0x08027948`, first scan |
| `0x080279CC` | `cmp r4, #0xe8` / `0x080279CE blt` | `0x08027948`, second scan |
| `0x08024F92` | `cmp r0, #0xe8` / `0x08024F94 blt` | `0x08024F3C`, roster bitmap walk |

Each loop starts its counter at zero and increments **before** the comparison, so
`0xE8` is an exclusive upper bound: index 231 is the last index visited and index
232 is never addressed. The search function `0x08027948` additionally returns
`-1` (`0x080279D0 movs r0,#0` / `0x080279D2 mvns r0,r0`) when its loops exhaust;
`0x08024F3C` has no such epilogue (its only `mvns` at `0x08024FFC` builds a `-1`
that it **stores** at `[object + 0x14]`), and its own loop simply falls through.
The exclusive bound does not depend on either epilogue.

**PROJECT OBSERVATION (independent corroboration).** `0x08024F3C` walks exactly
that index range against a runtime bitmap: for `index` in `0..231` it tests
`bit (index & 7)` of byte `(index >> 3)` at `base + 0xC5` (`0x08024F70 asrs r5,r0,#3`
/ `0x08024F72..0x08024F74` / `0x08024F7A ldrb r3,[r3,#5]` / `0x08024F7C..0x08024F80
movs r5,#1 ; lsls r5,r7 ; ands r3,r5`), where `base` is the IWRAM pointer held at
`0x087319D4`. A 232-bit map is 29 bytes, so the runtime index space is 232 wide.

**PROJECT OBSERVATION (boundary).** Record 232 (`0x0874E200`) reads
`+0x00 = 7244`, which is outside the 1,534-entry text table,
`+0x02 = 768 ≠ +0x00 + 1`, and `+0x04 = 0x030019A4`, which is not a table index at
all. Three of the four invariants that hold on all 232 accepted records fail on
it (section 15).

**PROJECT CONCLUSION - TABLE COUNT: CONFIRMED**, fixed at 232, index 231 valid,
index 232 outside.

---

## 8. THE ENGINE CONSUMERS

Six functions read the table. Every one of them was read in full; the field each
loads is quoted with its instruction.

| Function | Sites | Fields read | What it does with them |
| --- | --- | --- | --- |
| `0x08024F3C` | `0x08024FA0` | `+0x00` (`ldrh r5,[r5]` at `0x08024FAC`) | Walks the 232-bit runtime bitmap, then for each set bit reads `+0x00` and collapses **adjacent equal** values into a display list (`0x08024FAE cmp r3,r5` / `0x08024FB0 beq`), so `+0x00` is used as a *grouping key*, not only as text |
| `0x08025056` | `0x08025086`, `0x080251B6` | `+0x08` (`ldr r0,[r7,#8]` at `0x080250CA`), `+0x00` (`ldrh r0,[r0]` at `0x080251BC`), `+0x02` (`ldrh r0,[r7,#2]` at `0x080252E6`) | `+0x08` is passed to the `+0x08` accessor `0x08011F20` at `0x080250D2` and the result to the container dispatcher `0x0803D940`; `+0x00` and `+0x02` each select a text pointer from `0x0806BCE8` (`0x080251BE`/`0x080252E8` -> pool `0x08025328` = `0x0806BCE8`, `0x080251C2`/`0x080252EC ldr [r1,r0]`) and are drawn by `0x0803DADA` and `0x0803DD66` |
| `0x08025354` | `0x08025380` | `+0x02` (`ldrh r0,[r5,#2]` at `0x0802539E`) | Text pointer from `0x0806BCE8` (`0x080253A0` -> `0x080256C0`), then `0x0803DE6A`, which is called in a loop until the line counter reaches zero (`0x080253B6..0x080253BC`), i.e. a wrapping multi-line draw |
| `0x08025E50` | `0x08025E94` | `+0x02` (`ldrh r0,[r0,#2]` at `0x08025EC2`) | Same shape: text pointer from `0x0806BCE8` (`0x08025EC0` -> `0x08026190`), then `0x0803DE6A` |
| `0x08027390` | `0x080273AC` | `+0x04` (`ldr r0,[r0,#4]` at `0x080273B2`) | `bl 0x08000158` at `0x080273B4`, then `bl 0x0800EB60`; this is a 0x190-byte object constructor |
| `0x08027948` | `0x08027962`, `0x080279A0` | `+0x04` (`ldr r0,[r6,#4]` at `0x08027968`), `+0x0C` (`ldr r0,[r6,#0xc]` at `0x08027974`, `ldr r1,[r0,#0xc]` at `0x080279AA`) | A table **search**; see 8.1 |

### 8.1 The search function `0x08027948`

```text
08027948  push  {r3, r4, r5, r6, r7, lr}
0802794a  adds  r7, r0, #0            ; r7 = argument 1 (appearance id)
0802794c  adds  r5, r1, #0            ; r5 = argument 2 (a 0x1C-record pointer, or 0)
0802794e  movs  r0, #0x95
08027950  bl    0x08000158            ; f(0x95)
08027954  cmp   r0, r7
08027956  bne   0x08027960
08027958  movs  r0, #0x92
0802795a  bl    0x08000158            ; f(0x92) is the substituted id
0802795e  adds  r7, r0, #0
08027960  movs  r4, #0                ; loop 1: i = 0
08027962  ldr   r1, =0x0874D380
08027964  lsls  r0, r4, #4
08027966  adds  r6, r0, r1            ; r6 = &record[i]
08027968  ldr   r0, [r6, #4]          ; +0x04
0802796a  bl    0x08000158
0802796e  cmp   r0, r7
08027970  bne   0x08027996
08027972  cmp   r5, #0
08027974  ldr   r0, [r6, #0xc]        ; +0x0C
08027976  beq   0x0802798e
08027978  cmp   r0, #0
0802797a  blt   0x08027996
0802797c  lsls  r3, r0, #3
0802797e  subs  r0, r3, r0            ; 7 * index
08027980  ldr   r6, =0x08711274
08027982  lsls  r0, r0, #2            ; 28 * index
08027984  adds  r0, r0, r6
08027986  cmp   r0, r5
08027988  bne   0x08027996
0802798a  adds  r0, r4, #0            ; return i
...
08027998  cmp   r4, #0xe8
0802799a  blt   0x08027962
0802799c  ldr   r6, =0x08711274       ; loop 2, r5 == 0 path only
...
080279bc  ldr   r0, [r0, #4]
080279be  bl    0x08000158
080279c2  cmp   r0, r7
...
080279d0  movs  r0, #0
080279d2  mvns  r0, r0               ; return -1
```

**PROJECT CONCLUSION.** The function's argument 1 is in the **same id space as
`+0x04`**: it is compared after both values are mapped through the same accessor
`0x08000158`. Argument 2, when non-null, is in the **same address space as
`0x08711274 + 28 * +0x0C`**. The return value is a 0-based index into the
232-record table, or `-1`.

### 8.2 How runtime code arrives at a record

**PROJECT OBSERVATION.** `0x08027948` has exactly two Thumb `BL` callers:

| Caller | Argument 1 | Argument 2 |
| --- | --- | --- |
| `0x0800FB72`, in the function at `0x0800FAFA` | `ldr r0,[r4,#0x58]` at `0x0800FB70` | `ldr r1,[r4+0x224]` at `0x0800FB6E` (`lsls r0,r0,#9` -> `adds r0,r4,r0` -> `ldr r1,[r0,#0x24]`) |
| `0x08010312`, in the function at `0x080102D8` | `ldr r0,[r4,#0x58]` at `0x08010310` | `movs r1,#0` at `0x0801030E` |

Both pass a live object's `+0x58` as the appearance id, and the `-1` result is
tested with `adds r3, r0, #1` / `bne`. `[object + 0x224]` is a pointer into the
stat table's address space, which is the same object field the accepted
placement/type path uses. **The route is therefore
`runtime object -> (appearance id at +0x58, stat record pointer) -> 0x08027948 ->
0-based character-record index`.** Level **2** (static downstream role); no
runtime capture was taken and none was needed.

**PROJECT CONCLUSION - TABLE SEMANTIC IDENTITY: PARTIALLY CONFIRMED.** The table
is a **set of character/appearance definitions addressed by an appearance id and
a stat-record pointer**, read by text/drawing code and by object constructors. Whether every record is "a character" (playable, NPC, enemy, prop)
is not established by the engine: the census contains entries the game's own text
calls a laser turret, a worm body and a tank (section 14). The neutral canonical
name is **character-appearance definition table**; "character table" is the
external name and is not promoted.

---

## 9. RECORD `+0x00` AND `+0x02`

### 9.1 Physical representation

| Field | Width | Instruction | Sites |
| --- | --- | --- | --- |
| `+0x00` | `u16`, little-endian | `ldrh r5, [r5]`, `ldrh r0, [r0]` | `0x08024FAC`, `0x080251BC` |
| `+0x02` | `u16`, little-endian | `ldrh r0, [r7, #2]`, `ldrh r0, [r5, #2]`, `ldrh r0, [r0, #2]` | `0x080252E6`, `0x0802539E`, `0x08025EC2` |

Both are read with the halfword load; no `ldr` reads either field, and no
instruction reads `+0x00` and `+0x02` as one 32-bit value. **CONFIRMED** as two
separate 16-bit fields.

### 9.2 Text relationship

Four literal loads of the text table are used with these two fields: `0x080251BE`
and `0x080252E8` both resolve to the pool word at `0x08025328`, whose value is
`0x0806BCE8`; `0x080253A0` resolves to `0x080256C0` and `0x08025EC0` to
`0x08026190`, all three words `0x0806BCE8` (four loads, three pool words). Each
field is scaled by four
(`lsls r0,r0,#2` at `0x080251C0`, `0x080252EA`, `0x080253A2`, `0x08025EC6`) and
then loaded with `ldr` (`ldr r1,[r1,r0]` at `0x080251C2`; `ldr r0,[r1,r0]` at
`0x080253A4` and `0x08025EC8`) - exactly the access shape TOOLKIT-004
established for a `u32` pointer table indexed by a text id. The scale is **four**,
not two: the table's entries are 32-bit addresses.

**PROJECT OBSERVATION.** Over all 232 records both fields are in
`0..1533` (maximum `+0x00` = 1310, maximum `+0x02` = 1311), so **every** record's
text resolves; there are no empty, invalid or sentinel values.

| | Status |
| --- | --- |
| `+0x00` physical field `u16` | **CONFIRMED** |
| `+0x00` is an index into the accepted text table `0x0806BCE8` | **CONFIRMED** |
| `+0x02` physical field `u16` | **CONFIRMED** |
| `+0x02` is an index into the accepted text table `0x0806BCE8` | **CONFIRMED** |
| `+0x00` text is the entity's short label ("name") | **PARTIALLY CONFIRMED** |
| `+0x02` text is the entity's prose description | **PARTIALLY CONFIRMED** |

The semantic reading is supported by, and only by, three things: the string
content (`+0x00` resolves to `"Goku"`, `"Zombie"`, `"Airship Warlord"`; `+0x02`
resolves to one or two sentences of prose); the consumer shapes (`+0x00` is drawn
once by `0x0803DADA` at `0x080251C8`, `+0x02` by `0x0803DE6A`, which the caller
loops over a line counter at `0x080253B6..0x080253BC`); and the data itself (232
records carry only 154 distinct `+0x00` values and the same 154 distinct `+0x02`
values). None of that is a runtime observation, so the name "name" and the name
"description" are **not** promoted to engine facts. `docs/reverse-engineering.md`
therefore records the fields as text indices.

### 9.3 The `+0x02 = +0x00 + 1` invariant

**PROJECT OBSERVATION.** `+0x02 == +0x00 + 1` holds for **232 of 232** records.
The pairing is a strict bijection: no two distinct `+0x00` values share a
`+0x02` value, and vice versa.

**PROJECT CONCLUSION.** This is a **data invariant of the canonical image**, not
a demonstrated engine constraint: no instruction compares the two fields, and no
code derives one from the other. It is recorded because it is exact and would be
the first thing a future encoder must reproduce.

**EXTERNAL CLAIM (LOGExtractor).** `+0x02` is a "2-byte field skipped / loosely
described as description". **PROJECT CONCLUSION: the "skipped" reading is
REFUTED as a statement about the engine** - three separate engine functions read
`+0x02` and pass it to the text system. The extractor's images simply never
needed it.

---

## 10. RECORD `+0x04` AND THE CHARACTER-APPEARANCE POINTER TABLE

### 10.1 Physical field

`+0x04` is read as a full 32-bit value with `ldr r0, [r6, #4]` (`0x08027968`) and
`ldr r0, [r0, #4]` (`0x080273B2`). Its range over the 232 records is **12 .. 306**,
there are **198** distinct values, and **no record has `+0x04 == 0`**.

### 10.2 The accessor `0x08000158`

```text
08000158  push  {r4, lr}
0800015a  cmp   r0, #0xa
0800015c  blt   0x0800016a          ; ids 0..9 -> the party-slot path
0800015e  ldr   r1, [pc, #0x260]    ; pool 0x080003C0 = 0x086B6BDC
08000160  lsls  r0, r0, #2
08000162  adds  r0, r0, r1
08000164  subs  r0, #0x40           ; -64
08000166  ldr   r0, [r0, #0x18]     ; +24    => total displacement -0x28
08000168  pop   {r4, pc}
```

Raw encodings: `0x0800015E` = `4998`, `0x08000164` = `3840`, `0x08000166` =
`6980`. The function returns `u32 at 0x086B6BDC + 4*id - 0x28` for `id >= 10`.
`0x0801713C` is a second entry to the same table with the identical literal and
the identical displacement, taking the id from `ldrh r0,[r0,#0x0e]` of a party
record.

**PROJECT CONCLUSION - `+0x04` POINTER-ARRAY RELATIONSHIP: CONFIRMED.** `+0x04`
is an index into a 4-byte-entry pointer array, and the address it selects is
`u32 at 0x086B6BB4 + 4 * +0x04`. Every one of the 232 records selects a word
that is a valid ROM pointer.

### 10.3 Where the pointer array actually begins, and the disagreement

**EXTERNAL CLAIM (LOGExtractor).** The table is at `0x6B6BB4`.

**PROJECT OBSERVATION.** Two descriptions of the same arithmetic are possible,
and the ticket states both rather than picking one silently:

| Reading | Base | Index offset | First entry | Entries |
| --- | --- | --- | --- | --- |
| **A** - the accessor's arithmetic base | `0x086B6BB4` | `0` | `0x086A6424` | the 10 words at `0x086B6BB4` are **4 ascending valid pointers and 6 nulls**, then the contiguous run continues from `0x086B6BDC` |
| **B** - the contiguous valid run | `0x086B6BDC` | `10` | `0x086A89D0` | **297** entries, all valid ROM pointers, strictly ascending, terminated by `0x03001068` at `0x086B7080`, which is not a ROM address |

Reading B is the base this project already accepted independently in
TOOLKIT-010 (`GRAPHICS_FORMAT.md`: "character pointer table `0x006B6BDC`, 297
entries, all 297 valid ROM pointers, strictly ascending"). Reading A is what
LOGExtractor published. They are **not in conflict about the data**; they differ
about which byte is called "the table". Under the accessor, ids 0..9 never reach
the table at all, so reading A's first ten slots are unreachable through this
accessor; under reading B the last id the canonical table uses (306) lands
exactly on the last entry (296 + 10).

**PROJECT CONCLUSION - `0x6B6BB4` POINTER-ARRAY RELATIONSHIP: PARTIALLY
CONFIRMED.** The relationship `+0x04 -> 4-byte-entry pointer array -> one
pointer` is **CONFIRMED**; the identification of the array's first entry is
**UNRESOLVED**, with the project's accepted `0x086B6BDC`/297 contradiction-free
reading given precedence and LOGExtractor's `0x086B6BB4` recorded as the
accessor's compiler-folded base. Resolving which byte is the array's first entry
needs the entry layout and is handed to LOGX-SPRITE-001 (section 16).

### 10.4 The `f(0x95)` / `f(0x92)` substitution

`0x08027948` maps its argument 1 through the same accessor before comparing
(`0x0802794E..0x0802795E`): if `f(0x95) == argument`, the argument is replaced by
`f(0x92)`. Both constants are >= 10, so both are table ids. Their meaning is
**UNKNOWN**; what is established is that the engine treats the record field and
the caller's id as interchangeable *identifiers* mapped through one function, and
that the comparison is between **pointer values**, not raw ids.

---

## 11. RECORD `+0x08` AND ITS POINTER ARRAY

### 11.1 Physical field and accessor

`+0x08` is read as a full 32-bit value with `ldr r0, [r7, #8]` (`0x080250CA`).
Its 111 distinct values are `0` plus a **110-element subset of `8..162`**: exactly
one of the distinct values is zero (98 of the 232 *records* carry it) and none is
in `1..7`, so 45 of the array's 155 valid slots are unused by the table.

```text
08011f20  cmp   r0, #0
08011f22  beq   0x08011f28          ; slot 0  -> return 0
08011f24  cmp   r0, #7
08011f26  bne   0x08011f2c
08011f28  movs  r0, #0
08011f2a  bx    lr                  ; slot 7  -> return 0
08011f2c  cmp   r0, #8
08011f2e  bge   0x08011f52
08011f30  ...                       ; slots 1..6 -> a party-record path
08011f52  ldr   r1, [pc, #0x240]    ; pool 0x08012194 = 0x086F393C
08011f54  lsls  r0, r0, #2
08011f56  ldr   r0, [r1, r0]
08011f58  bx    lr
```

`0x08011F20` has three `BL` callers: `0x0801548E`, `0x080250D2` and `0x0802605C`.

**PROJECT CONCLUSION - `+0x08` POINTER-ARRAY RELATIONSHIP: CONFIRMED.** `+0x08`
is an index into the 4-byte-entry pointer array at `0x086F393C`; slot 0 returns
zero without reading the array. Every non-zero `+0x08` in the canonical table
selects a valid ROM pointer.

### 11.2 The `0x6F393C` array lead

**EXTERNAL CLAIM (LOGExtractor).** A portrait pointer table at `0x6F393C`.

**PROJECT OBSERVATION.** `0x086F393C` is the accessor's own literal (pool word
`0x08012194`), so the external address is exact. Read as raw words:

| | Value |
| --- | --- |
| slots 0..7 | all `0x00000000` (observed; the accessor returns 0 for 0 and 7 without reading the array) |
| slots 8..162 | **155** entries, all valid ROM pointers, strictly ascending, `0x086B880C .. 0x086F3360` |
| slot 163 | `0x0011E502`, **not a ROM address** - the array ends here |
| `+0x08` values used by the table | `0` plus a 110-element **subset** of the 155 valid slots; the maximum is 162, the last valid slot |

**PROJECT CONCLUSION - the `+0x08` pointer array: CONFIRMED** as the array the
field reaches, at the exact externally published address, 163 slots wide with
slots 0..7 zero. The field's value set is a strict **inclusion** in the valid
slots, not the whole of them - a base or width error would move values outside
the run, so the inclusion is still discriminating, but it is not an equality.

**EXTERNAL CLAIM (LOGExtractor).** The portrait entries are portrait graphics.

**PROJECT CONCLUSION - `+0x08` SEMANTIC (LOGExtractor: "portrait"): PARTIALLY
CONFIRMED.** The consumer `0x08025056` passes the accessor's result to the
Webfoot container dispatcher `0x0803D940` at `0x080250D6`, i.e. it is consumed as
a resource, and the first word at each target (`0x086B880C`, `0x086B8D90`,
`0x086B93F8` -> `01 00 00 00 00 10 00 00 ...`) has the same shape for all three.
No pixel format, dimension or rendering claim is made here; graphics
identification belongs downstream.

---

## 12. RECORD `+0x0C`

### 12.1 Physical access

`+0x0C` is read as a full 32-bit value with `ldr r1, [r0, #0xc]`
(`0x080279AA`) and `ldr r0, [r6, #0xc]` (`0x08027974`), and immediately tested
with `cmp r1, #0` / `blt`, i.e. **signed**. No `ldrh`, `ldrb` or `ldrsh` reads
any part of the field, and no consumer reads it as two subfields.

### 12.2 The consumer and the target

`0x08027948` computes `0x08711274 + 28 * +0x0C` (`lsls #3`, `subs` -> `*7`,
`lsls #2` -> `*28`, `adds` the literal) and compares the result with its second
argument. `0x08711274` is the base of the table already accepted by TOOLKIT-009
as the enemy-stat / placement-type table, stride `0x1C`, 141 records, with
`max_selector` 149.

**PROJECT OBSERVATION (distribution).**

| Quantity | Value |
| --- | ---: |
| records with `+0x0C < 0` | **88** |
| distinct negative values | `-1 .. -9` |
| records with `+0x0C >= 0` | **144** |
| distinct non-negative values | **123** |
| minimum / maximum non-negative | `0` / `149` |
| records with `+0x0C == 0` | 1 (record 0) |
| values at or above the accepted 141-record extent | `142, 143, 145, 146, 147, 148, 149` (records 220, 221, 222, 224, 225, 227, 228, 231); **141 and 144 are unused** |

**PROJECT CONCLUSION - `+0x0C` PHYSICAL STRUCTURE: CONFIRMED** as one signed
32-bit value. **PROJECT CONCLUSION - `+0x0C` SEMANTIC: PARTIALLY CONFIRMED.** It
is a **signed index into the 28-byte-record table at `0x08711274`**; a negative
value is one the engine **skips** (`blt` at `0x080279AE`, forming no address at
all) and `-1` is the most common such value. The evidence is the engine's own
address computation plus that signed test, not the numeric clustering, and the
field is *not* described as a stat id, a class, a faction or a playable flag: no
consumer was found that reads the target's contents in a way this ticket could
classify. The value range also means the eight records above address bytes past
the 141-record extent TOOLKIT-009 validated; they are recorded as an anomaly and
handed on, not promoted into records.

### 12.3 Negative coverage for `+0x0C`

Only `0x08027948` was found reading `+0x0C`. Scope of that finding:

- The table is reachable only through an address. Every address-producing site
  for it is either one of the **8** `ldr`-literal sites of section 5 or a folded
  base in the reported neighbourhood; the whole image was scanned at every even
  offset for the literal form, and the 16-bit `adr` and ARM forms were checked
  over the only range from which they could reach (section 5.1).
- Inside each of the six consuming functions, every `ldr`/`ldrh`/`ldrb` with a
  constant immediate on a record-derived base was enumerated by reading the
  function in full; the fields actually read are `+0x00` (2 sites), `+0x02`
  (3 sites), `+0x04` (2 sites), `+0x08` (1 site) and `+0x0C` (1 function).
- **Aggregate access:** no `ldm`/`stm` reads a record base in any consuming
  function. A record is always loaded field by field.
- **Not covered, and therefore excluded from the claim:** a base-adjusted access
  that first adds or subtracts a constant larger than the neighbourhood scan, or
  that stores the record address into a structure in one function and reads it in
  another through an offset this ticket did not follow. `0x08025E50` does store a
  record pointer into `object + 0x20` (`0x08025E9A`) and read `+0x02` from it
  later (`0x08025EC2`), so the pattern exists; no other stored record pointer was
  traced.

The claim made is therefore: *"within the six enumerated consumer functions, and
for every address-producing site the scans in section 5 cover, `+0x0C` has one
consumer"*, not "`+0x0C` has no other consumer".

---

## 13. FULL-TABLE CENSUS

Population: **232 records** at `0x0874D380`, stride `0x10`, file offsets
`0x74D380..0x74E1F0`. Reproduce with
`python -m tools.research.logx_char_probe <rom> --rows`.

### 13.1 Per-field arithmetic

| Field | Width | Distinct values | Zero-valued records | Minimum | Maximum |
| --- | --- | ---: | ---: | ---: | ---: |
| `+0x00` | `u16` | **154** | 0 | 986 | 1310 |
| `+0x02` | `u16` | **154** | 0 | 987 | 1311 |
| `+0x04` | `u32` | **198** | **0** | 12 | 306 |
| `+0x08` | `u32` | **111** | **98** | 0 | 162 |
| `+0x0C` (signed) | `i32` | **132** | 1 | -9 | 149 |

`+0x02` is `+0x00 + 1` on all 232 records, so the two text fields have the same
population and the same distinct count. Every text index is inside the accepted
1,534-entry table, so there are **no invalid text references**.

**Distinct indices are not distinct strings.** Three of the 154 `+0x00` slots
(`1038`, `1040`, `1042`) hold the identical text `"Super Buu"`, so the 154
indices resolve to **152** distinct strings, while still resolving to 154 distinct
*pool addresses*. The `+0x02` field is shared far more widely: its 154 distinct
indices resolve to **104** distinct strings. Both counts are emitted by the probe
(`distinct_text_strings`) so neither reading can be quoted as the other.

### 13.2 References and unique targets

Keeping references distinct from targets:

| Field | References | Unique values/ids/slots | Unique resolved targets (pool addresses) | Distinct strings |
| --- | ---: | ---: | ---: | ---: |
| `+0x00` -> text table | 232 | 154 | 154 | **152** |
| `+0x02` -> text table | 232 | 154 | 154 | **104** |
| `+0x04` -> `+0x04` pointer array | **232** | **198** | **198** | - |
| `+0x08` -> `+0x08` pointer array | **134** (98 records use 0) | **110** | **110** | - |
| `+0x0C` -> stat table | **144** (88 negative) | **123** | **123** | - |

No two distinct `+0x04` values resolve to the same pointer, and no two distinct
`+0x08` values do either: sharing happens at the *value* level (232 references
over 198 ids) and never as an aliased pointer. Text is the exception, and it is
recorded separately above: text slots alias at the **content** level.

### 13.3 Duplicates and aliases

**PROJECT OBSERVATION.** Exactly **one** pair of records is byte-identical in all
five fields:

| Records | Text pair | `+0x04` | `+0x08` | `+0x0C` |
| --- | --- | ---: | ---: | ---: |
| 80, 81 (`"Gunman"`) | 996 / 997 | 137 | 0 | 44 |

All other repetition is a **partial** match, and the dominant pattern is a
variant family: several records with the same text pair that differ in `+0x04`
and/or `+0x08`. Examples measured directly, with the measured value sets rather
than ranges (an ellipsis would imply values that are not used):

| Family | Records | Shared | Differing |
| --- | --- | --- | --- |
| `"Gohan"` | 49-57 (9 records) | text 1186/1187 | `+0x0C = -3` on 49-56 but **`+0x0C = 35` on record 57**; `+0x04` {107,108,109,110,111,112,113,114}; `+0x08` {39,43,45,46,47,49,51,54} |
| `"Goku"` | 58-63 (6 records) | text 1188/1189, `+0x0C = -2` | `+0x04` {115,117,118,119,120,121}; `+0x08` {57,60,61} |
| `"Babidi"` | 8, 9, 10 | text 1026/1027, `+0x04 = 28`, `+0x08 = 12` | `+0x0C` {4, 25, 29} |
| `"Super Buu"` | 184-187 | text 1038/1039, `+0x04 = 49`, `+0x08 = 127` | `+0x0C` {115, 116, 117, 121} |

**PROJECT CONCLUSION.** Duplicate *resource references* are sharing, not aliasing:
the engine compares resolved pointer values (`0x0802796E cmp r0, r7` after both
sides pass through `0x08000158`). When the search is called with a null second
argument, records that share `+0x04` are indeed indistinguishable by it; when a
stat-record pointer **is** supplied, the code at `0x08027972..0x08027988` also
requires `+0x0C >= 0` and `0x08711274 + 28*(+0x0C) == argument`, so records that
differ in `+0x0C` **are** distinguished. Whether a variant family is a
transformation chain, an alternate costume or simply several placements of one
enemy is **UNKNOWN**; no engine code was found that orders or groups the family,
and a shared `+0x0C` value only says they point at the same 28-byte record.

---

## 14. TABLE SEMANTIC SCOPE

**PROJECT OBSERVATION (verbatim).** The `+0x00` field holds 154 distinct text
indices over the 232 records, resolving to 152 distinct strings. Resolved through
the accepted text codec, those strings are, verbatim, the game's own labels:
`"Goku"`, `"Vegeta"`, `"Piccolo"`, `"Hercule"`, `"Supreme Kai"`, `"Zombie"`,
`"Nosferatu"`, `"Goon"`, `"Bruiser"`, `"Laser Turret"`, `"Ion Cannon"`,
`"War Machine"`, `"Grand Mechanoid"`, `"Worm Head"`, `"Worm Body"`, `"Worm Tail"`,
`"Janemba Hand"`, `"Kid Buu"`, `"Super Buu"`, `"Gotenks"`, `"Vegito"`,
`"Majin Vegeta"`, `"Human"`, and so on. `"Human"` is used by 16 records whose
`+0x02` reads "The Capsule Corporation database has no information on this
person."

**PROJECT CONCLUSION - what this establishes.** The label set is **not** a
playable roster: a roster would not carry `"Laser Turret"`, `"Worm Body"` or
`"Ion Cannon"`. That refutation is sound because it uses the strings to *exclude*
a reading, not to assert one.

**PROJECT CONCLUSION - what this does not establish.** It is **not** established
that the table is a complete or global registry of named entities, and the four
attributes are not universal. Measured counterexamples: **98 of 232** records
carry `+0x08 == 0` (the accessor returns 0 without reading the array, i.e. no
slot), **88 of 232** carry `+0x0C < 0` (the search skips them, i.e. no stat
record), and **93** records have no slot while still having a stat index. The
supported formulation is:

> a table of **named appearance definitions**, each carrying a label text index,
> an adjacent second text index, an appearance id, and **optional** slot and
> stat-record indices, spanning named fighters, generic enemies, machinery and
> body parts.

whether it is *complete*, and which records are props, duplicates or unused, is
**UNKNOWN**. The engine's own behaviour is consistent with the neutral reading
without proving completeness: the roster code at `0x08024F3C` intersects the
table with a runtime bitmap rather than enumerating it, so the table's extent is
a superset of whatever that bitmap can set. **UNRESOLVED:** which records the
bitmap ever sets. That requires a save-state or gameplay census and was not
attempted here.

---

## 15. TABLE BOUNDARIES

| Direction | Structure | Evidence |
| --- | --- | --- |
| below | a 4-byte table `00 03 01 02` at `0x0874D35C`, indexed `& 3` | literal load at `0x0802734C` (pool `0x08027388`), `lsls #0x17`/`lsrs #0x1e` mask |
| below | an 8-entry `u32` pointer table at `0x0874D360`, indexed `& 7` | literal load at `0x08027494` (pool `0x080274B0`), `lsls #0x1b`/`lsrs #0x1d` mask |
| above | `0x03001C4C` at `0x0874E200`, followed by IWRAM addresses and negative words | raw read |

The 8-entry pointer table ends exactly at the first record's first byte
(`0x0874D360 + 8*4 = 0x0874D380`), and the 4-byte table ends exactly where the
8-entry table begins. **PROJECT OBSERVATION (invariants).** Record 232 reads
`+0x00 = 7244` (outside 0..1533), `+0x02 = 768` (not `+0x00 + 1`), and
`+0x04 = 0x030019A4` (an IWRAM address, not a table id), so the first candidate
beyond the count fails **three** of the four invariants that hold on all 232
accepted records. Its `+0x08 = 0` happens to satisfy the fourth.

**PROJECT CONCLUSION - boundary: CONFIRMED as corroboration, not as the count
proof.** The count is proved by the engine's own loop bounds (section 7); the
boundary shows that stopping there lands on a real edge rather than mid-run.

---

## 16. HANDOFFS

**To LOGX-SPRITE-001** (details deliberately not reconstructed here):

- The accessor is `0x08000158`; its arithmetic is
  `u32 at 0x086B6BB4 + 4*id` for `id >= 10`, with the loaded literal
  `0x086B6BDC` and a folded `-0x28`; `0x0801713C` is the party-record entry to
  the same table.
- The ID space observed in this table is `12..306`; `0x08027948` also uses the
  constants `0x95` and `0x92`.
- The project's accepted base is `0x086B6BDC` with **297** entries, strictly
  ascending, terminated by `0x03001068` at `0x086B7080`. LOGExtractor's
  `0x086B6BB4` is the accessor's folded base. **Resolving which byte is the
  array's first entry needs the object layer.**
- The ten words at `0x086B6BB4..0x086B6BD8` are `0x086A6424`, `0x086A7238`,
  `0`, `0`, `0x086A7E7C`, `0`, `0`, `0`, `0`, `0x086A899C` - **four** valid
  ascending pointers and **six** nulls.
- The boundary cases are: entry 0 at `0x086B6BDC`, value `0x086A89D0`; entry 296
  at `0x086B707C`, value `0x086B6B60`; the terminator word `0x03001068` at
  `0x086B7080`; and the last graphics structure `0x086B6B60` itself.
- The record's `+0x04` is a **u32 id**, not a pointer, in all 232 records.

**To LOGX-FRAME-001:** nothing in this ticket constrains frame or multipart
graphics; the `+0x08` array's targets were located but not decoded.

**Other downstream:**

- The `+0x0C` -> `0x08711274` relation now links these appearance-definition
  records to the placement/type table TOOLKIT-009 accepted; a ticket that wants
  "placement -> appearance definition" has both ends and can join them.
- The `"Human"` catch-all (16 records, one shared `+0x02` string) and the fact
  that three `+0x00` slots hold one identical string are text-table facts
  (TOOLKIT-004 territory) only in that they resolve.
- `0x08711274` values `142, 143, 145, 146, 147, 148, 149`: TOOLKIT-009 recorded
  indices at and above the validated extent as reference-only. The character
  table uses exactly those, and not `141` or `144`, which is corroboration, not a
  new record claim.

---

## 17. EVIDENCE CLASSIFICATION

| Claim | Status |
| --- | --- |
| TABLE START at `0x0874D380` (file `0x74D380`) | **CONFIRMED** |
| TABLE STRIDE `0x10` | **CONFIRMED** |
| TABLE COUNT 232, index 231 last, 232 outside | **CONFIRMED** |
| TABLE SEMANTIC IDENTITY "named appearance definitions addressed by an appearance id and a stat-record pointer, with optional slot and stat indices" | **PARTIALLY CONFIRMED** |
| `+0x00` physical field: `u16` | **CONFIRMED** |
| `+0x00` text relationship: index into `0x0806BCE8` | **CONFIRMED** |
| `+0x00` character-name semantic | **PARTIALLY CONFIRMED** |
| `+0x02` physical field: `u16` | **CONFIRMED** |
| `+0x02` text relationship: index into `0x0806BCE8` | **CONFIRMED** |
| `+0x02` semantic = prose description | **PARTIALLY CONFIRMED** |
| `+0x02` is skipped/inert | **REFUTED** |
| `+0x04` physical field: `u32` index | **CONFIRMED** |
| `+0x04` pointer-array relationship (LOGExtractor's "sprite table") | **CONFIRMED** |
| `+0x04` sprite-definition semantic | **PARTIALLY CONFIRMED** |
| `+0x08` physical field: `u32` index | **CONFIRMED** |
| `+0x08` pointer-array relationship (LOGExtractor's "portrait table") | **CONFIRMED** |
| `+0x08` portrait semantic | **PARTIALLY CONFIRMED** |
| `+0x0C` physical structure: one signed `i32` | **CONFIRMED** |
| `+0x0C` semantic: signed index into `0x08711274` (stride `0x1C`); a negative value is skipped by the engine | **PARTIALLY CONFIRMED** |
| `0x6B6BB4` pointer-array relationship | **PARTIALLY CONFIRMED** (arithmetic base confirmed; which byte is the first entry UNRESOLVED) |
| `0x6F393C` pointer-array relationship | **CONFIRMED** |
| homogeneous record interpretation (all five fields at fixed offsets for all 232) | **CONFIRMED** |
| duplicate/alias semantics | **PARTIALLY CONFIRMED** (sharing confirmed at the value level and text content aliases; family meaning UNKNOWN) |
| LOGExtractor address notation is file-relative | **CONFIRMED** |

---

## 18. TOOLING AND TESTS

`tools/research/logx_char_probe.py` is SHA-256 gated, read-only and deterministic.
Its **field** API is purely positional (`text_index`, `text_index_2`, `field_04`,
`field_08`, `field_0c`), and the two pointer arrays are named after the field that
selects them (`FIELD_04_*`, `FIELD_08_*`, `field_04_target`, `field_08_target`)
rather than after their targets, because the target semantics are only
partially confirmed. Two of the `CensusLimits` bounds (`field_04_entry_count` 297
and `field_08_last_valid_slot` 162) are measured pointer-run extents rather than
engine bounds, and the class docstring says so.

- `tests/integration/test_logx_char_rom.py` (ROM-gated, skips cleanly without the
  private image) asserts the eight literal sites, every quoted instruction (37 of
  them), the eight stride sites, the count instructions, the search function's
  `-1` epilogue, representative raw records, the three-invariant failure of
  record 232, the census arithmetic, the distinct-string counts, the duplicate
  pair, all three field-to-array relationships, text resolution, both pointer
  arrays' shapes, the boundaries, determinism and the canonical gate.
- `tests/unit/test_logx_char_reference.py` (portable) exercises the census
  reference and the guard rails on synthetic rows, checks that the two kinds of
  census bound stay named apart, and asserts that no probe or test identifier
  promotes the partially confirmed target semantics. It embeds no ROM bytes, no
  ROM payload hash and no decoded string.
