# FRIEND-V3 release 3: the two boss encounters, the aggressive profile and the wording tail

Ticket: `FRIEND-V3-WT-SPLIT-CONTAINER-001`, release 3. Owner decision to ship: 2026-10-10.
Cut from release 2.1, and nothing else.

## 1. Identity

| | |
| --- | --- |
| image | `v3-release3.gba` |
| sha256 | `521bd0fa0a8bc198f36430e3419184807e335fa588bd718152996c076a8f15fd` |
| bytes | 10,146,136 |
| cut from | release 2.1, `018757c4e0dda9f463364675f32b307dff9e5ad89c7a0b932939aec320032389` |
| reproduced | twice, from two independent output directories, byte-identical |

The chain and every intermediate digest, as the builder records them:

| stage | tool | result |
| --- | --- | --- |
| boss retune | `apply_friend_v3_boss_retune.py` | `1d59e0da6f4d7639a23f97c9e0892dc8f7a6cbc6453a9236b5250c37aa467650` |
| behaviour profile | `apply_friend_v3_behaviour_profile.py` | `682eb7f48d0496b9d5658bb5a8c42c43140ec9282f569c6357d1588ed5a78a74` |
| wording | `apply_friend_v3_dialogue_text.py` | `521bd0fa0a8bc198f36430e3419184807e335fa588bd718152996c076a8f15fd` |

One command reproduces it, and it refuses unless the result equals the frozen digest:

```
python -m tools.research.build_friend_v3_release3 \
    --image <release 2.1>.gba \
    --expect-sha256 018757c4e0dda9f463364675f32b307dff9e5ad89c7a0b932939aec320032389 \
    --out v3-release3.gba --manifest v3-release3.manifest.json
```

## 2. What it changes

### 2.1 The two encounters

| record | file offset | was | now |
| --- | --- | --- | --- |
| Hercule (selector 45) | `0x711760` | hp 20, str 5, pow 5 | hp 2,500, str 40, pow 30 |
| Olibu (selector 85) | `0x711BC0` | hp 565, str 13, pow 0 | hp 1,500, str 22, pow 16 |

Endurance and level are untouched, deliberately: endurance is the DEFENDER's term, so raising it
would shorten the player's own damage and double-count the length the hit points already set.

**Where those numbers come from, measured rather than modelled.** A normally levelled character
dealt 46 to 50 a blow. The enemy's own bite was measured at three strengths in the emulator:

| enemy strength | damage per landed blow | source |
| --- | --- | --- |
| 13 (retail) | 4 to 9 | measured |
| 22 | 29 | measured, and the owner called it right |
| 30 | 5 to 62, mostly ~60 | measured in the Hercule run |
| 35 | 88 to 90 | measured |
| 72 | 603, which killed the player in two blows | measured |

The bite grows faster than linearly: between 22 and 30 it grew by 2.07 for a 1.36 times increase,
which is an exponent near 2.3, so the cubic is an upper bound and every prediction here says so.
Olibu's 22 was chosen after the owner fought 35 and 72 and rejected both.

**Hercule's 40 is unmeasured and owner-locked.** It was never fought at 40. An earlier version of
this document justified it with "about seven blows against the player's measured 925", and that
basis was wrong: 925 is an ENEMY's hit points in that log (actor `0x0202BEF0`, a target the player
damages), not the player's, so the player's own maximum is never captured anywhere in the
repository. What is measured about STR 30 in that run is small: two blows, 62 and 58. The owner
decided to keep 2,500/40/30 without a runtime check, and the value stands on his decision rather
than on evidence.

### 2.2 The aggressive profile, per enemy

Both bosses now run a copy of their own fight family's behaviour tree, written into an appended
block, with only their behaviour rows repointed. No shared node is edited, so the other ten
selectors that resolve into the same tree are unchanged.

| | retail | release 3 |
| --- | --- | --- |
| attack arm's position in the decision list | child[1] | **child[0]** |
| entry gate | r100 | r150 |
| swing radius | r50 | r150 |
| swing chance per evaluation | 12% | 50% |
| the swing's action row | 206 | **206, unchanged** |

Two levers were found by measurement rather than by reading:

* Moving the attack arm to the front was the decisive change, and it is what the owner felt. A build
  that only raised the attack's own numbers measured one landed blow in twenty seconds, because the
  hub is a first-true OR and a passive branch sat ahead of the attack.
* The chance leaf is NOT a rate lever: raising it from 50% to its ceiling changed the swing count
  not at all (37 in 22 seconds against 25 in 21).

**The cadence claim is retracted.** An earlier version of this document said the swing's action row
was moved to 204 and measured 19.8 frames per swing, nearly halving retail's interval. Review B1
then measured that the appended copy's probability leaf pointed at the retail shared spawn in every
build - the tool serialised the block before patching that word - so the copied spawn and SET nodes
were dead bytes and the action row never changed in ANY build, including the one the owner fought.
The 41-swings-in-812-frames run was therefore the same chain as the plain profile, measured with the
player held still, and the interval difference is a condition of the run rather than an effect of the
action row. The tool's ordering defect is fixed and covered by a test, but the action-row lever is
now unmeasured, so release 3 ships without it.

