# Portrait-run completeness (PORTRAIT-COMPLETENESS-001)

Does the 155-entry portrait container run reached through the pointer array at
`0x086F393C` completely account for the portrait references the game's appearance
definitions carry?

**Answer: YES for that population, and it is proven by exhaustive enumeration
rather than by plausible counts.** The run is a strict **superset** of the
referenced portraits: every one of the references resolves inside it, and **45**
of its 155 entries are not referenced by any appearance definition.

This record also corrects a premise. The portrait field is `+0x08` of the
**232-record appearance-definition table at `0x0874D380`**, not of the
**297-entry pointer run at `0x086B6BDC`**. Those are two different structures and
earlier notes conflated them.

Measured read-only against the canonical image `buus_fury_usa_rev0_01c1707f`,
SHA-256 `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`,
verified unchanged before and after. Addresses are GBA addresses; a file offset is
the address minus `0x08000000`. Instruction listings show raw **halfwords**, in
the image's own byte order.

---

## 1. Which record carries the portrait field: CONFIRMED

The question is decidable from the image, and it was not taken from a document.
The consumer `0x08025056` builds the record base and reads the field:

```text
address   halfword   instruction
08025086  49a2       ldr  r1, [pc, #0x288]     ; pool 0x08025310 = 0x0874D380
08025088  0100       lsls r0, r0, #4           ; index * 16  (the record stride)
0802508a  1847       adds r7, r0, r1            ; r7 = 0x0874D380 + 16*index
080250ca  68b8       ldr  r0, [r7, #8]          ; the portrait field
080250d2  f7ec ff25  bl   0x08011F20            ; -> the portrait pointer array
```

Every halfword above is asserted by `portrait_field_evidence` and re-checked by
`tests/integration/test_logx_portrait_rom.py`, so the binding cannot drift from
the image. The `lsls r0,r0,#4` scale is the same 16-byte stride LOGX-CHAR-001
established from eight engine sites, and the pool word is the table's own base.
The call target is decoded from the instruction, not assumed: `0xF7EC/0xFF25` is
an ARMv4T `bl` to `0x08011F20`.

**EXTERNAL NAME (LOGExtractor)** calls the `0x086B6BDC` structure the
sprite-definition pointer table and `0x086F393C` the portrait pointer table. The
project's accepted reading (LOGX-SPRITE-001) keeps `0x086B6BDC` as the **`+0x04`
target run**, and LOGX-CHAR-001 s11 binds `+0x08` to the `0x086F393C` array. This
ticket adds the measurement that makes the population unambiguous: the field read
into the accessor belongs to the **232-record** table.

**PROJECT CONCLUSION - the population that carries the portrait field:
CONFIRMED** as the 232-record appearance-definition table at `0x0874D380`,
stride `0x10`, field `+0x08`.

### 1.1 The 297-entry run does not carry the field

`definition_run_portrait_field_report` reads `+0x08` of every record the
297-entry run at `0x086B6BDC` points at:

| Measure over the 297 records | Value |
| --- | --- |
| distinct `+0x08` values | 16 |
| zero values | 7 |
| non-zero values in the portrait slot range `8..162` | **0** |
| carries portrait slot indices | **False** |

Seven records read `0`; the remaining 290 read values such as `0x040A0810`, which
is not a slot index into any 163-entry table. **The 297-entry run is not the
portrait-reference population**, and "297 appearance definitions" is a
conflation of the `+0x04` run with the appearance-definition table.

---

## 2. The appearance-definition population: CONFIRMED

Reused from the accepted census (`tools/research/logx_char_probe.py`, LOGX-CHAR-001)
rather than re-derived, so a second copy of a proven constant cannot drift:

| Measure | Value |
| --- | --- |
| table address | `0x0874D380` |
| record stride | `0x10` |
| records | **232** |
| portrait field | `+0x08`, read as a full 32-bit word (`ldr r0, [r7, #8]`) |

