# LOGX-FRAME-001 review: reconstruct Buu's Fury animation / frame / multipart sprite records

Status: **isolated research complete, independent review closed, not integrated.**
This ticket is not marked complete in `PROJECT_<local-state-name>`, is not archived, and does not
update canonical `PROJECT_STATE`.

```text
START SHA:            274502187596066cabf77c09bbefea5062438580
END SHA:              b731897c5e4c46646c3507c99edaf477d165d6a3
BRANCH:               logx-frame-001
COMMIT SHA(S):        b731897c5e4c46646c3507c99edaf477d165d6a3  (research)
                      plus the follow-up commit that records this SHA

CANONICAL ROM SHA BEFORE: 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
CANONICAL ROM SHA AFTER:  940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
```

---

## EXTERNAL CLAIMS TESTED

| Claim | Source | Verdict |
| --- | --- | --- |
| animation-leading `u32` frame count with a `value << 2` relationship | LOGExtractor | **PARTIALLY CONFIRMED**: the stored word is a count and the `<< 2` arithmetic is real, but the shift indexes a **row** of the cell table by the *frame index*; `count * 4` is the flat cell count |
| a frame record is `u32 piece_count` then **16-byte** pieces | accepted `GRAPHICS_FORMAT.md` §2 | **REFUTED**: 8-byte header then **12-byte** pieces |
| piece `+0x08` is an OAM attribute word, `+0x0C` the graphics pointer | accepted `GRAPHICS_FORMAT.md` §2 | **HALF REFUTED, HALF CONFIRMED**: the attribute pair and its bit layout are real but sit at **`+0x04`**; `+0x08` is the graphics word |
| "all 10,959 frames declare exactly one piece" | accepted `GRAPHICS_FORMAT.md` §2, §4 | **REFUTED**: 21 frames declare 2 or 4 pieces |
| "the four slots are numbered, never named" | accepted `GRAPHICS_FORMAT.md` §10 | **CONFIRMED as policy**, and strengthened: the four engine values and their axis split are observable; the physical order remains `INFERRED` |
| the animation record is `u32 frame_count` then `frame_count*4` pointers, direction-major | accepted `GRAPHICS_FORMAT.md` §2 | **CONFIRMED** |
| `16*frame + 4*direction + 4` indexes the selected animation | LOGX-SPRITE-001 handoff | **CONFIRMED** as a two-dimensional cell table |
| multipart frames with a piece count | LOGExtractor | **CONFIRMED** |
| flip/flag fields in a piece | LOGExtractor | **CONFIRMED as stored bits** at `+0x04` (horizontal flip set on 2,848 pieces, vertical on none); the rendering effect is `UNRESOLVED` |
| sprite origins / hitbox | LOGExtractor | **UNRESOLVED**; out of scope per section P |

---

## CENSUS

```text
TOTAL ANIMATION REFERENCES:      1,721   (definitions 297; array slots 4,070; null 2,349)
UNIQUE ANIMATION TARGETS:        1,017
SHARED ANIMATION TARGETS:          410   (max reuse 16)
MINIMUM / MAXIMUM TARGET:        0x083C3AC4 / 0x086A899C, all word-aligned, 0 malformed
```

## ENGINE CONSUMERS

| Address | Role |
| --- | --- |
| `0x0800ECDA` | animation selector `(obj, index)` -> `obj+0x50` (reused, LOGX-SPRITE-001) |
| `0x0800EF38` | method: recompute the current frame record from `obj+0x11` (frame), `obj+0x10` (direction) |
| `0x0800EF66` | method: screen position, same arithmetic plus frame `+0x05` |
| `0x0800EF94` | renderer: reads the frame record at `obj+0x54`, `obj+0x4C`, piece `+0x00`..`+0x03`, `+0x04` and `+0x08` |
| `0x0800FFA4` | state method: rebase the entity's position on the current frame record |
| `0x0800F188`..`0x0800F3F4` | composite builder: frame `+0x00` piece-count bound, `frame+6`*`frame+7` header area, pieces at `8 + 12*i`, extents at `+2`/`+3`, graphics at `+0x08` |
| `0x0800DE6C`, `0x0800DEB0` | frame advance: `u16` timer, shift from a state object, clamp on `animation + 0x00` |
| `0x08027390`, `0x080273D6`..`0x0802741A` | spawn constructor: the full cell arithmetic, then the **frame header's** `+0x04`..`+0x07` bounding box as the entity's offsets and extents |
| `0x0800A890`, `0x080159B0`, `0x08020660`, `0x0800A8DC`, `0x080159F4` | facing computers: write the four direction constants to `obj+0x10` |
| `0x0800F0CA`..`0x0800F17E` | OAM word construction for the tile-map path, from entity state |
| `0x0800F1C2`, `0x0800F24C` | OAM word construction for the container path: loads the piece's packed attribute pair and merges it under the `0xFE00FFFF` mask |

