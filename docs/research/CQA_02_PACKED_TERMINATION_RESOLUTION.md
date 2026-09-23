# CQA-02: Packed-stream termination: reconciliation and resolution

**CQA-02-PACKED-STREAM-TERMINATION-001, Phase 1 (evidence resolution).**
Adjudicated by the ticket owner after both independent investigations froze.

- Baseline: `origin/master` at `659db0ec3a996ea0338354c5162454981c8adff5`.
- Investigator A (a local reviewer) memo: [`CQA_02_PACKED_TERMINATION_DEEPSEEK.md`](CQA_02_PACKED_TERMINATION_DEEPSEEK.md)
- Investigator B (the reviewer) memo: [`CQA_02_PACKED_TERMINATION_<local-state-name>`](CQA_02_PACKED_TERMINATION_<local-state-name>)
- Canonical ROM SHA-256 `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`,
  8,388,608 bytes, verified before and after; unchanged. No production code
  changed; no ROM-derived fixture added; WORKBENCH-006 untouched.
- The two investigations were run in separate worktrees
  (`<temp>\log1-remake-cqa-02-evidence`, `<temp>\log1-remake-cqa-02-the reviewer`), each
  detached at the baseline, neither able to read the other's notes.

This document does not vote between the reports. Every point where they differ
is taken back to the instructions or to a rerun of the measurement.

---

## 1. Headline

**The retail engine terminates a packed stream at an explicit escape in the
bitstream, twelve consecutive zero bits read at a token boundary, and by
nothing else. `CONFIRMED` by two independent disassemblies of the canonical
image, plus a positive census showing no comparison against the destination
cursor anywhere in the decoder.**

This is **CASE A** of the ticket's decision table.

The audit's "two mutually exclusive engine termination rules" is real but is not
an engine ambiguity: one claim is about the engine, the other is about the host
tool, and the canonical corpus satisfies both at once, which is how the host
rule came to be mislabelled as the engine's.

---

## 2. The five separate facts

The ticket requires these to be stated separately. They are.

### 2.1 What the ENGINE does: `CONFIRMED`

| Item | Value |
| --- | --- |
| Entry | ARM `0x087B79E4` = IWRAM `0x03000040`, via Thumb→ARM veneer `0x08049120` (literal `0x03000040` at `0x08049128`) |
| Dispatcher | Thumb `0x0803D940`; second entry `0x0803D966` (1 caller: `0x0800F3D2`) |
| Call sites | dispatcher arms `0x0803D958` / `0x0803D97E`, plus **eight direct callers** of the veneer: `0x080040D2`, `0x08009B2C`, `0x08011FCE`, `0x08011FFA`, `0x08013EDE`, `0x0802800E`, `0x080280D4`, `0x08030AFC` |
| Arguments | exactly `(source, destination)`. `0803d940 adds r2, r0, #0` discards the incoming `r2`; no length survives |
| Input pointer | `r1 = container + 8` |
| Output pointer | `r0` = destination, write cursor only |
| Declared size read by the retail packed path | **NO**: `ldr r2,[r2,#4]` at `0x0803D95E` is on the kind-0 *stored* branch only; the decoder has zero references to `r2`, zero negative-offset loads from `r1`, and only the two bias constants (`0x087B7CCC = 0x37FF`, `0x087B7CD0 = 0x027F`) in its literal pool |
| Termination | the escape: `000` prefix → 7-bit field `0` → 2-bit selector `0`; detected at `0x087B7AD4`/`0x087B7B00`; the loop's **sole** exit is `0x087B7C78` (`pop {r4,r5,r6,r7,r8,sb,sl,fp,lr}` / `0x087B7C7C bx lr`) |
| Write | `strb rX,[r0],#1` at `0x087B7A04`, `0x087B7A78`, `0x087B7C0C`, `0x087B7C20`; back-references read `ldrb rX,[r0,-rN]` |
| Bound | **NONE**: of the 13 comparisons in `0x087B79E4`..`0x087B7C7C` (+17 `subs`), **zero name `r0`**. Compared registers are the bit counter, field width, count, distance, literal width and the bias thresholds |
| Multiplicity | **two byte-instances of the same decoder** (see §3.1). Same grammar, same termination rule. No caller supplies a length, so no caller can impose length termination |

