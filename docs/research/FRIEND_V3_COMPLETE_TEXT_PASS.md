# Friend v3 complete text pass: implementation record

Ticket FRIEND-V3-COMPLETE-TEXT-PASS-001. No ticket document is tracked for it
(`git grep FRIEND-V3-COMPLETE-TEXT-PASS` finds nothing), so this record states the
scope it was worked to: a game-wide character-name audit over every text surface, the
`Saiyaman` to `Soyman` rename completed in spoken dialogue, biographies matched to the
displayed identities, the original-Bulma cleanup finished, chapter and saga titles
checked, and the unresolved creative decisions collected in one list (section 5).

Baseline `origin/master` `b97b3d6365c193c85e37c06e613f62d323305a3c`, measured in this
session rather than quoted, because the ticket names no SHA.

## 1. Inputs

| role | sha256 | bytes |
| --- | --- | --- |
| canonical ROM (immutable) | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` | 8388608 |
| rename base `v3-safe.gba` | `b0de6ddffe53961bcade893107b7f9a8004d684b919552480ca688207e8f56d5` | 9740320 |
| merged content-pass candidate | `b3344a3fed42f13c34bdd28d74463e1f6a0d3e071f2a3cd159f73ef68e5885a7` | 10132968 |
| private rename map | `8fc91afc83614eb299a46cf4a62594fdc4586ee765cc4c24013a1a94e37cd138` | 187943 |

The merged candidate is the latest verified friend image: the content pass's record
names it, and section 2 reproduces it byte for byte from the rename base, which is what
makes this pass sit on the verified foundation rather than beside it.

## 2. Composition

Five digest-gated steps. Each output digest below was produced here, not copied.

| step | tool | sha256 of the output |
| --- | --- | --- |
| 1 extend the map | `tools/research/build_friend_v3_complete_map.py` | map `26192ee420ebed37a0a86db3c7a27e70f0ff397527ad022d0b2c6936f0beab52` |
| 2 splice the dialogue | `tools/research/splice_dialogue_tokens.py` | `bd428deeeaf99748e42d9ea4e87ce5747fac70a15dba3458891df0a169872a38` |
| 3 patch the token engine | `tools/research/build_dialogue_token_engine.py` | `26c3ca3dd11b3d9fbb15ab7a5212a136b2c88445a8741a51c7833b2fed892a27` |
| 4 merged content-pass edits | `tools/research/apply_friend_v3_text_edits.py` | `acf9c63f5d9b25d8a489a0d975f31e0c3ebd02629bd9b5b190c5f69d7d718c64` |
| 5 this ticket's menu edits | `tools/research/apply_friend_v3_complete_text_edits.py` | **`bf3e61b3def05eb5bfe9b0f54eafafff674684d9c248c6bf29948a52c9d252e8`** (10133394 bytes) |

The chain is one script, `build/fv3ctp001/build.ps1`, and running it twice produced the
same five digests. Reproducing the merged candidate means stopping after step 4, and it
lands on `b3344a3f` byte for byte, which is the foundation check.

The splice encodes 490 rows, applies 482 and refuses 8. Every refusal is one of the
large records that share bytes with a neighbour, where the neighbour writes first, so
the record's own replacement is not applied; the pre-existing `3:2184:2112` is one of
them. Refused records are how this tool has always reported that case (one refusal in
the merged build), and section 4 is what proves no name was lost to it.

## 3. What changed

### 3.1 Spoken dialogue: two word rules added to the rename map

The 451-row map renames twelve names and stops. It never carried `Saiyaman` or the
retail word `Bulma`, so both survived every spoken record. The map is extended rather
than a second pass being stacked on a spliced image, because the splice relocates
records and a second pass would have to re-encode an already-relocated container.

`build_friend_v3_complete_map.py` adds 39 rows and edits 10, taking the map from 451 to
490. Every row's replacement text is rebuilt from the retail text plus the map's own
84-entry word table plus two rules, so a row added for a record the operator's map
never covered cannot disagree with a neighbouring row that was covered. Measured: that
table reconstructs all 451 authored rows exactly, so this is the map's own rule and not
a reinterpretation of it.

* `Saiyaman` becomes `Soyman` (26 rows touched).
* The retail word `Bulma` becomes `Tulma` (25 rows touched).

**Provenance, not string replacement.** The rename pass had already turned retail
`Chi-Chi` into the displayed name `Bulma`. The two are told apart by aligning the retail
words against the substituted words and touching only the aligned-equal ones: retail
`Chi-Chi` sits in a replaced run and keeps its `Bulma`, retail `Bulma` sits in an equal
run and becomes `Tulma`. A blind replacement renames the wrong character.

### 3.2 The four records the plan called blocked

`1:26476:306`, `4:10050:156`, `4:18714:142` and `5:42592:1086` carry the retail word
`Bulma`, and the content pass's plan proposed `Chi-Chi` for them and recorded three
routes when the shipping token dictionary could not pay for the growth. Under the
ticket's rule (resolve remaining `Bulma` references by original-character provenance,
not by blind replacement) the answer is the other direction, and it is cheaper:

* the retail word is `Bulma`, so the character is original Bulma, whose displayed name
  is `Tulma`; `Bulma` and `Tulma` are both five units, so the substitution is exact and
  needs no dictionary change at all;
* the proposed `Chi-Chi` would name Android 18 in lines that pair the speaker's wife
  and son (`I do this for you, Trunks... Bulma...`, `Even Bulma!` beside `Trunks, your
  own son!`), which reads as the wrong character.

A variant map copy, `rename_map_fv3cp001.json`, differs from the shipped map in exactly
those four rows and only in `new_text`, saying `Chi-Chi` where the shipped copy keeps
`Bulma`; the merged candidate follows the shipped copy. That variant is a map-copy
question, not a build question, and this record treats the shipped copy as the source
of truth. The change here is recorded as a deliberate departure from the plan's section
3.2 direction.

### 3.3 Menu pool, including the strings that had to move

`tools/research/apply_friend_v3_complete_text_edits.py` carries two tables, because two
different things have to happen and each keeps one job.

In place, 13 sites, each replacement no longer than the text it replaces:

| slot | current | replacement |
| --- | --- | --- |
| 527 | `Bulma's Airship` | `Tulma's Airship` |
| 528 | `Bulma's House` | `Tulma's House` |
| 618 | `Fly to West City and talk to Bulma` | `...talk to Tulma` |
| 624 | `Tell Bulma and Tien That Yamcha's Coming Back` | `Tell Tulma and Tien...` |
| 627 | `Meet Bulma to go to the World Tournament` | `Meet Tulma...` |
| 634 | `Get the Dragon Radar from Bulma` | `...from Tulma` |
| 1075 | `Dr. Brief is the president of the Capsule Corporation, and Bulma's father.` | `...and Tulma's father.` |
| 1077 | `Mrs. Brief is Dr. Brief's wife, and Bulma's mother.` | `...and Tulma's mother.` |
| 1193 | `Uub is the son of Tien and Bulma. ...` | `Uub is the son of Tien and Tulma. ...` |
| 136 | `SS Gogeta` | `SS Yamien` |
| 165 | `Gogeta` | `Yamien` |
| 1304 | `Gogeta` | `Yamien` |
| 1305 | `Gogeta is the fusion of Yamcha and Tien using the Metamorese Art of Fusion.` | `Yamien is the fusion...` |

