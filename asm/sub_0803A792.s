	CODE16
|sub_0803A792|
	LSR      r7, r6, #1
	BMI      |loc_0803A808|
	LSR      r4, r0, #0x20
	POP      {r3, r4, r5, r6, r7, pc}
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r2, #4]
	CMP      r1, #0
	BNE      |sub_0803A7AC|
	MOV      r0, #1
	POP      {r3, pc}
