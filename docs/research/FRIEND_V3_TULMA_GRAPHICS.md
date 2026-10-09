# Tulma graphics: retail Bulma's own containers, redrawn

FRIEND-V3-TULMA-GRAPHICS-001. The ticket supplies four PNGs for the friend's modified
image and asks for them in the game. This is the evidence record: what the supplied art
turned out to be, what was written, every guard that refused or accepted a byte, and what
is claimed and not claimed.

Nothing here is a substitute for the runtime section. Until that section names a capture
directory, no claim in this document is a claim about what the engine drew.

## 1. Images

| role | path | sha256 | size |
| --- | --- | --- | --- |
| canonical (immutable) | `roms/Dragon Ball Z - Buu's Fury (U).gba` | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` | 8,388,608 |
| base (the approved content foundation) | `build/fv3ctp001/v3-complete-text-pass-2.gba` in the text-pass worktree | `20f2c14066648bb7ef2fad60ffc8d904121e8cd4f1c1fe171bfd80ca8551746c` | 10,133,410 |
| candidate | `build/tulma001/v3-tulma-graphics.gba` | `ef939dcd8c600fe52044df08d930d9dff1b1ceed52698aff8b21c8eef15b38b4` | 10,140,972 |
| final candidate (graphics plus the owner-authorized dialogue rewrite, section 9) | `build/tulma001/v3-tulma-final.gba` | `a4c12a95818cab2781165658d25f2463bc6fe0f87040620a7c89f0034c5b49db` | 10,140,972 |

The canonical image was re-hashed before and after every command in this record and is
unchanged. The base image was re-hashed after the write and is unchanged; the writer
refuses to run unless its `--expect-sha256` equals what it read.

The candidate is the base plus 7,562 appended bytes, with 7,888 changed bytes inside spans
the writer's own report attributes to a named owner and **zero changed bytes outside them**.

## 2. The supplied art, measured before anything was written

The four PNGs are opaque, carry a `(255,0,255)` chroma key rather than an alpha hole, and
every colour they use is stated as `v << 3`. Measured properties, each of which decided
part of the write:

- **The sheets are retail Bulma's own art recoloured, not new art.** Each 32x32 sheet cell
  cropped to the window x in [8,24) reproduces one of the donor's 16x32 frames: the
  silhouette union equals the intersection on all 32 frames, and the partition of positions
  by colour in the cell equals the partition by index in the donor frame. The artist
  recoloured the extracted frames; they did not redraw the figure.
- **The crop is lossless.** The figures occupy x 8..23 of each cell, so the donor's 16x32
  rect is recovered with no pixel dropped. That is why no frame, piece, anchor or
  composition size changes: the write fills the rect the donor already has.
- **Every colour already exists in the object palette.** Compared at 5-bit resolution, which
  is the hardware's own, 0 of 28, 30, 27 and 51 colours are missing from the portrait and
  the three sheets. So **no palette entry is written**, which matters because that palette
  is shared with every other actor and every portrait: an override changes indices, never
  colours (`GRAPHICS_PIXEL_OVERRIDE.md` section 2).
- **The portrait is retail Bulma's portrait raster, re-indexed.** Position by position it is
  slot 17's own index raster under a per-index colour map, with exactly one pixel differing.
  Its hair moves from palette index 187 (teal, `(0,115,115)`) to the colour index 200
  already carries (`(240,192,112)`), so the change is indices, not palette bytes. Its 32
  chroma-key pixels become index 0, the hardware transparent key, which is the hole the
  artist drew.
- **A portrait payload is a LINEAR raster, not swizzled tiles.** CONFIRMED by rendering the
  retail container's own 4,096 decoded bytes as a linear 64x64 raster: that reproduces the
  retail portrait. Reading the same bytes as swizzled 8x8 tiles produces noise. The sprite
  path is the opposite, which is why the two cannot share an encoder.

## 3. The target, and the trap

In the foundation **the only appearance record whose label reads `Bulma` is record 22,
which is retail Chi-Chi**. Retail Bulma is record 20 and the foundation labels her `Tulma`.
In the v3 rename base both records still read `Bulma`. Nothing in the writer keys on a
label: the target is the sprite-definition registry entry for **sprite id 41** (run index
31 of the 297-entry table at `0x086B6BDC`), structure at file `0x6A9DFC`, plus **portrait
slot 17** of the array at `0x086F393C`.

Provenance was measured, not assumed:

- sprite id 41 is named by exactly one appearance record (record 20), and its 22 containers,
  every frame, piece and attribute are byte-identical between the canonical image, the v3
  rename base and the foundation, so this character's art was untouched by every earlier
  friend pass and this write starts clean;
- seven map-sibling object records name a sprite id directly (`+0x10`, factory word
  `0x08017DA3`) and four of them name sprite 41, so the identity that must change is the one
  behind registry entry 31 itself. That is what this write does, which is also why it cannot
  be bypassed at runtime by a scene that resolves the character through a different route;
- Chi-Chi's sprite id 66 is named by exactly one record (record 22) and shares nothing with
  sprite 41: no container, animation, frame or portrait slot is common to the two.

## 4. What was written

| what | count | effect |
| --- | --- | --- |
| sprite 41 containers | 22 | 21 appended, 1 written in place (`0x3FD2E8`) |
| portrait slot 17 container | 1 | appended, the array word at file `0x6F3980` rewritten |
| reference words rewritten | 31 | every piece word naming a moved container |
| palette entries written | 0 | the object palette is byte-identical |

Placement rule: a re-encoded payload is written in place when it fits the container's
measured packed extent, and appended above the end of the image otherwise, with the word
that names it rewritten in the same batch. The packer is not competitive (median 1.06x), so
22 of 23 payloads had to move; the original payload bytes are left byte-intact in every
case, so a reference this writer did not discover still reaches the art it always reached.

**A defect this ticket found and fixed, and the guard that now prevents it.** The first
implementation repointed one piece word per container. Nine of the donor's containers are
named by two pieces each, because retail renders direction 3 by naming the direction-2
container under a horizontal flip. Repointing only the first word left direction 3 drawing
the untouched retail container: the exact "retail art during a scripted event" symptom the
ticket asks about, produced by the tooling rather than by the engine. The reopen check
below caught it before any runtime run, and a test now asserts that every container named
twice carries both of its words.

**A defect the runtime session found, and why the static checks could not.** The first
candidate rendered the sprite correctly and the portrait as noise. The portrait payload is a
linear raster, and the writer had put it through the sprite encoder, which swizzles 8x8
tiles. The reason no static check caught it is the part worth keeping: decode (unswizzle)
then re-encode (swizzle) round trips **byte-exactly**, so the writer's own reopen check
compared the art through the same wrong model and agreed with itself. A format guard that
shares the writer's assumption cannot see a wrong assumption. The fix is a dedicated
`plan_portrait`, which packs the raster straight, and a check that compares the raw payload
rather than an unswizzled reading of it. A unit test asserts the bytes actually written and
that they are not the swizzled alternative.

## 5. Static verification

1. **Round trip.** Every one of the 32 frame cells of sprite 41 was re-read from the
   candidate and decodes to the raster its own sheet cell states, across 22 distinct
   containers, in all four directions including the flipped one. The portrait container
   decodes to its supplied raster.
2. **Reopen.** `run()` walks the written image again and requires the set of containers the
   frames name to be exactly the set it placed, and each to decode to the art placed. A
   container that moved while one of its pieces stayed behind is a refusal here.
3. **Diff confinement.** The output differs from the base only inside spans the report
   attributes to an owner. That is what makes "every existing modification is preserved" a
   measurement rather than a promise: no text byte, no stat byte, no other character's
   graphic and no palette byte can have changed.
4. **Chi-Chi untouched.** Every container reached by sprite 66's frames is byte-identical in
   the candidate and the base.
5. **Determinism.** Two runs of the writer over the same base and the same four assets
   produce byte-identical output and reports that differ only in the
   output path they name, and the base image is re-hashed unchanged after each run.
6. **Tests.** `tests/unit/test_tulma_graphics.py` covers the pure decisions (colour to
   index, the chroma key, the transparent key, the ambiguous-colour refusal, the 5-bit
   match, the crop window, the mirror, one container with two words, the disagreement
   refusal, stale base, overlap, the append pad, and diff confinement).
   `tests/integration/test_tulma_graphics_rom.py` runs the writer over the canonical image
   with sheets it derives from that image, so the whole path is exercised without carrying a
   pixel of anyone's art, and asserts each of the four properties above plus the refusal of a
   facing that is not the mirror of its pair, and that the portrait payload is written as the
   linear raster and not as the swizzled alternative. Both files pass: 23 tests.
7. **A red test that is not this ticket's.** `tests/integration/test_graphics_rom.py::test_`
   `verified_graphics_pointers_join_the_common_reference_graph` fails on this baseline with
   11,304 references against an expectation of 11,302. It fails when run alone, it reads
   only the canonical image and the tracked SDK, and the file was last changed before later
   changes to `tools/webfoot/graphics.py` and `tools/webfoot/profile.py`, so the expectation
   looks stale rather than the walk wrong. It is disclosed here and left alone: repairing it
   is a separate ticket's scope, not this one's.

## 6. Runtime evidence

Session `tulma001-encounter-6`, run directory `build/gfximport001/tulma001-encounter-6`,
candidate `aec5aa9f` (the swizzled-portrait build), battery save `roms/v3.sav`, mGBA
`0.11.0.0`, no savestate. The operator booted the image, loaded the saved game and reached
map 134; the window was closed by hand, which is the documented way a session ends, so
`liveness.csv` rather than `proof.txt` is the instrument record.

What the captures show, and what they do not:

- **The instrument ran.** 11 settled screens latched between frames 46 and 6547, with a
  heartbeat every 120 frames throughout, so a silent target would have been a real negative
  rather than an unproven instrument. Settles 4 to 11 are gameplay on map 134.
- **The sprite is right.** In settle-08 the dialogue reads "It's great that Yamcha is back.
  Everyone seems so happy to be together." and the overworld figure renders normally. That is
  one written container streamed by the engine and drawn.
- **The portrait was wrong, and that is the finding.** The portrait cell in the same screen
  is noise. Diagnosed from the image, not from opinion: the retail container's payload
  rendered as a linear raster is the retail portrait, and the candidate's payload rendered
  the same way is noise, so the payload had been swizzled when it must not be. Section 4
  records the fix and why every static check passed anyway.
- **A confirmation session, `tulma001-encounter-8`, on candidate `ef939dcd`.** The portrait
  renders as the supplied Tulma art beside the same dialogue line (settle-10), and the
  operator confirmed it on screen. Tested mechanically as well: the engine's object tile
  region 0x06010000..0x06018000 holds the authored container `0x3fce94` (sprite 41's stand,
  direction 0) on every gameplay settle, which is the authored payload streamed into VRAM.
  One container is the expected figure, because the engine keeps one facing resident at a
  time.
- **The live object palette equals the image's table in all 256 colours.** One entry, index
  2, differs in raw halfwords only: the ROM holds `0xFFFF` and the engine `0x7FFF`, the same
  five channels with the unused top bit cleared. The analysis compares colours with that bit
  masked, and says why, because comparing raw halfwords reported a mismatch that is not one.
  The live background bank is a different table, which is consistent with the palette-write
  enumeration in section 7, and the difference follows from the engine's own copy.

The rig: mGBA `0.11.0.0` read from the binary, the candidate digest and size checked, no
running mGBA, no savestate (a state would restore VRAM a previous run assembled, so the area
has to be built during the session). The launcher is the tracked one the graphics-import
proof already uses, and this ticket adds only the observer, registered in the injector
allowlist and accepted by its `-CheckOnly` gate. One trap is worth recording because it cost a
launch: the observer names the image sizes it accepts, so a new candidate size throws on load
and the launcher reports "Lua script did not report ready", which reads like an injection
fault and is not one.

```text
powershell -NoProfile -ExecutionPolicy Bypass -File tools\runtime\start_gfximport001_live.ps1 `
  -RomPath build\tulma001\v3-tulma-graphics.gba `
  -RomSha256 ef939dcd8c600fe52044df08d930d9dff1b1ceed52698aff8b21c8eef15b38b4 `
  -ExpectedRomSize 10140972 -Label tulma001-encounter-8 `
  -LuaPath tools\runtime\tulma001_tulma_proof.lua -SavePath roms\v3.sav

