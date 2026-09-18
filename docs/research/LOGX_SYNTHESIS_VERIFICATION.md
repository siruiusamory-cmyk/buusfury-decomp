# LOGX-SYNTHESIS-001 - Consolidate LOGExtractor research into canonical schemas and an implementation roadmap

Research and synthesis only. No production code, GUI, Workbench, renderer,
authoring surface, `PROJECT_<local-state-name>` or canonical ROM was modified. Ten accepted
tickets were synthesized; the LOGExtractor research freeze ends here.

---

## 1. Identity

| | |
| --- | --- |
| **START SHA** | `64fa98626065cf49c631878c53e1c8e1073a3bd6` |
| **END SHA** | `271b26d532706cdc0731b3bf348589e479f299af` |
| **BRANCH** | `logx-synthesis-001` (isolated worktree `<temp>\log1-remake-logx-synthesis-001`) |
| **COMMIT SHA(S)** | `f6a6bc7` `research(synthesis): consolidate LOGX archaeology` (the synthesis, and the revision both reviewers measured)<br>`4722866` `research(synthesis): correct recall arithmetic and record project-state baseline` (self-check)<br>`b80d098` `research(synthesis): close independent review corrections`<br>`ad217c3` `docs(synthesis): record the LOGX-SYNTHESIS-001 result`<br>`271b26d` `docs(tickets): record the final LOGX-SYNTHESIS-001 revision` (this record's SHA lines; the END SHA) |
| **CANONICAL ROM SHA BEFORE** | `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E` |
| **CANONICAL ROM SHA AFTER** | `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E` |

The canonical image was opened **read-only** for every measurement; no write
path exists in any instrument used. No ROM, save, state, dump, derived ROM,
decoded payload, generated asset or `extern/` checkout is staged or untracked.
Not integrated to `master`.

---

## 2. Deliverables

| Artefact | Purpose |
| --- | --- |
| [`../research/LOGX_SYNTHESIS.md`](../research/LOGX_SYNTHESIS.md) | the authoritative synthesis: canonical resource graph, per-system schemas, the 39 refuted LOGExtractor assumptions, read-support and authoring-readiness matrices, `AUTHOR_NEW` gap analysis, freeze conclusion |
| [`../research/POST_LOGX_IMPLEMENTATION_ROADMAP.md`](../research/POST_LOGX_IMPLEMENTATION_ROADMAP.md) | the implementation queue in five phases, with the recommended first ticket |
| [`../research/LOGX_SYNTHESIS_PROVENANCE.md`](../research/LOGX_SYNTHESIS_PROVENANCE.md) | this ticket's own audit method, the ROM Bible corrections, and the bounded residual investigation |
| `tools/research/logx_synthesis_audit.py` | deterministic, ROM-free, read-only audit: canonical record presence, fact-table consistency, vocabulary discipline, superseded-assumption scan |
| `tests/unit/test_logx_synthesis_audit.py` | 23 portable tests pinning those invariants |
| corrected `docs/reverse-engineering.md` | ten accepted-evidence corrections |
| corrected `docs/research/GRAPHICS_FORMAT.md` | superseded-statements banner plus the `0x179764` ownership and piece-row corrections |
| corrected `docs/PROJECT_<local-state-name>`, `docs/PROJECT_<local-state-name>` | newest baseline entry and a stale `## Next` block |

---

## 3. TICKETS SYNTHESIZED

**10 / 10** - `LOGX-MAP-RECORD-001`, `LOGX-MAP-RENDER-001`, `LOGX-LAYER-001`,
`LOGX-TILE-001`, `LOGX-CONNECTOR-001`, `LOGX-CODEC-001`, `LOGX-CHAR-001`,
`LOGX-SPRITE-001`, `LOGX-FRAME-001`, `LOGX-GFXSCAN-001`. Each was read through
its own accepted review record, closeout record and provenance document; nothing
was synthesized from the ticket prompts or from memory.

---

## 4. CANONICAL RESOURCE GRAPH

`docs/research/LOGX_SYNTHESIS.md` §2. Five subsystems, each with its confirmed
links and its explicitly partial ones:

```text
MAP SIDE        MapEntry (452 x 0x38, 0x0808E2E0)
                  -> selector route 0x080089CC = word[selector-1] over +0x2C
                  -> selector-1 load-time template (452 non-null, 421 distinct)
                  -> four layer records (1808 refs / 1464 unique) + +0x24/+0x28,
                     +0x34/+0x38, +0x3C, +0x48, +0x4C
                  -> Webfoot containers -> 32x32x1024 u16 chunk payloads
                  -> selector stream (bank, tile) pairs -> 187-bank table at 0x08179764

CONNECTION SIDE root +0x40/+0x44 (one ldm) -> 735 transition records (24 bytes)
                  -> destination key at +0x11/+0x12 (TWO BYTES) -> MapEntry lookup
                  -> 694 directed links

CHARACTER SIDE  0x0874D380, 232 x 0x10 appearance definitions
                  -> +0x00/+0x02 text indices, +0x04 sprite-definition index,
                     +0x08 portrait pointer, +0x0C signed stat index

SPRITE SIDE     0x086B6BDC, 297-entry pointer run (ids 10..306)
                  -> variable-length definition (+0x00 count, +0x54 inline array)
                  -> animation object (u32 frame_count, 4 cells per frame)
                  -> frame record (8-byte header, 12-byte pieces)
                  -> piece (+0x04 attribute pair, +0x08 graphics container)

CODEC SIDE      wrapper {0 stored | 1,2 packed} + declared size at +0x04
                  -> dispatcher 0x0803D940 -> packed decoder (IWRAM 0x03000040)
                  -> decoded resource
```

Confirmed links are stated as confirmed; `PARTIAL`/`UNRESOLVED` links are marked
inline and repeated in §12.

---

## 5. STATUS BY SYSTEM

| System | Status |
| --- | --- |
| **MAP SCHEMA STATUS** | table `CONFIRMED` (452 x `0x38`, no terminator); `+0x00` is **two ordered key bytes** with the semantic identity `UNRESOLVED`; `+0x0C`'s text-table relationship `CONFIRMED` with purpose `UNRESOLVED`; `+0x2C` `CONFIRMED` as an indexed-word source. The root is a **load-time definition template** (`CONFIRMED`), with `+0x0C`/`+0x10`'s reading instruction unrecovered and `+0x30`/`+0x50..+0x5C` `UNRESOLVED` |
| **LAYER/TILE STATUS** | dominant handler `0x08008087` **only**: `+0x00` is a Thumb handler entry (not a type tag, not a layout discriminator), `+0x14`/`+0x15` are separate grid bytes, `+0x18` is a 4-byte-element container window. Chunk = 1024 LE u16, 32x32, 8x8-pixel tiles, 256x256 pixels. Bits 0-9 tile ordinal `CONFIRMED`; bits 10/11 stored but direction `PARTIALLY CONFIRMED`; **bits 12-15 reserved/constant, not "unused"**. Layer position `UNRESOLVED` |
| **CONNECTION STATUS** | `+0x40`/`+0x44` consumer, walk, 24-byte record layout and the **two-byte destination** `CONFIRMED`, 735/735 resolving. Geometry axis/origin/units/signedness/inclusivity, spawn/facing, the two record classes and LOGExtractor's `+8` all `UNRESOLVED` |
| **CODEC STATUS** | wrapper and dispatcher `CONFIRMED` (forms {0,1,2}, `+0x04` declared size, `+0x08` payload, no destination capacity); packed grammar `CONFIRMED` against 4,322/4,322 containers; identity **JCALG1-like/derived, not promoted**; `UnknownHeader` and the 64 KiB limit `REFUTED`. Project decoder **CORRECT WITH LIMITED FIXES REQUIRED**; encoder **PARTIAL** |
| **APPEARANCE STATUS** | 232 x `0x10` `CONFIRMED`; `+0x00`/`+0x02` text relationships `CONFIRMED`, higher-level name/description semantics `PARTIALLY CONFIRMED`; `+0x04` sprite path and `+0x08` portrait relationship `CONFIRMED`; `+0x0C` is one signed index into `0x08711274` at `0x1C` stride with high-level meaning `UNRESOLVED`. Canonical wording: **named appearance definitions with optional slot and stat indices** |
| **SPRITE STATUS** | run `0x086B6BDC`, 297 entries, ids 10..306, ids 0..9 party aliases `CONFIRMED`; `0x086B6BB4` resolved as definition 306's inline array; `+0x00` **count-bounded**, `+0x54` variable-length sparse array (4,070 slots / 1,721 non-null) `CONFIRMED`; **fixed 23-slot model `REFUTED`**; slot names mostly `UNRESOLVED` |
| **FRAME STATUS** | animation `u32 frame_count` + `4*frame_count` cells at `animation + 0x04 + 16*frame + 4*direction` `CONFIRMED`; **8-byte frame header, 12-byte pieces** `CONFIRMED` (11,005 pieces / 10,980 frames / 21 multipart); piece `+0x04` attribute pair and `+0x08` graphics word `CONFIRMED`; direction order, piece origin and the two trailer words `UNRESOLVED` |
| **GRAPHICS DISCOVERY STATUS** | shipping discovery tool **NO**, forensic/research tool **YES**, canonical enumerator **NO**; 100% sprite recall, 98.3% all-class; stored-form and `declared % 4 == 0` blind spots preserved; **no graphics semantic claimed for the 387 residuals** |

---

## 6. READ-SCHEMA MATRIX

`docs/research/LOGX_SYNTHESIS.md` §14 - 15 resource classes with discovery root,
structure confidence, field confidence, read support (`TRUSTED` /
`TRUSTED WITH KNOWN FIX` / `PARTIAL` / `RESEARCH ONLY`), current implementation,
known bugs, authoring readiness and follow-up. Added: **four of the fifteen
classes have no project implementation at all** (connection records, appearance
definitions, portrait lookup, and the animation/frame/piece chain outside
`graphics.py`) - an engineering gap, not a research one.

## 7. AUTHORING-READINESS MATRIX

`docs/research/LOGX_SYNTHESIS.md` §15 - 19 capabilities classified
`SAFE NOW` / `SAFE AFTER BOUNDED FIX` / `PARTIAL RESEARCH REQUIRED` /
`BLOCKED BY UNKNOWN SEMANTICS`, each with the writing requirements that remain
(allocation, bounds, relocation, count updates, encoding, runtime invariants).
Every `TRUSTED WITH KNOWN FIX` read row names an enumerated defect in §11; a row
whose known gap is an unrecovered *consumer* is rated `TRUSTED` with the gap in
its field-confidence column.

## 8. RANDOMIZER READINESS

- **Structural randomization: READY AFTER `TOOLS-3` + `TOOLS-4`.** Exactly two
  bytes change (`+0x11`/`+0x12`); the other 22 bytes of the record, the root's
  coupled count/pointer pair and the record count are untouched; every new pair
  must resolve through `0x080089FC`.
- **Reciprocity:** preservable, but it is a **measured property, not an engine
  invariant** (674 of 694 links; 20 non-reciprocal; 3 self). The tool must state
  its policy; silence is not acceptable.
- **Gameplay-logic / softlock validation: a separate, later problem** owned by
  progression logic, not by this research line. Ship the randomizer as a
  structural tool that refuses unresolvable keys and never claims solvability.

## 9. AUTHOR_NEW STATUS

`docs/research/LOGX_SYNTHESIS.md` §18. Two research-class blockers only: the
**appearance table's reloadable-count question** (now §12 #29 / §13 #29, and the
reason `NEW-3` is `research + engineering`) and **arbitrary new-warp trigger
authoring** (`NEW-4`, gated by `LOGX-CONNECTOR-GEOMETRY-001`). Everything else is
`IMPLEMENTATION ONLY`, `STRUCTURALLY SOLVED` or `PARTIAL` engineering.

