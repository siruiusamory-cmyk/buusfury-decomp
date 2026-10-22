	CODE16
|sub_080217AC|
	PUSH     {r4}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	LDR      r4, [pc, #0x7c]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	LDR      r2, [r0, #0x28]
	LDR      r2, [r2, #4]
	STR      r2, [r1]
	LDR      r3, [r0, #0x10]
	AND      r2, r4
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x14]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRH     r2, [r0, #0xc]
	LDR      r3, [r1, #4]
	LSR      r3, r3, #0xa
	LSL      r2, r2, #0x16
	LSR      r2, r2, #0x16
	LSL      r3, r3, #0xa
	ORR      r2, r3
	STR      r2, [r1, #4]
	LDRB     r0, [r0, #8]
	MOV      r3, #3
	LSL      r3, r3, #0xa
	LSL      r0, r0, #0x1a
	LSR      r0, r0, #0x1e
	LSL      r0, r0, #0xa
	BIC      r2, r3
	ORR      r0, r2
	STR      r0, [r1, #4]
	POP      {r4}
	MOV      r0, #0
	BX       lr
	PUSH     {r4, lr}
	CMP      r1, #0xb
	BNE      |sub_08021824|
	LDR      r1, [r0, #0x28]
	LDRH     r0, [r0, #0xc]
	LDRB     r3, [r1, #2]
	LDRB     r4, [r1, #3]
	LSL      r0, r0, #5
	LDR      r1, [r1, #8]
	MUL      r3, r4
	ADD      r2, r3, #0
	LDR      r3, [pc, #0xc]
	ADD      r0, r0, r3
	BL       |inc_0x049120_0x055620| + 0x18
	MOV      r0, #0
	POP      {r4, pc}
