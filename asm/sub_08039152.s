	CODE16
|sub_08039152|
|unk_08039152|
		ADD r3, sp, #0
		LDMIA r5!, {r0, r1}
		STRH r0, [r3]
		STRH r1, [r3, #2]
		ADD r1, r7, #0
		ADD r0, r4, #0
		MOV r3, sp
		LDR r2, [pc, #0xa4]
		BL       |inc_0x0158_0x143f2| + 0xe560
		LDR r0, [pc, #0xa4]
		STR r0, [r4]
		MOV r0, #0x45
		LSL r0, r0, #3
		ADD r0, r4, r0
		MOV r1, #0
		STR r1, [r0, #4]
		STR r1, [r0, #0x30]
		STR r4, [r0]
		LDR r1, [r6, #8]
		BL       |loc_0800AA9C|
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x3f90
