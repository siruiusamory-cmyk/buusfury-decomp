# Friend v3 image: modification and TODO tracker

The single source of truth for everything done to, planned for, or cancelled from the
customized Buu's Fury image. The other `FRIEND_V3_*` records are the evidence this tracker
cites; none of them carries a competing TODO list. The playtest checklists are
`FRIEND_V3_PLAYTEST_GUIDE.md` (hack-specific, for speedruns) and
`FRIEND_V3_PLAYTEST_CHAPTERS.md` (chapter by chapter); the build of the current image is
`FRIEND_V3_PLAYTEST_BOOST.md`.

Reconciled 2026-10-10 against master `372bb3aafbc4305c460e11fc4a8b9436cd7565dd` (MR !176),
every friend record under `docs/research/`, the merged tests, the mission charter
`FRIEND-V3-PLAYTEST-001`, and the owner's recorded decisions. "Walkthrough" means the Tom
Hayes walkthrough, version 2.0, hosted at Gamer's Temple and cited in
`FRIEND_V3_PLAYTEST_CHAPTERS.md`.

Short names used in the evidence columns: text-pass = `FRIEND_V3_COMPLETE_TEXT_PASS.md`;
content pass = `FRIEND_V3_CONTENT_PASS.md`; content-pass plan = `FRIEND_V3_CONTENT_PASS_PLAN.md`;
cold-boot = `FRIEND_V3_COLD_BOOT_ACCEPTANCE.md`; Tulma record = `FRIEND_V3_TULMA_GRAPHICS.md`;
stability record = `FRIEND_V3_STABILITY_PASS.md`; inventory = `FRIEND_V3_PLAYTEST_BOOST_INVENTORY.md`;
completion record = `FRIEND_V3_PLAYTEST_BOOST_COMPLETION.md`.

## 1. Current image

| field | value |
| --- | --- |
| image | `v3-playtest-boost.gba`, built by `build/fv3boost001/build.ps1` (ignored, not tracked) |
| SHA-256 | `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c` |
| bytes | 10,140,972 |
| status | frozen baseline; every future fix is a new image built from it |
| canonical retail ROM | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, unchanged |
| do not use | `6d7a56c6...` (retired, hp and ep read negative) and any Bandana probe image |

## 2. How to read the states

Every item carries an **implementation** state and a separate **verification** state.

| state | meaning |
| --- | --- |
| IMPLEMENTED | the bytes are in `acd98c2a` |
| ROM-VERIFIED | proven by a static read, census or test of image bytes; says nothing about what the game does |
| RUNTIME-VERIFIED | observed in a running game **on `acd98c2a`**, with the record named |
| PARTIALLY VERIFIED | part of the claim is observed, the rest is static, owner-attested, or observed on a different image |
| PLANNED / NOT IMPLEMENTED | intended or proposed; no bytes written |
| BLOCKED | waits on a named dependency |
| OWNER DECISION REQUIRED | waits on the owner; nothing is built until decided |
| CANCELLED | withdrawn by the owner; kept for the record |
| DEFERRED TO PLAYTEST | only a human playing the image can settle it |

**An observation on another image is never RUNTIME-VERIFIED here.** Ancestors of
`acd98c2a` (section 3) differ from it only in diff-confined spans, so their observations carry
forward as evidence about the same bytes, and the row is PARTIALLY VERIFIED. Sibling images
are not ancestors: they were built from a different rename map, so their runtime results show
the mechanism works, not that these bytes do.

Priority: **P0** blocks or invalidates the first playtest; **P1** needed in the first playtest
round; **P2** next development phase; **P3** latent or later.

Needs: **C** owner creative decision, **E** engineering investigation, **H** human playtest.

## 3. Lineage

### 3.1 The ancestors of `acd98c2a`

