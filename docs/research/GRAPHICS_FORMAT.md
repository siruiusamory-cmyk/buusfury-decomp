# Buu's Fury actor sprite graphics

TOOLKIT-010 evidence document. Every count here was measured against the
canonical image `buus_fury_usa_rev0_01c1707f`
(SHA-1 `f1c4b07554d2a3b1ad2f325307051e775ce68087`), read-only, and is asserted by
`tests/integration/test_graphics_rom.py`.

Evidence labels follow the project convention: **CONFIRMED_ROM** (measured here),
**VERIFIED_UPSTREAM** (taken from a pinned upstream and re-checked),
**CONFIRMED_RUNTIME**, **INFERRED**, **UNKNOWN**.

---

## 1. Selected family, and why

**Buu's Fury actor/character sprite graphics.**

Selected because the evidence was already decisive rather than because it was
the most desirable target. Before any new reverse engineering, the audit found:

* `extern/DragonByteZ` (MIT, pinned in `upstreams.lock`) declares explicit
  support for Buu's Fury USA Rev 0 `BG3E` and contains a complete decode path -
  `src/compression.cpp` for the container, `src/sprite_analysis.cpp` for the
  character/animation/frame/piece chain. Being MIT, it is promotable **as code**,
  not merely usable as a lead.
* Its Buu profile independently agrees with ours where they overlap: it records
  `map_entry_table = 0x0008E2E0, count 452`, matching `config/roms.yaml`'s
  `map_entries 0x0808e2e0 / 452` derived separately in TOOLKIT-006.
* The family is bounded, enumerable from a single pointer table, and visually
  verifiable.

Rejected as primary: map tilesets, portraits, UI, fonts and effects. None was
better understood, and §33/§34 of the ticket forbid widening. They remain
**DISCOVERED** - see §11 below.

### Existing local work audited first

`tools/sprites/slice_sheets.py` is the only pre-existing sprite tooling. It
slices **ripped reference sheets** for the Godot remake using a hand-rolled
zlib/struct PNG codec; it never touches a ROM. Nothing in it was duplicated, and
nothing in it was promotable, because it solves a different problem.

Also audited and found to contain no graphics decode path: `AUTO_RE_<local-state-name>`,
`PROJECT_STATE*.md`, `consumer-analysis.md`, `SUBSYSTEM_MAP.md`, the
TOOLKIT-007/008/009 findings, and the `p0xx` runtime probes. `AUTO_RE_<local-state-name>`
does record that EWRAM `0x3DE60..0x3DFA0` is *sprite/animation work* and that
several once-promising "HP" addresses were tile/frame data - useful negative
evidence, and consistent with what this ticket found statically.

Upstreams audited: DragonByteZ, `2genkidev/buusfury`, `Arefu/Legacy`,
`BuusFuryToolkit`, and the three mstan recomp repositories. `BuusFuryToolkit`
ships `.pal` files and PNGs but no format description; `2genkidev/buusfury` is a
build harness; the recomps supply no Buu graphics tables.

---

## 2. The chain

**CONFIRMED_ROM.** Every step measured.

```
character pointer table   0x006B6BDC, 297 entries
  -> character structure  variable size, animation pointers from +0x54
    -> animation record   u32 frame_count, then frame_count * 4 pointers
      -> frame record     u32 piece_count, then 16-byte piece records
        -> piece record   OAM-style attributes + graphics container pointer
          -> container    8-byte header + packed bitstream -> raw 8x8 tiles
```

> **(LOGX-FRAME-001, added later - CORRECTED.)** The last three chain steps read,
> with the stride and the two piece offsets corrected:
>
> ```text
> frame record     u32 piece_count + the frame's own bounding box (8-byte header),
>                  then piece_count * 12-byte piece records
>   piece record   x, y, two pixel extents, a packed OBJ attribute pair, and a
>                  pointer to the graphics container (12 bytes)
>     container    8-byte header + packed bitstream -> raw 8x8 tiles  (unchanged)
> ```

### Character pointer table

* 297 entries, **all 297** valid ROM pointers, **strictly ascending**.
* The last structure (`0x086B6B60`) ends immediately before the table itself, so
  the structures tile one contiguous region `0x006A89D0..0x006B6BDC`.
* 295 of 297 slots reach at least one decodable animation. The other two are
  kept in the numbering but not listed as characters.

