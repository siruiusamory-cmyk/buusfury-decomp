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
  covering `0..895`. Expanding every nonzero entry (1,241,888 of them) against
  the map's static selector ordinals and its animated-tile destination ranges
  leaves **0 exceptions** (1,218,581 static, 23,307 animated, on 178 maps). Bits
  0-9 are also CONFIRMED as the hardware character name: the halfword reaches the
  BG screenblock unchanged, and the engine writes `BG0CNT..BG3CNT` =
  `0x1C80 0x1D80 0x1E80 0x1F80` (8bpp, character base 0, screen bases 28..31).
- **BIT 10: CONFIRMED** to exist, to be used and to lie outside the tile-index
  field. **Horizontal-flip direction: PARTIALLY CONFIRMED** - the platform BG
  entry layout applied to a verbatim VRAM copy; no recovered engine instruction
  reads the bit. No site anywhere in the image isolates bit 10.
- **BIT 11: CONFIRMED** likewise. **Vertical-flip direction: PARTIALLY
  CONFIRMED**, same basis. Four sites isolate bit 11, all inside the
  `0x0806E000..0x0806F000` table block, which no `BL`/`BLX` in the image reaches
  and which is not the map/layer code region.
- **BIT 12, 13, 14, 15: RESERVED / CONSTANT IN CANONICAL DATA; UNUSED BY ANY
  KNOWN CONSUMER; semantic role UNRESOLVED.** Zero on all 3,834,880 entries. No
  `0x0000F000` or `0x00000FFF` mask exists as an aligned word anywhere in the
  image; no site extracts a 4-bit field at shift 12 in code. They are **not**
  documented as "unused by the format": the engine's occupancy test at
  `0x08008076` treats any nonzero entry as occupied, so a nonzero high nibble
  would not be inert.

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

## Tooling added

- `tools/research/logx_tile_probe.py` - SHA-256 gated, read-only, deterministic
  census. Reuses the accepted selector-1 root resolution and layer-record reader
  by import. Modes: summary, `--targets`, `--references`, `--chunks`,
  `--selectors`, `--tile-index`. Shared-target aware: the entry census is
  aggregated over **unique payloads**, never over references. Columns describe
  physical shape, container kind, decoded width and raw bit position only.
- `tools/research/thumb_disasm.py` - **extended**, not replaced:
  `decode_thumb_at`, `iter_thumb_wide`, `linear_thumb_wide` offer each site a
  four-byte window so two-halfword Thumb instructions decode, and
  `find_field_extractions` enumerates every `lsls`/`lsrs` field-extraction pair
  by raw halfword scan. The legacy two-byte entry points are left unchanged so
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
register write, the recurrence and the 64-byte tile copy; the BG control halfwords
`0x1C80 0x1D80 0x1E80 0x1F80`; the 187-entry bank table; the largest bank index;
the tile-index coverage invariant; the engine-side bit scans; and the probe's
documented invocation and refusal behaviour.

## Test results

Measured in this worktree with `LOGX_CANONICAL_ROM` and `WEBFOOT_BUU_ROM` set to
the canonical ROM:

- `tests/integration/test_logx_tile_rom.py`: **30 passed** (72 s).
- The four LOGX files plus `tests/integration/test_map_render_rom.py` (the
  accepted production renderer): **81 passed, 2 skipped** (57 s). The two skips
  are the MAP-VIS-001 VRAM oracle inputs, which are not configured here; the
  LOGX-LAYER-001 review records the same two skips.
- `tests/unit/test_project_safety.py`, `test_rom_safety.py`,
  `test_code_review_workflow.py`, `test_workflow_migration.py`: **31 passed**.
- With the ROM unavailable, `test_logx_tile_rom.py` reports **4 passed,
  26 skipped, 0 failed** - the four that need no ROM are the pointer-classification
  contract, the payload-shape constants, the non-canonical-image rejection and
  the non-canonical-file refusal.

The record-shape findings of this ticket do not disturb the accepted production
renderer.

Private-runtime validation: **none performed**. This ticket is static-only, made
no mGBA capture and produced no derived ROM.

Environment note: `tmp_path`-using tests fail with
`PermissionError: [WinError 5] ... \AppData\Local\Temp\pytest-of-<user>` in this
environment. That is pre-existing and not ticket-caused - the same failure occurs
on the untouched `tests/integration/test_logx_layer_rom.py` - and every run above
was made with an explicit `--basetemp`.

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

**Verdict: PENDING.** Recorded in the review/correction commit that follows the
research commit, together with a required-corrections table and the correction
gate state.

## Required corrections

Recorded in the review/correction commit.

## Correction gate

Recorded in the review/correction commit.

## Git status

The isolated worktree's change set is **3 new files plus 2 edited files**:

```text
 M docs/reverse-engineering.md
 M tools/research/thumb_disasm.py
?? docs/research/LOGX_TILE_PROVENANCE.md
?? docs/research/LOGX-TILE-001-review.md
?? tests/integration/test_logx_tile_rom.py
?? tools/research/logx_tile_probe.py
```

Unlike the LOGX-LAYER-001 worktree, this checkout produced no CRLF noise: the
worktree reports exactly those five paths, so a whole-tree `git diff --check` is
usable here and is clean (`exit 0`). None of the new files contains trailing
whitespace or a tab; all are LF.

No ROM, save, state, dump, derived ROM, generated commercial asset or `extern/`
checkout is staged or untracked in the worktree; the canonical ROM lives outside
it and outside the repository tree, and its SHA-256 was re-verified unchanged
after the work.
