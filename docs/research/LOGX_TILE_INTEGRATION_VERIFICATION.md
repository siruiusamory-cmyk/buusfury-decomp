# LOGX-TILE-001: Complete

`LOGX-TILE-001` is COMPLETE / ACCEPTED.

- Original accepted research commits:
  `5dd99cb` (`research(map): reconstruct Buu chunk and tile format`),
  `f4e3076` (`docs(tickets): record LOGX tile review verdict and corrections`)
  and `8fd1998` (`docs(tickets): record LOGX tile research and correction SHAs`).
- Accepted end SHA: `8fd199880125de700fac2d7e31dc0027fce91408`.
- Integration cherry-pick commits: `fcffeb3`, `a00e0e4` and `ed87f4b`, taken in
  order from `origin/master` `22d60419d61132ecaa3128b28a2ef274d317be66`. All
  three applied with no conflict, and every cherry-picked file is byte-identical
  to the accepted branch (verified per blob).
- Canonical ROM SHA-256:
  `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.
- Evidence: [provenance](../../research/LOGX_TILE_PROVENANCE.md) and
  [review](../LOGX-TILE-001-review.md).

## Applicability boundary

The accepted chunk and tile-entry model applies to layer handler

```text
0x08008087
```

**only**. It is **not** generalized to `0x0800897B`, `0x08007A41`, `0x08007B63`
or `0x080088BD`. On the dominant form `+0x14`/`+0x15` are the chunk-grid X and Y
counts; on `0x08007A41` both are zero (the shared absent-layer placeholder), on
`0x08007B63` and `0x080088BD` they cannot be a chunk grid, and `0x0800897B`
fails the dominant reading on 29 of its 41 records. No dominant-form decoding is
applied to those records.

## Array targets and accepted census

For the accepted `0x08008087` layer form, `record + 0x18 + 4*i` points
**directly** at a Webfoot container. There is **no second pointer
dereference** before the container: the constructor loads the element at
`0x08007BF2` and hands that same value to the decompressor `0x0803D940` at
`0x08007C04`.

| Quantity | Value |
| --- | ---: |
| Layer references (dominant handler) | **1516** |
| Grid cells (sum of `+0x14 * +0x15`) | **4274** |
| Null cells | **156** |
| Aligned non-null cells | **4118** |
| Malformed cells | **0** |
| Unique targets | **3745** |
| Shared targets | **165** |
| Maximum reuse count | **10** |

Every accepted target is **kind-1**, **declares `0x800` bytes**, and **decodes to
2048 bytes**; all **3745 decoded payload digests are distinct**. These are five
different units - references, grid cells, non-null cells, unique targets and
shared targets - and the accepted counts are never collapsed into one another.

## Accepted chunk physical format

The engine-proven dominant-form representation is **1024 little-endian u16
entries**, organized as **32 columns x 32 rows**, with **64 bytes per row**. The
engine arithmetic is `(row & 31) * 64` and `(col & 31) * 2` followed by a
halfword load (`0x0800806A`..`0x08008074`), and the graphics path performs a
**64-byte VRAM row copy** (`0x08007DD0`..`0x08007DDC`) into the layer's
screenblock. So a dominant-form chunk is `32 x 32` entries, 1024 total,
2048 bytes total.

This is **not** universal across layer classes.

## Tile size and coverage

The engine-confirmed tile dimension is **8 x 8 pixels**, from `asrs #3` on both
axes (`0x0800805C`/`0x0800805E`), the 64-byte per-tile copy
(`0x08009C6A`/`0x08009C78`) and the `>> 8` chunk index (`0x08008022`). A
32x32-entry dominant-form chunk therefore covers **256 x 256 pixels**. The three
distinct quantities are preserved: physical entry grid `32 x 32`, visual tile
unit `8 x 8` pixels, visual chunk coverage `256 x 256` pixels.

## Accepted tile-entry bitfield findings

Entry width is **little-endian u16**.

| Bits | Accepted classification |
| --- | --- |
| **0-9** | **CONFIRMED tile ordinal field.** The accepted total-coverage invariant found **1,241,888** nonzero entries and **0** entries outside the union of the map's static selector ordinals and its animation destination ranges |
| **10** | used in canonical data, **46,034** occurrences |
| **11** | used in canonical data, **15,668** occurrences |
| **12-15** | **zero across all 3,834,880 entries**; accepted classification **RESERVED / CONSTANT IN CANONICAL DATA** |

"Tile ordinal" is **not** strengthened into "final VRAM tile number". Bits 10
and 11 are **not** upgraded to fully engine-confirmed H/V semantics: the
directional interpretation is **PARTIALLY CONFIRMED** only, supported by the
platform BG entry layout under the engine's own 8bpp `BGxCNT` value, because the
accepted payload consumer does not read those bits in a way that independently
proves direction. Bits 12-15 are **not** documented as "unused by the format":
canonical-zero evidence is not format-level unused-bit proof, and the engine's
own occupancy test treats any nonzero entry as occupied.

