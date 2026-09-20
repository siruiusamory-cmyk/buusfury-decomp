# UI / HUD / menu graphics ownership and enumeration (UI-HUD-GRAPHICS-001)

What engine code owns Buu's Fury's UI, HUD and menu graphics, whether that
population can be enumerated deterministically, what container format it uses,
and whether it overlaps the already-accepted map / tile / sprite pipelines.

Measured read-only against the canonical image `buus_fury_usa_rev0_01c1707f`,
SHA-256 `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`,
verified unchanged before and after. Addresses are GBA addresses; a file offset is
the address minus `0x08000000`. Evidence labels are **CONFIRMED** (directly
established), **INFERRED** (supported, not proven) and **UNKNOWN** (not
established).

Method was **system-first**: every claim below is reached from an engine
instruction or an accepted resource graph, never from a byte scan. `GFXSCAN`
residual candidates appear only as a cross-check. A successful decompression is
not treated as proof of graphics.

Reproduce everything with:

```
.venv/Scripts/python.exe -m tools.research.ui_graphics_probe "roms/Dragon Ball Z - Buu's Fury (U).gba" --json build/ui_probe.json
```

---

## 1. Answer in one page

**STATUS: PARTIAL - a deterministic, literal-named enumeration exists and is
disjoint from the accepted corpus; completeness is not proven.**

| Question | Answer |
|---|---|
| What engine code loads UI/HUD/menu graphics? | The container decoder **`0x0803D940`**, reached by handing it a container address that the code named with a Thumb `ldr Rt,[pc,#imm]`. There is no UI-specific loader. **The literal is the population's evidence; the dispatch is observed for only 10 of the 34** (see §3), and the rest are named-but-not-observed. |
| One reusable descriptor/table system, or several? | **Neither, for graphics.** The "descriptor system around `0x08071700`" that GRAPHICS-COVERAGE-001 recorded is a **word inside a subsystem data table**, and the two "UI-asset descriptors" `0x0806E050` / `0x0806F150` are **text/format records**, not graphics. Engine-reachable graphics are named by **literal pool words in code**, exactly as sprites, map chunks and portraits are. |
| Can a UI/HUD graphics population be deterministically enumerated? | **Yes, for the literal-named family**: 34 containers are named by a literal load and accepted by the container test, and **0** of them are in the accepted corpus. The **count is proven for that rule**, and the rule's blind spots are named in §6. |
| What container format? | The **accepted Webfoot container**: an 8-byte header `{u32 kind, u32 declared_size}`, kind `0` = stored, `1`/`2` = the packed bitstream (LOGX-CODEC-001 / `GRAPHICS_FORMAT.md` §3). 11 of the 34 are packed, 23 stored. |
| Genuinely outside the map/tile/sprite pipelines? | **Yes, CONFIRMED**: 0 of the 34 addresses are in the 11,715-container accepted corpus, and the corpus filter removed **none** of the 34 literal-named containers. |
| Can a small representative sample be rendered correctly? | **Yes.** Six of the 34 are 38,400 bytes = `240 * 160 * 1`, and **five render correctly** against the accepted object palette: the **title screen**, the **copyright/legal screen**, and **three publisher/studio logos** (Atari, FUNimation, Webfoot Technologies). The sixth, `0x08732604`, does **not** resolve to a recognisable asset at any framing tried (§5). One further container is a 3,840-byte strip. |

---

## 2. What the recorded leads actually are

GRAPHICS-COVERAGE-001 left three leads. All three are measured here, and two are
**corrected**.

### 2.1 `0x08071700` is a word in a subsystem data table, not a graphics descriptor

`0x0800AB54` (the damage-number painter) loads a base pointer with
`0x0800AB66 ldr r1,[pc,#0x214]`, whose pool word at `0x0800AD7C` is
`0x08071700`, and then reads `[r1,#4]` and `[r1,#8]`. Those two words are
`0x0806F150` and `0x0806E050`.

