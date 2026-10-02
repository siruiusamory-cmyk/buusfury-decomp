# Packed-container literal-base reset: integration notes

The condensed record of the literal-base reset correction: the proven defect, the
implementation and the acceptance measurements.


The evidence record is
`WEBFOOT_LZ_LITERAL_BASE.md`; the
review brief is
the review brief recorded with that work.
The last archived closure before this record is
[`MAP-RESIZE-AND-LAYERS-001-COMPLETE.md`](MAP-RESIZE-AND-LAYERS-001-COMPLETE.md).

## Goal

Make Webfoot packed-container decoding reproduce the retail engine when a stream
returns from a 7-bit literal run to 8-bit literals.

## Proven defect

The shipping decoder retained the 7-bit run's `literal_base` after `literal_bits`
widened back to 8. The retail engine clears that base. This produced correct tile
geometry with palette indices uniformly too high. `MAP-GFX-DIAG-001` proved the
defect independently against canonical-ROM data, complete live VRAM payloads,
retained runtime captures, and framebuffer comparison.

## Implemented

1. `tools/webfoot/formats/webfoot_lz.py::_unpack_stream` clears `literal_base`
   whenever `literal_bits` becomes 8.
2. The identical rule is in `webfoot_strict.py::decode_packed` and, deliberately,
   in `tools/research/webfoot_codec_reference.py::decode_packed` - the
   differential's second implementation, which had transcribed the same defective
   rule, so a ROM-gated differential would otherwise have compared against a
   decoder wrong in the same place.
3. No other compression semantics or container layout changed.
4. The strict `xfail` marker was removed from the diagnostic regression once the
   engine-rule test passed normally; a companion mutation-control test requires
   the pre-correction grammar to produce the wrong byte.

## Rebaseline performed

* The 369 changed map character blocks: the map 39/40 `char_sha256` and
  `composite_sha256` pins and their post-load mutation lists were recomputed; the
  removed entries are exactly the 32 and 5 decode-error tiles `MAP-GFX-DIAG-001`
  measured.
* Every affected export-path pin: map layers and composites, screen-entry planes
  and their composites, one chunk pixel digest rendered through a changed block,
  and map 19's written composite PNG.
* The LOGX-GFXSCAN differential pins: external divergence 78 -> 1, bank recall
  110 -> 187, residual external agreement 381 -> 384.
* Chunk-container identities were **not** rebaselined: 0 of 3,745 change.
* Every changed pin carries its source map or bank and that source's changed-tile
  count in the evidence record; unchanged sibling pins are kept as controls.

## Acceptance, as measured

* Diagnostic engine-rule test passes without `xfail` (and its mutation control
  passes).
* Bank 141's corrected decode equals the complete captured retail-engine VRAM
  payload: 0 of 16,384 bytes differ (1,762 differed before).
* Retained map 39 and 40 comparisons: 0 tiles differ outside the pinned post-load
  mutation ranges.
* Runtime screen comparison reaches the engine's own ceiling: `0.9390`, 2,343 of
  38,400 differing pixels, identical to feeding the engine's own VRAM.
* Palette, screen entries, flips, layer records and stacking unchanged; 0 chunk,
  0 sprite, 0 selector-stream and 0 animated-frame decodes change.
* Portable, ROM-gated and export-path suites pass by name; CI green.
* Canonical ROM, saves and states unchanged by hash.

## Boundaries respected

No map-layout changes, no palette heuristics, no compositor/UI work, no map-102
investigation, and no capability-count increase.
