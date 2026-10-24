	CODE16
|sub_0802C6FE|
|unk_0802C6FE|
		LDR r0, [pc, #0x88]
		LDR r5, [r0]
		CMP r5, #0
		BNE      |loc_0802C70A|
		MOV r0, #1
		B        |inc_0x2bb4c_0x2d1c0| + 0xbae
|loc_0802C70A|
		ADD r0, r1, #0
		ADD r0, #0xff
		ADD r3, r4, #4
		LDR r6, [r4, #0x10]
		ADD r2, r3, #4
		ADD r0, #0xa1
		CMP r6, #0
		BEQ      |loc_0802C730|
		SUB r6, #1
		STR r6, [r4, #0x10]
		LDR r1, [r0]
		LDR r3, [r3]
		SUB r1, r1, r3
		STR r1, [r0]
		LDR r1, [r0, #4]
		LDR r2, [r2]
		SUB r1, r1, r2
		STR r1, [r0, #4]
		B        |loc_0802C776|
|loc_0802C730|
		LDR r6, [r0]
		LDR r3, [r3]
		MOV r7, #0x10
		ADD r3, r6, r3
		STR r3, [r0]
		LDR r3, [r0, #4]
		LDR r2, [r2]
		MOV r6, sp
		ADD r2, r3, r2
		STR r2, [r0, #4]
		STR r1, [sp, #0x20]
		LDRB r0, [r1, #0x10]
		ADD r3, sp, #0
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x3c]
		STR r1, [sp, #0x30]
		STR r0, [sp, #0x1c]
		LSL r0, r7, #6
		STR r0, [sp, #0x18]
		MOV r0, #0
		STRB r0, [r3]
		ADD r0, r6, #4
		BL       |Object_GetPoints|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x24]
		ADD r3, r2, r1
		ADD r2, r6, #0
		MOV r1, #1
		BL       |inc_0x046118_0x049114| + 0x98e
		CMP r0, #0
		BEQ      |loc_0802C776|
		STR r7, [r4, #0x10]
|loc_0802C776|
		MOV r0, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0xbae
	INCBIN  baserom.gba_0x2c77a_0x2c782.extracted