### Character structure header

`0x50` bytes before the animation pointer list. Across all 297 structures, ROM
pointers appear at only three header offsets: `+0x00` (4 structures), `+0x04`
(65) and `+0x50` (10). **No header word resolves to a palette**, which is what
first suggested a single global object palette.

`+0x10..+0x4F` is four 16-byte blocks, one per direction slot, each shaped as
two signed 32-bit offsets followed by two small positive values - consistent
with per-direction bounding boxes. **INFERRED**; not decoded, not exposed.

> **Deviation from upstream.** DragonByteZ scans animation pointers from
> `structure + 0x54`. This project declares the same `0x54` in profile data and
> gets the same corpus, but records here that the header is `0x50` bytes and
> that `+0x50` itself holds a ROM pointer in 10 of 297 structures. Whether those
> ten are animations the scan misses is **UNKNOWN** and was not chased, because
> §47 forbids turning this into another archaeology ticket.

> **(LOGX-SPRITE-001, added later.)** The extent question above is now settled and
> this section's two statements about it are superseded, without any figure in this
> document changing. `structure + 0x00` (a `u16` whose low byte is the element
> count) **does** bound the animation-pointer array: five engine sites read it with
> `ldrb`, compare it against the requested index, load `+0x54 + 4*index` and then
> null-test the element. The array is therefore count-bounded and **sparse** -
> 4,070 slots over the 297 structures, 1,721 non-null, 2,349 null - not a fixed
> 23-slot table. Consequently "no header field bounds the list" is no longer
> available as a justification, the header is `0x54` bytes rather than `0x50`, and
> the structures do not strictly tile one contiguous region: 65 of them are
> separated from the next by exactly `0x100` bytes, and each such block is what the
> **following** structure's `+0x04` points at. Every corpus figure in this
> document still reproduces exactly under the count model once this reader's own
> filters are applied (`1017 - 4 = 1013`, `13660 - 64 = 13596`,
> `10964 - 5 = 10959`, `1562` deduplicated); the reader itself
> (`tools/webfoot/graphics.py::_animations_in`) is **deliberately left unchanged**
> here, and the bounded correction is recorded as a deferred follow-up in
> [`../tickets/archive/LOGX-SPRITE-001-COMPLETE.md`](../tickets/archive/LOGX-SPRITE-001-COMPLETE.md).
> Evidence: [`LOGX_SPRITE_PROVENANCE.md`](LOGX_SPRITE_PROVENANCE.md).

### Animation record

`u32 frame_count`, then `frame_count * 4` frame pointers, **direction-major
within each frame**: slot `d` of frame `f` is at flat index `f * 4 + d`.

**13,596 direction slots are populated and 0 are NULL.** The four slots are
numbered, never named - see §10.

> **(LOGX-FRAME-001, added later - CONFIRMED and extended.)** 13,596 is the
> accepted reader's population over the animations it admits
> (`13660 - 64 = 13596`). Over **all** 1,017 unique animation objects the corpus
> holds **13,660 cells, none null**, with exactly **3,415 in each of the four
> direction positions**. The four-position structure is engine-grounded: the
> facing computers at `0x0800A890` and `0x080159B0` write `obj+0x10` from a
> compare of `|dx|` against `|dy|` and the only values they write are `0`, `1`, `2`
> and `3`, with the horizontal pair (`2`/`3`) chosen first and the sign selecting
> within each axis. **The physical screen-space assignment of those four values
> remains UNRESOLVED** and no direction is named here; the decisive structural
> evidence for the two-dimensional table is that all **989** shared frame targets
> are confined to **one frame index** while being reachable from several direction
> indices. Evidence: [`LOGX_FRAME_PROVENANCE.md`](LOGX_FRAME_PROVENANCE.md) §3, §5.

### Frame record

