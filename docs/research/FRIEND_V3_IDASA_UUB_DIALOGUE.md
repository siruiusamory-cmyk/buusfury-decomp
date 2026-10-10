# World Tournament Idasa/Uub dialogue: located records, speaker identities, wording review

Ticket: `FRIEND-V3-IDASA-UUB-DIALOGUE-LOCATE-001`. Research only. No ROM was modified and no
dialogue replacement was applied. This record is the evidence behind tracker item A12; the tracker
itself stays `FRIEND_V3_TRACKER.md`.

## 0. Identity of what was read

| item | value |
| --- | --- |
| image read | `v3-playtest-boost.gba`, 10,140,972 bytes, sha256 `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c` |
| copy read | `C:\Users\hears\.dsh\work\log1-protected-rom-backups\friend-v3-playtest-boost-001-final\v3-playtest-boost.gba` (read-only; hash re-verified before and after every read) |
| retail comparison | canonical `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, 8,388,608 bytes |
| worktree | `C:\Dev\log1-remake-friend-v3-idasa-uub-001`, branch `ticket/friend-v3-idasa-uub-dialogue-locate-001`, cut from live `origin/master` `59203721566bcd28edb645dc9cc21de9dec99b67` |
| scratch tools (git-ignored) | `build/fv3idasa001/locate.py` (record census), `scene.py` (script table with portrait operand resolved) |

Method: decode the dialogue containers through the table the image's own literal at file `0x123CC`
names, enumerate the record words the engine's dispatch reads, then read each record word's `+0x03`
portrait operand and resolve it through the appearance table. Retail and the playtest image were
read the same way, so every difference below is a difference in the bytes, not in the tooling.

## 1. Where the scene lives

* Container table: literal at file `0x123CC` = `0x089A9CE8` on the playtest image, `0x087B5B64` at
  retail. Selector 3's slot holds `0x08979EF8` (playtest) / `0x087A8AD8` (retail). The playtest
  image's selectors 0 to 5 are stored verbatim (container header kind 0); retail's are packed.
* The pre-fight conversation and the Idasa sequence are a script list at `0x0878B51C` (19 entries),
  reached from the opcode `0x07` record at `0x0878B14C`: bytes `11 00 07 00 1c b5 78 08`, payload
  `0x0878B51C`. The Idasa-match half is a second list at `0x0878B750` (10 entries).
* Those lists are entries of the tournament event resource reached from the table at `0x0879B704`
  (entries 235 and onward point into `0x0878A060`..`0x0878CF98`).
* A record word is 8 bytes: u16 id at `+0x00`, handler byte at `+0x02`, portrait operand at `+0x03`,
  packed u32 handle at `+0x04`. Handler `0x05` is compressed dialogue and loads `[record+0x04]`;
  the portrait operand is read by the box constructor (`0x08012012`, portrait pick at
  `0x08012118`..`0x08012142`, portrait array `0x086F393C`). Operands below 8 take the runtime face
  path and are **not** statically resolvable; operands 8 and above index the portrait array, whose
  entry maps to an appearance record at `0x0874D380` (stride `0x10`, `+0x00` name slot into the
  string-table at file `0x6BCE8`, `+0x04` sprite, `+0x08` portrait slot).

## 2. The records

Addresses are GBA addresses; the handle word sits at record word `+4`. "speaker" is the character
the appearance table derives from the portrait operand, read from the playtest image.

| record word | selector:start:length | portrait | speaker | text as the playtest image stores it |
| --- | --- | --- | --- | --- |
| `0x0878B400` | `3:7406:136` | `0x89` = 137 | Uub | `#So... If you won the tournament, what would you get with the money?` |
| `0x0878B408` | `3:7542:42` | `0x3F` = 63 | Videl | `#Uh... Toys, I guess!` |
| `0x0878B41C` | `3:7584:80` | `0x8A` = 138 | unnamed face of 137 (Uub) | `#Sheesh... You're such a toddler, Videl.` |
| `0x0878B424` | `3:7664:60` | `0x3F` | Videl | `#So what are you going to buy?` |
| `0x0878B438` | `3:7724:72` | `0x89` | Uub | `#I'm not sure what I'm going to buy.` |
| `0x0878B440` | `3:7796:204` | `0x3F` | Videl | `#Yeah. I guess when your family's the richest in the world there aren't many toys that you don't have.` |
| `0x0878B468` | `3:8000:214` | `0x4E` = 78 | Idasa | `#Hey, half pint. You're going to be fighting me in the tournament. I hope you're wearing diapers! Hahahaha!` |
| `0x0878B470` | `3:8214:118` | `0x89` | Uub | `#Spare me. I'm going to send you home crying to your mommy.` |
| `0x0878B490` | `3:8332:218` | `0x4E` | Idasa | `#How dare you? You've just sealed your fate, shorty! I'm going to beat you so hard, you'll have a concussion!` |
| `0x0878B4BC` | `3:8550:414` | `0x0A` = 10 | Announcer | `#Attention everyone! The Junior Tournament is going to begin! Rules are same as the big leagues! ...` |
| `0x0878B4F4` | `3:8964:148` | `0x00` | runtime face (player = Uub) | `!You are now playing as Uub.    Defeat ten fighters to win the tournament!` |
| `0x0878B6D4` | `3:9112:62` | `0x4E` | Idasa | `Are you ready to cry yet, baby?` |
| `0x0878B6DC` | `3:9174:114` | `0x02` | runtime face (player = Uub) | `#Please. Don't talk. You'll just make a fool of yourself.` |
| `0x0878B6F8` | `3:9288:282` | `0x4F` = 79 | unnamed portrait 79 | `#That's my baby Idasa down there!!!!! Ooooo!!! Idasa!!!!! I wish they would match Idasa up with a bigger kid! This won't even warm my boy up!` |
| `0x0878B714` | `3:9570:92` | `0x11` = 17 | Tulma | `#Oh, yeah? That's my son you're talking about!` |
| `0x0878B72C` | `3:9662:116` | `0x11` | Tulma | `#Get him, Uub!    You make that boy sorry he ever met you!` |
| `0x0878B7A4` | `3:9778:114` | `0x4F` | unnamed portrait 79 | `Noooo!!!!! My baby!!!! That was unfair! That boy cheated!` |
| `0x0878B988` | `3:9892:486` | `0x0A` | Announcer | `Unbelievable! Uub    wins and this means he's going to the final! ... between eight-year-old Uub    and seven-year-old Videl!` |

