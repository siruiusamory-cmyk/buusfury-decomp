# LOGX-TILE-001 review

Reconstruct Buu's Fury chunk / tile representation. Research only.

## Repository and safety

- **START SHA:** `22d60419d61132ecaa3128b28a2ef274d317be66`
- **END SHA:** the branch head of `logx-tile-001` after this commit
  (`git rev-parse logx-tile-001`); this document records the SHAs of the commits
  that precede it
- **BRANCH:** `logx-tile-001`
- **COMMIT SHA(S):** `research(map): reconstruct Buu chunk and tile format`
  (the research result) plus a review/correction commit recording the
  independent verdict and the correction gate
- **CANONICAL ROM SHA BEFORE:**
  `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`
- **CANONICAL ROM SHA AFTER:**
  `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`

The isolated worktree was created from the START SHA as a fresh branch. The
retained `logx-layer-001`, `logx-map-render-001` and `logx-map-record-001`
branches, the active WORKBENCH-006 worktree and stale local state were not used
and were not touched. The ROM was opened read-only; no save, state, derived ROM,
dump or extracted asset was created, and none is staged.

## External claims tested

Source: `mainant/LOGExtractor`, as summarised in the ticket. Every claim was
treated as a claim only:

1. background tiles are 8x8 pixels;
2. a chunk is 32x32 tiles = 256x256 pixels;
3. a chunk holds little-endian 16-bit entries;
4. bits 0-9 tile ID, bit 10 H flip, bit 11 V flip, bits 12-15 unused;
5. global graphics/tile-source data near file offset `0x179764`;
6. a referenced source image is 128x128 px = 16x16 tiles = 256 tiles;
7. `root+0x48` is decompressed as a u16 sequence;
8. the consumer accumulates `index += value; select(index); index++`.

## Dominant layer handler, array element references and targets

| Quantity | Value |
| --- | ---: |
| **Dominant layer handler** | `0x08008087` |
| Dominant handler references | **1516** |
| Dominant handler unique records | **1420** |
| **Array element references** (sum of `+0x14 * +0x15`) | **4274** |
| ... null | **156** |
| ... aligned in-ROM | **4118** |
| ... unaligned in-ROM | **0** |
| ... outside ROM | **0** |
| **Unique array targets** | **3745** |
| **Shared targets** (more than one reference) | **165** |
| Maximum references to one target | **10** |
| Target range | `0x08179A50`..`0x082B8BAC` |
| All targets 4-byte aligned | yes |

`4274 = 156 + 4118`; 4118 non-null references resolve to 3745 unique targets.
References, unique pointers and unique payloads are reported separately
throughout.

## Array element target structure

Every one of the 3745 unique targets is a **kind-1 Webfoot container declaring
exactly `0x800` bytes**, and all 3745 decode to exactly 2048 bytes. The
constructor loads the element with `ldr r0,[r0,#0x18]` at `0x08007BF2` and hands
that same value to `0x0803D940` in `r0` at `0x08007C04`: one dereference, no
intermediate header, no pointer-to-pointer hop. Every element is therefore
compressed, not raw tile data. **CONFIRMED.**

Anomalies: 117 of the 1420 unique dominant records (117 reference groups too)
carry a null inside the `x*y` window; on 85 of them a non-null follows a null.
Zero malformed pointers, zero size outliers, zero decode failures.

## Chunk dimensions, entry count, width and endianness

| Item | Result |
| --- | --- |
| **Chunk dimensions** | **32 columns x 32 rows** - CONFIRMED |
| **Chunk entry count** | **1024** - CONFIRMED |
| **Entry width** | **2 bytes** (`ldrh r1,[r3,r1]`, `0x08008074`) - CONFIRMED |
| **Entry endianness** | **little-endian** - CONFIRMED |
| Row stride | 64 bytes (`(row & 31) * 64`, `0x0800806A`) |
| Element stride | 2 bytes (`(col & 31) * 2`, `0x08008070`) |
| Decoded payload size | `0x800` = 2048 bytes = `32 * 32 * 2` |

The dimensions are hardcoded in two consumer constants, not stored in the chunk
and not derived from target spacing in ROM. **1024-entry interpretation:
CONFIRMED.** **32x32 interpretation: CONFIRMED** for the dominant class.
**8x8 tile interpretation: CONFIRMED**, independently of platform convention:
`asrs #3` on both axes at `0x0800805C`/`0x0800805E`, a 64-byte copy per
destination tile at `0x08009C6A`/`0x08009C78`, and a `>> 8` chunk index at
`0x08008022` (256 px per chunk).

## Bits 0-15

Union census over all 3745 unique decoded payloads: **3,834,880 entries**; 2,879
distinct raw values; raw range `0x0000`..`0x0F7B`; 2,727,181 zero entries; no
all-zero payload; every payload exactly 1024 entries.

| Bit | Entries set |
| --- | ---: |
| 0-9 | 581,251 / 507,444 / 518,253 / 513,338 / 513,485 / 472,053 / 451,130 / 377,289 / 177,836 / 81,271 |
| **10** | **46,034** |
| **11** | **15,668** (both 10 and 11 on 5,239) |
| **12** | **0** |
| **13** | **0** |
| **14** | **0** |
| **15** | **0** |

