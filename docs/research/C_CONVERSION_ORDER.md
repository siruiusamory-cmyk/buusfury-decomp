# The C conversion order

Ranking rule for the 94 ledger code rows: named rows first (a name that is not a bare `code_<hex>` placeholder), then largest first; the two GBARam rows are named but already converted. `span` is file offset..offset+size, `isa` its column, `bytes` the ledger's transcribed-byte column, `src` the assembled source.

Sections 5-11 were dated per-run logs; their tables are kept and their prose is cut.


## 2. The ranking rule

| rank | span (file) | size | isa | name | src | evidence | status |
|---:|---|---:|---|---|---|---|---|
| 1 | `0x7B79A4..0x7B89A8` | 4100 | arm | `codec_blob` | asm/rest_of_the_game.s | byte-proven | asm |
| 2 | `0x02E1C0..0x02F1C0` | 4096 | thumb | `code_reachable_02E1C0` | asm/buu.s | byte-proven | asm |
| 3 | `0x03D63C..0x03D730` | 244 | thumb | `GBARam_Free` | asm/GBARam.s | byte-proven | C, parked |
| 4 | `0x03D5B8..0x03D63C` | 132 | thumb | `GBARam_Malloc` | asm/GBARam.s | byte-proven | C, parked |
| 5 | `0x03D740..0x03D784` | 68 | thumb | `GBARam_UnusedFunctionsAndTheirVariables` | asm/buu.s | byte-proven | C, parked |
| 6 | `0x000158..0x0143F2` | 82586 | thumb | `code_158_143F2` | asm/buu.s | byte-proven | asm |
| 7 | `0x01C3F2..0x02AB4C` | 59226 | thumb | `code_1C3F2_2AB4C` | asm/buu.s | byte-proven | asm |
| 8 | `0x0494D8..0x053014` | 39740 | thumb | `code_494D8_53014` | asm/buu.s | byte-proven | asm |
| 9 | `0x0351C0..0x03D4D0` | 33552 | thumb | `code_351C0_3D4D0` | asm/buu.s | byte-proven | asm |
| 10 | `0x03D784..0x041118` | 14740 | thumb | `code_3D784_41118` | asm/buu.s | byte-proven | asm |
| 11 | `0x043118..0x046118` | 12288 | thumb | `code_043118` | asm/buu.s | byte-proven | asm |
| 12 | `0x01A3F2..0x01C3F2` | 8192 | thumb | `code_01A3F2` | asm/buu.s | byte-proven | asm |
| 13 | `0x0311C0..0x0331C0` | 8192 | thumb | `code_0311C0` | asm/buu.s | byte-proven | asm |
| 14 | `0x02BB4C..0x02D1C0` | 5748 | thumb | `code_2BB4C_2D1C0` | asm/buu.s | byte-proven | asm |
| 15 | `0x048054..0x049114` | 4288 | thumb | `code_48054_49114` | asm/buu.s | byte-proven | asm |
| 16 | `0x0143F2..0x0153F2` | 4096 | thumb | `code_0143F2` | asm/buu.s | byte-proven | asm |
| 17 | `0x02AB4C..0x02BB4C` | 4096 | thumb | `code_02AB4C` | asm/buu.s | byte-proven | asm |
| 18 | `0x02D1C0..0x02E1C0` | 4096 | thumb | `code_02D1C0` | asm/buu.s | byte-proven | asm |
| 19 | `0x02F1C0..0x0301C0` | 4096 | thumb | `code_02F1C0` | asm/buu.s | byte-proven | asm |
| 20 | `0x0301C0..0x0311C0` | 4096 | thumb | `code_301C0_311C0` | asm/buu.s | byte-proven | asm |
| 21 | `0x0331C0..0x0341C0` | 4096 | thumb | `code_331C0_341C0` | asm/buu.s | byte-proven | asm |
| 22 | `0x0341C0..0x0351C0` | 4096 | thumb | `code_0341C0` | asm/buu.s | byte-proven | asm |
| 23 | `0x041118..0x042118` | 4096 | thumb | `code_041118` | asm/buu.s | byte-proven | asm |
| 24 | `0x3715C0..0x3725C0` | 4096 | thumb | `code_3715C0` | asm/rest_of_the_game.s | byte-proven | asm |
| 25 | `0x042188..0x043118` | 3984 | thumb | `code_42188_43118` | asm/buu.s | byte-proven | asm |
| 26 | `0x046118..0x046B1C` | 2564 | thumb | `code_46118_46B1C` | asm/buu.s | byte-proven | asm |
| 27 | `0x046FF4..0x0476AC` | 1720 | thumb | `code_46FF4_476AC` | asm/buu.s | byte-proven | asm |
| 28 | `0x04776C..0x047A2C` | 704 | thumb | `code_4776C_47A2C` | asm/buu.s | byte-proven | asm |
| 29 | `0x053334..0x0534A8` | 372 | thumb | `code_53334_534A8` | asm/buu.s | byte-proven | asm |
| 30 | `0x0531A4..0x0532EC` | 328 | thumb | `code_531A4_532EC` | asm/buu.s | byte-proven | asm |
| 31 | `0x053F58..0x053FFC` | 164 | thumb | `code_53F58_53FFC` | asm/buu.s | byte-proven | asm |
| 32 | `0x054C68..0x054D04` | 156 | thumb | `code_54C68_54D04` | asm/buu.s | byte-proven | asm |
| 33 | `0x054710..0x054780` | 112 | thumb | `code_54710_54780` | asm/buu.s | byte-proven | asm |
| 34 | `0x047F5C..0x047FB4` | 88 | thumb | `code_47F5C_47FB4` | asm/buu.s | byte-proven | asm |
| 35 | `0x047FF4..0x04803C` | 72 | thumb | `code_47FF4_4803C` | asm/buu.s | byte-proven | asm |
| 36 | `0x0539D8..0x053A20` | 72 | thumb | `code_539D8_53A20` | asm/buu.s | byte-proven | asm |
| 37 | `0x046B58..0x046B74` | 28 | thumb | `code_46B58_46B74` | asm/buu.s | byte-proven | asm |
| 38 | `0x054EF8..0x054F14` | 28 | thumb | `code_54EF8_54F14` | asm/buu.s | byte-proven | asm |
| 39 | `0x05393C..0x053954` | 24 | thumb | `code_5393C_53954` | asm/buu.s | byte-proven | asm |
| 40 | `0x049198..0x0491AC` | 20 | thumb | `code_49198_491AC` | asm/buu.s | byte-proven | asm |
| 41 | `0x05440C..0x054420` | 20 | thumb | `code_5440C_54420` | asm/buu.s | byte-proven | asm |
| 42 | `0x054ACC..0x054AE0` | 20 | thumb | `code_54ACC_54AE0` | asm/buu.s | byte-proven | asm |
| 43 | `0x05460C..0x054618` | 12 | thumb | `code_5460C_54618` | asm/buu.s | byte-proven | asm |
| 44 | `0x047FBC..0x047FC4` | 8 | thumb | `code_47FBC_47FC4` | asm/buu.s | byte-proven | asm |
| 45 | `0x0540D4..0x0540DC` | 8 | thumb | `code_540D4_540DC` | asm/buu.s | byte-proven | asm |
| 46 | `0x054158..0x054160` | 8 | thumb | `code_54158_54160` | asm/buu.s | byte-proven | asm |
| 47 | `0x046B28..0x046B2C` | 4 | thumb | `code_46B28_46B2C` | asm/buu.s | byte-proven | asm |
| 48 | `0x046B38..0x046B3C` | 4 | thumb | `code_46B38_46B3C` | asm/buu.s | byte-proven | asm |
| 49 | `0x046B84..0x046B88` | 4 | thumb | `code_46B84_46B88` | asm/buu.s | byte-proven | asm |
| 50 | `0x046B94..0x046B98` | 4 | thumb | `code_46B94_46B98` | asm/buu.s | byte-proven | asm |
| 51 | `0x046BA4..0x046BA8` | 4 | thumb | `code_46BA4_46BA8` | asm/buu.s | byte-proven | asm |
| 52 | `0x046BFC..0x046C00` | 4 | thumb | `code_46BFC_46C00` | asm/buu.s | byte-proven | asm |
| 53 | `0x046C28..0x046C2C` | 4 | thumb | `code_46C28_46C2C` | asm/buu.s | byte-proven | asm |
| 54 | `0x046D18..0x046D1C` | 4 | thumb | `code_46D18_46D1C` | asm/buu.s | byte-proven | asm |
| 55 | `0x046DD0..0x046DD4` | 4 | thumb | `code_46DD0_46DD4` | asm/buu.s | byte-proven | asm |
| 56 | `0x046E40..0x046E44` | 4 | thumb | `code_46E40_46E44` | asm/buu.s | byte-proven | asm |
| 57 | `0x046E58..0x046E5C` | 4 | thumb | `code_46E58_46E5C` | asm/buu.s | byte-proven | asm |
| 58 | `0x046F30..0x046F34` | 4 | thumb | `code_46F30_46F34` | asm/buu.s | byte-proven | asm |
| 59 | `0x047A40..0x047A44` | 4 | thumb | `code_47A40_47A44` | asm/buu.s | byte-proven | asm |
| 60 | `0x047FD4..0x047FD8` | 4 | thumb | `code_47FD4_47FD8` | asm/buu.s | byte-proven | asm |
| 61 | `0x049120..0x049124` | 4 | thumb | `code_49120_49124` | asm/buu.s | byte-proven | asm |
| 62 | `0x04912C..0x049130` | 4 | thumb | `code_4912C_49130` | asm/buu.s | byte-proven | asm |
| 63 | `0x049138..0x04913C` | 4 | thumb | `code_49138_4913C` | asm/buu.s | byte-proven | asm |
| 64 | `0x049144..0x049148` | 4 | thumb | `code_49144_49148` | asm/buu.s | byte-proven | asm |
| 65 | `0x049150..0x049154` | 4 | thumb | `code_49150_49154` | asm/buu.s | byte-proven | asm |
| 66 | `0x04915C..0x049160` | 4 | thumb | `code_4915C_49160` | asm/buu.s | byte-proven | asm |
| 67 | `0x049168..0x04916C` | 4 | thumb | `code_49168_4916C` | asm/buu.s | byte-proven | asm |
| 68 | `0x049174..0x049178` | 4 | thumb | `code_49174_49178` | asm/buu.s | byte-proven | asm |
| 69 | `0x049180..0x049184` | 4 | thumb | `code_49180_49184` | asm/buu.s | byte-proven | asm |
| 70 | `0x04918C..0x049190` | 4 | thumb | `code_4918C_49190` | asm/buu.s | byte-proven | asm |
| 71 | `0x0491B4..0x0491B8` | 4 | thumb | `code_491B4_491B8` | asm/buu.s | byte-proven | asm |
| 72 | `0x0491C0..0x0491C4` | 4 | thumb | `code_491C0_491C4` | asm/buu.s | byte-proven | asm |
| 73 | `0x053034..0x053038` | 4 | thumb | `code_53034_53038` | asm/buu.s | byte-proven | asm |
| 74 | `0x053058..0x05305C` | 4 | thumb | `code_53058_5305C` | asm/buu.s | byte-proven | asm |
| 75 | `0x053080..0x053084` | 4 | thumb | `code_53080_53084` | asm/buu.s | byte-proven | asm |
| 76 | `0x0530A4..0x0530A8` | 4 | thumb | `code_530A4_530A8` | asm/buu.s | byte-proven | asm |
| 77 | `0x0530C8..0x0530CC` | 4 | thumb | `code_530C8_530CC` | asm/buu.s | byte-proven | asm |
| 78 | `0x05311C..0x053120` | 4 | thumb | `code_5311C_53120` | asm/buu.s | byte-proven | asm |
| 79 | `0x05313C..0x053140` | 4 | thumb | `code_5313C_53140` | asm/buu.s | byte-proven | asm |
| 80 | `0x05315C..0x053160` | 4 | thumb | `code_5315C_53160` | asm/buu.s | byte-proven | asm |
| 81 | `0x053694..0x053698` | 4 | thumb | `code_53694_53698` | asm/buu.s | byte-proven | asm |
| 82 | `0x0536DC..0x0536E0` | 4 | thumb | `code_536DC_536E0` | asm/buu.s | byte-proven | asm |
| 83 | `0x053994..0x053998` | 4 | thumb | `code_53994_53998` | asm/buu.s | byte-proven | asm |
| 84 | `0x0539B0..0x0539B4` | 4 | thumb | `code_539B0_539B4` | asm/buu.s | byte-proven | asm |
| 85 | `0x053A40..0x053A44` | 4 | thumb | `code_53A40_53A44` | asm/buu.s | byte-proven | asm |
| 86 | `0x053CF4..0x053CF8` | 4 | thumb | `code_53CF4_53CF8` | asm/buu.s | byte-proven | asm |
| 87 | `0x054054..0x054058` | 4 | thumb | `code_54054_54058` | asm/buu.s | byte-proven | asm |
| 88 | `0x05484C..0x054850` | 4 | thumb | `code_5484C_54850` | asm/buu.s | byte-proven | asm |
| 89 | `0x054A48..0x054A4C` | 4 | thumb | `code_54A48_54A4C` | asm/buu.s | byte-proven | asm |
| 90 | `0x054A64..0x054A68` | 4 | thumb | `code_54A64_54A68` | asm/buu.s | byte-proven | asm |
| 91 | `0x054B3C..0x054B40` | 4 | thumb | `code_54B3C_54B40` | asm/buu.s | byte-proven | asm |
| 92 | `0x054DEC..0x054DF0` | 4 | thumb | `code_54DEC_54DF0` | asm/buu.s | byte-proven | asm |
| 93 | `0x054E74..0x054E78` | 4 | thumb | `code_54E74_54E78` | asm/buu.s | byte-proven | asm |
| 94 | `0x054F38..0x054F3C` | 4 | thumb | `code_54F38_54F3C` | asm/buu.s | byte-proven | asm |







