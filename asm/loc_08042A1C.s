	CODE16
|loc_08042A1C|
		B        |inc_0x042118_0x049114| + 0x7e8
		LDR r5, [pc, #0x190]
		STRH r6, [r5, #0x14]
		STRH r4, [r5, #0x16]
		LDRB r0, [r5, #0xe]
		CMP r0, #0
		BEQ      |loc_08042A30|
		MOV r0, #0
		STRB r0, [r5, #5]
		STRB r0, [r5, #4]
|loc_08042A30|
		MOV r1, #2
		MOV r0, #0xf0
		BL       |loc_0804333c|
		BL       |sub_08043368|
