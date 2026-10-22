	CODE16
|sub_0801CDD6|
|unk_0801CDD6|
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
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #8]
		STR r1, [sp, #0x40]
		STR r0, [sp, #0x3c]
		BGE      |loc_0801CE36|
		NEG r0, r2
|loc_0801CE36|
		ADD r1, r0, #0
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BGE      |loc_0801CE40|
		NEG r0, r0
|loc_0801CE40|
		STR r1, [sp, #0x34]
		STR r0, [sp, #0x38]
		ADD r0, r1, #0
		MOV r6, #0
		LDR r1, [sp, #0x38]
		MOV r7, #3
		CMP r0, r1
		STR r6, [sp, #0x38]
		STR r6, [sp, #0x34]
		BLE      |loc_0801CEA0|
		CMP r1, #3
		BGE      |loc_0801CE86|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0801CE78|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
|loc_0801CE78|
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BGT      |loc_0801CE80|
		MOV r7, #2
|loc_0801CE80|
		STRB r7, [r4, #0x10]
		MOV r0, #1
		DCW     0xE7A5
|loc_0801CE86|
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BLE      |loc_0801CE94|
		STRB r6, [r4, #0x10]
		LDR r0, [r5, #4]
		STR r0, [sp, #0x38]
		B        |loc_0801CEEC|
|loc_0801CE94|
		MOV r0, #1
		STRB r0, [r4, #0x10]
		LDR r0, [r5, #4]
		NEG r0, r0
		STR r0, [sp, #0x38]
		B        |loc_0801CEEC|
|loc_0801CEA0|
		CMP r0, #3
		BGE      |loc_0801CED4|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0801CEC4|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
|loc_0801CEC4|
		LDR r1, [sp, #0x40]
		MOV r0, #1
		CMP r1, #0
		BLE      |loc_0801CECE|
		MOV r0, #0
|loc_0801CECE|
		STRB r0, [r4, #0x10]
		MOV r0, #1
		DCW     0xE77E
|loc_0801CED4|
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BLE      |loc_0801CEE2|
		STRB r7, [r4, #0x10]
		LDR r0, [r5, #4]
		STR r0, [sp, #0x34]
		B        |loc_0801CEEC|
|loc_0801CEE2|
		MOV r0, #2
		STRB r0, [r4, #0x10]
		LDR r0, [r5, #4]
		NEG r0, r0
		STR r0, [sp, #0x34]
|loc_0801CEEC|
		MOV r0, #0x4e
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BEQ      |loc_0801CF0C|
		MOV r0, #0x11
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BEQ      |loc_0801CF0C|
		MOV r0, #0x4c
		BL       |inc_0x0158_0x143f2|
		CMP r0, r5
		BNE      |loc_0801CF2E|
|loc_0801CF0C|
		LDRH r0, [r4, #0x12]
		CMP r0, #0
		BEQ      |loc_0801CF16|
		CMP r0, #0x10
		BNE      |loc_0801CF2E|
|loc_0801CF16|
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
|loc_0801CF2E|
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
		BEQ      |loc_0801CFA8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BNE      |loc_0801CF8E|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
|loc_0801CF8E|
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
		DCW     0xE714
|loc_0801CFA8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0801CFC8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
|loc_0801CFC8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		MOV r0, #1
		DCW     0xE6FB
