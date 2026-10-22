	CODE16
|Table_InitLink1|
	LSL      r2, r1, #2
	ADD      r2, r2, r1
	LSL      r2, r2, #1
	LDR      r3, [pc, #0x1d0]
	ADD      r2, r2, r0
	ADD      r2, r2, r3
	MOV      r3, #0xff
	STRB     r3, [r2]
	STRB     r3, [r2, #7]
	LDRB     r3, [r0, #1]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	CMP      r3, #0xff
	STRB     r3, [r2, #6]
	BEQ      |loc_080113AC|
	ADD      r2, r3, #0
	LSL      r3, r2, #2
	ADD      r2, r3, r2
	LSL      r2, r2, #1
	MOV      r3, #0x69
	LSL      r3, r3, #4
	ADD      r2, r2, r0
	ADD      r2, r2, r3
	STRB     r1, [r2, #0xb]
|loc_080113AC|
	STRB     r1, [r0, #1]
	BX       lr
	LSL      r3, r1, #2
	ADD      r3, r3, r1
	PUSH     {r4, r5, r6, r7}
	LDR      r4, [pc, #0x19c]
	LSL      r3, r3, #1
	ADD      r3, r3, r0
	ADD      r5, r3, r4
	LSL      r3, r2, #2
	ADD      r3, r3, r2
	LSL      r3, r3, #1
	ADD      r3, r3, r0
	ADD      r4, r3, r4
	LDRH     r6, [r4, #4]
	LDRH     r3, [r5, #4]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	ADD      r3, r3, r6
	STRH     r3, [r5, #4]
	LDRB     r3, [r4, #6]
	MOV      r6, #0x69
	LSL      r6, r6, #4
	STRB     r3, [r5, #6]
	LDRB     r3, [r4, #6]
	CMP      r3, #0xff
	BEQ      |loc_080113F0|
	ADD      r7, r3, #0
	LSL      r3, r7, #2
	ADD      r3, r3, r7
	LSL      r3, r3, #1
	ADD      r3, r3, r0
	ADD      r3, r3, r6
	STRB     r1, [r3, #0xb]
|loc_080113F0|
	LDRB     r3, [r4, #9]
	STRB     r3, [r5, #9]
	LDRB     r3, [r4, #9]
	CMP      r3, #0xff
	BEQ      |sub_0801140A|
	ADD      r7, r3, #0
	LSL      r3, r7, #2
	ADD      r3, r3, r7
	LSL      r3, r3, #1
	ADD      r3, r3, r0
	ADD      r3, r3, r6
	STRB     r1, [r3, #0xc]
	B        |sub_0801140C|