Read from the image, `0x08071700` holds **`0x03001C4C`**, an **EWRAM** address -
the font subsystem's RAM glyph buffer (`docs/research/GRAPHICS_COVERAGE.md`,
FONTS row: font descriptor `0x08753A18`, `+0x00` RAM glyph buffer `0x03001C4C`).
The surrounding words are not a graphics table at all: from `0x080716A0` the image
holds EWRAM subsystem block pointers (`0x030038A4`, `0x03004A8C`, …), code
pointers, and small `{value, count}` pairs, and `0x08071700` is simply one word
inside that structure. Whatever that structure is - a subsystem/context table is
the plain reading - **it is not a UI graphics descriptor table**, and
`[base+4]` / `[base+8]` land on two more words of it rather than on a table of
its own.

**CONFIRMED** (the pointer load, the table word, and its value are all asserted by
`tests/integration/test_ui_graphics_rom.py`). The table's own semantics are
**UNKNOWN** and are not needed here.

### 2.2 `0x0806E050` / `0x0806F150` are text/format records, not graphics

| Record | `+0x00` | `+0x04` | `+0x00` names |
|---|---|---|---|
| `0x0806E050` (normal side) | `0x0806D4E0` | `7` | a **kind 0 / declared 0** word - the engine's zero-length default container, **not an asset** |
| `0x0806EE6C` | `0x0806E05C` | `11` | a **kind 0 / declared 0** word - the same |
| `0x0806F150` (critical side) | `0x0806EE78` | `0` | a **kind 0 / declared 0** word - the same |

What the probe measures at each target is exactly that: **kind 0 with declared
size 0**, i.e. the engine's default container, which carries no resource at all
(LOGX-CODEC-001). Each of the three targets begins with **65 zero bytes** and then
holds non-zero u16 data, so the honest statement is "a zero-initialised work
region", not "all zero": **CONFIRMED** for the header words; **UNKNOWN** for what
writes the region at runtime.

`0x0806E050` carries a u16 pair run at `+0x48` and `0x0806F150` one at `+0x40`;
**both ascend** (`0x0100, 0x0105, 0x0109, …` and `0x0100, 0x0104, 0x0108, …`
respectively). A run of 4-byte OAM-shaped attribute groups (`0x00040000,
0x112009e0, …`) sits at `0x0806F0F4..0x0806F140`, i.e. **before** the
`0x0806F150` record base, so it is that record's *neighbour*, not a field of it.
These are layout observations and are **INFERRED** as to meaning; no test or probe
output depends on them.

The critical/normal branch itself is confirmed and unchanged from P-009:
`0x0800E94E ldr r2,[r6]` / `0x0800E952 cmp r2,#0` / `0x0800E954 beq` selects
`0x0800E958 movs r2,#4` (critical) against `0x0800E962 movs r2,#3` (normal). What
this ticket adds is the **record's role**: the two words are handed to the
text/OAM path as *format* descriptors whose `+0x00` names a zeroed work region,
so the damage number is drawn through the font and OAM machinery. It is **not** a
separate graphics family reached through these records.

**CONFIRMED** for the record shape, the `+0x00` values, their non-container
status and the branch. Whether the two records differ in anything beyond their
tables is **UNKNOWN** and is not needed for this ticket's question.

### 2.3 So where are the UI graphics?

Named the way every other engine-reachable container in this project is named: a
Thumb `ldr Rt,[pc,#imm8*4]` loads the container's address out of the code's own
literal pool, and, where the consumer is visible, that address is handed to
`0x0803D940`. **No accepted graph in this
project reaches a sprite, map chunk or portrait container by a data-embedded
pointer either** - the sprite pipeline's pieces carry the pointer, the map
pipeline's handlers do, the portrait array does - so this is the engine's own
addressing convention, not a UI peculiarity.

---

## 3. The enumeration rule and the measured population

```
1. Decode [0x08000000, 0x080BB000) as Thumb with resynchronisation
   (tools.research.thumb_disasm), one pass.
2. Collect the `ldr Rt,[pc,#imm8*4]` sites (16-bit encoding 01001 Rt imm8,
   Rt != sp) and the word each addresses: 9,341 sites, 4,556 distinct values.
   This is the *decodable-instruction* population; a raw halfword scan of the same
   bound finds 9,459 such encodings, the extra 118 being interior halfwords of
   4-byte decodes (see the note below). None of the 118 names an accepted
   container, so the population is unaffected.
