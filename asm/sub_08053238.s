	CODE16
|sub_08053238|
|unk_08053238|
		LDR r1, [r4]
		LDR r0, [r5]
		STR r1, [r5]
		STR r0, [r4]
		SUB r1, r4, #4
		ADD r0, r5, #0
		BL       |sub_080531A4|
		ADD r1, r7, #0
		ADD r0, r4, #4
		B        |inc_0x049120_0x055620| + 0xa086
