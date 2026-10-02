# ASSET-EXPORT-MAP-HANDLERS-001 - non-dominant map-layer handlers

Evidence record for classifying the 43 map-layer references that
`ASSET-EXPORT-001` left unresolved: 41 under handler `0x0800897B`, one under
`0x08007B63` and one under `0x080088BD`.

| | |
| --- | --- |
| START SHA | `1e6b361ef3c0e76fe036a1fc83a61b15e760ab1d` (tip of `asset-export-001`) |
| Parent project baseline | `a commit consolidated into a later one` |
| Superseded freeze | `359d346d83cb0cc380ae9627d0be76455692c58d` (handler `0x0800897B` misclassified; see §9) |
| END SHA | (filled at freeze) |
| Branch | `asset-export-map-handlers-001` |
| Canonical ROM SHA-256 | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| ROM access | read-only, hash verified before and after every run |

Three evidence classes are separated throughout:

* **ENGINE OBSERVATION** - what an instruction in the image does, cited by
  address.
* **PROJECT INTERPRETATION** - what this ticket concludes from that, with a
  status.
* **EXPORTER CONSEQUENCE** - what the resource library does as a result.

---

## 1. The unresolved census this ticket started from

**ENGINE OBSERVATION.** `ASSET-EXPORT-001` classified the four root layer slots
`root + 0x14 / +0x18 / +0x1C / +0x20` by the `+0x00` word of the record they
point at. Over the 452 `MapEntry` records that is 1,808 references and 1,464
unique records:

| `+0x00` word | Unique records | References | Prior status |
| --- | ---: | ---: | --- |
| `0x08008087` | 1420 | 1516 | dominant chunk grid, rendered |
| `0x08007A41` | 1 | 249 | shared zero-dimension absent placeholder |
| `0x0800897B` | 41 | 41 | unresolved |
| `0x08007B63` | 1 | 1 | unresolved |
| `0x080088BD` | 1 | 1 | unresolved |

**PROJECT INTERPRETATION.** The 43 unresolved references sit on 30 maps: 29 maps
carry `0x0800897B` references and no other unresolved handler, and map 19 carries
the two singletons. Every one of the 43 is a distinct record; nothing is shared.

**EXPORTER CONSEQUENCE.** Those 30 maps had their composites withheld with the
status `withheld_unresolved_layer`.

---

## 2. How a layer record is consumed - the calling convention

**ENGINE OBSERVATION.** The installer is `0x0800924C`, reached from the
background programmer `0x0800938C` at `0x080093C0` with `r1 = root`:

```text
08009252  movs r4, #0            ; slot index
08009254  lsls r5, r4, #2
08009256  ldr  r0, [r6, r5]      ; previous object in this slot, if any
0800925c  ldr  r1, [r0]          ; its type word
0800925e  ldr  r2, [r1]          ; relative offset of its method 0
08009260  adds r2, r2, r1        ; absolute method 0 (the shared destructor)
08009264  bl   0x08046AA4        ; bx r2 - dispose the old object
08009268  adds r0, r5, r7        ; r0 = root + 4*slot
0800926a  ldr  r1, [r0, #0x14]   ; r1 = record = [root + 0x14 + 4*slot]
0800926c  adds r0, r4, #0        ; r0 = slot index
0800926e  ldr  r2, [r1]          ; r2 = record + 0x00 = constructor entry
08009270  bl   0x08046AA4        ; bx r2 - constructor(slot, record)
08009278  str  r0, [r6, r5]      ; store the new object
```

`0x08046AA4` is literally `bx r2` (`0x08046AA0..0x08046AAE` is a run of
`bx r0..r7`).

**PROJECT INTERPRETATION.** `CONFIRMED`. A layer constructor is called with
`r0 = slot index` and `r1 = record pointer`, by branching through the record's
own `+0x00` word. The stored word is therefore a constructor entry, not a type
tag and not data.

**EXPORTER CONSEQUENCE.** Each constructor can be read on its own terms; the
record layout a given handler consumes is whatever that constructor reads.

---

## 3. Handler `0x0800897B` - 41 references, 41 records, 29 maps

**ENGINE OBSERVATION - the constructor installs only a marker.** Entry
`0x0800897A`, reached with `r0 = slot` and `r1 = record` under the convention of
§2, in full:

