# LOGX-FRAME-001 provenance: Buu's Fury animation, frame and multipart-piece records

Research record for LOGX-FRAME-001. Status labels are those of
[`../research-conventions.md`](../research-conventions.md): `CONFIRMED`,
`INFERRED`, `UNKNOWN`.

**Canonical profile.** SHA-256
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`,
8,388,608 bytes, read-only throughout. Addresses are GBA addresses; a file offset
is an address minus `0x08000000`. Every headline number below states its
population. Reproduce with
`python -m tools.research.logx_frame_probe <rom> --census`.

The document keeps four voices apart on purpose:

* **EXTERNAL CLAIM** - what `mainant/LOGExtractor` states or what an accepted
  project document previously published, quoted as a claim under test. Nothing
  here inherits an upstream field name or formula.
* **PROJECT OBSERVATION** - a number or byte string this ticket read out of the
  canonical image.
* **PROJECT CONCLUSION** - what the observations and the engine's own
  instructions jointly establish, with the strength stated.
* **NEGATIVE COVERAGE** - an absence claim, scoped to what was actually scanned.

**Accepted dependencies, reused and not re-opened.**

| Source | What is reused |
| --- | --- |
| LOGX-SPRITE-001 / [`LOGX_SPRITE_PROVENANCE.md`](LOGX_SPRITE_PROVENANCE.md) | the 297-entry definition run at `0x086B6BDC`, the `+0x00` count, the `+0x54` inline animation array, the animation selector `0x0800ECDA`, the state table `0x08072670`, and the handoff that the cell index uses `16*frame + 4*direction + 4` |
| LOGX-CHAR-001 | the 232-record appearance table, used only through the definition ids the sprite ticket already joined |
| TOOLKIT-010 / [`GRAPHICS_FORMAT.md`](GRAPHICS_FORMAT.md) | the packed-container decoder `tools/webfoot/formats/webfoot_lz.py` used as a black box, and the corpus figures this ticket tests for consistency |
| LOGX-CODEC-001 | the container grammar's declared-size semantics |

---

## 1. EXTERNAL CLAIMS AND THEIR VERDICTS

### 1.1 The accepted project documents

| Accepted statement | Verdict |
| --- | --- |
| `GRAPHICS_FORMAT.md` §2, `sprite_graphics.py`: an animation record is `u32 frame_count` then `frame_count * 4` frame pointers, direction-major within each frame | **CONFIRMED** in full, including the direction-major order |
| `GRAPHICS_FORMAT.md` §2: the frame record is `u32 piece_count` then that many **16-byte** piece records | **REFUTED** as a stride and a header: the record is an **8-byte header** then `piece_count` **12-byte** pieces. §4.1 |
| `GRAPHICS_FORMAT.md` §2: the piece record's `+0x08` is an OAM-style attribute pair and `+0x0C` is the graphics-container pointer | **HALF REFUTED, HALF CONFIRMED**: the attribute pair is real and its bit layout is exactly as that document describes, but it is stored at **`+0x04`**, not `+0x08`; `+0x08` is the graphics-container word. §4.1, §6.5 |
| `GRAPHICS_FORMAT.md` §2 and §4: **all 10,959 frames declare exactly one piece**; "the format permits more ... but no multi-piece frame exists in this corpus" | **REFUTED**. 21 frames declare more than one piece; one declares four. §4.4 |
| `GRAPHICS_FORMAT.md` §10: "No direction names. The four slots are numbered" | **CONFIRMED as policy, and strengthened**: the engine's own facing computers produce four values and the axis split is observable, but the physical assignment is still only `INFERRED`. §5 |
| `LOGX_SPRITE_PROVENANCE.md` §7: the frame count is `1..16`, the four direction slots are at `+0x04 + 16*f + 4*d`, and the engine indexes the same expression | **CONFIRMED** |
| `LOGX_SPRITE_PROVENANCE.md` §15: "frame count interpretation, frame-record internals, piece counts, per-piece graphics pointers, OAM attributes and flip flags, frame origins" are handed to LOGX-FRAME-001 | delivered below, with two of those items refuted rather than confirmed |

### 1.2 LOGExtractor

`mainant/LOGExtractor`, `src/sprite_analysis.cpp` (per `GRAPHICS_FORMAT.md` §1),
is recorded as assuming an animation-leading `u32` frame count transformed by a
`value << 2` relationship, and as extracting multipart frames with directions,
pieces, X/Y offsets, dimensions, graphics data, flip/flag fields and sprite
origins.

| External claim | Verdict |
| --- | --- |
| an animation-leading value participates in `value << 2` | **CONFIRMED as a physical relationship, REFUTED as a frame-count formula**. What the engine does is multiply the *frame index* by 4 to walk a row of the cell table (`lsls r2,r2,#4` then `ldrb ... #0x10` then `lsls r2,r2,#2`); the animation's leading word is a count of *rows*, not a count of pointers. `count * 4` is exactly the number of cells, so the shift reproduces the flat pointer count - which is why the extractor produced plausible sprites - but "frame count" in the extractor's sense and the stored field are the same number only because a row has four cells. §3.3 |
| multipart frames with a piece count | **CONFIRMED**. 21 of 10,980 canonical frames declare 2 or 4 pieces. §4.4 |
| piece X/Y offsets, dimensions, graphics data, flip/flag fields | **PARTIALLY CONFIRMED / REFUTED in detail**. X/Y and the two extent bytes are real and engine-read; the graphics word is real; **no flip/flag word is stored in a piece on this image**. §4.2, §6.5 |
| sprite origins | **UNRESOLVED**. The constructor's offset arithmetic is the only origin evidence read; no hitbox, collision or feet-origin field was established. §6.4 |

---

## 2. SECTION A: THE 1,721 ANIMATION REFERENCES

PROJECT OBSERVATION (`--census`, section `animation_references`), reproduced from
the accepted sprite-definition census rather than re-derived:

| Population | Value |
| --- | ---: |
| definitions | 297 |
| inline array slots (`array_slots`) | 4,070 |
| **non-null animation references** | **1,721** |
| null slots | 2,349 |
| **unique animation targets** | **1,017** |
| shared targets (referenced more than once) | **410** |
| maximum reuse | **16** |
| malformed (non-ROM, or misaligned) references | **0** |
| minimum target | `0x083C3AC4` |
| maximum target | `0x086A899C` |
| alignment | every target word-aligned |

Reuse histogram over the 1,017 unique targets:
`1:607, 2:252, 3:88, 4:45, 5:12, 6:4, 8:7, 10:1, 16:1`.

**PROJECT CONCLUSION.** 1,721 references are 1,017 animation objects. Reference
count and object count are different populations and are reported separately
everywhere below. **Sharing does not imply semantic identity** and is not treated
as if it did: two definitions that select the same animation object select the
same poses, which is a statement about bytes, not about gameplay.

---

## 3. SECTION C/D/E: THE ANIMATION OBJECT

### 3.1 Physical layout

PROJECT OBSERVATION and PROJECT CONCLUSION, for every one of the 1,017 unique
objects:

```text
+0x00            u32 frame_count           1..16 on the canonical image
+0x04            u32 cell[4 * frame_count] 4-byte stride; row stride 16
+0x04 + 16*fc    u32 trailer_0_raw         recorded raw; UNRESOLVED
+0x08 + 16*fc    u32 trailer_1_raw         recorded raw; UNRESOLVED
```

* **`+0x00` PHYSICAL FIELD: CONFIRMED** as one little-endian `u32`. The halfword
  above it is `0` on all 1,017 objects, so a reader cannot distinguish a `u16`
  from a `u32` by the data alone, but the engine reads it as a word: the frame
  advance at `0x0800DE7E` is `ldr r3,[r3]` (no `ldrh`, no `ldrb` on that path),
  and the composite loop's bound at `0x0800F18A` and `0x0800F3EC` is
  `ldr r0,[r0]`.
