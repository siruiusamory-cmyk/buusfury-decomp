# SPRITE-NEW-ATTACHMENT-RUNTIME-PARITY-001: both production planners, run in mGBA

Baseline `origin/master` = `144d06b5460c045eb9bb272cf0bdd9bd5e5bab00`. Ticket branch
`ticket/sprite-new-attachment-runtime-parity-001`. Canonical image
(`940ad5f0...36f059e`) and the private save (`8062e8bf...3080953`) read only and
re-verified unchanged after the session.

## Verdict

**SPRITE-NEW ATTACHMENT RUNTIME PARITY: PASS.**

An image whose **identity** is planned by
`webfoot.sprite_identity.plan_new_sprite_identity` and whose **attached actor** is
planned by `webfoot.sprite_attachment.plan_new_map_actor` was built and run in
mGBA. The retail engine booted, loaded map 102, resolved sprite 307 to the
authored structure exactly once, drew the identity's own frames, moved the actor,
followed the movement with the facing, ran the class-A behaviour with the
authored wander box accepting steps, and left the surrounding retail actors
normal. Both production planners are now runtime-proven together.

The research controlled-actor emitter was **not** used to plan anything here. The
proven image was read only to recover the actor's parameters and to compare the
result: the palette-grid composition differs from the proven walking image by zero
bytes, and the as-authored composition's sha256 is the image the previous parity
session ran.

## 1. What was built, and by which code

| part | planner |
| --- | --- |
| the 298-entry registry, the new character structure, the two animation records, the 24 frame records, the 24 packed containers and the six object-palette entries | `webfoot.sprite_identity.plan_new_sprite_identity` |
| map 102's object array re-emitted with 11 slots, the new object record with its `+0x18` entry word, its retained `+0x04` and `+0x0C` words and its authored wander box | `webfoot.sprite_attachment.plan_new_map_actor` |

`tools/research/sprite_new_attachment_parity.py` drives the two planners and
nothing else. The attachment's inputs are read out of the proven image's own
bytes, which is the direction the ticket asks for: the proven image's map-102
array has 11 slots and its last slot names the authored record, so the sprite id
(307), the position `(209, 580)`, the retained `+0x04` and `+0x0C` words, the
16-byte class-`0x0800A7A1` behaviour entry and the wander box
`x 0x00C0..0x0110, y 0x0220..0x0270` come from the reference, while the bytes
written come from the production planner.

The two production plans are merged the way a build merges domains: the identity
is planned first, its `reserved` spans are handed to the attachment planner as
the shared reservation set, and both change lists go into one
`write.plan_changes` against the canonical image. That is also what makes the
addresses come out right: the allocator withholds the identity's spans and places
the appended actor immediately above them.

## 2. The composed images against the proven builds

