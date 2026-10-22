	CODE16
|sub_0800A718|
|unk_0800A718|
		LDR r1, [r0]
		ADD r4, r0, #0
		LDR r2, [r1, #0x4c]
		ADD r3, r2, r1
		ADD r1, r5, #0
		ADD r1, #0x28
		MOV r2, #1
		ADD r7, r1, #0
		BL       |inc_0x046118_0x049114| + 0x98e
|loc_0800A72C|
|unk_0800A72C|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x50]
		ADD r2, r2, r1
		ADD r1, r5, #0
		ADD r1, #0x38
		ADD r6, r1, #0
		BL       |Thunk_JumpRegister1|
		LDR r1, [r4]
		ADD r5, r0, #0
		LDR r2, [r1, #0x4c]
		ADD r0, r4, #0
		ADD r3, r2, r1
		ADD r1, r6, #0
		CMP r5, #0
		BNE      |loc_0800A750|
		ADD r1, r7, #0
|loc_0800A750|
		MOV r2, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		ADD r0, r5, #0
		B        |inc_0x0158_0x143f2| + 0xa5be
