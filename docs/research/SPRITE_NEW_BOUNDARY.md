# SPRITE-NEW-BOUNDARY-001: what a genuinely new actor-sprite identity requires

Research record. Read-only against the canonical image
`buus_fury_usa_rev0_01c1707f` (SHA-1 `f1c4b07554d2a3b1ad2f325307051e775ce68087`,
SHA-256 `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`),
8,388,608 bytes, verified unchanged. No ROM was written and nothing here is
implemented.

Baseline `origin/master` = `7ce5b7bdfba64de2d264305e9df878709167abcc`, confirmed
before branching. Ticket worktree `C:\Dev\log1-remake-sprite-new-001`, branch
`ticket/sprite-new-boundary-001`.

Target asset: `C:\Dev\log1-remake\Cui\Cui`, five PNGs, the custom Cui sprite.

Evidence labels are the project's: **CONFIRMED** (measured here or already
CONFIRMED_ROM), **CONFIRMED_RUNTIME** (measured in mGBA by an earlier ticket),
**UNRESOLVED**.

What this record does not do: it does not re-prove
GRAPHICS-IMPORT-BOUNDARY-001. Container encoding, kind selection, allocation
above EOF and reference rewriting are taken as given. The question here is what
an **additional sprite/animation identity** needs that the retail ROM did not
already contain.

---

## 1. The registration point for a sprite identity

**CONFIRMED. There is exactly one registry, and it is a fixed-count array.**

The character pointer table lives at ROM `0x086B6BDC` (file `0x006B6BDC`), 297
entries, `sha256 afad8079e3653cc36393643feeb780a6565e96c97f81980880457e20f31a9e96`.
Entry `i` is sprite id `i + 10`, so the registered id space is `10..306`.

The accessor is `0x08000158`, disassembled here:

```text
08000158  push  {r4, lr}
0800015a  cmp   r0, #0xa
0800015c  blt   #0x800016a          ; ids 0..9 take the party path
0800015e  ldr   r1, [pc, #0x260]    ; the literal at 0x080003C0 = 0x086B6BDC
08000160  lsls  r0, r0, #2          ; 4 * id
08000162  adds  r0, r0, r1
08000164  subs  r0, #0x40           ; -0x40
08000166  ldr   r0, [r0, #0x18]     ; +0x18, so net -0x28 = -(4 * 10)
08000168  pop   {r4, pc}
```

The arithmetic folds to `*(u32 *)(0x086B6BB4 + 4 * id)`, that is
`table + 4 * (id - 10)`. **There is no comparison against 297 and no null test.**
A census of every 4-byte window in the image finds no word equal to `297`, `298`,
`0x129` or `0x12A` in the code region, so no length constant exists to find.

**The party path is not a second registry.** `0x0801713C` reads a party record's
`u16 +0x0E` and re-enters the same arithmetic through the same literal:

```text
0801713c  ldrh  r0, [r0, #0xe]
0801713e  ldr   r1, [pc, #0x1c]     ; the literal at 0x0801715C = 0x086B6BDC
08017140  lsls  r0, r0, #2
08017142  adds  r0, r0, r1
08017144  subs  r0, #0x40
08017146  ldr   r0, [r0, #0x18]
```

The 24-byte-stride party table at `0x086B82EC` carries sprite ids `115..121` in
its `+0x0E`, all inside `10..306`. It is a consumer of ids, not a registry.

**Consumers, not registries.** The 232-record appearance table at `0x0874D380`
(stride `0x10`, `+0x04` = a logical sprite id) and the party table both *name* ids
that the one registry resolves. A placement-driven actor reaches the registry
directly and needs no appearance record:

