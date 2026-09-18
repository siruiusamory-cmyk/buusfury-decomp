# LOGX-GFXSCAN-001 review

Research-only ticket. Isolated worktree and branch; no integration to master.

```text
START SHA:            421ac94012a7cf7ace110685f1a639811f27702b
END SHA:              8dad4a2c5dbd1105b920e9e277aa3fa775cc05ca
BRANCH:               logx-gfxscan-001
COMMIT SHA(S):        8dad4a2c5dbd1105b920e9e277aa3fa775cc05ca
                      research(gfxscan): validate Buu graphics discovery
                      <- all five artefacts, including every review correction.
                      A second, documentation-only commit records this hash in this
                      file:
                      HEAD (git rev-parse logx-gfxscan-001), subject
                      `docs(gfxscan): record the reviewed revision in the ticket
                      result`.
                      The reviewed revision was 142d308; the branch was amended
                      repeatedly while the two review rounds ran, so no intermediate
                      amend hash is named.
WORKTREE:             <temp>\log1-remake-logx-gfxscan-001

CANONICAL ROM SHA BEFORE: 940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
CANONICAL ROM SHA AFTER:  940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E
```

---

## EXTERNAL LOGEXTRACTOR SCANNER

`mainant/LOGExtractor`, commit `3a78bb35ad181082fbc9da01057538e5a78e8c2d`
("Adding remaining tools", 2024-05-21) - the **only** commit that ever touched
either transcribed file.

Files transcribed: `ImageScan/MainForm.cs` (`ScanForImages`),
`ImageScan/Gba/JCALG1.cs` (`Decompress`, `DecompressInternal`,
`DecompressUnknownHeader`, `CompressionSource`). `CharacterSpriteExtractor/Gba/JCALG1.cs`
is byte-identical to the ImageScan copy (same SHA-256); `MapViewer`'s differs only
in dropping an unused `using` and the `Array.Resize`.

What the scan recognises, exactly:

- **addresses tested**: every byte offset from `0x200` to `rom.Length - 4`,
  increment 1 - **no alignment assumption**;
- **signature rule**: the first word must be **exactly `1`**;
- **size filter**: `1 <= declared < 0x20000` **and** `declared % 4 == 0`;
- **decompression**: external grammar over little-endian words consumed MSB-first;
- **output-size filter**: none. `isPrio = (decoded.Length == 256)` is a **sort
  priority**, never a rejection;
- **graphics dimension assumptions**: none in the scan - the GUI user picks tile
  size and row width at draw time;
- **palette assumptions**: none in the scan - a 256-entry `.act` file is chosen by
  a checkbox;
- **duplicate suppression**: none; the list is sorted and kept whole;
- **rejection rules**: the three above, plus "the decompressor threw" and "it
  returned an empty array";
- **UnknownHeader path**: present in `JCALG1.cs`, **never called by the scan**;
- **visual plausibility**: **none in the scan**; `CreateBitmap` is display-only and
  the scan never calls it.

Full transcription, the token grammar, and the two places where a literal reading
of the external source does not reproduce the canonical corpus are in
[`../research/LOGX_GFXSCAN_PROVENANCE.md`](../research/LOGX_GFXSCAN_PROVENANCE.md)
§§3 and 9.3.

## SCAN POPULATION

| Quantity | Value |
| --- | ---: |
| byte positions the loop body executes at | **8,388,093** |
| positions whose first word is exactly `1` | 29,504 |
| ... word-aligned | 27,775 |
| positions passing the size filter (submitted to the decoder) | **13,463** |
| positions rejected by the size filter | 16,041 |

## ALIGNMENT / SEARCH MODEL

The external model walks **every byte**, as the tool does. The engine-informed
model requires **word-aligned wrapper starts** and removes **7,221** candidates at
**zero recall cost**. All accepted canonical container starts are word-aligned, so
alignment is independently justified, not a tuning choice.

---

## KNOWN POSITIVE CORPUS

Built from accepted graphs only; no sweep contributes.

