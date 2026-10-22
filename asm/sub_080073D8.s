	CODE16
|sub_080073D8|
|unk_080073D8|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x9994
		LDR r0, [pc, #0x74]
		STR r0, [r4]
		LDR r0, [r5, #0x10]
		STR r0, [r4, #0x14]
		MOV r0, #0
		STRH r0, [r4, #0x10]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x727e
