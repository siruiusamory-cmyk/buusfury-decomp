# Dialogue expansion tokens: encoding and engine contract

Ticket: DIALOGUE-EXPANSION-TOKEN-DESIGN-001, side research, continuing
`docs/research/DIALOGUE_RENDER_PATH.md` and `docs/research/DIALOGUE_TWO_GLYPH_POC.md`.
Branch `ticket/dialogue-expansion-token-001`, baseline
`119f9c7617c5c34103989f3ae06e716259d8eeea` (= `origin/master`
`9360379df45b2b928c0321d76c54226799b8235a` plus the two
DIALOGUE-RENDER-PATH-001 research commits).

**This ticket designs and does not implement.** No engine patch exists, no ROM was
written, no emulator ran, and no production module was touched. The canonical image
is unchanged: `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

The design is backed by three tracked tools, all run in this session against that
digest:

| tool | what it measures |
| --- | --- |
| `tools/research/dialogue_control_codes.py` | the special source-unit values, one row per comparison, each citing its instruction |
| `tools/research/dialogue_unit_census.py` | the unit census over the seven spoken-dialogue containers and over the menu/quest pool |
| `tools/research/dialogue_wrap_sim.py` | a transcription of the line fitter and the reveal step, with a self-check, a runtime-log check and the section 11 case matrix |

## 1. What the starting point proved, and three corrections

Proven and carried forward unchanged (DIALOGUE_TWO_GLYPH_POC.md):

* one stored UTF-16 unit can compose two ordinary glyphs through the real strip
  compositor, with one reveal step, one source consume and two glyph-specific
  advances, visibly, on the canonical image;
* the insertion boundary `0x0800B05C..0x0800B092` owns the source cursor
  (`obj+0x14`), the persistent cursor (`obj+0x64`), the compose descriptor
  (`obj+0x80`) and the single consume;
* ARM7TDMI is ARMv4T: a Thumb `BL` is the 23-bit form, so a cave further than
  ±4 MiB from its hook must be reached through a `bl` to a nearby
  `ldr pc,[pc,#imm]` trampoline. A cave at `0x082ED210`, `0x2E21AA` bytes from the
  hook, executed at runtime.

Three corrections were measured this ticket, each of which changes the design.
They are reported as findings, not silently applied to the older documents.

**(a) `obj+0x4C` is a pointer to a 20-byte style record, not a unit count.**
`FUN_0800B188` installs `obj+0x4C = 0x08071720 + 0x10 + style*0x14`. The record
fields are `+0x00` line capacity, `+0x04` max width in pixels, `+0x08` x origin,
`+0x0C` y origin, `+0x10` glyph blob pointer. Measured on the canonical image:
style 0 at `0x08071730` = capacity 4, max width 144, x 8, y 15; style 1 at
`0x08071744` = capacity 2, max width 128, x 16, y 30. `FUN_0800AE74` subtracts
20 px from the max width while `obj+0x28 == 0` (`0x0800AF30`), so the values the
fitter is actually handed are 124 and 108.

**(b) The wide-code class is declared but empty, and it is what an unpatched token
would land in.** `strip+0x0C` holds `0x0806EE6C`, a three-word font struct read as
`[0] = 0x0806E05C` (the 256-entry code → record-index map), `[1] = 11` (the fixed
advance for codes ≥ 0xFF) and `[2] = 0` (the wide-code bitmap base). The
rasteriser `FUN_0803F444` at `0x0803F44A`..`0x0803F458` refuses to draw a code at
or above `DAT_0803F704 = 0x1D9D`, and for a code in `0x00FF..0x1D9C` it composes
from `[2] + (code - 0x100) * 11 * 2`, which on this image is address 0 and above
(BIOS / open bus). So: **codes ≥ 0x1D9D are drawn as nothing at all, while the
caller's inline advance still applies (11 + 1 = 12 px).** Section 2 uses that as
the fail-closed floor for the token window.

**(c) The CODE list in `DIALOGUE_RENDER_PATH.md` section 10 is transposed; its x
values are right.** The document lists x = 8, 18, 28, 38, 48, 58, 60, 64, 70, 76,
82, 88, 91, 95, 97, 100, 110, 114, 118, 124 against codes 65, 119×4, 44, 32, 121,
101, 97, 104, 33, 39, 73, 32, 109, 32, 116, 104, 101. The primary observer log
(`build/toolkit031/twog3-caveonly/strip-probe.csv`, the unpatched control) has
those twenty x values exactly, and its codes read 65, 119×4, 44, 32, 121, 101, 97,
104, 33, **32, 73, 39**, 109, 32, 116, 104, 101: three units are transposed in the
document, nothing else is wrong. `tools/research/dialogue_wrap_sim.py` carries the
run in the log's own order, asserts it against the font table, and with
`--runtime-log` reports whether the log's first twenty compositions are those same
pairs, so the erratum is checkable rather than asserted in prose. The advance formula
is separately validated over the whole log: **941 compositions, 896
consecutive-advance checks, 0 mismatches.** The older document is left untouched.

*Provenance of this paragraph, because it was wrong once:* the first version of
this record claimed the x run was off by one and that `width(0x27) + 1 = 3`
contradicted it. That was an artefact of trusting the document's transposed code
list. The independent review of this ticket (candidate `15326b3`) found it, and the
log above settles it. The paragraph is corrected, not deleted, so the same
inference is not made twice.

## 2. The source-unit census (section 1)

### 2.1 The corpus

Spoken dialogue lives in seven Webfoot-LZ containers named by the pointer table at
file `0x007B5B64` (ROM `0x087B5B64`), reached by record words of kind `0x05`
through the dispatch at `0x08012552` and the consumer at `0x08012230`. Measured by
`dialogue_unit_census`:

| selector | decoded units | record spans | reachable units | span overlap | NUL halfwords |
| --- | --- | --- | --- | --- | --- |
| 0 | 32,674 | 521 | 32,674 | 28,484 | 0 |
| 1 | 32,737 | 447 | 31,970 | 10,880 | 0 |
| 2 | 32,732 | 464 | 32,279 | 17,231 | 0 |
| 3 | 32,667 | 421 | 32,491 | 8,240 | 0 |
| 4 | 32,661 | 486 | 32,661 | 13,650 | 0 |
| 5 | 32,697 | 460 | 32,424 | 9,384 | 0 |
| 6 | 218 | 6 | 218 | 0 | 0 |
| **total** | **196,386** | **2,805** | **194,717** | **87,869** | **0** |

* Reachable units are the union of every span a record handle can name,
  de-duplicated by decoded offset; that is 99.15 % of the decoded containers. The
  overlap column is the duplication between handles.
* **There is not one NUL halfword in the seven decoded containers.** The terminator
  is written at copy time: `0x08012272 strh r0,[r1,#8]` stores zero one unit past
  the copied span. Text is length-bounded in the container and NUL-terminated only
  in RAM.
* Distinct values: **89 reachable, 90 in the whole container.** The one that only
  the container holds is `0x003D` (`=`), 4 occurrences, in no record span. No NUL
  halfword occurs anywhere.

### 2.2 Every special value, with the site that tests it

| value | class | payload units | site | evidence |
| --- | --- | --- | --- | --- |
| `0x0000` | terminator | 0 | `0x0803DE6E`, `0x0803DE9A`, `0x0800AEB2` | sets the end flag / ends the fit |
| `0x0002` | formatting operand | 0 | no instruction compares it | 164 occurrences; consumed as the operand of `0x0008` |
| `0x0007` | formatting operand | 0 | no instruction compares it | 164 occurrences; the other operand |
| `0x0008` | inline formatting | 1 | `0x0800AE20`, `0x0800B046`, `0x0803DEBE` | operand to `strip+3` at `0x0800B04C`; cursor +4 at `0x0800B052`; fitter skips 2 units at `0x0803DEC2` |
| `0x000A` | line break | 0 | `0x0800AE06`, `0x0803DEB0` | dispatcher advances one unit; fitter returns, ending the line |
| `0x000B` | soft end | 0 | `0x0803DEB4` | sets the end flag and returns |
| `0x0020` | space / break point | 0 | `0x0803DEA6`, `0x0800AE4C`, `0x0800AE58` | records the last-space checkpoint; hyphen eats following spaces |
| `0x0021` | box width 40 px | 0 (leading only) | `0x080120E4`, `0x080120EC` | first unit of a string only; consumes that unit and nothing more |
| `0x0023` | box width 120 px | 0 (leading only) | `0x080120FC`, `0x08012102` | first unit of a string only; consumes that unit and nothing more |
| `0x002D` | hyphen join | 0 | `0x0800AE42` | advance one, eat following spaces, return 1 |
| `0x0040` | box width 80 px | 0 (leading only) | `0x080120F0`, `0x080120F8` | first unit of a string only; consumes that unit and nothing more |
| `0x005E` | reveal start | 0 | `0x0800B16E` | advances one unit, sets `obj+0x28 = 1`, installs the reveal controller `0x0800B0A9` |
| `0x00FF` | class threshold | n/a | `0x0800B074`, `0x0803DECA`, `0x0803F44A`, `0x0803FFF6`, `0x0800B74E` | not an equality test: below = two-level table, at or above = fixed advance, no glyph |

The formatting operand is exact, not inferred: over the whole containers `0x0008`
occurs 328 times and `0x0002` and `0x0007` occur 164 times each, and the successor
census shows `0x0008` is followed by exactly `{0x0002: 231, 0x0007: 231}`
occurrences. Every operand is consumed by every decoder site, so neither value can
ever appear as a standalone code.

### 2.3 Font facts that bound the namespace

* The code → record-index map is **exactly 256 entries**. `0x0100` already reads
  unrelated image data (measured: `3 0 0 0 0 2 3068 0`), so any stored unit
  ≥ 0x100 is out of contract for the ordinary path.
* **32 values have no glyph record: `0x00..0x1F`.** Every value in `0x20..0xFE`
  has one. `0xFF` also has a record but is NOT usable as a glyph: the rasteriser's
  `cmp r1,#0xff` at `0x0803F44A` puts it in the wide class, so it would compose
  from the empty wide table at address 0. The dictionary refuses it (section 4).
* **140 glyph values never occur in the corpus**, including all of `0x80..0x9F`,
  `0xA1..0xFE` and the ASCII slots `$ & / < = > [ \ ] _ { | } ~ 0x7F`.
* Highest stored unit anywhere in the corpus: **`0x00EF`**.

### 2.4 The other text store

The menu/quest/item pool is not the dialogue path and has its own renderer
(measurer `0x0803FFE8`, emitter `0x0802BFBC`), so a token window that store already
used would be a collision the dialogue census cannot see. The shipped profile
declares it (`tools/webfoot/data/roms.yaml`, `text_strings`: pool `0x0805792C`,
size 82,874, 1,534 strings) and the census reads it through the shipped loader:
**41,437 units, 89 distinct values, highest `0x00E9`, and nothing at or above
`0x0100`.**

### 2.5 The answer to section 1's question

**Yes: a safely reservable range exists, and it is contiguous and large.** Both
stores top out below `0x0100`, no decoder in the dialogue path branches on a value
outside the twelve above, and the whole `0x0100..0xFFFF` space is unused. A caveat
follows from (b) in section 1: not every unused value is equally safe, because the
engine's wide-code class has a rendering contract of its own.

## 3. Chosen token representation (section 2)

### Option A: a reserved UTF-16 range (CHOSEN): `0xE000..0xE0FF`

256 tokens, `0xE000..0xE0FF`, the first page of the Unicode private use area.
Why this range and not merely "above 0xFF":

* **`0xE000 > 0x1D9D = DAT_0803F704`,** so an unpatched or partially patched build
  draws *nothing* for a token and still advances 12 px. The failure is invisible
  text with a stable layout, not garbage pixels. A window in `0x0100..0x1D9C`
  would compose from the null wide-code base.
* It is above every value either text store uses (`0xEF`, `0xE9`), so no retail
  byte becomes a token.
* Private use is what an authoring tool should refuse to let a user type by
  accident, and it maps to one byte of token id, which keeps the cave's arithmetic
  to a subtract, a compare and a shift.

The window is one page so that the count is a single literal the builder patches;
`count < 256` is legal and the remaining ids fail closed.

### Option B: an existing escape prefix plus an id (REJECTED)

`0x0008` is already a two-unit escape: `0x0800B04C` writes the operand to
`strip+3` and `0x0800B052` advances the cursor by four bytes, and `0x0800AE30`
does the same job on the builder's own path. Reusing it costs two stored units per
token, which fails the compression objective below three glyphs, collides with a
code that occurs 328 times in retail dialogue, and would require the token decoder
to preserve an ink semantics that two independent sites implement.

### Option C: reuse unused glyph-code space (REJECTED)

140 values have a glyph and no occurrence (2.3). They are unused by *retail data*,
not unreachable by the decoder: `read_original_text` performs a raw
`span.decode("utf-16le")`, and a project author may legitimately type `0x00E9`.
Reserving such a value would silently convert future authored text into a token.
Only `0x00..0x1F` is genuinely non-textual, and 27 of those values are free, but
they are no safer than `0xE000` and collide with the C0 control range the fitter
and the dispatcher already read.

### Option D: the engine's own wide-code mechanism (DISCOVERED, REJECTED AS THE
MECHANISM, ADOPTED AS THE SAFETY FLOOR)

