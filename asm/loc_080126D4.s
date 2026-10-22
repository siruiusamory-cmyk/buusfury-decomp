	CODE16
|loc_080126D4|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	ADD      r7, #0xc0
	ADD      r6, r0, #0
	LDR      r0, [r7, #0x10]
	ADD      r5, r1, #0
	CMP      r0, #0
	SUB      sp, #0x14
	BEQ      |loc_080127AA|
	CMP      r5, #0
	BEQ      |loc_080127AA|
	LDR      r1, [r5]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r5, #0
	ADD      r1, r2, r1
|loc_080126F4|
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r0, #0x16
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	CMP      r0, #0
	BEQ      |loc_080127AA|
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	STR      r1, [sp]
	LDR      r1, [sp, #4]
	STR      r0, [sp, #8]
	STR      r1, [sp, #0xc]
	ADD      r1, r0, #0
	LDR      r0, [sp, #0xc]
	ADD      r3, sp, #0
	STRH     r1, [r3, #4]
	STRH     r0, [r3, #6]
	LDR      r0, [r7, #4]
	ADD      r0, #1
	STR      r0, [r7, #4]
	MOV      r0, #1
	STR      r0, [r7, #0xc]
	LDR      r4, [r6]
	SUB      r4, #1
	BMI      |loc_080127A6|
|loc_08012736|
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	ADD      r3, sp, #0
	STR      r0, [sp, #0x10]
	MOV      r1, #4
	LDRSH    r1, [r3, r1]
	MOV      r3, #0
	ADD      r0, #4
	LDRSH    r2, [r0, r3]
	CMP      r1, r2
	BLT      |loc_080127A2|
	ADD      r3, sp, #0
	MOV      r1, #4
	LDRSH    r1, [r3, r1]
	MOV      r3, #4
	LDRSH    r2, [r0, r3]
	CMP      r1, r2
	BGE      |loc_080127A2|
	ADD      r3, sp, #0
	MOV      r1, #6
	LDRSH    r1, [r3, r1]
	MOV      r3, #2
	LDRSH    r2, [r0, r3]
	CMP      r1, r2
	BLT      |loc_080127A2|
	ADD      r3, sp, #0
	MOV      r1, #6
	LDRSH    r1, [r3, r1]
	MOV      r3, #6
	LDRSH    r0, [r0, r3]
	CMP      r1, r0
	BGE      |loc_080127A2|
	LDR      r1, [sp, #0x10]
	LDR      r0, [r1, #0xc]
	LDR      r2, [r0]
	LDR      r3, [r2, #8]
	ADD      r3, r3, r2
	ADD      r2, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	CMP      r0, #0
	BEQ      |loc_080127A2|
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	LDR      r1, [r0, #4]
	LDR      r0, [r1, #0xc]
	LDR      r2, [r0]
	LDR      r3, [r2, #4]
	ADD      r3, r3, r2
	ADD      r2, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	B        |loc_080127A6|
|loc_080127A2|
	SUB      r4, #1
	BPL      |loc_08012736|
|loc_080127A6|
	MOV      r0, #0
	STR      r0, [r7, #0xc]
|loc_080127AA|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	ADD      r5, r1, #0
	SUB      sp, #0x14
	BNE      |sub_080127BE|
	MOV      r0, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
