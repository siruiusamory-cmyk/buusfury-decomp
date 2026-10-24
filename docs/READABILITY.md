# Readability rules

Every rule below is held by `tools\lint\lints.py`, which the gate runs before the build, and by
`tools\check_links.py`, which CI runs with it. A count moves only in the change that measures it.

| rule | what the tree does | lint |
| --- | --- | --- |
| one file per function start | `asm/<symbol>.s`, included in address order by `asm/buu.s` or `asm/rest_of_the_game.s`; a ledger row's name is the label at its address, and `tools\lint\ASM_INDEX.csv` maps every name and address to its file | `ASM-layout`, `NAMING-ledger-label` |
| hardware register addresses | one include of GBATEK names, and every literal that is a register or a region base replaced by its symbol; `tools\lint\HARDWARE_BASELINE.txt` admits the residue and nothing else | `ASM-hardware-literal` |
| RAM addresses and flags | a name only on one of the evidence classes in [NAMING.md](NAMING.md); `tools\lint\RAM_BASELINE.txt` holds the raw literal count as a ratchet | `ASM-ram-ratchet` |
| unnamed data tables and records | a table earns a name only with a consumer or a structural proof; a generator's record class names what it decodes, and an extent name stays until then | counted by the gate, not ratcheted |
| magic constants | a literal that encodes a hardware field, flag or table budget takes a name in `include/`; an instruction immediate stays literal, because it is the byte being reproduced | counted, not ratcheted |
| the newcomer path | [NEWCOMER.md](NEWCOMER.md) carries every step from a clone to a changed function | `DOC-newcomer-path` |
| tool code | a tool that the build or a check does not run does not stay in the tree; no module reaches outside the repository for a module | `P-148-repo-module-path`, `DUP-block` |
| the gate's figures | `README.md` carries the gate's own figures, and the lint reads them from the gate | `README-numbers` |

## The ratchets

| file | holds |
| --- | --- |
| `tools\lint\HARDWARE_BASELINE.txt` | value, admitted occurrence count for a raw hardware address |
| `tools\lint\RAM_BASELINE.txt` | the raw RAM literal count |
| `tools\lint\NAMING_BASELINE.txt` | the address-named function count |
| `tools\lint\ASM_INDEX.csv` | one row per function start, checked against the census |

A count below its baseline is a finding too: the baseline is lowered in the same change, so a
ratchet cannot quietly drift upward.
