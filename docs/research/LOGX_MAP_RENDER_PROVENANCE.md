# LOGX-MAP-RENDER-001: selected map root consumer and layout

## Scope and input

Read-only investigation of the canonical Buu's Fury USA Rev. 0 image, SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, size
8,388,608 bytes. No ROM, save, state, or derived image was written. The only
analysis database touched is the existing ignored Ghidra project
`build/ghidra/projects/buus_fury_calibration`, and it was opened with
`-readOnly`.

Nothing in this document is promoted from LOGExtractor's renderer. Engine
behaviour is the primary evidence; the production renderer in
`tools/webfoot/map_render.py` is cited only as prior project evidence that
happens to agree, never as the reason a claim is accepted.

## Provenance classes

| class | meaning |
| --- | --- |
| **EXTERNAL CLAIM** | asserted by a third-party project, not evidence here |
| **PROJECT OBSERVATION** | a deterministic measurement of this ROM |
| **PROJECT CONCLUSION** | an interpretation this ticket accepts, with its classification |

## Accepted dependency

LOGX-MAP-RECORD-001 is accepted and integrated. It establishes, and this ticket
relies on:

- MapEntry table file offset `0x08E2E0`, `0x1C4` (452) fixed records, stride `0x38`.
- MapEntry `+0x00` is two physical bytes used as an ordered lookup key by
  `0x080089FC`, which loads each byte separately (`ldrb r3,[r1]` /
  `ldrb r3,[r1,#1]`). It is **not** a physical u16 field.
- The selected-root resolver is `MapEntry[+0x2C] + 4 * (selector - 1)`.
- Selector `1` therefore reads the word at `source + 0x00`.

## 1. External hypothesis source

