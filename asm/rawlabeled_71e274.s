; PATH-100-004 / R-RAW-001: the census run 0x0871e274..0x0872c378 as LABELED RAW DATA.

	EXPORT	|unk_0871E274|
|unk_0871E274|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x71e274_0x71e630.extracted
	EXPORT	|unk_0871E630|
|unk_0871E630|
; cited by 0x0801C93A INDEXED base + register (r0, r0, r1) INDEXED base + register (r0, r0, r5), 0x0801CA4E

	INCBIN	baserom.gba_0x71e630_0x71e984.extracted
	EXPORT	|unk_0871E984|
|unk_0871E984|
; cited by 0x0801C732, 0x0801C840 INDEXED base + register (r0, r0, r1)

	INCBIN	baserom.gba_0x71e984_0x71e9a8.extracted
	EXPORT	|unk_0871E9A8|
|unk_0871E9A8|
; cited by 0x0804F81A ldr r0 +0x14

	INCBIN	baserom.gba_0x71e9a8_0x71e9d8.extracted
	EXPORT	|unk_0871E9D8|
|unk_0871E9D8|
; cited by 0x0801DFAC ldr r0 +0x0 ldr r0 +0x4 INDEXED base + register (r0, r0, r4)

	INCBIN	baserom.gba_0x71e9d8_0x720200.extracted
	EXPORT	|unk_08720200|
|unk_08720200|
; cited by 0x086178AE

	INCBIN	baserom.gba_0x720200_0x7202e8.extracted
	EXPORT	|unk_087202E8|
|unk_087202E8|
; cited by 0x0801E038, 0x0801E0DE INDEXED base + register (r0, r0, r1)

	INCBIN	baserom.gba_0x7202e8_0x72033c.extracted
	EXPORT	|unk_0872033C|
|unk_0872033C|
; cited by 0x080519E2 ldr r0 +0x0

	INCBIN	baserom.gba_0x72033c_0x720564.extracted
	EXPORT	|unk_08720564|
|unk_08720564|
; cited by 0x080141EE INDEXED base + register (r4, r0, r1)

	INCBIN	baserom.gba_0x720564_0x7207e4.extracted
	EXPORT	|unk_087207E4|
|unk_087207E4|
; cited by 0x0801E1AC ldr r6 +0x4 ldr r6 +0x0 INDEXED ldr [r0 + reg] INDEXED base + register (r0, r0, r1)

	DCD	|unk_03001068|
	DCD	|unk_03002BAC|
	EXPORT	|unk_087207EC|
|unk_087207EC|
; cited by 0x0801E234 ldr r6 +0x8, 0x0801E380 ldr r0 +0x8 INDEXED ldr [r1 + reg], 0x0801E3EC ldr r1 +0x4 INDEXED base + register (r0, r1, r0), 0x0801E440 ldr r0 +0x0 ldr r0 +0x4 INDEXED base + register (r0, r0, r7)

	DCD	|unk_03003300|
	DCD	|unk_03003898|
	DCD	|unk_0807012C|
	DCD	|unk_03003300|
	DCD	|unk_03003898|
	DCD	|unk_0806E050|
	DCD	|unk_03002BD4|
	DCD	|unk_030019A4|
	EXPORT	|unk_0872080C|
|unk_0872080C|
; cited by 0x0801E4BC, 0x0801E57A ldr r1 +0x4 INDEXED base + register (r5, r1, r0), 0x0801E68C ldr r4 +0x0 ldr r4 +0x4 INDEXED base + register (r0, r0, r5), 0x0801E72A ldr r1 +0x8

	INCBIN	baserom.gba_0x72080c_0x72081c.extracted
	EXPORT	|unk_0872081C|
|unk_0872081C|
; cited by 0x0801E790, 0x0801E84C ldr r3 +0x4 INDEXED base + register (r0, r1, r0) ldr r3 +0xc, 0x0801E8A2 ldr r3 +0xc, 0x0801E916 ldr r3 +0xc ldr r0 +0x0 ldr r0 +0x4 INDEXED base + register (r0, r0, r5) (+2 more sites)

	INCBIN	baserom.gba_0x72081c_0x72082c.extracted
	EXPORT	|unk_0872082C|
