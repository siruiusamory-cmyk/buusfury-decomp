	CODE16
|sub_08027CD8|
|unk_08027CD8|
		MOV r1, #0xff
		ADD r1, #1
		MOV r2, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0xb0]
		STR r0, [r4]
		LDMIA r6!, {r1, r2}
		STR r1, [r4, #0x40]
		STR r2, [r4, #0x44]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r0, r7, #1
		ADD r0, r0, r7
		LDR r1, [pc, #0xa0]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		LSL r0, r0, #4
		MOV r5, #0
		STR r5, [r4, #0x50]
		ADD r0, r0, r1
		STR r0, [r4, #0x48]
		STR r5, [r4, #0x4c]
		STR r0, [r4, #0x18]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [pc, #0x84]
		LDR r6, [r0]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x14
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0x78]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDR r0, [pc, #0x78]
		ADD r3, r5, #0
		MOV r2, #0x40
		ADD r0, r6, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		DCW     0xE7CB
