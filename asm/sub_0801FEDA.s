	CODE16
|sub_0801FEDA|
|unk_0801FEDA|
		MOV r2, #0x5d
		LSL r2, r2, #5
		ADD r0, r0, r2
		LDR r0, [r0]
		CMP r0, #0
		BLE      |loc_0801FED6|
		LDR r0, [r3]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		BEQ      |loc_0801FED6|
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #1
		STRB r0, [r4, #4]
		STR r6, [r5, #0x10]
		B        |loc_0801FED6|
|sub_0801FF02|
	DCW      0x4919
