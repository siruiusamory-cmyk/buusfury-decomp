# CODE-BAND-006: the six pointer-named rows, their readers, and the one thing a reader proves

Starting set: 6 rows / 20,854 B named by CODE-BAND-005's pointer channel. Result: 4 B converted (one Thumb leaf passed as an argument, byte-exact); the other five have readers that bound no row, so they stay.

## D1. Consumer trace, all six rows

| row | bytes | naming word | holding row | route | reader site | instructions | what the reader does with the word |
|---|---|---|---|---|---|---|---|
| `0x036E76..0x036E7A` | 4 | `0x08036E77` (bit 0 SET) | `0x75F7F4..0x75F808` | P | `0x08036D86` | `ldr r5,[pc,#0xcc]` (0x08036D86); `ldr r0,[r5]` (0x08036D8A); `bl 0x080210B6` (0x08036D8C); `ldr r0,[r5,#4]` (0x08036D90) | passed as `r0` to 0x080210B6, then the table's next word is read |
| `0x04A24A..0x04A59C` | 850 | `0x0804A368` | `0x1CB7C..0x1CB86` | A | `0x0801C928` (sub_0801C91C) | `ldr r0,[pc,#0x250]` (0x0801C928); `str r0,[r4]` (0x0801C92C); fields `+0x18 +0x20 +0x24 +0x40 +0x44 +0x48` set after | stored into object field 0; no load of field 0 in the window |
| `0x04AAF2..0x04BA78` | 3,974 | `0x0804B2DC` | `0x627C..0x6288` | A | `0x080060DA` (sub_080060C6) | `ldr r0,[pc,#0x1a0]` (0x080060DA); `str r0,[r4]` (0x080060DE); `ldr r1,[pc,#0x1a0]` (0x080060DC); `lsls r0,r0,#2` (0x080060E4); `ldr r0,[r1,r0]` (0x080060E6); `str r0,[r4,#0x1c]` (0x080060E8) | object field 0 = the word; field `+0x1C` = the second table's `index*4` word |
| `0x06D4E0..0x06FE18` | 10,552 | `0x0806E050` | `0x6B8078..0x6B8080` | P | `0x08016016` | `ldr r0,[pc,#0x1ec]` (0x08016016); `ldr r0,[r0,#4]` (0x0801601A); `bl 0x0803FFE8` (0x0801601C); `str r0,[r4,#8]` (0x08016020) | the word is the argument to 0x0803FFE8, whose RETURN is stored at `[r4,#8]` |
| `0x07012C..0x070130` | 4 | `0x0807012C` | none (no citation row holds 0x6B8024) | - | none | - | no reader anywhere in the tree |
| `0x0701FA..0x071758` | 5,470 | `0x080716A0` | `0x9018..0x9022` | A | `0x08008D80` (loc_08008D44) | `ldr r7,[pc,#0x294]` (0x08008D80); `ldr r0,[r7,#8]` (0x08008D86); `movs r3,#0x68` (0x08008D88); `ldrb r1,[r0]` (0x08008D8A); `muls r1,r3,r1` (0x08008D8C); `adds r0,r1,r0` (0x08008D8E); `adds r0,r0,#0x4f8` (0x08008D90-0x08008D94); `ldrb r0,[r0,#0x14]` (0x08008D96); `lsls r3,r0,#1` / `adds r0,r3,r0` / `lsls r0,r0,#3` (x24) | row `+8` is the base of a 0x68-byte record array; each record's byte at `+0x14` (behind a `+0x4F8` bias) indexes a 24-byte table |


## D3. Nulls, per family

| row | words | real | permuted |
|---|---|---|---|
| `0x04A24A` | 212 | 0 | 0 |
| `0x04AAF2` | 993 | 2 | 3 |
| `0x06D4E0` | 2,638 | 166 | 127 |
| `0x07012C` | 1 | 1 | 1 |
| `0x0701FA` | 1,367 | 1 | 4 |

## D4. Conversion

| doc | sha256 |
|---|---|
| `docs/research/THUMB_BODIES.csv` | `696ee3879ea1bca37936d48010a9ae5f991abda711000ed400a45672668549d5` |
| `docs/research/RAW_CITATIONS.csv` | `6ac305ece81ddf53dac642326be34388703499d1736ee938cd5d6607b6db1674` |
| `docs/research/INCBIN_CENSUS.md` | `7186c888ec690ed33662ca573bb5ae605ffc949c82f9f0e977d03d07cb3d0dc8` |
| `docs/research/RESIDUAL_LEDGER.csv` | `86c37e0b4368497a9547e0da11982e3e9e082b5d7d2ddd2cc184ef67910943a4` |
| `docs/research/RESIDUAL_LEDGER.md` | `6768e20a8ffdd417327c18d7fce269b7a4e4234c4e4dd29960a1204852fef95b` |
| `docs/research/RAW_REMAINDER.csv` | `63dae32df28e416e34ad9754d1d331f872b35be525505bfc371b1096e46fb220` |
| `docs/research/ROUTE_TO_100.md` | `173c7513fc543e63dee2e99d7e5bfb7748263fd6ff5898aab0cf9bba91f8b33d` |
