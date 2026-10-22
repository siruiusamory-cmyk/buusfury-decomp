# The `fill/padding` and `pointer-tables` rows: what moved, and why the rest did not

GEN-COMPRESSED-001, row set of 2026-10-16: `fill/padding` 3 rows / 43 B (all converted to `SPACE` blocks) and `pointer-tables` 84 rows / 1,118 B (41 rows / 460 B converted). A non-zero fill run is refused, never emitted as the wrong byte.

    python tools\research\fill_promote.py --slice 0xb5 0xbc --slice 0x7122dc 0x7122f8 ^
        --slice 0x75024c 0x750254 --minimum 4 --apply

## `fill/padding` - 3 rows, 43 B, all converted

| row | bytes | value | carrier | conversion |
|---|---|---|---|---|
| `0x0000B5..0x0000BC` | 7 | `0x00` | `asm/rom_header.s:44` | `asm/fill_b5.s` (`SPACE 7`), carrier keeps `|unk_080000B5|` |
| `0x7122DC..0x7122F8` | 28 | `0x00` | `asm/rawlabeled_7122dc.s:17` | `asm/fill_7122dc.s` (`SPACE 28`), carrier keeps `EXPORT |unk_087122DC|` |
| `0x75024C..0x750254` | 8 | `0x00` | `asm/rest_of_the_game.s:12657` | `asm/fill_75024c.s` (`SPACE 8`), carrier keeps `|unk_0875024C|` |

## `pointer-tables` - 84 rows, 1,118 B, 41 rows / 460 B converted

| verdict | rows | bytes | what the row needed |
|---|---|---|---|
| converted | 41 | 460 | 182 words: 32 a label the tree declares, 150 an IWRAM address |
| a word lies inside a carrier with no label at it | 31 | 478 | a name for a target in the middle of a carried slice |
| a word only a derived name has | 6 | 84 | `.constdata$76`, `.data$7675` twice, `map_record_run_1923a0_root_record`, `map_record_run_2520d4_root_record`, `endrom_container_run_79bf2c`: generated or linker-internal names, none of which carries an address |
| the carrier is a generated fragment | 6 | 72 | `rawlabeled.citation_check` regenerates that text and refuses one it did not write |
