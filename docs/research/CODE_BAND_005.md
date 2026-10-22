# CODE-BAND-005: the entry census of the `CODE-BAND-004:unreached` set, and its code/table split

Population: 1,174 rows / 35,510 B; the 702-row / 28,797 B `text/tables` intersection is a column, not the denominator. Result: nothing converted, because the entry set does not beat its byte-permuted null.

    python tools\research\code_band_entries.py --nulls --write
    python tools\research\thumb_body_convert.py --rows docs\research\CODE_BAND_ENTRY_ROWS.csv

## C1. Entry census, every channel measured alone

| channel | rows | bytes | what it is |
|---|---|---|---|
| `source` | 4 | 482 | a Thumb control transfer out of a source span landing in the row (`thumb_bodies.entries`) |
| `converted` | 0 | 0 | a branch out of a body this project already converted |
| `method` | 0 | 0 | a class-table method slot naming the row (`thumb_bodies.method_entries`) |
| `pool` | 0 | 0 | a code pc-relative pool word whose VALUE is an address in the row |
| `pointer` | 6 | 20,854 | a `pointer-tables` class word whose value (Thumb bit aside) names the row |
| `prologue` | 0 | 0 | the `0xB5xx` PUSH shape: a SHAPE, never an entry |
| **`entry=none`** | **1,164** | **14,174** | no channel fired |

## C2. Conversion: the entry set does not beat its byte-permuted null, so nothing was converted

| null | real | permuted |
|---|---|---|
| the walk from each entry ends in a return, vs the same walk on that row's bytes shuffled (`seed 20261017 + start`) | 0 of 4 | 0 of 4 |
| `code_band.walk_control`: the same walks against 12 random even addresses in the same rows | 0 returns of 12 | 0 of 12 |
| the whole SOURCE scan re-run with every Thumb source span permuted (the site side, where the rule actually reads) | 4 rows / 482 B | **124 rows / 28,428 B** |

## C3. Code-shaped versus table-shaped, one stated predicate and its null

| shape | rows | bytes | of the 702-row text/tables column: rows / B |
|---|---|---|---|
| `entry` | 10 | 21,336 | 7 / 20,980 |
| `code` | 50 | 678 | 24 / 202 |
| `table-pointer` | 70 | 926 | 3 / 80 |
| `table` | 1,044 | 12,570 | 668 / 7,535 |
| total | 1,174 | 35,510 | 702 / 28,797 |
| statistic | real | permuted |
|---|---|---|
| bytes covered by a clean forward Thumb sweep | 806 rows | 848 rows |
| rows whose walk from the row start covers any byte | 897 | 986 |
| walked bytes | 6,572 | 5,050 |
| walks ending in a return | 98 | 49 |
| rows with a `B`/`BL` landing inside themselves | 34 | 23 |
| rows with a `B`/`BL` leaving | 137 | 151 |
| rows whose first word is a value inside the image | 72 | 22 |

## C4. Table-shaped families: the pointer channel is real, but no reader gives the named rows a parse

| row | bytes | naming word | the word's target |
|---|---|---|---|
| `0x036E76..0x036E7A` | 4 | `0x75F7FC = 0x08036E77` (Thumb bit SET) | row start: `ldr r0,[pc,#0x28]` / `bx lr` - a leaf function |
| `0x04A24A..0x04A59C` | 850 | `0x01CB7C = 0x0804A368` | +0x11E, decodes as data |
| `0x04AAF2..0x04BA78` | 3,974 | `0x00627C = 0x0804B2DC` | +0x7EA, decodes as data |
| `0x06D4E0..0x06FE18` | 10,552 | `0x6B807C = 0x0806E050` | +0xB70, decodes as data |
| `0x07012C..0x070130` | 4 | `0x6B8024 = 0x0807012C` | row start, not an ARMv4T Thumb instruction |
| `0x0701FA..0x071758` | 5,470 | `0x009018 = 0x080716A0` | +0x14A6, decodes as data |

## Gate, perturbation, census

| doc | sha256 |
|---|---|
| `docs/research/THUMB_BODIES.csv` | `7d5d5b8514a05d07be082b29131a95aa078941f4d533b4c8925ed56013fa8fcc` |
| `docs/research/RAW_CITATIONS.csv` | `3aca7e6c45792216ac40a82a058cd3b749b381d4c3837f42b6c530c504549d23` |
| `docs/research/INCBIN_CENSUS.md` | `abb4ff13d513515944ffa847b344c66ed0e2614a8288e84f2f021bf4d75c3f34` |
| `docs/research/RESIDUAL_LEDGER.csv` | `712d19163bccb3956f719d5fd520b911c99b2e336c1a7771d2b1701ef59d48d1` |
| `docs/research/RESIDUAL_LEDGER.md` | `01769f5824e2463816dc8747957a08ee3230459a8285bf6122071c2f2e41e618` |
| `docs/research/RAW_REMAINDER.csv` | `437a408ecebc3dc90af4b6893ad77275de93eeb219b3e9bc36a8d402f4eb2959` |
| `docs/research/ROUTE_TO_100.md` | `968c85a6dab9b1d9ceeedaac6b7891aae85431c7ec06b13a36f821a2ef6e71abd` |
