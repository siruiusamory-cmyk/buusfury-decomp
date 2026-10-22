	CODE16
|sub_08036BF6|
	PUSH     {r4}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	LDR      r4, [pc, #0x180]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	LDR      r2, [r0, #0x38]
	LDR      r2, [r2, #4]
	STR      r2, [r1]
	LDR      r3, [r0, #0x18]
	AND      r2, r4
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r3, [r0, #0x1c]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDR      r2, [r1, #4]
	MOV      r3, #3
	LSL      r3, r3, #0xa
	ORR      r2, r3
	STR      r2, [r1, #4]
	LDRH     r3, [r0, #0xc]
	LSR      r2, r2, #0xa
	LSL      r2, r2, #0xa
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	ORR      r2, r3
	STR      r2, [r1, #4]
	LDR      r1, [r0, #0x38]
	LDR      r0, [r0, #0x30]
	CMP      r1, r0
	BEQ      |sub_08036C4A|
	MOV      r0, #1
	POP      {r4}
	BX       lr
