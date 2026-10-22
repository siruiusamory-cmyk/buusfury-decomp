	CODE16
|sub_0801FC9E|
|unk_0801FC9E|
		LDR r0, [r4, #0x20]
		LDR r1, [r4, #0x24]
		ADD r6, r5, #0
		ADD r6, #0xff
		ADD r0, r0, r1
		LSL r0, r0, #3
		ADD r6, #0x2d
		ADD r0, r0, r6
		ADD r0, #4
		LDR r1, [r0]
		CMP r1, #1
		BNE      |loc_0801FCBA|
		MOV r0, #1
		B        |loc_0801FCF6|
|loc_0801FCBA|
		STR r0, [sp]
		MOV r0, #0xff
		ADD r0, #0x39
		DCD     0xFC7AF01D
		CMP r0, #0
		BEQ      |loc_0801FCF2|
		LDR r1, [pc, #0x274]
		STMIA r0!, {r1, r7}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r7, [r1, #0xc]
		STR r7, [r1, #8]
		STR r7, [r1, #0x10]
		LDR r1, [pc, #0x268]
		STR r1, [r0]
		LDR r3, [sp]
		ADD r1, r0, #0
		LDRH r2, [r3]
		ADD r1, #0xff
		ADD r1, #0x15
		STRH r2, [r1]
		LDRH r2, [r3, #2]
		STRH r2, [r1, #2]
		LDRH r2, [r3, #4]
		STRH r2, [r1, #4]
|loc_0801FCF2|
		BL       |inc_0x03d784_0x041118| + 0x11c
|loc_0801FCF6|
		ADD r2, r0, #0
		CMP r0, #0
		BLE      |loc_0801FD3A|
		STR r2, [sp]
		LDR r0, [r4, #0x20]
		LDR r1, [r4, #0x24]
		ADD r2, r6, #0
		ADD r3, r0, r1
		MOV r0, #0x5d
		LSL r0, r0, #5
		ADD r1, r5, r0
		ADD r0, r5, #0
		BL       |sub_0801FC3E|
		LDR r2, [r6]
		LDR r0, [r4, #0x20]
		LDR r1, [r4, #0x24]
		ADD r3, r0, r1
		CMP r2, r3
		BGT      |loc_0801FD3A|
		CMP r1, #0
		BEQ      |loc_0801FD28|
		SUB r1, #1
		STR r1, [r4, #0x24]
		B        |loc_0801FD3A|
|loc_0801FD28|
		CMP r0, #0
		BEQ      |loc_0801FD32|
		SUB r0, #1
		STR r0, [r4, #0x20]
		B        |loc_0801FD3A|
|loc_0801FD32|
		MOV r0, #1
		ADD r5, #0xff
		ADD r5, #0x11
		STRB r0, [r5, #4]
|loc_0801FD3A|
		STR r7, [r4, #0x10]
|loc_0801FD3C|
|unk_0801FD3C|
		DCW     0xE00E
|loc_0801FD3E|
|unk_0801FD3E|
		LDR r0, [r4, #0x24]
		CMP r0, #0
		BEQ      |loc_0801FD4A|
		SUB r0, #1
		STR r0, [r4, #0x24]
		B        |loc_0801FD50|
|loc_0801FD4A|
		LDR r0, [r4, #0x20]
		SUB r0, #1
		STR r0, [r4, #0x20]
|loc_0801FD50|
		STR r7, [r4, #0x10]
		DCW     0xE003
