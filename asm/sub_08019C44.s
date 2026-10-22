	CODE16
|sub_08019C44|
	PUSH     {r4}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	LDR      r4, [pc, #0xd0]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	LDR      r2, [r0, #0x18]
	LDR      r2, [r2, #4]
	STR      r2, [r1]
	LDR      r3, [r0, #0x38]
	AND      r2, r4
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x3c]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRH     r2, [r0, #0xc]
	LDR      r3, [r1, #4]
	MOV      r4, #3
	LSR      r3, r3, #0xa
	LSL      r2, r2, #0x16
	LSR      r2, r2, #0x16
	LSL      r3, r3, #0xa
	ORR      r2, r3
	STR      r2, [r1, #4]
	LDRB     r3, [r0, #8]
	LSL      r4, r4, #0xa
	BIC      r2, r4
	LSL      r3, r3, #0x1a
	LSR      r3, r3, #0x1e
	LSL      r3, r3, #0xa
	ORR      r2, r3
	STR      r2, [r1, #4]
	ADD      r0, #0x14
	LDMIA    r0!, {r0, r1}
	CMP      r1, r0
	BEQ      |sub_08019CA2|
	MOV      r0, #1
	POP      {r4}
	BX       lr
