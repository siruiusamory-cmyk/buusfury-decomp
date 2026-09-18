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
  maps/map_000/{composite.png,layer_0.png,...}
  tiles/banks/bank_000/{sheet.png,tiles/tile_0000.png,...}
  tiles/chunks/chunk_000000.png
  sprites/sprite_010/animations/animation_00/
      frame_000/direction_0.png ... sheet.png
  sprite_graphics/graphic_000000.png
  palettes/palette_000.png ... palette_001.json
  metadata/{maps,tile_banks,chunks,sprites,animations,frames,sprite_graphics,aliases}.json
```

Naming is numeric and fixed-width, and derives only from canonical identity:
`map_000`, `sprite_010`, `animation_00`, `frame_003`, `direction_0`, `bank_017`,
`tile_0042`, `chunk_001827`, `graphic_000000`. No direction, animation slot, map,
bank or tile is given a semantic name, because the accepted work establishes
occupancy and ordering rather than semantics. ROM-derived strings appear only as
*data*, in `metadata/aliases.json` and in each map's `rom_text` field.

Index 0 is transparent in every layer, composite, frame, tile and chunk image,
and the alpha channel is written explicitly. Nothing is scaled, sharpened,
padded for visibility, labelled or overlaid.

## The audit directory

`<EXPORT_ROOT>_Audit` holds machine-readable verification output and is not part
of the resource library:

| File | Contents |
| --- | --- |
| `manifest.json` | tool and zlib versions, ROM digest, roots, options, counts |
| `counts.json` | every accepted population beside its measurement and an `accounted` flag |
| `hashes.csv` | `relative_path,bytes,sha256` for every artifact |
| `failures.json` | every structural failure, as `kind` / `population` / `identity` / `detail` |
| `references.json` | chunk to maps, layers by classification, palettes, bank containers |
| `duplicate_groups.json` | artifacts sharing identical bytes, grouped by digest |

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

`--compare` reads the earlier root's `<root>_Audit/hashes.csv` and reports
missing, extra and differing artifacts.

## What is exported, and what is withheld

The exporter walks the accepted post-LOGX graphs and never substitutes a
heuristic scan for them. `GFXSCAN`-style candidates are not enumerated and no
residual container is exported.

* **Maps.** All 452 `MapEntry` records get a directory. Their four root slots are
  each classified by the `+0x00` Thumb handler entry: the dominant chunk-grid
  form (`0x08008087`) is rendered, the shared zero-dimension absent-layer record
  (`0x08007A41`) is recorded as non-graphical, and the three unresolved handlers
  (`0x0800897B`, `0x08007B63`, `0x080088BD`) are recorded as unresolved. A
  composite is produced only when every slot is either rendered or the absent
  placeholder; otherwise it is withheld and the reason is recorded as a status
  value, never silently dropped.
  A null chunk pointer inside a dominant layer contributes no entries. The
  accepted record set has an internal null in 117 of the 1,420 dominant layer
  records, across 86 maps, occupying 156 of the 4,274 grid cells - exactly the
  accepted `4274 = 156 null + 4118 non-null` arithmetic. What such a cell
  displays is an open question: the constructor skips it while the streaming path
  substitutes the default container `0x08070808`. That container is measured to be
  a stored container declaring zero bytes, so the substitution carries no data
  either - the exporter renders the cell as no-data and records the counts in
  `references.json` rather than claiming the question is settled. Whether the
  destination would retain stale bytes is not something the ROM image can show.
  Rendering is cross-validated against the project's own accepted renderer: on
  every one of the 342 maps that renderer can also render, the exporter's layer
  images and composites are pixel-identical to it. The other 110 are exactly the
  maps it refuses - null chunk cells, the partial-zero unresolved records, the two
  unresolved singletons, and the one map reaching bank 186.
* **Tiles.** All 187 bank entries are exported at their own declared size, which
  is `0x4000` for 186 of them and `0x3C40` for entry 186 - and entry 186 is used
  by a canonical selector stream, so its size must not be assumed. A screen
  entry's bits 10 and 11 are applied as the platform's horizontal and vertical
  flip selectors when a chunk or layer is rendered; they are never baked into the
  exported tile resources, whose identity follows the underlying tile.
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
