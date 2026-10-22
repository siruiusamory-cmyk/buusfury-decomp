	CODE16
|sub_08012552|
|unk_08012552|
		LDRH r0, [r1]
		STRH r0, [r4, #8]
		LDRB r0, [r1, #2]
		LSL r0, r0, #2
		LDR r2, [r5, r0]
		ADD r0, r4, #0
		BL       |Thunk_JumpRegister1|
		STR r0, [r4, #0x28]
		LDR r1, [r0]
		LDR r2, [r1, #4]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BNE      |inc_0x0158_0x143f2| + 0x123aa
		LDR r0, [r4, #0x28]
		CMP r0, #0
		BEQ      |loc_08012584|
		LDR r1, [r0]
		LDR r2, [r1]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |Thunk_JumpRegister1|
|loc_08012584|
		STR r6, [r4, #0x28]
		B        |loc_08012530|
