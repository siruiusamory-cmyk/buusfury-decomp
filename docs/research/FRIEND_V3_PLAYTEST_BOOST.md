# FRIEND-V3-PLAYTEST-BOOST-001: consolidated build record, modification tracker and playtest plan

**Ticket:** FRIEND-V3-PLAYTEST-BOOST-001, under mission `FRIEND-V3-PLAYTEST-001`.
**Baseline:** live `origin/master` `1b02221732d7b76d38fd9e35d731e9f3317da9a4`, re-measured
before the worktree was created. Worktree: a dedicated ticket worktree beside the primary
checkout, on branch `ticket/friend-v3-playtest-boost-001`.
**Status:** CLOSED. Built, reproduced, independently reviewed and merged as true merges
(MR !170, `a6e4aba2`; MR !176, `372bb3aa`), with master CI green. The human campaign
playthrough is outstanding. Section 4 is the authoritative tracker for the whole friend
image, not only this ticket.

Nothing here is a claim about retail behaviour. Every figure below was produced by a command
recorded in section 2 or a hash recorded in section 1.

## 1. The consolidated artifact

| | |
| --- | --- |
| image | `build/fv3boost001/out/v3-playtest-boost.gba` (ignored, not tracked) |
| SHA-256 | `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c` |
| bytes | 10,140,972 |
| manifest | `build/fv3boost001/out/v3-playtest-boost.manifest.json` |
| changed bytes | 25, all inside the character base-stat table `0x006FDA4C..0x006FDA9D` |
| superseded | `6d7a56c6f96e83cf6e5b86a1ab188d40ab88247c6ffa274f09531e03f609414e`, the first consolidated baseline, retired because its hp and ep edit read as negative in game. See `docs/research/FRIEND_V3_PLAYTEST_BOOST_COMPLETION.md` |
| canonical ROM | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, unchanged |

There is one current final image. No competing variant was built.

## 2. Reproducible build, with the provenance chain

Inputs are the worktree's own copies under `build/fv3boost001/inputs/` and
`build/fv3boost001/staging/`, each verified against the digest below. The canonical ROM store
is not a write target and is not read through a junction; no input is hardlinked.

| stage | input digest | output digest |
| --- | --- | --- |
| rename base `v3-safe.gba` | `b0de6ddffe53961bcade893107b7f9a8004d684b919552480ca688207e8f56d5` | - |
| 1 complete map (492 rows) | - | map artifact, not a published digest |
| 2 splice | `b0de6ddf...` | `bf16dfd3...` |
| 3 token engine | `bf16dfd3...` | `cec009d9...` |
| 4 content-pass spans | `cec009d9...` | `d564ef8a...` |
| 5 complete text pass | `d564ef8a...` | `20f2c14066648bb7ef2fad60ffc8d904121e8cd4f1c1fe171bfd80ca8551746c` |
| 6 toolkit graphics swap | `20f2c140...` | `ef939dcd8c600fe52044df08d930d9dff1b1ceed52698aff8b21c8eef15b38b4` |
| 7 toolkit dialogue swap | `ef939dcd...` | `a4c12a95818cab2781165658d25f2463bc6fe0f87040620a7c89f0034c5b49db` |
| 8 playtest boost, first form | `a4c12a95...` | `6d7a56c6f96e83cf6e5b86a1ab188d40ab88247c6ffa274f09531e03f609414e`, superseded: its hp and ep edit read as negative in game |
| 9 playtest boost, corrected | `a4c12a95...` | `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c`, this build's current image |

Steps 1 to 5 are the merged complete-text-pass chain. Step 6 and 7 are the merged
character-swap toolkit, invoked as
`python -m tools.webfoot.character_swap --image IN --expect-sha256 DIGEST --spec SPEC --out OUT`
with `tools/presets/tulma-graphics-spec.json`
(`b922b0cba860d1b7e0911e8f73187729a81cf25de33f18dd22300fb05cfee731`) and
`tools/presets/tulma-dialogue-spec.json`
(`a00723db38b4956f0620e71f259256bb4610cc01f4df7f59d41b22372655a227`). Asset names in a spec
resolve against the spec's own directory, so the run copies the spec beside the four PNGs
under ignored `build/`. The four art inputs are `stand.png`
`6563198bf83a8b7144498f2f9c1238693dad4ba30e9e9ddf24af31b7afedc245`, `walk.png`
`d2acc67ef31cb5bd986615f3143e9e5db31f7d0b2d0b826ea2afcb7ff5123229`, `arms_up.png`
`859cbfbb5137ae914ae4af7a87429d952fea02fd0bfc5b1573c254bff723a429`, `portrait.png`
`5f920a3a713603f287488ccc9c3b83c06488fbb632ba8a17c9204f1392bf161c`.