powershell -NoProfile -ExecutionPolicy Bypass -File tools\runtime\finish_gfximport001_session.ps1 -Label tulma001-encounter-8
```

The launcher prints the run directory and exits holding no wait loop; the operator boots the
image, loads the saved game, walks to a Tulma appearance and closes the window. The observer
then has, per settled screen, a screenshot plus full VRAM, palette and OAM dumps, so the claim
is checked against the object-tile bytes rather than judged from a picture. The three
instrument states of the runtime skill's section 8 are reported when this section is
completed: target silent with a silent liveness channel is no evidence, target silent with the
heartbeat firing is a real negative, and anything drawn is execution observed.

## 7. The palette question, answered

The ticket's owner asked not to be bound by the shared palette. Measured verdict, from a
complete enumeration of every site that writes palette RAM:

- the source is always the single global table at `0x0805652C` (28 copies), or a fade of
  palette RAM's own contents, or a clear. No path takes a palette pointer from a character,
  appearance, sprite-definition or actor structure, so **no per-character palette exists**;
- OBJ palette RAM is one 256-entry bank, and the OAM palette-bank field is ignored in
  256-colour mode, which every one of the 11,005 piece records sets. Two characters on
  screen therefore cannot have different palettes: the constraint is structural, not policy;
- within that one bank there are 240 entries used by actor-sprite graphics and 219 by the
  155 portraits, and **11 entries are referenced by neither**: indices 6, 8, 9, 103, 193,
  217, 218, 223, 224, 225, 236. The SDK can prove only the actor-sprite half, since UI and
  HUD payloads share the bank and are not decoded.

So the freedom this image has is: 256 shared colours, 11 candidate spare entries, and
re-quantisation. That is enough for this ticket, which needs none of them. Making it more
than that is a separate ticket, filed with this evidence.

## 8. Not claimed

- Runtime observation IS claimed, for the states section 6 names and no others: the sprite was
  drawn in session 6, the portrait in session 8, and the two dialogue lines in session
  `tulma001-dialogue-2`. Nothing here claims a state that was not on a screen in one of those
  sessions, and no cutscene beyond the one that was played.
- No claim about directions beyond the donor's own cell order: the sheets are read
  direction-major, `cell = direction * frames_per_facing + frame`, which is the convention
  `sprite_identity.SourceSheet.slot_cell_index` states, and the walk proves it for this donor
  because all 32 cells align to the donor's 32 frames with zero mismatches. Which compass
  direction each slot is remains unestablished, unchanged by this ticket, and the donor's own
  arrangement is preserved either way.
- No claim about cutscene behaviour beyond this: the write is to the character's own
  containers, so every route that draws sprite id 41 draws the new art. No scripted reload
  path was found that could substitute another payload, and no such path is claimed to
  exist or not to exist for other characters. The scene the dialogue rewrite was confirmed in
  is the same World Tournament area, and no other scene was played.
- No claim about the 45 unreferenced portrait run entries or the 22 with no located
  consumer.
- No art judgment: the supplied art is reproduced as faithfully as the format allows, which
  here means exactly, because the crop loses no pixel and no colour had to be approximated.
- One thing outside this ticket's control, recorded because it affects any ROM claim: during
  the work, the canonical image's shared inode was briefly written in place by something this
  session did not run, which made the ROM-gated test skip until it was restored. The canonical
  is intact and verified, and the observation is recorded in the cross-session store rather
  than here, because attributing it is not this ticket's business.

## 9. The dialogue rewrite, an owner-authorized expansion

The ticket's own text forbids expanding into dialogue rewrites. The owner authorized this one
in the same session, so it is recorded here rather than left to another document; the tool is
`tools/research/apply_tulma_dialogue.py` and the reusable procedure is the
`log1-friend-dialogue-rewrite` skill.

**What changed.** Two lines in the World Tournament registration scene, each in its own
speaker's record slot:

| slot (decoded offset) | speaker | was | now |
| --- | --- | --- | --- |
| 60182 | Bulma | `Isn't this wonderful? Our family is back together again!` | `Look at how mad Tulma is! Do you think I went too far this time?` |
| 60294 | Tulma | `It's great that <player> is back. Everyone seems so happy to be together.` | `That bitch! She knew I was going to wear this!` |