3. Keep the values that pass the container test: **word-aligned**, header kind in
   {0,1,2}, declared size non-zero and inside the host bound, and for the packed
   kinds an exact decode to the declared size. Only the kind test is the engine's
   (`0x0803D940` selects on nothing else); the rest is host policy and format.
4. Record, *before* filtering, how many of those the accepted known corpus
   already reaches (`logx_gfxscan_probe.build_known_corpus`, 11,715 containers) -
   so the disjointness result in §6 is a measurement and not a restatement of the
   filter - then remove them.
5. Join every aligned word occurrence anywhere in the image, split into
   code-region and data-region references, and attribute each code reference to
   its containing Thumb `push {..,lr}` prologue.
6. Separately, ask for each container whether a `bl 0x0803D940` follows its
   literal load within 32 bytes. That is the *observed dispatch* count; it is
   reported alongside the population, not used to filter it.
```

Result on the canonical image:

| Measure | Value |
|---|---|
| literal load sites scanned (decodable instructions) | 9,341 |
| distinct literal values | 4,556 |
| literal values that are **not** containers | 4,522 |
| literal-named containers, **before** the corpus filter | **34** |
| of those, already in the accepted corpus | **0** |
| **literal-named containers outside the accepted corpus** | **34** |
| kinds | 23 stored (kind 0), 11 packed (kind 1) |
| overlap with the 11,715-container accepted corpus | **0** (measured on the pre-filter set) |
| decode failures | **0** (every container decodes to exactly its declared size) |
| **containers observed handed to `0x0803D940`** | **10** |
| named by more than one code site | 20 |
| referenced from both code and data regions | 0 |

**What the 10/34 dispatch count means.** The literal proves the code *names* the
address; it does not by itself prove a decode. Ten of the 34 have a load site with
a `bl 0x0803D940` inside the window - `0x08055620`, `0x08071758`, `0x0807248C`,
`0x083BE3D4`, `0x086B7E8C`, `0x086F9EC8`, `0x086FA398`, `0x086FABF4`,
`0x087317C8`, `0x08732604` - and are **CONFIRMED** as dispatched containers. For
the other 24 the *role* is **INFERRED** from the header + literal evidence alone.
A negative here is **not** evidence of absence: the dispatch may be further away,
go through a helper, or be reached another way. The window is host policy, not an
engine rule.

**On the 118 extra raw halfwords.** `tools/research/thumb_disasm.py`'s wide sweep
runs Capstone on a Thumb-2-enabled decoder against an ARMv4T image, so it produces
some 4-byte decodes the real CPU would not (3,588 non-`bl`/`blx` 4-byte decodes
inside the code bound). A raw halfword scan finds 118 `ldr Rt,[pc,#imm8*4]`
encodings that this sweep steps over. All 118 were checked and **none** names an
accepted container, so step 2's population is unaffected - but "every site" would
be the wrong word for it.

### The 34, with decoded size, owner and shape

Owners are the containing Thumb `push {..,lr}` prologue; a prologue is a
*candidate* boundary, so an owner address is orientation, not a symbol.

| Container | Kind | Decoded | Packed | Code sites | Owner(s) | Reading |
|---|---:|---:|---:|---:|---|---|
| `0x08055620` | 1 | 38,400 | 2,980 | 3 | `0x08004E2A` | 240x160 8bpp - **renders as the copyright/legal screen** |
| `0x083BE3D4` | 1 | 38,400 | 16,168 | 3 | `0x080051E8`, `0x0801E4A0`, `0x0801E774` | 240x160 8bpp - **renders as the title screen** |
| `0x086F9EC8` | 1 | 38,400 | 1,232 | 1 | `0x08017A14` | 240x160 8bpp - **renders as the Atari logo** |
| `0x086FA398` | 1 | 38,400 | 2,140 | 1 | `0x08017A14` | 240x160 8bpp - **renders as the FUNimation logo** |
| `0x086FABF4` | 1 | 38,400 | 5,700 | 1 | `0x08017AE6` | 240x160 8bpp - **renders as the Webfoot logo** |
| `0x08732604` | 1 | 38,400 | 1,304 | 2 | `0x0802641C`, `0x0802648E` | 240x160 8bpp; **does not render to a recognisable asset** |
| `0x0807248C` | 1 | 3,840 | 56 | 8 | `0x0800BE90`, `0x0800BF34`, `0x0800BF94`, `0x0800C06C`, `0x0800C144`, `0x080364C6` | 240x16 8bpp strip |
| `0x08071758` | 1 | 10,240 | 788 | 4 | `0x08027F74`, `0x08028034`, `0x08028144` | 128x80 8bpp |
| `0x08071A6C` | 1 | 10,240 | 548 | 1 | `0x0806D3A4` | 128x80 8bpp |
| `0x087317C8` | 1 | 2,048 | 236 | 1 | `0x08024A9C` | whole-tile block |
| `0x086B7E8C` | 1 | 256 | 76 | 2 | `0x08016208`, `0x080178C8` | 16x16 8bpp - **renders as an orange/yellow energy burst** |
| `0x086B8088` | 0 | 1,024 | 1,032 | 5 | `0x0802084C`, `0x08028CF4`, `0x08034DE8` | whole-tile block, repeating motif |
| `0x08759334` | 0 | 4,096 | 4,104 | 2 | `0x0803399E`, `0x08033A2A` | whole-tile block |
| `0x08719C40` | 0 | 768 | 776 | 7 | `0x080197B4`, `0x08019858`, `0x08019888` | whole-tile block |
| `0x0874F08C` | 0 | 768 | 776 | 3 | `0x080293E4`, `0x08029584` | whole-tile block |
| `0x0874E208` | 0 | 672 | 680 | 3 | `0x080274B4`, `0x08027516`, `0x08027562` | 7 tiles |
| `0x08759688` | 0 | 672 | 680 | 3 | `0x080359D4`, `0x08035A34`, `0x08035A80` | 7 tiles |
| `0x0871E234` | 0 | 448 | 456 | 6 | `0x0801C900`, `0x0801C978`, `0x0801C9C4` | 7 tiles |
| `0x0874E234` | 0 | 448 | 456 | 5 | `0x080276A8`, `0x0802770C`, `0x0802776E` | 7 tiles |
| `0x0875497C` | 0 | 448 | 456 | 3 | `0x0802C790`, `0x0802C7EA`, `0x0802C8AE` | 7 tiles |
| `0x08756B74` | 0 | 448 | 456 | 4 | `0x0802D79C`, `0x0802D89A`, `0x0802D8E8` | 7 tiles |
| `0x08752EB4` | 0 | 256 | 264 | 1 | `0x0802B708` | 4 tiles |
| `0x08756B0C` | 0 | 256 | 264 | 1 | `0x0802D4B0` | 4 tiles |
| `0x08756B38` | 0 | 256 | 264 | 1 | `0x0802D650` | 4 tiles |
| `0x087113FC` | 0 | 4,450 | 4,458 | 1 | `0x0803044C` | not a whole-tile size |
| `0x087B6EEC` | 0 | 1,608 | 1,616 | 17 | `0x08000738`, `0x0800C368`, … | 13 code-region refs, 0 data-region |
| `0x086B7084` | 0 | 10 | 18 | 7 | - | too small to be graphics |
| `0x0876BA40` | 0 | 4 | 12 | 1 | - | too small to be graphics |
| `0x0875021C` | 0 | 2 | 10 | 1 | - | too small to be graphics |
| `0x0807268C` | 0 | 1 | 9 | 16 | - | one byte |
| `0x080555B8` | 0 | 44 | 52 | 9 | - | 44 bytes |
| `0x087113E0` | 0 | 100 | 108 | 1 | - | 100 bytes |
| `0x0877AE80` | 0 | 80 | 88 | 1 | - | 80 bytes |
| `0x083C34B0` | 0 | 128 | 136 | 1 | - | 128 bytes |

The **whole-tile subset is 25 of the 34** - sizes that are a whole number of 8x8
tiles at 8bpp or 4bpp: the six 38,400-byte screens, the 3,840-byte strip, the two
10,240-byte blocks, the 2,048-byte block, the 1,024-byte motif, the 4,096-byte
block, the 256-byte 16x16 burst, and a family of 448/672/768-byte and 128-byte
blocks.
The other **9 are not tile-aligned at either depth** (sizes 1, 2, 4, 10, 44, 80,
100, 1,608, 4,450), so they are **not graphics** by this test; what they are is
**UNKNOWN**. The rule enumerates *containers the code names*, which is not the
same claim as *graphics* - exactly the distinction GRAPHICS-COVERAGE-001 insists
on.

---

## 4. Format, and what "240x160" means here

The container format is the accepted one and needs no new decoder: an 8-byte
header `{u32 kind, u32 declared_size}`, kind `1` a packed bitstream that
`tools.webfoot.formats.webfoot_lz` decodes exactly. All 34 decode with **zero
failures** to exactly their declared size.

The container header carries **no dimension field** - the same limit
PORTRAIT-COMPLETENESS-001 recorded for portraits. So a dimension is a *reading*
of the decoded size, not a stored fact:

* `38,400 = 240 * 160 * 1` is the GBA screen at 8bpp. **Five of the six** are
  confirmed as full-screen bitmaps **by sight** (§5); the sixth, `0x08732604`,
  does not resolve and is recorded as a render failure.
* `3,840`: the depth is settled **by the render, not by arithmetic**. Rendered at
  240x16 8bpp the payload is a coherent smooth gradient; rendered at 240x32 4bpp
  it is broken dotted banding, and at 240x16 4bpp it bands as well. The code is
  consistent with the 8bpp reading but does not by itself prove it: the owner at
  `0x0800BE90` computes an address from **`0x06010000`** and copies the payload in
  **32-byte addressing units** (`0x0800BEEE lsls r0,r0,#5`, `lsls r1,r4,#9` =
  `16 * 32`), then passes it to the copy helper. A 32-byte unit is the 4bpp 8x8
  tile size, so **the unit is an addressing granularity and not evidence of the
  depth** - which is why the render is the evidence. The width (240) is
  **INFERRED** and the height (16) follows from it; the 8bpp depth, the extent and
  the fact that a `0x06010000`-derived address is passed are what is supported.
* `10,240 = 128 * 80 * 1` is a 128x80 8bpp block. **INFERRED**; the block does
  **not** render to a recognisable asset at that framing (§5).
* `4,096`, `2,048`, `1,024`, `768`, `672`, `448`, `256` are whole numbers of 8x8
  tiles at 8bpp (and of 8x8 tiles at 4bpp); the probe reports both readings
  rather than choosing. **UNKNOWN**.

The probe exposes this as `graphics_shape_candidates(decoded_size)`, a pure
function, and reports tile counts and at most four readings per depth.

---

## 5. Representative visual proof

Rendered with the project's accepted **object** palette (file offset
`0x0005652C`, 512 bytes) as indexed PNGs under the ignored
`build/qa/ui-hud-graphics-001/`. **None of this output is tracked.** Rendered and
inspected:

| Output | Container | Result |
|---|---|---|
| `title_screen_083be3d4.png` | `0x083BE3D4` | The Dragon Ball Z / Buu's Fury title screen, correct colours and transparency. |
| `legal_screen_08055620.png` | `0x08055620` | The copyright / "ALL RIGHTS RESERVED" legal screen, legible. |
| `publisher_logo_086f9ec8.png` | `0x086F9EC8` | The Atari logo: white **ATARI** lettering on a red field. |
| `publisher_logo_086fa398.png` | `0x086FA398` | The FUNimation Productions logo, correct. |
| `screen_086fabf4.png` | `0x086FABF4` | The Webfoot Technologies logo with `www.WebfootGames.com`, correct. |
| `hud_bar_0807248c.png` | `0x0807248C` | A smooth 16-pixel-tall horizontal colour ramp (orange-green-black). |
| `glow_086b7e8c.png` | `0x086B7E8C` | A 16x16 orange/yellow radial energy burst - an impact or hit spark, not obviously UI. |
| `screen_08732604.png` | `0x08732604` | **Not a recognisable asset**: 240x160 noise. Recorded as a failure, not a proof. |

This is the ticket's render proof: **format and palette reading are correct**
(seven distinct assets across three independent container regions decode to
recognisable, correctly-coloured art, **five of them among the six 38,400-byte
screens**). The **remaining 27 containers were not
rendered to a recognisable asset**: the
23 small/non-tile payloads plus `0x08732604`, `0x08071758`, `0x08071A6C` and
`0x08759334`, whose bytes are dominated by very few palette indices and which do
not resolve as plain 8bpp raster at any whole-tile framing. Their **graphics
identity is UNKNOWN** and is not claimed.

