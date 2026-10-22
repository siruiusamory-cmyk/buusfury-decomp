	CODE16
|sub_08038502|
|unk_08038502|
		CMP r1, #0
		BEQ      |loc_080384FE|
		LDR r0, [r4, #0x3c]
		LDR r1, [r4, #0x34]
		LDR r2, [r4, #0x38]
		MUL r1, r0
		MUL r2, r0
		ADD r0, r1, #0
		STR r1, [sp, #0x34]
		ADD r1, r2, #0
		STR r2, [sp, #0x38]
		LDR r2, [r4, #0x1c]
		ADD r3, sp, #0
		ADD r0, r2, r0
		LDR r2, [r4, #0x20]
		STR r0, [sp, #0x34]
		ADD r1, r2, r1
		STR r1, [sp, #0x38]
		STR r1, [sp, #0x40]
		STR r0, [sp, #0x3c]
		LDR r0, [r4, #0x48]
		MOV r5, #1
		STR r0, [sp, #0x28]
		LDR r0, [r4, #0x40]
		ADD r1, r4, #0
		STRB r0, [r3, #0x1c]
		LDR r0, [pc, #0x1cc]
		ADD r1, #0x1c
		STR r0, [sp, #0x24]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x20]
		STRB r5, [r3, #8]
		STR r4, [sp, #0x38]
		LDR r0, [sp, #0x3c]
		LDR r2, [r4, #0x1c]
		ADD r6, sp, #0x3c
		CMP r0, r2
		BGE      |loc_08038554|
		ADD r0, r6, #0
		B        |loc_08038556|
|loc_08038554|
		ADD r0, r1, #0
|loc_08038556|
		LDR r0, [r0]
		LDR r3, [sp, #0x40]
		SUB r0, #2
		STR r0, [sp, #0xc]
		ADD r0, r4, #0
		LDR r7, [r4, #0x20]
		ADD r0, #0x20
		ADD r2, r6, #4
		CMP r3, r7
		BGE      |loc_0803856E|
		ADD r3, r2, #0
		B        |loc_08038570|
|loc_0803856E|
		ADD r3, r0, #0
|loc_08038570|
		LDR r3, [r3]
		SUB r3, #2
		STR r3, [sp, #0x10]
		LDR r3, [sp, #0x3c]
		LDR r7, [r1]
		CMP r3, r7
		BLE      |loc_08038580|
		ADD r1, r6, #0
|loc_08038580|
		LDR r1, [r1]
		ADD r1, #2
		STR r1, [sp, #0x14]
		LDR r1, [sp, #0x40]
		LDR r3, [r0]
		CMP r1, r3
		BLE      |loc_08038590|
		ADD r0, r2, #0
|loc_08038590|
		LDR r0, [r0]
		LDR r6, [pc, #0x14c]
		ADD r0, #2
		STR r0, [sp, #0x18]
		LDR r1, [r6, #8]
		ADD r7, sp, #8
		ADD r0, r7, #4
		ADD r1, #0x80
		LDR r1, [r1, #0x2c]
		BL       |loc_08009324|
		CMP r0, #0
		BEQ      |loc_080385EE|
		ADD r2, r7, #0
		MOV r1, #0
		LDR r0, [r6, #4]
		BL       |loc_08011C0C|
		CMP r0, #0
		BEQ      |loc_080385BC|
		STRB r5, [r4, #0x10]
		B        |loc_080384FE|
|loc_080385BC|
		LDR r0, [r4, #0x3c]
		CMP r0, #0x30
		BGE      |loc_080385C8|
		ADD r0, #4
		STR r0, [r4, #0x3c]
		B        |loc_080385E0|
|loc_080385C8|
		LDR r0, [r4, #0x34]
		LDR r1, [r4, #0x38]
		LSL r0, r0, #2
		LSL r1, r1, #2
		STR r1, [sp, #4]
		STR r0, [sp]
		LDR r2, [r4, #0x1c]
		ADD r0, r2, r0
		STR r0, [r4, #0x1c]
		LDR r0, [r4, #0x20]
		ADD r0, r0, r1
		STR r0, [r4, #0x20]
|loc_080385E0|
		LDR r0, [r4, #0x18]
		ADD r0, #1
		STR r0, [r4, #0x18]
		CMP r0, #0xf0
		BLE      |loc_080384FE|
		STRB r5, [r4, #0x10]
		B        |loc_080384FE|
|loc_080385EE|
		STRB r5, [r4, #0x10]
		B        |loc_080384FE|
