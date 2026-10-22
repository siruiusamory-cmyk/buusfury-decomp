# The packer oracle: corpus census and a fitted re-encoder

PACKER-001 T11/T12. Oracle: tracked `tools/compress/compress.exe` (sha256 `4ADE5D523843D91692418477EF13DBD6ACCE8FEB46A8BAFCFE001883E1121AEA`), run as `<payload file> <out file>`, writing an 8-byte `{kind=1, declared=len(payload)}` header and the packed stream; decoder `tools/webfoot/webfoot_lz.py`. The fitted encoder is not byte-exact and is unused by the build; fixtures and reports live under the ignored `build/packer-*`.


## 2. T11 census

| Corpus | Walked | Re-encoded | Byte-equal | Failures |
| --- | --- | --- | --- | --- |
| Tile banks | 187 | 187 | 187 | 0 |
| Sprite graphics (kind 1) | 7,390 | 7,390 | 7,390 | 0 |
| ATTRIB-001 fixtures, packed | 12 | 12 | 12 | 0 |
| ATTRIB-001 fixtures, stored | 3 | 3 (`build_stored`) | 3 | 0 |
| Offset | Kind | Declared | Marker extent | Oracle | Payload sha256[:16] | Container sha256[:16] |
| --- | --- | --- | --- | --- | --- | --- |
| 0x3C34D0 | 1 | 1024 | 232 | 232 | d4acde2b35d4d9c2 | 9ffad6000b93a461 |
| 0x3C35B8 | 1 | 1024 | 232 | 232 | 9fc054ad73ae9086 | 1ea675608aba9913 |
| 0x3C36A0 | 1 | 1024 | 180 | 180 | 09dd24a2940ed548 | 94c379f45c553848 |
| 0x3C3754 | 1 | 1024 | 180 | 180 | c5ef11eec8f00287 | bdae86df36d2d549 |
| 0x3C3808 | 1 | 1024 | 272 | 272 | 1ed5c45fb02768ab | aab8ec1413136b5f |
| 0x3C3918 | 1 | 1024 | 268 | 268 | 183c995b1c20ed29 | 34ca869cf54b1a9f |
| 0x54A5C8 | 1 | 512 | 248 | 248 | f7a8d951e2877100 | 06186278ecc72bb6 |
| 0x54A6C0 | 1 | 1024 | 292 | 292 | 07a1d314138d0155 | cdb675d76140594b |
| 0x54A7E4 | 1 | 1024 | 300 | 300 | 2e7c1fe4f2d29a9e | 5901458a6c2f5a70 |
| 0x54A910 | 1 | 1024 | 280 | 280 | 4ff8e18928c051f7 | dba06909ce4ab4c1 |
| 0x54AB4C | 1 | 1024 | 288 | 288 | bced0f3d40e30678 | 1755e1d59172701f |
| 0x54AC6C | 1 | 1024 | 292 | 292 | fa45171e6480965e | becce7d5fe8c7f75 |
| 0x0154CC | 0 | 4108 | 4116 | 4116 | 63168c1c591c7048 | d46d1ec86a62c884 |
| 0x047F60 | 0 | 1 | 9 | 9 | 6e340b9cffb37a98 | cdb032de4c6cb506 |
| 0x0555B8 | 0 | 44 | 52 | 52 | fb6b55724a8edb01 | 15930f6a55590b7c |
