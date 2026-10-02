# Correcting the packed-container literal-base reset

The decoder correction that clears a 7-bit run's literal base on return to 8-bit
literals: the defect and the rule, the measured blast radius and the runtime
proof.

## 1. The defect and the rule

`MAP-GFX-DIAG-001` proved, against the retail engine's own character memory, that
the packed-container grammar **clears the literal base when the stream returns to
8-bit literals**. The shipping decoders kept it:

```python
literal_bits = 7 + reader.bit()
if literal_bits != 8:
    literal_base = reader.get(8)     # 8-bit literals kept the previous base
```

A stale base is added to every following 8-bit literal, so a container keeps its
token structure and its tile geometry and shifts its palette indices. That is why
the symptom looked like "correctly shaped tiles in the wrong colours" rather than
garbage.

The rule itself is not new knowledge in this repository: the external JCALG1
model in `tools/research/logx_gfxscan_probe.py` already reset the offset
(`literal_offset = 0` before the conditional read), and
`docs/research/LOGX_GFXSCAN_PROVENANCE.md` §3.3 had recorded the reset - as a
*difference* attributed to the external tool rather than as the project's bug.
This record reverses that attribution on the engine's own evidence.

## 2. Implementation

| File | Change |
| --- | --- |
| `tools/webfoot/formats/webfoot_lz.py::_unpack_stream` | `literal_bits == 8` clears `literal_base`; module docstring states the rule and its provenance |
| `tools/export/webfoot_strict.py::decode_packed` | the identical rule, so the export path and the SDK cannot disagree |
| `tools/research/webfoot_codec_reference.py::decode_packed` | the same rule. **Third path, added deliberately**: this module is the differential's second implementation and had transcribed the same defective rule, so `tests/integration/test_logx_codec_rom.py::test_every_packed_container_decodes_identically` compares against a decoder that was wrong in the same place. Correcting it is the same semantics change, not an additional one |

Nothing else changed: no token, no distance ladder, no container layout, no
termination rule, no encoder. The encoder emits 8-bit literals without ever
narrowing, so `pack`/round-trip behaviour is untouched.

Tests:

- `tests/unit/test_webfoot_lz.py` - the strict `xfail` spec test
  `test_widening_back_to_eight_bit_literals_clears_the_literal_base` now passes
  and its marker is **deleted**, as the diagnostic record required. A second,
  new test replays the same synthetic stream under the pre-correction grammar and
  requires `0x51` instead of the engine's `0x11`: the pair is a regression with a
  mutation control rather than a restatement.
- `tests/unit/test_logx_gfxscan_probe.py`, `tests/integration/test_logx_gfxscan_rom.py`,
  `tests/integration/test_map_render_rom.py` and
  `tests/integration/test_asset_export_rom.py` - re-baselined, every value
  attributed in place.

## 3. Blast radius - measured, not assumed

`build/gfxdiag/probe_correction_rebaseline.py` (ignored, read-only) decodes every
candidate class twice: once through the production path and once through an inline
replay of the *same grammar with the single changed rule*, so each difference is
attributable to that rule and nothing else. Measured on the canonical image
(SHA-256 `940ad5f0...f059e`):

| Population | Containers whose decode changes |
| --- | ---: |
| root `+0x4C` graphics banks | **77 / 187** |
| assembled map character blocks | **369 / 452** (27,804 tile slots) |
| map chunk containers | **0 / 3,745** |
| sprite graphics containers | **0 / 7,390** |
| map selector streams | **0 / 452** |
| animated-tile frames (raw streams) | **0 / 2,721** |

The 369 and the 77 agree with what `MAP-GFX-DIAG-001` predicted, and the zeros
are why the map *layout*, palette, flips, screen entries and layer records do not
move.

**Byte-level attribution.** For each changed bank the probe records, per output
byte, the literal emission it descends from, and predicts the changed set as the
closure of emissions made while a non-zero stale base was in force. Predicted and
observed sets are **equal on 77 / 77 banks** (307,890 changed bytes in total). No
changed byte is unexplained, which is what makes this a correction rather than a
regeneration.

## 4. Re-baselined pins

Every value below was recomputed through production code
(`build/gfxdiag/recompute_pins.py`, `recompute_export_pins.py`,
`recompute_gfxscan_pins.py`), and each changed pin is attributed to a source that
the blast radius above independently says changes. Unchanged entries are kept as
the control.