The engine already implements "one stored unit → one composite, fixed-width, drawn
from a bitmap table": `advance = [font+1] + 1` and bitmap
`[font+2] + (code - 0x100) * [font+1] * 2`, bounded by `0x1D9D`. It needs no code
patch at all: a build could populate `[font+1]` and `[font+2]`. It is rejected
because the advance is **one constant for every code in the class**, so a token
cell must be padded to a common width; proportional two- and three-glyph
expansions would then advance uniformly and the text would read as monospaced.
This is the honest trade: no patch at all, incorrect width for the stated purpose.

For contrast, the mechanism this design chooses keeps the engine's own advance
formula per glyph, at the cost of two four-byte hooks.

## 4. Dictionary binary format (section 3)

Plain data, fixed stride, fail-closed validation. The engine reads no header; the
header exists so a build can prove what it wrote and a test can refuse a corrupt
blob.

```text
offset  size  field
0x00    4     magic "DTKN"
0x04    1     version = 1
0x05    1     flags   = 0
0x06    2     token count (u16, 1..256)
0x08    1     max glyphs per entry = 3
0x09    1     entry stride in halfwords = 4
0x0A    2     reserved = 0
0x0C    8*n   entries, n = token count
```

One entry is four halfwords: 2..3 glyph codes (`0x0000..0x00FF`) followed by
`0xFFFF` terminators to fill. Entry *i* is the expansion of unit
`0xE000 + i`. Token ids are **generated, not authored**: the dictionary document
lists expansions and the build assigns ids in the document's own deterministic key
order, so no user ever sees or types a code unit.

