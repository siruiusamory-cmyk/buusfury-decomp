	CODE16
|sub_0800A606|
|unk_0800A606|
		ADD r0, r4, #0
		LDR r1, [r5, #4]
		BL       |inc_0x0158_0x143f2| + 0xa120
		LDR r0, [pc, #0x184]
		STR r0, [r4]
		LDRH r0, [r5, #8]
		LDRH r1, [r5, #0xa]
		LDRH r2, [r5, #0xc]
		LDRH r3, [r5, #0xe]
		ADD r4, #0x48
		STMIA r4!, {r0, r1, r2, r3}
		SUB r4, #0x58
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xa4ac