---

## 10. RESEARCH GAPS

| # | Gap | Blocks |
| --- | --- | --- |
| 1 | connector interval axis/origin/units/signedness/edge inclusivity and the region-membership test | arbitrary new trigger authoring only |
| 2 | connector spawn / arrival position, facing | `NEW-4` |
| 3 | the two connector record classes; `+0x10`/`+0x13`/`+0x14`/`+0x16`/`+0x17` semantics | nothing current |
| 4 | the consumer entry path `0x080071F8`; LOGExtractor's `+8` | forensic |
| 5 | selector values other than `1` and what chooses them | nothing current |
| 6 | the instruction reading `root+0x0C`/`+0x10` | nothing current |
| 7 | tile bits 10/11 direction; bits 12-15 role | forensic |
| 8 | layer positioning; the other handler classes; internal-null meaning | advanced authoring |
| 9 | animation trailer words; loop/terminal behaviour | new-animation authoring |
| 10 | direction screen orientation; piece position origin | advanced authoring |
| 11 | sprite-definition `+0x08`/`+0x0C`/`+0x10..+0x4F`; `+0x50` array; state mapping; slot names | new-definition authoring |
| 12 | appearance `+0x0C` target meaning; `f(0x92)`/`f(0x95)`; roster activation; variant families | new-appearance authoring |
| 13 | the decoder's initial literal width; the marker-vs-size rule; exact JCALG1 identity | the encoder |
| 14 | **is the appearance table's count of 232 reloadable?** | `NEW-3` |
| 15 | the 387 residuals' consumer; portrait recall and pixel format | nothing current / portrait import |