Relocated, 6 sites, because the replacement is LONGER than the site's own span, which a
prefix write cannot express. Each is appended to the end of the image and its single
table pointer is repointed, the mechanism the earlier rename pass used for 84 slots.
The guard is what makes it safe: the tool counts every word-aligned occurrence of the
site's old pointer in the whole image and refuses unless there is exactly one, its own
table entry.

| slot | old offset | new offset | current | replacement |
| --- | --- | --- | --- | --- |
| 134 | `0x058530` | `0x9A9DE8` | `Vegito` | `Tiencha` |
| 135 | `0x05853E` | `0x9A9DF8` | `SS Vegito` | `SS Tiencha` |
| 164 | `0x058746` | `0x9A9E10` | `Vegito` | `Tiencha` |
| 1306 | `0x069024` | `0x9A9E20` | `Vegito` | `Tiencha` |
| 1307 | `0x949D78` | `0x9A9E30` | `Vegito is the fusion of Yamcha and Tien using the magic Potara earrings.` | `Tiencha is the fusion...` |
| 1347 | `0x949E9E` | `0x9A9EC4` | `...turn back into Goku.` | `...turn back into Krillin.` |

The `Gogeta` and `Vegito` sites are names the audit found still shown as their retail
spelling. Four `Gogeta` sites fit in place and two do not; all five `Vegito` sites grow.
The dialogue map already renames both (`Gogeta!` to `Yamien!`, `Goku? Vegito` to
`Yamcha? Tiencha`), so the menu pool was the surface that had not followed.

