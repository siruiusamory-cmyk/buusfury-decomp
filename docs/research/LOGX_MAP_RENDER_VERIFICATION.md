# LOGX map render verification

The selected-map root layout of Buu's Fury, verified against the canonical image.
Static analysis only; no runtime capture was made for this pass.

Canonical ROM SHA-256, before and after:
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`

Evidence document: [`LOGX_MAP_RENDER_PROVENANCE.md`](LOGX_MAP_RENDER_PROVENANCE.md).
## External claims tested

The external hypothesis source is `mainant/LOGExtractor`, `MapViewer/MainForm.cs`
(`ReadMapsFromROM`, `UxMapCanvas_Paint`) and `MapViewer/Gba/ROM.cs`, current
`main` observed 2026-09-15 in the accepted predecessor. Its claims about the
selector-1 root were treated as claims only.

## Root consumers found

**CONFIRMED.** The selector-1 root is consumed as a *load-time map definition
template*, not as a runtime render structure.

| consumer | role |
| --- | --- |
| `0x080089CC` | accepted selector resolver; `source + 4*(selector-1)` |
| `0x080089A0` | selector default helper; non-zero returned unchanged, else `1` when `MapEntry+0x28` is null |
| `0x0800953E` | the root consumer: copies root scalars into the RAM map-state structure and dispatches root pointer fields to the graphics, layer, and object loaders |
| `0x0800938C` | reads the root back from destination `+0x8C`, programs `BG0CNT..BG3CNT`, the palette, and `DISPCNT` |
| `0x08009670` -> `0x08012664` | forwards the exact `root+0x40`/`+0x44` pair to the spatial-object registry population routine |
| `0x08009BD4` | reads `root+0x48` directly as a compressed container |

Evidence type: instruction access-width evidence, caller/callee
cross-reference, and read-only decompilation. `0x0800953E` has exactly two
callers, both MapEntry load flows (`0x08008BD0`, `0x08009078`).

**PROJECT OBSERVATION.** A full-ROM sweep found **zero** `LDR Rd,[PC,#imm]`
literals inside the 452-root address range, so roots are reachable only through
`MapEntry+0x2C`.

## Selector behavior

**PARTIALLY CONFIRMED, and narrower than "selector 1 only".**

- `0x080089CC` performs `ldr [r0,#0x2c]`, `lsls r1,#2`, `adds`, `subs #0x40`,
  `ldr [r0,#0x3c]`, i.e. one effective access at `source + 4*selector - 4`.
  Selector `1` reads `source + 0x00`.
- Both zero-selector call sites pass `r3 = 0` (`0x08008D48`, `0x08008E84`)
  into `0x08008B30`, so the helper resolves them to `1`.
- Both accepted Level 3 runtime captures were selector `1`.
- However, 55 of 452 MapEntries expose a source array with more than one valid
  word (run lengths 2..12; one each at 6..10 and 12). The engine never bounds
  the array in the examined paths, so selectors above `1` are structurally
  possible and were **not** excluded.

## Root layout findings

All widths below are the width the engine actually uses. "Pointer" means only
4-byte aligned and inside the 8 MiB image.

| field | classification | finding |
| --- | --- | --- |
| `+0x08` | **CONFIRMED** | unsigned LE halfword, `ldrh` at `0x0800958A`; horizontal map extent in pixels stored as `extent - 1`; camera maximum is `extent - 1 + 239` |
| `+0x0A` | **CONFIRMED** | unsigned LE halfword, `ldrh` at `0x08009592`; vertical map extent, same `-1` bias, camera maximum `+159` |
| `+0x0C` | **CONFIRMED** (count) | 32-bit count, null on 274 roots |
| `+0x10` | **CONFIRMED** (pointer) | 32-bit aligned in-ROM pointer, null on exactly the same 274 roots |
| `+0x14` | **CONFIRMED** (pointer) | aligned in-ROM pointer on all 452 roots, 330 distinct, to a layer record |
| `+0x18` | **CONFIRMED** (pointer) | aligned in-ROM pointer on all 452 roots, 319 distinct |
| `+0x1C` | **CONFIRMED** (pointer) | aligned in-ROM pointer on all 452 roots, 398 distinct |
| `+0x20` | **CONFIRMED** (pointer) | aligned in-ROM pointer on all 452 roots, 420 distinct |
| `+0x40` | **CONFIRMED** (count) | 32-bit count in `1..14`, null on 104 roots |
| `+0x44` | **CONFIRMED** (pointer) | aligned in-ROM pointer, null on exactly the same 104 roots; dereferenced as `ldm` of `root+0x40`/`+0x44` at `0x08009676` |
| `+0x48` | **CONFIRMED** (pointer) | aligned in-ROM pointer on all 452 roots; compressed container, length at target `+0x04`, decompressor `0x0803D940` |

Additional confirmed physical facts not in the external hypothesis: `+0x00` is
a halfword read whole (`0x08009630 ldrh`); `+0x02`/`+0x03` are bytes
(`0x08009634`, `0x08009638`); `+0x04..+0x07` are four bytes added to
`BG0CNT..BG3CNT`; `+0x24`/`+0x28` are a null-coupled count/pointer pair walked at
a 0x18-byte element stride by `0x08009420`; `+0x34`/`+0x38` are decompressed by
`0x0803D940` into 0x2000-byte buffers; `+0x3C` selects an engine table row;
`+0x4C` is the single word `0x08179764` on every root.

Three count/pointer pairs (`+0x0C`/`+0x10`, `+0x24`/`+0x28`, `+0x40`/`+0x44`)
are each exactly null-coupled; no root has a count without a pointer or the
reverse.

## Interpretation classifications

| interpretation | classification |
| --- | --- |
| four-layer interpretation | **CONFIRMED** , four layer-record pointers consumed by one layer-construction subsystem |
| BG0/BG1/BG2/BG3 interpretation | **PARTIALLY CONFIRMED** , slot order is added to `BG0CNT..BG3CNT` in order, but a direct per-slot assignment was not proven |
| animated-tile interpretation | **PARTIALLY CONFIRMED** , the record loader `0x08009B12`, its frame/tile/destination field widths, and the VRAM copy target are established, but the instruction that reads `+0x0C`/`+0x10` out of the root was not recovered |
| connector interpretation | **PARTIALLY CONFIRMED** , count and pointer are confirmed and the only consumer registers spatial objects; no transition semantics established |
| tileset/index-stream interpretation | **PARTIALLY CONFIRMED** , compressed delta-coded u16 selector stream confirmed; bank/tile indexing semantics not re-verified here |
| selector-1 root semantic identity | **CONFIRMED** as a structural per-map load-time template; name-level semantics unresolved |
| selector usage/range | **PARTIALLY CONFIRMED** |

## Full-census results

452 records, 452 valid sources, 452 valid selector-1 roots, 0 null roots, 421
distinct roots, 11 shared-root groups. Root range
`0x0817B1B0..0x082B8C38`. Source-array run histogram: 397 records with one valid
word, 38 with 2, 6 with 3, 3 with 4, 2 with 5, and one each with 6, 7, 8, 9, 10,
and 12 (55 records expose more than one selector).

Largest shared groups: `0x0822CC08` x10 (maps 163,172,175,182,184,189,194,197,201,203);
`0x0829C2D8` x5 (maps 24,25,26,27,28); three x4 groups and five x3 groups.

Layer-slot target handlers over 1808 slots: `0x08008087` x1516, `0x08007A41`
x249, `0x0800897B` x41, `0x08007B63` x1, `0x080088BD` x1.

## Representative roots

| map | key bytes | source | selector-1 root | `+08`/`+0A` | `+0C` | `+40` | `+44` | `+48` | `+50`/`+54` |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| 0 | `0001` | `0x080728CC` | `0x082B8C38` | `0x0311`/`0x0001` | 0 | 0 | 0 | `0x082B8BF4` | 0 / 0 |
| 1 | `0002` | `0x080728D4` | `0x082B5FA0` | `0x0001`/`0x0001` | 0 | 0 | 0 | `0x082B5F94` | `1` / `0x800` |
| 2 | `0003` | `0x080728D8` | `0x082B5F28` | `0x0001`/`0x0001` | 0 | 0 | 0 | `0x082B5F1C` | `0x08008087` / `0x400` |
| 39 | `010B` | `0x080753F0` | `0x08294968` | `0x0179`/`0x0109` | 2 | 2 | `0x08294960` | `0x08294660` | `1` / `0x800` |
| 100 | `0317` | `0x080782F4` | `0x0826AD50` | `0x0001`/`0x0001` | 0 | 0 | 0 | `0x0826AB94` | `1` / `0x800` |
| 225 | `090F` | `0x0807F930` | `0x08216A18` | `0x0001`/`0x0051` | 0 | 1 | `0x08216A14` | `0x08216684` | `1` / `0x800` |
| 338 | `0E05` | `0x08087C40` | `0x081DAD0C` | `0x0051`/`0x00A1` | 1 | 3 | `0x081DAD00` | `0x081DA6E4` | `1` / `0x800` |
| 451 | `1601` | `0x0808E1E0` | `0x0817B1B0` | `0x0051`/`0x00A1` | 2 | 0 | 0 | `0x0817A75C` | `1` / `0x800` |

The set covers the beginning, early-middle, middle, late-middle, and end of the
table, plus null-candidate-field outliers (maps 0, 1, 2, 100, 451), a
multi-layer root (map 39), and the handler-variant roots. Text labels are not
used as proof of any field's meaning.

## Anomalies

- Map 0 is the only root with `+0x50` = `0`, `+0x54` = `0`, no connectors, and
  a `0x0311`/`0x0001` extent pair.
- Map 295 is the only root with `+0x50` = `0x0800897B`.
- Map 19 is the only root with non-zero `+0x3C` (value `1`).
- Map 39's `+0x14` slot points at the shared zero-dimension record
  `0x080707FC` (handler `0x08007A41`), the engine's absent-layer form; 98 roots
  do this in the `+0x14` slot specifically.
- Roots and layer records share a handler vocabulary: `0x08008087` appears both
  as a root `+0x50` value (36 roots) and as a layer-record `+0x00` handler.
- `+0x0C`/`+0x10` maximum count is 6 while `+0x40` maximum is 14.

## Tooling added

- `tools/research/logx_map_render_probe.py` : deterministic, read-only, and
  explicit about candidate offsets. It validates the 8 MiB canonical size, emits
  the input SHA-256 in its report, and assigns no semantic names. Full-census
  mode emits all 452 records with every `+0x00..+0x5C` field plus aggregate
  statistics, null/aligned/in-ROM/out-of-ROM counts, shared roots and sources.
  SHA gating is enforced by the regression test, which asserts the canonical
  digest before calling `analyze`.
- `tools/ghidra/LogxRootConsumers.java` : read-only Ghidra headless report that
  refuses any program whose MD5, SHA-256, or language differs from the canonical
  profile, refuses output outside `build/ghidra/reports/`, seeds only the
  supplied Thumb entry addresses, and reports blind state, boundaries, callers,
  callees, entry and outgoing references, referenced addresses, disassembly,
  and decompilation. It writes no markup back.
- `tools/ghidra/run-logx-root-consumers.ps1` : wrapper enforcing the ignored
  report path and a freshly-written report.

## Tests added

`tests/integration/test_logx_map_render_rom.py`, 12 tests. Only independently
established findings are encoded: the 452 valid aligned roots, the seven
representative roots, `selector_1_root == ROM[source]` for all 452 records, the
uniform alignment/in-ROM status of the six pointer fields, the `ldrh`-observed
halfword widths and representative extent values, exact null-coupling of all
three count/pointer pairs, the 11 shared-root groups, the multi-word source
count, the single shared `+0x4C` word, the documented module invocation, and
rejection of a non-canonical input size. No LOGExtractor hypothesis is asserted.
The file skips cleanly when the ROM is unavailable.

## Test results

- **MEASURED** `pytest tests/integration/test_logx_map_record_rom.py
  tests/integration/test_logx_map_render_rom.py -q` -> `16 passed`.
- **MEASURED** the new file alone with no ROM configured ->
  `2 passed, 10 skipped`; the ROM-gated tests skip cleanly and the two
  non-ROM-gated tests (input-size rejection and the module invocation guard's
  skip path) still run.
- **MEASURED** `pytest tests/integration/test_map_render_rom.py
  tests/integration/test_local_maps_rom.py
  tests/integration/test_local_map_entry_roundtrip.py
  tests/unit/test_map_render.py tests/unit/test_maps.py
  tests/unit/test_map_entry.py -q` -> `49 passed, 46 skipped, 15 errors`.
  The 15 errors are all
  `PermissionError: [WinError 5] Access is denied:
  <pytest temporary root>` raised during `tmp_path`
  fixture setup, i.e. an environment temp-directory restriction, not a record
  failure.
- **MEASURED** the same three affected files re-run with a writable
  `--basetemp` -> `18 passed, 52 skipped`. The skips are the pre-existing
  `roms/` path expectation, which this fresh worktree does not satisfy; those
  tests are unmodified by this record. No record-caused failure remains
  unresolved.
- No full-suite run: this change adds isolated read-only research tooling, one
  new regression file, and documentation. It changes no production parser,
  codec, build, profile, or shared-library code, so the blast radius is bounded
  by the focused runs above.

## Physical facts recorded

`docs/reverse-engineering.md` gained one section, "LOGX-MAP-RENDER-001 selected
map root", documenting only engine-confirmed physical readings: access widths
with the instruction that establishes each, the extent interpretation and its
`-1` bias, the three null-coupled count/pointer pairs, the layer-record target
shape, the container at `+0x48`, the shared `+0x4C` word, and the
no-literal-root observation. Field names that remain provisional
(width/height, BG slot assignment, animated-tile identity, connector record
layout, `+0x30`, `+0x50..+0x5C`) are explicitly listed as not promoted.

## Disagreements with LOGExtractor

1. The selector-1 value is not "the map render structure"; it is a load-time
   per-map definition template consumed by a map-state loader. The renderer is
   downstream.
2. `+0x08`/`+0x0A` are already `extent - 1`; adding the viewport is correct in
   effect but the stored value carries a `-1` bias LOGExtractor does not model.
3. The root is not only the render-relevant graphics container LOGExtractor
   models: `+0x34`/`+0x38` are two more independent compressed payloads handled
   by the same decompressor, `+0x24`/`+0x28` and `+0x40`/`+0x44` are object lists
   outside the render path, and `+0x4C` is engine-global rather than per-map.
4. LOGExtractor's 24-bit pointer masking is not used; all pointer claims require
   alignment plus containment in the 8 MiB image.
5. The `+0x44` "connector pointer list" record layout was **not** reproduced;
   only the count/pointer dereference is confirmed.

## Unresolved questions

- Which instruction reads `root+0x0C`/`+0x10` out of the root?
- Does any executable path pass a selector other than `1`, and what chooses it?
- What object types populate `+0x24`/`+0x28` (0x18-byte elements, dispatch targets
  `0x0800CE1A`/`0x0800D15A`) and `+0x40`/`+0x44`?
- What are `+0x30`, `+0x50`, `+0x54`, `+0x58`, `+0x5C`? The `+0x50`/`+0x54`
  handler+size shape hints that the root is itself a layer-record-family member.
- Do the layer/animation fields differ between selector variants of one
  MapEntry?
- What are the true units of `+0x08`/`+0x0A` (pixels versus tiles)?

## Downstream consumers

- **LOGX-LAYER-001** : handler vocabulary and layer-record constructor
  `0x08007B78`, chunk dimensions as separate bytes, the 4-chunk cap, the shared
  absent record `0x080707FC`, and the camera streaming range
  `0x08007C82..0x08007E63`.
- **LOGX-TILE-001** : delta-coded selector stream at `+0x48`, shared atlas
  `u32[]` at `+0x4C` = `0x08179764`, VRAM copier `0x08009C62..0x08009C78`.
- **LOGX-CONNECTOR-001** : `+0x40`/`+0x44` count/pointer dereferenced by
  `0x08009670` into registry routine `0x08012664`; record layout open; do not
  attribute the `0x18`-stride pointer walk at `0x08008C00..0x08008C1C` to the
  root, because it reads MapEntry `+0x05`/`+0x18`. MapEntry `+0x05` there is the
  length of the `+0x18` pointer array (values `{0:399,1:24,2:14,3:5,4:6,5:3,19:1}`,
  null exactly when `+0x18` is null), not a small flag, so `+0x18` is a
  variable-length record list with the count at `+0x05`.

## Independent verification

**Verification:** independent claim-verification pass, independent context, read-only,
separate from the implementation.

**Verdict: `APPROVE WITH REQUIRED CORRECTIONS`.** The verification pass re-derived the
ROM hash before and after and found it unchanged, confirmed no tracked file was
modified during its pass, and independently recomputed the census. Seven of the
eight claim groups were `CONFIRMED` with exact bytes and addresses reproduced
independently. One claim group was **`REFUTED` as worded**, and six concrete
documentation errors were found. All were corrected before commit:

| finding | resolution |
| --- | --- |
| **REFUTED:** "zero `LDR Rd,[PC,#imm]` literal loads in the root range in the image" | The negative was an artefact. A resynchronising sweep finds 19,784 such Thumb literals plus 568 ARM, all with instruction addresses inside the root data region, where bytes are data, not code. Rewritten to "no **code** loads or computes a root address by PC-relative constant", and the intended conclusion is now carried by an artefact-free route: exactly 453 word-aligned ROM words hold a root value (452 `+0x2C` slots plus a stray at `0x0837F900`), bounding any loading instruction to the preceding 1024 bytes, where an exhaustive search yields three data-region candidates with no callers, against ~3.5 expected by chance. |
| source-array run table summed to 451 | Corrected to eleven separate rows summing to 452 (`{1:397,2:38,3:6,4:3,5:2,6:1,7:1,8:1,9:1,10:1,12:1}`). |
| `+0x50` alignment column said "0 (37 unaligned)" | Corrected to "0 (451 unaligned)"; 451 of 452 values are odd, i.e. Thumb-bit-set code pointers, and the `37` was a misread count. `+0x54`'s single unaligned value `0x266` is now also stated. |
| "37 occurrences of `0x08008087` across the four layer-pointer targets" | Removed. Measured: 36 root headers, all at `+0x50`; 1516 layer-target first words; 0 layer slot values. The section now states the 1808-slot handler census directly. |
| `+0x24`/`+0x28` described as a "12-byte stride" in the findings and unresolved-questions sections | Corrected to a 0x18-byte element stride in every location, consistent with `0x08009452/54/58`. The same error was corrected in `docs/reverse-engineering.md`. |
| glibc `param_1 + 0x27` annotated "dest +0x4E" | Corrected to `dest +0x9C`; `strh r0,[r4,#0x1c]` with `r4 = param_1 + 0x80`. |
| MapEntry `+0x05` annotated "a count, 1..3" | Corrected with the measured distribution and the `+0x18` coupling, and the missing `cmp`/`ble` guard was added to the snippet. |

**Cross-checks that passed unchanged:** root resolution for maps 0, 1,
2, 39, 451; all 17 header fields of root `0x08294968`; every instruction address
in section 4; the resolver bytes and its exactly three `BL` callers; the
`0x08009670` bytes, its literal `0x080716C4` -> `0x03002A64`, and its single
caller; the `0x08009BD4` container reads and the delta decode; the full census
(452 aligned roots, 421 distinct, all distinct counts, all three null-couplings,
`+0x40` max 14, `+0x4C` shared); all 11 shared-root groups; the layer-handler
census 1516/249/41/1/1 over 1808 slots; 98 roots and 249 slots pointing at
`0x080707FC` with dimensions `0`x`0`; the `+0x34`/`+0x38` container length word
`0x2000` on all 452; and the `BG0CNT..BG3CNT` store addresses.

**Required-correction gate: CLOSED.** Every verification pass finding was independently
re-verified by the author against the ROM before being applied, and every
one reproduced; no finding was accepted on the review pass's authority alone and no
finding was left unaddressed.

**Closeout follow-up.** During canonical closeout a systematic search for the
superseded wording found three residual instances of the corrected `12`-byte
stride inside this review document's own findings and unresolved-questions
sections, and one run-length sentence that omitted the tail of the histogram.
Those were corrected in the closeout commit without touching the accepted
research commits. The corrections table above now names every affected section,
and this document contains no remaining instance of the superseded values.