The count `232` is the **census / loop bound**, and its provenance is stated
precisely rather than rounded: LOGX-CHAR-001 section 7 measures two `cmp r4, #0xe8`
loops at `0x08027998` and `0x080279CC` and one `cmp r0, #0xe8` loop at
`0x08024F92`, each an exclusive bound starting at zero, plus a 232-bit runtime
bitmap walked by `0x08024F3C`. The portrait consumer `0x08025056` itself carries
**no bound check**: it takes its index from a runtime object field, so `232` is
the population the table is defined with, not one this consumer enforces. An
index outside the table is not something this ticket measured, and it is not
claimed to be impossible.

Census of the field across all 232 records:

| Measure | Value |
| --- | --- |
| records with a portrait reference (non-zero `+0x08`) | **134** |
| records with no portrait reference (`+0x08 == 0`) | **98** |
| distinct non-zero references | **110** |
| minimum / maximum reference | **8 / 162** |
| references in the reserved range `1..7` | **0** |
| references above `162` | **0** |

---

## 3. The run: REPRODUCED, unchanged

`tools/research/logx_portrait_probe.py` reproduces GRAPHICS-COVERAGE-001 exactly:
base `0x086F393C` read from the accessor's own pool word `0x08012194`; slots 0..7
zero; slots 8..162 hold **155** strictly ascending, in-image pointers
`0x086B880C .. 0x086F3360`; slot 163 holds `0x0011E502`, which is not a ROM
address. All 155 containers are kind 1, declare 4,096 bytes, decode to 4,096
bytes, with **0** decode failures.

Note the two addresses are different things: `0x086F393C` is the **pointer-array
base**, while the **containers** it points at occupy `0x086B880C..0x086F3938`.

Two structural observations that bound the array, recorded because the count is
data-bounded rather than engine-declared:

- The 155 containers are **contiguous** in `0x086B880C .. 0x086F3938`; measured
  gaps between consecutive containers are only `0` or `4` bytes, and the last
  container's packed end is exactly **4 bytes before** the array base.
- Slot 163 is followed not by pointers but by a different structure. Read as
  halfwords from `0x086F3BC8` the image holds `E502 0011 020A 11E0 E702 0211 ...`,
  i.e. the 32-bit `0x0011E502` and then a run of never-in-ROM halfword pairs. The
  non-pointer word at 163 therefore terminates the array rather than being a lone
  non-pointer inside it.

**PROJECT CONCLUSION - the run: CONFIRMED** at 155 entries, slots `8..162`.

---

## 4. The join: CONFIRMED

`portrait_reference_report` joins the field to the run. The arithmetic lives in
the pure function `join_portrait_references`, so its failure branches are unit
tested without a ROM.

| Measure | Value |
| --- | --- |
| appearance definitions | **232** |
| with a portrait reference | **134** |
| without a portrait reference | **98** |
| unique portrait references | **110** |
| references resolving **inside** the run | **134 / 134** |
| references pointing **outside** the run | **0** |
| references in the reserved slots `1..7` (cannot select a run entry) | **0** |
| run entries referenced | **110** |
| run entries **unused** by appearance definitions | **45** |

The three buckets account for every non-zero field: `134 = 134 + 0 + 0`. The keys
say which range they describe: `min_in_run_reference` / `max_in_run_reference`
describe the references the run must cover, while `min_non_zero_reference` /
`max_non_zero_reference` describe the whole non-zero population, so a value
outside the run can never hide behind a range that reads like a population
extremum.

The 45 unused slots are `13, 18, 27, 28, 30, 31, 34, 36, 37, 38, 40, 41, 42, 44,
48, 50, 52, 53, 55, 56, 58, 59, 64, 67, 70, 71, 75, 79, 92, 101, 111, 116, 122,
123, 125, 128, 130, 132, 138, 139, 141, 142, 143, 145, 148`.

**PROJECT CONCLUSION - COMPLETENESS OF REFERENCE COVERAGE: CONFIRMED.** The
155-entry run accounts for **every** appearance-definition portrait reference.
Nothing the appearance table asks for falls outside it.

### 4.1 What that does *not* establish

- **The run is a strict superset, not an equality.** 45 run entries carry no
  appearance-definition reference. Being unreferenced is not evidence they are
  not portraits: measured on the same run they are container kind 1, declare and
  decode to exactly 4,096 bytes, and sit interleaved inside the same contiguous
  packed block as the referenced entries. Their consumer is **UNKNOWN**.
