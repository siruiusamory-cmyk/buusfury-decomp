	CODE16
|sub_08006116|
|unk_08006116|
		ADD r2, sp, #0x30
		LDMIA r2!, {r0, r1, r2}
		STR r0, [sp]
		STR r1, [sp, #4]
		ADD r3, sp, #0x10
		STR r2, [sp, #8]
		LDMIA r3!, {r1, r2, r3}
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x5e66
		LDR r0, [pc, #0x150]
		STR r0, [r4]
		STR r6, [r4, #0x28]
		LDR r0, [sp, #0x3c]
		STR r0, [r4, #0x1c]
		LDR r0, [sp, #0x40]
		STR r0, [r4, #0x20]
		STR r5, [r4, #0x24]
		MOV r0, #0x2c
		STRB r7, [r0, r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x5fba
		ADD r2, r0, #0
		ADD r0, r1, #0
		MOV r1, #0x2c
		PUSH {r4, lr}
		LDRB r1, [r1, r2]
		STRB r1, [r0]
		MOV r1, #1
		STRB r1, [r0, #2]
		LDR r1, [pc, #0x130]
		STR r1, [r0, #0x20]
		LDR r1, [r2, #4]
		ADD r1, #0xff
		ADD r1, #1
		LDR r1, [r1, #0xc]
		LDR r3, [r2, #8]
		CMP r1, r3
		BNE      |sub_08006168|
		MOV r1, #6
		B        |inc_0x0158_0x143f2| + 0x6012
