	CODE16
|sub_08024A44|
|unk_08024A44|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x9994
		LDR r0, [pc, #0x28]
		STR r0, [r4]
		ADD r0, r4, #0
		DCW     0xE7F6
