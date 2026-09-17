# LOGX-SPRITE-001: reconstruct Buu's Fury sprite-definition / animation-table structure

**Research only. Isolated branch, not integrated, not accepted, not archived.
This document is the ticket's own record and is written by the implementer; the
reviewer reports below carry the reviewer's own words; each block is followed
by an implementer note and by the correction record, and the closure
annotations inside the blocks are marked as such.**

```text
START SHA:                470fe1bcdb733a3acdd05b1a3697b5f55ff5cd0d
END SHA:                  <FINAL>
BRANCH:                   logx-sprite-001
COMMIT SHA(S):            bccd03c  research(sprite): reconstruct Buu sprite definitions
                          e3de67b  research(sprite): correct LOGX-SPRITE-001 review findings
                          <FINAL>  docs(tickets): record LOGX-SPRITE-001 review and SHAs
WORKTREE:                 <temp>\log1-remake-logx-sprite-001

CANONICAL ROM SHA BEFORE: 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
CANONICAL ROM SHA AFTER:  940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
```

Evidence document: [`../research/LOGX_SPRITE_PROVENANCE.md`](../research/LOGX_SPRITE_PROVENANCE.md).
Tooling: `tools/research/logx_sprite_probe.py`.

**Environment note.** The worktree has no local `roms/` directory, and no
junction was created for it this time: LOGX-CHAR-001 recorded that a `roms/`
junction inside a worktree breaks
`tests/unit/test_project_safety.py::test_proprietary_and_generated_paths_are_git_ignored`
(`git check-ignore` exits 128 beyond a symbolic link). The canonical image was
therefore read only through the `LOGX_CANONICAL_ROM` environment variable, which
is what every LOGX integration suite already supports, and the suites that glob
a local `roms/` skip exactly as they do on the baseline.

---

## EXTERNAL CLAIMS TESTED

`mainant/LOGExtractor` `src/sprite_analysis.cpp`, as recorded in
[`GRAPHICS_FORMAT.md`](../research/GRAPHICS_FORMAT.md) §1: a byte animation count
at `+0x00`, an animation-pointer array from `+0x54`, 23 hardcoded semantic
animation slots, a pointer-table base of `0x6B6BB4`, and an animation-leading
`u32` frame count read through a `<< 2` relationship.

| External claim | Verdict |
| --- | --- |
| byte animation count at `+0x00` | **CONFIRMED**: the low byte bounds the inline array at `+0x54`; the high byte is `0` on all 297 objects and the engine reads it with `ldrb` at five sites that compare it against the index they then load |
| animation-pointer array begins at `+0x54` | **CONFIRMED**: 297 of 297 values are word-aligned ROM pointers, the extent is `0x54 + 4*count`, and `0x0800EBD0` is the only read of the field |
| fixed positional slots | **PARTIALLY CONFIRMED**: position is comparable across definitions; a fixed 23-slot array is **REFUTED** |
| the 23 semantic slot names | **NOT PROMOTED**: no engine instruction names an animation; recorded as upstream convention |
| pointer-table base `0x6B6BB4` | **REFUTED as a run base**: it is the accessor's compiler fold, and the bytes it reaches are the last definition object's own inline array |
| animation `u32` + `value << 2` | **PARTIALLY CONFIRMED**: the leading word is the frame count and the engine indexes it with `<< 4` and `<< 2`; frame interpretation is handed to LOGX-FRAME-001 |

---

## SPRITE POINTER RUN START

**CONFIRMED**, GBA `0x086B6BDC` = file offset `0x6B6BDC`. Exactly two
`ldr Rt,[pc,#imm]` sites in the whole image load that literal (`0x0800015E` from
pool `0x080003C0`, `0x0801713E` from pool `0x0801715C`), found by a raw halfword
scan of every even offset of the whole 8 MiB image.

## SPRITE POINTER RUN COUNT

**CONFIRMED as the project's accepted extent**, 297 entries. It is **not** an
engine bound: the accessor is
`push {r4,lr} / cmp r0,#0xa / blt / ldr / lsls / adds / subs / ldr / pop`, with
no comparison against 297 or 307 anywhere, and the run is bounded by the
non-ROM word `0x03001068` at `0x086B7080` plus the fact that every id the
canonical image derives falls inside it.

## SPRITE POINTER RUN BOUNDARY

**CONFIRMED as corroboration, not as the count proof.** The last entry is
`0x086B6B60`, the word after the run is the non-ROM `0x03001068`, and the run is
strictly ascending with 297 unique targets and no duplicate pointer. The run's
first entry, id 10, is preceded by the *inline array of the definition object at*
`0x086B6B60`, not by another run entry.

## SPRITE POINTER RUN IDENTITY

**CONFIRMED**: the run is the array the appearance table's `+0x04` accessor
indexes, `index = id - 10`, ids `10..306`.

## TOTAL RUN ENTRIES

297.

## UNIQUE DEFINITION TARGETS

297. No two run entries hold the same pointer, so the 297 entries name 297
distinct objects.

## APPEARANCE-REFERENCED DEFINITIONS

198, over 232 appearance records. `+0x04` values span `12..306` (run indices
`2..296`); 198 distinct ids resolve to 198 distinct targets with no aliasing, so
no two distinct ids share a definition.

## UNREFERENCED DEFINITIONS

99 of the 297 run entries are never selected by any of the 232 appearance
records, including run indices 0 and 1 (ids 10 and 11).

---

## ENGINE CONSUMERS

| Function | Role |
| --- | --- |
| `0x08000158` | the `+0x04` accessor: `0x086B6BB4 + 4*id` for `id >= 10`; ids `0..9` take a party-slot branch that resolves a 24-byte record at `0x086B82EC` and re-enters through `0x0801713C` |
| `0x0801713C` | a second entry to the same array, reading the id from `u16 [record + 0x0E]`, with **no** party branch |
| `0x08027390` | spawn path: appearance id -> `0x0874D380 + 16*id` -> `+0x04` -> accessor -> `0x0800EB60` |
| `0x0800EB60` | the character constructor; the only reader of `definition + 0x54`; reads `+0x00`, `+0x02`, `+0x04`, `+0x08`, `+0x0A`, `+0x0B`, `+0x50`, `+0x54` |
| `0x0800EDF8` | re-skin/transform; 41 direct `BL` callers |
| `0x0800ECDA` | direct animation selector: `obj+0x50 = def[0x54 + 4*index]`, no range check, 162 `BL` call sites |
| `0x0800ECF0`, `0x0800ED3E` | state selectors: translate a state through the table at `0x08072670`, then the same assignment; `0x0800ED3E` also writes `obj+0x11` |
| `0x0800EF38` | recomputes the current frame: `obj+0x54 = *(u32*)(obj+0x50 + 16*obj[0x11] + 4*obj[0x10] + 4)` |
| `0x0800EF66` | screen position, using the same two-dimensional slot arithmetic |
| `0x0800F53C`, `0x0800F558` | save/restore of the animation-state tuple (`obj+0x11`, `+0x12`, `+0x14`, `+0x50`, `+0x4C`) |

