	CODE16
|loc_08025330|
|unk_08025330|
		LDR r1, [r6]
		MOV r0, #0
		CMP r1, #0
		BEQ      |loc_0802534A|
		LDR r1, [r4, #0x10]
		LSL r1, r1, #3
		ADD r1, r1, r6
		ADD r1, #4
		LDR r2, [r1]
		LDR r1, [r1, #4]
		CMP r2, r1
		BEQ      |loc_0802534A|
		MOV r0, #1
|loc_0802534A|
		LDR r1, [r4, #4]
		STR r0, [r1, #0x20]
		LDR r1, [r4, #8]
		STR r0, [r1, #0x20]
		DCW     0xE7D6
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDRB r0, [r0, #0xd]
		SUB sp, #0x34
		CMP r0, #0
		BEQ      |sub_080253E2|
		LDRB r0, [r4, #0xe]
		MOV r7, #0
		CMP r0, #0
		BEQ      |sub_0802536E|
		STRB r7, [r4, #0xe]
		STRB r7, [r4, #0xd]
		DCW     0xE030
