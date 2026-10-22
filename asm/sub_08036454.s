	CODE16
|sub_08036454|
|unk_08036454|
		LDR r0, [pc, #0x2b0]
		MOV r6, #0x3d
		LSL r6, r6, #6
		LDR r5, [pc, #0x2b0]
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		LDR r0, [r5, #4]
		ADD r1, r6, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0803647C|
		ADD r1, r6, #0
		LDR r0, [r5, #4]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5, #4]
		BL       |loc_0801124C|
|loc_0803647C|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LDR r1, [pc, #0x28c]
		STRH r0, [r4, #0xc]
		STR r1, [r4]
		MOV r1, #0
		STR r1, [r4, #0x14]
		MOV r1, #0x11
		STRB r1, [r4, #8]
		LDR r1, [r5, #8]
		LSL r0, r0, #5
		LDR r2, [r1]
		SUB r2, r2, r7
		SUB r2, #1
		LSL r2, r2, #2
		ADD r1, r2, r1
		LDR r1, [r1, #4]
		MOV r2, #0x40
		STR r1, [r4, #0x10]
		LDR r1, [pc, #0x270]
		ADD r0, r0, r1
		LDR r1, [pc, #0x264]
		ADD r1, #0x14
		BL       |Thunk_VramCopy|
		MOV r0, #0
		MVN r1, r0
|loc_080364B2|
		LSL r2, r0, #2
		ADD r2, r2, r4
		ADD r0, #1
		CMP r0, #0x20
		STR r1, [r2, #0x18]
		BLT      |loc_080364B2|
		MOV r0, #0x98
		STR r1, [r0, r4]
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x1292
