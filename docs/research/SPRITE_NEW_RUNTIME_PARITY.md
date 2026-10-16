# SPRITE-NEW-RUNTIME-PARITY-001: the production planner at runtime

Baseline `origin/master` = `4054152df8852f1556bd4d4f713adbc6924c325d`, the merge
that landed the production planner. Ticket branch
`ticket/sprite-new-runtime-parity-001`. The canonical image
(`940ad5f0...36f059e`) and the private save (`8062e8bf...3080953`) were read only
and re-verified unchanged after every run; no ROM-derived artifact, screenshot or
save is committed.

## Verdict

The supported API `webfoot.sprite_identity.plan_new_sprite_identity` produces the
identity the landed runtime experiment proved, the retail engine resolves it, and
the actor renders, moves, and faces the direction it moves in.

**SPRITE-NEW PRODUCTION RUNTIME PARITY: PASS.**

## 1. What was built, and by which code

The runtime image is composed from two sources, and the split is the point:

| part | produced by |
| --- | --- |
| the 298-entry registry, the character structure, both animation records, all 24 frame records, all 24 packed containers, the object-palette entries | `tools/webfoot/sprite_identity.py`, `plan_new_sprite_identity` |
| map 102's object array re-emitted one element longer, the new object record, its `+0x18` registration word, its `+0x0C` data pointer and the widened wander box | the research builder `tools/research/sprite_new_behavior_registration.py`, whose `new-actor` arm comes from `sprite_new_runtime.py` |

`tools/research/sprite_new_parity.py` plans the identity, re-emits the harness
parts after the identity block and rebases their three internal pointers (the
array's last element, which names the record, and the record's `+0x18`, which names
its own template at `+0x1C`). Nothing was spliced and nothing canonical was
shifted. The harness is placement authoring and stays research; the ticket forbade
productizing it.

The four research images the comparison rests on were reproduced from the current
tree and match their recorded digests exactly: `new-actor` `706a2615...`,
behaviour `efd9640e...`, movement-data `7b12576e...`, bounds (the one that walks)
`033e04ba27ac8fcafe99df1f4f6cf2aa6f9a09445eee1ad15b707d2ff694ff57`.

## 2. Identity A (research) against identity B (production)

Two production variants were planned from the same sheets.

**B `palette-grid`**: byte-identical to A. All 29 identity regions compare equal,
0 of 6,080 container bytes differ, and the composed runtime image is
**`033e04ba27ac8fcafe99df1f4f6cf2aa6f9a09445eee1ad15b707d2ff694ff57`**, the
recorded walking build exactly. The registry moved to `0x088017C0`, the structure
to `0x08801C68`, and the palette entries written are 217 (`0x39CE`) and 236
(`0x56B5`) - the two the runtime experiment wrote.

**B `as-authored`**: the same planner on the sheets exactly as they are drawn. It
is **not** byte-identical, and the difference is entirely a colour-reduction
difference that the sheets' own encoding exposes:

| source colour | production word | production displays | research displays |
| --- | --- | --- | --- |
| `(96, 8, 168)` | `0x502C` | `(99, 8, 165)` | `(99, 8, 173)` |
| `(112, 40, 184)` | `0x58AE` | `(115, 41, 181)` | `(115, 41, 189)` |
| `(168, 168, 0)` | `0x0294` | `(165, 165, 0)` | `(173, 173, 0)` |
| `(192, 192, 192)` | `0x5EF7` | `(189, 189, 189)` | `(198, 198, 198)` |
| `(115, 115, 115)` | `0x39CE` | `(115, 115, 115)` | same |
| `(173, 173, 173)` | `0x56B5` | `(173, 173, 173)` | same |

Why: the sheets are 5-bit artwork stored in 8-bit channels, and the two encodings
of one 5-bit value are different numbers - zero-padded `v << 3` (168 = 21 << 3)
and bit-replicated `(v << 3) | (v >> 2)` (173). The research emitter took the top
five bits (`channel >> 3`), which is exact for both encodings. The production
planner uses the SDK's one RGB-to-word conversion
(`sprite_graphics.pack_gba_colour`), which rounds to the nearest 5-bit step and is
exact for the replicated form only. So four source colours land on the
neighbouring step, which the object palette does not hold, and the identity needs
six palette entries instead of two.