| Class | Reference | Refs | Unique | Digests | Graphics? |
| --- | --- | ---: | ---: | ---: | --- |
| `sprite_piece_graphics` | LOGX-FRAME-001 piece `+0x08` | 11,005 | **7,390** | 7,390 | **CONFIRMED** |
| `map_dominant_layer_chunks` | LOGX-TILE-001 `+0x18` array | 3,912 | 3,745 | 3,745 | REFUTED (tile indices) |
| ... of which decode digest-identically under the external grammar | | | | 3,744 | one container differs (§ below) |
| `root_48_selector_streams` | LOGX-MAP-RENDER-001 `root+0x48` | 421 | 392 | 392 | REFUTED (u16 selectors) |
| `root_4c_graphics_banks` | LOGX-TILE-001 bank table | 187 | 187 | 187 | UNRESOLVED |
| `zero_header_form0_containers` (a **subset** of the selector class) | form-0 selector members | 2 | 2 | 2 | UNRESOLVED |
| `engine_installed_default_container` | LOGX-CODEC-001 default | 1 | 1 | 1 | REFUTED (size 0) |
| **total** | | **15,528** refs / **15,526** distinct | **11,715** | **11,715** | |

No two known containers share a payload digest, so the corpus's sharing is by
reference (11,005 piece references to 7,390 containers).

**The classes are not a partition and the one overlap is named.**
`zero_header_form0_containers` is a **subset** of `root_48_selector_streams`: the
same two addresses, `0x082B5F1C` and `0x082B5F94`. The per-class sizes sum to
**11,717** while the corpus holds **11,715** containers. The authoritative totals
are the corpus's own; the probe reports `class_size_sum`, `class_overlap` and the
overlap addresses so the over-count is visible. An earlier revision of this
document printed `7,390 + 3,745 + 392 + 187 + 2 + 1 = 11,715`, which was
arithmetically wrong, and the ROM-gated suite now asserts the overlap by address.

### SPRITE GRAPHICS

7,390 unique containers from 11,005 piece references. External-model recall:
**7,390 / 7,390 (100%), digest-exact**. All form 1, declared 64..4,096 bytes.

### MAP GRAPHICS

There is no class here whose *graphics* identity is established, so no map
graphics recall is claimed. The map containers measured are the dominant-layer
chunks and the `root + 0x4C` banks; both are found in full by address, and the
chunk class is **refuted as graphics** (its payload is `u16` tile indices).

### PORTRAITS

**No figure claimed.** LOGX-CHAR-001's `+0x08` pointer array was not enumerated as
a known-positive class by this ticket, so portrait recall is an unmeasured
limitation, not a zero. The external `CharacterSpriteExtractor` decodes a portrait
through the same `JCALG1.Decompress`, so the population is measurable with the
same tool as a follow-up.

### OTHER GRAPHICS CLASSES

`root_4c_graphics_banks` (187 unique, form 1, 15,424..16,384 bytes) is enumerated
and found in full by address, but its graphics identity is **UNRESOLVED**, so it
contributes no recall claim.

---

## EXTERNAL-MODEL RAW CANDIDATES: 12,990

(`decode_raised` 175, `empty_output` 298, submitted 13,463.)

## EXTERNAL-MODEL VALID DECODES: 12,990 accepted; 12,976 reach the declared size

14 accepted candidates hit the stream's own end marker first - the tool's
`Array.Resize` keeps them, so it never notices.

## EXTERNAL-MODEL UNIQUE ADDRESSES: 12,990

## EXTERNAL-MODEL UNIQUE DIGESTS: 12,912 (78 shared-payload instances)

---

## KNOWN GRAPHICS HITS: 7,390 of 7,390 sprite containers

## KNOWN GRAPHICS MISSES: 0

## KNOWN GRAPHICS RECALL: 100.0%

## KNOWN NON-GRAPHICS HITS: 4,123

(map chunks 3,745, selector streams 191, banks 187 - real engine-reachable
containers that are not pixels.)

All-class recall: **11,513 / 11,715 (98.3%)**. The 202 misses are 199 selector
streams rejected by `declared % 4 == 0`, 2 form-0 selector streams, and the
form-0 zero-length engine default.

---

## ENGINE-INFORMED MODEL

