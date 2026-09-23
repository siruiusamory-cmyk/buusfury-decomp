# LOGX-CODEC-001: Buu's Fury Webfoot container and packed-stream semantics

Evidence document for the canonical Buu's Fury USA Rev. 0 image, SHA-256
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

Every claim is labelled with one status from
[`../research-conventions.md`](../research-conventions.md):

- **CONFIRMED** - directly supported by cited engine instructions, cited ROM
  bytes, or a reproducible observation scoped to this profile;
- **INFERRED** - best explanation supported by evidence, not directly proven;
- **UNKNOWN** - evidence absent, contradictory or insufficient.

Three provenance labels are used and never mixed:

- **EXTERNAL CLAIM** - a statement taken from `mainant/LOGExtractor`;
- **PROJECT OBSERVATION** - a reproducible measurement on the canonical image or
  a reading of the canonical image's own instructions;
- **PROJECT CONCLUSION** - this ticket's reasoned verdict on an observation.

Terminology is fixed here. A **container** is the eight-byte header plus the
bytes that follow it. The **wrapper** is the engine function that reads that
header and selects a payload form. The **packed stream** is the bitstream the
packed form carries. The **codec** is the algorithm that consumes a packed
stream. "JCALG1" is used only where the ticket is specifically assessing that
name, never as a synonym for the wrapper.

---

## 1. Scope and input

Research only. No GUI, renderer, Workbench or authoring change; no derived ROM;
no emulator; no mutation of the canonical image. Addresses are GBA addresses;
file offset is address minus `0x08000000`. The image was opened read-only and its
SHA-256 re-verified before and after every measurement pass.

---

## 2. Accepted dependencies used as given

| Fact | Source |
| --- | --- |
| `MapEntry` table at `0x0808E2E0`, stride `0x38`, 452 records | LOGX-MAP-RECORD-001 |
| Selector-1 root route: `MapEntry[+0x2C]` -> leading run of aligned in-ROM words -> `word[0]` | LOGX-MAP-RENDER-001 |
| Root layer slots `+0x14`, `+0x18`, `+0x1C`, `+0x20`; handler word at record `+0x00` | LOGX-LAYER-001 |
| Dominant handler `0x08008087`; array indexed `record + 0x18 + 4*i`; bound `record[+0x14] * record[+0x15]`; every element points directly at a container | LOGX-TILE-001 |
| `root + 0x48` is a container address whose decoded `u16` array feeds the accepted selector recurrence; `root + 0x4C` is a container pointer table with 187 entries at `0x08179764` | LOGX-TILE-001 |
| Project container decoder `tools/webfoot/formats/webfoot_lz.py` | TOOLKIT-010 |

This ticket does not re-derive those routes. It re-runs them through
`tools/research/logx_codec_probe.py`.

---

## 3. EXTERNAL CLAIMS AND THEIR DISPOSITION

**EXTERNAL CLAIM (LOGExtractor, older `Gba/JCALG1.cs` path).** A leading wrapper
word of zero means approximately "empty data".

**EXTERNAL CLAIM (LOGExtractor, later MapViewer / ImageScan /
CharacterSpriteExtractor paths).** A leading wrapper word of zero means
approximately "the following declared decoded-size bytes are stored raw".

**EXTERNAL CLAIM (LOGExtractor, `UnknownHeader` path).** Four bytes are skipped,
compressed data is decoded without the ordinary wrapper header, decoding runs
until a codec end marker, into a temporary buffer sized around 64 KiB.

**PROJECT CONCLUSION.** The "older" and "later" readings are **not in conflict,
and neither is a statement about the tag**. The engine's dispatcher reads the
first word as a *form selector*:

```text
0803d946  ldr  r3, [r2]          ; r3 = container[+0x00]
0803d94c  cmp  r3, #0
0803d94e  beq  0x0803D95E        ; kind 0  -> memcpy(dst, container+8, container[+0x04])
0803d950  cmp  r3, #1
0803d952  beq  0x0803D958        ; kind 1  -> packed decoder
0803d954  cmp  r3, #2
0803d956  bne  0x0803D95C        ; other   -> return, destination untouched
0803d958  bl   0x08049120        ; Thumb->ARM stub -> IWRAM 0x03000040
0803d95c  pop  {r3, pc}
0803d95e  ldr  r2, [r2, #4]      ; declared decoded size = container[+0x04]
0803d960  bl   0x08046D18        ; ROM ARM memcpy (not a stub)
0803d964  b    0x0803D95C
```

A zero first word selects `memcpy(dst, container + 8, container[+0x04])`. It
copies **the second word's length**, so it is "raw/uncompressed payload follows",
not "empty", whenever the second word is non-zero, and it is *exactly* "empty"
when the second word is zero. Both external readings describe one branch of this
one dispatcher from opposite ends. **CONFIRMED** from the instructions above.

The `UnknownHeader` claim is **REFUTED as a separate container form** for the
canonical image: see section 11.

---

## 4. ENGINE DECODE ENTRY POINTS

### 4.1 The wrapper dispatcher

`0x0803D940`, Thumb. **CONFIRMED** (instruction access). Its first instruction
is `adds r2, r0, #0`, which discards the incoming `r2`; the routine therefore
takes exactly **two** arguments:

| Argument | Register | Meaning |
| --- | --- | --- |
| 1 | `r0` | source container address |
| 2 | `r1` | destination buffer address |

No length is passed and none is derived. `0x0803D940` has **57** Thumb `BL`
callers in the canonical image. Method: a raw-halfword scan of **every even
offset** over the whole 8 MiB image for `BL`/`BLX` encodings, **17,748** encoding
pairs (35,496 halfwords; each Thumb BL/BLX *pair* is one encoding), **9,624**
distinct targets.

**The every-even-offset walk is required, not a convenience.** A stride-4 walk
sees only **8,838** encoding pairs and only **30** of the 57 callers of
`0x0803D940`: 27 of the 57 sites sit at address ≡ 2 (mod 4), including two of the
four accepted sites below (`0x08009BF6`, `0x08009C5A`). So any claim of 57 must
name the every-even-offset walk. (LOGX-TILE-001 quotes `8,838 / 8,266 / 4,440`
for a different scan; the 4,440 cannot be reproduced and those figures are not
used here. Independent review's halfword-count convention gives 33,960 / 17,299
for the two strides, with the same 57 / 30 caller counts.)
The accepted call sites are among the 57:

| Caller | Consumer |
| --- | --- |
| `0x08007C04` | dominant-layer constructor (`0x08007B78`) |
| `0x08007D4C` | dominant-layer streaming install |
| `0x08009BF6` | `root + 0x48` selector stream |
| `0x08009C5A` | `root + 0x4C` selector bank |

The wrapper function itself is reached from five resource graphs; the packed
decoder underneath it is reached from all of them. **PROJECT CONCLUSION.**

### 4.2 A second dispatcher entry

`0x0803D966` is a distinct entry point that **does** use its third argument.
**CONFIRMED** from its own instructions:

```text
0803d966  adds r3, r0, #0        ; r3 = source container
0803d968  adds r0, r1, #0        ; r0 = destination
0803d96a  adds r1, r3, #0
0803d96c  adds r1, #8            ; r1 = container + 8
0803d96e  push {r4, lr}
0803d970  ldr  r4, [r3]          ; r4 = dispatch word
0803d972  cmp  r2, #0
0803d974  bne  0x0803D98C        ; r2 non-NULL -> the remapping path
0803d976  cmp  r4, #0
0803d978  beq  0x0803D984        ; kind 0 -> stored
0803d97a  cmp  r4, #1
0803d97c  bne  0x0803D982        ; other -> return, destination untouched
0803d97e  bl   0x08049120        ; kind 1 -> the same packed decoder
0803d982  pop  {r4, pc}
0803d984  ldr  r2, [r3, #4]      ; declared size
0803d986  bl   0x08049138        ; -> IWRAM 0x03000768 (block memcpy)
0803d98a  pop  {r4, pc}
0803d98c  cmp  r4, #0            ; r2 non-NULL and kind 0
0803d98e  beq  0x0803D99A
0803d990  cmp  r4, #1
0803d992  bne  0x0803D98A
0803d994  bl   0x080491A8        ; -> alt decoder, IWRAM 0x03000CA0
0803d998  pop  {r4, pc}
0803d99a  ldr  r3, [r3, #4]
0803d99c  bl   0x0804918C        ; -> alt decoder, IWRAM 0x030002DC
```

**PROJECT CONCLUSION (corrected).** `r2` is **not a length**: it is only ever
tested for NULL and then handed to two alternate routines as a **table pointer**
for a per-byte lookup (`ldrb rX, [r2, rX]`). The non-NULL branch is a
remapping/alternate decode path, not a length-aware variant of the main decoder.

`0x0803D966` has exactly **one** Thumb `BL` caller: `0x0800F3D2`, inside live
code (`0x0800F3CC ldr r2,[r4,#0x34]` / `0x0800F3D0 add r1,sp,#0x28` /
`0x0800F3D2 bl 0x0803D966`). It is **not** used by any of the four accepted call
sites above. On the NULL path it computes `r1 = container + 8` exactly as
`0x0803D940` does.

### 4.3 Where the decoder actually runs

`0x08049120` is **not code**. Its bytes are `78 47 c0 46 04 f0 1f e5 40 00 00 03`:

```text
08049120  78 47        bx pc           ; switch to ARM state at the next word
08049122  c0 46        nop
08049124  04 f0 1f e5  ldr pc, [pc, #-4]
08049128  40 00 00 03  .word 0x03000040
```

That is a Thumb->ARM interworking stub. The run at
`0x08049120`..`0x080491C8` holds **15** stubs and occupies **172** bytes
(`0x08049120`..`0x080491CC` = 13×12 + 2×8): **13** in the `ldr pc` form, each a
12-byte slot, and **2** branch stubs at `0x08049198` and `0x080491A0`, each an
8-byte slot. Measured targets:

| Stub | Target (IWRAM) | Role |
| --- | --- | --- |
| `0x08049120` | `0x03000040` | **the packed decoder** (called by `0x0803D958`, `0x0803D97E`) |
| `0x0804912C` | `0x030007A8` | **memset** (broadcasts a byte into eight registers) |
| `0x08049138` | `0x03000768` | **block memcpy** (`ldm`/`stm` loop with a word tail) |
| `0x08049144` | `0x030007FC` | not identified here |
| `0x08049150` | `0x03000388` | not identified here |
| `0x0804915C` | `0x030004C0` | not identified here |
| `0x08049168` | `0x03000858` | not identified here |
| `0x08049174` | `0x03000560` | not identified here |
| `0x08049180` | `0x03000700` | not identified here |
| `0x0804918C` | `0x030002DC` | alternate decode path, `r2`-indexed lookup (`0x0803D99C`) |
| `0x080491A8` | `0x03000CA0` | alternate decode path, `0x0803D994` |
| `0x080491B4` | `0x03000A4C` | not identified here |
| `0x080491C0` | `0x03000000` | not identified here |
| `0x08049198` | ARM branch to `0x08047040` | not identified here |
| `0x080491A0` | ARM branch to `0x08047450` | not identified here |

**PROJECT OBSERVATION (corrected).** The stored branch of `0x0803D940` does
**not** call a stub. `0x0803D960` is `bl 0x08046D18`, a **ROM-resident ARM
memcpy** (`78 47 00 00` then an `ldm`/`stm` block loop at `0x08046D1C`), and its
only caller in the image is `0x0803D960`. The stub at `0x08049138` is the stored
branch of the *second* entry, `0x0803D986`.

An earlier revision of this document claimed `0x08049138 -> 0x030007A8`, that
`0x0803D960` called it, and that `0x08049144 -> 0x03000190` was a "row copy".
All three were wrong: the target is `0x03000768`, the caller is `0x0803D986`,
and **`0x03000190` occurs zero times in the 8 MiB image** in any form. The two
false constants were also hard-coded in `webfoot_codec_reference.py`; they are
corrected there and the veneer count may not be asserted from the old table.

**Scope note on the stub table.** The rows above give each stub's measured
target. Where a row names a caller, it names the call site relevant to this
ticket's resource graphs, **not** the stub's complete caller count: `0x08049120`
has 10 callers in the image and `0x08049138` has 164. The table is a target
census, not a caller census, and no row is exhaustive on callers.

**PROJECT OBSERVATION (base CONFIRMED, not INFERRED).** The startup code copies
the blob with DMA3. The literal at `0x08000150` is `0x00001007`, but that is only
the *source* of the count: the register value is built at
`0x08000118`..`0x08000124` (`lsrs r1, r1, #2` then `orr r1, r1, #0x84000000`) and
stored 32-bit at `0x040000DC`:

```text
08000148  .word 0x087B79A4   ; source address
0800014C  .word 0x03000000   ; destination address
08000150  .word 0x00001007   ; literal source of the count
08000118  ldr  r1, [pc, #0x30]
0800011c  lsrs r1, r1, #2         ; 0x00001007 >> 2 = 0x401 = 1025 units
08000120  orr  r1, r1, #0x84000000  ; CNT_H = 0x8400: enable, bit 10 = 32-bit
08000124  strne r1, [r0, #0xdc]   ; 0x040000DC = DMA3CNT
```

`CNT_H` bit 10 selects **32-bit transfer units**, so the copy is
`0x401 * 4 = ` **4,100 bytes**, from ROM `0x087B79A4` to IWRAM `0x03000000`. The
mapping **ROM `0x087B79A4` ↔ IWRAM `0x03000000`** is therefore **CONFIRMED**, and
IWRAM `0x03000040` is ROM `0x087B79E4`.

**PROJECT OBSERVATION (cross-check).** 4,100 bytes is the smallest length that
makes this document's own stub table reachable: the highest IWRAM target in it is
`0x03000CA0`, a blob offset of `0xCA0` = **3,232**. A 2,050-byte copy would leave
that row - and every row above `0x03000802` - outside the copied image.

That is consistent with the stub table above: `0x087B79E4` is `f0 4f 2d e9` =
ARM `push {r4-r11, lr}`, the function entry the dispatcher calls.

**PROJECT CONCLUSION (corrected).** The **packed decoder is the function at ROM
`0x087B79E4` = IWRAM `0x03000040` = blob base + `0x40`**. `0x087B7A9C`
(base + `0xF8`) is an *interior* label of that function - a bit-loop head that
later code branches back to - not an entry point. An earlier revision of this
document gave `0xF8` as the decoder's address, which contradicted the
dispatcher's own target.

The adjacent structure starting at `0x087B7960` (`"EEProm_V124\0"` followed by
version and IWRAM addresses) is **not** a source/destination pairing table: the
words at `0x087B7990` and `0x087B7994` point back inside that same structure. Its
semantics are **UNKNOWN** and are not relied on here.

### 4.4 The packed decoder's own constants

The engine's bias ladder is readable straight out of the blob's literal pool:

| ROM address | Value | Use |
| --- | --- | --- |
| `0x087B7CCC` | `0x000037FF` | second length-bias threshold |
| `0x087B7CD0` | `0x0000027F` | third length-bias threshold |

