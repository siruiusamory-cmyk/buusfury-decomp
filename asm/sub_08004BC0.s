	CODE16
|sub_08004BC0|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x228]
	ADD      r5, r0, #0
	LDR      r0, [r6]
	SUB      sp, #0x74
	BL       |loc_080048A0|
	LDR      r0, [r6]
	MOV      r1, #0
	LDRB     r0, [r0, #1]
	LSL      r0, r0, #0x1f
	LSR      r0, r0, #0x1f
	STR      r0, [r5]
	CMP      r0, #0
	BEQ      |sub_08004C84|
	LDR      r0, [r6]
	BL       |loc_08004A76|
	BL       |sub_08008A36|
	STRH     r0, [r5, #6]
	LDR      r0, [r6]
	MOV      r1, #0x13
	LSL      r1, r1, #6
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x10]
	BL       |inc_0x049120_0x055620| + 0x9fa8
	STR      r1, [r5, #8]
	LDR      r1, [pc, #0x1f4]
	MOV      r2, #0
	ADD      r0, sp, #4
	BL       |loc_08004098|
	LDR      r0, [sp, #8]
	MOV      r4, #0
	STRH     r0, [r5, #4]
	LDR      r0, [r6]
	LDRB     r0, [r0]
	STR      r0, [r5, #0x7c]
	ADD      r0, r5, #0
	ADD      r0, #0xc
	STR      r0, [sp, #0x70]
|loc_08004C16|
	LDR      r1, [pc, #0x1d4]
	LDR      r0, [r1]
	MOV      r1, #0x68
	MUL      r1, r4
	ADD      r0, r1, r0
	MOV      r1, #0x9f
	LSL      r1, r1, #3
	ADD      r7, r0, r1
	LDR      r0, [r5, #0x7c]
	CMP      r0, r4
	BEQ      |loc_08004C32|
	LDRB     r0, [r7]
	LSL      r0, r0, #0x1f
	BEQ      |loc_08004C7A|
|loc_08004C32|
	LDR      r0, [sp, #0x70]
	LDR      r1, [r0]
	ADD      r2, r1, #1
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #2
	ADD      r6, r1, r0
	ADD      r6, #4
	STR      r2, [r0]
	STR      r4, [r6, #8]
	LDRB     r0, [r7, #0x14]
	LDR      r1, [pc, #0x1a8]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	BL       |inc_0x153f2_0x1a3f2| + 0x1d4a
	STR      r0, [r6]
	LDR      r1, [r5, #0x7c]
	MOV      r0, #1
	CMP      r1, r4
	BEQ      |loc_08004C62|
	MOV      r0, #0
|loc_08004C62|
	LDR      r1, [pc, #0x188]
	STR      r0, [r6, #4]
	LDR      r1, [r1]
	LDRB     r1, [r1, #1]
	LSL      r1, r1, #0x1c
	LSR      r1, r1, #0x1f
	BEQ      |loc_08004C7A|
	LDRB     r1, [r7]
	LSL      r1, r1, #0x1e
	LSR      r1, r1, #0x1f
	ORR      r0, r1
	STR      r0, [r6, #4]
|loc_08004C7A|
	ADD      r4, #1
	CMP      r4, #9
	BLT      |loc_08004C16|
	ADD      sp, #0x74
	POP      {r4, r5, r6, r7, pc}
