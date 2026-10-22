	CODE16
|sub_08009F06|
|unk_08009F06|
		LDR r0, [pc, #0x110]
		MOV r2, #1
		LDR r6, [r0]
		ADD r6, #0x80
		LDR r1, [r6, #0x28]
		ADD r0, r7, #0
		BL       |loc_08009930|
		MOV r2, #1
		ADD r0, r7, #0
		LDR r1, [r6, #0x30]
		BL       |loc_08009930|
		LDR r1, [r6, #0x28]
		LDR r0, [sp, #0x14]
		BL       |loc_08009324|
		CMP r0, #0
		BNE      |loc_08009F7A|
		MOV r2, #0
		ADD r0, r7, #0
		LDR r1, [r6, #0x28]
		BL       |loc_08009930|
		MOV r2, #0
		ADD r0, r7, #0
		LDR r1, [r6, #0x30]
		BL       |loc_08009930|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_08009F60|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
|loc_08009F60|
		LDR r1, [sp, #0x40]
		LDR r2, [sp, #0x3c]
		LDR r0, [r1]
		LDR r2, [r2]
		SUB r0, r0, r2
		STR r0, [r1]
		LDR r2, [sp, #0x38]
		LDR r0, [r1, #4]
		LDR r2, [r2]
		SUB r0, r0, r2
		STR r0, [r1, #4]
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x9daa
|loc_08009F7A|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_08009F9A|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
|loc_08009F9A|
		LDRB r0, [r5, #0x12]
		MOV r2, #0
		STRB r0, [r4, #0x10]
		LDR r1, [r6, #0x28]
		LDR r0, [sp, #0x14]
		BL       |loc_08009930|
		LDR r1, [r6, #0x30]
		LDR r0, [sp, #0x14]
		MOV r2, #0
		BL       |loc_08009930|
		LDRH r0, [r5, #0x10]
		SUB r0, #1
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		STRH r0, [r5, #0x10]
		BNE      |loc_0800A00A|
		ADD r1, r4, #0
		ADD r0, sp, #4
		BL       |sub_0800FDFA|
		MOV r2, #1
		ADD r0, sp, #4
		LDR r1, [r6, #0x28]
		BL       |loc_08009930|
		MOV r2, #1
		ADD r0, sp, #4
		LDR r1, [r6, #0x30]
		BL       |loc_08009930|
		MOV r3, #0xc
		LDRSH r0, [r5, r3]
		MOV r3, #0xe
		LDRSH r2, [r5, r3]
		LDR r1, [sp, #0x40]
		LSL r0, r0, #8
		LSL r2, r2, #8
		STMIA r1!, {r0, r2}
		ADD r1, r4, #0
		ADD r0, sp, #4
		BL       |sub_0800FDFA|
		MOV r2, #0
		ADD r0, sp, #4
		LDR r1, [r6, #0x28]
		BL       |loc_08009930|
		MOV r2, #0
		ADD r0, sp, #4
		LDR r1, [r6, #0x30]
		BL       |loc_08009930|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x9daa
|loc_0800A00A|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x9daa
