	CODE16
|sub_08016800|
|unk_08016800|
		LDR r1, [r5, #0x28]
		MOV r2, #1
		STR r2, [r1, #0x10]
		LDR r1, [r5, #0x28]
		LDR r3, [r5, #0x24]
		ADD r0, r2, #0
		CMP r3, #0
		BNE      |loc_08016812|
		MOV r0, #0
|loc_08016812|
		STR r0, [r1, #8]
		LDR r0, [r5, #0x2c]
		ADD r3, sp, #0x3fc
		STR r2, [r0, #0x10]
		LDR r1, [r3, #0x2c]
		LDR r0, [r5, #0x2c]
		LDR r1, [r1]
		LDR r2, [r5, #0x24]
		SUB r1, #1
		CMP r1, r2
		BEQ      |loc_0801682C|
		MOV r1, #1
		B        |loc_0801682E|
|loc_0801682C|
		MOV r1, #0
|loc_0801682E|
		STR r1, [r0, #8]
		LDR r0, [r5, #0x24]
		LDR r1, [r5, #0x20]
		CMP r1, r0
		BLE      |loc_0801683A|
		STR r0, [r5, #0x20]
|loc_0801683A|
		LDR r1, [r5, #0x20]
		SUB r0, #4
		CMP r1, r0
		BGE      |loc_08016844|
		STR r0, [r5, #0x20]
|loc_08016844|
		MOV r3, #0x70
		MOV r2, #0x37
		MOV r1, #0xdb
		ADD r0, r4, #0
		BL       |loc_080051B0|
		MOV r0, #0
		STRB r0, [r4]
		MOV r7, #0
|loc_08016856|
		LDR r0, [r5, #0x20]
		ADD r3, sp, #0x3fc
		ADD r2, r0, r7
		STR r2, [r3, #0x18]
		LDR r1, [r3, #0x2c]
		LDR r0, [r1]
		CMP r0, r2
		BLE      |inc_0x153f2_0x1a3f2| + 0x1406
		LDR r2, [r3, #0x18]
		LDR r1, [r3, #0x2c]
		LSL r0, r2, #2
		ADD r0, r0, r1
		LDR r1, [r0, #4]
		MOV r0, #0x34
		MUL r0, r1
		STR r1, [r3, #0x14]
		LDR r1, [pc, #0x228]
		ADD r6, r0, r1
		LDR r0, [r6, #0x28]
		ADD r1, sp, #0x10
		BL       |inc_0x03d784_0x041118| + 0x1bc
		LDR r1, [r6, #0x1c]
		LSL r2, r7, #3
		LSR r0, r1, #0x1f
		ADD r0, r0, r1
		MOV ip, r1
		MOV r1, #0x25
		ASR r0, r0, #1
		SUB r0, r1, r0
		STR r0, [sp]
		LDR r0, [r6, #0x20]
		ADD r2, r2, r7
		LSL r2, r2, #1
		ADD r3, sp, #0x3fc
		LSR r1, r0, #0x1f
		ADD r1, r1, r0
		STR r2, [r3, #0x20]
		ADD r2, #0x34
		ASR r1, r1, #1
		SUB r1, r2, r1
		LDR r2, [sp]
		STR r1, [sp, #4]
		ADD r1, r2, #0
		ADD r1, ip
		STR r1, [sp, #8]
		LDR r1, [sp, #4]
		MOV r2, sp
		ADD r0, r1, r0
		STR r0, [sp, #0xc]
		ADD r0, r4, #0
		ADD r1, sp, #0x10
		BL       |inc_0x03d784_0x041118| + 0x219e
		LDR r0, [pc, #0x1d4]
		ADD r3, sp, #0x3fc
		LDR r1, [r3, #0x14]
		LDR r0, [r0, #0xc]
		ADD r0, r0, r1
		STR r0, [r3, #0x1c]
		LDRB r0, [r0, #2]
		CMP r0, #1
		BLE      |loc_080168D8|
		LDRH r0, [r6, #6]
		B        |loc_080168DA|
|loc_080168D8|
		LDRH r0, [r6, #4]
|loc_080168DA|
		LDR r6, [pc, #0x1c0]
		LSL r0, r0, #2
		LDR r1, [r6, r0]
		LDR r0, [r5, #0xc]
		CMP r0, #2
		BNE      |loc_080168F4|
		ADD r3, sp, #0x3fc
		LDR r0, [r5, #0x24]
		LDR r2, [r3, #0x18]
		CMP r0, r2
		BNE      |loc_080168F4|
		MOV r0, #6
		B        |loc_080168F6|
|loc_080168F4|
		MOV r0, #2
|loc_080168F6|
		STRB r0, [r4, #3]
		ADD r3, sp, #0x3fc
		LDR r0, [r3, #0x20]
		MOV r2, #0x38
		ADD r0, #0x38
		STR r0, [r4, #8]
		STR r2, [r4, #4]
		ADD r0, r4, #0
		BL       |loc_0803DADA|
		ADD r3, sp, #0x3fc
		LDR r0, [r3, #0x1c]
		LDRB r2, [r0, #2]
		CMP r2, #1
		BLE      |loc_08016920|
		MOV r0, #0x9d
		LSL r0, r0, #2
		LDR r1, [r6, r0]
		ADD r0, r4, #0
		BL       |sub_0803DC96|
|loc_08016920|
		ADD r7, #1
		CMP r7, #5
		BLT      |loc_08016856|
		B        |inc_0x153f2_0x1a3f2| + 0x1406
