	CODE16
|sub_080195C4|
|unk_080195C4|
		LDR r0, [pc, #0x1d0]
		MOV r6, #1
		LSL r6, r6, #9
		LDR r5, [pc, #0x1d0]
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		LDR r0, [r5]
		ADD r1, r6, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_080195EC|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |loc_0801124C|
|loc_080195EC|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x1b0]
		MOV r3, #0x35
		STR r0, [r4]
		LDR r0, [sp, #8]
		STR r0, [r4, #0x10]
		MOV r0, #0xff
		STRB r0, [r4, #0x14]
		MOV r0, #0x10
		STRB r0, [r4, #8]
		MOV r0, #0
		STR r0, [r4, #4]
		MOV r0, #0xf8
		STRB r0, [r4, #0x18]
		MOV r0, #1
		STRB r0, [r4, #0x17]
		LDR r0, [sp, #0xc]
		MUL r0, r3
		BL       |sub_08053034|
		ADD r5, r1, #0
		MOV r0, #0x35
		MUL r0, r7
		STRB r1, [r4, #0x15]
		BL       |sub_08053034|
		SUB r0, r1, r5
		STRB r0, [r4, #0x16]
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0x41ce
