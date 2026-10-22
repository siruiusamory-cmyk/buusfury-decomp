	CODE16
|sub_0801FB3A|
	LSR      r6, r0, #0x20
|loc_0801FB3C|
	LSL      r5, r4, #0
	LSL      r3, r6, #1
	LSL      r0, r4, #0
	LSL      r0, r5, #0
|loc_0801FB44|
	LSL      r5, r4, #0
	LSL      r4, r4, #1
	LSL      r1, r5, #0
	LSL      r0, r0, #0
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	BCS      |loc_0801FB44|
	LSR      r3, r7, #0x20
	DCW      0xf5a5,0x0803
	LSR      r4, r7, #0x20
	LSR      r2, r6, #1
	LSL      r0, r0, #1
	LSL      r0, r0, #0x18
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r4, [sp, #0x1f0]
	LSR      r1, r6, #0x20
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	POP      {r2}
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LSL      r0, r2, #3
	ADD      r4, r0, r1
	LDR      r5, [r4, #4]
	ADD      r0, r4, #4
	SUB      r3, r5, r3
	STR      r3, [r4, #4]
	BNE      |loc_0801FB94|
	LDR      r3, [r1]
	SUB      r3, #1
	STR      r3, [r1]
	SUB      r1, r3, r2
	BEQ      |loc_0801FB94|
	LSL      r2, r1, #3
	ADD      r1, r4, #0
	ADD      r1, #0xc
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0801FB94|
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, r7}
	LDRB     r6, [r2, #4]
	MOV      r7, #0
	MVN      r7, r7
	CMP      r6, #0
	BNE      |sub_0801FBAA|
	ADD      r0, r7, #0
	POP      {r4, r5, r6, r7}
	BX       lr