* **`+0x00` FRAME-COUNT SEMANTIC: CONFIRMED**, and it is a count of *rows*, not
  of pointers. Two consumers:
  * `0x0800DE6C`: `ldrh r2,[r1,#0x12]` / `adds r2,#1` / store / `ldrb r3,[r0,#4]`
    / `lsrs r2,r3` / `ldr r3,[r1,#0x50]` / `ldr r3,[r3]` / `cmp r3,r2` /
    `bgt #0x800de90` / `strb r2,[r1,#0x11]`. The `ldr r3,[r3]` is
    `animation + 0x00` (the selected animation is `obj+0x50`); if the derived
    index has not reached it the index is stored, otherwise a class method runs.
  * `0x0800DEB0`: the wrap form of the same comparison, with `strh r0,[r1,#0x12]`
    resetting the timer when the count is exhausted.
  * `0x0800F188`: `ldr r0,[r4,#0x54]` / `ldr r0,[r0]` / `cmp r0,#0` / `ble`,
    bounding the composite piece loop.
* **`+0x00` EXTENT SEMANTIC: CONFIRMED.** The object is
  `0x04 + 16*frame_count + 8` bytes. Over the 1,016 consecutive pairs of unique
  animation objects, **no pair overlaps** (`animation_pairs_where_the_count_overruns_the_next_record: 0`)
  and every gap is a multiple of four. The gap *itself* is other data: the
  animation objects are interleaved with frame records and packed containers
  across one `0x083C3AC4..0x086A89D0` region, so a gap is never padding and is
  never used as an extent signal here.

### 3.2 The cell table

**`+0x04` STRUCTURAL MEANING: CONFIRMED.** `+0x04` begins a table of `4 *
frame_count` 32-bit ROM pointers with a 4-byte element stride and a 16-byte row
stride. The engine reaches cell `(frame, direction)` at
`animation + 0x04 + 16*frame + 4*direction`, which is flat index
`4*frame + direction`.

### 3.3 The `16*frame + 4*direction + 4` arithmetic

**EXTERNAL CLAIM (accepted handoff, LOGX-SPRITE-001 §15):** the engine's
arithmetic is `16*frame + 4*direction + 4`, and it must not be assumed to mean
four directions, four-byte pointers, sixteen bytes per frame or frame records
beginning at `+0x04` until this ticket establishes it.

**PROJECT OBSERVATION.** The arithmetic, or a restatement of it, appears in the
functions below. In the first seven the base is the *selected animation*
(`obj+0x50`, written by the selector `0x0800ECDA`), not the definition; the eighth
is the `obj+0x4C` variant described after them:

```text
0x0800EF38  ldrb r2,[r0,#0x11]   0x0800EF3A  ldr r1,[r0,#0x50]
0x0800EF3C  lsls r2,r2,#4        0x0800EF3E  adds r1,r1,r2
0x0800EF40  ldrb r2,[r0,#0x10]   0x0800EF42  lsls r2,r2,#2
0x0800EF44  adds r1,r1,r2        0x0800EF46  ldr  r1,[r1,#4]
0x0800EF48  str  r1,[r0,#0x54]                       ; -> the selected frame record

0x0800EF68  ldrb r3,[r1,#0x11]   0x0800EF6A  ldr r2,[r1,#0x50]
0x0800EF6E  lsls r3,r3,#4        0x0800EF70  adds r2,r2,r3
0x0800EF76  lsls r3,r3,#2        0x0800EF7A  ldr r3,[r2,#4]   ; screen position

0x0800FFA4  ... identical shape ...
0x080100A4  ... identical shape ...
0x08010192  ... identical shape ...
0x080272AE  ... identical shape ..., plus a composite
0x080273D6  ldrb r3,[r4,#0x11] / ldrb r1,[r4,#0x10] / lsls r3,r3,#4 /
            adds r2,r2,r3 / lsls r1,r1,#2 / adds r1,r2,r1 / ldr r1,[r1,#4]
0x0800F0A2  ldrb r1,[r4,#0x11] / ldr r0,[r4,#0x4c] / lsls r1,r1,#3 /
            adds r0,r0,r1 / ldrb r1,[r4,#0x10] / lsls r1,r1,#1 / adds r7,r0,r1
            ; NOT the cell table: base obj+0x4C, 8-byte rows, 0x80 terminator
```

**PROJECT CONCLUSION: CONFIRMED as a two-dimensional cell table.** Each of the
four readings the handoff warned against, resolved separately:

| Handoff caution | Verdict |
| --- | --- |
| "four directions" | **CONFIRMED as four positions and four engine values**; the physical assignment is `INFERRED` (§5) |
| "four-byte pointers" | **CONFIRMED**: every one of the 13,660 cells is a word-aligned ROM pointer |
| "sixteen bytes per frame" | **CONFIRMED as a row stride**, i.e. four 4-byte cells per frame index - not as a 16-byte frame record |
| "frame records beginning at `+0x04`" | **REFUTED**: the frame record's pieces begin at `+0x08` and are 12 bytes each (§4.1) |

Four independent measurements support the cell-table reading, none of which
depends on the others:

1. **All 13,660 cells are ROM pointers, and none is null.** Over the 1,017
   unique objects there are exactly `4 * frame_count` cells each, and the four
   direction positions each carry 3,415 of them. A direction-major reading with
   `frame_count` frames per direction would produce the same totals, so this
   measurement alone does not discriminate; it does eliminate an
   offsets-or-indices model.
2. **989 frame records are shared, and every shared one is reached from exactly
   one frame index** and from two, three or four direction indices
   (`shared_targets_confined_to_one_frame_index: 989`,
   `shared_targets_spanning_frame_indices: 0`). Under a direction-major table a
   shared target would be reached from one direction at several frames. This is
   the decisive structural measurement, and it is a property of the table alone.
3. **The target of a cell is a piece-count-bounded record with a 12-byte piece
   stride** (§4), which is a *pose*, not a row of a matrix.
4. **The frame advance wraps on `frame_count`** while a separate byte
   (`obj+0x10`) is left untouched, so the two indices have different lifetimes:
   one is advanced by the timer, the other is set by the facing logic.

**PROJECT CONCLUSION.** Seven functions index the cell table by
`4*frame + direction` from `obj+0x50`. `0x0800F0A2` indexes a **different**
table: its base is `obj+0x4C` (`0x0800F0A4 ldr r0,[r4,#0x4c]`), its row stride is
8 bytes and its direction stride 2, and it terminates on a `0x80` byte
(`0x0800F0B0 ldrb r0,[r7]` / `0x0800F0B2 cmp r0,#0x80` / `0x0800F0B4 beq`). That
table is the definition's `+0x50` parallel array - 10 of 297 definitions carry
one, per LOGX-SPRITE-001 §6 - and it is not a second reading of the cell table. It
is recorded here because the two are easy to conflate and because an earlier draft
of this ticket did conflate them.

### 3.4 The trailing words

PROJECT OBSERVATION over the 1,017 unique objects:

* `trailer_0` is `1` in **1,006** objects; the other eleven values are seven
  large raw words, one of them (`3825263616`) appearing six times.
* `trailer_1` takes **21** distinct values. `512:430, 1024:379, 4096:116,
  2048:38, 256:11` cover **974** objects; `0`, `64` and `128` appear once each;
  thirteen values are large raw words.

**PROJECT CONCLUSION: `trailer_0` and `trailer_1` SEMANTICS: UNRESOLVED**, with
one structural qualification that must be stated because it bounds the claim. The
counted object is `0x04 + 16*frame_count` bytes of table followed by two words, but
in **30 of the 1,017 objects a frame record starts exactly at the table's end**, so
in those 30 the two "trailer" words are that record's `u32 piece_count` and its
header - `1` is a piece count, not a trailer value. The two-word trailer extent is
therefore **not proven to exist at all**; what is proven is that the cell table
ends where the count says it does and that 987 objects have two words after it that
no read site was found for.

The shape of the remaining `trailer_1` values - powers of two, five values covering
974 of 1,017 - is *consistent with* a timing or scale field, and the ticket's
section G asked for timing; **no instruction was read that loads either word on the
animation path**, so no timing semantic is claimed. The values above 4,096 are not
plausibly timings and are recorded as raw words rather than filtered out.