Settled by measurement or by the fail-closed rule:

* **glyph-code width**: u16, the same width as a source unit, because a glyph
  identity *is* a source unit on this path.
* **terminator, not explicit length**: one load per glyph and no bounds arithmetic;
  a missing terminator is refused at build time.
* **fixed stride**: the engine's lookup is `base + (unit - 0xE000) * 8`, one shift
  and one add. Variable-length entries would need a second index.
* **alignment**: the blob is 4-byte aligned in ROM; entries are 8 bytes, so every
  entry stays 4-byte aligned within it.
* **ordering**: deterministic by the document key order; ids are not stable across
  an insertion, which is harmless because projects store author text and the build
  re-encodes the whole record every time.
* **duplicates**: two entries with the same glyph run are refused at build time
  (they cost table space and hide a mistake).
* **malformed**: any entry with fewer than 2 or more than 3 glyphs, a glyph that is
  not `glyph_admissible` (at or above 0xFF, or a stream control: `0x0000`, `0x0008`,
  `0x000A`, `0x000B`, `0x0020`, `0x002D`), a glyph with no glyph record (which
  excludes the formatting operands `0x0002`/`0x0007` and the empty C0 block), a
  nested token, a missing terminator, a count over 256 or a length that disagrees
  with the header is refused by `decode_dictionary` (implemented in the simulator
  today, so the rule is executable rather than prose). The stream controls are
  excluded because a token is one unit to the fitter: it can never honour a break
  point or a join inside itself, and a space inside a value would silently destroy
  a wrap opportunity. The positional commands (`0x0021`, `0x0023`, `0x0040`) and
  the pre-reveal command (`0x005E`) are NOT excluded: they carry no meaning once
  the unit sits inside an expansion.