| stage | image (SHA-256 prefix, bytes) | what it added | record |
| --- | --- | --- | --- |
| friend's own modded image, third party, before this repository | `a6f44422`, 9,732,800 | the friend's original customization; its full change list is not recorded anywhere in this repository | `FRIEND_V3_STABILITY_PASS.md` section 2 |
| `v3.gba` | `38504057`, 9,740,166 | the image that crashed on map 134 (`F0674DD8`) | same, section 3 |
| `v3-safe.gba`, the rename base | `b0de6ddf`, 9,740,320 | slot 292 composition buffer `0x200` to `0x400`, the crash fix | same, section 3 |
| extended rename map, 492 rows | map `5a60806b` | the operator's private 451-row map (`8fc91afc`) plus 41 rows: Soyman, Tulma and Chichi rules | `FRIEND_V3_COMPLETE_TEXT_PASS.md` sections 2, 3.1 |
| dialogue splice | `bf16dfd3` | renamed dialogue carried by two-glyph tokens | same, section 2 |
| token engine | `cec009d9` | the engine patch that draws the tokens | same, section 2 |
| content-pass edits | `d564ef8a` | seven menu, biography and Soyman sites, reapplied on this chain | same, section 2; `FRIEND_V3_CONTENT_PASS.md` section 2 |
| complete text pass | `20f2c140`, 10,133,410 | 14 in-place and 7 relocated menu sites | `FRIEND_V3_COMPLETE_TEXT_PASS.md`, MR !155 and !156, merges `1a45f494`, `d003ce93` |
| Tulma graphics | `ef939dcd`, 10,140,972 | sprite 41 (22 containers), portrait slot 17 | `FRIEND_V3_TULMA_GRAPHICS.md`, MR !165, merge `0b3676a7` |
| Tulma dialogue | `a4c12a95`, 10,140,972 | two World Tournament lines, owner-authorized | same, section 9 |
| **playtest boost** | **`acd98c2a`**, 10,140,972 | records 0 to 4: level 200, STR/POW/END/SPD 255 | `FRIEND_V3_PLAYTEST_BOOST.md`, MR !170 (`a6e4aba2`), MR !176 (`372bb3aa`) |

`CHARACTER_SWAP_TOOLKIT.md` (MR !166, merge `1b022217`) reproduces the two Tulma stages
byte for byte from `20f2c140`; the boost build re-ran them.

### 3.2 Sibling and retired images, not ancestors

| image | what it is | why it matters |
| --- | --- | --- |
| `cffdb81e`, `d401d71c` | the 451-row splice and its token engine | the cold-boot Kibito acceptance and the map-134 crash regression ran on `d401d71c` |
| `b3344a3f` | the merged content-pass candidate, also on the 451-row map | a cold boot to the Kibito scene ran on it |
| `aec5aa9f` | discarded Tulma candidate with a wrongly encoded portrait | the sprite was first seen on it |
| `6d7a56c6` | first playtest boost, RETIRED | its status screen is the only capture of level 200 and the 255 stats |

All images are private inputs and are not in the repository.

## 4. Displayed identities

A report must name the base-stat record or the retail character, because this build renames
the name table itself (`FRIEND_V3_PLAYTEST_BOOST_COMPLETION.md` section 0e).

| retail character | displays as | evidence |
| --- | --- | --- |
| Goku | Yamcha | name-table index 116; status screen `YAMCHA LVL 200` on `6d7a56c6` |
| Gohan | Krillin | index 123; cold-boot screenshot on `d401d71c`, `Kibito will take care of Krillin` |
| Krillin | Goku | text-pass audit: retail `Goku and Krillin` displays as `Yamcha and Goku` |
| Goten | Videl | biography slot 1191 |
| Trunks | Uub | biography slot 1193 |
| Vegeta | Tien | biography slot 1195; chapter 5 title `Majin Tien` |
| Chi-Chi | Bulma | text-pass rule for retail `Chi-Chi` and `Chichi` |
| retail Bulma | Tulma | slot 1032; dialogue rule; sprite 41 and portrait 17 |
| Android 18 | Chi-Chi | text-pass section 5, item 7 |
| Gogeta | Yamien | menu slots 136, 165, 181, 1304, 1305 |
| Vegito | Tiencha | menu slots 134, 135, 164, 180, 1306, 1307 |
| Saiyaman | Soyman | 20 spoken occurrences; slots 122, 1453, 603, 1346, 1347 |
| Piccolo | unchanged | owner decision, content-pass plan section 4 |
| Hercule | unchanged | no rename recorded |
| Gotenks | not established | no rename recorded; the checklists use the retail name |