```text
0800fd54  push  {r3, lr}            ; the 0x0800FD55 placement factory
0800fd56  ldr   r2, [r0, #8]        ; placement +0x08 = the stat selector
0800fd58  lsls  r3, r2, #3
0800fd5a  subs  r2, r3, r2          ; 7 * selector
0800fd5c  ldr   r3, [pc, #0x10]     ; 0x08711274, the stat table
0800fd5e  lsls  r2, r2, #2          ; 28 * selector
0800fd60  adds  r2, r2, r3
0800fd68  bl    #0x800f68c          ; constructor(0, placement, stat record, arg)

0800f68c  ...                       ; allocates 0x29C bytes for the actor
0800f6ae  ldr   r0, [r5, #0x10]     ; placement +0x10 = the sprite id
0800f6b0  bl    #0x8000158          ; the registry accessor
0800f6be  adds  r0, r4, #0
0800f6c4  bl    #0x8000e754         ; the actor initialiser, r1 = structure
```

So `placement +0x10 -> 0x08000158 -> 0x0800E754`. The chain is measured
instruction by instruction, and it means one 4-byte placement write is a complete
and sufficient way to point one actor at a different sprite identity.

### Can the table be expanded?

**In place: no.** The word immediately after the 297th entry, file `0x006B7080`,
holds `0x03001068`, an IWRAM pointer, and its own address is named by literal-pool
words at file `0x13BA0` and `0x13E2C`. It is live. `0x006B7084` begins the
experience table and is named at file `0x13610` and `0x13908`. The last character
structure (`0x086B6B60`, 124 bytes) ends exactly at the table, so there is no room
before it either.

**By relocation: yes, and cheaply.** A whole-image stride-4 census, repeated at
byte alignment, finds exactly **two** words equal to `0x086B6BDC`:

| Literal-pool word | Consuming instruction | Used for |
|---|---|---|
| file `0x0003C0` (rom `0x080003C0`) | `ldr r1,[pc,#0x260]` at `0x0800015E` | ids `>= 10` |
| file `0x01715C` (rom `0x0801715C`) | `ldr r1,[pc,#0x1c]` at `0x0801713E` | the party re-entry |

That is the same census the project's relocate-never-splice doctrine requires
before a packed record table is moved, and it makes a table relocation a
**two-word patch**.

### The smallest safe way to create one additional identity

1. Copy the 297 canonical entries to fresh space and append one more, making a
   298-entry table. 298 * 4 = 1,192 bytes.
2. Rewrite the two literal-pool words to the new address.
3. Append one new character structure.
4. Point entry 297 at it.
5. Change one placement's `+0x10` to `307`.

Nothing else registers an identity. No appearance record, no party record, no
name, no stat record.

---

## 2. Animation, direction, frame and timing

### The character structure

`+0x00` is a `u16` whose **low byte is the animation-array count**.
**CONFIRMED independently here**: the counts over the 297 structures sum to
exactly **4,070**, matching LOGX-SPRITE-001, and the populated slots sum to
exactly **1,721**.

| Field | Extent | Status |
|---|---|---|
| `+0x00` | `u16`, low byte = animation slot count, values `1..23`, 14 distinct | CONFIRMED |
| `+0x04`, `+0x0C` | `u32`, zero in the donors examined | recorded, semantics UNRESOLVED |
| `+0x08` | 4 bytes; byte 0 is a per-character screen-y offset, `0/8/16/32/64` | PARTIALLY CONFIRMED |
| `+0x10..+0x4F` | four 16-byte blocks, one per direction slot, shaped `(i32, i32, i32, i32)` | semantics **UNRESOLVED** |
| `+0x50` | `u32`; a parallel per-animation pointer array, zero in 287 of 297 | PARTIALLY CONFIRMED |
| `+0x54` | the inline animation pointer array, count-bounded | CONFIRMED |

The four 16-byte blocks are **not** the per-direction frame boxes. Tested across
the corpus, their `(max - min)` size matches the reached frames' `w x h` in only
**43 of 1,188** direction slots, so that hypothesis is refuted. For a new
structure the safe move is to **clone the donor's whole 0x54-byte header
verbatim**, which keeps their unknown meaning exactly as the retail actor had it.

### The animation record

`u32 frame_count`, then `frame_count * 4` frame pointers, **direction-major within
each frame**: slot `d` of frame `f` is at flat index `f * 4 + d`. Proven extent is
exactly `4 + 16 * frame_count` bytes.

The engine's own arithmetic, at `0x0800EF38`:

```text
0800ef38  ldrb  r2, [r0, #0x11]   ; the published frame index
0800ef3a  ldr   r1, [r0, #0x50]   ; the selected animation
0800ef3c  lsls  r2, r2, #4        ; frame_index * 16
0800ef3e  adds  r1, r1, r2
0800ef40  ldrb  r2, [r0, #0x10]   ; the direction slot
0800ef42  lsls  r2, r2, #2        ; direction * 4
0800ef44  adds  r1, r1, r2
0800ef46  ldr   r1, [r1, #4]      ; +4 for the frame_count word
0800ef48  str   r1, [r0, #0x54]   ; obj+0x54 = the frame record
```

so `frame = *(u32 *)(animation + 4 + 16 * frame_index + 4 * direction)`.

`obj+0x50`, the selected animation, is initialised from `structure + 0x54`, the
animation index 0, at `0x0800EBD0`. Animation slots may be **NULL**: the array is
sparse (2,349 of 4,070 slots are null) and the engine null-tests them. Five
accessor sites follow one shape, for example:

```text
08013044  ldr   r0, [r4, #0x58]   ; the character structure
08013046  ldrb  r1, [r0]          ; the animation count
08013048  cmp   r1, #7
0801304a  bls   #0x8013078        ; count too small: refuse
0801304c  ldr   r0, [r0, #0x70]   ; +0x54 + 4*7
0801304e  cmp   r0, #0
08013050  beq   #0x8013078        ; null: refuse
```

### Frame timing

**There is none in the animation, and none to author.** Playback is driven by the
entity, not the record:

```text
0800de6e  ldrh  r2, [r1, #0x12]   ; a u16 counter on the entity
0800de70  adds  r2, #1
0800de72  lsls  r2, r2, #0x10
0800de74  lsrs  r2, r2, #0x10     ; wrap to 16 bits
0800de76  strh  r2, [r1, #0x12]
0800de78  ldrb  r3, [r0, #4]      ; a shift amount from the state object
0800de7a  lsrs  r2, r3            ; frame index = counter >> shift
0800de7c  ldr   r3, [r1, #0x50]   ; the selected animation
0800de7e  ldr   r3, [r3]          ; animation + 0x00 = frame_count
0800de80  cmp   r3, r2
0800de82  bgt   #0x800de90        ; in range
0800de90  strb  r2, [r1, #0x11]   ; publish the frame index
```

The rate lives in the state object, not the animation. `0x0800DEB0` is the same
computation with a wrap, and `0x08010398` a third variant at a quarter speed. So a
new animation carries no duration, delay or loop field at all.

### The two words after the frame-pointer table

LOGX-FRAME-001 left these UNRESOLVED and could not show the trailer extent exists.
Measured here over all 1,017 animation objects:

* 987 objects have two words after the table; **30 do not, because a frame record
  starts exactly there**;
* their values are `(1, a power of two)` in 974 of 987;
* `trailer_1` equals the animation's own maximum frame byte size in **677 of
  987**, so it is *not* a reliable frame-size field, and it differs in both
  directions (an animation with 32x32 frames can carry 512; one with 128-byte
  frames can carry 512).

**This is dissolved by layout rather than by guessing.** The new animation record
will be written so that the new frame record begins immediately after its pointer
table, which is precisely the shape the other 30 canonical objects have. The two
words are then a frame record's `u32 piece_count` and its box header, not an
invented trailer value.

### The frame record and the piece

```text
frame  +0x00  u32 piece_count        1..4 canonically
       +0x04  s8  min_x              the frame's own bounding box
       +0x05  s8  min_y
       +0x06  u8  width
       +0x07  u8  height
       +0x08  12-byte piece records, piece_count of them

piece  +0x00  s8  x
       +0x01  s8  y
       +0x02  u8  pixel extent 0       (the engine halves it to centre an OBJ)
       +0x03  u8  pixel extent 1       (halved, and multiplied to size the buffer)
       +0x04  u32 packed GBA OBJ attribute pair, (attribute1 << 16) | attribute0
       +0x08  u32 pointer to the graphics container
```

