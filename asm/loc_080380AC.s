	CODE16
|loc_080380AC|
|unk_080380AC|
		MOV r0, #2
		STRB r0, [r4, #0x10]
		LDR r0, [r4, #0x40]
		LDR r1, [pc, #0xc8]
		LSL r0, r0, #3
		ADD r1, #0x28
		ADD r0, r0, r1
		LDR r1, [r0]
		LDR r3, [sp, #0x40]
		LDR r0, [r0, #4]
		ADD r1, r7, r1
		ADD r0, r3, r0
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		STMIA r6!, {r0, r1}
		MOV r0, #0xff
		ADD r0, #0xc9
		LDR r0, [r0, r5]
		SUB r6, #8
		CMP r0, #0
		BEQ      |loc_080380EE|
		LDRB r0, [r5, #0x10]
		LDR r1, [r4, #0x40]
		MOV r2, #1
		B        |loc_080380E4|
|loc_080380E2|
		B        |inc_0x351c0_0x3d4d0| + 0x2f7c
