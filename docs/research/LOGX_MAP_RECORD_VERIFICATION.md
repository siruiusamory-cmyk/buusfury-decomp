# LOGX map record verification

The Buu's Fury MapEntry root table, verified against the canonical image. Static
analysis only; no runtime capture was made for this pass.

Canonical ROM SHA-256, before and after:
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`

Evidence document: [`LOGX_MAP_RECORD_PROVENANCE.md`](LOGX_MAP_RECORD_PROVENANCE.md).

## Claims tested and result

| claim | result |
| --- | --- |
| table start `0x08e2e0` | **CONFIRMED** |
| count `0x1c4` | **CONFIRMED** |
| stride `0x38` | **CONFIRMED** |
| `+0x00` field | **PARTIALLY CONFIRMED**: BE u16 lookup key, semantics unresolved |
| `+0x00` big-endian | **CONFIRMED** |
| `+0x0c` field | **PARTIALLY CONFIRMED**: low u16 text-table slot, purpose unresolved |
| text resolution path | **CONFIRMED**: low u16 -> `0x06bce8 + 4*i` -> UTF-16LE string |
| `+0x2c` field | **CONFIRMED**: 452 unique aligned in-ROM indexed-word sources |
| pointer chain | **PARTIALLY CONFIRMED**: selector 1 reads first target word; no generic second-hop schema |
| destination structure identity | **UNRESOLVED** table-wide; map 39 only is independently scene-supported |

The verified physical table is `0x08e2e0..0x0945c0`, 452 records of `0x38`.
No terminator or padding sentinel occurs at the boundary.  The bytes immediately
before/after and all representative raw records are in
[`LOGX_MAP_RECORD_PROVENANCE.md`](../research/LOGX_MAP_RECORD_PROVENANCE.md).

Representative rows span index 0, 1, 39, 100, 225, 338, and 451; they include
blank text, repeated text indices, low/middle/high keys, and divergent selected
target ranges.  Key anomalies: 70 distinct text slots across 452 records, 23
zero/empty entries, and 421 unique selected words despite 452 unique sources.

## Validation

- Added `tools/research/logx_map_record_probe.py` and
  `tests/integration/test_logx_map_record_rom.py`.
- Focused ROM-gated result: `4 passed` (including the documented
  `python -m tools.research.logx_map_record_probe` invocation).
- No full suite: this is isolated read-only research tooling with a bounded
  regression file; no shared production parser/codec behavior changed.
- **ROM Bible impact:** none.  The physical facts were already documented;
  the semantic uncertainties remain in record provenance rather than being
  promoted.
- Independent verification pass: initial verdict `BLOCK` found the direct-script import
  failure and an incorrect evidence citation; both were corrected.  Recheck
  verdict: **APPROVE WITH NON-BLOCKING NOTES**.

## Downstream consumers

LOGX-MAP-RENDER-001 may use the proven selector-dependent route
`MapEntry+0x2c + 4*(selector-1)`.  It must establish descriptor bounds and
type per selected target; it may not call every selected word a render
structure from this record.  This record stops after independent review,
final hash check, and the single isolated commit; it does not begin that work.
