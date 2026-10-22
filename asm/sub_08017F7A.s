	CODE16
|sub_08017F7A|
|unk_08017F7A|
		LDR r1, [r5]
		LDR r2, [r6, #4]
		ADD r3, r6, #2
		ADD r1, r1, r2
		LDR r2, [r5, #4]
		LDR r0, [r6, #8]
		STR r1, [sp, #4]
		ADD r0, r2, r0
		STR r0, [sp, #8]
		LDRB r2, [r6]
		ADD r0, r1, #0
		LDR r1, [sp, #8]
		LSR r2, r2, #1
		SUB r0, r0, r2
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		LDR r1, [r6, #0x10]
		ADD r0, r4, #0
		ADD r2, sp, #0xc
		BL       |sub_08018550|
		LDR r0, [pc, #0x2d0]
		ADD r1, r4, #0
		ADD r1, #0x30
		STR r0, [r4]
		ADD r0, r1, #4
		STR r0, [sp, #0x1c]
		ADD r0, #0x1c
		STR r0, [sp, #0x18]
		ADD r0, #4
		STR r0, [sp, #0x14]
		MOV r0, #0
		MVN r0, r0
		STR r1, [sp, #0x20]
		STR r0, [r4, #0x64]
		STR r6, [r4, #0x60]
		MOV r0, #0
		STR r0, [r4, #0x24]
		STR r0, [r4, #0x2c]
		BL       |loc_0803FAAC|
		STR r0, [r4, #0x28]
		LDR r0, [sp, #0x18]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		LSL r1, r1, #8
		STR r1, [r0]
		LDR r0, [sp, #0x14]
		LSL r2, r2, #8
		STR r2, [r0]
		MOV r0, #0xff
		ADD r0, #1
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [r7, #4]
		SUB r0, #0x80
		MUL r0, r1
		LDR r1, [r7]
		ASR r0, r0, #8
		ADD r0, r0, r1
		STR r0, [r4, #0x58]
		MOV r0, #0xff
		ADD r0, #1
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [r7]
		SUB r0, #0x80
		MUL r0, r1
		LDR r1, [r7, #4]
		ASR r0, r0, #8
		ADD r0, r0, r1
		STR r0, [r4, #0x5c]
		MOV r0, #0x40
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [r4, #0x58]
		ADD r0, #0xe0
		MUL r0, r1
		ASR r0, r0, #8
		STR r0, [r4, #0x58]
		MOV r0, #0x40
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [r4, #0x5c]
		ADD r0, #0xe0
		MUL r0, r1
		ASR r0, r0, #8
		STR r0, [r4, #0x5c]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		LDR r1, [sp, #0x20]
		MOV r0, #0
		STR r0, [r1]
		LDR r1, [sp, #0x1c]
		MOV r0, #0x80
		STR r0, [r1]
		ADD r1, r4, #0
		MOV r0, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x2a72
		ADD r2, r0, #0
		STR r0, [r4, #0x68]
		LDR r0, [pc, #0x220]
		LDR r0, [r0, #0x10]
		LDR r1, [r0]
		ADD r3, r1, #1
		STR r3, [r0]
		LSL r1, r1, #2
		ADD r0, r1, r0
		STR r2, [r0, #4]
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x48]
		STR r2, [r4, #0x4c]
		LDR r0, [r4, #0x60]
		SUB r5, #8
		LDRB r2, [r0]
		LDR r1, [r5]
		LSR r2, r2, #1
		SUB r1, r1, r2
		STR r1, [r4, #0x38]
		LDRB r0, [r0]
		ADD r0, r1, r0
		STR r0, [r4, #0x40]
		LDR r0, [r5, #4]
		STR r0, [r4, #4]
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0x2b84
