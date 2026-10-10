# FRIEND-V3-PLAYTEST-BOOST-001: consolidated build record and playtest plan

**Ticket:** FRIEND-V3-PLAYTEST-BOOST-001, under mission `FRIEND-V3-PLAYTEST-001`.
**Baseline:** live `origin/master` `1b02221732d7b76d38fd9e35d731e9f3317da9a4`, re-measured
before the worktree was created. Worktree: a dedicated ticket worktree beside the primary
checkout, on branch `ticket/friend-v3-playtest-boost-001`.
**Status:** CLOSED. Built, reproduced, independently reviewed and merged as true merges
(MR !170, `a6e4aba2`; MR !176, `372bb3aa`), with master CI green. The human campaign
playthrough is outstanding and is tracked in `FRIEND_V3_TRACKER.md`, the single tracker
for the whole friend image.

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
listed in `FRIEND_V3_TRACKER.md` section 6. Independent review and CI were performed at integration (status line).

## 4. Modification tracker

Moved to `FRIEND_V3_TRACKER.md`, the single tracker for the whole friend image.

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
2. **The Bandana is not in this image.** Cancelled by owner; see `FRIEND_V3_TRACKER.md` H1.
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
`FRIEND_V3_TRACKER.md` when it arrives; the ticket does not reopen for it. Future fixes run under
`FRIEND-V3-PLAYTEST-001`, which stays armed for that purpose, each as a new image built
from `acd98c2a`, which remains the frozen baseline.