### 3.4 The cascade this ticket corrected

Slot 1347 read `...turn back into Goku.` in the merged candidate. The retail text is
`...turn back into Gohan.` and the map's single step is `Gohan` to `Krillin`, so the
merged image had applied the map twice: `Gohan` to `Krillin` to `Goku`. The audit's
`cascade` verdict found it, and this pass restores the single-step name. The content
pass's plan defended the change as deliberate; under single-step provenance it is a
rule applied twice, which is the failure this ticket's audit exists to catch.

### 3.5 Changed bytes

Against the step-4 image (the same chain without the menu edits): **50 bytes** differ
below the old end of file, plus **426 bytes** appended. The 50 are 9 single-byte
`B` to `T` changes, 24 bytes of `Gogeta` to `Yamien`, and 17 bytes in six repointed
table words; the tools claim 57 byte positions, seven of which are pointer bytes whose
value did not change. Nothing else in a 10132968-byte image moved.

## 4. Coverage report

The instrument is `tools/research/audit_friend_v3_name_coverage.py`. It walks two
surfaces with two provenances: the 1,534-entry text table, whose provenance is the
canonical ROM slot by slot, and the seven compressed dialogue containers, whose
provenance is the rename base. For each surface it builds the EXPECTED text (the retail
text with every retail name replaced by the single name it must display as), aligns
expected against displayed token by token, and judges each retail name by what appears
in the run it aligns to. Pairing a retail name directly with a displayed token would
mis-pair a chain that swaps two names in one sentence (retail `Goku and Krillin` is
displayed as `Yamcha and Goku`), which is a real record in this image.

| verdict | merged candidate | this candidate |
| --- | --- | --- |
| dialogue occurrences correct | 672 | **719** |
| dialogue occurrences unresolved | 47 (`Bulma` 23, `Saiyaman` 24) | **0** |
| menu occurrences correct | 95 | **114** |
| menu occurrences protected | 6 | 6 |
| menu occurrences approved | 5 | 5 |
| menu occurrences unresolved | 19 (`Bulma` 9, `Gogeta` 4, `Vegito` 5, cascade 1) | **0** |
| total tracked occurrences | 844 | 844 |

**Protected** are the six `planet`/`Planet Vegeta` and `Grandpa Gohan` spellings, where
the mapped name rides inside a protected phrase. **Approved** are the five occurrences
inside slot 1033, the content pass's authored twin-sister biography, which the ticket
says to preserve.

**Occurrence counts on the dialogue surface are per record, and records overlap.** The
honest stream count, where each character of each container is counted once, agrees with
the ticket's claim: `Saiyaman` appears exactly **20** times across the seven decoded
containers (selector 1 nine, selector 2 five, selector 3 six, containers 0/4/5/6 zero).
An independent audit of the same ticket counted 20 occurrences on the cutscene
event-handle surface as well, and 26 to 28 record spans containing the word, which is
the same data counted with overlap.

Measured counts of the words themselves, decoded with the token dictionary expanded:

| word | merged candidate | this candidate |
| --- | --- | --- |
| `Saiyaman` | 20 | **0** |
| `Soyman` | 0 | **20** |
| `Bulma` | 21 | **3** |
| `Tulma` | 0 | **18** |
| `Great Soy Man` (spaced) | 1 | 1 |

The 3 remaining `Bulma` words in dialogue are the ones the rename pass put there for
retail `Chi-Chi`, which is exactly the distinction the provenance rule draws. The one
spaced `Great Soy Man` is a spelling the rules do not touch, because they match the
single word `Saiyaman`; it is left as found and listed for the owner in section 5.