## 11. ENGINEERING GAPS

Parser corrections (`FIX-1`..`FIX-4`), the stale-figure sweep (`FIX-5`), the
metadata writer (`FIX-6`), the four missing readers (`TOOLS-1`, `TOOLS-3`), the
multipart preview (`TOOLS-2`), the randomizer (`TOOLS-4`), in-place replacement
(`TOOLS-5`), the stored writer and packed encoder (`WRITE-1`, `WRITE-2`),
allocator integration (`WRITE-3`), graphics insertion (`WRITE-4`), and all five
`AUTHOR_NEW` tickets. **No engineering gap is described as a research blocker and
no research gap as implementation-only.**

---

## 12. PRODUCTION DEFECTS AND STALE ASSUMPTIONS

| # | Defect | Class | Owner |
| --- | --- | --- | --- |
| 1 | `webfoot_lz` does not enforce exact declared-size completion; an over-long final match is clipped and reported as success | `PRODUCTION BUG` | `FIX-1` |
| 2 | `graphics.py::_animations_in` walks from `+0x54` to the next structure and ignores the definition `+0x00` count (8,230 slots scanned vs 4,070) | `PRODUCTION BUG`, numerically inert today | `FIX-3` |
| 3 | `sprite_graphics.py` models the refuted 4+16 frame/piece record: `PIECE_SIZE = 16`, a 4-byte header, attributes at `+0x08`, graphics at `+0x0C` | `PRODUCTION BUG` | `FIX-2` |
| 4 | `graphics.py` composes a graphics reference at `frame_offset + 4 + 0x0C` | latent `PRODUCTION BUG` (coincidentally correct for piece 0 only) | `FIX-4` |
| 5 | the `7,355` single-piece subset presented as the corpus total across shipping docstrings, CLI help, profile evidence and four documents | `STALE DOCUMENTATION` | `FIX-5` |
| 6 | `atlas_producers/scan.py::_compression_rows` is a stride-4 noise sweep (24,285 hits / 68.7 MiB) | `PRODUCTION BUG` (output quality), outside the canonical path | parked with a disposition in §11.6 |
| 7 | tests that pin the refuted layout (`UNIQUE_GRAPHICS = 7355`; `FRAME_FIRST_PIECE == 0x04`; 16-byte piece fixtures; 4-byte-header frame fixtures) | `TEST EXPECTATION` | §11.5; re-pointed by `FIX-2` |

