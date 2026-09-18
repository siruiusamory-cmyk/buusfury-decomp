# Asset export (ASSET-EXPORT-001)

`tools/export/` builds a complete local Buu's Fury resource library from the
canonical ROM, plus a separate audit directory for verification. The library is
resource output: PNG, JSON, CSV and nothing else.

## Running it

```text
python -m tools.export.buu_resource_export ^
  --rom "roms/Dragon Ball Z - Buu's Fury (U).gba" ^
  --output "D:\BuuFury_Resources"
```

| Option | Effect |
| --- | --- |
| *(none)* / `--all` | export the map, tile and sprite sides |
| `--maps` | map layers, composites and `metadata/maps.json` |
| `--tiles` | bank sheets, individual tiles, chunks |
| `--sprites` | animations, directional frames, frames, sprite graphics |
| `--audit-only` | analyse and write the audit directory, write no resources |
| `--force` | write into a non-empty export root |
| `--audit <dir>` | override the audit root (default `<OUTPUT>_Audit`) |
| `--compare <root>` | diff an earlier export tree against this run |

The canonical ROM is required and identity-checked by SHA-256 before and after
the run. It is never written, copied into the output, or referenced from inside
the library.

The output root must **not** resolve inside a git work tree. The exporter looks
for a usable `.git` (a directory containing `HEAD`, or a work-tree `.git` file)
in the output path and every ancestor, and refuses if it finds one. That is a
hard refusal rather than a `.gitignore` entry: an ignore rule protects one
checkout, a refusal protects every one. Put the library beside the checkout, not
inside it.

## Output layout

```text
<EXPORT_ROOT>/
  maps/map_039_grand_kai_s_planet/{map.json,composite.png,layer_0.png,...}
  tiles/banks/bank_000/{sheet.png,tiles/tile_0000.png,...}
  tiles/chunks/chunk_000000.png
  sprites/sprite_028_babidi/animations/animation_00/
      frame_000/direction_0.png ... sheet.png
  sprite_graphics/graphic_000000.png
  palettes/palette_000.png ... palette_001.json
  metadata/{maps,tile_banks,chunks,sprites,animations,frames,sprite_graphics,
            aliases,names}.json
```

Naming is numeric and fixed-width, and derives only from canonical identity:
`map_039`, `sprite_028`, `animation_00`, `frame_003`, `direction_0`, `bank_017`,
`tile_0042`, `chunk_001827`, `graphic_000000`. Where the accepted ROM data carries
a genuine text string for the object, the sanitized string is appended after the
numeric id - `map_039_grand_kai_s_planet`, `sprite_028_babidi` - with lowercasing,
one underscore per run of other characters, and a 48-character cap. The numeric id
stays first and stays canonical, so a renamed or missing string can never make a
path ambiguous. No direction and no animation slot is named, because nothing in
the accepted data names them.

Across the corpus, 429 of the 452 maps carry a ROM text string (69 distinct
strings, because neighbouring maps share a place name) and 198 of the 297 sprite
definitions are named by an appearance definition (147 distinct strings; 25
sprites are reached by more than one appearance and 8 of those disagree on the
name, in which case the directory uses the lowest appearance index and every
alternative is listed in `metadata/names.json`).

Every layer, frame, tile and chunk image keeps index 0 transparent, and the alpha
channel is written explicitly. A **composite** is flattened instead: the display
backdrop - palette entry 0 of the background palette - fills every pixel no layer
painted, so a composite is the faithful view of the screen rather than an image
full of holes. Each map's `composite_unpainted_pixels` records how many pixels
that affects. Nothing is scaled, sharpened, padded for visibility, labelled or
overlaid.

## The audit directory

`<EXPORT_ROOT>_Audit` holds machine-readable verification output and is not part
of the resource library:

