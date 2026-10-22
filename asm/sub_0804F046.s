	CODE16
|sub_0804F046|
|unk_0804F046|
; cited by 0x0804F04A (a pc-relative load targets 0x0804F060)
		MOV r0, #0
		STR r0, [r4, #8]
		LDR r0, [pc, #0x14]
		STR r5, [r4, #4]
		STR r0, [r4]
		MOV r0, #0xb4
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x78
		STR r0, [r4, #0xc]
		ADD r0, r4, #0
		B        |inc_0x049120_0x055620| + 0x5f24
	INCBIN  baserom.gba_0x4f05e_0x4f060.extracted
		DCD     0x0804E1A4
		BX       lr
