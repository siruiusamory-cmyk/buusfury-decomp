	CODE16
|sub_0803B57E|
|unk_0803B57E|
		LDR r1, [sp, #0x2c]
		LDR r2, [sp, #0x4c]
		LDR r3, [sp, #0x50]
		ADD r1, r1, r2
		LDR r2, [sp, #0x30]
		STR r1, [sp, #0x14]
		ADD r2, r2, r3
		STR r2, [sp, #0x18]
		STR r2, [sp, #0x20]
		STR r1, [sp, #0x1c]
		ADD r0, r4, #0
		LDR r1, [r0]
		ADD r3, sp, #0x1c
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, r3, #0
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |sub_0803B5AA|
		MOV r5, #1
		B        |inc_0x351c0_0x3d4d0| + 0x63f2
