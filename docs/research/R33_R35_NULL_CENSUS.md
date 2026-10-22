# R33, R34 and R35: one reader-bounded pointer array and a per-row null

Measured 2026-10-19 from ROM sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`. Data addresses are
file offsets, instruction addresses are bus addresses `0x08...`, and every quote is a
Thumb decode of the bytes at that address (`tools/research/thumb_annotate.py`). The three
regions are `incbin_census.REGIONS` R33-R35 over the still-raw rows of
`docs/research/RAW_REMAINDER.csv`.

R33 was PATH-100-006's raw-labeled rows (named by a Thumb literal with more than one
loader, or above its 12-window control), R34 its singleton-literal rows, R35 its rows
that no literal names but a word or a literal-named table does. One row is bounded by
its reader and becomes source; the other 160 keep a measured null below.

## Totals

| region | rows | bytes | definition |
|---|---|---|---|
| `R33` | 73 | 12264 | PATH-100-006 raw-labeled rows (a cited consumer, no extent) |
| `R34` | 16 | 14608 | PATH-100-006 rows named only by singleton literals |
| `R35` | 71 | 63001 | PATH-100-006 rows no literal names, but a word or a literal-named table does |
| decoded | 1 | 12 | `0x6B8028`, section below |
| **measured** | **161** | **89,885** | R33 74 / 12,276 before the decode |

`python tools\research\raw_remainder.py` prints
`total 3345 row(s) 586568 B  gate raw-data 586568 B  EXACT` after the decode, and
R33 reads 73 rows / 12,264 B; the region sums in this table are that run's.

## What was searched

| channel | instrument | denominator | result on these rows |
|---|---|---|---|
| decoded `ldr` literal load in transcribed code | `tools/research/consumer_search.py` `literal_loads` | 2,783 ledger Thumb/ARM rows / 292,722 B | 167 loads into 34 R33 rows; 0 into R34 or R35 |
| Thumb/ARM branch or Thumb function pointer | `tools/research/thumb_bodies.py` `entries` | 2,785 walked rows / 130,513 Thumb instructions | 0 |
| class-table method slot | `thumb_bodies.method_entries` | 1,002 slots over 150 class bases | 0 |
| pointer-table word with bit 0 set | `thumb_bodies.pointer_entries` | 124 carrier rows / 392 grid words | 0 |
| Thumb-1 literal-shaped halfword over the whole image | `unknown_consumer_search.loaders` | 117,008 Thumb + 618 ARM literal sites | 244 R33, 24 R34 and 25 R35 naming literals; the site class below |
| word-aligned word over the whole image | `consumer_search.sites` | 2,097,152 words | 2,060 R33, 272 R34 and 801 R35 naming words |

Every count above is half-open over each row's own span (`[start, end)`), not over
the interval that contains the rows: the gaps between rows are other rows' bytes
(P-738). `unknown_consumer_search.loaders()` tests an inclusive high bound; the runs
here subtract one byte from the end so a row's end byte is not counted (P-725), which
is why a row can carry fewer naming literals than its `UNMAPPED_ROWS.md` run line.

## Where the naming evidence actually sits

| region | naming literals | sites in a ledger code row | sites in an INCBIN slice | sites in a generated or transcribed data row | rows with a decoded reader |
|---|---|---|---|---|---|
| `R33` | 244 | 167 | 21 | 138 | 34 |
| `R34` | 24 | 0 | 6 | 18 | 0 |
| `R35` | 25 | 0 | 26 | 0 | 0 |

R34 and R35 have no naming literal in a code row: every one sits in a container or
JCALG1 payload, so the channel that put those rows in their region names bytes with
data and not with a consumer (P-721, P-732). R33's 34 reader rows are the only rows
in the three regions with a decoded `ldr`.

Region membership is the census span's, keyed on the row's start: a span can name
some of its rows and none of the others, so a row with no naming literal at its own
half-open bounds still belongs to the region its start falls in. The table reports
each row's own evidence.

## `0x6B8028`: a 3-entry pointer array, decoded

Reader body `0x080141CA..0x080141E8`, a loop over a table whose base is the literal
`0x080141CC ldr r6, [pc, #0x248]` (pool file `0x014418` = `0x086B8028`):

    080141CA 0024       movs r4, #0
    080141D6 2002       lsls r0, r4, #8
    080141D8 4019       adds r0, r0, r5
    080141DA C119       adds r1, r0, r7
    080141DC A000       lsls r0, r4, #2
    080141DE 3058       ldr r0, [r6, r0]
    080141E0 29F0AEFB   bl 0x0803D940
    080141E4 0134       adds r4, #1
    080141E6 032C       cmp r4, #3
    080141E8 F5DB       blt 0x080141D6

Stride 4 and count 3 are the reader's own arithmetic and compare; 3 x 4 = 12 B, the
row's exact extent (`0x6B8028..0x6B8034`, zero residual). The three words are
`0x086B7FAC`, `0x086B7F3C` and `0x086B7ED8`, each inside
`endrom_container_run_6b7e8c`, whose bytes carry no label at them; the callee
`0x0803D940` reads a word at the target (`cmp r3,#0` / `cmp r3,#1` / `cmp r3,#2`)
and a second word as a size, so the targets are 8-byte headers, but that layout is
the target's and not this row's.

The row becomes three numeric `DCD` words, emitted by
`tools/research/pointer_rows.py` (`NUMERIC_MEASURED`), which refuses unless the
operands reproduce the retail bytes. Gate accounting: source 7,775,916 ->
7,775,928 B, raw-data 586,580 -> 586,568 B, `DIGEST MATCH`. Falsifier: an access to
`[base+0xC]` or any
indexed read that leaves the 3-entry range, which the `cmp r4,#3` above excludes.

## The per-row null

Each line: file offsets, bytes, entropy, zero-byte share, word-aligned words inside
the row holding an in-image address, ledger class, naming literals with their site
classes and word-aligned naming words outside the row, the decoded reader, and why
the row stays raw. `none` means no decoded instruction in the four reader channels
names a byte of the row at the denominators above.

### R33 (73 rows / 12,264 B)

| start | end | bytes | ent | zero | words | class | naming | readers | null |
|---|---|---|---|---|---|---|---|---|---|
| `0x17A9AC` | `0x17AAAC` | 256 | 6.63 | 0.06 | 0 | `graphics` | L8 c0/i0/d8, W160 | none | no decoded reader; the naming literals sit in data |
| `0x17AAAC` | `0x17ABAC` | 256 | 6.68 | 0.04 | 1 | `graphics` | L28 c0/i3/d25, W320 | none | no decoded reader; the naming literals sit in data |
| `0x17ABAC` | `0x17ACA4` | 248 | 6.61 | 0.06 | 0 | `graphics` | L8 c0/i1/d7, W81 | none | no decoded reader; the naming literals sit in data |
| `0x17ACA4` | `0x17ADA4` | 256 | 6.68 | 0.04 | 1 | `graphics` | L19 c0/i2/d17, W320 | none | no decoded reader; the naming literals sit in data |
| `0x17ADA4` | `0x17AEA4` | 256 | 6.63 | 0.06 | 0 | `graphics` | L3 c0/i0/d4, W80 | none | no decoded reader; the naming literals sit in data |
| `0x17AEA4` | `0x17AFA4` | 256 | 6.63 | 0.06 | 0 | `graphics` | L4 c0/i0/d4, W80 | none | no decoded reader; the naming literals sit in data |
| `0x17AFA4` | `0x17B1B0` | 524 | 6.67 | 0.07 | 20 | `graphics` | L16 c0/i2/d14, W242 | none | no decoded reader; the naming literals sit in data |
| `0x1911D8` | `0x191214` | 60 | 5.35 | 0.12 | 0 | `graphics` | L3 c0/i0/d3, W76 | none | no decoded reader; the naming literals sit in data |
| `0x191214` | `0x191250` | 60 | 4.94 | 0.17 | 0 | `graphics` | L5 c0/i0/d6, W77 | none | no decoded reader; the naming literals sit in data |
| `0x191250` | `0x19125C` | 12 | 3.08 | 0.0 | 2 | `graphics` | L1 c0/i0/d2, W1 | none | no decoded reader; the naming literals sit in data |
| `0x19125C` | `0x191288` | 44 | 4.37 | 0.2 | 0 | `graphics` | L2 c0/i0/d2, W21 | none | no decoded reader; the naming literals sit in data |
| `0x191288` | `0x1912C8` | 64 | 4.95 | 0.12 | 4 | `graphics` | L1 c0/i0/d1, W21 | none | no decoded reader; the naming literals sit in data |
| `0x19AEAC` | `0x19B0AC` | 512 | 7.11 | 0.06 | 5 | `graphics` | L1 c0/i0/d1, W21 | none | no decoded reader; the naming literals sit in data |
| `0x19B0AC` | `0x19B104` | 88 | 5.12 | 0.12 | 0 | `graphics` | L1 c0/i0/d1, W61 | none | no decoded reader; the naming literals sit in data |
| `0x19B104` | `0x19B130` | 44 | 4.77 | 0.16 | 0 | `graphics` | L1 c0/i0/d1, W30 | none | no decoded reader; the naming literals sit in data |
| `0x19B130` | `0x19B178` | 72 | 4.97 | 0.1 | 6 | `graphics` | L5 c0/i3/d2, W30 | none | no decoded reader; the naming literals sit in data |
| `0x1BFAA4` | `0x1BFD60` | 700 | 7.14 | 0.04 | 27 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x1BFD60` | `0x1BFD9C` | 60 | 5.31 | 0.12 | 0 | `graphics` | L4 c0/i0/d4, W56 | none | no decoded reader; the naming literals sit in data |
| `0x1BFD9C` | `0x1BFDF8` | 92 | 5.13 | 0.11 | 7 | `graphics` | L3 c0/i2/d1, W56 | none | no decoded reader; the naming literals sit in data |
| `0x1D2618` | `0x1D2650` | 56 | 4.9 | 0.14 | 0 | `graphics` | L0 c0/i0/d0, W5 | none | no decoded reader; naming words are data |
| `0x1D2650` | `0x1D268C` | 60 | 5.2 | 0.15 | 0 | `graphics` | L1 c0/i0/d1, W10 | none | no decoded reader; the naming literals sit in data |
| `0x1D268C` | `0x1D2711` | 133 | 5.69 | 0.11 | 1 | `graphics` | L2 c0/i0/d2, W25 | none | no decoded reader; the naming literals sit in data |
| `0x1D2711` | `0x1D2754` | 67 | 5.38 | 0.1 | 0 | `graphics` | L1 c0/i0/d1, W3 | none | no decoded reader; the naming literals sit in data |
| `0x1E41E0` | `0x1E42B0` | 208 | 6.46 | 0.07 | 0 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x1E42B0` | `0x1E4448` | 408 | 6.83 | 0.05 | 1 | `graphics` | L1 c0/i0/d2, W10 | none | no decoded reader; the naming literals sit in data |
| `0x1E4448` | `0x1E4518` | 208 | 6.46 | 0.06 | 1 | `graphics` | L1 c0/i0/d1, W8 | none | no decoded reader; the naming literals sit in data |
| `0x1E4518` | `0x1E45E8` | 208 | 6.46 | 0.07 | 0 | `graphics` | L1 c0/i0/d1, W4 | none | no decoded reader; the naming literals sit in data |
| `0x1E45E8` | `0x1E46B8` | 208 | 6.46 | 0.07 | 0 | `graphics` | L1 c0/i0/d1, W2 | none | no decoded reader; the naming literals sit in data |
| `0x1E46B8` | `0x1E4780` | 200 | 6.48 | 0.04 | 0 | `graphics` | L1 c0/i0/d1, W6 | none | no decoded reader; the naming literals sit in data |
| `0x1F880C` | `0x1F88A4` | 152 | 5.91 | 0.16 | 1 | `graphics` | L1 c0/i0/d2, W8 | none | no decoded reader; the naming literals sit in data |
| `0x21FC4C` | `0x21FD7C` | 304 | 6.97 | 0.03 | 4 | `graphics` | L0 c0/i0/d0, W17 | none | no decoded reader; naming words are data |
| `0x21FD7C` | `0x22002C` | 688 | 7.37 | 0.04 | 0 | `graphics` | L4 c0/i1/d3, W45 | none | no decoded reader; the naming literals sit in data |
| `0x22002C` | `0x220498` | 1132 | 7.52 | 0.03 | 0 | `graphics` | L1 c0/i0/d1, W19 | none | no decoded reader; the naming literals sit in data |
| `0x220498` | `0x2205DC` | 324 | 6.69 | 0.02 | 20 | `graphics` | L1 c0/i0/d1, W7 | none | no decoded reader; the naming literals sit in data |
| `0x260EA8` | `0x260F1C` | 116 | 5.86 | 0.09 | 0 | `graphics` | L0 c0/i0/d0, W1 | none | no decoded reader; naming words are data |
| `0x260F1C` | `0x261004` | 232 | 5.93 | 0.09 | 0 | `graphics` | L1 c0/i0/d1, W4 | none | no decoded reader; the naming literals sit in data |
| `0x261004` | `0x2610EC` | 232 | 5.91 | 0.09 | 0 | `graphics` | L1 c0/i0/d1, W3 | none | no decoded reader; the naming literals sit in data |
| `0x2B5F94` | `0x2B5FA0` | 12 | 0.82 | 0.83 | 0 | `graphics` | L1 c0/i1/d0, W2 | none | no decoded reader; the naming literals sit in data |
| `0x3C33F8` | `0x3C34B0` | 184 | 2.68 | 0.52 | 0 | `unknown` | L3 c10/i0/d3, W3 | 10 (`0x08012978` `ldr r0, [pc, #0x394]`) | fixed fields +4/+8/+0xC/+0x14/+0x94, no stride and no compare |
| `0x3C34B0` | `0x3C34D0` | 32 | 1.2 | 0.69 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x08013356` `ldr r2, [pc, #0x1c]`) | stride 8 proven at `0x08013356`, index is a byte field, no compare |
| `0x6B8048` | `0x6B806C` | 36 | 3.15 | 0.44 | 2 | `unknown` | L4 c22/i0/d1, W4 | 22 (`0x08014CC8` `ldr r0, [pc, #0x3d8]`) | reads the row+0x10 word as a base; the 0x68 stride at `0x08015176` belongs to another array, no compare |
| `0x6B806C` | `0x6B8070` | 4 | 2.0 | 0.25 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x08015A04` `ldr r1, [pc, #0x1c]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B8070` | `0x6B8074` | 4 | 2.0 | 0.25 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x08015A72` `ldr r5, [pc, #0x28]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B8074` | `0x6B8078` | 4 | 2.0 | 0.25 | 0 | `unknown` | L1 c2/i0/d0, W1 | 2 (`0x08015B92` `ldr r0, [pc, #0x20]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B8080` | `0x6B8088` | 8 | 3.0 | 0.0 | 0 | `unknown` | L1 c3/i0/d0, W1 | 3 (`0x08015BC0` `ldr r2, [pc, #0x2bc]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B8088` | `0x6B8090` | 8 | 0.54 | 0.88 | 0 | `unknown` | L5 c4/i0/d1, W5 | 4 (`0x0802090C` `ldr r3, [pc, #0x190]`) | 8-byte record base at `0x08020912`, index is a byte field, no compare |
| `0x6B8090` | `0x6B8098` | 8 | 1.3 | 0.62 | 0 | `unknown` | L12 c11/i0/d1, W12 | 11 (`0x0801C87A` `ldr r0, [pc, #0x7c]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B8098` | `0x6B80A0` | 8 | 1.06 | 0.75 | 0 | `unknown` | L17 c15/i0/d2, W17 | 15 (`0x08012A46` `ldr r0, [pc, #0x2cc]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B80A0` | `0x6B80A8` | 8 | 1.06 | 0.75 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x08018B98` `ldr r0, [pc, #0x48]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B80A8` | `0x6B80C0` | 24 | 1.61 | 0.62 | 0 | `unknown` | L2 c2/i0/d0, W2 | 2 (`0x08019982` `ldr r0, [pc, #0x178]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B80C0` | `0x6B80D0` | 16 | 1.67 | 0.62 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x080213D2` `ldr r0, [pc, #0x1b0]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B80D0` | `0x6B80D8` | 8 | 1.55 | 0.62 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x0801B368` `ldr r0, [pc, #0x178]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B80D8` | `0x6B80E0` | 8 | 1.55 | 0.62 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x080294CC` `ldr r0, [pc, #0x104]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B80E0` | `0x6B80E8` | 8 | 1.55 | 0.62 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x0803717E` `ldr r1, [pc, #0xdc]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B80E8` | `0x6B80F0` | 8 | 1.55 | 0.62 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x0802DDB2` `ldr r0, [pc, #0x68]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B80F0` | `0x6B8100` | 16 | 1.67 | 0.62 | 0 | `unknown` | L1 c2/i0/d0, W1 | 2 (`0x080375DA` `ldr r0, [pc, #0x2c0]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B8100` | `0x6B8108` | 8 | 1.55 | 0.62 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x08037CD2` `ldr r0, [pc, #0x78]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B8108` | `0x6B8110` | 8 | 1.06 | 0.75 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x08038536` `ldr r0, [pc, #0x1cc]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B8110` | `0x6B8118` | 8 | 1.55 | 0.62 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x08038860` `ldr r1, [pc, #0x20c]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B8118` | `0x6B8120` | 8 | 1.55 | 0.62 | 0 | `unknown` | L2 c2/i0/d0, W2 | 2 (`0x08038D82` `ldr r1, [pc, #0x60]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B8120` | `0x6B8124` | 4 | 2.0 | 0.25 | 0 | `unknown` | L1 c2/i0/d0, W1 | 2 (`0x080162DC` `ldr r0, [pc, #0x20]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B8124` | `0x6B814C` | 40 | 3.54 | 0.17 | 5 | `unknown` | L1 c5/i0/d0, W1 | 5 (`0x08016324` `ldr r5, [pc, #0x194]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x6B82EC` | `0x6B87FC` | 1296 | 5.05 | 0.35 | 0 | `unknown` | L37 c55/i6/d5, W37 | 55 (`0x08000170` `ldr r2, [pc, #0x250]`) | stride 24 proven at `0x08000170`, u16 field at +2 indexes a pointer table; 1296 = 54 x 24 but no compare on the index |
| `0x6F9EC4` | `0x6F9EC8` | 4 | 2.0 | 0.25 | 0 | `unknown` | L2 c2/i0/d0, W2 | 2 (`0x080178EA` `ldr r5, [pc, #0xe4]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x73198C` | `0x7319CC` | 64 | 1.25 | 0.0 | 0 | `unknown` | L1 c5/i0/d0, W1 | 5 (`0x08024ABA` `ldr r1, [pc, #0x290]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x732350` | `0x732360` | 16 | 1.31 | 0.75 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x080250DE` `ldr r0, [pc, #0x240]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x7325E8` | `0x7325F8` | 16 | 1.31 | 0.75 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x08026098` `ldr r0, [pc, #0x10c]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x74C92C` | `0x74CA24` | 248 | 4.71 | 0.08 | 57 | `unknown` | L0 c0/i0/d0, W1 | none | no decoded reader; naming words are data |
| `0x74CA24` | `0x74CA2C` | 8 | 2.41 | 0.38 | 1 | `unknown` | L2 c3/i0/d0, W2 | 3 (`0x08004A8A` `ldr r0, [pc, #0x78]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x74CB04` | `0x74CF24` | 1056 | 2.34 | 0.43 | 4 | `unknown` | L0 c0/i0/d0, W0 | none | no decoded reader; no naming word at half-open bounds |
| `0x74CF24` | `0x74CF28` | 4 | 2.0 | 0.25 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x08026DB2` `ldr r0, [pc, #0x28]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x74CF28` | `0x74D02C` | 260 | 1.89 | 0.65 | 0 | `unknown` | L3 c5/i0/d0, W3 | 5 (`0x08026E00` `ldr r5, [pc, #0x178]`) | reader loads the row, no stride, count or terminator in the reading body |
| `0x74D02C` | `0x74D03C` | 16 | 1.94 | 0.38 | 0 | `unknown` | L1 c1/i0/d0, W1 | 1 (`0x08026F4E` `ldr r2, [pc, #0x40]`) | reader loads the row, no stride, count or terminator in the reading body |

### R34 (16 rows / 14,608 B)

| start | end | bytes | ent | zero | words | class | naming | readers | null |
|---|---|---|---|---|---|---|---|---|---|
| `0x17F330` | `0x17F48C` | 348 | 6.59 | 0.08 | 0 | `graphics` | L1 c0/i0/d1, W8 | none | no decoded reader; the naming literals sit in data |
| `0x180694` | `0x180B40` | 1196 | 7.52 | 0.02 | 0 | `graphics` | L3 c0/i1/d2, W27 | none | no decoded reader; the naming literals sit in data |
| `0x1A90A8` | `0x1A9570` | 1224 | 6.88 | 0.07 | 0 | `graphics` | L3 c0/i2/d1, W32 | none | no decoded reader; the naming literals sit in data |
| `0x1C7C48` | `0x1C7F24` | 732 | 7.14 | 0.04 | 33 | `graphics` | L1 c0/i0/d1, W1 | none | no decoded reader; the naming literals sit in data |
| `0x2176EC` | `0x2177B4` | 200 | 5.19 | 0.17 | 0 | `graphics` | L1 c0/i0/d1, W10 | none | no decoded reader; the naming literals sit in data |
| `0x21E878` | `0x21EE20` | 1448 | 7.46 | 0.05 | 0 | `graphics` | L4 c0/i2/d2, W73 | none | no decoded reader; the naming literals sit in data |
| `0x225FB8` | `0x226514` | 1372 | 7.41 | 0.05 | 15 | `graphics` | L1 c0/i0/d1, W2 | none | no decoded reader; the naming literals sit in data |
| `0x259A88` | `0x259BE4` | 348 | 6.21 | 0.13 | 1 | `graphics` | L0 c0/i0/d0, W6 | none | no decoded reader; naming words are data |
| `0x274598` | `0x274D84` | 2028 | 7.51 | 0.04 | 4 | `graphics` | L2 c0/i1/d1, W8 | none | no decoded reader; the naming literals sit in data |
| `0x279ABC` | `0x279EEC` | 1072 | 6.67 | 0.07 | 47 | `graphics` | L1 c0/i0/d1, W2 | none | no decoded reader; the naming literals sit in data |
| `0x29B308` | `0x29B320` | 24 | 3.42 | 0.33 | 0 | `other-compressed` | L1 c0/i0/d1, W3 | none | no decoded reader; the naming literals sit in data |
| `0x3BBBB0` | `0x3BBE70` | 704 | 4.45 | 0.17 | 0 | `unknown` | L2 c0/i0/d2, W23 | none | no decoded reader; the naming literals sit in data |
| `0x74312C` | `0x743264` | 312 | 3.47 | 0.58 | 5 | `unknown` | L1 c0/i0/d1, W4 | none | no decoded reader; the naming literals sit in data |
| `0x746844` | `0x746C74` | 1072 | 4.27 | 0.53 | 32 | `unknown` | L1 c0/i0/d1, W9 | none | no decoded reader; the naming literals sit in data |
| `0x7473E4` | `0x74798C` | 1448 | 3.96 | 0.52 | 8 | `unknown` | L1 c0/i0/d1, W14 | none | no decoded reader; the naming literals sit in data |
| `0x747E64` | `0x74829C` | 1080 | 4.12 | 0.48 | 16 | `unknown` | L1 c0/i0/d1, W10 | none | no decoded reader; the naming literals sit in data |

### R35 (71 rows / 63,001 B)

| start | end | bytes | ent | zero | words | class | naming | readers | null |
|---|---|---|---|---|---|---|---|---|---|
| `0x17BCCC` | `0x17C0DC` | 1040 | 7.47 | 0.03 | 0 | `graphics` | L0 c0/i0/d0, W5 | none | no decoded reader; naming words are data |
| `0x17C700` | `0x17CA58` | 856 | 7.34 | 0.04 | 2 | `graphics` | L0 c0/i0/d0, W5 | none | no decoded reader; naming words are data |
| `0x17D1C8` | `0x17D340` | 376 | 6.8 | 0.05 | 1 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x17DAB0` | `0x17DE24` | 884 | 7.35 | 0.04 | 0 | `graphics` | L0 c0/i0/d0, W12 | none | no decoded reader; naming words are data |
| `0x17E44C` | `0x17E5BC` | 368 | 6.68 | 0.08 | 0 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x18206C` | `0x1823F8` | 908 | 7.41 | 0.03 | 0 | `graphics` | L0 c0/i0/d0, W13 | none | no decoded reader; naming words are data |
| `0x182DCC` | `0x183090` | 708 | 7.23 | 0.04 | 0 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x1837DC` | `0x183DB4` | 1496 | 7.48 | 0.02 | 2 | `graphics` | L0 c0/i0/d0, W7 | none | no decoded reader; naming words are data |
| `0x1886AC` | `0x188A20` | 884 | 7.34 | 0.04 | 0 | `graphics` | L0 c0/i0/d0, W6 | none | no decoded reader; naming words are data |
| `0x189C34` | `0x189F7C` | 840 | 7.36 | 0.03 | 0 | `graphics` | L0 c0/i0/d0, W3 | none | no decoded reader; naming words are data |
| `0x18B334` | `0x18BA74` | 1856 | 7.51 | 0.04 | 31 | `graphics` | L1 c0/i1/d0, W1 | none | no decoded reader; the naming literals sit in data |
| `0x18C638` | `0x18CCAC` | 1652 | 7.49 | 0.04 | 21 | `graphics` | L0 c0/i0/d0, W3 | none | no decoded reader; naming words are data |
| `0x18D808` | `0x18DE14` | 1548 | 7.44 | 0.04 | 21 | `graphics` | L1 c0/i1/d0, W1 | none | no decoded reader; the naming literals sit in data |
| `0x190240` | `0x190650` | 1040 | 7.39 | 0.03 | 22 | `graphics` | L1 c0/i1/d0, W3 | none | no decoded reader; the naming literals sit in data |
| `0x19FC04` | `0x1A0248` | 1604 | 7.02 | 0.05 | 24 | `graphics` | L1 c0/i1/d0, W7 | none | no decoded reader; the naming literals sit in data |
| `0x1A2434` | `0x1A2E70` | 2620 | 7.36 | 0.04 | 47 | `graphics` | L2 c0/i2/d0, W5 | none | no decoded reader; the naming literals sit in data |
| `0x1B2DAC` | `0x1B2F1C` | 368 | 6.74 | 0.07 | 11 | `graphics` | L0 c0/i0/d0, W1 | none | no decoded reader; naming words are data |
| `0x1C0CB4` | `0x1C0D68` | 180 | 5.95 | 0.12 | 0 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x1C1630` | `0x1C1964` | 820 | 7.25 | 0.04 | 34 | `graphics` | L0 c0/i0/d0, W6 | none | no decoded reader; naming words are data |
| `0x1C2FF4` | `0x1C30A8` | 180 | 5.93 | 0.14 | 0 | `graphics` | L0 c0/i0/d0, W7 | none | no decoded reader; naming words are data |
| `0x1C3A70` | `0x1C3BF8` | 392 | 6.19 | 0.06 | 35 | `graphics` | L0 c0/i0/d0, W5 | none | no decoded reader; naming words are data |
| `0x1E24F4` | `0x1E2B58` | 1636 | 7.03 | 0.05 | 2 | `graphics` | L2 c0/i2/d0, W16 | none | no decoded reader; the naming literals sit in data |
| `0x1EA2D8` | `0x1EA714` | 1084 | 6.75 | 0.06 | 13 | `graphics` | L0 c0/i0/d0, W17 | none | no decoded reader; naming words are data |
| `0x1F5028` | `0x1F50FC` | 212 | 6.23 | 0.09 | 0 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x1FB060` | `0x1FB348` | 744 | 6.86 | 0.05 | 8 | `graphics` | L1 c0/i1/d0, W5 | none | no decoded reader; the naming literals sit in data |
| `0x2113E4` | `0x211664` | 640 | 6.89 | 0.09 | 11 | `graphics` | L1 c0/i2/d0, W7 | none | no decoded reader; the naming literals sit in data |
| `0x2119F8` | `0x211AD8` | 224 | 5.76 | 0.11 | 10 | `graphics` | L2 c0/i2/d0, W6 | none | no decoded reader; the naming literals sit in data |
| `0x2133A4` | `0x213514` | 368 | 6.75 | 0.09 | 0 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x215F98` | `0x216308` | 880 | 6.91 | 0.07 | 11 | `graphics` | L1 c0/i1/d0, W2 | none | no decoded reader; the naming literals sit in data |
| `0x21DD88` | `0x21E0D0` | 840 | 7.36 | 0.05 | 10 | `graphics` | L0 c0/i0/d0, W1 | none | no decoded reader; naming words are data |
| `0x225024` | `0x2250B4` | 144 | 5.2 | 0.2 | 0 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x236470` | `0x2369D8` | 1384 | 6.76 | 0.07 | 23 | `graphics` | L1 c0/i1/d0, W1 | none | no decoded reader; the naming literals sit in data |
| `0x24451C` | `0x2445D4` | 184 | 6.04 | 0.11 | 0 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x252BEC` | `0x253558` | 2412 | 7.79 | 0.02 | 4 | `graphics` | L0 c0/i0/d0, W10 | none | no decoded reader; naming words are data |
| `0x25C6E4` | `0x25C814` | 304 | 5.96 | 0.07 | 27 | `graphics` | L0 c0/i0/d0, W1 | none | no decoded reader; naming words are data |
| `0x25D5A0` | `0x25DF64` | 2500 | 6.93 | 0.11 | 45 | `graphics` | L1 c0/i1/d0, W10 | none | no decoded reader; the naming literals sit in data |
| `0x25EB64` | `0x25F584` | 2592 | 6.83 | 0.14 | 62 | `graphics` | L6 c0/i6/d0, W3 | none | no decoded reader; the naming literals sit in data |
| `0x262F74` | `0x2637A0` | 2092 | 7.46 | 0.04 | 40 | `graphics` | L0 c0/i0/d0, W2 | none | no decoded reader; naming words are data |
| `0x263EAC` | `0x2645E0` | 1844 | 7.1 | 0.08 | 29 | `graphics` | L2 c0/i2/d0, W8 | none | no decoded reader; the naming literals sit in data |
| `0x26F6C0` | `0x26FD70` | 1712 | 7.05 | 0.05 | 2 | `graphics` | L0 c0/i0/d0, W16 | none | no decoded reader; naming words are data |
| `0x277C08` | `0x27823C` | 1588 | 7.34 | 0.05 | 27 | `graphics` | L1 c0/i1/d0, W29 | none | no decoded reader; the naming literals sit in data |
| `0x285C18` | `0x285E20` | 520 | 7.12 | 0.07 | 1 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x2B2998` | `0x2B2A10` | 120 | 5.13 | 0.24 | 1 | `graphics` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x2B31E8` | `0x2B3E6C` | 3204 | 7.21 | 0.08 | 31 | `graphics` | L1 c0/i1/d0, W3 | none | no decoded reader; the naming literals sit in data |
| `0x2B5F1C` | `0x2B5F28` | 12 | 1.21 | 0.75 | 0 | `graphics` | L0 c0/i0/d0, W1 | none | no decoded reader; naming words are data |
| `0x3192A5` | `0x3192A8` | 3 | 0.0 | 1.0 | 0 | `unknown` | L0 c0/i0/d0, W0 | none | no decoded reader; no naming word at half-open bounds |
| `0x36D18A` | `0x36D18C` | 2 | 0.0 | 1.0 | 0 | `unknown` | L0 c0/i0/d0, W0 | none | no decoded reader; no naming word at half-open bounds |
| `0x6F3BC8` | `0x6F3C30` | 104 | 3.82 | 0.18 | 0 | `unknown` | L0 c0/i0/d0, W15 | none | no decoded reader; naming words are data |
| `0x7434B0` | `0x743E68` | 2488 | 4.75 | 0.42 | 6 | `unknown` | L0 c0/i0/d0, W22 | none | no decoded reader; naming words are data |
| `0x744EF0` | `0x74535C` | 1132 | 4.46 | 0.44 | 40 | `unknown` | L0 c0/i0/d0, W12 | none | no decoded reader; naming words are data |
| `0x745798` | `0x74606C` | 2260 | 4.16 | 0.53 | 10 | `unknown` | L0 c0/i0/d0, W31 | none | no decoded reader; naming words are data |
| `0x748668` | `0x748788` | 288 | 3.7 | 0.46 | 11 | `unknown` | L0 c0/i0/d0, W3 | none | no decoded reader; naming words are data |
| `0x748860` | `0x7488E4` | 132 | 2.82 | 0.61 | 3 | `unknown` | L0 c0/i0/d0, W2 | none | no decoded reader; naming words are data |
| `0x7489D4` | `0x748A38` | 100 | 2.52 | 0.61 | 2 | `unknown` | L0 c0/i0/d0, W2 | none | no decoded reader; naming words are data |
| `0x748AC8` | `0x748C58` | 400 | 3.48 | 0.57 | 4 | `unknown` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x748F34` | `0x74901C` | 232 | 3.23 | 0.55 | 5 | `unknown` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x749118` | `0x749178` | 96 | 2.79 | 0.53 | 4 | `unknown` | L0 c0/i0/d0, W2 | none | no decoded reader; naming words are data |
| `0x7491D0` | `0x7495C8` | 1016 | 3.64 | 0.53 | 4 | `unknown` | L0 c0/i0/d0, W12 | none | no decoded reader; naming words are data |
| `0x74980C` | `0x749CBC` | 1200 | 3.84 | 0.51 | 15 | `unknown` | L0 c0/i0/d0, W15 | none | no decoded reader; naming words are data |
| `0x749F1C` | `0x74A820` | 2308 | 3.77 | 0.52 | 18 | `unknown` | L0 c0/i0/d0, W29 | none | no decoded reader; naming words are data |
| `0x74AA98` | `0x74AC18` | 384 | 3.94 | 0.38 | 30 | `unknown` | L0 c0/i0/d0, W5 | none | no decoded reader; naming words are data |
| `0x74ACB4` | `0x74B0F8` | 1092 | 3.96 | 0.59 | 6 | `unknown` | L0 c0/i0/d0, W13 | none | no decoded reader; naming words are data |
| `0x74B8B4` | `0x74BA44` | 400 | 3.77 | 0.41 | 13 | `unknown` | L0 c0/i0/d0, W5 | none | no decoded reader; naming words are data |
| `0x74BB40` | `0x74BC88` | 328 | 2.94 | 0.57 | 5 | `unknown` | L0 c0/i0/d0, W6 | none | no decoded reader; naming words are data |
| `0x74BCF8` | `0x74BFB4` | 700 | 4.33 | 0.51 | 9 | `unknown` | L0 c0/i0/d0, W4 | none | no decoded reader; naming words are data |
| `0x74C58C` | `0x74C660` | 212 | 3.07 | 0.6 | 5 | `unknown` | L0 c0/i0/d0, W2 | none | no decoded reader; naming words are data |
| `0x74C804` | `0x74C884` | 128 | 2.82 | 0.56 | 2 | `unknown` | L0 c0/i0/d0, W2 | none | no decoded reader; naming words are data |
| `0x74CA3C` | `0x74CA60` | 36 | 2.45 | 0.36 | 0 | `unknown` | L0 c0/i0/d0, W0 | none | no decoded reader; no naming word at half-open bounds |
| `0x74CA70` | `0x74CA90` | 32 | 2.25 | 0.38 | 0 | `unknown` | L0 c0/i0/d0, W0 | none | no decoded reader; no naming word at half-open bounds |
| `0x74CAA0` | `0x74CAC4` | 36 | 2.45 | 0.36 | 0 | `unknown` | L0 c0/i0/d0, W0 | none | no decoded reader; no naming word at half-open bounds |
| `0x74CAD4` | `0x74CAF4` | 32 | 1.96 | 0.41 | 0 | `unknown` | L0 c0/i0/d0, W0 | none | no decoded reader; no naming word at half-open bounds |


## What the null does not cover

- A reader that computes a row address from a base register and an offset is
  invisible to the pc-relative literal, branch, method-slot and pointer channels. The
  map-container header tables name R35's graphics rows from the bytes directly after
  them, which makes that shape the most likely real access path for those rows.
- Code outside the ledger's 2,783 transcribed Thumb/ARM rows is outside every
  denominator above; the whole-image literal sweeps shrink that gap but the site
  class is the ledger's.
- No row here has a runtime read watch, so a consumer that only exists at run time
  is not measured.

## Sweep read verdict (generated: docs/research/REGION_READS.csv)

One line per raw row of `R33`, `R34`, `R35`, from `tools/research/region_readers.py`.
The offsets are the byte offsets inside the row that the sweep's reads used, and the
share is the part of the row those reads reached. The null above each row stays its
measured null; this line is the read verdict on it.

| start | end | bytes | region | class | verdict |
|---|---|---|---|---|---|
| `0x17B1A8` | `0x17B1B0` | 8 | `R33` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x18BA60` | `0x18BA74` | 20 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x18CCA0` | `0x18CCAC` | 12 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x18DE08` | `0x18DE14` | 12 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x190644` | `0x190650` | 12 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x1912C0` | `0x1912C8` | 8 | `R33` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x19B170` | `0x19B178` | 8 | `R33` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x1A0240` | `0x1A0248` | 8 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x1A2E58` | `0x1A2E70` | 24 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x1B2F10` | `0x1B2F1C` | 12 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x1BFDE4` | `0x1BFDF8` | 20 | `R33` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x1C1950` | `0x1C1964` | 20 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x1C3BE4` | `0x1C3BF8` | 20 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x1C7F10` | `0x1C7F24` | 20 | `R34` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x1D268C` | `0x1D2711` | 133 | `R33` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); read by 2 pc(s): copy return `08009B2C bl #0x8049120`; field load `08009D04 ldr r1, [r1]`; 5 offset(s) of 33 word(s), 0.12 of the row, 72 read(s) |
| `0x1D2711` | `0x1D2754` | 67 | `R33` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); read by 1 pc(s): copy return `08009B2C bl #0x8049120`; 1 offset(s) of 16 word(s), 0.06 of the row, 8 read(s) |
| `0x1FB340` | `0x1FB348` | 8 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x21165C` | `0x211664` | 8 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x211AD0` | `0x211AD8` | 8 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x216300` | `0x216308` | 8 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x21E0C8` | `0x21E0D0` | 8 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x21FD7C` | `0x22002C` | 688 | `R33` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); read by 2 pc(s): copy return `08009B2C bl #0x8049120`; field load `08009D04 ldr r1, [r1]`; 4 offset(s) of 172 word(s), 0.01 of the row, 316 read(s) |
| `0x22002C` | `0x220498` | 1132 | `R33` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); read by 2 pc(s): copy return `08009B2C bl #0x8049120`; field load `08009D04 ldr r1, [r1]`; 6 offset(s) of 283 word(s), 0.01 of the row, 48 read(s) |
| `0x220498` | `0x220588` | 240 | `R33` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x2205D4` | `0x2205DC` | 8 | `R33` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x22650C` | `0x226514` | 8 | `R34` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x2369CC` | `0x2369D8` | 12 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x25C808` | `0x25C814` | 12 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x25DF4C` | `0x25DF64` | 24 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x25F578` | `0x25F584` | 12 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x263788` | `0x2637A0` | 24 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x2645D4` | `0x2645E0` | 12 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x278230` | `0x27823C` | 12 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x279ED8` | `0x279EEC` | 20 | `R34` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x29B308` | `0x29B320` | 24 | `R34` | `other-compressed` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); read by 2 pc(s): field load `0803D946 ldr r3, [r2]`; copy return `0803D958 bl #0x8049120`; 2 offset(s) of 6 word(s), 0.33 of the row, 4 read(s) |
| `0x2B3E58` | `0x2B3E6C` | 20 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); no reader in the 452-map sweep |
| `0x2B5F1C` | `0x2B5F28` | 12 | `R35` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); read by 5 pc(s): field load `08009B86 ldr r2, [r2, #4]`; field load `08009BE8 ldr r0, [r0, #4]`; field load `0803D946 ldr r3, [r2]`; 3 offset(s) of 3 word(s), 1.00 of the row, 10 read(s) |
| `0x2B5F94` | `0x2B5FA0` | 12 | `R33` | `graphics` | pending-image-route: the animation row's payload is a JCALG1 stream decoded at IWRAM 0x03000040 before the copy to VRAM, or it is the carve-out 0x29B308; not carried by the image route (docs/research/MAP_BLOCK_LAYOUTS.md); read by 5 pc(s): field load `08009B86 ldr r2, [r2, #4]`; field load `08009BE8 ldr r0, [r0, #4]`; field load `0803D946 ldr r3, [r2]`; 3 offset(s) of 3 word(s), 1.00 of the row, 5 read(s) |
| `0x3192A5` | `0x3192A8` | 3 | `R35` | `unknown` | read by 1 pc(s): copy return `0803E278 bl #0x8046aa6`; 1 offset(s) of 1 word(s), 0.33 of the row, 4 read(s) |
| `0x36D18A` | `0x36D18C` | 2 | `R35` | `unknown` | no reader in the 452-map sweep |
| `0x3BBBB0` | `0x3BBE70` | 704 | `R34` | `unknown` | no reader in the 452-map sweep |
| `0x3C33F8` | `0x3C34B0` | 184 | `R33` | `unknown` | read by 2 pc(s): field load `08012980 ldr r0, [r0, #8]`; field load `080132DC ldrb r0, [r0, r1]`; 2 offset(s) of 46 word(s), 0.02 of the row, 21696 read(s) |
| `0x3C34B0` | `0x3C34D0` | 32 | `R33` | `unknown` | read by 2 pc(s): field load `08013362 ldr r3, [r1]`; field load `0801336A ldr r1, [r1, #4]`; 2 offset(s) of 8 word(s), 0.25 of the row, 57792 read(s) |
| `0x6B8048` | `0x6B806C` | 36 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B806C` | `0x6B8070` | 4 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B8070` | `0x6B8074` | 4 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B8074` | `0x6B8078` | 4 | `R33` | `unknown` | read by 2 pc(s): field load `08015B94 ldr r0, [r0]`; field load `08015BA2 ldr r0, [r0]`; 1 offset(s) of 1 word(s), 1.00 of the row, 74 read(s) |
| `0x6B8080` | `0x6B8088` | 8 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B8088` | `0x6B8090` | 8 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B8090` | `0x6B8098` | 8 | `R33` | `unknown` | read by 3 pc(s): field load `0800E9EA ldrb r1, [r0]`; field load `0800E9EC ldr r5, [r0, #4]`; field load `0800EAEE ldrb r0, [r0]`; 2 offset(s) of 2 word(s), 0.62 of the row, 42 read(s) |
| `0x6B8098` | `0x6B80A0` | 8 | `R33` | `unknown` | read by 4 pc(s): field load `0800E9EA ldrb r1, [r0]`; field load `0800E9EC ldr r5, [r0, #4]`; field load `0800EA04 ldrb r0, [r0, #1]`; 3 offset(s) of 2 word(s), 0.75 of the row, 192 read(s) |
| `0x6B80A0` | `0x6B80A8` | 8 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B80A8` | `0x6B80C0` | 24 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B80C0` | `0x6B80D0` | 16 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B80D0` | `0x6B80D8` | 8 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B80D8` | `0x6B80E0` | 8 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B80E0` | `0x6B80E8` | 8 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B80E8` | `0x6B80F0` | 8 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B80F0` | `0x6B8100` | 16 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B8100` | `0x6B8108` | 8 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B8108` | `0x6B8110` | 8 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B8110` | `0x6B8118` | 8 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B8118` | `0x6B8120` | 8 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B8120` | `0x6B8124` | 4 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B8124` | `0x6B814C` | 40 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x6B82EC` | `0x6B87FC` | 1296 | `R33` | `unknown` | read by 8 pc(s): field load `0800E1F8 ldrb r0, [r0]`; field load `080105A8 ldrb r2, [r2]`; field load `0801072E ldrb r0, [r0]`; 3 offset(s) of 324 word(s), 0.01 of the row, 328808 read(s) |
| `0x6F3BC8` | `0x6F3C30` | 104 | `R35` | `unknown` | no reader in the 452-map sweep |
| `0x6F9EC4` | `0x6F9EC8` | 4 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x73198C` | `0x7319CC` | 64 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x732350` | `0x732360` | 16 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x7325E8` | `0x7325F8` | 16 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x74312C` | `0x743264` | 312 | `R34` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 11 offset(s) of 78 word(s), 0.08 of the row, 1520 read(s) |
| `0x7434B0` | `0x743E68` | 2488 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 60 offset(s) of 622 word(s), 0.02 of the row, 5544 read(s) |
| `0x744EF0` | `0x74535C` | 1132 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 38 offset(s) of 283 word(s), 0.08 of the row, 5089 read(s) |
| `0x745798` | `0x74606C` | 2260 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 88 offset(s) of 565 word(s), 0.03 of the row, 6316 read(s) |
| `0x746844` | `0x746C74` | 1072 | `R34` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 49 offset(s) of 268 word(s), 0.12 of the row, 5809 read(s) |
| `0x7473E4` | `0x74798C` | 1448 | `R34` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 47 offset(s) of 362 word(s), 0.04 of the row, 3278 read(s) |
| `0x747E64` | `0x74829C` | 1080 | `R34` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 38 offset(s) of 270 word(s), 0.07 of the row, 3084 read(s) |
| `0x748668` | `0x748788` | 288 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 15 offset(s) of 72 word(s), 0.14 of the row, 1434 read(s) |
| `0x748860` | `0x7488E4` | 132 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 6 offset(s) of 33 word(s), 0.12 of the row, 505 read(s) |
| `0x7489D4` | `0x748A38` | 100 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 5 offset(s) of 25 word(s), 0.12 of the row, 374 read(s) |
| `0x748AC8` | `0x748C58` | 400 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 5 offset(s) of 100 word(s), 0.03 of the row, 370 read(s) |
| `0x748F34` | `0x74901C` | 232 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 11 offset(s) of 58 word(s), 0.07 of the row, 613 read(s) |
| `0x749118` | `0x749178` | 96 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 7 offset(s) of 24 word(s), 0.21 of the row, 601 read(s) |
| `0x7491D0` | `0x7495C8` | 1016 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 32 offset(s) of 254 word(s), 0.02 of the row, 1836 read(s) |
| `0x74980C` | `0x749CBC` | 1200 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 47 offset(s) of 300 word(s), 0.05 of the row, 2898 read(s) |
| `0x749F1C` | `0x74A820` | 2308 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 94 offset(s) of 577 word(s), 0.04 of the row, 3998 read(s) |
| `0x74AA98` | `0x74AC18` | 384 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 40 offset(s) of 96 word(s), 0.30 of the row, 2637 read(s) |
| `0x74ACB4` | `0x74B0F8` | 1092 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 35 offset(s) of 273 word(s), 0.04 of the row, 1014 read(s) |
| `0x74B8B4` | `0x74BA44` | 400 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 23 offset(s) of 100 word(s), 0.13 of the row, 899 read(s) |
| `0x74BB40` | `0x74BC88` | 328 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 17 offset(s) of 82 word(s), 0.09 of the row, 472 read(s) |
| `0x74BCF8` | `0x74BFB4` | 700 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 11 offset(s) of 175 word(s), 0.03 of the row, 340 read(s) |
| `0x74C58C` | `0x74C660` | 212 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 6 offset(s) of 53 word(s), 0.08 of the row, 184 read(s) |
| `0x74C804` | `0x74C884` | 128 | `R35` | `unknown` | read by 5 pc(s): field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; field load `08004AAE ldrb r6, [r3]`; 5 offset(s) of 32 word(s), 0.09 of the row, 133 read(s) |
| `0x74C92C` | `0x74CA24` | 248 | `R33` | `unknown` | read by 3 pc(s): field load `08004A9E ldr r5, [r0, r3]`; field load `08004AA2 ldr r7, [r5, #0x14]`; field load `08004AAC ldr r3, [r3, #0x18]`; 57 offset(s) of 62 word(s), 0.32 of the row, 13319 read(s) |
| `0x74CA24` | `0x74CA2C` | 8 | `R33` | `unknown` | read by 2 pc(s): field load `08004A8E ldr r3, [r0]`; field load `08004A96 ldr r0, [r0, #4]`; 2 offset(s) of 2 word(s), 1.00 of the row, 904 read(s) |
| `0x74CA3C` | `0x74CA60` | 36 | `R35` | `unknown` | no reader in the 452-map sweep |
| `0x74CA70` | `0x74CA90` | 32 | `R35` | `unknown` | read by 2 pc(s): field load `080266AA ldr r2, [r0]`; field load `080266B0 ldr r0, [r0, #4]`; 2 offset(s) of 8 word(s), 0.25 of the row, 4 read(s) |
| `0x74CAA0` | `0x74CAC4` | 36 | `R35` | `unknown` | no reader in the 452-map sweep |
| `0x74CAD4` | `0x74CAF4` | 32 | `R35` | `unknown` | read by 2 pc(s): field load `080269FC ldr r2, [r0]`; field load `08026A02 ldr r0, [r0, #4]`; 4 offset(s) of 8 word(s), 0.38 of the row, 8 read(s) |
| `0x74CB04` | `0x74CF24` | 1056 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x74CF24` | `0x74CF28` | 4 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x74CF28` | `0x74D02C` | 260 | `R33` | `unknown` | no reader in the 452-map sweep |
| `0x74D02C` | `0x74D03C` | 16 | `R33` | `unknown` | no reader in the 452-map sweep |
