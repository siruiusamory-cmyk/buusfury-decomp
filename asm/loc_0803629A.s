	CODE16
|loc_0803629A|
		STR r4, [sp, #0x38]
		LDRB r0, [r4, #0x10]
		ADD r3, sp, #0x20
		MOV r6, #0
		STRB r0, [r3, #0xc]
		LDR r0, [pc, #0xd0]
		ADD r3, sp, #0
		STR r0, [sp, #0x34]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x30]
		LDR r0, [r7, #0xc]
		ADD r2, sp, #0x18
		LSL r0, r0, #0xa
		STR r0, [sp, #0x30]
		STRB r6, [r3, #0x18]
		STR r4, [sp, #0x48]
		LDR r0, [r7, #0x10]
		CMP r0, #0
		BEQ      |loc_080362C6|
		LDR r0, [sp, #0x14]
		STRB r0, [r4, #0x10]
|loc_080362C6|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r3, [r1, #0x24]
		ADD r3, r3, r1
		MOV r1, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		CMP r0, #0
		BEQ      |loc_080362FE|
		LDR r0, [pc, #0xa0]
		LDR r4, [r0]
		MOV r0, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r0, #0x30
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [pc, #0x94]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDR r0, [pc, #0x94]
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r4, r0
		BL       |inc_0x03d784_0x041118| + 0xbf4
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x100a
|loc_080362FE|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x100a