Both are loaded with `ldr r8, [pc, #…]` and compared against the decoded
distance (`0x087B7BD8 cmp ip, r8`, `0x087B7BE8 cmp ip, r8`). **CONFIRMED.**

---

## 5. WRAPPER FORMS

Exactly **three** wrapper forms are consumed by the engine:
:data:`kind` 0, 1 and 2. A word outside `{0, 1, 2}` returns with the destination
untouched. **CONFIRMED** from `0x0803D94C`..`0x0803D956`.

### 5.1 Ordinary wrapper layout

```text
offset  width  field              meaning
+0x00   u32    dispatch word      0 stored, 1 and 2 packed, other -> return
+0x04   u32    declared_size      decoded output length in bytes
+0x08   ...    payload            stored bytes, or the packed bitstream
```

**CONFIRMED.** Both words are read as 32-bit little-endian via `ldr`.

### 5.2 The first word

**It is a form selector whose value is used arithmetically, not a tag.** The
value also reaches the packed decoder in `r3`, see section 7.4, and the
decoder's loop prologue derives a width test from it. **CONFIRMED** for the
selection; the arithmetic reach is **INFERRED** (see 7.4).

### 5.3 First-word-zero semantics

**Semantic meaning:** select `memcpy(dst, container + 8, container[+0x04])`.
**CONFIRMED.** It does *not* mean "empty", "no payload", "sentinel" or "error",
and it is not caller- or class-dependent.

**Canonical instances reachable from the accepted resource graphs: 2.**

| Address | Resource class | Referencing root | Wrapper words | Declared | Decoded | Decoded SHA-256 |
| --- | --- | --- | --- | ---: | ---: | --- |
| `0x082B5F1C` | selector stream `root + 0x48` | `0x082B5F28` | `0`, `4` | 4 | 4 | `9c14ff2232b3d3427a3197aa999afadc58d36c2c3f855c9efcd5f1675291997a` |
| `0x082B5F94` | selector stream `root + 0x48` | `0x082B5FA0` | `0`, `4` | 4 | 4 | `b98a002565f52a2b53593a390fdcfd620a4e5783d545779e5fbbac207e995101` |

Both are `root + 0x48` selector streams declaring four bytes (two `u16`
selectors), each referenced exactly once. Both decode identically under both
implementations.

**The engine's own instance.** The dominant-layer constructor stores
`0x08070808` into the object's four resident-slot pointers *before* installing
anything (LOGX-TILE-001 section 4.4). That address holds a `0x00000000` dispatch
word and a `0x00000000` declared size, then **2,040 (`0x7F8`) zero bytes**; the
first non-zero byte is `0xFF` at `+0x800`, immediately after the container.
**PROJECT OBSERVATION.** So a zero-header container with a **zero declared size**
is not hypothetical: the engine installs one as its default for every
dominant-layer object.

**Classification, per the ticket's instruction to separate pattern from meaning:**

| | Status |
| --- | --- |
| "zero-header physical pattern" | **CONFIRMED**, first word `0`, layout unchanged, payload at `+8` |
| "zero-header semantic meaning" | **CONFIRMED**, raw/stored copy of `container[+0x04]` bytes |
| "zero first word means empty" | **REFUTED**, engine-supported and canonically observed, both with non-zero declared sizes |
| "zero first word means raw" | **CONFIRMED**, with the qualifier that the copy length is the *second* word and may be zero |

**ENGINE-SUPPORTED PATH** and **CANONICALLY OBSERVED ROM INSTANCE** are both
present here: the path is `0x0803D94C`/`0x0803D94E`; the instances are the two
selector streams plus the engine's own default container.

---

## 6. DECLARED SIZE SEMANTICS

| Question | Answer | Evidence |
| --- | --- | --- |
| Field offset | `+0x04` | `0x0803D95E ldr r2, [r2, #4]` |
| Width / endianness | `u32`, little-endian | `ldr` on a little-endian ARM7TDMI |
| Includes wrapper bytes? | **No**, it is the decoded output length | the stored branch copies exactly this many bytes from `+8` |
| Zero allowed? | **Yes**; the engine installs a size-0 default | `0x08070808` |
| Stored form copies exactly this many bytes? | **Yes** | `0x0803D95E`..`0x0803D960` |
| Packed form must produce exactly this many bytes? | See below | measured |

**Measurement over all 4,322 reachable packed containers.** The project decoder
and an independent reimplementation of the same grammar agree byte-for-byte on
**4,322 / 4,322**, and on **4,322 / 4,322** the decoded length equals the
declared size. **CONFIRMED.**

**Where the stream's own terminator falls.** Re-running each packed container to
its own control escape (ignoring the declared size) gives, for
**4,322 / 4,322**, a decoded length **exactly equal** to the declared size. The
distribution of `end-marker length − declared size` is `{0: 4322}`.

**PROJECT CONCLUSION.** The declared size is not merely a bound the decoder
happens to respect: in this corpus it is *exactly* the length the packed stream
produces, and the stream carries its own end marker at that same point. Both
termination rules agree on every canonical container, so this ticket cannot
distinguish them from corpus behaviour alone, and says so rather than picking
one. See section 9.

---

## 7. SEPARATING WRAPPER FROM CODEC

The ticket requires the layers not be conflated. They are:

```text
WEBFOOT WRAPPER   (0x0803D940, Thumb, in ROM)
  reads container[+0x00], container[+0x04]; chooses a form; passes (container+8)
      |
      +-- kind 0 ------> ROM ARM memcpy 0x08046D18
      |
      +-- kind 1 or 2 --> Thumb->ARM stub 0x08049120 -> IWRAM 0x03000040
                              |
                              v
                        PACKED BITSTREAM (the codec proper)
                              |
                              v
                        decoded bytes at the caller's destination
```

### 7.1 What belongs to the wrapper

- the dispatch word at `+0x00` and its `{0, 1, 2}` value set;
- the declared-size word at `+0x04`;
- the payload offset `+0x08`;
- the stored/packed selection;
- the "unknown kind returns with the destination untouched" behaviour;
- the absence of any destination bound and of any output-length argument.

### 7.2 What belongs to the codec

- the bit grammar over the bytes at `+0x08`;
- the literal width / base escapes;
- the distance and count codings and their bias ladder;
- the end marker.

### 7.3 What belongs to neither

The 64 KiB figure the external tooling uses is a host buffer size, not a format
property. See section 12.

### 7.4 The first word's reach into the codec

**INFERRED, and immaterial to every canonical decode.**

The packed decoder's entry from the dispatcher has `r3 = container[+0x00]`. The
loop prologue at `0x087B7A08` computes `adc r3, r4, #7` / `cmp r3, #8`. Whether
the dispatch word is copied into that register before the decoder's first
instruction, and therefore whether kind 1 and kind 2 differ in initial literal
width, is **not** established from the blob alone, because that register is set
by code outside it.

**PROJECT OBSERVATION.** The question is moot for this image, and the measurement
that shows it is `python -m tools.research.logx_codec_probe <rom> --opening`,
which reads the raw bits without involving any decoder. All **4,322** reachable
packed containers open on the same token *shape* - prefix `0 0 1`, four-bit code
`0000`, and a two-bit escape field:

| Opening token field | Value over all 4,322 packed containers |
| --- | --- |
| prefix bits `b0 b1 b2` | `0 0 1` on all 4,322 |
| four-bit code `b3..b6` | `0` (the escape) on all 4,322 |
| two-bit escape field `b7 b8` | `1` on 3,160, `0` on 1,162 |
| when the field is `1` | literal width becomes 8; **no base byte is read** |
| when the field is `0` | literal width becomes 7; an eight-bit base byte follows at `b9..b16`, with 11 distinct values across the 1,162 containers, `0x00` on 1,130 of them |