```text
0800897A  push {r3, r4, r5, lr}
0800897C  adds r4, r0, #0        ; r4 = slot index
0800897E  adds r5, r1, #0        ; r5 = record pointer
08008980  movs r0, #0xc          ; twelve bytes
08008982  bl   0x0803D5B8        ; allocate
08008986  cmp  r0, #0
08008988  beq  0x08008992
0800898A  ldr  r1, [pc, #8]      ; pool 0x08008994 = 0x080498B0
0800898C  strb r4, [r0, #4]      ; object + 0x04 = slot byte
0800898E  str  r1, [r0]          ; object + 0x00 = 0x080498B0
08008990  str  r5, [r0, #8]      ; object + 0x08 = record pointer
08008992  pop  {r3, r4, r5, pc}
```

This routine contains no `bl 0x0803D940` (the container decoder), no
`bl 0x08049138` (the copy veneer), no `bl 0x0804912C` (the memset veneer) and no
store to a `0x04000000`-region register. Its object is twelve bytes: a type word,
a slot byte and the record pointer. Reading only this routine is where the
superseded revision of this ticket went wrong - see §9.

**ENGINE OBSERVATION - the object's own methods are the drawing path.**
`0x080498B0`, the word the constructor stores, is a descriptor of 32-bit signed
relative offsets from its own base:

| Method | Stored offset | Resolves to |
| --- | ---: | --- |
| 0 | `+0x000073AD` | `0x08050C5C` - the shared destructor shape |
| 1 | `-0x00040FC9` | `0x080088E6` |
| 2 | `-0x00040F8B` | `0x08008924` |

Method 1, `0x080088E6`, decompresses and uploads a screen-entry plane:

```text
080088E6  push {r4, r5, r6, lr}
080088E8  ldr  r3, [pc, #0xac]   ; pool 0x08008998 = 0xFFFFF800 -> -0x800
080088EA  adds r4, r0, #0        ; r4 = the object
080088EC  add  sp, r3            ; a 0x800-byte stack buffer
080088EE  ldr  r0, [r0, #8]      ; r0 = object + 0x08 = the record
080088F0  adds r6, r1, #0        ; r6 = the argument the dispatcher passed
080088F2  mov  r1, sp            ; destination = the stack buffer
080088F4  mov  r5, sp
080088F6  ldr  r0, [r0, #0x1c]   ; source = record + 0x1C  <-- the container
080088F8  bl   0x0803D940        ; decode
080088FC  ldrb r0, [r4, #4]      ; r0 = slot index
080088FE  ldr  r1, [pc, #0x9c]   ; pool 0x0800899C = 0x0600E000
08008900  movs r2, #1
08008902  lsls r0, r0, #0xb      ; slot * 0x800
08008904  adds r0, r0, r1        ; 0x0600E000 + slot * 0x800
08008906  lsls r2, r2, #0xb      ; 0x800 bytes
08008908  adds r1, r5, #0        ; source = the stack buffer
0800890A  bl   0x08049138        ; copy to the background screen area
0800890E  ldr  r1, [r4]          ; the object's type word
08008910  adds r0, r4, #0        ; r0 = the object
08008912  ldr  r2, [r1, #8]      ; method 2's relative offset
08008914  adds r2, r2, r1
08008916  adds r1, r6, #0        ; forward the argument
08008918  bl   0x08046AA4        ; bx r2 - call method 2 on this object
0800891C  movs r3, #1
0800891E  lsls r3, r3, #0xb
08008920  add  sp, r3            ; release the 0x800-byte buffer
08008922  pop  {r4, r5, r6, pc}
```

The three literals of the family are `0x08008994 = 0x080498B0` (the type word),
`0x08008998 = 0xFFFFF800` (the buffer size) and `0x0800899C = 0x0600E000` (the
background screen base).

Method 2, `0x08008924`, programs the background scroll registers from the record
and from the pointer the dispatcher forwarded in `r1`. Every comment below that
names a *role* for a field is `INFERRED`; the register reads and writes are
`CONFIRMED` by the listing itself. In full:

