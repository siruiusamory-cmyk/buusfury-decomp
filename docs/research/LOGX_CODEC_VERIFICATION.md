# LOGX codec verification

The Buu's Fury Webfoot container and compression semantics, canonicalized
against the canonical image. Static analysis only; no runtime capture was made
for this pass.

Canonical ROM SHA-256, before and after:
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

Evidence document: [`LOGX_CODEC_PROVENANCE.md`](LOGX_CODEC_PROVENANCE.md).
Tooling: `tools/research/logx_codec_probe.py`.
## EXTERNAL CLAIMS TESTED

| Claim (mainant/LOGExtractor) | Result |
| --- | --- |
| older `Gba/JCALG1.cs`: a leading zero wrapper word means approximately "empty data" | **REFUTED as a general rule**, it is the stored branch, and the copy length is the second word |
| later MapViewer / ImageScan / CharacterSpriteExtractor: a leading zero word means the following declared-size bytes are stored raw | **CONFIRMED**, with the correction that the length is `container[+0x04]`, not whatever the reader assumed |
| `UnknownHeader`: skip four bytes, decode compressed data with no ordinary wrapper, run to a codec end marker, into a ~64 KiB temporary buffer | **REFUTED as a container form**; the four bytes belong to engine records. The 64 KiB figure is host-tool convenience, **not** an engine limit |
| the codec is JCALG1 (or a JCALG1-derived LZSS) | **PARTIALLY CONFIRMED** as "JCALG1-like / derived, engine-consistent". The name is not promoted |
| `0x179764` is global graphics/tile-source data | already corrected by LOGX-TILE-001; re-confirmed as the `root + 0x4C` bank table |

Both external readings of the zero first word were, in fact, describing the
*same* engine branch from opposite ends. That is the record's central
disagreement result and it is not a case of one tool being right.

---

## ENGINE DECODE ENTRY POINTS

| Address | Kind | Role | Callers |
| --- | --- | --- | --- |
| `0x0803D940` | Thumb | **wrapper dispatcher**, reads `container[+0x00]`, chooses a form | 57 Thumb `BL` callers, including `0x08007C04`, `0x08007D4C`, `0x08009BF6`, `0x08009C5A` |
| `0x0803D966` | Thumb | a **second** dispatcher entry; its `r2` is a lookup-table pointer, not a length | exactly one: `0x0800F3D2` |
| `0x08046D18` | ARM in ROM | the **stored-branch memcpy** | `0x0803D960` |
| `0x08049120` | Thumb->ARM stub | `bx pc ; nop ; ldr pc,[pc,#-4] ; .word 0x03000040` | `0x0803D958`, `0x0803D97E` |
| `0x08049138` | Thumb->ARM stub | -> IWRAM `0x03000768` (block memcpy) | `0x0803D986` |
| ROM `0x087B79E4` = IWRAM `0x03000040` | ARM | **the packed decoder**, copied to IWRAM by the startup DMA3 | the kind-1/2 arm of the dispatcher |

Caller enumeration method: a raw halfword `BL`/`BLX` scan of **every even offset**
over the whole image, **17,748** encoding pairs (35,496 halfwords; each Thumb
BL/BLX *pair* is one encoding), **9,624** distinct targets, finds **57** callers
of `0x0803D940`.

**The every-even-offset walk is required, not a convenience.** The same scan on a
stride-4 walk finds only **8,838** encoding pairs and only **30** of the 57
callers: 27 of the 57 sites sit at address ≡ 2 (mod 4), including two of the four
accepted sites this record names (`0x08009BF6`, `0x08009C5A`). Any enumeration
that reports 57 must be an every-even-offset walk. (Independent review re-ran the
same scan counting individual *halfwords* rather than pairs and reported
33,960 / 17,299 for the two strides, twice these figures, as expected, with the
same 57 / 30 caller counts. The `8,838 / 8,266 / 4,440` figures an earlier
revision quoted here came from a different scan; the 4,440 cannot be reproduced
and is not used.)

`0x0803D940`'s first instruction is `adds r2, r0, #0`, which discards its
incoming third argument: it takes exactly **(source, destination)** and never
sees an output length or a declared size on the packed path.

**Correction to an earlier revision of this record.**
LOGX-TILE-001 phrased this as "the decompressor takes exactly two arguments";
that is true of `0x0803D940`. An earlier revision of this record claimed
`0x0803D966` was a **length-aware** variant. It is not: `r2` is only tested for
NULL (`0x0803D972 cmp r2,#0` / `0x0803D974 bne`) and is then handed to alternate
decode routines as a **table pointer** for a per-byte lookup, so its non-NULL
branch is a remapping path. It has exactly one `BL` caller (`0x0800F3D2`), not
none.

The decoder itself runs from IWRAM. `0x08049120`..`0x080491CC` (172 bytes) holds
**15** Thumb->ARM stubs: 13 in the `ldr pc` form (12-byte slots) and 2 branch
stubs at `0x08049198` and `0x080491A0` (8-byte slots). The blob's ROM base is
**CONFIRMED**, not inferred: the startup code programs DMA3 from the literals at
`0x08000148`/`0x0800014C`/`0x08000150`. The source literal is `0x087B79A4`, the
destination literal is `0x03000000`, and the count literal `0x00001007` is built
into the register at `0x08000118`..`0x08000124` (`lsrs r1, r1, #2` then
`orr r1, r1, #0x84000000`) and stored 32-bit at `0x040000DC`. So `CNT_L = 0x0401`
= **1,025 units** and `CNT_H = 0x8400`, whose bit 10 selects **32-bit units**:
**4,100 bytes** are copied. (That length is what makes the stub table's own IWRAM
`0x03000CA0` row reachable at all - blob offset `0xCA0` is 3,232.) ROM
`0x087B79E4` is therefore IWRAM `0x03000040`, which is exactly the stub target,
and its first word is `f0 4f 2d e9` = ARM `push {r4-r11, lr}`. An earlier revision
placed the decoder at `0x087B7A9C` (base + `0xF8`); that is an interior bit-loop
label, not an entry.

