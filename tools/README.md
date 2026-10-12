# Tool index: which tool already reads this format

Read this before writing a decoder. It exists because a session drafted the next step "reverse engineer the
codec" for a container family the repository already decoded and had validated on 7,390 of 7,390 members,
because nothing in the tree said which tool owned that format. The cost was a delegation, a blocked census
artifact and a committed result that said "BLOCKED before the measurement".

## How to use it

1. Search this file for the format's name, its header size, or the kind/opcode values you can see in the
   bytes.
2. Open the reader named here. It is the authority for that format's bytes, and its docstring states the
   evidence behind the reading.
3. If nothing here names the format, it genuinely needs a reader. New readers belong in
   `tools/webfoot/formats/` when they are pure codecs over `bytes`, or in `tools/research/` when they are
   probes over a whole image - not inside a one-off census script.

## Container and codec formats

| Format | What identifies it in the bytes | Reader |
| --- | --- | --- |
| Webfoot packed container | 8-byte header: `u32 kind` (0 stored, 1 and 2 packed) then `u32 declared_size`; bits are consumed most-significant-first from little-endian 32-bit words | `tools/webfoot/formats/webfoot_lz.py` |
| Actor sprite graphics | tiles, then the object palette, then 12-byte piece records, an 8-byte frame header and the animation table | `tools/webfoot/formats/sprite_graphics.py` |
| Map entry records | 452 records of `0x38` bytes at file `0x8E2E0` | `tools/webfoot/formats/map_entry.py` |
| Placements (factory-led) | a factory word per record, three families, variable length | `tools/webfoot/formats/map_placements.py` |
| Map-linked slot arrays | 8-byte slots reached from a map entry | `tools/webfoot/formats/map_slots.py` |
| Map transitions | selector-1-root connection records | `tools/webfoot/formats/map_transitions.py` |
| Placement links | physical bindings for verified placement descriptors and VM dispatch | `tools/webfoot/formats/placement_links.py` |
| Map graphics | the accepted map/graphics binary concepts, read in one place | `tools/webfoot/formats/map_graphics.py` |
| Background tilemap | GBA Mode 0 regular tiled background: 16-bit screen entries and screenblocks | `tools/webfoot/formats/bg_tilemap.py` |
| Stat tables | the static enemy and character stat records | `tools/webfoot/formats/stat_tables.py` |
| Text pool and pointer table | UTF-16LE strings behind a `u16` code-to-offset table and a pointer table | `tools/webfoot/formats/text_tables.py` |
| ASCII text pool | NUL-terminated strings and their pointer table | `tools/webfoot/formats/ascii_text_tables.py` |
| Script VM bytecode | the event VM's bounded instruction stream, decoded to a control-flow IR | `tools/webfoot/formats/script_vm.py` |
| Indexed PNG | colour type 3, one palette index per byte, `tRNS` for transparency | `tools/webfoot/formats/indexed_png.py` |
| Truecolour PNG | colour type 2 or 6, read for captures and authored sheets | `tools/webfoot/formats/rgb_png.py` |
| RGBA PNG (writer) | colour type 6, deterministic, used by the exporter and by the crops in `tools/research/compare_intent.py` | `tools/export/png.py` |
| BPS patch | the `BPS1` magic and its variable-width fields | `tools/webfoot/formats/bps.py` |

The reader column is checked by `tests/unit/test_tools_readme.py`: every path here must exist, and every
module in `tools/webfoot/formats/` must be named, so this table cannot rot while the code moves.

## Research tools built on those codecs

| Tool | Input | What it answers |
| --- | --- | --- |
| `tools/research/thumb_disasm.py` | an image | Thumb and ARM disassembly, and the authoritative `BL`/`BLX` caller census |
| `tools/research/exact_search.py` | a state space | bitmasks, Gosper submask iteration, and an exhaustive count with a witness; a partial walk cannot be quoted as an impossibility |
| `tools/research/decode_cache.py` | an image plus offsets | the same decoded containers without decoding them again, cached under `build/cache/` |
| `tools/research/oam_sprites.py` | a run directory with `oam.bin`, `palette.bin`, `vram.bin` | the sprites the OAM says are on screen, as an indexed PNG, plus the palette banks they paint |
| `tools/research/compare_intent.py` | an image, a sprite/frame and a capture PNG | intent against screen: differing, missing and extra pixel counts, the union's bounding box, and both crops |
| `tools/research/definition_copy.py` | an image plus sprite ids | a definition copy that fills every animation slot the target's own definition needs |
| `tools/research/free_space_audit.py` | an image | which byte ranges are candidates for reuse, and why a candidate is not a declaration |
| `tools/research/capacity_model.py` | an image | the space accounting and the margin curve behind it |

## Runtime capture

mGBA evidence is governed by `docs/skills/mgba-runtime.md`: every run goes through a tracked launcher, the
observer is read-only and allowlisted in `tools/runtime/inject_mgba_lua.ps1`, and a silent channel is never a
negative. `tools/runtime/mapvis001_vram_dump.lua` is the read-only dump the OAM/PNG reader consumes: it
writes `vram.bin`, `palette.bin` and `oam.bin` into the run directory.
