|sub_0803D374|
	EXPORT |sub_0803D374|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x120]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x3c
	CMP      r1, #0
	BNE      |sub_0803D388|
	MOV      r0, #0
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
