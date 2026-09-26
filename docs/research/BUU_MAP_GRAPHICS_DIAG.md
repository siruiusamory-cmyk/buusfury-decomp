# Buu's Fury map graphics corruption: diagnosis

Evidence document for `MAP-GFX-DIAG-001`. Canonical image: Buu's Fury USA rev 0,
SHA-256 `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

Claims use this repository's labels: **CONFIRMED_ROM**, **CONFIRMED_RUNTIME**,
**INFERRED**, **UNKNOWN**, and the runtime levels **LEVEL 3** (verified runtime
observation) and **LEVEL 4** (meaningful runtime subsystem confirmed).

**No production behaviour changed.** This ticket diagnoses; it does not correct.
The candidate rule below is carried as an injectable decoder under the ignored
`build/gfxdiag/` tree so that the shipping decoder is untouched.

> **EXECUTED (2026-09-26, WEBFOOT-LZ-LITERAL-BASE-001).** The correction §9
> specifies has since shipped: the rule is now in
> `tools/webfoot/formats/webfoot_lz.py::_unpack_stream`, in the export reader and
> in the research reference, and every pin this document predicted would move has
> been re-baselined with per-pin attribution. The evidence record is
> [`../tickets/WEBFOOT-LZ-LITERAL-BASE-001.md`](../tickets/WEBFOOT-LZ-LITERAL-BASE-001.md).
> Every number below is the **pre-correction** measurement and is left as it stood.

## 1. Result

**The corruption is a decompression defect, not a layout, palette or bit-depth
defect.** `tools/webfoot/formats/webfoot_lz.py` carries the packed stream's
*literal base* across a switch back to 8-bit literals:

```python
literal_bits = 7 + reader.bit()
if literal_bits != 8:
    literal_base = reader.get(8)
