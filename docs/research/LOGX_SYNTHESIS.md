# LOGX synthesis: canonical LOGExtractor knowledge, read support and authoring readiness

**Ticket:** LOGX-SYNTHESIS-001 - the final ticket of the LOGExtractor-derived
research queue. **Documentation and audit only.** No GUI, no Workbench, no
authoring surface and no production parser was changed by this ticket.

```text
START SHA:                 64fa98626065cf49c631878c53e1c8e1073a3bd6
BRANCH:                    logx-synthesis-001
CANONICAL ROM SHA-256:     940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
                           (unchanged before and after; never written)
```

Tickets synthesized: **10 / 10**

| # | Ticket | Subject | Deep evidence |
| --- | --- | --- | --- |
| 1 | LOGX-MAP-RECORD-001 | MapEntry table and selector source | [provenance](LOGX_MAP_RECORD_PROVENANCE.md) / [review](../tickets/LOGX-MAP-RECORD-001-review.md) |
| 2 | LOGX-MAP-RENDER-001 | selector-1 root / map load template | [provenance](LOGX_MAP_RENDER_PROVENANCE.md) / [review](../tickets/LOGX-MAP-RENDER-001-review.md) |
| 3 | LOGX-LAYER-001 | layer record structure | [provenance](LOGX_LAYER_PROVENANCE.md) / [review](../tickets/LOGX-LAYER-001-review.md) |
| 4 | LOGX-TILE-001 | chunk payloads, tile entries, selector streams | [provenance](LOGX_TILE_PROVENANCE.md) / [review](../tickets/LOGX-TILE-001-review.md) |
| 5 | LOGX-CONNECTOR-001 | `root +0x40`/`+0x44` transition records | [provenance](LOGX_CONNECTOR_PROVENANCE.md) / [review](../tickets/LOGX-CONNECTOR-001-review.md) |
| 6 | LOGX-CODEC-001 | Webfoot container wrapper and packed stream | [provenance](LOGX_CODEC_PROVENANCE.md) / [review](../tickets/LOGX-CODEC-001-review.md) |
| 7 | LOGX-CHAR-001 | appearance-definition records | [provenance](LOGX_CHAR_PROVENANCE.md) / [review](../tickets/LOGX-CHAR-001-review.md) |
| 8 | LOGX-SPRITE-001 | sprite-definition objects and animation arrays | [provenance](LOGX_SPRITE_PROVENANCE.md) / [review](../tickets/LOGX-SPRITE-001-review.md) |
| 9 | LOGX-FRAME-001 | animation, frame and multipart-piece records | [provenance](LOGX_FRAME_PROVENANCE.md) / [review](../tickets/LOGX-FRAME-001-review.md) |
| 10 | LOGX-GFXSCAN-001 | external scanner measured as a recall instrument | [provenance](LOGX_GFXSCAN_PROVENANCE.md) / [review](../tickets/LOGX-GFXSCAN-001-review.md) |

---

## 1. Purpose and evidence policy

The queue answered a set of questions about the Webfoot Buu's Fury engine that
an external tool, `mainant/LOGExtractor`, had answered before us - sometimes
correctly, sometimes from a plausible but wrong physical model. This document is
the single canonical synthesis of those ten answers. It exists to establish a
**trustworthy development baseline**, not to make every table look complete.

**Evidence vocabulary** (project-wide, unchanged by this ticket):

| Label | Meaning |
| --- | --- |
| `CONFIRMED` | directly established by adequate evidence, usually an engine instruction or a whole-corpus measurement |
| `PARTIALLY CONFIRMED` | a physical fact is established but its semantic interpretation is not |
| `REFUTED` | an earlier claim, usually LOGExtractor's, is contradicted by the engine |
| `UNRESOLVED` | not established. This is a **result**, not a failure |

**Readiness vocabulary** (separate, and never interchangeable with evidence):

| Label | Meaning |
| --- | --- |
| `READ-READY` | the structure and its fields are sufficiently understood to read correctly |
| `EDIT-READY` | an in-place edit of an existing record is understood, bounded and safe |
| `WRITE-READY` | new bytes can be produced: allocation, encoding, relocation and count updates all exist |
| `AUTHOR_NEW-READY` | new resources of this class can be created from nothing |
| `NEEDS ENGINEERING` | the format is understood; the tooling does not exist yet |
| `NEEDS RESEARCH` | a semantic unknown stands in the way |
| `BLOCKED` | both, or a dependency is unresolved |

> **A structure can be `CONFIRMED` and still not `WRITE-READY`**, because
> writing additionally requires allocation, bounds, relocation, count updates,
> encoding and runtime invariants. Every readiness claim below is about the whole
> writing problem, not about the reading schema.

**Policy for unknowns.** This synthesis is allowed to say `UNRESOLVED`,
`PARTIAL` and `NOT YET SAFE TO AUTHOR`. Where the queue left a semantic open, it
stays open here. No table below is completed by inference.

---

## 2. Canonical resource graph

`CONFIRMED` links are solid; `PARTIAL`/`UNRESOLVED` links are marked inline.
Every address is the engine's own literal or the value the engine reads; where a
distinction matters, the GBA address and the file offset are both given.

### 2.1 Map side

```text
MapEntry table  0x0808E2E0 (file 0x0008E2E0), 452 records, stride 0x38, no terminator
  |
  |  +0x00  TWO ORDERED KEY BYTES  (physically two bytes; big-endian is a display)
  |  +0x0C  u32, low half resolves through the verified text pointer table 0x0806BCE8
  |  +0x2C  u32, indexed-word source; selector route = 0x080089CC = word[selector-1]
  v
selector-1 root  ("map load template", 452/452 non-null, 421 distinct, 0x0817B1B0..0x082B8C38)
  |      consumed by 0x0800953E (load flow 0x08008BD0 / 0x08009078) - CONFIRMED
  |      reads it back at 0x0800938C, programs BG0CNT..BG3CNT, palette, DISPCNT
  |
  +--> +0x08 / +0x0A : ldrh, map extent in pixels, stored as extent-1; camera max extent-1+239/+159
  |                    units (pixel vs tile) UNRESOLVED
  +--> +0x0C / +0x10 : count / pointer, exactly null-coupled  (UNRESOLVED consumer detail:
  |                    the instruction that reads the pair out of the root was not recovered)
  +--> +0x14,+0x18,+0x1C,+0x20 : four layer-record pointers, ALL NON-NULL on all 452 roots
  +--> +0x24 / +0x28 : count / pointer, null-coupled, 0x18-byte element stride at 0x08009420
  +--> +0x34 / +0x38 : two containers decompressed into 0x2000-byte buffers
  +--> +0x3C         : word, 0 on 451 roots and 1 on map 19 - selects the BGxCNT table row
  +--> +0x40 / +0x44 : count / pointer to the transition-record array  (see 2.2)
  +--> +0x48         : container -> delta-coded u16 selector stream
  +--> +0x4C         : the single word 0x08179764 on all 452 roots -> 187-entry bank table
```

**Layer record** (1464 unique over 1808 references):

```text
layer record
  +0x00  4  ODD, non-4-byte-aligned word = a valid Thumb code entry / handler
  |         five values: 0x08008087 [1516 refs], 0x0800897B [41],
  |                      0x08007A41 [249], 0x08007B63 [1], 0x080088BD [1]
  |         NOT a numeric type tag. It is NOT the word the constructor writes into
  |         its runtime object, which is an even data pointer (0x08049410 family).
  +0x04  4  scalar -> object+0x3C            meaning UNKNOWN
  +0x08  4  scalar -> object+0x40            meaning UNKNOWN
  +0x0C  4  word   -> object+0x44            signedness/units/X-Y pairing UNRESOLVED
  +0x10  4  word   -> object+0x48            as above
  +0x14  1  unsigned chunk-grid X count      CONFIRMED
  +0x15  1  unsigned chunk-grid Y count      CONFIRMED
  +0x16  2  signed halfword -> object+0x0C   consumer of the object field UNRESOLVED
  +0x18  4*N  chunk-pointer window, N = +0x14 * +0x15   (4-byte elements)
  |
  v
Webfoot container, kind 1, declaring 0x800 bytes -> 2048 decoded bytes
  -> 1024 little-endian u16 entries, 32 columns x 32 rows, 64 bytes per row
     bits 0..9  tile ordinal                       CONFIRMED
     bit 10     H flip (platform-derived)          PARTIALLY CONFIRMED
     bit 11     V flip (platform-derived)          PARTIALLY CONFIRMED
     bits 12..15  zero in all 3,834,880 entries    RESERVED / CONSTANT IN CANONICAL DATA
```

**Selector stream and bank lookup:**

```text
root +0x48  container -> u16 array, prefix-decoded in place at 0x08009C02..0x08009C12
            abs[0] = raw[0]
            abs[i] = (raw[i] + abs[i-1] + 1) & 0xFFFF        CONFIRMED
  -> each absolute value is a PACKED PAIR, not a flat tile id:
       value >> 8   -> index into the bank array at root +0x4C
       value & 0xFF -> one 64-byte tile inside that bank's 0x4000-byte decoded payload
root +0x4C  = 0x08179764 on all 452 roots
  -> 187-entry array of kind-1 containers: 186 declare 0x4000, entry 186 declares 0x3C40
     largest bank index used by any canonical stream = 186 (the last entry)
```

**Two reference counts that look contradictory and are not.** LOGX-TILE-001
reports **4,118 non-null array-element references** over the dominant handler and
LOGX-CODEC-001 reports **3,912 dominant-chunk container references**. These are
different units on the same population:

```text
4,274 grid cells = 156 null + 4,118 non-null          (LOGX-TILE-001)
3,745 distinct payloads from 4,118 references         (LOGX-TILE-001)
4,520 = 3,912 + 421 + 187                             (LOGX-CODEC-001)
```

**Both are the same unit - non-null array-element (container) references - over
different populations, and neither ticket states which population it used.**
Re-traversing the same array gives **4,118 over the 452 MapEntries** and
**3,920 over the 421 distinct selector-1 roots**: the population difference
explains **198** of the 206 gap, and the remaining **8 is unexplained in both
tickets**. This synthesis therefore reports the discrepancy rather than
harmonising it, and any tool that needs a dominant-chunk reference count must
state which population it measured. **The 3,745 distinct-payload figure is the
one both tickets agree on.**

**Applicability boundary.** The chunk/tile model is established **only** for
handler `0x08008087`. On `0x08007A41` both dimension bytes are zero (the shared
absent-layer placeholder `0x080707FC`, referenced 249 times); on `0x08007B63`
and `0x080088BD` the bytes cannot be a chunk grid; `0x0800897B` fails the
dominant reading on 29 of its 41 records. **No dominant-form decoding is applied
to those records.**

### 2.2 Connection side

```text
map root
  +0x40  count  in 1..14   (0 on 104 roots)
  +0x44  pointer           (null exactly when the count is null, 452/452)
  |      read together by ONE ldm r1,{r1,r2} at 0x08009676 - no constant-offset
  |      load of either word exists anywhere
  v
array of count 4-byte ROM pointers  -> 24-byte transition records (0x18 block stride)
  |
  |  +0x00  4  class/constructor function pointer, CALLED via 0x08046AA2
  |            two values: 0x08007675 (566) / 0x080072CD (169) - class meaning UNRESOLVED
  |  +0x04  4  one value on all 735: 0x0800776D - meaning UNRESOLVED
  |  +0x08  2  u16   \  four little-endian u16 forming TWO ORDERED INTERVALS
  |  +0x0A  2  u16    |  A<=C and B<=D on 735/735, no zero area
  |  +0x0C  2  u16    |  axis names / units / origin / signedness / edge
  |  +0x0E  2  u16   /   inclusivity all UNRESOLVED
  |  +0x10  1  small selector byte, 0..3 on 725 records, 10 outliers - semantics UNRESOLVED
  |  +0x11  1  destination key HIGH byte
  |  +0x12  1  destination key LOW byte
  |  +0x13  1  further engine-read byte, census {0:561, 1:174} - semantics UNRESOLVED
  |  +0x14  2  read by the object the record feeds - semantics UNRESOLVED
  |  +0x16  1  \ bytes read by that object's constructor - semantics UNRESOLVED
  |  +0x17  1  /
  v
destination MapEntry key lookup  at 0x080089FC (linear scan of the 0x38-stride table)
  -> resolves on 735/735 records; 350 distinct destination keys
  -> 694 directed links, 674 reciprocal, 20 one-way, 3 self-links (maps 125/126/127)

CONFIRMED: the destination is TWO INDEPENDENT BYTES, not a big-endian u16.
           Four separate engine places handle it byte-wise.
UNRESOLVED: LOGExtractor's viewer-side "X += 8". No engine counterpart was found on
            the recovered path (whose own arithmetic is -112 / -76), and it is not
            needed to resolve a destination. It is neither confirmed as record
            semantics nor refuted as a pure viewer artifact.
UNRESOLVED: spawn position, facing/direction, script/event relationship.
```

### 2.3 Character / appearance side

```text
appearance-definition table  0x0874D380 (file 0x74D380)
  232 records, stride 0x10, fixed count (cmp rN,#0xE8, pre-increment -> exclusive)
  8 literal load sites; 8 sites apply the index<<4 scale
  |
  |  +0x00  u16  text index  -> 0x0806BCE8 pointer table (x4 scale)   CONFIRMED relationship
  |  |             higher-level "name" semantics            PARTIALLY CONFIRMED
  |  +0x02  u16  text index  -> the same table                        CONFIRMED relationship
  |  |             NOT "skipped": three engine functions read it (REFUTES LOGExtractor)
  |  |             "description" semantics                  PARTIALLY CONFIRMED
  |  |             +0x02 == +0x00 + 1 on 232/232 - a DATA INVARIANT, not an engine rule
  |  +0x04  u32  index -> accessor 0x08000158 -> sprite-definition pointer run
  |  +0x08  u32  index -> accessor 0x08011F20 -> pointer array 0x086F393C
  |  |             consumed as a Webfoot container at 0x080250D6
  |  |             "portrait graphics"                      PARTIALLY CONFIRMED
  |  +0x0C  i32  SIGNED index into 0x08711274 at 0x1C stride (TOOLKIT-009 family)
  |               negative values are SKIPPED by the engine (blt, no address formed)
  |               target record meaning                     UNRESOLVED
  v
named appearance definitions with optional slot and stat indices
  - NOT "the global character table": the labels span machinery, body parts,
    generic enemies and a "Human" catch-all; completeness is not established;
    98 records have no slot (+0x08 == 0) and 88 have no stat record (+0x0C < 0)
```

### 2.4 Sprite side

```text
appearance +0x04
  -> accessor 0x08000158:  for id >= 10,  u32 at 0x086B6BDC + 4*id - 0x28
                           arithmetic base 0x086B6BB4 (a COMPILER FOLD, not a run start)
                           ids 0..9 take a party-slot branch and never read the array
  v
sprite-definition pointer run  0x086B6BDC, 297 entries, strictly ascending,
  logical ids 10..306 (index = id - 10), terminated by non-ROM 0x03001068 at 0x086B7080
  |
  v
sprite definition object (VARIABLE LENGTH)
  +0x00  u16   low byte = inline animation-array element COUNT; high byte 0 on all 297
  |            five engine sites ldrb it, compare against the requested index,
  |            load +0x54 + 4*index, then null-test the element
  +0x02  u16   byte size handed to allocator 0x0803D5B8 (block-pool reading INFERRED)
  +0x04  u32   pointer to the 256 bytes immediately before the object, in exactly
  |            65 objects (+0x04 == address - 0x100); palette-remap reading INFERRED
  +0x08  4x u8 byte 0 added to a screen x; bytes 2/3 select a resource - UNRESOLVED
  +0x0C  u32   no consumer found                                  UNRESOLVED
  +0x10..+0x4F four 16-byte records of four s32; no consumer found UNRESOLVED
  +0x50  u32   parallel per-animation pointer array, present in 10 of 297 objects
  |            entry meaning                                      UNRESOLVED
  +0x54  u32[count]  INLINE, COUNT-BOUNDED, VARIABLE-LENGTH, SPARSE
                     array of animation-record pointers
                     extent = 0x54 + 4*count
  |
  v
animation object  (u32 frame_count at +0x00, values 1..16)
  +0x04  4 * frame_count 32-bit ROM pointers
         cell(frame, direction) = animation + 0x04 + 16*frame + 4*direction
         four direction cells per frame index, independent of frame_count
         SELECTED BY obj+0x50 (the animation), not by the definition
         direction ORDER on screen  UNRESOLVED (only the sign/axis split is CONFIRMED)
  |
  v
frame record  (8-byte header)
  +0x00  u32  piece_count
  +0x04  s8   min_x   \  the rendered frame's own bounding box; equals the piece
  +0x05  s8   min_y    | minima and the extent of their union on 10,980/10,980 frames
  +0x06  u8   width    | NOT a collision, hitbox, feet or origin box
  +0x07  u8   height  /
  +0x08  piece[piece_count], stride 0x0C
  |
  v
piece (12 bytes)
  +0x00  s8   x offset, added to the entity's own coordinate   axes INFERRED
  +0x01  s8   y offset                                          origin UNRESOLVED
  +0x02  u8   pixel extent dim_0 (engine halves it to centre an OBJ)
  +0x03  u8   pixel extent dim_1 (engine multiplies the pair to size the composite)
  +0x04  u32  PACKED GBA OBJ ATTRIBUTE PAIR (attr1 << 16) | attr0
  |            merged into the outgoing OAM word under mask 0xFE00FFFF
  |            colour-256 on all 11,005; shape in {0,1,2}; size in {0..3};
  |            H flip set on 2,848 (STORED bit; rendering effect UNRESOLVED);
  |            V flip on 0 of 11,005; the shape/size decode reproduces the stored
  |            extents on 11,005/11,005 - which is what makes it an attribute pair
  +0x08  u32  graphics-container pointer; the ONLY word in the record whose target
              container declares a decoded length equal to dim_0 * dim_1
  |
  v
graphics container (see 2.5)
```

