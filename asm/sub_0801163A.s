	CODE16
|sub_0801163A|
|unk_0801163A|
		ADD r1, r7, #0
		ADD r0, r6, #0
		BL       |loc_08052EE0|
		CMP r0, #0
		BEQ      |loc_080116A2|
		LDR r0, [sp, #0x10]
		LDR r1, [r7]
		STR r1, [sp, #0x10]
		STR r0, [r7]
		B        |loc_080116A2|
