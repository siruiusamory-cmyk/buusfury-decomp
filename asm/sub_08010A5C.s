	CODE16
|sub_08010A5C|
|unk_08010A5C|
		MOV r3, #0
		ADD r2, r7, #0
		ADD r1, r6, #0
		ADD r0, r5, #0
		BL       |loc_080109AA|
		LDR r0, [pc, #0x108]
		MOV r2, #2
		STR r0, [r5]
		MOV r0, #9
		LSL r0, r0, #6
		ADD r0, r5, r0
		ADD r1, r0, #0
		ADD r1, #0x3a
		ADD r6, r0, #0
		ADD r0, #0x2e
		LDR r3, [pc, #0xf8]
		BL       |__vecmap1c__FPvT1iPFPv_v|
		ADD r1, r6, #0
		ADD r1, #0x4c
		MOV r2, #4
|loc_08010A88|
|unk_08010A88|
		ADD r0, r6, #0
		ADD r0, #0x3c
		LDR r3, [pc, #0xec]
		BL       |__vecmap1c__FPvT1iPFPv_v|
		ADD r0, r6, #0
		ADD r0, #0x56
		STR r0, [sp, #0x20]
		ADD r0, #1
		STR r0, [sp, #0x1c]
		ADD r0, #1
		STR r0, [sp, #0x18]
		ADD r0, #2
		STR r0, [sp, #0x14]
		ADD r0, #2
		STR r0, [sp, #0x10]
		ADD r0, #2
		STR r0, [sp, #0xc]
		ADD r0, #2
		STR r0, [sp, #8]
		ADD r0, #2
		STR r0, [sp, #4]
		ADD r7, r0, #2
		MOV r2, #0x56
		ADD r1, r4, #0
		ADD r0, r6, #0
		BL       |sub_08046DD0|
		MOV r1, #0x56
		LDRB r1, [r1, r4]
		LDR r0, [sp, #0x20]
		ADD r3, r4, #0
		STRB r1, [r0]
		MOV r1, #0x57
		LDRB r1, [r1, r4]
		LDR r0, [sp, #0x1c]
		ADD r3, #0x40
		STRB r1, [r0]
		MOV r1, #0x58
		LDRH r1, [r1, r4]
		LDR r0, [sp, #0x18]
		STRH r1, [r0]
		MOV r1, #0x5a
		LDRH r1, [r1, r4]
		LDR r0, [sp, #0x14]
		STRH r1, [r0]
		MOV r1, #0x5c
		LDRH r1, [r1, r4]
		LDR r0, [sp, #0x10]
		STRH r1, [r0]
		MOV r1, #0x5e
		LDRH r1, [r1, r4]
		LDR r0, [sp, #0xc]
		STRH r1, [r0]
		MOV r1, #0x60
		LDRH r1, [r1, r4]
		LDR r0, [sp, #8]
		STRH r1, [r0]
		MOV r1, #0x62
		LDRH r1, [r1, r4]
		LDR r0, [sp, #4]
		STRH r1, [r0]
		MOV r0, #0x64
		LDRH r0, [r0, r4]
		LDR r1, [pc, #0x64]
		STRH r0, [r7]
		LDRH r0, [r3, #0x26]
		ADD r3, r6, #0
		ADD r3, #0x40
		STRH r0, [r3, #0x26]
		LDRB r0, [r6, #0x14]
		LSL r3, r0, #1
		ADD r0, r3, r0
		LSL r0, r0, #3
		ADD r0, r0, r1
		BL       |inc_0x153f2_0x1a3f2| + 0x1d58
		MOV r1, #1
		LSL r1, r1, #9
		ADD r1, r5, r1
		STR r0, [r1, #0x2c]
		LDR r1, [r0]
		LDR r2, [r1]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |loc_08046AA4|
		MOV r1, #0
		ADD r0, r5, #0
		BL       |inc_0x0158_0x143f2| + 0x1081c
		ADD r0, r5, #0
		B        |inc_0x0158_0x143f2| + 0x10900
