# Packed-stream termination: how the retail engine ends a Webfoot packed stream

Two independent investigations of the retail packed decoder were run against the
canonical image in separate detached worktrees, neither able to read the other's
notes, and this document reconciles them. Every point where they differ is taken
back to the instructions or to a rerun of the measurement, and each disagreement
is adjudicated on the bytes.

- Canonical ROM SHA-256
  `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`,
  8,388,608 bytes, verified before and after; unchanged. No production code
  changed; no ROM-derived fixture added.
- Both passes disassembled the decoder themselves. Their disassembly-level results
  are consolidated in §8.

---

## 1. Headline

**The retail engine terminates a packed stream at an explicit escape in the
bitstream, twelve consecutive zero bits read at a token boundary, and by nothing
else. `CONFIRMED` by two independent disassemblies of the canonical image, plus a
positive census showing no comparison against the destination cursor anywhere in
the decoder.**

The audit's "two mutually exclusive engine termination rules" is real but is not
an engine ambiguity: one claim is about the engine, the other is about the host
tool, and the canonical corpus satisfies both at once, which is how the host rule
came to be mislabelled as the engine's.

---

## 2. The five separate facts

### 2.1 What the ENGINE does: `CONFIRMED`

| Item | Value |
| --- | --- |
| Entry | ARM `0x087B79E4` = IWRAM `0x03000040`, via Thumb to ARM veneer `0x08049120` (literal `0x03000040` at `0x08049128`) |
| Dispatcher | Thumb `0x0803D940`; second entry `0x0803D966` (1 caller: `0x0800F3D2`) |
| Call sites | dispatcher arms `0x0803D958` / `0x0803D97E`, plus **eight direct callers** of the veneer: `0x080040D2`, `0x08009B2C`, `0x08011FCE`, `0x08011FFA`, `0x08013EDE`, `0x0802800E`, `0x080280D4`, `0x08030AFC` |
| Arguments | exactly `(source, destination)`. `0x0803D940 adds r2, r0, #0` discards the incoming `r2`; no length survives |
| Input pointer | `r1 = container + 8`, established at `0x0803D94A` |
| Output pointer | `r0` = destination, write cursor only, established at `0x0803D942` |
| Declared size read by the retail packed path | **NO**: `ldr r2,[r2,#4]` at `0x0803D95E` is on the kind-0 *stored* branch only; the decoder has zero references to `r2`, zero negative-offset loads from `r1`, and only the two bias constants (`0x087B7CCC = 0x37FF`, `0x087B7CD0 = 0x027F`) in its literal pool |
| Termination | the escape: `000` prefix, 7-bit field `0`, 2-bit selector `0`; detected at `0x087B7AD4` / `0x087B7B00`; the loop's **sole** exit is `0x087B7C78` (`pop {r4,r5,r6,r7,r8,sb,sl,fp,lr}` / `0x087B7C7C bx lr`) |
| Write | `strb rX,[r0],#1` at `0x087B7A04`, `0x087B7A78`, `0x087B7C0C`, `0x087B7C20`; back-references read `ldrb rX,[r0,-rN]` |
| Bound | **NONE**: of the 13 comparisons in `0x087B79E4`..`0x087B7C7C` (+17 `subs`), **zero name `r0`**. Compared registers are the bit counter, field width, count, distance, literal width and the bias thresholds |
| Multiplicity | **two byte-instances of the same decoder** (see §3.1). Same grammar, same termination rule. No caller supplies a length, so no caller can impose length termination |

### 2.2 What CANONICAL WEBFOOT DATA does: `CONFIRMED` for the corpus