Several of the small payloads are **plausibly 4bpp tile blocks** rather than 8bpp
rasters (7 tiles x 32 bytes = 224, 21 x 32 = 672 and 24 x 32 = 768 are all exact
at 4bpp), which is why no dimension is asserted for them.

## 6. Overlap, and what the rule cannot see

**Overlap with the accepted pipelines: none, and the check can fail.** Of the 34
literal-named containers the corpus filter removed **0** - the pre-filter set and
the reported population are both 34 - so the intersection with the
11,715-container accepted corpus (7,390 sprite pieces, 3,745 map-layer chunks,
392 root+0x48 selector streams, 187 root+0x4C bank containers, 1 engine default)
is empty by **measurement against
`logx_gfxscan_probe.build_known_corpus`**, the same baseline
GRAPHICS-COVERAGE-001 and PORTRAIT-COMPLETENESS-001 used. The intersection is
taken on the pre-filter set precisely so it *could* be non-empty: a unit test
drives a fixture whose literal-named container **is** in the supplied corpus and
asserts that the report records it, which a check computed after the filter could
never do.

The addresses sit in regions the accepted corpus never reaches: the six 240x160
screens at `0x08055620`, `0x083BE3D4`, `0x086F9EC8`, `0x086FA398`, `0x086FABF4`
and `0x08732604` (all below the sprite graphics region, which starts at file
offset `0x03C34D0`),
the strip at `0x0807248C` in the early data region, and the 16x16 burst at `0x086B7E8C`
just inside the portrait block.

