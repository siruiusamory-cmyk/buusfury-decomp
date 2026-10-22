	CODE16
|sub_0803C71C|
|unk_0803C71C|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x7558
