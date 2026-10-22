# The census's `unmapped` rows, measured once

PATH-100-006, on master after PATH-100-004 merged. The census
(`docs/research/INCBIN_CENSUS.md`) called 591 rows / 189,777 B `unmapped`: no region claimed them.
This file is the one pass over all of them, largest first, and the outcome each row now carries in
the census region table. It promotes nothing by itself; the promotion is `asm/rawlabeled_<start>.s`
plus the `INCLUDE` that replaced the row's INCBIN line.

Channels, measured at the retail bytes with the tracked tools (`unknown_consumer_search.py`'s
Thumb-1 `ldr Rd,[pc,#imm8]` literal channel, `code_xref.py`'s ARM literal channel):

| channel | what it measures |
|---|---|
| `loaders` | Thumb-1 literal sites whose literal's VALUE names the row, split by whether the site's own address lies inside the row (P-420: an in-row site is the row's own bytes decoded as an instruction) |
| `multi`   | of those literals, how many are loaded by more than one instruction - the only shape that separates a real literal pool from a coincidence (P-418) |
| `null`    | the same `loaders` measurement over 12 same-size control windows at the tool's stride, so no count is read alone |
| `arm`     | ARM `ldr rX,[pc,#+/-imm12]` sites whose loaded word IS an address in the row |
| `direct`  | word-aligned words outside the row whose value names it |
| `indirect`| words that name the row from inside a table that a literal itself names |

Denominators, quoted with every negative: 117,008 Thumb + 618 ARM ldr-literal sites (the whole-image
linear sweep, `code_xref.scan`), and 2,097,152 word-aligned words for the `direct` channel.

Outcome classes:

- `raw-labeled` - the row is named by a literal loaded by more than one instruction, or its loader
  count is above every same-size control window. R-RAW-001 promotes it as LABELED RAW DATA: the
  bytes are carried as assembler directives with one symbol per cited base, NO EXTENT claimed.
- `no-consumer` - no literal site names the row. Recorded in the census with the denominator; not
  promoted, because the census needs a cited consumer before either a parse or a raw label.

| # | range | bytes | outcome | consumer / denominator |
|---|---|---|---|---|
| 1 | `0x2659D4..0x26670C` | 3384 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 5 - at or below the null (P-418) |
| 2 | `0x24A1CC..0x24AEC4` | 3320 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 3 | `0x2B31E8..0x2B3E6C` | 3204 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 1 through a table a literal itself names |
| 4 | `0x73E540..0x73F0CC` | 2956 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 5 - at or below the null (P-418) |
| 5 | `0x1A241C..0x1A2E8C` | 2672 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 3 through a table a literal itself names |
| 6 | `0x7372E8..0x737D58` | 2672 | `no-consumer` | no consumer: 3 singleton literal site(s) (0 multi-site), same-size control max 4 - at or below the null (P-418) |
| 7 | `0x740E1C..0x74188C` | 2672 | `no-consumer` | no consumer: 0 literal sites; 32 word(s) outside name it, 0 through a table a literal itself names |
| 8 | `0x25EB64..0x25F5A0` | 2620 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 9 | `0x73917C..0x739BB8` | 2620 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 4 - at or below the null (P-418) |
| 10 | `0x252BBC..0x2535E0` | 2596 | `no-consumer` | no consumer: 0 literal sites; 7 word(s) outside name it, 3 through a table a literal itself names |
| 11 | `0x25D5A0..0x25DF9C` | 2556 | `no-consumer` | no consumer: 0 literal sites; 11 word(s) outside name it, 1 through a table a literal itself names |
| 12 | `0x7434B0..0x743E68` | 2488 | `no-consumer` | no consumer: 0 literal sites; 23 word(s) outside name it, 0 through a table a literal itself names |
| 13 | `0x21FC4C..0x2205F8` | 2476 | `raw-labeled` | raw-labeled, R-RAW-001: 5 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 4 |
| 14 | `0x749F1C..0x74A820` | 2308 | `no-consumer` | no consumer: 0 literal sites; 30 word(s) outside name it, 0 through a table a literal itself names |
| 15 | `0x745798..0x74606C` | 2260 | `no-consumer` | no consumer: 0 literal sites; 32 word(s) outside name it, 0 through a table a literal itself names |
| 16 | `0x1A8110..0x1A89E0` | 2256 | `no-consumer` | no consumer: 0 literal sites; 11 word(s) outside name it, 1 through a table a literal itself names |
| 17 | `0x2AC150..0x2ACA20` | 2256 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 18 | `0x274598..0x274E4C` | 2228 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 3 - at or below the null (P-418) |
| 19 | `0x262F74..0x2637F4` | 2176 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 20 | `0x73A134..0x73A9B4` | 2176 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 3 - at or below the null (P-418) |
| 21 | `0x735E34..0x7366A8` | 2164 | `no-consumer` | no consumer: 0 literal sites; 20 word(s) outside name it, 0 through a table a literal itself names |
| 22 | `0x23275C..0x232FBC` | 2144 | `no-consumer` | no consumer: 0 literal sites; 8 word(s) outside name it, 0 through a table a literal itself names |
| 23 | `0x23048C..0x230CB4` | 2088 | `no-consumer` | no consumer: 0 literal sites; 13 word(s) outside name it, 0 through a table a literal itself names |
| 24 | `0x17A9AC..0x17B1B0` | 2052 | `raw-labeled` | raw-labeled, R-RAW-001: 86 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 3 |
| 25 | `0x18B31C..0x18BAE4` | 1992 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 26 | `0x26F6C0..0x26FE2C` | 1900 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 27 | `0x263E94..0x2645FC` | 1896 | `no-consumer` | no consumer: 0 literal sites; 11 word(s) outside name it, 0 through a table a literal itself names |
| 28 | `0x18C638..0x18CD1C` | 1764 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 1 through a table a literal itself names |
| 29 | `0x1E24F4..0x1E2BD8` | 1764 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 2 through a table a literal itself names |
| 30 | `0x73CE0C..0x73D490` | 1668 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 3 - at or below the null (P-418) |
| 31 | `0x18D808..0x18DE84` | 1660 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 32 | `0x19FC04..0x1A0264` | 1632 | `no-consumer` | no consumer: 0 literal sites; 9 word(s) outside name it, 0 through a table a literal itself names |
| 33 | `0x277C08..0x278258` | 1616 | `no-consumer` | no consumer: 0 literal sites; 7 word(s) outside name it, 24 through a table a literal itself names |
| 34 | `0x21E878..0x21EEC0` | 1608 | `no-consumer` | no consumer: 2 singleton literal site(s) (0 multi-site), same-size control max 4 - at or below the null (P-418) |
| 35 | `0x1837DC..0x183DFC` | 1568 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 2 through a table a literal itself names |
| 36 | `0x1E41E0..0x1E4800` | 1568 | `raw-labeled` | raw-labeled, R-RAW-001: 6 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 3 |
| 37 | `0x7473E4..0x74798C` | 1448 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 3 - at or below the null (P-418) |
| 38 | `0x236470..0x236A10` | 1440 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 39 | `0x225FB8..0x226514` | 1372 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 4 - at or below the null (P-418) |
| 40 | `0x1A90A8..0x1A95F0` | 1352 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 4 - at or below the null (P-418) |
| 41 | `0x74CB04..0x74D044` | 1344 | `raw-labeled` | raw-labeled, R-RAW-001: 11 literal site(s) outside the row, 2 multi-site literal(s), same-size control max 4 |
| 42 | `0x6B82DC..0x6B880C` | 1328 | `raw-labeled` | raw-labeled, R-RAW-001: 83 literal site(s) outside the row, 22 multi-site literal(s), same-size control max 4 |
| 43 | `0x732B20..0x733040` | 1312 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 4 - at or below the null (P-418) |
| 44 | `0x180694..0x180B90` | 1276 | `no-consumer` | no consumer: 2 singleton literal site(s) (0 multi-site), same-size control max 3 - at or below the null (P-418) |
| 45 | `0x1EA2D8..0x1EA794` | 1212 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 2 through a table a literal itself names |
| 46 | `0x74980C..0x749CBC` | 1200 | `no-consumer` | no consumer: 0 literal sites; 16 word(s) outside name it, 0 through a table a literal itself names |
| 47 | `0x28943C..0x2898C0` | 1156 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 48 | `0x744EF0..0x74535C` | 1132 | `no-consumer` | no consumer: 0 literal sites; 13 word(s) outside name it, 0 through a table a literal itself names |
| 49 | `0x279ABC..0x279F24` | 1128 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 3 - at or below the null (P-418) |
| 50 | `0x73C04C..0x73C4B4` | 1128 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 3 - at or below the null (P-418) |
| 51 | `0x190240..0x190688` | 1096 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 0 through a table a literal itself names |
| 52 | `0x74ACB4..0x74B0F8` | 1092 | `no-consumer` | no consumer: 0 literal sites; 14 word(s) outside name it, 0 through a table a literal itself names |
| 53 | `0x747E64..0x74829C` | 1080 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 5 - at or below the null (P-418) |
| 54 | `0x746844..0x746C74` | 1072 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 4 - at or below the null (P-418) |
| 55 | `0x17BCCC..0x17C0F4` | 1064 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 1 through a table a literal itself names |
| 56 | `0x215F20..0x216324` | 1028 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 3 through a table a literal itself names |
| 57 | `0x7491D0..0x7495C8` | 1016 | `no-consumer` | no consumer: 0 literal sites; 13 word(s) outside name it, 0 through a table a literal itself names |
| 58 | `0x182054..0x182444` | 1008 | `no-consumer` | no consumer: 0 literal sites; 16 word(s) outside name it, 3 through a table a literal itself names |
| 59 | `0x733C9C..0x734084` | 1000 | `no-consumer` | no consumer: 0 literal sites; 11 word(s) outside name it, 0 through a table a literal itself names |
| 60 | `0x1886AC..0x188A8C` | 992 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 61 | `0x1847B0..0x184B8C` | 988 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 2 through a table a literal itself names |
| 62 | `0x17DAB0..0x17DE74` | 964 | `no-consumer` | no consumer: 0 literal sites; 9 word(s) outside name it, 2 through a table a literal itself names |
| 63 | `0x17C700..0x17CAA8` | 936 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 64 | `0x189C1C..0x189FAC` | 912 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 3 through a table a literal itself names |
| 65 | `0x1BFAA4..0x1BFE30` | 908 | `raw-labeled` | raw-labeled, R-RAW-001: 6 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 3 |
| 66 | `0x21DD88..0x21E108` | 896 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 67 | `0x1C1630..0x1C199C` | 876 | `no-consumer` | no consumer: 0 literal sites; 8 word(s) outside name it, 0 through a table a literal itself names |
| 68 | `0x22F748..0x22FAAC` | 868 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 3 - at or below the null (P-418) |
| 69 | `0x73B4C4..0x73B800` | 828 | `no-consumer` | no consumer: 0 literal sites; 9 word(s) outside name it, 0 through a table a literal itself names |
| 70 | `0x1FB060..0x1FB380` | 800 | `no-consumer` | no consumer: 0 literal sites; 7 word(s) outside name it, 0 through a table a literal itself names |
| 71 | `0x182DCC..0x1830E0` | 788 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 72 | `0x1C7C48..0x1C7F5C` | 788 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 3 - at or below the null (P-418) |
| 73 | `0x285C18..0x285F28` | 784 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 74 | `0x73FE00..0x7400E0` | 736 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 2 - at or below the null (P-418) |
| 75 | `0x2113E4..0x2116B8` | 724 | `no-consumer` | no consumer: 0 literal sites; 7 word(s) outside name it, 2 through a table a literal itself names |
| 76 | `0x1BDC54..0x1BDF24` | 720 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 77 | `0x19AEAC..0x19B178` | 716 | `raw-labeled` | raw-labeled, R-RAW-001: 5 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 2 |
| 78 | `0x3BBBB0..0x3BBE70` | 704 | `no-consumer` | no consumer: 2 singleton literal site(s) (0 multi-site), same-size control max 2 - at or below the null (P-418) |
| 79 | `0x26561C..0x2658D8` | 700 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 4 through a table a literal itself names |
| 80 | `0x74BCF8..0x74BFB4` | 700 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 81 | `0x26512C..0x2653E4` | 696 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 1 through a table a literal itself names |
| 82 | `0x260EA8..0x261130` | 648 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 1 |
| 83 | `0x667F64..0x6681EC` | 648 | `no-consumer` | no consumer: 0 literal sites; 21 word(s) outside name it, 0 through a table a literal itself names |
| 84 | `0x51C618..0x51C898` | 640 | `no-consumer` | no consumer: 0 literal sites; 22 word(s) outside name it, 0 through a table a literal itself names |
| 85 | `0x52781C..0x527A7C` | 608 | `no-consumer` | no consumer: 0 literal sites; 20 word(s) outside name it, 0 through a table a literal itself names |
| 86 | `0x734FD4..0x735210` | 572 | `no-consumer` | no consumer: 0 literal sites; 9 word(s) outside name it, 0 through a table a literal itself names |
| 87 | `0x674154..0x674384` | 560 | `no-consumer` | no consumer: 0 literal sites; 19 word(s) outside name it, 1 through a table a literal itself names |
| 88 | `0x740440..0x740654` | 532 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 0 through a table a literal itself names |
| 89 | `0x1AF324..0x1AF534` | 528 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 2 through a table a literal itself names |
| 90 | `0x2133A4..0x2135B4` | 528 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 91 | `0x73E120..0x73E31C` | 508 | `no-consumer` | no consumer: 0 literal sites; 10 word(s) outside name it, 0 through a table a literal itself names |
| 92 | `0x253C00..0x253DE4` | 484 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 93 | `0x742C48..0x742E18` | 464 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 0 through a table a literal itself names |
| 94 | `0x17D1C8..0x17D390` | 456 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 95 | `0x17E44C..0x17E60C` | 448 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 96 | `0x1C3A70..0x1C3C30` | 448 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 6 through a table a literal itself names |
| 97 | `0x4BA1FC..0x4BA3B4` | 440 | `no-consumer` | no consumer: 0 literal sites; 23 word(s) outside name it, 0 through a table a literal itself names |
| 98 | `0x259A88..0x259C3C` | 436 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 99 | `0x73DDD4..0x73DF88` | 436 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 100 | `0x1D25E8..0x1D2798` | 432 | `raw-labeled` | raw-labeled, R-RAW-001: 5 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 1 |
| 101 | `0x532C1C..0x532DCC` | 432 | `no-consumer` | no consumer: 0 literal sites; 18 word(s) outside name it, 0 through a table a literal itself names |
| 102 | `0x17F330..0x17F4DC` | 428 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 103 | `0x1BE0F0..0x1BE298` | 424 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 104 | `0x2511A4..0x25133C` | 408 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 105 | `0x748AC8..0x748C58` | 400 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 106 | `0x74B8B4..0x74BA44` | 400 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 0 through a table a literal itself names |
| 107 | `0x1B2DAC..0x1B2F38` | 396 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 108 | `0x1C0CB4..0x1C0E38` | 388 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 109 | `0x74AA98..0x74AC18` | 384 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 0 through a table a literal itself names |
| 110 | `0x258514..0x25867C` | 360 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 111 | `0x25FAA0..0x25FC08` | 360 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 112 | `0x19C744..0x19C8A8` | 356 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 113 | `0x267998..0x267AFC` | 356 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 114 | `0x7357F0..0x735944` | 340 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 0 through a table a literal itself names |
| 115 | `0x2119F8..0x211B48` | 336 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 2 through a table a literal itself names |
| 116 | `0x2176BC..0x217808` | 332 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 117 | `0x25C6E4..0x25C830` | 332 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 118 | `0x73AF04..0x73B050` | 332 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 119 | `0x74BB40..0x74BC88` | 328 | `no-consumer` | no consumer: 0 literal sites; 7 word(s) outside name it, 0 through a table a literal itself names |
| 120 | `0x73C998..0x73CAD8` | 320 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 121 | `0x1D93EC..0x1D9524` | 312 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 122 | `0x74312C..0x743264` | 312 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 123 | `0x6B801C..0x6B814C` | 304 | `raw-labeled` | raw-labeled, R-RAW-001: 107 literal site(s) outside the row, 14 multi-site literal(s), same-size control max 1 |
| 124 | `0x1C2FF4..0x1C3120` | 300 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 0 through a table a literal itself names |
| 125 | `0x23220C..0x232334` | 296 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 126 | `0x1C6064..0x1C6188` | 292 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 127 | `0x1C4DC4..0x1C4EE4` | 288 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 128 | `0x249D80..0x249EA0` | 288 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 129 | `0x26B14C..0x26B26C` | 288 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 130 | `0x29D074..0x29D194` | 288 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 131 | `0x748668..0x748788` | 288 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 132 | `0x1F5028..0x1F5144` | 284 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 2 through a table a literal itself names |
| 133 | `0x740B98..0x740CA8` | 272 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 134 | `0x1911D8..0x1912E4` | 268 | `raw-labeled` | raw-labeled, R-RAW-001: 14 literal site(s) outside the row, 2 multi-site literal(s), same-size control max 1 |
| 135 | `0x26BB94..0x26BC9C` | 264 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 136 | `0x2788CC..0x2789D4` | 264 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 137 | `0x279120..0x279228` | 264 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 138 | `0x74C92C..0x74CA2C` | 256 | `raw-labeled` | raw-labeled, R-RAW-001: 3 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 2 |
| 139 | `0x207E6C..0x207F68` | 252 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 140 | `0x7347BC..0x7348B0` | 244 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 141 | `0x1B1CF8..0x1B1DE8` | 240 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 142 | `0x24DCC0..0x24DDB0` | 240 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 143 | `0x28C000..0x28C0F0` | 240 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 144 | `0x23FF58..0x240044` | 236 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 0 through a table a literal itself names |
| 145 | `0x283F20..0x28400C` | 236 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 146 | `0x2065FC..0x2066E4` | 232 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 2 |
| 147 | `0x240AD0..0x240BB8` | 232 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 1 through a table a literal itself names |
| 148 | `0x748F34..0x74901C` | 232 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 149 | `0x2087B0..0x208894` | 228 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 150 | `0x24451C..0x244600` | 228 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 2 through a table a literal itself names |
| 151 | `0x1FC5B0..0x1FC690` | 224 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 2 |
| 152 | `0x1FD1F0..0x1FD2D0` | 224 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 153 | `0x22C11C..0x22C1F4` | 216 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 154 | `0x25066C..0x250744` | 216 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 155 | `0x28B6E8..0x28B7C0` | 216 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 156 | `0x29DD8C..0x29DE64` | 216 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 2 - at or below the null (P-418) |
| 157 | `0x3C33F8..0x3C34D0` | 216 | `raw-labeled` | raw-labeled, R-RAW-001: 14 literal site(s) outside the row, 2 multi-site literal(s), same-size control max 2 |
| 158 | `0x734C9C..0x734D74` | 216 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 159 | `0x73B1D8..0x73B2AC` | 212 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 160 | `0x74C58C..0x74C660` | 212 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 161 | `0x1C28D4..0x1C29A4` | 208 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 162 | `0x1C4348..0x1C4418` | 208 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 2 - at or below the null (P-418) |
| 163 | `0x206AC8..0x206B98` | 208 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 164 | `0x207108..0x2071D8` | 208 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 165 | `0x27F9B0..0x27FA80` | 208 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 166 | `0x73CBB4..0x73CC84` | 208 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 167 | `0x74098C..0x740A5C` | 208 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 168 | `0x1F880C..0x1F88D8` | 204 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 2 |
| 169 | `0x742B20..0x742BEC` | 204 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 170 | `0x28EC28..0x28ECF0` | 200 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 171 | `0x73BE30..0x73BEF4` | 196 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 172 | `0x1CDF74..0x1CE034` | 192 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 173 | `0x1CEBD4..0x1CEC94` | 192 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 1 through a table a literal itself names |
| 174 | `0x2025C0..0x202680` | 192 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 175 | `0x2075C0..0x207680` | 192 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 176 | `0x1CA528..0x1CA5E4` | 188 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 177 | `0x23BF5C..0x23C018` | 188 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 178 | `0x27E288..0x27E344` | 188 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 179 | `0x286884..0x286940` | 188 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 180 | `0x195C3C..0x195CF4` | 184 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 181 | `0x20537C..0x205434` | 184 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 1 through a table a literal itself names |
| 182 | `0x23A4A8..0x23A560` | 184 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 183 | `0x23AF80..0x23B038` | 184 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 184 | `0x287508..0x2875C0` | 184 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 185 | `0x27A4A0..0x27A550` | 176 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 186 | `0x1A1290..0x1A133C` | 172 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 187 | `0x24BF54..0x24C000` | 172 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 188 | `0x254CF4..0x254DA0` | 172 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 189 | `0x1AF7CC..0x1AF874` | 168 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 190 | `0x1F9518..0x1F95C0` | 168 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 191 | `0x216F28..0x216FD0` | 168 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 192 | `0x225024..0x2250CC` | 168 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 193 | `0x23D3F0..0x23D498` | 168 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 194 | `0x26C8D4..0x26C97C` | 168 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 195 | `0x2912F4..0x29139C` | 168 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 196 | `0x29ECA4..0x29ED4C` | 168 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 197 | `0x2B2998..0x2B2A40` | 168 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 198 | `0x735C74..0x735D1C` | 168 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 199 | `0x733AE8..0x733B8C` | 164 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 200 | `0x1BF08C..0x1BF12C` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 201 | `0x1C6B90..0x1C6C30` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 202 | `0x1C88D4..0x1C8974` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 203 | `0x1C91D8..0x1C9278` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 204 | `0x1C9B48..0x1C9BE8` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 205 | `0x1CB0CC..0x1CB16C` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 206 | `0x1CE30C..0x1CE3AC` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 207 | `0x201A70..0x201B10` | 160 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 208 | `0x23805C..0x2380FC` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 209 | `0x23881C..0x2388BC` | 160 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 210 | `0x23C8CC..0x23C96C` | 160 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 211 | `0x23E0B0..0x23E150` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 212 | `0x26A6D8..0x26A778` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 213 | `0x275FE8..0x276088` | 160 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 214 | `0x27C04C..0x27C0EC` | 160 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 215 | `0x27C614..0x27C6B4` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 216 | `0x27CB28..0x27CBC8` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 217 | `0x27D454..0x27D4F4` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 218 | `0x27F088..0x27F128` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 219 | `0x280AD8..0x280B78` | 160 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 2 through a table a literal itself names |
| 220 | `0x2818CC..0x28196C` | 160 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 0 through a table a literal itself names |
| 221 | `0x281E18..0x281EB8` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 222 | `0x282AB4..0x282B54` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 223 | `0x283414..0x2834B4` | 160 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 224 | `0x2845D8..0x284678` | 160 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 225 | `0x284AE0..0x284B80` | 160 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 226 | `0x1E6E2C..0x1E6EC8` | 156 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 227 | `0x1EC044..0x1EC0E0` | 156 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 228 | `0x1F0F5C..0x1F0FF8` | 156 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 229 | `0x2083C0..0x20845C` | 156 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 230 | `0x276D40..0x276DDC` | 156 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 231 | `0x1AFFA8..0x1B0040` | 152 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 232 | `0x734A5C..0x734AF4` | 152 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 233 | `0x19D5DC..0x19D66C` | 144 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 234 | `0x1D1298..0x1D1328` | 144 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 235 | `0x1DA7B0..0x1DA840` | 144 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 236 | `0x217D30..0x217DC0` | 144 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 237 | `0x235A10..0x235AA0` | 144 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 238 | `0x24FD48..0x24FDD8` | 144 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 1 through a table a literal itself names |
| 239 | `0x291C50..0x291CE0` | 144 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 240 | `0x2927A4..0x292834` | 144 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 241 | `0x2933E4..0x293474` | 144 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 242 | `0x2948D8..0x294968` | 144 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 243 | `0x20270C..0x202798` | 140 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 244 | `0x203210..0x20329C` | 140 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 245 | `0x2346D0..0x23475C` | 140 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 1 |
| 246 | `0x251F4C..0x251FD8` | 140 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 247 | `0x252048..0x2520D4` | 140 | `raw-labeled` | raw-labeled, R-RAW-001: 4 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 1 |
| 248 | `0x295BCC..0x295C58` | 140 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 249 | `0x20630C..0x206394` | 136 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 1 |
| 250 | `0x256EAC..0x256F34` | 136 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 251 | `0x1D3D38..0x1D3DBC` | 132 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 252 | `0x22EA1C..0x22EAA0` | 132 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 253 | `0x2393F0..0x239474` | 132 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 1 |
| 254 | `0x23D810..0x23D894` | 132 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 1 |
| 255 | `0x241C90..0x241D14` | 132 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 256 | `0x249EBC..0x249F40` | 132 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 257 | `0x2805E4..0x280668` | 132 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 258 | `0x748860..0x7488E4` | 132 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 259 | `0x1AAC54..0x1AACD4` | 128 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 260 | `0x1B037C..0x1B03FC` | 128 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 261 | `0x1E11E8..0x1E1268` | 128 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 262 | `0x1E7898..0x1E7918` | 128 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 263 | `0x1E900C..0x1E908C` | 128 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 264 | `0x1EDDA8..0x1EDE28` | 128 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 265 | `0x1EF1A8..0x1EF228` | 128 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 266 | `0x1F1E44..0x1F1EC4` | 128 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 1 through a table a literal itself names |
| 267 | `0x1F31F8..0x1F3278` | 128 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 268 | `0x74C804..0x74C884` | 128 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 269 | `0x1DAC90..0x1DAD0C` | 124 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 270 | `0x215100..0x21517C` | 124 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 271 | `0x1DEB1C..0x1DEB94` | 120 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 272 | `0x1F63B8..0x1F6430` | 120 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 273 | `0x205C2C..0x205CA4` | 120 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 2 through a table a literal itself names |
| 274 | `0x209B4C..0x209BC4` | 120 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 275 | `0x216718..0x216790` | 120 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 1 through a table a literal itself names |
| 276 | `0x218E6C..0x218EE4` | 120 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 277 | `0x2246E0..0x224758` | 120 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 278 | `0x235710..0x235788` | 120 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 279 | `0x24F4E4..0x24F55C` | 120 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 280 | `0x25C338..0x25C3B0` | 120 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 281 | `0x273A40..0x273AB4` | 116 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 282 | `0x1BB010..0x1BB080` | 112 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 283 | `0x1D482C..0x1D489C` | 112 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 284 | `0x1D606C..0x1D60DC` | 112 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 285 | `0x2048B0..0x204920` | 112 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 286 | `0x204ECC..0x204F3C` | 112 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 287 | `0x205F08..0x205F78` | 112 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 288 | `0x2079CC..0x207A3C` | 112 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 289 | `0x20D298..0x20D308` | 112 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 290 | `0x20EF60..0x20EFD0` | 112 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 291 | `0x219044..0x2190B4` | 112 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 292 | `0x251B94..0x251C04` | 112 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 293 | `0x264D50..0x264DC0` | 112 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 1 through a table a literal itself names |
| 294 | `0x211E08..0x211E74` | 108 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 1 through a table a literal itself names |
| 295 | `0x1EA9DC..0x1EAA44` | 104 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 296 | `0x21AE40..0x21AEA8` | 104 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 1 through a table a literal itself names |
| 297 | `0x21D4D4..0x21D53C` | 104 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 298 | `0x46D2EC..0x46D354` | 104 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 299 | `0x6F3BC8..0x6F3C30` | 104 | `no-consumer` | no consumer: 0 literal sites; 13 word(s) outside name it, 3 through a table a literal itself names |
| 300 | `0x1A6890..0x1A68F4` | 100 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 301 | `0x7489D4..0x748A38` | 100 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 302 | `0x17F034..0x17F094` | 96 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 303 | `0x19F7F4..0x19F854` | 96 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 304 | `0x1D4E44..0x1D4EA4` | 96 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 0 |
| 305 | `0x1D7174..0x1D71D4` | 96 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 306 | `0x1D7DA8..0x1D7E08` | 96 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 307 | `0x1DD900..0x1DD960` | 96 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 308 | `0x204CC8..0x204D28` | 96 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 3 through a table a literal itself names |
| 309 | `0x2091A0..0x209200` | 96 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 310 | `0x2390FC..0x23915C` | 96 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 311 | `0x280378..0x2803D8` | 96 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 312 | `0x288F00..0x288F60` | 96 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 313 | `0x289DE4..0x289E44` | 96 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 314 | `0x29478C..0x2947EC` | 96 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 315 | `0x4ADD30..0x4ADD90` | 96 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 316 | `0x7408D8..0x740938` | 96 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 317 | `0x749118..0x749178` | 96 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 318 | `0x1FC928..0x1FC980` | 88 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 319 | `0x26D48C..0x26D4E4` | 88 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 320 | `0x26DAA0..0x26DAF8` | 88 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 321 | `0x26E074..0x26E0CC` | 88 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 322 | `0x26E678..0x26E6D0` | 88 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 323 | `0x26EC80..0x26ECD8` | 88 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 324 | `0x272D48..0x272DA0` | 88 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 325 | `0x1AB430..0x1AB484` | 84 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 326 | `0x1B71B8..0x1B720C` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 327 | `0x1B8818..0x1B886C` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 328 | `0x1B9BB8..0x1B9C0C` | 84 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 0 |
| 329 | `0x1D1C74..0x1D1CC8` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 330 | `0x1D68F4..0x1D6948` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 331 | `0x1DBCE0..0x1DBD34` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 332 | `0x209498..0x2094EC` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 333 | `0x20ADF8..0x20AE4C` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 334 | `0x20EB08..0x20EB5C` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 335 | `0x217F88..0x217FDC` | 84 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 336 | `0x21C070..0x21C0C4` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 337 | `0x25464C..0x2546A0` | 84 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 338 | `0x26CE28..0x26CE7C` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 339 | `0x28AE60..0x28AEB4` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 340 | `0x28BB54..0x28BBA8` | 84 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 341 | `0x73198C..0x7319E0` | 84 | `raw-labeled` | raw-labeled, R-RAW-001: 17 literal site(s) outside the row, 3 multi-site literal(s), same-size control max 0 |
| 342 | `0x17ECD4..0x17ED24` | 80 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 343 | `0x17FB64..0x17FBB4` | 80 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 344 | `0x181348..0x181398` | 80 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 345 | `0x181448..0x181498` | 80 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 2 through a table a literal itself names |
| 346 | `0x181548..0x181598` | 80 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 347 | `0x1A5B7C..0x1A5BCC` | 80 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 348 | `0x1B1A08..0x1B1A58` | 80 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 349 | `0x1F2100..0x1F2150` | 80 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 1 through a table a literal itself names |
| 350 | `0x20E490..0x20E4E0` | 80 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 351 | `0x296D4C..0x296D9C` | 80 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 352 | `0x187BC8..0x187C14` | 76 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 353 | `0x189334..0x189380` | 76 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 354 | `0x271EC4..0x271F10` | 76 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 355 | `0x18A07C..0x18A0C4` | 72 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 356 | `0x190088..0x1900D0` | 72 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 357 | `0x196FA8..0x196FF0` | 72 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 358 | `0x1AA968..0x1AA9B0` | 72 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 359 | `0x1D45F0..0x1D4638` | 72 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 360 | `0x1D9D54..0x1D9D9C` | 72 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 361 | `0x1E7B8C..0x1E7BD4` | 72 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 362 | `0x1F40D8..0x1F4120` | 72 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 363 | `0x1F8548..0x1F8590` | 72 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 364 | `0x226BFC..0x226C44` | 72 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 365 | `0x228A20..0x228A68` | 72 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 366 | `0x22D930..0x22D978` | 72 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 367 | `0x241924..0x24196C` | 72 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 368 | `0x24720C..0x247254` | 72 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 369 | `0x25440C..0x254454` | 72 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 370 | `0x26A410..0x26A458` | 72 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 371 | `0x26ABC0..0x26AC08` | 72 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 372 | `0x275C60..0x275CA8` | 72 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 373 | `0x27723C..0x277284` | 72 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 374 | `0x277950..0x277998` | 72 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 375 | `0x2980F8..0x298140` | 72 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 376 | `0x597DB0..0x597DF0` | 64 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 3 through a table a literal itself names |
| 377 | `0x5BFC44..0x5BFC84` | 64 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 378 | `0x192364..0x1923A0` | 60 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 379 | `0x2709C4..0x270A00` | 60 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 380 | `0x19470C..0x194744` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 381 | `0x1971D0..0x197208` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 382 | `0x19807C..0x1980B4` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 383 | `0x198EF0..0x198F28` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 384 | `0x1A539C..0x1A53D4` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 385 | `0x1B0DCC..0x1B0E04` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 386 | `0x1B3A70..0x1B3AA8` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 387 | `0x1B4488..0x1B44C0` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 388 | `0x1B4E28..0x1B4E60` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 389 | `0x1B5790..0x1B57C8` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 390 | `0x1B618C..0x1B61C4` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 391 | `0x1B6810..0x1B6848` | 56 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 392 | `0x1B7BFC..0x1B7C34` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 393 | `0x1BA1D8..0x1BA210` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 394 | `0x1CF9D4..0x1CFA0C` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 395 | `0x1D0184..0x1D01BC` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 396 | `0x1D09E4..0x1D0A1C` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 397 | `0x1D146C..0x1D14A4` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 398 | `0x1D5480..0x1D54B8` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 399 | `0x1D5A9C..0x1D5AD4` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 400 | `0x1D857C..0x1D85B4` | 56 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 1 |
| 401 | `0x1D9674..0x1D96AC` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 402 | `0x1DB374..0x1DB3AC` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 403 | `0x1DCD68..0x1DCDA0` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 404 | `0x1E3780..0x1E37B8` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 405 | `0x1E7D58..0x1E7D90` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 406 | `0x1ECA40..0x1ECA78` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 407 | `0x1EFC4C..0x1EFC84` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 408 | `0x1F97EC..0x1F9824` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 409 | `0x1F9CD0..0x1F9D08` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 410 | `0x1FA458..0x1FA490` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 411 | `0x1FA55C..0x1FA594` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 412 | `0x1FBC28..0x1FBC60` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 413 | `0x1FCE38..0x1FCE70` | 56 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 414 | `0x1FCF3C..0x1FCF74` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 415 | `0x1FD39C..0x1FD3D4` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 416 | `0x1FE6CC..0x1FE704` | 56 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 417 | `0x1FF618..0x1FF650` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 418 | `0x1FF708..0x1FF740` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 419 | `0x20A250..0x20A288` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 420 | `0x20A640..0x20A678` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 421 | `0x20B24C..0x20B284` | 56 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 422 | `0x20B998..0x20B9D0` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 423 | `0x20C0C0..0x20C0F8` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 424 | `0x20C40C..0x20C444` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 425 | `0x20CD58..0x20CD90` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 426 | `0x20DB9C..0x20DBD4` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 427 | `0x20E090..0x20E0C8` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 428 | `0x2103DC..0x210414` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 429 | `0x210A54..0x210A8C` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 430 | `0x2121E4..0x21221C` | 56 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 431 | `0x2128C8..0x212900` | 56 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 432 | `0x213CFC..0x213D34` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 433 | `0x21426C..0x2142A4` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 434 | `0x214964..0x21499C` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 435 | `0x217150..0x217188` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 436 | `0x2199A4..0x2199DC` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 437 | `0x219DB0..0x219DE8` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 438 | `0x21B5A8..0x21B5E0` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 439 | `0x21CA44..0x21CA7C` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 440 | `0x2478AC..0x2478E4` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 441 | `0x248070..0x2480A8` | 56 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 442 | `0x255C64..0x255C9C` | 56 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 443 | `0x2560D4..0x25610C` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 444 | `0x2639F8..0x263A30` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 445 | `0x271258..0x271290` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 446 | `0x271948..0x271980` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 447 | `0x2725B8..0x2725F0` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 448 | `0x27A900..0x27A938` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 449 | `0x27AE9C..0x27AED4` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 450 | `0x290560..0x290598` | 56 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 451 | `0x298324..0x29835C` | 56 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 452 | `0x299698..0x2996D0` | 56 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 453 | `0x1F8C1C..0x1F8C50` | 52 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 454 | `0x1FA008..0x1FA03C` | 52 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 455 | `0x1FA358..0x1FA38C` | 52 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 456 | `0x1FA824..0x1FA858` | 52 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 1 through a table a literal itself names |
| 457 | `0x1FAB3C..0x1FAB70` | 52 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 1 through a table a literal itself names |
| 458 | `0x1FCC60..0x1FCC94` | 52 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 459 | `0x1FCD38..0x1FCD6C` | 52 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 460 | `0x1FD018..0x1FD04C` | 52 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 461 | `0x1FD0F0..0x1FD124` | 52 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 462 | `0x1FD478..0x1FD4AC` | 52 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 463 | `0x1FDEA8..0x1FDEDC` | 52 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 1 through a table a literal itself names |
| 464 | `0x1FEF08..0x1FEF3C` | 52 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 1 through a table a literal itself names |
| 465 | `0x233A34..0x233A68` | 52 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 466 | `0x732350..0x732384` | 52 | `raw-labeled` | raw-labeled, R-RAW-001: 18 literal site(s) outside the row, 2 multi-site literal(s), same-size control max 1 |
| 467 | `0x17CF5C..0x17CF8C` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 468 | `0x17E20C..0x17E23C` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 469 | `0x1B0CCC..0x1B0CFC` | 48 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 470 | `0x1CF63C..0x1CF66C` | 48 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 2 through a table a literal itself names |
| 471 | `0x1D08EC..0x1D091C` | 48 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 1 through a table a literal itself names |
| 472 | `0x1E6588..0x1E65B8` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 473 | `0x1F7020..0x1F7050` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 474 | `0x2041B0..0x2041E0` | 48 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 475 | `0x21F99C..0x21F9CC` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 476 | `0x223040..0x223070` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 477 | `0x226848..0x226878` | 48 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 478 | `0x227120..0x227150` | 48 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 479 | `0x227ADC..0x227B0C` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 480 | `0x228684..0x2286B4` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 481 | `0x2291D8..0x229208` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 482 | `0x22A2FC..0x22A32C` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 483 | `0x22A768..0x22A798` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 484 | `0x22DF58..0x22DF88` | 48 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 485 | `0x22EF54..0x22EF84` | 48 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 1 through a table a literal itself names |
| 486 | `0x22F674..0x22F6A4` | 48 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 2 through a table a literal itself names |
| 487 | `0x22FB10..0x22FB40` | 48 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 488 | `0x23BD7C..0x23BDAC` | 48 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 489 | `0x255B30..0x255B60` | 48 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 3 through a table a literal itself names |
| 490 | `0x260D50..0x260D80` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 491 | `0x27BD78..0x27BDA8` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 492 | `0x28ABD4..0x28AC04` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 493 | `0x28FAAC..0x28FADC` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 494 | `0x2AE058..0x2AE088` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 495 | `0x2B1F04..0x2B1F34` | 48 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 496 | `0x1F6750..0x1F677C` | 44 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 497 | `0x246B08..0x246B34` | 44 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 2 through a table a literal itself names |
| 498 | `0x74CA3C..0x74CA60` | 36 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 0 through a table a literal itself names |
| 499 | `0x74CAA0..0x74CAC4` | 36 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 0 through a table a literal itself names |
| 500 | `0x74CA70..0x74CA90` | 32 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 3 through a table a literal itself names |
| 501 | `0x74CAD4..0x74CAF4` | 32 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 0 through a table a literal itself names |
| 502 | `0x193A10..0x193A2C` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 503 | `0x199CF4..0x199D10` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 504 | `0x19B658..0x19B674` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 505 | `0x1A4490..0x1A44AC` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 506 | `0x1B1FF4..0x1B2010` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 507 | `0x1CED8C..0x1CEDA8` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 508 | `0x1D2C28..0x1D2C44` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 509 | `0x1D9FE0..0x1D9FFC` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 510 | `0x1DDBE4..0x1DDC00` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 511 | `0x1DEF58..0x1DEF74` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 512 | `0x1DFF10..0x1DFF2C` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 513 | `0x1F7AF4..0x1F7B10` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 514 | `0x1FF490..0x1FF4AC` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 515 | `0x1FF954..0x1FF970` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 516 | `0x20A908..0x20A924` | 28 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 517 | `0x20CA54..0x20CA70` | 28 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 518 | `0x20D834..0x20D850` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 519 | `0x2110DC..0x2110F8` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 520 | `0x215938..0x215954` | 28 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 521 | `0x2169FC..0x216A18` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 522 | `0x247388..0x2473A4` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 523 | `0x24FED0..0x24FEEC` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 524 | `0x250A08..0x250A24` | 28 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 525 | `0x253908..0x253924` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 526 | `0x258B9C..0x258BB8` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 527 | `0x2590F0..0x25910C` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 528 | `0x25E31C..0x25E338` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 529 | `0x2607B4..0x2607D0` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 530 | `0x26B808..0x26B824` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 531 | `0x26C29C..0x26C2B8` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 532 | `0x270D38..0x270D54` | 28 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 533 | `0x277374..0x277390` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 534 | `0x28A1C8..0x28A1E4` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 535 | `0x28A6F4..0x28A710` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 536 | `0x28C4B4..0x28C4D0` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 537 | `0x28FBE4..0x28FC00` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 538 | `0x297C68..0x297C84` | 28 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 1 through a table a literal itself names |
| 539 | `0x29B478..0x29B494` | 28 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 540 | `0x7325E8..0x732604` | 28 | `raw-labeled` | raw-labeled, R-RAW-001: 5 literal site(s) outside the row, 1 multi-site literal(s), same-size control max 1 |
| 541 | `0x17A7C8..0x17A7E0` | 24 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 2 through a table a literal itself names |
| 542 | `0x17BB28..0x17BB40` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 2 through a table a literal itself names |
| 543 | `0x1945EC..0x194604` | 24 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 2 through a table a literal itself names |
| 544 | `0x199B54..0x199B6C` | 24 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 2 through a table a literal itself names |
| 545 | `0x19AE34..0x19AE4C` | 24 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 546 | `0x19C368..0x19C380` | 24 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 547 | `0x1A4F18..0x1A4F30` | 24 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 548 | `0x1A6384..0x1A639C` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 549 | `0x1AFEA8..0x1AFEC0` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 550 | `0x1B6FEC..0x1B7004` | 24 | `no-consumer` | no consumer: 0 literal sites; 5 word(s) outside name it, 0 through a table a literal itself names |
| 551 | `0x1C2EF4..0x1C2F0C` | 24 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 1 through a table a literal itself names |
| 552 | `0x1C7BE8..0x1C7C00` | 24 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 553 | `0x1DB334..0x1DB34C` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 554 | `0x1DCCC8..0x1DCCE0` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 555 | `0x1E36CC..0x1E36E4` | 24 | `no-consumer` | no consumer: 0 literal sites; 6 word(s) outside name it, 2 through a table a literal itself names |
| 556 | `0x1F79F4..0x1F7A0C` | 24 | `no-consumer` | no consumer: 0 literal sites; 11 word(s) outside name it, 2 through a table a literal itself names |
| 557 | `0x1FF3F0..0x1FF408` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 558 | `0x2003FC..0x200414` | 24 | `no-consumer` | no consumer: 0 literal sites; 1 word(s) outside name it, 2 through a table a literal itself names |
| 559 | `0x200F88..0x200FA0` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 560 | `0x20D674..0x20D68C` | 24 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 561 | `0x22766C..0x227684` | 24 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 562 | `0x227E8C..0x227EA4` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 563 | `0x228154..0x22816C` | 24 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 564 | `0x22B178..0x22B190` | 24 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 565 | `0x22BA74..0x22BA8C` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 566 | `0x22CF10..0x22CF28` | 24 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 567 | `0x22E1D8..0x22E1F0` | 24 | `no-consumer` | no consumer: 0 literal sites; 4 word(s) outside name it, 0 through a table a literal itself names |
| 568 | `0x237F20..0x237F38` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 569 | `0x24779C..0x2477B4` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 570 | `0x247E7C..0x247E94` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 571 | `0x2598A8..0x2598C0` | 24 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 572 | `0x25D51C..0x25D534` | 24 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 573 | `0x262E20..0x262E38` | 24 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 574 | `0x2648EC..0x264904` | 24 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 575 | `0x271134..0x27114C` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 576 | `0x27E0D4..0x27E0EC` | 24 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 577 | `0x2829B4..0x2829CC` | 24 | `no-consumer` | no consumer: 0 literal sites; 3 word(s) outside name it, 0 through a table a literal itself names |
| 578 | `0x2844E4..0x2844FC` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 579 | `0x28A678..0x28A690` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 580 | `0x290394..0x2903AC` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 581 | `0x29B308..0x29B320` | 24 | `no-consumer` | no consumer: 1 singleton literal site(s) (0 multi-site), same-size control max 1 - at or below the null (P-418) |
| 582 | `0x29E274..0x29E28C` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 583 | `0x2AFCE4..0x2AFCFC` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 584 | `0x2B28FC..0x2B2914` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 585 | `0x2B4994..0x2B49AC` | 24 | `no-consumer` | no consumer: 0 literal sites; 2 word(s) outside name it, 0 through a table a literal itself names |
| 586 | `0x6B8284..0x6B8294` | 16 | `raw-labeled` | raw-labeled, R-RAW-001: 14 literal site(s) outside the row, 3 multi-site literal(s), same-size control max 0 |
| 587 | `0x2B5F1C..0x2B5F28` | 12 | `no-consumer` | no consumer: 0 literal sites; 0 word(s) outside name it, 2 through a table a literal itself names |
| 588 | `0x2B5F94..0x2B5FA0` | 12 | `raw-labeled` | raw-labeled, R-RAW-001: 1 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 589 | `0x6F9EC4..0x6F9EC8` | 4 | `raw-labeled` | raw-labeled, R-RAW-001: 2 literal site(s) outside the row, 0 multi-site literal(s), same-size control max 0 |
| 590 | `0x3192A5..0x3192A8` | 3 | `no-consumer` | no consumer: 0 literal sites; 47 word(s) outside name it, 0 through a table a literal itself names |
| 591 | `0x36D18A..0x36D18C` | 2 | `no-consumer` | no consumer: 0 literal sites; 40 word(s) outside name it, 13 through a table a literal itself names |

## What is left

41 rows / 15280 B are `raw-labeled` (a cited consumer, no extent): `asm/rawlabeled_<start>.s`, one file
per row, `INCLUDE`d where the row's INCBIN line was. The extracted payload was the source and the
image slice the check, exactly as in PATH-100-004.

550 rows / 174497 B carry no consumer and stay retail, with the denominators in the table above: the
literal channel's own null is why they are not promoted - a singleton literal, or a row whose loader
count is at or below every same-size control window, is not evidence of a consumer (P-418), and a
word that names the row without a code site naming it is data naming data, not a consumer.

The stop rule: no row above 512 B is left with an unmeasured channel. Every row that is not promoted
above measured 0 literal sites, or a count at or below its own null, so the next ticket would need a
NEW channel (runtime observation), not another pass of these.
