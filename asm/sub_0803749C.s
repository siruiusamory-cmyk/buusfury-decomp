	CODE16
|sub_0803749C|
|unk_0803749C|
		MOV r1, #1
		LSL r1, r1, #0xc
		ADD r2, r7, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x3cc]
		LDR r3, [pc, #0x3d0]
		STR r0, [r4]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		STR r6, [r4, #0x4c]
		LDRB r0, [r4, #0x10]
		MOV r5, #0
		LSL r1, r0, #3
		LDR r2, [r3, r1]
		ADD r1, r1, r3
		LSL r2, r2, #7
		STR r2, [r4, #0x44]
		LDR r1, [r1, #4]
		LSL r3, r0, #4
		LSL r1, r1, #7
		STR r1, [r4, #0x48]
		MOV r1, #0x37
		STRB r1, [r4, #8]
		LDR r1, [r6, #8]
		SUB r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r1, r0
		STR r0, [r4, #0x50]
		STR r0, [r4, #0x18]
		STR r5, [r4, #0x58]
		STR r5, [r4, #0x54]
		MOV r0, #0x40
		STRB r5, [r0, r4]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [pc, #0x38c]
		ADD r3, r5, #0
		LDR r5, [pc, #0x390]
		LDR r0, [r0]
		MOV r2, #0x40
		ADD r0, r0, r5
		LDR r1, [pc, #0x384]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r1, [pc, #0x388]
		LDRB r0, [r1]
		ADD r0, #1
		STRB r0, [r1]
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x22da