**What the rule cannot see** - stated here because a count is only as strong as
its stated gap:

1. `add Rd,pc,#imm` and any register-computed base are outside the sweep.
2. Only the 16-bit `ldr Rt,[pc,#imm8*4]` form is read. A container named by a
   wide encoding or by a data-table entry is out of scope.
3. The sweep is bounded to `[0x08000000, 0x080BB000)`. A host-policy bound, not a
   derived code extent: the count is unchanged out to `0x08100000` and only grows
   in data regions (48 at `0x08200000`, 90 at `0x08800000`, the extras being
   data-region coincidences around `0x0817xxxx`). **Relocated IWRAM routines exist
   and are called** - this ticket's own HUD owner calls the veneer `0x0804915C`,
   whose body is at IWRAM `0x030004C0` (§7), and the project documents the same
   family at `0x08049120` -> `0x03000040` - so a loader living in such a routine
   would be invisible to a ROM-only sweep. **Whether any of them names a container
   is UNKNOWN.** The words after `0x08071760` do **not** read as ARM code - **215
   of 232** have a conditional (`cond != 0xF`) high nibble against a random
   expectation of 217.5, and Capstone accepts 200 of 232 as ARM - so no
   relocated-code claim is made for *that* region.
4. A container named only as `base + index` (a pointer table) is invisible,
   though *reading* such a table is how a caller would use it, and no UI pointer
   table was located.

**Related, INFERRED, not enumerated and not claimed as graphics:** 1,475 novel
containers have an aligned word reference **only** in the data region and none in
code. That population is dominated by low-declared-size coincidences and by
containers that resolve *inside* the packed extent of another container, so it is
a residual, not an asset family, and no count from it is promoted here. The
strongest sub-population is the **55 kind-1 containers of declared size >= 1,024
in `0x087315E8..0x0874D044`**: **52** of them have exactly one aligned word
reference and **3 have none** (so they are named by nothing this scan can see),
and they are **not** "one data word each", which is why the count is 55 and not
52. Declared sizes run 1,152..38,400 and the ratio `declared / packed_extent` runs
**5.33x..63.16x** against a corpus median of ~3x. Their location inside the region
the font descriptor's glyph source occupies (`0x087548DC`) makes a **glyph- or
UI-sheet pointer table** the leading reading, but this ticket did **not** establish
it, and no shipped instrument produces this number - it is reproduced by the
scratch recount in the ticket's validation notes, not by the probe.