UNVERIFIED, source not in the repository: `Yamcha` displays as `Gohan`, and `Kakarot` as
`Yamcha` (owner handoff record only). Not established: what the retail Videl, Uub and Tien
records display as, and whether base-stat record 8 is Videl (external RAM map) or Hercule
(`BASE_STAT_NAMES`).

## 5. Items

**A. Names, text and dialogue**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | character rename across dialogue, menus, scans, chapters | IMPLEMENTED | PARTIALLY VERIFIED: 868 occurrences, 0 unresolved (ROM); renamed lines seen on a savestate run of ancestor `20f2c140` and on cold boots of siblings `d401d71c` and `b3344a3f`; not observed on `acd98c2a` | text-pass section 4, 6; cold-boot section 4 | P1 | read names in every scene; report a retail name by record | H |
| A2 | `Saiyaman` to `Soyman`, spoken and menu | IMPLEMENTED | PARTIALLY VERIFIED: 20 to 0 by stream count; one renamed line seen on ancestor `20f2c140` | text-pass sections 3.1, 6 | P1 | check chapter 2 in play | H |
| A3 | retail `Bulma` displays `Tulma` (18 spoken, 9 menu sites) | IMPLEMENTED | ROM-VERIFIED | text-pass sections 3.1, 3.3 | P1 | check quest log and Capsule Corp scenes | H |
| A4 | `Gogeta` to `Yamien`, `Vegito` to `Tiencha` in the menu pool | IMPLEMENTED | ROM-VERIFIED | text-pass section 3.3 | P1 | check each fusion and its menu | H |
| A5 | four spoken records read `Tulma` where the content-pass plan said `Chi-Chi` (`1:26476:306`, `4:10050:156`, `4:18714:142`, `5:42592:1086`) | IMPLEMENTED as `Tulma` | ROM-VERIFIED | text-pass section 5, item 1 | P2 | owner confirms `Tulma` or picks a `Chi-Chi` route (content pass section 4) | C |
| A6 | slot 1347 reads `back into Krillin`, reversing the content pass's `Goku` | IMPLEMENTED | ROM-VERIFIED | text-pass sections 3.4, 5 item 3 | P2 | owner confirms | C |
| A7 | slot 1193 `Uub is the son of Tien and Tulma`, which implies a marriage Tulma's biography omits | IMPLEMENTED, retail-derived | ROM-VERIFIED | text-pass section 5, item 2 | P2 | owner keeps it or approves a one-site rewording | C |
| A8 | one spoken `Great Soy Man`, spaced, retail text | not changed | ROM-VERIFIED | text-pass section 5, item 8 | P3 | owner keeps it or approves `Great Soyman` | C |
| A9 | chapter and saga titles | IMPLEMENTED for chapter 2 `Great Soyman` and chapter 5 `Majin Tien`; no other title text recorded | ROM-VERIFIED | text-pass section 5, item 5 | P3 | none unless the owner supplies title text | C |
| A10 | credits line `Cale Aaron Cymek` | IMPLEMENTED; present since at least the content-pass foundation; origin not recorded | ROM-VERIFIED at file `0x949FFE`; not seen at runtime | text-pass section 7 | P1 | read the end credits | H |
| A11 | five orphaned retail strings with no table entry or reference | left in place by decision | ROM-VERIFIED unreachable by the checks applied | text-pass section 4 | P3 | reopen only if one appears on screen | none |
| A12 | Idasa and Uub interaction dialogue | PLANNED / NOT IMPLEMENTED. Owner has RESERVED the wording and rejected the drafted proposal; the owner supplies the lines | records, speakers, portraits and length constraints located and preserved (see A13) | Idasa record | P2 | owner supplies wording; then the group relayout path | C, then E |
| A13 | Idasa/Uub scene located in bytes: 18 records, one reference site each, portraits resolve to owner-confirmed speakers | LOCATED, recorded in the unmerged research doc | ROM-VERIFIED on `acd98c2a`; MR !178 still open and unmerged | `FRIEND_V3_IDASA_UUB_DIALOGUE.md` (unmerged), Adja `44c7505b` | P2 | merge !178 or re-cut the doc; owner wording unchanged until supplied | E |
| A14 | approved text batch: seven biographies (1059, 1069, 1187, 1189, 1191, 1193, 1195) and the slot 1065 grammar repair | **IMPLEMENTED and INTEGRATED** into the mainline derivative built on the pre-BOOST foundation `a4c12a95`; seven in place, 1065 relocated | ROM-VERIFIED: all eight slots read their approved wording back, 0 of the other 1,526 slots changed text, 0 bytes differ outside the declared sites, adapted to the foundation and reproduced byte-identically | Adja `a6f39d3e`; derivative `d2a25f9a…`, 10,141,220 bytes | P1 | runtime read of each biography | H |
| A15 | one spoken `Great Soy Man` reads `Great Soyman` | NOT IMPLEMENTED; measured | ROM-VERIFIED: record `1:38856:252` holds it once; a second record `1:37530:2416` covers the span, so it needs a group relayout, not an in-place edit | Adja `f8d4608b` | P1 | DEFERRED TO ENGINE TICKET | E |
| A16 | interior dialogue padding from the rename (321 runs, 653 units) | PARTIALLY: 32 trailing-pad records repairable in place and proven; the interior remainder needs container duplication, which the 15-bit handle start field caps at 65,534 bytes, so containers 0 and 2 cannot take it | ROM-VERIFIED: four independent checks pass on the trailing subset; the non-duplicating rebuild drops 0 units; 43 high-drift records are left byte-identical rather than corrupted | Adja `09bddc8b`, `b63df963`, `bbce5015` | P1 | DEFERRED TO ENGINE TICKET: the owner chose the engine-side change and directed that it not start here; disassembly scope measured in Adja `9c29d1df` | C then E |
| A17 | `Kakarot` to `Bandit` where Tien addresses Yamcha | NOT IMPLEMENTED; target set resolved from the rename map's provenance | ROM-VERIFIED: the friend image holds 0 literal `Kakarot`; the map has 56 rows carrying a renamed Kakarot word; across them **57 occurrences are direct address** and **2 are mentions** (`Yamcha's boy`, `the youngest child of Yamcha`) and out of the approved context. Punctuated occurrences are +1 unit and need a group relayout | Adja `5b97beb5`, `0c535869` | P1 | DEFERRED TO ENGINE TICKET; the address-only set still awaits owner confirmation | C then E |
| A18 | trailing-pad repair tooling | IMPLEMENTED in tracked source: `tools/research/trim_dialogue_padding.py`, staged write, refuses its own input | ROM-VERIFIED statically: the tool reproduces candidate `02b69c8e` byte-identically and the four-check verifier passes on the real image. Its evidence scripts live under the ignored `build/` tree, the unit test is OWED (four synthetic fixtures failed; the last was removed rather than left failing, Adja `29e35270`), and display correctness is NOT proven | Adja `29e35270` | P1 | build the synthetic test from the inventory's own scan offsets; runtime evidence | H, E |


**B. Tulma**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | Tulma actor art: sprite 41, 22 containers | IMPLEMENTED | PARTIALLY VERIFIED: drawn in session `tulma001-encounter-6` on discarded `aec5aa9f`; authored container bytes in VRAM in session `tulma001-encounter-8` on ancestor `ef939dcd`; not observed on `acd98c2a` | Tulma record sections 4 to 6 | P1 | see her in play | H |
| B2 | Tulma portrait, slot 17 | IMPLEMENTED | PARTIALLY VERIFIED: captured in session `tulma001-encounter-8` on `ef939dcd`; not observed on `acd98c2a` | Tulma record section 6 | P1 | same | H |
| B3 | blonde appearance | IMPLEMENTED by the supplied recoloured art (portrait hair index 187 to 200). Supersedes text-pass section 5 item 10 and content-pass section 5 item 2, which predate MR !165. No separate appearance record is needed: the displayed `Bulma` is retail Chi-Chi on sprite 66 | PARTIALLY VERIFIED as for B1 and B2; final look not accepted | Tulma record sections 2, 3 | P1 | owner visual acceptance in play | C, H |
| B4 | two rewritten World Tournament lines, slots 60182 and 60294 | IMPLEMENTED | PARTIALLY VERIFIED: exhaustive 2,814-record compare (ROM); on screen owner-attested on `a4c12a95`, no capture | Tulma record section 9 | P1 | capture the scene on `acd98c2a` | H |
| B5 | Tulma name (slot 1032) and biography (slot 1033): identical twin, daughter of Dr. and Mrs. Brief, no marriage line | IMPLEMENTED | ROM-VERIFIED; scan screen not seen | content pass section 2 | P1 | open her scan in play | H |
| B6 | Tulma's scenes | the World Tournament registration scene is the only one established; every retail Bulma scene now draws her (walkthrough: West City in chapters 2, 3 and 6) | PARTIALLY VERIFIED: B1, B2, B4 on other images; none on `acd98c2a` | Tulma record sections 6, 8, 9; walkthrough chapters 2, 3, 6 | P1 | check each scene listed in the guide | H |
| B7 | the two enclosing scene views carry 15 units of padding after B4 | as written | unknown whether ever displayed | Tulma record section 9 | P2 | watch for stray spaces in that scene | H |
| B8 | more palette freedom (11 candidate spare entries) | PLANNED / NOT IMPLEMENTED; the Tulma record says it was filed as a separate ticket, and no ticket id is recorded | none | Tulma record section 7 | P3 | the owner decides whether it is wanted | C |

**C. Bosses, difficulty and combat**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | Dabura replaced by Broly | PLANNED / NOT IMPLEMENTED; OWNER DECISION REQUIRED | none | proposal in the owner's handoff record only (UNVERIFIED, not in the repository). Retail already has Broly as the chapter 6 boss of the northern wilderness; Dabura is the chapter 4 Babidi's ship boss (walkthrough chapters 4, 6) | P2 | owner approves or drops; then research the encounter records | C, then E |
| C2 | Spopovich replaced by Android #13 or Perfect Cell | OWNER DECISION REQUIRED | none | content pass section 5 item 5; text-pass section 5 item 6; Spopovich is fought in chapter 3 (walkthrough). Whether either target has a usable actor is not established | P2 | owner picks; then check the actor | C, then E |
| C3 | tougher Hercule encounter | OWNER DECISION REQUIRED | none | content pass section 5 item 1; text-pass section 5 item 9: the lever is his enemy stat record, survey values not archived, only hp has measured consumption evidence, the enemy-stat randomizer writes the same record | P2 | owner sets the intent; engineering re-derives the record | C, then E |
| C4 | tougher Olibu encounter | OWNER DECISION REQUIRED | none | proposal in the owner's handoff record only (UNVERIFIED). Olibu is fought in chapter 1 (walkthrough); no lever located | P2 | owner confirms; then locate the record | C, then E |
| C5 | balancing beyond the playtest boosts | owner-reserved | none | `FRIEND-V3-PLAYTEST-001` charter | P3 | none until requested | C |

**D. Biographies**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | six proposed scan-biography rewrites (slots 1059, 1187, 1189, 1191, 1193, 1195) | PLANNED / NOT IMPLEMENTED | wording measured to fit | content-pass plan section 7; text-pass section 5 item 7 judges them unnecessary | P2 | owner approves, rejects or rewrites | C |
| D2 | slot 1065 retail grammar defect | not changed | ROM-VERIFIED | text-pass section 5, item 7 | P3 | owner approves the one-word repair or keeps retail | C |
| D3 | slot 1043, ambiguous under the renaming | not changed | ROM-VERIFIED | content pass section 5, item 3 | P3 | owner reads it | C |
| D4 | new biography content | none recorded | none | charter `owner_reserved` | P3 | none until supplied | C |

**E. Visuals and cutscenes**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | hospital Senzu cutscene shows Videl in bed where retail shows Android 18 standing | tracked only; no animation change made | not reproduced in this repository | owner handoff record; `372bb3aa:docs/research/FRIEND_V3_PLAYTEST_BOOST.md` section 4.5 | P2 | reproduce and capture on `acd98c2a` and retail; then the owner decides | H, then E, then C |
| E2 | cutscene sprite persistence workstream | PLANNED / NOT IMPLEMENTED; scope not written | none | owner handoff record only; UNVERIFIED, no repository record | P3 | owner states what should change; E1 is the only concrete case | C |
| E3 | fusion characters keep retail art under renamed text | as retail | none | A4 | P3 | none | none |

**F. Levels and progression**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | bypass level gates where the mechanism is located | NOT IMPLEMENTED. No gate search is recorded. The walkthrough lists character gates the boosted records should clear: 65 (chapter 1), Goku's forest gates (chapters 3 and 4), Trunks' 80 (chapter 6), and a level 120 door for Vegeta (chapter 4) | none | charter `in_scope`; `FRIEND_V3_PLAYTEST_BOOST_INVENTORY.md` section 6; walkthrough | P1 | the guide's gate checks; a gate that refuses a boosted character becomes an engineering item | H, then E |
| F2 | level cap 200 is a code constant (`cmp r6,#0xc8`) | unchanged by decision | ROM-VERIFIED | `FRIEND_V3_PLAYTEST_BOOST.md` section 2 | P3 | none | none |
| F3 | starting at level 200 with `NXT LVL: 0` | IMPLEMENTED | status screen seen on `6d7a56c6` only; that the game handles the state is not shown | completion record section 0b | P0 | first stat screen; first experience gain | H |