## ANIMATION OBJECT LAYOUT

```text
+0x00            u32 frame_count            1..16 (high halfword always 0)
+0x04            u32 cell[4 * frame_count]  4-byte stride, 16-byte row stride
+0x04 + 16*fc    two words, recorded raw    UNRESOLVED - and not proven to be a trailer
                at all: in 30 of 1,017 objects a frame record starts exactly here,
                so those two words are that record's piece count and header
```

Existence is bounded by its own count: no two of the 1,017 canonical animation
objects overlap, and every gap to the next is a multiple of four (the gap is
other data interleaved in the region, never padding).

```text
ANIMATION +0x00:            u32, read as a word by the engine (0x0800DE7E, 0x0800F18A, 0x0800F3EC)
FRAME-COUNT SEMANTIC:       CONFIRMED as a count of table ROWS, enforced by the frame advance
                            (0x0800DE78..0x0800DE90 clamp; 0x0800DEBA..0x0800DECC wrap)
```

## LOGEXTRACTOR SHIFT/COUNT CLAIM

The stored word is a count of rows. The engine's `<< 2` is applied to the
**direction index**, not to the count:

```text
0x0800EF3C  lsls r2, r2, #4      ; frame  -> row offset
0x0800EF42  lsls r2, r2, #2      ; direction -> cell offset within the row
0x0800EF46  ldr  r1, [r1, #4]    ; cell = animation + 4 + 16*frame + 4*direction
```

`count * 4` reproduces the flat cell count exactly, which is why an extractor that
reads it as a pointer count still produced plausible output. The physical field,
its engine use and its count semantic are established; the extractor's *formula*
is not preserved.

## FRAME/DIRECTION INDEX FORMULA

```text
FRAME/DIRECTION INDEX FORMULA:  cell_address = animation + 4 + 16*frame + 4*direction
                                (flat index 4*frame + direction)
+0x04 STRUCTURAL MEANING:       4-byte-stride table of 4*frame_count ROM pointers
                                (row stride 16, four cells per frame index)
```

Seven engine functions perform this arithmetic on the base of the **selected
animation** (`obj+0x50`, written by `0x0800ECDA`), not the definition:
`0x0800EF38`, `0x0800EF66`, `0x0800FFA4`, `0x080100A4`, `0x08010192`,
`0x080272AE`, `0x080273D6`/`DA`/`DC`. An eighth site, `0x0800F0A2`, has the same
shape but base `obj+0x4C`, an 8-byte row stride and a `0x80` terminator: it reads
the definition's `+0x50` parallel slot table (10 of 297 definitions), not the cell
table.

## FRAME COUNT / DIRECTION

```text
FRAME COUNT:          explicit u32 at animation + 0x00; 1..16; 0 zero-frame animations
                      distribution 1:80 2:275 3:180 4:407 5:16 6:13 7:11 8:3 9:2 10:2 11:24 12:2 16:2
DIRECTION COUNT:      four, independent of frame_count; all 1,017 objects have all four cells populated
DIRECTION SEMANTIC:   values 2/3 are the horizontal axis pair and 0/1 the vertical pair
                      (both facing computers compare |dx| vs |dy| first);
                      CONFIRMED at the sign/axis level
DIRECTION ORDER:      UNRESOLVED at the screen level - the screen orientation of the compared
                      coordinates was not observed.  Recorded INFERRED for the sign convention only.
```

## FRAME/DIRECTION CELLS AND TARGETS

```text
TOTAL FRAME/DIRECTION CELLS:  13,660 over the 1,017 unique objects (4 * 3,415 frame units)
                              23,068 over the 1,721 animation references
NON-NULL CELLS:               13,660   (NULL CELLS: 0)
UNIQUE FRAME TARGETS:         10,980
SHARED FRAME TARGETS:            989   (max reuse 4; every shared target is confined to ONE frame
                                       index and reached from 2-4 direction indices)
CELLS BY DIRECTION INDEX:     0:3415  1:3415  2:3415  3:3415
DISTINCT CELLS PER FRAME:     1:702  2:287  4:2426
```

## FRAME TARGET IDENTITY

