	CODE16
|sub_080178E4|
|unk_080178E4|
		LDR r0, [pc, #0xe4]
		MOV r6, #0xff
		ADD r6, #1
		LDR r5, [pc, #0xe4]
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		LDR r0, [r5]
		ADD r1, r6, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0801790C|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |loc_0801124C|
|loc_0801790C|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0xc4]
		MOV r5, #0
		STR r0, [r4]
		STR r5, [r4, #0x10]
		MOV r2, #0x10
		MOV r1, #0x10
		STR r7, [r4, #0x14]
		MOV r0, sp
		MOV r6, sp
		BL       |loc_0803F540|
		LDR r0, [pc, #0xb0]
		LDR r1, [sp, #0x24]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LDRH r0, [r4, #0xc]
		LDR r1, [pc, #0xac]
		LSL r0, r0, #5
		ADD r1, r0, r1
		ADD r0, r6, #0
		BL       |inc_0x03d784_0x041118| + 0x2234
		MOV r0, #1
		STR r0, [r4, #4]
		MOV r1, #0
		ADD r0, r6, #0
		STRB r5, [r4, #8]
		BL       |sub_0803F58C|
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0x24ee
