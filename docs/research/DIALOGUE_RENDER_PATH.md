# The ordinary dialogue character rendering path

Ticket: DIALOGUE-RENDER-PATH-001, side research, isolated from the appearance and
roster work. Research id `842da34b` is not a Git commit; it resolves to the Xael
memory node of that id, "v3 WRITER-EPILOGUE HOOK RUNS CLEAN, BUT THE CHARACTER
GLYPHS COME FROM A THIRD PATH". Its measurements are the starting checkpoint and
were treated as claims to re-measure, not as authority.

Branch `ticket/dialogue-render-path-001`, baseline `origin/master`
`9360379df45b2b928c0321d76c54226799b8235a`. The canonical image was never
opened for writing and is unchanged before and after every run:
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

## 1. The fork

The ticket asks whether ordinary spoken characters reach the screen as

* Model A: individual or per-character OAM entries, or
* Model B: a small stable set of strip or line OAM entries whose backing OBJ
  VRAM tile pixels are rewritten as the reveal proceeds.

**Model B is correct, and it is proven from OAM diffs, not inferred.**

## 2. The mechanism used

`tools/runtime/mgba_session.ps1` (`Start-MgbaSession`) is the tracked entry point
for an instrumented session. It renders a bootstrap, hands mGBA `--script` itself,
loads the savestate from that bootstrap after the observer's `dofile`, and puts
every Lua file through `inject_mgba_lua.ps1 -CheckOnly` first, so the allowlist and
the path rules still gate it. Both identity gates are parameters and were supplied
exactly.

The runs below were made with the pre-merge carrier of that helper: at the time it
existed only as an unmerged commit on `ticket/appearance-authoring-gate-001`, and
the ticket's own non-goals forbid new runtime infrastructure, so it was carried on
the research branch as a separate commit, verbatim apart from the allowlist entries
this ticket needs. That was a recorded deviation, not a silent one. The helper has
since landed on `origin/master` through the appearance gate merge `991e0f3`, and the
authoritative copy is the one to use; only this research branch's duplicate was
temporary.

Observers:

* `tools/runtime/dialogue_strip_probe.lua`, read-only. It installs breakpoints at
  `0x0803DE5E` (inside the glyph composer), `0x0800B08E` (the cursor store),
  `0x0800B092` (the source-cursor store), `0x0800B006` (the reveal queue store)
  and `0x0801227A` (the dialogue record copier, the liveness channel). It dumps
  the full 128-entry OAM with each entry's exact tile coverage, and diffs the
  whole of `0x06014360..0x06014EC0` by byte every 30 frames.
* `tools/runtime/npc_talk_driver.lua`, the input driver, a separate file by rule.
  One A press every 180 frames, held 6, no directional input, bounded.
* `tools/research/dialogue_oam_window_coverage.py` recomputes the window
  inventory independently from the raw OAM words, so the closure does not rest on
  the observer's own arithmetic.

## 3. Proof levels, recorded separately

**IDENTITY VERIFIED.** mGBA `0.11.0.0` from the pinned dev build, checked from
`VersionInfo.FileVersion`. Canonical image digest checked against the exact
caller-supplied value before launch and re-checked after. Savestate
`roms/npc-front.ss1`, sha256
`CBEB1585EA80DD125B53DE247AE441B94BACFA4C2402C755C9B6DE574FD09417`, copied into
each run directory and the copy verified.

**PROCESS LAUNCHED.** `Start-MgbaSession` returned the mGBA process for each run
below. No mGBA process was raced or left behind.

**OBSERVED STATE.** Three runs, each ending by itself through the observer's own
frame budget: the box-closed baseline at 1800 frames, and the control and the
causal diagnostic at 3000 frames each (measured from each run's own
`strip-probe.csv`).

| Run | Image | Purpose |
| --- | --- | --- |
| `build/spritenew001/dialogue-render-01` | canonical | box closed, no input: baseline OAM |
| `build/toolkit031/renderpath-02` | canonical | control with the A driver |
| `build/toolkit031/renderpath-03` | derivative `build/runtime-roms/dialogue-glyphpin.gba` | causal diagnostic |

