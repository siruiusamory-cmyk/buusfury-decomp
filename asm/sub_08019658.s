	CODE16
|sub_08019658|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0x1fc
	LDR      r2, [pc, #0x140]
	SUB      sp, #8
	STR      r2, [r0]
	LDRB     r3, [r4, #0x18]
	MOV      r5, #3
	LSL      r5, r5, #0xa
	ORR      r2, r3
	STR      r2, [r0]
	LDR      r2, [r0, #4]
	MOV      r6, #1
	LSL      r6, r6, #0xa
	BIC      r2, r5
	ADD      r2, r2, r6
	STR      r2, [r0, #4]
	LDRH     r3, [r4, #0xc]
	LSR      r2, r2, #0xa
	LSL      r2, r2, #0xa
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	ORR      r2, r3
	STR      r2, [r0, #4]
	LDR      r2, [pc, #0x11c]
	ADD      r0, #8
	STR      r2, [r0]
	LDRB     r3, [r4, #0x18]
	ORR      r2, r3
	STR      r2, [r0]
	LDR      r2, [r0, #4]
	BIC      r2, r5
	ADD      r2, r2, r6
	STR      r2, [r0, #4]
	LDRH     r3, [r4, #0xc]
	LSR      r2, r2, #0xa
	LSL      r2, r2, #0xa
	ADD      r3, #8
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	ORR      r2, r3
	STR      r2, [r0, #4]
	ADD      r0, #8
	STR      r0, [r1]
	LDRB     r7, [r4, #0x15]
	LDR      r0, [r4, #0x10]
	CMP      r0, #0
	BEQ      |loc_080196C8|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x64]
	ADD      r2, r2, r1
	LDRB     r1, [r4, #0x16]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r7, r0, r7
|loc_080196C8|
	LDRB     r0, [r4, #0x14]
	CMP      r0, r7
	BEQ      |loc_08019716|
	MOV      r6, #1
	LDR      r1, [pc, #0xc8]
	LSL      r6, r6, #9
	ADD      r2, r6, #0
	ADD      r5, sp, #4
	ADD      r1, #4
	ADD      r0, r5, #0
	STRB     r7, [r4, #0x14]
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r0, r7, #0
	CMP      r7, #0x35
	BGE      |loc_08019706|
	LDR      r7, [pc, #0xc0]
	MOV      r1, #1
|loc_080196EC|
	LSL      r2, r0, #4
	LDR      r3, [r7, r2]
	ADD      r2, r2, r7
	STRB     r1, [r5, r3]
	LDR      r3, [r2, #4]
	ADD      r0, #1
	STRB     r1, [r5, r3]
	LDR      r3, [r2, #8]
	CMP      r0, #0x35
	STRB     r1, [r5, r3]
	LDR      r2, [r2, #0xc]
	STRB     r1, [r5, r2]
	BLT      |loc_080196EC|
|loc_08019706|
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0xa4]
	ADD      r2, r6, #0
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	ADD      r1, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08019716|
	ADD      sp, #0x1fc
	ADD      sp, #8
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	ADD      r3, r1, #0
	MOV      r1, #0
	CMP      r3, #0x12
	BEQ      |loc_08019766|
	BGT      |sub_08019742|
	CMP      r3, #0xb
	BEQ      |loc_0801975E|
	CMP      r3, #0xc
	BEQ      |loc_08019750|
	CMP      r3, #0x11
	BNE      |loc_08019788|
	LDR      r3, [r0, #0x10]
	CMP      r3, r2
	BNE      |loc_0801973E|
	STR      r1, [r0, #0x10]
|loc_0801973E|
	MOV      r0, #0
	POP      {r3, pc}