- **Render identity is not claimed.** Palette, dimensions and on-screen
  placement remain UNKNOWN, as GRAPHICS-COVERAGE-001 recorded. The 64x64 @ 8bpp
  reading of the 4,096-byte payload stays INFERRED.
- **The array's own width is still data-bounded.** No engine upper-index clamp
  was found; `155` is the measured run extent. It is corroborated by the block
  layout in section 3, not by an engine-declared length.

---

## 5. The accessor's three callers: every slot source, and none escapes the run

The accessor `0x08011F20` dispatches on its argument: slot `0` returns 0 without
reading the array, slot `7` returns 0 likewise, slots `1..6` take a party path,
and slots `>= 8` index the array with `lsls r0,r0,#2` / `ldr r0,[r1,r0]` and **no
upper clamp**. An independent resynchronising halfword scan finds exactly **three**
`bl` sites targeting `0x08011F20`, and no indirect code pointer to it.

Each caller's slot source matters, because "no reference escapes the run" is only
as strong as the set of sources it covers. All three were read:

| Caller | Slot source | Status |
| --- | --- | --- |
| `0x080250D2` | `[0x0874D380 + 16*index + 8]`, the **appearance-definition `+0x08`** of section 1 | CONFIRMED |
| `0x0802605C` | `[[object+0x20] + 8]`, where `0x08025E9A` stored `0x0874D380 + 16*index` (pool `0x0802618C` = `0x0874D380`) into `[object+0x20]`, the **same appearance-definition `+0x08`**, reached through an object cache | CONFIRMED (source); reachability UNKNOWN |
| `0x0801548E` | `[0x086B82EC + 24*index + 0x10]` (pool `0x080154B8` = `0x086B82EC`), the **party table's slot-1 byte**, i.e. the party path with slot hard-coded to 1 | CONFIRMED |

So there is **no third distinct slot source**: callers 1 and 2 both resolve the
appearance table's `+0x08`, and caller 3 resolves the party table measured below.

One bounded uncertainty is recorded rather than implied. Caller `0x0802605C` sits
in the function at `0x08026048`, and **no `bl`, `b`/conditional branch or
pointer-table entry referencing `0x08026048` was found**, so whether that path is
reachable at runtime is **UNKNOWN**. It does not affect the result: whatever
reaches it supplies the appearance table's own `+0x08`, which section 4 already
covers in full.

### 5.1 The party path

For slots `1..6` the accessor itself resolves the slot through a byte of the
24-byte-stride table at `0x086B82EC` (pool `0x08012190`):

```text
address   halfword   instruction
08011f30  4996       ldr  r1, [pc, #0x258]     ; 0x0801218c = 0x08072890
08011f32  2368       movs r3, #0x68            ; 104-byte record stride
08011f34  6809       ldr  r1, [r1]             ; -> EWRAM roster base
08011f36  780a       ldrb r2, [r1]             ; roster count
08011f38  435a       muls r2, r3, r2
08011f3a  1851       adds r1, r2, r1
08011f3c  229f       movs r2, #0x9f
08011f3e  00d2       lsls r2, r2, #3           ; 0x4F8
08011f40  1889       adds r1, r1, r2
08011f42  7d09       ldrb r1, [r1, #0x14]      ; -> a party-table record index
08011f44  4a92       ldr  r2, [pc, #0x248]     ; 0x08012190 = 0x086B82EC
08011f46  004b       lsls r3, r1, #1
08011f48  1859       adds r1, r3, r1            ; 3 * index
08011f4a  00c9       lsls r1, r1, #3            ; 24 * index
08011f4c  1889       adds r1, r1, r2            ; 0x086B82EC + 24*index
08011f4e  1808       adds r0, r1, r0            ; + slot (1..6)
08011f50  7bc0       ldrb r0, [r0, #0xf]        ; -> a portrait slot
08011f52  4990       ldr  r1, [pc, #0x240]      ; 0x08012194 = 0x086F393C
08011f54  0080       lsls r0, r0, #2
08011f56  5808       ldr  r0, [r1, r0]
```

