# The end-of-ROM regions: what a reader says about the biggest rows

Measured 2026-10-20 from ROM sha256 `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.
Data addresses are file offsets, instruction addresses are bus addresses `0x08...`, and every quote
is the halfword present at that file offset (a Thumb decode of it is beside it).

Population: the 1,129 rows / 328,954 B `docs/research/RAW_REMAINDER.csv` still calls raw in the eleven
regions R20, R21, R23, R24, R25, R26, R27, R28, R29, R30 and R31. `docs/research/ENDROM_NULL_CENSUS.md`
is the per-row reader and null over that population, measured by `tools/research/endrom_readers.py`.

## What a reader gives, per region

| region | rows | bytes | rows with a read pc | read bytes | biggest row |
|---|---|---|---|---|---|
| `R20` | 13 | 57,568 | 0 | 0 | `0x77110C..0x77AD10` 39,940 |
| `R21` | 32 | 57,472 | 6 | 40,551 | `0x725749..0x72A690` 20,295 |
| `R23` | 37 | 48,100 | 10 | 27,105 | `0x7144D8..0x7180E9` 15,377 |
| `R24` | 6 | 21,064 | 2 | 16,148 | `0x72D6B8..0x7315A8` 16,112 |
| `R25` | 4 | 10,784 | 2 | 7,592 | `0x7504CC..0x7520D4` 7,176 |
| `R26` | 7 | 6,680 | 1 | 40 | `0x753A18..0x7548E8` 3,792 |
| `R27` | 5 | 8,404 | 5 | 8,404 | `0x754A1C..0x756A04` 8,168 |
| `R28` | 6 | 4,732 | 0 | 0 | `0x77B2A8..0x77C41C` 4,468 |
| `R29` | 17 | 75,164 | 6 | 20,644 | `0x762270..0x76ACC0` 35,408 |
| `R30` | 80 | 17,850 | 12 | 2,152 | `0x74F08C..0x7501EC` 4,448 |
| `R31` | 922 | 21,136 | 236 | 4,140 | `0x710FA3..0x71115B` 440 |

145 rows are named by a decoded load's literal value, and every one of them names the row at offset
`+0`. So across 328,986 B the code states 145 base addresses and one 2-bit block selector, which is a
name and not a layout (P-733).

## The biggest named row of each region, and what it does not say

| row | bytes | reader site | quote | what the reader adds |
|---|---|---|---|---|
| `0x77110C..0x77AD10` | 39,940 | file `0x038B98` (6 sites) | `8E48` `ldr r0,[pc,#0x238]`, pool file `0x038DD4` = `0x0877110C` | the base only: at `0x08038B9A` `0068` `ldr r0,[r0]` it reads one word of the object, not of the row |
| `0x762270..0x76ACC0` | 35,408 | file `0x01B2F6` | `7949` `ldr r1,[pc,#0x1e4]`, pool file `0x01B4DC` = `0x08762270` | base, then `0x0801B2FA` `C300` `lsls r3,r0,#3` / `1818` / `8000` = stride 36, index `ldrb r0,[r4,#0x10]`; no compare on the index |
| `0x75A7A4..0x75F7AC` | 20,488 | file `0x036A62` (4 sites) | `C24D` `ldr r5,[pc,#0x308]`, pool file `0x036D6C` = `0x0875A7A4` | the base, which the reader stores into an object at `0x08036A64` `2060` `str r0,[r4]` |
| `0x72084C..0x725018` | 18,380 | file `0x01FFFC` (7 sites) | `A34B` `ldr r3,[pc,#0x28c]`, pool file `0x02028C` = `0x0872084C` | base, indexed by a per-frame counter `cmp r2,#2` at `0x0802002E`; a counter over frames, not over records |
| `0x72D6B8..0x7315A8` | 16,112 | file `0x02472C` | `8949` `ldr r1,[pc,#0x224]`, pool file `0x024954` = `0x0872D6B8` | base, then `0x0802472E` `8000` `lsls r0,r0,#2` = stride 4 at this site and stride 60 at `0x08024728`; two strides, neither bounded |
| `0x7144D8..0x7180E9` | 15,377 | file `0x00B57E` | `A04A` `ldr r2,[pc,#0x280]`, pool file `0x00B800` = `0x087144D8` | 2 bits select one of four `0x100`-byte blocks (`0x0800B568` `C006` `lsls r0,r0,#0x1b`, `0x0800B56A` `810F` `lsrs r1,r0,#0x1e`), copied to VRAM by `0x0800B586` `bl 0x08049138` with size `0x100`: an identity copy |
| `0x76E264..0x7703AC` | 8,520 | file `0x038458` | `A34B` `ldr r3,[pc,#0x28c]`, pool file `0x0386E8` = `0x0876E264` | base plus stride 36 (`0x0803845A..0x0803845E`) and a parallel 8-byte table at pool file `0x0386EC`; the index `ldrb r0,[r6,#0x10]` has no compare |
| `0x754A1C..0x756A04` | 8,168 | file `0x02C7CA` (2 sites) | `4D48` `ldr r0,[pc,#0x318]`, pool file `0x02C900` = `0x08754A1C` | the base only |
| `0x7504CC..0x7520D4` | 7,176 | file `0x02A840` (6 sites) | `6E48` `ldr r0,[pc,#0x2b8]`, pool file `0x02A9FC` = `0x087504CC` | base, then `0x0802A844` `0068` `ldr r0,[r0]` |
| `0x753A18..0x7548E8` | 3,792 | file `0x02BEF0` (7 sites) | `5A48` `ldr r0,[pc,#0x2c0]`, pool file `0x02C05C` = `0x08753A18` | the base only |
| `0x74F08C..0x7501EC` | 4,448 | file `0x0293E8` (6 sites) | `764B` `ldr r3,[pc,#0x260]`, pool file `0x0295C4` = `0x0874F08C` | the base only |
| `0x759680..0x75A0E9` | 2,665 | file `0x035A18` (4 sites) | `5B4A` `ldr r2,[pc,#0x2b8]`, pool file `0x035B88` = `0x08759688` | a base at `+8` inside the row, this family's own extent proof (below) |
| `0x6FDA4C..0x6FDB18` | 204 | file `0x00430C` (3 sites) | `894F` `ldr r7,[pc,#0x224]`, pool file `0x004534` = `0x086FDA4C` | the base only |

## The six rows with a stride and no count

Restated from `docs/research/ENDROM_BOUND_CENSUS.md` in this census's own decode, in the regions above:

| row | bytes | base pool | stride code | index | tiles the row |
|---|---|---|---|---|---|
| `0x762270..0x76ACC0` | 35,408 | `0x01B4DC` | `C300`/`1818`/`8000` = 36 | `ldrb r0,[r4,#0x10]` | no: 36 x 983 + 20 |
| `0x76E264..0x7703AC` | 8,520 | `0x0386E8` | `C100`/`0918`/`8900` = 36 | `ldrb r0,[r6,#0x10]` | no: 36 x 236 + 24 |
| `0x72D6B8..0x7315A8` | 16,112 | `0x024954` | `3001`/`801B`/`8000` = 60 at `0x08024728` | `ldrb r6,[r6,#0x10]` | no: 60 x 268 + 32 |
| `0x7144D8..0x7180E9` | 15,377 | `0x00B800` | 2-bit block of `0x100` | `(r0>>3)&3` | no: 60 x 256 + 17 |
| `0x76174C..0x762270` | 2,852 | `0x037244` | `4300`/`1818`/`8000` = 12 | call's 4th argument | no: 12 x 237 + 8 |
| `0x77B2A8..0x77C41C` | 4,468 | `0x03C408` | `4300`/`1818`/`8000` = 12 | `ldrb r0,[r4,#0x10]` | no: 12 x 372 + 4 |

No reader of any of the six compares its index against a constant, so none of the six states a count,
and the table above is why none of them converts on the stride alone.

## The sprite-descriptor family: three tables (R30, R25, R20)

One entry is `{u32 dest; u16 size 0x2000; u16 mode; u32 tile}`, 12 B, and one record is a whole number
of entries. `tools/mapcontainer/pairsprite.py` emits all three tables, and
`tools/mapcontainer/generate_mapcontainer.py --block endrom` writes them.

| table | region | records | entry bytes | bytes | dest words | modes | tiles |
|---|---|---|---|---|---|---|---|
| `0x759620..0x759680` | R30 | 4 | 2 x 12 | 96 | `0x08080000` | 0, `0x1000` | 4 blocks `0x759520..0x759620` |
| `0x75043C..0x7504CC` | R25 | 4 | 3 x 12 | 144 | `0x08080000` | 0, `0x1000`, `0x2000` | 6 blocks `0x7502BC..0x75043C` |
| `0x76E264..0x76E2F4` | R20 | 4 | 3 x 12 | 144 | `0x08080000`, `0x0808F800`, `0x080800F8` | 0, `0x1000`, `0x2000` | 6 blocks `0x76E0E4..0x76E264` |

Every one of the 36 entries meets the same four conditions: the dest word's high half is `0x0808`, the
size word is `0x2000`, the mode is at most `0x2000`, and the tile is a `0x40`-byte block inside the
table's own six- or four-block run.

The consumers, all walking the record stride:

- R30, stride 24: `0x08035670` `4A86` `ldr r2,[pc,#0x218]`, pool file `0x03588C` = `0x08759620`;
  `0x08035672` `0041` `lsls r1,r0,#1`, `0x08035674` `1809` `adds r1,r1,r0`, `0x08035676` `00C9`
  `lsls r1,r1,#3`, `0x08035678` `1889` `adds r1,r1,r2`. It copies each entry's tile to VRAM:
  `0x08035690` `6889` `ldr r1,[r1,#8]`, `0x08035696` `2240` `movs r2,#0x40`, then `bl 0x08049138`,
  and the second entry at `0x080356A8` `6949` `ldr r1,[r1,#0x14]` with the same size.
- R25, stride 36: `0x0802A378` `606C` `ldr r0,[r4,#0x44]`, `0x0802A37A` `4B84` `ldr r3,[pc,#0x210]`,
  pool file `0x02A58C` = `0x0875043C`; `0x0802A37C` `C100` `lsls r1,r0,#3`, `0x0802A37E` `0918`
  `adds r1,r1,r0`, `0x0802A380` `8900` `lsls r1,r1,#2`, `0x0802A382` `C918` `adds r1,r1,r3`,
  `0x0802A384` `A164` `str r1,[r4,#0x48]`.
- R20, stride 36: the same four instructions at `0x08038458` `A34B` `ldr r3,[pc,#0x28c]`, pool file
  `0x0386E8` = `0x0876E264`, `0x0803845A` `C100`, `0x0803845C` `0918`, `0x0803845E` `8900`, with the
  index byte at `0x08038432` `307C` `ldrb r0,[r6,#0x10]`.

The extents are three different proofs, all of them the end of the table and not a slice boundary:

- R30: the next structure's own base literal at file `0x051CCC` = `0x08759680` is exactly `+4 x 24`, and
  the word there is `0x03001C4C`, an IWRAM pointer, so no fifth record fits.
- R25: the next structure's base literal at file `0x02A9FC` = `0x087504CC` is exactly `+4 x 36`, and
  the word there is `0x03001C4C`; the row's own span ends on the same byte.
- R20: the table is the first 144 B of an 8,520 B row. The 13th record at `0x76E2F4` holds
  `0x00000000` and fails the dest word's high half, and the word at file `0x0770CFC` names exactly
  `0x0876E2F4`, so the record array ends there and the rest of the row is not a record.

The null each table beats: a byte-permuted copy holds no record that passes the four entry conditions
(`tools/mapcontainer/test_pairsprite.py`), and every retail record does. What stays raw around them:
the tile blocks they point at (a graphics route, not a decode), the four `{s32 dx, s32 dy}` pairs at `0x7594F0` that the same index reads
(emitted, below), the two pairs after them, and the remaining 8,376 B of the R20 row.

## Reads logged in play

A read of a byte of 280 of these rows, 126,776 B, was logged in play; `docs/research/ENDROM_READS.csv`
holds the pc of each reader with the row it reached, and the census quotes them per row. The biggest
rows with a read, and the instruction the pc holds:

| row | bytes | read pc | quote and what it does |
|---|---|---|---|
| `0x75A7A4..0x75F7AC` | 20,488 | `0x08036BB6` | `4968` `ldr r1,[r1,#4]` on the base `0x0875A7A4`, then `0x08036BBC` `0C68` `ldr r4,[r1]` of the value it loaded and `0x08036BCC` `18C2` `stm r2!,{r3,r4}`: the row's word at `+4` is a value the object subtracts from its own position |
| `0x725749..0x72A690` | 20,295 | `0x08019CAC` | `8B78` `ldrb r3,[r1,#2]` (width), `0x08019CAE` `CC78` `ldrb r4,[r1,#3]` (height), `0x08019CB2` `8968` `ldr r1,[r1,#8]` (source), `0x08019CB4` `6343` `muls r3,r4,r3`, `0x08019CBE` `bl 0x08049138` to `0x06010000`: a width x height copy to VRAM |
| `0x72084C..0x725018` | 18,380 | the same four pcs | the same copy; `0x08019C54` `5268` `ldr r2,[r2,#4]` reads one descriptor word into a hardware attribute word |
| `0x72D6B8..0x7315A8` | 16,112 | `0x08019B58` | `CC56` `ldrsb r4,[r1,r3]` then `0x08019B62` `CD56` `ldrsb r5,[r1,r3]` at `+1`, `0x08019B6A` `8B78` `ldrb r3,[r1,#2]` and `0x08019B6C` `C978` `ldrb r1,[r1,#3]`: a record of `{s8 dx; s8 dy; u8 w; u8 h; ...}`, 12 B, indexed by `r3` |
| `0x7144D8..0x7180E9` | 15,377 | `0x0800BB57` | the 2-bit block select and its `0x100` B VRAM copy |
| `0x754A1C..0x756A04` | 8,168 | `0x08019B58` | the same 12-byte frame record |
| `0x7504CC..0x7520D4` | 7,176 | `0x0802A844` | `0068` `ldr r0,[r0]` on the base, then `0x0802A846` `bl 0x0801124c` with the word as its argument |

So the reads name a consumer for 280 rows and still no record count: the four biggest are graphics the
code copies to VRAM or descriptor words it dereferences, and a copy is an identity, not a decode (D1).
The 849 rows without a read pc keep the null the census states for each.

## The end-of-ROM copies that decode nothing

Three readers copy a span of these regions to VRAM and nothing else: `0x7144D8` (2-bit select, `0x100`
B), `0x72C3B8` (`0x1300` B, pool file `0x024950`) and `0x753008` (`0x400` B). A copy is an identity,
not a layout, so none of them is a route (D1).

## What a read pc is: 157 pcs, eight of them a copy return

The read table and the sweep's offset table name 157 distinct pcs over these rows. Eight are not
loads at all: they are the return address of a `bl` into a VRAM copy body, so their "read" is the
copy's byte pass, not a field. They are `0x0800BB57`, `0x0800BB63`, `0x08011FFF`, `0x08019CC3`,
`0x0802A9C5`, `0x0802CBE7`, `0x0802F4F9` and `0x08036AE9`; each resolves to a `bl 0x08049138` (or
`bl 0x08049120`) whose return follows it by two bytes. The other 149 pcs are `ldr`/`ldrb`/`ldrh`/
`ldrsb` loads of a field, identified at the halfword present at `pc - 1`.

| region | rows | bytes | rows with a read pc | read bytes | rows read by a copy return | copy bytes | rows read by a field load | field bytes | rows with no read pc |
|---|---|---|---|---|---|---|---|---|---|
| `R20` | 13 | 57,568 | 0 | 0 | 0 | 0 | 0 | 0 | 13 |
| `R21` | 32 | 57,472 | 6 | 40,551 | 1 | 956 | 5 | 39,595 | 26 |
| `R23` | 37 | 48,100 | 10 | 27,105 | 3 | 4,068 | 7 | 23,037 | 27 |
| `R24` | 6 | 21,064 | 2 | 16,148 | 0 | 0 | 2 | 16,148 | 4 |
| `R25` | 4 | 10,784 | 2 | 7,592 | 0 | 0 | 2 | 7,592 | 2 |
| `R26` | 7 | 6,680 | 1 | 40 | 0 | 0 | 1 | 40 | 6 |
| `R27` | 5 | 8,404 | 5 | 8,404 | 1 | 32 | 4 | 8,372 | 0 |
| `R28` | 6 | 4,732 | 0 | 0 | 0 | 0 | 0 | 0 | 6 |
| `R29` | 17 | 75,164 | 6 | 20,644 | 0 | 0 | 6 | 20,644 | 11 |
| `R30` | 80 | 17,850 | 12 | 2,152 | 1 | 1,664 | 11 | 488 | 68 |
| `R31` | 922 | 21,136 | 236 | 4,140 | 0 | 0 | 236 | 4,140 | 686 |
| **total** | **1,129** | **328,954** | **280** | **126,776** | **6** | **6,720** | **274** | **120,056** | **849** |

A row can carry both classes: the biggest rows below are read by a copier and by a field load.

## The biggest rows, bytes first: what each reader touches

The offset census is one row per `(raw row, reader pc)`: the byte offset inside the row, the width,
and how many times the game read it. A field reader touches the offsets its record needs; a copier
touches a block's every byte. `F` is a field load, `C` a copy return.

| row | bytes | region | readers, offsets inside the row | what the reader states |
|---|---|---|---|---|
| `0x75A7A4..0x75F7AC` | 20,488 | `R29` | `0x08036AE9` `C` 1,024 offsets; `0x08036BB6` `F` `+4` | a width x height copy, plus one word of the row read as `ldr r1,[r1,#4]` |
| `0x725749..0x72A690` | 20,295 | `R21` | `0x08019C54`/`AC`/`AE`/`B2` `F` 6 offsets; `0x08019CC3` `C` 3,072 | sprite piece: `+2` w, `+3` h, `+8` source, then a `w*h` copy |
| `0x72084C..0x725018` | 18,380 | `R21` | the same four `F` pcs, 2 offsets; the same `C` pc, 128 offsets | the same piece copy, one or two pieces |
| `0x72D6B8..0x7315A8` | 16,112 | `R24` | `0x08019B58`/`62`/`6A`/`6C` `F` 5 offsets each; `0x080248EC` `F` `+4`; `0x08024910` `F` `+8` | 60-byte frame of five 12-byte pieces; fields `+0..+3` box, `+4` attribute, `+8` container |
| `0x7144D8..0x7180E9` | 15,377 | `R23` | `0x0800BB57` `C` 256 offsets; `0x08029178` `F` (cited) | a 2-bit block select and a `0x100`-byte copy |
| `0x754A1C..0x756A04` | 8,168 | `R27` | `0x08019B58`/`62`/`6A`/`6C` `F` 2 offsets; `0x08019C54`/`AC`/`AE`/`B2` `F` 2 | one 12-byte piece and its copy |
| `0x7504CC..0x7520D4` | 7,176 | `R25` | `0x0802A844` `F` `+0`, `0x0802A8D4` `F`, `0x0802A908` `F`, `0x08052638` `F` | `ldr r0,[r0]` on the base, then a call with the word |
| `0x719C60..0x71B050` | 5,104 | `R23` | `0x08019B14` `F` `+0`, `0x08019BF8` `F` `+4` | the object's base word and one more |
| `0x712FDC..0x71370C` | 1,840 | `R23` | 12 `F` pcs, 1 to 4 offsets each | piece fields `+0..+3` then the copy |
| `0x7122F8..0x7129A5` | 1,709 | `R23` | `0x0802A9C5` `C` 428 offsets | copy return only |
| `0x7129A5..0x712FDC` | 1,591 | `R23` | `0x0802A9C5` `C` 397 offsets | copy return only |
| `0x756B74..0x7571F4` | 1,664 | `R30` | `0x08019CC3` `C` 192 offsets | copy return only |

## The 60-byte frame at `0x72D6B8`: five pieces, and the phase is what is bounded

The constructor reads `[obj+0x10]` as the frame index and stores `0x0872D6B8 + 60 * index` at
`[obj+0x18]`:

```
0x08024728  3001  lsls r0,r6,#4
0x0802472A  801B  subs r0,r0,r6
0x0802472E  8000  lsls r0,r0,#2      ; 60 * index
0x08024734  A061  str r0,[r4,#0x18]
```

The update adds the phase, and that addition is bounded: `0x080247E8` `0429` `cmp r1,#4`,
`0x080247EA` `06D9` `bls`, then `0x080247FA` `4B00` `lsls r3,r1,#1` / `0x080247FC` `5918`
`adds r1,r3,r1` / `0x08024800` `8900` `lsls r1,r1,#2` = `12 * phase`, added to `[r4+0x54]` and
stored at `[r4+0x18]` before the `bl 0x08019B4E` that reads it. The reader at `0x08019B4E` consumes
the piece's four box bytes and the two words after them:

```
0x08019B58  CC56  ldrsb r4,[r1,r3]     ; +0, signed
0x08019B62  CD56  ldrsb r5,[r1,r3]     ; +1, signed
0x08019B6A  8B78  ldrb r3,[r1,#2]      ; width
0x08019B6C  C978  ldrb r1,[r1,#3]      ; height
0x080248EC  5268  ldr r2,[r2,#4]       ; the piece's attribute word
0x08024910  9B68  ldr r3,[r3,#8]       ; the container pointer
```

So the record layout is the piece from `docs/research/ENDROM_CELL_MAP.md`'s sibling family: 12 bytes,
`{s8 x; s8 y; u8 w; u8 h; u32 attr; u32 container}`, and a 60-byte frame holds five of them. What
neither instruction states is the frame count: the index is a byte, and the row is
`16,112 = 268 x 60 + 32`, so the row boundary cuts a frame rather than closing the array. The six
offsets the runtime touched in this row are 5 per reader, 18 bytes apart, not 60 (the runtime reached
this row through more than one object class), so the row also holds arrays of another stride. No
count, no emission.

## The offset census and its null

For each `(row, pc)` the census counts the distinct offsets and the reads. If the same reads were
spread uniformly over the row's bytes, the expected distinct offsets is `L * (1 - (1 - 1/L)^n)` for a
row of `L` bytes and `n` reads. A field reader is far below that number; a copier is near its own
block size, not the row.

| row | pc | reads | distinct offsets | expected if uniform | ratio |
|---|---|---|---|---|---|
| `0x72D6B8..0x7315A8` | `0x08019B62` | 3,821 | 5 | 3,401.8 | 680 |
| `0x72D6B8..0x7315A8` | `0x08019B6A` | 3,821 | 5 | 3,401.8 | 680 |
| `0x72D6B8..0x7315A8` | `0x08019B6C` | 3,821 | 5 | 3,401.8 | 680 |
| `0x72D6B8..0x7315A8` | `0x080248EC` | 4,894 | 5 | 4,220.7 | 844 |
| `0x72D6B8..0x7315A8` | `0x08024910` | 4,894 | 5 | 4,220.7 | 844 |
| `0x719C60..0x71B050` | `0x08019BF8` | 6,485 | 1 | 3,671.6 | 3,672 |
| `0x71DAF8..0x71DD38` | `0x0800BAEC` | 169,604 | 1 | 576.0 | 576 |
| `0x71DA98..0x71DAF8` | `0x08019F4E` | 169,604 | 1 | 96.0 | 96 |
| `0x7137D8..0x713AD8` | `0x0800BB63` | 667,008 | 192 | 768.0 | 4.0 |
| `0x7144D8..0x7180E9` | `0x0800BB57` | 444,672 | 256 | 15,377.0 | 60.1 |

The first six lines are the field readers the layout above rests on; the last two are copiers, whose
ratio is the number of times a block was copied and says nothing about a record. Every count is
half-open over the row and comes from the sweep's own offset table (556 logs from 102 warped
maps and the play sitting).

