	CODE16
|sub_0801248E|
|unk_0801248E|
		LDR r0, [sp, #8]
		STMIA r4!, {r0, r6}
		SUB r4, #8
		LDMIA r7!, {r0, r1}
		STR r0, [r4, #0xc]
		MOV r0, #0
		STR r1, [r4, #0x10]
		STR r0, [r4, #0x28]
		CMP r5, #0
		BNE      |loc_080124A6|
		ADD r5, r4, #0
		ADD r5, #0x18
|loc_080124A6|
		LDR r2, [pc, #0x12c]
		STR r5, [r4, #0x14]
		LDR r1, [r2, #4]
		CMP r1, #0
		BNE      |loc_080124B2|
		STR r0, [r2]
|loc_080124B2|
		ADD r1, #1
		STR r1, [r2, #4]
		LDRH r1, [r6]
		MOV r2, #0
		STRH r1, [r4, #8]
		STR r0, [r4, #0x18]
		STR r0, [r4, #0x1c]
		STR r0, [r4, #0x20]
		STR r0, [r4, #0x24]
		LDR r0, [pc, #0x110]
		MOV r1, #0xf
		LDR r0, [r0]
		BL       |loc_08011C0C|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x12332