---

## 4. SECTIONS F/I/J: THE FRAME RECORD AND ITS PIECES

### 4.1 The layout, and what the accepted layout got wrong

**PROJECT OBSERVATION.** For every one of the 10,980 distinct frame targets:

```text
+0x00            u32 piece_count      1..4 on the canonical image
+0x04            s8  min_x            the frame's bounding box over its pieces
+0x05            s8  min_y
+0x06            u8  width
+0x07            u8  height
+0x08            12-byte piece records, piece_count of them
```

**PROJECT CONCLUSION: the 8-byte header and the 12-byte piece stride are
CONFIRMED**, from two independent directions.

*From the engine.* The composite loop at `0x0800F3C0`:

```text
0x0800F3B4  ldr  r6,[r4,#0x40]        ; destination
0x0800F3BA  ldr  r0,[r0]              ; piece_count
0x0800F3BE  ble  #0x800f3f4
0x0800F3C0  lsls r1,r5,#1             ; r1 = 2*index
0x0800F3C2  adds r1,r1,r5             ; r1 = 3*index
0x0800F3C4  ldr  r0,[r4,#0x54]        ; the selected frame record
0x0800F3C6  lsls r1,r1,#2             ; r1 = 12*index
0x0800F3C8  adds r7,r0,r1             ; r7 = frame + 12*index
0x0800F3CA  adds r7,#8                ; r7 = frame + 8 + 12*index
0x0800F3CE  ldr  r0,[r7,#8]           ; the piece's graphics word
0x0800F3D6  adds r0,r7,#2
0x0800F3D8  ldrb r7,[r7,#2]           ; piece dimension 0
0x0800F3DA  ldrb r0,[r0,#1]           ; piece dimension 1
0x0800F3DE  muls r7,r0,r7             ; width * height
```

So `r7 = frame + 8 + 12*index`: the first piece is 8 bytes in and the entry stride
is 12. The same function reads `[r7,#2]` and `[r7,#3]` for the extents and
`[r7,#8]` for the container.

*From the corpus.* Given `(header, stride, dim_offset, graphics_offset)`, only
`(8, 12, +2, +8)` makes the whole corpus self-consistent: under it, **all 11,005
pieces** resolve to a container whose own declared decoded length equals
`dim_0 * dim_1`, with **zero** exceptions. The accepted `(4, 16, +6, +12)` model
leaves 25 pieces failing the same test, and an intermediate
`(4, 16, +6, +12)` reading of `+0x0C` as the graphics word resolves on 10,980 of
11,005. Independently, the 8+12 model predicts the address of the next known frame start
for **9,963 of the 10,979 consecutive frame pairs**, against **9,947** for the
accepted model (the population is pairs, not frames, and §9 states it that way);
both fall short of the total because 1,017 frame targets are shared sub-records of
a larger frame, which is a property of sharing and not of either model. The stronger form of the same test settles it without appeal to sharing:
under 8+12, **no** frame record's counted extent crosses the next known frame
start, and every one of the 1,017 records that does not end on a frame start ends
on a word that is itself a valid piece count. The accepted 4+16 model has the
opposite behaviour: it crosses the next frame start on 16 records.

**The header's four bytes are the frame's own bounding box - CONFIRMED.**
Measured over all 10,980 canonical frames: `+0x04`/`+0x05` (signed) equal the
minimum `x` and `y` over that frame's pieces on **10,980 of 10,980**, and
`+0x06`/`+0x07` (unsigned) equal the width and height of their union on **10,980
of 10,980**. The two multi-piece examples are the proof rather than an
illustration: `0x08423128`'s header is `(-8, -40, 32, 48)` for pieces at
`(-8,-40,32x32)` and `(-8,-8,32x16)`, and `0x08579890`'s is `(0, -80, 96, 96)`
for four pieces reaching from `x = 0` to `x = 96` and from `y = -80` to
`y = 16`. The engine reads the same bytes: `0x0800F38E`/`0x0800F390` load
`frame+6` and `frame+7` and `0x0800F392` multiplies them to size the composite
buffer, and the spawn constructor at `0x080273F0`/`0x080273F4` reads `frame+4`
and `frame+5` as the entity's initial offsets.

**The one correction this ticket makes to `GRAPHICS_FORMAT.md` §2 is an offset,
not a layout.** That document's OAM attribute pair is real and its bit layout is
right; it is stored at piece **`+0x04`**, and what the document places at `+0x08`
is the piece's graphics-container word. See §6.5, where the decode is verified
against the corpus.

### 4.2 The piece fields

| Piece offset | Physical field | Engine read | Corpus observation |
| --- | --- | --- | --- |
| `+0x00` | `s8` | `ldrsb` at `0x080273F0`, `0x0800F204`, `0x0800FE36`, `0x080101DE` | `-32..8`, 17 distinct values |
| `+0x01` | `s8` | `ldrsb` at `0x080273F4`, `0x0800FFFA` | `-109..96`, 18 distinct values |
| `+0x02` | `u8` | `ldrb` at `0x0802740C`, `0x0800F206`, `0x080101E2`, halved at `0x0800F20A` | `8, 16, 32, 64` |
| `+0x03` | `u8` | `ldrb` at `0x08027410`, `0x0800F22A`, `0x080101FE`, halved at `0x0800F230` | `8, 16, 32, 64` |
| `+0x04` | `u32` packed OBJ attribute pair `(attr1 << 16) \| attr0` | `ldr` at `0x0800F1C2` and `0x0800F24C`, merged into the outgoing OAM word under mask `0xFE00FFFF` (pool `0x0800F4B0`) | 16 distinct words; shape in `{0,1,2}`; see §6.5 |
| `+0x08` | `u32` | `ldr` at `0x0800F3CE` | the graphics-container word, 11,005 of 11,005 |

Detailed distributions (over the 11,005 pieces):

* dimension 0: `8:12, 16:3977, 32:5645, 64:1371`.
* dimension 1: `8:8, 16:78, 32:9252, 64:1667`.
* the pair is one of **16** combinations, all of whole 8x8 tiles, and in every
  case `dim_0 * dim_1` equals the container's declared decoded length.

**PROJECT CONCLUSION.**
* **PIECE POSITION FIELDS: CONFIRMED as two signed byte offsets at `+0x00` and
  `+0x01`.** The renderer reads piece `+0x00` with `ldrsb` at `0x0800F204`,
  piece `+0x01` at `0x0800F22A`, and piece `+0x01` again at `0x0800F25E`, and
  adds each to its own coordinate. **The frame header carries the same two fields
  for the whole frame** (`0x080273F0`/`0x080273F4` read `frame+4`/`frame+5`, not a
  piece), which is how the spawn path positions an entity from a pose without
  walking its pieces. **Which axis is which is INFERRED** and is not
  independently labelled by the image.
* **POSITION ORIGIN: UNRESOLVED.** The offsets are relative to the entity's own
  coordinates and nothing read here establishes a hitbox, collision, feet or
  camera anchor. The ticket's section P caution is honoured: no X/Y offset is
  called an origin.
* **PIECE SIZE REPRESENTATION: CONFIRMED as two unsigned byte extents at `+0x02`
  and `+0x03`, in pixels.** The engine halves dimension 0 to centre an OBJ
  horizontally (`0x0800F20A lsrs r3,r3,#1` then `0x0800F20C subs r7,r6,r3`) and
  dimensions 1 similarly (`0x0800F230`), multiplies the pair to size the
  composite buffer (`0x0800F3DE muls r7,r0,r7`), and the product equals the
  container's own declared decoded length on every piece. These are **stored
  fields**, not derived dimensions.
* **`+0x04` IS the packed OBJ attribute pair** - see §6.5. It is not
  unexplained; the earlier draft of this ticket recorded it as raw and was wrong.

### 4.3 Frame count over the corpus

