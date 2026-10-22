# The end-of-ROM regions' raw rows: a reader per row, and its null

`R20`/`R21`/`R23`/`R24`/`R25`/`R26`/`R27`/`R28`/`R29`/`R30`/`R31` is 1129 rows / 328954 B as `docs/research/RAW_REMAINDER.csv` carries them, the same
figure as `python tools\research\raw_remainder.py` reports for the ledger's identified
binary (328954 B) against the gate's raw-data (584374 B). Data addresses are file offsets,
instruction addresses are bus addresses `0x08...`, and every quote is a Thumb decode of the
bytes at that address. The reader for a row is the first pc, in the order the channels below
are listed, that reads a byte of it. No row's null below claims that a byte cannot be
reduced: a reader this census does not hold would move the row.

## Totals by region

| region | spans | rows | bytes | rows with a cited pc | cited bytes | rows read in play | play bytes | rows with a read pc | read bytes | rows without a read pc |
|---|---|---|---|---|---|---|---|---|---|---|
| `R20` | raw-labeled run 0x76CCE4..0x77AE68 | 13 | 57568 | 0 | 0 | 0 | 0 | 0 | 0 | 13 |
| `R21` | raw-labeled run 0x71E274..0x72C378 | 32 | 57472 | 0 | 0 | 6 | 40551 | 6 | 40551 | 26 |
| `R23` | raw-labeled row 0x7122F8..0x71E258 | 37 | 48100 | 1 | 15377 | 10 | 27105 | 10 | 27105 | 27 |
| `R24` | raw-labeled row 0x72C388..0x7315E8 | 6 | 21064 | 0 | 0 | 2 | 16148 | 2 | 16148 | 4 |
| `R25` | raw-labeled row 0x75029C..0x752D4C | 4 | 10784 | 0 | 0 | 2 | 7592 | 2 | 7592 | 2 |
| `R26` | raw-labeled row 0x752EF0..0x754910 | 7 | 6680 | 0 | 0 | 1 | 40 | 1 | 40 | 6 |
| `R27` | raw-labeled row 0x754978..0x756A4C | 5 | 8404 | 0 | 0 | 5 | 8404 | 5 | 8404 | 0 |
| `R28` | raw-labeled row 0x77B200..0x77C47C | 6 | 4732 | 0 | 0 | 0 | 0 | 0 | 0 | 6 |
| `R29` | raw-labeled run 0x75A738..0x76CCD4 | 17 | 75164 | 0 | 0 | 6 | 20644 | 6 | 20644 | 11 |
| `R30` | recon slice A lower half 0x74F080..0x77C5A4 | 80 | 17850 | 0 | 0 | 12 | 2152 | 12 | 2152 | 68 |
| `R31` | recon slice B residue 0x6FC238..0x7315E8 | 922 | 21136 | 0 | 0 | 236 | 4140 | 236 | 4140 | 686 |
| **total** | | **1129** | **328954** | **1** | **15377** | **280** | **126776** | **280** | **126776** | **849** |

| class | rows | bytes | rule |
|---|---|---|---|
| `cited` | 1 | 15377 | a cited read names the pc that read a byte of the row |
| `read` | 279 | 111399 | a read logged in play names the pc that read a byte of the row |
| `pool` | 0 | 0 | the row's every grid word is the target of a decoded pc-literal load |
| `code-null` | 0 | 0 | a decoded branch enters and an instruction decodes, but the branch channel loses to its own permutation null |
| `pool-fragment` | 0 | 0 | a word loaded inside the row ends past its end |
| `pool-partial` | 0 | 0 | some grid words load, the rest have no decoded reader |
| `named-data` | 113 | 142726 | a decoded load's literal word names the row and no layout follows |
| `after-dispatch` | 0 | 0 | the row sits after a computed jump and no instruction reads it |
| `between` | 0 | 0 | the row sits between two transcribed code rows, unread |
| `unreached` | 736 | 59452 | no decoded reader and no naming word |
| **total** | **1129** | **328954** | |

`849` rows / `202178` B have no read pc at any denominator below.

## What was searched, and its denominator

| channel | instrument | denominator | result on these rows |
|---|---|---|---|
| cited read of a byte of the row | `docs/research/ENDROM_READS.csv`, cited column | 1 pc(s) | 1 row(s) |
| read of a byte of the row in play | `docs/research/ENDROM_READS.csv`, play column | 787 pc(s) | 280 row(s) |
| decoded `ldr [pc,#imm]` literal address in the row | `row_readers.walked_literals` | 4346 walked bod(ies): 2715 ledger Thumb row(s) | 0 row(s) with >= 1 word |
| decoded branch at an instruction boundary inside a walked body | `row_readers.walked_branches` | 69600 decoded instruction(s) | 0 row(s) |
| decoded `ldr` whose literal VALUE names the row | `consumer_search.literal_loads` | 2783 code row(s) / 292722 B, 467 load(s) | 145 row(s) |
| word-aligned word holding an address in the row | `row_readers.naming_words` | 2097152 words | 634 row(s), 1629 word(s) |

Every count is half-open over each row's own span. A naming word is a name, not a consumer
(P-733), and a literal-shaped halfword inside a data stream is not a reader (P-721).
A read of a byte is a consumer whatever register it lands in, and the read table holds one
pc per reader of the row it reached.

## Byte statistics

Entropy 0.50..7.71 bits/byte, zero-byte share 0.00..0.92, 0 row(s) are a single halfword,
21 row(s) are not a whole number of words and 978 hold at least one word that is an address
in the image.

## The per-row null

Each line: file offsets, region, bytes, entropy, zero-byte share, word-aligned words inside
the row, words of it that are an address in the image, class, the reader with its site, and
why the row stays raw. `none` means no instruction in the channels above names a byte of the
row at the denominators quoted.

