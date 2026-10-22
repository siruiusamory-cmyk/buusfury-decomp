	CODE16
|loc_08021950|
		MOV r0, #0x98
		ADD r3, sp, #0xc0
		STRH r0, [r3, #0x28]
		MOV r0, #0xdc
		STRH r0, [r3, #0x2a]
		LDR r0, [r7, #0x20]
		LDRB r0, [r0]
		CMP r0, #1
		BNE      |loc_080219BE|
		ADD r0, sp, #0x80
		BL       |inc_0x049120_0x055620| + 0x7244
		ADD r0, sp, #0x18
		BL       |inc_0x049120_0x055620| + 0x7244
		MOV r2, #0x68
		MOV r1, #0
		ADD r0, sp, #0x80
		BL       |sub_0804912C|
		MOV r2, #0x68
		MOV r1, #0
		ADD r0, sp, #0x18
		BL       |sub_0804912C|
		ADD r0, sp, #0x80
		LDR r1, [r7, #0x24]
		BL       |loc_0801339C|
		ADD r0, sp, #0x18
		LDR r1, [r7, #0x28]
		BL       |loc_0801339C|
		LDR r0, [r7, #0x28]
		LDR r0, [r0, #0x14]
		BL       |inc_0x0158_0x143f2|
		STR r0, [sp, #0x14]
		LDR r0, [r7, #0x24]
		LDR r0, [r0, #0x14]
		BL       |inc_0x0158_0x143f2|
		ADD r2, sp, #0x18
		ADD r1, sp, #0x80
		STR r1, [sp, #8]
		STR r2, [sp, #0xc]
		ADD r2, r0, #0
		STR r6, [sp, #4]
		STR r5, [sp]
		LDR r3, [sp, #0x14]
		LDR r0, [r7, #0x2c]
		ADD r1, sp, #0xe8
		BL       |inc_0x0158_0x143f2| + 0x8d18
		B        |loc_08021A18|
|loc_080219BE|
		ADD r0, sp, #0x80
		BL       |inc_0x049120_0x055620| + 0x7244
		ADD r0, sp, #0x18
		BL       |inc_0x049120_0x055620| + 0x7244
		ADD r1, sp, #0x80
		LDR r0, [r7, #0x24]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x65be
		ADD r1, sp, #0x18
		LDR r0, [r7, #0x28]
		BL       |inc_0x1c3f2_0x2ab4c| + 0x65be
		ADD r3, sp, #0x20
		LDRB r0, [r3, #0xc]
		LDR r1, [pc, #0x1fc]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
		STR r0, [sp, #0x14]
		ADD r3, sp, #0x80
		LDRB r0, [r3, #0x14]
		LDR r1, [pc, #0x1e8]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
		ADD r2, sp, #0x18
		ADD r1, sp, #0x80
		STR r1, [sp, #8]
		STR r2, [sp, #0xc]
		ADD r2, r0, #0
		STR r6, [sp, #4]
		STR r5, [sp]
		LDR r3, [sp, #0x14]
		LDR r0, [r7, #0x2c]
		ADD r1, sp, #0xe8
		BL       |inc_0x0158_0x143f2| + 0x8d18
|loc_08021A18|
		LDR r7, [pc, #0x19c]
		LDR r0, [r7, #8]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x24]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |loc_08021A30|
		LDR r0, [r4, #4]
		B        |loc_08021A32|
|loc_08021A30|
		LDR r0, [r4, #8]
|loc_08021A32|
		LDR r7, [pc, #0x180]
		STR r0, [r7, #0x14]
		LDR r0, [pc, #0x180]
		LDR r0, [r0, #8]
		LDR r0, [r0]
		LDR r1, [r0]
		LDR r2, [r1, #0x24]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		CMP r0, #0
		BEQ      |sub_08021A4E|
		LDR r0, [r4, #8]
		DCW     0xE000