The repository-wide audit found **28 surviving superseded-string hits**, 5 of them
in live code, and **every one is a recorded defect above**. Four of the fourteen
refuted patterns have **zero** surviving occurrences anywhere; five more survive
only as quoted external claims or explicit refutations. The audit's own bypasses
that an independent review demonstrated - a case-sensitive address regex, an
over-broad historical-marker filter, a document-wide banner exemption, and globs
that missed `THIRD-PARTY-NOTICES.md`, `config/roms.yaml` and three documents -
were all reproduced and fixed, and are now pinned by tests.

---

## 13. 387 REFERENCED RESIDUAL RESULT

```text
CLASSIFICATION:  UNCLASSIFIED - needs a targeted ticket (parked, not recommended)
  6   / 387  ALREADY-KNOWN FAMILY `compressed_text`
  177 / 387  two size-locked pointer tables (155 x 4,096 at 0x086F395C,
             140 x 1,024 at 0x082ABF08), structure CONFIRMED, consumer UNKNOWN
  204 / 387  cited only by short runs or isolated words
```

The `0x087B5B64` lead is **answered by pre-existing records**: it is exactly
7 word-aligned form-1 pointers (28 bytes) pointing directly at container headers,
and it is the **`compressed_text` selector table** already documented as
`compressed_text.pointer_table` (`tools/webfoot/atlas_producers/seed.py:686-704`,
"STRUCTURAL GATE: exactly 7 containers") with consumer literal `0x080123CC`.
The size distribution was re-measured and **corroborates LOGX-GFXSCAN-001
exactly** (129 x 256, 26 >= 8 KiB, median 1,024, max 65,474). One new
discriminator: 381 of 387 decoded lengths are divisible by 32, and **the 6
exceptions are exactly the 6 `compressed_text` members**. **No graphics semantic
and no new resource class is claimed.** Recommendation: `LOGX-RESTABLE-001`,
parked because it names no blocked capability.

## 14. PORTRAIT COVERAGE DECISION

**`PORTRAIT GFXSCAN RECALL: UNMEASURED / NON-BLOCKING.`** The pointer path is
structurally sufficient for the roadmap (`+0x08` -> `0x086F393C` -> container
dispatcher), recall measures the *scanner* rather than the engine, and the
question that would matter - pixel format and dimensions - is a different,
`UNRESOLVED` question that this ticket is forbidden to pursue. Recorded as a
known limitation; `LOGX-PORTRAIT-FORMAT-001` is conditional on portrait import.

## 15. AUDITS