Consequences, all measured: the container payload is 6,088 bytes instead of 6,080,
the metadata block therefore starts 8 bytes later (registry `0x088017C8`,
structure `0x08801C70`), every internal pointer differs, and the composed image
hashes `d21c2b1a0d748ad1dabc588f107d13e63c7c66338e1c6be4c749b624eb4a390d`. The
colours differ by at most 9 of 255 per channel on 4 of the sheets' 36 source
colours: `(192, 192, 192)` becomes `(189, 189, 189)` against the research
emitter's `(198, 198, 198)`, which is the widest gap in the table above.

This is recorded rather than corrected, and it is **not** a defect in the planner.
`pack_gba_colour`'s rounding is the SDK's published conversion, the same one
`graphics.plan_palette_entry_rgb` uses; making the planner truncate instead would
give the SDK two rules for the same RGB triple. What the parity run did expose is
that the *source art* is not on the palette's own grid, which is an authoring
observation, not an algorithm fault: the planner refused to approximate and asked
for more entries, which is the fail-closed behaviour the API promises.

The `palette-grid` variant is the same artwork rewritten channel-by-channel to
`(v << 3) | (v >> 2)`, a lossless re-encoding (the script refuses any sheet whose
channels are not 5-bit in one of the two forms). It shows that once the input is
expressed on the palette's grid the mechanism is byte-exact.

## 3. The runtime images and what they proved

Two mGBA sessions ran the **`as-authored`** production image with the private
save, the `menu` key schedule (Start then four A presses, the schedule the runtime
and movement tickets used) and a purpose-built read-only observer,
`tools/runtime/spritenew005_parity.lua`, allow-listed in `inject_mgba_lua.ps1`.
The observer records: the map object factory's resolution site `0x08017DB0`; the
walk action's result and the step it tested at `0x0800A3B0`; and, every fourth
frame, every actor that reached the walk action, with world position
(`+0x1A0`/`+0x1A4`) and the frame record it is currently drawing (`+0x54`). The
authored actor is identified not by an actor offset but by its drawn frame record
being one of the identity's own 24 - the engine cannot draw a cell of identity 307
without having resolved 307.

Session 1, 2,400 frames, observer-completed:

```text
map_index=102
resolutions=10  new_resolutions=1
   frame 483  record 0x08801F40  sprite 307  structure 0x08801C70  is_new 1  map 102
actors_tracked=10   samples=600
walk_calls=235  walk_accepts=167
our_walk_calls=31  our_walk_accepts=20
```

Session 2, an independent boot ended by the operator at about frame 1,800:
`new_resolutions=1` at frame 283 with the same record, sprite and structure;
`our_walk_accepts=15`; identical results on every check below.

- **Boots and loads.** The game reaches the title, the save is loaded and map 102
  is live; `map_index=102` and the nine retail map-102 records resolve to their
  retail structures (`0x086A9A68`, `0x086B0680`, `0x086B4C98`, `0x086B05F8`,
  `0x086B6574`, `0x086B1B28`, `0x086AB008` three times).
- **Identity 307 resolves to the authored structure.** One resolution row carries
  `sprite 307` and `structure 0x08801C70` (session 2: the same), above canonical
  EOF, exactly once per session.
- **Cui renders.** 23 of the identity's 24 frame records were observed being drawn
  (all 8 stand cells bar one, and all 16 walk cells), and the operator confirmed
  the authored actor on screen, moving, in both sessions.
- **Cui moves.** World position moved from `(0xD100, 0x24580)` to
  `(0xC100, 0x23400)` - 16 px in x and 17.5 px in y - over session 1, with 174
  sampled position changes and 20 accepted steps of `+/-16` px.
- **Facing follows movement.** Every sampled position change was paired with the
  frame record being drawn at that instant: **174 of 174 in session 1 and 126 of
  126 in session 2 matched**, with all four facings exercised. A mis-wired
  direction would show the animation advancing through the four facings while the
  displacement stayed constant, which is the spin defect the movement ticket
  fixed; it is absent here. The pairing is reproducible from the tree with
  `tools/research/sprite_new_parity_report.py`, which reads one observer run
  directory and the parity manifest's frame map:

  ```text
  python tools/research/sprite_new_parity_report.py \
      --manifest <parity manifest> --variant as-authored \
      --run-dir <observer out directory>
  ```

  Run over session 1 it prints `position changes 174, facing matched 174,
  mismatched 0`, the ten resolution rows with the authored one marked, and the
  nine retail actors with seven moving.