* **allocation and provenance**: the blob is emitted by the same allocating build
  domain the dialogue payload already uses (compressed dialogue is engine-proven
  above EOF), and the change manifest records the blob digest and the token count,
  so a build can be re-checked without trusting the ROM.

## 5. Width semantics (section 4)

The engine computes a per-unit advance in exactly two inlined places, both from
the same data, with **no shared helper**:

```text
fitter  0x0803DEC8  ldr r5,[r0,#0xc]        r5 = 0x0806EE6C
        0x0803DECA  cmp r4,#0xff
        0x0803DECE  ldr r4,[r5,#4] / add r4,#1         (>= 0xFF: fixed advance + 1)
        0x0803DED4  ldr r5,[r5,#0] / lsl r4,#1 / ldrh r4,[r5,r4]
        0x0803DEDA  lsl r4,#1 / ldrh r4,[r5,r4] / add r4,#1   (< 0xFF: width + 1)
        0x0803DEE0  ldr r5,[r3,#8] / add r4,r5,r4       += accumulated
        0x0803DEE4  cmp r4,r2 / ble 0x0803DEF2          wrap test
reveal  0x0800B06E  ldr r2,[r4,#0x14] / ldrh r0,[r2,#0]
        0x0800B072  ldr r1,[r5,#0xc]
        0x0800B074  cmp r0,#0xff  ... identical arithmetic ...
        0x0800B08E  strb r0,[r6,#4]                     persistent x := x + width + 1
```

**Exact formula.** For a glyph `g`, `advance(g) = width(g) + 1`, where `width` is
the u16 at `map[map[g]]` and `map` is the table at `0x0806E05C`. For an expansion
`TOKEN -> [g0..gn]`:

```text
expanded_advance = Σ (width(gi) + 1)          no trailing adjustment, no separator
```

This is measured, not assumed: the same formula reproduces **896 consecutive
runtime advances with 0 mismatches** (`--runtime-log`), and the two-glyph proof
measured the second glyph at `x + width(A) + 1` and the persistent cursor at
`x2 + width(B) + 1`.

The wrap check and the composition therefore agree if and only if both are given
the same number. Since the two derivations are separate code, a **single hook
cannot serve both**. That was the design's central question, and the measurement
settles it. The two substitution points:

* composition side: `0x0800B066` (runtime-proven by the two-glyph proof) plus the
  advance at `0x0800B07E..0x0800B08E`.
* wrap side, and this is where the first version of this record was wrong: **the
  width block cannot be hooked in place.** `FUN_0803DE6A` is a leaf:
  `0x0803DE6A push {r4,r5,r6,r7}` and `0x0803DEA2 pop {r4,r5,r6,r7}` / `0x0803DEA4
  bx lr`, with no saved LR. A `BL` at `0x0803DEC8` writes the resume address into
  LR, which is the register holding the caller's return address, and there is no
  other copy of it anywhere: the first return would jump back into the fitter's own
  body and all six callers would break. `r0` (strip) is also live across the loop
  (`0x0803DEF8 b 0x0803DE96` re-enters at `0x0803DEC8`), so it cannot be spent on a
  scratch pointer either. The wrap side is therefore served by a **relocated copy
  of the fitter** (section 10), which is not a leaf by construction: it saves LR,
  so a `BL` inside it is safe.

A third place matters for a detail nobody would expect: for centred text the
**centring path** reads `out[2]` at `0x0800AFE2` and uses it at
`0x0800AFE4..0x0800AFEA` to place the line. A token whose width is wrong shifts
centred text, so the wrap side is load-bearing even when no wrap occurs.

## 6. Wrapping policy (section 5)

Transcribed from `FUN_0803DE6A` and confirmed line by line in the simulator:

* **Per glyph, single forward pass, no lookahead.** The accumulator is `out[2]`,
  zeroed at `0x0803DE94` on every call, and each accepted glyph commits
  `out[1] += 1`, `out[2] += advance` at `0x0803DEF2`.
* **Wrapping is at the last space.** A space records `(its address, width before
  it)` at `0x0803DEAA`/`0x0803DEAC` (one slot, last wins). When
  `accumulated + advance > max`, the fitter rewinds `out[1]`/`out[2]` to that
  checkpoint (`0x0803DEEC`). With no space seen it returns with `out[1]` at the
  overflowing unit, so a single long word breaks at the character rather than
  moving to the next line.
