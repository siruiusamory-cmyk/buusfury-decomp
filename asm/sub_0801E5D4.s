	CODE16
|sub_0801E5D4|
|unk_0801E5D4|
		BL       |inc_0x03d784_0x041118| + 0x2954
		ADD r1, r4, #0
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #0xbf
		LSL r0, r0, #2
		DCD     0xFFE6F01E
		ADD r4, r0, #0
		BEQ      |loc_0801E608|
		MOV r3, #1
		MOV r2, #0xa
		MOV r1, #9
		ADD r0, r4, #0
		BL       |loc_08005460|
		LDR r0, [pc, #0x168]
		STR r0, [r4]
		MOV r0, #0xb
		LSL r0, r0, #6
		ADD r0, r4, r0
		STR r6, [r0, #0x38]
|loc_0801E608|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE7DF
|loc_0801E612|
|unk_0801E612|
		BL       |inc_0x03d784_0x041118| + 0x2912
		ADD r1, r4, #0
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r7, #0
		DCD     0xFFC8F01E
		CMP r0, #0
		BEQ      |loc_0801E642|
		LDR r1, [pc, #0x130]
		STMIA r0!, {r1, r6}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		LDR r1, [pc, #0x124]
		STR r1, [r0]
|loc_0801E642|
		BL       |inc_0x03d784_0x041118| + 0xcc
		MOV r0, #1
		DCW     0xE7C3
|loc_0801E64A|
|unk_0801E64A|
		BL       |inc_0x03d784_0x041118| + 0x2928
		ADD r1, r4, #0
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r7, #0
		DCD     0xFFACF01E
		CMP r0, #0
		BEQ      |loc_0801E67A|
		LDR r1, [pc, #0xf8]
		STMIA r0!, {r1, r6}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r6, [r1, #0xc]
		STR r6, [r1, #8]
		STR r6, [r1, #0x10]
		LDR r1, [pc, #0xec]
		STR r1, [r0]
|loc_0801E67A|
		BL       |inc_0x03d784_0x041118| + 0xcc
		DCW     0xE000
|loc_0801E680|
|unk_0801E680|
		B        |loc_0801E686|
		MOV r0, #1
		DCW     0xE7A5
