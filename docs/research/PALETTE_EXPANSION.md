# Palette expansion: what is shared, and the routes that are safe

Researched for the owner's question: can a palette be expanded beyond the global 256-entry object palette
without changing other actors? Short answer from the measurements: **there is no spare index space and no
per-actor palette mechanism, so a naive recolour reaches every actor on screen.** The routes below are the
ones the engine can actually support, with their blast radius stated.

Everything here is measured: from the ROM bytes, from decoded disassembly, or from a pixel census over
every actor container, portrait and box surface. Where a lane flagged an assumption rather than a
measurement, it says so.

## 1. How a palette reaches the hardware

- There is **no palette-loading function**. There is a halfword copy primitive: a Thumb veneer
  `0x08049144` whose body lives in IWRAM at `0x030007FC` (ROM copy at `0x087B81A0`), and a memset veneer
  `0x0804912C` (IWRAM `0x030007A8`). Callers inline destination, source and length.
- **28 call sites copy a palette**, every one of them `0x200` bytes = **256 entries**. Source format is raw
  BGR555, little endian, no header.
- **14 scene setups copy the SAME bank, `0x0805652C`, into BOTH `0x05000000` (BG) and `0x05000200`
  (OBJ).** One scene (`0x0802C9C6`) copies a second bank, `0x0805632C`, into BG. The map BG palette for
  fades is a 768-byte RGB888 table at `0x080701B0`, blended in by `0x08007074`.
- One worked site, from bytes: `0x0802C9C6` loads `0x0805632C` into `0x05000000`, then `0x0802C9D4` loads
  `0x0805652C` into `0x05000200`, each `0x200` bytes, through `0x08049144`.
- No DMA and no BIOS call is used for palettes; the four `0x040000D4` literal sites are unrelated.

## 2. What the banks are

| bank | file | entries | bytes | index 0/1 | index 2 |
| --- | --- | --- | --- | --- | --- |
| BG | `0x5632C` | 256 | 512 | `0x0000` | `0xFFFF` white |
| OBJ | `0x5652C` | 256 | 512 | `0x0000` | `0xFFFF` white |

- `0x0805652C` is referenced by exactly **16 word-aligned pointer words** in the image, all in code, and
  loaded by 30 instructions. `0x0805632C` has exactly **one** reference.
- A strict whole-image scan for palette-grade data finds **one** region; the two banks sit inside it.
- No palette in the image is larger than 256 entries, and both banks are 254 of 256 non-zero: there is no
  unused tail inside what a loader copies.

## 3. What is shared (the whole problem)

- **No actor definition carries a palette.** All 297 definitions reachable through `0x086B6BB4` were
  walked over their full extent: **zero** words point anywhere inside either bank.
- **No portrait slot carries a palette.** All 155 live slots of `0x086F393C` are kind-1 containers
  declaring exactly 4096 bytes (64x64 at 8bpp). One portrait is 8x the size of a palette; nothing there is
  even the right shape.
- **Every piece is 8bpp.** Across 22,648 pieces, `attr0` bit 13 is set in **all** of them, so there is no
  palette bank to switch: OAM has no palette field in 256-colour mode, and the piece record does not store
  `attr2`. Two actors on screen **cannot** use different palette entries today.
- **The dialogue portrait is not a separate sprite.** It is decoded into the SAME 160x64 surface as the
  box and text (`0x0800B218`), with **no palette write anywhere on that path**. It draws through whichever
  bank the surface resolves in, and the box ink is index 2 = white in both banks today.

## 4. The pixel census: which indices are actually used

`tools/research/palette_census.py`, over **7,398 actor containers** (deduplicated), 155 portraits and both
box surfaces:

| audience | indices painted | notes |
| --- | --- | --- |
| actor sprites | **252 of 256** | index 0 dominates (5.49M px, the transparent/background value) |
| portraits | 219 | all of them also painted by actors |
| box surfaces | 14 | includes the ink index 2 |

- Indices painted by **nobody at all: 193, 223, 225, 236** - four.
- Indices painted by **both actors and portraits: 219**, so a portrait recolour and an actor recolour
  collide unless the index is one of the four unused ones.

Conclusion: **an index-level recolour is a global change.** With 252 of 256 indices live in actor art
alone, there is no room to give one actor new colours by editing the shared bank.

## 5. Routes, with blast radius

**A. Scene-scoped palette: append a new 256-entry bank, repoint that scene's loader.** The load is an
inline copy with a literal source address, so one scene can be pointed at a bank of its own. Cost: 512
bytes appended plus a literal edit per scene, using the same append-and-repoint machinery the Release 4A
work already uses. Blast radius: **that scene only**, because no other scene references the new bank. This
is the cheapest real expansion and the only one that is safe today.

**B. Duplicate bank with a controlled recolour.** Take the shared bank, change the entries whose consumers
you intend to change, and point ONE scene at the copy. Same mechanism as A but the intent is colour change
rather than room for new entries. Blast radius: scenes repointed. Risk: the ten indices shared by box
surfaces must keep index 2 white, or dialogue text changes colour.

**C. Per-actor palettes via 4bpp conversion.** Give each actor 16-colour art plus its own 16-entry bank, a
new draw path that sets `attr2` palette bits, and bank loads at actor spawn. Cost: every actor's art
container re-authored and a new renderer path; none of it exists today (0 of 22,648 pieces are 4bpp).
Blast radius: everything touched becomes a new build. This is the only route that gives true per-actor
colour, and it is the largest.

**D. Portrait-specific palettes.** Portraits share the box surface's bank, so a portrait can only get its
own colours through C (if the portrait draw path gets a bank) or through A/B by dedicating a scene's bank.
Blast radius: the box surface, hence every dialogue on that screen; index 2 must stay white.

**Recommendation for the owner to pick from:** A or B for a bounded, verifiable colour change; C only if
per-actor palettes are a requirement rather than a convenience.

## 6. What must be verified before any expansion is built

Both static lanes flagged the same assumption, and it is worth stating plainly: the copy's argument order
is **inferred** from register setup (`0x05000000` in `r0`, the ROM pointer in `r1`), because the routine
body lives in IWRAM and cannot be read statically. Agreement between two lanes on that point is the same
assumption twice, not corroboration.

The measurement that settles it: breakpoint after the copy on a live map scene and a live dialogue scene,
dump `0x05000000` and `0x05000200`, and check entry for entry against file `0x5652C` (and against the fade
output of `0x080701B0`). Plus one screenshot showing ink index 2 rendering as white. Nothing static can
answer it, and no expansion should be implemented before it is answered.