| Audit | Result |
| --- | --- |
| **ROM BIBLE AUDIT** (`docs/reverse-engineering.md`) | **UPDATED.** Ten corrections: the `0x0803D966` caller and `r2` role; the decoder blob base **CONFIRMED** from the startup DMA3 literals with the library-table reading withdrawn; `0x08070808`'s `0x7F8` trailing zeros; the withdrawn `0x0801AF96` direction claim; the animation-trailer caveat (30 of 1,017); the 7,355/7,390 reconciliation; MapEntry `+0x00`/`+0x0C` accepted key and text semantics; a ROM-003/ROM-004 superseded note; the ROM-007/ROM-008 "rectangle" demotion; and a new **LOGX-GFXSCAN-001** section. Also restored a malformed MapEntry table row. Verified clean: address notation, widths, signedness, pointer-vs-index semantics, the two-byte destination, layer `+0x00`, the container model and every population total |
| **GRAPHICS_FORMAT AUDIT** | **UPDATED.** A `SUPERSEDED STATEMENTS` banner names every claim LOGX-SPRITE-001/LOGX-FRAME-001 refuted or offset-corrected (4+16 frame record; attribute/graphics offsets; "all frames single-piece"; 7,355 as the total; 13,596 vs 13,660; the unbounded animation walk; the 23-slot model) and states that **where a figure disagrees with the banner the banner wins**. The `0x179764` ownership passage and the "16 bytes exact" row were corrected, and the two production defects are cross-referenced. Historical correction notes are preserved |
| **REPOSITORY-WIDE STALE-ASSUMPTION AUDIT** | **28 hits, 5 in live code, none unrecorded.** Zero hits for four refuted patterns (64 KiB limit; zero-first-word-means-empty; layer `+0x00` as a numeric type; big-endian `u16` destination). Instrument hardened against all four bypasses the review demonstrated |

---

## 16. IMPLEMENTATION ROADMAP

`docs/research/POST_LOGX_IMPLEMENTATION_ROADMAP.md` - five phases (correctness
and parser repair; verified existing-content tools; resource writing and
allocation; `AUTHOR_NEW`; advanced/forensic, not scheduled), 18 proposed tickets,
each with goal, dependencies, subsystem, kind, acceptance, risk, `AUTHOR_NEW`
impact and public visibility. A randomized-warp readiness assessment and a
separate gameplay-logic/softlock note are included.

## 17. RECOMMENDED FIRST IMPLEMENTATION TICKET

**`FIX-1` - strict decoded-size enforcement in `webfoot_lz`.** Smallest change in
the roadmap, no research dependency, the failure mode it removes is the most
damaging one available (a silently truncated payload reported as success), and it
is already pinned by a reproducible test. `FIX-2` + `FIX-3` follow as one window;
`FIX-1` is first because a wrong decoder can corrupt a payload that a correct
parser then faithfully reports as valid.

## 18. TARGETED FUTURE RESEARCH TICKETS

| Ticket | Priority |
| --- | --- |
| `LOGX-CODEC-WRITE-001` | **high** - the gate for every insertion capability |
| `LOGX-CONNECTOR-GEOMETRY-001` | only when trigger authoring is scheduled |
| `LOGX-PORTRAIT-FORMAT-001` | only when portrait import is scheduled |
| `LOGX-RESTABLE-001` | **parked** - names no blocked capability |

## 19. RESEARCH FREEZE

**CAN END.** Every question the near roadmap needs is answered; the unanswered
ones are enumerated, classified and separated into research and engineering; the
remaining research items are bounded, with one dedicated ticket each and a named
blocked capability. Six of `AUTHOR_NEW`'s twelve dependencies are
`IMPLEMENTATION ONLY`, `STRUCTURALLY SOLVED` or structurally solved for their
stored form; only the appearance-count question, map data, new connections and
compression encoding need research or a decision.

## 20. public progress impact

**NONE.** No public SDK capability, frontier, questline or product story changed:
this ticket adds research documents, an audit instrument and its tests, and
documentation corrections. `src/data/project.ts` is untouched and no site edit is
made. The "research freeze completed" milestone is an internal project event, not
an outside-usable capability, so under the project's own convention it does not
qualify as a public milestone. Actual public updating, if any, is left to
post-acceptance closeout.

---

## 21. TOOLING ADDED

- `tools/research/logx_synthesis_audit.py` - deterministic, read-only, ROM-free,
  no optional dependency. Three checks (canonical record presence; synthesis
  fact-table and vocabulary consistency; superseded-assumption scan) with a
  documented scope, a conditional `GRAPHICS_FORMAT.md` banner exemption that is
  key-scoped, and a deliberately narrow historical-marker filter.
- `python -m tools.research.logx_synthesis_audit` reports 28 superseded hits
  (5 in live code) and exits 1 while findings remain.

## 22. TESTS ADDED

- `tests/unit/test_logx_synthesis_audit.py` - **23 portable tests**: the ten
  tickets' canonical records; the fact table in both directions; vocabulary
  discipline including the `PARTIAL` / `PARTIAL RESEARCH REQUIRED` collision; the
  roadmap's phase structure; the recorded-defect set; and four **adversarial**
  tests that plant a lowercase address, a hedging comment on a defect line, a new
  stale claim inside the banner-exempt document, and a stale hit inside an
  already-listed file, each of which must still be reported.

## 23. TEST RESULTS

