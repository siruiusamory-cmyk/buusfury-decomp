	CODE16
|sub_08028F56|
|unk_08028F56|
		LDR r0, [r2, #0x30]
		CMP r0, r4
		BNE      |loc_08028F60|
		MOV r0, #0
		DCW     0xE7F8
|loc_08028F60|
		LDRB r0, [r2, #0x14]
		LDR r1, [r4, #0x38]
		MOV r3, #1
		EOR r1, r3
		CMP r0, r1
		BEQ      |loc_08028F70|
		MOV r0, #0
		DCW     0xE7F0
|loc_08028F70|
		LDR r0, [r4, #0x34]
		LDR r1, [r4, #0x2c]
		LDR r3, [r4, #0x30]
		MUL r1, r0
		MUL r3, r0
		ADD r0, r1, #0
		STR r1, [sp, #4]
		ADD r1, r3, #0
		STR r3, [sp, #8]
		LDR r3, [r4, #0x1c]
		ADD r2, #4
		ADD r0, r3, r0
		LDR r3, [r4, #0x20]
		STR r0, [sp, #4]
		ADD r1, r3, r1
		STR r1, [sp, #8]
		ADD r4, r1, #0
		ADD r3, r0, #0
		LDR r5, [r2]
		ADD r3, #0xc
		SUB r0, #0xc
		ADD r4, #0xc
		SUB r1, #0xc
		CMP r5, r3
		BGE      |loc_08028FB8|
		LDR r3, [r2, #8]
		CMP r0, r3
		BGE      |loc_08028FB8|
		LDR r0, [r2, #4]
		CMP r0, r4
		BGE      |loc_08028FB8|
		LDR r0, [r2, #0xc]
		CMP r1, r0
		BGE      |loc_08028FB8|
		MOV r0, #1
		DCW     0xE7CC
|loc_08028FB8|
		MOV r0, #0
		DCW     0xE7CA
|loc_08028FBC|
|unk_08028FBC|
		MOV r0, #0
		DCW     0xE7C8
|loc_08028FC0|
|unk_08028FC0|
		LDRH r0, [r4, #0xc]
		LDR r5, [pc, #0x4c]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #5
		ADD r0, r0, r5
		MOV r2, #0x40
		LDR r1, [r1, #8]
		BL       |Thunk_VramCopy|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x3c]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, #0x40
		MOV r2, #0x80
		LDR r1, [r1, #0x14]
		BL       |Thunk_VramCopy|
		MOV r0, #0
		DCW     0xE7B4
|loc_08028FE8|
|unk_08028FE8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #0
		DCW     0xE7AB
|loc_08028FFA|
|unk_08028FFA|
		MOV r0, #0
		DCW     0xE7A9