- Blind scan of the whole image (header kind 1/2, declared in range, kept only
  when the shipping decoder then produces exactly that many bytes): **13,168**
  structurally valid packed containers with declared `<= 0x4000`, and **13,189**
  with declared `<= 0x10000` (the host readers' `MAX_OUTPUT`).
- Run each to its own escape ignoring the declared size: `escape_length -
  declared_size = {0: 13162}` at the narrow cap and `{0: 13183}` at the wide cap,
  **never early, never late**; **6** containers are refused by the strict reader
  in both (`literal at output N overruns the declared N`, declared 1-2), and
  13,183/13,183 agree between two independent decoders.
- The second pass's independent re-measurement over the project's map-side
  reachability walk gives **4,322 / 4,322** with the same `{0: 4322}` distribution.
  Different population, same property.
- **Interpretation:** Webfoot's compressor always placed the escape exactly at
  the declared decompressed length. This is a property of the *data*, and the
  engine imposes none of it.
- **Caveat established here:** the claim that "the largest declared size in the
  reachable corpus is 0x4000" is false for the image as a whole, because the
  shipped dialogue container used in §2.5 declares **65,474**.

### 2.3 What the pre-fix PACKER does: `CONFIRMED`

`tools/webfoot/formats/webfoot_lz.pack` never emits the escape. Its token kinds
are literal / one / short / previous / long only. `_WordBitWriter.finish`
(`:490-495`) pads the final partial word with zeroes **only while `_count` is
non-zero**, so:

| Zero padding emitted by `pack` | Share of 32,202 synthetic payloads |
| --- | ---: |
| 0 (final token lands exactly on a word boundary) | 0.1% |
| 1..11 (escape needs bits from the following bytes) | 34.8% |
| >= 12 (the padding itself decodes as the escape) | 65.1% |

Deterministic named case: `pack(b"A" * 64)`, declared 64, fill 0, **0 padding
bits**, shipping reader OK, strict reader refuses. (One Phase-1 record gave this
case a packed length of 292; §7 corrects that figure to **12**.)

### 2.4 What the SHIPPING DECODER does: `CONFIRMED`

`webfoot_lz.unpack` / `_unpack_stream` (`:251`, `:313`) loops
`while len(out) < expected` and then requires the output to be *exactly*
`expected`, refusing an over-long match, an over-long raw run, a short stream and
a truncated stream. It does **not** require the escape. It is stricter than the
engine in every malformed case and different from it in exactly one respect: it
stops on the declared length, where the engine stops on the escape.

### 2.5 What the STRICT HOST DECODER requires: `CONFIRMED`

`tools/export/webfoot_strict.py` with `require_end_marker=True` (`:249-320`) runs
past the declared size to the stream's own escape and requires that escape to fall
at exactly the declared size. Every canonical container satisfies it; roughly a
third of `pack` outputs do not.

**Measured on the one shipped `pack` consumer.** `compressed_dialogue` re-packs
the whole 65,474-byte decoded dialogue container. Across **406** authored
replacements (each exactly the 16 UTF-16 code units the durable handle requires):

| | Count |
| --- | ---: |
| pack output fits the measured retail allocation (16,856 B), in-place branch | **0** |
| pack output 17,924..17,952 B, **relocation** branch into `0xFF`-filled expansion | **406** |
| relocation branch, escape inside our own output (padding >= 12) | 266 / 406 |
| **relocation branch, escape ABSENT (padding < 12; the following bytes are `0xFF`)** | **140 / 406 = 34.5%** |

Over 400 sampled canonical containers re-packed in place, only 8 fit and 6 of
those 8 would leave the decoder reading past the declared size.

The shipped target measured here is the `goku-greeting` line: the retail line
sits at `+0x132` and is 32 bytes, `'Good luck, Goku!'`; the selector-1 container's
table slot is `0x7B5B68` pointing to file offset `0x7A04F0`; the authored flush
payload used for the synthetic family is 64 bytes of `0x41`.

`require_end_marker=True` is used only on the read/export side; nothing under
`tools/webfoot/**` re-decodes a planned payload with it. `CONFIRMED`.

### 2.6 Cost of the separation

| | engine | canonical data | our `pack` | our shipping reader | our strict reader |
| --- | --- | --- | --- | --- | --- |
| stops on declared length | no | n/a | n/a | **yes** | no |
| stops on escape | **yes** | carries it at exactly the declared size | usually by accident | not required | **required at exactly the declared size** |
| output bound | none | n/a | n/a | yes (host policy) | yes (host policy) |
| over-long match | executes it | n/a | n/a | refused | refused |

---

## 3. Adjudication of every disagreement

### 3.1 One packed decoder or two byte-instances

One pass states there is one packed decoder and that the alternate `r2`-indexed
routines are a per-byte remapping path, not a second decoder.

**Returning to the bytes:** the decoder's exact 16-byte ARM head
`f0 4f 2d e9 08 50 a0 e3 00 a0 a0 e3 01 c0 a0 e3` occurs **twice** in the image,
at ROM `0x087B79E4` and at ROM `0x087B8644`. The veneer at `0x080491A8` carries
the literal `0x03000CA0` at `0x080491B0`, and `0x087B79A4 + 0xCA0 = 0x087B8644`
exactly. Disassembling `0x087B8644` shows the same prefix tree, the same bias
comparisons (`cmp ip,#64,#22` for `0x100`, `cmp ip,#0x7f`), the same thresholds in
its pool (`0x087B88E8 = 0x37FF`, `0x087B88EC = 0x027F`), the same 13 comparisons
with **zero** naming `r0`, and its own escape epilogue at `0x087B88E0` /
`0x087B88E4`. Its only functional difference is `ldrb r7,[r2,r7]` inserted before
the byte store at `0x087B8664` and `0x087B86DC`, a 256-byte output remap table.

**Ruling:** there are two byte-instances of the packed decoder, not one, and the
`r2`-indexed variant is a *remap variant of the packed decoder*, not the simple
lookup routine it was grouped with (`0x030002DC` = ROM `0x087B7C80` is that
separate simple routine). **The conclusion is unaffected**: both instances have
identical termination semantics and no length argument, so there is still exactly
one termination rule. The correction is factual, not a change of conclusion.

Also corrected here:
`webfoot_codec_reference.dispatcher_report()["iwram_blob"]["copied_bytes"] = 2050`
cannot be the blob's size while `0x03000CA0` is a reachable veneer target. True
extent `UNKNOWN`; the field must not be read as the blob length.

### 3.2 The sprite path is planned and unreachable today

One pass classified `sprite_graphics.plan_graphic_payload` as a shipped authoring
path. The audit says the sprite-payload path "has no GUI or CLI caller today".

**Returning to the call graph:** `plan_graphic_payload` is called only from
`graphics.py:543` (`plan_pixels`) and `graphics.py:613`. `plan_pixels` /
`apply_plan` have **no** caller under `tools/webfoot/workbench/`, the Workbench
graphics tab uses only `get_palette_override`, `set_palette_override`,
`remove_palette_override` and `get_palette_overrides`
(`graphics_tab.py:686, 1380, 1387, 1394`), and no CLI verb reaches
`plan_graphic_payload` or `plan_pixels` (`cli.py` has no match).

**Ruling:** `sprite_graphics.plan_graphic_payload` is **PLANNED / UNREACHABLE
TODAY**, not shipped. The live blast radius is **one** consumer, the compressed
dialogue build (`compressed_dialogue.py:111`, reached from `build.py:958-959`,
`dialogue.py`, `scene.py`). The `atlas_producers/scan.py:348, 416` uses are
**RESEARCH / QA ONLY**. This does not change the rule; it changes how much of the
product is exposed to it today.

### 3.3 Corpus population: 4,322 against 13,168, both correct, different populations

One pass re-measured the project's map-side reachability walk (4,322, gap
`{0: 4322}`). The other ran a blind structural scan (13,168 at declared
`<= 0x4000`, gap `{0: 13162}` plus 6 strict refusals).

