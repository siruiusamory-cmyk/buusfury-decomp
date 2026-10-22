	CODE16
|loc_0803E4E4|
	ADD      r2, r0, #0
	ADD      r2, #0x50
	PUSH     {r4, r5, r6}
	LDRB     r3, [r2, #8]
	MOV      r1, #0x11
	ADD      r4, r3, #0
	AND      r4, r1
	ADD      r1, r0, #0
	ADD      r1, #0x40
	CMP      r4, #0
	BEQ      |loc_0803E55C|
	LDRB     r4, [r2, #0xa]
	MOV      r6, #4
	CMP      r4, #0xff
	BNE      |sub_0803E514|
	LDRB     r2, [r1, #0xa]
	BIC      r2, r6
	STRB     r2, [r1, #0xa]
	LDRB     r1, [r0, #0x10]
	LSR      r1, r1, #1
	LSL      r1, r1, #1
	STRB     r1, [r0, #0x10]
	POP      {r4, r5, r6}
	BX       lr
