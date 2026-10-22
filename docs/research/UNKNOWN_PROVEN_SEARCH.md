# The widened search for the census's `unknown-proven` rows

PATH-100-002. Population: 339,704 B in 1,028 rows from two regions. The widened search measured channels the recorded denominator did not cover; run 1 was later promoted as labeled raw data (STEP 3), the three largest rows were not promoted because no parse follows.

| region | bytes now INCBIN |
|---|---|
| `recon slice A lower half 0x74F080..0x77C5A4` | 183,856 |
| `recon slice B residue 0x6FC238..0x7315E8` | 155,848 |

## The recorded denominator, and what it does not cover

| channel | what it measures |
|---|---|
| `loaders` | every Thumb-1 `ldr Rd,[pc,#imm8]` position whose literal holds an address inside the range, with the loaders-per-literal cluster and its distribution |
| `indirect` | every literal that names a TABLE elsewhere in the image whose own words name the range (a pointer table reached indirectly) |
| `direct` | every word whose value names the range, split into words inside the range and words outside it |
| `shape` | the range's word classes (zero / small / ROM pointer / odd code pointer / IWRAM pointer) |
| `null` | the same `loaders` measurement over 12 same-size control windows, so a hit count is never read on its own |


## The runs, largest first

| run | range | bytes | channel result | outcome |
|---|---|---|---|---|
| 1 | `0x75A738..0x76CCD4` | 75,164 | `loaders`: 79 loaders, 35 literals, 17 multi-literal, largest cluster 9; `indirect`: 12 tables name it; `direct`: 167 inside / 54 outside; `null`: 12 controls at [5, 37, 10, 39, 253, 33, 43, 347, 2, 49, 4, 20] loaders | consumer cited, **not promotable** (see below) |
| 2 | `0x76CCE4..0x77AE68` | 57,732 | `loaders`: 40 loaders, 22 literals, 7 multi, largest 8; `indirect`: 6 tables; `direct`: 111 inside / 50 outside; `null`: [4, 32, 6, 16, 74, 34, 29, 14, 1, 18, 3, 9] | consumer cited, **not promotable** |
| 3 | `0x71E274..0x72C378` | 57,604 | `loaders`: 182 loaders, 61 literals, 36 multi, largest 11; `indirect`: 25 tables; `direct`: 334 inside / 93 outside; `null`: [4, 32, 6, 16, 74, 34, 29, 14, 1, 19, 3, 9] | consumer cited, **not promotable** |


## STEP 2 (PATH-100-002 amendment): what run 1's loaders actually do

| loader site (ROM) | literal loaded | what the code does with it | stride / count | extent from code |
|---|---|---|---|---|
| `080363C4` | `0x036438` = `0x0875A738` | `ldr r1,[r1]`, `ldrh r1,[r1,#4]` - the word is a pointer to a global object | none | none |
| `0803645A 080364A6 080364E2 08036510 080365C2 080365D6 0803666E 08036682 080366A0` | `0x03670C` = `0x0875A73C` | `ldr r0,[r5,#4]`, `ldr r1,[r5,#8]` - two IWRAM pointers out of a global table; `08036B9E` compares an object field against `base + 0x18` | none | none (12 B in use) |
| `0803698C 080369D4` | `0x036A10` = `0x0875A7A0` | `ldr r0,[r4]` = IWRAM pointer, passed to `0x08011C70` | none | none |
| `08036A62 08036BB2 08036C8E` | `0x036D6C` = `0x0875A7A4` | `ldr r0,[r5]` = IWRAM pointer | none | none |
| `08036A8C 08036ACC 08036B9E 08036C62 08036D1C` | `0x036D74` = `0x0875F7AC` | K-089 piece record: `ldrsb [r0,#0]` / `ldrsb [r0,#1]` = box x,y, `ldrb [r0,#2]` / `ldrb [r0,#3]` = w,h, `ldr [.,#8]` = container pointer | pointer advanced by `adds r0,#0xc`; live offsets `0x18 <= off < 0x3C` | **60 B lower bound only** (0x18..0x30 used, no end) |
| `08036D86 08036DD8 08036DF4 08036E2C` | `0x036E54` = `0x0875F7F4` | `ldr r0,[r5]` passed to `0x080210B6`; `ldr r0,[r5,#4]` used as a destination base (`+0x80`, `[+0x10]`, `stm r0!,{r1,r2}`) | none | none |
| `08036FC2 08036FFE 080370B6 080370D2 08037124 080371E0 08037274 080372D6 080372E4 080372EE 080373CA` | `0x037238` / `0x037478` = `0x0875F808` | `ldr r0,[r6,#4]` = IWRAM pointer, passed to a memory routine | none | none |
| `08037084` | `0x037244` = `0x0876174C` | `record = base + 12*N` (`lsls #1`, `adds r0,r3,r0`, `lsls #2`); `record[0]` is a base and the code then indexes `base + 24*M` | 12, then 24 | none (unbounded index) |
| `080374F0 0803751C 08037576 080375AE 0803761E 08037662 0803770A 080377E8 080378A6 0803793E` | `0x037880` / `0x0379BC` = `0x0876ACF0` | `ldr r0,[r0]` = IWRAM pointer, then `+0x5C4` and `bl 0x0803E378` (the asset-directory loader) | none | none |
| `08037A88` | `0x037B40` = `0x0876BA40` | `entry = base + 8*N` (`lsls r0,r0,#3`, `adds r0,r0,r1`), then `ldm r0!,{r5,r6}` | 8 | none (unbounded index) |
| `0801A7EC` | `0x01A8EC` = `0x0876ACC0` | `entry = base + 16*N` (`lsls r0,r0,#4`) | 16 | none |
| `0801B2F6` | `0x01B4DC` = `0x08762270` | `entry = base + 36*N` (`lsls r3,r0,#3`, `adds r0,r3,r0`, `lsls r0,r0,#2`), stored at `obj+8` | 36 | none |
| `0801A698` | `0x01A8E4` = `0x0876BA2C` | the address is stored to `[sp]` and passed as an argument | none | none |
| `08037C60 08037CA8` | `0x037D44` = `0x0876CBD8` | `base + 0x3C` when a state value is 3, else the base alone, stored at `obj+0x44` and `obj+0x18` | none | 0x3C in use |
| `08037C74` | `0x037D48` = `0x0876BA78` | fields `+8`, `+0xC`, `+0x10`, `+0x14` read into stack slots | none | 0x18 in use |
| `08037D8E` | `0x037E98` = `0x0876CCB0` | `ldr r0,[r5]` passed to `0x080116FC` | none | none |
| `080516E2 08051E3A 08051A1E` | `0x0875A7A4`, `0x0875A73C`, `0x0876BA78` | same globals as above, from the `0x049120..0x055620` slice | none | none |



## PATH-100-002 STEP 3: run 1 as labeled raw data (R-RAW-001)

| range | bytes | symbols | rule | source | census |
|---|---|---|---|---|---|
| `0x75A738..0x76CCD4` (run 1) | 75,164 | 17 | R-RAW-001 | `asm/rawlabeled_75a738.s` | `raw-labeled`, 0 B of the range INCBIN |
