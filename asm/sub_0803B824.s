	CODE16
|sub_0803B824|
|unk_0803B824|
		LDR r0, [sp, #0x2c]
		LDR r1, [sp, #0x1c]
		ADD r5, r5, r0
		LDR r0, [sp, #0x34]
		ADD r0, r0, r1
		STR r0, [sp, #0x34]
		LDR r0, [sp, #0x38]
		LDR r1, [sp, #0x20]
		ADD r0, r0, r1
		STR r0, [sp, #0x38]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x34
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BNE      |loc_0803B8CA|
		LDR r0, [sp, #0x34]
		LDR r1, [sp, #0x1c]
		SUB r0, r0, r1
		STR r0, [sp, #0x34]
		LDR r0, [sp, #0x38]
		LDR r1, [sp, #0x20]
		SUB r0, r0, r1
		STR r0, [sp, #0x38]
		LDR r0, [sp, #0x24]
		LDR r1, [sp, #0x1c]
		CMP r0, r1
		BNE      |loc_0803B86C|
		LDR r0, [sp, #0x20]
		MOV r1, #0
		STR r1, [sp, #0x14]
		STR r0, [sp, #0x18]
		B        |loc_0803B874|
|loc_0803B86C|
		LDR r0, [sp, #0x1c]
		MOV r1, #0
		STR r1, [sp, #0x18]
		STR r0, [sp, #0x14]
|loc_0803B874|
		LDR r0, [sp, #0x34]
		LDR r1, [sp, #0x24]
		ADD r0, r0, r1
		STR r0, [sp, #0x34]
		LDR r0, [sp, #0x38]
		LDR r1, [sp, #0x28]
		ADD r0, r0, r1
		STR r0, [sp, #0x38]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x34
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BNE      |inc_0x351c0_0x3d4d0| + 0x670c
		LDR r0, [sp, #0x34]
		LDR r1, [sp, #0x24]
		STR r6, [sp, #0x10]
		SUB r0, r0, r1
		STR r0, [sp, #0x34]
		LDR r0, [sp, #0x38]
		LDR r1, [sp, #0x28]
		SUB r0, r0, r1
		STR r0, [sp, #0x38]
		ADD r1, sp, #0x54
		LDMIA r1!, {r0, r1}
		STR r0, [sp, #8]
		B        |inc_0x351c0_0x3d4d0| + 0x66f2
|loc_0803B8B0|
|unk_0803B8B0|
		B        |loc_0803B926|
		STR r1, [sp, #0xc]
		ADD r1, sp, #0x24
		LDMIA r1!, {r0, r1}
		STR r0, [sp]
		STR r1, [sp, #4]
		ADD r3, sp, #0x34
		ADD r1, r4, #0
		ADD r0, r7, #0
		LDMIA r3!, {r2, r3}
		BL       |sub_0803B4FC|
		B        |inc_0x351c0_0x3d4d0| + 0x6660
