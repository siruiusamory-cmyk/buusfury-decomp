# Project pixel overrides: authoring actor-sprite graphics into a built ROM

GRAPHICS-IMPORT-BOUNDARY-001. This is the evidence record for the first
production graphics-pixel authoring boundary: a project overrides the pixels of
an actor-sprite container, the normal `extract` / edit / `validate` / `build`
path plans it, and the retail engine renders the authored art.

The ticket's question was narrow on purpose. One graphics family, no resizing,
no sprite creation, no editor surface. What follows separates what was measured
from what is inferred, and it records one defect the runtime proof found in
existing production code.

- Canonical ROM SHA-256
  `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`,
  8,388,608 bytes, verified unchanged before and after every run in this record.
- Emulator: mGBA `0.11.0.0`, `build/tools/mgba-dev/...`, version read from the
  binary rather than trusted from its path.

## 1. The selected family

Actor-sprite graphics containers: the compressed payload a frame piece record
names at `+0x08`. It is the only graphics family in this toolkit where all of
the following are already established, which is why it is the safest first
shipping boundary rather than merely the first one available:

| property | status | basis |
| --- | --- | --- |
| decode | CONFIRMED | `sprite_graphics.decode_graphic`; declared size cross-checked against the piece's own extents on all 7,390 containers |
| encode | CONFIRMED | `swizzle_tiles` is an exact inverse of `unswizzle_tiles`, proven over the whole corpus |
| dimensions | CONFIRMED | Object dimensions from the piece's packed OBJ attribute pair, agreeing with the record's stored extents on 11,005 of 11,005 pieces |
| palette | CONFIRMED | One global 256-entry object palette at the profile's declared address; 8bpp indices 0..255, 4bpp 0..15; index 0 transparent |
| payload location | CONFIRMED | `Graphic.packed_size` measured by running the decoder, never trusted from a header length field |
| reference discovery | CONFIRMED | One `ABSOLUTE_ROM_U32_LE` word per distinct piece record, published into the shared graph |
| runtime visibility | CONFIRMED | The player sprite is one of these containers; measured below |

The `graphics_container` anchor kind joined `layout.RELOCATION_ELIGIBLE_KINDS`
and `AllocationKind.GRAPHICS_CONTAINER` joined the single allocation authority.
Those are two separate registrations and both are tested independently.

## 2. Import contract

| property | label | value / basis |
| --- | --- | --- |
| width, height | CONFIRMED | from the piece record; 32x32 and 16x32 in the player set |
| bit depth | CONFIRMED | piece attribute bit 13; 8bpp for every container authored here |
| transparency | CONFIRMED | index 0 |
| palette relationship | CONFIRMED | indices address the one global object palette; the override changes indices, never the palette |
| tile order | CONFIRMED | hardware 8x8 swizzle, exact inverse pair proven over the corpus |
| encoded representation | CONFIRMED | Webfoot container: 8-byte header, kind in the header word, packed bitstream |
| container kind | CONFIRMED | **kind 1 for all 7,390 graphics containers, measured; no other value occurs** |
| original payload extent | CONFIRMED | measured packed extent, the bound an in-place edit may occupy |
| tail semantics | CONFIRMED | the bytes after a re-encoded payload inside its original extent are the old stream's remainder and are left untouched |
| confirmed reference encoding | CONFIRMED | absolute ROM address, 32-bit little-endian, in the piece record at `+0x08` |
| alignment | CONFIRMED | containers are 4-byte aligned |
| relocation alignment | CONFIRMED | 4, matching the source containers |
| allocation policy | CONFIRMED | `Addressability.EXPANDED_PERMITTED`: canonical verified-free first fit, declared expanded storage otherwise |
| complete inbound reference set | **UNKNOWN** | see section 6 |

No write-critical property is left `UNKNOWN`. The one `UNKNOWN` row is the
completeness of the reference set, and the design tolerates it explicitly rather
than assuming it away.

## 3. A defect the runtime proof found in existing code

`webfoot_lz.pack` defaults to container kind 2, which is the form the packed
dialogue path uses. Every actor-sprite graphics container in the canonical image
is **kind 1**, and a container kind is not a label: `webfoot_lz` passes it to
its decoder as the stream's initial literal width, so the retail engine
dispatches on it.

Measured consequence. A derivative was built in which the player's eight
containers were replaced by re-encoded payloads written in place at their
original offsets, packed with the packer's default kind 2. The host codec
round-tripped those payloads exactly. The retail engine drew a garbled,
magenta-mottled sprite. The run is retained at
`build/gfximport001/caseA-kind2-garbled`, and that derivative's SHA-256 is
`C13922B4287CC56A31F027151260B416A0C1CB24FC295D52A427BEA58A747F84`.

