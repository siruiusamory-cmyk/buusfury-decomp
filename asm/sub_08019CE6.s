	CODE16
|sub_08019CE6|
|unk_08019CE6|
		STR r1, [r0, #0x14]
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x48f2
|loc_08019CEC|
|unk_08019CEC|
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |Thunk_JumpRegister1|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x48f2
|loc_08019CFC|
|unk_08019CFC|
		ADD r0, r1, #0
		B        |inc_0x153f2_0x1a3f2| + 0x48f2
