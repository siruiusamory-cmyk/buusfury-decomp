# SPRITE-NEW-PROJECT-SURFACE-001: the Cui case through the ordinary project build

A project authors a new actor-sprite identity and the one map actor that draws
it, and `webfoot build` emits the image. No planner is called by hand, no
research module is imported by the build path, and the result is byte-for-byte
the image the previous two tickets proved in the retail engine.

Measured 2026-10-05. Baseline `aba12576c6c357645f9ce7e9b81a5ab2e27dc2db` (the
merge of SPRITE-NEW-ATTACHMENT-RUNTIME-PARITY-001). Worktree
`sprite-new-project-surface-001`, branch `ticket/sprite-new-project-surface-001`.

## Verdict

**PASS** for this ticket's acceptance: the Cui case is authored through the
ordinary SDK project/build workflow, and the built image's SHA-256 equals the
recorded runtime-parity image exactly.

`sprite-new` is still **not shipped**, and this ticket does not change that
status. What remains is listed in section 6.

## 1. What the project model adds

`sprites/sprites.toml`, one document, holding exactly one identity and its actor:

```toml
[sprite.cui]
sprite_id = 307
donor_sprite_id = 10
free_palette_entries = [6, 8, 9, 103, 193, 217, 218, 223, 224, 225, 236]

[sprite.cui.animation.stand]
sheet = "sprites/cui/stand.png"
frames = 2

[sprite.cui.animation.walk]
sheet = "sprites/cui/walk.png"
frames = 4

[sprite.cui.actor]
map = "map:0102"
family = "map-sibling-08017da3"
position = [209, 580]
retained_raw = 0
data_pointer_raw = 142104172
behaviour_template = "map:0102/object:0007"
wander_box = [192, 544, 272, 624]
```

The document is loaded by `webfoot.project.model.AuthoredSprites` and reaches
disk only through `write_authored_sprites`, which is the mirror of
`write_authored_chunks`.

Three decisions are the whole model:

* **Exactly one identity per build.** An identity is added by growing the
  character registry and repointing the two literal words that name it
  (`graphics.CHARACTER_TABLE_REFERENCE_OFFSETS`), so a second identity would
  grow the same registry again and point the same two words at a different
  table. A document declaring two is refused.
* **Animation slots are ordered by name.** A TOML table has no order to inherit
  and the engine reads an animation by slot index, so the order is a stated rule
  rather than a file accident: `stand` before `walk`.
* **Three kinds of value stay apart.** Authored: the map, the position, the
  wander box. Carried verbatim: `retained_raw` and `data_pointer_raw`, the new
  object header's `+0x04` and `+0x0C` words, whose meanings are UNRESOLVED, with
  `_raw` suffixes and no invented meaning. Resolved: `behaviour_template`, a
  `map:NNNN/object:IIII` identity naming an existing slot of the same map's
  object array, whose inline behaviour entry the build copies. No ROM address is
  accepted from project source.

Refused shapes, each with its own test: two identities; no animations; more
animation slots than the structure's own count byte can state; an animation table
key that disagrees with the animation's own name; a sheet path that is absolute,
backslash-spelled, climbs out of the project or is not a PNG; a frame count
outside the one bound this project reads; a free palette entry of 0, of 256 or
repeated; a free palette entry the decoded corpus already draws; a retained word
that is not an unsigned 32-bit value; a behaviour template from another map, or
in the wrong identity form. A sprite id the appended registry entry does not
yield, and a claimed free palette entry that fails the corpus check, are refused
by the planners themselves rather than by the document model.

## 2. What the build path does

One new domain in `webfoot.build.build_project`, run after the dialogue domain
and before the graphics pixel domain (which the existing comment already pins as
last):

1. `sprite_authoring.materialize_authored_sprites` resolves the document against
   the verified image - the sheets, the free palette entries, the behaviour
   template - and then calls
   `sprite_identity.plan_new_sprite_identity`;
2. that plan's `reserved` spans are handed straight to
   `sprite_attachment.plan_new_map_actor` as the shared reservation set, so the
   appended object record and the re-emitted object array can only land clear of
   the identity;
3. both change lists, both allocation-provenance sets and both relocation sets
   merge into the ONE `plan_changes` call and the ONE `emit_image`, exactly like
   stats, text, chunks or transitions.

Two integration facts are worth naming because they are not optional:

* **The map domain yields the actor's `MapEntry` record.** The attachment
  planner rewrites that record's `+0x04` bound and `+0x14` array pointer itself,
  so `maps.changes(authored_maps=...)` now also receives the map an authored
  actor is appended to. Without the yield the two domains would collide on the
  same bytes.
* **The yield is why two combinations are refused.** A project that also edits a
  field of that map's record, or gives that map an authored placement expansion,
  would have that work silently dropped (or would fail later as a byte-range
  overlap), so both are refused up front, by name.

The manifest gains a `sprite_authoring` array holding the two planners' own
`to_json()` documents, so a reader can answer where sprite 307 landed without
re-deriving it. `validate` runs the same materialization and the same map-clash
check the build runs, so a project that cannot be built is refused at validation
rather than at the last step.

