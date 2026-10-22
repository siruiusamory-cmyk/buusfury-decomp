	CODE16
|sub_08011FF2|
|unk_08011FF2|
		ADD r0, r4, #0
		ADD r0, #8
		ADD r1, r5, #4
		ADD r5, r0, #0
		BL       |inc_0x049120_0x055620|
		ADD r3, r6, #0
		ADD r2, r7, #0
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_08011F5A|
		LDR r0, [pc, #0x194]
		STR r0, [r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x11e98