|unk_0872082C|
; cited by 0x0801EA3A ldr r6 +0x4, 0x0801EB68 ldr r0 +0x4 INDEXED ldr [r1 + reg] INDEXED base + register (r0, r0, r1), 0x0801EC3A ldr r1 +0x0 INDEXED base + register (r0, r1, r0)

	DCD	|unk_03003898|
	DCD	|unk_0807012C|
	EXPORT	|unk_08720834|
|unk_08720834|
; cited by 0x0801ED6A ldr r6 +0x4, 0x0801EF90 ldr r2 +0x0, 0x0801EFF8 ldr r2 +0x0

	DCD	|unk_03003300|
	DCD	|unk_0807012C|
	EXPORT	|unk_0872083C|
|unk_0872083C|
; cited by 0x0801FE9A ldr r3 +0x4 INDEXED base + register (r7, r6, r1) ldr r3 +0x0

	DCD	|unk_03003300|
	DCD	|unk_03003898|
	DCD	|unk_0807012C|
	DCD	|unk_03001068|
	EXPORT	|unk_0872084C|
|unk_0872084C|
; cited by 0x08020416 ldr r6 +0xc, 0x08020516 ldr r0 +0x10

	INCBIN	baserom.gba_0x72084c_0x725018.extracted
	EXPORT	|unk_08725018|
|unk_08725018|
; cited by 0x0801ADE0 INDEXED base + register (r2, r0, r1)

	INCBIN	baserom.gba_0x725018_0x725038.extracted
	EXPORT	|unk_08725038|
|unk_08725038|
; cited by 0x0803C352

	INCBIN	baserom.gba_0x725038_0x725048.extracted
	EXPORT	|unk_08725048|
|unk_08725048|
; cited by 0x08020AF0 ldr r0 +0x4, 0x08020CCA ldr r1 +0x8, 0x08020D34

	DCD	|unk_03003898|
	DCD	|unk_03001C4C|
	DCD	|unk_030019A4|
	EXPORT	|unk_08725054|
|unk_08725054|
; cited by 0x08020DBE, 0x08020DE4, 0x08020E1E, 0x08020E84 (+1 more sites)

	INCBIN	baserom.gba_0x725054_0x72507c.extracted
	EXPORT	|unk_0872507C|
|unk_0872507C|
; cited by 0x0802111E ldr r4 +0x4 ldr r4 +0x0

	DCD	|unk_03002BD8|
	DCD	|unk_030019A4|
	EXPORT	|unk_08725084|
|unk_08725084|
; cited by 0x080211AA ldr r5 +0x0 ldr r5 +0x4, 0x0802121E ldr r7 +0x4 ldr r7 +0x0

	DCD	|unk_030019A4|
	DCD	|unk_03002BD8|
	EXPORT	|unk_0872508C|
|unk_0872508C|
; cited by 0x08021270 ldr r0 +0x0

	INCBIN	baserom.gba_0x72508c_0x725090.extracted
	EXPORT	|unk_08725090|
|unk_08725090|
; cited by 0x080212E4 ldr r0 +0x0 INDEXED base + register (r0, r0, r5) ldr r5 +0x0 INDEXED base + register (r0, r0, r2), 0x08021306 ldr r5 +0x0 INDEXED base + register (r0, r0, r2) ldr r5 +0x4, 0x0802135E ldr r5 +0x4, 0x080213F0 ldr r5 +0x4 ldr r5 +0x0 INDEXED base + register (r1, r0, r1) INDEXED base + register (r0, r5, r0) (+2 more sites)

	DCD	|unk_03003898|
	DCD	|unk_03001C4C|
	EXPORT	|unk_08725098|
|unk_08725098|
; cited by 0x0805204A ldr r0 +0x0

	INCBIN	baserom.gba_0x725098_0x72509e.extracted
	EXPORT	|unk_0872509E|
|unk_0872509E|
; cited by 0x080215B0 ldrb r7 +0x0 ldrb r7 +0x1 ldr r0 +0x0 ldr r1 +0x8, 0x080215EA ldr r1 +0x8 INDEXED base + register (r0, r0, r3), 0x080216F2 INDEXED base + register (r2, r2, r3)

	INCBIN	baserom.gba_0x72509e_0x7251c8.extracted
	EXPORT	|unk_087251C8|
|unk_087251C8|
; cited by 0x0802177E ldr r5 +0x8 ldr r5 +0x0 ldr r5 +0xc ldr r5 +0x4

	INCBIN	baserom.gba_0x7251c8_0x7251d8.extracted
	EXPORT	|unk_087251D8|