## 3. Parity

The recorded runtime-parity image is
`033e04ba27ac8fcafe99df1f4f6cf2aa6f9a09445eee1ad15b707d2ff694ff57`
(16 MiB, the "palette-grid" composition). SPRITE-NEW-ATTACHMENT-RUNTIME-PARITY-001
composed it from the same two production planners and then ran it in mGBA; it is
also the image SPRITE-NEW-RUNTIME-PARITY-001 recorded as its walking build.

Building the same case through the project workflow produces **that digest
exactly**, at the same length. Independent of the digest, the emitted image was
checked byte for byte against the canonical image:

* every canonical byte that differs lies in one of six published fields - the two
  32-bit registry words at `0x0003C0` and `0x01715C`, map 102's `+0x04` bound and
  `+0x14` array field, and object-palette entries 217 and 236 - and each of those
  fields did change: 14 canonical bytes in total;
* all ten retail object records are byte-identical to the canonical image, and
  the re-emitted object array carries their ten pointers verbatim;
* the new record is at `0x08801F38`, its array at `0x08801F0C` with 11 slots, its
  behaviour entry at `0x08801F54` leading with the class word `0x0800A7A1` and
  carrying the authored box `(192, 544, 272, 624)`;
* the identity's registry is at `0x088017C0` and its structure at `0x08801C68`,
  both above canonical EOF, and both allocations are `generated_expansion`
  provenance.

**One defect was found by building it, and it matters.** The first project-driven
build produced digest `c4268e9cb1f31becbb8b7c1f5887af143f8540844caa57f3db9ad3aee7d1981c`
with 7,952 differing bytes. The cause was the sheet reader: `SourceSheet` reads
cell `c` from pixel `c * cell_width * cell_height`, which is cell-major, while
the PNG's own bytes are row-major across the whole image. Handing over the file
order still produced a valid build - the identity simply drew a rearrangement of
the author's art, which compressed to 4,172 bytes instead of 6,080. The order is
now gathered explicitly, and `tests/unit/test_sprite_authoring.py` gives every
cell its own colour so that a reader which mislays that order fails rather than
merely differing.

## 4. Focused tests

| file | gate | what it establishes |
|---|---|---|
| `tests/unit/test_sprite_project.py` | `fast` | the document: round trip, writer determinism, every refusal, identity parsing |
| `tests/unit/test_sprite_authoring.py` | `fast` | a sheet PNG as the planner reads it: cell order per facing and per frame, dimension, alpha and file refusals |
| `tests/unit/test_rgb_png.py` | `fast` | the truecolour reader: RGB and RGBA, all five scanline filters at four bytes per pixel, and by-name refusals |
| `tests/integration/test_sprite_new_project_rom.py` | `rom` | the project route against the canonical image: the Cui parity case, the five required properties, determinism, the reservation-set contract, and the map-clash refusal on both the validate and the build route |

## 5. Safety

The canonical commercial image was re-read, never written: its SHA-256 is
asserted at the start of every ROM-gated test. Every build wrote a new image into
a temporary directory outside the work tree. No ROM-derived, art-derived or
machine-specific artefact is tracked: the evidence here is digests, offsets and
counts, and the private source sheets are referenced only through an environment
variable whose documented default is a relative path inside the checkout.

## 6. What this does not claim

* **No frame-composition budget.** The planner still refuses to let an author
  choose frame geometry: every authored frame copies the donor's own first frame,
  so the budget is unchanged rather than modelled. Attaching an identity to an
  actor that draws smaller frames than its donor remains the open case.
* **No direction-slot-to-facing mapping.** The engine's four direction slots are
  written in sheet order and their screen meaning is still unresolved
  project-wide.
* **No authoring surface.** This ticket adds the project model and the build
  path, not an editor: a person writes `sprites/sprites.toml` and supplies the
  sheet PNGs. There is no GUI, no CLI subcommand, and no generalization of the
  existing authored-placement document.
* **No capability-status change.** `src/data/capabilities.json` is untouched, so
  the public progress surface still reports `sprite-new` as missing. Marking it
  shipped is a separate, deliberate decision and is not taken here.

## 7. Reproduce

```sh
SPRITE_NEW_CANONICAL_ROM=<canonical image> python -m pytest tests/unit/test_sprite_project.py tests/unit/test_sprite_authoring.py tests/unit/test_rgb_png.py
SPRITE_NEW_CANONICAL_ROM=<canonical image> SPRITE_NEW_CUI_SHEETS=<directory holding stand.png and walk.png> python -m pytest tests/integration/test_sprite_new_project_rom.py
```

The second command is the parity proof. Without the private sheets it still
builds the same route on art the test draws itself, which is the half that runs
on any machine holding the canonical image.

The research composition that produced the recorded digest independently is
`tools/research/sprite_new_attachment_parity.py`, which takes the same canonical
image and sheets and reports both variants.
