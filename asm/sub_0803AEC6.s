	CODE16
|sub_0803AEC6|
|unk_0803AEC6|
		LDR r0, [pc, #0x2f8]
		ADD r6, r4, #0
		STR r0, [r4]
		LDMIA r5!, {r1, r2}
		ADD r4, #0x14
		STMIA r4!, {r1, r2, r7}
		MOV r2, #0
		MOV r1, #2
		STR r1, [sp]
		STR r2, [sp, #4]
		SUB r4, #0x20
		SUB r5, #8
		ADD r6, #0x10
		ADD r2, r5, #0
		MOV r1, #0
		MOV r3, #1
		MOV r0, #0
		BL       |inc_0x351c0_0x3d4d0| + 0x568a
		ADD r2, r0, #0
		LDR r5, [pc, #0x2d4]
		STR r0, [r4, #0xc]
		LDRB r1, [r2, #4]
		LDR r0, [r5, #8]
		BL       |loc_0800927E|
		MOV r2, #1
		MOV r1, #0
		LDR r0, [r5, #4]
		BL       |loc_080096C4|
		MOV r2, #1
		MOV r1, #0
		LDR r0, [r5, #4]
		BL       |loc_080096EA|
		MOV r2, #2
		MOV r1, #1
		LDR r0, [r5, #4]
		BL       |loc_080096EA|
		MOV r2, #2
		MOV r1, #2
		LDR r0, [r5, #4]
		BL       |loc_080096EA|
		MOV r2, #2
		MOV r1, #3
		LDR r0, [r5, #4]
		BL       |loc_080096EA|
		MOV r2, #2
		MOV r1, #4
		LDR r0, [r5, #4]
		BL       |loc_080096EA|
		MOV r2, #0x32
		MOV r1, #0x32
		LDR r0, [r5, #4]
		BL       |loc_08009728|
		MOV r1, #0
		LDR r0, [r5, #4]
		BL       |loc_080096AC|
		MOV r0, #0xff
		ADD r0, #1
		STR r0, [r6]
		LDR r1, [pc, #0x278]
		MOV r0, #0
		STRB r0, [r1]
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x5d02
