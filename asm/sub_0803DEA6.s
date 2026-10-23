	CODE16
|sub_0803DEA6|
|unk_0803DEA6|
		CMP r4, #0x20
		BNE      |loc_0803DEB0|
		ADD r6, r1, #0
		LDR r7, [r3, #8]
		B        |loc_0803DEC8|
|loc_0803DEB0|
		CMP r4, #0xa
		BEQ      |inc_0x03d784_0x041118| + 0x71e
		CMP r4, #0xb
		BNE      |loc_0803DEBE|
		MOV r4, #1
		STR r4, [r3, #0xc]
		B        |inc_0x03d784_0x041118| + 0x71e
|loc_0803DEBE|
		CMP r4, #8
		BNE      |loc_0803DEC8|
		ADD r1, #4
		STR r1, [r3, #4]
		B        |inc_0x03d784_0x041118| + 0x712
|loc_0803DEC8|
		LDR r5, [r0, #0xc]
		CMP r4, #0xff
		BLO      |loc_0803DED4|
		LDR r4, [r5, #4]
		ADD r4, #1
		B        |loc_0803DEE0|
|loc_0803DED4|
		LDR r5, [r5]
		LSL r4, r4, #1
		LDRH r4, [r5, r4]
		LSL r4, r4, #1
		LDRH r4, [r5, r4]
		ADD r4, #1
|loc_0803DEE0|
		LDR r5, [r3, #8]
		ADD r4, r5, r4
		CMP r4, r2
		BLE      |loc_0803DEF2|
		CMP r6, #0
		BEQ      |inc_0x03d784_0x041118| + 0x71e
		ADD r3, #4
		STMIA r3!, {r6, r7}
		B        |inc_0x03d784_0x041118| + 0x71e
|loc_0803DEF2|
		ADD r1, #2
		STR r1, [r3, #4]
		STR r4, [r3, #8]
		B        |inc_0x03d784_0x041118| + 0x712
|sub_0803DEFA|
	DCW      0xb40f