**Steps 6, 7 and 8 were re-run here, not assumed.** Re-running the two swaps from the
verified `20f2c140` foundation produced `ef939dcd` and then `a4c12a95` byte for byte, and
re-running the boost on that fresh output reproduced the first form's digest, and after the hp and ep fields were dropped it reproduces `acd98c2a`. That is the integration
provenance check the ticket asks for: the selected foundation demonstrably contains the text
pass and the Tulma work, because the toolkit regenerates it.

Step 8 is the only new code:

```text
python tools/research/build_friend_v3_playtest_boost.py \
  --image build/fv3boost001/staging/foundation-a4c12a95.gba \
  --expect-sha256 a4c12a95818cab2781165658d25f2463bc6fe0f87040620a7c89f0034c5b49db \
  --out build/fv3boost001/out/v3-playtest-boost.gba \
  --manifest build/fv3boost001/out/v3-playtest-boost.manifest.json
```

`build/fv3boost001/build.ps1` runs that step with a digest assertion before and after, and
re-hashes the canonical copy at both ends.

### What the boost changes

Character base-stat records are 9 records of 0x12 bytes at `0x006FDA4C`; the layout is
`tools/webfoot/formats/stat_tables.py:188-220` (level u8, pad, hp u16, ep u16, strength,
power, endurance, speed, appearance id, technique count, 6 technique bytes). Records 0..4 are
set to the widest value each field's own mode uses, **except hp and ep, which are left at
the foundation's own values**:

| field | offset | value | basis |
| --- | --- | --- | --- |
| level | +0x00 | 200 | the game's XP ceiling, not the u8 bound: `cmp r6,#0xc8` before the threshold lookup, reported at `tools/webfoot/stats.py:71-75` from `docs/research/P010_ENEMY_DEATH_AND_REWARDS.md:393`. The encoding is a u8 and would accept 255 |
| hp, ep | +0x02, +0x04 | unchanged | both are u16 and the engine reads them as signed. Writing 0xFFFF made a live character read HP -1 and EP -5 with energy attacks disabled, observed on a cold boot; see the completion record beside this one |
| strength, power, endurance, speed | +0x06..+0x09 | 255 each | u8 fields; 255 reads correctly in game |

Records 0..4 are set, and records 5..8 are deliberately untouched. Two separate things are
known about identity, and they must not be confused:

- **The record order** `0=Goku, 1=Gohan, 2=Goten, 3=Trunks, 4=Vegeta, 5=Gotenks, 6=Vegito,
  7=Gogeta, 8=Videl`, with a per-character block stride of `0x68`, comes from the external Data
  Crystal RAM map. It is an external source, not a measurement of this image. It agrees with
  `tools/webfoot/formats/stat_tables.py:77` calling all nine records playable, and it puts
  Videl in the ninth record where `BASE_STAT_NAMES` says Hercule.
- **The status screen agrees with the order rather than contradicting it.** On a cold boot of
  the first consolidated image, the boosted character was displayed as YAMCHA, and the friend
  build renames the name table itself: index 116 "Goku" became "Yamcha", 117 "SS Yamcha", 118
  "SS3 Yamcha", and 123 "Gohan" became "Krillin". So a YAMCHA screen is what this build calls
  the record labelled Goku, and it is why the boost is described by record index rather than by
  character name.

The consequence for the playtest remains: the record order is externally sourced, and the
correspondence between a record index and the on-screen name is this build's own renaming, so
a named character in a report must be tracked by index. See the completion record beside this
one for the screen and for how to settle the index directly.
The builder refuses a byte that its own field table does not account for. That catches a write
outside the table. It cannot catch a wrong offset or width inside the table, because the table
also drives the writes; those were checked by hand against `decode_base_stat_record` and by
the reviewer, not by the assertion.

## 3. Verification performed

| gate | result |
| --- | --- |
| `tests/unit/test_friend_v3_playtest_boost.py` | **10 passed**, including a test that fails if the cancelled Bandana hook regains a caller |
| related unit suites (`test_character_swap`, `test_mgba_capture`, `test_project_safety`, `test_mgba_identity_gate`, `test_mgba_launch_coverage`) | **175 passed**; captured to ignored `build/review/related-suites.log` |
| changed-byte census on the delivered image | 25 bytes, all in `0x006FDA4C..0x006FDA9D`, length unchanged |
| foundation re-run through the toolkit | reproduces `ef939dcd` then `a4c12a95` byte for byte |
| boost re-run on the reproduced foundation | reproduces `acd98c2a` byte for byte, twice, identical hashes |
| cancelled-hook exclusion | bytes at `0x08004892` (`20 1c db e7`) and the whole trampoline run at `0x083C22FC` are byte-identical to the foundation; no injection is present |
| canonical ROM digest after every run | `940ad5f0...` unchanged |

