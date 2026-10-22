	CODE16
|sub_08027306|
|unk_08027306|
		LDR r0, [r5, #4]
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		LDR r2, [pc, #0x6c]
		BL       |loc_0800EB60|
		LDR r0, [pc, #0x6c]
		MOV r1, #0xff
		STR r0, [r4]
		MOV r0, #0
		ADD r1, #0x95
		STR r0, [r1, r4]
		ADD r0, r4, #0
		BL       |loc_080272AC|
		ADD r0, r4, #0
		DCW     0xE7EB