### 4.1 `tests/integration/test_map_render_rom.py`

| Pin | Old | New | Attribution |
| --- | --- | --- | --- |
| `map:0039` `char_sha256` | `e0d04925...5839e` | `4c7167a3...c2c46` | map 39: 32 tiles change |
| `map:0039` `composite_sha256` | `35d3b51f...8ed2b` | `0de70425...9bc04` | same block |
| `map:0040` `char_sha256` | `48601230...f14a7` | `0d17922e...67b0d` | map 40: 5 tiles change |
| `map:0040` `composite_sha256` | `21985e5c...c70f9d` | `d1519793...12d66` | same block |
| map 39 `char_mutations` | 49 entries | 17 (`879..895`) | the 32 removed are exactly the decode-error tiles of the diagnostic §3.8; all are inside the pinned animation ranges |
| map 40 `char_mutations` | 38 entries | 33 (`239..258`, `879..891`) | the 5 removed are the diagnostic's 5 decode-error tiles |

### 4.2 `tests/integration/test_asset_export_rom.py`

All of these are pixel digests rendered **through a map's assembled character
block**, so a changed pin must name a map in the 369.

| Pin | Changed | Attribution (map, changed tiles) |
| --- | --- | --- |
| `EXPECTED_SCREENBLOCK_SHA256` (map 19) | yes | map 19, 117 |
| `UPLOADED_SCREENBLOCK[(7,3)]` | yes | map 7, 79 |
| `UPLOADED_SCREENBLOCK[(8,2)]`, `[(8,3)]` | yes | map 8, 79 |
| `UPLOADED_SCREENBLOCK[(8,0)]`, `[(8,1)]`, `[(20,3)]`, `[(390,3)]` | **no** | map 8 is changed but these planes select no changed tile; map 20 and 390 are not in the 369 |
| `SCREENBLOCK_COMPOSITE[7, 8, 14, 17, 22]` | yes | maps 7/8/14/17/22, 79/79/38/224/25 |
| `SCREENBLOCK_COMPOSITE[390]` | **no** | map 390 unchanged |
| `MAP_LAYER[(0,0)]`, `[(0,1)]`, `[(0,3)]` | yes | map 0, 231 |
| `MAP_LAYER[(0,2)]`, `[(19,0)]`, `[(39,1)]`, `[(40,0)]`, `[(40,1)]` | **no** | layers of changed maps whose ordinals select no changed tile |
| `MAP_LAYER[(39,2)]`, `[(39,3)]`, `[(40,2)]`, `[(40,3)]`, `[(125,3)]` | yes | maps 39/40/125, 32/5/3 |
| `MAP_COMPOSITE[0, 19, 39, 40, 125]` | yes | the same maps |
| `MAP_COMPOSITE_FILE_SHA256[19]` | yes | the written PNG of the same composite |
| `CHUNK_SHA256[0x08179A50]` | yes | the chunk's own entries do **not** change; it renders through map 451's block (144 tiles) |
| `CHUNK_SHA256[0x08179C38]`, `[0x08179C54]`, `[0x082B8B94]`, `[0x082B8BAC]` | **no** | same maps, no changed ordinal selected |
| `GRAPHIC_SHA256`, bank payload / tile / sheet pins, sprite frames, palettes, terrain field, terrain field file | **no** | 0 of 7,390 sprite containers change; banks 0 and 186 are not among the 77; the terrain plane is not a character block |

### 4.3 `tests/integration/test_logx_gfxscan_rom.py` and its unit sibling

| Pin | Old | New | Attribution |
| --- | --- | --- | --- |
| `EXPECTED_EXTERNAL_VS_CANONICAL_DIFFERING` | 78 | **1** | the 77 were the banks; the residual one is the `value == 0` arm's `0x0829B308`, a genuine grammar difference this record does not touch |
| bank recall `digests_agreeing` | 110 | **187** | every bank now reproduces the external JCALG1 model, which already reset the base |
| residual `external_model_agrees` | 381 | **384** | `0x086B9A9C`, `0x086BC6A0`, `0x086D8C78` (4,096 bytes each, engine-referenced) now agree. Nothing moved *out*: the external sweep never submits a declared size that is not a multiple of four |
| residual `external_confirmed` with `decoded_length % 32 == 0` | 378 | **381** | the same three |

The test's shape assertions were kept: `banks == []` and the single remaining
divergence is still asserted by address and class, so a future change cannot pass
by keeping a total.