That token **assigns** the literal width before any literal is read, so whatever
width the caller supplied is overwritten in every canonical stream and cannot
affect the output.

**PROJECT CONCLUSION.** The initial-width register is **UNRESOLVED** as an engine
fact and **immaterial** as a decoding fact. The project decoder derives
`initial_literal_bits` from the dispatch word; nothing observable depends on that
choice. Recorded, not hidden, because an encoder that *relied* on the initial
width rather than writing its own escape would be relying on an unresolved fact.

The 74-versus-141 base-byte confusion that an earlier revision of this document
carried is worth stating as a caution: reading the base byte from `b8..b15`
instead of `b9..b16` silently folds the escape's own selector bit into the value.
It yields a plausible histogram and is wrong on 3,188 of the 4,322 containers.

---

## 8. THE PACKED GRAMMAR

### 8.1 Token prefixes

Every token begins with a prefix of one, two or three bits:

```text
b0 b1 b2 ...        token
1                   literal: one `width`-bit value, added to `base`
0 1 [gamma] ...     long match
0 0 0 ...           seven-bit short / control field
0 0 1 [4 bits]      four-bit code
```

**PROJECT OBSERVATION.** This is the prefix tree of
`tools.webfoot.formats.webfoot_lz._unpack_stream` and of
`tools.research.webfoot_codec_reference.decode_packed`, and the two agree
byte-for-byte on all 4,322 canonical packed containers.

**The third prefix bit is a discriminator, not part of a field, and its polarity
is inverted between the two remaining branches.** Bit 0 clear sends control to
bit 1; bit 1 clear sends it to bit 2. Bit 2 **clear** selects the seven-bit
short/control form; bit 2 **set** selects the four-bit code form. Every canonical
container opens with bit 2 set (`0 0 1`), which is why the four-bit escape is the
first thing every stream does.

A parser that reads the four-bit field at `b3` without first testing `b2` consumes
three bits that belong to the prefix and takes the wrong branch, see section 8.5.

### 8.2 Literals

A literal is one value of `width` bits, added to `base`, truncated to a byte.
`width` starts at the container's dispatch word and changes **only** at a width
escape. `base` starts at zero and changes only at a base escape. **CONFIRMED**
by the byte-exact differential.

### 8.3 Long matches

Field order is **distance code gamma, low distance bits, count gamma**.
**CONFIRMED**, measured, not guessed. Reading the two in the other order
desynchronises the canonical dominant chunk at `0x0817C144` on its fourth token
and yields a 326-byte back-reference into a 26-byte output; the two orders agree
only when the distance code is exactly 3, which is why a single small fixture
cannot distinguish them.

```text
distance_code = gamma()
if distance_code == 2:  copy(previous_distance, gamma())
distance = get(distance_bits) + ((distance_code - 3) << distance_bits)
count    = gamma()
previous_distance = distance
bias:  distance >= 0x10000 -> +3
       distance >= 0x037FF -> +2
       distance >= 0x0027F -> +1
       distance <= 0x0007F -> +4
```

The four thresholds are the engine's own constants: `0x37FF` and `0x027F` are
literal-pool words at `0x087B7CCC` and `0x087B7CD0`, and the other two are
immediates in the same cascade. **CONFIRMED.**

### 8.4 Short form and control

Prefix `0 0 0`, then a seven-bit distance field at `b3..b9`:

- **non-zero**, a short match: `count = get(2) + 2`, and the field becomes the
  new previous distance;
- **zero**, a control escape whose next two bits (`b10..b11`) select the long
  form's `distance_bits` as `get(field + 3)`; because the 3 already carried by
  the long form is added back, a field of `1` gives 4 bits, `2` gives 5, `3`
  gives 6;
- **zero after a zero control field**, the end marker: **twelve** zero bits - this
  three-bit prefix, the seven-bit field and the two-bit selector - with no payload.
  This line said "seventeen bits" until
  CQA-02-PACKED-STREAM-TERMINATION-001; the instruction trace gives
  `3 + 7 + 2 = 12`, both host readers implement twelve, and the twelve-zero-bit
  model predicted the strict reader's accept/refuse outcome on 30/30 controlled
  trials. Corrected here rather than deleted; the correction is recorded in
  [`CQA_02_PACKED_TERMINATION_RESOLUTION.md`](CQA_02_PACKED_TERMINATION_RESOLUTION.md)
  §3.8.

**CONFIRMED** by the differential.

### 8.5 Four-bit code and the width escapes

Prefix `0 0 1`, then a four-bit code `c` at `b3..b6`:

| Code | Action |
| --- | --- |
| 1 | write `base` as one byte |
| 2..15 | copy one byte from distance `c - 1` |
| 0 | the literal-width / base escape |

The escape reads a two-bit field at `b7..b8`, then:

- **field 1**, literal width becomes 8 and **no base byte is read**;
- **field 0**, literal width becomes 7 and an eight-bit `base` byte is read
  from `b9..b16`.

**CONFIRMED** by the differential, and **PROJECT OBSERVATION** on the canonical
image: all 4,322 reachable packed containers open on exactly this escape. 3,160
of them take the field-1 form and read no base; the other 1,162 read a base byte,
which is `0x00` on 1,130 of them and one of 11 distinct values overall.

`0 0 1` with a **non-zero** four-bit code is *not* an escape. That distinction
matters: an escape that reads the four-bit code before testing it against zero, or
that tests the wrong prefix bit, runs the wrong branch on the canonical opening
token and desynchronises much of the corpus.

Two independent transcription attempts made exactly this mistake during the
ticket, each producing a decoder that decoded small fixtures and diverged on
larger ones. What resolved it was a population differential, not more reading.

### 8.6 Reading the byte values directly

The grammar can also be checked without any decoder, from the raw bits, and this
is how the field order above was finally pinned down. Taking the canonical
container at `0x0817C144`: its payload bytes are `4f 11 00 20`, i.e. the
little-endian `u32` `0x2000114F`, whose bits MSB-first are
`00100000000000000001000101001111`.

| Index | Value | Role |
| --- | --- | --- |
| 0 | 0 | not a literal |
| 1 | 0 | not a long match |
| 2 | **1** | **the discriminator: this is the four-bit-code path** |
| 3..6 | `0000` | four-bit code 0, the escape |
| 7..8 | `00` | escape field 0, keep 7-bit literals, read a base byte |
| 9..16 | `00000000` | the base byte, `0x00` |

**PROJECT OBSERVATION.** Index 2 is the discriminator, and it can be got wrong
two ways, both measured:

- **Not testing it at all**, reading a four-bit field starting at index 2 -
  gives `0010 = 2`, i.e. a one-byte copy from distance 1 at output position 0,
  which fails immediately.
- **Testing it and inverting the polarity**, reading the *seven-bit* field at
  index 3 instead of the four-bit code, makes **0 of 4,322** canonical
  containers produce any output at all: 1,159 hit an end marker, 3,162 fail in a
  short back-reference and 1 in a four-bit back-reference. A total failure, and
  therefore one of the easier mistakes to catch *if* the test population is the
  real corpus rather than one fixture. (The subtler variant is a *field order*
  error inside one token, which can pass small fixtures and only desynchronise
  later.)

**Methodology note.** The `u32` must be read little-endian *and* its bits consumed
MSB-first. Reading the word as a big-endian `u32` produces a bit string that
appears nowhere in the image and makes every worked example above wrong even
though the grammar it describes is right.

---

## 9. END-OF-STREAM SEMANTICS