|unk_087251D8|
; cited by 0x0802183A ldr r0 +0x0

	INCBIN	baserom.gba_0x7251d8_0x725749.extracted
	EXPORT	|unk_08725749|
|unk_08725749|
; cited by 0x08465A36 strh r0 +0x2e

	INCBIN	baserom.gba_0x725749_0x72a690.extracted
	EXPORT	|unk_0872A690|
|unk_0872A690|
; cited by 0x0801C0EC INDEXED base + register (r2, r0, r1)

	INCBIN	baserom.gba_0x72a690_0x72a6a8.extracted
	EXPORT	|unk_0872A6A8|
|unk_0872A6A8|
; cited by 0x0803BDD8

	INCBIN	baserom.gba_0x72a6a8_0x72a6b4.extracted
	EXPORT	|unk_0872A6B4|
|unk_0872A6B4|
; cited by 0x0804FD10 ldr r0 +0x14

	INCBIN	baserom.gba_0x72a6b4_0x72a6f8.extracted
	EXPORT	|unk_0872A6F8|
|unk_0872A6F8|
; cited by 0x0802211A ldr r7 +0x4 ldr r7 +0x8, 0x0802215E ldr r7 +0x4, 0x0802222C ldr r7 +0x4, 0x080222B6 ldr r7 +0x4 (+1 more sites)

	INCBIN	baserom.gba_0x72a6f8_0x72bf06.extracted
	EXPORT	|unk_0872BF06|
|unk_0872BF06|
; cited by 0x080222F8 ldrb r6 +0x0 ldrb r6 +0x1 ldr r7 +0x4 ldr r1 +0x8, 0x0802232E ldr r1 +0x8 INDEXED base + register (r0, r0, r3), 0x0802236E

	INCBIN	baserom.gba_0x72bf06_0x72bf34.extracted
	EXPORT	|unk_0872BF34|
|unk_0872BF34|
; cited by 0x08022368

	INCBIN	baserom.gba_0x72bf34_0x72bf64.extracted
	EXPORT	|unk_0872BF64|
|unk_0872BF64|
; cited by 0x08022376

	INCBIN	baserom.gba_0x72bf64_0x72bf94.extracted
	EXPORT	|unk_0872BF94|
|unk_0872BF94|
; cited by 0x08052E86 ldr r0 +0x4

	DCD	|unk_03003300|
	DCD	|unk_03001C4C|
	DCD	|unk_030019A4|
	EXPORT	|unk_0872BFA0|
|unk_0872BFA0|
; cited by 0x08022646 ldr r7 +0x0

	INCBIN	baserom.gba_0x72bfa0_0x72bfa4.extracted
	EXPORT	|unk_0872BFA4|
|unk_0872BFA4|
; cited by 0x080226E4 ldr r7 +0x0, 0x080227D0 ldr r5 +0x0, 0x0802284A ldr r0 +0x0, 0x080228A6 ldr r0 +0x0

	INCBIN	baserom.gba_0x72bfa4_0x72bfa8.extracted
	EXPORT	|unk_0872BFA8|
|unk_0872BFA8|
; cited by 0x08022AF8 ldr r4 +0x1c, 0x08022B72 ldr r5 +0xc INDEXED ldr [r7 + reg] ldr r5 +0x8

	INCBIN	baserom.gba_0x72bfa8_0x72c34c.extracted
	EXPORT	|unk_0872C34C|
|unk_0872C34C|
; cited by 0x080237FC ldr r6 +0x0

	DCD	|unk_0807012C|
	DCD	|unk_03002F58|
	DCD	|unk_03003898|
	EXPORT	|unk_0872C358|
|unk_0872C358|
; cited by 0x08023F64 INDEXED base + register (r0, r0, r2) ldr r0 +0x0 INDEXED base + register (r1, r1, r2) INDEXED base + register (r0, r0, r4), 0x08023F8A ldr r0 +0x0 INDEXED base + register (r1, r1, r2) INDEXED base + register (r0, r0, r4), 0x08023FDE ldr r0 +0x0 INDEXED base + register (r1, r1, r2) INDEXED base + register (r0, r0, r4)


	INCBIN	baserom.gba_0x72c358_0x72c378.extracted