**Orphaned retail copies.** Five retail strings sit in the pool with no table entry and
zero word-aligned references anywhere in the image: file `0x06364E` (a second copy of
the slot-1033 biography), `0x0643BC`, `0x06459E`, `0x06472E` and `0x0666FC`. They are
unenumerated leftovers of the earlier rename pass, they are not reachable through the
table or the event pool, and no pass here writes them. They are accounted for rather
than repaired, because a change nobody can see is a change that cannot be verified.

**Orphaned copies that ARE enumerated are not orphaned.** File `0x06CD08` is the table
entry for slot 1032, not a string; the string it names is `Tulma` at `0x063642`, and the
orphan at `0x06364E` begins immediately after its terminator. That is the geometry the
merged content pass was built around.

**Surfaces outside the table.** An independent whole-image scan found no game text
outside the surfaces above: no new UTF-16 region outside the table and the dialogue
containers, no pointer table whose targets decode as text, and no separate nameplate or
HUD surface. The appended block holds 82 strings that the table itself names, and the
status text is served by the same table from two zones (131 entries into the retail pool
window, 84 into the appended block). Cutscene dialogue resolves to the same seven
containers: an independent count of 2,500 event handle sites over 284 event resources
found 13 sites still holding a retail name, all of them the literal `Bulma`, which are
the same occurrences this pass corrects in the containers.

## 5. Owner decisions, consolidated

Unresolved creative decisions, each with what is recorded and what is missing.

1. **Idasa and Uub dialogue: TEXT NOT RECORDED.** The ticket asks to include "the
   planned Idasa/Uub interaction". No such text exists anywhere: `Idasa` has zero hits
   in every tracked file, zero in the cross-session memory store, and the only game-side
   presence is the database entry at pool slot 1016 (`Idasa`, with its description slot
   next to it) plus three dialogue mentions. The character exists; the lines do not.
   This is the owner's to write.
2. **Chapter and saga titles: nothing left to change, no new title TEXT recorded.** The
   twelve chapter titles and the eleven saga strings already carry the established
   names: chapter 2 is `Great Soyman` and chapter 5 is `Majin Tien`, both applied before
   this ticket. No owner-authored replacement title text is recorded, so no title was
   invented.
3. **Spopo's target: NOT RECORDED.** The record names `Android #13` or `Perfect Cell` as
   the candidates and records the choice as the owner's. Both names exist in the game's
   text; no replacement text is recorded.
4. **Scan-biography wording: the plan's section 7 proposals are NOT applied.** Six
   proposed rewrites remain unapproved in the repository, and they are not needed: with
   the `Bulma`/`Tulma` collision resolved, the biographies read consistently under the
   displayed identities (for example `Krillin is the son of Yamcha and Bulma` is
   Gohan son of Goku and Chi-Chi, and `Goku is married to Chi-Chi` is Krillin married to
   Android 18). Reading the whole database block found one inherited retail defect that
   identity work cannot fix because it is grammar, slot 1065: `Tien was once a rival of
   Yamcha is now a loyal Z-Fighter.` The missing `, and` is the original writing and is
   preserved. A one-word repair is offered for approval.
5. **`Great Soy Man`, one dialogue record.** One record spells the name with spaces, so
   the word rules do not match it. It is left as found; a decision to make it
   `Great Soyman` belongs to the owner.
6. **Hercule's encounter difficulty.** Out of this ticket's scope, which puts combat
   balancing and boss replacement in separate workstreams. The record's numbers were
   deleted as unarchived and live only in a memory node, so they must be re-derived
   before any target is written.
7. **Tulma's blonde art.** Out of scope (sprite workstream). Tulma is a name over
   original Bulma's art until the art lands, and the biography deliberately makes no
   appearance claim.

## 6. Runtime