**G. Statistics and abilities**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G1 | records 0 to 4 at level 200, STR/POW/END/SPD 255 | IMPLEMENTED | PARTIALLY VERIFIED: 25-byte census (ROM); the values read on the status screen of `6d7a56c6`; on `acd98c2a` a 60-second boot-to-New-Game smoke and a New Game run of about six minutes (to frame 34,890) with no crash, neither reading the stat screen | `FRIEND_V3_PLAYTEST_BOOST.md` sections 1, 3; inventory section 3; completion 0b | P0 | read each boosted character's stat screen | H |
| G2 | hp and ep left at foundation values (owner ruling after `0xFFFF` read as negative) | IMPLEMENTED | ROM-VERIFIED and pinned by a unit test; not observed on `acd98c2a` | completion record 0b | P0 | read hp and ep | H |
| G3 | energy-consuming attacks work | as retail | DEFERRED TO PLAYTEST; they failed on `6d7a56c6` | completion record 0b | P0 | use one per boosted character | H |
| G4 | character switching keeps each character's stats | as retail | DEFERRED TO PLAYTEST | none | P1 | switch to each boosted character and back | H |
| G5 | records 5 to 8 (fusions and record 8) untouched by the boost | by design | ROM-VERIFIED | `FRIEND_V3_PLAYTEST_BOOST.md` section 2 | P3 | a weaker fusion is expected | none |
| G6 | techniques unchanged | as retail | ROM-VERIFIED | same | P3 | none | none |
| G7 | the friend's own stat and level values, kept | IMPLEMENTED by the friend build, stage not recorded; record 1 hp and ep `0x0064` against retail `0x0055`; foundation levels `[65,65,75,60,75,75,75,75,50]`, whose difference from retail is not recorded | ROM-VERIFIED | completion record 0b; text-pass section 7 | P3 | none | none |