Control accounting: `compose=941 advance=941 consume=941 qwrite=6 copier=5`,
30 OAM snapshots, 55 non-zero window diffs. The liveness channel fired
(`copier=5`, five dialogue loads), so a silent result elsewhere would be a real
negative rather than an unproven instrument.

**CAUSAL DIAGNOSTIC and VISIBLE RESULT.** Section 9.

## 4. The active OBJ interpretation

Read live from `DISPCNT` (`0x04000000`) on every snapshot: `0x1F40`.

* BG mode 0; BG0 to BG3 enabled; OBJ enabled; not forced blank.
* Bit 6 set, so **OBJ character VRAM mapping is 1D**, not 2D.
* Per entry, the colour depth comes from attr0 bit 13, the shape from attr0
  bits 14-15, the size from attr1 bits 14-15, the affine flag from attr0 bit 8,
  the flip flags from attr1 bits 12-13 (non-affine only) and the palette bank
  from attr2 bits 12-15. All of these are recorded per entry in each
  `oam_*.txt`.

**The tile field is an index of 32-byte units even for an 8bpp entry.** Four
independent measurements agree:

1. The text object's four strip slots are 178, 242, 370 and 498, and the four
   sprites that display them are one 32x64 and three 64x64 256-colour objects.
   Their allocations are exactly contiguous in 32-byte units: 178 + 64 = 242,
   242 + 128 = 370, 370 + 128 = 498, and the next allocation, an unrelated 16x16
   scene sprite, starts at 498 + 128 = 626. Arithmetic that only closes in units
   of 32 cannot be arithmetic in units of 64.
2. The engine's own per-frame blit computes `0x06010000 + slot*32`; decompiled at
   `0x0800ADA0`, and the measured copy arguments in the earlier session
   (`[obj+0x0C] = 626`, `dst = 0x06014E40`) are the same formula.
3. The 16x16 256-colour scene sprite carries tile 626 and its pixels are at
   `0x06014E40..0x06014F3F`. The only bytes that move in a box-closed run are
   exactly the first four 32-byte units of that range.
4. The reveal-correlated changed bytes all fall inside the range computed this
   way.

An object whose starting tile lies below the window can still overlap it, so the
test is byte intersection over the computed span, never "starting tile is inside
the window".

## 5. Every live OAM entry over the character window

Recomputed from the raw OAM words of the control run's 30 snapshots by
`tools/research/dialogue_oam_window_coverage.py`:

```
index   0: seen 18/30  STABLE  tile=498 xy=72,88  square3 8bpp affine=1 pri=0  0x06013E40..0x06014E3F
index   1: seen  3/30  STABLE  tile=498 xy=72,88  square3 8bpp affine=1 pri=0  0x06013E40..0x06014E3F
index  10: seen  9/30  STABLE  tile=626 xy=92,8   square1 8bpp affine=0 pri=1  0x06014E40..0x06014F3F
index  14: seen 18/30  STABLE  tile=626 xy=92,8   square1 8bpp affine=0 pri=1  0x06014E40..0x06014F3F
index  15: seen  3/30  STABLE  tile=626 xy=92,8   square1 8bpp affine=0 pri=1  0x06014E40..0x06014F3F
```

Only two distinct objects ever cover the window. The OAM *index* shifts between
snapshots (0 to 1, 10 to 14 to 15) because the whole table is rebuilt each frame
as unrelated scene sprites come and go; the identity, position, tile and depth of
both objects never change. That is the OAM diff that decides the fork.

The full box-open inventory, from `oam_TICK_01200.txt` in the control run:

| Slot | Tile | Shape and size | Depth | X, Y | Affine | Pri | Bytes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| obj+0x7c | 178 | tall 32x64 | 8bpp | 200, 88 | yes | 0 | `0x06011640..0x06011E3F` |
| obj+0x7e | 242 | square 64x64 | 8bpp | 8, 88 | yes | 0 | `0x06011E40..0x06012E3F` |
| obj+0x7a | 370 | square 64x64 | 8bpp | 136, 88 | yes | 0 | `0x06012E40..0x06013E3F` |
| obj+0x78 | 498 | square 64x64 | 8bpp | 72, 88 | yes | 0 | `0x06013E40..0x06014E3F` |

The four tiles are not an inference: they are the text object's own fields,
`obj+0x78`, `obj+0x7a`, `obj+0x7c`, `obj+0x7e`, read live at all 941
compositions (`t78=498 t7a=370 t7c=178 t7e=242 active=8`), and they are also the
destination of the per-frame upload (section 8).

Of the four, only the `obj+0x78` sprite reaches the window, and only its tail.

## 6. Before the box opens, and during the reveal

**Before dialogue opens** (baseline run, 1800 frames, no input): 11 sprites are
enabled, and exactly one of them touches the window, the 16x16 scene sprite at
tile 626. None of the four strip slots exists in the table.

**Box open, zero characters**: the same snapshot boundary at frame 240, 15
sprites enabled, and the four strip entries are present at their final position
and tile. They are created once per dialogue box, not per character.

**Across the reveal** (941 compositions, control and diagnostic alike): the two
covering objects keep their identity, X, Y, tile, shape, size, depth and
priority. Nothing is created, moved or retargeted per character. What changes is
the byte content of the tiles underneath them.

## 7. Reveal-correlated OBJ VRAM changes

55 non-zero window diffs in the control run, in two families:

* 17 rows of exactly 72 changed bytes across tiles 626 to 629. These also occur
  with the box closed and are the 16x16 scene sprite's animation, not text.
* 38 rows with 128 to 1152 changed bytes whose first changed tile is 539, the
  first 32-byte unit of the window. These only occur while a dialogue box is
  open and they track the reveal. Tiles 539 to 625 are inside the `obj+0x78`
  strip's range, so the reveal is rewriting that strip's tile pixels.

Compactly:

```
reveal k        source unit  = *(u16*)source_cursor          (COMPOSE row, column b)
                cursor       = strip+4, strip+8              (COMPOSE row, columns c and d)
                changed VRAM = window bytes, first tile 539  (WINDOW row)
                covering OAM = one fixed entry, tile 498     (OAMSNAP row)
                OAM changed? NO
```

## 8. Exact role of `0x0800ADA0`

`FUN_0800ADA0(strip)` is the per-frame atlas upload, and it is not a compositor.
It calls the runtime-installed blit thunk `030004C0` three times, once per strip
slot, with the destination `slot * 0x20 + DAT_0800b098` and the source rectangle
taken from `strip` itself (the descriptor at `text_object + 0x80`):

```
slot obj+0x78   rect (0x00, 0, 0x40, 0x40)
slot obj+0x7a   rect (0x40, 0, 0x80, 0x40)
slot obj+0x7c   rect (0x80, 0, 0xA0, 0x40)
```

Its only two callers are `0x0800B14E` and `0x0800B2AE`, both text object
constructors, so it runs once per frame per live text object. It does not choose
glyphs, does not place them and does not touch OAM. Uploading it twice uploads
the same pixels twice. The compositor is elsewhere (section 9).

## 9. The ordinary-character output chain

Every link below is runtime-measured on the canonical control run except the two
marked decompiled.

```
stored UTF-16 source unit
  -> source cursor                     text_object+0x14, advanced by 2 bytes,
                                       at 0x0800B092, once per composed glyph
  -> glyph identity                    r1 = *(u16*)source_cursor, at 0x0800B066,
                                       941 of 941 compositions
  -> glyph pixels                      font table at strip+0x0C = 0x0806EE6C
  -> composition cursor                strip+0x04 = x, strip+0x08 = y,
                                       copied out at 0x0800B060/0x0800B062
  -> composition call                  bl 0x0803DE50 at 0x0800B06A
  -> rasteriser                        [strip+0x20] = 0x0803F445, constant over
                                       all 941 compositions
  -> destination surface               [strip+0x24] + [strip+0x28] * y + x
                                       (decompiled, FUN_0803F444)
  -> per-frame upload                  0x0800ADA0 -> OBJ VRAM at 0x06010000 +
                                       slot * 32                       (decompiled)
  -> stable OAM objects                the four strip entries of section 5
  -> visible ordinary character        control screenshot shot_01200.png
```

