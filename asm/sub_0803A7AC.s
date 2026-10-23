	CODE16
|sub_0803A7AC|
|unk_0803A7AC|
		ADD r1, r2, #0
		ADD r1, #0x18
		LDR r2, [r3, #0xc]
		LDR r1, [r1]
		MUL r1, r2
		ASR r1, r1, #0x10
		STR r1, [sp]
		LDR r1, [r0]
		LDR r2, [r1, #0x60]
		ADD r2, r2, r1
		MOV r1, sp
		BL       |Thunk_JumpRegister1|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x55ea
|sub_0803A7CA|
	DCW      0x0000