```text
08008924  push {r4}
08008926  ldr  r2, [r0, #8]      ; r2 = the record
08008928  ldr  r4, [r1, #0x18]   ; forwarded pointer + 0x18 (INFERRED: horizontal)
0800892A  ldr  r3, [r2, #4]      ; record + 0x04
0800892C  sub  sp, #8
0800892E  muls r3, r4, r3
08008930  ldr  r4, [r2, #0xc]    ; record + 0x0C
08008932  adds r3, r3, r4
08008934  ldr  r4, [r1, #0x30]   ; forwarded pointer + 0x30
08008936  adds r3, r3, r4
08008938  ldr  r4, [r1, #0x40]   ; forwarded pointer + 0x40
0800893A  ldr  r2, [r2, #0x14]   ; record + 0x14
0800893C  muls r2, r4, r2
0800893E  adds r2, r3, r2
08008940  str  r2, [sp]          ; horizontal term
08008942  ldr  r2, [r0, #8]      ; the record again
08008944  ldr  r4, [r1, #0x1c]   ; forwarded pointer + 0x1C (INFERRED: vertical)
08008946  ldr  r3, [r2, #4]      ; record + 0x04
08008948  muls r3, r4, r3
0800894A  ldr  r4, [r2, #0x10]   ; record + 0x10
0800894C  adds r3, r3, r4
0800894E  ldr  r4, [r1, #0x34]   ; forwarded pointer + 0x34
08008950  ldr  r1, [r1, #0x40]   ; forwarded pointer + 0x40
08008952  ldr  r2, [r2, #0x18]   ; record + 0x18
08008954  adds r3, r3, r4
08008956  muls r2, r1, r2
08008958  adds r1, r3, r2
0800895A  str  r1, [sp, #4]      ; vertical term
0800895C  ldrb r0, [r0, #4]      ; the slot byte
0800895E  movs r1, #1
08008960  lsls r1, r1, #0x1a     ; 0x04000000
08008962  lsls r0, r0, #2
08008964  adds r0, r0, r1
08008966  ldr  r1, [sp]
08008968  adds r0, #0x10         ; 0x04000010 + 4 * slot
0800896A  ldr  r2, [sp, #4]
0800896C  asrs r1, r1, #0xa
0800896E  strh r1, [r0]          ; BG{slot}HOFS
08008970  asrs r2, r2, #0xa
08008972  strh r2, [r0, #2]      ; BG{slot}VOFS
08008974  add  sp, #8
08008976  pop  {r4}
08008978  bx   lr
```

So both terms are `(scale * coordinate + offset + second term) >> 10`: the
record's `+0x04` scales the forwarded pointer's `+0x18`/`+0x1C`, `+0x0C`/`+0x10`
are constant offsets, and `+0x14`/`+0x18` scale its `+0x40`. Labelling the first
pair a viewport position and the transform a parallax scroll is `INFERRED`; only
the arithmetic is read from the instructions. The forwarded pointer is the
dispatcher's own argument (loaded at `0x080093D0` from `r5`), not the map root -
the root is reached separately at `0x080093B2` - and nothing in the image names
it.

**ENGINE OBSERVATION - both methods are dispatched on the live objects.** A whole
image sweep over every immediate `BL`/`BLX` site - enumerated with Capstone 5.0.7
rather than by a halfword mask, because no single mask selects the population
exactly - decodes exactly one caller for each of the three routines that reach
these records. Capstone confirms **29,509** immediate `BL`/`BLX` sites in the
image: **24,226 `BL`** and **5,283 `BLX`**. For reference, `hw2 & 0xD000 ==
0xD000` selects exactly the 24,226 `BL` sites and nothing else, so it is the
`BL`-only predicate, not the `BL`/`BLX` one; `hw2 & 0xC000 == 0xC000` selects
33,960 sites of which only the same 29,509 are `BL`/`BLX`. The helper
`tools/research/thumb_disasm.py::scan_thumb_bl_callers` accepts a site only when
`hw2 & 0xF800` is `0xF800` or `0xE800`, i.e. only when its `J1` and `J2` bits are
both set: it matches 17,748 sites, **16,196** of which are genuine `BL`/`BLX` -
**54.9 %** of the population, with 1,552 false positives. That is why this sweep
enumerates sites with a decoder instead of taking them from the helper. See §7.

| Routine | Callers |
| --- | --- |
| layer installer `0x0800924C` | `0x080093C2` |
| method-1 dispatcher `0x0800929C` | `0x080093D2` |
| method-2 dispatcher `0x080092BC` | `0x08009664` |

Both callers sit in the background programmer `0x0800938C`, which passes the
four-object layer array `[0x080716C4] = 0x03001990` to the installer at
`0x080093C2`/`0x080093C0` and to the method-1 dispatcher at
`0x080093D2`/`0x080093D0`. The dispatcher loads `object[+0x00]`, adds `[type + 4]`
to it and branches - i.e. it calls method 1 of whatever type the object carries.
`0x08009664` calls the method-2 dispatcher every frame with the same array, so
the scroll programming runs per frame, not once.

**ENGINE OBSERVATION - the upload destination is the map's own screen base.** The
upload address `0x0600E000 + slot * 0x800` is background screen base `28 + slot`.
The background programmer reads `root + 0x3C` at `0x080093D6`, scales it by 8 and
indexes `0x080716C4 + 0x14 = 0x080716D8`, whose row 0 is
`0x1C80 0x1D80 0x1E80 0x1F80` - screen bases 28, 29, 30, 31. For **all 42**
screen-entry layers in the image, the `BG{slot}CNT` halfword their own map's row
declares is exactly the base their slot uploads to:

| `bg_control_index` | `BGxCNT` | screen base | layers |
| ---: | ---: | ---: | ---: |
| 0 | `0x1C80` | 28 | 5 |
| 0 | `0x1D80` | 29 | 1 |
| 0 | `0x1E80` | 30 | 11 |
| 0 | `0x1F80` | 31 | 24 |
| 1 | `0x1D80` | 29 | 1 |

42 of 42 agree, with no exception. The one row-1 layer is map 19's, whose row is
`0x1C80 0x1D80 0xBE80 0x1F80`.

**The 41 records.** Field census, read directly from the image:

| Field | Observed |
| --- | --- |
| `+0x00` | `0x0800897B` on all 41 |
| `+0x04` (u32) == `+0x08` (u32) | on all 41; values `1024` (26), `614` (6), `512` (4), `409` (4), `1331` (1) |
| `+0x0C` (u32) | `0` on 37; `10240` on 2, `204800` on 2 |
| `+0x10` (u32) | `0` on 37; `10240` on 4 |
| `+0x14` (s32) | `-4096` (9), `-512` (9), `-2048` (5), `-341` (4), `341` (4), `-2560` (2), `-170` (2), `-3413`, `-1024`, `-85`, `170`, `512`, `1024` |
| `+0x18` (s32) | `0` on 38, `170`, `-170`, `-85` |
| `+0x1C` (u32) | a container pointer on all 41; the 41 references name **33 distinct** containers |
| every `+0x1C` container | kind 1, declaring `0x800` = 2048 decoded bytes |
| after `+0x1C` | not read by either method; recorded raw, extent not established |

The four records with a non-zero `+0x0C`/`+0x10` are the only ones whose `+0x04`
is `0x200`: `0x0824DB1C` (map 132 slot 3), `0x082505D8` (map 129 slot 3),
`0x082510F0` (map 128 slot 3) and `0x0825831C` (map 116 slot 3). Every
`+0x14` value is a multiple of `1024 / 12`.

**PROJECT INTERPRETATION.** `CONFIRMED` - the class is
**`STATIC_GRAPHICAL_RENDERABLE`**. The handler's object decodes
`record + 0x1C` and uploads it to the background screen area the map itself
declares for that slot, and the payload is a screen-entry plane (below). The
record fields `+0x04..+0x18` are read on this path, by method 2, so they are not
free-form padding.

`INFERRED` - the reading of `+0x04`/`+0x0C`/`+0x10`/`+0x14`/`+0x18` as a
parallax transform, with `+0x04` a 10.10 fixed-point scale (`0x400` = 1.0,
`0x200` = 0.5, `0x199` ~ 0.4, `0x266` ~ 0.6, `0x533` ~ 1.3) and `+0x14`/`+0x18`
secondary scales. The arithmetic is `CONFIRMED` - the fields are multiplied and
the product shifted right by 10 - but the transform's *purpose* is read from its
shape, not from a named engine routine, and no runtime capture was taken. The
exporter does not consume these fields: it renders the plane from `record + 0x1C`
alone, and because `+0x14`/`+0x15` are a scroll scale here rather than a chunk
grid it publishes no chunk-grid field for this record form at all (§7).

**Structural cross-check.** All 41 `+0x1C` containers decode to exactly 1024
little-endian screen entries with no non-zero high nibble, and for all 41 the
highest tile ordinal resolves inside the owning map's own assembled character
block. Rendered through the existing screen-entry renderer they are coherent art,
not noise: sky-and-cloud planes for maps 7 and 128, a complete sky-and-rock scene
for map 8, a starfield for map 20, a water surface for map 21, lava ground for
map 390.

**EXPORTER CONSEQUENCE.** All 41 references are written with
`"classification": "static_graphical_screenblock"` and `"status": "rendered"`,
each emitting a 256x256 `layer_<slot>.png` through the existing screen-entry
renderer - no second map renderer was added. The container field is taken from the
record's own `+0x00` handler word, so a `0x0800897B` record reads `+0x1C` and a
`0x08007B63` record reads `+0x04`; neither can be read at the other's offset. A
plane whose ordinals did not resolve would fail closed and withhold the composite.
Because these 41 layers now render, they also compose: the 29 maps that carry them
all gained a composite (§6).

---

## 4. Handler `0x08007B63` - 1 reference, 1 record

**ENGINE OBSERVATION.** Entry `0x08007B62` is a three-instruction argument
shuffle into the allocator family at `0x08007A60`:

```text
08007B62  adds r2, r1, #0        ; r2 = record
08007B64  adds r1, r0, #0        ; r1 = slot
08007B66  movs r0, #0
08007B68  b    0x08007A60
```