### 2.2 What CANONICAL WEBFOOT DATA does: `CONFIRMED` for the corpus

- Blind scan of the whole image (header kind 1/2, declared in range, kept only
  when the shipping decoder then produces exactly that many bytes): **13,168**
  structurally valid packed containers with declared `<= 0x4000`, and **13,189**
  with declared `<= 0x10000` (the host readers' `MAX_OUTPUT`).
- Run each to its own escape ignoring the declared size: `escape_length −
  declared_size = {0: 13162}` at the narrow cap and `{0: 13183}` at the wide cap,
  **never early, never late**; **6** containers are refused by the strict reader
  in both (`literal at output N overruns the declared N`, declared 1–2), and
  13,183/13,183 agree between two independent decoders.
- the reviewer's independent re-measurement over the project's map-side reachability
  walk gives **4,322 / 4,322** with the same `{0: 4322}` distribution. Different
  population, same property.
- **Interpretation:** Webfoot's compressor always placed the escape exactly at
  the declared decompressed length. This is a property of the *data*, and the
  engine imposes none of it.
- **Caveat established here:** the claim that "the largest declared size in the
  reachable corpus is 0x4000" is false for the image as a whole, the shipped
  dialogue container used in §2.5 declares **65,474**.

### 2.3 What OUR CURRENT PACKER does: `CONFIRMED`

`tools/webfoot/formats/webfoot_lz.pack` never emits the escape. Its token kinds
are literal / one / short / previous / long only. `_WordBitWriter.finish`
(`:490-495`) pads the final partial word with zeroes **only while `_count` is
non-zero**, so:

| Zero padding emitted by `pack` | Share of 32,202 synthetic payloads |
| --- | ---: |
| 0 (final token lands exactly on a word boundary) | 0.1% |
| 1..11 (escape needs bits from the following bytes) | 34.8% |
| >= 12 (the padding itself decodes as the escape) | 65.1% |

Deterministic named case: `pack(b"A" * 64)` → 292 packed bytes, declared 64,
fill 0, **0 padding bits**, shipping reader OK, strict reader refuses.

### 2.4 What OUR SHIPPING DECODER does: `CONFIRMED`

`webfoot_lz.unpack` / `_unpack_stream` (`:251`, `:313`) loops `while len(out) <
expected` and then requires the output to be *exactly* `expected`, refusing an
over-long match, an over-long raw run, a short stream and a truncated stream. It
does **not** require the escape. It is stricter than the engine in every
malformed case and different from it in exactly one respect: it stops on (B) the
declared length, where the engine stops on the escape.

### 2.5 What the STRICT HOST DECODER requires: `CONFIRMED`

`tools/export/webfoot_strict.py` with `require_end_marker=True` (`:249-320`)
runs past the declared size to the stream's own escape and requires that escape
to fall at exactly the declared size. Every canonical container satisfies it;
roughly a third of `pack` outputs do not.

**Measured on the one shipped `pack` consumer.** `compressed_dialogue` re-packs
the whole 65,474-byte decoded dialogue container. Across **406** authored
replacements (each exactly the 16 UTF-16 code units the durable handle requires):

| | Count |
| --- | ---: |
| pack output fits the measured retail allocation (16,856 B) → in-place branch | **0** |
| pack output 17,924..17,952 B → **relocation** branch into `0xFF`-filled expansion | **406** |
| relocation branch, escape inside our own output (padding >= 12) | 266 / 406 |
| **relocation branch, escape ABSENT (padding < 12; the following bytes are `0xFF`)** | **140 / 406 = 34.5%** |

Over 400 sampled canonical containers re-packed in place, only 8 fit and 6 of
those 8 would leave the decoder reading past the declared size.

`require_end_marker=True` is used only on the read/export side; nothing under
`tools/webfoot/**` re-decodes a planned payload with it. `CONFIRMED`.

### 2.6 Cost of the separation

| | engine | canonical data | our `pack` | our shipping reader | our strict reader |
| --- | --- | --- | --- | --- | --- |
| stops on declared length | no | n/a | n/a | **yes** | no |
| stops on escape | **yes** | carries it at exactly (B) | usually by accident | not required | **required at exactly (B)** |
| output bound | none | n/a | n/a | yes (host policy) | yes (host policy) |
| over-long match | executes it | n/a | n/a | refused | refused |

---

## 3. Adjudication of every disagreement

### 3.1 "One packed decoder" vs "two byte-instances": INVESTIGATOR B IMPRECISE

the reviewer's §3 states there is one packed decoder and that the alternate
`r2`-indexed routines are a per-byte remapping path, not a second decoder.

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
lookup routine the reviewer grouped it with (`0x030002DC` = ROM `0x087B7C80` is that
separate simple routine). **The conclusion is unaffected**: both instances have
identical termination semantics and no length argument, so there is still exactly
one termination rule. the reviewer's INFERRED-level statement is corrected at the
factual level, not the conclusion level.

Also corrected here: `webfoot_codec_reference.dispatcher_report()["iwram_blob"]
["copied_bytes"] = 2050` cannot be the blob's size while `0x03000CA0` is a
reachable veneer target. True extent `UNKNOWN`; the field must not be read as the
blob length.

### 3.2 Sprite path: "shipped" vs "unreachable today": INVESTIGATOR B IMPRECISE, AUDIT CORRECT

the reviewer's §8 classifies `sprite_graphics.plan_graphic_payload` as a **SHIPPED
AUTHORING PATH**. The audit says the sprite-payload path "has no GUI or CLI
caller today".

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

### 3.3 Corpus population: 4,322 vs 13,168: BOTH CORRECT, DIFFERENT POPULATIONS

the reviewer re-measured the project's map-side reachability walk (4,322, gap
`{0: 4322}`). Investigator A ran a blind structural scan (13,168 at declared
<= 0x4000, gap `{0: 13162}` plus 6 strict refusals).