> **(LOGX-FRAME-001, added later - CORRECTED.)** This section's `u32 piece_count`
> then **16-byte** pieces is **REFUTED**. The record is an **8-byte header**
> followed by `piece_count` **12-byte** pieces, and the header's second word is the
> frame's own bounding box. The render loop settles the stride from the engine:
> `0x0800F3C0` computes `r1 = 3*index`, `r1 <<= 2`, then `r7 = frame + r1 + 8`, so
> `r7 = frame + 8 + 12*index`. Under 8+12 **all 11,005 pieces** in the canonical
> image resolve to a graphics container whose declared decoded length equals
> `piece[+0x02] * piece[+0x03]`, and no record's counted extent crosses the next
> known frame start; the 4+16 reading fails the size test on **25** pieces and
> overruns the following record on **16**.
>
> **All 10,959 frames declare exactly one piece is also REFUTED.** The canonical
> corpus contains **21 multi-piece frames**: **19** declare two pieces and **2**
> declare four, for **11,005 piece records over 10,980 distinct frames**. The count
> is a full `u32` read in a loop bounded by itself (`0x0800F3BA`..`0x0800F3F2`).
> The accepted reader never observed one because its 16-byte stride makes
> `_frame_offset` reject every multi-piece frame - measured: it accepts exactly the
> 10,959 single-piece frames and rejects exactly the 21 - which is also the exact
> reason this document's "7,355 unique graphics containers" differs from the
> 7,390 distinct container offsets the corpus actually reaches (the 21 frames reach
> 35 containers the single-piece set does not).
> Evidence: [`LOGX_FRAME_PROVENANCE.md`](LOGX_FRAME_PROVENANCE.md);
> closure: [`../tickets/archive/LOGX-FRAME-001-COMPLETE.md`](../tickets/archive/LOGX-FRAME-001-COMPLETE.md).

> **SUPERSEDED - the paragraph below is the accepted reader's original description,
> retained as history. LOGX-FRAME-001 refutes it; see the correction note above.**

`u32 piece_count`, then that many 16-byte pieces. **All 10,959 distinct frames
in this corpus declare exactly one piece.** The format permits more (the count
is a full word) and the codec handles the general case, but nothing may assume a
frame and its piece are interchangeable.

### Piece record (16 bytes)

> **SUPERSEDED - the heading and table below are the original description, retained
> as history. LOGX-FRAME-001 corrects the record to 12 bytes and moves the two
> offsets; see the correction note immediately below.**

> **(LOGX-FRAME-001, added later - CORRECTED.)** The record is **12 bytes**, not 16,
> and the attribute and graphics fields sit at different offsets. `GRAPHICS_FORMAT.md`'s
> **bit layout below is correct**; only its offset was wrong.

| Offset | Field | Status |
|---|---|---|
| `+0x00` | `x`, signed 8-bit | CONFIRMED_ROM |
| `+0x01` | `y`, signed 8-bit | CONFIRMED_ROM |
| `+0x02` | pixel extent, unsigned 8-bit; the engine halves it to centre an OBJ | CONFIRMED_ROM |
| `+0x03` | pixel extent, unsigned 8-bit; the engine halves it and multiplies the pair to size the composite buffer | CONFIRMED_ROM |
| `+0x04` | **packed GBA OBJ attribute pair**, `(attribute1 << 16) \| attribute0` | CONFIRMED_ROM |
| `+0x08` | pointer to the graphics container | CONFIRMED_ROM |

The attribute word splits into GBA OAM attribute 0 (low half) and attribute 1
(high half):

* shape = attribute0 bits 14-15, size = attribute1 bits 14-15
* 8bpp flag = attribute0 `0x2000`
* horizontal flip = attribute1 `0x1000`, vertical flip = attribute1 `0x2000`

Cross-checked against GBATEK (via the mgba-emu gbatek mirror) and gbadev.net's
OAM chapter, whose shape/size table matches ours entry for entry and whose
attribute-1 bit layout `S S V H X X X I...` puts V at bit 13 and H at bit 12.
Shape 3 is "not used" on this hardware and is refused rather than looked up.

