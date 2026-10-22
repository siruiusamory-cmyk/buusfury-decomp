	CODE16
|sub_08004792|
|unk_08004792|
		LSR r1, r0, #0x10
		BEQ      |loc_080047CC|
		LSL r3, r0, #0x10
		LSR r3, r3, #0x10
		LSL r5, r3, #0x1d
		MOV r4, #1
		ADD r2, r4, #0
		LSR r5, r5, #0x1d
		LSL r2, r5
		LDR r5, [pc, #0x68]
		LSR r3, r3, #3
		SUB r5, #0x14
		LDR r5, [r5, #4]
		ADD r3, r3, r5
		ADD r3, #0x50
		CMP r1, #1
		BEQ      |loc_080047D0|
		CMP r1, #2
		BEQ      |loc_080047DE|
		CMP r1, #3
		BNE      |loc_080047F2|
		LDRB r0, [r3, #5]
		ADD r1, r0, #0
		AND r1, r2
		BEQ      |loc_080047EE|
		BIC r0, r2
		STRB r0, [r3, #5]
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x4636
|loc_080047CC|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x4636
|loc_080047D0|
		LDRB r0, [r3, #5]
		AND r0, r2
		BEQ      |loc_080047DA|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x4636
|loc_080047DA|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x4636
|loc_080047DE|
		LDRB r0, [r3, #5]
		AND r0, r2
		BEQ      |loc_080047E8|
		MOV r0, #1
		B        |loc_080047EA|
|loc_080047E8|
		MOV r0, #0
|loc_080047EA|
		SUB r0, r4, r0
		B        |inc_0x0158_0x143f2| + 0x4636
|loc_080047EE|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x4636
|loc_080047F2|
		MOV r1, #0
		STR r1, [sp]
		STR r1, [sp, #0x44]
		MOV r2, #0
		ADD r1, r0, #0
		MOV r0, sp
		BL       |loc_08004038|
		LDR r0, [sp, #4]
		CMP r0, #0
		BEQ      |loc_0800480C|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x4636
|loc_0800480C|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x4636
	INCBIN  baserom.gba_0x4810_0x4812.extracted
