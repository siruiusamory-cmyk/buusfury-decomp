# Buu's Fury map background rendering chain

Evidence document for the canonical Buu's Fury USA image (SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`).
Addresses are GBA ROM addresses; file offset is address minus `0x08000000`.
Claims use **CONFIRMED_ROM**, **CONFIRMED_RUNTIME**, and **INFERRED** exactly as
defined by repository governance.

## 1. Result

MAP-VIS-002 closes the one gap left by MAP-VIS-001:

```text
semantic map
-> MapEntry +0x2C
-> scene descriptor
-> tile-selector + tileset + logical-layer containers
-> ROM-resident assembly
-> complete logical BG layers + static-frame character data
-> global palette
-> pixels
```

`tools/webfoot/map_render.py:550` exposes the production API
`render_map(rom, map_id)`. It takes no VRAM argument. The previous VRAM renderer
remains at `tools/webfoot/map_render.py:476` and
`tools/webfoot/map_render.py:629` only as an independent reference path.

## 2. Map identity and palette (MAP-VIS-001, retained)

| Fact | Value | Evidence |
| --- | --- | --- |
| MapEntry table | `0x0808E2E0`, stride `0x38` | **CONFIRMED_ROM** |
| scene route | MapEntry `+0x2C`, dereference target once | **CONFIRMED_ROM** |
| map 39 descriptor | `0x08294968` | **CONFIRMED_ROM** |
| map 40 descriptor | `0x08293474` | **CONFIRMED_ROM** |
| BG palette | `0x080701B0`, 256 RGB888 entries | **CONFIRMED_ROM** |
| display conversion | channel `c -> (c>>3)` expanded from 5 bits | **CONFIRMED_ROM/RUNTIME** |

The palette is engine-global. Runtime fade is a display effect and is not part
of immutable map data.

## 3. Phase-0 mismatch and rejected simple transforms

The MAP-VIS-001 overlap statement was converted to 64-byte tile mappings before
new runtime work. Exact hashes classified source indices, destination indices,
duplicates, absent source tiles, contiguous runs, and unmatched live tiles.

**OLD CLAIM:** each 0x4000 tileset container might be overlaid or concatenated
into character memory, but only roughly 40–65% appeared to match.

**NEW EVIDENCE:** the load captured at `0x0803D940` groups work by selector bank,
not by destination range. For map 39 the observed groups cover destination
ordinals `[0,1)`, `[1,64)`, `[64,143)`, `[143,172)`, `[172,173)`,
`[173,175)`, `[175,198)`, `[198,199)`, `[199,200)`, `[200,201)`,
`[201,202)`, and `[202,259)` while their ROM sources are twelve independent
0x4000 containers. Static code at `0x08009C62..0x08009C78` selects one tile per
ordinal and advances VRAM by exactly 64 bytes.

**RESOLUTION:** fixed offset, whole-container overlay, concatenation,
interleaving, row/column permutation, tile-index bias, blank suppression, and
container-base placement are rejected. The apparent partial overlaps were the
wrong unit of comparison. The unit is a decoded u16 selector.

## 4. Character-memory assembly

### Selector object

The scene descriptor carries:

| Offset | Meaning | Evidence |
| --- | --- | --- |
| `+0x48` | Webfoot-LZ container of delta-coded u16 tile selectors | **CONFIRMED_ROM/RUNTIME** |
| `+0x4C` | pointer to the tileset-container `u32[]` | **CONFIRMED_ROM** |

Map 39's selector container is `0x08294660` and decodes to `0x206` bytes / 259
selectors. Map 40's is `0x082932F8` and decodes to `0x1DE` bytes / 239
selectors.

The engine decompresses `+0x48` at `0x08009BF2..0x08009BF6`, then prefix-decodes
entries at `0x08009C02..0x08009C12`:

```text
absolute[0] = raw[0]
absolute[i] = (raw[i] + absolute[i-1] + 1) & 0xFFFF
```