All measured on this worktree. The canonical image was supplied only through
`LOGX_CANONICAL_ROM`; no local `roms/` junction was left in place (a junction
temporarily created to run the graphics suite was removed, and
`test_project_safety.py` was re-run afterwards to prove it).

| Suite | Result |
| --- | --- |
| `tests/unit` (whole portable suite) | **1516 passed, 16 skipped** |
| `tests/unit/test_logx_synthesis_audit.py` | **23 passed** |
| `python -m tools.research.logx_synthesis_audit` | **28 findings**, 5 live-code, all recorded; exit 1 |
| LOGX ROM-gated integration (all ten suites) | **241 passed** (`111` + `130`) |
| `tests/integration/test_graphics_rom.py` + `test_graphics_override_build_rom.py` + `tests/unit/test_sprite_graphics.py` (with a `roms/` junction) | **73 passed** |
| `tests/unit/test_project_safety.py` + `test_rom_safety.py` + `test_code_review_workflow.py` + `test_workflow_migration.py` + the synthesis audit tests | **49 passed** |
| ROM-absent behaviour (`LOGX_CANONICAL_ROM` pointed at a missing file) | **20 passed, 49 skipped, 0 failed** |
| `git diff --check` | clean (exit 0) |
| canonical ROM SHA-256 | `940AD5F0...F059E`, unchanged |

**Junction evidence.** With a temporary `roms/` junction present,
`test_project_safety.py::test_proprietary_and_generated_paths_are_git_ignored`
failed with `fatal: pathspec 'roms/safety-probe.gba' is beyond a symbolic link`;
after removing it, the file reports **5 passed**. That reproduces LOGX-CHAR-001's
recorded environment fact rather than working around it.

**Not run:** the full 15-minute repository suite. This ticket changes
documentation, one research module, one portable test file and no production
code, so the blast radius is bounded by the LOGX suites, `tests/unit`, and the
graphics/safety/workflow files - all run above. If the scope ever grows into
production code, the suite gate applies.

---

## 24. INDEPENDENT REVIEW

Two fresh-context reviewers, neither of whom wrote any part of the ticket, both
measured against the **frozen revision `f6a6bc7`** using `git show f6a6bc7:<path>`
so the working tree's later commits could not contaminate their evidence. Both
were told to re-derive claims rather than read them, to report `SURVIVES` for
attacks that failed, and not to manufacture findings.

### REVIEWER A - architecture / cross-ticket consistency / engine-schema

**Verdict: REQUEST CHANGES** (3 BLOCKING, 9 NON-BLOCKING, 4 NIT). It re-derived
more than 40 `CONFIRMED` claims and every §3.6 population total with its own
scripts against the canonical ROM and found them correct, reproduced the whole
387-residual investigation exactly (5,479 residuals; 414 referenced; the 7-word
table; tables A and B and their sizes; the single citing word `0x080123CC`; the
size profile; the 6-exception set), and confirmed **no promoted hypothesis, no
read-presented-as-write, no mislabeled gap** beyond the items listed.

