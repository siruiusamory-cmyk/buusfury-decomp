	CODE16
|sub_0801140C|
	LDRB     r3, [r4, #8]
	STRB     r3, [r5, #8]
	LDRB     r3, [r4, #8]
	CMP      r3, #0xff
	BEQ      |loc_08011424|
	ADD      r4, r3, #0
	LSL      r3, r4, #2
	ADD      r3, r3, r4
	LSL      r3, r3, #1
	ADD      r3, r3, r0
	ADD      r3, r3, r6
	STRB     r1, [r3, #0xd]
|loc_08011424|
	ADD      r1, r2, #0
	POP      {r4, r5, r6, r7}
	B        |loc_0801137C|