`0x08007A60` allocates `0x1008` bytes, stores the type word `0x08049604` at
`+0x00` and the slot byte at `+0x04`, then loops twice:

```text
08007A86  lsls r0, r4, #2
08007A88  adds r0, r0, r6        ; r6 = record
08007A8A  ldr  r0, [r0, #4]      ; container = [record + 4 + 4*i]
08007AA0  lsls r1, r4, #0xb      ; i * 0x800
08007AA2  adds r1, r1, r5        ; + object
08007AA4  adds r1, #8            ; destination object + 8 + 0x800*i
08007AA6  bl   0x0803D940        ; decompress
08007AAA  adds r4, #1
08007AAC  cmp  r4, #2
08007AAE  blt  0x08007A86
```

So `record + 0x04` and `record + 0x08` are container pointers, decoded into the
object's first and second 0x800-byte buffers. The family also holds a copy
routine `0x08007AB4` (32 rows per call through the copy veneer) and an update
routine `0x08007B26`, reached only indirectly.

**The canonical record.** `0x0829F808`, map 19 slot `+0x18`:

| Field | Value |
| --- | --- |
| `+0x00` | `0x08007B63` |
| `+0x04` | `0x0829F700` |
| `+0x08` | `0x0829F700` - the same container |
| `+0x0C` | `0x00000001` |
| `+0x10` | `0x00000400` |
| `+0x14`, `+0x15` | `64`, `192` |
| `+0x16` | `0x2000` |

**Container `0x0829F700`.** Kind 1, declares `0x800`, decodes to exactly 2048
bytes with its own end marker at that length. Read as little-endian `u16`:
1024 entries, ordinals `0..538`, no flip bits, no non-zero high nibble, 224
non-zero.

**PROJECT INTERPRETATION.** `CONFIRMED`. The payload is exactly the
32x32 regular-background screen-entry form a dominant chunk carries, and the
layer is **`STATIC_GRAPHICAL_RENDERABLE`**. Because `+0x04` and `+0x08` name the
same container on the canonical record, the plane is unambiguous - there is no
double-buffer question to answer.

**Structural cross-check.** Map 19's own assembled character block holds
**539** tiles, and the plane's highest tile ordinal is **538**. Every ordinal the
plane names resolves inside the map's own character block, which is what makes
the plane renderable from accepted knowledge rather than needing a new tile
source. Rendered, it is a coherent 256x256 sky-and-cloud plane, consistent with
map 19's `BG1CNT` (`0x1D80`: 8bpp, character base 0, screen base 29, 32x32 tiles).

**EXPORTER CONSEQUENCE.** One reference, written with
`"classification": "static_graphical_screenblock"` and `"status": "rendered"`,
emitting `maps/map_019/layer_1.png` at 256x256 through the existing screen-entry
renderer - no second map renderer was added. A layer whose ordinals did not
resolve would fail closed and withhold the composite.

---

## 5. Handler `0x080088BD` - 1 reference, 1 record

**ENGINE OBSERVATION.** Entry `0x080088BC`:

```text
080088BC  push {r3, lr}
080088BE  movs r0, #0
080088C0  bl   0x080080C0        ; r1 = record passes through
080088C4  pop  {r3, pc}
```

`0x080080C0` allocates `0x27A0` bytes, stores the type word `0x08049C84` at
`+0x00` and the record at `+0x04`, fills `object + 0x08 + 4*i` with the constant
`0x08071020` and `object + 0x2C + 4*i` with `0xFF` for `i = 0..8`, then:

```text
0800811E  ldr  r0, [r4, #4]      ; the record
08008120  adds r0, #4
08008122  ldrb r6, [r0]          ; byte[record + 0x04]
08008124  ldrb r0, [r0, #1]      ; byte[record + 0x05]
08008126  muls r6, r0, r6        ; grid product
08008128  cmp  r6, #9
0800812A  bgt  0x08008152        ; more than nine: skip eager loading
        ...
08008138  ldr  r0, [r0, #8]      ; container = [record + 8 + 4*i]
08008140  str  r5, [r1, #0x2c]   ; mark slot i resident
08008148  bl   0x0803D940        ; decompress into object + 0x3A0 + 0x400*i
```

