# Buu's Fury map background rendering chain

Evidence document. Every address here was measured against the canonical Buu's
Fury image (SHA-256 `940ad5f0...f059e`), read-only, by static byte-match, Thumb
disassembly, or a read-only runtime capture of live VRAM, and is cross-checked
against the live retail-assembled state of map 40.

Evidence labels follow the project convention: **CONFIRMED_ROM** (measured in the
image), **CONFIRMED_RUNTIME** (measured in a live read-only capture),
**VERIFIED_UPSTREAM** (from a pinned upstream and re-checked), **INFERRED**,
**UNKNOWN**.

File offset = ROM address - `0x08000000`.

---

## 0. Status: what is proven, and the one thing that is not

This document records a **partial** result. The background *representation* and
the path from runtime-resident tile/tilemap data to pixels are proven; the fully
ROM-resident source of the tile-graphics and tilemap bytes is **not yet proven**.

**PROVEN**

* Map identity -> scene descriptor resolution, from ROM (section 2).
* Scene-descriptor relationships (section 3) and the tileset pointer array (section 4).
* Webfoot LZ decompressor identity (section 5).
* Background palette: exact ROM source and RGB888->BGR555 conversion, byte-verified
  against live palette RAM (section 6).
* GBA background interpretation: Mode 0, four regular tiled BGs, 8bpp, direct
  hardware tilemap (not metatiles), screen-entry flip/priority semantics (section 8).
* A neutral software renderer that reproduces the retail map **from live-VRAM
  tile/tilemap bytes** (section 9), validated on two structurally distinct maps.

**NOT YET PROVEN (the one remaining blocker)**

* The exact, general, ROM-resident source and reconstruction path for the tile
  **graphics (charblock)** and **tilemap (screenblock)** bytes. Those bytes are
  currently supplied by a per-map runtime VRAM capture, not derived from the
  immutable ROM. The tileset/tilemap **containers** are located in ROM and
  decompress cleanly, but only ~40-65 % of a container's tiles land in the live
  charblock, at offsets no clean overlay reproduces, so a ROM-only charblock
  cannot yet be assembled (section 7). Until this is solved, there is **no ROM-only map
  renderer**; the renderer is VRAM-backed.

## 1. The chain, top to bottom

```text
map:NNNN (a MapEntry table index)
  -> MapEntry[N] @ 0x0808E2E0 + N*0x38, field +0x2C  (content-stream pointer)   [PROVEN]
    -> *(that pointer) = a scene descriptor                                      [PROVEN]
      -> descriptor fields -> tilemap (screenblock) LZ containers               [containers located, PROVEN]
      -> flat tileset-pointer array @ file 0x00179764 -> tileset LZ containers  [containers located, PROVEN]
      -> engine-global BG palette @ 0x080701B0 (RGB888)                         [PROVEN]
    -> Webfoot LZ decompressor 0x0803D940                                       [PROVEN]
      -> VRAM: charblocks (tile graphics) + screenblocks (tilemaps)            [ROM->VRAM assembly UNKNOWN, see section 7]
      -> palette RAM 0x05000000 (via a fade blend)                             [PROVEN]
  -> hardware composes four regular tiled BG layers -> screen pixels            [PROVEN, from VRAM bytes]
```

Every arrow is CONFIRMED **except** the reconstruction of the VRAM charblock and
screenblocks from the ROM containers (see section 7), which is **UNKNOWN**. That single
gap is why a fully ROM-derived renderer does not yet exist; the software renderer
reproduces the map from VRAM-resident bytes rather than ROM-resident ones.

## 2. Map identity and the scene selector

| Fact | Value | Status |
| --- | --- | --- |
| MapEntry table address | `0x0808E2E0` (file `0x0008E2E0`) | CONFIRMED_ROM |
| Record stride | `0x38` | CONFIRMED_ROM |
| Graphics/scene selector field | MapEntry `+0x2C` (content-stream pointer) | CONFIRMED_ROM |
| MapEntry has a dedicated tileset field | No, `+0x2C` is the only graphics route | CONFIRMED_ROM |

`+0x2C` points into the content stream; the value it points at is the scene
descriptor address. Worked example, map 40 (index `0x28`):

```text
MapEntry[40] @ 0x0808EBA0
  +0x2C -> 0x0807561C
  *(0x0807561C) = 0x08293474   (scene descriptor; the only pointer to it in ROM)
```

Map 39 resolves the same way to descriptor `0x08294968`, a different scene,
proving the resolution is general and not map-40-specific.

## 3. Scene descriptor

The scene descriptor (map 40: `0x08293474`, `0x40` bytes) carries the tilemap
container source pointers at `+0x34`/`+0x38` and tilemap-bank record header
pointers at `+0x10..+0x20`. The four background screenblocks are kind-1 Webfoot
LZ containers, each declaring `0x800` bytes (one 2 KiB screenblock).

