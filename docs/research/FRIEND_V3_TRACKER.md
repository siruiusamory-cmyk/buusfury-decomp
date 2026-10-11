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
completion record = `FRIEND_V3_PLAYTEST_BOOST_COMPLETION.md`; Idasa/Uub record =
`FRIEND_V3_IDASA_UUB_DIALOGUE.md`.

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
| A12 | Idasa and Uub World Tournament dialogue | **HELD, NOT IN THIS RELEASE.** The owner approved the full script and chose to land every line together in the successor ticket, because five of the fifteen grow their record and a partial scene would mix new replies with old prompts | ROM-VERIFIED: 	ools/research/apply_friend_v3_world_tournament.py places the ten that fit and measures the five that need 17, 12, 13, 5 and 15 more units; the release keeps the whole scene retail, proven by erify_wt_retail.py reporting 0 differences across all eighteen records | Adja 38925127; script in the owner decision log | P1 | successor ticket lands all fifteen with the container work | C done, E pending |
| A13 | Idasa/Uub scene located in bytes: 18 records, one reference site each, portraits resolve to owner-confirmed speakers | LOCATED, recorded in the research doc now on master (MR !178) | ROM-VERIFIED: every record, handle and single reference site is in the Idasa/Uub record, each owner-confirmed speaker agrees with the record's portrait operand, and the earlier claim that no change was necessary was the LOCATE ticket's scope, not a judgement about the wording | `FRIEND_V3_IDASA_UUB_DIALOGUE.md`; Adja `44c7505b`. Owner decisions still open in it: the wealth line (section 5) and the two characters named Uub (section 6) | P2 | owner decides those two; the script itself is approved and held (A12) | C then E |
| A14 | approved text batch: seven biographies (1059, 1069, 1187, 1189, 1191, 1193, 1195) and the slot 1065 grammar repair | **IMPLEMENTED and INTEGRATED** into the mainline derivative built on the pre-BOOST foundation `a4c12a95`; seven in place, 1065 relocated | ROM-VERIFIED: all eight slots read their approved wording back, 0 of the other 1,526 slots changed text, 0 bytes differ outside the declared sites, reproduced byte-identically | Adja `a6f39d3e`; derivative `d2a25f9a…`, 10,141,220 bytes | P1 | runtime read of each biography | H |
| A15 | one spoken `Great Soy Man` reads `Great Soyman` | NOT IMPLEMENTED; measured | ROM-VERIFIED: record `1:38856:252` holds it once; a second record `1:37530:2416` covers the span, so it needs a group relayout, not an in-place edit | Adja `f8d4608b` | P1 | DEFERRED TO ENGINE TICKET | E |
| A16 | interior dialogue padding from the rename (321 runs, 653 units) | PARTIALLY: 32 trailing-pad records repairable in place and proven; the interior remainder was recorded as needing container duplication, which the 15-bit handle start field caps at 65,534 bytes. **That reading was too pessimistic and is corrected here**: the ceiling is per container, and a record can be moved to a new one. Measured on the mainline derivative, 133 of the 229 padded records are repairable **in place** (their pad is read by no other record), and only the 96 whose pad a sharing record also reads have to move - into ONE new container, 47,532 bytes with the grown rows, against 65,536. Full duplication of all 2,808 records indeed does not fit (572,888 bytes against 384 KiB of selectors 0-5); the targeted repair does | ROM-VERIFIED: four independent checks pass on the trailing subset; the non-duplicating rebuild drops 0 units; 43 high-drift records are left byte-identical rather than corrupted. The corrected split arithmetic is ROM-VERIFIED in `FRIEND_V3_WT_SPLIT_CONTAINER.md` | Adja `09bddc8b`, `b63df963`, `bbce5015`; `tools/research/plan_friend_v3_container_split.py` | P1 | the runtime proof landed (`FRIEND_V3_WT_SPLIT_CONTAINER_RUNTIME.md`), so the selector 7 split replaces the engine change; phase B is the remaining work | E |
| A17 | `Kakarot` to `Bandit` where Tien addresses Yamcha | NOT IMPLEMENTED; target set resolved from the rename map's provenance | ROM-VERIFIED: the friend image holds 0 literal `Kakarot`; the map has 56 rows carrying a renamed Kakarot word; across them **57 occurrences are direct address** and **2 are mentions** and out of the approved context. Punctuated occurrences need a group relayout | Adja `5b97beb5`, `0c535869` | P1 | DEFERRED TO ENGINE TICKET; the address-only set still awaits owner confirmation | C then E |
| A18 | trailing-pad repair tooling and its unit test | IMPLEMENTED in tracked source: `tools/research/trim_dialogue_padding.py` (staged write, refuses its own input) and `tests/unit/test_dialogue_trim_padding.py` (4 passed, synthetic bytes, no ROM needed) | ROM-VERIFIED statically: the tool reproduces candidate `02b69c8e` byte-identically and the four-check verifier passes on the real image. Display correctness is NOT proven; CI is green on MR !180 and no runtime text capture exists | Adja `38925127`; MR !180 | P1 | runtime evidence, which needs an input driver from the idle savestate | H |
| A19 | mainline derivative, its lineage and its CI | **DELIVERED**: `v3-mainline-text-dialogue-pass.gba`, 10,141,220 bytes, reproduced twice byte-identically | ROM-VERIFIED: base is the pre-BOOST foundation, and all 25 BOOST-only base-stat bytes are re-checked against it after the final write; CI green (test-site, test-sdk) on `4a1957f` | MR !180, pipeline `2933408207`; Adja `38925127` | P1 | merged by the owner; then the successor engine ticket | C |
| A20 | the split-container route: a new dialogue container on a selector above 6, reached by one table word | **RELEASE 2 DELIVERED ON THIS ROUTE.** One new container of 2,028 bytes on selector 7 carries the fifteen World Tournament rows; fifteen handle words rewritten; no base container byte moved and no game code changed | RUNTIME-VERIFIED on the release candidate `0b5ac8f4` (cold boot, battery save): fourteen of fifteen rows resolved out of the appended container `0x089ABE24` with their approved wording, one photographed on screen in the junior division scene, operator-confirmed; row 18 static-verified only. ROM-VERIFIED: 0 stray bytes, three unchanged rows byte-identical, 63 other slots unchanged, reproduced twice, BOOST absence 25 of 25 non-vacuous. The longer run also falsified the *general* claim that `0x080122CE` never runs: it fires with a level-up, and both sites read the same literal | `FRIEND_V3_WT_SPLIT_CONTAINER.md`, `FRIEND_V3_WT_SPLIT_CONTAINER_RUNTIME.md`, `FRIEND_V3_WT_SPLIT_CONTAINER_RELEASE2.md`; `tools/research/build_friend_v3_world_tournament_split.py`; `tests/unit/test_friend_v3_world_tournament_rows.py` | P1 | release 3: interior padding, `Great Soyman`, punctuated `Bandit`, and the Hercule and Olibu encounters | E |
| A21 | release 2.1: the registration scene's two owner lines and Bulma's biography | **IMPLEMENTED, ALL THREE RUNTIME-CHECKED.** `2:60432:98` (Oolong) and `2:60922:140` (Master Roshi) carry the owner's wording, copied into the selector-7 container rather than written in place because covering records read through both spans. Text slot 1083 (Bulma's scanner biography) is relocated to file `0x9ACFE6` | ROM-VERIFIED: both rows resolve through the table and read the wording exactly, slot 1083 reads its wording from the new home, the container declares and decodes 2,266 bytes and carries 18 record words including the fifteen World Tournament rows, 0 stray bytes, 12 differing bytes in the base, reproduced twice, BOOST absence 25 of 25. RUNTIME-VERIFIED for the biography: the running game fetched pointer `0x089AC618` and drew the new wording, screenshot `scanner-screen-bulma-frame2160.png`. OWNER-ATTESTED for the two registration rows: the owner played `018757c4` and confirmed both lines in the scene; no capture exists for them | `FRIEND_V3_WT_SPLIT_CONTAINER_RELEASE21.md`; `tools/research/apply_friend_v3_registration_rows.py`; `tools/research/friend_v3_text_approvals.py` | P1 | optional machine capture of the registration scene, as the World Tournament scene had | H |
| A22 | continuity: the approved Roshi line calls Bulma and Tulma twins | recorded, no text changed to reconcile it | owner decision, 2026-10-10; the sibling biographies still describe Tulma as Bulma's identical twin, so "twin" agrees with them | `FRIEND_V3_WT_SPLIT_CONTAINER_RELEASE21.md` | P2 | owner review | C |
| A23 | release 3 delivery: Hercule and Olibu as real boss fights, the aggressive profile the owner fought, and the wording tail | **DELIVERED.** Image `521bd0fa0a8bc198f36430e3419184807e335fa588bd718152996c076a8f15fd` (10,146,136 bytes), cut from release 2.1, reproduced twice byte-identically by one command. Hercule 2500/40/30, Olibu 1500/22/16, endurance and level untouched; both given a per-enemy behaviour profile (attack arm first, gate r150, swing radius r150, chance 50%, retail swing chain) whose decisive change is the attack arm's position; the spaced "Great Soy Man" repaired and seven of the ten kakarot lines reading "Bandit" | ROM-VERIFIED: 149 other enemy records byte-identical, 0 stray bytes outside the declared sites, both verifiers PASS, 10 focused tests, RUNTIME-VERIFIED: the bite curve was measured at five strengths in the emulator (13 -> 4 to 9, 22 -> 29, 30 -> ~60, 35 -> 88 to 90, 72 -> 603) and both bosses were fought on the WITHDRAWN candidate; the owner beat each there. This image is not yet re-checked in game. OWNER-LOCKED values, including Hercule's strength 40 whose bite is arithmetic over one measured point | `FRIEND_V3_RELEASE3.md`; `tools/research/build_friend_v3_release3.py`; `tools/research/apply_friend_v3_boss_retune.py`; `tools/research/apply_friend_v3_behaviour_profile.py`; `tools/research/apply_friend_v3_dialogue_text.py`; `tests/unit/test_friend_v3_boss_profile.py` | P1 | none: shipped | E |
| A24 | release 4, NOT STARTED: interior double spaces left by the rename pass | **MEASURED, NOT ATTEMPTED AGAIN.** 349 interior runs of two or more spaces over 238 records, against 24 records in the canonical ROM (byte coordinates; earlier figures of 424 over 212 were measured with windows scaled by the two-byte unit a second time, the B3 defect). 147 runs are covered by exactly one live record; 202 by two or more, because the containers are chain-shared and records cover each other. An in-place pass was built and run, then discarded: it collapsed 118 runs and the measured total barely moved, because each payback space lands inside a covering record and re-creates a run | measured with `build/fv3wt001/measure_run_coverage.py` and `build/fv3wt001/count_double_spaces.py`, both now in byte coordinates; the failed pass is pitfall P-023, and its guards (payback only from a record's own trailing pad, span must lie inside the payload, non-space characters must not change) are pitfalls P-021 and P-022 | `FRIEND_V3_RELEASE3.md` section 5 | P2 | a container rebuild that rewrites every handle word, so records can be re-laid out instead of edited in place | C |



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
| C1 | Dabura replaced by Broly | **DELIVERED as Release 4A.** Image `a21c1e27f7b4f04cbe6952d70eb102b350adac04e6eaba106fa10e2b90a55021` (10,170,720 bytes: the base plus 738 appended bytes), cut from the shipped release 3.1 `f5c9648b`, reproduced twice byte-identically. Sprite ids 73 and 98 each point at a COPY of Broly's own definition, appended, filled so that every slot the original definition occupied is non-empty - the donor leaves slot 12 (the Heaven actor's scripted animation) and slot 22 empty - with shorter donor animations padded to the original frame counts. The placed sites and the appearance records KEEP their retail ids, because scripts find an actor by definition pointer and a site moved to the donor id would carry the shared definition while the scripts resolve the copies: the Heaven actor's resource 490 (state 12) and the ship scene's resource 337 (natives 71/65) must find the actors they target. The two FD55 fights take the donor's stat selector 10, the appearances take his portrait, and text slot 1024 reads Broly. 17 bytes change inside the base. No enemy stat record, behaviour table, placement descriptor, script payload or dialogue record is touched. The Heaven form is included by owner decision; the 31 dialogue records naming Dabura are unchanged and the owner is reworking the wording; description slot 1025 still names him | ROM-VERIFIED: an independent verifier walks both script corpora itself (226 native-53 spawn sites, 121 state calls, 236 type-0 and 141 type-4 records), derives its own field set from the canonical ROM, models the actor lookup (a script target id must resolve to the same definition a placed or spawned actor carries) and fails on any byte outside the set. RUNTIME: pending, the owner plays to Heaven and the ship scene | `tools/research/build_friend_v4_broly.py`; `tools/research/verify_friend_v4_broly.py`; `tools/research/definition_copy.py`; `tools/research/script_spawns.py`; `tests/unit/test_friend_v4_broly.py` | P1 | runtime check, then review **STATUS: OPEN ITEMS, DEFERRED BY THE OWNER (2026-10-10).** (1) The owner reports that in the zoomed-out story scene Dabura is STILL DRAWN as Dabura. Measured in that scene by the release-4A observer: its actors are sprite ids 258 Supreme Kai, 158 Kibito, 222 Piccolo, 166 Krillin plus two party slots, and NEITHER 73 nor 98 is built there, so the figure is not drawn from either Dabura definition; retail has exactly two Dabura definitions and each is named by exactly one word (its own character-table entry), so no path bypasses the table either. The remaining explanation is map graphics (a prop baked into the map) and it is NOT yet established. (2) Actors built BEFORE a savestate loads are invisible to the observer: the resolver fires only on construction and the animation selector only on a state change, so a standing actor appears in neither channel; the draw-path channel added for this (frame reader 0x0800EF38) fires only when a frame index changes, and a one-shot RAM hunt for definition pointers was prepared but not run. (3) The Heaven actor (map 451, sprite 98, its scripted index 12) was never reached in a runtime session. Runtime evidence: an actor using copy 73 played animations 3 and 20, both non-null. The log does NOT say which actor that was, nor that those slots are the padded ones. The probe's 'mode-5 lookups' are NOT evidence of actor matching - every such line logged the same r0, a constant IWRAM address (0x03001C4C), so the lookup channel is UNPROVEN at runtime. | E |
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
5. A12: the Idasa and Uub lines are located and already read correctly; decide the wealth line
   (Idasa/Uub record section 5) and the two characters named Uub (section 6).
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
| A25 | release 3.1, on top of release 3: retail Videl's actor renamed to Lazuli | **DELIVERED.** Image `b8ee65657986d05d57911ade9ce4b2bf9f216811b874756aec5de8df06351dd5` (10,169,986 bytes), cut from release 3 `521bd0fa`, reproduced twice byte-identically. 34 dialogue records copied into the selector-7 container with that container's payload carried forward as a prefix, 35 handle words rewritten, and 3 text-table slots (138, 172, 1066) relocated. The occurrence test is the approval: this image displays "Videl" on two different actors, so only occurrences where the CANONICAL ROM says Videl are renamed; where it says Goten they stay | ROM-VERIFIED: every container diffed in byte coordinates shows 0 differing records in selectors 0 to 6 and the live-handle drops sum to exactly 34; all 1,534 text slots compared, exactly 3 differ; the carried prefix keeps every release-2 and 2.1 handle inside the declared size; 2 focused tests and the identity asserted by the builder; two independent builds identical. NOT runtime-checked | `tools/research/build_friend_v3_release31.py`; `tools/research/friend_v3_text_approvals.py`; `tests/unit/test_friend_v3_character_rename.py` | P1 | owner to load the image; 57 records and 12 slots left by the retail test, 3 records listed for the owner | E |
| F1 | dialogue speaker grouping for the text tool: the portrait operand | **DELIVERED as research.** The record word is 8 bytes with the portrait operand at `+0x03` (handler `+0x02` into the table at `0x080728AC`, handle `+0x04`), read by the box constructor at `0x080122A6`. Three meanings from the consumer's own branches: `0` and `7` = NO portrait at all (no default, no fallback); `1..6` = the party/save path (EWRAM `0x03001068`, party table `0x086B82EC`), so the character depends on the player's save and is not statically resolvable; `8` and above index the portrait array `0x086F393C` with no clamp. The engine never maps an operand to a character: the join is by value against an appearance record's `+0x08`, in tooling. The speaker is NOT in the record: the VM supplies only box geometry and a bytecode descriptor, so a record's only identity is its portrait. Census of 2,221 dialogue records: no portrait 229 (10%), party 431 (19%), array 1,561 (70%); top characters Babidi 180, Super Buu 147, Goku 134, Piccolo 111, Vegeta 106. Some operands own no appearance record at all (58 -> 55 records, 28 -> 30, 56 -> 17) | ROM-VERIFIED: the consumer's four branches decoded instruction by instruction; counts reproduced by `tools/research/dialogue_portrait_census.py` over 1,565 record lists and 8,904 records, every one word-referenced. Chapters are text only (slots 1450..1473) with no chapter table and no map-to-chapter field, so map order is the only structural order | `tools/research/dialogue_portrait_census.py`; `tests/unit/test_dialogue_portrait_census.py`; K-017; K-018 | P2 | the text tool consumes it | E |


