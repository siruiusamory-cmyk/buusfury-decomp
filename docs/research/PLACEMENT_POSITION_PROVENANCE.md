# PLACEMENT-POS-001 Phase 0 â€” placement `position_raw` static provenance

Static reverse-engineering only. No runtime capture, no ROM mutation, no
emulator. This locates where placement record `+0x0C` is read during object
construction and where the converted value is stored in the runtime object.
It does **not** establish an axis (X/Y), a unit (pixel/tile/subpixel), or a
map-pixel mapping. Those remain UNKNOWN and are closed only by the runtime
phase (SC7 handoff below).

Profile `buus_fury_usa_rev0_01c1707f`, SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.
Disassembly mechanism: `tools/research/placement_type_audit.py` (Capstone Thumb,
profile/hash-guarded, read-only, post-read immutability check). ROM hash
unchanged before and after every read.

Neutral labels are used throughout: `position_raw_0` = low halfword
(`+0x0C+0`), `position_raw_1` = high halfword (`+0x0C+2`). No axis label is
assigned.

## OBSERVATION â€” the construction chain that carries `+0x0C`

The placement factory `0x0800FD55` (Thumb fetch `0x0800FD54`) reaches the shared
constructor `0x0800F68C` (`r5` = placement record base, `r4` = actor object
base â€” corroborated `AUTHORED_BEHAVIOR_EXECUTION.md:77-78`). The constructor
does **not** read the position value itself. It computes a **pointer** to the
field and forwards it down two calls:

```
0800F6B4  adds r1, r5, #0     ; r1 = placement record base
0800F6B6  adds r1, #0xc       ; r1 = &placement[+0x0C]  (address of position_raw)
0800F6B8  str  r1, [sp]       ; 5th arg (stack) to the next call
0800F6C4  bl   #0x800e754     ; sub-initializer receives &position_raw on the stack
```

`0x0800E754` reads its stack args (`ldm r7,{r6,r7}` at `0800E760`, `r7=sp+0x28`;
`r6` = caller `[sp]` = `&position_raw`) and forwards the same pointer into
`0x0800FD74`:

```
0800E77A  adds r3, r6, #0     ; r3 = &position_raw
0800E780  bl   #0x800fd74     ; r3 carries &position_raw into 0x0800FD74
```

`0x0800FD74` receives it in `r3`, retains it in `r5` (`0800FD7A adds r5,r3,#0`),
and `r5` is not overwritten before the reads below. The intervening call at
`0800FD9C bl 0x800f58c` operates on `r0`/`r1=[sp+8]`/`r2`, not on `r5`
(verified: `0x0800F58C -> 0x0800EB60` is a base-object initializer that never
dereferences `r5`).

## OBSERVATION â€” SC1/SC2/SC3/SC4: the reads, the conversion, the stores

Inside `0x0800FD74`, with `r5 = &placement[+0x0C]` and `r4 = actor object base`:

```
0800FDC0  adds  r1, r4, #0
0800FDC2  adds  r1, #0xff
;   (0800FDC4 strh of an unrelated field via r2=actor+0x1AC â€” not position)
0800FDC6  movs  r3, #0
0800FDC8  ldrsh r2, [r5, r3]   ; SC1: read position_raw_0 (low HW) at &+0, SIGN-EXTENDED
0800FDCA  movs  r3, #2
0800FDCC  ldrsh r5, [r5, r3]   ; SC1: read position_raw_1 (high HW) at &+2, SIGN-EXTENDED
0800FDCE  adds  r1, #0xa1      ; r1 = actor + 0xFF + 0xA1 = actor + 0x1A0
0800FDD0  lsls  r2, r2, #8     ; SC3: position_raw_0 << 8
0800FDD2  str   r2, [r1]       ; SC2: store to actor + 0x1A0
0800FDD4  adds  r0, r1, #4
0800FDD6  lsls  r3, r5, #8     ; SC3: position_raw_1 << 8
0800FDD8  str   r3, [r0]       ; SC2: store to actor + 0x1A4
```