**Ruling:** these count different populations and are not interchangeable; both
show the same property (escape at exactly the declared size, never early, never
absent, with a handful of structurally-suspect headers in the larger blind set).
Neither figure should be quoted as "the" canonical corpus size. The blind scan is
larger because it does not require graph reachability; the walk is smaller
because it is the reachable set. The 0x4000 cap in the blind scan is Investigator
A's own and is known to exclude at least one real container (declared 65,474);
a wide-cap re-scan did not complete in this phase.

### 3.4 Padding probability: "1 of 64" vs "65%": INVESTIGATOR B'S FAMILY IS DEGENERATE

the reviewer's §7 measured strict acceptance over `pack(b"\x41" * n)` for n = 1..64 and
found **1** accepted. Investigator A measured over 32,202 payloads (random of
sizes 1..1024, plus the `A`*n family) and found **65.1%** with padding >= 12.

**Returning to the measurement:** the `A`*n family is highly compressible, so its
token stream is short and its alignment is not representative; `pack(b"A"*2)`
finishes with `fill = 27`, i.e. **5** padding bits, below the 12 the escape needs
; hence the reviewer's refusal. Over a spread of payloads the fill is near-uniform on
`0..31`, and the `>= 12` share is `20/32 = 62.5%` by construction, observed 65.1%.

**Ruling:** the reviewer's `1/64` is a property of one degenerate family, not of `pack`
in general. The representative figure is **~65% of `pack` outputs carry the
escape in their own padding; ~35% do not**. This strengthens, rather than
weakens, the audit's concern: the accident is common but far from guaranteed.

### 3.5 Over-reading past the payload: AGREEMENT, both reached it independently