> **(LOGX-FRAME-001, added later.)** The cross-check above is **confirmed and
> strengthened** at the corrected offset. Over all **11,005** canonical pieces the
> attribute pair gives: colour-256 set on **11,005**; shape in `{0, 1, 2}` with the
> reserved shape 3 never used; horizontal flip (attribute-1 bit 12) set on
> **2,848**; vertical flip on **none**; and the shape/size decode reproduces the
> piece's independently stored extents on **11,005 of 11,005**. The engine loads
> the word at `0x0800F1C2` and `0x0800F24C` (`ldr r3,[r0,#4]` / `ldr r6,[r0,#4]`,
> with `r0 = frame + 8 + 12*index`) and merges it into the outgoing OAM word under
> the mask literal `0xFE00FFFF` (pool `0x0800F4B0`). **Stored bits stay separate
> from derived dimensions**: the stored fields are the two extent bytes and the
> attribute word; the pixel width/height are the GBATEK table's *derived* reading
> of shape and size, and they agree.
>
> The horizontal-flip bit is a **stored bit whose rendering effect was not
> observed**. Its correlation is measured, not assumed: in the **2,600 poses where
> directions 2 and 3 differ in attribute-1 bit 12**, the two cells name the **same**
> graphics container in **2,599** cases - which is what a flip of shared art looks
> like. An earlier revision of LOGX-FRAME-001 concluded the opposite from a count
> that compared *frame records* instead of *graphics containers*; Reviewer B
> refuted it and the corrected measurement is the one above.
> Evidence: [`LOGX_FRAME_PROVENANCE.md`](LOGX_FRAME_PROVENANCE.md) §6.5.

---

## 3. Compression

**VERIFIED_UPSTREAM, then CONFIRMED_ROM.**

The container header is two little-endian words:

```
+0x00  kind            0 = stored, 1 and 2 = packed
+0x04  declared_size   decoded length in bytes
```

For a packed stream, `kind` **is** the initial literal width in bits, which is
why both packed kinds share one decoder. Bits are read MSB-first out of
little-endian 32-bit words; byte-wise reading produces plausible garbage at the
first back-reference.

The grammar selects between a literal, a long back-reference with an
Elias-gamma-style length, a re-use of the previous distance, a short 7-bit
distance, a run of raw bytes, and two escapes that retune the distance width and
the literal base/width mid-stream. **A long match's length is biased by its own
distance** (thresholds `0x10000` / `0x37FF` / `0x027F` / `0x007F`) - the one part
of the format not derivable from first principles, and the strongest reason to
promote a verified implementation rather than invent one.

### The structural verification

The decode was **not** taken on trust. The container declares a decoded length;
the piece that points at it independently declares OAM dimensions. Nothing in
the file links the two. They agree on **all 7,355 payloads**:

```
decoded_size == width * height   (8bpp, one byte per pixel)
```

7,355 independent agreements is what moved this from VERIFIED_UPSTREAM to
CONFIRMED_ROM. All 7,355 containers are `kind 1`; **zero** decode failures.

---

## 4. Corpus

| Measure | Value |
|---|---|
| Character table entries | 297 |
| Characters with decodable art | 295 |
| Unique animation records | 1,013 |
| Animation references (with duplicates) | 1,562 |
| Animations shared by more than one character | 333 |
| Direction slots populated / NULL | 13,596 / 0 |
| Unique frame records | 10,959 |
| Frames with exactly one piece | 10,959 (all) |
| Unique graphics containers | 7,355 |
| Total packed graphics bytes | 2,724,940 |
| Total decoded tile bytes | 9,131,136 |
| Compression ratio | ~3.35x |
| Bit depth | 8bpp, uniformly |

> **(LOGX-FRAME-001, added later.)** Two rows above are **reader-scoped**, not
> corpus-wide, and are left in place as the accepted reader's figures:
> **"Frames with exactly one piece: 10,959 (all)"** holds only for the frames the
> 16-byte stride can parse; the canonical image has **11,005 piece records over
> 10,980 distinct frames**, of which **21** declare two or four pieces. And
> **"Unique graphics containers: 7,355"** is exactly the set reached by
> *single-piece* frames; the corpus reaches **7,390** distinct container offsets,
> the extra **35** being what the 21 multi-piece frames reach. Every other row in
> this table is reproduced unchanged by LOGX-FRAME-001 under the corrected layout
> (`1017 - 4 = 1013` unique animation records, `13660 - 64 = 13596` direction
> slots, `10964 - 5 = 10959` frame records). The reader
> (`tools/webfoot/graphics.py`) and `tools/webfoot/formats/sprite_graphics.py`
> are **deliberately left unchanged** by this closeout; the bounded implementation
> follow-up is recorded in
> [`../tickets/archive/LOGX-FRAME-001-COMPLETE.md`](../tickets/archive/LOGX-FRAME-001-COMPLETE.md).

### Sharing

