	CODE16
|sub_08029A74|
|unk_08029A74|
		LDRB r0, [r5, #0x10]
		LDRB r1, [r4, #0x10]
		MOV r2, #1
		EOR r1, r2
		CMP r0, r1
		BEQ      |loc_08029A84|
		MOV r0, #0
		DCW     0xE7F5
|loc_08029A84|
		LDR r0, [r4, #0x14]
		LDR r1, [r0]
		LDR r2, [r1, #0x1c]
		ADD r2, r2, r1
		ADD r1, r4, #0
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BNE      |loc_08029A98|
		DCW     0xE7EB
|loc_08029A98|
		ADD r1, r4, #0
		ADD r0, sp, #0x14
		BL       |Object_GetPoints|
		ADD r1, r5, #0
		ADD r0, sp, #4
		BL       |Object_GetPoints|
		LDRB r0, [r4, #0x10]
		CMP r0, #0
		BEQ      |loc_08029AF0|
		CMP r0, #1
		BEQ      |loc_08029B04|
		CMP r0, #2
		BEQ      |loc_08029B18|
		CMP r0, #3
		BNE      |loc_08029ACC|
		LDR r0, [sp, #0x18]
		SUB r0, #4
		STR r0, [sp, #0x18]
		LDR r0, [sp, #0x20]
		ADD r0, #4
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x1c]
		ADD r0, #0xf0
		STR r0, [sp, #0x1c]
|loc_08029ACC|
		LDR r0, [sp, #4]
		LDR r1, [sp, #0x1c]
		CMP r0, r1
		BGE      |loc_08029B2C|
		LDR r0, [sp, #0x14]
		LDR r1, [sp, #0xc]
		CMP r0, r1
		BGE      |loc_08029B2C|
		LDR r0, [sp, #8]
		LDR r1, [sp, #0x20]
		CMP r0, r1
		BGE      |loc_08029B2C|
		LDR r0, [sp, #0x18]
		LDR r1, [sp, #0x10]
		CMP r0, r1
		BGE      |loc_08029B2C|
		MOV r0, #1
		DCW     0xE7BF
|loc_08029AF0|
		LDR r0, [sp, #0x14]
		SUB r0, #4
		STR r0, [sp, #0x14]
		LDR r0, [sp, #0x1c]
		ADD r0, #4
		STR r0, [sp, #0x1c]
		LDR r0, [sp, #0x20]
		ADD r0, #0xf0
		STR r0, [sp, #0x20]
		B        |loc_08029ACC|
|loc_08029B04|
		LDR r0, [sp, #0x14]
		SUB r0, #4
		STR r0, [sp, #0x14]
		LDR r0, [sp, #0x1c]
		ADD r0, #4
		STR r0, [sp, #0x1c]
		LDR r0, [sp, #0x18]
		SUB r0, #0xf0
		STR r0, [sp, #0x18]
		B        |loc_08029ACC|
|loc_08029B18|
		LDR r0, [sp, #0x18]
		SUB r0, #4
		STR r0, [sp, #0x18]
		LDR r0, [sp, #0x20]
		ADD r0, #4
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x14]
		SUB r0, #0xf0
		STR r0, [sp, #0x14]
		B        |loc_08029ACC|
|loc_08029B2C|
		MOV r0, #0
		DCW     0xE79F
