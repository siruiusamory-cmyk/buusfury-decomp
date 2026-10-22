	CODE16
|loc_0803B0FC|
|unk_0803B0FC|
		LDR r6, [pc, #0xc8]
		LDRB r0, [r6]
		CMP r0, #1
		BEQ      |loc_0803B1B2|
		LDR r0, [pc, #0xcc]
		LDR r0, [r0]
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		LDR r1, [r4, #0x14]
		SUB r0, r0, r1
		LDR r1, [sp, #0x10]
		LDR r2, [r4, #0x18]
		STR r0, [sp, #4]
		SUB r1, r1, r2
		STR r1, [sp, #8]
		ADD r2, r1, #0
		ADD r1, r0, #0
		LDR r0, [r4, #0x18]
		LDR r3, [r4, #0x14]
		STR r0, [sp, #0x18]
		STR r3, [sp, #0x14]
		LDR r0, [r4, #0x10]
		ASR r0, r0, #8
		STR r0, [sp, #0x1c]
		LDR r0, [r4, #0x1c]
		STR r0, [sp, #0x2c]
		MOV r0, #1
		LSL r0, r0, #0xa
		STR r0, [sp, #0x24]
		ADD r0, r1, #0
		CMP r1, #0
		BGE      |loc_0803B152|
		NEG r0, r0
|loc_0803B152|
		ADD r3, r2, #0
		CMP r2, #0
		BGE      |loc_0803B15A|
		NEG r3, r2
|loc_0803B15A|
		MOV r7, #3
		CMP r0, r3
		BLE      |sub_0803B16A|
		ADD r0, r7, #0
		CMP r1, #0
		BGT      |loc_0803B172|
		MOV r0, #2
		B        |loc_0803B172|