- **SC1 â€” read PC(s).** `0x0800FDC8` reads `position_raw_0`; `0x0800FDCC` reads
  `position_raw_1`. Both halfwords are read separately, both by `ldrsh`.
- **SC2 â€” runtime object field(s) + store PC.** `position_raw_0` is stored at
  **actor + 0x1A0** (`str` at `0x0800FDD2`); `position_raw_1` at **actor +
  0x1A4** (`str` at `0x0800FDD8`). Both are 32-bit stores.
- **SC3 â€” conversion.** Each halfword is left-shifted by 8 (`lsls #8`) before
  the store. No axis swap, no added constant, no actor-dimension/anchor/origin
  term appears between read and store. The only arithmetic is
  `signed(halfword) << 8`.
- **SC4 â€” signedness.** Both reads are `ldrsh` (load register signed halfword):
  each halfword is **sign-extended** from 16 to 32 bits. `position_raw_0` and
  `position_raw_1` are therefore treated as **signed** 16-bit quantities.

## SC5 â€” neutral provenance chain

```
ROM placement +0x0C (position_raw)
  -> factory 0x0800FD54 -> constructor 0x0800F68C
       computes &placement[+0x0C], stores it as a stack arg   (0800F6B4..0800F6B8)
  -> 0x0800E754  forwards &placement[+0x0C] onward             (0800E77A..0800E780)
  -> 0x0800FD74  &placement[+0x0C] retained in r5              (0800FD7A)
       read position_raw_0 : ldrsh r2,[r5,#0]   (0800FDC8)
       read position_raw_1 : ldrsh r5,[r5,#2]   (0800FDCC)
       convert            : each  <<8            (0800FDD0 / 0800FDD6)
       store position_raw_0<<8 -> actor + 0x1A0  (0800FDD2)
       store position_raw_1<<8 -> actor + 0x1A4  (0800FDD8)
```

## INTERPRETATION â€” bounded, not proven in Phase 0

- The `<<8` is consistent with a **Q8 fixed-point** (8 fractional bits)
  representation of the runtime coordinate: the actor fields at `+0x1A0/+0x1A4`
  are read back with `asrs #8` by the position-advance helper `0x0800FDFA`
  (called from the constructor at `0800F712`), the inverse shift. This is an
  INTERPRETATION of the shift's purpose; the fixed-point reading is not required
  to state SC1â€“SC4.
- Two separately-stored, contiguous signed 16-bit values at `actor+0x1A0` and
  `actor+0x1A4` are **shape-consistent** with a coordinate pair, but Phase 0
  assigns **no axis** (which of `raw_0`/`raw_1` is horizontal vs vertical) and
  **no unit** (whether the post-`<<8` value is pixels, subpixels of a pixel, or
  another grid). Those are runtime questions.

## What Phase 0 does NOT close â€” axis/unit/pixel remain UNKNOWN

The pre-existing UNKNOWN axis claims stand unchanged and are **not** removed:

- `formats/map_placements.py:6` â€” "Prefix meanings stay raw, including position halfwords."
- `docs/research/PLACEMENT_CODEC.md:16` â€” "+0C position_raw; position_low/high remain axis-UNKNOWN".
- `docs/research/PLACEMENT_TYPES.md:81` â€” "position_low/high retained; no axis claim added".

Phase 0 locates the read/convert/store chain. It does not measure any object's
on-screen pixel against its `position_raw`, so it cannot say which halfword is X,
which is Y, or how `actor+0x1A0/0x1A4` map to a rendered map pixel. That is the
runtime phase.

## SC7 â€” runtime-capture-phase handoff

To close axis/unit/pixel (the WORKBENCH-006 SC2 blocker,
`docs/research/WORKBENCH_MAP_AUTHORING_DESIGN.md:42-76`):

- **BREAKPOINT PC:** `0x0800FDD2` (after `position_raw_0<<8` is stored) and
  `0x0800FDD8` (after `position_raw_1<<8`), for a known map with a known
  placement. Alternatively break at `0x0800FDC8`/`0x0800FDCC` to capture the raw
  halfwords at the read, with `r5` = `&placement[+0x0C]`.
