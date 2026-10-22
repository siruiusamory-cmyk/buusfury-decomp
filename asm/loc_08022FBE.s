	CODE16
|loc_08022FBE|
		LDR r0, [r4, #0x2c]
		CMP r0, #0
		BEQ      |loc_08022FCC|
		ADD r1, r0, #0
		LDR r0, [r6, #0x1c]
		BL       |loc_08011944|
|loc_08022FCC|
		LDR r0, [r4, #0x30]
		STR r0, [r4, #0x2c]
		LDR r0, [r4, #0x34]
		STR r0, [r4, #0x30]
		LDR r1, [r4, #0x38]
		STR r1, [r4, #0x34]
		LDR r1, [r4, #0x3c]
		STR r1, [r4, #0x38]
		MOV r1, #0
		STR r1, [r4, #0x3c]
		CMP r0, #0
		BEQ      |loc_08022FF0|
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
|loc_08022FF0|
		LDR r0, [r4, #0x34]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		LDR r1, [r4, #0x1c]
		LDR r0, [sp]
		ADD r1, #2
		CMP r1, r0
		BGE      |loc_08023018|
		ADD r0, r5, #0
		BL       |loc_08022DAA|
		ADD r1, r0, #0
		STR r0, [r4, #0x3c]
		LDR r0, [r6, #0x1c]
		BL       |List_Append|
|loc_08023018|
		MOV r0, #0
		MOV r6, #0x6a
|loc_0802301C|
		LSL r1, r0, #2
		ADD r1, r1, r5
		ADD r1, #0xff
		ADD r1, #1
		LDR r2, [r1, #0x2c]
		CMP r2, #0
		BEQ      |loc_08023046|
		ADD r1, r2, #0
		LDR r2, [r2, #0x58]
		ADD r1, #0x6c
		LDRB r3, [r2, #8]
		LDRB r2, [r2, #9]
		LSR r4, r3, #1
		MOV r3, #0x2a
		MUL r3, r0
		ADD r3, #0x23
		SUB r3, r3, r4
		LSR r2, r2, #1
		SUB r2, r6, r2
		STR r2, [r1, #4]
		STR r3, [r1]
|loc_08023046|
		ADD r0, #1
		CMP r0, #5
		BLT      |loc_0802301C|
		DCW     0xE017
