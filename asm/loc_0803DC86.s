	CODE16
|loc_0803DC86|
		ADD r5, #2
		LDRH r0, [r5]
		CMP r0, #0
		BEQ      |loc_0803DC90|
		B        |inc_0x03d784_0x041118| + 0x408
|loc_0803DC90|
		MOV r0, #0
		STRH r0, [r4]
		B        |inc_0x03d784_0x041118| + 0x46a
|sub_0803DC96|
	DCW      0xb40f
