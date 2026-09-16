# LOGX-TILE-001: Buu's Fury chunk payload and tile-entry format

Evidence document for the canonical Buu's Fury USA Rev. 0 image, SHA-256
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

Every claim is labelled with one status from
[`../research-conventions.md`](../research-conventions.md):

- **CONFIRMED** - directly supported by cited engine instructions, cited ROM
  bytes, or a reproducible observation scoped to this profile;
- **INFERRED** - best explanation supported by evidence, not directly proven;
- **UNKNOWN** - evidence absent, contradictory or insufficient.

**EXTERNAL CLAIM** marks a statement taken from `mainant/LOGExtractor`.
**PROJECT OBSERVATION** marks a reproducible measurement on the canonical image.
**PROJECT CONCLUSION** marks this ticket's reasoned verdict on an observation.

Terminology is fixed here and used consistently below. The word *chunk* is used
only after section 3 establishes the object: **a chunk is the decoded payload of
one dominant-layer `+0x18` array element** - 0x800 bytes, consumed by the engine
as 1024 little-endian 16-bit screen entries laid out 32 columns by 32 rows. It
is not used to mean "graphics" or "metatile" anywhere in this document.

---

## 1. Scope and input

The ticket is research only. No GUI, renderer, Workbench or authoring change is
made. No derived ROM was produced, no emulator was launched, and the canonical
image was opened read-only. Addresses are GBA addresses; file offset is address
minus `0x08000000`.

External lead: `mainant/LOGExtractor` (`MapViewer/MainForm.cs` and
`MapViewer/Gba/ROM.cs`), as summarised in the ticket. Its claims are treated as
claims only; nothing in this document is inherited from it.

---

## 2. Accepted dependencies from prior LOGX tickets

Used as given, not re-derived:

| Fact | Source |
| --- | --- |
| `MapEntry` table at `0x0808E2E0`, stride `0x38`, 452 records | LOGX-MAP-RECORD-001 |
| Selector-1 root route: `MapEntry[+0x2C]` -> leading run of aligned in-ROM words -> `word[0]` | LOGX-MAP-RENDER-001 |
| Root layer slots `+0x14`, `+0x18`, `+0x1C`, `+0x20`; 1808 references; 1464 unique records; five `+0x00` handler words | LOGX-LAYER-001 |
| Dominant handler `0x08008087`; `+0x14`/`+0x15` are separate unsigned bytes read by two `ldrb`s; array indexed `record + 0x18 + 4*i`; index `y * (+0x14) + x` at `0x08007C86` | LOGX-LAYER-001 |
| The `0x18`-byte element stride belongs to root `+0x24`/`+0x28`, **not** to a layer record's `+0x18` window | LOGX-LAYER-001 |
| Layer positioning is UNRESOLVED; LOGExtractor's `+0x0D`/`+0x11` X/Y reading is refuted | LOGX-LAYER-001 |
| Project Webfoot container decoder `tools/webfoot/formats/webfoot_lz.py` (header `kind`, `declared_size`) | TOOLKIT-010 |

This ticket reuses those routes through
`tools/research/logx_layer_probe.py` and does not restate them as its own.

---

## 3. The `+0x18` array element target

### 3.1 Measurement

`python -m tools.research.logx_tile_probe <rom> --targets` enumerates the window
of every reference whose handler word is `0x08008087`, using the accepted bound
`record[+0x14] * record[+0x15]`, and classifies each raw word.

| Quantity | Value |
| --- | ---: |
| Dominant handler references | **1516** |
| Dominant handler unique records | **1420** |
| Array elements enumerated (sum of `x*y` over the 1516 references) | **4274** |
| ... classified `null` | **156** |
| ... classified `aligned_in_rom` | **4118** |
| ... classified `unaligned_in_rom` | **0** |
| ... classified `outside_rom` | **0** |
| Distinct non-null targets | **3745** |
| Targets referenced more than once (**shared targets**) | **165** |
| Maximum references to one target | **10** |
| Target address range | `0x08179A50`..`0x082B8BAC` |
| Every target 4-byte aligned | **yes** |

`4274 = 156 null + 4118 non-null`; `4118` non-null references resolve to `3745`
distinct targets. *References*, *unique targets* and *unique payloads* are
therefore three different numbers and are never mixed below.

### 3.2 Target structure

Each of the 3745 unique targets begins with an eight-byte header:

| Word | Measurement over 3745 unique targets |
| --- | --- |
| `+0x00` | `1` on all 3745 (a **kind-1** Webfoot container) |
| `+0x04` | `0x800` on all 3745 (declared decoded size) |

**PROJECT CONCLUSION.** Each array element points *directly* at a Webfoot
container. There is no chunk header of the engine's own, no second dereference,
and no pointer-to-pointer step: the constructor at `0x08007B78` loads the word
with `ldr r0,[r0,#0x18]` (`0x08007BF2`) and hands that same value to the
decompressor in `r0` at `0x08007C04`. **CONFIRMED** (physical).

**PROJECT OBSERVATION (reach beyond the selector-1 root set).** LOGX-LAYER-001
recorded 19 aligned `0x08008087` occurrences in `0x08100000..0x08400000` that no
selector-1 root references. Expanding those 19 records' own `x*y` windows gives
**86 cells, of which 82 are non-null** (4 nulls: one in `0x0822F748`, three in
`0x0824A2A8`). Every non-null element is an aligned in-ROM kind-1 container
declaring exactly `0x800`; the dimension products are `{1, 2, 3, 4, 6, 8}`.
So the container shape of section 3.2 is not an artifact of the reachable set;
an independent reviewer's own scan of all 1439 dominant-shape records reached
the same result (4002 non-null elements, 160 nulls, zero size outliers).
The addresses are `0x08220804`, `0x08220EEC`, `0x08221418`, `0x08221884`,
`0x0822F674`, `0x0822F748`, `0x0822FB10`, `0x0823048C`, `0x0823275C`,
`0x08232C30`, `0x0824A1CC`, `0x0824A2A8`, `0x0824A8C8`, `0x0824AC58`,
`0x0826512C`, `0x0826561C`, `0x082659D4`, `0x08265F74`, `0x082B608C`.
Which selector reaches them stays **UNRESOLVED**, as LOGX-LAYER-001 recorded.

**PROJECT CONCLUSION.** The element target is compressed, not raw tile data.
**CONFIRMED** (the header's kind word is the decompressor's own dispatch key, see
section 4.2).

### 3.3 Anomalies

| Anomaly | References | Unique records |
| --- | ---: | ---: |
| A null occurs inside the `x*y` window | **117** | **117** |
| A non-null follows a null inside the window | **85** | **85** |
| Target not aligned in ROM | 0 | 0 |
| Target outside ROM | 0 | 0 |
| Target declared size != `0x800` | 0 | 0 |
| Target failed to decode | 0 | 0 |
| Dominant record with a zero `x*y` product | 0 | 0 |

The 117 / 117 pair matches LOGX-LAYER-001's independently measured "117 of 1420
dominant records carry an internal null". It is reproduced here rather than
inherited, and it is stated for both counting units because a shared record is
one record but possibly several references.

Whether an internal null means "skip this grid cell" or "use the default
container `0x08070808`" is a *runtime* question and stays **UNRESOLVED** here.
This ticket adds one negative observation: the constructor's own null handling
(`0x08007BF4` `cmp r0,#0` / `0x08007BF6` `beq 0x08007C08`) **skips** the slot
without writing a default, while the streaming method writes the default at
`0x08007CBE`/`0x08007CFC`. So the two paths disagree at the code level.

---

## 4. Engine consumers of an array element

All addresses are Thumb instruction addresses. Instruction encodings quoted in
section 4.4 are the raw little-endian halfwords of the canonical image.

### 4.1 How a layer record is installed

`0x0800924C` walks four sub-objects and, for each, calls the corresponding layer
record's `+0x00` handler through the virtual-call trampoline:

```text
08009268  adds r0, r5, r7        ; r0 = 4*i
0800926a  ldr  r1, [r0, #0x14]   ; r1 = root[+0x14 + 4*i]  = the layer record
0800926c  adds r0, r4, #0        ; r0 = i                  = the layer slot index
0800926e  ldr  r2, [r1]          ; r2 = record[+0x00]      = the handler word
08009270  bl   0x08046AA4        ; bx r2  -> handler(r0 = i, r1 = record)
```

`0x08046AA4` is literally `bx r2` (bytes `1047`), i.e. a `bl`-callable register
trampoline. The dominant handler `0x08008086` then forwards
`(r0 = 0, r1 = i, r2 = record)` to the constructor `0x08007B78`, which stores
`r1`'s low byte at `object+0x04` (`08007B94 strb r6,[r4,#4]`, bytes `70 60` at
`0x08007B94`). **PROJECT CONCLUSION.** `object+0x04` is the layer's slot index
`i`, which section 9 proves is also the hardware BG index. **CONFIRMED**
(instruction access).

### 4.2 Where the array element is consumed

`0x08007B78` (constructor, dominant class), the only `bl` caller of which is
`0x0800808E`:

```text
08007BDA  adds r0, #0x14         ; r0 = record + 0x14
08007BDC  ldrb r6, [r0]          ; r6 = record[+0x14]      (x count)
08007BDE  ldrb r0, [r0, #1]      ; r0 = record[+0x15]      (y count)
08007BE0  muls r6, r0, r6        ; r6 = x * y
08007BE2  cmp  r6, #4
08007BE4  bgt  0x08007C0E        ; product > 4  ->  install nothing
08007BE6  movs r5, #0            ; i = 0
08007BEC  ldr  r0, [r4, #8]      ; r0 = record
08007BEE  lsls r1, r5, #2        ; r1 = 4*i
08007BF0  adds r0, r0, r1
08007BF2  ldr  r0, [r0, #0x18]   ; r0 = record[+0x18 + 4*i]   <-- the array element
08007BF4  cmp  r0, #0
08007BF6  beq  0x08007C08        ; null -> skip, no default written
08007BF8  adds r1, r4, r5
08007BFA  adds r1, #0x20
08007BFC  strb r5, [r1]          ; object[+0x20 + i] = i
08007BFE  lsls r1, r5, #0xB      ; r1 = i * 0x800
08007C00  adds r1, r1, r4
08007C02  adds r1, #0x4C         ; r1 = object + 0x4C + 0x800*i   (destination)
08007C04  bl   0x0803D940        ; decompress(r0 = container, r1 = destination)
```

### 4.3 The decompressor entry point

```text
0803D940  adds r2, r0, #0        ; r2 = source
0803D942  adds r0, r1, #0        ; r0 = destination
0803D946  ldr  r3, [r2]          ; r3 = container[+0x00] = kind
0803D948  adds r1, r2, #0
0803D94A  adds r1, #8            ; r1 = payload = container + 8
0803D94C  cmp  r3, #0
0803D94E  beq  0x0803D95E        ; kind 0: memcpy(dst, payload, container[+0x04])
0803D950  cmp  r3, #1
0803D952  beq  0x0803D958        ; kind 1: packed stream
0803D954  cmp  r3, #2
0803D956  bne  0x0803D95C        ; any other kind: return, destination untouched
0803D958  bl   0x08049120        ; packed decoder
0803D95E  ldr  r2, [r2, #4]      ; declared size
0803D960  bl   0x08046D18        ; memcpy(dst, payload, declared size)
```

**PROJECT OBSERVATION.** The third argument at the constructor's call site
(`r2` = `object+0x40`) is overwritten by `0x0803D940`'s own first instruction
(`adds r2,r0,#0`), so the decompressor takes exactly two arguments: source
container address and destination. **PROJECT CONCLUSION.** The decoded length
is the container's own `+0x04` field; the engine supplies no size and no bound.
**CONFIRMED** (instruction access). This is why the fixed `0x800` destination
stride is safe in this corpus: every dominant target declares exactly `0x800`.

**PROJECT OBSERVATION.** A kind-2 container would also decode, and a kind outside
`{0,1,2}` returns with the destination buffer untouched. Both remain
LOGX-CODEC-001's scope; no canonical dominant target uses either.

### 4.4 Loop structure, iteration order and destination

| Question | Answer | Evidence |
| --- | --- | --- |
| Iteration order over the array | ascending `i`, `0` to `x*y - 1` | `0x08007BE6`/`0x08007C08`/`0x08007C0A` |
| How many elements traversed | `x*y`, and only when `0 < x*y <= 4`; the `x*y == 0` case exits at `0x08007BE8`/`0x08007BEA` | `0x08007BE2`/`0x08007BE4`/`0x08007BE8` |
| Destination | `object + 0x4C + 0x800*i`, in EWRAM | `0x08007BFE`..`0x08007C02` |
| Object allocation | `0x204C` bytes = `4 * 0x800 + 0x4C` | pool `0x08007E64` read at `0x08007B84` |
| Is data copied to RAM? | **yes**, always; entries are never read from ROM at draw time | `0x08007C04` |
| Are dimensions hardcoded? | the *count* is data-driven (`+0x14`/`+0x15`); the per-payload 32x32 shape is hardcoded (section 6) | `0x08007BE0`, `0x0800806A` |
| What the constructor leaves in the four slots | all four `object+0x10`..`+0x1C` pointers are first set to the default container `0x08070808` (`0x08007BA8`..`0x08007BB2`), which is kind 0, declares size 0 and is followed by `0x800` zero bytes | pool `0x08007E6C`, `0x08007BA8` |

The four-slot cap is not a limit on the format. `0x08007C12` recomputes the 2x2
viewport window into a four-entry id array at `stack+0x804`, then installs
whichever of the four slots is not resident. `0x08007C12` has exactly two
`bl` callers, `0x08007EE4` and `0x08007F9E`, both inside methods of the layer
object class that section 9.4 recovers from the class word's self-relative
offset table; that is an **INFERRED** attribution (a table entry, not a direct
call, is what makes those two functions reachable):

```text
08007D0E  bne  0x08007D68        ; slot already resident -> next slot
08007D18  bne  0x08007D62        ; resident buffer already used -> next buffer
08007D42  ldr  r1, [r4, #8]      ; record
08007D44  lsls r0, r0, #2
08007D46  adds r0, r1, r0
08007D48  ldr  r0, [r0, #0x18]   ; record[+0x18 + 4*chunk_id]
08007D4A  add  r1, sp, #4
08007D4C  bl   0x0803D940        ; decompress
08007D5C  bl   0x08049138        ; copy 0x800 bytes to the chosen resident buffer
```

**PROJECT CONCLUSION.** The open question LOGX-LAYER-001 recorded - "the
four-slot install cap (`cmp r6,#4`) versus 133 records with products above four"
- is **RESOLVED**. The constructor's loop is a bounded warm-up; the streaming
method installs any chunk of the record on demand into a four-entry resident
cache. A record with `x*y > 4` therefore loses nothing.

### 4.5 The two consumers of a decoded payload

A decoded payload is read in exactly two places, both methods of the layer
object class (section 9.3):

1. **blit to VRAM** - `0x08007D98`, row-by-row `memcpy` (section 9.2);
2. **a 16-bit query** - `0x0800800A`, `ldrh` at `payload + (y & 31)*64 + (x & 31)*2` (section 6.2).

Both are reached by enumerating every read of `object+0x10`..`object+0x1C`, and
all four methods of the class word's offset table are accounted for. The
section 8 scan finds no third consumer and no bit-level decode anywhere. The
limit of this enumeration is that it is a *static* one: an indirect call could
in principle reach a payload reader that does not load its base from
`object+0x10`..`+0x1C`, and nothing in this ticket excludes that. What is
excluded is a second reader inside the payload's own code region.

---

## 5. Payload structure: what an array element resolves to

**PROJECT CONCLUSION.** A dominant-layer chunk is **0x800 decoded bytes**, i.e.
**1024 little-endian 16-bit entries**. The engine never states this as a pair of
dimensions; it is fixed by two independent hardcoded constants in the consumer:

- the destination stride `lsls r1, r5, #0xB` at `0x08007BFE` (`0x800` per slot);
- the row stride `64` and the `& 31` masks in the query method (section 6.2).

All 3745 unique targets declare exactly `0x800` and all 3745 decode to exactly
2048 bytes; there are no size outliers to reconcile.

---

## 6. Chunk dimensions

### 6.1 The 32x32 claim

**EXTERNAL CLAIM (LOGExtractor).** A chunk is 32 x 32 tiles = 1024 entries.

**PROJECT OBSERVATION.** The layer object's query method `0x0800800A` computes
element positions from a pixel coordinate and reads the payload with `ldrh`:

```text
08008022  asrs r4, r4, #8        ; r4 = x_px >> 8     -> chunk column
08008024  asrs r3, r3, #8        ; r3 = y_px >> 8     -> chunk row
08008032  cmp  r4, #2
08008034  bge  0x0800803A        ; chunk column must be 0 or 1
08008036  cmp  r3, #2
08008038  blt  0x08008042        ; chunk row must be 0 or 1
08008056  lsls r3, r6, #1        ; r3 = chunk_row * 2
0800805A  adds r3, r3, r4        ; r3 = chunk_row * 2 + chunk_col
0800805C  asrs r1, r1, #3        ; r1 = x_px >> 3     -> tile column
0800805E  asrs r5, r5, #3        ; r5 = y_px >> 3     -> tile row
08008062  lsls r3, r3, #2
08008064  adds r3, r3, r0
08008068  ldr  r3, [r3, #0x10]   ; r3 = object[+0x10 + 4*(row*2+col)]
0800806A  lsls r4, r5, #0x1B
0800806C  lsrs r4, r4, #0x15     ; r4 = (tile_row & 31) * 64
0800806E  lsls r1, r1, #0x1B
08008070  lsrs r1, r1, #0x1A     ; r1 = (tile_col & 31) * 2
08008072  adds r3, r4, r3
08008074  ldrh r1, [r3, r1]      ; 16-bit load
```

`(tile_row & 31) * 64` is a **64-byte row stride**, and `(tile_col & 31) * 2` is
a **2-byte element** inside that row. `64 / 2 = 32` elements per row and the
`& 31` mask on the row index gives 32 rows: `32 * 32 * 2 = 0x800`.

