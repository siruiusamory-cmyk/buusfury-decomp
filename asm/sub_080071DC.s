	CODE16
|sub_080071DC|
|unk_080071DC|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x9994
		LDR r0, [pc, #0x114]
		LDR r1, [pc, #0x118]
		STR r0, [r4]
		STR r5, [r4, #0x14]
		LDRB r0, [r5, #0x10]
		STRB r0, [r4, #0x10]
		LDRB r0, [r1, r0]
		STRB r0, [r4, #0x11]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x7082
