	CODE16
|sub_08038F3E|
|unk_08038F3E|
		ADD r1, r5, #0
		ADD r0, sp, #0x1c
		BL       |loc_0800FE34|
		LDR r0, [sp, #0x1c]
		LDR r1, [sp, #0x24]
		LDR r2, [sp, #0x28]
		ADD r1, r0, r1
		LDR r0, [sp, #0x20]
		STR r1, [sp, #0x14]
		ADD r0, r0, r2
		STR r0, [sp, #0x18]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp, #0x14]
		STR r1, [sp, #0x2c]
		STR r0, [sp, #0x18]
		STR r0, [sp, #0x30]
		LDR r0, [r7]
		MOV r4, #0
		CMP r0, #0
		LDR r6, [pc, #0x128]
		BLE      |loc_08038FC0|
|loc_08038F6C|
		LSL r0, r4, #2
		ADD r0, r0, r7
		LDR r1, [r0, #4]
		ADD r0, sp, #0xc
		BL       |loc_0800FE34|
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
		STR r0, [sp, #8]
		STR r0, [sp, #0x20]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		LDR r1, [sp, #0x2c]
		LDR r2, [sp, #0x30]
		SUB r0, r0, r1
		LDR r1, [sp, #0x20]
		STR r0, [sp, #0x14]
		SUB r1, r1, r2
		ADD r2, r0, #0
		ADD r3, r1, #0
		MUL r3, r1
		MUL r2, r0
		ADD r2, r2, r3
		CMP r2, r6
		STR r1, [sp, #0x18]
		BGE      |loc_08038FB8|
		ADD r6, r2, #0
		STR r0, [sp, #0x24]
		STR r1, [sp, #0x28]
|loc_08038FB8|
		LDR r0, [r7]
		ADD r4, #1
		CMP r0, r4
		BGT      |loc_08038F6C|
|loc_08038FC0|
		LDR r1, [sp, #0x24]
		CMP r1, #0
		BGE      |loc_08038FC8|
		NEG r1, r1
|loc_08038FC8|
		LDR r0, [sp, #0x28]
		CMP r0, #0
		BGE      |loc_08038FD0|
		NEG r0, r0
|loc_08038FD0|
		ADD r4, r1, #0
		CMP r1, r0
		STR r1, [sp, #0x1c]
		STR r0, [sp, #0x20]
		BLE      |loc_08038FE8|
		LDR r1, [sp, #0x24]
		MOV r0, #3
		CMP r1, #0
		BGT      |loc_08038FE4|
		MOV r0, #2
|loc_08038FE4|
		STRB r0, [r5, #0x10]
		B        |loc_08038FF6|
|loc_08038FE8|
		ADD r4, r0, #0
		LDR r1, [sp, #0x28]
|loc_08038FEC|
|unk_08038FEC|
		MOV r0, #1
		CMP r1, #0
		BLE      |loc_08038FF4|
		MOV r0, #0
|loc_08038FF4|
		STRB r0, [r5, #0x10]
|loc_08038FF6|
		CMP r4, #4
		BGE      |loc_08038FFE|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x3d7a
|loc_08038FFE|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x34]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		CMP r0, #0
		BNE      |loc_0803901E|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
|loc_0803901E|
		LDR r0, [sp, #0x24]
		LDR r1, [sp, #0x28]
		LSL r0, r0, #8
		STR r0, [sp, #0x1c]
		LDR r0, [sp, #0x34]
		LSL r1, r1, #8
		STR r1, [sp, #0x20]
		LDR r1, [r0, #4]
		LDR r0, [sp, #0x1c]
		LDR r2, [sp, #0x20]
		MUL r0, r1
		MUL r2, r1
		ASR r1, r2, #8
		ASR r0, r0, #8
		STR r1, [sp, #8]
		STR r1, [sp, #0x10]
		ADD r5, #0xff
		ADD r5, #0xa1
		LSL r1, r0, #8
		STR r0, [sp, #4]
		STR r0, [sp, #0xc]
		LSL r4, r4, #8
		ADD r0, r4, #0
		BL       |sub_08046E58|
		ADD r6, r0, #0
		LDR r0, [sp, #0x10]
		LSL r1, r0, #8
		ADD r0, r4, #0
		BL       |sub_08046E58|
		STR r0, [sp, #8]
		LDR r1, [sp, #8]
		STR r6, [sp, #4]
		STR r6, [sp, #0x14]
		STR r1, [sp, #0x18]
		LDR r0, [r5]
		ADD r0, r0, r6
		STR r0, [r5]
		LDR r0, [r5, #4]
		LDR r1, [sp, #0x18]
		ADD r0, r0, r1
		STR r0, [r5, #4]
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x3d7a
