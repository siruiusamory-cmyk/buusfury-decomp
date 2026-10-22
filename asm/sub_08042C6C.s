	CODE16
|sub_08042C6C|
|unk_08042C6C|
		LDRB r0, [r5, #4]
		MOV r1, #0xc
		CMP r0, #0
		BEQ      |loc_08042C78|
		CMP r0, #9
		BNE      |sub_08042C80|
|loc_08042C78|
		STRB r1, [r5, #4]
		MOV r0, #0xd
		STRB r0, [r5, #5]
		B        |inc_0x042118_0x049114| + 0xb6e