| variant | runtime sha256 | identity regions versus the reference | byte differences versus the reference |
| --- | --- | --- | --- |
| `as-authored` | `d21c2b1a0d748ad1dabc588f107d13e63c7c66338e1c6be4c749b624eb4a390d` | 29 of 29 differ (its identity is not the reference's) | 7,072 |
| `palette-grid` | `033e04ba27ac8fcafe99df1f4f6cf2aa6f9a09445eee1ad15b707d2ff694ff57` | 29 of 29 identical | **0** |

The two actor-region rows the driver also reports are comparable only in the
`palette-grid` variant, which reproduces the reference's actor addresses; in the
`as-authored` variant they are marked not comparable rather than counted, because
at its offsets they would compare unrelated bytes.

The `palette-grid` composition is **exactly** the recorded walking build
`033e04ba...`: every identity region identical, zero differing bytes anywhere,
and the recorded 14 canonical bytes. Its appended actor landed on the same
addresses the research composition used (array `0x08801F0C`, record
`0x08801F38`, entry `0x08801F54`).

The `as-authored` composition matches the image the previous parity session ran
by digest: `d21c2b1a...`, 22 canonical bytes, appended actor at array
`0x08801F14`, record `0x08801F40`, entry `0x08801F5C`. That equality is a
sha256 comparison rather than a byte diff, because the driver's diff runs against
the palette-grid reference and the two identities are not the same bytes: the
sheets as drawn carry four colours whose 8-bit encoding is not on the object
palette's grid, so the production planner writes six palette entries instead of
two, its container is 6088 bytes rather than 6080, and every identity address and
pointer downstream of that shifts by 8 bytes.

The 7,072 differing bytes split into 7,059 inside the two appended spans
(`0x800012` to `0x801F6B`, the containers and the shifted identity records) and 13
inside the canonical image: the two registry pointer words (one byte each), five
object-palette entries (8, 9, 103, 193 and 236; 10 bytes together) and one byte
of the map-102 array field, 0x08F944, which moves by one byte because the
appended actor's address shifts with the identity. The cause of the expanded bulk
is an inference consistent with that split rather than a measured classification:
it is the identity's own colour and geometry shift just described, which is the
same finding SPRITE-NEW-RUNTIME-PARITY-001 recorded.

Required checks, both variants, from the emitted bytes:

- the ten retail object records are byte-identical;
- map 102's object bound reads 11;
- `MapEntry+0x14` names the re-emitted array;
- the first ten array words are the retail words verbatim, and the eleventh names
  the new record;
- the record's `+0x18` names its own entry at `record+0x1C`;
- the sprite id is 307, the retained `+0x04` and `+0x0C` words are the
  reference's, and the wander-box halfwords are the requested ones.

## 3. The runtime session

One mGBA session, 0.11.0.0 (verified from `VersionInfo.FileVersion`), launched by
the tracked `tools/runtime/start_spritenew001_session.ps1` on the **as-authored**
production image with the private save, the `menu` key schedule (Start then four
A presses) and the tracked read-only observer
`tools/runtime/spritenew005_parity.lua`, allow-listed in
`tools/runtime/inject_mgba_lua.ps1`. No savestate: the area is built by the image
itself. 2,400 frames, observer-completed, run directory
`build/spritenew001/attachparity-as-authored`. A second independent boot
(`attachparity-as-authored-2`, same image, same schedule) reproduced every result
and is the numbers in parentheses below.

The run follows `docs/skills/mgba-runtime.md`: the Lua scripted-breakpoint
vehicle rather than the GDB-halted one, emulator identity asserted from the
binary's version resource rather than its path, an allow-listed read-only
observer with no emulated-memory writes, the image's own area construction rather
than a restored savestate, and the liveness rule of section 8 stated below.

```text
frame=2400
map_index=102
resolutions=10  new_resolutions=1
   frame 442 (282)  record 0x08801F40  sprite 307  structure 0x08801C70
                    is_new 1  map 102
actors_tracked=10   samples=600
walk_calls=299 (328)  walk_accepts=211 (215)
our_walk_calls=45 (44)  our_walk_accepts=27 (24)
authored_frames=24
error.txt: header line only in both sessions
```

- **Boots and loads.** The game reaches the title, the save loads, and map 102 is
  live: `map_index=102`, and nine retail records resolve to their retail
  structures (`0x086A9A68`, `0x086B0680`, `0x086B4C98`, `0x086B05F8`,
  `0x086B6574`, `0x086B1B28`, `0x086AB008` three times).
- **Identity 307 resolves to the authored structure.** One resolution row carries
  `sprite 307` and `structure 0x08801C70`, above canonical EOF, exactly once per
  session, from the record the production attachment planner created
  (`0x08801F40`).
- **Cui renders.** The authored actor's drawn frame record (`actor+0x54`) was one
  of the identity's own 24 on every one of its samples (489 in session 1, 529 in
  session 2), spread over all four facings: session 1 `down 164`, `up 147`,
  `left 106`, `right 72`; session 2 `down 112`, `up 147`, `left 126`,
  `right 144`. The engine cannot draw a cell of identity 307 without having
  resolved 307.
