	CODE16
|sub_0803A86C|
|unk_0803A86C|
		LDR r0, [sp, #8]
		MOV r1, #0
		STRB r0, [r4, #4]
		LDR r0, [pc, #0x3d8]
		STR r0, [r4]
		STRB r5, [r4, #0xa]
		STRB r6, [r4, #9]
		STRB r1, [r4, #0xc]
		STRB r1, [r4, #0xd]
		LDR r2, [sp, #0xc]
		LDR r3, [r2]
		LDR r2, [r2, #4]
		STR r2, [r4, #0x14]
		STR r3, [r4, #0x10]
		STRB r1, [r4, #8]
		LSL r1, r7, #0x18
		LSR r1, r1, #0x18
		ADD r0, r4, #0
		BL       |loc_0803A7FC|
		ADD r0, r4, #0
		B        |inc_0x351c0_0x3d4d0| + 0x56a8
