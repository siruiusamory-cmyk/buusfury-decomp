	CODE16
|sub_080127BE|
|unk_080127BE|
		ADD r0, r5, #0
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
		ADD r1, r0, #0
		LDR r0, [sp, #0x10]
		ADD r3, sp, #0
		STRH r1, [r3, #8]
		STRH r0, [r3, #0xa]
		LDR r4, [r6]
		SUB r4, #1
		BMI      |loc_08012842|
|loc_080127E8|
		LSL r0, r4, #2
		ADD r0, r0, r6
		ADD r3, sp, #0
		MOV r2, #8
		LDRSH r2, [r3, r2]
		LDR r1, [r0, #4]
		MOV r3, #4
		LDRSH r7, [r1, r3]
		ADD r0, r1, #4
		CMP r2, r7
		BLT      |loc_0801283E|
		ADD r3, sp, #0
		MOV r2, #8
		LDRSH r2, [r3, r2]
		MOV r3, #4
		LDRSH r7, [r0, r3]
		CMP r2, r7
		BGE      |loc_0801283E|
		ADD r3, sp, #0
		MOV r2, #0xa
		LDRSH r2, [r3, r2]
		MOV r3, #2
		LDRSH r7, [r0, r3]
		CMP r2, r7
		BLT      |loc_0801283E|
		ADD r3, sp, #0
		MOV r2, #0xa
		LDRSH r2, [r3, r2]
		MOV r3, #6
		LDRSH r0, [r0, r3]
		CMP r2, r0
		BGE      |loc_0801283E|
		LDR r0, [r1, #0xc]
		LDR r1, [r0]
		LDR r2, [r1, #0xc]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |Thunk_JumpRegister1|
		CMP r0, #0
		BEQ      |loc_0801283E|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x12662
|loc_0801283E|
		SUB r4, #1
		BPL      |loc_080127E8|
|loc_08012842|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x12662
