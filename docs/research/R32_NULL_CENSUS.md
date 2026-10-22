# `R32`'s raw rows: a per-row null

`R32` is the region `first-MiB code band`, 1173 rows / 38182 B as `docs/research/RAW_REMAINDER.csv` carried them and
the same figure as `python tools\research\raw_remainder.py` reports against the gate's
raw-data (`total 1173 row(s) 38182 B  gate raw-data 585508 B  EXACT`). Data addresses are file
offsets, instruction addresses are bus addresses `0x08...`, and every quote is a Thumb decode
of the bytes at that address. The census is measured before the conversion this ticket lands:
the family below becomes source and every other row keeps a measured null.

## Totals

| class | rows | bytes | rule |
|---|---|---|---|
| `pool` | 27 | 264 | a row on the word grid whose every word is a decoded `ldr [pc,#imm]` literal address |
| `code-null` | 11 | 512 | a decoded branch enters and an instruction decodes, but the branch channel is below its null |
| `pool-fragment` | 303 | 1224 | a loaded word crosses the row boundary |
| `pool-partial` | 23 | 3007 | some words of the grid load, the rest have no reader |
| `named-data` | 39 | 13093 | code loads a word naming the row; its bytes have no layout |
| `after-dispatch` | 5 | 408 | the row follows a computed jump, unread |
| `between` | 356 | 4696 | between transcribed code rows, unread |
| `unreached` | 409 | 14978 | no decoded reader and no naming word |
| **total** | **1173** | **38182** | |

The rows are exactly `docs/research/R32_ROWS.csv`, written once from that run; the family below
leaves the remainder and the rest keep their class here.

## What was searched, and its denominator

| channel | instrument | denominator | result on these rows |
|---|---|---|---|
| decoded `ldr [pc,#imm]` literal address in the row | `row_readers.walked_literals` | 4346 walked bod(ies): 2715 ledger Thumb row(s) and 1631 converted | 370 row(s) with >= 1 word |
| decoded branch at an instruction boundary inside a walked body | `row_readers.walked_branches` | 69600 decoded instruction(s) | 11 row(s) |
| decoded `ldr` whose literal VALUE names the row | `consumer_search.literal_loads` | 2783 code row(s) / 292722 B, 776 load(s) | 42 row(s) |
| word-aligned word holding an address in the row | `row_readers.naming_words` | 2097152 words | 144 row(s), 3623 word(s) |

Every count is half-open over each row's own span (`[start, end)`), never over the interval
that contains the rows (P-738). A naming word is a name, not a consumer (P-733), and a
literal-shaped halfword inside a data stream is not a reader (P-721).

## Byte statistics

Entropy 0.00..6.27 bits/byte, zero-byte share 0.00..1.00, 698 row(s) are a single halfword,
788 row(s) are not a whole number of words and 79 hold at least one word that is an address
in the image: most rows are a fragment of a pool or a gap between two bodies, not a body.

## The `pool` family: a word grid every reader names

