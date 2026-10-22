	CODE16
|sub_0800A0C2|
|unk_0800A0C2|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_0800A0E2|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
|loc_0800A0E2|
		LDRB r0, [r5, #0x12]
		STRB r0, [r4, #0x10]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x4c]
		ADD r3, r2, r1
		MOV r2, #0
		ADD r1, r7, #0
		BL       |inc_0x046118_0x049114| + 0x98e
		LDRH r0, [r5, #0x10]
		SUB r0, #1
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		STRH r0, [r5, #0x10]
		BNE      |loc_0800A130|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		MOV r3, #0xc
		LDRSH r0, [r5, r3]
		MOV r3, #0xe
		LDRSH r1, [r5, r3]
		LSL r0, r0, #8
		LSL r1, r1, #8
		STMIA r6!, {r0, r1}
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x9f66
|loc_0800A130|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x9f66
