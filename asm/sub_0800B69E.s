	CODE16
|sub_0800B69E|
|unk_0800B69E|
		MOV r0, #1
		POP {r4, pc}
		PUSH {r4, r5, r6, r7, lr}
		LDR r5, [pc, #0x150]
		ADD r4, r0, #0
		LDR r0, [r5, #0xc]
		ADD r6, r1, #0
		LDRB r1, [r0]
		MOV r3, #0x68
		SUB sp, #0xc
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		LDR r0, [r0, #8]
		LDR r3, [pc, #0x158]
		LDR r1, [r4, #0x10]
		MUL r0, r3
		ASR r0, r0, #0x10
		CMP r1, r0
		BEQ      |loc_0800B7AE|
		STR r0, [r4, #0x10]
		BL       |inc_0x049120_0x055620| + 0x9fd4
		ADD r1, #0x30
		ADD r3, sp, #0
		STRH r1, [r3, #4]
		BL       |inc_0x049120_0x055620| + 0x9ef0
		ADD r1, #0x30
		ADD r3, sp, #0
		STRH r1, [r3, #6]
		ADD r0, #0x30
		STRH r0, [r3, #8]
		LDR r0, [r4, #0x3c]
		LDR r2, [r4, #0x48]
		MOV r1, #0
		BL       |sub_08046E40|
		ADD r3, sp, #0
		LDRH r1, [r3, #4]
		ADD r7, r5, #0
		LDR r0, [r5, #0x14]
		CMP r1, #0xff
		BLO      |loc_0800B700|
		LDR r0, [r0, #4]
		ADD r0, #1
		B        |loc_0800B70C|
|loc_0800B700|
		LDR r0, [r0]
		LSL r1, r1, #1
		LDRH r1, [r0, r1]
		LSL r1, r1, #1
		LDRH r0, [r0, r1]
		ADD r0, #1
|loc_0800B70C|
		MOV r1, #8
		SUB r0, r1, r0
		STR r0, [r4, #0x1c]
		MOV r0, #0xf
		STR r0, [r4, #0x20]
		ADD r0, r4, #0
		ADD r0, #0x18
		ADD r3, sp, #0
		LDRH r1, [r3, #4]
		ADD r5, r0, #0
		BL       |sub_0803DE50|
		LDR r0, [pc, #0xd0]
		MOV r7, #0xf
		LDR r0, [r0, #0x14]
		LDR r1, [r0]
		MOV r0, #0x74
		LDRH r0, [r1, r0]
		LSL r0, r0, #1
		LDRH r0, [r1, r0]
		MOV r1, #0xa
		ADD r0, #1
		SUB r0, r1, r0
		STR r0, [r4, #0x1c]
		MOV r1, #0x3a
		ADD r0, r5, #0
		STR r7, [r4, #0x20]
		BL       |sub_0803DE50|
		LDR r0, [pc, #0xb0]
		ADD r3, sp, #0
		LDR r0, [r0, #0x10]
		LDRH r1, [r3, #6]
		CMP r1, #0xff
		BLO      |loc_0800B758|
		LDR r0, [r0, #4]
		ADD r0, #1
		B        |loc_0800B764|
|loc_0800B758|
		LDR r0, [r0]
		LSL r1, r1, #1
		LDRH r1, [r0, r1]
		LSL r1, r1, #1
		LDRH r0, [r0, r1]
		ADD r0, #1
|loc_0800B764|
		MOV r1, #0x12
		SUB r0, r1, r0
		STR r0, [r4, #0x1c]
		STR r7, [r4, #0x20]
		ADD r3, sp, #0
		LDRH r1, [r3, #6]
		ADD r0, r5, #0
		BL       |sub_0803DE50|
		LDR r0, [pc, #0x80]
		ADD r3, sp, #0
		LDR r0, [r0, #0x10]
		LDRH r1, [r3, #8]
		CMP r1, #0xff
		BLO      |loc_0800B788|
		LDR r0, [r0, #4]
		ADD r0, #1
		B        |loc_0800B794|
|loc_0800B788|
		LDR r0, [r0]
		LSL r1, r1, #1
		LDRH r1, [r0, r1]
		LSL r1, r1, #1
		LDRH r0, [r0, r1]
		ADD r0, #1
|loc_0800B794|
		MOV r1, #0x18
		SUB r0, r1, r0
		STR r0, [r4, #0x1c]
		STR r7, [r4, #0x20]
		ADD r3, sp, #0
		LDRH r1, [r3, #8]
		ADD r0, r5, #0
		BL       |sub_0803DE50|
		LDRH r0, [r4, #0xc]
		LDR r1, [pc, #0x50]
		LSL r0, r0, #5
		B        |sub_0800B7B0|
|loc_0800B7AE|
		B        |inc_0x0158_0x143f2| + 0xb660