## The facing-pair table at `0x7594F0` is source

`0x7594F0..0x759510` is four records of 8 bytes, `{s32 dx; s32 dy}`:
`(0,1)`, `(0,-1)`, `(-1,0)`, `(1,0)`. The consumer is the sprite-piece object that also selects the
sprite-descriptor table at `0x759620`, with ONE index for both:

```
0x08035670  864A  ldr r2,[pc,#0x218]   ; literal file 0x03588C = 0x08759620
0x08035672  4100  lsls r1,r0,#1
0x08035674  1809  adds r1,r1,r0
0x08035676  C900  lsls r1,r1,#3       ; 24 * index
0x08035678  8918  adds r1,r1,r2
0x0803567A  824A  ldr r2,[pc,#0x208]   ; literal file 0x035884 = 0x087594E8
0x0803567C  C000  lsls r0,r0,#3       ; 8 * index
0x0803567E  0832  adds r2,#8           ; +8 = 0x087594F0
0x08035680  8018  adds r0,r0,r2
0x08035684  0268  ldr r2,[r0]          ; dx
0x08035686  4068  ldr r0,[r0,#4]       ; dy
0x0803568A  2063  str r0,[r4,#0x30]
0x0803568C  E262  str r2,[r4,#0x2c]
```

The index is bounded by the sibling table: its own 4 records end at `0x759680`, the word there is
`0x03001C4C`, and the file `0x051CCC` literal names exactly `0x08759680`. So the 4 records this
family reads are 32 bytes. The four pairs are the four axis unit vectors in the order the facing
byte takes them (`0` down, `1` up, `2` left, `3` right; RAM_MAP section 3). The null: a shuffle of
the eight words puts the four vectors back in this order once in 420.

