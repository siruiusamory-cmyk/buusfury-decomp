	CODE16
|sub_08019F5A|
|unk_08019F5A|
		ADD r1, r0, #0
		ADD r1, #0x1c
		MOV r3, #0
		LDRSH r1, [r1, r3]
		LDR r3, [pc, #0x7c]
		LDR r2, [pc, #0x7c]
		MUL r1, r3
		ADD r1, r1, r2
		ASR r1, r1, #0x10
		BL       |inc_0x0158_0x143f2| + 0x13360
		B        |inc_0x153f2_0x1a3f2| + 0x4b66
