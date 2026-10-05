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

Two things were wrong with that as a *guard*:

1. it was one frame, not the donor. A donor is a population of frames: 212 of the
   297 canonical structures draw frames that do not all occupy one rect, and in
   those the first frame is not reliably the largest. The old check would accept
   a size measured from one frame of a donor whose own animation draws three
   different rects.
2. the refusal stated a budget veto. Nothing here has measured the per-actor
   composition budget. CRASH-ROOT-CAUSE-001 measured a `0x200` budget on one
   actor and could not locate the allocation site, so the rule that sizes it is
   still **unresolved**. Saying "budget" claimed a measurement that does not
   exist.

## 2. The guard rule

An authored frame is admitted if and only if its footprint is **exactly** the
donor's proven composition shape, measured from the donor's own decoded records:

1. **`measure_donor_envelope(image, structure_offset, frame_at)`** walks every
   animation the donor structure's count byte names, skips the `pointer == 0`
   slots the canonical sparse arrays contain, decodes every frame each animation
   points at, and collects the set of frame rects `(width, height)`.
   * more than one rect -> **refuse the donor**: it proves no single composition
     shape, and the authored record copies one donor frame's geometry verbatim,
     so choosing a shape would be a guess.
   * exactly one rect -> that rect is the envelope, with its pixel count
     `w * h` and the number of pieces the frames carrying it hold.
2. **The donor's first frame must be self-consistent**: its frame box
   `(width, height)` must equal its single piece's stored extents
   `(dim_0, dim_1)`. That is the decoder's structural check, not an assumption;
   `sprite_graphics` records the frame box and does not require it to equal the
   pieces' union, so a donor whose record disagrees with itself is refused here
   rather than copied.
3. **`_require_cell_geometry`** then requires every authored sheet cell to be
   exactly the envelope: `(cell_width, cell_height) == (envelope.width,
   envelope.height)`. A larger cell is an unproven composition budget; a smaller
   cell has no measured placement, because the authored record copies the donor's
   own anchor (`piece.x`, `piece.y` and the frame's `min_x`/`min_y` fall out of
   the same decoded geometry) instead of centring anything.

The guard decides geometry only. It never authors a placement, an anchor or an
allocation, and `_encode_frame` is untouched, so for every input the old check
accepted the emitted bytes are unchanged.

## 3. The measured envelope

Measured on the canonical Buu's Fury image (sha256 `940ad5f0...`) with
`build/probe_donor_envelope.py`, which reads the registry entry, the structure,
each animation and each frame with the shipped decoders:

* **Cui's donor is sprite id 10** (`sprite_identity.SPRITE_ID_FLOOR` + entry 0,
  structure at file `0x6A89D0`, two animation slots, four frames): every frame is
  `32x32` at anchor `(-8, -24)`, one piece, packed OAM attributes `0x80002000`
  (8bpp, square, size 2, no flip), container kind 1.
  **Envelope: 32x32, 1024 bytes, 1 piece.** The authored cell is 32x32
  (`CELL_SIDE` in `tests/integration/test_sprite_new_project_rom.py`), so the Cui
  project sits exactly on the envelope.
* Corpus census over all 297 registry entries (the envelope every donor proves):

  | envelope | pieces | structures |
  |---|---|---|
  | 8x8 | 1 | 5 |
  | 16x16 | 1 | 8 |
  | 16x32 | 1 | 59 |
  | 32x16 | 1 | 2 |
  | 32x32 | 1 | 177 |
  | 32x64 | 1 | 4 |
  | 64x64 | 1 | 40 |
  | 96x64 | 2 | 1 |
  | 96x96 | 4 | 1 |

* **212 of the 297 structures draw more than one frame rect** and are therefore
  refused as donors (for example sprite 23: slots 0, 1 and 9 draw `16x32` at
  anchor `(0, -24)` while slot 4 draws `32x32` at `(-8, -24)`; sprite 42 mixes
  `32x64` and `64x64`; sprite 29 mixes `16x16` and `8x16`; sprite 47 mixes
  `32x48` and `16x64`). Four structures hold a rect drawn by more than one piece - sprite
  163's `96x64` and sprite 146's `96x96` (two and four pieces respectively) - and
  the envelope records the largest piece count among the frames sharing the rect,
  so a caller can see that the proven shape was reached by more than one piece
  rather than assume it. The multi-piece donor refusal still fires first, because
  the authored record holds one piece.

## 4. Cui result

Unchanged in every byte. The Cui donor's own frames are all exactly `32x32`, its
first frame is a single 32x32 piece, and the private sheets are 512x32 and
1024x32 pixel rows of 32-pixel cells, so the cell geometry already equalled the
envelope and the guard admits the project as before. The project route's parity
assertion still holds: the build emits
`033e04ba27ac8fcafe99df1f4f6cf2aa6f9a09445eee1ad15b707d2ff694ff57`, the image
SPRITE-NEW-ATTACHMENT-RUNTIME-PARITY-001 composed and ran.

## 5. Refusal cases

| case | refusal |
|---|---|
| authored cell larger than the envelope | `... but the donor's own frames prove exactly one composition shape, WxH, drawn as N piece(s) (B bytes); this write path copies the donor's proven geometry verbatim, and neither a larger frame (an unproven composition budget) nor a smaller one (an unmeasured placement) is authored here` |
| authored cell smaller than the envelope | the same refusal: the envelope is one rect and the record copies its anchor |
| donor frames disagree about their rect | `the donor structure at 0x...... draws frames of several shapes (16x32, 32x32), so it proves no single composition shape; choose a donor whose own frames all occupy one rect` |
| donor frame box contradicts its own single piece | `the donor's first frame declares a AxB frame box but its own piece is CxD; this write path copies the frame box, so a donor whose record disagrees with itself would author geometry the donor does not draw` |
| multi-piece donor, 4bpp donor, flipped donor, undecodable donor | unchanged from SPRITE-NEW-AUTHORING-CORE-001 |

## 6. Focused tests

| file | what it establishes |
|---|---|
| `tests/unit/test_sprite_identity_authoring.py` (7 new/updated cases) | a larger cell is refused; a smaller cell is refused; a donor with two frame rects is refused; a donor whose box contradicts its own piece is refused; the measured envelope is the rect the emitted records carry; a valid input emits identical bytes and the record's own geometry is still the donor's |
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

1. **No runtime proof of this guard.** The envelope is a property of the donor's
   own records; the claim that an authored actor drawing the donor's exact frame
   rect composes correctly on every actor that will be pointed at it is still a
   runtime claim, and the runtime proof so far covers one map-102 actor.
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
every ROM-gated test and the probes in `build/` never write to it. No ROM-derived
or art-derived artefact is tracked; every number above is a count, an offset, a
digest or a comparison against bytes read from the file at run time. The probes
are local working tools and are not part of the module or of any test.