- **RUNTIME FIELDS TO WATCH (actor object offsets):** `actor+0x1A0`
  (`position_raw_0<<8`) and `actor+0x1A4` (`position_raw_1<<8`). Rediscover the
  actor base per load (never hard-code EWRAM addresses â€” `docs/runtime-capture.md` runtime
  rules); the actor base is `r4` at the breakpoint.
- **WHAT mGBA MUST MEASURE:** for a placement whose stored `position_raw` is
  known from the ROM, capture the object's actual on-screen pixel (or its camera
  transform inputs) and correlate against `actor+0x1A0/0x1A4 >> 8`. That
  correlation establishes (a) which halfword is which screen axis, (b) the unit
  (pixel vs subpixel vs tile), and (c) any map-origin/camera offset between the
  actor coordinate and the rendered-map pixel of `MAP_RENDER_FORMAT.md`. Only
  then can `position_raw <-> logical map pixel` be asserted in both directions.

## Reproduce (read-only)

```powershell
.venv/Scripts/python.exe -m tools.research.placement_type_audit "roms/Dragon Ball Z - Buu's Fury (U).gba" 0x0800f68c 0x0800f740
.venv/Scripts/python.exe -m tools.research.placement_type_audit "roms/Dragon Ball Z - Buu's Fury (U).gba" 0x0800e754 0x0800e784
.venv/Scripts/python.exe -m tools.research.placement_type_audit "roms/Dragon Ball Z - Buu's Fury (U).gba" 0x0800fd74 0x0800fdfa
```

## Phase 1 â€” runtime capture (PLACEMENT-POS-001) â€” HORIZONTAL AXIS + UNIT PROVEN; +0x1A4/vertical to Phase 1b

Phase 1 ran a human-play capture (run `build/placementpos001/doorway-01/`) and
CLOSES the horizontal axis and the unit. The vertical-axis runtime confirmation
and the exact world->screen origin remain open, blocked by a breakpoint-timing
gap that Phase 1b fixes with a one-instruction-later trap. The historical
"staged / wall" notes below are kept because the wall is real and recurs; the
RUNTIME RESULTS subsection at the end carries the closes.

**Capture summary.** SKILL Â§8 case = TARGET FIRES (liveness `0x08004038` fired,
row 1; 40 construction cycles captured). Canonical ROM SHA-256 unchanged
(`940ad5f0â€¦f059e` before == after); source savestate unchanged. Operator (the maintainer)
walked from the map-39 doorway state into **map 39** (one map left of map 40) and
screenshotted the destination area (`mgba-shot-01.png`).

### OBSERVATION â€” the chosen placement (SC0), measured from the ROM

Selected observation target: canonical map 40, resolver key `(0x01,0x0C)`, the
map the private savestate `roms/Dragon Ball Z - Buu's Fury (U).ss1`
(SHA-256 `2d5740a8c54180d153024a11b0e4d1143306957af55a3ad0664c71cf7d9a1aab`)
loads into. It owns two real placement records, both placement type 86
(`enemy:434`, `CONFIRMED_ENEMY_STAT_LINK`), read via
`webfoot map placement`:

| Placement | `position_raw` | low HW (`raw_0`) | high HW (`raw_1`) | type |
|---|---|---|---|---|
| `map:0040/placement:0000` | `0x00D000B0` | 176 | 208 | 86 |
| `map:0040/placement:0001` | `0x00E000C0` | 192 | 224 | 86 |

`raw_0` (low) feeds `actor+0x1A0`; `raw_1` (high) feeds `actor+0x1A4`, per the
Phase 0 chain. **No axis is assigned to either.**

### OBSERVATION â€” the Q8 readback code path (static, this phase)

Disassembly of the position readback helper (`0x080101A6..0x080101C6`,
`placement_type_audit`) shows the exact inverse of the construction `<<8`:

```
080101A6  ldr  r1,[r1]        ; r1 = one packed position field (Q8)
080101A8  ldr  r0,[r0]        ; r0 = the other packed position field (Q8)
080101AA  asrs r1,r1,#8       ; r1 -> integer coordinate  (inverse of <<8)
080101AC  asrs r0,r0,#8       ; r0 -> integer coordinate
080101BA  adds r0,r4,#0xff
080101BC  adds r0,#0x91       ; r0 = actor+0x190
080101C0  ldrb r2,[r0,#0xd]   ; actor+0x19D (a dimension byte)
080101C2  lsrs r2,r2,#1       ; half of it
080101C4  adds r1,r1,r2       ; integer coord + half-dimension
080101C6  str  r1,[r4,#4]     ; -> actor+0x04
```

This corroborates the Q8 (`>>8`) interpretation and shows `actor+0x04` is
derived from **one** of the two Q8 fields plus half of `actor+0x19D`. This is
the same shape as the retired-HP invariant recorded in the mgba-runtime skill
(`u32(actor+0x04) == floor(u32(actor+0x1A4)/256) + 4`, 2,060 samples). **But
which of r0/r1 came from `+0x1A4` is set in the caller and is not proven for the
placement object by this static code** â€” see INTERPRETATION.

### INTERPRETATION â€” what prior evidence suggests and why it is NOT sufficient

- Prior runtime evidence tying `actor+0x04` to `actor+0x1A4>>8` (the "world-Y"
  invariant) was measured on the **wolf combat object** (factory `0x08007675`),
  a DIFFERENT construction family from the placement factory `0x0800FD55`. The
  offsets `+0x1A0/+0x1A4` and the constructor `0x0800F68C` overlap, so it is
  strongly suggestive that a placement's actor shares the layout â€” but the
  contract forbids stating the axis from cross-object inference.
- Even if that binding transfers, "world-Y" is a **label prior work assigned**;
  it is not a proof that `+0x1A4` is the SCREEN-vertical axis of the rendered
  map. SC3 requires correlating against the object's ACTUAL on-screen pixel.
- Static X evidence remains only **suggestive** (`ENTITY_FORMAT.md`: bounds
  packing `0x080755C0` holds X in the low halfword; low-HW spread exceeds high-HW
  in 130 maps vs 52). Suggestive, not proof. Axis stays UNKNOWN.

### THE WALL â€” construction fires only on a live map load (SC1 BLOCKED)