| | EXTERNAL | ENGINE-ALIGNED | ENGINE-UNCONSTRAINED |
| --- | ---: | ---: | ---: |
| submitted | 13,463 | 25,074 | 32,880 |
| **candidates** | **12,990** | **24,283** | **31,504** |
| stored-form | 0 | 11,097 | 18,309 |
| packed-form | 12,990 | 13,186 | 13,195 |
| unaligned | 10 | **0** | 7,221 |
| unique digests | 12,912 | 19,109 | 25,425 |
| known containers found | 11,513 | **11,714** | 11,714 |

## ENGINE-INFORMED CANDIDATES: 24,283

## ENGINE-INFORMED RECALL: 7,390 / 7,390 sprites; 11,714 / 11,715 known containers

The single exception is the **form-0 container declaring zero bytes** at
`0x08070808`, which every model's size floor (`declared >= 1`) excludes. It is
named, not silently dropped.

---

## FALSE-POSITIVE CLASSES

Three mechanisms, counted apart. Collapsing the first two was a defect of an
earlier revision: the class named "inside a known container" counted candidates
whose owner was **not** a known container.

| Class | External | Engine-aligned | Engine-unconstrained | Mechanism |
| --- | ---: | ---: | ---: | --- |
| `end_marker_before_the_declared_size` | 14 | 0 | 0 | the stream stops early; `Array.Resize` accepts the short payload |
| `wrapper_start_inside_a_known_container` | **0** | **4** | **267** | the "header" is inside a **known** container's measured extent |
| `wrapper_start_inside_another_candidate` | **2** | **7,084** | **15,320** | the "header" is inside **another candidate's** measured extent |
| `wrapper_start_not_word_aligned` | 0 | 0 | **74** | classified on an unaligned start |
| `clipped_decode_against_declared_size` | 0 | 0 | 0 | not reachable: the loop cannot cross its own declared bound |
| **total F** | **16** | **7,088** | **15,661** | |

`decode_raised` (175) is **not** a false-positive class: those positions never
became candidates.

**Not the same number as the nested flag.** `flag_nested_candidates` records
`nested_inside_candidate` for **all** candidates inside another candidate's
extent - 4 external, **12,612** engine-aligned, **21,610** engine-unconstrained -
while the F class counts only those that reach classification without a known
match, a reference or an earlier class. The 74 in the third row are candidates
*classified* on alignment, which is not the **7,221** unaligned candidates the
engine-aligned model never forms; an earlier revision reported the second number
under the first name.

---

## RESIDUAL CANDIDATES: 5,479

(engine-aligned candidates minus every accepted known container)

| Quantity | Value |
| --- | ---: |
| with a payload a known container also has | **0** (definitional: a payload match is classified A/B before it can reach the residual) |
| confirmed by the external model too (same address, same digest) | 381 |
| form 0 (stored) | 5,092 |
| form 1 (packed) | 387 |

## ENGINE-REFERENCED RESIDUALS: 414

## NO-REFERENCE-FOUND RESIDUALS: 5,065

Of the 414 referenced, **387 are packed**; 381 of those have whole-tile decoded
lengths; 381 are byte-for-byte confirmed by the external model; and the
conjunction *packed and whole-tile and at least 8 KiB* is **21**.

**They are not a homogeneous block of large tile banks**, and an earlier revision
described them as one. Their declared sizes run **128 .. 65,474** bytes and the
distribution is dominated by small streams:

| Declared size | Count |
| --- | ---: |
| 256 | 129 |
| 1,024 | 88 |
| 4,096 | 97 |
| 2,048 | 24 |
| 8,192 | 16 |
| other | 33 |
| **= 8 KiB or larger** | **26** |

The largest referenced residual is `0x087A04F0` (65,474 bytes) and it is **not**
external-confirmed. Several of the largest are named by consecutive words in one
table around `0x087B5B64`, which is the first thing a follow-up should read. They
are the ticket's most useful output and are **not** claimed as graphics: no
rendering consumer was established for any of them.

The 5,065 unreferenced residuals are all form 0, i.e. positions where a scan read
a plausible header out of code or data and "decoded" the image's own bytes back.