The definition object is render-only in the narrow sense that it carries no
gameplay data this ticket found; it is broader than render-only in that it also
carries a per-animation parallel pointer array (`+0x50`, 10 objects), an
allocation size (`+0x02`) and a palette-remap pointer (`+0x04`, 65 objects).

## DEFINITION OBJECT IDENTITY

**CONFIRMED as a physical object**, described by structure only: a variable-size
object whose extent is `0x54 + 4 * count` and whose trailing inline array holds
`count` 32-bit ROM pointers to animation records. Its semantic identity as a
"sprite definition" is **PARTIALLY CONFIRMED**: the appearance table's `+0x04`
selects it, the character constructor builds a renderable object from it, and
the engine's shape matches the accepted ROM bible's "character structure". This
ticket does not claim it is the only such structure or that the 297 cover every
character.

## `+0x00`

`u16` little-endian, low byte `1..23` over 14 distinct values, high byte `0` on
all 297 objects. Read as a **byte** by `ldrb` at `0x08013046`, `0x08013088`,
`0x080131DA`, `0x0802736C`, `0x0802A28E`. **PHYSICAL FIELD: CONFIRMED.**

## COUNT SEMANTIC

**CONFIRMED.** Two independent lines of evidence: the object extent
`0x54 + 4*count` (232 of 296 consecutive run pairs place the next definition
exactly there; the 65 exceptions are separated by exactly `0x100`, the remap
block, so the formula holds for every object and the last object ends exactly at
`0x086B6BDC`), and five engine sites that read the byte, compare it with an
index, and only then load `definition + 0x54 + 4*index`.

## ANIMATION-COUNT SEMANTIC

**CONFIRMED.** The bounded elements are animation pointers, and the selector
uses indices in `0..21`. The count is not consulted at the selection site (there
is no range check); it is consulted at the five guarded reads.

## `+0x54`

`u32` little-endian, the first element of an inline array of `count` 32-bit ROM
pointers. 297 of 297 values are word-aligned ROM pointers. **PHYSICAL FIELD and
ANIMATION-ARRAY SEMANTIC: CONFIRMED.**

## ANIMATION-ARRAY SEMANTIC

**CONFIRMED** (see above). 4,070 slots over the 297 counts: **1,721 non-null,
2,349 null**. Index 0 is non-null in 297 of 297 definitions; index 1 in 262 of
285; index 22 in 5 of 5.

## PREFIX `+0x04..+0x53`

| Offset | Status |
| --- | --- |
| `+0x02` `u16` | **CONFIRMED** as a byte size handed to the allocator `0x0803D5B8`; 8 distinct values, never zero. Its second use through `0x0801124C` (`>> 6`) is **INFERRED** as a block-pool size |
| `+0x04` `u32` | **CONFIRMED** as a pointer to the 256 bytes immediately before the object, in exactly the 65 objects that have it (`+0x04 == address - 0x100`, 65 of 65). The 256 bytes are a near-identity byte permutation with 4..50 substitutions; the palette-remap reading is **INFERRED** |
| `+0x08` four bytes | byte 0 is added to a screen x coordinate (`0x0800EF74`); bytes 2 and 3 select a resource through `0x08013E38`. Semantics **UNRESOLVED**, recorded as four separate bytes |
| `+0x0C` `u32` | **UNRESOLVED**; no consumer found |
| `+0x10..+0x4F` | four 16-byte records of four `s32`; **UNRESOLVED**; no consumer found, value ranges are rect-like |
| `+0x50` `u32` | **PARTIALLY CONFIRMED**: a parallel per-animation pointer array used by the 10 objects that have one; entry meaning **UNRESOLVED** |

**PROJECT CONCLUSION: none of `+0x04..+0x53` is padding.** Four of the six areas
have at least one engine consumer; the two without (as scoped in §12.3 of the
provenance document) are preserved as unknown.

## ANIMATION-SELECTION MECHANISM

**CONFIRMED** as a selector index, with a state-to-index **translation table** in
front of two of the three entry points.

* `0x0800ECDA(obj, index)` assigns `def[0x54 + 4*index]` to `obj+0x50` with no
  range check; 161 of its 162 direct `BL` call sites pass a compile-time
  constant in `0..21`.
* `0x0800ECF0(obj, state)` and `0x0800ED3E(obj, state, row)` first read
  `u8[0x08072670 + state]`; exactly three sites in the image read that table
  (`0x0800ECF6`, `0x0800ED48`, `0x0802CB96`).
* the table is `0..15` identity, `16..22 -> 17..23`, and states 23/24 alias
  indices 10/11; entries above 24 are zero. It is a translation, not an
  identity: state and animation index are not in bijection.
* `0x0800EF38` then computes the current frame from `obj+0x11` (frame) and
  `obj+0x10` (direction slot) with `16*` and `4*` scales.

## FIXED-SLOT MODEL

**PARTIALLY CONFIRMED / REFUTED in part.** Fixed *positional* slots are
**CONFIRMED structurally**: "animation index k" means the same array position for
every definition, the selectors apply no per-definition translation, and the five
guarded reads treat `+0x58`, `+0x6C`, `+0x70`, `+0x74` as indices 1, 6, 7, 8.
A fixed **23-slot** model is **REFUTED**: the extent tracks the count, counts are
`1..23` over 14 values, and 2,349 of 4,070 slots are null.

## VARIABLE-LENGTH MODEL

**CONFIRMED.** Extent is `0x54 + 4*count`.

## SPARSE-SLOT MODEL

**CONFIRMED.** Nulls are real and are not filtered: the selectors copy the
loaded word into `obj+0x50` with no null test. A selected null is a null
animation base, which is a data property of the definition.

## SEMANTIC SLOT RESULTS

**Mostly UNRESOLVED, and deliberately left so.** Four positions have an
engine-visible *role* rather than a name: index 1 is tested before a state-object
swap (`0x0802736A`), index 6 before a two-versus-three selection (`0x0802A28A`),
index 7 before allocating a 12-byte object and before an unrelated check
(`0x08013044`, `0x080131D8`), and index 8 before dispatching the state method
with the argument `8` (`0x08013086`). Positions are comparable across
definitions and their occupancy is measurable, but **no engine instruction names
an animation**, LOGExtractor's `stand/walk/run/attack/...` labels are **not
promoted**, and the 23-slot numbering is **not adopted**. In particular, no code
adds one to an animation index, so a `slot = index + 1` shift has no witness.

## TOTAL ANIMATION REFERENCES

