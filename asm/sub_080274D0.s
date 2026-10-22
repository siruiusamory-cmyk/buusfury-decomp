	CODE16
|sub_080274D0|
|unk_080274D0|
		ADD r2, r7, #0
		MOV r1, #0x80
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x1b8]
		STR r0, [r4]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		MOV r0, #0
		STR r0, [r4, #0x48]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r0, r6, #1
		ADD r0, r0, r6
		LDR r1, [pc, #0x1a8]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		LSL r0, r0, #2
		ADD r0, r0, r1
		STR r0, [r4, #0x18]
		LDR r2, [pc, #0x1a0]
		LSL r0, r6, #3
		LDR r1, [r2, r0]
		ADD r0, r0, r2
		STR r1, [r4, #0x40]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x44]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		DCW     0xE7DB
