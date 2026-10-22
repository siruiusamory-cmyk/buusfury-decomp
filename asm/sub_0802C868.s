	CODE16
|sub_0802C868|
|unk_0802C868|
		CMP r7, #0
		BEQ      |inc_0x2bb4c_0x2d1c0| + 0xd18
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		BEQ      |inc_0x2bb4c_0x2d1c0| + 0xd18
		LDR r0, [r4, #0x1c]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		LDRB r0, [r4, #0x10]
		MOV r7, sp
		STRB r0, [r3, #0x14]
		LDR r0, [pc, #0x88]
		STR r0, [sp, #0x1c]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x18]
		LDMIA r6!, {r1, r2, r3, r6}
		ADD r0, sp, #4
		STMIA r0!, {r1, r2, r3, r6}
		MOV r0, #0
		ADD r3, sp, #0
		STRB r0, [r3]
		STR r4, [sp, #0x30]
		ADD r2, r7, #0
		MOV r1, #0
		LDR r0, [r5]
		BL       |loc_08011C70|
		CMP r0, #0
		BEQ      |inc_0x2bb4c_0x2d1c0| + 0xd18
		ADD r1, r4, #0
		LDR r0, [r5]
		BL       |loc_08011944|
		B        |inc_0x2bb4c_0x2d1c0| + 0xd18
