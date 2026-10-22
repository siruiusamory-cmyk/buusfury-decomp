	CODE16
|sub_080212A0|
|unk_080212A0|
		MOV r1, #1
		LSL r1, r1, #0xc
		ADD r2, r7, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x2b8]
		STR r0, [r4]
		LDR r3, [r5]
		LDR r5, [r5, #4]
		LSL r3, r3, #8
		STR r3, [r4, #0x20]
		LSL r5, r5, #8
		STR r5, [r4, #0x24]
		STR r6, [r4, #0x5c]
		LDR r2, [sp, #0xc]
		MOV r5, #0
		STRB r2, [r4, #8]
		LDR r2, [r6, #4]
		ADD r0, r4, #0
		STR r2, [r4, #0x18]
		STR r5, [r4, #0x40]
		STR r5, [r4, #0x44]
		MOV r2, #1
		ADD r0, #0x54
		LSL r2, r2, #0xd
		STR r5, [r4, #0x48]
		STR r2, [r0]
		ADD r1, r0, #4
		LSR r0, r2, #4
		STR r0, [r1]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [pc, #0x284]
		ADD r3, r5, #0
		LDR r5, [pc, #0x288]
		LDR r0, [r0]
		MOV r2, #0x40
		ADD r0, r0, r5
		LDR r1, [pc, #0x27c]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		DCW     0xE7D0
