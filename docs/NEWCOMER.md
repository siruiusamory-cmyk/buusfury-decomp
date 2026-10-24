# From a clone to a change

Six steps, each a command that prints what the next one needs.

## 1. Clone

```
git clone <the repository> buusfury
cd buusfury
```

The tree carries no ROM and no game asset. Everything the build needs beyond the source comes from
your own copy.

## 2. Put your ROM in place

Save Dragon Ball Z: Buu's Fury (USA) as `baserom.gba` in the clone. The build reads its sha1 from
`baserom.sha1` and refuses any other image, so a wrong dump stops at the first command instead of
producing a wrong result.

## 3. Extract

```
extract.cmd
```

It writes the image payloads under `assets\generated\`, two palettes and six payload stores, the
tile-bank sheets, the map block's payloads and records, and one slice per transcribed raw fragment.
None of that is tracked; re-running it overwrites edits.

## 4. Build

```
rebuild.cmd
```

The compressor is built from its own source on the first run. Then `armasm` assembles `asm\buu.s`
and `asm\rest_of_the_game.s`, `tcpp` compiles the units `rebuild.cmd` lists, the generators re-encode
the payloads and assets, `armlink` links by `scatter.ld` and `fromelf` writes the image. Set `ADS`
first if ARM Developer Suite 1.2 is not beside the checkout's parent directory.

## 5. Gate

```
python tools\gate\gate.py
```

It runs the lints and the function-bounds census, purges every object, rebuilds, and prints
`DIGEST MATCH` and `GATE PASS` when the image equals the retail sha256. `--cold` measures the whole
procedure against an isolated encode cache.

## 6. Find a function

`tools\lint\ASM_INDEX.csv` has one row per function start: `address,kind,symbol,file`.

```
findstr /c:"sub_0800536A" tools\lint\ASM_INDEX.csv
```

answers with the file that holds it. `docs\ASM_INDEX.md` explains the layout and the data carriers.
`tools\research\FUNCTION_BOUNDS.csv` says which addresses are function starts, interior blocks or
unreached rows.

## 7. Change one thing

Open the file the index names. A name change is the byte-neutral change this tree wants most:
`docs\NAMING.md` says which evidence promotes `sub_0800XXXX` to a `Module_Verb`, and the same commit
adds one row to `tools\lint\NAMING_LEDGER.csv`. A code change that moves bytes is a different job:
the gate prints `DIGEST MISMATCH` and names the differing offsets, so a change that is meant to
reproduce the retail bytes cannot land silently.

Then run the gate again. `DIGEST MATCH` for a name change, the named difference for a byte change.

## Where to read next

| page | says |
| --- | --- |
| `README.md` | what the tree is, the progress figure and the commands above |
| `docs\README.md` | what the game's code is organised into, and where to look next |
| `docs\READABILITY.md` | the rules a change has to keep readable |
| `docs\NAMING.md` | function, data and unit names, and the evidence each needs |
| `docs\ASM_INDEX.md` | how a function, an address and a file find each other |
| `docs\DEFINITION_OF_DONE.md` | what counts as source and what the finish line is |
| `CONTRIBUTING.md` | formatting, the pre-commit hook and how to convert a unit to C |