- **BITS 0-9: CONFIRMED** as an integer field, and **CONFIRMED** as the tile
  ordinal the engine's own loaders populate. 896 distinct values, maximum 895,
  covering `0..895`. Expanding every nonzero entry of every dominant payload a
  map references - a per-map, per-reference expansion of shared payloads -
  gives 1,241,888 entries; comparing bits 0-9 against the map's static selector
  ordinals and its animated-tile destination ranges leaves **0 exceptions**
  (1,218,581 static, 23,307 animated, on 178 maps). Aggregating over *unique*
  payloads instead gives a smaller and differently-scoped 1,107,699 nonzero
  entries, which is not the denominator this check uses. Bits 0-9 are also
  CONFIRMED as the hardware character name: the halfword reaches the BG
  screenblock unchanged, and the engine writes `BG0CNT..BG3CNT` from one of two
  records at `0x080716D8` selected by `root+0x3C` - index 0 on **451** roots
  (`0x1C80 0x1D80 0x1E80 0x1F80`) and index 1 on **map 19 only**
  (`0x1C80 0x1D80 0xBE80 0x1F80`). Both are 8bpp with character base 0 and
  screen bases 28..31; they differ only in map 19's BG2, whose `0xBE80` makes
  that single screenblock 512x256 instead of 256x256. The value actually stored
  is the table halfword **plus** a per-frame offset (`0x080093E2`/`0x080093E4`,
  `[r6,#0x34]`) whose source no recovered code writes. The blit destination
  `0x0600E000 + slot*0x800` matches the table record's screen base in both cases.
- **BITS 10 AND 11 (existence and independence): CONFIRMED.** **Direction
  assignment: PARTIALLY CONFIRMED.** See above.
- **BIT 10: CONFIRMED** to exist, to be used and to lie outside the tile-index
  field. **Horizontal-flip direction: PARTIALLY CONFIRMED** - the platform BG
  entry layout applied to a verbatim VRAM copy. **No site anywhere in the image
  isolates bit 10** (0 of the image's 1532 adjacent `lsls`/`lsrs`
  mask-or-field pairs).
- **BIT 11: CONFIRMED** likewise. **Vertical-flip direction: PARTIALLY
  CONFIRMED**, same basis. Four sites isolate bit 11, all inside the
  `0x0806E000..0x0806F000` table block, which no `BL`/`BLX` in the image reaches
  (0 targets from all 8,838 4-byte-aligned encodings) and which is not the
  map/layer code region.
- **BIT 12, 13, 14, 15: RESERVED / CONSTANT IN CANONICAL DATA; UNUSED BY ANY
  KNOWN CONSUMER; semantic role UNRESOLVED.** Zero on all 3,834,880 entries. No
  `0x0000F000` or `0x00000FFF` mask exists as an aligned word anywhere in the
  image; no site extracts a 4-bit field at shift 12 in code (the four `(12, 4)`
  sites are all at `0x0816A0E2` or above, inside data). They are **not**
  documented as "unused by the format": the engine's occupancy test at
  `0x08008076` treats any nonzero entry as occupied, so a nonzero high nibble
  would not be inert.

The absence evidence is a raw-halfword scan over the whole image, not a linear
disassembly sweep. It finds **1532** adjacent mask-or-field pairs - **46** below
`0x08007000`, **29** inside the map/layer code region `0x08007000..0x0800A000`,
**961** inside the first `0x70000` bytes and **571** at or above `0x08070000` -
and **none of the region's 29 pairs has a `right_shift` that reaches bit 9**, so
nothing in the code that owns a payload *selects* a field beginning at bit 9 or
above. (The region does contain two `(0, 16)` `& 0xFFFF` truncations at
`0x08009E32`/`0x08009FB6`, which read a whole halfword and select none of it.)
The low-ten-bit mask `(0, 10)` exists 51 times elsewhere in the image and never
in that region; the sampled uses are OAM attribute packing.

**The scope of this negative is deliberately narrow.** It is *not* "no engine
instruction anywhere reads those bits". Three idioms that could test a bit of
another value were not scanned, and each was measured so the gap is visible:
shift-immediately-followed-by-a-conditional-branch pairs (8,014 image-wide; 241 /
395 / 372 / 312 / 350 / 760 of them put bits 10-15 in the tested position; none
of the bit-10..14 ones is in the map/layer region, and most are result tests
rather than carry tests); `movs #imm ; lsls` mask builds with a bit at 10 or
above set (1,204 sites, 301 constants, the bits-10-11 constant `0x0C00` 34 times,
none in the map/layer region); and non-adjacent `lsls`/`lsrs` pairs, one of which
does sit in the map/layer region (`& 0x3FF` at `0x08008728`..`0x08008730`) but
operates on a shifted coordinate, not a payload word. Every sampled source of
every one of those idioms is an object field, never `object+0x10..object+0x1C`.

