	CODE16
|sub_08037EC4|
|unk_08037EC4|
		LDR r0, [pc, #0x2b0]
		MOV r7, #7
		LSL r7, r7, #8
		LDR r6, [pc, #0x2b0]
		STR r0, [r4]
		STRH r7, [r4, #0xe]
		LDR r0, [r6]
		ADD r1, r7, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08037EEC|
		ADD r1, r7, #0
		LDR r0, [r6]
		BL       |sub_08011732|
		ADD r1, r7, #0
		LDR r0, [r6]
		BL       |loc_0801124C|
|loc_08037EEC|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x290]
		STR r0, [r4]
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x1c]
		STR r2, [r4, #0x20]
		MOV r1, #0x38
		STRB r1, [r4, #8]
		SUB r5, #8
		LDR r1, [r5, #4]
		ADD r0, r4, #0
		STR r1, [r4, #4]
		LDR r1, [sp, #0x10]
		ADD r0, #0x1c
		STR r1, [r4, #0x58]
		MOV r1, #0
		STR r1, [r4, #0x14]
		STRB r1, [r4, #0x10]
		MOV r1, #8
		STR r1, [r4, #0x3c]
		MOV r1, #0
		MVN r1, r1
		STR r1, [r4, #0x18]
		LDR r1, [sp, #0xc]
		STR r1, [r4, #0x40]
		LDMIA r5!, {r1, r2}
		STMIA r0!, {r1, r2}
		LDR r0, [r4, #0x40]
		LDR r2, [pc, #0x25c]
		LSL r1, r0, #1
		ADD r1, r1, r0
		LSL r1, r1, #4
		ADD r1, r1, r2
		STR r1, [r4, #0x54]
		LDR r1, [pc, #0x248]
		LSL r0, r0, #3
		ADD r1, #8
		ADD r0, r0, r1
		LDR r1, [r0]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x30]
		STR r1, [r4, #0x2c]
		MOV r1, #0
		STR r1, [sp]
		LDRH r0, [r4, #0xc]
		LDR r1, [pc, #0x240]
		LSL r0, r0, #5
		ADD r7, r0, r1
		MOV r5, #0
|loc_08037F4E|
		LSL r0, r5, #2
		LDR r1, [sp]
		ADD r0, r0, r4
		STR r1, [r0, #0x44]
		LSL r1, r5, #1
		ADD r1, r1, r5
		LDR r0, [r4, #0x54]
		LSL r1, r1, #2
		ADD r0, r0, r1
		LDRB r6, [r0, #2]
		LDRB r1, [r0, #3]
		MUL r6, r1
		ADD r2, r6, #0
		LDR r1, [r0, #8]
		ADD r0, r7, #0
		BL       |Thunk_VramCopy|
		ASR r0, r6, #0x1f
		LSR r0, r0, #0x1b
		ADD r0, r0, r6
		LDR r1, [sp]
		ASR r0, r0, #5
		ADD r1, r0, r1
		ADD r7, r7, r6
		ADD r5, #1
		CMP r5, #4
		STR r1, [sp]
		BLT      |loc_08037F4E|
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x2d00
