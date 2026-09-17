# LOGX-CHAR-001: reconstruct Buu's Fury character table / character-definition records

**Research only. Integrated to `master` through the closeout merge recorded in
[archive/LOGX-CHAR-001-COMPLETE.md](archive/LOGX-CHAR-001-COMPLETE.md); this
review document is the accepted record and is not rewritten by integration.**

```text
START SHA:                005795fdf540bd4c8997e2014a16c5c7eb0ba89f
END SHA:                  5caa671e6a2d84a9915918f0052b943870e7935f
                          (branch tip after the last content-bearing commit; the
                          commit that adds these three lines is documentation-only)
BRANCH:                   logx-char-001
COMMIT SHA(S):            caeb773285209d662c16d6fa79b08e83b57ca5e9
                          research(char): reconstruct Buu character definitions
                          5caa671e6a2d84a9915918f0052b943870e7935f
                          docs(tickets): record LOGX character research SHAs and gate
                          24f6ef5a468a3b5c4e8b517b1ab43d80fe3eef05
                          docs(tickets): record LOGX character branch SHAs
INTEGRATED EQUIVALENTS:   caeb773 -> 13586f5, 5caa671 -> b151441, 24f6ef5 -> c712de4
                          (cherry-picks into integrate/logx-char-001, whose base is
                          origin/master 6fa9928; every accepted blob is identical)
WORKTREE:                 <temp>\log1-remake-logx-char-001

CANONICAL ROM SHA BEFORE: 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
CANONICAL ROM SHA AFTER:  940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
```

Evidence document: [`../research/LOGX_CHAR_PROVENANCE.md`](../research/LOGX_CHAR_PROVENANCE.md).
Tooling: `tools/research/logx_char_probe.py`.