**Ruling:** these count different populations and are not interchangeable; both
show the same property (escape at exactly the declared size, never early, never
absent, with a handful of structurally suspect headers in the larger blind set).
Neither figure should be quoted as "the" canonical corpus size. The blind scan is
larger because it does not require graph reachability; the walk is smaller because
it is the reachable set. The `0x4000` cap in the blind scan is the scan's own and
is known to exclude at least one real container (declared 65,474); a wide-cap
re-scan did not complete in this phase.

### 3.4 Padding probability: "1 of 64" against "65%"

One pass measured strict acceptance over `pack(b"\x41" * n)` for n = 1..64 and
found **1** accepted. The other measured over 32,202 payloads (random of sizes
1..1024, plus the `A`*n family) and found **65.1%** with padding >= 12.

**Returning to the measurement:** the `A`*n family is highly compressible, so its
token stream is short and its alignment is not representative; `pack(b"A"*2)`
finishes with `fill = 27`, that is **5** padding bits, below the 12 the escape
needs, hence that refusal. Over a spread of payloads the fill is near-uniform on
`0..31`, and the `>= 12` share is `20/32 = 62.5%` by construction, observed 65.1%.

**Ruling:** the `1/64` result is a property of one degenerate family, not of
`pack` in general. The representative figure is **~65% of `pack` outputs carry the
escape in their own padding; ~35% do not**. This strengthens, rather than weakens,
the audit's concern: the accident is common but far from guaranteed.

