# Buu's Fury Hash Investigation

## Claims inspected

| Source | Size | Game code | Revision | CRC32 | MD5 | SHA-1 |
|---|---:|---|---:|---|---|---|
| Local user ROM | 8,388,608 | `BG3E` | 0 | `01c1707f` | `3a74fce97f1ea2b28c2a50ec3df0acee` | `f1c4b07554d2a3b1ad2f325307051e775ce68087` |
| `2genkidev/buusfury@cc53d0c` | 8,388,608 expected by build layout | `BG3E` in reconstructed header | 0 | not published | not published | `f1c4b07554d2a3b1ad2f325307051e775ce68087` |
| `mstan/DragonBallZBuusFuryRecomp@453a913` | 8,388,608 | `BG3E` | 0 | `dcf23468` | `808eda67b17c901e9052f47bdc419e2f` | `e65738e9d67688309f09811a54f495523ec9aada` |
| DragonByteZ `b269120` classifier | requires 8,388,608 | `BG3E` | 0 | none | none | none |

The local SHA-256 is `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`. The recomp profile publishes SHA-256 `15df2fbbe072cc5d28a699ae9af9c56657e290cdb47c92e57d6ce14a01be4b64`.

## Reproducible local observation

Before any read, Git ignore checks confirmed `roms/`, `*.gba`, and the exact local path were ignored; `git ls-files` returned no tracked ROM. A streaming read-only analysis produced the metadata above.

Header result:

- Title: `DBZBUUSFURY` with NUL padding
- Game code: `BG3E`
- Maker code: `70`
- Fixed byte: `0x96`, valid
- Revision: 0
- Stored checksum: `0x84`
- Calculated checksum: `0x84`, valid
- Reserved bytes: valid

Before and after size remained 8,388,608, modification time remained `2026-08-20T01:10:12.330Z`, and two SHA-1 calculations returned the same value. No content change was detected.

## Confirmed conclusions

- The local file exactly matches the SHA-1 required by the pinned disassembly.
- The local file does not match any hash published by the pinned recomp.
- Both upstream targets share an 8 MiB `BG3E`, revision-0 header class. That does not make them byte-equivalent.
- DragonByteZ would classify that header class but does not cryptographically distinguish these two images.
- Community metadata independently associates `01C1707F` with the USA `BG3E` image. RetroAchievements pairs the local CRC32/MD5 and labels the `DCF23468`/`808e...` image `[f1]`. These are community classifications, not cartridge provenance proof.

Community sources inspected:

- <https://retroachievements.org/viewtopic.php?t=549>
- <https://datacrystal.tcrf.net/wiki/Dragon_Ball_Z%3A_Buu%27s_Fury>
- <https://gamehacking.org/game/4390>

## Hypotheses

### Separate retail revisions

Evidence against a simple header revision distinction: both projects specify revision 0 and `BG3E`. Retail manufacturing history was not established. Status: `UNKNOWN`.

### Trimming or overdump

Evidence against: both images are documented as exactly 8 MiB. Equal length does not rule out content differences. Status: not supported, not disproven byte-by-byte.

### Header-only difference

No second binary was locally available, so no byte comparison was performed. The recomp and disassembly header metadata agree in the documented fields, but undocumented header bytes were not compared. Status: `UNKNOWN`.

### Patched, fixed, or modified image

Community metadata labels the recomp profile `[f1]`, supporting an inference that it is an alternate modified/fixed image. The exact modification, origin, and correctness were not established. Status: `INFERRED`, not `CONFIRMED`.

### Bad dump or incorrect upstream documentation

Exact cross-source hash pairings show that both byte images are recognized in public metadata. That does not establish which provenance label is historically correct. Status: `UNKNOWN`.

## Conclusion

The discrepancy is real and remains unresolved at the byte/provenance level. The project therefore encodes two Buu's Fury profiles. The local ROM is `buus_fury_usa_rev0_01c1707f`; recomp offsets or generated outputs must not be transferred to it without explicit validation.

No second commercial image was obtained, transmitted, or compared.