4,070 slots over the 297 definitions, of which **1,721 are non-null**.

## UNIQUE ANIMATION TARGETS

**1,017** distinct animation records.

## SHARED ANIMATION TARGETS

410 of the 1,017 records are referenced from more than one (definition, index)
site; maximum reuse 16. 1,721 references over 1,017 targets.

## NULL ANIMATION ENTRIES

**2,349** of the 4,070 slots.

## FIRST POINTER-RUN ENTRY

**RESOLVED, and the LOGX-CHAR-001 question is closed.** Run index 0 is id 10 and
carries no special meaning. The accessor's folded base `0x086B6BB4` is not a run
prefix: the ten words it reaches (`0x086A6424, 0x086A7238, 0, 0, 0x086A7E7C, 0,
0, 0, 0, 0x086A899C`) are the inline animation array of the definition object at
`0x086B6B60`, which is the run's own last entry (id 306, count 10, array
`0x086B6BB4..0x086B6BDC`). Ids `0..9` are party-slot selectors and never index
the array. `probe.folded_base_explanation` re-derives this by scanning for a
definition header whose count lands the object exactly on the run, and finds
exactly one candidate.

## FULL-CENSUS RESULTS

Every figure states its population.

| Population | Value |
| --- | ---: |
| pointer-run entries | 297 |
| unique definition targets | 297 |
| appearance records (LOGX-CHAR-001) | 232 |
| appearance `+0x04` ids used | 198 |
| appearance-referenced definitions | 198 |
| appearance-unreferenced definitions | 99 |
| definition inline-array slots | 4,070 |
| non-null animation references | 1,721 |
| null animation references | 2,349 |
| unique animation records | 1,017 |
| animation records with more than one referrer | 410 |
| animation frame-pointer slots | 13,660 |
| unique frame records | 10,980 |
| frame records with more than one referrer | (max reuse 4) |
| definitions with nonzero `+0x04` | 65 |
| definitions with nonzero `+0x50` | 10 |
| definitions with nonzero `+0x0C` | 14 |

Definition element counts, over the 297: `{1:12, 2:41, 3:1, 5:2, 10:51, 13:44,
15:1, 16:3, 18:9, 19:67, 20:29, 21:16, 22:16, 23:5}`.

Animation frame counts, over the 1,017 unique records: `{1:80, 2:275, 3:180,
4:407, 5:16, 6:13, 7:11, 8:3, 9:2, 10:2, 11:24, 12:2, 16:2}`.

Frame `piece_count`, over the 10,980 unique frame records: `{1:10959, 2:19,
4:2}`.

**Reconciliation with the accepted corpus.** The accepted reader itself
(`tools.webfoot.graphics.load_actor_sprites`) was re-run on the canonical image:
295 structures listed, 1,562 animation references, 1,013 unique animation
offsets, 10,964 frame pointers of which 10,959 resolve, 7,355 graphics payloads.
Every figure in `GRAPHICS_FORMAT.md` is reproduced exactly once the reader's
per-structure deduplication and its two filters are accounted for:
`1017 - 4 = 1013`, `13660 - 64 = 13596`, `10964 - 5 = 10959`.

## REPRESENTATIVE DEFINITIONS

| id | address | count | size | raw header, fixed block and array |
| ---: | --- | ---: | ---: | --- |
| 10 | `0x086A89D0` | 2 | `0x400` | asserted byte-exact by the ROM-gated suite |
| 12 | `0x086A8A88` | 2 | `0x200` | asserted byte-exact |
| 115 | `0x086AD1CC` | 22 | `0x400` | animation index 0 is `0x0850C1DC`, `frame_count` 2, trailer `(1, 0x400)`, first frame `0x0850C13C` with `piece_count` 1 |
| 306 | `0x086B6B60` | 10 | `0x400` | asserted byte-exact; its array *is* the accessor's folded base |

## ANOMALIES

1. The run's last definition object occupies the bytes immediately before the
   run, which is why the accessor's folded base points into a different structure
   than the run holds.
2. 65 objects are preceded by, and point at, a 256-byte near-identity byte
   permutation; the correlation is exact (65 and 65).
3. `+0x02` is both a byte size and, after `>> 6`, a block-pool index.
4. A selected animation can be null and no selector tests for it.
5. `+0x50` is populated for only 10 of 297 objects, and the constructor branches
   on it.
6. The state table aliases states 23 and 24 onto animation indices 10 and 11.
7. Five frame pointers inside accepted animations do not resolve under the
   accepted reader's `_frame_offset`, which is why its frame total is 10,959.

## TOOLING ADDED

`tools/research/logx_sprite_probe.py`: SHA-256 gated, read-only, deterministic,
capstone deferred to first use. Reports: the pointer run and the folded-base
explanation; the definition census with the prefix, the count distribution, the
array-slot occupancy by position and the animation-reference arithmetic; the
`+0x04 == address - 0x100` invariant; the comparison of the counted extent with
the accepted next-structure walk, with both the 296-pair and 297-boundary
populations; the animation and frame censuses including the measured trailer
histograms; the appearance join, reusing LOGX-CHAR-001's probe rather than
re-deriving it; the state table with its four reader sites, its one address
literal and the bytes that follow it; the selector's argument census; and an
engine-evidence report (`--engine`) that re-reads every quoted instruction.

## TESTS ADDED

* `tests/integration/test_logx_sprite_rom.py`: 27 ROM-gated tests.
* `tests/unit/test_logx_sprite_reference.py`: 38 portable tests.

## TEST RESULTS

Measured on the corrected, committed revision, not derived.