---

## WRAPPER FORMS

Exactly three values the engine consumes, from `0x0803D94C`..`0x0803D956`:

| Form | Meaning |
| --- | --- |
| `container[+0x00] == 0` | stored: `memcpy(dst, container + 8, container[+0x04])` |
| `container[+0x00] == 1` | packed stream, literal width from the dispatch word |
| `container[+0x00] == 2` | packed stream, same decoder |
| any other value | return with the destination **untouched** |

## ORDINARY WRAPPER LAYOUT

```text
+0x00  u32 LE  dispatch word (0 stored, 1 and 2 packed)
+0x04  u32 LE  declared decoded size, excluding the wrapper
+0x08  ...      payload: stored bytes, or the packed bitstream
```

## FIRST WORD

A **form selector**, and its value is used arithmetically, not merely compared:
kind 1 and kind 2 both enter the packed decoder. It is not a tag, a magic, or a
length. **CONFIRMED.**

## FIRST-WORD-ZERO SEMANTIC

**Selects the stored branch: copy `container[+0x04]` bytes from `container + 8`.**
It does not mean "empty", "sentinel" or "error", and it is not caller- or
class-dependent. When the second word is zero the copy is indeed empty, which is
how the older external reading arose.

*Canonically observed instances (reachable from the accepted resource graphs):*
**2**, both `root + 0x48` selector streams declaring 4 bytes:

| Address | Referencing root | Wrapper words | Decoded SHA-256 |
| --- | --- | --- | --- |
| `0x082B5F1C` | `0x082B5F28` | `0`, `4` | `9c14ff2232b3d3427a3197aa999afadc58d36c2c3f855c9efcd5f1675291997a` |
| `0x082B5F94` | `0x082B5FA0` | `0`, `4` | `b98a002565f52a2b53593a390fdcfd620a4e5783d545779e5fbbac207e995101` |

*Engine-supported and engine-installed instance:* `0x08070808`, form 0,
declared 0, followed by **2,040 (`0x7F8`) zero bytes** (the first non-zero byte is
`0xFF` at `+0x800`), is what the dominant-layer constructor stores into its four
resident-slot pointers before installing anything (LOGX-TILE-001 §4.4).

## DECODED SIZE FIELD

`container[+0x04]`, `u32` little-endian, decoded-output length excluding the
8-byte wrapper. Zero is legal and the engine installs one. Read at `0x0803D95E`
on the stored path only.

## DECODED SIZE SEMANTIC

| Question | Answer |
| --- | --- |
| stored form copies exactly this many bytes | **yes** |
| packed form produces exactly this many bytes | **yes, on 4,322 / 4,322 reachable packed containers** |
| the stream's own end marker falls at this length | **yes, on 4,322 / 4,322** (`end-marker length − declared size` is `{0: 4322}`) |
| mismatch detected by the engine | **no**, the engine has no size comparison at all |

## RAW FORM

**CONFIRMED.** Discriminator: `container[+0x00] == 0`. Payload offset: `+0x08`.
Copy routine: the ROM-resident ARM memcpy at `0x08046D18`, invoked from
`0x0803D960` with `r0` = destination, `r1` = `container + 8`, `r2` =
`container[+0x04]`. Exact byte count: the declared size, unrounded and unpadded.
No alignment requirement is imposed on the payload. (The *second* dispatcher
entry's stored branch uses the Thumb->ARM stub at `0x08049138`, which resolves
to IWRAM `0x03000768`.)

## RAW PAYLOAD OFFSET

`+0x08`.

## RAW COPY SEMANTIC

A flat little-endian byte copy of exactly `container[+0x04]` bytes. No
transformation, no stride, no padding, no destination bound.

## COMPRESSED FORM

**CONFIRMED** on 4,322 canonical containers. Wrapper: form 1 (or 2), declared
size at `+0x04`. Stream start: `+0x08`. Source reads are whole 32-bit
little-endian words, so the stream occupies a whole number of words and the
engine over-reads up to three bytes past the last token.

## COMPRESSED PAYLOAD OFFSET

`+0x08`.

## CODEC IDENTITY

**PARTIALLY CONFIRMED** as **"JCALG1-like / derived, engine-consistent"**.

The project will not state *byte-compatible JCALG1*: no pinned JCALG1 reference
implementation was compared byte-for-byte, and a class name is not evidence. What
is **CONFIRMED** is the grammar actually used by the canonical image's
containers, established by a whole-corpus differential. Two engine constants that
the grammar shares were read out of the IWRAM blob's own literal pool:
`0x087B7CCC = 0x37FF` and `0x087B7CD0 = 0x027F`.

## LITERAL SEMANTICS

Prefix bit `1`, then one value of `literal_bits` bits, added to `literal_base`
and truncated to a byte. **CONFIRMED** by differential.

## BACKREFERENCE SEMANTICS

Long match: prefix `0 1`, then

```text
distance_code = gamma()
if distance_code == 2:  copy(previous_distance, gamma())
distance = get(distance_bits) + ((distance_code - 3) << distance_bits)
count    = gamma()
bias:  distance >= 0x10000 -> +3
       distance >= 0x037FF -> +2
       distance >= 0x0027F -> +1
       distance <= 0x0007F -> +4
```

**Field order is distance code, then low distance bits, then count** -
**CONFIRMED** by measurement: the other order desynchronises the canonical chunk
at `0x0817C144` on its fourth token and yields a 326-byte back-reference into a
26-byte output. The two orders agree only when the distance code is exactly 3.

Short match: prefix `0 0 0` then a seven-bit distance, `count = get(2) + 2`.
Four-bit copy: prefix `0 0 1` then `1..15`, where `1` writes `literal_base` and
`n >= 2` copies one byte from distance `n - 1`. **CONFIRMED.**