### 2.3 The wording tail

| change | records | result |
| --- | --- | --- |
| spaced "Great Soy Man" -> "Great Soyman" | 1 (`1:38856:252`) | 0 spaced forms remain in the image |
| the records where retail says "Kakarot" and this image said "Yamcha" -> "Bandit" | 4 spans | **seven of the ten Kakarot lines read "Bandit"**; see the deferral below |

The spans are BYTE coordinates: `tools/webfoot/handles.py:unpack_handle` already returns decoded
start and length in bytes, and an earlier version of this tool scaled them by the two-byte unit a
second time, which doubled every window and damaged 28 records in the withdrawn `a72f1ecd` build.
The spans were re-derived with a byte-correct search after that defect was found by review.

One phrase is deliberately NOT applied: **"If Yamcha is coming back to fight in the World
Tournament"**. Every span that carries it has another live record's boundary inside it - `2:1948:252`
contains `1976:128`, and the chained records `2:528:2450` and `2:560:3562` fail the same test - so
the replacement's shift would cut that record and its text would lose a character. The wording tool
refuses such a span by name. That phrase, three of the ten records, moves to release 4 with the
container rebuild.

Both live inside the dialogue containers rather than the text table, so they were written by
`apply_friend_v3_dialogue_text.py` at each record's own unit count: no later record moves, and both
containers went back at exactly their original packed size. The tool reads every record back and
proves that only the edited spans changed, comparing whitespace-insensitively because a pad
absorbed inside a phrase moves a space within a record that covers the same bytes.

## 3. Verification

| check | result |
| --- | --- |
| boss retune verifier | PASS: the other 149 enemy records byte-identical, 0 differing bytes outside the six declared fields |
| profile verifier | PASS: the appended nodes are the family's own bytes with only the declared patches, the probability leaf reaches the copied spawn INSIDE the block, both borrowed rows are proven unnamed, 0 stray bytes |
| wording tool readback | PASS: 5 edits; every record outside an edited span is character-identical once spaces are ignored, and no character is lost, gained or reordered anywhere |
| focused tests | 9 in `tests/unit/test_friend_v3_boss_profile.py`, including one test per blocking finding and the two drift guards |
| reproduction | twice, from two independent output directories, byte-identical |
| runtime | measured on the withdrawn candidate: both bosses were fought in the emulator and the owner beat each. **Not yet re-checked on this candidate**: the image changed with the fixes (the swing chain is now the retail one and the wording spans moved), so a claim that this exact image was played would be unsupported |

## 4. Save guidance

**Battery saves are compatible.** Nothing in this release moves a save-visible structure: the
changes are two 28-byte enemy records, an appended behaviour block, and wording inside two dialogue
containers. A save made on release 2.1 loads and plays.

**Savestates are not.** A savestate taken while an enemy is on screen restores that enemy's actor,
and an actor carries its stats COPIED out of the record when it was built. A state taken at the
fight therefore plays with the old hit points and the old attack bytes, and will look as if the
retune did nothing. To see the retune, load a battery save, or a state taken before the enemy is
built. This was measured: an early attempt to check the retune from a state taken with the enemy on
screen showed retail numbers.

**Text changes are the same for both.** A savestate restores the dialogue the engine had already
copied, so a line will read its old wording until the scene is entered again from a save.

## 5. What is deliberately not in this release

**Interior double spaces.** Measured on this image in BYTE coordinates: **349 interior runs of two or
more spaces over 238 records**, against **24** records in the canonical ROM. The gap is the artifact
of the earlier rename pass, which replaced longer words with shorter ones and left the difference as
spaces. (An earlier version of this document quoted 424 runs over 212 records, against 26 in retail.
Those figures came from windows scaled by the two-byte unit a second time, which is the B3 defect;
they are corrected here and the measurement scripts now read byte spans.)

It is not in release 3 because it cannot be fixed in place, and that was measured rather than
assumed:

* these containers are chain-shared: records cover each other, so a run is often inside more than
  one live record;
* of the 349 runs, **147 are covered by exactly one live record**. The other 202 are covered by two
  or more;
* an in-place pass was built, run and discarded: it collapsed 118 runs and the measured total barely
  moved, because each payback space lands inside a covering record and re-creates a run;

The correct fix is a container rebuild with every handle word rewritten, which is a ticket of its
own (release 4). The failed attempt is recorded as pitfall P-023 so it is not repeated.

## 6. Limits that travel with these claims

* The appended behaviour block sits past the header's declared 8 MiB cart size, exactly like the
  containers releases 2 and 2.1 appended. It reads because mGBA serves the whole file; that is an
  emulator behaviour, not a hardware claim.
* A stand-still run measures the ENEMY's cadence with the player held still, and input automation is
  stimulus, never evidence about the player. One fight recorded 7 swings where another recorded 34 on
  a byte-identical profile, because a boss kept staggered never reaches his attack arm. Cadence
  claims are quoted with the run that produced them.
* Hercule's strength 40 is arithmetic over one measured point, not a measurement.
