	CODE16
|sub_080222F8|
|unk_080222F8|
		LDR r6, [pc, #0x304]
		LDR r7, [pc, #0x30c]
		LDRB r5, [r6]
		LDRB r0, [r6, #1]
		MUL r5, r0
		LDR r0, [pc, #0x300]
		ADD r1, r5, #0
		STR r0, [r4]
		STRH r5, [r4, #0xe]
		LDR r0, [r7, #4]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08022324|
		ADD r1, r5, #0
		LDR r0, [r7, #4]
		BL       |sub_08011732|
		ADD r1, r5, #0
		LDR r0, [r7, #4]
		BL       |loc_0801124C|
|loc_08022324|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LDR r1, [pc, #0x2e0]
		STRH r0, [r4, #0xc]
		STR r1, [r4]
		LDR r1, [pc, #0x2d0]
		MOV r2, #8
		SUB r1, #2
		STR r1, [r4, #0x28]
		STRB r2, [r4, #8]
		LDRB r2, [r6]
		LDRB r3, [r6, #1]
		LSL r0, r0, #5
		LDR r1, [r1, #8]
		MUL r2, r3
		LDR r3, [pc, #0x2cc]
		ADD r0, r0, r3
		BL       |Thunk_VramCopy|
		LDR r0, [pc, #0x2c8]
		STR r0, [r4]
		LDR r1, [sp, #8]
		LDR r0, [pc, #0x2c4]
		LDR r2, [r1]
		LDR r1, [r1, #4]
		STR r0, [r4]
		STR r1, [r4, #0x30]
		STR r2, [r4, #0x2c]
		LDR r0, [r4, #0x28]
		STR r0, [r4, #0x34]
		MOV r0, #0
		STR r0, [r4, #0x38]
		ADD r0, r4, #0
		DCW     0xE7C5