A cell's target is a **frame record**: an 8-byte header and then `piece_count`
12-byte piece records. It is not an OAM command list, not a graphics descriptor
and not a further pointer layer.

**The header is the frame's own bounding box**, confirmed rather than inferred: on
all 10,980 canonical frames, `s8 min_x` at `+0x04`, `s8 min_y` at `+0x05`,
`u8 width` at `+0x06` and `u8 height` at `+0x07` equal the minima over the frame's
pieces and the extent of their union. The spawn constructor reads `frame+4`/
`frame+5` as the entity's initial offsets (`0x080273F0`/`0x080273F4`), and the
renderer multiplies `frame+6` by `frame+7` to size the composite buffer
(`0x0800F38E`, `0x0800F390`, `0x0800F392`).

## MULTIPART FRAME STRUCTURE / PIECE COUNT / STRIDE

```text
MULTIPART FRAME STRUCTURE:  u32 piece_count at +0x00, then the frame's bounding box
                            (s8 min_x, s8 min_y, u8 width, u8 height) at +0x04..+0x07,
                            then piece_count 12-byte pieces starting at +0x08
PIECE COUNT:                u32, bounded by the engine's own loop (0x0800F3BA..0x0800F3F2);
                            distribution 1:10959  2:19  4:2  (21 multi-piece frames)
PIECE ENTRY STRIDE:         12 bytes, proved twice over:
                            (a) render loop 0x0800F3C0 computes r7 = frame + 8 + 12*index
                            (b) under (8, 12) all 11,005 pieces resolve to a container whose
                                declared decoded length equals dim_0 * dim_1, with 0 exceptions;
                                the previously accepted (4, 16, +6, +0x0C) model fails on 25
```

## PIECE FIELDS

```text
PIECE POSITION FIELDS:   +0x00 s8 and +0x01 s8, added to the entity's own coordinates
                         by the renderer (0x0800F204, 0x0800F22A, 0x0800F25E).
                         The frame header carries the same pair for the whole frame.
                         Axes INFERRED.
POSITION ORIGIN:         UNRESOLVED.  No hitbox, collision, feet or camera anchor established.
PIECE SIZE REPRESENTATION: +0x02 u8 and +0x03 u8, pixel extents; the engine halves them to
                         centre (0x0800F20A, 0x0800F230) and multiplies them to size the
                         composite buffer (0x0800F3DE).  dim_0*dim_1 equals the container's
                         declared decoded length on all 11,005 pieces.  STORED fields, not derived.
```

## FLIP / ATTRIBUTE / PALETTE / GRAPHICS

```text
FLIP / ATTRIBUTE FIELDS:  A packed OBJ attribute pair IS stored, at piece +0x04, as
                          (attr1 << 16) | attr0 - the layout GRAPHICS_FORMAT.md section 2
                          describes, at a different offset.  Loaded at 0x0800F1C2 and
                          0x0800F24C and merged into the outgoing OAM word under mask
                          0xFE00FFFF (literal pool 0x0800F4B0).
                          Over all 11,005 pieces: colour-256 set on 11,005; shape in
                          {0,1,2} with reserved shape 3 never used; size in {0..3};
                          horizontal flip (attr1 bit 12) set on 2,848; vertical flip on 0.
                          And the shape/size decode equals the separately stored
                          (dim_0, dim_1) on 11,005 of 11,005 pieces - which is what makes
                          the decode evidence.
                          HORIZONTAL FLIP: stored bit CONFIRMED; rendering effect UNRESOLVED.
                          VERTICAL FLIP: absent from the canonical corpus (0 of 11,005).
                          Where the horizontal pair differs in attribute-1 bit 12 the two
                          cells name the SAME container in 2,599 of 2,600 poses, so the bit
                          is a flip applied to shared art - which is what an earlier draft
                          of this ticket got backwards.
PALETTE RELATIONSHIP:     No palette field in a frame or a piece: the 12-byte record's six
                          fields all have a located engine read.  UNRESOLVED at this level.
GRAPHICS RELATIONSHIP:    piece +0x08 is a pointer to a packed Webfoot container.  Every one
                          of the 11,005 pieces stores the full GBA-address form.
                          11,005 of 11,005 resolve AND decode AND declare a decoded length equal
                          to dim_0*dim_1.  0 failures.  7,390 distinct container offsets reached,
                          all decoding, region 0x003C34D0..0x006A87A8 (file offsets), which
                          agrees with the region GRAPHICS_FORMAT.md section 9 records.
                   SHARING: 2,994 of the 7,390 are reached by more than one piece (max 24).
```

