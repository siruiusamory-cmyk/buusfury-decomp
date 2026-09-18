# LOGX-GFXSCAN-001: ImageScan-style graphics discovery, measured against verified engine graphs

Evidence document for the canonical Buu's Fury USA Rev. 0 image, SHA-256
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

Every claim is labelled with one status from
[`../research-conventions.md`](../research-conventions.md):

- **CONFIRMED** - directly supported by cited implementation, cited ROM bytes, or
  a reproducible observation scoped to this profile;
- **PARTIALLY CONFIRMED** - the physical fact is established but the semantic
  reading is not;
- **INFERRED** - best explanation supported by evidence, not directly proven;
- **UNKNOWN** - evidence absent, contradictory or insufficient.

Three provenance labels are used and never mixed:

- **EXTERNAL CLAIM** - a statement taken from `mainant/LOGExtractor`;
- **PROJECT OBSERVATION** - a reproducible measurement on the canonical image or a
  reading of the canonical image's own instructions;
- **PROJECT CONCLUSION** - this ticket's reasoned verdict on an observation.

Terminology is fixed here. A **container** is the eight-byte wrapper plus the
bytes that follow it. The **wrapper** is the engine function that reads that
header and selects a payload form (LOGX-CODEC-001). A **candidate** is one
wrapper position a scanner model accepted. A **known positive** is a container an
accepted resource graph reaches. **Graphics** is never used as a synonym for
"decoded".

---

## 1. Scope and input

Research only. No GUI, Workbench, renderer, atlas, authoring or shipping-SDK
change; no derived ROM; no emulator; no mutation of the canonical image. The
image was opened read-only and its SHA-256 re-verified before and after every
measurement pass (`tests/integration/test_logx_gfxscan_rom.py` asserts the object
the probes were given is unchanged).

Addresses are GBA addresses; a file offset is an address minus `0x08000000`.

---

## 2. Accepted dependencies used as given

| Fact | Source |
| --- | --- |
| Wrapper dispatcher `0x0803D940`; forms `{0, 1, 2}`; `+0x04` declared decoded size; payload at `+0x08` | LOGX-CODEC-001 |
| Packed codec: JCALG1-like / derived; end marker agrees with the declared size on 4,322 of 4,322 canonical packed containers | LOGX-CODEC-001 |
| `UnknownHeader` as an engine container form | REFUTED by LOGX-CODEC-001 |
| 64 KiB as an engine/container limit | REFUTED by LOGX-CODEC-001 |
| Animation object: `u32 frame_count`, then `4 * frame_count` 4-byte cells at `+0x04` | LOGX-FRAME-001 |
| Frame record: 8-byte header (piece count + bounding box) then `piece_count` **12-byte** pieces | LOGX-FRAME-001 |
| Piece `+0x04` packed OBJ attributes; piece `+0x08` graphics-container word | LOGX-FRAME-001 |
| 10,980 frame records, 11,005 pieces; the piece's dimension bytes multiply to its container's declared decoded size on all 11,005 | LOGX-FRAME-001 |
| Dominant handler `0x08008087`; leaf array at `record + 0x18 + 4*i` bounded by `record[+0x14] * record[+0x15]`; every element a container | LOGX-TILE-001 |
| Selector-1 root route `MapEntry[+0x2C]` -> leading aligned word run -> `word[0]`; `root + 0x48` selector stream; `root + 0x4C` bank table at `0x08179764` | LOGX-MAP-RENDER-001 / LOGX-TILE-001 |
| The engine's own zero-header default container at `0x08070808` | LOGX-CODEC-001 |
| Project container decoder `tools/webfoot/formats/webfoot_lz.py` | TOOLKIT-010 |

This ticket re-derives none of those routes. It re-runs them through
`tools/research/logx_gfxscan_probe.py`.

---

## 3. THE EXTERNAL SCANNER, TRANSCRIBED

### 3.1 Source and revision

**EXTERNAL CLAIM / PROJECT OBSERVATION (source identity).** The external tooling
inspected is `mainant/LOGExtractor`, repository
`https://github.com/mainant/LOGExtractor`, at commit
**`3a78bb35ad181082fbc9da01057538e5a78e8c2d`** ("Adding remaining tools",
2024-05-21T22:21:29Z). That commit is the **only** commit that ever touched either
file this ticket transcribes; `git` history over
`ImageScan/Gba/JCALG1.cs` and `ImageScan/MainForm.cs` returns exactly that one
entry each, so there is no earlier revision to compare against.

Files read, with the SHA-256 of the bytes fetched at that commit:

| Path | SHA-256 |
| --- | --- |
| `ImageScan/MainForm.cs` | `f9fdd5a15f30b47b2a845f68f87c104b68d1f978bc0b5f68414e48d2fc9f5acf` |
| `ImageScan/Gba/JCALG1.cs` | `b0d54b0188c6b8b53e9847af7d0f94581bf9606e4ad51165baa32c9449fb13a4` |
| `ImageScan/Gba/ROM.cs` | fetched whole; supplies `ReadInt` (little-endian `u32`) and `PushPosition`/`PopPosition` |

`CharacterSpriteExtractor/Gba/JCALG1.cs` is **byte-identical** to the ImageScan
copy (same SHA-256 above). `MapViewer/Gba/JCALG1.cs` differs only in that it
drops an unused `using` and drops the `Array.Resize`; its decode loop is the same.
The LOGExtractor GUI copy was also fetched; and
`CharacterSpriteExtractor/Program.cs` was read for its resource routes.

No LOGExtractor code is present in this repository and none was copied. It is not
a dependency.

### 3.2 What `ScanForImages` does, exactly

`ImageScan/MainForm.cs`, `ScanForImages`. Verbatim structure:

```csharp
for (int i = 0x200; i < rom.Length - 3; i += 1)
{
    rom.Seek(i);
    int magic = rom.ReadInt();
    if (magic != 0x1) continue;
    int length = rom.ReadInt();
    if (length > 0 && length < 0x20000 && length % 4 == 0)
    {
        try
        {
            byte[] decompressed = JCALG1.Decompress(rom, i);
            if (decompressed.Length > 0)
            {
                bool isPrio = decompressed.Length == 16 * 16;
                scanResults.Add(new ScanResult(i, isPrio ? 1 : 9));
                cache.TryAdd(i, decompressed);
                if (isPrio) prioResults++;
            }
        }
        catch { }
    }
}
```

Documented properties, each of which this ticket reproduces as an explicit
quantity:

| Property | Value |
| --- | --- |
| addresses tested | **every byte offset** from `0x200` to `rom.Length - 4`, increment 1 |
| alignment assumption | **none**: the loop body runs at odd offsets too |
| signature rule | first word must be **exactly 1**; a stored-form (`0`) or form-2 container is never even submitted |
| size filter | `1 <= declared < 0x20000` **and** `declared % 4 == 0`, where `declared` is the second word |
| decompression | `JCALG1.Decompress` (§3.3) |
| output-size filter | none after decoding. `isPrio = (decompressed.Length == 16*16)` only assigns a **sort priority** (1 or 9) and a counter; it never rejects |
| graphics dimension assumptions | none during the scan. Dimensions are chosen by the *user* in the GUI (`uxTileSize`, `uxImageWidth`) at draw time |
| palette assumptions | none during the scan. The GUI paints with a 256-entry `.act` file, chosen by a checkbox |
| duplicate suppression | **none**. The result list is sorted by `(priority, address)` and kept whole |
| rejection rules | the three above plus "the decompressor threw" and "the decompressor returned an empty array" |
| headerless / "UnknownHeader" path | present in `JCALG1.cs` (`DecompressUnknownHeader`) but **never called from `ScanForImages`** |
| heuristic based on visually plausible output | **none in the scan**. `CreateBitmap` decodes tiles for display only, and the scan never calls it |
| reporting | `scanResults.Count` and `prioResults` in the status bar, and a 1-based spinner to pick a result |

**PROJECT CONCLUSION.** The scanner is a *decoder filter over every byte offset*,
not a graphics detector. Its only notion of "looks like graphics" is the
post-decode priority value `decoded length == 256`, which reorders the list.

### 3.3 What `JCALG1.Decompress` does, exactly

`ImageScan/Gba/JCALG1.cs`, `Decompress`:

```csharp
int skip = rom.ReadInt();               // the dispatch word
int decompressedSize = rom.ReadInt();   // the declared decoded size
if (skip == 0)
{
    byte[] bytes = new byte[decompressedSize];
    for (int i = 0; i < bytes.Length; i++) bytes[i] = (byte)rom.ReadByte();
    return bytes;                       // the stored form: a byte-by-byte copy
}
var (data, size) = DecompressInternal(rom, decompressedSize);
Array.Resize(ref data, size);           // truncate to what was actually written
return data;
```

`DecompressInternal` allocates `new byte[decompressedSize]`, runs the token loop
from §3.4, and returns `(destination, w)` where `w` is the write cursor. The
caller `Array.Resize`s to `w`, so **the accepted payload can be shorter than the
declared size** and can never be longer.

The packed reader is `CompressionSource`:

```csharp
private void AdvanceBuffer()
{
    if (rom.Remaining >= 4) bitBuffer = (uint)rom.ReadInt();
    else bitBuffer = 0;
}
public int GetBit()
{
    if (bitsRemaining == 0) { bitsRemaining = 32; AdvanceBuffer(); }
    uint result = bitBuffer >> 31; bitBuffer <<= 1; bitsRemaining--;
    return (int)result;
}
public int GetInteger()
{
    int result = 1;
    do { result = (result << 1) + GetBit(); } while (GetBit() != 0);
    return result;
}
```

**PROJECT OBSERVATION (bit framing).** `rom.ReadInt()` is little-endian
(`Read() | Read() << 8 | Read() << 16 | Read() << 24`) and `GetBit` consumes from
bit 31 down, so the bit sequence is *little-endian words consumed MSB-first*. This
is the same framing as the project decoder, and it is the framing this ticket
reproduces. It is asserted directly by
`tests/unit/test_logx_gfxscan_probe.py::test_bits_of_is_msb_first_within_little_endian_words`
and cross-checked against the project reader.

**PROJECT OBSERVATION (`GetInteger`).** The external loop body reads a payload
bit and its continuation test reads a continuation bit with `!= 0`, i.e. it
continues while that bit is *set*:

```csharp
do { result = (result << 1) + GetBit(); } while (GetBit() != 0);
```

The reproduction exits when the same bit is *clear*. **These are the same loop
written from the other side** - `while (bit != 0)` and `if (bit == 0) return`
accept and reject exactly the same bit sequences - and the project decoder's
`gamma` is the same loop again. There is therefore **no** transcription
discrepancy in `GetInteger`.

**PROJECT CONCLUSION.** The claim an earlier revision of this document made -
that a literal reading of `GetInteger` fails on the canonical corpus - was
**wrong**: it described a *transposed* reading (exit when the continuation bit is
set) that no source contains. That transposed reading does fail, on all 11,712
kind-1 known containers; the source's reading succeeds on all 11,712. Corrected
here, and pinned by
`tests/unit/test_logx_gfxscan_probe.py::test_integer_reads_one_value_bit_per_continuation_bit`.

**PROJECT OBSERVATION (the initial literal state).** `CompressionState` has no
constructor, so `literalBits` and `literalOffset` both start at the C# field
default of **0**. They change only at a width/base escape
(`literalBits = 7 + GetBit(); literalOffset = 0; if (literalBits != 8)
literalOffset = GetBits(8);`).

**PROJECT CONCLUSION.** The `literalOffset` **is not** seeded from the
declared-size word, and the authority for that is the **source**, not the corpus.
An earlier revision argued from the corpus - that the sprite containers span every
word-aligned low byte, so a seed would shift their literals - but that argument is
**vacuous**: measured over all 11,712 kind-1 known containers and all 7,390
sprites, **zero** emit a literal before their first escape, so the initial value is
overwritten before it can be read. Seeding `literalOffset` with `declared & 0xFF`,
`(declared >> 8) & 0xFF`, `0x80` or `0xFF` leaves the known-corpus result
identical. The initial value is therefore **UNKNOWN from the corpus** and
**CONFIRMED from the source**; the tests record the premise (no literal precedes
the first escape) rather than pretending to discriminate.

