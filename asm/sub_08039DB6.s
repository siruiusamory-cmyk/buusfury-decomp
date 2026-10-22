	CODE16
|sub_08039DB6|
|unk_08039DB6|
		LDR r0, [pc, #0x158]
		MOV r3, #4
		STR r0, [r4]
		LDRH r2, [r5, #4]
		MOV r0, #0xff
		ADD r0, #0xa1
		STRH r2, [r4, #4]
		LDRH r2, [r5, #6]
		STRH r2, [r4, #6]
		LDRH r1, [r5, #8]
		STRH r1, [r4, #8]
		LDR r0, [r0, r6]
		LDRSH r1, [r5, r3]
		ASR r0, r0, #8
		MOV r3, #6
		SUB r0, r1, r0
		STR r0, [sp, #0x10]
		MOV r0, #0xff
		ADD r0, #0xa5
		LDR r0, [r0, r6]
		LDRSH r1, [r5, r3]
		ASR r0, r0, #8
		MOV r3, #8
		SUB r0, r1, r0
		STR r0, [sp, #0x14]
		MOV r0, #0xff
		ADD r0, #0xa9
		LDR r0, [r0, r6]
		LDRSH r1, [r5, r3]
		ASR r0, r0, #0xa
		LDR r2, [sp, #0x10]
		SUB r0, r1, r0
		STR r0, [sp, #0x18]
		CMP r2, #0
		BGE      |loc_08039DFE|
		NEG r2, r2
|loc_08039DFE|
		LDR r1, [sp, #0x14]
		CMP r1, #0
		BGE      |loc_08039E06|
		NEG r1, r1
|loc_08039E06|
		LDR r0, [sp, #0x18]
		CMP r0, #0
		BGE      |loc_08039E0E|
		NEG r0, r0
|loc_08039E0E|
		STR r1, [sp, #8]
		STR r2, [sp, #4]
		STR r0, [sp, #0xc]
		ADD r3, sp, #4
		ADD r7, sp, #8
		LDMIA r7!, {r2, r7}
		ADD r1, r3, #0
		ADD r1, #8
		ADD r0, r3, #4
		CMP r2, r7
		BGT      |loc_08039E26|
		ADD r0, r1, #0
|loc_08039E26|
		LDR r1, [sp, #4]
		LDR r2, [r0]
		CMP r1, r2
		BLE      |loc_08039E30|
		ADD r0, r3, #0
|loc_08039E30|
		LDR r0, [r0]
		LSL r1, r0, #8
		LDRH r0, [r5, #0xa]
		BL       |sub_08046E58|
		ADD r5, r0, #0
		CMP r0, #0
		STR r0, [r4, #0x18]
		BGT      |loc_08039E4A|
		MOV r0, #1
		STR r0, [r4, #0x18]
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x4bf2
|loc_08039E4A|
		LDR r0, [sp, #0x10]
		LSL r1, r0, #8
		ADD r0, r5, #0
		BL       |sub_08046E58|
		STR r0, [r4, #0xc]
		LDR r0, [sp, #0x14]
		LSL r1, r0, #8
		ADD r0, r5, #0
		BL       |sub_08046E58|
		STR r0, [r4, #0x10]
		LDR r0, [sp, #0x18]
		LSL r1, r0, #0xa
		ADD r0, r5, #0
		BL       |sub_08046E58|
		ADD r1, r6, #0
		ADD r1, #0xff
		STR r0, [r4, #0x14]
		ADD r1, #0xad
		STR r1, [sp]
		LDR r0, [sp, #0x14]
		BL       |sub_08054ADC|
		ADD r5, r0, #0
		LDR r0, [sp, #0x10]
		BL       |sub_08054ADC|
		BL       |inc_0x049120_0x055620| + 0xb894
		ADD r6, r0, #0
		ADD r7, r1, #0
		ADD r0, r5, #0
		BL       |inc_0x049120_0x055620| + 0xb894
		ADD r3, r7, #0
		ADD r2, r6, #0
		BL       |sub_080491A0|
		BL       |sub_080532E8|
		LDR r1, [pc, #0x74]
		BL       |sub_08054B3C|
		MOV r1, #0x89
		LSL r1, r1, #0x17
		BL       |sub_08054B3C|
		BL       |sub_08054A64|
		LDR r1, [sp]
		STR r0, [r1]
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x4bf2
