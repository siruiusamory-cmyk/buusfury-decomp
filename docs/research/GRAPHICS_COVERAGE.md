# Buu's Fury graphics-coverage matrix (GRAPHICS-COVERAGE-001)

What graphical asset *systems* exist in Buu's Fury **outside** the accepted actor
sprite pipeline (TOOLKIT-010 / LOGX-*), who owns each, and which can be
deterministically enumerated with a proven population.

Measured read-only against the canonical image
`buus_fury_usa_rev0_01c1707f`, SHA-256
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`
(SHA-1 `f1c4b07554d2a3b1ad2f325307051e775ce68087`), verified unchanged before and
after. Addresses are GBA addresses; a file offset is the address minus
`0x08000000`.

Evidence labels: **CONFIRMED** (directly established), **INFERRED** (supported,
not proven), **UNKNOWN** (not established). Graphics-shape is reported apart from
graphics-render: a whole-tile decode is CONFIRMED_SHAPE; a rendered/palette proof
would be CONFIRMED_RENDER and is **not** claimed for any category here.

Method was **system-first**: for each category the owning engine table/accessor
was sought before any byte scan. GFXSCAN residuals (LOGX-GFXSCAN-001) were used
only as a cross-check. A successful decompression is not proof of graphics; an
unclassified scanner hit is not proof of a missing asset.

---

## The coverage boundary this ticket starts from

The accepted sprite pipeline reaches **7,390** graphics containers via the
297-entry character table at `0x086B6BDC` (GRAPHICS_FORMAT.md section 12, corrected by
LOGX-FRAME-001). LOGX-GFXSCAN-001 built the full *known-container corpus* from
every accepted graph: **11,715** unique containers across five classes:
7,390 sprite pieces, 3,745 map-dominant-layer chunks (tile-index data, not
pixels), 392 root+0x48 selector streams (u16 selectors, not pixels), 187
root+0x4C tileset banks, and 1 engine default. GRAPHICS_FORMAT.md section 11 lists the
**never-investigated** families: map tilesets, background palette, portraits,
UI/HUD, fonts, effects, title graphics. This ticket resolves those.

The overlap test below is exact: the enumerated portrait and residual container
addresses were intersected with all 11,715 known-corpus addresses. This
intersection is computed from the LOGX-GFXSCAN-001 --known corpus baseline (see
Reproduction), not by the portrait probe, which only self-checks portrait extents.

---

## Matrix

| Category | STATUS | OWNER (table / code, file:line or ROM addr) | FORMAT | COUNT (only if proven) | EXPORT COVERAGE | EVIDENCE |
|---|---|---|---|---|---|---|
| UI / HUD / MENUS | PARTIAL / UNRESOLVED | code-referenced UI-asset descriptors near `0x08071700`; damage-number assets `0x0806E050` (normal, 11 refs) & `0x0806F150` (crit) selected by branch `0x0800E94E` (P-009 runtime) | descriptor record `{ptr, small int}`, not a bare container; underlying graphics format not established | UNKNOWN (no complete table bound) | NONE | **INFERRED** system exists; population **UNKNOWN** |
| KI BLASTS / EFFECTS | UNRESOLVED (no separate system found) | none found outside the actor pipeline; ki-blast observed as an actor object (P-003/P-004 runtime) | n/a | n/a | ALREADY COVERED if actor sprites; else UNKNOWN | **INFERRED**: rides the sprite pipeline or is runtime-composited; **no dedicated effects graphics table located** |
| PORTRAITS | **ENUMERABLE** | portrait pointer array `0x086F393C`, indexed by appearance-def field `+0x08` via accessor `0x08011F20`; array base read from pool word `0x08012194` (LOGX-CHAR-001 section 11) | Webfoot container, form 1, 4,096 B decoded (whole-tile block; INFERRED 64x64 @ 8bpp, no dimension field in the container header) | **155** | NONE | **CONFIRMED_SHAPE**: 155 pointers, all form 1, all decode to exactly 4,096 B, 0 failures, disjoint from the 11,715 known corpus |
| FONTS / GLYPHS | PARTIAL | font descriptor `0x08753A18` (`+0x00` RAM glyph buffer `0x03001C4C`, `+0x04` ROM glyph source `0x087548DC`); measurer `0x0803FFE8` (font metrics table, per-glyph advance, `0xFF` wide/narrow split); blitter `0x0802BF8E` -> OBJ VRAM `0x06010000` (BUU_DIALOG_RUNTIME.md) | glyph tiles blitted per code unit (32 B/glyph step); metrics table = per-glyph u16 advances | UNKNOWN (glyph-bank extent/count not bound) | NONE | **CONFIRMED** a font system is engine-owned and located; **UNKNOWN** glyph-tile population/format |
| TITLE / STATIC / CUTSCENE | UNRESOLVED | residual load-descriptor table at `0x087B5B64` (single ref, pool word `0x080123CC`): 7 ROM container ptrs `0x0879BF2C..0x087B5AA0` then 6 EWRAM `0x0300xxxx` destinations | 6 containers form 1, ~65,322-65,474 B each; 1 small (436 B); RAM-destination load list | UNKNOWN (semantics not proven) | NONE | **CONFIRMED** table shape & that its 7 containers are outside the known corpus; **UNKNOWN** whether graphics vs other resource |
| OTHER GRAPHICS SYSTEMS | see below | root+0x4C tileset banks `0x08179764` (187) already accepted by LOGX-TILE-001; background palette `0x0805632C` runtime-built | banks: form 1, 15,424-16,384 B | 187 (tilesets, prior ticket) | ALREADY COVERED (LOGX-TILE) | tilesets CONFIRMED as containers (LOGX-TILE-001); pixel identity UNRESOLVED there too |

---

## Overlap with the accepted sprite pipeline (SC2, cross-checked vs section 12's 7,390)

Every category's overlap answer, by exact address intersection with the 11,715
known-corpus containers:

- **PORTRAITS: no overlap.** 155 portrait containers `0x086B880C..0x086F3360`,
  0 in the known corpus. The packed region `0x086B880C..0x086F3938` sits **above**
  the sprite graphics region (which ends at `0x086A88AC`): a dedicated block.
- **TITLE/RESIDUAL: no overlap.** The 7 `0x087B5B64` containers are 0-in-corpus.
- **KI BLASTS / EFFECTS: overlap likely.** No separate effects graphics table was
  found; a ki blast is observed as a runtime actor object, and actor graphics are
  the 297-table sprite pieces. So effects graphics, where they are sprites, are
  **already inside** the accepted pipeline. Not independently proven here.
- **FONTS: no container overlap.** Glyphs are blitted from a font glyph source
  (`0x087548DC` region), not from a piece-graphics container.
- **UI/HUD: no overlap.** The damage-number descriptors (`0x0806E050`,
  `0x0806F150`) are records, not corpus containers, and are not in the known set.

---

## The two human-named categories: explicit verdicts (SC3)

**UI / HUD:** *A deterministic source system was NOT fully identified.* Evidence
of a UI-graphics descriptor system exists and is engine-referenced: the
damage-number assets `0x0806E050` / `0x0806F150` selected by the crit branch
`0x0800E94E`, and a cluster of references around `0x08071700`, but no bounded
table with a proven complete population was established. `0x0806E050` is a
descriptor record (`{ROM ptr 0x0806D4E0, 7}`), not a bare container, so its
graphics format is one hop further and was not resolved. Marked **UNRESOLVED**
with the exact leads recorded; not fabricated into a count.

**KI BLASTS / EFFECTS:** *A separate deterministic source system was NOT found,
because the evidence points to there not being one.* No effects-only graphics
table exists outside the actor pipeline in what was searched (the residual,
portrait, font and UI sweeps surfaced no effects table). Prior runtime work
(P-003/P-004) observes the ki blast as an ordinary actor object, which resolves
its graphics to the 297-table sprite pieces already covered by TOOLKIT-010, or to
runtime OBJ composition. Verdict: **INFERRED that effects ride the sprite
pipeline**; no dedicated effects graphics enumerator is warranted.

---

## What settled, what stayed open

**External / upstream evidence.** LOGExtractor (`mainant/LOGExtractor` rev
`3a78bb35`, not vendored) names a "portrait pointer table at `0x6F393C`" and
decodes portraits through its `JCALG1.Decompress`; LOGX-CHAR-001 already confirmed
the address is exact (the accessor's own pool literal) and PARTIALLY CONFIRMED the
"portrait" semantic (consumer passes each pointer to the container dispatcher
`0x0803D940`). This ticket adds the measured population and decode: **155
containers, all 4,096-byte whole-tile blocks, all decode cleanly**, which
upgrades the shape claim to CONFIRMED_SHAPE while leaving render/palette
UNKNOWN. The count 155 is DATA-bounded, not engine-bounded: it is the run of
consecutive ROM-pointer slots (8..162) terminated by the first non-pointer word
(slot 163 = `0x0011E502`), and the accessor `0x08011F20` enforces no upper-index
clamp, so 155 is the measured array run, not an engine-declared length. DragonByteZ (pinned) supplies the sprite/tileset routes reused as the
overlap baseline; it describes no portrait/UI/font/effects format. No new external
research pass was needed for the two human-named categories beyond the standing
IGN/GameFAQs/REFERENCE.md pass already recorded in P-008/P-009 (which established
that damage numbers and criticals are the visible UI-graphics surface).

**Still open (honest UNKNOWNs).**
- Portrait *render*: palette and on-screen size/placement not captured (static
  shape only).
- Font glyph-tile *population*: the font descriptor and glyph source are located
  (`0x08753A18` -> `0x087548DC`), but the glyph-bank extent, glyph count and exact
  tile format were not bound.
- UI/HUD *population*: descriptor system referenced but no complete table.
- Residual `0x087B5B64` *semantics*: 6 ~65 KB containers + 6 RAM destinations look
  like a full-screen/static-image load list, but no rendering consumer was traced;
  graphics identity UNKNOWN. This is the single largest referenced-residual lead
  from LOGX-GFXSCAN-001 section 9 and the correct next target.

---

## Reproduction (SC5)

Portrait population, from the engine-derived array base:

```
.venv/Scripts/python.exe -m tools.research.logx_portrait_probe "roms/Dragon Ball Z - Buu's Fury (U).gba"
```

reports `portrait_count: 155`, `container_kinds {1: 155}`, `declared_sizes
[4096]`, `decoded_sizes [4096]`, `decode_failures 0`. Asserted by
`tests/unit/test_logx_portrait_probe.py` (synthetic) and
`tests/integration/test_logx_portrait_rom.py` (canonical, ROM-gated). The probe
does not compute corpus disjointness; that is established by the separate
`--known` command shown immediately below (0 overlap, independently reproduced).

Known-corpus baseline used for the overlap check:

```
.venv/Scripts/python.exe -m tools.research.logx_gfxscan_probe "roms/Dragon Ball Z - Buu's Fury (U).gba" --known
```

---

## Recommended follow-up exporter / RE tickets

1. **Portrait exporter** (small, ready): the population is enumerable and decodes;
   an indexed-PNG export reusing the sprite palette/codec path is a bounded ticket.
   The one open question is the render palette.
2. **Residual `0x087B5B64` load-descriptor** RE: walk the single reference at
   `0x080123CC`/`0x080123xx` as instructions, identify the consumer, and settle
   whether the 6 large containers are title/cutscene/static graphics. Highest-value
   unknown here.
3. **Font glyph bank** RE: bound `0x087548DC`'s glyph tiles and metrics table at
   the font metrics base; then a glyph-sheet export is feasible.
4. **UI/HUD descriptor table** RE: bound the table around `0x08071700` and resolve
   the damage-number and HUD asset format before any UI exporter.
5. **Portrait completeness** RE: enumerate the 297 appearance-defs' `+0x08` field
   to confirm 155 is complete vs a run.