| Command | Result |
| --- | --- |
| `pytest tests/unit/test_logx_sprite_reference.py tests/integration/test_logx_sprite_rom.py -q` | **65 passed** |
| the same with `LOGX_CANONICAL_ROM` pointed at a non-existent file | **40 passed, 23 skipped**, every skip reported as "canonical Buu ROM not configured locally" |
| `pytest tests/unit tests/integration/test_logx_sprite_rom.py tests/integration/test_logx_char_rom.py tests/integration/test_graphics_rom.py -q` | **1484 passed, 44 skipped** |
| `pytest tests/integration/test_logx_{sprite,char,codec,connector,layer,map_record,map_render,tile}_rom.py tests/integration/test_text_rom.py tests/unit/test_project_safety.py tests/unit/test_code_review_workflow.py tests/unit/test_workflow_migration.py -q` | **210 passed, 37 skipped** |
| `pytest tests/unit -q` with a meta-path blocker that makes `import capstone` raise (CI's exact command and dependency set) | **1422 passed, 16 skipped, 0 failed** |

The 44 and 37 skips are the suites' own guards being reported honestly: the
graphics ROM suite and `test_text_rom.py` glob a local `roms/` directory this
worktree deliberately does not have, and the rest are the pre-existing PySide6,
site-build and local-dump guards. No ticket-caused failure was observed and no
test was weakened.

## ROM_BIBLE_IMPACT

`docs/reverse-engineering.md` gains one section, **LOGX-SPRITE-001
sprite-definition objects and animation tables**: the run's identity and the
folded base's real meaning; the definition layout table; the count with its five
guarded reads and the extent arithmetic; the inline array with its occupancy; the
animation record and the selection mechanism with the state translation table;
the positional-versus-semantic slot distinction; and the disagreement with the
accepted graphics corpus. It writes no semantic slot name: "stand", "walk",
"run" and the rest appear only as LOGExtractor claims that were not promoted.
One bracketed note is appended to the existing LOGX-CHAR-001 section recording
that this ticket resolved that section's first-entry question; the original
paragraph is left as LOGX-CHAR-001 wrote it.

## public progress impact

**NONE.** Isolated research with no shipped SDK capability, no public frontier
and no product-story change. `src/data/project.ts` is untouched,
`docs/PROJECT_<local-state-name>` is not modified, `docs/PROJECT_<local-state-name>` is not
updated, and the ticket is not archived, because it has not been independently
accepted or integrated.

---

## DISAGREEMENTS WITH LOGEXTRACTOR

1. **The pointer-table base.** `0x6B6BB4` is the accessor's compiler-folded
   arithmetic base, and the bytes it reaches are another object's inline array.
   The accepted run starts at `0x086B6BDC` and its first entry is id 10.
2. **The animation count is not a loop bound.** The engine reads it at five
   guarded sites; the selector itself has no range check at all.
3. **Fixed 23 semantic slots.** Position is fixed; the array is count-bounded and
   sparse; the slot *names* are not engine facts.

## DISAGREEMENT WITH THE ACCEPTED GRAPHICS CORPUS

`tools/webfoot/graphics.py::_animations_in` walks animation pointers from `+0x54`
to the **next structure**, stating that "no field in this header has been shown
to bound the list". That justification is **refuted**: `definition + 0x00` bounds
the list and five engine instructions use it as an index bound. The walk scans
8,230 slots where the count model scans 4,070; its 4,160 extra slots are all
nonzero and none is a ROM pointer (they are the 256-byte remap blocks read as if
they were pointers), so its corpus figures survive only because its pointer
filter discards them. Its "1,562 animation references" is a per-structure
deduplicated count, not the slot count of 1,721. **No accepted artifact was
modified**: the finding is documented and flagged for synthesis or a targeted
correction.

## UNRESOLVED QUESTIONS

1. What the 256-byte block at `definition - 0x100` is used for.
2. What `definition + 0x0C` and `definition + 0x10..+0x4F` hold.
3. What the animation record's two trailer words mean.
4. What `obj+0x12` is.
5. Which game states the state table's `0..24` correspond to.
6. Whether any producer passes a state above 24 or an index at or above a
   definition's count.
7. Which definitions reach only the 4 art-filter-rejected animations.
8. What the five unresolvable frame pointers are.

## HANDOFF TO LOGX-FRAME-001

* Animation record: `u32 frame_count` at `+0x00`, then `4 * frame_count` 32-bit
  ROM pointers; slot `d` of frame `f` at byte offset `+0x04 + 16f + 4d`.
* Selected by `0x0800ECDA(obj, index)` -> `obj+0x50`; the state entry points
  translate through `0x08072670` first; `0x0800EF38` reads the current frame into
  `obj+0x54`.
* 1,017 unique animation records over 1,721 non-null slots; 13,660 frame-pointer
  slots over 10,980 unique frame records.
* Representative raw prefix: definition id 115 at `0x086AD1CC` (count 22),
  animation `0x0850C1DC` (`frame_count` 2, pointers `0x0850C13C`, `0x0850C164`,
  `0x0850C18C`, `0x0850C1B4`, trailer `(1, 0x400)`), frame `0x0850C13C`
  (`piece_count` 1, bytes `F8 E8 20 20` at `+0x04`).
* Entry points and the count/metadata needed to locate frames are listed in
  §15 of the provenance document.
* **Not done here**: frame-count interpretation, frame-record internals, piece
  counts, per-piece graphics pointers, OAM attributes and flip flags, frame
  origins.

## OTHER DOWNSTREAM HANDOFFS

* **TOOLKIT-010 / `GRAPHICS_FORMAT.md`**: the extent-model correction above.
* **`tools/webfoot/graphics.py`**: `_animations_in` should read `count` from
  `definition + 0x00`; `sprite_graphics.decode_animation` needs no change.
* **LOGX-CHAR-001**: its two UNRESOLVED items about the run are resolved; its
  accepted conclusions are unchanged.
* **Future authoring work**: an animation slot is optional, so an editor must be
  able to write a null element and must not assume 23 positions exist.

---

## REVIEWER A

Engine/dataflow/object-layout focused. Fresh context; nothing read from the
documents was trusted, and every figure was re-derived from raw bytes and
disassembly. Reviewed `bccd03c`; the review was in flight while the
implementer's own corrections landed, and Reviewer A re-verified the delta's
claims where they touched its scope.

```text
CODE REVIEW

Verdict: APPROVE WITH NON-BLOCKING NOTES

Scope reviewed: docs/research/LOGX_SPRITE_PROVENANCE.md;
  tools/research/logx_sprite_probe.py; tests/integration/test_logx_sprite_rom.py;
  tests/unit/test_logx_sprite_reference.py; the "## LOGX-SPRITE-001" section and
  the LOGX-CHAR-001 bracketed note in docs/reverse-engineering.md.

Reproduced independently (raw bytes / Capstone, never the probe, for raw checks):
- Run at 0x086B6BDC: 297 contiguous strictly-ascending in-ROM words, first
  0x086A89D0, last 0x086B6B60, 297/297 unique, terminator 0x03001068 at
  0x086B7080. Whole-image raw halfword scan (117,008 ldr-literal sites): exactly
  two carry literal 0x086B6BDC - 0x0800015E (r1, pool 0x080003C0) and
  0x0801713E (r1, pool 0x0801715C).
- THE CENTRAL CLAIM IS CORRECT. 0x086B6B60 header u32 = 0x0400000A (count 10,
  high byte 0), +0x02 = 0x0400; 0x086B6B60+0x54+4*10 = 0x086B6BDC exactly; the
  ten words 0x086B6BB4..0x086B6BD8 are 0x086A6424,0x086A7238,0,0,0x086A7E7C,
  0,0,0,0,0x086A899C and are byte-identical to that object's own inline array;
  0x086B6B60 is run entry 296 (id 306). Backward header scan finds exactly one
  object whose counted extent lands on the run.
- Fold: 0x086B6BDC+4*id-0x40+0x18 == 0x086B6BB4+4*id for id 0..399. 0x0801713C
  is the identical arithmetic with no party branch. Party branch:
  0x08054FBC+0x14 -> 0x68-stride record -> byte at +0x14 -> *24 + table
  0x086B82EC (pool 0x080003C4); records 0..11 u16+0x0E = 115..121,121,120,106..108.
- Five count-guard sites re-read from raw bytes with exact encodings (e.g.
  0x08013046 ldrb r1,[r0] raw=0178; 0x08013048 cmp r1,#7 raw=0729;
  0x0801304C ldr r0,[r0,#0x70] raw=006f). Exhaustiveness STRENGTHENED: an
  independent desync-immune raw halfword triple scan over the whole 8 MiB image
  returns exactly those five, as does the Capstone sweep (183,296 instructions,
  exactly the document's figure). No sixth site.
- Count is a byte, high byte 0 on all 297; low byte 1..23 over 14 values;
  distribution matches. +0x02 handed to 0x0803D5B8 at 0x0800EC02 and divided by
  64 at 0x08011252 (asrs r0,r1,#6, raw 8811); 8 block sizes, never zero. 232/65
  +0x04 invariant exact with zero deviations.
- 0x0800EF38 = ldrb [r0,#0x11]; ldr r1,[r0,#0x50]; lsls #4; adds;
  ldrb [r0,#0x10]; lsls #2; adds; ldr [r1,#4]; str [r0,#0x54] - engine
  arithmetic 16*frame+4*dir+4. 0x08027390 matches. Census: 4,070 slots / 1,721
  non-null / 1,017 animations / 13,660 frame slots / 10,980 unique frames /
  piece-count {1:10959,2:19,4:2}; appearances 232 records, 198 ids, 198 targets,
  99 unreferenced, 25 shared.
- Caller census reproduced exactly: 121 (0x08000158), 19 (0x0801713C), 162
  (0x0800ECDA), 41 (0x0800EDF8). 0x0800ED3E writes obj+0x11 at 0x0800ED7C (raw
  6574). State table bytes match. Class vtables: 0x0804AC20+0x28 -> 0x0800ECF0,
  +0x0C -> 0x0800EF38, +0x30 -> 0x0800ED3E; 0x0804CEB8+0x28 -> 0x08027468 ->
  0x0800ED18 (swaps obj+0x14 only).
- graphics.py: the quoted justification is verbatim (lines 687-689); the profile
  has character_table_address 0x086b6bdc and animation_pointer_offset 0x54, so
  the reader's walk model matches the probe's exactly. Measured 4,070 counted vs
  8,230 walked, 4,160 extra, all nonzero, none a ROM pointer - reproduced.
- Frame boundary: 0x080273F0 ldrsb (r3=4), 0x080273F4 ldrsb (r3=5),
  0x0802740C ldrb [r3,#6], 0x08027410 ldrb [r3,#7] with r3 = obj+0x54 = frame
  record. So the four recorded bytes are exactly what the constructor reads.
- Probe is deterministic: --engine and --rows (590,562 bytes) byte-identical
  across runs. With capstone blocked by a meta_path hook the module still imports
  and load_rom/run_report/definition_census still work (instruction_at raises as
  documented) - the deferred import is real.
- 11 deliberate expectation perturbations in scratch copies all FAILED as
  required. Tests: 62 passed at bccd03c.

Non-blocking findings:
N1. Section 4 extent arithmetic was inconsistent (232 + 65 = 297 > 296).
  CLOSED: the document now states 231 of 296 pairs and 232 of 297 boundaries,
  the probe reports both populations, and a test asserts both.
N2. "0x0800EBD0 is the only reader of a definition's +0x54" was false as written:
  0x0800ECE0, 0x0800ECFE and 0x0800ED50 read the same word with an index added.
  CLOSED: sections 3.2, 5 and 12.1 now separate the scalar read from the three
  indexed reads; the falsification sweep found no additional reader.
N3. Section 3.2 attributed +0x00 and +0x08 reads to 0x0800EB60 that its body does
  not perform. CLOSED: the field list is now +0x02, +0x04, +0x0A, +0x0B, +0x50,
  +0x54.
N4. Section 7's trailer-1 summary was wrong (21 distinct values, not 5 with 11
  outliers). CLOSED: the measured histograms are quoted and asserted.
N5. The integration test docstring said no ROM bytes are committed while three
  raw dumps were. CLOSED: the raw dumps are gone; the tests assert field values
  and a round-trip of the packed dump, and the docstring matches.
N6. Three EXPECTED_OBJECT_ENDING_AT_RUN keys were dead. CLOSED: the assertions
  read the dict.
N7. PROCESS: the reviewed files were edited during the review. CLOSED for the
  delta by committing it and re-running both reviewers' checks; the artifact
  under closure is the committed revision recorded in the header.

Correctness: PASS.
Architecture/product alignment: PASS.
ROM/data safety: PASS. SHA-256 940AD5F0...F059E, 8,388,608 bytes, identical
  before and after; no tracked file modified by the reviewer; scratch confined to
  the git-ignored build/research/.
Determinism: PASS.
Tests/evidence: PASS.
Compatibility: PASS.
Maintainability: PASS.
Public-release hygiene: PASS with N5.
Reviewer validation performed: 15 scratch verification scripts plus a
  perturbation harness under build/research/, all git-ignored.
Remaining uncertainty: the +0x0C / +0x10..+0x4F negative claim was not
  re-scanned by this reviewer.
```

**Implementer note on Reviewer A's report.** Findings N1-N6 were reproduced from
the image and applied as K1-K7 below; N7 (mid-review drift) was closed by
freezing and committing the delta. Reviewer A then re-reviewed the frozen
revision `e3de67b` and returned:

```text
CODE REVIEW (delta) - e3de67b93d460918a1feb21946c8562d992e82cf

Verdict: APPROVE WITH NON-BLOCKING NOTES
Blocking findings: none
N1 CONFIRMED CLOSED   N2 CONFIRMED CLOSED   N3 CONFIRMED CLOSED
N4 CONFIRMED CLOSED (headline numbers) - with new issue D2
N5 PARTIALLY CLOSED (24-byte residual of the same class)
N6 CONFIRMED CLOSED   N7 CONFIRMED CLOSED
New claims: five null tests CONFIRMED; fourth state-table reader CONFIRMED
New non-blocking issues: D1, D2, D3, D4
Correctness PASS / Arch PASS / ROM-data safety PASS / Determinism PASS /
Tests-evidence PASS (65 passed) / Compatibility PASS / Maintainability PASS /
Public-release hygiene PASS with the N5 residual
```

Reviewer A's D1-D4 were reproduced and are closed as K22-K25 below; D4 in
particular is the reason the reviewer blocks in this document are no longer
described as verbatim.

## REVIEWER B

Census/slot-semantics/adversarial focused. Fresh context; the probe's own census
functions were never the instrument, and the accepted reader was re-run
independently. Reviewed `bccd03c`; its two in-flight findings were already fixed
when it reported.

```text
CODE REVIEW

Verdict: REQUEST CHANGES

Scope reviewed: the same five artifacts, each re-derived with struct.unpack,
raw-Thumb halfword scans and capstone.

PROCESS: the tree moved during the review. The final verdict therefore covers the
committed revision recorded in this document's header, not only bccd03c.

Blocking findings:
B1. "232 of the 296 consecutive run pairs" is impossible (232+65=297). Measured:
  231 of 296 pairs at delta 0, 65 at +0x100. CLOSED: both populations are now
  stated, reported and asserted, and the 65 gaps are shown to be the 65 objects
  the *successor* points at.
B2. The section 7 trailer claim was wrong: trailer-1 has 21 distinct values,
  with 43 records outside the five named values. CLOSED: the histogram is quoted
  and asserted; the document no longer says "5 values with 11 outliers".
B3. "No engine code was found that guards the selection" was falsified: all five
  count-guard sites null-test the element they load (0x0801304E/50,
  0x08013090/92, 0x080131E2/E4, 0x08027374/76 cmp+beq, 0x0802A296/98 cmp+bne).
  CLOSED: sections 4, 5, 8.3 and 13.4 now attribute the null test to the five
  guarded sites and the absence of one to the three selectors only, and the
  probe reports the null-test address for each guard.
B4. "Entries above 24 are zero" was false: index 25..31 are 0, a hypothetical
  index 32 would read 1, and bytes +0x24..+0x2B are 0xFF. CLOSED: the document
  now states the table's used range and reports the bytes after it; a test pins
  them.
B5. Committed ROM-derived fixtures (308 bytes of DEFINITION_*_RAW) while the
  docstring said none were. CLOSED: the raw dumps were removed; the tests now
  assert field values, list lengths and a round trip of the packed dump.
B6. The selector histogram said 159 constants with 1:6. Measured 161 with 1:8.
  CLOSED and independently reproduced: 162 sites, 161 constant in 0..21, one
  runtime index at 0x0802CB9A.

Non-blocking findings:
N1. The +0x10..+0x4F column ranges were record 0 only. CLOSED: both the
  all-record and first-record ranges are stated.
N2. A FOURTH state-table path (0x0800EEB0/0x0800EEB6) reaches the table from the
  literal 0x080725F0 with adds #0x80 and uses it as a predicate. CLOSED and
  promoted to a blocking-level correction: the probe, the document and a test
  now carry four sites, and the test pins the literal list rather than the
  probe's own constant.
N3. Section 5's "only read of the field" was unscoped. CLOSED.
N4. "No object carries an index at or above its own count" is true by
  construction of the reader and cannot support the count model. CLOSED: the
  sentence is removed and replaced by the extent arithmetic, the five guards,
  index-0 universality and the nonzero word at +0x54 + 4*count.
N5. Section 9 under-reported index 7. CLOSED: both index-7 bodies then select
  index 7 and call 0x0800ED18.
N6. Section 13.1's title said "two objects" and named one. CLOSED.
N7. Section 14.7 was answerable. CLOSED: definitions 146 and 163 reach only
  rejected animations; the fourth rejected record is reached by definition 47.
N8. Probe JSON key hazards. CLOSED: renamed to slots / non_null_slots /
  null_slots / malformed_slots, frame_slots_over_unique_animations, max_value vs
  largest_state, and the bytes-after-the-table field.

Circular or weak test expectations (C1-C6), all addressed:
C1. The guard test compared the array offset to the probe's own expression.
  CLOSED: it compares to a literal offset map.
C2. pointer_for was compared to the expression the list was built from. CLOSED:
  the pointer tuple is now literal expectation data.
C3. The extent test restated its own properties. CLOSED: it now asserts both
  populations and the per-object gap relationship.
C4. The determinism test compared one pure function to itself. CLOSED: it now
  also asserts that a one-byte change moves the report.
C5/C6. Constant-vs-constant geometry tests are labelled as internal consistency,
  and the state-table assertions now use literal site lists.
Coverage gaps CLOSED: tests now cover the selector histogram, the trailer
  histograms, the state-table bytes beyond index 24, the pair/boundary
  populations, the null tests and the boolean-file invariant.

Reproduced exactly (independent): the run, the folded-base uniqueness, the count
  distribution, the +0x02 sizes, the +0x04 232/65 with deviations 4..50, +0x0C
  14, +0x50 10, the +0x08 byte distributions, all 23 array occupancy rows, 1,017
  animations / 410 multi-referrer / max reuse 16, the frame-count distribution,
  13,660 / 10,980 / max reuse 4 / 0 malformed, piece_count {1:10959,2:19,4:2},
  the appearance join 232/198/198/99/25, the 25 state-table bytes, the five
  guard sites with an independent pattern scan finding exactly those five, the
  183,296-instruction census, the four caller counts, the party table row, the
  class method table, and the section 15 representative prefix.
Accepted corpus, with the real load_actor_sprites: 295 characters, 7,355
  graphics, 1,013 accepted animations, 13,596 accepted direction slots, 4
  rejected animations (frame counts 7, 2, 2, 5 = 16 frames = 64 slots), frame
  pointers accepted 10,964 / rejected 16 / disjoint, exactly 5 accepted pointers
  failing _frame_offset (0x08424F9C, 0x0869AF3C/5C/7C/9C), 10,959 accepted
  frames, 1,562 = per-structure distinct accepted references. The walk and the
  counted-filtered model agree for all 297 structures, so the recommended
  correction changes no accepted figure.
Slot-model alternatives attacked quantitatively: no base offset 0x3C..0x64
  makes the array dense, no stride 8/12/16 beats stride 4, an (index, pointer)
  pair array is refuted, and all 2,349 non-pointer values are exactly 0. So
  "sparse" is the only reading the data supports.

Correctness: FAIL. Architecture/product alignment: PASS.
ROM/data safety: PASS.
Determinism: PASS (two include_rows builds byte-identical, 221,491 characters).
Tests/evidence: PASS with caveats.
Compatibility: PASS.
Maintainability: PASS with N8's notes.
Public-release hygiene: FAIL.
Remaining uncertainty: no ARM-state or outside-0x08000000..0x08060000 coverage;
  the selector-argument classification uses a lookback heuristic.
```

**Implementer note on Reviewer B's report.** Every one of B1-B6 and N1-N8 was
reproduced from the image and applied as K1-K21 below, and the six circular test
expectations as K19-K20. Reviewer B then re-reviewed the frozen revision
`e3de67b` and returned:

```text
REVIEWER B - DELTA RE-REVIEW of e3de67b93d460918a1feb21946c8562d992e82cf

B1 CONFIRMED CLOSED. Both populations stated and asserted; probe keys
   consecutive_pairs=296, consecutive_pairs_where...=231,
   structures_where_the_counted_end_is_the_next_boundary=232; the new 65-gap
   claim verified independently (all 65 deltas exactly 0x100; each gap address ==
   the successor's +0x04 == the predecessor's counted end; the preceded-by-gap
   set equals the +0x04 != 0 set as sets; the followed-by-gap set is a different
   65; ids 10 and 306 in neither).
B2 CONFIRMED CLOSED for the data, with one new prose defect (NEW ISSUE 1).
B3 CONFIRMED CLOSED. The five null tests are cmp rX,#0 followed by
   beq/beq/beq/beq/bne. CORRECTION TO MY OWN EARLIER REPORT: I had cited the
   branch addresses; the commit's addresses are right.
B4 CONFIRMED CLOSED for the data, with one new prose defect (NEW ISSUE 2).
B5 CONFIRMED CLOSED in substance. One residual: a 24-byte ROM byte string is
   still committed (NEW ISSUE 5).
B6 CONFIRMED CLOSED. selector_argument_census matches my independent scan
   exactly: 162 sites, 161 constants, the documented histogram, max 21,
   runtime_index_sites 1 at 0x0802CB9A, unresolved 0.
N1..N8 ALL CONFIRMED CLOSED. N2 VERIFIED, not falsified: a whole-image
   literal+adds sweep finds exactly four addressing paths.
C1/C2/C3 CLOSED; C4 CLOSED and strengthened; coverage gaps closed.

NEW ISSUES:
1. BLOCKING (prose, self-inconsistent): the trailer-1 breakdown says 15 other
   values / twelve large; correct is 16 / thirteen (21 - 5 named = 16; measured
   3 small + 13 large).
2. BLOCKING (prose, wrong bytes): the +0x19 sixteen-byte quote ends in 00 where
   the image has FF, and "the eight bytes at +0x24 are 0xFF" should be +0x28.
3. Non-blocking: section 12.2's "34 unguarded sites" is not reproducible from the
   stated pattern; the count is window-dependent.
4. Non-blocking: section 3.2's "not +0x08" conflicts with its own table row.
5. Non-blocking hygiene: the integration test docstring's absolute "No
   ROM-derived fixtures are committed" versus the 24-byte tail string.
6. Non-blocking: this ticket record was committed with the SHA fields pending.
7. Non-blocking dead code: probe _ldr_pool and two predicate constants.

FINAL VERDICT: REQUEST CHANGES. Every prior blocking finding is closed in
substance and the delta is a genuine improvement, but the corrected prose
introduces two new false numeric statements. Both are one-line fixes; no measured
number in the probe, the tests or the ROM model is wrong.
ROM verified identical before and after; git diff --check clean.
```

All seven new issues were reproduced in this session and are closed as K22-K28
below. Reviewer B's B2 and B4 residuals are the same class as A's D1 and D2, and
B5's residual is A's N5 residual, so the last four corrections are single fixes
that close both reviewers' remaining items. Reviewer B then confirmed all seven
on the frozen revision `1a3eb70`, closing its REQUEST CHANGES into **APPROVE**
with one non-blocking recommendation (drop section 12.2's illustrative window
counts, which it could not reproduce under any natural rule variant); that
recommendation was applied as K29:

```text
REVIEWER B - FINAL CONFIRMATION, LOGX-SPRITE-001 @ 1a3eb7011628ce6d779108838574e5619ee1f503

1. CONFIRMED CLOSED   2. CONFIRMED CLOSED   3. CONFIRMED CLOSED in substance
  (non-blocking: the three illustrative counts do not reproduce; recommendation
  to delete them or pin the rule)
4. CONFIRMED CLOSED   5. CONFIRMED CLOSED (a scan of all 440 committed text
  files for 16+ byte hex runs finds no contiguous ROM byte literal in any
  LOGX-SPRITE-001 artifact)   6. CONFIRMED (only the two intentional <FINAL>
  tokens remain)   7. CONFIRMED CLOSED

NEW BLOCKING FINDINGS: none.
FINAL VERDICT for 1a3eb70: APPROVE.
ROM verified identical before and after; git show --check exit 0; 65 passed.
```

## REQUIRED CORRECTIONS

Every finding from both reviewers was reproduced in this session from the image
before being applied; none was rejected on substance. 29 distinct corrections
were accepted and are closed.

| # | Correction | Source | Status |
| ---: | --- | --- | --- |
| K1 | "232 of the 296 pairs" -> both populations: 231 of 296 pairs and 232 of 297 boundaries; probe reports both; test asserts both | A-N1, B-B1 | CLOSED |
| K2 | The 65 gaps belong to the *successor's* `+0x04`, and the "has `+0x04`" set equals the "preceded by a block" set, verified as sets | A-N1, B-B1 | CLOSED |
| K3 | "0x0800EBD0 is the only reader of `+0x54`" -> the only *unindexed* read; 0x0800ECE0 / 0x0800ECFE / 0x0800ED50 are indexed reads of the same word | A-N2, B-N3 | CLOSED |
| K4 | `0x0800EB60` reads `+0x02`, `+0x04`, `+0x0A`, `+0x0B`, `+0x50`, `+0x54` - not `+0x00` or `+0x08` | A-N3 | CLOSED |
| K5 | Trailer histograms quoted and asserted (trailer-0: 7 values; trailer-1: 21 values) | A-N4, B-B2 | CLOSED |
| K6 | Committed `DEFINITION_*_RAW` dumps removed; field values, lengths and a packed-dump round trip instead; docstring corrected | A-N5, B-B5 | CLOSED |
| K7 | `EXPECTED_OBJECT_ENDING_AT_RUN` keys now actually read | A-N6 | CLOSED |
| K8 | Freeze-and-commit the delta; both reviewers re-verify the committed revision | A-N7, B-process | CLOSED |
| K9 | The five count-guard sites null-test the element they load; only the three selectors do not. Added `COUNT_GUARD_NULL_TESTS`, a `null_test_site` report field, and doc corrections in sections 4, 5, 8.3, 13.4 | B-B3 | CLOSED |
| K10 | The bytes after the state table are not zero; the table's used range is `0..24`. Documented and pinned by a test | B-B4 | CLOSED |
| K11 | Selector histogram corrected to 161 constants with `1:8`; a `selector_argument_census` report and a test were added so the figure is covered | B-B6 | CLOSED |
| K12 | `+0x10..+0x4F` column ranges now state their population (all four records versus record 0) | B-N1 | CLOSED |
| K13 | The fourth state-table path `0x0800EEB6` (predicate, via literal `0x080725F0` + 0x80) added to the probe, the document and a literal-site test | B-N2 | CLOSED |
| K14 | "No object carries an index at or above its own count" removed as evidence; replaced with the extent arithmetic, the five guards, index-0 universality and the nonzero word at `+0x54 + 4*count` | B-N4 | CLOSED |
| K15 | Index 7's additional role documented (both bodies then select index 7 and call `0x0800ED18`) | B-N5 | CLOSED |
| K16 | Section 13.1 title corrected from "two objects" to "the run's first boundary is another object's tail" | B-N6 | CLOSED |
| K17 | Section 14.7 answered: definitions 146 and 163 reach only rejected animations; the fourth is reached by definition 47 | B-N7 | CLOSED |
| K18 | Probe JSON keys renamed: `slots`/`non_null_slots`/`null_slots`/`malformed_slots`, `frame_slots_over_unique_animations`, `max_value` vs `largest_state`, `bytes_after_table_hex` | B-N8 | CLOSED |
| K19 | Circular guard-offset and `pointer_for` expectations replaced with literal data | B-C1, B-C2 | CLOSED |
| K20 | Extent, determinism and state-table tests strengthened, and coverage added for the selector histogram, the trailer histograms, the state-table tail bytes and the pair/boundary populations | B-C3..C6 | CLOSED |
| K21 | Section 10.1 now records that the recommended correction is a numerical no-op for the accepted corpus | B (§10) | CLOSED |
| K22 | The trailer-1 residue breakdown corrected to **16** other values (three small plus thirteen large), matching `21 - 5 = 16` | A-D2, B-NEW-1 | CLOSED |
| K23 | The `+0x19` sixteen-byte quote corrected to end in `FF`, and the eight `0xFF` bytes located at `+0x28..+0x2F` | A-D1, B-NEW-2 | CLOSED |
| K24 | The committed 24-byte state-table tail string replaced by property assertions on the tail (index 32 holds `1`, eight `0xFF` bytes start at index 40, the rest zero), so `tests/integration/test_logx_sprite_rom.py` carries no ROM byte dump | A-N5, B-NEW-5 | CLOSED |
| K25 | Section 3.2 reworded: the constructor does not read `+0x00` and does not read the `+0x08` word's first byte, while it does read that word's `+0x0A`/`+0x0B` bytes listed in the table below | A (delta), B-NEW-4 | CLOSED |
| K26 | Section 12.2's unguarded-pattern count now states its window and its window-dependence (34 at 30 instructions, 19..35 across 2..60) instead of quoting a bare figure | A-D3, B-NEW-3 | CLOSED |
| K27 | The reviewer blocks in this document were made faithful: the implementer's closure annotations are marked as such, and Reviewer A's verdict and PASS lines are restored to the reviewer's own words | A-D4 | CLOSED |
| K28 | Probe dead code removed (`_ldr_pool`, the two unused predicate constants) | B-NEW-7 | CLOSED |
| K29 | Section 12.2's illustrative window counts removed entirely: Reviewer B could not reproduce 34/35 under any natural rule variant, and the section's conclusion does not rest on a count, so the scan is now described by its rule and its window with no figure claimed | B (final, item 3) | CLOSED |

## REJECTED REVIEWER ASSERTIONS

None. Every finding raised by either reviewer reproduced from the canonical image
in this session and was applied. Two reviewer observations were **superseded
rather than rejected** and are recorded so the record is complete:

1. **Reviewer A's N1 arithmetic ("231 exact + 65 short = 296") is right; the
   implementer's original "232 of 296" was the wrong population.** Reviewer A
   also noted that the 232nd agreement is the last object measured against the
   array start, which is what the probe's key measures; both readings are now
   reported under names that cannot be confused.
2. **Reviewer B's B6 (159 -> 161 constants) was already applied when it
   reported**, because the implementer had independently widened the lookback
   window. Reviewer B's independently measured histogram agrees exactly with the
   committed one.
3. **Reviewer B's B3 address convention was corrected by Reviewer B itself.**
   B's first report cited the null-test *branch* addresses; the commit uses the
   `cmp` addresses, which B's delta confirms are the right ones.
4. **Reviewer A's N5 and Reviewer B's B5 were the same class and are the only
   partial closures recorded here.** The 308 bytes of `DEFINITION_*_RAW` were
   removed; a 24-byte state-table tail string survived the first pass and was
   replaced by property assertions in K24, after which both reviewers' residuals
   are closed.

## CORRECTION GATE

**CLOSED.** 29 corrections across the two reviewers' 21 first-round findings, 7
delta-round findings and 1 final round finding were reproduced and applied; none
was rejected. Reviewer A's final verdict on `e3de67b` was APPROVE WITH
NON-BLOCKING NOTES; Reviewer B's final verdict moved from REQUEST CHANGES on
`bccd03c` and `e3de67b` to **APPROVE** on `1a3eb70`. Measured on the final
committed revision:

```text
pytest tests/integration/test_logx_sprite_rom.py tests/unit/test_logx_sprite_reference.py -q
-> 65 passed

the same with LOGX_CANONICAL_ROM pointed at a non-existent file
-> 40 passed, 23 skipped, every skip "canonical Buu ROM not configured locally"

python -m tools.research.logx_sprite_probe <rom> [--run|--engine|--rows]
-> exit 0 in all four modes
```

No correction changed a load-bearing claim: the run's start, count, terminator
and first-entry resolution, the folded base's meaning, the count's five guarded
reads, the inline array's extent and occupancy, the animation and frame layouts,
the selection mechanism and the state table all reproduce from the ROM exactly as
first reported. What changed is the *populations* of two counts, two histograms,
four over-broad or wrong sentences, the state table's tail, one missing reader,
the committed byte fixtures, and the test suite's independence from the probe's
own expressions.

## GIT STATUS

Staged explicitly by path before the correction commit:

```text
 M docs/research/LOGX_SPRITE_PROVENANCE.md
 M docs/reverse-engineering.md
 A docs/research/LOGX-SPRITE-001-review.md
 M tests/integration/test_logx_sprite_rom.py
 M tests/unit/test_logx_sprite_reference.py
 M tools/research/logx_sprite_probe.py
```

Verification performed against that index before committing:

```text
git diff --cached --check     -> exit 0, no output
staged paths matching a proprietary extension (.gba/.sav/.srm/.ss?/.state/.bin/.dump/.raw/.png) -> none
canonical ROM SHA-256         -> 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E (unchanged)
```

`docs/PROJECT_<local-state-name>`, `docs/PROJECT_<local-state-name>`, `src/data/project.ts` and the
active WORKBENCH-006 worktree were **not** touched during the isolated research
pass, the branch was not pushed, and the ticket was not integrated or archived at
that point.
