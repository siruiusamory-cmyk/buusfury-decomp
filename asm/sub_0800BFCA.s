	CODE16
|sub_0800BFCA|
|unk_0800BFCA|
		MOV r0, #1
		POP {r4, pc}
		PUSH {r3, r4, r5, r6, r7, lr}
		LDMIA r1!, {r2, r3}
		SUB r1, #8
		ADD r4, r3, #0
		ADD r3, #0x20
		STR r3, [r1, #4]
		LDR r3, [r1, #8]
		ADD r5, r3, #0
		ADD r3, #1
		STR r3, [r1, #8]
		MOV r3, #0
		LSL r5, r5, #0x1b
		LSR r6, r5, #2
		MOV ip, r6
|loc_0800BFEA|
		LDR r6, [pc, #0xd4]
		LSL r5, r3, #0x15
		ADD r5, r5, r6
		STR r5, [r2]
		LDRH r6, [r0, #0xc]
		LSL r7, r3, #4
		ADD r3, #1
		ADD r6, r6, r7
		LDR r7, [r2, #4]
		LSL r6, r6, #0x16
		LSR r7, r7, #0xa
		LSL r7, r7, #0xa
		LSR r6, r6, #0x16
		ORR r6, r7
		STR r6, [r2, #4]
		MOV r6, #0x1f
		LSL r6, r6, #0x19
		BIC r5, r6
		MOV r6, ip
		ORR r5, r6
		STR r5, [r2]
		ADD r2, #8
		CMP r3, #7
		BLT      |loc_0800BFEA|
		LDR r3, [pc, #0xa8]
		MOV r6, ip
		STR r3, [r2]
		LDRH r3, [r0, #0xc]
		LDR r5, [r2, #4]
		ADD r3, #0x70
		LSL r3, r3, #0x16
		LSR r5, r5, #0xa
		LSL r5, r5, #0xa
		LSR r3, r3, #0x16
		ORR r3, r5
		STR r3, [r2, #4]
		LDR r3, [pc, #0x90]
		ORR r3, r6
		STR r3, [r2]
		ADD r2, #8
		STR r2, [r1]
		MOV r2, #0xff
		ADD r2, #1
		STRH r2, [r4, #6]
		MOV r1, #0
		STRH r1, [r4, #0xe]
		STRH r1, [r4, #0x16]
		LDRB r0, [r0, #0x10]
		CMP r0, #0x10
		BLS      |sub_0800C052|
		STRH r2, [r4, #0x1e]
		B        |inc_0x0158_0x143f2| + 0xbf04