For each absolute selector, the high byte selects `descriptor[+0x4C][bank]` and
the low byte selects a 64-byte tile within that decoded 0x4000-byte atlas. Code
`0x08009C4E..0x08009C5A` decompresses each bank once into the 0x4000-byte work
buffer; `0x08009C62..0x08009C78` copies tile `selector & 0xFF` to sequential
destination tile `i` through copy veneer `0x08049138`.

Consequences, all **CONFIRMED_ROM**:

- destination tile index is selector ordinal;
- selector order is preserved;
- repeated selectors produce repeated destination tiles (no deduplication);
- unselected atlas tiles are unused;
- selected blank tiles are copied (no zero suppression);
- multiple atlas containers populate one character region;
- no descriptor-specified destination base or per-map constant participates.

The runtime capture caught decompressor `0x0803D940` with return PC
`0x08009C5E`, ROM container in `r0`, work buffer `0x0202C2A8` in `r1`, and the
sequential VRAM destination/range state in `r4/r5/r6`. This establishes the live
writer family and the pre-VRAM intermediate buffer (**CONFIRMED_RUNTIME**, capture
`20260914-010341-f59fb76a`; private ignored evidence).

### ROM-resident animated tiles

The static selector assembly is followed by descriptor-owned animated-tile
records:

| Descriptor field | Meaning | Evidence |
| --- | --- | --- |
| `+0x0C` | animation-record count | **CONFIRMED_ROM** |
| `+0x10` | animation-record pointer array | **CONFIRMED_ROM** |

Each record is `{u8 frame_count, u8 tile_count, u16 destination_tile,
u32 frame_pointer[frame_count]}`. A frame begins with a u32 duration followed by
a headerless Webfoot bitstream. The relocated IWRAM routine at `0x03000040`,
captured read-only from mGBA 0.11, is instruction-for-instruction the existing
Webfoot grammar with initial literal width 8. Loader `0x08009B12..0x08009B42`
expands one frame and copies `tile_count * 64` bytes to
`0x06000000 + destination_tile*64`.

This is ROM data, not runtime synthesis. In the later MAP-VIS-001 captures,
every reserved animation range matches one decoded ROM frame exactly: map 39's
3-tile record matches frame 1 and its 11-tile record matches every equivalent
odd frame; map 40's 4-tile record matches frame 0 and its 11-tile record matches
frames 2/10/12/14. Production rendering deliberately chooses frame 0.

## 5. Logical layer and screenblock assembly

The four descriptor pointers at `+0x14`, `+0x18`, `+0x1C`, and `+0x20` are BG
layer records. A non-empty proven record has handler `0x08008087`, width and
height in 32x32 chunks at bytes `+0x14/+0x15`, and a row-major u32 container
array at `+0x18`. Every container decodes to `0x800` bytes: 1024 little-endian
regular-BG screen entries. A zero-by-zero record is an absent layer.

**OLD CLAIM:** descriptor `+0x34/+0x38` and `+0x10..+0x20` were described as
screenblock sources, and the residual could have implied another compression or
tilemap transform.

**NEW EVIDENCE:** constructor `0x08007BDE..0x08007C08` multiplies the record's
`+0x14/+0x15` chunk dimensions, reads container pointers at `+0x18 + 4*i`, and
decompresses up to four resident chunks to 0x800-spaced EWRAM buffers. Camera
loader `0x08007C82..0x08007C90` computes chunk index `y * width + x`.
`0x08007D44..0x08007D5C` decompresses a missing selected chunk and copies it to
the chosen resident buffer. Streaming code beginning `0x08007D98` splits rows
at `(coordinate & 0xFF) >> 3` and writes the camera-relative circular hardware
screenblock. Consequently a resident logical cell `(x, y)` is stored at
`(y & 31) * 32 + (x & 31)`. Applying that equation to the retained captures is
exact for all populated screen entries. Capture-specific logical origins are
map 39 BG1 `(54,8)`, BG2 `(62,8)`, BG3 `(70,8)` and map 40 BG0 `(0,0)`, BG1–3
`(0,9)`; these origins are runtime viewport state and are not production map
constants.