For one-piece frames the frame's box equals the piece's own `(x, y, dim0, dim1)`.

### The reference actor, measured end to end

Sprite **10**, table slot 0, structure `0x086A89D0` (file `0x006A89D0`), 92 bytes:

```text
+0x00  02 00 00 04     animation count 2
+0x04  00 00 00 00
+0x08  10 08 0a 04
+0x0C  00 00 00 00
+0x10  f8 ff ff ff  f2 ff ff ff  18 00 00 00  07 00 00 00
+0x20  f9 ff ff ff  f3 ff ff ff  17 00 00 00  07 00 00 00
+0x30  fa ff ff ff  f1 ff ff ff  16 00 00 00  07 00 00 00
+0x40  fa ff ff ff  f1 ff ff ff  16 00 00 00  07 00 00 00
+0x50  00 00 00 00     no parallel array
+0x54  c4 3a 3c 08     animation 0 = 0x083C3AC4
+0x58  c4 3a 3c 08     animation 1 = 0x083C3AC4  (the same record)
```

Animation `0x083C3AC4`: `frame_count = 2`, eight direction pointers, then the two
words `1, 1024` which are in fact the following record's header. Every frame is
`32x32`, box `(-8, -24, 32, 32)`, one piece at `x=-8, y=-24`, dims `32x32`:

| Direction | Attribute word | Horizontal flip | Container |
|---|---|---|---|
| 0 | `0x80002000` | no | `0x083C34D0` |
| 1 | `0x80002000` | no | `0x083C36A0` |
| 2 | `0x80002000` | no | `0x083C3808` |
| 3 | `0x90002000` | **yes** | `0x083C3808` (shared with direction 2) |

`attribute0 = 0x2000` is the 8bpp flag with shape 0 (square); `attribute1 = 0x8000`
is size 2, which is `32x32`. Every container is `kind 1`, `declared_size 1024`.
Direction 3 re-uses direction 2's container with the horizontal-flip bit set,
which is the corpus's normal way of mirroring a facing.

### Mapping Cui into this format

| Cui sheet | Cells | Size |
|---|---|---|
| `stand.png` | 8 | 32x32 |
| `walk.png` | 16 | 32x32 |
| `attack2.png` | 16 | 32x32 |
| `hurt.png` | 12 | 32x32 |
| `block.png` | 4 | 32x32 |

All five are a **single row of 32x32 cells**, one direction only. That matches the
donor's frame geometry exactly, including the box and piece anchor, so no resizing
and no repositioning is required.

**The one-direction problem, stated exactly.** An animation's frame cell is four
pointers, one per direction slot, and the engine reads the one matching the
actor's current facing with **no null test**:

```text
0800f380  ldr   r0, [r4, #0x54]   ; the frame record
0800f38e  ldrb  r2, [r0, #6]      ; width, read without a null check
0800f390  ldrb  r1, [r0, #7]      ; height
```

The canonical corpus has **13,660 cells and not one is null**, which is what a
guard-free dereference looks like. So **all four direction slots must point at a
valid frame record.** Because Cui is genuinely one direction, the first experiment
points all four slots at the *same* frame record. The consequence is honest and
visible: **the Cui sprite does not turn and does not mirror; it renders the same
art in every facing slot.** That is not a directional claim, and no facing is
named.

The horizontal-flip bit is available (2,848 canonical pieces set it) and is the
obvious later refinement, but which slot corresponds to which screen-space facing
is **UNRESOLVED** in this project, so the first experiment must not use it.

### Palette and conversion

Closed in the preceding analysis and summarised here because the experiment
depends on it. Magenta `#FF00FF` is a chroma key, not artwork: every Cui PNG is
100% opaque. It maps to palette index 0, the family's transparent index. Every one
of the 36 art colours is already an exact 5-bit colour (`v = channel >> 3` is
exact for all 36, so there is **no quantisation error**), collapsing to 30
distinct 5-bit colours, of which **28 already exist verbatim in the global object
palette at index >= 1**. Two greys, `v(14,14,14)` and `v(21,21,21)`, need either a
new palette entry or a conservative snap.