Runtime smoke test on the delivered image, isolated mGBA, fresh 8192-byte save, operator-confirmed.
The run directory was created by hand, so this is a recorded observation without a manifest or ROM
copy beside it; the reproducible form is the build plus the launcher in section 2.

| check | result |
| --- | --- |
| cold boot | reaches the title screen |
| title screen artwork | correct |
| menu selection and frame rate | **72.7 fps**, normal; the arrow glitch belongs to the cancelled hook, and the control foundation image is clean |
| New Game | begins, gameplay reachable |
| progression | no crash and no softlock observed in the smoke window; 679 observer frames, 15 distinct PCs, PC inside GBA ROM |
| equipment at `0x0300114C` | **0** on a fresh save, as expected with the injection cancelled |
| save file | 8192 bytes, valid |
| injected equipment | none |

Still not performed, and not claimed: chapter-by-chapter progression and every in-game check
listed in section 4.4. Independent review and CI were performed at integration (status line).

## 4. The authoritative modification tracker for the whole friend image

This section is the single source of truth for every change made to, planned for, or
cancelled from the customized Buu's Fury image, not only this ticket's. The other
`FRIEND_V3_*` records are the evidence it cites; none of them carries a competing TODO
list. Reconciled 2026-10-10 against master `372bb3aafbc4305c460e11fc4a8b9436cd7565dd`
(MR !176), the friend records under `docs/research/`, the merged tests, and the owner's
recorded decisions.

### 4.0 How to read it

Every row carries an **implementation** state and a separate **verification** state.

| state | meaning |
| --- | --- |
| IMPLEMENTED | the bytes are in `acd98c2a` |
| ROM-VERIFIED | proven by a static read, census or test of the image bytes; says nothing about what the game does |
| RUNTIME-VERIFIED | observed in a running game, with the image and the record named; it covers that scene only |
| PARTIALLY VERIFIED | some of the claim is observed, the rest is static, owner-attested or on an earlier image |
| PLANNED / NOT IMPLEMENTED | intended or proposed, no bytes written |
| BLOCKED | cannot proceed until a named dependency clears |
| OWNER DECISION REQUIRED | waits on the owner; nothing is built until it is decided |
| CANCELLED | withdrawn by the owner; kept for the record |
| DEFERRED TO PLAYTEST | only a human playing the image can settle it |

**Which image a runtime observation was taken on matters.** `acd98c2a` differs from its
foundation `a4c12a95` in 25 bytes, all inside the base-stat table (section 1), and the
earlier images in the chain are diff-confined in the same way, so an observation of text or
art on an earlier image carries forward as ROM-VERIFIED, not as RUNTIME-VERIFIED on this one.

Priority: **P0** blocks or invalidates the first playtest; **P1** needed in the first
playtest round; **P2** next development phase; **P3** latent or later.

Needs: **C** owner creative decision, **E** engineering investigation, **H** human playtest.

### 4.1 Image lineage, every stage that produced `acd98c2a`

| stage | image (SHA-256 prefix, bytes) | what it added | record |
| --- | --- | --- | --- |
| friend's own modded image (third party, before this repository) | `a6f44422`, 9,732,800 | the friend's original customization; its full change list is not recorded in this repository | `FRIEND_V3_STABILITY_PASS.md` section 2 |
| `v3.gba` | `38504057`, 9,740,166 | the image that crashed on map 134 (`F0674DD8`) | same, section 3 |
| `v3-safe.gba`, the rename base | `b0de6ddf`, 9,740,320 | slot 292 composition buffer `0x200` to `0x400`, the crash fix | same, section 3 |
| 451-record rename splice, token engine | `cffdb81e`, then `d401d71c`, 10,132,968 | the operator's private 451-record rename map (`8fc91afc`) carried by two-glyph tokens, so the Kibito scene no longer freezes | `FRIEND_V3_COLD_BOOT_ACCEPTANCE.md` |
| content pass | `b3344a3f`, 10,132,968 | seven menu, biography and Soyman sites | `FRIEND_V3_CONTENT_PASS.md`, MR !152, merge `0bdf1df5` |
| complete text pass | `20f2c140`, 10,133,410 | map 451 to 492 rows; Soyman, Tulma and Chichi rules; 14 in-place and 7 relocated menu sites | `FRIEND_V3_COMPLETE_TEXT_PASS.md`, MR !155 and !156, merges `1a45f494`, `d003ce93` |
| Tulma graphics | `ef939dcd`, 10,140,972 | sprite 41 (22 containers) and portrait slot 17 | `FRIEND_V3_TULMA_GRAPHICS.md`, MR !165, merge `0b3676a7` |
| Tulma dialogue | `a4c12a95`, 10,140,972 | two World Tournament lines, owner-authorized | same, section 9 |
| character-swap toolkit | reproduces `ef939dcd` and `a4c12a95` | stages 6 and 7 become one command | `CHARACTER_SWAP_TOOLKIT.md`, MR !166, merge `1b022217` |
| playtest boost, first form | `6d7a56c6`, RETIRED | hp and ep `0xFFFF`, which read as negative | MR !168, merge `42106cac` |
| **playtest boost, final** | **`acd98c2a`**, 10,140,972 | records 0 to 4: level 200, STR/POW/END/SPD 255 | MR !170 (`a6e4aba2`) and MR !176 (`372bb3aa`) |

