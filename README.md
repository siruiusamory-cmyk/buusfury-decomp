# Dragon Ball Z: Buu's Fury disassembly

**A byte-exact disassembly of Dragon Ball Z: Buu's Fury (GBA, USA) that rebuilds the original ROM from tracked source.**

![License](https://img.shields.io/badge/license-MPL--2.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Game%20Boy%20Advance-lightgrey.svg)
![Build](https://img.shields.io/badge/build-byte--exact-brightgreen.svg)

## Contents

- [What this is](#what-this-is)
- [What this is not](#what-this-is-not)
- [Progress](#progress)
- [Building](#building)
- [Repository layout](#repository-layout)
- [Credits and license](#credits-and-license)

## What this is

The program code is ARM and Thumb assembly in `asm/`. ARM Developer Suite 1.2 assembles and links
it back into the retail ROM, and the build checks the result against the retail sha256. The game's
graphics, audio, text and record tables are rebuilt at build time by generators that decode them
from your own copy of the game and re-encode them byte for byte.

It builds one ROM:

* Dragon Ball Z: Buu's Fury (USA), sha1 `f1c4b07554d2a3b1ad2f325307051e775ce68087`

## What this is not

This is not a decompilation. Almost all of the game's code is still assembly, and only a handful of
small C files exist in `src/`. Most functions are still named by their address (`sub_08000158`,
`loc_0800016A`): 2,868 of the 3,025 functions the census classifies. Naming them is the next
readability step, and `tools/lint/lints.py` holds the count to a measured baseline with
`tools/lint/NAMING_LEDGER.csv` as the record of every promotion; `tools/research/name_evidence.py
--mode audit` checks every row's evidence against your own copy of the image. No part of the code is
claimed to match the original compiler's C output.

The progress figure below measures how much of the ROM the build produces from tracked source. It
does not measure how much of the code has been turned into C.

## Progress

94.0959 % of the ROM (7,893,334 of 8,388,608 bytes) builds from tracked source: assembly, tables
with named fields, and generators that rebuild assets from your own ROM. The rest is still copied
into the build as raw slices of the original image. `python tools\gate\gate.py` prints the split,
and [docs/DEFINITION_OF_DONE.md](docs/DEFINITION_OF_DONE.md) says what counts as source.

Of what remains, 3.9214 % is identified binary (328,954 B): bytes whose purpose is known but which
still have no reader that rebuilds them.

## Building

You need ARM Developer Suite 1.2, Python 3.12, grit, Visual Studio or Build Tools 2022 with the C++
workload, and your own copy of the game saved as `baserom.gba`. [INSTALL.md](INSTALL.md) has the
details, and [docs/README.md](docs/README.md) is the guide to the code once it builds.

```
extract.cmd
rebuild.cmd
python tools\gate\gate.py
```

`rebuild.cmd` builds the compressor from its own source on the first run. The gate rebuilds from
scratch and prints `DIGEST MATCH` and `GATE PASS` when the output equals the retail ROM.

## Tests

`python -m pytest -q tools` runs every test file in the tree, and the GitHub Actions workflow runs
that same command on `ubuntu-latest` without the game. A test that needs your ROM, ARM Developer
Suite 1.2 or `cmd.exe` skips itself and names the one that is absent.

## Repository layout

| Path | Contents |
| --- | --- |
| `asm/` | the game's code and data as assembly |
| `src/` | the few parts already written in C |
| `include/` | shared assembler and C declarations |
| `tools/` | what builds the ROM and what checks it; [tools/README.md](tools/README.md) lists every entry |
| `docs/` | a reader's guide to the code and the game's data |
| `work/` | the byte ledger the gate reads |

## Credits and license

This tree starts from the [2genkidev/buusfury](https://github.com/2genkidev/buusfury) disassembly.
Third-party code and credits are listed in [NOTICE](NOTICE). Changes are listed in
[CHANGELOG.md](CHANGELOG.md).

No ROM, BIOS or extracted game data is included. You need your own legally obtained copy of the
game. Not affiliated with pret, Nintendo, Atari, Bandai or Webfoot Technologies.

MPL-2.0, see [LICENSE](LICENSE).
