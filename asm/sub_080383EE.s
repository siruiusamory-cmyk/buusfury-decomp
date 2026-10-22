	CODE16
|sub_080383EE|
|unk_080383EE|
		LDR r0, [pc, #0x2ec]
		LDR r7, [pc, #0x2ec]
		STR r0, [r4]
		MOV r0, #0xc0
		STRH r0, [r4, #0xe]
		LDR r0, [r7, #4]
		MOV r1, #0xc0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08038414|
		MOV r1, #0xc0
		LDR r0, [r7, #4]
		BL       |sub_08011732|
		MOV r1, #0xc0
		LDR r0, [r7, #4]
		BL       |loc_0801124C|
|loc_08038414|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x2cc]
		ADD r1, r4, #0
		STR r0, [r4]
		LDMIA r5!, {r0, r2}
		STR r0, [r4, #0x24]
		STR r2, [r4, #0x28]
		MOV r2, #0
		STR r2, [r4, #0x18]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		SUB r5, #8
		LDR r0, [r5, #4]
		ADD r1, #0x24
		STR r0, [r4, #4]
		LDRB r0, [r6, #0x10]
		STR r0, [r4, #0x40]
		CMP r0, #0
		BNE      |loc_08038440|
		LDR r0, [r5, #4]
		ADD r0, #0x2c
		STR r0, [r4, #4]
|loc_08038440|
		STR r2, [r4, #0x14]
		STR r6, [r4, #0x48]
		STRB r2, [r4, #0x10]
		MOV r0, #8
		STR r0, [r4, #0x3c]
		LDMIA r5!, {r0, r3}
		STMIA r1!, {r0, r3}
		SUB r5, #8
		LDMIA r5!, {r1, r3}
		STR r1, [r4, #0x1c]
		STR r3, [r4, #0x20]
		LDR r0, [r4, #0x40]
		LDR r3, [pc, #0x28c]
		LSL r1, r0, #3
		ADD r1, r1, r0
		LSL r1, r1, #2
		ADD r1, r1, r3
		STR r1, [r4, #0x44]
		LDR r1, [pc, #0x284]
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [r0]
		LDR r0, [r0, #4]
		ADD r3, r2, #0
		STR r0, [r4, #0x38]
		STR r1, [r4, #0x34]
		LDR r0, [r7]
		LDR r5, [pc, #0x27c]
		MOV r2, #0x40
		ADD r0, r0, r5
		LDR r1, [pc, #0x270]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDRH r0, [r4, #0xc]
		LDR r1, [pc, #0x270]
		LSL r0, r0, #5
		ADD r0, r0, r1
		LDR r1, [r4, #0x44]
		MOV r2, #0xc0
		LDR r1, [r1, #8]
		BL       |Thunk_VramCopy|
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x322c