The 451-record map, the rename base and every image are private inputs and are not in the
repository; the digests above are what a holder of them checks against.

### 4.2 Displayed identities

A report must name the record, not the on-screen name, because this build renames the name
table itself (completion record, section 0e).

| retail character | displays as | evidence |
| --- | --- | --- |
| Goku (and `Kakarot`) | Yamcha | name-table index 116 reads `Yamcha`; status screen `YAMCHA LVL 200` |
| Gohan | Krillin | index 123; cold-boot screenshot `Kibito will take care of Krillin` where retail reads `Gohan` |
| Krillin | Goku | text-pass audit: retail `Goku and Krillin` displays as `Yamcha and Goku` |
| Goten | Videl | biography slot 1191 `Videl is the son of Yamcha and Bulma` |
| Trunks | Uub | biography slot 1193 |
| Vegeta | Tien | biography slot 1195; chapter 5 title `Majin Tien` |
| Chi-Chi | Bulma | text-pass rule: retail `Chi-Chi` and `Chichi` display as `Bulma` |
| retail Bulma | Tulma | slot 1032; dialogue rule; sprite 41 and portrait 17 art |
| Android 18 | Chi-Chi | text-pass section 5, item 7 |
| Yamcha | Gohan | owner handoff record only; not measured here |
| Gogeta | Yamien | menu slots 136, 165, 181, 1304, 1305 |
| Vegito | Tiencha | menu slots 134, 135, 164, 180, 1306, 1307 |
| Saiyaman | Soyman | 20 spoken occurrences, slots 122, 1453, 603, 1346, 1347 |
| Piccolo, Hercule | unchanged | owner decision |

Not established: what the retail Videl, Uub and Tien records display as, and whether base-stat
record 8 is Videl (external RAM map) or Hercule (`BASE_STAT_NAMES`).

### 4.3 Every item, by area

**A. Names, text and dialogue**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | character rename across dialogue, menus, scans, chapters | IMPLEMENTED | PARTIALLY VERIFIED: 868 occurrences, 0 unresolved (ROM); renamed lines seen on cold boot of `d401d71c` and on a savestate run of `20f2c140`; not observed on `acd98c2a` | text-pass section 4; cold-boot section 4 | P1 | read names on every scene during the playtest; report any retail name by record | H |
| A2 | `Saiyaman` to `Soyman`, spoken and menu | IMPLEMENTED | PARTIALLY VERIFIED: 20 to 0 by stream count; one line seen at runtime on `20f2c140` | text-pass sections 3.1, 6 | P1 | check chapter 2 (`Great Soyman`) in play | H |
| A3 | retail `Bulma` displays `Tulma` (18 spoken, 9 menu sites) | IMPLEMENTED | ROM-VERIFIED | text-pass sections 3.1, 3.3 | P1 | check quest log and Capsule Corp scenes in play | H |
| A4 | `Gogeta` to `Yamien`, `Vegito` to `Tiencha` in the menu pool | IMPLEMENTED | ROM-VERIFIED; no runtime observation | text-pass section 3.3 | P1 | check every fusion moment and its menu | H |
| A5 | four spoken records read `Tulma` where the content-pass plan said `Chi-Chi` (`1:26476:306`, `4:10050:156`, `4:18714:142`, `5:42592:1086`) | IMPLEMENTED as `Tulma` | ROM-VERIFIED | text-pass section 5, item 1 | P2 | owner confirms `Tulma` or picks one of the three `Chi-Chi` routes in content-pass section 4 | C |
| A6 | slot 1347 ability line reads `back into Krillin`, reversing the content pass's `Goku` | IMPLEMENTED | ROM-VERIFIED | text-pass section 3.4 and section 5, item 3 | P2 | owner confirms | C |
| A7 | slot 1193 `Uub is the son of Tien and Tulma`, which implies a marriage Tulma's biography omits | IMPLEMENTED as retail-derived | ROM-VERIFIED | text-pass section 5, item 2 | P2 | owner keeps it or approves a one-site rewording | C |
| A8 | one spoken `Great Soy Man`, spaced, retail text | not changed | ROM-VERIFIED | text-pass section 5, item 8 | P3 | owner keeps retail spacing or approves `Great Soyman` | C |
| A9 | chapter and saga titles | IMPLEMENTED for chapter 2 `Great Soyman` and chapter 5 `Majin Tien`; no other title text recorded | ROM-VERIFIED | text-pass section 5, item 5 | P3 | none unless the owner supplies new title text | C |
| A10 | credits line `Cale Aaron Cymek` | IMPLEMENTED before this repository | ROM-VERIFIED at file `0x949FFE`; not seen at runtime | text-pass section 7 | P1 | read the end credits | H |
| A11 | five orphaned retail strings with no table entry or reference | left in place by decision | ROM-VERIFIED unreachable by the checks applied | text-pass section 4 | P3 | none; reopen only if one appears on screen | none |
| A12 | Idasa and Uub interaction dialogue | PLANNED / NOT IMPLEMENTED | none: the text is recorded nowhere | text-pass section 5, item 4; Idasa is pool slot 1016 | P2 | owner writes the lines; then one dialogue edit with the merged toolkit | C, then E |