The third prefix bit is a discriminator and its polarity is easy to invert: bit 2
**clear** is the seven-bit short/control form and bit 2 **set** is the four-bit
form. Every one of the 4,322 reachable packed containers opens with bit 2 set
(`0 0 1`), i.e. on the four-bit escape.

## END-MARKER SEMANTICS

The terminator is the control escape: prefix `0 0 0`, a seven-bit field of zero,
then a two-bit field of zero. **CONFIRMED** present on all 4,322 reachable packed
containers and falling **exactly** at the declared size in every one.

How the engine *uses* it is a separate matter and is **UNRESOLVED**: the packed
decoder receives no output length and carries no output counter. The project
decoder stops on the declared size; the corpus cannot distinguish the two rules
because they coincide everywhere. See "Future encoder requirements" below.

Absence of the marker, truncation mid-token, and out-of-range back-references are
all cases where the engine would simply read on; see "Malformed".

## SOURCE BYTES CONSUMED

Measured by advancing the source pointer exactly as the engine's `ldr r6,[r1],#4`
does, over the 4,322 reachable packed containers:

| Quantity | Value |
| --- | ---: |
| minimum | 12 |
| maximum | 8,708 |
| total | 1,750,808 |
| samples | 4,322 |

Always a multiple of four. **No encoded length is stored anywhere**, the wrapper
holds only the decoded size, so a stream's extent can only be found by decoding
it.

## DESTINATION BOUND / SAFETY

**The packed decoder receives no destination capacity.** `0x0803D940` passes
`(source, destination)` and no length; the decoder stores with `strb` and
increments with no comparison. What keeps the canonical callers safe is that each
sizes its buffer from the same constant its containers declare: `0x800` per
dominant chunk (`0x08007BFE lsls r1, r5, #0xB`) and `0x4000` per selector bank.
**CONFIRMED** (instruction access).

Host-side tooling must keep its own declared-size bound; this record does not
relax it and does not implement it.

## UNKNOWNHEADER / HEADERLESS FORM

**REFUTED as a container form the engine can be handed.**

- The dispatcher knows only `{0, 1, 2}` at `+0x08`.
- The packed decoder is reached from exactly one place, the kind-1/2 arm -
  always with `r1 = container + 8`. There is no engine path that skips four bytes
  and then decodes.
- Four-byte prefixes do exist in the image, but as fields of engine *records*.
  A record that stores a decoded length and then a packed stream supplies exactly
  what a headerless decode needs, which is why the external tool's approach
  works.

Verdict on the four bytes: **resource-record metadata**, not codec data.
Headerless decoding is **CONSISTENT** with the engine but is not a distinct
container form.

## 64-KIB HYPOTHESIS

**REFUTED as an engine limit.** No instruction in the dispatcher or the packed
decoder compares against 65,536. The largest declared size in the reachable
corpus is `0x4000` (16,384). The figure is host-tool convenience and the project
decoder's own `DEFAULT_MAX_OUTPUT` is an unrelated safety constant.

## CANONICAL CONTAINER CENSUS

Seeded from the accepted resource graphs only: 421 distinct selector-1 roots from
452 `MapEntry` records.

| Resource class | References | Unique containers | Wrapper forms | Declared size |
| --- | ---: | ---: | --- | --- |
| dominant layer chunk (`record + 0x18`, handler `0x08008087`) | 3,912 | 3,745 | kind 1 × 3,745 | `0x800` on all |
| `root + 0x48` selector stream | 421 | 392 | kind 1 × 390, kind 0 × 2 | 4 .. 1,784 |
| `root + 0x4C` selector bank | 187 | 187 | kind 1 × 187 | `0x4000` × 186, `0x3C40` × 1 |

| Headline | Value |
| --- | ---: |
| REFERENCES | **4,520** |
| UNIQUE CONTAINERS | **4,324** |
| UNIQUE PAYLOAD DIGESTS | **4,324** |
| RESOURCE CLASSES | **3** |
| RAW (stored) FORMS | **2** |
| COMPRESSED (packed) FORMS | **4,322** |
| ZERO-HEADER FORMS | **2** |
| ALTERNATE / HEADERLESS FORMS | **0** |
| MALFORMED CANDIDATES | **0** |
| PAYLOAD-DIGEST COLLISIONS | **0** |
| SHARED CONTAINERS BETWEEN CLASSES | **0** |

`4,324 = 3,745 + 392 + 187`; `4,520 = 3,912 + 421 + 187`. The 3,745 dominant
figure reproduces LOGX-TILE-001 exactly. Declared sizes run **4..16,384**.

## KNOWN-GOOD FIXTURES

| Label | Address | Class | Declared | Decoded | Source consumed | Decoded SHA-256 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `dominant_chunk_0` | `0x08179A50` | dominant chunk | 2,048 | 2,048 | 476 | `f7ac0e36dd93d70c22ea62884adfdffbb7af1d597ca78b399fb35b1d7e507c27` |
| `dominant_chunk_1` | `0x0820BE10` | dominant chunk | 2,048 | 2,048 | 288 | `b6df3104b1ef19f5538c0fc760451fedfed1d016f0efd0302b26d6d2364715f3` |
| `dominant_chunk_2` | `0x082B8BAC` | dominant chunk | 2,048 | 2,048 | 20 | `0757872b4b26d36cd91ae3a60d55c8cdd5f4da5a60f0cda029fcab3a38250ac8` |
| `selector_stream_0` | `0x0817A75C` | `root+0x48` | 904 | 904 | 12 | `4edc8d61b019dd8371c5cbc49f6315769aee163c6a40f9ab79687084b28057e2` |
| `selector_stream_1` | `0x0817BA28` | `root+0x48` | 478 | 478 | 12 | `8d045c3637f6eb73a3a650b27eeb76e125d0e27e7fc680d932d192d24f113e16` |
| `selector_stream_2` | `0x082B8BF4` | `root+0x48` | 1,682 | 1,682 | 56 | `9b473f15cf67eea0fa3882780ee54527684fa208bc66b268af2f416713affbe0` |
| `zero_header_stored` | `0x082B5F1C` | `root+0x48` | 4 | 4 | 4 | `9c14ff2232b3d3427a3197aa999afadc58d36c2c3f855c9efcd5f1675291997a` |
| `bank_first` | `0x080945C0` | `root+0x4C` | 16,384 | 16,384 | 5,100 | `ccfa6a39379a38a292504012568d6bd39bd7c50bf5c50cb4e2334fd5370953f0` |
| `bank_last` | `0x08177AB8` | `root+0x4C` | 15,424 | 15,424 | 7,328 | `e1c9b6dd8a61ace97e7009f8b7523666150575737933b9ec706108b25e608909` |
| `engine_default_container` | `0x08070808` | engine default | 0 | 0 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