### 2.5 Codec side

```text
Webfoot wrapper
  +0x00  u32 LE  dispatch word: 0 = stored/raw, 1 = packed, 2 = packed
                 any other value -> the dispatcher returns with the destination
                 UNTOUCHED.  The value is used arithmetically, not merely compared.
  +0x04  u32 LE  DECLARED DECODED BYTE COUNT, excluding the 8-byte wrapper.
                 Zero is legal and the engine installs one.
  +0x08  ...     payload: stored bytes, or the packed bitstream
  |
  v
dispatcher 0x0803D940   (Thumb; first instruction `adds r2, r0, #0` DISCARDS any
                         incoming third argument - it takes exactly (source, dest)
                         and therefore receives NO destination capacity)
   form 0 -> rom ARM memcpy 0x08046D18, exactly container[+0x04] bytes
   form 1 -> packed decoder via the Thumb->ARM veneer 0x08049120
   form 2 -> the SAME packed decoder
   other  -> return, destination untouched
  |
  v
packed decoder, ROM 0x087B79E4 = IWRAM 0x03000040 (blob copied by startup DMA3,
  4,100 bytes from ROM 0x087B79A4 to IWRAM 0x03000000 - CONFIRMED from the
  startup literals, not inferred from a library table)
  grammar: JCALG1-like / derived.  Name NOT promoted; byte-compatibility with a
  pinned JCALG1 reference was never established.
  MSB-first bits over little-endian u32 words.
  prefix 1     = literal
  prefix 0 1   = long match: distance-code gamma, low distance bits, count gamma,
                 with the length bias ladder (>=0x10000 +3, >=0x037FF +2,
                 >=0x0027F +1, <=0x0007F +4)
  prefix 0 0 0 = seven-bit field (non-zero = short match; 0 + a second 0 = end marker)
  prefix 0 0 1 = four-bit code (1 = write base, 2..15 = one-byte copy, 0 = the
                 literal-width/base escape)
  BIT 2 CLEAR is the seven-bit form and BIT 2 SET is the four-bit form; all 4,322
  canonical streams open on `0 0 1`. Inverting this desynchronises the corpus.
  |
  v
decoded resource.  On 4,322/4,322 reachable packed containers the decode produces
  exactly the declared size AND the stream's own end marker falls at that same
  length.  That is a CANONICAL OBSERVATION, not a format guarantee: the engine
  carries no output counter and performs no size comparison.
```

**Refuted container claims (do not reintroduce):**

| Claim | Disposition |
| --- | --- |
| `UnknownHeader` is a canonical engine wrapper | **REFUTED.** The dispatcher knows only `{0,1,2}`; no engine path skips four bytes and then decodes. Four-byte prefixes belong to engine *records*. As an external heuristic it decodes, but over bytes that are not the stream the wrapper names |
| a ~64 KiB engine or format limit | **REFUTED.** No instruction compares against 65,536; the largest declared size in the reachable corpus is `0x4000`. The project decoder's own `DEFAULT_MAX_OUTPUT` is an unrelated host safety constant |
| a zero first wrapper word means "empty" | **REFUTED as a general rule.** It selects the stored branch. The copy is empty only because the declared size is itself zero |
| the packed decoder receives a destination capacity | **Absent.** Confirmed by instruction reading: it takes `(source, destination)` only |
| `declared % 4 == 0` is a container test | **REFUTED.** It rejects 199 genuine selector streams declaring `4k + 2` bytes. It must not appear in project tooling |
| a successful decode establishes graphics identity | **REFUTED as a discipline.** A matching first word, a plausible declared size and a successful decode together are not evidence of graphics |

---

## 3. Map and world structures

### 3.1 MapEntry - canonical schema

Owner: LOGX-MAP-RECORD-001. Registry: LOGX-MAP-RENDER-001.

| Offset | Width | Physical type | Engine use | Semantic status |
| --- | --- | --- | --- | --- |
| `+0x00` | 2 | **two ordered key bytes** (physically two bytes) | the engine's own lookup at `0x080089FC` compares the two bytes with two `ldrb` and a byte `cmp` | `CONFIRMED` as a lookup key; **"map id" not promoted**. Big-endian is a correct *display* of the pair, not the physical type |
| `+0x0C` | 4 | `u32` LE, high half zero across the corpus | low half resolves through the verified text pointer table `0x0806BCE8` (x4 scale) | `PARTIALLY CONFIRMED`: the text relationship is `CONFIRMED`; the field's *purpose* is `UNRESOLVED` and "map name" is not promoted |
| `+0x2C` | 4 | aligned in-ROM `u32`, unique per record | indexed-word source: the selector route `0x080089CC` computes `source + 4*(selector-1)`, so selector `1` reads `source + 0x00` | `CONFIRMED` as an indexed-word source; general destination typing `UNRESOLVED` |

Table: `0x0808E2E0` / file `0x0008E2E0`, **452 fixed records**, stride **`0x38`**,
no terminator and no sentinel iteration rule. Range `[0x08E2E0, 0x0945C0)`.
The bytes immediately before and after the table are other structures, not
padding; the table is bounded by the engine's fixed count, not by inspection.

> **Superseded label.** The ROM Bible's `Physical record layout` table still
> carries the DragonByteZ names `output_raw`, `zone_raw`, `area_raw`,
> `variation_raw`, the five upstream "count" labels and the nine
> `*_pointer_raw` words. Those are **upstream labels**, explicitly marked
> `INFERRED`/`UNKNOWN` in the same table, and the ROM-003 census contradicts the
> simple count/pointer pairing model. They are retained as labelled upstream
> hypotheses, not as canonical semantics; this synthesis adds no field meaning to
> them. Discovery for the accepted graph goes through `+0x00`, `+0x0C` and
> `+0x2C` only.

### 3.2 selector-1 root - the map-load template

Owner: LOGX-MAP-RENDER-001. **The root is a load-time per-map definition
template, not merely renderer state.** `0x0800953E` is its consumer: it copies
the root's scalar fields into the RAM map-state structure and hands the pointer
fields to the graphics, layer and object loaders. `0x0800938C` reads the root
back out of map state `+0x8C` and programs `BG0CNT..BG3CNT`, the palette and
`DISPCNT`, indexing an engine table with `root+0x3C`.

| Field | Width | Physical type | Engine use | Semantic status |
| --- | --- | --- | --- | --- |
| `+0x00` | 2 | halfword, loaded whole at `0x08009630` | scalar | `UNRESOLVED` |
| `+0x02`, `+0x03` | 1 each | bytes | scalars | `UNRESOLVED` |
| `+0x04`..`+0x07` | 1 each | four bytes | added to `BG0CNT`..`BG3CNT` | `CONFIRMED` as the arithmetic; per-slot assignment `PARTIALLY CONFIRMED` |
| `+0x08` | 2 | `ldrh` at `0x0800958A` | horizontal map extent, stored as `extent - 1`; camera max `extent - 1 + 239` | `CONFIRMED` as pixels-minus-one; the pixel-vs-tile *unit name* is not promoted |
| `+0x0A` | 2 | `ldrh` at `0x08009592` | vertical extent, same `-1` bias, `+159` | as above |
| `+0x0C` / `+0x10` | 4 / 4 | count / aligned in-ROM pointer | one of three exactly null-coupled pairs | **`UNRESOLVED` consumer detail**: the record loader `0x08009B12` and the VRAM target are established, but the instruction that reads the pair out of the root was not recovered. "Animated tiles" is `PARTIALLY CONFIRMED` |
| `+0x14`, `+0x18`, `+0x1C`, `+0x20` | 4 each | four aligned in-ROM layer-record pointers | **all non-null on all 452 roots**; 0 null slots over 1808 references | four-layer reading `CONFIRMED`; BG slot order `PARTIALLY CONFIRMED` |
| `+0x24` / `+0x28` | 4 / 4 | count / null-coupled pointer | walked at a **`0x18`-byte** element stride by `0x08009420` | object types `UNRESOLVED` |
| `+0x34` / `+0x38` | 4 / 4 | pointers | containers decompressed into `0x2000`-byte buffers | bounded as outside the tile-index space; otherwise `UNRESOLVED` |
| `+0x3C` | 4 | word | selects the `0x080716D8` BG-control record: index 0 on **451** roots, index 1 on **map 19 only** | `CONFIRMED` |
| `+0x40` / `+0x44` | 4 / 4 | count / null-coupled pointer | read together by one `ldm`; consumed on the selector-1 map-load route | `CONFIRMED` (see §4) |
| `+0x48` | 4 | aligned in-ROM pointer | container whose payload is a delta-coded `u16` selector stream | `CONFIRMED` |
| `+0x4C` | 4 | `u32` | the single word `0x08179764` on all 452 roots; engine-global, not per-map | `CONFIRMED` as the value; it is the bank-container table's address, not an independent global structure |
| `+0x30`, `+0x50`..`+0x5C` | | | | `UNRESOLVED`; `+0x50`/`+0x54` have a handler+size shape that suggests the root is itself a layer-record-family member |

**Selector use is `PARTIALLY CONFIRMED`.** Both accepted Level-3 runtime
captures were selector `1`, both zero-selector call sites resolve to `1` through
`0x080089A0`, and every examined selector source resolves to `1`. But **55 of 452
MapEntries expose a multi-word source array** (run lengths 2..12), the engine
never bounds the array on the examined paths, and selectors above `1` were
**not excluded**. "Selector 1 only" is not a canonical claim.

### 3.3 Layer record - dominant form only

Owner: LOGX-LAYER-001 (record), LOGX-TILE-001 (payload).

| Field | Width | Engine use | Semantic status |
| --- | --- | --- | --- |
| `+0x00` | 4 | odd, non-4-byte-aligned word; a valid Thumb code entry; five distinct values | **handler/function entry.** `PARTIALLY CONFIRMED` semantically. **`REFUTED` as a numeric layer type tag** and **`REFUTED` as a discriminator between field layouts**: the one recovered reader `0x08007B78` is shared by 1516 of 1808 references and reads the same offsets regardless of the word |
| `+0x04`, `+0x08` | 4 each | copied to `object+0x3C`/`object+0x40` | meaning `UNKNOWN` |
| `+0x0C`..`+0x13` | 4 + 4 | two words copied to `object+0x44`/`object+0x48` | signedness, units, X/Y pairing `UNRESOLVED` |
| `+0x14`, `+0x15` | 1 each | separate `ldrb`, multiplied; the streaming consumer computes `y*record[+0x14] + x` | **`CONFIRMED`**: X count and Y count. Never merged into a halfword |
| `+0x16` | 2 | `ldrsh`; 0 on all 1420 dominant records | `CONFIRMED` signed; the consumer of `object+0x0C` is `UNRESOLVED` |
| `+0x18` | 4 x (`+0x14`*`+0x15`) | chunk-pointer window, `record + 0x18 + 4*i` | `CONFIRMED` physical; 117 dominant records carry an internal null |

`+0x0D` and `+0x11` as X/Y offsets are **`REFUTED` at the value level** (0 on
1458 and 1453 of 1464 records, and not among the fields the recovered consumer
reads). The stronger "no consumer exists" claim is **not** made: the region's
instruction census is incomplete (2,035 undecodable halfwords in
`0x08007000..0x08010000`). **Layer positioning remains `UNRESOLVED`** - no signed
coordinate transform was found and none was imported.

`+0x1C` as "a content pointer" is **`REFUTED`**: on the dominant class it is
simply word index 1 of the `+0x18` window.

The four-slot install cap is resolved: `cmp r6,#4` / `bgt` at
`0x08007BE2`/`0x08007BE4` bounds only the constructor's warm-up; the streaming
method `0x08007C12` uses a four-entry resident cache and loses nothing when
`x*y > 4`.

### 3.4 Chunk payload and tile entries

Owner: LOGX-TILE-001. A dominant-form chunk is **2048 decoded bytes consumed as
1024 little-endian `u16` entries, 32 columns x 32 rows, 64 bytes per row.** Both
dimensions come from the engine's own accesses (`(row & 31) * 64`,
`(col & 31) * 2`, `ldrh`, and a whole-64-byte-row VRAM copy), not from stored
data and not from target spacing. The tile unit is **8x8 pixels**
(`asrs #3` on both axes, a 64-byte copy per destination tile, a `>> 8` chunk
index), so a chunk covers **256x256 pixels**.