The construction store at `0x0800FDD2`/`0x0800FDD8` executes only while a
placement is being BUILT, which happens during a MAP LOAD. Every available
savestate â€” including the map-40 state above â€” is a snapshot taken AFTER its map
already loaded, so its placements were already constructed; continuing from such
a state does not re-run construction and the breakpoint stays silent
(mgba-runtime SKILL Â§5 ordering; ROM-012 node b493d921: "fresh
factory/descriptor/object attribution occurs during the south transition").

To fire the breakpoint, the operator must, after the observer is armed, walk the
player through a doorway into a fresh area (e.g. the map-39 doorway state
`build/rom012/postload-live-01/input.ss1`, SHA-256
`58228e1d...e207e0f7`, recorded by node 666922c9 as leading to a transition).
Input cannot be driven by the read-only observer, and mGBA sessions in this repo
are human-played. SC3 additionally needs a screenshot of the visible, operator-
recognizable object to read its pixel. Both are legitimate human-play steps.

### INSTRUMENT STAGED (ready for a human-play run)

- Observer: `tools/runtime/placementpos001_construct_watch.lua` (read-only:
  breakpoints + register/memory READS only; allowlisted in
  `tools/runtime/inject_mgba_lua.ps1`). It sets breakpoints at `0x0800FDC8`
  (raw halfwords via `r5`), `0x0800FDD2` and `0x0800FDD8` (captures `r4`=actor
  base, `actor+0x1A0`, `actor+0x1A4`, and their `>>8`), plus a **liveness**
  breakpoint at the interpreter `0x08004038`. It writes `event,pc,r4_actor_base,
  r5,position_raw_0,position_raw_1,actor_1A0,actor_1A4,actor_1A0_asr8,
  actor_1A4_asr8,note`.
- Vehicle: the 0.11 dev build (has `emu:setBreakpoint`), injected into a
  free-running, human-played core â€” NOT the GDB launcher.
- Liveness reading (SKILL Â§8): target silent + liveness silent = nothing proven;
  target silent + liveness fires = real negative; target fires = observed.

### RUNTIME RESULTS (run doorway-01) â€” OBSERVATION

Read from `build/placementpos001/doorway-01/placementpos001-construct.csv`
(122 rows: 1 liveness + 40 read_low + 40 store_low + 40 store_high; 40 distinct
construction cycles, several placements re-constructed, matched by `r5` = the ROM
placement-field address).

**O1 â€” `raw_0 -> actor+0x1A0` is exact at runtime. 40/40 clean, 0 exceptions.**
On every `store_high` row, `actor+0x1A0 >> 8` equals that construction's
`position_raw_0` (paired by `r4`). Sample rows (verbatim CSV):

```
read_low ,0x0800FDC8,r4=0x0203DC90,r5=0x08075628,raw_0=176,raw_1=208
store_high,0x0800FDD8,r4=0x0203DC90,             actor_1A0=0x0000B000 -> >>8 = 176   (== raw_0)
read_low ,0x0800FDC8,r4=0x0203D090,r5=0x08075488,raw_0=232,raw_1=128
store_high,0x0800FDD8,r4=0x0203D090,             actor_1A0=0x0000E800 -> >>8 = 232   (== raw_0)
read_low ,0x0800FDC8,r4=0x0202EB20,r5=0x0807556C,raw_0=504,raw_1=176
store_high,0x0800FDD8,r4=0x0202EB20,             actor_1A0=0x0001F800 -> >>8 = 504   (== raw_0)
read_low ,0x0800FDC8,r4=0x0202E4D0,r5=0x08293450,raw_0=599,raw_1=196
store_high,0x0800FDD8,r4=0x0202E4D0,             actor_1A0=0x00025700 -> >>8 = 599   (== raw_0)
```

`actor+0x1A0` increases monotonically with `raw_0` across placements. This closes
the read/convert/store chain for `raw_0` AT RUNTIME (Phase 0 had it statically).

**O2 â€” the `+0x1A4` capture-timing gap. 0/40 match, 40/40 mismatch (expected).**
On `store_high`, `actor+0x1A4 >> 8` never equals `raw_1`; the field holds
pre-construction values (`0x082947D4`, `0x50505073`, ASCII-looking `0x76757677`,
`0x00000000`, ...). This is NOT evidence `raw_1` is unused â€” it is a breakpoint
phase artifact. mGBA's `setBreakpoint` callback fires when PC *reaches* the
address, i.e. BEFORE that instruction executes. The store to `+0x1A4` is
`0x0800FDD8 str r3,[r0]` and the `store_high` trap sits exactly there, so the
write has not happened yet at capture time. The disassembly (re-read this phase)
confirms `[r0]` IS `r4+0x1A4`:

```
0800FDC0 adds r1,r4,#0
0800FDC2 adds r1,#0xff
0800FDCE adds r1,#0xa1     ; r1 = r4 + 0x1A0
0800FDD2 str  r2,[r1]      ; store raw_0<<8 -> r4+0x1A0   (captured post-write at store_high)
0800FDD4 adds r0,r1,#4     ; r0 = r4 + 0x1A4
0800FDD8 str  r3,[r0]      ; store raw_1<<8 -> r4+0x1A4   (NOT yet run when the trap fires)
0800FDDA ldr  r0,[r4,#0x58]; <- the first instruction where BOTH stores are in the past
```

The symmetry proves the mechanism: `+0x1A0` reads clean at `store_high` (its
store `0x0800FDD2` is already in the past) but stale at `store_low` (its own
store not yet run); `+0x1A4` is stale at both. **Phase 1b fix:** add a breakpoint
at `0x0800FDDA` (one instruction after the high store) and read `r4+0x1A0`,
`r4+0x1A4` there; both stores are then committed. That single added trap closes
the `raw_1 -> actor+0x1A4` runtime confirmation.

**O3 â€” the on-screen scene (`mgba-shot-01.png`, map 39, the maintainer-confirmed).**
Objects read in GBA-screen pixels (viewport window x[10..952]->[0..240],
y[228..872]->[0..160]); the grass/dirt seam runs horizontally at screen-y ~72:

| Object | screen X | screen Y | note |
|---|---|---|---|
| green-armored NPC | ~109 | ~18 | leftmost visible, on grass |
| pink sprite | ~113 | ~39 | on grass |
| Krillin-like NPC | ~165 | ~53 | on grass |
| **Olibu** (blonde/white) | ~238 | ~55 | **rightmost, at the right screen edge** (the maintainer-identified) |
| Goku (player) | ~120 | ~70 | on the seam |

Visible objects span screen-X ~109..238 (WIDE, ~129 px) and screen-Y ~18..55
(NARROW, ~37 px) â€” strung left-to-right along the grass strip above the seam.

Captured map-39 world coords (the `0x08075440..0x0807556C` ROM run), sorted by
`raw_0`: raw_0 spans 88..504 (spread 416), raw_1 spans 96..304 (spread 208).

### RUNTIME RESULTS â€” INTERPRETATION / CLOSES

**C1 â€” AXIS: `raw_0` (low halfword, -> actor+0x1A0) is the HORIZONTAL / screen-X
axis. PROVEN (convergent runtime + pixel + static).** The camera-invariance law
`screen = world - camera` (one shared shift for all objects on a map) forces
screen-order == world-order per axis. The visible set is WIDE in screen-X and
NARROW in screen-Y; the captured world coords are WIDE in raw_0 and narrower in
raw_1; and the ordering co-directs â€” the LEFTMOST visible object (green-armor,
screen-x ~109) carries a small world-X while the RIGHTMOST (Olibu, screen-x ~238
at the right edge) carries a near-maximal world-X (the run reaches raw_0 = 504,
map-scale). raw_0 is the only halfword whose spread exceeds a screen width and
whose ordering matches the left-to-right screen layout. This is independently
corroborated by the static bounds-packing evidence (`0x080755C0` holds X in the
low halfword) â€” convergent, not circular.

**C2 â€” AXIS: `raw_1` (high halfword, -> actor+0x1A4) is the VERTICAL / screen-Y
axis. STRONGLY INDICATED, runtime confirmation deferred to Phase 1b.** By
elimination raw_1 is the remaining (vertical) axis, consistent with the narrow
screen-Y arrangement and with the readback code deriving `actor+0x04` (integer
world-Y in the retired-HP invariant) from a Q8 field. NOT stated as fully proven
because (a) the runtime `+0x1A4` value was not captured post-store (O2), and
(b) no per-object sprite<->record pairing exists for map 39 (0 SDK-attributed
placements), so the vertical pixel correlation rests on elimination + arrangement,
not a locked value. Phase 1b (the `0x0800FDDA` trap) closes (a).

**C3 â€” UNIT: map-space PIXELS (internally Q8 fixed-point).** raw_0 reaches 504
(> 240 screen width) and raw_1 reaches 304 (> 160 screen height), so the values
are MAP/world space, not screen-relative and not per-screen. Magnitudes are
pixel-scale, not tile-scale (a 504-tile-wide map is implausible; 504 px ~ a few
screens wide matches a scrolling area). The construction `<<8` stores them as Q8
fixed-point pixels in `actor+0x1A0/+0x1A4`; the readback `asrs #8`
(`0x080101AA`, `0x0800FE0A`) recovers the integer pixel. So the post-`>>8` value
is an **integer map pixel**.

**C4 â€” ORIGIN / world->screen constant: STILL UNKNOWN (Phase 2 / calibration).**
The camera offset (world_x - screen_x) was not solved: the visible objects could
not be uniquely paired to records (map 39 has no SDK placement attribution), and
the player had already moved after construction, so no single object anchors an
exact `screen = world - camera` constant. Axis polarity is not inverted for X
(world-X increases left->right, same as screen-X â€” proven by the co-ordering in
C1); Y polarity is not yet measured. Closing the exact origin/offset needs Phase
1b's trustworthy `+0x1A4` plus a controlled anchor (a known object at a known
screen pixel, or the live camera register), which is Phase 2's controlled-delta
experiment territory.

