	CODE16
|sub_08035AD4|
|unk_08035AD4|
		ADD r0, r4, #0
		ADD r0, #0x28
		LDR r1, [r6, #4]
		ADD r5, r0, #0
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_08035AF0|
		ADD r0, r4, #0
		BL       |sub_08035A34|
		B        |inc_0x351c0_0x3d4d0| + 0x910
|loc_08035AF0|
		CMP r7, #0
		BEQ      |inc_0x351c0_0x3d4d0| + 0x910
		LDR r0, [r4, #0x1c]
		CMP r0, #0
		BEQ      |inc_0x351c0_0x3d4d0| + 0x910
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
		LDMIA r5!, {r1, r2, r3, r5}
		ADD r0, sp, #4
		STMIA r0!, {r1, r2, r3, r5}
		MOV r0, #0
		ADD r3, sp, #0
		STRB r0, [r3]
		STR r4, [sp, #0x30]
		ADD r2, r7, #0
		MOV r1, #0
		LDR r0, [r6]
		BL       |List_CallMethod1|
		CMP r0, #0
		BEQ      |inc_0x351c0_0x3d4d0| + 0x910
		ADD r0, r4, #0
		BL       |sub_08035A34|
		B        |inc_0x351c0_0x3d4d0| + 0x910