No decoded payload is committed anywhere; these are digests and lengths.

## EXISTING PROJECT DECODER STATUS

**`CORRECT WITH LIMITED FIXES REQUIRED`**, and **no shipping behaviour was
changed**.

`tools/webfoot/formats/webfoot_lz.py`:

- reads the engine's own wrapper layout and dispatch value set;
- its stored-branch semantics match the engine's `memcpy`;
- its packed grammar is byte-exact against a second implementation on all
  **4,322** reachable canonical packed containers. That proves the two agree; it
  is *not* an independent derivation, because the second was written after
  reading the first (see the note under DECODER DIFFERENTIAL VALIDATION). The
  grammar's authority rests on the corpus, not on the agreement;
- all 4,322 decoded lengths equal their declared sizes;
- its `packed_end` is measured by running the decoder, never read from a field -
  which is exactly what future allocation work needs.

Two differences from the engine are now documented rather than assumed, and
**neither is an engine-contract violation**:

1. the module **does not** enforce "the packed stream must produce exactly the
   declared size". It silently **clips** an over-long final match to the declared
   length and reports success, so it can hand a caller a truncated payload
   (`01000000040000000558d020000000c0` -> accepts, returns 4 bytes). That is
   host-side behaviour, and the engine has no length comparison either, but it
   is the failure mode `_unpack_stream`'s docstring says the function exists to
   prevent, and the module does not currently prevent it. **Recorded here and
   pinned by a test; fixing it belongs to a follow-up implementation task.**
   The second implementation refuses the same input, which is why the
   whole-corpus differential also demonstrates that this case never arises in the
   canonical image.
2. `DEFAULT_MAX_OUTPUT = 64 * 1024` is a host safety limit with no engine
   counterpart and must not be cited as a format maximum.

No correctness bug was found that blocks research, so no shipping change was
made. Any change to the module's failure policy belongs to a follow-up
implementation task.

## DECODER DIFFERENTIAL VALIDATION

Two implementations were run over the same corpus:

1. the project decoder, `tools.webfoot.formats.webfoot_lz.unpack`;
2. `tools.research.webfoot_codec_reference.decode_packed`, a second
   implementation written for this record.

| Comparison | Population | Result |
| --- | ---: | --- |
| decoded length equal | 4,322 packed containers | **4,322** |
| decoded digest equal | 4,322 packed containers | **4,322** |
| decode success on both | 4,322 packed containers | **4,322** |
| decoded length equals declared | 4,322 packed containers | **4,322** |
| end marker at the decoded length | 4,322 packed containers | **4,322** |

**What this proves, and what it does not.** The second module does not import or
call `webfoot_lz`, its only imports are `struct` and `dataclasses`, so the two
are not literally one implementation run twice, and the differential does prove
that they agree on every reachable container and that they differ in *policy* on
malformed input.

It does **not** prove the grammar is correct. The second implementation was
written after reading the first, and the two share most of their token grammar
line for line; an independent review measured **65 of 83** normalised grammar
lines as verbatim identical, including the whole dispatch table and the bias
ladder. A shared misreading would not be caught here.

**PROJECT CONCLUSION.** The grammar's authority rests on the corpus, not on the
agreement: 4,322 real containers decode to exactly their declared sizes, reach
their own end markers at that same length, and, for the dominant chunk class -
satisfy the tile-index coverage invariant LOGX-TILE-001 established
independently. The differential is a consistency and policy check on top of that.

No external implementation was copied. `mainant/LOGExtractor` was read only as a
source of claims to test; it is not a dependency and no code from it is present.

## MALFORMED-INPUT RESULTS

Synthetic data only; the canonical image was never mutated. **Every refusal below
is host-side policy.** The engine validates nothing. Reproduce with
`python -m tools.research.logx_codec_probe <rom> --malformed`.

| Case | Engine's instructions would | Project decoder | Reference |
| --- | --- | --- | --- |
| truncated header (< 8 bytes) | read the following bytes as the header words | refuse | no packed arm to run |
| dispatch word 3 | return with the destination untouched | refuse | no packed arm to run |
| packed, payload truncated | read past the container | refuse | refuse |
| packed, declared size 0 | never read `+0x04`; run the decoder | accept, 0 bytes | accept, 0 bytes |
| stored, size past the image | memcpy 0x7FFFFFFF bytes | refuse (host limit) | no stored arm to run |
| stored, declared size 0 | copy zero bytes | accept, 0 bytes | no stored arm to run |
| packed, no end marker, size reached | keep decoding; no size comparison exists | accept | accept |
| packed back-reference before output start | copy from bytes before the buffer | refuse | refuse |

**The second module decodes the packed arm only.** For the stored arm and for
unknown dispatch words its column states that, and the engine's own branch is
reported beside it; it does not pretend to answer for a branch it does not
implement.

**One case is not in the table because it is not malformed at all, and it is the
one that matters for safety.** The project decoder does **not** enforce "the
packed stream must produce exactly the declared size". An over-long final match
is silently **clipped** to the declared length and the decode is reported as
successful:

```text
blob 01000000040000000558d020000000c0   (kind 1, declared 4)
webfoot_lz.unpack        -> accepts, returns 4 bytes 0x41414141
reference.decode_packed  -> refuses: "decoded 15 bytes against a declared 4"
```