Follow-ups recorded by the 2026-10-11 review of `96073aaa`, each one line, not fixed yet:
- N1 the verifier's lookup model is existence-only (spawn targets match themselves, natives 71/65 are never walked), so it would not have caught the 73 half of the round-3 defect; check 1 covers that regression instead.
- N4 the probe's ACTOR_LOOKUP channel reads an r0 that is a constant IWRAM address, so it cannot answer its stated question; the committed probe also has more channels than the version that produced the shipped log.
- N5 `dialogue_preview.py --fit` compares the render against itself instead of against the capture, and `split_units` claims to recognise control units but maps only `ord`.
- N6 `dialogue_font.py:render_glyphs` raises IndexError on its first inked glyph and is unused.
- N7 the new research tools read any image without an identity check and write `--out/--json` without a source-alias refusal, so an operator error could clobber an input.
- N8 line endings: `test_friend_v4_broly.py` was converted wholesale to CRLF and the new `dialogue_*.py`, `test_dialogue_portrait_census.py` and the probe were added in CRLF; `git diff --check` flags each one.
| F4 | dialogue font and box: extraction plus a reference renderer for the text tool preview | **IN PROGRESS on branch `ticket/dialogue-preview-validation` cut from the frozen `96073aaa`.** The font is extracted and proven (`tools/research/dialogue_font.py` + 6 tests): the 12-byte descriptor at file `0x6EE6C` names the table at `0x6E05C`; a record is `u16 width` plus `width+1` u16 columns, column k is pixel column k, bit r of a column is row r from the top, advance = width + 1, 224 records of which 150 put ink, 74 are blank and 32 codes have no record. The box surface is proven by runtime: the container at `0x71758` matches a native capture at offset (8,8) with 9,723 of 10,240 pixels identical. RENDERER: `tools/research/dialogue_preview.py` draws a line over that surface; `tools/research/dialogue_validate.py` locates the box in a capture, extracts the engine's ink pixels and matches a corpus line to them; `tools/research/dialogue_compare.py` is the single-capture comparator. LAYOUT, fitted from captures: origin (8,3), line spacing 14, ink = OBJ palette index 2 (white), and the WRAP WIDTH DEPENDS ON THE BOX STYLE - 108 pixels with a portrait on screen, 132 without, both exact to zero disagreement. VALIDATION: 17 native captures; one booked pixel-exact before the wrap sweep, and the sweep is re-running over all 17 (the owner asked for ten varied lines) | ROM-VERIFIED for the font and the surface; capture-fitted for the layout: 477 of 477 ink pixels with zero missed and zero extra on two captures with different wrap widths. NOT yet the ten-variant set: multi-page and a renamed line are not confirmed captured | `tools/research/dialogue_font.py`; `tools/research/dialogue_preview.py`; `tools/research/dialogue_validate.py`; `tests/unit/test_dialogue_font.py`; K-019; T-017; T-018 | P2 | the text tool preview consumes it; the wrap-by-style rule needs one more capture of each style to be certain | E |