**PROJECT OBSERVATION (the four-bit code's single arms).** The external source's
`0 0 1` branch is

```csharp
int value = source.GetBits(4) - 1;
if (value == 0)                       destination[w++] = 0;
else if (value > 0)                 { destination[w] = destination[w - value]; w++; }
else if (source.GetBit() != 0)      { /* a run of 256-byte raw blocks */ }
else { state.literalBits = 7 + source.GetBit();
       state.literalOffset = 0;
       if (state.literalBits != 8) state.literalOffset = source.GetBits(8); }
```

which differs from the project decoder in two places: the `value == 0` arm writes
a literal **0** rather than the literal base, and the escape **resets** the
literal offset where the project leaves its base alone. Both are reproduced as
written, and the first is **load-bearing**: it is the one arm where the two
grammars genuinely disagree, and §6.3 measures its cost.

**PROJECT OBSERVATION (the declared-size bound).** The token loop tests
`w < decompressedSize` at the top of every iteration, and every write arm is
entered from inside that loop, so no arm can be entered with `w` already at the
bound. `TransferMatch` therefore never indexes past the allocation.

**PROJECT CONCLUSION.** The external tool's `catch` never has to discard a
candidate because a match overran the declared size. Measured over all 13,463
submitted positions with a faithful write-counting transcription, **zero** accepted
decodes reach a write offset above their declared size. The reproduction still
reports an explicit `overrun` count (zero on this image) rather than assuming it.

### 3.4 The external token grammar, as reproduced

Shared prefix tree, read bit by bit (all four branches are reached in the
canonical corpus):

| Prefix | Branch |
| --- | --- |
| `1` | literal: `get(literalBits)`, added to the literal offset, truncated to a byte |
| `0 1` | long phrase: `gamma()` distance code; code `2` re-uses the previous distance with `gamma()` count; otherwise `distance = get(indexBase) + ((code - 3) << indexBase)`, then a `gamma()` count biased by the distance ladder `+3 / +2 / +1 / +4` at `0x10000 / 0x37FF / 0x027F / <= 0x7F` |
| `0 0 0` | seven-bit field, then a two-bit sub-field: non-zero field is a short match (`count = sub + 2`); field `0` with sub-field `0` is the **end marker**; field `0` with a non-zero sub-field re-tunes `indexBase = get(sub + 1)` |
| `0 0 1` | four-bit code: `1` writes the literal base, `2..15` copy one byte from distance `code - 1`, `0` is the width/base escape above |

**PROJECT OBSERVATION.** The four length-bias thresholds are the engine's own
constants, read out of the IWRAM blob's literal pool by LOGX-CODEC-001
(`0x087B7CCC = 0x37FF`, `0x087B7CD0 = 0x027F`), and the same ladder appears in the
project decoder. The external copy spells them as three `if` tests plus one
`else if (<= 127)`; they are the same four values.

### 3.5 Files fetched and their digests

The three files this ticket transcribes were fetched from
`raw.githubusercontent.com/mainant/LOGExtractor/3a78bb35ad181082fbc9da01057538e5a78e8c2d/`
and hashed locally:

| Path | SHA-256 |
| --- | --- |
| `ImageScan/Gba/JCALG1.cs` | `b0d54b0188c6b8b53e9847af7d0f94581bf9606e4ad51165baa32c9449fb13a4` |
| `CharacterSpriteExtractor/Gba/JCALG1.cs` | `b0d54b0188c6b8b53e9847af7d0f94581bf9606e4ad51165baa32c9449fb13a4` |
| `MapViewer/Gba/JCALG1.cs` | `a573d80e99d1aeb46e5337521f60b72f5a9312b5bbc221ae84c8fd34756e18e3` |
| `ImageScan/MainForm.cs` | `f9fdd5a15f30b47b2a845f68f87c104b68d1f978bc0b5f68414e48d2fc9f5acf` |

Only `JCALG1.cs`'s bytes are load-bearing for the decode model; `MainForm.cs`'s
scan loop is quoted whole in §3.2, so its behaviour is auditable from this
document even though the file itself is not vendored.

`DecompressUnknownHeader` reads:

```csharp
rom.PushPosition(address);
rom.Skip(0x4);
const int buf_size = 1024 * 64;
var (data, size) = DecompressInternal(rom, buf_size);
```

i.e. **skip four bytes, decode headerless with an 8-bit initial literal width and
a 64 KiB destination**. `ScanForImages` never calls it. It is measured separately
in §7.5.

---

## 4. THE PROJECT'S OWN GRAPHICS DISCOVERY PATHS

Inventoried before anything was added. This is a survey of existing code, not a
change to it.

| Path | File | Kind | Notes |
| --- | --- | --- | --- |
| Actor sprite decode (shipping) | `tools/webfoot/formats/sprite_graphics.py` | **structured graph walk** | 297-entry character pointer table -> animation -> frame -> piece -> container. Its frame/piece layout is the **superseded 16-byte** reading LOGX-FRAME-001 corrected to 12 bytes, and its `decode_animation` default `maximum_frames = 64` is the known-bad unbounded animation walk. Neither was repaired here. |
| Semantic sprite assets (shipping) | `tools/webfoot/graphics.py` | **structured graph walk** | stable identities, consumer lists, palette override store. Emits no images. |
| Graphics export (shipping) | `tools/webfoot/build.py` | **structured graph walk**, writes PNG | `graphic_%04d.png`; an authoring output, not a discovery path. |
| Sprite export (Workbench) | `tools/webfoot/workbench/graphics_tab.py` | GUI, writes PNG on demand | out of scope for this ticket. |
| Map rendering | `tools/webfoot/map_render.py`, `tools/webfoot/atlas.py` | structured walks over accepted map graphs | reuses LOGX-TILE-001's routes. |
| ROM atlas broad scan, compression pass | `tools/webfoot/atlas_producers/scan.py` `_compression_rows` | **heuristic**, stride **4** | `lz.looks_like_container` (`kind <= 2`, `1 <= declared <= 65536`) then `lz.unpack`. Its own docstring records **24,285** hits of which 68.7 MiB "decodes and round-trips" and calls the result "overwhelmingly probe noise". |
| ROM atlas broad scan, other passes | same file | heuristics: text runs, pointer tables, entropy, code shape | unrelated to graphics. |
| Atlas assembly | `tools/webfoot/atlas.py`, `atlas_build.py` | consumer of the above artifacts | proprietary-input tooling outside the SDK core. |
| Research probes | `tools/research/logx_*_probe.py` | **structured graph walks and censuses** | SHA-gated, read-only, digest-only output. |
| Instruction reading | `tools/research/thumb_disasm.py` | depends on **capstone** (imported lazily) | the only optional-package dependency in `tools/`. |
| `graphics_extents` producer | `tools/webfoot/atlas_producers/graphics_extents.py` | structured (pointer tables) | part of the atlas chain. |

**PROJECT CONCLUSION.** The project already had exactly one broad heuristic sweep
(the atlas compression pass at stride 4) and it is explicitly documented as noise
in its own source. Every path that produces a *named asset* is a structured graph
walk. Nothing in this ticket changes any of them.

---

## 5. KNOWN-POSITIVE CORPUS

Built from the accepted graphs only. No sweep contributes to it: a container is
known because a named graph reaches it.

| Class | Source graph | References | Unique containers | Unique payload digests | Wrapper kinds | Declared size | Slot semantics | Graphics identity |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |
| `sprite_piece_graphics` | LOGX-FRAME-001 piece `+0x08` | 11,005 | **7,390** | 7,390 | form 1 x7390 | 64 .. 4,096 | CONFIRMED: packed GBA OBJ tile data; the piece's dimension bytes multiply to the declared size on all 11,005 pieces | **CONFIRMED graphics** |
| `map_dominant_layer_chunks` | LOGX-TILE-001 dominant handler `+0x18` array | 3,912 | **3,745** | 3,745 | form 1 x3745 | exactly 2,048 | CONFIRMED: an array of `u16` tile indices feeding the accepted selector recurrence | **REFUTED as graphics** |
| `root_48_selector_streams` | LOGX-MAP-RENDER-001 `root + 0x48` | 421 | **392** | 392 | form 1 x390, form 0 x2 | 4 .. 1,784 | CONFIRMED: an array of `u16` selectors indexing the `root + 0x4C` bank | **REFUTED as graphics** |
| `root_4c_graphics_banks` | LOGX-TILE-001 `root + 0x4C` bank table | 187 | **187** | 187 | form 1 x187 | 15,424 .. 16,384 | UNRESOLVED | UNRESOLVED |
| `zero_header_form0_containers` | the form-0 members of the selector class | 2 | **2** | 2 | form 0 x2 | exactly 4 | CONFIRMED: form 0 is a raw copy of the declared bytes | UNRESOLVED |
| `engine_installed_default_container` | the dominant-layer constructor's default | 1 | **1** | 1 | form 0 x1 | 0 | CONFIRMED: form 0, declared size 0 | **REFUTED as graphics** |

**Headline arithmetic.** `11,715` unique containers =
`7,390 + 3,745 + 392 + 187 + 1`; `11,715` unique payload digests, i.e. **no two
known containers share a payload**, so the corpus's sharing is by *reference*
(11,005 piece references to 7,390 containers), not by duplicated bytes.

**The classes are not a partition, and the one overlap is named.**
`zero_header_form0_containers` is a **subset** of `root_48_selector_streams`: the
form-0 members are the same two addresses, `0x082B5F1C` and `0x082B5F94`. The
per-class sizes therefore sum to **11,717** while the corpus holds **11,715**
containers, and the reference totals sum to **15,528** against **15,526**
distinct-address references. An earlier revision printed the six-class sum as an
equation, which was wrong; the authoritative numbers are `len(resources)` and
`len(by_digest)`, and the probe now reports `class_size_sum`, `class_overlap` and
the overlap's addresses so the over-count is visible rather than hidden.

**PROJECT OBSERVATION (correction to a stale figure).** `sprite_graphics.py`'s
module docstring carries `7,355` distinct containers from an older 16-byte piece
walk. LOGX-FRAME-001's accepted 12-byte walk gives **7,390**. This ticket uses
7,390 and records the discrepancy for SYNTHESIS rather than editing the shipping
module.

**PROJECT CONCLUSION.** The only class whose *graphics* identity is established is
`sprite_piece_graphics`. It is therefore the **only** recall denominator. The map
chunk and selector classes are known engine-reachable **containers** whose
payloads are not pixels; a scanner that finds them has found real resources and
has not found graphics, and both statements are reported.

---

## 6. EXTERNAL-MODEL RESULTS

### 6.1 Scan population

| Quantity | Value |
| --- | ---: |
| byte positions the loop body executes at | **8,388,093** |
| positions whose first word is exactly `1` | **29,504** |
| ... of those, word-aligned | 27,775 |
| positions passing `1 <= declared < 0x20000` and `declared % 4 == 0` | **13,463** |
| positions rejected by the size filter | 16,041 |

### 6.2 Candidates

| Quantity | Value |
| --- | ---: |
| positions submitted to the decoder | 13,463 |
| decoder raised (swallowed by the tool's `catch`) | 175 |
| decoder returned an empty array | 298 |
| **raw candidates** (what `scanResults.Count` would show) | **12,990** |
| unique candidate addresses | 12,990 |
| unique decoded payload digests | 12,912 |
| candidates sharing a payload with another candidate | 78 |
| word-aligned candidates | 12,980 |
| unaligned candidates | 10 |
| decodes that hit the stream's own end marker before the declared size | 14 |
| candidates whose decoded length is exactly 256 (the tool's "priority" value) | 244 |
| stored-form candidates | 0 (the `kind == 1` test forbids them) |

**PROJECT OBSERVATION.** Every candidate is accepted by the same rule, and that
rule asserts almost nothing: the decoder is told how many bytes to produce, it
stops when it has produced them, and the only way to fail is for a token to index
before the start of its own output. The size it is told comes from the same
four-byte window that supplied the form word, so a run of bytes that happens to
contain a `1` and a plausible size word is admitted whether or not it is a
container. That is the mechanism behind the false-positive classes in §8.

### 6.3 Fidelity against the project decoder

**PROJECT OBSERVATION.** Run at the address of **every** known kind-1 container.
The corpus has 11,715 known containers, of which 3 are form 0, leaving **11,712**
kind-1 containers:

| Result | Count |
| --- | ---: |
| decodes, payload digest equals the project decoder's | **11,634** |
| decodes, payload digest **differs** | **78** |
| raises | **0** |

77 of the differing containers are `root_4c_graphics_banks` declaring exactly
`16,384` bytes; both models produce exactly 16,384 bytes and the bytes differ.
The 78th is `0x0829B308`, a `map_dominant_layer_chunks` container declaring
`2,048` bytes, and it is the one container the external `value == 0` arm moves
(§3.3): the external grammar writes a literal **0** there, the project grammar
writes its literal base.

**PROJECT CONCLUSION.** The external grammar and the project grammar agree
byte-for-byte on 99.33% of the reachable corpus. Where they differ, the cause is
the literal-base handling in §3.3, not the token dispatch: the escaped
`value == 0` arm and the escape's offset reset move a literal on some streams.
Both models reproduce the *container structure*; only the external one shifts a
few literals on streams that re-tune the literal width mid-stream. This matters
for digest-based coverage claims and not for address-based ones. It also means a
digest-based map-chunk claim is 3,744 rather than 3,745 - the one miss is this
container, and it is a decode difference, not a discovery miss.

### 6.4 Recall against the known corpus

| Class | Known unique | Found | Missed | Recall | Digests agreeing | Why the misses happen |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `sprite_piece_graphics` | 7,390 | **7,390** | 0 | **100.0%** | 7,390 | - |
| `map_dominant_layer_chunks` | 3,745 | **3,745** | 0 | **100.0%** | 3,744 | one container's bytes differ (§6.3) |
| `root_4c_graphics_banks` | 187 | **187** | 0 | **100.0%** | 110 | found by address; 77 decode differently (§6.3) |
| `root_48_selector_streams` | 392 | 191 | **201** | 48.7% | 191 | 199 rejected by `declared % 4 == 0`; 2 are form 0 |
| `zero_header_form0_containers` | 2 | 0 | 2 | 0.0% | 0 | `kind == 1` test excludes the stored form |
| `engine_installed_default_container` | 1 | 0 | 1 | 0.0% | 0 | `kind == 1` test, and declared size 0 fails `length > 0` |
| **all classes** | **11,715** | **11,513** | **202** | **98.3%** | 11,435 | - |

**PROJECT CONCLUSION.** Two structural blind spots, both of them the external
model's own filters rather than a decoding weakness:

1. **form 0 is invisible.** `magic != 0x1` excludes every stored container before
   the decoder is reached: 3 known containers plus every stored resource the
   accepted graphs do not enumerate.
2. **`declared % 4 == 0` rejects 199 real selector streams.** These containers
   declare `4k + 2` bytes because they hold `u16` selectors; the size filter has no
   engine basis. This is the single largest miss class.

Sprite recall is **total, digests included**: every one of the 7,390 engine-
referenced OBJ graphics containers is found at its own address and decoded to the
project decoder's exact bytes.

### 6.5 Candidate quality

| Category | Count |
| --- | ---: |
| **A** known engine-reachable graphics | **7,391** |
| **B** known engine-reachable non-graphics | 4,123 |
| **C** valid container, semantics unresolved | 7 |
| **D** engine-referenced, not previously catalogued | 1,453 |
| **E** structurally plausible, no engine reference found | 0 |
| **F** malformed / scanner false positive | 16 |
| total | 12,990 |

Match basis: 11,513 candidates are a known container at its own address; **1** is
a *new* address whose payload digest equals a known container's (a duplicate
parse); 1,476 match nothing known.

**PROJECT OBSERVATION (the A/B split is not scanner performance).** The 7,391
category-A candidates are 7,390 sprite containers plus one address whose payload
digest equals a sprite container's. The 4,123 category-B candidates are the map
chunks and selector streams the scanner reached. Those counts measure the
*corpus*, not the scanner: a scanner that finds every known container has an
A+B equal to the number of known containers it can see.

**PROJECT CONCLUSION.** Precision, stated honestly: of the 1,476 candidates at
addresses no accepted graph reaches, **1,453 are named by a word in the image**
and **7 are not**; the remaining **16** are the class-F candidates of §8, which
the counts here do not include. The 7 unreferenced ones are the only candidates
that are neither known nor referenced nor malformed, and they are all word-aligned,
exact and full-length. That is a far better precision figure than the 12,990 raw
candidate count suggests, and it is *not* evidence of graphics: an
engine-referenced word is a consumer, and this ticket establishes no graphics
semantics for any of them.

---

## 7. THE ENGINE-INFORMED MODEL

Three models are kept apart. `EXTERNAL` is the external tool.
`ENGINE_ALIGNED` adds the rules the engine's own dispatcher and the accepted
corpus imply. `ENGINE_UNCONSTRAINED` is the same with the alignment rule removed,
and exists only to measure how much of a scan's yield is an alignment artefact.

| | EXTERNAL | ENGINE_ALIGNED | ENGINE_UNCONSTRAINED |
| --- | ---: | ---: | ---: |
| form test | `kind == 1` | `kind in {0,1,2}` | `kind in {0,1,2}` |
| size filter | `1 <= declared < 0x20000`, `% 4 == 0` | `1 <= declared <= 65536` | same |
| alignment | none | **word-aligned starts only** | none |
| decode rule | external grammar, no exactness check | canonical grammar, exact decode, terminator at the declared size | same |
| positions submitted | 13,463 | 25,074 | 32,880 |
| decoded-error rejections | - | 791 | 1,376 |
| **candidates** | **12,990** | **24,283** | **31,504** |
| stored-form candidates | 0 | 11,097 | 18,309 |
| packed-form candidates | 12,990 | 13,186 | 13,195 |
| unaligned candidates | 10 | **0** | 7,221 |
| unique payload digests | 12,912 | 19,109 | 25,425 |
| known containers found | 11,513 | **11,714** | 11,714 |

### 7.1 What alignment is worth

**PROJECT OBSERVATION.** The **7,221** candidates the unconstrained model gains
over the aligned one are all at non-word-aligned offsets, and the aligned model's
candidate set is a subset of the unconstrained one. **PROJECT CONCLUSION.**
Requiring word alignment removes 7,221 candidates at zero recall cost: the aligned
model still finds **11,714 of the 11,715** known containers (the exception is the
form-0, zero-length engine default, which no model submits). Alignment is
therefore the cheapest single precision improvement available and it is
independently justified - every canonical container start is word-aligned.

### 7.2 What the exact-decode rule is worth

**PROJECT OBSERVATION.** Of 25,074 submitted positions, 791 decode with the
canonical grammar but **do not reach the declared size**, and are rejected.
**PROJECT CONCLUSION.** The exact-decode rule removes candidates whose stream ends
before its own header says it should. On the canonical corpus the packed streams'
end markers and declared sizes coincide on 4,322 of 4,322 containers
(LOGX-CODEC-001), so requiring agreement costs no known container and rejects 791
positions that are not containers.

### 7.3 What the engine model does *not* fix

**PROJECT OBSERVATION.** The engine model accepts **11,097** stored-form
candidates. A form-0 container is a byte-for-byte copy of `declared` bytes, so
*any* four-byte window reading as `0` followed by a plausible size is accepted,
and the "decoded" bytes are the image's own bytes read straight back. Of those
11,097:

The decomposition below is by the **classifier's own decision order**, so each
stored candidate appears exactly once and the rows can be checked directly against
the category tally:

| Decision | Count |
| --- | ---: |
| known container at its own address | 2 |
| a **new** address whose payload digest equals a known container's | 1 |
| inside a **known container's** extent | 4 |
| flagged as starting inside **another candidate's** measured extent | 5,998 |
| neither, and referenced by a word in the image | 27 |
| neither, and no reference found | 5,065 |
| **total** | **11,097** |

Two rows need their own sentence, because an earlier revision of this document
got both wrong:

* the digest-match row is `0x08772F8C` (form 0, declaring 1,024 bytes), whose
  payload equals the sprite container `0x0857C2EC`.  It is **not** a corpus entry:
  only **two** stored candidates are known containers at their own address
  (`0x082B5F1C`, `0x082B5F94`), and the third form-0 corpus entry - the engine's
  zero-length default at `0x08070808` - is never submitted at all, because every
  model requires `declared >= 1`;
* the nested row is 5,998 **form-0** candidates.  The all-form nested population is
  7,084 (5,998 stored plus 1,086 packed), which is exactly why §8 reports the F
  class and the nested flag as separate quantities.

**Arithmetic check.** `2 + 1 + 4 + 5,998 + 27 + 5,065 = 11,097`; the 27 referenced
plus the 5,065 unreferenced are the candidates that are neither known nor nested,
and they are exactly the 27 category-D and 5,065 category-C stored candidates of
the residual set (§9).

**PROJECT CONCLUSION.** *Form 0 makes a scan accept essentially anything.* A
scanner cannot use "the wrapper says form 0" as evidence of a container, because
form 0 asserts nothing a byte sequence can contradict. Only an engine reference
distinguishes a stored container from read-back code. This is why
`residual_engine_referenced` is the number worth reading and `raw_candidates` is
not.

### 7.4 Engine-informed model: recall

`sprite_piece_graphics`: **7,390 / 7,390** found, every digest agreeing. The
engine-aligned model finds **11,714 of 11,715** known containers, the exception
being the zero-length engine default that every model's size floor excludes.

### 7.5 The `UnknownHeader` heuristic

**EXTERNAL CLAIM.** `JCALG1.DecompressUnknownHeader` skips four bytes and decodes
headerless into a 64 KiB buffer.

**PROJECT OBSERVATION.** `ScanForImages` never calls it. The routine does
`PushPosition(address); Skip(0x4);` and then constructs a fresh
`CompressionSource`, whose first `AdvanceBuffer` reads the word at the *new*
position. So the first stream byte it reads is **`container + 4`** - the
declared-size word itself - its destination is 64 KiB rather than the declared
size, and its literal state is left at the C# default of **zero**. Measured over
the first 2,048 known packed containers: it accepts (does not raise) on the
population it is tried against, and its output digest matches the canonical decoded
payload on a minority of them.

**PROJECT CONCLUSION.** `UnknownHeader` remains **REFUTED as an engine container
form** (LOGX-CODEC-001) and this ticket does not re-promote it. As an *external
heuristic* it is a decoder run over bytes that are not the stream the wrapper
names, so a candidate it produced would carry no container semantics at all. No
independently engine-referenced headerless stream was found, and none is claimed.

---

## 8. FALSE-POSITIVE CLASSES

Measured classes, each with its mechanism:

Three mechanisms are counted apart. Collapsing the first two was a defect of an
earlier revision of this document: the class named "inside a known container"
counted candidates whose owner was **not** a known container at all.

| Class | External | Engine-aligned | Engine-unconstrained | Mechanism |
| --- | ---: | ---: | ---: | --- |
| `end_marker_before_the_declared_size` | 14 | 0 | 0 | the stream's own terminator fires before the header's size; `Array.Resize` accepts the short payload, so the tool never notices |
| `wrapper_start_inside_a_known_container` | 0 | **4** | **267** | the "header" lies inside a **known engine-reachable container's** measured extent |
| `wrapper_start_inside_another_candidate` | **2** | **7,084** | **15,320** | the "header" lies inside **another candidate's** measured extent |
| `wrapper_start_not_word_aligned` | 0 | 0 | **74** | the candidate was classified on an unaligned start |
| `clipped_decode_against_declared_size` | 0 | 0 | 0 | not reachable: the loop cannot cross its own declared bound (§3.3) |
| **total F** | **16** | **7,088** | **15,661** | |

The two "inside" classes are **different defects**, and they are not the same
number as the nested flag: `flag_nested_candidates` records
`nested_inside_candidate` for **all** candidates inside another candidate's extent
- 4 external, 12,612 engine-aligned, 21,610 engine-unconstrained - while the F
class counts only those that reach classification without a known match, a
reference or an earlier class. For the external model, 4 candidates carry the flag
and 2 survive to the class. For the engine-aligned model the flag's members are
6,607 packed and 6,005 stored. Of the 6,005 **stored** ones, 6 have an owner that
is itself a known container and 5,999 do not; of the 12,612 in total, 5,526 have
such an owner.  No candidate that is *flagged* nested can also be *classified*
`wrapper_start_inside_a_known_container`, because `classify_candidates` tests
`container_containing` first: the flag records a geometric fact, and the class
records the reason the candidate was rejected.

**PROJECT OBSERVATION (a distinction the ticket required).** The external model's
`decode_raised` count - 175 - is **not** a false-positive class: those positions
never became candidates. Of the positions that *did*, 14 are accepted despite
having stopped early and 2 start inside another candidate. Everything else is a
real container.

**PROJECT OBSERVATION (`not_word_aligned`).** The 74 in the unconstrained column
are the candidates *classified* on that ground, which is **not** the 7,221
unaligned candidates the engine-aligned model does not form at all. Reporting the
second number under the first name was a defect of an earlier revision.

**PROJECT CONCLUSION.** The dominant defect is **not** "the decompressor accepts
garbage" - on this image it accepts 12,990 candidates of which 11,513 are a known
container at its own address. The dominant defect is the **absent acceptance
contract**: the model has no way to say what a container is, so an unanchored form
word plus an unanchored size word is enough, and the form-0 arm makes that true of
almost anything once it is admitted.

---

## 9. RESIDUAL SET

The engine-aligned model's candidates minus every accepted known container:

| Quantity | Value |
| --- | ---: |
| candidate universe | 24,283 |
| residual candidates | **5,479** |
| ... with a payload a known container also has | **0** |
| ... with a payload nothing else has | 5,479 |
| ... named by a word in the image | **414** |
| ... no reference found within the stated coverage | **5,065** |
| ... confirmed by the external model too (same address, same digest) | **381** |
| residual by form | form 0: 5,092; form 1: 387 |
| residual that are packed **and** engine-referenced | 387 |
| residual that are packed, whole-tile **and** engine-referenced | 381 |
| residual that are packed, whole-tile, engine-referenced **and** >= 8 KiB | 21 |

**Reference-search coverage, stated with the claim.** A complete sweep of every
word-aligned word position in the image (2,097,152 positions) for the two stored
pointer forms. **Not covered:** a consumer reached through computed arithmetic, a
folded base, an `LDM`/`STM` aggregate, or any access the sweep cannot see. The two
forms are reported apart because the bare file-offset form of a small offset is a
tiny integer that occurs throughout the image: of the 1,546 targets with a hit,
1,508 have a full-GBA-address hit and 38 have only a bare-offset hit.

### 9.1 What the residual is

**PROJECT OBSERVATION.** The 387 packed residual candidates are all form 1 and all
named by at least one word. Their declared sizes run **128 .. 65,474** bytes, and
the distribution is dominated by small streams, not by tile banks:

| Declared size | Count |
| --- | ---: |
| 256 | 129 |
| 1,024 | 88 |
| 4,096 | 97 |
| 2,048 | 24 |
| 8,192 | 16 |
| other | 33 |
| **= 8 KiB or larger** | **26** |

381 of the 387 have whole-tile decoded lengths; 381 of the 387 are byte-for-byte
confirmed by the external model; the conjunction *packed and whole-tile and at
least 8 KiB* is **21**. The largest referenced residual is `0x087A04F0`
(65,474 bytes) and it is **not** external-confirmed. An earlier revision of this
document described the population as "all 8 KiB or larger, largest 38,400, all
confirmed by the external model", which was wrong in every clause.

**PROJECT CONCLUSION (deliberately weak).** These are **engine-referenced
containers that no accepted resource graph enumerates**. Their shape is
*consistent with* tile data - packed and, for 381 of 387, whole-tile - and that is
**all this ticket claims**. It does not claim they are graphics, because no
rendering consumer was established for any of them, and it does not claim they are
new to the project, because LOGX-CODEC-001's reach census already recorded
containers outside the accepted root set. The follow-up that would settle them is
named in §12. Several of the largest are named by consecutive words in one table
around `0x087B5B64`, which is a lead, not a conclusion.

**PROJECT OBSERVATION.** The 5,065 unreferenced residual candidates are
overwhelmingly form 0: 5,065 of 5,065 read their payload back out of the image
itself, because a form-0 container is a byte-for-byte copy of `declared` bytes at
`+8`.

**PROJECT CONCLUSION.** The residual set is **not** 5,479 new resources. It is
414 referenced containers whose consumer is unidentified - 387 of them packed -
and 5,065 positions where a scan read a plausible header out of code or data.
Reporting the first as discovery and the second as resources would be exactly the
failure this ticket exists to measure.

### 9.2 Representative residual candidates

| Address | Form | Declared | Engine reference |
| --- | --- | ---: | --- |
| `0x08055620` | 1 | 38,400 | `0x08004EFC` |
| `0x0825FC08` | 1 | 15,872 | `0x082607FC` |
| `0x082ACA20` | 1 | 12,608 | `0x082AD8E8` |
| `0x08071758` | 1 | 10,240 | `0x08028118`, `0x0802837C`, `0x08071740` |
| `0x0818FEA0` | 1 | 8,192 | `0x081906BC` |
| `0x080154CC` | 0 | 4,108 | none found |

`0x08071758` is one of the two the engine's own default container
(`0x08070808`) neighbours: the region around `0x08070800` is reachable by a
constructor and holds a run of large packed containers no accepted graph
enumerates.

### 9.3 Arbitration rule used when the external source and the corpus disagree

Two disagreements arose in this ticket, and both were settled the same way:

1. `GetInteger`'s continuation test (§3.3);
2. the literal offset's initial value (§3.3).

**PROJECT CONCLUSION.** The rule applied is: **the model must reproduce the
project decoder's bytes on the canonical corpus**, because the project decoder is
independently validated (LOGX-CODEC-001: 4,322 of 4,322 containers, two
implementations, end markers at the declared sizes) and the external source is
not. Where a literal transcription of the external source fails that test, the
reproduction uses the reading that passes it and the discrepancy is documented
here rather than resolved silently. Both readings are stated so a reviewer can
re-derive the choice.

---

## 10. EVIDENCE CLASSIFICATION SUMMARY

| Claim | Status |
| --- | --- |
| `ScanForImages` scans every byte offset from `0x200`, increment 1 | **CONFIRMED** (source) |
| it requires the first word to be exactly `1` | **CONFIRMED** (source) |
| it requires `1 <= declared < 0x20000` and `declared % 4 == 0` | **CONFIRMED** (source) |
| it has no post-decode output-size filter; `== 256` only sets a sort priority | **CONFIRMED** (source) |
| it runs no visual plausibility test | **CONFIRMED** (source) |
| `DecompressUnknownHeader` exists and is never called by the scan | **CONFIRMED** (source) |
| external bit framing is little-endian words consumed MSB-first | **CONFIRMED** (source + bit-level cross-check) |
| external grammar reproduces the project decoder on the canonical corpus | **CONFIRMED** for 11,634 of 11,712 kind-1 known containers |
| the two grammars diverge on 78 containers | **CONFIRMED**, cause identified: the `value == 0` arm writes a literal 0 where the project writes its base, plus literal-base persistence on 77 large banks |
| the `GetInteger` continuation test differs between the two sources | **REFUTED**: `!= 0` continue and `== 0` exit are the same loop |
| the initial literal state distinguishes the models on the canonical corpus | **REFUTED / UNKNOWN from the corpus**: no known container emits a literal before its first escape, so the state is inert; the source sets it to 0 |
| an accepted decode can overrun its declared size | **REFUTED**: 0 of 12,990 accepted decodes reach a write offset above the declared size |
| wrapper detection validity as a *container* test | **PARTIALLY CONFIRMED**: the kind word and the size word are the engine's fields, but acceptance requires no agreement with anything |
| codec validation | **CONFIRMED** for the grammar; **REFUTED** as a container-identification rule |
| graphics classification heuristic in the external tool | **REFUTED**: the only post-decode test is `length == 256`, used for sorting |
| sprite-graphics recall (external model) | **CONFIRMED** 7,390 / 7,390, digests included |
| map-chunk recall (external model) | **CONFIRMED** 3,745 / 3,745 (not graphics) |
| selector-stream recall (external model) | **CONFIRMED** 191 / 392; 199 misses caused by `declared % 4` |
| stored-form (form 0) recall | **REFUTED** at 0: the `kind == 1` test excludes the form |
| packed-form recall | **CONFIRMED** 100% of every known packed container that passes the size filter |
| engine-aligned recall | **CONFIRMED** 11,714 / 11,715 known containers, 7,390 / 7,390 sprites |
| alignment as a precision rule | **CONFIRMED**: removes 7,221 candidates, no recall loss |
| `UnknownHeader` as an engine container form | **REFUTED** (LOGX-CODEC-001), not re-promoted |
| `UnknownHeader` as an external heuristic | **PARTIALLY CONFIRMED** that it decodes; **REFUTED** that its output carries container semantics |
| residual candidate identity | **UNRESOLVED** for 387 referenced packed candidates (26 of them >= 8 KiB); **REFUTED as resources** for the 5,065 unreferenced stored-form ones |
| residual graphics semantics | **UNKNOWN**: no rendering consumer established |
| residual reference status | **CONFIRMED** ENGINE-REFERENCED for 414; **CONFIRMED** NO REFERENCE FOUND for 5,065, within the documented coverage |
| shipping discovery scanner suitability | **REFUTED** (see §11) |
| forensic / research scanner suitability | **CONFIRMED**, with the caveats in §11 |
| canonical enumeration suitability | **REFUTED**: structured graph traversal must remain authoritative |

---

## 11. SUITABILITY AND DISAGREEMENTS

### 11.1 Verdicts

| Question | Verdict |
| --- | --- |
| **shipping discovery tool** | **NO** |
| **forensic / research tool** | **YES** |
| **canonical resource enumerator** | **NO** |

**PROJECT CONCLUSION.** *Useful forensic scanner with high recall and an
unacceptable candidate contract; structured graph traversal must remain
authoritative.*

- **Not a shipping discovery tool.** It reports 12,990 candidates for 11,715 known
  containers, and 5,065 residual candidates whose payloads are the image's own
  bytes read back through the stored form. A shipping tool cannot present that
  list as assets, and it cannot rank it: the tool's only ranking is
  `decoded length == 256`.
- **A useful forensic tool.** On this image the external model finds **100%** of
  the engine-referenced sprite graphics containers - 7,390 of 7,390, digest-exact
  - and 100% of the map chunks and banks. When the question is "has anything been
  missed", it is a strong recall instrument, and its 1,453 engine-referenced
  candidates at addresses no accepted graph reaches are a real lead list.
- **Not a canonical enumerator.** It has no acceptance contract. Its precision
  comes from the corpus, not from the method: it cannot distinguish a container
  from a byte sequence that looks like one, and the form-0 arm makes that
  indistinguishable in principle. Enumeration must go through the graphs.

### 11.2 Disagreements with LOGExtractor

| LOGExtractor statement / behaviour | Disposition |
| --- | --- |
| the scan tests every byte offset | **CONFIRMED**; reported as 8,388,093 tested positions with 27,775 of 29,504 kind-word matches aligned |
| a decoded, non-empty payload is a scan result | **CONFIRMED** as the tool's behaviour; **REFUTED** as a container test |
| `decoded length == 16 * 16` identifies graphics | **REFUTED**: it is a sort priority, and 244 of 12,990 candidates carry it |
| `UnknownHeader` decodes headerless streams | **PARTIALLY CONFIRMED** as a decoder; **REFUTED** as an engine container form (LOGX-CODEC-001) |
| a ~64 KiB temporary buffer | **REFUTED** as a format maximum (LOGX-CODEC-001); it is the host tool's buffer |
| the codec is JCALG1 | **PARTIALLY CONFIRMED** as JCALG1-like/derived; the name is not promoted (LOGX-CODEC-001) |
| `GetInteger` continues while its continuation bit is set, as written | **CONFIRMED as written, and reproduced as written.** The reproduction exits when the bit is clear, which is the same loop; the source's reading decodes all 11,712 kind-1 known containers and reproduces the project decoder on 11,634 of them |
| the declared-size word seeds the literal base | **REFUTED**, from the source: `CompressionState` leaves both fields at the C# default 0. The corpus cannot discriminate this - no known container emits a literal before its first escape - and an earlier revision wrongly claimed it could |
| the `value == 0` arm writes the literal base | **REFUTED**: the source writes a literal 0, and that is the arm that makes the two grammars disagree on 78 rather than 77 containers |
| `declared % 4 == 0` is a valid container test | **REFUTED**: 199 real selector streams declare `4k + 2` bytes |
| a form-0 header means "the declared bytes are stored raw" | **CONFIRMED** (LOGX-CODEC-001), with the correction that this makes form 0 non-discriminating as a discovery signal |

---

## 12. UNRESOLVED QUESTIONS

1. **Which consumer reads the 387 referenced residual containers?** The follow-up
   is to walk the named reference sites (`0x08004EFC`, `0x082607FC`, `0x082AD8E8`,
   `0x08028118`, `0x087B5B64`, ...) as instructions and identify the resource
   family. Several of the largest are named by consecutive words in one table
   around `0x087B5B64`, which makes that table the first thing to read. Until that
   is done they are neither new nor graphics.
2. **Do the residual containers overlap LOGX-CODEC-001's non-root reach?** That
   ticket recorded 3,819 dominant-handler element targets outside the selector-1
   root set. A set comparison was not performed here.
3. **Is the divergence in §6.3 one mechanism or two?** Two are identified - the
   external `value == 0` arm (one map chunk) and the escape's offset reset (77
   banks) - but the 77 were not individually traced token by token.
4. **What does the initial literal state change on the *scan population*?** It is
   inert on the known corpus (no literal precedes the first escape), but a reviewer
   measured that a scan-population re-run with the field at the kind word rather
   than 0 changes a small number of accepted positions. That population was not
   re-measured here; the reproduction follows the source and leaves it at 0.
5. **Portrait resources.** LOGX-CHAR-001's `+0x08` pointer array was not enumerated
   as a known-positive class here, so no portrait recall figure is claimed. The
   external `CharacterSpriteExtractor` decodes a portrait through the same
   `JCALG1.Decompress`, so a portrait population would be measurable with the same
   tool.
6. **The engine's own graphics-size constraints.** This ticket applied no
   tile-dimension constraint to the engine model beyond whole-tile divisibility in
   the report, because no independently justified set of allowed dimensions was
   available. A justified constraint set would tighten the residual further.

---

## 13. TOOLING AND TESTS ADDED

| Artefact | Purpose |
| --- | --- |
| `tools/research/logx_gfxscan_probe.py` | SHA-gated, read-only, deterministic reproduction of the external scanner plus two engine-informed models, the known-positive corpus, the reference search and the residual set, with `--external-model`, `--engine-model`, `--known`, `--classify`, `--diff`, `--residual`, `--references`, `--summary`, `--unknown-header` and `--json` |
| `tests/unit/test_logx_gfxscan_probe.py` | 39 portable synthetic tests: bit framing, the external acceptance filter, the external decoder's arms (including the literal-zero arm and the initial literal state), `GetInteger` bit order, candidate arithmetic, classification, the two false-positive mechanisms, nested flagging as a pre-pass, deduplication, reference search, the canonical gate, optional-dependency behaviour |
| `tests/integration/test_logx_gfxscan_rom.py` | 31 ROM-gated tests: corpus counts and the class overlap by address, the external model against real containers, the scan population, recall per class, the three false-positive splits, the engine models, residual invariants and the residual size distribution, word-alignment proofs, reference-search coverage, canonical-image integrity |

No decoded payload is written anywhere. The probe emits addresses, lengths and
SHA-256 digests only.

---

## 14. SYNTHESIS HANDOFF

1. **The external scanner is a recall instrument, not a detector.** Its value is
   that it finds 100% of the engine-referenced sprite graphics containers; its
   cost is 5,065 residual candidates whose payloads are read-back bytes.
2. **Form 0 is the precision cliff.** Any future scanner must require an engine
   reference or a structural agreement for the stored form, because a form-0
   header asserts nothing.
3. **`declared % 4 == 0` is wrong** and costs 199 real containers. It should never
   appear in project tooling.
4. **The 387 referenced residual candidates are the ticket's most useful output**
   and are the next concrete reverse-engineering target. They are not a homogeneous
   block: 129 declare 256 bytes, 97 declare 4,096, and only 26 reach 8 KiB. The
   table around `0x087B5B64` names several of the largest and is the first thing a
   follow-up should read.
5. **Two stale figures in shipping code** (7,355 vs 7,390 sprite containers; the
   16-byte piece walk) belong to SYNTHESIS, not here.
6. **LOGX-GFXSCAN-001 changes no canonical format.** `ROM_BIBLE_IMPACT` is
   **NONE** for formats; the residual candidate list is a lead list, not a format.