That is the partial-payload failure mode `_unpack_stream`'s own docstring says
it exists to prevent, and the module does not currently prevent it. It is
**host-side behaviour only**, the engine has no length comparison either, so
this is not an engine-contract violation, but it means the module can hand a
caller a truncated payload without saying so. Fixing the failure policy is a
follow-up implementation task, not this research pass; this record records
the behaviour and pins it with a test.

Coverage for every row above is in `tests/unit/test_logx_codec_reference.py`
("malformed" section).

## ENCODER FORMAT SUFFICIENTLY UNDERSTOOD

**PARTIAL.**

## FUTURE ENCODER REQUIREMENTS

| Requirement | Value / rule | Basis |
| --- | --- | --- |
| wrapper form | `u32` form, `u32` declared size, payload at `+0x08` | CONFIRMED |
| form to emit | `1` (the only form the canonical packed corpus uses) | CONFIRMED |
| declared-size field | the **decoded** byte count, excluding the 8-byte wrapper | CONFIRMED |
| raw fallback | form `0` plus the byte count; the engine supports it and `build_stored` emits it | CONFIRMED |
| stream termination | emit the stream's own control escape such that decoding stops where the declared size says | CONFIRMED for the corpus; the encoder must self-verify |
| alignment | source is read as whole 32-bit little-endian words; pad the final word | CONFIRMED |
| destination safety | must not rely on the engine to bound output, it does not | CONFIRMED |
| round-trip | decode the encoded stream and require exact equality | project policy |

**What is not sufficient.** The *initial literal width* the dispatcher supplies
is **UNRESOLVED**. It is immaterial for decoding, because every canonical stream
opens with an escape that overwrites it, but an encoder that relied on the
initial width instead of writing its own escape would be relying on an unresolved
fact.

This record does **not** ship an encoder. `webfoot_lz.pack` is a valid-stream
generator with a measured size penalty; whether that suits insertion is an
authoring decision this record does not make.

## TOOLING ADDED

| Artefact | Purpose |
| --- | --- |
| `tools/research/logx_codec_probe.py` | SHA-gated, read-only, deterministic probe: `--report`, `--fixtures`, `--census`, `--zero-header`, `--malformed`, `--entry-points`, `--json` |
| `tools/research/webfoot_codec_reference.py` | A second implementation of the packed grammar plus the engine wrapper report, for the differential. It does not import or call `webfoot_lz`, but it was written after reading it; see the note under DECODER DIFFERENTIAL VALIDATION |

Both are deterministic and write nothing except an explicitly requested
`--json`. Neither dumps decoded payloads.

## TESTS ADDED

| File | Coverage |
| --- | --- |
| `tests/unit/test_logx_codec_reference.py` | **39** portable synthetic tests: wrapper layout and the stored form (including its zero-length case), the opening control token and both escape forms, seven-bit literals and the base byte, the end marker (with a consumed-bit assertion so word padding cannot mask it), both prefix polarities, the declared-size stop, whole-word source consumption, determinism, eight malformed and boundary cases, a pinned clipping case, and a round-trip through the project encoder |
| `tests/integration/test_logx_codec_rom.py` | **23** ROM-gated tests: dispatcher contract, the 15-stub run with its measured targets, the ROM memcpy call, the DMA3 blob mapping, engine default container, census arithmetic, dominant-chunk shape, zero-header fixtures, all 10 fixture digests, the 4,322-container differential, end-marker position, opening-token census, source-consumption granularity, determinism, SHA gate |

## TEST RESULTS

| Suite | Result |
| --- | --- |
| `tests/unit/test_logx_codec_reference.py` | **39 passed** |
| `tests/integration/test_logx_codec_rom.py` (canonical ROM configured) | **23 passed** |
| `tests/integration/test_logx_codec_rom.py` (ROM absent) | skips cleanly |
| `tests/unit` (whole directory, ROM configured) | **1,373 passed, 15 skipped** |
| `tests/integration/test_logx_tile_rom.py` + `test_logx_layer_rom.py` + `test_logx_connector_rom.py` | **92 passed** |
| `tests/integration/test_map_render_rom.py` + `test_graphics_rom.py` | **32 passed, 2 skipped** (the 2 need the MAP-VIS-001 VRAM oracle, not this record) |

Environment note: five tests that use pytest's `tmp_path` fail in this
environment with `PermissionError: [WinError 5] '<pytest temporary root>'`
- a pre-existing temp-directory permission problem, unrelated to this record;
they pass when the suite is run with `--basetemp` on a writable path.

Additional focused runs are recorded in "Correction gate" below.

## DISAGREEMENTS WITH LOGEXTRACTOR

See "External claims tested". The load-bearing ones:

1. the two zero-word readings are **one engine branch**, not a disagreement about
   the format;
2. `UnknownHeader` is **not** a container form;
3. the 64 KiB figure is **not** a format limit;
4. JCALG1 is **not** promoted as the codec's identity.

## UNRESOLVED QUESTIONS

1. **RESOLVED after independent review:** the IWRAM base is **CONFIRMED**, not
   inferred, by the startup DMA3 literals at `0x08000148`/`0x0800014C`/
   `0x08000150` (ROM `0x087B79A4` -> IWRAM `0x03000000`, **4,100 bytes**). The
   packed decoder is blob base + `0x40` = ROM `0x087B79E4`.
2. The initial literal width the dispatcher supplies on the packed path.
3. Which termination rule the hardware obeys when a stream's end marker and the
   declared size disagree. No canonical container exercises the case.
4. Whether the engine's codec is byte-compatible with any specific JCALG1
   reference implementation.
5. Which selector reaches the 3,819 non-root dominant element targets (inherited
   from LOGX-LAYER-001, out of scope here).
6. Whether any container form exists outside the three reachable resource graphs.
   This record does not scan the image and does not claim none does.

## Related work: LOGX character records