## Root `+0x48`

`root+0x48` is a **Webfoot container address** (`ldr r0,[r1,#0x48]` at
`0x08009BE6`). All **452** canonical roots decode it with **0 failures**: 450 are
kind 1 and 2 are kind 0, declared sizes 4..1784 bytes, all even.

**Decoded stream.** A `u16` array of `declared_size / 2` words (`asrs r7,r0,#1`
at `0x08009BF0`); 2..892 words; 283 distinct counts.

**Delta recurrence. CONFIRMED** from `0x08009C02`..`0x08009C12`, independently of
LOGExtractor and of the accepted `MAP_RENDER_FORMAT.md` statement of the same
rule:

```text
absolute[0] = raw[0]
absolute[i] = (raw[i] + absolute[i-1] + 1) & 0xFFFF      for i >= 1
```

**Selector semantics. CONFIRMED.** The decoded value is a packed pair, not a bare
tile index: `value >> 8` indexes the container array at `root+0x4C`
(`0x08009C54`/`0x08009C56`) and `value & 0xFF` selects a 64-byte tile inside that
bank's `0x4000`-byte decoded payload (`0x08009C6E`). One selector contributes one
8x8 tile to character memory at `0x06000000 + 64*ordinal`. Only the high byte
groups: a bank container is decoded once per contiguous run of equal
`value >> 8` (`0x08009C3A`..`0x08009C48`). LOGExtractor's "running index selects
a tile directly" is **REFUTED**; its recurrence is **CONFIRMED**.

**Consumers.** The decoded *stream* has exactly one consumer, `0x08009BD4`. The
*field* `root+0x48` has two: `0x08009B80` also loads it and takes
`declared_size / 2` to derive the static selector count used with the
`root+0x0C`/`+0x10` animation records. That second reader does not decode the
stream, so the recurrence and the `(bank, tile)` split are unaffected.

## Global graphics source and `0x179764`

**0x179764 HYPOTHESIS: CORRECTED.** GBA address `0x08179764` is exactly the value
held at `root+0x4C` on **all 452** roots. It points at **187 consecutive aligned
in-ROM u32 pointers**, every one a kind-1 Webfoot container, 186 declaring
`0x4000` bytes and the last (index 186, at `0x08177AB8`) declaring `0x3C40`. The
entry after the table is `0x00000001`. The largest `value >> 8` bank index used
by any canonical selector stream is **186**, exactly the last table entry, and
the largest `value & 0xFF` tile index used is 255. So `0x179764` is a
**per-descriptor pointer field's value** - the selector-bank container table -
not an independent global graphics structure. Its location matches
LOGExtractor's address; its identity and ownership do not.

**128x128 / 256-TILE HYPOTHESIS: PARTIALLY CONFIRMED as an engine resource unit;
REFUTED as a universal property.** The engine allocates a fixed `0x4000`-byte
decode buffer (`0x08009C18`) and indexes it with an 8-bit field scaled by 64, so
256 64-byte tiles is the exact addressed capacity; 256 tiles at 8x8 is 16x16
tiles = 128x128 px. But 186 of 187 canonical banks declare exactly `0x4000`, one
declares `0x3C40`, and the payload side of this ticket uses a different decoded
size (`0x800`) and index width.

## Non-dominant handler applicability

**Applicability: handler `0x08008087` only. CONFIRMED.**

| Handler | References | Unique records | `+0x14` | `+0x15` | `x*y` |
| --- | ---: | ---: | --- | --- | --- |
| `0x08007A41` | 249 | 1 | `0` only | `0` only | `0` only |
| `0x08007B63` | 1 | 1 | `64` | `192` | `12288` |
| `0x080088BD` | 1 | 1 | `48` | `251` | `12048` |
| `0x0800897B` | 41 | 41 | `0` x28, `85` x4, `86` x2, `170` x1, `171` x6 | 11 values | `0` x29, `85` x4, `21930` x2, `41382` x1, `43434` x4, `43605` x1 |

`0x08007A41` is the absent-layer placeholder (`0x08007A40` allocates 8 bytes and
has no payload); the two singletons' dimension bytes cannot be a chunk grid; and
`0x0800897B` fails the dominant reading on 29 of 41 records. The probe enumerates
the `+0x18` window **only** for the dominant handler and reports the others by
shape, dereferencing nothing.

## Full-census results

| Count | Value | Unit |
| --- | ---: | --- |
| 452 | map entries | maps |
| 421 | distinct selector-1 roots | roots |
| 1516 / 1420 | dominant references / unique records | layer records |
| 4274 | enumerated array elements | chunk-grid cells |
| 3745 | distinct non-null targets | unique pointers |
| 165 | shared targets | unique pointers |
| 3745 | distinct payload digests | unique payloads |
| 3,834,880 | decoded entries (`3745 * 1024`) | tile entries |
| 1,241,888 | nonzero tile-index references | tile entries |
| 0 | references outside both tile loaders | tile entries |
| 452 | decoded selector streams | maps |
| 187 | bank-table entries | unique pointers |