```

The engine clears that base when the stream returns to 8-bit literals. The
consequence is that the SDK decodes some atlas tiles with pixel indices that are
uniformly too high (measured: `+2`, and `+15` in one tile), so the tiles keep
their shape and lose their colours. Measured on the retail engine's own screen:
the shipping decode reproduces **84.07 %** of the visible frame; the corrected
decode reproduces **93.90 %**, which is *exactly* the ceiling set by feeding the
engine's own VRAM back through the same renderer.

Blast radius, measured over the canonical image:

| Quantity | Value |
| --- | --- |
| Atlas banks whose decode changes | **77 / 187** |
| Maps whose assembled character block changes | **369 / 452** |
| Chunk (screen-entry) containers whose decode changes | **0 / 3745** |

The last row is why the symptom looks the way it does: the map **layout** is
correct and only the **tile pixels** are wrong, so geometry reads correctly while
tiles appear to be "from elsewhere" and "the wrong colour".

## 2. Corpus

Chosen with the maintainer from the compiled resource compile (`<resource-library>`,
452 maps, 1,808 layers). Reported symptoms: Yakon's Planet, Yemma's Office and
West City. The first two screenshots were matched back to their artifacts by
`build/gfxdiag/match_reported.py` at distance 0.00000, so the map identity is not
a guess.

| Map | Root | Role | Reported symptom |
| --- | --- | --- | --- |
| `map:0040` Grand Kai's Planet | `0x08293474` | known good (runtime-validated by MAP-VIS-001/002) | none |
| `map:0036` Yemma's Office | `0x08297C84` | bad, **runtime-captured this ticket** | tiles/colours, "the Other World planes" |
| `map:0179` Yakon's Planet | `0x08229F50` | bad | "a lot of errors" |
| `map:0102` West City | `0x0826A778` | bad | "wrong colour" trees, large empty regions |
| `map:0039` Grand Kai's Planet (west) | `0x08294968` | known good (cross-check) | none |

## 3. Evidence

### 3.1 The library is not stale - CONFIRMED_ROM

Every layer of all 452 maps was re-rendered from the current tree and compared
with the compiled artifact the user is looking at: **0 maps, 0 layers differ**
(`build/gfxdiag/compare_library.py`). The compile and the tree are the same
render, so the reported images are the current renderer's output.

### 3.2 The map chain and the layer records are right - CONFIRMED_RUNTIME

A new read-only observer (`tools/runtime/mapgfxdiag001_map_layer_dump.lua`) dumped
the engine's own state after settling. Live versus SDK, all equal:

- root `0x08297C84`, extent `273`/`353`, selector container `0x08297BDC`, bank
  table `0x08179764`, BG addends `2:3:3:3`;
- all four layer records and all sixteen chunk-window words, byte for byte.

### 3.3 The screen entries are right - CONFIRMED_RUNTIME

Under the engine's own storage warp, logical cell `(x, y)` lives at physical cell
`(y & 31) * 32 + (x & 31)` (MAP-VIS-002). Searching every window origin
(`build/gfxdiag/probe_window_match.py`, validated by reproducing map 40's pinned
origins `(0,0)`, `(0,9)`, `(0,9)`, `(0,9)` and map 39's `(54,8)`, `(62,8)` at
0/1024 mismatch):

| BG | SDK class | window origin | mismatch |
| --- | --- | --- | --- |
| BG0 | dominant 2x2 | (0,23) | **0 / 1024** |
| BG1 | dominant 2x2 | (0,28) | **0 / 1024** |
| BG2 | dominant 2x2 | (0,32) | 186 / 1024, every one a live-zero cell |
| BG3 | dominant 2x2 | (0,32) | 192 / 1024, every one a live-zero cell |

The BG2/BG3 residual is the documented unpopulated-window phenomenon: the engine
has not streamed those cells, and every other cell is the ROM word exactly. **The
SDK's chunk composition reproduces the engine's screen entries.**

### 3.4 The palette and the layering are right - CONFIRMED_RUNTIME

- Live palette: **256 / 256** entries equal the ROM table at 5-bit precision.
- Live `BG0CNT..BG3CNT` priorities `2,3,3,3` equal the root's four addend bytes
  `[2,3,3,3]`, so the composite order the renderer uses is the engine's.
- All four BGs are 8bpp with char base 0.

### 3.5 The character block is wrong - CONFIRMED_RUNTIME

`build/gfxdiag/analyze_run.py` over the settled dump: **647 / 859** tiles
byte-identical, **212 differ**. The differing tiles are referenced by the
displayed layers, so they are visible.

### 3.6 The engine's own tile bytes are our bytes minus a constant - CONFIRMED_RUNTIME

Bank 141 is referenced by all 256 of its tiles from map 36, so live VRAM is a
**complete** copy of the engine's payload for that container. Diffing the full
16,384 bytes (`build/gfxdiag/probe_full_bank_diff.py`):

- 1,762 bytes differ, **every one by exactly −2** (engine − SDK);
- first divergence at payload offset `0x140F`, last at `0x3FFE`;
- 1,004 of the differing offsets are adjacent to the next, i.e. runs, not noise.

The engine's tiles exist in **no bank** of the SDK's atlas
(`build/gfxdiag/probe_atlas_search.py`: 212/212 "not in any of 187 banks"), which
rules out a wrong bank or a wrong tile index and leaves the decode.

### 3.7 The candidate rule reproduces the engine exactly - CONFIRMED_RUNTIME

`build/gfxdiag/probe_literal_base.py` re-runs the identical grammar with one
change (returning to 8-bit literals clears the literal base):

| Bank | Referenced tiles | shipping == engine | base-reset == engine |
| --- | --- | --- | --- |
| 140 | 256 | True | True |
| 141 | 256 | **False** | **True** |

### 3.8 Cross-validation against the two runtime-validated maps - CONFIRMED_RUNTIME

`build/gfxdiag/probe_cross_validate.py` rebuilds maps 39 and 40 both ways and
compares against the retained MAP-VIS-001 VRAM captures:

| Map | Decode | differing tiles outside animation ranges | inside them |
| --- | --- | --- | --- |
| 39 | shipping | 0 | 32 of 70 |
| 39 | corrected | **0** | **0 of 70** |
| 40 | shipping | 0 | 5 of 38 |
| 40 | corrected | **0** | **0 of 38** |

The corrected rule reproduces **every** tile of both validated captures. The
"post-load animated mutations" MAP-VIS-002 had to normalize were partly this
decode error, not animation.

Chunks are unaffected: **0 / 3,745** chunk containers change under the rule.

### 3.9 End-to-end: the corrected decode reaches the engine's own ceiling - CONFIRMED_RUNTIME

`build/gfxdiag/probe_final_proof.py`, against the emulator's own framebuffer at
the scroll that best fits, with the engine's own planes held fixed:

| Character block fed to the render | Agreement with the engine's screen | Differing pixels |
| --- | --- | --- |
| engine's own VRAM (ceiling) | 0.9390 | 2,343 / 38,400 |
| SDK, shipping decode | 0.8407 | 6,117 / 38,400 |
| SDK, corrected decode | **0.9390** | **2,343 / 38,400** |

The corrected decode is *indistinguishable* from the engine's own bytes on
screen. The residual 6.1 % is the sprite layer (Goku, HUD, item icons, the plane
sprites) and the `BLDCNT` alpha blend on BG0 (`BLDCNT 0x1041`, `BLDALPHA 0x000C`)
 - OBJ and display effects the background renderer does not claim to draw.

Artifacts (ignored): `engine_display_map36_1.png`, `proof_map36_1.png`,
`display_compare_map36_1.png` under `build/gfxdiag/`.

### 3.10 Blast radius per map - CONFIRMED_ROM

`build/gfxdiag/probe_permap_numbers.py`: map 36 **212/859** tiles change, map 39
32/896, map 40 5/896, map 102 128/896, map 179 112/610. 369 of 452 maps change.

## 4. Eliminated hypotheses

| Hypothesis | Verdict | Evidence |
| --- | --- | --- |
| The compiled library is stale | **Eliminated** | 3.1: 0/452 maps differ from the tree |
| Tile/index decode (selector ordinal → destination tile) | **Eliminated as the fault; confirmed correct** | disassembly `0x08009C18..0x08009C82`: a 32-bit VRAM cursor from `0x06000000`, `+0x40` per selector, no modulo; `sel[i] = (raw[i] + sel[i-1] + 1) & 0xFFFF` |
| Graphics-bank/base selection | **Eliminated** | live root `+0x4C` = `0x08179764` = the SDK's table; every differing tile was searched against all 187 banks and found in none |
| Bit depth (4bpp vs 8bpp) | **Eliminated** | every rendered layer has `entry_high_nibble_nonzero_count == 0`; live BG0CNT..BG3CNT are all 8bpp; the engine's copy moves exactly `0x40` bytes per tile |
| 4bpp palette-bank selection | **Eliminated** | same; `BGxCNT` colour mode is 1 (8bpp) for all four BGs at runtime |
| Palette / palette-bank selection | **Eliminated** | live palette **256/256** equals ROM `0x080701B0`; the palette address has exactly one 32-bit code reference image-wide |
| H/V flip | **Eliminated** | entries match the engine bit-for-bit including bits 10 and 11 (3.3) |
| Chunk/metatile composition and layout | **Eliminated** | 3.3: 0/1024 mismatch on BG0/BG1, and every BG2/BG3 mismatch is a live-zero cell |
| Layer stacking / priority | **Eliminated** | live priorities equal the root addends exactly (3.4) |
| Per-layer tile-base shift | **Eliminated** | the dominant record's unknown header words are `0x400` constants or layer ordinals, never bases |
| Multiple map-root "variations" | **Eliminated** | 452/452 maps have exactly one descriptor-shaped word at `+0x2C`'s target |
| A second tilemap layer the SDK ignores (`+0x34`/`+0x38`) | **Eliminated** | both are `0x2000`-byte sparse planes (map 36's `+0x38` is 8,192 bytes of `0xFF`), not tile graphics; the engine decompresses them into the scene object, and no rendered pixel depends on them |
| Runtime-only BG the root does not name | **Eliminated** | map 39's live BG0 plane at the capture is empty (1024/1024 zero), so the engine enables a BG that draws nothing |
| Asset bounds / short container | **Eliminated** | bank 186 declares `0x3C40` (241 tiles) honestly and only map 0 uses it; every map's referenced ordinals are within 896 tiles, the char area's own size (`0xE000 / 64`) |

## 5. The remaining unexplained observation

Map 102 (West City) leaves **29.4 %** of its *reachable* rectangle unpainted
(reachable = root extent + viewport = 881x721 of a 1280x1024 canvas; measured
over rendered layer indices, not artifact alpha). The corrected decode moves this
by 0.0004, so **it is not the decode defect**.

Two candidate causes remain, and neither is established:

1. the layers really are empty there and the engine shows the backdrop (which is
   palette entry 0, black) - the game screen for map 36 shows the same backdrop
   convention at the map's edges;
2. the composite places every layer origin-aligned, while the engine gives each
   BG its own scroll. The capture shows different window origins per BG
   (BG0 (0,23), BG1 (0,28), BG2/BG3 (0,32)), and `BGxHOFS`/`BGxVOFS` are
   **write-only** registers that mGBA returns 1/1/1/1 for, so the display offsets
   could not be read from the register file.

This does **not** block the proven cause and it is not claimed as a cause. The
runtime method that settled section 3 is directly reusable on map 102.

## 6. The "jigsaw" question

Both readings are now answered, and they are different things:

- **The bank sheets are raw hardware-tile storage.** A bank container is
  16,384 decoded bytes = 256 tiles of 8x8, 8bpp, 64 bytes each, in storage order.
  There is no metatile, no chunk grid and no composition rule inside a bank; the
  sheet's jigsaw appearance is the storage order of the art, not a format layer.
- **The map's composition layer is the chunk** - a native 32x32 regular-BG
  screen-entry plane, named by one 4-byte pointer per grid cell, laid out in
  row-major grid order (`y * width + x`) in the layer record's window at `+0x18`.
  It is not a Webfoot metatile format: the entries are native GBA entries with
  tile index (bits 0-9), H flip (10), V flip (11) and palette bits (12-15), and at
  8bpp the palette bits are unused and zero everywhere in the canonical corpus.
- **The "jigsaw" appearance in the rendered maps is neither of those.** It is the
  decode defect of section 1: tiles with correct shapes and wrong palette indices
  read as tiles borrowed from another set.

## 7. Native-GBA hypotheses, tested explicitly

- Runtime screen entries are native: **CONFIRMED_RUNTIME** - live words equal the
  ROM words including flip bits, and `palette_bank` is zero at 8bpp.
- 4bpp with a palette bank: **excluded for the canonical corpus** - no rendered
  entry in any of the 1,808 layers sets a high nibble, and all four live `BGxCNT`
  colour-mode bits are 1.
- The engine's text-BG entry layout is the platform's, not a Webfoot variant:
  **CONFIRMED_RUNTIME** by the bit-for-bit entry agreement.

## 8. Confidence and limitations

- The root cause is **CONFIRMED_RUNTIME / LEVEL 4**: an independent decode rule
  reproduces 16,384 bytes of the engine's own character memory exactly, and two
  maps with retained runtime captures at **0 differing tiles**, and the visible
  frame at the engine's own ceiling.
- **Limitation, stated plainly.** The map-36 capture comes from a savestate saved
  in that area, so it is the engine's *restored assembly*, not a fresh area build;
  the observer's departure gate was additionally fooled by the state-load
  transient (a one-frame index change), which is a defect in the observer, not in
  the evidence. What makes the capture usable as the engine's own bytes is that
  section 3.7's rule reproduces 16,384 of them exactly - a wrong decode cannot do
  that. The corrected rule is *also* validated against the two retained
  leave-and-re-enter captures (maps 39/40), which is the discipline the ticket
  asks for.
- The rule is verified byte-exactly on banks 136/139/140/141 (map 36) and on maps
  39/40's banks. Its effect on the other 73 changing banks is measured by the
  same decoder, not independently runtime-checked; the direction is fixed by the
  four banks that are.
- Maps 102 and 179 are **INFERRED** to carry the same defect (their character
  blocks change by 128/896 and 112/610 tiles under the rule). They were not
  runtime-captured this pass.
- Corrupt-looking regions on map 102 are **UNKNOWN** in cause (section 5) and are
  explicitly not attributed to the decode defect.

## 9. Exact next correction boundary

The smallest evidence-driven correction ticket is:

> **Fix the packed container decoder's literal base across a return to 8-bit
> literals, and re-baseline everything that depends on a decoded container.**

Scope, exactly:

1. `tools/webfoot/formats/webfoot_lz.py::_unpack_stream` - clear `literal_base`
   when `literal_bits` becomes 8. This is the whole code fix.
2. `tools/export/webfoot_strict.py::decode_packed` - the same rule, so the export
   path and the SDK cannot disagree. It already requires the stream's own end
   marker; the two readers must stay byte-identical.
3. Re-baseline the artifacts and pins the change moves: the 369 changed map
   character blocks, the per-map `char_sha256` pins in
   `tests/integration/test_map_render_rom.py`, and any chunk/sprite/tile artifact
   digest derived from a changed bank (chunks are unaffected; the 77 banks feed
   tiles, sprite graphics and the atlas).
4. A regression that cannot silently regress: pin the engine's rule with a
   synthetic packed stream that exercises base-switch-return, and pin one
   ROM-gated end-to-end fact (bank 141's first divergence offset and the maps
   39/40 zero-mismatch property).
5. Re-run the runtime screen comparison of section 3.9 as the acceptance gate.

Explicitly **out of scope** for that ticket: the map-102 unpainted measurement
(section 5), which needs its own runtime capture first, and any compositor work.

**`TILESET-COMPOSITOR-001` remains parked**, and this ticket gives the reason
rather than an opinion: there is nothing in the render chain that a compositor
would fix. The screen entries reproduce the engine byte-for-byte, the palette is
identical, the stacking order is the engine's, and the one defect between the ROM
and the screen is a decoder rule. A compositor becomes worth proposing only if
corrected rendering still disagrees with a runtime capture - which, at the
engine's own 0.9390 ceiling, it currently does not.

## 10. Reproducing this document

Every probe named above is a read-only script under the ignored
`build/gfxdiag/`, and every runtime artifact under the ignored
`build/toolkit031/`. **The probes hardcode `ROOT = <checkout>`,** the
checkout they were written in; a reviewer working from a clone or a ticket
worktree must point that constant at their own tree first (the review of this
ticket ran them from the main checkout for that reason, with the candidate's
`tools/` and `tests/` on the path).

The runtime comparison is carried by `probe_final_proof.py`, which reports the
shipping decode, the corrected decode and the engine's own ceiling from one dump.
An earlier `probe_display_model.py` produced the same A/B numbers but crashes on
the SDK-plane case, and was removed rather than repaired;
`probe_display_compare.py` covers the SDK-plane projection properly.

The candidate was frozen and reviewed in the ticket worktree
`<ticket-worktrees>\map-gfx-diag-001` at
`13e9e11955762dc4f61255e65a8fc9fd85500948`. The main checkout carries the same
content uncommitted, which is this ticket's normal pattern.