## 5. Runtime proof

`build/gfxdiag/probe_final_proof.py` re-run against the retained capture
`build/toolkit031/mapgfxdiag001-yemma2` (map 36, ordinal 1) with the production
decoder now corrected - the probe's own "candidate" column and its "shipping"
column are the same code path, and the engine's own VRAM is the upper bound:

| Character block fed to the render | Agreement with the engine's screen | Differing pixels |
| --- | ---: | ---: |
| engine's own VRAM (ceiling) | 0.9390 | 2,343 / 38,400 |
| **SDK, production decode after this change** | **0.9390** | **2,343 / 38,400** |
| SDK, candidate helper | 0.9390 | 2,343 / 38,400 |

The acceptance ceiling of `MAP-GFX-DIAG-001` is reached by the shipping path
itself. Against the engine's **character memory**, `probe_correction_rebaseline.py`
reports bank 141 at **0 / 16,384 differing bytes** (the pre-correction rule
differed at 1,762, first at `0x140F`), and the two runtime-validated captures
(map 39, map 40) at **0 tiles differing outside the pinned post-load mutation
ranges**. Both runs are read-only replays of retained captures; no new runtime
capture was taken and no save or state was written.

## 6. Validation

Measured in this checkout, on the canonical image:

| Command | Result |
| --- | --- |
| `pytest tests/unit/test_webfoot_lz.py` | 67 passed |
| `pytest tests/unit/test_asset_export_strict_lz.py tests/unit/test_logx_codec_reference.py` | 59 passed |
| `pytest tests/integration/test_webfoot_lz_strict_rom.py tests/integration/test_logx_codec_rom.py` | 27 passed |
| `pytest tests/integration/test_map_render_rom.py` (with `WEBFOOT_MAP39_VRAM`, `WEBFOOT_MAP40_VRAM`) | 6 passed |
| `pytest tests/integration/test_logx_gfxscan_rom.py tests/unit/test_logx_gfxscan_probe.py` | 70 passed |
| `pytest tests/integration/test_asset_export_rom.py` | 81 passed |
| `pytest -m fast` (the portable gate, all of `tests/unit`) | 2,931 passed, 3 skipped, **1 failed** - a pre-existing stale build artifact, see below |
| CI `test-sdk` on the frozen candidate (`a commit consolidated into a later one`) | **passed**, pipeline `2884791492` |
| `git diff --check` | clean |

The CI job runs the whole portable suite (all of `tests/unit`) on the frozen
candidate and passed; the local single failure below does not reproduce there
because it reads a git-ignored build artifact that CI does not have.

**The one `-m fast` failure is not record-caused.**
`tests/unit/test_capability_registry.py::test_the_built_page_renders_the_registry_list`
fails with `resize renders with the wrong state class`. It reads only
`src/data/capabilities.json` and `dist/index.html`; the registry says `resize` is
`shipped` (MAP-RESIZE-AND-LAYERS-001, merged after that page was built) while the
local page still marks it todo. `dist/` is git-ignored build output (`.gitignore`
line 33) last written 2026-09-25 12:54, before the merge, and neither file is
modified by this record. Left as found rather than rebuilt, because rebuilding the
site is unrelated to this correction.

`MAP-GFX-DIAG-001`'s own observer test
(`tests/unit/test_mgba_capture.py`) and its allow-listing in
`tools/runtime/inject_mgba_lua.ps1` are part of the same uncommitted baseline the
diagnostic record left behind, not part of this correction.

## 7. What did not change, and what remains open

- **Not changed:** chunk-container identities (0 / 3,745), palette, screen
  entries and their flip bits, layer records, stacking order, sprite graphics,
  annotations, the canonical ROM, the saved states and the retained captures.
  The ROM and both input savestates hash identically before and after every run.
- **The one remaining external divergence** is the four-bit `value == 0` arm,
  which the external JCALG1 source writes as a literal `0` and the project writes
  as `literal_base & 0xFF`. This record deliberately does not change it: it is a
  separate grammar question and no runtime evidence covers it. It is now
  recorded as the only difference rather than half of one.
- **Map 102's unpainted region** remains exactly as `MAP-GFX-DIAG-001` left it:
  out of scope, cause UNKNOWN, and not attributed to this correction.
- **The 369 / 77 populations are measured by the corrected decoder**, not
  independently runtime-checked per map; the direction is fixed by bank 141 and
  by maps 39/40, which are.