---

## 3. The minimum runtime experiment

### The target and the trigger

**Test actor: map 19, placement 6**, file `0x072EF8`, 44 bytes:

```text
55fd0008 84010200 8d000000 4003a001 0a000000 f02e0708 04000000 b42e0708 c02e0708 cc2e0708 d82e0708
factory +0x00 = 0x0800FD55
flags   +0x04 = 0x00020184
type    +0x08 = 141          <- unchanged
position+0x0C = 0x0000008D   -> map (832, 416)
id      +0x10 = 10           <- the ONLY word this experiment changes, to 307
descr   +0x14 = 0x08072EF0
children+0x18 = 4
```

Chosen because its sprite, id 10, **already draws 32x32 frames**, and because
map 19 placements **7 to 10 also use id 10**, so after the change the retail
sprite is still rendered in the same map at the same time. That is a direct
on-screen A/B in one session with no second boot.

The other candidate, sprite **227** (map 19 placement 11, animation count 2, one
32x32 frame, and the only user of that id), is simpler still but loses the
in-map control, so it is the fallback if map 19 turns out to be awkward to reach.

### Exact writes

Nothing canonical is overwritten except two literal-pool words, one placement
word, and at most two palette halfwords.

| # | Write | Target | Size | Kind |
|---|---|---|---|---|
| 1 | 298-entry character table (297 canonical + entry 297 = new structure) | expanded space | 1,192 B | new |
| 2 | literal-pool word for the main resolver | file `0x0003C0` | 4 B | patch |
| 3 | literal-pool word for the party re-entry | file `0x01715C` | 4 B | patch |
| 4 | new character structure: clone of `0x086A89D0`'s 0x54-byte header, count 2, both animation pointers = the new animation | expanded space | 92 B | new |
| 5 | new animation record: `frame_count = 1` + 4 direction pointers, all to the new frame, immediately followed by that frame record | expanded space | 20 B | new |
| 6 | new frame record: `piece_count = 1`, box `(-8, -24, 32, 32)`, piece `x=-8, y=-24, dim=(32,32), attr=0x80002000`, container = the new container | expanded space | 20 B | new |
| 7 | new graphics container: `kind 1`, `declared_size 1024`, packed Cui 32x32 8bpp indices | expanded space | ~8 + packed | new |
| 8 | placement `+0x10` | file `0x072EF8` + 0x10 | 4 B | patch |
| 9 | optional: two palette halfwords for `v(14,14,14)` and `v(21,21,21)` | file `0x0005652C` + 2*index | 4 B | patch |

Every new payload needs **expanded storage**. The canonical allocation surface is
one 256-byte verified-free window at `0x007EA400`, and even the smallest single
record exceeds it once the table is included; the total is about **1,732 bytes**.
The generated expansion declares `0x00800000..0x00FFFFFF`, mapping file
`0x00800000` to ROM `0x08800000`, and the allocation authority already places
above-EOF payloads there.

Two layout constraints are load-bearing and cheap:

* the new animation record must be laid out **immediately before** the new frame
  record, so the two words after its pointer table are that frame record's header,
  which is a shape 30 canonical objects already have;
* the new structure must be placed so that `base + 4 * 307` addresses entry 297,
  which is automatic once the literal is `table_base` and entries are
  `sprite_id - 10`.

The frame's `min_x, min_y` and the piece's `x, y` are copied from the donor
(`-8, -24`), so the Cui art is anchored exactly where the retail 32x32 art was.

### What already exists in the SDK, and what does not

