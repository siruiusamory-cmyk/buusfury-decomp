	CODE16
|loc_0801FE5E|
|unk_0801FE5E|
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x72f4
		BL       |inc_0x03d784_0x041118| + 0x29dc
|loc_0801FE68|
		MOV r0, #0xff
		ADD r0, #0x15
		LDRB r0, [r0, r4]
		CMP r0, #0
		BEQ      |loc_0801FE82|
		CMP r0, #1
		BNE      |loc_0801FE8E|
		ADD r2, r5, #0
		MOV r1, #0
		ADD r0, r4, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x364a
		DCW     0xE7D3
|loc_0801FE82|
		ADD r2, r5, #0
		MOV r1, #0
		ADD r0, r4, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x3888
		DCW     0xE7CD
|loc_0801FE8E|
		MOV r0, #0
		DCW     0xE7CB