The effective byte offset is `0x0F + slot`, so slots `1..6` read offsets
`0x10..0x15` of the record. `0x0801213E`, the second literal site that loads the
array base, is an **inline duplicate** of this same computation inside another
function, not a third distinct source.

`other_portrait_slot_sources` measures this table from the image: **54** whole
24-byte records before the first portrait container, and across the six slot
offsets **60 distinct values, `0 .. 159`**. **None reaches 163**, so this source
does not escape the run either. The table's identity as a party/roster record
table is **INFERRED**; the instructions that index it are CONFIRMED.

Two bounds on that statement are recorded rather than left implicit:

- The measurement takes **every** record in the table, which is a **superset** of
  the records a runtime index can select, so it is a bound and not an
  enumeration of what the game actually uses.
- Both this path and caller `0x0801548E` index `0x086B82EC` from **unclamped
  runtime bytes** (an EWRAM roster byte and `[object+0x14]`), so "reads only
  in-run values" is **INFERRED** from the table's contents, not engine-bounded.

Including this source, the union of all portrait-slot sources found covers **133**
of the 155 run entries, leaving **at least 22** entries referenced by no
portrait-slot source located here. The 22 figure is a lower bound, for the
superset reason above.

### 5.2 Literal-reference coverage, stated rather than assumed

A raw halfword scan of every even offset for the `ldr Rt,[pc,#imm]` encoding finds
exactly **two** sites in the image whose pool word is `0x086F393C`, both from pool
`0x08012194`: the accessor at `0x08011F52` and the inline party path at
`0x0801213E`. The same scan finds **eight** sites for the appearance table
`0x0874D380`, reproducing LOGX-CHAR-001 section 5.

This scan is resynchronising by construction (it tests the encoding at every even
offset rather than walking control flow), so it does not carry the linear-sweep
false negative `docs/research-conventions.md` warns about. Its **coverage gap** is
reported alongside its result by `other_portrait_slot_sources`: it sees only the
`ldr Rt,[pc,#imm]` form. An `add Rd,pc,#imm`, ARM-state, or register-computed base
would not appear, so the result is evidence of two *literal* sites, not proof that
no other code reaches the array.

---

## 6. Verdict

**PORTRAIT COMPLETENESS: PROVEN**, for this population:

> the portrait references carried by the `+0x08` field of the 232
> appearance-definition records at `0x0874D380`: 134 references over 110 distinct
> slots, are all resolved by the 155-entry portrait container run reached through
> the pointer array at `0x086F393C`, with zero references outside it.

The 155-entry run is a **superset** of the referenced portraits, not an equality:
45 entries carry no appearance-definition reference and at least 22 carry no
reference from any portrait-slot source located in this ticket.

---

## 7. Reproduction

```text
.venv/Scripts/python.exe -m tools.research.logx_portrait_probe "roms/Dragon Ball Z - Buu's Fury (U).gba" --references
```

emits the join, the corrected 297-entry cross-check, the derived engine binding
and the `other_portrait_slot_sources` block, that is, every **count** in sections
1.1, 2, 3, 4 and 5.1: `appearance_record_count: 232`, `run_entry_count: 155`,
`with_reference: 134`, `without_reference: 98`, `unique_references: 110`,
`references_inside_run: 134`, `references_outside_run: 0`, `run_entries_unused: 45`,
`carries_portrait_slot_indices: false`, `party_records_scanned: 54`,
`party_max_slot: 159`, `array_base_literal_site_count: 2`,
`appearance_table_literal_site_count: 8`, `union_run_entries_covered: 133`,
`run_entries_covered_by_no_source: 22`.

The per-caller table in section 5 is **not** probe output: it was read with a
disassembler at the instruction sites quoted there, and its halfwords are
re-checked from the image by `portrait_field_evidence` and the integration suite.

Portable synthetic coverage is `tests/unit/test_logx_portrait_probe.py`; the
canonical ROM-gated evidence is `tests/integration/test_logx_portrait_rom.py`.
