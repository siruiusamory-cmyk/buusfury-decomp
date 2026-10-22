	CODE16
|sub_080109C8|
|unk_080109C8|
		ADD r3, r5, #0
		ADD r1, r7, #0
		ADD r0, r4, #0
		LDR r2, [pc, #0x194]
		BL       |inc_0x0158_0x143f2| + 0xe560
		LDR r0, [pc, #0x190]
		MOV r2, #1
		STR r0, [r4]
		MOV r0, #0x45
		LSL r0, r0, #3
		ADD r1, r4, r0
		LDR r0, [pc, #0x188]
		LSL r2, r2, #9
		ADD r5, r4, r2
		STR r4, [r0]
		ADD r0, #8
		STR r0, [r5, #0x24]
		ADD r2, #0x20
		ADD r2, r4, r2
		MOV r0, #0
		STRH r0, [r2, #0x10]
		STR r0, [r5, #0x34]
		STR r0, [r1]
		CMP r6, #0
		BEQ      |loc_08010A36|
		LDR r0, [pc, #0x144]
		MOV r3, #0x68
		SUB r0, #0x78
		LDR r0, [r0, #8]
		LDRB r1, [r0]
		MUL r1, r3
		ADD r0, r1, r0
		MOV r1, #0x9f
		LSL r1, r1, #3
		ADD r0, r0, r1
		LDRB r0, [r0, #0x14]
		LDR r1, [pc, #0x15c]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		BL       |inc_0x153f2_0x1a3f2| + 0x1d58
		STR r0, [r5, #0x2c]
		LDR r1, [r0]
		LDR r2, [r1]
		ADD r2, r2, r1
		ADD r1, r4, #0
		BL       |Thunk_JumpRegister1|
		MOV r1, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x1081c
|loc_08010A36|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x1086e