## 5. Note (2026-10-15): the C-PILOT-001 row split

| row | span (file) | size | insn | data | origin / evidence |
|---|---|---:|---:|---:|---|
| `code_1C3F2_1C62C` | `0x1C3F2..0x1C62C` | 570 | 442 | 128 | `transcription` / `byte-proven` |
| `sub_0801C62C` | `0x1C62C..0x1C634` | 8 | 8 | 0 | `c` / `c-matched` |
| `code_1C634_2AB4C` | `0x1C634..0x2AB4C` | 58,648 | 33,772 | 24,876 | `transcription` / `byte-proven` |


## 7. Note (2026-10-15): C-TIDY-001 and the C-UNITS-003 units

| file | B | flags | callees | caller repointed | AREA kept / new |
|---|---:|---|---|---|---|
| `0x3431C` | 20 | `-O2 -Otime -apcs /nointerwork` | `Thunk_JumpRegister1` | none | `CPilotTail2` / `CPilotTail3` at `0x34330` |
| `0x45598` | 28 | `-O2 -apcs /interwork` | `loc_08043b66`, `loc_080437c2` | none | `UnusedGBARam2` / `UnusedGBARam3` at `0x455B4` |
| `0x45658` | 24 | `-O2 -apcs /interwork` | `loc_080437c2` | none | `UnusedGBARam3` / `UnusedGBARam4` at `0x45670` |
| `0x3E44C` | 84 | `-O2 -Otime -apcs /nointerwork` | `GBARam_Malloc`, `sub_08049138` | file `0x11DCE` | `UnusedGBARam` / `UnusedGBARam5` at `0x3E4A0` |
| `0x3E4A0` | 68 | `-O2 -Otime -apcs /nointerwork` | `GBARam_Free`, `sub_08049138` | file `0x11E70` | `UnusedGBARam5` renamed `UnusedGBARam6` at `0x3E4E4` |