| Consumers | Graphics |
|---|---|
| 1 frame | 4,369 |
| 2 frames | 2,751 |
| 3-10 frames | 235 |

**2,986 of 7,355 graphics are reached by more than one frame; 2,644 are used by
more than one character** (one by eight). Sharing is the normal case, and the
API exposes it: `consumers_of()` and `characters_using()` exist to be read
*before* an edit, not as diagnostics.

> **Correction, recorded rather than silently fixed.**
> **OLD CLAIM.** An early probe reported 13,588 frames and 13,588 pieces.
> **NEW EVIDENCE.** That walk counted a frame once per reaching path, and paths
> outnumber records because animations are shared between characters.
> **RESOLUTION.** There are **10,959 distinct frame records** reached by
> **20,760 traversal paths**. The consumer list is deduplicated by frame offset;
> character membership is tracked separately, because several characters can
> legitimately reach one frame through a shared animation.

---

## 5. Palette

**CONFIRMED_ROM.** One global 256-entry object palette at file offset
`0x0005652C`, declared in profile data.

Evidence that it is the right one:

* **16 inbound word-aligned references** across the image, against **1** for the
  background palette at `0x0005632C`.
* 255 distinct entries; only one word has GBA's unused bit 15 set, against 20 in
  the background palette.
* It reads as a deliberate ramp: black, black, white, red, orange, yellow,
  green, cyan.
* Decoded sprites render correctly with it - see §8.

The palette is carried in **both** representations. `raw` holds the original
little-endian 15-bit words and is what a write emits; `rgb` is derived for
display. This matters: GBA colour is 5 bits per channel, so an 8-bit RGB triple
does not round-trip to a unique word, and a palette edited through RGB alone
would silently re-quantise. Entry order is never sorted or deduplicated - the
index *is* the identity every pixel byte refers to, and two entries may hold the
same colour.

`encode_palette` reproduces the exact 512 source bytes.

---

## 6. Transparency

**CONFIRMED_ROM.** Palette index 0.

Index 0 being transparent for GBA objects is a platform convention, which is
precisely why it was checked rather than assumed. In a decoded 32x32 frame from
character 0, index 0 accounts for **60.2%** of pixels and forms the connected
surround, while the body occupies a tight 114-119 ramp. Rendering with index 0
opaque produces a solid block - the visible signature of a wrong convention.

---

## 7. Editable representation

**Indexed PNG** (colour type 3, 8-bit) plus the ROM palette in `PLTE`, and
`tRNS` marking index 0 transparent. The PNG 1.2 specification defines `tRNS` for
colour type 3 as one alpha byte per palette entry beginning at index 0, which is
exactly the shape this family needs.

Indexed rather than RGBA because **the index is the asset**. Two palette entries
may hold identical colours; a pixel meaning "index 7" is not interchangeable
with one meaning "index 200" even when they render the same. RGBA export would
discard that and force a colour-match on import, which is a quantiser - lossy by
construction and unable to round-trip.

Writes use filter type 0 on every scanline, so the same asset always produces
the same file bytes (diffable project, reproducible build). All five filter
types are supported on read, because an editor round-tripping one of these files
will re-filter it.

**Proven:** export -> import returns identical pixels, dimensions, palette and
transparent index for **all 7,355 assets**.

---

## 8. Visual confirmation

Decoding is confirmed by sight, not only by counts. A contact sheet of seven
characters across all four direction slots renders as unmistakably correct Buu's
Fury sprites: Kid Buu, a Super Saiyan character, an old man in a suit and
glasses, a dog, two vehicles, and a mushroom-hat character - all four directions
coherent, correct colours, clean transparency.

---

## 9. Editing, capacity, and an honest limit

### The capacity fact

**CONFIRMED_ROM.** The 7,355 containers occupy `0x03C34D0..0x06A88AC` with
**zero overlaps** and **4,014 exactly-adjacent pairs** (gap 0); 2,358 more have
only a 4-byte gap. There is **no slack**, and no profile declares free space. A
payload that grows by one byte overwrites the next asset.

Per §22 the pipeline therefore **fails closed**. It does not scan for free space
(a scan cannot distinguish padding from data, and gives different answers on an
already-edited ROM), does not overwrite following assets, and does not relocate.

### What was tried, and what it cost