| start | end | region | bytes | ent | zero | words | in | class | readers | null |
|---|---|---|---|---|---|---|---|---|---|---|
| `0x6FDA1C` | `0x6FDA20` | `R31` | 4 | 2.00 | 0.25 | 1 | 0 | `read` | play 08018BBA | no decoded reader and no naming word at half-open bounds |
| `0x6FDA20` | `0x6FDA30` | `R31` | 16 | 1.81 | 0.38 | 4 | 0 | `read` | play 08018A4E; 00018A4A ldr [pc] 0x018BE0 = 0x086FDA20; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x6FDA4C` | `0x6FDB18` | `R31` | 204 | 4.76 | 0.29 | 51 | 8 | `named-data` | 0000430C ldr [pc] 0x004534 = 0x086FDA4C; 3 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x6FDB28` | `0x6FDB68` | `R31` | 64 | 3.49 | 0.28 | 16 | 11 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6FDB78` | `0x6FDBA4` | `R31` | 44 | 3.71 | 0.23 | 11 | 8 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FDBB4` | `0x6FDBB8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FDC18` | `0x6FDC44` | `R31` | 44 | 3.77 | 0.14 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FDC54` | `0x6FDC58` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FDD3C` | `0x6FDD64` | `R31` | 40 | 3.61 | 0.25 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FDD74` | `0x6FDD78` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FDD94` | `0x6FDDA4` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FDDB4` | `0x6FDDB8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FDE08` | `0x6FDE44` | `R31` | 60 | 3.45 | 0.28 | 15 | 10 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FDE54` | `0x6FDE58` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FDEA0` | `0x6FDEDC` | `R31` | 60 | 3.57 | 0.28 | 15 | 10 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6FDEEC` | `0x6FDEF0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FDF20` | `0x6FDF4C` | `R31` | 44 | 3.86 | 0.14 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FDF5C` | `0x6FDF60` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FE034` | `0x6FE044` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE054` | `0x6FE058` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FE0A4` | `0x6FE0A8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x6FE0F8` | `0x6FE11C` | `R31` | 36 | 3.44 | 0.25 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE258` | `0x6FE25C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x6FE2BC` | `0x6FE2C0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029664 | no decoded reader and no naming word at half-open bounds |
| `0x6FE2E0` | `0x6FE2E4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029664 | no decoded reader and no naming word at half-open bounds |
| `0x6FE310` | `0x6FE344` | `R31` | 52 | 3.43 | 0.33 | 13 | 8 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE354` | `0x6FE358` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 0802AA40 | no decoded reader and no naming word at half-open bounds |
| `0x6FE368` | `0x6FE36C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029664 | no decoded reader and no naming word at half-open bounds |
| `0x6FE3E4` | `0x6FE3F8` | `R31` | 20 | 3.11 | 0.15 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE408` | `0x6FE40C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FE41C` | `0x6FE420` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FE46C` | `0x6FE470` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FE4B0` | `0x6FE4B4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x6FE51C` | `0x6FE520` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x6FE578` | `0x6FE57C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x6FE5BC` | `0x6FE5CC` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `read` | play 0801890C; play 08029C6A; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE5DC` | `0x6FE5E0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x6FE638` | `0x6FE63C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x6FE67C` | `0x6FE68C` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `read` | play 0801890C; play 08029FEA; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE69C` | `0x6FE6B0` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE6C0` | `0x6FE6C4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x6FE6D4` | `0x6FE6E8` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE6F8` | `0x6FE6FC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x6FE70C` | `0x6FE734` | `R31` | 40 | 3.28 | 0.40 | 10 | 5 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE744` | `0x6FE76C` | `R31` | 40 | 3.56 | 0.23 | 10 | 7 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE77C` | `0x6FE790` | `R31` | 20 | 3.21 | 0.15 | 5 | 4 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE7A0` | `0x6FE7B4` | `R31` | 20 | 3.21 | 0.15 | 5 | 4 | `read` | play 080188AC; play 080188AE; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6FE7C4` | `0x6FE7C8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x6FEA30` | `0x6FEA44` | `R31` | 20 | 3.01 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FEA64` | `0x6FEA68` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FEAC8` | `0x6FEAD8` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `read` | play 0801890C; play 08029666; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FEAE8` | `0x6FEB10` | `R31` | 40 | 3.56 | 0.23 | 10 | 7 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FEB20` | `0x6FEB98` | `R31` | 120 | 3.92 | 0.20 | 30 | 22 | `read` | play 080188AA; play 080188AC; 3 naming word(s) | named by a word; a name is not a consumer |
| `0x6FEBA8` | `0x6FEBAC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x6FEBDC` | `0x6FEBE0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x6FEBF0` | `0x6FEBF4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x6FEC3C` | `0x6FECB8` | `R31` | 124 | 3.91 | 0.22 | 31 | 22 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6FECD8` | `0x6FECDC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FED14` | `0x6FED24` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FED34` | `0x6FED38` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FEDCC` | `0x6FEDE0` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FEDF0` | `0x6FEDF4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FEEA8` | `0x6FEEAC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FEF04` | `0x6FEF14` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FEF8C` | `0x6FEF9C` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FEFAC` | `0x6FEFB0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FF02C` | `0x6FF08C` | `R31` | 96 | 3.76 | 0.29 | 24 | 16 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF09C` | `0x6FF0A0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08039858 | no decoded reader and no naming word at half-open bounds |
| `0x6FF0C8` | `0x6FF0E0` | `R31` | 24 | 3.36 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF0F0` | `0x6FF0F4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FF120` | `0x6FF130` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF140` | `0x6FF168` | `R31` | 40 | 3.56 | 0.23 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF178` | `0x6FF1A4` | `R31` | 44 | 3.74 | 0.20 | 11 | 8 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF1B4` | `0x6FF22C` | `R31` | 120 | 3.87 | 0.21 | 30 | 22 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF23C` | `0x6FF240` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FF2A8` | `0x6FF324` | `R31` | 124 | 3.93 | 0.22 | 31 | 22 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF344` | `0x6FF348` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FF380` | `0x6FF390` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF3A0` | `0x6FF3A4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FF420` | `0x6FF434` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF444` | `0x6FF448` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FF4EC` | `0x6FF4F0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FF538` | `0x6FF548` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF5C0` | `0x6FF5D0` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF5E0` | `0x6FF5E4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FF640` | `0x6FF69C` | `R31` | 92 | 3.72 | 0.30 | 23 | 15 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF6AC` | `0x6FF6B0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FF6C0` | `0x6FF6D8` | `R31` | 24 | 3.18 | 0.29 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FF6E8` | `0x6FF6EC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FF78C` | `0x6FF790` | `R31` | 4 | 0.81 | 0.75 | 1 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FFAD8` | `0x6FFAF0` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FFB00` | `0x6FFB04` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FFB70` | `0x6FFB74` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FFBD4` | `0x6FFBD8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x6FFC18` | `0x6FFC28` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `read` | play 0801890C; play 08029FEA; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6FFCC4` | `0x6FFCD4` | `R31` | 16 | 1.50 | 0.69 | 4 | 1 | `read` | play 0801CDA2; play 08029C6A; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6FFCE4` | `0x6FFD04` | `R31` | 32 | 3.96 | 0.09 | 8 | 7 | `read` | play 08018F94; play 08018FB2; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FFD14` | `0x6FFD28` | `R31` | 20 | 3.21 | 0.15 | 5 | 4 | `read` | play 0801890C; play 08029664; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6FFD38` | `0x6FFD3C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 0802AA40 | no decoded reader and no naming word at half-open bounds |
| `0x6FFD80` | `0x6FFD90` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `read` | play 0801890C; play 08029FEA; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x6FFE28` | `0x6FFE38` | `R31` | 16 | 1.62 | 0.69 | 4 | 1 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FFE48` | `0x6FFE5C` | `R31` | 20 | 3.21 | 0.15 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FFE6C` | `0x6FFE70` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FFE80` | `0x6FFE84` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FFEE4` | `0x6FFEE8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FFEF8` | `0x6FFEFC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FFF0C` | `0x6FFF10` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FFF20` | `0x6FFF24` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FFF34` | `0x6FFF38` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FFF70` | `0x6FFF80` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x6FFF90` | `0x6FFF94` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x6FFFC8` | `0x700000` | `R31` | 56 | 3.65 | 0.29 | 14 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700010` | `0x700014` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700090` | `0x7000B4` | `R31` | 36 | 3.25 | 0.28 | 9 | 6 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7000D4` | `0x7000E8` | `R31` | 20 | 2.90 | 0.35 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7000F8` | `0x700120` | `R31` | 40 | 3.37 | 0.28 | 10 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x700130` | `0x700144` | `R31` | 20 | 3.05 | 0.15 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700154` | `0x700168` | `R31` | 20 | 3.05 | 0.15 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x700178` | `0x70017C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70018C` | `0x700190` | `R31` | 4 | 2.00 | 0.25 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700210` | `0x700220` | `R31` | 16 | 2.09 | 0.56 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700230` | `0x700234` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7002CC` | `0x7002D0` | `R31` | 4 | 2.00 | 0.25 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700300` | `0x700310` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700320` | `0x700324` | `R31` | 4 | 2.00 | 0.25 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700380` | `0x700390` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7003A0` | `0x7003E8` | `R31` | 72 | 3.58 | 0.31 | 18 | 12 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7003F8` | `0x70040C` | `R31` | 20 | 3.21 | 0.15 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70041C` | `0x700420` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70043C` | `0x700450` | `R31` | 20 | 2.76 | 0.35 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700460` | `0x700478` | `R31` | 24 | 3.27 | 0.29 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700488` | `0x7004A0` | `R31` | 24 | 3.08 | 0.33 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7004B0` | `0x7004B4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7004C4` | `0x7004F0` | `R31` | 44 | 3.46 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700500` | `0x700504` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700558` | `0x700568` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7005F4` | `0x7005FC` | `R31` | 8 | 1.06 | 0.75 | 2 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700650` | `0x700658` | `R31` | 8 | 2.75 | 0.00 | 2 | 2 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700678` | `0x70067C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700700` | `0x700710` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7007A4` | `0x7007A8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x7007E8` | `0x7007F8` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `read` | play 080188AE; play 0801890C; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x700808` | `0x700820` | `R31` | 24 | 3.02 | 0.29 | 6 | 4 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700830` | `0x700848` | `R31` | 24 | 3.29 | 0.12 | 6 | 5 | `read` | play 080190B4; play 080190C2; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700858` | `0x70085C` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x700888` | `0x700898` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `read` | play 0801890C; play 08029C6A; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7008A8` | `0x7008AC` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x700930` | `0x700940` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700950` | `0x700954` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700974` | `0x700978` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700988` | `0x70098C` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7009B8` | `0x7009E0` | `R31` | 40 | 3.42 | 0.23 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700AE8` | `0x700B10` | `R31` | 40 | 2.96 | 0.42 | 10 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700B20` | `0x700B28` | `R31` | 8 | 2.75 | 0.00 | 2 | 2 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700B50` | `0x700B54` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700B64` | `0x700B68` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700C08` | `0x700C0C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700C4C` | `0x700C5C` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700C6C` | `0x700C7C` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700C8C` | `0x700D18` | `R31` | 140 | 3.87 | 0.22 | 35 | 25 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x700D28` | `0x700DA0` | `R31` | 120 | 3.87 | 0.21 | 30 | 22 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x700DB0` | `0x700DB4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700E20` | `0x700E74` | `R31` | 84 | 4.05 | 0.21 | 21 | 15 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x700E94` | `0x700E98` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700EB8` | `0x700EC8` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700ED8` | `0x700EDC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x700F68` | `0x700F80` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x700F90` | `0x700F94` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701060` | `0x7010A0` | `R31` | 64 | 3.95 | 0.25 | 16 | 11 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7010F4` | `0x7010F8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701128` | `0x701138` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x701148` | `0x7011B8` | `R31` | 112 | 3.74 | 0.30 | 28 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7011C8` | `0x7011CC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7011F4` | `0x7011F8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701208` | `0x70120C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701244` | `0x701248` | `R31` | 4 | 0.81 | 0.75 | 1 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701298` | `0x7012D4` | `R31` | 60 | 3.53 | 0.28 | 15 | 10 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7012E4` | `0x701310` | `R31` | 44 | 3.71 | 0.23 | 11 | 8 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x701320` | `0x701324` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70137C` | `0x7013A8` | `R31` | 44 | 3.86 | 0.14 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7013B8` | `0x7013BC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7014A0` | `0x7014A4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x7014E4` | `0x7014F4` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x701504` | `0x701568` | `R31` | 100 | 3.82 | 0.22 | 25 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x701578` | `0x7015F0` | `R31` | 120 | 3.87 | 0.21 | 30 | 22 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x701600` | `0x701604` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70165C` | `0x7016B0` | `R31` | 84 | 4.05 | 0.21 | 21 | 15 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7016D0` | `0x7016D4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7016F4` | `0x701704` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x701714` | `0x701718` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701794` | `0x7017AC` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7017BC` | `0x7017C0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701868` | `0x70186C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70189C` | `0x70190C` | `R31` | 112 | 3.76 | 0.30 | 28 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70191C` | `0x701920` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701930` | `0x701948` | `R31` | 24 | 3.27 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x701958` | `0x70195C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701998` | `0x70199C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7019DC` | `0x7019EC` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7019FC` | `0x701A0C` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x701A1C` | `0x701AA8` | `R31` | 140 | 3.92 | 0.22 | 35 | 25 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x701AB8` | `0x701B30` | `R31` | 120 | 3.92 | 0.20 | 30 | 22 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x701B40` | `0x701B44` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701BB0` | `0x701C04` | `R31` | 84 | 3.99 | 0.23 | 21 | 15 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x701C24` | `0x701C28` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701C58` | `0x701C68` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x701C78` | `0x701C7C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701CF8` | `0x701D10` | `R31` | 24 | 3.07 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x701D20` | `0x701D24` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701E00` | `0x701E24` | `R31` | 36 | 3.05 | 0.39 | 9 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x701E34` | `0x701E50` | `R31` | 28 | 3.77 | 0.11 | 7 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x701EA4` | `0x701EA8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701ED8` | `0x701EE8` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x701EF8` | `0x701F68` | `R31` | 112 | 3.75 | 0.30 | 28 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x701F78` | `0x701F7C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x701FA4` | `0x701FD4` | `R31` | 48 | 3.93 | 0.19 | 12 | 9 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x701FE4` | `0x701FE8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x702050` | `0x702054` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70207C` | `0x7020A0` | `R31` | 36 | 3.44 | 0.25 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7020B0` | `0x7020B4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70210C` | `0x702120` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x702130` | `0x702134` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x702144` | `0x702148` | `R31` | 4 | 0.81 | 0.75 | 1 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x702188` | `0x7021AC` | `R31` | 36 | 3.30 | 0.25 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7021BC` | `0x7021C0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x702584` | `0x702594` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `read` | play 0801890C; play 08029D1A; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7025A4` | `0x7025B8` | `R31` | 20 | 3.21 | 0.15 | 5 | 4 | `read` | play 080188AE; play 0801890C; 3 naming word(s) | named by a word; a name is not a consumer |
| `0x7025C8` | `0x7025CC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x7025DC` | `0x7025E0` | `R31` | 4 | 0.81 | 0.75 | 1 | 0 | `read` | play 0802B7CA | no decoded reader and no naming word at half-open bounds |
| `0x702624` | `0x702628` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x702638` | `0x70263C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7026C8` | `0x7026DC` | `R31` | 20 | 3.21 | 0.15 | 5 | 4 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7026EC` | `0x7026F0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70271C` | `0x70272C` | `R31` | 16 | 2.81 | 0.19 | 4 | 3 | `read` | play 0801890C; play 08029FEA; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7027B4` | `0x702804` | `R31` | 80 | 3.92 | 0.24 | 20 | 14 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x702814` | `0x702818` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 0802AA40 | no decoded reader and no naming word at half-open bounds |
| `0x70289C` | `0x7028B0` | `R31` | 20 | 3.21 | 0.15 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7028C0` | `0x7028C4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70297C` | `0x702980` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x7029D0` | `0x7029E4` | `R31` | 20 | 3.01 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7029F4` | `0x702A30` | `R31` | 60 | 4.01 | 0.20 | 15 | 11 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x702A40` | `0x702A80` | `R31` | 64 | 4.03 | 0.19 | 16 | 12 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x702A90` | `0x702AC8` | `R31` | 56 | 3.29 | 0.39 | 14 | 8 | `read` | play 0801890C; play 08029662; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x702AD8` | `0x702AEC` | `R31` | 20 | 3.21 | 0.15 | 5 | 4 | `read` | play 0801890C; play 08029666; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x702AFC` | `0x702B00` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029664 | no decoded reader and no naming word at half-open bounds |
| `0x702B4C` | `0x702B50` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x702B94` | `0x702B98` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x702BC8` | `0x702BDC` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x702BEC` | `0x702BF0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029664 | no decoded reader and no naming word at half-open bounds |
| `0x702C70` | `0x702C74` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x702CA0` | `0x702CA4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x702CB4` | `0x702CB8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x702D38` | `0x702D3C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029E80 | no decoded reader and no naming word at half-open bounds |
| `0x702D7C` | `0x702DB0` | `R31` | 52 | 3.43 | 0.33 | 13 | 8 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x702DC0` | `0x702DD8` | `R31` | 24 | 3.27 | 0.25 | 6 | 4 | `read` | play 08039858; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x702DE8` | `0x702DEC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x702E6C` | `0x702E70` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x702FA0` | `0x702FB0` | `R31` | 16 | 2.58 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x702FC0` | `0x702FC4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703008` | `0x703018` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703028` | `0x70302C` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703070` | `0x703080` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703090` | `0x703094` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70327C` | `0x70328C` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70329C` | `0x7032A0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7032D8` | `0x703310` | `R31` | 56 | 3.78 | 0.23 | 14 | 10 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703320` | `0x703324` | `R31` | 4 | 2.00 | 0.25 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703474` | `0x703484` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703494` | `0x703498` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x703524` | `0x703528` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703568` | `0x70358C` | `R31` | 36 | 3.45 | 0.22 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70359C` | `0x7035D4` | `R31` | 56 | 3.55 | 0.29 | 14 | 9 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7035E4` | `0x7035E8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7035F8` | `0x70360C` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70361C` | `0x703620` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703630` | `0x703644` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703654` | `0x703668` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703678` | `0x7036A0` | `R31` | 40 | 3.52 | 0.20 | 10 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7036B0` | `0x7036C4` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7036D4` | `0x7036D8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7036E8` | `0x7036EC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703784` | `0x703788` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703820` | `0x703824` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703904` | `0x703938` | `R31` | 52 | 3.46 | 0.31 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x703948` | `0x703974` | `R31` | 44 | 3.81 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703984` | `0x703988` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703998` | `0x7039C4` | `R31` | 44 | 3.54 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7039D4` | `0x7039D8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703A98` | `0x703ACC` | `R31` | 52 | 3.46 | 0.31 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x703ADC` | `0x703AE0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703AF0` | `0x703B04` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703B14` | `0x703B18` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703B28` | `0x703B3C` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703B4C` | `0x703B60` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703B70` | `0x703B98` | `R31` | 40 | 3.57 | 0.20 | 10 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x703BA8` | `0x703BBC` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x703BCC` | `0x703BD0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703BE0` | `0x703BE4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703C78` | `0x703C7C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703D14` | `0x703D18` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703E10` | `0x703E20` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703E30` | `0x703E68` | `R31` | 56 | 3.55 | 0.29 | 14 | 9 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x703E78` | `0x703E7C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703E98` | `0x703EC0` | `R31` | 40 | 3.72 | 0.12 | 10 | 8 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703ED0` | `0x703ED4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703EE4` | `0x703F10` | `R31` | 44 | 3.54 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x703F20` | `0x703F24` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x703F74` | `0x703F78` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x703FAC` | `0x703FE4` | `R31` | 56 | 3.71 | 0.27 | 14 | 9 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x704004` | `0x704014` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704024` | `0x704028` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x7040BC` | `0x7040CC` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 0801890C; play 08029B34; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7040EC` | `0x7040F0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704148` | `0x704164` | `R31` | 28 | 3.84 | 0.11 | 7 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704174` | `0x704178` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7041A4` | `0x7041A8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08039858 | no decoded reader and no naming word at half-open bounds |
| `0x7041E0` | `0x704200` | `R31` | 32 | 3.20 | 0.31 | 8 | 5 | `read` | play 0801890C; play 0802692E; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704210` | `0x704214` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x7042C8` | `0x7042D8` | `R31` | 16 | 2.48 | 0.38 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7042E8` | `0x704304` | `R31` | 28 | 3.70 | 0.11 | 7 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704314` | `0x704318` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704408` | `0x70440C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x70444C` | `0x70446C` | `R31` | 32 | 3.20 | 0.31 | 8 | 5 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70447C` | `0x704480` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x704490` | `0x704494` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x7044A4` | `0x7044B8` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7044C8` | `0x7044F0` | `R31` | 40 | 3.57 | 0.20 | 10 | 7 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x704500` | `0x704514` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `read` | play 080188AE; play 0801890C; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x704524` | `0x704528` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x704538` | `0x70453C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x704650` | `0x704654` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704684` | `0x7046B8` | `R31` | 52 | 3.46 | 0.31 | 13 | 8 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7046C8` | `0x7046CC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08039858 | no decoded reader and no naming word at half-open bounds |
| `0x7046DC` | `0x704708` | `R31` | 44 | 3.54 | 0.30 | 11 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x704718` | `0x70471C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704758` | `0x70475C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x7047AC` | `0x7047C0` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7047D0` | `0x7047D4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x7047E4` | `0x7047F8` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704808` | `0x704830` | `R31` | 40 | 3.62 | 0.20 | 10 | 7 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704840` | `0x704854` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704864` | `0x704878` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `read` | play 080188AC; play 080188AE; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x704888` | `0x70488C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70494C` | `0x704950` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x704A34` | `0x704A44` | `R31` | 16 | 2.48 | 0.38 | 4 | 2 | `read` | play 08018878; play 08029B34; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704A64` | `0x704A68` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704AA4` | `0x704AA8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704AE8` | `0x704B08` | `R31` | 32 | 3.20 | 0.31 | 8 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704B18` | `0x704B1C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704B2C` | `0x704B30` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704B40` | `0x704B54` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704B64` | `0x704B8C` | `R31` | 40 | 3.57 | 0.20 | 10 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x704B9C` | `0x704BC4` | `R31` | 40 | 3.57 | 0.20 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704BD4` | `0x704BFC` | `R31` | 40 | 3.57 | 0.20 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704C0C` | `0x704C20` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x704C30` | `0x704C34` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704C44` | `0x704C48` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704CDC` | `0x704CE0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704DC8` | `0x704DCC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704DFC` | `0x704E30` | `R31` | 52 | 3.50 | 0.31 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x704E40` | `0x704E44` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704E54` | `0x704E80` | `R31` | 44 | 3.58 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704E90` | `0x704E94` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x704ED0` | `0x704ED4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x704F14` | `0x704F34` | `R31` | 32 | 3.20 | 0.31 | 8 | 5 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704F44` | `0x704F48` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x704F58` | `0x704F5C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x704F6C` | `0x704F80` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704F90` | `0x704F94` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x704F94` | `0x704FA4` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 080188AE; play 0801890C; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x704FA4` | `0x704FB8` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x704FC8` | `0x704FDC` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `read` | play 080188AE; play 0801890C; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x704FEC` | `0x704FF0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x705000` | `0x705004` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x7050E4` | `0x7050E8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x705130` | `0x705134` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x705168` | `0x705178` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 0801890C; play 08029E82; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705188` | `0x7051E8` | `R31` | 96 | 3.78 | 0.28 | 24 | 16 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7051F8` | `0x7051FC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08039858 | no decoded reader and no naming word at half-open bounds |
| `0x705224` | `0x70523C` | `R31` | 24 | 3.27 | 0.25 | 6 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70523C` | `0x70527C` | `R31` | 64 | 3.07 | 0.41 | 16 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70528C` | `0x705290` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7052F0` | `0x705300` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 0801890C; play 08029FEA; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705310` | `0x705320` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 0801890C; play 0802AA42; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705330` | `0x705334` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 0802AA40 | no decoded reader and no naming word at half-open bounds |
| `0x705360` | `0x705364` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7053C4` | `0x7053C8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x7053F8` | `0x705408` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705418` | `0x70542C` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70543C` | `0x705440` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x705484` | `0x7054AC` | `R31` | 40 | 3.30 | 0.35 | 10 | 6 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x7054BC` | `0x7054C0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x705514` | `0x705518` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x705568` | `0x70557C` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70558C` | `0x7055B4` | `R31` | 40 | 3.57 | 0.20 | 10 | 7 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7055C4` | `0x7055C8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x7055D8` | `0x705614` | `R31` | 60 | 3.28 | 0.43 | 15 | 7 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705624` | `0x70564C` | `R31` | 40 | 3.46 | 0.23 | 10 | 7 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70565C` | `0x705670` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705680` | `0x705684` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x7057EC` | `0x7057F0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x705800` | `0x705804` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x705838` | `0x70584C` | `R31` | 20 | 3.01 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70586C` | `0x705870` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7058A8` | `0x7058AC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x7058EC` | `0x7058FC` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 0801890C; play 08029FEA; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70590C` | `0x705920` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705930` | `0x705934` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x705944` | `0x705958` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705968` | `0x70596C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x70597C` | `0x7059A4` | `R31` | 40 | 3.23 | 0.40 | 10 | 5 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7059B4` | `0x7059DC` | `R31` | 40 | 3.57 | 0.20 | 10 | 7 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7059EC` | `0x705A00` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705A10` | `0x705A24` | `R31` | 20 | 3.02 | 0.10 | 5 | 4 | `read` | play 080188AC; play 080188AE; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x705A34` | `0x705A38` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x705BD8` | `0x705BDC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x705C0C` | `0x705C40` | `R31` | 52 | 3.46 | 0.31 | 13 | 8 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x705C50` | `0x705C54` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08039858 | no decoded reader and no naming word at half-open bounds |
| `0x705C64` | `0x705C90` | `R31` | 44 | 3.49 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705CA0` | `0x705CA4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x705CE8` | `0x705CF8` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 0801890C; play 08029D1A; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705D08` | `0x705D0C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x705D5C` | `0x705D6C` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705D7C` | `0x705D90` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705DA0` | `0x705DA4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x705DB4` | `0x705DC8` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705DD8` | `0x705DDC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x705DEC` | `0x705E14` | `R31` | 40 | 3.23 | 0.40 | 10 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705E24` | `0x705E4C` | `R31` | 40 | 3.46 | 0.23 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705E5C` | `0x705E70` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x705E80` | `0x705E94` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x705EA4` | `0x705EA8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x706048` | `0x70604C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70607C` | `0x7060B0` | `R31` | 52 | 3.46 | 0.31 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7060C0` | `0x7060C4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7060D4` | `0x706100` | `R31` | 44 | 3.54 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x706110` | `0x706114` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x706150` | `0x706154` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x706194` | `0x7061A8` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7061B8` | `0x7061CC` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7061DC` | `0x7061F0` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x706200` | `0x706204` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x706214` | `0x706228` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x706238` | `0x70623C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70624C` | `0x706274` | `R31` | 40 | 3.23 | 0.40 | 10 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x706284` | `0x7062AC` | `R31` | 40 | 3.51 | 0.20 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7062BC` | `0x7062D0` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7062E0` | `0x7062F4` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x706304` | `0x706308` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7064AC` | `0x7064B0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7064E0` | `0x706514` | `R31` | 52 | 3.46 | 0.31 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x706524` | `0x706528` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x706538` | `0x706564` | `R31` | 44 | 3.58 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x706574` | `0x706578` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7065BC` | `0x7065CC` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7065DC` | `0x7065E0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x706630` | `0x706640` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x706650` | `0x706664` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x706674` | `0x706678` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x706688` | `0x70669C` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7066AC` | `0x7066B0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7066C0` | `0x7066E8` | `R31` | 40 | 3.23 | 0.40 | 10 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7066F8` | `0x706720` | `R31` | 40 | 3.52 | 0.20 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x706730` | `0x706744` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x706754` | `0x706768` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x706778` | `0x70677C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x706920` | `0x706924` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x706954` | `0x706988` | `R31` | 52 | 3.46 | 0.31 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x706998` | `0x70699C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7069AC` | `0x7069D8` | `R31` | 44 | 3.54 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7069E8` | `0x7069EC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x706F2C` | `0x706F3C` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x706F4C` | `0x706F50` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7071CC` | `0x7071D0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x707210` | `0x707230` | `R31` | 32 | 3.20 | 0.31 | 8 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707240` | `0x707244` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x707254` | `0x707258` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x707268` | `0x70727C` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70728C` | `0x7072B4` | `R31` | 40 | 3.57 | 0.20 | 10 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7072C4` | `0x7072D8` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7072E8` | `0x7072EC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7072FC` | `0x707300` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x707414` | `0x707418` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x707460` | `0x707464` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x7074D4` | `0x7074D8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x707570` | `0x707590` | `R31` | 32 | 3.14 | 0.31 | 8 | 5 | `read` | play 0801890C; play 080190C4; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7075A0` | `0x7075D0` | `R31` | 48 | 3.88 | 0.21 | 12 | 9 | `read` | play 080190B4; play 080190C2; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7075F0` | `0x7075F4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x707628` | `0x707644` | `R31` | 28 | 3.91 | 0.11 | 7 | 6 | `read` | play 080190B4; play 080190C2; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7076E0` | `0x7076E4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x707754` | `0x707768` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707778` | `0x70777C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70778C` | `0x7077A0` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7077B0` | `0x7077D8` | `R31` | 40 | 3.57 | 0.20 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7077E8` | `0x7077FC` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70780C` | `0x707820` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707830` | `0x707834` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x707980` | `0x707994` | `R31` | 20 | 3.01 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7079A4` | `0x7079A8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7079B8` | `0x7079CC` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7079DC` | `0x707A04` | `R31` | 40 | 3.57 | 0.20 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707A14` | `0x707A28` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707A38` | `0x707A4C` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707A5C` | `0x707A60` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x707B38` | `0x707B48` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707B58` | `0x707B6C` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707B7C` | `0x707B80` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x707B98` | `0x707BA8` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707BB8` | `0x707BBC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x707BE4` | `0x707BE8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x707C68` | `0x707C6C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x707CAC` | `0x707CC0` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707CD0` | `0x707CE4` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `read` | play 0801890C; play 08029C68; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707CF4` | `0x707D08` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707D18` | `0x707D1C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x707D2C` | `0x707D40` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707D50` | `0x707D54` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x707D64` | `0x707D8C` | `R31` | 40 | 3.23 | 0.40 | 10 | 5 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707D9C` | `0x707DC4` | `R31` | 40 | 3.57 | 0.20 | 10 | 7 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707DD4` | `0x707DE8` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x707DF8` | `0x707E0C` | `R31` | 20 | 3.18 | 0.10 | 5 | 4 | `read` | play 080188AC; play 080188AE; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x707E1C` | `0x707E20` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x707FC4` | `0x707FC8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x707FF8` | `0x70802C` | `R31` | 52 | 3.42 | 0.31 | 13 | 8 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70803C` | `0x708040` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08039858 | no decoded reader and no naming word at half-open bounds |
| `0x708050` | `0x70807C` | `R31` | 44 | 3.58 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70808C` | `0x708090` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7080AC` | `0x7080BC` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7080CC` | `0x7080D0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x708120` | `0x708130` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 0801890C; play 08029D1A; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x708140` | `0x708144` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x708184` | `0x708194` | `R31` | 16 | 2.78 | 0.12 | 4 | 3 | `read` | play 0801890C; play 08029FEA; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7081A4` | `0x7081B8` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7081C8` | `0x7081CC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x7081DC` | `0x7081F0` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x708200` | `0x708204` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x708214` | `0x70823C` | `R31` | 40 | 3.18 | 0.40 | 10 | 5 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70824C` | `0x708274` | `R31` | 40 | 3.67 | 0.20 | 10 | 7 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x708284` | `0x708298` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7082A8` | `0x7082BC` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `read` | play 080188AC; play 080188AE; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7082CC` | `0x7082D0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x708474` | `0x708478` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7084A8` | `0x7084DC` | `R31` | 52 | 3.50 | 0.31 | 13 | 8 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7084EC` | `0x7084F0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08039858 | no decoded reader and no naming word at half-open bounds |
| `0x708500` | `0x70852C` | `R31` | 44 | 3.58 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70853C` | `0x708540` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70857C` | `0x708580` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x7085D0` | `0x7085E4` | `R31` | 20 | 2.97 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7085F4` | `0x70861C` | `R31` | 40 | 3.67 | 0.20 | 10 | 7 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70862C` | `0x708650` | `R31` | 36 | 3.56 | 0.22 | 9 | 6 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x708660` | `0x708674` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `read` | play 080188AE; play 0801890C; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x708684` | `0x708688` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x708698` | `0x70869C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x7086F8` | `0x708710` | `R31` | 24 | 3.62 | 0.12 | 6 | 5 | `read` | play 08018F94; play 08018FB2; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70877C` | `0x708780` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x7087CC` | `0x7087F8` | `R31` | 44 | 3.89 | 0.11 | 11 | 9 | `read` | play 0801890C; play 08018FC0; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x708808` | `0x708834` | `R31` | 44 | 3.90 | 0.11 | 11 | 9 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x708844` | `0x708848` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708858` | `0x70885C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708894` | `0x7088AC` | `R31` | 24 | 3.62 | 0.12 | 6 | 5 | `read` | play 08018F94; play 08018FB2; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7088BC` | `0x7088E8` | `R31` | 44 | 3.86 | 0.11 | 11 | 9 | `read` | play 08029E80; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x708968` | `0x70896C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70897C` | `0x708980` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7089D8` | `0x7089E0` | `R31` | 8 | 2.75 | 0.00 | 2 | 2 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708A4C` | `0x708A50` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708A90` | `0x708AB0` | `R31` | 32 | 3.24 | 0.31 | 8 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x708AC0` | `0x708AC4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708AD4` | `0x708AD8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708AE8` | `0x708AFC` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x708B0C` | `0x708B34` | `R31` | 40 | 3.72 | 0.20 | 10 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x708B44` | `0x708B58` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x708B68` | `0x708B6C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708B7C` | `0x708B80` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708CA4` | `0x708CA8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708CD8` | `0x708D0C` | `R31` | 52 | 3.50 | 0.31 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x708D1C` | `0x708D20` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708D30` | `0x708D5C` | `R31` | 44 | 3.58 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x708D6C` | `0x708D70` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708DAC` | `0x708DB0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708DF0` | `0x708E10` | `R31` | 32 | 3.18 | 0.31 | 8 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x708E20` | `0x708E24` | `R31` | 4 | 2.00 | 0.25 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708E34` | `0x708E38` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708E48` | `0x708E5C` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x708E6C` | `0x708E94` | `R31` | 40 | 3.60 | 0.20 | 10 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x708EA4` | `0x708EB8` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x708EC8` | `0x708ECC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708EDC` | `0x708EE0` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x708FF4` | `0x708FF8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709028` | `0x70905C` | `R31` | 52 | 3.50 | 0.31 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70906C` | `0x709070` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709080` | `0x7090AC` | `R31` | 44 | 3.54 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7090BC` | `0x7090C0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7090FC` | `0x709120` | `R31` | 36 | 3.51 | 0.22 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709130` | `0x709154` | `R31` | 36 | 3.39 | 0.28 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709164` | `0x709168` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709178` | `0x70917C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70918C` | `0x7091A0` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7091B0` | `0x7091D8` | `R31` | 40 | 3.67 | 0.20 | 10 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7091E8` | `0x7091FC` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70920C` | `0x709210` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709220` | `0x709224` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70933C` | `0x709340` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709370` | `0x7093A4` | `R31` | 52 | 3.45 | 0.31 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7093B4` | `0x7093B8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7093C8` | `0x7093F4` | `R31` | 44 | 3.46 | 0.30 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709404` | `0x709408` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709484` | `0x709488` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7094C8` | `0x7094E8` | `R31` | 32 | 3.24 | 0.31 | 8 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7094F8` | `0x7094FC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70950C` | `0x709510` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709520` | `0x709534` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709544` | `0x70956C` | `R31` | 40 | 3.67 | 0.20 | 10 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70957C` | `0x709590` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7095A0` | `0x7095A4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7095B4` | `0x7095B8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7096CC` | `0x7096D0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709700` | `0x709734` | `R31` | 52 | 3.40 | 0.33 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x709744` | `0x709748` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709758` | `0x709784` | `R31` | 44 | 3.42 | 0.32 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709794` | `0x709798` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7097E4` | `0x7097E8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709828` | `0x709838` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709848` | `0x709858` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709868` | `0x7098F4` | `R31` | 140 | 3.99 | 0.19 | 35 | 25 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709904` | `0x70997C` | `R31` | 120 | 3.97 | 0.18 | 30 | 22 | `unreached` | 4 naming word(s) | named by a word; a name is not a consumer |
| `0x70998C` | `0x709990` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7099EC` | `0x709A40` | `R31` | 84 | 4.10 | 0.20 | 21 | 15 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x709A70` | `0x709A74` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709A98` | `0x709AA8` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709AB8` | `0x709ABC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709B38` | `0x709B50` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709B60` | `0x709B64` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709C40` | `0x709C90` | `R31` | 80 | 3.72 | 0.31 | 20 | 12 | `unreached` | 4 naming word(s) | named by a word; a name is not a consumer |
| `0x709CE4` | `0x709CE8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709D18` | `0x709D88` | `R31` | 112 | 3.78 | 0.29 | 28 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x709D98` | `0x709D9C` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709DAC` | `0x709DB0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709DC0` | `0x709DC4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x709E00` | `0x709E04` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x709E44` | `0x709E54` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709E64` | `0x709E74` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709E84` | `0x709F10` | `R31` | 140 | 3.99 | 0.19 | 35 | 25 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x709F20` | `0x709F98` | `R31` | 120 | 4.02 | 0.18 | 30 | 22 | `unreached` | 4 naming word(s) | named by a word; a name is not a consumer |
| `0x709FA8` | `0x709FAC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A008` | `0x70A05C` | `R31` | 84 | 4.03 | 0.20 | 21 | 15 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x70A08C` | `0x70A090` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A0B4` | `0x70A0C4` | `R31` | 16 | 2.20 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A0D4` | `0x70A0D8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A154` | `0x70A16C` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A17C` | `0x70A180` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A250` | `0x70A290` | `R31` | 64 | 3.93 | 0.23 | 16 | 11 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A2E4` | `0x70A2E8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A338` | `0x70A364` | `R31` | 44 | 4.00 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A374` | `0x70A378` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A3B0` | `0x70A3DC` | `R31` | 44 | 4.00 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A3EC` | `0x70A3F0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A448` | `0x70A44C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A4A8` | `0x70A4CC` | `R31` | 36 | 3.51 | 0.22 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A4DC` | `0x70A54C` | `R31` | 112 | 3.78 | 0.30 | 28 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70A55C` | `0x70A570` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A580` | `0x70A584` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A5B0` | `0x70A5B4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A5C4` | `0x70A5C8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A5F4` | `0x70A604` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A614` | `0x70A624` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A634` | `0x70A6C0` | `R31` | 140 | 4.00 | 0.19 | 35 | 25 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A6D0` | `0x70A748` | `R31` | 120 | 3.98 | 0.18 | 30 | 22 | `unreached` | 4 naming word(s) | named by a word; a name is not a consumer |
| `0x70A758` | `0x70A75C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A7B8` | `0x70A80C` | `R31` | 84 | 4.10 | 0.20 | 21 | 15 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70A83C` | `0x70A840` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A884` | `0x70A894` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A8A4` | `0x70A8A8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70A924` | `0x70A93C` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70A94C` | `0x70A950` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70AA30` | `0x70AA80` | `R31` | 80 | 3.69 | 0.33 | 20 | 12 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70AAD4` | `0x70AAD8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70AB28` | `0x70AB54` | `R31` | 44 | 4.00 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70AB64` | `0x70AB68` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70ABA0` | `0x70ABCC` | `R31` | 44 | 4.00 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70ABDC` | `0x70ABE0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70AC1C` | `0x70AC40` | `R31` | 36 | 3.33 | 0.25 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70AC50` | `0x70ACC0` | `R31` | 112 | 3.75 | 0.29 | 28 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70ACD0` | `0x70ACD4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70ACFC` | `0x70AD00` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70AD10` | `0x70AD14` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70AD50` | `0x70AD54` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70AD94` | `0x70ADA4` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70ADB4` | `0x70ADC4` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70ADD4` | `0x70AE60` | `R31` | 140 | 4.07 | 0.19 | 35 | 25 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70AE70` | `0x70AEE8` | `R31` | 120 | 3.95 | 0.18 | 30 | 22 | `unreached` | 4 naming word(s) | named by a word; a name is not a consumer |
| `0x70AEF8` | `0x70AEFC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70AF58` | `0x70AFAC` | `R31` | 84 | 4.07 | 0.20 | 21 | 15 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70AFDC` | `0x70AFE0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B004` | `0x70B014` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B024` | `0x70B028` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B0A4` | `0x70B0BC` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B0CC` | `0x70B0D0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B1A0` | `0x70B1E0` | `R31` | 64 | 3.93 | 0.23 | 16 | 11 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B234` | `0x70B238` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B288` | `0x70B2B4` | `R31` | 44 | 4.00 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B2C4` | `0x70B2C8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B300` | `0x70B32C` | `R31` | 44 | 3.91 | 0.14 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B33C` | `0x70B340` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B3B4` | `0x70B3B8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B3F8` | `0x70B41C` | `R31` | 36 | 3.51 | 0.22 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B42C` | `0x70B49C` | `R31` | 112 | 3.78 | 0.29 | 28 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70B4AC` | `0x70B4C0` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B4D0` | `0x70B4D4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B500` | `0x70B504` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B514` | `0x70B518` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B548` | `0x70B558` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B568` | `0x70B578` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B588` | `0x70B614` | `R31` | 140 | 4.02 | 0.19 | 35 | 25 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B624` | `0x70B69C` | `R31` | 120 | 3.88 | 0.19 | 30 | 22 | `unreached` | 4 naming word(s) | named by a word; a name is not a consumer |
| `0x70B6AC` | `0x70B6B0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B70C` | `0x70B760` | `R31` | 84 | 4.12 | 0.20 | 21 | 15 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70B790` | `0x70B794` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B7B8` | `0x70B7C8` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B7D8` | `0x70B7DC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B858` | `0x70B870` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B880` | `0x70B884` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70B954` | `0x70B994` | `R31` | 64 | 3.93 | 0.23 | 16 | 11 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70B9E8` | `0x70B9EC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70BA3C` | `0x70BA68` | `R31` | 44 | 4.00 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70BA78` | `0x70BA7C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70BAB4` | `0x70BAE0` | `R31` | 44 | 4.00 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70BAF0` | `0x70BAF4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70BB30` | `0x70BB54` | `R31` | 36 | 3.33 | 0.25 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70BB64` | `0x70BBD4` | `R31` | 112 | 3.72 | 0.29 | 28 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70BBE4` | `0x70BBE8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70BC10` | `0x70BC14` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70BC24` | `0x70BC28` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70BC68` | `0x70BC6C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70BCAC` | `0x70BCBC` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70BCCC` | `0x70BD6C` | `R31` | 160 | 4.01 | 0.24 | 40 | 27 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70BD7C` | `0x70BDF4` | `R31` | 120 | 3.95 | 0.18 | 30 | 22 | `unreached` | 4 naming word(s) | named by a word; a name is not a consumer |
| `0x70BE04` | `0x70BE08` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70BE60` | `0x70BEB4` | `R31` | 84 | 4.03 | 0.20 | 21 | 15 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70BEE4` | `0x70BEE8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70BF0C` | `0x70BF1C` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70BF2C` | `0x70BF30` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70BFAC` | `0x70BFC4` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70BFD4` | `0x70BFD8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70C12C` | `0x70C130` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70C160` | `0x70C1D0` | `R31` | 112 | 3.75 | 0.29 | 28 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70C1E0` | `0x70C1E4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70C1F4` | `0x70C1F8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70C208` | `0x70C20C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70C24C` | `0x70C250` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70C338` | `0x70C348` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70C358` | `0x70C35C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70C460` | `0x70C470` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70C480` | `0x70C484` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70C580` | `0x70C584` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70C5C4` | `0x70C5D4` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70C5E4` | `0x70C684` | `R31` | 160 | 3.98 | 0.24 | 40 | 27 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70C694` | `0x70C70C` | `R31` | 120 | 3.95 | 0.18 | 30 | 22 | `unreached` | 4 naming word(s) | named by a word; a name is not a consumer |
| `0x70C71C` | `0x70C720` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70C778` | `0x70C7CC` | `R31` | 84 | 4.05 | 0.20 | 21 | 15 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x70C7FC` | `0x70C800` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70C824` | `0x70C834` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70C844` | `0x70C848` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70C8C4` | `0x70C8DC` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70C8EC` | `0x70C8F0` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70CA74` | `0x70CA78` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70CAC8` | `0x70CAF4` | `R31` | 44 | 4.00 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70CB04` | `0x70CB08` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70CB40` | `0x70CB6C` | `R31` | 44 | 4.00 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70CB7C` | `0x70CB80` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70CBE4` | `0x70CC08` | `R31` | 36 | 3.45 | 0.22 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70CC18` | `0x70CC88` | `R31` | 112 | 3.73 | 0.29 | 28 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70CC98` | `0x70CC9C` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70CCC4` | `0x70CCC8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70CCD8` | `0x70CCDC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70CD1C` | `0x70CD20` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70CD60` | `0x70CD70` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70CD80` | `0x70CD90` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70CDA0` | `0x70CE2C` | `R31` | 140 | 4.02 | 0.19 | 35 | 25 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70CE3C` | `0x70CEB4` | `R31` | 120 | 3.95 | 0.18 | 30 | 22 | `unreached` | 4 naming word(s) | named by a word; a name is not a consumer |
| `0x70CEC4` | `0x70CEC8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70CF24` | `0x70CF78` | `R31` | 84 | 4.10 | 0.20 | 21 | 15 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70CF98` | `0x70CF9C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70CFAC` | `0x70CFB0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70CFD4` | `0x70CFE4` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70CFF4` | `0x70CFF8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D074` | `0x70D08C` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70D09C` | `0x70D0A0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D170` | `0x70D1B0` | `R31` | 64 | 3.88 | 0.23 | 16 | 11 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70D204` | `0x70D208` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D258` | `0x70D284` | `R31` | 44 | 4.00 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70D294` | `0x70D298` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D2D0` | `0x70D2FC` | `R31` | 44 | 4.00 | 0.11 | 11 | 9 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70D30C` | `0x70D310` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D384` | `0x70D3A8` | `R31` | 36 | 3.51 | 0.22 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70D3B8` | `0x70D428` | `R31` | 112 | 3.74 | 0.30 | 28 | 18 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70D438` | `0x70D43C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D464` | `0x70D468` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D478` | `0x70D47C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D498` | `0x70D4A8` | `R31` | 16 | 2.66 | 0.38 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70D4B8` | `0x70D4D4` | `R31` | 28 | 3.70 | 0.11 | 7 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70D4E4` | `0x70D4E8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D5D8` | `0x70D5DC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D61C` | `0x70D62C` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70D63C` | `0x70D6B4` | `R31` | 120 | 3.91 | 0.21 | 30 | 21 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70D6C4` | `0x70D73C` | `R31` | 120 | 3.98 | 0.18 | 30 | 22 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x70D74C` | `0x70D750` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D7A8` | `0x70D7FC` | `R31` | 84 | 4.04 | 0.20 | 21 | 15 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70D81C` | `0x70D820` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D840` | `0x70D850` | `R31` | 16 | 2.38 | 0.50 | 4 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70D860` | `0x70D864` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D8E0` | `0x70D8F8` | `R31` | 24 | 3.19 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70D908` | `0x70D90C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D964` | `0x70D968` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70D9EC` | `0x70DA18` | `R31` | 44 | 3.76 | 0.23 | 11 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70DA28` | `0x70DA2C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70DA5C` | `0x70DA78` | `R31` | 28 | 3.58 | 0.14 | 7 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70DA88` | `0x70DA8C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70DAA4` | `0x70DABC` | `R31` | 24 | 3.62 | 0.12 | 6 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70DACC` | `0x70DB40` | `R31` | 116 | 3.85 | 0.28 | 29 | 19 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70DB50` | `0x70DB54` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70DB7C` | `0x70DB80` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70DB90` | `0x70DB94` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70DBD0` | `0x70DBD4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x70DC14` | `0x70DC38` | `R31` | 36 | 3.56 | 0.22 | 9 | 6 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70DCCC` | `0x70DCF4` | `R31` | 40 | 3.68 | 0.23 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70DD04` | `0x70DD08` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70DD68` | `0x70DD6C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x70DDAC` | `0x70DDD0` | `R31` | 36 | 3.56 | 0.22 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70DE34` | `0x70DE38` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70DEB0` | `0x70DEC4` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70DED4` | `0x70DEFC` | `R31` | 40 | 3.67 | 0.20 | 10 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70DF0C` | `0x70DF10` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70DF20` | `0x70DF5C` | `R31` | 60 | 3.28 | 0.43 | 15 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70DF6C` | `0x70DF94` | `R31` | 40 | 3.60 | 0.20 | 10 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70DFA4` | `0x70DFB8` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70DFC8` | `0x70DFCC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70E114` | `0x70E118` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70E128` | `0x70E12C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70E160` | `0x70E170` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E180` | `0x70E184` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70E1D4` | `0x70E1EC` | `R31` | 24 | 3.27 | 0.25 | 6 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E224` | `0x70E228` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70E260` | `0x70E264` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x70E2A4` | `0x70E2C8` | `R31` | 36 | 3.56 | 0.22 | 9 | 6 | `read` | play 080188AA; play 080188AC; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70E2E8` | `0x70E2FC` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E30C` | `0x70E310` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029C68 | no decoded reader and no naming word at half-open bounds |
| `0x70E320` | `0x70E334` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E344` | `0x70E348` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029664 | no decoded reader and no naming word at half-open bounds |
| `0x70E368` | `0x70E36C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E394` | `0x70E3AC` | `R31` | 24 | 3.54 | 0.12 | 6 | 5 | `read` | play 080188AE; play 08018F94; 3 naming word(s) | named by a word; a name is not a consumer |
| `0x70E3BC` | `0x70E3C0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E404` | `0x70E41C` | `R31` | 24 | 3.62 | 0.12 | 6 | 5 | `read` | play 080188AE; play 08018F94; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E42C` | `0x70E430` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E448` | `0x70E458` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `read` | play 0801890C; play 08029FEA; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E4D4` | `0x70E4E8` | `R31` | 20 | 2.68 | 0.40 | 5 | 3 | `read` | play 080188AC; play 080188AE; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E4F8` | `0x70E4FC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E57C` | `0x70E580` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70E590` | `0x70E594` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70E5DC` | `0x70E5E0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70E664` | `0x70E678` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E688` | `0x70E6A0` | `R31` | 24 | 3.27 | 0.25 | 6 | 4 | `read` | play 080188AA; play 080188AC; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E6B0` | `0x70E6B4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029664 | no decoded reader and no naming word at half-open bounds |
| `0x70E6C4` | `0x70E6C8` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E6D8` | `0x70E6DC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E71C` | `0x70E734` | `R31` | 24 | 3.62 | 0.12 | 6 | 5 | `read` | play 080188AE; play 08018F94; 3 naming word(s) | named by a word; a name is not a consumer |
| `0x70E744` | `0x70E748` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E758` | `0x70E78C` | `R31` | 52 | 3.53 | 0.33 | 13 | 8 | `read` | play 080188AE; play 0801890C; 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70E79C` | `0x70E7A0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E7CC` | `0x70E7D0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E7E0` | `0x70E814` | `R31` | 52 | 3.49 | 0.33 | 13 | 8 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E824` | `0x70E828` | `R31` | 4 | 2.00 | 0.25 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E854` | `0x70E858` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E868` | `0x70E87C` | `R31` | 20 | 2.46 | 0.50 | 5 | 2 | `read` | play 0801CDA2; play 08029664; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E88C` | `0x70E8DC` | `R31` | 80 | 3.93 | 0.25 | 20 | 14 | `read` | play 080188AE; play 0801890C; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E8EC` | `0x70E8F0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70E978` | `0x70E97C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70E994` | `0x70E9AC` | `R31` | 24 | 3.46 | 0.12 | 6 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E9BC` | `0x70E9D0` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70E9E0` | `0x70E9E4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70EA2C` | `0x70EA4C` | `R31` | 32 | 3.93 | 0.12 | 8 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70EA78` | `0x70EA7C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70EAA4` | `0x70EAA8` | `R31` | 4 | 1.50 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70EB9C` | `0x70EBA0` | `R31` | 4 | 0.81 | 0.75 | 1 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70EBF4` | `0x70EBFC` | `R31` | 8 | 1.06 | 0.75 | 2 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70EC40` | `0x70EC44` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70EC74` | `0x70EC9C` | `R31` | 40 | 3.35 | 0.35 | 10 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70ECAC` | `0x70ECB0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70ECC8` | `0x70ECEC` | `R31` | 36 | 3.40 | 0.22 | 9 | 6 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70ECFC` | `0x70ED50` | `R31` | 84 | 3.89 | 0.27 | 21 | 14 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70ED60` | `0x70ED64` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70ED90` | `0x70EDB0` | `R31` | 32 | 3.30 | 0.31 | 8 | 5 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70EDC0` | `0x70EDC8` | `R31` | 8 | 2.25 | 0.00 | 2 | 2 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70EE58` | `0x70EE68` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70EE78` | `0x70EE7C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70EECC` | `0x70EED0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70EF8C` | `0x70EF9C` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70EFAC` | `0x70EFB0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70F020` | `0x70F054` | `R31` | 52 | 3.54 | 0.31 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70F064` | `0x70F068` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70F078` | `0x70F08C` | `R31` | 20 | 3.11 | 0.30 | 5 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70F09C` | `0x70F0C4` | `R31` | 40 | 3.67 | 0.20 | 10 | 7 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70F0D4` | `0x70F0E8` | `R31` | 20 | 3.35 | 0.10 | 5 | 4 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70F0F8` | `0x70F0FC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70F10C` | `0x70F110` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70F19C` | `0x70F1A0` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70F238` | `0x70F23C` | `R31` | 4 | 2.00 | 0.25 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70F26C` | `0x70F27C` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70F28C` | `0x70F2C0` | `R31` | 52 | 3.54 | 0.31 | 13 | 8 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x70F2D0` | `0x70F2D4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70F2FC` | `0x70F328` | `R31` | 44 | 3.47 | 0.32 | 11 | 7 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70F338` | `0x70F33C` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x70F394` | `0x70F398` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 08029D18 | no decoded reader and no naming word at half-open bounds |
| `0x70F3F8` | `0x70F3FC` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70F434` | `0x70F444` | `R31` | 16 | 2.98 | 0.12 | 4 | 3 | `read` | play 0801890C; play 08029FEA; 1 naming word(s) | named by a word; a name is not a consumer |
| `0x70F464` | `0x70F468` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x70F4AC` | `0x70F4B0` | `R31` | 4 | 0.81 | 0.75 | 1 | 0 | `read` | play 0802B7CA | no decoded reader and no naming word at half-open bounds |
| `0x70F4C0` | `0x70F4C4` | `R31` | 4 | 2.00 | 0.00 | 1 | 1 | `read` | play 080188AC | no decoded reader and no naming word at half-open bounds |
| `0x710EF4` | `0x710FA3` | `R31` | 175 | 3.81 | 0.26 | 43 | 6 | `unreached` | 14 naming word(s) | named by a word; a name is not a consumer |
| `0x710FA3` | `0x71115B` | `R31` | 440 | 3.74 | 0.00 | 110 | 0 | `unreached` | 44 naming word(s) | named by a word; a name is not a consumer |
| `0x71115B` | `0x71121A` | `R31` | 191 | 3.66 | 0.01 | 47 | 0 | `unreached` | 19 naming word(s) | named by a word; a name is not a consumer |
| `0x71121A` | `0x711256` | `R31` | 60 | 3.38 | 0.00 | 15 | 0 | `unreached` | 6 naming word(s) | named by a word; a name is not a consumer |
| `0x711256` | `0x711274` | `R31` | 30 | 3.37 | 0.00 | 7 | 0 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x7122F8` | `0x7129A5` | `R23` | 1709 | 2.06 | 0.49 | 427 | 0 | `read` | play 0802A9C5; 4 naming word(s) | named by a word; a name is not a consumer |
| `0x7129A5` | `0x712FDC` | `R23` | 1591 | 1.20 | 0.78 | 397 | 0 | `read` | play 0802A9C5; 3 naming word(s) | named by a word; a name is not a consumer |
| `0x712FDC` | `0x71370C` | `R23` | 1840 | 2.10 | 0.54 | 460 | 4 | `read` | play 0802A88A; play 0802A894; 00019564 ldr [pc] 0x019574 = 0x08712FDC; 25 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71370C` | `0x7137CC` | `R23` | 192 | 3.39 | 0.19 | 48 | 20 | `named-data` | 000197F4 ldr [pc] 0x019AE8 = 0x0871370C; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7137CC` | `0x7137D8` | `R23` | 12 | 2.86 | 0.17 | 3 | 1 | `named-data` | 00019852 ldr [pc] 0x019AF8 = 0x087137CC; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7137D8` | `0x713AD8` | `R23` | 768 | 3.90 | 0.04 | 192 | 0 | `read` | play 0800BB63; 0000BB5C ldr [pc] 0x00BC78 = 0x087137D8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x713AD8` | `0x713FD8` | `R23` | 1280 | 3.93 | 0.03 | 320 | 0 | `named-data` | 0000BBD2 ldr [pc] 0x00BC84 = 0x08713AD8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x713FD8` | `0x714077` | `R23` | 159 | 2.79 | 0.02 | 39 | 0 | `named-data` | 0000BB9E ldr [pc] 0x00BC80 = 0x08713FD8; 4 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x714077` | `0x7144D8` | `R23` | 1121 | 3.92 | 0.03 | 280 | 0 | `unreached` | 3 naming word(s) | named by a word; a name is not a consumer |
| `0x7144D8` | `0x7180E9` | `R23` | 15377 | 3.83 | 0.04 | 3844 | 0 | `cited` | cited 08029178; play 0800BB57; 0000B57E ldr [pc] 0x00B800 = 0x087144D8; 48 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7180E9` | `0x718249` | `R23` | 352 | 2.99 | 0.01 | 88 | 0 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x718249` | `0x7196D8` | `R23` | 5263 | 3.80 | 0.01 | 1315 | 0 | `unreached` | 21 naming word(s) | named by a word; a name is not a consumer |
| `0x7196D8` | `0x7196DC` | `R23` | 4 | 2.00 | 0.25 | 1 | 0 | `read` | play 08051150; 0005114E ldr [pc] 0x051170 = 0x087196D8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7196DC` | `0x7196E0` | `R23` | 4 | 1.50 | 0.50 | 1 | 0 | `named-data` | 0001957C ldr [pc] 0x0195A4 = 0x087196DC; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7196E0` | `0x7198E4` | `R23` | 516 | 3.23 | 0.06 | 129 | 0 | `named-data` | 000195CA ldr [pc] 0x01979C = 0x087196E0; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x719C40` | `0x719C60` | `R23` | 32 | 1.19 | 0.75 | 8 | 0 | `named-data` | 00019800 ldr [pc] 0x019AEC = 0x08719C40; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x719C60` | `0x71B050` | `R23` | 5104 | 2.26 | 0.41 | 1276 | 0 | `read` | play 08019B14; play 08019BF8; 00019B0A ldr [pc] 0x019D10 = 0x08719C60; 66 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71B050` | `0x71B1A6` | `R23` | 342 | 2.14 | 0.39 | 85 | 0 | `unreached` | 5 naming word(s) | named by a word; a name is not a consumer |
| `0x71B1A6` | `0x71DA68` | `R23` | 10434 | 3.48 | 0.34 | 2608 | 0 | `unreached` | 12 naming word(s) | named by a word; a name is not a consumer |
| `0x71DA68` | `0x71DA88` | `R23` | 32 | 3.50 | 0.25 | 8 | 4 | `named-data` | 0001BE0A ldr [pc] 0x01C09C = 0x0871DA68; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71DA88` | `0x71DA98` | `R23` | 16 | 3.45 | 0.12 | 4 | 2 | `named-data` | 0003C11E ldr [pc] 0x03C1DC = 0x0871DA88; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71DA98` | `0x71DAF8` | `R23` | 96 | 2.97 | 0.53 | 24 | 0 | `read` | play 08019F4E; 00019D2A ldr [pc] 0x019FC0 = 0x0871DA98; 4 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71DAF8` | `0x71DD38` | `R23` | 576 | 4.92 | 0.13 | 144 | 96 | `read` | play 0800BAEC; play 0800BAF8; 000135A4 ldr [pc] 0x013618 = 0x0871DAF8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71DD4C` | `0x71DDC8` | `R23` | 124 | 2.60 | 0.45 | 31 | 0 | `named-data` | 0001A678 ldr [pc] 0x01A8E0 = 0x0871DD4C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71DDC8` | `0x71DE74` | `R23` | 172 | 2.64 | 0.44 | 43 | 0 | `named-data` | 0001A904 ldr [pc] 0x01AB70 = 0x0871DDC8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71DE74` | `0x71DEC4` | `R23` | 80 | 2.32 | 0.45 | 20 | 0 | `named-data` | 0001AD56 ldr [pc] 0x01AE18 = 0x0871DE74; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71DEC4` | `0x71DF70` | `R23` | 172 | 2.21 | 0.56 | 43 | 0 | `named-data` | 0001AE6E ldr [pc] 0x01B230 = 0x0871DEC4; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71DF70` | `0x71DF9C` | `R23` | 44 | 2.21 | 0.50 | 11 | 0 | `named-data` | 0001B30E ldr [pc] 0x01B4E0 = 0x0871DF70; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71DF9C` | `0x71E024` | `R23` | 136 | 2.52 | 0.49 | 34 | 0 | `named-data` | 0001B564 ldr [pc] 0x01B800 = 0x0871DF9C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E024` | `0x71E0A4` | `R23` | 128 | 2.59 | 0.33 | 32 | 0 | `named-data` | 0001B946 ldr [pc] 0x01BA8C = 0x0871E024; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E0A4` | `0x71E0F8` | `R23` | 84 | 1.75 | 0.68 | 21 | 0 | `named-data` | 0001BB64 ldr [pc] 0x01BDC4 = 0x0871E0A4; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E0F8` | `0x71E1B0` | `R23` | 184 | 2.46 | 0.48 | 46 | 0 | `named-data` | 0001BDE8 ldr [pc] 0x01C098 = 0x0871E0F8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E1B0` | `0x71E1E0` | `R23` | 48 | 2.09 | 0.50 | 12 | 0 | `named-data` | 0001C0CE ldr [pc] 0x01C3D8 = 0x0871E1B0; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E1E0` | `0x71E200` | `R23` | 32 | 2.10 | 0.38 | 8 | 0 | `named-data` | 0001C67A ldr [pc] 0x01C6C4 = 0x0871E1E0; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E200` | `0x71E228` | `R23` | 40 | 2.13 | 0.60 | 10 | 0 | `read` | play 0800C492; play 0800C496; 0001C774 ldr [pc] 0x01C8EC = 0x0871E200; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E234` | `0x71E254` | `R23` | 32 | 1.80 | 0.62 | 8 | 0 | `named-data` | 0001C92A ldr [pc] 0x01CB84 = 0x0871E234; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E254` | `0x71E258` | `R23` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 0001CF16 ldr [pc] 0x01CFF4 = 0x0871E254; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E274` | `0x71E630` | `R21` | 956 | 1.77 | 0.67 | 239 | 0 | `read` | play 08019CC3; play 0802A9C5; 5 naming word(s) | named by a word; a name is not a consumer |
| `0x71E630` | `0x71E984` | `R21` | 852 | 2.47 | 0.47 | 213 | 10 | `read` | play 08019B58; play 08019B62; 0001C93A ldr [pc] 0x01CB80 = 0x0871E630; 4 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E984` | `0x71E9A8` | `R21` | 36 | 2.99 | 0.17 | 9 | 3 | `read` | play 08019B58; play 08019B62; 0001C732 ldr [pc] 0x01C8E8 = 0x0871E984; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E9A8` | `0x71E9D8` | `R21` | 48 | 3.01 | 0.50 | 12 | 1 | `named-data` | 0001D0DA ldr [pc] 0x01D3FC = 0x0871E9A8; 3 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x71E9D8` | `0x720200` | `R21` | 6184 | 2.63 | 0.30 | 1546 | 1 | `named-data` | 0001D5F8 ldr [pc] 0x01D958 = 0x0871E9D8; 12 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x720200` | `0x7202E8` | `R21` | 232 | 2.08 | 0.38 | 58 | 0 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x7202E8` | `0x72033C` | `R21` | 84 | 3.17 | 0.17 | 21 | 7 | `named-data` | 0001E038 ldr [pc] 0x01E148 = 0x087202E8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72033C` | `0x720564` | `R21` | 552 | 3.37 | 0.26 | 138 | 0 | `named-data` | 000519E2 ldr [pc] 0x051A04 = 0x0872033C; 121 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x720564` | `0x7207E4` | `R21` | 640 | 4.46 | 0.10 | 160 | 120 | `named-data` | 000141EE ldr [pc] 0x01441C = 0x08720564; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72080C` | `0x72081C` | `R21` | 16 | 1.31 | 0.75 | 4 | 0 | `named-data` | 0001E4BC ldr [pc] 0x01E74C = 0x0872080C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72081C` | `0x72082C` | `R21` | 16 | 1.31 | 0.75 | 4 | 0 | `named-data` | 0001E790 ldr [pc] 0x01E9E8 = 0x0872081C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72084C` | `0x725018` | `R21` | 18380 | 3.42 | 0.40 | 4595 | 200 | `read` | play 08019C54; play 08019CAC; 0001FFFC ldr [pc] 0x02028C = 0x0872084C; 26 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x725018` | `0x725038` | `R21` | 32 | 3.39 | 0.22 | 8 | 4 | `named-data` | 0001ADE0 ldr [pc] 0x01AE1C = 0x08725018; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x725038` | `0x725048` | `R21` | 16 | 3.50 | 0.12 | 4 | 2 | `named-data` | 0003C352 ldr [pc] 0x03C40C = 0x08725038; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x725054` | `0x72507C` | `R21` | 40 | 0.57 | 0.90 | 10 | 0 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x72508C` | `0x725090` | `R21` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 00021270 ldr [pc] 0x02127C = 0x0872508C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x725098` | `0x72509E` | `R21` | 6 | 2.25 | 0.17 | 1 | 0 | `named-data` | 0005204A ldr [pc] 0x05206C = 0x08725098; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72509E` | `0x7251C8` | `R21` | 298 | 1.17 | 0.83 | 74 | 0 | `named-data` | 000215B0 ldr [pc] 0x021728 = 0x0872509E; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7251C8` | `0x7251D8` | `R21` | 16 | 0.67 | 0.88 | 4 | 0 | `named-data` | 0002177E ldr [pc] 0x02182C = 0x087251C8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7251D8` | `0x725749` | `R21` | 1393 | 1.47 | 0.69 | 348 | 0 | `named-data` | 0002183A ldr [pc] 0x021870 = 0x087251D8; 5 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x725749` | `0x72A690` | `R21` | 20295 | 0.93 | 0.86 | 5073 | 0 | `read` | play 08019C54; play 08019CAC; 14 naming word(s) | named by a word; a name is not a consumer |
| `0x72A690` | `0x72A6A8` | `R21` | 24 | 3.60 | 0.00 | 6 | 5 | `named-data` | 0001C0EC ldr [pc] 0x01C3DC = 0x0872A690; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72A6A8` | `0x72A6B4` | `R21` | 12 | 3.25 | 0.00 | 3 | 2 | `named-data` | 0003BDD8 ldr [pc] 0x03BF18 = 0x0872A6A8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72A6B4` | `0x72A6F8` | `R21` | 68 | 3.45 | 0.38 | 17 | 0 | `named-data` | 0002187A ldr [pc] 0x021BB8 = 0x0872A6B4; 5 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72A6F8` | `0x72BF06` | `R21` | 6158 | 1.98 | 0.65 | 1539 | 0 | `named-data` | 0002211A ldr [pc] 0x0222DC = 0x0872A6F8; 15 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72BF06` | `0x72BF34` | `R21` | 46 | 3.24 | 0.17 | 11 | 0 | `named-data` | 000222F8 ldr [pc] 0x022600 = 0x0872BF06; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72BF34` | `0x72BF64` | `R21` | 48 | 3.19 | 0.17 | 12 | 4 | `named-data` | 00022368 ldr [pc] 0x02261C = 0x0872BF34; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72BF64` | `0x72BF94` | `R21` | 48 | 3.19 | 0.17 | 12 | 4 | `named-data` | 00022376 ldr [pc] 0x022620 = 0x0872BF64; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72BFA0` | `0x72BFA4` | `R21` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 00022646 ldr [pc] 0x022674 = 0x0872BFA0; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72BFA4` | `0x72BFA8` | `R21` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 000227D0 ldr [pc] 0x0228FC = 0x0872BFA4; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72BFA8` | `0x72C34C` | `R21` | 932 | 2.17 | 0.69 | 233 | 1 | `named-data` | 00022AF8 ldr [pc] 0x022D38 = 0x0872BFA8; 4 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72C358` | `0x72C378` | `R21` | 32 | 2.25 | 0.38 | 8 | 0 | `read` | play 08023F6C; play 08023F72; 00023F64 ldr [pc] 0x02402C = 0x0872C358; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72C388` | `0x72C38C` | `R24` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 000244BE ldr [pc] 0x024570 = 0x0872C388; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72C394` | `0x72C3B8` | `R24` | 36 | 1.61 | 0.69 | 9 | 0 | `read` | play 0802478E; play 080247F0; 000246EE ldr [pc] 0x024948 = 0x0872C394; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72C3B8` | `0x72C461` | `R24` | 169 | 2.10 | 0.45 | 42 | 0 | `named-data` | 0002470A ldr [pc] 0x024950 = 0x0872C3B8; 6 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x72C461` | `0x72D6B8` | `R24` | 4695 | 1.82 | 0.74 | 1173 | 0 | `unreached` | 20 naming word(s) | named by a word; a name is not a consumer |
| `0x72D6B8` | `0x7315A8` | `R24` | 16112 | 3.38 | 0.36 | 4028 | 194 | `read` | play 08019B58; play 08019B62; 0002472C ldr [pc] 0x024954 = 0x0872D6B8; 16 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7315A8` | `0x7315D8` | `R24` | 48 | 3.55 | 0.21 | 12 | 6 | `named-data` | 0001BF76 ldr [pc] 0x01C0A4 = 0x087315A8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x74F08C` | `0x7501EC` | `R30` | 4448 | 1.17 | 0.79 | 1112 | 0 | `named-data` | 000293E8 ldr [pc] 0x0295C4 = 0x0874F08C; 8 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7501EC` | `0x750204` | `R30` | 24 | 3.04 | 0.21 | 6 | 3 | `named-data` | 000293B2 ldr [pc] 0x0295C0 = 0x087501EC; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x750204` | `0x75021C` | `R30` | 24 | 2.94 | 0.17 | 6 | 2 | `named-data` | 00029410 ldr [pc] 0x0295D0 = 0x08750204; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75021C` | `0x75023C` | `R30` | 32 | 1.32 | 0.69 | 8 | 0 | `named-data` | 00029708 ldr [pc] 0x029848 = 0x0875021C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x750270` | `0x75027C` | `R30` | 12 | 1.73 | 0.50 | 3 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x75029C` | `0x75043C` | `R25` | 416 | 1.66 | 0.66 | 104 | 0 | `read` | play 0802A408; play 0802A5C6; 12 naming word(s) | named by a word; a name is not a consumer |
| `0x7504CC` | `0x7520D4` | `R25` | 7176 | 1.50 | 0.67 | 1794 | 0 | `read` | play 0802A844; play 0802A8D4; 0002A840 ldr [pc] 0x02A9FC = 0x087504CC; 12 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7520D4` | `0x752D28` | `R25` | 3156 | 1.96 | 0.57 | 789 | 7 | `named-data` | 0001C472 ldr [pc] 0x01C6B4 = 0x087520D4; 6 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x752D28` | `0x752D4C` | `R25` | 36 | 3.15 | 0.17 | 9 | 3 | `named-data` | 0001C4CA ldr [pc] 0x01C6B8 = 0x08752D28; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x752D68` | `0x752DAC` | `R30` | 68 | 2.53 | 0.37 | 17 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x752DF8` | `0x752E18` | `R30` | 32 | 1.57 | 0.09 | 8 | 0 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x752E28` | `0x752E68` | `R30` | 64 | 2.28 | 0.28 | 16 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x752E78` | `0x752E9C` | `R30` | 36 | 2.45 | 0.36 | 9 | 0 | `named-data` | 0002B60A ldr [pc] 0x02B6EC = 0x08752E78; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x752EB8` | `0x752ED4` | `R30` | 28 | 1.09 | 0.71 | 7 | 0 | `read` | play 0802B74C; play 0802B750 | no decoded reader and no naming word at half-open bounds |
| `0x752EF0` | `0x752F8C` | `R26` | 156 | 3.43 | 0.23 | 39 | 16 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x752F8C` | `0x753008` | `R26` | 124 | 3.41 | 0.42 | 31 | 5 | `named-data` | 0005196A ldr [pc] 0x05198C = 0x08752F8C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x753008` | `0x753A08` | `R26` | 2560 | 2.84 | 0.49 | 640 | 19 | `named-data` | 0002B9C2 ldr [pc] 0x02BC00 = 0x08753008; 9 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x753A10` | `0x753A14` | `R26` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 0002BD9E ldr [pc] 0x02BDC8 = 0x08753A10; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x753A14` | `0x753A18` | `R26` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 0002BDCC ldr [pc] 0x02BDF0 = 0x08753A14; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x753A18` | `0x7548E8` | `R26` | 3792 | 3.99 | 0.49 | 948 | 2 | `named-data` | 0002BEF0 ldr [pc] 0x02C05C = 0x08753A18; 4 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7548E8` | `0x754910` | `R26` | 40 | 2.69 | 0.35 | 10 | 0 | `read` | play 0802C0BC; play 0802C0EC; 0002C0BA ldr [pc] 0x02C194 = 0x087548E8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x754958` | `0x75495C` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x754978` | `0x75497C` | `R27` | 4 | 2.00 | 0.25 | 1 | 0 | `read` | play 0802C824; play 0802C84C | no decoded reader and no naming word at half-open bounds |
| `0x75497C` | `0x754A1C` | `R27` | 160 | 1.71 | 0.62 | 40 | 0 | `read` | play 08019CC3; play 0802C7D2; 0002C7CC ldr [pc] 0x02C904 = 0x0875497C; 3 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x754A1C` | `0x756A04` | `R27` | 8168 | 1.96 | 0.60 | 2042 | 36 | `read` | play 08019B58; play 08019B62; 0002C7CA ldr [pc] 0x02C900 = 0x08754A1C; 4 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x756A04` | `0x756A2C` | `R27` | 40 | 3.51 | 0.23 | 10 | 6 | `read` | play 0802CC2C; play 0802CC5A; 0001B662 ldr [pc] 0x01B810 = 0x08756A04; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x756A2C` | `0x756A4C` | `R27` | 32 | 2.55 | 0.53 | 8 | 3 | `read` | play 0802CBE7; 0002CBDA ldr [pc] 0x02CD10 = 0x08756A2C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x756A74` | `0x756A94` | `R30` | 32 | 2.10 | 0.38 | 8 | 0 | `read` | play 0802D13C; play 0802D142 | no decoded reader and no naming word at half-open bounds |
| `0x756AA4` | `0x756AE4` | `R30` | 64 | 1.81 | 0.53 | 16 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x756B10` | `0x756B2C` | `R30` | 28 | 1.09 | 0.71 | 7 | 0 | `read` | play 0802D558; play 0802D562 | no decoded reader and no naming word at half-open bounds |
| `0x756B3C` | `0x756B58` | `R30` | 28 | 1.09 | 0.71 | 7 | 0 | `read` | play 0802D6E4; play 0802D6EA | no decoded reader and no naming word at half-open bounds |
| `0x756B74` | `0x7571F4` | `R30` | 1664 | 2.14 | 0.52 | 416 | 0 | `read` | play 08019CC3; 0002D840 ldr [pc] 0x02DAF4 = 0x08756B74; 13 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7571F4` | `0x757284` | `R30` | 144 | 3.37 | 0.21 | 36 | 15 | `read` | play 08019B58; play 08019B62; 0002D866 ldr [pc] 0x02DAF0 = 0x087571F4; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x757284` | `0x7572AC` | `R30` | 40 | 2.03 | 0.60 | 10 | 0 | `named-data` | 0002DBEA ldr [pc] 0x02DE0C = 0x08757284; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7572C8` | `0x7572F0` | `R30` | 40 | 1.41 | 0.50 | 10 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x757324` | `0x757344` | `R30` | 32 | 2.10 | 0.38 | 8 | 0 | `named-data` | 0002E20E ldr [pc] 0x02E25C = 0x08757324; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x757354` | `0x757374` | `R30` | 32 | 2.04 | 0.56 | 8 | 0 | `read` | play 0802E2C2; play 0802E2C8 | no decoded reader and no naming word at half-open bounds |
| `0x7573A0` | `0x7579B8` | `R30` | 1560 | 0.87 | 0.85 | 390 | 0 | `named-data` | 0002E6B2 ldr [pc] 0x02E814 = 0x087573A0; 11 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7579B8` | `0x757A30` | `R30` | 120 | 3.08 | 0.17 | 30 | 10 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x757A50` | `0x757A74` | `R30` | 36 | 2.74 | 0.53 | 9 | 3 | `read` | play 0802F4CC; play 0802F4F9 | no decoded reader and no naming word at half-open bounds |
| `0x757A84` | `0x757AA4` | `R30` | 32 | 2.25 | 0.38 | 8 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x757AE8` | `0x757B04` | `R30` | 28 | 3.22 | 0.32 | 7 | 2 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x757B58` | `0x757B5C` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x757B5C` | `0x757B64` | `R30` | 8 | 1.06 | 0.75 | 2 | 0 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x757B64` | `0x757EE8` | `R30` | 900 | 4.13 | 0.10 | 225 | 0 | `named-data` | 00030216 ldr [pc] 0x030370 = 0x08757B64; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x758190` | `0x758194` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 000303C6 ldr [pc] 0x030444 = 0x08758190; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x758194` | `0x7581C8` | `R30` | 52 | 2.83 | 0.54 | 13 | 4 | `named-data` | 0003045A ldr [pc] 0x0304DC = 0x08758194; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7581C8` | `0x7581CC` | `R30` | 4 | 1.50 | 0.50 | 1 | 0 | `named-data` | 0003053A ldr [pc] 0x030608 = 0x087581C8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7581E8` | `0x7581EC` | `R30` | 4 | 2.00 | 0.00 | 1 | 1 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7581F4` | `0x7581FC` | `R30` | 8 | 1.06 | 0.75 | 2 | 0 | `named-data` | 00030A0C ldr [pc] 0x030AA4 = 0x087581F4; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7581FC` | `0x7585EC` | `R30` | 1008 | 7.37 | 0.04 | 252 | 9 | `named-data` | 00030AE0 ldr [pc] 0x030B18 = 0x087581FC; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7585EC` | `0x759154` | `R30` | 2920 | 7.71 | 0.02 | 730 | 4 | `unreached` | 7 naming word(s) | named by a word; a name is not a consumer |
| `0x75917C` | `0x75918C` | `R30` | 16 | 1.81 | 0.38 | 4 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7591A8` | `0x7591B8` | `R30` | 16 | 1.19 | 0.75 | 4 | 0 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7591C8` | `0x7591D8` | `R30` | 16 | 1.19 | 0.75 | 4 | 0 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7591D8` | `0x7591DC` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x7591EC` | `0x759210` | `R30` | 36 | 2.74 | 0.53 | 9 | 3 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x759220` | `0x75922C` | `R30` | 12 | 1.58 | 0.67 | 3 | 1 | `unreached` | 2 naming word(s) | named by a word; a name is not a consumer |
| `0x75925C` | `0x7592AC` | `R30` | 80 | 2.32 | 0.53 | 20 | 0 | `named-data` | 00033016 ldr [pc] 0x0331D4 = 0x0875925C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7592BC` | `0x7592DC` | `R30` | 32 | 2.34 | 0.56 | 8 | 3 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7592DC` | `0x75930C` | `R30` | 48 | 1.71 | 0.75 | 12 | 0 | `named-data` | 000333AC ldr [pc] 0x0335B4 = 0x087592DC; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75931C` | `0x759320` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 00033890 ldr [pc] 0x0338FC = 0x0875931C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x759320` | `0x759324` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `read` | play 0804E89C; play 0804E8F0; 0004E896 ldr [pc] 0x04E8FC = 0x08759320; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x759334` | `0x759354` | `R30` | 32 | 1.19 | 0.75 | 8 | 0 | `named-data` | 000339C6 ldr [pc] 0x033B3C = 0x08759334; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75939C` | `0x7593BC` | `R30` | 32 | 2.10 | 0.38 | 8 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7593CC` | `0x7593D8` | `R30` | 12 | 1.78 | 0.58 | 3 | 0 | `named-data` | 00052586 ldr [pc] 0x0525A8 = 0x087593CC; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7593D8` | `0x7593E4` | `R30` | 12 | 2.36 | 0.33 | 3 | 2 | `named-data` | 00033F92 ldr [pc] 0x0340F4 = 0x087593D8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7593E4` | `0x7593E8` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `read` | play 08034132; play 0803426C; 00034268 ldr [pc] 0x034280 = 0x087593E4; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7593E8` | `0x7593EC` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 0003446A ldr [pc] 0x034568 = 0x087593E8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7593FC` | `0x759418` | `R30` | 28 | 1.38 | 0.46 | 7 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x759440` | `0x759460` | `R30` | 32 | 2.10 | 0.38 | 8 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x759480` | `0x7594A0` | `R30` | 32 | 1.75 | 0.50 | 8 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7594B0` | `0x7594D0` | `R30` | 32 | 2.10 | 0.38 | 8 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x7594EC` | `0x7594F0` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x759510` | `0x759620` | `R30` | 272 | 1.96 | 0.49 | 68 | 0 | `unreached` | 8 naming word(s) | named by a word; a name is not a consumer |
| `0x759680` | `0x75A0E9` | `R30` | 2665 | 1.12 | 0.81 | 666 | 0 | `named-data` | 00035A18 ldr [pc] 0x035B88 = 0x08759688; 6 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75A22F` | `0x75A2A0` | `R30` | 113 | 0.61 | 0.85 | 28 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x75A6A8` | `0x75A6DC` | `R30` | 52 | 3.57 | 0.17 | 13 | 4 | `named-data` | 00035A0C ldr [pc] 0x035B84 = 0x0875A6A8; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75A714` | `0x75A718` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `read` | play 08035F0E; 00035F0A ldr [pc] 0x035F84 = 0x0875A714; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75A738` | `0x75A73C` | `R29` | 4 | 1.50 | 0.50 | 1 | 0 | `named-data` | 000363C4 ldr [pc] 0x036438 = 0x0875A738; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75A73C` | `0x75A7A0` | `R29` | 100 | 2.52 | 0.47 | 25 | 1 | `named-data` | 0003645A ldr [pc] 0x03670C = 0x0875A73C; 3 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75A7A0` | `0x75A7A4` | `R29` | 4 | 2.00 | 0.25 | 1 | 0 | `read` | play 08036994; 0003698C ldr [pc] 0x036A10 = 0x0875A7A0; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75A7A4` | `0x75F7AC` | `R29` | 20488 | 1.65 | 0.75 | 5122 | 0 | `read` | play 08036AE9; play 08036BB6; 00036A62 ldr [pc] 0x036D6C = 0x0875A7A4; 11 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75F7AC` | `0x75F7F4` | `R29` | 72 | 2.94 | 0.33 | 18 | 6 | `read` | play 08036AD4; play 08036AD6; 00036A8C ldr [pc] 0x036D74 = 0x0875F7AC; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75F7F4` | `0x75F808` | `R29` | 20 | 3.17 | 0.10 | 5 | 3 | `read` | play 08036F48; 00036D86 ldr [pc] 0x036E54 = 0x0875F7F4; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x75F808` | `0x76174C` | `R29` | 8004 | 2.93 | 0.12 | 2001 | 24 | `named-data` | 00036FC2 ldr [pc] 0x037238 = 0x0875F808; 9 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76174C` | `0x762270` | `R29` | 2852 | 1.90 | 0.60 | 713 | 3 | `named-data` | 00037084 ldr [pc] 0x037244 = 0x0876174C; 13 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x762270` | `0x76ACC0` | `R29` | 35408 | 3.28 | 0.38 | 8852 | 80 | `named-data` | 0001B2F6 ldr [pc] 0x01B4DC = 0x08762270; 23 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76ACC0` | `0x76ACF0` | `R29` | 48 | 2.52 | 0.54 | 12 | 3 | `named-data` | 0001A7EC ldr [pc] 0x01A8EC = 0x0876ACC0; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76ACF0` | `0x76BA2C` | `R29` | 3388 | 2.34 | 0.49 | 847 | 56 | `named-data` | 000374F0 ldr [pc] 0x037880 = 0x0876ACF0; 3 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76BA2C` | `0x76BA3C` | `R29` | 16 | 3.62 | 0.12 | 4 | 2 | `named-data` | 0001A698 ldr [pc] 0x01A8E4 = 0x0876BA2C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76BA3C` | `0x76BA40` | `R29` | 4 | 2.00 | 0.25 | 1 | 0 | `read` | play 080379CC; 000379C8 ldr [pc] 0x037A24 = 0x0876BA3C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76BA40` | `0x76BA78` | `R29` | 56 | 1.83 | 0.68 | 14 | 2 | `read` | play 080190C4; 00037A88 ldr [pc] 0x037B40 = 0x0876BA40; 3 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76BA78` | `0x76CBD8` | `R29` | 4448 | 0.76 | 0.87 | 1112 | 0 | `named-data` | 00037C74 ldr [pc] 0x037D48 = 0x0876BA78; 21 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76CBD8` | `0x76CCB0` | `R29` | 216 | 4.05 | 0.18 | 54 | 22 | `named-data` | 00037C60 ldr [pc] 0x037D44 = 0x0876CBD8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76CCB0` | `0x76CCD4` | `R29` | 36 | 2.56 | 0.28 | 9 | 0 | `named-data` | 00037D8E ldr [pc] 0x037E98 = 0x0876CCB0; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76CCE4` | `0x76DFF8` | `R20` | 4884 | 2.04 | 0.62 | 1221 | 0 | `unreached` | 17 naming word(s) | named by a word; a name is not a consumer |
| `0x76DFF8` | `0x76E0B8` | `R20` | 192 | 3.73 | 0.28 | 48 | 20 | `named-data` | 00037F24 ldr [pc] 0x038184 = 0x0876DFF8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76E0C4` | `0x76E0DC` | `R20` | 24 | 0.50 | 0.92 | 6 | 0 | `named-data` | 00038714 ldr [pc] 0x0387D4 = 0x0876E0C4; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76E0DC` | `0x76E264` | `R20` | 392 | 1.57 | 0.54 | 98 | 0 | `named-data` | 00038800 ldr [pc] 0x038A64 = 0x0876E0DC; 14 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x76E2F4` | `0x7703AC` | `R20` | 8376 | 1.69 | 0.54 | 2094 | 0 | `unreached` | 42 naming word(s) | named by a word; a name is not a consumer |
| `0x7703AC` | `0x770CF4` | `R20` | 2376 | 1.90 | 0.27 | 594 | 0 | `unreached` | 30 naming word(s) | named by a word; a name is not a consumer |
| `0x770CF4` | `0x770D0C` | `R20` | 24 | 2.94 | 0.17 | 6 | 2 | `named-data` | 00038826 ldr [pc] 0x038A6C = 0x08770CF4; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x770D0C` | `0x7710FC` | `R20` | 1008 | 3.51 | 0.38 | 252 | 70 | `named-data` | 000388EE ldr [pc] 0x038A7C = 0x08770D0C; 2 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x7710FC` | `0x77110C` | `R20` | 16 | 3.16 | 0.19 | 4 | 2 | `named-data` | 0001A924 ldr [pc] 0x01AB74 = 0x087710FC; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77110C` | `0x77AD10` | `R20` | 39940 | 2.75 | 0.47 | 9985 | 0 | `named-data` | 00038B98 ldr [pc] 0x038DD4 = 0x0877110C; 30 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77AD10` | `0x77ADD0` | `R20` | 192 | 3.47 | 0.17 | 48 | 16 | `named-data` | 00038B30 ldr [pc] 0x038DCC = 0x0877AD10; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77ADD8` | `0x77AE58` | `R20` | 128 | 3.12 | 0.33 | 32 | 3 | `named-data` | 000391C0 ldr [pc] 0x039210 = 0x0877ADD8; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77AE58` | `0x77AE68` | `R20` | 16 | 2.16 | 0.38 | 4 | 0 | `unreached` | 1 naming word(s) | named by a word; a name is not a consumer |
| `0x77AE84` | `0x77AEC0` | `R30` | 60 | 1.87 | 0.50 | 15 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x77AED0` | `0x77AF0C` | `R30` | 60 | 1.87 | 0.50 | 15 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x77AF34` | `0x77AF38` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x77AF38` | `0x77AF44` | `R30` | 12 | 3.42 | 0.08 | 3 | 2 | `named-data` | 000395AA ldr [pc] 0x039744 = 0x0877AF38; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77AF4C` | `0x77AF50` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 000398AE ldr [pc] 0x0398C8 = 0x0877AF4C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77AF78` | `0x77AF98` | `R30` | 32 | 2.44 | 0.56 | 8 | 3 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x77AF98` | `0x77AFC0` | `R30` | 40 | 1.54 | 0.75 | 10 | 0 | `named-data` | 00039B10 ldr [pc] 0x039BCC = 0x0877AF98; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77AFDC` | `0x77B03C` | `R30` | 96 | 2.54 | 0.56 | 24 | 9 | `named-data` | 00039C8E ldr [pc] 0x039D8C = 0x0877AFDC; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77B04C` | `0x77B070` | `R30` | 36 | 2.74 | 0.53 | 9 | 3 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x77B0B0` | `0x77B0D0` | `R30` | 32 | 2.55 | 0.53 | 8 | 3 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x77B0D0` | `0x77B0F8` | `R30` | 40 | 1.51 | 0.72 | 10 | 0 | `named-data` | 0003A63A ldr [pc] 0x03A694 = 0x0877B0D0; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77B16C` | `0x77B170` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `named-data` | 0003BD22 ldr [pc] 0x03BD84 = 0x0877B16C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77B180` | `0x77B1B0` | `R30` | 48 | 2.09 | 0.50 | 12 | 0 | `named-data` | 0003BDA6 ldr [pc] 0x03BF14 = 0x0877B180; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77B1C0` | `0x77B1E4` | `R30` | 36 | 1.89 | 0.67 | 9 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x77B200` | `0x77B254` | `R28` | 84 | 2.51 | 0.44 | 21 | 0 | `named-data` | 0003C0EA ldr [pc] 0x03C1D8 = 0x0877B200; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77B254` | `0x77B2A8` | `R28` | 84 | 2.51 | 0.44 | 21 | 0 | `named-data` | 0003C206 ldr [pc] 0x03C2F0 = 0x0877B254; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77B2A8` | `0x77C41C` | `R28` | 4468 | 3.01 | 0.53 | 1117 | 67 | `named-data` | 0003C31E ldr [pc] 0x03C408 = 0x0877B2A8; 3 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77C41C` | `0x77C430` | `R28` | 20 | 3.34 | 0.25 | 5 | 2 | `named-data` | 0003C23A ldr [pc] 0x03C2F4 = 0x0877C41C; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77C430` | `0x77C450` | `R28` | 32 | 2.21 | 0.28 | 8 | 0 | `named-data` | 0003C470 ldr [pc] 0x03C4D8 = 0x0877C430; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77C450` | `0x77C47C` | `R28` | 44 | 2.11 | 0.41 | 11 | 0 | `named-data` | 0003C580 ldr [pc] 0x03C674 = 0x0877C450; 1 naming word(s) | code loads a word naming this row; its bytes have no layout |
| `0x77C48C` | `0x77C490` | `R30` | 4 | 2.00 | 0.25 | 1 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x77C4D4` | `0x77C4F4` | `R30` | 32 | 2.00 | 0.41 | 8 | 0 | `unreached` | none | no decoded reader and no naming word at half-open bounds |
| `0x77C510` | `0x77C5A4` | `R30` | 148 | 4.70 | 0.28 | 37 | 3 | `read` | play 08003C7C; play 08003CC2; 9 naming word(s) | named by a word; a name is not a consumer |
