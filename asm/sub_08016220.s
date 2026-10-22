	CODE16
|sub_08016220|
|unk_08016220|
		LDR r0, [pc, #0x9c]
		STMIA r4!, {r0, r5}
		SUB r4, #8
		MOV r0, #0
		STR r0, [r4, #8]
		MOV r0, #0xff
		ADD r0, #1
		DCW     0xF027
		DCW     0xF9C3
		ADD r1, r0, #0
		STR r0, [r4, #0xc]
		LDR r0, [pc, #0x8c]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0xe2c
