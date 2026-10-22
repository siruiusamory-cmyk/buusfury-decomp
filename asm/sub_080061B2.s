	CODE16
|sub_080061B2|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	ADD      r5, r1, #0
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r0, [r0, #0xc]
	LDR      r1, [r4, #8]
	CMP      r0, r1
	BEQ      |sub_080061CA|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