### What this closes in the axis-UNKNOWN claims

- `ENTITY_FORMAT.md` / `PLACEMENT_CODEC.md` / `PLACEMENT_TYPES.md` "position_low
  is axis-UNKNOWN": the HORIZONTAL identity of `raw_0` (low HW) is now PROVEN at
  runtime; `raw_1` vertical is STRONGLY INDICATED pending Phase 1b. Update those
  docs only after Phase 1b locks the vertical confirmation, or annotate them as
  "low HW = X PROVEN (PLACEMENT-POS-001 Phase 1); high HW = Y indicated, runtime
  confirmation Phase 1b."
- The unit is now PIXEL (map space), not UNKNOWN.
- The world->map-pixel ORIGIN constant remains UNKNOWN (Phase 2).

## Phase 2 â€” controlled authored-coordinate runs (PLACEMENT-POS-001)

### OBSERVATION â€” constructor copy is confirmed; screenshot identity is not

Four generated output ROMs changed only the authored clone at placement field
`0x087EA40C`, while retaining the canonical source at `0x0807567C`.  The
read-only observer fired at the post-store trap `0x0800FDDA` in every run and
paired each settled row with its live `read_low` row.  The clone and baseline
rows were:

| Run | clone `(raw_0, raw_1)` | baseline `(raw_0, raw_1)` | settled rows |
|---|---:|---:|---:|
| `x-plus-64` | `(240, 224)` | `(192, 224)` | 28/28 both fields exact |
| `x-plus-256` | `(448, 224)` | `(192, 224)` | 28/28 both fields exact |
| `y-plus-64` | `(192, 288)` | `(192, 224)` | 14/14 both fields exact |
| `y-plus-256` | `(192, 480)` | `(192, 224)` | 28/28 both fields exact |