**Why it is a byte-exact write and not a container rebuild.** Selectors 0 through 5 of this
image's dialogue table are Webfoot containers of kind 0, the stored form: the payload after the
8-byte header is the decoded stream itself, and `webfoot_lz.pack` cannot emit kind 0. So the
text is edited where it lies.

**Why the two records were laid out together.** A record's length lives in its handle, and the
records here are back-to-back with no terminator unit. Bulma's new line needs 128 bytes where
her span held 112, so it cannot grow in place. Her record and Tulma's are contiguous (112 + 138
= 250 bytes) and the two replacements need 220, so the pair is re-laid out inside its own
combined region and both handles are rewritten to match. Nothing else in the container moves,
which is what keeps every other record's absolute offsets valid. The writer refuses when the
records are not adjacent or when the pair has no room, because either case needs a container
re-layout, which is a different mechanism.

**A defect this expansion found, in my own mapping.** The first version had the two speaker
labels the wrong way round, so each new line landed in the other character's record and the
game displayed them swapped. The owner caught it on screen. The fix is the slot-to-speaker
assignment, and the lesson is worth keeping: a line's speaker is which record the scene asks
for, so the slot is the identity and only the wording may move.

**Verification, and it is exhaustive rather than sampled.** Every record in the image was read
before and after with the engine's own reader: 2,814 records both times; exactly two old
handles no longer exist and exactly two new ones do, each reading its own speaker's line with
no padding; the only other records whose text changed are the two enclosing scene views, which
is expected because they cover the same bytes; and no record anywhere still holds the old
wording. The image diff is 120 bytes: 116 in the re-laid text region and 4 in the two handle
words. The container's packed size and the table word are unchanged.

**Runtime confirmation.** Session `tulma001-dialogue-2` on the final candidate
`a4c12a95`: both lines read as written, in the right characters' mouths, with the portrait from
section 6 beside them. The owner confirmed it on screen.

**Not claimed for this expansion.** The wording of any other line, any record's length or
handle beyond these two, who speaks a line (that is the scene's actor, not the text record),
which portrait a scene shows, or any scene other than the one played.
