	CODE16
|sub_08012350|
|unk_08012350|
		ADD r2, r7, #0
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x1215c
		ADD r1, r0, #0
		ADD r3, r6, #0
		ADD r0, r4, #0
		LDRB r2, [r5, #3]
		BL       |sub_08012012|
		LDR r0, [pc, #0x74]
		STR r0, [r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x121f6