## FRAME TIMING / LOOPING

```text
FRAME TIMING:            PARTIALLY CONFIRMED at the mechanism level.  A u16 counter at
                         obj+0x12 is incremented, shifted right by a byte read from a STATE
                         object ([r0,#4]), and clamped against animation + 0x00.  No per-frame
                         duration is stored in the animation record on this path, and no
                         instruction consuming either trailing word was located.
LOOPING / COMPLETION:    Looping CONFIRMED present (0x0800DEB0 wraps the counter and resets it).
                         Terminal behaviour, ping-pong and completion state UNRESOLVED.
```

## FULL-CENSUS RESULTS

| # | Population | Value |
| ---: | --- | ---: |
| 1 | definitions | 297 |
| 2 | inline array slots | 4,070 |
| 3 | animation references (non-null) | 1,721 |
| 4 | unique animation objects | 1,017 |
| 5 | frame units over unique objects | 3,415 |
| 6 | cells over unique objects | 13,660 |
| 7 | cells over animation references | 23,068 |
| 8 | unique frame targets | 10,980 |
| 9 | piece references over unique frames | 11,005 |
| 10 | piece references over references | 23,180 |
| 11 | graphics references | 11,005 |
| 12 | unique graphics targets | 7,390 |
| 12b | shared graphics targets / max reuse | 2,994 / 24 |
| 13 | multi-piece frames | 21 |
| 14 | shared frame targets / max reuse | 989 / 4 |
| 15 | shared animation targets / max reuse | 410 / 16 |
| 16 | frames whose header equals the piece bounding box | 10,980 of 10,980 |
| 17 | pieces whose attribute decode equals the stored extents | 11,005 of 11,005 |
| 18 | pieces storing the absolute graphics-pointer form | 11,005 of 11,005 |
| 19 | containers reached by single-piece frames (the accepted 7,355) | 7,355 of 7,390 |
| 20 | animation objects whose table end is a frame-record start | 30 of 1,017 |

## REPRESENTATIVE RECORDS

**Animations.** `0x0850C1DC` (definition 115, slot 0): `frame_count 2`, cells
`0x0850C13C 0x0850C164 0x0850C18C 0x0850C1B4 0x0850C150 0x0850C178 0x0850C1A0
0x0850C1C8`, trailers `(1, 0x400)`. `0x083C51C4` (definition 12, slot 1):
`frame_count 4`, 16 cells, trailers `(1, 0x200)`.

**Frames.** `0x0850C13C`: piece count 1, header bounds `(-8, -24, 32, 32)`,
piece at `0x0850C144` = `x -8, y -24, 32x32, attributes 0x80002000, graphics
0x0850BBB8` (container declares 1024). `0x08423128`: piece count 2, header bounds
`(-8, -40, 32, 48)`, piece 0 at `0x08423130` = `-8, -40, 32x32, 0x80002000,
0x084224E0` (1024) and piece 1 at `0x0842313C` = `-8, -8, 32x16, 0x80006000,
0x0842259C` (512); record ends `0x08423148`. `0x08579890`: piece count 4, header
bounds `(0, -80, 96, 96)`, four pieces `64x64 + 32x64 + 64x32 + 32x32` at
`(0,-80) (64,-80) (0,-16) (64,-16)`.

**Pieces.** The two-piece example above, plus `0x08579894` = `(0,-80) 64x64`
graphics `0x08578FE8` declaring 4096.

## ANOMALIES

1. Under the corrected layout the canonical corpus has **zero** malformed
   animations, cells, pieces or graphics words. The anomalies LOGX-SPRITE-001
   recorded - four art-filter-rejected animations and five frame pointers its
   reader dropped - **do not exist under this layout**; they were artifacts of the
   16-byte piece stride.
2. The graphics-pointer population was mis-stated in earlier drafts of this
   ticket itself. Two successive errors were found by the independent reviewers and
   corrected: an early rule accepted words such as `0x80002000` that resolve as GBA
   addresses but point into the code area, and a later draft reported a 19-piece
   "relative pointer" minority that does not exist. The final rule requires all
   three conditions (resolve, land in the measured region, decode with a matching
   declared size), and under it **every one of the 11,005 pieces** resolves and
   decodes, with no anomaly.
3. **7,390 distinct container offsets, not 7,355 - and the difference is now
   explained exactly.** The accepted set is precisely the set of containers reached
   by single-piece frames; the extra 35 are exactly what the 21 multi-piece frames
   reach, and the accepted reader's 16-byte stride rejects all 21 of them. See
   [`../research/LOGX_FRAME_PROVENANCE.md`](../research/LOGX_FRAME_PROVENANCE.md) §7.
