	CODE16
|sub_0803BE34|
|unk_0803BE34|
		LDR r0, [r5, #8]
		SUB r1, r0, #1
		STR r1, [r5, #8]
		CMP r0, #0
		BNE      |loc_0803BE30|
		LDR r0, [pc, #0xdc]
		ADD r1, r4, #0
		LDR r0, [r0]
		ADD r1, #0xff
		ADD r0, #0xff
		ADD r0, #0xa1
		ADD r1, #0xa1
		LDMIA r0!, {r2}
		LDMIA r1!, {r3}
		LDR r0, [r0]
		LDR r1, [r1]
		SUB r2, r2, r3
		SUB r0, r0, r1
		STR r0, [sp, #4]
		LDR r1, [sp, #4]
		STR r2, [sp]
		STR r1, [sp, #0x14]
		LDR r0, [sp, #0x14]
		STR r1, [sp, #0xc]
		ASR r1, r2, #8
		ASR r0, r0, #8
		STR r0, [sp, #4]
		STR r0, [sp, #0xc]
		ADD r0, r1, #0
		STR r2, [sp, #8]
		STR r1, [sp, #8]
		MUL r0, r1
		STR r1, [sp]
		LDR r1, [sp, #0xc]
		STR r2, [sp, #0x10]
		ADD r2, r1, #0
		MUL r1, r2
		ADD r0, r0, r1
		BL       |sub_0803FAF6|
		ADD r6, r0, #0
		LDR r1, [sp, #0x10]
		BL       |sub_08046E58|
		STR r0, [sp, #0x10]
		ADD r0, r6, #0
		LDR r1, [sp, #0x14]
		BL       |sub_08046E58|
		STR r0, [sp, #0x14]
		MOV r0, #1
		STRH r0, [r4, #0x12]
		STRB r0, [r4, #0x11]
		STR r6, [sp]
		LDRB r1, [r4, #0x10]
		LDR r0, [r5, #4]
		ADD r3, sp, #0x10
		LDMIA r3!, {r2, r3}
		BL       |inc_0x1c3f2_0x2ab4c| + 0x50e8
		MOV r0, #0
		STR r0, [r5, #4]
		B        |loc_0803BE30|
