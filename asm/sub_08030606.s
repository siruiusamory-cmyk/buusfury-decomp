	CODE16
|sub_08030606|
	LSL      r0, r0, #0xc
	STRH     r0, [r1, #0xe]
	LSR      r5, r6, #1
	SUB      r0, r0, r4
	LSL      r0, r0, #0xc
	ADD      r1, #0x44
	LSL      r0, r0, #0xc
	ADD      r4, r7, #0
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	MOV      r3, #0
	STRH     r3, [r1, #0x12]
	MOV      r2, #0x38
	STRB     r2, [r1, #8]
	STRB     r3, [r1, #0x11]
	LDR      r2, [r0]
	LDR      r3, [r2, #8]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
|sub_08030630|
|unk_08030630|
		PUSH {r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		LDR r0, [pc, #0x218]
		ADD r4, r1, #0
		LDR r7, [r0]
		SUB sp, #0x44
		CMP r7, #0
		BEQ      |loc_08030722|
		LDRH r0, [r4, #0x12]
		ADD r6, r5, #4
		ADD r3, r6, #4
		STR r3, [sp, #0x40]
		CMP r0, #0
		BNE      |loc_08030724|
		ADD r1, r7, #0
		ADD r0, sp, #0x10
		BL       |Object_WriteBounds1|
		ADD r1, sp, #0x10
		ADD r0, sp, #0x20
		BL       |inc_0x049120_0x055620| + 0x67e0
		ADD r1, r4, #0
		ADD r0, sp, #0x28
		BL       |Object_WriteBounds1|
		ADD r1, sp, #0x28
		ADD r0, sp, #0x38
		BL       |inc_0x049120_0x055620| + 0x67e0
		LDR r0, [sp, #0x20]
		LDR r1, [sp, #0x38]
		LDR r2, [sp, #0x3c]
		SUB r0, r0, r1
		LDR r1, [sp, #0x24]
		STR r0, [sp, #8]
		SUB r1, r1, r2
		MOV r2, #1
		ADD r3, r2, #0
		CMP r0, #0
		STR r1, [sp, #0xc]
		BGT      |loc_08030686|
		NEG r3, r2
|loc_08030686|
		LSL r3, r3, #8
		MOV r2, #1
		CMP r1, #0
		BGT      |loc_08030690|
		NEG r2, r2
|loc_08030690|
		STR r3, [r6]
		LDR r3, [sp, #0x40]
		LSL r2, r2, #8
		STR r2, [r3]
		MOV r2, #0x20
		NEG r3, r2
		CMP r0, #0
		BGT      |loc_080306A2|
		ADD r2, r3, #0
|loc_080306A2|
		MOV r0, #0x20
		CMP r1, #0
		BGT      |loc_080306AA|
		ADD r0, r3, #0
|loc_080306AA|
		ADD r1, r7, #0
		ADD r7, sp, #8
		STR r0, [sp, #0x3c]
		ADD r0, r7, #0
		STR r2, [sp, #0x38]
		BL       |Object_WriteBounds1|
		ADD r1, r7, #0
		ADD r0, sp, #0x18
		BL       |inc_0x049120_0x055620| + 0x67e0
		ADD r1, r4, #0
		ADD r7, sp, #0x20
		ADD r0, r7, #0
		BL       |Object_WriteBounds1|
		ADD r1, r7, #0
		ADD r0, sp, #0x30
		BL       |inc_0x049120_0x055620| + 0x67e0
		LDR r0, [sp, #0x30]
		LDR r2, [sp, #0x38]
		MOV r3, #1
		ADD r1, r0, r2
		LDR r0, [sp, #0x3c]
		LDR r2, [sp, #0x34]
		STR r1, [sp]
		ADD r0, r2, r0
		LDR r2, [sp, #0x18]
		STR r0, [sp, #4]
		SUB r1, r2, r1
		LDR r2, [sp, #0x1c]
		STR r1, [sp]
		SUB r0, r2, r0
		ADD r2, r3, #0
		CMP r1, #0
		STR r0, [sp, #4]
		BGT      |loc_080306F8|
		NEG r2, r2
|loc_080306F8|
		LSL r1, r2, #8
		CMP r0, #0
		BGT      |loc_08030702|
		MOV r3, #0
		MVN r3, r3
|loc_08030702|
		LSL r0, r3, #8
		STR r0, [sp, #0x34]
		STR r1, [sp, #0x30]
		LDR r0, [r5, #4]
		MUL r0, r1
		ASR r0, r0, #8
		MOV r1, #0
		CMP r0, #0
		BGE      |loc_08030726|
		LDR r0, [r5, #8]
		LDR r2, [sp, #0x34]
		MUL r0, r2
		ASR r0, r0, #8
		BPL      |loc_08030726|
		MOV r0, #1
		B        |loc_08030728|
|loc_08030722|
		B        |loc_080307F6|
|loc_08030724|
		B        |inc_0x301c0_0x311c0| + 0x58a
|loc_08030726|
		MOV r0, #0
|loc_08030728|
		STRB r0, [r5, #0xc]
		STRB r1, [r4, #0x11]
		LDRB r0, [r5, #0xc]
		CMP r0, #0
		BEQ      |sub_08030740|
		CMP r0, #1
		BNE      |inc_0x301c0_0x311c0| + 0x58a
		MOV r1, #0xe
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		B        |inc_0x301c0_0x311c0| + 0x58a
