# SPRITE-NEW-COMPOSITION-GUARD-001: the proven composition shape

Baseline `954a4027263c428fb2b0a48fcf78e478ec9a77b5` (`origin/master`, the
SPRITE-NEW-PROJECT-SURFACE-001 merge), branch
`ticket/sprite-new-composition-guard-001`.

The ticket adds one production guard to the authored-sprite path and nothing
else. No GUI, no CLI, no change to sprite allocation or attachment behaviour, and
no attempt at arbitrary sprite composition.

## 1. What was already enforced, and what was not

`plan_new_sprite_identity` has never let an author choose frame geometry. It
decoded the donor's **first frame**, required it to hold exactly one piece, and
required every authored sheet cell to equal that piece's stored extents. The
refusal message claimed the reason was "a per-actor composition budget this write
path does not model".

Three things were wrong with that as a *guard*:

1. **CONFIRMED** it was one frame, not the donor. A donor is a population of
   frames: 136 of the 297 canonical structures draw frames that do not all occupy
   one rect. The old check read the first frame alone, so a donor whose later
   animations draw a different rect was still admitted on the strength of a frame
   that does not describe it.
2. **UNKNOWN** is the veto itself. Nothing here has measured the per-actor
   composition budget. CRASH-ROOT-CAUSE-001 measured a `0x200` budget on one actor
   and could not locate the allocation site, so the rule that sizes it is still
   unresolved. Saying "budget" claimed a measurement that does not exist.
3. **CONFIRMED** it compared a size and nothing else. The donor's frame record also
   carries the anchor the rect is drawn at, and 31 canonical structures draw one
   rect at several anchors - sprite 94 to sprite 99 place `32x32` at `(-8, -26)`,
   `(-8, -25)` and `(-8, -24)`. Copying frame 0's anchor there would be a placement
   nothing measured, which is the same objection as a smaller cell.

## 2. The guard rule

An authored frame is admitted if and only if its footprint is **exactly** the
donor's proven composition shape, measured from the donor's own decoded records:

1. **`measure_donor_envelope(image, structure_offset, frame_at)`** walks every
   animation the donor structure's count byte names, skips the slots whose
   animation word is null (an observation: the canonical arrays carry them, the
   word is zero, and zero is not an address in this image), decodes every frame
   each animation points at, and collects the set of frame rects
   `(width, height)` together with the anchors `(min_x, min_y)` they are drawn at.
   * more than one rect -> **refuse the donor**: it proves no single composition
     shape, and the authored record copies one donor frame's geometry verbatim,
     so choosing a shape would be a guess.
   * one rect at more than one anchor -> **refuse the donor**: it proves no single
     placement either.
   * one rect at one anchor -> that pair is the envelope, with its pixel count
     `w * h` and the largest piece count among the frames carrying it.
2. **The donor's first frame must be self-consistent**: its frame box
   `(width, height)` and anchor `(min_x, min_y)` must equal its single piece's
   stored extents `(dim_0, dim_1)` and placement `(x, y)`. The decoder does **not**
   require this - `sprite_graphics` records the frame box and states that it need
   not equal the pieces' union - so this is the write path's own structural check,
   and a donor whose record disagrees with itself is refused here rather than
   copied.
3. **The anchor is part of the proven shape.** A donor whose frames share the rect
   but place it at different anchors proves no single placement, and is refused
   for that reason before the cell is considered; 31 of the canonical structures
   are refused this way. Every authored frame takes the envelope's anchor.
4. **`_require_cell_geometry`** then requires every authored sheet cell to be
   exactly the envelope: `(cell_width, cell_height) == (envelope.width,
   envelope.height)`. A larger cell is a composition shape this path cannot prove;
   a smaller cell has no measured placement, because the authored record copies
   the donor's own anchor (`piece.x`, `piece.y` and the frame's `min_x`/`min_y`
   fall out of the same decoded geometry) instead of centring anything.

The guard decides geometry only. It never authors a placement, an anchor or an
allocation, and `_encode_frame` is untouched, so for every input *both* checks
accept - the old piece-equality check and the new envelope check - the emitted
bytes are unchanged. The new check accepts a subset of the old one's inputs: a
donor with several frame rects, a donor with one rect at several anchors and a
donor whose record contradicts itself were all accepted before and are refused
now.

