	CODE16
|sub_08018C50|
|unk_08018C50|
		ADD r0, sp, #0xc
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		STR r0, [sp, #8]
		STR r0, [sp, #0x20]
		ADD r0, sp, #0x24
		ADD r1, r4, #0
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0x24]
		LDR r1, [sp, #0x2c]
		LDR r2, [sp, #0x30]
		ADD r1, r0, r1
		LDR r0, [sp, #0x28]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x38]
		ASR r1, r1, #1
		LDR r0, [sp, #0x1c]
		STR r1, [sp, #4]
		SUB r0, r0, r1
		STR r1, [sp, #0x34]
		LDR r1, [sp, #0x20]
		LDR r2, [sp, #0x38]
		STR r0, [sp, #4]
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #8]
		STR r1, [sp, #0x40]
		STR r0, [sp, #0x3c]
		BGE      |loc_08018CB0|
		NEG r0, r2
|loc_08018CB0|
		ADD r1, r0, #0
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BGE      |loc_08018CBA|
		NEG r0, r0
|loc_08018CBA|
		ADD r7, r1, #0
		CMP r1, r0
		STR r1, [sp, #0x34]
		STR r0, [sp, #0x38]
		BLE      |inc_0x153f2_0x1a3f2| + 0x38e0
		LDR r1, [sp, #0x3c]
		MOV r0, #2
		CMP r1, #0
		BLT      |loc_08018CCE|
		MOV r0, #3
|loc_08018CCE|
		STRB r0, [r4, #0x10]
|loc_08018CD0|
|unk_08018CD0|
		B        |loc_08018CDA|
		ADD r7, r0, #0
		LDR r0, [sp, #0x40]
		LSR r0, r0, #0x1f
		STRB r0, [r4, #0x10]
|loc_08018CDA|
		CMP r7, #0
		BNE      |loc_08018CE2|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x385a
|loc_08018CE2|
		LDR r5, [pc, #0x160]
		LDR r0, [r4, #0x14]
		CMP r0, r5
		BEQ      |loc_08018CFA|
		MOV r1, #1
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800ED18|
|loc_08018CFA|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		LDR r0, [sp, #0x3c]
		LDR r1, [sp, #0x40]
		LSL r0, r0, #8
		LSL r1, r1, #8
		STR r1, [sp, #0x38]
		STR r0, [sp, #0x34]
		LDR r1, [r6, #4]
		LDR r2, [sp, #0x38]
		MUL r0, r1
		MUL r2, r1
		ASR r1, r2, #8
		ASR r0, r0, #8
		ADD r5, r4, #0
		ADD r5, #0xff
		STR r1, [sp, #0x10]
		STR r1, [sp, #0x18]
		LSL r1, r0, #8
		ADD r5, #0xa1
		STR r0, [sp, #0xc]
		STR r0, [sp, #0x14]
		LSL r7, r7, #8
		ADD r0, r7, #0
		BL       |sub_08046E58|
		STR r0, [sp, #8]
		LDR r0, [sp, #0x18]
		LSL r1, r0, #8
		ADD r0, r7, #0
		BL       |sub_08046E58|
		LDR r1, [sp, #8]
		STR r0, [sp, #0x10]
		ADD r0, r1, #0
		STR r1, [sp, #0xc]
		LDR r1, [sp, #0x10]
		STR r0, [sp, #0x1c]
		STR r1, [sp, #0x20]
		LDR r0, [r5]
		LDR r1, [sp, #0x1c]
		ADD r7, r5, #4
		SUB r0, r0, r1
		LDR r1, [r5, #4]
		LDR r2, [sp, #0x20]
		STR r0, [sp, #0xc]
		SUB r1, r1, r2
		STR r1, [sp, #0x10]
		STR r1, [sp, #0x30]
		STR r1, [sp, #0x28]
		STR r0, [sp, #0x2c]
		STR r0, [sp, #0x24]
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x54]
		ADD r2, r2, r1
		ADD r1, sp, #0x2c
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_08018D88|
		LDR r0, [sp, #0x2c]
		STR r0, [r5]
		LDR r0, [sp, #0x30]
		STR r0, [r7]
		B        |loc_08018E04|
|loc_08018D88|
		ADD r0, r6, #4
		LDR r2, [sp, #0x3c]
		STR r0, [sp, #0x48]
		ADD r1, sp, #0x24
		CMP r2, #0
		BGE      |loc_08018D9C|
		LDR r0, [r6, #4]
		NEG r0, r0
		STR r0, [sp, #0x20]
		ADD r0, sp, #0x20
|loc_08018D9C|
		LDR r2, [r5]
		LDR r0, [r0]
		ADD r1, sp, #0x24
		SUB r0, r2, r0
		STR r0, [sp, #0x24]
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa5
		STR r0, [sp, #0x44]
		LDR r0, [r0]
		STR r0, [sp, #0x28]
		LDR r2, [r4]
		ADD r0, r4, #0
		LDR r3, [r2, #0x54]
		ADD r2, r3, r2
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_08018DCC|
		LDR r0, [sp, #0x24]
		STR r0, [r5]
		LDR r0, [sp, #0x28]
		STR r0, [r7]
		B        |loc_08018E04|
|loc_08018DCC|
		LDR r0, [r5]
		ADD r2, sp, #0x44
		STR r0, [sp, #0x24]
		LDMIA r2!, {r0, r2}
		LDR r3, [sp, #0x40]
		ADD r1, sp, #0x24
		CMP r3, #0
		BGE      |loc_08018DE4|
		LDR r2, [r6, #4]
		NEG r2, r2
		STR r2, [sp, #0x20]
		ADD r2, sp, #0x20
|loc_08018DE4|
		LDR r0, [r0]
		LDR r2, [r2]
		SUB r0, r0, r2
		STR r0, [sp, #0x28]
		LDR r2, [r4]
		ADD r0, r4, #0
		LDR r3, [r2, #0x54]
		ADD r2, r3, r2
		BL       |loc_08046AA4|
		CMP r0, #0
		BEQ      |loc_08018E16|
		LDR r0, [sp, #0x24]
		STR r0, [r5]
		LDR r0, [sp, #0x28]
		STR r0, [r7]
|loc_08018E04|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x385a
|loc_08018E16|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x385a
