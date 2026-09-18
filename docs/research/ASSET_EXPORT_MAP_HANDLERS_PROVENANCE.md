# ASSET-EXPORT-MAP-HANDLERS-001 - non-dominant map-layer handlers

Evidence record for classifying the 43 map-layer references that
`ASSET-EXPORT-001` left unresolved: 41 under handler `0x0800897B`, one under
`0x08007B63` and one under `0x080088BD`.

| | |
| --- | --- |
| START SHA | `ac047fd6728759af9a32bd54841c19060881e7a3` (tip of `asset-export-001`) |
| Parent project baseline | `2111a819e9fdfc0820e5a089eacfa8cd03a90890` |
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

**PROJECT INTERPRETATION.** The 43 unresolved references sit on 30 maps:
29 maps carry only `0x0800897B` references, and map 19 carries the two
singletons. Every one of the 43 is a distinct record; nothing is shared.

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

## 3. Handler `0x0800897B` - 41 references, 41 records

**ENGINE OBSERVATION.** Entry `0x0800897A` in full:

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

The routine contains no `bl 0x0803D940` (the container decoder), no
`bl 0x08049138` (the copy veneer), no `bl 0x0804912C` (the memset veneer) and no
store to a `0x04000000`-region register. Its object is twelve bytes: a type word,
a slot byte and the record pointer. The word `0x080498B0` occurs exactly once in
the whole image, at `0x08008994` - nothing dispatches on it by literal load.

For comparison, the method-0 slot of every layer type's descriptor table holds a
relative offset to the same shared destructor shape, which is what the installer
calls at `0x08009264`; the `0x0800897B` object's method 0 resolves to
`0x08050C5C`, which is that shape:

```text
08050C5C  ldr  r2, [pc, #0xc]    ; the type word again
08050C5E  push {r3, lr}
08050C60  str  r2, [r0]          ; restore the type word
08050C62  cmp  r1, #0
08050C64  beq  0x08050C6A
08050C66  bl   0x0803D63C        ; free
08050C6A  pop  {r3, pc}
```

**The 41 records.** Field census, read directly from the image:

| Field | Observed |
| --- | --- |
| `+0x00` | `0x0800897B` on all 41 |
| `+0x04` == `+0x08` | on all 41; values `0x400` (35), `0x266` (4), `0x199` (3), `0x533` (1), `0x200` (4) |
| `+0x0C`, `+0x10` | `0` on all 41 |
| `+0x14`, `+0x15` | one byte `0` and the other in `2..255` on 29; `85/1` (4), `86/255` (2), `170/0` (1), `171/242..255` (5) |
| `+0x16` (`s16`) | `-1` on 34, `0` on 7 |
| `+0x18` window | 13 to 16 of the first 16 words non-zero; word 1 is a pointer to roughly `0xB0` bytes before the record |

**PROJECT INTERPRETATION.** `CONFIRMED`. The handler's constructor installs an
inert marker: it decodes nothing and touches no graphics hardware. Whatever the
41 records' `+0x04..+0x18` bytes describe, no instruction on this path reads them,
so they cannot be a chunk grid, a container pointer array or a screen-entry map
consumed by this handler. The class is **`NON_GRAPHICAL`**.

The record fields are *not* promoted to semantics. They are recorded raw. The
observation that `+0x04 == +0x08` and that `+0x0C`/`+0x10` are zero is stated as
a measured regularity of this class, not as a schema.

**EXPORTER CONSEQUENCE.** All 41 references are written with
`"classification": "non_graphical"` and `"status": "not_graphical"`. They no
longer withhold a composite, because a slot that draws nothing cannot make a
composite unfaithful.

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
| `+0x16` | `0x0020` |

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

and then writes `DISPCNT` (`ORs` bit 2) and a state object at `0x08008152`
onward. The continuation function `0x08008174` stores a type word and clears the
same `DISPCNT` bit, and the renderer `0x08008192` reads a viewport
(`[state+0x18..+0x24]`) and issues DMA row copies with 32-byte and 64-byte
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
  overshoot map 19's 539-tile character block - the reading is out of range;
* as a 32x32, 64x16, 16x64 or 32x64 image at 8bpp, and as 64x32 or 32x64 at
  4bpp, the assembled 14x10 grid is noise (44% to 96% of horizontally adjacent
  pixels differ), not art.

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

| | Before | After |
| --- | ---: | ---: |
| Composites produced | 422 | **450** |
| Composites withheld | 30 | **2** |
| Rendered map layers | 1516 | **1517** |
| References left unresolved | 43 | **0** |

The two maps still without a composite, each for a proven structural reason:

| Map | Status | Reason |
| --- | --- | --- |
| 19 | `withheld_unresolved_layer` | slot `+0x1C` is graphical (handler `0x080088BD`) and its pixel arrangement is unresolved |
| 8 | `withheld_no_renderable_layer` | all four slots are `non_graphical`; there is no graphical layer to compose and no layer dimension to size a canvas from |

Map 19's renderable screenblock layer is still exported as
`maps/map_019/layer_1.png`, so the art is preserved even though the composite is
withheld.

---

## 7. Unresolved fields, stated rather than implied

* The pixel arrangement of a `0x400`-byte container under `0x080088BD`. Its
  containers decode cleanly and its grid product matches its pointer count, but
  the tile order, tile size and destination layout were not recovered.
* `+0x0C`, `+0x10`, `+0x14`, `+0x15`, `+0x16` on the two graphical records, and
  the whole `+0x04..+0x18` span on the 41 `non_graphical` records. The
  constructors do not read them, so they are recorded raw.
* What a `non_graphical` slot does at run time. This ticket establishes what it
  does *not* do - draw - and does not name a role.
* The `0x08007B26` update routine's register arithmetic
  (`0x04000010 + 4*slot`) was read but not interpreted.

---

## 8. Artefacts and tests

* `tools/export/canonical.py` - `LayerRecord.classification`, `.renderable`,
  `.graphical`, `.blocks_composite`; `read_screenblock_entries`;
  `read_unresolved_assembly_probe`.
* `tools/export/buu_resource_export.py` - screenblock collection and rendering,
  the composite gate, and the structural probe written to `references.json`.
* `tests/integration/test_asset_export_rom.py` - handler and class censuses, the
  43-reference classification, the screenblock render and its pixel digest, the
  unresolved-assembly probe, the recovered-composite digests, and the two
  withheld maps.
