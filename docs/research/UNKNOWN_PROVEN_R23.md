# What consumes runs 2 and 3 of the census's `unknown-proven` rows

PATH-100-004. Run 2 `0x76CCE4..0x77AE68` (57,732 B) and run 3 `0x71E274..0x72C378` (57,604 B) each have cited loaders (40 sites on 22 literals; 182 on 61) but no byte-exact parse, so neither gains an extent. Both are promoted as labeled raw data under R-RAW-001.

    python tools\research\loader_access_trace.py --rom baserom.gba --range 0x76CCE4 0x77AE68

| run | range | bytes | census row | INCBIN name |
|---|---|---|---|---|
| 2 | `0x76CCE4..0x77AE68` | 57,732 | `INCBIN_CENSUS.md:2181` | `baserom.gba_0x76cce4_0x77ae68.extracted` |
| 3 | `0x71E274..0x72C378` | 57,604 | `INCBIN_CENSUS.md:2071` | `baserom.gba_0x71e274_0x72c378.extracted` |

## Bytes explained, per run (SC2)

| run | bytes | loader sites | sites in real code | bytes read at a constant offset | share |
|---|---|---|---|---|---|
| 2 | 57,732 | 40 | 35 (5 in-range, see P-420) | 75 | 0.13 % |
| 3 | 57,604 | 182 | 182 | 326 | 0.57 % |


### run 0x76CCE4..0x77AE68  bytes=75

| literal | target | loaders | accesses (mnemonic + constant offset) | bytes in the run | indexes a register |
|---|---|---|---|---|---|
| `0x0386E0` | `0x0876E0B8` | 8 | ldr r7 +0x4, INDEXED base + register (r1, r1, r3), INDEXED base + register (r0, r0, r1), ldr r0 +0x4, ldr r6 +0x4, ldr r6 +0x8, ldr r1 +0x8, ldr r7 +0x8, ldr r7 +0x0, ldr r5 +0xc, ldr r5 +0x4 | 24 | yes |
| `0x038DD4` | `0x0877110C` | 4 | ldr r0 +0x0, ldr r4 +0x0, INDEXED base + register (r0, r0, r3) | 4 | yes |
| `0x038A64` | `0x0876E0DC` | 3 | ldr r5 +0x0, INDEXED base + register (r3, r3, r6), INDEXED base + register (r0, r0, r5), ldr r1 +0x8, ldr r3 +0x4 | 12 | yes |
| `0x038A6C` | `0x08770CF4` | 3 | INDEXED base + register (r1, r1, r2), INDEXED base + register (r0, r0, r7), ldr r1 +0x8, ldr r3 +0x4, ldr r6 +0x4, INDEXED ldrsb [r6 + reg], ldrb r6 +0x1 | 13 | yes |
| `0x039350` | `0x0877AE58` | 3 | ldm r0 +0x0, ldr r0 +0x0 | 20 | no |
| `0x038F20` | `0x0877110C` | 2 | ldr r4 +0x0, ldr r0 +0x0 | 4 | no |
| `0x039210` | `0x0877ADD8` | 2 | INDEXED ldr [r2 + reg], INDEXED ldr [r3 + reg] | 0 | yes |
| `0x01AB74` | `0x087710FC` | 1 | - | 0 | no |
| `0x038184` | `0x0876DFF8` | 1 | INDEXED base + register (r1, r1, r2), INDEXED base + register (r0, r0, r1), INDEXED base + register (r7, r0, r1) | 0 | yes |
| `0x0386E8` | `0x0876E264` | 1 | INDEXED base + register (r1, r1, r3), INDEXED base + register (r0, r0, r1), INDEXED base + register (r0, r0, r5), ldr r0 +0x4 | 4 | yes |
| `0x0387D4` | `0x0876E0C4` | 1 | - | 0 | no |
| `0x038A7C` | `0x08770D0C` | 1 | INDEXED base + register (r3, r3, r6), INDEXED base + register (r0, r0, r5), ldr r1 +0x8, ldr r3 +0x4 | 8 | yes |
| `0x038AD4` | `0x08770CF4` | 1 | ldr r1 +0x8 | 4 | no |
| `0x038DCC` | `0x0877AD10` | 1 | INDEXED base + register (r0, r0, r1), ldr r0 +0x0 | 4 | yes |
| `0x039124` | `0x0877ADD0` | 1 | ldr r4 +0x4, ldr r4 +0x0, INDEXED base + register (r1, r0, r1), INDEXED base + register (r0, r4, r0) | 8 | yes |
| `0x052C6C` | `0x0876E0DC` | 1 | ldr r0 +0x0 | 4 | no |
| `0x1270AC` | `0x087703AC` | 1 | ldrh r0 +0x18 | 2 | no |
| `0x770D14` | `0x0876EAF4` | 1 | - | 0 | no |
| `0x770D2C` | `0x0876EEF4` | 1 | - | 0 | no |
| `0x770D74` | `0x0876F0F4` | 1 | - | 0 | no |
| `0x770DA4` | `0x0876F6F4` | 1 | - | 0 | no |
| `0x770DEC` | `0x0876F8F4` | 1 | - | 0 | no |

