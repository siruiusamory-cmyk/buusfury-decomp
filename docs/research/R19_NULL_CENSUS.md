# R19's 574 raw rows: a per-row null

`R19` is the raw-labeled run `0x071C90..0x0945C0`, 574 rows / 42,756 B, measured at
`python tools\research\raw_remainder.py` and identical to the gate's raw-data total
(`raw-data=586580`). Every row carries class `unreached` in
`docs/research/CODE_BAND_R19.csv` with proof `no instrument above fired`
(`python tools\research\code_band.py --region R19 --outside --check`).

## What was searched, and its denominator

| channel | instrument | denominator | hits |
|---|---|---|---|
| pc-relative literal load in transcribed code | `tools/research/consumer_search.py` `literal_loads` | 2,783 ledger thumb/arm rows / 292,722 B | 0 |
| branch or Thumb function pointer out of transcribed code | `tools/research/thumb_bodies.py` `entries` | 2,713 Thumb instruction rows / 130,370 instructions | 0 |
| class-table method slot | `thumb_bodies.method_entries` | 150 class bases, 5 class-table rows | 0 |
| pointer-table word with bit 0 set | `thumb_bodies.pointer_entries` | 124 carrier rows / 392 grid words | 0 |

    python -m tools.research.consumer_search --image baserom.gba --range 0x71C90-0x945C0

prints `0 decoded pc-literal load(s)` over that denominator. A row can be named without being
read: 2,506 word-aligned words in the image hold an address inside a row, 1,069 of
them in INCBIN rows, 1,434 in data rows and 3 in one ledger Thumb row, where they
are three words at `0x6FF50`, `0x6FF78` and `0x6FF7C` in an inline data run that no decoded
pc-relative load loads. A table word is a name, not a consumer
(`docs/research/RAW_CITATIONS.csv` route `-` on every row agrees).

## Byte statistics

Entropy 0.81..5.36 bits/byte, zero-byte share 0.00..0.75 and no row all
zero. 269 rows begin with an in-image address, 305 do not. The bytes are
the code band's gaps, not bodies: no row's walk beats its own control.

## The shape predicate, its control and its two hits

Shape is the predicate `docs/research/CODE_BAND_ENTRIES.csv` uses: `code-shaped` when the
Thumb walk from the row's own start ends in a return and the same walk on the row permuted
with `random.Random(20261017 + start)` does not; else `table-pointer` when the row's first
word is an in-image address; else `table`. Counts: `code-shaped` 2, `table-pointer` 269,
`table` 303.

The predicate's own null is level with its hits: row-start walks return in 4 of 574 rows, and
walks from the same rows entered at +2, +4, +6 and +8 return in 4 of 574 each, while the
permuted copies return in 2 of 574. The two hits:

| row | terminal | why it is not code |
|---|---|---|
| `0x07BDE8..0x07BE14` | `0x07BDFC pop {r3,r5,r6,r7,pc}` | the word at `0x07BDFC` is `0x0807BDE8`, a pointer to this row's own start, so the terminal halfword is the low half of a pointer |
| `0x07EE9C..0x07EFA8` | `0x07EEBE bx r0` | the walk ends 36 B into a 268 B run of `lsls`/`str`/`asrs` nonsense, and no entry channel names the row |

## The per-row null

Each line: file offsets, bytes, entropy, zero-byte share, word-aligned words holding an
in-image address, shape, band class, and the verdict. `none` means no instruction in the four
channels above names a byte of the row, at the denominators quoted, and the row's shape is level with the predicate's control.

