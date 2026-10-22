	CODE16
|sub_080279F8|
|unk_080279F8|
		LDR r0, [pc, #0x13c]
		LDR r6, [pc, #0x140]
		STR r0, [r4]
		MOV r0, #0x40
		STRH r0, [r4, #0xe]
		LDR r0, [r6]
		MOV r1, #0x40
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08027A1E|
		MOV r1, #0x40
		LDR r0, [r6]
		BL       |sub_08011732|
		MOV r1, #0x40
		LDR r0, [r6]
		BL       |loc_0801124C|
|loc_08027A1E|
		LSL r7, r0, #0x10
		LSR r7, r7, #0x10
		LDR r0, [pc, #0x11c]
		STRH r7, [r4, #0xc]
		STR r0, [r4]
		LDR r0, [r5]
		SUB r0, #8
		STR r0, [r4, #0x10]
		LDR r0, [r5, #4]
		SUB r0, #8
		STR r0, [r4, #0x14]
		LDR r0, [r6, #4]
		LDR r1, [r5]
		ADD r6, r0, #0
		LDR r0, [r5, #8]
		ADD r6, #0x94
		SUB r0, r0, r1
		LSL r1, r0, #0x16
		LDR r0, [r6]
		BL       |sub_08046E58|
		STR r0, [r4, #0x18]
		LDR r0, [r5, #0xc]
		LDR r1, [r5, #4]
		SUB r0, r0, r1
		LSL r1, r0, #0x16
		LDR r0, [r6, #4]
		BL       |sub_08046E58|
		STR r0, [r4, #0x1c]
		MOV r0, #0
		STR r0, [r4, #4]
		STRB r0, [r4, #8]
		LDR r1, [pc, #0xe0]
		LSL r0, r7, #5
		ADD r0, r0, r1
		LDR r1, [pc, #0xd4]
		MOV r2, #0x40
		ADD r1, #8
		BL       |Thunk_VramCopy|
		ADD r0, r4, #0
		DCW     0xE7C0
