	CODE16
|sub_0803F55E|
|unk_0803F55E|
		MOV r7, #0
		MOV r1, #0
		ADD r0, r4, #0
		STR r7, [sp, #4]
		STR r7, [sp, #8]
		STR r5, [sp, #0xc]
		STR r6, [sp, #0x10]
		ADD r2, sp, #4
		BL       |inc_0x03d784_0x041118| + 0x2f4
		STR r5, [r4, #0x28]
		MUL r5, r6
		ADD r0, r5, #0
		STR r6, [r4, #0x2c]
		STR r0, [r4, #0x30]
		DCD     0xF81CF7FE
		STR r0, [r4, #0x24]
		LDR r0, [pc, #0x184]
		STR r0, [r4, #0x20]
		STRB r7, [r4, #3]
		ADD r0, r4, #0
		DCW     0xE7E6