| # | Severity | Finding | Resolution |
| --- | --- | --- | --- |
| A-B1 | BLOCKING | `11515 = 11513 + 202` contradicts the document's own 11,715 corpus | **Reproduced.** It is a typo. Corrected to `11715 = 11513 + 202` in `4722866` |
| A-B2 | BLOCKING | the audit instrument was reported as "exit 0, zero findings" but exits 1 with 20 findings, 5 in live code; the related test description was inverted | **Reproduced.** Provenance now reports the real result; the description now says no **unrecorded** hit survives, and that the recorded defects must remain until their fixes land |
| A-B3 | BLOCKING | `docs/reverse-engineering.md`'s MapEntry table had the `0x01` and `0x02` rows merged, corrupting the table | **Reproduced.** The newline is restored |
| A-N1 | NON-BLOCKING | the appearance count is baked into **three** `cmp rN,#0xE8` bounds, not "eight" (eight is the base-load/`index << 4` site count) | Corrected in the synthesis and the roadmap |
| A-N2 | NON-BLOCKING | `LOGX-RESTABLE-001` was "recommended" while its own Blocks cell said "nothing currently planned", violating the Vertical-Slice-First Rule and §17's own preamble | **Reproduced.** Moved to a **Parked, not recommended** paragraph; the roadmap says the same; §19's count corrected |
| A-N3 | NON-BLOCKING | the published link-graph triple is not disjoint: the probe's `reciprocal` excludes self-links while `one_way` includes them, so 674 + 20 + 3 = 697 ≠ 694 | **Reproduced.** The synthesis and roadmap now state the definitions, that 674 + 20 = 694 closes the total, and that the disjoint reading is 674 non-self reciprocal + 17 non-self one-way + 3 self |
| A-N4 | NON-BLOCKING | 4,118 vs 3,912 was explained as "different units"; it is the same unit over different populations (4,118 over 452 MapEntries, 3,920 over the 421 distinct roots) leaving 8 unexplained | **Reproduced.** The text now states the population difference, the 198 explained, and the 8 unexplained - reported, not harmonised |
| A-N5 | NON-BLOCKING | in-place container replacement omitted the `packed_end - offset` encoded-length constraint, making a Phase-2 ticket depend on the `PARTIAL` encoder | **Reproduced.** Added to both affected §15 rows and reflected in `TOOLS-5` |
| A-N6 | NON-BLOCKING | §11, the "authoritative" inventory, omitted the `TEST EXPECTATION` class and four `STALE DOCUMENTATION` files its own provenance reports | **Reproduced.** New §11.5 tables the three test files; §11.4 now lists `config/roms.yaml`, `THIRD-PARTY-NOTICES.md`, `docs/architecture.md`, `docs/project-format.md` and `SUBSYSTEM_MAP.md` |
| A-N7 | NON-BLOCKING | §14's authoring column used read-support tokens, and packed emission was rated two different ways in §14 and §15 | **Reproduced.** Plain `TRUSTED` where the gap is an unrecovered consumer; the emission classification reconciled |
| A-N8 | NON-BLOCKING | the appearance-table growth question is a genuine research unknown but appeared in neither §12 nor §13 | **Reproduced.** Added as §12 #29 and §13 #29 |
| A-N9 | NON-BLOCKING | "warp" was adopted as a class name though the owning closeout assigns no such name | **Reproduced.** A naming note now uses **transition record / destination key** and records "connector"/"warp"/"door"/"exit" as community labels; the roadmap's ticket names keep the community word with that caveat |
| A-T1 | NIT | the `0x080089FC` byte-wise lookup evidence was attributed to LOGX-MAP-RECORD-001 | Corrected to LOGX-CONNECTOR-001, with the key *shape* left with MAP-RECORD |
| A-T2 | NIT | "Six of the twelve rows are `IMPLEMENTATION ONLY`, `STRUCTURALLY SOLVED` or `SOLVED`" does not reproduce | Rewritten with the actual rows named |
| A-T3 | NIT | "Every entry is `REFUTED`" is false for rows 21, 23 and 27 | Rewritten to distinguish narrowed readings from refutations |
| A-T4 | NIT | the audit instrument's enforcement is narrower than its description | **Reproduced in substance** and answered: the scope, the exemption and the marker filter are now documented as limits, the bypasses are fixed, and four adversarial tests pin them |

### REVIEWER B - adversarial / implementation-readiness / stale-assumption

**Verdict: REQUEST CHANGES** (2 BLOCKING, 14 other findings). It attempted to
falsify the headline claims and reported which attacks **survived**: the
7,355/7,390 subset relation, the whole sprite/frame census, the codec and
connector populations, `FIX-1`'s pinned clipping case, the test-expectation
drift, and the 387-residual pointer structures all reproduced independently.
It also confirmed **`PROMOTED HYPOTHESES: NONE`** and **no scope violation**.

| # | Severity | Finding | Resolution |
| --- | --- | --- | --- |
| B-1 | BLOCKING | `THIRD-PARTY-NOTICES.md` presents 7,355 as the corpus total and was in no inventory, no roadmap list and no audit glob | **Reproduced.** Added to §11.4, `FIX-5`, `stale-7355`'s globs and the audit's scan scope; `config/roms.yaml` too |
| B-2 | BLOCKING | `atlas_producers/scan.py::_compression_rows` was recorded by LOGX-GFXSCAN-001 as a production follow-up and was absent from the synthesis entirely | **Reproduced** (24,285 hits / 68.7 MiB, "overwhelmingly probe noise"). Now §11.6 with an explicit disposition |
| B-3 | NON-BLOCKING | the audit result was misreported | Same fix as A-B2 |
| B-4 | NON-BLOCKING | "every `KNOWN FIX` is an enumerated production defect in §11" was false for the map-root and portrait rows | **Reproduced.** Both reclassified; the umbrella sentence rewritten |
| B-5 | NON-BLOCKING | `decode_animation`'s `maximum_frames = 64` was recorded by GFXSCAN as a defect and omitted | **Reproduced** and recorded as a **recorded disagreement, not a defect** (64 is a bound; the canonical `frame_count` range is 1..16) |
| B-6 | NON-BLOCKING | the `packed_end - offset` constraint was omitted from the tile rows | Fixed with A-N5 |
| B-7 | NON-BLOCKING | the `+0x50` parallel-array coupling was omitted from the animation-pointer row | Fixed: the row now states the pairing and forbids silent desynchronisation |
| B-8 | NON-BLOCKING | `NEW-3`'s acceptance could not be met under its own stopping point; `NEW-1`'s count update did not say where the +4 bytes go | Both rewritten |
| B-9 | NON-BLOCKING | §12/§13 omitted five fields §2-§9 mark `UNKNOWN`/`UNRESOLVED` | Added (tile bits 10/11, layer `+0x04`/`+0x08`, root `+0x24`/`+0x28` and `+0x34`/`+0x38`, root `+0x30`/`+0x50..+0x5C`), and §12/§13 renumbered |
| B-10 | NIT | "the largest canonical payload is 4 KiB" contradicted the 16 KiB and 65,474-byte figures | Corrected |
| B-11 | NIT | two §14 rows named files that do not exist | Corrected |
| B-12 | NIT | `FIX-4` blamed the wrong function for the `+4 + 0x0C` literal | Corrected |
| B-13 | NON-BLOCKING | audit-instrument bypasses (case-sensitive regex; over-broad markers; document-wide banner exemption; unreached globs; file-set-only test) | **All five reproduced and fixed**; four adversarial tests added |
| B-14 | NON-BLOCKING | `LOGX-CODEC-WRITE-001`'s initial-literal-width item is engineering with a documented workaround, not research | Accepted: §13 and §17 now say so and the workaround is stated |

