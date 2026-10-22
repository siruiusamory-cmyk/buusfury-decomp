# The two asset-directory block runs: 143 entries, 733,911 bytes, and no format that beats a copy

Instrument: `tools/mapcontainer/assetdir_samples.py`; per-entry table `docs/research/ASSETDIR_SAMPLES.csv` (LF, sha256 `9505d1c7183acdec7c4de32f71e29d895c24630cdb5b405d16ba8dcbf4f4ff88`; shuffle null seeded 20261018, 5 draws). `tools/mapcontainer/audiodir.py` ties the 64 records directory 1 names and the 79 records directory 2 names to the engine's sample and music tables, and emits both runs from their decoded streams.

    python tools\mapcontainer\assetdir_samples.py --rom baserom.gba --csv docs\research\ASSETDIR_SAMPLES.csv

## 1. The two runs

| directory | table (file) | records | table bytes | block run (file) | block bytes | gap |
|---|---|---|---|---|---|---|
| `asset_directory_64` | `0x3192A8` | 64 | 768 | `0x2B9BB0..0x3192A5` | 390,901 | 3 B |
| `asset_directory_79` | `0x36D18C` | 79 | 948 | `0x3195A8..0x36D18A` | 343,010 | 2 B |
| both | - | 143 | 1,716 | - | **733,911** | 5 B |

## 2. The census: every byte is in an entry, no gap

| low 16 bits | entries | bytes |
|---|---|---|
| `flags=0` | 76 | 381,397 |
| `flags=1` | 62 | 305,031 |
| `flags=3` | 5 | 47,483 |
| high 16 bits | entries | bytes |
|---|---|---|
| `aux=0` | 90 | 429,221 |
| `aux=set` (1..7,431) | 53 | 304,690 |

## 3. The family table

| family | entries | bytes | format hypothesis | in-tree codec | consumer | route |
|---|---|---|---|---|---|---|
| the two 12-byte directories | 143 | 1,716 | `{u32 data_ptr, u32 flags, u16 byte_length, u16 unit}`, exact tiling (PROVEN) | `assetdirectory` parse + pack; carried through the record store | dir 1's records reach the channel allocator `0x0803E378` from `0x0800082A`; dir 2 none | **source already** (not in `identity_ranges()`) |
| the two block runs | 143 | 733,911 | 8-bit signed sample stream, silence `0x00`, read at `unit` (SUPPORTED); no in-tree container tag at an entry's start and no fixed-stride frame at strides 2/4/8/16/32 (SUPPORTED, not PROVEN - section 4) | `assetdirectory.block_blob` decodes each stream and re-encodes it (section 5) | dir 1's blocks: the channel allocator `0x0803E378` from `0x0800082A`; dir 2's: a music record's `+8` read at `0x0803E542` (section 7) | **both runs (733,911 B) are source** through the audio decode route |
| the two alignment gaps | 2 | 5 | none, alignment between a run and its table | none | - | stays retail (outside both families) |

## 4. What the payload is: the format evidence

| test | measurement | what it weighs against |
|---|---|---|
| four in-tree container tags at every entry's start (webfoot kind 0/1/2 with a declared size, `JCAL`, BIOS LZ77 `0x10`, BIOS RLE `0x30`) | 0 of 143 for each | a packed or stored container that names itself with one of these four tags at the entry's start (the tree's own test, `webfoot_lz` + `assetdir3.packed_container`) |
| fixed-stride framing: columns fixed to one value in >95 % of their bytes, strides 2/4/8/16/32 | 0 constrained columns at every stride | a per-sample or per-frame header at one of those five strides, a framed ADPCM block whose fields sit on them, a strobed record |
| 16-bit samples | 45 of 143 entries have an **odd** length | a uniform 16-bit sample reading of the whole payload; the 98 even-length entries are not excluded by this test |
| lag-1 correlation on the signed reading, against each entry's own within-block shuffle null (5 draws, seed 20261018) | mean real **0.600**, mean null **0.000**; 140 of 143 lie more than 0.05 from their own null (122 above it, 18 below) | a table, code or compressed stream: none of those has this much temporal coherence, and a shuffle destroys it - a statistical reading, not an exclusion |
| byte histogram and constant runs | mode `0x00` at 7.55 % of the bytes, signed asymmetry 2.05 %, 1,068 runs of ≥8 B (24,999 B) with 79.07 % of the run bytes at `0x00` | an unsigned reading centred on `0x80` (its share is 0.33 %); silence is `0x00`, i.e. **signed** 8-bit |
| per-entry byte spread | 28..256 distinct values, entropy 3.908..7.902 bits | a constant block, a pointer table, a text run |




## 5. The engine's fields

Directory 1's table is `0x083192A8`, loaded at `0x0800082A` (`ldr r1, [pc, #0xc4]`, pool
`0x080008F0 = 0x083192A8`). The index becomes a record address in four instructions
(`lsls r3, r0, #1` / `adds r0, r3, r0` / `lsls r0, r0, #2` / `adds r1, r0, r1`, so `12 * index`),
and `bl 0x0803E378` stores it into a free channel slot (`str r1, [r0, #0x28]`). The mixer reads the
record through that slot (`r2 = [slot+0x28]`) at `0x0803E0FC..0x0803E112`:

| record field | offset | width | instruction | site | stored as |
|---|---|---|---|---|---|
| `data_ptr` | +0 | u32 | `ldr r3, [r2]` | `0x0803E0FC` | slot+8, the sample address |
| `flags` low byte | +4 | u8 | `ldrb r2, [r2, #4]` | `0x0803E110` | slot+0x11, the sample's flag byte; bits 0-2 select the loop paths |
| `flags` high half | +6 | u16 | `ldrh r3, [r2, #6]` | `0x0803E100` | slot+0x20, `<< 14` |
| `byte_length` | +8 | u16 | `ldrh r3, [r2, #8]` | `0x0803E106` | slot+0x24, `<< 14`, the end position |
| `unit` | +10 | u16 | `ldrh r3, [r2, #0xa]` | `0x0803E10C` | slot+0x14, the rate term |