> **OLD CLAIM.** A modified asset could be rewritten as a *stored* (`kind 0`)
> container, needing no encoder anyone has to trust.
> **NEW EVIDENCE.** Measured across the corpus, the packed form is between
> **1.6% and 78.1%** of raw (median 32.8%). A stored rewrite therefore exceeds
> the original allocation in **every single case: 0 of 7,355 fit.**
> **RESOLUTION.** `build_stored` is retained because the header defines the kind
> and a profile that one day declares free space could use it, but it is not the
> write path.

A real encoder was then written in the ROM's own grammar (`webfoot_lz.pack`),
implementing literals, long matches, previous-distance matches, short matches
and single-byte copies, opening with the escape that widens literals to 8 bits.
It emits **valid** streams - the verified decoder reads every one back exactly.

What it cannot promise is size. It lands at a **median 1.06x** the original
packed size (min 1.00, 195 of 200 within 1.10x), so roughly **one payload in two
hundred** re-encodes small enough to fit its own allocation. An optimal-parse
variant was tried and regressed to 1.60x; greedy with the full token set was
better. Beating Webfoot's own compressor reliably is a compression-research
project, which §48 forbids brute-forcing.

### The supported write path

**Palette editing.** The object palette is uncompressed and fixed at 512 bytes,
so a recolour is an exact in-place two-byte write with no re-encoding and no
capacity question at all - and §21 names recolouring as the preferred safer
edit. `plan_palette_entry` validates the index and refuses any word with bit 15
set; `palette_users` reports every graphic that references the index before the
edit is made.

**Pixel editing** reaches EDIT - decode, modify, re-encode to a valid stream, all
proven - but not WRITE for most assets. That is reported as a measured
limitation, never as unimplemented and never as compressor exactness.

### No-op identity

Unchanged payloads are re-emitted **verbatim**. The whole-ROM no-op rebuild is
byte-identical, 0 changed bytes. This is **payload preservation, not compressor
exactness**, and must never be described as the latter.

---

## 10. What is deliberately not claimed

* **No direction names.** The four slots are numbered. Nothing in the ROM labels
  one "down"; asserting it for API convenience would make a gameplay claim from
  a pointer index.
* **No character names.** The table index is the engine's own key. Aliases like
  "Kid Buu" appear in this document as human orientation and are not structural
  evidence (§36).
* **No animation names.** No sequence is called "walk" or "attack".
* **No `Sprite` class.** The ROM does not collapse payload / tiles / palette /
  piece / frame / animation into one object, so neither does the code.
* **No enemy -> graphics link.** See §12.

---

## 11. Other graphics families

**DISCOVERED** only, deliberately unexplored per §33:

* map tilesets (DragonByteZ records a `level_tileset_table` at `0x00179764`,
  count 187, with a per-level pointer at record `+0x4C` - **VERIFIED_UPSTREAM**,
  not checked here)
* the background palette at `0x0005632C` (1 inbound reference)
* portraits, UI, fonts, effects, title graphics

None was investigated. Whether any shares this container format is **UNKNOWN**.

---

## 12. Enemy / entity linkage

**Searched for, measured absent, and not invented.**

TOOLKIT-009 verified 101 placement types, 95 linked to enemy-stat identities
across 1,284 placements. The obvious next hop was probed directly rather than
merely declared unproven. Across **all 141 enemy records** (`0x1C` stride at
`0x00711274`), examining every word:

| Probe | Result |
|---|---|
| Words pointing into the character-structure region | **0** |
| Words equal to a character-table pointer | **0** |
| Words pointing at any of the 7,355 graphics containers | **0** |
| Words pointing into the character pointer table | **0** |

The enemy record holds **no graphics pointer of any kind**.

An index is equally absent. Of the u16 fields, only `+0x02` (max 3), `+0x06`
(max 1), `+0x0A` (all zero) and `+0x12` (all zero) stay within `0..296` at all -
far too narrow to select among 295 characters. The one field with 141 distinct
values is `+0x08` (18..790), which is the already-known type id, not a sprite
index.

The character pointer table itself has only **2 inbound word-aligned
references** in the whole image (`0x3C0`, `0x1715C`), so whatever selects a
character does so from code rather than from a data table an enemy record
reaches.

