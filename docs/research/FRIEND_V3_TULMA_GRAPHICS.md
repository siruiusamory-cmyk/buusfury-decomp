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
| candidate | `build/tulma001/v3-tulma-graphics.gba` | `aec5aa9ff1cabe454ae314721a647b31fe75102af96e6cde9b0a99f91bc1c7a6` | 10,141,224 |

The canonical image was re-hashed before and after every command in this record and is
unchanged. The base image was re-hashed after the write and is unchanged; the writer
refuses to run unless its `--expect-sha256` equals what it read.

The candidate is the base plus 7,814 appended bytes, with 8,140 changed bytes inside spans
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
5. **Determinism.** Two runs of the writer over the same base and assets produce the same
   digest, and the base is re-hashed unchanged.
6. **Tests.** `tests/unit/test_tulma_graphics.py` covers the pure decisions (colour to
   index, the chroma key, the transparent key, the ambiguous-colour refusal, the 5-bit
   match, the crop window, the mirror, one container with two words, the disagreement
   refusal, stale base, overlap, the append pad, and diff confinement).
   `tests/integration/test_tulma_graphics_rom.py` runs the writer over the canonical image
   with sheets it derives from that image, so the whole path is exercised without carrying a
   pixel of anyone's art, and asserts each of the four properties above plus the refusal of a
   facing that is not the mirror of its pair.

## 6. Runtime evidence

To be recorded. The writer and the static checks above establish the bytes; only a session
establishes what the engine draws. The run must follow `docs/skills/mgba-runtime.md`: the
tracked launcher, an exact image digest, an allowlisted read-only observer with a liveness
channel, and a session the operator ends.

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

- No runtime observation yet. Nothing in this record says the engine drew Tulma.
- No claim about directions beyond the donor's own cell order: the sheets are read
  direction-major, `cell = direction * frames_per_facing + frame`, which is the convention
  `sprite_identity.SourceSheet.slot_cell_index` states, and the walk proves it for this donor
  because all 32 cells align to the donor's 32 frames with zero mismatches. Which compass
  direction each slot is remains unestablished, unchanged by this ticket, and the donor's own
  arrangement is preserved either way.
- No claim about cutscene behaviour beyond this: the write is to the character's own
  containers, so every route that draws sprite id 41 draws the new art. No scripted reload
  path was found that could substitute another payload, and no such path is claimed to
  exist or not to exist for other characters.
- No claim about the 45 unreferenced portrait run entries or the 22 with no located
  consumer.
- No art judgment: the supplied art is reproduced as faithfully as the format allows, which
  here means exactly, because the crop loses no pixel and no colour had to be approximated.
