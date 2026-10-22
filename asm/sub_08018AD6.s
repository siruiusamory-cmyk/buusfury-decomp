	CODE16
|sub_08018AD6|
|unk_08018AD6|
		ADD r0, r4, #0
		MOV r1, #9
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_08018AE6|
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x36e0
|loc_08018AE6|
|unk_08018AE6|
		ADD r1, r4, #0
		ADD r6, sp, #0x48
		ADD r0, r6, #0
		BL       |sub_0800FDFA|
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		ADD r2, r5, #4
		STR r2, [sp, #0x58]
		STR r0, [sp, #0x5c]
		LDR r1, [r0]
		LDR r3, [r5, #4]
		ADD r7, r2, #4
		ADD r1, r1, r3
		STR r1, [r0]
		LDR r1, [r0, #4]
		LDR r2, [r5, #8]
		ADD r5, sp, #0x38
		ADD r1, r1, r2
		STR r1, [r0, #4]
		ADD r1, r4, #0
		ADD r0, r5, #0
		BL       |sub_0800FDFA|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x4c]
		ADD r3, r2, r1
		MOV r2, #1
		ADD r1, r6, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x50]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_08018B4C|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x4c]
		ADD r3, r2, r1
		MOV r2, #0
		ADD r1, r5, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		B        |loc_08018BC6|
|loc_08018B4C|
		LDR r0, [sp, #0x5c]
		LDR r1, [sp, #0x58]
		LDR r2, [r0]
		LDR r1, [r1]
		SUB r1, r2, r1
		STR r1, [r0]
		LDR r1, [r0, #4]
		LDR r2, [r7]
		SUB r1, r1, r2
		STR r1, [r0, #4]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x4c]
		ADD r3, r2, r1
		MOV r2, #0
		ADD r1, r6, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		MOV r0, #5
		LSL r0, r0, #7
		ADD r0, r4, r0
		LDR r1, [r0, #0x14]
		CMP r1, #0
		BNE      |loc_08018B82|
		LDR r0, [r0, #0x18]
		CMP r0, #0
		BEQ      |loc_08018BC6|
|loc_08018B82|
		ADD r6, sp, #4
		ADD r0, r6, #4
		LDMIA r5!, {r1, r2, r3, r5}
		STMIA r0!, {r1, r2, r3, r5}
		MOV r1, #0x29
		LSL r1, r1, #4
		ADD r0, r4, r1
		STR r4, [sp, #0x24]
		LDRB r0, [r0]
		ADD r3, sp, #0
		STRB r0, [r3, #0x18]
		LDR r0, [pc, #0x48]
		STR r0, [sp, #0x20]
		LDR r0, [pc, #0x48]
		BL       |sub_08054A64|
		STR r0, [sp, #0x1c]
		MOV r5, #1
		ADD r3, sp, #0
		STRB r5, [r3, #4]
		STR r4, [sp, #0x34]
		LDR r4, [sp, #0x60]
		MOV r0, #0
		STR r0, [r4, #0xc]
		LDR r0, [pc, #0x2c]
		ADD r2, r6, #0
		MOV r1, #0
		SUB r0, #4
		LDR r0, [r0]
		BL       |loc_08011C0C|
		MOV r0, #1
		STR r5, [r4, #0xc]
		B        |inc_0x153f2_0x1a3f2| + 0x36e0
|loc_08018BC6|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x36e0
