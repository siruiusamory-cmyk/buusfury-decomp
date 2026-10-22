	CODE16
|sub_08018626|
|unk_08018626|
		LDR r2, [pc, #0x164]
		LDR r3, [r0, #0x14]
		LDR r2, [r2, #4]
		ADD r2, #0x28
		LDR r4, [r2]
		SUB r3, r3, r4
		LDR r4, [r0, #0x18]
		LDR r2, [r2, #4]
		STR r3, [sp]
		SUB r2, r4, r2
		STR r2, [sp, #4]
		ADD r2, r3, #0
		LDR r3, [sp, #4]
		STR r2, [sp, #8]
		STR r3, [sp, #0xc]
		LDR r2, [r1]
		LDR r4, [pc, #0x158]
		ADD r3, r2, #0
		ADD r3, #8
		STR r3, [r1]
		ADD r1, r2, #0
		LDR r2, [r0, #0x10]
		LDR r2, [r2, #0xc]
		LDR r3, [sp, #8]
		AND r2, r4
		LSL r3, r3, #0x17
		LSR r3, r3, #7
		ORR r3, r2
		LDR r2, [sp, #0xc]
		LSR r3, r3, #8
		LSL r2, r2, #0x18
		LSR r2, r2, #0x18
		LSL r3, r3, #8
		ORR r3, r2
		STR r3, [r1]
		LDRB r2, [r0, #8]
		MOV r4, #3
		LSL r4, r4, #0xa
		LSL r3, r2, #0x1a
		LDR r2, [r1, #4]
		LSR r3, r3, #0x1e
		LSL r3, r3, #0xa
		BIC r2, r4
		ORR r3, r2
		STR r3, [r1, #4]
		LDR r0, [r0, #0x10]
		LSR r2, r3, #0xa
		LDR r0, [r0, #8]
		LSL r2, r2, #0xa
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x16
		LSR r0, r0, #0x16
		ORR r0, r2
		STR r0, [r1, #4]
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x322e