| Map 40 screenblock | Container source | Status |
| --- | --- | --- |
| BG0 (screen base 28) | ~`0x0829C7A8` | CONFIRMED_RUNTIME |
| BG1 (screen base 29) | `0x082928DC` | CONFIRMED_RUNTIME (r0 at 0x0803D940) |
| BG2 (screen base 30) | `0x08292F48` | CONFIRMED_RUNTIME |
| BG3 (screen base 31) | `0x08293028` | CONFIRMED_RUNTIME |

## 4. Tileset graphics

| Fact | Value | Status |
| --- | --- | --- |
| Tileset pointer array | file `0x00179764`, 187 ascending u32 ROM pointers | CONFIRMED_ROM |
| Array element | plain u32 pointer (not a record/stride) | CONFIRMED_ROM |
| Each target | kind-1 Webfoot LZ container, declared `0x4000` (256 8bpp tiles) | CONFIRMED_ROM |

The upstream claim of a `+0x4C` per-record stride is **REFUTED**: the array is a
flat `u32[]`; `+0x4C` is simply element index 19.

Map 40 loads (runtime-observed source pointers at the decompressor, in order):
array indices 0, 1, 2, 10, 14, 17, 22, 91, 92, 100, 119, 136. These decompress
into the charblock region; see section 7 for why their placement is not a clean overlay.

## 5. Decompressor

`0x0803D940` is the Webfoot container unpacker: reads kind at `[r2]`
(0 = stored, 1/2 = packed), declared size at `[r2+4]`, payload at `r2+8`. It is
byte-for-byte equivalent to `tools/webfoot/formats/webfoot_lz.py`
(CONFIRMED_ROM by disassembly).

## 6. Background palette

| Fact | Value | Status |
| --- | --- | --- |
| Source | ROM `0x080701B0` (file `0x000701B0`) | CONFIRMED_ROM |
| Size / format | 768 bytes, 256 x RGB888, uncompressed | CONFIRMED_ROM |
| Scope | engine-global (one master BG palette for all maps) | CONFIRMED_RUNTIME |
| Display conversion | per channel `v5 = c >> 3`, expand `v5<<3 \| v5>>2` | CONFIRMED_ROM |
| Match to live palette RAM | 256/256 verbatim at full brightness | CONFIRMED_RUNTIME |

The fade routine `sub_08007074` (store at `0x080070C0`) blends the master palette
toward a target colour per channel:
`out_c = (src_c*(256-level) + target_c*level) >> 11`, output packed BGR555. A
fade-in from black passes target `(0,0,0)`; at full brightness (`level` 0) the
output equals `src >> 3`. A static ROM scan for the palette must apply the
`>> 3` reduction or it will not match.

The palette is not selected per map, the map selects the fade *behaviour* (via
the descriptor's object handlers near `0x0829343C`), not the palette bytes.

## 7. VRAM charblock reconstruction, UNKNOWN

Reconstructing the exact charblock the hardware indexes, purely from the ROM
tileset containers, is **not solved**. Measured against live VRAM (map 40):

| Container | Tiles present in live charblock | Status |
| --- | --- | --- |
| index 2 (`0x08096DA0`) | 103 / 256 | CONFIRMED_RUNTIME |
| index 1 (`0x080959B4`) | 67 / 256 | CONFIRMED_RUNTIME |
| index 0 (`0x080945C0`) | 0 / 256 | CONFIRMED_RUNTIME |

Each container decompresses 256 tiles, but only a fraction land in the live
charblock, at offsets that do not follow a simple cumulative-tile overlay. The
engine's per-tile placement is more granular than a container copy; the exact
rule is UNKNOWN. Consequently a faithful renderer sources the charblock (and
screenblocks) from a captured VRAM state, not from ROM-container reconstruction.

## 8. Display configuration

Measured from live DISPCNT/BGxCNT (map 40):

| Fact | Value | Status |
| --- | --- | --- |
| Video mode | 0 (four regular tiled BGs) | CONFIRMED_RUNTIME |
| Colour depth | 8bpp (256-colour) all layers | CONFIRMED_RUNTIME |
| Layer size | 256x256 (32x32 tiles) | CONFIRMED_RUNTIME |
| Char base | block 0 (all layers) | CONFIRMED_RUNTIME |
| Screen bases | 28 / 29 / 30 / 31 (BG0..3) | CONFIRMED_RUNTIME |

Screen entry (16-bit, GBATEK): bits 0-9 tile index, 10 H-flip, 11 V-flip, 12-15
palette bank (unused at 8bpp). Maps use direct hardware tilemap entries, not a
metatile layer (no metatile indirection observed).

## 9. Rendering fidelity and known omissions

A software renderer over the (VRAM-sourced) charblock/screenblock plus the
ROM-proven palette reproduces the retail map. The charblock/screenblock bytes are
from a runtime capture, not ROM (section 0, section 7). Documented omissions:

* **Runtime fade / brightness**, not applied; rendered at full brightness.
* **Animated tiles**, rendered at their static frame-0 bytes.
* **Runtime sprite/HUD overwrites of shared VRAM**, a live capture taken during
  gameplay carries these; they account for the 1-15% screenblock deltas between a
  mid-gameplay dump and the static map.
