# ROM Profiles

Profiles are cryptographic identities, not fuzzy classifiers. `config/roms.yaml` is authoritative for the CLI.

## Verified configured profiles

### `buus_fury_usa_rev0_01c1707f`

- Title: Dragon Ball Z: Buu's Fury
- Region: USA
- Game code: `BG3E`
- Revision: 0
- Size: 8,388,608 bytes
- CRC32: `01c1707f`
- MD5: `3a74fce97f1ea2b28c2a50ec3df0acee`
- SHA-1: `f1c4b07554d2a3b1ad2f325307051e775ce68087`
- SHA-256: `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
- Evidence: local reproducible observation; `2genkidev/buusfury@cc53d0cd2d1c167e749419187e2d92017ac07468`, `README.md:6`
- Confidence: `CONFIRMED`
- Compatibility: exact local/disassembly base. No compatibility claim with the recomp profile.
- MapEntry table: GBA address `0x0808E2E0`, file offset `0x0008E2E0`, 452 records of `0x38` bytes. This metadata is profile-scoped and independently corroborated by target-ROM code inspection.

### `buus_fury_usa_rev0_dcf23468`

- Title: Dragon Ball Z: Buu's Fury
- Region: USA
- Game code: `BG3E`
- Revision: 0
- Size: 8,388,608 bytes
- CRC32: `dcf23468`
- MD5: `808eda67b17c901e9052f47bdc419e2f`
- SHA-1: `e65738e9d67688309f09811a54f495523ec9aada`
- SHA-256: `15df2fbbe072cc5d28a699ae9af9c56657e290cdb47c92e57d6ce14a01be4b64`
- Evidence: `mstan/DragonBallZBuusFuryRecomp@453a913a9f67916b9b358776da1c1229b09a6c80`, `baserom.md`
- Confidence: `CONFIRMED` as the upstream requirement
- Compatibility: distinct from the local profile. Binary differences are unresolved.
- MapEntry table: intentionally unconfigured. No table metadata transfers from the local profile.

### `legacy_of_goku_usa_a3c8c767`

- Title: Dragon Ball Z: The Legacy of Goku
- Region: USA
- Game code: `ALGE`
- Revision: `UNKNOWN` and intentionally unconstrained
- Size: 8,388,608 bytes
- CRC32: `d47ccff4`
- SHA-1: `a3c8c76742f11fc6a3f6e3fcca20992458cac0b5`
- SHA-256: `3ba9919e26704b0f5fdc2bfabc7f7a0404c71413761d38abcd94224c3bd4b1b9`
- Evidence: `mstan/DragonBallZLegacyOfGokuRecomp@fbe502a3d44256402262cd3f5baeb072a7235932`, `baserom.md`
- Confidence: `CONFIRMED` as the upstream requirement; revision remains `UNKNOWN`

### `legacy_of_goku_ii_usa_rev0_204142e1`

- Title: Dragon Ball Z: The Legacy of Goku II
- Region: USA
- Game code: `ALFE`
- Revision: 0
- Size: 8,388,608 bytes
- CRC32: `204142e1`
- MD5: `4e1565aa1f0627c2bf5e51019440cb70`
- SHA-1: `18e0715dec419f3501c301511530d2edcd590f8b`
- SHA-256: `6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75`
- Evidence: `mstan/DragonBallZLegacyofGokuIIRecomp@add98b5d76fb2b822be870f29fa27b22c9a95631`, `baserom.md`
- Confidence: `CONFIRMED` as the upstream requirement

## Header-only upstream support

DragonByteZ additionally recognizes `ALGP` LoG Europe revision 0, `ALFP` LoG II Europe revision 0, `ALFE` LoG II USA revision 0, and `BG3E` Buu's Fury USA revision 0. Its pinned implementation checks game code, 8 MiB size, and revision but supplies no cryptographic whitelist. These are not configured as verified profiles without hashes.

## Matching rules

1. Configured SHA-256 must match exactly.
2. Every other configured hash and metadata constraint must also match.
3. Exactly one profile must survive.
4. Header/size matches without a cryptographic match are `UNKNOWN`.
5. A cryptographic match plus contradictory metadata is `CONFLICT`.
6. Multiple exact matches are an error.

Distinct hashes normally remain distinct profiles even if title, game code, revision, and size agree.
