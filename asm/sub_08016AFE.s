	CODE16
|sub_08016AFE|
|unk_08016AFE|
		LDR r1, [r5, #0x30]
		MOV r0, #8
		STR r0, [r1, #8]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x24]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		LDR r0, [r5, #0x24]
		LSL r0, r0, #2
		ADD r0, r0, r6
		LDR r2, [r0, #4]
		MOV r0, #0xff
		ADD r0, #0x19
		STR r2, [sp]
		DCW     0xF026
		DCW     0xFD4B
		CMP r0, #0
		BEQ      |loc_08016B40|
		LDR r1, [pc, #0x1b0]
		LDR r2, [pc, #0x1b0]
		STMIA r0!, {r1, r7}
		SUB r0, #8
		ADD r1, r0, #0
		ADD r1, #0xff
		ADD r1, #1
		STR r7, [r1, #0xc]
		STR r7, [r1, #8]
		STR r7, [r1, #0x10]
		STR r2, [r0]
		LDR r2, [sp]
		STR r2, [r1, #0x14]
|loc_08016B40|
		BL       |inc_0x03d784_0x041118| + 0x11c
		CMP r0, #1
		BNE      |loc_08016B62|
		ADD r0, r4, #0
		BL       |sub_080164D0|
		LDR r0, [r6]
		LDR r1, [r5, #0x24]
		CMP r0, r1
		BGT      |loc_08016B5A|
		SUB r0, #1
		STR r0, [r5, #0x24]
|loc_08016B5A|
		LDR r0, [r5, #0x24]
		CMP r0, #0
		BGE      |loc_08016B62|
		STR r7, [r5, #0x24]
|loc_08016B62|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x170a
	INCBIN  baserom.gba_0x16b66_0x16c58.extracted
|loc_08016C58|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x170a
|sub_08016C5C|
	DCW      0x4b1b
