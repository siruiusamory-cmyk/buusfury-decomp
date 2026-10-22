	CODE16
|sub_08012AB4|
|unk_08012AB4|
		LDR r0, [r6]
		LDR r1, [r7]
		ASR r0, r0, #8
		ASR r1, r1, #8
		STR r1, [sp, #8]
		STR r1, [sp, #0x10]
		STR r0, [sp, #4]
		STR r0, [sp, #0xc]
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0x248]
		ADD r6, sp, #0x14
		ADD r1, #0x14
		LSL r0, r0, #4
		ADD r1, r0, r1
		ADD r0, r6, #0
		ADD r2, sp, #0xc
		BL       |inc_0x049120_0x055620| + 0x9eb4
		STR r4, [sp, #0x24]
		ADD r2, r6, #0
		MOV r1, #3
		LDR r0, [r5, #4]
		BL       |List_CallMethod1|
		CMP r0, #0
		BNE      |loc_08012B28|
		ADD r1, r4, #0
		LDR r0, [r5, #0x10]
		BL       |inc_0x0158_0x143f2| + 0x12656
		CMP r0, #0
		BNE      |loc_08012B28|
