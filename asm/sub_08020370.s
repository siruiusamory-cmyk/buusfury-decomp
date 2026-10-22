	CODE16
|sub_08020370|
|unk_08020370|
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0x2d
		BL       |sub_08004DC0|
		CMP r0, #0
		BEQ      |loc_08020386|
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x5754
		DCW     0xE7F3
|loc_08020386|
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x5754
		MOV r0, #0xff
		ADD r0, #0x19
		DCD     0xF912F01D
		CMP r0, #0
		BEQ      |loc_080203B4|
		ADD r1, r0, #0
		ADD r1, #0xff
		STMIA r0!, {r5, r6}
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		LDR r1, [pc, #0x194]
		SUB r0, #8
		STR r1, [r0]
		MOV r1, #2
		MOV r2, #0xff
		ADD r2, #0x15
		STRB r1, [r2, r0]
|loc_080203B4|
		BL       |inc_0x03d784_0x041118| + 0x11c
		ADD r0, r7, #0
		DCW     0xF01D
		DCW     0xF8FD
		CMP r0, #0
		BEQ      |loc_080203D6|
		ADD r1, r0, #0
		ADD r1, #0xff
		STMIA r0!, {r5, r6}
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		LDR r1, [pc, #0x164]
		SUB r0, #8
		STR r1, [r0]
|loc_080203D6|
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #0
		DCW     0xE7C7
