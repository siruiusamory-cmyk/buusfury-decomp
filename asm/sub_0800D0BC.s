	CODE16
|sub_0800D0BC|
|unk_0800D0BC|
		LDR r0, [pc, #0xdc]
		LDR r1, [pc, #0xe0]
		STR r0, [r4]
		MOV r0, #0
		STR r0, [r4, #0xc]
		STR r1, [r4]
		STR r5, [r4, #0x20]
		STR r4, [r4, #0x10]
		ADD r7, r4, #0
		ADD r7, #0x24
		LDMIA r5!, {r1, r2, r3}
		STMIA r7!, {r1, r2, r3}
		LDMIA r5!, {r3}
		SUB r5, #0x10
		STMIA r7!, {r3}
		LDR r1, [r4, #0x20]
		LDRB r2, [r1, #0x16]
		STRB r2, [r4, #8]
		LDR r2, [r5, #0xc]
		STR r2, [r4, #4]
		LDRB r1, [r1, #0x17]
		MOV r2, #1
		CMP r1, #0
		BNE      |loc_0800D0EE|
		MOV r2, #0
|loc_0800D0EE|
		STR r2, [r4, #0x1c]
		STRH r6, [r4, #0x14]
		STR r0, [r4, #0x18]
		LDR r0, [pc, #0xbc]
		LDR r1, [pc, #0xb8]
		STR r0, [r4]
		LDR r5, [sp, #0xc]
		STR r5, [r4, #0x34]
		LDRH r0, [r5, #0x16]
		CMP r0, r1
		BNE      |loc_0800D11A|
		LDR r0, [r5, #0x34]
		LDR r0, [r0, #0x2c]
		LDR r1, [r0, #4]
		LDR r0, [pc, #0x98]
		LDR r0, [r0]
		BL       |loc_0801124C|
		STRH r0, [r5, #0x16]
		ADD r0, r5, #0
		BL       |sub_0800D026|
|loc_0800D11A|
		LDR r1, [r4, #0x20]
		LDRH r0, [r5, #0x16]
		LDRH r1, [r1, #0x14]
		ADD r0, r0, r1
		STRH r0, [r4, #0x16]
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0xcf60
		BX       lr
