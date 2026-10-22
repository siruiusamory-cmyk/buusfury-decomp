	CODE16
|sub_0801C91C|
|unk_0801C91C|
		MOV r1, #0xff
		ADD r1, #1
		ADD r2, r7, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x250]
		LDR r3, [pc, #0x258]
		STR r0, [r4]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r0, r6, #1
		ADD r0, r0, r6
		LDR r1, [pc, #0x244]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		LSL r0, r0, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		MOV r2, #0
		STR r2, [r4, #0x48]
		LSL r0, r6, #3
		LDR r1, [r3, r0]
		ADD r0, r0, r3
		STR r1, [r4, #0x40]
		LDR r0, [r0, #4]
		ADD r3, r2, #0
		STR r0, [r4, #0x44]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		LDR r0, [pc, #0x224]
		LDR r5, [pc, #0x22c]
		SUB r0, #0xc
		LDR r0, [r0]
		MOV r2, #0x40
		ADD r0, r0, r5
		LDR r1, [pc, #0x21c]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		DCW     0xE7D0