| Question | Answer | Status |
| --- | --- | --- |
| How does decoding terminate? | the packed stream carries a control escape; the declared size is an independent bound | **CONFIRMED** |
| Is the marker mandatory? | on all 4,322 reachable packed containers a marker is present and lands exactly at the declared size | **CONFIRMED** for this corpus |
| May it occur before the declared size? | **not observed**, the gap distribution is `{0: 4322}` | **CONFIRMED** for this corpus; behaviour on a hypothetical early marker is **UNKNOWN** |
| Is it ignored once the declared size is reached? | the two coincide on every canonical container, so the corpus cannot distinguish "stop on size" from "stop on marker" | **UNRESOLVED** from corpus evidence |
| Does it exist only for headerless streams? | no: every canonical packed stream has the wrapper *and* the marker | **CONFIRMED** |

**PROJECT CONCLUSION.** Both the declared size and the end marker are
independent and both are satisfied at the same decoder position on all 4,322
reachable packed containers. The project decoder stops on the declared size; it
does **not** require the marker to be reached, and it does **not** require the
stream to produce exactly the declared size, it clips an over-long final match
and reports success (see section 15). Which rule the hardware would obey on a
stream where the two disagree is **UNRESOLVED** and is a stated encoder
obligation below.

> **UPDATE, CQA-02-PACKED-STREAM-TERMINATION-001 (2026-09-23).** The last sentence
> above is now settled for the engine, from the engine's own instructions rather
> than from this corpus: the retail packed decoder takes `(source, destination)`,
> and none of the thirteen comparisons in its body names the destination cursor,
> so there is no length rule for a precedence question to be about. The engine
> stops on the escape and on nothing else - `CONFIRMED`, from two independent
> disassemblies plus a positive census that found no destination comparison. See
> [`CQA_02_PACKED_TERMINATION_RESOLUTION.md`](CQA_02_PACKED_TERMINATION_RESOLUTION.md)
> §2.1 and §3.6. The corpus statements in this section remain true as *corpus*
> statements and are not restated.

---

## 10. VERIFYING THE CODEC IDENTITY

**EXTERNAL CLAIM (LOGExtractor).** The compression is JCALG1, or a C# port of
JCALG1, or a JCALG1-derived LZSS variant.

**PROJECT OBSERVATION.** The engine's own decoder is consistent with the project
implementation, not merely with an upstream description of it:

| Property | Engine evidence | Project implementation |
| --- | --- | --- |
| bit order | MSB-first, `adds r6, r6, r6` on a `ldr`-fed word | MSB-first over little-endian `u32` |
| prefix tree polarity | `0x087B7A18` / `0x087B7A2C` / `0x087B7A40`: bit 2 **set** dispatches the four-bit code form (`mov r8, #4`), bit 2 **clear** falls through to the seven-bit short/control form at `0x087B7AD4` | same tree |
| literal width | the escape sets 7 or 8 bits (`0x087B7AB0` `adc r3, r4, #7`); the dispatcher also leaves the dispatch word in `r3`, so the initial width is arguably 1 or 2 | read from the dispatch word |
| two length thresholds | literal-pool words `0x37FF`, `0x027F` | same constants |
| whole-corpus result | not directly observable without a runtime capture | 4,322 / 4,322 byte-exact against a second implementation |

An independent review of this ticket enumerated every `cmp`/`subs` in the primary
decoder (`0x087B79E4`..`0x087B7C30`) and found **no comparison against `r0` or any
output counter**: all 28 involve only the bit counter, the literal width, token
fields and the bias thresholds. That is direct instruction evidence for the
"no destination bound" conclusion in section 16, not merely an absence of one.

**PROJECT CONCLUSION.** The classification this ticket can support is
**"JCALG1-like / derived, engine-consistent"**. The project cannot state
*byte-compatible JCALG1* because no pinned JCALG1 reference implementation was
compared byte-for-byte, and it will not state it from a class name. The name
`JCALG1` is **not** promoted by this ticket. Status: **PARTIALLY CONFIRMED**.

For contrast, the bit grammar's *identity* is **CONFIRMED** as the grammar the
canonical image's containers actually use: 4,322 containers, two independent
implementations, zero disagreements.

---

## 11. UNKNOWNHEADER / HEADERLESS INVESTIGATION

**EXTERNAL CLAIM (LOGExtractor).** An `UnknownHeader` path skips four bytes,
decodes compressed data without the ordinary wrapper header, runs until a codec
end marker, and writes into a temporary buffer sized around 64 KiB.

**PROJECT OBSERVATION.** The engine's packed decoder at IWRAM `0x03000040`
(= ROM `0x087B79E4`) is reached from exactly two places, both of them the
kind-1 arm of a dispatcher entry, `0x0803D958` in `0x0803D940` and `0x0803D97E`
in `0x0803D966`, through the stub at `0x08049120`, and always with
`r1 = container + 8`. `0x0803D966`'s other arm reaches two *different* routines
(`0x030002DC`, `0x03000CA0`) which also read `container + 8`. **No engine path
skips four bytes of a container and then decodes.**

Four-byte prefixes do exist in the canonical image, but they belong to
*records*, not to the codec. The clearest example is already established by prior
tickets: the dominant-layer object's chunk destination is at `object + 0x4C`,
and the engine-owned structures around it carry their own headers. A record that
stores a size and then a packed stream supplies the decoded length itself, which
is exactly what a headerless decode needs and exactly why the external tool can
decode one.

**PROJECT CONCLUSION.**

| Reading of `UnknownHeader` | Verdict |
| --- | --- |
| a separate container form the engine can be handed | **REFUTED**, the dispatcher knows only `{0,1,2}` at `+0x08` |
| headerless codec data decoded by a record that supplies the size | **CONSISTENT** with the engine, but the four bytes are the *record's* field, not a codec artefact |
| an embedded stream | not established |
| another resource-specific wrapper | not established |

**The 64 KiB figure is NOT an engine limit.** No engine instruction compares
against 65,536 anywhere in the dispatcher or the packed decoder; the largest
declared size in the reachable corpus is `0x4000` (16,384) and the project
decoder's own `MAX_OUTPUT` was an unrelated host-side safety constant. Status:
**REFUTED as an engine limit**; **INFERRED** as host-tool convenience.

---

## 12. CANONICAL CONTAINER CENSUS

Seeded from the accepted resource graphs only; no blind aligned-word sweep.

**Population.** 421 distinct selector-1 roots (from 452 `MapEntry` records), of
which **452 root references** resolve. Three resource classes are enumerated:

| Resource class | References | Unique containers | Wrapper form | Declared size range |
| --- | ---: | ---: | --- | --- |
| dominant layer chunk (`record + 0x18` array, handler `0x08008087`) | 3,912 | **3,745** | kind 1 on 3,745 | exactly `0x800` on all |
| `root + 0x48` selector stream | 421 | **392** | kind 1 on 390, kind 0 on 2 | 4 .. 1,784 |
| `root + 0x4C` selector bank | 187 | **187** | kind 1 on 187 | `0x4000` on 186, `0x3C40` on 1 |

**Headline arithmetic.**

| Quantity | Value |
| --- | ---: |
| References (sum over the three classes) | **4,520** |
| Unique containers | **4,324** |
| Unique payload digests | **4,324** |
| … payload-digest collisions | **0** |
| Packed forms (kind 1 or 2) | **4,322** |
| Stored forms (kind 0) | **2** |
| Zero-header forms | **2** |
| Compressed forms among packed | 4,322 |
| Raw forms among packed | 0 |
| Malformed candidates | **0** |
| Containers shared between classes | **0** |

`4,324 = 3,745 + 392 + 187`. `4,520 = 3,912 + 421 + 187`. The three counts are
distinct quantities and are never mixed. The 3,745 dominant-chunk figure
reproduces LOGX-TILE-001's accepted count exactly.