**EXTERNAL CLAIM.** [`mainant/LOGExtractor`](https://github.com/mainant/LOGExtractor)
`MapViewer/MainForm.cs` treats the selector-1 value as a map-render root and
reads `+0x08`/`+0x0A` as width/height-like, `+0x0C`/`+0x10` as an animated-tile
sequence count and pointer, `+0x14`/`+0x18`/`+0x1C`/`+0x20` as BG0-BG3 layer
pointers, `+0x40`/`+0x44` as a connector count and pointer list, and `+0x48` as
a compressed map tileset/index-stream pointer. Its `ReadPointer` masks to 24 bits
and is not this project's pointer rule.

## 2. Resolver and root consumers

### 2.1 Resolver

**PROJECT OBSERVATION.** Thumb fetch address `0x080089CC`, six instructions:

```text
080089CC  6AC0  ldr  r0,[r0,#0x2c]     ; MapEntry -> source
080089CE  0089  lsls r1,r1,#2          ; selector * 4
080089D0  1840  adds r0,r0,r1
080089D2  4038  subs r0,#0x40          ; -64
080089D4  C06B  ldr  r0,[r0,#0x3c]     ; +60  => net +0 relative to source
080089D6  4770  bx   lr
```

The Thumb byte encodings are `c06a 8900 4018 4038 c06b 7047`.

`subs r0,#0x40` followed by `ldr r0,[r0,#0x3c]` is a single effective access at
`source + 4*selector - 4`. Selector `1` yields exactly `source + 0x00`, which
matches the accepted formula without any masking.

Direct `BL` callers, recovered by a full-ROM Thumb `BL`/`BLX` sweep and
independently agreeing with the accepted `docs/consumer-analysis.md:167-171`
census:

| caller | selector register | selector provenance |
| --- | --- | --- |
| `0x08008ABA` | byte `[r7+0x02]` | helper `0x080089A0` (**runtime-unreached path**) |
| `0x08008BC4` | byte `[r4+0x02]` | helper `0x080089A0` |
| `0x0800906A` | byte `[r4+0x02]` | helper `0x080089A0` |

### 2.2 Selector population and observed range

**PROJECT OBSERVATION.** Helper Thumb `0x080089A0`:

```text
080089A4  0029  cmp  r1,#0
080089A6  02D0  beq  -> 0x080089AE      ; selector == 0 -> resolve default
080089A8  081C  adds r0,r1,#0           ; non-zero selector returned unchanged
...
080089AE  816A  ldr  r1,[r0,#0x28]      ; MapEntry +0x28
080089B2  01D1  bne  -> 0x080089B8      ; non-null -> different path
080089B4  0120  movs r0,#1              ; null +0x28 -> selector 1
```

All 452 canonical records have `+0x28` null (accepted evidence), so the
zero-selector path always returns `1`.

**PROJECT OBSERVATION.** Both zero-selector call sites pass `r3 = 0` as the
selector argument into the map-load flow `0x08008B30`:

- `0x08008D48  movs r3,#0` before `0x08008D7A  bl 0x08008B30`.
- `0x08008E84  movs r6,#0` / `0x08008E9E adds r3,r6,#0` before
  `0x08008EA4  bl 0x08008B30`.

**PROJECT OBSERVATION.** The source array behind `+0x2C` is not a single word.
Scanning each source forward while words remain 4-byte aligned and inside ROM:

| leading run of valid words | maps |
| ---: | ---: |
| 1 | 397 |
| 2 | 38 |
| 3 | 6 |
| 4 | 3 |
| 5 | 2 |
| 6 | 1 |
| 7 | 1 |
| 8 | 1 |
| 9 | 1 |
| 10 | 1 |
| 12 | 1 |

The histogram sums to 452. 55 of 452 MapEntries expose more than one selector;
the maximum observed run is 12 (map 0).

**PROJECT CONCLUSION.** Selector use is **PARTIALLY CONFIRMED**. The engine's
only examined selector sources are the helper and one direct byte read, and the
helper's zero-selector path resolves to `1` for every canonical record. The
runtime captures already accepted at Level 3 were both selector `1`. No
executable path examined here passes a non-`1` selector, but the data supplies
multi-word sources for 55 records, so a wider range remains structurally
possible and unresolved.

### 2.3 The root consumer

**PROJECT OBSERVATION.** The root pointer is passed in `r0` to Thumb
`0x0800953E` from both map-load flows:
`0x08008BD0  bl 0x0800953E` (from `0x08008B30`) and
`0x08009078  bl 0x0800953E` (from `0x08009030`). The accepted consumer analysis
already records that a second path, `0x08008ABA -> 0x08009670`, treats the
selected value as a base and dereferences `+0x40`/`+0x44`.

**PROJECT OBSERVATION.** Ghidra decompilation of `0x0800953E` (read-only,
`build/ghidra/reports/logx-root-consumers.txt`), with `param_1` the destination
map-state structure and `param_2` the selector-1 root:

```c
param_1[0x23] = (int)param_2;                       /* dest +0x8C <- root      */
param_1[0x24] = *(int *)(param_2 + 0x1e);           /* dest +0x90 <- root+0x3C */
...
*(short *)(param_1 + 0x27) = param_2[4] + -1;       /* dest +0x9C <- root+0x08 */
*(short *)((int)param_1 + 0x9e) = param_2[5] + -1;  /* dest +0x9E <- root+0x0A */
param_1[0x25] = (ushort)param_2[4] + 0xef;          /* dest +0x94 <- root+0x08 + 239 */
param_1[0x26] = (ushort)param_2[5] + 0x9f;          /* dest +0x98 <- root+0x0A + 159 */
FUN_08009420(param_1,param_2);
FUN_0803d940(*(undefined4 *)(param_2 + 0x1a),param_1[0x2a]);  /* root+0x34 */
FUN_0803d940(*(undefined4 *)(param_2 + 0x1c),param_1[0x2b]);  /* root+0x38 */
...
param_1[0x2d] = *(byte *)(param_2 + 2);             /* dest +0xB4 <- root+0x04 */
param_1[0x2e] = *(byte *)((int)param_2 + 5);        /* dest +0xB8 <- root+0x05 */
param_1[0x2f] = *(byte *)(param_2 + 3);             /* dest +0xBC <- root+0x06 */
param_1[0x30] = *(byte *)((int)param_2 + 7);        /* dest +0xC0 <- root+0x07 */
*(undefined2 *)(param_1 + 0x29) = *param_2;         /* dest +0xA4 <- root+0x00 halfword */
*(undefined1 *)((int)param_1 + 0xa1) = *(undefined1 *)(param_2 + 1);  /* root+0x02 */
*(undefined1 *)(param_1 + 0x28) = *(undefined1 *)((int)param_2 + 3);  /* root+0x03 */
cand_frame_helper_0800938C(param_1,param_4);
```

`param_2` is typed `undefined2 *`, so `param_2[4]` is byte `+0x08`, `param_2[5]`
is byte `+0x0A`, and `param_2 + 0x1e` is byte `+0x3C`. Matching Thumb
instructions at `0x0800958A  ldrh r0,[r5,#0x8]`, `0x08009592  ldrh r0,[r5,#0xa]`,
`0x0800959A  add r0,#0xef`, `0x080095A0  add r0,#0x9f`, and
`0x0800961E-0x0800963A` confirm every access width directly.

**PROJECT OBSERVATION.** `0x0800938C` reads the root back out of the destination
(`iVar3 = *(int *)(param_1 + 0x8c)`) and uses it to select the map's BG control
values from an engine table indexed by `root+0x3C`, adding the four values the
load copied from `root+0x04..+0x07`. It also programs the five palette and
display registers and soft-resets a 0x200-byte region at `0x05000000`.

**PROJECT CONCLUSION.** The selector-1 root's consumer is **CONFIRMED** and is a
map-state loader, not a renderer: exactly one Thumb function
(`0x0800953E`, called from the two MapEntry load flows) receives the root as its
source record and copies scalar fields into a RAM map-state structure, and one
thin adapter (`0x08009670`) forwards the root's `+0x40`/`+0x44` pair to the
object registry. The root is read directly from ROM at load; it is not copied
wholesale into RAM, and its pointer fields are never rewritten into a second
ROM-resident form.

**PROJECT OBSERVATION** , root-address reachability, stated carefully. An
earlier draft of this section claimed a whole-image sweep found zero
`LDR Rd,[PC,#imm]` literals in the root range. **That claim was wrong as worded
and an independent review refuted it.** A resynchronising Thumb sweep (advance
2 bytes at every undecodable halfword; 156,963 resyncs) over file
`0x0..0x800000` decodes 114,299 `ldr rd,[pc,#imm]` instructions, of which
19,784 compute a literal inside `0x0817B1B0..0x082B8C38`; an ARM-mode sweep adds
568 more. Every one of those instruction addresses is `>= 0x0817B010`, i.e.
inside the root data region itself, where the bytes are compressed and pointer
data rather than code. The correct statement is therefore about **code**, not
about the image: no code loads a root address from a PC-relative literal.

The same review supplied an artefact-free route to the intended conclusion.
Exactly **453** word-aligned ROM words hold a value equal to one of the 421
selector-1 roots: the 452 `MapEntry+0x2C` selector-1 slots, plus one stray hold
at ROM `0x0837F900` whose value is `0x08250A24` (map 129's root). A root value
can therefore be loaded only from one of those 453 addresses, which bounds the
loading instruction to the preceding 1024 bytes. An exhaustive search there
yields exactly three Thumb candidates (`0x0807970A`, `0x08079774`, `0x08084DA8`),
all inside data regions, none with a `BL`/`BLX` caller and with incoherent
surrounding decodes , three observed against roughly 3.5 expected by chance.
ARM literal loads: zero. Thumb `ADR` decodes landing on a root: 26, all in data.
ARM `add`/`sub pc,#imm`: zero. So no code loads or computes a root address by
PC-relative constant, and the only intended access route is `MapEntry+0x2C`.

### 2.4 Semantic identity of the root

**PROJECT CONCLUSION.** The root is **CONFIRMED** as a per-map ROM-resident
**map definition template**: a load-time source record whose scalars seed the
RAM map-state structure and whose pointer fields name the map's graphics,
layer, animation, and object data. It is not a runtime render structure, a
live layer container, and not a `MapEntry`; it is the first of the MapEntry's
selector-indexed variants.

This is a structural identity, not a name. No evidence here ties the root to a
player-visible label, and the multi-selector data means the family is broader
than selector 1.

## 3. Selected-root header layout

All statistics are over the 452 selector-1 roots. "Pointer" means only
4-byte aligned and inside the 8 MiB image.

| offset | width | nulls | distinct | aligned in-ROM | physical reading |
| --- | --- | ---: | ---: | ---: | --- |
| `+0x00` | 2 | 0 | 16 | 0 | halfword; engine loads it whole (`0x08009630 ldrh r0,[r5,#0x0]`) |
| `+0x02` | 1 | 0 | 8 | 0 | byte (`0x08009634 ldrb`) |
| `+0x03` | 1 | 0 | 8 | 0 | byte (`0x08009638 ldrb`) |
| `+0x04`..`+0x07` | 1 each | 0 | 2/3/2/1 | 0 | four bytes (`0x0800961E`..`0x0800962E`) |
| `+0x08` | 2 | 0 | 18 | 0 | halfword (`0x0800958A ldrh`) |
| `+0x0A` | 2 | 0 | 19 | 0 | halfword (`0x08009592 ldrh`) |
| `+0x0C` | 4 | 274 | 7 | 0 | word; count of the `+0x10` array |
| `+0x10` | 4 | 274 | 179 | 178 | word pointer, null exactly when `+0x0C` is null |
| `+0x14`/`+0x18`/`+0x1C`/`+0x20` | 4 | 0 | 330/319/398/420 | 452 each | aligned ROM pointers |
| `+0x24` | 4 | 230 | 21 | 0 | word count |
| `+0x28` | 4 | 230 | 205 | 222 | word pointer, null exactly when `+0x24` is null (walked at a 0x18-byte stride, section 7) |
| `+0x2C` | 4 | 230 | 136 | 222 | word pointer |
| `+0x30` | 4 | 0 | 183 | 0 | word, not pointer-shaped |
| `+0x34`, `+0x38` | 4 | 0 | 362/245 | 452 each | aligned ROM pointers |
| `+0x3C` | 4 | 451 | 2 | 0 | word, values `0` (451 roots) and `1` (map 19); used as an engine-table selector |
| `+0x40` | 4 | 104 | 8 | 0 | word count, `1..14` |
| `+0x44` | 4 | 104 | 349 | 348 | word pointer, null exactly when `+0x40` is null |
| `+0x48` | 4 | 0 | 392 | 452 | aligned ROM pointer (compressed container) |
| `+0x4C` | 4 | 0 | 1 | 452 | every root holds `0x08179764` |
| `+0x50` | 4 | 1 | 4 | 0 (451 unaligned) | word: `1` (414), `0x08008087` (36), `0` (1, map 0), `0x0800897B` (1, map 295); 451 of 452 are odd, i.e. Thumb-bit-set code pointers, and none is 4-byte aligned |
| `+0x54` | 4 | 1 | 5 | 0 (1 unaligned) | word: `0x800` (414), `0x400` (35), `0` (map 0), `0x266` (1, unaligned), `0x500` (1) |
| `+0x58`, `+0x5C` | 4 | 1 / 38 | 166 / 318 | 0 | words, not pointer-shaped |

`+0x4C` is a single shared word across all 452 roots and is not per-map data.
The `+0x50`/`+0x54` pair carries a Thumb handler word and a size word on 36
roots and the values `1`/`0x800` on 414; the same shape appears as a layer
record header (handler at `+0x00`, chunk dimensions at `+0x14`/`+0x15`), which is
recorded as a lead, not a conclusion.

Zero-count/zero-pointer coupling is exact for all three count pairs:
`+0x0C`/`+0x10` (274 both null, 178 both non-null), `+0x24`/`+0x28`
(230/222), `+0x40`/`+0x44` (104/348). No root has a count without a pointer or
a pointer without a count.

### 3.1 Shared roots

421 distinct roots for 452 records; 11 shared groups:

```text
0x0822CC08 x10  maps 163,172,175,182,184,189,194,197,201,203
0x0829C2D8 x5   maps 24,25,26,27,28
0x0822DBC4 x4   maps 161,171,181,188
0x0822DF88 x4   maps 160,170,187,192
0x08228290 x3   maps 191,196,200
0x0822BB50 x3   maps 166,178,206
0x0822C6E4 x3   maps 165,177,205
0x0822E1F0 x3   maps 159,164,176
0x0822EF84 x3   maps 157,167,180
0x0822CF28 x2   maps 162,169
0x0829D26C x2   maps 23,32
```

Every root is unique per MapEntry `+0x2C` source, but the selected words are
shared, so distinct maps can load identical map definitions.

## 4. `+0x08` and `+0x0A`

**PROJECT OBSERVATION** , instruction-level access:

```text
0800958A  ldrh r0,[r5,#0x8]     ; halfword load
0800958E  subs r0,#0x1
08009590  strh r0,[r4,#0x1c]    ; r4 = dest+0x80, so dest+0x9C = (root+0x08) - 1
08009592  ldrh r0,[r5,#0xa]
08009594  subs r0,#0x1
08009596  strh r0,[r4,#0x1e]    ; dest+0x9E = (root+0x0A) - 1
08009598  ldrh r0,[r5,#0x8]
0800959A  adds r0,#0xef         ; +239
0800959C  str  r0,[r4,#0x14]    ; dest+0x94 = (root+0x08) + 239
0800959E  ldrh r0,[r5,#0xa]
080095A0  adds r0,#0x9f         ; +159
080095A2  str  r0,[r4,#0x18]    ; dest+0x98 = (root+0x0A) + 159
```

**PROJECT OBSERVATION.** `0x080094F0` clamps two candidate coordinates against
`ldrh [dest+0x9C]` / `ldrh [dest+0x9E]` (the two `value - 1` fields) and treats
the arguments as signed 10.6 coordinates (`lsls r2,r4,#0xa`); `0x0800938C` uses
`dest+0x94`/`dest+0x98` to offset the map's BG scroll base. `0x0800953E`
chooses between the two paths by testing `root+0x3C`.

**PROJECT CONCLUSION.** `+0x08` and `+0x0A` are **CONFIRMED** as unsigned
little-endian halfwords read with `ldrh`, and are **CONFIRMED** as horizontal
and vertical map extents in pixels whose stored value is `extent - 1`. The
engine stores `extent - 1` as coordinate maxima and derives the maximum camera
scroll as `extent - 1 + 239` and `extent - 1 + 159`, i.e. `extent - 1` plus the
GBA viewport minus one. LOGExtractor's viewport addition is therefore correct in
effect: it recovers `extent + viewport - 1` from `extent - 1`. The engine never
uses these words as tile or chunk counts.

Representative raw values: map 39 `0x0179` (377) and `0x0109` (265); map 2
`0x0001` and `0x0001`; map 451 `0x0051` (81) and `0x00A1` (161). All 452 values
are non-zero. The two words are independent: map 39 is `377 x 265` and map 451
is `81 x 161`.

## 5. `+0x0C` and `+0x10`

**PROJECT OBSERVATION.** Coupling is exact: 274 roots have both zero, 178 have
both non-zero; `+0x0C` values are `0..6` and every non-zero `+0x10` is an
aligned in-ROM pointer.

**PROJECT OBSERVATION.** The accept/production renderer decodes this pair as
`count` and a `u32[count]` array of animated-tile records, each record
`{u8 frame_count, u8 tile_count, u16 destination_tile, u32 frame_pointer[]}`,
and the frame loader `0x08009B12` reads exactly `ldrsh [rec]` (frame index),
`ldr [rec+4]` (frame pointer array), `ldrb [rec+1]` (tile count), and
`ldrh [rec+2]` (destination tile), copying `tile_count * 64` bytes to
`0x06000000 + destination*64`.

**PROJECT CONCLUSION.** `+0x0C` is **CONFIRMED** as a 32-bit count and `+0x10`
as a 32-bit in-ROM pointer, null exactly when the count is zero. The pair is a
distinct subsystem from the layer pointers. Its identity as an *animated-tile*
subsystem is **PARTIALLY CONFIRMED**: the consumer function's own reads and the
VRAM copy target are established, but this ticket did not locate the instruction
site that reads `root+0x0C` / `root+0x10` out of the root itself, so the link
from root field to the `0x08009B12` loader is prior project evidence rather than
reproduced here.

## 6. `+0x14`, `+0x18`, `+0x1C`, `+0x20`

**PROJECT OBSERVATION.** All four are non-null, 4-byte aligned, in-ROM words in
all 452 roots, with 330/319/398/420 distinct values. Each target's first word is
a Thumb code pointer (odd). Observed targets:

| target `+0x00` | occurrences over 4*452 slots |
| --- | ---: |
| `0x08008087` | 1516 |
| `0x08007A41` | 249 |
| `0x0800897B` | 41 |
| `0x08007B63` | 1 |
| `0x080088BD` | 1 |

`0x08008086` (the Thumb function behind `0x08008087`) is a five-instruction
constructor that calls `0x08007B78`. `0x08007A40` (behind `0x08007A41`) is the
8-byte "absent layer" allocator; called with `(0,0)` at `0x0800923E` it returns
the shared zero-dimension record at `0x080707FC`. `0x08007B78` is the
layer-object constructor: it stores `0x08008087` at object `+0x00`, stores the
passed chunk pointer at `+0x08`, reads the layer record's chunk dimensions as
*separate bytes* at `+0x14`/`+0x15`, multiplies them, requires the product to be
`<= 4` (`0x08007BE2  cmp r6,#4`), and decompresses the container pointers at
`+0x18 + 4*i`.

`+0x50` carries the same handler word on 36 roots, so the root and the layer
records share a type-word vocabulary. Across the 1808 layer-pointer slots the
observed target handlers (the word at target `+0x00`) are `0x08008087` x1516,
`0x08007A41` x249, `0x0800897B` x41, `0x08007B63` x1, and `0x080088BD` x1. The
four root fields are pointers to layer records whose own `+0x00` is a Thumb code
pointer, `+0x14`/`+0x15` are chunk width and height bytes, and `+0x18` is a
container-pointer array. 98 roots point the **`+0x14`** slot at the shared
`0x080707FC` record, whose dimensions are `0` x `0`, which is the engine's
representation of an absent bottom layer.

**PROJECT CONCLUSION.** "Four aligned in-ROM pointers at `+0x14`/`+0x18`/
`+0x1C`/`+0x20`" is **CONFIRMED**, and they are **CONFIRMED** to be consumed by
one subsystem: the layer-object construction path (`0x08008086 -> 0x08007B78`)
and the BG control programming in `0x0800938C`. The four-layer interpretation is
**CONFIRMED**; the mapping of the four slots to GBA BG0/BG1/BG2/BG3 is
**PARTIALLY CONFIRMED**, because `0x0800938C` adds the copied `root+0x04..+0x07`
bytes to `BG0CNT..BG3CNT` in slot order, which is strong but not a direct
per-slot BG assignment.

## 7. `+0x40` and `+0x44`

**PROJECT OBSERVATION.** `+0x40` is a word count in `1..14` and `+0x44` is an
aligned in-ROM pointer, null exactly when the count is null; values are `0`
(104 roots), `1` (86), `2` (188), `3` (40), `4` (27), `5` (5), `6` (1), and
`14` (1).

**PROJECT OBSERVATION.** The accepted consumer path
`0x08008ABA -> 0x080089CC -> 0x08009670` dereferences exactly these two words:

```text
08009672  4031  adds r1,#0x40
08009676  06C9  ldm  r1,{r1,r2}      ; r1 = root+0x40, r2 = root+0x44
0800967A  08F0F3FF  bl 0x08012664
```

`0x08012664` is the object-registry population routine (accepted ROM-006
finding: iterates descriptors backward, indirect factory per descriptor, appends
results to the IWRAM registry at `0x03002A64`).

**PROJECT OBSERVATION.** The `+0x24`/`+0x28` pair, which shares the count/
pointer shape, is walked by `0x08009420` with the count at `+0x24` and the base
at `+0x28`:

```text
0800944A  606A  ldr  r0,[r4,#0x24]     ; destination count (from root+0x24)
08009452  6900  lsls r1,r5,#1
08009454  4919  adds r1,r1,r5
08009456  A06A  ldr  r0,[r4,#0x28]     ; destination base
08009458  C900  lsls r1,r1,#3          ; i*24
0800945A  4118  adds r1,r0,r1          ; element at base + i*0x18
08009462        bl   0x0800CD78
```

so `+0x28` is a base of inline 0x18-byte elements. The element's first word
selects between two dispatch targets (`0x0800CE1A` and `0x0800D15A`) by way of
the `ldr r0,[r4,#0x3c]` test at `0x08009432` and its branch at `0x08009436`.

**PROJECT OBSERVATION.** The accepted population path
(`0x08008AA0 -> 0x08009670 -> 0x08012664`) reaches `0x08012664` with the two
words loaded from root `+0x40`/`+0x44`. That routine is already established
(ROM-006) to iterate descriptors backward, call each descriptor's first word as
an indirect factory through the Thumb veneer at `0x08046AA2`, and append the
results to the IWRAM registry at `0x03002A64`. The descriptor iteration with an
independent `+4`/`+8` data pointer is visible at `0x08012664`'s caller-supplied
arguments only; this ticket did not re-derive its loop body.

**PROJECT OBSERVATION.** A `+0x18`-byte-stride walk of a pointer array *does*
exist in the same load flow, but it reads **MapEntry** fields, not root fields:

```text
08008C00  0025  movs r5,#0              ; loop index
08008C02  4079  ldrb r0,[r0,#5]         ; MapEntry +0x05: length of the +0x18 array
08008C04  0028  cmp  r0,#0
08008C06  10DD  ble  -> skip
08008C08  6068  ldr  r0,[r4,#4]         ; r4+4 = the MapEntry pointer
08008C0A  A900  lsls r1,r5,#2
08008C0C  8069  ldr  r0,[r0,#0x18]      ; MapEntry +0x18 pointer array
08008C0E  4658  ldr  r6,[r0,r1]         ; record = array[i]
08008C10  3068  ldr  r0,[r6]
08008C1C  03F0E1FD  bl 0x0800C7E2
```

MapEntry `+0x05` takes values `{0:399, 1:24, 2:14, 3:5, 4:6, 5:3, 19:1}` and is
null on exactly the 399 records whose `+0x18` is null; it is the length of that
pointer array (map 122 has 19), not a small flag.

This is recorded here specifically so LOGX-CONNECTOR-001 does not misattribute
MapEntry `+0x18`/`+0x05` evidence to the root.

**PROJECT CONCLUSION.** `+0x40` as a word count and `+0x44` as an aligned
in-ROM pointer are **CONFIRMED**; so is the exact dereference of those two words
by `0x08009670`. Whether `+0x44` addresses flat records or a table of record
pointers is **UNRESOLVED here**: no recovered instruction indexes `+0x44`, and
the only recovered consumer forwards the pair wholesale to `0x08012664`. The
objects' participation in map-to-map transitions is likewise **UNRESOLVED**;
the established consumer feeds the spatial-object registry whose subtype is
already unresolved in `docs/consumer-analysis.md`.

## 8. `+0x48`

**PROJECT OBSERVATION.** All 452 values are aligned in-ROM words, none null,
392 distinct. Thumb `0x08009BD4` reads it directly from the root and treats its
target as a Webfoot-LZ container:

```text
08009BE6  886C  ldr r0,[r1,#0x48]
08009BE8  4068  ldr r0,[r0,#4]        ; container header: decoded byte length
08009BF0  4710  asrs r7,r0,#1         ; halfword count
08009BF2  886C  ldr r0,[r1,#0x48]
08009BF6  33F0A3FE  bl 0x0803D940     ; decompress into a stack buffer
08009C02-08009C12   delta decode: abs[i] = raw[i] + abs[i-1] + 1
```

Confirmation that the compressed length really is at target `+0x04` comes from
the container at `0x080945C0`, whose first two words are `0x00000001` and
`0x00004000`, matching the accepted decoded size of the first atlas bank.

**PROJECT CONCLUSION.** `+0x48` is **CONFIRMED** as a non-null aligned in-ROM
pointer to a compressed, delta-coded u16 selector stream decompressed by
`0x0803D940`. Its interpretation as a "map tileset/index-stream pointer" is
**PARTIALLY CONFIRMED**: the compressed-selector structure is established, but
this ticket did not verify the bank/tile indexing semantics of the decoded
values. `+0x4C` is additionally **CONFIRMED** to be the single shared
`0x08179764` word that the renderer treats as the atlas-container `u32[]`
array; all 452 roots share it, so it is engine-global rather than per-map.

## 9. Multi-selector variant family

`+0x0C`/`+0x10`, `+0x24`/`+0x28`, `+0x40`/`+0x44` are three independent
count/pointer pairs. The renderer's decoded selector-1 content uses only
`+0x0C`/`+0x10` (animation), `+0x14..+0x20` (layers), `+0x48`/`+0x4C` (tile
characters), and `+0x08`/`+0x0A` (extent). `+0x24`/`+0x28` and `+0x40`/`+0x44`
share no pointers in any of the 162 roots where both are non-null.

## 10. Disagreements with LOGExtractor

| LOGExtractor | this ticket |
| --- | --- |
| selector-1 value is "the map render structure" | it is a per-map load-time definition template consumed by a state loader; the renderer is downstream of it |
| `+0x08`/`+0x0A` are width/height, adjusted by adding viewport | confirmed as `extent - 1` in pixels; the viewport addition is correct in effect but the stored value is already biased by `-1` |
| `+0x40`/`+0x44` are a connector count and pointer-list pointer | count and pointer are confirmed, and the pair is dereferenced only by the registry path; the record layout of `+0x44` was not reproduced, and no transition role is established |
| 24-bit masked pointer reads | not used; all pointer claims require 4-byte alignment and containment in the 8 MiB image |
| renderer-first field naming | physical widths and consumers established first; semantic names left provisional |

## 11. Unresolved questions

- Which engine instruction reads `root+0x0C` / `root+0x10` out of the root
  itself? The animation record loader and VRAM destination are established, but
  the read site was not recovered here.
- Does any executable path pass a selector other than `1`, and what selects it?
  55 MapEntries have multi-word sources and nothing examined derives a selector
  from a MapEntry byte.
- What object types populate `+0x24`/`+0x28` (0x18-byte elements, two dispatch
  targets at `0x0800CE1A` / `0x0800D15A`) and `+0x40`/`+0x44` (0x18-byte
  records, registry at `0x08012664`)?
- What do `+0x30`, `+0x50`, `+0x54`, `+0x58`, `+0x5C` mean? `+0x50`/`+0x54`
  hold a handler word and a size word for 36 roots, which is the same shape as a
  layer record header, so the root may itself be a member of the layer-record
  family. Not established here.
- Do `+0x0C`/`+0x10` and the layer pointers differ between selector variants of
  the same MapEntry?

## 12. Handoffs

| ticket | handoff |
| --- | --- |
| **LOGX-LAYER-001** | Layer records have Thumb handler `0x08008087` at `+0x00` (also `0x08007A41`, `0x0800897B`, `0x08007B63`, `0x080088BD`); chunk dimensions are separate bytes at `+0x14`/`+0x15`; `+0x18` is a container-pointer array; the constructor is `0x08007B78` with the 4-chunk cap at `0x08007BE2`; `0x080707FC` is the shared zero-dimension absent record; camera streaming is `0x08007C82`..`0x08007E63`. |
| **LOGX-TILE-001** | `+0x48` is a delta-coded u16 selector stream (`abs[i] = raw[i] + abs[i-1] + 1`) in a `0x0803D940` container; `+0x4C` is the shared `0x08179764` atlas `u32[]`; the VRAM copy is `0x08009C62..0x08009C78`. |
| **LOGX-CONNECTOR-001** | `+0x40` is a word count (`1..14`) and `+0x44` an aligned in-ROM pointer, null exactly when the count is null; `0x08009670` loads exactly `root+0x40`/`+0x44` with `ldm` and forwards both to registry routine `0x08012664`. No indexing of `+0x44` was recovered, so flat records vs a pointer table is open. Do not cite the `0x18`-stride pointer walk at `0x08008C00..0x08008C1C`: it reads MapEntry `+0x05`/`+0x18`, not root fields. |
| **LOGX-CODEC-001** | `+0x34` and `+0x38` are both decompressed by `0x0803D940` into 0x2000-byte buffers from `0x080095AE`/`0x080095B6`, then one is copied over the other by the `0x08049138` veneer, so one of the two is a fallback or override; the container header length at `+0x04` is read before decompression. `0x08009BD4` additionally reads `[root+0x48][+4]` as a decoded byte length before calling the same decompressor. Separately, `0x0800938C` soft-resets `0x05000000` and a second palette block only when its fourth argument is non-zero, and that argument arrives from `0x08008B30`'s stack-passed parameter; identify whether it encodes a first-load/fade condition. |

## 13. Reproduction

```powershell
python -m tools.research.logx_map_render_probe <canonical rom> --records
python -m pytest tests/integration/test_logx_map_render_rom.py
```

The Ghidra consumer report is regenerated with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\ghidra\run-logx-root-consumers.ps1 `
  -GhidraInstallDir <ghidra> -ProjectDir <project dir> `
  -ProjectName buus_fury_calibration -ProgramName buus_fury_verified.gba `
  -OutputPath build\ghidra\reports\logx-root-consumers.txt `
  -Addresses 0x080089CC,0x0800953E,0x08009670,0x08012664,0x0800938C
```

## 14. Evidence strength per conclusion

Every promoted conclusion and the evidence types that carry it. "Static raw-byte
inspection" means the probe's deterministic read of the verified image; no
conclusion below rests on correlation alone, and none rests on runtime
observation, because this ticket used no emulator and made no mutation.

| conclusion | classification | evidence types |
| --- | --- | --- |
| 452 valid aligned selector-1 roots | **CONFIRMED** | static raw-byte inspection; table-wide consistency; pointer-range/alignment evidence; existing project evidence |
| selector-1 root consumer is `0x0800953E`, called from two MapEntry load flows | **CONFIRMED** | caller/callee cross-reference; instruction access-width evidence; code/dataflow evidence (read-only decompilation) |
| no **code** loads or computes a root address by PC-relative constant; exactly 453 ROM words hold a root value | **CONFIRMED** | resynchronising full-image Thumb and ARM instruction scans; exhaustive word-alignment search for root values; table-wide consistency over the 452 known roots |
| root identity as a per-map load-time definition template | **CONFIRMED** (structural) | code/dataflow evidence; instruction access-width evidence; caller/callee cross-reference |
| `+0x08`, `+0x0A` are halfwords read by `ldrh`, holding `extent - 1` | **CONFIRMED** | instruction access-width evidence; code/dataflow evidence (`+0xEF`/`+0x9F` and the `-1` stores); table-wide consistency of the value ranges |
| `+0x0C` count, `+0x10` pointer, null-coupled on 274 roots | **CONFIRMED** (physical) | static raw-byte inspection; table-wide consistency |
| `+0x14`/`+0x18`/`+0x1C`/`+0x20` are aligned in-ROM layer-record pointers | **CONFIRMED** | static raw-byte inspection; pointer-range/alignment evidence; instruction evidence at the target (`0x08007B78` reads `+0x14`/`+0x15` bytes) |
| the four-layer interpretation (one subsystem consumes all four) | **CONFIRMED** | caller/callee cross-reference; code/dataflow evidence (`0x0800938C` BG control, `0x08007B78` constructor) |
| `+0x40` count and `+0x44` pointer, null-coupled on 104 roots | **CONFIRMED** | static raw-byte inspection; table-wide consistency; instruction evidence (`0x08009672`/`0x08009676`) |
| `+0x48` is a compressed delta-coded u16 selector container | **CONFIRMED** | instruction evidence (`0x08009BE6`..`0x08009C12`); raw-byte inspection of a container header at `0x0800945C0` |
| three count/pointer pairs are exactly null-coupled | **CONFIRMED** | table-wide consistency |
| `+0x4C` is the same word on all 452 roots | **CONFIRMED** | table-wide consistency |
| animated-tile identity of `+0x0C`/`+0x10` | **PARTIALLY CONFIRMED** | instruction evidence at the record loader `0x08009B12`; existing project evidence for the root-to-loader link, which was **not** reproduced here |
| BG0/BG1/BG2/BG3 slot assignment | **PARTIALLY CONFIRMED** | instruction evidence that slot order feeds `BG0CNT..BG3CNT`; no direct per-slot assignment recovered |
| connector/transition role of `+0x40`/`+0x44` | **PARTIALLY CONFIRMED** | existing project evidence for the registry consumer; static raw-byte inspection of the count range; record layout and transition role unresolved |
| tileset/index-stream semantics of `+0x48` payload | **PARTIALLY CONFIRMED** | instruction evidence for the container and delta decode; bank/tile indexing not re-verified |
| selector usage beyond `1` | **PARTIALLY CONFIRMED** | instruction evidence for both examined selector sources; table-wide consistency of multi-word source arrays (55 records) |
| `+0x30`, `+0x50`..`+0x5C` semantics | **UNRESOLVED** | static raw-byte inspection only |
| `+0x44` flat records vs pointer table | **UNRESOLVED** | no indexing instruction recovered |
| map-to-map transition participation | **UNRESOLVED** | no evidence; the only consumer feeds the spatial-object registry |

No claim in this document uses runtime observation or reversible mutation as
support, because neither was performed.

## 15. Evidence index

| source | use |
| --- | --- |
| `docs/research/LOGX_MAP_RECORD_PROVENANCE.md` | accepted dependency (table, key, selector formula) |
| `docs/consumer-analysis.md:14-59,167-175,236-258` | accepted resolver, caller, and registry evidence |
| `docs/research/MAP_RENDER_FORMAT.md` | prior project renderer evidence used only for cross-check |
| `tools/research/logx_map_render_probe.py` | this ticket's deterministic census |
| `tools/ghidra/LogxRootConsumers.java` | read-only Ghidra consumer report |
| `build/ghidra/reports/logx-root-consumers*.txt` | generated decompilation and cross-references (ignored, local) |