## Selector stream

`root + 0x48` points to a container whose decoded u16 values participate in the
accepted recurrence

```text
abs[0] = raw[0]
abs[i] = (raw[i] + abs[i-1] + 1) & 0xFFFF      for i >= 1
```

including the exact initial-condition treatment above; LOGExtractor's
approximate presentation is not substituted for the engine formula. Each
resulting absolute selector resolves as an accepted **`(bank, tile)` pair**
through the `root + 0x4C` relationship - `value >> 8` indexes the bank array and
`value & 0xFF` selects a 64-byte tile inside that bank's `0x4000`-byte payload.
It is **not** simplified into one flat tile ID.

## `0x179764` correction

The prior LOGExtractor interpretation is corrected. `0x179764` is a **file
offset**; the corresponding GBA address is `0x08179764`. That address is **not
itself the bank table structure**; it is the value stored at `root + 0x4C`:

```text
root + 0x4C
  -> invariant value 0x08179764 (file offset 0x179764) on all 452 selector-1 roots
  -> 187-entry bank-container table at 0x08179764
```

All 187 entries are kind-1 containers: 186 declare `0x4000` bytes and entry 186
(`0x08177AB8`) declares `0x3C40`. The largest `value >> 8` bank index used by any
canonical selector stream is 186. File offsets and GBA addresses are kept
distinct throughout.

## Streaming-cache resolution

`LOGX-TILE-001` resolves the `LOGX-LAYER-001` open question about
`cmp r6, #4` (`0x08007BE2`/`0x08007BE4`). The comparison is a **warm-up limit
associated with filling a four-entry streaming cache**; it is **not** a permanent
total-entry cap. The streaming method `0x08007C12` recomputes a 2x2 viewport
window into a four-entry id array and decompresses whichever chunk is missing
into a four-entry resident cache, so a record with `x*y > 4` loses nothing. No
unrelated cache reverse engineering was performed.

## Independent review and correction gate

Reviewer A (census and disassembly gate) returned **REJECT (fixable)**;
reviewer B (adversarial verification) returned **APPROVE WITH REQUIRED
CORRECTIONS**. **20 required corrections** were re-measured against the ROM and
applied; the correction gate is **closed**. Two reviewer assertions did not
survive re-measurement and are recorded as reviewer errors rather than adopted.

The material tooling correction is preserved: a faulty
`find_field_extractions` predicate (a strict `>` between the two shift amounts)
made `right_shift == 0` unreachable, so earlier statements about the absence of
bits-0..9 masking sites were **vacuously true rather than measured**. The
predicate was fixed, the scan total re-measured from 959 to **1532** pairs, and a
portable synthetic test now fails if the vacuous form returns. Those invalid
absence claims are **not** restored. Every canonical statement about absence of
masks, absence of bit consumers, field-extraction searches and code-site
coverage matches the corrected evidence, including the explicit list of idioms
that were **not** scanned.

## Impact

`ROM_BIBLE_IMPACT: UPDATED`. The integrated ROM Bible gains one section at
`docs/reverse-engineering.md`, "LOGX-TILE-001 chunk payloads and tile entries";
this closeout makes no technical expansion beyond the accepted evidence.

`public progress impact: NONE`: the accepted research changes no public SDK
capability, frontier or product story, so no public milestone is created and no
site edit is made.

## Next dependency

`LOGX-CONNECTOR-001` may start only from the post-merge `origin/master` SHA
recorded by this closeout. The tile/chunk side is closed; the codec handoff
below is retained for `LOGX-CODEC-001` and is not absorbed by
`LOGX-CONNECTOR-001`.

Codec handoff retained for `LOGX-CODEC-001`: decompressor entry `0x0803D940`
dispatches on the container's first word (`0` -> `memcpy`, `1`/`2` -> packed
decoder `0x08049120`, anything else -> destination untouched); it takes source
and destination only, with no bound and no returned length, so the decoded size
is the container's own `+0x04`. Canonical usage measured by this ticket: 3745
dominant chunk targets all kind-1 `0x800`; 452 selector streams (450 kind-1,
2 kind-0); 187 bank containers (186 x `0x4000`, 1 x `0x3C40`). Canonical wrapper
behaviour, the raw/uncompressed wrapper form beyond the kind-0 branch, the
first-word-zero disagreement, the `UnknownHeader` path, general encoder
requirements and all other compressed asset classes remain `LOGX-CODEC-001`'s.

Do not begin `LOGX-CONNECTOR-001` here.