| Need | Status |
|---|---|
| Deterministic above-EOF allocation from a declared expansion | **exists**: `webfoot.allocation.allocate`, `GeneratedExpansionProfile`, `generated_allocation_provenance` |
| Atomic, validated, attributed byte writes | **exists**: `webfoot.write.ByteChange` / `plan_changes` |
| Packed container encoding with the right kind | **exists**: `webfoot_lz.pack(payload, kind=1)`, `sprite_graphics.encode_graphic_payload` (kind is a required keyword, so the packer's default cannot leak) |
| 8bpp 8x8 tile swizzle | **exists**: `sprite_graphics.swizzle_tiles` |
| Rewriting one placement's `+0x10` | **exists**: `PlacementRecord.id_raw` is in `enemy_randomizer.records.EDITABLE_FIELDS`, and `changes_for` already emits exactly this `ByteChange`; only `enemy_type`'s corpus-pair policy would refuse a novel id, and that policy is not in the write path |
| Relocating the character pointer table | **missing, and small.** `layout.RELOCATION_ELIGIBLE_KINDS` is `{placement_reference_array, text-string, graphics_container}`; `character_pointer_table` is not eligible. And `ActorSprites.reference_document()` publishes the 295 table-slot-to-structure references but publishes **no reference whose target is the table**, so `_relocation_candidate` would refuse for "no confirmed reference reaches this payload". Both are additive: two references at file `0x0003C0` and `0x0001715C`, and one set member |
| An allocation kind for sprite metadata | **missing, and mechanical.** `DEFAULT_ADDRESSABILITY` is keyed by `AllocationKind` and would raise on an unknown kind. `LAYER_RECORD` and `TRANSITION_RECORD` are `EXPANDED_ONLY`, which is the same situation: a created record with nowhere canonical to go |
| A domain that composes a new sprite identity | **missing, and intended.** `graphics_authoring.plan_graphic_overrides` refuses a graphic "this ROM does not contain", which is exactly the boundary this ticket describes |

### Remaining unknowns

1. **The frame-composition buffer bound is not established.**
   The compositor writes the frame's `w * h` bytes to `[actor + 0x40]` (the total
   is stored at `[actor + 0x48]`), and CRASH-ROOT-CAUSE-001 measured a **0x200**
   budget on one actor, whose canonical frames were exactly `16x32 = 0x200`;
   growing them to 32x32 corrupted the actor. The actor constructor allocates a
   **0x29C**-byte block, and where `+0x40` is assigned was not located, so the
   sizing rule is **UNRESOLVED**. The experiment does not depend on resolving it:
   it points a 32x32 sprite at an actor that **already renders 32x32 frames**, so
   the budget is proven adequate by the retail game's own behaviour, and the
   sprite never grows.
2. **A relocated character table above EOF has never been exercised.** The
   supporting evidence is strong (the GBA Game Pak ROM window is flat to
   `0x09FFFFFF`; the table is reached only through those two literals; and
   GRAPHICS-IMPORT-BOUNDARY-001's Case B already proved the retail engine follows
   a rewritten pointer into expanded storage and decodes what it finds), but the
   *table* itself has never run from there. This is the first thing the run
   proves, and it is a binary outcome.
3. **The two animation trailer words** have no known reader. Handled by layout,
   not by assumption, as described above.
4. **The frame buffer's `+0x40` assignment site** was not located. Not needed,
   given unknown 1 is avoided by actor choice.

### Proposed next ticket

`SPRITE-NEW-RUNTIME-001`. Implement only the two SDK gaps (reference publication
for the character table, and its eligibility and allocation-kind registration),
then a single research command that emits the derivative described in the write
table above. Boot it in mGBA through the existing injector, load the saved game,
walk to map 19, and capture the settled screen. The proof is: one actor renders
Cui, its four siblings in the same map still render the retail sprite, and the
original sprite 10 structure, animation, frame and container bytes are unchanged
in the image. No editor surface, no authoring UI, no bulk import of the other 52
Cui frames.

---

## Verdict

Every write is named with an offset and a size, every byte-encoding primitive
exists and is already proven, the actor and its trigger are identified, the
palette and conversion questions are closed, and the two genuinely unknown items
are either avoided by construction or are exactly what the run establishes.

**SPRITE-NEW RUNTIME EXPERIMENT READY: YES**

The two residual risks to record against the next ticket, in order:

1. the frame-composition budget, mitigated by choosing an actor that already
   draws 32x32 frames rather than by resolving the sizing rule;
2. the relocated 298-entry character table above EOF, which is unproven and is
   the first thing the run tests.
