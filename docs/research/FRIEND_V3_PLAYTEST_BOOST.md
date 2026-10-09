# FRIEND-V3-PLAYTEST-BOOST-001: consolidated build record, modification tracker and playtest plan

**Ticket:** FRIEND-V3-PLAYTEST-BOOST-001, under mission `FRIEND-V3-PLAYTEST-001`.
**Baseline:** live `origin/master` `1b02221732d7b76d38fd9e35d731e9f3317da9a4`, re-measured
before the worktree was created. Worktree: a dedicated ticket worktree beside the primary
checkout, on branch `ticket/friend-v3-playtest-boost-001`.
**Status:** the boosted image is built, reproduced and unit-tested. Independent review, CI
and the human campaign playthrough are outstanding, and this record says so rather than
claiming them.

Nothing here is a claim about retail behaviour. Every figure below was produced by a command
recorded in section 2 or a hash recorded in section 1.

## 1. The consolidated artifact

| | |
| --- | --- |
| image | `build/fv3boost001/out/v3-playtest-boost.gba` (ignored, not tracked) |
| SHA-256 | `6d7a56c6f96e83cf6e5b86a1ab188d40ab88247c6ffa274f09531e03f609414e` |
| bytes | 10,140,972 |
| manifest | `build/fv3boost001/out/v3-playtest-boost.manifest.json` |
| changed bytes | 45, all inside the character base-stat table `0x006FDA4C..0x006FDA9D` |
| canonical ROM | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, unchanged |

There is exactly one final image. No competing variant was built.

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
| 8 playtest boost | `a4c12a95...` | `6d7a56c6f96e83cf6e5b86a1ab188d40ab88247c6ffa274f09531e03f609414e` |

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
re-running the boost on that fresh output produced `6d7a56c6` again. That is the integration
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
power, endurance, speed, appearance id, technique count, 6 technique bytes). The five base
party records are set to the widest value each field's own mode uses:

| field | offset | value | basis |
| --- | --- | --- | --- |
| level | +0x00 | 200 | the game's XP ceiling, not the u8 bound: `cmp r6,#0xc8` before the threshold lookup, reported at `tools/webfoot/stats.py:71-75` from `docs/research/P010_ENEMY_DEATH_AND_REWARDS.md:393`. The encoding is a u8 and would accept 255 |
| hp | +0x02 | 65535 | u16 field |
| ep | +0x04 | 65535 | u16 field |
| strength, power, endurance, speed | +0x06..+0x09 | 255 each | u8 fields |

Records 0..4 are set from `BASE_STAT_NAMES` order (Goku, Gohan, Goten, Trunks, Vegeta).
Records 5..8 (Gotenks, Vegito, Gogeta, Hercule) are deliberately untouched. The record order
itself is now **externally confirmed**, and the earlier inference about names is corrected:
the external Data Crystal RAM map (fetched through the Wayback mirror) names the current
character index at `0x03001068` as `0=Goku, 1=Gohan, 2=Goten, 3=Trunks, 4=Vegeta,
5=Gotenks, 6=Vegito, 7=Gogeta, 8=Videl`, and the per-character block stride is `0x68`. That
matches this table's record order for the first eight and shows the ninth is **Videl**, not
Hercule, which agrees with `tools/webfoot/formats/stat_tables.py:77` calling all nine records
playable. The five-record split of the boost is therefore a scope decision inside a confirmed
nine-character roster, not a claim about which records are characters. Records 5 to 8 stay at
retail values, the conservative side.

The builder refuses a byte that its own field table does not account for. That catches a write
outside the table. It cannot catch a wrong offset or width inside the table, because the table
also drives the writes; those were checked by hand against `decode_base_stat_record` and by
the reviewer, not by the assertion.

## 3. Verification performed

| gate | result |
| --- | --- |
| `tests/unit/test_friend_v3_playtest_boost.py` | **8 passed** |
| related unit suites (`test_character_swap`, `test_mgba_capture`, `test_project_safety`, `test_mgba_identity_gate`, `test_mgba_launch_coverage`) | **175 passed**; captured to ignored `build/review/related-suites.log` |
| changed-byte census on the delivered image | 45 bytes, all in `0x006FDA4C..0x006FDA9D`, length unchanged |
| foundation re-run through the toolkit | reproduces `ef939dcd` then `a4c12a95` byte for byte |
| boost re-run on the reproduced foundation | reproduces `6d7a56c6` byte for byte |
| canonical ROM digest after every run | `940ad5f0...` unchanged |

Not yet performed, and not claimed: independent review of the frozen candidate, GitLab CI,
and any runtime observation of this image. See section 5.

## 4. The authoritative modification tracker

### 4.1 Completed and ROM-verified

| item | evidence |
| --- | --- |
| Character-name text pass, 868 occurrences, 0 unresolved | MR !155 / !156, merged `1a45f494`, `d003ce93`; `docs/research/FRIEND_V3_COMPLETE_TEXT_PASS.md` |
| Content pass: 7 menu edits, credits line, slot-292 crash fix | merged; `20f2c140` entered this build as a digest-verified input, not rebuilt here |
| Token engine for the two-glyph name tokens | merged; `cec009d9` is its stage-3 published digest, carried through the chain, not re-run here |
| Tulma actor sprite, 22 containers | MR !165, merge `0b3676a7`; re-run here and reproduced as `ef939dcd` |
| Tulma portrait slot 17, and the two rewritten dialogue records | MR !166, merge `1b02221732d7b76d38fd9e35d731e9f3317da9a4`; re-run here and reproduced as `a4c12a95` |
| Cold-boot acceptance of the content-pass foundation | `docs/research/FRIEND_V3_COLD_BOOT_ACCEPTANCE.md`, 13,440 frames on the delivered image |
| Tail-allocation hazard assessment | `docs/research/FRIEND_V3_STABILITY_PASS.md`, LATENT |