**B. Tulma**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | Tulma actor art: sprite 41, all 22 containers, supplied art | IMPLEMENTED | RUNTIME-VERIFIED on map 134, session `tulma001-encounter-6`, on `aec5aa9f`, and the object-tile bytes on `ef939dcd`; carried to `acd98c2a` by diff confinement | Tulma record sections 4 to 6 | P1 | observe her on this image in the tournament scene | H |
| B2 | Tulma portrait, slot 17 | IMPLEMENTED | RUNTIME-VERIFIED, session `tulma001-encounter-8` on `ef939dcd` | Tulma record section 6 | P1 | same scene | H |
| B3 | blonde appearance | IMPLEMENTED by the supplied recoloured art (portrait hair index 187 to 200). Supersedes text-pass section 5, item 10 and content-pass section 5, item 2, which predate MR !165. A separate appearance record is not needed, because the displayed `Bulma` is retail Chi-Chi on sprite 66 | RUNTIME-VERIFIED as drawn; final look not accepted | Tulma record sections 2, 3 | P1 | owner visual acceptance in play | C, H |
| B4 | two rewritten World Tournament lines, slots 60182 and 60294 | IMPLEMENTED | PARTIALLY VERIFIED: exhaustive 2,814-record compare (ROM); on screen owner-attested on `a4c12a95`, no capture | Tulma record section 9 | P1 | capture the scene on `acd98c2a` | H |
| B5 | Tulma biography, slots 1032 and 1033: identical twin, daughter of Dr. and Mrs. Brief, no marriage line | IMPLEMENTED | ROM-VERIFIED; scan screen not seen | content-pass section 2 | P1 | open her scan in play | H |
| B6 | "Tulma's scripted encounter" | the tournament registration scene is the only Tulma scene established | RUNTIME-VERIFIED on earlier images only (B1, B2, B4). The playtest guide's statement that no scripted encounter was observed is inaccurate for earlier images and is corrected | Tulma record sections 6, 9 | P1 | reach the scene on `acd98c2a`; any other Tulma scene is unknown and is reported if met | H |
| B7 | enclosing scene views padded by 15 units after the B4 rewrite | as written | unknown whether ever shown as continuous text | Tulma record section 9 | P2 | watch for stray spaces in that scene | H |

**C. Bosses, difficulty and combat**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | Dabura replaced by Broly | PLANNED / NOT IMPLEMENTED; OWNER DECISION REQUIRED | none | proposal in the owner's handoff record only; Broly exists as an actor (appearance records 16 and 17) | P2 | owner approves or drops; then a research ticket for the encounter's placement and stat records | C, then E |
| C2 | Spopovich replaced by Android #13 or Perfect Cell | OWNER DECISION REQUIRED | none | both names exist in game text (Android #13 at slots 1050 to 1057); whether Cell has a usable actor is not established | P2 | owner picks a target; then check the actor exists | C, then E |
| C3 | tougher Hercule encounter | OWNER DECISION REQUIRED | none | lever is his enemy stat record, reached through the appearance record naming him; the survey values were not archived and must be re-derived; only hp has measured consumption evidence; the enemy-stat randomizer writes the same record | P2 | owner sets the intent; engineering re-derives the record | C, then E |
| C4 | tougher Olibu encounter | OWNER DECISION REQUIRED | none | proposal in the owner's handoff record only; no lever located | P2 | owner confirms; then locate the record | C, then E |
| C5 | balancing beyond the playtest boosts | owner-reserved | none | `FRIEND-V3-PLAYTEST-001` charter | P3 | none until requested | C |

**D. Biographies**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | six proposed scan-biography rewrites (slots 1059, 1187, 1189, 1191, 1193, 1195) | PLANNED / NOT IMPLEMENTED | wording measured to fit | content-pass plan section 7; text-pass section 5, item 7 judges them unnecessary once Tulma and Bulma split | P2 | owner approves, rejects or rewrites | C |
| D2 | slot 1065 retail grammar defect `Tien was once a rival of Yamcha is now a loyal Z-Fighter` | not changed | ROM-VERIFIED | text-pass section 5, item 7 | P3 | owner approves the one-word repair or keeps retail | C |
| D3 | slot 1043, ambiguous under the renaming | not changed | ROM-VERIFIED | content-pass section 5, item 3 | P3 | owner reads it | C |
| D4 | new biography content | none recorded | none | charter `owner_reserved` | P3 | none until supplied | C |