| start | end | bytes | ent | zero | in-image words | shape | class | readers |
|---|---|---|---|---|---|---|---|---|
| `0x072974` | `0x0729B0` | 60 | 4.23 | 0.22 | 9 | `table` | `unreached` | none |
| `0x072A44` | `0x072A48` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x072A48` | `0x072C9C` | 596 | 4.66 | 0.21 | 1 | `table` | `unreached` | none |
| `0x072CD4` | `0x072D10` | 60 | 3.79 | 0.28 | 4 | `table-pointer` | `unreached` | none |
| `0x072D44` | `0x072D74` | 48 | 4.0 | 0.25 | 3 | `table-pointer` | `unreached` | none |
| `0x072DA4` | `0x072DD4` | 48 | 3.92 | 0.25 | 3 | `table-pointer` | `unreached` | none |
| `0x072E04` | `0x072E28` | 36 | 3.78 | 0.25 | 2 | `table-pointer` | `unreached` | none |
| `0x072E54` | `0x072E84` | 48 | 3.88 | 0.25 | 3 | `table-pointer` | `unreached` | none |
| `0x072EB4` | `0x072EF0` | 60 | 4.0 | 0.18 | 4 | `table-pointer` | `unreached` | none |
| `0x072F24` | `0x072F54` | 48 | 3.98 | 0.19 | 4 | `table-pointer` | `unreached` | none |
| `0x072F84` | `0x072FB4` | 48 | 4.18 | 0.19 | 3 | `table-pointer` | `unreached` | none |
| `0x072FE4` | `0x073008` | 36 | 4.18 | 0.19 | 2 | `table-pointer` | `unreached` | none |
| `0x073034` | `0x073064` | 48 | 4.19 | 0.19 | 3 | `table-pointer` | `unreached` | none |
| `0x073094` | `0x0730AC` | 24 | 3.48 | 0.29 | 1 | `table` | `unreached` | none |
| `0x073104` | `0x073994` | 2192 | 5.36 | 0.18 | 134 | `table` | `unreached` | none |
| `0x073994` | `0x073AF8` | 356 | 4.44 | 0.29 | 31 | `table` | `unreached` | none |
| `0x073D9C` | `0x073EF8` | 348 | 5.09 | 0.19 | 17 | `table` | `unreached` | none |
| `0x0741AC` | `0x07430C` | 352 | 5.15 | 0.16 | 18 | `table` | `unreached` | none |
| `0x074314` | `0x074318` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x074334` | `0x074338` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x07435C` | `0x074398` | 60 | 3.67 | 0.38 | 7 | `table-pointer` | `unreached` | none |
| `0x07439C` | `0x0743A4` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x0743C0` | `0x0743FC` | 60 | 3.76 | 0.35 | 7 | `table-pointer` | `unreached` | none |
| `0x074404` | `0x074408` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x074424` | `0x074428` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x07444C` | `0x074488` | 60 | 3.67 | 0.38 | 7 | `table-pointer` | `unreached` | none |
| `0x07448C` | `0x074494` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x0744B0` | `0x0744EC` | 60 | 3.57 | 0.4 | 7 | `table-pointer` | `unreached` | none |
| `0x0744F0` | `0x0744F8` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x074518` | `0x07457C` | 100 | 4.07 | 0.32 | 12 | `table-pointer` | `unreached` | none |
| `0x07457C` | `0x07458C` | 16 | 2.85 | 0.31 | 1 | `table` | `unreached` | none |
| `0x074D08` | `0x074D10` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x074D2C` | `0x074D38` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x074E64` | `0x074E80` | 28 | 3.8 | 0.21 | 4 | `table-pointer` | `unreached` | none |
| `0x074E80` | `0x074EA8` | 40 | 4.29 | 0.17 | 1 | `table` | `unreached` | none |
| `0x074F44` | `0x074F50` | 12 | 2.52 | 0.33 | 0 | `table` | `unreached` | none |
| `0x074F6C` | `0x074F7C` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x074F98` | `0x074FA8` | 16 | 3.0 | 0.25 | 1 | `table-pointer` | `unreached` | none |
| `0x074FC4` | `0x074FD4` | 16 | 2.98 | 0.31 | 1 | `table-pointer` | `unreached` | none |
| `0x074FF0` | `0x075000` | 16 | 2.78 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x07509C` | `0x0750D4` | 56 | 3.93 | 0.18 | 8 | `table-pointer` | `unreached` | none |
| `0x075104` | `0x075114` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x075130` | `0x075140` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x07515C` | `0x075164` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x0751AC` | `0x0751C8` | 28 | 3.61 | 0.21 | 4 | `table-pointer` | `unreached` | none |
| `0x0751C8` | `0x07526C` | 164 | 4.82 | 0.2 | 15 | `table` | `unreached` | none |
| `0x07526C` | `0x075278` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x07535C` | `0x0753D0` | 116 | 4.37 | 0.22 | 16 | `table-pointer` | `unreached` | none |
| `0x0753D0` | `0x0753F0` | 32 | 3.04 | 0.31 | 0 | `table` | `unreached` | none |
| `0x075434` | `0x075438` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x075454` | `0x07545C` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x075478` | `0x075480` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x07549C` | `0x0754A4` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x0754C0` | `0x0754C8` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x0754E4` | `0x0754EC` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x075508` | `0x075510` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x07552C` | `0x075534` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x075550` | `0x075564` | 20 | 3.02 | 0.4 | 1 | `table` | `unreached` | none |
| `0x0755AC` | `0x07561C` | 112 | 4.64 | 0.15 | 16 | `table-pointer` | `unreached` | none |
| `0x0756A0` | `0x0756BC` | 28 | 3.59 | 0.29 | 4 | `table-pointer` | `unreached` | none |
| `0x075780` | `0x07579C` | 28 | 3.54 | 0.29 | 4 | `table-pointer` | `unreached` | none |
| `0x0757C4` | `0x0757C8` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x0757E8` | `0x0757F0` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x07580C` | `0x075810` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x075830` | `0x075838` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x075854` | `0x075858` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x075878` | `0x075880` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x07589C` | `0x0758A0` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x0758E0` | `0x0758FC` | 28 | 3.75 | 0.25 | 4 | `table-pointer` | `unreached` | none |
| `0x0758FC` | `0x07593C` | 64 | 4.14 | 0.14 | 0 | `table` | `unreached` | none |
| `0x075944` | `0x075948` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x075964` | `0x075968` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x075998` | `0x075A44` | 172 | 4.96 | 0.2 | 18 | `table-pointer` | `unreached` | none |
| `0x075A4C` | `0x075A58` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x075A60` | `0x075A64` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x075AA4` | `0x075ADC` | 56 | 4.06 | 0.25 | 6 | `table-pointer` | `unreached` | none |
| `0x075AE0` | `0x075AF4` | 20 | 2.68 | 0.4 | 0 | `table` | `unreached` | none |
| `0x075B18` | `0x075BA8` | 144 | 4.21 | 0.28 | 20 | `table-pointer` | `unreached` | none |
| `0x075DCC` | `0x075E3C` | 112 | 3.31 | 0.43 | 10 | `table` | `unreached` | none |
| `0x075E58` | `0x075E84` | 44 | 3.33 | 0.11 | 10 | `table-pointer` | `unreached` | none |
| `0x075EB4` | `0x075EB8` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x075ED4` | `0x075ED8` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x075EF4` | `0x075EF8` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x075F20` | `0x075FC0` | 160 | 4.49 | 0.28 | 20 | `table` | `unreached` | none |
| `0x075FC0` | `0x07600C` | 76 | 4.22 | 0.29 | 9 | `table` | `unreached` | none |
| `0x07600C` | `0x076044` | 56 | 4.15 | 0.21 | 0 | `table` | `unreached` | none |
| `0x076084` | `0x076180` | 252 | 4.96 | 0.23 | 24 | `table-pointer` | `unreached` | none |
| `0x076188` | `0x07618C` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x0761AC` | `0x0761B4` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x076350` | `0x076354` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x076380` | `0x076388` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x0763A8` | `0x0763B0` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x0763DC` | `0x0763F4` | 24 | 2.92 | 0.42 | 3 | `table-pointer` | `unreached` | none |
| `0x07656C` | `0x076588` | 28 | 3.75 | 0.25 | 4 | `table-pointer` | `unreached` | none |
| `0x0765B0` | `0x0765C0` | 16 | 3.0 | 0.25 | 0 | `table` | `unreached` | none |
| `0x076678` | `0x076694` | 28 | 3.73 | 0.21 | 4 | `table-pointer` | `unreached` | none |
| `0x076694` | `0x0766FC` | 104 | 4.81 | 0.13 | 5 | `table` | `unreached` | none |
| `0x0767C0` | `0x0767CC` | 12 | 1.95 | 0.58 | 1 | `table` | `unreached` | none |
| `0x0768B4` | `0x076934` | 128 | 4.64 | 0.25 | 10 | `table-pointer` | `unreached` | none |
| `0x076A64` | `0x076A84` | 32 | 3.6 | 0.31 | 5 | `table-pointer` | `unreached` | none |
| `0x076A84` | `0x076A94` | 16 | 2.98 | 0.31 | 0 | `table` | `unreached` | none |
| `0x076AE0` | `0x076AFC` | 28 | 3.59 | 0.29 | 4 | `table-pointer` | `unreached` | none |
| `0x076AFC` | `0x076B30` | 52 | 4.19 | 0.23 | 6 | `table` | `unreached` | none |
| `0x076B30` | `0x076B54` | 36 | 3.94 | 0.17 | 0 | `table` | `unreached` | none |
| `0x076B60` | `0x076B64` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x076BD4` | `0x076C24` | 80 | 4.43 | 0.21 | 4 | `table` | `unreached` | none |
| `0x076C2C` | `0x076C3F` | 19 | 3.07 | 0.26 | 0 | `table` | `unreached` | none |
| `0x076C3F` | `0x076C4C` | 13 | 2.93 | 0.31 | 0 | `table` | `unreached` | none |
| `0x076C94` | `0x076C98` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x076D48` | `0x076D5C` | 20 | 3.1 | 0.35 | 1 | `table` | `unreached` | none |
| `0x076D78` | `0x076D7C` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x076DB4` | `0x076DC4` | 16 | 2.5 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x076DE0` | `0x076DE8` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x076E38` | `0x076ECC` | 148 | 4.36 | 0.27 | 21 | `table-pointer` | `unreached` | none |
| `0x076ECC` | `0x076EE0` | 20 | 2.88 | 0.4 | 0 | `table` | `unreached` | none |
| `0x076F6C` | `0x076F74` | 8 | 2.41 | 0.38 | 0 | `table` | `unreached` | none |
| `0x077010` | `0x077028` | 24 | 3.31 | 0.38 | 1 | `table` | `unreached` | none |
| `0x077044` | `0x077054` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x077070` | `0x077090` | 32 | 2.79 | 0.34 | 4 | `table-pointer` | `unreached` | none |
| `0x0770AC` | `0x0770D0` | 36 | 3.09 | 0.33 | 5 | `table-pointer` | `unreached` | none |
| `0x0770EC` | `0x0770F0` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x07714C` | `0x077168` | 28 | 3.77 | 0.21 | 5 | `table-pointer` | `unreached` | none |
| `0x07720C` | `0x077210` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x07722C` | `0x077230` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x07724C` | `0x077250` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x077330` | `0x07733C` | 12 | 2.58 | 0.33 | 0 | `table` | `unreached` | none |
| `0x0773BC` | `0x077410` | 84 | 3.32 | 0.33 | 6 | `table` | `unreached` | none |
| `0x07742C` | `0x077488` | 92 | 3.55 | 0.26 | 11 | `table-pointer` | `unreached` | none |
| `0x0774A4` | `0x0774C8` | 36 | 3.52 | 0.14 | 6 | `table-pointer` | `unreached` | none |
| `0x077538` | `0x0775A0` | 104 | 4.65 | 0.14 | 17 | `table-pointer` | `unreached` | none |
| `0x0775A0` | `0x0775D0` | 48 | 4.09 | 0.27 | 5 | `table` | `unreached` | none |
| `0x0775D0` | `0x077604` | 52 | 4.28 | 0.27 | 4 | `table` | `unreached` | none |
| `0x077618` | `0x07761C` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x077638` | `0x077640` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x07765C` | `0x077664` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x077680` | `0x077688` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x0776A4` | `0x0776AC` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x0776DC` | `0x077768` | 140 | 4.23 | 0.32 | 16 | `table` | `unreached` | none |
| `0x077790` | `0x077794` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x0777B0` | `0x0777B4` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x0777D0` | `0x0777D4` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x0777F0` | `0x0777F4` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x077810` | `0x077814` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x077830` | `0x077834` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x077850` | `0x077854` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x077870` | `0x077874` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x077890` | `0x077894` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x0778D4` | `0x07790C` | 56 | 3.65 | 0.32 | 8 | `table-pointer` | `unreached` | none |
| `0x077930` | `0x077A44` | 276 | 4.42 | 0.28 | 28 | `table` | `unreached` | none |
| `0x077A88` | `0x077AB0` | 40 | 4.23 | 0.2 | 5 | `table` | `unreached` | none |
| `0x077D88` | `0x077D94` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x077DC0` | `0x077E10` | 80 | 3.94 | 0.21 | 0 | `table` | `unreached` | none |
| `0x077E14` | `0x077E1C` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x077E38` | `0x077F10` | 216 | 4.46 | 0.26 | 24 | `table-pointer` | `unreached` | none |
| `0x077F10` | `0x0780FC` | 492 | 4.86 | 0.23 | 41 | `table` | `unreached` | none |
| `0x0780FC` | `0x0782FC` | 512 | 4.9 | 0.23 | 43 | `table` | `unreached` | none |
| `0x0782FC` | `0x07830C` | 16 | 2.98 | 0.31 | 0 | `table` | `unreached` | none |
| `0x078338` | `0x078348` | 16 | 2.77 | 0.31 | 1 | `table-pointer` | `unreached` | none |
| `0x078364` | `0x078374` | 16 | 3.27 | 0.31 | 1 | `table-pointer` | `unreached` | none |
| `0x078390` | `0x0783A0` | 16 | 3.0 | 0.25 | 1 | `table-pointer` | `unreached` | none |
| `0x0783BC` | `0x0783CC` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x0783E8` | `0x0783F8` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x078414` | `0x07841C` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x078438` | `0x078440` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x07845C` | `0x07846C` | 16 | 3.25 | 0.25 | 1 | `table-pointer` | `unreached` | none |
| `0x078488` | `0x078498` | 16 | 3.38 | 0.25 | 1 | `table-pointer` | `unreached` | none |
| `0x0784DC` | `0x078538` | 92 | 4.47 | 0.25 | 11 | `table` | `unreached` | none |
| `0x078538` | `0x078584` | 76 | 3.62 | 0.07 | 0 | `table` | `unreached` | none |
| `0x0785A8` | `0x078628` | 128 | 2.84 | 0.47 | 12 | `table-pointer` | `unreached` | none |
| `0x078644` | `0x078670` | 44 | 2.96 | 0.0 | 11 | `table-pointer` | `unreached` | none |
| `0x078678` | `0x0786C8` | 80 | 3.8 | 0.34 | 8 | `table` | `unreached` | none |
| `0x0786D0` | `0x0786D4` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x0786F0` | `0x078700` | 16 | 2.5 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x078724` | `0x078784` | 96 | 3.94 | 0.35 | 12 | `table-pointer` | `unreached` | none |
| `0x078788` | `0x078798` | 16 | 2.5 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x0787B8` | `0x0787D0` | 24 | 3.0 | 0.42 | 3 | `table-pointer` | `unreached` | none |
| `0x0787D4` | `0x0787DC` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x0787F8` | `0x078814` | 28 | 3.34 | 0.36 | 4 | `table-pointer` | `unreached` | none |
| `0x078814` | `0x078824` | 16 | 3.38 | 0.25 | 1 | `table` | `unreached` | none |
| `0x078854` | `0x078BC0` | 876 | 4.89 | 0.24 | 66 | `table` | `unreached` | none |
| `0x078BCC` | `0x078BE4` | 24 | 3.2 | 0.42 | 1 | `table` | `unreached` | none |
| `0x078C00` | `0x078C08` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x078C50` | `0x078C60` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x078C80` | `0x078C98` | 24 | 2.71 | 0.5 | 2 | `table` | `unreached` | none |
| `0x078C9C` | `0x078CAC` | 16 | 3.25 | 0.25 | 0 | `table` | `unreached` | none |
| `0x078CB4` | `0x078CC0` | 12 | 2.29 | 0.5 | 0 | `table` | `unreached` | none |
| `0x078D10` | `0x078D20` | 16 | 3.0 | 0.25 | 1 | `table-pointer` | `unreached` | none |
| `0x078D58` | `0x078D60` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x078D7C` | `0x078D8C` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x078DB8` | `0x078E44` | 140 | 4.64 | 0.24 | 17 | `table` | `unreached` | none |
| `0x078E44` | `0x078E54` | 16 | 3.08 | 0.25 | 0 | `table` | `unreached` | none |
| `0x078E74` | `0x078E84` | 16 | 3.08 | 0.25 | 0 | `table` | `unreached` | none |
| `0x078EA0` | `0x078EB0` | 16 | 3.2 | 0.25 | 1 | `table-pointer` | `unreached` | none |
| `0x078ECC` | `0x078EDC` | 16 | 3.08 | 0.25 | 0 | `table` | `unreached` | none |
| `0x078EF8` | `0x078F04` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x078FA0` | `0x079144` | 420 | 5.14 | 0.19 | 37 | `table-pointer` | `unreached` | none |
| `0x079144` | `0x0791E4` | 160 | 4.84 | 0.23 | 10 | `table` | `unreached` | none |
| `0x0791E4` | `0x079370` | 396 | 3.78 | 0.35 | 43 | `table` | `unreached` | none |
| `0x0793BC` | `0x0793C0` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x0793C0` | `0x0793C8` | 8 | 1.55 | 0.62 | 0 | `table` | `unreached` | none |
| `0x0793F0` | `0x0793F8` | 8 | 2.16 | 0.38 | 0 | `table` | `unreached` | none |
| `0x0794C4` | `0x0794D0` | 12 | 2.79 | 0.0 | 3 | `table-pointer` | `unreached` | none |
| `0x0794D0` | `0x0794E0` | 16 | 3.45 | 0.19 | 0 | `table` | `unreached` | none |
| `0x079524` | `0x0798E8` | 964 | 4.76 | 0.1 | 20 | `table` | `unreached` | none |
| `0x0798E8` | `0x079920` | 56 | 4.33 | 0.21 | 6 | `table` | `unreached` | none |
| `0x07997C` | `0x079AF4` | 376 | 4.87 | 0.22 | 37 | `table` | `unreached` | none |
| `0x079C14` | `0x079C70` | 92 | 4.4 | 0.25 | 11 | `table` | `unreached` | none |
| `0x079C70` | `0x079CD8` | 104 | 4.55 | 0.13 | 0 | `table` | `unreached` | none |
| `0x079D38` | `0x079D54` | 28 | 3.74 | 0.29 | 1 | `table` | `unreached` | none |
| `0x079D70` | `0x079D90` | 32 | 3.75 | 0.28 | 1 | `table` | `unreached` | none |
| `0x079DAC` | `0x079DBC` | 16 | 3.0 | 0.25 | 1 | `table-pointer` | `unreached` | none |
| `0x079DD8` | `0x079DE8` | 16 | 3.0 | 0.25 | 1 | `table-pointer` | `unreached` | none |
| `0x079E04` | `0x079E14` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x079E30` | `0x079E40` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x079E5C` | `0x079E6C` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x079E88` | `0x079E98` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x079EB4` | `0x079EC4` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x079EE0` | `0x079EF0` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x079F0C` | `0x079F1C` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x079F38` | `0x079F48` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x079F64` | `0x079F74` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x079F90` | `0x079FA0` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x079FBC` | `0x079FCC` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x079FE8` | `0x079FF8` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x07A014` | `0x07A020` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x07A0DC` | `0x07A294` | 440 | 5.11 | 0.22 | 38 | `table` | `unreached` | none |
| `0x07A350` | `0x07A358` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x07A374` | `0x07A384` | 16 | 2.38 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x07A3A0` | `0x07A3B0` | 16 | 2.38 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x07A3CC` | `0x07A3E4` | 24 | 3.11 | 0.38 | 1 | `table` | `unreached` | none |
| `0x07A424` | `0x07A460` | 60 | 4.02 | 0.25 | 9 | `table-pointer` | `unreached` | none |
| `0x07A498` | `0x07A4A8` | 16 | 2.52 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x07A4C4` | `0x07A4D4` | 16 | 2.52 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x07A4F0` | `0x07A500` | 16 | 2.25 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x07A51C` | `0x07A52C` | 16 | 2.25 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x07A548` | `0x07A558` | 16 | 2.5 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x07A574` | `0x07A584` | 16 | 2.52 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x07A5A0` | `0x07A5B0` | 16 | 2.52 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x07A5CC` | `0x07A5DC` | 16 | 2.98 | 0.31 | 1 | `table-pointer` | `unreached` | none |
| `0x07A5F8` | `0x07A608` | 16 | 3.0 | 0.25 | 1 | `table-pointer` | `unreached` | none |
| `0x07A624` | `0x07A634` | 16 | 2.52 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x07A650` | `0x07A660` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x07A67C` | `0x07A68C` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x07A6FC` | `0x07A714` | 24 | 3.17 | 0.33 | 3 | `table-pointer` | `unreached` | none |
| `0x07AAA4` | `0x07AB1C` | 120 | 4.43 | 0.27 | 13 | `table-pointer` | `unreached` | none |
| `0x07AB24` | `0x07ACA0` | 380 | 4.89 | 0.15 | 15 | `table` | `unreached` | none |
| `0x07AD3C` | `0x07AD48` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x07AE78` | `0x07AE98` | 32 | 2.81 | 0.41 | 4 | `table` | `unreached` | none |
| `0x07AFE8` | `0x07AFF8` | 16 | 3.2 | 0.25 | 0 | `table` | `unreached` | none |
| `0x07B1AC` | `0x07B1F4` | 72 | 4.05 | 0.29 | 8 | `table-pointer` | `unreached` | none |
| `0x07B3B0` | `0x07B3CC` | 28 | 3.71 | 0.14 | 0 | `table` | `unreached` | none |
| `0x07B580` | `0x07B5C4` | 68 | 4.62 | 0.16 | 4 | `table` | `unreached` | none |
| `0x07B6CC` | `0x07B6DC` | 16 | 2.65 | 0.44 | 2 | `table` | `unreached` | none |
| `0x07B96C` | `0x07B97C` | 16 | 2.65 | 0.44 | 2 | `table` | `unreached` | none |
| `0x07B980` | `0x07B990` | 16 | 3.0 | 0.25 | 0 | `table` | `unreached` | none |
| `0x07BA24` | `0x07BA60` | 60 | 3.64 | 0.35 | 8 | `table-pointer` | `unreached` | none |
| `0x07BDE8` | `0x07BE14` | 44 | 3.89 | 0.3 | 3 | `code-shaped` | `unreached` | none |
| `0x07BFAC` | `0x07BFDC` | 48 | 2.82 | 0.4 | 6 | `table` | `unreached` | none |
| `0x07BFE8` | `0x07C044` | 92 | 4.15 | 0.28 | 10 | `table-pointer` | `unreached` | none |
| `0x07C044` | `0x07C0A4` | 96 | 4.36 | 0.15 | 0 | `table` | `unreached` | none |
| `0x07C0B8` | `0x07C0BC` | 4 | 2.0 | 0.25 | 0 | `table` | `unreached` | none |
| `0x07C0D8` | `0x07C0E8` | 16 | 3.28 | 0.19 | 0 | `table` | `unreached` | none |
| `0x07C104` | `0x07C114` | 16 | 3.11 | 0.19 | 0 | `table` | `unreached` | none |
| `0x07C130` | `0x07C13C` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x07C188` | `0x07C254` | 204 | 4.92 | 0.21 | 14 | `table-pointer` | `unreached` | none |
| `0x07C254` | `0x07C440` | 492 | 5.05 | 0.25 | 38 | `table` | `unreached` | none |
| `0x07C458` | `0x07C4B4` | 92 | 3.79 | 0.36 | 11 | `table-pointer` | `unreached` | none |
| `0x07C4BC` | `0x07C4D8` | 28 | 3.85 | 0.11 | 0 | `table` | `unreached` | none |
| `0x07C56C` | `0x07C5C8` | 92 | 4.43 | 0.26 | 6 | `table` | `unreached` | none |
| `0x07C5CC` | `0x07C6B4` | 232 | 4.69 | 0.22 | 9 | `table` | `unreached` | none |
| `0x07C6B4` | `0x07C6CC` | 24 | 3.49 | 0.04 | 0 | `table` | `unreached` | none |
| `0x07C760` | `0x07C7FC` | 156 | 4.34 | 0.31 | 12 | `table-pointer` | `unreached` | none |
| `0x07C894` | `0x07C950` | 188 | 3.97 | 0.37 | 20 | `table-pointer` | `unreached` | none |
| `0x07C958` | `0x07CA40` | 232 | 4.66 | 0.23 | 9 | `table` | `unreached` | none |
| `0x07CAD4` | `0x07CB14` | 64 | 3.68 | 0.36 | 6 | `table-pointer` | `unreached` | none |
| `0x07CB14` | `0x07CBFC` | 232 | 4.65 | 0.22 | 9 | `table` | `unreached` | none |
| `0x07CBFC` | `0x07CD38` | 316 | 4.89 | 0.23 | 18 | `table` | `unreached` | none |
| `0x07CD3C` | `0x07CD48` | 12 | 2.45 | 0.42 | 0 | `table` | `unreached` | none |
| `0x07CDB0` | `0x07CDEC` | 60 | 4.03 | 0.23 | 0 | `table` | `unreached` | none |
| `0x07CE28` | `0x07CE84` | 92 | 3.82 | 0.36 | 11 | `table-pointer` | `unreached` | none |
| `0x07CF20` | `0x07CF9C` | 124 | 3.79 | 0.38 | 13 | `table-pointer` | `unreached` | none |
| `0x07CF9C` | `0x07D080` | 228 | 4.65 | 0.24 | 8 | `table` | `unreached` | none |
| `0x07D114` | `0x07D180` | 108 | 3.81 | 0.37 | 12 | `table-pointer` | `unreached` | none |
| `0x07D1D0` | `0x07D28C` | 188 | 3.95 | 0.37 | 20 | `table-pointer` | `unreached` | none |
| `0x07D34C` | `0x07D38C` | 64 | 3.72 | 0.36 | 6 | `table-pointer` | `unreached` | none |
| `0x07D3D8` | `0x07D438` | 96 | 3.46 | 0.42 | 10 | `table-pointer` | `unreached` | none |
| `0x07D440` | `0x07D560` | 288 | 4.81 | 0.23 | 12 | `table` | `unreached` | none |
| `0x07D618` | `0x07D658` | 64 | 3.74 | 0.34 | 6 | `table-pointer` | `unreached` | none |
| `0x07D658` | `0x07D740` | 232 | 4.69 | 0.22 | 9 | `table` | `unreached` | none |
| `0x07D740` | `0x07D84C` | 268 | 4.87 | 0.24 | 18 | `table` | `unreached` | none |
| `0x07D8D0` | `0x07D8D4` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x07D8F0` | `0x07D8F4` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x07D944` | `0x07D9A0` | 92 | 3.82 | 0.36 | 11 | `table-pointer` | `unreached` | none |
| `0x07DA84` | `0x07DB40` | 188 | 3.99 | 0.37 | 20 | `table-pointer` | `unreached` | none |
| `0x07DBDC` | `0x07DC1C` | 64 | 3.72 | 0.36 | 6 | `table-pointer` | `unreached` | none |
| `0x07DC1C` | `0x07DC74` | 88 | 4.3 | 0.31 | 9 | `table` | `unreached` | none |
| `0x07DCE4` | `0x07DD24` | 64 | 3.77 | 0.34 | 6 | `table-pointer` | `unreached` | none |
| `0x07DDB8` | `0x07DDF8` | 64 | 3.59 | 0.39 | 6 | `table-pointer` | `unreached` | none |
| `0x07DDF8` | `0x07DEB4` | 188 | 4.72 | 0.25 | 13 | `table` | `unreached` | none |
| `0x07DF6C` | `0x07DFD8` | 108 | 3.8 | 0.37 | 12 | `table-pointer` | `unreached` | none |
| `0x07E070` | `0x07E12C` | 188 | 3.91 | 0.37 | 20 | `table-pointer` | `unreached` | none |
| `0x07E1A4` | `0x07E1E4` | 64 | 3.72 | 0.36 | 6 | `table-pointer` | `unreached` | none |
| `0x07E1E4` | `0x07E208` | 36 | 3.95 | 0.14 | 0 | `table` | `unreached` | none |
| `0x07E278` | `0x07E374` | 252 | 4.38 | 0.35 | 22 | `table-pointer` | `unreached` | none |
| `0x07E378` | `0x07E39C` | 36 | 3.37 | 0.39 | 3 | `table` | `unreached` | none |
| `0x07E434` | `0x07E4A0` | 108 | 3.8 | 0.38 | 12 | `table-pointer` | `unreached` | none |
| `0x07E514` | `0x07E570` | 92 | 3.9 | 0.36 | 10 | `table-pointer` | `unreached` | none |
| `0x07E5E0` | `0x07E620` | 64 | 3.66 | 0.36 | 6 | `table-pointer` | `unreached` | none |
| `0x07E620` | `0x07E644` | 36 | 3.95 | 0.14 | 0 | `table` | `unreached` | none |
| `0x07E690` | `0x07E720` | 144 | 3.89 | 0.38 | 16 | `table-pointer` | `unreached` | none |
| `0x07E724` | `0x07E73C` | 24 | 2.63 | 0.5 | 2 | `table` | `unreached` | none |
| `0x07E7D4` | `0x07E814` | 64 | 3.69 | 0.36 | 6 | `table-pointer` | `unreached` | none |
| `0x07E83C` | `0x07E8B8` | 124 | 3.91 | 0.37 | 13 | `table-pointer` | `unreached` | none |
| `0x07E8B8` | `0x07E8DC` | 36 | 3.95 | 0.14 | 0 | `table` | `unreached` | none |
| `0x07E970` | `0x07EA00` | 144 | 3.84 | 0.38 | 16 | `table-pointer` | `unreached` | none |
| `0x07EA04` | `0x07EA1C` | 24 | 2.63 | 0.5 | 2 | `table` | `unreached` | none |
| `0x07EAB4` | `0x07EAF4` | 64 | 3.69 | 0.36 | 6 | `table-pointer` | `unreached` | none |
| `0x07EAF4` | `0x07ED70` | 636 | 4.23 | 0.29 | 16 | `table` | `unreached` | none |
| `0x07EE04` | `0x07EE44` | 64 | 3.77 | 0.34 | 6 | `table-pointer` | `unreached` | none |
| `0x07EE44` | `0x07EE9C` | 88 | 4.41 | 0.28 | 9 | `table` | `unreached` | none |
| `0x07EE9C` | `0x07EFA8` | 268 | 4.85 | 0.24 | 18 | `code-shaped` | `unreached` | none |
| `0x07F0E8` | `0x07F0EC` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x07F128` | `0x07F134` | 12 | 3.02 | 0.25 | 0 | `table` | `unreached` | none |
| `0x07F1E8` | `0x07F210` | 40 | 4.36 | 0.17 | 4 | `table` | `unreached` | none |
| `0x07F2B0` | `0x07F374` | 196 | 4.87 | 0.24 | 12 | `table` | `unreached` | none |
| `0x07F5D4` | `0x07F5F4` | 32 | 3.82 | 0.25 | 5 | `table-pointer` | `unreached` | none |
| `0x07F618` | `0x07F630` | 24 | 3.77 | 0.17 | 0 | `table` | `unreached` | none |
| `0x07F674` | `0x07F6AC` | 56 | 4.08 | 0.12 | 0 | `table` | `unreached` | none |
| `0x07F6F8` | `0x07F708` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x07F740` | `0x07F748` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x07F788` | `0x07F798` | 16 | 2.91 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x07F818` | `0x07F8F8` | 224 | 4.47 | 0.31 | 28 | `table-pointer` | `unreached` | none |
| `0x07F8F8` | `0x07F930` | 56 | 4.02 | 0.14 | 0 | `table` | `unreached` | none |
| `0x07FA04` | `0x07FA14` | 16 | 3.08 | 0.25 | 0 | `table` | `unreached` | none |
| `0x07FA5C` | `0x07FA9C` | 64 | 4.16 | 0.25 | 10 | `table-pointer` | `unreached` | none |
| `0x07FA9C` | `0x07FC80` | 484 | 5.07 | 0.17 | 22 | `table` | `unreached` | none |
| `0x07FCBC` | `0x07FCC8` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x080014` | `0x08002C` | 24 | 3.74 | 0.21 | 0 | `table` | `unreached` | none |
| `0x080174` | `0x0801D0` | 92 | 4.22 | 0.18 | 5 | `table-pointer` | `unreached` | none |
| `0x0801D0` | `0x0801F0` | 32 | 4.24 | 0.19 | 1 | `table` | `unreached` | none |
| `0x08067C` | `0x080690` | 20 | 3.32 | 0.1 | 0 | `table` | `unreached` | none |
| `0x0807E0` | `0x080930` | 336 | 4.83 | 0.15 | 13 | `table` | `unreached` | none |
| `0x080930` | `0x080948` | 24 | 3.8 | 0.17 | 0 | `table` | `unreached` | none |
| `0x080A48` | `0x080AA8` | 96 | 4.29 | 0.21 | 5 | `table-pointer` | `unreached` | none |
| `0x080AA8` | `0x080AC0` | 24 | 3.82 | 0.12 | 0 | `table` | `unreached` | none |
| `0x080BE4` | `0x080C44` | 96 | 4.37 | 0.2 | 5 | `table-pointer` | `unreached` | none |
| `0x080C44` | `0x080C74` | 48 | 4.12 | 0.17 | 0 | `table` | `unreached` | none |
| `0x080DBC` | `0x080E3C` | 128 | 4.43 | 0.25 | 8 | `table-pointer` | `unreached` | none |
| `0x080E3C` | `0x080E54` | 24 | 3.94 | 0.12 | 0 | `table` | `unreached` | none |
| `0x080F9C` | `0x080FFC` | 96 | 4.4 | 0.2 | 5 | `table-pointer` | `unreached` | none |
| `0x080FFC` | `0x08103C` | 64 | 4.35 | 0.23 | 4 | `table` | `unreached` | none |
| `0x08103C` | `0x081058` | 28 | 3.79 | 0.25 | 0 | `table` | `unreached` | none |
| `0x0810C8` | `0x0810E8` | 32 | 3.56 | 0.31 | 3 | `table-pointer` | `unreached` | none |
| `0x081230` | `0x081234` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x0812A4` | `0x0812A8` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x0813F0` | `0x081408` | 24 | 3.86 | 0.12 | 0 | `table` | `unreached` | none |
| `0x081508` | `0x081568` | 96 | 4.21 | 0.2 | 5 | `table-pointer` | `unreached` | none |
| `0x0816D4` | `0x0816EC` | 24 | 3.8 | 0.17 | 0 | `table` | `unreached` | none |
| `0x0817EC` | `0x081850` | 100 | 4.41 | 0.2 | 6 | `table-pointer` | `unreached` | none |
| `0x081950` | `0x081968` | 24 | 2.78 | 0.42 | 3 | `table-pointer` | `unreached` | none |
| `0x081968` | `0x081980` | 24 | 3.49 | 0.25 | 0 | `table` | `unreached` | none |
| `0x0819E4` | `0x0819FC` | 24 | 3.11 | 0.38 | 0 | `table` | `unreached` | none |
| `0x081A58` | `0x081AB0` | 88 | 3.76 | 0.38 | 9 | `table-pointer` | `unreached` | none |
| `0x081AB8` | `0x081B44` | 140 | 4.22 | 0.19 | 0 | `table` | `unreached` | none |
| `0x081BE0` | `0x081D2C` | 332 | 4.88 | 0.18 | 20 | `table` | `unreached` | none |
| `0x081D48` | `0x081D5C` | 20 | 3.05 | 0.3 | 0 | `table` | `unreached` | none |
| `0x081DC0` | `0x081DCC` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x081E68` | `0x081EF4` | 140 | 3.91 | 0.29 | 8 | `table` | `unreached` | none |
| `0x081FE0` | `0x082004` | 36 | 1.99 | 0.53 | 3 | `table` | `unreached` | none |
| `0x082010` | `0x082024` | 20 | 3.05 | 0.3 | 0 | `table` | `unreached` | none |
| `0x082148` | `0x0821E0` | 152 | 3.72 | 0.34 | 9 | `table` | `unreached` | none |
| `0x0821F4` | `0x082218` | 36 | 3.27 | 0.31 | 0 | `table` | `unreached` | none |
| `0x0823A8` | `0x082450` | 168 | 4.07 | 0.31 | 12 | `table` | `unreached` | none |
| `0x082560` | `0x082590` | 48 | 2.07 | 0.52 | 4 | `table` | `unreached` | none |
| `0x0826A0` | `0x0826D0` | 48 | 2.07 | 0.52 | 4 | `table` | `unreached` | none |
| `0x082804` | `0x082840` | 60 | 2.13 | 0.52 | 5 | `table` | `unreached` | none |
| `0x082854` | `0x082868` | 20 | 2.88 | 0.4 | 0 | `table` | `unreached` | none |
| `0x0829F8` | `0x082A1C` | 36 | 3.49 | 0.28 | 3 | `table` | `unreached` | none |
| `0x082A20` | `0x082A34` | 20 | 3.05 | 0.3 | 0 | `table` | `unreached` | none |
| `0x082B34` | `0x082BB4` | 128 | 3.99 | 0.29 | 7 | `table` | `unreached` | none |
| `0x082D50` | `0x082D74` | 36 | 1.99 | 0.53 | 3 | `table` | `unreached` | none |
| `0x082E5C` | `0x082E8C` | 48 | 2.07 | 0.52 | 4 | `table` | `unreached` | none |
| `0x082E9C` | `0x082F44` | 168 | 4.68 | 0.24 | 8 | `table-pointer` | `unreached` | none |
| `0x08308C` | `0x0830DC` | 80 | 3.82 | 0.23 | 0 | `table` | `unreached` | none |
| `0x083194` | `0x0831D8` | 68 | 4.13 | 0.25 | 5 | `table` | `unreached` | none |
| `0x0832B4` | `0x08337C` | 200 | 4.5 | 0.27 | 12 | `table` | `unreached` | none |
| `0x0834C4` | `0x08354C` | 136 | 4.05 | 0.29 | 8 | `table` | `unreached` | none |
| `0x083628` | `0x0836B0` | 136 | 4.06 | 0.29 | 8 | `table` | `unreached` | none |
| `0x0836B0` | `0x0836BC` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x08372C` | `0x083830` | 260 | 4.68 | 0.28 | 12 | `table` | `unreached` | none |
| `0x083978` | `0x0839F4` | 124 | 4.27 | 0.27 | 4 | `table` | `unreached` | none |
| `0x083BB0` | `0x083BB8` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x083BD4` | `0x083BDC` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x083BF8` | `0x083C00` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x083C28` | `0x083C30` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x083C58` | `0x083C60` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x083C88` | `0x083C90` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x083CB8` | `0x083CC0` | 8 | 2.41 | 0.38 | 1 | `table-pointer` | `unreached` | none |
| `0x083D88` | `0x083D9C` | 20 | 3.21 | 0.3 | 0 | `table` | `unreached` | none |
| `0x083E00` | `0x083E7C` | 124 | 4.34 | 0.27 | 12 | `table` | `unreached` | none |
| `0x083EC8` | `0x083EF0` | 40 | 4.02 | 0.23 | 5 | `table` | `unreached` | none |
| `0x083F3C` | `0x0840E0` | 420 | 4.86 | 0.16 | 10 | `table` | `unreached` | none |
| `0x084174` | `0x084198` | 36 | 3.71 | 0.28 | 4 | `table` | `unreached` | none |
| `0x084198` | `0x08431C` | 388 | 4.75 | 0.1 | 9 | `table` | `unreached` | none |
| `0x0843B0` | `0x084498` | 232 | 4.67 | 0.23 | 9 | `table` | `unreached` | none |
| `0x084508` | `0x0845C8` | 192 | 4.51 | 0.21 | 5 | `table` | `unreached` | none |
| `0x084718` | `0x084860` | 328 | 4.56 | 0.18 | 9 | `table` | `unreached` | none |
| `0x0848D0` | `0x0848F4` | 36 | 3.49 | 0.33 | 4 | `table` | `unreached` | none |
| `0x0848F4` | `0x084990` | 156 | 4.74 | 0.14 | 9 | `table` | `unreached` | none |
| `0x084A24` | `0x084A48` | 36 | 3.63 | 0.28 | 4 | `table` | `unreached` | none |
| `0x084B00` | `0x084C4C` | 332 | 4.64 | 0.18 | 10 | `table-pointer` | `unreached` | none |
| `0x084DBC` | `0x084F08` | 332 | 4.61 | 0.18 | 10 | `table-pointer` | `unreached` | none |
| `0x084F78` | `0x084F9C` | 36 | 3.63 | 0.31 | 4 | `table` | `unreached` | none |
| `0x084F9C` | `0x085124` | 392 | 4.89 | 0.2 | 19 | `table` | `unreached` | none |
| `0x085224` | `0x0853C4` | 416 | 5.01 | 0.19 | 17 | `table` | `unreached` | none |
| `0x0853E8` | `0x0854D8` | 240 | 4.36 | 0.2 | 2 | `table` | `unreached` | none |
| `0x085534` | `0x085624` | 240 | 4.85 | 0.18 | 7 | `table` | `unreached` | none |
| `0x085628` | `0x0857AC` | 388 | 4.88 | 0.19 | 23 | `table` | `unreached` | none |
| `0x0857E8` | `0x085808` | 32 | 3.78 | 0.22 | 5 | `table-pointer` | `unreached` | none |
| `0x08584C` | `0x085858` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x085AB0` | `0x085AE8` | 56 | 3.85 | 0.3 | 7 | `table` | `unreached` | none |
| `0x0864E4` | `0x086504` | 32 | 2.81 | 0.41 | 4 | `table` | `unreached` | none |
| `0x08679C` | `0x0867D0` | 52 | 3.96 | 0.13 | 0 | `table` | `unreached` | none |
| `0x08685C` | `0x08686C` | 16 | 3.58 | 0.12 | 0 | `table` | `unreached` | none |
| `0x0868BC` | `0x0868CC` | 16 | 3.58 | 0.12 | 0 | `table` | `unreached` | none |
| `0x086938` | `0x086970` | 56 | 3.9 | 0.3 | 7 | `table` | `unreached` | none |
| `0x086974` | `0x086978` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x086B98` | `0x086BCC` | 52 | 3.39 | 0.35 | 7 | `table-pointer` | `unreached` | none |
| `0x086E5C` | `0x086E6C` | 16 | 2.65 | 0.44 | 2 | `table` | `unreached` | none |
| `0x087344` | `0x08735C` | 24 | 2.5 | 0.54 | 2 | `table` | `unreached` | none |
| `0x087360` | `0x087388` | 40 | 3.55 | 0.28 | 0 | `table` | `unreached` | none |
| `0x0873B8` | `0x0873F8` | 64 | 4.1 | 0.25 | 7 | `table` | `unreached` | none |
| `0x0873FC` | `0x087414` | 24 | 2.5 | 0.54 | 2 | `table` | `unreached` | none |
| `0x087418` | `0x087600` | 488 | 4.87 | 0.19 | 22 | `table` | `unreached` | none |
| `0x087668` | `0x087680` | 24 | 3.4 | 0.29 | 1 | `table` | `unreached` | none |
| `0x08769C` | `0x0876B4` | 24 | 3.4 | 0.29 | 1 | `table` | `unreached` | none |
| `0x0876D0` | `0x0876E8` | 24 | 3.4 | 0.29 | 1 | `table` | `unreached` | none |
| `0x087704` | `0x08771C` | 24 | 3.4 | 0.29 | 1 | `table` | `unreached` | none |
| `0x087738` | `0x087744` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x08787C` | `0x0878EC` | 112 | 4.19 | 0.29 | 10 | `table-pointer` | `unreached` | none |
| `0x087AF0` | `0x087C40` | 336 | 3.88 | 0.32 | 48 | `table-pointer` | `unreached` | none |
| `0x087E18` | `0x087F70` | 344 | 4.37 | 0.23 | 30 | `table` | `unreached` | none |
| `0x08806C` | `0x088154` | 232 | 4.49 | 0.26 | 19 | `table-pointer` | `unreached` | none |
| `0x088154` | `0x0881B4` | 96 | 3.52 | 0.32 | 11 | `table` | `unreached` | none |
| `0x088398` | `0x0883B0` | 24 | 2.61 | 0.38 | 2 | `table-pointer` | `unreached` | none |
| `0x0883D4` | `0x0883EC` | 24 | 2.78 | 0.38 | 2 | `table-pointer` | `unreached` | none |
| `0x088410` | `0x088428` | 24 | 2.78 | 0.38 | 2 | `table-pointer` | `unreached` | none |
| `0x08844C` | `0x088464` | 24 | 2.78 | 0.38 | 2 | `table-pointer` | `unreached` | none |
| `0x088658` | `0x088660` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x088680` | `0x088688` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x0886A8` | `0x0886B0` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x0886D0` | `0x0886D8` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x0886F8` | `0x088700` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x088740` | `0x088748` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x088768` | `0x088770` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x088790` | `0x088798` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x0888BC` | `0x0888C0` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x088C2C` | `0x088C80` | 84 | 4.35 | 0.13 | 0 | `table` | `unreached` | none |
| `0x088D10` | `0x088D44` | 52 | 3.7 | 0.33 | 7 | `table-pointer` | `unreached` | none |
| `0x088D44` | `0x088D54` | 16 | 3.02 | 0.31 | 0 | `table` | `unreached` | none |
| `0x088E78` | `0x088E80` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x088EA0` | `0x088EA8` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x088EC8` | `0x088ED0` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x088EF0` | `0x088EF8` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x088F4C` | `0x089128` | 476 | 4.03 | 0.3 | 68 | `table-pointer` | `unreached` | none |
| `0x08912C` | `0x089134` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x089154` | `0x089164` | 16 | 3.02 | 0.31 | 0 | `table` | `unreached` | none |
| `0x089318` | `0x089334` | 28 | 3.81 | 0.18 | 4 | `table-pointer` | `unreached` | none |
| `0x089458` | `0x08947C` | 36 | 3.26 | 0.33 | 5 | `table-pointer` | `unreached` | none |
| `0x089484` | `0x089498` | 20 | 3.0 | 0.35 | 0 | `table` | `unreached` | none |
| `0x089604` | `0x089624` | 32 | 3.78 | 0.22 | 5 | `table-pointer` | `unreached` | none |
| `0x089624` | `0x089644` | 32 | 4.35 | 0.12 | 0 | `table` | `unreached` | none |
| `0x08974C` | `0x08978C` | 64 | 3.79 | 0.34 | 7 | `table-pointer` | `unreached` | none |
| `0x089790` | `0x0897D0` | 64 | 3.27 | 0.31 | 0 | `table` | `unreached` | none |
| `0x0897D4` | `0x0897DC` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x0897FC` | `0x08986C` | 112 | 3.85 | 0.28 | 16 | `table-pointer` | `unreached` | none |
| `0x08986C` | `0x0898D8` | 108 | 4.43 | 0.17 | 0 | `table` | `unreached` | none |
| `0x0898F8` | `0x089900` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08991C` | `0x089924` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x089940` | `0x089948` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x089964` | `0x08996C` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08999C` | `0x089AF0` | 340 | 5.05 | 0.18 | 26 | `table` | `unreached` | none |
| `0x089B6C` | `0x089B78` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x08AE2C` | `0x08AE30` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x08AE30` | `0x08AF88` | 344 | 4.73 | 0.24 | 20 | `table` | `unreached` | none |
| `0x08B5CC` | `0x08B5DC` | 16 | 2.91 | 0.38 | 0 | `table` | `unreached` | none |
| `0x08B670` | `0x08B688` | 24 | 3.38 | 0.25 | 2 | `table` | `unreached` | none |
| `0x08B88C` | `0x08B890` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x08BD1C` | `0x08BD34` | 24 | 2.87 | 0.42 | 3 | `table-pointer` | `unreached` | none |
| `0x08BD34` | `0x08BD60` | 44 | 4.27 | 0.07 | 0 | `table` | `unreached` | none |
| `0x08BDD8` | `0x08BE1C` | 68 | 4.05 | 0.31 | 6 | `table-pointer` | `unreached` | none |
| `0x08BE20` | `0x08BE30` | 16 | 2.85 | 0.31 | 0 | `table` | `unreached` | none |
| `0x08BE54` | `0x08BEA4` | 80 | 3.77 | 0.3 | 10 | `table` | `unreached` | none |
| `0x08BECC` | `0x08BF08` | 60 | 3.81 | 0.3 | 7 | `table` | `unreached` | none |
| `0x08BF08` | `0x08BF18` | 16 | 2.98 | 0.31 | 0 | `table` | `unreached` | none |
| `0x08BFAC` | `0x08C000` | 84 | 4.18 | 0.2 | 4 | `table` | `unreached` | none |
| `0x08C070` | `0x08C088` | 24 | 3.74 | 0.21 | 0 | `table` | `unreached` | none |
| `0x08C0D4` | `0x08C0E4` | 16 | 3.2 | 0.25 | 0 | `table` | `unreached` | none |
| `0x08C178` | `0x08C1C0` | 72 | 4.14 | 0.28 | 8 | `table-pointer` | `unreached` | none |
| `0x08C2E8` | `0x08C304` | 28 | 3.53 | 0.21 | 4 | `table-pointer` | `unreached` | none |
| `0x08C350` | `0x08C360` | 16 | 3.0 | 0.25 | 0 | `table` | `unreached` | none |
| `0x08C38C` | `0x08C394` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08C3B4` | `0x08C3BC` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08C3DC` | `0x08C3E4` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08C404` | `0x08C40C` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08C42C` | `0x08C434` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08C490` | `0x08C4C8` | 56 | 3.93 | 0.23 | 8 | `table-pointer` | `unreached` | none |
| `0x08C4C8` | `0x08C4F4` | 44 | 4.09 | 0.16 | 0 | `table` | `unreached` | none |
| `0x08C520` | `0x08C528` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08C548` | `0x08C550` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08C570` | `0x08C578` | 8 | 2.0 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08C5CC` | `0x08C8AC` | 736 | 5.01 | 0.2 | 43 | `table-pointer` | `unreached` | none |
| `0x08C8E0` | `0x08C8F0` | 16 | 2.5 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08C90C` | `0x08C91C` | 16 | 2.38 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08C938` | `0x08C944` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x08CA00` | `0x08CA18` | 24 | 2.67 | 0.46 | 3 | `table-pointer` | `unreached` | none |
| `0x08CA18` | `0x08CA3C` | 36 | 3.83 | 0.19 | 0 | `table` | `unreached` | none |
| `0x08CA64` | `0x08CAB0` | 76 | 4.41 | 0.2 | 4 | `table` | `unreached` | none |
| `0x08CAB8` | `0x08CAE4` | 44 | 4.05 | 0.2 | 0 | `table` | `unreached` | none |
| `0x08CB0C` | `0x08CB4C` | 64 | 3.78 | 0.31 | 8 | `table-pointer` | `unreached` | none |
| `0x08CB4C` | `0x08CB58` | 12 | 2.75 | 0.33 | 0 | `table` | `unreached` | none |
| `0x08CB64` | `0x08CB68` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x08CBEC` | `0x08CC58` | 108 | 4.5 | 0.2 | 17 | `table-pointer` | `unreached` | none |
| `0x08CD04` | `0x08CD08` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x08CD08` | `0x08CDA0` | 152 | 4.48 | 0.21 | 6 | `table` | `unreached` | none |
| `0x08CDE4` | `0x08CE44` | 96 | 4.13 | 0.32 | 12 | `table-pointer` | `unreached` | none |
| `0x08CE90` | `0x08CEA4` | 20 | 3.35 | 0.3 | 1 | `table` | `unreached` | none |
| `0x08CEC0` | `0x08CED4` | 20 | 3.35 | 0.3 | 1 | `table` | `unreached` | none |
| `0x08CEF0` | `0x08CF04` | 20 | 3.35 | 0.3 | 1 | `table` | `unreached` | none |
| `0x08CF20` | `0x08CF24` | 4 | 0.81 | 0.75 | 0 | `table` | `unreached` | none |
| `0x08CFC0` | `0x08D020` | 96 | 4.49 | 0.18 | 13 | `table-pointer` | `unreached` | none |
| `0x08D090` | `0x08D0DC` | 76 | 4.04 | 0.16 | 0 | `table` | `unreached` | none |
| `0x08D194` | `0x08D238` | 164 | 4.84 | 0.15 | 9 | `table` | `unreached` | none |
| `0x08D350` | `0x08D36C` | 28 | 3.7 | 0.21 | 4 | `table-pointer` | `unreached` | none |
| `0x08D36C` | `0x08D390` | 36 | 3.75 | 0.25 | 0 | `table` | `unreached` | none |
| `0x08D400` | `0x08D434` | 52 | 3.45 | 0.37 | 7 | `table-pointer` | `unreached` | none |
| `0x08D4D8` | `0x08D4E4` | 12 | 2.79 | 0.0 | 3 | `table-pointer` | `unreached` | none |
| `0x08D600` | `0x08D670` | 112 | 4.29 | 0.23 | 11 | `table` | `unreached` | none |
| `0x08D750` | `0x08D778` | 40 | 3.92 | 0.25 | 0 | `table` | `unreached` | none |
| `0x08D784` | `0x08D788` | 4 | 2.0 | 0.0 | 0 | `table` | `unreached` | none |
| `0x08D86C` | `0x08D890` | 36 | 4.16 | 0.17 | 0 | `table` | `unreached` | none |
| `0x08D898` | `0x08D8A4` | 12 | 3.02 | 0.25 | 0 | `table` | `unreached` | none |
| `0x08D8CC` | `0x08D8D8` | 12 | 3.58 | 0.08 | 0 | `table` | `unreached` | none |
| `0x08D908` | `0x08D918` | 16 | 3.02 | 0.31 | 2 | `table` | `unreached` | none |
| `0x08D98C` | `0x08D9A8` | 28 | 3.95 | 0.14 | 0 | `table` | `unreached` | none |
| `0x08D9B0` | `0x08D9BC` | 12 | 3.19 | 0.25 | 0 | `table` | `unreached` | none |
| `0x08D9E4` | `0x08D9F4` | 16 | 3.38 | 0.25 | 0 | `table` | `unreached` | none |
| `0x08DB04` | `0x08DB28` | 36 | 2.9 | 0.33 | 0 | `table` | `unreached` | none |
| `0x08DB74` | `0x08DBE0` | 108 | 4.33 | 0.18 | 6 | `table` | `unreached` | none |
| `0x08DBEC` | `0x08DBF0` | 4 | 2.0 | 0.0 | 1 | `table-pointer` | `unreached` | none |
| `0x08DBF0` | `0x08DC08` | 24 | 3.75 | 0.08 | 0 | `table` | `unreached` | none |
| `0x08DC10` | `0x08DC18` | 8 | 2.75 | 0.25 | 0 | `table` | `unreached` | none |
| `0x08DC40` | `0x08DC50` | 16 | 3.41 | 0.19 | 0 | `table` | `unreached` | none |
| `0x08DC80` | `0x08DC98` | 24 | 3.57 | 0.25 | 0 | `table` | `unreached` | none |
| `0x08DD08` | `0x08DD20` | 24 | 2.91 | 0.38 | 3 | `table-pointer` | `unreached` | none |
| `0x08DEE0` | `0x08DEF4` | 20 | 3.62 | 0.2 | 0 | `table` | `unreached` | none |
| `0x08DF2C` | `0x08DF50` | 36 | 3.63 | 0.11 | 0 | `table` | `unreached` | none |
| `0x08DF84` | `0x08DFA0` | 28 | 3.62 | 0.25 | 4 | `table-pointer` | `unreached` | none |
| `0x08DFA0` | `0x08DFB4` | 20 | 3.42 | 0.2 | 1 | `table` | `unreached` | none |
| `0x08DFB4` | `0x08DFC8` | 20 | 3.78 | 0.15 | 0 | `table` | `unreached` | none |
| `0x08DFE8` | `0x08E010` | 40 | 3.6 | 0.15 | 0 | `table` | `unreached` | none |
| `0x08E040` | `0x08E05C` | 28 | 3.69 | 0.25 | 4 | `table-pointer` | `unreached` | none |
| `0x08E05C` | `0x08E06C` | 16 | 3.58 | 0.19 | 1 | `table` | `unreached` | none |
| `0x08E06C` | `0x08E080` | 20 | 3.62 | 0.2 | 0 | `table` | `unreached` | none |
| `0x08E0A0` | `0x08E0C4` | 36 | 3.63 | 0.11 | 0 | `table` | `unreached` | none |
| `0x08E0F4` | `0x08E110` | 28 | 3.69 | 0.25 | 4 | `table-pointer` | `unreached` | none |
| `0x08E110` | `0x08E13C` | 44 | 3.92 | 0.3 | 5 | `table` | `unreached` | none |
| `0x08E13C` | `0x08E15C` | 32 | 3.88 | 0.16 | 0 | `table` | `unreached` | none |
| `0x08E1A8` | `0x08E1E0` | 56 | 3.87 | 0.27 | 8 | `table-pointer` | `unreached` | none |
| `0x08E1F0` | `0x08E1F4` | 4 | 1.5 | 0.5 | 0 | `table` | `unreached` | none |
| `0x08E210` | `0x08E220` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x08E23C` | `0x08E24C` | 16 | 2.77 | 0.44 | 1 | `table-pointer` | `unreached` | none |
| `0x08E268` | `0x08E278` | 16 | 2.5 | 0.5 | 1 | `table-pointer` | `unreached` | none |
| `0x08E2A4` | `0x08E2E0` | 60 | 3.67 | 0.33 | 7 | `table` | `unreached` | none |

## The rows the table above does not carry

These 17 rows / 200 B of the region are raw slices the census splits out on their own and
the table above does not carry. Each line is the measurement the table above uses, at its
columns; `none` means no instruction in the four channels above names a byte of the row,
at the denominators the channels print.

| start | end | bytes | ent | zero | in-image words | class | readers |
|---|---|---|---|---|---|---|---|
| `0x072D04` | `0x072D10` | 12 | 3.02 | 0.25 | 0 | `unknown` | none |
| `0x072D68` | `0x072D74` | 12 | 3.02 | 0.25 | 0 | `unknown` | none |
| `0x072DC8` | `0x072DD4` | 12 | 3.02 | 0.25 | 0 | `unknown` | none |
| `0x072E1C` | `0x072E28` | 12 | 3.02 | 0.25 | 0 | `unknown` | none |
| `0x072E78` | `0x072E84` | 12 | 3.02 | 0.25 | 0 | `unknown` | none |
| `0x072EE4` | `0x072EF0` | 12 | 3.02 | 0.25 | 0 | `unknown` | none |
| `0x072F48` | `0x072F54` | 12 | 3.02 | 0.25 | 0 | `unknown` | none |
| `0x072FA8` | `0x072FB4` | 12 | 3.02 | 0.25 | 0 | `unknown` | none |
| `0x072FFC` | `0x073008` | 12 | 3.02 | 0.25 | 0 | `unknown` | none |
| `0x073058` | `0x073064` | 12 | 3.02 | 0.25 | 0 | `unknown` | none |
| `0x073094` | `0x0730A0` | 12 | 2.75 | 0.33 | 0 | `unknown` | none |
| `0x077010` | `0x077018` | 8 | 2.41 | 0.38 | 0 | `unknown` | none |
| `0x0774A4` | `0x0774B8` | 20 | 2.58 | 0.00 | 5 | `pointer-tables` | no decoder names a byte of the row; every one of the row's 5 grid words is an address, and no symbol names one |
| `0x078BCC` | `0x078BD4` | 8 | 2.75 | 0.25 | 0 | `unknown` | none |
| `0x079D38` | `0x079D44` | 12 | 3.08 | 0.17 | 0 | `unknown` | none |
| `0x079D70` | `0x079D80` | 16 | 3.28 | 0.19 | 0 | `unknown` | none |
| `0x07F794` | `0x07F798` | 4 | 1.50 | 0.00 | 0 | `unknown` | none |


## The opcode streams the `+0x30` field names

These 98 rows / 13853 B are the `MapEntry` `+0x30` streams the interpreter ends on `0x11`
before the row's last byte. `stream` is the bytes the interpreter consumes, `stop` the
offset where its call stops; the bytes past `stop` are not reached by that call, so they
stay raw. Measured by `tools/research/opcode_stream.py` from the interpreter at
`0x08004038` and the handler table at `0x080554C0`.

| start | end | bytes | stream | stop | class | readers |
|---|---|---|---|---|---|---|
| `0x072974` | `0x0729B0` | 60 | 9 | 9 | `unknown` | none |
| `0x072A48` | `0x072C9C` | 596 | 593 | 593 | `unknown` | none |
| `0x073994` | `0x073AF8` | 356 | 16 | 16 | `unknown` | none |
| `0x07457C` | `0x07458C` | 16 | 9 | 9 | `unknown` | none |
| `0x074E80` | `0x074EA8` | 40 | 36 | 36 | `unknown` | none |
| `0x0751C8` | `0x07526C` | 164 | 41 | 41 | `unknown` | none |
| `0x0753D0` | `0x0753F0` | 32 | 31 | 31 | `unknown` | none |
| `0x0758FC` | `0x07593C` | 64 | 61 | 61 | `unknown` | none |
| `0x075AE0` | `0x075AF4` | 20 | 17 | 17 | `unknown` | none |
| `0x075FC0` | `0x07600C` | 76 | 16 | 16 | `unknown` | none |
| `0x07600C` | `0x076044` | 56 | 54 | 54 | `unknown` | none |
| `0x076694` | `0x0766FC` | 104 | 24 | 24 | `unknown` | none |
| `0x076AFC` | `0x076B30` | 52 | 12 | 12 | `unknown` | none |
| `0x076C3F` | `0x076C4C` | 13 | 12 | 12 | `unknown` | none |
| `0x076ECC` | `0x076EE0` | 20 | 17 | 17 | `unknown` | none |
| `0x0775A0` | `0x0775D0` | 48 | 16 | 16 | `unknown` | none |
| `0x0775D0` | `0x077604` | 52 | 24 | 24 | `unknown` | none |
| `0x077F10` | `0x0780FC` | 492 | 123 | 123 | `unknown` | none |
| `0x0780FC` | `0x0782FC` | 512 | 135 | 135 | `unknown` | none |
| `0x078538` | `0x078584` | 76 | 5 | 5 | `unknown` | none |
| `0x078814` | `0x078824` | 16 | 12 | 12 | `unknown` | none |
| `0x078854` | `0x078BC0` | 876 | 244 | 244 | `unknown` | none |
| `0x079144` | `0x0791E4` | 160 | 25 | 25 | `unknown` | none |
| `0x0791E4` | `0x079370` | 396 | 23 | 23 | `unknown` | none |
| `0x0793C0` | `0x0793C8` | 8 | 5 | 5 | `unknown` | none |
| `0x0794D0` | `0x0794E0` | 16 | 13 | 13 | `unknown` | none |
| `0x0798E8` | `0x079920` | 56 | 12 | 12 | `unknown` | none |
| `0x07997C` | `0x079AF4` | 376 | 16 | 16 | `unknown` | none |
| `0x079C70` | `0x079CD8` | 104 | 103 | 103 | `unknown` | none |
| `0x07AB24` | `0x07ACA0` | 380 | 115 | 115 | `unknown` | none |
| `0x07B3B0` | `0x07B3CC` | 28 | 23 | 23 | `unknown` | none |
| `0x07C044` | `0x07C0A4` | 96 | 95 | 95 | `unknown` | none |
| `0x07C254` | `0x07C440` | 492 | 35 | 35 | `unknown` | none |
| `0x07C4BC` | `0x07C4D8` | 28 | 25 | 25 | `unknown` | none |
| `0x07C5CC` | `0x07C6B4` | 232 | 12 | 12 | `unknown` | none |
| `0x07C958` | `0x07CA40` | 232 | 12 | 12 | `unknown` | none |
| `0x07CB14` | `0x07CBFC` | 232 | 12 | 12 | `unknown` | none |
| `0x07CBFC` | `0x07CD38` | 316 | 133 | 133 | `unknown` | none |
| `0x07CD3C` | `0x07CD48` | 12 | 9 | 9 | `unknown` | none |
| `0x07CF9C` | `0x07D080` | 228 | 12 | 12 | `unknown` | none |
| `0x07D440` | `0x07D560` | 288 | 43 | 43 | `unknown` | none |
| `0x07D658` | `0x07D740` | 232 | 12 | 12 | `unknown` | none |
| `0x07D740` | `0x07D84C` | 268 | 133 | 133 | `unknown` | none |
| `0x07DC1C` | `0x07DC74` | 88 | 12 | 12 | `unknown` | none |
| `0x07DDF8` | `0x07DEB4` | 188 | 35 | 35 | `unknown` | none |
| `0x07E1E4` | `0x07E208` | 36 | 35 | 35 | `unknown` | none |
| `0x07E620` | `0x07E644` | 36 | 35 | 35 | `unknown` | none |
| `0x07E8B8` | `0x07E8DC` | 36 | 35 | 35 | `unknown` | none |
| `0x07EAF4` | `0x07ED70` | 636 | 34 | 34 | `unknown` | none |
| `0x07EE44` | `0x07EE9C` | 88 | 12 | 12 | `unknown` | none |
| `0x07EE9C` | `0x07EFA8` | 268 | 133 | 133 | `unknown` | none |
| `0x07F2B0` | `0x07F374` | 196 | 36 | 36 | `unknown` | none |
| `0x07F618` | `0x07F630` | 24 | 23 | 23 | `unknown` | none |
| `0x07FA9C` | `0x07FC80` | 484 | 121 | 121 | `unknown` | none |
| `0x080014` | `0x08002C` | 24 | 21 | 21 | `unknown` | none |
| `0x0801D0` | `0x0801F0` | 32 | 25 | 25 | `unknown` | none |
| `0x080C44` | `0x080C74` | 48 | 47 | 47 | `unknown` | none |
| `0x080FFC` | `0x08103C` | 64 | 25 | 25 | `unknown` | none |
| `0x08103C` | `0x081058` | 28 | 25 | 25 | `unknown` | none |
| `0x0813F0` | `0x081408` | 24 | 23 | 23 | `unknown` | none |
| `0x081968` | `0x081980` | 24 | 23 | 23 | `unknown` | none |
| `0x081AB8` | `0x081B44` | 140 | 138 | 138 | `unknown` | none |
| `0x0821F4` | `0x082218` | 36 | 35 | 35 | `unknown` | none |
| `0x082854` | `0x082868` | 20 | 17 | 17 | `unknown` | none |
| `0x08308C` | `0x0830DC` | 80 | 79 | 79 | `unknown` | none |
| `0x083194` | `0x0831D8` | 68 | 16 | 16 | `unknown` | none |
| `0x083E00` | `0x083E7C` | 124 | 10 | 10 | `unknown` | none |
| `0x084198` | `0x08431C` | 388 | 96 | 96 | `unknown` | none |
| `0x0848F4` | `0x084990` | 156 | 96 | 96 | `unknown` | none |
| `0x084F9C` | `0x085124` | 392 | 96 | 96 | `unknown` | none |
| `0x085628` | `0x0857AC` | 388 | 63 | 63 | `unknown` | none |
| `0x087360` | `0x087388` | 40 | 37 | 37 | `unknown` | none |
| `0x087418` | `0x087600` | 488 | 124 | 124 | `unknown` | none |
| `0x088154` | `0x0881B4` | 96 | 11 | 11 | `unknown` | none |
| `0x088D44` | `0x088D54` | 16 | 13 | 13 | `unknown` | none |
| `0x089154` | `0x089164` | 16 | 13 | 13 | `unknown` | none |
| `0x089484` | `0x089498` | 20 | 17 | 17 | `unknown` | none |
| `0x089624` | `0x089644` | 32 | 31 | 31 | `unknown` | none |
| `0x089790` | `0x0897D0` | 64 | 61 | 61 | `unknown` | none |
| `0x08AE30` | `0x08AF88` | 344 | 137 | 137 | `unknown` | none |
| `0x08B5CC` | `0x08B5DC` | 16 | 13 | 13 | `unknown` | none |
| `0x08CA18` | `0x08CA3C` | 36 | 33 | 33 | `unknown` | none |
| `0x08CAB8` | `0x08CAE4` | 44 | 42 | 42 | `unknown` | none |
| `0x08CD08` | `0x08CDA0` | 152 | 29 | 29 | `unknown` | none |
| `0x08D090` | `0x08D0DC` | 76 | 74 | 74 | `unknown` | none |
| `0x08D36C` | `0x08D390` | 36 | 33 | 33 | `unknown` | none |
| `0x08D750` | `0x08D778` | 40 | 37 | 37 | `unknown` | none |
| `0x08D86C` | `0x08D890` | 36 | 35 | 35 | `unknown` | none |
| `0x08D98C` | `0x08D9A8` | 28 | 25 | 25 | `unknown` | none |
| `0x08DB04` | `0x08DB28` | 36 | 34 | 34 | `unknown` | none |
| `0x08DBF0` | `0x08DC08` | 24 | 23 | 23 | `unknown` | none |
| `0x08DC80` | `0x08DC98` | 24 | 23 | 23 | `unknown` | none |
| `0x08DEE0` | `0x08DEF4` | 20 | 18 | 18 | `unknown` | none |
| `0x08DFA0` | `0x08DFB4` | 20 | 16 | 16 | `unknown` | none |
| `0x08E05C` | `0x08E06C` | 16 | 12 | 12 | `unknown` | none |
| `0x08E06C` | `0x08E080` | 20 | 18 | 18 | `unknown` | none |
| `0x08E110` | `0x08E13C` | 44 | 12 | 12 | `unknown` | none |
| `0x08E13C` | `0x08E15C` | 32 | 31 | 31 | `unknown` | none |


## Why they stay raw

A row becomes source only with a named layout and a consumer or a structural proof
(`docs/DEFINITION_OF_DONE.md`). These rows have neither: no instruction reaches them, no data
word that names them sits in code, and the layout they would need is the structure their
consumer would have to state. A stride, a first-word pointer or a return shape is not a
consumer, and the shape predicate's hits are level with its own control.

A runtime read watchpoint over `0x071C90..0x0945C0` is the one instrument that could change
this, and none of these rows has been watched.

## Re-run

    python tools\research\raw_remainder.py --check
    python tools\research\code_band.py --region R19 --outside --check
    python -m tools.research.consumer_search --image baserom.gba --range 0x71C90-0x945C0

## The 452-map read sweep

A logged headless run over all 452 `MapEntry` maps (one warped state per map, 400 frames each), the
two live sittings and the 102 warp runs were re-scanned against this run's rows: **500 of the 574
rows (41,628 B) were read; 74 rows (1,128 B) were not, by any of the three log sets.** The 574 rows,
the bytes and the region are the gate's own census figures.

### Rows whose reader proves a field set

| reader | instruction | rows | reads, relative to its own base |
|---|---|---|---|
| `0x08039DBC` | `ldrh r2,[r5,#4]` | 10 | a child's `+4` halfword |
| `0x08039DC4` | `ldrh r2,[r5,#6]` | 10 | a child's `+6` halfword |
| `0x08039DC8` | `ldrh r1,[r5,#8]` | 10 | a child's `+8` halfword |
| `0x08039DCE` | `ldrsh r1,[r5,r3]`, `r3=4` | 10 | the same `+4` halfword, signed |
| `0x08039DDE` | `ldrsh r1,[r5,r3]`, `r3=6` | 10 | the same `+6` halfword, signed |
| `0x08039DEE` | `ldrsh r1,[r5,r3]`, `r3=8` | 10 | the same `+8` halfword, signed |
| `0x0800A7C2` | `ldr r1,[r5,#4]` | 43 | a source record's `+4` word |
| `0x0800A7CC` | `ldrh r0,[r5,#8]` | 43 | its `+8` halfword |
| `0x0800A7CE` | `ldrh r1,[r5,#0xa]` | 43 | its `+0xa` halfword |
| `0x0800A7D0` | `ldrh r2,[r5,#0xc]` | 44 | its `+0xc` halfword |
| `0x0800A7D2` | `ldrh r3,[r5,#0xe]` | 44 | its `+0xe` halfword |
| `0x08009AF4` | `ldr r0,[r1,#0xc]` | 184 | a source record's `+0xc` word |
| `0x08009AF6` | `ldr r2,[r1,#8]` | 184 | its `+8` word |
| `0x08009AFC` | `ldr r0,[r1,#4]` | 184 | its `+4` word |
| `0x080089D4` | `ldr r0,[r0,#0x3c]` after `subs r0,#0x40` | 95 | one word of the `MapEntry+0x2C` array |

The constructor at `0x08039D98` allocates `0x1C` bytes and copies the `+4`, `+6` and `+8` halfwords
of the record it is handed into `+4`, `+6` and `+8` of the instance; it then subtracts, from each of
the three, a signed value read from a table indexed by `r6`, shifted right by 8, 8 and 10. The record
it is handed is the child a placement record's pointer array names: every child pointer of a
placement record classified here is an odd in-ROM word, and one descriptor's four child pointers step
12 B (`0x072CD4`, `0x072CE0`, `0x072CEC`, `0x072CF8`). The child's own first word is that method
pointer, and its last halfword is constant per group (`25` in one group, `128` in the other).

Those 80 records / 960 B are source now (`tools/structured/families.py`, family `placement_child`),
736 B of them net of overlap with the larger records that already claimed the shared bytes. Thirty of
the eighty were read by the sweep. Each of the ten rows that held them lost its trailing 12 B to the
next object in the array, and keeps that tail raw:

| row before | row after |
|---|---|
| `0x072CD4..0x072D10` | `0x072CD4..0x072D04` |
| `0x072D44..0x072D74` | `0x072D44..0x072D68` |
| `0x072DA4..0x072DD4` | `0x072DA4..0x072DC8` |
| `0x072E04..0x072E28` | `0x072E04..0x072E1C` |
| `0x072E54..0x072E84` | `0x072E54..0x072E78` |
| `0x072EB4..0x072EF0` | `0x072EB4..0x072EE4` |
| `0x072F24..0x072F54` | `0x072F24..0x072F48` |
| `0x072F84..0x072FB4` | `0x072F84..0x072FA8` |
| `0x072FE4..0x073008` | `0x072FE4..0x072FFC` |
| `0x073034..0x073064` | `0x073034..0x073058` |

### The method records the five readers prove

The five readers at `0x0800A7C2`, `0x0800A7CC`, `0x0800A7CE`, `0x0800A7D0` and `0x0800A7D2` read
`+4` as a word and `+8`, `+0xa`, `+0xc`, `+0xe` as halfwords of the record they are handed. The
record's own base is therefore the row-relative read offset minus the field offset, and the 44 rows
these readers touch put it at the row's start in 39, at `+8` in two, at `+0x14` in one and before the
row in the other two (a row that keeps only a record's last 12 B, and one that keeps 4 B). That is 42
whole records / 672 B, and the two tail rows stay raw.

Every one of the 42 records holds `0x0800A7A1` in its first word (the Thumb address of the routine at
`0x0800A7A0`, the constructor that builds the instance) and `0x40` or `0x80` in its second. The same
signature occurs 68 times on region A's word grid, always in runs 44 B apart, so the family is those
68 records / 1,088 B through `tools/structured/families.py` (family `method_record`). Forty-two were
read by the sweep; 26 were not, and the signature and the 44 B runs are their only evidence. Seven of
the 68 sit inside `variation_source_words` extents, which keep those bytes (108 B clipped, one
fragment broken), so the conversion is 976 B net of the overlap rule. Round trip 68/68 records,
1,088/1,088 B.

The two bigger reader sets do not convert. `0x08009AF4`/`0x08009AF6`/`0x08009AFC` touch 184 rows: 112
of them carry at least one of the three pcs at two or more offsets inside the one row (a base that
moves per element), and the other 72 carry one fixed field read inside a row that is a whole
container or script blob, which bounds no record extent. `0x080089D4` touches 95 rows: 21 move, and 74
read one word of a scene structure the `MapEntry+0x2C` array already carries. Both sets stay raw with
those measured reasons.

After this family the `R19` group is 478 rows / 41,044 B (42,020 B at the merge commit, 42,756 B when
this census was first written; the placement child definitions took the first 736 B).

### Rows whose readers move their own base

The other read rows are named by readers that re-point their base register every iteration: the walk
at `0x08008AD6` takes a record count from a descriptor's `+3`, the array from its `+0x10`, strides 8
B and reads `+0` and `+4` of each record; the copy at `0x08009AF4` re-reads three words of every
element it is handed; scene code reads bytes across whole structures. The loci they touch inside a
row move with that base: `0x08009AF4` touches 112 distinct offsets over 1,904 B, `0x08004066` 330
offsets over 1,849 B, `0x08003CC2` 182 offsets over 1,847 B. A base that moves per iteration bounds
no stride and no count inside the row, so each of those rows stays raw with that measured reason and
not with "no reader".

### The 74 rows no log read

`0x074D08..0x074D10`, `0x0757C4..0x0757C8`, `0x07580C..0x075810`, `0x075854..0x075858`,
`0x07589C..0x0758A0`, `0x075964..0x075968` and 68 more, 1,128 B in all: no reader in the 452-map
sweep. The per-row table above carries each of them as `none`; the sweep is the fifth channel and it
agrees with the four static ones. Their rows and bytes are listed in
`docs/research/RAW_REMAINDER.csv` under region `R19`.