Each of these records has exactly one reference site in the whole image: the record word addresses
above. No record in this scene is named by a second handle.

Textual changes already present in the playtest image (retail to playtest), all name substitutions:

| record | retail | playtest |
| --- | --- | --- |
| `0x0878B41C` | `...toddler, Goten.` | `...toddler, Videl.` |
| `0x0878B4F4` | `playing as Trunks. Defeat` | `playing as Uub.    Defeat` (3 padding spaces) |
| `0x0878B72C` | `Get him, Trunks! You make` | `Get him, Uub!    You make` (3 padding spaces) |
| `0x0878B988` | `Trunks wins ... eight-year-old Trunks and seven-year-old Goten` | `Uub    wins ... eight-year-old Uub    and seven-year-old Videl` |

Every other record in the list is byte-identical to retail, including all four Idasa lines, the
announcer's junior-tournament speech, and the two parent lines apart from the speaker's own name
table entry.

## 3. Speaker identities

The owner's runtime identities (the transcript), the record's portrait operand, and the name that
portrait resolves to agree on every line:

| line | owner | record portrait | resolves to | verdict |
| --- | --- | --- | --- | --- |
| `Are you ready to cry yet, baby?` | Idasa | `0x4E` | Idasa (appearance 102, sprite 143, name slot 1016) | confirmed |
| `Please. Don't talk.` | Uub | `0x02` | runtime face, player character | confirmed by owner only; the operand is not statically resolvable |
| `That's my baby Idasa down there!!!!!` | Idasa's mother | `0x4F` | no appearance record for portrait 79 | owner-attested, internally consistent: her second line uses the same `0x4F` |
| `Oh, yeah? That's my son...` and `Get him, Uub!` | Tulma | `0x11` = 17 | Tulma (appearance 20, sprite 41, name slot 1032) | confirmed |
| `Noooo!!!!! My baby!!!!` | Idasa's mother | `0x4F` | as above | owner-attested, same portrait as her first line |