| Population | Value |
| --- | ---: |
| unique animation objects | 1,017 |
| frame-count distribution (`--census`, `cells.frame_count_distribution`) | `1:80, 2:275, 3:180, 4:407, 5:16, 6:13, 7:11, 8:3, 9:2, 10:2, 11:24, 12:2, 16:2` |
| minimum frame count | 1 |
| maximum frame count | 16 |
| zero-frame animations | **0** |
| **frame units** (sum of frame counts over unique objects) | **3,415** |
| cells over unique objects | 13,660 |
| animation references | 1,721 |
| cells over references | 23,068 |
| healthy references | 1,721 of 1,721 |

There is no separate timeline/duration array: playback derives the frame index
from a timer and bounds it with the stored count (§6.6). **Zero-frame animations
do not occur.**

### 4.4 Multipart frames

| Population | Value |
| --- | ---: |
| unique frame records | 10,980 |
| piece records over those frames | 11,005 |
| piece-count distribution | `1:10959, 2:19, 4:2` |
| frames with more than one piece | **21** |
| maximum piece count | **4** |
| minimum piece count | **1** |
| frames whose pieces all resolve to a container | 10,980 of 10,980 |
| frames whose pieces are reached by an animation reference | 11,005 of 11,005 |

**PROJECT CONCLUSION: MULTIPART FRAMES: CONFIRMED.** The count is a `u32` read in
a loop bounded by itself (`0x0800F3BA..0x0800F3F2`), so it is never a sentinel and
is never inferred by scanning bytes for a plausible-looking value. Worked
examples:

* `0x08423128`, two pieces: piece 0 at `0x08423130` (`x=-8, y=-40, dims 32x32`,
  graphics `0x084224E0`, container declares 1024), piece 1 at `0x0842313C`
  (`x=-8, y=-8, dims 32x16`, graphics `0x0842259C`, container declares 512). The
  record ends at `0x08423148` and the next record begins there.
* `0x08579890`, four pieces, reached by definition 146: `64x64` + `32x64` +
  `64x32` + `32x32`, containers declaring `4096, 2048, 2048, 1024`, at
  `(0,-80)`, `(64,-80)`, `(0,-16)`, `(64,-16)`. This is a four-part composite.

This **refutes** the accepted statements that all 10,959 frames declare exactly
one piece and that no multi-piece frame exists in the corpus. The 21 multi-piece
frames are reached by 6 animations, and the four-part frame's animation is one of
the records the accepted reader's art filter drops, which is why the accepted
corpus never observed one.

---

## 5. SECTION Q: DIRECTION COUNT, SEMANTIC AND ORDER

Three separate claims, kept apart as the ticket requires.

**FOUR-POSITION STRUCTURE: CONFIRMED.** Two independent lines of evidence.

1. The cell table is four wide for every animation object, whatever its
   `frame_count` (§3.2), and all four positions are populated on all 1,017
   objects.
2. The engine produces the direction index as one of exactly four compile-time
   constants. `0x0800A890` and `0x080159B0` are two facing computers; each
   loads two coordinate differences, takes their absolute values, compares them,
   and writes a constant to `obj+0x10`:

```text
0x0800A8A4  subs r2,r2,r4     ; dx
0x0800A8A8  subs r3,r3,r4     ; dy
0x0800A8BA  cmp  r4,r5        ; |dx| vs |dy|
0x0800A8BC  blt  #0x800a8ce   ; vertical wins -> 0 or 1 below
0x0800A8C2  movs r2,#3        ; 0x0800A8C4 strb r2,[r1,#0x10]
0x0800A8C8  movs r2,#2        ; 0x0800A8CA strb r2,[r1,#0x10]
0x0800A8CE  cmp  r3,#0        ; dy
0x0800A8D2  movs r2,#0        ; 0x0800A8D4 strb r2,[r1,#0x10]
0x0800A8D8  movs r2,#1        ; 0x0800A8DA strb r2,[r1,#0x10]
```

The eight sites (`0x0800A8C2`, `0x0800A8C8`, `0x0800A8D2`, `0x0800A8D8`,
`0x080159D4`, `0x080159DC`, `0x080159E6`, `0x080159EC`) write exactly
`{0, 1, 2, 3}`, and **no other instruction writes a literal to `obj+0x10` next to
a store**. A third family (`0x0800A8C4`-style store sites in at least four other
functions) reaches the same four-value pattern from movement vectors.

**DIRECTION SEMANTIC: PARTIALLY CONFIRMED, with the axis split `INFERRED`.**
Both facing computers compare `|dx|` with `|dy|` first and only reach the
vertical pair when the horizontal pair does not dominate. Therefore:

* values **2 and 3** belong to the horizontal axis, and the sign of `dx` chooses
  between them (`0x0800A8BE cmp r2,#0` / `ble` picks 2, falling through picks 3;
  `0x080159D0 cmp r1,#0` / `ble` picks 2);
* values **0 and 1** belong to the vertical axis, and the sign of `dy` chooses
  between them (`0x0800A8CE cmp r3,#0` / `ble` picks 1, falling through picks 0;
  `0x080159E2 cmp r2,#0` / `ble` picks 1).

**INDIVIDUAL DIRECTION ORDER: UNRESOLVED in the physical sense.** The sign
convention above makes "`3` is the direction of positive `dx`" and "`0` is the
direction of positive `dy`" a mechanical consequence of the code, and *if* the
compared coordinates are screen coordinates with the screen's usual downward Y
then `0` is screen-down, `1` screen-up, `2` screen-left and `3` screen-right. That
conditional is **not established**: runtime capture was not performed in this
ticket, the coordinate objects compared are `obj+0x20`/`obj+0x24` of two entities
and their axis orientation was not observed, and section Q forbids naming
directions from artwork. The ordering is therefore recorded as `INFERRED` at the
sign level and `UNRESOLVED` at the screen level.

What the four positions *are* is further constrained by data, and the reading is
recorded rather than promoted:

* **702 frame units have all four cells pointing at the same record** and 287
  have three of four the same, so many poses are direction-independent.
* Over the 3,415 poses there are **20,490 direction pairs**; **8,713** of them
  share a graphics container, **5,420** of those with byte-identical attribute
  words and **3,293** with differing ones. An attribute difference between two
  cells that share art is therefore common, which is what a per-cell flag looks
  like.
* The horizontal pair is the decisive case. There are exactly **2,600 poses where
  directions 2 and 3 differ in attribute-1 bit 12**, and in those the two cells
  name the **same** container in **2,599** cases (a different one once). Over
  same-container horizontal pairs the attribute delta is `+0x10000000` on 2,580,
  `-0x10000000` on 19 and `0` on 753. **Bit 12 is therefore a stored horizontal
  flip applied to the same graphic**, which is exactly what a flip flag looks
  like - and this **reverses** what an earlier draft of this ticket concluded from
  the same data (§11).

**A correction this ticket made to its own reasoning, recorded because it was
load-bearing.** An earlier draft counted direction pairs whose **frame records**
differed and reported them as pairs whose **containers** differed. Two distinct
frame records routinely name the same container - that is precisely the sharing
in §6.3 - so the count measured nothing and the conclusion drawn from it was the
exact inverse of the truth. The corrected measurement is above.

---

## 6. SECTIONS H/K/L/M/N/O/P: CENSUSES AND FIELD SEMANTICS

### 6.1 Frame/direction target census (section H)

Populations, kept apart:

| Population | Value |
| --- | ---: |
| animation objects | 1,017 |
| frame units (rows) | 3,415 |
| cells | 13,660 |
| non-null cells | **13,660** |
| null cells | **0** |
| central cell references (over animation references) | 23,068 |
| **unique frame targets** | **10,980** |
| shared frame targets | 989 |
| maximum frame reuse | 4 |
| frame-reuse histogram | `1:9991, 3:287, 4:702` |
| cells by direction index | `0:3415, 1:3415, 2:3415, 3:3415` |
| distinct cells per frame unit | `1:702, 2:287, 4:2426` |

The four direction positions are exactly balanced, which is a direct consequence
of the `4*frame_count` table size and is not independent evidence of anything
else.