| Bits | Measurement | Status |
| --- | --- | --- |
| 0-9 | 896 distinct values, max 895; 1,241,888 per-map nonzero entries with **0** outside the map's own two tile sources | **`CONFIRMED`** as the tile ordinal the engine's own loaders populate. Not strengthened into "final VRAM tile number" |
| 10 | 46,034 entries | **`CONFIRMED` to exist, be used and lie outside the index field.** "Horizontal flip" is **`PARTIALLY CONFIRMED`** (platform BG layout under the engine's own 8bpp `BGxCNT`); no payload consumer reads the bit |
| 11 | 15,668 entries (both 10 and 11 on 5,239) | as bit 10 |
| 12-15 | **zero on all 3,834,880 entries** | **RESERVED / CONSTANT IN CANONICAL DATA; UNUSED BY ANY KNOWN CONSUMER; semantic role `UNRESOLVED`.** Explicitly **not** to be documented as "unused by the format": canonical-zero evidence is not format-level unused-bit proof, and the engine's occupancy test at `0x08008076` treats any nonzero entry as occupied |

The absence evidence is a raw-halfword mask scan that finds 1532 adjacent
`lsls`/`lsrs` pairs, **none of the 29 in the map/layer region reaching bit 9 or
above**. Its scope is deliberately narrow and the unscanned idioms are published
(8,014 shift-then-branch pairs, 1,204 `movs`+`lsls` builds, non-adjacent pairs).

### 3.5 Selector stream and bank lookup

`root+0x48` is a container whose decoded `u16` array the engine prefix-decodes
**in place** at `0x08009C02`..`0x08009C12`:

```text
abs[0] = raw[0]
abs[i] = (raw[i] + abs[i-1] + 1) & 0xFFFF        for i >= 1
```

with the container's declared size as the terminator. All 452 roots decode;
declared sizes 4..1784 bytes (2..892 selectors). **LOGExtractor's recurrence is
`CONFIRMED`; its use of the value is `REFUTED`.** A decoded value is a packed
pair: `value >> 8` indexes the `root+0x4C` bank array, `value & 0xFF` selects a
64-byte tile inside that bank's `0x4000`-byte payload (load at `0x08009C6E`).
One selector contributes one 8x8 tile to character memory at
`0x06000000 + 64*ordinal`. A bank container is decoded once per contiguous run of
equal `value >> 8`.

**`0x179764` is corrected.** GBA `0x08179764` is the value stored at `root+0x4C`
on all 452 roots. It points at **187 consecutive aligned in-ROM `u32` pointers**,
every one a kind-1 container: 186 declare `0x4000` and the last (index 186, at
`0x08177AB8`) declares `0x3C40`. The entry after the table is `0x00000001`. The
largest bank index used by any canonical stream is **186**, exactly the last
entry. So `0x179764` is a **descriptor field's value**, not an independent global
graphics structure. The "128x128 / 256-tile source block" is that bank's
`0x4000 / 64` addressed capacity under an 8-bit tile field -
**`PARTIALLY CONFIRMED` as an engine resource unit, and `REFUTED` as a universal
property** (one canonical bank declares `0x3C40`).

### 3.6 Map populations (canonical fact table)

Every figure the synthesis asserts, with the ticket that owns it. This table is
**machine-checked**: `tools/research/logx_synthesis_audit.py` parses it and
compares it with its own `CANONICAL_FACTS`, so prose and key cannot drift.

| key | value | ticket |
| --- | ---: | --- |
| `mapentry_records` | 452 | `LOGX-MAP-RECORD-001` |
| `mapentry_stride` | 56 | `LOGX-MAP-RECORD-001` |
| `selector_1_roots` | 452 | `LOGX-MAP-RENDER-001` |
| `distinct_selector_1_roots` | 421 | `LOGX-MAP-RENDER-001` |
| `layer_references` | 1808 | `LOGX-LAYER-001` |
| `unique_layer_records` | 1464 | `LOGX-LAYER-001` |
| `dominant_layer_references` | 1516 | `LOGX-LAYER-001` |
| `dominant_layer_records` | 1420 | `LOGX-LAYER-001` |
| `chunk_grid_cells` | 4274 | `LOGX-TILE-001` |
| `unique_chunk_targets` | 3745 | `LOGX-TILE-001` |
| `chunk_decoded_entries` | 3834880 | `LOGX-TILE-001` |
| `selector_bank_containers` | 187 | `LOGX-TILE-001` |
| `connector_records` | 735 | `LOGX-CONNECTOR-001` |
| `connector_directed_links` | 694 | `LOGX-CONNECTOR-001` |
| `connector_reciprocal_links` | 674 | `LOGX-CONNECTOR-001` |
| `connector_one_way_links` | 20 | `LOGX-CONNECTOR-001` |
| `connector_self_links` | 3 | `LOGX-CONNECTOR-001` |
| `codec_unique_containers` | 4324 | `LOGX-CODEC-001` |
| `codec_packed_containers` | 4322 | `LOGX-CODEC-001` |
| `codec_stored_containers` | 2 | `LOGX-CODEC-001` |
| `appearance_definitions` | 232 | `LOGX-CHAR-001` |
| `appearance_stride` | 16 | `LOGX-CHAR-001` |
| `sprite_definition_run` | 297 | `LOGX-SPRITE-001` |
| `sprite_definition_array_slots` | 4070 | `LOGX-SPRITE-001` |
| `sprite_definition_non_null_slots` | 1721 | `LOGX-SPRITE-001` |
| `unique_animation_objects` | 1017 | `LOGX-SPRITE-001` |
| `animation_direction_cells` | 13660 | `LOGX-FRAME-001` |
| `unique_frame_records` | 10980 | `LOGX-FRAME-001` |
| `piece_records` | 11005 | `LOGX-FRAME-001` |
| `multipart_frames` | 21 | `LOGX-FRAME-001` |
| `unique_sprite_graphics` | 7390 | `LOGX-FRAME-001` |
| `known_container_corpus` | 11715 | `LOGX-GFXSCAN-001` |
| `external_scanner_recall` | 11513 | `LOGX-GFXSCAN-001` |
| `referenced_packed_residuals` | 387 | `LOGX-GFXSCAN-001` |
| `engine_informed_residuals` | 5479 | `LOGX-GFXSCAN-001` |

`mapentry_stride` and `appearance_stride` are recorded in **bytes** here; the
tickets state them as `0x38` and `0x10` respectively.

**Arithmetic checks that must close**, stated with numerator and denominator so
no percentage is quoted alone:

```text
1808 = 4 slots * 452 roots                 (LOGX-LAYER-001)
4274 = 156 null + 4118 non-null            (LOGX-TILE-001)
3834880 = 3745 * 1024                      (LOGX-TILE-001)
1241888 = 1218581 static + 23307 animated  (LOGX-TILE-001; 0 exceptions, 178 maps)
4070 = 1721 non-null + 2349 null           (LOGX-SPRITE-001)
4324 = 4322 packed + 2 stored              (LOGX-CODEC-001)
11715 = 11513 + 202                        (LOGX-GFXSCAN-001 all-class recall)
11715 = 11715                              (distinct corpus; the per-class sizes
                                            sum to 11717 because
                                            zero_header_form0_containers is a
                                            SUBSET of root_48_selector_streams,
                                            sharing 0x082B5F1C and 0x082B5F94)
7390 = 7355 + 35                           (LOGX-FRAME-001: 7355 is exactly the
                                            single-piece-frame subset)
```

---

## 4. Connection / warp structures

Owner: LOGX-CONNECTOR-001.

### 4.1 What is `CONFIRMED`

| Claim | Status |
| --- | --- |
| `root +0x40` is a 4-byte word field | `CONFIRMED` |
| `root +0x40` is the element count of the array at `+0x44` | `CONFIRMED` |
| `root +0x44` is a 4-byte aligned pointer to an array of 4-byte ROM pointers | `CONFIRMED` |
| the pair is read by one `ldm r1,{r1,r2}` at `0x08009676` | `CONFIRMED` |
| the walk `0x08012664` iterates `count-1 .. 0` at a 4-byte stride and calls each record's `+0x00` | `CONFIRMED` |
| each element resolves to a `MapEntry` through the accepted two-byte key lookup | `CONFIRMED` (735/735) |
| the record block stride is 24 bytes (`0x18`) and the engine reads `+0x00..+0x17` | `CONFIRMED` |
| the destination lives at `+0x11` (high) / `+0x12` (low) and is **two independent bytes** | `CONFIRMED` |
| the four `u16` at `+0x08` are two ordered intervals (`A<=C`, `B<=D`, 735/735, no zero area) | `CONFIRMED` |
| record census: 735 references, 735 unique, 0 shared, 0 malformed; `count == 0` iff `list == 0` on 452/452 | `CONFIRMED` |
| link graph: 694 directed, 674 reciprocal, 20 non-reciprocal, 3 self-links, 350 distinct destinations, 348 maps with links | `CONFIRMED` as topology, with a **definitional caution**: the three published categories are not disjoint. The ticket's probe computes `reciprocal` **excluding** self-links and `one_way = links - reciprocal`, so the 3 self-links are counted inside the 20. **674 + 20 = 694 closes the total**; the disjoint reading is **674 non-self reciprocal + 17 non-self one-way + 3 self** |

The corpus layout invariant `root + 0x44 == root - 4 * root[+0x40]` holds on all
348 non-null roots and is recorded as a **layout invariant, not an engine rule**.

### 4.2 What is `PARTIALLY CONFIRMED`

| Claim | Status |
| --- | --- |
| the record is a "connector" in the engine's own vocabulary | `PARTIALLY CONFIRMED`: it is a map-destination record; the engine's own name is not recovered |
| `+0x00` is a **class tag** | `PARTIALLY CONFIRMED` physically (`CONFIRMED` that it is called as a function pointer and takes exactly two values); **no class-table walk was recovered that names the two classes** |
| `+0x13`, `+0x14`, `+0x16`, `+0x17` are engine-read fields | `CONFIRMED` as read; semantics `UNRESOLVED` |
| the four `u16` are tested against a position | `UNRESOLVED` |

### 4.3 What is `UNRESOLVED` - and must stay so

- **geometry axis** - which pair is horizontal and which vertical;
- **geometry origin** - the only coordinate arithmetic on the recovered path is
  `-112` / `-76`, applied to the *caller's* coordinate pair, not to the record;
- **geometry units** - every reading is `0` or `8k+1` (1468 at `8k+0`, 1448 at
  `8k+1`, 24 at `8k+7`), consistent with a pixel coordinate inclusive of the last
  pixel of an 8-pixel cell, but no conversion constant is introduced on shape alone;
- **signedness** - as `u16` the values are `0..977`, and as `s16` every value
  `<= 977` has the same numeric value, so canonical data cannot distinguish them;
- **edge inclusivity** - no membership comparison against the four values was
  recovered, so inclusivity cannot be stated;
- **the exact region-membership test**;
- **spawn / arrival position**, **facing / direction**, **script or event
  relationship**;
- **the meaning of the two record classes**;
- **LOGExtractor's `+8`** - no engine counterpart on the recovered path. It is
  **neither confirmed nor refuted**; it is not needed to resolve a destination.

### 4.4 Edge-case populations the authoring tools must respect

| Population | Count |
| --- | ---: |
| roots with `+0x40 == 0` and `+0x44 == 0` | 104 |
| roots with a non-null array | 348 |
| maximum `+0x40` | 14 |
| `+0x40` distribution | `{0:104, 1:86, 2:188, 3:40, 4:27, 5:5, 6:1, 14:1}` |
| `+0x44` targets shared between roots | 0 |
| destination keys that fail to resolve | 0 |
| records whose `+0x10` exceeds 3 | 10 (maps 48, 49, 114, 115, 117, 119, 218, 219, 252, 257) |
| `+0x13` census | `{0:561, 1:174}` |
| `+0x17` census | `{0:543, 1:180, 2:8, 3:2, 255:2}` |
| state/byte `+0x14` distinct values / maximum | 139 / `0xFFFF` |

### 4.5 Transition-record authoring readiness

> **Naming.** This synthesis uses **transition record** and **destination key**
> for the accepted structures. "Connector", "warp", "door", "exit" and "edge
> transition" are **community labels, not engine facts**: LOGX-CONNECTOR-001
> recovered no engine vocabulary for the record, and its accepted closeout
> explicitly assigns no such name. The task names `TOOLS-3`, `TOOLS-4` and
> `NEW-4` keep the community word only because a human reader looks for it.
> This supersedes the earlier wording in this document that used "warp" as a
> class name.

| Capability | Classification | Basis |
| --- | --- | --- |
| **Existing connection inspection** | **READY** | the whole record layout is `CONFIRMED` at engine access widths; 735/735 records read with zero anomalies |
| **Existing destination editing** (rewrite `+0x11`/`+0x12` in place) | **READY WITH VALIDATION** | the destination is two bytes in a fixed-size 24-byte record, so an in-place rewrite changes no size, moves no pointer and updates no count. Validation required: the new pair must resolve through the `0x080089FC` lookup, and the corpus has 0 unresolvable destinations so a tool must refuse one. No other field needs to change |
| **Destination randomization** | **READY WITH VALIDATION** (structural) | as above. Structural invariants to preserve: the pair resolves; `+0x40`/`+0x44` are untouched; the record's other 22 bytes are preserved byte-exactly. See §14 for the gameplay-logic half, which is **not** part of this readiness |
| **Reciprocal-graph rewriting** | **READY WITH VALIDATION** (structural) | reciprocity is a measured property (674 of 694 links), not an engine invariant, and the corpus already contains 20 one-way and 3 self links. A tool may preserve, break or create reciprocity, but it must **state which**, and it must not claim the engine requires a symmetric graph |
| **Trigger-region editing** | **BLOCKED** | the four `u16` are `CONFIRMED` only as two ordered intervals. Axis, origin, units, signedness and edge inclusivity are all `UNRESOLVED`, so a tool cannot tell a user what a number means or validate a proposed region |
| **New connection-record creation** | **BLOCKED** | three obstacles, any one sufficient: (1) `+0x00`/`+0x04` are the addresses of the engine's own record classes (`0x08007675` / `0x080072CD` / `0x0800776D`), which cannot be invented; (2) the array is not null-terminated and `+0x40 == 0` iff `+0x44 == 0`, so growing it requires relocating or extending the array and updating two coupled fields; (3) the `root +0x44 == root - 4*count` corpus layout means a grown array may overwrite the bytes immediately below the root |
| **Spawn / arrival control** | **BLOCKED** | no record field was shown to be a destination spawn position, and facing is `UNRESOLVED`. A destination key selects a *map*, not a position |
| **Full `AUTHOR_NEW` warp authoring** | **BLOCKED** | requires new-record creation (blocked) *and* region authoring (blocked) *and* a spawn mechanism (unknown). Not "close to ready" |

> **The practical distinction the queue exists to preserve:** *destination-key
> randomization is safe before arbitrary new-region authoring.* Rewriting
> `+0x11`/`+0x12` touches two bytes of a fixed-size record and needs only a
> resolvability check. Authoring a new trigger rectangle needs semantics the
> queue did not recover.

---

## 5. Containers and compression

Owner: LOGX-CODEC-001. The canonical wrapper model is in §2.5; this section adds
the census, the decoder status, the encoder readiness and the discovery
adjacency.

### 5.1 Census over the accepted resource graphs

Seeded from the accepted graphs only: 421 distinct selector-1 roots.

| Resource class | References | Unique containers | Forms | Declared size |
| --- | ---: | ---: | --- | --- |
| dominant layer chunk (`record + 0x18`, handler `0x08008087`) | 3,912 | 3,745 | kind 1 x 3,745 | `0x800` on all |
| `root + 0x48` selector stream | 421 | 392 | kind 1 x 390, kind 0 x 2 | 4..1,784 |
| `root + 0x4C` selector bank | 187 | 187 | kind 1 x 187 | `0x4000` x 186, `0x3C40` x 1 |
| **total** | **4,520** | **4,324** | 4,322 packed + 2 stored | 4..16,384 |

Zero malformed candidates, zero payload-digest collisions, zero containers shared
between classes. The 3,745 dominant figure reproduces LOGX-TILE-001 exactly.

### 5.2 Project decoder status

**`CORRECT WITH LIMITED FIXES REQUIRED`.** No shipping behaviour changed.

Confirmed correct:

- it reads the engine's wrapper layout and dispatch value set;
- its stored-branch semantics match the engine's `memcpy`;
- its packed grammar is byte-exact against a second, non-importing implementation
  on all **4,322** reachable packed containers;
- all 4,322 decoded lengths equal their declared sizes;
- its `packed_end` is **measured by running the decoder, never read from a
  field** - which is exactly what future allocation work needs.

Two documented differences from the engine, **neither an engine-contract
violation**:

1. **It does not enforce exact declared-size completion.** An over-long final
   match is silently **clipped** to the declared length and the decode is
   reported as successful, so a caller can receive a truncated payload
   (`01000000040000000558d020000000c0` -> accepts, returns 4 bytes). The engine
   has no length comparison either, and the case never arises on the canonical
   corpus. **This is the single most important production defect in the queue**
   because every later writing capability will rest on this decoder's
   trustworthiness. Pinned by
   `test_project_decoder_clips_an_over_long_final_match`.
2. `DEFAULT_MAX_OUTPUT = 64 * 1024` is a host safety limit with **no engine
   counterpart** and must never be cited as a format maximum.

**Honest limit of the differential**: the second implementation was written after
reading the first, and 65 of 83 normalised grammar lines are verbatim identical.
The grammar's authority rests on the **corpus** (4,322 real containers decode to
exactly their declared sizes and reach their own end markers there), not on the
agreement.

### 5.3 Encoder readiness: `PARTIAL`

| Requirement | Value or rule | Basis |
| --- | --- | --- |
| wrapper form | `u32` form, `u32` declared size, payload at `+0x08` | `CONFIRMED` |
| form to emit | `1` (the only form the canonical packed corpus uses) | `CONFIRMED` |
| declared-size field | the **decoded** byte count, excluding the 8-byte wrapper | `CONFIRMED` |
| raw fallback | form `0` plus the byte count | `CONFIRMED`; `build_stored` already emits it |
| stream termination | emit the stream's own control escape so decoding stops at the declared size | `CONFIRMED` for the corpus; **the encoder must self-verify** |
| alignment | the source is read as whole 32-bit little-endian words; pad the final word | `CONFIRMED` |
| destination safety | must not rely on the engine to bound output | `CONFIRMED` |
| round-trip | decode the encoded stream and require exact equality | project policy |

**What is missing.** The *initial literal width* the dispatcher supplies is
`UNRESOLVED` (immaterial for decoding, because every canonical stream opens with
an escape that overwrites it, but an encoder must not rely on it). No production
encoder exists: `webfoot_lz.pack` is a valid-stream generator with a **measured
size penalty**; whether that suits insertion is an authoring decision this queue
did not make. Because the engine has no output counter, **the end marker's
placement is load-bearing**, and `packed_end - offset` is the only capacity a
re-encoded payload may occupy.

---

## 6. Appearance / character resources

Owner: LOGX-CHAR-001. Discovery root: the literal in eight engine functions.

| Offset | Width | Physical type | Engine use | Semantic status |
| --- | --- | --- | --- | --- |
| `+0x00` | 2 | `u16` LE | `ldrh` at `0x08024FAC`, `0x080251BC`; index into `0x0806BCE8` (x4) | **text relationship `CONFIRMED`**; "name" `PARTIALLY CONFIRMED` - the field is drawn once at `0x0803DADA` and its text is a short label, but no instruction names or derives it |
| `+0x02` | 2 | `u16` LE | `ldrh` at `0x080252E6`, `0x0802539E`, `0x08025EC2`; the same table | **text relationship `CONFIRMED`**; "description" `PARTIALLY CONFIRMED` (prose text, wrapped draw). **`REFUTED` as "skipped"**: three engine functions read it |
| `+0x04` | 4 | `u32` LE | `ldr` at `0x080273B2`, `0x08027968`; accessor `0x08000158` -> the 297-entry pointer run | **sprite lookup path `CONFIRMED`**; the words it selects are the accepted sprite-definition objects |
| `+0x08` | 4 | `u32` LE | `ldr` at `0x080250CA`; accessor `0x08011F20` -> `u32 at 0x086F393C + 4*slot`; result passed to the container dispatcher `0x0803D940` | **portrait-pointer relationship `CONFIRMED`**; "portrait graphics" `PARTIALLY CONFIRMED` - no pixel format, dimension or rendering claim |
| `+0x0C` | 4 | `i32` LE, sign-tested with `blt` | `0x08027948` computes `0x08711274 + 28 * +0x0C` (the TOOLKIT-009 stat table, stride `0x1C`, 141 records) and compares it with its second argument | **`CONFIRMED` as one signed index into that family**; higher-level meaning `PARTIALLY CONFIRMED`/`UNRESOLVED` |

**Canonical semantic wording.** The table is **named appearance definitions with
optional slot and stat indices**. It is **not** promoted to "the character
table" or "the global character table": the 152 distinct labels span named
fighters, story characters, generic enemies, machinery, body parts and a
`"Human"` catch-all, which refutes both "playable roster" and "enemy table";
completeness is not established; 98 records have `+0x08 == 0` (no slot) and 88
have `+0x0C < 0` (no stat record).

**Do not invent labels for `+0x0C`.** Its physical structure, its signedness and
its index arithmetic are established; its target's meaning is not.

Non-obvious invariants an editor must respect:

- `+0x02 == +0x00 + 1` on **232/232** records. This is a **data invariant of the
  canonical image**, not an engine constraint - no instruction compares or
  derives the two fields. Editing `+0x00` alone makes the image
  non-representative of the corpus.
- The input index to `0x08027948` is an **appearance id in the same id space as
  `+0x04`** (both sides pass through the accessor `0x08000158` before comparison),
  not a party id, dialogue-portrait id or entity-template id.