**H. Inventory and equipment**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | Bandana in the starting inventory | **CANCELLED BY OWNER.** Obtained through normal gameplay; the walkthrough notes bandanas drop from enemies before chapter 6. Do not reopen | the excluded hook is byte-compared absent and a unit test fails if it regains a caller. The two research records give different withdrawal reasons (a hang, then after a fix a menu-arrow defect); the cancellation makes that moot | `FRIEND_V3_PLAYTEST_BOOST_TRAMPOLINE.md`; inventory section 5 | none | none | none |
| H2 | starting inventory is retail: 2 Miso Soup, equipment count 0 | as retail | RUNTIME-VERIFIED on `acd98c2a`, real New Game from an erased save | inventory record section 3 | P3 | none | none |
| H3 | items, shops and equipment otherwise retail | as retail | DEFERRED TO PLAYTEST | `FRIEND_V3_PLAYTEST_BOOST.md` section 6 step 3 | P1 | buy, use and equip | H |

**I. Save and load**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I1 | EEPROM save, 8,192 bytes; the emulator save type must be EEPROM or Flash 128K (Almar's Guides; Gamer's Temple walkthrough, as cited by the earlier guide) | as retail | the smoke run on `acd98c2a` wrote a valid 8,192-byte save; reload not tested | `FRIEND_V3_PLAYTEST_BOOST.md` section 3 | P1 | save, quit, reload | H |
| I2 | a save written by another image restores old stats | known limit | documented | same, section 5 item 5 | P1 | start from an empty save | H |

