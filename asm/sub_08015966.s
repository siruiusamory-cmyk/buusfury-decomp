	CODE16
|sub_08015966|
|unk_08015966|
		LDR r0, [r2, #4]
		LDR r2, [r0]
		LDR r3, [r2, #0x34]
		ADD r2, r3, r2
		BL       |Thunk_JumpRegister1|
		MOV r1, #1
		SUB r0, r1, r0
		B        |inc_0x153f2_0x1a3f2| + 0x572
