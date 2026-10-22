# Six end-of-ROM rows with a proven stride and no count

Measured 2026-10-19 from ROM sha256 `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.
Data addresses are file offsets, instruction addresses are bus addresses, and every quote is the
halfword present at that address. Decodes come from `tools/research/thumb_annotate.py`.

Each row below has a reader that proves its record stride. None has an instruction that proves how
many records the row holds, so none becomes source: a stride is the reader's arithmetic, not the
row's extent. Rows still raw in `docs/research/RESIDUAL_LEDGER.csv`. None of the six is called
irreducible: each count column measures what the readers hold on the date above, and a reader found
later moves the row.

| row | bytes | class | base literal | stride | index | count | verdict |
|---|---|---|---|---|---|---|---|
| `0x762270..0x76ACC0` | 35,408 | R29 | `0x01B4DC` = `0x08762270` | 36 | byte at `[obj+0x10]` | none | no bound |
| `0x76E264..0x7703AC` | 8,520 | R20 | `0x0386E8` = `0x0876E264` | 36 | byte at `[obj+0x10]` | none | no bound |
| `0x72D6B8..0x7315A8` | 16,112 | R24 | `0x024954` = `0x0872D6B8` | 60 | byte at `[obj+0x10]` | none | no bound |
| `0x7144D8..0x7180E9` | 15,377 | R23 | `0x00B800` = `0x087144D8` | `0x100` block | 2 bits, `(n>>3)&3` | none | no bound, bytes copied in place |
| `0x76174C..0x762270` | 2,852 | R29 | `0x037244` = `0x0876174C` | 12 | call's 4th argument, 32-bit | none | no bound |
| `0x77B2A8..0x77C41C` | 4,468 | R28 | `0x03C408` = `0x0877B2A8` | 12 | byte at `[obj+0x10]` | none | no bound |

## `0x762270`

Reader body `0x0801B2B4..0x0801B46E`, entered as a branch target at `0x0801B2AA` (`D203`).

- base `0x0801B2F6` `4979` `ldr r1,[pc,#0x1e4]`, pool file `0x01B4DC` = `0x08762270`
- stride `0x0801B2FA` `C300` `lsls r3,r0,#3`, `0x0801B2FC` `1818` `adds r0,r3,r0`,
  `0x0801B2FE` `8000` `lsls r0,r0,#2`, so 36 bytes
- index `0x0801B2F4` `207C` `ldrb r0,[r4,#0x10]`
- the body compares `0x0801B2B4` `3C28` `cmp r0,#0x3c`, `0x0801B2EA` `0828` `cmp r0,#8`,
  `0x0801B2F0` `0128` `cmp r0,#1`, `0x0801B33E` `0028` `cmp r0,#0`, `0x0801B344` `342A`
  `cmp r2,#0x34`, `0x0801B382`/`0x0801B438`/`0x0801B446` `0028` `cmp r0,#0`; none bounds the
  record index. A byte index caps the array at 256 x 36 = 9,216 B, 26 % of the row.
- `35,408 = 36 x 983 + 20`, so the stride does not tile the row.

## `0x76E264`

Reader body `0x080383D4..0x08038496`.

- base `0x08038458` `A34B` `ldr r3,[pc,#0x28c]`, pool file `0x0386E8` = `0x0876E264`
- stride `0x0803845A` `C100`, `0x0803845C` `0918`, `0x0803845E` `8900`, so 36 bytes
- index `0x08038432` `307C` `ldrb r0,[r6,#0x10]`, kept at `[r4,#0x40]` and reloaded at
  `0x08038456`; its only bound is `0x08038436` `0028` `cmp r0,#0`, a null test
- parallel table `0x08038464` `A149` `ldr r1,[pc,#0x284]`, pool file `0x0386EC` = `0x0807268C`,
  indexed `0x08038466` `C000` `lsls r0,r0,#3` with no compare. The table holds four 8-byte
  direction pairs at `0x07268C..0x0726AC` and the next structure starts at `0x0726AC`
  (`0x03001C4C`), so its length is 4 by shape and cannot bound a 236-record array. It is loaded
  and indexed unchecked at `0x0801B3F8` and `0x0803703A` as well.
- `8,520 = 36 x 236 + 24`.

## `0x72D6B8`

Reader body `0x080246B4..0x08024766`.

- base `0x0802472C` `8949` `ldr r1,[pc,#0x224]`, pool file `0x024954` = `0x0872D6B8`
- stride `0x08024728` `3001` `lsls r0,r6,#4`, `0x0802472A` `801B` `subs r0,r0,r6`,
  `0x0802472E` `8000` `lsls r0,r0,#2`, so 60 bytes
- index `0x08024714` `367C` `ldrb r6,[r6,#0x10]`; no compare touches it, so the byte width caps
  the array at 256 records = `0x3C00` B and leaves `0x2F0` B of the row out of its reach
- the VRAM copy at `0x0802470C` comes from `0x024950` = `0x0872C3B8` with size `0x08024706`
  `1322` `movs r2,#0x13` plus `0x08024708` `1202` `lsls r2,r2,#8` = `0x1300`; that source plus
  its size ends exactly at `0x72D6B8`, so the copy decodes none of this row
- `16,112 = 268 x 60 + 32`.

## `0x7144D8`

Reader body `0x0800B55C..0x0800B5C0`.

- base `0x0800B57E` `A04A` `ldr r2,[pc,#0x280]`, pool file `0x00B800` = `0x087144D8`
- block offset `0x0800B568` `C006` `lsls r0,r0,#0x1b` then `0x0800B56A` `810F`
  `lsrs r1,r0,#0x1e`, so 2 bits select one of four `0x100`-byte blocks; size `0x0800B582`
  `FF22` `movs r2,#0xff` plus `0x0800B584` `0132` `adds r2,#1` = `0x100`
- `0x0800B56E` `8842` `cmp r0,r1` skips the copy when the selected block is the current one, a
  dirty check and not a count
- the copy at `0x0800B586` `f03d` `fdd7` `bl 0x08049138` takes `0x0800B57E` `a04a`
  `ldr r2,[pc,#0x280]` = `0x087144D8` plus `0x0800B578` `0902` `lsls r1,r1,#8`, added at
  `0x0800B580` `8918` `adds r1,r1,r2`: the row's own bytes, read in place
- no call in the body loads `0x08049120` and no buffer is written before the copy; the veneer's
  body at `0x03000768` is `03000778` `f813b1e8` `ldm r1!,{r3,r4,r5,r6,r7,r8,sb,ip}` and
  `0300077C` `f813a0e8` `stm r0!,{r3,r4,r5,r6,r7,r8,sb,ip}`, so the copy decodes nothing
- the select at `0x0800B568` `c006` `lsls r0,r0,#0x1b` and `0x0800B56A` `810f`
  `lsrs r1,r0,#0x1e` keeps two bits, so the reader reaches four of the row's blocks
- `15,377 = 60 x 0x100 + 0x11`; the 17 trailing bytes are the head of block 60 at `0x7180D8`,
  which continues past the row. The four blocks the reader reaches are 1,024 B of it.

## `0x76174C`

Reader body `0x08036FC0..0x080370CA`.

- base `0x08037084` `6F49` `ldr r1,[pc,#0x1bc]`, pool file `0x037244` = `0x0876174C`
- stride `0x08037086` `4300` `lsls r3,r0,#1`, `0x08037088` `1818` `adds r0,r3,r0`,
  `0x0803708A` `8000` `lsls r0,r0,#2`, so 12 bytes; the record's first word is walked at
  `0x08037094` `4200`, `0x08037096` `1218`, `0x08037098` `D200`, so 24 bytes
- index `0x08037082` `0A98` `ldr r0,[sp,#0x28]`, which is the call's fourth argument and is not
  masked or compared anywhere in the body; the callers at `0x0803A708` `0223` `movs r3,#2` and
  `0x0803CDB2` `2302` `movs r3,#2` reach record 2, a lower bound of three records and not a count
- `2,852 = 12 x 237 + 8`.

## `0x77B2A8`

Reader body `0x0803C2F8..0x0803C376`, a coherent Thumb decode and a ledger `code` region, but the
image holds no branch and no pointer word to `0x0803C2F8`; the row is counted as having a reader
with no static caller.

- base `0x0803C31E` `3A49` `ldr r1,[pc,#0xe8]`, pool file `0x03C408` = `0x0877B2A8`
- stride `0x0803C320` `4300`, `0x0803C322` `1818`, `0x0803C324` `8000`, so 12 bytes
- index `0x0803C31C` `207C` `ldrb r0,[r4,#0x10]`, written at `0x0803C302` `2074`
  `strb r0,[r4,#0x10]` from a word loaded at `0x0803C2FC` `C068`, truncation only
- second table at base `+0x30`: `0x0803C3AC` `164A` plus `0x0803C3AE` `3032` `adds r2,#0x30`
  is a fixed distance; the index is scaled `0x0803C3B0` `C900` `lsls r1,r1,#3` with no compare
- the word before the base is read as a size at `0x0803C36C` `0438` `subs r0,#4` and
  `0x0803C36E` `0068` `ldr r0,[r0]`, and it holds `0x03001C4C`, an IWRAM pointer
- `4,468 = 12 x 372 + 4`.

## The routes a count could come from, and what each gave

| route | measured outcome |
|---|---|
| loop compare on the record index | absent from all six bodies; the compares in them bound other fields and are quoted above |
| index width | 8 bits in four rows, 32 bits in `0x76174C`; a width is a maximum, not a size |
| parallel table with a length | `0x0807268C` is four 8-byte direction pairs, no length and no compare at any of its loads |
| size word before the base | `0x762270` 0, `0x76E264` `0x00000502`, `0x72D6B8` 0, `0x7144D8` 0, `0x76174C` `0x08760CEC`, `0x77B2A8` `0x03001C4C`; no reader loads one as a length |
| terminator | no sentinel compare on a record word in any body |
| second base literal inside the row | none of the six rows is named twice; the inner arrays that are indexed (`0x0801B38A` scale 16, `0x08037094` scale 24, `0x0803C3AC` `+0x30`) carry their own unchecked index |

## The runtime census, and why it cannot state a count

`docs/research/ENDROM_INDEX_CENSUS.md` is the read watch over the first three rows of the table
above: each row watched in full, plus the liveness read, one headless run per map. It re-derives
itself from `docs/research/RUNTIME_READ_RUNS.csv` and `docs/research/RUNTIME_READ_ROW_HITS.csv`, so
every run it counts carries a log digest and a liveness count.

Every one of the three rows stays raw-data. The highest index a run reaches is a lower bound, and
none of the three reader bodies tests an end marker - the compares are the ones quoted above - so no
watched read can name the array's last record. The word one reader loads from just before a base is
an IWRAM pointer it appends to a runtime list at `0x0801191A`, not a length. A row the watch never
reaches is stated as not reached, and its step is blocked rather than guessed.

## Consequence

82,737 B across the six rows stay raw-data. No family module, no build-time generator and no gate
movement follow from a stride alone, and none of the copies that do reach an end-of-ROM row is a
decode. A count for any one row would have to come from a runtime read-watch on its base, or from a
reader that compares its index against a value the bytes can be shown to hold.