**E. Visuals and cutscenes**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | hospital Senzu cutscene shows Videl in bed where retail shows Android 18 standing | tracked only; no animation change made | not reproduced in this repository | owner handoff record; earlier tracker row | P2 | reproduce and capture on `acd98c2a` and on retail; then the owner decides | H, then E, then C |
| E2 | cutscene sprite persistence workstream | PLANNED / NOT IMPLEMENTED; scope not written | none | named as a separate workstream when the text pass was scoped | P3 | owner states what should change; E1 is the only concrete case known | C |
| E3 | fusion characters keep retail art under renamed text | as retail | none | A4 | P3 | none | none |

**F. Levels and progression**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | bypass level gates where the mechanism is located | NOT IMPLEMENTED. No gate search is recorded; the records only state that nothing measured showed a gate that level 200 fails | none | charter `in_scope`; inventory section 6 | P1 | playtest records every gate met (chapter, place, condition); a located gate becomes an engineering item | H, then E |
| F2 | level cap 200 is a code constant (`cmp r6,#0xc8`) | unchanged by decision | ROM-VERIFIED | section 2 | P3 | none | none |
| F3 | starting at level 200 with `NXT LVL: 0` | IMPLEMENTED | status screen seen on the `6d7a56c6` image family only; that the game handles the state is not shown | completion record section 0b | P0 | check the first stat screen and the first experience gain | H |

**G. Statistics and abilities**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G1 | records 0 to 4 at level 200, STR/POW/END/SPD 255 | IMPLEMENTED | PARTIALLY VERIFIED: 25-byte census (ROM); 255s and level 200 read on the status screen of the `6d7a56c6` family; on `acd98c2a` only a 60-second boot-to-New-Game smoke | sections 1, 3; completion record 0b | P0 | read the stat screen of each boosted character on `acd98c2a` | H |
| G2 | hp and ep left at foundation values (owner ruling after `0xFFFF` read as negative) | IMPLEMENTED | ROM-VERIFIED and pinned by a unit test; not observed at runtime on `acd98c2a` | completion record 0b | P0 | read hp and ep; fire an energy attack | H |
| G3 | energy-consuming attacks work | as retail | DEFERRED TO PLAYTEST; they failed on `6d7a56c6` | completion record 0b | P0 | use one per boosted character | H |
| G4 | character switching keeps each character's stats | as retail | DEFERRED TO PLAYTEST; in neither checklist before this revision | none | P1 | switch to each of the five boosted characters and back | H |
| G5 | records 5 to 8 (fusions and record 8) untouched | by design | ROM-VERIFIED | section 2 | P3 | a weaker fusion is expected, not a defect | none |
| G6 | techniques unchanged | as retail | ROM-VERIFIED | section 2 | P3 | none | none |

**H. Inventory and equipment**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | Bandana in the starting inventory | **CANCELLED BY OWNER.** The Bandana is obtained through normal gameplay. Do not reopen | the excluded hook is byte-compared absent and a unit test fails if it regains a caller | trampoline record; section 3 | none | none | none |
| H2 | starting inventory is retail: 2 Miso Soup, equipment count 0 | as retail | RUNTIME-VERIFIED on a real New Game | inventory record section 3 | P3 | none | none |
| H3 | items, shops and equipment otherwise retail | as retail | DEFERRED TO PLAYTEST | section 6 step 3 | P1 | buy and use an item; equip one | H |

**I. Save and load**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I1 | EEPROM save, 8,192 bytes | as retail | the smoke run wrote a valid 8,192-byte save | section 3 | P1 | save, quit and reload; progress, stats and inventory survive | H |
| I2 | a save written by another image restores old stats | known limit | documented | section 5, item 5 | P1 | start from an empty save only | H |

**J. Stability and engine limits**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J1 | `F0674DD8` crash on map 134 (slot 292 buffer) | fixed in `v3-safe` | RUNTIME-VERIFIED: two hand-driven runs on `d401d71c`; frame-budget audit finds no slot over budget | stability record sections 3, 4, 6 | P3 | none | none |
| J2 | Kibito-scene freeze from a grown rename | fixed by the token engine | RUNTIME-VERIFIED on cold boot: 13,440 frames on `d401d71c`, 15,780 on `b3344a3f` | cold-boot and content-pass records | P3 | none | none |
| J3 | zero slack on all 297 composition buffers | LATENT | ROM-VERIFIED | stability record section 7.1 | P3 | any future frame resize must enlarge its slot's buffer | E |
| J4 | 275,033 bytes over the targets of 99 canonical references | LATENT; no consumer found | ROM-VERIFIED | stability record section 7.2 | P2 | report any crash with its scene; compare against retail | H |
| J5 | late-game stability | not claimed | DEFERRED TO PLAYTEST | section 5, item 3 | P1 | full campaign | H |

