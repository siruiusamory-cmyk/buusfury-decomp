	CODE16
|loc_080372A4|
	PUSH     {r4, r5, r6, r7, lr}
	MOV      ip, r3
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r5, [sp, #0x18]
	LDR      r4, [r0, #0x3c]
	LSL      r1, r1, #2
	ADD      r1, r4, r1
	MOV      r3, #0
	LDRSB    r6, [r1, r3]
	LDR      r4, [r0, #0x24]
	SUB      r3, r4, r6
	LDR      r6, [sp, #0x14]
	LDR      r4, [r6]
	ADD      r4, r3, r4
	MOV      r3, #1
	LDRSB    r7, [r1, r3]
	LDR      r6, [r0, #0x28]
	SUB      r3, r6, r7
	LDR      r6, [sp, #0x14]
	LDRB     r7, [r1, #3]
	LDR      r6, [r6, #4]
	ADD      r3, r3, r6
	MOV      lr, r3
	ADD      lr, r7
	LDR      r7, [pc, #0x1a0]
	LDRB     r6, [r1, #2]
	ADD      r7, #0x14
	LDR      r7, [r7, #8]
	ADD      r6, r4, r6
	CMP      r4, r7
	BGE      |loc_08037374|
	LDR      r7, [pc, #0x190]
	ADD      r7, #0x14
	LDR      r7, [r7]
	CMP      r7, r6
	BGE      |loc_08037374|
	LDR      r6, [pc, #0x188]
	ADD      r6, #0x14
	LDR      r7, [r6, #0xc]
	CMP      r3, r7
	BGE      |loc_08037374|
	LDR      r6, [r6, #4]
	CMP      r6, lr
	BGE      |loc_08037374|
	LDR      r6, [r2]
	LDR      r1, [r1, #4]
	LDR      r7, [pc, #0x178]
	STR      r1, [r6]
	LDR      r1, [r2]
	LSL      r4, r4, #0x17
	LDR      r6, [r1]
	LSR      r4, r4, #7
	AND      r6, r7
	ORR      r4, r6
	STR      r4, [r1]
	LSR      r4, r4, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r4, r4, #8
	LDR      r1, [r2]
	ORR      r3, r4
	STR      r3, [r1]
	ADD      r1, r3, #0
	ADD      r3, r5, #1
	BEQ      |loc_08037342|
	MOV      r4, #0xff
	ADD      r4, #1
	ORR      r1, r4
	LDR      r3, [r2]
	MOV      r4, #0x1f
	STR      r1, [r3]
	LSL      r4, r4, #0x19
	BIC      r1, r4
	LSL      r4, r5, #0x1b
	LSR      r4, r4, #2
	LDR      r3, [r2]
	ORR      r1, r4
	STR      r1, [r3]
|loc_08037342|
	LDRH     r1, [r0, #0xc]
	ADD      r3, r1, #0
	LDR      r1, [r2]
	ADD      r3, ip
	ADD      r1, #4
	LDR      r4, [r1]
	LSL      r3, r3, #0x16
	LSR      r4, r4, #0xa
	LSL      r4, r4, #0xa
	LSR      r3, r3, #0x16
	ORR      r3, r4
	STR      r3, [r1]
	LDRB     r0, [r0, #8]
	MOV      r4, #3
	LSL      r4, r4, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r3, r4
	LDR      r1, [r2]
	ORR      r0, r3
	STR      r0, [r1, #4]
	LDR      r0, [r2]
	ADD      r0, #8
	STR      r0, [r2]
|loc_08037374|
	POP      {r4, r5, r6, r7, pc}
|sub_08037376|
|unk_08037376|
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r0, [r1]
		SUB sp, #0x14
		STR r0, [sp, #0x10]
		LDR r0, [r4, #0x18]
		MOV r7, #0
		MVN r7, r7
		ADD r6, r1, #0
		SUB r0, #0xff
		SUB r0, #1
		BEQ      |loc_080373CA|
		LDR r0, [r6, #4]
		ADD r5, r0, #0
		ADD r0, #0x20
		STR r0, [r6, #4]
		LDR r0, [r6, #8]
		ADD r7, r0, #0
		ADD r0, #1
		STR r0, [r6, #8]
		MOV r0, #1
		LSL r0, r0, #0x10
		LDR r1, [r4, #0x18]
		SWI 6
		MOV r1, #0x7f
		LDR r3, [r4, #0x38]
		MVN r1, r1
		CMP r3, #0
		BEQ      |loc_080373EA|
		MOV r2, #0xff
		ADD r2, #1
		CMP r3, #1
		BEQ      |loc_080373F6|
		CMP r3, #2
		BEQ      |loc_08037402|
		CMP r3, #3
		BNE      |loc_080373CA|
		STRH r2, [r5, #6]
		MOV r2, #0
		STRH r2, [r5, #0xe]
		STRH r2, [r5, #0x16]
		STRH r0, [r5, #0x1e]
|loc_080373CA|
		LDR r1, [pc, #0xac]
		MOV r3, #0
		ADD r1, #0xc
		STR r1, [sp]
		MOV r1, #0
		ADD r0, r4, #0
		STR r7, [sp, #4]
		ADD r2, sp, #0x10
		BL       |loc_080372A4|
		LDR r0, [r4, #0x34]
		MOV r5, #0x10
		SUB r0, #1
		CMP r0, #0x10
		BLE      |inc_0x351c0_0x3d4d0| + 0x227c
		B        |sub_0803740E|
|loc_080373EA|
		STRH r0, [r5, #6]
		MOV r2, #0
		STRH r2, [r5, #0xe]
		STRH r2, [r5, #0x16]
		STRH r1, [r5, #0x1e]
		B        |loc_080373CA|
|loc_080373F6|
		STRH r0, [r5, #6]
		MOV r1, #0
		STRH r1, [r5, #0xe]
		STRH r1, [r5, #0x16]
		STRH r2, [r5, #0x1e]
		B        |loc_080373CA|
|loc_08037402|
		STRH r1, [r5, #6]
		MOV r2, #0
		STRH r2, [r5, #0xe]
		STRH r2, [r5, #0x16]
		STRH r0, [r5, #0x1e]
		B        |loc_080373CA|
