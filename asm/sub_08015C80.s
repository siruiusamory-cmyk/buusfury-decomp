	CODE16
|sub_08015C80|
|unk_08015C80|
		ADD r2, sp, #0x30
		LDMIA r2!, {r0, r1, r2}
		STR r0, [sp]
		STR r1, [sp, #4]
		ADD r3, sp, #0x10
		STR r2, [sp, #8]
		LDMIA r3!, {r1, r2, r3}
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x5e66
		LDR r0, [pc, #0x1f0]
		ADD r1, r6, #0
		STR r0, [r4]
		STR r5, [r4, #0x20]
		STR r6, [r4, #0x24]
		ADD r0, r5, #3
		STR r0, [r4, #0x30]
		ADD r1, #8
		STR r1, [r4, #0x34]
		LDR r0, [sp, #0x3c]
		LDR r1, [pc, #0x1e0]
		LSL r0, r0, #2
|loc_08015CAC|
|unk_08015CAC|
		LDR r1, [r1, r0]
		STR r1, [r4, #0x1c]
		LDR r0, [sp, #0x48]
		STR r0, [r4, #0x38]
		LDR r0, [pc, #0x1c8]
		STR r7, [r4, #0x3c]
		SUB r0, #8
		LDR r0, [r0, #4]
		BL       |sub_0803FFE8|
		LDR r1, [r4, #0x20]
		ADD r0, #6
		ADD r0, r1, r0
		STR r0, [r4, #0x28]
		LDR r0, [r4, #0x24]
		ADD r0, #0xa
		STR r0, [r4, #0x2c]
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0x88a
