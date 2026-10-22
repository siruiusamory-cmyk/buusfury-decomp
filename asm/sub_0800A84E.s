	CODE16
|sub_0800A84E|
|unk_0800A84E|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xa120
		LDR r0, [pc, #0x2c]
		STR r0, [r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xa6f4