For every settled row, `actor+0x1A0 >> 8 == raw_0` and
`actor+0x1A4 >> 8 == raw_1`.  The source rows are the current load's live
actors, never a reused EWRAM address.  The four generated ROM hashes and the
canonical ROM hash were stable when each run was collected; the canonical
SHA-256 remained `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

The PNGs are not enough to bind either of those actors to a particular sprite.
In particular, `y-plus-256` has clone coordinates `(192,480)`, which are
off-screen for the pictured camera, but it still contains a lower red NPC that
resembles the candidate in `y-plus-64`.  Therefore that NPC cannot be treated
as the authored clone, and no pixel delta, screen scale, or camera constant was
measured from these images.

### INTERPRETATION â€” the controlled runs close construction, not sprite identity

**CONFIRMED:** placement `raw_0/raw_1` are copied exactly into actor world
coordinates as Q8 values at `+0x1A0/+0x1A4`; after the established `>>8`
readback, the actor coordinates equal the two stored integers.

**NOT CONFIRMED BY THESE PNGS:** the particular live actor constructed from
`0x087EA40C` is any particular visible sprite.  This is the same
placement-to-sprite identity gap recorded in `WORKBENCH-006-design.md` (SC5);
numeric similarity or a visually similar red NPC is not evidence of that edge.
That gap does not, however, preclude proving the actor class's coordinate and
render-consumer path statically, which Phase 3 does below.

## Phase 3 â€” placement actor render-consumer proof (static)

### OBSERVATION â€” the placement constructor installs the relevant dispatch table

The same constructor that receives the placement record writes `0x0804C484` to
the newly allocated actor at `0x0800F6C8` (`AUTHORED_BEHAVIOR_EXECUTION.md:76-79,
:110-112`).  This is an actor-specific fact, not an inference from a similarly
shaped combat object.  The table uses signed relative Thumb targets.  Its entries
at `+0x0C` and `+0x10` resolve respectively to fetch addresses `0x0801003A` and
`0x0800EF94` (raw targets `0x0801003B` and `0x0800EF95`).

At `0x08010060..0x08010066`, entry `+0x0C` reads the two actor Q8 fields and
arithmetic-shifts both right by eight.  At `0x08010232..0x08010250` it subtracts
the active view origin at `context+0x28/+0x2C` and stores the results in actor
words `+0x6C/+0x70`.  The dataflow is exact:

```text
actor+0x1A0 >> 8 - context+0x28  -> actor+0x6C
actor+0x1A4 >> 8 - context+0x2C  -> actor+0x70
```

The direct disassembly is retained in the reproducible bounded audit below.
It corroborates the independently recorded screen-delta writer
(`AUTO_RE_<local-state-name>:1754-1774`) without transferring any combat-object identity.

The following dispatch-table entry (`+0x10`, fetch `0x0800EF94`) reads
`actor+0x6C` and `actor+0x70` and packs them independently into the generated
OAM entries (X at `0x0800F0D8`/`0x0800F13C`, Y at
`0x0800F0FA`/`0x0800F14A`).  OAM X and Y are hardware pixel fields.  Therefore
the two source axes, their polarity, and their integer unit are established by
the code that presents this exact placement actor class; no screenshot
lookalike or static EWRAM address is involved.

### RESULT â€” coordinate contract

For the supported canonical Buu profile, placement position has this exact
authoring-space contract:

```text
raw_0 = signed 16-bit map/world X in pixels
raw_1 = signed 16-bit map/world Y in pixels

