	CODE16
|sub_08010C14|
|unk_08010C14|
		LDR r1, [r4]
		MOV r2, #0x80
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		ADD r5, r0, #0
		ADD r5, #0x16
		MOV r3, #0
		LDRSH r1, [r5, r3]
		CMP r1, #0
		BNE      |loc_08010C32|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x10aba
|loc_08010C32|
		MOV r1, #0x45
		LSL r1, r1, #3
		ADD r2, r4, r1
		LDR r1, [r2]
		LDR r3, [r6]
		ADD r1, r1, r3
		ADD r3, r1, #0
		STR r1, [r2]
		ASR r1, r1, #0xa
		BNE      |loc_08010C4A|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x10aba
|loc_08010C4A|
		LSL r6, r1, #0xa
		SUB r3, r3, r6
		STR r3, [r2]
		MOV r3, #0
		LDRSH r2, [r5, r3]
		CMP r2, r1
		BGE      |loc_08010C64|
|loc_08010C58|
		STRH r7, [r5]
		MOV r3, #0
		LDRSH r1, [r5, r3]
		CMP r1, r7
		BNE      |loc_08010C58|
		B        |loc_08010C76|
|loc_08010C64|
		LDRH r2, [r5]
		SUB r1, r2, r1
		LSL r1, r1, #0x10
		ASR r1, r1, #0x10
|loc_08010C6C|
		STRH r1, [r5]
		MOV r3, #0
		LDRSH r2, [r5, r3]
		CMP r2, r1
		BNE      |loc_08010C6C|
|loc_08010C76|
		LDRB r1, [r0, #0x13]
		LSL r1, r1, #0x1f
		BPL      |loc_08010C80|
		BL       |loc_08013C66|
|loc_08010C80|
		MOV r3, #0
		LDRSH r0, [r5, r3]
		CMP r0, #0
		BEQ      |loc_08010C8C|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x10aba
|loc_08010C8C|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x7c]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x10aba
