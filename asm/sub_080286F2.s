	CODE16
|sub_080286F2|
|unk_080286F2|
		LDR r0, [pc, #0x2c8]
		LDR r7, [pc, #0x2c8]
		STR r0, [r4]
		MOV r0, #0xc0
		STRH r0, [r4, #0xe]
		LDR r0, [r7]
		MOV r1, #0xc0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08028718|
		MOV r1, #0xc0
		LDR r0, [r7]
		BL       |sub_08011732|
		MOV r1, #0xc0
		LDR r0, [r7]
		BL       |loc_0801124C|
|loc_08028718|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x2a8]
		STR r0, [r4]
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x28]
		STR r2, [r4, #0x2c]
		MOV r2, #0
		STR r2, [r4, #0x1c]
		MOV r1, #0x38
		STRB r1, [r4, #8]
		SUB r5, #8
		LDR r1, [r5, #4]
		ADD r0, r4, #0
		ADD r0, #0x28
		CMP r6, #0
		STR r1, [r4, #4]
		BNE      |loc_08028740|
		LDR r1, [r5, #4]
		ADD r1, #0x2c
		STR r1, [r4, #4]
|loc_08028740|
		LDR r1, [sp, #0x10]
		STR r1, [r4, #0x4c]
		STR r2, [r4, #0x14]
		STRB r2, [r4, #0x10]
		MOV r1, #8
		STR r1, [r4, #0x40]
		MOV r1, #0
		MVN r1, r1
		STR r1, [r4, #0x18]
		STR r6, [r4, #0x44]
		LDMIA r5!, {r1, r2}
		STMIA r0!, {r1, r2}
		SUB r5, #8
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x20]
		STR r2, [r4, #0x24]
		LDR r0, [r4, #0x44]
		LDR r2, [pc, #0x264]
		LSL r1, r0, #4
		SUB r1, r1, r0
		LSL r1, r1, #2
		ADD r1, r1, r2
		STR r1, [r4, #0x48]
		LDR r1, [pc, #0x250]
		LSL r0, r0, #3
		ADD r1, #0x14
		ADD r0, r0, r1
		LDR r1, [r0]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x3c]
		STR r1, [r4, #0x38]
		ADD r0, r4, #0
		DCW     0xE7B5