### REQUIRED CORRECTIONS

**Five blocking corrections and every non-blocking finding were reproduced,
accepted and closed.** Every one changed a document, a scope constant or a test -
none required re-deriving a measurement, and none changed a `CONFIRMED` verdict.

### REJECTED REVIEWER ASSERTIONS

**None.** No finding was rejected on substance. One assertion was **partly
redirected**: Reviewer B's `decode_animation(maximum_frames=64)` item is accepted
as a finding about the *inventory*, but this synthesis declines to classify the
cap itself as a defect and records the disagreement with reasoning (B-5). Two
items were **upgraded rather than merely accepted**: the audit-instrument bypasses
became fixed code plus adversarial tests, and the `THIRD-PARTY-NOTICES.md`
omission widened the audit's scan scope.

### CORRECTION GATE

**CLOSED.** Both reviewers raised blocking findings against `f6a6bc7`; every one
was reproduced here before being applied, the corrections were re-validated
(`1516 passed / 16 skipped` on `tests/unit`, 241 LOGX ROM-gated tests, 73
graphics tests, 49 safety/workflow/audit tests, the audit instrument re-run, `git
diff --check` clean, canonical ROM unchanged), and the frozen end SHA `b80d098`
carries them. Reviewer A's own note that the working tree already fixed A-B1,
A-N1, the A-N5-adjacent wording and A-T4's substance is accurate and is recorded
rather than presented as review-driven work.

---

## 25. GIT STATUS

```text
branch   logx-synthesis-001   (isolated; NOT integrated to master)
worktree <temp>\log1-remake-logx-synthesis-001
commits  64fa986 (START) -> f6a6bc7 -> 4722866 -> b80d098 -> ad217c3 -> 271b26d (END,
         whose only change is the SHA lines in this record)
```

```text
 M docs/PROJECT_<local-state-name>
 M docs/PROJECT_<local-state-name>
 M docs/reverse-engineering.md
 M docs/research/GRAPHICS_FORMAT.md
 A docs/research/LOGX_SYNTHESIS.md
 A docs/research/LOGX_SYNTHESIS_PROVENANCE.md
 A docs/research/POST_LOGX_IMPLEMENTATION_ROADMAP.md
 A tests/unit/test_logx_synthesis_audit.py
 A tools/research/logx_synthesis_audit.py
```

Safety results:

| Check | Result |
| --- | --- |
| canonical ROM SHA-256 before / after | `940AD5F0...F059E` / identical |
| ROM writes | none; every instrument opens it through `Path.read_bytes` |
| `git diff --check` | clean |
| proprietary artefacts staged | none (no `.gba`, `.sav`, `.srm`, state, dump, `.raw`, `.png`, `extern/`) |
| scratch artefacts | all under the ignored `build/` tree, never staged |
| WORKBENCH-006 worktree | untouched |
| `docs/PROJECT_<local-state-name>` | untouched |
| GUI, Workbench, renderer, authoring and production code | untouched |
| commit attribution trailers | none |

## 26. STOPPING POINT

All ten accepted tickets synthesized; ROM Bible audited; graphics-format
documentation audited; stale project assumptions audited repository-wide;
read/write/authoring readiness classified; research and engineering gaps
separated; the 387-residual lead investigated, classified and parked;
implementation roadmap produced; a first implementation ticket recommended; four
targeted follow-up tickets proposed with only one considered genuinely necessary;
two independent fresh-context reviews completed against a frozen revision with
every required correction closed; committed on the isolated branch; canonical ROM
verified unchanged.

**Stopped here.** Not integrated to `master`. No implementation begun. The first
post-LOGX ticket is not started.