### 3.5 Over-reading past the payload: agreement

Both passes established that the engine's unconditional `ldrmi r6,[r1],#4` has no
input bound, so the escape need not lie inside the packed payload; the decoder
keeps consuming following image words until it sees twelve zero bits. Both also
stated that a marker-less stream therefore runs into whatever bytes follow. No
adjudication needed.

### 3.6 "Marker against declared size is UNRESOLVED" (prior notes): RESOLVED

`docs/research/LOGX_CODEC_PROVENANCE.md` §9 marks "which rule the hardware obeys"
as `UNRESOLVED` and `webfoot_codec_reference` transcribed the dispatcher.

**Ruling:** the prior `UNRESOLVED` was scoped to *corpus discriminability* and was
correctly scoped there. The instruction path is not ambiguous: there is no length
branch in the decoder for a length rule to occupy, so "precedence" is moot. One
pass sharpened this; the other reached it independently.

### 3.7 Comparison-count convention: no disagreement

One pass reports 28 comparisons over `0x087B79E4`..`0x087B7C5C`; the other reports
13 `cmp`/`cmn`/`tst`/`teq` plus 17 `subs` over `0x087B79E4`..`0x087B7C7C`. Both
ranges are stated, both give **zero** comparisons naming `r0`. The difference is
the helper `0x087B7C30`..`0x087B7C74`, included in one range and not the other,
and whether `subs` is counted as a comparison.

### 3.8 End-marker length: "seventeen bits" against twelve: TWELVE

`LOGX_CODEC_PROVENANCE.md` §8.4 says "seventeen bits of prefix and zeroes". The
instruction trace gives `3 + 7 + 2 = 12` zero bits, and both host readers
implement twelve (`webfoot_lz.py:279-288`, `webfoot_strict.py:276-285`). Twelve
is `CONFIRMED`; the seventeen is a documentation error.

Independently validated: the twelve-zero-bit model, evaluated with the engine's
own word-wise MSB-first bit order, predicted the strict reader's accept/refuse
outcome on **30/30** controlled trials (5 payloads x 6 trailing-byte patterns).

---

## 4. Where the repository's two claims live, and what must change

**Correct (engine = escape):**
`webfoot_lz.py:73-75`; `webfoot_codec_reference.py:14-17, 31-33`;
`LOGX_CODEC_PROVENANCE.md:649-653, 870, 878-882, 902-908`.

**Wrong (attributes declared-size stopping to the engine):**
- `tools/export/webfoot_strict.py:213-214`, "the decode stops as soon as the
  declared size is produced, **which is the engine's and the shipping decoder's
  rule**". This contradicts the same module's own docstring at `:62-67` ("the
  engine carries no output counter and performs no size comparison"). **The
  module contradicts itself**; that self-contradiction is the concrete artefact.
- `tests/unit/test_asset_export_strict_lz.py:159-160`, "**the engine stops at the
  declared size**, and the canonical corpus ... carries a marker at that size as
  well."

Note the audit cited the strict-module claim at `webfoot_strict.py:69-75`; at the
baseline those lines are the *correct* statement. The wrong sentence is at
`:213-214`. The losing assertions must be corrected **with their evidence rather
than deleted**.

---

## 5. Decision

**The ENGINE TERMINATES ON THE MARKER.**

Consequences for the write path:

1. `webfoot_lz.pack`'s postcondition ("a valid stream this module's own decoder
   reads back exactly") is insufficient for the retail engine. A stream must
   carry the escape at the declared size.
2. The cheapest sufficient guarantee, given what the engine actually requires, is
   **an explicit escape emitted after the final token**: `pack` should write the
   twelve zero bits itself rather than depending on `finish()`'s padding. That
   makes every output self-terminating regardless of alignment or of what follows
   it, and it costs at most one extra word of packed length.
3. Whichever route is chosen, every planned packed write should prove the
   postcondition, `webfoot_strict.unpack(..., require_end_marker=True)` on the
   planned payload, before it enters a plan. Expected-length host validation alone
   is not sufficient, by §2.4.
