# RUNTIME-READ-PLAN-001: one read session, as a frozen, checkable plan

Frozen plan: 194 rows / 141,342 B in five groups, all with a static negative. Nothing was run at plan time. P5 records the runtime route: the runtime read survey logged five headless sessions and cited 42 of the 194 rows.

## P1. The target list (MEASURED)

| group | rows | bytes | static negative | question the read answers |
|---|---|---|---|---|
| `set_a` | 38 | 58,404 | K-217 | does any instruction read these bytes while a map is live, and at what width? |
| `set_b` | 62 | 31,808 | K-218 | does any instruction read this child-list payload, and at what offset from its start? |
| `runtime_pending` | 89 | 30,280 | T-197 | which instruction reads this row, and is the access a read or a write? |
| `pointer_0x68` | 1 | 5,470 | K-220 | what bounds the 0x68-byte record array whose base sits at 0x080716A8? |
| `pointer_other` | 4 | 15,380 | K-220 | which field of the named object is dereferenced, and with what stride? |
| **total** | **194** | **141,342** | | |

## P2. What the session watches, and what a hit must carry

| group | watch ranges (bus addresses) | RAM / structure fields to log | one run or many |
|---|---|---|---|
| `set_a` | its 38 rows, `0x08000000 + start` | the map root's `+0x0C` (count) and `+0x10` (word array) - K-218's pair | many: the launcher takes ONE `-Watchpoint` per run |
| `set_b` | its 62 rows | same root pair; log `address - row_start` as the offset | many |
| `runtime_pending` | its 89 rows | none; the value's width is the question | many |
| `pointer_0x68` | `0x080716A8` (the `+8` word), then `0x080716A0..0x08071758` | the word read at `0x080716A8`, then a byte read at that base (the count) | two runs |
| `pointer_other` | the 4 row starts + the object fields: `[r4,#0x1c]` written at `0x080060E8`, field 0 written at `0x0801C92C`, `[r4,#8]` written at `0x08016020` | the object base register's value at the store (so the field is identifiable later) | two runs |


## P4. The unmapped remainder on the CODE-BAND-006 master (MEASURED)

| region | rows | bytes | | attempts | rows | bytes |
|---|---|---|---|---|---|---|
| R32 | 1,069 | 51,046 | | `CODE-BAND-004:unreached` | 1,173 | 35,506 |
| R19 | 574 | 42,756 | | `CODE-BAND-003:unreached` | 574 | 42,756 |
| R00 | 161 | 4,023 | | none | 139 | 58,359 |
| R35 | 31 | 17,317 | | `CODE-BAND-004:source-entry` | 17 | 31 |
| R09 | 26 | 7,744 | | `CODE-BAND-004:pool-data` | 16 | 18,478 |
| R10 | 22 | 7,696 | | `PTR-TABLE-001:unnamed-word;PTR-WORDS-002:no-family` | 16 | 248 |
| R18 | 8 | 3,596 | | `GRAPHICS-RESIDUAL-002:null` | 5 | 2,176 |
| R34 | 5 | 4,616 | | `CODE-ENTRY-001:9-row-boundary-fragments` | 1 | 128 |
| R22 | 3 | 6,040 | | | | |
| R07 | 2 | 5,376 | | | | |
| R02 | 1 | 3,960 | | | | |
| R33 | 39 | 3,512 | | | | |
| **total** | **1,941** | **157,682** | | **total** | **1,941** | **157,682** |
| start..end | bytes | region | attempts |
|---|---|---|---|
| `0x04BA82..0x04E488` | 10,758 | R32 | `CODE-BAND-004:pool-data` |
| `0x06D4E0..0x06FE18` | 10,552 | R32 | `CODE-BAND-004:unreached` (K-220 row 4) |
| `0x0701FA..0x071758` | 5,470 | R32 | `CODE-BAND-004:unreached` (K-220 row 6, `pointer_0x68`) |
| `0x3BD2F8..0x3BE3D4` | 4,316 | R07 | none |
| `0x04AAF2..0x04BA78` | 3,974 | R32 | `CODE-BAND-004:unreached` (K-220 row 3) |
| `0x2B8C38..0x2B9BB0` | 3,960 | R02 | none |
| `0x74D380..0x74E200` | 3,712 | R10 | none |
| `0x6FCCC8..0x6FD9D0` | 3,336 | R22 | none |




### P5.2 The build stop: what is missing and where the README expects it (MEASURED)