**Extra reach, outside the root set.** LOGX-TILE-001 recorded dominant-handler
records no selector-1 root reaches. Expanding their own `x*y` windows gives
**3,819** distinct non-null element targets, a superset of the 3,745. Every one
is a kind-1 container declaring exactly `0x800`. This ticket decodes only the
3,745 root-reachable ones for its differential and states the 3,819 as reach, not
as a decoded population. **PROJECT OBSERVATION.**

**Declared-size range over the union:** 4 .. 16,384 bytes. **CONFIRMED.**

---

## 13. KNOWN-GOOD FIXTURE SUITE

Curated, spanning classes and sizes. Digests and lengths are reproducible with
`python -m tools.research.logx_codec_probe <rom> --fixtures`; decoded payloads
are **not** committed or written anywhere.

| Label | ROM address | Resource class | Wrapper words | Declared | Decoded | Source consumed | Decoded SHA-256 |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `dominant_chunk_0` | `0x08179A50` | dominant layer chunk | `1`, `0x800` | 2,048 | 2,048 | 476 | `f7ac0e36dd93d70c22ea6288…` |
| `dominant_chunk_1` | `0x0820BE10` | dominant layer chunk | `1`, `0x800` | 2,048 | 2,048 | 288 | `b6df3104b1ef19f5538c0fc7…` |
| `dominant_chunk_2` | `0x082B8BAC` | dominant layer chunk | `1`, `0x800` | 2,048 | 2,048 | 20 | `0757872b4b26d36cd91ae3a6…` |
| `selector_stream_0` | `0x0817A75C` | `root + 0x48` | `1`, `0x388` | 904 | 904 | 12 | `4edc8d61b019dd8371c5cbc4…` |
| `selector_stream_1` | `0x0817BA28` | `root + 0x48` | `1`, `0x1DE` | 478 | 478 | 12 | `8d045c3637f6eb73a3a650b2…` |
| `selector_stream_2` | `0x082B8BF4` | `root + 0x48` | `1`, `0x692` | 1,682 | 1,682 | 56 | `9b473f15cf67eea0fa388278…` |
| `zero_header_stored` | `0x082B5F1C` | `root + 0x48` | `0`, `4` | 4 | 4 | 4 | `9c14ff2232b3d3427a3197aa…` |
| `bank_first` | `0x080945C0` | `root + 0x4C` bank | `1`, `0x4000` | 16,384 | 16,384 | 5,100 | `ccfa6a39379a38a292504012…` |
| `bank_last` | `0x08177AB8` | `root + 0x4C` bank | `1`, `0x3C40` | 15,424 | 15,424 | 7,328 | `e1c9b6dd8a61ace97e7009f8…` |
| `engine_default_container` | `0x08070808` | engine-installed default | `0`, `0` | 0 | 0 | 0 | `e3b0c442…` (SHA-256 of the empty string) |

Every row satisfies: decoded length equals the declared size **and** the packed
stream's own end marker falls at that same length. Each digest is asserted in
full by `tests/integration/test_logx_codec_rom.py` and emitted in full by
`--fixtures --json`.

### 13.1 Byte-level structure of two representative containers

Recorded because the packed grammar's field order is otherwise hard to review:

```text
0x0817C144  header 01000000 00080000   -> kind 1, declared 0x800
            payload words 2000114f a0580b88 a6bd5046 a48d511a
            first payload byte bits 0010 0000 = prefix 0 0 1 (four-bit form),
                          code 0000 (escape), field 00 (7-bit literals + base),
                          base 0000 0000
            first tokens  escape (bits 0..16), four-bit code 1 writes the base
                          (17..24), previous-distance copy gamma count=15
                          (24..34), literal 0x01 (34..42), long match d=2,
                          raw count 7 with the distance<=0x7F bias +4 -> 11 bytes
                          (42..58)

0x082B5F94  header 00000000 04000000   -> kind 0, declared 4 (the zero-header form)
            payload bytes  the four stored bytes
```

**PROJECT OBSERVATION (methodology).** During this ticket, two independent
transcription attempts of the same grammar each produced a *plausible-looking*
decoder that agreed on small fixtures and failed on larger ones. The failure mode
was identical both times: the third prefix bit was tested against the wrong
polarity, so the stream took the four-bit-code branch where it should have taken
the seven-bit/control branch. That only desynchronises once a token with
non-degenerate operands appears.

A third, distinct failure mode followed. An independent reviewer found that the
*prose* still had the inversion after the code was already correct, in this
document's earlier revision, in the ticket README, and in
`docs/reverse-engineering.md`. A correct implementation documented with inverted
prose passes every test and misleads every later reader, and it is invisible to
any check that only exercises the code.

Both lessons are recorded in `docs/research-conventions.md`: a bit-grammar
transcription must be validated on a **population** of real fixtures, not on one
or two; and a document that states a bit layout must be re-derived from the raw
bytes rather than transcribed from the implementation's control flow.

---

## 14. DECODER DIFFERENTIAL VALIDATION

Two implementations were run over the same corpus:

1. the project decoder, `tools.webfoot.formats.webfoot_lz.unpack`;
2. `tools.research.webfoot_codec_reference.decode_packed`, a second
   implementation written for this ticket.

| Comparison | Population | Result |
| --- | ---: | --- |
| decoded length equal | 4,322 packed containers | **4,322** |
| decoded digest equal | 4,322 packed containers | **4,322** |
| decode success on both | 4,322 packed containers | **4,322** |
| decoded length equals declared | 4,322 packed containers | **4,322** |
| end marker at the decoded length | 4,322 packed containers | **4,322** |

**What this proves, and what it does not.** The second module does not import
or call `webfoot_lz`, its only imports are `struct` and `dataclasses`, so the
two decoders are not literally one implementation run twice, and the differential
does prove that the two agree on every reachable container and that they differ in
their *policy* on malformed input (section 15).

It does **not** prove that the grammar is correct. The second implementation was
written after the project decoder was read, and the two share most of their token
grammar line for line. An independent review measured **65 of 83** normalised
grammar lines as verbatim identical, including the whole token dispatch table and
the bias ladder.
A shared misreading would therefore not be caught by this differential.

**PROJECT CONCLUSION.** The grammar's authority rests on the corpus, not on the
agreement: 4,322 real containers decode to exactly their declared sizes, reach
their own end markers at that same length, and, for the dominant chunk class -
produce the accepted tile-index coverage invariant established independently by
LOGX-TILE-001. The differential is a consistency and policy check on top of that,
and is described here as no more than that.

No external implementation was copied. `mainant/LOGExtractor` was read only as a
source of claims to test; it is not a dependency and no code from it is present.

---

## 15. MALFORMED AND TRUNCATED INPUT

Synthetic data only; the canonical image is never mutated. The engine has **no**
validation at all, so every refusal below is host-side policy.

| Case | Engine's instructions would | Project decoder | Research reference |
| --- | --- | --- | --- |
| truncated header (< 8 bytes) | read the following bytes as the header words | refuse | no packed arm to run |
| dispatch word 3 | return, destination untouched | refuse | no packed arm to run |
| packed, payload truncated | read past the container | refuse | refuse |
| packed, declared size 0 | never read `+0x04`; run the decoder | accept, 0 bytes | accept, 0 bytes |
| stored, declared size past the image | memcpy `0x7FFFFFFF` bytes | refuse (host limit) | no stored arm to run |
| stored, declared size 0 | copy zero bytes | accept, 0 bytes | no stored arm to run |
| packed, no end marker, size reached | keep decoding; no size comparison exists | accept | accept |
| packed back-reference before the output start | copy from bytes before the buffer | refuse | refuse |