4. The losing assertions in §4 must be corrected with their evidence, not
   deleted.

**Recommended bounded change, not implemented here:** make `pack` emit the
decoder's own escape (twelve zero bits at the token boundary after the final
token) before word padding, then add a write-path guard that re-decodes every
planned packed payload with `require_end_marker=True`. Two focused tests should
fail before the change and pass after it: the flush payload (`pack(b"A" * 64)`)
must be strict-accepted, and the shipped dialogue target must be strict-accepted
for an authored replacement whose current output has `padding < 12` (for example
one of the 140 measured cases).

**Smallest next experiment, only if the runtime consequence is to be promoted
from `INFERRED`:** a bounded mGBA probe on a disposable derivative, with a small
declared size and a scratch destination, comparing a variant whose padding is
`>= 12` bits against one whose padding is `< 12` bits followed by `0xFF`; the
prediction under the marker rule is that the second runs past the declared size
and the first stops at it. This is a *consequence* experiment, not a rule
experiment, because the rule is already `CONFIRMED` statically.

---

## 6. Reproduction

The probes were run outside the repository, with no ROM writes and no ROM-derived
fixtures committed. They decode the canonical image with capstone 5.0.7 and cover
the decoder body, the IWRAM blob copy, the dispatcher callers, the byte-remap
variant, the canonical corpus, the flush payload, in-situ and shipped re-packs,
and the corpus pool constants. Focused validation ran by explicit file and node,
not as a full suite.

---

## 7. Correction: one measured figure in §2.3 was mis-transcribed

Recorded explicitly rather than edited into the evidence above, so a Phase-1
conclusion is never rewritten silently. **Nothing in the decision table changes**:
§2.3's conclusion (the pre-fix encoder does not emit the escape, and the flush
case has zero padding bits) is unaffected. One number is wrong.

§2.3 gives `pack(b"A" * 64)` a **packed byte length of 292**, and the same figure
appears in one investigation's own table. Re-measured against the untouched
pre-fix module
(`git show f02fb890bee9cb3ac955a4fdf4108e923093800a:tools/webfoot/formats/webfoot_lz.py`):

| Field | Phase-1 figure | Re-measured |
| --- | ---: | ---: |
| `pack(b"A" * 64)` packed length, header included | 292 | **12** |
| declared size | 64 | 64 |
| padding bits emitted by `finish()` | 0 | **0** |
| shipping `webfoot_lz.unpack` | OK, 64 bytes | OK, 64 bytes |
| strict marker-required reader, container alone | `ContainerError` | `ContainerError` |

The bytes are `02 00 00 00 40 00 00 00 fe 53 d0 20`. Every *property* §2.3 states
about the case holds; only the length is wrong.

**Where 292 came from.** The probe output's own session table shows 292 as the
packed length of the **256-byte** random payload in its first row, with
`fill = 0`, the same `fill` / `0 padding bits` pair the `A`*64 row reports. The
`A`*64 row immediately below it reads `packed byte length = 12 ... fill at finish
= 0; zero padding emitted = 0`. The figure was carried across rows; a 64-byte
payload cannot reach 292 bytes under this encoder, whose literal token is nine
bits.

The corrected figure is pinned as a frozen fixture in
`tests/unit/test_webfoot_lz.py` (`_A_TIMES_64_BEFORE_CQA_02`), together with its
post-fix counterpart, so the discriminator is exact in both directions.

---

## 8. Decoder disassembly detail from the two independent passes

Both passes disassembled the decoder and agreed on the structure below. Where the
two stated a different counting convention it is noted; no structural
disagreement remains.

### 8.1 Dispatcher and entry

```
0803d940  adds r2, r0, #0     ; r2 = source container (incoming r2 DISCARDED)
0803d942  adds r0, r1, #0     ; r0 = destination
0803d944  push {r3, lr}
0803d946  ldr  r3, [r2]       ; dispatch word = container[+0x00]
0803d948  adds r1, r2, #0
0803d94a  adds r1, #8         ; payload pointer = container + 8
0803d94c  cmp  r3, #0
0803d94e  beq  0x0803d95e     ; kind 0  -> stored memcpy branch
0803d950  cmp  r3, #1
0803d952  beq  0x0803d958     ; kind 1  -> packed decoder
0803d954  cmp  r3, #2
0803d956  bne  0x0803d95c     ; other   -> return, destination untouched
0803d958  bl   0x08049120     ; -> Thumb to ARM veneer -> IWRAM 0x03000040
0803d95c  pop  {r3, pc}
0803d95e  ldr  r2, [r2, #4]   ; declared size (used ONLY on the stored path)
0803d960  bl   0x08046d18     ; ROM ARM memcpy(dst, src, declared)
0803d964  b    0x0803d95c
```