Both investigators established that the engine's unconditional
`ldrmi r6,[r1],#4` has no input bound, so the escape need not lie inside the
packed payload; the decoder keeps consuming following image words until it sees
twelve zero bits. Both also stated that a marker-less stream therefore runs into
whatever bytes follow. No adjudication needed.

### 3.6 "Marker vs declared size is UNRESOLVED" (prior notes): RESOLVED, the reviewer CORRECT

`docs/research/LOGX_CODEC_PROVENANCE.md` §9 marks "which rule the hardware obeys"
as `UNRESOLVED` and `webfoot_codec_reference` transcribed the dispatcher.

**Ruling:** the prior `UNRESOLVED` was scoped to *corpus discriminability* and
was correctly scoped there. The instruction path is not ambiguous: there is no
length branch in the decoder for a length rule to occupy, so "precedence" is
moot. the reviewer's sharpening stands; the a local reviewer memo reaches it independently.

### 3.7 Comparison-count convention: NO DISAGREEMENT

the reviewer reports 28 comparisons over `0x087B79E4..0x087B7C5C`; Investigator A
reports 13 `cmp`/`cmn`/`tst`/`teq` plus 17 `subs` over
`0x087B79E4..0x087B7C7C`. Both ranges are stated, both give **zero** comparisons
naming `r0`. The difference is the helper `0x087B7C30`..`0x087B7C74`, included in
one range and not the other, and whether `subs` is counted as a comparison.

### 3.8 End-marker length: "seventeen bits" (prior note) vs twelve: TWELVE

`LOGX_CODEC_PROVENANCE.md` §8.4 says "seventeen bits of prefix and zeroes". The
instruction trace gives `3 + 7 + 2 = 12` zero bits, and both host readers
implement twelve (`webfoot_lz.py:279-288`, `webfoot_strict.py:276-285`). Twelve
is `CONFIRMED`; the seventeen is a documentation error for Phase 2 to correct.

Independently validated: the twelve-zero-bit model, evaluated with the engine's
own word-wise MSB-first bit order, predicted the strict reader's accept/refuse
outcome on **30/30** controlled trials (5 payloads × 6 trailing-byte patterns).

---

## 4. Where the repository's two claims live, and what must change in Phase 2

**Correct (engine = escape):**
`webfoot_lz.py:73-75`; `webfoot_codec_reference.py:14-17, 31-33`;
`LOGX_CODEC_PROVENANCE.md:649-653, 870, 878-882, 902-908`.

**Wrong (attributes declared-size stopping to the engine):**
- `tools/export/webfoot_strict.py:213-214`, "the decode stops as soon as the
  declared size is produced, **which is the engine's and the shipping decoder's
  rule**". This contradicts the same module's own docstring at `:62-67` ("the
  engine carries no output counter and performs no size comparison"). **The
  module contradicts itself**; that self-contradiction is the concrete artefact.
- `tests/unit/test_asset_export_strict_lz.py:159-160`, "**the engine stops at
  the declared size**, and the canonical corpus … carries a marker at that size
  as well."

Note the audit cited the strict-module claim at `webfoot_strict.py:69-75`; at
`659db0ec` those lines are the *correct* statement. The wrong sentence is at
`:213-214`. Phase 2 must correct the loser **with its evidence rather than delete
it**, per the ticket's Required Work item 3.

---

## 5. Decision

**CASE A: ENGINE TERMINATES ON MARKER.**

Consequences recorded for Phase 2, **not implemented here**:

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
   planned payload, before it enters a plan. Expected-length host validation
   alone is not sufficient, by §2.4.
4. The losing assertions in §4 must be corrected with their evidence, not
   deleted.
5. `ROM-CAPACITY-AND-ALLOCATION-001` stays **BLOCKED** until the must-fix set
   closes; this phase does not unblock it.