- **Cui moves.** Session 1: `0xD100,0x24400` to `0xD100,0x23400` (16 px) over 237
  sampled position changes. Session 2: `0xD100,0x24400` to `0xF100,0x22400` over
  207 changes.
- **Facing follows movement.** Every sampled position change was paired with the
  frame record being drawn at that instant: **237 of 237 in session 1 and 207 of
  207 in session 2 matched, 0 mismatched in either**.
- **The class-A behaviour runs.** The record carries the class-`0x0800A7A1`
  entry with the authored box, and the walk action's own result at `0x0800A3B0`
  was 1 on 27 of 45 calls (24 of 44 in session 2) for the authored actor: the box
  is accepting steps.
- **Surrounding retail actors remain normal.** Nine retail actors were sampled in
  each session, seven moved and two stayed still, the same split the movement
  record measured; retail walk calls were accepted 184 of 254 times (191 of 284
  in session 2), which excludes the authored actor's own calls (with them, 211 of
  299 and 215 of 328), the player and the retail worker NPCs render normally, and
  the map itself is the retail West City park.
- **The instrument was live.** The same resolution site fired nine times for
  retail records and once for the authored one, and 299 (328) walk calls were
  recorded; `error.txt` holds only its header line in both sessions, so no
  breakpoint callback raised. This is the "target fires, liveness fires" row of
  `docs/skills/mgba-runtime.md` section 8, not a silent channel.

## 4. Safety

- The canonical image and the private save are byte-identical before and after
  (`940ad5f0...`, `8062e8bf...`); the session ran a staged copy of each inside the
  run directory, and the source images were re-verified by the finisher.
- The generated images live under `build/` and are not committed. Nothing
  ROM-derived is committed: the evidence is counts, addresses and comparisons.
- Both images were emitted through `webfoot.write.emit_image`, which refuses to
  name a source image as an output and refuses to overwrite an existing artefact.

## 5. What this does not claim

- It is not a claim that the retail corpus uses the self-named `+0x18` pattern:
  across the image's 191 sibling slots none names its own `+0x1C`. The self-named
  record is the shape the controlled-actor work proved, and the production
  planner authors it deliberately.
- The frame-composition budget is still unmodelled, and the actor here is the
  same 32x32 donor geometry the runtime tickets used.
- Nothing here adds a project or command surface; the authoring surface still
  needs a caller, which is a later ticket.

## 6. Reproduce

```text
python tools/research/sprite_new_attachment_parity.py \
    --rom <canonical> --stand <stand.png> --walk <walk.png> \
    --reference <the proven walking image> \
    --out-dir <fresh directory> --manifest <fresh json>

powershell -NoProfile -ExecutionPolicy Bypass \
    -File tools/runtime/start_spritenew001_session.ps1 \
    -RomPath <the emitted as-authored image> -RomSha256 <its digest> \
    -ExpectedRomSize 16777216 -Label <fresh label> \
    -SavePath <private save> -Script menu -Ticks 2400 \
    -LuaPath tools/runtime/spritenew005_parity.lua \
    -StructureAddress 0x08801C70 -SpriteId 307 \
    -MGBPath <the 0.11 dev build>
# SPRITENEW005_FRAMES is the manifest's 24 frame addresses, comma separated

powershell -NoProfile -ExecutionPolicy Bypass \
    -File tools/runtime/finish_spritenew001_session.ps1 -Label <label>

python tools/research/sprite_new_parity_report.py \
    --manifest <the parity json> --variant as-authored \
    --run-dir build/spritenew001/<label>/out
```

The driver's own reader is covered portably by
`tests/unit/test_sprite_attachment_runtime_parity.py`: it pins that the actor's
parameters come from the proven image's bytes and that a reference of the wrong
family, slot count or entry class is refused.