**J. Stability and engine limits**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J1 | `F0674DD8` crash on map 134 (slot 292 buffer) | fixed in ancestor `v3-safe`; byte `0x6B692B` = `0x04` preserved through the chain | PARTIALLY VERIFIED: ROM-VERIFIED in the chain; two hand-driven runs on sibling `d401d71c`; not run on `acd98c2a` | stability record sections 3, 4, 6; text-pass section 7 | P2 | the map-134 tournament grounds are on the chapter 3 route (walkthrough) | H |
| J2 | Kibito-scene freeze from a grown rename | fixed by the token engine | PARTIALLY VERIFIED: cold boots survived on siblings `d401d71c` and `b3344a3f`; a savestate run survived on ancestor `20f2c140`; no cold boot of `acd98c2a` to the scene | cold-boot and content-pass records; text-pass section 6 | P1 | reach the Kibito scene in chapter 3 (walkthrough) | H |
| J3 | zero slack on all 297 composition buffers | LATENT | ROM-VERIFIED | stability record section 7.1 | P3 | any future frame resize must enlarge its slot's buffer | E |
| J4 | 275,033 bytes over the targets of 99 canonical references | LATENT; no consumer found | ROM-VERIFIED | stability record section 7.2 | P2 | report any crash with its scene | H |
| J5 | late-game stability | not claimed | DEFERRED TO PLAYTEST | `FRIEND_V3_PLAYTEST_BOOST.md` section 5 item 3 | P1 | full campaign | H |