**The second module decodes the packed arm only.** For the stored arm and for
unknown dispatch words its column says so and the engine's own branch is reported
beside it; it does not answer for a branch it does not implement. Reproduce the
whole table with `python -m tools.research.logx_codec_probe <rom> --malformed`.

**PROJECT CONCLUSION.** The engine performs no bounds check, no kind validation
beyond the `{0,1,2}` comparison, and no declared-size comparison. Every
project-side refusal is **PROJECT DECODER SAFETY POLICY**, deliberately stricter
than the engine. None of these behaviours is evidence that the engine validates
anything, and none is promoted as such.

**A gap this ticket records rather than fixes, and it is not visible in the table
above because it is not malformed.** The project decoder does not enforce "the
packed stream produces exactly the declared size": an over-long final match is
silently **clipped** to the declared length and reported as success. The
synthetic container `01000000040000000558d020000000c0` (kind 1, declared 4)
decodes to 15 bytes' worth of stream; `wl.unpack` accepts it and returns 4 bytes
`41 41 41 41`, while `reference.decode_packed` refuses it. That is the
partial-payload failure mode `_unpack_stream`'s own docstring says it exists to
prevent.

**PROJECT CONCLUSION (scoped).** This is **host-side behaviour** and not an
engine-contract violation, the engine has no length comparison either, but it
means a caller can receive a truncated payload with no error. It never arises on
the canonical corpus, where the two implementations agree on all 4,322 packed
containers, so no decoding claim in this document depends on it. It is pinned by
`test_project_decoder_clips_an_over_long_final_match` and the failure-policy fix
belongs to a follow-up implementation ticket.

**A distinctive consequence, stated because it affects authoring.** The engine's
packed decoder has no output counter. A future encoder must therefore place the
stream's own end marker such that decoding terminates where the declared size
says, or the engine will keep consuming whatever the packed decoder can still
interpret. On the canonical corpus this is automatic, the marker and the
declared size coincide on 4,322 of 4,322 containers, but it is a property of
these streams, not a guarantee the format makes.

---

## 16. DESTINATION SAFETY

**The engine's packed decoder receives no destination capacity.**
`0x0803D940` takes `(source, destination)` and passes no length to the packed
decoder veneer; the decoder stores with `strb` and increments, with no
comparison against a bound. **CONFIRMED** (instruction access).

What makes this safe in the canonical image is that the caller's buffer is sized
from the same constant the container declares: the dominant-layer constructor
uses a fixed `0x800` destination stride (`0x08007BFE` `lsls r1, r5, #0xB`) and
every dominant target declares exactly `0x800`; the selector-bank path uses a
fixed `0x4000` work buffer and every bank but one declares exactly `0x4000` (the
exception declares `0x3C40`, leaving stale tail bytes that no selector
addresses). **CONFIRMED** from prior tickets' accepted observations, re-measured
here.

**PROJECT RECOMMENDATION (not implemented here).** Host-side tooling must keep
its own `declared_size` bound; it must not be relaxed to "trust the stream".
A profile in which a container declared more than its caller's buffer would be a
real overflow in the engine, and no such container was observed.

---

## 17. SOURCE CONSUMPTION AND ENCODE-READINESS

Measured over the 4,322 reachable packed containers:

| Quantity | Value |
| --- | ---: |
| Source bytes consumed, minimum | 12 |
| Source bytes consumed, maximum | 8,708 |
| Source bytes consumed, total | 1,750,808 |
| Declared decoded bytes, total | 10,995,858 |

Consumption is counted at the engine's own access granularity: `ldr r6,[r1],#4`
advances the source pointer by whole words, so the consumed length is always a
multiple of four and the engine over-reads up to three bytes past the final
token. **CONFIRMED** for the granularity; the per-container figures are
**PROJECT OBSERVATION**.

**No encoded length is stored anywhere.** The wrapper holds only the decoded
size. Determining where a packed stream ends requires parsing it. **CONFIRMED.**

**PROJECT CONCLUSION.** A container's allocation can be bounded deterministically
by decoding it and recording the source position at which the end marker fires -
which is what `Decoded.source_consumed` reports, but it cannot be read off a
field.

---

## 18. EXISTING PROJECT DECODER STATUS

**Classification: `CORRECT WITH LIMITED FIXES REQUIRED`, and no shipping
behaviour was changed by this ticket.**

What is **CONFIRMED** about `tools/webfoot/formats/webfoot_lz.py`:

- the wrapper field layout it reads (`kind`, `declared_size`) is the engine's;
- its stored-branch semantics match the engine's `memcpy`;
- its dispatch value set matches the engine's `{0, 1, 2}`;
- its packed grammar is byte-exact against an independent reimplementation on
  all 4,322 reachable canonical packed containers;
- its decoded lengths equal the declared sizes on all 4,322;
- its `packed_end` (source consumed) is measured, never read from a field, and
  is the field future allocation work needs.

What this ticket **adds** (research-only, no production change):

- **The module does not enforce "the packed stream produces exactly the declared
  size".** Its `copy_match` stops writing once `len(out) >= expected`, so an
  over-long final match is silently **clipped** to the declared length and the
  decode is reported as successful. Repro: the synthetic container
  `01000000040000000558d020000000c0` (kind 1, declared 4) is **accepted** by
  `wl.unpack`, which returns 4 bytes `41 41 41 41`; the independent
  `reference.decode_packed` **refuses** the same input with "packed stream
  decoded 15 bytes against a declared 4". This is the partial-payload failure
  mode `_unpack_stream`'s own docstring says it exists to prevent, and the module
  does not currently prevent it. It is **host-side behaviour only**, the engine
  has no length comparison either, so it is not an engine-contract violation,
  but a caller can receive a truncated payload with no error. Fixing it is a
  follow-up implementation ticket; this ticket records and pins it
  (`test_project_decoder_clips_an_over_long_final_match`).
- the module's `DEFAULT_MAX_OUTPUT = 64 * 1024` is a host safety limit with no
  engine counterpart, and must not be cited as a format maximum.

Because the clipping case never arises on the canonical corpus, where the
reference and the project decoder agree on all 4,322 packed containers, it does
not weaken any decoding claim in this document. It is a robustness gap, not a
decoding error.

No correctness bug was found that blocks research, so no shipping change was
made. Any change to the module's failure policy belongs to a follow-up
implementation ticket.

---

## 19. ENCODER-READINESS

**ENCODER FORMAT SUFFICIENTLY UNDERSTOOD: PARTIAL.**

A future encoder must guarantee, at minimum:

| Requirement | Value / rule | Basis |
| --- | --- | --- |
| wrapper form | `u32 kind`, `u32 declared_size`, then payload at `+0x08` | CONFIRMED |
| kind to emit | `1` (the only kind the canonical packed corpus uses) | CONFIRMED |
| declared-size field | the **decoded** byte count, excluding the 8-byte header | CONFIRMED |
| raw fallback | `kind 0` + the byte count; supported by the engine and by the module | CONFIRMED |
| stream termination | emit the stream's own control escape such that decoding stops at the declared size | CONFIRMED for the corpus; the encoder must self-verify, because the engine has no size check |
| alignment | source reads are whole 32-bit little-endian words; pad the final word | CONFIRMED |
| destination safety | the encoder must not rely on the engine to bound output | CONFIRMED (no bound exists) |
| round-trip | decode the encoded stream and require exact equality with the input | project policy |

**What is NOT sufficient for an encoder.** The ticket does not establish the
*initial literal width* the engine supplies on the packed path (section 7.4).
The project's own encoder writes its own opening width escape, which makes the
question moot for any stream it emits, but an encoder that assumed it could rely
on the initial width would be relying on an unresolved fact.

