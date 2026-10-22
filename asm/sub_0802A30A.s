	CODE16
|sub_0802A30A|
|unk_0802A30A|
		LDR r0, [pc, #0x274]
		LDR r7, [pc, #0x274]
		STR r0, [r4]
		MOV r0, #0x80
		STRH r0, [r4, #0xe]
		LDR r0, [r7, #4]
		MOV r1, #0x80
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0802A330|
		MOV r1, #0x80
		LDR r0, [r7, #4]
		BL       |sub_08011732|
		MOV r1, #0x80
		LDR r0, [r7, #4]
		BL       |loc_0801124C|
|loc_0802A330|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x254]
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
		BNE      |loc_0802A358|
		LDR r1, [r5, #4]
		ADD r1, #0x2c
		STR r1, [r4, #4]
|loc_0802A358|
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
		LDMIA r5!, {r1, r3}
		STMIA r0!, {r1, r3}
		SUB r5, #8
		LDMIA r5!, {r1, r3}
		STR r1, [r4, #0x20]
		STR r3, [r4, #0x24]
		LDR r0, [r4, #0x44]
		LDR r3, [pc, #0x210]
		LSL r1, r0, #3
		ADD r1, r1, r0
		LSL r1, r1, #2
		ADD r1, r1, r3
		STR r1, [r4, #0x48]
		LDR r1, [pc, #0x208]
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [r0]
		LDR r0, [r0, #4]
		ADD r3, r2, #0
		STR r0, [r4, #0x3c]
		STR r1, [r4, #0x38]
		LDR r0, [r7]
		LDR r5, [pc, #0x1fc]
		MOV r2, #0x40
		ADD r0, r0, r5
		LDR r1, [pc, #0x1f4]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		DCW     0xE7AE
