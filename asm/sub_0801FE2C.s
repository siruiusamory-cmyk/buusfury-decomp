	CODE16
|sub_0801FE2C|
|unk_0801FE2C|
		MOV r0, #0xbf
		LSL r0, r0, #2
		DCD     0xFBC2F01D
		ADD r4, r0, #0
		BEQ      |loc_0801FE50|
		MOV r3, #1
		MOV r2, #0xd
		MOV r1, #0x5e
		ADD r0, r4, #0
		BL       |loc_08005460|
		LDR r0, [pc, #0x110]
		STR r0, [r4]
		MOV r0, #0xb
		LSL r0, r0, #6
		ADD r0, r4, r0
		STR r6, [r0, #0x38]
|loc_0801FE50|
		ADD r0, r4, #0
		DCW     0xE000
|loc_0801FE54|
|unk_0801FE54|
		B        |loc_0801FE68|
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE7E5
