	CODE16
|sub_0800CC7A|
|unk_0800CC7A|
		LDR r2, [r1]
		LDR r6, [pc, #0x158]
		ADD r3, r2, #0
		ADD r3, #8
		STR r3, [r1]
		LDR r3, [r1, #4]
		MOV r7, #3
		ADD r5, r3, #0
		ADD r5, #0x20
		STR r5, [r1, #4]
		ADD r5, r4, #1
		STR r5, [r1, #8]
		ADD r1, r4, #0
		LDR r4, [r0, #0x20]
		MOV r5, #1
		LDR r4, [r4, #0x10]
		LSL r5, r5, #9
		ORR r4, r5
		LSR r5, r5, #1
		ORR r4, r5
		STR r4, [r2]
		LDR r5, [r0, #0x4c]
		AND r4, r6
		LSL r5, r5, #0x17
		LSR r5, r5, #7
		ORR r4, r5
		STR r4, [r2]
		LDR r5, [r0, #0x50]
		LSR r4, r4, #8
		LSL r5, r5, #0x18
		LSR r5, r5, #0x18
		LSL r4, r4, #8
		ORR r4, r5
		STR r4, [r2]
		LDRB r5, [r0, #8]
		LDR r6, [r2, #4]
		LSL r7, r7, #0xa
		LSL r5, r5, #0x1a
		LSR r5, r5, #0x1e
		LSL r5, r5, #0xa
		BIC r6, r7
		ORR r5, r6
		STR r5, [r2, #4]
		LDRH r6, [r0, #0x16]
		LSR r5, r5, #0xa
		LSL r5, r5, #0xa
		LSL r6, r6, #0x16
		LSR r6, r6, #0x16
		ORR r5, r6
		MOV r6, #0x1f
		LSL r6, r6, #0x19
		BIC r4, r6
		STR r5, [r2, #4]
		ADD r5, r4, #0
		LSL r1, r1, #0x1b
		LSR r1, r1, #2
		ORR r1, r5
		STR r1, [r2]
		LDR r1, [r0, #0x58]
		STRH r1, [r3, #6]
		MOV r1, #0
		STRH r1, [r3, #0xe]
		STRH r1, [r3, #0x16]
		LDR r0, [r0, #0x58]
		STRH r0, [r3, #0x1e]
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xcb1e