**Recommended Phase-2 change, bounded and not implemented here:** make `pack`
emit the decoder's own escape (twelve zero bits at the token boundary after the
final token) before word padding, then add a write-path guard that re-decodes
every planned packed payload with `require_end_marker=True`. Two focused tests
should fail before the change and pass after it: the flush payload
(`pack(b"A" * 64)`) must be strict-accepted, and the shipped dialogue target must
be strict-accepted for an authored replacement whose current output has
`padding < 12` (e.g. one of the 140 measured cases).

**Smallest next experiment, only if the owner wants the runtime consequence
promoted from `INFERRED`:** a bounded mGBA probe on a disposable derivative, with
a small declared size and a scratch destination, comparing a variant whose
padding is `>= 12` bits against one whose padding is `< 12` bits followed by
`0xFF`; the prediction under CASE A is that the second runs past the declared
size and the first stops at it. This is a *consequence* experiment, not a rule
experiment, the rule is already `CONFIRMED` statically.

---

## 6. Reproduction and artefacts

Probes (outside the repository, no ROM writes, no ROM-derived fixtures):
`<temp>\cqa02\probe_decoder.py`, `probe_blob.py`, `probe_static.py`,
`probe_callers.py`, `probe_variant.py`, `probe_multi.py`, `probe_corpus.py`,
`probe_flush.py`, `probe_insitu.py`, `probe_shipped.py`, `probe_dialogue.py`,
`check_pool.py`. Investigator B's probes are recorded in its memo's Reproduction
section and live outside the repository.

Focused validation run in this phase (no full suite, per standing policy) is
recorded in the ticket's final report. `git diff --check` result and the exact
worktree state are recorded there too.

**Baseline note.** The session checkout `<checkout>` is on branch
`workbench-006` at `b4b13c9`, an ancestor of the ticket's `659db0ec`, with 132
modified paths; it is **not** the ticket baseline. All work here was done in the
detached baseline worktrees under `C:\tmp`, consistent with the audit's own
record that "the dirty WORKBENCH-006 checkout was never read as the baseline and
was never touched". WORKBENCH-006 remains untouched.

---

## 7. Phase-2 correction: one measured figure in §2.3 was mis-transcribed

Recorded explicitly rather than edited into the evidence above, per the ticket's
requirement not to rewrite Phase-1 conclusions silently. **Nothing in the decision
table changes**: §2.3's conclusion (the pre-fix encoder does not emit the escape,
and the flush case has zero padding bits) is unaffected. One number is wrong.

§2.3 and the a local reviewer memo's §6 table (`CQA_02_PACKED_TERMINATION_DEEPSEEK.md`
line 346) both give `pack(b"A" * 64)` a **packed byte length of 292**. Re-measured
in Phase 2 against the untouched pre-fix module
(`git show 659db0ec3a996ea0338354c5162454981c8adff5:tools/webfoot/formats/webfoot_lz.py`):

| Field | Phase-1 figure | Re-measured |
| --- | ---: | ---: |
| `pack(b"A" * 64)` packed length, header included | 292 | **12** |
| declared size | 64 | 64 |
| padding bits emitted by `finish()` | 0 | **0** |
| shipping `webfoot_lz.unpack` | OK, 64 bytes | OK, 64 bytes |
| strict marker-required reader, container alone | `ContainerError` | `ContainerError` |

The bytes are `02 00 00 00 40 00 00 00 fe 53 d0 20`. Every *property* §2.3 states
about the case holds; only the length is wrong.

**Where 292 came from.** The investigator's own probe output, `<temp>\cqa02\flush.txt`
section B, shows 292 as the packed length of the **256-byte** random payload in the
first row of that section, with `fill = 0` - the same `fill`/`0 padding bits` pair
the A*64 row reports. The A*64 row immediately below it reads
`packed byte length = 12 ... fill at finish = 0; zero padding emitted = 0`. The
figure was carried across rows; a 64-byte payload cannot reach 292 bytes under this
encoder, whose literal token is nine bits.

The corrected figure is pinned as a frozen fixture in
`tests/unit/test_webfoot_lz.py` (`_A_TIMES_64_BEFORE_CQA_02`), together with its
post-fix counterpart, so the discriminator is exact in both directions.