**Reference-search coverage, stated with the claim:** a complete sweep of every
word-aligned word position (2,097,152) for the two stored pointer forms.
**Not covered:** computed arithmetic, folded bases, `LDM`/`STM` aggregates. Of the
1,546 targets with a hit, 1,508 have a full-GBA-address hit and 38 have only a
bare-file-offset hit; the two forms are reported apart because a small integer
occurs throughout the image.

---

## STORED-FORM COVERAGE: 0 of 3 known form-0 containers

The `magic != 0x1` test excludes the form before the decoder is reached.

## PACKED-FORM COVERAGE: 11,513 of 11,513 known packed containers admitted

100% of every known packed container whose declared size passes the external
filter; 11,513 found by address, 11,435 of them digest-exact, 78 differing per
the two divergences below.

## UNKNOWNHEADER RESULT

**REFUTED as an engine container form** (LOGX-CODEC-001) and not re-promoted. As
an external heuristic it decodes, but it is run over bytes that are not the stream
the wrapper names, so its output carries no container semantics. No independently
engine-referenced headerless stream was found, and none is claimed.

---

## OVERLAP / NESTED-CANDIDATE RESULT

Two quantities, and they are not the same number:

| Model | inside a **known** container's extent | inside **another candidate's** extent |
| --- | ---: | ---: |
| external | 0 | 4 |
| engine-aligned | 4 | 12,612 |
| engine-unconstrained | 267 | 21,610 |

Extents are the models' own **measured** source consumption, not declared lengths.
Of the 12,612 engine-aligned nested candidates, 6,607 are packed and 6,005 are
stored-form; an earlier revision of this section reported the mislabeled F class
(7,088 / 15,587) as the nested population, and called all of it form 0, which was
wrong on both counts.

---

## SHIPPING DISCOVERY TOOL: **NO**

Its acceptance rule asserts almost nothing: the decoder is told how many bytes to
produce, it stops when it has produced them, and the only failure is a token
indexing before its own output start - with the size itself read from the same
four-byte window that supplied the form word. It reports 12,990 candidates for
11,715 known containers, ranks them only by `decoded length == 256`, and cannot
distinguish a container from a byte sequence that looks like one. The form-0 arm
makes that indistinguishable in principle.

## FORENSIC / RESEARCH TOOL: **YES**

It finds 100% of the engine-referenced sprite graphics containers, digest-exact,
and 100% of the map chunks and banks. As a recall instrument for "has anything
been missed" it is strong, and its 1,453 engine-referenced candidates at addresses
no accepted graph reaches are a real lead list.

## CANONICAL ENUMERATOR: **NO**

It has no acceptance contract. Its precision comes from the corpus, not from the
method. Structured graph traversal must remain authoritative.

---

## NEW CANONICAL RESOURCE FINDINGS: none

The 387 referenced, packed residual candidates are a **lead list**, not a format
and not a resource class: no consumer and no semantics were established for any of
them. They are not a homogeneous block - only 21 are whole-tile and at least
8 KiB - and the table around `0x087B5B64` names several of the largest.

---

## TOOLING ADDED

| Path | Purpose |
| --- | --- |
| `tools/research/logx_gfxscan_probe.py` | SHA-gated read-only reproduction of the external scanner plus two engine-informed models, the known-positive corpus, the reference search and the residual set; modes `--external-model`, `--engine-model`, `--known`, `--classify`, `--diff`, `--residual`, `--references`, `--summary`, `--unknown-header`, `--json` |

The module imports only the standard library, the project's research modules and
the project's container decoder. It does **not** import `thumb_disasm` (the only
capstone-dependent module), so importing it never requires an optional package;
`tests/unit` asserts that under a poisoned `capstone` entry.

## TESTS ADDED

| Path | Scope |
| --- | --- |
| `tests/unit/test_logx_gfxscan_probe.py` | 39 portable synthetic tests: bit framing (including that the fast reader and the explicit bit list agree), the external form/size filter, the external decoder's arms and its failure mode, `GetInteger` bit order, address normalisation, `exact` vs `full_length`, classification arithmetic, nested flagging, deduplication, reference search, the canonical gate, optional-dependency behaviour |
| `tests/integration/test_logx_gfxscan_rom.py` | 31 ROM-gated tests: corpus counts, **the external model reproducing the project decoder on real containers**, per-class recall, the scan population, the engine models, residual invariants, word-alignment proofs, canonical-image integrity |

