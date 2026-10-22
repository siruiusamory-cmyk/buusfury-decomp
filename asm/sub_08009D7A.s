	CODE16
|sub_08009D7A|
|unk_08009D7A|
		LDR r1, [sp, #0x20]
		NEG r1, r1
|loc_08009D7E|
|unk_08009D7E|
		STR r1, [sp, #8]
		STR r1, [sp, #0x10]
		STR r1, [sp, #0x18]
		MOV r1, lr
		STR r0, [sp, #4]
		STR r0, [sp, #0xc]
		STR r0, [sp, #0x14]
		LDR r0, [r1]
		ADD r1, sp, #0x14
		STR r0, [r4, #0xc]
		LDMIA r1!, {r0, r1}
		CMP r0, r1
		BLT      |loc_08009DAC|
		LDR r0, [sp, #0x1c]
		LDR r1, [sp, #0x14]
		CMP r0, #0
		BLT      |loc_08009DA6|
		MOV r0, #3
		STRB r0, [r4, #0x12]
		B        |loc_08009DBE|
|loc_08009DA6|
		MOV r0, #2
		STRB r0, [r4, #0x12]
		B        |loc_08009DBE|
|loc_08009DAC|
		LDR r0, [sp, #0x20]
		MOV r2, #0
		CMP r0, #0
		LDR r1, [sp, #0x18]
		BLT      |loc_08009DBA|
		STRB r2, [r4, #0x12]
		B        |loc_08009DBE|
|loc_08009DBA|
		MOV r0, #1
		STRB r0, [r4, #0x12]
|loc_08009DBE|
		MOV r0, ip
		LDRH r0, [r0, #8]
		LSL r1, r1, #8
		BL       |sub_08046E58|
		ASR r0, r0, #8
		STRH r0, [r4, #0x10]
		LDRB r0, [r4, #0x12]
		STRB r0, [r7, #0x10]
		LDRH r0, [r4, #0x10]
		CMP r0, #0
		BEQ      |sub_08009E08|
		STR r5, [sp, #8]
		LDRH r0, [r4, #0x10]
		LSL r7, r0, #8
		LDR r0, [sp, #0x1c]
		LSL r1, r0, #8
		ADD r0, r7, #0
		BL       |sub_08046E58|
		ADD r5, r0, #0
		LDR r0, [sp, #0x20]
		LSL r1, r0, #8
		ADD r0, r7, #0
		BL       |sub_08046E58|
		STR r0, [sp, #4]
		LDR r1, [sp, #4]
		ADD r0, r5, #0
		STR r5, [sp]
		STR r5, [sp, #0xc]
		LDR r5, [sp, #8]
		STR r1, [sp, #0x10]
		STR r0, [r5]
		LDR r0, [sp, #0x10]
		STR r0, [r6]
		B        |inc_0x0158_0x143f2| + 0x9cba
