	CODE16
|sub_08022E8C|
|unk_08022E8C|
		LDR r0, [r4, #0x34]
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		DCW     0xD107
		LDR r0, [r4, #0x34]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
|loc_08022EAC|
|unk_08022EAC|
		DCW     0xE086
		LDR r0, [r4, #0x30]
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BNE      |loc_08022ED0|
		LDR r0, [r4, #0x30]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		B        |loc_08022FBC|
|loc_08022ED0|
		LDR r0, [r4, #0x38]
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		DCW     0xD109
		LDR r0, [r4, #0x38]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		B        |loc_08022FBC|
|loc_08022EF2|
|unk_08022EF2|
		DCW     0xE022
|loc_08022EF4|
|unk_08022EF4|
		B        |loc_08022FBE|
		LDR r0, [r4, #0x2c]
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BNE      |loc_08022F18|
		LDR r0, [r4, #0x2c]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		B        |loc_08022FBC|
|loc_08022F18|
		LDR r0, [r4, #0x3c]
		LDR r1, [r0]
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BNE      |loc_08022FBC|
		LDR r0, [r4, #0x3c]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		B        |loc_08022FBC|
		LDR r7, [r4, #0x1c]
		LDR r6, [pc, #0x148]
		SUB r7, #2
		LDR r0, [r6, #0x1c]
		BL       |loc_08011B04|
		MOV r6, #0
|loc_08022F48|
		CMP r7, #0
		BLT      |loc_08022FA8|
		LDR r0, [sp]
		CMP r7, r0
		BGE      |loc_08022FA8|
		ADD r1, r7, #0
		ADD r0, r5, #0
		BL       |loc_08022DAA|
		LSL r1, r6, #2
		ADD r1, r1, r5
		ADD r1, #0xff
		ADD r1, #1
		STR r1, [sp, #4]
		STR r0, [r1, #0x2c]
		LDR r1, [r4, #0x1c]
		CMP r1, r7
		BNE      |loc_08022F78|
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
|loc_08022F78|
		LDR r1, [sp, #4]
		MOV r3, #0x2a
		LDR r1, [r1, #0x2c]
		MUL r3, r6
		ADD r0, r1, #0
		LDR r1, [r1, #0x58]
		ADD r3, #0x23
		LDRB r2, [r1, #8]
		LDRB r1, [r1, #9]
		ADD r0, #0x6c
		LSR r2, r2, #1
		SUB r2, r3, r2
		MOV r3, #0x6a
		LSR r1, r1, #1
		SUB r1, r3, r1
		STR r1, [r0, #4]
		STR r2, [r0]
		LDR r1, [sp, #4]
		LDR r0, [pc, #0xe8]
		LDR r1, [r1, #0x2c]
		LDR r0, [r0, #0x1c]
		BL       |List_Append|
		B        |loc_08022FB4|
|loc_08022FA8|
		LSL r0, r6, #2
		ADD r0, r0, r5
		ADD r0, #0xff
		MOV r1, #0
		ADD r0, #1
		STR r1, [r0, #0x2c]
|loc_08022FB4|
		ADD r7, #1
		ADD r6, #1
		CMP r6, #5
		BLT      |loc_08022F48|
|loc_08022FBC|
		DCW     0xE05F
