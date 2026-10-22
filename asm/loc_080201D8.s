	CODE16
|loc_080201D8|
		LDR r2, [r4, #0xc]
		CMP r2, #0
		BEQ      |loc_080201F4|
		ADD r3, r7, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0xc]
		SUB r0, #1
		STR r0, [r4, #0xc]
		LSL r0, r0, #7
		LDR r0, [r6, r0]
		LDR r1, [r5, #0x34]
		STR r0, [r1, #8]
|loc_080201F4|
		MOV r0, #0
		MVN r0, r0
		STR r0, [r4, #0x1c]
		STR r7, [r4, #0x10]
		B        |loc_08020050|
