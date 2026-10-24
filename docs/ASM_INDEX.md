# Where a function lives

`tools\lint\ASM_INDEX.csv` is the index. It is a check input: `tools\lint\lints.py` refuses a row
whose address carries no such label, or whose file does not carry it.

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
holds its extent; the index gives its address and that file.

## A naming-ledger row

`tools\lint\NAMING_LEDGER.csv` names the starts the tree has promoted. The label at each address
carries the row's name, in a file named after it (`asm/Blend_WriteControl1.s`,
`asm/Irq_WriteEnable1.s`); the two whose start is inside `asm/buu.s` stay there and the index points
at `asm/buu.s`.

## Using the index

The index has one row per census start: `address,kind,symbol,file`.

- A name: find the symbol in the `symbol` column, open the file it names.
- An address: find the row with that address, open the file it names.
- A file: read its first label; the file name repeats it.

`kind` is the census kind from `tools/research/FUNCTION_BOUNDS.csv`: `start` is reached by a call,
table, vector or prologue rule, `unreferenced` is a transcribed row start that nothing reaches.