| File | Contents |
| --- | --- |
| `manifest.json` | tool and zlib versions, ROM digest, roots, options, counts |
| `counts.json` | every accepted population beside its measurement and an `accounted` flag |
| `hashes.csv` | `relative_path,bytes,sha256` for every artifact |
| `failures.json` | every structural failure, as `kind` / `population` / `identity` / `detail` |
| `references.json` | chunk to maps, layers by classification, palettes, bank containers, null chunk cells |
| `duplicate_groups.json` | artifacts sharing identical bytes, grouped by digest |

`metadata/names.json` is the numeric-identity to ROM-text index: every map's text
relationship and directory, and every sprite definition's appearance-derived
names, descriptions, portrait and stat indices. A sprite reached by several
appearance definitions carries several names; the directory uses the lowest
appearance index and all alternatives are listed there.

The palette strips (`palettes/palette_000.png`, `palette_001.png`) are opaque on
purpose: they are a view of the palette values, so suppressing entry 0 would hide
an entry rather than show its colour. Both palettes have entries 0 and 1 equal to
black, so only the alpha channel of a *layer* image distinguishes "entry 0,
transparent" from "entry 1, opaque black".

The exporter exits non-zero when a gate is unaccounted, a failure was recorded,
or a prose field or prose file reached the library.

## Determinism

Every path is a pure function of numeric identity; every PNG uses filter 0 and a
fixed deflate level with no timestamp chunk; every JSON document is written with
sorted keys and LF endings. Two runs against the same ROM produce the same
layout, filenames, pixel data, metadata values and hashes. To check a fresh run
against an earlier one:

```text
python -m tools.export.buu_resource_export ^
  --rom "roms/Dragon Ball Z - Buu's Fury (U).gba" ^
  --output "D:\BuuFury_Resources_Second" ^
  --compare "D:\BuuFury_Resources"
```

`--compare` hashes every file in the given earlier root and compares it against
**this run's** `<audit>/hashes.csv`, reporting missing, extra and differing
artifacts.

## What is exported, and what is withheld

The exporter walks the accepted post-LOGX graphs and never substitutes a
heuristic scan for them. `GFXSCAN`-style candidates are not enumerated and no
residual container is exported.

* **Maps.** All 452 `MapEntry` records get a directory, a `map.json` record and an
  entry in `metadata/maps.json`; a map whose four slots are all non-graphical still
  gets all three, so no identity is ever missing from the inventory. Their four
  root slots are each classified by the `+0x00` Thumb handler entry, and the
  layer installer confirms the calling convention: the constructor is reached by
  branching through that word with the slot index and the record pointer.
  * `0x08008087` (`dominant`) - the accepted chunk-grid form, rendered.
  * `0x08007A41` (`absent_placeholder`) - the shared zero-dimension record an
    unused slot points at; it draws nothing.
  * `0x0800897B` (`non_graphical`) - constructor `0x0800897A` allocates a
    twelve-byte marker holding only a type word, the slot byte and the record
    pointer. It performs no decompression, no copy and no background-register
    write, so the slot draws nothing and is recorded as `not_graphical`.
  * `0x08007B63` (`static_graphical_screenblock`) - constructor `0x08007A60`
    decompresses `record + 0x04` into a 0x800-byte buffer. That payload is 1024
    little-endian screen entries, the same 32x32 form a dominant chunk carries,
    so the layer renders as a 256x256 screen-entry plane through the existing
    renderer. One canonical record (map 19, slot 1) and it renders.
  * `0x080088BD` (`static_graphical_assembly_unresolved`) - constructor
    `0x080080C0` programs `DISPCNT` and the background control registers and
    streams `record + 4` x `record + 5` containers of 0x400 decoded bytes through
    a nine-slot resident cache. The layer is graphical, but the pixel arrangement
    of a 0x400-byte container is not established, so it is recorded rather than
    guessed into an image. One canonical record (map 19, slot 2).
  A composite is withheld only when a slot is graphical and cannot be assembled -
  never because a handler is unknown. After the classification that is 450
  composites produced and 2 withheld: map 19 (one slot is graphical but
  unassembled) and map 8, whose four slots are all non-graphical so there is no
  graphical layer to compose. The other 28 previously withheld maps compose, and
  map 19's screenblock layer is still exported as `layer_1.png`.
  A null chunk pointer inside a dominant layer contributes screen entry 0, the
  value the engine's own occupancy test treats as unoccupied, so nothing is drawn
  there. The accepted record set has an internal null in 117 of the 1,420 dominant
  layer records, across 86 maps, occupying 156 of the 4,274 grid cells - exactly
  the accepted `4274 = 156 null + 4118 non-null` arithmetic. What an in-game null
  cell displays is an open question: the constructor skips it while the streaming
  path substitutes the default container `0x08070808`. That container is measured
  to be a stored container declaring zero bytes, so the substitution carries no
  data either - but whether the destination would retain stale bytes is not
  something the ROM image can show, so the counts are recorded in
  `references.json` rather than the question being called settled.
  Rendering is cross-validated against the project's own accepted renderer: on
  every one of the 342 maps that renderer can render, the exporter's layer images
  and composites are pixel-identical to it. It refuses the other 110; measured by
  first failure those are 85 with a null chunk cell, 20 with a partial-zero
  record, 4 with a non-dominant handler record, and 1 (map 0) whose selector
  stream reaches the `0x3C40`-declaring bank. Relaxing exactly those two
  fail-closed refusals in a scratch copy of the renderer - skip a null cell, honour
  a bank's declared size - makes it agree with the exporter on all 422 of the maps
  that carry only dominant layers, so the only place the two differ is the set of
  maps the renderer declines.
