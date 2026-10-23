	CODE16
|sub_080353FC|
|unk_080353FC|
		LDRH r0, [r4, #0x12]
		LDR r6, [sp, #0x44]
		ADD r6, #4
		ADD r7, r6, #4
		CMP r0, #0
		BNE      |loc_080354CE|
		ADD r5, sp, #8
		ADD r0, r5, #0
		BL       |Object_WriteBounds1|
		ADD r1, r5, #0
		ADD r0, sp, #0x18
		BL       |inc_0x049120_0x055620| + 0x67e0
		ADD r1, r4, #0
		ADD r5, sp, #0x20
		ADD r0, r5, #0
		BL       |Object_WriteBounds1|
		ADD r1, r5, #0
		ADD r0, sp, #0x30
		BL       |inc_0x049120_0x055620| + 0x67e0
		LDR r0, [sp, #0x18]
		LDR r1, [sp, #0x30]
		LDR r2, [sp, #0x34]
		SUB r0, r0, r1
		LDR r1, [sp, #0x1c]
		STR r0, [sp]
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #4]
		STR r1, [sp, #0x3c]
		STR r0, [sp, #0x38]
		BGE      |loc_08035446|
		NEG r0, r2
|loc_08035446|
		ADD r1, r0, #0
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BGE      |loc_08035450|
		NEG r0, r0
|loc_08035450|
		STR r0, [sp, #0x34]
		ADD r0, r1, #0
		STR r1, [sp, #0x30]
		LDR r1, [sp, #0x34]
		CMP r0, r1
		BLE      |loc_0803546A|
		LDR r2, [sp, #0x38]
		MOV r1, #2
		CMP r2, #0
		BGT      |loc_08035466|
		MOV r1, #3
|loc_08035466|
		STRB r1, [r4, #0x10]
		B        |loc_08035478|
|loc_0803546A|
		ADD r0, r1, #0
		LDR r2, [sp, #0x3c]
		MOV r1, #1
		CMP r2, #0
		BGT      |loc_08035476|
		MOV r1, #0
|loc_08035476|
		STRB r1, [r4, #0x10]
|loc_08035478|
		CMP r0, #0
		BNE      |loc_0803547E|
		MOV r0, #1
|loc_0803547E|
		LDR r1, [sp, #0x38]
		LDR r2, [sp, #0x3c]
		LSL r1, r1, #8
		STR r1, [r6]
		LSL r2, r2, #8
		STR r2, [r7]
		LDR r1, [sp, #0x40]
		LDR r2, [r6]
		LDR r3, [r7]
		MUL r2, r1
		MUL r3, r1
		ASR r1, r3, #8
		ASR r2, r2, #8
		STR r1, [sp, #0x24]
		ADD r1, r2, #0
		STR r2, [sp, #0x20]
		LDR r2, [sp, #0x24]
		STR r1, [sp, #0x28]
		LSL r1, r1, #8
		LSL r5, r0, #8
		ADD r0, r5, #0
		STR r2, [sp, #0x2c]
		BL       |Thunk_SignedDivide|
		STR r0, [sp, #0x1c]
		LDR r0, [sp, #0x2c]
		LSL r1, r0, #8
		ADD r0, r5, #0
		BL       |Thunk_SignedDivide|
		LDR r1, [sp, #0x1c]
		STR r0, [sp, #0x24]
		ADD r0, r1, #0
		STR r1, [sp, #0x20]
		LDR r1, [sp, #0x24]
		STR r0, [sp, #0x30]
		STR r1, [sp, #0x34]
		STR r0, [r6]
		LDR r0, [sp, #0x34]
		STR r0, [r7]
|loc_080354CE|
		ADD r5, r4, #0
		ADD r5, #0xff
		ADD r5, #0xa1
		LDR r0, [r5]
		LDR r1, [r6]
		ADD r6, r5, #4
		SUB r0, r0, r1
		LDR r1, [r5, #4]
		LDR r2, [r7]
		STR r0, [sp, #0x28]
		SUB r1, r1, r2
		STR r1, [sp, #0x2c]
		STR r1, [sp, #0x34]
		STR r1, [sp, #0x3c]
		STR r0, [sp, #0x30]
		STR r0, [sp, #0x38]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x38
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_08035518|
		LDR r0, [sp, #0x38]
		STR r0, [r5]
		LDR r0, [sp, #0x3c]
		STR r0, [r6]
		B        |loc_0803559E|
|loc_08035518|
		LDR r1, [sp, #0x44]
		ADD r3, sp, #0x30
		LDR r0, [r1, #4]
		CMP r0, #0
		BGE      |loc_0803552C|
		LDR r0, [sp, #0x40]
		NEG r0, r0
		STR r0, [sp, #0x2c]
		ADD r0, sp, #0x2c
		B        |loc_0803552E|
|loc_0803552C|
		ADD r0, sp, #0x40
|loc_0803552E|
		LDR r1, [r5]
		LDR r0, [r0]
		ADD r3, sp, #0x30
		SUB r0, r1, r0
		STR r0, [sp, #0x30]
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa5
		ADD r7, r0, #0
		LDR r0, [r0]
		STR r0, [sp, #0x34]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, r3, #0
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_08035560|
		LDR r0, [sp, #0x30]
		STR r0, [r5]
		LDR r0, [sp, #0x34]
		STR r0, [r6]
		B        |loc_0803559E|
|loc_08035560|
		LDR r0, [r5]
		LDR r1, [sp, #0x44]
		STR r0, [sp, #0x30]
		LDR r1, [r1, #8]
		ADD r0, r7, #0
		CMP r1, #0
		ADD r3, sp, #0x30
		BGE      |loc_0803557A|
		LDR r1, [sp, #0x40]
		NEG r1, r1
		STR r1, [sp, #0x2c]
		ADD r1, sp, #0x2c
		B        |loc_0803557C|
|loc_0803557A|
		ADD r1, sp, #0x40
|loc_0803557C|
		LDR r0, [r0]
		LDR r1, [r1]
		SUB r0, r0, r1
		STR r0, [sp, #0x34]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, r3, #0
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_080355B0|
		LDR r0, [sp, #0x30]
		STR r0, [r5]
		LDR r0, [sp, #0x34]
		STR r0, [r6]
|loc_0803559E|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x238
|loc_080355B0|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x238
	CODE16
|dat_080355C2|
	DCW      0x0000
	DCW      0x6eec
	DCW      0x087b
	DCW      0x1c34
	DCW      0x0300
	DCW      0xfe80
	DCW      0xffff
	DCW      0xb210
	DCW      0x0804
	DCW      0xb508
	DCW      0x200c
	DCW      0xf007
	DCW      0xffee
	DCW      0x2800
	DCW      0xd001
	DCW      0x4901
	DCW      0x6001
|loc_080355E4|
	DCW      0xbd08
|sub_080355E6|
|unk_080355E6|
	INCBIN	baserom.gba_0x355e6_0x355ea.extracted
|sub_080355EA|
	DCW      0x0804