Character/sprite resources reach their graphics through the same dispatcher
(`0x0803D940` has 57 `BL` callers across the image), so the wrapper and grammar
established here apply unchanged. Two concrete downstream notes:

- **Use `webfoot_lz.unpack` and its `packed_end`.** The module is confirmed
  byte-exact on the whole reachable corpus; do not add a second decoder.
- **Character containers are not in this record's census population.** The
  census covers dominant chunks, `root+0x48` streams and `root+0x4C` banks only.
  A character-graphics container's declared size and container kind must be
  measured for that class; do not assume `0x800` or `0x4000`.

## Encoder implementation requirements

- The format is **PARTIAL**-ready for an encoder. Read "Future encoder
  requirements" before writing one.
- The engine performs **no** validation: no kind check beyond `{0,1,2}`, no
  declared-size comparison, no destination bound. An encoder cannot rely on the
  engine to catch a bad stream.
- Because the engine has no output counter, the end marker's placement is
  load-bearing. On every canonical container the marker and the declared size
  coincide, which is a property of these streams and not a guarantee the format
  makes.
- `packed_end - offset` is the only capacity a re-encoded payload may occupy, and
  it is measured, never stored.

## Other downstream consumers

- **LOGX-TILE-001 / map render:** unchanged; the dominant-chunk route and the
  `0x800` shape are re-measured here and reproduce exactly.
- **Graphics/atlas tooling:** the `root+0x4C` bank class is 187 containers, 186
  declaring `0x4000` and one `0x3C40`; all decode byte-exactly.
- **Any tool reading `container[+0x00]` as a boolean:** it is a form selector
  with three live values, and a non-`{0,1,2}` value means "the engine returns
  with the destination untouched".

## First independent verification

engine/wrapper/dataflow-focused independent review. `APPROVE WITH NON-BLOCKING
NOTES` at the third round.

**VERDICT HISTORY: BLOCK → BLOCK → APPROVE WITH NON-BLOCKING NOTES.** Every
load-bearing engine/wrapper/dataflow conclusion was independently CONFIRMED from
the first round; the blocking items were wrong CONFIRMED engine addresses and
labels in the evidence record, a refuted engine semantic, an unreproducible
method figure, and stale test bookkeeping.

the first review pass independently confirmed, static and read-only: the dispatcher's
argument convention and raw halfwords; the three dispatch comparisons; the
`+0x08` payload offset; the `{0,1,2}` selector set; "destination untouched" for
other values; the stored-branch copy of `container[+0x04]` bytes; the **57**
`BL` callers and all four accepted call sites with their consumers; the absence of
any destination bound or output length, by enumerating **all 28** `cmp`/`subs` in
the primary decoder and showing none touches `r0` or an output counter; every
census headline; and all ten fixture addresses and digests.

the first review pass also independently derived the corrected prefix polarity from the
engine's own tree (`0x087B7A3C adds r6,r6,r6` / `0x087B7A40 blo 0x087B7AD4`: bit 2
clear goes to the seven-bit/control path, bit 2 set falls through to
`mov r8,#4`), corroborating the second review pass's B1 independently.

The three non-blocking notes it left at the end (the caller-population counting
convention, a stale `0x800` figure in the body text, and the corrections-log
staleness) were all fixed after that verdict; it asked for no further review.

### Findings raised

| # | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| A1 | REQUIRED | The stored branch calls `0x08046D18`, a ROM-resident ARM memcpy, **not** the stub at `0x08049138`; the doc gave the wrong routine *and* the wrong caller. | **ACCEPTED, corrected.** Verified here: `0x0803D960` decodes to `bl 0x08046D18`, whose only caller is `0x0803D960`. Provenance §4.3 and the README now state the ROM routine and note that `0x08049138` belongs to `0x0803D986` (the second entry). |
| A2 | REQUIRED | `0x08049138` -> `0x03000768`, not `0x030007A8` (that literal belongs to `0x0804912C`, and it is a **memset**); and **`0x03000190` occurs zero times in the 8 MiB image**, so the "row copy" row was invented. The same two values were hard-coded in `webfoot_codec_reference.py` and a passing test asserted the wrong label. | **ACCEPTED, corrected.** The full 15-stub table is re-derived from each stub's own literal and is now in the evidence record; `IWRAM_MEMSET`/`IWRAM_MEMCPY`/`IWRAM_ROW_COPY` were replaced by the measured set, `IWRAM_ROW_COPY` was deleted, and the integration test now asserts the measured targets rather than a label. |
| A3 | REQUIRED | "8,838 encodings; 8,266 resolve in-ROM; 4,440 distinct targets" does not reproduce under the stated method, and the "alignment-independent" claim was false. | **ACCEPTED, corrected.** The method sentence now specifies the every-even-offset walk, reports 17,748 encoding pairs (35,496 halfwords) and 9,624 distinct targets, and states that a stride-4 walk finds only 30 of the 57 callers because 27 of them sit at address ≡ 2 (mod 4). The `8,838 / 8,266 / 4,440` figures are named as belonging to a different scan that cannot produce the 57, and are not used. A final review round showed the population counts are convention-dependent (pair versus halfword); both conventions are now stated with their ratio. |
| A4 | REQUIRED | "decoder at base + `0xF8`" contradicts the dispatcher's own target. | **ACCEPTED, corrected.** The packed decoder is ROM `0x087B79E4` = IWRAM `0x03000040` = base + `0x40`; `0x087B7A9C` is described as an interior bit-loop label. |
| A5 | REQUIRED | The "library table at `0x087B7970` pairs destinations with ROM sources" reading is address-shifted and does not show the claimed pairing. | **ACCEPTED, corrected.** The table reading is withdrawn; its semantics are recorded as UNKNOWN, and the base is established instead from the startup DMA3 literals. the first review pass's stronger evidence **upgraded the base from INFERRED to CONFIRMED**, which this record now states. |
| A6 | REQUIRED | `0x0803D966` **does** have a `BL` caller: `0x0800F3D2`. | **ACCEPTED, corrected.** Verified here by raw scan (exactly one caller) and by disassembling the call site. Both documents now record it. |
| A7 | REQUIRED | `r2` is a lookup-table pointer, not a length; "length-aware variant" is refuted. | **ACCEPTED, corrected.** The full `0x0803D966` control flow is now transcribed; the non-NULL branch is described as a `r2`-indexed remapping path, and the "length-aware variant" sentence is withdrawn. The `UnknownHeader` conclusion is unaffected and is now scoped to "no path skips four bytes and then decodes", which the verification pass confirmed still holds. |
| A9 | REQUIRED | Stale test counts (41 / 33 / 20 against a frozen file holding 39 and 21). | **ACCEPTED, corrected.** The counts now match the collected totals; after the first review pass's own two added tests the final figures are **39 unit + 23 integration = 62 passed**. |