**RESOLUTION.** No verified static path exists. Per §47 the pipeline does not
depend on one: graphics assets are independently addressable by stable identity,
and the ticket closes with this link **UNKNOWN** rather than fabricated. A future
ticket's lead is those two inbound references plus runtime tracing of which
character index a spawned enemy resolves to - **not** more static scanning of the
enemy record, which is now exhausted.

---

## 12a. The common reference graph

The verified pointers are published into the shared graph
(`ActorSprites.reference_document()`, `webfoot graphics references`):

| | Count |
|---|---|
| Anchors | 7,652 = 7,355 containers + 295 characters + palette + table |
| References | 11,254 = 10,959 frame-to-payload + 295 table-to-structure |
| Distinct reference sources | 11,254 (no word claimed twice) |

All are `CONFIRMED_REFERENCE`, because each was checked twice: the pointer
resolved, *and* the payload it reached agreed with the OAM dimensions an
unrelated record declared. Nothing is promoted from pointer shape - a scanner is
not permitted to grow the graph, per the rule TOOLKIT-003 established.

A container's anchor spans its **measured packed extent**, which is the region an
edit is bounded by, not the decoded size - which is larger and exists nowhere in
the image. Frame pointers are deliberately not published: 13,596 more references
would restate what the animation records already say, and none is an edit target.

---

## 13. Capability matrix

Reported per layer, never collapsed into "Graphics = ROUND_TRIP".

| Layer | Rung | Basis |
|---|---|---|
| Container header | ROUND_TRIP | 7,355 decode; header re-emitted exactly |
| Decompression | ROUND_TRIP | 7,355 of 7,355, zero failures |
| Recompression (valid stream) | WRITE | `pack` output decodes back exactly |
| Recompression (bit-exact) | **not achieved** | no bit-exact packer exists; none claimed |
| Tiles / pixels | ROUND_TRIP | exact swizzle inverse on all 7,355 |
| Palette | ROUND_TRIP | encodes to the exact 512 source bytes |
| Logical graphic assets | ROUND_TRIP | stable IDs, sharing represented |
| Pieces | ROUND_TRIP | 16 bytes exact, unknowns preserved |
| Frames | READ | decoded; the accepted reader reaches the 10,959 single-piece frames. **LOGX-FRAME-001 corrects the stride**: the corpus holds **11,005 piece records over 10,980 frames**, including **21 multi-piece frames** |
| Animations | READ | structure decoded; **no semantics named** |
| Project PNG export/import | ROUND_TRIP | exact on all 7,355 |
| Palette writes | **WRITE** | in-place, 2 bytes, proven |
| Pixel writes | EDIT | valid re-encode; capacity-blocked for ~199/200 |
| Reference graph | DECLARED | 7,652 anchors / 11,254 confirmed references |
| Enemy -> graphics linkage | **UNKNOWN** | no verified static path; all 141 records probed |
| Map tilesets / other families | DISCOVERED | not investigated |

---

## 14. Runtime validation status

**Not performed.** The visual proof in §8 and the edit proof are **static**:
assets decoded from the canonical image and from the built image by this
project's own codec, then rendered and inspected.

In-game confirmation on an emulator was **not** carried out, and this document
does not claim it. Per §24 that is an acceptable close with the gap stated
explicitly rather than glossed.

---

## 15. Sources

**Upstream (pinned).**

* `extern/DragonByteZ` @ `b2691209` - MIT. `src/compression.cpp` (container bit
  grammar), `src/sprite_analysis.cpp:30-31` (table `0x006B6BDC`, count 297) and
  `:634-830` (piece/frame/animation layout), `src/rom.cpp:76-92` (Buu profile,
  object palette `0x0005652C`). Promoted as code under its licence.
* `extern/BuusFuryToolkit` @ `4353f6a2` - `.pal` files and PNGs; no format
  description. Lead only.
* `extern/buusfury`, `extern/Legacy`, the three mstan recomps - audited, no Buu
  graphics tables.

**External.**

* GBATEK via the mgba-emu mirror - OAM attribute layout and the shape/size table.
* gbadev.net GBA documentation - attribute-1 bit positions; 64 bytes per 8x8 tile
  at 8bpp against 32 at 4bpp.
* PNG 1.2 specification, section 4.2.1.1 - `tRNS` for colour type 3.

**Local.** The canonical ROM, read-only, for every count in this document.