Two limits of the check are deliberate. Only the **first frame** is compared
against its own piece, because that frame is the one whose geometry the authored
record copies; the remaining frames are read for their box and anchor and their
piece records are not re-derived. And the envelope is measured from the frame
record's stored box rather than from a union recomputed over its pieces, so the
frame box is trusted exactly where `sprite_graphics` records it and does not
require it to equal the pieces' union.

## 3. The measured envelope

**Local observation, 2026-10-05**, over the canonical image. The figures below are
**CONFIRMED** by running the shipped function over every registry entry; what they
do *not* establish is what the retail engine does with an authored frame, which is
**UNKNOWN** here and is item 1 of section 7.

The census probe is `build/census_composition_guard.py`, a local working tool that
is ignored by git rather than tracked, so it cannot be run from a fresh clone. It
is short and self-contained, and this is its procedure:

1. read the canonical image and assert its sha256;
2. take the 297 registry entries from the address the profile declares
   (`layout.actor_sprites.character_table_address`, `0x086B6BDC` in
   `tools/webfoot/data/roms.yaml`);
3. for each entry, call the shipped `measure_donor_envelope` with a
   `sprite_graphics.decode_frame` over the pointer's raw window offset - the same
   decode the planner performs, without the planner's own `_file_offset` bounds
   message - and tally the refusals by message;
4. print the admitted envelopes and the highest envelope piece count.

```sh
python build/census_composition_guard.py
```

The image is the canonical Buu's Fury ROM, sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, 8,388,608
bytes, whose hash is asserted by every ROM-gated test and by the probe itself.

* **Cui's donor is sprite id 10** (`sprite_identity.SPRITE_ID_FLOOR` + entry 0,
  structure at file `0x6A89D0`, two animation slots, four frames): every frame is
  `32x32` at anchor `(-8, -24)`, one piece, packed OAM attributes `0x80002000`
  (8bpp, square, size 2, no flip), container kind 1.
  **Envelope: 32x32, 1024 bytes, anchor (-8, -24), 1 piece.** The authored cell is
  32x32 (`CELL_SIDE` in `tests/integration/test_sprite_new_project_rom.py`), so
  the Cui project sits exactly on the envelope.
* Corpus census over all 297 registry entries: **130 admit exactly one rect at one
  anchor, 167 are refused** - 136 because their own frames disagree about the
  rect, 31 because their frames share a rect but place it at more than one anchor.
  The admitted 130 split:

  | envelope | pieces | structures |
  |---|---|---|
  | 32x32 | 1 | 50 |
  | 16x32 | 1 | 48 |
  | 64x64 | 1 | 15 |
  | 16x16 | 1 | 7 |
  | 8x8 | 1 | 5 |
  | 32x16 | 1 | 2 |
  | 32x64 | 1 | 1 |
  | 96x64 | 2 | 1 |
  | 96x96 | 4 | 1 |

  Two admitted structures - sprite 146 (`96x96`, four pieces) and sprite 163
  (`96x64`, two pieces) - have an envelope whose frames hold more than one piece,
  which is what `DonorEnvelope.piece_count` records. It is the largest piece count
  among the frames sharing the rect, so the refusal message's "drawn as N pieces"
  names the worst case. **CONFIRMED** by decoders: their *first* frames hold four
  and two pieces, so both are then refused by the single-piece rule, before the
  cell is considered; the envelope measurement is what admits them for a moment.
* Examples of the refusals: sprite 23 (slots 0, 1 and 9 draw `16x32` at anchor
  `(0, -24)` while slot 4 draws `32x32` at `(-8, -24)`), sprite 29 (`16x16` and
  `8x16`), sprite 42 (`32x64` and `64x64`), sprite 47 (`32x48` and `16x64`);
  sprites 94-99 draw one `32x32` rect at `(-8, -26)`, `(-8, -25)` and `(-8, -24)`,
  which is the anchor refusal. 243 of the 297 animation arrays carry at least one
  null pointer in a slot; the canonical total is 4,070 slots, and a null slot's
  word is zero, which is not an address in this image, so it names no record to
  decode.

## 4. Cui result

**CONFIRMED**, unchanged in every byte. The Cui donor's own frames are all exactly
`32x32` at one anchor `(-8, -24)`, its first frame is a single 32x32 piece, and the
private sheets are 512x32 and 1024x32 pixel rows of 32-pixel cells, so the cell
geometry already equalled the envelope and the guard admits the project as before.
The project route's parity assertion still holds: the build emits
`033e04ba27ac8fcafe99df1f4f6cf2aa6f9a09445eee1ad15b707d2ff694ff57`, the image
SPRITE-NEW-ATTACHMENT-RUNTIME-PARITY-001 composed and ran. Measured by the
ROM-gated tests below, and re-run at the frozen candidate.

