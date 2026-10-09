# Friend v3 content pass: the frozen change plan

Ticket FRIEND-V3-CONTENT-PASS-001. Baseline `origin/master`
`0fa1aa70fe22aecb4aa58d6e3c19098f14f10b92`. Worktree
the ticket worktree, branch
`ticket/friend-v3-content-pass-001`.

This document is the change plan, not the implementation record. It names every
site, the exact old and new text, the byte budget at that site, and the mechanism
that carries the edit. The implementation record follows in
`FRIEND_V3_CONTENT_PASS.md`.

Evidence labels follow `docs/DEVELOPMENT.md`. The figures in the edit tables below were
measured against the image when this plan was written. Where a figure has no archived
artefact behind it, the implementation record says so rather than restating it.

## 1. Foundation, and how it was verified

| artefact | sha256 | bytes | status |
| --- | --- | --- | --- |
| rename base `roms\v3-safe.gba` | `b0de6ddffe53961bcade893107b7f9a8004d684b919552480ca688207e8f56d5` | 9740320 | CONFIRMED, hashed here |
| rename map `build\crash-repro\rename_map.json` | `8fc91afc83614eb299a46cf4a62594fdc4586ee765cc4c24013a1a94e37cd138` | 187943 | CONFIRMED, hashed here |
| 451 derivative | `cffdb81e471567fab623d3ec3a0b920cc0b5ef3f0a11bc5f3c70e5bab1395446` | 10132968 | CONFIRMED, REPRODUCED here |
| engine candidate | `d401d71c0ed3fbf93476aaa1825ea8c680e3caac7f7d7fbc05cbfe16344ab0f5` | 10132968 | CONFIRMED, REPRODUCED here |
| canonical `roms\Dragon Ball Z - Buu's Fury (U).gba` | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` | 8388608 | CONFIRMED, untouched |

Reproduction is by re-running, not by reading:

```text
python -m tools.research.splice_dialogue_tokens --base roms\v3-safe.gba \
  --base-sha256 b0de6ddffe53961bcade893107b7f9a8004d684b919552480ca688207e8f56d5 \
  --map build\crash-repro\rename_map.json \
  --tokens Ya ha Kr in Ti YA HA KR IN TI \
  --out build\scratch-fv3cp001\repro-451.gba \
  --report build\scratch-fv3cp001\repro-451-report.json

python -m tools.research.build_dialogue_token_engine --variant token \
  --rom build\scratch-fv3cp001\repro-451.gba \
  --expect-sha256 cffdb81e471567fab623d3ec3a0b920cc0b5ef3f0a11bc5f3c70e5bab1395446 \
  --out build\scratch-fv3cp001\repro-451-engine.gba \
  --tokens Ya ha Kr in Ti YA HA KR IN TI \
  --splice-report build\scratch-fv3cp001\repro-451-report.json
