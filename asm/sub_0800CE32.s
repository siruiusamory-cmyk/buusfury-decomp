	CODE16
|sub_0800CE32|
|unk_0800CE32|
		MOV r2, #0
		ADD r0, r4, #0
		LDR r1, [r5, #0x28]
		BL       |inc_0x0158_0x143f2| + 0xc9bc
		LDR r0, [pc, #0xac]
		STR r0, [r4]
		STR r5, [r4, #0x5c]
		LDR r0, [r5, #0x2c]
		LDR r1, [r0, #4]
		LDR r0, [pc, #0xa0]
		LDR r0, [r0]
		BL       |loc_0801124C|
		STRH r0, [r4, #0x16]
		ADD r0, r4, #0
		BL       |sub_0800CD00|
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xccd8
