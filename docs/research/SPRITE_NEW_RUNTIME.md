# SPRITE-NEW-RUNTIME-001: a genuinely new actor-sprite identity, at runtime

Runtime record. Baseline `origin/master` =
`7ce5b7bdfba64de2d264305e9df878709167abcc`, confirmed before branching. Ticket
worktree `C:\Dev\log1-remake-sprite-new-runtime-001`, branch
`ticket/sprite-new-runtime-001`. Canonical image read-only throughout and
re-verified unchanged (`940ad5f0...36f059e`).

This ticket implements the experiment SPRITE-NEW-BOUNDARY-001 specified. Its
premise came from that ticket; one of that ticket's own findings turned out to be
wrong, and the correction is recorded in section 6.

---

## 1. Result

**An actor-sprite identity the retail image does not contain was authored above
canonical EOF, and the retail engine resolved it and drew it.**

Measured, not inferred. The observer puts a breakpoint on the placement
constructor immediately after the registry accessor returns, so the engine's own
resolution is recorded:

```
frame=3178
new_sprite_id=307
structure=0x088005B4        <- above canonical EOF
actor=0x0202D004            <- an EWRAM actor the engine built
placement=0x08800674        <- a placement record the retail ROM does not contain
placement_sprite_id=307
map_index=102               <- West City park
```

and the subsequent state reports read that actor's live fields:

```
constructor_hits=1
actors_using_new_identity=1
actor_1=0x0202D004 structure=0x088005B4 animation=0x08800610 frame=0x08800634
```

`0x088005B4`, `0x08800610` and `0x08800634` are all in the generated expansion.
Sprite id 307 is the 298th entry of a relocated registry; the retail image's
registry holds 297 and its highest id is 306.

## 2. What is new, and what is not

In the whole 8,388,608-byte retail image, **14 bytes change**. The current build
`29f9195a2f7ed9ebb7cf72188dad2d52fec1b5cd1dc7d819432fa2954f946529` changes:

| file offset | bytes | what |
| --- | ---: | --- |
| `0x0003C0` | 3 | registry literal, main resolver (`0x086B6BDC` -> relocated) |
| `0x01715C` | 3 | registry literal, party re-entry |
| `0x0566DE` | 2 | object-palette entry 217 |
| `0x056704` | 2 | object-palette entry 236 |
| `0x08F934` | 1 | map 102 object count 10 -> 11 |
| `0x08F944` | 3 | map 102 object-array pointer |

No byte of any existing sprite's graphics, structure, animation or frame changes.
The retail art the controlled actor used is byte-identical in the output and
still reachable. This is a genuinely new identity, not a repaint.

New material, all above `0x00800000`:

* the **298-entry registry**, 297 canonical entries verbatim plus entry 297;
* one **new character structure** (clone of the donor's `0x54`-byte header, its
  `+0x00` count byte rewritten to the number of animation slots actually written);
* **2 animation records** (`stand` 2 frames, `walk` 4 frames);
* **24 frame records**, one per cell, and **24 kind-1 graphics containers**;
* one **new map-102 object record**, and map 102's array re-emitted one element
  longer with all ten existing words copied verbatim.

## 3. The three SDK capabilities this needed

1. **The registry's inbound surface.** `webfoot.graphics` now publishes
   `CHARACTER_TABLE_REFERENCE_OFFSETS = (0x0003C0, 0x01715C)` as two
   `CONFIRMED_REFERENCE` `ABSOLUTE_ROM_U32_LE` words targeting the existing
   `character_table:0000` anchor, re-checked against the image at publication
   time, plus `ActorSprites.registry_identity` and `.registry_references()`.
   Before this the registry had **no inbound reference at all** in the graph, so
   nothing could justify moving it.
2. **`layout.RELOCATION_ELIGIBLE_KINDS` += `character_pointer_table`**.
3. **`allocation.AllocationKind.SPRITE_IDENTITY_RECORD`**, `EXPANDED_ONLY`, the
   first 1,192-byte-against-a-256-byte-window domain, plus
   `relocation._ALLOCATION_KIND["character_pointer_table"]` so a moved registry
   gets that kind rather than the canonical-only default.

## 4. The experiment

`tools/research/sprite_new_runtime.py`, three targets:

* `placement` - repoint map 19 placement 6's `+0x10`.
* `player` - repoint the party table's sprite-id field (works on any map).
* `new-actor` - **a new object record and a grown map object array**, which is
  what "author a new actor" means rather than "repoint an existing one".

Runtime harness: `tools/runtime/spritenew001_observer.lua` (read-only; its only
emulated-state change is `emu:setKeys`), `start_spritenew001_session.ps1`,
`finish_spritenew001_session.ps1`, and an allow-list entry in
`inject_mgba_lua.ps1`.

## 5. Four defects found by running it

Each of these was found by the runtime run, not by inspection, and each is a
standing trap for the next ticket.

1. **The registry cannot grow in place.** The word after entry 296
   (file `0x006B7080`) is a live IWRAM pointer slot, and it is itself named by
   literal-pool words at file `0x13BA0` and `0x13E2C`; the experience table
   follows at `0x006B7084`. The table must be relocated.
2. **Growing the object array is not enough: the COUNT is what the engine
   reads.** `BUU_MAP_OBJECT_ARRAYS.md` records the engine walking `MapEntry+0x04`
   with `ldrb` and indexing `MapEntry+0x14` by `index * 4`, with no sentinel. A
   build that re-emits an 11-slot array but leaves the count at 10 is an array the
   engine still reads at ten: the new actor **never constructs at all**.