27 rows / 264 B start on the word grid, are a whole number of words, and every one of their
words is the literal address of a decoded `ldr [pc,#imm]` in a walked body, for example

    0x00627C..0x006288  080060DA ldr r0, [pc, #0x1a0]
    0x006FE4..0x006FF0  08006E46 ldr r0, [pc, #0x19c]
    0x00B51C..0x00B528  0800B32C ldr r1, [pc, #0x1ec]
    0x00CDD0..0x00CDD4  0800CB38 ldr r0, [pc, #0x294]

so the layout is the reader's: one `DCD` per word, in order, at the row's own address (P-732).
The null is the site side permuted:

| channel | the site side byte-permuted | the real image |
|---|---|---|
| `literal`: any word of the row | 53 row(s) | 370 row(s) |
| `literal`: every word of the row | 3 row(s) / 24 B | 27 row(s) / 264 B |
| `branch` at an instruction boundary inside a walked body | 27 row(s) of 19100 decoded instruction(s) | 11 row(s) of 69600 |

4466 decoded literal site(s) over an 8388608 B image: a random target lands in the population 20.33
time(s) in total, so a row whose every word carries one is not a coincidence of the sweep.
The permutation shuffles every ledger Thumb row's own bytes (seed 20261017), the side the
literal, branch and walk rules read; the population's own bytes are untouched. The wider
branch sweep `thumb_bodies.entries` fires on 98 row(s) of the permuted source, so its count is
not evidence and no row is decoded on it.

A word of the image is the target of a decoded load by chance with probability 0.0021 (4466 sites x
4 B / 8388608 B), so the every-word rule is not what a sweep produces on its own.

Falsifier: a row in this family with a word no decoded load reads, or a cold rebuild whose
bytes differ.

## The `code-null`: a branch enters and an instruction decodes

3 rows / 496 B are entered by a decoded source branch and decode as Thumb from that entry.
They stay raw because the branch channel is BELOW its own null: the same rule over the
byte-permuted source fires on more rows, so a branch target is not evidence in this band and
no row is promoted on it (P-613). A row here is a branch target whose body the project's
converter would accept, and nothing measures that it is reached.

    0x0153F2..0x015470 entered by 080152F8 b #0x80153f6
    0x0426D0..0x042750 entered by 08042604 b #0x80426d0
    0x042784..0x042876 entered by 08042638 b #0x8042784

The 8 other branch-entry rows are one halfword each: no ARMv4T instruction fits.

## The per-row null

Each line: file offsets, bytes, entropy, zero-byte share, word-aligned words inside the row,
words of it that are an address in the image, class, the decoded reader with its instruction,
and why the row stays raw. `none` means no decoded instruction in the channels above names a
byte of the row at the denominators quoted. The region's 9 `code-without-entry` rows are not in
this table: each is one half of an instruction whose other half lies in a neighbouring raw row,
and `docs/research/CODE_FRAGMENT_NULL_CENSUS.md` carries that null per row.

| start | end | bytes | ent | zero | words | in | class | readers | null |
|---|---|---|---|---|---|---|---|---|---|
| `0x1D0` | `0x1D2` | 2 | 0.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3C0` | `0x3C2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800015E ldr r1, [pc, #0x260] (x1) | a loaded word crosses the row boundary |
| `0x3FC` | `0x45E` | 98 | 5.66 | 0.06 | 24 | 0 | between | 10 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x660` | `0x662` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080003E4 ldr r1, [pc, #0x278] (x1) | a loaded word crosses the row boundary |
| `0xB1C` | `0xB40` | 36 | 4.38 | 0.06 | 9 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x10F0` | `0x10F2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x10FC` | `0x10FE` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x17D8` | `0x1808` | 48 | 3.85 | 0.10 | 12 | 0 | between | 2 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x1B6C` | `0x1B82` | 22 | 3.62 | 0.14 | 5 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x1EBC` | `0x1EBE` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x25E0` | `0x25E2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x26B4` | `0x26B6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x2720` | `0x273A` | 26 | 3.98 | 0.15 | 6 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x2990` | `0x2992` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x29C0` | `0x29C2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080026CC ldr r7, [pc, #0x2f0] (x1) | a loaded word crosses the row boundary |
| `0x29D8` | `0x2A12` | 58 | 5.12 | 0.07 | 14 | 0 | between | 2 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x2C2A` | `0x2C58` | 46 | 4.81 | 0.09 | 11 | 0 | between | 2 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3310` | `0x3348` | 56 | 4.40 | 0.16 | 14 | 0 | between | 2 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3352` | `0x3354` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3354` | `0x3358` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3718` | `0x371A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3986` | `0x399E` | 24 | 3.68 | 0.17 | 6 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x39D4` | `0x39D6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080039C8 ldr r0, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x3A74` | `0x3B12` | 158 | 5.37 | 0.04 | 39 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3C44` | `0x3C46` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080039F4 ldr r2, [pc, #0x24c] (x1) | a loaded word crosses the row boundary |
| `0x3C6C` | `0x3C6E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3C8A` | `0x3CAC` | 34 | 4.79 | 0.06 | 8 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3CF6` | `0x3D10` | 26 | 3.69 | 0.15 | 6 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3D38` | `0x3D3A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3F40` | `0x3F42` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3FEE` | `0x3FF8` | 10 | 3.12 | 0.00 | 2 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x4092` | `0x4094` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4094` | `0x4098` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4156` | `0x4212` | 188 | 5.84 | 0.07 | 47 | 0 | between | 080040F8 ldr r0, [pc, #0x9c] (x4) | between transcribed code rows and no instruction reads it |
| `0x45C2` | `0x45C4` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x45C4` | `0x45C8` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4810` | `0x4812` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080045B8 ldr r0, [pc, #0x254] (x5) | a loaded word crosses the row boundary |
| `0x4AE4` | `0x4AE6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800483E ldr r5, [pc, #0x2a4] (x3) | a loaded word crosses the row boundary |
| `0x4DEC` | `0x4DEE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08004BC2 ldr r6, [pc, #0x228] (x5) | a loaded word crosses the row boundary |
| `0x524E` | `0x5250` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x5AD4` | `0x5BC0` | 236 | 5.96 | 0.04 | 59 | 0 | after-dispatch | none | the row follows a computed jump and no instruction reads it |
| `0x5BFC` | `0x5BFE` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x5C40` | `0x5C44` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x5C6E` | `0x5E36` | 456 | 6.14 | 0.08 | 114 | 0 | unreached | 080059D2 ldr r0, [pc, #0x3d0] (x20) | no decoded reader and no naming word at half-open bounds |
| `0x5FA0` | `0x5FA2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x6092` | `0x6094` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x6094` | `0x6098` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x627C` | `0x6288` | 12 | 3.19 | 0.00 | 3 | 3 | pool | 080060DA ldr r0, [pc, #0x1a0] (x7) | decoded, section above |
| `0x628C` | `0x628E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08006218 ldr r1, [pc, #0x70] (x1) | a loaded word crosses the row boundary |
| `0x649E` | `0x64A0` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x686C` | `0x686E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800661C ldr r0, [pc, #0x24c] (x1) | a loaded word crosses the row boundary |
| `0x6AA8` | `0x6AAA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x6B94` | `0x6B96` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08006ABC ldr r0, [pc, #0xd4] (x1) | a loaded word crosses the row boundary |
| `0x6BCC` | `0x6BCE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08006BA2 ldr r4, [pc, #0x28] (x1) | a loaded word crosses the row boundary |
| `0x6E18` | `0x6E1A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08006DC6 ldr r0, [pc, #0x50] (x2) | a loaded word crosses the row boundary |
| `0x6E38` | `0x6E3A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08006E28 ldr r0, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x6FE4` | `0x6FF0` | 12 | 3.19 | 0.25 | 3 | 1 | pool | 08006E46 ldr r0, [pc, #0x19c] (x3) | decoded, section above |
| `0x6FF4` | `0x6FFA` | 6 | 2.25 | 0.33 | 1 | 0 | pool-fragment | 08006EA6 ldr r0, [pc, #0x14c] (x2) | a loaded word crosses the row boundary |
| `0x7052` | `0x7054` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x7054` | `0x7056` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x7164` | `0x7166` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x71A6` | `0x71AA` | 4 | 2.00 | 0.00 | 1 | 0 | between | 21 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x71BC` | `0x71BE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08007168 ldr r1, [pc, #0x50] (x2) | a loaded word crosses the row boundary |
| `0x73B6` | `0x73B8` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x73BC` | `0x73BE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800734C ldr r0, [pc, #0x6c] (x1) | a loaded word crosses the row boundary |
| `0x74BA` | `0x74BC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x74C0` | `0x74C2` | 2 | 1.00 | 0.50 | 0 | 0 | pool-fragment | 08007490 ldr r0, [pc, #0x2c] (x1) | a loaded word crosses the row boundary |
| `0x770C` | `0x7710` | 4 | 2.00 | 0.25 | 1 | 0 | between | 131 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x774E` | `0x7752` | 4 | 2.00 | 0.00 | 1 | 0 | between | 97 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x7764` | `0x7766` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08007752 ldr r0, [pc, #0x10] (x1) | a loaded word crosses the row boundary |
| `0x7770` | `0x7774` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x77DE` | `0x77E2` | 4 | 2.00 | 0.00 | 1 | 0 | between | 154 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x7854` | `0x7856` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080077F8 ldr r0, [pc, #0x58] (x1) | a loaded word crosses the row boundary |
| `0x7A18` | `0x7A1A` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x7A1A` | `0x7A1E` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x7A56` | `0x7A5A` | 4 | 0.81 | 0.75 | 1 | 0 | pool-fragment | 08007A2C ldr r1, [pc, #0x28] (x1) | a loaded word crosses the row boundary |
| `0x7B62` | `0x7B76` | 20 | 3.25 | 0.30 | 5 | 0 | pool-fragment | 08007A6C ldr r0, [pc, #0xfc] (x4) | a loaded word crosses the row boundary |
| `0x7D5C` | `0x7D5E` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x7D5E` | `0x7D62` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x8094` | `0x8096` | 2 | 1.00 | 0.50 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x8486` | `0x84A6` | 32 | 3.65 | 0.28 | 8 | 0 | pool-fragment | 080080A8 ldr r1, [pc, #0x3dc] (x17) | a loaded word crosses the row boundary |
| `0x86B2` | `0x86B4` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x86B4` | `0x86B8` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x8A58` | `0x8AA0` | 72 | 3.98 | 0.33 | 18 | 1 | pool-partial | 08008A0A ldr r1, [pc, #0x4c] (x1) | 1 of 18 word(s) load; the rest have no reader |
| `0x9018` | `0x9022` | 10 | 3.12 | 0.00 | 2 | 2 | pool-partial | 08008F24 ldr r0, [pc, #0xf0] (x4) | between transcribed code rows and no instruction reads it |
| `0x91FC` | `0x91FE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08009072 ldr r7, [pc, #0x188] (x2) | a loaded word crosses the row boundary |
| `0x9648` | `0x964A` | 2 | 1.00 | 0.50 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x98F8` | `0x98FA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800965E ldr r4, [pc, #0x298] (x1) | a loaded word crosses the row boundary |
| `0x9AD8` | `0x9ADA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x9B4C` | `0x9B80` | 52 | 4.77 | 0.06 | 13 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0xA208` | `0xA20A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800A152 ldr r0, [pc, #0xb4] (x1) | a loaded word crosses the row boundary |
| `0xA20C` | `0xA20E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0xA210` | `0xA212` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0xA214` | `0xA216` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0xA26E` | `0xA272` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | 1 naming word(s) | named by a word; a name is not a consumer |
| `0xA418` | `0xA41A` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0xA41A` | `0xA41E` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0xA4E0` | `0xA4E2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800A27C ldr r0, [pc, #0x260] (x1) | a loaded word crosses the row boundary |
| `0xA520` | `0xA522` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0xA522` | `0xA526` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0xA78C` | `0xA78E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800A516 ldr r1, [pc, #0x274] (x5) | a loaded word crosses the row boundary |
| `0xA79C` | `0xA79E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800A784 ldr r0, [pc, #0x14] (x2) | a loaded word crosses the row boundary |
| `0xA938` | `0xA93A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0xA9B0` | `0xA9B8` | 8 | 2.50 | 0.12 | 2 | 0 | between | 2 naming word(s) | between transcribed code rows and no instruction reads it |
| `0xAB50` | `0xAB52` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0xAD7A` | `0xAD82` | 8 | 2.41 | 0.38 | 2 | 0 | pool-fragment | 0800AB66 ldr r1, [pc, #0x214] (x11) | a loaded word crosses the row boundary |
| `0xB096` | `0xB0A8` | 18 | 3.20 | 0.33 | 4 | 0 | between | 0800ADAA ldr r2, [pc, #0x2ec] (x11) | between transcribed code rows and no instruction reads it |
| `0xB328` | `0xB32A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800B2B6 ldr r0, [pc, #0x70] (x2) | a loaded word crosses the row boundary |
| `0xB51C` | `0xB528` | 12 | 3.25 | 0.17 | 3 | 2 | pool | 0800B32C ldr r1, [pc, #0x1ec] (x3) | decoded, section above |
| `0xBC46` | `0xBC5A` | 20 | 3.48 | 0.20 | 5 | 0 | between | 0800B92A ldr r5, [pc, #0x320] (x2) | between transcribed code rows and no instruction reads it |
| `0xBE70` | `0xBE72` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800BC96 ldr r1, [pc, #0x1d8] (x1) | a loaded word crosses the row boundary |
| `0xC274` | `0xC276` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0xC42C` | `0xC42E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0xC588` | `0xC58A` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0xC58A` | `0xC58E` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0xCB00` | `0xCB02` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0xCB02` | `0xCB06` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0xCDD0` | `0xCDD4` | 4 | 2.00 | 0.00 | 1 | 1 | pool | 0800CB38 ldr r0, [pc, #0x294] (x1) | decoded, section above |
| `0xCDD8` | `0xCDE2` | 10 | 2.05 | 0.30 | 2 | 0 | pool-fragment | 0800CC7C ldr r6, [pc, #0x158] (x5) | a loaded word crosses the row boundary |
| `0xCEE4` | `0xCEF2` | 14 | 3.38 | 0.14 | 3 | 2 | pool-fragment | 0800CE3C ldr r0, [pc, #0xac] (x8) | a loaded word crosses the row boundary |
| `0xD1A8` | `0xD1B2` | 10 | 2.05 | 0.30 | 2 | 0 | pool-fragment | 0800CF9A ldr r5, [pc, #0x20c] (x5) | a loaded word crosses the row boundary |
| `0xD1B4` | `0xD1B6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800D0F4 ldr r0, [pc, #0xbc] (x2) | a loaded word crosses the row boundary |
| `0xD518` | `0xD538` | 32 | 4.05 | 0.12 | 8 | 6 | pool-partial | 0800D304 ldr r1, [pc, #0x220] (x18) | 7 of 8 word(s) load; the rest have no reader |
| `0xD646` | `0xD648` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0xD650` | `0xD652` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0xD876` | `0xD892` | 28 | 3.80 | 0.21 | 7 | 0 | pool-fragment | 0800D5AA ldr r0, [pc, #0x2cc] (x9) | a loaded word crosses the row boundary |
| `0xDE14` | `0xDE16` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0xDE16` | `0xDE1A` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0xE74C` | `0xE74E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800E6E2 ldr r0, [pc, #0x68] (x3) | a loaded word crosses the row boundary |
| `0xEB34` | `0xEB36` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800E784 ldr r0, [pc, #0x3ac] (x5) | a loaded word crosses the row boundary |
| `0xF1E8` | `0xF1F8` | 16 | 3.50 | 0.12 | 4 | 2 | unreached | 1 naming word(s) | named by a word; a name is not a consumer |
| `0xF4B0` | `0xF4B2` | 2 | 0.00 | 0.00 | 0 | 0 | pool-fragment | 0800F216 ldr r3, [pc, #0x298] (x3) | a loaded word crosses the row boundary |
| `0xF4B2` | `0xF4B6` | 4 | 0.81 | 0.75 | 1 | 0 | pool-fragment | 0800F3FE ldr r2, [pc, #0xb4] (x1) | a loaded word crosses the row boundary |
| `0xF584` | `0xF586` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800F4F8 ldr r1, [pc, #0x88] (x1) | a loaded word crosses the row boundary |
| `0xF624` | `0xF62C` | 8 | 3.00 | 0.12 | 2 | 1 | pool-partial | 0800F5BC ldr r1, [pc, #0x64] (x1) | 1 of 2 word(s) load; the rest have no reader |
| `0xFCE0` | `0xFCF0` | 16 | 3.58 | 0.12 | 4 | 3 | pool | 0800F9B4 ldr r1, [pc, #0x328] (x10) | decoded, section above |
| `0x10008` | `0x1000A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0800FDA0 ldr r0, [pc, #0x264] (x2) | a loaded word crosses the row boundary |
| `0x10448` | `0x1044A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x10576` | `0x10582` | 12 | 3.25 | 0.17 | 3 | 0 | pool-fragment | 08010466 ldr r6, [pc, #0x114] (x4) | a loaded word crosses the row boundary |
| `0x107E4` | `0x107E6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08010588 ldr r0, [pc, #0x258] (x1) | a loaded word crosses the row boundary |
| `0x10DD8` | `0x10DDA` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x10DDA` | `0x10DDE` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x10F26` | `0x10F40` | 26 | 3.74 | 0.23 | 6 | 0 | unreached | 08010B84 ldr r0, [pc, #0x3a0] (x11) | named by a word; a name is not a consumer |
| `0x10FFC` | `0x11014` | 24 | 4.05 | 0.08 | 6 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x110D0` | `0x110D2` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x110D2` | `0x110D6` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x111FC` | `0x11200` | 4 | 2.00 | 0.00 | 1 | 1 | pool | 08011150 ldr r1, [pc, #0xa8] (x3) | decoded, section above |
| `0x11552` | `0x1155A` | 8 | 1.75 | 0.50 | 2 | 0 | between | 08011204 ldr r3, [pc, #0x34c] (x1) | between transcribed code rows and no instruction reads it |
| `0x11DA4` | `0x11DA6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x1218C` | `0x1218E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08012038 ldr r0, [pc, #0x150] (x23) | a loaded word crosses the row boundary |
| `0x123C4` | `0x123DE` | 26 | 3.78 | 0.15 | 6 | 3 | pool-fragment | 08012228 ldr r0, [pc, #0x19c] (x5) | a loaded word crosses the row boundary |
| `0x125D0` | `0x125D2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x128F4` | `0x128F6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x128FA` | `0x128FE` | 4 | 1.50 | 0.00 | 1 | 0 | pool-fragment | 08012848 ldr r0, [pc, #0xb0] (x1) | a loaded word crosses the row boundary |
| `0x12B58` | `0x12B5A` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x12B5A` | `0x12B5E` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x12D0A` | `0x12D0C` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x12D0C` | `0x12D10` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x12FA4` | `0x12FA6` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x12FA6` | `0x12FAA` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x13072` | `0x13074` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x131B4` | `0x131B6` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x131B6` | `0x131BA` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x13908` | `0x1390A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0801362E ldr r2, [pc, #0x2d8] (x1) | a loaded word crosses the row boundary |
| `0x13B94` | `0x13B96` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x13B96` | `0x13B9A` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x13E20` | `0x13E22` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08013BF8 ldr r0, [pc, #0x224] (x1) | a loaded word crosses the row boundary |
| `0x13FBE` | `0x13FC0` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x13FC0` | `0x13FC4` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1411C` | `0x1411E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0801405A ldr r0, [pc, #0xc0] (x2) | a loaded word crosses the row boundary |
| `0x14180` | `0x14182` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x153F2` | `0x15470` | 126 | 5.15 | 0.02 | 31 | 0 | code-null | 080152F8 b #0x80153f6 | a decoded branch enters and an instruction decodes, but the branch channel is below its own null |
| `0x15470` | `0x15472` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x15998` | `0x1599A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08015986 ldr r1, [pc, #0x10] (x1) | a loaded word crosses the row boundary |
| `0x159C2` | `0x159C4` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x159CA` | `0x159CC` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x15A24` | `0x15A26` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08015A04 ldr r1, [pc, #0x1c] (x1) | a loaded word crosses the row boundary |
| `0x15A94` | `0x15A96` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x15E80` | `0x15E94` | 20 | 3.44 | 0.00 | 5 | 5 | pool-partial | 08015C94 ldr r0, [pc, #0x1f0] (x8) | 4 of 5 word(s) load; the rest have no reader |
| `0x16300` | `0x16302` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x164B8` | `0x164D0` | 24 | 3.64 | 0.17 | 6 | 4 | pool | 08016322 ldr r0, [pc, #0x194] (x14) | decoded, section above |
| `0x16714` | `0x16718` | 4 | 1.50 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x16748` | `0x1674A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x1678C` | `0x1678E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080164E4 ldr r4, [pc, #0x2a4] (x1) | a loaded word crosses the row boundary |
| `0x16996` | `0x16998` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x16998` | `0x1699C` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x16A92` | `0x16AA8` | 22 | 3.64 | 0.18 | 5 | 0 | unreached | 080167AE ldr r1, [pc, #0x2e4] (x13) | no decoded reader and no naming word at half-open bounds |
| `0x16B66` | `0x16C58` | 242 | 5.77 | 0.04 | 60 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x16CCC` | `0x16CCE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08016ACC ldr r0, [pc, #0x1fc] (x2) | a loaded word crosses the row boundary |
| `0x1710C` | `0x1710E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x174FE` | `0x17500` | 2 | 1.00 | 0.00 | 0 | 0 | after-dispatch | none | the row follows a computed jump and no instruction reads it |
| `0x175A0` | `0x175C8` | 40 | 4.80 | 0.05 | 10 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x17694` | `0x17696` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08017500 ldr r0, [pc, #0x190] (x2) | a loaded word crosses the row boundary |
| `0x178C0` | `0x178C2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080176B0 ldr r0, [pc, #0x20c] (x1) | a loaded word crosses the row boundary |
| `0x17964` | `0x17966` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x17966` | `0x1796A` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x179E6` | `0x179EA` | 4 | 2.00 | 0.25 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x17BDA` | `0x17BE0` | 6 | 2.25 | 0.33 | 1 | 0 | unreached | 080179FC ldr r0, [pc, #0x1dc] (x1) | no decoded reader and no naming word at half-open bounds |
| `0x17BE4` | `0x17BE8` | 4 | 2.00 | 0.00 | 1 | 1 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x17BEC` | `0x17BF2` | 6 | 1.46 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x18260` | `0x18268` | 8 | 2.50 | 0.00 | 2 | 2 | pool | 08017E9E ldr r0, [pc, #0x3c0] (x4) | decoded, section above |
| `0x1826C` | `0x18280` | 20 | 3.44 | 0.25 | 5 | 2 | pool | 08017ECC ldr r2, [pc, #0x39c] (x6) | decoded, section above |
| `0x18392` | `0x18394` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x18786` | `0x187A2` | 28 | 3.51 | 0.21 | 7 | 0 | pool-fragment | 0801856C ldr r0, [pc, #0x224] (x23) | a loaded word crosses the row boundary |
| `0x187A2` | `0x187A6` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x18836` | `0x1883A` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x18BE0` | `0x18BE2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08018BB2 ldr r0, [pc, #0x2c] (x2) | a loaded word crosses the row boundary |
| `0x18E5E` | `0x18E62` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x1906C` | `0x1906E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x19268` | `0x1926C` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x192AC` | `0x192AE` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x195A4` | `0x195A6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0801957C ldr r0, [pc, #0x24] (x1) | a loaded word crosses the row boundary |
| `0x1987A` | `0x1987C` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1987C` | `0x1987E` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x19D0C` | `0x19D1E` | 18 | 3.53 | 0.06 | 4 | 3 | pool-fragment | 08019B08 ldr r0, [pc, #0x200] (x4) | a loaded word crosses the row boundary |
| `0x19D1E` | `0x19D22` | 4 | 0.81 | 0.75 | 1 | 0 | pool-fragment | 08019CB8 ldr r3, [pc, #0x64] (x1) | a loaded word crosses the row boundary |
| `0x19D28` | `0x19D2A` | 2 | 1.00 | 0.00 | 0 | 0 | between | 3 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x1A23A` | `0x1A2AA` | 112 | 5.16 | 0.10 | 28 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x1A30E` | `0x1A322` | 20 | 3.48 | 0.10 | 5 | 0 | pool-fragment | 0801A006 ldr r2, [pc, #0x308] (x13) | a loaded word crosses the row boundary |
| `0x1A354` | `0x1A356` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1A356` | `0x1A35A` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1A3B0` | `0x1A3B2` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1A3B2` | `0x1A3B6` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1A3EC` | `0x1A3F2` | 6 | 2.25 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x1C6A4` | `0x1C6C6` | 34 | 4.29 | 0.15 | 8 | 5 | pool-fragment | 0801C400 ldr r2, [pc, #0x2a0] (x15) | a loaded word crosses the row boundary |
| `0x1CB32` | `0x1CB34` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1CB34` | `0x1CB38` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1CB7C` | `0x1CB86` | 10 | 3.12 | 0.00 | 2 | 2 | pool-fragment | 0801C928 ldr r0, [pc, #0x250] (x9) | a loaded word crosses the row boundary |
| `0x1D046` | `0x1D04A` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x1D08C` | `0x1D08E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0801D04C ldr r0, [pc, #0x3c] (x1) | a loaded word crosses the row boundary |
| `0x1D0A0` | `0x1D0A6` | 6 | 2.58 | 0.00 | 1 | 0 | pool-fragment | 0801D09C ldr r0, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x1D762` | `0x1D790` | 46 | 4.67 | 0.11 | 11 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x1D958` | `0x1D95A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0801D6AE ldr r0, [pc, #0x2a8] (x6) | a loaded word crosses the row boundary |
| `0x1DCE8` | `0x1DD72` | 138 | 5.76 | 0.08 | 34 | 0 | after-dispatch | none | the row follows a computed jump and no instruction reads it |
| `0x1DDA2` | `0x1DDEC` | 74 | 5.14 | 0.05 | 18 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1DDEE` | `0x1DF7E` | 400 | 6.27 | 0.04 | 100 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1DFA0` | `0x1DFA2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x1E13E` | `0x1E142` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1E9DE` | `0x1E9E2` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x1EAC2` | `0x1EAC6` | 4 | 1.50 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x1ECBC` | `0x1ECBE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0801EA10 ldr r0, [pc, #0x2a8] (x1) | a loaded word crosses the row boundary |
| `0x1F05E` | `0x1F06A` | 12 | 2.79 | 0.25 | 3 | 1 | unreached | 0801EF90 ldr r2, [pc, #0xd0] (x2) | no decoded reader and no naming word at half-open bounds |
| `0x1F220` | `0x1F22A` | 10 | 2.92 | 0.00 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x1F346` | `0x1F364` | 30 | 4.17 | 0.00 | 7 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1F790` | `0x1F792` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1F792` | `0x1F796` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1F7AE` | `0x1F7B0` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1F7B0` | `0x1F7B2` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x1FB38` | `0x1FB3A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0801F818 ldr r1, [pc, #0x31c] (x2) | a loaded word crosses the row boundary |
| `0x1FF40` | `0x1FF4E` | 14 | 2.64 | 0.00 | 3 | 3 | pool-partial | 0801FCC8 ldr r1, [pc, #0x274] (x5) | between transcribed code rows and no instruction reads it |
| `0x1FF94` | `0x1FF96` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0801FF86 ldr r1, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x20530` | `0x2054A` | 26 | 3.84 | 0.08 | 6 | 5 | pool-partial | 08020336 ldr r0, [pc, #0x1f8] (x9) | between transcribed code rows and no instruction reads it |
| `0x2065E` | `0x20660` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x20668` | `0x2066A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x2079C` | `0x2079E` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2079E` | `0x207A2` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x20A76` | `0x20A7C` | 6 | 2.25 | 0.33 | 1 | 0 | unreached | 080206D6 ldr r0, [pc, #0x3a0] (x3) | no decoded reader and no naming word at half-open bounds |
| `0x20A80` | `0x20A84` | 4 | 2.00 | 0.00 | 1 | 1 | pool | 08020704 ldr r0, [pc, #0x378] (x3) | decoded, section above |
| `0x20A88` | `0x20A8C` | 4 | 1.50 | 0.50 | 1 | 0 | pool | 0802072C ldr r2, [pc, #0x358] (x3) | decoded, section above |
| `0x20A94` | `0x20AA4` | 16 | 3.45 | 0.12 | 4 | 3 | pool-partial | 080207B2 ldr r0, [pc, #0x2e0] (x3) | 3 of 4 word(s) load; the rest have no reader |
| `0x20DA0` | `0x20DAC` | 12 | 3.25 | 0.17 | 3 | 1 | pool-partial | 08020B38 ldr r0, [pc, #0x268] (x1) | 1 of 3 word(s) load; the rest have no reader |
| `0x20EEA` | `0x20EEC` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x20EEC` | `0x20EF0` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x21052` | `0x2105A` | 8 | 2.50 | 0.25 | 2 | 0 | pool-fragment | 08020E30 ldr r2, [pc, #0x224] (x7) | a loaded word crosses the row boundary |
| `0x2105A` | `0x2105C` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x21166` | `0x2116E` | 8 | 2.75 | 0.25 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x2125E` | `0x2126A` | 12 | 3.08 | 0.17 | 3 | 0 | pool-fragment | 08021188 ldr r1, [pc, #0xd4] (x3) | a loaded word crosses the row boundary |
| `0x2127C` | `0x2127E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08021270 ldr r0, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x21728` | `0x2172A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080215B0 ldr r7, [pc, #0x174] (x5) | a loaded word crosses the row boundary |
| `0x21730` | `0x21732` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080215E4 ldr r1, [pc, #0x148] (x2) | a loaded word crosses the row boundary |
| `0x2173C` | `0x2173E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0802160A ldr r0, [pc, #0x130] (x2) | a loaded word crosses the row boundary |
| `0x21828` | `0x21832` | 10 | 2.92 | 0.20 | 2 | 1 | pool-fragment | 08021756 ldr r3, [pc, #0xd0] (x2) | a loaded word crosses the row boundary |
| `0x21832` | `0x21834` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x21870` | `0x21872` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0802183A ldr r0, [pc, #0x34] (x1) | a loaded word crosses the row boundary |
| `0x21BB4` | `0x21BB6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08021874 ldr r2, [pc, #0x33c] (x14) | a loaded word crosses the row boundary |
| `0x220C2` | `0x220D8` | 22 | 3.48 | 0.23 | 5 | 0 | between | 08021EBE ldr r4, [pc, #0x204] (x8) | between transcribed code rows and no instruction reads it |
| `0x22626` | `0x2262A` | 4 | 2.00 | 0.25 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x2266E` | `0x22672` | 4 | 2.00 | 0.00 | 1 | 0 | between | 5 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x22674` | `0x22676` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x228FA` | `0x228FC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x22900` | `0x22902` | 2 | 0.00 | 0.00 | 0 | 0 | pool-fragment | 08022870 ldr r1, [pc, #0x8c] (x4) | a loaded word crosses the row boundary |
| `0x23088` | `0x2309C` | 20 | 3.04 | 0.35 | 5 | 1 | pool-partial | 08022DF6 ldr r6, [pc, #0x290] (x2) | 2 of 5 word(s) load; the rest have no reader |
| `0x2312A` | `0x2312C` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2312C` | `0x23130` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x23482` | `0x23484` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x23488` | `0x23490` | 8 | 2.75 | 0.25 | 2 | 1 | pool | 080230A8 ldr r2, [pc, #0x3dc] (x2) | decoded, section above |
| `0x23490` | `0x234DC` | 76 | 4.16 | 0.28 | 19 | 8 | pool-partial | 08023148 ldr r1, [pc, #0x34c] (x19) | 16 of 19 word(s) load; the rest have no reader |
| `0x237BC` | `0x237BE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080235B2 ldr r0, [pc, #0x208] (x1) | a loaded word crosses the row boundary |
| `0x237C4` | `0x237C6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0802361E ldr r0, [pc, #0x1a4] (x2) | a loaded word crosses the row boundary |
| `0x23838` | `0x2383A` | 2 | 0.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x23840` | `0x23842` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x23B2A` | `0x23B50` | 38 | 4.47 | 0.05 | 9 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x23B52` | `0x23C1C` | 202 | 5.71 | 0.02 | 50 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x23C58` | `0x23C5A` | 2 | 1.00 | 0.00 | 0 | 0 | code-null | 08023C28 beq #0x8023c58 | a decoded branch enters and no ARMv4T instruction fits in the row |
| `0x23C5A` | `0x23C5E` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x23C7C` | `0x23CB8` | 60 | 4.08 | 0.22 | 15 | 8 | pool-partial | 08023B22 ldr r0, [pc, #0x160] (x6) | 4 of 15 word(s) load; the rest have no reader |
| `0x23EE0` | `0x23EE2` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x23EE2` | `0x23EE6` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x23F84` | `0x23F86` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x23F86` | `0x23F8A` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x242D6` | `0x242E2` | 12 | 3.02 | 0.25 | 3 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x2435C` | `0x2435E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x243E6` | `0x243E8` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x243E8` | `0x243EC` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x244DA` | `0x244EC` | 18 | 3.84 | 0.06 | 4 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x24556` | `0x2455E` | 8 | 2.50 | 0.25 | 2 | 0 | pool-fragment | 0802431A ldr r0, [pc, #0x23c] (x6) | a loaded word crosses the row boundary |
| `0x24666` | `0x246A2` | 60 | 4.89 | 0.08 | 15 | 0 | pool-fragment | 08024586 ldr r0, [pc, #0x114] (x2) | a loaded word crosses the row boundary |
| `0x24976` | `0x24978` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x24D44` | `0x24D94` | 80 | 4.16 | 0.31 | 20 | 5 | pool-partial | 08024A8C ldr r1, [pc, #0x2b4] (x22) | 8 of 20 word(s) load; the rest have no reader |
| `0x24E40` | `0x24E42` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x25288` | `0x2528A` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2528A` | `0x2528E` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x255A8` | `0x255AA` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x255AA` | `0x255AE` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x25AD4` | `0x25ADC` | 8 | 2.75 | 0.25 | 2 | 1 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x25AE4` | `0x25AF0` | 12 | 2.75 | 0.33 | 3 | 1 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x25AF8` | `0x25AFA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08025A3A ldr r0, [pc, #0xbc] (x2) | a loaded word crosses the row boundary |
| `0x25DF0` | `0x25DF2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08025B0E ldr r1, [pc, #0x2e0] (x1) | a loaded word crosses the row boundary |
| `0x25E4C` | `0x25E4E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x26044` | `0x26048` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x263BA` | `0x263BE` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x264D0` | `0x264D2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x26582` | `0x26584` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x26584` | `0x26588` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x266D2` | `0x266D4` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x266D4` | `0x266D8` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x26802` | `0x26804` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x26804` | `0x26808` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x26B2C` | `0x26B32` | 6 | 2.58 | 0.00 | 1 | 0 | pool-fragment | 08026ADA ldr r1, [pc, #0x54] (x1) | a loaded word crosses the row boundary |
| `0x271AC` | `0x271AE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08026F9A ldr r0, [pc, #0x210] (x1) | a loaded word crosses the row boundary |
| `0x2737A` | `0x2737C` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2737C` | `0x27380` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x27692` | `0x2769E` | 12 | 3.02 | 0.17 | 3 | 0 | pool-fragment | 080274DA ldr r0, [pc, #0x1b8] (x7) | a loaded word crosses the row boundary |
| `0x278DE` | `0x278E2` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x27926` | `0x27932` | 12 | 3.25 | 0.17 | 3 | 0 | pool-fragment | 080276D0 ldr r0, [pc, #0x254] (x7) | a loaded word crosses the row boundary |
| `0x27B38` | `0x27B4C` | 20 | 3.75 | 0.15 | 5 | 3 | pool | 080279F8 ldr r0, [pc, #0x13c] (x14) | decoded, section above |
| `0x27B8C` | `0x27B8E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x27B96` | `0x27B98` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x27D90` | `0x27D92` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x27D92` | `0x27D96` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x27E40` | `0x27E42` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x284B6` | `0x284B8` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x286B6` | `0x286B8` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x286BC` | `0x286D2` | 22 | 4.00 | 0.05 | 5 | 4 | pool-partial | 0802839C ldr r0, [pc, #0x31c] (x4) | no decoded reader and no naming word at half-open bounds |
| `0x289BA` | `0x289DE` | 36 | 4.04 | 0.14 | 9 | 0 | pool-fragment | 080286F2 ldr r0, [pc, #0x2c8] (x24) | a loaded word crosses the row boundary |
| `0x28BFA` | `0x28C02` | 8 | 2.50 | 0.25 | 2 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x28C02` | `0x28C04` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x28EBA` | `0x28EBC` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2900A` | `0x2900E` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x292D8` | `0x292E0` | 8 | 1.06 | 0.75 | 2 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x295BC` | `0x295BE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080293B0 ldr r0, [pc, #0x208] (x2) | a loaded word crosses the row boundary |
| `0x296AE` | `0x296B2` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x2995E` | `0x29962` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x299A2` | `0x299A6` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x299BA` | `0x299BC` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x299BC` | `0x299BE` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x299D8` | `0x299DA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080299B2 ldr r1, [pc, #0x24] (x2) | a loaded word crosses the row boundary |
| `0x29BD4` | `0x29BD6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x29BDC` | `0x29BDE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08029BCC ldr r1, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x29ED4` | `0x29ED6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08029EC0 ldr r0, [pc, #0x10] (x1) | a loaded word crosses the row boundary |
| `0x2A004` | `0x2A006` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08029EDA ldr r0, [pc, #0x128] (x1) | a loaded word crosses the row boundary |
| `0x2A09A` | `0x2A09E` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2A0BC` | `0x2A0C4` | 8 | 3.00 | 0.12 | 2 | 1 | pool | 0802A00C ldr r2, [pc, #0xac] (x2) | decoded, section above |
| `0x2A236` | `0x2A238` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2A238` | `0x2A23C` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2A580` | `0x2A5A2` | 34 | 4.08 | 0.12 | 8 | 6 | pool-fragment | 0802A30A ldr r0, [pc, #0x274] (x21) | a loaded word crosses the row boundary |
| `0x2A7AC` | `0x2A7B2` | 6 | 2.25 | 0.00 | 1 | 1 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2A7B2` | `0x2A7B4` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2A9F8` | `0x2AA06` | 14 | 2.99 | 0.00 | 3 | 3 | pool-fragment | 0802A83A ldr r0, [pc, #0x1bc] (x12) | a loaded word crosses the row boundary |
| `0x2AA06` | `0x2AA0A` | 4 | 0.81 | 0.75 | 1 | 0 | pool-fragment | 0802A9BA ldr r3, [pc, #0x4c] (x1) | a loaded word crosses the row boundary |
| `0x2AA1A` | `0x2AA1E` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x2AAC4` | `0x2AAC6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x2AB08` | `0x2AB0A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0802AAE6 ldr r1, [pc, #0x20] (x1) | a loaded word crosses the row boundary |
| `0x2BC1A` | `0x2BC1E` | 4 | 2.00 | 0.25 | 1 | 0 | pool-fragment | 0802BBCA ldr r0, [pc, #0x50] (x1) | a loaded word crosses the row boundary |
| `0x2BC68` | `0x2BC70` | 8 | 2.50 | 0.25 | 2 | 1 | pool | 0802BC50 ldr r1, [pc, #0x14] (x4) | decoded, section above |
| `0x2BDBE` | `0x2BDC2` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2BDC4` | `0x2BDC6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0802BD80 ldr r0, [pc, #0x40] (x2) | a loaded word crosses the row boundary |
| `0x2C058` | `0x2C066` | 14 | 3.32 | 0.00 | 3 | 3 | pool-fragment | 0802BEEA ldr r0, [pc, #0x16c] (x15) | a loaded word crosses the row boundary |
| `0x2C1D0` | `0x2C1DC` | 12 | 3.02 | 0.25 | 3 | 0 | unreached | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x2C33C` | `0x2C340` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x2C4B8` | `0x2C4BA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x2C684` | `0x2C686` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0802C4CA ldr r6, [pc, #0x1b8] (x5) | a loaded word crosses the row boundary |
| `0x2C698` | `0x2C69A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0802C67E ldr r1, [pc, #0x18] (x1) | a loaded word crosses the row boundary |
| `0x2C77A` | `0x2C782` | 8 | 2.41 | 0.38 | 2 | 0 | pool-fragment | 0802C6B0 ldr r0, [pc, #0xcc] (x2) | a loaded word crosses the row boundary |
| `0x2C8FA` | `0x2C8FE` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 0802C7B6 ldr r0, [pc, #0x144] (x2) | a loaded word crosses the row boundary |
| `0x2CBAA` | `0x2CBAE` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 0802CB7C ldr r1, [pc, #0x2c] (x1) | a loaded word crosses the row boundary |
| `0x2CD10` | `0x2CD12` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x2CD76` | `0x2CD78` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2CD78` | `0x2CD7C` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2CD80` | `0x2CD82` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0802CD7C ldr r0, [pc, #0] (x1) | a loaded word crosses the row boundary |
| `0x2CDE0` | `0x2CDE4` | 4 | 2.00 | 0.25 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x2D166` | `0x2D168` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x2D168` | `0x2D16C` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x301F4` | `0x301F6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x304DC` | `0x304DE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803045A ldr r6, [pc, #0x80] (x3) | a loaded word crosses the row boundary |
| `0x30604` | `0x30606` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08030508 ldr r1, [pc, #0xf8] (x1) | a loaded word crosses the row boundary |
| `0x3084C` | `0x30850` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x30B12` | `0x30B14` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x30B14` | `0x30B18` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x30EF4` | `0x30EF8` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x30EFC` | `0x30F04` | 8 | 2.25 | 0.00 | 2 | 2 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x30F08` | `0x30F0C` | 4 | 2.00 | 0.00 | 1 | 1 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x333A4` | `0x333A6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803334C ldr r1, [pc, #0x54] (x1) | a loaded word crosses the row boundary |
| `0x335B4` | `0x335B6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080333AC ldr r3, [pc, #0x204] (x2) | a loaded word crosses the row boundary |
| `0x3383A` | `0x33862` | 40 | 3.68 | 0.30 | 10 | 0 | between | 080335D4 ldr r0, [pc, #0x264] (x3) | between transcribed code rows and no instruction reads it |
| `0x338FC` | `0x33908` | 12 | 3.02 | 0.00 | 3 | 3 | pool-partial | 08033890 ldr r1, [pc, #0x68] (x2) | 2 of 3 word(s) load; the rest have no reader |
| `0x3396E` | `0x33972` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x33B86` | `0x33B88` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x33B88` | `0x33B8C` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x33BB2` | `0x33BB6` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x33C3A` | `0x33C3C` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x33C42` | `0x33C44` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x33D60` | `0x33D66` | 6 | 2.58 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x33D80` | `0x33D82` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08033D7C ldr r0, [pc, #0] (x1) | a loaded word crosses the row boundary |
| `0x33E72` | `0x33E74` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x33E74` | `0x33E78` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x33EE8` | `0x33EFA` | 18 | 3.95 | 0.06 | 4 | 2 | pool-fragment | 08033DCA ldr r0, [pc, #0x120] (x11) | a loaded word crosses the row boundary |
| `0x33F22` | `0x33F26` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 08033F1A ldr r1, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x35204` | `0x35208` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x355E6` | `0x355EA` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x358A2` | `0x358A4` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x35B80` | `0x35B94` | 20 | 3.64 | 0.00 | 5 | 5 | pool | 080359FC ldr r0, [pc, #0x180] (x10) | decoded, section above |
| `0x35BD4` | `0x35BD6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x35DCA` | `0x35DCE` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x35E34` | `0x35E38` | 4 | 2.00 | 0.25 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x35E82` | `0x35E86` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x35F00` | `0x35F02` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08035E9A ldr r0, [pc, #0x64] (x1) | a loaded word crosses the row boundary |
| `0x35F04` | `0x35F06` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08035EF8 ldr r1, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x35F80` | `0x35F86` | 6 | 2.58 | 0.00 | 1 | 0 | pool-fragment | 08035F0A ldr r4, [pc, #0x78] (x1) | a loaded word crosses the row boundary |
| `0x36198` | `0x3619A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08035FF8 ldr r0, [pc, #0x19c] (x3) | a loaded word crosses the row boundary |
| `0x36430` | `0x36432` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x36654` | `0x36656` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x36968` | `0x3696E` | 6 | 2.25 | 0.00 | 1 | 1 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3696E` | `0x36972` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x36A10` | `0x36A12` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803698C ldr r4, [pc, #0x80] (x1) | a loaded word crosses the row boundary |
| `0x36D66` | `0x36D82` | 28 | 3.89 | 0.18 | 7 | 0 | pool-fragment | 08036A5C ldr r0, [pc, #0x308] (x19) | a loaded word crosses the row boundary |
| `0x36D82` | `0x36D84` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3722E` | `0x37238` | 10 | 2.52 | 0.40 | 2 | 0 | unreached | 08036FC0 ldr r0, [pc, #0x270] (x3) | no decoded reader and no naming word at half-open bounds |
| `0x3723C` | `0x37248` | 12 | 3.19 | 0.00 | 3 | 3 | pool | 08036FEE ldr r0, [pc, #0x24c] (x7) | decoded, section above |
| `0x3724C` | `0x37250` | 4 | 2.00 | 0.00 | 1 | 1 | pool | 080370C2 ldr r1, [pc, #0x188] (x3) | decoded, section above |
| `0x37254` | `0x3725A` | 6 | 1.92 | 0.33 | 1 | 0 | pool-fragment | 080370EA ldr r0, [pc, #0x168] (x2) | a loaded word crosses the row boundary |
| `0x37478` | `0x3747E` | 6 | 1.92 | 0.00 | 1 | 1 | pool-partial | 080373CA ldr r1, [pc, #0xac] (x1) | no decoded reader and no naming word at half-open bounds |
| `0x3747E` | `0x37480` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x37568` | `0x3756A` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3756A` | `0x3756E` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3764A` | `0x3764C` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3764C` | `0x37650` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x37878` | `0x37880` | 8 | 2.75 | 0.00 | 2 | 2 | pool | 080374A8 ldr r0, [pc, #0x3cc] (x5) | decoded, section above |
| `0x3788C` | `0x37894` | 8 | 3.00 | 0.12 | 2 | 1 | pool | 08037502 ldr r1, [pc, #0x388] (x4) | decoded, section above |
| `0x37898` | `0x3789A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08037554 ldr r0, [pc, #0x340] (x1) | a loaded word crosses the row boundary |
| `0x378DA` | `0x378DC` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x378DC` | `0x378E0` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x378EE` | `0x378F0` | 2 | 1.00 | 0.00 | 0 | 0 | code-null | 080378E8 bne #0x80378ee | a decoded branch enters and no ARMv4T instruction fits in the row |
| `0x378F0` | `0x378F4` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x379B4` | `0x379B6` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x379B6` | `0x379BA` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x37A24` | `0x37A26` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080379C8 ldr r0, [pc, #0x58] (x1) | a loaded word crosses the row boundary |
| `0x37B2E` | `0x37B32` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x37B40` | `0x37B42` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08037A88 ldr r1, [pc, #0xb4] (x2) | a loaded word crosses the row boundary |
| `0x37BB4` | `0x37BB6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08037B4A ldr r0, [pc, #0x68] (x1) | a loaded word crosses the row boundary |
| `0x37C18` | `0x37C1A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x37D48` | `0x37D4A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x37E26` | `0x37E28` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x37E28` | `0x37E2C` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x38178` | `0x3817C` | 4 | 2.00 | 0.00 | 1 | 1 | pool | 08037EC4 ldr r0, [pc, #0x2b0] (x3) | decoded, section above |
| `0x38180` | `0x38192` | 18 | 3.50 | 0.22 | 4 | 2 | pool-fragment | 08037EEE ldr r0, [pc, #0x290] (x8) | a loaded word crosses the row boundary |
| `0x382BE` | `0x382C0` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x382C0` | `0x382C4` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x383CA` | `0x383D2` | 8 | 2.50 | 0.25 | 2 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x383D2` | `0x383D4` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3870A` | `0x3870C` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x387D2` | `0x387D6` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 08038714 ldr r2, [pc, #0xbc] (x1) | a loaded word crosses the row boundary |
| `0x38A82` | `0x38A84` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x38AD0` | `0x38AD2` | 2 | 0.00 | 1.00 | 0 | 0 | pool-fragment | 08038A9E ldr r5, [pc, #0x30] (x1) | a loaded word crosses the row boundary |
| `0x38DD8` | `0x38DE2` | 10 | 2.92 | 0.20 | 2 | 1 | pool-fragment | 08038BB6 ldr r0, [pc, #0x220] (x3) | a loaded word crosses the row boundary |
| `0x39120` | `0x39122` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3925C` | `0x3925E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3934A` | `0x3934E` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x39360` | `0x39362` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803935C ldr r0, [pc, #0] (x1) | a loaded word crosses the row boundary |
| `0x393BE` | `0x393C2` | 4 | 2.00 | 0.25 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3942A` | `0x3942E` | 4 | 2.00 | 0.25 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x39440` | `0x39442` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803943C ldr r0, [pc, #0] (x1) | a loaded word crosses the row boundary |
| `0x39472` | `0x39476` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x39562` | `0x39566` | 4 | 0.81 | 0.75 | 1 | 0 | pool-fragment | 08039486 ldr r0, [pc, #0xdc] (x2) | a loaded word crosses the row boundary |
| `0x3973E` | `0x3974A` | 12 | 3.02 | 0.25 | 3 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3983C` | `0x3983E` | 2 | 1.00 | 0.50 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x398C4` | `0x398CA` | 6 | 2.58 | 0.00 | 1 | 0 | pool-fragment | 080398AE ldr r0, [pc, #0x18] (x1) | a loaded word crosses the row boundary |
| `0x39994` | `0x39996` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x39998` | `0x3999A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x39BCC` | `0x39BCE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08039B10 ldr r1, [pc, #0xb8] (x6) | a loaded word crosses the row boundary |
| `0x39C0E` | `0x39C12` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 08039C08 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x39D7A` | `0x39D8E` | 20 | 3.52 | 0.20 | 5 | 0 | pool-fragment | 08039C22 ldr r3, [pc, #0x15c] (x9) | a loaded word crosses the row boundary |
| `0x39F08` | `0x39F16` | 14 | 3.52 | 0.14 | 3 | 1 | pool-fragment | 08039DB6 ldr r0, [pc, #0x158] (x4) | a loaded word crosses the row boundary |
| `0x3A084` | `0x3A086` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08039F2A ldr r1, [pc, #0x158] (x2) | a loaded word crosses the row boundary |
| `0x3A62C` | `0x3A62E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3A68E` | `0x3A692` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3A790` | `0x3A792` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803A6BE ldr r5, [pc, #0xd0] (x1) | a loaded word crosses the row boundary |
| `0x3A7EE` | `0x3A7F2` | 4 | 2.00 | 0.00 | 1 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3A7F4` | `0x3A7F6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803A7D8 ldr r0, [pc, #0x18] (x1) | a loaded word crosses the row boundary |
| `0x3AC4C` | `0x3AC54` | 8 | 2.75 | 0.00 | 2 | 1 | pool-partial | 0803A872 ldr r0, [pc, #0x3d8] (x2) | 1 of 2 word(s) load; the rest have no reader |
| `0x3AC58` | `0x3AC5C` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3AC64` | `0x3AC70` | 12 | 2.92 | 0.08 | 3 | 1 | pool | 0803AA7C ldr r1, [pc, #0x1e4] (x5) | decoded, section above |
| `0x3AE60` | `0x3AE62` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3AEA0` | `0x3AEA2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803AE7A ldr r1, [pc, #0x24] (x1) | a loaded word crosses the row boundary |
| `0x3B1C4` | `0x3B1C6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803AEEE ldr r5, [pc, #0x2d4] (x3) | a loaded word crosses the row boundary |
| `0x3B1D2` | `0x3B1D4` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3B368` | `0x3B36A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803B336 ldr r1, [pc, #0x30] (x1) | a loaded word crosses the row boundary |
| `0x3B514` | `0x3B516` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3B524` | `0x3B526` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3B56C` | `0x3B56E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3B572` | `0x3B574` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3B5F0` | `0x3B5F2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3B5F6` | `0x3B5F8` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3B7A8` | `0x3B7AA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3B7B8` | `0x3B7BA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3B99A` | `0x3B99C` | 2 | 1.00 | 0.00 | 0 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3B9A4` | `0x3B9A6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3BAD0` | `0x3BAD2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3BC18` | `0x3BC1A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803B936 ldr r0, [pc, #0x2e0] (x1) | a loaded word crosses the row boundary |
| `0x3BC24` | `0x3BC26` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3BCF6` | `0x3BCF8` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3BD84` | `0x3BD86` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803BD22 ldr r0, [pc, #0x60] (x1) | a loaded word crosses the row boundary |
| `0x3BF0E` | `0x3BF28` | 26 | 4.13 | 0.15 | 6 | 0 | unreached | 0803BDA6 ldr r2, [pc, #0x16c] (x6) | named by a word; a name is not a consumer |
| `0x3C0A8` | `0x3C0B6` | 14 | 3.52 | 0.14 | 3 | 1 | pool-partial | 0803C016 ldr r1, [pc, #0x98] (x6) | between transcribed code rows and no instruction reads it |
| `0x3C0C0` | `0x3C0C2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803C0BC ldr r0, [pc, #0] (x1) | a loaded word crosses the row boundary |
| `0x3C1D8` | `0x3C1DA` | 2 | 1.00 | 0.50 | 0 | 0 | pool-fragment | 0803C0EA ldr r1, [pc, #0xec] (x2) | a loaded word crosses the row boundary |
| `0x3C2F0` | `0x3C2F2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803C206 ldr r1, [pc, #0xe8] (x2) | a loaded word crosses the row boundary |
| `0x3C408` | `0x3C40A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803C31E ldr r1, [pc, #0xe8] (x2) | a loaded word crosses the row boundary |
| `0x3C4D8` | `0x3C4DC` | 4 | 2.00 | 0.00 | 1 | 1 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3C602` | `0x3C604` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3C60A` | `0x3C60C` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3C814` | `0x3C816` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3C8D0` | `0x3C8D2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803C85A ldr r5, [pc, #0x74] (x1) | a loaded word crosses the row boundary |
| `0x3CD24` | `0x3CD26` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803CB84 ldr r0, [pc, #0x19c] (x3) | a loaded word crosses the row boundary |
| `0x3CE64` | `0x3CE66` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803CDB0 ldr r1, [pc, #0xb0] (x2) | a loaded word crosses the row boundary |
| `0x3D0EC` | `0x3D0EE` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3D0EE` | `0x3D0F2` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3D0FA` | `0x3D10C` | 18 | 2.66 | 0.28 | 4 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3D360` | `0x3D362` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803D114 ldr r0, [pc, #0x248] (x1) | a loaded word crosses the row boundary |
| `0x3D370` | `0x3D372` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0803D358 ldr r1, [pc, #0x14] (x1) | a loaded word crosses the row boundary |
| `0x3DA74` | `0x3DA76` | 2 | 1.00 | 0.50 | 0 | 0 | pool-fragment | 0803D9B4 ldr r0, [pc, #0xbc] (x3) | a loaded word crosses the row boundary |
| `0x3DAAC` | `0x3DAB6` | 10 | 2.52 | 0.00 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3DD32` | `0x3DD34` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3DD34` | `0x3DD38` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3DF12` | `0x3DF14` | 2 | 0.00 | 1.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3E014` | `0x3E016` | 2 | 1.00 | 0.50 | 0 | 0 | pool-fragment | 0803DF1A ldr r0, [pc, #0xf8] (x1) | a loaded word crosses the row boundary |
| `0x3E142` | `0x3E144` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3E368` | `0x3E36A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3E848` | `0x3E89A` | 82 | 5.55 | 0.04 | 20 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3E950` | `0x3E954` | 4 | 1.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3E9A8` | `0x3EA24` | 124 | 5.43 | 0.05 | 31 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3EA46` | `0x3EB1A` | 212 | 5.75 | 0.04 | 53 | 0 | between | 0803E89A ldr r3, [pc, #0x1bc] (x2) | between transcribed code rows and no instruction reads it |
| `0x3EB68` | `0x3EB6C` | 4 | 1.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3EB96` | `0x3EB98` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3EBF4` | `0x3EBF8` | 4 | 1.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3ECA2` | `0x3ECA6` | 4 | 1.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3ECC2` | `0x3ECC6` | 4 | 1.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3F1B4` | `0x3F1B6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3F36C` | `0x3F36E` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3F36E` | `0x3F372` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x3FCA4` | `0x3FCA6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3FCDE` | `0x3FCE0` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3FD34` | `0x3FD36` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3FF08` | `0x3FF0A` | 2 | 1.00 | 0.00 | 0 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x3FF16` | `0x3FF18` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3FF32` | `0x3FF34` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3FF4E` | `0x3FF50` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3FF98` | `0x3FF9A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3FF9E` | `0x3FFA0` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3FFAA` | `0x3FFAC` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x3FFC6` | `0x3FFC8` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x40794` | `0x407A0` | 12 | 1.95 | 0.58 | 3 | 1 | between | none | between transcribed code rows and no instruction reads it |
| `0x40880` | `0x40882` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x40A14` | `0x40A18` | 4 | 2.00 | 0.25 | 1 | 0 | pool | 080409B6 ldr r0, [pc, #0x5c] (x2) | decoded, section above |
| `0x40AE2` | `0x40AF0` | 14 | 3.09 | 0.29 | 3 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x40B22` | `0x40B24` | 2 | 0.00 | 1.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x40B9A` | `0x40B9C` | 2 | 0.00 | 1.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x40F7C` | `0x40F7E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4110C` | `0x41110` | 4 | 2.00 | 0.25 | 1 | 0 | pool | 0804106C ldr r0, [pc, #0x9c] (x1) | decoded, section above |
| `0x42118` | `0x42188` | 112 | 4.95 | 0.01 | 28 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4222A` | `0x4222C` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4222C` | `0x42230` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4223C` | `0x4223E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4225E` | `0x42260` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x424FE` | `0x42500` | 2 | 0.00 | 1.00 | 0 | 0 | after-dispatch | none | the row follows a computed jump and no instruction reads it |
| `0x42500` | `0x4251E` | 30 | 2.92 | 0.30 | 7 | 0 | after-dispatch | none | the row follows a computed jump and no instruction reads it |
| `0x4256C` | `0x42592` | 38 | 3.81 | 0.18 | 9 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x42594` | `0x425B0` | 28 | 4.16 | 0.11 | 7 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x425B4` | `0x425F0` | 60 | 4.94 | 0.12 | 15 | 0 | pool-partial | 08042244 ldr r3, [pc, #0x3a0] (x1) | 1 of 15 word(s) load; the rest have no reader |
| `0x425F2` | `0x42604` | 18 | 4.06 | 0.00 | 4 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4260A` | `0x42638` | 46 | 4.88 | 0.02 | 11 | 0 | between | 2 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x4263C` | `0x4269C` | 96 | 4.79 | 0.18 | 24 | 0 | pool-partial | 0804227E ldr r2, [pc, #0x3dc] (x7) | 3 of 24 word(s) load; the rest have no reader |
| `0x4269E` | `0x426C4` | 38 | 4.43 | 0.08 | 9 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x426D0` | `0x42750` | 128 | 5.04 | 0.15 | 32 | 0 | code-null | 08042604 b #0x80426d0 | a decoded branch enters and an instruction decodes, but the branch channel is below its own null |
| `0x42784` | `0x42876` | 242 | 5.71 | 0.12 | 60 | 0 | code-null | 08042638 b #0x8042784 | a decoded branch enters and an instruction decodes, but the branch channel is below its own null |
| `0x42BAC` | `0x42BBC` | 16 | 3.50 | 0.12 | 4 | 2 | pool | 08042884 ldr r5, [pc, #0x328] (x22) | decoded, section above |
| `0x42D2A` | `0x42D72` | 72 | 4.51 | 0.01 | 18 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x42FAA` | `0x42FAC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x42FB8` | `0x42FBC` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x462AC` | `0x46A7A` | 1998 | 5.56 | 0.17 | 499 | 0 | named-data | 00045A7A ldr [pc] 0x045E18 = 0x08046A28 | code loads a word naming this row; its bytes have no layout |
| `0x46AA8` | `0x46AAE` | 6 | 1.79 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x46C50` | `0x46C54` | 4 | 2.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x46CBA` | `0x46CBC` | 2 | 0.00 | 1.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x47040` | `0x47648` | 1544 | 5.70 | 0.17 | 386 | 0 | between | 3 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x47652` | `0x47654` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x47684` | `0x47686` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x476A6` | `0x476A8` | 2 | 0.00 | 1.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4776E` | `0x47770` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x47770` | `0x479FC` | 652 | 5.38 | 0.11 | 163 | 0 | unreached | 5 naming word(s) | named by a word; a name is not a consumer |
| `0x479FC` | `0x47A00` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x47A02` | `0x47A08` | 6 | 2.25 | 0.33 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x47FAE` | `0x47FB0` | 2 | 0.00 | 1.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4802E` | `0x48034` | 6 | 2.25 | 0.33 | 1 | 0 | unreached | 08047FF6 ldr r6, [pc, #0x38] (x1) | no decoded reader and no naming word at half-open bounds |
| `0x480EA` | `0x480EC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x48186` | `0x4818A` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48194` | `0x48196` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0804818C ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x481E4` | `0x481E6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48228` | `0x4822A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48238` | `0x4823A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048230 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x482A0` | `0x482A2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x482AC` | `0x482AE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080482A4 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x482BC` | `0x482BE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080482B4 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48400` | `0x48402` | 2 | 1.00 | 0.00 | 0 | 0 | between | 3 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x4840C` | `0x4840E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048404 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x4841C` | `0x4841E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048414 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48430` | `0x48432` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048420 ldr r0, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x48490` | `0x48492` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x484E4` | `0x484E6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x484F8` | `0x484FA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080484EC ldr r1, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x48508` | `0x4850A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048500 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48518` | `0x4851A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048510 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x4854C` | `0x4854E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4855C` | `0x4855E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048554 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x4856C` | `0x4856E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048564 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x4859C` | `0x4859E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x485B0` | `0x485B2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080485A8 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x485DC` | `0x485DE` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48618` | `0x4861A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4862A` | `0x4862E` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 0804861C ldr r0, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x48640` | `0x48642` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048638 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48650` | `0x48652` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048648 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48660` | `0x48662` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048658 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x4868C` | `0x4868E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48716` | `0x4871A` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48732` | `0x48736` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 08048724 ldr r0, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x4879C` | `0x4879E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x487C8` | `0x487CA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x487E8` | `0x487EA` | 2 | 1.00 | 0.50 | 0 | 0 | pool-fragment | 080487D6 ldr r0, [pc, #0x10] (x1) | a loaded word crosses the row boundary |
| `0x487F4` | `0x487F6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080487EC ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x487F8` | `0x487FA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080487EE ldr r0, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x48804` | `0x48806` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080487FC ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48808` | `0x4880A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080487FE ldr r0, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x48828` | `0x4882A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048816 ldr r0, [pc, #0x10] (x1) | a loaded word crosses the row boundary |
| `0x48844` | `0x48846` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48848` | `0x4884A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48864` | `0x48866` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048852 ldr r0, [pc, #0x10] (x1) | a loaded word crosses the row boundary |
| `0x4889C` | `0x4889E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048894 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x488AC` | `0x488AE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080488A4 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x488F4` | `0x488F6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48904` | `0x48906` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080488FC ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48950` | `0x48952` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48960` | `0x48962` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048958 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48974` | `0x48976` | 2 | 1.00 | 0.50 | 0 | 0 | pool-fragment | 08048968 ldr r1, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x4898A` | `0x4898E` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 0804897C ldr r0, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x489A0` | `0x489A2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048998 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48A02` | `0x48A06` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48A18` | `0x48A1A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048A10 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48A28` | `0x48A2A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048A20 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48A38` | `0x48A3A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048A30 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48A54` | `0x48A56` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048A40 ldr r1, [pc, #0x10] (x1) | a loaded word crosses the row boundary |
| `0x48A88` | `0x48A8A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48A98` | `0x48A9A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048A90 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48AB4` | `0x48AB6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48AB8` | `0x48ABA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48AC4` | `0x48AC6` | 2 | 1.00 | 0.50 | 0 | 0 | pool-fragment | 08048ABC ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48AE4` | `0x48AE6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48AF4` | `0x48AF6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048AEC ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48B18` | `0x48B1A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048B06 ldr r0, [pc, #0x10] (x1) | a loaded word crosses the row boundary |
| `0x48B24` | `0x48B26` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048B1C ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48B34` | `0x48B36` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048B2C ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48B44` | `0x48B46` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048B3C ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48B76` | `0x48B7A` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48BBE` | `0x48BC2` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48BD4` | `0x48BD6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48BD8` | `0x48BDA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48BE4` | `0x48BE6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048BDC ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48BF4` | `0x48BF6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048BEC ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48C42` | `0x48C46` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48C58` | `0x48C5A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048C50 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48C84` | `0x48C86` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48D0C` | `0x48D0E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48D1C` | `0x48D1E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048D14 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48D2C` | `0x48D2E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048D24 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48D40` | `0x48D42` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048D34 ldr r1, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x48D50` | `0x48D52` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048D48 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48D70` | `0x48D72` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048D68 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48D90` | `0x48D92` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48DB0` | `0x48DB2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48DC0` | `0x48DC2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048DB8 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48DD0` | `0x48DD2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048DC8 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48DE6` | `0x48DEA` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 08048DD8 ldr r0, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x48DFC` | `0x48DFE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048DF4 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48E38` | `0x48E3A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48E44` | `0x48E46` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048E3C ldr r0, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48E54` | `0x48E56` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048E4C ldr r0, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x48E84` | `0x48E86` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x48EA4` | `0x48EA6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048E8C ldr r0, [pc, #0x14] (x1) | a loaded word crosses the row boundary |
| `0x48EB4` | `0x48EB6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08048EA8 ldr r0, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x48ECA` | `0x48F54` | 138 | 3.57 | 0.02 | 34 | 0 | unreached | 08048EBC ldr r0, [pc, #0xc] (x3) | no decoded reader and no naming word at half-open bounds |
| `0x48F54` | `0x49010` | 188 | 3.13 | 0.00 | 47 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x49010` | `0x49114` | 260 | 3.32 | 0.00 | 65 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x49124` | `0x4912C` | 8 | 2.75 | 0.25 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x49130` | `0x49138` | 8 | 3.00 | 0.12 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4913C` | `0x49144` | 8 | 3.00 | 0.12 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x49148` | `0x49150` | 8 | 3.00 | 0.12 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x49154` | `0x4915C` | 8 | 2.75 | 0.12 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x49160` | `0x49168` | 8 | 2.75 | 0.12 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4916C` | `0x49174` | 8 | 3.00 | 0.12 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x49178` | `0x49180` | 8 | 3.00 | 0.12 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x49184` | `0x4918C` | 8 | 2.75 | 0.25 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x49190` | `0x49198` | 8 | 3.00 | 0.12 | 2 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x4919C` | `0x491A0` | 4 | 2.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x491A4` | `0x491A8` | 4 | 2.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x491AC` | `0x491B4` | 8 | 3.00 | 0.12 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x491B8` | `0x491C0` | 8 | 3.00 | 0.12 | 2 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x491C4` | `0x494D8` | 788 | 5.09 | 0.30 | 197 | 3 | named-data | 00002892 ldr [pc] 0x002970 = 0x0804920C | code loads a word naming this row; its bytes have no layout |
| `0x494DE` | `0x49B44` | 1638 | 5.37 | 0.29 | 409 | 0 | named-data | 0000236E ldr [pc] 0x002434 = 0x080495B4 | code loads a word naming this row; its bytes have no layout |
| `0x49DB8` | `0x49DBA` | 2 | 1.00 | 0.00 | 0 | 0 | named-data | 00048A32 ldr [pc] 0x048A3C = 0x08049DB8 | code loads a word naming this row; its bytes have no layout |
| `0x49DC8` | `0x49DCA` | 2 | 1.00 | 0.00 | 0 | 0 | named-data | 0003334C ldr [pc] 0x0333A4 = 0x08049DC8 | code loads a word naming this row; its bytes have no layout |
| `0x49DCA` | `0x4A1FC` | 1074 | 5.30 | 0.27 | 268 | 0 | named-data | 0000252C ldr [pc] 0x0026C4 = 0x0804A070 | code loads a word naming this row; its bytes have no layout |
| `0x4A1FE` | `0x4A202` | 4 | 2.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4A218` | `0x4A21A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4A242` | `0x4A244` | 2 | 0.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A244` | `0x4A246` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A24A` | `0x4A254` | 10 | 2.52 | 0.40 | 2 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A254` | `0x4A25C` | 8 | 2.00 | 0.50 | 2 | 0 | named-data | 0001413E ldr [pc] 0x014180 = 0x0804A254 | code loads a word naming this row; its bytes have no layout |
| `0x4A25C` | `0x4A260` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A260` | `0x4A264` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A264` | `0x4A268` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A268` | `0x4A298` | 48 | 4.03 | 0.08 | 12 | 0 | named-data | 000374A8 ldr [pc] 0x037878 = 0x0804A26C | code loads a word naming this row; its bytes have no layout |
| `0x4A298` | `0x4A29C` | 4 | 2.00 | 0.00 | 1 | 0 | named-data | 0001634A ldr [pc] 0x0164C0 = 0x0804A298 | code loads a word naming this row; its bytes have no layout |
| `0x4A29C` | `0x4A2A0` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A2A0` | `0x4A2A4` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A2A4` | `0x4A2A8` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A2A8` | `0x4A2BC` | 20 | 3.32 | 0.10 | 5 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A2BC` | `0x4A404` | 328 | 5.05 | 0.14 | 82 | 0 | pool-partial | 0804A22C ldr r3, [pc, #0xc4] (x1) | 1 of 82 word(s) load; the rest have no reader |
| `0x4A404` | `0x4A408` | 4 | 1.50 | 0.50 | 1 | 0 | named-data | 000028A6 ldr [pc] 0x002974 = 0x0804A404 | code loads a word naming this row; its bytes have no layout |
| `0x4A408` | `0x4A40C` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A40C` | `0x4A410` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A410` | `0x4A414` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A414` | `0x4A418` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A418` | `0x4A420` | 8 | 2.75 | 0.25 | 2 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A420` | `0x4A424` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A424` | `0x4A428` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A428` | `0x4A42C` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A42C` | `0x4A4BC` | 144 | 4.74 | 0.15 | 36 | 0 | named-data | 00005302 ldr [pc] 0x005438 = 0x0804A430 | code loads a word naming this row; its bytes have no layout |
| `0x4A4BC` | `0x4A4C0` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A4C0` | `0x4A4D4` | 20 | 3.15 | 0.30 | 5 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A4D4` | `0x4A4D8` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A4D8` | `0x4A4DC` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A4DC` | `0x4A4E0` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A4E0` | `0x4A4E4` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4A4E4` | `0x4A59C` | 184 | 4.54 | 0.17 | 46 | 0 | named-data | 0002570A ldr [pc] 0x025AD8 = 0x0804A4E8 | code loads a word naming this row; its bytes have no layout |
| `0x4A67C` | `0x4A67E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0804A5A4 ldr r1, [pc, #0xd4] (x1) | a loaded word crosses the row boundary |
| `0x4AA8A` | `0x4AA8E` | 4 | 2.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4AA90` | `0x4AA92` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4AAA0` | `0x4AAA2` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4AABA` | `0x4AABE` | 4 | 2.00 | 0.00 | 1 | 0 | named-data | 000299F4 ldr [pc] 0x029A3C = 0x0804AABC | code loads a word naming this row; its bytes have no layout |
| `0x4AAE0` | `0x4AAE2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4AAF0` | `0x4AAF2` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4AAF2` | `0x4AB24` | 50 | 3.87 | 0.24 | 12 | 0 | named-data | 00018E8C ldr [pc] 0x01906C = 0x0804AAF4 | code loads a word naming this row; its bytes have no layout |
| `0x4AB24` | `0x4AC8C` | 360 | 4.95 | 0.27 | 90 | 0 | named-data | 00001290 ldr [pc] 0x0013A8 = 0x0804AB58 | code loads a word naming this row; its bytes have no layout |
| `0x4AC8C` | `0x4AC94` | 8 | 2.75 | 0.25 | 2 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4AC94` | `0x4AC98` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4AC98` | `0x4AC9C` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4AC9C` | `0x4ACAC` | 16 | 3.33 | 0.12 | 4 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4ACAC` | `0x4ACB0` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4ACB0` | `0x4AEB0` | 512 | 5.06 | 0.29 | 128 | 0 | pool-partial | 0804AA88 ldr r4, [pc, #0x284] (x4) | 4 of 128 word(s) load; the rest have no reader |
| `0x4AEB0` | `0x4AEB4` | 4 | 1.50 | 0.50 | 1 | 0 | named-data | 0001245E ldr [pc] 0x0125D0 = 0x0804AEB0 | code loads a word naming this row; its bytes have no layout |
| `0x4AEB4` | `0x4AFF8` | 324 | 5.09 | 0.17 | 81 | 0 | named-data | 0001D0D8 ldr [pc] 0x01D3F8 = 0x0804AFCC | code loads a word naming this row; its bytes have no layout |
| `0x4AFF8` | `0x4B000` | 8 | 2.75 | 0.25 | 2 | 0 | named-data | 0001752C ldr [pc] 0x0176A4 = 0x0804AFF8 | code loads a word naming this row; its bytes have no layout |
| `0x4B000` | `0x4B024` | 36 | 3.70 | 0.11 | 9 | 0 | unreached | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x4B024` | `0x4B02C` | 8 | 2.75 | 0.25 | 2 | 0 | named-data | 00017186 ldr [pc] 0x0174D4 = 0x0804B024 | code loads a word naming this row; its bytes have no layout |
| `0x4B02C` | `0x4B040` | 20 | 3.25 | 0.30 | 5 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B040` | `0x4B2DC` | 668 | 5.01 | 0.31 | 167 | 0 | named-data | 00000E8E ldr [pc] 0x0010F0 = 0x0804B2B4 | code loads a word naming this row; its bytes have no layout |
| `0x4B2DC` | `0x4B2E4` | 8 | 2.75 | 0.25 | 2 | 0 | named-data | 000060DA ldr [pc] 0x00627C = 0x0804B2DC | code loads a word naming this row; its bytes have no layout |
| `0x4B2E4` | `0x4B2E8` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B2E8` | `0x4B2EC` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B2EC` | `0x4B2F0` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B2F0` | `0x4B2F4` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B2F4` | `0x4B3D8` | 228 | 5.09 | 0.17 | 57 | 0 | named-data | 0000A1F2 ldr [pc] 0x00A214 = 0x0804B308 | code loads a word naming this row; its bytes have no layout |
| `0x4B3D8` | `0x4B3DC` | 4 | 1.50 | 0.50 | 1 | 0 | named-data | 0002BF16 ldr [pc] 0x02C060 = 0x0804B3D8 | code loads a word naming this row; its bytes have no layout |
| `0x4B3DC` | `0x4B3E4` | 8 | 2.00 | 0.50 | 2 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B3E4` | `0x4B3E8` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B3E8` | `0x4B3FC` | 20 | 3.48 | 0.10 | 5 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B3FC` | `0x4B45C` | 96 | 4.38 | 0.19 | 24 | 0 | named-data | 0000D36C ldr [pc] 0x00D52C = 0x0804B428 | code loads a word naming this row; its bytes have no layout |
| `0x4B45C` | `0x4B468` | 12 | 2.40 | 0.00 | 3 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B468` | `0x4B47C` | 20 | 3.06 | 0.00 | 5 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B47C` | `0x4B52C` | 176 | 4.48 | 0.15 | 44 | 0 | named-data | 00004744 ldr [pc] 0x004834 = 0x0804B500 | code loads a word naming this row; its bytes have no layout |
| `0x4B52C` | `0x4B54C` | 32 | 3.66 | 0.19 | 8 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B54C` | `0x4B894` | 840 | 5.11 | 0.29 | 210 | 0 | named-data | 00003436 ldr [pc] 0x00344C = 0x0804B5D8 | code loads a word naming this row; its bytes have no layout |
| `0x4B894` | `0x4B898` | 4 | 1.50 | 0.50 | 1 | 0 | named-data | 00021192 ldr [pc] 0x021268 = 0x0804B894 | code loads a word naming this row; its bytes have no layout |
| `0x4B898` | `0x4B89C` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B89C` | `0x4B8A0` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8A0` | `0x4B8A4` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8A4` | `0x4B8A8` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8A8` | `0x4B8AC` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8AC` | `0x4B8B0` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8B0` | `0x4B8B4` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8B4` | `0x4B8C4` | 16 | 2.77 | 0.44 | 4 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8C4` | `0x4B8C8` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8C8` | `0x4B8CC` | 4 | 1.00 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8CC` | `0x4B8D0` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8D0` | `0x4B8D4` | 4 | 1.50 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8D4` | `0x4B8D8` | 4 | 0.81 | 0.75 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4B8D8` | `0x4B940` | 104 | 4.53 | 0.23 | 26 | 0 | named-data | 00000FF8 ldr [pc] 0x0010FC = 0x0804B918 | code loads a word naming this row; its bytes have no layout |
| `0x4B940` | `0x4BA78` | 312 | 5.04 | 0.19 | 78 | 0 | named-data | 000019C6 ldr [pc] 0x001C0C = 0x0804B940 | code loads a word naming this row; its bytes have no layout |
| `0x4BA80` | `0x4BA82` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E4DA` | `0x4E4DC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E4DE` | `0x4E4E0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x4E4E2` | `0x4E4E4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E4E6` | `0x4E4E8` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E4EA` | `0x4E4EC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E4EE` | `0x4E4F0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E4F2` | `0x4E4F4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E4F6` | `0x4E4F8` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E4FA` | `0x4E4FC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E4FE` | `0x4E500` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E502` | `0x4E504` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E506` | `0x4E508` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E51E` | `0x4E520` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E522` | `0x4E524` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E546` | `0x4E548` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E54A` | `0x4E54C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4E5B4` | `0x4E5B6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4E604` | `0x4E606` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4E954` | `0x4E956` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4E9E4` | `0x4E9E6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4EA08` | `0x4EA0A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0804E9F8 ldr r1, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x4EAF0` | `0x4EAF2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4EC02` | `0x4EC04` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4EC06` | `0x4EC08` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4EC18` | `0x4EC1C` | 4 | 2.00 | 0.25 | 1 | 0 | pool | 0804EC10 ldr r1, [pc, #4] (x1) | decoded, section above |
| `0x4EC1E` | `0x4EC20` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4EC9A` | `0x4EC9C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4ECBE` | `0x4ECC0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4ECE2` | `0x4ECE4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4ECF6` | `0x4ECF8` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4ED94` | `0x4ED96` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4EE20` | `0x4EE22` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4EE58` | `0x4EE5A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4EEF8` | `0x4EEFA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4EF1C` | `0x4EF1E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0804EF12 ldr r2, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x4EF44` | `0x4EF46` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0804EF36 ldr r1, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x4EF68` | `0x4EF6A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0804EF5E ldr r2, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x4F00A` | `0x4F00C` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F02E` | `0x4F032` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 0804F01A ldr r0, [pc, #0x14] (x2) | a loaded word crosses the row boundary |
| `0x4F05E` | `0x4F060` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F076` | `0x4F078` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F09E` | `0x4F0A0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F0A2` | `0x4F0A4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F0C2` | `0x4F0C4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F0DE` | `0x4F0E0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x4F116` | `0x4F118` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F15E` | `0x4F160` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F162` | `0x4F164` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F172` | `0x4F174` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F176` | `0x4F178` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F186` | `0x4F188` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F19E` | `0x4F1A0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F1A2` | `0x4F1A4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F1A6` | `0x4F1A8` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F1AA` | `0x4F1AC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F1AE` | `0x4F1B0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F1B2` | `0x4F1B4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F1E4` | `0x4F1E8` | 4 | 2.00 | 0.00 | 1 | 1 | pool | 0804F1C8 ldr r0, [pc, #0x18] (x1) | decoded, section above |
| `0x4F1EA` | `0x4F1EC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F1EE` | `0x4F1F0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F1F2` | `0x4F1F4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F1F6` | `0x4F1F8` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F1FA` | `0x4F1FC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F1FE` | `0x4F200` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F202` | `0x4F204` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F206` | `0x4F208` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F20A` | `0x4F20C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F282` | `0x4F284` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F292` | `0x4F294` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F296` | `0x4F298` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F29A` | `0x4F29C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F2BA` | `0x4F2BC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F2CA` | `0x4F2CC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F2CE` | `0x4F2D0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F2DE` | `0x4F2E0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F2E2` | `0x4F2E4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F2E6` | `0x4F2E8` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F30E` | `0x4F310` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F31E` | `0x4F320` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F322` | `0x4F324` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F36E` | `0x4F370` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F37E` | `0x4F380` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F382` | `0x4F384` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F386` | `0x4F388` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F38A` | `0x4F38C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F39A` | `0x4F39C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F3AA` | `0x4F3AC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F3AE` | `0x4F3B0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F3EE` | `0x4F3F2` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4F404` | `0x4F406` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0804F3FA ldr r1, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x4F412` | `0x4F414` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F44A` | `0x4F44C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F44E` | `0x4F450` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F452` | `0x4F454` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F456` | `0x4F458` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F48A` | `0x4F48C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F49A` | `0x4F49C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F4C2` | `0x4F4C4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F51A` | `0x4F51C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F51E` | `0x4F520` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F522` | `0x4F524` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F526` | `0x4F528` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F52A` | `0x4F52C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F52E` | `0x4F530` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F532` | `0x4F534` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F536` | `0x4F538` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F556` | `0x4F558` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F596` | `0x4F598` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F5E2` | `0x4F5E4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F672` | `0x4F674` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4F80E` | `0x4F810` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4F826` | `0x4F82A` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 0804F81A ldr r0, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x4F854` | `0x4F856` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4F870` | `0x4F872` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4F99C` | `0x4F99E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4FCB6` | `0x4FCB8` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FCBA` | `0x4FCBC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FCBE` | `0x4FCC0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FCC2` | `0x4FCC4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FCC6` | `0x4FCC8` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FCDA` | `0x4FCDC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FCDE` | `0x4FCE0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FD48` | `0x4FD4A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4FDB0` | `0x4FDB2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0804FDA4 ldr r0, [pc, #8] (x1) | a loaded word crosses the row boundary |
| `0x4FDCA` | `0x4FDCC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FDCE` | `0x4FDD0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FDD2` | `0x4FDD4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FDD6` | `0x4FDD8` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FDDA` | `0x4FDDC` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FDDE` | `0x4FDE0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FDE2` | `0x4FDE4` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FE14` | `0x4FE16` | 2 | 0.00 | 0.00 | 0 | 0 | pool-fragment | 0804FDFA ldr r1, [pc, #0x18] (x1) | a loaded word crosses the row boundary |
| `0x4FE4C` | `0x4FE4E` | 2 | 0.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x4FE72` | `0x4FE74` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FE76` | `0x4FE78` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FE7A` | `0x4FE7C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FE9A` | `0x4FE9C` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x4FED6` | `0x4FEDC` | 6 | 1.79 | 0.50 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x501DE` | `0x501E0` | 2 | 0.00 | 1.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x5020C` | `0x5020E` | 2 | 1.00 | 0.00 | 0 | 0 | between | 1 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x502F8` | `0x502FA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x5039C` | `0x5039E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50564` | `0x50566` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x505AC` | `0x505AE` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x5068C` | `0x5068E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x5070C` | `0x5070E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080506D8 ldr r0, [pc, #0x30] (x2) | a loaded word crosses the row boundary |
| `0x5074C` | `0x5074E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050732 ldr r0, [pc, #0x18] (x2) | a loaded word crosses the row boundary |
| `0x50820` | `0x50822` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080507E6 ldr r1, [pc, #0x38] (x2) | a loaded word crosses the row boundary |
| `0x508D4` | `0x508D6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080508C4 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x508F4` | `0x508F6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50908` | `0x5090A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080508F8 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x5094C` | `0x5094E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50960` | `0x50962` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050950 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50974` | `0x50976` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050964 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50988` | `0x5098A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050978 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x5099C` | `0x5099E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0805098C ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x509B0` | `0x509B2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080509A0 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x509C4` | `0x509C6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080509B4 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x509E4` | `0x509E6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x509F8` | `0x509FA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080509E8 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50A0C` | `0x50A0E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080509FC ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50A4C` | `0x50A4E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50A90` | `0x50A92` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50AA4` | `0x50AA6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050A94 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50AB8` | `0x50ABA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050AA8 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50AE4` | `0x50AE6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50AF8` | `0x50AFA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050AE8 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50B0C` | `0x50B0E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050AFC ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50B20` | `0x50B22` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050B10 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50B34` | `0x50B36` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050B24 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50B78` | `0x50B7A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50B8C` | `0x50B8E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050B7C ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50BA0` | `0x50BA2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050B90 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50C0E` | `0x50C12` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50C24` | `0x50C26` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050C14 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50C38` | `0x50C3A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050C28 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50C4C` | `0x50C4E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050C3C ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50C6C` | `0x50C6E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50CD6` | `0x50CDA` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 08050CB8 ldr r0, [pc, #0x1c] (x1) | a loaded word crosses the row boundary |
| `0x50D04` | `0x50D06` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50D18` | `0x50D1A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050D08 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50D2C` | `0x50D2E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050D1C ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50D58` | `0x50D5A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050D34 ldr r0, [pc, #0x20] (x1) | a loaded word crosses the row boundary |
| `0x50D6C` | `0x50D6E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050D5C ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50DD4` | `0x50DD6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50DFA` | `0x50DFE` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 08050DDC ldr r0, [pc, #0x1c] (x1) | a loaded word crosses the row boundary |
| `0x50E22` | `0x50E26` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 08050E04 ldr r0, [pc, #0x1c] (x1) | a loaded word crosses the row boundary |
| `0x50E68` | `0x50E6A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50EAC` | `0x50EAE` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50EEA` | `0x50EEE` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50F48` | `0x50F4A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x50F5C` | `0x50F5E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050F4C ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50F70` | `0x50F72` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050F60 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x50F84` | `0x50F86` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08050F74 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x5107C` | `0x5107E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x5109C` | `0x5109E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x510C2` | `0x510C6` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 080510A4 ldr r0, [pc, #0x1c] (x1) | a loaded word crosses the row boundary |
| `0x510EA` | `0x510EE` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 080510CC ldr r0, [pc, #0x1c] (x1) | a loaded word crosses the row boundary |
| `0x51118` | `0x5111A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51138` | `0x5113A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51274` | `0x51276` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x512B8` | `0x512BA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x512CC` | `0x512CE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080512BC ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x512E0` | `0x512E2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080512D0 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x5136C` | `0x5136E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51380` | `0x51382` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051370 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51394` | `0x51396` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051384 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x513B4` | `0x513B6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x513C8` | `0x513CA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080513B8 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51418` | `0x5141A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x5142C` | `0x5142E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0805141C ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51470` | `0x51472` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51484` | `0x51486` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051474 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51498` | `0x5149A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051488 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x514AC` | `0x514AE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 0805149C ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51508` | `0x5150A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x5154C` | `0x5154E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x515A8` | `0x515AA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x516A0` | `0x516A2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x516CC` | `0x516CE` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x517B8` | `0x517BA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x517DE` | `0x517E2` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 080517C0 ldr r0, [pc, #0x1c] (x1) | a loaded word crosses the row boundary |
| `0x51854` | `0x51856` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51868` | `0x5186A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051858 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x518C4` | `0x518C6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x518D8` | `0x518DA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080518C8 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x518EC` | `0x518EE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080518DC ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51900` | `0x51902` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080518F0 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51B24` | `0x51B26` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51B50` | `0x51B52` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51BDC` | `0x51BDE` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51C0C` | `0x51C0E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051BE4 ldr r0, [pc, #0x24] (x1) | a loaded word crosses the row boundary |
| `0x51C6C` | `0x51C6E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51C80` | `0x51C82` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051C70 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51C94` | `0x51C96` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051C84 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51DA4` | `0x51DA6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51EC8` | `0x51ECA` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51EDC` | `0x51EDE` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051ECC ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51EF0` | `0x51EF2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051EE0 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51F1C` | `0x51F1E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51F90` | `0x51F92` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51FBC` | `0x51FBE` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x51FD0` | `0x51FD2` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051FC0 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51FE4` | `0x51FE6` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051FD4 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x51FF8` | `0x51FFA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08051FE8 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52144` | `0x52146` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52182` | `0x52186` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52250` | `0x52252` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52264` | `0x52266` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052254 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52278` | `0x5227A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052268 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x524F4` | `0x524F6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52508` | `0x5250A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080524F8 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52534` | `0x52536` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052524 ldr r0, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52670` | `0x52672` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x526C4` | `0x526C6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x526D8` | `0x526DA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 080526C8 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52794` | `0x52796` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x527A8` | `0x527AA` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052798 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x527D4` | `0x527D6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52830` | `0x52832` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x5285C` | `0x5285E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052838 ldr r0, [pc, #0x20] (x1) | a loaded word crosses the row boundary |
| `0x52870` | `0x52872` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052860 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52884` | `0x52886` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052874 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52A0C` | `0x52A0E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52A20` | `0x52A22` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052A10 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52AF0` | `0x52AF2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52B1C` | `0x52B1E` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52B58` | `0x52B5A` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052B24 ldr r0, [pc, #0x30] (x1) | a loaded word crosses the row boundary |
| `0x52CE4` | `0x52CE6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52D10` | `0x52D12` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052D00 ldr r0, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52DF0` | `0x52DF2` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52E1C` | `0x52E1E` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052E0C ldr r0, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52E30` | `0x52E32` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052E20 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52E44` | `0x52E46` | 2 | 1.00 | 0.00 | 0 | 0 | pool-fragment | 08052E34 ldr r2, [pc, #0xc] (x1) | a loaded word crosses the row boundary |
| `0x52E70` | `0x52E72` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52EC4` | `0x52EC6` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x52ECE` | `0x52ED2` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 08052EC8 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x52EDA` | `0x52EDE` | 4 | 1.50 | 0.50 | 1 | 0 | pool-fragment | 08052ED4 ldr r1, [pc, #4] (x1) | a loaded word crosses the row boundary |
| `0x530EC` | `0x530EE` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x53178` | `0x5317A` | 2 | 1.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x53336` | `0x53338` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x53338` | `0x533C4` | 140 | 5.39 | 0.09 | 35 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x533C4` | `0x5349C` | 216 | 5.18 | 0.08 | 54 | 0 | unreached | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x5349C` | `0x534A0` | 4 | 2.00 | 0.00 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x539DA` | `0x539DC` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x539DC` | `0x53A0C` | 48 | 3.88 | 0.25 | 12 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x53A0C` | `0x53A1C` | 16 | 3.75 | 0.12 | 4 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x53FC0` | `0x53FC2` | 2 | 0.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x53FD0` | `0x53FD4` | 4 | 0.81 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x5440E` | `0x54412` | 4 | 0.81 | 0.75 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x5460E` | `0x54612` | 4 | 1.50 | 0.50 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x54712` | `0x54714` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x54714` | `0x5477C` | 104 | 5.13 | 0.14 | 26 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x549A4` | `0x549A6` | 2 | 0.00 | 0.00 | 0 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x54A18` | `0x54A1C` | 4 | 2.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x54CFC` | `0x54D00` | 4 | 2.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x54F04` | `0x54F08` | 4 | 2.00 | 0.00 | 1 | 0 | between | none | between transcribed code rows and no instruction reads it |
| `0x6D4E0` | `0x6D586` | 166 | 3.37 | 0.39 | 41 | 0 | unreached | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6D586` | `0x6D928` | 930 | 4.70 | 0.24 | 232 | 16 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x6D928` | `0x6D92A` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x6D92A` | `0x6E050` | 1830 | 2.83 | 0.52 | 457 | 40 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x6E050` | `0x6E0FC` | 172 | 3.48 | 0.42 | 43 | 1 | unreached | 12 naming word(s) | named by a word; a name is not a consumer |
| `0x6E0FC` | `0x6E55C` | 1120 | 4.99 | 0.25 | 280 | 29 | unreached | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6E55C` | `0x6E55E` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x6E55E` | `0x6EE6C` | 2318 | 3.37 | 0.49 | 579 | 63 | unreached | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6EE6C` | `0x6F58A` | 1822 | 2.38 | 0.71 | 455 | 3 | unreached | 14 naming word(s) | named by a word; a name is not a consumer |
| `0x6F58A` | `0x6F5A6` | 28 | 3.37 | 0.00 | 7 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x6F5A6` | `0x6F896` | 752 | 4.95 | 0.23 | 188 | 8 | unreached | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6F896` | `0x6F94E` | 184 | 3.45 | 0.31 | 46 | 3 | unreached | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6F94E` | `0x6F950` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x6F950` | `0x6FE18` | 1224 | 2.33 | 0.65 | 306 | 15 | unreached | 6 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE18` | `0x6FE1A` | 2 | 1.00 | 0.50 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x7012C` | `0x70130` | 4 | 2.00 | 0.25 | 1 | 1 | between | 28 naming word(s) | between transcribed code rows and no instruction reads it |
| `0x7014A` | `0x701EC` | 162 | 4.14 | 0.27 | 40 | 0 | named-data | 0000630C ldr [pc] 0x00659C = 0x0807014C | code loads a word naming this row; its bytes have no layout |
| `0x701FA` | `0x701FB` | 1 | 0.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x701FB` | `0x701FC` | 1 | 0.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x701FC` | `0x707DB` | 1503 | 4.86 | 0.10 | 375 | 0 | pool-partial | 0807000C ldr r0, [pc, #0x200] (x1) | code loads a word naming this row; its bytes have no layout |
| `0x707DB` | `0x707E8` | 13 | 2.66 | 0.23 | 3 | 0 | named-data | 000076B8 ldr [pc] 0x0076EC = 0x080707DC | code loads a word naming this row; its bytes have no layout |
| `0x707E8` | `0x707EC` | 4 | 2.00 | 0.25 | 1 | 0 | named-data | 000077F8 ldr [pc] 0x007854 = 0x080707E8 | code loads a word naming this row; its bytes have no layout |
| `0x707EC` | `0x707F0` | 4 | 2.00 | 0.25 | 1 | 0 | named-data | 00007882 ldr [pc] 0x007978 = 0x080707EC | code loads a word naming this row; its bytes have no layout |
| `0x707FC` | `0x70800` | 4 | 2.00 | 0.25 | 1 | 1 | unreached | 226 naming word(s) | named by a word; a name is not a consumer |
| `0x70800` | `0x70804` | 4 | 0.81 | 0.75 | 1 | 0 | named-data | 00007E94 ldr [pc] 0x008094 = 0x08070800 | code loads a word naming this row; its bytes have no layout |
| `0x70804` | `0x71008` | 2052 | 0.01 | 1.00 | 513 | 0 | named-data | 00007BA8 ldr [pc] 0x007E6C = 0x08070808 | code loads a word naming this row; its bytes have no layout |
| `0x71008` | `0x716A0` | 1688 | 2.40 | 0.75 | 422 | 0 | named-data | 00007C16 ldr [pc] 0x007E74 = 0x08071008 | code loads a word naming this row; its bytes have no layout |
| `0x716A8` | `0x716AC` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x716AC` | `0x716B0` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x716B0` | `0x716B4` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x716C0` | `0x716C4` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x716C4` | `0x716C8` | 4 | 2.00 | 0.25 | 1 | 0 | named-data | 000093B4 ldr [pc] 0x00964C = 0x080716C4 | code loads a word naming this row; its bytes have no layout |
| `0x716C8` | `0x716CC` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x716CC` | `0x716D0` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x716D0` | `0x716D4` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x716D4` | `0x716D8` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x716D8` | `0x716DA` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x716DA` | `0x716DC` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x716DC` | `0x716DE` | 2 | 1.00 | 0.00 | 0 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x716DE` | `0x71720` | 66 | 3.63 | 0.33 | 16 | 0 | named-data | 00009F06 ldr [pc] 0x00A018 = 0x080716E8 | code loads a word naming this row; its bytes have no layout |
| `0x71720` | `0x71724` | 4 | 1.50 | 0.50 | 1 | 0 | named-data | 0000AE9E ldr [pc] 0x00B09C = 0x08071720 | code loads a word naming this row; its bytes have no layout |
| `0x71724` | `0x71728` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x71728` | `0x7172C` | 4 | 2.00 | 0.25 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x7172C` | `0x71730` | 4 | 2.00 | 0.00 | 1 | 1 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x71730` | `0x71734` | 4 | 0.81 | 0.75 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x71734` | `0x71738` | 4 | 0.81 | 0.75 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x71738` | `0x7173C` | 4 | 0.81 | 0.75 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x7173C` | `0x71740` | 4 | 0.81 | 0.75 | 1 | 0 | unreached | none | no decoded reader and no naming word at half-open bounds |
| `0x71740` | `0x71758` | 24 | 2.63 | 0.50 | 6 | 2 | unreached | none | no decoded reader and no naming word at half-open bounds |

## Sweep read verdict (generated: docs/research/REGION_READS.csv)

One line per raw row of `R32`, from `tools/research/region_readers.py`.
The 9 `code-without-entry` row(s) of those regions carry their null in
`docs/research/CODE_FRAGMENT_NULL_CENSUS.md`, which is the class's census.
The offsets are the byte offsets inside the row that the sweep's reads used, and the
share is the part of the row those reads reached. The null above each row stays its
measured null; this line is the read verdict on it.

| start | end | bytes | region | class | verdict |
|---|---|---|---|---|---|
| `0x1D0` | `0x1D2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3C0` | `0x3C2` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0800015E ldr r1, [pc, #0x260]`; 1 offset(s) of 1 word(s), 1.00 of the row, 193760 read(s) |
| `0x3FC` | `0x45E` | 98 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x660` | `0x662` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xB1C` | `0xB40` | 36 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x10F0` | `0x10F2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x10FC` | `0x10FE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x17D8` | `0x1808` | 48 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1B6C` | `0x1B82` | 22 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1EBC` | `0x1EBE` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08001CF4 ldr r1, [pc, #0x1c4]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1 read(s) |
| `0x25E0` | `0x25E2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x26B4` | `0x26B6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2720` | `0x273A` | 26 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2990` | `0x2992` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x29C0` | `0x29C2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x29D8` | `0x2A12` | 58 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2C2A` | `0x2C58` | 46 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3310` | `0x3348` | 56 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3352` | `0x3354` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3354` | `0x3358` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3718` | `0x371A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3986` | `0x399E` | 24 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x39D4` | `0x39D6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3A74` | `0x3B12` | 158 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3C44` | `0x3C46` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3C6C` | `0x3C6E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3C8A` | `0x3CAC` | 34 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3CF6` | `0x3D10` | 26 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3D38` | `0x3D3A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3F40` | `0x3F42` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08003CCA ldr r2, [pc, #0x274]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1747 read(s) |
| `0x3FEE` | `0x3FF8` | 10 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4092` | `0x4094` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4094` | `0x4098` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4156` | `0x4212` | 188 | `R32` | `text/tables` | read by 6 pc(s): field load `0800403A ldr r3, [pc, #0x11c]`; field load `08004052 ldr r5, [pc, #0x104]`; field load `0800405E ldr r7, [pc, #0xfc]`; 2 offset(s) of 47 word(s), 0.04 of the row, 4848 read(s) |
| `0x45C2` | `0x45C4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x45C4` | `0x45C8` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4810` | `0x4812` | 2 | `R32` | `unknown` | read by 2 pc(s): field load `08004774 ldr r0, [pc, #0x98]`; field load `080047A4 ldr r5, [pc, #0x68]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1599 read(s) |
| `0x4AE4` | `0x4AE6` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4DEC` | `0x4DEE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x524E` | `0x5250` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5AD4` | `0x5BC0` | 236 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x5BFC` | `0x5BFE` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x5C40` | `0x5C44` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5C6E` | `0x5E36` | 456 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x5FA0` | `0x5FA2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x6092` | `0x6094` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x6094` | `0x6098` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x628C` | `0x628E` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x649E` | `0x64A0` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x686C` | `0x686E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x6AA8` | `0x6AAA` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x6B94` | `0x6B96` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x6BCC` | `0x6BCE` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08006BA2 ldr r4, [pc, #0x28]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1494 read(s) |
| `0x6E18` | `0x6E1A` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08006DC6 ldr r0, [pc, #0x50]`; 1 offset(s) of 1 word(s), 1.00 of the row, 452 read(s) |
| `0x6E38` | `0x6E3A` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08006E28 ldr r0, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1270 read(s) |
| `0x6FF4` | `0x6FFA` | 6 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x7052` | `0x7054` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x7054` | `0x7056` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x7164` | `0x7166` | 2 | `R32` | `text/tables` | read by 3 pc(s): field load `0800707C ldr r4, [pc, #0xe4]`; field load `08007116 ldr r0, [pc, #0x4c]`; field load `08007124 ldr r0, [pc, #0x3c]`; 1 offset(s) of 1 word(s), 1.00 of the row, 57970 read(s) |
| `0x71A6` | `0x71AA` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x71BC` | `0x71BE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x73B6` | `0x73B8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x73BC` | `0x73BE` | 2 | `R32` | `unknown` | read by 1 pc(s): field load `0800734C ldr r0, [pc, #0x6c]`; 1 offset(s) of 1 word(s), 1.00 of the row, 13 read(s) |
| `0x74BA` | `0x74BC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x74C0` | `0x74C2` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x770C` | `0x7710` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x774E` | `0x7752` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x7764` | `0x7766` | 2 | `R32` | `text/tables` | read by 4 pc(s): field load `0800774E ldr r0, [pc, #0x14]`; field load `08007752 ldr r0, [pc, #0x10]`; field load `08007758 ldr r0, [pc, #8]`; 1 offset(s) of 1 word(s), 1.00 of the row, 42 read(s) |
| `0x7770` | `0x7774` | 4 | `R32` | `unknown` | read by 1 pc(s): field load `0800776C ldr r0, [pc, #0]`; 1 offset(s) of 1 word(s), 1.00 of the row, 853 read(s) |
| `0x77DE` | `0x77E2` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x7854` | `0x7856` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `080077F8 ldr r0, [pc, #0x58]`; 1 offset(s) of 1 word(s), 1.00 of the row, 169882 read(s) |
| `0x7A18` | `0x7A1A` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x7A1A` | `0x7A1E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x7A56` | `0x7A5A` | 4 | `R32` | `text/tables` | read by 1 pc(s): field load `08007A2C ldr r1, [pc, #0x28]`; 1 offset(s) of 1 word(s), 0.50 of the row, 250 read(s) |
| `0x7B62` | `0x7B76` | 20 | `R32` | `text/tables` | read by 3 pc(s): field load `08007A6C ldr r0, [pc, #0xfc]`; field load `08007A7C ldr r0, [pc, #0xf0]`; field load `08007ACA ldr r1, [pc, #0xa8]`; 3 offset(s) of 5 word(s), 0.20 of the row, 330 read(s) |
| `0x7D5C` | `0x7D5E` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x7D5E` | `0x7D62` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x8094` | `0x8096` | 2 | `R32` | `text/tables` | read by 2 pc(s): field load `08007E94 ldr r2, [pc, #0x1fc]`; field load `08007F3E ldr r2, [pc, #0x154]`; 1 offset(s) of 1 word(s), 1.00 of the row, 590910 read(s) |
| `0x8486` | `0x84A6` | 32 | `R32` | `unknown` | read by 9 pc(s): field load `080080A8 ldr r1, [pc, #0x3dc]`; field load `080080B4 ldr r4, [pc, #0x3d4]`; field load `080080C8 ldr r0, [pc, #0x3c4]`; 7 offset(s) of 8 word(s), 0.62 of the row, 70949 read(s) |
| `0x86B2` | `0x86B4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x86B4` | `0x86B8` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x8A58` | `0x8AA0` | 72 | `R32` | `text/tables` | read by 1 pc(s): field load `08008A0A ldr r1, [pc, #0x4c]`; 1 offset(s) of 18 word(s), 0.06 of the row, 453 read(s) |
| `0x9018` | `0x9022` | 10 | `R32` | `pointer-tables` | read by 3 pc(s): field load `08008D80 ldr r7, [pc, #0x294]`; field load `08008D98 ldr r1, [pc, #0x280]`; field load `08008DC8 ldr r1, [pc, #0x254]`; 3 offset(s) of 2 word(s), 1.00 of the row, 905 read(s) |
| `0x91FC` | `0x91FE` | 2 | `R32` | `text/tables` | read by 3 pc(s): field load `08009072 ldr r7, [pc, #0x188]`; field load `080090B2 ldr r7, [pc, #0x148]`; field load `080091A2 ldr r4, [pc, #0x58]`; 1 offset(s) of 1 word(s), 1.00 of the row, 3 read(s) |
| `0x9648` | `0x964A` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `080093A8 ldr r0, [pc, #0x29c]`; 1 offset(s) of 1 word(s), 1.00 of the row, 452 read(s) |
| `0x98F8` | `0x98FA` | 2 | `R32` | `unknown` | read by 2 pc(s): field load `0800965E ldr r4, [pc, #0x298]`; field load `08009674 ldr r0, [pc, #0x280]`; 1 offset(s) of 1 word(s), 1.00 of the row, 171416 read(s) |
| `0x9AD8` | `0x9ADA` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `080099A8 ldr r0, [pc, #0x12c]`; 1 offset(s) of 1 word(s), 1.00 of the row, 490843 read(s) |
| `0x9B4C` | `0x9B80` | 52 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xA208` | `0xA20A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xA20C` | `0xA20E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xA210` | `0xA212` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0800A1CC ldr r0, [pc, #0x40]`; 1 offset(s) of 1 word(s), 1.00 of the row, 46 read(s) |
| `0xA214` | `0xA216` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0800A1F2 ldr r0, [pc, #0x20]`; 1 offset(s) of 1 word(s), 1.00 of the row, 5 read(s) |
| `0xA26E` | `0xA272` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0xA418` | `0xA41A` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0xA41A` | `0xA41E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xA4E0` | `0xA4E2` | 2 | `R32` | `unknown` | read by 1 pc(s): field load `0800A27C ldr r0, [pc, #0x260]`; 1 offset(s) of 1 word(s), 1.00 of the row, 59 read(s) |
| `0xA520` | `0xA522` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0xA522` | `0xA526` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xA78C` | `0xA78E` | 2 | `R32` | `unknown` | read by 3 pc(s): field load `0800A516 ldr r1, [pc, #0x274]`; field load `0800A560 ldr r0, [pc, #0x228]`; field load `0800A5AC ldr r1, [pc, #0x1dc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 370 read(s) |
| `0xA79C` | `0xA79E` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0800A784 ldr r0, [pc, #0x14]`; 1 offset(s) of 1 word(s), 1.00 of the row, 10 read(s) |
| `0xA938` | `0xA93A` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0800A906 ldr r1, [pc, #0x30]`; 1 offset(s) of 1 word(s), 1.00 of the row, 7 read(s) |
| `0xA9B0` | `0xA9B8` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0xAB50` | `0xAB52` | 2 | `R32` | `text/tables` | read by 2 pc(s): field load `0800AA50 ldr r1, [pc, #0xfc]`; field load `0800AAA8 ldr r1, [pc, #0xa4]`; 1 offset(s) of 1 word(s), 1.00 of the row, 7091 read(s) |
| `0xAD7A` | `0xAD82` | 8 | `R32` | `unknown` | read by 8 pc(s): field load `0800AB66 ldr r1, [pc, #0x214]`; field load `0800AB7C ldr r1, [pc, #0x200]`; field load `0800ABAE ldr r2, [pc, #0x1cc]`; 2 offset(s) of 2 word(s), 0.75 of the row, 3373 read(s) |
| `0xB096` | `0xB0A8` | 18 | `R32` | `unknown` | read by 3 pc(s): field load `0800ADAA ldr r2, [pc, #0x2ec]`; field load `0800ADC8 ldr r1, [pc, #0x2cc]`; field load `0800ADE2 ldr r1, [pc, #0x2b4]`; 1 offset(s) of 4 word(s), 0.22 of the row, 3687 read(s) |
| `0xB328` | `0xB32A` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0800B2B6 ldr r0, [pc, #0x70]`; 1 offset(s) of 1 word(s), 1.00 of the row, 6 read(s) |
| `0xBC46` | `0xBC5A` | 20 | `R32` | `unknown` | read by 12 pc(s): field load `0800B868 ldr r0, [pc, #0x3dc]`; field load `0800B86E ldr r5, [pc, #0x3dc]`; field load `0800B892 ldr r0, [pc, #0x3bc]`; 5 offset(s) of 5 word(s), 0.60 of the row, 175601 read(s) |
| `0xBE70` | `0xBE72` | 2 | `R32` | `text/tables` | read by 2 pc(s): field load `0800BC96 ldr r1, [pc, #0x1d8]`; field load `0800BCCA ldr r6, [pc, #0x1a4]`; 1 offset(s) of 1 word(s), 1.00 of the row, 173087 read(s) |
| `0xC274` | `0xC276` | 2 | `R32` | `unknown` | read by 1 pc(s): field load `0800C0DC ldr r0, [pc, #0x194]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1 read(s) |
| `0xC42C` | `0xC42E` | 2 | `R32` | `unknown` | read by 1 pc(s): field load `0800C2B0 ldr r1, [pc, #0x178]`; 1 offset(s) of 1 word(s), 1.00 of the row, 28 read(s) |
| `0xC588` | `0xC58A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xC58A` | `0xC58E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xCB00` | `0xCB02` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0xCB02` | `0xCB06` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xCDD8` | `0xCDE2` | 10 | `R32` | `unknown` | read by 2 pc(s): field load `0800CD1C ldr r1, [pc, #0xbc]`; field load `0800CDA0 ldr r1, [pc, #0x3c]`; 2 offset(s) of 2 word(s), 0.60 of the row, 94 read(s) |
| `0xCEE4` | `0xCEF2` | 14 | `R32` | `unknown` | read by 2 pc(s): field load `0800CE3C ldr r0, [pc, #0xac]`; field load `0800CE46 ldr r0, [pc, #0xa0]`; 2 offset(s) of 3 word(s), 0.57 of the row, 2 read(s) |
| `0xD1A8` | `0xD1B2` | 10 | `R32` | `unknown` | read by 3 pc(s): field load `0800CF9A ldr r5, [pc, #0x20c]`; field load `0800D042 ldr r1, [pc, #0x168]`; field load `0800D0F6 ldr r1, [pc, #0xb8]`; 3 offset(s) of 2 word(s), 1.00 of the row, 95646 read(s) |
| `0xD1B4` | `0xD1B6` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0800D0F4 ldr r0, [pc, #0xbc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 667 read(s) |
| `0xD518` | `0xD538` | 32 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0xD646` | `0xD648` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xD650` | `0xD652` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xD876` | `0xD892` | 28 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0xDE14` | `0xDE16` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0xDE16` | `0xDE1A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xE74C` | `0xE74E` | 2 | `R32` | `text/tables` | read by 2 pc(s): field load `0800E6E2 ldr r0, [pc, #0x68]`; field load `0800E6FC ldr r0, [pc, #0x4c]`; 1 offset(s) of 1 word(s), 1.00 of the row, 904 read(s) |
| `0xEB34` | `0xEB36` | 2 | `R32` | `text/tables` | read by 3 pc(s): field load `0800E784 ldr r0, [pc, #0x3ac]`; field load `0800E826 ldr r0, [pc, #0x30c]`; field load `0800E862 ldr r0, [pc, #0x2d0]`; 1 offset(s) of 1 word(s), 1.00 of the row, 2912 read(s) |
| `0xF1E8` | `0xF1F8` | 16 | `R32` | `unknown` | read by 6 pc(s): field load `0800EE6C ldr r1, [pc, #0x378]`; field load `0800EEB0 ldr r3, [pc, #0x334]`; field load `0800EF96 ldr r3, [pc, #0x254]`; 4 offset(s) of 4 word(s), 0.75 of the row, 1612888 read(s) |
| `0xF4B0` | `0xF4B2` | 2 | `R32` | `unknown` | read by 3 pc(s): field load `0800F216 ldr r3, [pc, #0x298]`; field load `0800F26C ldr r3, [pc, #0x240]`; field load `0800F322 ldr r3, [pc, #0x18c]`; 1 offset(s) of 1 word(s), 1.00 of the row, 721115 read(s) |
| `0xF4B2` | `0xF4B6` | 4 | `R32` | `text/tables` | read by 1 pc(s): field load `0800F3FE ldr r2, [pc, #0xb4]`; 1 offset(s) of 1 word(s), 0.50 of the row, 22080 read(s) |
| `0xF584` | `0xF586` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0xF624` | `0xF62C` | 8 | `R32` | `pointer-tables` | read by 2 pc(s): field load `0800F5BC ldr r1, [pc, #0x64]`; field load `0800F60E ldr r2, [pc, #0x18]`; 2 offset(s) of 2 word(s), 1.00 of the row, 1336 read(s) |
| `0x10008` | `0x1000A` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0800FDA0 ldr r0, [pc, #0x264]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1303 read(s) |
| `0x10448` | `0x1044A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x10576` | `0x10582` | 12 | `R32` | `pointer-tables` | read by 4 pc(s): field load `080103A8 ldr r2, [pc, #0x1cc]`; field load `080103EC ldr r2, [pc, #0x188]`; field load `08010466 ldr r6, [pc, #0x114]`; 3 offset(s) of 3 word(s), 0.67 of the row, 761 read(s) |
| `0x107E4` | `0x107E6` | 2 | `R32` | `text/tables` | read by 2 pc(s): field load `08010588 ldr r0, [pc, #0x258]`; field load `08010724 ldr r7, [pc, #0xbc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 13 read(s) |
| `0x10DD8` | `0x10DDA` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x10DDA` | `0x10DDE` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x10F26` | `0x10F40` | 26 | `R32` | `unknown` | read by 8 pc(s): field load `08010B84 ldr r0, [pc, #0x3a0]`; field load `08010B88 ldr r1, [pc, #0x3a0]`; field load `08010BFC ldr r0, [pc, #0x32c]`; 5 offset(s) of 6 word(s), 0.54 of the row, 31268 read(s) |
| `0x10FFC` | `0x11014` | 24 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x110D0` | `0x110D2` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x110D2` | `0x110D6` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x11552` | `0x1155A` | 8 | `R32` | `unknown` | read by 7 pc(s): field load `08011204 ldr r3, [pc, #0x34c]`; field load `08011258 ldr r1, [pc, #0x2fc]`; field load `0801125C ldr r2, [pc, #0x2f4]`; 2 offset(s) of 2 word(s), 0.75 of the row, 16530 read(s) |
| `0x11DA4` | `0x11DA6` | 2 | `R32` | `text/tables` | read by 4 pc(s): field load `08011B2C ldr r0, [pc, #0x274]`; field load `08011C40 ldr r0, [pc, #0x160]`; field load `08011CA0 ldr r0, [pc, #0x100]`; 1 offset(s) of 1 word(s), 1.00 of the row, 3543 read(s) |
| `0x1218C` | `0x1218E` | 2 | `R32` | `unknown` | read by 10 pc(s): field load `08012038 ldr r0, [pc, #0x150]`; field load `08012042 ldr r0, [pc, #0x148]`; field load `08012052 ldr r0, [pc, #0x138]`; 1 offset(s) of 1 word(s), 1.00 of the row, 58 read(s) |
| `0x123C4` | `0x123DE` | 26 | `R32` | `unknown` | read by 3 pc(s): field load `08012242 ldr r1, [pc, #0x188]`; field load `0801228A ldr r0, [pc, #0x138]`; field load `080122AC ldr r0, [pc, #0x120]`; 3 offset(s) of 6 word(s), 0.46 of the row, 18 read(s) |
| `0x125D0` | `0x125D2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x128F4` | `0x128F6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x128FA` | `0x128FE` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x12B58` | `0x12B5A` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x12B5A` | `0x12B5E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x12D0A` | `0x12D0C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x12D0C` | `0x12D10` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x12FA4` | `0x12FA6` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x12FA6` | `0x12FAA` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x13072` | `0x13074` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x131B4` | `0x131B6` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x131B6` | `0x131BA` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x13908` | `0x1390A` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08013646 ldr r6, [pc, #0x2c0]`; 1 offset(s) of 1 word(s), 1.00 of the row, 169604 read(s) |
| `0x13B94` | `0x13B96` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x13B96` | `0x13B9A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x13E20` | `0x13E22` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x13FBE` | `0x13FC0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x13FC0` | `0x13FC4` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1411C` | `0x1411E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x14180` | `0x14182` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x153F2` | `0x15470` | 126 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x15470` | `0x15472` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x15998` | `0x1599A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x159C2` | `0x159C4` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x159CA` | `0x159CC` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x15A24` | `0x15A26` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x15A94` | `0x15A96` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x15E80` | `0x15E94` | 20 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x16300` | `0x16302` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x16714` | `0x16718` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x16748` | `0x1674A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1678C` | `0x1678E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x16996` | `0x16998` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x16998` | `0x1699C` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x16A92` | `0x16AA8` | 22 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x16B66` | `0x16C58` | 242 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x16CCC` | `0x16CCE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1710C` | `0x1710E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x174FE` | `0x17500` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x175A0` | `0x175C8` | 40 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x17694` | `0x17696` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x178C0` | `0x178C2` | 2 | `R32` | `unknown` | read by 1 pc(s): field load `080176B0 ldr r0, [pc, #0x20c]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1 read(s) |
| `0x17964` | `0x17966` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x17966` | `0x1796A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x179E6` | `0x179EA` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x17BDA` | `0x17BE0` | 6 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x17BE4` | `0x17BE8` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x17BEC` | `0x17BF2` | 6 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x18392` | `0x18394` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x18786` | `0x187A2` | 28 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x187A2` | `0x187A6` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x18836` | `0x1883A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x18BE0` | `0x18BE2` | 2 | `R32` | `text/tables` | read by 2 pc(s): field load `08018A4A ldr r2, [pc, #0x194]`; field load `08018BB2 ldr r0, [pc, #0x2c]`; 1 offset(s) of 1 word(s), 1.00 of the row, 3 read(s) |
| `0x18E5E` | `0x18E62` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1906C` | `0x1906E` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08018FAA ldr r0, [pc, #0xc0]`; 1 offset(s) of 1 word(s), 1.00 of the row, 6107 read(s) |
| `0x19268` | `0x1926C` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x192AC` | `0x192AE` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08019288 ldr r2, [pc, #0x20]`; 1 offset(s) of 1 word(s), 1.00 of the row, 5497 read(s) |
| `0x195A4` | `0x195A6` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1987A` | `0x1987C` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1987C` | `0x1987E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x19D0C` | `0x19D1E` | 18 | `R32` | `pointer-tables` | read by 5 pc(s): field load `08019B08 ldr r0, [pc, #0x200]`; field load `08019B0A ldr r6, [pc, #0x204]`; field load `08019B30 ldr r0, [pc, #0x1e0]`; 4 offset(s) of 4 word(s), 0.67 of the row, 8037 read(s) |
| `0x19D1E` | `0x19D22` | 4 | `R32` | `text/tables` | read by 1 pc(s): field load `08019CB8 ldr r3, [pc, #0x64]`; 1 offset(s) of 1 word(s), 0.50 of the row, 178 read(s) |
| `0x19D28` | `0x19D2A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1A23A` | `0x1A2AA` | 112 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1A30E` | `0x1A322` | 20 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x1A354` | `0x1A356` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1A356` | `0x1A35A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1A3B0` | `0x1A3B2` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1A3B2` | `0x1A3B6` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1A3EC` | `0x1A3F2` | 6 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1C6A4` | `0x1C6C6` | 34 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1CB32` | `0x1CB34` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1CB34` | `0x1CB38` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1CB7C` | `0x1CB86` | 10 | `R32` | `pointer-tables` | read by 3 pc(s): field load `0801C9DE ldr r0, [pc, #0x1a4]`; field load `0801CA4E ldr r2, [pc, #0x130]`; field load `0801CA82 ldr r6, [pc, #0x100]`; 2 offset(s) of 2 word(s), 0.60 of the row, 106 read(s) |
| `0x1D046` | `0x1D04A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1D08C` | `0x1D08E` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0801D006 ldr r0, [pc, #0x84]`; 1 offset(s) of 1 word(s), 1.00 of the row, 17599 read(s) |
| `0x1D0A0` | `0x1D0A6` | 6 | `R32` | `text/tables` | read by 1 pc(s): field load `0801D09C ldr r0, [pc, #4]`; 1 offset(s) of 1 word(s), 0.33 of the row, 3553 read(s) |
| `0x1D762` | `0x1D790` | 46 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1D958` | `0x1D95A` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1DCE8` | `0x1DD72` | 138 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1DDA2` | `0x1DDEC` | 74 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1DDEE` | `0x1DF7E` | 400 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1DFA0` | `0x1DFA2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1E13E` | `0x1E142` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1E9DE` | `0x1E9E2` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1EAC2` | `0x1EAC6` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1ECBC` | `0x1ECBE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1F05E` | `0x1F06A` | 12 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x1F220` | `0x1F22A` | 10 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1F346` | `0x1F364` | 30 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1F790` | `0x1F792` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1F792` | `0x1F796` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1F7AE` | `0x1F7B0` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1F7B0` | `0x1F7B2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x1FB38` | `0x1FB3A` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x1FF40` | `0x1FF4E` | 14 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x1FF94` | `0x1FF96` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x20530` | `0x2054A` | 26 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x2065E` | `0x20660` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x20668` | `0x2066A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2079C` | `0x2079E` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2079E` | `0x207A2` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x20A76` | `0x20A7C` | 6 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x20A94` | `0x20AA4` | 16 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x20DA0` | `0x20DAC` | 12 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x20EEA` | `0x20EEC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x20EEC` | `0x20EF0` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x21052` | `0x2105A` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2105A` | `0x2105C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x21166` | `0x2116E` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2125E` | `0x2126A` | 12 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x2127C` | `0x2127E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x21728` | `0x2172A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x21730` | `0x21732` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2173C` | `0x2173E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x21828` | `0x21832` | 10 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x21832` | `0x21834` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x21870` | `0x21872` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x21BB4` | `0x21BB6` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x220C2` | `0x220D8` | 22 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x22626` | `0x2262A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2266E` | `0x22672` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x22674` | `0x22676` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x228FA` | `0x228FC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x22900` | `0x22902` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x23088` | `0x2309C` | 20 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2312A` | `0x2312C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2312C` | `0x23130` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x23482` | `0x23484` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x23490` | `0x234DC` | 76 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x237BC` | `0x237BE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x237C4` | `0x237C6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x23838` | `0x2383A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x23840` | `0x23842` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x23B2A` | `0x23B50` | 38 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x23B52` | `0x23C1C` | 202 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x23C58` | `0x23C5A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x23C5A` | `0x23C5E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x23C7C` | `0x23CB8` | 60 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x23EE0` | `0x23EE2` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x23EE2` | `0x23EE6` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x23F84` | `0x23F86` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x23F86` | `0x23F8A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x242D6` | `0x242E2` | 12 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x2435C` | `0x2435E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x243E6` | `0x243E8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x243E8` | `0x243EC` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x244DA` | `0x244EC` | 18 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x24556` | `0x2455E` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x24666` | `0x246A2` | 60 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x24976` | `0x24978` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x24D44` | `0x24D94` | 80 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x24E40` | `0x24E42` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x25288` | `0x2528A` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2528A` | `0x2528E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x255A8` | `0x255AA` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x255AA` | `0x255AE` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x25AD4` | `0x25ADC` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x25AE4` | `0x25AF0` | 12 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x25AF8` | `0x25AFA` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x25DF0` | `0x25DF2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x25E4C` | `0x25E4E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x26044` | `0x26048` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x263BA` | `0x263BE` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x264D0` | `0x264D2` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `080264CC ldr r0, [pc, #0]`; 1 offset(s) of 1 word(s), 1.00 of the row, 21 read(s) |
| `0x26582` | `0x26584` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x26584` | `0x26588` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x266D2` | `0x266D4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x266D4` | `0x266D8` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x26802` | `0x26804` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x26804` | `0x26808` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x26B2C` | `0x26B32` | 6 | `R32` | `text/tables` | read by 1 pc(s): field load `08026ADA ldr r1, [pc, #0x54]`; 1 offset(s) of 1 word(s), 0.33 of the row, 4 read(s) |
| `0x271AC` | `0x271AE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2737A` | `0x2737C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2737C` | `0x27380` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x27692` | `0x2769E` | 12 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x278DE` | `0x278E2` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x27926` | `0x27932` | 12 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x27B8C` | `0x27B8E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x27B96` | `0x27B98` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x27D90` | `0x27D92` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x27D92` | `0x27D96` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x27E40` | `0x27E42` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x284B6` | `0x284B8` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x286B6` | `0x286B8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x286BC` | `0x286D2` | 22 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x289BA` | `0x289DE` | 36 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x28BFA` | `0x28C02` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x28C02` | `0x28C04` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x28EBA` | `0x28EBC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2900A` | `0x2900E` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x292D8` | `0x292E0` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x295BC` | `0x295BE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x296AE` | `0x296B2` | 4 | `R32` | `text/tables` | read by 1 pc(s): field load `0802969A ldr r1, [pc, #0x14]`; 1 offset(s) of 1 word(s), 0.50 of the row, 18 read(s) |
| `0x2995E` | `0x29962` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x299A2` | `0x299A6` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x299BA` | `0x299BC` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x299BC` | `0x299BE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x299D8` | `0x299DA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x29BD4` | `0x29BD6` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08029B5A ldr r0, [pc, #0x78]`; 1 offset(s) of 1 word(s), 1.00 of the row, 7322 read(s) |
| `0x29BDC` | `0x29BDE` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08029BCC ldr r1, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 395 read(s) |
| `0x29ED4` | `0x29ED6` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08029EC0 ldr r0, [pc, #0x10]`; 1 offset(s) of 1 word(s), 1.00 of the row, 4 read(s) |
| `0x2A004` | `0x2A006` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08029EDA ldr r0, [pc, #0x128]`; 1 offset(s) of 1 word(s), 1.00 of the row, 8555 read(s) |
| `0x2A09A` | `0x2A09E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2A236` | `0x2A238` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2A238` | `0x2A23C` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2A580` | `0x2A5A2` | 34 | `R32` | `unknown` | read by 1 pc(s): field load `0802A404 ldr r6, [pc, #0x17c]`; 1 offset(s) of 8 word(s), 0.12 of the row, 2 read(s) |
| `0x2A7AC` | `0x2A7B2` | 6 | `R32` | `unknown` | read by 6 pc(s): field load `0802A5C2 ldr r1, [pc, #0x1e8]`; field load `0802A614 ldr r7, [pc, #0x194]`; field load `0802A626 ldr r7, [pc, #0x184]`; 2 offset(s) of 1 word(s), 1.00 of the row, 20 read(s) |
| `0x2A7B2` | `0x2A7B4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2A9F8` | `0x2AA06` | 14 | `R32` | `pointer-tables` | read by 6 pc(s): field load `0802A83A ldr r0, [pc, #0x1bc]`; field load `0802A840 ldr r0, [pc, #0x1b8]`; field load `0802A864 ldr r0, [pc, #0x198]`; 4 offset(s) of 3 word(s), 0.86 of the row, 3175 read(s) |
| `0x2AA06` | `0x2AA0A` | 4 | `R32` | `text/tables` | read by 1 pc(s): field load `0802A9BA ldr r3, [pc, #0x4c]`; 1 offset(s) of 1 word(s), 0.50 of the row, 194 read(s) |
| `0x2AA1A` | `0x2AA1E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2AAC4` | `0x2AAC6` | 2 | `R32` | `unknown` | read by 1 pc(s): field load `0802AA54 ldr r1, [pc, #0x6c]`; 1 offset(s) of 1 word(s), 1.00 of the row, 146 read(s) |
| `0x2AB08` | `0x2AB0A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2BC1A` | `0x2BC1E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2BDBE` | `0x2BDC2` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2BDC4` | `0x2BDC6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2C058` | `0x2C066` | 14 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x2C1D0` | `0x2C1DC` | 12 | `R32` | `unknown` | read by 2 pc(s): field load `0802C1C8 ldr r1, [pc, #8]`; field load `0802C1D0 ldr r0, [pc, #4]`; 2 offset(s) of 3 word(s), 0.67 of the row, 9 read(s) |
| `0x2C33C` | `0x2C340` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2C4B8` | `0x2C4BA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2C684` | `0x2C686` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2C698` | `0x2C69A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2C77A` | `0x2C782` | 8 | `R32` | `unknown` | read by 1 pc(s): field load `0802C6B0 ldr r0, [pc, #0xcc]`; 1 offset(s) of 2 word(s), 0.25 of the row, 26 read(s) |
| `0x2C8FA` | `0x2C8FE` | 4 | `R32` | `unknown` | read by 1 pc(s): field load `0802C7B6 ldr r0, [pc, #0x144]`; 1 offset(s) of 1 word(s), 0.50 of the row, 17 read(s) |
| `0x2CBAA` | `0x2CBAE` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2CD10` | `0x2CD12` | 2 | `R32` | `text/tables` | read by 3 pc(s): field load `0802CBDA ldr r1, [pc, #0x134]`; field load `0802CC28 ldr r0, [pc, #0xe4]`; field load `0802CC56 ldr r0, [pc, #0xb8]`; 1 offset(s) of 1 word(s), 1.00 of the row, 11 read(s) |
| `0x2CD76` | `0x2CD78` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2CD78` | `0x2CD7C` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2CD80` | `0x2CD82` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x2CDE0` | `0x2CDE4` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2D166` | `0x2D168` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x2D168` | `0x2D16C` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x301F4` | `0x301F6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x304DC` | `0x304DE` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x30604` | `0x30606` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3084C` | `0x30850` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x30B12` | `0x30B14` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x30B14` | `0x30B18` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x30EF4` | `0x30EF8` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x30EFC` | `0x30F04` | 8 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x30F08` | `0x30F0C` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x333A4` | `0x333A6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x335B4` | `0x335B6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3383A` | `0x33862` | 40 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x338FC` | `0x33908` | 12 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x3396E` | `0x33972` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x33B86` | `0x33B88` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x33B88` | `0x33B8C` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x33BB2` | `0x33BB6` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x33C3A` | `0x33C3C` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x33C42` | `0x33C44` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x33D60` | `0x33D66` | 6 | `R32` | `unknown` | read by 1 pc(s): field load `08033BC6 ldr r0, [pc, #0x19c]`; 1 offset(s) of 1 word(s), 0.33 of the row, 2 read(s) |
| `0x33D80` | `0x33D82` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x33E72` | `0x33E74` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x33E74` | `0x33E78` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x33EE8` | `0x33EFA` | 18 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x33F22` | `0x33F26` | 4 | `R32` | `text/tables` | read by 1 pc(s): field load `08033F1A ldr r1, [pc, #8]`; 1 offset(s) of 1 word(s), 0.50 of the row, 5 read(s) |
| `0x35204` | `0x35208` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x355E6` | `0x355EA` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x358A2` | `0x358A4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x35BD4` | `0x35BD6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x35DCA` | `0x35DCE` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x35E34` | `0x35E38` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x35E82` | `0x35E86` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x35F00` | `0x35F02` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x35F04` | `0x35F06` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x35F80` | `0x35F86` | 6 | `R32` | `text/tables` | read by 1 pc(s): field load `08035F0A ldr r4, [pc, #0x78]`; 1 offset(s) of 1 word(s), 0.33 of the row, 1 read(s) |
| `0x36198` | `0x3619A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x36430` | `0x36432` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x36654` | `0x36656` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x36968` | `0x3696E` | 6 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3696E` | `0x36972` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x36A10` | `0x36A12` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0803698C ldr r4, [pc, #0x80]`; 1 offset(s) of 1 word(s), 1.00 of the row, 30 read(s) |
| `0x36D66` | `0x36D82` | 28 | `R32` | `unknown` | read by 6 pc(s): field load `08036ACC ldr r6, [pc, #0x2a4]`; field load `08036AD8 ldr r3, [pc, #0x29c]`; field load `08036B9E ldr r2, [pc, #0x1d4]`; 4 offset(s) of 7 word(s), 0.43 of the row, 2806 read(s) |
| `0x36D82` | `0x36D84` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3722E` | `0x37238` | 10 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x37254` | `0x3725A` | 6 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x37478` | `0x3747E` | 6 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3747E` | `0x37480` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x37568` | `0x3756A` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3756A` | `0x3756E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3764A` | `0x3764C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3764C` | `0x37650` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x37898` | `0x3789A` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x378DA` | `0x378DC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x378DC` | `0x378E0` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x378EE` | `0x378F0` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x378F0` | `0x378F4` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x379B4` | `0x379B6` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x379B6` | `0x379BA` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x37A24` | `0x37A26` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `080379C8 ldr r0, [pc, #0x58]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1 read(s) |
| `0x37B2E` | `0x37B32` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x37B40` | `0x37B42` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x37BB4` | `0x37BB6` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08037B4A ldr r0, [pc, #0x68]`; 1 offset(s) of 1 word(s), 1.00 of the row, 2040 read(s) |
| `0x37C18` | `0x37C1A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x37D48` | `0x37D4A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x37E26` | `0x37E28` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x37E28` | `0x37E2C` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x38180` | `0x38192` | 18 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x382BE` | `0x382C0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x382C0` | `0x382C4` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x383CA` | `0x383D2` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x383D2` | `0x383D4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3870A` | `0x3870C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x387D2` | `0x387D6` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x38A82` | `0x38A84` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x38AD0` | `0x38AD2` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x38DD8` | `0x38DE2` | 10 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x39120` | `0x39122` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3925C` | `0x3925E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3934A` | `0x3934E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x39360` | `0x39362` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x393BE` | `0x393C2` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3942A` | `0x3942E` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x39440` | `0x39442` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x39472` | `0x39476` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x39562` | `0x39566` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3973E` | `0x3974A` | 12 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x3983C` | `0x3983E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x398C4` | `0x398CA` | 6 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x39994` | `0x39996` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x39998` | `0x3999A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x39BCC` | `0x39BCE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x39C0E` | `0x39C12` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x39D7A` | `0x39D8E` | 20 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x39F08` | `0x39F16` | 14 | `R32` | `unknown` | read by 1 pc(s): field load `08039DB6 ldr r0, [pc, #0x158]`; 1 offset(s) of 3 word(s), 0.29 of the row, 10 read(s) |
| `0x3A084` | `0x3A086` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3A62C` | `0x3A62E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3A68E` | `0x3A692` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3A790` | `0x3A792` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3A7EE` | `0x3A7F2` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3A7F4` | `0x3A7F6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3AC4C` | `0x3AC54` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3AC58` | `0x3AC5C` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3AE60` | `0x3AE62` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3AEA0` | `0x3AEA2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B1C4` | `0x3B1C6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B1D2` | `0x3B1D4` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B368` | `0x3B36A` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0803B336 ldr r1, [pc, #0x30]`; 1 offset(s) of 1 word(s), 1.00 of the row, 5 read(s) |
| `0x3B514` | `0x3B516` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B524` | `0x3B526` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B56C` | `0x3B56E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B572` | `0x3B574` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B5F0` | `0x3B5F2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B5F6` | `0x3B5F8` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B7A8` | `0x3B7AA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B7B8` | `0x3B7BA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B99A` | `0x3B99C` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3B9A4` | `0x3B9A6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3BAD0` | `0x3BAD2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3BC18` | `0x3BC1A` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0803B936 ldr r0, [pc, #0x2e0]`; 1 offset(s) of 1 word(s), 1.00 of the row, 31347 read(s) |
| `0x3BC24` | `0x3BC26` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0803BBA0 ldr r2, [pc, #0x80]`; 1 offset(s) of 1 word(s), 1.00 of the row, 31347 read(s) |
| `0x3BCF6` | `0x3BCF8` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3BD84` | `0x3BD86` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3BF0E` | `0x3BF28` | 26 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3C0A8` | `0x3C0B6` | 14 | `R32` | `pointer-tables` | no reader in the 452-map sweep |
| `0x3C0C0` | `0x3C0C2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3C1D8` | `0x3C1DA` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3C2F0` | `0x3C2F2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3C408` | `0x3C40A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3C4D8` | `0x3C4DC` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3C602` | `0x3C604` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3C60A` | `0x3C60C` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3C814` | `0x3C816` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3C8D0` | `0x3C8D2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3CD24` | `0x3CD26` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3CE64` | `0x3CE66` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3D0EC` | `0x3D0EE` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3D0EE` | `0x3D0F2` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3D0FA` | `0x3D10C` | 18 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3D360` | `0x3D362` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3D370` | `0x3D372` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3DA74` | `0x3DA76` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3DAAC` | `0x3DAB6` | 10 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3DD32` | `0x3DD34` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3DD34` | `0x3DD38` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3DF12` | `0x3DF14` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3E014` | `0x3E016` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3E142` | `0x3E144` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3E368` | `0x3E36A` | 2 | `R32` | `unknown` | read by 1 pc(s): field load `0803E0EC ldr r2, [pc, #0x278]`; 1 offset(s) of 1 word(s), 1.00 of the row, 6391 read(s) |
| `0x3E848` | `0x3E89A` | 82 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3E950` | `0x3E954` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3E9A8` | `0x3EA24` | 124 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3EA46` | `0x3EB1A` | 212 | `R32` | `text/tables` | read by 9 pc(s): field load `0803E7CC ldr r4, [pc, #0x278]`; field load `0803E80E ldr r4, [pc, #0x23c]`; field load `0803E870 ldr r6, [pc, #0x1dc]`; 7 offset(s) of 53 word(s), 0.13 of the row, 9464 read(s) |
| `0x3EB68` | `0x3EB6C` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3EB96` | `0x3EB98` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3EBF4` | `0x3EBF8` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3ECA2` | `0x3ECA6` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3ECC2` | `0x3ECC6` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3F1B4` | `0x3F1B6` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0803F14C ldr r1, [pc, #0x64]`; 1 offset(s) of 1 word(s), 1.00 of the row, 429 read(s) |
| `0x3F36C` | `0x3F36E` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x3F36E` | `0x3F372` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3FCA4` | `0x3FCA6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3FCDE` | `0x3FCE0` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3FD34` | `0x3FD36` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3FF08` | `0x3FF0A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3FF16` | `0x3FF18` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3FF32` | `0x3FF34` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3FF4E` | `0x3FF50` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3FF98` | `0x3FF9A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3FF9E` | `0x3FFA0` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3FFAA` | `0x3FFAC` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x3FFC6` | `0x3FFC8` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x40794` | `0x407A0` | 12 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x40880` | `0x40882` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x40AE2` | `0x40AF0` | 14 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x40B22` | `0x40B24` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x40B9A` | `0x40B9C` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x40F7C` | `0x40F7E` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x42118` | `0x4212C` | 20 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x42168` | `0x42170` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4222A` | `0x4222C` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4222C` | `0x42230` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4223C` | `0x4223E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4225E` | `0x42260` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x424FE` | `0x42500` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x42500` | `0x4251E` | 30 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4256C` | `0x42592` | 38 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x42594` | `0x425B0` | 28 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x425B4` | `0x425F0` | 60 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x425F2` | `0x42604` | 18 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4260A` | `0x42638` | 46 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4263C` | `0x4269C` | 96 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4269E` | `0x426C4` | 38 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x42D2A` | `0x42D72` | 72 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x42FAA` | `0x42FAC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x42FB8` | `0x42FBC` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x462AC` | `0x46A7A` | 1998 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x46AA8` | `0x46AAE` | 6 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x46C50` | `0x46C54` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x46CBA` | `0x46CBC` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x47040` | `0x47648` | 1544 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x47652` | `0x47654` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x47684` | `0x47686` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x476A6` | `0x476A8` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4776E` | `0x47770` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x47770` | `0x479FC` | 652 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x479FC` | `0x47A00` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x47A02` | `0x47A08` | 6 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x47FAE` | `0x47FB0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4802E` | `0x48034` | 6 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x480EA` | `0x480EC` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48186` | `0x4818A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48194` | `0x48196` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x481E4` | `0x481E6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48228` | `0x4822A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48238` | `0x4823A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x482A0` | `0x482A2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x482AC` | `0x482AE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x482BC` | `0x482BE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48400` | `0x48402` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4840C` | `0x4840E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4841C` | `0x4841E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48430` | `0x48432` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48490` | `0x48492` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x484E4` | `0x484E6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x484F8` | `0x484FA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48508` | `0x4850A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48518` | `0x4851A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4854C` | `0x4854E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4855C` | `0x4855E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4856C` | `0x4856E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4859C` | `0x4859E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x485B0` | `0x485B2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x485DC` | `0x485DE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48618` | `0x4861A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4862A` | `0x4862E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48640` | `0x48642` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48650` | `0x48652` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48660` | `0x48662` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4868C` | `0x4868E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48716` | `0x4871A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48732` | `0x48736` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4879C` | `0x4879E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x487C8` | `0x487CA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x487E8` | `0x487EA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x487F4` | `0x487F6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x487F8` | `0x487FA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48804` | `0x48806` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48808` | `0x4880A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48828` | `0x4882A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48844` | `0x48846` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48848` | `0x4884A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48864` | `0x48866` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4889C` | `0x4889E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x488AC` | `0x488AE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x488F4` | `0x488F6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48904` | `0x48906` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48950` | `0x48952` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48960` | `0x48962` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48974` | `0x48976` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4898A` | `0x4898E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x489A0` | `0x489A2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48A02` | `0x48A06` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48A18` | `0x48A1A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48A28` | `0x48A2A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48A38` | `0x48A3A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48A54` | `0x48A56` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48A88` | `0x48A8A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48A98` | `0x48A9A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48AB4` | `0x48AB6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48AB8` | `0x48ABA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48AC4` | `0x48AC6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48AE4` | `0x48AE6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48AF4` | `0x48AF6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48B18` | `0x48B1A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48B24` | `0x48B26` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48B34` | `0x48B36` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48B44` | `0x48B46` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48B76` | `0x48B7A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48BBE` | `0x48BC2` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48BD4` | `0x48BD6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48BD8` | `0x48BDA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48BE4` | `0x48BE6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48BF4` | `0x48BF6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48C42` | `0x48C46` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48C58` | `0x48C5A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48C84` | `0x48C86` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48D0C` | `0x48D0E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48D1C` | `0x48D1E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48D2C` | `0x48D2E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48D40` | `0x48D42` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48D50` | `0x48D52` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48D70` | `0x48D72` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48D90` | `0x48D92` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48DB0` | `0x48DB2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48DC0` | `0x48DC2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48DD0` | `0x48DD2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48DE6` | `0x48DEA` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48DFC` | `0x48DFE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48E38` | `0x48E3A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48E44` | `0x48E46` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48E54` | `0x48E56` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48E84` | `0x48E86` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48EA4` | `0x48EA6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48EB4` | `0x48EB6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48ECA` | `0x48F54` | 138 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x48F54` | `0x49010` | 188 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x49010` | `0x49114` | 260 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x49124` | `0x4912C` | 8 | `R32` | `text/tables` | read by 1 pc(s): copy body `inside the copy routine`; 1 offset(s) of 2 word(s), 0.50 of the row, 32924 read(s) |
| `0x49130` | `0x49138` | 8 | `R32` | `text/tables` | read by 1 pc(s): copy body `inside the copy routine`; 1 offset(s) of 2 word(s), 0.50 of the row, 174390 read(s) |
| `0x4913C` | `0x49144` | 8 | `R32` | `text/tables` | read by 1 pc(s): copy body `inside the copy routine`; 1 offset(s) of 2 word(s), 0.50 of the row, 402267 read(s) |
| `0x49148` | `0x49150` | 8 | `R32` | `text/tables` | read by 1 pc(s): copy body `inside the copy routine`; 1 offset(s) of 2 word(s), 0.50 of the row, 37676914 read(s) |
| `0x49154` | `0x4915C` | 8 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x49160` | `0x49168` | 8 | `R32` | `text/tables` | read by 1 pc(s): copy body `inside the copy routine`; 1 offset(s) of 2 word(s), 0.50 of the row, 7187 read(s) |
| `0x4916C` | `0x49174` | 8 | `R32` | `text/tables` | read by 1 pc(s): copy body `inside the copy routine`; 1 offset(s) of 2 word(s), 0.50 of the row, 8 read(s) |
| `0x49178` | `0x49180` | 8 | `R32` | `text/tables` | read by 1 pc(s): copy body `inside the copy routine`; 1 offset(s) of 2 word(s), 0.50 of the row, 329 read(s) |
| `0x49184` | `0x4918C` | 8 | `R32` | `text/tables` | read by 1 pc(s): copy body `inside the copy routine`; 1 offset(s) of 2 word(s), 0.50 of the row, 656 read(s) |
| `0x49190` | `0x49198` | 8 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4919C` | `0x491A0` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x491A4` | `0x491A8` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x491AC` | `0x491B4` | 8 | `R32` | `text/tables` | read by 1 pc(s): copy body `inside the copy routine`; 1 offset(s) of 2 word(s), 0.50 of the row, 12052 read(s) |
| `0x491B8` | `0x491C0` | 8 | `R32` | `text/tables` | read by 1 pc(s): unclassified `080491B8 ??`; 1 offset(s) of 2 word(s), 0.50 of the row, 264362 read(s) |
| `0x491C4` | `0x494D8` | 788 | `R32` | `text/tables` | read by 11 pc(s): field load `08007024 ldr r2, [r1, #0x1c]`; field load `08007036 ldr r2, [r1, #0x20]`; field load `08007046 ldr r2, [r1, #0x24]`; 12 offset(s) of 197 word(s), 0.00 of the row, 2558524 read(s) |
| `0x494DE` | `0x49B44` | 1638 | `R32` | `text/tables` | read by 58 pc(s): field load `08006BC2 ldr r2, [r1, #0x2c]`; field load `08007024 ldr r2, [r1, #0x1c]`; field load `08007036 ldr r2, [r1, #0x20]`; 90 offset(s) of 409 word(s), 0.08 of the row, 1153465 read(s) |
| `0x49DB8` | `0x49DBA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x49DC8` | `0x49DCA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x49DCA` | `0x4A1FC` | 1074 | `R32` | `text/tables` | read by 49 pc(s): field load `08007354 ldr r2, [r1]`; field load `080077C4 ldr r3, [r2, #4]`; field load `0800EC6E ldr r2, [r1, #0xc]`; 72 offset(s) of 268 word(s), 0.14 of the row, 973495 read(s) |
| `0x4A1FE` | `0x4A202` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4A218` | `0x4A21A` | 2 | `R32` | `text/tables` | read by 3 pc(s): field load `0800EF10 ldr r2, [r1, #4]`; field load `0800EF1E ldr r2, [r1, #4]`; field load `0800F5E4 ldr r2, [r1, #4]`; 1 offset(s) of 1 word(s), 1.00 of the row, 529005 read(s) |
| `0x4A242` | `0x4A244` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4A244` | `0x4A246` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4A24A` | `0x4A254` | 10 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A254` | `0x4A25C` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A25C` | `0x4A260` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A260` | `0x4A264` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A264` | `0x4A268` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A268` | `0x4A298` | 48 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A298` | `0x4A29C` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A29C` | `0x4A2A0` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A2A0` | `0x4A2A4` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A2A4` | `0x4A2A8` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A2A8` | `0x4A2BC` | 20 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A2BC` | `0x4A404` | 328 | `R32` | `unknown` | read by 8 pc(s): field load `0801159E ldr r2, [r1, #0x14]`; field load `080115D2 ldr r2, [r1, #0xc]`; field load `080116D2 ldr r2, [r1, #0x10]`; 27 offset(s) of 82 word(s), 0.24 of the row, 6963 read(s) |
| `0x4A404` | `0x4A408` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A408` | `0x4A40C` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A40C` | `0x4A410` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A410` | `0x4A414` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A414` | `0x4A418` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A418` | `0x4A420` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A420` | `0x4A424` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A424` | `0x4A428` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A428` | `0x4A42C` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A42C` | `0x4A4BC` | 144 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A4BC` | `0x4A4C0` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A4C0` | `0x4A4D4` | 20 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A4D4` | `0x4A4D8` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A4D8` | `0x4A4DC` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A4DC` | `0x4A4E0` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A4E0` | `0x4A4E4` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A4E4` | `0x4A59C` | 184 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4A67C` | `0x4A67E` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `080342B6 ldr r2, [r1, #0x14]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1874 read(s) |
| `0x4AA8A` | `0x4AA8E` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4AA90` | `0x4AA92` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4AAA0` | `0x4AAA2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4AABA` | `0x4AABE` | 4 | `R32` | `text/tables` | read by 2 pc(s): field load `080190F4 ldr r2, [r1]`; field load `080342D2 ldr r2, [r1]`; 1 offset(s) of 1 word(s), 0.50 of the row, 12 read(s) |
| `0x4AAE0` | `0x4AAE2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4AAF0` | `0x4AAF2` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0804F22A ldr r2, [r1, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1 read(s) |
| `0x4AAF2` | `0x4AB24` | 50 | `R32` | `unknown` | read by 19 pc(s): field load `0800A9E8 ldr r2, [r1, #0xc]`; field load `0800AA1C ldr r2, [r1, #8]`; field load `0800AA2A ldr r2, [r1, #0xc]`; 8 offset(s) of 12 word(s), 0.60 of the row, 91042 read(s) |
| `0x4AB24` | `0x4AC8C` | 360 | `R32` | `unknown` | read by 8 pc(s): field load `08007018 ldr r2, [r1, #0xc]`; field load `080193E4 ldr r2, [r1, #8]`; field load `080193F2 ldr r2, [r1, #0xc]`; 8 offset(s) of 90 word(s), 0.09 of the row, 262 read(s) |
| `0x4AC8C` | `0x4AC94` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4AC94` | `0x4AC98` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4AC98` | `0x4AC9C` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4AC9C` | `0x4ACAC` | 16 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4ACAC` | `0x4ACB0` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4ACB0` | `0x4AEB0` | 512 | `R32` | `unknown` | read by 24 pc(s): field load `0800AA90 ldr r2, [r1]`; field load `0800AACC ldr r2, [r1]`; field load `0800AB22 ldr r2, [r1, #4]`; 45 offset(s) of 128 word(s), 0.11 of the row, 59212 read(s) |
| `0x4AEB0` | `0x4AEB4` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4AEB4` | `0x4AFF8` | 324 | `R32` | `unknown` | read by 10 pc(s): field load `0800A96A ldr r2, [r1, #8]`; field load `0800F7EE ldr r2, [r1, #4]`; field load `0801159E ldr r2, [r1, #0x14]`; 9 offset(s) of 81 word(s), 0.04 of the row, 154285 read(s) |
| `0x4AFF8` | `0x4B000` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B000` | `0x4B024` | 36 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B024` | `0x4B02C` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B02C` | `0x4B040` | 20 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B040` | `0x4B2DC` | 668 | `R32` | `unknown` | read by 20 pc(s): field load `0800ED22 ldr r2, [r1, #0xc]`; field load `0800ED32 ldr r2, [r1]`; field load `0800EF1E ldr r2, [r1, #4]`; 38 offset(s) of 167 word(s), 0.11 of the row, 21943 read(s) |
| `0x4B2DC` | `0x4B2E4` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B2E4` | `0x4B2E8` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B2E8` | `0x4B2EC` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B2EC` | `0x4B2F0` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B2F0` | `0x4B2F4` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B2F4` | `0x4B3D8` | 228 | `R32` | `unknown` | read by 11 pc(s): field load `0800A3A0 ldr r2, [r1, #0x10]`; field load `0800A3C0 ldr r2, [r1, #0x18]`; field load `0800A404 ldr r2, [r1, #0x14]`; 12 offset(s) of 57 word(s), 0.21 of the row, 7056 read(s) |
| `0x4B3D8` | `0x4B3DC` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B3DC` | `0x4B3E4` | 8 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B3E4` | `0x4B3E8` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B3E8` | `0x4B3FC` | 20 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B3FC` | `0x4B45C` | 96 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B45C` | `0x4B468` | 12 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B468` | `0x4B47C` | 20 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B47C` | `0x4B52C` | 176 | `R32` | `unknown` | read by 1 pc(s): field load `0804F544 ldr r2, [r1]`; 1 offset(s) of 44 word(s), 0.00 of the row, 422 read(s) |
| `0x4B52C` | `0x4B54C` | 32 | `R32` | `unknown` | read by 6 pc(s): field load `080115D2 ldr r2, [r1, #0xc]`; field load `080116D2 ldr r2, [r1, #0x10]`; field load `08011760 ldr r2, [r1, #0x18]`; 6 offset(s) of 8 word(s), 0.50 of the row, 303332 read(s) |
| `0x4B54C` | `0x4B894` | 840 | `R32` | `unknown` | read by 36 pc(s): field load `08007024 ldr r2, [r1, #0x1c]`; field load `08007036 ldr r2, [r1, #0x20]`; field load `08007046 ldr r2, [r1, #0x24]`; 45 offset(s) of 210 word(s), 0.09 of the row, 134987 read(s) |
| `0x4B894` | `0x4B898` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B898` | `0x4B89C` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B89C` | `0x4B8A0` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8A0` | `0x4B8A4` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8A4` | `0x4B8A8` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8A8` | `0x4B8AC` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8AC` | `0x4B8B0` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8B0` | `0x4B8B4` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8B4` | `0x4B8C4` | 16 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8C4` | `0x4B8C8` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8C8` | `0x4B8CC` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8CC` | `0x4B8D0` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8D0` | `0x4B8D4` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8D4` | `0x4B8D8` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4B8D8` | `0x4B940` | 104 | `R32` | `unknown` | read by 5 pc(s): field load `080193E4 ldr r2, [r1, #8]`; field load `080193F2 ldr r2, [r1, #0xc]`; field load `0801940A ldr r2, [r1, #0x10]`; 5 offset(s) of 26 word(s), 0.00 of the row, 33 read(s) |
| `0x4B940` | `0x4BA78` | 312 | `R32` | `unknown` | read by 8 pc(s): field load `0800A3A0 ldr r2, [r1, #0x10]`; field load `0800A3C0 ldr r2, [r1, #0x18]`; field load `0800A404 ldr r2, [r1, #0x14]`; 8 offset(s) of 78 word(s), 0.10 of the row, 5343 read(s) |
| `0x4BA80` | `0x4BA82` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08011A7E ldr r2, [r1, #8]`; 1 offset(s) of 1 word(s), 1.00 of the row, 179151 read(s) |
| `0x4E4DA` | `0x4E4DC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E4DE` | `0x4E4E0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E4E2` | `0x4E4E4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E4E6` | `0x4E4E8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E4EA` | `0x4E4EC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E4EE` | `0x4E4F0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E4F2` | `0x4E4F4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E4F6` | `0x4E4F8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E4FA` | `0x4E4FC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E4FE` | `0x4E500` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E502` | `0x4E504` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E506` | `0x4E508` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E51E` | `0x4E520` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E522` | `0x4E524` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E546` | `0x4E548` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E54A` | `0x4E54C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4E5B4` | `0x4E5B6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4E604` | `0x4E606` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4E954` | `0x4E956` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4E9E4` | `0x4E9E6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4EA08` | `0x4EA0A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4EAF0` | `0x4EAF2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4EC02` | `0x4EC04` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4EC06` | `0x4EC08` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4EC1E` | `0x4EC20` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4EC9A` | `0x4EC9C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4ECBE` | `0x4ECC0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4ECE2` | `0x4ECE4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4ECF6` | `0x4ECF8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4ED94` | `0x4ED96` | 2 | `R32` | `unknown` | read by 1 pc(s): field load `0804ED7C ldr r2, [pc, #0x14]`; 1 offset(s) of 1 word(s), 1.00 of the row, 6954 read(s) |
| `0x4EE20` | `0x4EE22` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0804EE06 ldr r0, [pc, #0x18]`; 1 offset(s) of 1 word(s), 1.00 of the row, 4 read(s) |
| `0x4EE58` | `0x4EE5A` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4EEF8` | `0x4EEFA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4EF1C` | `0x4EF1E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4EF44` | `0x4EF46` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4EF68` | `0x4EF6A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4F00A` | `0x4F00C` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4F02E` | `0x4F032` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F05E` | `0x4F060` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F076` | `0x4F078` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F09E` | `0x4F0A0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F0A2` | `0x4F0A4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F0C2` | `0x4F0C4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F0DE` | `0x4F0E0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F116` | `0x4F118` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F15E` | `0x4F160` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F162` | `0x4F164` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F172` | `0x4F174` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F176` | `0x4F178` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F186` | `0x4F188` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F19E` | `0x4F1A0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F1A2` | `0x4F1A4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F1A6` | `0x4F1A8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F1AA` | `0x4F1AC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F1AE` | `0x4F1B0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F1B2` | `0x4F1B4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F1EA` | `0x4F1EC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F1EE` | `0x4F1F0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F1F2` | `0x4F1F4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F1F6` | `0x4F1F8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F1FA` | `0x4F1FC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F1FE` | `0x4F200` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F202` | `0x4F204` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F206` | `0x4F208` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F20A` | `0x4F20C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F282` | `0x4F284` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F292` | `0x4F294` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F296` | `0x4F298` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F29A` | `0x4F29C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F2BA` | `0x4F2BC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F2CA` | `0x4F2CC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F2CE` | `0x4F2D0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F2DE` | `0x4F2E0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F2E2` | `0x4F2E4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F2E6` | `0x4F2E8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F30E` | `0x4F310` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F31E` | `0x4F320` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F322` | `0x4F324` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F36E` | `0x4F370` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F37E` | `0x4F380` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F382` | `0x4F384` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F386` | `0x4F388` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F38A` | `0x4F38C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F39A` | `0x4F39C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F3AA` | `0x4F3AC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F3AE` | `0x4F3B0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F3EE` | `0x4F3F2` | 4 | `R32` | `text/tables` | read by 1 pc(s): field load `0804F3C2 ldr r0, [pc, #0x2c]`; 1 offset(s) of 1 word(s), 0.50 of the row, 7610 read(s) |
| `0x4F404` | `0x4F406` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0804F3FA ldr r1, [pc, #8]`; 1 offset(s) of 1 word(s), 1.00 of the row, 14 read(s) |
| `0x4F412` | `0x4F414` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F44A` | `0x4F44C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F44E` | `0x4F450` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F452` | `0x4F454` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F456` | `0x4F458` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F48A` | `0x4F48C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F49A` | `0x4F49C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F4C2` | `0x4F4C4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F51A` | `0x4F51C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F51E` | `0x4F520` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F522` | `0x4F524` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F526` | `0x4F528` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F52A` | `0x4F52C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F52E` | `0x4F530` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F532` | `0x4F534` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F536` | `0x4F538` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F556` | `0x4F558` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F596` | `0x4F598` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F5E2` | `0x4F5E4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F672` | `0x4F674` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4F80E` | `0x4F810` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4F826` | `0x4F82A` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4F854` | `0x4F856` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0804F840 ldr r0, [pc, #0x10]`; 1 offset(s) of 1 word(s), 1.00 of the row, 479111 read(s) |
| `0x4F870` | `0x4F872` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4F99C` | `0x4F99E` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FCB6` | `0x4FCB8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FCBA` | `0x4FCBC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FCBE` | `0x4FCC0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FCC2` | `0x4FCC4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FCC6` | `0x4FCC8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FCDA` | `0x4FCDC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FCDE` | `0x4FCE0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FD48` | `0x4FD4A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4FDB0` | `0x4FDB2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4FDCA` | `0x4FDCC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FDCE` | `0x4FDD0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FDD2` | `0x4FDD4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FDD6` | `0x4FDD8` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FDDA` | `0x4FDDC` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FDDE` | `0x4FDE0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FDE2` | `0x4FDE4` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FE14` | `0x4FE16` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x4FE4C` | `0x4FE4E` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `0804FE32 ldr r1, [pc, #0x18]`; 1 offset(s) of 1 word(s), 1.00 of the row, 910 read(s) |
| `0x4FE72` | `0x4FE74` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FE76` | `0x4FE78` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FE7A` | `0x4FE7C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FE9A` | `0x4FE9C` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x4FED6` | `0x4FEDC` | 6 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x501DE` | `0x501E0` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x5020C` | `0x5020E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x502F8` | `0x502FA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5039C` | `0x5039E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50564` | `0x50566` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08050556 ldr r1, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 452 read(s) |
| `0x505AC` | `0x505AE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5068C` | `0x5068E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5070C` | `0x5070E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5074C` | `0x5074E` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08050732 ldr r0, [pc, #0x18]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1 read(s) |
| `0x50820` | `0x50822` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x508D4` | `0x508D6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x508F4` | `0x508F6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50908` | `0x5090A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5094C` | `0x5094E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50960` | `0x50962` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50974` | `0x50976` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50988` | `0x5098A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5099C` | `0x5099E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x509B0` | `0x509B2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x509C4` | `0x509C6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x509E4` | `0x509E6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x509F8` | `0x509FA` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `080509E8 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1809 read(s) |
| `0x50A0C` | `0x50A0E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50A4C` | `0x50A4E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50A90` | `0x50A92` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08050A80 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1 read(s) |
| `0x50AA4` | `0x50AA6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50AB8` | `0x50ABA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50AE4` | `0x50AE6` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08050AD4 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1 read(s) |
| `0x50AF8` | `0x50AFA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50B0C` | `0x50B0E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50B20` | `0x50B22` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50B34` | `0x50B36` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50B78` | `0x50B7A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50B8C` | `0x50B8E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50BA0` | `0x50BA2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50C0E` | `0x50C12` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50C24` | `0x50C26` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50C38` | `0x50C3A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50C4C` | `0x50C4E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50C6C` | `0x50C6E` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08050C5C ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 2 read(s) |
| `0x50CD6` | `0x50CDA` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50D04` | `0x50D06` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50D18` | `0x50D1A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50D2C` | `0x50D2E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50D58` | `0x50D5A` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08050D34 ldr r0, [pc, #0x20]`; 1 offset(s) of 1 word(s), 1.00 of the row, 43 read(s) |
| `0x50D6C` | `0x50D6E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50DD4` | `0x50DD6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50DFA` | `0x50DFE` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50E22` | `0x50E26` | 4 | `R32` | `text/tables` | read by 1 pc(s): field load `08050E04 ldr r0, [pc, #0x1c]`; 1 offset(s) of 1 word(s), 0.50 of the row, 1 read(s) |
| `0x50E68` | `0x50E6A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50EAC` | `0x50EAE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50EEA` | `0x50EEE` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50F48` | `0x50F4A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50F5C` | `0x50F5E` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08050F4C ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 5 read(s) |
| `0x50F70` | `0x50F72` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x50F84` | `0x50F86` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5107C` | `0x5107E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5109C` | `0x5109E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x510C2` | `0x510C6` | 4 | `R32` | `text/tables` | read by 1 pc(s): field load `080510A4 ldr r0, [pc, #0x1c]`; 1 offset(s) of 1 word(s), 0.50 of the row, 910 read(s) |
| `0x510EA` | `0x510EE` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51118` | `0x5111A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51138` | `0x5113A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51274` | `0x51276` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x512B8` | `0x512BA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x512CC` | `0x512CE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x512E0` | `0x512E2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5136C` | `0x5136E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51380` | `0x51382` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51394` | `0x51396` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x513B4` | `0x513B6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x513C8` | `0x513CA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51418` | `0x5141A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5142C` | `0x5142E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51470` | `0x51472` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51484` | `0x51486` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51498` | `0x5149A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x514AC` | `0x514AE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51508` | `0x5150A` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `080514F8 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 2 read(s) |
| `0x5154C` | `0x5154E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x515A8` | `0x515AA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x516A0` | `0x516A2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x516CC` | `0x516CE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x517B8` | `0x517BA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x517DE` | `0x517E2` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51854` | `0x51856` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51868` | `0x5186A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x518C4` | `0x518C6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x518D8` | `0x518DA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x518EC` | `0x518EE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51900` | `0x51902` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `080518F0 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 6 read(s) |
| `0x51B24` | `0x51B26` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08051B14 ldr r0, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 451 read(s) |
| `0x51B50` | `0x51B52` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51BDC` | `0x51BDE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51C0C` | `0x51C0E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51C6C` | `0x51C6E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51C80` | `0x51C82` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08051C70 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 42 read(s) |
| `0x51C94` | `0x51C96` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51DA4` | `0x51DA6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51EC8` | `0x51ECA` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08051EB8 ldr r0, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 452 read(s) |
| `0x51EDC` | `0x51EDE` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08051ECC ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1 read(s) |
| `0x51EF0` | `0x51EF2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51F1C` | `0x51F1E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51F90` | `0x51F92` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51FBC` | `0x51FBE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51FD0` | `0x51FD2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51FE4` | `0x51FE6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x51FF8` | `0x51FFA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52144` | `0x52146` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08052134 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 34 read(s) |
| `0x52182` | `0x52186` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52250` | `0x52252` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08052240 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1 read(s) |
| `0x52264` | `0x52266` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52278` | `0x5227A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x524F4` | `0x524F6` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `080524E4 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 5 read(s) |
| `0x52508` | `0x5250A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52534` | `0x52536` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52670` | `0x52672` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x526C4` | `0x526C6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x526D8` | `0x526DA` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52794` | `0x52796` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x527A8` | `0x527AA` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08052798 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 2 read(s) |
| `0x527D4` | `0x527D6` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `080527C4 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 456 read(s) |
| `0x52830` | `0x52832` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5285C` | `0x5285E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52870` | `0x52872` | 2 | `R32` | `text/tables` | read by 1 pc(s): field load `08052860 ldr r2, [pc, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 303 read(s) |
| `0x52884` | `0x52886` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52A0C` | `0x52A0E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52A20` | `0x52A22` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52AF0` | `0x52AF2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52B1C` | `0x52B1E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52B58` | `0x52B5A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52CE4` | `0x52CE6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52D10` | `0x52D12` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52DF0` | `0x52DF2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52E1C` | `0x52E1E` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52E30` | `0x52E32` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52E44` | `0x52E46` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52E70` | `0x52E72` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52EC4` | `0x52EC6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52ECE` | `0x52ED2` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x52EDA` | `0x52EDE` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x530EC` | `0x530EE` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x53178` | `0x5317A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x53336` | `0x53338` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x53338` | `0x533C4` | 140 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x533C4` | `0x5349C` | 216 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5349C` | `0x534A0` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x539DA` | `0x539DC` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x539DC` | `0x53A0C` | 48 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x53A0C` | `0x53A1C` | 16 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x53FC0` | `0x53FC2` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x53FD0` | `0x53FD4` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5440E` | `0x54412` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x5460E` | `0x54612` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x54712` | `0x54714` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x54714` | `0x5477C` | 104 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x549A4` | `0x549A6` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x54A18` | `0x54A1C` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x54CFC` | `0x54D00` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x54F04` | `0x54F08` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x6D4E0` | `0x6D586` | 166 | `R32` | `unknown` | read by 6 pc(s): field load `0803F5C4 ldrh r0, [r0, r3]`; field load `0803F5F0 ldrh r1, [r0, r1]`; field load `0803F72C ldrh r0, [r0, r3]`; 36 offset(s) of 41 word(s), 0.13 of the row, 4585 read(s) |
| `0x6D586` | `0x6D928` | 930 | `R32` | `unknown` | read by 8 pc(s): field load `0803F5C4 ldrh r0, [r0, r3]`; field load `0803F5F0 ldrh r1, [r0, r1]`; field load `0803F5F6 ldrh r5, [r0]`; 187 offset(s) of 232 word(s), 0.07 of the row, 22518 read(s) |
| `0x6D928` | `0x6D92A` | 2 | `R32` | `unknown` | read by 2 pc(s): field load `0803F5F6 ldrh r5, [r0]`; field load `08040038 ldrh r3, [r5, r3]`; 1 offset(s) of 1 word(s), 1.00 of the row, 246 read(s) |
| `0x6D92A` | `0x6E050` | 1830 | `R32` | `unknown` | read by 3 pc(s): field load `0803F5F6 ldrh r5, [r0]`; field load `0803F654 ldrh r1, [r2, r1]`; field load `08040038 ldrh r3, [r5, r3]`; 173 offset(s) of 457 word(s), 0.18 of the row, 30322 read(s) |
| `0x6E050` | `0x6E0FC` | 172 | `R32` | `unknown` | read by 9 pc(s): field load `0800B082 ldrh r0, [r1, r0]`; field load `0803DED8 ldrh r4, [r5, r4]`; field load `0803F462 ldrh r0, [r0, r3]`; 18 offset(s) of 43 word(s), 0.06 of the row, 19520 read(s) |
| `0x6E0FC` | `0x6E55C` | 1120 | `R32` | `unknown` | read by 8 pc(s): field load `0800B082 ldrh r0, [r1, r0]`; field load `0800B086 ldrh r0, [r1, r0]`; field load `0803DED8 ldrh r4, [r5, r4]`; 135 offset(s) of 280 word(s), 0.06 of the row, 1667 read(s) |
| `0x6E55C` | `0x6E55E` | 2 | `R32` | `unknown` | read by 3 pc(s): field load `0800B086 ldrh r0, [r1, r0]`; field load `0803DEDC ldrh r4, [r5, r4]`; field load `0803F492 ldrh r6, [r7]`; 1 offset(s) of 1 word(s), 1.00 of the row, 4 read(s) |
| `0x6E55E` | `0x6EE6C` | 2318 | `R32` | `unknown` | read by 4 pc(s): field load `0800B086 ldrh r0, [r1, r0]`; field load `0803DEDC ldrh r4, [r5, r4]`; field load `0803F492 ldrh r6, [r7]`; 166 offset(s) of 579 word(s), 0.14 of the row, 1691 read(s) |
| `0x6EE6C` | `0x6F58A` | 1822 | `R32` | `unknown` | read by 13 pc(s): field load `0800B07E ldr r1, [r1]`; field load `0803DED4 ldr r5, [r5]`; field load `0803F45E ldr r0, [r2]`; 98 offset(s) of 455 word(s), 0.00 of the row, 2667 read(s) |
| `0x6F58A` | `0x6F5A6` | 28 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x6F5A6` | `0x6F896` | 752 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x6F896` | `0x6F94E` | 184 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x6F94E` | `0x6F950` | 2 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x6F950` | `0x6FE18` | 1224 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x6FE18` | `0x6FE1A` | 2 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x7012C` | `0x70130` | 4 | `R32` | `text/tables` | no reader in the 452-map sweep |
| `0x7014A` | `0x701EC` | 162 | `R32` | `text/tables` | read by 27 pc(s): field load `08006BA6 ldr r0, [r4]`; field load `08006BAC ldr r0, [r4, #4]`; field load `08006BB8 ldr r0, [r4]`; 75 offset(s) of 40 word(s), 0.37 of the row, 3439157 read(s) |
| `0x701FA` | `0x701FB` | 1 | `R32` | `unknown` | read by 1 pc(s): field load `080070A4 ldrb r6, [r4, #2]`; 1 offset(s) of 1 word(s), 1.00 of the row, 29010 read(s) |
| `0x701FB` | `0x701FC` | 1 | `R32` | `unknown` | read by 1 pc(s): field load `080070A2 ldrb r3, [r4]`; 1 offset(s) of 1 word(s), 1.00 of the row, 29010 read(s) |
| `0x701FC` | `0x707DB` | 1503 | `R32` | `unknown` | read by 8 pc(s): field load `080070A0 ldrb r5, [r4, #1]`; field load `080070A2 ldrb r3, [r4]`; field load `080070A4 ldrb r6, [r4, #2]`; 1471 offset(s) of 375 word(s), 0.40 of the row, 42356209 read(s) |
| `0x707DB` | `0x707E8` | 13 | `R32` | `pointer-tables` | read by 4 pc(s): field load `0800769E ldrb r0, [r1, r0]`; field load `080076BC ldr r0, [r0]`; field load `080077BA ldr r6, [r7]`; 3 offset(s) of 3 word(s), 0.69 of the row, 426 read(s) |
| `0x707E8` | `0x707EC` | 4 | `R32` | `unknown` | read by 2 pc(s): field load `080077FA ldr r1, [r0]`; field load `08007848 ldr r0, [r0]`; 1 offset(s) of 1 word(s), 1.00 of the row, 339764 read(s) |
| `0x707EC` | `0x707F0` | 4 | `R32` | `unknown` | read by 1 pc(s): field load `08007968 ldr r0, [r5]`; 1 offset(s) of 1 word(s), 1.00 of the row, 2 read(s) |
| `0x707FC` | `0x70800` | 4 | `R32` | `unknown` | read by 1 pc(s): field load `0800926E ldr r2, [r1]`; 1 offset(s) of 1 word(s), 1.00 of the row, 250 read(s) |
| `0x70800` | `0x70804` | 4 | `R32` | `unknown` | read by 2 pc(s): field load `08007EC0 ldr r1, [r2]`; field load `08007F6A ldr r1, [r2]`; 1 offset(s) of 1 word(s), 1.00 of the row, 590910 read(s) |
| `0x70804` | `0x71008` | 2052 | `R32` | `unknown` | read by 7 pc(s): copy return `08007DDE bl #0x8049144`; copy return `08007E04 bl #0x8049144`; copy return `08007E30 bl #0x8049144`; 1025 offset(s) of 513 word(s), 0.39 of the row, 89198865 read(s) |
| `0x71008` | `0x716A0` | 1688 | `R32` | `unknown` | read by 6 pc(s): field load `08007C1E ldm r5, {r1, r2, r3, r5}`; field load `080080AC ldr r1, [r1, #4]`; field load `08008156 ldr r0, [r0]`; 214 offset(s) of 422 word(s), 0.01 of the row, 42374 read(s) |
| `0x716A8` | `0x716AC` | 4 | `R32` | `unknown` | read by 3 pc(s): field load `08008BBA ldr r0, [r6, #8]`; field load `08008D86 ldr r0, [r7, #8]`; field load `08008E14 ldr r0, [r7, #8]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1355 read(s) |
| `0x716AC` | `0x716B0` | 4 | `R32` | `unknown` | read by 5 pc(s): field load `08008AC0 ldr r0, [r5, #0xc]`; field load `08008BCC ldr r0, [r6, #0xc]`; field load `08008DA6 ldr r1, [r7, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1359 read(s) |
| `0x716B0` | `0x716B4` | 4 | `R32` | `unknown` | read by 2 pc(s): field load `08008AA8 ldr r0, [r5, #0x10]`; field load `08008AE4 ldr r5, [r5, #0x10]`; 1 offset(s) of 1 word(s), 1.00 of the row, 909 read(s) |
| `0x716C0` | `0x716C4` | 4 | `R32` | `unknown` | read by 3 pc(s): field load `08008DD6 ldr r0, [r7, #0x20]`; field load `08008E06 ldr r0, [r7, #0x20]`; field load `080091A4 ldr r0, [r4, #0x20]`; 1 offset(s) of 1 word(s), 1.00 of the row, 453 read(s) |
| `0x716C4` | `0x716C8` | 4 | `R32` | `unknown` | read by 4 pc(s): field load `080093C0 ldr r0, [r7]`; field load `080093D0 ldr r0, [r7]`; field load `08009662 ldr r0, [r4]`; 1 offset(s) of 1 word(s), 1.00 of the row, 662712 read(s) |
| `0x716C8` | `0x716CC` | 4 | `R32` | `unknown` | read by 3 pc(s): field load `080093B8 ldr r0, [r7, #4]`; field load `080093C8 ldr r0, [r7, #4]`; field load `08009668 ldr r0, [r4, #4]`; 1 offset(s) of 1 word(s), 1.00 of the row, 171869 read(s) |
| `0x716CC` | `0x716D0` | 4 | `R32` | `unknown` | read by 1 pc(s): field load `08009678 ldr r0, [r0, #8]`; 1 offset(s) of 1 word(s), 1.00 of the row, 453 read(s) |
| `0x716D0` | `0x716D4` | 4 | `R32` | `unknown` | read by 5 pc(s): field load `08009426 ldr r0, [r7, #0xc]`; field load `08009444 ldr r0, [r7, #0xc]`; field load `08009468 ldr r0, [r7, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1436 read(s) |
| `0x716D4` | `0x716D8` | 4 | `R32` | `unknown` | read by 1 pc(s): field load `080095C6 ldr r0, [r0, #0x10]`; 1 offset(s) of 1 word(s), 1.00 of the row, 453 read(s) |
| `0x716D8` | `0x716DA` | 2 | `R32` | `unknown` | read by 1 pc(s): field load `080093E0 ldrh r1, [r0]`; 1 offset(s) of 1 word(s), 1.00 of the row, 452 read(s) |
| `0x716DA` | `0x716DC` | 2 | `R32` | `unknown` | read by 1 pc(s): field load `080093EC ldrh r2, [r0, #2]`; 1 offset(s) of 1 word(s), 1.00 of the row, 452 read(s) |
| `0x716DC` | `0x716DE` | 2 | `R32` | `unknown` | read by 1 pc(s): field load `080093F4 ldrh r2, [r0, #4]`; 1 offset(s) of 1 word(s), 1.00 of the row, 452 read(s) |
| `0x716DE` | `0x71720` | 66 | `R32` | `unknown` | read by 23 pc(s): field load `080093E0 ldrh r1, [r0]`; field load `080093EC ldrh r2, [r0, #2]`; field load `080093F4 ldrh r2, [r0, #4]`; 17 offset(s) of 16 word(s), 0.52 of the row, 11059 read(s) |
| `0x71720` | `0x71724` | 4 | `R32` | `unknown` | read by 4 pc(s): field load `0800B0AE ldr r0, [r2]`; field load `0800B0F4 ldr r1, [r2]`; field load `0800B108 ldr r1, [r2]`; 1 offset(s) of 1 word(s), 1.00 of the row, 4934 read(s) |
| `0x71724` | `0x71728` | 4 | `R32` | `unknown` | no reader in the 452-map sweep |
| `0x71728` | `0x7172C` | 4 | `R32` | `unknown` | read by 1 pc(s): field load `0800B11C ldr r1, [r2, #8]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1223 read(s) |
| `0x7172C` | `0x71730` | 4 | `R32` | `unknown` | read by 1 pc(s): field load `0800B1EA ldr r1, [r1, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 6 read(s) |
| `0x71730` | `0x71734` | 4 | `R32` | `unknown` | read by 3 pc(s): field load `0800AF46 ldr r1, [r1]`; field load `0800AF5E ldr r1, [r1]`; field load `0800B018 ldr r1, [r1]`; 1 offset(s) of 1 word(s), 1.00 of the row, 29 read(s) |
| `0x71734` | `0x71738` | 4 | `R32` | `unknown` | read by 2 pc(s): field load `0800AF16 ldr r7, [r0, #4]`; field load `0800AFAA ldr r7, [r0, #4]`; 1 offset(s) of 1 word(s), 1.00 of the row, 28 read(s) |
| `0x71738` | `0x7173C` | 4 | `R32` | `unknown` | read by 2 pc(s): field load `0800AFE0 ldr r0, [r0, #8]`; field load `0800B034 ldr r0, [r0, #8]`; 1 offset(s) of 1 word(s), 1.00 of the row, 14 read(s) |
| `0x7173C` | `0x71740` | 4 | `R32` | `unknown` | read by 2 pc(s): field load `0800AF5C ldr r0, [r0, #0xc]`; field load `0800AF6E ldr r0, [r0, #0xc]`; 1 offset(s) of 1 word(s), 1.00 of the row, 6 read(s) |
| `0x71740` | `0x71758` | 24 | `R32` | `unknown` | read by 1 pc(s): field load `0800B2A2 ldr r0, [r0, #0x10]`; 1 offset(s) of 6 word(s), 0.17 of the row, 6 read(s) |