The pre-fight exchange resolves the same way and matches the owner's transcript: line 1 and 5 Uub
(`0x89`), lines 2 and 4 and 6 Videl (`0x3F`), line 3 Uub (`0x8A`, the alternate face next to 137).
"Idasa" is the game's own spelling: string-pool slot 1016 at file `0x62EF8` reads `Idasa` in both
images, unchanged, and appearance record 102 at `0x0874D9E0` links that name to sprite `0x8F` and
portrait 78. The owner's `Ibasa` is a transcription artifact.

## 4. Tulma, and whether Bulma appears

Both parent lines carry portrait operand `0x11` = 17, which is appearance record 20, whose name slot
is 1032. Slot 1032 reads `Tulma` in the playtest image and `Bulma` at retail; the appearance record
bytes are identical in both images (`08 04 09 04 29 00 00 00 11 00 00 00`, name 1032, sprite `0x29`
= 41, portrait `0x11`). The art moved, not the reference:

| portrait slot | retail pointer | playtest pointer | first 256 bytes |
| --- | --- | --- | --- |
| 17 (Tulma, the parent in this scene) | `0x086BBFE8` | `0x089AB64C` | differ |
| 63 (Goten / Videl) | `0x086CDC28` | `0x08923300` | differ |
| 137 (Trunks / Uub) | `0x086E9CB0` | `0x088A5C3C` | differ |
| 78 (Idasa) | `0x086D3AFC` | `0x086D3AFC` | identical |
| 79 (unnamed, Idasa's mother) | `0x086D41B0` | `0x086D41B0` | identical |
| 10 (announcer) | `0x086B93F8` | `0x086B93F8` | identical |

So the character drawn in this exchange is the customized Tulma, not retail Bulma: the scene selects
portrait 17 and sprite 41, and both carry replaced art in the playtest image. Idasa, his mother and
the announcer were not touched. This is `read from bytes` for the selection and the pointer change,
and it is corroborated by the owner seeing Tulma in play.

## 5. Does any line need rewriting? (owner decision, nothing applied)

**Nothing in the five newly reported lines needs rewriting.** Tulma calling Uub "my son" is the
approved relationship. Idasa's and his mother's lines are retail and reference nothing about the
custom canon. Uub's two lines are addressed to Idasa.

The one line worth an owner decision is the pre-fight exchange's closing line, record `0x0878B440`
(`#Yeah. I guess when your family's the richest in the world there aren't many toys that you don't
have.`). Read from bytes, the speaker portrait is `0x3F` = the retail Goten appearance, so the
speaker is Videl, and she is addressing Uub (the retail Trunks role). Under the approved canon
Uub's adoptive mother Tulma is Bulma's twin sister and a Brief, so "your family's the richest in
the world" reads as true of Uub and needs no change. The only tension is that Videl is Bulma's
daughter and therefore inside that same family herself, which softens the retail joke (poor kid
teasing the rich kid) without contradicting anything. That is a tone question, not a continuity
defect, and it is recorded here as an owner decision, not as a defect.

Two wording facts for the record, since the transcript differs from the source:

* The owner's `bigger big` and `bigger boy` are both wrong: record `0x0878B6F8` reads
  `a bigger kid` in the playtest image **and** in retail. It is not an in-game typo and not a
  replacement site. Keep the retail wording.
* The owner's `the World Tournament` in the first line is `the tournament` in the record; `Oh yeah?`
  is `Oh, yeah?`; `Uh, toys I guess!` is `Uh... Toys, I guess!`; and the two Tulma lines are two
  separate records (`3:9570:92` and `3:9662:116`), not one.

## 6. One continuity question outside this scene, found by the name search

The rename makes the child protagonist display as `Uub`, and the game already has its own `Uub` at
the end of the story, whose records were not touched. Both now read `Uub`:

* `3:9892:486`, site `0x0878B98C` (this scene): `eight-year-old Uub`.
* `3:31484:464`, site `0x0878D2A8` (endgame, byte-identical in both images): `Look at his name.
  Uub. It's Buu spelled backwards! ... Uub is ten years old ... Uub is Buu reincarnated!`
* `3:33530:430`, site `0x0878D5C0`: `I'm going to live in Uub's village so I can train him!`

Two different characters therefore share one displayed name, and their stated ages disagree (eight
against ten). This is not a defect in the Idasa scene and no change is proposed here; it is flagged
because the tracker's section 4 already records the retail `Uub` records as "not established", and
the owner may want the endgame name distinguished.

## 7. Text space and the edit path, if the owner asks for a change

* A record's length lives only in its handle. The engine copies the handle's decoded length, so a
  replacement must occupy exactly the record's own unit count, or the handle must be rewritten.
* Measured spans for the lines above run from 21 units (`3:7542:42`) to 243 units (`3:9892:486`);
  each record's text fills its span exactly, with zero slack. A longer line cannot grow in place.
* Growth is possible only by re-laying out the affected region of the container: the established
  engine `tools/webfoot/dialogue_edit.py` reads the table through file `0x123CC`, requires the
  container to be stored verbatim (true for selectors 0 to 5 on this image), refuses a wording that
  matches zero or more than one record, refuses to grow a record whose neighbours are not adjacent,
  and refuses a re-layout that would leave a partial overlap reading mixed text. The precedent on
  this exact image chain is `tools/research/apply_tulma_dialogue.py`, which rewrote two contiguous
  World Tournament records (112 + 138 = 250 bytes) into 220 bytes and rewrote both handles.
* Constraint the leading marker imposes: these records begin with a unit the box constructor consumes
  as a width command, `#` = 120 px and `!` = 40 px (reported by the independent static lane from
  `0x080120E2`..`0x08012102`; re-verify before relying on it if a replacement changes it). Keep the
  leading marker in any replacement.
* Any edit produces a new image built from `acd98c2a`; the playtest image stays as it is.

## 8. Lines in the sequence that were not in the transcript

The transcript covers 14 lines. The same two lists also carry the announcer's junior-tournament
speech (`3:8550:414`), the `playing as Uub` banner (`3:8964:148`), the announcer's winner
announcement and championship line (`3:9892:486`, `3:10378:136`), and the post-fight exhibition
sequence against Hercule (`3:10718:170` onward). Only one of those, `3:9892:486`, has changed from
retail, and only in the names. The Idasa story is referenced again later in the campaign at
`2:23350:634`, site `0x08787958` (retail `That boy was Trunks!` reads `That boy was Uub!    `),
already renamed by the same map.

## 9. Confidence, limits, and what would falsify

* `read from bytes`: the container pointers and table slots, every record word, handle, span, the
  portrait operands and their appearance resolution, the slot 1032 text, the portrait pointer and
  payload differences, the pool slot 1016 text, and every quoted line. All measured on the named
  digests.
* `observed at runtime`: the owner's transcript, on this image, from the live playtest. It is
  owner-attested; no capture, savestate or screenshot is recorded here, and the live session was not
  touched.
* `inferred from structure`: that portrait operand 79 is Idasa's mother (the appearance table has no
  record for it; the owner's observation supplies the identity, and her second line uses the same
  operand). That operand `0x8A` is an alternate face of the same character as 137. That portrait
  operands below 8 resolve to the player character.
* `not established`: whether the 3872-byte span at `3:6232` is a real referenced record. Its record
  word sits at `0x082FE430` in high-entropy data with no referrer found; the text it spans is the
  scene's contiguous text region, so it is the same bytes either way. Also not established: what the
  private-use token pairs elsewhere in the container draw on screen, and whether any of the three
  undecoded handlers (`02`, `03`, `06`) can set a speaking actor.
* Falsifiers: a second handle naming any of these records, a record word whose portrait operand
  disagrees with the table above, a differing digest on either image, or an in-play observation
  contradicting an owner-confirmed speaker. Any of those reopens the line it touches.

## 10. Provenance

Reading tools: `build/fv3idasa001/locate.py`, `build/fv3idasa001/scene.py` (both git-ignored), run
from `C:\Dev\log1-remake-friend-v3-idasa-uub-001` on 2026-10-10, Python 3.12.10. Container decode via
`tools/webfoot/formats/webfoot_lz.py`; record enumeration via
`tools/webfoot/compressed_dialogue.py`. The independent static lane read the same records with its own
decoder and reported the same 31 records, the same spans and the same single site per record.