## TEST RESULTS

```text
portable:  python -m pytest tests/unit/test_logx_gfxscan_probe.py -q
           39 passed
ROM-gated: LOGX_CANONICAL_ROM=<image> python -m pytest tests/integration/test_logx_gfxscan_rom.py -q
           31 passed
full unit: TMP=<writable> python -m pytest tests/unit -q
           1493 passed, 16 skipped
ROM-absent: the ROM-gated module collects 31 tests and skips cleanly
           (pytest.skip) when the image is absent
```

---

## ROM_BIBLE_IMPACT: NONE

No new canonical format, field or resource class was established. The residual
candidates are a lead list; nothing in `docs/reverse-engineering.md` changes.

## public progress impact: NONE

Research-only measurement of an external tool's discovery behaviour inside an
isolated worktree; it adds no user-facing capability, no frontier, no questline
change and no completed capability.

---

## DISAGREEMENTS WITH LOGEXTRACTOR

| Statement / behaviour | Disposition |
| --- | --- |
| scans every byte offset | **CONFIRMED** |
| a decoded non-empty payload is a scan result | **CONFIRMED** as behaviour; **REFUTED** as a container test |
| `decoded length == 256` identifies graphics | **REFUTED**: a sort priority; 244 of 12,990 carry it |
| `UnknownHeader` decodes headerless streams | **PARTIALLY CONFIRMED** as a decoder; **REFUTED** as an engine container form; it reads from `container + 4`, not `container + 8` |
| the ~64 KiB buffer is a format maximum | **REFUTED** (LOGX-CODEC-001) |
| the codec is JCALG1 | **PARTIALLY CONFIRMED** as JCALG1-like/derived; the name is not promoted |
| `GetInteger` continues while its continuation bit is set, as the source reads | **CONFIRMED as written, and reproduced as written**: exiting on a clear bit is the same loop. The source's reading decodes all 11,712 kind-1 known containers and reproduces the project decoder on 11,634 |
| the declared-size word seeds the literal base | **REFUTED**, from the source (`CompressionState` leaves both fields at 0). The corpus cannot discriminate it; an earlier revision wrongly claimed it could |
| the `value == 0` arm writes the literal base | **REFUTED**: the source writes a literal 0, and that is the arm that moves one map chunk |
| `declared % 4 == 0` is a valid container test | **REFUTED**: 199 real selector streams declare `4k + 2` bytes |
| a form-0 header means raw stored bytes | **CONFIRMED**, with the correction that it makes form 0 non-discriminating |

**Arbitration rule used.** Where a literal transcription of the external source
fails to reproduce the project decoder's bytes on the canonical corpus, the
reproduction uses the reading that passes and the discrepancy is documented. The
project decoder is independently validated (LOGX-CODEC-001: 4,322 / 4,322
containers, two implementations, end markers at the declared sizes); the external
source is not. That rule was applied to **one** arm in the end - the four-bit
code's `value == 0` arm, where the source and the project decoder genuinely
differ. An earlier revision also applied it to `GetInteger` and to the initial
literal state, and both of those "discrepancies" turned out not to exist: the
reviewers refuted them and the corrections are recorded below.

---

## UNRESOLVED QUESTIONS

1. Which consumer reads the 387 referenced residual containers (named sites:
   `0x08004EFC`, `0x082607FC`, `0x082AD8E8`, `0x08028118`, `0x081906BC`, and the
   table around `0x087B5B64`)?
2. Do those residual containers overlap LOGX-CODEC-001's 3,819 non-root dominant
   reach? A set comparison was not performed.
3. Is the 78-container decode divergence one mechanism or two? Two are identified -
   the external `value == 0` arm (one map chunk) and the escape's offset reset (77
   banks) - but the 77 were not traced token by token.
4. What does the initial literal state change on the **scan population**? It is
   inert on the known corpus; a reviewer measured a small number of changed
   accepted positions when the field is set to the kind word instead of 0. The
   reproduction follows the source and leaves it at 0.