**RESOLUTION:** the ROM objects are complete logical 32x32 chunks in row-major
chunk order. The live 32x32 screenblock is a mutable camera window, not the map
format. BG scroll changes the resident storage/window; it does not reorder ROM
logical cells. The production renderer decompresses every chunk and stitches
rows directly, preserving the entire u16 entry (tile ID, H/V flips, and palette
bits). It does not emulate camera streaming.

The direct single-chunk comparison from the initial investigation was the wrong
coordinate model and is retained here as a rejected diagnostic:

| Map | BG -> selected chunk | exact live entries / 1024 |
| --- | --- | --- |
| 39 | BG1 -> 2; BG2 -> 2; BG3 -> 2 | 792; 915; 858 |
| 40 | BG0 -> 0; BG1 -> 0; BG2 -> 2; BG3 -> 0 | 999; 739; 792; 973 |

Map 39's BG0 record is absent; its live BG0 is runtime-only and is not promoted
to map data. Map 39 logical layer grids are 3x2, 3x2, and 4x2 chunks for BG1–3.
Map 40 uses 1x1 for BG0 and 2x2 for BG1–3.

Under the proven circular coordinate transform, every populated live word
matches the corresponding ROM logical word exactly, including tile number,
H/V flips, and palette bits. Map 39 has zero residual screen entries. Map 40's
only residual is a pinned set of zero/unpopulated live cells: 25 on BG0, 6 on
BG1, 3 on BG2, and the off-window final column (32) on BG3. The comparison test
enumerates those physical cells and fails if any nonzero live entry conflicts
with ROM. The BG0 4x5 cleared rectangle is classified as captured runtime state,
not persistent layout; the immutable ROM renderer correctly retains the logical
cells.

## 6. Reference comparison and retail validation

**OLD CLAIM:** the first oracle test rebuilt both char data and screen entries
from the new ROM assembly before invoking the VRAM renderer. Its pixel equality
was tautological and did not prove the retained capture.

**NEW EVIDENCE:** the replacement test starts with the actual captured VRAM. It
asserts the circular projection against every raw screen word, enumerates the
zero/unpopulated cells above, and pins the exact post-load mutable destination
tile sets (49 tiles for map 39; 38 for map 40). The initial selector writer at
`0x08009C62..0x08009C78` proves the low ranges held the selected ROM tiles at
load; later differences are post-load mutation. Each high animated range is
also required to equal one decoded ROM animation frame exactly. Only those
enumerated screen cells and tile destinations are normalized to static frame
zero. The old VRAM-backed renderer then matches the new logical-entry renderer
exactly for every layer and for the priority-composited pixels on both maps.

**RESOLUTION:** `ROM-only vs VRAM oracle: EXACT` is supported for the static map
structure after the proven circular coordinate transform and the explicitly
enumerated runtime state are normalized. Raw later-frame VRAM is expected to
differ; it is not used by production rendering.

Read-only visual inspection of generated ROM-only outputs confirmed:

- map 39: the continuous forest, branching dirt path, tree-stump landmarks,
  flowers, layer transparency, and path-border geometry;
- map 40: the forked forest trail, both white pillars, trees, flowers, correct
  palette, and foreground/background occlusion.

No per-map branch or constant exists in production code. Unsupported layer
handlers, malformed dimensions, missing tile coverage, invalid selectors, and
out-of-range entries raise `UnsupportedMapAssemblyVariant`.

Measured uncached renders with the production SHA-256 gate were 1.03 s (map 39)
and 0.53 s (map 40). Each selector/layout container is decoded once per render and
atlas banks are cached within the assembly; there is no full-ROM scan and no
per-cell decompression.

## 7. Proven display interpretation (MAP-VIS-001, retained)

Retail runtime uses Mode 0, four regular tiled BGs, 8bpp, shared char base 0,
and screen bases 28–31. A 16-bit entry is tile index bits 0–9, H flip bit 10, V
flip bit 11, and palette bank bits 12–15 (ignored by 8bpp). Hardware priority is
descriptor bytes `+0x04..+0x07`; lower priority number is above higher, with
lower BG number winning ties.

Runtime fade and the selected animation phase remain intentional display-time
effects. They do not require a VRAM capture for production rendering.
