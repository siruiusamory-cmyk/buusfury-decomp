	CODE16
|sub_0801E18A|
|unk_0801E18A|
		MOV r0, #0x14
		DCD     0xFA14F01F
		CMP r0, #0
		BEQ      |loc_0801E19E|
		LDR r1, [pc, #0x48]
		STMIA r0!, {r1, r6}
		SUB r0, #8
		STR r5, [r0, #0xc]
		STR r6, [r0, #8]
|loc_0801E19E|
		ADD r1, r0, #0
		CMP r4, #0
		BEQ      |loc_0801E1AA|
		ADD r6, r4, #0
		ADD r6, #0xff
		ADD r6, #0x8d
|loc_0801E1AA|
		ADD r2, r6, #0
		LDR r6, [pc, #0x34]
		LDR r0, [r6, #4]
		BL       |inc_0x153f2_0x1a3f2| + 0x3f78
		LDR r1, [r4]
		MOV r2, #0x88
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		DCW     0xD0DF
		LDR r0, [r6]
		MOV r2, #0xff
		ADD r0, r0, r5
		LDRB r1, [r0, #2]
		ADD r2, #1
		ADD r1, #1
		CMP r1, r2
		BGE      |loc_0801E1DA|
		STRB r1, [r0, #2]
		DCW     0xE7D5
|loc_0801E1DA|
		MOV r1, #0xff
		STRB r1, [r0, #2]
		DCW     0xE7D2
|sub_0801E1E0|
	DCW      0xc83c
	DCW      0x0804
	DCW      0x07e4
	DCW      0x0872