5. Portrait recall: unmeasured because the class was not enumerated.
6. A justified set of engine graphics-size constraints, which would tighten the
   residual further.

---

## HANDOFF TO LOGX-SYNTHESIS-001

1. The external scanner is a **recall instrument**, not a detector: 100% sprite
   recall, 5,065 residual candidates whose payloads are read-back bytes.
2. **Form 0 is the precision cliff**; a scanner must require an engine reference
   or structural agreement for the stored form.
3. **`declared % 4 == 0` is wrong** and costs 199 real containers. It must not
   appear in project tooling.
4. The **387 referenced residual candidates** are the next concrete
   reverse-engineering target. They are not one homogeneous block: 129 declare 256
   bytes, 97 declare 4,096, only 26 reach 8 KiB, and the table around `0x087B5B64`
   names several of the largest - read that table first.
5. Two stale figures in shipping code belong to SYNTHESIS: `sprite_graphics.py`'s
   `7,355` distinct containers (LOGX-FRAME-001's accepted 12-byte walk gives
   **7,390**) and the module's 16-byte piece walk.

## PRODUCTION FOLLOW-UPS

None implemented here. Recorded, not repaired:

- `tools/webfoot/formats/sprite_graphics.py`: `PIECE_SIZE = 16` and the
  `unknown_raw` 6-byte field are the superseded layout; `decode_animation`'s
  `maximum_frames = 64` is the known-bad unbounded animation walk; its docstring's
  `7,355` container figure is stale (7,390).
- `tools/webfoot/atlas_producers/scan.py` `_compression_rows` is a stride-4
  heuristic sweep whose own docstring calls its output noise; it is unaffected by
  this ticket and remains out of the SDK's canonical path.

---

## REVIEWER A (scanner algorithm / codec / reference validation)

Two fresh-context reviewers ran against the **frozen** revision `142d308`, each
re-measuring the image independently. Both returned **BLOCK** on the first pass.
Their reports are summarised here; the raw reports are the reviewers' own.

**Verdict at `142d308`: BLOCK.**

Independently reproduced by Reviewer A: the scan population (8,388,093 / 29,504 /
27,775 / 13,463 / 16,041), the external totals, the known corpus and its
per-class sizes, per-class recall, the reference search (2,097,152 word
positions), the whole portable suite (1,493 passed, 16 skipped), the ROM-gated
suite (26 passed; 2 passed / 24 skipped with the image absent), determinism (two
`--json` runs byte-identical), and canonical-image integrity (SHA-256 identical
before and after, mtime unchanged). All replicated exactly.

**Blocking findings:**

