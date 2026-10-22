	CODE16
|sub_0801E8DA|
|unk_0801E8DA|
		MOV r7, #0
		ADD r3, r7, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r5, #0
		DCW     0xF01E
		DCW     0xFE67
		CMP r0, #0
		BEQ      |loc_0801E90E|
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STMIA r0!, {r6, r7}
		STR r7, [r1, #0xc]
		STR r7, [r1, #8]
		SUB r0, #8
		ADD r2, r1, #0
		ADD r2, #0x10
		STR r7, [r1, #0x10]
		LDR r3, [pc, #0xf8]
		STRB r7, [r2, #4]
		STR r3, [r0]
		STR r7, [r1, #0x18]
		MOV r1, #2
		STRB r1, [r2, #0xc]
|loc_0801E90E|
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #2
		DCW     0xD11D
		LDR r3, [pc, #0xd0]
		SUB r3, #0x24
		LDR r0, [r3, #0xc]
		BL       |inc_0x03d784_0x041118| + 0x2a16
		MOV r0, #0xbf
		LSL r0, r0, #2
		DCD     0xFE48F01E
		ADD r5, r0, #0
		BEQ      |loc_0801E944|
		ADD r3, r4, #0
		MOV r2, #0xd
		MOV r1, #0x5e
		ADD r0, r5, #0
		BL       |loc_08005460|
		LDR r0, [pc, #0xc4]
		STR r0, [r5]
		MOV r0, #0xb
		LSL r0, r0, #6
		ADD r0, r5, r0
		STR r4, [r0, #0x38]
|loc_0801E944|
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xcc
		DCW     0xE000
|loc_0801E94C|
|unk_0801E94C|
		B        |loc_0801E96C|
		MOV r0, #1
		DCW     0xE7C2
		MOV r1, #0
		MOV r0, #0
		BL       |inc_0x049120_0x055620| + 0x71dc
		BL       |inc_0x03d784_0x041118| + 0x29dc
		B        |loc_0801E96C|