### 6.2 Multipart piece census (section J)

| Population | Value |
| --- | ---: |
| piece references over unique frames | **11,005** |
| piece references over animation references | 23,180 |
| unique frames | 10,980 |
| multi-piece frames | 21 |
| minimum / maximum pieces per frame | 1 / 4 |

### 6.3 Sharing and deduplication at each layer (section R)

| Layer | References | Unique targets | Max reuse | Shared targets |
| --- | ---: | ---: | ---: | ---: |
| definition inline array -> animation | 1,721 | 1,017 | 16 | 410 |
| animation cell -> frame record | 13,660 | 10,980 | 4 | 989 |
| frame piece -> graphics container | 11,005 | 7,390 | 24 | 2,614 |

Reference count and unique-object count are reported separately at every layer.
**Sharing is not treated as semantic equivalence**: 989 frame records are reached
from more than one cell, 702 of them from four cells of the same pose, and the
census never converts a shared pointer into a claim that two animations are the
same animation.

### 6.4 Piece position fields (section K)

See §4.2. `+0x00` and `+0x01` are signed byte offsets added to the entity's own
coordinates by two engine consumers; the axes are `INFERRED`, and no origin,
anchor, hitbox or feet position is claimed. **Combat and collision semantics are
out of scope for this ticket and were not investigated.**

### 6.5 Piece size, shape and flags (sections L and M)

**PIECE SIZE REPRESENTATION: CONFIRMED twice over.**

* *Stored pixel extents*: the two bytes at `+0x02`/`+0x03`, read by the renderer
  (`0x0800F206`, `0x0800F22E`), halved by the engine to centre an OBJ
  (`0x0800F20A`, `0x0800F230`), multiplied to size the composite buffer
  (`0x0800F3DE`), and equal to the container's own declared decoded length on all
  11,005 pieces.
* *Raw OAM attribute bits*: **PRESENT**, at `+0x04`, as one `u32` packing
  attribute 1 in the high half and attribute 0 in the low half - the layout
  `GRAPHICS_FORMAT.md` §2 describes, at a different offset. The engine loads it
  at `0x0800F1C2` (`ldr r3,[r0,#4]`) and `0x0800F24C` (`ldr r6,[r0,#4]`) and
  merges it into the outgoing OAM word under the mask literal `0xFE00FFFF`
  (pool `0x0800F4B0`), which keeps attribute 0 in full and attribute 1 bits 9-15
  - the tile-number and priority-range bits are rebuilt from entity state.

**The two representations agree on every piece, and that agreement is the
evidence.** Decoded as `(attr1 << 16) | attr0` with the GBATEK shape/size table
and shape = attribute-0 bits 14-15, size = attribute-1 bits 14-15:

| Measure | Value |
| --- | ---: |
| pieces | 11,005 |
| colour-256 (attribute-0 bit 13) set | **11,005** |
| shape 3 (reserved on this hardware) | **0** |
| shape/size decode equals the stored `dim_0`/`dim_1` | **11,005 of 11,005** |
| shape distribution | `0:6656, 1:73, 2:4276` |
| size distribution | `0:12, 1:47, 2:9233, 3:1713` |
| distinct attribute words | 16 |
| horizontal flip (attribute-1 bit 12) set | 2,848 |
| vertical flip (attribute-1 bit 13) set | **0** |

The independent agreement between a bit-field decode and a separately stored pair
of extents, on all 11,005 pieces, is what makes this a stored attribute word and
not a coincidence. Two consequences:

* **Shape/size: CONFIRMED** as raw attribute bits, and the pixel dimensions
  `GRAPHICS_FORMAT.md` derives from them are **derived**, not stored - the stored
  fields are the two extent bytes and the attribute pair, and they agree.
* **Horizontal flip: CONFIRMED as a stored bit** (2,848 pieces set it) and
  **UNRESOLVED as a rendering behaviour**: the engine's OAM path under the
  `0xFE00FFFF` mask preserves the bit, and no runtime observation of the mirrored
  result was made here. **Vertical flip: CONFIRMED absent** from the canonical
  corpus (0 of 11,005), which is a data fact about this game rather than a
  statement about the hardware.

This **refutes** the earlier draft of this ticket, which recorded the four bytes
as unexplained and claimed no attribute word was stored, and it **corrects**
`sprite_graphics.Piece` by one offset: the attribute word is at `+0x04`, so the
shape/size/flip properties belong there rather than being removed.

**PALETTE RELATIONSHIP: UNRESOLVED at the piece level.** No piece carries a
palette index or a palette pointer: the record is 12 bytes and all six fields are
accounted for. Whether a global or per-definition palette is used is
`GRAPHICS_FORMAT.md` §5's single global object palette, and nothing in this
ticket contradicts it; nothing in a frame or piece selects one.

### 6.6 Frame timing and playback (section G)

**FRAME TIMING: PARTIALLY CONFIRMED, at the mechanism level only.**

PROJECT OBSERVATION. Three engine sites advance the animation:

```text
0x0800DE6C  ldrh r2,[r1,#0x12]   ; a u16 counter on the entity
0x0800DE70  adds r2,#1
0x0800DE72  lsls r2,r2,#0x10
0x0800DE74  lsrs r2,r2,#0x10     ; wrap to 16 bits
0x0800DE76  strh r2,[r1,#0x12]
0x0800DE78  ldrb r3,[r0,#4]      ; a shift amount from the state object
0x0800DE7A  lsrs r2,r3           ; frame index = counter >> shift
0x0800DE7C  ldr  r3,[r1,#0x50]   ; the selected animation
0x0800DE7E  ldr  r3,[r3]         ; animation + 0x00 = frame_count
0x0800DE80  cmp  r3,r2
0x0800DE82  bgt  #0x800de90
0x0800DE90  strb r2,[r1,#0x11]   ; in range: publish the frame index
```

and `0x0800DEB0` is the same computation with a wrap
(`0x0800DEC6 movs r0,#0` / `0x0800DEC8 strh r0,[r1,#0x12]`) that restarts the
counter when the count is exhausted. `0x08010398`..`0x080103A6` is a third
variant that derives the index as `(counter >> 1) >> 2`, i.e. a quarter-speed
frame.

**PROJECT CONCLUSION.**
* **Frame counter width: CONFIRMED** as a 16-bit counter (`strh`/`ldrh` at
  `obj+0x12`), separate from the 8-bit published frame index at `obj+0x11`.
