	CODE16
|sub_0803E32C|
	PUSH     {r4, r5, r6}
	ADD      r5, r3, #0
	MOV      r4, #0xf
	LSL      r3, r4, #6
	ADD      r3, r3, r0
	LDRB     r6, [r3, #0x10]
	LSL      r6, r6, #0x1f
	BEQ      |sub_0803E362|
	LDR      r6, [r3, #0x28]
	CMP      r6, r1
	BNE      |sub_0803E362|
	LDRB     r6, [r3, #0x12]
	CMP      r6, r2
	BNE      |sub_0803E362|
	ADD      r6, r3, #0
	MOV      r3, #0x13
	LDRSB    r6, [r6, r3]
	CMP      r6, r5
	BNE      |sub_0803E362|
	LSL      r1, r4, #6
	ADD      r0, r1, r0
	LDRB     r1, [r0, #0x10]
	LSR      r1, r1, #1
	LSL      r1, r1, #1
	STRB     r1, [r0, #0x10]
	POP      {r4, r5, r6}
	BX       lr