### run 0x71E274..0x72C378  bytes=326

| literal | target | loaders | accesses (mnemonic + constant offset) | bytes in the run | indexes a register |
|---|---|---|---|---|---|
| `0x021BB8` | `0x0872A6B4` | 11 | ldr r1 +0x10, ldr r1 +0x14, ldr r7 +0x8, ldr r0 +0x8, ldr r0 +0x18, ldr r7 +0x18, ldr r7 +0xc, ldr r0 +0xc, ldr r7 +0x30, ldr r7 +0x4, INDEXED base + register (r0, r0, r1), ldr r7 +0x20 | 32 | yes |
| `0x020A7C` | `0x08725048` | 9 | ldr r6 +0x4, INDEXED base + register (r0, r0, r2), ldr r7 +0x0, INDEXED base + register (r5, r2, r1), ldr r7 +0x4, ldr r0 +0x0, ldr r0 +0x4, ldr r1 +0x8, INDEXED base + register (r0, r0, r3), INDEXED base + register (r1, r0, r1), INDEXED base + register (r0, r6, r0) | 12 | yes |
| `0x01D3FC` | `0x0871E9A8` | 8 | ldr r2 +0xc, INDEXED base + register (r7, r0, r1), INDEXED base + register (r0, r0, r1), ldr r6 +0x8, ldr r5 +0x8, INDEXED ldr [r3 + reg], ldr r1 +0x1c, ldr r1 +0x18, ldr r1 +0xc, INDEXED base + register (r1, r1, r2) | 16 | yes |
| `0x01DF84` | `0x0871E9D8` | 8 | ldr r2 +0xc, INDEXED base + register (r3, r3, r6), ldr r2 +0x4, INDEXED base + register (r0, r0, r5), ldr r0 +0x4, INDEXED base + register (r0, r0, r6), INDEXED base + register (r0, r0, r4), INDEXED base + register (r0, r0, r7), ldr r0 +0x0 | 12 | yes |
| `0x01F7B8` | `0x0872083C` | 8 | ldr r0 +0xc, INDEXED base + register (r0, r0, r1), ldr r2 +0xc, INDEXED base + register (r6, r2, r1), ldr r1 +0xc, INDEXED base + register (r5, r5, r0), ldr r7 +0xc, ldr r7 +0x8, INDEXED ldr [r1 + reg] | 8 | yes |
| `0x023484` | `0x0872BFA8` | 7 | ldr r0 +0x10, INDEXED base + register (r6, r5, r2), INDEXED ldr [r0 + reg], ldr r6 +0xc, INDEXED base + register (r0, r0, r1), INDEXED base + register (r1, r5, r0), ldr r7 +0x0, INDEXED base + register (r0, r3, r0), ldr r7 +0x4 | 16 | yes |
| `0x01E9E8` | `0x0872081C` | 6 | ldr r3 +0x4, INDEXED base + register (r0, r1, r0), ldr r3 +0xc, ldr r0 +0x0, ldr r0 +0x4, INDEXED base + register (r0, r0, r5), ldr r0 +0x10 | 16 | yes |
| `0x02156C` | `0x08725090` | 6 | ldr r0 +0x0, INDEXED base + register (r0, r0, r5), ldr r5 +0x0, INDEXED base + register (r0, r0, r2), ldr r5 +0x4, INDEXED base + register (r1, r0, r1), INDEXED base + register (r0, r5, r0) | 8 | yes |
| `0x021EB4` | `0x0872A6B4` | 6 | ldr r5 +0x10, ldr r5 +0x14, ldr r0 +0xc, ldr r1 +0x10, ldr r1 +0x14, ldr r6 +0xc, ldr r4 +0x10, ldr r4 +0x14 | 12 | no |
| `0x023088` | `0x0872BFA8` | 6 | ldr r5 +0x1c, INDEXED base + register (r1, r4, r0), ldr r5 +0xc, ldr r2 +0x10, INDEXED ldrh [r1 + reg], ldr r6 +0x10, INDEXED base + register (r0, r5, r0), ldr r6 +0x1c, ldr r0 +0x1c | 12 | yes |
| `0x01D5E4` | `0x0871E9A8` | 5 | ldr r7 +0x4, INDEXED base + register (r0, r1, r0), ldr r0 +0xc, ldr r1 +0x0, ldr r3 +0x4, INDEXED base + register (r6, r3, r2), ldr r0 +0x0 | 12 | yes |
| `0x01D958` | `0x0871E9D8` | 5 | ldr r1 +0xc, ldr r0 +0xc, INDEXED base + register (r3, r3, r6), ldr r6 +0xc, ldr r7 +0x8 | 8 | yes |
| `0x02028C` | `0x0872084C` | 5 | ldr r3 +0x4, INDEXED base + register (r0, r1, r0), ldr r6 +0x14, ldr r6 +0x10, ldr r6 +0x8, ldr r1 +0x0, INDEXED base + register (r7, r3, r2), ldr r0 +0x0 | 20 | yes |
| `0x021054` | `0x08725054` | 5 | - | 0 | no |
| `0x0222DC` | `0x0872A6F8` | 5 | ldr r7 +0x4, ldr r7 +0x8, ldr r4 +0x4, ldr r4 +0x0 | 12 | no |
| `0x01E47C` | `0x087207EC` | 4 | ldr r6 +0x8, ldr r0 +0x8, INDEXED ldr [r1 + reg], ldr r1 +0x4, INDEXED base + register (r0, r1, r0), ldr r0 +0x0, ldr r0 +0x4, INDEXED base + register (r0, r0, r7) | 12 | yes |
| `0x01E74C` | `0x0872080C` | 4 | ldr r1 +0x4, INDEXED base + register (r5, r1, r0), ldr r4 +0x0, ldr r4 +0x4, INDEXED base + register (r0, r0, r5), ldr r1 +0x8 | 12 | yes |
| `0x0228FC` | `0x0872BFA4` | 4 | ldr r7 +0x0, ldr r5 +0x0, ldr r0 +0x0 | 4 | no |
| `0x01ECC0` | `0x0872082C` | 3 | ldr r6 +0x4, ldr r0 +0x4, INDEXED ldr [r1 + reg], INDEXED base + register (r0, r0, r1), ldr r1 +0x0, INDEXED base + register (r0, r1, r0) | 8 | yes |
| `0x01F064` | `0x08720834` | 3 | ldr r6 +0x4, ldr r2 +0x0 | 8 | no |
| `0x020DA0` | `0x08725048` | 3 | ldr r0 +0x4, ldr r1 +0x8 | 8 | no |
| `0x021728` | `0x0872509E` | 3 | ldrb r7 +0x0, ldrb r7 +0x1, ldr r0 +0x0, ldr r1 +0x8, INDEXED base + register (r0, r0, r3), INDEXED base + register (r2, r2, r3) | 10 | yes |
| `0x0220C4` | `0x0872A6B4` | 3 | ldr r4 +0x10, ldr r4 +0x14, ldr r7 +0x8, ldr r6 +0x14, ldr r6 +0x0 | 16 | no |
| `0x022600` | `0x0872BF06` | 3 | ldrb r6 +0x0, ldrb r6 +0x1, ldr r7 +0x4, ldr r1 +0x8, INDEXED base + register (r0, r0, r3) | 10 | yes |
| `0x022608` | `0x0872BF94` | 3 | ldr r7 +0x4, ldr r1 +0x8, INDEXED base + register (r0, r0, r3), ldr r2 +0x8, ldr r1 +0x0 | 16 | yes |
| `0x0237C4` | `0x0872BFA8` | 3 | ldr r0 +0x1c, ldr r4 +0x1c, ldr r0 +0x4 | 8 | no |
| `0x02402C` | `0x0872C358` | 3 | INDEXED base + register (r0, r0, r2), ldr r0 +0x0, INDEXED base + register (r1, r1, r2), INDEXED base + register (r0, r0, r4) | 4 | yes |
| `0x01C8E8` | `0x0871E984` | 2 | INDEXED base + register (r0, r0, r1) | 0 | yes |
| `0x01CB80` | `0x0871E630` | 2 | INDEXED base + register (r0, r0, r1), INDEXED base + register (r0, r0, r5) | 0 | yes |
| `0x01DC6C` | `0x0871E9D8` | 2 | ldr r6 +0xc, ldr r6 +0x8 | 8 | no |
| `0x01E148` | `0x087202E8` | 2 | INDEXED base + register (r0, r0, r1) | 0 | yes |
| `0x01FB58` | `0x0872083C` | 2 | ldr r0 +0x8, INDEXED ldr [r1 + reg], ldr r1 +0x4, INDEXED base + register (r7, r1, r0) | 8 | yes |
| `0x020544` | `0x0872084C` | 2 | ldr r6 +0xc, ldr r0 +0x10 | 8 | no |
| `0x02126C` | `0x08725084` | 2 | ldr r5 +0x0, ldr r5 +0x4, ldr r7 +0x4, ldr r7 +0x0 | 8 | no |
| `0x022D38` | `0x0872BFA8` | 2 | ldr r4 +0x1c, ldr r5 +0xc, INDEXED ldr [r7 + reg], ldr r5 +0x8 | 12 | yes |
| `0x023C84` | `0x0872C34C` | 2 | ldr r0 +0x4, ldr r1 +0x4, INDEXED base + register (r1, r4, r1), INDEXED base + register (r0, r4, r0), INDEXED base + register (r5, r4, r0) | 4 | yes |
| `0x01441C` | `0x08720564` | 1 | INDEXED base + register (r4, r0, r1) | 0 | yes |
| `0x01AE1C` | `0x08725018` | 1 | INDEXED base + register (r2, r0, r1) | 0 | yes |
| `0x01C3DC` | `0x0872A690` | 1 | INDEXED base + register (r2, r0, r1) | 0 | yes |
| `0x01DFD4` | `0x0871E9D8` | 1 | ldr r0 +0x0, ldr r0 +0x4, INDEXED base + register (r0, r0, r4) | 8 | yes |
| `0x01E1E4` | `0x087207E4` | 1 | ldr r6 +0x4, ldr r6 +0x0, INDEXED ldr [r0 + reg], INDEXED base + register (r0, r0, r1) | 8 | yes |
| `0x01FF60` | `0x0872083C` | 1 | ldr r3 +0x4, INDEXED base + register (r7, r6, r1), ldr r3 +0x0 | 8 | yes |
| `0x021168` | `0x0872507C` | 1 | ldr r4 +0x4, ldr r4 +0x0 | 8 | no |
| `0x02127C` | `0x0872508C` | 1 | ldr r0 +0x0 | 4 | no |
| `0x02182C` | `0x087251C8` | 1 | ldr r5 +0x8, ldr r5 +0x0, ldr r5 +0xc, ldr r5 +0x4 | 16 | no |
| `0x021870` | `0x087251D8` | 1 | ldr r0 +0x0 | 4 | no |
| `0x02261C` | `0x0872BF34` | 1 | - | 0 | no |
| `0x022620` | `0x0872BF64` | 1 | - | 0 | no |
| `0x022674` | `0x0872BFA0` | 1 | ldr r7 +0x0 | 4 | no |
| `0x023A74` | `0x0872C34C` | 1 | ldr r6 +0x0 | 4 | no |
| `0x03BF18` | `0x0872A6A8` | 1 | - | 0 | no |
| `0x03C40C` | `0x08725038` | 1 | - | 0 | no |
| `0x04F828` | `0x0871E9A8` | 1 | ldr r0 +0x14 | 4 | no |
| `0x04FCF4` | `0x0872A6B4` | 1 | ldr r1 +0x10 | 4 | no |
| `0x04FD20` | `0x0872A6B4` | 1 | ldr r0 +0x14 | 4 | no |
| `0x051A04` | `0x0872033C` | 1 | ldr r0 +0x0 | 4 | no |
| `0x05206C` | `0x08725098` | 1 | ldr r0 +0x0 | 4 | no |
| `0x052DA8` | `0x0872BF94` | 1 | ldr r0 +0x4 | 4 | no |
| `0x052EA8` | `0x0872BF94` | 1 | ldr r0 +0x4 | 4 | no |
| `0x465CD0` | `0x08725749` | 1 | strh r0 +0x2e | 2 | no |
| `0x617B40` | `0x08720200` | 1 | - | 0 | no |





