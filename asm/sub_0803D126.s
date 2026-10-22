	CODE16
|sub_0803D126|
|unk_0803D126|
		ADD r0, sp, #0xc
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		STR r0, [sp, #8]
		STR r0, [sp, #0x20]
		ADD r0, sp, #0x24
		ADD r1, r4, #0
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0x24]
		LDR r1, [sp, #0x2c]
		LDR r2, [sp, #0x30]
		ADD r1, r0, r1
		LDR r0, [sp, #0x28]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x38]
		ASR r1, r1, #1
		LDR r0, [sp, #0x1c]
		STR r1, [sp, #4]
		SUB r0, r0, r1
		STR r1, [sp, #0x34]
		LDR r1, [sp, #0x20]
		LDR r2, [sp, #0x38]
		STR r0, [sp, #4]
		SUB r1, r1, r2
		STR r1, [sp, #8]
		STR r1, [sp, #0x40]
		ADD r1, r0, #0
		CMP r0, #0
		STR r0, [sp, #0x3c]
		BGE      |loc_0803D186|
		NEG r0, r1
|loc_0803D186|
		LDR r1, [sp, #0x40]
		CMP r1, #0
		BGE      |loc_0803D18E|
		NEG r1, r1
|loc_0803D18E|
		STR r0, [sp, #0x34]
		MOV r6, #0
		ADD r2, r0, #0
		ADD r0, r1, #0
		STR r1, [sp, #0x38]
		MOV r7, #3
		CMP r2, r1
		STR r6, [sp, #0x38]
		STR r6, [sp, #0x34]
		BLE      |loc_0803D1EE|
		CMP r0, #3
		BGE      |loc_0803D1D4|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0803D1C6|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
|loc_0803D1C6|
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BGT      |loc_0803D1CE|
		MOV r7, #2
|loc_0803D1CE|
		STRB r7, [r4, #0x10]
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x7f62
|loc_0803D1D4|
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BLE      |loc_0803D1E2|
		STRB r6, [r4, #0x10]
		LDR r0, [r5, #4]
		STR r0, [sp, #0x38]
		B        |loc_0803D25C|
|loc_0803D1E2|
		MOV r0, #1
		STRB r0, [r4, #0x10]
		LDR r0, [r5, #4]
		NEG r0, r0
		STR r0, [sp, #0x38]
		B        |loc_0803D25C|
|loc_0803D1EE|
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BGE      |loc_0803D1FC|
		LDR r0, [sp, #0x3c]
		ADD r0, #0xc
		STR r0, [sp, #0x3c]
		B        |loc_0803D202|
|loc_0803D1FC|
		LDR r0, [sp, #0x3c]
		SUB r0, #8
		STR r0, [sp, #0x3c]
|loc_0803D202|
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BGE      |loc_0803D20A|
		NEG r0, r0
|loc_0803D20A|
		LDR r2, [sp, #0x40]
		STR r0, [sp, #0x2c]
		STR r1, [sp, #0x30]
		CMP r0, #3
		BGE      |loc_0803D244|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0803D234|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
|loc_0803D234|
		LDR r1, [sp, #0x40]
		MOV r0, #1
		CMP r1, #0
		BLE      |loc_0803D23E|
		MOV r0, #0
|loc_0803D23E|
		STRB r0, [r4, #0x10]
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x7f62
|loc_0803D244|
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BLE      |loc_0803D252|
		STRB r7, [r4, #0x10]
		LDR r0, [r5, #4]
		STR r0, [sp, #0x34]
		B        |loc_0803D25C|
|loc_0803D252|
		MOV r0, #2
		STRB r0, [r4, #0x10]
		LDR r0, [r5, #4]
		NEG r0, r0
		STR r0, [sp, #0x34]
|loc_0803D25C|
		MOV r0, #0x4e
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BEQ      |loc_0803D27C|
		MOV r0, #0x11
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BEQ      |loc_0803D27C|
		MOV r0, #0x4c
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BNE      |loc_0803D29E|
|loc_0803D27C|
		LDRH r0, [r4, #0x12]
		CMP r0, #0
		BEQ      |loc_0803D286|
		CMP r0, #0x10
		BNE      |loc_0803D29E|
|loc_0803D286|
		LDR r0, [pc, #0xdc]
		MOV r1, #0x27
		LDR r2, [pc, #0xdc]
		LSL r1, r1, #4
		ADD r1, r1, r2
		LDR r5, [pc, #0xd8]
		LDR r0, [r0]
		MOV r2, #0x40
		ADD r3, r6, #0
		ADD r0, r0, r5
		BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_0803D29E|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		ADD r5, r4, #0
		ADD r5, #0xff
		ADD r5, #0xa1
		LDR r0, [r5]
		LDR r1, [sp, #0x34]
		ADD r6, r5, #4
		ADD r0, r0, r1
		LDR r1, [r5, #4]
		LDR r2, [sp, #0x38]
		STR r0, [sp, #0x1c]
		ADD r1, r1, r2
		STR r1, [sp, #0x20]
		STR r1, [sp, #0x28]
		STR r1, [sp, #0x30]
		STR r0, [sp, #0x24]
		STR r0, [sp, #0x2c]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x2c
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0803D318|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BNE      |loc_0803D2FE|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
|loc_0803D2FE|
		LDR r0, [sp, #0x2c]
		STR r0, [r5]
		LDR r0, [sp, #0x30]
		STR r0, [r6]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x7f62
|loc_0803D318|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0803D338|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
|loc_0803D338|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x7f62