* **Tiles.** All 187 bank entries are exported at their own declared size: 186
  declare `0x4000` and entry 186 declares `0x3C40`. Entry 186 is used by a
  canonical selector stream (map 0), so its size must not be assumed - and after
  that map's selectors are decoded, the largest tile ordinal it names is 240,
  inside the 241 tiles the declaration covers. A screen entry's bits 10 and 11 are
  applied as the platform's horizontal and vertical flip selectors when a chunk or
  layer is rendered; they are never baked into the exported tile resources, whose
  identity follows the underlying tile.
* **Chunks.** All 3,745 distinct dominant chunk containers are exported as
  256x256 images, rendered against the lowest-index map that references them.
  Every reference is recorded, and any chunk whose pixels differ between
  referencing maps carries a `distinct_render_variant_count`.
* **Sprites.** The animation array is walked at its accepted count bound
  (`definition + 0x00`), never to the next structure and never over a fixed
  23-slot table. Null slots produce no image. All 7,390 structured graphics
  containers are exported from the underlying resource, unflipped.
* **Frames.** A frame is assembled onto its own stored bounding box, with pieces
  placed at `piece offset - frame minimum` and the stored horizontal flip applied.
  Multipart frames are assembled piece by piece.

Nothing here repairs the shipping parsers. The known stale assumptions
inventoried in `docs/research/LOGX_SYNTHESIS.md` §11 are still present in
`tools/webfoot/formats/sprite_graphics.py` and `tools/webfoot/graphics.py`, and
`tools/webfoot/formats/webfoot_lz.py` still clips an over-long final match. This
package implements the accepted schema on the export side instead, with its own
strict container reader (`tools/export/webfoot_strict.py`) that refuses to clip
and, on the export path, also requires each packed stream's own end marker to
fall at its declared size. Repairing the shared parsers is the `FIX-*` queue in
`docs/research/POST_LOGX_IMPLEMENTATION_ROADMAP.md`.

## Tests

```text
python -m pytest tests/unit/test_asset_export_*.py
LOGX_CANONICAL_ROM=roms/Dragon\ Ball\ Z\ -\ Buu\'s\ Fury\ (U).gba \
  python -m pytest tests/integration/test_asset_export_rom.py
```

The unit tests need no ROM. The integration module skips cleanly when the
canonical image is absent and never writes to it. No decoded asset is committed
as a fixture: the expectations are counts, addresses, indices, dimensions and
digests over decoded pixels.
