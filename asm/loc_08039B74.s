	CODE16
|loc_08039B74|
|unk_08039B74|
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		LDR r0, [r0, #4]
		MOV r7, #1
		ADD r4, r1, #0
		CMP r0, #0
		BNE      |loc_08039BA4|
		MOV r0, #0xc
		DCD     0xFD18F003
		CMP r0, #0
		BEQ      |loc_08039B90|
		LDR r1, [pc, #0x48]
		STR r1, [r0]
|loc_08039B90|
		ADD r6, r0, #0
		MOV r1, #0x13
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |loc_0800ED18|
		STR r7, [r5, #4]
|loc_08039BA4|
		LDR r0, [r4, #0x58]
		ADD r0, #0x4c
		LDR r0, [r0, #0x54]
		LDR r1, [r4, #0x50]
		CMP r0, r1
		BNE      |sub_08039BB4|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x49f6