**K. Playtest coverage**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| K1 | chapters 1 to 12 in order | n/a | DEFERRED TO PLAYTEST; none walked | guide | P1 | play and tick each chapter | H |
| K2 | chapter-specific checkpoints | provided from this revision in `FRIEND_V3_PLAYTEST_CHAPTERS.md`, sourced from the cited walkthrough; the short speedrun version is the guide | n/a | both checklists | P1 | use them | H |
| K3 | full campaign completion | n/a | DEFERRED TO PLAYTEST | guide | P1 | the playthrough that closes the H rows | H |

**L. Tooling debt that touches this image**

| id | item | state | evidence | pri |
| --- | --- | --- | --- | --- |
| L1 | four span-writer refusals have no unit test | debt, guards exercised by hand | content pass section 3 | P3 |
| L2 | `test_graphics_rom.py::test_verified_graphics_pointers_join_the_common_reference_graph` red at its baseline (11,304 against 11,302) | disclosed, not this track's | Tulma record section 5, item 9 | P3 |
| L3 | the 60-second smoke left no replayable run directory | recorded observation only | `FRIEND_V3_PLAYTEST_BOOST.md` section 5 item 1 | P3 |

Program-level safety items (R1 filesystem migration, R3 destination guard) are project
records, not changes to this image, and are not tracked here.

## 6. The BOOST acceptance checks, demonstrated versus deferred

