	CODE16
|sub_0800D6D2|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BL       |sub_0800DA92|
	LDR      r1, [r5]
	ADD      r2, r1, #0
	ADD      r2, #8
	STR      r2, [r5]
	LDR      r2, [r4, #0x4c]
	LDR      r5, [pc, #0x194]
	LDR      r2, [r2, #0xc]
	STR      r2, [r1]
	LDR      r3, [r4, #0x58]
	AND      r2, r5
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r4, #0x5c]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRB     r2, [r4, #8]
	LDR      r3, [r1, #4]
	MOV      r5, #3
	LSL      r2, r2, #0x1a
	LSR      r2, r2, #0x1e
	LSL      r5, r5, #0xa
	BIC      r3, r5
	LSL      r2, r2, #0xa
	ORR      r2, r3
	STR      r2, [r1, #4]
	LDR      r3, [r4, #0x4c]
	LSR      r2, r2, #0xa
	LDR      r3, [r3, #8]
	LSL      r2, r2, #0xa
	LDRH     r3, [r3, #2]
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	ORR      r2, r3
	STR      r2, [r1, #4]
	POP      {r3, r4, r5, pc}