- `0x08027948` returns `-1` when its scans exhaust; `0x08024F3C` does not (its
  only `mvns` builds a `-1` it stores at `[object + 0x14]`).
- `+0x08`'s value set is a strict **inclusion** in the array's 155 valid slots
  (`0` plus a 110-element subset of `8..162`), not the whole of them.
- The `+0x0C` values `{142,143,145,146,147,148,149}` (8 records) lie past the
  141-record extent TOOLKIT-009 validated; `141` and `144` are unused. Recorded
  as an **anomaly**, not promoted.
- Exactly one pair of records (80, 81) is byte-identical in all five fields.
  78 records repeat an existing `(+0x00, +0x02)` text pair with different
  resource fields, so text pairs do **not** identify a record.

---

## 7. Sprite definitions

Owner: LOGX-SPRITE-001.

**Pointer run.** `0x086B6BDC`, **297 entries**, logical ids **10..306**
(`index = id - 10`), all word-aligned ROM pointers, strictly ascending, 297
unique targets, no duplicate pointer, terminated by the non-ROM word
`0x03001068` at `0x086B7080`. Exactly two `ldr Rt,[pc,#imm]` sites in the whole
image carry the literal: `0x0800015E` (pool `0x080003C0`) and `0x0801713E`
(pool `0x0801715C`).

**The run is not "ids 0..296".** Ids `0..9` are **party-slot aliases**:
`0x08000158` branches at `cmp r0,#0xa` into a party path that resolves a party
slot through a `0x68`-stride record to a byte, indexes a 24-byte-record table at
`0x086B82EC`, and re-enters the array through `0x0801713C`, which reads a `u16` id
from record `+0x0E` and applies the identical arithmetic. Run index 0 is simply
logical sprite id 10 and carries **no established special meaning**.

**`0x086B6BB4` is resolved, not a run prefix.** It is the compiler-folded
arithmetic base of the accessor. The ten words it reaches
(`0x086A6424, 0x086A7238, 0, 0, 0x086A7E7C, 0, 0, 0, 0, 0x086A899C`) are the
**inline animation array of the definition object at `0x086B6B60`** - the run's
own last entry, logical id 306, count 10 - whose array therefore spans
`0x086B6BB4..0x086B6BDC` and ends exactly where the pointer run starts. A backward
header scan finds exactly one object whose counted extent lands on the run.

**Definition object.** Extent is `0x54 + 4*count`. **231 of 296** adjacent
definition pairs match it and **232 of 297** accepted boundaries match it once
the last definition is measured against the run start; the **65 gaps** are each
exactly `0x100` bytes, and each such gap is the block that the *successor's*
`+0x04` points at. Those gaps are not over-interpreted.

| Offset | Physical field | Status |
| --- | --- | --- |
| `+0x00` | `u16` LE; low byte = inline array element count; high byte `0` on all 297 | physical `CONFIRMED`; count semantic `CONFIRMED`; animation-count semantic `CONFIRMED` |
| `+0x02` | `u16` LE byte size handed to `0x0803D5B8` | size `CONFIRMED`; block-pool reading `INFERRED` |
| `+0x04` | `u32` pointer to the 256 bytes immediately before the object, in exactly the 65 objects that have it | pointer relationship `CONFIRMED`; palette-remap reading `INFERRED` |
| `+0x08` | four individually read bytes | `UNRESOLVED` |
| `+0x0C` | `u32` | `UNRESOLVED` - no consumer found |
| `+0x10..+0x4F` | four 16-byte records of four `s32` | `UNRESOLVED` - no consumer found; value ranges are rect-like |
| `+0x50` | `u32` parallel per-animation pointer array | present in exactly 10 of 297 objects; `PARTIALLY CONFIRMED`; entry meaning `UNRESOLVED` |
| `+0x54` | `count` x `u32` LE inline array | physical field and animation-array semantic `CONFIRMED` |

**The count-bounded model is `CONFIRMED` and the fixed-slot model is
`REFUTED`.** Five engine sites read the low byte with `ldrb`, compare it with the
index they are about to load, skip the load when the count is not greater, and
then null-test the element:

```text
0x08013046  ldrb r1,[r0]  0x08013048  cmp r1,#7  0x0801304C  ldr r0,[r0,#0x70]
0x08013088  ldrb r1,[r0]  0x0801308A  cmp r1,#8  0x0801308E  ldr r0,[r0,#0x74]
0x080131DA  ldrb r1,[r0]  0x080131DC  cmp r1,#7  0x080131E0  ldr r0,[r0,#0x70]
0x0802736C  ldrb r2,[r1]  0x0802736E  cmp r2,#1  0x08027372  ldr r1,[r1,#0x58]
0x0802A28E  ldrb r1,[r0]  0x0802A290  cmp r1,#6  0x0802A294  ldr r2,[r0,#0x6c]
```

A raw scan of every decodable instruction boundary in `0x08000000..0x08060000`
finds these five sites and no others, under three different window widths.

**Census over the 297 definitions:** 4,070 inline-array slots, **1,721 non-null
and 2,349 null**; index 0 is non-null in 297 of 297, index 1 in 262 of the 285
that have it, index 22 in 5 of 5. The word at `+0x54 + 4*count` is nonzero for all
297 objects, so the array is genuinely bounded by the count. Definition element
counts over the 297: `{1:12, 2:41, 3:1, 5:2, 10:51, 13:44, 15:1, 16:3, 18:9,
19:67, 20:29, 21:16, 22:16, 23:5}`. **1,017 unique animation records** are reached
by the 1,721 non-null slots; 410 of them are referenced from more than one
definition/index site, with maximum reuse 16.

**Selection mechanism (`CONFIRMED` as a selector index).**

- `0x0800ECDA(obj, index)` assigns `*(u32*)(definition + 0x54 + 4*index)` to
  `obj+0x50`, and `definition[0x50][index]` to `obj+0x4C` when `definition + 0x50`
  is non-null. **It has no range check.** 162 call sites examined: 161 pass a
  compile-time constant in `0..21`, one passes an index read from the state table.
- `0x0800ECF0(obj, state)` and `0x0800ED3E(obj, state, row)` first translate the
  state through the **25-entry table at `0x08072670`** (`0..15` identity,
  `16..22 -> 17..23`, states `23`/`24` both alias indices `10`/`11`), so state and
  animation index are **not** in bijection. That table is read by exactly four
  sites (`0x0800ECF6`, `0x0800ED48`, `0x0802CB96`, and the predicate at
  `0x0800EEB6`), is addressed only with states `0..24`, and the bytes after it are
  not part of it.
- `0x0800EF38` computes `*(u32*)(obj+0x50 + 16*frame + 4*direction + 4)` into
  `obj+0x54`.

**Semantic slot status: mostly `UNRESOLVED`, deliberately.** Four positions have
an engine-visible *role* rather than a name: index 1 is tested before a
state-object swap, index 6 before a two-versus-three selection, index 7 before
allocating a 12-byte object and then selecting index 7 and calling `0x0800ED18`,
and index 8 before dispatching the state method with argument `8`. Positions are
comparable across definitions and their occupancy is measurable, but **no engine
instruction names an animation**, and no code adds one to an animation index, so a
`slot = index + 1` shift has **no witness**. LOGExtractor's `stand`, `walk`,
`run`, `attack1..4`, `block`, `idle`, `hurt`, `transform`, `arms_up`, `pickup`,
`takeoff`, `flying`, `mode7_fly`, `dead`, `special`, `teleport` and `fusion`
labels are **not promoted** and the **23-slot numbering is not adopted**.

**Authoring consequence:** an animation slot is *optional*. An editor must be
able to write a **null element**, and must not assume 23 positions exist.

---

## 8. Animation and frame structures

Owner: LOGX-FRAME-001.

### 8.1 Animation object

```text
+0x00            u32 frame_count, values 1..16 (high halfword always 0)
+0x04            4 * frame_count 32-bit ROM pointers, 4-byte stride, 16-byte row
                 cell(frame, direction) = animation + 0x04 + 16*frame + 4*direction
+0x04 + 16*fc    two words, recorded raw and NOT named
```

Three readings are kept apart and must never be collapsed:

- the **physical field** - a `u32` read as a word (`0x0800DE7E`, `0x0800F18A`,
  `0x0800F3EC`);
- the **count semantic** - it counts table **rows**, enforced by the frame advance
  (`0x0800DE78..0x0800DE90` clamps, `0x0800DEBA..0x0800DECC` wraps modulo);
- the **extent semantic** - no two of the 1,017 canonical animation objects
  overlap and every gap to the next is a multiple of four.

**LOGExtractor's shift/count hypothesis is given a narrower physical explanation
rather than retained or discarded wholesale.** The stored word is a count of rows;
the engine's `<< 2` is applied to the **direction index** to walk a cell within a
row (`0x0800EF3C lsls r2,r2,#4` then `0x0800EF42 lsls r2,r2,#2` then
`0x0800EF46 ldr r1,[r1,#4]`). `count * 4` reproduces the flat cell count exactly,
which is why an extractor that read it as a pointer count still produced plausible
output. **The shift formula is not canonical.**

**The two trailing words remain `UNRESOLVED`.** They are not proven to be a
trailer at all: in **30 of 1,017** objects a frame record starts exactly at
`+0x04 + 16*frame_count`, so those two words are that record's piece count and
header. Recorded raw as `trailer_0_raw` / `bytes_04_raw`.

**Direction.** Four cells per frame index, **independent of `frame_count`**; over
the 1,017 unique objects there are **13,660 cells, none null**, **3,415 in each
position**. The engine's facing computers write exactly `{0,1,2,3}` to `obj+0x10`,
and in both functions the horizontal pair is compared first (`|dx| >= |dy|`), so
`2`/`3` are the horizontal axis and `0`/`1` the vertical, with the sign choosing
within each axis. The decisive structural evidence that this is a two-dimensional
cell table rather than a direction-major list is that **all 989 shared frame
targets are confined to one frame index** while being reachable from several
direction indices. **The screen-space orientation of the values is `UNRESOLVED`**,
recorded `INFERRED` for the sign convention only; **no direction is named**.

Frame counts over the 1,017 records: `{1:80, 2:275, 3:180, 4:407, 5:16, 6:13,
7:11, 8:3, 9:2, 10:2, 11:24, 12:2, 16:2}` - **0 zero-frame animations**.

### 8.2 Frame record

```text
header, 0x08 bytes
  +0x00  u32 piece_count
  +0x04  s8  min_x   \  the RENDERED FRAME'S OWN BOUNDING BOX: equals the minima
  +0x05  s8  min_y    | over the frame's pieces and the extent of their union on
  +0x06  u8  width    | 10,980 of 10,980 frames.  It is NOT a collision box,
  +0x07  u8  height  /   hitbox, feet box or origin box
pieces begin +0x08, stride 0x0C
```

The stride is settled from the engine, twice over:

- the render loop `0x0800F3C0` computes `r1 = 3*index`, `r1 <<= 2`,
  `r7 = frame + r1 + 8`, i.e. `frame + 8 + 12*index`;
- under `(8, 12)` **all 11,005 pieces** resolve to a container whose declared
  decoded length equals `dim_0 * dim_1`, with **0 exceptions**, while the
  previously accepted `(4, 16, +6, +0x0C)` model **fails on 25 pieces** and
  overruns the following frame record on 16.

Internal consistency checks that must close:

```text
10980 = 10959 single-piece + 19 two-piece + 2 four-piece
11005 = 10959*1 + 19*2 + 2*4
2*287 + 3*702 = 2680   (the frame-target reuse identity; NOT 3*287 + 4*702)
```

**Populations:** 10,980 unique frame records over 11,005 piece references
(23,180 over animation *references*); 21 multipart frames; 989 shared frame
targets, maximum reuse 4, and every shared target is confined to one frame index;
piece counts `{1:10959, 2:19, 4:2}`; distinct cells per frame
`{1:702, 2:287, 4:2426}`.

### 8.3 Piece

| Offset | Width | Physical field | Engine read |
| --- | --- | --- | --- |
| `+0x00` | 1 | `s8` x offset, added to the entity's own coordinate | `ldrsb` at `0x0800F204`, `0x0800F22A`, `0x0800F25E` |
| `+0x01` | 1 | `s8` y offset | `ldrsb` at `0x0800F22A` (axis assignment `INFERRED`) |
| `+0x02` | 1 | `u8` pixel extent `dim_0`; the engine halves it to centre an OBJ | `ldrb` at `0x0800F206`; halved at `0x0800F20A` |
| `+0x03` | 1 | `u8` pixel extent `dim_1`; the engine multiplies the pair to size the composite buffer | `ldrb` at `0x0800F22E`/`0x0800F230`; multiplied at `0x0800F3DE` |
| `+0x04` | 4 | **packed GBA OBJ attribute pair** `(attr1 << 16) \| attr0` | `ldr` at `0x0800F1C2` and `0x0800F24C`, merged into the outgoing OAM word under mask `0xFE00FFFF` (pool `0x0800F4B0`) |
| `+0x08` | 4 | **graphics-container word** | `ldr` at `0x0800F3CE`, where the loop's index is `r7 = frame + 8 + 12*index` |

Attribute census over all 11,005 pieces: colour-256 set on **11,005**; shape in
`{0,1,2}` with reserved shape 3 never used; size in `{0..3}`; **horizontal flip
set on 2,848**; **vertical flip on 0 of 11,005**. The shape/size decode
**reproduces the separately stored `dim_0`/`dim_1` on 11,005 of 11,005**, and
that independent agreement is what makes the word an attribute pair rather than a
coincidence. Shape and size are **raw stored bits**; the pixel dimensions derived
from them are **derived**.

**Horizontal flip: `CONFIRMED` as a stored bit, rendering effect `UNRESOLVED`.**
In the **2,600 poses where directions 2 and 3 differ in attribute-1 bit 12**, the
two cells name the **same** container in **2,599** cases - a stored flip applied
to shared art. An earlier draft of LOGX-FRAME-001 concluded the opposite; the
count had compared *frame records* rather than *graphics containers*. **The
initial conclusion is not restored anywhere.**

**Piece position origin is `UNRESOLVED`.** The offsets are relative to the
entity's own coordinates; no hitbox, collision, feet or camera anchor was
established. One anchor-adjacent computation (`0x0800F0EA`/`0x0800F106`/
`0x0800F132`, composing a position from `obj+0x6C`/`obj+0x70`) is recorded as a
lead, not promoted.

**Graphics relationship.** `piece +0x08` is a pointer to a packed Webfoot
container: **11,005 of 11,005 resolve AND decode AND declare a decoded length
equal to `dim_0 * dim_1`; 0 failures.** Every piece stores the full GBA-address
form. The targets occupy `0x003C34D0..0x006A87A8` (file offsets), whose lower
bound equals the region `GRAPHICS_FORMAT.md` §9 records. **7,390 distinct
container offsets are reached**, 2,994 of them by more than one piece (maximum
reuse 24).

**The 7,355 / 7,390 relationship, explained exactly:** the accepted set is
precisely the set of containers reached by **single-piece** frames; the extra 35
are exactly what the 21 multi-piece frames reach, and the accepted reader's
16-byte stride rejects all 21 of them.

### 8.4 Frame timing

`PARTIALLY CONFIRMED` at the mechanism level: a `u16` counter at `obj+0x12` is
incremented, shifted right by a byte read from a **state object** (`[r0,#4]`), and
clamped against `animation + 0x00`. **No per-frame duration is stored in the
animation record on this path**, and no instruction consuming either trailing word
was located. Looping is `CONFIRMED` present (`0x0800DEB0` wraps the counter and
resets it). Terminal behaviour, ping-pong and completion state are `UNRESOLVED`.

---

## 9. Graphics discovery

Owner: LOGX-GFXSCAN-001. The external scanner was reconstituted from
`mainant/LOGExtractor` revision `3a78bb35ad181082fbc9da01057538e5a78e8c2d`, the
only commit that ever touched `ImageScan/MainForm.cs` or `ImageScan/Gba/JCALG1.cs`.

**What it does, exactly:** walks every byte offset from `0x200`, requires the
first word to be **exactly `1`**, requires `1 <= declared < 0x20000` **and**
`declared % 4 == 0`, and accepts a position when the decode returns without
raising. No alignment, palette, dimension or visual-plausibility test; no
duplicate suppression. Its only post-decode size treatment
(`decoded length == 256`) changes **sort priority** and does **not** establish
graphics identity.

| Question | Verdict |
| --- | --- |
| **Shipping discovery tool** | **NO** - the acceptance rule asserts almost nothing: the size is read from the same four-byte window that supplied the form word, and the stored form makes a container indistinguishable from a byte sequence that looks like one |
| **Forensic / research tool** | **YES** - 100% of engine-referenced sprite graphics found digest-exact, plus 100% of map chunks and banks, and its 1,453 engine-referenced candidates at unreached addresses are a real lead list |
| **Canonical enumerator** | **NO** - it has no acceptance contract. Its precision comes from the corpus, not from the method |

**Structured engine graph traversal remains authoritative.**

| Measurement | Value |
| --- | ---: |
| byte positions tested | 8,388,093 |
| form-word matches | 29,504 (27,775 word-aligned) |
| submitted after the external size filters | 13,463 |
| external-model candidates | 12,990 |
| **all-class recall** | **11,513 / 11,715 = 98.3%** |
| sprite graphics recall | **7,390 / 7,390 = 100%**, digest-exact |
| map chunks | 3,745 / 3,745 (3,744 digest-agreeing; one differs, see below) |
| banks (`root + 0x4C`) | 187 / 187 (decode differs on 77) |
| **portrait recall** | **UNMEASURED** |