## 5. Refusal cases

| case | refusal |
|---|---|
| authored cell larger than the envelope | `animation '...' is authored at AxB, but the donor's own frames prove exactly one composition shape, WxH at anchor (X, Y), drawn as N piece(s) (B bytes); this write path copies the donor's proven geometry verbatim, and neither a larger frame (an unproven composition shape) nor a smaller one (an unmeasured placement) is authored here` |
| authored cell smaller than the envelope | the same refusal: the envelope is one rect and the record copies its anchor |
| donor frames disagree about their rect | `the donor structure at 0x...... draws frames of several shapes (16x32, 32x32), so it proves no single composition shape; choose a donor whose own frames all occupy one rect` |
| donor frames share a rect but not an anchor | `the donor structure at 0x...... draws its 32x32 frames at several anchors ((-8, -26), (-8, -25), (-8, -24)), so it proves no single placement; choose a donor whose frames all sit at one anchor` |
| donor frame box or anchor contradicts its own single piece | `the donor's first frame declares a AxB frame box at (X, Y) but its own piece is CxD at (x, y); this write path copies the frame record, so a donor whose record disagrees with itself would author geometry the donor does not draw` |
| every animation slot null | `the donor structure at 0x...... names no decodable frame, so it proves no composition shape` |
| slot 0 null but a later slot valid | refused safely, with the `_file_offset` message that 0x00000000 is not a file offset in this image: `_donor` decodes slot 0 for the geometry it copies, while the envelope measurement skips null slots |
| multi-piece donor, 4bpp donor, flipped donor, undecodable donor | unchanged from SPRITE-NEW-AUTHORING-CORE-001 |

## 6. Focused tests

| file | what it establishes |
|---|---|
| `tests/unit/test_sprite_identity_authoring.py` (9 new cases plus one whose refused message changed) | a larger cell is refused; a smaller cell is refused; a donor with two frame rects is refused; a donor with one rect at two anchors is refused; a donor whose box contradicts its own piece is refused; a null animation slot is skipped; a donor whose every slot is null is refused; a null first slot is refused before the geometry is read; the measured envelope is the rect the emitted records carry; a valid input is still deterministic and still carries the donor's own record geometry |
| `tests/integration/test_sprite_identity_rom.py` (3 new cases) | on the canonical image: the donor's measured envelope is `32x32`, 1 piece, 1024 bytes and is what the emitted records carry; a doubled cell and a halved cell are both refused |
| `tests/integration/test_sprite_new_project_rom.py` (unchanged) | the Cui project still emits the recorded runtime image byte for byte |

```
SPRITE_NEW_CANONICAL_ROM=<canonical image> python -m pytest \
  tests/unit/test_sprite_identity_authoring.py \
  "tests/integration/test_sprite_identity_rom.py" -k "envelope or refused"
SPRITE_NEW_CANONICAL_ROM=<canonical image> \
SPRITE_NEW_CUI_SHEETS=<directory holding stand.png and walk.png> python -m pytest \
  "tests/integration/test_sprite_new_project_rom.py::test_the_cui_project_reproduces_the_runtime_parity_image"
```

## 7. Remaining blockers to sprite-new shipping

Unchanged by this ticket, and in this order:

1. **UNKNOWN: no runtime proof of this guard.** The envelope is a property of the
   donor's own records; the claim that an authored actor drawing the donor's exact
   frame rect composes correctly on every actor that will be pointed at it is still
   a runtime claim, and the runtime proof so far covers one map-102 actor.
2. **The per-actor composition budget is still unmodelled.** An authored cell
   cannot exceed the donor's proven rect, so a genuinely larger sprite - the
   common want - is still refused rather than sized.
3. **No direction-slot-to-facing mapping**, unresolved project-wide.
4. **No authoring surface**: a person writes `sprites/sprites.toml` and supplies
   the PNGs by hand.
5. `src/data/capabilities.json` is untouched, so the public surface still reports
   `sprite-new` as missing.

## 8. Safety

Read-only against the canonical image: its SHA-256 is asserted at the start of
every ROM-gated test and the census probe in `build/` never writes to it. No
ROM-derived or art-derived artefact is tracked; every number above is a count, an
offset, a digest or a comparison against bytes read from the file at run time. The
census probe is a local working tool, not part of the module or of any test.