and then writes `DISPSTAT` (`ORs` bit 1) and a state object at `0x08008152`
onward: `0x08008158 ldr r2,[pc,#0x344]` loads the pool at `0x080084A0` =
`0x04000200`, `0x0800815C ldrh r0,[r2]`, `0x0800815E movs r1,#2`,
`0x08008160 orrs r0,r1`, `0x08008166 strh r0,[r2]` sets bit 1. The following
`strh 0` writes are `0x04000022`/`0x04000026` (via `adds r1,r2,#0`,
`subs r1,#0xff`, `subs r1,#0xe1`), i.e. `BG2PB`/`BG2PD`, not the background
control registers. The continuation function `0x08008174` stores a type
word and clears the same `DISPSTAT` bit, and the renderer `0x08008192` reads a
viewport (`[state+0x18..+0x24]`) and issues DMA row copies with 32-byte and 64-byte
strides. `0x27A0 = 0x3A0 + 9 * 0x400` - the allocation is exactly nine resident
0x400-byte chunk buffers plus the object header.

**The canonical record.** `0x082ABF00`, map 19 slot `+0x1C`:

| Field | Value |
| --- | --- |
| `+0x00` | `0x080088BD` |
| `+0x04`, `+0x05` bytes | `14`, `10` -> grid product **140** |
| `+0x08` onward | **140** consecutive container pointers, `0x0829F814` .. `0x082ABDF4` |
| word after the run | `0x00000001` - not a pointer, the run is exactly 140 |
| `+0x14`, `+0x15` | `48`, `251` |

Every one of the 140 containers is kind 1 declaring `0x400` and decodes to
exactly 1024 bytes. The grid product `14 * 10 = 140` is exactly the length of the
pointer run, which is what ties `+0x04`/`+0x05` to the container array.

**PROJECT INTERPRETATION.** `CONFIRMED` for graphical identity: the handler
programs background registers, streams 140 decoded containers and runs a
viewport-driven DMA renderer. It is a graphical layer. `UNRESOLVED` for
assembly: the pixel arrangement of a `0x400`-byte container is not established.

The natural readings were tested and rejected rather than assumed:

* as 512 little-endian screen entries, its ordinals are `257..771`, which
  overshoot map 19's 539-tile character block - the reading is out of range. This
  is the decisive rejection: it is a hard structural failure, not a judgement
  about how the result looks;
* as a 32x32, 64x16 or 16x64 image at 8bpp the assembled 14x10 grid shows a
  central silhouette but is dithered throughout (44.8 % to 45.3 % of horizontally
  adjacent pixels differ, against 81.0 % for the same pixels shuffled, so it is
  structured but not art), and as 64x32 or 32x64 at 4bpp it is 96.2 % - above its
  own 81.7 % shuffled control, i.e. noise-like. Corroborating only: a coherence
  metric cannot by itself establish what an arrangement means.

So the class is **`STATIC_GRAPHICAL_NEEDS_UNRESOLVED_SEMANTIC`**, not
`STATIC_GRAPHICAL_RENDERABLE`. Publishing any of those images would be a guess.

**EXPORTER CONSEQUENCE.** One reference, written with
`"classification": "static_graphical_assembly_unresolved"` and
`"status": "not_rendered_assembly_unresolved"`, plus a structural probe in
`references.json`: `grid_x`, `grid_y`, `grid_product`, `chunk_targets`,
`resident_slots`, `chunk_decoded_bytes`. No image is written and the map's
composite is withheld - for a proven structural reason, not for an unknown
handler.

---

## 6. Composite reassessment

**EXPORTER CONSEQUENCE.** The composite gate changed from "every slot is the
dominant form or the absent placeholder" to "no slot is graphical-and-
unassembled". A slot that draws nothing cannot make a composite unfaithful.

| | Before | Superseded revision | Corrected |
| --- | ---: | ---: | ---: |
| Composites produced | 422 | 450 | **451** |
| Composites withheld | 30 | 2 | **1** |
| Rendered map layers | 1516 | 1517 | **1558** |
| References left unresolved | 43 | 0 | **0** |

The one map still without a composite has a proven structural reason:

| Map | Status | Reason |
| --- | --- | --- |
| 19 | `withheld_unresolved_layer` | slot `+0x1C` is graphical (handler `0x080088BD`) and its pixel arrangement is unresolved |

Map 19's renderable screen-entry layer is still exported as
`maps/map_019/layer_1.png`, so the art is preserved even though the composite is
withheld.

The 29 maps that carry a `0x0800897B` slot were all withheld at the start of this
ticket, and all 29 now carry a composite built from their four classified layers.
Against the superseded revision, 28 of those composites were already written and
every one of them changed - by 0.45 % to 23.95 % of their pixels (median 8.75 %,
measured as the fraction of pixels whose four RGBA bytes differ after PNG decode) -
and map 8 gained a composite where it had none. That is the corrected revision
replacing a composite that had silently omitted a real layer.

---

## 7. Unresolved fields, stated rather than implied