**K. Playtest coverage**

| id | item | implementation | verification | evidence | pri | next action | needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| K1 | chapters 1 to 12 in order | n/a | DEFERRED TO PLAYTEST; none walked | guide section 6 | P1 | play and tick each chapter | H |
| K2 | chapter-specific checkpoints in the playtest guide | NOT PROVIDED: the guide lists chapter names only, with no per-chapter event, boss or checkpoint | n/a | guide section 6 | P1 | add per-chapter checkpoints sourced from the cited walkthrough, documentation only | E |
| K3 | full campaign completion | n/a | DEFERRED TO PLAYTEST | section 6 | P1 | the playthrough that closes A1 to J5 | H |

**L. Tooling debt that touches this image**

| id | item | state | evidence | pri |
| --- | --- | --- | --- | --- |
| L1 | four span-writer refusals have no unit test | debt, guards exercised by hand | content-pass section 3 | P3 |
| L2 | `test_graphics_rom.py::test_verified_graphics_pointers_join_the_common_reference_graph` red at its baseline (11,304 against 11,302) | disclosed, not this track's | Tulma record section 5, item 9 | P3 |
| L3 | the 60-second smoke left no replayable run directory | recorded observation only | section 5, item 1 | P3 |

### 4.4 The BOOST acceptance checks, demonstrated versus deferred

| check | demonstrated | deferred to the human playtest |
| --- | --- | --- |
| level 200 and boosted stats on the in-game stat screen | on the `6d7a56c6` family's status screen; static census on `acd98c2a` | the stat screen on `acd98c2a` (G1, F3) |
| valid hp and ep, working energy attacks | bytes pinned by test | on-screen values and an energy attack (G2, G3) |
| character switching and stat persistence | nothing | all of it (G4) |
| save and reload | a valid 8,192-byte save was written | reload with progress intact (I1) |
| representative level-gate behaviour | nothing; no gate search recorded | every gate met (F1) |
| Tulma's scripted encounter | art, portrait and lines on earlier images (B1, B2, B4) | the scene on `acd98c2a` (B6) |
| chapter progression and late-game stability | boot to New Game, 72.7 fps, no crash in the smoke window | chapters 1 to 12 (K1, J5) |
| full campaign completion | nothing | all of it (K3) |

### 4.5 Original requirements omitted, contradicted or never verified

The `FRIEND-V3-PLAYTEST-001` charter's `in_scope`, compared with what landed:

| requirement | outcome |
| --- | --- |
| maximum valid level and statistics for the five playable characters | delivered for level and four stats; **hp and ep deliberately not maximised** by owner ruling (G2) |
| bypass character-level restrictions where the mechanism is located; record a gate that cannot be located | **not done and not recorded as searched** (F1) |
| one standard Bandana in the starting inventory if a ROM-initiated mechanism is located | **CANCELLED BY OWNER** (H1) |
| one authoritative modification and TODO tracker | delivered by this section; the earlier section 4 covered this ticket only |
| one full-campaign speedrun and stability checklist | section 6 and the guide exist; **no chapter-specific checkpoints** (K2); character switching and save-reload were missing and are added |
| independent review of a frozen candidate, CI, integration | done: MR !170 and MR !176 merged as true merges |
| targeted runtime verification | a 60-second smoke on `acd98c2a`; every in-game check in 4.4 is outstanding |

Contradictions corrected in this revision: the playtest guide said Krillin, Gohan, Goten, Trunks
and Vegeta keep their names and that Chi-Chi reads as Tulma (4.2 shows otherwise); it said no
Tulma encounter had been observed (B6); two earlier records said Tulma's blonde art did not
exist (B3); this record's own section 3 said review and CI were not performed.

### 4.6 Owner decisions, separate from engineering

1. A5: confirm `Tulma` in the four spoken records, or choose a `Chi-Chi` route.
2. A6: confirm `back into Krillin` in slot 1347.
3. A7: keep slot 1193 or approve rewording.
4. A8: keep `Great Soy Man` or approve `Great Soyman`.
5. A12: write the Idasa and Uub lines.
6. B3: accept Tulma's final look after seeing it in play.
7. C1 to C4: approve or drop Dabura to Broly, choose Spopovich's replacement, set Hercule's and Olibu's intended difficulty.
8. D1 to D3: approve, reject or rewrite the six biography proposals; slot 1065 repair; slot 1043.
9. E1, E2: decide the hospital scene once it is reproduced; state what cutscene persistence should cover.
10. Any new title, biography or balancing text (A9, D4, C5).

### 4.7 Phases