- The veneer at `0x08049120` is bytes `78 47 c0 46 04 f0 1f e5 40 00 00 03`:
  `bx pc` / `nop` / `ldr pc,[pc,#-4]` / `.word 0x03000040`.
- The second dispatcher entry `0x0803D966` has exactly one caller, `0x0800F3D2`,
  and its arm is `0x0803D97E`. Its extra register `r2` is **not** a length: it is
  tested only with `cmp r2,#0` / `bne`, and on the non-NULL arm it is handed to
  two routines as a per-byte lookup table base (`ldrb r5,[r2,r5]` at
  `0x087B7C90`).
- Ten decoded Thumb `BL` sites reach the veneer: the two dispatcher arms
  `0x0803D958` and `0x0803D97E`, plus the eight direct callers above. None passes
  a length. Several compute a source that is *not* a standard container payload
  pointer: `record + 4` at `0x080040CE`, `0x08011FC8` and `0x08011FF6`; a
  table-loaded pointer at `0x08009B26` and `0x08030AFA`; and a strided
  destination at `0x08013ED6`. The engine therefore treats the packed decoder as a
  general headerless bitstream decoder, not as a container-only routine.
- An earlier accepted resource-graph census recorded four call sites,
  `0x08007C04`, `0x08007D4C`, `0x08009BF6` and `0x08009C5A`, and a nearby
  three-argument memcpy-like call at `0x080040C4`; these were not independently
  re-enumerated, and no argument or termination fact above depends on the caller
  count.
- The kind survives into the decoder and is the initial literal width:
  `mov r8, r3` at `0x087B79F8`.

### 8.2 Decoder prologue and register model

```
087b79e4  push {r4,r5,r6,r7,r8,sb,sl,fp,lr}
087b79e8  mov  r5, #8        ; distance_bits = 8
087b79ec  mov  sl, #0        ; 0 bits buffered, forces a word load
087b79f0  mov  ip, #1        ; previous_distance = 1
087b79f4  b    0x087b7a08    ; enter the token loop
```

| Reg | Role | Evidence |
| --- | --- | --- |
| `r0` | destination pointer, write cursor only | `strb r7,[r0],#1` post-increment stores |
| `r1` | source pointer | `ldrmi r6,[r1],#4` whole-word post-increment reads |
| `r6` | current 32-bit word, shifted MSB-first | `adds r6,r6,r6` |
| `sl` / r10 | bits remaining in word (reloads to `0x1f`/`0x20`) | `subs sl,sl,#1` / `movmi sl,#0x1f` |
| `ip` / r12 | distance / previous distance | `mov ip,r7`, `ldrb r8,[r0,-ip]` |
| `sb` / r9 | match or run count | `subs sb,sb,#1; bne` |
| `r5` | distance_bits (init 8) | `mov r5,#8` prologue |
| `r4` | literal base | `mov r4,r7` at the width escape |

**There is no output-limit register**, and there is no destination-end value in a
register to compare against. Three independent instruction-level checks are all
negative: the declared-size word sits at `[r1 - 4]` when `r1 = container + 8`, and
across the whole decoder there are 19 loads and 4 stores with **not one
negative-offset load from `r1`**; the decoder body contains **zero references to
`r2`**; and its only two literal loads are `ldr r8,[pc,#0xf0]` at `0x087B7BD4`
to `0x087B7CCC = 0x000037FF` and `ldr r8,[pc,#0xe4]` at `0x087B7BE4` to
`0x087B7CD0 = 0x0000027F`, both match-length bias thresholds.

### 8.3 Termination and writes

The token loop head is `0x087B7A08`, and every token path ends in an
unconditional `b 0x087B7A08`. One pass counted five such tails:
`0x087B7A98`, `0x087B7AC8`, `0x087B7B1C`, `0x087B7C18`, `0x087B7C2C`. The loop
never tests output length, so it cannot end by reaching a byte count. The only
structured exit is the escape:

```
087b7ad4  mov  r8, #7         ; 000-prefix: read the 7-bit short/control field
087b7ad8  bl   0x087b7c30     ; -> r7
087b7adc  cmp  r7, #0
087b7ae0  beq  0x087b7b00     ; field == 0 : control escape
087b7b00  mov  r8, #2         ; read the 2-bit width field
087b7b04  bl   0x087b7c30     ; -> r7
087b7b08  cmp  r7, #0
087b7b0c  beq  0x087b7c78     ; width == 0 : END MARKER, return
087b7c78  pop  {r4,r5,r6,r7,r8,sb,sl,fp,lr}
087b7c7c  bx   lr
```

`0x087B7C74 bx lr` and `0x087B7C34 ldreq` / `0x087B7C5C bxeq lr` belong to the
bit-fetch helper `0x087B7C30`, whose own body is `0x087B7C30`..`0x087B7C74`, not
to the decode loop. The decode loop's sole exit is the escape at `0x087B7C78`.

```
087b7a04  strb r7, [r0], #1   ; literal / widened-base byte
087b7a78  strb r7, [r0], #1   ; raw-literal-run byte
087b7c0c  strb r8, [r0], #1   ; match copy write (loop 0x087b7c08)
087b7c20  strb r8, [r0], #1   ; match copy write (loop 0x087b7c1c)
087b7acc  ldrb r7, [r0, -r7]  ; back-reference read
087b7c08  ldrb r8, [r0, -ip]  ; back-reference read
```

Every byte is written by an unconditional post-increment store. A census of every
comparison in the decoder finds **zero comparisons naming `r0`**: 13
`cmp`/`cmn`/`tst`/`teq` plus 17 `subs` over `0x087B79E4`..`0x087B7C7C` (the other
pass counted 28 comparisons over `0x087B79E4`..`0x087B7C5C`, the same set under a
different range and counting convention). The compared registers are the bit
counter `sl`, the field width `r8`, the count `sb`, the distance `ip`, the literal
width `r3` and the two bias thresholds. **Bound: none, `CONFIRMED` by positive
census rather than by absence of evidence.**

The marker is, at a token boundary, MSB-first: bit 0 = 0 (not a literal), bit 1 =
0 (not a long match), bit 2 = 0 (seven-bit short/control form), bits 3..9 =
`0000000` (7-bit distance field 0, control escape), bits 10..11 = `00` (2-bit
width field 0, end marker). **Exactly 12 consecutive zero bits at a token
boundary.**

### 8.4 The second byte-instance and the simple remap routine

| Path | Entry | Source | Length argument | Termination |
| --- | --- | --- | --- | --- |
| Container dispatcher | `0x0803D940` kind 1/2 to `0x0803D958` | `container + 8` | none | escape |
| Second dispatcher entry | `0x0803D966` to `0x0803D97E` | `container + 8` | none (`r2` is only tested for NULL, then used as a byte-remap table pointer) | escape |
| Eight direct callers | veneer `0x08049120` | computed per caller (`record+4`, table pointer, ...) | none | escape |
| Second decoder copy (byte-remap variant) | ARM `0x087B8644` = IWRAM `0x03000CA0`, via veneer `0x080491A8` | same | none | escape |
| Simple byte-remap decode | ARM `0x087B7C80` = IWRAM `0x030002DC`, via veneer `0x0804918C` | table-driven | n/a | not a packed token loop |

The simple routine's per-byte lookup uses `ldrb r5,[r2,r5]` at `0x087B7C90`.

A note-size correction: `tools/research/webfoot_codec_reference.py` records
`iwram_blob.copied_bytes: 2050` (`0x802`). That cannot be the whole blob, because
the veneer at `0x080491A8` carries the literal `0x03000CA0` at `0x080491B0`,
which is `0xCA0` bytes past the blob base, and ROM `0x087B79A4 + 0xCA0 =
0x087B8644` is exactly the variant's head. Either the copy is contiguous and
longer than 2050 bytes, or a second copy exists that the module does not record.
The DMA setup was not located, so the true extent is **UNKNOWN** and the field
must not be read as the blob's size.