**PROJECT CONCLUSION.** `32 x 32 entries`, `64`-byte rows, `1024` entries per
payload are **CONFIRMED** for the dominant class, from the consumer's own
arithmetic and access width - not from target spacing in ROM, and not from
LOGExtractor.

**PROJECT CONCLUSION.** The dimensions are **not** stored in a chunk and are not
derivable from the container; they are hardcoded in the two consumers. The
per-record *chunk grid* dimensions (`+0x14`/`+0x15`) are a different thing and
are data-driven.

### 6.2 What the query method does with a payload

The query method takes `(object, pixel coordinate pointer, output pointer)`,
offsets the coordinate by `object+0x34`/`object+0x38`, requires the resulting
chunk indices to be in `[0, 2)` (a 2x2 resident window), loads the entry, and:

```text
08008076  cmp  r1, #0
08008078  bne  0x0800807E        ; nonzero -> "occupied"
0800807E  ldr  r0, [r0, #0xC]    ; object+0x0C = the record's signed +0x16 value
08008080  str  r0, [r2]          ; write it to the caller's output pointer
08008082  movs r0, #1            ; return 1
```

**PROJECT OBSERVATION.** The only engine test applied to a 16-bit entry value is
"is it zero". Coverage: the predicate is `cmp r1,#0` on the result of the single
`ldrh` at `0x08008074`; every site in the image that loads from a payload buffer
is enumerated in section 4.5 (the VRAM blit's row `memcpy` and this `ldrh`), and
the image-wide mask and field-extraction scan of section 8.4 finds no site
inside `0x08007000..0x0800A000` whose `right_shift` reaches bit 9 or above, so
no code in the payload's own region extracts or masks any part of an entry.
**PROJECT CONCLUSION.** `0` is the engine's empty/absent entry; every nonzero
entry is "occupied", **including** a word whose low ten bits are zero but whose
upper bits are set. This matters for bits 12-15 (section 8.4).

---

## 7. Entry width and byte order

| Question | Result | Evidence |
| --- | --- | --- |
| Physical width | **2 bytes** | `ldrh r1,[r3,r1]` at `0x08008074` |
| Byte order | **little-endian** | `ldrh` on a little-endian ARM7TDMI; and the VRAM blit moves whole rows unchanged, so the value that arrives in the screenblock is the same little-endian halfword the payload holds |
| Stride | 2 bytes | `(tile_col & 31) * 2` at `0x08008070` |
| Alignment | payload base 4-byte aligned; every read offset is even | all 3745 targets 4-byte aligned; offsets are `2*k` |
| Copied or transformed before use? | **copied verbatim**; no transformation, packing or reordering anywhere | `0x08007DCE`..`0x08007DDC` `memcpy` of whole rows |
| `ldrb` / `ldr` alternative | none found; the only payload reads in the image are the `ldrh` above and the row `memcpy` | section 4.5 enumerates every read of `object+0x10`..`object+0x1C`; section 8.4's region scan finds no bit-level consumer |

**PROJECT CONCLUSION.** 16-bit little-endian elements, stride 2, no packing.
**CONFIRMED.**

---

## 8. Tile-entry bit fields

### 8.1 Method

Three independent routes were used, and every negative statement below states
its coverage:

1. **Exhaustive constant search.** Every 4-byte-aligned and 2-byte-aligned
   occurrence of `0x000003FF`, `0x00000400`, `0x00000800`, `0x00000C00`,
   `0x00000FFF`, `0x0000F000`, `0x0000FC00`, `0x00003000`, `0x0000C000`,
   `0x000001FF`, `0x000000FF` over the whole 8 MiB image.
2. **Exhaustive mask-idiom scan.** Every adjacent `lsls rd,rs,#a ; lsrs rd,rd,#b`
   halfword pair over the whole image (a raw halfword scan, so an undecodable
   neighbour cannot hide a site), reported as `(right_shift, width)`.
   `(0, 10)` is the plain `& 0x3FF` idiom, `(10, 1)` extracts bit 10, `(11, 1)`
   bit 11, `(12, 4)` bits 12-15. Implemented as
   `tools.research.thumb_disasm.find_field_extractions`. **Both** forms are
   reported, and the pairing accepts `b == a` as well as `b > a`: a scan that
   only accepted a strictly larger second shift would never emit
   `right_shift == 0` and would make every "no site masks the low *n* bits"
   statement vacuously true. The synthetic suite
   `tests/unit/test_thumb_disasm_field_extraction.py` pins that behaviour.
   Measured totals: **1532** pairs over the whole image - **46** below
   `0x08007000`, **29** inside the map/layer code region `0x08007000..0x0800A000`,
   **961** inside the first `0x70000` bytes (`0x08000000..0x08070000`) and **571**
   at or above `0x08070000`.
3. **Exhaustive payload census** over all 3745 unique decoded payloads.

### 8.2 Census over the 3745 unique payloads (3,834,880 entries)

The union is over **unique payloads**, not over references: each payload's 1024
words are counted once, so a chunk shared by ten layer cells does not multiply
any count.

| Bit | Entries with the bit set |
| --- | ---: |
| 0 | 581,251 |
| 1 | 507,444 |
| 2 | 518,253 |
| 3 | 513,338 |
| 4 | 513,485 |
| 5 | 472,053 |
| 6 | 451,130 |
| 7 | 377,289 |
| 8 | 177,836 |
| 9 | 81,271 |
| **10** | **46,034** |
| **11** | **15,668** |
| **12** | **0** |
| **13** | **0** |
| **14** | **0** |
| **15** | **0** |

Derived: bit 10 and bit 11 both set on 5,239 entries. The high nibble is `0x0`
on all 3,834,880 entries. Zero entries: 2,727,181. Distinct raw values: 2,879.
Raw minimum `0x0000`, maximum `0x0F7B` (= `0b1111_0111_1011`: bit 11, bit 10, and
low field `0x37B`). Maximum low field (bits 0-9): **895**, with 896 distinct
values, i.e. the field covers `0..895` contiguously. No payload is entirely zero.

### 8.3 Bits 0-9

**PROJECT OBSERVATION.** No engine consumer of a payload masks bits 0-9 of an
entry, and none extracts a 10-bit field from one. The scan covers the adjacent
`lsls`/`lsrs` mask idiom and the aligned-constant search; section 8.4 lists the
idioms it does not cover.

| Scan | Result |
| --- | --- |
| `(right_shift, width) = (0, 10)`, the plain `& 0x3FF` idiom, over the whole image | 51 sites |
| ... of those, inside the map/layer code region `0x08007000..0x0800A000` | **0** |
| `(0, 9)`, `(0, 11)`, `(0, 13)`, `(0, 14)` - masks of width 9, 11, 13, 14 | 1 (at `0x08271402`, data), 0, 0, 0 |
| any pair with `right_shift` in `9..12`, inside `0x08007000..0x0800A000` | **0 of the region's 29 pairs** (123 such pairs exist elsewhere in the image) |
| `0x000003FF` as an aligned word anywhere | 5 (`0x0800AD84`, `0x0800FCE8`, `0x08010F30`, `0x082AC294`, `0x082FC748`) |
| ... of those, PC-relative loaders | 5, at `0x0800AB9A`, `0x0800FA8A`, `0x0800FB98`, `0x0800FC4E`, `0x08010CEA` - **none inside the map/layer code region** |

The low-ten-bit mask is therefore a real engine idiom, used 51 times, and **none
of its uses is in the code that owns a layer payload**; the sampled uses are OAM
attribute packing (section 8.4). The negative claim is about *where* it is used,
not about whether it exists.

**PROJECT OBSERVATION.** Bits 0-9 alone account for the whole tile space the two
graphics loaders can populate. Expanding every nonzero entry of every dominant
payload that a map's four layer slots reference - a per-map, per-reference
expansion, so a payload shared by ten maps is expanded ten times - gives
**1,241,888 nonzero entries**, and comparing each entry's bits 0-9 against the
map's own two tile sources:

- the static source is the `root+0x48` selector stream; it writes **one 64-byte
  tile per selector**, sequentially, at `0x06000000 + 64*i` (section 10), so a
  map with `n` selectors has tiles `0..n-1`;
- the animated-tile records (`root+0x0C` count, `root+0x10` pointer array) each
  write `tile_count` 64-byte tiles starting at their own `destination_tile`
  (`0x08009B12`).

A different, smaller number belongs to a different unit and is not used here:
aggregating over the **unique payloads** instead (each payload counted once)
gives 1,107,699 nonzero entries, which is `3,834,880 - 2,727,181`. The coverage
check is per map, so 1,241,888 is the correct denominator for it.

**Result: 0 of 1,241,888 nonzero entries has a bits 0-9 value that is neither a
static selector ordinal nor inside one of the map's own animation destination
ranges.** 23,307 entries land inside an animation range, on 178 maps. The global
maximum low field, 895, is exactly map 39's highest animation destination plus
its tile count minus one (893 + 3 - 1). Map 0 has 841 selectors, no animation
records, and a maximum low field of 840.

**PROJECT CONCLUSION.** Bits 0-9 are the **tile ordinal in the engine's character
region**. **CONFIRMED** (two independent engine loaders plus a total-coverage
invariant: 0 exceptions in 1,241,888 entries).

*Physical versus semantic.* "Bits 0-9 survive as an integer field" is CONFIRMED.
"Bits 0-9 are the final hardware character name" is also CONFIRMED here, because
the same halfword is `memcpy`ed unchanged into a BG screenblock whose control
register the engine itself writes as 8bpp with character base 0 (section 9.3),
and the hardware reads bits 0-9 as the character name. Nothing between the
payload and VRAM modifies the word.

### 8.4 Bits 10, 11, 12-15

**PROJECT OBSERVATION (engine side).** 1532 pairs over the whole image; 29 of
them inside the map/layer code region `0x08007000..0x0800A000`.

| Scan (`find_field_extractions`, raw halfword) | Whole image | Inside `0x08007000..0x0800A000` |
| --- | ---: | ---: |
| `(10, 1)` - isolate bit 10 | **0** | 0 |
| `(11, 1)` - isolate bit 11 | 4, at `0x0806E682`, `0x0806ECD8`, `0x0806ECF4`, `0x0806ED10` | 0 |
| `(12, 4)` - isolate bits 12-15 | 4, at `0x0816A0E2`, `0x08780714`, `0x08781C16`, `0x08788D9E` | 0 |
| `(0, 9)` - mask `0x1FF` | 1, at `0x08271402` (data) | 0 |
| `(0, 10)` - mask `0x3FF` | 51 | **0** |
| `(0, 11)` - mask `0x7FF` | **0** | 0 |
| `(0, 12)` - mask `0xFFF` | 5, all at `0x082D8F1E` or above (data) | 0 |
| `(0, 13)` - mask `0x1FFF` | **0** | 0 |
| `(0, 14)` - mask `0x3FFF` | **0** | 0 |
| `(0, 15)` - mask `0x7FFF` | 2, at `0x0802EEB6`, `0x08043E0E` | 0 |
| `(0, 16)` - mask `0xFFFF` | 156 | 2, at `0x08009E32`, `0x08009FB6` |
| any pair with `right_shift` in `9..12` | 123 | **0** of 29 |
| `0x00000FFF` aligned word | 0 | 0 |
| `0x0000F000` aligned word | 0 | 0 |
| `0x0000FC00` aligned word | 3 | 0 |

So **no pair in the map/layer region has `right_shift >= 9`** (0 of its 29
pairs): nothing in the code that owns a payload extracts or masks a field that
*begins* at bit 9 or above. The region does contain two `(0, 16)` `& 0xFFFF`
pairs (`0x08009E32`, `0x08009FB6`), which read all sixteen bits of a 16-bit
counter and select none of them, so the statement is about field *selection*,
not about touching a whole halfword. The low-ten-bit mask that does exist
elsewhere in the image is used 51 times, never in that region. The three sampled
`(0, 10)` sites are OAM attribute packing - `ldrh r0,[r0,#0xC]` masked to ten
bits and merged into a sprite attribute word at `[r3,#4]`/`[r4,#4]`
(`lsls` at `0x0800ACF4` and `0x0801798A`) and an unrelated `subs` difference at
`0x0803F2A6`. **PROJECT OBSERVATION.**

**PROJECT CONCLUSION (scope of the negative).** The exact statement this ticket
supports is: **no recovered engine consumer of a payload reads bits 10-15**, and
**no code in the payload's own region selects any field beginning at bit 9 or
above**. It is *not* "no engine instruction anywhere reads those bits", and the
image-wide form is not established. Three idioms that could test a bit of some
*other* value are outside this ticket's scan and are measured here so the
negative is not over-read:

- **shift immediately followed by a conditional branch** - `lsrs`/`lsls` with a
  non-zero immediate directly before a `Bcond`. **8,014** such pairs exist
  image-wide; restricting to shift amounts that put bits 10-15 in the carry or
  top position gives 241 / 395 / 372 / 312 / 350 / 760 sites respectively. Inside
  `0x08007000..0x0800A000` the only such pairs are 2 for bit 1
  (`0x0800772A`, `0x08009872`), 1 for bit 4 (`0x0800763C`) and 2 for bit 15
  (`0x080089DE`, `0x08008A3E`) - **none for bits 10-14**. This count is an upper
  bound on *carry* tests: most of these pairs test the shifted **result**, e.g.
  `0x08008A3E` is `lsrs r2,r0,#0x10` / `beq`, which asks whether the word at
  `object+0x0C` fits in 16 bits. Every one sampled reads an object field, never
  `object+0x10..object+0x1C`.
- **`movs #imm` followed by `lsls` on the same register** - a mask constant built
  in two instructions. **1,204** such builds produce a constant with a bit at 10
  or above set, over 301 distinct constants. The bits-10-11 constant `0x0C00`
  accounts for 34 of them, none inside `0x08007000..0x0800A000`, and they are the
  same OAM attribute packing sampled above (`0x0800ACFC`, `0x0800B5B0`,
  `0x0800B7E2`, `0x0800B9C8`, `0x0800C55A`).
- **non-adjacent `lsls`/`lsrs` pairs** on one register, which the scan requires
  to be adjacent. One exists in the map/layer region:
  `0x08008728 lsls r3,r3,#0x16` and `0x08008730 lsrs r3,r3,#0x16`, an `& 0x3FF`
  applied to a coordinate already shifted by `asrs r3,r3,#0xA` at `0x08008712`
  and combined with a `0x400` scale constant at `0x0800872E`. It reads no payload
  buffer.
- `ldrb` byte-wise access into a payload is not scanned in either direction,
  because no payload read other than the `ldrh` of section 6.1 exists
  (section 4.5).

Each of those idioms is a way to test a bit of *something*; none was found
operating on a payload entry. Section 8.5's classification rests on that scoped
statement.

Coverage caveats, stated so the negatives are not over-read:

- the four `(11, 1)` sites all lie in `0x0806E000..0x0806F000`. That 4 KiB block
  is a table, not code: the aligned words at `0x0806E640` are `0x03800070`,
  `0x00000C00` and `0x40040002`, and **no Thumb `BL`/`BLX` encoding in the image
  resolves into that block**. Measured by decoding every `BL`/`BLX` halfword
  encoding at a **4-byte-aligned** offset: **8,838** encodings, of which **8,266**
  resolve to an in-ROM address and **4,440** are distinct targets. Per-64 KiB-block
  call-target counts span **2** (blocks `0x08680000` and `0x087E0000`) to
  **1,384** (block `0x08040000`); block `0x08060000` receives **9**; and
  `0x0806E000..0x0806F000` receives **0**. (Enumerating every *even* offset
  instead gives 17,748 encodings; that wider population is not used for the
  per-block figures.) This bounds *direct* calls only; a function pointer could
  still reach the block, so the statement is "no `BL`/`BLX` in the image targets
  it", not "it is unreachable".
- the four `(12, 4)` sites are all at `0x0816A0E2` or above, i.e. inside
  compressed/graphics data, not the executable region.
- `0x0000F000` occurs twice as an *unaligned* byte sequence; it never occurs as a
  4-byte-aligned word, which is the only way the engine could load it as a mask.

**PROJECT CONCLUSION (bit 10 and bit 11).** Both bits are used in canonical data
and neither is any part of the tile ordinal:

- they are outside the field that fully explains the loaders' tile space
  (section 8.3), so treating them as index bits would produce indices into tiles
  that no loader ever writes;
- they vary largely independently (46,034 / 15,668 / 5,239 both), which is the
  shape of two independent control flags rather than an encoded small integer;
- the 16-bit word reaches the BG screenblock unchanged, and the engine's own BG
  control word for these layers is `0x1C80 + 0x100*bg`, which sets bit 7
  (**8bpp**) and bits 8-12 (screen base `28 + bg`) and leaves bits 14-15 zero
  (256x256 text BG).

Under that register configuration the platform's BG map entry layout assigns
bit 10 to horizontal flip and bit 11 to vertical flip, and ignores bits 12-15.

**Direction assignment: PARTIALLY CONFIRMED.** The bits are confirmed to exist,
to be used, and to be outside the tile-index field. Which of the two is
horizontal is derived from the platform BG entry format applied to bytes the
engine copies verbatim into a live screenblock; **no recovered engine consumer of
a payload reads either bit** (section 8.4 states the exact scope and the
techniques that were not scanned), so the direction is not engine-proven here.
The accepted production renderer (`docs/research/MAP_RENDER_FORMAT.md` section 7)
assumes the same assignment and matched retail VRAM pixel-exactly in
MAP-VIS-002, which corroborates it; this ticket did not repeat that comparison
and no runtime experiment was performed (mutation is optional per the ticket).

**PROJECT CONCLUSION (bits 12-15).** Each of bits 12, 13, 14 and 15:

- is **zero on all 3,834,880 entries** of all 3745 unique payloads;
- is never masked as a group (`0x0000F000`: 0 aligned occurrences in the image)
  and never extracted as a 4-bit field at shift 12 inside code;
- is, however, **not inert**: the query method at `0x0800800A` treats any nonzero
  entry as occupied, so a word with bits 12-15 set and bits 0-9 clear would be
  read as occupied while selecting tile 0.

Classification, per bit, is **RESERVED / CONSTANT IN CANONICAL DATA** plus
**UNUSED BY ANY KNOWN CONSUMER** - deliberately *not* "the format defines these
bits as unused". For this image the layers are 8bpp, and the platform ignores the
palette-bank field of a BG entry in 8bpp mode, which is *consistent* with the
all-zero census but is not itself engine evidence; a profile in which any layer
were 4bpp would make the same four bits live. No canonical data distinguishes
the two readings, so the semantic role is **UNRESOLVED**.

### 8.5 Classification table

| Item | Status |
| --- | --- |
| bits 0-9 survive as an integer field | **CONFIRMED** |
| bits 0-9 are the tile ordinal the engine's own loaders populate | **CONFIRMED** |
| bits 0-9 are the hardware character name | **CONFIRMED** (verbatim VRAM copy, engine-written 8bpp/char-base-0 control) |
| bit 10 exists, is used, and is not an index bit | **CONFIRMED** |
| bit 11 exists, is used, and is not an index bit | **CONFIRMED** |
| bit 10 = horizontal flip | **PARTIALLY CONFIRMED** (platform format; no engine read) |
| bit 11 = vertical flip | **PARTIALLY CONFIRMED** (platform format; no engine read) |
| bit 12 | RESERVED / CONSTANT IN CANONICAL DATA; UNUSED BY ANY KNOWN CONSUMER; semantic role UNRESOLVED |
| bit 13 | as bit 12 |
| bit 14 | as bit 12 |
| bit 15 | as bit 12 |
| "the format defines bits 12-15 as unused" | **REFUTED as a stated conclusion** - not supported and not claimed |

---

## 9. The pixel-tile and BG chain around a payload

### 9.1 8x8 pixels

**PROJECT OBSERVATION.** Two independent engine facts fix the visual tile size:

1. the query method converts pixels to tiles by `asrs #3` on both axes
   (`0x0800805C`, `0x0800805E`), i.e. 8 pixels per tile;
2. the character-data writer copies **64 bytes per destination tile**
   (`movs r2,#0x40` at `0x08009C6A`, `adds r6,#0x40` at `0x08009C78`), and the
   animated-tile writer copies `tile_count * 64` bytes (`lsls r2,r1,#6` at
   `0x08009B36`). With BGxCNT bit 7 set (8bpp) and character base 0, 64 bytes is
   exactly one 8x8 8bpp tile.

**PROJECT CONCLUSION.** 8x8 tiles are **CONFIRMED** for this engine path, from
engine accesses - not from the platform's usual 8x8 convention. A **256x256
pixel chunk** follows from `32 * 8` on both axes and is separately corroborated
by the query method's own `>> 8` chunk-index arithmetic at `0x08008022`.
**CONFIRMED.**

### 9.2 The VRAM blit

`0x08007D98(object, coordinate)`, reached from the layer object's render methods
(**INFERRED** on the same basis as section 4.4: `0x08007D98` has exactly two
`bl` callers, `0x08007EEC` and `0x08007FA6`, both inside methods recovered from
the class word's self-relative offset table):

```text
08007D9C  ldr  r0, [r1]          ; coordinate[0] = x_px
08007DA0  lsls r0, r0, #0x18
08007DA2  lsrs r0, r0, #0x1B     ; r0 = x_px >> 3   (tile column, 8 px per tile)
08007DA6  ldr  r0, [r1, #4]
08007DAA  lsls r0, r0, #0x18
08007DAC  lsrs r6, r0, #0x1B     ; r6 = y_px >> 3   (tile row)
08007DAE  ldrb r0, [r5, #4]      ; r0 = object[+0x04] = the layer slot index
08007DB2  lsls r0, r0, #0xB      ; r0 = slot * 0x800
08007DB4  adds r7, r0, r1        ; r7 = 0x0600E000 + slot*0x800   (pool 0x08007E80)
08007DB8  movs r0, #0x20
08007DBA  subs r0, r0, r1        ; 32 - tile_column
08007DCE  ldr  r1, [r5, #0x10]   ; resident payload for 2x2 slot 0
08007DD0  lsls r0, r4, #6        ; tile_row * 64
08007DD4  ldr  r2, [sp, #0x1C]   ; tile_column * 2
08007DDE  bl   0x08049144        ; memcpy(dst = VRAM + row*64 + col*2,
                                 ;        src = payload + row*64 + col*2,
                                 ;        n   = (32 - col) * 2)
08007DE2  adds r4, #1
08007DE6  blt  0x08007DCE        ; next row
```

and then, for the same row band and the four-part scroll wrap, three more such
loops read `object+0x14`, `object+0x18` and `object+0x1C` (`0x08007DFA`,
`0x08007E20`, `0x08007E4C`).

**PROJECT CONCLUSION.** The payload leaves EWRAM as **whole unchanged 16-bit
elements**; nothing is decoded, re-ordered or masked. **CONFIRMED.** The blit is
not quite the screenblock region's only writer: the absent-layer placeholder
class (`0x08049548`) `memset`s the same region to zero
(`0x08007A28`..`0x08007A38` → `0x0600E000 + slot*0x800`, 0x800 bytes), so the
lane can also be *cleared*. Only whole zero halfwords are written, so nothing
decodes, re-orders or masks an entry there either.

### 9.3 The hardware configuration the engine writes

`0x0800938C` is the per-map presentation routine. It reads the selector-1 root
from `arg0+0x8C` (`0x080093B2`, written by `0x08009552` when the root is loaded),
runs the animation setup, the character-data assembly and the layer install, then:

```text
080093D6  ldr  r0, [r4, #0x3C]    ; r0 = root + 0x3C
080093D8  ldr  r1, [pc, #0x270]  ; r1 = 0x080716C4  (pool 0x0800964C)
080093DA  lsls r0, r0, #3        ; r0 = 8 * root[+0x3C]
080093DC  adds r1, #0x14         ; r1 = 0x080716D8
080093DE  adds r0, r0, r1        ; r0 = 0x080716D8 + 8*root[+0x3C]
080093E0  ldrh r1, [r0]          ; BG0CNT value
080093E2  ldr  r2, [r6, #0x34]   ; per-frame offset added to BG0CNT
080093E4  adds r2, r1, r2
080093E6  movs r1, #1
080093E8  lsls r1, r1, #0x1A     ; r1 = 0x04000000
080093EA  strh r2, [r1, #8]      ; REG_BG0CNT
...       strh r2, [r1, #0xA]    ; REG_BG1CNT
...       strh r2, [r1, #0xC]    ; REG_BG2CNT
...       strh r2, [r1, #0xE]    ; REG_BG3CNT
0800941A  ldrh r0, [r0, #2]      ; DISPCNT value from arg0+0xA2
0800941C  strh r0, [r1]          ; REG_DISPCNT
```

**PROJECT OBSERVATION.** `root+0x3C` is **not** zero on every root. Measured over
all 452: **451 roots hold 0** and exactly one - map 19, root `0x082AD8BC` - holds **1**.
The two selected records are:

```text
index 0, 0x080716D8:  1C80 1D80 1E80 1F80     (451 roots, including maps 0, 39, 40)
index 1, 0x080716E0:  1C80 1D80 BE80 1F80     (map 19 only)
```

The halfword actually stored into `REG_BGxCNT` is `record[i] + [r6,#0x34]`
(`0x080093E2`/`0x080093E4`, then `strh r2,[r1,#8]`), i.e. the table record plus a
per-frame offset whose source is not written by any code recovered in this
ticket. The table record itself is what the decoding below describes.

Decoded as BGxCNT text-mode words, both records agree on priority `0`, character
base `0` (`0x06000000`), **8bpp** (bit 7 set) and screen bases `28, 29, 30, 31`
(that is, `0x0600E000 + i*0x800`), with mosaic off. They differ in exactly one
word: map 19's BG2 value is `0xBE80` rather than `0x1E80`, whose bits 14-15 are
`0b10`, i.e. a **512x256** screenblock rather than 256x256. Every other field,
including the screen base of 30, is unchanged.

**PROJECT CONCLUSION.** The VRAM address in section 9.2 and the screen base in
the engine's own register value agree exactly for both records and all four
slots, and the character base agrees with
the `0x06000000` destination of the character-data writer (section 10.4). The
slot index in `object+0x04` is therefore the BG index. **CONFIRMED** from ROM
data plus the register write, not from a runtime capture.

### 9.4 The layer object class

`0x08007B96` stores the even data pointer `0x08049410` (pool `0x08007E68`) at
`object+0x00`. That address is a **table of signed 32-bit offsets relative to the
table base**; adding each offset to `0x08049410` yields a Thumb entry point for
every entry:

| Index | Target | Role observed in this ticket |
| ---: | --- | --- |
| 1 | `0x08007E84` | stream the 2x2 window and blit to VRAM |
| 2 | `0x08007F2E` | the same, with an early-out when the chunk position is unchanged |
| 3 | `0x08007FE8` | set position (adds `coordinate[0] << 10`) |
| 4 | `0x0800800A` | the 16-bit payload query of sections 6.1/6.2 |

The three other class words this project already recorded (`0x08049548`
`0x08049604`, `0x080498B0`) resolve the same way, every entry landing on an odd
address, which is what makes the "table of self-relative offsets" reading
**CONFIRMED** rather than **INFERRED**.

**PROJECT CONCLUSION.** `0x08007E84` and `0x08007F2E`, which have **no** direct
`bl` caller anywhere in the image, are reached only through this table; that
explains LOGX-LAYER-001's observation that `0x08008086` has no `bl` caller. The
record's `+0x00` word is used as a *handler* in this ticket's sense (it is
branched through at `0x08009270`), but LOGX-LAYER-001's narrower claim - that
whether the word encodes a *class* is unresolved - is unchanged and not re-opened
here: the four class words come from the *object's* `+0x00`, not the record's.

---

## 10. `root +0x48`: the selector stream

### 10.1 Where it is decompressed and consumed

`0x08009BD4` (character-data assembly), reached from `0x080093CA` with `r1` = the
selector-1 root:

```text
08009BE4  ldr  r1, [r3, #8]      ; r1 = the root
08009BE6  ldr  r0, [r1, #0x48]   ; r0 = root[+0x48]  -> a Webfoot container address
08009BE8  ldr  r0, [r0, #4]      ; r0 = container[+0x04] = declared decoded size
08009BEA  lsrs r1, r0, #0x1F
08009BEC  adds r0, r1, r0
08009BF0  asrs r7, r0, #1        ; r7 = declared_size / 2  = the selector count
08009BF2  ldr  r0, [r1, #0x48]   ; source container again
08009BF4  add  r1, sp, #4        ; destination: a stack buffer
08009BF6  bl   0x0803D940        ; decode
08009BFA  movs r0, #1            ; i = 1
08009C02  lsls r1, r0, #1        ; 2*i
08009C04  adds r3, r1, r4
08009C06  subs r3, #0x20
08009C08  ldrh r3, [r3, #0x1E]   ; absolute[i-1]
08009C0A  ldrh r2, [r4, r1]      ; raw[i]
08009C0E  adds r2, r2, r3
08009C10  adds r2, #1
08009C12  strh r2, [r4, r1]      ; absolute[i] = raw[i] + absolute[i-1] + 1
08009C14  cmp  r0, r7
08009C16  blt  0x08009C02
```

**PROJECT CONCLUSION.** `root+0x48` is a **Webfoot container address**, and the
decoded stream is a `u16` array. `absolute[0]` is `raw[0]`; for `i >= 1`,
`absolute[i] = (raw[i] + absolute[i-1] + 1) & 0xFFFF` (the `strh` truncates).
**CONFIRMED** from the instructions above, independently of LOGExtractor and
independently of the accepted `MAP_RENDER_FORMAT.md` statement of the same
recurrence. Termination is the container's declared size, not a sentinel.

### 10.2 What each decoded value selects

```text
08009C2E  lsls r0, r4, #1
08009C32  ldrh r0, [r1, r0]      ; absolute[i]
08009C34  lsrs r0, r0, #8        ; bank = absolute[i] >> 8
08009C38  adds r5, #1            ; extend the run of equal bank
08009C3A  cmp  r5, r7
08009C46  cmp  r1, r0
08009C48  beq  0x08009C38
08009C4A  movs r3, #7
08009C4C  lsls r3, r3, #8        ; 0x700
08009C4E  add  r3, sp, r3
08009C50  ldr  r1, [r3, #8]      ; the root
08009C52  lsls r0, r0, #2
08009C54  ldr  r1, [r1, #0x4C]   ; root[+0x4C] = a u32 array
08009C56  ldr  r0, [r1, r0]      ; root[+0x4C][bank] = a container
08009C58  ldr  r1, [sp]          ; 0x4000-byte work buffer (0x08009C1C)
08009C5A  bl   0x0803D940        ; decode that container once
08009C5E  cmp  r4, r5
08009C62  lsls r0, r4, #1
08009C66  ldrh r0, [r1, r0]      ; absolute[i]
08009C6A  movs r2, #0x40         ; 64 bytes
08009C6C  lsls r0, r0, #0x18
08009C6E  lsrs r0, r0, #0x12     ; (absolute[i] & 0xFF) << 6
08009C70  adds r1, r0, r1        ; source tile inside the decoded bank
08009C72  adds r0, r6, #0        ; destination: 0x06000000 + 64*i (0x08009C20)
08009C74  bl   0x08049138        ; copy 64 bytes
08009C78  adds r6, #0x40
08009C7A  adds r4, #1
```

**PROJECT CONCLUSION.** A selector value is a **packed pair**: `value >> 8` is an
index into the `root+0x4C` array of containers ("banks"), and `value & 0xFF` is a
64-byte tile inside that bank's `0x4000`-byte decoded payload. One selector
therefore selects **one 8x8 8bpp tile**, and selector ordinal `i` becomes
character-region tile ordinal `i`. **CONFIRMED** (instruction access).

Note the run-length grouping at `0x08009C3A`..`0x08009C48`: a bank container is
decoded once per contiguous run of equal `value >> 8`, not once per selector, and
a fresh bank decodes over the same work buffer. **PROJECT OBSERVATION.**

### 10.3 Census

| Quantity | Value |
| --- | ---: |
| Selector-1 roots examined | **452** |
| Distinct roots | **421** |
| `root+0x48` values that are aligned in-ROM addresses | **452** |
| ... that decode successfully | **452** (0 failures) |
| Container kinds | kind `0` on 2 maps, kind `1` on 450 |
| Declared decoded size | 4 .. 1784 bytes, **all even** |
| Decoded selector count | 2 .. **892** words |
| Distinct selector counts | 283 |

The two kind-0 (stored) streams decode through the same `0x0803D940` path via
its `memcpy` branch, so the format does not vary with the container kind.

### 10.4 Representative streams

```text
map 39  root 0x08294968  root+0x48 = 0x08294660
        header bytes 0100000006020000  -> kind 1, declared 0x206 (518 bytes = 259 words)
        raw[:10]      = 0000 01BC 0000 0000 0000 0000 0000 0000 0000 0000
        absolute[:10] = 0000 01BD 01BE 01BF 01C0 01C1 01C2 01C3 01C4 01C5
        banks used    = 00 01 02 0A 0E 11 16 5B 5C 64 77 88

map 40  root 0x08293474  root+0x48 = 0x082932F8
        header bytes 01000000DE010000  -> kind 1, declared 0x1DE (478 bytes = 239 words)

map 0   root 0x082B8C38  root+0x48 = 0x082B8BF4
        header bytes 0100000092060000  -> kind 1, declared 0x692 (1682 bytes = 841 words)
        banks used    = 00 01 02 0B 1A 2C 2D 34 35 7D 7F B9 BA
```

### 10.5 What the selector is *not* used for

The selector value never reaches a map entry. The engine does not write it into
the payload, does not compare it against one, and does not use it to relocate
one. The decoded **stream** has exactly one consumer, the character-region writer
`0x08009BD4`; the **field** `root+0x48` has two, because `0x08009B80` also reads
its declared size (`ldr r2,[r1,#0x48]` / `asrs r2,r2,#1`) to derive the static
selector count and pair it with the `root+0x0C`/`+0x10` animation records. That
second reader takes only the size; it neither decodes nor consumes the stream, so
the selector semantics below are unaffected. **PROJECT OBSERVATION.**
Consequently "selector" names an input to character memory, and the payload's
bits 0-9 name an *output* ordinal of that same memory - a relationship the
coverage invariant of section 8.3 exercises.

---

## 11. `0x179764`

**EXTERNAL CLAIM (LOGExtractor).** Global graphics/tile-source data lives at
file/GBA-relative area `0x179764`.

**PROJECT OBSERVATION.** GBA address `0x08179764` is exactly the value held by
`root + 0x4C` on **all 452** canonical selector-1 roots. Reading its aligned
`u32` words from that address:

| Index | Value | Kind | Declared size |
| ---: | --- | ---: | ---: |
| 0 | `0x080945C0` | 1 | `0x4000` |
| 1 | `0x080959B4` | 1 | `0x4000` |
| ... | ... | 1 | `0x4000` |
| 186 | `0x08177AB8` | 1 | **`0x3C40`** |
| 187 | `0x00000001` | - | - |

The table contains **187** consecutive aligned in-ROM pointers and is immediately
followed by a non-pointer word. The maximum `value >> 8` bank index used by any
canonical selector stream is **186**, and the maximum `value & 0xFF` tile index
used is **255**, which is exactly the `0x4000 / 64` tile capacity of a bank.

**PROJECT CONCLUSION.** LOGExtractor's `0x179764` is not an independent global
graphics structure: it is the address **held by a per-descriptor pointer field**
(`root+0x4C`) and it points at an **array of Webfoot containers**, one per
selector bank. The engine reaches it only through that field
(`0x08009C54`..`0x08009C56`). In this image every root happens to hold the same
value, so the table is shared - but it is a field, not a literal.

**Correction recorded explicitly:** the structure starts at exactly `0x08179764`,
which matches LOGExtractor's address; the correction is to its *identity and
ownership*, not to its location. `0x08179764` is the **selector-bank container
pointer table referenced by scene-descriptor `+0x4C`**, with 187 entries.

The remaining entry, bank 186 at `0x08177AB8`, is the only bank that declares
less than `0x4000` (`0x3C40` = 241 tiles); the engine's fixed `0x4000` work
buffer simply leaves stale tail bytes there, and no selector in any canonical
stream addresses past tile 240 of that bank. **PROJECT OBSERVATION.**

---

## 12. The 128x128 / 256-tile hypothesis

**EXTERNAL CLAIM (LOGExtractor).** A referenced source image is 128x128 pixels =
16x16 8x8 tiles = 256 tiles.

**PROJECT OBSERVATION.** The engine allocates a **fixed `0x4000`-byte** decode
buffer for a bank (`movs r0,#1 ; lsls r0,r0,#0xE` at `0x08009C18`/`0x08009C1A`)
and indexes it with an **8-bit** field scaled by 64 (`0x08009C6C`..`0x08009C70`).

**PROJECT CONCLUSION.** `0x4000 / 64 = 256` tiles is the maximum a bank can
supply and the exact `(1 << 8) * 64` range the engine's index arithmetic can
reach; 256 tiles at 8x8 is 16x16 tiles = 128x128 pixels. So the *unit* is real
and engine-sized, but:

- it is the **bank container**, not "the global graphics source";
- it is a **fixed buffer size plus an 8-bit selector field**, not a stored
  dimension: 186 of the 187 canonical banks declare exactly `0x4000`, and one
  declares `0x3C40`;
- it is one resource class, not universal: the whole subsystem appears only
  through `root+0x4C`, and the payload side of this ticket (chunks) uses a
  different decoded size (`0x800`) and a different index width (10 bits).

Status: **PARTIALLY CONFIRMED** as an engine resource unit; **REFUTED** as a
universal claim about "source blocks" in this image. The 128x128/16x16/256
phrasing is arithmetic on the confirmed 64-byte tile and the confirmed 8-bit
field, and is labelled as derived rather than as a stored engine property.

---

## 13. The longest engine-proven chain

```text
MapEntry table 0x0808E2E0, 452 * 0x38                      [LOGX-MAP-RECORD-001]
  -> MapEntry + 0x2C -> 4*(selector-1) -> selected word     [LOGX-MAP-RECORD-001]
  -> selector-1 root  =  scene descriptor                   CONFIRMED
  -> root + 0x14 + 4*i        =  layer record               [LOGX-LAYER-001] CONFIRMED
  -> layer record + 0x00      =  handler entry, called with (r0 = i, r1 = record)
                                                            0x08009268..0x08009270  CONFIRMED
  -> record + 0x14 / + 0x15   =  chunk grid x / y           [LOGX-LAYER-001] CONFIRMED
  -> record + 0x18 + 4*cell   =  Webfoot container address   0x08007BF2  CONFIRMED
  -> decompress(0x0803D940)   ->  object + 0x4C + 0x800*k, k in 0..3
                                                            0x08007BFE..0x08007C04  CONFIRMED
  -> payload = 1024 little-endian u16, 32 columns x 32 rows 0x0800806A..0x08008074 CONFIRMED
  -> entry bits 0-9           =  tile ordinal in character memory
                                (validated against both loaders, 0/1,241,888 exceptions)
                                                            CONFIRMED
  -> character memory 0x06000000 populated by:
       static:   root + 0x48 selector stream, one 64-byte tile per selector,
                 ordinal i                                   0x08009BD4  CONFIRMED
       animated: root + 0x0C / + 0x10 records writing to their own
                 destination_tile                            0x08009B12  CONFIRMED
  -> entry bits 10/11         =  flip controls (platform BG entry layout under the
                                 engine's own 8bpp BGxCNT = 0x1C80 + 0x100*i)
                                                            PARTIALLY CONFIRMED
  -> payload row              ->  BG screenblock 0x0600E000 + i*0x800, verbatim
                                0x08007D98 / 0x080093E6      CONFIRMED
```

Remaining link marked UNRESOLVED: **which runtime state selects the MapEntry**,
and **layer positioning** (inherited as UNRESOLVED from LOGX-LAYER-001; this
ticket adds nothing).

---

## 14. Non-dominant layer handlers

The probe enumerates the `+0x18` window **only** for the dominant handler. A
record with a different handler is a structurally different record; its `+0x14`
and `+0x15` bytes are not a chunk-grid product and walking `x*y` words from it
would read unrelated bytes. The census therefore reports their shape without
dereferencing anything:

| Handler | References | Unique records | `+0x14` values | `+0x15` values | `x*y` products | First window word |
| --- | ---: | ---: | --- | --- | --- | --- |
| `0x08007A41` | 249 | 1 | `0` | `0` | `0` | `0` (one value) |
| `0x08007B63` | 1 | 1 | `64` | `192` | `12288` | one value, **outside ROM** |
| `0x080088BD` | 1 | 1 | `48` | `251` | `12048` | one value, aligned in ROM |
| `0x0800897B` | 41 | 41 | `0` x28, `85` x4, `86` x2, `170` x1, `171` x6 | `0` x1, `1` x4, `2` x1, `4` x1, `240` x9, `242` x1, `246` x2, `248` x5, `252` x1, `254` x13, `255` x3 | `0` x29, `85` x4, `21930` x2, `41382` x1, `43434` x4, `43605` x1 | four distinct values: `0x00000000` on 38 records (`null`), and `0xFFFFFF56`, `0xFFFFFFAB`, `0x000000AA` once each (all three outside the ROM address range) |

**PROJECT CONCLUSION.** LOGX-TILE-001's chunk and tile-entry format is
**CONFIRMED for handler `0x08008087` only**.

- `0x08007A41` (249 of 1808 references) allocates a **8-byte** object at
  `0x08007A40` and has no payload at all - it is the absent-layer placeholder.
- `0x08007B63` and `0x080088BD` are singletons whose dimension bytes are in the
  hundreds and cannot be a chunk grid bounded by the constructor's `cmp r6,#4`
  warm-up; nothing in this ticket shows they use the dominant representation.
- `0x0800897B` (41 records) fails the dominant representation on 29 of 41
  records (zero product) and its first window words are not all in-ROM pointers;
  LOGX-LAYER-001 already **refuted** "`+0x1C` is its content pointer", and this
  ticket does not reopen the class.

No test in this ticket runs dominant-form decoding over a non-dominant record.

---

## 15. Compression boundary

This ticket reverses only enough of the decompression path to make the decoded
formats reproducible, and explicitly does **not** absorb LOGX-CODEC-001.

| Question | Answer established here | Evidence |
| --- | --- | --- |
| Which decompressor is invoked? | `0x0803D940` dispatches on `container[+0x00]`: kind `0` -> `memcpy`, kinds `1`/`2` -> packed decoder `0x08049120`, any other kind -> no-op return | `0x0803D946`..`0x0803D964` |
| Source pointer | the container address held in the layer `+0x18` element or scene descriptor `+0x48`/`+0x4C[bank]` | `0x08007BF2`, `0x08009BF2`, `0x08009C56` |
| Destination behaviour | caller-supplied address, no bound, no return value used | `0x0803D942`, `0x08007BFE` |
| Decoded data format | `0x800` bytes = 1024 LE u16 for a dominant chunk; `2 * word_count` bytes of u16 for a selector stream; `0x4000` bytes for a bank | sections 5, 10, 12 |
| Size / termination needed | the container's own `+0x04` (declared size); no sentinel | `0x08009BE8` |
| Kind-2 in canonical dominant data | none: all 3745 dominant targets are kind 1, all 452 selector streams are kind 0 (2) or kind 1 (450) | census |

**Handed to LOGX-CODEC-001 (not answered here):** canonical wrapper behaviour in
general, the raw/uncompressed wrapper form beyond the kind-0 `memcpy` branch, the
first-word-zero disagreement, the `UnknownHeader` path, general encoder
requirements, and every other compressed asset class.

No second compression implementation was written. The probe imports
`tools.webfoot.formats.webfoot_lz` directly.

---

## 16. Full census and arithmetic

Reproduce with:

```powershell
python -m tools.research.logx_tile_probe <rom> --targets --references --chunks --selectors
python -m tools.research.logx_tile_probe <rom>            # summary only
```

Every headline count, with its unit:

| Count | Value | Unit |
| --- | ---: | --- |
| 452 | map entries | maps |
| 421 | distinct selector-1 roots | roots |
| 1516 | dominant-handler references | layer references |
| 1420 | dominant-handler unique records | layer records |
| 4274 | enumerated `+0x18` elements | chunk-grid cells |
| 156 | null cells | chunk-grid cells |
| 4118 | non-null cells | chunk-grid cells |
| 3745 | distinct non-null targets | unique pointers |
| 165 | targets with more than one reference | unique pointers |
| 10 | maximum references to one target | references |
| 3745 | distinct payload digests | unique payloads |
| 0 | payload digests shared by two targets | unique payloads |
| 3,834,880 | decoded entries (`3745 * 1024`) | tile entries |
| 2,727,181 | zero entries | tile entries |
| 2879 | distinct raw 16-bit values | unique raw values |
| 3,834,880 | entries with high nibble `0x0` | tile entries |
| 1,241,888 | nonzero tile-index references (unique-target expansion) | tile entries |
| 0 | references outside both tile loaders' ranges | tile entries |
| 452 | decoded selector streams | maps |
| 187 | bank table entries | unique pointers |

Arithmetic checks: `4274 = 156 + 4118`; `3745 <= 4118`;
`3,834,880 = 3745 * 1024`; `2,727,181 + 1,107,699 = 3,834,880` (the remainder is
the nonzero entries); `165 <= 3745`; `187 = 186 + 1` and the largest bank index
used is `186`.

Percentages are not reported; the numerator and denominator for any ratio a
reader wants are the two rows above.

---

## 17. Representative raw chunks and entries

```text
map 39, root 0x08294968, layer slot +0x18, record 0x08293BEC, grid 3x2
  cell 0 -> container 0x082934C4
    header bytes : 01000000 00080000        (kind 1, declared 0x800)
    payload sha256: 450c3dc596a0a9bb...  (full digest in the probe output)
    words[0:32]  : 0000 0000 0000 0000 0000 0000 0000 0000
                   0027 0028 0029 002A 002B 0000 0000 0000
                   0000 0000 0000 0000 0000 0000 0000 0000
    distinct values: 82, zero entries: 716, high nibbles: {0}
  cell 1 -> container 0x082935A0
    header bytes : 01000000 00080000
    words[0:23]  : 0000 ... 0000
    words[23:32] : 0001 0002 00C2 00B4 00B5 002F 0030 0031 0032

map 39, layer slot +0x20, record 0x08294628, grid 4x2
  cell 0 -> container 0x082941FC
    words[24:32] : 0055 0056 037F 0057 004D 004E 004F 00E8
    (0x037F = 895 is this map's animated-tile destination; see section 8.3)
  cell 1 -> container 0x08294268
    words[0:32]  : 006E 006F 00E9 00EA 00AC 00EB 008F 0095
                   0096 0091 0092 0090 0091 0092 0090 008F
                   0095 0096 0091 0092 0090 0091 0092 0090
                   00EB 0056 00E9 00EA 00AC 004E 004F 0050
    zero entries: 0

first dominant target in the image, 0x08179A50
    words[0:16]  : 0001 0002 0003 0004 0005 0006 0007 0008
                   0009 000A 000B 000C 000C 000C 000C 000C
```

Representative instruction bytes (raw halfwords, little-endian, as stored):

```text
0x08007B94  26 71                strb r6,[r4,#4]     object+0x04 = layer slot index
0x08007BE0  46 43 04 2E 13 DC 00 25          muls / cmp #4 / bgt / movs r5,#0
0x08007BFE  E9 02 09 19 4C 31 35 F0          lsls r5,#0xB / add / add #0x4C / bl 0x0803D940
0x0800806A  EC 06 64 0D C9 06 89 0E          (row & 31)*64 ; (col & 31)*2
0x08008074  59 5A 00 29 D1 01                ldrh r1,[r3,r1] ; cmp r1,#0 ; bne
0x08007DB2  C0 02 47 18                      lsls r0,#0xB ; adds r7,r0,r1   (0x0600E000 + slot*0x800)
0x08009BE6  88 6C 40 68 C1 0F 08 18          ldr r0,[r1,#0x48] ; ldr r0,[r0,#4] ; size rounding
0x08009C08  5B 8E 62 5A 01 30 D2 18 01 32 62 52   the recurrence
0x08009C66  08 5A 00 99 40 22 00 06 80 0C    ldrh ; ldr ; movs r2,#0x40 ; lsls/lsrs (low byte)*64
0x08046AA4  10 47                            bx r2   (the virtual-call trampoline)
```

---

## 18. External claims, verdicts

| LOGExtractor claim | Independent verdict |
| --- | --- |
| background tiles are 8x8 pixels | **CONFIRMED**, from `asrs #3` and the 64-byte tile copy, not from platform convention |
| a chunk is 32x32 tiles / 256x256 pixels | **CONFIRMED** for the dominant class, from the 64-byte row stride, `& 31` masks and `>> 8` chunk arithmetic |
| a chunk holds little-endian 16-bit entries | **CONFIRMED**, from the `ldrh` at `0x08008074` and the verbatim row `memcpy` |
| bits 0-9 are the tile ID | **CONFIRMED**, and additionally bounded against both engine tile loaders |
| bit 10 is horizontal flip | **PARTIALLY CONFIRMED** (platform BG entry layout; no engine consumer of a payload reads it) - direction assignment |
| bit 11 is vertical flip | **PARTIALLY CONFIRMED** (platform BG entry layout; no engine consumer of a payload reads it) - direction assignment |
| bits 12-15 unused / uninterpreted | **REFUTED as a format statement.** They are zero in all canonical data and no payload consumer reads them; they are not inert to the engine's own occupancy test. Status: reserved / constant in canonical data, semantic role UNRESOLVED |
| global graphics source near file offset `0x179764` | **CORRECTED**: `0x08179764` is the value of the scene descriptor's `+0x4C` field, an array of 187 Webfoot containers - a per-descriptor field, not a global structure |
| a referenced source image is 128x128 px / 16x16 tiles / 256 tiles | **PARTIALLY CONFIRMED** as the addressed capacity of one bank (`0x4000` bytes, 8-bit index * 64); **REFUTED** as a universal source-block property |
| `root+0x48` is decompressed as a u16 sequence | **CONFIRMED** |
| running index += value; use that index; index++ | **CONFIRMED** as the same recurrence, re-derived from `0x08009C02`..`0x08009C12`; LOGExtractor's *use* of the index (a bare tile selector) is **REFUTED** - the value is a `(bank, tile)` pair |

---

## 19. Disagreements with LOGExtractor

1. `0x179764` is a descriptor field's value, not a global graphics structure.
2. The `128x128` source block is a bank's *capacity*, not a declared dimension,
   and one canonical bank is `0x3C40` bytes.
3. Bits 12-15 must not be documented as "unused": they are absent from canonical
   data and unread by any payload consumer, but a nonzero value would be read as
   "occupied" by the engine's own entry test.
4. The decoded selector value is a `(bank, tile)` pair, not a bare tile index;
   the engine's own arithmetic at `0x08009C34`/`0x08009C6E` splits it.
5. LOGExtractor's coordinate and `+0x1C` readings remain refuted by
   LOGX-LAYER-001 and are not revisited here.

---

## 20. Unresolved questions

1. **Bit 10 versus bit 11 direction.** Platform-derived; no engine consumer of a
   payload reads either bit. A reversible runtime experiment on a derived ROM (a
   single flipped entry, then a screenshot comparison) would settle it; not
   performed.
2. **Bits 12-15 semantic role.** All-zero canonically, no consumer. Whether the
   format reserves them or the 8bpp configuration merely makes them inert is not
   distinguishable from this image.
3. **Internal null in the `+0x18` window** (117 records): the constructor skips
   it silently; only runtime behaviour settles what the layer shows.
4. **`object+0x34`/`0x38`**, the offsets added to a query coordinate, are never
   written by any recovered code, so the query method's coordinate space is only
   partially explained.
5. **`root+0x34`/`+0x38`**, two `0x2000`-byte decodes into `object+0xA8`/`+0xAC`
   plus a `memcpy` to `object+0xB0` (`0x080095AA`..`0x080095C0`), are a distinct
   path this ticket bounds but does not explain. It is **not** part of the tile
   index space: 0 of 1,241,888 tile references need it.
6. **`root+0x08`/`+0x0A`** are `u16` values consumed by the same `0x0800953E`
   path (map 39: 377 x 265; map 40: 89 x 185). Meaning unknown.
7. **`0x08007B63` and `0x080088BD`** singletons: not investigated beyond
   excluding them from the dominant representation.
8. **Packed-stream internals** remain LOGX-CODEC-001's scope.

---

## 21. Reproduction and tooling

The probe is `tools/research/logx_tile_probe.py`: SHA-256 gated against the
canonical digest, read-only, deterministic (`json.dump(..., sort_keys=True)`),
sharing the accepted root/layer traversal by import, and shared-target aware -
it aggregates the entry census over **unique payloads**, never over references.
Columns describe physical shape, container kind, decoded width and raw bit
position only; no unverified semantic name appears in a column.

`tools/research/thumb_disasm.py` is extended with `decode_thumb_at`,
`iter_thumb_wide`, `linear_thumb_wide` and `find_field_extractions`. The
four-byte window is what makes `bl` decode: the constructor at `0x08007B78`
sweeps to 210 instructions with the wide window and only 208 with the legacy
two-byte window, which reports two `bl` sites as undecodable. The legacy entry
points are left unchanged so LOGX-LAYER-001's published census stays
reproducible; the distinction is documented in the module docstring.

`find_field_extractions` reports **both** the plain mask idiom
(`lsls rd,rs,#a ; lsrs rd,rd,#a`, `right_shift == 0`) and true field extraction
(`b > a`). An earlier draft of this ticket compared the two shift amounts with a
strict `>`, which made `right_shift == 0` unreachable and every "no site masks a
field of width *n*" statement above vacuously true. The defect was found during
self-check while writing the synthetic suite, fixed, and the affected numbers
were re-measured; the corrected scan reports 1532 pairs rather than 959. The
synthetic regression `tests/unit/test_thumb_disasm_field_extraction.py` pins the
behaviour so the vacuous form cannot return.

`tests/integration/test_logx_tile_rom.py` gates on the canonical ROM and skips
cleanly when it is absent; `tests/unit/test_thumb_disasm_field_extraction.py` is
portable and synthetic. Together they assert only the facts above.