`0x0803DE50` is a two-line wrapper: it loads `strip+4` and `strip+8` into a
`{x, y-12}` pair and calls `0x08046AA6`, which is `bx r3` with `r3 = [strip+0x20]`.
The rasteriser `FUN_0803F444(strip, glyph, &cursor)` looks the glyph up in the
font table at `strip+0x0C`, clips it against the rectangle at `strip+0x10`, plots
its set bits into `[strip+0x24] + [strip+0x28] * row + x` with the ink value from
`*(u8*)(strip+3)`, and advances its own cursor copy by `width + 1`.

The reveal step itself is the region entered at `0x0800AE74` (called once from
`0x0800B144`) running through `0x0800AF7A`; it writes one `(x, y)` position-queue
entry to `text_object+0x40` per accepted unit (`qwrite=6`), which is the
prompt-arrow path and not the character output.

## 10. Horizontal advance

The cursor is a byte pair at `strip+4` (x) and `strip+5` (y). The advance is
glyph-specific and table-driven:

* the rasteriser advances its private copy: `*cursor = *cursor + width + 1`,
  where `width` is the `u16` at `font + font_table[glyph]*2`;
* the caller recomputes the same width from the same table and stores
  `width + 1 + strip->x` into `strip+4` at `0x0800B08E`, which is the persistent
  value.

Measured from consecutive COMPOSE rows, the strip's x cursor runs 8, 18, 28, 38,
48, 58, 60, 64, 70, 76, 82, 88, 91, 95, 97, 100, 110, 114, 118, 124 for the
glyph codes 65, 119, 119, 119, 119, 44, 32, 121, 101, 97, 104, 33, 39, 73, 32,
109, 32, 116, 104, 101. The advances are 10, 10, 10, 10, 10, 2, 4, 6, 6, 6, 6,
3, 4, 2, 3, 10, 4, 4, 6, 6, so the width is a property of the glyph and not a
constant. The width is not checked here against the character identity: this run
does not establish the code-to-letter mapping, and the report does not claim one.
The y stride is 14 (compositions land at y = 15, 29, 43, 57).

## 11. Causal diagnostic and control

**The edit.** `build/runtime-roms/dialogue-glyphpin.gba`, sha256
`37F5D540C4FA15A7D1147B1CA12484333A8B2E4EA7A414FCA94C82A4F2AB3FAA`, exactly two
bytes different from canonical, at file offset `0x00B066`:

```
canonical  01 88   ldrh r1,[r0,#0x0]     the glyph identity comes from the source unit
patched    41 21   movs r1,#0x41         every composed glyph is the same code
```

Built by `tools/research/build_dialogue_glyphpin.py`, which refuses unless the
source digest is canonical and the two bytes at that offset are the expected
instruction, and which reads the patch back before writing. The width lookup at
`0x0800B070` reloads the unit from the cursor, so spacing and the consume
accounting are untouched.

**Accounting unchanged.** The derivative run reports
`compose=941 advance=941 consume=941 qwrite=6 copier=5`, byte for byte identical
to the unpatched control. The dialogue record, the number of stored units, the
number of reveal steps and the line layout are unchanged.

**Visible result.** Control `build/toolkit031/renderpath-02/shot_01200.png` shows
the ordinary dialogue text reading "to punch. Fighting isn't all about brute
strength, you need to be smart too!". Diagnostic
`build/toolkit031/renderpath-03/shot_01200.png` shows the same box, the same
portrait, the same scene and the same layout with the ordinary text drawn as
repeated identical glyphs. No overlay, highlight, prompt or portrait sprite is
involved.

