# The identified rows no other ticket owns: what was searched, and what the search found

PATH-100-003 read-only pass. STEP 2 landed both runs as labeled raw data: run 1's remaining 42,756 B in `asm/rawlabeled_71c90.s`, run 2's 3,596 B in `asm/rawlabeled_6b7080.s`; both census rows are now `raw-labeled` with 0 B INCBIN. The contract's other list (identified-with-consumer rows outside the event-resource pool) is EMPTY as measured.

| run | census region | status in `INCBIN_CENSUS.md` | bytes now INCBIN | census rows |
|---|---|---|---|---|
| 1 | structured block retail spans `0x071C90..0x0945C0` | `raw-labeled` | 0 / 141,616 | 461 |
| 2 | spritedefs retail tail `0x6B7080..0x6B7E8C` | `raw-labeled` | 0 / 3,596 | 1 |


## The run table

| run | range | bytes | consumer cited, or the search denominator | outcome |
|---|---|---|---|---|
| 1 | structured spans, 461 ranges `0x072974..0x08E2E0` | 43,532 | 2,586 word-aligned sites name a byte (data=2,586, code=0, incbin=0); **0** pc-literal loads name one, over the run's own 114 code rows / 322,386 B / 6,560 decoded loads (that run's snapshot, not today's code map of the first figure in this section); the ranges' own pointer field census is below | partly **promoted** (776 B); 42,756 B **blocked** |
| 1a | the three MapEntry arrays (`entry_pointer_array_18/_1c`, `entry_record_array_20`) | 776 | readers cited: `008BD8 ldrb r0,[r0,#7]` + `008BE0 lsls r1,r5,#3` + `008BE2 ldr r0,[r0,#0x20]` + `008BE8 bl 0xC300`; `008C02 ldrb r0,[r0,#5]` + `008C0A lsls r1,r5,#2` + `008C0E ldr r6,[r0,r1]`; `008C2E ldrb r0,[r0,#6]` + `008C3A ldr r6,[r0,r1]` | **promoted** |
| 2 | spritedefs tail `0x6B7080..0x6B7E8C` | 3,596 | 53 sites name a byte (code=8 literal-pool words, data=45); **18 pc-literal loads** name one, over 6 distinct targets (`0x6B7080`, `0x6B7084`, `0x6B72E0`, `0x6B748C`, `0x6B759C`, `0x6B77A4`), re-measured at the UNATTEMPTED-001 master | **consumer cited; promotion not landed** (see below) |



## What STEP 2 landed, and what it measures

| run | file | symbols | bytes | cited bases | round trip (RED then GREEN) |
|---|---|---|---|---|---|
| 1 | `asm/rawlabeled_71c90.s` | 574 | 42,756 | 132 distinct of 167 naming entries | one-byte perturbation of `0x072974` refused; retail GREEN |
| 2 | `asm/rawlabeled_6b7080.s` | 8 | 3,596 | 8 | one-byte perturbation of `0x6B7080` refused; retail GREEN |