3. **A childless placement is a shape the corpus never contains.** Of 1,559
   canonical placements, 1,544 carry one child, seven carry two, six carry three
   and two carry four. The first build emitted a 28-byte childless record; the
   engine resolved the identity and then **faulted within ~20 frames**, reading a
   child pointer that is not there into the generated image's `0xFF` padding.
4. **`Start-Process -ArgumentList` does not quote.** mGBA's usage is
   `[option ...] file` with `-C OPTION=VALUE` taking a separate argument, so the
   ROM must be the trailing, bare argument; and a bare argument containing spaces
   is split. Quoting it is not a fix, it reaches mGBA with the quote characters.
   Staging the image to a space-free path is. Both faults present identically as
   "mGBA did not report the loaded ROM title".

## 6. Correction to SPRITE-NEW-BOUNDARY-001

That record states the Cui sheets are **single direction**, on the evidence that
each is one row of 32x32 cells. That is wrong. Each sheet is **four direction
cells per frame**, in exactly the order the animation record stores them
(`f * 4 + d`):

| sheet | cells | frames |
| --- | ---: | ---: |
| `block.png` | 4 | 1 |
| `stand.png` | 8 | 2 |
| `hurt.png` | 12 | 3 |
| `walk.png` | 16 | 4 |
| `attack2.png` | 16 | 4 |

Rendering the cells individually is what shows it: `block`'s four cells are four
facings, not four frames of one. The first revision of this ticket built identity
307 from a **single cell stamped into all four direction slots**, which is why the
actor rendered as a motionless stamp. The current build carries all 24 cells.

**Standing lesson:** a row of cells at one height is not evidence of one
direction. Count the frames against the direction count and render them.

## 7. Palette

The Cui art needs no quantisation: `v = channel >> 3` is exact for every colour,
and 28 of the 30 distinct 5-bit colours already exist in the object palette. The
current build writes **2 entries**, indices 217 and 236, chosen from the indices
no actor-sprite graphic and no portrait draws
(`[6, 8, 9, 103, 193, 217, 218, 223, 224, 225, 236]`). The UI/HUD family is not
included in that union because it mixes background-palette images and its
byte-union spans all 256 values; the runtime run's "no obvious corruption" check
is what covers the residual.

## 8. Open, and honest about it

**The new actor does not wander.** Cui is on the map, animates through the full
24-cell set, and stands still. Map 102's own NPCs do wander, and the driver is
read:

```
0x0800A2A8  movs r0, #5
            bl   0x0803FACC        ; a random draw
            strb r0, [r5, #0x10]   ; heading
            str  r1, [r4, #0x20]   ; target x
            str  r2, [r4, #0x24]   ; target y
```

and the live run confirms those words moving (`npc_3`: `+0x20` 0x30 -> 0x70,
`+0x24` 0x180 -> 0x1D0). So the behaviour comes from the object record itself and
the clone inherits the record's `+0x0C` data pointer and constructor.

**Leading hypothesis, untested.** Map 102's ten object records are a `0x2C`-stride
contiguous run, and every argument the constructor received is of the form
`record + 0x1C`:

| engine passed | is |
| --- | --- |
| `0x08078488` | rec8 + 0x1C |
| `0x0807845C` | rec7 + 0x1C |
| `0x08078390` | rec2 + 0x1C |

So an object is read *through* its neighbour in the run. The clone is a lone
44-byte record with `0xFF` padding on both sides and has no neighbour, so whatever
that read pattern needs is padding. The fix to try is to emit the whole
contiguous run above EOF with the clone appended, rather than one isolated record.

Also open, and pre-existing:

* **Which direction slot is which screen facing is unresolved** project-wide. The
  cells are wired positionally; no facing is named.
* **No script-body authoring path exists**, so the actor cannot yet be given its
  own dialogue. `AUTHORED_BEHAVIOR_ATTACHMENT.md` records the same blocker. A
  descriptor can be cloned from a retail NPC (66 placements use handler
  `0x0800424F`), which would make the actor talkable with an existing line.
* **The frame-composition budget rule is still unsolved.** This ticket avoids it
  by pointing a 32x32 sprite at an actor that already draws 32x32 frames, exactly
  as the boundary record required.

## 9. Two instrument errors worth recording

1. **A field offset from a different actor class.** The observer read
   `actor+0x48` as a map object's position and reported that none of map 102's
   seven NPCs moved in 80 seconds. `+0x48` belongs to the *placement* actor class;
   the sibling class keeps its live state elsewhere, and `+0x20`/`+0x24` are what
   the think routine writes. The measurement was an artifact of the instrument and
   the conclusion drawn from it was false.
2. **Seeding a range before the value is written.** The first survey seeded each
   actor's min/max at the constructor breakpoint, which sits *before* the
   constructor's own `stm`. Every NPC then appeared to have "travelled" from 0 to
   its coordinate.

Standing lesson: when a measurement contradicts what everyone can see, suspect the
instrument before the game, and check the field against the code that writes it.

## Verdict

The ticket's acceptance list is met: the retail sprite is preserved (14 canonical
bytes, none of them sprite data), the new identity exists beyond the retail 297,
its graphics and metadata live in newly allocated space above EOF, the engine
resolves it at runtime, and Cui renders in mGBA.

**SPRITE-NEW RUNTIME PROOF: PASS**

**Sufficient to begin productizing `sprite-new`? Not yet.** The mechanism is
proven end to end for one identity, through a research-only planner. Three things
should be nailed first, in this order:

1. the object-record run model, so a new actor's behaviour is controlled rather
   than inherited by luck (the wandering defect above);
2. the direction-slot-to-facing mapping, so the four facing cells can be wired
   deliberately instead of positionally;
3. a decision on the frame-composition budget, which is currently avoided by
   actor selection and is the one thing that can corrupt memory if a future
   author picks the wrong actor.