1. **Playtest round 1 on `acd98c2a`** (now). P0 then P1 rows marked H, guided by section 6 and
   the guide. Bugs go into the tracker with the guide's section 7 fields and a severity.
2. **Triage and fix.** A fix is proposed only for a defect reproduced twice from a fresh save,
   built as a new image from `acd98c2a`, which stays the frozen baseline. Engineering items that
   playtest exposes (F1 gates, E1 reproduction) are scoped here.
3. **Owner text batch.** Once 4.6 items 1 to 5 and 8 are decided, one text and dialogue ticket
   with the merged toolkit, one new image, one review.
4. **Combat and boss workstream** (C1 to C4), only after the owner decides; each starts with a
   research step, because none of the levers is archived.
5. **Cutscene workstream** (E1, E2), after reproduction and an owner decision.
6. **Final campaign playthrough** on the last image, closing K3.

## 5. Limits of this record, stated plainly

1. **The runtime smoke test is a 60-second observation, not a campaign.** It was run on the
   delivered image at the time of writing, from a fresh save, and it reached the title screen and
   a started New Game at 72.7 fps with equipment count 0. It left no ROM copy or manifest under
   `build/fv3boost001/runtime/`, because the run directory was created by hand rather than by the
   launcher's manifest path, so it is a recorded observation rather than a replayable artifact.
   The claim that the party starts at level 200 with maximum stats is a static decode of a
   verified table plus the game's XP ceiling; nothing here shows that a starting level of 200 with
   no experience is a state the game handles. That is why the first checklist step is a
   started-game stat-screen check.
2. **The Bandana is not in this image.** Cancelled by owner; see the tracker row above.
3. **Full-game stability is not claimed.** One human playthrough is required before anything
   stronger than "targeted checks pass" is written here.
4. **The pipeline record above was exercised from `20f2c140` forward.** Steps 1 to 5 carry
   the digest chain published by the merged ticket; they were not re-driven end to end in
   this worktree, and this record says so instead of implying otherwise.
5. **Savestates may not reflect table changes.** Where the game persists absolute stats in
   save data, a save written before the boost can restore old values. The playtest therefore
   starts from a new game or a save whose data is re-derived, and a mid-campaign load that
   shows retail stats is a save-state artifact, not a build defect.
6. **The capsule under test is a 10,140,972-byte image, not the 8 MiB canonical ROM.** Any
   digest check must name this file.

## 6. Full-campaign speedrun and stability checklist

Route: one sitting, no savestate restores except where a crash forces one, logging for each
chapter the entry frame, exit frame, and any freeze. A freeze is a run-ending observation:
note the frame, the last text box, and whether the music continued.

| step | what to check | pass condition |
| --- | --- | --- |
| 0 | pre-flight | the loaded image is `acd98c2a...`; emulator reports `0.11` dev build; no other mGBA process holds TCP 2345 |
| 1 | new game, first stat screen | the boosted party reads **level 200**, with STR, POW, END and SPD at 255, and hp and ep at their ordinary starting values, never negative |
| 2 | first combat encounter | damage lands normally and hp never displays as a negative; no freeze, no graphical glitch in the HUD |
| 3 | first shop and item use | items still buyable and usable; the inventory screen renders the party's techniques unchanged |
| 4 | first quest-gated door or NPC | the gate opens on the same trigger as retail. A gate that requires a level or a specific item is the case this boost does not address: record it, do not route around it silently |
| 5 | each chapter in order | chapter completes; no freeze; the party remains at boosted stats; check the quest log after each chapter |
| 6 | every fusion moment | Gotenks, Vegito and Gogeta still transform and still fight; their records were deliberately left untouched, so a fusion that is *weaker* than its parts is expected and is not a defect |
| 7 | dialogue-heavy scenes | text matches the friend build (Tulma, Great Soyman), no truncated or missing line |
| 8 | scans and biographies | the screens open and read consistently |
| 9 | Dragon Ball and story progression | every collectible and story trigger reached in order; no sequence break |
| 10 | end credits | the credits line `Cale Aaron Cymek` is present and readable |
| 11 | character switching | switch to each of the five boosted characters and back; level and stats persist |
| 12 | save, quit, reload | progress, stats and inventory survive a reload from the save this image wrote |

Regression watch-list for the playthrough, carried from the open risks:
the composition-buffer slack (a crash at a frame boundary in a crowded scene), the tail
window (a crash that reproduces on a retail reference but not here, or the reverse), and any
dialogue that renders as token glyphs rather than letters.

## 7. Closure

Closed by the owner on 2026-10-09 after MR !176. The playthrough result is recorded in
section 4 when it arrives; the ticket does not reopen for it. Future fixes run under
`FRIEND-V3-PLAYTEST-001`, which stays armed for that purpose, each as a new image built
from `acd98c2a`, which remains the frozen baseline.