Emitted by `tools/mapcontainer/endromfacing.py`, family `endrom_facing_pair`, four records, round
trip 4/4. The ten bytes before it (`0x7594EC..0x7594F0`) and the 272 after it (`0x759510..0x759620`,
the last two pairs and the first tile block) stay raw; the tile blocks are the graphics question.

## What still stays raw, region by region

- `R20` 13 rows / 57,568 B: no read pc; the biggest row `0x77110C` is named by six literal loads
  and read at one word, not a record.
- `R21` 26 rows / 16,921 B: no read pc; the two biggest are the piece copies above and a row of
  pieces with no index bound.
- `R23` 27 rows / 20,995 B: no read pc; `0x719C60` and `0x71B1A6` are piece or copy data.
- `R24` 4 rows / 4,916 B: the strided rows of `ENDROM_BOUND_CENSUS.md`, no count.
- `R25` 2 rows / 3,192 B: no read pc.
- `R26` 6 rows / 6,640 B: one 40 B read, four remaining rows in the sprite-descriptor block.
- `R27` 0 rows: every row has a read pc, all of them piece copies.
- `R28` 6 rows / 4,732 B: no read pc; the 12-byte triple array read by `0x0803C2F8` has no count.
- `R29` 11 rows / 54,520 B: no read pc; the biggest is `0x762270` (36-byte stride, no count).
- `R30` 68 rows / 15,698 B: no read pc; tiles and the two pairs after the facing table.
- `R31` 686 rows / 16,996 B: no read pc; the class-record fragments read by the dispatch stubs
  (`0x080188AA` `+0xC`, `0x080188AC` `+0x10`, `0x080188AE` `+0`, and their siblings) sit between
  emitted records and no instruction states a record's own extent.

`docs/research/ENDROM_NULL_CENSUS.md` carries the per-row line, one per row, with the reader and the
null; this section is its region summary.