---

## 7. Damage numbers, HUD, menus and icons - explicit verdicts

**Damage numbers.** The critical/normal branch and the two selected records are
**CONFIRMED** as P-009 recorded. Their *role* is now **corrected**: they are
text/format records whose `+0x00` names a kind 0 / declared 0 word - the engine's
zero-length default container, i.e. nothing - so the damage number
is drawn through the font and OAM machinery and there is **no damage-number
graphics container family** to enumerate. The visible red/yellow distinction is a
record swap, not an asset-family swap. **CONFIRMED** for the branch and the header
words; what writes the 65-byte-zero-prefixed work region at runtime is **UNKNOWN**
and is not needed here.

**HUD.** `0x0807248C` is a 3,840-byte packed container, named by **eight** code
sites in six functions (`0x0800BE90`, `0x0800BF34`, `0x0800BF94`, `0x0800C06C`,
`0x0800C144`, `0x080364C6`). The owner around `0x0800BE90` is the most specific:

* `0x0800BEA8 bl 0x0803D940` decodes the container into a stack buffer;
* `0x0800BEEA ldr r1,[pc,#…]` loads **`0x06010000`** (pool `0x0800C0B4`), and the
  loop at `0x0800BEE8..0x0800BF0C` forms `0x06010000 + [r5+0xc]*32 + r4*512`,
  passing that address with the stack buffer as `r0` and `sp` as `r2` to
  `bl 0x0804915C`;
* `0x0800BF1E` then copies one more chunk with `movs r1,#7 ; lsls r1,#9`, a
  **3,584-byte** step.

`7 * 512 + 256 = 3,840`: the whole payload is passed in **32-byte addressing
units**. **What that means for the destination is NOT established.** `0x0804915C`
is a **Thumb->ARM interworking veneer** - `bx pc` ; `ldr pc,[pc,#-4]` ; pool word
at `0x08049164` = **`0x030004C0`, an IWRAM address** - so the routine body is not
in the ROM image and only the argument setup is visible. An address derived from
`0x06010000` is **computed and passed**; whether the helper writes to it or reads
from it is **UNKNOWN**, and the buffer being `r0` is at least as consistent with a
VRAM->RAM read as with a RAM->VRAM write. The project already documents the same
veneer family (`0x08049120` -> IWRAM `0x03000040`, PROJECT_STATE_5 TOOLKIT-019).

The **depth is therefore settled by the render, not by the copy**: at 240x16 8bpp
the payload is a coherent smooth gradient, while 240x32 4bpp is broken dotted
banding. This is the strongest HUD-bar candidate in the population.

**CONFIRMED:** the container's extent, that a `0x06010000`-derived address is
computed and passed to an IWRAM veneer, and that the payload renders coherently at
240x16 8bpp. **INFERRED:** the 240-pixel width and the 16-pixel height, the 8bpp
depth (from the render), and that this element is a HUD bar specifically.
**UNKNOWN:** the copy direction, its semantics, and the routine's body.

**Menus.** No menu-window container is claimed. The two 10,240-byte blocks
(`0x08071758` named by three functions around `0x08027F74`, `0x08071A6C` reached
from the context entry at `0x08071754`) are whole-tile-sized and render as
coarse, regular motifs at 128x80 rather than as window frames, and the engine
blits them via `0x080495C0`-family tile copies rather than as a bitmap. Whether
they are window furniture, a font sheet or a texture is **UNKNOWN**.

**Icons.** `0x086B7E8C` is a 16x16 orange/yellow radial energy burst - more
plausibly an impact/hit spark than an icon - and `0x086B8088` a
1,024-byte repeating motif; a family of 448/672/768-byte whole-tile blocks
(`0x0871E234`, `0x0874E208`, `0x0874E234`, `0x0874F08C`, `0x0875497C`,
`0x08756B0C`, `0x08756B38`, `0x08756B74`, `0x08759688`, `0x08719C40`) is
referenced from many small functions. Whether they are icons, cursors or HUD
furniture is **UNKNOWN**; none was rendered as a recognisable icon.

