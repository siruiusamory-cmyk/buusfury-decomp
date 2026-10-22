	CODE16
|Math_Divide5|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r4, r0, #0
	LDR      r0, [r5, #0x50]
	LDR      r0, [r0]
	LSL      r1, r0, #4
	ADD      r0, r4, #0
	ADD      r0, #0x1c
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	LDRH     r2, [r5, #0x12]
	MUL      r0, r2
	SWI      6
	LDRB     r1, [r4, #0x14]
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LDR      r2, [pc, #0x19c]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDRB     r1, [r1]
	LSL      r1, r1, #0x1f
	BEQ      |sub_0801C540|
	ADD      r1, r4, #0
	ADD      r1, #0x20
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
|loc_0801C536|
	STRH     r0, [r1]
	LDRH     r2, [r1]
	CMP      r2, r0
	BNE      |loc_0801C536|
	POP      {r3, r4, r5, pc}