- **Surrounding retail actors remain normal.** Seven of the nine sampled retail
  movers changed position during each session and two stayed still, which is the
  same split the movement record measured; 147 retail walk accepts in session 1;
  the map, the player and the retail worker NPCs render normally.

**Class-A behaviour and the wander box.** The composed record still carries the
class-A handler word `0x0800A7A1`, speed `0x80`, the same `+0x0C` data pointer the
movement ticket measured (`0x0878566C`), and the widened wander box
`x 0x00C0..0x0110, y 0x0220..0x0270`; the walk action's own result at
`0x0800A3B0` was 1 on 20 of 31 calls, which is the box accepting the step.

## 4. Safety

- The canonical image and the private save are byte-identical before and after
  every session (`940ad5f0...`, `8062e8bf...`); each session ran a staged copy in
  an ignored build directory and an isolated save directory.
- The observer writes no emulated memory: its only emulated-state change is
  `emu:setKeys` on the named schedule, and every memory read is wrapped.
- Nothing ROM-derived is committed. The variant images, the logs and the
  screenshots live under `build/`, which is ignored.
- The runtime image changes **22 canonical bytes** as `as-authored`, and every one
  is accounted for: 18 for the identity (the two registry words, 6 bytes, and the
  six object-palette entries the art needs, 12 bytes) plus 4 for the controlled
  actor the research builder contributes (map 102's object count byte and the 3
  changed bytes of the 4-byte word naming its object array). The `palette-grid`
  variant is the same accounting with two entries: 10 for the identity plus the
  same 4, which is the 14 the runtime record tabulates. No existing sprite
  structure, animation, frame or container byte changes.
- Both images and the parity report are written through
  `webfoot.write.emit_image`, which refuses to name a source image as an output
  and refuses to overwrite an existing artefact, so no run of the parity harness
  can write over the canonical image or silently replace a previous result.

## 5. What this does not establish

- **Placement attachment is still research.** The identity is production; the
  actor that carries it is not. A user cannot yet author a new actor end to end
  through the supported surface.
- The **frame-composition budget** is still unmodelled; this run, like the proof
  before it, avoids it by pointing a 32x32 identity at an actor that already draws
  32x32 frames.
- **No direction slot is named a facing** in the API. The engine's order (0 down,
  1 up, 2 left, 3 right) is measured and the mapping is exercised, but the planner
  is direction-indexed.
- **The free palette entries are a caller claim**, checked against the decoded
  actor-sprite graphics only; portrait and user-interface payloads are not decoded.
- **Both authored animations were drawn, and the selection rule is not explained.**
  The actor drew stand cells on 323 of its 478 samples and walk cells on the other
  155, interleaved across the whole session. Which slot the engine's state machine
  selects, and when, is engine behaviour this ticket neither changed nor
  determined; the facing check holds for both, since it pairs the displacement
  with whatever frame record is being drawn.
- A **source-art observation**: 5-bit artwork stored zero-padded is not on the
  object palette's own grid, so the SDK's rounding conversion shifts it by up to
  one 5-bit step. A future authoring helper that snaps imported art onto the grid
  would remove that surprise; the planner itself should not be the place it
  happens.

## 5a. Follow-up from the cross-audit

A read-only cross-audit of this ticket's commit raised four NOTE-level findings,
none blocking, all resolved by SPRITE-NEW-PARITY-HYGIENE-001 and none of them a
change to sprite authoring behaviour:

1. the parity harness wrote its images and report with raw file writes; it now
   emits both images through `webfoot.write.emit_image` and takes the same
   source-alias and overwrite guards for the report, and the outputs are
   byte-identical to the ones this record tabulates;
2. this record under-counted the canonical bytes as 18; the composed image
   changes 22, and section 4 now attributes all of them;
3. the stated colour bound was 8 where the table's own widest gap is 9;
4. the facing pairing was described but its script was not committed, and the
   record's own summary of which animation was drawn contradicted its evidence;
   the pairing is now `tools/research/sprite_new_parity_report.py`, named in
   section 3, and section 5 states the animation split the samples actually show.

## Verdict

**SPRITE-NEW PRODUCTION RUNTIME PARITY: PASS.**

**Is `sprite-new` now sufficient to mark shipped? No.** The *mechanism* is
production code, runtime-proven, and byte-reproducible. The *capability* is not:
there is no supported way to attach the identity to an actor, no project or CLI
surface that reaches the planner, and the composition-budget question is still
open. Marking it shipped would tell a reader they can author a new actor with this
SDK today, and they cannot.