`unit` becomes the mixer's Q14 step at `0x0803E128..0x0803E13A`: `unit * 0x4000`, `>> 14`, `* 0x1063`,
`+ 0x7FF`, `>> 12`, i.e. a step of `unit / 16000` at `0x4000`, so `unit` reads as the sample rate in
Hz against a 16 kHz mixer (SUPPORTED: the arithmetic is read, the 16 kHz reference is the constant's
value, no capture). Byte +5 of the record is the only byte no instruction reads; it is `0x00` in all
64 records.

## 6. The tie: which run the engine reads

| directory | records | bytes | reached by | verdict |
|---|---|---|---|---|
| `asset_directory_64` | 64 | 390,901 | 49 literal sites name `0x083192A8` and call `0x0803E378` within the next 36 B (`0x0800082A` first) | **tied** |
| `asset_directory_79` | 79 | 343,010 | a music record's `+8` at `0x0803E542`, indexed by `12 * byte` and stored at `slot+0x28` (section 7) | **tied** |

The music table is reached at four sites, each `ldr r2, [pc, #n]` = `0x083BB78C` followed by
`bl 0x0803F110`: `0x080008BC`, `0x080041BA`, `0x080053F8`, `0x08008C86` (calls at `0x080008D2`,
`0x080041CE`, `0x0800540E`, `0x08008C9A`). `0x0803F110` stores the record at state+0xC; the sequencer
reads `+0` (entry array), `+4` (ramp) and `+12` (block) at `0x0803EF00`, `0x0803EF0E`, `0x0803EF76`.
`0x0836D18C` has 0 literal sites; its only holders are the 53 music records' `+8`.

## 7. The music record's `+8`: the sample bank a note triggers

The slot engine's note handler (`0x0803E4E4`, one of the 32 Thumb pointers at `0x087B6904`, most of
them `0x0803E4E5`, dispatched every tick by `0x0803EE84`) selects a sample from the current song's
bank:

| site | instruction | reads |
|---|---|---|
| `0x0803E536` | `ldr r3, [pc, #0x270]` (pool `0x0803E7A8` = `0x087B6724`) | the music-object table |
| `0x0803E53A` | `subs r3, #4` | `0x087B6720` |
| `0x0803E53C` | `ldr r3, [r3]` | `0x030038A4`, the object the four attach sites fill |
| `0x0803E540` | `ldr r3, [r3, #0xc]` | the current music record (`0x0803F11C` wrote it) |
| `0x0803E542` | `ldr r5, [r3, #8]` | `0x0836D18C`, the 79-record table |
| `0x0803E544` | `lsls r3, r2, #1` / `adds r2, r3, r2` / `lsls r2, r2, #2` | `12 * byte` (the byte is `sub+0xb` at `0x0803E538`) |
| `0x0803E54A` | `adds r2, r5, r2` | the table's record |
| `0x0803E54C` | `str r2, [r0, #0x28]` | the channel slot |

The mixer prepare then reads that slot: `0x0803E0FA ldr r2, [r0, #0x28]`, then `+0` (`0x0803E0FC`),
`+6` (`0x0803E100`), `+8` (`0x0803E106`), `+0xa` (`0x0803E10C`) and `+4` (`0x0803E110`), which is the
same 12-byte record layout section 5 gives. So directory 2's 948 B table is read through a music
record's `+8`, and the 343,010 B its records name reaches the mixer as the sample address.

## 8. What each figure rests on

| figure | evidence class | rests on |
|---|---|---|
| 143 entries, 733,911 B, exact tiling, 5 B of gaps | PROVEN | each instance's `assert_contract`, asserted by the census before it counts |
| the kind partitions (76/62/5 and 90/53) | PROVEN | the records' own `flags` words, read at the table |
| no in-tree container tag / no fixed stride / 45 odd lengths | SUPPORTED | four tags and five strides at an entry's start, over the retail bytes; a tagless container, a variable-length table and a headerless framed codec pass every structural test |
| 8-bit signed sample stream | SUPPORTED | lag-1 coherence against a per-entry shuffle null, the zero-centred histogram, the signed-silence runs; `unit` is the rate term the mixer scales to its step (`0x0803E128..0x0803E13A`) |
| `data_ptr`, `byte_length`, `unit`, the record's flag byte | SUPPORTED | each is read by the mixer at `0x0803E0FC..0x0803E112` and stored in the channel slot (section 5) |
| the `flags` high half (`+6`) | NOT ESTABLISHED | read as a position (`<< 14`, slot+0x20); the loop-start reading is refuted (section 4) |
| the payload's decoded reader | PROVEN | `0x0803E184 ldr r3, [r4, #0x18]` then `0x0803E186 bl 0x08046AA6` (`bx r3`) calls the slot's mixing routine; for an active slot it is IWRAM `0x03000868`, the ARM bytes copied at boot from file `0x7B820C` (`asm/crt0.s` DMA3 `0x087B79A4 -> 0x03000000`, 4,100 B), whose `ldm r0, {r3, r4, r5, r6}` reads slot+0..+0xc and mixes `ldrsb` samples from the address in slot+8 |
| 733,911 B source | PROVEN under the route | `audiodir.py`'s two tie channels (sections 6 and 7), `assetdirectory.block_blob` for both runs, and `gate.identity_ranges()` declaring neither |
