	CODE16
|sub_080293A4|
|unk_080293A4|
		MOV r1, #1
		LSL r1, r1, #0xa
		ADD r0, r4, #0
		LDR r2, [sp, #0xc]
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x208]
		LDR r2, [pc, #0x20c]
		STR r0, [r4]
		STR r7, [r4, #0x50]
		LDR r3, [r5]
		LDR r5, [r5, #4]
		LSL r3, r3, #8
		STR r3, [r4, #0x20]
		LSL r5, r5, #8
		STR r5, [r4, #0x24]
		MOV r3, #0
		STR r3, [r4, #0x48]
		STR r2, [r4, #0x54]
		ADD r0, r4, #0
		ADD r0, #0x40
		STR r3, [r4, #0x4c]
		STR r2, [r4, #0x18]
		STR r3, [r0]
		ADD r1, r0, #4
		STR r3, [r1]
		STRB r6, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		DCW     0xE7DD
