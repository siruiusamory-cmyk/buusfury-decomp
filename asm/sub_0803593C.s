	CODE16
|sub_0803593C|
|unk_0803593C|
		LDR r1, [r2, #0x30]
		ADD r5, r2, #0
		CMP r1, r0
		BNE      |loc_08035948|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x778
|loc_08035948|
		LDRB r1, [r5, #0x14]
		LDR r2, [r0, #0x38]
		MOV r3, #1
		EOR r2, r3
		CMP r1, r2
		BEQ      |loc_08035958|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x778
|loc_08035958|
		LDR r1, [r0, #0x34]
		LDR r2, [r0, #0x2c]
		LDR r3, [r0, #0x30]
		MUL r2, r1
		MUL r3, r1
		ADD r1, r2, #0
		STR r2, [sp, #4]
		ADD r2, r3, #0
		STR r3, [sp, #8]
		LDR r3, [r0, #0x1c]
		LDR r0, [r0, #0x20]
		ADD r1, r3, r1
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ADD r2, r0, #0
		ADD r4, r0, #0
		ADD r0, r5, #4
		STR r1, [sp, #4]
		ADD r3, r1, #0
		LDR r5, [r5, #4]
		ADD r3, #0xc
		SUB r1, #0xc
		ADD r4, #0xc
		SUB r2, #0xc
		CMP r5, r3
		BGE      |loc_080359A2|
		LDR r3, [r0, #8]
		CMP r1, r3
		BGE      |loc_080359A2|
		LDR r1, [r0, #4]
		CMP r1, r4
		BGE      |loc_080359A2|
		LDR r0, [r0, #0xc]
		CMP r2, r0
		BGE      |loc_080359A2|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x778
|loc_080359A2|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x778
|loc_080359A6|
|unk_080359A6|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x778
|loc_080359AA|
|unk_080359AA|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x778
|loc_080359AE|
|unk_080359AE|
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x778
|loc_080359BE|
|unk_080359BE|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x778