### Non-blocking notes, and their disposition

| Note | Disposition |
| --- | --- |
| N1: `--fixtures` emits 9 rows, not the 10 in the fixture table. | **ACCEPTED, fixed.** `default_fixtures` now includes `engine_default_container`, so the command emits all 10 rows. |
| N2: the default container has `0x7F8` trailing zeros, not `0x800`. | **ACCEPTED, corrected** to 2,040 (`0x7F8`) bytes, with the first non-zero byte at `+0x800` recorded. |
| The UNRESOLVED initial-width item is over-conservative: the dispatcher leaves the dispatch word in `r3` and the decoder's prologue does not overwrite it, so the width is resolvable as 1 or 2. | **ACCEPTED, recorded.** Provenance §23 still lists it as unresolved for the *engine contract*, but now states the narrowing and that the project decoder's "read it from the dispatch word" happens to be engine-exact. |
| The `roms` junction escapes `.gitignore`'s `roms/` rule. | **ACCEPTED**, removed before commit; only explicit paths are staged. |

## Second independent verification

decoder/fixtures/adversarial-safety-focused independent review. `APPROVE WITH
NON-BLOCKING NOTES` at the third round.

**VERDICT HISTORY: BLOCK → BLOCK → APPROVE WITH NON-BLOCKING NOTES.**

the second review pass reproduced, from its own from-scratch decoder and with no repo file
written: the census arithmetic (3,745 / 392 / 187 unique, 3,912 / 421 / 187
references, 4,324 unique, kinds `{1: 4322, 0: 2}`, 421 roots, 4,324/4,324 unique
digests with 0 collisions, declared 4..16,384, source consumed 12..8,708 totalling
1,750,808 all `%4 == 0`); the differential (project == reference on 4,322/4,322,
second-verification-pass-decoder == project on 4,322/4,322, sizes == declared on 4,322/4,322);
the end-marker distribution `{0: 4322}` and the non-vacuity of the test that
asserts it; all ten fixture digests; and the ROM SHA-256 before and after.

### Findings raised

| # | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| B1 | HIGH | The prefix tree was stated **inverted** in the prose (README, provenance §8.1/§8.4/§8.5, `docs/reverse-engineering.md`): the seven-bit/control form is prefix `0 0 0` and the four-bit form is `0 0 1`. | **ACCEPTED, corrected.** The code was right and the prose was wrong. Every statement in every file now reads `0 0 0` = seven-bit/control (end marker), `0 0 1` = four-bit code. the second review pass's re-review caught three README lines that still carried the inversion; those are fixed, and the review doc's own "SHORT MATCH"/"END-MARKER" lines were the last two. |
| B2 | HIGH | The unit test's `_end_marker()` helper built `001`+7 zeros+`00`, which is not a marker, so the test passed only because the stream is padded to a whole word. | **ACCEPTED, corrected.** The helper now returns `000`+7 zeros+`00`, and the test asserts the consumed bit count (`37`) so padding cannot mask a wrong marker. A second test pins both prefix polarities. |
| B3 | HIGH | The project decoder does **not** enforce "produces exactly the declared size": it silently clips an over-long final match and reports success, so a caller can receive a truncated payload. | **ACCEPTED, documented, pinned, and routed to follow-up work.** Repro reproduced exactly (`01000000040000000558d020000000c0` -> `wl.unpack` accepts 4 bytes; the reference refuses). README "EXISTING PROJECT DECODER STATUS" and provenance §18/§15 rewritten; `test_project_decoder_clips_an_over_long_final_match` added. No shipping change was made. |
| B4 | MEDIUM | The malformed table disagreed with `--malformed` and asserted engine behaviour the record elsewhere denies. | **ACCEPTED, corrected.** The probe's report now emits an explicit `engine` column phrased as "the engine would ...", routes the reference column through the same kind dispatch as the engine instead of hard-coding, and states where the reference has no arm. The README table was rewritten to match the tool's actual output. |
| B5 | MEDIUM | `opening_token_report` read the base byte from `b8..b15` instead of `b9..b16`, folding the escape's own selector bit into the value. | **ACCEPTED, corrected.** The report now decodes the two-bit field at `b7..b8` and reads the base at `b9..b16`, and reports the field histogram separately. Measured consequence of the old window: 74 distinct "base bytes" instead of the true 11, wrong on 3,188 of 4,322 containers. |
| B6 | MEDIUM | Provenance §7.4's table and §8.6's worked example were wrong in their bit indices and values. | **ACCEPTED, corrected.** §7.4 now records the measured prefix histogram (`001` on all 4,322), the two-bit field split (1 on 3,160, 0 on 1,162), and the base-byte distribution; §8.6 now walks `0x2000114F` bit by bit with the correct polarities, and states the little-endian/MSB-first reading rule that makes the example reproducible. |
| B7 | LOW | README said 20 ROM-gated tests; 21 were collected at that point. | **ACCEPTED, corrected.** Both counts are now current: **39 unit + 23 integration = 62 passed**. |

### Non-blocking notes, and their disposition

