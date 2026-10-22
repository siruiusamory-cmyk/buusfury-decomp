	CODE16
|sub_08017E80|
|unk_08017E80|
		LDR r1, [r5, #0x14]
		LDR r2, [r5, #0x18]
		LDR r3, [r5, #0x1c]
		LDR r6, [r5, #0x20]
		SUB r1, #4
		SUB r2, #4
		ADD r3, #4
		ADD r6, #4
		STR r6, [sp, #0xc]
		STR r3, [sp, #8]
		STR r2, [sp, #4]
		STR r1, [sp]
		BL       |loc_0800776C|
		ADD r6, r0, #0
		LDR r0, [pc, #0x3c0]
		ADD r3, sp, #8
		STR r0, [r4]
		LDR r0, [sp]
		LDR r1, [sp, #4]
		LDMIA r3!, {r2, r3}
		SUB r0, #0xf
		STRH r0, [r4, #4]
		SUB r1, #7
		STRH r1, [r4, #6]
		STRH r2, [r4, #8]
		LDR r0, [pc, #0x3ac]
		STRH r3, [r4, #0xa]
		STR r0, [r4]
		STR r5, [r4, #0x10]
		STR r6, [r4, #0xc]
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0x2a8a
