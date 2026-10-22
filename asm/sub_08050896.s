	CODE16
|sub_08050896|
|unk_08050896|
		STR r5, [sp, #0x14]
		STR r6, [sp, #0x18]
		STR r7, [sp, #0x1c]
		ADD r2, sp, #0x50
		LDMIA r2!, {r0, r1, r2}
		STR r0, [sp, #8]
		STR r2, [sp, #0x10]
		ADD r2, sp, #0x48
		STR r1, [sp, #0xc]
		LDMIA r2!, {r1, r2}
		STR r1, [sp]
		ADD r3, sp, #0x28
		STR r2, [sp, #4]
		LDMIA r3!, {r1, r2, r3}
		ADD r0, r4, #0
		BL       |loc_080060A8|
		LDR r0, [pc, #4]
		STR r0, [r4]
		ADD r0, r4, #0
		B        |inc_0x049120_0x055620| + 0x7772