```

Both outputs landed on the recorded digests exactly, and the fresh splice report
is byte-identical to the archived `v3-token-report.json`. 451 encoded, 450
applied, 1 refused (`3:2184:2112`, covered by an overlapping neighbour's rewrite).

The two candidate images exist only under ignored `build\` directories of sibling
worktrees. They are reproducible from `roms\` material, which is why this plan
builds from the base rather than from either image: the splice tool refuses a
replayed map whose spans no longer hold `old_text`, and the engine builder refuses
an already-patched base.

## 2. The constraint that shapes every edit

The friend's text table is 1,534 `u32` pointers at file `0x6BCE8`. In
`v3-safe.gba` they resolve to two regions: retail pool offsets below `0x06BCE8`
and an appended block above `0x08900000` written by the earlier rename pass.

Both regions are packed with no growth slack: a named string is followed by its own
2-byte terminator and then by the next string's first byte, with no gap. That is the
property the earlier rename pass did NOT leave intact everywhere, which is the whole
reason section 3.1 is a prefix write rather than a pad-to-span write: slot 1032 is
followed by a 490-byte orphaned copy of the slot-1033 biography that no table entry
names, so measuring a site by the distance to the next NAMED string reached far past it
and erased another string's text. A text edit therefore has to be
length-neutral or shorter, or it needs the relocation path
(`config/roms.yaml` declares `text_strings.relocatable: true` with a 256-byte
CONFIRMED free window at file `0x007EA400`). This plan needs neither: every edit
below is measured shorter than or equal to the span it occupies.

## 3. Edits, by site

### 3.1 Menu, quest, and biography pool (direct span write)

Each row names the slot, the file offset in `v3-safe.gba`, the current text, and the
replacement. Every replacement is the same length as its site's text or shorter.

The write is a prefix substitution: the replacement goes over the front of the site's
own text, and every byte after it keeps its base value.

**Mechanism.** Two mechanisms, because the two surfaces are different corpora.
Section 3.2 goes through the existing token/splice system (`tools/research/splice_dialogue_tokens.py`
then `tools/research/build_dialogue_token_engine.py`), which is the only thing that
can rebuild a compressed dialogue stream. This section is the 1,534-entry pointer
table's pool, which the splice tool never reads, so it is carried by a new
digest-gated span writer that refuses unless the bytes at each named offset are
exactly the text it replaces, refuses any TABLE-NAMED string that starts inside the span
it would write, refuses a span whose offset a second table slot aliases, and leaves every
byte after the replacement untouched. It cannot see a pointer into those same bytes held
in code rather than in the table; that limit is why the shipped edit table was measured
against the real image. Both
steps are applied to the same base in sequence, and the second step refuses any
replacement longer than the span it replaces.

| slot | file offset | span (text + terminator) | current | replacement |
| --- | --- | --- | --- | --- |
| 1032 | `0x063642` | 12 B | `Bulma` | `Tulma` |
| 1033 | `0x94879C` | 490 B | `Bulma Brief is the daughter of ... married to Tien.` | `Tulma Brief is the daughter of the founder and president of the Capsule Corporation, Dr. Brief. Tulma is the identical twin sister of Bulma. Like her sister, Tulma has many invention patents in her name, most notably the Dragon Radar.` |
| 122 | `0x058454` | 30 B | `Great Saiyaman` | `Great Soyman` |
| 1453 | `0x06B5C4` | 30 B | `Great Saiyaman` | `Great Soyman` |
| 603 | `0x05DE3E` | 40 B | `Great Saiyaman Saga` | `Great Soyman Saga` |
| 1346 | `0x06A3E0` | 18 B | `Saiyaman` | `Soyman` |
| 1347 | `0x949E9E` | 210 B | `Press the B Button to turn into the Great Saiyaman.  Press the B Button again to turn back into Krillin.` | `Press the B Button to turn into the Great Soyman.  Press the B Button again to turn back into Goku.` |

Slot 1033's replacement removes the marriage clause (owner decision) and carries
the twin canon minus any appearance claim, because the blonde asset the owner states
will exist does not exist yet, and a text claim about hair colour would be false until
it lands.

Slot 1347's tail changes `Krillin` to `Goku` under the established permutation: the
runtime identity named `Krillin` is original Goku, and `Krillin` is the identity
that owns this ability.

### 3.2 Spoken dialogue: the four closure records

All four keep the word `Bulma` in the applied text where the closure says the identity
is Chi-Chi. `Bulma` -> `Chi-Chi` is a two-unit growth against a five-unit span, and the
shipping dictionary cannot close it (the BLOCKED paragraph below records the
measurement and the three routes).

| record | old length | applied length | slack | intended replacement |
| --- | --- | --- | --- | --- |
| `1:26476:306` | 306 | 296 | 10 | `...so will Chi-Chi and Tien!...` |
| `4:10050:156` | 156 | 150 | 6 | `...Can't you see that? Chi-Chi! Uub!...` |
| `4:18714:142` | 142 | 134 | 8 | `I do this for you, Uub... Chi-Chi... And yes...` |
| `5:42592:1086` | 1086 | 1074 | 12 | `...we care about! Even Chi-Chi!...` |

NOT APPLIED, for the reason measured below. The mechanism would be the existing map
with these four `new_text` values corrected and every other record carried through
unchanged.

**BLOCKED, and the reason is measured.** The splice tool pays for a substitution
inside the changed span itself: `local_replacement(old_side, new_side, dictionary)`,
which is asked for a replacement that occupies exactly `len(old_side)`.
`Bulma` is shorter than `Chi-Chi`, so that span must offer a saving, and it does not.
Two independent reviews reproduced those refusals; the command that produced the exact
refusal text is not archived, so the text is described here rather than quoted.

The four records' recorded slack is real but is record-level, already consumed by the
operator's own padding; it is not payment a substitution may draw on. The table
constraint is global as well: `Bulma` must map to one new side in every record, so the
payment cannot be re-worded for four
records without contradicting the other 447.

Three routes exist and all are outside this pass:

1. Add one admissible two-letter token (`Ch` or `hi`), which closes `Chi-Chi` to 5
   units against a 256-token window. The cost is a dictionary change, an engine
   rebuild and a fresh Kibito runtime check, because a new token shifts the id order
   the engine patch and the dictionary blob are built from.
2. Widen those four records' decoded length by 2 units. The handle carries an
   11-bit halfword length field (`docs/research/ROM_DIALOGUE_VARIABLE_LENGTH.md`)
   and `relayout_for_length` already refuses a span that another record's start
   crosses. This is the documented capacity mechanism, but it cannot use the
   supported authoring entry point yet: `target_named` refuses these records because
   they are not in `AUTHORED_DIALOGUE_TARGETS`, so it needs a registry extension or a
   deliberate decision to call the low-level API past that gate. It is a new tool
   plus its own runtime check.