| Note | Disposition |
| --- | --- |
| The differential is not an independent derivation: 65 of 83 normalised grammar lines are verbatim identical to `_unpack_stream`, so the "not agreement-by-construction" claim overstated it. | **ACCEPTED, claim narrowed.** Provenance §14 now states exactly what the differential does and does not prove, and rests the grammar's authority on the corpus. |
| `test_dominant_chunks_all_declare_0x800` and `test_source_consumption_is_whole_words` pass on an empty population. | **ACCEPTED, count assertions added** to both. |
| No test covered truncated header, missing end marker, output overflow, or the clipping case. | **ACCEPTED, four tests added** (`test_truncated_header_is_refused_by_the_project_decoder`, `test_missing_end_marker_with_declared_size_reached_is_accepted`, `test_output_never_exceeds_the_declared_size`, `test_project_decoder_clips_an_over_long_final_match`). |
| §13.1 said "long match d=2 c=7"; the decoded count is 11 (gamma 7 plus the `<= 0x7F` bias of 4). | **ACCEPTED, corrected**, and the entry now shows the raw count and the bias separately. |
| The portable dispatcher test only asserts literals inside the module's own report dict and must not be cited as engine evidence. | **ACCEPTED**, the integration test is the one that reads the ROM, and the distinction is stated in both files. |
| The worktree has an untracked `roms` link to the main repository, which `.gitignore`'s `roms/` rule does not cover. | **ACCEPTED**, it is a local-only directory junction created for the ROM-gated suites; it is removed before commit and only explicit paths are ever staged. |

## Correction table

Seventeen required corrections were raised across the two reviews, all of them
reproduced here before being accepted:

| From | Count | Where they landed |
| --- | ---: | --- |
| the first review pass (A1–A7, A9) | 8 | provenance §4.1–§4.3, §5.3, §8, §18, §21, §23; README entry-point and decoder-status sections; `webfoot_codec_reference.py` constants and `veneer_table`; integration test assertions |
| the second review pass (B1–B7) | 7 blocking + 2 test-quality | provenance §7.4, §8.1, §8.4–§8.6, §13.1, §14, §15, §18; README malformed/status/test sections; `logx_codec_probe.opening_token_report` and `malformed_report`; unit-test fixtures and five added tests; integration count assertions |
| the first review pass non-blocking (N1, N2) | 2 | `default_fixtures`; provenance §5.3 |

## Assertions that did not survive re-measurement

**Two assertions were initially rejected and both were subsequently upheld.** They
are recorded here because the first pass rejected them on wrong arithmetic of our
own, and the correction is the point.

| Assertion | First-pass result | Final result |
| --- | --- | --- |
| the first review pass: the two branch stubs target `0x08047040` and `0x08047450`. | Rejected. Re-measured as `0x08047038` / `0x0804744C` using `stub_address + 8 + (delta << 2)`. | **UPHELD.** The ARM `b` is at `stub + 4`, so PC reads as `stub + 12`. Capstone agrees: `0x0804919C b #0x8047040` and `0x080491A4 b #0x8047450`, and both targets begin `80 4d 2d e9` = `push {r7,r8,sl,fp,lr}`, valid ARM entries, while `0x0804703C` / `0x0804744C` / `0x08047038` decode mid-instruction. `veneer_table` was fixed to `address + 12 + (delta << 2)` and the two documentation rows now read `0x08047040` / `0x08047450`. |
| the first review pass: the stub slots are not uniform. | Accepted and refined. | **UPHELD and refined.** `ldr pc` slots are 12 bytes and branch slots are 8, so a fixed 12-byte walk stops after the first branch stub. The run is 15 stubs / **172** bytes; `veneer_table` walks both forms. |

A third assertion was rejected as worded and accepted in substance:

| Assertion | Result |
| --- | --- |
| the first review pass (round 1): the caller-enumeration figures do not reproduce. | **Upheld in substance, and the first replacement was also wrong.** Round 2 measured 17,748 encoding pairs / 57 callers for the every-even-offset walk and 8,838 / 30 for stride 4. The final text states the pair convention explicitly, notes that a halfword-counting convention gives 33,960 / 17,299 (exactly twice, same 57 / 30 caller counts), and no longer claims alignment independence: a stride-4 walk provably cannot produce 57. |

## CORRECTION GATE

All required corrections from both reviews were re-measured against the canonical
image, applied, and re-tested. Both verification passes re-verified three times.

| Round | the first review pass | the second review pass |
| --- | --- | --- |
| 1 | BLOCK (A1–A7, A9) | BLOCK (B1–B7) |
| 2 | BLOCK (A2 partial, A3, A11) | BLOCK (B1 partial, B7) |
| 3 | **APPROVE WITH NON-BLOCKING NOTES** | **APPROVE WITH NON-BLOCKING NOTES** |

Every finding was reproduced before acceptance. Two assertions were rejected on
first pass and both were upheld on re-measurement (recorded under REJECTED
VERIFICATION ASSERTIONS); one first-pass rejection turned out to be *our* arithmetic
error, which is recorded rather than quietly fixed.

Ten non-blocking notes remained after the final verdicts; all ten were fixed, and
neither verification pass asked for a fourth round.

### Final validation on the frozen revision

| Check | Result |
| --- | --- |
| `tests/unit/test_logx_codec_reference.py` | **39 passed** |
| `tests/integration/test_logx_codec_rom.py` (canonical ROM) | **23 passed** |
| both together | **62 passed** in 72 s |
| `tests/unit` (whole directory) | **1,373 passed, 15 skipped** |
| prior LOGX integration (`tile`, `layer`, `connector`) | **92 passed** |
| prior LOGX integration (`map_record`, `map_render`) | **16 passed** |
| `map_render` + `graphics` ROM suites | **32 passed, 2 skipped** (VRAM oracle absent) |
| `git diff --check` | clean |
| canonical ROM SHA-256 | unchanged |
| `webfoot_lz.py` | untouched (no production edit) |
| staged proprietary artefacts | none |
