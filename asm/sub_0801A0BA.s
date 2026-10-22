	CODE16
|sub_0801A0BA|
|unk_0801A0BA|
		LDRB r1, [r0, #0x15]
		LSL r1, r1, #1
		ADD r1, r1, r0
		ADD r1, #0x2e
		LDRB r1, [r1]
		LDR r2, [pc, #0x248]
		ADD r2, #6
		LDRB r1, [r2, r1]
		BL       |inc_0x0158_0x143f2| + 0x13360
		B        |inc_0x153f2_0x1a3f2| + 0x4cc6
