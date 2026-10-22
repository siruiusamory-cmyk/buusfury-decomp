	CODE16
|sub_0801856C|
|unk_0801856C|
		LDR r0, [pc, #0x224]
		ADD r1, r5, #0
		STR r0, [r4]
		LDR r0, [pc, #0x218]
		STRH r5, [r4, #0xe]
		LDR r0, [r0]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08018594|
		LDR r0, [pc, #0x208]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |sub_08011732|
		LDR r0, [pc, #0x200]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |loc_0801124C|
|loc_08018594|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x200]
		STR r0, [r4]
		MOV r0, #0
		STR r0, [r4, #0x10]
		LDMIA r6!, {r1, r2}
		STR r1, [r4, #0x14]
		STR r2, [r4, #0x18]
		LDRB r2, [r7, #1]
		SUB r6, #8
		ADD r0, r4, #0
		LDRB r1, [r7]
		BL       |inc_0x153f2_0x1a3f2| + 0x30ce
		LDR r0, [r6, #4]
		STR r0, [r4, #4]
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0x3178