3. Leave the four lines carrying `Bulma` and record the inconsistency as accepted.

Extending the splice to accept a length change is rejected: a plain grown rename
is what froze the Kibito scene, and the acceptance criteria forbid unintended
change to unrelated records.

Until one of the three is chosen, those four records keep the permuted name and no
further correction is applied. Everything else in this plan is independent of them.

The spoken records that say `Super Saiyan` and the `Saiyan Race` speech in
`5:42592` are preserved; the notes ask for scan text, not spoken transformation
terminology, and the transformation system remains reachable.

## 4. Deliberately out of scope

* `Piccolo` - owner decision: leave unchanged.
* Hercule's encounter - separate lever, section 6.
* Chapter titles and the Spopo target - owner-authored content, section 6.
* The five contradictory Z-Fighter scan biographies (1187, 1189, 1191, 1193,
  1195) and the Android-name bio at 1059 - the phrasing carries the permuted
  names and is therefore authored content, section 6.

## 5. Preservation obligations, and how each is checked

| obligation | check |
| --- | --- |
| the 451 spoken renames | the splice report still reports 451 encoded |
| credits line | `Cale Aaron Cymek` utf-16le present at file `0x949FFE` |
| slot-292 crash fix | file byte `0x6B692B` = `0x04` |
| levels | base-stat table `0x6FDA4C`, 9 x `0x12` = `[65,65,75,60,75,75,75,75,50]` |
| graphics | the actor-sprite region `0x3C0000`-`0x6B6BDC` and the portrait array byte-identical to `v3-safe.gba` |
| the stable images | `roms\v3-safe.gba` and both candidates re-hashed unchanged after every run |
| canonical ROM | `940ad5f0...` unchanged before and after |

## 6. Open owner decisions

1. Hercule's difficulty: the lever is Hercule's own enemy stat record, reached through
   the appearance-definition record that names him, and the placement that builds him.
   This plan surveyed both and recorded the addresses and values here; that survey left
   no archived artefact, so the numbers are DELETED and must be re-derived before any
   target is written. Two constraints that do not depend on the survey: only hit points
   have measured consumption evidence, and the shipped enemy-stat randomizer also
   writes that record, so build order must be declared.
2. Tulma's blonde appearance: the owner states it will exist and it does not exist
   yet. Until it lands she is a name wearing original Bulma's art, and the biography
   makes no appearance claim for that reason. A distinct appearance record plus a
   distinct actor-sprite slot and palette are separate future work.
3. The scan biographies: proposed wording in section 7 for six sites, plus slot 1065
   (broken grammar) and slot 1043 (recorded as ambiguous rather than wrong).
4. Chapter titles (ten saga strings remain) and the Spopo target (`Android #13`
   and `Perfect Cell` both exist in the game).

## 7. Proposed scan-biography wording, awaiting approval

Each replacement is shorter than its current span, keeps the permuted character
name, and removes the contradiction:

| slot | current | proposed |
| --- | --- | --- |
| 1189 | `Yamcha is a Saiyan from the planet Vegeta that was stranded on Earth. He is an all-around good guy, who often saves the Earth.` | `Yamcha was once a bandit of the Diablo Desert, and is now one of Earth's greatest defenders.` (184 B) |
| 1195 | `Tien was the prince of the Planet Vegeta before it was destroyed by Frieza. Although he was once a villian, he usually fights for the Z-Fighters now.` | `Tien was once a rival of the Z-Fighters who became one of their most loyal members. His most distinguishing feature is his mysterious third eye.` (288 B) |
| 1187 | `Krillin is the son of Yamcha and Bulma. He is half human and half Saiyan. Krillin defeated Cell in the Cell Games.` | `Krillin is an old friend of Goku's. They trained together under Master Roshi. Krillin is married to Chi-Chi.` (216 B) |
| 1191 | `Videl is the son of  Yamcha and Bulma. Despite his young age, he's one of the most powerful fighters in the universe.` | `Videl is the crimefighting daughter of Hercule. She attends Orange Star High School with Krillin.` (194 B) |
| 1193 | `Uub is the son of Tien and Bulma. Despite his young age he's one of the most powerful fighters in the universe.` | `Uub is a young boy who is the reincarnation of Buu, and one of the most powerful fighters in the universe.` (212 B) |
| 1059 | `Once Dr. Gero's evil Android, she has now changed her ways and fights for the good guys. Is married to Goku.` | `Bulma is the daughter of Dr. Brief, the president of the Capsule Corporation. She is married to Yamcha.` (206 B) |

Every replacement above was byte-measured against its span and fits with at least
2 bytes to spare; the three that first overflowed were shortened until they fit. The
byte figures are the replacement's UTF-16LE text alone. What limits a replacement is
the size of the text already at that site: it may be as long as that text is, because
the writer covers the old text plus its terminator.