* The pixel arrangement of a `0x400`-byte container under `0x080088BD`. Its
  containers decode cleanly and its grid product matches its pointer count, but
  the tile order, tile size and destination layout were not recovered.
* The purpose of `+0x04`, `+0x0C`, `+0x10`, `+0x14` and `+0x18` on the 41
  `0x0800897B` records. Their arithmetic is read from `0x08008924` and is
  `CONFIRMED`; naming the transform a parallax scroll is `INFERRED`. The exporter
  does not consume them: it renders the plane from `record + 0x1C` alone, and
  because `+0x14`/`+0x15` are a scroll scale here rather than a chunk grid it
  publishes no chunk-grid field for this record form at all (see the
  `record + 0x14`/`+0x15` bullet below).
* The record words after `+0x1C` on the 41 records. Neither method reads them, so
  the record's extent on this path is not established. They are not published:
  the record address is in the document and the ROM is the source of record, the
  same convention the `record + 0x14`/`+0x15` bullet states.
* What `0x0800897B`'s object does between frames beyond method 2, and whether any
  other code mutates the same background screen area. Both dispatchers were
  measured, so the drawing path is complete, but the frame budget was not.
* The `0x08007B26` update routine's register arithmetic
  (`0x04000010 + 4*slot`) was read but not interpreted. It belongs to the
  `0x08007B63` family, not to `0x0800897B`.
* `record + 0x14`/`+0x15` on a non-dominant layer. On the dominant record form
  those two bytes are the chunk grid, and the exporter publishes `chunk_x`,
  `chunk_y`, `chunk_cells` and `null_chunk_cells` for it. On the screen-entry and
  unresolved-assembly forms they are not that grid: on `0x0800897B` the four
  bytes at `+0x14` are the s32 scale method 2 multiplies, and the exporter
  previously published their low halfword as a chunk extent - `0/240` on map 8
  slot 0, `171 x 242 = 41382` on map 7 slot 3, `48 x 251 = 12048` on map 19
  slot 2. No chunk-grid key is published for those classes now. The raw bytes are
  not republished under invented names either, because the established reading of
  `+0x14` on `0x0800897B` spans `+0x14..+0x17` and a published byte pair would be
  a lossy split of it; the record address is in the document and the ROM is the
  source of record.
* `tools/research/thumb_disasm.py::scan_thumb_bl_callers` accepts a `BL`/`BLX`
  site only when the second halfword's `J1` and `J2` bits are both set
  (`hw2 & 0xF800` in `(0xF800, 0xE800)`). Measured against Capstone 5.0.7 it
  matches 17,748 sites, of which 16,196 are genuine immediate `BL`/`BLX` - **54.9
  %** of the image's 29,509 such sites (24,226 `BL` + 5,283 `BLX`) - with 1,552
  false positives. Two numbers that circulated during review are wrong and are
  recorded here so they are not reused: the denominator is not 24,226 (that is
  the `BL`-only set) and not 33,960 (that over-captures by 4,451 non-`BL`/`BLX`
  patterns), and 73.3 % and 52.3 % both follow from a wrong denominator.
  `resolve_thumb_bl` in the same module carries a second, independent defect: a
  `BLX` immediate target is an ARM address and must be word-aligned, but the
  helper returns the raw `address + 4 + offset` and only clears the low bit. Of
  the sites it does match, it resolves all 14,447 genuine `BL` ones and the 881
  word-aligned `BLX` ones correctly, and returns a target 2 bytes high for the
  **868** matched `BLX` sites whose own instruction address is `2 (mod 4)` - the
  only mismatching group.
  Both defects are pre-existing, are not in this ticket's diff, and affect a
  helper other accepted tickets cite for caller censuses, so they are recorded
  here rather than repaired under this ticket. The defect cuts both ways: besides
  the 13,313 genuine sites it never matches, its 1,552 false positives can invent
  a caller - it reports one for the `0x0800897A` constructor entry at
  `0x082F3DC8`, whose halfwords `F514 EDD7` match the predicate but are an
  undefined `BLX` immediate that a decoder refuses. That is why a "zero callers"
  conclusion in particular must be re-derived with a decoder.
  The accepted census is not disturbed: `docs/research/LOGX_CODEC_PROVENANCE.md`
  records 17,748 encoding pairs, 9,624 distinct targets and 57 callers of
  `0x0803D940` for its every-even-offset walk, and re-measuring both ways here
  reproduces all three exactly - the helper's convention gives 17,748 sites and
  9,624 distinct targets, and enumerating the full 29,509-site population with a
  decoder also finds exactly 57 callers of `0x0803D940`. So the helper's defect
  does not change that accepted count, and this ticket's own single-caller
  results were re-derived over all 29,509 Capstone-confirmed sites - not over the
  `BL`-only subset - and hold, as does the accepted `0x08009670` connector claim
  (`0x08008AC2`). Fixing the helper needs its own ticket and its own
  re-validation of the censuses that cite it.

  **CORRECTED LATER (EVIDENCE-RISK-DEBT-001, 2026-09-20).** That ticket exists and
  is the one that repaired the helper, so the paragraph above is the record of what
  was believed at this revision and no longer describes live code.
  `scan_thumb_bl_callers` now enumerates sites by decoding every halfword-aligned
  window and accepts only a real four-byte `bl`/`blx`, and `resolve_thumb_bl`
  applies `Align(PC, 4)` to `BLX`. Re-measured on the canonical image, this
  document's own figures are unchanged: 17,748 predicate pairs, 16,196 genuine
  sites, 1,552 false positives, 54.9 % of 29,509, 868 matched unaligned `BLX`
  sites at 2 (mod 4), and 57 callers of `0x0803D940`. The dependency this section
  records - that nothing here may take a census from the helper - is now satisfied
  by the helper itself, and the tests that pin it live in
  `tests/integration/test_thumb_caller_census_rom.py`.

