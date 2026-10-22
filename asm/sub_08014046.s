	CODE16
|sub_08014046|
|unk_08014046|
		ADD r2, sp, #0x30
		LDMIA r2!, {r0, r1, r2}
		STR r0, [sp]
		STR r1, [sp, #4]
		ADD r3, sp, #0x10
		STR r2, [sp, #8]
		LDMIA r3!, {r1, r2, r3}
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x5e66
		LDR r0, [pc, #0xc0]
		STR r0, [r4]
		ADD r0, r4, #0
		ADD r0, #0x24
		LDMIA r5!, {r1, r2, r3, r5}
		STMIA r0!, {r1, r2, r3, r5}
		STR r6, [r4, #0x20]
		STR r7, [r4, #0x1c]
		SUB r0, #0x10
		ADD r2, r0, #0
		LDR r3, [r4, #0x24]
		LDR r5, [r4, #0x2c]
		ADD r2, #8
		LDR r0, [r4, #0x28]
		LDR r2, [r2, #4]
		ADD r3, r3, r5
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r2, r3, #1
		STR r3, [sp, #4]
		ADD r1, r4, #0
		ADD r1, #0x34
		STR r2, [sp, #4]
		STR r0, [sp, #8]
		STR r0, [r1, #4]
		STR r2, [r1]
		LDR r0, [r4, #0x38]
		ADD r0, #3
		STR r0, [r4, #0x38]
		LDR r0, [pc, #0x7c]
		LDR r1, [r4, #0x20]
		SUB r0, #8
		LDR r0, [r0, #4]
		BL       |sub_0803FFE8|
		LSR r1, r0, #0x1f
		ADD r0, r1, r0
		LDR r1, [r4, #0x34]
		ASR r0, r0, #1
		SUB r0, r1, r0
		STR r0, [r4, #0x34]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x13eea