* **Another form of wrap.** The fitter returns the *bounds*, never the source
  cursor; `FUN_0800AE74` stores `out[0] → obj+0x14` (`0x0800AFD0`) and
  `out[1] → obj+0x18` (`0x0800AFD4`). Nothing is consumed or replayed; the
  measured pass reads each line's units and the reveal pass reads them again, which
  is the engine's own idiom.
* **Leading spaces are skipped** at `0x0803DE6C..0x0803DE86`, so the space a wrap
  rewound to is never composed and contributes nothing to the next line.
* **Control codes interrupt the scan**: `0x0A` returns ending the line, `0x0B` and
  `0x00` set the end flag and return, `0x08` skips two units with no width. `0x2D`
  is handled by the *dispatcher* before the scan, not by the fitter.
* **Max width** is `[obj+0x4C]+0x04`, minus 20 px while `obj+0x28 == 0`: 124 px for
  style 0 and 108 px for style 1 are the values actually handed in on the canonical
  image.

**The token's participation follows from being one unit:**

* one stored unit, so the fitter consumes exactly one unit and the token can never
  be split between lines (`--self-check` asserts a fit too narrow for the token
  stops at the token's own unit);
* its full expanded advance enters the accumulator, so the space checkpoint and the
  centring read the same number the composition will use;
* neighbours are unaffected, because the change is arithmetic on one unit.

**What happens without the wrap hook**, the failure section 5 asks about, measured
in the simulator: a line `the` + `WW`-token + `m` at 30 px ends at unit 4 unpatched
(the token is priced at the engine's fixed 12 px, so the line fills as if it fitted)
and at unit 3 patched (the token is priced at its real 28 px). The unpatched build
composes the token starting 16 px into a 30 px line and overruns by 26 px; the
rasteriser clips it and every later unit on that line is placed too far right.

## 7. Reveal semantics (section 6)

```text
one expansion token:  source units consumed = 1
                      reveal steps consumed = 1
                      compositions           = 2..3
                      persistent x advance   = Σ (width(gi) + 1)
```

Measured on the engine: `0x0800B092` is the only source consume in the block
(`cursor += 2`), so one invocation of `FUN_0800AE74` consumes one unit; the
composition count is not tied to it, and the engine's own `FUN_0800B706` already
composes four glyphs in one invocation. The two-glyph proof measured exactly this
shape.

Interaction with the surrounding systems, checked one by one:

* **Typewriter speed.** The reveal controller `0x0800B0A8` calls `FUN_0800AE74`
  in a loop `0x0800B142..0x0800B14A`, `r5` times, where `r5` derives from the font
  descriptor byte at `0x0800B122`/`0x0800B12A`/`0x0800B140`. One call is one unit;
  a token keeps that ratio, so fast text reveals a token in one step.
* **Skip / instant reveal.** There is no separate instant path in
  `FUN_0800AE74`: skipping more per frame is the same loop with a larger `r5`. The
  token stays one step.
* **Sound per character.** `FUN_0800AE74` calls `0x08011944`, `0x0801191A`,
  `0x0803D940`, `0x0800AE00`, `0x0803DE6A`, `0x080178C8` and `0x0803DE50`, and
  nothing else; none of those is an audio call. Nothing on this path can fire once
  per composed glyph, so a token cannot desync a per-character sound.
* **Punctuation delay.** The fitter and the step test only `0x00`, `0x08`, `0x0A`,
  `0x0B`, `0x20` and `0x2D`. There is no punctuation test to desync.
* **Waits and control codes.** Tokens may not contain them (section 4), and a
  token before or after an escape is covered by the case matrix.
* **Line transitions.** The y cursor advances between steps (`0x0800AF9C` adds
  14), never inside one, and a token is one unit of one line.
* **Reveal counters.** `obj+0x34` is incremented at `0x0800B0F0` and decremented at
  `0x0800B0DA` by the controller; the counters are per-step, not per-glyph, so they
  keep their old meaning.

The one thing that would be visibly inconsistent is a token whose glyphs are wider
than the line it starts: section 10 bounds that.

## 8. Encoder and authoring model (section 7)

```text
author text (project dialogue/replacements.toml, UTF-8)
  -> semantic expansion dictionary (new project document, one entry per expansion)
  -> deterministic token assignment (document key order -> 0xE000 + index)
  -> encoded UTF-16 stream (longest match first, non-overlapping, case-sensitive)
  -> ROM
```

* **Where definitions live**: a new project document alongside
  `dialogue/replacements.toml`, holding expansions as text (not code units). The
  authoring model is the existing semantic one; nothing exposes a reserved unit.
* **What the encoder does**: at build time only, matching the dictionary
  longest-first over the author text, never across a control code, never producing
  a substitution that does not strictly shorten the encoded stream (an entry of N
  glyphs replaces N units with 1, so a match always wins; the rule exists to refuse
  a dictionary that encodes to nothing useful).
* **Deterministic ids**: generated from key order. Projects never store ids, so
  renumbering is invisible to authors and the same input always produces the same
  ROM.
* **Round trip**: extraction of the retail corpus is unchanged (`read_original_text`
  is a raw UTF-16LE decode and retail has no tokens). For an authored project the
  build's decode direction maps a token unit back to its expansion text. A unit in
  the window with no dictionary entry is **unknown** and fails closed: the error
  names the unit and the record, and no fallback rendering is invented.
* **Normal Unicode editing stays understandable**: the PUA page is reserved, and
  the authoring validator refuses those code points in authored text, so a token
  can never be typed by hand or arrive from a paste.

## 9. Backward compatibility (section 8)

* **Retail dialogue is untouched.** `0xE000` does not occur in either text store
  (section 2), and no retail record is re-encoded.
* **A project with no expansions produces exactly today's image.** The token domain
  is opt-in: no hooks and no table are emitted, so the byte-identical no-op build
  the current architecture guarantees still holds. (Adopting the patch with an
  empty dictionary would *not* be byte-identical, which is why the patch is emitted
  only when the dictionary is non-empty.)
* **The token branch is dormant for ordinary units.** The measure copy prices a
  non-token unit with the same two table reads the original does, and the
  composition cave does the same, so both fall through to today's arithmetic; the
  self-check, the runtime-log check and the corpus check all assert that no stored
  unit is in the window.
* **Malformed token ids fail closed** as the engine's wide class: nothing drawn,
  advance 12, layout stable.
* **Unsupported profiles fail closed**: the hook and the table depend on the
  measured font struct (`0x0806EE6C`) and the measured insertion sites, and the
  build refuses any image whose digest is not the profile's declared one.
* **Partial application is refused**: a build writes both hooks and the blob
  atomically or not at all; the POC's `caveonly` derivative is the control that
  proves the cave bytes alone are inert.

## 10. Engine patch architecture (section 9)

Three hook sites, one cave block, one shared lookup. The measure side is a copy of
the fitter rather than a patch inside it (section 5), reached by retargeting the two
dialogue-side calls.

| # | site | replaced instruction | entry | resume |
| --- | --- | --- | --- | --- |
| 1a | `0x0800AF3A` | `bl 0x0803DE6A` (the bulk-layout call) | `cave_fitter` | the copy's own epilogues |
| 1b | `0x0800AFC8` | `bl 0x0803DE6A` (the line-start call) | `cave_fitter` | the copy's own epilogues |
| 2 | `0x0800B066` | `0x8801` `ldrh r1,[r0,#0]`; `0x1C28` `add r0,r5,#0` | `cave_compose` | ordinary: `0x0800B06E`; token: `0x0800B094` |

Site 2 is the two-glyph proof's own hook and is runtime-proven. Sites 1a and 1b are
one 4-byte `BL` each, in the same function `FUN_0800AE74`, and both are inside the
23-bit range of the candidate cave (`0x2E22D6` and `0x2E2248`).

**The measure copy.** `FUN_0803DE6A`'s body is `0x0803DE6A..0x0803DEFA`, **144
bytes**: the loop-back branch at `0x0803DEF8` is part of it and the next function
begins at `0x0803DEFA`. It has no literal pool, no nested call and only relative
internal branches, so it can be moved as one block and every internal branch stays
valid; a copy that dropped the last branch would be caught by the re-decode below.
Three same-size edits turn it into a function that may call out:

* `0x0803DE6A push {r4,r5,r6,r7}` (`0xB4F0`) becomes `push {r4,r5,r6,r7,lr}`
  (`0xB5F0`), so the copy owns a saved return address and a `BL` inside it is safe;
* the single shared epilogue `pop {r4,r5,r6,r7}` + `bx lr` (`0xBCF0 0x4770`) becomes
  `pop {r4,r5,r6,r7,pc}` (`0xBDF0`) plus a two-byte no-op filler, so every return
  path leaves through the popped LR;
* the width site `ldr r5,[r0,#0xc]` + `cmp r4,#0xff` becomes `bl token_advance`,
  which prices the unit (token or ordinary) in `r4` and long-jumps back to the
  copy's accumulate point (`ldr r5,[r3,#8]; add r4,r5,r4`). The displaced width
  instructions stay in the copy as dead bytes; the build asserts the jump skips
  them.

The other four callers of `0x0803DE6A` keep the original function, so no other
subsystem can ever be handed token pricing, and the copy is reachable only from the
two dialogue sites. The copy is *not* a re-implementation: it is the original bytes
with three edits, re-decoded from the finished image and compared against a written
instruction table, the check that caught the first cave's encoding error.

**Cave placement.** Candidate `0x082ED210`, in a **3,019-byte all-zero run**, proven
to execute at runtime by the two-glyph proof (`0x2E21AA` from site 2). A second
candidate is `0x083C22FC` (4,348 zero bytes). All-zero is necessary, not sufficient:
a zero run can still be read as data, and the first cave's failure mode was exactly
a plausible-looking placement that did not behave. The build must therefore also
run the POC's **cave-only control** (cave written, hooks not patched) and require it
to match the canonical counters, and it must take the region from the project's own
free-space/allocation machinery rather than from a hand-picked offset.

**ARMv4T branch plan.** Every Thumb `BL` must have `J1 = J2 = 1` and a displacement
inside ±4 MiB; the build refuses otherwise (this is the defect that cost two runs).
**No cave exit may be a Thumb-1 `b`**: that branch reaches ±2 KB only. Every jump
back into `0x0800xxxx` or `0x0803xxxx` is a literal load plus `bx`, the shape the
two-glyph proof used to rejoin at `0x0800B06E`.

**Required state, per entry:**

* `cave_fitter` entry (via `BL` from `0x0800AF3A`/`0x0800AFC8`): the ordinary fitter
  ABI, `r0 = strip (obj+0x80)`, `r1 = &current unit`, `r2 = max width`,
  `r3 = &out`. The copy's prologue saves `lr`; at the width site `r4` holds the unit
  and `r6`/`r7` hold the break-point state. `token_advance` takes `r4` (the unit) and
  `r0` (the strip), because the displaced `ldr r5,[r0,#0xc]` was `r0`'s only reader
  in the copy and the helper needs it on every loop pass. It must preserve `r0`,
  `r1`, `r2`, `r3`, `r6` and `r7`, and return the advance in `r4`. It must not return
  through `lr`: the copy owns the saved return address, so the helper jumps back to
  the copy's accumulate point instead, and `r5` is dead until that point, which
  makes it the free register for the jump-back address.
* `cave_compose` entry: `r4 = obj`, `r5 = strip`, `r6 = obj+0x60`, `r0 = source
  cursor`, and `strip+4`/`strip+8` already loaded from the cursor pair at
  `0x0800B060`/`0x0800B062`. The cave sets `strip+4` before each composition
  (`0x0803DE50(strip, glyph)` reads it back into a private cursor), advances it by
  `width(glyph) + 1`, then writes `strip+4 = x_final`, `obj+0x14 += 2`, and jumps
  to `0x0800B094`. `r4`, `r5` and `r6` must survive every call.

**Shared helpers.** One `token_lookup(unit)` returns the entry pointer or zero
(range test against a patched bound), and one `glyph_advance(glyph)` returns
`width + 1` from the same two-level table the engine reads. The measure copy and
the composition cave both call them, so width and composition can never disagree
about what an entry means. The table itself is read as
`base + (unit - 0xE000) * 8`, with `base` and `count` as literals the builder
patches and the cave re-reads. A unit in the window whose id is at or above `count`
takes the ordinary path in both, which is what keeps a stale literal fail-closed
rather than half-decoded.

**Nothing else is duplicated.** The dialogue renderer is not re-implemented: the
composition cave calls the engine's own `0x0803DE50` per glyph, and the measure side
keeps the engine's own loop, accumulator, checkpoint and compare, because the copy
*is* those bytes. The only new algorithm is the token lookup and the per-glyph
advance, and both are shared by the two sides.

## 11. Capacity and limits (section 10)

| dimension | v1 limit | why |
| --- | --- | --- |
| token count | 256 (`0xE000..0xE0FF`) | one page of the PUA, one byte of id in the cave's arithmetic |
| glyphs per token | 2..3 | the common English digraph/trigraph case; stride 4 halfwords keeps the lookup a shift |
| dictionary bytes | 12 + 8·count ≤ 2,060 | 256 × 8 bytes of entries |
| expansion advance | ≤ 108 px, refused above | the narrowest measured line. The fitter's max width is `[obj+0x4C]+0x04`, and `obj+0x4C` is installed by `FUN_0800B188` as `0x08071720 + 0x10 + style*0x14`, so it is the style record: 144 (style 0) or 128 (style 1), minus the 20 px `0x0800AF30` applies while `obj+0x28 == 0`. The leading box-width commands do NOT narrow it: `0x080120E8`/`0x080120F4`/`0x08012100` write the geometry word that `FUN_0800B188` stores into `obj+0x60` (`param_1[0x18] = param_4[1]`), which is where the strip sprites are placed, not the style record. A box frame narrower than a token would clip it visually; it cannot stall the reveal, because the fitter's width is never below 108 px. The glyph cap implies at most 3 × 14 = 42 px, so this bound is a check, not a design constraint |
| token id ≥ count | fall through to the original path | invisible, advance 12, layout stable |
| table base or count literal stale | a unit in the window with no entry takes the ordinary path | same as above; the build refuses a blob whose header disagrees with the patched literals |

Fail closed above every limit, at build time where possible (entry validation,
width bound) and at run time where not (id ≥ count).

## 12. Corpus simulation (section 11)

`tools/research/dialogue_wrap_sim.py` transcribes the fitter and the reveal step
and is checked three ways.

**Calibration.** 896 consecutive runtime advances, 0 mismatches (section 1c), and
the twenty-pair run of section 1c asserted in the log's own unit order.

**Non-interference.** Over all 2,805 record spans of the seven containers (282,586
stored units) no unit is in the token window, so with the patch enabled every
retail line fits exactly as it does today.

**Case matrix** (`--cases`, dictionary 0 = `th` (10 px), 1 = `ing` (14 px),
2 = `WW` (28 px); "stored-look" is the unpatched engine pricing a token at 12 px):

| case | max px | stored-look | expanded | verdict |
| --- | --- | --- | --- | --- |
| expansion mid-word | 124 | width 54, ends 8 | width 54, ends 8 | same line end |
| expansion at a line boundary | 40 | width 16, ends 3 | width 40, ends 7 | **line end moved** |
| expansion before a space | 124 | 36, ends 6 | 34, ends 6 | same |
| expansion after a space | 124 | 36, ends 6 | 34, ends 6 | same |
| two expansions on one line | 124 | 60, ends 7 | 74, ends 7 | same |
| narrow glyphs inside | 124 | 18, ends 4 | 16, ends 4 | same |
| wide glyphs inside | 124 | 50, ends 4 | 48, ends 4 | same |
| wide expansion that looked narrow | 40 | 38, ends 5 | 16, ends 3 | **line end moved** |
| expansion before a control code | 124 | 16, ends 2 | 14, ends 2 | same |
| expansion before a formatting escape | 124 | 20, ends 5 | 18, ends 5 | same |
| expansion on the narrower style | 108 | 58, ends 8 | 72, ends 8 | same |

Readings: a token narrower than the engine's 12 px placeholder makes lines *longer*
and a wider one makes them *shorter*, so the wrap hook is required in both
directions; a token is never split; control codes and formatting escapes keep their
positions; and the two "line end moved" rows are the cases a token-free model
cannot reproduce. All assertion-backed outcomes live in `--self-check`.

## 13. Smallest recommended production scope (section 12)

**v1: tokens in authored dialogue replacements, 2..3 ordinary glyphs, no
recursion.** Explicitly prohibited, each refused at build time:

* nested expansion tokens inside a value;
* control codes, line breaks, formatting escapes or box-width codes inside a value;
* recursive decoding, alternate dictionaries, per-record dictionaries;
* tokens in retail text or in the menu/quest pool;
* more than 256 tokens, more than 3 glyphs, or an expansion advance over 108 px.

Justification: the engine contract this design depends on (one unit, one reveal
step, one consume, per-glyph advance) is exactly what a bounded 2..3-glyph
dictionary exercises, and the value the product gets, more authored text in a
container whose headroom is measured in tens of bytes, is fully obtained by that
scope. Anything larger (a general dictionary codec, nested or stateful expansions)
buys compression this corpus cannot use and multiplies the failure modes.

## 14. Hard failure conditions

| condition | behaviour |
| --- | --- |
| token id ≥ patched count, or any unit in the window with no entry | falls through to the original path: nothing drawn, advance 12 px, layout unchanged |
| dictionary header, count, stride or an entry malformed | build refuses, naming the entry |
| entry holds a stream control, the `0xFF` threshold, a glyph with no glyph record, or a nested token | build refuses |
| expansion advance > 108 px | build refuses |
| a table base or count literal that disagrees with the blob header | build refuses before writing; at run time a stale count alone degrades to the row above |
| hook displacement outside the Thumb 23-bit range or `J1/J2 != 1` | build refuses (existing check) |
| a hook placed inside a leaf function (the defect this design had) | build refuses: the measure side must be the LR-saving copy of section 10, and the build asserts the copy's prologue saves LR and its epilogue returns through it |
| cave region not all zero, the cave re-decode does not match its table, or the cave-only control does not match canonical | build refuses |
| a token unit present in retail text or in the menu/quest pool | build refuses (the census is the check) |
| a token reaching a renderer other than the dialogue path | the other four fitter callers and twelve of the thirteen `0x0803DE50` callers keep the original code, so a token there is priced at 12 px and drawn as nothing: fail-closed, not a crash |
| the authoring validator that refuses the token window in authored text is missing | unsupported: the window is safe for authored text only while that rule exists, so it is a prerequisite of the first build that emits a token, not a later nicety |
| profile identity not the declared digest | build refuses before any read |
| partially applied patch (one hook, or hooks without the blob) | not emitted by construction; a ROM with a stray hook is detected by the site asserts |

## 15. Reproduction

```text
python -m tools.research.dialogue_unit_census \
    --rom "<canonical>.gba" --json build/dialogue-expansion-001/unit-census.json
python -m tools.research.dialogue_wrap_sim \
    --rom "<canonical>.gba" --self-check --cases --corpus \
    --runtime-log "<worktree of DIALOGUE-RENDER-PATH-001>/build/toolkit031/twog3-caveonly/strip-probe.csv"
```

Generated output lives under ignored `build/`; nothing in this ticket writes a ROM
or a tracked binary. The tracked files are the three tools above and this record.

## 16. Verdict

**TOKEN ENCODING DESIGN PROVEN - READY FOR IMPLEMENTATION POC**

The namespace is reserved and collision-proof against both measured text stores
(`0xE000..0xE0FF`, above the rasteriser's `0x1D9D` bound so an unpatched build
degrades to invisible text rather than garbage); the width contract is exact and
validated against 896 runtime advances; the measure side is a relocated copy of the
engine's own fitter rather than a patch inside a leaf function, and the composition
side is the two-glyph proof's own runtime-proven hook; the dictionary is a fixed
8-byte-stride table the simulator decodes and refuses, with every refusal rule
exercised by a case that names the message it expects; and the offline matrix covers
the cases the ticket listed, including the two where the wrap substitution changes
the line end.

What is proven and what is not, stated separately: the composition hook is
runtime-proven on the canonical image; the measure copy and the two `BL`
retargetings are designed and statically consistent with the six caller sites, but
no build has executed them, so the implementation POC carries its own runtime proof.
Nothing was implemented here.