| README requires | measured | evidence |
|---|---|---|
| CMake | present, but it is the **MSYS** build (4.0.2): it lists only `Unix Makefiles`/`Ninja` and refuses `NMake Makefiles`, so the installed Visual Studio 2022 BuildTools (`cl.exe` 14.44.35207) cannot be driven by it | `-G "NMake Makefiles"` -> `CMake Error: Could not create named generator NMake Makefiles` |
| Ninja | **missing**: absent from PATH, from the MinGW64 prefix and from the VS BuildTools tree | `Get-Command ninja` -> not found; `Test-Path` false at each location |
| MSYS2 MinGW64 | **missing**: the prefix exists and its `bin` holds `0` entries; `pacman -Q` lists `cmake` and the devkit cmake wrappers but no `mingw-w64-*` package, and the pacman cache carries no gcc package to install from | the MinGW64 prefix's `bin` lists `0` entries |
| SDL2 | **missing**: no SDL2 development library; the only `SDL2.dll` files on disk sit inside unrelated application installs | `find_package(SDL2 REQUIRED)` is reached when the launcher UI is on |


### P5.4 What the prover makes of the entries (MEASURED)

| row | bytes | runtime entry or entries | verdict |
|---|---|---|---|
| `0x003fee..0x003ff8` | 10 | `0x08003fee` | leaves |
| `0x004156..0x004212` | 188 | `0x0800419c` | leaves |
| `0x005ad4..0x005bc0` | 236 | `0x08005ae4` | leaves |
| `0x005c6e..0x005e36` | 456 | `0x08005c6e`, `0x08005cba`, `0x08005d0a`, `0x08005d5a` | leaves x4 |
| `0x006094..0x006098` | 4 | `0x08006096` | leaves |
| `0x00770c..0x007710` | 4 | `0x0800770c` | returns |
| `0x0077de..0x0077e2` | 4 | `0x080077de` | returns |
| `0x00a26e..0x00a272` | 4 | `0x0800a26e` | returns |
| `0x0175a0..0x0175c8` | 40 | `0x080175a0` | leaves |
| `0x03e848..0x03e89a` | 82 | `0x0803e848`, `0x0803e85a`, `0x0803e884` | leaves x3 |
| `0x03eb68..0x03eb6c` | 4 | `0x0803eb68`, `0x0803eb6a` | returns x2 |
| `0x03eb96..0x03eb98` | 2 | `0x0803eb96` | returns |
| `0x03ebf4..0x03ebf8` | 4 | `0x0803ebf4`, `0x0803ebf6` | returns x2 |
| `0x03eca2..0x03eca6` | 4 | `0x0803eca2`, `0x0803eca4` | returns x2 |
| `0x03ecc2..0x03ecc6` | 4 | `0x0803ecc2`, `0x0803ecc4` | returns x2 |
| `0x048eca..0x048f54` | 138 | `0x08048ed8` | leaves |
| `0x049010..0x049114` | 260 | `0x080490f8` | no-code |
| `0x04aaf2..0x04ba78` | 3,974 | `0x0804b8dc`, `0x0804b8f0`, `0x0804b904` | stops x3 |





### P5.9 The runs: five headless sessions, one of them a live map (RUNTIME-PROVEN)

| run | input track | frames | hit lines | live map |
|---|---|---|---|---|
| 1 | none (attract) | 1,800 | 16,174 | no |
| 2 | `campaign` | 6,000 | 3,145,560 | **yes** |
| 3 | `walk` | 6,000 | 3,093,226 | yes |
| 4 | `campaign-safe` | 12,000 | 4,125,304 | yes |
| 5 | `campaign-traverse` | 12,000 | 4,125,304 | yes |

### P5.10 The citations: 42 of the 194 rows, and 6 of them were not yet carried (RUNTIME-PROVEN)

| group | target rows | target bytes | rows cited | citations | distinct readers |
|---|---|---|---|---|---|
| `pointer_0x68` | 1 | 5,470 | 1 | 60 | 60 |
| `pointer_other` | 4 | 15,380 | 4 | 112 | 89 |
| `runtime_pending` | 89 | 30,280 | 35 | 117 | 20 |
| `set_a` | 38 | 58,404 | 2 | 12 | 12 |
| `set_b` | 62 | 31,808 | 0 | 0 | 0 |
| **total** | **194** | **141,342** | **42** | **301** | **180** |

### P5.11 What was promoted, and the gate (MEASURED)

| row | bytes | symbols | citations | owner file |
|---|---|---|---|---|
| `0x04A24A..0x04A59C` | 850 | 29 | 28 | `asm/slice_049120.s` |
| `0x04AAF2..0x04BA78` | 3,974 | 47 | 46 | `asm/slice_049120.s` |
| `0x06D4E0..0x06FE18` | 10,552 | 14 | 13 | `asm/slice_06d4e0.s` |
| `0x07012C..0x070130` | 4 | 1 | 1 | `asm/slice_06d4e0.s` |
| `0x0701FA..0x071758` | 5,470 | 35 | 35 | `asm/slice_06d4e0.s` |
| `0x2B60A8..0x2B7E78` | 7,632 | 8 | 7 | `asm/rest_of_the_game.s` |
| **total** | **28,482** | **134** | **130** | |
