	CODE16
|sub_0801C700|
|unk_0801C700|
		MOV r1, #0xff
		ADD r1, #1
		ADD r2, r7, #0
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x1d4]
		STR r0, [r4]
		LDMIA r6!, {r1, r2}
		STR r1, [r4, #0x40]
		STR r2, [r4, #0x44]
		LDR r2, [r5]
		LDR r3, [r5, #4]
		LSL r2, r2, #8
		STR r2, [r4, #0x20]
		ADD r0, r4, #0
		LSL r3, r3, #8
		STR r3, [r4, #0x24]
		ADD r0, #0x4c
		MOV r5, #0
		MOV r1, #1
		LSL r1, r1, #0xb
		STR r5, [r4, #0x48]
		STR r1, [r0]
		ADD r6, r0, #4
		LDR r0, [pc, #0x1b4]
		LSR r1, r1, #2
		STR r1, [r6]
		STR r0, [r4, #0x18]
		MOV r0, #0x37
		STRB r0, [r4, #8]
		LDR r0, [r4, #0x44]
		SUB r0, r0, r1
		STR r0, [r4, #0x44]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		STRB r5, [r6, #4]
		ADD r0, r4, #0
		DCW     0xE7D6
