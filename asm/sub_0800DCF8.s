	CODE16
|sub_0800DCF8|
|unk_0800DCF8|
		ADD r3, r6, #0
		ADD r2, r7, #0
		ADD r0, r4, #0
		LDR r1, [r5, #4]
		BL       |loc_0800D30E|
		LDR r0, [pc, #0x20]
		STR r0, [r4]
		MOV r0, #0x80
		STR r5, [r0, r4]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xdb9e
