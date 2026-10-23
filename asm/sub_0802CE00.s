	CODE16
|sub_0802CE00|
|unk_0802CE00|
		LDR r0, [pc, #0x288]
		LDR r1, [r0]
		CMP r1, #0
		BNE      |loc_0802CE0C|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x12b0
|loc_0802CE0C|
		ADD r0, sp, #8
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #8]
		LDR r1, [sp, #0x10]
		LDR r2, [sp, #0x14]
		ADD r1, r0, r1
		LDR r0, [sp, #0xc]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp]
		STR r1, [sp, #0x18]
		STR r0, [sp, #4]
		STR r0, [sp, #0x1c]
		MOV r5, #1
		ADD r1, r6, #0
		ADD r0, sp, #0x20
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0x20]
		LDR r1, [sp, #0x28]
		LDR r2, [sp, #0x2c]
		ADD r1, r0, r1
		LDR r0, [sp, #0x24]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		STR r0, [sp, #4]
		STR r0, [sp, #0x34]
		ASR r1, r1, #1
		LDR r0, [sp, #0x18]
		STR r1, [sp]
		SUB r0, r0, r1
		STR r1, [sp, #0x30]
		LDR r1, [sp, #0x1c]
		LDR r2, [sp, #0x34]
		STR r0, [sp]
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #4]
		STR r1, [sp, #0x3c]
		STR r0, [sp, #0x38]
		BGE      |loc_0802CE6E|
		NEG r0, r2
|loc_0802CE6E|
		ADD r1, r0, #0
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BGE      |loc_0802CE78|
		NEG r0, r0
|loc_0802CE78|
		ADD r7, r1, #0
		CMP r1, r0
		STR r1, [sp, #0x30]
		STR r0, [sp, #0x34]
		BLE      |loc_0802CE90|
		LDR r1, [sp, #0x38]
		MOV r0, #3
		CMP r1, #0
		BGT      |loc_0802CE8C|
		MOV r0, #2
|loc_0802CE8C|
		STRB r0, [r6, #0x10]
		B        |loc_0802CE9C|
|loc_0802CE90|
		ADD r7, r0, #0
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BLE      |loc_0802CE9A|
		MOV r5, #0
|loc_0802CE9A|
		STRB r5, [r6, #0x10]
|loc_0802CE9C|
		CMP r7, #8
		BGE      |loc_0802CEA4|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x12b0
|loc_0802CEA4|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BNE      |loc_0802CEC4|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
|loc_0802CEC4|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		LDR r0, [sp, #0x38]
		LDR r1, [sp, #0x3c]
		LSL r0, r0, #8
		LSL r1, r1, #8
		STR r1, [sp, #0x34]
		STR r0, [sp, #0x30]
		LDR r1, [r4, #4]
		LDR r2, [sp, #0x34]
		MUL r0, r1
		MUL r2, r1
		ASR r1, r2, #8
		ASR r0, r0, #8
		ADD r5, r6, #0
		ADD r5, #0xff
		STR r1, [sp, #0xc]
		STR r1, [sp, #0x14]
		LSL r1, r0, #8
		ADD r5, #0xa1
		STR r0, [sp, #8]
		STR r0, [sp, #0x10]
		LSL r7, r7, #8
		ADD r0, r7, #0
		BL       |Thunk_SignedDivide|
		STR r0, [sp, #4]
		LDR r0, [sp, #0x14]
		LSL r1, r0, #8
		ADD r0, r7, #0
		BL       |Thunk_SignedDivide|
		LDR r1, [sp, #4]
		STR r0, [sp, #0xc]
		ADD r0, r1, #0
		STR r1, [sp, #8]
		LDR r1, [sp, #0xc]
		STR r0, [sp, #0x18]
		STR r1, [sp, #0x1c]
		LDR r0, [r5]
		LDR r1, [sp, #0x18]
		ADD r7, r5, #4
		ADD r0, r0, r1
		LDR r1, [r5, #4]
		LDR r2, [sp, #0x1c]
		STR r0, [sp, #8]
		ADD r1, r1, r2
		STR r0, [sp, #0x28]
		STR r0, [sp, #0x20]
		MOV r0, #0
		STR r1, [sp, #0xc]
		STR r1, [sp, #0x24]
		STR r0, [sp, #0x24]
		STR r1, [sp, #0x2c]
		LDR r0, [r4, #8]
		CMP r0, #0
		BNE      |loc_0802CFE0|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x28
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0802CF60|
		LDR r0, [sp, #0x28]
		STR r0, [r5]
		LDR r0, [sp, #0x2c]
		STR r0, [r7]
		MOV r0, #1
		STR r0, [sp, #0x24]
		B        |loc_0802CFE0|
|loc_0802CF60|
		LDR r0, [sp, #0x28]
		STR r0, [sp, #0x1c]
		ADD r0, r6, #0
		ADD r0, #0xff
		ADD r0, #0xa5
		STR r0, [sp, #0x40]
		LDR r0, [r0]
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x28]
		LDR r1, [r5]
		SUB r0, r0, r1
		STR r0, [sp, #0x18]
		BPL      |loc_0802CF7C|
		NEG r0, r0
|loc_0802CF7C|
		MOV r1, #1
		LSL r1, r1, #0xa
		CMP r0, r1
		BLE      |loc_0802CFA4|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x1c
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0802CFA4|
		LDR r0, [sp, #0x1c]
		STR r0, [r5]
		LDR r0, [sp, #0x20]
		STR r0, [r7]
		MOV r0, #1
		STR r0, [sp, #0x24]
		B        |loc_0802CFE0|
|loc_0802CFA4|
		LDR r0, [r5]
		LDR r2, [sp, #0x2c]
		STR r0, [sp, #0x1c]
		LDR r0, [sp, #0x2c]
		ADD r1, sp, #0x1c
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x40]
		LDR r0, [r0]
		SUB r0, r2, r0
		STR r0, [sp, #0x18]
		BPL      |loc_0802CFBC|
		NEG r0, r0
|loc_0802CFBC|
		MOV r2, #1
		LSL r2, r2, #0xa
		CMP r0, r2
		BLE      |loc_0802CFE0|
		LDR r2, [r6]
		ADD r0, r6, #0
		LDR r3, [r2, #0x54]
		ADD r2, r3, r2
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0802CFE0|
		LDR r0, [sp, #0x1c]
		STR r0, [r5]
		LDR r0, [sp, #0x20]
		STR r0, [r7]
		MOV r0, #1
		STR r0, [sp, #0x24]
|loc_0802CFE0|
		LDR r0, [sp, #0x24]
		CMP r0, #0
		BNE      |loc_0802D074|
		LDR r0, [r4, #8]
		CMP r0, #0
		BNE      |loc_0802CFF6|
		MOV r0, #0x20
		BL       |inc_0x03d784_0x041118| + 0x2348
		SUB r0, #0x10
		STR r0, [r4, #8]
|loc_0802CFF6|
		LDR r0, [r5, #4]
		LDR r1, [r5]
		STR r0, [sp, #0x20]
		LDR r0, [sp, #0x38]
		STR r1, [sp, #0x1c]
		CMP r0, #0
		BGE      |loc_0802D006|
		NEG r0, r0
|loc_0802D006|
		LDR r2, [sp, #0x3c]
		CMP r2, #0
		BGE      |loc_0802D00E|
		NEG r2, r2
|loc_0802D00E|
		CMP r0, r2
		LDR r0, [r4, #8]
		ADD r1, sp, #0x1c
		BGE      |loc_0802D03A|
		CMP r0, #0
		BGE      |loc_0802D02A|
		LDR r0, [sp, #0x1c]
		LDR r2, [r4, #4]
		SUB r0, r0, r2
		STR r0, [sp, #0x1c]
		LDR r0, [r4, #8]
		ADD r0, #1
		STR r0, [r4, #8]
		B        |loc_0802D05C|
|loc_0802D02A|
		LDR r0, [sp, #0x1c]
		LDR r2, [r4, #4]
		ADD r0, r0, r2
		STR r0, [sp, #0x1c]
		LDR r0, [r4, #8]
		SUB r0, #1
		STR r0, [r4, #8]
		B        |loc_0802D05C|
|loc_0802D03A|
		CMP r0, #0
		BGE      |loc_0802D04E|
		LDR r0, [sp, #0x20]
		LDR r2, [r4, #4]
		SUB r0, r0, r2
		STR r0, [sp, #0x20]
		LDR r0, [r4, #8]
		ADD r0, #1
		STR r0, [r4, #8]
		B        |loc_0802D05C|
|loc_0802D04E|
		LDR r0, [sp, #0x20]
		LDR r2, [r4, #4]
		ADD r0, r0, r2
		STR r0, [sp, #0x20]
		LDR r0, [r4, #8]
		SUB r0, #1
		STR r0, [r4, #8]
|loc_0802D05C|
		LDR r2, [r6]
		ADD r0, r6, #0
		LDR r3, [r2, #0x54]
		ADD r2, r3, r2
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0802D076|
		LDR r0, [sp, #0x1c]
		STR r0, [r5]
		LDR r0, [sp, #0x20]
		STR r0, [r7]
|loc_0802D074|
		B        |loc_0802D07A|
|loc_0802D076|
		MOV r0, #0
		STR r0, [r4, #8]
|loc_0802D07A|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x12b0
|sub_0802D08C|
	DCW      0x1b94
	DCW      0x0300
