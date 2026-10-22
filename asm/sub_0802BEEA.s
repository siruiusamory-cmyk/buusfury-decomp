	CODE16
|sub_0802BEEA|
|unk_0802BEEA|
		LDR r0, [pc, #0x16c]
		LSL r5, r6, #5
		STR r0, [r4]
		LDR r0, [pc, #0x168]
		STRH r5, [r4, #0xe]
		LDR r0, [r0]
		ADD r1, r5, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_0802BF14|
		LDR r0, [pc, #0x158]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |sub_08011732|
		LDR r0, [pc, #0x150]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |loc_0801124C|
|loc_0802BF14|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x148]
		ADD r1, r6, #0
		STR r0, [r4]
		MOV r2, #0x20
		ADD r5, sp, #0x10
		ADD r0, r5, #0
		STR r6, [r4, #0x10]
		BL       |loc_0803F540|
		LDR r0, [pc, #0x130]
		ADD r3, sp, #0
		LDR r0, [r0, #4]
		MOV r1, #2
		STR r0, [sp, #0x1c]
		MOV r0, #1
		STRB r0, [r3, #0x10]
		STRB r1, [r3, #0x13]
		STRB r0, [r3, #0x12]
		LDR r0, [pc, #0x128]
		STR r0, [sp, #0x30]
		LDR r0, [r4, #0x10]
		LDR r2, [sp, #0x40]
		LSR r1, r0, #0x1f
		ADD r0, r1, r0
		ASR r0, r0, #1
		STR r0, [sp, #0x14]
		MOV r0, #0x16
		STR r0, [sp, #0x18]
		LDR r0, [sp, #0x34]
		MOV r1, #0
		BL       |sub_08046E40|
		ADD r0, r5, #0
		LDR r1, [sp, #0x4c]
		BL       |loc_0803DADA|
		LDR r0, [r4, #0x10]
		LSR r1, r0, #0x1f
		ADD r0, r1, r0
		LDR r1, [r7]
		ASR r0, r0, #1
		SUB r0, r1, r0
		STR r0, [r4, #0x14]
		LDR r0, [r7, #4]
		SUB r0, #0x10
		STR r0, [r4, #0x18]
		MOV r0, #0
		STR r0, [sp, #4]
		MOV r0, #0x20
		STR r0, [sp, #0xc]
		LDR r1, [r4, #0x10]
		MOV r0, #0
		CMP r1, #0
		BLE      |loc_0802BFAA|
		MOV r6, sp
		ADD r7, sp, #0x10
|loc_0802BF86|
		ADD r5, r0, #0
		ADD r5, #0x20
		STR r5, [sp, #8]
		STR r0, [sp]
		LDRH r1, [r4, #0xc]
		LDR r2, [pc, #0xd4]
		LSL r0, r0, #5
		LSL r1, r1, #5
		ADD r1, r1, r2
		ADD r1, r1, r0
		ADD r2, r6, #0
		ADD r0, r7, #0
		BL       |sub_0804915C|
		LDR r1, [r4, #0x10]
		ADD r0, r5, #0
		CMP r1, r5
		BGT      |loc_0802BF86|
|loc_0802BFAA|
		MOV r0, #0
		STR r0, [r4, #4]
		STRB r0, [r4, #8]
		ADD r0, sp, #0x10
		MOV r1, #0
		BL       |sub_0803F58C|
		ADD r0, r4, #0
		B        |inc_0x2bb4c_0x2d1c0| + 0x39a