The fix is `sprite_graphics.GRAPHICS_CONTAINER_KIND`: a re-encode now takes the
kind the source container actually declares, read from the image, and a graphics
container in any other form is refused at the codec boundary. `encode_graphic_payload`
requires `kind` as a keyword rather than defaulting it, so the packer's default
can no longer be inherited silently.

This is the class of error the ticket's "do not claim graphics relocation from
pointer encoding alone" rule exists to catch, and it applied to the in-place path
too: no runtime proof of a re-encoded graphics container existed before this one.

## 4. Runtime proof

Method. Human-played sessions, driven by the repository's tracked tooling:
`tools/runtime/start_gfximport001_live.ps1` verifies the exact image digest and
size, verifies the emulator's `FileVersion` from the binary, refuses to race an
existing mGBA, copies the private save into an isolated `savegamePath`, launches,
injects the read-only observer `tools/runtime/gfximport001_pixel_proof.lua`
through `tools/runtime/inject_mgba_lua.ps1`, and exits holding no wait loop.
`tools/runtime/finish_gfximport001_session.ps1` re-verifies both the image and the
source save afterwards and refuses to read a silent observer as evidence.

There is deliberately **no savestate**. A savestate restores the VRAM a previous
run assembled, so an image loaded into a settled area can never be shown to have
supplied that area's sprite graphics. Each session boots the image and loads the
saved game, so the area is built from the image under test.

The observer captures every screen whose object-tile region has settled, with the
live map index, rather than guessing which settle event is the gameplay one. It
does no input and writes no emulated state.

What is authored. The player sprite is characters 105 and 107, containers
`graphic:2858` through `graphic:2865`: eight 32x32 8bpp containers with measured
extents 320, 316, 260, 256, 252, 264, 296, 284 bytes. All eight are authored
because the engine streams **one facing's container into VRAM at a time**:
measured, the retail session had container 2861 resident at one settled screen
and 2858 at the next, and the first single-container Case A run stopped on 2859,
which is why its screenshots showed unedited art.

Case A, in place. Authored art: each container's own silhouette flattened to
palette index 3. Re-encoded payloads 136, 136, 136, 136, 136, 132, 140 and 148
bytes, all inside their original extents, therefore eight in-place overwrites and
no allocation and no reference rewrite. Output 8,388,608 bytes, SHA-256
`CA6B8B4145F54BB95AD6F819ED0651C82DD1BAB011B3DF13FA2184E31D0A4509`.

Case B, relocated. Authored art: deterministic high-entropy pixels, seeded from
each container's own content so the eight payloads are genuinely distinct (an
earlier build seeded the generator with a constant, which made all eight payloads
byte-identical and therefore made "each of the eight is resident" a claim about
one blob rather than eight references; that build is retained at
`build/gfximport001/caseB-identical-payloads`). Re-encoded payloads 1,152, 1,152,
1,156, 1,148, 1,152, 1,152, 1,152 and 1,152 bytes, all above every original
extent, so each went through the allocator: eight allocations placed at file
offsets `0x00800000` through `0x00801F80`, i.e. ROM addresses `0x08800000`
onwards, above the original end of the image. Eight relocations, twelve
confirmed consumer words rewritten, output 16,777,216 bytes, SHA-256
`7CB536754D48F110AD7E48F6B1D2CE998B857903C256DC0D618CDF79D00EDEC0`.

Results.

| run | image | what the engine had in object VRAM | what it drew |
| --- | --- | --- | --- |
| retail control | canonical | container 2858's canonical tiles, 16/16 | the retail Goku sprite |
| Case A | `caseA.gba` | authored in-place tiles for three distinct containers, 16/16 each | a solid red silhouette |
| Case B | `caseB.gba` | one relocated payload in full, 16/16 | the authored high-entropy art |

**What the Case B run measured, stated exactly.** At each settled screen from
settle-04 onwards, exactly one of the eight distinct relocated payloads was
present in the engine's object-tile region, in full, and the original containers
were not. That is one rewritten confirmed reference followed into storage above
the original end of the image. It is **not** eight: the engine streams one
facing's container into VRAM at a time, which the retail control run measured
independently (container 2861 resident at one settled screen, 2858 at the next),
so a single settled screen can only ever exhibit the container it is displaying.

The rest of the consumer set is established statically rather than by residency,
and independently of the planner that produced it: all twelve
`references_rewritten` records in `caseB.manifest.json` were read back from
`caseB.gba`, and every one holds the relocated GBA address while the original
payload bytes are still present and unchanged.

How the two derivatives were made, so the digests above are reproducible from
the repository rather than from a scratch directory. Both start from a project
extracted from the canonical image with graphics, edit the eight player PNGs in
place, and run the normal build:

- **Case A.** Each container's decoded indices replaced by `3 if index else 0`,
  re-encoded as an indexed PNG with that same PNG's palette. Every payload then
  fits, so the build takes the in-place path and allocates nothing.
- **Case B.** Each container's decoded indices replaced by a deterministic
  high-entropy sequence seeded from that container's own content, so the eight
  payloads differ:
  `state = 0x12345678 ^ (len(base) << 3) ^ sum(base) ^ (sum(base) * 31)` masked to
  32 bits, then repeated `state = (state * 1103515245 + 12345) mod 2**32` with the
  output byte taken from `(state >> 16) & 0xFF`. Every payload then exceeds its
  original extent, so the build relocates all eight.

Conclusion: **relocation ships.** The retail engine follows a rewritten graphics
reference into allocator-chosen expanded storage and renders the authored pixels,
and the whole confirmed consumer set for the moved payloads is repointed in the
emitted image.

## 5. Shared graphics

A payload named by several frame pieces is relocated **once**. The batch writes
one new payload and rewrites one four-byte word per distinct confirmed consumer,
all to the same address, so a shared payload stays shared rather than becoming a
private copy per consumer. The original payload bytes are left byte-intact, not
retired, so a reference this toolkit did not discover still points at the art it
always pointed at.

In-place edits write only the region the re-encoded payload needs. The remainder
of the original extent, the neighbouring containers, and every unrelated graphic
are byte-identical; the ROM-gated test asserts this globally by requiring the
diff between base and output to be exactly the union of the spans the write
manifest attributes to a named owner.

## 6. Known completeness limit

Relocation rewrites the references the graphics walk actually published: one
`CONFIRMED_REFERENCE` per distinct piece record that names the payload. That set
is **not claimed** to be every word in the image that equals the payload's
address, and no word-aligned scan for one was run. An undiscovered reference is
therefore possible in principle. It is documented as `UNKNOWN` rather than
silently upgraded to complete coverage, and two properties keep it honest:

- the original payload bytes are never freed, so an undiscovered reference still
  reaches intact original art. This is the only protection that operates in
  production, and it is the one the runtime run actually exercised;
- a `CANDIDATE_REFERENCE` reaching a payload withdraws that anchor's
  relocatability, so an unresolved numeric hit refuses the move rather than being
  ignored. This is a guard, not an active protection: the graphics reference
  document publishes only `CONFIRMED_REFERENCE` records, so in production the
  check cannot fire, and it is exercised only by tests that construct a candidate
  deliberately. It is kept because a document produced anywhere else must not be
  able to move a payload with a half-decoded consumer set.

The eight authored containers here have 1, 1, 3, 2, 2, 1, 1 and 1 confirmed
consumers respectively, twelve in total once the shared containers are counted.

## 6a. Other stated limits

- **A PNG palette recolour is not a pixel override.** The authored content is the
  index array; the PNG's own palette is discarded on import, exactly as it is
  discarded on export. An author who edits only the PNG's colours has changed
  nothing the build can see, and the build reports no problem. Palette authoring
  goes through the project's palette overrides, which do reach the image.
- **A settled screen is what is captured.** The observer writes `proof.txt` when
  it reaches its own cap or frame limit; a session the operator closes first
  leaves `liveness.csv` as the record that the instrument was running, which is
  why the finisher reports liveness rather than relying on `proof.txt`.
- **A manifest without digests costs a corpus walk.** A project extracted before
  this boundary carries no `png_sha256`, so its assets are compared against the
  decoded base image instead and every build pays that walk. Re-extracting writes
  the digests and restores the hash-only fast path.

## 7. Determinism

`extract` with no edits, then `build`, reproduces the canonical image
byte-for-byte: no change is planned at all. Two builds of the same edited project
are byte-identical. Extraction writes a baseline digest per asset
(`png_sha256` for the file, `pixels_sha256` for the decoded indices), so an
unchanged asset is decided by hashing a small file rather than by decoding it,
and an editor that re-saves identical art is recognized as a no-op rather than a
change.

What is **not** claimed: the packer is not a competitive encoder, so a re-encoded
payload is a different byte stream from the original even when the pixels are
unchanged. Re-encoding is canonical for this toolkit's encoder, not a
reproduction of the retail stream. The no-op guarantee is about a project with no
edits, where nothing is re-encoded at all.

## 8. Not claimed

- No resizing, no frame or animation topology change, no sprite creation.
- No claim that the reference set is complete (section 6).
- No editor surface; this ticket is backend and project authoring only.
- No claim about any other graphics family: map chunks, tilesets, UI, HUD and
  portraits have their own formats and their own reference graphs.
