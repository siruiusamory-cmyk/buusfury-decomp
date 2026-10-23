	CODE16
|sub_0804F016|
|unk_0804F016|
		MOV r0, #0
		STR r0, [r4, #8]
		LDR r0, [pc, #0x14]
		STR r5, [r4, #4]
		STR r0, [r4]
		MOV r0, #0x78
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0xf0
		STR r0, [r4, #0xc]
		ADD r0, r4, #0
		B        |inc_0x049120_0x055620| + 0x5ef4
	INCBIN  baserom.gba_0x4f02e_0x4f032.extracted
|sub_0804F032|
	DCW      0x0804
