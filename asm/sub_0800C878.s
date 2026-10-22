	CODE16
|sub_0800C878|
|unk_0800C878|
		LSL r0, r0, #0x1e
		BMI      |loc_0800C874|
		MOV r0, #5
		BL       |inc_0x03d784_0x041118| + 0x2348
		SUB r5, r0, #2
		MOV r0, #3
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r1, [r4, #0x2c]
		SUB r0, #1
		ADD r2, r1, #0
		LDR r1, [r1, #0x20]
		ADD r2, #0x24
		LDR r3, [r1]
		LDR r4, [r1, #4]
		ADD r3, r3, r5
		ADD r4, r4, r0
		STR r4, [sp, #4]
		STR r3, [sp]
		ADD r1, #8
		LDR r6, [r1]
		LDR r1, [r1, #4]
		ADD r5, r6, r5
		ADD r0, r1, r0
		STR r0, [sp, #4]
		LDR r1, [sp, #4]
		STR r4, [sp, #0xc]
		ADD r4, r2, #0
		ADD r0, sp, #8
		STR r5, [sp]
		STR r5, [sp, #0x10]
		STR r3, [sp, #8]
		STR r1, [sp, #0x14]
		LDMIA r0!, {r0, r1, r2, r3}
		STMIA r4!, {r0, r1, r2, r3}
		B        |loc_0800C874|
