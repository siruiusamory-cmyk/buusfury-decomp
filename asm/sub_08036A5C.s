	CODE16
|sub_08036A5C|
|unk_08036A5C|
		LDR r0, [pc, #0x308]
		MOV r6, #1
		LSL r6, r6, #0xc
		LDR r5, [pc, #0x308]
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		LDR r0, [r5]
		ADD r1, r6, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08036A84|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |loc_0801124C|
|loc_08036A84|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x2e8]
		MOV r3, #0
		STR r0, [r4]
		LDR r0, [pc, #0x2e4]
		LDMIA r7!, {r1, r2}
		STR r0, [r4, #0x38]
		STR r1, [r4, #0x10]
		STR r2, [r4, #0x14]
		MOV r1, #0x3c
		STRB r1, [r4, #8]
		MOV r1, #0
		STR r1, [r4, #0x30]
		STR r2, [r4, #4]
		STR r1, [r4, #0x34]
		LDRSB r5, [r0, r3]
		LDR r1, [r4, #0x10]
		MOV r3, #1
		SUB r1, r1, r5
		STR r1, [r4, #0x20]
		LDRSB r5, [r0, r3]
		SUB r3, r2, r5
		STR r3, [r4, #0x24]
		LDRB r2, [r0, #2]
		LDRB r0, [r0, #3]
		ADD r1, r1, r2
		ADD r0, r3, r0
		STR r0, [r4, #0x2c]
		STR r1, [r4, #0x28]
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x189a
		PUSH {r4, r5, r6, lr}
		ADD r4, r0, #0
		LDR r0, [r0, #0x30]
		LDR r1, [r4, #0x38]
		SUB sp, #0x48
		LDR r6, [pc, #0x2a4]
		CMP r0, r1
		BEQ      |loc_08036AF6|
		STR r1, [r4, #0x30]
		LDRB r2, [r1, #2]
		LDRB r0, [r1, #3]
		LDR r3, [pc, #0x29c]
		MUL r2, r0
		LDRH r0, [r4, #0xc]
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r3
		BL       |Thunk_VramCopy|
		ADD r1, r6, #0
		LDR r0, [r4, #0x38]
		ADD r1, #0x18
		CMP r0, r1
		BNE      |loc_08036AF6|
		MOV r0, #0xf0
		STR r0, [r4, #0x34]
|loc_08036AF6|
		LDR r0, [r4, #0x38]
		SUB r1, r0, r6
		CMP r1, #0x18
		BLT      |inc_0x351c0_0x3d4d0| + 0x195e
		LDR r1, [r4, #0x34]
		SUB r2, r1, #1
		STR r2, [r4, #0x34]
		CMP r1, #0
		BNE      |inc_0x351c0_0x3d4d0| + 0x195e
		ADD r0, #0xc
		STR r0, [r4, #0x38]
		SUB r0, r0, r6
		BL       |sub_08053080|
		CMP r1, #6
		BNE      |sub_08036B1A|
		STR r6, [r4, #0x38]
		B        |inc_0x351c0_0x3d4d0| + 0x195e
