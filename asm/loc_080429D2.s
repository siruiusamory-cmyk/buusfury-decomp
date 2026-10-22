	CODE16
|loc_080429D2|
		LDRB r0, [r5, #0xe]
		CMP r0, #0
		BNE      |loc_080429F6|
		MOV r1, #1
		MOV r0, #0x40
		B        |loc_080429F2|
		B        |inc_0x042118_0x049114| + 0x906
		BL       |inc_0x042118_0x049114| + 0x127a
		LDR r0, [pc, #0x1c4]
		LDR r0, [r0]
		LDRB r0, [r0]
		CMP r0, #0xff
		BEQ      |loc_080429F6|
		MOV r1, #0
		MOV r0, #0x50
|loc_080429F2|
		BL       |loc_0804333c|
|loc_080429F6|
		CMP r4, #0
		BEQ      |loc_08042A3C|
		CMP r6, #0x1c
		BNE      |inc_0x042118_0x049114| + 0x906
		LDR r5, [pc, #0x1b0]
		LDRB r0, [r5, #7]
		CMP r0, #4
		BNE      |inc_0x042118_0x049114| + 0x906
		LDR r0, [pc, #0x1a4]
		MOV r7, #1
		LDR r0, [r0]
		MOV r1, #0xf
		STRB r7, [r0]
		STRB r1, [r0, #2]
		MOV r0, #0xf
		BL       |inc_0x042118_0x049114| + 0x1264
		BL       |loc_0804389e|
