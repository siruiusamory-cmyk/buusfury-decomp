# The seven `unknown-proven` rows PATH-100-002 listed: their consumers, their extents, and the R-RAW-001 promotion

PATH-100-005. All seven rows are promoted as labeled raw data under R-RAW-001; no cited site proves an extent. The tables below carry the rows, the citation channels and the per-row round trip (RED then GREEN).

| instrument | origin | what it measures here |
|---|---|---|
| `tools/research/unknown_consumer_search.py` | PATH-100-002 (T-143) | the citation channels: `shape`, `direct`, `loaders`, `indirect`, and the same `loaders` measurement over 12 matched control windows |
| `tools/research/loader_access_trace.py` | PATH-100-004 (T-146) | what a cited site does with the pointer: constant-offset field read, indexed access, pass-only, or a site whose own address lies inside the range (P-420) |
| `tools/research/thumb_annotate.py` | PATH-100-002 | the decoded instruction at a cited site, capstone Thumb, pc-relative literals resolved to file offset and value |
| `tools/research/rawlabeled.py` | PATH-100-004 (T-147) | the R-RAW emitter: the exact bytes as assembler source, split at every cited base |

## SC1 - the rows and their outcome

| # | range | bytes | cited consumer | outcome |
|---|---|---|---|---|
| 1 | `0x7122F8..0x71E258` | 48,992 | yes, `175` loader sites on `66` literals; null controls over 12 same-size windows give `[4, 26, 5, 13, 50, 27, 20, 25, 3, 15, 4, 14]` | raw-labeled |
| 2 | `0x72C388..0x7315E8` | 21,088 | yes, `25` on `11`; null `[3, 11, 2, 20, 36, 13, 13, 16, 2, 11, 3, 7]` | raw-labeled |
| 3 | `0x75029C..0x752D4C` | 10,928 | yes, `9` on `5`; null `[3, 8, 2, 4, 29, 18, 10, 86, 1, 5, 0, 2]` - the count is inside that spread, so the citation rests on the decoded sites, not the count | raw-labeled |
| 4 | `0x754978..0x756A4C` | 8,404 | yes, `13` on `5`; null `[3, 6, 3, 1, 2, 8, 5, 172, 0, 5, 1, 6]` - same caveat, same answer | raw-labeled |
| 5 | `0x752EF0..0x754910` | 6,688 | yes, `20` on `9`, above every control (`[3, 5, 4, 2, 1, 3, 4, 1, 0, 3, 1, 8]`) | raw-labeled |
| 6 | `0x6FC260..0x6FDA00` | 6,048 | yes, `33` on `16`; null `[3, 3, 4, 2, 1, 2, 2, 1, 0, 2, 0, 13]` | raw-labeled |
| 7 | `0x77B200..0x77C47C` | 4,732 | yes, `14` on `6`, above every control (`[3, 3, 5, 2, 0, 7, 1, 1, 0, 0, 0, 1]`); all six literals are loaded by 2+ sites, so none is a singleton coincidence | raw-labeled |
| | **total** | **106,880** | | **7 of 7 raw-labeled** |


### Strides the cited sites' own arithmetic proves

| row | cited base | stride | site and instructions |
|---|---|---|---|
| 1 | `0x0871DDC8` | 12 | `0x0801A908 lsls r3,r0,#1`, `0x0801A90A adds r0,r3,r0`, `0x0801A90C lsls r0,r0,#2` |
| 3 | `0x0875043C` | 36 | `0x0802A37C lsls r1,r0,#3`, `0x0802A37E adds r1,r1,r0`, `0x0802A380 lsls r1,r1,#2` |
| 7 | `0x0877B200` | 12 | `0x0803C0EC lsls r3,r0,#1`, `0x0803C0EE adds r0,r3,r0`, `0x0803C0F0 lsls r0,r0,#2` |
| 7 | `0x0877B254` | 12 | `0x0803C208`..`0x0803C20C`, same three-instruction form |
| 7 | `0x0877B2A8` | 12 | `0x0803C320`..`0x0803C324`, same three-instruction form |


## The promotion (R-RAW-001)

| row | range | bytes | fragment | symbols | cited bases | stride comments |
|---|---|---|---|---|---|---|
| 6 | `0x6FC260..0x6FDA00` | 6,048 | `asm/rawlabeled_6fc260.s` | 4 | 3 | 0 |
| 1 | `0x7122F8..0x71E258` | 48,992 | `asm/rawlabeled_7122f8.s` | 41 | 40 | 1 |
| 2 | `0x72C388..0x7315E8` | 21,088 | `asm/rawlabeled_72c388.s` | 8 | 8 | 0 |
| 3 | `0x75029C..0x752D4C` | 10,928 | `asm/rawlabeled_75029c.s` | 5 | 4 | 1 |
| 5 | `0x752EF0..0x754910` | 6,688 | `asm/rawlabeled_752ef0.s` | 8 | 7 | 0 |
| 4 | `0x754978..0x756A4C` | 8,404 | `asm/rawlabeled_754978.s` | 5 | 4 | 0 |
| 7 | `0x77B200..0x77C47C` | 4,732 | `asm/rawlabeled_77b200.s` | 6 | 6 | 3 |
| | **total** | **106,880** | | **77** | **72** | **5** |