Arithmetic checks: `4274 = 156 + 4118`; `3,834,880 = 3745 * 1024`;
`1,241,888 = 1,218,581 + 23,307`; `187 = 186 + 1`. No percentage is reported
without its numerator and denominator.

## Representative raw chunks, entries and selector streams

```text
map 39, root 0x08294968, layer slot +0x18, record 0x08293BEC, grid 3x2
  cell 0 -> container 0x082934C4
    header bytes   01 00 00 00 00 08 00 00      (kind 1, declared 0x800)
    words[0:16]    0000 0000 0000 0000 0000 0000 0000 0000
                   0027 0028 0029 002A 002B 0000 0000 0000
    distinct 82, zero entries 716, high nibble {0}
  cell 1 -> container 0x082935A0
    words[23:32]   0001 0002 00C2 00B4 00B5 002F 0030 0031 0032

map 39, layer slot +0x20, record 0x08294628, grid 4x2
  cell 0 -> container 0x082941FC
    words[24:32]   0055 0056 037F 0057 004D 004E 004F 00E8
                   0x037F = 895, this map's animated-tile destination
  cell 1 -> container 0x08294268
    words[0:16]    006E 006F 00E9 00EA 00AC 00EB 008F 0095
                   0096 0091 0092 0090 0091 0092 0090 008F
    zero entries 0

first dominant target in the image, 0x08179A50
    words[0:16]    0001 0002 0003 0004 0005 0006 0007 0008
                   0009 000A 000B 000C 000C 000C 000C 000C

map 39 selector stream  root+0x48 = 0x08294660
    header bytes   01 00 00 00 06 02 00 00      (kind 1, declared 0x206)
    raw[0:10]      0000 01BC 0000 0000 0000 0000 0000 0000 0000 0000
    absolute[0:10] 0000 01BD 01BE 01BF 01C0 01C1 01C2 01C3 01C4 01C5
map 40 selector stream  root+0x48 = 0x082932F8  declared 0x1DE (239 words)
map 0  selector stream  root+0x48 = 0x082B8BF4  declared 0x692 (841 words)

bank table at 0x08179764
    [0]   0x080945C0  kind 1  declared 0x4000
    [1]   0x080959B4  kind 1  declared 0x4000
    [186] 0x08177AB8  kind 1  declared 0x3C40
    [187] 0x00000001  (end of table)
```

Representative instruction bytes (raw halfwords as stored, verified against the
image):

```text
0x08007B94  26 71                     strb r6,[r4,#4]   object+0x04 = layer slot
0x08007BE0  46 43 04 2E 13 DC 00 25   muls / cmp #4 / bgt / movs r5,#0
0x08007BFE  E9 02 09 19 4C 31 35 F0   lsls #0xB / add / add #0x4C / bl 0x0803D940
0x08007DAE  28 79 34 1C C0 02 47 18   ldrb object+4 / lsls #0xB / adds -> 0x0600E000 + slot*0x800
0x08008022  24 12 1B 12               asrs #8 on both axes (256 px per chunk)
0x0800805C  C9 10 ED 10                asrs #3 on both axes (8 px per tile)
0x0800806A  EC 06 64 0D C9 06 89 0E   (row & 31)*64 ; (col & 31)*2
0x08008074  59 5A 00 29 D1 01 00 20    ldrh / cmp #0 / bne / movs r0,#0
0x080093D6  E0 6B 9C 49 C0 00 14 31   ldr root+0x3C / table base / lsls #3 / +0x14
0x080093E6  01 21 89 06 0A 81          r1 = 0x04000000 / strh r2,[r1,#8]
0x08009BE6  88 6C 40 68 C1 0F 08 18   ldr root+0x48 / ldr container+4 / size rounding
0x08009C08  DB 8B 62 5A 01 30 D2 18 01 32 62 52   the recurrence
0x08009C66  08 5A 00 99 40 22 00 06 80 0C 41 18 30 1C   low byte * 64 -> 64-byte copy
0x080046AA4 10 47                    bx r2  (virtual-call trampoline)
```

## Anomalies

