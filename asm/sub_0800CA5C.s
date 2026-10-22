	CODE16
|sub_0800CA5C|
|unk_0800CA5C|
		LDR r0, [r0, #0x1c]
		CMP r0, #0
		BEQ      |loc_0800CAAE|
		LDR r0, [r2, #0x18]
		CMP r0, #0
		BNE      |loc_0800CA6A|
		B        |inc_0x0158_0x143f2| + 0xc902
|loc_0800CA6A|
		LDR r0, [r4, #0x14]
		LDR r1, [r3, #8]
		CMP r0, r1
		BGE      |loc_0800CAAE|
		LDR r0, [r3]
		LDR r1, [r4, #0x1c]
		CMP r0, r1
		BGE      |loc_0800CAAE|
		LDR r0, [r4, #0x18]
		LDR r1, [r3, #0xc]
		CMP r0, r1
		BGE      |loc_0800CAAE|
		LDR r0, [r3, #4]
		LDR r1, [r4, #0x20]
		CMP r0, r1
		BGE      |loc_0800CAAE|
		LDRB r0, [r2, #0x14]
		ADD r1, r6, #0
		STR r0, [r4, #0x10]
		LDR r0, [r2, #0x1c]
		LDRB r2, [r0]
		LDRB r0, [r0, #1]
		LSL r1, r2
		LSL r6, r0
		ORR r1, r6
		ADD r0, r1, #0
		LDRH r1, [r4, #0xe]
		AND r1, r0
		BEQ      |loc_0800CAAE|
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xc7ba
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0xc902
|loc_0800CAAE|
		MOV r0, #0
|loc_0800CAB0|
|unk_0800CAB0|
		B        |inc_0x0158_0x143f2| + 0xc902
|loc_0800CAB2|
|unk_0800CAB2|
		LDR r0, [r0, #0x1c]
		CMP r0, #0
		BEQ      |inc_0x0158_0x143f2| + 0xc9a0
		LDRB r0, [r2]
		CMP r0, #0
		BNE      |loc_0800CAC0|
		B        |inc_0x0158_0x143f2| + 0xc902
|loc_0800CAC0|
		LDR r0, [r4, #0x14]
		LDR r1, [r3, #8]
		CMP r0, r1
		BGE      |inc_0x0158_0x143f2| + 0xc9a0
		LDR r0, [r3]
		LDR r1, [r4, #0x1c]
		CMP r0, r1
		BGE      |inc_0x0158_0x143f2| + 0xc9a0
		LDR r0, [r4, #0x18]
		LDR r1, [r3, #0xc]
		CMP r0, r1
		BGE      |inc_0x0158_0x143f2| + 0xc9a0
		LDR r0, [r3, #4]
		LDR r1, [r4, #0x20]
		CMP r0, r1
		BGE      |inc_0x0158_0x143f2| + 0xc9a0
		LDR r0, [r2, #0x1c]
		ADD r1, r6, #0
		LDRB r2, [r0]
		LDRB r0, [r0, #1]
		LSL r1, r2
		LSL r6, r0
		ORR r1, r6
		ADD r0, r1, #0
		LDRH r1, [r4, #0xe]
		AND r0, r1
		B        |inc_0x0158_0x143f2| + 0xc902
|loc_0800CAF6|
|unk_0800CAF6|
		B        |loc_0800CAFC|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0xc902
