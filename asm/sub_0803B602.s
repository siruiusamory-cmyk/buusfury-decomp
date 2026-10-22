	CODE16
|sub_0803B602|
|unk_0803B602|
		LDR r1, [sp, #0x24]
		LDR r2, [sp, #0x44]
		LDR r3, [sp, #0x48]
		ADD r2, r1, r2
		LDR r1, [sp, #0x28]
		STR r2, [sp, #0x14]
		ADD r3, r1, r3
		STR r3, [sp, #0x18]
		STR r3, [sp, #0x20]
		STR r2, [sp, #0x1c]
		ADD r0, r4, #0
		LDR r2, [r0]
		ADD r1, sp, #0x1c
		LDR r3, [r2, #0x54]
		ADD r2, r3, r2
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_0803B62C|
		MOV r6, #1
		B        |loc_0803B634|
|loc_0803B62C|
|unk_0803B62C|
		ADD r0, r7, #0
		SUB r7, #1
		CMP r0, #0
		BGT      |inc_0x351c0_0x3d4d0| + 0x63f4
|loc_0803B634|
		LDR r1, [sp, #0x54]
		ADD r1, #0xc
		ADD r0, r1, #4
		CMP r5, #0
		BEQ      |loc_0803B64C|
		CMP r6, #0
		BNE      |loc_0803B65E|
		LDR r2, [sp, #0x2c]
		STR r2, [r1]
		LDR r1, [sp, #0x30]
		STR r1, [r0]
		B        |inc_0x351c0_0x3d4d0| + 0x651c
|loc_0803B64C|
		CMP r6, #0
		BEQ      |loc_0803B65E|
		CMP r5, #0
		BNE      |loc_0803B65E|
		LDR r2, [sp, #0x24]
		STR r2, [r1]
		LDR r1, [sp, #0x28]
		STR r1, [r0]
		B        |inc_0x351c0_0x3d4d0| + 0x651c
|loc_0803B65E|
		LDR r2, [sp, #0x80]
		LDR r3, [sp, #0x2c]
		LDR r4, [sp, #0x30]
		SUB r2, r2, r3
		LDR r3, [sp, #0x84]
		STR r2, [sp, #0xc]
		SUB r3, r3, r4
		STR r3, [sp, #0x20]
		STR r3, [sp, #0x10]
		STR r3, [sp, #0x18]
		STR r2, [sp, #0x14]
		STR r2, [sp, #0x1c]
		LDR r2, [sp, #0x80]
		LDR r3, [sp, #0x24]
		LDR r4, [sp, #0x28]
		SUB r2, r2, r3
		LDR r3, [sp, #0x84]
		STR r2, [sp, #4]
		SUB r3, r3, r4
		STR r2, [sp, #0xc]
		STR r2, [sp, #0x14]
		LDR r2, [sp, #0x1c]
		STR r3, [sp, #8]
		STR r3, [sp, #0x10]
		STR r3, [sp, #0x18]
		ASR r3, r2, #8
		LDR r2, [sp, #0x20]
		STR r3, [sp, #4]
		ASR r2, r2, #8
		STR r2, [sp, #8]
		STR r2, [sp, #0x10]
		ADD r2, r3, #0
		MUL r2, r3
		STR r3, [sp, #0xc]
		LDR r3, [sp, #0x10]
		ADD r4, r3, #0
		MUL r3, r4
		ADD r4, r2, r3
		LDR r2, [sp, #0x14]
		ASR r3, r2, #8
		LDR r2, [sp, #0x18]
		STR r3, [sp, #4]
		ASR r2, r2, #8
		STR r2, [sp, #8]
		STR r2, [sp, #0x10]
		ADD r2, r3, #0
		MUL r2, r3
		STR r3, [sp, #0xc]
		LDR r3, [sp, #0x10]
		ADD r7, r3, #0
		MUL r3, r7
		ADD r2, r2, r3
		CMP r4, r2
		BGE      |sub_0803B6D4|
		LDR r2, [sp, #0x2c]
		STR r2, [r1]
		LDR r1, [sp, #0x30]
		STR r1, [r0]
		B        |inc_0x351c0_0x3d4d0| + 0x651c
