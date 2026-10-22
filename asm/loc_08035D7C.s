	CODE16
|loc_08035D7C|
|unk_08035D7C|
		LDR r0, [r6]
		BL       |loc_080116FC|
		CMP r0, r7
		BLT      |loc_08035D92|
		MOV r6, #1
		LSL r6, r6, #0xc
		ADD r0, r6, #0
		BL       |inc_0x03d784_0x041118| + 0x2348
		B        |sub_08035D94|
|loc_08035D92|
		B        |inc_0x351c0_0x3d4d0| + 0xc04