---

## 8. What settled, what stayed open

**Settled.**

* UI/HUD/menu graphics are **not** a separate resource system. They are the
  accepted container format, named from code literal pools, decoded by the same
  container decoder where the consumer is visible.
* The recorded "descriptor system around `0x08071700`" is a subsystem data table
  and the two "UI-asset descriptors" are text/format records. **Corrected.**
* A deterministic, literal-named, corpus-disjoint population of **34**
  containers exists, all decoding exactly, with **0** measured overlap with the
  accepted corpus. **CONFIRMED for the rule.**
* Format and palette reading are **CONFIRMED_RENDER** for seven assets across
  three independent ROM regions (title, legal screen, three publisher logos, a
  HUD strip and a 16x16 burst) - **five of the six 38,400-byte screens**, the
  sixth (`0x08732604`) being an explicit render failure.
* **The disjointness is measured, not assumed**: the corpus filter removed **0** of
  the 34 literal-named containers, and the intersection is taken on the
  pre-filter set so a hit would be reported.

**Still open.**

* **Completeness is not proven.** 34 is the count for the code-literal rule, not
  a claim about every UI graphic. The four blind spots named in §6 are the reason.
* **The graphics identity of 27 of the 34 is UNKNOWN**, including whether the
  23 small payloads are 4bpp tiles, rasters, data or coincidence.
* **The `0x087315E8..0x0874D044` data-referenced cluster** (55 kind-1 containers:
  52 with exactly one aligned word reference, 3 with none) is unestablished. If it
  is a glyph or UI sheet table it is the single largest remaining UI-graphics
  population.
* **No UI pointer table was located.** The population is literal-named, so there
  is no table whose length could bound it the way the portrait array bounds
  portraits.
* **The role of 24 of the 34 is INFERRED, not observed.** Only 10 have a `bl
  0x0803D940` within the dispatch window; for the other 24 the evidence is the
  literal plus a valid header.

---

## 9. Reproduction and validation

```
# the population, its owners, its shapes and the lead measurements
.venv/Scripts/python.exe -m tools.research.ui_graphics_probe "roms/Dragon Ball Z - Buu's Fury (U).gba"

# just the GRAPHICS-COVERAGE-001 lead measurement
.venv/Scripts/python.exe -m tools.research.ui_graphics_probe "roms/Dragon Ball Z - Buu's Fury (U).gba" --leads

# just the corpus-disjointness cross-check (pre-filter intersection)
.venv/Scripts/python.exe -m tools.research.ui_graphics_probe "roms/Dragon Ball Z - Buu's Fury (U).gba" --overlap
```

* `tests/unit/test_ui_graphics_probe.py` - 22 portable synthetic tests, no ROM:
  the literal-load encoding and its PC-relative, word-aligned arithmetic (pinned
  independently at `0x4985`/`0x0800AB66` -> `0x0800AD7C`, which is the only thing
  that can catch a wrong PC base), the refusal of the `Rt == sp` form, sweep
  resynchronisation, container acceptance and its refusals **including word
  alignment**, the shape reading **including that every reading of every depth
  fits the payload**, the enumeration join, the pre-filter corpus record, sharing,
  and the ROM gate.
* `tests/integration/test_ui_graphics_rom.py` - 15 ROM-gated tests: the 34/23/11
  population, **disjointness measured on the pre-filter set**, the 10/34 observed
  dispatch count, every container decoding to its declared size, the named
  addresses and sizes, the sharing count, the lead corrections, and the engine
  halfwords and pool words this document rests on re-asserted from the image.
* **Independently re-derived outside the probe**, with a raw halfword scan and the
  *shipping* `tools.webfoot.formats.webfoot_lz` rather than the research codec:
  the same **34** values, **126** literal sites, **0** in the 11,715-container
  corpus, **0** decode failures. That is the strongest check on the population,
  because it shares no code with the probe's own sweep.
* Canonical ROM SHA-256 unchanged before and after. No ROM, save, state, dump or
  generated asset is tracked; the rendered PNGs live under the ignored `build/`.