## 8. Note (2026-10-15): C-UNITS-004, the two units that landed and the five windows that did not

| file | B | flags | callees | AREA kept / new | ledger instrument |
|---|---:|---|---|---|---|
| `0x2AD88` | 52 | `-O2 -apcs /nointerwork` | `loc_0800ECDA`, `loc_0800ED18` | `CPilotTail` / `CPilotTail4` at `0x2ADBC` | `$d` |
| `0x46124` | 212 | `-O2 -apcs /interwork` | `loc_08045b40`, `loc_08045d8c` | `UnusedGBARam4` / `UnusedGBARam7` at `0x461F8` | decode-based mode map |



## 10. Note (2026-10-15): C-UNITS-005 unit 3, file `0x02F5F8` (300 B) - MEASURED NEGATIVE

| body | span | B | instructions |
|---|---|---:|---:|
| `sub_0802F5F8` | `0x02F5F8..0x02F6A8` | 176 | 84 |
| `sub_0802F6A8` | `0x02F6A8..0x02F6F6` | 78 | 35 |
| `sub_0802F6F6` | `0x02F6F6..0x02F708` | 18 | 9 |
| `sub_0802F708` | `0x02F708..0x02F70E` | 6 | 3 |
| alignment | `0x02F70E..0x02F710` | 2 | - |
| pool | `0x02F710..0x02F724` | 20 | 5 words |
| file offset | word | names | reading |
|---|---|---|---|
| `0x2CCBCC` | `0802F603` | `0x02F602` | coincidence: neighbours `E5E0E1DF`, `0E07F7FA`, `0F06090B` are not pointers |
| `0x2CCFA8` | `0802F6F9` | `0x02F6F8` | coincidence: neighbours `EEF0E6E9`, `F3F9FEEE`, `0217071A` |
| `0x3087B4` | `0802F6F8` | `0x02F6F8` | coincidence: neighbours `171B0AE9`, `FF0C1B11`, `FCE7DEF2` |
| `0x46B544` | `0802F71A` | `0x02F71A` (a pool word) | coincidence: neighbours `116DCA36`, `21000092`, `908D0248` |
| `0x757AA4` | `0802F709` | `0x02F708` (Thumb-odd) | REAL: a table word, neighbours `0802F743`, `FFFFFFF5`, `00000018` |
| approach | first divergence | halfwords differing | code bytes / instructions | `sub_0802F5F8` | `sub_0802F6A8` | section |
|---|---|---|---:|---:|---:|---:|
| (1) `u16 c` + struct copies | `0x02F5FC` hw2: linked `1c0c`, retail `b086` | 139 of 150 | 268 / 126 | 77 insns (154 B) | 37 | 288 B |
| (2) `++p->unk_12` | `0x02F5FC` hw2: linked `1c0c`, retail `b086` | 137 of 150 | 272 / 128 | 79 insns (158 B) | 37 | 292 B |
| retail | - | - | 278 / 131 | 84 insns (176 B) | 35 | 300 B |
