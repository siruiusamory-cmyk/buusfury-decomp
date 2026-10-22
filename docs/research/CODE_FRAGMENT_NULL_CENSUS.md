# `code-without-entry`'s 11 raw rows: a per-row null

`code-without-entry` is the third rule of `docs/research/ROUTE_TO_100.md`. It holds 11 rows / 20 B,
measured at `python tools\research\raw_remainder.py` (`code-without-entry 11 row(s) 20 B`, total
3,287 rows / 579,162 B, `EXACT` against the gate's raw-data total). The class held 14 rows / 502 B
before its three whole spans were transcribed: 454 B of those are source in `asm/slice_042118.s`,
and the 28 B the walk does not reach are class `unknown` (`0x042118..0x04212C`,
`0x042168..0x042170`). Every remaining row is one half of a single instruction whose other half
lies in a neighbouring raw row of another class, so no instruction can be spelled inside the row
alone. Each row is therefore irreducible as a row: the whole instruction spans two rows, and merging
them is a change to the neighbouring class's split.

## What was searched, and its denominator

| channel | instrument | denominator | hits |
|---|---|---|---|
| branch or Thumb pointer out of transcribed code | `tools/research/thumb_bodies.py` `entries` | 2,715 Thumb instruction rows / 130,513 decoded instructions / 278,016 B | 12 sites over 11 rows / 20 B |
| the same over every transcribed Thumb row byte-permuted (seed 20261017 + row start) | the permutation `tools/research/code_band_entries.py` `source_null` applies | 126,080 decoded Thumb instructions | 1 site (`0x02BDBC`) |
| a spelling inside the row | `tools/research/thumb_body_convert.py --rows` | 11 rows / 20 B | 0 converted, 11 `no-code` (9 `the instruction crosses the row end`, 2 `not an ARMv4T Thumb instruction`) |
| the whole instruction, this row merged with its neighbour | `thumb_body_convert --rows` on the 11 instruction spans | 11 spans / 40 B | 0 converted, 11 `already-source`: no INCBIN row in the tree has that span |
| a pointer-table word with bit 0 set, a class-table method slot or a `PUSH`-shape entry | `thumb_bodies.entries` with `pointer`, `method`, `prologue` | the same 11 rows | 0 beyond the 12 branch sites |
| a word-aligned word in the image holding an address inside a row | `tools/research/consumer_search.py` `sites` | 8,388,608 image bytes / 2,097,152 grid words | 0 |
| a decoded pc-relative literal load naming a row | `consumer_search.py` `literal_loads` | 2,783 ledger thumb/arm rows / 292,722 B | 0 |
| a read of the row in play | the 452-map read sweep `RAW_READERS.csv` | 452 maps / 3,316 census rows | 0 (all 11 rows listed, `reader_pcs` empty) |

Before the three spans were transcribed the branch channel read 22 sites over 14 rows / 502 B
against 9 sites over the same 126,080 permuted instructions: 0.1686 against 0.0714 sites per 1,000
instructions, ratio 2.36. At the current class the same channel reads 12 sites over 130,513
instructions against 1 over 126,080. The instrument still cannot convert a fragment: its walk
stops on the row's own first instruction with `the instruction crosses the row end` (9 rows) or
`not an ARMv4T Thumb instruction` (2 rows), which is `thumb_body_convert`'s own refusal text:

    python tools\research\thumb_body_convert.py --rows <the 11 class rows>
    rows 11: converted 0 (0 walked B, 0 pool B), assembler-refused 0, no-code 11, already-source 0

## Per-row null

| row | bytes | the instruction it is half of | entry site | the other half | read | stays raw because |
|---|---|---|---|---|---|---|
| `0x005C3E..0x005C40` | 2 | `bl #0x803D8A0`, first halfword | `Thumb 0x08005c32 beq #0x8005c3e` | `0x005C40..0x005C42`, row `0x005C40..0x005C44` `text/tables` | none | the second halfword is not in converted source |
| `0x013074..0x013076` | 2 | `bl #0x800ED18`, second halfword (head at `0x013072`) | `Thumb 0x08012fb8 bvc #0x8013074` | `0x013072..0x013074`, row `0x013072..0x013074` `text/tables` | none | the head is not in converted source |
| `0x01E13C..0x01E13E` | 2 | `bl #0x8019BF4`, first halfword | `Thumb 0x0801e130 bne #0x801e13c` and `Thumb 0x0801e136 bne #0x801e13c` | `0x01E13E..0x01E140`, row `0x01E13E..0x01E142` `text/tables` | none | the second halfword is not in converted source |
| `0x026042..0x026044` | 2 | `bl #0x8024C04`, first halfword | `Thumb 0x08026020 beq #0x8026042` | `0x026044..0x026046`, row `0x026044..0x026048` `text/tables` | none | the second halfword is not in converted source |
| `0x0263B8..0x0263BA` | 2 | `bl #0x8024C04`, first halfword | `Thumb 0x08026396 beq #0x80263b8` | `0x0263BA..0x0263BC`, row `0x0263BA..0x0263BE` `text/tables` | none | the second halfword is not in converted source |
| `0x0278DC..0x0278DE` | 2 | `bl #0x802770C`, first halfword | `Thumb 0x080279d8 blo #0x80278dc` | `0x0278DE..0x0278E0`, row `0x0278DE..0x0278E2` `text/tables` | none | the second halfword is not in converted source |
| `0x02A098..0x02A09A` | 2 | `bl #0x803BB48`, first halfword | `Thumb 0x0802a084 bgt #0x802a098` | `0x02A09A..0x02A09C`, row `0x02A09A..0x02A09E` `text/tables` | none | the second halfword is not in converted source |
| `0x02BDBC..0x02BDBE` | 2 | `bl #0x800DA3E`, first halfword | `Thumb 0x0802bdae bne #0x802bdbc` | `0x02BDBE..0x02BDC0`, row `0x02BDBE..0x02BDC2` `text/tables` | none | the second halfword is not in converted source |
| `0x02D79C..0x02D79D` | 1 | `push {r0-r7, lr}`, low byte | `Thumb 0x0802d15e bl #0x802d79c` | `0x02D79D..0x02D79E`, row `0x02D79D..0x02D826` `text/tables` | none | the high byte is not in converted source |
| `0x03018C..0x03018D` | 1 | `push {r4, lr}`, low byte | `Thumb 0x08030006 bl #0x803018c` | `0x03018D..0x03018E`, row `0x03018D..0x0301B8` `unknown` | none | the high byte is in an `unknown` row |
| `0x04F00C..0x04F00E` | 2 | `bl #0x803D5B8`, second halfword (head at `0x04F00A`) | `Thumb 0x0804f000 bpl #0x804f00c` | `0x04F00A..0x04F00C`, row `0x04F00A..0x04F00C` `text/tables` | none | the head is not in converted source |

Every entry site is a decoded branch in transcribed code, so each row is entered; the entry does
not make the row spellable. The bytes before and after each row are converted source except where
the table names a raw neighbour, and no `text/tables` or `unknown` row carries a route onto this
class. Spelling a fragment needs its whole instruction, and that instruction crosses the row
boundary, so it is not a span the tree carries as one INCBIN row:
`thumb_body_convert --rows <the 11 instruction spans>` prints `rows 0: converted 0 (0 walked B,
0 pool B), assembler-refused 0, no-code 0, already-source 11`. Converting one therefore needs its
row merged with the neighbour's, which changes the neighbouring row of another class - not this
class's route. The 12 sites, 11 rows and 20 B are the class line, and the class line and the gate's
raw-data total agree at every step recorded above.

## The three whole spans, and how CODE-BAND-005's hold was answered

| span | bytes | walked bytes | entry sites |
|---|---|---|---|
| `0x042118..0x042188` | 112 | 84 | `0x080420CC beq`, `0x080420D6 beq`, `0x080420DC beq`, `0x08042112 beq`, `0x08042114 bgt` |
| `0x0426D0..0x042750` | 128 | 128 | `0x08042604 b`, `0x08042606 b` |
| `0x042784..0x042876` | 242 | 242 | `0x08042608 b`, `0x08042638 b`, `0x0804263A b` |

`docs/research/CODE_BAND_005.md` C2 held these because the entry set did not beat its null - 4 rows /
482 B against a source-permuted 124 rows / 28,428 B - over a 1,174-row population. At this class's own
denominator the same channel beats the same permutation (first table), and for `0x042118` the entry
needs no null: the transcribed Thumb row `0x0420B0..0x042118` decodes to `cmp r0, #0x41` at
`0x042116`, which transfers nowhere and ends on the row boundary, so the next instruction executed is
`beq #0x80420E6` at `0x042118`. The 454 walked bytes reassemble byte-exact under the assembler. The
28 B the walk does not reach (`0x042118..0x04212C`, `0x042168..0x042170`) stay raw and class
`unknown`, outside this class.

    python tools\research\thumb_body_convert.py --rows <a CSV of these three spans> --write
    python tools\research\raw_remainder.py --check