---

## 8. Artefacts and tests

* `tools/export/canonical.py` - `SCREENBLOCK_HANDLERS` (handler to container
  field), `screenblock_container_offset`, `LayerRecord.classification`,
  `.resolved`, `.renderable`, `.graphical`, `.blocks_composite`,
  `read_screenblock_entries`, `read_unresolved_assembly_probe`.
* `tools/export/buu_resource_export.py` - screen-entry collection and rendering,
  the composite gate, the refusal of an unaccounted record form, and the
  structural probe written to `references.json`. `references.json` is written
  into the sibling `_Audit` directory, not into `metadata/`.
* `tests/integration/test_asset_export_rom.py` - handler and class censuses, the
  43-reference classification, the per-handler container field, 8 representative
  screen-entry plane digests and the structural check over all 42, the
  unresolved-assembly probe, the composite digests, the written-tree status
  census and the withheld set.
* `tests/unit/test_asset_export_map_handlers.py` (portable, synthetic fixtures) -
  the handler-to-container-field registry, the refusal of a handler that is not a
  screen-entry layer, the container field being taken from the record's own
  handler word, the class and predicate table for every handler, and the
  fail-closed predicates for an unaccounted record form.

---

## 9. Correction record

This ticket was first frozen at `359d346d83cb0cc380ae9627d0be76455692c58d` with
handler `0x0800897B` classified `NON_GRAPHICAL`. Independent review falsified that
classification, and the corrected revision supersedes it. The record is kept here
because the retraction is part of the evidence.

**What the frozen revision claimed.** That the handler's constructor "performs no
decompression, no copy and no background-register write, so the slot contributes
no pixels", and that "no instruction on this path reads" the records'
`+0x04..+0x18` fields.

**Why it was wrong.** The constructor is not the object. It installs a type word,
and the engine drives the resulting object through that type's method table. The
methods of `0x080498B0` decompress `record + 0x1C` and copy it into the map's own
background screen area (§3), and they are dispatched on the live objects: method 1
by `0x0800929C` (single caller `0x080093D2`) and method 2 by `0x080092BC` (single
caller `0x08009664`, the per-frame updater - not in the background programmer).
The frozen revision also reported the record census with two counting errors and
one semantics error: the `+0x04` distribution was `0x400` (35) / `0x266` (4) /
`0x199` (3) / `0x200` (4) / `0x533` (1) where the measured values are
26 / 6 / 4 / 4 / 1; it reported `+0x0C` and `+0x10` as zero on all 41 when four
records carry non-zero values; and it described the `+0x04 == +0x08` pattern as a
regularity of a class that "reads nothing" rather than as the two parallax scales
method 2 multiplies.

**Consequence of the error.** 41 real graphical layers were written with no image;
28 composites that the frozen revision called "recovered" in fact omitted a layer
and were less faithful than the withheld state they replaced; and map 8, whose four
slots are all this handler, was left with no composite at all.

**How it was caught.** Two independent reviewers, given only the frozen revision
and the ROM, each traced the descriptor at `0x080498B0` to its methods, measured the
41 `+0x1C` containers and rejected the classification. Their measurements agree with
the ones recorded above, which were then reproduced here independently.

**What did not change.** The census of the 43 references and their 41/1/1 split, the
calling convention of §2, the map 19 screen-entry plane and its digest, the
`0x080088BD` structure and its unresolved arrangement, and every dominant-layer
image. The correction adds layers; it removes none.
