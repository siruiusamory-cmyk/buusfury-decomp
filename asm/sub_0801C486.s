	CODE16
|sub_0801C486|
|unk_0801C486|
		ADD r1, r6, #0
		ADD r6, sp, #0x1c
		ADD r0, r6, #0
		BL       |sub_0800FDFA|
		ADD r2, r6, #0
		ADD r2, #8
		ADD r1, sp, #0x1c
		ADD r0, sp, #0xc
		BL       |inc_0x049120_0x055620| + 0x9e94
		LDR r0, [sp, #0xc]
		MOV r2, #1
		ASR r1, r0, #1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x30]
		MOV r0, #0
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x2c]
		STR r2, [sp, #0x18]
		ADD r2, sp, #0x14
		ADD r1, sp, #0x2c
		ADD r0, sp, #0x34
		BL       |inc_0x049120_0x055620| + 0x9e94
		MOV r0, #0x48
		DCD     0xF87AF021
		ADD r6, r0, #0
		BEQ      |loc_0801C4E8|
		STR r7, [sp, #4]
		LDR r7, [pc, #0x1ec]
		MOV r2, #0x38
		MOV r0, #1
		LSL r0, r0, #0xe
		STR r2, [sp, #8]
		ADD r2, r7, #0
		STR r0, [sp]
		MOV r3, #3
		ADD r0, r6, #0
		ADD r1, sp, #0x34
		BL       |loc_0802A81C|
		LDR r0, [pc, #0x1d8]
		STR r0, [r6]
		STR r7, [r6, #0x44]
|loc_0801C4E8|
		STR r6, [r4, #0xc]
		LDR r0, [r5, #4]
		ADD r1, r6, #0
		BL       |List_Append|
		B        |loc_0801C482|