| check | demonstrated | deferred to the human playtest |
| --- | --- | --- |
| level 200 and boosted stats on the stat screen | status screen of `6d7a56c6`; static census of `acd98c2a` | stat screen on `acd98c2a` (G1, F3) |
| valid hp and ep, working energy attacks | bytes pinned by test | values on screen and an energy attack (G2, G3) |
| character switching and stat persistence | nothing | all of it (G4) |
| save and reload | a valid 8,192-byte save written | reload with progress intact (I1) |
| representative level-gate behaviour | nothing; no gate search recorded | the walkthrough's gates (F1) |
| Tulma's scripted encounter | art, portrait and lines on other images (B1, B2, B4) | her scenes on `acd98c2a` (B6) |
| chapter progression and late-game stability | boot to New Game at 72.7 fps; a six-minute New Game run with no crash | chapters 1 to 12 (K1, J5) |
| full campaign completion | nothing | all of it (K3) |

## 7. Original requirements against the outcome

The `FRIEND-V3-PLAYTEST-001` charter `in_scope`:

| requirement | outcome |
| --- | --- |
| consolidate verified completed modifications into one image | done: `acd98c2a` carries the chain in section 3.1 |
| maximum valid level and statistics for the five playable characters | level and four stats done; **hp and ep deliberately not maximised** by owner ruling (G2) |
| bypass character-level restrictions where located, preserving story events; record a gate that cannot be located | **not done and no search recorded** (F1); story preservation unverified until playtest |
| one Bandana in the starting inventory if a ROM-initiated mechanism is located | **CANCELLED BY OWNER** (H1) |
| reproducible builds with input hashes, output digest and manifest | done for stages 6 to 9 (`build.ps1`, manifest, reproduced twice); stages 1 to 5 rest on the merged chain's published digests, not re-driven |
| regression tests for the code written | done: `tests/unit/test_friend_v3_playtest_boost.py`, 10 passed |
| one authoritative modification and TODO tracker | this document |
| one full-campaign speedrun and stability checklist | `FRIEND_V3_PLAYTEST_GUIDE.md` (hack-specific) and `FRIEND_V3_PLAYTEST_CHAPTERS.md` (chapter checkpoints, added in this revision); `FRIEND_V3_PLAYTEST_BOOST.md` section 6 gains character switching and save-reload |
| independent review of a frozen candidate, CI, integration | done: MR !170 and MR !176, true merges, master CI green |
| targeted runtime verification | two boot runs on `acd98c2a`; every in-game check in section 6 is outstanding |

## 8. Owner decisions, separate from engineering

1. A5: confirm `Tulma` in the four spoken records, or choose a `Chi-Chi` route.
2. A6: confirm `back into Krillin` in slot 1347.
3. A7: keep slot 1193 or approve rewording.
4. A8: keep `Great Soy Man` or approve `Great Soyman`.
5. A12: write the Idasa and Uub lines.
6. B3: accept Tulma's look after seeing it in play.
7. B8: whether more palette freedom is wanted.
8. C1 to C4: approve or drop Dabura to Broly (noting retail already has a Broly boss), choose Spopovich's replacement, set Hercule's and Olibu's difficulty.
9. D1 to D3: the six biography proposals, slot 1065, slot 1043.
10. E1, E2: the hospital scene once reproduced; what cutscene persistence should cover.
11. Any new title, biography or balancing text (A9, D4, C5).

## 9. Phases

1. **Playtest round 1 on `acd98c2a`** (now): the P0 and P1 rows marked H, through the guide.
   Each bug goes into section 10 with the guide's report fields and a severity.
2. **Triage and fix.** A fix is proposed only for a defect reproduced twice from a fresh save,
   built as a new image from `acd98c2a`. Engineering items playtest exposes (F1 gates, E1) are
   scoped here.
3. **Owner text batch.** Once items 1 to 5 and 9 of section 8 are decided: one text and
   dialogue ticket with the merged toolkit, one new image, one review.
4. **Combat and boss workstream** (C1 to C4), after the owner decides; each starts with a
   research step, because none of the levers is archived.
5. **Cutscene workstream** (E1, E2), after reproduction and a decision.
6. **Final campaign playthrough** on the last image, closing K3.

## 10. Playtest bug log

Severity: S1 crash, softlock or save loss; S2 wrong behaviour that blocks progress; S3 wrong
but passable; S4 cosmetic. A fix is proposed only for a reproduction.

| id | date | image (prefix) | fresh save | chapter and place | symptom | repro count | severity | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
