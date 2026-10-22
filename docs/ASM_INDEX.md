# Where a function lives

`python tools\readability\audit.py` reports the layout; `docs/ASM_INDEX.csv` is the index.

## The rule

One transcribed function start, one file: `asm/<symbol>.s`, named after the symbol at its first
instruction. A file is included by `asm/buu.s` or `asm/rest_of_the_game.s` in address order, so the
image is assembled from the same bytes in the same order as before the split.

Three files are not one function each, and each says what it is by name:

| file | contents |
| --- | --- |
| `asm/buu.s` | the first area: header, `crt0`, and the code this tree transcribes directly at the head of the image |
| `asm/rest_of_the_game.s` | the second area: generated runs and the transcribed spans after `0x0806D4E0` |
| `asm/rawlabeled_<offset>.s`, `asm/assetdir3_<first>_<last>.s`, `asm/fill_<offset>.s`, `asm/rom_header.s` | a data carrier, named by the extent it rebuilds; the content is generated, raw, or a fill run |

A function start that no label reaches has no name to give a file, so it stays in the file that
holds its extent; `docs/ASM_INDEX.csv` gives its address and that file.

## A naming-ledger row

`docs/NAMING_LEDGER.csv` names 54 starts. The label at each address carries the row's name, in a
file named after it (`asm/Blend_WriteControl1.s`, `asm/Irq_WriteEnable1.s`); the two whose start is
inside `asm/buu.s` stay there and the index points at `asm/buu.s`. `NAMING-ledger-label` refuses a
ledger row whose address carries no such label, and one whose index row names a file that does not
carry it.

## Using the index

`docs/ASM_INDEX.csv` has one row per census start: `address,kind,symbol,file`.

- A name: find the symbol in the `symbol` column, open the file it names.
- An address: find the row with that address, open the file it names.
- A file: read its first label; the file name repeats it.

`kind` is the census kind from `docs/research/FUNCTION_BOUNDS.csv`: `start` is reached by a call,
table, vector or prologue rule, `unreferenced` is a transcribed row start that nothing reaches.

## What moved

The twelve `asm/slice_<first>.s` files were split at their labelled function starts. Each former
file and the files it became:

| former file | first byte | files |
| --- | --- | --- |
| `slice_000158.s` | `0x08000158` | 759 |
| `slice_0153f2.s` | `0x080153F2` | 198 |
| `slice_01c3f2.s` | `0x0801C3F2` | 382 |
| `slice_02bb4c.s` | `0x0802BB4C` | 53 |
| `slice_0301c0.s` | `0x080301C0` | 26 |
| `slice_0331c0.s` | `0x080331C0` | 36 |
| `slice_0351c0.s` | `0x080351C0` | 306 |
| `slice_03d784.s` | `0x0803D784` | 144 |
| `slice_042118.s` | `0x08042118` | 41 |
| `slice_046118.s` | `0x08046118` | 154 |
| `slice_049120.s` | `0x08049120` | 434 |
| `slice_06d4e0.s` | `0x0806D4E0` | 2 |

A document written before the split that cites `asm/slice_<first>.s` still names the right bytes:
its first address is the table's key, and the function's own file is one lookup away in
`docs/ASM_INDEX.csv`.