actor_x_q8 = raw_0 << 8
actor_y_q8 = raw_1 << 8
screen_x = raw_0 - camera_x + sprite_anchor_x
screen_y = raw_1 - camera_y + sprite_anchor_y
```

`sprite_anchor_*` is presentation metadata and `camera_*` is mutable viewport
state; neither belongs in a map authoring transform.  The renderer's logical
map canvas uses the map/world pixel plane, so the reversible placement transform
is simply `map_x = raw_0`, `map_y = raw_1`, with the inverse encoding each
coordinate as a signed 16-bit integer before preserving it as its raw unsigned
halfword.  Reject coordinates outside `[-32768, 32767]`; do not clamp, wrap, or
silently reinterpret them.  Map/background extents remain a separate validation
question: a placement may legitimately lie outside a currently rendered layer.

**Phase 3 verdict:** `FORWARD TRANSFORM (placement raw â†” logical map pixel):
CONFIRMED`; inverse encoding is CONFIRMED under the signed-16 range guard.
The uncontrolled visual identity question is deliberately not promoted and is
not required for marker placement or drag-to-move on the logical canvas.

### SDK/domain exposure

The public placement codec exposes this contract without replacing the lossless
raw fields: `decode_position()`/`encode_position()` convert raw halves and signed
map pixels; `PlacementRecord.position_x`/`.position_y` and
`.with_map_position()` expose the record form.  `scene.map_placements()` and
`scene.scene_placements()` publish both raw halves and `position_x`/`position_y`,
while `scene.add_authored_npc_at()` accepts signed map pixels and performs the
range-checked inverse encoding.  Synthetic boundary tests cover `-32768`, `-1`,
`0`, and `32767`, including rejection rather than wrapping for values outside the
signed-16 domain.

### Reproduce Phase 3 (read-only)

```powershell
.venv/Scripts/python.exe -m tools.research.placement_type_audit "roms/Dragon Ball Z - Buu's Fury (U).gba" 0x0800f68c 0x0800f6d0
.venv/Scripts/python.exe -m tools.research.placement_type_audit "roms/Dragon Ball Z - Buu's Fury (U).gba" 0x0801003a 0x080102d0
.venv/Scripts/python.exe -m tools.research.placement_type_audit "roms/Dragon Ball Z - Buu's Fury (U).gba" 0x0800ef94 0x0800f150
```
