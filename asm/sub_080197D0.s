	CODE16
|sub_080197D0|
|unk_080197D0|
		MOV r1, #0xff
		ADD r1, #1
		ADD r2, r7, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x304]
		STR r0, [r4]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		MOV r5, #0
		STR r5, [r4, #0x48]
		STR r5, [r4, #0x4c]
		LDRB r0, [r4, #0x10]
		LDR r2, [pc, #0x2f0]
		LSL r1, r0, #1
		ADD r1, r1, r0
		LSL r1, r1, #4
		ADD r1, r1, r2
		STR r1, [r4, #0x50]
		LDR r2, [pc, #0x2e8]
		STR r1, [r4, #0x18]
		LSL r0, r0, #3
		LDR r1, [r2, r0]
		ADD r0, r0, r2
		MUL r1, r6
		STR r1, [r4, #0x40]
		LDR r0, [r0, #4]
		MUL r0, r6
		STR r0, [r4, #0x44]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		STR r5, [r4, #0x54]
		STR r5, [r4, #0x58]
		STR r5, [r4, #0x5c]
		STR r5, [r4, #0x60]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [pc, #0x2c4]
		SUB r0, #0xc
		LDR r6, [r0]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x14
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0x2b4]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDR r0, [pc, #0x2b4]
		ADD r3, r5, #0
		MOV r2, #0x40
		ADD r0, r6, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		B        |inc_0x153f2_0x1a3f2| + 0x43dc