That is the ticket's section 5 acceptance, met in the visual domain: an ordinary
spoken character's appearance is causally controlled by the source unit at
`0x0800B066`.

## 12. Two ordinary glyphs from one stored source unit

The four accounts, answered separately.

**Source accounting: YES.** The consume is one independent store,
`str r2,[r4,#0x14]` with `r2 += 2`, at `0x0800B092`. Nothing ties the number of
compositions to it. Measured 941 compositions against 941 consumes, in both the
control and the diagnostic.

**Reveal accounting: YES.** One invocation of the reveal step composes exactly
one character, but the composer itself is not bounded to one call per
invocation: the engine's own `FUN_0800B706` calls `0x0803DE50` four times in a
single invocation (its call sites are `0x0800B720`, `0x0800B742`, `0x0800B772`
and `0x0800B7A2`). Two compositions inside one reveal step are therefore within
the engine's own idiom.

**Cursor accounting: YES, with work.** The composition cursor is an explicit
argument (`strip+0x04`, `strip+0x08`) that the caller writes before each call at
`0x0800B060` and `0x0800B062`. To emit two glyphs from one unit you must plot the
second at `x + width(first) + 1` and leave the persistent `strip+4` holding the
sum of both advances. The advance arithmetic exists twice, once inside the
rasteriser on its private copy and once in the caller at `0x0800B08E`, and only
the caller's copy persists, so a second call must be paired with its own advance
rather than relying on the rasteriser.

**Rendering accounting: YES.** The strips are stable OAM entries whose pixels are
refreshed every frame from the composed surface, so anything composed into the
surface is displayed until the line's surface is rebuilt (the clear path is the
decompression at `0x0803D940` into `strip+0x24`). Measured: across 941
compositions the four strip entries never changed tile, X, Y or depth, while the
window's tile bytes changed 38 times during reveals.

## 13. Canonical ROM safety

The canonical image is immutable and unchanged:
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E` before and
after every run. The savestate was copied into each run directory and the copy
verified. Every generated image and every capture lives under ignored `build/`.
The one derivative image exists only for the diagnostic, its identity is
recorded above, and nothing in it is proposed for production.

## 14. What this does not prove

* The code-to-letter mapping of the font table is not established here.
* The on-screen placement convention for these affine strip objects (whether the
  OAM X and Y name the top-left or the centre) is recorded as raw values only; it
  was not measured.
* `strip+0x24` and `strip+0x28`, the composition surface base and stride, are
  decompiled field semantics; their live values were not captured this run.
* The field at `strip+0x00` was logged as `0x02DC0F00` in 829 of 941
  compositions and `0x07DC0F00` in the other 112, in contiguous runs. Neither
  address is inside any GBA memory region, so that field is not a RAM pointer and
  the earlier note that called it "the static font buffer" is wrong. What the
  field is was not determined.
* The OAM builder `0x0800B374` was read statically (it writes the four entries
  from `obj+0x78`, `obj+0x7a`, `obj+0x7c` and `obj+0x7e`); the run measures the
  entries it produced, not its own entry point.

## 15. Verdict

**STRIP COMPOSITOR PROVEN, READY FOR EXPANSION TOKEN TEST.**

Ordinary spoken characters are not individual OAM entries. They are four stable
2048 to 4096 byte strip sprites, created once per dialogue box, never moved or
retargeted, whose OBJ VRAM tile pixels are rewritten by the glyph rasteriser
`FUN_0803F444` as the reveal proceeds. The composition operation is
`0x0803DE50(strip, source_unit)` called from `0x0800B06A`, with the cursor at
`strip+4` and `strip+8`, the font at `strip+0x0C`, and the advance
`x += width(glyph) + 1` computed from the font table. One ordinary character was
made to visibly change by a two-byte edit at `0x0800B066` with the composition,
advance and consume accounting unchanged.

Two ordinary glyphs from one stored source unit is structurally possible and the
state it needs is named in section 12. No expansion token was implemented.