**Do not ship an encoder from this ticket.** The format is understood well enough
to *decode with confidence* and to *state an encoder's obligations*; producing a
bit-exact reproduction of Webfoot's compressor is **not** in scope and is not
claimed. The existing `webfoot_lz.pack` is a valid-stream generator with a
measured size penalty; whether that is acceptable for insertion is an authoring
decision this ticket does not make.

---

## 20. TOOLING AND TESTS ADDED

| Artefact | Purpose |
| --- | --- |
| `tools/research/logx_codec_probe.py` | SHA-gated, read-only, deterministic census / fixture / zero-header / malformed / entry-point probe with `--report` and `--json` |
| `tools/research/webfoot_codec_reference.py` | Independent reimplementation of the packed grammar plus the engine wrapper report, for the differential |
| `tests/unit/test_logx_codec_reference.py` | Portable synthetic tests: wrapper layout, stored form, width/base escapes, long/short/four-bit tokens, end marker, malformed handling |
| `tests/integration/test_logx_codec_rom.py` | ROM-gated: fixture digests, full-census invariants, differential over the whole reachable corpus |

---

## 21. EVIDENCE CLASSIFICATION SUMMARY

| Claim | Status |
| --- | --- |
| outer wrapper exists | **CONFIRMED** |
| wrapper field layout (`+0x00` form, `+0x04` size, `+0x08` payload) | **CONFIRMED** |
| first word is a form selector over `{0, 1, 2}` | **CONFIRMED** |
| first word zero selects a raw copy of `container[+0x04]` bytes | **CONFIRMED** |
| first word zero means "empty" | **REFUTED** |
| raw/uncompressed form | **CONFIRMED** (2 canonical instances + the engine's default container) |
| compressed form | **CONFIRMED** (4,322 canonical instances) |
| decoded-size field at `+0x04`, `u32` LE, excluding the header | **CONFIRMED** |
| decoded size equals the produced output on every canonical container | **CONFIRMED** |
| payload starts at `+0x08` | **CONFIRMED** |
| codec identity as JCALG1 | **PARTIALLY CONFIRMED**, "JCALG1-like/derived, engine-consistent"; the name is not promoted |
| literal coding | **CONFIRMED** |
| backreference coding | **CONFIRMED** |
| long-match field order (distance before count) | **CONFIRMED** |
| end-marker behaviour | **CONFIRMED** for this corpus; marker-vs-size precedence **UNRESOLVED** |
| source consumption is whole-word granular | **CONFIRMED** |
| destination-bound behaviour (none in the engine) | **CONFIRMED** |
| headerless / `UnknownHeader` form as an engine container form | **REFUTED** |
| 64 KiB as an engine limit | **REFUTED** |
| canonical form inventory | **CONFIRMED** |
| existing project decoder correctness | **CONFIRMED** for the corpus; stricter-than-engine failure policy documented |
| future encoder-readiness | **PARTIAL** |
| `0x087B79A4` as the exact IWRAM blob base | **CONFIRMED** (startup DMA3 literals) |
| initial literal width supplied by the dispatcher | **UNRESOLVED** |
| which of declared size / end marker the hardware obeys first | **UNRESOLVED** |

Two statements are kept deliberately apart throughout:

- **"the project decoder safely rejects malformed input"**, true, and a
  host-side policy;
- **"the game engine rejects malformed input"**, **REFUTED**; it does not.

---

## 22. DISAGREEMENTS WITH LOGEXTRACTOR

| LOGExtractor statement | Disposition |
| --- | --- |
| older path: leading zero word means empty data | **REFUTED as a general rule**; it is the stored branch with a zero length |
| later paths: leading zero word means the declared bytes are stored raw | **CONFIRMED**, with the correction that the length is `container[+0x04]` |
| `UnknownHeader`: skip four bytes and decode headerless to an end marker | **REFUTED as a container form**; four-byte prefixes belong to records, not to the codec |
| a ~64 KiB temporary buffer | **REFUTED as a format maximum**; host convenience |
| the codec is JCALG1 | **PARTIALLY CONFIRMED** as JCALG1-like/derived; not asserted as byte-compatible |
| `0x179764` is global graphics/tile-source data | already corrected by LOGX-TILE-001; re-confirmed here as the `root + 0x4C` bank table |

---

## 23. UNRESOLVED QUESTIONS

1. **RESOLVED after independent review:** the IWRAM base is **CONFIRMED** via the
   startup DMA3 literals; the packed decoder is ROM `0x087B79E4` = IWRAM
   `0x03000040`.
2. The initial literal width the dispatcher supplies on the packed path. Engine
   evidence narrows it to "the dispatch word itself" (the dispatcher leaves it in
   `r3` and the decoder's prologue does not overwrite it before first use), so
   1 or 2; it remains immaterial because every canonical stream opens with the
   escape that sets it.
3. Which termination rule the hardware obeys when a stream's end marker and the
   declared size disagree. No canonical container exercises the case.
   **RESOLVED as moot (CQA-02-PACKED-STREAM-TERMINATION-001, 2026-09-23):** the
   engine has no declared-size comparison to obey, so precedence never arises -
   see [`CQA_02_PACKED_TERMINATION_RESOLUTION.md`](CQA_02_PACKED_TERMINATION_RESOLUTION.md)
   §3.6.
4. Whether the engine's codec is byte-compatible with any specific JCALG1
   reference implementation.
5. Which selector reaches the 3,819 non-root dominant element targets
   (inherited from LOGX-LAYER-001, not addressed here).
6. Whether any container form exists outside the three reachable resource
   graphs. This ticket does not scan the image and does not claim none does.
7. What `r2` indexes in the `0x0803D966` alternate path: the two routines read it
   as a byte lookup table, but which table a given caller passes is not
   established here.
8. The semantics of the structure at `0x087B7960` (`"EEProm_V124\0"`); it is not
   a source/destination pairing table and is not used by this ticket.

---

## 24. ADDENDUM, HOW THE FIELD ORDER WAS ACTUALLY ESTABLISHED

The ticket originally intended to recover the packed grammar by reading the
IWRAM blob's instructions and then simulate them. That plan was abandoned, and
the reason is a finding worth recording.

The blob's packed decoder is present and readable: `0x087B79A4` is a blob base,
`0x087B79E4` is its only ARM `push {..., lr}` prologue, and the region's internal
`BL` offsets are self-consistent. Its literal pool supplies two of the
length-bias thresholds (`0x087B7CCC = 0x37FF`, `0x087B7CD0 = 0x027F`), which match
the grammar exactly.

What did **not** work was recovering the token field order by eye. Two successive
readings of the same instructions each produced a decoder that agreed with the
project decoder on small fixtures and diverged on larger ones, and the divergence
always appeared only once a particular token first carried non-degenerate
operands. The misleading case was the third prefix bit: reading the four-bit
field before testing it against the prefix takes the wrong branch on the
canonical opening token, and the resulting stream stays plausible for a while
before any back-reference goes out of range.

What settled it was a **population** differential: 4,322 canonical containers,
byte-exact, between the project decoder and an independently written
reimplementation. Every field-order claim in section 8 rests on that, not on a
reading of the instructions.

Consequently this ticket claims:

- the **wrapper** is transcribed from engine instructions and is **CONFIRMED**
  (sections 4 and 5);
- the **packed grammar** is **CONFIRMED** as the grammar the canonical corpus
  uses, established by the whole-corpus differential (section 14);
- the **instruction-to-token mapping** for the packed decoder is
  **PARTIALLY CONFIRMED**: the MSB-first word framing, the two literal-pool
  thresholds and the four-branch prefix tree are all readable in the blob and
  agree with the grammar, but a complete instruction-level transcription is not
  asserted.

This is the conservative reading and is the one downstream work should rely on.
