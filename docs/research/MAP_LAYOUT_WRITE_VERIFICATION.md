# MAP-LAYOUT-WRITE-001 - Fixed-size map-layout writing

Status: **COMPLETE** (2026-09-19). Human verdict: **ACCEPTED**. Independent
review: **APPROVE** after the public-progress wording was corrected.

## Result and boundary

**MAP LAYOUT WRITING: PROVEN FOR FIXED-SIZE IN-PLACE CHUNK-POINTER EDITS.**
The narrow writer in `tools/webfoot/map_layout_write.py` accepts a replacement
only when it is an existing, non-null chunk pointer in the same dominant layer.
It builds from verified canonical bytes. It does not create chunks, paint tiles,
resize maps, relocate data, edit other layer forms, or integrate with the
project format. Emulator runtime validation was not performed.

The accepted map model is reused: `tools/export/canonical.py:697-729` reads the
dominant record's row-major pointer window at `+0x18`, and
`tools/export/map_browser.py:149-174` stitches those pointers into the logical
layer. The writer neither changes the compressed chunk payload nor substitutes
a new binary model.

## Proof case

| Item | Measured result |
| --- | --- |
| Canonical input | Buu's Fury USA rev0, 8,388,608 bytes; SHA-256 `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E` |
| Map | `map:0040`, ROM-derived label Grand Kai's Planet |
| Layer and cell | Dominant layer slot 1, row-major chunk-pointer cell 0 |
| Original / replacement | `0x082928DC` / `0x08292A54`; replacement already occurs in cell 1 of the same layer |
| Encoded field width | Four-byte little-endian pointer |
| Actual changed bytes | Two, at file offsets `0x00292CA0` and `0x00292CA1` |
| Header/checksum | Unchanged |
| Render | Top-left 256x256 region uses the neighboring foliage chunk; 29,208 pixels differ there; the other three chunk regions are pixel-identical |
| No-op build | Byte-identical, zero changed bytes |
| Inverse edit | Byte-identical; SHA-256 returns to the canonical value above |
| Canonical source | Hash and file metadata unchanged; generated ROM and PNGs stayed ignored |

The test wrote the generated ROM to an ignored temporary output, re-read the
edited pointer, and rendered both layer images using the accepted chunk and
character-block pipeline. The viewed original and edited images showed the
top-left foliage layout change. This is deterministic renderer evidence, not
an emulator observation. The two byte changes are within the four-byte field;
**write width is four bytes**, not two.

## Validation and integration

- Focused map writer and Map Browser gate: **13 passed**.
- Public questline tests: **7 passed, 1 skipped** (no not-yet-started milestone).
- `npm run check`: 0 errors, 0 warnings; `npm run build`: passed.
- MR !53 portable CI: **1,817 passed, 18 skipped**, including ROM-gated skips
  where the private canonical ROM is unavailable to CI.
- `git diff --check`: clean; no ROM, save, state, proprietary asset, generated
  ROM, or generated PNG tracked. WORKBENCH-006 untouched.

Frozen capability commit `5c08d8414b53873cc2fb28ac1f00af852670ec8f`
merged by MR !53 as `3cdec7e317132561845f735464c9a036c05b0bc3`.
`public progress impact: UPDATED`: the reviewed `src/data/project.ts` text
reports only the fixed-size reversible chunk-pointer proof. The overall
percentage was not changed. Master pipeline `2864612153` passed `test-sdk`
and `deploy-site`; a fresh HTTP 200 fetch of the live site contained the new
"First reversible map-layout write" and "in-place layout replacement" text.

## Stop

Next substantive ticket: **DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001**. Its initial
scope is to select a dominant-layer chunk cell in the existing Map Browser /
Workbench surface, choose another valid existing chunk from that same layer,
preview it, and safely rebuild a ROM copy with no-op identity. Tile painting,
new chunks, resizing, relocation, arbitrary layer formats, and Map 19 editing
are outside that initial scope.

STOP. Do not begin DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001 in this pass.
