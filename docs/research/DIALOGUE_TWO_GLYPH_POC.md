# One stored source unit to two ordinary dialogue glyphs

Ticket: DIALOGUE-RENDER-PATH-001, second phase. Side research, isolated from the
appearance and roster work. Starting proof is `docs/research/DIALOGUE_RENDER_PATH.md`:
ordinary spoken characters are four stable strip sprites whose OBJ VRAM tile
pixels are rewritten by the glyph rasteriser as the reveal proceeds.

Branch `ticket/dialogue-render-001`. The canonical image is unchanged before and after
every run: `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

## 1. Verdict

**ONE SOURCE UNIT TO TWO ORDINARY GLYPHS CAUSALLY PROVEN, READY FOR TOKEN
ENCODING DESIGN.**

## 2. Where the edit goes, and why there

The reveal step reached through `0x0800AE74` and `0x0800AF7A` holds all four
pieces of state the problem needs in one scope:

```
0x0800B05C  ldrb r0,[r6,#0x4]      x = the text object's cursor x   (r6 = obj+0x60)
0x0800B05E  ldrb r1,[r6,#0x5]      y = the text object's cursor y
0x0800B060  str  r0,[r5,#0x4]      compose descriptor x := x        (r5 = obj+0x80)
0x0800B062  str  r1,[r5,#0x8]      compose descriptor y := y
0x0800B064  ldr  r0,[r4,#0x14]     r0 = the source cursor            (r4 = obj)
0x0800B066  ldrh r1,[r0,#0x0]      r1 = THE SOURCE UNIT
0x0800B068  add  r0,r5,#0x0        r0 = the strip descriptor
0x0800B06A  bl   0x0803DE50        compose_glyph(strip, unit)
0x0800B06E  ldr  r2,[r4,#0x14]
0x0800B070  ldrh r0,[r2,#0x0]      the same unit, for the width lookup
0x0800B07E  ldr  r1,[r1,#0x0]      font base
0x0800B082  ldrh r0,[r1,r0]        glyph record index
0x0800B086  ldrh r0,[r1,r0]        advance width
0x0800B088  add  r0,#0x1
0x0800B08A  ldrb r1,[r6,#0x4]      the old persistent x
0x0800B08C  add  r0,r0,r1
0x0800B08E  strb r0,[r6,#0x4]      persistent x := x + width + 1
0x0800B090  add  r2,#0x2
0x0800B092  str  r2,[r4,#0x14]     source cursor += 2, ONE unit consumed
```

The edit replaces the two halfwords at `0x0800B066` with a four-byte branch to a
cave, and the cave reproduces the displaced instructions on its normal path:

```
    unit := source_unit
    if unit != TEST_UNIT:
        the original path, exactly, then rejoin at 0x0800B06E
    else:
        compose GLYPH_A at x
        x2 := x + width(GLYPH_A) + 1
        compose GLYPH_B at x2
        x_final := x2 + width(GLYPH_B) + 1
        source cursor += 2, ONE unit consumed
        rejoin at 0x0800B094, past the ordinary advance and consume
```

Not touched: `0x0800ADA0`, the OAM builder, `0x0800B55C`, any prompt or overlay
writer, the dialogue record, the font, the encoder.

## 3. The image and the edit

`build/runtime-roms/dialogue-twoglyph.gba`, sha256
`A5B9C04D9C7CEEE69E034DDBD754E2E693F61DF9AB29D52B52122E523E0AB3E6`, same size as
canonical, built by `tools/research/build_dialogue_twoglyph.py`.

```
hook       0x0800B066   bl 0x082ED210        (4 bytes; the cave's normal path
                                             rejoins at 0x0800B06E)
cave       0x082ED210   92 bytes, no filler before it (a 3019-byte run of 0x00)
expand     0x082ED222   the gated branch
advance    0x082ED24C   the shared width-and-advance helper
```

`GLYPH_A = 0x41 'A'` (width 9) and `GLYPH_B = 0x21 '!'` (width 2), both chosen by
decoding the real font, and `TEST_UNIT = 0x4B 'K'` (width 8), which occurs twice
in the 3000-frame control run. The widths come from
`tools/research/dialogue_font_probe.py`, which reads the table the rasteriser
reads. Every patched site is asserted from the ROM bytes, every branch is encoded
and then decoded back and compared with its intended target, the whole cave is
re-decoded from the finished image and compared instruction by instruction with a
written table, and the build refuses if any byte outside the two patched regions
moved.

## 4. The hard part: ARM7TDMI cannot branch that far

The first cave was placed at `0x087B8A00`, in a 292 KB run of `0xFF` at the end of
the image. That build was correct in every way a disassembler can see: the file
held the right branch, the emulator read the branch and the cave back from its own
address space, and byte intersection confirmed both. The game nevertheless reset
to its boot sequence on the first reveal, and the cave never executed.

The cause is the encoding, not the placement logic. ARM7TDMI is ARMv4T, which has
no Thumb-2. Its Thumb `BL` is the 23-bit form:

```
11110 imm11
11111 imm11
```

so the second halfword's bits 15..11 are all ones. That is exactly the special
case `J1 = J2 = 1` of the Thumb-2 25-bit `BL`, which means the two encodings agree
only while the displacement fits in 23 signed bits. The hook is at `0x0800B06A`
and the first cave was at `0x087B8A00`, 8.05 MB away, so the encoder produced
`J1 = 1, J2 = 0`: a second halfword of `0xF4CB`. On ARM7TDMI that is not a `BL`
suffix at all; the pair is an undefined instruction, the CPU takes the undefined
exception, and the game ends up back at its entry point.

The symptom was misleading in the most expensive way. The patched site appeared
never to execute, the compose that did fire came from the original call site with
garbage arguments, and the game replayed its Funimation logo. Two runs were spent
on that before the built image was disassembled with the repository's own
`tools/research/thumb_disasm.py`, which agreed with the Thumb-2 reading and so
proved nothing about ARMv4T. What settled it was a three-way control:

| Image | Hook | Cave | Result |
| --- | --- | --- | --- |
| `dialogue-twoglyph-caveonly.gba` | not patched | written | identical to canonical control |
| `dialogue-twoglyph-passthrough.gba` | branch | pass-through, 16 bytes | game resets |
| `dialogue-selfbl.gba` | branch to the next instruction | none | game resets |

The first row proves the cave bytes are inert. The second isolates the branch from
the gate. The third is the smallest possible control-flow change and it also
resets, which localises the fault to the branch encoding itself.

The build now refuses any `BL` whose displacement does not fit the 23-bit range or
whose `J1`/`J2` are not both set, with a message naming the trampoline as the fix.
A cave further than 4 MB from its hook needs `bl` to a nearby
`ldr pc,[pc,#imm]` slot, which is the shape the earlier overlay work used.

## 5. Event record

Two events, frames 953 and 2213, byte-identical in the log. Frame 953, from
`build/toolkit031/twog3-full/strip-probe.csv`:

```
952 CONSUME  obj=0x0202CFD8  cursor 0x0202D2A6 -> 0x0202D2A8   (the previous unit)
953 EXPAND   src=0x0202D2AA  unit=75  x=8  y=43  strip+4=8
953 COMPOSE  desc=0x0202D058  glyph=65  x=8   y=43  lr=0x082ED22F
953 COMPOSE  desc=0x0202D058  glyph=33  x=18  y=43  lr=0x082ED23D
954 COMPOSE  desc=0x0202D058  glyph=110 x=21  y=43  lr=0x082ED21F   (next unit)
954 CONSUME  obj=0x0202CFD8  cursor 0x0202D2AC -> 0x0202D2AE
```

```
source unit          : 75 (0x4B)
source ptr before    : 0x0202D2AA
source ptr after     : 0x0202D2AC          (the next unit's read; +2, not +4)

x before             : 8                   (strip+4, and obj+0x64)

glyph A              : 65 (0x41)
width A              : 9
compose A x          : 8

glyph B              : 33 (0x21)
width B              : 2
compose B x          : 18                  (8 + 9 + 1)

persistent x after   : 21                  (18 + 2 + 1, read back from the next
                                            composition, which lands at x = 21)

reveal before/after  : 1 step, 1 EXPAND row, 2 COMPOSE rows, and the following
                       source unit composes normally on the next frame
consume delta        : 1
compose delta        : 2
visible glyphs       : 2
```

The `lr` column is the caller, and it is the independent proof that the pair came
from the cave and not from the original site: `0x082ED22F` is the return address
of the cave's first `bl` and `0x082ED23D` that of its second, where the control's
compositions all carry `0x0800B06F`.

## 6. What each instrument counter means

The whole-run totals differ from the control, and the difference is a property of
where the instruments sit, not of the accounting:

| Counter | Probe site | Control | Diagnostic | Meaning |
| --- | --- | --- | --- | --- |
| compose | `0x0803DE5E` inside the composer | 941 | 943 | compositions actually made, +2 |
| advance | `0x0800B08E`, the ordinary persistent-cursor store | 941 | 939 | the cave performs the advances itself, so this site is not executed for the two events |
| consume | `0x0800B092`, the ordinary source-cursor store | 941 | 939 | same: the cave's single `str r7,[r4,#0x14]` replaces it |
| qwrite | `0x0800B006` | 6 | 6 | unchanged |
| copier | `0x0801227A` | 5 | 5 | unchanged liveness |

The semantic consume for the event is still exactly one, and it is proved from the
pointers rather than from that counter: the next unit's read is at
`0x0202D2AA + 2`.

## 7. Visible causal proof

Same savestate, same three-second A-tap driver, same 3000 frames, same observer.
The gated unit is the first character of the third line.

Control `build/toolkit031/twog3-caveonly/shot_01080.png`:

> Knowing these things is as important as knowing how

Diagnostic `build/toolkit031/twog3-full/shot_01080.png`:

> A!nowing these things is as important as knowing how

The pair is two different ordinary glyphs, a capital A and an exclamation mark,
drawn by the real strip compositor into the real strip sprite, and the rest of the
line continues coherently at the advanced position. Nothing overlay, prompt,
portrait or box related is involved. `cmp_control_1080.png` and `cmp_diag_1080.png`
in the same directory are five-times crops of that line.

Three frames after the event, `expand_00956.png` against the control's
`shot_00960.png` shows the same thing mid-reveal: the control reads `Knowing` and
the diagnostic reads `A!no`, which is the pair plus the first two following
characters.

## 8. Survival and redraw

* The pair is visible on the frame after its reveal and still present 127 frames
  later at frame 1080.
* Subsequent characters reveal normally, at the advanced positions.
* The line stays intact and the following line is unaffected.
* The dialogue closes normally: five dialogue loads and 3000 frames, exactly as in
  the control.
* `0x0800ADA0` refreshed the strip throughout with no corruption; the window
  change count is 55 in both runs and the OAM inventory is identical in shape.

## 9. Where a future token decoder should intervene

**Option A, intercepting the glyph identity immediately before `0x0803DE50`**, is
not sufficient on its own. At that point the source cursor, the persistent x and
the consume are all outside the scope of the interception. A substituted glyph is
easy from there; a second glyph with its own advance is not, because the ordinary
path recomputes the width from the same unit at `0x0800B070` and stores one
advance at `0x0800B08E`.

**Option B, intercepting source-unit handling in the reveal step, is the right
boundary**, and it is the one this proof used: `0x0800B05C..0x0800B092`. It is the
only measured point where the source cursor (`obj+0x14`), the persistent cursor
(`obj+0x64`), the compose descriptor (`obj+0x80`) and the single consume are
simultaneously in scope. The cost is one four-byte branch plus a cave, and the
normal path can be reproduced exactly.

**Option C candidates, rejected on measurement:**

* `0x0800ADA0`, the per-frame upload, sees no glyphs and no cursor and runs once
  per frame regardless of the reveal.
* `0x0800B374`, the OAM builder, emits the same fixed strip entries every frame
  with no per-character state, measured in the first phase.
* `0x0803F444`, the rasteriser, draws one glyph at a caller-owned cursor and has
  no access to the source cursor, so it cannot consume anything.
* `0x0803DE50`, the two-line wrapper, passes a private cursor copy, so a sequence
  built there still needs the caller's advance.

Constraints a design must respect, each measured:

* **Source consumption.** One store, `0x0800B092`; an expansion must keep it at
  one.
* **Width handling.** The ordinary path recomputes the width from the font table
  per unit. An expansion must compute the width of every glyph it emits; this
  proof does so twice, from the same table.
* **Reveal timing.** One reveal step is one source unit. Nothing may consume an
  extra reveal unit; measured unchanged.
* **Control-code collision.** The engine already treats source unit `8` as an
  inline formatting code: at `0x0800B044` it is tested for, and at `0x0800B04A`
  the next halfword becomes a byte at `strip+3` while the source cursor advances
  by four. The gate in this proof sits behind that test, in the block reached from
  `0x0800B048`. A token decoder that reuses a code the ordinary path can reach, or
  that is placed before that test without handling it, will collide with it.
* **Normal path.** Proved identical by the cave-only control, which matches the
  canonical control on every counter.
* **Intrusion.** One four-byte branch.

## 10. Safety, deviations, and what is not settled

The canonical image is unchanged. Every derivative is under ignored `build/`, and
its digest and exact changed bytes are recorded above. The runtime mechanism was the
pre-merge carrier of `Start-MgbaSession`, carried on the research branch as its own
commit; the authoritative helper has since landed on `origin/master` through the
appearance gate merge `991e0f3`, and this record's duplicate is not published.

Four runs were lost to two defects, both now caught at build time: the ARMv4T `BL`
range, and a first cave whose `ldrb`/`strb` offsets were encoded with the word
scaling rule (`[r6,#1]` where `[r6,#4]` was meant), which read the wrong cursor byte
and wrote a byte of the text object. The lesson is the same for both: decode the
built bytes and compare them with a written table.

Not settled here:

* The gate fires on every occurrence of the chosen unit, so a decoder design must
  decide whether a token is a code the engine cannot otherwise emit, an escape
  sequence, or a lookaside table.
* The pair is emitted at the current cursor with no bounds check of its own; the
  ordinary clip still applies, so a pair that overruns a line is clipped rather
  than wrapped. Wrapping is computed from the source widths before composition, so
  an expansion that widens a line by more than the slack can push text past the
  line's end.
* No token value was allocated, no encoder was touched, and no dialogue length
  changed.
