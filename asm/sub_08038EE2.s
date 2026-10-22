	CODE16
|sub_08038EE2|
|unk_08038EE2|
		MOV r0, #1
		STR r0, [r4, #0x60]
		LDRB r0, [r4, #0x10]
		CMP r0, #1
		BNE      |loc_08038F00|
		LDR r0, [r4, #0x4c]
		CMP r0, #0
		BEQ      |loc_08038F12|
		LDR r1, [r0]
		LDR r2, [r1, #0x10]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |Thunk_JumpRegister1|
		B        |loc_08038F12|
|loc_08038F00|
		LDR r0, [r4, #0x48]
		CMP r0, #0
		BEQ      |loc_08038F12|
		LDR r1, [r0]
		LDR r2, [r1, #0x10]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |Thunk_JumpRegister1|
|loc_08038F12|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |sub_08019C44|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x3d20