**The 202 misses are the scanner's own filters, not engine limits:**

- `magic != 1` hides the **stored / form-0** resources: **3** known containers are
  missed structurally. **This is not an engine restriction and stored resources
  are not "non-graphics" merely because this scanner cannot see them.**
- `declared % 4 == 0` rejects **199 genuine selector streams** whose declared
  lengths are `4k + 2`. **This filter has no accepted engine basis.**

**Preserved blind spots and disciplines:**

- **Form 0 is the precision cliff.** A scanner must require an engine reference or
  structural agreement for the stored form.
- **A candidate is not a resource.** Candidates are classified as known graphics,
  known non-graphics resources, valid containers with unresolved semantics,
  engine-referenced residuals, unreferenced candidates, or scanner false
  positives - and a successful decode never promotes a candidate into any of them
  on its own.
- **Do not call arbitrary successful decodes graphics.** No decode is promoted to
  graphics anywhere in the queue, and the sprite class is the only recall
  denominator whose graphics identity is established.
- **Do not sum overlapping resource-class counts as if they were mutually
  exclusive.** The per-class sizes sum to 11,717 while the corpus holds 11,715,
  because `zero_header_form0_containers` re-lists the two addresses
  `0x082B5F1C` and `0x082B5F94` already counted in `root_48_selector_streams`.

**`UnknownHeader` result:** `REFUTED` as an engine container form and not
re-promoted. As an external heuristic it decodes, but it is run over bytes that
are not the stream the wrapper names, so its output carries no container
semantics. It also reads from `container + 4`, not `container + 8`.

**Two decode divergences between the external grammar and the project decoder,
both identified:** the four-bit code's `value == 0` arm (the external source
writes a plain `0`; the project decoder writes `literal_offset & 0xFF`), which
moves one map chunk, and the escape's offset reset, which moves 77 banks. The two
grammars therefore disagree on **78** of 11,712 known kind-1 containers.

### 9.1 The 387 referenced, packed residuals

**Result of this synthesis's bounded investigation: see §12.**

What the queue established and this synthesis preserves:

- the engine-informed residual set is **5,479** candidates - a **different
  population** from the 1,476 external candidates at unreached addresses;
- of the 414 engine-referenced residuals, **387 are packed**;
- they are **not** a homogeneous tile-bank family. Declared sizes run
  **128 .. 65,474** bytes and the distribution is dominated by small streams:

  | Declared size | Count |
  | --- | ---: |
  | 256 | 129 |
  | 1,024 | 88 |
  | 4,096 | 97 |
  | 2,048 | 24 |
  | 8,192 | 16 |
  | other | 33 |
  | **>= 8 KiB** | **26** |

- 381 of the 387 are whole-tile; 381 are byte-for-byte confirmed by the external
  model; the conjunction *packed and whole-tile and >= 8 KiB* is **21**;
- the largest referenced residual is `0x087A04F0` (65,474 bytes) and it is **not**
  external-confirmed;
- the concrete lead is the pointer/reference structure around **`0x087B5B64`**;
- **no graphics semantic and no new canonical resource class is claimed for the
  387.** They are a **lead list**.

Named reference sites found by the queue that are relevant to a follow-up:
`0x08004EFC`, `0x082607FC`, `0x082AD8E8`, `0x08028118`, `0x081906BC`, and the
table around `0x087B5B64`.

---

## 10. Refuted LOGExtractor assumptions - one authoritative list

Most entries are `REFUTED`; three are **narrowed rather than refuted** - row 21
(JCALG1 identity is `PARTIALLY CONFIRMED` as JCALG1-like/derived, not established),
row 23 (`+0x0C` was *improved* from "unresolved" to a signed index whose target
meaning remains `UNRESOLVED`), and row 27 (the animation count is a real count,
just not a loop bound). **None of these readings may be reintroduced into
production code or current canonical docs as the whole story.**