* **Per-frame versus global timing: UNRESOLVED.** The shift amount is read from
  a *state object* (`[r0,#4]` where `r0` is the animation's state), so the rate
  is not stored in the animation record on this path. Nothing read connects the
  animation's two trailer words to the timer, so their timing interpretation
  remains open.
* **Looping: CONFIRMED present** in the wrap form at `0x0800DEB0`; **terminal
  behaviour, ping-pong and completion state: UNRESOLVED.** A frame index of
  `frame_count` is out of range and the two advance forms react differently (one
  calls a class method, one resets the counter), which is consistent with more
  than one loop policy, and this ticket did not chase the gameplay state machine.

---

## 7. SECTION N: THE GRAPHICS RELATIONSHIP

**GRAPHICS-RESOURCE RELATIONSHIP: CONFIRMED as a pointer to a packed container,
with the resolution test stated.**

PROJECT OBSERVATION over the 11,005 pieces:

| Measure | Value |
| --- | ---: |
| piece references | 11,005 |
| pieces whose `+0x08` resolves **and** whose container's declared decoded length equals `dim_0 * dim_1` | **11,005** |
| unresolvable pieces | **0** |
| pieces whose word is not a pointer | 0 |
| distinct container offsets reached | **7,390** |
| distinct containers that decode | **7,390** |
| containers that fail to decode | **0** |
| region occupied by the targets (file offsets) | `0x003C34D0..0x006A87A8` |
| every target word-aligned | yes |
| every target inside the measured region | yes |

**Stored forms.** On this image **every** piece stores the full GBA address form
(`0x08xxxxxx`, 11,005 of 11,005); **zero** store a bare file offset. The reader
accepts the file-offset form as well, because the same reader must serve a
differently-authored image, and the census reports which form it saw. An earlier
draft of this ticket reported a 19-piece "relative" minority; that measurement was
an artifact of the refuted 16-byte piece stride and is withdrawn.

**What this does and does not establish.**

* It **does** establish that the graphics relationship is a pointer to a Webfoot
  packed container, and that the piece independently states the container's
  decoded size. 11,005 independent agreements between a stored size and a
  container header is the same class of evidence TOOLKIT-010 used for the 7,355
  containers it accepted.
* **The joint test alone is not unique in the record's neighbourhood.** On 7 of
  the 21 multi-piece frames the frame header's own `+0x04` word, read as a
  pointer, also decodes to a container of exactly the piece's stated size;
  inside the 12-byte piece, by contrast, `+0x00`, `+0x04`, `+0x0C` and `+0x10`
  satisfy the test on **zero** pieces of 11,005. The graphics word is therefore
  fixed by the engine's own `ldr r0,[r7,#8]` at `0x0800F3CE` **and** by the
  11,005-piece agreement, not by the joint test alone. An earlier draft presented
  the joint test as if it were unique; it is 99.94% unique at frame level, and the
  exception is recorded rather than hidden.
* The engine instruction that loads the word is `0x0800F3CE`
  (`ldr r0,[r7,#8]` with `r7 = frame + 8 + 12*index`), inside the composite loop.
  That loop also reads the two extents and calls the container copy path.
* It **does not** establish a graphics *resource id*, a tile index, a
  VRAM-relative index or a palette binding. The word is a file/GBA address into
  packed data, not an index.
* **Handoff boundary:** unknown or unindexed graphics discovery, container
  taxonomy and any graphics family outside the actor/character chain remain
  LOGX-GFXSCAN-001's. This ticket neither starts it nor widens it.

**A population disagreement with accepted material, recorded rather than
reconciled.** This ticket counts **7,390** distinct container offsets reached by
a piece; `GRAPHICS_FORMAT.md` §4 publishes **7,355 unique graphics containers`.
Both are exceeded by the 10,980 pieces and 7,390 decodes here. The likely cause is
that the accepted reader deduplicates shared containers differently: the 21
multi-piece frames, two of which sit in the animations the accepted art filter
rejects, and the accepted reader's per-frame container projection would not have
enumerated them. **This ticket does not claim the accepted figure is wrong** - it
counts a differently-defined population - and does not silently widen the
accepted number. The reconciliation is handed to synthesis.

**Corrections this ticket made to its own earlier drafts, recorded rather than
quietly patched.** Three intermediate revisions of this research were wrong, and
every one was caught by the independent review gate:

1. An early revision used `to_file_offset` plus a region test as the resolution
   rule, which accepted words such as `0x80002000` that resolve as GBA addresses
   but point into the code area. The final rule requires all three conditions
   (resolve, land in the region, decode with a matching declared size), and under
   it the canonical corpus has **zero** anomalies.
2. A later revision recorded the piece's `+0x04` word as an unexplained "four raw
   bytes" and asserted that no piece stores an OAM attribute word. Both were
   false; §6.5 carries the measurement that refutes them. The four bytes are the
   attribute pair, and the shape/size decode agrees with the separately stored
   extents on 11,005 of 11,005 pieces.

The malformed records described in LOGX-SPRITE-001 §13.7 and §14.8 - the four
art-filter-rejected animations and the five frame pointers its reader dropped -
**do not exist under the corrected layout**: those records' pieces are ordinary
pieces, and the reader's rejection was an artifact of the 16-byte piece stride.

---

## 8. NEGATIVE-COVERAGE STATEMENTS

Absence claims are scoped, per [`../research-conventions.md`](../research-conventions.md).

**8.1 The piece record's field set.** *Superseded claim.* An earlier draft asserted
that no canonical piece stores an OAM attribute word. That was **false**; §6.5
carries the measurement that refutes it. What survives is the narrower and
testable statement: the record is 12 bytes and **every one of its six fields has a
located engine read** - `+0x00`, `+0x01`, `+0x02`, `+0x03` and `+0x08` in the
renderer, `+0x04` in the OAM merge. There is no room for a further field, and none
is claimed. What this does **not** cover: a different build, a different game, or a
hand-authored record.

**8.2 The piece attribute word's consumers.** *Superseded claim.* An earlier
draft of this document asserted that no instruction decodes piece `+0x04` as
flags. That was **false**: `0x0800F1C2` and `0x0800F24C` load it and merge it
into the outgoing OAM word under the `0xFE00FFFF` mask. The claim is replaced by
the positive evidence in §6.5, and the search window that made it look empty
(`0x0800F0CA..0x0800F17E`) stopped 0x44 bytes before the first consumer. The
lesson is recorded rather than quietly patched: a windowed search is only as good
as its window, and this one was not validated against a known positive before the
absence claim was written.

**8.3 No direction names.** The claim is that the image does not name a
direction. Coverage: the values `0..3` are produced from sign comparisons in the
facing computers, and no table, string or constant in the image attaches a label.
Naming a direction from artwork alone is forbidden by the ticket and was not
attempted.

**8.4 No palette field in a frame or piece.** The claim is that neither record
selects a palette. Coverage: every byte of a piece is accounted for by an engine
read or by the graphics resolution test, and the frame header's second word has
no located consumer. This does not cover a palette selected by the *definition*
or globally, which is outside this ticket.

**8.5 Multi-piece frames are not an inference.** The claim that 21 frames declare
more than one piece is a direct read of a `u32` bound at `0x0800F3BA` and was
checked piece by piece: every one of the 21 frames' pieces resolves to a
container whose declared size equals the piece's stated extents.

---

## 9. SECTION S: OBJECT BOUNDARIES AND PADDING

**How each extent is bounded.**

* **Animation object**: by its own `frame_count` (`0x04 + 16*fc + 8`). Measured
  against the next unique animation object, no pair overlaps and every gap is a
  multiple of four. The gap is **other data** - the objects sit inside a region
  shared with frame records and containers - so the gap is never used as the
  extent and no padding is claimed.
* **Frame record**: by its own `piece_count` (`8 + 12*n`). 9,963 of the 10,979
  consecutive pairs place the next known frame start exactly at that end; the
  remainder are shared sub-records and are reported as such.
* **Piece**: fixed 12 bytes.
* **Container**: by the container's own packed extent, as the accepted reader
  already measures.

**No extent in this ticket is derived from "next pointer minus current pointer".**
Where that measurement is reported it is reported *as* a gap histogram and
nothing else, precisely because the region is interleaved.

---

## 10. SECTION T: MALFORMED AND NULL BEHAVIOUR

Static engine evidence, plus what the corpus contains. **The canonical ROM was
never mutated**; the synthetic mutations used by the tests are applied to
in-memory copies only.

| Case | Engine behaviour (static) | Corpus incidence |
| --- | --- | --- |
| null animation slot (`definition + 0x54 + 4*i` is zero) | the selector `0x0800ECDA` copies the word into `obj+0x50` with no null test, so the animation base becomes null; the five count-guarded sprite sites of LOGX-SPRITE-001 §4 null-test the element they load | 2,349 of 4,070 slots |
| null cell | not applicable: **0 of 13,660 cells are null** | 0 |
| out-of-range frame index | the advance clamps to `frame_count` (`0x0800DE80`, `0x0800DEC2`), so the index never exceeds it on that path; the render arithmetic itself has no bound check, so a caller that passes a larger row would read the trailer or the next object | not exercised by the canonical corpus |
| out-of-range direction | the cell arithmetic has no check; the direction byte comes from the facing computers, whose only literals are `0..3` | not exercised |
| zero piece count | `read_frame` refuses it, and the engine's own loop `ble`s out at `0x0800F3BE` | 0 of 10,980 |
| malformed piece graphics word | **not null-tested.** `0x0800F3A4 ldr r2,[r1]` beside `0x0800F3A6 cmp r2,#0` is a **container-kind** test: it checks the loaded container's first word, and the zero branch is the stored (`kind 0`) fast path. Since all 11,005 canonical containers are `kind 1`, that fast path is unreachable here, and the piece's container pointer is dereferenced with no null test | 0 of 11,005 |
| malformed animation target | `read_animation` refuses a frame count outside `1..16` or a nonzero second halfword | 0 of 1,017 |

**ORIGINAL ENGINE BEHAVIOUR versus HOST TOOL SAFETY POLICY.** The engine's
selector does not null-test what it loads; the host tool does, by refusing to
parse a null animation target rather than reading address zero. The engine's cell
arithmetic has no range check; the host tool raises rather than reading outside
the record. Those are deliberately different, and the host tool does not
reproduce an unsafe read in order to be faithful.

---

## 11. SECTION U: DISAGREEMENTS WITH LOGEXTRACTOR AND WITH ACCEPTED MATERIAL

| Item | LOGExtractor / accepted position | This ticket | Classification |
| --- | --- | --- | --- |
| animation-leading value and `value << 2` | the value is a frame count and `<< 2` participates in interpreting it | the value is a count of table rows; the engine multiplies the **frame index** by 4 to walk a row. `count * 4` happens to be the flat cell count, which is why the extractor's sprites looked right | **PARTIALLY CONFIRMED**: the physical word is a count and the `<< 2` arithmetic is real; the formula's *interpretation* is refined |
| frame/direction organisation | four direction slots per frame, direction-major | **CONFIRMED** exactly | **CONFIRMED** |
| piece-record stride | 16 bytes | **12 bytes**, with an 8-byte frame header | **REFUTED** |
| piece-count logic | a full word | **CONFIRMED** as a `u32` loop bound | **CONFIRMED** |
| piece coordinates | X/Y offsets at `+0x00`/`+0x01` | **CONFIRMED** as two `s8` added to the entity's coordinates; axes `INFERRED`, origin `UNRESOLVED` | **PARTIALLY CONFIRMED** |
| piece dimensions | width/height | **CONFIRMED**, as stored byte extents whose product is the container's decoded size | **CONFIRMED** |
| flip/flag fields | a flag word at `+0x08` | no stored flag word exists on this image; bit 12 of the middle bytes tracks a *different* container | **REFUTED** |
| graphics addressing | a container pointer | **CONFIRMED**, with the resolution test over all 11,005 pieces | **CONFIRMED** |
| sprite origins | visual compensation for assembly | not established; only the constructor's offsets were read | **UNRESOLVED** |
| multipart frames | exist | **CONFIRMED**: 21 frames, up to 4 pieces | **CONFIRMED** |
| "all 10,959 frames declare exactly one piece" | accepted project statement | **REFUTED** | **REFUTED** |
| "7,355 unique graphics containers" | accepted project figure | **CONFIRMED as an exact subset**: 7,355 is precisely the set of containers reached by single-piece frames; the accepted reader's 16-byte stride rejects all 21 multi-piece frames, which reach 35 further containers | **CONFIRMED**, with the gap explained by the refuted stride rather than by a filter |
| "5 frame pointers do not resolve" | accepted project statement | under the corrected layout, 0 pieces fail to resolve | **REFUTED** |
| piece `+0x04` | an unexplained four-byte field (this ticket's earlier draft) | the packed OBJ attribute pair, whose decode agrees with the stored extents on 11,005 of 11,005 pieces | **REFUTED** (self-correction) |
| the frame header's second word | a raw `u32` (this ticket's earlier draft) | `s8 min_x`, `s8 min_y`, `u8 width`, `u8 height` - the bounding box of the frame's pieces, exact on 10,980 of 10,980 frames | **REFUTED** (self-correction) |
| graphics-pointer forms | 10,980 absolute + 25 relative (this ticket's earlier draft) | 11,005 absolute, 0 relative | **REFUTED** (self-correction) |
| graphics region lower bound | 1,332 bytes below the accepted figure (this ticket's earlier draft) | `0x003C34D0` **equals** the figure `GRAPHICS_FORMAT.md` §9 records | **REFUTED** (self-correction) |
| frame/direction arithmetic sites | "nine functions, base `obj+0x50` in each" (this ticket's earlier draft) | **seven** functions use base `obj+0x50`; `0x0800F0A2` addresses a different per-animation table from base `obj+0x4C`, with an 8-byte row and a `0x80` terminator | **PARTIALLY CONFIRMED** (self-correction) |

No agreement is claimed on the basis of visual similarity. Every "CONFIRMED"
above rests on an instruction site or on a corpus-wide test whose failure
condition is stated.

---

## 12. SECTION X: FULL-CENSUS ARITHMETIC

Every headline number with its population. Independent reviewers must be able to
reproduce each row from `--census`.

| # | Population | Value | Where |
| ---: | --- | ---: | --- |
| 1 | definitions | 297 | `animation_references.definitions` |
| 2 | inline array slots | 4,070 | `animation_references.array_slots` |
| 3 | animation references (non-null) | 1,721 | `animation_references.non_null_references` |
| 4 | unique animation objects | 1,017 | `animation_references.unique_animation_targets` |
| 5 | frame units (rows) over unique objects | 3,415 | `cells.frame_units` |
| 6 | cells over unique objects | 13,660 | `cells.cells` |
| 7 | non-null cells | 13,660 | `cells.non_null_cells` |
| 8 | cells over animation references | 23,068 | `animation_walk.cell_references` |
| 9 | unique frame targets | 10,980 | `cells.unique_frame_targets` |
| 10 | frame-record references | 13,660 | `cells.cells` |
| 11 | piece references (over unique frames) | 11,005 | `frames.piece_references` |
| 12 | piece references (over animation references) | 23,180 | `animation_walk.piece_references` |
| 13 | graphics references | 11,005 | `graphics.piece_references` |
| 14 | unique graphics targets | 7,390 | `graphics.unique_targets` |
| 15 | multi-piece frames | 21 | `frames.multi_piece_frames` |
| 16 | shared graphics targets / max reuse | 2,994 / 24 | `pieces.graphics_reuse_histogram` |

Identity checks a reader can perform without re-deriving anything:

* `1,721 > 1,017` - references exceed unique objects at the animation layer;
* `13,660 = 4 * 3,415`, and **`3,415 =` the frame-count-weighted sum**
  `sum(k * count(k))` over `frame_count_distribution`. The *unweighted* sum of that
  distribution is **1,017**, the number of animation objects; the two must not be
  interchanged, and an earlier draft of this document did interchange them;
* the piece total is the sum of `piece_count_distribution` weighted by count:
  `10,959 + 2*19 + 4*2 = 11,005`;
* `13,660 - 10,980 = 2,680` reuse slots beyond first use, and the histogram
  accounts for exactly that: a pose with three equal cells contributes **2** extra
  references and one with four contributes **3**, so `2*287 + 3*702 = 2,680`. An
  earlier draft wrote `3*287 + 4*702`, which is 3,669 and wrong - the extra
  references are one fewer than the number of equal cells, because the first
  reference is not an extra one;
* `989 = 287 + 702`: the shared frame targets are exactly the poses whose cells
  are not all distinct, an independent cross-check of both figures;
* `23,068 != 13,660` and `23,180 != 11,005`, because the walk counts a shared
  animation once per definition that selects it.

---

## 13. SECTION B: THE ENGINE CONSUMERS

Functions read in full or in the part that establishes a field, with the argument
roles and field offsets this ticket relies on.

| Address | Role | Field accesses |
| --- | --- | --- |
| `0x0800ECDA` | animation selector `(obj, index)` | `obj+0x58` definition, `def+0x54+4*index`, `obj+0x50`, `def+0x50`/`obj+0x4C` (reused from LOGX-SPRITE-001) |
| `0x0800EF38` | methods: recompute the current frame record | reads `obj+0x11`, `obj+0x50`, `obj+0x10`; writes `obj+0x54` |
| `0x0800EF66` | methods: screen position | reads `obj+0x11`, `obj+0x50`, `obj+0x58`, `obj+0x10`, `obj+0x6C`, `obj+0x70`, frame `+0x05` |
| `0x0800EF94` | the renderer | reads `obj+0x54` (the frame record), `obj+0x50`, `obj+0x4C`, `obj+0x10`, `obj+0x11`, `obj+0x60`, `obj+0x6C`, `obj+0x70`, `obj+0x68`, `obj+0x58`, `obj+0x5C`; frame `+0x00`, `+0x04`, piece `+0x00`..`+0x03`, piece `+0x08` |
| `0x0800FFA4` | state method: rebase the entity's position on the current frame | the `16*frame + 4*direction + 4` arithmetic plus frame `+0x05` |
| `0x0800F188`..`0x0800F3F4` | the composite builder | frame `+0x00` piece count, `+0x04` header word, pieces at `+8 + 12*i`, piece `+0x02`, `+0x03`, `+0x08` |
| `0x0800DE6C`, `0x0800DEB0` | frame advance, two loop policies | animation `+0x00`, `obj+0x12` timer, `obj+0x11` index |
| `0x08027390`, `0x080273D6`..`0x0802741A` | spawn constructor | the full cell arithmetic plus piece `+0x00`..`+0x03` |
| `0x0800A890`, `0x080159B0`, `0x08020660`, `0x0800A8DC`, `0x080159F4` | facing computers | write `obj+0x10` with the four constants |
| `0x0800F0CA`..`0x0800F17E` | OAM word construction for the tile-map path | builds attributes from `obj+0x10`, `obj+0x11`, `obj+0x8`, `obj+0x6C`, `obj+0x70`, `obj+0x68`, `obj+0x4C`; this path does **not** use a piece attribute word |
| `0x0800F1C2`, `0x0800F24C` | OAM word construction for the container path | `ldr r3,[r0,#4]` / `ldr r6,[r0,#4]` where `r0 = frame + 8 + 12*index`: **loads the piece's packed attribute pair** and merges it under the `0xFE00FFFF` mask (pool `0x0800F4B0`) |

**Bounds checks observed:** the frame advance bounds the frame index against
`animation + 0x00` (two forms, with different overflow policies: one tail-calls a
class method, the other resets the timer); the composite loop bounds itself by the
frame's `piece_count` (`0x0800F3BA`/`0x0800F3EC`, and again at `0x0800F2D8`/
`0x0800F2DC`). **No** consumer bounds `piece_count` from above - the loop trusts
it - and no consumer null-tests a piece's container pointer. On the canonical
image neither matters: every `piece_count` is 1, 2 or 4 and every pointer
resolves. **No** consumer of the cell table bounds the frame or direction index
there; the caller-side bounds are the advance and the facing functions' four
constants.

---

## 14. SECTION R: SHARING AND DEDUPLICATION

Reported in §6.3. Two points worth stating separately:

* **989 shared frame targets** are reached 2,680 times beyond their first use.
  Of those, 702 are reached from all four direction positions of one pose and 287
  from three. Sharing a frame record therefore means two direction positions
  render the same pose, which is a data fact and not a claim that two directions
  look alike on screen in every animation.
* **2,994 of 7,390 containers are reached by more than one piece**, with a
  maximum of 24 (`4,396` are reached exactly once). The accepted corpus reports
  2,986 of 7,355 reached by more than one frame; the two differ because the
  populations differ, and neither is asserted over the other.

---

## 15. UNRESOLVED QUESTIONS

1. **What the two trailing words of an animation object mean.** Recorded raw,
   with histograms. The second word's five dominant values are powers of two, and
   the frame advance reads its shift amount from a state object rather than from
   the animation, so a timing interpretation is possible but unproven.
2. **What the four bytes at piece `+0x04` mean.** They take 16 distinct values and
   their high byte correlates with bit 12 of the word formed by bytes 4..7. No
   consumer was located.
3. **Which physical facing each direction value is.** The sign convention is
   established; the screen-space orientation of the compared coordinates is not.
4. **The screen-space orientation of `obj+0x20`/`obj+0x24`**, the coordinates the
   facing computers difference.
5. **Whether any animation's trailer words select a loop mode**, and what the
   three different advance forms at `0x0800DE6C`, `0x0800DEB0` and `0x0801039C`
   correspond to behaviourally.
6. **Why 21 frames declare more than one piece** while 10,959 declare one, and
   whether the composite path is used only for the four-part animation or for a
   broader class this ticket did not enumerate. The complete population is
   reported; its purpose is not.
7. **How the accepted "7,355 unique graphics containers" figure relates to this
   ticket's 7,390 distinct container offsets.** Both are measured; the
   populations are defined differently and the reconciliation belongs to
   synthesis.
8. **Whether the two stored graphics-pointer forms are used in different
   situations** or are an artifact of how the records were authored.
9. **What `definition + 0x50`'s parallel array holds**, which LOGX-SPRITE-001
   left open and this ticket did not need.

---

## 16. HANDOFF TO LOGX-GFXSCAN-001

The boundary this ticket leaves:

* **Inside**: the frame record, its piece records, the graphics *pointer* and the
  joint resolution test (resolve, in region, decode, declared size equals stated
  extents), and the region those targets occupy.
* **Outside, explicitly**: unknown or unindexed graphics discovery; whether other
  graphics families share the container format; container taxonomy beyond
  "Webfoot packed, kind 1"; tile and pixel semantics; palettes; and any graphics
  reached by a path other than an actor piece.

Concretely useful to the later ticket:

* 7,390 container offsets are reachable by a piece and all decode; the region
  they occupy is `0x003C34D0..0x006A87A8` as file offsets, and its lower bound
  **agrees with** the first container `GRAPHICS_FORMAT.md` §9 records. There is no
  unexplained container below the accepted region: an earlier draft of this
  document claimed six such containers and that claim was an artifact of the
  refuted 16-byte piece stride.
* `webfoot.formats.webfoot_lz.unpack` decodes all 7,390 with zero failures, so the
  decoder is not the bottleneck for any discovery work.
* The reader accepts two pointer forms even though this image uses only one. A
  discovery scan should therefore accept both a `0x08xxxxxx` word and a bare file
  offset, and require a decodable container whose declared size is credible; a
  scan that accepts only one form is not wrong on this image but is not portable.

## 17. OTHER DOWNSTREAM HANDOFFS

* **`GRAPHICS_FORMAT.md` §2, §4 and §10**: two statements are refuted by this
  ticket - the 16-byte piece stride and "all 10,959 frames declare exactly one
  piece" - and one is corrected by a single offset: the OAM attribute pair is at
  piece `+0x04`, not `+0x08`, and its bit layout is right. A targeted correction
  is recommended. **This ticket does not modify the accepted document.**
* **`tools/webfoot/formats/sprite_graphics.py`**: `decode_frame` hard-codes
  `PIECE_SIZE = 16` and reads the graphics pointer at `+0x0C`; the corrections are
  the frame header size (8), the piece stride (12), the graphics offset (`+0x08`)
  and the attribute offset (`+0x04`). `Piece.horizontal_flip`/`vertical_flip`/
  `shape`/`size` are **kept**, with the attribute offset moved. `decode_animation`
  needs no change. The correction is bounded and is left to the production owner,
  since it changes a shipped reader's public shape.
* **`tools/webfoot/graphics.py`**: the `_animations_in` walk (LOGX-SPRITE-001
  §10.1) is unchanged and is not this ticket's to repair. The **known production
  bug is not allowed to corrupt any census here**: every population in this
  document was computed from `definition + 0x00` and the `+0x54` array directly,
  never through `graphics.py`.
* **LOGX-SPRITE-001**: its frame-record handoff is superseded in two places - the
  piece stride and the claim that a piece's `+0x08` is an attribute word. Its
  animation-object handoff is confirmed in full.
* **Any future authoring work**: a frame record is variable-length and a piece is
  12 bytes; a frame's pieces must be written contiguously; and the graphics word
  must resolve to a container whose declared decoded size equals the stated
  extents, or the engine's composite path will not have a size to copy.