1. `logx_gfxscan_probe.py:514-516` - the four-bit code's `value == 0` arm wrote
   `literal_offset & 0xFF` (the **project** decoder's arm) where `JCALG1.cs:102-105`
   writes a plain `0`. Reviewer A rebuilt the C# independently and measured that
   the arm moves one known container. **ACCEPTED.**
2. The §3.3/§9.3/§11.2 `GetInteger` "arbitration" was inverted: the document
   claimed a literal reading of `while (GetBit() != 0)` fails on 11,513 of 11,513
   containers, but the probe's loop **is** that reading written from the other
   side. **ACCEPTED.**
3. The §9.3 literal-offset argument was vacuous: **0** of 11,712 kind-1 known
   containers (0 of 7,390 sprites) emit a literal before their first escape, so
   the initial value cannot be observed. **ACCEPTED.**

**Non-blocking findings, all accepted:** the initial `literalBits` should be the
C# default 0, not the kind word; `get(0)` behaviour differs from C# `GetBits(0)`;
the §8 "cannot overrun" mechanism was stated wrongly (the loop cannot cross its own
bound, rather than a `catch` discarding an overrun); the FP class conflated two
mechanisms; `flag_nested_candidates`'s docstring described the opposite call
order; the 381-residual characterisation was wrong (26 of 387 are >= 8 KiB, the
largest is 65,474, and the arithmetic did not close); the `UnknownHeader` offset
was `container + 8` instead of `container + 4`; `resolve_offset` is test-only; and
the committed ticket still carried placeholder SHAs.

## REVIEWER B (census / false-positive / graphics-semantics adversarial)

**Verdict at `142d308`: BLOCK.**

Independently reproduced by Reviewer B: the scan population (by its own raw byte
loop), the external totals, the sprite class (by an independent per-record walk
through `logx_frame_probe`), per-class recall with the `declared % 4` histogram,
the engine models, the candidate categories, the residual arithmetic, the
reference search with 10 rows re-verified against its own word index, the tests,
and canonical-image integrity. All replicated exactly.

Reviewer B also verified the **graphics-semantics discipline** as PASS: no decode
is promoted to graphics anywhere, and the sprite class is the only recall
denominator. It confirmed the suitability verdicts follow from the measurements
and that scope compliance and ROM safety are clean.

**Blocking findings:**

1. The FP class named "inside a known container" counted candidates whose owner was
   **not** a known container: 0 external / 4 aligned / 267 unconstrained are truly
   inside one, against the 2 / 7,088 / 15,587 the documents reported, and 1,086 of
   them are form 1 rather than "all form 0". **ACCEPTED.**
2. The corpus classes are not disjoint and the printed equation was false:
   `7,390 + 3,745 + 392 + 187 + 2 + 1 = 11,717 != 11,715`, because
   `zero_header_form0_containers` re-lists two addresses already in
   `root_48_selector_streams`. **ACCEPTED.**
3. The residual population was materially mischaracterised ("381 are packed,
   tile-aligned and 8 KiB or larger"; "all 387 ... largest 38,400 ... all confirmed
   by the external model"): measured, 21 satisfy that conjunction, 26 of 387 reach
   8 KiB, 381 of 387 are whole-tile, 381 of 387 are external-confirmed, and the
   largest is 65,474. **ACCEPTED.**
4. The overlap section used the mislabeled FP numbers as if they were nested-flag
   counts (12,612 / 21,610), and the provenance arithmetic
   `700 + 7,088 + 5,065 = 12,853 != 11,097`. **ACCEPTED.**
5. `graphics_evidence` emitted "no engine reference established" on all 414 rows
   whose own status field says ENGINE-REFERENCED, and an integration test asserted
   the contradictory string. **ACCEPTED.**

**Non-blocking findings, accepted:** the module docstring mis-described the
external model; category E is unreachable; `residual_with_a_known_payload: 0` is
definitional; the nested-flag docstring inverted the call order; the 791 rejection
reason was described as "decodes but does not reach the declared size"; the
`1,453 + 7 != 1,478` sentence omitted the 18 F candidates; and the ROM-gated suite
could not catch the class overlap.

## REQUIRED CORRECTIONS

All five blocking findings and every non-blocking finding above were closed. Each
was first reproduced independently before being accepted:

| # | Correction | Where | Verification |
| --- | --- | --- | --- |
| 1 | `value == 0` arm now writes a literal `0` | `logx_gfxscan_probe.py` | differential re-measured: 11,634 agree / **78** differ; the 78th is `0x0829B308`, a map chunk; bank count unchanged at 77 |
| 2 | `GetInteger` passages corrected: the probe **is** the source's loop; the "refuted" reading was a transposition no source contains | provenance §3.3, §9.3, §10, §11.2; ticket disagreements | reviewer A's 20,000/20,000 bit-stream comparison accepted |
| 3 | literal-offset argument replaced: source-authoritative, with the corpus explicitly recorded as unable to discriminate and 0/11,712 as the measurement | provenance §3.3, §9.3 | the "0 literals before the first escape" measurement reproduced here |
| 4 | initial `literalBits` is now the C# default 0 | `logx_gfxscan_probe.py` | known-corpus result unchanged (11,634 / 78 / 0 raises); inert, as measured |
| 5 | FP classes split: `wrapper_start_inside_a_known_container` is `container_containing` only; nesting gets `wrapper_start_inside_another_candidate` | `logx_gfxscan_probe.py`, both documents, both test suites | 0 / 4 / 267 and 2 / 7,084 / 15,320 measured; nested flags 4 / 12,612 / 21,610 measured separately |
| 6 | unknown-header offset corrected to `container + 4` | `logx_gfxscan_probe.py`, provenance §7.5 | `Skip(0x4)` then a fresh reader's first `AdvanceBuffer` |
| 7 | corpus classes documented as non-partitioning; `class_size_sum` and `class_overlap` reported; overlap asserted by address in the ROM-gated suite | `logx_gfxscan_probe.py`, both documents, ROM tests | 11,717 vs 11,715 and the two addresses measured |
| 8 | residual characterisation replaced with the measured size distribution; the 21/26/378/381/387 figures asserted | both documents, ROM tests | distribution measured from the report rows |
| 9 | overlap section rebuilt from `nested_candidate_flags` and the corrected FP split | provenance §7.3, §8; ticket overlap section | form-0 breakdown audited to close: 3 + 7,084 + 4 + 27 + 3,979 = 11,097 |
| 10 | `graphics_evidence` now says "no rendering consumer established"; the test asserts it | `logx_gfxscan_probe.py`, ROM tests | 414 ENGINE-REFERENCED rows no longer contradict their own status |
| 11 | module docstring, `flag_nested_candidates` docstring, category C/E note, `residual_with_a_known_payload` note, 791-rejection wording, `1,453 + 7 + 16` sentence, and the ticket's placeholder SHAs all corrected | both documents, `logx_gfxscan_probe.py` | - |
| 12 | every stale count in both documents re-derived from a fresh full run and re-asserted in the ROM-gated suite | both documents, ROM tests | 31 ROM-gated tests pass |

## REJECTED REVIEWER ASSERTIONS

None. Every blocking and non-blocking finding from both reviewers was reproduced
and accepted. Two findings needed their *direction* restated rather than their
substance corrected, and both are recorded:

- Reviewer A's BLOCK-2 ("the `GetInteger` arbitration is inverted") is correct
  about the document and wrong about the code: the probe's loop was already the
  source's loop, so the fix is to the prose, not to the decoder. The `integer()`
  docstring now says so explicitly.
- Reviewer B's finding that category E is unreachable is accepted as a **reporting**
  defect, not as a missing measurement: C and E describe the same predicate on this
  corpus, so E is reported empty and `CATEGORY_EQUIVALENT_NOTE` states why. No
  population was fabricated to fill it.

## CORRECTION GATE

- Both reviewers' measurements were reproduced locally before any edit; no
  correction rests on a reviewer's number alone.
- After the corrections, every measurement that changed was re-derived from a
  **fresh** full run, and every changed number is pinned by a ROM-gated test.
- The corrections changed no ROM-derived artefact and no shipping code; the two
  documents and the probe are the only files touched.
- Re-review of the corrected revision: both reviewers were asked to verify their
  own required corrections against the corrected revision; their verdicts are
  recorded below.
- The reviewed revision was `142d308`. It has been superseded by a single commit
  carrying the corrections and the LF line endings the repository uses. Nothing in
  `142d308` was edited after review; the corrections are new revisions, and the
  branch was amended repeatedly while the two review rounds ran, so the review
  documents name it by subject. The exact final SHA is reported in the isolated
  ticket result.

## RE-REVIEW OF THE CORRECTED REVISION

---

## GIT STATUS

```text
branch logx-gfxscan-001, worktree <temp>\log1-remake-logx-gfxscan-001

8dad4a2  research(gfxscan): validate Buu graphics discovery
         (the reviewed revision was 142d308; this one commit is that same revision
          with every correction from both review rounds applied and the files
          re-encoded to the repository's LF line endings. The branch was amended
          while the reviews ran, so no intermediate amend hash is named.)

files added/changed vs START SHA 421ac94012a7cf7ace110685f1a639811f27702b:
  A tools/research/logx_gfxscan_probe.py
  A tests/unit/test_logx_gfxscan_probe.py
  A tests/integration/test_logx_gfxscan_rom.py
  A docs/research/LOGX_GFXSCAN_PROVENANCE.md
  A docs/research/LOGX-GFXSCAN-001-review.md

staged ROM/save/state/dump/image/decoded-asset files: none
git diff --check: clean
canonical ROM SHA-256 before and after: unchanged (940AD5F0...F059E)
```
