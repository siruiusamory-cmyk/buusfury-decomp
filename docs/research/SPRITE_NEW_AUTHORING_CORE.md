# SPRITE-NEW-AUTHORING-CORE-001: the new-identity mechanism as an SDK primitive

Baseline `origin/master` = `70dacdd5ad7829c940c438e2573e47ec476a3108` (the merge
that brought the movement and facings evidence in). Ticket branch
`ticket/sprite-new-authoring-core-001`. The canonical image was read only; it is
re-verified by digest before and after every run below (`940ad5f0...36f059e`), and
every expectation in the ROM-gated suite is a count, an address, an index or a
comparison against bytes read from the file at run time.

## Verdict

The proven minimum mechanism for **one new actor-sprite identity** is now a
supported SDK primitive, `tools/webfoot/sprite_identity.py`, and no research
script is required to plan that identity. The registry growth, the two literal
words that name the registry, the cloned character structure, the animation and
frame records and the graphics containers are all planned by
`plan_new_sprite_identity`.

**AUTHORING CORE: READY. RUNTIME-BACKED ACCEPTANCE: NOT CLAIMED HERE.** This
ticket moves the mechanism; it does not re-run the emulator, and nothing in it
promotes a runtime claim.

## 1. What moved, and what did not

| measured mechanism | research home | production home |
| --- | --- | --- |
| registry re-emitted one entry longer, above EOF | `sprite_new_runtime.build_experiment` | `sprite_identity._encode_records` |
| the two literal-pool words repointed | `build_experiment`, from `ActorSprites.registry_references` | `_registry` + `_changes`, from `RomDocument.inbound` |
| structure cloned verbatim, count byte rewritten | `encode_structure_many` | `_donor` + `_encode_records` |
| animation per sheet, frame per direction slot | `encode_animation` | `_encode_records` |
| frame geometry copied from the donor's own frame | hardcoded `PIECE_X/PIECE_Y/PIECE_ATTRIBUTE` | `_donor`, read from the image |
| one packed kind-1 container per frame | `build_experiment` | `_container_payloads` via `sprite_graphics.encode_graphic_payload` |
| direction-major sheet cell to frame-major slot | `cui_cell_index` | `SourceSheet.slot_cell_index` |
| existing palette entry reused, else a free entry written | `assign_palette` | `_assign_palette` + `_take_free_entry` |