**Environment note, reported rather than hidden.** A read-only directory junction
`roms/` -> `<checkout>\roms` was created inside this worktree mid-ticket
so the pre-existing project suites that glob `roms/*Buu*.gba` would execute. It
was **removed** again: `tests/unit/test_project_safety.py::test_proprietary_and_generated_paths_are_git_ignored`
failed with `git check-ignore` returning 128 ("pathspec 'roms/safety-probe.gba'
is beyond a symbolic link"), i.e. the junction broke an established repository
safety regression. Removing it restored that test to passing, and the canonical
ROM was verified intact after removal (5 files, SHA-256 unchanged). The final
validation run below is therefore the pristine configuration, in which the text
suite skips for want of a local `roms/` exactly as it does on the baseline.

---

## EXTERNAL CLAIMS TESTED

`mainant/LOGExtractor` `CharacterSpriteExtractor`: a character table at `0x74D380`
with 232 records of 16 bytes; `+0x00` name text index; `+0x02` skipped /
"description"; `+0x04` `u32` sprite-definition index; `+0x08` `u32` portrait
index; `+0x0C` unresolved; plus an apparent sprite-definition pointer table at
`0x6B6BB4`, a portrait pointer table at `0x6F393C` and a text pointer table at
`0x06BCE8`.

**Address space.** LOGExtractor's addresses are **file offsets**: its `0x06BCE8`
is the project's independently verified `TEXT_TABLE_START`, and the engine's own
literal for the text table is `0x0806BCE8`. No ambiguity is carried into the
documentation; every address below is given in both forms.

| External claim | Verdict |
| --- | --- |
| character table begins at `0x74D380` | **CONFIRMED** |
| fixed count | **CONFIRMED** |
| count exactly 232 | **CONFIRMED** |
| stride exactly `0x10` | **CONFIRMED** |
| `+0x00` is a name text index | **PARTIALLY CONFIRMED** (physical field and text relationship confirmed; "name" not promoted) |
| `+0x02` is skipped / loosely a description | **REFUTED as "skipped"**; it is a second `u16` text index read by three engine functions |
| `+0x04` is a `u32` sprite-definition index | **PARTIALLY CONFIRMED**: `u32` index into a 4-byte-entry pointer array **CONFIRMED**; what the entries are is handed to LOGX-SPRITE-001 |
| `+0x08` is a `u32` portrait index | **PARTIALLY CONFIRMED**: `u32` index into the pointer array at `0x086F393C` **CONFIRMED**; "portrait graphics" not promoted |
| `+0x0C` unresolved | **IMPROVED**: one signed `i32` used as an index into `0x08711274` at stride `0x1C`; a negative value is one the engine skips; the target's meaning stays UNRESOLVED |
| sprite-definition pointer table `0x6B6BB4` | **PARTIALLY CONFIRMED**: that address is the accessor's compiler-folded arithmetic base; the project's accepted 297-entry run starts at `0x086B6BDC` |
| portrait pointer table `0x6F393C` | **CONFIRMED**, and it is the accessor's own literal |
| text pointer table `0x06BCE8` | **CONFIRMED**, already accepted (TOOLKIT-004) |

---

## TABLE START

**CONFIRMED**, GBA `0x0874D380` = file offset `0x74D380`.

The word `0x0874D380` occurs 5 times in the image and is loaded by **8**
`ldr Rt,[pc,#imm]` instructions (`0x08024FA0`, `0x08025086`, `0x080251B6`,
`0x08025380`, `0x08025E94`, `0x080273AC`, `0x08027962`, `0x080279A0`), found by a
raw halfword scan of **every even offset of the whole 8 MiB image** - not by a
disassembly sweep, so an undecodable neighbour cannot hide a site. Negative
coverage is scoped in the provenance document, section 5.1: no 16-bit `adr` and
no ARM `pc`-relative form reaches the address, and the only literals within the
`0x100` bytes below it are the two independently explained neighbouring tables.
The scope limit (a folded base *further* below is outside the reported range) is
stated there, along with the check of the candidate literals below it.

## TABLE COUNT

**CONFIRMED**, fixed, exactly **232**, index 231 last, index 232 outside.

Engine loop bounds `cmp rN,#0xE8` at `0x08027998`, `0x080279CC` and `0x08024F92`,
each incrementing its counter **before** the comparison, so `0xE8` is an
exclusive bound. Independent corroboration: the roster walk at `0x08024F3C`
drives a 232-bit runtime bitmap (`bit (i & 7)` of byte `(i >> 3)` at
`base + 0xC5`) over the same index range, and the first candidate record past the
count (`0x0874E200`) fails **three** of the four invariants that hold on all 232
records (`+0x00 = 7244` is outside the 1,534-entry text table, `+0x02 = 768` is
not `+0x00 + 1`, and `+0x04` is an IWRAM address).

The **only** function that returns `-1` is the search `0x08027948`
(`0x080279D0`/`0x080279D2`); `0x08024F3C` has no such epilogue - its only `mvns`
(`0x08024FFC`) builds a `-1` that it stores at `[object + 0x14]`, and its loop
falls through. Both facts are pinned by tests.

## TABLE STRIDE

**CONFIRMED**, `0x10`. **Eight** engine sites compute `index << 4` and add the
base - one per literal load: `0x08027964`, `0x080279A2`, `0x08024FA8` inside the
two walks, and `0x08025088`, `0x080251B8`, `0x08025382`, `0x08025E92`,
`0x080273AE` for single-record lookups. No other scale is ever applied to a
record index. Other `adds rX, #0x10` instructions and other `lsls #1`/`#2` scales
do exist in the same functions, so the claim is scoped to the record index and
those counterexamples are named in the provenance document.

## TABLE SEMANTIC IDENTITY

**PARTIALLY CONFIRMED.** The table holds **named appearance definitions with
optional slot and stat-record indices**, addressed by an appearance id and a
stat-record pointer: both `BL` callers of the search function `0x08027948` pass a
live object's `+0x58` as the id and the first also passes `[object + 0x224]`. It
is **not** promoted to "the character table": the label set includes machinery,
body parts and a `"Human"` catch-all, which refutes a playable-roster reading;
completeness is not established, and 98 records have no slot while 88 have no
stat record. Neutral name used throughout: *named appearance definitions*.

---

## ENGINE CONSUMERS

Six functions read the table; each was read in full.

| Function | Literal site(s) | Fields read | Use |
| --- | --- | --- | --- |
| `0x08024F3C` | `0x08024FA0` | `+0x00` `ldrh` `0x08024FAC` | 232-bit runtime bitmap walk, then adjacent-equal collapse of `+0x00` into a list |
| `0x08025056` | `0x08025086`, `0x080251B6` | `+0x08` `ldr` `0x080250CA`, `+0x00` `ldrh` `0x080251BC`, `+0x02` `ldrh` `0x080252E6` | `+0x08` -> accessor `0x08011F20` -> container dispatcher `0x0803D940`; `+0x00`/`+0x02` -> `0x0806BCE8` |
| `0x08025354` | `0x08025380` | `+0x02` `ldrh` `0x0802539E` | text pointer -> `0x0803DE6A`, looped over a line counter |
| `0x08025E50` | `0x08025E94` | `+0x02` `ldrh` `0x08025EC2` | text pointer -> `0x0803DE6A` |
| `0x08027390` | `0x080273AC` | `+0x04` `ldr` `0x080273B2` | -> accessor `0x08000158` -> `0x0800EB60`, in a 0x190-byte object constructor |
| `0x08027948` | `0x08027962`, `0x080279A0` | `+0x04` `ldr` `0x08027968`, `+0x0C` `ldr` `0x08027974`/`0x080279AA` | table **search**, returns a 0-based index or `-1` |

The input index is an **appearance id in the same id space as `+0x04`**, compared
after both sides pass through the accessor `0x08000158`; it is not a party id, a
dialogue-portrait id or an entity-template id. Argument 2, when non-null, is a
pointer into the `0x08711274` table's address space.

---

## `+0x00`

- **Physical field:** `u16` little-endian, read with `ldrh` at `0x08024FAC` and
  `0x080251BC`; never read as half a word or as part of a `u32`. **CONFIRMED.**
- Range over 232 records: `986..1310`; **154** distinct indices resolving to
  **152** distinct strings; no zero value.

### TEXT RELATIONSHIP

**CONFIRMED.** Four literal loads of `0x0806BCE8` are used with the two text
fields (`0x080251BE`/`0x080252E8` -> pool `0x08025328`, `0x080253A0` ->
`0x080256C0`, `0x08025EC0` -> `0x08026190`); the field is scaled by **four**
(`lsls r0,r0,#2` at `0x080251C0`, `0x080252EA`, `0x080253A2`, `0x08025EC6`) and
loaded with `ldr r1,[r1,r0]` (`0x080251C2`) or `ldr r0,[r1,r0]` (`0x080253A4`,
`0x08025EC8`) - the `u32` pointer-table access shape TOOLKIT-004 established. All
232 records resolve; there are no empty, invalid or sentinel text references.

### CHARACTER-NAME SEMANTIC

**PARTIALLY CONFIRMED.** The field is drawn once (`0x0803DADA` at `0x080251C8`)
and its text is a short label (`"Goku"`, `"Zombie"`, `"Airship Warlord"`), while
`+0x02` is drawn through a line-wrapping routine. That is content and consumer
correlation; no engine instruction names or derives the field, so
`docs/reverse-engineering.md` calls it a text index, not a name.

---

## `+0x02`

**Physical field:** `u16` little-endian, read with `ldrh r0,[r7,#2]` at
`0x080252E6`, `ldrh r0,[r5,#2]` at `0x0802539E` and `ldrh r0,[r0,#2]` at
`0x08025EC2`. **CONFIRMED** as a second text index into `0x0806BCE8`.

**Semantic:** **PARTIALLY CONFIRMED** as the entity's prose description. The
supporting evidence is the resolved text (one or two sentences), the wrapping
draw, and the distribution (232 records over 154 distinct indices and **104**
distinct strings). It is **not** called a description field as an engine fact.

LOGExtractor's "skipped" reading is **REFUTED as a statement about the engine**:
three engine functions read the field.

`+0x02 == +0x00 + 1` holds on **232 of 232** records, a strict bijection. This is
recorded as a **data invariant of the canonical image**, not an engine
constraint: no instruction compares or derives the two fields.

---

## `+0x04`

**Physical field:** `u32` little-endian, read with `ldr r0,[r0,#4]` at
`0x080273B2` and `ldr r0,[r6,#4]` at `0x08027968`. Range `12..306`; **198**
distinct; **no record has zero**.

### SPRITE-TABLE RELATIONSHIP

**CONFIRMED.** The accessor `0x08000158` returns, for `id >= 10`,
`u32 at 0x086B6BDC + 4*id - 0x28` - raw halfwords `0x0800015E = 4998`
(literal `0x086B6BDC`, pool `0x080003C0`), `0x08000164 = 3840` (`subs r0,#0x40`),
`0x08000166 = 6980` (`ldr r0,[r0,#0x18]`). The arithmetic base is
`0x086B6BB4`. `0x0801713C` is a second entry to the same array with the identical
literal and displacement. Ids `0..9` never read the array. All 232 records select
a valid ROM pointer; 198 unique ids over 232 references, and no two distinct ids
share a target.

### SPRITE-DEFINITION SEMANTIC

**PARTIALLY CONFIRMED.** The words the field selects are the project's accepted
character-graphics structures (`GRAPHICS_FORMAT.md`). Their layout is **not**
reconstructed here; that boundary is stated in the handoff.

---

## `+0x08`

**Physical field:** `u32` little-endian, read with `ldr r0,[r7,#8]` at
`0x080250CA`. Its 111 distinct values are `0` plus a **110-element subset of
`8..162`**: exactly one distinct value is zero (98 *records* carry it), none is in
`1..7`, and 45 of the array's 155 valid slots are unused by the table.

### PORTRAIT-TABLE RELATIONSHIP

**CONFIRMED.** `0x08011F20` returns `0` for slots 0 and 7 without reading the
array, takes a party-record path for slots `1..6`, and otherwise returns
`u32 at 0x086F393C + 4*slot` (`0x08011F52 ldr r1,[pc,#0x240]`, pool `0x08012194`).
The array holds 163 slots: `0..7` zero, `8..162` **155** valid strictly ascending
ROM pointers (`0x086B880C .. 0x086F3360`), slot 163 the non-ROM word `0x0011E502`.
The field's value set is a strict **inclusion** in the valid slots, not the whole
of them - a base or width error would push values outside the run, so the
inclusion still discriminates, but it is not an equality.

### PORTRAIT SEMANTIC

**PARTIALLY CONFIRMED.** The consumer passes the accessor's result to the Webfoot
container dispatcher `0x0803D940` at `0x080250D6`, so it is consumed as a
resource. No pixel format, dimension or rendering claim is made; graphics work is
handed downstream.

---

## `+0x0C`

**Physical structure:** one `i32` little-endian, read with `ldr r0,[r6,#0xc]` at
`0x08027974` and `ldr r1,[r0,#0xc]` at `0x080279AA` and sign-tested with `blt`
(`0x080279AE`). No `ldrh`/`ldrb`/`ldrsh` reads any part of it, and no consumer
treats it as subfields. **CONFIRMED.**

**Semantic: PARTIALLY CONFIRMED.** `0x08027948` computes
`0x08711274 + 28 * +0x0C` (`0x080279B0 lsls r3,r1,#3`, `0x080279B2 subs r1,r3,r1`,
`0x080279B4 lsls r1,r1,#2`, `0x080279B6 adds r1,r1,r6`) and compares it to its
second argument. `0x08711274` is the base of the stat table already accepted by
TOOLKIT-009 (stride `0x1C`, 141 records). 88 records are negative (`-1..-9`),
which the engine **skips** without forming an address; 144 are `0..149` over 123
distinct values. The values at or above the validated extent are
`142, 143, 145, 146, 147, 148, 149` (records 220, 221, 222, 224, 225, 227, 228,
231); `141` and `144` are unused. Those eight records are recorded as an anomaly,
not promoted.

The absence claim for this field is scoped in the provenance document,
section 12.3: the search covers every address-producing site of the table
(section 5's scans) and a full instruction reading of all six consuming
functions, including an explicit check that no `ldm`/`stm` reads a record base; it
explicitly does **not** cover a record pointer stored in one function and read in
another through an unfollowed offset, and says so.

---

## SPRITE TABLE

Address space GBA `0x086B6BB4` (arithmetic base; LOGExtractor's `0x6B6BB4`) and
`0x086B6BDC` (literal / entry run; the project's accepted TOOLKIT-010 base).
Entry width **4 bytes**, entry model **direct GBA pointer**.

- `0x086B6BDC`: **297** entries, all valid ROM pointers, strictly ascending,
  terminated by the non-ROM word `0x03001068` at `0x086B7080`.
- `0x086B6BB4`: `0x086A6424`, `0x086A7238`, `0`, `0`, `0x086A7E7C`, `0`, `0`,
  `0`, `0`, `0x086A899C` - **four** ascending valid pointers and **six** nulls.
- `+0x04` reaches it: **CONFIRMED**. Whether the array is indexed from
  `0x086B6BB4` or from `0x086B6BDC` with an offset of 10 is **UNRESOLVED** and is
  the recorded disagreement with LOGExtractor. The last id the canonical table
  uses (306) lands on the last valid entry under both readings.
- Representative entries: entry 0 at `0x086B6BDC` -> `0x086A89D0`; `+0x04 = 12` ->
  `0x086A8A88`; entry 296 at `0x086B707C` -> `0x086B6B60`.

## PORTRAIT TABLE

Address space GBA `0x086F393C` (file `0x6F393C`; LOGExtractor's address is
exactly the engine's literal). Entry width **4 bytes**, entries are **direct GBA
pointers**. 163 slots; `0..7` zero; `8..162` the 155 valid ascending entries;
slot 163 not a ROM address. `+0x08` resolves through it: **CONFIRMED**.
Representative resources: slot 8 -> `0x086B880C`, slot 9 -> `0x086B8D90`,
slot 10 -> `0x086B93F8`, slot 162 -> `0x086F3360`.

---

## FULL-CENSUS RESULTS

Population: **232 records** (`0x74D380..0x74E1F0`).

| Field | Distinct indices/values | Distinct strings | Zero-valued records | Min | Max | References | Unique targets |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `+0x00` | 154 | **152** | 0 | 986 | 1310 | 232 | 154 pool addresses |
| `+0x02` | 154 | **104** | 0 | 987 | 1311 | 232 | 154 pool addresses |
| `+0x04` | 198 | - | 0 | 12 | 306 | 232 | 198 |
| `+0x08` | 111 | - | 98 | 0 | 162 | 134 | 110 |
| `+0x0C` (signed) | 132 | - | 1 | -9 | 149 | 144 | 123 |

- **DISTINCT TEXT REFERENCES:** 154 distinct `+0x00` indices resolving to **152**
  distinct strings (slots 1038, 1040, 1042 all hold `"Super Buu"`), and 154
  distinct `+0x02` indices resolving to **104** distinct strings. 154 distinct
  `(+0x00, +0x02)` pairs across 232 records, so 78 records repeat an existing pair
  with different resource fields.
- **DISTINCT SPRITE REFERENCES:** 198 distinct `+0x04` ids over 232 references;
  **198** distinct resolved targets (no aliased pointer).
- **DISTINCT PORTRAIT REFERENCES:** 110 distinct non-zero `+0x08` slots over 134
  references; **110** distinct resolved targets.
- **DUPLICATE COMPLETE RECORDS:** exactly **1** pair - records **80** and **81**
  (`"Gunman"`, text 996/997, `+0x04` 137, `+0x08` 0, `+0x0C` 44). No other pair
  matches on all five fields.
- **Invalid references:** 0 text, 0 sprite, 0 portrait.
- **Outliers / suspicious sentinels:** `+0x08 == 0` (98 records, "no slot");
  `+0x0C` negative (88 records, "no stat record", `-1` dominant); `+0x0C` in
  `{142,143,145,146,147,148,149}` (8 records, past the validated stat extent). No
  value in `+0x08` 1..7 and no `+0x04 == 0`.
- **Repeated aliases:** none at the pointer level; sharing is at the value level
  only, which the engine's pointer comparison confirms. Text aliases at the
  **content** level, recorded separately above.
- **Variant families** are partial matches, not exact duplicates, and the shared
  field is not always `+0x0C`: the `"Gohan"` family (records 49-57) shares text
  1186/1187 and `+0x0C = -3` on 49-56, but record 57 carries `+0x0C = 35` with
  `+0x04 = 110` and `+0x08 = 45`; the `"Goku"` family uses `+0x04`
  {115,117,118,119,120,121} and `+0x08` {57,60,61}.

## REPRESENTATIVE RECORDS

| Index | Address | Raw 16 bytes | `+0x00`/`+0x02` text | `+0x04` | `+0x08` | `+0x0C` |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 0 | `0x0874D380` | `100511051f0000000000000000000000` | "Airship Warlord" / "Watch out for this Cyborg's killer claw!" | 31 | 0 | 0 |
| 58 | `0x0874D720` | `a404a5047300000039000000feffffff` | "Goku" / "Goku is a Saiyan from the planet Vegeta…" | 115 | 57 | -2 |
| 80 | `0x0874D880` | `e403e50389000000000000002c000000` | "Gunman" / "A known criminal…" | 137 | 0 | 44 |
| 231 | `0x0874E1F0` | `a004a104320100000000000095000000` | "Zombie" / "When there is no more room in H.F.I.L.…" | 306 | 0 | 149 |

Rows 0 and 231 are asserted byte-exact by the ROM-gated test; rows 58 and 80 are
taken from the probe's `--rows` output.

## TABLE-BOUNDARY RESULT

**CONFIRMED as corroboration, not as the count proof.** Immediately before the
table: a 4-byte table `00 03 01 02` at `0x0874D35C` (indexed `& 3`, loaded at
`0x0802734C`) and an 8-entry `u32` pointer table at `0x0874D360`
(`0x0805752C, 0x0805762C, 0x0805772C, 0x0805782C, 0x0805782C, 0x0805762C,
0x0805762C, 0x0805752C`, indexed `& 7`, loaded at `0x08027494`). The 8-entry
table ends **exactly** at `0x0874D380`. Immediately after the 232nd record,
`0x0874E200` holds `0x03001C4C` (an IWRAM address), and the candidate 233rd
record fails three of the four table invariants.

## ANOMALIES

1. Records 220, 221, 222, 224, 225, 227, 228, 231 have `+0x0C` in
   `{142,143,145,146,147,148,149}`, past the 141-record extent TOOLKIT-009
   validated for `0x08711274`.
2. Records 80 and 81 are byte-identical in all five fields.
3. 78 records repeat an existing `(+0x00, +0x02)` pair; the variant families are
   not ordered or grouped by any engine code found, and one family member
   (`"Gohan"` record 57) differs in the very field the rest share.
4. The `f(0x95)` / `f(0x92)` substitution inside `0x08027948` names two
   appearance ids whose meaning is UNKNOWN.
5. The `+0x04` pointer array's "first entry" is ambiguous between the accessor's
   folded base `0x086B6BB4` and the accepted 297-entry run at `0x086B6BDC`.
6. Three `+0x00` slots share one string, so distinct-index and distinct-string
   counts differ (154 vs 152); the `+0x02` field differs far more (154 vs 104).

---

## TOOLING ADDED

`tools/research/logx_char_probe.py` - SHA-256 gated, read-only, deterministic.
Its field API is purely positional; the two pointer arrays are named after the
field that selects them (`FIELD_04_*`, `FIELD_08_*`, `field_04_target`,
`field_08_target`) precisely because their target semantics are only partially
confirmed, and a portable test asserts that no probe or test identifier uses the
un-promoted names. `CensusLimits` separates codec/engine bounds from measured
pointer-run extents and says which is which.

Reports: record parsing at physical widths; full-table census with anomaly flags,
distinct-index **and** distinct-string counts, and reference/unique-target
arithmetic for all five fields; text resolution through the accepted codec; both
pointer arrays' shape reports including the pre-run slot census; the boundary
report with the named invariants that record 232 breaks; and an engine-evidence
report (`--engine`) that re-reads each of the 37 quoted instructions and every
`ldr`-literal site for the table address.

## TESTS ADDED

- `tests/integration/test_logx_char_rom.py` - 24 ROM-gated tests: the eight
  literal sites, the neighbourhood negative, all 37 quoted instructions, the
  eight stride sites, the count instructions, the search function's `-1`
  epilogue, the accessor arithmetic, representative raw records, the
  three-invariant failure of record 232, full census arithmetic, distinct-string
  counts, the duplicate pair, all three field-to-array relationships, text
  resolution, the `×4` text scale and the `ldr`/`ldrh` register forms, both
  pointer arrays' shapes, the boundaries, determinism and the canonical gate.
- `tests/unit/test_logx_char_reference.py` - 22 portable tests on synthetic rows
  and constants only: the anomaly branches, the two kinds of census bound kept
  apart, the identifier-naming invariant, the fail-closed gate, and the
  conservative refusals. No ROM bytes, no payload hash and no decoded string.

## TEST RESULTS

Measured, not derived.

| Command | Result |
| --- | --- |
| `pytest tests/unit/test_logx_char_reference.py tests/integration/test_logx_char_rom.py -q` | **46 passed** |
| the same, with the ROM path pointed at a non-existent file | **22 passed, 24 skipped**, every skip reported as "canonical Buu ROM not configured locally" |
| `pytest tests/unit tests/integration/test_logx_char_rom.py tests/integration/test_logx_{codec,connector,layer,map_record,map_render,tile}_rom.py tests/integration/test_text_rom.py -q` (isolated basetemp outside the repository, junction removed) | see below |

```text
$ cd <temp>\log1-remake-logx-char-001
$ $env:LOGX_CANONICAL_ROM = "<checkout>\roms\Dragon Ball Z - Buu's Fury (U).gba"
$ python -m pytest tests/unit tests/integration/test_logx_char_rom.py `
    tests/integration/test_logx_codec_rom.py tests/integration/test_logx_connector_rom.py `
    tests/integration/test_logx_layer_rom.py tests/integration/test_logx_map_record_rom.py `
    tests/integration/test_logx_map_render_rom.py tests/integration/test_logx_tile_rom.py `
    tests/integration/test_text_rom.py -q --basetemp=<temp>\dsh-pytemp-final

1551 passed, 52 skipped in 249.97s (0:04:09)
```

The 52 skips are the suites' own guards being reported honestly:
`test_text_rom.py` skips 37 because this worktree has no local `roms/` directory
(its own unchanged baseline behaviour), and the remainder are the pre-existing
PySide6, site-build and local-dump guards. No ticket-caused failure was observed,
and no test was weakened to reach zero.

Two environmental failures were observed and resolved; neither is attributable to
this ticket, and both are reported rather than hidden.

1. `tests/unit/test_project_safety.py::test_proprietary_and_generated_paths_are_git_ignored`
   failed while the temporary `roms/` junction existed (git refuses `check-ignore`
   beyond a symbolic link, exit 128). The junction was removed and the test
   passes; this was a real regression caused by a local convenience, so the
   convenience was withdrawn rather than the test weakened.
2. `tests/unit/test_mgba_capture.py::test_capture_output_is_restricted_to_ignored_build_tree`
   failed when pytest's basetemp was placed inside the repository's own `build/`
   tree, because the test asserts that a path under `build/` is *accepted* and any
   other path is refused. With an out-of-repository basetemp the module is
   **73 passed**.

A third, unrelated environment error was also seen once:
`PermissionError` on `<temp>\pytest-of-<user>`, caused by a concurrent process
holding that directory; re-running with an isolated basetemp cleared it.

---

## ROM_BIBLE_IMPACT

`docs/reverse-engineering.md` gains one section, **LOGX-CHAR-001
character-definition records**: the table start with the eight literal sites and
the negative-coverage scope; the eight stride sites and the three count sites
with their instructions; the five physical field reads; the `+0x00`/`+0x02`
text-index relationship including the `×4` scale and the distinct-string counts;
the `+0x04` accessor arithmetic with the folded `-0x28`, the four-plus-six
pre-run slots and the unresolved first-entry question; the `+0x08` accessor and
the array's extent; the `+0x0C` index arithmetic and the anomaly set; the runtime
arrival route; and the semantic-scope conclusion with its counterexamples. No
`+0x02` or `+0x0C` guess is promoted, "name"/"description" are not promoted, and
the fields are described by what the engine does with them.

## public progress impact

**NONE.** This is isolated research with no shipped SDK capability, no public
frontier and no product-story change; `src/data/project.ts` is untouched, no
site edit is made, `docs/PROJECT_<local-state-name>` is not modified, and
`docs/PROJECT_<local-state-name>` is not updated, because the ticket has not been
independently accepted or integrated.

---

## DISAGREEMENTS WITH LOGEXTRACTOR

1. **`+0x02` is not skipped.** Three engine functions read it; it is a second
   `u16` index into the same text table.
2. **The sprite-definition pointer table's base.** LOGExtractor publishes
   `0x6B6BB4`. That is exactly the accessor's compiler-folded arithmetic base
   (`literal 0x086B6BDC`, displacement `-4*10`). The project's independently
   accepted entry run begins at `0x086B6BDC` with 297 valid entries. The
   disagreement is about which byte is the array's first entry; it is recorded as
   UNRESOLVED rather than silently resolved in either direction.
3. **`+0x0C` is not unresolved.** It is one signed `i32` index into `0x08711274`
   at stride `0x1C`, and a negative value is one the engine skips. Its *target's*
   meaning remains open.
4. **"Character table" is too strong.** The table spans machinery, body parts,
   generic enemies and a `"Human"` catch-all, and its attributes are optional;
   the neutral name is used.
5. **Address notation.** LOGExtractor's addresses are file offsets; the
   documentation states both forms for every address.

## UNRESOLVED QUESTIONS

1. Which byte is the `+0x04` pointer array's first entry (`0x086B6BB4` versus
   `0x086B6BDC`), and therefore how the id space is anchored.
2. What the 28-byte records at `0x08711274` mean for a character, and whether
   values `142..149` are valid records.
3. What `f(0x95)` and `f(0x92)` denote.
4. Which of the 232 records are ever activated by the runtime bitmap; whether
   any are unused, and what a variant family means (forms, costumes, or several
   placements of one enemy).
5. Whether `+0x0C` has a consumer outside the six functions this ticket read
   (scoped negative, provenance document section 12.3).
6. Whether any producer of object `+0x58` uses an id the table does not contain;
   `0x08027948` returns `-1` and both callers handle it, but no caller census was
   taken.

---

## HANDOFF TO LOGX-SPRITE-001

- Accessor `0x08000158`: `u32 at 0x086B6BDC + 4*id - 0x28` for `id >= 10`;
  literal pool `0x080003C0`; raw halfwords `4998`, `3840`, `6980` at
  `0x0800015E`, `0x08000164`, `0x08000166`. Party-record entry `0x0801713C` reads
  the id from `ldrh [record + 0x0E]`.
- Accepted array base `0x086B6BDC`, **297** entries, strictly ascending,
  terminated by `0x03001068` at `0x086B7080`. Ids observed here: `12..306`.
- The ten words at `0x086B6BB4..0x086B6BD8`: four valid ascending pointers, six
  nulls, listed in the provenance document, section 16.
- `0x08027948` also uses the appearance-id constants `0x92` and `0x95`.
- Each record's `+0x04` is a **`u32` id, never a pointer**, in all 232 records.
- Do **not** assume animation count, `+0x54`, or animation-slot semantics from
  this ticket: nothing here constrains them.

## HANDOFF TO LOGX-FRAME-001

Nothing in this ticket constrains frame or multipart graphics. The `+0x08` array's
targets were located (`0x086B880C`, `0x086B8D90`, `0x086B93F8`, …) but not
decoded, and their first words were not interpreted. LOGExtractor's "portrait"
reading is **PARTIALLY CONFIRMED** only; confirming it is pixel work.

## OTHER DOWNSTREAM HANDOFFS

- **Placement/type work (TOOLKIT-009 family):** `+0x0C` now links a
  character-appearance record to `0x08711274 + 28*index`, the same table the
  placement path selects through `0x0800FD55`/`0x0800F68C`. Both ends of a
  "placement -> character" relation now exist.
- **Text work (TOOLKIT-004 family):** `+0x00` and `+0x02` are two adjacent text
  slots used by 232 records over 154 distinct pairs; a text-table change must
  consider both, and three `+0x00` slots share one string.
- **`0x08711274`:** values `142..149` are used by this table as well as by
  placements, which corroborates TOOLKIT-009's "reference-only" note without
  creating a record claim.

---

## REVIEWER A

Engine/dataflow/table-structure focused. Fresh context, nothing read from the
documents was trusted; all numbers re-derived from ROM bytes and disassembly.

```text
CODE REVIEW

Verdict: APPROVE WITH NON-BLOCKING NOTES (after corrections; see CORRECTION GATE)

Scope reviewed:
- docs/research/LOGX_CHAR_PROVENANCE.md, tools/research/logx_char_probe.py,
  tests/integration/test_logx_char_rom.py, tests/unit/test_logx_char_reference.py,
  and the LOGX-CHAR-001 section appended to docs/reverse-engineering.md.

Blocking findings (raised, reproduced, corrected - all closed):
- [high] provenance 10.3 / 16 / reverse-engineering.md - "the ten words at
  0x086B6BB4 are 3 valid ascending pointers and 6 nulls".
  Evidence: struct.unpack("<10I", rom, 0x6B6BB4) = 086a6424, 086a7238, 0, 0,
  086a7e7c, 0, 0, 0, 0, 086a899c -> 4 + 6 = 10.  Impact: an arithmetically
  impossible count in the handoff.  Required fix: 4 valid + 6 nulls.  CLOSED.
- [high] provenance 6 - "Three engine sites compute index<<4 + base".
  Evidence: the instruction follows *every* literal load; the five missing sites
  are 0x08025088, 0x080251B8, 0x08025382, 0x08025E92, 0x080273AE, and 5's
  conclusion ("one engine index computation") contradicted 6.  Required fix:
  eight sites with the walk/lookup split.  CLOSED.
- [high] provenance 7 - "Both functions return -1 (0x080279D0/0x080279D2)".
  Evidence: 0x08024F3C has no mvns/rsbs -1 at all; its only return is
  pop {r3-r7,pc} at 0x08024F50, and 0x08024FFC mvns r1,r1 builds a -1 it *stores*
  at [object+0x14].  Impact: a false statement about an engine epilogue.
  Required fix: only 0x08027948 returns -1; exclusivity rests on the
  pre-increment.  CLOSED.
- [medium] provenance 13.3 - the "Gohan" family is stated to share +0x0C = -3.
  Evidence: records 49-56 are -3; record 57 is 35 (with +0x04 = 110, +0x08 = 45).
  CLOSED.
- [medium] provenance 13.3 - "the Goku family +0x04 115..121, +0x08 57..61".
  Evidence: measured sets are {115,117,118,119,120,121} and {57,60,61}; the
  ranges imply unused values.  CLOSED.
- [medium] provenance 9.2 / 14 and reverse-engineering.md - "154 distinct
  strings".  Evidence: indices 1038, 1040 and 1042 all decode to "Super Buu";
  154 indices -> 152 strings.  CLOSED.
- [medium] provenance 11.1 and reverse-engineering.md - "{0} u {8..162}", which
  has 156 elements while the measured set has 111.  Required fix: {0} plus a
  110-element subset.  CLOSED.
- [medium] provenance 16 - "The four +0x00 values above 1,310".
  Evidence: no +0x00 value exceeds 1310.  CLOSED.
- [medium] provenance 16 - the entry-296 parenthetical.  Evidence: 0x086A89D0 is
  entry 0; entry 296 is slot 0x086B707C with value 0x086B6B60; 0x086B7080 is the
  terminator slot.  CLOSED.
- [low] provenance 2 - max_selector 149 attributed to stat_tables.py, which has
  no such symbol.  Evidence: it is config/roms.yaml placement_types:35.  CLOSED.
- [low] provenance 8 - the 0x08025056 row omits its +0x02 read at 0x080252E6.
  CLOSED.

Non-blocking findings:
- 5.1 did not state that a folded base further than 0x100 below the table is out
  of scope.  The candidate literals below it (0x0874CA24, 0x0874CA38, 0x0874D02C,
  0x0874D03C, 0x0874D248) were checked and none is used with a 16-byte stride.
  Now stated in 5.1.
- Probe/test naming encodes the partially confirmed sprite/portrait readings in
  identifiers and anomaly codes; CensusLimits' "every bound has an engine or
  codec source" is overstated for 297/162.  Now renamed and qualified.

Correctness:
- PASS after corrections.  Every load-bearing fact reproduced: table start,
  stride, count, the eight literal sites, the eight stride sites, all quoted
  field reads, the three accessor arithmetic paths, the two BL callers, the
  boundary structures and record 232.

Architecture/product alignment:
- PASS.  Research-only; no production code, GUI or authoring surface touched.

ROM/data safety:
- PASS.  SHA-256 940AD5F0...F059E, 8,388,608 bytes, identical before and after.
  No file written in the worktree by the reviewer.

Determinism:
- PASS.  Probe CLI exits 0 and is deterministic; the suite asserts report
  equality across repeated calls.

Tests/evidence:
- PASS.  41 passed at review time, 46 after the corrections; without a ROM,
  22 passed / 24 skipped, all "canonical Buu ROM not configured locally".

Compatibility:
- PASS.  The six existing LOGX integration suites and the text suite unchanged.

Maintainability:
- PASS.  EVIDENCE_INSTRUCTIONS makes every quoted site a data row asserted by a
  test, so prose cannot drift from the record again without failing.

Public-release hygiene:
- PASS.  No ROM, save, state or extracted asset staged; roms/ is ignored.

Reviewer validation performed:
- Whole-image halfword scans for ldr-literal, Thumb BL, and 16-bit adr; ARM
  pc-relative scans; 36 Thumb adr hits and 21+6 ARM sites checked; an independent
  Thumb size walk to confirm each reported site sits on a real instruction
  boundary; an independent text decode agreeing with text_tables on all 154 used
  indices.

Remaining uncertainty:
- The array's first entry (10.3), the stat target's meaning, and which records
  the runtime bitmap can set.
```

## REVIEWER B

Census/adversarial semantic-assumption focused. Fresh context; the probe's own
`census()`/summary functions were never the instrument - every figure below came
from the reviewer's own `struct.unpack`, literal scan, BL decoder and instruction
walk.

```text
CODE REVIEW

Verdict: APPROVE WITH NON-BLOCKING NOTES (after corrections; see CORRECTION GATE)

Scope reviewed:
- the same five artifacts.

Blocking findings (raised, reproduced, corrected - all closed):
- [high] provenance 14 - "global appearance/definition table spanning everything
  the game gives a name, a bio line, an appearance and a face".
  Evidence: "everything"/"global" is a completeness claim a 232-record census
  cannot support, and the attributes are not universal - 98/232 have +0x08 == 0,
  88/232 have +0x0C < 0, and 93 have no slot yet a stat index.  Required fix: the
  optional-field formulation with completeness UNKNOWN.  CLOSED.
- [high] provenance 14 first sentence - 154 distinct strings; measured 152 (and
  the category list was the reviewer's classification presented as observation).
  CLOSED (observation and classification are now separated).
- [medium] provenance 13.3 - "two records that name the same appearance are not
  distinguishable by that search".  Evidence: when argument 2 is non-null the
  code at 0x08027972..0x08027988 also requires +0x0C >= 0 and
  0x08711274 + 28*(+0x0C) == argument, so records differing in +0x0C *are*
  distinguished.  CLOSED.
- [medium] provenance 12.2 - "values at or above the accepted extent | 141..149".
  Evidence: the used values are {142,143,145,146,147,148,149}; 141 and 144 are
  unused.  CLOSED.
- [medium] provenance 7 / 15 - "fails two invariants".  Evidence: record 232 also
  breaks +0x02 == +0x00 + 1 (768 != 7245), so three of four fail.  CLOSED.
- [medium] provenance 6 - "No adds rX,#0x10 walk, no other multiplier and no
  variable stride appears in any consuming function".  Evidence: adds #0x10
  exists at 0x08024F64, 0x0802506C, 0x08025378, 0x0802607A, and lsls #1/#2
  throughout; none walks a record base.  Required fix: scope the sentence to the
  record index and name the counterexamples.  CLOSED.
- [medium] provenance 9.2 and reverse-engineering.md - "doubled" and a single
  ldr form for the text load.  Evidence: the scale is x4 (lsls r0,r0,#2 at
  0x080251C0, 0x080252EA, 0x080253A2, 0x08025EC6); 0x080251C2 is
  ldr r1,[r1,r0] while 0x080253A4/0x08025EC8 are ldr r0,[r1,r0]; four, not three,
  text-table literal sites are used.  CLOSED.
- [low] provenance 11.1 / reverse-engineering.md - "111 distinct values, 98 of
  which are zero".  Evidence: 111 distinct values of which exactly one is zero
  and 110 are non-zero; 98 of the 232 records carry 0.  CLOSED.
- [low] provenance 11.2 - "a set equality".  Evidence: 110 of the 155 valid slots
  are used, so it is a strict inclusion.  CLOSED.
- [low] provenance 8/9.1 - register transpositions at 0x08027974 (ldr r0,[r6,#0xc])
  and 0x080252E6 (ldrh r0,[r7,#2]).  CLOSED.
- [low] provenance 11.2/12.2 - "reserved" slots and "negative value meaning no
  record" stated as observation of engine intent.  Required fix: state the
  observable (all zero; the engine skips with blt and forms no address).  CLOSED.
- [low] provenance 3 vs 10.3 - mutually inconsistent framing of the 0x6B6BB4
  correction.  CLOSED.
- [low] probe/tests - sprite/portrait identifiers and anomaly codes carry the
  partially confirmed semantics; test_sprite_pointer_table_shape's comment said
  "seven are null" while its assertion said 6.  CLOSED.
- [low] the probe computed no text-target arithmetic, so 13.2's text row was
  untested.  Required fix: measure it.  CLOSED (references["text_index"],
  ["text_index_2"] and distinct_text_strings added).

Non-blocking findings:
- "no aliased pointer" must stay scoped to pointers: text content does alias
  (3 slots -> "Super Buu", 154 +0x02 indices -> 104 strings).  Now stated.
- The 134/110 portrait arithmetic does add up; the reviewer's own prompt
  hypothesis of "13 non-zero distinct" was correctly refuted (110).

Correctness:
- PASS after corrections.  Census arithmetic reproduced exactly: 232 records /
  0x10 stride; +0x00 154/0/986/1310; +0x02 154/0/987/1311; adjacency 232/232;
  all text indices in range; +0x04 198/0/12/306; +0x08 111 distinct with 98 zero
  records and no 1..7; +0x0C 132/1/-9/149 with 88 negative over -1..-9 and 144
  non-negative over 123 distinct; one byte-identical pair (80,81) and no other;
  references/targets 232/198/198, 134/110/110, 144/123/123 with no aliased
  target; 154 distinct (text,text2) pairs; the anomaly record set; the boundary
  numbers; and the 297/155-entry array extents.

Architecture/product alignment:
- PASS.  Research-only.

ROM/data safety:
- PASS.  SHA-256 verified identical before and after; worktree status unchanged;
  the reviewer's scratch code lives outside the worktree.

Determinism:
- PASS.

Tests/evidence:
- PASS.  41 passed at review time (20 unit + 21 ROM-gated), 46 after the
  corrections; skip guard clean.

Compatibility:
- PASS.

Maintainability:
- PASS.  154/154 census agreement with the probe on every figure it asserts; the
  defects were in the prose and naming, not the arithmetic.

Public-release hygiene:
- PASS.

Reviewer validation performed:
- Independent struct.unpack census, independent Thumb halfword/ldr-literal scan,
  independent BL-target decoder, independent Thumb size walk, own text decode via
  the accepted codec only.

Remaining uncertainty:
- Same as Reviewer A, plus the honest classification of the table's scope, which
  the reviewer recommended as "a table of named appearance definitions with
  optional portrait/stat links; globality UNKNOWN" - adopted.
```

## REQUIRED CORRECTIONS

All findings from both reviewers were reproduced in this session with the
commands and bytes quoted above; none was rejected on substance. 25 corrections
were raised and **all 25 are closed**. Corrections affecting only prose or
naming changed no measured figure; the census arithmetic was confirmed correct by
both reviewers.

| # | Correction | Source | Status |
| ---: | --- | --- | --- |
| C1 | `0x086B6BB4` pre-run slots: 3 valid + 6 nulls -> **4 + 6** | A1, B3 | CLOSED |
| C2 | "three stride sites" and "one engine index computation" -> **eight** sites, walk/lookup split | A2 | CLOSED |
| C3 | "both functions return -1" -> only `0x08027948`; `0x08024F3C` stores a `-1` sentinel | A3, B4 | CLOSED |
| C4 | `"Gohan"` family: record 57 is `+0x0C = 35`, only 49-56 share `-3` | A4, B5 | CLOSED |
| C5 | `"Goku"` family ranges -> measured value sets | A5 | CLOSED |
| C6 | "154 distinct strings" -> 154 indices / **152** strings; `+0x02` 154 / **104** | A6, B1 | CLOSED |
| C7 | `{0} ∪ {8..162}` -> `{0}` + a 110-element subset; 45 slots unused | A7, B9 | CLOSED |
| C8 | delete "four `+0x00` values above 1,310" (max is 1310) | A8, B6 | CLOSED |
| C9 | entry-296 parenthetical -> slot `0x086B707C` = `0x086B6B60`; `0x086A89D0` is entry 0; `0x086B7080` is the terminator slot | A9, B7 | CLOSED |
| C10 | `max_selector` 149 -> `config/roms.yaml` `placement_types`, not `stat_tables.py` | A10, B15 | CLOSED |
| C11 | add `0x08025056`'s `+0x02` read at `0x080252E6` | A11, B13 | CLOSED |
| C12 | anomaly values are `{142,143,145,146,147,148,149}`; `141` and `144` unused | B2 | CLOSED |
| C13 | "doubled" -> `×4`; `ldr r1,[r1,r0]` at `0x080251C2` only; four text literals | B8 | CLOSED |
| C14 | "two invariants" -> **three** | B10 | CLOSED |
| C15 | scope the "no `adds rX,#0x10`" sentence to the record index; name the counterexamples | B11 | CLOSED |
| C16 | "set equality" -> strict inclusion | B14 | CLOSED |
| C17 | "negative = no record" -> "the engine skips it with `blt`" | B (semantics) | CLOSED |
| C18 | "reserved" slots -> observable "all zero; accessor returns 0 for 0 and 7" | B (semantics) | CLOSED |
| C19 | replace the "global … spanning everything" sentence with the optional-field formulation | B (semantics) | CLOSED |
| C20 | qualify "not distinguishable by that search" with the `+0x0C`/argument-2 condition | B (semantics) | CLOSED |
| C21 | make §3's framing of the `0x6B6BB4` reading consistent with §10.3's UNRESOLVED | B16 | CLOSED |
| C22 | state the folded-base coverage limit in §5.1 and record the check of the literals below | A (coverage) | CLOSED |
| C23 | rename probe/test identifiers and anomaly codes to the neutral field-based vocabulary; qualify the docstring and `CensusLimits` claims | A (d), B R17 | CLOSED |
| C24 | fix the test comment that said "seven are null" while asserting six | B (d) | CLOSED |
| C25 | measure the text-target arithmetic the census quoted | B (d) | CLOSED |

## REJECTED REVIEWER ASSERTIONS

1. **Reviewer A: "§16's list of the ten words prints eleven values (an extra `0`
   between `0x086A7238` and `0x086A7E7C`)."** Rejected. The list contains
   exactly ten values - `0x086A6424`, `0x086A7238`, `0`, `0`, `0x086A7E7C`, `0`,
   `0`, `0`, `0`, `0x086A899C` - which is the measured content of
   `0x086B6BB4..0x086B6BD8`; slots 2 and 3 are both zero. Evidence:
   `struct.unpack_from("<10I", rom, 0x6B6BB4)`. The genuine error in that region
   was the "3 valid + 6 nulls" count, which is accepted as C1.
2. **Reviewer B: the `×4` scale site for the `+0x02` read is `0x080252E8`.**
   Partially rejected as a location detail: `0x080252E8` is
   `ldr r1, [pc, #0x3c]`; the `lsls r0, r0, #2` is at `0x080252EA`. The substance
   - the scale is four and not two - is accepted as C13.

## CORRECTION GATE

**CLOSED.** 27 findings were raised by the two reviewers (11 by A, 16 by B). 25
distinct corrections were accepted and applied; 1 assertion was rejected with
evidence and 1 was accepted in substance with its location corrected, both
recorded above. After the corrections:

- the two reviewers' own commands re-run clean - 46 passed / 0 failed with the
  ROM, 22 passed / 24 skipped without it;
- every corrected figure was re-measured in this session before being written;
- no correction changed a load-bearing claim: the table start, stride, count, the
  eight literal sites, the eight stride sites, the three accessor arithmetic
  paths, the two `BL` callers, the pointer arrays' extents and the boundaries all
  reproduce from the ROM exactly as first reported;
- the probe, both test files and the ROM bible were re-verified against the
  corrected prose, so implementation and documentation cannot drift.

The gate is closed for human handoff. The ticket is **not** integrated, **not**
marked complete in `docs/PROJECT_<local-state-name>`, and `docs/PROJECT_<local-state-name>` is
untouched.

## GIT STATUS

Before the primary commit (`caeb773`), staged explicitly by path:

```text
A  docs/research/LOGX_CHAR_PROVENANCE.md
M  docs/reverse-engineering.md
A  docs/research/LOGX-CHAR-001-review.md
A  tests/integration/test_logx_char_rom.py
A  tests/unit/test_logx_char_reference.py
A  tools/research/logx_char_probe.py
```

Verification performed against that index before committing:

```text
git diff --cached --check         -> exit 0, no output
git diff --cached --stat          -> 6 files changed, 3385 insertions(+), 0 deletions(-)
staged paths matching a proprietary extension (.gba/.sav/.srm/.ss?/.state/.bin/.dump/.raw/.png) -> none
canonical ROM SHA-256             -> 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E (unchanged)
```

`docs/PROJECT_<local-state-name>`, `docs/PROJECT_<local-state-name>`, `src/data/project.ts` and the
active WORKBENCH-006 worktree were **not** touched during the isolated research
pass; the branch was not pushed and was not integrated at that point. The
project-level closeout that followed (queue update, archive record, project-state
entry, integration) is recorded in
[archive/LOGX-CHAR-001-COMPLETE.md](archive/LOGX-CHAR-001-COMPLETE.md), and the
integrated commits correspond to the isolated ones as listed in the header above.

## Closeout validation

Re-run on the integration branch after the cherry-picks, with the canonical ROM
configured, so the accepted measurements are re-proved on the tree that reaches
`master`:

```text
python -m pytest tests/unit/test_logx_char_reference.py \
    tests/integration/test_logx_char_rom.py -q
-> 46 passed in 7.24s

the same with the ROM path pointed at a non-existent file
-> 22 passed, 24 skipped in 0.97s
   (every skip: "canonical Buu ROM not configured locally")
```

The broad gate, `git diff --check`, the staged-scope inspection, the
proprietary-artifact scan and the canonical ROM re-hash are recorded in the
closeout commit's own report.