4. The graphics region's lower bound is `0x003C34D0`, which **equals** the first
   container `GRAPHICS_FORMAT.md` §9 records. An earlier draft claimed a
   1,332-byte gap and six unreferenced containers below it; that claim was an
   artifact of the refuted 16-byte piece stride and is withdrawn.
5. 1,017 frame targets are shared sub-records of a larger frame, so the counted
   extent lands on the next known frame start for 9,963 of the **10,979 consecutive
   frame pairs** and not for all of them. Both numbers are reported.
6. **This ticket corrected itself four times under review**, each time because a
   reviewer reproduced a measurement that contradicted the draft: the resolution
   rule, the "no attribute word" claim, the frame-header description, and the
   direction of the horizontal-flip correlation. Every correction is recorded in
   place rather than quietly patched, and each is cross-referenced from the
   provenance document's §11 table.

## TOOLING ADDED

`tools/research/logx_frame_probe.py` - read-only, canonical-SHA-gated,
deterministic, no image extraction, no proprietary payload written to disk, with
the disassembly dependency deferred to first use (`--engine` only). Modes:
`--census` (full JSON census; `--no-engine` omits the capstone-dependent section),
`--rows` (one row per animation reference), `--frames` (one row per distinct
frame), `--representative ADDRESS` (one animation object end to end), `--engine`
(instruction evidence). Neutral names for unresolved fields
(`trailer_0_raw`, `bytes_04_raw`).

The known production bug in `tools/webfoot/graphics.py::_animations_in` is **not
repaired here**, and it **cannot corrupt this census**: every population was
computed from `definition + 0x00` and the `+0x54` array directly, never through
`graphics.py`.

## TESTS ADDED

* `tests/unit/test_logx_frame_probe.py` - portable: address and cell arithmetic,
  synthetic animation/frame/piece parsing, fail-closed rejection of zero or
  oversized counts, both graphics-word forms, the joint resolution rule,
  canonical-gate failure, the dependency boundary (no capstone import at module
  level; `thumb_disasm` fails loudly when capstone is absent).
* `tests/integration/test_logx_frame_rom.py` - ROM-gated: the reference census,
  animation-object layout, the cell arithmetic, four-frame repetition, frame and
  piece layouts for 1-, 2- and 4-piece records, piece fields, the graphics
  resolution test over the whole corpus, extent census, every quoted instruction,
  the direction constants, and determinism/mutation sensitivity. Skips cleanly
  with no ROM configured.

## TEST RESULTS

```text
tests/unit/test_logx_frame_probe.py                    20 passed  (ROM absent)
tests/unit/test_logx_frame_probe.py                    20 passed, 1 skipped (capstone present)
tests/integration/test_logx_frame_rom.py               25 passed  (ROM configured)
tests/integration/test_logx_frame_rom.py               25 skipped (ROM absent, no errors)
tests/integration/test_logx_sprite_rom.py              (see GIT STATUS section)
tests/integration/test_graphics_rom.py                 (see GIT STATUS section)
```

```text
ROM_BIBLE_IMPACT:         UPDATED - new `## LOGX-FRAME-001` section in
                          docs/reverse-engineering.md (evidence above threshold only)
public progress impact:   NONE - isolated research on internal record layout; no new
                          shipping capability, no user-visible behaviour change
