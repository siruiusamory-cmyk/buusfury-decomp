	CODE16
|sub_080423D4|
|unk_080423D4|
		MOV r2, #0
		STRB r2, [r6, #0xa]
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		BL       |inc_0x042118_0x049114| + 0x1264
		MOV r5, #1
		MOV r1, #1
		MOV r0, #0x33
		B        |loc_080423F6|
