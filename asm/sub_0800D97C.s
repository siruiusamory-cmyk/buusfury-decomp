	CODE16
|sub_0800D97C|
|unk_0800D97C|
		LDR r0, [r6, #4]
		LDR r5, [r6]
		LDR r7, [pc, #0x338]
		MUL r5, r0
		LDR r0, [pc, #0x330]
		ADD r1, r5, #0
		STR r0, [r4]
		STRH r5, [r4, #0xe]
		LDR r0, [r7]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0800D9A6|
		ADD r1, r5, #0
		LDR r0, [r7]
		BL       |sub_08011732|
		ADD r1, r5, #0
		LDR r0, [r7]
		BL       |loc_0801124C|
|loc_0800D9A6|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x314]
		STR r0, [r4]
		STR r6, [r4, #0x14]
		LDR r0, [r6, #8]
		STR r0, [r4, #0x10]
		LDR r1, [sp, #0x10]
		ADD r0, r4, #0
		LDR r2, [r1]
		LDR r1, [r1, #4]
		ADD r0, #0x18
		STR r1, [r4, #0x1c]
		STR r2, [r4, #0x18]
		ADD r2, r0, #0
		LDR r0, [r0, #4]
		LDR r3, [r4, #0x18]
		LDR r5, [r6]
		LDR r1, [r6, #4]
		ADD r3, r3, r5
		ADD r0, r0, r1
		STR r0, [sp, #4]
		LDR r1, [sp, #4]
		STR r3, [sp]
		ADD r2, #8
		STR r1, [r2, #4]
		STR r3, [r2]
		LDR r0, [r4, #0x24]
		STR r0, [r4, #4]
		ADD r0, r4, #0
		BL       |loc_0800D918|
		LDR r1, [pc, #0x2dc]
		LDR r0, [r1]
		ADD r0, #1
		STR r0, [r1]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xd820