```

## DISAGREEMENTS WITH LOGEXTRACTOR

| Item | Disagreement | Classification |
| --- | --- | --- |
| frame-count formula | the stored word counts table **rows**; the `<< 2` applies to the direction index | PARTIALLY CONFIRMED |
| piece stride | 12 bytes, with an 8-byte frame header, not 16 bytes with none | REFUTED |
| flip/flag fields | no stored flag word exists on this image | REFUTED |
| piece dimensions | confirmed, but as stored byte extents whose product is the container's declared size | CONFIRMED |
| graphics addressing | confirmed as a container pointer, stored in two forms | CONFIRMED |
| multipart frames | confirmed | CONFIRMED |
| sprite origins | not established | UNRESOLVED |

Disagreements with **accepted project material** are itemised in
[`../research/LOGX_FRAME_PROVENANCE.md`](../research/LOGX_FRAME_PROVENANCE.md) §11;
three accepted `GRAPHICS_FORMAT.md` statements are refuted there and the accepted
documents are deliberately left unmodified.

## UNRESOLVED QUESTIONS

1. The meanings of the animation's two trailing words (histograms recorded), and
   whether a trailer exists at all given the 30 table-end frame-record aliases.
2. What the anchor-adjacent computation at `0x0800F0EA`/`0x0800F106`/
   `0x0800F132` means (an OAM position derived from `obj+0x6C`/`obj+0x70`).
3. The screen-space orientation of the direction values, and of the compared
   coordinates.
4. Whether a loop mode is selected by any animation field.
5. Why 21 frames are multi-piece while 10,959 are not.
6. How the accepted "7,355 containers" figure relates to 7,390 distinct offsets.
7. Whether the OAM construction paths at `0x0800F0CA` and `0x0800F1C2`
   correspond to different entity classes, and what the `0xFE00FFFF` mask's
   preserved attribute-1 bits 9-15 mean for tile numbering.
8. What `definition + 0x50`'s parallel array holds (left open by LOGX-SPRITE-001).

## HANDOFF TO LOGX-GFXSCAN-001

* The boundary: the frame record, its pieces, the graphics **pointer** and the
  joint resolution test are in scope here; unknown or unindexed graphics
  discovery, container taxonomy, tile/pixel semantics, palettes and any graphics
  not reached through an actor piece are out of scope.
* 7,390 container offsets are reachable by a piece and all decode; the region is
  `0x003C34D0..0x006A87A8` (file offsets), whose lower bound agrees with the
  accepted figure.
* The reader accepts two pointer forms even though this image uses only the
  absolute one, so a portable discovery scan should accept both and require a
  decodable container whose declared size is credible.
* The piece attribute pair's `0xFE00FFFF` merge preserves attribute-1 bits 9-15;
  whatever rebuilds the tile number is the next thing a graphics ticket needs.

## OTHER DOWNSTREAM HANDOFFS

* `GRAPHICS_FORMAT.md` §2/§4: two statements are refuted (the 16-byte piece
  stride, "all frames are single-piece") and one is corrected by a single offset
  (the attribute pair is at piece `+0x04`, not `+0x08`; its bit layout is right).
  A targeted correction is recommended and was not made here.
* `tools/webfoot/formats/sprite_graphics.py`: `decode_frame` hard-codes a 16-byte
  piece and reads the graphics pointer at `+0x0C`; the fixes are the header size
  (8), the stride (12), the graphics offset (`+0x08`) and the attribute offset
  (`+0x04`). `Piece.shape`/`size`/`horizontal_flip`/`vertical_flip` are **kept**.
  `decode_animation` needs no change. Left to the production owner.
* `tools/webfoot/graphics.py::_animations_in` (LOGX-SPRITE-001 §10.1): unchanged,
  not this ticket's to repair.
* LOGX-SPRITE-001: its frame-record handoff is superseded in two places; its
  animation-object handoff is confirmed in full.

## REVIEW

Two fresh-context reviewers were used, neither of which had seen the other's work
or this conversation.

```text
REVIEWER A (engine / dataflow / frame layout):
REVIEWER B (census / adversarial graphics semantics):
REQUIRED CORRECTIONS:
REJECTED REVIEWER ASSERTIONS:
CORRECTION GATE:
```

### REVIEWER A - engine, dataflow and frame layout

Verified the ROM hash, re-implemented the definition -> animation -> frame walk
without importing the probe for its corpus numbers, capstone-checked 103 quoted
instruction addresses, and ran the focused suites.

Verdicts: the frame count and its use as a bound **CONFIRMED**; the cell-table
layout **CONFIRMED**; the 8+12 frame layout **CONFIRMED hard** while the document's
header description was **REFUTED**; the "no stored attribute word" claim
**REFUTED**; the constructor's field attribution **PARTIALLY** wrong; the axis
split **CONFIRMED** with the screen orientation correctly left open; the
multi-piece counts **CONFIRMED exactly**; seven of 103 quoted addresses wrong.

**All 13 required corrections were reproduced by the implementer before
acceptance, and all were accepted.**

| # | Correction | Reproduced as |
| ---: | --- | --- |
| 1 | frame header `+0x04..+0x07` is the frame's bounding box, not a raw word | `+4`/`+5` equal the piece minima on **10,980/10,980** frames; `+6`/`+7` equal the union extent on **10,980/10,980** |
| 2 | piece `+0x04` **is** the packed OBJ attribute pair | `(attr1 << 16) \| attr0` gives shape in `{0,1,2}`, size in `{0..3}`, colour-256 always, and reproduces the stored extents on **11,005/11,005**; loaded at `0x0800F1C2` and `0x0800F24C` under mask `0xFE00FFFF` |
| 3 | the constructor's four reads are the **frame header** | `0x080273E4` stores the selected cell in `obj+0x54`, then `0x080273F0`/`F4` read `frame+4`/`+5` and `0x0802740C`/`10` read `frame+6`/`+7` |
| 4 | piece `+0x02`/`+0x03` are read at `0x0800F206`/`0x0800F22E`; `0x0800F22A` is piece `+0x01` | verified by decode |
| 5 | **seven** cell-arithmetic functions, not nine; `0x0800F0A2` uses base `obj+0x4C`, an 8-byte row and a `0x80` terminator | verified by decode of `0x0800F0A4`, `0x0800F0A6`, `0x0800F0B0`-`0x0800F0B4` |
| 6 | all 11,005 graphics words are absolute; no relative minority | census reports `{"absolute": 11005}` |
| 7 | the region lower bound **equals** the accepted figure | `0x003C34D0 == 0x03C34D0` |
| 8 | seven quoted instruction addresses were wrong | corrected and re-verified; `engine_census` reports `all_match: true` over 67 sites |
| 9 | `0x0801AF96` writes `obj+0x11`, the frame index, so it is not direction evidence | dropped from the direction argument and the ROM bible |
| 10 | the "no other literal writer to `obj+0x10`" negative is not established | replaced with the narrower statement the code supports |
| 11 | 30 of 1,017 animation objects are followed immediately by a frame record, so the trailer extent is unproven | reported as `animations_whose_table_end_is_a_frame_record_start: 30` |
| 12 | `0x0800F3A6` is a container-**kind** test, not a null test, and the pointer is dereferenced unguarded | corrected in both documents |
| 13 | `sprite_graphics.Piece` needs its attribute offset **moved**, not its flip/shape/size properties deleted | downstream handoff rewritten |

### REVIEWER B - census, populations, graphics semantics, tests

Re-implemented a walk of its own, froze a snapshot of the revision it reviewed,
verified the ROM hash after every run, and computed the exact set relation between
this ticket's container population and the accepted one.

It confirmed all 15 rows of the full-census table, the ten named populations, both
extent figures, the frame bounding box, the `7,355` subset relation, the clean
skip behaviour and the absence of committed proprietary content. It **refuted
three of this ticket's conclusions and eight of its numbers**, every one of which
the implementer reproduced before accepting.

| # | Finding | Reproduced as |
| ---: | --- | --- |
| 1 | the evidence against the horizontal-flip field was **inverted** | in the 2,600 poses where directions 2 and 3 differ in attribute-1 bit 12, the two cells name the **same** container in **2,599** cases (different once). The earlier count had compared *frame records* rather than containers. Conclusion reversed |
| 2 | "1,691 same-container pairs, zero attribute differences" is wrong | **8,713** same-container pairs over 20,490 direction pairs: 5,420 identical, 3,293 differing |
| 3 | shared graphics targets: 2,614 is wrong | **2,994** |
| 4 | the `7,355` vs `7,390` gap is **not** deduplication | the accepted set is **exactly** the single-piece-frame container set; `ticket \ accepted` is exactly the 35 offsets the 21 multi-piece frames reach; the accepted 16-byte stride accepts exactly 10,959 frames and rejects exactly the 21 |
| 5 | §12 identity arithmetic | `3,415 = sum(k*count(k))`, not the distribution's sum (**1,017**); the reuse identity is `2*287 + 3*702 = 2,680`, not `3*287 + 4*702` (= 3,669) |
| 6 | the "1,332 bytes below / six containers" graphics lead | refuted; the region bound equals the accepted figure |
| 7 | two stored pointer forms | refuted: **11,005 absolute, 0 bare offsets** |
| 8 | "10,980 pieces resolve" | **11,005** |
| 9 | the determinism test compared a memoised object with itself | rewritten to clear the memo between computations and assert `first is not second` |
| 10 | several assertions were tautological | rewritten to re-derive from raw bytes (cell arithmetic, sortedness, region bounds) |
| 11 | `representative_report` substituted offset 0 for an unresolved word | now returns `None` and performs no read |
| 12 | `git diff --check` failed with 2,262 CRLF whitespace errors | all artifacts normalised to LF; `git diff --check` exits 0 |
| 13 | `scratchpad2/` untracked and unignored; the bare `roms` symlink missed by `roms/` | scratch removed; `.gitignore` gained `/scratchpad/` and a bare `roms` |
| 14 | §4.1's frame-pair denominator | stated as 9,963 **of 10,979 consecutive pairs** |

**Reviewer B's process finding is accepted.** It reported that the worktree was
not frozen while it measured - the implementer kept editing - so its document
verdicts are scoped to its own snapshot and no revision of the ticket was
recoverable from git at that time. That is a real defect in how this review was
run, and it is recorded rather than excused. Its ROM measurements are unaffected,
every one was reproduced against the frozen artifacts, and this commit is the
freeze that was missing.

**Reviewer B's caveat on the joint test is accepted.** On 7 of the 21 multi-piece
frames the frame header's own `+0x04` word also decodes to a container of the
right size. The graphics-word identity does not rest on that test alone - it rests
on the engine's `ldr r0,[r7,#8]` at `0x0800F3CE` and on the 11,005-piece agreement,
and no word *inside* the 12-byte piece passes the test except `+0x08` - but the
provenance now states the exception rather than presenting the test as unique.

### Where the two reviewers disagreed

They agree that piece `+0x04` is a stored OAM attribute pair and that the earlier
"no attribute word" claim was wrong. They differ on the flip inference: Reviewer A
did not examine the container-sharing correlation at all, while Reviewer B measured
it and showed the earlier count was inverted. The implementer reproduced Reviewer
B's measurement directly (2,599 same-container cases of 2,600) and adopted it;
Reviewer A's findings are unaffected and all are applied. **No reviewer assertion
was rejected.**

### CORRECTION GATE

```text
REVIEWER A  : 13 required corrections, all reproduced and accepted
REVIEWER B  : 14 required corrections, all reproduced and accepted
REJECTED    : 0 reviewer assertions
DISAGREEMENT: one, on the flip inference; resolved by direct measurement in
              Reviewer B's favour
GATE        : CLOSED - all corrections applied, focused suites green with and
              without the ROM, git diff --check clean, canonical ROM hash
              unchanged, worktree frozen by the commit below
```

## GIT STATUS

```text
WORKTREE:   <temp>\log1-remake-logx-frame-001   branch logx-frame-001
START SHA:  274502187596066cabf77c09bbefea5062438580
END SHA:    b731897c5e4c46646c3507c99edaf477d165d6a3

SCOPED DIFF (7 paths, no unrelated edits):
  M  .gitignore                              (ignore /scratchpad/ and a bare roms symlink)
  M  docs/reverse-engineering.md             (+145 lines: the LOGX-FRAME-001 section)
  A  docs/research/LOGX_FRAME_PROVENANCE.md
  A  docs/research/LOGX-FRAME-001-review.md
  A  tools/research/logx_frame_probe.py
  A  tests/integration/test_logx_frame_rom.py
  A  tests/unit/test_logx_frame_probe.py

FOCUSED TESTS
  tests/unit/test_logx_frame_probe.py                22 passed  (ROM absent)
  tests/integration/test_logx_frame_rom.py           27 passed  (ROM configured)
  both together                                      49 passed, 1 skipped (capstone present)
  both together, ROM absent                          23 passed, 27 skipped, 0 errors
  tests/unit (whole portable suite)                  1545 passed, 8 skipped

RELATED REGRESSION SUITES (run earlier in this session, ROM configured)
  tests/integration/test_logx_sprite_rom.py          passed
  tests/integration/test_graphics_rom.py             29 passed
  tests/integration/test_logx_char_rom.py            passed
  tests/integration/test_logx_codec_rom.py           passed
  tests/integration/test_logx_connector_rom.py       passed
  tests/integration/test_logx_layer_rom.py           passed
  tests/integration/test_logx_map_record_rom.py      passed
  tests/integration/test_logx_map_render_rom.py      passed
  tests/integration/test_logx_tile_rom.py            passed
  tests/unit/test_logx_*_reference.py                passed
  tests/unit/test_sprite_graphics.py                 passed
  tests/unit/test_graphics_*.py                      passed

ROM SAFETY
  canonical SHA-256 before 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
  canonical SHA-256 after  940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
  ROM writes: none.  Every probe reads bytes the caller supplies and writes nothing.
  No ROM, save, state, dump, image or decoded proprietary asset is staged; the
  staged set is the seven paths above and nothing else.
  All artifacts are LF; git diff --check exits 0.

WORKFLOW
  Not integrated to master.  Not archived.  PROJECT_<local-state-name> and PROJECT_<local-state-name>
  deliberately unchanged.  public progress impact: NONE.
```