Two things were **not** moved, deliberately. The research planner's `new-actor`
arm (a map object array re-emitted one element longer, a placement record cloned,
a map's count field bumped) is placement authoring and is out of this ticket's
scope. The Cui sheet reader is not moved either: it decodes a PNG through Pillow,
which is not a declared dependency of this repository.

## 2. What replaced the research logic

`tools/research/sprite_new_runtime.py` is unchanged and is still the record of the
runtime experiment. What changed is that its identity half is no longer the only
implementation of the mechanism: the production planner reproduces it from the
image alone, with no research import, no hardcoded retail address and no
hardcoded frame geometry.

Three differences from the research emitter, each a deliberate tightening:

1. **The registry's inbound surface is consumed from the reference graph, and a
   scan of the image checks that the graph is complete.** The research planner
   compared the published word count against
   `graphics.CHARACTER_TABLE_REFERENCE_OFFSETS`, which is a census of one image.
   The production planner requires the anchor to be published relocatable - the
   graph's own statement that its inbound surface is fully expressed - and checks
   every word it is handed: confirmed, delta-free, absolute 32-bit, and still
   holding the table address. What that does *not* add is new evidence about the
   census itself: the graph's two words are published from that same measured
   constant, so the planner and the constant cannot be checked against each other.
   The ROM-gated suite therefore scans the canonical image for the table address
   and requires every word-aligned occurrence to be exactly the published pair,
   which is the measurement and not a restatement of it.
2. **Frame geometry is read from the donor, not restated.** The research carried
   `PIECE_X`, `PIECE_Y` and `PIECE_ATTRIBUTE` as constants copied by hand from
   sprite 10's own piece. The planner reads that piece and requires the authored
   sheet cell to equal it, so a donor whose geometry differs cannot be authored at
   the wrong size. A donor whose first piece carries a flip bit is refused: the
   authored pixels come from the sheet the author drew, and inheriting a mirror
   would silently reverse them.
3. **A palette entry's colour is its low 15 bits.** One canonical entry stores
   bit 15, and `pack_gba_colour` can only produce 15-bit words, so a strict word
   comparison would fail to see a colour the palette already displays and would
   spend a free entry duplicating it.
4. **Reusing a requested free entry reserves it, and writing one withdraws the
   colour it held.** Both directions are needed. A free entry holds a colour
   before it is written, and the authored artwork may use that colour; if the
   entry were reused for its own colour and then handed out again as free, every
   pixel that had just taken it would be repainted, with no refusal anywhere. The
   planner now removes a reused entry from the free list and drops a written
   entry's old colour from the reuse map.

## 3. The API

```python
plan_new_sprite_identity(image, identification, identity, *,
                         reserved=(), sprites=None) -> SpriteIdentityMaterialization
```

Input, the narrow shape the Cui standing proof needs:

- `NewSpriteIdentity(sprite_id, donor_sprite_id, animations, free_palette_entries)`
- `AnimationSource(name, sheet)`
- `SourceSheet(frames_per_direction, cell_width, cell_height, pixels,
  transparent_colour)` - RGB888, one row of cells, direction-major

Output: `SpriteIdentityMaterialization(identity, changes, reserved,
generated_allocations, relocations)`, the same four plan fields every authoring
domain returns, plus `AuthoredIdentity` describing what was laid out (registry,
structure, per-animation ranges and per-frame slot, cell and container ranges,
and the palette entries written).

Refused rather than guessed: a sprite id that is not the appended entry; an
unknown donor; a donor whose first frame has more than one piece, is 4bpp, carries
a flip bit, or does not decode; a sheet cell that does not equal the donor's own
frame geometry; a sheet with more frames per facing than this project's own
animation reader accepts; more animation slots than the engine's count byte is
read against; a registry anchor of the wrong kind, size, offset or relocatability;
a registry word that no longer holds the table address; a profile with no declared
expansion; a requested free entry that a decoded actor-sprite graphic draws or
that is out of range; and a colour the palette does not hold when no free entry is
left.

## 4. The one mapping

A source sheet is **direction-major**: four facings, each holding all of its own
frames. The animation record is **frame-major**. Sheet cell
`d * frames_per_direction + f` is engine slot `f * 4 + d`, and
`SourceSheet.slot_cell_index` is the only place those orders are reconciled. The
portable suite asserts the mapping on synthetic sheets; the ROM-gated suite
asserts it on the canonical image by painting each cell a distinct existing
palette entry and decoding the container each slot resolves to.

## 5. Validation performed

Portable, measured on the ticket worktree:

- `python -m pytest tests/unit -q` - **3882 passed, 45 skipped**, 0 failed. The
  skips are pre-existing (site not built, capstone present, and two files that
  need the canonical profile at a fixed local path).
- `tests/unit/test_sprite_identity_authoring.py` - **53 passed**. Synthetic
  image holding a 297-entry registry, a decodable donor, a real `RomDocument` and
  a duck-typed corpus stub that supplies exactly the four members the planner
  reads, so an accidental fifth dependency fails loudly. Four of the cases are
  regressions for findings the independent review raised and this ticket fixed.
- `tests/unit/test_logx_synthesis_audit.py` - **26 passed**. Two superseded-
  assumption patterns matched the first draft of the module's prose
  (`fixed-23-animation-slots`, `four-byte-frame-header`); the wording was
  corrected. This is the audit doing its job, and it is recorded rather than
  quietly fixed.

ROM-gated, against the canonical image, `tests/integration/test_sprite_identity_rom.py`
- **13 passed** (about 5 minutes; the corpus walk and one reference-document build
dominate). What they establish:

- the published registry is 297 entries at `0x006B6BDC`, relocatable, with exactly
  the two published inbound words, and a scan of the image for the table address
  finds exactly those two words and no others;
- a planned identity grows it to 298 and carries the first 297 entries byte for
  byte;
- both words are repointed, and no other canonical byte changes;
- all 297 existing character structures are byte-identical afterwards;
- the new identity resolves registry -> structure -> animation -> frame ->
  container through the retail decoders, with the authored pixels in the right
  direction slots;
- a colour the palette lacks takes one of the requested free entries (217 or 236,
  the pair the runtime experiment wrote) and only that entry's bytes change;
- planning twice produces identical changes and an identical image;
- the canonical file is re-hashed afterwards and its digest is unchanged.

Repository gates, all green on the frozen candidate: `readability --all`
(0 hard findings tree-wide), `architecture` (0 violations), `public_surface --all`
(0 findings), `public_release` (0 findings).

## 6. Independent review and its findings

The review was run by the Claude CLI headless in this worktree against the frozen
candidate, with a fresh context that did not implement the change. It returned
**BLOCKED** with one blocking finding and three non-blocking ones, all of which
are addressed here.

| finding | disposition |
| --- | --- |
| BLOCKING: a requested free palette entry could be reused for its own colour and then overwritten with a different one, so authored pixels displayed the wrong colour with no refusal | fixed: a reused entry leaves the free list, and a written entry's old colour leaves the reuse map. Two regression cases, one for each order, now assert that every emitted cell's index displays the colour it was painted with. |
| NONBLOCKING: no bound on frames per direction, so a plan could write an animation the SDK's own reader refuses | fixed: `SourceSheet` refuses above the 64-frame bound `sprite_graphics.decode_animation` applies. |
| NONBLOCKING: the donor's flip bits were copied without a check, so a flipped first piece would mirror every authored frame | fixed: a donor whose first piece carries a flip bit is refused. |
| NOTE: the evidence text claimed the inbound words come from the graph rather than a census constant, which overstated what changed, and a ROM test compared the graph to the constant it was built from | corrected in section 2, and the ROM suite now scans the image for the table address instead of restating the constant. |
| NOTE: the review did not run the repository gates or the ROM-gated suite | recorded: those results are this ticket's own measurement, and CI is where they are reproducible. |

## 7. What remains open

- **Runtime.** No emulator run was performed for a derivative this planner
  produced. The runtime claim stays owned by `SPRITE_NEW_RUNTIME.md` and its mGBA
  session; a re-run through the production planner is the natural next ticket.
- **The frame-composition budget.** Still unsolved, and this ticket does not
  solve it. The planner refuses to author frame geometry at all: every authored
  frame copies the donor's own first frame, so the frames are ones the donor's
  animation already draws. What that does not establish is the case a later act
  creates - pointing this identity at an actor that draws smaller frames than the
  donor.
- **Placement.** Attaching the identity to a map object, a placement or the party
  table is a separate act and no placement, map or party byte is written here.
- **Dialogue and script.** Out of scope.
- **The free-entry census.** `free_palette_entries` is a caller claim, checked
  only against the actor-sprite graphics the SDK decodes. Portrait and
  user-interface payloads share the same 256-entry palette and are not decoded, so
  their residual is the caller's, and it is stated on the field.
- **Which direction slot is which screen facing.** Unresolved project-wide. The
  planner is direction-indexed and names no facing, matching
  `formats/sprite_graphics.py`'s own refusal to name them.
