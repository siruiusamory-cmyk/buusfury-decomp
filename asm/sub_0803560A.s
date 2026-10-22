	CODE16
|sub_0803560A|
|unk_0803560A|
		LDR r0, [pc, #0x274]
		LDR r7, [pc, #0x274]
		STR r0, [r4]
		MOV r0, #0x80
		STRH r0, [r4, #0xe]
		LDR r0, [r7]
		MOV r1, #0x80
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08035630|
		MOV r1, #0x80
		LDR r0, [r7]
		BL       |sub_08011732|
		MOV r1, #0x80
		LDR r0, [r7]
		BL       |loc_0801124C|
|loc_08035630|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x254]
		STR r0, [r4]
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x1c]
		STR r2, [r4, #0x20]
		MOV r1, #0x38
		STRB r1, [r4, #8]
		SUB r5, #8
		LDR r1, [r5, #4]
		ADD r0, r4, #0
		ADD r0, #0x1c
		CMP r6, #0
		STR r1, [r4, #4]
		BNE      |loc_08035654|
		LDR r1, [r5, #4]
		ADD r1, #0x2c
		STR r1, [r4, #4]
|loc_08035654|
		LDR r1, [sp, #0x10]
		STR r1, [r4, #0x40]
		MOV r1, #0
		STR r1, [r4, #0x14]
		STRB r1, [r4, #0x10]
		MOV r1, #8
		STR r1, [r4, #0x34]
		MOV r1, #0
		MVN r1, r1
		STR r1, [r4, #0x18]
		STR r6, [r4, #0x38]
		LDMIA r5!, {r1, r2}
		STMIA r0!, {r1, r2}
		LDR r0, [r4, #0x38]
		LDR r2, [pc, #0x218]
		LSL r1, r0, #1
		ADD r1, r1, r0
		LSL r1, r1, #3
		ADD r1, r1, r2
		LDR r2, [pc, #0x208]
		LSL r0, r0, #3
		ADD r2, #8
		ADD r0, r0, r2
		STR r1, [r4, #0x3c]
		LDR r2, [r0]
		LDR r0, [r0, #4]
		LDR r5, [pc, #0x204]
		STR r0, [r4, #0x30]
		STR r2, [r4, #0x2c]
		LDRH r0, [r4, #0xc]
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r5
		MOV r2, #0x40
		BL       |Thunk_VramCopy|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, #0x40
		MOV r2, #0x40
		LDR r1, [r1, #0x14]
		BL       |Thunk_VramCopy|
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x446
