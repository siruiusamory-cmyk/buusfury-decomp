	CODE16
|sub_080060C6|
|unk_080060C6|
		ADD r2, sp, #0x30
		LDMIA r2!, {r0, r1, r2}
		STR r0, [sp]
		STR r1, [sp, #4]
		ADD r3, sp, #0x10
		STR r2, [sp, #8]
		LDMIA r3!, {r1, r2, r3}
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x5e66
		LDR r0, [pc, #0x1a0]
		LDR r1, [pc, #0x1a0]
		STR r0, [r4]
		STR r6, [r4, #0x28]
		LDR r0, [sp, #0x3c]
		LSL r0, r0, #2
		LDR r0, [r1, r0]
		STR r0, [r4, #0x1c]
		LDR r0, [sp, #0x40]
		STR r0, [r4, #0x20]
		STR r5, [r4, #0x24]
		MOV r0, #0x2c
		STRB r7, [r0, r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x5f6a