| # | LOGExtractor claim | Canonical position | Ticket |
| --- | --- | --- | --- |
| 1 | MapEntry `+0x00` is a big-endian `u16` map id | physically **two ordered key bytes**; the engine compares them with two `ldrb` and a byte `cmp`. Big-endian is a correct display, not the type. "Map id" not promoted | MAP-RECORD |
| 2 | the selector-1 value is "the map render structure" | it is a **per-map load-time definition template** consumed by a map-state loader; the renderer is downstream | MAP-RENDER |
| 3 | `+0x08`/`+0x0A` hold map dimensions | they hold `extent - 1`; the `-1` bias is not modelled upstream | MAP-RENDER |
| 4 | the root is only the render graphics container | `+0x24`/`+0x28`, `+0x34`/`+0x38`, `+0x40`/`+0x44` and `+0x48` are separate subsystems; `+0x4C` is engine-global, not per-map | MAP-RENDER |
| 5 | `ReadPointer`'s 24-bit pointer masking | not used; every pointer claim requires alignment plus containment in the 8 MiB image | MAP-RENDER |
| 6 | the `+0x44` "connector pointer list" record layout | the layout was **not** reproduced; the record's real shape is a two-word class prefix, four `u16` intervals, a selector byte, two destination bytes and four further engine-read bytes | MAP-RENDER then CONNECTOR |
| 7 | layer `+0x00` is a numeric layer type tag | it is an **odd Thumb handler/function entry**; and it does **not** discriminate between field layouts - one reader is shared by 1516 of 1808 references | LAYER |
| 8 | two layer forms discriminated by the first word | replaced by **five constructor/allocator entries over one shared record shape, with two dominant representations** | LAYER |
| 9 | layer `+0x0D`/`+0x11` are X/Y offsets | `REFUTED` at the value level (0 on 1458 and 1453 of 1464 records, and not read by the recovered consumer). Layer positioning `UNRESOLVED`; no signed transform imported | LAYER |
| 10 | layer `+0x1C` is a content pointer | on the dominant class it is word index 1 of the `+0x18` window; no content pointer at `+0x1C` was recovered for any class | LAYER |
| 11 | an `0x18`-byte element stride in the layer record | the `0x18` stride belongs to **root `+0x24`/`+0x28`**; the layer `+0x18` array is **4-byte** elements | LAYER |
| 12 | `0x179764` is the global graphics/atlas table itself | `0x179764` is a **file offset**; GBA `0x08179764` is the **value stored at `root + 0x4C`** and points at a 187-entry selector-bank container table. It agrees on location and entry count, and disagrees on ownership | TILE |
| 13 | the 128x128 / 256-tile source block is a stored dimension | it is that bank's `0x4000 / 64` **addressed capacity** under an 8-bit tile field; one canonical bank declares `0x3C40` | TILE |
| 14 | `root+0x48`'s decoded value selects a tile directly | the value is a **packed `(bank, tile)` pair** (`>> 8` and `& 0xFF`). The **recurrence is `CONFIRMED`**; its use is `REFUTED` as stated | TILE |
| 15 | tile bits 12-15 are "unused" | **reserved / constant in canonical data**, unused by any known consumer, semantic role `UNRESOLVED`. They must **not** be documented as "unused by the format": the engine's occupancy test treats any nonzero entry as occupied | TILE |
| 16 | tile bits 10/11 are H/V flip (as a proven engine fact) | the bits are `CONFIRMED` to exist and be used; the **direction assignment is `PARTIALLY CONFIRMED`** (platform BG layout only - no payload consumer reads them) | TILE |
| 17 | `cmp r6,#4` is a permanent four-chunk cap | it bounds only the constructor's warm-up; the streaming method uses a four-entry resident cache and loses nothing above four | TILE |
| 18 | the opener in `Gba/JCALG1.cs`: a leading zero wrapper word means "empty data" | the zero word **selects the stored branch**; the copy is empty only when the declared size is zero. This and the later "stored raw" reading describe **the same engine branch from opposite ends** | CODEC |
| 19 | `UnknownHeader` is a canonical engine container form | `REFUTED`. The dispatcher knows only `{0,1,2}`; no engine path skips four bytes and then decodes. Four-byte prefixes belong to engine *records* | CODEC |
| 20 | a ~64 KiB engine/format limit | `REFUTED`. No engine comparison against 65,536; the largest declared size reachable is `0x4000`. The figure is host-tool convenience | CODEC |
| 21 | the codec is JCALG1 | `PARTIALLY CONFIRMED` as **JCALG1-like / derived, engine-consistent**. The name is not promoted and byte-compatibility with a pinned reference was never established | CODEC |
| 22 | `+0x02` is skipped / "loosely a description" | `REFUTED` as "skipped": three engine functions read it. It is a second `u16` text index; "description" stays `PARTIALLY CONFIRMED` | CHAR |
| 23 | `+0x0C` is unresolved | **improved**: one signed `i32` index into `0x08711274` at `0x1C` stride, and a negative value is one the engine **skips**. The target's meaning remains `UNRESOLVED` | CHAR |
| 24 | the sprite-definition pointer table starts at `0x6B6BB4` | `0x086B6BB4` is the accessor's **compiler-folded arithmetic base**; the accepted 297-entry run starts at **`0x086B6BDC`** and its first entry is logical id 10. `0x086B6BB4` is definition id 306's inline animation array | CHAR then SPRITE |
| 25 | "character table" | too strong. It is a table of **named appearance definitions with optional slot and stat indices**; the labels include machinery, body parts and a `"Human"` catch-all | CHAR |
| 26 | a fixed 23-slot animation table | `REFUTED as a physical model`. The array is **count-bounded, variable-length and sparse**: 4,070 slots, 1,721 non-null, 2,349 null. The 23 semantic slot names are **not promoted** | SPRITE |
| 27 | the animation count is a loop bound | the engine reads it at **five guarded sites**; the selector itself has **no range check at all** | SPRITE |
| 28 | animation `u32` + `value << 2` | the stored word counts table **rows**; the engine's `<< 2` applies to the **direction index**. `count * 4` reproduces the flat cell count, which is why the reading looked plausible | FRAME |
| 29 | a frame record is `u32 piece_count` then **16-byte** pieces | `REFUTED`: an **8-byte header** (piece count + the frame's own bounding box) then **12-byte** pieces | FRAME |
| 30 | piece `+0x08` is the OAM attribute word and `+0x0C` the graphics pointer | **offset-corrected**: attributes at **`+0x04`**, graphics at **`+0x08`**. The bit layout upstream describes is **correct** | FRAME |
| 31 | "all 10,959 frames declare exactly one piece" | `REFUTED`: 19 frames declare two and 2 declare four; 11,005 pieces over 10,980 frames | FRAME |
| 32 | there is no stored flip/flag field | `REFUTED`: a packed OBJ attribute pair **is** stored at piece `+0x04`; horizontal flip is set on 2,848 pieces. The **rendering effect** is `UNRESOLVED` and the vertical flip is absent from the corpus | FRAME |
| 33 | "unique graphics containers: 7,355" as the corpus total | 7,355 is an exact **subset** - the single-piece-frame set. The corpus reaches **7,390** | FRAME |
| 34 | `declared % 4 == 0` is a container test | `REFUTED`: it rejects 199 genuine selector streams declaring `4k + 2` bytes. It must not appear in project tooling | GFXSCAN |
| 35 | `decoded length == 256` identifies graphics | `REFUTED`: it is a **sort priority**; 244 of 12,990 candidates carry it | GFXSCAN |
| 36 | a decoded non-empty payload is a scan result | `CONFIRMED` as **behaviour**, `REFUTED` as a **container test** | GFXSCAN |
| 37 | the declared-size word seeds the literal base | `REFUTED` from the external source itself (`CompressionState` leaves both fields at 0). An earlier revision claimed the corpus proved it; the corpus **cannot discriminate** it (0 of 11,712 kind-1 containers emit a literal before their first escape) | GFXSCAN |
| 38 | the four-bit code's `value == 0` arm writes the literal base | `REFUTED`: the external source writes a plain literal `0`. This arm is the one that moves a map chunk | GFXSCAN |
| 39 | `GetInteger` "continues while its continuation bit is set" needed arbitration | the probe **is** that reading written from the other side; the claimed refutation was a transposition no source contains | GFXSCAN |

---

## 11. Known production defects and stale assumptions

This is the **authoritative deferred-fix inventory**. Nothing in this section was
fixed by this ticket. Each entry names the defect, the evidence, the required
future behaviour and the risk if it is not fixed.

### 11.1 `webfoot_lz` does not enforce exact declared-size completion

| | |
| --- | --- |
| **File** | `tools/webfoot/formats/webfoot_lz.py` |
| **Class** | `PRODUCTION BUG` (host-side, not an engine-contract violation) |
| **Problem** | the module does not enforce that a packed stream produces exactly its declared size. An over-long final match is silently **clipped** to the declared length and the decode is reported as **successful**, so a caller can receive a truncated payload without any error. A malformed or truncated stream can likewise be returned as apparent success |
| **Reproduction** | `01000000040000000558d020000000c0` (kind 1, declared 4): `webfoot_lz.unpack` accepts and returns 4 bytes; the second implementation refuses with "decoded 15 bytes against a declared 4". Pinned by `test_project_decoder_clips_an_over_long_final_match` |
| **Canonical exposure** | none: the case never arises on the 4,322 reachable canonical containers |
| **Why it matters anyway** | `_unpack_stream`'s own docstring says the function exists to prevent exactly this failure mode. Every later writing capability - graphics replacement, re-encoding, insertion - will trust this decoder. A silent truncation that reports success is the worst possible failure for an authoring tool |
| **Required future behaviour** | strict decoded-size completion: require the decode to produce exactly the declared size and **reject** a stream that does not; report truncation as an error |
| **Risk if unfixed** | a future authoring path can read a corrupted payload as valid and re-emit it, producing a ROM that is wrong in a way no test catches |

### 11.2 `graphics.py::_animations_in` walks past the count-bounded array

| | |
| --- | --- |
| **File** | `tools/webfoot/graphics.py`, method `_animations_in` (line ~684), used by `ActorSprites` |
| **Class** | `PRODUCTION BUG` (bounds), currently **numerically inert** |
| **Problem** | the method walks animation pointers from `+0x54` to the **next structure**, on the stated ground that "no field in this header has been shown to bound the list". That ground is **refuted**: definition `+0x00` (low byte) bounds the array and five engine instructions use it as an index bound |
| **Measured effect** | the walk scans **8,230** slots where the count model scans **4,070**; its 4,160 extra slots are all nonzero and **none is a ROM pointer** (they are the 256-byte remap blocks read as if they were pointers), so the existing pointer filter discards them |
| **Why it still matters** | the justification is wrong and the code is unbounded by construction: it relies on a *filter* to be correct rather than on the engine's own bound. Any future change that relaxes the filter turns 4,160 non-pointer words into candidate animations. Its `1,562` "animation references" is also a per-structure deduplicated count, not the slot count (which is 1,721) |
| **Required future behaviour** | honour definition `+0x00`: read `count` and walk `[+0x54, +0x54 + 4*count)`; restate the two reference-count figures as slot counts |
| **Accepted canonical graphics totals** | **unchanged** by the correction. Every published figure reproduces exactly (`1017 - 4 = 1013`, `13660 - 64 = 13596`, `10964 - 5 = 10959`, `1562` deduplicated), and the reader produces the same animation set for all 297 structures under both models. The regression suite must be updated to prove that rather than to preserve the old count |
| **Risk if unfixed** | a latent unbounded walk in the shipping reader; any later filter change silently corrupts the sprite corpus |

### 11.3 `sprite_graphics.py` still models the refuted 4+16 frame record

| | |
| --- | --- |
| **File** | `tools/webfoot/formats/sprite_graphics.py` |
| **Class** | `PRODUCTION BUG` (stale structure). The `Piece.shape` / `size` / `horizontal_flip` / `vertical_flip` / `dimensions` properties are **kept**; only the offsets move |
| **Defects** | `PIECE_SIZE = 16` (should be `12`); `decode_frame` requires only `offset + 4` for the header and lays pieces out at `offset + 4 + index*PIECE_SIZE` (should be an `0x08` header and `offset + 8 + index*12`); `decode_piece` reads the attribute pair and graphics pointer with one `struct.unpack_from("<II", data, offset + 8)` (should be attributes at `+0x04`, graphics at `+0x08`), which also skips the piece's `+0x02`/`+0x03` extent bytes into the legacy `unknown_raw` field; the `unknown_raw` 6-byte field is the superseded layout; and the docstrings carry the stale **7,355** container figure against the accepted **7,390** |
| **Observed effect today** | `decode_animation` itself needs **no change** (the animation layout is right). `decode_frame`'s `maximum_pieces = 16` is not the binding constraint; the 4+16 walk rejects the 21 multi-piece frames on the size/geometry test, which is exactly why the accepted reader reports 7,355 containers instead of 7,390, and why it needs the 5-frame `_frame_offset` rejection |
| **Required future behaviour** | frame header `8`; piece stride `12`; attribute pair at piece `+0x04`; graphics word at piece `+0x08`; keep the flip/shape/size properties with the offset moved; update the stale figure and the docstrings |
| **Risk if unfixed** | multipart sprites (21 frames, 35 graphics containers) cannot be rendered, edited or re-encoded correctly, and any write path built on the current offsets would corrupt every piece record |
| **Recorded disagreement, not a defect** | LOGX-GFXSCAN-001's follow-up list also names `decode_animation`'s `maximum_frames = 64` as a "known-bad unbounded animation walk". This synthesis does **not** classify it as a defect: `64` is a *bound*, the canonical `frame_count` range is `1..16`, and the same ticker records the animation walk itself as correct (only the definition-side traversal is unbounded). Removing the cap would remove a sanity check with no demonstrated benefit, so the honest disposition is to record the disagreement rather than act on it |

### 11.4 Stale `7,355` figure across shipping code and documentation

| | |
| --- | --- |
| **Files** | `tools/webfoot/graphics.py` (~17, ~20), `tools/webfoot/build.py` (~177, ~284), `tools/webfoot/cli.py` (~545), `tools/webfoot/atlas_producers/seed.py` (~429), `tools/webfoot/formats/sprite_graphics.py` (~25, ~253, ~475), `tools/webfoot/formats/webfoot_lz.py` (~12, ~15, ~354, ~357), `tools/webfoot/data/roms.yaml` (~25), `config/roms.yaml` (~25), `THIRD-PARTY-NOTICES.md` (~41), `docs/architecture.md` (~62), `docs/project-format.md` (~26, ~38, ~52), `docs/research/SUBSYSTEM_MAP.md` (~154, ~160), `docs/research/GRAPHICS_FORMAT.md` |
| **Class** | `STALE DOCUMENTATION` in docstrings, help text, profile comments and the graphics document; the **figures themselves** stay correct as the accepted reader's population |
| **Problem** | `7,355` is presented as the corpus total in several places (module docstrings, CLI help text, the profile's own comment, the document's headline table). It is the **single-piece-frame subset**; the canonical corpus reaches **7,390**. Separately, the module docstrings' "13,588 reachable pieces" and "all frames are single-piece" statements belong to the same refuted layout |
| **Required future behaviour** | restate each figure with its population: "7,390 distinct container offsets are reachable by a piece; 7,355 of them by single-piece frames, which is what the current reader accepts". Do **not** simply replace 7,355 with 7,390 while the reader still cannot see the 21 multipart frames |
| **Risk if unfixed** | users read a subset as the corpus total, and the reader's own blind spot becomes invisible |

### 11.5 Tests that pin the refuted layout

The `TEST EXPECTATION` class from §11.5's vocabulary has concrete members, and
they are **part of this inventory** because a parser correction that leaves them
alone will fail its own regression suite:

| File | Pins | Moves with |
| --- | --- | --- |
| `tests/integration/test_graphics_rom.py` | `UNIQUE_GRAPHICS = 7355` (`:40`) and four dependants (`:74`, `:409`, `:498`, `:519`) | `FIX-2` (then 7,390) and `FIX-5` |
| `tests/unit/test_logx_sprite_reference.py` | `probe.FRAME_FIRST_PIECE == 0x04` (`:142`) and `probe.PIECE_RECORD_SIZE == 0x10` (`:143`) | the research probe, or the expectation, whichever is corrected first |
| `tests/unit/test_sprite_graphics.py` | a 4-byte-header frame fixture (`:172`, `:185`) and 16-byte `_piece_bytes` (`:125-127`) | `FIX-2` |

**These expectations are not to be deleted when the parser is corrected** - they
are to be re-pointed at the accepted layout, so the correction is pinned by the
same tests that currently pin the defect. That is the acceptance condition
`FIX-2` carries.

### 11.6 `atlas_producers/scan.py::_compression_rows` is a noisy heuristic sweep

| | |
| --- | --- |
| **File** | `tools/webfoot/atlas_producers/scan.py` |
| **Class** | `PRODUCTION BUG` (output quality), **outside the SDK's canonical path** |
| **Problem** | `_compression_rows` is a **stride-4 heuristic sweep** for container headers. Its own docstring calls its output noise, and the shipped atlas evidence records the scale as **24,285 hits / 68.7 MiB**, "overwhelmingly probe noise" |
| **Why it is inventoried rather than fixed** | LOGX-GFXSCAN-001 recorded it as a production follow-up and noted it "is unaffected by this ticket and remains out of the SDK's canonical path". It produces atlas *rows*, not decoded resources, so it cannot corrupt a read or a write; but it is user-visible atlas content |
| **Required future behaviour** | decide its fate explicitly: gate it behind a research flag, replace it with a reference-driven producer over the accepted graphs (which this synthesis now fully specifies), or delete it. **Do not leave it as an unlabelled default** |
| **Risk if unfixed** | a user reading atlas output cannot distinguish a real resource row from sweep noise; the module's own docstring concedes this, so the defect is disclosure and default behaviour rather than silent corruption |

### 11.7 Repository-wide stale-assumption audit

See §11.8 for the mechanical result. **Classification vocabulary** used, and
what it means here:

| Class | Meaning |
| --- | --- |
| `PRODUCTION BUG` | live code under `tools/webfoot/` or `src/` that would produce a wrong result for a user |
| `STALE DOCUMENTATION` | current canonical documentation that still asserts a refuted claim as current |
| `RESEARCH-ONLY LEGACY` | files under `tools/research/`, or historical/provenance/ticket records that intentionally preserve the old text as evidence |
| `TEST EXPECTATION` | an assertion that encodes a refuted value |
| `HARMLESS COMMENT` | prose that does not drive behaviour |
| `NO LONGER USED` | dead or unreachable code |

**Historical records are deliberately not edited.** The review, provenance and
archive documents for the ten tickets quote the superseded wording in order to
refute it, and that is the evidence trail. Editing them would destroy the record
of what was believed and corrected. This synthesis therefore audits **live code
and current canonical documentation**, and leaves the historical records intact.

### 11.8 Mechanical audit result

Run:

```text
python -m tools.research.logx_synthesis_audit
```

`tools/research/logx_synthesis_audit.py` scans the in-scope globs for every
superseded pattern in §10 that can be recognised mechanically, and reports each
surviving hit with its `file:line`, the pattern key and one line of context. On
this revision it reports **20 surviving hits, 5 of them in live code**
(`sprite_graphics.py` and `graphics.py`), and **every one of them is a defect
already inventoried above** in §11.1-§11.4 - the instrument's purpose is to make a
new one visible, not to reach zero. It exits `1` while any finding remains, which
is why the test asserts the finding *set*, not the exit code.

The audit is reviewed by `tests/unit/test_logx_synthesis_audit.py`, which asserts
that (a) **no superseded hit exists anywhere in the scan scope outside the
recorded defect files**, (b) inside `tools/webfoot/**` every surviving hit uses a
pattern the synthesis already classifies, and (c) the five production hits are
exactly the recorded ones, so neither a new defect nor a silent disappearance
passes. Hits that are inside a dated correction note ("superseded", "refuted",
"added later", "corrected") are history and are filtered out by design.

**Two limits of the instrument, stated rather than implied.** Its globs cover
`tools/webfoot/**/*.py`, `tools/webfoot/data/*.yaml`, `config/roms.yaml`,
`THIRD-PARTY-NOTICES.md` and `docs/research/GRAPHICS_FORMAT.md`; the wider
documentation sweep that found `docs/architecture.md`, `docs/project-format.md`
and `docs/research/SUBSYSTEM_MAP.md` was performed by hand for this ticket, and
those files are named in §11.4 and in `FIX-5` so the next pass does not have to
rediscover them. And `docs/research/GRAPHICS_FORMAT.md` is exempt while its
`SUPERSEDED STATEMENTS` banner stands - the exemption is conditional on the
banner markers being present, so deleting the banner re-arms the scan.

---

## 12. Unresolved research questions

Only genuinely unresolved items. Anything the queue settled is in §2-§9; this
list is the input to §13 (does it block anything?) and §17 (does it need a
ticket?).

| # | Question | Where it lives |
| --- | --- | --- |
| 1 | connector interval **axis**, **origin**, **units**, **signedness**, **edge inclusivity** and the exact **region-membership test** | CONNECTOR: no coordinate comparison against the four `u16` was recovered |
| 2 | connector **spawn / arrival position** and **facing / direction** | CONNECTOR |
| 3 | the meaning of the two connector record **classes** (`+0x00` = `0x08007675` / `0x080072CD`) and of `+0x04` = `0x0800776D` | CONNECTOR: no class-table walk recovered |
| 4 | the semantics of connector `+0x10`, `+0x13`, `+0x14`, `+0x16`, `+0x17` | CONNECTOR |
| 5 | the entry path that reaches the record consumer `0x080071F8` (no direct `bl` caller, not in any literal pool) | CONNECTOR |
| 6 | the origin of LOGExtractor's connector `+8` | CONNECTOR |
| 7 | which selector values other than `1` the engine ever passes, and what chooses them (55 of 452 MapEntries expose multi-word source arrays) | MAP-RENDER |
| 8 | the instruction that reads `root+0x0C`/`+0x10` out of the root (the "animated tiles" pair) | MAP-RENDER / TILE |
| 9 | the semantic role of tile bits 12-15: reserved by the format, or merely inert under the 8bpp BG configuration | TILE |
| 10 | what an internal null chunk pointer in the `+0x18` window displays: the constructor skips it, the streaming path substitutes the default container `0x08070808` | LAYER / TILE |
| 11 | **layer positioning**: what consumes `+0x0C`, `+0x0E`, `+0x10`, `+0x12`, and what consumes `object+0x0C` (the copied `+0x16`) | LAYER |
| 12 | whether the `0x0800897B` class is a layer at all, and the full semantics of the `0x08007B63` / `0x080088BD` singletons | LAYER |
| 13 | whether an internal null chunk pointer means "skip" or "default" | LAYER |
| 14 | the meanings of an animation's **two trailing words**, and whether a trailer exists at all given the 30 table-end frame-record aliases | FRAME |
| 15 | the **screen-space orientation** of the four direction values and of the compared coordinates | FRAME: only the sign/axis split is `CONFIRMED` |
| 16 | sprite piece **position origin** and axis assignment; the anchor-adjacent computation at `0x0800F0EA`/`0x0800F106`/`0x0800F132` (`obj+0x6C`/`obj+0x70`) | FRAME |
| 17 | whether a loop mode is selected by any animation field; terminal and ping-pong behaviour | FRAME |
| 18 | what `definition + 0x0C` and `definition + 0x10..+0x4F` hold; what the 256-byte block at `definition - 0x100` is for; what `definition + 0x50`'s parallel array holds beyond the 10 objects that have one | SPRITE |
| 19 | which game states the 25-entry state table's `0..24` correspond to, and whether any producer passes a state above 24 or an index at or above a definition's count | SPRITE |
| 20 | the animation **semantic slot names**: four positions have an engine-visible role, the rest are `UNRESOLVED` | SPRITE |
| 21 | the higher-level meaning of appearance `+0x0C`'s target records, and whether values `142..149` are valid records | CHAR |
| 22 | what `f(0x92)` / `f(0x95)` denote inside `0x08027948` | CHAR |
| 23 | which of the 232 appearance records are ever activated by the runtime bitmap, and what a variant family means | CHAR |
| 24 | the packed decoder's **initial literal width** (immaterial for decoding; load-bearing for a naive encoder) | CODEC |
| 25 | which termination rule the hardware obeys when a stream's end marker and the declared size disagree (no canonical container exercises it) | CODEC |
| 26 | whether the engine's codec is byte-compatible with any specific JCALG1 reference implementation | CODEC |
| 27 | the consumer of the **387 referenced, packed residual containers**, and the meaning of the pointer structure around `0x087B5B64` | GFXSCAN. **Partly answered by this synthesis** (§12.1): `0x087B5B64` is the known `compressed_text` selector table and covers 6 of the 387; the remaining 177 sit in two size-locked pointer tables with no nameable consumer. The residual question is now narrowed, not closed |
| 28 | **portrait recall** for the external scanner, and portrait pixel format / dimensions | GFXSCAN / CHAR |
| 29 | **is the appearance table's fixed count of 232 reloadable by the engine, or is it a compile-time constant?** The table has no terminator, its count appears as three `cmp rN,#0xE8` loop bounds, and the runtime roster walk is bounded by a 232-bit bitmap | CHAR: the one genuinely unresolved item behind `AUTHOR_NEW` appearance creation (`NEW-3`), and a **research** question rather than an engineering one |
| 30 | MapEntry's DragonByteZ-labelled fields: `output`, `zone`, `area`, `variation`, the five counts, `flags`, `music_id` and the eight remaining pointer words | MAP-RECORD: upstream labels, `INFERRED`/`UNKNOWN` |

### 12.1 The 387 referenced residuals - bounded investigation result

The queue handed synthesis one concrete lead: the pointer/reference structure
around **`0x087B5B64`**, which names several of the largest of the 387 packed,
engine-referenced residual containers. This synthesis ran a **bounded**
investigation against that lead. Method, measurements and limits are in
[`LOGX_SYNTHESIS_PROVENANCE.md`](LOGX_SYNTHESIS_PROVENANCE.md) §3.

```text
RESIDUAL CLASSIFICATION:  UNCLASSIFIED - needs a targeted ticket
  6   / 387 : ALREADY-KNOWN FAMILY `compressed_text`
  177 / 387 : two size-locked data-region pointer tables, family UNKNOWN
  204 / 387 : cited only by short runs or isolated words
FOLLOW-UP TICKET:         LOGX-RESTABLE-001 (see §17)
```

**The `0x087B5B64` lead is answered, and by pre-existing records rather than by
new archaeology.** The structure is exactly **seven** word-aligned in-ROM
pointers (`0x087B5B64..0x087B5B7C`, 28 bytes) that point **directly** at container
headers (all form 1, no indirection), and the boundary is real: of the 18 words
after it, only one is an in-ROM pointer and the next four are EWRAM addresses. It
is the **`compressed_text` (dialogue text store) selector table**, already
documented as `compressed_text.pointer_table` in the shipped atlas evidence
(`tools/webfoot/atlas_producers/seed.py:686-704`, "STRUCTURAL GATE: exactly 7
containers") and in `docs/research/BUU_MAP_EVENT_REFERENCES.md`, TEXT-HANDLE-001/
002, ROM-EXPAND-001 and TEXT-INDEX-001. Its consumer is **`0x080123CC`**, the
single literal shared by the two documented `compressed_text` consumers
`0x08012230` (`RUNTIME_CONFIRMED`, 65 live hits) and `0x080122B4`
(`CONFIRMED` static). **Do not call these 387 members of a new family: six of
them are a subsystem this project already reads.**

**The other 177 sit in two size-locked pointer tables** whose *structure* is
established and whose *semantic family is not*:

| Table | Words | Members in the 387 | Declared size |
| --- | ---: | ---: | --- |
| `0x086F395C..0x086F3BC4` | 155 consecutive | 95 | **all exactly 4,096** |
| `0x082ABF08..0x082AC134` | 140 consecutive | 82 | **all exactly 1,024** |

Neither table's base is named by any word in the image (whole-image sweep count
**0** for both), so the base is **computed or folded** and no consumer is
reachable through the pointer/literal model. The only code-region citation sites
for any of the 387 are `0x08004EFC`, `0x08028118` and `0x0802837C`.

**Size distribution, re-measured and corroborating GFXSCAN exactly:** min 128,
max 65,474, median 1,024, mean 3,017.66; `256 x129`, `4,096 x97`, `1,024 x88`,
`2,048 x24`, `8,192 x16`, 33 others; **26 reach 8 KiB**. All 387 decode to exactly
their declared size. **381 of 387 decoded lengths are divisible by 32, and the 6
exceptions are exactly the 6 `compressed_text` members** - so "non-whole-tile"
and "the already-known text store" are the same set, and 32-byte divisibility is a
necessary condition, nowhere near a sufficient one.

**No graphics semantic and no new canonical resource class is claimed for the
387.** They are not one family.

---

## 13. Does each unknown actually block a product goal?

Not every unresolved field deserves another archaeology ticket. The
**Vertical-Slice-First Rule** applies: an unknown earns a ticket only when it
provably blocks a named authoring operation. Classification below:

- **BLOCKS CURRENT PRODUCT GOAL** - a shipping capability the roadmap needs next
  cannot be built without it;
- **BLOCKS ONLY ADVANCED AUTHORING** - only `AUTHOR_NEW` for that class;
- **DOES NOT CURRENTLY BLOCK** - the planned capability does not read the field;
- **FORENSIC CURIOSITY ONLY** - no planned capability needs it.

| # | Unknown | Classification | Reasoning |
| --- | --- | --- | --- |
| 1 | connector geometry axes/origin/units/signedness/inclusivity | **BLOCKS ONLY ADVANCED AUTHORING** | only **trigger-region authoring** needs it. Destination editing and randomization do not |
| 2 | connector spawn / facing | **BLOCKS ONLY ADVANCED AUTHORING** | a destination key selects a map; the engine supplies the arrival position by a route this queue did not need |
| 3-4 | connector record classes and `+0x10`/`+0x13`/`+0x14`/`+0x16`/`+0x17` | **DOES NOT CURRENTLY BLOCK** | a destination rewrite preserves all of them byte-exactly |
| 5-6 | consumer entry path `0x080071F8`; LOGExtractor's `+8` | **FORENSIC CURIOSITY ONLY** | neither is needed to read, edit or randomize a destination |
| 7 | other selector values | **DOES NOT CURRENTLY BLOCK** | the accepted render path uses selector 1; a tool can read and edit what the engine actually selects |
| 8 | the instruction reading `root+0x0C`/`+0x10` | **DOES NOT CURRENTLY BLOCK** | the pair is identified, null-coupled, and its record loader and VRAM target are established. Editing it is out of the near roadmap |
| 9 | tile bits 12-15 role | **FORENSIC CURIOSITY ONLY** | zero in all 3,834,880 canonical entries; an editor must preserve them, which requires no semantics |
| 10 | null chunk pointer display | **DOES NOT CURRENTLY BLOCK** | 117 records have one; a tool that reads the engine's own default (`0x08070808`) is correct without naming it |
| 11-13 | layer positioning, other handler classes, null meaning | **BLOCKS ONLY ADVANCED AUTHORING** | only **new layer authoring / map position authoring** needs positioning. Tile *data* editing does not: the chunk payload is fully understood |
| 14 | animation trailing words | **DOES NOT CURRENTLY BLOCK** | preserving two unknown words byte-exactly needs no semantics. It becomes a blocker only for **creating a new animation**, which is `AUTHOR_NEW` |
| 15 | direction screen orientation | **DOES NOT CURRENTLY BLOCK** for editing; **BLOCKS ONLY ADVANCED AUTHORING** for tooling that must label a direction to a user | an editor can present numbered cells; a *named* direction is a UX claim nobody proved |
| 16 | piece position origin | **BLOCKS ONLY ADVANCED AUTHORING** | preserving offsets and extents is enough to replace graphics; authoring a *new* piece that lands correctly needs the origin |
| 17 | loop mode / terminal behaviour | **DOES NOT CURRENTLY BLOCK** | playback preview can show frames sequentially and say so |
| 18-19 | sprite definition unknowns, state mapping | **DOES NOT CURRENTLY BLOCK**; **BLOCKS ONLY ADVANCED AUTHORING** for a new definition | reading a definition, its count and its array is complete |
| 20 | animation slot names | **DOES NOT CURRENTLY BLOCK** | a UI may show index, occupancy and a preview. Naming a slot would be an invented semantic |
| 21-23 | appearance `+0x0C` target meaning, `f(0x92)`/`f(0x95)`, roster activation, variant families | **DOES NOT CURRENTLY BLOCK** for text-reference editing and for reading; **BLOCKS ONLY ADVANCED AUTHORING** for a *new* appearance definition | preserving `+0x0C` byte-exactly is enough to edit text references |
| 24-26 | decoder initial literal width, disagreement rule, exact JCALG1 identity | **BLOCKS CURRENT PRODUCT GOAL** for the **encoder** | an encoder must emit streams the engine decodes; the requirements are `PARTIAL` and the two open items must be resolved or worked around before packed emission is trusted. Note the workaround exists: emit your own opening escape and self-verify by exact round-trip |
| 27 | the 387 residuals' consumer | **DOES NOT CURRENTLY BLOCK** | see §12.1. It matters only if the residual family turns out to be a useful authoring class |
| 28 | portrait recall and portrait pixel format | **BLOCKS ONLY ADVANCED AUTHORING** (portrait import); `DOES NOT CURRENTLY BLOCK` for reading the portrait *pointer* | see §16 |
| 29 | is the appearance table's count of 232 reloadable? | **BLOCKS ONLY ADVANCED AUTHORING** | nothing in the near roadmap grows the table; it blocks only `NEW-3` (a new appearance definition) and is why that ticket is `research + engineering` |
| 30 | MapEntry upstream-labelled fields | **DOES NOT CURRENTLY BLOCK** | the accepted discovery route uses `+0x00`, `+0x0C` and `+0x2C` only. A metadata editor must preserve the other bytes, which needs no semantics |

> **The reasoning this table exists to encode:** *connector destination
> randomization does not require fully understanding the trigger rectangle.*
> That single example removes the largest apparent blocker from the near
> roadmap. Endless reverse engineering is avoided by asking, per field, which
> named operation actually reads it.

---

## 14. Read-support matrix

Vocabulary: `TRUSTED`, `TRUSTED WITH KNOWN FIX`, `PARTIAL`, `RESEARCH ONLY`.
**"Read support" is not write support**: a `TRUSTED` row may still be
`BLOCKED BY UNKNOWN SEMANTICS` for authoring in §15.

| Resource | Discovery root | Structure confidence | Field confidence | Read support | Current project implementation | Known bugs | Authoring readiness | Follow-up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- read-support-matrix -->
| MapEntry | `0x0808E2E0`, fixed 452 x `0x38` | `CONFIRMED` | `PARTIAL` (`+0x00`/`+0x0C`/`+0x2C` confirmed) | `TRUSTED` for `+0x00`, `+0x0C`, `+0x2C` | `tools/webfoot/formats/map_entry.py` | none found | `SAFE AFTER BOUNDED FIX` for metadata edits | none |
| map root / template | `MapEntry+0x2C + 4*(selector-1)` | `CONFIRMED` | `PARTIAL` | `TRUSTED` (`+0x0C`/`+0x10` is an unrecovered consumer, not a defect) | `tools/webfoot/map_render.py`, `map_slots.py` | none confirmed | `SAFE AFTER BOUNDED FIX` for reading; `PARTIAL` for editing | none |
| dominant layer record | root `+0x14`/`+0x18`/`+0x1C`/`+0x20` | `CONFIRMED` | `PARTIAL` (grid dims confirmed; position unknown) | `TRUSTED WITH KNOWN FIX` (dominant handler only) | `tools/webfoot/map_render.py` | applicability must stay scoped to `0x08008087` | `SAFE AFTER BOUNDED FIX` for tile data; `PARTIAL` for position | none |
| tile chunk | layer `+0x18 + 4*i` | `CONFIRMED` | `CONFIRMED` (1024 u16, 32x32, bits 0-9; bits 12-15 reserved) | `TRUSTED` | `tools/webfoot/formats/map_chunks.py`-family reader | none confirmed | `SAFE AFTER BOUNDED FIX` (replace data in place) | none |
| selector stream | root `+0x48` | `CONFIRMED` | `CONFIRMED` (recurrence and packed pair) | `TRUSTED` | `tools/webfoot/map_render.py` | none confirmed | `SAFE AFTER BOUNDED FIX` | none |
| bank resource | `root+0x4C` -> `0x08179764`, 187 entries | `CONFIRMED` | `PARTIAL` (bank/tile split confirmed; "graphics identity" unresolved) | `TRUSTED` | `tools/webfoot` atlas path | none confirmed | `PARTIAL RESEARCH REQUIRED` | none |
| connection record | root `+0x40`/`+0x44` | `CONFIRMED` | `CONFIRMED` for destination bytes and the interval ordering; `PARTIAL`/`UNRESOLVED` for the rest | `TRUSTED` | none (research tooling only: `tools/research/logx_connector_probe.py`) | none | `SAFE AFTER BOUNDED FIX` for destination edits | `CONNECTOR-GEOMETRY` only if trigger authoring is needed |
| Webfoot container | engine-reachable pointer or `root+0x48`/`+0x4C` | `CONFIRMED` | `CONFIRMED` for hand-rolled consistency | `TRUSTED WITH KNOWN FIX` (declared-size enforcement) | `tools/webfoot/formats/webfoot_lz.py` | clipping accepted as success | `SAFE AFTER BOUNDED FIX` for stored; `BLOCKED BY UNKNOWN SEMANTICS` for packed emission | `CODEC-WRITE` |
| appearance definition | `0x0874D380`, 232 x `0x10` | `CONFIRMED` | `CONFIRMED` physical; `PARTIAL` semantic | `TRUSTED` | none (research tooling only: `tools/research/logx_char_probe.py`) | none | `SAFE AFTER BOUNDED FIX` for text-reference edits | none |
| portrait lookup | appearance `+0x08` -> `0x086F393C` | `CONFIRMED` (pointer relationship) | `PARTIAL` (no pixel format, dimension or render claim) | `TRUSTED` for the pointer; `PARTIAL` for the resource (no defect) | none | none | `PARTIAL RESEARCH REQUIRED` for import; `SAFE NOW` for pointer inspection | `PORTRAIT-FORMAT` if import is required |
| sprite definition | `0x086B6BDC`, 297 entries, ids 10..306 | `CONFIRMED` | `CONFIRMED` for `+0x00`, `+0x02`, `+0x04`, `+0x50`, `+0x54`; `UNRESOLVED` for `+0x08`, `+0x0C`, `+0x10..+0x4F` | `TRUSTED WITH KNOWN FIX` | `tools/webfoot/graphics.py` (walker) | `_animations_in` unbounded walk | `SAFE AFTER BOUNDED FIX` for animation-pointer edits | none |
| animation object | definition `+0x54 + 4*index` | `CONFIRMED` | `CONFIRMED` for `frame_count` and the cell table; trailing words `UNRESOLVED` | `TRUSTED` | `tools/webfoot/formats/sprite_graphics.py::decode_animation` | none | `SAFE AFTER BOUNDED FIX` for replacing pointers | none |
| frame record | animation cell | `CONFIRMED` | `CONFIRMED` (header, bounding box, piece count) | `TRUSTED WITH KNOWN FIX` | `sprite_graphics.py::decode_frame` | 4-byte header assumption, 16-byte stride | `SAFE AFTER BOUNDED FIX` | none |
| sprite piece | frame `+0x08 + 12*i` | `CONFIRMED` | `CONFIRMED` for `+0x00`..`+0x04` and `+0x08`; origin `UNRESOLVED` | `TRUSTED WITH KNOWN FIX` | `sprite_graphics.py::decode_piece` | attribute and graphics offsets both stale | `SAFE AFTER BOUNDED FIX` for replacement | none |
| graphics container | piece `+0x08` | `CONFIRMED` | `CONFIRMED` (declared size equals `dim_0*dim_1` on 11,005/11,005) | `TRUSTED WITH KNOWN FIX` | `webfoot_lz.unpack`, `sprite_graphics.decode_graphic` | declared-size enforcement | `SAFE AFTER BOUNDED FIX` for replacement in place | none |

**Project implementation coverage.** Four of the fifteen classes have **no**
project implementation at all: connection records, appearance definitions,
portrait lookup and (as a first-class reader) the animation/frame/piece chain
outside `graphics.py`. They exist only as SHA-gated research probes. That is an
**engineering** gap, not a research one.

---

## 15. Authoring-readiness matrix

Vocabulary: `SAFE NOW`, `SAFE AFTER BOUNDED FIX`, `PARTIAL RESEARCH REQUIRED`,
`BLOCKED BY UNKNOWN SEMANTICS`.

| Capability | Classification | Why |
| --- | --- | --- |
<!-- authoring-readiness-matrix -->
| edit existing map metadata | `SAFE AFTER BOUNDED FIX` | `+0x00`, `+0x0C`, `+0x2C` are `CONFIRMED` and fixed-size, so an in-place rewrite of those fields moves nothing. A tool must preserve the remaining 43 bytes byte-exactly. The bounded fix is the metadata reader plus round-trip proof |
| edit existing layer/chunk tile data | `SAFE AFTER BOUNDED FIX` | the chunk payload is fully `CONFIRMED` (1024 u16, 32x32), so editing entries in place is a byte rewrite inside a fixed 2048-byte payload. The bounded fix is the 8+12 frame/piece parser (independent of this path) and a round-trip proof. **Two binding constraints, not one:** the replacement must fit the container's declared decoded size **and**, for a packed container, the re-encoded stream must fit `packed_end - offset` - the byte extent the decoder actually consumed (§5.3). A chunk whose content does not re-encode smaller than the original does **not** fit in place and needs the allocator |
| replace existing tile data | `SAFE AFTER BOUNDED FIX` | as above: the replacement must fit both the declared decoded size and the measured `packed_end - offset`. Replacing a `0x800` chunk with content that re-encodes no larger is safe; changing the size, or exceeding the encoded extent, requires the writer and the allocator |
| new map data / `AUTHOR_NEW` map | `BLOCKED BY UNKNOWN SEMANTICS` | needs layer positioning (unknown), selector semantics above 1 (unresolved), the `+0x0C`/`+0x10` consumer (unrecovered), the `+0x24`/`+0x28` object types (unknown), and a verified allocator for every new structure plus five pointer/count updates per root |
| edit existing warp destination | `SAFE AFTER BOUNDED FIX` | two bytes in a fixed 24-byte record; no size change, no pointer move, no count update. Validation: the new pair must resolve through `0x080089FC`. Bounded fix = a connection-record reader/writer plus the resolve check |
| warp randomizer | `SAFE AFTER BOUNDED FIX` (structural) | same write as above, plus a deterministic permutation policy. `GAMEPLAY LOGIC / SOFTLOCK VALIDATION` is a **separate, later** problem (see §14 of the roadmap) |
| edit warp trigger geometry | `BLOCKED BY UNKNOWN SEMANTICS` | axis, origin, units, signedness and edge inclusivity are all `UNRESOLVED`, and no membership test was recovered. A tool cannot describe or validate a proposed region |
| create new warp | `BLOCKED BY UNKNOWN SEMANTICS` | three independent obstacles: un-inventable class pointers at `+0x00`/`+0x04`; a non-null-terminated array whose count/pointer pair is null-coupled on 452/452 roots; and the `root + 0x44 == root - 4*count` corpus layout, where a grown array may overwrite the bytes immediately below the root |
| edit appearance text references | `SAFE AFTER BOUNDED FIX` | `+0x00`/`+0x02` are two `u16` indices in a fixed 16-byte record. Bounded fix: a record reader/writer and a range check against the 1,534-entry text table. **Editorial invariant to surface to the user:** `+0x02 == +0x00 + 1` holds on all 232 records but is a *data* invariant, not an engine rule - changing one field alone makes the image diverge from the corpus |
| edit sprite-definition animation pointers | `SAFE AFTER BOUNDED FIX` | `+0x54 + 4*index` elements are fixed-width pointers inside a variable-length object. Replacing a pointer changes no size. Bounded fix: honour the `+0x00` count bound and validate each new pointer as an in-ROM animation. **Second coupling to respect:** when `definition + 0x50` is non-null (10 of 297 objects) the *same index* also selects `definition[0x50][index]` into `obj+0x4C`, and that entry's meaning is `UNRESOLVED` - so an editor must either leave `+0x54` alone for those definitions or present the pair as one edit, and must not silently desynchronise them |
| replace animation/frame data | `SAFE AFTER BOUNDED FIX` | animation objects and frame records are fixed-size given their counts. Replacing an animation's cell pointers or a frame's pieces in place, at the same counts, moves nothing. The bounded fix is the 8+12 parser |
| replace sprite graphics | `SAFE AFTER BOUNDED FIX` | `piece +0x08` points at a container whose declared size **must** equal `dim_0 * dim_1`. Replacing a container with one of the *same decoded size* is a byte rewrite. A different size needs the encoder and an allocator |
| import new sprite graphics | `BLOCKED BY UNKNOWN SEMANTICS` | requires (a) a trusted packed encoder (currently `PARTIAL`: initial literal width unresolved, no production encoder) and (b) a verified allocator for new container bodies and for the pointers that name them. This is `NEEDS ENGINEERING` **and** `NEEDS RESEARCH` |
| create new animation | `PARTIAL RESEARCH REQUIRED` | the animation object layout is `CONFIRMED`, but a *new* animation needs a home (allocation), two trailing words whose meaning is `UNRESOLVED`, and a definition slot to point at it. Creating one that only reuses existing frames is closer than creating a new animation record body |
| create new appearance definition | `PARTIAL RESEARCH REQUIRED` | the record layout is `CONFIRMED` and fixed-size, but the table has a **fixed count of 232 with no terminator**, so a new record requires table growth, relocation and every `index << 4` site to follow. `+0x0C`'s target meaning is also `UNRESOLVED`, so a new record cannot be given a stat record with confidence |
| insert new compressed resource | `BLOCKED BY UNKNOWN SEMANTICS` | needs a trusted encoder (`PARTIAL`) **and** a verified allocator **and** a relocation strategy for every pointer that names the resource. No allocator is integrated in this worktree's scope |
| encode new packed Webfoot container | `PARTIAL RESEARCH REQUIRED` | the wrapper and the decoded-size field are `CONFIRMED` and the grammar is `CONFIRMED` enough to decode the whole corpus; what is open is the initial literal width, the marker-vs-size disagreement rule, and the fact that no production encoder exists. `webfoot_lz.pack` produces valid streams with a **measured size penalty** |
| portrait replacement/import | `PARTIAL RESEARCH REQUIRED` | the pointer relationship is `CONFIRMED` and the consumer is the container dispatcher, but no pixel format, dimension or rendering claim was established, and GFXSCAN never measured portrait recall. Replacing a portrait whose format is already known is closer than importing a new one |
| new dialogue/script content | `NOT APPLICABLE` to LOGX | dialogue and script authoring are outside this research queue and have their own accepted work. This synthesis adds no claim about them |

> **Rule applied throughout:** **writing requires more than reading.** Every
> `SAFE AFTER BOUNDED FIX` row above is read-`TRUSTED` but its write path still
> needs allocation, bounds, relocation, count updates, encoding and runtime
> invariants *where applicable* - and an **in-place, same-size rewrite** is the
> only class where all of those collapse to "no size change, no pointer move, no
> count update". That is why in-place replacement is rated so much higher than
> creation throughout this table.

---

## 16. Portrait coverage decision

**`PORTRAIT GFXSCAN RECALL: UNMEASURED / NON-BLOCKING`.**

Reasoning, so the decision is checkable rather than asserted:

- the portrait **pointer path** is already structurally sufficient for the
  implementation roadmap: appearance `+0x08` is a `u32` index into the
  163-slot array at `0x086F393C`, `0x08011F20` resolves it (returning `0` for
  slots `0` and `7` without reading the array and taking a party-record path for
  slots `1..6`), the canonical value set is `{0}` plus a 110-element subset of
  `8..162`, and the result is consumed as a Webfoot container at `0x080250D6`.
  A tool can therefore **enumerate, read and identify** every portrait the
  canonical table references **without** a scanner recall measurement;
- portrait recall measures **the external scanner's** coverage, not the engine's
  structure. It is a property of a tool this synthesis rates
  `FORENSIC / RESEARCH TOOL: YES, CANONICAL ENUMERATOR: NO`. A missing recall
  figure does not weaken the engine-derived portrait path;
- the one measurement that **would** matter, portrait graphics' pixel format and
  dimensions, is a different question from recall and is `UNRESOLVED` (§12 #28).
  It is a **portrait-format** question, and this ticket is explicitly forbidden
  from becoming a portrait-format research ticket.

Therefore the missing recall figure is recorded as a **known, non-blocking
limitation** rather than closed by a new measurement. If portrait **import** or
**replacement** is later scheduled, the dependency is
[`PORTRAIT-FORMAT`](#17-targeted-follow-up-research-tickets), which is a
structural question, not a recall one.

---

## 17. Targeted follow-up research tickets

Only four are recommended, and each is tied to a named blocked capability. A
ticket that cannot complete the sentence "this blocks the SDK from authoring
____" stays parked.

| Ticket | Blocks | Why it is necessary | Minimum evidence | Priority |
| --- | --- | --- | --- | --- |
| **`LOGX-CONNECTOR-GEOMETRY-001`** | **arbitrary new warp trigger authoring**; map position authoring generally | the four `u16` are `CONFIRMED` only as two ordered intervals. Axis, origin, units, signedness, edge inclusivity, the membership test and the spawn mechanism are all `UNRESOLVED`. No amount of engineering can substitute: there is nothing to validate a proposed region against | a runtime capture that places the player at a known coordinate inside and outside a record's interval and observes whether the `0x08008B30` install fires (`docs/runtime-capture.md` path), plus the consumer entry path `0x080071F8` | **only when trigger authoring is scheduled.** Destination editing and randomization do **not** need it |
| **`LOGX-CODEC-WRITE-001`** | trustworthy packed-resource emission: new sprite graphics, inserted resources, any size-changing container write | the encoder format is `PARTIAL`: the initial literal width is `UNRESOLVED`, no production encoder exists, and `webfoot_lz.pack` has a measured size penalty. The engine performs **no** validation, so a bad stream is not caught at runtime | an encoder that emits a stream, decodes it back, and requires exact round-trip equality of bytes, declared size **and** end-marker position; plus a decision on the initial literal state that does not rely on the unresolved dispatcher value | **high** - it is the gate for every "insert" capability and for `AUTHOR_NEW` graphics |
| **`LOGX-PORTRAIT-FORMAT-001`** | portrait replacement / import | the pointer relationship is `CONFIRMED` but the resource behind it was never characterised: no pixel format, no dimensions, no rendering claim, and no portrait recall measurement | enumerate `0x086F393C`'s 155 valid pointers as a known-positive class, decode each, and establish the pixel format and dimensions from the piece/consumer side | **only when portrait import is scheduled.** Non-blocking today (§16) |

**Parked, not recommended** (deliberately, to avoid endless reverse
engineering). A parked item does **not** complete the Vertical-Slice-First
sentence "this blocks the SDK from authoring ____", so it is recorded and left:
`LOGX-RESTABLE-001` (the two size-locked residual tables have no consumer and no
planned capability needs them; revisit only if that family turns out to be
useful). The same treatment applies to:
tile bits 12-15 semantics (forensic), LOGExtractor's `+8` (forensic), the
connector record classes (does not block an in-place destination rewrite), the
animation trailing words (preserving two unknown words needs no semantics),
animation slot names (naming them would be an invented semantic), and MapEntry's
upstream-labelled metadata fields (the accepted route does not use them).

---

## 18. `AUTHOR_NEW` gap analysis

For each known `AUTHOR_NEW` dependency, classified as `SOLVED`,
`STRUCTURALLY SOLVED`, `PARTIAL`, `UNRESOLVED`, `IMPLEMENTATION ONLY`.

| Dependency | Classification | Detail |
| --- | --- | --- |
| verified ROM allocation | `IMPLEMENTATION ONLY` | free-space discovery and relocation are established work elsewhere in the project (`FREE_SPACE_RELOCATION.md`, `ROM_EXPANSION.md`, `BUU_VERIFIED_CAPACITY.md`). Nothing in this queue blocks it, and this queue adds no allocator requirement beyond "carry the container's `packed_end`" |
| materialising new entity/resource bodies | `PARTIAL` | the *sizes* are known for every structure this queue studied (container, chunk, frame, piece, animation, definition, appearance record). What is not built is a writer that materialises them; that is `IMPLEMENTATION ONLY` per class |
| pointer/table expansion | `UNRESOLVED` | three concrete blockers: the layer chunk-pointer array's length is derived from `+0x14 * +0x15` **bytes** (so growing a layer means editing dimension bytes and relocating the window); the connection array is non-null-terminated with a null-coupled count, and `root + 0x44 == root - 4*count` means growth may collide with the bytes below the root; the appearance table has a **fixed count of 232 with no terminator**, so a 233rd record requires table growth and every `index << 4` site to follow. None of these is a *research* unknown for the layer and connection cases - they are relocation engineering - but the **appearance table's growth story is genuinely unresolved** because the count appears as **three** `cmp rN,#0xE8` loop bounds, in a table with no terminator, while **eight** separate sites load the base and apply the `index << 4` scale and the runtime roster walk is bounded by a **232-bit bitmap** |
| map data | `PARTIAL` | the schema is `CONFIRMED` for the accepted subset, but a new map needs the unresolved items in §12 (#7, #8, #11, #12) |
| tiles | `STRUCTURALLY SOLVED` | a chunk is fully understood: 2048 bytes, 1024 u16, 32x32, bits 0-9 ordinal, bits 10/11 stored, bits 12-15 preserve. Creating a **new** chunk means encoding or storing 2048 bytes and pointing a layer window cell at it |
| connections | `PARTIAL` | destination rewriting is `SAFE AFTER BOUNDED FIX`; **new** records are `BLOCKED BY UNKNOWN SEMANTICS` (§4.5). The gap is split cleanly: structural editing is engineering, new-record and geometry authoring is research |
| character definitions | `PARTIAL` | the record layout is `CONFIRMED` and fixed-size, but the table count is fixed at 232 by three `cmp rN,#0xE8` bounds, a 232-bit runtime bitmap, and eight base-load/`index << 4` sites. Appending is `UNRESOLVED`; editing an existing record is trivially safe |
| sprite definitions | `STRUCTURALLY SOLVED` for existing objects; `PARTIAL` for new ones | the object's extent formula `0x54 + 4*count` is `CONFIRMED`, so a new definition body can be materialised. What is unresolved is the id space: the run is 297 entries bounded by a literal and a terminator word, so a 298th definition needs the run relocated and the terminator moved |
| animation/frame data | `STRUCTURALLY SOLVED` | the animation object is `u32 frame_count` plus `4*frame_count` cells plus two unknown words; the frame record is an 8-byte header plus `piece_count` 12-byte pieces. Extents are fully determined by the counts. The two trailing animation words are `UNRESOLVED` but a new animation can **preserve** them from an existing record |
| graphics containers | `STRUCTURALLY SOLVED` for stored form; `PARTIAL` for packed | the wrapper is `CONFIRMED` and stored emission already exists (`build_stored`). Packed emission is the `LOGX-CODEC-WRITE-001` gate |
| compression encoding | `PARTIAL` | see §5.3 and §17. The concrete obligations are enumerated; the initial literal width and the marker-vs-size rule are open |
| scripts/dialogue | `NOT APPLICABLE` to this queue | outside LOGX scope; separate accepted work exists |

**Do not read this table as "research is blocking implementation".** Of the
twelve rows, `verified ROM allocation` is `IMPLEMENTATION ONLY`; `tiles`,
`animation/frame data` and `sprite definitions` (for existing objects) are
`STRUCTURALLY SOLVED`; and `graphics containers` is structurally solved for the
stored form. Only `pointer/table expansion` (the appearance-count case), `map
data`, `connections` (new records and geometry) and `compression encoding`
genuinely need research or a decision, and each is scheduled with its own
blocking reason in §17 and
[`POST_LOGX_IMPLEMENTATION_ROADMAP.md`](POST_LOGX_IMPLEMENTATION_ROADMAP.md).

---

## 19. Research freeze conclusion

**The LOGExtractor research freeze can end.**

The ten tickets answered every question the SDK needs answered before
implementation can begin on the near roadmap, and the questions they did **not**
answer are documented here as unresolved with an explicit statement of which
capability each one blocks. The basis for ending the freeze:

1. **Nothing in the accepted resource graph is guessed.** Every `CONFIRMED`
   claim in §2-§9 is anchored to an engine instruction address or a whole-corpus
   census, and the superseded models are enumerated once in §10 so they cannot be
   silently reintroduced.
2. **Read support is complete for the classes the near roadmap uses.** §14 rates
   MapEntry, the map root, the dominant layer, the tile chunk, the selector
   stream, the connection record, the container, the appearance definition, the
   sprite definition, the animation object, the frame record, the sprite piece
   and the graphics container as `TRUSTED` or `TRUSTED WITH KNOWN FIX`. Every
   `TRUSTED WITH KNOWN FIX` read row names a specific enumerated, bounded,
   testable production defect in §11.1-§11.4; a row whose known gap is an
   unresolved *consumer* rather than a defect is rated `TRUSTED` with the gap in
   its field-confidence column (the map root) or `PARTIAL` for the resource
   (the portrait pointer).
3. **The near-roadmap authoring operations are engineering, not research.** §15
   rates in-place editing of map metadata, tiles, appearance text references,
   animation pointers, animation/frame data, sprite graphics and warp
   destinations as `SAFE AFTER BOUNDED FIX` - and every one of those fixes is a
   parser correction, a validation or a writer. Each `TRUSTED WITH KNOWN FIX`
   read row points at an enumerated defect in §11.1-§11.4; a row whose "known"
   gap is an unrecovered consumer rather than a defect is rated plain `TRUSTED`
   and carries the gap in its field-confidence column instead. **Only four research tickets are
   recommended** (§17): one is a hard gate for the writing phase and the
   other two are conditional on a capability being scheduled. A fourth lead is
   recorded as **parked**, not recommended.
4. **The remaining unknowns are bounded and located.** §12 names 30 questions;
   §13 classifies each as blocking nothing, blocking only advanced authoring, or
   forensic. None of them blocks the first post-freeze ticket.
5. **The research method's own limits are published.** The queue's negative
   claims carry their scope (unscanned idioms, undecodable halfwords, coverage
   notes), and the two process defects the reviewers found - editing artifacts
   during review, and a first-pass rejection that was our own arithmetic error -
   are preserved in the ticket records rather than sanitised.

**What must happen before the freeze actually closes**, and is done by this
ticket: the ROM Bible is consistent with the accepted evidence (§20), the
graphics-format documentation is unambiguous (§21), the stale-assumption audit
has no surviving production hit (§11.6), production defects are inventoried
rather than fixed (§11), the implementation roadmap exists
([`POST_LOGX_IMPLEMENTATION_ROADMAP.md`](POST_LOGX_IMPLEMENTATION_ROADMAP.md)),
and the result has been independently reviewed against a frozen revision.

---

## 20. ROM Bible consistency audit

Target: `docs/reverse-engineering.md`, audited against all ten accepted tickets.

**Result: `UPDATED`.** Two stale statements and one structural gap were found and
corrected in this branch. Full findings and the audit method are in
[`LOGX_SYNTHESIS_PROVENANCE.md`](LOGX_SYNTHESIS_PROVENANCE.md) §1.

Corrected in this ticket:

| Location | Was | Now |
| --- | --- | --- |
| `docs/reverse-engineering.md` LOGX-CODEC-001 section | "`0x0803D966` ... has no `BL` caller in the image and none of the accepted call sites use it" | the accepted LOGX-CODEC-001 review found and the implementer re-verified **exactly one** `BL` caller, `0x0800F3D2`, and the "length-aware variant" reading was **withdrawn**: `r2` is a lookup-table pointer, tested only for NULL. The corrected text names the caller and the remapping path |
| `docs/reverse-engineering.md` LOGX-CODEC-001 section | the decoder blob's ROM base is "**INFERRED** from the library table at `0x087B7970`" | **CONFIRMED** from the startup DMA3 literals at `0x08000148`/`0x0800014C`/`0x08000150` (ROM `0x087B79A4` -> IWRAM `0x03000000`, **4,100 bytes**), so ROM `0x087B79E4` = IWRAM `0x03000040`. The library-table reading was **withdrawn** in review; the Bible still cited it |
| `docs/reverse-engineering.md` heading structure | eight LOGX sections, with LOGX-GFXSCAN-001 having no section because it promoted no format claim | unchanged, and **recorded** here: the absence is deliberate. A one-line pointer is added in the LOGX-FRAME-001 section so a reader can find the discovery verdict |

Verified clean by the audit (no change needed): every address notation in the
LOGX sections keeps GBA address and file offset distinct; the connector
destination is documented as two independent bytes and not as a big-endian `u16`;
layer `+0x00` is documented as a Thumb handler and not as a numeric type tag;
MapEntry `+0x00` is documented as a two-byte key; tile bits 12-15 are documented
as reserved/constant with the explicit instruction not to call them "unused";
the frame record is documented as an 8-byte header with 12-byte pieces; the
sprite-definition array is documented as count-bounded; and no LOGX section
promotes a LOGExtractor semantic slot name.

Historical correction context is **preserved**. The LOGX-CHAR-001 section's
bracketed note about the pointer-run first entry, the LOGX-SPRITE-001 section's
disagreement paragraph, and the LOGX-MAP-RENDER-001 section's refuted
"zero literal loads" claim are all left as written, because they are the record
of what was corrected.

---

## 21. `GRAPHICS_FORMAT.md` consistency audit

Target: `docs/research/GRAPHICS_FORMAT.md`, audited after LOGX-SPRITE-001 and
LOGX-FRAME-001.

**Result: `UPDATED`.** A **superseded-statements banner** was added at the top of
the document (§0 of that file), listing every claim in it that the two later
tickets refuted or offset-corrected, with the canonical position and the
superseding ticket. The dated in-place correction notes remain untouched as the
evidence trail.

| Claim in `GRAPHICS_FORMAT.md` | Disposition |
| --- | --- |
| frame record is `u32 piece_count` then **16-byte** pieces | **REFUTED**; banner states the 8-byte header and 12-byte stride |
| piece attribute word at `+0x08`, graphics pointer at `+0x0C` | **OFFSET CORRECTED**; attributes `+0x04`, graphics `+0x08`; the bit layout is confirmed |
| "All 10,959 frames declare exactly one piece" | **REFUTED**; 19 declare two and 2 declare four; 11,005 pieces over 10,980 frames |
| "Unique graphics containers: **7,355**" | **SUBSET, not the total**; the corpus reaches **7,390**, the extra 35 being what the 21 multipart frames reach |
| "Direction slots populated / NULL: 13,596 / 0" | **CONFIRMED for that reader's population**, extended to **13,660 / 0** over all 1,017 animation objects |
| the animation-pointer array is bounded by walking to the next structure because "no header field bounds the list" | **REFUTED**; `structure + 0x00` bounds it (4,070 slots, 1,721 non-null, 2,349 null); header is `0x54` bytes, not `0x50`; correcting the walk is a numerical no-op |
| LOGExtractor's fixed **23-slot** table | **REFUTED as a physical model**; positional slots are comparable, the array is count-bounded, variable-length and sparse; no slot name is adopted |

**Historical text is marked, not deleted.** The document's own
`> **(LOGX-*-001, added later ...)**` notes already marked the earlier
corrections; the banner makes the *current* reading unambiguous for a reader who
lands in the middle of the file, which is what section V requires. The two
consequences that are production defects rather than documentation -
`sprite_graphics.py`'s 4+16 layout and `graphics.py::_animations_in`'s unbounded
walk - are named in the banner and scheduled in §11.

**Not claimed:** this audit does not re-measure any number in
`GRAPHICS_FORMAT.md`. Every figure there remains the accepted reader's
population and is reproducible; the banner states which population.

---

## 22. Where the deep evidence lives

This document deliberately does **not** duplicate provenance. For any claim
above, the authoritative record is:

| For | Read |
| --- | --- |
| what a ticket measured, and how | `docs/research/LOGX_<TICKET>_PROVENANCE.md` |
| what its reviewers found and how the gate closed | `docs/research/LOGX-<TICKET>-001-review.md` |
| its accepted conclusions, refutations and deferred follow-ups | `docs/research/archive/LOGX-<TICKET>-001-COMPLETE.md` |
| the current canonical engine format | `docs/reverse-engineering.md` |
| the actor-graphics document, with its supersession banner | `docs/research/GRAPHICS_FORMAT.md` |
| this ticket's own audit method and measurements | `docs/research/LOGX_SYNTHESIS_PROVENANCE.md` |
| what to implement, in what order | `docs/research/POST_LOGX_IMPLEMENTATION_ROADMAP.md` |
| the runnable, ROM-free audit | `python -m tools.research.logx_synthesis_audit` |