## Promoted as `raw-labeled` (R-RAW-001)

| run | file | symbols | bytes | cited bases | generated by |
|---|---|---|---|---|---|
| 2 | `asm/rawlabeled_76cce4.s` | 15 | 57,732 | 14 | `tools/research/rawlabeled.py` |
| 3 | `asm/rawlabeled_71e274.s` | 43 | 57,604 | 42 | `tools/research/rawlabeled.py` |
| symbol | file offset | bytes | first cited site | stride | shape (no extent claimed) |
|---|---|---|---|---|---|
| `|unk_0876CCE4|` | `0x76CCE4` | 592 | - | - | - |
| `|unk_0876DFF8|` | `0x76DFF8` | 192 | 0x08037F24 | 48 | K-089 pieces |
| `|unk_0876E0B8|` | `0x76E0B8` | 12 | 0x080383F0 +3 | - | IWRAM descriptor |
| `|unk_0876E0C4|` | `0x76E0C4` | 24 | 0x08038714 | - | - |
| `|unk_0876E0DC|` | `0x76E0DC` | 392 | 0x08052C4A | - | IWRAM descriptor |
| `|unk_0876E264|` | `0x76E264` | 576 | 0x08038458 | 36 | K-089 pieces |
| `|unk_087703AC|` | `0x7703AC` | 592 | 0x08126D20 | - | - |
| `|unk_08770CF4|` | `0x770CF4` | 24 | 0x08038AA4 | 4 | K-089 pieces |
| `|unk_08770D0C|` | `0x770D0C` | 592 | 0x080388EE | - | - |
| `|unk_087710FC|` | `0x7710FC` | 16 | 0x0801A924 | - | - |
| `|unk_0877110C|` | `0x77110C` | 592 | 0x08038E1E +1 | - | - |
| `|unk_0877AD10|` | `0x77AD10` | 192 | 0x08038B30 | - | - |
| `|unk_0877ADD0|` | `0x77ADD0` | 8 | 0x080390C8 | - | - |
| `|unk_0877ADD8|` | `0x77ADD8` | 128 | 0x080391C0 +1 | 4 | IWRAM addr table |
| `|unk_0877AE58|` | `0x77AE58` | 16 | 0x0803928E +2 | - | box |
| `|unk_0871E274|` | `0x71E274` | 592 | - | - | - |
| `|unk_0871E630|` | `0x71E630` | 592 | 0x0801C93A +1 | - | - |
| `|unk_0871E984|` | `0x71E984` | 36 | 0x0801C732 +1 | - | K-089 pieces |
| `|unk_0871E9A8|` | `0x71E9A8` | 48 | 0x0804F81A | - | IWRAM descriptor |
| `|unk_0871E9D8|` | `0x71E9D8` | 576 | 0x0801DFAC | - | IWRAM descriptor |
| `|unk_08720200|` | `0x720200` | 232 | 0x086178AE | - | - |
| `|unk_087202E8|` | `0x7202E8` | 84 | 0x0801E038 +1 | - | - |
| `|unk_0872033C|` | `0x72033C` | 552 | 0x080519E2 | - | - |
| `|unk_08720564|` | `0x720564` | 592 | 0x080141EE | - | - |
| `|unk_087207E4|` | `0x7207E4` | 8 | 0x0801E1AC | - | - |
| `|unk_087207EC|` | `0x7207EC` | 32 | 0x0801E234 +3 | - | - |
| `|unk_0872080C|` | `0x72080C` | 16 | 0x0801E4BC +3 | - | - |
| `|unk_0872081C|` | `0x72081C` | 16 | 0x0801E790 +3 | - | - |
| `|unk_0872082C|` | `0x72082C` | 8 | 0x0801EA3A +2 | - | - |
| `|unk_08720834|` | `0x720834` | 8 | 0x0801ED6A +2 | - | - |
| `|unk_0872083C|` | `0x72083C` | 16 | 0x0801FE9A | - | - |
| `|unk_0872084C|` | `0x72084C` | 592 | 0x08020416 +1 | - | - |
| `|unk_08725018|` | `0x725018` | 32 | 0x0801ADE0 | - | - |
| `|unk_08725038|` | `0x725038` | 16 | 0x0803C352 | - | - |
| `|unk_08725048|` | `0x725048` | 12 | 0x08020AF0 +2 | - | IWRAM descriptor |
| `|unk_08725054|` | `0x725054` | 40 | 0x08020DBE +3 | - | - |
| `|unk_0872507C|` | `0x72507C` | 8 | 0x0802111E | - | - |
| `|unk_08725084|` | `0x725084` | 8 | 0x080211AA +1 | - | - |
| `|unk_0872508C|` | `0x72508C` | 4 | 0x08021270 | - | - |
| `|unk_08725090|` | `0x725090` | 8 | 0x080212E4 +3 | - | - |
| `|unk_08725098|` | `0x725098` | 6 | 0x0805204A | - | - |
| `|unk_0872509E|` | `0x72509E` | 298 | 0x080215B0 +2 | - | - |
| `|unk_087251C8|` | `0x7251C8` | 16 | 0x0802177E | - | - |
| `|unk_087251D8|` | `0x7251D8` | 592 | 0x0802183A | - | - |
| `|unk_08725749|` | `0x725749` | 577 | 0x08465A36 | - | - |
| `|unk_0872A690|` | `0x72A690` | 24 | 0x0801C0EC | - | - |
| `|unk_0872A6A8|` | `0x72A6A8` | 12 | 0x0803BDD8 | - | - |
| `|unk_0872A6B4|` | `0x72A6B4` | 68 | 0x0804FD10 | - | IWRAM descriptor |
| `|unk_0872A6F8|` | `0x72A6F8` | 576 | 0x0802211A +3 | - | IWRAM descriptor |
| `|unk_0872BF06|` | `0x72BF06` | 46 | 0x080222F8 +2 | - | - |
| `|unk_0872BF34|` | `0x72BF34` | 48 | 0x08022368 | - | - |
| `|unk_0872BF64|` | `0x72BF64` | 48 | 0x08022376 | - | - |
| `|unk_0872BF94|` | `0x72BF94` | 12 | 0x08052E86 | - | - |
| `|unk_0872BFA0|` | `0x72BFA0` | 4 | 0x08022646 | - | - |
| `|unk_0872BFA4|` | `0x72BFA4` | 4 | 0x080226E4 +3 | - | IWRAM descriptor |
| `|unk_0872BFA8|` | `0x72BFA8` | 576 | 0x08022AF8 +1 | - | IWRAM descriptor |
| `|unk_0872C34C|` | `0x72C34C` | 12 | 0x080237FC | - | - |
| `|unk_0872C358|` | `0x72C358` | 32 | 0x08023F64 +2 | - | - |