| Anomaly | Count |
| --- | ---: |
| Dominant record with a null inside the `x*y` window | 117 (record and reference level) |
| ... with a non-null after a null | 85 |
| Malformed / out-of-ROM / undecodable array element | 0 |
| Target declaring anything other than `0x800` | 0 |
| All-zero payload | 0 |
| Payload digest shared by two targets | 0 |
| Selector stream that failed to decode | 0 |
| Selector stream with an odd declared size | 0 |
| Tile reference outside both engine loaders | **0 of 1,241,888** |
| Bank table entry that is not a kind-1 container | 0 |
| Bank declaring a size other than `0x4000` | 1 (index 186, `0x3C40`) |
| Selector-1 roots whose `+0x3C` is not 0 | **1** (map 19, root `0x082AD8BC`, value 1) |
| Selector-1 roots whose four `BGxCNT` screen bases are not `28..31` | **0** (map 19's index-1 record keeps bases 28..31; only its BG2 screenblock size differs) |

## Tooling added

- `tools/research/logx_tile_probe.py` - SHA-256 gated, read-only, deterministic
  census. Reuses the accepted selector-1 root resolution and layer-record reader
  by import. Modes: summary, `--targets`, `--references`, `--chunks`,
  `--selectors`, `--tile-index`. Shared-target aware: the entry census is
  aggregated over **unique payloads**, never over references. Columns describe
  physical shape, container kind, decoded width and raw bit position only.
  Determinism verified by two byte-identical runs over the canonical image.
- `tools/research/thumb_disasm.py` - **extended**, not replaced:
  `decode_thumb_at`, `iter_thumb_wide`, `linear_thumb_wide` offer each site a
  four-byte window so two-halfword Thumb instructions decode, and
  `find_field_extractions` enumerates every `lsls`/`lsrs` mask-or-field pair by
  raw halfword scan. The legacy two-byte entry points are left unchanged so
  LOGX-LAYER-001's published undecodable-halfword census stays reproducible; the
  distinction is documented in the module docstring.

## Tests added

`tests/integration/test_logx_tile_rom.py`, **30 ROM-gated tests**. They skip
cleanly when the canonical ROM is not configured and never write to it. They
assert only the independently established facts: the array/pointer census and
its arithmetic; container kind and declared size; the 117/85 null anomalies;
non-dominant handlers reported by shape only; the union entry census and the
full per-bit table; representative payload words and selector streams; the
32x32 constants; the exact instruction bytes for the array indexing, the row and
column masks, the occupancy test, the pixel shifts, the VRAM destination, the BG
register write, the recurrence and the 64-byte tile copy; the BG control
halfwords and the two-record variation; the 187-entry bank table; the largest
bank index; the tile-index coverage invariant; the engine-side bit scans; and the
probe's documented invocation and refusal behaviour.

`tests/unit/test_thumb_disasm_field_extraction.py`, **11 portable synthetic
tests**. No ROM and no private input: they build the halfword sequences the
helper claims to recognise and pin both the plain mask idiom
(`lsls #a ; lsrs #a`, `right_shift == 0`) and true field extraction, plus the
wide-window `bl` decode. They exist because the first draft of the helper
required a strictly larger second shift, which made `right_shift == 0`
unreachable and every ROM-gated "no site masks the low *n* bits" assertion
vacuously true.

## Test results

Measured in this worktree with `LOGX_CANONICAL_ROM` and `WEBFOOT_BUU_ROM` set to
the canonical ROM, after the review corrections:

- `tests/integration/test_logx_tile_rom.py` + `tests/unit/test_thumb_disasm_field_extraction.py`:
  **41 passed** (52.5 s) - 30 ROM-gated integration tests and 11 portable
  synthetic tests.- The four LOGX files plus `tests/integration/test_map_render_rom.py` (the
  accepted production renderer) and the two safety files: **101 passed,
  2 skipped** (78.9 s). The two skips are the MAP-VIS-001 VRAM oracle inputs,
  which are not configured here; the LOGX-LAYER-001 review records the same two
  skips.
- `tests/unit` (whole directory): **1308 passed, 15 skipped**. The skips are nine
  PySide6-dependent Workbench modules, three site-build-dependent questline
  tests, one VRAM-dump-dependent map-render test and one ROM-dependent Workbench
  session test.
- `tests/unit/test_project_safety.py`, `test_rom_safety.py`,
  `test_code_review_workflow.py`, `test_workflow_migration.py`: **31 passed**.
- With the ROM unavailable, `test_logx_tile_rom.py` reports **4 passed,
  26 skipped, 0 failed** - the four that need no ROM are the pointer-classification
  contract, the payload-shape constants, the non-canonical-image rejection and
  the non-canonical-file refusal. The portable synthetic file needs no ROM and
  passes either way.

The record-shape findings of this ticket do not disturb the accepted production
renderer.

Private-runtime validation: **none performed**. This ticket is static-only, made
no mGBA capture and produced no derived ROM.

Environment note: `tmp_path`-using tests fail with
`PermissionError: [WinError 5] ... \AppData\Local\Temp\pytest-of-<user>` in this
environment. That is pre-existing and not ticket-caused - the same failure occurs
on the untouched `tests/integration/test_logx_layer_rom.py` - and every run above
was made with an explicit `--basetemp`. The independent reviewer could not
reproduce the claim on their machine and therefore did not confirm it; it is a
local environment observation, not a ticket finding.

## ROM_BIBLE_IMPACT

`docs/reverse-engineering.md` gains a "LOGX-TILE-001 chunk payloads and tile
entries" section stating physical facts only: the element-to-container
resolution and the two dereference-free steps, the reference/target/payload
counts, the 32x32x2-byte payload shape with its engine constants, the per-bit
table with bits 12-15 classified as reserved/constant rather than "unused", the
8x8 tile and 256x256 chunk derivation, the BG register halfwords, the selector
container and its prefix recurrence and packed `(bank, tile)` semantics, the
corrected identity of `0x179764`, the handler-applicability boundary, and the
resolution of LOGX-LAYER-001's four-slot-cap question. Layer positioning stays
UNRESOLVED. No speculative semantic name is promoted.

## public progress impact

**NONE.** The ticket is research-only: no parser, editor, renderer or SDK facade
changes, no new shipping capability, and no public frontier moves.

## Disagreements with LOGExtractor

1. `0x179764` is the value of a scene-descriptor pointer field
   (`root+0x4C`) and points at a 187-entry bank-container table, not a global
   graphics structure.
2. The 128x128 / 256-tile source block is a bank's addressed capacity, not a
   stored dimension; one canonical bank declares `0x3C40`.
3. Bits 12-15 must not be documented as "unused": absent from canonical data and
   unread by any consumer, but not inert to the engine's own occupancy test.
4. A decoded selector is a `(bank, tile)` pair, not a bare tile index.
5. `root+0x48`'s recurrence is **confirmed**; its use of the resulting value is
   **refuted** as stated.
6. LOGExtractor's `+0x0D`/`+0x11` and `+0x1C` readings remain refuted by
   LOGX-LAYER-001 and are not revisited.

## Unresolved questions

1. Bit 10 versus bit 11 direction (platform-derived; no engine read). A
   reversible derived-ROM experiment could settle it; not performed.
2. Semantic role of bits 12-15 - reserved by the format, or merely inert under
   the 8bpp BG configuration.
3. What an internal null in the `+0x18` window displays: the constructor skips it,
   the streaming path substitutes the default container `0x08070808`.
4. `object+0x34`/`+0x38`, added to a query coordinate, are never written by any
   recovered code, so the query coordinate space is only partly explained.
5. `root+0x34`/`+0x38`: two `0x2000`-byte decodes plus a `memcpy` to
   `object+0xB0` (`0x080095AA`..`0x080095C0`). Bounded here as outside the tile
   index space (0 of 1,241,888 references need it) but not explained.
6. `root+0x08`/`+0x0A`, consumed by the same `0x0800953E` path.
7. The `0x08007B63` and `0x080088BD` singletons.
8. Packed-stream internals.

## Handoff to LOGX-CONNECTOR-001

Nothing new. The `0x18`-byte element stride remains scoped to root `+0x24`/`+0x28`
and MapEntry `+0x18`; no layer-record site uses it.

## Handoff to LOGX-CODEC-001

- Decompressor entry `0x0803D940`: `kind 0` -> `memcpy(dst, src+8, src[+4])`,
  `kind 1`/`kind 2` -> packed decoder `0x08049120`, any other kind -> return with
  the destination untouched. Two arguments only; the caller's `r2` is discarded.
- No bound and no returned length: the decoded size is the container's `+0x04`.
- Canonical container usage measured here: 3745 dominant chunk targets all kind 1
  `0x800`; 452 selector streams (450 kind 1, 2 kind 0); 187 bank containers
  (186 x `0x4000`, 1 x `0x3C40`).
- Still LOGX-CODEC-001's: canonical wrapper behaviour in general, the
  raw/uncompressed wrapper form beyond the kind-0 `memcpy` branch, the
  first-word-zero disagreement, the `UnknownHeader` path, general encoder
  requirements, and every other compressed asset class.

## Other downstream handoffs

- **Any position consumer:** layer positioning is still UNRESOLVED.
- **Any renderer change:** the 32x32 payload shape, bits 0-9 semantics and the
  character-region ordering are now engine-proven and can be relied on; the
  bit 10/11 direction is not engine-proven.
- **LOGX-LAYER-001 successor:** its four-slot-cap open question is resolved by
  this ticket; its other questions are unchanged.

## Independent review

Two fresh-context reviewers were used, each with no knowledge of this ticket's
working sessions and each free to write and run its own analysis code against the
canonical image. Both verified the ROM SHA-256 before and after their work and
neither wrote to the image or to the worktree.

**Reviewer A - census and disassembly gate. Verdict: REJECT (fixable), then
re-verified.** It independently re-derived every census number with its own code:
452 / 421 / 1808 / 1464; 1516 / 1420; `4274 = 156 + 4118`; 3745 distinct with 165
shared and a maximum reuse of 10; the target range; all 3745 targets kind-1
declaring `0x800` and decoding to 2048 bytes with 3745 distinct digests; the full
union bit table; the 117/85 anomalies; all 452 selector streams; map 39's stream
and recurrence; the 187-entry bank table; and the coverage invariant
`1,218,581 + 23,307 = 1,241,888` with 0 exceptions on 178 maps. Every one matched
exactly. It reproduced all 17 cited instruction byte ranges, found no
instruction-level statement in provenance sections 4, 6, 9 or 10 contradicted by
disassembly, and confirmed that the only platform-convention claim (bit 10/11
direction) is correctly labelled PARTIALLY CONFIRMED. It confirmed the ROM
unchanged. It then reported seven blocking corrections, of which C1 was found
independently by this ticket during self-check before the verdict arrived.

**Reviewer B - adversarial verification. Verdict: APPROVE WITH REQUIRED
CORRECTIONS.** It attacked each conclusion rather than confirming it, using
dataflow rather than linear sweeps:

- **no second dereference**: enumerated every `ldr rN,[rM,#8]` and
  `ldr rP,[rQ,#0x18]` site with a nine-instruction backward window. Exactly seven
  candidates, of which only the two dominant-layer consumers hand the value to
  `0x0803D940`; no site dereferences one more level. **SURVIVES.**
- **verbatim copy, no repack or runtime mutation**: the only reads of
  `object+0x10`..`+0x1C` are the row `memcpy` and the `ldrh`; the only `strh` in
  the layer code region writes `REG_BGxHOFS`. **SURVIVES.**
- **bit absence claim**: **WEAKENED.** It confirmed the cited sites and the
  table-block claim, but showed the technique set does not cover
  shift-then-branch carry tests, `movs`+`lsls` mask builds or non-adjacent
  `lsls`/`lsrs` pairs, and that the image-wide form of the claim is therefore not
  established. Every sampled source is an object field, never a payload buffer,
  so the payload-scoped conclusion stands but the wording had to be corrected
  (correction 4 below).
- **BGxCNT derivation**: decoded bit by bit and confirmed; also independently
  reproduced the `root+0x3C` census (451 zeros, map 19 = 1). **SURVIVES.**
- **bits 12-15 classification**: re-expanded **all 1439** dominant-shape records
  (4002 non-null elements, 160 nulls) and confirmed no size outlier, no entry
  writer anywhere, and that the null-cell default container `0x08070808` is
  kind 0 with `0x800` zero bytes - so no runtime path can set those bits.
  **SURVIVES.**
- **selector recurrence and `(bank, tile)` split**: verified instruction by
  instruction. **SURVIVES**, with the one omission corrected below
  (correction 5).
- **`0x08179764`**: 427 aligned words hold the value, all inside the descriptor
  region; the 30 apparent direct code references are data coincidences whose
  "disassembly" contains Thumb-2 forms that cannot execute on ARM7TDMI.
  **SURVIVES.**
- **`0x800` stride and the 19 orphan records**: reproduced the orphans and the
  products, and confirmed over all 1439 records that no element declares anything
  but kind-1 `0x800`, so the stride cannot overrun the `0x204C` allocation.
  **SURVIVES.**
- **four-entry resident cache**: read `0x08007C12` end to end and confirmed the
  cache size and the conclusion. **SURVIVES, not over-stated.**

## Required corrections

Every correction below was independently re-verified against the ROM by this
ticket before being applied, and the affected numbers were re-measured rather
than copied from a review.

| # | Correction | Source | Status |
| ---: | --- | --- | --- |
| 1 | `find_field_extractions` compared the two shift amounts with a strict `>`; `right_shift == 0` was therefore **unreachable**, and every "no site masks the low *n* bits" statement was vacuously true rather than measured. Changed to `>=`; the scan total rose from 959 to **1532**; added a portable synthetic test that fails if the vacuous form returns. | found in self-check, independently confirmed by A as its worst blocker | APPLIED and re-verified |
| 2 | `root+0x3C` is **not** 0 on every root: 451 roots hold 0 and **map 19 (root `0x082AD8BC`) holds 1**, selecting `0x080716E0 = 1C80 1D80 BE80 1F80`, whose BG2 is 512x256. Corrected in the provenance document, the review document and the ROM bible. | A (C2), independently confirmed by B | APPLIED and re-verified |
| 3 | `"961 of them inside 0x08000000..0x08007000"` transposed two digits of the range. Corrected to the full breakdown: 46 below `0x08007000`, 29 in the map/layer region, 961 in the first `0x70000` bytes, 571 above. | B (1) | APPLIED and re-verified |
| 4 | The absence claim was stated image-wide. Rewritten to the payload-scoped form, with the three unscanned idioms measured and published (8,014 shift-then-branch pairs, 1,204 `movs`+`lsls` builds, non-adjacent pairs) and the sampling result that none of them reads a payload buffer. Corrected in the provenance document, the review document and the ROM bible. | B (4), corroborated by A (C) | APPLIED and re-verified |
| 5 | `"its only consumer"` was too narrow: the decoded stream has one consumer, but the *field* `root+0x48` has two, because `0x08009B80` reads its declared size. | B (5) | APPLIED and re-verified |
| 6 | `"inside the code that owns a layer payload there is no mask or field extraction reaching bit 9 or above at all"` contradicted the ticket's own table row for the two in-region `(0, 16)` `& 0xFFFF` truncations. Rewritten as "no pair in the region has `right_shift >= 9`". | B (3) | APPLIED and re-verified |
| 7 | The BL/BLX figures mixed two enumerations. Replaced with one enumeration stated per number: **8,838** 4-byte-aligned encodings, **8,266** resolving in-ROM, **4,440** distinct targets, per-block call targets **2**..**1,384**, block `0x08060000` = **9**, `0x0806E000..0x0806F000` = **0**. Also corrected the bytes quoted at `0x0806E640` to `0x03800070` / `0x00000C00` / `0x40040002`. | B (2) and A (C3, C4, C5) | APPLIED and re-verified |
| 8 | `"Expanding every unique dominant payload (1,241,888 nonzero entries)"` used the wrong unit. 1,241,888 is a per-map, per-reference expansion; the unique-payload expansion is **1,107,699** (`3,834,880 - 2,727,181`). Both are now stated with their units, and the probe's union output carries `nonzero_entries` so the two can never be confused again. | A (C6), independently confirmed by B | APPLIED and re-verified |
| 9 | `0x0800897B`'s first-window-word prose was ambiguous. Replaced with the four exact values and their record counts: `0x00000000` on 38 records, plus `0xFFFFFF56`, `0xFFFFFFAB` and `0x000000AA` once each, all three outside the ROM address range. | A (C7) - A's own classification of `0x000000AA` as unaligned-in-ROM is itself incorrect, since it lies below the ROM base; the document states the measured class | APPLIED and re-verified |
| 10 | BGxCNT receives `record[bg]` **plus** a per-frame offset (`0x080093E2`/`0x080093E4`), not the record unconditionally. Stated. | B (6) | APPLIED and re-verified |
| 11 | Two image-wide absence claims ("the only payload read", "the only engine test") stated no coverage method. Both now name the enumeration and the region scan behind them. | A (a) | APPLIED and re-verified |
| 12 | `"only when x*y <= 4"` omitted the constructor's `x*y == 0` guard at `0x08007BE8`. Corrected to `0 < x*y <= 4`. | A (b) | APPLIED and re-verified |
| 13 | ROM bible: `root+0x4C` is a pointer to the bank array, which is then indexed; reworded. | A (c) | APPLIED and re-verified |
| 14 | The quoted BG-register instruction block skipped `0x080093E2`/`0x080093E4`. Added. | A (d) | APPLIED and re-verified |
| 15 | "invoked by the layer object's own render methods" was asserted as fact; it rests on the recovered class table, not on a direct call. Now marked **INFERRED** and the two `bl` callers named. | A (e) | APPLIED and re-verified |
| 16 | The 19 orphan records yield **86** cells of which **82** are non-null; the paragraph implied all 82. Corrected, and the independent reproduction recorded. | B (non-blocking) | APPLIED and re-verified |
| 17 | The placeholder class `0x08049548` `memset`s the same screenblock region to zero (`0x08007A28`..`0x08007A38`); the blit is not the region's only writer. Recorded. | B (non-blocking) | APPLIED and re-verified |
| 18 | The constructor initialises `object+0x10`..`+0x1C` to the default container `0x08070808` (`0x08007BA8`..`0x08007BB2`); added, because it explains the null-cell blit path. | B (non-blocking) | APPLIED and re-verified |
| 19 | The payload-read enumeration cannot exclude an indirect call reaching a reader. Scoping caveat added. | B (non-blocking) | APPLIED and re-verified |
| 20 | `tmp_path` `PermissionError` claim: reviewer A could not reproduce it on its machine. Retained as a local environment observation only, and labelled as such. | A (non-blocking) | APPLIED |

No correction was rejected, and no reviewer finding was accepted on its word
alone: each was re-measured here first. Two reviewer assertions did not survive
that check and are recorded rather than adopted - reviewer A's classification of
`0x000000AA` as unaligned-in-ROM, and reviewer B's per-64 KiB-block range, which
belongs to a different enumeration than the one the document now cites.

## Correction gate

Closed. All 20 corrections were verified against the ROM by this ticket, the
provenance document, the review document and the ROM bible were updated, and the
focused suites plus the surrounding integration files were re-run after the last
edit: `test_logx_tile_rom.py` + `test_thumb_disasm_field_extraction.py`
**41 passed**; with the four LOGX files, `test_map_render_rom.py` and the four
safety/workflow unit files **123 passed, 2 skipped**; `tests/unit`
**1308 passed, 15 skipped**; and with the ROM unavailable `test_logx_tile_rom.py`
**4 passed, 26 skipped, 0 failed**.
The canonical ROM SHA-256 was re-verified as unchanged after the corrections, and
the probe's output was re-checked for determinism (two byte-identical runs).

## Git status

The isolated worktree's change set is **4 new files plus 2 edited files**:

```text
 M docs/reverse-engineering.md
 M tools/research/thumb_disasm.py
?? docs/research/LOGX_TILE_PROVENANCE.md
?? docs/research/LOGX-TILE-001-review.md
?? tests/integration/test_logx_tile_rom.py
?? tests/unit/test_thumb_disasm_field_extraction.py
?? tools/research/logx_tile_probe.py
```

Unlike the LOGX-LAYER-001 worktree, this checkout produced no CRLF noise: the
worktree reports exactly those seven paths, so a whole-tree `git diff --check` is
usable here and is clean (`exit 0`). None of the new files contains trailing
whitespace or a tab; all are LF.

No ROM, save, state, dump, derived ROM, generated commercial asset or `extern/`
checkout is staged or untracked in the worktree; the canonical ROM lives outside
it and outside the repository tree, and its SHA-256 was re-verified unchanged
after the work.
