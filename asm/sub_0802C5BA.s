	CODE16
|sub_0802C5BA|
|unk_0802C5BA|
		MOV r1, #0x11
		LDR r0, [r4, #4]
		BL       |loc_0800EEB0|
		CMP r0, #0
		BNE      |loc_0802C62C|
		LDR r0, [pc, #0xcc]
		MOV r2, #0xf0
		LDR r1, [r0]
		LDRH r1, [r1, #4]
		AND r1, r2
		BEQ      |loc_0802C5DE|
		LDR r1, [pc, #0xb0]
		MOV r3, #1
		LDR r1, [r1]
		LDRB r2, [r1, #0x11]
		EOR r2, r3
		STRB r2, [r1, #0x11]
|loc_0802C5DE|
		MOV r3, #0x5a
		MOV r2, #0x14
		MOV r1, #0xf0
		LDR r0, [r0]
		BL       |inc_0x03d784_0x041118| + 0x2b00
		CMP r0, #0
		BEQ      |loc_0802C62C|
		LDR r0, [r4, #8]
		ADD r0, #1
		STR r0, [r4, #8]
		CMP r0, #5
		BNE      |loc_0802C62C|
		LDR r1, [pc, #0x88]
		LDR r2, [r6]
		LDR r0, [r1]
		ADD r0, #0xff
		ADD r0, #0xa1
		STMIA r0!, {r2}
		LDR r2, [r5]
		STR r2, [r0]
		LDR r0, [r1]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		LDR r1, [r7]
		ADD r0, r7, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #9
		BL       |loc_08046AA4|
		MOV r3, #1
		STRB r3, [r4, #0x14]
		MOV r0, #0x3c
		STRB r0, [r4, #0x15]
|loc_0802C62C|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xa6c
