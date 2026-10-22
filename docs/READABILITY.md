# Readability audit

Every count below is printed by `python tools\readability\audit.py`, which reads the tracked tree
only. The rule column says what the tree does about the class and which lint holds it; a count moves
only when the tool prints its new figure.

| class | before | after | rule | lint |
| --- | --- | --- | --- | --- |
| asm file organisation | 225 `asm/*.s` files; 12 slice files held all 3,094 function starts; the largest held 833 starts in 42,698 lines | 2,785 files; 2,508 address-named files carry one function start each; no file carries two; the 64 ledger names that live in a function file own the file that holds their start, and the two inside `asm/buu.s` are indexed there; 282 unlabelled starts stay in the file that holds their extent | one file per labelled function start, `asm/<symbol>.s`, included in address order; a ledger row's name is the label at its address; `docs/ASM_INDEX.csv` maps every name and address to its file | `ASM-layout`, `NAMING-ledger-label` |
| hardware register addresses | 24 literal sites in the I/O page (10 values) and 14 in the palette, VRAM and OAM pages (6 values) | 3 sites in the I/O page (2 values) and 1 in the palette page (1 value), all listed in `docs/HARDWARE_BASELINE.txt` | one include of GBATEK names, every literal that is a register or a region base replaced by its symbol; `docs/HARDWARE_BASELINE.txt` admits the residue and nothing else | `ASM-hardware-literal` |
| RAM addresses and flags | 158 sites, 123 of them raw; 69 distinct addresses; 0 semantic names | 108 raw sites, 61 distinct; 8 proven names in `docs/RAM_LEDGER.csv` (plus 3 value constants); the rest address-named and held by a ratchet | a name only on one of the evidence classes (`docs/NAMING.md`, `docs/RAM_LEDGER.csv`); `docs/RAM_BASELINE.txt` holds the raw count | `ASM-ram-ratchet` |
| unnamed data tables and records | 12,614 `INCBIN` lines; 3,128 raw rows / 494,250 B; 0 carry a semantic symbol | unchanged | a table earns a name only with a consumer or a structural proof; a generator's record class names what it decodes, and an extent name stays until then | counted above, not ratcheted |
| magic constants | 35 literal sites, 25 distinct values in C outside every address range | unchanged | a literal that encodes a hardware field, flag or table budget takes a name in the include (A3 named three); an instruction immediate stays literal, because it is the byte being reproduced | counted above |
| doc gaps on the newcomer path | 6 steps; 0 of 6 in one path; `clone` and find-a-function absent from the whole tree | 6 of 6 in `docs/NEWCOMER.md`, and the tree gained `docs/ASM_INDEX.md` | one page carries every step with the command that ran it, and a lint refuses a page that loses one | `DOC-newcomer-path` |
| tool code | 1,513 module-level definitions, 15 unreferenced, 2 names of one or two characters | 1,547 definitions, 1 unreferenced, 0 short names | delete what nothing reaches; the one survivor is a subcommand the dispatcher reaches by name | `DUP-block` (unchanged) |
| test naming | 116 tool modules, 83 test files, 45 modules with no same-name test | 119 modules, 88 test files, 44 modules with no same-name test | a new module brings `test_<module>.py`; the existing gaps are counted, not renamed wholesale | counted above |

## What the numbers moved

`asm/` lost its twelve slice files and gained 2,508 address-named function files, and the 64 starts
the naming ledger names in a function file became `asm/<name>.s`; the moves are byte-neutral, which
is why the digest still matches and the symbol set still has its 26,042 entries. The hardware class
went from 38 literal sites to 4 by naming the registers the tree actually reads (`REG_IE`,
`REG_TM0CNT_L`, `REG_VCOUNT`, `REG_BG0HOFS`, `REG_BLDALPHA`, `REG_DMA3SAD`, `REG_SIODATA32_L`,
`REG_DISPCNT`) and the three region bases (`PLTT`, `VRAM`, `OAM`).

`python tools\readability\rank.py` orders the naming work: the address-named functions by call-site
count, the address-named RAM words by reference count, and the raw slices by the references the tree
makes to them. `python tools\readability\rank.py --bases` ranks the RAM base pointers by the fields a
reader meets through them, and `python tools\readability\name.py` applies a batch of promotions with
its ledger rows, its index rows and the ratchet in one pass.

The four admitted hardware sites are `0x04000003` twice and `0x04000053`, `0x05000003` once each.
They sit in pool words of the ARM library body and of two register tables; nothing measured shows
which register each names, so each stays a number and the baseline records it.

`0x03000000` stays a literal in `asm/crt0.s` for the same reason a name is not enough: the DMA copy
reader in `tools/recomp/export_inputs.py` reads that word's value to describe the copy, and a symbol
there stops it. Every other RAM address with evidence is in `docs/RAM_LEDGER.csv`.

## The ratchets

| file | holds |
| --- | --- |
| `docs/HARDWARE_BASELINE.txt` | value, admitted occurrence count for a raw hardware address |
| `docs/RAM_BASELINE.txt` | the raw RAM literal count |
| `docs/NAMING_BASELINE.txt` | the address-named function count |
| `docs/ASM_INDEX.csv` | one row per function start, checked against the census |

A count below its baseline is a finding too: the baseline must be lowered in the same tree, so a
ratchet cannot quietly drift upward.
