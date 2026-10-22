	CODE16
|loc_0803B8CA|
|unk_0803B8CA|
		B        |loc_0803B91E|
		LDR r0, [sp, #0x34]
		LDR r1, [sp, #0x14]
		ADD r0, r0, r1
		STR r0, [sp, #0x34]
		LDR r0, [sp, #0x38]
		LDR r1, [sp, #0x18]
		ADD r0, r0, r1
		STR r0, [sp, #0x38]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x34
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BNE      |loc_0803B91E|
		LDR r0, [sp, #0x34]
		LDR r1, [sp, #0x1c]
		STR r6, [sp, #0x10]
		SUB r0, r0, r1
		STR r0, [sp, #0x34]
		LDR r0, [sp, #0x38]
		LDR r1, [sp, #0x20]
		ADD r3, sp, #0x34
		SUB r0, r0, r1
		STR r0, [sp, #0x38]
		ADD r1, sp, #0x54
		LDMIA r1!, {r0, r1}
		STR r0, [sp, #8]
		STR r1, [sp, #0xc]
		ADD r1, sp, #0x14
		LDMIA r1!, {r0, r1}
		STR r0, [sp]
		STR r1, [sp, #4]
		ADD r1, r4, #0
		ADD r0, r7, #0
		LDMIA r3!, {r2, r3}
		BL       |sub_0803B4FC|
		B        |inc_0x351c0_0x3d4d0| + 0x6660