Rig: `tools/runtime/run_token_engine_session.ps1` in two phases, with the 0.11 dev
build, the `v3-fixed-credits.ss1` savestate, and the read-only observer
`tools/runtime/friendv3_coldboot_probe.lua`. The observer writes a frame heartbeat every
60 frames, a text snippet for each dialogue-copier hit, and a screenshot every
`DIALOGUE_SHOT_EVERY` frames. Its snippet window and shot cadence are environment
overrides with the original defaults, added here because 40 units stop inside a line
that opens with eight control codes and five seconds can miss a box between two copies.

Two things move on this route and both were observed on the final image:

| measurement | candidate | known-bad control |
| --- | --- | --- |
| image digest reported by `emu:romSize()` size | 10133394 | 9764900 |
| frame heartbeat | 60 to 10560 in the first run | 60 to **1980, then stops** |
| dialogue copier hits | 23 in the first run | 8 |
| verdict | **SURVIVED, renamed text copied** | FROZEN at frame 1980 |

The renamed line, copied by the engine from the image under test, in the wide-snippet
run at copy 6 (about frame 1500):

```text
........It can't be! .ill.'s the Great Soyman   AND the Gold Fighter??? Impossible!
```

The dots are the two-glyph token units that compose `KRILLIN` at the retail unit count,
exactly as the cold-boot acceptance recorded for the merged image (its copy 33 reads
`It can't be! .ill.'s the Great S`). `Great Soyman` is this ticket's rename, in plain
glyphs, and the three spaces before `AND` are the documented shrink padding: a shorter
replacement keeps the following characters where retail put them by paying the
difference with spaces. Retail reads `Great Saiyaman` here.

**Instrument proven, not assumed.** The same rig on the known-bad
`v3-fixed-credits.gba` (`ddfdf780...`) wrote its last heartbeat at frame 1980 and its
CSV was byte-identical across a 75-second wait with the emulator still running. That is
the failure this route is known for, so a candidate that reaches 10560 frames with 23
copies on the same rig is a surviving run, not a silent instrument.

**After the runs**: the candidate re-hashes to `bf3e61b3...`, the canonical ROM to
`940ad5f0...` and the rename base to `b0de6ddf...`, all unchanged.

The limit is stated: this route loads a savestate whose EWRAM holds a decoded dialogue
cache, so it proves the ENGINE copies the renamed record from this image, not that a
cold boot rebuilds the same text with no restored RAM. The merged content pass has a
cold-boot acceptance on the exact foundation this build starts from, and this ticket
does not re-run it; a cold boot of THIS image remains the stronger check somebody with
the emulator in front of them can take.

## 7. Preservation

| obligation | check | result |
| --- | --- | --- |
| the 451 spoken renames | audit over all 2,814 records | 719 correct, 0 unresolved |
| the content pass's seven menu edits | step 4 re-hashed in the chain | 204 bytes, same seven sites |
| credits line | `Cale Aaron Cymek` utf-16le | present at file `0x949FFE` |
| slot-292 crash fix | file byte `0x6B692B` | `0x04` |
| levels | base-stat table `0x6FDA4C` | `[65,65,75,60,75,75,75,75,50]` |
| graphics | actor-sprite region `0x3C0000` to `0x6B6BDC` | byte-identical to the merged candidate |
| canonical ROM | digest before and after every run | `940ad5f0...` unchanged |
| rename base | digest before and after every run | `b0de6ddf...` unchanged |

No ROM, image, savestate or capture is tracked. `roms/`, `build/` and the audit
evidence stay under ignored paths.

## 8. Limits, not proven

* The cold boot of this exact image is not run (section 6). The savestate route's
  decoded dialogue cache is the reason.
* The audit proves which name each enumerated string displays. It does not prove which
  string the game draws for a given menu, scan screen or quest line; that is index
  topology, and the runtime leg is what shows the dialogue path.
* The orphaned retail copies (section 4) are left in place. They have no table entry and
  no word-aligned reference; a pointer into them from code that is not a literal word
  in the image would not be visible to that check.
* The 2,814-record inventory and the 1,534-entry table are the surfaces this project
  enumerates. A text surface stored only inside compressed graphics or code was not
  looked for beyond the whole-image scan the independent audit ran.
* Relocation is proven safe by the one-reference guard, not by disassembly of the code
  that reads those five pointers.

## 9. Closure

Filled at integration: reviewed SHA, merge request, pipelines, merge commit.
