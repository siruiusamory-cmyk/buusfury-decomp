	CODE16
|sub_0800F6AE|
|unk_0800F6AE|
		LDR r0, [r5, #0x10]
		BL       |inc_0x0158_0x143f2|
		ADD r1, r5, #0
		ADD r1, #0xc
		STR r1, [sp]
		ADD r1, r0, #0
		ADD r3, r7, #0
		ADD r0, r4, #0
		STR r6, [sp, #4]
		LDR r2, [pc, #0x248]
		BL       |inc_0x0158_0x143f2| + 0xe5fc
		LDR r0, [pc, #0x244]
		ADD r1, r5, #0
		STR r0, [r4]
		MOV r0, #0x8b
		LSL r0, r0, #2
		ADD r1, #0x18
		ADD r0, r4, r0
		BL       |inc_0x0158_0x143f2| + 0xa7e4
		MOV r0, #0x47
		LSL r0, r0, #3
		ADD r6, r4, r0
		MOV r0, #0
		MOV r3, #1
		LSL r3, r3, #9
		STR r0, [r6, #4]
		ADD r2, r7, #0
		ADD r7, r4, r3
		STR r0, [r6, #0x30]
		STR r2, [r7, #0x24]
		LDR r3, [r5, #0x14]
		MOV r1, #0xa3
		STR r3, [r7, #0x28]
		MOV r3, #0x29
		LSL r3, r3, #4
		ADD r3, r4, r3
		STRB r0, [r3, #1]
		STRB r0, [r3]
		LDR r0, [r2, #4]
		LSL r1, r1, #2
		ADD r1, r4, r1
		LSL r0, r0, #0xa
		STR r0, [r1]
		LDR r0, [pc, #0x1f8]
		ADD r1, r4, #0
		LDR r5, [r0, #8]
		ADD r0, sp, #4
		BL       |sub_0800FDFA|
		ADD r5, #0x80
		LDR r1, [r5, #0x30]
		MOV r2, #0
		ADD r0, sp, #4
		BL       |loc_08009930|
		STR r4, [r6]
		LDR r0, [r7, #0x24]
		LDR r1, [r0, #8]
		ADD r0, r6, #0
		BL       |loc_0800AA9C|
		LDR r0, [pc, #0x1e4]
		LDR r1, [r0]
		ADD r2, r1, #1
		STR r2, [r0]
		LSL r1, r1, #2
		ADD r0, r1, r0
		STR r4, [r0, #4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xf552
