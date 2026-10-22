# R00, R07, R09, R10, R18 and R22: one reader-bounded record table and a per-row null

Measured 2026-10-19 from ROM sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`. Data addresses are
file offsets, instruction addresses are bus addresses `0x08...`, and every quote is a
Thumb decode of the bytes at that address (`tools/research/thumb_annotate.py`). The regions
are `incbin_census.REGIONS` over the still-raw rows of `docs/research/RAW_REMAINDER.csv`.
One row is bounded by its reader and becomes source; the other 210 keep a measured null.

## Totals

| region | rows | bytes | definition |
|---|---|---|---|
| `R00` | 151 | 3915 | no measured region |
| `R09` | 26 | 7744 | dialogue container table 0x7B5B64 and the run it heads |
| `R10` | 22 | 7696 | container-rich run 0x74D248..0x74F058 |
| `R18` | 8 | 3596 | raw-labeled run 0x6B7080..0x6B7E8C |
| `R22` | 3 | 6040 | raw-labeled row 0x6FC260..0x6FDA00 |
| decoded | 1 | 1060 | `0x3BB78C..0x3BBBB0`, section below |
| **measured** | **210** | **28,991** | |

R07 held one row before the decode and holds none after it, so the six regions' raw rows
today are 210 / 28,991 B. `python tools\research\raw_remainder.py` prints
`total 3344 row(s) 585508 B  gate raw-data 585508 B  EXACT`.

## What was searched

| channel | instrument | denominator | result on these rows |
|---|---|---|---|
| decoded `ldr` literal load in transcribed code | `tools/research/consumer_search.py` `literal_loads` | 2,783 ledger Thumb/ARM rows / 292,722 B | 203 loads into 57 rows |
| Thumb/ARM branch or Thumb function pointer | `tools/research/thumb_bodies.py` `entries` | 2,785 walked rows | 3 entries, into three 1-byte R00 rows |
| class-table method slot | `thumb_bodies.method_entries` | 1,002 slots over 150 class bases | 0 |
| pointer-table word with bit 0 set | `thumb_bodies.pointer_entries` | 124 carrier rows / 392 grid words | 0 |
| Thumb-1 literal-shaped halfword over the whole image | `unknown_consumer_search.loaders` | 117,008 Thumb + 618 ARM literal sites | 116 naming literals; the site class below |
| word-aligned word over the whole image | `consumer_search.sites` | 2,097,152 words | 301 naming words |

Every count is half-open over each row's own span (`[start, end)`), not over the interval
that contains the rows (P-738); `unknown_consumer_search.loaders()` tests an inclusive high
bound, so the run subtracts one byte from each row's end (P-725).

## Where the naming evidence actually sits

| region | naming literals | with a loader in a ledger code row | with a loader in an INCBIN slice | with a loader in a data row | naming words | rows with a decoded reader |
|---|---|---|---|---|---|---|
| `R00` | 1 | 1 | 0 | 0 | 81 | 1 |
| `R09` | 53 | 48 | 0 | 8 | 57 | 26 |
| `R10` | 34 | 33 | 0 | 2 | 87 | 22 |
| `R18` | 13 | 9 | 0 | 5 | 53 | 6 |
| `R22` | 15 | 12 | 0 | 5 | 23 | 2 |

A naming literal is a pool word whose value lands inside a row and that a decoded `ldr`
loads; 103 of the 116 have a loader inside a ledger code row, and that is where the 57
reader rows come from. The 13 that do not are loaded only from data rows, so a data row
that loads a pool word names a row without consuming it (P-721, P-732). The 301
word-aligned words that hold an address inside a row are names, not consumers (P-733):
they are what the ledger's `references` column reports, and no decoded `ldr` loads most of
them. R00's reader row is `0x561CC` and its three entries are the 1-byte rows `0x2D79C`,
`0x2E444` and `0x3018C`.

## `0x3BB78C`: 53 x 20 B records, decoded

The row is 1,060 B (R07). Its stride is the reader's own arithmetic, at the four sites that
load the base literal `0x083BB78C` (pool words at file `0x0008F8`, `0x004210`, `0x00545C`,
`0x008D10`):

    080008BC 4A0E  ldr r2, [pc, #0x38]   ; 0x083BB78C
    080008BE 008B  lsls r3, r1, #2
    080008C0 1859  adds r1, r3, r1
    080008C2 0089  lsls r1, r1, #2        ; 20 * index
    080008C4 1889  adds r1, r1, r2

and the same three-instruction arithmetic at `0x080041BC`, `0x080053FE` and `0x08008C8A`.
The record's fields are read by the stream machine, quoted at their sites:

| offset | type | field | evidence |
|---|---|---|---|
| +0x0 | u32 | array_base | `0x0803EEFE ldr r1, [r0, #0xc]` then `0x0803EF0E ldr r1, [r1]` |
| +0x4 | u32 | ramp_base | `0x0803EF00 ldr r4, [r1, #4]`, read as `ldrb r3, [r4, r3]` |
| +0x8 | u32 | samples | `0x0803E542 ldr r5, [r3, #8]`; `0x0836D18C` in 53/53 records |
| +0xC | u32 | block | `0x0803EF74 ldr r2, [r0, #0xc]`; `0x0836D540` in 53/53 records |
| +0x10 | u16 | count | `0x0803F14A ldrb r0, [r1, #0x10]` |
| +0x11 | u8 | count byte | `0x0803F120 ldrb r0, [r1, #0x11]` |
| +0x12 | u16 | pad | no instruction reads it; zero in 53/53 records |

The count of records is not an instruction's: K-153 measured it by the `+8` word, and no
instruction compares the index. The bound is the row's own extent at the instruction-proven
stride (1,060 = 53 x 20) together with the two constants and the zero pad that 53/53 records
hold: a byte-permuted copy of the row (`random.Random(seed).shuffle`, seeds 1, 2, 20261018
and 20261019) holds 0 of 53. That is the null this decode beats. Falsifier: a load at
`[base+0x424]` or an index above 0x34, or a record whose `+8`/`+0xC` differs from the
constants.

Emitter: `tools/assetrecords/musicrecords_layout.json` carries the field names, offsets and
types only; the existing `tools/assetrecords/records_table.py` parses the image at build
time, re-emits every record and refuses unless its own reread equals the image's 1,060
bytes. `tools/gate/emit_all.py` runs it as `musicrecords_gen`, and
`asm/rawlabeled_3bb78c.s` includes `build\musicrecords.s` in place of the INCBIN slice.
Gate accounting: source 7,775,928 -> 7,776,988 B and raw-data 586,568 -> 585,508 B in the
same build, `DIGEST MATCH`. Tests: `tools/assetrecords/test_records_table.py` (three new
cases: the layout's 53 x 20 tiling, the image round trip, and a swapped pointer pair).

## The per-row null

Each line: file offsets, bytes, entropy, zero-byte share, word-aligned words inside the row
holding an in-image address, class, naming literals with their site classes (`c` ledger code
row, `i` INCBIN slice, `d` data) and word-aligned naming words outside the row, the decoded
reader with its instruction, and why the row stays raw. `none` means no decoded instruction
in the four reader channels names a byte of the row at the denominators above. The two
`code-without-entry` rows of `R00` (`0x2D79C`, `0x3018C`) are counted in the totals above and
their null is in `docs/research/CODE_FRAGMENT_NULL_CENSUS.md`: each is the low byte of an
instruction whose high byte lies in the neighbouring row.

### R00 (151 rows / 3915 B)

| start | end | bytes | ent | zero | words | class | naming | readers | null |
|---|---|---|---|---|---|---|---|---|---|
| `0x4` | `0xA0` | 156 | 6.52 | 0.01 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0xA0` | `0xAC` | 12 | 3.02 | 0.08 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0xAC` | `0xB0` | 4 | 2.00 | 0.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0xB0` | `0xB2` | 2 | 1.00 | 0.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0xB2` | `0xB3` | 1 | 0.00 | 0.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0xB3` | `0xB4` | 1 | 0.00 | 1.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0xB4` | `0xB5` | 1 | 0.00 | 1.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0xBC` | `0xBD` | 1 | 0.00 | 1.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0xBD` | `0xBE` | 1 | 0.00 | 0.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0xBE` | `0xC0` | 2 | 0.00 | 1.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x145BC` | `0x14666` | 170 | 5.74 | 0.02 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x14668` | `0x146B2` | 74 | 4.97 | 0.03 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x14744` | `0x14748` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x1474C` | `0x14750` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x14754` | `0x14770` | 28 | 3.94 | 0.11 | 5 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x14C34` | `0x14C5C` | 40 | 4.15 | 0.12 | 7 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x1A460` | `0x1A576` | 278 | 5.75 | 0.07 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x1A578` | `0x1A590` | 24 | 4.33 | 0.08 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x1A594` | `0x1A624` | 144 | 5.70 | 0.05 | 8 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x1AB6E` | `0x1AB7C` | 14 | 3.09 | 0.29 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x1B22E` | `0x1B23C` | 14 | 2.56 | 0.43 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x1B4CE` | `0x1B4EC` | 30 | 3.99 | 0.13 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x1B7FE` | `0x1B800` | 2 | 0.00 | 1.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x1B810` | `0x1B814` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x1BA7E` | `0x1BA84` | 6 | 1.25 | 0.67 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x1BA88` | `0x1BA8C` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x1BDB6` | `0x1BDBC` | 6 | 2.25 | 0.33 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x1BDC0` | `0x1BDC4` | 4 | 1.50 | 0.50 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x1BDC8` | `0x1BDCC` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2AD34` | `0x2AD48` | 20 | 3.52 | 0.20 | 2 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2AD4C` | `0x2AD58` | 12 | 3.25 | 0.08 | 2 | `pointer-tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2AE18` | `0x2AE20` | 8 | 2.75 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2AEAA` | `0x2AEB0` | 6 | 2.58 | 0.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2AEF8` | `0x2AF04` | 12 | 2.79 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2B1FC` | `0x2B20C` | 16 | 3.33 | 0.19 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2B210` | `0x2B214` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2B3B4` | `0x2B3C0` | 12 | 3.25 | 0.17 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2B3C4` | `0x2B3D0` | 12 | 3.25 | 0.08 | 2 | `pointer-tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2B5CE` | `0x2B5D4` | 6 | 1.92 | 0.33 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2B6E4` | `0x2B6F8` | 20 | 3.65 | 0.15 | 2 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2B6FC` | `0x2B708` | 12 | 3.42 | 0.17 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2B7E0` | `0x2B7E4` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2B89C` | `0x2B8AC` | 16 | 3.33 | 0.19 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2B8B0` | `0x2B8F0` | 64 | 4.85 | 0.03 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2B974` | `0x2B97C` | 8 | 2.75 | 0.00 | 2 | `pointer-tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2D1CC` | `0x2D1E8` | 28 | 3.75 | 0.14 | 3 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2D318` | `0x2D324` | 12 | 3.42 | 0.17 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2D3BA` | `0x2D3BC` | 2 | 0.00 | 1.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2D49E` | `0x2D4A4` | 6 | 2.25 | 0.33 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2D4AC` | `0x2D4B0` | 4 | 2.00 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2D63E` | `0x2D640` | 2 | 0.00 | 1.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2D64C` | `0x2D650` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2D76C` | `0x2D78C` | 32 | 4.26 | 0.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2D798` | `0x2D79C` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2D79D` | `0x2D826` | 137 | 5.55 | 0.04 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2DB6A` | `0x2DB6C` | 2 | 0.00 | 1.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2DE08` | `0x2DE1C` | 20 | 3.48 | 0.10 | 4 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2DE66` | `0x2DE7C` | 22 | 3.17 | 0.27 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2DF32` | `0x2DF38` | 6 | 2.25 | 0.33 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2DF40` | `0x2DF44` | 4 | 2.00 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2DFCA` | `0x2DFD0` | 6 | 2.25 | 0.33 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2DFD4` | `0x2DFD8` | 4 | 2.00 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2E036` | `0x2E040` | 10 | 2.85 | 0.30 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2E09E` | `0x2E0A8` | 10 | 2.85 | 0.30 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2E254` | `0x2E270` | 28 | 4.08 | 0.18 | 3 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2E274` | `0x2E278` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2E2F2` | `0x2E300` | 14 | 3.47 | 0.21 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2E33A` | `0x2E348` | 14 | 3.09 | 0.29 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2E444` | `0x2E445` | 1 | 0.00 | 0.00 | 0 | `text/tables` | L0 c0/i0/d0 | entry `Thumb 0x0803c63c bl #0x802e444` | a branch enters the row; the bytes decode to no body and no naming word names it |
| `0x2E445` | `0x2E568` | 291 | 6.11 | 0.06 | 1 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2E638` | `0x2E63C` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2E644` | `0x2E654` | 16 | 3.70 | 0.06 | 3 | `pointer-tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2E6A6` | `0x2E6A8` | 2 | 0.00 | 1.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2E812` | `0x2E83C` | 42 | 3.92 | 0.29 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2ED7C` | `0x2ED98` | 28 | 3.66 | 0.29 | 2 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2F200` | `0x2F202` | 2 | 1.00 | 0.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2F210` | `0x2F212` | 2 | 1.00 | 0.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2F21A` | `0x2F224` | 10 | 2.52 | 0.40 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2F5D6` | `0x2F5E8` | 18 | 3.53 | 0.17 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2F708` | `0x2F710` | 8 | 2.75 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2F714` | `0x2F724` | 16 | 3.58 | 0.06 | 3 | `pointer-tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2F742` | `0x2F74C` | 10 | 2.85 | 0.30 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2F92A` | `0x2F940` | 22 | 3.72 | 0.23 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2FB9C` | `0x2FC2C` | 144 | 5.75 | 0.06 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2FC34` | `0x2FC52` | 30 | 4.10 | 0.13 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2FF06` | `0x2FF0C` | 6 | 2.25 | 0.33 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2FF10` | `0x2FF1C` | 12 | 3.25 | 0.17 | 2 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x2FF50` | `0x2FF56` | 6 | 1.92 | 0.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2FF96` | `0x2FFA0` | 10 | 2.85 | 0.30 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2FFD8` | `0x2FFDE` | 6 | 1.92 | 0.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x2FFEE` | `0x30000` | 18 | 3.30 | 0.28 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x30174` | `0x3018C` | 24 | 3.57 | 0.21 | 1 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x3018D` | `0x301B8` | 43 | 4.22 | 0.05 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x3123A` | `0x31258` | 30 | 4.39 | 0.17 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x314C0` | `0x314DC` | 28 | 4.16 | 0.14 | 4 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x315A4` | `0x315A8` | 4 | 2.00 | 0.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x315AC` | `0x315B0` | 4 | 2.00 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x31832` | `0x3185C` | 42 | 4.11 | 0.26 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x31E6A` | `0x31E6C` | 2 | 0.00 | 1.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x321A2` | `0x321D0` | 46 | 4.07 | 0.26 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x327CA` | `0x327D0` | 6 | 1.25 | 0.67 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x327D4` | `0x327E0` | 12 | 3.08 | 0.17 | 2 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x3281C` | `0x32824` | 8 | 2.75 | 0.00 | 2 | `pointer-tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x32B8E` | `0x32B94` | 6 | 1.79 | 0.50 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x32D2A` | `0x32D30` | 6 | 2.25 | 0.33 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x32D40` | `0x32D44` | 4 | 2.00 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x32DC4` | `0x32DC8` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x32F6C` | `0x32F84` | 24 | 3.83 | 0.17 | 2 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x34280` | `0x34294` | 20 | 3.35 | 0.30 | 2 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x34330` | `0x34334` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x343A2` | `0x343A4` | 2 | 0.00 | 1.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x3455C` | `0x3456C` | 16 | 3.75 | 0.06 | 2 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x34816` | `0x3481C` | 6 | 2.58 | 0.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x349E8` | `0x349F8` | 16 | 3.62 | 0.12 | 2 | `pointer-tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x34AA4` | `0x34AAC` | 8 | 2.75 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x34BA6` | `0x34BB8` | 18 | 3.68 | 0.06 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x34BBC` | `0x34BC0` | 4 | 2.00 | 0.00 | 1 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x34CE2` | `0x34CF8` | 22 | 3.91 | 0.18 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x34EC0` | `0x34EC8` | 8 | 3.00 | 0.12 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x34ED4` | `0x34ED8` | 4 | 2.00 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x413A4` | `0x413A8` | 4 | 2.00 | 0.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x413D6` | `0x413D8` | 2 | 0.00 | 1.00 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x413DC` | `0x413E0` | 4 | 2.00 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x4165C` | `0x4168C` | 48 | 3.85 | 0.21 | 3 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x41786` | `0x417AC` | 38 | 4.42 | 0.03 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x41828` | `0x41864` | 60 | 4.54 | 0.22 | 3 | `unknown` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x41AFC` | `0x41B00` | 4 | 2.00 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x41CB4` | `0x41CE4` | 48 | 4.36 | 0.02 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x41DF4` | `0x41DF8` | 4 | 2.00 | 0.25 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x4208A` | `0x420B0` | 38 | 3.37 | 0.29 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x43140` | `0x43158` | 24 | 4.10 | 0.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x43318` | `0x43320` | 8 | 2.50 | 0.12 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x433E2` | `0x433E4` | 2 | 1.00 | 0.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x561C4` | `0x561C8` | 4 | 2.00 | 0.25 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x561C8` | `0x561CC` | 4 | 2.00 | 0.25 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x561CC` | `0x561DC` | 16 | 1.31 | 0.75 | 0 | `text/tables` | L1 c3/i0/d0 | 3 0x08005204 `ldr r1, [pc, #0x214]` | loads the 16 B as a call argument; no stride or count in the body |
| `0x561E0` | `0x561E4` | 4 | 2.00 | 0.25 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x561E4` | `0x561E8` | 4 | 2.00 | 0.00 | 1 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x561E8` | `0x561EC` | 4 | 2.00 | 0.00 | 1 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x561EC` | `0x561F0` | 4 | 2.00 | 0.25 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x561F0` | `0x561F4` | 4 | 2.00 | 0.25 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x561F4` | `0x561F8` | 4 | 2.00 | 0.25 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x561F8` | `0x5622C` | 52 | 3.00 | 0.33 | 8 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |
| `0x3717C0` | `0x3717C2` | 2 | 1.00 | 0.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x37199A` | `0x37199C` | 2 | 1.00 | 0.00 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x372358` | `0x3724E8` | 400 | 5.51 | 0.08 | 0 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x3724F2` | `0x372574` | 130 | 4.73 | 0.09 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x37259C` | `0x3725C0` | 36 | 4.38 | 0.08 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x7B88E8` | `0x7B89A8` | 192 | 2.73 | 0.51 | 16 | `text/tables` | L0 c0/i0/d0 | none | no decoded reader; the naming words are data |

### R09 (26 rows / 7744 B)

| start | end | bytes | ent | zero | words | class | naming | readers | null |
|---|---|---|---|---|---|---|---|---|---|
| `0x7B5B64` | `0x7B5B80` | 28 | 3.75 | 0.00 | 7 | `pointer-tables` | L1 c2/i0/d0 | 2 0x08012242 `ldr r1, [pc, #0x188]` | 0x08012242 indexes it by a byte offset (`lsls #0x1a; lsrs #0x18`) with no compare; the seven words are ROM pointers and word 8 is IWRAM |
| `0x7B5B80` | `0x7B5B94` | 20 | 2.87 | 0.30 | 0 | `pointer-tables` | L1 c3/i0/d0 | 3 0x0803D784 `ldr r0, [pc, #0x1a4]` | fixed fields +0, +8 and +0x10 are read at 0x0803D784..0x0803D7FE; no stride |
| `0x7B5B94` | `0x7B6724` | 2960 | 3.77 | 0.42 | 51 | `unknown` | L1 c3/i0/d0 | 3 0x0803DF22 `ldr r0, [pc, #0xf4]` | 0x0803DF22 quotes the row as a container base and 0x0803DFF8 copies 4 bytes of it; no stride |
| `0x7B6724` | `0x7B6904` | 480 | 4.67 | 0.45 | 0 | `unknown` | L3 c5/i0/d2 | 5 0x0803E51C `ldr r5, [pc, #0x288]` | 0x0803E51A does 4*index (`lsls r4,r4,#2`) on a byte with no compare |
| `0x7B6904` | `0x7B6A04` | 256 | 5.16 | 0.01 | 32 | `unknown` | L1 c1/i0/d0 | 1 0x0803EEBC `ldr r2, [pc, #0x194]` | 0x0803EEBE does 4*index (`lsls r1,r1,#2`) with no compare |
| `0x7B6A04` | `0x7B6C84` | 640 | 7.52 | 0.00 | 0 | `unknown` | L4 c7/i0/d0 | 7 0x0803E71E `ldr r3, [pc, #0x9c]` | halfword tables indexed by a nibble (`lsls #1`) at 0x0803E722 and 0x0803E768; no compare |
| `0x7B6C84` | `0x7B6E84` | 512 | 7.63 | 0.00 | 0 | `unknown` | L4 c7/i0/d0 | 7 0x0803E690 `ldr r3, [pc, #0x120]` | halfword tables indexed by a nibble at 0x0803E6DA and 0x0803E7D2; no compare |
| `0x7B6E84` | `0x7B6EC4` | 64 | 4.95 | 0.03 | 0 | `unknown` | L1 c1/i0/d0 | 1 0x0803E8CE `ldr r3, [pc, #0x18c]` | a signed-byte lookup indexed by a 6-bit field at 0x0803E8D2; no stride |
| `0x7B6EC4` | `0x7B6EDC` | 24 | 3.21 | 0.00 | 6 | `pointer-tables` | L1 c2/i0/d0 | 2 0x0803EB3C `ldr r2, [pc, #0x258]` | 0x0803EB3E does 4*index (`lsls r1,r6,#2`) with no compare |
| `0x7B6EDC` | `0x7B6EE0` | 4 | 2.00 | 0.25 | 0 | `unknown` | L1 c3/i0/d0 | 3 0x0803F218 `ldr r0, [pc, #0x19c]` | quotes the row's word as a constant; no stride |
| `0x7B6EE0` | `0x7B6EEC` | 12 | 2.52 | 0.33 | 0 | `pointer-tables` | L1 c2/i0/d0 | 2 0x0803FA0C `ldr r0, [pc, #0x8c]` | 0x0803FA10 stores the row's word into a state object; no stride |
| `0x7B6EEC` | `0x7B72EC` | 1024 | 4.98 | 0.26 | 0 | `unknown` | L13 c17/i0/d5 | 17 0x08000754 `ldr r4, [pc, #0x194]` | 0x08000758 and 0x08008756 do 4*index (`lsls #2`) on a byte with no compare |
| `0x7B72EC` | `0x7B76EC` | 1024 | 5.81 | 0.14 | 0 | `unknown` | L2 c3/i0/d0 | 3 0x0800871C `ldr r4, [pc, #0x120]` | 0x0800871E and 0x0802EFE8 do 4*index (`lsls #2`) on a byte with no compare |
| `0x7B76EC` | `0x7B76F0` | 4 | 2.00 | 0.25 | 0 | `unknown` | L1 c4/i0/d0 | 4 0x0803FBA4 `ldr r0, [pc, #0x100]` | quotes the row's word as a constant; no stride |
| `0x7B76F0` | `0x7B76F4` | 4 | 2.00 | 0.25 | 0 | `unknown` | L3 c3/i0/d0 | 3 0x0804004A `ldr r5, [pc, #0x1d0]` | quotes the row's word as a constant; no stride |
| `0x7B76F4` | `0x7B76F8` | 4 | 2.00 | 0.25 | 0 | `unknown` | L1 c4/i0/d0 | 4 0x08040C90 `ldr r0, [pc, #0x214]` | stores the row's word into a state object (`str r1,[r0,#0x18]`); no stride |
| `0x7B76F8` | `0x7B76FC` | 4 | 1.50 | 0.00 | 0 | `unknown` | L1 c1/i0/d0 | 1 0x080415A6 `ldr r3, [pc, #0xdc]` | 0x080415A6 passes the row's word as an argument to 0x08042B3C; no stride |
| `0x7B76FC` | `0x7B7704` | 8 | 2.75 | 0.12 | 0 | `unknown` | L1 c1/i0/d1 | 1 0x080417C2 `ldr r2, [pc, #0x7c]` | 0x080417C2 stores the row's word into a record (`str r2,[r0,#0xc]`); no stride |
| `0x7B7704` | `0x7B7708` | 4 | 1.50 | 0.00 | 0 | `unknown` | L1 c1/i0/d0 | 1 0x0804204E `ldr r3, [pc, #0x58]` | 0x0804204E passes the row's word as an argument; no stride |
| `0x7B7708` | `0x7B7710` | 8 | 2.75 | 0.12 | 0 | `unknown` | L1 c2/i0/d0 | 2 0x0804219C `ldr r1, [pc, #0xb8]` | 0x0804219C stores the row's word into a record; no stride |
| `0x7B7710` | `0x7B7714` | 4 | 2.00 | 0.25 | 0 | `unknown` | L1 c2/i0/d0 | 2 0x0804340A `ldr r0, [pc, #0x13c]` | 0x0804340A stores the row's word into a state object; no stride |
| `0x7B7714` | `0x7B7734` | 32 | 3.63 | 0.19 | 0 | `unknown` | L4 c4/i0/d0 | 4 0x08044890 `ldr r5, [pc, #0x38]` | 0x08044890 does 16*index (`lsls r3,r3,#4`) after `cmp r3,#0` only |
| `0x7B7734` | `0x7B773E` | 10 | 3.12 | 0.10 | 0 | `unknown` | L1 c1/i0/d0 | 1 0x0804391E `ldr r0, [pc, #0x3a4]` | 0x0804391E passes the row's word as an argument; no stride |
| `0x7B773E` | `0x7B7970` | 562 | 6.24 | 0.11 | 0 | `unknown` | L1 c1/i0/d0 | 1 0x08045942 `ldr r4, [pc, #0xfc]` | 0x08045942 is a four-entry u16 table (`cmp r3,#3; bhi`) indexed at `lsls #1`; the row is 562 B |
| `0x7B7970` | `0x7B797C` | 12 | 1.58 | 0.67 | 0 | `unknown` | L2 c2/i0/d0 | 2 0x080407AE `ldr r0, [pc, #8]` | stores the row's word into state; no stride |
| `0x7B797C` | `0x7B79A4` | 40 | 3.00 | 0.33 | 2 | `unknown` | L1 c1/i0/d0 | 1 0x080407C2 `ldr r0, [pc, #8]` | stores the row's word into state; no stride |

### R10 (22 rows / 7696 B)

| start | end | bytes | ent | zero | words | class | naming | readers | null |
|---|---|---|---|---|---|---|---|---|---|
| `0x74D248` | `0x74D35C` | 276 | 2.06 | 0.63 | 0 | `unknown` | L2 c4/i0/d0 | 4 0x080271EA `ldr r6, [pc, #0xb4]` | constructors store the row's address (`str r0,[r4]`); 0x08027276 indexes +4 by a byte; no count |
| `0x74D35C` | `0x74D360` | 4 | 2.00 | 0.25 | 0 | `unknown` | L1 c1/i0/d0 | 1 0x0802734C `ldr r1, [pc, #0x38]` | 0x0802734A `lsrs r0,r0,#0x1e` indexes a 4-entry byte table; no count |
| `0x74D360` | `0x74D380` | 32 | 2.50 | 0.00 | 8 | `pointer-tables` | L1 c1/i0/d0 | 1 0x08027494 `ldr r2, [pc, #0x18]` | 0x08027496 does 4*index (`lsls r1,r1,#2`) on a 3-bit field with no compare |
| `0x74D380` | `0x74E200` | 3712 | 3.94 | 0.51 | 0 | `unknown` | L5 c8/i0/d0 | 8 0x08024FA0 `ldr r7, [pc, #0x36c]` | 0x080251B8 and 0x08024FA2 do 16*index and 4*index+4 with no compare |
| `0x74E200` | `0x74E208` | 8 | 2.50 | 0.25 | 0 | `pointer-tables` | L1 c1/i0/d0 | 1 0x08050FB2 `ldr r0, [pc, #0x20]` | stores the row's IWRAM word into state; no stride |
| `0x74E208` | `0x74E228` | 32 | 1.80 | 0.62 | 0 | `unknown` | L1 c3/i0/d0 | 3 0x080274FA `ldr r2, [pc, #0x1a0]` | 0x080274FC does 8*index (`lsls r0,r6,#3`) with no compare |
| `0x74E228` | `0x74E234` | 12 | 2.79 | 0.25 | 0 | `pointer-tables` | L1 c1/i0/d0 | 1 0x08051042 `ldr r0, [pc, #0x20]` | stores the row's IWRAM words; no stride |
| `0x74E234` | `0x74E614` | 992 | 2.09 | 0.62 | 0 | `unknown` | L1 c5/i0/d0 | 5 0x080276F0 `ldr r2, [pc, #0x23c]` | 0x080276F2 does 8*index (`lsls r0,r6,#3`) with no compare |
| `0x74E614` | `0x74E968` | 852 | 1.84 | 0.73 | 10 | `unknown` | L1 c2/i0/d0 | 2 0x080276E4 `ldr r1, [pc, #0x244]` | 0x080276E0 does 12*index (3*n `lsls #1; adds`, then `lsls #2`) with no compare |
| `0x74E968` | `0x74E9F8` | 144 | 3.55 | 0.21 | 18 | `unknown` | L1 c1/i0/d0 | 1 0x080274EE `ldr r1, [pc, #0x1a8]` | 0x080274EA does 12*index with no compare |
| `0x74E9F8` | `0x74EA40` | 72 | 1.59 | 0.62 | 0 | `unknown` | L2 c5/i0/d0 | 5 0x080279FA `ldr r6, [pc, #0x140]` | constructors store the row's address; 0x08027A64 copies `lsls #5` bytes from it to VRAM |
| `0x74EA40` | `0x74EA44` | 4 | 2.00 | 0.25 | 0 | `unknown` | L1 c1/i0/d0 | 1 0x08027BC0 `ldr r0, [pc, #0x68]` | 0x08027BC0 stores the row's word into state; no stride |
| `0x74EA44` | `0x74EA48` | 4 | 2.00 | 0.25 | 0 | `unknown` | L1 c2/i0/d0 | 2 0x08027C3E `ldr r5, [pc, #0x78]` | 0x08027C3E loads the row's word and passes it as a length base; no stride |
| `0x74EA48` | `0x74EA50` | 8 | 2.50 | 0.25 | 0 | `pointer-tables` | L2 c3/i0/d0 | 3 0x08027D18 `ldr r0, [pc, #0x84]` | 0x08027D18 dereferences the row's first word; no stride |
| `0x74EA50` | `0x74EA54` | 4 | 2.00 | 0.25 | 0 | `unknown` | L1 c4/i0/d0 | 4 0x08027DCA `ldr r5, [pc, #0x78]` | 0x08027DCA stores the row's word into state; no stride |
| `0x74EA54` | `0x74EA60` | 12 | 3.02 | 0.25 | 1 | `pointer-tables` | L2 c2/i0/d0 | 2 0x08028162 `ldr r6, [pc, #0x20c]` | 0x08028162 stores the row's word into state; no stride |
| `0x74EA60` | `0x74EA80` | 32 | 3.72 | 0.12 | 6 | `unknown` | L1 c4/i0/d0 | 4 0x08027EC4 `ldr r1, [pc, #0x248]` | 0x08027EC4 passes the row to 0x08046C54; no stride |
| `0x74EA80` | `0x74EAC4` | 68 | 1.80 | 0.69 | 0 | `unknown` | L3 c13/i0/d0 | 13 0x0802839C `ldr r0, [pc, #0x31c]` | 0x0802839C and 0x080284E2 load the row's +4 word; no stride or count |
| `0x74EAC4` | `0x74ED7C` | 696 | 1.79 | 0.59 | 0 | `unknown` | L2 c9/i0/d0 | 9 0x08028C24 `ldr r7, [pc, #0x274]` | 0x08028C8E does 24*index (3*n `lsls #1; adds`, `lsls #3`) and 0x08028C94 does 8*index, both without a compare |
| `0x74ED7C` | `0x74EFEC` | 624 | 3.38 | 0.37 | 40 | `unknown` | L1 c1/i0/d0 | 1 0x08028762 `ldr r2, [pc, #0x264]` | 0x08028764 does 60*index (`lsls #4; subs; lsls #2`) with no compare |
| `0x74EFEC` | `0x74F04C` | 96 | 2.84 | 0.38 | 14 | `unknown` | L1 c1/i0/d0 | 1 0x08028C88 `ldr r2, [pc, #0x218]` | 0x08028C8E does 24*index with no compare |
| `0x74F04C` | `0x74F058` | 12 | 3.25 | 0.17 | 1 | `pointer-tables` | L2 c2/i0/d3 | 2 0x08029040 `ldr r6, [pc, #0x27c]` | stores the row's IWRAM word; no stride |

### R18 (8 rows / 3596 B)

| start | end | bytes | ent | zero | words | class | naming | readers | null |
|---|---|---|---|---|---|---|---|---|---|
| `0x6B7080` | `0x6B7084` | 4 | 2.00 | 0.25 | 0 | `unknown` | L2 c5/i0/d0 | 5 0x08013940 `ldr r7, [pc, #0x25c]` | 0x08013A0A indexes base+4+4*index with no compare; the other four quote the word |
| `0x6B7084` | `0x6B72E0` | 604 | 6.15 | 0.25 | 0 | `unknown` | L2 c7/i0/d0 | 7 0x08013380 `ldr r1, [pc, #0x28c]` | 0x08013380 does 4*index-0x90 under `cmp r0,#0x32` / `cmp r0,#0xC8`; the entries leave the row (index 0xC8 reads row+0x290) |
| `0x6B72E0` | `0x6B7400` | 288 | 1.43 | 0.79 | 0 | `unknown` | L1 c1/i0/d0 | 1 0x0801368C `ldr r1, [pc, #0x280]` | 0x08013690 does 32*index (`lsls r0,r0,#5`) on a byte field with no compare; +0/+4/+8/+0xC are read as fixed-point at 0x080136C4.., field meanings not established |
| `0x6B7400` | `0x6B748C` | 140 | 3.06 | 0.51 | 0 | `unknown` | L1 c1/i0/d0 | none | no decoded reader; the naming words are data |
| `0x6B748C` | `0x6B7590` | 260 | 3.08 | 0.51 | 0 | `unknown` | L1 c2/i0/d0 | 2 0x08013BF8 `ldr r0, [pc, #0x224]` | 0x08013BF8 hands the row to 0x0803DF14 and 0x08013DF6 builds a pointer +0x98 into it; no stride or count |
| `0x6B7590` | `0x6B759C` | 12 | 3.19 | 0.25 | 0 | `unknown` | L1 c0/i0/d1 | none | no decoded reader; the naming words are data |
| `0x6B759C` | `0x6B77A4` | 520 | 1.94 | 0.59 | 5 | `unknown` | L1 c1/i0/d0 | 1 0x08013E3A `ldr r5, [pc, #0x24]` | 0x08013E3E does 16*index (`lsls r3,r2,#4`) on a loop counter with no compare |
| `0x6B77A4` | `0x6B7E8C` | 1768 | 6.91 | 0.10 | 33 | `unknown` | L4 c2/i0/d5 | 2 0x08013E84 `ldr r1, [pc, #0x28c]` | 0x08013E84 stores the word at +0 as a descriptor and 0x08014096 loads +0x30; no stride or count |

### R22 (3 rows / 6040 B)

| start | end | bytes | ent | zero | words | class | naming | readers | null |
|---|---|---|---|---|---|---|---|---|---|
| `0x6FC260` | `0x6FCCC0` | 2656 | 3.77 | 0.34 | 0 | `unknown` | L0 c0/i0/d0 | none | no decoded reader and no naming word at half-open bounds |
| `0x6FCCC8` | `0x6FD9D0` | 3336 | 1.74 | 0.63 | 0 | `unknown` | L1 c10/i0/d0 | 10 0x080184E6 `ldr r0, [pc, #0x2a4]` | ten sites load the row and dereference its first word (`ldr r0,[r0]`, 0x03001C4C); no stride or count |
| `0x6FD9D0` | `0x6FDA00` | 48 | 3.14 | 0.17 | 4 | `unknown` | L14 c15/i0/d6 | 15 0x0800C9C8 `ldr r2, [pc, #0x140]` | fifteen sites pass the row to 0x0802A81C as a four-word source; no record stride |

## What the null does not cover

- A reader that forms the row's address from a base register and an offset computed from
  another table is covered only where a decoded `ldr` loads the address; a computed address
  inside a body this census did not walk is invisible.
- Code outside the ledger's 2,783 transcribed Thumb/ARM rows is outside every denominator
  above.
- No row here has a runtime read watch, so a consumer that exists only at run time is not
  measured.
- R18's 288 B row has a stride (32, `0x08013690 lsls r0, r0, #5`) and four fixed-point
  fields read at `0x080136C4`..`0x080136DE`, but no field meaning and no count: emitting its
  numbers would be the byte dump the route vocabulary refuses.

## Sweep read verdict (generated: docs/research/REGION_READS.csv)

One line per raw row of `R00`, `R09`, `R10`, `R18`, `R22`, from `tools/research/region_readers.py`.
The 2 `code-without-entry` row(s) of those regions carry their null in
`docs/research/CODE_FRAGMENT_NULL_CENSUS.md`, which is the class's census.
The offsets are the byte offsets inside the row that the sweep's reads used, and the
share is the part of the row those reads reached. The null above each row stays its
measured null; this line is the read verdict on it.

| start | end | bytes | region | class | verdict |
|---|---|---|---|---|---|
| `0x4` | `0xA0` | 156 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0xA0` | `0xAC` | 12 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0xAC` | `0xB0` | 4 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0xB0` | `0xB2` | 2 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0xB2` | `0xB3` | 1 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0xB3` | `0xB4` | 1 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0xB4` | `0xB5` | 1 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0xBC` | `0xBD` | 1 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0xBD` | `0xBE` | 1 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0xBE` | `0xC0` | 2 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x145BC` | `0x14666` | 170 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x14668` | `0x146B2` | 74 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x14744` | `0x14748` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1474C` | `0x14750` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x14754` | `0x14770` | 28 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x14C34` | `0x14C5C` | 40 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1A460` | `0x1A576` | 278 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1A578` | `0x1A590` | 24 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1A594` | `0x1A624` | 144 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1AB6E` | `0x1AB7C` | 14 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1B22E` | `0x1B23C` | 14 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1B4CE` | `0x1B4EC` | 30 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1B7FE` | `0x1B800` | 2 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1B810` | `0x1B814` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1BA7E` | `0x1BA84` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1BA88` | `0x1BA8C` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1BDB6` | `0x1BDBC` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1BDC0` | `0x1BDC4` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x1BDC8` | `0x1BDCC` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2AD34` | `0x2AD48` | 20 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2AD4C` | `0x2AD58` | 12 | `R00` | `pointer-tables` | no reader in the 452-map sweep |
| `0x2AE18` | `0x2AE20` | 8 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2AEAA` | `0x2AEB0` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2AEF8` | `0x2AF04` | 12 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2B1FC` | `0x2B20C` | 16 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2B210` | `0x2B214` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2B3B4` | `0x2B3C0` | 12 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2B3C4` | `0x2B3D0` | 12 | `R00` | `pointer-tables` | no reader in the 452-map sweep |
| `0x2B5CE` | `0x2B5D4` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2B6E4` | `0x2B6F8` | 20 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2B6FC` | `0x2B708` | 12 | `R00` | `unknown` | read by 1 pc(s): field load `0802B700 ldr r0, [pc, #0]`; 1 offset(s) of 3 word(s), 0.33 of the row, 21 read(s) |
| `0x2B7E0` | `0x2B7E4` | 4 | `R00` | `unknown` | read by 1 pc(s): field load `0802B744 ldr r1, [pc, #0x98]`; 1 offset(s) of 1 word(s), 1.00 of the row, 8685 read(s) |
| `0x2B89C` | `0x2B8AC` | 16 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2B8B0` | `0x2B8F0` | 64 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2B974` | `0x2B97C` | 8 | `R00` | `pointer-tables` | no reader in the 452-map sweep |
| `0x2D1CC` | `0x2D1E8` | 28 | `R00` | `unknown` | read by 6 pc(s): field load `0802D10C ldr r5, [pc, #0xc4]`; field load `0802D16E ldr r0, [pc, #0x68]`; field load `0802D178 ldr r2, [pc, #0x60]`; 4 offset(s) of 7 word(s), 0.43 of the row, 140 read(s) |
| `0x2D318` | `0x2D324` | 12 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2D3BA` | `0x2D3BC` | 2 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2D49E` | `0x2D4A4` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2D4AC` | `0x2D4B0` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2D63E` | `0x2D640` | 2 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2D64C` | `0x2D650` | 4 | `R00` | `unknown` | read by 1 pc(s): field load `0802D638 ldr r1, [pc, #0x10]`; 1 offset(s) of 1 word(s), 1.00 of the row, 5 read(s) |
| `0x2D76C` | `0x2D78C` | 32 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2D798` | `0x2D79C` | 4 | `R00` | `unknown` | read by 1 pc(s): field load `0802D77E ldr r0, [pc, #0x18]`; 1 offset(s) of 1 word(s), 1.00 of the row, 2 read(s) |
| `0x2D79D` | `0x2D826` | 137 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x2DB6A` | `0x2DB6C` | 2 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2DE08` | `0x2DE1C` | 20 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2DE66` | `0x2DE7C` | 22 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2DF32` | `0x2DF38` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2DF40` | `0x2DF44` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2DFCA` | `0x2DFD0` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2DFD4` | `0x2DFD8` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2E036` | `0x2E040` | 10 | `R00` | `unknown` | read by 1 pc(s): field load `0802E036 ldr r0, [pc, #4]`; 1 offset(s) of 2 word(s), 0.40 of the row, 11 read(s) |
| `0x2E09E` | `0x2E0A8` | 10 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2E254` | `0x2E270` | 28 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2E274` | `0x2E278` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2E2F2` | `0x2E300` | 14 | `R00` | `text/tables` | read by 2 pc(s): field load `0802E290 ldr r6, [pc, #0x64]`; field load `0802E2F2 ldr r0, [pc, #8]`; 2 offset(s) of 3 word(s), 0.29 of the row, 9 read(s) |
| `0x2E33A` | `0x2E348` | 14 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2E444` | `0x2E445` | 1 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x2E445` | `0x2E568` | 291 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x2E638` | `0x2E63C` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2E644` | `0x2E654` | 16 | `R00` | `pointer-tables` | no reader in the 452-map sweep |
| `0x2E6A6` | `0x2E6A8` | 2 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2E812` | `0x2E83C` | 42 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2ED7C` | `0x2ED98` | 28 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2F200` | `0x2F202` | 2 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x2F210` | `0x2F212` | 2 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x2F21A` | `0x2F224` | 10 | `R00` | `unknown` | read by 1 pc(s): field load `0802F21C ldr r0, [pc, #0]`; 1 offset(s) of 2 word(s), 0.40 of the row, 43 read(s) |
| `0x2F5D6` | `0x2F5E8` | 18 | `R00` | `unknown` | read by 5 pc(s): field load `0802F464 ldr r3, [pc, #0x170]`; field load `0802F478 ldr r0, [pc, #0x160]`; field load `0802F4C6 ldr r6, [pc, #0x118]`; 4 offset(s) of 4 word(s), 0.56 of the row, 108 read(s) |
| `0x2F708` | `0x2F710` | 8 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2F714` | `0x2F724` | 16 | `R00` | `pointer-tables` | no reader in the 452-map sweep |
| `0x2F742` | `0x2F74C` | 10 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2F92A` | `0x2F940` | 22 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2FB9C` | `0x2FC2C` | 144 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2FC34` | `0x2FC52` | 30 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2FF06` | `0x2FF0C` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2FF10` | `0x2FF1C` | 12 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2FF50` | `0x2FF56` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2FF96` | `0x2FFA0` | 10 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2FFD8` | `0x2FFDE` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x2FFEE` | `0x30000` | 18 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x30174` | `0x3018C` | 24 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x3018D` | `0x301B8` | 43 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x3123A` | `0x31258` | 30 | `R00` | `unknown` | read by 1 pc(s): field load `08031008 ldr r0, [pc, #0x240]`; 1 offset(s) of 7 word(s), 0.13 of the row, 1 read(s) |
| `0x314C0` | `0x314DC` | 28 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x315A4` | `0x315A8` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x315AC` | `0x315B0` | 4 | `R00` | `unknown` | read by 1 pc(s): field load `080315A4 ldr r0, [pc, #4]`; 1 offset(s) of 1 word(s), 1.00 of the row, 1 read(s) |
| `0x31832` | `0x3185C` | 42 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x31E6A` | `0x31E6C` | 2 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x321A2` | `0x321D0` | 46 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x327CA` | `0x327D0` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x327D4` | `0x327E0` | 12 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x3281C` | `0x32824` | 8 | `R00` | `pointer-tables` | no reader in the 452-map sweep |
| `0x32B8E` | `0x32B94` | 6 | `R00` | `unknown` | read by 1 pc(s): field load `08032A76 ldr r0, [pc, #0x118]`; 1 offset(s) of 1 word(s), 0.67 of the row, 134 read(s) |
| `0x32D2A` | `0x32D30` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x32D40` | `0x32D44` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x32DC4` | `0x32DC8` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x32F6C` | `0x32F84` | 24 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x34280` | `0x34294` | 20 | `R00` | `unknown` | read by 6 pc(s): field load `0803412A ldr r2, [pc, #0x154]`; field load `08034160 ldm r2, {r2, r3}`; field load `0803417C ldr r2, [pc, #0x10c]`; 5 offset(s) of 5 word(s), 0.70 of the row, 1315 read(s) |
| `0x34330` | `0x34334` | 4 | `R00` | `unknown` | read by 1 pc(s): field load `08034294 ldr r1, [pc, #0x98]`; 1 offset(s) of 1 word(s), 1.00 of the row, 39767 read(s) |
| `0x343A2` | `0x343A4` | 2 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x3455C` | `0x3456C` | 16 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x34816` | `0x3481C` | 6 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x349E8` | `0x349F8` | 16 | `R00` | `pointer-tables` | no reader in the 452-map sweep |
| `0x34AA4` | `0x34AAC` | 8 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x34BA6` | `0x34BB8` | 18 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x34BBC` | `0x34BC0` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x34CE2` | `0x34CF8` | 22 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x34EC0` | `0x34EC8` | 8 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x34ED4` | `0x34ED8` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x413A4` | `0x413A8` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x413D6` | `0x413D8` | 2 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x413DC` | `0x413E0` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x4165C` | `0x4168C` | 48 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x41786` | `0x417AC` | 38 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x41828` | `0x41864` | 60 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x41AFC` | `0x41B00` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x41CB4` | `0x41CE4` | 48 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x41DF4` | `0x41DF8` | 4 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x4208A` | `0x420B0` | 38 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x43140` | `0x43158` | 24 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x43318` | `0x43320` | 8 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x433E2` | `0x433E4` | 2 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x561C4` | `0x561C8` | 4 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x561C8` | `0x561CC` | 4 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x561CC` | `0x561DC` | 16 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x561E0` | `0x561E4` | 4 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x561E4` | `0x561E8` | 4 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x561E8` | `0x561EC` | 4 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x561EC` | `0x561F0` | 4 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x561F0` | `0x561F4` | 4 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x561F4` | `0x561F8` | 4 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x561F8` | `0x5622C` | 52 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x3717C0` | `0x3717C2` | 2 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x37199A` | `0x37199C` | 2 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x372358` | `0x3724E8` | 400 | `R00` | `text/tables` | no reader in the 452-map sweep |
| `0x3724F2` | `0x372574` | 130 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x37259C` | `0x3725C0` | 36 | `R00` | `unknown` | no reader in the 452-map sweep |
| `0x6B7080` | `0x6B7084` | 4 | `R18` | `unknown` | read by 1 pc(s): field load `08013CE8 ldr r0, [r0]`; 1 offset(s) of 1 word(s), 1.00 of the row, 822 read(s) |
| `0x6B7084` | `0x6B72E0` | 604 | `R18` | `unknown` | read by 5 pc(s): field load `080135E2 ldr r4, [r5, r4]`; field load `080135F8 ldr r2, [r5, r2]`; field load `0801364E ldr r1, [r1, #0x18]`; 8 offset(s) of 151 word(s), 0.04 of the row, 1865644 read(s) |
| `0x6B72E0` | `0x6B7400` | 288 | `R18` | `unknown` | no reader in the 452-map sweep |
| `0x6B7400` | `0x6B748C` | 140 | `R18` | `unknown` | no reader in the 452-map sweep |
| `0x6B748C` | `0x6B7590` | 260 | `R18` | `unknown` | no reader in the 452-map sweep |
| `0x6B7590` | `0x6B759C` | 12 | `R18` | `unknown` | no reader in the 452-map sweep |
| `0x6B759C` | `0x6B77A4` | 520 | `R18` | `unknown` | read by 13 pc(s): field load `0800EC18 ldrh r2, [r0, #2]`; field load `0800EC1A ldr r1, [r0, #4]`; field load `0800EC1C ldr r0, [r0, #8]`; 115 offset(s) of 130 word(s), 0.25 of the row, 1681547 read(s) |
| `0x6B77A4` | `0x6B7E8C` | 1768 | `R18` | `unknown` | no reader in the 452-map sweep |
| `0x6FC260` | `0x6FCCC0` | 2656 | `R22` | `unknown` | no reader in the 452-map sweep |
| `0x6FCCC8` | `0x6FD9D0` | 3336 | `R22` | `unknown` | read by 1 pc(s): copy return `0802A9C0 bl #0x8049138`; 832 offset(s) of 834 word(s), 0.30 of the row, 6656 read(s) |
| `0x6FD9D0` | `0x6FDA00` | 48 | `R22` | `unknown` | read by 12 pc(s): field load `0802A88A ldrsb r5, [r0, r3]`; field load `0802A894 ldrsb r5, [r0, r3]`; field load `0802A89A ldrb r2, [r0, #2]`; 24 offset(s) of 12 word(s), 0.67 of the row, 577 read(s) |
| `0x74D248` | `0x74D35C` | 276 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74D35C` | `0x74D360` | 4 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74D360` | `0x74D380` | 32 | `R10` | `pointer-tables` | no reader in the 452-map sweep |
| `0x74D380` | `0x74E200` | 3712 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74E200` | `0x74E208` | 8 | `R10` | `pointer-tables` | no reader in the 452-map sweep |
| `0x74E208` | `0x74E228` | 32 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74E228` | `0x74E234` | 12 | `R10` | `pointer-tables` | no reader in the 452-map sweep |
| `0x74E234` | `0x74E614` | 992 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74E614` | `0x74E968` | 852 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74E968` | `0x74E9F8` | 144 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74E9F8` | `0x74EA40` | 72 | `R10` | `unknown` | read by 4 pc(s): field load `08027A02 ldr r0, [r6]`; field load `08027A34 ldr r0, [r6, #4]`; copy return `08027A6C bl #0x8049138`; 18 offset(s) of 18 word(s), 0.67 of the row, 346 read(s) |
| `0x74EA40` | `0x74EA44` | 4 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74EA44` | `0x74EA48` | 4 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74EA48` | `0x74EA50` | 8 | `R10` | `pointer-tables` | no reader in the 452-map sweep |
| `0x74EA50` | `0x74EA54` | 4 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74EA54` | `0x74EA60` | 12 | `R10` | `pointer-tables` | no reader in the 452-map sweep |
| `0x74EA60` | `0x74EA80` | 32 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74EA80` | `0x74EAC4` | 68 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74EAC4` | `0x74ED7C` | 696 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74ED7C` | `0x74EFEC` | 624 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74EFEC` | `0x74F04C` | 96 | `R10` | `unknown` | no reader in the 452-map sweep |
| `0x74F04C` | `0x74F058` | 12 | `R10` | `pointer-tables` | no reader in the 452-map sweep |
| `0x7B5B64` | `0x7B5B80` | 28 | `R09` | `pointer-tables` | read by 1 pc(s): field load `08012248 ldr r0, [r1, r0]`; 3 offset(s) of 7 word(s), 0.43 of the row, 6 read(s) |
| `0x7B5B80` | `0x7B5B94` | 20 | `R09` | `pointer-tables` | read by 5 pc(s): field load `0803D788 ldr r0, [r0, #0x10]`; field load `0803D80E ldr r0, [r4, #0xc]`; field load `0803D816 ldr r0, [r4, #4]`; 4 offset(s) of 5 word(s), 0.50 of the row, 864143 read(s) |
| `0x7B5B94` | `0x7B6724` | 2960 | `R09` | `unknown` | read by 3 pc(s): field load `0803E53C ldr r3, [r3]`; field load `0803E584 ldr r1, [r1]`; field load `0803EC4A ldr r4, [r0]`; 1 offset(s) of 740 word(s), 0.00 of the row, 16236 read(s) |
| `0x7B6724` | `0x7B6904` | 480 | `R09` | `unknown` | read by 2 pc(s): field load `0803E51E ldr r4, [r5, r4]`; field load `0803E874 ldr r4, [r6, r4]`; 63 offset(s) of 120 word(s), 0.16 of the row, 45466 read(s) |
| `0x7B6904` | `0x7B6A04` | 256 | `R09` | `unknown` | read by 2 pc(s): field load `0803E8F2 ldrh r1, [r3, r1]`; field load `0803EEC0 ldr r1, [r2, r1]`; 27 offset(s) of 64 word(s), 0.17 of the row, 112221 read(s) |
| `0x7B6A04` | `0x7B6C84` | 640 | `R09` | `unknown` | read by 4 pc(s): field load `0803E724 ldrh r1, [r3, r1]`; field load `0803E768 ldrh r0, [r2, r0]`; field load `0803E814 ldrh r2, [r4, r2]`; 25 offset(s) of 160 word(s), 0.03 of the row, 3243 read(s) |
| `0x7B6C84` | `0x7B6E84` | 512 | `R09` | `unknown` | read by 3 pc(s): field load `0803E696 ldrh r1, [r3, r1]`; field load `0803E6DA ldrh r0, [r2, r0]`; field load `0803E7D2 ldrh r2, [r4, r2]`; 12 offset(s) of 128 word(s), 0.04 of the row, 8999 read(s) |
| `0x7B6E84` | `0x7B6EC4` | 64 | `R09` | `unknown` | read by 1 pc(s): field load `0803E8D2 ldrsb r2, [r3, r2]`; 64 offset(s) of 16 word(s), 0.62 of the row, 800 read(s) |
| `0x7B6EC4` | `0x7B6EDC` | 24 | `R09` | `pointer-tables` | no reader in the 452-map sweep |
| `0x7B6EDC` | `0x7B6EE0` | 4 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B6EE0` | `0x7B6EEC` | 12 | `R09` | `pointer-tables` | no reader in the 452-map sweep |
| `0x7B6EEC` | `0x7B72EC` | 1024 | `R09` | `unknown` | read by 33 pc(s): field load `08008756 ldr r7, [r7, r6]`; field load `08008764 ldr r6, [r7, r6]`; field load `0800C384 ldr r2, [r3, r2]`; 256 offset(s) of 256 word(s), 0.39 of the row, 12631 read(s) |
| `0x7B72EC` | `0x7B76EC` | 1024 | `R09` | `unknown` | read by 6 pc(s): field load `08008724 ldr r5, [r4, r5]`; field load `08008726 ldr r4, [r4, r6]`; field load `0802F016 ldr r2, [r3, r2]`; 46 offset(s) of 256 word(s), 0.18 of the row, 1622 read(s) |
| `0x7B76EC` | `0x7B76F0` | 4 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B76F0` | `0x7B76F4` | 4 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B76F4` | `0x7B76F8` | 4 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B76F8` | `0x7B76FC` | 4 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B76FC` | `0x7B7704` | 8 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B7704` | `0x7B7708` | 4 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B7708` | `0x7B7710` | 8 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B7710` | `0x7B7714` | 4 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B7714` | `0x7B7734` | 32 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B7734` | `0x7B773E` | 10 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B773E` | `0x7B7970` | 562 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B7970` | `0x7B797C` | 12 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B797C` | `0x7B79A4` | 40 | `R09` | `unknown` | no reader in the 452-map sweep |
| `0x7B88E8` | `0x7B89A8` | 192 | `R00` | `text/tables` | no reader in the 452-map sweep |
