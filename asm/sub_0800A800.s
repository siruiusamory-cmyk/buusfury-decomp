	CODE16
|sub_0800A800|
|unk_0800A800|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xa120
		LDR r0, [pc, #0x74]
		STR r0, [r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xa6a6