### 4.2 Implemented, verification outstanding

| item | what is missing |
| --- | --- |
| the playtest boost (`6d7a56c6`) | independent review, CI, and one runtime observation that level 200 is what the game displays |
| Tulma graphics runtime confirmation | the human-played encounter session the graphics ticket names |

### 4.3 In progress

Nothing. The boost lane is frozen at `6d7a56c6` pending review.

### 4.4 Approved future changes

| item | authority |
| --- | --- |
| R3 bounded ROM destination safety | owner authorization 2026-10-09, assigned to the raw-write lane |
| R1 filesystem migration | owner authorized as a *conditional, prepared, unexecuted* plan. **Not authorized to execute**, and not executed here |

### 4.5 Owner-reserved creative decisions, recorded and awaiting the owner

| item | state |
| --- | --- |
| Idasa/Uub dialogue wording | text is recorded nowhere: 0 hits in the repository and 0 in the store. Awaiting the owner. Not invented here, and not a blocker for this build |
| Spopo's target (Android #13 or Perfect Cell) | both names exist in game text; no choice recorded |
| Boss replacements | owner-reserved |
| Difficulty balancing beyond these boosts | owner-reserved |
| New biography content, six scan-bio rewrites | not applied, not needed; retail grammar defect at slot 1065 kept as found |
| Cutscene sprite inconsistency at the hospital | **tracked only.** No character-animation modification was introduced |
| Chapter/saga titles | already carry Great Soyman and Majin Tien; no new title text is recorded |
| `Great Soy Man` spacing | retail text, preserved |
| Four records that now read Tulma where the merged plan said Chi-Chi | provenance says retail "Bulma"; confirmation is the owner's |
| Slot 1193 "Uub is the son of Tien and Tulma" | implies a marriage Tulma's own bio omits |

### 4.6 Known bugs, blockers and regressions

| item | state |
| --- | --- |
| the Bandana starting item | **NOT IMPLEMENTED.** The gear names sit in a general name table of 8-byte records at `0x06BCE8` (name pointer, then description pointer): index 428 is "Geromantium Bandana" and index 518 is "Bandana", described as "Only a really vicious criminal would wear something like this." That table continues into room names immediately after index 518, so it is a shared name table and not an item-only one. The 83-record item table at `0x3BD2F8` names no bandana and runs item ids 0..82, its names resolving through that same table at four entries per item. Two facts measured on the hardware image in this pass (see the completion record beside this one): the inventory slots are 8-byte records of a count word and an id word whose top nibble is a flag, and the item-add routine `0x08004448` refuses silently at 250 entries and stores `id & 0x0FFFFFFF`. **The unresolved mechanism is the id arithmetic by which the game names an id through `0x06BCE8`, and therefore the Bandana's own id.** Without it, choosing an id or an insertion point would be invention, so no bandana code was written |
| zero slack on every composition buffer | `docs/research/FRIEND_V3_STABILITY_PASS.md` section 7.1: 297 of 297 slots have declared size equal to the largest frame demand |
| latent tail-write hazard | same record, section 7.2: 275,033 bytes of third-party payload over 99 canonical references, none reachable by the instruments applied |
| the level cap of 200 is a code constant, not a table | raising it is a code patch with no verified consumer list, and was not attempted |

## 5. Limits of this record, stated plainly

1. **No runtime observation of `6d7a56c6` exists yet.** The claim that the party starts at
   level 200 with maximum stats is a static decode of a verified table plus the game's XP
   ceiling, which is itself a static read of one comparison. Nothing here shows that a
   starting level of 200 with no experience is a state the game handles. That is why the
   first checklist step below is a started-game stat-screen check.
2. **The Bandana is not in this image.** It is a tracker item, not a silent omission.
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
| 0 | pre-flight | the loaded image is `6d7a56c6...`; emulator reports `0.11` dev build; no other mGBA process holds TCP 2345 |
| 1 | new game, first stat screen | every party member reads **level 200**; hp and ep at the boosted maximum; four combat stats at 255 |
| 2 | first combat encounter | damage taken is small relative to the boosted hp; no freeze, no graphical glitch in the HUD |
| 3 | first shop and item use | items still buyable and usable; the inventory screen renders the party's techniques unchanged |
| 4 | first quest-gated door or NPC | the gate opens on the same trigger as retail. A gate that requires a level or a specific item is the case this boost does not address: record it, do not route around it silently |
| 5 | each chapter in order | chapter completes; no freeze; the party remains at boosted stats; check the quest log after each chapter |
| 6 | every fusion moment | Gotenks, Vegito and Gogeta still transform and still fight; their records were deliberately left at retail values, so a fusion that is *weaker* than its parts is expected and is not a defect |
| 7 | dialogue-heavy scenes | text matches the friend build (Tulma, Great Soyman), no truncated or missing line |
| 8 | scans and biographies | the screens open and read consistently |
| 9 | Dragon Ball and story progression | every collectible and story trigger reached in order; no sequence break |
| 10 | end credits | the credits line `Cale Aaron Cymek` is present and readable |

Regression watch-list for the playthrough, carried from the open risks:
the composition-buffer slack (a crash at a frame boundary in a crowded scene), the tail
window (a crash that reproduces on a retail reference but not here, or the reverse), and any
dialogue that renders as token glyphs rather than letters.

## 7. What closes this ticket

Independent review of the frozen candidate, CI green, and the owner's playthrough result
recorded here. Until then the status line at the top of this document stays as written.
